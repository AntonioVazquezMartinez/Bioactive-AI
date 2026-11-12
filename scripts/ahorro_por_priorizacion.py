#!/usr/bin/env python3
"""Cuántos ensayos se evitan y cuántos candidatos reales se pierden al ensayar solo lo mejor ordenado (fase 1).

Es la base medida del resumen ejecutivo: en lugar de suponer un porcentaje de ahorro, se lee de las
probabilidades que el modelo final dio a los 1,499 compuestos de la prueba reservada. Si solo se ensaya la
fracción de compuestos con mayor probabilidad de cruzar la barrera, ¿qué fracción de los permeables reales
queda dentro (cobertura) y qué tan seguido acierta lo que se ensaya (aciertos entre lo ensayado)?

**No abre la prueba reservada de nuevo**: lee `prueba_predicciones.csv`, que la lectura registrada de la C.5
(`2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba`) ya dejó versionado, con sus etiquetas. No pide
`incluir_prueba` ni `tomar_prueba`, así que no suma una lectura a `experimentos/prueba.csv`.

La regla se escribió antes de correr: fracciones ensayadas de 30% a 90%, en pasos de 10, y el intervalo del 95%
remuestrea los **grupos de andamio**, no las filas. Se compara contra ensayar al azar, que cubre lo mismo que la
fracción ensayada.

    ./env312/bin/python scripts/ahorro_por_priorizacion.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from src.tracking import Corrida

ORIGEN = RAIZ / "experimentos" / "2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba" / "prueba_predicciones.csv"
FRACCIONES = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def medir(y: np.ndarray, p: np.ndarray, fraccion: float) -> tuple[float, float]:
    """Cobertura de los permeables y aciertos entre lo ensayado, al ensayar la fracción mejor ordenada."""
    n = int(round(fraccion * len(y)))
    elegidos = np.argsort(-p, kind="stable")[:n]
    return float(y[elegidos].sum() / y.sum()), float(y[elegidos].mean())


def main() -> None:
    d = pd.read_csv(ORIGEN)
    y, p, g = d["y"].to_numpy(), d["probabilidad"].to_numpy(), d["grupo"].to_numpy()
    params = {"fracciones_ensayadas": FRACCIONES, "remuestras": 2000, "toca_prueba": False,
              "origen": str(ORIGEN.relative_to(RAIZ)), "prevalencia": float(y.mean()), "n": int(len(y))}
    with Corrida("ahorro-por-priorizacion-fase1", decision="C.5", params=params, semillas=[0], datos=[ORIGEN]) as c:
        rng = np.random.default_rng(0)
        indices = pd.Series(np.arange(len(d))).groupby(g).apply(lambda s: s.to_numpy())
        grupos = list(indices)
        filas = []
        for f in FRACCIONES:
            cob, acierto = medir(y, p, f)
            cobs, aciertos = [], []
            for _ in range(2000):
                idx = np.concatenate([grupos[i] for i in rng.integers(0, len(grupos), len(grupos))])
                co, ac = medir(y[idx], p[idx], f)
                cobs.append(co)
                aciertos.append(ac)
            filas.append({"fraccion_ensayada": f, "ensayos_evitados": round(1 - f, 2),
                          "cobertura_permeables": round(cob, 4),
                          "cobertura_ic95_inf": round(float(np.percentile(cobs, 2.5)), 4),
                          "cobertura_ic95_sup": round(float(np.percentile(cobs, 97.5)), 4),
                          "aciertos_entre_lo_ensayado": round(acierto, 4),
                          "cobertura_al_azar": f})
        tabla = pd.DataFrame(filas)
        tabla.to_csv(c.carpeta / "ahorro.csv", index=False)
        print(tabla.to_string(index=False))
        c.metricas({"prevalencia": float(y.mean()), "n": int(len(y)), "por_fraccion": tabla.to_dict("records")})


if __name__ == "__main__":
    main()
