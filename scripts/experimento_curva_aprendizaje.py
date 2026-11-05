#!/usr/bin/env python3
"""E8 · curva de aprendizaje agrupada: ¿añadir filas mejora al modelo final? (decide qué se sirve)

La patrocinadora recibirá un modelo servido. Se puede reentrenar con las filas de ajuste (lo que
se evaluó) o añadir las de la prueba reservada (fase 1: +1,499 a 6,306; fase 2: +13,944 a 56,241).
Añadirlas da un modelo mejor *si* faltan datos, y uno que ya no se puede evaluar. Esta corrida
decide con evidencia, **antes de tocar nada de la prueba**, si faltan datos.

**Diseño.** Para cada pliegue agrupado (3 semillas × 5 pliegues) se ajusta el modelo final de la
fase —`svm_rbf` en la fase 1, `aft` en la fase 2— con el 25, 50, 75 y 100% de los **grupos** del
pliegue de ajuste (se submuestrean grupos, no filas) y se mide siempre sobre el mismo pliegue de
validación, así que las diferencias entre fracciones son pareadas. Métricas: AUROC y MCC (fase 1),
concordancia de Harrell (fase 2).

**Lo que se declara antes de correr.**
- Se mide la ganancia del último escalón, 75% → 100%, pareada por evaluación (15).
- *Faltan datos* si la ganancia media es positiva y lo es en al menos 12 de las 15 evaluaciones,
  **y** supera 0.005 (AUROC o concordancia). Si no, añadir filas no se justifica con esta curva.
- Además se ajusta `metrica = a + b·ln(n)` por mínimos cuadrados sobre las cuatro fracciones y se
  proyecta la ganancia de añadir las filas de la prueba (`b·ln(n_total / n_ajuste)`); es una
  proyección, no una medición, y se reporta como tal.
- La prueba reservada **no se lee**. Los números de filas que se proyectan vienen de los
  conteos ya registrados.
- Límite que se asume: la prueba tiene andamios raros a propósito, así que sus filas pueden
  aportar más (o menos) que filas parecidas a las de ajuste; la curva no lo mide.

    ./env/bin/python scripts/experimento_curva_aprendizaje.py
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

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from src.evaluation.regresion import concordancia_harrell
from src.models.alternativos import seleccion
from src.models.aft import RegresionAFT
from src.models.tareas import PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
FRACCIONES = (0.25, 0.5, 0.75, 1.0)
MIN_GANANCIA = 0.005
MIN_EVALUACIONES = 12
# Conteos ya registrados (no se leen de la prueba): filas de ajuste y de prueba por fase.
FILAS = {"fase1": (6306, 1499), "fase2": (56241, 13944)}
PARES = PROCESADOS / "fase2_pares.parquet"
DESC2 = PROCESADOS / "fase2_descriptores_limpios.parquet"


def submuestra_de_grupos(ajuste, grupos, fraccion, rng):
    """Índices de `ajuste` que caen en una fracción de sus grupos (por filas, ~fraccion)."""
    if fraccion >= 1.0:
        return ajuste
    g = grupos[ajuste]
    unicos = rng.permutation(np.unique(g))
    tam = {u: n for u, n in zip(*np.unique(g, return_counts=True))}
    meta, acum, elegidos = fraccion * len(ajuste), 0, []
    for u in unicos:
        if acum >= meta:
            break
        elegidos.append(u)
        acum += tam[u]
    return ajuste[np.isin(g, elegidos)]


def curva(X, y_estrat, grupos, ajustar_y_medir, etiqueta):
    filas = []
    for semilla in SEMILLAS:
        cv = StratifiedGroupKFold(5, shuffle=True, random_state=semilla)
        for k, (aj, val) in enumerate(cv.split(X, y_estrat, grupos), 1):
            for f in FRACCIONES:
                rng = np.random.default_rng(1000 * semilla + k)
                sub = submuestra_de_grupos(aj, grupos, f, rng)
                t0 = time.perf_counter()
                met = ajustar_y_medir(sub, val)
                filas.append({"fase": etiqueta, "semilla": semilla, "pliegue": k, "fraccion": f,
                              "n_ajuste": int(len(sub)), **met})
            print(f"  {etiqueta} semilla {semilla} pliegue {k} ({time.perf_counter() - t0:.0f} s último)",
                  flush=True)
    return pd.DataFrame(filas)


def resumen(df, metrica, etiqueta):
    ancho = df.pivot_table(index=["semilla", "pliegue"], columns="fraccion", values=metrica)
    n_medio = df.groupby("fraccion")["n_ajuste"].mean()
    ganancia = ancho[1.0] - ancho[0.75]
    media_f = ancho.mean()
    # a + b ln(n), ajustado sobre las medias por fracción
    b, a = np.polyfit(np.log(n_medio.to_numpy()), media_f.to_numpy(), 1)
    n_aj, n_pr = FILAS[etiqueta]
    proyeccion = float(b * np.log((n_aj + n_pr) / n_aj))
    faltan = bool(ganancia.mean() > MIN_GANANCIA and (ganancia > 0).sum() >= MIN_EVALUACIONES)
    return {"fase": etiqueta, "metrica": metrica,
            "por_fraccion": {str(k): round(float(v), 4) for k, v in media_f.items()},
            "n_medio": {str(k): int(v) for k, v in n_medio.items()},
            "ganancia_75_a_100": round(float(ganancia.mean()), 4),
            "desv_ganancia": round(float(ganancia.std()), 4),
            "positiva_en": f"{int((ganancia > 0).sum())} de {len(ganancia)}",
            "pendiente_por_ln_n": round(float(b), 4),
            "proyeccion_con_filas_de_prueba": round(proyeccion, 4),
            "faltan_datos_segun_regla": faltan}


def fase1():
    t = cargar("permeabilidad")
    X, y, g = np.asarray(t.X, float), np.asarray(t.y), np.asarray(t.grupos)
    modelo = seleccion(("svm_rbf",))["svm_rbf"]

    def medir(sub, val):
        m = clone(modelo).fit(X[sub], y[sub])
        p = m.predict_proba(X[val])[:, 1]
        return {"auroc": roc_auc_score(y[val], p), "mcc": matthews_corrcoef(y[val], (p >= 0.5).astype(int))}
    return curva(X, y, g, medir, "fase1")


def fase2():
    pares, desc = pd.read_parquet(PARES), pd.read_parquet(DESC2)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [c for c in desc.columns if c != "smiles"]
    inf, sup = d["limite_inferior"].to_numpy(float), d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inf) & np.isposinf(sup)) & (inf <= sup)
    d, inf, sup = d[util].reset_index(drop=True), inf[util], sup[util]
    fuera = (d["particion"] != "prueba").to_numpy()
    X = np.hstack([d[cols].to_numpy("float32"), pd.get_dummies(d["target_gene"]).to_numpy("float32")])[fuera]
    inf, sup, g = inf[fuera], sup[fuera], d["grupo_cv"].to_numpy()[fuera]
    clase = np.where(np.isnan(d["activo_10um"].to_numpy(float)[fuera]), -1,
                     d["activo_10um"].to_numpy(float)[fuera]).astype(int)
    assert len(inf) == 56_241

    def medir(sub, val):
        m = RegresionAFT(semilla=0).fit(X[sub], inf[sub], sup[sub])
        return {"concordancia": concordancia_harrell(inf[val], sup[val], m.predict(X[val]))}
    return curva(X, clase, g, medir, "fase2")


def main() -> None:
    params = {"fracciones": list(FRACCIONES), "semillas": list(SEMILLAS), "pliegues": 5,
              "modelos": {"fase1": "svm_rbf", "fase2": "aft"}, "submuestreo": "grupos",
              "regla": {"min_ganancia": MIN_GANANCIA, "min_evaluaciones": MIN_EVALUACIONES,
                        "escalon": "75% a 100%"},
              "filas_registradas": FILAS, "toca_prueba": False}
    with Corrida("curva-aprendizaje-modelos-finales", decision="1.5", params=params,
                 semillas=list(SEMILLAS), datos=[PROCESADOS / "bbb_meta.parquet", PARES, DESC2]) as c:
        c1, c2 = fase1(), fase2()
        res = [resumen(c1, "auroc", "fase1"), resumen(c1, "mcc", "fase1"),
               resumen(c2, "concordancia", "fase2")]
        pd.concat([c1, c2], ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
        for r in res:
            print(r)
        c.metricas({"curvas": res})


if __name__ == "__main__":
    main()
