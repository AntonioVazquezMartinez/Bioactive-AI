#!/usr/bin/env python3
"""La censura del conjunto de ajuste de la fase 2, desglosada por procedencia.

Evidencia de la [2.13](../docs/decisiones.md#d2-13) y del #196. El argumento con
el que se elige el AFT como modelo final de la fase 2 es que ajusta con las
mediciones censuradas que `SoloExactas` descarta, y que eso pesa justo donde el
proyecto decide: en los productos naturales. Ese argumento descansa en cinco
conteos —**52,529** filas de ChEMBL con **16.6%** censuradas, **2,114** de NPASS
con **53.5%**, y las **982** exactas que el filtro deja en NPASS— que vivían
escritos a mano en el markdown del 05b: ninguna celda los imprimía, ningún
`metricas.json` los guardaba y ningún script los producía. Son correctos, y este
script es lo que les pone una corrida detrás, que es lo que el `CLAUDE.md` pide
de cualquier cifra publicada.

    python scripts/cifras_censura_fase2.py

Tres criterios de los que dependen los conteos, porque ninguno es el único
posible y con otro salen otros números:

- **Censurada** es lo que `SoloExactas` tira, no lo que la fuente marca con `>`.
  El envoltorio de `src/models/baseline_regresion.py` entrena con
  `np.isfinite(inferior) & (inferior == superior)`, así que censurada es toda
  fila cuyo intervalo de `pActividad` no se cierra en un punto. Contar por
  `activity_relation_used` sobre el archivo crudo responde otra pregunta —esa
  es la de `scripts/cifras_fase2.py`— y da otra cifra, porque un par reúne
  varias mediciones.
- **Ajuste** es `particion != "prueba"`, entrenamiento más validación, que es
  el conjunto que los modelos del 05b ven. Un conteo sin partición no se puede
  comprobar: el mismo desglose sobre el archivo completo da 66,324 filas de
  ChEMBL en vez de 52,529.
- **Se cuenta tras el cruce con los descriptores**, con la misma lectura de las
  celdas 5 y 7 del cuaderno. El cruce sí mueve el desglose por estrato: sobre
  `fase2_pares.parquet` a secas el ajuste tiene 56,411 filas y 52,697 de
  ChEMBL, y son las 56,241 y 52,529 de después del cruce las que el cuaderno
  asevera. NPASS no se mueve, se queda en 2,114 por los dos caminos.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.tracking import Corrida  # noqa: E402

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"

# El orden en que el cuaderno presenta los estratos, de mayor a menor.
ESTRATOS = ("solo_chembl", "solo_npass", "mixto", "solo_cmaup")


def es_exacta(inferior: np.ndarray, superior: np.ndarray) -> np.ndarray:
    """Las filas con las que `SoloExactas` entrena: intervalo cerrado en un punto.

    Es la definición del envoltorio, repetida aquí a propósito y no importada,
    porque `SoloExactas.fit` la aplica dentro de un `fit` que necesitaría la
    matriz entera. Si una cambia, `tests/test_cifras_censura_fase2.py` falla.
    """
    inferior = np.asarray(inferior, dtype=float)
    superior = np.asarray(superior, dtype=float)
    return np.isfinite(inferior) & (inferior == superior)


def censura_por_estrato(estrato: np.ndarray, inferior: np.ndarray,
                        superior: np.ndarray) -> pd.DataFrame:
    """Filas, censuradas y exactas por estrato de procedencia.

    `exactas` es con cuántas filas entrena un ensamble envuelto en
    `SoloExactas` y `filas` con cuántas entrena el AFT: la diferencia entre las
    dos columnas es lo que el modelo final gana por tratar la censura.
    """
    exacta = es_exacta(inferior, superior)
    estrato = np.asarray(estrato)
    filas = []
    orden = [e for e in ESTRATOS if (estrato == e).any()]
    orden += sorted(set(map(str, estrato)) - set(ESTRATOS))
    for nombre in orden:
        sel = estrato == nombre
        n = int(sel.sum())
        exactas = int(exacta[sel].sum())
        filas.append({"estrato": nombre, "filas": n, "censuradas": n - exactas,
                      "pct_censuradas": round(100 * (n - exactas) / n, 1),
                      "exactas": exactas})
    return pd.DataFrame(filas)


def cargar() -> dict:
    """La misma lectura que las celdas 5 y 7 del 05b, sin huellas.

    Idéntica a `scripts/cifras_graficos_05b.py:cargar`, recortada a lo que estos
    conteos necesitan: no arma la matriz de entrada ni las variables de diana,
    porque aquí no se ajusta ningún modelo.
    """
    for ruta in (PARES, DESCRIPTORES):
        if not ruta.exists():
            raise SystemExit(
                f"falta {ruta.relative_to(RAIZ)}; se genera con "
                "scripts/construir_pares_fase2.py")
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)

    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    # El mismo criterio de utilidad del cuaderno: un intervalo que no dice nada
    # (−inf, +inf) no es una medición, y las cotas cruzadas tampoco.
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)
    d = d[util].reset_index(drop=True)
    return {"d": d, "inferior": inferior[util], "superior": superior[util]}


def main() -> None:
    datos = cargar()
    d = datos["d"]
    ajuste = d["particion"].ne("prueba").to_numpy()

    tabla = censura_por_estrato(d.loc[ajuste, "estrato"].to_numpy(),
                                datos["inferior"][ajuste],
                                datos["superior"][ajuste])

    with Corrida("cifras-censura-ajuste", decision="2.13",
                 params={"particion": "ajuste (entrenamiento + validacion)",
                         "censurada": "no isfinite(inferior) o inferior != superior",
                         "tras_cruce_con_descriptores": True},
                 semillas=[], datos=[PARES, DESCRIPTORES]) as c:
        print(f"Archivos: {PARES.name} × {DESCRIPTORES.name}")
        print(f"{len(d):,} pares útiles; {int(ajuste.sum()):,} de ajuste "
              f"(entrenamiento + validación), {int((~ajuste).sum()):,} de prueba\n")

        print(f"{'estrato':<14}{'filas':>8}{'censuradas':>12}{'%':>8}{'exactas':>9}")
        for fila in tabla.itertuples():
            print(f"{fila.estrato:<14}{fila.filas:>8,}{fila.censuradas:>12,}"
                  f"{fila.pct_censuradas:>7.1f}%{fila.exactas:>9,}")

        npass = tabla.set_index("estrato").loc["solo_npass"]
        con_censura, exactas = int(npass.filas), int(npass.exactas)
        print(f"\nEn NPASS el AFT ajusta con {con_censura:,} filas y los ensambles "
              f"envueltos en SoloExactas con {exactas:,}:")
        print(f"{con_censura / exactas:.2f} veces más datos justo donde más escasean.")

        c.metricas({"ajuste_total": int(ajuste.sum()),
                    "por_estrato": {
                        f.estrato: {"filas": f.filas, "censuradas": f.censuradas,
                                    "pct_censuradas": f.pct_censuradas,
                                    "exactas": f.exactas}
                        for f in tabla.itertuples()}})
        print(f"\nCorrida: experimentos/{c.id}/")


if __name__ == "__main__":
    main()
