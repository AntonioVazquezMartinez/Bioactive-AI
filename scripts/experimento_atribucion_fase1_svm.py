#!/usr/bin/env python3
"""Los dos métodos de atribución de la fase 1, sobre el MISMO modelo (el `svm_rbf` final).

Parte del comentario de Grettel del 3 de noviembre sobre el 05: la intersección de la C.2 mezclaba la
permutación sobre el SVM con la impureza de un **bosque**, que son dos modelos distintos. Aquí los dos
métodos miran el mismo `svm_rbf`:

1. permutación de columnas, caída de MCC en el pliegue de evaluación (5 repeticiones);
2. KernelSHAP sobre la probabilidad BBB+, media del |valor| en el pliegue de evaluación.

**Regla declarada antes de correr.** Mismos 5 pliegues agrupados que el cuaderno 05 (semilla 0). En cada
pliegue KernelSHAP explica 60 compuestos de evaluación elegidos al azar (semilla del pliegue), con fondo
de 10 centroides de k-means del ajuste y 400 muestras. Se agrega por la media entre pliegues. Se reportan
las 15 primeras de cada método y su intersección; si tiene menos de 5 columnas se reporta que **los métodos
no coinciden** (eso es un resultado, no se afina). Además, correlación de Spearman entre los dos rankings
completos, el contraste con TPSA y NumHDonors, y la estabilidad: la intersección se repite con otra
muestra de compuestos explicados (semilla distinta) y se reporta cuántas columnas comparte con la primera.
No toca la prueba reservada. Con 400 muestras y 151 columnas KernelSHAP es ruidoso por compuesto; la
agregación entre 300 compuestos y 5 pliegues es lo que se lee, y la estabilidad dice si alcanza.

    python scripts/experimento_atribucion_fase1_svm.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedGroupKFold

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.models import cargar, seleccion  # noqa: E402
from src.tracking import Corrida  # noqa: E402

warnings.filterwarnings("ignore")
PRIMERAS = 15
EXPLICADOS = 60
FONDO = 10
MUESTRAS = 400


def atribuir(t, semilla_muestra: int) -> pd.DataFrame:
    X, y, g = t.X, t.y, t.grupos
    final = seleccion(("svm_rbf",))["svm_rbf"]
    filas = []
    for k, (ajuste, val) in enumerate(StratifiedGroupKFold(5, shuffle=True, random_state=0).split(X, y, g), 1):
        m = clone(final).fit(X[ajuste], y[ajuste])
        perm = permutation_importance(m, X[val], y[val], n_repeats=5, random_state=k, scoring="matthews_corrcoef")
        rng = np.random.default_rng(1000 * semilla_muestra + k)
        elegidos = rng.choice(val, EXPLICADOS, replace=False)
        fondo = shap.kmeans(X[ajuste], FONDO)
        f = lambda a: m.predict_proba(a)[:, 1]  # noqa: E731
        phi = shap.KernelExplainer(f, fondo).shap_values(X[elegidos], nsamples=MUESTRAS, silent=True)
        shap_abs = np.abs(np.asarray(phi)).mean(axis=0)
        for j, nombre in enumerate(t.columnas):
            filas.append({"caracteristica": nombre, "pliegue": k,
                          "permutacion": perm.importances_mean[j], "shap": shap_abs[j]})
        print(f"  semilla {semilla_muestra} · pliegue {k} de 5", flush=True)
    d = pd.DataFrame(filas).groupby("caracteristica", as_index=False)[["permutacion", "shap"]].mean()
    d["r_perm"] = d["permutacion"].rank(ascending=False)
    d["r_shap"] = d["shap"].rank(ascending=False)
    return d


def interseccion(d: pd.DataFrame) -> list[str]:
    a = set(d.nsmallest(PRIMERAS, "r_perm")["caracteristica"])
    b = set(d.nsmallest(PRIMERAS, "r_shap")["caracteristica"])
    return sorted(a & b)


def main() -> None:
    t = cargar("permeabilidad")
    assert len(t.columnas) == t.X.shape[1]
    with Corrida("atribucion-fase1-svm-dos-metodos", decision="C.2",
                 params={"modelo": "svm_rbf", "metodos": ["permutacion MCC", "KernelSHAP |phi| medio"],
                         "explicados_por_pliegue": EXPLICADOS, "fondo_kmeans": FONDO, "muestras": MUESTRAS,
                         "primeras": PRIMERAS, "pliegues": 5},
                 semillas=[0, 1], datos=[RAIZ / "data" / "processed" / "bbb_meta.parquet"]) as c:
        d0, d1 = atribuir(t, 0), atribuir(t, 1)
        d0.to_csv(c.carpeta / "atribucion_semilla0.csv", index=False)
        d1.to_csv(c.carpeta / "atribucion_semilla1.csv", index=False)
        i0, i1 = interseccion(d0), interseccion(d1)
        rho = float(spearmanr(d0["permutacion"], d0["shap"]).statistic)
        res = {
            "interseccion_semilla0": i0, "interseccion_semilla1": i1,
            "comparten_entre_semillas": sorted(set(i0) & set(i1)),
            "spearman_entre_metodos": rho,
            "spearman_shap_entre_semillas": float(spearmanr(d0["shap"], d1["shap"]).statistic),
            "los_metodos_no_coinciden": len(i0) < 5,
            "contraste_c2": {n: {"puesto_permutacion": int(d0.loc[d0["caracteristica"] == n, "r_perm"].iloc[0]),
                                 "puesto_shap": int(d0.loc[d0["caracteristica"] == n, "r_shap"].iloc[0])}
                             for n in ("TPSA", "NumHDonors")},
            "antes_con_bosque": ["fr_lactam", "NumHDonors", "VSA_EState3", "MolLogP"],
        }
        c.metricas(res)
    for k, v in res.items():
        print(k, v)
    for nombre, col in (("permutación", "r_perm"), ("KernelSHAP", "r_shap")):
        print(f"\n=== las {PRIMERAS} primeras por {nombre} (semilla 0) ===")
        print(d0.nsmallest(PRIMERAS, col)[["caracteristica", "permutacion", "shap"]].to_string(index=False))


if __name__ == "__main__":
    main()
