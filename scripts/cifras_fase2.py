#!/usr/bin/env python3
"""Las cifras de la fase 2 que cita el registro, recalculadas desde el archivo.

Evidencia de las decisiones 2.1 a 2.8 de `docs/decisiones.md`. El notebook 01b
hace el EDA de la actividad, pero varias de las cifras que la bitácora usa para
plantear las preguntas a la patrocinadora vivían solo en prosa, sin celda que
las produjera: el caso claro era «12,809 de los 15,293 naturales», que es el
número con el que se justifica el etiquetado por tres vías de la 2.3.

Este script recalcula esas cifras a nivel de registro y las imprime con la
definición que usa cada una, para que la bitácora pueda citarlas con una orden
detrás. No calcula nada que necesite RDKit —los conteos por esqueleto de
conectividad y el cruce con el conjunto de permeabilidad siguen en el notebook
01b—, así que corre en segundos.

    python scripts/cifras_fase2.py

Dos criterios que conviene tener a la vista, porque de ellos dependen los
conteos:

- **Censurado** es `activity_relation_used` en `>`, `>=` o `>>`. El `>>` son
  solo 3 filas, pero omitirlo da 54,495 en vez de 54,498 y esa es justo la
  cifra que la bitácora cita.
- **Negativo seguro** es la regla de la patrocinadora (diccionario, sección 7):
  un censurado sirve como negativo únicamente si su límite es mayor o igual que
  el umbral de «activo». Las filas en µg/mL no se pueden convertir a molar sin
  el peso molecular, así que cuentan como ambiguas.
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = (RAIZ / "data/external/profesora"
           / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")

CENSURA = (">", ">=", ">>")
NATURALES = ("npass", "cmaup")

# A molar en µM. Las másicas quedan fuera: sin peso molecular no hay conversión.
A_MICROMOLAR = {"nM": 1e-3, "uM": 1.0, "um": 1.0, "mM": 1e3, "M": 1e6,
                "10^3nM": 1.0}

UMBRALES_UM = (1, 10, 100)


def en_micromolar(df: pd.DataFrame) -> pd.Series:
    """Límite de concentración en µM, o NaN si la unidad no es convertible."""
    valor = pd.to_numeric(df["activity_value_used"], errors="coerce")
    factor = df["activity_units_used"].fillna("").map(A_MICROMOLAR)
    return valor * factor


def main() -> None:
    if not ARCHIVO.exists():
        raise SystemExit(f"No está el archivo de actividad: {ARCHIVO}")

    df = pd.read_csv(ARCHIVO, low_memory=False)
    relacion = df["activity_relation_used"]
    censurado = relacion.isin(CENSURA)
    natural = df["source"].isin(NATURALES)
    micromolar = en_micromolar(df)

    print(f"Archivo: {ARCHIVO.name}")
    print(f"{len(df):,} registros\n")

    print("Por fuente")
    for fuente, n in df["source"].value_counts().items():
        print(f"  {fuente:<8} {n:>8,}")
    print(f"  {'naturales':<8} {natural.sum():>8,}  (NPASS + CMAUP)")

    print("\nLo que descartaría etiquetar solo por pChEMBL")
    print(f"  registros de NPASS y CMAUP     {natural.sum():>8,}"
          f"  (con pChEMBL: {df.loc[natural, 'chembl_pchembl_value'].notna().sum()})")
    print(f"  mediciones censuradas          {censurado.sum():>8,}"
          f"  (relación {', '.join(CENSURA)})")
    print(f"  inactivos declarados por texto "
          f"{df['chembl_standard_text_value'].notna().sum():>8,}")

    print("\nLos naturales que recupera la concentración exacta")
    exacta = natural & relacion.eq("=")
    print(f"  con relación «=»               {exacta.sum():>8,}"
          f" de {natural.sum():,}")
    print("  el resto, por relación:")
    for rel, n in relacion[natural & ~relacion.eq("=")].value_counts().items():
        print(f"    {rel:<4} {n:>6,}")

    print("\nCensurados que sirven como negativo, por umbral de «activo»")
    print("  (regla del diccionario: el límite debe ser >= el umbral)")
    total_censurado = int(censurado.sum())
    print(f"  {'umbral':<10} {'negativos seguros':>18} {'ambiguos':>10}")
    for umbral in UMBRALES_UM:
        seguros = int((micromolar[censurado] >= umbral).sum())
        pct = 100 * seguros / total_censurado
        print(f"  {str(umbral) + ' µM':<10} {seguros:>11,} ({pct:4.0f}%)"
              f" {total_censurado - seguros:>10,}")
    sin_convertir = int(micromolar[censurado].isna().sum())
    print(f"  de los {total_censurado:,} censurados, {sin_convertir} están en"
          " µg/mL y no se pueden convertir")

    print("\nConcentración de los censurados en un solo límite y una sola fuente")
    en_diez = censurado & micromolar.eq(10)
    print(f"  con límite de 10 µM            {en_diez.sum():>8,}")
    referencia = df.loc[en_diez, "reference_id"].value_counts()
    if not referencia.empty:
        print(f"  la referencia más repetida     {referencia.iloc[0]:>8,}"
              f"  ({referencia.index[0]})")

    print("\nRegistros por categoría de diana")
    categorias = df["diana_categoria"].value_counts()
    sin_diana = int(categorias.get("Sin diana de la lista", 0))
    print(f"  con diana de la lista          {len(df) - sin_diana:>8,}")
    print(f"  sin diana de la lista          {sin_diana:>8,}  (fenotípicos)")
    for categoria, n in categorias.items():
        if categoria != "Sin diana de la lista":
            print(f"    {categoria:<28} {n:>7,}")


if __name__ == "__main__":
    main()
