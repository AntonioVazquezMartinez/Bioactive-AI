#!/usr/bin/env python3
"""¿Qué características pesan en el `aft` final, según dos métodos independientes? (#146, C.2)

La C.2 exige al menos **dos métodos de atribución independientes** y reportar solo lo en que concuerdan; la
fase 2 no tenía ninguno (el `04b` no atribuía nada). Aquí, sobre el modelo final de la fase 2 (el `aft` con 201
descriptores y la diana, la 2.13):

| método | qué mide | de dónde sale |
|:--|:--|:--|
| TreeSHAP | cuánto aporta cada columna a la predicción (media del valor absoluto sobre el pliegue de validación) | los árboles del propio modelo (`pred_contribs` de XGBoost) |
| permutación | cuánta **concordancia** se pierde al barajar una columna en el pliegue de validación | solo la predicción y la etiqueta, sin mirar el modelo por dentro |

Son independientes en lo que importa: uno lee la estructura de los árboles y el otro solo sus salidas.

**Cómo.** Semilla 0, cinco pliegues agrupados (los de siempre). En cada pliegue se ajusta el `aft` con las filas
de ajuste y se atribuye sobre el pliegue de validación (la permutación, sobre 3,000 filas al azar de él, con dos
repeticiones). Se promedia sobre los pliegues.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control de TreeSHAP: la suma de las contribuciones más el sesgo reproduce la predicción del modelo en escala
   del margen (diferencia máxima < 1e-3), y coincide con `shap.TreeExplainer` en 200 filas (< 1e-3).
2. **Los dos métodos concuerdan** si la correlación de Spearman entre sus importancias (las 227 columnas) es al
   menos **0.70** y comparten al menos **8 de sus 15 columnas más importantes**. Si no, el artículo reporta solo
   las que comparten y dice que los métodos discrepan.
3. Se reporta la lista de las que están en el top 15 de **los dos**, con sus valores; solo esas se afirman.
4. Contraste con TPSA (< 67 Å²) y HBD (≤ 1), que `CLAUDE.md` pide antes que cualquier afirmación: en qué lugar
   queda `TPSA` y `NumHDonors` en cada método.
5. **Alcance:** el `aft` final **no usa huellas**, así que sus características son descriptores y dianas, no
   subestructuras. La parte de la C.2 que pide atribución por subestructura **no se puede cumplir con este modelo**
   y se declara así; hace falta el brazo con huellas.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_atribucion_aft.py
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
import shap
import xgboost as xgb
from scipy.stats import spearmanr
from sklearn.model_selection import StratifiedGroupKFold

from src.evaluation.regresion import concordancia_harrell
from src.models.aft import RegresionAFT
from src.tracking import Corrida

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
SEMILLA = 0
PLIEGUES = 5
FILAS_PERMUTACION = 3_000
REPETICIONES = 2
TOP = 15
RHO_MINIMO = 0.70
COMPARTIDAS_MINIMO = 8
TOLERANCIA_SHAP = 1e-3


def datos() -> dict:
    """Las mismas 56,241 filas y 227 columnas que el 05b, con el nombre de cada columna."""
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [c for c in desc.columns if c != "smiles"]
    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)
    d = d[util].reset_index(drop=True)
    inferior, superior = inferior[util], superior[util]
    fuera = (d["particion"] != "prueba").to_numpy()
    diana = pd.get_dummies(d["target_gene"])
    X = np.hstack([d[cols].to_numpy("float32"), diana.to_numpy("float32")])
    assert fuera.sum() == 56_241
    nombres = cols + [f"diana:{c}" for c in diana.columns]
    return {"X": X[fuera], "inferior": inferior[fuera], "superior": superior[fuera],
            "grupos": d["grupo_cv"].to_numpy()[fuera], "clase": d["activo_10um"].to_numpy(float)[fuera],
            "nombres": nombres, "n_desc": len(cols)}


def permutacion(modelo, X, inferior, superior, rng) -> np.ndarray:
    """Pérdida media de concordancia al barajar cada columna (sobre una muestra de la validación)."""
    idx = rng.choice(len(X), size=min(FILAS_PERMUTACION, len(X)), replace=False)
    Xs, inf, sup = X[idx], inferior[idx], superior[idx]
    base = concordancia_harrell(inf, sup, modelo.predict(Xs))
    perdida = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        for _ in range(REPETICIONES):
            Xp = Xs.copy()
            Xp[:, j] = rng.permutation(Xp[:, j])
            perdida[j] += base - concordancia_harrell(inf, sup, modelo.predict(Xp))
    return perdida / REPETICIONES


def main() -> None:
    d = datos()
    nombres = np.array(d["nombres"])
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    params = {"modelo": "aft (201 descriptores y diana, la 2.13)", "semilla": SEMILLA, "pliegues": PLIEGUES,
              "metodos": ["TreeSHAP (pred_contribs)", "permutación sobre la concordancia"],
              "filas_permutacion": FILAS_PERMUTACION, "repeticiones": REPETICIONES, "top": TOP,
              "rho_minimo": RHO_MINIMO, "compartidas_minimo": COMPARTIDAS_MINIMO, "toca_prueba": False}
    with Corrida("atribucion-aft-treeshap-y-permutacion", decision="2.13", params=params,
                 semillas=[SEMILLA], datos=[PARES, DESCRIPTORES]) as c:
        shap_pliegues, perm_pliegues = [], []
        control_aditividad, control_explainer = [], []
        rng = np.random.default_rng(SEMILLA)
        cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=SEMILLA)
        for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
            t0 = time.perf_counter()
            m = RegresionAFT(semilla=SEMILLA).fit(d["X"][aj], d["inferior"][aj], d["superior"][aj])
            Xv = np.asarray(d["X"][val], dtype=float)
            contrib = m.booster_.predict(xgb.DMatrix(Xv), pred_contribs=True)       # (n, 227 + 1)
            shap_pliegues.append(np.abs(contrib[:, :-1]).mean(axis=0))
            if k == 1:   # controles de TreeSHAP: aditividad y contra shap.TreeExplainer
                margen = m.booster_.predict(xgb.DMatrix(Xv[:200]), output_margin=True)
                control_aditividad.append(float(np.abs(contrib[:200].sum(axis=1) - margen).max()))
                ex = shap.TreeExplainer(m.booster_).shap_values(Xv[:200])
                control_explainer.append(float(np.abs(ex - contrib[:200, :-1]).max()))
            perm_pliegues.append(permutacion(m, Xv, d["inferior"][val], d["superior"][val], rng))
            print(f"  pliegue {k}: {time.perf_counter() - t0:.0f} s", flush=True)
        imp_shap = np.mean(shap_pliegues, axis=0)
        imp_perm = np.mean(perm_pliegues, axis=0)
        rho, _ = spearmanr(imp_shap, imp_perm)
        top_shap = set(np.argsort(-imp_shap)[:TOP])
        top_perm = set(np.argsort(-imp_perm)[:TOP])
        compartidas = sorted(top_shap & top_perm, key=lambda j: -imp_shap[j])
        # estabilidad entre pliegues de cada método
        est_shap = float(np.mean([spearmanr(shap_pliegues[a], shap_pliegues[b])[0]
                                  for a in range(PLIEGUES) for b in range(a + 1, PLIEGUES)]))
        est_perm = float(np.mean([spearmanr(perm_pliegues[a], perm_pliegues[b])[0]
                                  for a in range(PLIEGUES) for b in range(a + 1, PLIEGUES)]))
        rango_shap = (-imp_shap).argsort().argsort() + 1
        rango_perm = (-imp_perm).argsort().argsort() + 1
        n_desc = d["n_desc"]
        resultado = {
            "control_aditividad_max": max(control_aditividad), "control_contra_shap_explainer_max": max(control_explainer),
            "control_pasa": bool(max(control_aditividad) < TOLERANCIA_SHAP and max(control_explainer) < TOLERANCIA_SHAP),
            "spearman_entre_metodos": round(float(rho), 4), "compartidas_top15": len(compartidas),
            "concuerdan": bool(rho >= RHO_MINIMO and len(compartidas) >= COMPARTIDAS_MINIMO),
            "estabilidad_entre_pliegues": {"shap": round(est_shap, 4), "permutacion": round(est_perm, 4)},
            "compartidas": [{"columna": str(nombres[j]), "shap": round(float(imp_shap[j]), 4),
                             "perdida_de_concordancia": round(float(imp_perm[j]), 4),
                             "rango_shap": int(rango_shap[j]), "rango_permutacion": int(rango_perm[j])} for j in compartidas],
            "top15_shap": [str(nombres[j]) for j in np.argsort(-imp_shap)[:TOP]],
            "top15_permutacion": [str(nombres[j]) for j in np.argsort(-imp_perm)[:TOP]],
            "fraccion_de_la_atribucion_en_la_diana": {"shap": round(float(imp_shap[n_desc:].sum() / imp_shap.sum()), 4)},
            "tpsa_y_hbd": {n: {"rango_shap": int(rango_shap[list(nombres).index(n)]),
                               "rango_permutacion": int(rango_perm[list(nombres).index(n)])}
                           for n in ("TPSA", "NumHDonors")},
            "aviso_subestructuras": "el aft final no usa huellas: sus columnas son descriptores y dianas, no subestructuras"}
        pd.DataFrame({"columna": nombres, "shap": imp_shap, "perdida_de_concordancia": imp_perm,
                      "rango_shap": rango_shap, "rango_permutacion": rango_perm}).sort_values("rango_shap").to_csv(
            c.carpeta / "importancias.csv", index=False)
        c.metricas(resultado)
        for k, v in resultado.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
