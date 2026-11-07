#!/usr/bin/env python3
"""¿Cuánto de lo que llamamos «ruido» es la semilla del modelo y no la partición? (E16, fase 1)

Los intervalos del proyecto remuestrean grupos y las semillas cambian el reparto en pliegues, **no el
modelo**: el arnés lo dice en su propio código (`src/evaluation/cv.py`, «la semilla cambia la partición,
no el modelo»). Eso deja sin medir cuánto se mueve una cifra al cambiar la semilla del modelo con la
partición fija. Aquí se mide, para los seis modelos de la escalera.

**Qué se mide.** Para cada modelo, partición fija por semilla (0, 1, 2 × 5 pliegues = 15 evaluaciones) y
cinco semillas de modelo (0 a 4). En cada evaluación, la desviación estándar del MCC y del AUROC **entre
semillas del modelo**; se promedia sobre las 15 evaluaciones. Se compara con desviaciones pareadas que el
proyecto ha registrado al leer diferencias de MCC: 0.0054 (`svm_rbf` contra su variante de calibración
agrupada, corrida `2026-11-04-artemio-1.5-calibracion-svm-agrupada-permeabilidad`) y 0.0132 (`aft`
contra bosque, corrida `2026-11-04-artemio-2.13-mcc-por-umbral-aft-contra-bosque`).

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. La semilla del modelo **importa** para un modelo si su desviación entre semillas del modelo, en MCC,
   es de al menos **0.005** (del orden de la menor desviación pareada con la que se ha leído una
   diferencia de MCC, 0.0054). Si es menor, la semilla del modelo es despreciable para ese modelo.
2. Un modelo determinista (la misma predicción con cualquier semilla) tendrá desviación 0 y se reporta
   como tal; no es un hallazgo sino una comprobación.
3. Se reporta qué modelos de los seis importan y cuánto, y se dice qué cifras del proyecto (la
   comparativa de once modelos de la fase 1, 4.2 puntos entre extremos) quedan dentro de esa varianza.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_semilla_del_modelo.py
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

import pandas as pd

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.baseline import canalizaciones
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS_PARTICION = (0, 1, 2)
SEMILLAS_MODELO = (0, 1, 2, 3, 4)
MODELOS = ("svm_rbf", "logistica", "mlp", "knn", "bosque", "boosting")
UMBRAL_MCC = 0.005


def modelos(semilla: int) -> dict:
    p = seleccion(("svm_rbf", "logistica", "mlp", "knn"), semilla)
    b = canalizaciones(semilla)
    p["bosque"], p["boosting"] = b["bosque"], b["boosting"]
    return {k: p[k] for k in MODELOS}


def main() -> None:
    t = cargar("permeabilidad")
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelos": list(MODELOS), "semillas_particion": list(SEMILLAS_PARTICION),
              "semillas_modelo": list(SEMILLAS_MODELO), "umbral_mcc": UMBRAL_MCC, "filas": int(len(t.y)),
              "toca_prueba": False}
    with Corrida("semilla-del-modelo-permeabilidad", decision="1.5", params=params,
                 semillas=list(SEMILLAS_MODELO), datos=datos) as c:
        partes = []
        for sm in SEMILLAS_MODELO:
            t0 = time.perf_counter()
            res, _ = evaluar(modelos(sm), t.X, t.y, t.grupos, semillas=SEMILLAS_PARTICION, verboso=False)
            r = res[res["estrato"] == "todos"].copy()
            r["semilla_modelo"] = sm
            partes.append(r[["modelo", "semilla", "pliegue", "semilla_modelo", "mcc", "auroc"]])
            pd.concat(partes, ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
            print(f"  semilla de modelo {sm}: {time.perf_counter() - t0:.0f} s", flush=True)
        res = pd.concat(partes, ignore_index=True)
        filas = []
        for modelo, g in res.groupby("modelo"):
            fila = {"modelo": modelo}
            for m in ("mcc", "auroc"):
                por_eval = g.groupby(["semilla", "pliegue"])[m].std(ddof=1)
                fila[f"desv_entre_semillas_de_modelo_{m}"] = round(float(por_eval.mean()), 5)
                fila[f"maximo_{m}"] = round(float(por_eval.max()), 5)
            fila["importa"] = bool(fila["desv_entre_semillas_de_modelo_mcc"] >= UMBRAL_MCC)
            fila["determinista"] = bool(fila["maximo_mcc"] == 0.0)
            filas.append(fila)
        tabla = pd.DataFrame(filas).set_index("modelo")
        print(tabla.to_string())
        c.metricas({"por_modelo": tabla.reset_index().to_dict("records"),
                    "importan": [k for k, v in tabla.iterrows() if v["importa"]]})
        print("\nimportan:", [k for k, v in tabla.iterrows() if v["importa"]])


if __name__ == "__main__":
    main()
