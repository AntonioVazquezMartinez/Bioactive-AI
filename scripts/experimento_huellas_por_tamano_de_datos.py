#!/usr/bin/env python3
"""¿Las huellas ayudan en la fase 2 y no en la 1 solo porque la fase 2 tiene nueve veces más datos? (E9)

La 1.3 midió que las huellas no mejoran a ningún modelo de la fase 1 (6,306 compuestos) y sí a cinco
de seis en la fase 2 (56,241 pares). Una explicación más simple que la «granularidad de la etiqueta»
es el tamaño: las huellas tienen miles de columnas y suelen pedir más filas. Aquí se somete a la
fase 2 al tamaño de la fase 1 y se mide si la ganancia sobrevive.

**Qué se mide.** El `aft` con y sin huellas (`ConHuellasCensurado`, vocabulario aprendido dentro del
pliegue, con las filas que el modelo ve), con el ajuste submuestreado **por grupos** (`grupo_cv`) a
5,000, 10,000 y 20,000 filas y completo (≈45,000), mismas 15 evaluaciones agrupadas de siempre. La
evaluación es siempre sobre el pliegue de validación completo, así que los números son comparables
entre tamaños. 5,000 es el tamaño de ajuste de un pliegue de la fase 1 (0.8 × 6,306 = 5,045). Los dos
brazos de un pliegue ven **la misma submuestra**.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: con el ajuste completo, `aft` y `aft_huellas` reproducen la concordancia de la corrida
   `2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura` (0.7610 y 0.7659 en `todos`) dentro de
   0.003. Si no, hay un error y el resto no se lee.
2. Sea g(n) la diferencia pareada media de concordancia `aft_huellas − aft` en `todos`, con n filas
   de ajuste. **El tamaño explica la diferencia entre fases** si g(5,000) ≤ 0, o si g(5,000) < 0.5·g(completo)
   y las huellas mejoran en menos de 12 de 15 evaluaciones. **No la explica** si g(5,000) ≥ 0.5·g(completo)
   y mejoran en 12 de 15 o más. Cualquier otro caso es **no concluyente** y se reporta así.
3. Es una sola familia de modelos (el `aft`): lo que se concluya vale para ella, no para los seis
   modelos de la fase 1. Se dice así.
4. Se reporta también `solo_npass`, pero la regla se aplica a `todos`.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_huellas_por_tamano_de_datos.py
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
from experimento_aft_huellas import DESCRIPTORES, N_BITS, PARES, PLIEGUES, SEMILLAS, datos  # noqa: E402
from sklearn.base import BaseEstimator, clone

from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado, evaluar_baselines
from src.tracking import Corrida

TAMANOS = (5_000, 10_000, 20_000, None)       # None = el ajuste completo
REFERENCIA = {"aft": 0.7610, "aft_huellas": 0.7659}   # de: 2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura
TOLERANCIA = 0.003
REGLA_EVALUACIONES = 12


class Submuestreado(BaseEstimator):
    """Ajusta el modelo con grupos completos hasta reunir `n_filas`; evalúa con lo que se le pida.

    La submuestra depende de la semilla y del tamaño del ajuste, no del modelo: dos brazos con la misma
    semilla ven las mismas filas en un pliegue.
    """

    necesita_grupos = True

    def __init__(self, modelo, n_filas=None, semilla: int = 0):
        self.modelo = modelo
        self.n_filas = n_filas
        self.semilla = semilla

    def fit(self, X, inferior, superior, grupos=None):
        n = X.shape[0]
        if self.n_filas is None or self.n_filas >= n:
            idx = np.arange(n)
        else:
            rng = np.random.default_rng([self.semilla, n])
            unicos, inv, cuenta = np.unique(grupos, return_inverse=True, return_counts=True)
            orden = rng.permutation(len(unicos))
            elegidos = orden[np.cumsum(cuenta[orden]) - cuenta[orden] < self.n_filas]
            idx = np.flatnonzero(np.isin(inv, elegidos))
        self.n_ajuste_ = int(len(idx))
        self.modelo_ = clone(self.modelo)
        self.modelo_.fit(X[idx], inferior[idx], superior[idx])
        return self

    def predict(self, X):
        return self.modelo_.predict(X)


def pareado(res: pd.DataFrame, estrato: str) -> dict:
    sub = res[res["estrato"] == estrato]
    piv = sub.pivot_table(index=["semilla", "pliegue"], columns="modelo", values="concordancia").dropna()
    dif = piv["aft_huellas"] - piv["aft"]
    return {"aft": round(float(piv["aft"].mean()), 4), "aft_huellas": round(float(piv["aft_huellas"].mean()), 4),
            "dif_media": round(float(dif.mean()), 4), "dif_desv": round(float(dif.std()), 4),
            "huellas_mejor_en": int((dif > 0).sum()), "evaluaciones": int(len(dif))}


def main() -> None:
    d = datos()
    params = {"tamanos": [t if t else "completo" for t in TAMANOS], "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "n_bits_sortslice": N_BITS, "submuestreo": "por grupos grupo_cv",
              "referencia_control": REFERENCIA, "tolerancia": TOLERANCIA,
              "regla_evaluaciones": REGLA_EVALUACIONES, "toca_prueba": False,
              "tamano_de_un_ajuste_de_la_fase_1": 5045}
    with Corrida("huellas-por-tamano-de-datos-actividad", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        partes = []
        for n in TAMANOS:
            etiqueta = "completo" if n is None else str(n)
            for nombre, matriz, modelo in (
                    ("aft", "X", RegresionAFT(semilla=SEMILLAS[0])),
                    ("aft_huellas", "X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]),
                                                                    d["n_densas"], N_BITS))):
                t = time.perf_counter()
                r = evaluar_baselines(d[matriz], d["inferior"], d["superior"], d["grupos"], d["procedencia"],
                                      d["clase"], semillas=SEMILLAS, pliegues=PLIEGUES,
                                      modelos={nombre: Submuestreado(modelo, n_filas=n, semilla=SEMILLAS[0])})
                r["n_ajuste"] = etiqueta
                partes.append(r)
                pd.concat(partes, ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
                print(f"  n={etiqueta:>8} {nombre:12}{time.perf_counter() - t:6.0f} s", flush=True)
        res = pd.concat(partes, ignore_index=True)

        salida = {}
        for etiqueta in [("completo" if n is None else str(n)) for n in TAMANOS]:
            sub = res[res["n_ajuste"] == etiqueta]
            salida[etiqueta] = {e: pareado(sub, e) for e in ("todos", "solo_npass")}
        completo = salida["completo"]["todos"]
        control = {m: abs(completo[m] - REFERENCIA[m]) <= TOLERANCIA for m in REFERENCIA}
        g5, gc = salida["5000"]["todos"], completo
        if g5["dif_media"] <= 0 or (g5["dif_media"] < 0.5 * gc["dif_media"] and g5["huellas_mejor_en"] < REGLA_EVALUACIONES):
            veredicto = "el tamaño explica la diferencia"
        elif g5["dif_media"] >= 0.5 * gc["dif_media"] and g5["huellas_mejor_en"] >= REGLA_EVALUACIONES:
            veredicto = "el tamaño no la explica"
        else:
            veredicto = "no concluyente"
        c.metricas({"por_tamano": salida, "control_dentro_de_tolerancia": control,
                    "referencia_control": REFERENCIA, "veredicto_declarado": veredicto})
        print(f"\ncontrol: {control}\nveredicto por la regla declarada: {veredicto}")
        for etiqueta, v in salida.items():
            print(f"n={etiqueta:>8}  todos {v['todos']}")
            print(f"{'':11}solo_npass {v['solo_npass']}")


if __name__ == "__main__":
    main()
