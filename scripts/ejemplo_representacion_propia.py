#!/usr/bin/env python3
"""Ejemplo de punta a punta de la herramienta de representaciones propias (#295).

La «tabla de la patrocinadora» es aquí una tabla de tres propiedades que se calculan en este mismo
script con RDKit (TPSA, donadores de hidrógeno y peso), para que el ejemplo corra sin datos externos. Se
mide contra la representación de descriptores del proyecto y contra un control de ruido, en la fase 1,
con la regresión logística. Para usar una tabla propia basta cambiar `mi_tabla` por un `read_csv` con una
columna `smiles` y las columnas numéricas que se quieran medir.

    BIOACTIVE_AUTOR=ingrid ./env/bin/python scripts/ejemplo_representacion_propia.py

**Registra la corrida.** La cifra del ejemplo se publica en `docs/medir-una-representacion.md`, que va
al sitio, y una cifra publicada necesita su corrida: la guía misma advierte en su primer *gotcha* de
medir que la regresión logística da 0.481, 0.489 o 0.497 de MCC según el sistema operativo y la versión
de Python, así que sin el entorno registrado el ejemplo contradice su propio aviso. La carpeta queda en
`experimentos/` con el `sha256` de los datos, el commit y las versiones.

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
from src.models.tareas import DESCRIPTORES, PROCESADOS
from src.tracking import Corrida


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
    params = {"representaciones": ["descriptores", "tpsa_hbd_peso", "ruido_3_columnas"],
              "referencia": "descriptores", "modelo": "logistica",
              "columnas_propias": ["tpsa", "donadores", "peso"],
              "filas": int(base.X.shape[0]), "grupos": int(len(set(base.grupos))),
              "por_que_estas_tres": ("son los filtros de la literatura de permeabilidad; la fase 1 ya "
                                     "midió que TPSA no domina (puesto 40 por permutación y 10 por "
                                     "SHAP) y que los donadores sí entran (puesto 4)"),
              "toca_prueba": False}
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    with Corrida("ejemplo-representacion-propia", decision="1.3", params=params,
                 semillas=[0, 1, 2], datos=datos) as c:
        resumen, pliegues = comparar(
            {"descriptores": base, "tpsa_hbd_peso": mia, "ruido_3_columnas": ruido},
            logistica, referencia="descriptores")
        # Los CSV antes de `metricas()`: son el producto caro y las métricas se derivan de ellos.
        resumen.to_csv(c.carpeta / "resumen.csv", index=False)
        pliegues.to_csv(c.carpeta / "pliegues.csv", index=False)
        solo = resumen[(resumen["estrato"] == "todos") & resumen["metrica"].isin(["mcc", "auroc"])]
        c.metricas({"todos": solo.drop(columns=["modelo", "estrato"]).to_dict("records")})

        print(f"Referencia: descriptores ({base.X.shape[1]} columnas), {base.X.shape[0]:,} compuestos, "
              f"{len(set(base.grupos)):,} grupos.\n")
        print(solo.drop(columns=["modelo", "estrato"]).to_string(index=False))
        print(f"\n  carpeta: experimentos/{c.id}")


if __name__ == "__main__":
    main()
