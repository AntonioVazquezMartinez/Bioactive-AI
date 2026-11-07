#!/usr/bin/env python3
"""¿La escalera de la fase 1 depende de cómo se define «parecido»? (E13)

La escalera agrupa por componentes conexas de Tanimoto sobre Morgan radio 2 (ECFP4). Esa es una
decisión: otra huella da otros vecinos. Aquí se repite la escalera con dos definiciones más y se mira
si el efecto de la semejanza sobre el modelo entregado cambia.

**Cómo se hace comparable.** Un umbral de 0.5 no significa lo mismo en dos huellas distintas, así que
**no se comparan umbrales sino peldaños de igual severidad**: para cada huella se elige el umbral cuyo
número de grupos queda más cerca de los de ECFP4 (1,413, 1,017 y 631, de la corrida
`2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`), con umbrales en pasos de 0.01.

**Huellas.** ECFP4 (control: Morgan radio 2, 2048 bits), ECFP6 (Morgan radio 3, 2048 bits) y atom-pair
(2048 bits). Modelo: `svm_rbf` y `logistica`, las mismas 15 evaluaciones agrupadas.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: con ECFP4 los grupos son 1,413, 1,017 y 631, y el AUROC del `svm_rbf` en esos peldaños es el de
   la corrida registrada (0.9127, 0.8348, 0.7798) dentro de 0.003. Si no, hay un error.
2. La escalera **es robusta a la definición** si, para cada huella y en cada uno de los tres peldaños, el
   AUROC del `svm_rbf` difiere del de ECFP4 en menos de **0.020** (unas siete veces la desviación pareada
   del `svm_rbf`, 0.0028). Si en algún peldaño difiere más, la escalera **depende** de la definición y el
   artículo tiene que decir cuál usó.
3. Los grupos con más del 20% de las filas dejan el peldaño sin evaluar; se marca.
4. Una sola familia de molécula–representación (descriptores RDKit) y dos modelos.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_escalera_definicion_de_parecido.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator

from src.evaluation.cv import evaluar
from src.features.similitud import grupos_por_similitud, matriz_dispersa, resumen_grupos
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
GRUPOS_ECFP4 = {"6": 1413, "5": 1017, "4": 631}      # de: 2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad
AUROC_ECFP4 = {"6": 0.9127, "5": 0.8348, "4": 0.7798}  # idem, svm_rbf
MODELOS = ("svm_rbf", "logistica")
TOLERANCIA_CONTROL = 0.003
DIFERENCIA_MAXIMA = 0.020
MAX_GRUPO = 0.20
BUSQUEDA = np.round(np.arange(0.20, 0.96, 0.01), 2)


def generadores() -> dict:
    return {
        "ECFP4": rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048),
        "ECFP6": rdFingerprintGenerator.GetMorganGenerator(radius=3, fpSize=2048),
        "atom-pair": rdFingerprintGenerator.GetAtomPairGenerator(fpSize=2048),
    }


def huellas(smiles: list[str], gen) -> list:
    return [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in smiles]


def umbral_con_grupos(S, objetivo: int) -> tuple[float, np.ndarray]:
    """El umbral (en pasos de 0.01) cuyo número de grupos queda más cerca de `objetivo`."""
    mejor = None
    for u in BUSQUEDA:
        g = grupos_por_similitud(S, float(u))
        err = abs(len(np.unique(g)) - objetivo)
        if mejor is None or err < mejor[0]:
            mejor = (err, float(u), g)
    return mejor[1], mejor[2]


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    smiles = t.meta["SMILES"].tolist()
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"huellas": list(generadores()), "modelos": list(MODELOS), "semillas": list(SEMILLAS),
              "grupos_objetivo": GRUPOS_ECFP4, "diferencia_maxima": DIFERENCIA_MAXIMA,
              "tolerancia_control": TOLERANCIA_CONTROL, "paso_umbral": 0.01, "filas": int(len(t.y)),
              "toca_prueba": False}
    with Corrida("escalera-definicion-de-parecido-permeabilidad", decision="1.2", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        filas = []
        for nombre, gen in generadores().items():
            t0 = time.perf_counter()
            fps = huellas(smiles, gen)
            S = matriz_dispersa(fps, BUSQUEDA.min())
            print(f"{nombre}: similitud lista en {time.perf_counter() - t0:.0f} s", flush=True)
            for clave, objetivo in GRUPOS_ECFP4.items():
                u, g = umbral_con_grupos(S, objetivo)
                fila = {"huella": nombre, "peldano": f"≈{objetivo} grupos", "clave": clave, "umbral": u,
                        **resumen_grupos(g)}
                if fila["mayor_grupo_pct"] > 100 * MAX_GRUPO:
                    fila["nota"] = "no evaluable: un grupo pasa del 20% de las filas"
                else:
                    res, _ = evaluar(seleccion(MODELOS), t.X, t.y, g, semillas=SEMILLAS, verboso=False)
                    todos = res[res["estrato"] == "todos"]
                    for modelo, gg in todos.groupby("modelo"):
                        fila[f"auroc_{modelo}"] = round(float(gg["auroc"].mean()), 4)
                        fila[f"mcc_{modelo}"] = round(float(gg["mcc"].mean()), 4)
                filas.append(fila)
                print(fila, flush=True)
                pd.DataFrame(filas).to_csv(c.carpeta / "escalera.csv", index=False)
        tabla = pd.DataFrame(filas)
        ecfp4 = tabla[tabla["huella"] == "ECFP4"].set_index("clave")
        control_grupos = {k: int(ecfp4.loc[k, "grupos"]) == v for k, v in GRUPOS_ECFP4.items()}
        control_auroc = {k: abs(float(ecfp4.loc[k, "auroc_svm_rbf"]) - AUROC_ECFP4[k]) <= TOLERANCIA_CONTROL
                         for k in AUROC_ECFP4}
        diferencias = {}
        for nombre in ("ECFP6", "atom-pair"):
            sub = tabla[tabla["huella"] == nombre].set_index("clave")
            for k in GRUPOS_ECFP4:
                if "auroc_svm_rbf" in sub.columns and pd.notna(sub.loc[k, "auroc_svm_rbf"]):
                    diferencias[f"{nombre}|{k}"] = round(float(sub.loc[k, "auroc_svm_rbf"] - ecfp4.loc[k, "auroc_svm_rbf"]), 4)
                else:
                    diferencias[f"{nombre}|{k}"] = None
        robusta = all(v is not None and abs(v) < DIFERENCIA_MAXIMA for v in diferencias.values())
        c.metricas({"escalera": tabla.where(tabla.notna(), None).to_dict("records"),
                    "control_grupos_ecfp4": control_grupos, "control_auroc_ecfp4": control_auroc,
                    "diferencia_de_auroc_contra_ecfp4": diferencias, "la_escalera_es_robusta": robusta})
        print(f"\ncontrol grupos: {control_grupos}\ncontrol AUROC: {control_auroc}\ndiferencias: {diferencias}\n"
              f"robusta a la definición: {robusta}")


if __name__ == "__main__":
    main()
