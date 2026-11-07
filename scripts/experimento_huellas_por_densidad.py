#!/usr/bin/env python3
"""¿La ganancia de las huellas sigue a la densidad del espacio químico, a igual peso molecular? (E11)

Queda en pie una explicación de por qué las huellas ayudan en la fase 2 y no en la 1 (E9 y E10 descartaron
el tamaño de datos y el tipo de etiqueta): que ganen donde el espacio químico está densamente muestreado,
porque son una buena llave de similitud. El peso molecular y la densidad van juntos, así que aquí se mide la
densidad **dentro de cada tramo de peso**, con los mismos cortes fijos que E6 (`etiquetas_por_tamano`).

**Densidad.** Para cada molécula, cuántas moléculas del ajuste con similitud de Tanimoto ≥ 0.4 (Morgan radio
2, 2,048 bits) hay **en otro grupo** (`grupo_cv`): lo que el modelo podría usar como vecino sin que sea un
análogo de la misma partición. Dentro de cada tramo se parte en terciles (empates rotos al azar, semilla 0).

**Qué se mide.** La ganancia de añadir huellas a los descriptores, por celda (tramo × tercil de densidad):
ΔAUROC en la fase 1 (`logistica`, `svm_rbf`, `knn`) y Δconcordancia del `aft` en la fase 2, en las mismas 15
evaluaciones agrupadas.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Controles: la ganancia en `todos` reproduce la de E6 dentro de 0.003 (fase 1: `knn` −0.0056, `logistica`
   −0.0043, `svm_rbf` −0.0016; fase 2: +0.0057). Si no, el resto no se lee.
2. En cada evaluación, sea D la media, sobre los tramos que tienen la celda de densidad alta y la baja, de
   [ganancia en el tercil alto − ganancia en el tercil bajo]. **La densidad explica la ganancia** (por modelo)
   si la media de D es positiva, mayor que su desviación entre evaluaciones y D > 0 en al menos 12 de 15.
   **No la explica** si la media de D es ≤ 0 o D > 0 en menos de 8 de 15. Cualquier otro caso es **no
   concluyente**. En la fase 1 el veredicto es el de la mayoría de los tres modelos.
3. No se afirma causalidad: es una asociación a igual peso, y la densidad puede ir con otras cosas.
4. Se reportan las celdas y cuántas evaluaciones tiene cada una; una celda se usa si tiene al menos 3.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_huellas_por_densidad.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import numpy as np
import pandas as pd
from experimento_aft_huellas import N_BITS, PARES, datos as datos_fase2
from scipy import sparse
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline

from src.evaluation.cv import evaluar
from src.evaluation.regresion import concordancia_harrell
from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan
from src.features.similitud import huellas as huellas_rdkit, matriz_densa, matriz_dispersa
from src.models.alternativos import seleccion
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado
from src.models.tareas import PROCESADOS, cargar, etiquetas_por_tamano
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
UMBRAL_VECINO = 0.4
MODELOS = ("logistica", "svm_rbf", "knn")
REF_FASE1 = {"knn": -0.0056, "logistica": -0.0043, "svm_rbf": -0.0016}     # de: 2026-11-03-artemio-1.3-tamano-huellas-permeabilidad
REF_FASE2 = 0.0057                                                          # de: 2026-11-03-artemio-1.3-tamano-huellas-actividad
TOLERANCIA = 0.003
MIN_EVAL = 3
REGLA_EVALUACIONES = 12
NO_EXPLICA_MAXIMO = 8
NIVELES = ("d1 baja", "d2", "d3 alta")


def terciles(densidad: np.ndarray, tramo: np.ndarray) -> np.ndarray:
    """Tercil de densidad dentro de cada tramo; los empates se rompen al azar con semilla 0."""
    rng = np.random.default_rng(0)
    salida = np.empty(len(densidad), dtype=object)
    for t in np.unique(tramo):
        idx = np.flatnonzero(tramo == t)
        orden = np.lexsort((rng.random(len(idx)), densidad[idx]))
        for k, nivel in enumerate(NIVELES):
            salida[idx[orden[k * len(idx) // 3:(k + 1) * len(idx) // 3 if k < 2 else len(idx)]]] = nivel
    return np.array([f"{t}|{n}" for t, n in zip(tramo, salida, strict=True)])


def densidad_por_vecinos(S, grupo: np.ndarray) -> np.ndarray:
    """Cuántos vecinos con similitud ≥ UMBRAL_VECINO hay en otro grupo, para cada molécula."""
    if sparse.issparse(S):
        c = S.tocoo()
        mascara = (c.data >= UMBRAL_VECINO) & (grupo[c.row] != grupo[c.col])
        return np.bincount(c.row[mascara], minlength=S.shape[0])
    A = (np.asarray(S) >= UMBRAL_VECINO) & (grupo[:, None] != grupo[None, :])
    return A.sum(axis=1)


def resumen_d(ganancias: pd.DataFrame) -> dict:
    """`ganancias`: filas (semilla, pliegue, tramo, nivel) con `dif`. D por evaluación y la regla."""
    ancho = ganancias.pivot_table(index=["semilla", "pliegue", "tramo"], columns="nivel", values="dif")
    if "d3 alta" not in ancho or "d1 baja" not in ancho:
        return {"d_media": None, "veredicto": "sin celdas"}
    d = (ancho["d3 alta"] - ancho["d1 baja"]).dropna().groupby(["semilla", "pliegue"]).mean()
    out = {"d_media": round(float(d.mean()), 4), "d_desv": round(float(d.std()), 4),
           "d_positiva_en": int((d > 0).sum()), "evaluaciones": int(len(d))}
    if out["d_media"] > 0 and out["d_media"] > out["d_desv"] and out["d_positiva_en"] >= REGLA_EVALUACIONES:
        out["veredicto"] = "la densidad explica la ganancia"
    elif out["d_media"] <= 0 or out["d_positiva_en"] < NO_EXPLICA_MAXIMO:
        out["veredicto"] = "la densidad no la explica"
    else:
        out["veredicto"] = "no concluyente"
    return out


def fase1() -> tuple[dict, pd.DataFrame]:
    t = cargar("permeabilidad", estratos="tamano")
    X = np.asarray(t.X, dtype=float)
    n_densas = X.shape[1]
    tramo = np.asarray(t.estratos)           # los tramos de peso de `etiquetas_por_tamano`, como en E6
    hs = huellas_rdkit(t.meta["SMILES"].tolist())
    dens = densidad_por_vecinos(matriz_densa(hs), np.asarray(t.grupos))
    celdas = terciles(dens, tramo)
    huellas, ident = identificadores_morgan(t.meta["SMILES"].tolist())
    huellas, ident, _ = agrupar_iguales(huellas, ident)
    X_mixta = sparse.hstack([sparse.csr_matrix(X), huellas]).tocsr()
    partes = {}
    for brazo, (M, envolver) in {"descriptores": (X, lambda m: m),
                                 "huellas": (X_mixta, lambda m: make_pipeline(AgregarHuellas(n_densas, n_bits=N_BITS), m))}.items():
        t0 = time.perf_counter()
        modelos = {k: envolver(v) for k, v in seleccion(MODELOS).items()}
        res, _ = evaluar(modelos, M, t.y, t.grupos, estratos=celdas, semillas=SEMILLAS, verboso=False)
        partes[brazo] = res
        print(f"fase 1 · {brazo}: {time.perf_counter() - t0:.0f} s", flush=True)
    m = partes["descriptores"].merge(partes["huellas"], on=["modelo", "semilla", "pliegue", "estrato"], suffixes=("_d", "_h"))
    m["dif"] = m["auroc_h"] - m["auroc_d"]
    todos = m[m["estrato"] == "todos"].groupby("modelo")["dif"].mean()
    celdas_df = m[m["estrato"] != "todos"].copy()
    celdas_df[["tramo", "nivel"]] = celdas_df["estrato"].str.split("|", expand=True)
    return {"todos": todos.round(4).to_dict(), "densidad_media": float(dens.mean())}, celdas_df


def fase2() -> tuple[dict, pd.DataFrame]:
    d = datos_fase2()
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")
    merged = pares.merge(desc, on="smiles").reset_index(drop=True)
    inf = merged["limite_inferior"].to_numpy(float)
    sup = merged["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inf) & np.isposinf(sup)) & (inf <= sup)
    merged = merged[util].reset_index(drop=True)
    fuera = (merged["particion"] != "prueba").to_numpy()
    merged = merged[fuera].reset_index(drop=True)
    assert len(merged) == len(d["inferior"]) == 56_241
    unicos, mol = np.unique(merged["smiles"].to_numpy(), return_inverse=True)
    grupo_mol = pd.Series(merged["grupo_cv"].to_numpy()).groupby(mol).first().to_numpy()
    t0 = time.perf_counter()
    S = matriz_dispersa(huellas_rdkit(unicos.tolist()), UMBRAL_VECINO)
    dens_mol = densidad_por_vecinos(S, grupo_mol)
    print(f"fase 2 · densidad de {len(unicos):,} moléculas en {time.perf_counter() - t0:.0f} s", flush=True)
    peso = merged["MolWt"].to_numpy(float)
    tramo = etiquetas_por_tamano(peso)
    celdas = terciles(dens_mol[mol], tramo)
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    brazos = {"aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
              "aft_huellas": ("X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]), d["n_densas"], N_BITS))}
    filas = []
    for semilla in SEMILLAS:
        cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=semilla)
        for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
            preds = {}
            for nombre, (matriz, modelo) in brazos.items():
                m = clone(modelo).fit(d[matriz][aj], d["inferior"][aj], d["superior"][aj])
                preds[nombre] = m.predict(d[matriz][val])
            print(f"  fase 2 · semilla {semilla} pliegue {k}", flush=True)
            for etiqueta in ("todos", *sorted(set(celdas))):
                sel = np.ones(len(val), bool) if etiqueta == "todos" else celdas[val] == etiqueta
                if sel.sum() < 30:
                    continue
                fila = {"semilla": semilla, "pliegue": k, "estrato": etiqueta, "n": int(sel.sum())}
                for nombre, p in preds.items():
                    fila[nombre] = concordancia_harrell(d["inferior"][val][sel], d["superior"][val][sel], p[sel])
                filas.append(fila)
    res = pd.DataFrame(filas)
    res["dif"] = res["aft_huellas"] - res["aft"]
    todos = float(res[res["estrato"] == "todos"]["dif"].mean())
    celdas_df = res[res["estrato"] != "todos"].copy()
    celdas_df[["tramo", "nivel"]] = celdas_df["estrato"].str.split("|", expand=True)
    return {"todos": round(todos, 4), "densidad_media": float(dens_mol.mean())}, celdas_df


def tabla_celdas(celdas: pd.DataFrame, por: str | None) -> list[dict]:
    claves = ["tramo", "nivel"] + ([por] if por else [])
    g = celdas.groupby(claves)["dif"].agg(["mean", "size", lambda s: int((s > 0).sum())])
    g.columns = ["dif_media", "evaluaciones", "mejora_en"]
    return g.round(4).reset_index().to_dict("records")


def main() -> None:
    params = {"modelos_fase1": list(MODELOS), "semillas": list(SEMILLAS), "pliegues": PLIEGUES,
              "umbral_vecino": UMBRAL_VECINO, "n_bits_sortslice": N_BITS, "terciles_dentro_de_cada_tramo": True,
              "referencias_control": {"fase1": REF_FASE1, "fase2": REF_FASE2}, "tolerancia": TOLERANCIA,
              "regla_evaluaciones": REGLA_EVALUACIONES, "no_explica_maximo": NO_EXPLICA_MAXIMO,
              "min_evaluaciones_celda": MIN_EVAL, "toca_prueba": False}
    with Corrida("huellas-por-densidad-del-espacio-quimico", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, PROCESADOS / "bbb_meta.parquet"]) as c:
        meta1, celdas1 = fase1()
        meta2, celdas2 = fase2()
        celdas1.to_csv(c.carpeta / "celdas_fase1.csv", index=False)
        celdas2.to_csv(c.carpeta / "celdas_fase2.csv", index=False)
        control1 = {m: abs(meta1["todos"][m] - REF_FASE1[m]) <= TOLERANCIA for m in REF_FASE1}
        control2 = abs(meta2["todos"] - REF_FASE2) <= TOLERANCIA
        resultado = {"control_fase1": control1, "control_fase2": control2,
                     "todos_fase1": meta1["todos"], "todos_fase2": meta2["todos"]}
        v1 = {}
        for modelo, g in celdas1.groupby("modelo"):
            ok = g.groupby(["tramo", "nivel"])["dif"].transform("size") >= MIN_EVAL
            v1[modelo] = resumen_d(g[ok])
        resultado["fase1_por_modelo"] = v1
        votos = [v["veredicto"] for v in v1.values()]
        resultado["veredicto_fase1"] = max(set(votos), key=votos.count) if votos.count(max(set(votos), key=votos.count)) >= 2 else "no concluyente"
        ok2 = celdas2.groupby(["tramo", "nivel"])["dif"].transform("size") >= MIN_EVAL
        resultado["fase2"] = resumen_d(celdas2[ok2])
        resultado["celdas_fase1"] = tabla_celdas(celdas1, "modelo")
        resultado["celdas_fase2"] = tabla_celdas(celdas2, None)
        c.metricas(resultado)
        print("\ncontroles:", control1, control2)
        print("fase 1 por modelo:", v1)
        print("veredicto fase 1:", resultado["veredicto_fase1"])
        print("fase 2:", resultado["fase2"])


if __name__ == "__main__":
    main()
