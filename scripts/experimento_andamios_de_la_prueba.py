#!/usr/bin/env python3
"""Qué proporción de la prueba reservada tiene andamio o esqueleto que el entrenamiento no vio.

Parte del comentario de Grettel del 3 de noviembre: la prueba solo dice algo sobre
generalización si sus estructuras no están ya en el ajuste.

**Regla declarada antes de correr.** Para cada fase, la proporción de filas de la prueba
(y de la validación, como referencia) cuyo andamio de Bemis-Murcko, o cuyo esqueleto de
conectividad, no aparece en entrenamiento. No usa etiquetas y no entrena nada; solo
columnas estructurales. Se reporta también por `natural` en la fase 1. Si la proporción
es menor a 0.95 en la prueba, algo del agrupamiento no se cumple y se investiga antes
de seguir.

Toca la partición de prueba, y por eso pasa por `tomar_prueba` (queda una línea en
`experimentos/prueba.csv` por fase).

    python scripts/experimento_andamios_de_la_prueba.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.tracking import Corrida, tomar_prueba  # noqa: E402

FASE1 = RAIZ / "data" / "processed" / "bbb_meta.parquet"
FASE2 = RAIZ / "data" / "processed" / "fase2_pares.parquet"


def ausentes(d: pd.DataFrame, col: str) -> dict:
    """Fracción de filas y de valores distintos de validación/prueba ausentes del entrenamiento."""
    vistos = set(d.loc[d["particion"] == "entrenamiento", col])
    salida = {}
    for parte in ("validacion", "prueba"):
        x = d[d["particion"] == parte]
        nuevo = ~x[col].isin(vistos)
        salida[parte] = {"filas": int(len(x)), "filas_nuevas": int(nuevo.sum()),
                         "prop_filas": float(nuevo.mean()),
                         "distintos": int(x[col].nunique()),
                         "distintos_nuevos": int(x.loc[nuevo, col].nunique())}
    return salida


def main() -> None:
    # Solo columnas estructurales: la etiqueta ni se carga.
    f1 = pd.read_parquet(FASE1, columns=["andamio", "esqueleto", "natural", "particion"])
    f2 = pd.read_parquet(FASE2, columns=["andamio", "esqueleto", "particion"])
    motivo = "Proporción de andamios y esqueletos de la prueba ausentes del entrenamiento (estructural, sin etiquetas)"
    tomar_prueba(f1, final=True, motivo=motivo + ", fase 1")
    tomar_prueba(f2, final=True, motivo=motivo + ", fase 2")
    res = {}
    for fase, d in (("fase1", f1), ("fase2", f2)):
        for col in ("andamio", "esqueleto"):
            res[f"{fase}_{col}"] = ausentes(d, col)
    vistos = set(f1.loc[f1["particion"] == "entrenamiento", "andamio"])
    prueba = f1[f1["particion"] == "prueba"]
    res["fase1_por_natural"] = {
        str(v): {"filas": int(len(x)), "prop_andamio_nuevo": float((~x["andamio"].isin(vistos)).mean())}
        for v, x in prueba.groupby("natural")}
    with Corrida("andamios-de-la-prueba", decision="1.6", params={"regla": "proporcion ausente del entrenamiento", "toca_prueba": "solo columnas estructurales, sin etiquetas"},
                 semillas=[], datos=[FASE1, FASE2]) as c:
        c.metricas(res)
    for k, v in res.items():
        print(k, v)


if __name__ == "__main__":
    main()
