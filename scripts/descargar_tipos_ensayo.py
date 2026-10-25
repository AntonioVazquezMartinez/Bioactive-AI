#!/usr/bin/env python3
"""Baja de ChEMBL el tipo de cada ensayo detrás de las mediciones tipo IC.

Un IC50 no dice por sí solo en qué sentido actúa el compuesto. Si el ensayo es de
**unión** (tipo `B`: desplazamiento de un radioligando, competencia por fluorescencia),
mide cuánto se une y es una medida de afinidad como el Ki, también para un agonista;
solo si es **funcional** (`F`) mide inhibición. El archivo de la patrocinadora trae
`assay_type` únicamente en la ruta `neuronal_assay`, así que para las filas de `cns_target`
—casi todas las de las dianas de activación— el tipo se pide a ChEMBL por `assay_chembl_id`,
que sí viene en todas las filas de ChEMBL. NPASS y CMAUP no traen identificador de ensayo y
quedan sin tipo.

    python scripts/descargar_tipos_ensayo.py

Escribe `notebooks/datos/tipos_ensayo_chembl.csv` (identificador y tipo de cada ensayo; los
datos de ChEMBL son CC BY-SA 3.0). Pide solo los ensayos de filas IC50/IC33/IC60 que el
archivo no tipifica ya, por lotes; necesita red y tarda un par de minutos.
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
ACTIVIDAD = (RAIZ / "data/external/profesora"
             / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
SALIDA = RAIZ / "notebooks/datos/tipos_ensayo_chembl.csv"
API = "https://www.ebi.ac.uk/chembl/api/data/assay.json"
TIPOS_IC = ("IC50", "IC33", "IC60")
LOTE = 100


def main() -> None:
    d = pd.read_csv(ACTIVIDAD, low_memory=False, usecols=["activity_type", "assay_chembl_id"])
    ids = sorted(d.loc[d["activity_type"].isin(TIPOS_IC), "assay_chembl_id"].dropna().unique())
    print(f"{len(ids):,} ensayos con mediciones {'/'.join(TIPOS_IC)}")
    filas = []
    for i in range(0, len(ids), LOTE):
        lote = ids[i:i + LOTE]
        for intento in range(4):
            r = requests.get(API, params={"assay_chembl_id__in": ",".join(lote),
                                          "only": "assay_chembl_id,assay_type,assay_type_description",
                                          "limit": 1000}, timeout=60)
            if r.ok:
                break
            time.sleep(2 ** intento)
        r.raise_for_status()
        filas += r.json()["assays"]
        print(f"  {min(i + LOTE, len(ids)):,}/{len(ids):,}", end="\r", flush=True)
    t = pd.DataFrame(filas).sort_values("assay_chembl_id")
    faltan = set(ids) - set(t["assay_chembl_id"])
    print(f"\n{len(t):,} ensayos devueltos · sin respuesta: {len(faltan)}")
    print(t["assay_type"].value_counts(dropna=False).to_dict())
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA, index=False)
    print(f"Escrito {SALIDA.relative_to(RAIZ)}")
    if faltan:
        sys.exit(1)


if __name__ == "__main__":
    main()
