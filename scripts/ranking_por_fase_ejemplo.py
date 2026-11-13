#!/usr/bin/env python3
"""Un ranking por fase para seis compuestos **de la prueba reservada**: es lo que muestran la presentación y el cuaderno 06.

Los compuestos no se escogen a mano. La regla, fijada antes de mirar ninguna predicción:

1. Candidatos: compuestos de la prueba reservada de la fase 1 cuyo **esqueleto** también está en la prueba de la
   fase 2 y **no** está en el ajuste de ninguna de las dos (así ninguna de las dos fases los vio, ni a ellos ni a un
   estereoisómero).
2. Con nombre (solo letras, hasta dos palabras: se descartan códigos como `chembl218017` o `zinc19848892`) y con
   alguna potencia medida en la fase 2.
3. Seis, por sorteo con semilla 0 sobre la lista ordenada por nombre.

Cada fase se ordena **por separado** con los modelos finales (entrenados solo con las filas de ajuste): la fase 1
por la probabilidad de cruzar la barrera y la fase 2 por la potencia máxima predicha contra alguna diana. Junto a
cada predicción se guarda **lo medido**: la etiqueta BBB de la fase 1 y la mayor potencia medida en la fase 2, con
su diana. **No combina las dos fases** (C.3 sigue pendiente) y **no es una lista de candidatos ni una métrica**: son
seis ejemplos para ver el formato; la métrica está en las diapositivas de resultados y en el artículo.

Lee la prueba reservada, así que pasa por `tomar_prueba` y queda en `experimentos/prueba.csv`. No cambia ningún
modelo ni ninguna cifra de desempeño: solo elige seis compuestos y muestra su valor medido.

    ./env312/bin/python scripts/ranking_por_fase_ejemplo.py
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from src import inferencia
from src.tracking import Corrida, tomar_prueba

SEMILLA = 0
CUANTOS = 6
SOLO_LETRAS = re.compile(r"^[a-z]{4,}( [a-z]+)?$")


def elegir() -> tuple[pd.DataFrame, int]:
    """Los seis compuestos, con su SMILES y lo medido en cada fase."""
    meta = pd.read_parquet(RAIZ / "data" / "processed" / "bbb_meta.parquet")
    pares = pd.read_parquet(RAIZ / "data" / "processed" / "fase2_pares.parquet")
    ajuste1 = set(meta.loc[meta["particion"] != "prueba", "esqueleto"])
    ajuste2 = set(pares.loc[pares["particion"] != "prueba", "esqueleto"])
    t1 = tomar_prueba(meta, final=True,
                      motivo="C.5: elegir seis compuestos de ejemplo para el cuaderno 06 y mostrar su etiqueta BBB; no evalúa ni cambia ningún modelo")
    t2 = tomar_prueba(pares, final=True,
                      motivo="C.5: mostrar la mayor potencia medida de esos seis compuestos; no evalúa ni cambia ningún modelo")
    comunes = (set(t1["esqueleto"]) & set(t2["esqueleto"])) - ajuste1 - ajuste2
    medida = (t2[t2["esqueleto"].isin(comunes)].dropna(subset=["pActividad"])
              .sort_values("pActividad", ascending=False).drop_duplicates("esqueleto").set_index("esqueleto"))
    c = t1[t1["esqueleto"].isin(medida.index) & t1["compound_name"].fillna("").str.match(SOLO_LETRAS)]
    c = c.sort_values("compound_name").drop_duplicates("esqueleto").reset_index(drop=True)
    candidatos = len(c)
    elegidos = np.random.default_rng(SEMILLA).choice(candidatos, CUANTOS, replace=False)
    c = c.iloc[sorted(elegidos)].reset_index(drop=True)
    return pd.DataFrame({
        "nombre": c["compound_name"],
        "smiles": c["SMILES"],
        "bbb_real": c["y"].astype(int),
        "pActividad_medida": c["esqueleto"].map(medida["pActividad"]).round(2),
        "diana_medida": c["esqueleto"].map(medida["target_gene"]),
    }), candidatos


def main() -> None:
    elegidos, candidatos = elegir()
    params = {"compuestos": dict(zip(elegidos["nombre"], elegidos["smiles"], strict=True)), "semilla": SEMILLA,
              "candidatos_con_nombre": candidatos, "combina_fases": False, "toca_prueba": True,
              "uso_de_la_prueba": "solo elige seis compuestos y muestra su valor medido; ningun modelo cambia"}
    with Corrida("ranking-por-fase-ejemplo-prueba", decision="C.5", params=params, semillas=[SEMILLA]) as c:
        modelos = inferencia.cargar()
        r = inferencia.predecir(elegidos["smiles"].tolist(), modelos)
        r = pd.concat([elegidos.drop(columns="smiles"), r.reset_index(drop=True)], axis=1)
        fase1 = r.sort_values("p_bbb_mas", ascending=False).reset_index(drop=True)
        fase1.insert(0, "lugar", range(1, len(fase1) + 1))
        fase2 = r.sort_values("pActividad_max", ascending=False).reset_index(drop=True)
        fase2.insert(0, "lugar", range(1, len(fase2) + 1))
        c1 = ["lugar", "nombre", "p_bbb_mas", "bbb_real", "similitud_fase1", "aviso_extrapolacion"]
        c2 = ["lugar", "nombre", "pActividad_max", "mejor_diana", "pActividad_medida", "diana_medida",
              "similitud_fase2", "aviso_extrapolacion"]
        fase1[c1].to_csv(c.carpeta / "ranking_fase1.csv", index=False)
        fase2[c2].to_csv(c.carpeta / "ranking_fase2.csv", index=False)
        print(fase1[c1].round(3).to_string(index=False))
        print(fase2[c2].round(3).to_string(index=False))
        c.metricas({
            "candidatos_con_nombre": candidatos,
            "fase1": dict(zip(fase1["nombre"], fase1["p_bbb_mas"].round(4), strict=True)),
            "fase2": dict(zip(fase2["nombre"], fase2["pActividad_max"].round(4), strict=True)),
        })


if __name__ == "__main__":
    main()
