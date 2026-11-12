#!/usr/bin/env python3
"""Un ranking por fase para los compuestos de ejemplo del cuaderno 06: es lo que muestra la presentación.

Ordena **cada fase por separado**, con los modelos finales entrenados sobre las filas de ajuste:

- fase 1: de mayor a menor probabilidad de cruzar la barrera (`p_bbb_mas`);
- fase 2: de mayor a menor potencia máxima predicha contra alguna diana (`pActividad_max`).

**No combina las dos fases**: esa combinación sigue pendiente (C.3); este orden por fase es parte de la C.5. Y **no es una lista de candidatos**: son
compuestos conocidos que el cuaderno trae de ejemplo, y casi todos estaban en el entrenamiento (similitud 1.0),
así que su predicción no es una prueba del modelo. Se deja `similitud` junto al lugar para que se lea así.
El SMILES inválido y la molécula diminuta de los ejemplos del cuaderno se omiten: están ahí para ver los avisos.

No toca la prueba reservada: `inferencia.cargar()` usa los modelos guardados en `models/finales/`.

    ./env312/bin/python scripts/ranking_por_fase_ejemplo.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))


from src import inferencia
from src.tracking import Corrida

EJEMPLOS = {
    "cafeína": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "nicotina": "CN1CCC[C@H]1c1cccnc1",
    "galantamina": "COc1ccc2c3c1O[C@H]1C[C@@H](O)C=C[C@@]31CCN(C)C2",
    "resveratrol": "Oc1ccc(/C=C/c2cc(O)cc(O)c2)cc1",
    "curcumina": "COc1cc(/C=C/C(=O)CC(=O)/C=C/c2ccc(O)c(OC)c2)ccc1O",
    "quercetina": "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
}


def main() -> None:
    params = {"compuestos": EJEMPLOS, "toca_prueba": False, "combina_fases": False}
    with Corrida("ranking-por-fase-ejemplo", decision="C.5", params=params, semillas=[0]) as c:
        modelos = inferencia.cargar()
        r = inferencia.predecir(list(EJEMPLOS.values()), modelos)
        r.insert(0, "nombre", list(EJEMPLOS))
        fase1 = r.sort_values("p_bbb_mas", ascending=False).reset_index(drop=True)
        fase1.insert(0, "lugar", range(1, len(fase1) + 1))
        fase2 = r.sort_values("pActividad_max", ascending=False).reset_index(drop=True)
        fase2.insert(0, "lugar", range(1, len(fase2) + 1))
        fase1[["lugar", "nombre", "p_bbb_mas", "similitud_fase1", "aviso_extrapolacion"]].to_csv(
            c.carpeta / "ranking_fase1.csv", index=False)
        fase2[["lugar", "nombre", "pActividad_max", "mejor_diana", "similitud_fase2", "aviso_extrapolacion"]].to_csv(
            c.carpeta / "ranking_fase2.csv", index=False)
        print(fase1[["lugar", "nombre", "p_bbb_mas", "similitud_fase1", "aviso_extrapolacion"]].round(3).to_string(index=False))
        print(fase2[["lugar", "nombre", "pActividad_max", "mejor_diana", "similitud_fase2", "aviso_extrapolacion"]]
              .round(3).to_string(index=False))
        c.metricas({
            "fase1": dict(zip(fase1["nombre"], fase1["p_bbb_mas"].round(4), strict=True)),
            "fase2": dict(zip(fase2["nombre"], fase2["pActividad_max"].round(4), strict=True)),
        })


if __name__ == "__main__":
    main()
