#!/usr/bin/env python3
"""Las cifras de la etiqueta de la fase 2, recalculadas desde el archivo.

Evidencia de la propuesta de variable objetivo y de la decisión 2.3 de
`docs/decisiones.md`. Donde `scripts/cifras_fase2.py` cuenta **registros** para
plantear las preguntas a la patrocinadora, este cuenta **pares**, que es la
unidad sobre la que el modelo entrena, y por eso varias proporciones no
coinciden entre los dos: el caso claro es el peso de `CHEMBL1909046` en la
clase negativa, que es el 61% por registro y el 14% por par porque esas 29,730
filas son 772 compuestos.

    python scripts/cifras_etiqueta_fase2.py            # T = 10 µM
    python scripts/cifras_etiqueta_fase2.py --umbral 1

Necesita RDKit, porque la llave del par se calcula desde `smiles_raw`.

Cuatro criterios de los que dependen los conteos:

- **Llave del par:** esqueleto de conectividad (los primeros 14 caracteres del
  InChIKey) × `target_gene`. No `source_compound_id`, que usa prefijos
  distintos por fuente (`CHEMBL…` contra `NPC…`) y no comparte ningún valor
  entre ellas, así que un compuesto medido en dos fuentes entraría como dos
  pares y sus contradicciones quedarían invisibles. Es la misma llave que
  `grupos_cv` usa en `src/data_prep/splits.py`.
- **Etiqueta de la medición:** exacta (`=`, `~`) contra el umbral; `<` y `<=`
  activan solo si el valor llega al umbral; `>`, `>=` y `>>` sirven de negativo
  solo si el límite alcanza el umbral, que es la regla de la sección 7 del
  diccionario de la patrocinadora. Lo demás queda sin decisión.
- **Par en conflicto:** tiene a la vez una medición activa y una inactiva. Se
  reportan y se excluyen; la alternativa (dejarlos activos) también se imprime.
- **La fuente no es un atributo del par.** Un par puede tener mediciones de
  varias fuentes, así que «por fuente» se imprime en estratos disjuntos por
  procedencia de la evidencia. Contar cada par en todas sus fuentes da los
  porcentajes de la propuesta, y también se imprime para poder citarlos.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO = (RAIZ / "data/external/profesora"
           / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")

# Las cinco categorías que la patrocinadora aprobó el 15 de octubre de 2026.
CINCO = ("Alzheimer", "Parkinson", "Neuroinflamación", "Depresión",
         "Estrés oxidativo")

# A µM. Las másicas quedan fuera: sin peso molecular no hay conversión.
A_MICROMOLAR = {"nM": 1e-3, "uM": 1.0, "um": 1.0, "mM": 1e3, "M": 1e6,
                "10^3nM": 1.0, "10^2 uM": 1e2, "10^6uM": 1e6, "umol/L": 1.0}

EXACTA = ("=", "~")
MENOR = ("<", "<=")
CENSURA = (">", ">=", ">>")

# El pChEMBL observado en este archivo va de 2.35 a 12.00; ChEMBL no lo calcula
# para los valores implausibles, así que ese rango sirve de recorte declarado.
RANGO_POTENCIA = (2.0, 12.0)

REFERENCIA_UNICA = "CHEMBL1909046"


def esqueleto(smiles: pd.Series) -> pd.Series:
    """Esqueleto de conectividad: los 14 primeros caracteres del InChIKey."""
    from rdkit import Chem, RDLogger

    RDLogger.DisableLog("rdApp.*")
    llaves: dict[str, str] = {}
    for texto in smiles.dropna().unique():
        mol = Chem.MolFromSmiles(texto)
        if mol is None:
            continue
        try:
            clave = Chem.MolToInchiKey(mol)
        except Exception:
            continue
        if clave:
            llaves[texto] = clave[:14]
    return smiles.map(llaves)


def en_micromolar(df: pd.DataFrame) -> pd.Series:
    valor = pd.to_numeric(df["activity_value_used"], errors="coerce")
    factor = df["activity_units_used"].fillna("").map(A_MICROMOLAR)
    return valor * factor


def etiqueta_medicion(df: pd.DataFrame, micromolar: pd.Series,
                      umbral: float) -> pd.Series:
    """Activa, inactiva o sin decisión, para cada medición."""
    relacion = df["activity_relation_used"].fillna("")
    hay = micromolar.notna()
    etiqueta = pd.Series(pd.NA, index=df.index, dtype="object")

    exacta = relacion.isin(EXACTA) & hay
    etiqueta[exacta & micromolar.le(umbral)] = True
    etiqueta[exacta & micromolar.gt(umbral)] = False
    etiqueta[relacion.isin(MENOR) & hay & micromolar.le(umbral)] = True
    etiqueta[relacion.isin(CENSURA) & hay & micromolar.ge(umbral)] = False
    return etiqueta


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--umbral", type=float, default=10.0,
                     help="umbral de «activo» en µM (10 principal, 1 sensibilidad)")
    args = cli.parse_args()
    umbral = args.umbral

    if not ARCHIVO.exists():
        raise SystemExit(f"No está el archivo de actividad: {ARCHIVO}")

    df = pd.read_csv(ARCHIVO, low_memory=False)
    df["key14"] = esqueleto(df["smiles_raw"])
    micromolar = en_micromolar(df)
    df["activa"] = etiqueta_medicion(df, micromolar, umbral)

    print(f"Archivo: {ARCHIVO.name}")
    print(f"{len(df):,} registros · umbral de «activo» {umbral:g} µM\n")

    # --- Qué filas forman par -------------------------------------------------
    cinco = df["diana_categoria"].isin(CINCO)
    con_llave = df["key14"].notna() & df["target_gene"].notna()
    print("Filas que pueden formar par")
    print(f"  en las cinco categorías        {cinco.sum():>8,}")
    print(f"  ...con gen y estructura        {(cinco & con_llave).sum():>8,}")
    print(f"  sin gen                        "
          f"{(cinco & df['target_gene'].isna()).sum():>8,}")
    print(f"  sin estructura calculable      "
          f"{(cinco & df['key14'].isna()).sum():>8,}")

    por_texto = df["evidence_kind"].eq("inactivo_por_texto")
    # Una fila en µg/mL no puede etiquetarse sin el peso molecular, así que un
    # par cuyas filas estén todas en esas unidades no es un par del conjunto.
    base = cinco & con_llave & micromolar.notna()
    print(f"  ...con unidad convertible      "
          f"{base.sum():>8,}  (las {(cinco & con_llave & micromolar.isna()).sum()}"
          " restantes están en µg/mL)")

    for con_los_textos in (False, True):
        filas = base if con_los_textos else base & ~por_texto
        rotulo = ("con los inactivos por texto" if con_los_textos
                  else "sin los inactivos por texto (definición principal)")
        sub = df[filas & df["activa"].notna()]
        grupos = sub.groupby(["key14", "target_gene"])["activa"]
        distintas, cuantas = grupos.nunique(), grupos.size()
        conflicto = distintas.eq(2)
        limpios = distintas[~conflicto].index
        par = (sub.set_index(["key14", "target_gene"])
                  .loc[list(limpios)].groupby(level=[0, 1])["activa"].max())

        print(f"\nPares · {rotulo}")
        print(f"  totales en las cinco categorías "
              f"{len(df[filas].groupby(['key14', 'target_gene'])):>7,}")
        print(f"  con alguna medición etiquetable {len(distintas):>7,}")
        print(f"  con más de una medición         {cuantas.gt(1).sum():>7,}")
        print(f"  en conflicto                    {conflicto.sum():>7,}"
              f"  ({conflicto.sum() / max(cuantas.gt(1).sum(), 1):.1%} de esos)")
        print(f"  con etiqueta, conflictos fuera  {len(par):>7,}"
              f"  · activos {par.mean():.1%}")
        dejando = distintas.index
        todos = (sub.set_index(["key14", "target_gene"])
                    .groupby(level=[0, 1])["activa"].max())
        print(f"  si el conflicto quedara activo  {len(dejando):>7,}"
              f"  · activos {todos.mean():.1%}")

    # --- La fuente no es un atributo del par ---------------------------------
    sub = df[base & ~por_texto & df["activa"].notna()]
    grupos = sub.groupby(["key14", "target_gene"])["activa"]
    limpios = grupos.nunique().loc[lambda s: s.ne(2)].index
    sub = sub.set_index(["key14", "target_gene"]).loc[list(limpios)]
    par = sub.groupby(level=[0, 1]).agg(activa=("activa", "max"),
                                        fuentes=("source", "nunique"))

    print("\nLa fuente no es un atributo del par")
    print(f"  pares de una sola fuente        {par.fuentes.eq(1).sum():>7,}")
    print(f"  pares con más de una fuente     {par.fuentes.gt(1).sum():>7,}")
    print("\n  Estratos disjuntos por procedencia de la evidencia")
    unica = sub[sub.index.isin(par[par.fuentes.eq(1)].index)]
    de_quien = unica.groupby(level=[0, 1])["source"].first()
    for fuente, idx in de_quien.groupby(de_quien):
        print(f"    solo {fuente:<8} {len(idx):>7,}"
              f"  · activos {par.loc[idx.index, 'activa'].mean():.1%}")
    mixtos = par[par.fuentes.gt(1)]
    if len(mixtos):
        print(f"    {'mixtos':<13} {len(mixtos):>7,}"
              f"  · activos {mixtos.activa.mean():.1%}")

    print("\n  Contando cada par en todas sus fuentes (los porcentajes citados)")
    for fuente in ("chembl", "npass", "cmaup"):
        idx = sub[sub["source"].eq(fuente)].index.unique()
        if not len(idx):
            continue
        compartidos = par.loc[idx, "fuentes"].gt(1)
        print(f"    {fuente:<8} {len(idx):>7,}  · activos "
              f"{par.loc[idx, 'activa'].mean():.1%}"
              f"  · comparten par con otra fuente {compartidos.mean():.1%}")

    # --- El corte frente a la potencia de cada fuente ------------------------
    relacion = df["activity_relation_used"].fillna("")
    exactas = df[base & relacion.isin(EXACTA) & micromolar.notna()
                 & micromolar.gt(0)].copy()
    exactas["pActividad"] = 6 - np.log10(micromolar[exactas.index])

    print("\nDónde cae el corte en la distribución de cada fuente")
    print("  (mediciones exactas; pActividad = 6 − log10 µM)")
    for fuente, g in exactas.groupby("source"):
        um = micromolar[g.index]
        print(f"    {fuente:<8} mediana {um.median():>8.3f} µM"
              f"  · pActividad mediana {g.pActividad.median():.2f}"
              f"  · ≤ {umbral:g} µM {um.le(umbral).mean():.1%}")

    # --- Peso de la referencia única en la clase negativa --------------------
    negativos = par[~par.activa.astype(bool)].index
    evidencia = sub.loc[list(negativos)].groupby(level=[0, 1])["reference_id"]
    solo = evidencia.apply(lambda s: s.eq(REFERENCIA_UNICA).all())
    print(f"\nPeso de {REFERENCIA_UNICA} en la clase negativa, por par")
    print(f"  pares negativos                 {len(negativos):>7,}")
    print(f"  cuya evidencia es solo de ahí   {solo.sum():>7,}"
          f"  ({solo.mean():.1%})")
    print("  por registro la misma referencia da el 61%: son 772 compuestos")

    # --- Ejercicio de potencia ----------------------------------------------
    print("\nEjercicio de potencia")
    print(f"  mediciones exactas              {len(exactas):>7,}")
    fuera = ~exactas.pActividad.between(*RANGO_POTENCIA)
    print(f"  pActividad observada            "
          f"{exactas.pActividad.min():>7.2f} a {exactas.pActividad.max():.2f}")
    print(f"  fuera de [{RANGO_POTENCIA[0]:g}, {RANGO_POTENCIA[1]:g}]"
          f"                 {fuera.sum():>7,}  ({fuera.mean():.2%})")
    print("  esas filas traen la unidad bien y el valor implausible,"
          " y ChEMBL no les asignó pChEMBL")

    pchembl = pd.to_numeric(exactas["chembl_pchembl_value"], errors="coerce")
    tiene = pchembl.notna()
    if tiene.any():
        dif = (exactas.pActividad[tiene] - pchembl[tiene]).abs()
        print(f"  contra el pChEMBL ({tiene.sum():,} filas):"
              f" mediana {dif.median():.4f} · máximo {dif.max():.3f}")

    for recorte in (None, RANGO_POTENCIA):
        g = exactas if recorte is None else exactas[~fuera]
        mediana = g.groupby(["key14", "target_gene"])["pActividad"].median()
        rotulo = "sin recorte" if recorte is None else f"recortada a {list(recorte)}"
        print(f"  {rotulo:<24} pares {len(mediana):>7,}"
              f"  · mediana {mediana.median():.2f}"
              f"  · de {mediana.min():.2f} a {mediana.max():.2f}")


if __name__ == "__main__":
    main()
