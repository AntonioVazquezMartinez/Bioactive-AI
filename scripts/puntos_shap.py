#!/usr/bin/env python3
"""Los valores de SHAP **por compuesto** de las dos fases, para dibujar los gráficos de puntos (#303).

Las corridas de atribución (`2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos` y
`2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion`) guardaron solo la media de |SHAP| por columna.
Para ver **en qué dirección** empuja cada columna hace falta el valor de cada compuesto, así que aquí se repiten
los mismos modelos y los mismos pliegues, y se guarda lo que aquellas no guardaron. No cambia ninguna cifra de
desempeño ni toca la prueba reservada.

- **Fase 1** (`svm_rbf`): KernelSHAP sobre la probabilidad BBB+, con las mismas reglas de la corrida original
  (semilla 0, cinco pliegues agrupados, 60 compuestos por pliegue, fondo de 10 centroides, 400 muestras). Los
  300 compuestos explicados son los mismos. Un valor positivo sube la probabilidad de cruzar la barrera.
- **Fase 2** (`aft`): TreeSHAP sobre el margen del modelo, en cinco pliegues agrupados (semilla 0), con 600
  filas de validación por pliegue. **Cada fila es un par compuesto-diana, no un compuesto** (56,241 en total),
  y es una **submuestra**: la corrida original de atribución calculó sobre todas las filas de validación de cada
  pliegue (unas 11,248); aquí se toman 600 por pliegue solo para poder dibujar. Se convierte a la escala de pActividad (`-phi / ln 10`): un valor positivo
  sube la potencia predicha.

Se guardan, por fila, el valor de SHAP y el valor de la columna de las 12 columnas con mayor media de
|SHAP|; el valor de la columna es lo que colorea cada punto.

    ./env312/bin/python scripts/puntos_shap.py [fase1|fase2]
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import math
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold

from scripts.experimento_atribucion_aft import datos as datos_fase2
from src.models import cargar, seleccion
from src.models.aft import RegresionAFT
from src.tracking import Corrida

EXPLICADOS = 60
FONDO = 10
MUESTRAS = 400
FILAS_FASE2 = 600
TOP = 12


def fase1() -> pd.DataFrame:
    t = cargar("permeabilidad")
    final = seleccion(("svm_rbf",))["svm_rbf"]
    filas = []
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=0)
    for k, (ajuste, val) in enumerate(cv.split(t.X, t.y, t.grupos), 1):
        m = clone(final).fit(t.X[ajuste], t.y[ajuste])
        rng = np.random.default_rng(1000 * 0 + k)
        elegidos = rng.choice(val, EXPLICADOS, replace=False)
        fondo = shap.kmeans(t.X[ajuste], FONDO)
        phi = shap.KernelExplainer(lambda a: m.predict_proba(a)[:, 1], fondo).shap_values(
            t.X[elegidos], nsamples=MUESTRAS, silent=True)
        phi = np.asarray(phi)
        for i, fila in enumerate(elegidos):
            for j, nombre in enumerate(t.columnas):
                filas.append((k, int(fila), nombre, float(phi[i, j]), float(t.X[fila, j])))
        print(f"  fase 1 · pliegue {k} de 5", flush=True)
    return pd.DataFrame(filas, columns=["pliegue", "fila", "columna", "shap", "valor"])


def fase2() -> pd.DataFrame:
    d = datos_fase2()
    nombres = np.array(d["nombres"])
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    filas = []
    rng = np.random.default_rng(0)
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=0)
    for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
        m = RegresionAFT(semilla=0).fit(d["X"][aj], d["inferior"][aj], d["superior"][aj])
        elegidos = rng.choice(val, FILAS_FASE2, replace=False)
        Xv = np.asarray(d["X"][elegidos], dtype=float)
        contrib = m.booster_.predict(xgb.DMatrix(Xv), pred_contribs=True)[:, :-1]
        phi = -contrib / math.log(10)           # a la escala de pActividad: positivo = más potente
        for i, fila in enumerate(elegidos):
            for j, nombre in enumerate(nombres):
                filas.append((k, int(fila), str(nombre), float(phi[i, j]), float(Xv[i, j])))
        print(f"  fase 2 · pliegue {k} de 5", flush=True)
    return pd.DataFrame(filas, columns=["pliegue", "fila", "columna", "shap", "valor"])


def quedarse_con_las_primeras(d: pd.DataFrame) -> pd.DataFrame:
    media = d.assign(a=d["shap"].abs()).groupby("columna")["a"].mean().nlargest(TOP)
    return d[d["columna"].isin(media.index)].reset_index(drop=True)


def main() -> None:
    cual = sys.argv[1] if len(sys.argv) > 1 else "ambas"
    params = {"fase1": {"modelo": "svm_rbf", "metodo": "KernelSHAP", "explicados_por_pliegue": EXPLICADOS,
                        "fondo_kmeans": FONDO, "muestras": MUESTRAS},
              "fase2": {"modelo": "aft", "metodo": "TreeSHAP", "filas_por_pliegue": FILAS_FASE2},
              "pliegues": 5, "columnas_guardadas": TOP, "toca_prueba": False, "cual": cual}
    with Corrida("puntos-shap-por-compuesto-" + cual, decision="C.2", params=params, semillas=[0]) as c:
        res = {}
        if cual in ("ambas", "fase1"):
            d1 = quedarse_con_las_primeras(fase1())
            d1.to_csv(c.carpeta / "shap_fase1.csv", index=False)
            res["fase1"] = {"compuestos": int(d1.groupby("columna").size().iloc[0]),
                            "columnas": list(d1.assign(a=d1["shap"].abs()).groupby("columna")["a"].mean()
                                             .sort_values(ascending=False).index)}
        if cual in ("ambas", "fase2"):
            d2 = quedarse_con_las_primeras(fase2())
            d2.to_csv(c.carpeta / "shap_fase2.csv", index=False)
            res["fase2"] = {"pares_compuesto_diana": int(d2.groupby("columna").size().iloc[0]),
                            "columnas": list(d2.assign(a=d2["shap"].abs()).groupby("columna")["a"].mean()
                                             .sort_values(ascending=False).index)}
        c.metricas(res)
        print(res)


if __name__ == "__main__":
    main()
