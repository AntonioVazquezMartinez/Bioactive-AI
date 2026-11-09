#!/usr/bin/env python3
"""Prevalencia de BBB+ en el entrenamiento de cada brazo de la 1.11, sorteo por sorteo.

La revisión de la 1.11 propuso una lectura del MCC: meter filas raras de la prueba al ajuste baja el % de
BBB+ del entrenamiento y acerca el corte de 0.5 al que la prueba necesita; sería un efecto de umbral y no de
aprendizaje, porque el AUROC casi no se mueve (+0.0020) y el MCC sube +0.0352 en los 15 sorteos. Esto mide la
parte barata de esa lectura: **no entrena nada**, solo reconstruye los mismos 15 repartos (`repartir`, mismas
semillas) y cuenta qué fracción de cada conjunto de entrenamiento es BBB+.

Usa las etiquetas de la prueba, así que **es otra lectura de la prueba reservada**: pasa por `tomar_prueba` y
el script está en `PERMITIDOS`. No cambia ninguna cifra de la 1.11.

    ./env312/bin/python scripts/prevalencia_raros_al_ajuste.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from src.models.rareza_entrenamiento import matriz_similitud
from src.models.raros_al_ajuste import repartir, similitud_fuera_del_grupo, terciles_de_grupos
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida, tomar_prueba

SORTEOS = 15
MOTIVO = ("1.11: prevalencia de BBB+ en el entrenamiento de cada brazo (no entrena nada), para leer el efecto "
          "del MCC como umbral o como aprendizaje")


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano", incluir_prueba=True, motivo=MOTIVO)
    tomar_prueba(t.meta, final=True, motivo=MOTIVO)
    y = np.asarray(t.y)
    particion, grupos = t.meta["particion"].to_numpy(), np.asarray(t.grupos)
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    with Corrida("raros-al-ajuste-prevalencia-permeabilidad", decision="1.11",
                 params={"sorteos": SORTEOS, "toca_prueba": True, "entrena": False},
                 semillas=list(range(SORTEOS)), datos=datos) as c:
        sim = similitud_fuera_del_grupo(matriz_similitud(t.meta["SMILES"].to_numpy()), grupos)
        terc = terciles_de_grupos(sim, grupos, np.asarray(t.estratos))
        filas = []
        for r in range(SORTEOS):
            rep = repartir(particion, grupos, terc, r)
            fila = {"sorteo": r, "prevalencia_E": float(y[rep.evaluacion].mean()),
                    "prevalencia_Q": float(y[rep.quitadas].mean()),
                    "prevalencia_movidas_raras": float(y[rep.movidas_raras].mean()),
                    "prevalencia_movidas_azar": float(y[rep.movidas_azar].mean())}
            for brazo in "ABCD":
                fila[f"prevalencia_entrena_{brazo}"] = float(y[rep.entrenamiento(brazo)].mean())
            filas.append(fila)
        tabla = pd.DataFrame(filas)
        tabla.to_csv(c.carpeta / "prevalencia.csv", index=False)
        medias = {k: round(float(v), 4) for k, v in tabla.drop(columns="sorteo").mean().items()}
        print(pd.Series(medias).to_string())
        c.metricas({"medias": medias,
                    "b_menos_a_prevalencia_entrena": round(float((tabla["prevalencia_entrena_B"]
                                                                   - tabla["prevalencia_entrena_A"]).mean()), 4)})


if __name__ == "__main__":
    main()
