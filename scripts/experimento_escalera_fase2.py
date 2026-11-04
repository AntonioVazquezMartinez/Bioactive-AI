#!/usr/bin/env python3
"""¿La escalera de semejanza existe también en la fase 2? (E12)

La escalera de la fase 1 (corrida `2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`) mostró que
cuánta semejanza se permite entre entrenamiento y validación mueve el resultado más que elegir el
modelo. Falta saber si es de la fase 1 o general. Aquí el `aft`, modelo final de la fase 2, se evalúa con
los mismos peldaños, cambiando solo cómo se parten los pliegues.

**Peldaños.** (1) por **par** al azar, (2) por **molécula** (una molécula con varias dianas queda entera
de un lado), (3) `grupo_cv`, el del proyecto, y (4–6) por similitud: componentes conexas de Tanimoto
(Morgan radio 2, 2048 bits) ≥ 0.6, 0.5 y 0.4 sobre las moléculas únicas del ajuste. Un grupo con más del
20% de las filas deja sin sentido la partición en cinco pliegues y ese peldaño se marca no evaluable,
como en la fase 1. Se mide además qué tan parecida es la validación al ajuste: similitud media al vecino
más cercano, sobre 1,500 filas de validación por pliegue de la semilla 0.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: el peldaño 3 reproduce la concordancia del `aft` de la 2.13 (0.7610) dentro de 0.003.
2. La escalera **existe en la fase 2** si la concordancia en `todos` del peldaño evaluable más estricto
   cae al menos **0.030** por debajo de la del peldaño 2 (por molécula). 0.030 es el doble de la
   dispersión entre los siete modelos competitivos de la 2.13 (0.750 a 0.765, es decir 0.015), la vara que
   usa el artículo. Si cae menos, la fase 2 es **menos sensible** y se reporta así. Si un peldaño no es
   evaluable, se usa el más estricto que sí lo sea, y se dice cuál.
3. Una sola familia de modelos (el `aft`); lo que se concluya vale para ella.
4. Se reporta también `solo_npass`, pero la regla se aplica a `todos`.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_escalera_fase2.py
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
from sklearn.model_selection import StratifiedGroupKFold

from src.features.similitud import (bits_como_matriz, grupos_por_similitud, huellas, matriz_dispersa,
                                    resumen_grupos, similitud_al_vecino_matricial)
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import evaluar_baselines
from src.tracking import Corrida

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
SEMILLAS = (0, 1, 2)
PLIEGUES = 5
UMBRALES = (0.6, 0.5, 0.4)
MAX_GRUPO = 0.20
MUESTRA_VECINO = 1_500
REFERENCIA = 0.7610          # de: 2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura
TOLERANCIA = 0.003
CAIDA_MINIMA = 0.030


def datos() -> dict:
    """Las mismas 56,241 filas y columnas que el 05b, con el SMILES de cada fila."""
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
    assert fuera.sum() == 56_241, "las filas de ajuste cambiaron respecto al 05b"
    return {"X": X[fuera], "inferior": inferior[fuera], "superior": superior[fuera],
            "grupos": d["grupo_cv"].to_numpy()[fuera], "procedencia": d["estrato"].to_numpy()[fuera],
            "clase": d["activo_10um"].to_numpy(float)[fuera], "smiles": d["smiles"].to_numpy()[fuera]}


def peldanos(d: dict, mol: np.ndarray, componentes: dict) -> dict:
    n = len(mol)
    salida = {"1 par al azar": np.arange(n), "2 por molécula": mol, "3 grupo_cv (el del proyecto)": d["grupos"]}
    for u in UMBRALES:
        salida[f"4 similitud ≥ {u}"] = componentes[u][mol]
    return salida


def vecino(A: np.ndarray, mol: np.ndarray, estratificar: np.ndarray, grupos: np.ndarray, semilla: int = 0) -> float:
    """Similitud media al vecino más cercano de ajuste, con 1,500 filas de validación por pliegue."""
    rng = np.random.default_rng(0)
    cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=semilla)
    valores = []
    for ajuste, val in cv.split(np.zeros(len(mol)), estratificar, grupos):
        ajuste_mol = np.unique(mol[ajuste])
        muestra = rng.choice(val, size=min(MUESTRA_VECINO, len(val)), replace=False)
        valores.append(similitud_al_vecino_matricial(A, ajuste_mol, mol[muestra]))
    return float(np.concatenate(valores).mean())


def main() -> None:
    d = datos()
    unicos, mol = np.unique(d["smiles"], return_inverse=True)
    print(f"{len(d['smiles']):,} filas · {len(unicos):,} moléculas únicas", flush=True)
    t = time.perf_counter()
    fps = huellas(unicos.tolist())
    A = bits_como_matriz(fps)
    S = matriz_dispersa(fps, min(UMBRALES))
    componentes = {u: grupos_por_similitud(S, u) for u in UMBRALES}
    print(f"similitud: {S.nnz // 2:,} pares ≥ {min(UMBRALES)} en {time.perf_counter() - t:.0f} s", flush=True)
    estratificar = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    params = {"peldanos": ["par al azar", "por molécula", "grupo_cv", *[f"similitud >= {u}" for u in UMBRALES]],
              "semillas": list(SEMILLAS), "pliegues": PLIEGUES, "modelo": "aft", "grupo_maximo": MAX_GRUPO,
              "referencia_control": REFERENCIA, "tolerancia": TOLERANCIA, "caida_minima": CAIDA_MINIMA,
              "muestra_vecino": MUESTRA_VECINO, "moleculas_unicas": int(len(unicos)), "toca_prueba": False}
    with Corrida("escalera-agrupacion-actividad", decision="1.2", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        filas = []
        for nombre, g in peldanos(d, mol, componentes).items():
            g = np.asarray(g)
            fila = {"peldano": nombre, **resumen_grupos(g)}
            if fila["mayor_grupo_pct"] > 100 * MAX_GRUPO:
                fila["nota"] = "no evaluable: un grupo pasa del 20% de las filas"
                filas.append(fila)
                print(fila, flush=True)
                continue
            t = time.perf_counter()
            r = evaluar_baselines(d["X"], d["inferior"], d["superior"], g, d["procedencia"], d["clase"],
                                  semillas=SEMILLAS, pliegues=PLIEGUES,
                                  modelos={"aft": RegresionAFT(semilla=SEMILLAS[0])})
            print(f"  {nombre}: aft evaluado en {time.perf_counter() - t:.0f} s", flush=True)
            for estrato in ("todos", "solo_npass"):
                sub = r[r["estrato"] == estrato]
                if len(sub):
                    fila[f"concordancia_{estrato}"] = round(float(sub["concordancia"].mean()), 4)
            fila["vecino_mas_cercano"] = round(vecino(A, mol, estratificar, g), 4)
            filas.append(fila)
            print(fila, f"{time.perf_counter() - t:.0f} s", flush=True)
            pd.DataFrame(filas).to_csv(c.carpeta / "escalera.csv", index=False)
        tabla = pd.DataFrame(filas)
        evaluables = tabla.dropna(subset=["concordancia_todos"])
        actual = float(evaluables[evaluables["peldano"].str.startswith("3")]["concordancia_todos"].iloc[0])
        molecula = float(evaluables[evaluables["peldano"].str.startswith("2")]["concordancia_todos"].iloc[0])
        mas_estricto = evaluables.iloc[-1]
        caida = molecula - float(mas_estricto["concordancia_todos"])
        existe = bool(caida >= CAIDA_MINIMA)
        c.metricas({"escalera": tabla.where(tabla.notna(), None).to_dict("records"),
                    "control_actual": {"obtenido": actual, "referencia": REFERENCIA,
                                       "dentro_de_tolerancia": abs(actual - REFERENCIA) <= TOLERANCIA},
                    "peldano_mas_estricto_evaluable": mas_estricto["peldano"],
                    "caida_desde_por_molecula": round(caida, 4), "la_escalera_existe": existe})
        print(f"\ncontrol: {actual} (ref {REFERENCIA})\nmás estricto evaluable: {mas_estricto['peldano']}\n"
              f"caída desde 'por molécula': {caida:.4f} → la escalera {'existe' if existe else 'es menor'}")


if __name__ == "__main__":
    main()
