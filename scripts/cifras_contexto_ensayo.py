#!/usr/bin/env python3
"""Cómo se distribuyen los registros por tejido, línea celular y tipo de ensayo.

Es la revisión que la patrocinadora pidió en su correo del 16 de octubre antes de
decidir el etiquetado (decisión 2.3): «revisar cómo se distribuyen los registros por
tejido y tipo de experimento». La tabla de cobertura por ruta de
`docs/datos-contenido.md` contaba **filas** y no decía ni cuántos de los **pares** que
entrena el modelo traen el dato, ni si el contexto mueve la potencia.

Calcula cuatro cosas:

1. cobertura de las columnas de contexto por fuente y por ruta de selección (filas);
2. potencia (`pActividad`) por formato, tipo de ensayo, tejido y línea celular;
3. cuántas dianas tienen dos formatos comparables, que decide si el efecto del contexto se
   puede separar del de la diana;
4. cobertura **por par** esqueleto × gen, que es la unidad del modelo, por estrato de
   procedencia, por conflicto y por diana, y qué tan distinto es un par con contexto de
   uno sin él.

    python scripts/cifras_contexto_ensayo.py

Salida: `notebooks/datos/contexto_ensayo.csv` (formato largo, versionado) y una corrida en
`experimentos/`. Necesita RDKit, porque la llave del par se calcula desde `smiles_raw`;
tarda unos minutos.

Criterios de los que dependen los conteos:

- **Las filas son las del modelo.** La sección 4 parte de `filas_de_pares`, la misma
  función que alimenta a `tabla_de_pares`: cinco categorías, sin inactivos por texto, con
  unidad convertible y estructura parseable. Los 70,384 pares de la tabla completa se
  comprueban contra ella.
- **Un par «tiene» un dato si al menos una de sus mediciones lo trae.**
- **`n.a.` es un valor, no un nulo.** NPASS lo trae en 7,595 de 11,992 filas de
  `assay_cell_type_raw`; aquí no cuenta como línea celular.
- **Las medianas por contexto no son un efecto del contexto**: cada formato mide dianas
  distintas. Solo la sección 3 dice cuánto se puede aislar.
- **`pActividad`** es la de la 2.10 (6 − log10 µM, recortada a [2, 12]), con las
  mediciones exactas (`=`, `~`) únicamente.
"""

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "src"))

from tracking import Corrida  # noqa: E402

from src.data_prep.pares_fase2 import (EXACTA, RANGO_POTENCIA,  # noqa: E402
                                       filas_de_pares, tabla_de_pares)

ARCHIVO = (RAIZ / "data/external/profesora"
           / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
SALIDA = RAIZ / "notebooks/datos/contexto_ensayo.csv"

CONTEXTO = ["assay_tissue_raw", "assay_cell_type_raw", "assay_organism",
            "assay_type", "assay_format"]
MIN_FILAS = 10  # por formato, dentro de una diana, para poder compararlo
COLUMNAS_PAR = {"tejido": "assay_tissue_raw", "celula": "assay_cell_type_raw",
                "formato": "assay_format"}


def cobertura_por_par(filas: pd.DataFrame) -> pd.DataFrame:
    """Por par esqueleto × gen, si alguna de sus mediciones trae cada dato de contexto.

    La línea celular `n.a.` no cuenta: es un valor literal que significa «no aplica».
    """
    marcas = pd.DataFrame({
        "tejido": filas["assay_tissue_raw"].notna(),
        "celula": filas["assay_cell_type_raw"].notna()
                  & filas["assay_cell_type_raw"].ne("n.a."),
        "formato": filas["assay_format"].notna(),
    })
    marcas[["esqueleto", "target_gene"]] = filas[["esqueleto", "target_gene"]]
    por_par = marcas.groupby(["esqueleto", "target_gene"], sort=False).any().reset_index()
    por_par["alguno"] = por_par[["tejido", "celula", "formato"]].any(axis=1)
    return por_par


def dianas_con_dos_formatos(exactas: pd.DataFrame, minimo: int = MIN_FILAS) -> pd.DataFrame:
    """Dianas con al menos dos formatos de ensayo con `minimo` exactas cada uno."""
    filas = []
    anotadas = exactas[exactas["assay_format"].notna()]
    for gen, s in anotadas.groupby("target_gene"):
        k = s.groupby("assay_format")["pActividad"].agg(["size", "median"])
        k = k[k["size"] >= minimo]
        if len(k) >= 2:
            filas.append((gen, ", ".join(k.index),
                          round(k["median"].max() - k["median"].min(), 2),
                          int(k["size"].sum())))
    return pd.DataFrame(filas, columns=["diana", "formatos", "rango_pActividad", "n"])


def _porcentaje(serie: pd.Series) -> str:
    return f"{int(serie.sum()):,} ({100 * serie.mean():.1f}%)"


def main() -> None:
    d = pd.read_csv(ARCHIVO, low_memory=False)
    largo: list[tuple] = []  # tabla, grupo, métrica, valor
    metricas: dict = {}

    with Corrida("contexto-ensayo", decision="2.3",
                 params={"min_filas_por_formato": MIN_FILAS,
                         "rango_potencia": list(RANGO_POTENCIA)},
                 semillas=[], datos=[ARCHIVO]) as corrida:
        print(f"Archivo: {len(d):,} filas, {d['target_gene'].nunique()} dianas\n")

        print("1. Filas con la columna informada, por fuente y por ruta")
        for agrupar in ("source", "selection_route"):
            t = d.groupby(agrupar)[CONTEXTO].agg(lambda s: s.notna().sum())
            t.insert(0, "filas", d.groupby(agrupar).size())
            print(t.to_string(), "\n")
            for grupo, fila in t.iterrows():
                for col, v in fila.items():
                    largo.append((f"filas_por_{agrupar}", grupo, col, int(v)))
        na = int((d["assay_cell_type_raw"] == "n.a.").sum())
        print(f"   «n.a.» literal en assay_cell_type_raw: {na:,}\n")
        metricas["filas_n_a_celula"] = na

        # --- mediciones exactas con pActividad, para las secciones 2 y 3 ------------
        filas = filas_de_pares(d)
        exactas = filas[filas["activity_relation_used"].isin(EXACTA)
                        & filas["exacta"].notna()].copy()
        exactas["pActividad"] = exactas["exacta"]

        print(f"2. pActividad por contexto ({len(exactas):,} exactas que entran al modelo)")
        metricas["exactas_del_modelo"] = len(exactas)
        for col, excluir in (("assay_format", None), ("assay_type", None),
                             ("assay_tissue_raw", None), ("assay_cell_type_raw", "n.a.")):
            s = exactas[exactas[col].notna()]
            if excluir:
                s = s[s[col].ne(excluir)]
            t = (s.groupby(col)["pActividad"].agg(["size", "median"])
                 .sort_values("size", ascending=False).round(2))
            print(f"   {col}\n      " + t.head(8).to_string().replace("\n", "\n      "))
            for valor, fila in t.iterrows():
                largo.append((f"pActividad_por_{col}", valor, "n", int(fila["size"])))
                largo.append((f"pActividad_por_{col}", valor, "mediana", fila["median"]))
        print()

        print(f"3. Dianas con dos formatos comparables (≥ {MIN_FILAS} exactas en cada uno)")
        dos = dianas_con_dos_formatos(exactas)
        con_formato = exactas[exactas["assay_format"].notna()]["target_gene"].nunique()
        print(f"   dianas con exactas: {exactas['target_gene'].nunique()} · con formato "
              f"anotado: {con_formato} · con dos formatos comparables: {len(dos)}")
        if len(dos):
            print("      " + dos.to_string(index=False).replace("\n", "\n      "))
        metricas.update(dianas_con_exactas=int(exactas["target_gene"].nunique()),
                        dianas_con_formato=int(con_formato),
                        dianas_con_dos_formatos=len(dos))
        for _, f in dos.iterrows():
            largo.append(("dianas_con_dos_formatos", f["diana"], "rango_pActividad",
                          f["rango_pActividad"]))
        print()

        # --- por par ---------------------------------------------------------------
        print("4. Cobertura por par esqueleto × gen")
        pares = tabla_de_pares(d)
        cob = cobertura_por_par(filas)
        assert len(cob) == len(pares), (len(cob), len(pares))
        m = pares.merge(cob, on=["esqueleto", "target_gene"], how="left", validate="1:1")
        marcas = ["tejido", "celula", "formato", "alguno"]
        print(f"   pares: {len(m):,}")
        for c in marcas:
            print(f"   con {c:<8} {_porcentaje(m[c])}")
            largo.append(("cobertura_pares", "todos", c, int(m[c].sum())))
            metricas[f"pares_con_{c}"] = int(m[c].sum())
        metricas["pares"] = len(m)

        for agrupar, nombre in (("estrato", "por estrato"), ("conflicto", "por conflicto")):
            t = m.groupby(agrupar)[marcas].mean().mul(100).round(1)
            t.insert(0, "pares", m.groupby(agrupar).size())
            print(f"\n   {nombre}\n      " + t.to_string().replace("\n", "\n      "))
            for grupo, fila in t.iterrows():
                largo.append((f"cobertura_pares_{agrupar}", str(grupo), "pares", int(fila["pares"])))
                for c in marcas:
                    largo.append((f"cobertura_pares_{agrupar}", str(grupo), f"{c}_pct", fila[c]))

        por_diana = m.groupby("target_gene").agg(pares=("tejido", "size"),
                                                 tejido=("tejido", "mean"))
        sin = int((por_diana["tejido"] == 0).sum())
        print(f"\n   dianas del modelo: {len(por_diana)} · sin ningún par con tejido: {sin} · "
              f"con todos: {int((por_diana['tejido'] == 1).sum())}")
        metricas.update(dianas_del_modelo=len(por_diana), dianas_sin_tejido=sin)

        t = m.groupby("tejido").agg(pares=("tejido", "size"),
                                    activos_10um=("activo_10um", "mean"),
                                    pActividad_mediana=("pActividad", "median")).round(3)
        print("\n   par con tejido frente a par sin tejido\n      "
              + t.to_string().replace("\n", "\n      "))
        for tiene, fila in t.iterrows():
            for c, v in fila.items():
                largo.append(("par_con_tejido", "con" if tiene else "sin", c, v))
            clave = "con" if tiene else "sin"
            metricas[f"activos_10um_{clave}_tejido"] = round(float(fila["activos_10um"]), 3)

        rutas = d.groupby("target_gene")["selection_route"].agg(
            lambda s: "+".join(sorted(set(s))))
        print("\n   dianas según las rutas en que aparecen:",
              rutas.value_counts().to_dict())

        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(largo, columns=["tabla", "grupo", "metrica", "valor"]).to_csv(
            SALIDA, index=False)
        corrida.metricas(metricas)
        print(f"\nEscrito {SALIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
