#!/usr/bin/env python3
"""Cobertura de los cinco campos de ensayo que pidió la patrocinadora, antes de bajar nada.

Ella pidió traer por identificador de ensayo **tipo de ensayo, formato BAO, puntaje de
confianza, organismo y `action_type`** (#134), y el propio issue puso la condición correcta:
medir primero la cobertura, porque si un campo viene casi vacío lo que toca es escribir esa
cifra en la [2.11](../docs/decisiones.md#d2-11) y no construir sobre él.

Medir no necesita la API. **Tres de los cinco campos ya están en el archivo** que ella nos
dio, así que la cobertura se mide del archivo y del CSV ya bajado, sin red y de forma
reproducible. Lo que la API sí haría falta para medir son los dos que no están en ninguna
parte, y ahí la cobertura es 0% por construcción y no por el dato.

Dos cosas que este script existe para no volver a suponer:

- `assay_format` **es** el formato BAO: sus ocho valores son etiquetas BAO («cell membrane
  format», «tissue-based format»…). O sea que ese campo no hay que bajarlo. Pero uno de esos
  ocho valores es `assay format`, la **clase raíz** de BAO, en 2,921 filas: tener ese
  «formato» no dice cuál, así que no cuenta como útil.
- `assay_organism` está al revés de lo que cualquiera supondría: **0% en las filas de ChEMBL
  y 100% en las de NPASS**, que son justo las que no traen `assay_chembl_id` y por las que no
  se puede preguntar. Y una parte de esos valores es el literal `n.a.`, que no es un organismo.

    BIOACTIVE_AUTOR=ingrid python scripts/cobertura_campos_ensayo.py

Escribe `notebooks/datos/cobertura_campos_ensayo.csv` (una fila por campo y fuente) y registra
la corrida. No toca ningún dato ni ninguna cifra publicada: solo cuenta nulos.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402

from src.tracking import Corrida  # noqa: E402

ARCHIVO = (RAIZ / "data/external/profesora"
           / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
BAJADOS = RAIZ / "notebooks/datos/tipos_ensayo_chembl.csv"
SALIDA = RAIZ / "notebooks/datos/cobertura_campos_ensayo.csv"

# Los cinco que pidió, con el nombre que tienen en el archivo cuando lo tienen.
PEDIDOS = {
    "tipo de ensayo": "assay_type",
    "formato BAO": "assay_format",
    "organismo": "assay_organism",
    "puntaje de confianza": None,   # no está en el archivo: solo por API
    "action_type": None,            # no está, y no es un campo del endpoint `assay`
}
# Valores presentes que no informan: se cuentan aparte de los nulos. `assay format` es la
# clase raíz de BAO —el padre de `cell-based format` y los otros siete—, así que decir que un
# ensayo tiene ese «formato» es decir que tiene un formato, no cuál: es el mismo caso que
# `n.a.` y entra por el mismo criterio.
NO_INFORMA = {"n.a.", "n.a", "N.A.", "unknown", "Unknown", "assay format"}


def main() -> None:
    columnas = ["source", "assay_chembl_id", "assay_type", "assay_format", "assay_organism"]
    d = pd.read_csv(ARCHIVO, usecols=columnas, low_memory=False)
    bajados = set(pd.read_csv(BAJADOS)["assay_chembl_id"])

    filas = []
    for etiqueta, col in PEDIDOS.items():
        for fuente in [*sorted(d["source"].unique()), "todas"]:
            s = d if fuente == "todas" else d[d["source"] == fuente]
            if col is None:
                filas.append(dict(campo=etiqueta, columna="(no está en el archivo)",
                                  fuente=fuente, filas=len(s), con_valor=0, utiles=0,
                                  pct_con_valor=0.0, pct_utiles=0.0))
                continue
            con = s[col].notna()
            util = con & ~s[col].isin(NO_INFORMA)
            filas.append(dict(campo=etiqueta, columna=col, fuente=fuente, filas=len(s),
                              con_valor=int(con.sum()), utiles=int(util.sum()),
                              pct_con_valor=round(100 * con.mean(), 2),
                              pct_utiles=round(100 * util.mean(), 2)))
    # La ruta por la que se preguntaría: solo ChEMBL trae identificador de ensayo.
    for fuente in [*sorted(d["source"].unique()), "todas"]:
        s = d if fuente == "todas" else d[d["source"] == fuente]
        con = s["assay_chembl_id"].notna()
        filas.append(dict(campo="identificador de ensayo", columna="assay_chembl_id",
                          fuente=fuente, filas=len(s), con_valor=int(con.sum()),
                          utiles=int(con.sum()), pct_con_valor=round(100 * con.mean(), 2),
                          pct_utiles=round(100 * con.mean(), 2)))

    ch = d[d["source"] == "chembl"]
    todos = set(ch["assay_chembl_id"].dropna())
    sin_tipo = set(ch.loc[ch["assay_type"].isna(), "assay_chembl_id"].dropna())
    faltan = sin_tipo - bajados
    hueco = {
        "ensayos_chembl_distintos": len(todos),
        "con_tipo_en_el_archivo": len(todos - sin_tipo),
        "sin_tipo_en_el_archivo": len(sin_tipo),
        "ya_bajados": len(bajados),
        "sin_tipo_ya_bajados": len(sin_tipo & bajados),
        "faltan_por_bajar": len(faltan),
        "filas_sin_tipo_si_no_se_bajan": int(ch["assay_chembl_id"].isin(faltan).sum()),
    }
    valores_bao = sorted(d["assay_format"].dropna().unique())

    tabla = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)   # antes de metricas(): un fallo al cerrar no cuesta el cálculo
    print(tabla.to_string(index=False))
    print("\nhueco de descarga:", hueco)

    with Corrida("cobertura-campos-ensayo", decision="2.11",
                 params={"archivo": ARCHIVO.name, "bajados": BAJADOS.name,
                          "campos_pedidos": list(PEDIDOS), "no_informa": sorted(NO_INFORMA)},
                 semillas=[], datos=[ARCHIVO, BAJADOS]) as corrida:
        corrida.metricas({
            "filas": len(d),
            "filas_por_fuente": d["source"].value_counts().to_dict(),
            "pct_con_valor": {f"{r.campo}·{r.fuente}": r.pct_con_valor
                              for r in tabla.itertuples()},
            "pct_utiles": {f"{r.campo}·{r.fuente}": r.pct_utiles for r in tabla.itertuples()},
            "hueco_de_descarga": hueco,
            "valores_de_assay_format": valores_bao,
            "n_valores_de_assay_format": len(valores_bao),
        })
        print(f"\ncorrida {corrida.id}")


if __name__ == "__main__":
    main()
