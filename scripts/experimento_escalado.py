#!/usr/bin/env python3
"""Qué transformación conviene para los descriptores, medido con validación cruzada.

Evidencia de la decisión 1.5 del registro (`docs/decisiones.md`). Sustituye la
medición de una sola corrida que tenía la sección 8.2 del notebook 02, cuyo
orden entre Yeo-Johnson y min–max cambiaba según el sistema operativo: en macOS
min–max daba 0.497 de MCC contra 0.484, y en Linux 0.481 contra 0.484. Con una
sola partición de validación, la conclusión dependía de quién ejecutara.

Compara cuatro transformaciones —sin escalar, estandarización, min–max y
Yeo-Johnson— sobre los 206 descriptores (203 de RDKit utilizables más las tres
de dominio), con validación cruzada de 5 pliegues agrupada por andamio y
esqueleto de conectividad, repetida con 3 semillas, y los dos modelos que usaba
la sección 8.2 con sus mismos hiperparámetros.

Mide tres cosas, no una: el **desempeño**, el **tiempo de ajuste** y la
**convergencia misma** —iteraciones de `lbfgs` y si avisó de no haber convergido—,
más el número de condición de la matriz. El tiempo solo sería evidencia indirecta:
las iteraciones y el aviso son la prueba de lo que la rúbrica del Avance 2 pide al
escalar, «acelerar la convergencia de algunos algoritmos», y el número de
condición mide lo que la frase «mal condicionado» afirma.

**El C de la regresión logística se elige para cada transformación.** La versión
anterior usaba C = 1 con las cuatro, y la penalización L2 depende de la escala de cada
columna: al cambiar de escalador cambiaba también cuánto se regularizaba, y no se podía
saber si «min–max gana y Yeo-Johnson pierde» venía del escalador o de la penalización
(observación de la asesora sobre la §8.2). Ahora, dentro de cada pliegue de ajuste, una
validación cruzada interna agrupada de 3 pliegues elige C en {0.01, 0.1, 1, 10, 100}
por AUPRC sobre BBB− (salvo sin escalar, que no converge con ningún C y se queda en
C = 1: ver `modelos`). La fila «LogReg (C=1)» conserva la medición anterior para ver
cuánto de la diferencia venía de la regularización.

Dos cosas que hacen válida la comparación:

- **La transformación se reajusta dentro de cada pliegue.** Ajustarla sobre todo
  el entrenamiento y después partir filtraría la media y la varianza del pliegue
  de evaluación, que es el mismo error que el proyecto evita con el vocabulario
  de Sort & Slice y con el umbral de TPSA.
- **La prueba y la validación no se tocan.** Todo ocurre dentro de las 5,557
  filas de entrenamiento.

Salida: `notebooks/datos/resultados_escalado.csv`, que se versiona para que el
notebook lo lea sin volver a correr el experimento. Tarda unos 5 minutos.
"""
import platform
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MinMaxScaler, PowerTransformer, StandardScaler

from data_prep.splits import (andamio_murcko, esqueleto_conectividad, grupos_cv,
                              scaffold_split)
from features.molecular import a_mol, descriptores_rdkit, limpiar_descriptores
from tracking import Corrida

SEMILLAS = (0, 1, 2)
PLIEGUES = 5


def transformadores() -> dict:
    """Uno nuevo por pliegue: reutilizar un ajustado filtraría información."""
    return {"sin escalar": None,
            "estandarización": StandardScaler(),
            "min-max": MinMaxScaler(),
            "Yeo-Johnson": PowerTransformer(method="yeo-johnson", standardize=True)}


REJILLA_C = (0.01, 0.1, 1.0, 10.0, 100.0)
PLIEGUES_INTERNOS = 3


def elegir_c(Xa: np.ndarray, ya: np.ndarray, ga: np.ndarray, semilla: int) -> float:
    """El C de la logística para ESTA transformación, elegido dentro del pliegue de ajuste.

    La penalización L2 actúa sobre coeficientes cuya escala depende del escalador, así que
    comparar escaladores con el mismo C mezcla dos efectos: cambiar de escalador también
    cambia cuánto se regulariza. Con un C ajustado por escalador, la comparación es entre
    escaladores cada uno en su mejor regularización. El criterio es el AUPRC sobre BBB−,
    que no depende del corte, en una validación cruzada interna agrupada igual que la externa.
    """
    interna = StratifiedGroupKFold(n_splits=PLIEGUES_INTERNOS, shuffle=True, random_state=semilla)
    mejor, mejor_ap = REJILLA_C[0], -np.inf
    for C in REJILLA_C:
        aps = []
        for ia, ib in interna.split(Xa, ya, ga):
            m = LogisticRegression(C=C, max_iter=3000, random_state=semilla).fit(Xa[ia], ya[ia])
            aps.append(average_precision_score(1 - ya[ib], m.predict_proba(Xa[ib])[:, 0]))
        if np.mean(aps) > mejor_ap:
            mejor, mejor_ap = C, float(np.mean(aps))
    return mejor


SIN_ESCALAR = "sin escalar"


def modelos(semilla: int, C: float, transformacion: str) -> dict:
    """La logística con el C de su transformación, la de C = 1 fijo (la medición anterior,
    para ver cuánto venía de la regularización) y el bosque, que no tiene C.

    Sin escalar no se ajusta C: la logística no converge con ningún escalado ausente
    (agota sus 3,000 iteraciones, ~74 s por ajuste en Linux), así que esa fila ya se
    descarta de la comparación, y elegir C ahí costaba unas 5 horas sin cambiar nada de
    lo que se concluye. Queda con C = 1, como en la medición anterior, y por eso no lleva
    la fila duplicada «LogReg (C=1)».
    """
    m = {"LogReg": LogisticRegression(C=C, max_iter=3000, random_state=semilla)}
    if transformacion != SIN_ESCALAR:
        m["LogReg (C=1)"] = LogisticRegression(max_iter=3000, random_state=semilla)
    m["RF"] = RandomForestClassifier(n_estimators=200, random_state=semilla, n_jobs=-1)
    return m


def metricas(y: np.ndarray, puntuacion: np.ndarray) -> tuple[float, float, float]:
    """MCC, AUPRC sobre la clase minoritaria (BBB−) y AUROC.

    El AUPRC se invierte —`1 - y`, `1 - s`— porque la clase que importa es la
    minoritaria: medido sobre la mayoritaria, la línea base es más alta y los
    valores parecen mejores de lo que son.
    """
    return (matthews_corrcoef(y, (puntuacion >= 0.5).astype(int)),
            average_precision_score(1 - y, 1 - puntuacion),
            roc_auc_score(y, puntuacion))


def main() -> None:
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)

    b = pd.read_csv(RAIZ / "data/external/profesora/bbb_permeability_experimental.csv")
    b.columns = [c.strip().lstrip("﻿") for c in b.columns]
    b = b.rename(columns={"smiles_std": "SMILES", "bbb_class": "BBB+/BBB-"})
    b["mol"] = b["SMILES"].map(a_mol)
    d = b.dropna(subset=["mol", "BBB+/BBB-"]).reset_index(drop=True)
    d["y"] = (d["BBB+/BBB-"] == "BBB+").astype(int)
    d["andamio"] = [andamio_murcko(m) for m in d["mol"]]
    d["esqueleto"] = [esqueleto_conectividad(m) for m in d["mol"]]
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1,
                                    semilla=42, acíclicos_a="entrenamiento")
    print(d["particion"].value_counts().to_dict(), flush=True)

    # --- las mismas 206 columnas que mide la sección 8.2 -----------------------
    desc = descriptores_rdkit(list(d["mol"]))
    limpio, _ = limpiar_descriptores(desc, verbose=False)
    derivadas = pd.DataFrame(index=limpio.index)
    derivadas["regla_2p"] = ((limpio["TPSA"] < 67) & (limpio["NumHDonors"] <= 1)).astype(float)
    derivadas["tpsa_por_mw"] = limpio["TPSA"] / limpio["MolWt"]
    derivadas["lipo_neta"] = limpio["MolLogP"] - limpio["TPSA"] / 100
    X = pd.concat([limpio, derivadas], axis=1).values.astype(float)
    print(f"{X.shape[1]} columnas ({limpio.shape[1]} descriptores + 3 de dominio)", flush=True)

    y = d["y"].values
    g = grupos_cv(d)
    tr = np.where((d["particion"] == "entrenamiento").values)[0]
    va = np.where((d["particion"] == "validacion").values)[0]

    datos = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
    params = dict(transformaciones=list(transformadores()), pliegues=PLIEGUES,
                  columnas=int(X.shape[1]), rejilla_C=list(REJILLA_C),
                  pliegues_internos=PLIEGUES_INTERNOS, criterio_C="AUPRC sobre BBB−",
                  partición=dict(fraccion_prueba=0.2, fraccion_validacion=0.1, semilla=42,
                                 acíclicos_a="entrenamiento"),
                  modelos={"LogReg": "C elegido por transformación, max_iter=3000",
                           "LogReg (C=1)": "max_iter=3000", "RF": "n_estimators=200"})
    with Corrida("escalado", decision="1.5", params=params, semillas=list(SEMILLAS),
                 datos=[datos]) as c:
        filas = []
        for nombre in transformadores():
            t0 = time.time()
            for semilla in SEMILLAS:
                cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
                for k, (ia, ib) in enumerate(cv.split(tr, y[tr], g[tr])):
                    ajuste, evalua = tr[ia], tr[ib]
                    t = transformadores()[nombre]
                    if t is None:
                        Xa, Xb = X[ajuste], X[evalua]
                    else:
                        Xa = t.fit_transform(X[ajuste])   # reajustada en cada pliegue
                        Xb = t.transform(X[evalua])
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore", ConvergenceWarning)
                        C = 1.0 if nombre == SIN_ESCALAR else elegir_c(Xa, y[ajuste], g[ajuste], semilla)
                    for mod_n, mod in modelos(semilla, C, nombre).items():
                        t1 = time.perf_counter()
                        with warnings.catch_warnings(record=True) as avisos:
                            warnings.simplefilter("always", ConvergenceWarning)
                            mod.fit(Xa, y[ajuste])
                        ajuste_s = time.perf_counter() - t1
                        # `n_iter_` solo existe en los modelos iterativos; el bosque no itera
                        n_iter = int(np.ravel(mod.n_iter_)[0]) if hasattr(mod, "n_iter_") else None
                        sin_converger = any(issubclass(a.category, ConvergenceWarning)
                                            for a in avisos)
                        mcc, ap, au = metricas(y[evalua], mod.predict_proba(Xb)[:, 1])
                        filas.append(dict(transformacion=nombre, modelo=mod_n, seed=semilla,
                                          fold=k, MCC=mcc, AUPRC_neg=ap, AUROC=au,
                                          ajuste_s=ajuste_s, n_iter=n_iter,
                                          sin_converger=sin_converger, eval="cv",
                                          C=C if mod_n == "LogReg" else (1.0 if mod_n.startswith("LogReg") else None)))
            # la validación fija, para poder comparar con la medición anterior
            t = transformadores()[nombre]
            Xt, Xv = (X[tr], X[va]) if t is None else (t.fit_transform(X[tr]), t.transform(X[va]))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", ConvergenceWarning)
                C_val = 1.0 if nombre == SIN_ESCALAR else elegir_c(Xt, y[tr], g[tr], 42)
            for mod_n, mod in modelos(42, C_val, nombre).items():
                t1 = time.perf_counter()
                with warnings.catch_warnings(record=True) as avisos:
                    warnings.simplefilter("always", ConvergenceWarning)
                    mod.fit(Xt, y[tr])
                ajuste_s = time.perf_counter() - t1
                n_iter = int(np.ravel(mod.n_iter_)[0]) if hasattr(mod, "n_iter_") else None
                sin_converger = any(issubclass(a.category, ConvergenceWarning) for a in avisos)
                mcc, ap, au = metricas(y[va], mod.predict_proba(Xv)[:, 1])
                filas.append(dict(transformacion=nombre, modelo=mod_n, seed=42, fold=-1,
                                  MCC=mcc, AUPRC_neg=ap, AUROC=au, ajuste_s=ajuste_s,
                                  n_iter=n_iter, sin_converger=sin_converger, eval="val",
                                  C=C_val if mod_n == "LogReg" else (1.0 if mod_n.startswith("LogReg") else None)))
            # el número de condición es de la matriz, no del modelo: una fila por transformación
            filas.append(dict(transformacion=nombre, modelo="matriz", seed=42, fold=-1,
                              condicion=float(np.linalg.cond(Xt)), eval="cond"))
            print(f"{nombre} listo en {time.time()-t0:.0f}s", flush=True)

        salida = RAIZ / "notebooks/datos/resultados_escalado.csv"
        salida.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(filas).to_csv(salida, index=False)
        print("escrito", salida)

        cvd = pd.DataFrame(filas)
        cvd = cvd[cvd["eval"] == "cv"]
        lr = cvd[cvd["modelo"] == "LogReg"]
        c.metricas({"cv_media": {t: {m: {k: float(v)
                                         for k, v in g_[["MCC", "AUPRC_neg", "AUROC"]].mean().items()}
                                     for m, g_ in cvd[cvd.transformacion == t].groupby("modelo")}
                                 for t in transformadores()},
                    "C_elegido": {t: {str(k): int(v) for k, v in s["C"].value_counts().items()}
                                  for t, s in lr.groupby("transformacion")},
                    "convergencia": {t: {"iteraciones_mediana": float(s["n_iter"].median()),
                                         "sin_converger": int(s["sin_converger"].sum()),
                                         "ajuste_s_mediano": float(s["ajuste_s"].median())}
                                     for t, s in lr.groupby("transformacion")},
                    "filas_cv": int(len(cvd))})


if __name__ == "__main__":
    main()
