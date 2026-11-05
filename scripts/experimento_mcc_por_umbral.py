#!/usr/bin/env python3
"""¿La ventaja del `aft` en MCC es discriminación o dónde cae su distribución? (#185, fase 2)

La razón número uno para elegir el `aft` dice «gana donde el proyecto decide, MCC 0.467 contra
0.310». Pero el mismo par ordena peor (concordancia −0.004, Spearman −0.057) y yerra más (RMSE
+0.093) con un AUROC casi empatado (+0.013). El MCC corta la potencia predicha en pActividad 5,
así que mide también **dónde cae la distribución predicha** respecto de ese corte, y el `bosque`
(que se ajusta solo con las exactas, ricas en activos) cae en otro lugar por construcción.

**Lo que se mide.** Las mismas 15 evaluaciones agrupadas de la 2.13 (5 pliegues, semillas 0 a 2,
mismas filas y matrices que el 05b), `aft` contra `bosque`, y para cada uno el MCC leído de tres
maneras con **las mismas predicciones** (se ajusta una vez por pliegue):

| lectura | corte | usa etiquetas de validación |
|:--|:--|:--|
| `fijo` | pActividad 5, el de la comparativa (control: debe reproducir 0.3103 y 0.4668) | no |
| `prevalencia` | el cuantil de la potencia predicha que declara activa la **misma fracción que tiene el ajuste** | no, solo las del ajuste |
| `optimo` | el mejor corte posible en el propio pliegue | sí: es una cota optimista, no un resultado |

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. `fijo` debe reproducir el MCC de la comparativa dentro de 0.01. Si no, hay un error y el resto
   no se lee.
2. La razón «gana en MCC» **se sostiene** si, con `prevalencia`, la diferencia pareada
   `aft − bosque` es positiva, mayor que su desviación pareada y se cumple en al menos 12 de 15
   evaluaciones. Si queda dentro de la dispersión, la razón se reescribe como colocación y no
   como discriminación. Vale para `todos` y se mira aparte en `solo_npass`, que es el estrato por el
   que la 2.13 eligió el modelo.
3. El AUROC y la concordancia no dependen del corte y se reportan al lado.
4. Se reporta lo que salga, aunque favorezca o perjudique al `aft`. El argumento de NPASS no depende
   de esta línea y no se evalúa aquí.

No toca la prueba reservada.

    ./env/bin/python scripts/experimento_mcc_por_umbral.py
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
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline

sys.path.insert(0, str(RAIZ / "scripts"))
from experimento_aft_huellas import DESCRIPTORES, N_BITS, PARES, PLIEGUES, SEMILLAS, datos  # noqa: E402
from src.evaluation.regresion import metricas_regresion
from src.features.huellas import AgregarHuellas
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import CORTE_10_UM, MIN_POR_CLASE, SoloExactas
from src.tracking import Corrida

ESTRATOS = ("todos", "solo_chembl", "mixto", "solo_npass")
REFERENCIA = {"aft": 0.4668, "bosque": 0.3103}   # MCC `todos` de la comparativa 2.13 (#185)
TOLERANCIA = 0.01
REGLA_EVALUACIONES = 12


def mcc_en(y: np.ndarray, p: np.ndarray, corte: float) -> float:
    return float(matthews_corrcoef(y, (p >= corte).astype(int)))


def mejor_corte(y: np.ndarray, p: np.ndarray) -> float:
    """MCC máximo sobre cortes en los cuantiles de `p`: cota optimista, usa las etiquetas."""
    cortes = np.unique(np.quantile(p, np.linspace(0.02, 0.98, 97)))
    return max(mcc_en(y, p, c) for c in cortes)


def modelos(n_densas: int) -> dict:
    def con_huellas(m):
        return make_pipeline(AgregarHuellas(n_densas, n_bits=N_BITS), m)
    return {
        "aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
        "bosque": ("X_mixta", SoloExactas(con_huellas(
            RandomForestRegressor(random_state=SEMILLAS[0], n_jobs=-1)))),
    }


def correr(d: dict, c: Corrida) -> pd.DataFrame:
    catalogo = modelos(d["n_densas"])
    clase = d["clase"]
    estratificar = np.where(np.isnan(clase), -1, clase).astype(int)
    filas = []
    for semilla in SEMILLAS:
        cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=semilla)
        for k, (aj, val) in enumerate(cv.split(d["X"], estratificar, d["grupos"]), 1):
            # Fracción de activos del ajuste, solo con las filas cuyo intervalo decide la etiqueta.
            tasa_ajuste = float(np.nanmean(clase[aj]))
            for nombre, (matriz, modelo) in catalogo.items():
                m = clone(modelo)
                t = time.perf_counter()
                X = d[matriz]
                m.fit(X[aj], d["inferior"][aj], d["superior"][aj])
                seg = time.perf_counter() - t
                pred = m.predict(X[val])
                for estrato in ESTRATOS:
                    sel = (np.ones(len(val), bool) if estrato == "todos"
                           else d["procedencia"][val] == estrato)
                    if not sel.any():
                        continue
                    decide = ~np.isnan(clase[val][sel])
                    y = clase[val][sel][decide].astype(int)
                    if len(np.unique(y)) < 2:
                        continue
                    if estrato != "todos" and min(y.sum(), (1 - y).sum()) < MIN_POR_CLASE:
                        continue
                    p = pred[sel][decide]
                    reg = metricas_regresion(d["inferior"][val][sel], d["superior"][val][sel],
                                             pred[sel])
                    corte_prev = float(np.quantile(p, 1 - tasa_ajuste))
                    filas.append({
                        "modelo": nombre, "semilla": semilla, "pliegue": k, "estrato": estrato,
                        "n": int(len(y)), "activos": float(y.mean()), "tasa_ajuste": tasa_ajuste,
                        "frac_activa_a_5": float((p >= CORTE_10_UM).mean()),
                        "mcc_fijo": mcc_en(y, p, CORTE_10_UM),
                        "mcc_prevalencia": mcc_en(y, p, corte_prev),
                        "mcc_optimo": mejor_corte(y, p),
                        "auroc": float(roc_auc_score(y, p)),
                        "concordancia": reg["concordancia"], "seg": seg})
            pd.DataFrame(filas).to_csv(c.carpeta / "pliegues.csv", index=False)
            print(f"  semilla {semilla} · pliegue {k} listo", flush=True)
    return pd.DataFrame(filas)


def pareado(res: pd.DataFrame, estrato: str, col: str) -> dict:
    sub = res[res["estrato"] == estrato]
    piv = sub.pivot_table(index=["semilla", "pliegue"], columns="modelo", values=col).dropna()
    if piv.empty:
        return {}
    dif = piv["aft"] - piv["bosque"]
    return {"aft": round(float(piv["aft"].mean()), 4), "bosque": round(float(piv["bosque"].mean()), 4),
            "dif_media": round(float(dif.mean()), 4), "dif_desv": round(float(dif.std()), 4),
            "aft_mejor_en": int((dif > 0).sum()), "evaluaciones": int(len(dif))}


def main() -> None:
    d = datos()
    params = {"modelos": ["aft", "bosque"], "semillas": list(SEMILLAS), "pliegues": PLIEGUES,
              "cortes": ["fijo=5.0", "prevalencia del ajuste", "optimo en el pliegue (cota)"],
              "referencia_2_13": REFERENCIA, "tolerancia_reproduccion": TOLERANCIA,
              "regla_evaluaciones": REGLA_EVALUACIONES, "toca_prueba": False,
              "nota_seg": "tiempo de reloj con doce núcleos; no comparable con la 2.13"}
    with Corrida("mcc-por-umbral-aft-contra-bosque", decision="2.13", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        res = correr(d, c)
        salida = {}
        for estrato in ESTRATOS:
            salida[estrato] = {col: pareado(res, estrato, col)
                               for col in ("mcc_fijo", "mcc_prevalencia", "mcc_optimo",
                                           "auroc", "concordancia", "frac_activa_a_5")}
        todos = salida["todos"]["mcc_fijo"]
        reproduce = {m: abs(todos[m] - REFERENCIA[m]) <= TOLERANCIA for m in REFERENCIA}
        salida["reproduccion_del_corte_fijo"] = {"referencia": REFERENCIA, "obtenido":
                                                 {m: todos[m] for m in REFERENCIA},
                                                 "dentro_de_tolerancia": reproduce}
        for estrato in ("todos", "solo_npass"):
            p = salida[estrato]["mcc_prevalencia"]
            if p:
                salida[estrato]["se_sostiene_con_prevalencia"] = bool(
                    p["dif_media"] > 0 and p["dif_media"] > p["dif_desv"]
                    and p["aft_mejor_en"] >= REGLA_EVALUACIONES)
        c.metricas(salida)
        for estrato in ESTRATOS:
            print(f"\n=== {estrato}")
            for col, v in salida[estrato].items():
                if isinstance(v, dict):
                    print(f"  {col:17}{v}")
                else:
                    print(f"  {col:17}{v}")
        print("\nreproducción del corte fijo:", salida["reproduccion_del_corte_fijo"])


if __name__ == "__main__":
    main()
