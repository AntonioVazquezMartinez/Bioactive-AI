#!/usr/bin/env python3
"""¿La similitud al vecino más cercano explica el nivel de la prueba reservada? (E14, fase 1)

La prueba reservada tiene una similitud media al vecino más cercano de 0.414, parecida a la del peldaño
de similitud ≥ 0.6 de la escalera (0.422), pero su AUROC (0.7928) es el de los peldaños de ≥ 0.5 y ≥ 0.4.
Si la similitud al vecino fuera lo que ordena la dificultad, la prueba rendiría como el peldaño de 0.6.
Aquí se pone a prueba si **la distribución completa** de esa similitud, y no su media, predice el AUROC.

**Cómo.** Se juntan las predicciones fuera de pliegue del `svm_rbf` en cuatro agrupamientos (el del
proyecto y similitud ≥ 0.6, 0.5 y 0.4; semillas 0, 1, 2), cada una con la similitud al vecino más cercano
de **su** parte de ajuste. Se **reponderan** esas predicciones para que su distribución de similitud sea la
de la prueba (cuantiles de la prueba como cubetas, pesos = fracción de la prueba / fracción de la
validación en cada cubeta) y se calcula el AUROC ponderado. Es una predicción: **se hace sin usar las
etiquetas de la prueba**, que solo se leen como SMILES, y se compara después con el 0.7928 ya registrado.

**Acceso a la prueba.** Es un acceso estructural de **solo SMILES**, sin etiquetas ni predicciones, anotado
en `experimentos/prueba.csv` por `tomar_prueba` con su motivo (como el de E1+).

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: sin reponderar, el AUROC de las predicciones juntas está entre el del peldaño de ≥ 0.4 (0.7798) y
   el del proyecto (0.9190). Si no, hay un error.
2. **La similitud al vecino explica el nivel de la prueba** si el AUROC reponderado queda a menos de **0.030**
   de 0.7928 (el doble de la dispersión de 0.015 que ha servido de vara en el proyecto). Si queda a más, la
   similitud al vecino **no basta** y lo que falta es otra cosa que esa medida no ve.
3. Se reporta además el mismo cálculo con el promedio de los cinco vecinos más cercanos, y se dice si
   cambia la conclusión.
4. Una sola familia de modelos (el `svm_rbf`) y una sola definición de parecido (ECFP4, ver E13).

    ./env312/bin/python scripts/experimento_dificultad_de_la_prueba.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from src.features.similitud import (bits_como_matriz, grupos_por_similitud, huellas, matriz_densa,
                                    similitud_al_vecino_matricial)
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida, tomar_prueba

SEMILLAS = (0, 1, 2)
UMBRALES = (0.6, 0.5, 0.4)
AUROC_PRUEBA = 0.7928          # de: 2026-11-01-artemio-1.5-modelo-final-permeabilidad
LIMITE_CONTROL = (0.7798, 0.9190)
TOLERANCIA = 0.030
CUBETAS = 10
K = 5


def similitud_k(A, ajuste, validacion, k):
    """Promedio de las k mayores similitudes de cada compuesto de validación al ajuste (matriz de bits)."""
    cuenta = A.sum(axis=1)
    out = np.empty(len(validacion), dtype=np.float32)
    A_aj, c_aj = A[ajuste], cuenta[ajuste]
    for i in range(0, len(validacion), 256):
        v = validacion[i:i + 256]
        inter = A[v] @ A_aj.T
        sim = inter / np.maximum(cuenta[v][:, None] + c_aj[None, :] - inter, 1e-9)
        out[i:i + 256] = np.sort(sim, axis=1)[:, -k:].mean(axis=1)
    return out


def agrupamientos(t, S) -> dict:
    d = {"4 andamio + esqueleto (actual)": t.grupos}
    for u in UMBRALES:
        d[f"5 similitud ≥ {u}"] = grupos_por_similitud(S, u)
    return d


def reponderado(y, p, sim, sim_prueba) -> float:
    """AUROC ponderado para que `sim` tenga la distribución de `sim_prueba` (cubetas por cuantiles)."""
    bordes = np.quantile(sim_prueba, np.linspace(0, 1, CUBETAS + 1))
    bordes[0], bordes[-1] = -np.inf, np.inf
    cub_val = np.clip(np.digitize(sim, bordes[1:-1]), 0, CUBETAS - 1)
    frac_prueba = np.full(CUBETAS, 1 / CUBETAS)          # cuantiles de la prueba: cada cubeta pesa lo mismo
    frac_val = np.bincount(cub_val, minlength=CUBETAS) / len(sim)
    w = np.where(frac_val[cub_val] > 0, frac_prueba[cub_val] / np.maximum(frac_val[cub_val], 1e-12), 0.0)
    return float(roc_auc_score(y, p, sample_weight=w))


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    smiles = t.meta["SMILES"].tolist()
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelo": "svm_rbf", "semillas": list(SEMILLAS), "agrupamientos": ["actual", *map(str, UMBRALES)],
              "cubetas": CUBETAS, "k_vecinos": K, "auroc_prueba_registrado": AUROC_PRUEBA,
              "tolerancia": TOLERANCIA, "filas": int(len(t.y)),
              "toca_prueba": "solo SMILES, sin etiquetas ni predicciones (acceso estructural)"}
    with Corrida("dificultad-de-la-prueba-permeabilidad", decision="1.5", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        fps = huellas(smiles)
        A = bits_como_matriz(fps)
        S = matriz_densa(fps)
        modelo = seleccion(("svm_rbf",))["svm_rbf"]
        y_todo, p_todo, s1_todo, sk_todo = [], [], [], []
        for nombre, g in agrupamientos(t, S).items():
            for semilla in SEMILLAS:
                for aj, val in StratifiedGroupKFold(5, shuffle=True, random_state=semilla).split(t.X, t.y, g):
                    m = clone(modelo).fit(t.X[aj], t.y[aj])
                    y_todo.append(t.y[val])
                    p_todo.append(m.predict_proba(t.X[val])[:, 1])
                    s1_todo.append(similitud_al_vecino_matricial(A, aj, val))
                    sk_todo.append(similitud_k(A, aj, val, K))
            print(f"  {nombre} listo", flush=True)
        y, p = np.concatenate(y_todo), np.concatenate(p_todo)
        s1, sk = np.concatenate(s1_todo), np.concatenate(sk_todo)
        auroc_sin_ponderar = float(roc_auc_score(y, p))

        # Acceso estructural a la prueba: solo SMILES.
        bbb = pd.read_parquet(PROCESADOS / "bbb_meta.parquet")
        prueba = tomar_prueba(bbb, final=True,
                              motivo="E14: distribución de la similitud de la prueba con el ajuste, solo SMILES, "
                                     "sin etiquetas ni predicciones")
        A_p = bits_como_matriz(huellas(prueba["SMILES"].tolist()))
        A_all = np.vstack([A, A_p])
        idx_aj = np.arange(len(A))
        idx_pr = np.arange(len(A), len(A_all))
        s1_prueba = similitud_al_vecino_matricial(A_all, idx_aj, idx_pr)
        sk_prueba = similitud_k(A_all, idx_aj, idx_pr, K)

        r1 = reponderado(y, p, s1, s1_prueba)
        rk = reponderado(y, p, sk, sk_prueba)
        control = bool(LIMITE_CONTROL[0] <= auroc_sin_ponderar <= LIMITE_CONTROL[1])
        explica = bool(abs(r1 - AUROC_PRUEBA) < TOLERANCIA)
        explica_k = bool(abs(rk - AUROC_PRUEBA) < TOLERANCIA)
        resultado = {
            "auroc_sin_ponderar": round(auroc_sin_ponderar, 4), "control_en_rango": control,
            "auroc_reponderado_vecino_1": round(r1, 4), "auroc_reponderado_vecino_k5": round(rk, 4),
            "auroc_prueba_registrado": AUROC_PRUEBA,
            "diferencia_vecino_1": round(r1 - AUROC_PRUEBA, 4), "diferencia_vecino_k5": round(rk - AUROC_PRUEBA, 4),
            "la_similitud_explica_el_nivel": explica, "la_conclusion_con_k5_es_la_misma": explica == explica_k,
            "similitud_validacion_media": round(float(s1.mean()), 4), "similitud_prueba_media": round(float(s1_prueba.mean()), 4),
            "cuantiles_prueba_vecino_1": [round(float(q), 4) for q in np.quantile(s1_prueba, [0.05, 0.25, 0.5, 0.75, 0.95])],
            "cuantiles_validacion_vecino_1": [round(float(q), 4) for q in np.quantile(s1, [0.05, 0.25, 0.5, 0.75, 0.95])],
            "n_prueba": int(len(s1_prueba)), "n_predicciones": int(len(y))}
        c.metricas(resultado)
        for k, v in resultado.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
