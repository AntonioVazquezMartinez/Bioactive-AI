#!/usr/bin/env python3
"""E6 (fase 2) · ¿lo que aportan las huellas al `aft` depende del tamaño de la molécula? (#215)

Mitad de fase 2 de la prueba cuya mitad de fase 1 es `experimento_tamano_fase1.py` (las huellas no
ayudan en ningún tramo ni hay tendencia con el peso). Aquí se mide, con el mismo diseño, cuánto
cambia la **concordancia de Harrell** del `aft` al añadir las huellas Sort & Slice, **por tramo de
peso molecular** (los cortes fijos de `etiquetas_por_tamano`, los mismos que en la fase 1) y, como
segundo corte, por procedencia dentro de cada tramo para `solo_chembl`.

**Lo que se declara antes de correr.**
- Brazos: `aft` (descriptores y diana, el modelo final) y `aft_huellas` (lo mismo más 2,048 bits,
  vocabulario relearned dentro del pliegue; conserva las columnas densas). Semillas 0, 1, 2 y
  5 pliegues: las mismas que la corrida de la 2.13, y las mismas filas (56,241).
- Lectura principal: la diferencia **pareada** de concordancia (`aft_huellas` − `aft`) por tramo,
  su media y en cuántas de las 15 evaluaciones es positiva. Un tramo se reporta si tiene al
  menos 1,000 pares de validación en el pliegue.
- La hipótesis de tamaño dice que las huellas ayudan más a las moléculas grandes. Se sostiene en
  la fase 2 si la ganancia **crece con el tramo** (el último mayor que el primero y el orden
  mayormente monótono); si es plana, no se sostiene, y no se reinterpreta.
- **El tramo de arriba no es el mismo en las dos fases** (va hasta 1,449 Da en la fase 1 y hasta
  4,114 en la fase 2), y se reporta diciendo qué población cubre. No se iguala el tamaño de los
  tramos por submuestreo; si aparece un patrón, es la corrida siguiente. No toca la prueba.

    ./env/bin/python scripts/experimento_tamano_fase2.py     # unos 40 min en macOS con 16 núcleos
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
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold

from experimento_aft_huellas import DESCRIPTORES, N_BITS, PARES, PLIEGUES, SEMILLAS, datos
from src.evaluation.regresion import concordancia_harrell
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado
from src.models.tareas import etiquetas_por_tamano
from src.tracking import Corrida

MIN_PARES = 1000


def pesos_moleculares() -> np.ndarray:
    """MolWt de las mismas filas y en el mismo orden que `datos()` (ajuste, con intervalo útil)."""
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)
    d = d[util].reset_index(drop=True)
    return d["MolWt"].to_numpy(float)[(d["particion"] != "prueba").to_numpy()]


def main() -> None:
    d = datos()
    peso = pesos_moleculares()
    assert len(peso) == len(d["inferior"]), "los pesos no son de las mismas filas que la matriz"
    tramo = etiquetas_por_tamano(peso)
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    brazos = {"aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
              "aft_huellas": ("X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]),
                                                             d["n_densas"], N_BITS))}
    params = {"brazos": list(brazos), "semillas": list(SEMILLAS), "pliegues": PLIEGUES,
              "n_bits": N_BITS, "tramos": sorted(set(tramo)), "min_pares_validacion": MIN_PARES,
              "filas": int(len(tramo)), "toca_prueba": False,
              "peso_maximo_ajuste": float(peso.max()), "iguala_tramos": False,
              "metrica_principal": "diferencia pareada de concordancia por tramo"}
    with Corrida("tamano-huellas-actividad", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        filas = []
        for semilla in SEMILLAS:
            cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=semilla)
            for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
                preds = {}
                for nombre, (matriz, modelo) in brazos.items():
                    t0 = time.perf_counter()
                    m = clone(modelo)
                    m.fit(d[matriz][aj], d["inferior"][aj], d["superior"][aj])
                    preds[nombre] = m.predict(d[matriz][val])
                    print(f"  semilla {semilla} pliegue {k} {nombre} {time.perf_counter() - t0:.0f} s",
                          flush=True)
                for etiqueta in ("todos", *sorted(set(tramo))):
                    sel = np.ones(len(val), bool) if etiqueta == "todos" else tramo[val] == etiqueta
                    if sel.sum() < MIN_PARES:
                        continue
                    fila = {"semilla": semilla, "pliegue": k, "tramo": etiqueta, "n": int(sel.sum())}
                    for nombre, p in preds.items():
                        fila[nombre] = concordancia_harrell(d["inferior"][val][sel],
                                                            d["superior"][val][sel], p[sel])
                    filas.append(fila)
        res = pd.DataFrame(filas)
        res["dif"] = res["aft_huellas"] - res["aft"]
        res.to_csv(c.carpeta / "pliegues.csv", index=False)
        tabla = (res.groupby("tramo").agg(n_medio=("n", "mean"), evaluaciones=("dif", "size"),
                                          aft=("aft", "mean"), aft_huellas=("aft_huellas", "mean"),
                                          dif=("dif", "mean"),
                                          mejora_en=("dif", lambda s: int((s > 0).sum())))
                 .round(4).reset_index())
        print(tabla.to_string(index=False))
        c.metricas({"por_tramo": tabla.to_dict("records")})


if __name__ == "__main__":
    main()
