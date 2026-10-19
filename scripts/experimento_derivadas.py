#!/usr/bin/env python3
"""¿Mejoran el modelo las tres características derivadas del dominio?

Evidencia de la decisión 1.3 del registro (`docs/decisiones.md`). El notebook 02
justifica `regla_2p`, `tpsa_por_mw` y `lipo_neta` solo con AUC individual y
correlación con la clase; la asesora pidió **comparar el modelo con y sin ellas**,
que es lo que mide este script.

Las tres derivadas, calculadas con los descriptores crudos:

- `regla_2p = (TPSA < U) & (NumHDonors <= 1)`, como float. U = 67 Å² es el valor
  publicado, pero el umbral óptimo de TPSA no es constante (sobre el entrenamiento
  da 107 Å²), así que también se prueba U derivado **dentro de cada pliegue** con el
  índice de Youden sobre la TPSA del pliegue de ajuste.
- `tpsa_por_mw = TPSA / MolWt`
- `lipo_neta = MolLogP − TPSA / 100`

Variantes (siempre los 203 descriptores de `limpiar_descriptores`): `sin_derivadas`,
`con_las_tres` (U = 67), `con_las_tres_U_pliegue` (U de Youden por pliegue) y
quitar una a la vez (`sin_regla_2p`, `sin_tpsa_por_mw`, `sin_lipo_neta`, con U = 67).

Dentro de cada pliegue, ajustados solo con el pliegue de ajuste y en este orden:
`FiltroCasiConstante(min_distintas=10)`, `FiltroCorrelacion(umbral=0.95)` y el modelo
(`LogReg` con min–max, o `RF`), todo en un `Pipeline`. Así una derivada que es
redundante con un descriptor (p. ej. `tpsa_por_mw` con TPSA) puede ser descartada
por el filtro, y el script registra si sobrevivió.

Validación cruzada de 5 pliegues agrupada por andamio y esqueleto de conectividad,
con 3 semillas, solo sobre las filas de entrenamiento; la validación y la prueba no
se tocan. Las diferencias contra `sin_derivadas` son **pareadas por (semilla,
pliegue)** y su error estándar lleva la corrección de Nadeau y Bengio, porque las 15
evaluaciones comparten datos de entrenamiento:
`ee = std(dif, ddof=1)/sqrt(J) * sqrt(1 + J * (1/5)/(1 - 1/5))`, J = 15.

Salida: `notebooks/datos/resultados_derivadas.csv`, versionado para que el notebook lo
lea sin repetir el experimento. Tarda unos minutos (7 variantes × 2 modelos × 15
evaluaciones).

Uso: `python scripts/experimento_derivadas.py [--sin-registro] [--semillas 0 1 2]
[--variantes sin_derivadas con_las_tres ...]`
"""
import argparse
import platform
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from data_prep.splits import (andamio_murcko, esqueleto_conectividad, grupos_cv,
                              scaffold_split, umbral_youden)
from features.molecular import a_mol, descriptores_rdkit, limpiar_descriptores
from features.seleccion import FiltroCasiConstante, FiltroCorrelacion
from tracking import Corrida

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
U_PUBLICADO = 67.0
DERIVADAS = ("regla_2p", "tpsa_por_mw", "lipo_neta")

# variante -> (derivadas que incluye, U de la regla: número o "pliegue")
VARIANTES = {
    "sin_derivadas": ((), None),
    "con_las_tres": (DERIVADAS, U_PUBLICADO),
    "con_las_tres_U_pliegue": (DERIVADAS, "pliegue"),
    "sin_regla_2p": (("tpsa_por_mw", "lipo_neta"), U_PUBLICADO),
    "sin_tpsa_por_mw": (("regla_2p", "lipo_neta"), U_PUBLICADO),
    "sin_lipo_neta": (("regla_2p", "tpsa_por_mw"), U_PUBLICADO),
}
MODELOS = ("LogReg", "RF")


def modelo(nombre: str, semilla: int) -> Pipeline:
    """Selección de columnas y modelo, en un solo objeto que se ajusta por pliegue."""
    casi = FiltroCasiConstante(min_distintas=10)
    corr = FiltroCorrelacion(umbral=0.95)
    if nombre == "LogReg":
        return Pipeline([("casi", casi), ("corr", corr), ("escala", MinMaxScaler()),
                         ("modelo", LogisticRegression(max_iter=3000, random_state=semilla))])
    return Pipeline([("casi", casi), ("corr", corr),
                     ("modelo", RandomForestClassifier(n_estimators=200, random_state=semilla,
                                                       n_jobs=-1))])


def metricas(y: np.ndarray, puntuacion: np.ndarray) -> tuple[float, float, float]:
    """MCC, AUPRC sobre la clase minoritaria (BBB−) y AUROC.

    El AUPRC se invierte —`1 - y`, `1 - s`— porque la clase que importa es la
    minoritaria: medido sobre la mayoritaria, la línea base es más alta y los
    valores parecen mejores de lo que son.
    """
    return (matthews_corrcoef(y, (puntuacion >= 0.5).astype(int)),
            average_precision_score(1 - y, 1 - puntuacion),
            roc_auc_score(y, puntuacion))


def matriz(limpio: pd.DataFrame, derivadas: tuple, u: float | None) -> pd.DataFrame:
    """Los descriptores más las derivadas pedidas, con U para la regla de dos parámetros."""
    cols = limpio.copy()
    if "regla_2p" in derivadas:
        cols["regla_2p"] = ((limpio["TPSA"] < u) & (limpio["NumHDonors"] <= 1)).astype(float)
    if "tpsa_por_mw" in derivadas:
        cols["tpsa_por_mw"] = limpio["TPSA"] / limpio["MolWt"]
    if "lipo_neta" in derivadas:
        cols["lipo_neta"] = limpio["MolLogP"] - limpio["TPSA"] / 100
    return cols


def sobrevivientes(pipe: Pipeline, columnas: list[str]) -> set[str]:
    """Nombres de las columnas que quedaron tras los dos filtros."""
    s1 = pipe.named_steps["casi"].get_support()
    nombres = np.array(columnas)[s1]
    s2 = pipe.named_steps["corr"].get_support()
    return set(nombres[s2])


def resumen(cv: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Medias por variante y modelo, y diferencias pareadas contra `sin_derivadas`."""
    medias = cv.groupby(["variante", "modelo"])[["MCC", "AUPRC_neg", "AUROC", "n_columnas"]].mean()
    filas = []
    for modelo_n in cv["modelo"].unique():
        base = cv[(cv.variante == "sin_derivadas") & (cv.modelo == modelo_n)] \
            .set_index(["seed", "fold"]).sort_index()
        for var in cv["variante"].unique():
            if var == "sin_derivadas":
                continue
            otra = cv[(cv.variante == var) & (cv.modelo == modelo_n)] \
                .set_index(["seed", "fold"]).sort_index()
            for met in ("MCC", "AUPRC_neg"):
                dif = (otra[met] - base[met]).dropna().values
                J = len(dif)
                # Nadeau y Bengio: las J evaluaciones comparten datos de entrenamiento
                ee = dif.std(ddof=1) / np.sqrt(J) * np.sqrt(1 + J * (1 / PLIEGUES) / (1 - 1 / PLIEGUES))
                filas.append(dict(variante=var, modelo=modelo_n, metrica=met, J=J,
                                  dif_media=dif.mean(), ee=ee,
                                  ic95_inf=dif.mean() - 1.96 * ee, ic95_sup=dif.mean() + 1.96 * ee))
    return medias, pd.DataFrame(filas)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-registro", action="store_true", help="no crea carpeta en experimentos/")
    ap.add_argument("--semillas", type=int, nargs="+", default=list(SEMILLAS))
    ap.add_argument("--variantes", nargs="+", default=list(VARIANTES))
    args = ap.parse_args()
    semillas = tuple(args.semillas)
    variantes = {k: VARIANTES[k] for k in args.variantes}
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)

    datos = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
    b = pd.read_csv(datos)
    b.columns = [c.strip().lstrip("﻿") for c in b.columns]
    b = b.rename(columns={"smiles_std": "SMILES", "bbb_class": "BBB+/BBB-"})
    b["mol"] = b["SMILES"].map(a_mol)
    d = b.dropna(subset=["mol", "BBB+/BBB-"]).reset_index(drop=True)
    d["y"] = (d["BBB+/BBB-"] == "BBB+").astype(int)
    d["andamio"] = [andamio_murcko(m) for m in d["mol"]]
    d["esqueleto"] = [esqueleto_conectividad(m) for m in d["mol"]]
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1,
                                    semilla=42, acíclicos_a="entrenamiento")
    print(d["particion"].value_counts().to_dict(), flush=True)

    desc = descriptores_rdkit(list(d["mol"]))
    limpio, _ = limpiar_descriptores(desc, verbose=False)
    limpio = limpio.reset_index(drop=True)
    print(f"{limpio.shape[1]} descriptores utilizables", flush=True)

    y = d["y"].values
    g = grupos_cv(d)
    tr = np.where((d["particion"] == "entrenamiento").values)[0]
    tpsa = limpio["TPSA"].values

    params = dict(variantes={k: dict(derivadas=list(v[0]), U=v[1]) for k, v in variantes.items()},
                  modelos=dict(LogReg="MinMaxScaler + max_iter=3000", RF="n_estimators=200"),
                  seleccion=dict(casi_constante_min_distintas=10, correlacion_spearman=0.95),
                  pliegues=PLIEGUES, descriptores=int(limpio.shape[1]),
                  partición=dict(fraccion_prueba=0.2, fraccion_validacion=0.1, semilla=42,
                                 acíclicos_a="entrenamiento"))
    registro = None if args.sin_registro else Corrida(
        "derivadas", decision="1.3", params=params, semillas=list(semillas), datos=[datos])
    if registro is not None:
        registro.__enter__()
    try:
        t0 = time.time()
        filas = []
        for semilla in semillas:
            cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
            for k, (ia, ib) in enumerate(cv.split(tr, y[tr], g[tr])):
                ajuste, evalua = tr[ia], tr[ib]
                # U de Youden con la TPSA del pliegue de ajuste (BBB+ = TPSA baja)
                u_pliegue, _ = umbral_youden(y[ajuste], tpsa[ajuste], mayor_es_positivo=False)
                for var, (deriv, u_cfg) in variantes.items():
                    u = u_pliegue if u_cfg == "pliegue" else u_cfg
                    X = matriz(limpio, deriv, u)
                    columnas = list(X.columns)
                    Xv = X.values.astype(float)
                    for mod_n in MODELOS:
                        pipe = modelo(mod_n, semilla).fit(Xv[ajuste], y[ajuste])
                        mcc, ap_, au = metricas(y[evalua], pipe.predict_proba(Xv[evalua])[:, 1])
                        vivas = sobrevivientes(pipe, columnas)
                        filas.append(dict(
                            variante=var, modelo=mod_n, seed=semilla, fold=k,
                            MCC=mcc, AUPRC_neg=ap_, AUROC=au, n_columnas=len(vivas),
                            U_tpsa=u if "regla_2p" in deriv else np.nan,
                            sobrevive_regla_2p=("regla_2p" in vivas) if "regla_2p" in deriv else np.nan,
                            sobrevive_tpsa_por_mw=("tpsa_por_mw" in vivas) if "tpsa_por_mw" in deriv else np.nan,
                            sobrevive_lipo_neta=("lipo_neta" in vivas) if "lipo_neta" in deriv else np.nan,
                            eval="cv"))
                print(f"semilla {semilla} pliegue {k} listo ({time.time()-t0:.0f}s)", flush=True)

        res = pd.DataFrame(filas)
        salida = RAIZ / "notebooks/datos/resultados_derivadas.csv"
        salida.parent.mkdir(parents=True, exist_ok=True)
        res.to_csv(salida, index=False)
        print("escrito", salida)

        medias, difs = resumen(res)
        pd.set_option("display.width", 200)
        print("\nMedias por variante y modelo\n", medias.round(4).to_string())
        if len(difs):
            print("\nDiferencias pareadas contra sin_derivadas (Nadeau y Bengio)\n",
                  difs.round(4).to_string(index=False))
        u_f = res[(res.variante == "con_las_tres_U_pliegue") & (res.modelo == "LogReg")]["U_tpsa"]
        if len(u_f):
            print(f"\nU de Youden por pliegue: media {u_f.mean():.1f}, rango "
                  f"{u_f.min():.1f}-{u_f.max():.1f} Å² ({len(u_f)} pliegues)")
        for var in variantes:
            for mod_n in MODELOS:
                s = res[(res.variante == var) & (res.modelo == mod_n)]
                txt = ", ".join(f"{n}: {int(s[f'sobrevive_{n}'].sum())}/{int(s[f'sobrevive_{n}'].notna().sum())}"
                                for n in DERIVADAS if s[f"sobrevive_{n}"].notna().any())
                if txt:
                    print(f"supervivencia {var}/{mod_n}: {txt}")
        print(f"\ntiempo total {time.time()-t0:.0f}s")

        if registro is not None:
            registro.metricas({
                "cv_media": {v: {m: {k_: float(x) for k_, x in medias.loc[(v, m)].items()}
                                 for m in MODELOS} for v in variantes},
                "diferencias": difs.to_dict(orient="records"),
                "U_pliegue": ({"media": float(u_f.mean()), "min": float(u_f.min()),
                               "max": float(u_f.max())} if len(u_f) else None),
                "filas_cv": int(len(res))})
    finally:
        if registro is not None:
            registro.__exit__(*sys.exc_info())


if __name__ == "__main__":
    main()
