#!/usr/bin/env python3
"""E1+ · la escalera de agrupación con seis modelos, y dónde cae la prueba reservada.

Amplía `experimento_agrupacion.py` (E1, dos modelos) a los seis del Avance 4 —`svm_rbf`,
`logistica`, `mlp`, `knn`, `bosque` y `boosting`— y responde dos preguntas que E1 dejó abiertas.

**1 · ¿`logistica` se degrada menos que `svm_rbf` al apretar el agrupamiento, o es ruido?**
E1 vio que a similitud ≥ 0.5 y ≥ 0.4 la `logistica` supera a `svm_rbf` en AUROC, con una corrida
y sin intervalo. Aquí se calcula la diferencia pareada de AUROC (`logistica` − `svm_rbf`) sobre
las mismas filas y las mismas predicciones fuera de pliegue, con bootstrap de **grupos** (no de
filas), para cada agrupamiento.

**2 · ¿Dónde cae la prueba reservada en la escalera?** Se mide, sin etiquetas ni predicciones, la
similitud media de cada compuesto de la prueba con su vecino más cercano del ajuste, y se compara
con la de la validación bajo cada agrupamiento. Es **un acceso estructural** a la prueba (solo
SMILES), anotado en `experimentos/prueba.csv` con su motivo.

**Lo que se declara antes de correr.** La métrica principal de la comparación pareada es el AUROC,
porque el MCC depende de un umbral fijo en 0.5 y no es lo que la escalera ordena bien; el MCC
se reporta en la misma tabla como segunda lectura. La diferencia se considera distinguible del
cero solo si su intervalo del 95% por grupos lo excluye. Se espera que la diferencia de AUROC
crezca a favor de `logistica` al apretar el agrupamiento, pero no se afirma cuánto; si el
intervalo incluye el cero en todas las filas, se reporta como ruido.
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import numpy as np
import pandas as pd
from sklearn.metrics import matthews_corrcoef, roc_auc_score

from experimento_agrupacion import (MAX_GRUPO, SEMILLAS, UMBRALES_SIMILITUD, grupos_por_similitud,
                                    json_seguro, similitudes, vecino_mas_cercano)
from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.baseline import canalizaciones
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida, tomar_prueba

from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

REMUESTRAS = 1000
MODELOS = ("svm_rbf", "logistica", "mlp", "knn", "bosque", "boosting")


def todos_los_modelos(semilla: int = 0) -> dict:
    p = seleccion(("svm_rbf", "logistica", "mlp", "knn"), semilla)
    b = canalizaciones(semilla)
    p["bosque"], p["boosting"] = b["bosque"], b["boosting"]
    return {k: p[k] for k in MODELOS}


def diferencia_pareada(y, pa, pb, grupos, metrica, semilla=0):
    """metrica(pa) - metrica(pb), con intervalo del 95% remuestreando grupos."""
    rng = np.random.default_rng(semilla)
    unicos, inv = np.unique(grupos, return_inverse=True)
    indices = [np.flatnonzero(inv == i) for i in range(len(unicos))]
    punto = metrica(y, pa) - metrica(y, pb)
    muestras = []
    for _ in range(REMUESTRAS):
        elegidos = rng.integers(0, len(unicos), len(unicos))
        idx = np.concatenate([indices[g] for g in elegidos])
        if len(np.unique(y[idx])) < 2:
            continue
        muestras.append(metrica(y[idx], pa[idx]) - metrica(y[idx], pb[idx]))
    lo, hi = np.percentile(muestras, [2.5, 97.5])
    return float(punto), float(lo), float(hi)


def mcc05(y, p):
    return matthews_corrcoef(y, (p >= 0.5).astype(int))


def similitud_prueba(smiles_ajuste, smiles_prueba) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fa = [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in smiles_ajuste]
    fp = [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in smiles_prueba]
    return np.array([max(DataStructs.BulkTanimotoSimilarity(f, fa)) for f in fp])


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    columnas = list(pd.read_parquet(PROCESADOS / DESCRIPTORES["descriptores"]).columns)
    object.__setattr__(t, "columnas", columnas)
    meta = t.meta
    y = np.asarray(t.y)
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelos": list(MODELOS), "semillas": list(SEMILLAS), "pliegues": 5,
              "umbrales_similitud": list(UMBRALES_SIMILITUD), "grupo_maximo": MAX_GRUPO,
              "remuestras_bootstrap": REMUESTRAS, "filas": int(len(y)),
              "toca_prueba": "solo SMILES, sin etiquetas ni predicciones (acceso estructural)",
              "metrica_principal_pareada": "auroc"}
    with Corrida("escalera-ampliada-permeabilidad", decision="1.2", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        S = similitudes(meta["SMILES"].tolist())
        sin = "SIN_ANDAMIO"
        andamio = meta["andamio"].fillna(sin).to_numpy()
        esqueleto = meta["esqueleto"].to_numpy()
        opciones = {"1 al azar": np.arange(len(meta)),
                    "3 por andamio": np.where(andamio == sin, esqueleto, andamio),
                    "4 andamio + esqueleto (actual)": t.grupos}
        for u in UMBRALES_SIMILITUD:
            opciones[f"5 similitud ≥ {u}"] = grupos_por_similitud(S, u)

        filas_m, filas_p = [], []
        for nombre, g in opciones.items():
            g = np.asarray(g)
            _, cuenta = np.unique(g, return_counts=True)
            if cuenta.max() / len(g) > MAX_GRUPO:
                print(f"{nombre}: no evaluable")
                continue
            print(f"== {nombre} · {len(cuenta)} grupos ==", flush=True)
            res, oof = evaluar(todos_los_modelos(), t.X, y, g, semillas=SEMILLAS, verboso=False)
            vecino = vecino_mas_cercano(S, y, g)
            for modelo, d in res[res["estrato"] == "todos"].groupby("modelo"):
                filas_m.append({"agrupacion": nombre, "modelo": modelo, "grupos": len(cuenta),
                                "auroc": round(float(d["auroc"].mean()), 4),
                                "mcc": round(float(d["mcc"].mean()), 4),
                                "vecino_mas_cercano": round(vecino, 4)})
            # pareadas con la semilla 0 (predicciones fuera de pliegue)
            for a, b in (("logistica", "svm_rbf"), ("bosque", "svm_rbf"), ("knn", "svm_rbf")):
                for etiqueta, f in (("auroc", roc_auc_score), ("mcc", mcc05)):
                    d, lo, hi = diferencia_pareada(y, oof[a][0], oof[b][0], g, f)
                    filas_p.append({"agrupacion": nombre, "par": f"{a} - {b}", "metrica": etiqueta,
                                    "dif": round(d, 4), "lo": round(lo, 4), "hi": round(hi, 4),
                                    "distinguible": bool(lo > 0 or hi < 0)})
            print(pd.DataFrame(filas_m).query("agrupacion == @nombre").to_string(index=False),
                  flush=True)

        tabla_m, tabla_p = pd.DataFrame(filas_m), pd.DataFrame(filas_p)
        print("\n== diferencias pareadas (semilla 0, bootstrap de grupos) ==")
        print(tabla_p.to_string(index=False))

        # Acceso estructural a la prueba: solo SMILES.
        bbb = pd.read_parquet(PROCESADOS / "bbb_meta.parquet")
        prueba = tomar_prueba(bbb, final=True,
                              motivo="E1+: similitud estructural de la prueba con el ajuste, solo SMILES, "
                                     "sin etiquetas ni predicciones")
        s_prueba = similitud_prueba(meta["SMILES"].tolist(), prueba["SMILES"].tolist())
        resumen_prueba = {"n": int(len(s_prueba)), "media": round(float(s_prueba.mean()), 4),
                          "mediana": round(float(np.median(s_prueba)), 4),
                          "terciles": [round(float(q), 4) for q in np.quantile(s_prueba, [1 / 3, 2 / 3])]}
        print("\nprueba reservada, similitud al vecino más cercano del ajuste:", resumen_prueba)

        c.metricas({"e1_ampliada": json_seguro(tabla_m), "pareadas": json_seguro(tabla_p),
                    "prueba_similitud": resumen_prueba})


if __name__ == "__main__":
    main()
