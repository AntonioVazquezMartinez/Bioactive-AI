#!/usr/bin/env python3
"""E3 · los cuatro brazos del `aft`: descriptores, filtrados, solo huellas y descriptores + huellas.

La 2.13 eligió el `aft` con descriptores y diana. La corrida de Ingrid
(`2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura`) midió `aft_huellas` (descriptores, huellas y
diana). Faltaban dos de los cuatro brazos del plan: los **descriptores filtrados** (el filtro de la 03c y de
la 04c: casi constantes y redundantes, aprendido **dentro de cada pliegue**, con TPSA y HBD protegidos) y las
**huellas solas** con la diana (sin ningún descriptor). Aquí los cuatro corren juntos con los mismos pliegues y
semillas, para que la comparación sea pareada.

| brazo | qué ve el modelo |
|:--|:--|
| `aft` | 201 descriptores y la diana (el control: es el modelo de la 2.13) |
| `aft_filtrados` | los descriptores que sobreviven al filtro de cada pliegue, y la diana |
| `aft_huellas_diana` | 2,048 huellas Sort & Slice y la diana, **sin descriptores** |
| `aft_huellas` | 201 descriptores, 2,048 huellas y la diana (el control de Ingrid) |

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Controles: `aft` y `aft_huellas` reproducen la concordancia de la corrida de Ingrid en `todos` (0.7610 y
   0.7659) y en `solo_npass` (0.6322 y 0.6246) dentro de 0.003. Si no, hay un error y el resto no se lee.
2. **La métrica principal es la concordancia en `solo_npass`**, el estrato por el que la 2.13 eligió el modelo.
   Un brazo **supera** al `aft` ahí si su diferencia pareada media es positiva, mayor que su desviación pareada
   y positiva en al menos 12 de 15 evaluaciones. **Empeora** si es negativa, mayor en valor absoluto que su
   desviación y negativa en al menos 12 de 15. Cualquier otro caso es **empate dentro del ruido**.
3. En `todos` se reporta lo mismo, sin que decida: el agregado es 93% ChEMBL.
4. El `aft_filtro` (las 745 filas censuradas por la izquierda) y la sensibilidad de σ ya existen en las
   corridas de Ingrid y no se repiten aquí.
5. Una sola σ (1.0, la de siempre), una sola semilla del modelo, 15 evaluaciones. No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_aft_brazos.py
"""
from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "scripts"))

import numpy as np
import pandas as pd
from experimento_aft_huellas import DESCRIPTORES, N_BITS, PARES, PLIEGUES, SEMILLAS, datos
from sklearn.base import BaseEstimator

from src.features.huellas import AgregarHuellas
from src.features.seleccion import DepuracionDescriptores
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado, evaluar_baselines
from src.tracking import Corrida

N_DESC = 201
N_DIANA = 26
PROTEGIDAS_NOMBRES = ("TPSA", "NumHDonors")
REFERENCIA = {"todos": {"aft": 0.7610, "aft_huellas": 0.7659},
              "solo_npass": {"aft": 0.6322, "aft_huellas": 0.6246}}   # de: 2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura
TOLERANCIA = 0.003
REGLA_EVALUACIONES = 12


class FiltradosCensurado(BaseEstimator):
    """`DepuracionDescriptores` ajustado dentro del pliegue, para un modelo que recibe el intervalo.

    El filtro elige entre pares redundantes la columna que más se relaciona con el objetivo, y un intervalo no
    es un valor: se usa la mitad del intervalo cuando ambos extremos son finitos y el extremo finito si no.
    """

    def __init__(self, modelo, n_descriptores: int, protegidas: tuple[int, ...] = ()):
        self.modelo = modelo
        self.n_descriptores = n_descriptores
        self.protegidas = protegidas

    def fit(self, X, inferior, superior, grupos=None):
        inferior, superior = np.asarray(inferior, float), np.asarray(superior, float)
        y = np.where(np.isfinite(inferior) & np.isfinite(superior), (inferior + superior) / 2,
                     np.where(np.isfinite(inferior), inferior, superior))
        self.filtro_ = DepuracionDescriptores(self.n_descriptores, self.protegidas).fit(np.asarray(X, float), y)
        self.modelo.fit(self.filtro_.transform(np.asarray(X, float)), inferior, superior)
        return self

    def predict(self, X):
        return self.modelo.predict(self.filtro_.transform(np.asarray(X, float)))


class HuellasConDianaCensurado(BaseEstimator):
    """Las huellas del pliegue y la diana, **sin los descriptores** (`AgregarHuellas(densas=diana)`)."""

    def __init__(self, modelo, n_densas: int, densas: tuple[int, ...], n_bits: int = 2048):
        self.modelo = modelo
        self.n_densas = n_densas
        self.densas = densas
        self.n_bits = n_bits

    def fit(self, X, inferior, superior, grupos=None):
        self.huellas_ = AgregarHuellas(self.n_densas, densas=self.densas, n_bits=self.n_bits).fit(X)
        self.modelo.fit(self.huellas_.transform(X), inferior, superior)
        return self

    def predict(self, X):
        return self.modelo.predict(self.huellas_.transform(X))


def brazos(d: dict, protegidas: tuple[int, ...]) -> dict:
    n_dens = d["n_densas"]                      # descriptores + diana (227)
    diana = tuple(range(N_DESC, n_dens))
    assert n_dens == N_DESC + N_DIANA, "las columnas del 05b cambiaron"
    return {
        "aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
        "aft_filtrados": ("X", FiltradosCensurado(RegresionAFT(semilla=SEMILLAS[0]), N_DESC, protegidas)),
        "aft_huellas_diana": ("X_mixta", HuellasConDianaCensurado(RegresionAFT(semilla=SEMILLAS[0]), n_dens, diana, N_BITS)),
        "aft_huellas": ("X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]), n_dens, N_BITS)),
    }


def pareado(res: pd.DataFrame, estrato: str, metrica: str, contra: str = "aft") -> dict:
    sub = res[res["estrato"] == estrato]
    piv = sub.pivot_table(index=["semilla", "pliegue"], columns="modelo", values=metrica).dropna()
    salida = {"medias": {m: round(float(piv[m].mean()), 4) for m in piv.columns}}
    for m in piv.columns:
        if m == contra:
            continue
        dif = piv[m] - piv[contra]
        media, desv = float(dif.mean()), float(dif.std())
        pos, neg = int((dif > 0).sum()), int((dif < 0).sum())
        if media > 0 and media > desv and pos >= REGLA_EVALUACIONES:
            veredicto = "supera al aft"
        elif media < 0 and abs(media) > desv and neg >= REGLA_EVALUACIONES:
            veredicto = "empeora al aft"
        else:
            veredicto = "empate dentro del ruido"
        salida[m] = {"dif_media": round(media, 4), "dif_desv": round(desv, 4), "mejor_en": pos,
                     "peor_en": neg, "evaluaciones": int(len(dif)), "veredicto": veredicto}
    return salida


def main() -> None:
    d = datos()
    # columnas protegidas = TPSA y HBD dentro de los 201 descriptores (como en la 04c)
    desc_cols = [c for c in pd.read_parquet(DESCRIPTORES).columns if c != "smiles"]
    protegidas = tuple(desc_cols.index(c) for c in PROTEGIDAS_NOMBRES)
    assert len(desc_cols) == N_DESC
    params = {"brazos": ["aft", "aft_filtrados", "aft_huellas_diana", "aft_huellas"], "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "n_bits_sortslice": N_BITS, "n_descriptores": N_DESC, "n_diana": N_DIANA,
              "protegidas": list(PROTEGIDAS_NOMBRES), "filtro": "DepuracionDescriptores dentro del pliegue (0.99 modal, |Spearman| 0.95)",
              "metrica_principal": "concordancia en solo_npass, declarada antes de correr",
              "referencia_control": REFERENCIA, "tolerancia": TOLERANCIA, "regla_evaluaciones": REGLA_EVALUACIONES,
              "sigma": 1.0, "toca_prueba": False}
    with Corrida("brazos-aft-filtrados-y-huellas-solas", decision="2.13", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        partes = []
        for nombre, (matriz, modelo) in brazos(d, protegidas).items():
            t = time.perf_counter()
            r = evaluar_baselines(d[matriz], d["inferior"], d["superior"], d["grupos"], d["procedencia"], d["clase"],
                                  semillas=SEMILLAS, pliegues=PLIEGUES, modelos={nombre: modelo})
            partes.append(r)
            pd.concat(partes, ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
            print(f"  {nombre:20}{time.perf_counter() - t:6.0f} s", flush=True)
        res = pd.concat(partes, ignore_index=True)
        # cuántas columnas deja el filtro con todo el ajuste (informativo; el real es por pliegue)
        filtro = DepuracionDescriptores(N_DESC, protegidas).fit(
            d["X"].astype(float), np.where(np.isfinite(d["inferior"]), d["inferior"], d["superior"]))
        salida = {"concordancia": {e: pareado(res, e, "concordancia") for e in ("todos", "solo_chembl", "mixto", "solo_npass")},
                  "spearman_solo_npass": pareado(res, "solo_npass", "spearman"),
                  "auroc_solo_npass": pareado(res, "solo_npass", "auroc"),
                  "columnas_que_deja_el_filtro_con_todo_el_ajuste": int(len(filtro.descriptores_)),
                  "descriptores": N_DESC}
        control = {e: {m: abs(salida["concordancia"][e]["medias"][m] - REFERENCIA[e][m]) <= TOLERANCIA
                       for m in REFERENCIA[e]} for e in REFERENCIA}
        salida["control_dentro_de_tolerancia"] = control
        c.metricas(salida)
        print("\ncontrol:", control)
        for e in ("solo_npass", "todos"):
            print(f"\n== concordancia · {e}")
            for k, v in salida["concordancia"][e].items():
                print(f"  {k}: {v}")
        print("\nel filtro deja", salida["columnas_que_deja_el_filtro_con_todo_el_ajuste"], "de", N_DESC, "descriptores")


if __name__ == "__main__":
    main()
