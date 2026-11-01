#!/usr/bin/env python3
"""Las filas que el filtro del AFT descarta, y sobre qué partición se cuentan.

Evidencia del defecto que la lectura del 05b y la decisión 2.13 citan. El AFT
censurado es el modelo final de la fase 2, y el argumento para elegirlo es que
ajusta con las mediciones censuradas que `SoloExactas` tira. Pero su propio
filtro, en `src/models/aft.py`, exige `inf_um > 0`:

    valida = (inf_um > 0) & np.isfinite(inf_um) & (sup_um >= inf_um)

y eso tira las filas cuya cota inferior en µM es exactamente 0 —las «más potente
que X», donde el límite superior de pActividad es infinito—, que XGBoost AFT
acepta de forma nativa con `label_lower_bound = 0`.

**Y un conteo sin partición no se puede comprobar**, que es la razón de que este
script exista y no una línea en prosa: el mismo filtro da 656 filas sobre
entrenamiento, 745 sobre entrenamiento más validación —que es el conjunto de
ajuste del 05b, el que sus asertos fijan en 56,241— y 972 sobre el archivo
completo, prueba reservada incluida. La cifra que el registro cita es la de
ajuste, porque es la que el modelo ve.

    python scripts/descartadas_aft.py

Se mide sobre `data/processed/fase2_pares.parquet`, antes del cruce con los
descriptores. Ese cruce filtra por química disponible, no por procedencia, así
que el desglose por estrato no se mueve; los totales del cruce son los que el
cuaderno asevera.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.evaluation.regresion import limites_en_micromolar  # noqa: E402

PARES = RAIZ / "data" / "processed" / "fase2_pares.parquet"


def main() -> None:
    if not PARES.exists():
        raise SystemExit(f"falta {PARES}; se genera con scripts/construir_pares_fase2.py")

    d = pd.read_parquet(PARES)
    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)

    # El mismo criterio de utilidad del cuaderno: un intervalo que no dice nada
    # (−inf, +inf) no es una medición, y las cotas cruzadas tampoco.
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)

    inf_um, sup_um = limites_en_micromolar(inferior, superior)
    valida = (inf_um > 0) & np.isfinite(inf_um) & (sup_um >= inf_um)

    particion = d["particion"].to_numpy()
    grupos = {
        "entrenamiento": particion == "entrenamiento",
        "validación": particion == "validacion",
        "ajuste (entrenamiento + validación)": particion != "prueba",
        "prueba reservada": particion == "prueba",
        "archivo completo": np.ones(len(d), bool),
    }

    print(f"{'partición':<38}{'útiles':>9}{'descarta':>10}{'%':>8}")
    for nombre, sel in grupos.items():
        utiles = util & sel
        descarta = utiles & ~valida
        pct = 100 * descarta.sum() / max(utiles.sum(), 1)
        print(f"{nombre:<38}{utiles.sum():>9,}{descarta.sum():>10,}{pct:>7.2f}%")

    ajuste = util & (particion != "prueba")
    descarta = ajuste & ~valida

    print("\nPor qué se descartan, sobre el ajuste:")
    print(f"  cota inferior exactamente 0 µM:  {(ajuste & (inf_um == 0)).sum():,}")
    print(f"  cota inferior no finita:         {(ajuste & ~np.isfinite(inf_um)).sum():,}")

    col = "procedencia" if "procedencia" in d.columns else "estrato"
    print(f"\nPor {col}, sobre el ajuste — el estrato es lo que decide si el defecto importa:")
    print(f"  {'estrato':<14}{'ajuste':>9}{'descarta':>10}")
    for estrato in sorted(d.loc[ajuste, col].dropna().unique()):
        sel = ajuste & (d[col] == estrato).to_numpy()
        des = descarta & (d[col] == estrato).to_numpy()
        print(f"  {str(estrato):<14}{sel.sum():>9,}{des.sum():>10,}")

    cotas = inferior[descarta]
    cotas = cotas[np.isfinite(cotas)]
    if len(cotas):
        exactas = inferior[ajuste & (inferior == superior)]
        print(f"\nLo que se pierde: la cota en pActividad tiene mediana {np.median(cotas):.2f} "
              f"(= {10 ** (6 - np.median(cotas)):.3f} µM),")
        print(f"contra una mediana de {np.median(exactas):.2f} en las exactas de ajuste. "
              "Son mediciones potentes.")


if __name__ == "__main__":
    main()
