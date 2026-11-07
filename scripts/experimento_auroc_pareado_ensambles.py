#!/usr/bin/env python3
"""¿Algún ensamble supera al mejor individual en AUROC, con la diferencia pareada y su intervalo? (E18)

Grettel (3 de nov) señaló que «si el objetivo es determinar si un ensamble presenta un AUROC superior al modelo
individual, deben evaluar directamente la diferencia entre ambos AUROC y estimar su intervalo», no comparar el
traslape de intervalos individuales. El 05 ya hace la diferencia pareada para MCC y AUPRC (con la corrección de
Nadeau y Bengio, #188); falta el AUROC.

**Qué se hace.** Sin entrenar nada: lee el detalle por pliegue de la corrida
`2026-11-01-artemio-1.5-ensambles-permeabilidad` (`pliegues.csv`, #256). Para cada uno de los diez modelos
distintos del individual `svm_rbf`, en las mismas 15 evaluaciones (3 semillas × 5 pliegues): la diferencia pareada
(modelo − `svm_rbf`), su media, su desviación y el intervalo del 95% con la **corrección de Nadeau y Bengio**
(error × √(1/J + n_prueba/n_entrenamiento), con J = 15 y la proporción 1/4, y t de 14 grados de libertad), la
misma de la 1.7. Se hace para AUROC y, como control, para MCC y AUPRC.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: el intervalo de MCC de `stacking` y de `votacion` reproduce el que publica el #228
   (`stacking` +0.0093 [−0.0101, +0.0287]; `votacion` +0.0075 [−0.0113, +0.0263]) dentro de 0.0005. Si no, la
   corrección está mal implementada y el resto no se lee.
2. Un modelo **supera** al individual en AUROC si el límite inferior de su intervalo es mayor que 0; **empeora** si
   el superior es menor que 0; en otro caso el intervalo incluye el cero y **no se distingue**.
3. Se reporta también en cuántas de las 15 evaluaciones gana, sin que decida.
4. No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_auroc_pareado_ensambles.py
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from scipy import stats

from src.tracking import Corrida

CORRIDA = "2026-11-01-artemio-1.5-ensambles-permeabilidad"
DETALLE = RAIZ / "experimentos" / CORRIDA / "pliegues.csv"
INDIVIDUAL = "svm_rbf"
PLIEGUES = 5
CONTROL = {"stacking": (0.0093, -0.0101, 0.0287), "votacion": (0.0075, -0.0113, 0.0263)}   # de: #188, decisión 1.7
TOLERANCIA = 0.0005


def intervalo_nb(dif: np.ndarray) -> tuple[float, float, float, float]:
    """Media, desviación y el IC del 95% corregido por Nadeau y Bengio para J evaluaciones sobre k pliegues."""
    j = len(dif)
    media, desv = float(dif.mean()), float(dif.std(ddof=1))
    proporcion = (1 / PLIEGUES) / (1 - 1 / PLIEGUES)
    ee = desv * np.sqrt(1 / j + proporcion)
    t = float(stats.t.ppf(0.975, j - 1))
    return media, desv, media - t * ee, media + t * ee


def main() -> None:
    d = pd.read_csv(DETALLE)
    todos = d[d["estrato"] == "todos"].set_index(["modelo", "semilla", "pliegue"])
    params = {"corrida_de_origen": CORRIDA, "individual": INDIVIDUAL, "evaluaciones": 15,
              "correccion": "Nadeau y Bengio, J = 15, proporcion 1/4, t de 14 g.l.", "control": CONTROL,
              "tolerancia": TOLERANCIA, "toca_prueba": False}
    with Corrida("auroc-pareado-ensambles-permeabilidad", decision="1.7", params=params, semillas=[0, 1, 2],
                 datos=[DETALLE]) as c:
        ref = todos.loc[INDIVIDUAL]
        filas = []
        for modelo in sorted(set(todos.index.get_level_values("modelo")) - {INDIVIDUAL}):
            fila = {"modelo": modelo}
            for metrica in ("auroc", "mcc", "auprc_minoritaria"):
                dif = (todos.loc[modelo][metrica] - ref[metrica]).to_numpy()
                m, s, lo, hi = intervalo_nb(dif)
                fila[metrica] = {"dif_media": round(m, 4), "desv": round(s, 4), "ic95": [round(lo, 4), round(hi, 4)],
                                 "gana_en": int((dif > 0).sum())}
            a = fila["auroc"]["ic95"]
            fila["veredicto_auroc"] = ("supera al individual" if a[0] > 0 else
                                       "empeora al individual" if a[1] < 0 else "no se distingue (el IC incluye el cero)")
            filas.append(fila)
        control = {}
        for modelo, (media, lo, hi) in CONTROL.items():
            f = next(x for x in filas if x["modelo"] == modelo)["mcc"]
            control[modelo] = bool(abs(f["dif_media"] - media) <= TOLERANCIA and abs(f["ic95"][0] - lo) <= TOLERANCIA
                                   and abs(f["ic95"][1] - hi) <= TOLERANCIA)
        c.metricas({"por_modelo": filas, "control_reproduce_el_188": control,
                    "modelos_que_superan_en_auroc": [f["modelo"] for f in filas if f["veredicto_auroc"].startswith("supera")]})
        print("control (reproduce el #188):", control)
        for f in filas:
            a = f["auroc"]
            print(f"{f['modelo']:18} ΔAUROC {a['dif_media']:+.4f} IC95 [{a['ic95'][0]:+.4f}, {a['ic95'][1]:+.4f}] "
                  f"gana en {a['gana_en']:>2}/15 · {f['veredicto_auroc']}")


if __name__ == "__main__":
    main()
