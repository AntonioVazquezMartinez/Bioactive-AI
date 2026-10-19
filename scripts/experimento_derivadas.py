#!/usr/bin/env python3
"""¿Las tres características derivadas mejoran el modelo, o solo se justifican en papel?

Evidencia de la decisión 1.5 (`docs/decisiones.md`). La sección 6 del notebook 02
las conservaba por su AUC individual y por su correlación con los descriptores
base, que es la única decisión de inclusión de ese notebook que no se medía con
el modelo. Aquí se mide: el mismo modelo con y sin ellas, con la misma
validación cruzada agrupada.

Cinco conjuntos de columnas: los 203 descriptores de RDKit solos; con las tres
derivadas; y con cada una por separado, para ver cuál aporta si alguna lo hace.
Dos modelos, los de la sección 8.2: regresión logística con min-max y con el `C`
que ella elige dentro de cada pliegue (el `C` fijo castiga distinto según la
escala; ver `experimento_escalado.py`), y Random Forest.

La validación cruzada es de 5 pliegues agrupada por andamio y esqueleto, repetida
con 3 semillas, solo sobre entrenamiento; la prueba y la validación no se tocan.
La diferencia contra «sin derivadas» se toma pareada por pliegue y su error
estándar se corrige como proponen Nadeau y Bengio (2003), porque las 15
evaluaciones comparten datos.

Salida: `notebooks/datos/resultados_derivadas.csv`. Tarda unos 10 minutos.
"""
import platform
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts"))

import numpy as np
import pandas as pd
from experimento_escalado import PLIEGUES, SEMILLAS, elegir_c, metricas
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MinMaxScaler

from data_prep.splits import (andamio_murcko, esqueleto_conectividad, grupos_cv,
                              scaffold_split)
from features.molecular import a_mol, descriptores_rdkit, limpiar_descriptores
from tracking import Corrida

DERIVADAS = ["regla_2p", "tpsa_por_mw", "lipo_neta"]
CONJUNTOS = {"sin derivadas": [], "las tres": DERIVADAS,
             "solo regla_2p": ["regla_2p"], "solo tpsa_por_mw": ["tpsa_por_mw"],
             "solo lipo_neta": ["lipo_neta"]}


def main() -> None:
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    datos = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
    b = pd.read_csv(datos)
    b.columns = [c.strip().lstrip("﻿") for c in b.columns]
    b = b.rename(columns={"smiles_std": "SMILES", "bbb_class": "BBB+/BBB-"})
    b["mol"] = b["SMILES"].map(a_mol)
    d = b.dropna(subset=["mol", "BBB+/BBB-"]).reset_index(drop=True)
    d["y"] = (d["BBB+/BBB-"] == "BBB+").astype(int)
    d["andamio"] = [andamio_murcko(m) for m in d["mol"]]
    d["esqueleto"] = [esqueleto_conectividad(m) for m in d["mol"]]
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1,
                                    semilla=42, acíclicos_a="entrenamiento")

    limpio, _ = limpiar_descriptores(descriptores_rdkit(list(d["mol"])), verbose=False)
    todas = limpio.copy()
    todas["regla_2p"] = ((limpio["TPSA"] < 67) & (limpio["NumHDonors"] <= 1)).astype(float)
    todas["tpsa_por_mw"] = limpio["TPSA"] / limpio["MolWt"]
    todas["lipo_neta"] = limpio["MolLogP"] - limpio["TPSA"] / 100
    base = list(limpio.columns)
    print(f"{len(base)} descriptores base + {len(DERIVADAS)} derivadas", flush=True)

    y = d["y"].values
    g = grupos_cv(d)
    tr = np.where((d["particion"] == "entrenamiento").values)[0]

    params = dict(conjuntos={k: v for k, v in CONJUNTOS.items()}, pliegues=PLIEGUES,
                  columnas_base=len(base),
                  modelos=dict(LogReg="min-max + C elegido por CV interna",
                               RF="n_estimators=200"))
    with Corrida("derivadas", decision="1.5", params=params, semillas=list(SEMILLAS),
                 datos=[datos]) as c:
        filas = []
        for semilla in SEMILLAS:
            cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
            for k, (ia, ib) in enumerate(cv.split(tr, y[tr], g[tr])):
                ajuste, evalua = tr[ia], tr[ib]
                for nombre, extra in CONJUNTOS.items():
                    X = todas[base + extra].values.astype(float)
                    esc = MinMaxScaler().fit(X[ajuste])
                    Xa, Xb = esc.transform(X[ajuste]), esc.transform(X[evalua])
                    c_ = elegir_c(Xa, y[ajuste], g[ajuste], semilla)
                    lr = LogisticRegression(C=c_, max_iter=3000, random_state=semilla)
                    rf = RandomForestClassifier(n_estimators=200, random_state=semilla,
                                                n_jobs=-1)
                    for mod_n, mod, A, B in (("LogReg", lr, Xa, Xb),
                                             ("RF", rf, X[ajuste], X[evalua])):
                        mod.fit(A, y[ajuste])
                        mcc, ap, au = metricas(y[evalua], mod.predict_proba(B)[:, 1])
                        filas.append(dict(conjunto=nombre, modelo=mod_n, seed=semilla,
                                          fold=k, columnas=X.shape[1], MCC=mcc,
                                          AUPRC_neg=ap, AUROC=au))
            print(f"semilla {semilla} lista", flush=True)

        res = pd.DataFrame(filas)
        salida = RAIZ / "notebooks/datos/resultados_derivadas.csv"
        salida.parent.mkdir(parents=True, exist_ok=True)
        res.to_csv(salida, index=False)
        print("escrito", salida)

        # diferencia contra «sin derivadas», pareada por pliegue
        out = {}
        for mod, sub in res.groupby("modelo"):
            for met in ("MCC", "AUPRC_neg", "AUROC"):
                p = sub.pivot_table(index=["seed", "fold"], columns="conjunto", values=met)
                n = len(p)
                t95 = stats.t.ppf(0.975, n - 1)
                for conj in CONJUNTOS:
                    if conj == "sin derivadas":
                        continue
                    dif = p[conj] - p["sin derivadas"]
                    ee = dif.std() * np.sqrt(1 / n + 0.25)
                    out[f"{mod}|{met}|{conj}"] = dict(
                        dif=float(dif.mean()), ee=float(ee),
                        ic_inf=float(dif.mean() - t95 * ee), ic_sup=float(dif.mean() + t95 * ee))
        c.metricas({"medias": {f"{m}|{cj}": {k: float(v) for k, v in s[["MCC", "AUPRC_neg", "AUROC"]].mean().items()}
                               for (m, cj), s in res.groupby(["modelo", "conjunto"])},
                    "diferencias_contra_sin_derivadas": out})


if __name__ == "__main__":
    main()
