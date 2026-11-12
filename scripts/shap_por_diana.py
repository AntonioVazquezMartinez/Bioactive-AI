#!/usr/bin/env python3
"""SHAP de la fase 2 **separado por diana**: qué columnas pesan en cada diana, y cuánto pesa la diana misma.

En el modelo de la fase 2 la diana entra como 26 columnas 0/1 (`diana:MAOA`, ...). Un ranking global de SHAP las
mezcla con los descriptores y no contesta lo que interesa: *para esta diana, qué química empuja la potencia*.
Como cada fila es un par compuesto-diana y tiene exactamente una de esas 26 columnas en 1, el SHAP de cada fila se
puede agrupar por su diana. Aquí se hacen dos cosas con los mismos modelos y pliegues de
`2026-11-12-artemio-C.2-puntos-shap-por-compuesto-fase2` (`aft`, TreeSHAP, cinco pliegues agrupados, semilla 0):

1. **El efecto de la diana**: la suma de SHAP de las 26 columnas `diana:*` de la fila. Es cuánto sube o baja la
   predicción por *ser esa diana*, sin que intervenga la molécula.
2. **La química por diana**: media de |SHAP|, media con signo y correlación (valor de la columna contra su SHAP,
   Spearman) de cada descriptor, en las filas de cada diana.

A diferencia de aquella corrida, **no hay submuestra**: cada par queda en validación una vez, así que se explican
los 56,241. No toca la prueba reservada ni cambia ninguna cifra de desempeño. Escala de pActividad (`-phi / ln 10`):
positivo = más potente.

Un descriptor que pesa en una diana lo hace **dentro de lo que el modelo aprendió**, no es un mecanismo, y solo
se interpreta en dianas con filas suficientes (`MIN_FILAS`).

    ./env312/bin/python scripts/shap_por_diana.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import math
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import StratifiedGroupKFold

from scripts.experimento_atribucion_aft import datos as datos_fase2
from src.models.aft import RegresionAFT
from src.tracking import Corrida

MIN_FILAS = 500          # una diana con menos pares no se interpreta (hay 16 con 500 o más)
TOP_POR_DIANA = 8        # descriptores que se guardan por punto en el gráfico de cada diana
PUNTOS_POR_DIANA = 300


def calcular() -> tuple[np.ndarray, np.ndarray, np.ndarray, list]:
    """SHAP de todas las filas, cada una explicada por el modelo que no la vio. Devuelve (phi, X, diana, nombres)."""
    d = datos_fase2()
    nombres = [str(n) for n in d["nombres"]]
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    X = np.asarray(d["X"], dtype=np.float32)
    phi = np.zeros(X.shape, dtype=np.float32)
    cv = StratifiedGroupKFold(5, shuffle=True, random_state=0)
    for k, (aj, val) in enumerate(cv.split(X, clase, d["grupos"]), 1):
        m = RegresionAFT(semilla=0).fit(d["X"][aj], d["inferior"][aj], d["superior"][aj])
        contrib = m.booster_.predict(xgb.DMatrix(np.asarray(d["X"][val], dtype=float)), pred_contribs=True)[:, :-1]
        phi[val] = (-contrib / math.log(10)).astype(np.float32)
        print(f"  pliegue {k} de 5 · {len(val)} filas", flush=True)
    return phi, X, nombres


def main() -> None:
    params = {"modelo": "aft", "metodo": "TreeSHAP", "filas": "todas (cada par en validacion una vez)",
              "pliegues": 5, "min_filas_para_interpretar": MIN_FILAS, "toca_prueba": False}
    with Corrida("shap-por-diana-fase2", decision="C.2", params=params, semillas=[0]) as c:
        phi, X, nombres = calcular()
        es_diana = np.array([n.startswith("diana:") for n in nombres])
        idx_diana = np.where(es_diana)[0]
        idx_quim = np.where(~es_diana)[0]
        quimica = [nombres[j] for j in idx_quim]
        de_la_fila = np.array([nombres[idx_diana[i]][len("diana:"):] for i in X[:, idx_diana].argmax(1)])
        assert (X[:, idx_diana].sum(1) == 1).all(), "cada fila debe tener exactamente una diana"

        # 1. el efecto de la diana y el de la química, por diana
        efecto_d = phi[:, idx_diana].sum(1)
        quim_abs = np.abs(phi[:, idx_quim]).sum(1)
        diana_abs = np.abs(phi[:, idx_diana]).sum(1)
        filas = []
        for dn in sorted(set(de_la_fila)):
            m = de_la_fila == dn
            filas.append({"diana": dn, "n_pares": int(m.sum()),
                          "efecto_diana_media": float(efecto_d[m].mean()),
                          "efecto_diana_sd": float(efecto_d[m].std()),
                          "quimica_abs_suma_media": float(quim_abs[m].mean()),
                          "diana_abs_suma_media": float(diana_abs[m].mean())})
        ef = pd.DataFrame(filas).sort_values("efecto_diana_media", ascending=False)
        ef.to_csv(c.carpeta / "efecto_diana.csv", index=False)

        # 2. la química por diana
        largo = []
        for dn in sorted(set(de_la_fila)):
            m = de_la_fila == dn
            if m.sum() < 30:
                continue
            P, V = phi[m][:, idx_quim], X[m][:, idx_quim]
            for j, col in enumerate(quimica):
                v = V[:, j]
                corr = float(pd.Series(v).corr(pd.Series(P[:, j]), method="spearman")) if v.std() > 0 else float("nan")
                largo.append((dn, col, int(m.sum()), float(np.abs(P[:, j]).mean()), float(P[:, j].mean()), corr))
        por = pd.DataFrame(largo, columns=["diana", "columna", "n_pares", "media_abs", "media", "spearman_valor_shap"])
        por.to_csv(c.carpeta / "shap_por_diana.csv", index=False)

        # 3. puntos para dibujar, en las dianas con filas suficientes
        rng = np.random.default_rng(0)
        pts = []
        grandes = [dn for dn in sorted(set(de_la_fila)) if (de_la_fila == dn).sum() >= MIN_FILAS]
        for dn in grandes:
            fila_dn = np.where(de_la_fila == dn)[0]
            elegidas = rng.choice(fila_dn, PUNTOS_POR_DIANA, replace=False)
            top = por[por["diana"] == dn].nlargest(TOP_POR_DIANA, "media_abs")["columna"]
            for col in top:
                j = nombres.index(col)
                for i in elegidas:
                    pts.append((dn, int(i), col, float(phi[i, j]), float(X[i, j])))
        pd.DataFrame(pts, columns=["diana", "fila", "columna", "shap", "valor"]).to_csv(
            c.carpeta / "puntos_por_diana.csv", index=False)

        # cifras para el texto
        tot_diana = float(diana_abs.mean())
        tot_quim = float(quim_abs.mean())
        res = {"pares": int(len(X)), "dianas": int(len(set(de_la_fila))), "dianas_con_filas_suficientes": len(grandes),
               "media_abs_suma_diana": tot_diana, "media_abs_suma_quimica": tot_quim,
               "parte_de_la_diana": tot_diana / (tot_diana + tot_quim),
               "efecto_diana_mas_alto": ef.iloc[0][["diana", "efecto_diana_media"]].to_dict(),
               "efecto_diana_mas_bajo": ef.iloc[-1][["diana", "efecto_diana_media"]].to_dict()}
        c.metricas(res)
        print(res)


if __name__ == "__main__":
    main()
