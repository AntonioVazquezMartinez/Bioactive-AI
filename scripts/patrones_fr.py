#!/usr/bin/env python3
"""Exporta los patrones SMARTS de los descriptores `fr_*` para el navegador.

**Para qué.** El proyecto promete explicabilidad **a nivel de subestructura** —es
el requisito que la patrocinadora puso como no negociable ([C.2](../docs/decisiones.md#dc-2))—
y hoy eso se demuestra con una tabla de importancias. Con los patrones en el
navegador, el visualizador puede hacer lo otro: señalar en la molécula **qué
átomos producen cada columna**.

No vale para todas. De las 151 columnas de la matriz de la fase 1:

- las `fr_*` son conteos de un patrón SMARTS, así que se resaltan **exacto**;
- las VSA reparten área por átomo, así que se pueden colorear por átomo;
- las fisicoquímicas —TPSA, peso molecular, logP— son de la molécula entera y
  **no se pueden señalar**. Decirlo es la mitad del mensaje: un modelo que se
  apoya en TPSA explica distinto que uno que se apoya en `fr_lactam`.

Los patrones viven dentro de RDKit como el segundo argumento por omisión de cada
función de `Chem.Fragments`; aquí se recuperan y se escriben a JSON.

    python scripts/patrones_fr.py
"""

import json
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import Fragments

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "recursos" / "patrones_fr.json"

# Las que llegan a la matriz de trabajo llevan una marca, para que el
# visualizador pueda distinguir «existe en RDKit» de «la usa este proyecto».
MATRIZ = RAIZ / "data" / "processed" / "bbb_descriptores_filtrados_sin_normalizar.parquet"


def columnas_de_la_matriz() -> set[str] | None:
    """Las columnas que sobreviven la selección, o `None` si no hay artefacto.

    `data/processed/` no se versiona, así que en un checkout limpio —o en un
    worktree recién creado— el parquet no está. Devolver un conjunto vacío
    haría que todas las columnas salieran marcadas como «no llega a la matriz»,
    que es afirmar algo falso en vez de admitir que no se sabe.
    """
    if not MATRIZ.exists():
        return None
    import pandas as pd
    return set(pd.read_parquet(MATRIZ).columns)


def main() -> None:
    en_matriz = columnas_de_la_matriz()
    salida = {}
    sin_patron = []
    for nombre in sorted(n for n in dir(Fragments) if n.startswith("fr_")):
        f = getattr(Fragments, nombre)
        d = getattr(f, "__defaults__", None)
        if not (d and len(d) >= 2 and isinstance(d[1], Chem.rdchem.Mol)):
            sin_patron.append(nombre)
            continue
        salida[nombre] = {
            "smarts": Chem.MolToSmarts(d[1]),
            "describe": (f.__doc__ or "").strip(),
            "en_matriz": None if en_matriz is None else (nombre in en_matriz),
        }

    DESTINO.write_text(
        json.dumps({
            "_comentario": (
                "Generado por scripts/patrones_fr.py. Cada entrada es un descriptor "
                "`fr_*` de RDKit con el SMARTS que cuenta, para poder resaltar en la "
                "molécula los átomos que lo producen. `en_matriz` dice si la columna "
                "sobrevive a la selección de la fase 1."),
            "patrones": salida,
        }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    print(f"[escrito] {DESTINO.relative_to(RAIZ)}")
    if en_matriz is None:
        print(f"  {len(salida)} patrones · sin `data/processed/`, así que no se sabe "
              "cuáles llegan a la matriz: quedan en `null`, no en `false`")
    else:
        n_matriz = sum(1 for v in salida.values() if v["en_matriz"])
        print(f"  {len(salida)} patrones · {n_matriz} llegan a la matriz de 151 columnas")
    if sin_patron:
        print(f"  sin patrón recuperable: {', '.join(sin_patron)}")


if __name__ == "__main__":
    main()
