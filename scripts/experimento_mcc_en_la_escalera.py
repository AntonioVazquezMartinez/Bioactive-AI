#!/usr/bin/env python3
"""¿Cuánto del derrumbe del MCC a lo largo de la escalera es colocación del corte? (E15, fase 1)

En la escalera de agrupación el AUROC del `svm_rbf` baja de 0.947 a 0.780 y el MCC de 0.752 a 0.419; en
la prueba reservada el MCC cae 52% y el AUROC 14%. El MCC corta la probabilidad en 0.5, un punto fijo, y
bajo un cambio de distribución ese punto deja de ser el adecuado. Aquí se mide, en cada peldaño de la
escalera, cuánto MCC se recupera con un corte que no use las etiquetas de validación.

**Lecturas del MCC, con las mismas predicciones fuera de pliegue** (un ajuste por pliegue):
- `fijo`: probabilidad ≥ 0.5, la de siempre (control: reproduce el MCC de la escalera registrada).
- `prevalencia`: el cuantil que declara positiva la misma fracción que tiene el ajuste. No usa etiquetas
  de validación.
- `optimo`: el mejor corte del propio pliegue. Cota optimista, usa etiquetas; no es un resultado.

**Peldaños.** Los de la corrida `2026-11-03-artemio-1.2-escalera-ampliada-permeabilidad`: al azar, por
andamio, andamio + esqueleto (el del proyecto) y similitud ≥ 0.6, 0.5 y 0.4. Modelo: `svm_rbf`.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: `fijo` reproduce el MCC del `svm_rbf` de la escalera registrada (0.7515, 0.7209, 0.7017,
   0.6876, 0.4859, 0.4190) dentro de 0.003 en cada peldaño. Si no, el resto no se lee.
2. Sea `recuperado` = MCC(`prevalencia`) − MCC(`fijo`) en el peldaño. **La colocación explica parte del
   derrumbe** si `recuperado` en el peldaño de similitud ≥ 0.5 o ≥ 0.4 supera 0.020 (unas cuatro veces la
   desviación pareada del MCC del `svm_rbf`, 0.0054) **y** es mayor que en el peldaño del proyecto. Si es
   menor que 0.020 en los tres peldaños estrictos, el derrumbe es de discriminación y no de colocación.
3. Se reporta además la fracción que el corte fijo declara BBB+ en cada peldaño, contra la prevalencia
   real del ajuste, que es lo que muestra la colocación.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_mcc_en_la_escalera.py
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
from sklearn.base import clone
from sklearn.metrics import matthews_corrcoef
from sklearn.model_selection import StratifiedGroupKFold

from src.features.similitud import grupos_por_similitud, huellas, matriz_dispersa
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
UMBRALES = (0.6, 0.5, 0.4)
REFERENCIA = {"1 al azar": 0.7515, "3 por andamio": 0.7209, "4 andamio + esqueleto (actual)": 0.7017,
              "5 similitud ≥ 0.6": 0.6876, "5 similitud ≥ 0.5": 0.4859, "5 similitud ≥ 0.4": 0.4190}  # de: corrida de la escalera
TOLERANCIA = 0.003
RECUPERADO_MINIMO = 0.020


def mcc(y, p, corte):
    return float(matthews_corrcoef(y, (p >= corte).astype(int)))


def mejor_corte(y, p):
    cortes = np.unique(np.quantile(p, np.linspace(0.02, 0.98, 97)))
    return max(mcc(y, p, c) for c in cortes)


def peldanos(t) -> dict:
    meta = t.meta
    sin = "SIN_ANDAMIO"
    andamio = meta["andamio"].fillna(sin).to_numpy()
    solo_andamio = np.where(andamio == sin, meta["esqueleto"].to_numpy(), andamio)
    S = matriz_dispersa(huellas(meta["SMILES"].tolist()), min(UMBRALES))
    salida = {"1 al azar": np.arange(len(meta)), "3 por andamio": solo_andamio,
              "4 andamio + esqueleto (actual)": t.grupos}
    for u in UMBRALES:
        salida[f"5 similitud ≥ {u}"] = grupos_por_similitud(S, u)
    return salida


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    modelo = seleccion(("svm_rbf",))["svm_rbf"]
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelo": "svm_rbf", "semillas": list(SEMILLAS), "pliegues": 5, "referencia_mcc": REFERENCIA,
              "tolerancia": TOLERANCIA, "recuperado_minimo": RECUPERADO_MINIMO, "filas": int(len(t.y)),
              "toca_prueba": False}
    with Corrida("mcc-en-la-escalera-permeabilidad", decision="1.2", params=params, semillas=list(SEMILLAS),
                 datos=datos) as c:
        filas = []
        for nombre, g in peldanos(t).items():
            t0 = time.perf_counter()
            acum = {"fijo": [], "prevalencia": [], "optimo": [], "frac_positiva_a_05": []}
            for semilla in SEMILLAS:
                cv = StratifiedGroupKFold(5, shuffle=True, random_state=semilla)
                for aj, val in cv.split(t.X, t.y, g):
                    m = clone(modelo).fit(t.X[aj], t.y[aj])
                    p = m.predict_proba(t.X[val])[:, 1]
                    y = t.y[val]
                    corte = float(np.quantile(p, 1 - t.y[aj].mean()))
                    acum["fijo"].append(mcc(y, p, 0.5))
                    acum["prevalencia"].append(mcc(y, p, corte))
                    acum["optimo"].append(mejor_corte(y, p))
                    acum["frac_positiva_a_05"].append(float((p >= 0.5).mean()))
            fila = {"peldano": nombre, **{k: round(float(np.mean(v)), 4) for k, v in acum.items()},
                    "prevalencia_real": round(float(t.y.mean()), 4),
                    "recuperado": round(float(np.mean(np.array(acum["prevalencia"]) - np.array(acum["fijo"]))), 4)}
            filas.append(fila)
            print(fila, f"{time.perf_counter() - t0:.0f} s", flush=True)
        tabla = pd.DataFrame(filas).set_index("peldano")
        control = {k: abs(float(tabla.loc[k, "fijo"]) - v) <= TOLERANCIA for k, v in REFERENCIA.items()}
        rec = tabla["recuperado"]
        estrictos = [k for k in tabla.index if "≥ 0.5" in k or "≥ 0.4" in k]
        actual = float(rec[[k for k in tabla.index if k.startswith("4")][0]])
        explica = bool(any(float(rec[k]) > RECUPERADO_MINIMO and float(rec[k]) > actual for k in estrictos))
        c.metricas({"escalera": tabla.reset_index().to_dict("records"), "control_dentro_de_tolerancia": control,
                    "la_colocacion_explica_parte": explica})
        print(f"\ncontrol: {control}\nla colocación explica parte del derrumbe: {explica}")


if __name__ == "__main__":
    main()
