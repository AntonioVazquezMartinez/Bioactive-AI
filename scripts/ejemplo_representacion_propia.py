#!/usr/bin/env python3
"""Ejemplo de punta a punta de la herramienta de representaciones propias (#295).

La «tabla de la patrocinadora» es aquí una tabla de tres propiedades que se calculan en este mismo
script con RDKit (TPSA, donadores de hidrógeno y peso), para que el ejemplo corra sin datos externos. Se
mide contra la representación de descriptores del proyecto y contra un control de ruido, en la fase 1,
con la regresión logística. Para usar una tabla propia basta cambiar `mi_tabla` por un `read_csv` con una
columna `smiles` y las columnas numéricas que se quieran medir.

    ./env312/bin/python scripts/ejemplo_representacion_propia.py

No toca la prueba reservada (`cargar` la deja fuera).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

from src.models import cargar
from src.models.baseline import canalizaciones
from src.models.representaciones import columnas_al_azar, comparar, con_tabla


def mi_tabla(smiles: pd.Series) -> pd.DataFrame:
    filas = []
    for s in smiles:
        m = Chem.MolFromSmiles(s)
        filas.append({"smiles": s, "tpsa": rdMolDescriptors.CalcTPSA(m),
                      "donadores": rdMolDescriptors.CalcNumHBD(m), "peso": Descriptors.MolWt(m)})
    return pd.DataFrame(filas)


def main() -> None:
    base = cargar("permeabilidad", representacion="descriptores")
    tabla = mi_tabla(base.meta["SMILES"])
    mia = con_tabla(base, tabla, nombre="tpsa_hbd_peso")
    ruido = columnas_al_azar(base, mia.X.shape[1], nombre="ruido_3_columnas")
    logistica = {"logistica": canalizaciones()["logistica"]}
    resumen, _ = comparar({"descriptores": base, "tpsa_hbd_peso": mia, "ruido_3_columnas": ruido},
                          logistica, referencia="descriptores")
    solo = resumen[(resumen["estrato"] == "todos") & resumen["metrica"].isin(["mcc", "auroc"])]
    print(f"Referencia: descriptores ({base.X.shape[1]} columnas), {base.X.shape[0]:,} compuestos, "
          f"{len(set(base.grupos)):,} grupos.\n")
    print(solo.drop(columns=["modelo", "estrato"]).to_string(index=False))


if __name__ == "__main__":
    main()
