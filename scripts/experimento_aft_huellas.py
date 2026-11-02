"""El `aft` con huellas, sin ellas, sin censura y con el filtro corregido: cuatro brazos.

Cierra tres preguntas que la corrida de la [2.13](../docs/decisiones.md#d2-13) dejó abiertas,
y las cierra en una sola corrida porque las cuatro comparten pliegues, semillas y matriz:

| Brazo | Qué aísla |
|:--|:--|
| `aft` | el control: es el modelo que eligió la 2.13, tal cual |
| `aft_huellas` | lo que aportan las huellas Sort & Slice, que la [1.3](../docs/decisiones.md#d1-3) decidió para la fase 2 y el modelo final no tiene |
| `xgb_sin_censura` | si el mérito es de la pérdida censurada o de XGBoost: mismos árboles, misma profundidad, `reg:squarederror` y solo las exactas |
| `aft_filtro` | lo que valen las 745 filas censuradas por la izquierda que el filtro por omisión descarta |

Sin el tercer brazo, un `aft` que gana no distingue las dos cosas: ve más filas *y* usa otra
librería. Es el mismo razonamiento con el que `src/models/baseline_regresion.py` justifica
`ridge_cota_imputada` entre `ridge_exactas` y el Tobit.

La métrica principal queda declarada aquí, antes de ver el resultado: **la concordancia de
Harrell en `solo_npass`**, que es el estrato por el que la 2.13 eligió este modelo.

    ./env/bin/python scripts/experimento_aft_huellas.py
"""
from __future__ import annotations

import math
import os

os.environ["OMP_NUM_THREADS"] = "1"   # un hilo por proceso: no competir con n_jobs=-1

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse
from xgboost import XGBRegressor

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.features.huellas import agrupar_iguales, identificadores_morgan          # noqa: E402
from src.models.aft import AftConCensuraIzquierda, RegresionAFT                    # noqa: E402
from src.models.baseline_regresion import (ConHuellasCensurado, SoloExactas,      # noqa: E402
                                           evaluar_baselines)
from src.tracking import Corrida                                                  # noqa: E402

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
SEMILLAS = [0, 1, 2]
PLIEGUES = 5
N_BITS = 2048
ESTRATOS = ("todos", "solo_chembl", "mixto", "solo_npass")
METRICAS = ("concordancia", "spearman", "rmse", "rmse_entrenamiento", "mcc", "auroc", "seg")


def datos():
    """Las mismas filas y columnas que el cuaderno 05b, con sus dos aserciones."""
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [c for c in desc.columns if c != "smiles"]

    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)
    d = d[util].reset_index(drop=True)
    inferior, superior = inferior[util], superior[util]
    es_prueba = (d["particion"] == "prueba").to_numpy()

    diana = pd.get_dummies(d["target_gene"])
    X = np.hstack([d[cols].to_numpy("float32"), diana.to_numpy("float32")])
    exacta = inferior == superior
    assert (~es_prueba).sum() == 56_241, "las filas de ajuste cambiaron respecto al 05b"
    assert exacta[~es_prueba].sum() == 46_100, "las exactas de ajuste cambiaron"

    t = time.perf_counter()
    huellas, identificadores = identificadores_morgan(d["smiles"])
    huellas, identificadores, _ = agrupar_iguales(huellas, identificadores)
    # Sobre el conjunto completo, para que una columna signifique lo mismo en ajuste y prueba.
    X_mixta = sparse.hstack([sparse.csr_matrix(X), huellas]).tocsr()
    print(f"huellas: {huellas.shape[1]:,} columnas en {time.perf_counter() - t:.0f} s "
          f"· X_mixta {X_mixta.shape}", flush=True)

    fuera = ~es_prueba
    return {"X": X[fuera], "X_mixta": X_mixta[fuera], "n_densas": X.shape[1],
            "inferior": inferior[fuera], "superior": superior[fuera],
            "grupos": d["grupo_cv"].to_numpy()[fuera],
            "procedencia": d["estrato"].to_numpy()[fuera],
            "clase": d["activo_10um"].to_numpy(float)[fuera]}


# σ de la pérdida AFT, en unidades de ln(µM). El docstring de `src/models/aft.py` justifica
# el 1.0 por omisión como «comparable» a la dispersión de ~0.7 que ChEMBL reporta — pero ese
# 0.7 está en pActividad, que es log10, y σ vive en ln. El factor es ln(10) = 2.3026, así que
# el 1.0 supone las mediciones 1.6 veces más precisas de lo que su propia justificación cita.
# σ gobierna cuánta información lleva un intervalo censurado, y la ventaja del `aft` en los
# naturales viene entera de la censura, así que el supuesto manda sobre el mecanismo.
ESCALA_EQUIVALENTE = 0.7 * math.log(10)      # 1.6118 en ln(µM) = 0.7 en pActividad


def brazos_escala() -> dict:
    """El `aft` con la σ que su propia justificación implica, contra el `aft` tal cual."""
    return {
        "aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
        "aft_escala_equivalente": ("X", RegresionAFT(semilla=SEMILLAS[0],
                                                     escala=ESCALA_EQUIVALENTE)),
    }


def brazos(n_densas: int) -> dict:
    """Los cuatro, con los mismos árboles y la misma profundidad: 100 rondas, profundidad 6."""
    return {
        "aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
        "aft_huellas": ("X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]),
                                                       n_densas, N_BITS)),
        "xgb_sin_censura": ("X", SoloExactas(XGBRegressor(
            n_estimators=100, max_depth=6, tree_method="hist",
            random_state=SEMILLAS[0], n_jobs=-1))),
        "aft_filtro": ("X", AftConCensuraIzquierda(semilla=SEMILLAS[0])),
    }


def resumen(res: pd.DataFrame) -> dict:
    """Medias por estrato y, contra el control, la diferencia pareada y los pliegues ganados."""
    salida: dict = {}
    for estrato in ESTRATOS:
        sub = res[res["estrato"] == estrato]
        if sub.empty:
            continue
        salida[estrato] = {
            modelo: {m: round(float(filas[m].mean()), 4) for m in METRICAS if m in filas}
            for modelo, filas in sub.groupby("modelo")
        }
        piv = sub.pivot_table(index=["semilla", "pliegue"], columns="modelo",
                              values="concordancia")
        if "aft" not in piv:
            continue
        pareado = {}
        for modelo in piv.columns:
            if modelo == "aft":
                continue
            par = piv[["aft", modelo]].dropna()
            dif = par[modelo] - par["aft"]
            pareado[modelo] = {"dif_media": round(float(dif.mean()), 4),
                               "dif_desv": round(float(dif.std()), 4),
                               "mejor_en": int((dif > 0).sum()),
                               "evaluaciones": int(len(par))}
        salida[estrato]["contra_aft"] = pareado
    return salida


def main() -> None:
    solo_escala = "--solo-escala" in sys.argv
    d = datos()
    catalogo = brazos_escala() if solo_escala else brazos(d["n_densas"])
    params = {
        "modelos": list(catalogo), "pliegues": PLIEGUES, "n_bits_sortslice": N_BITS,
        "radio_morgan": 2, "objetivo": "pActividad", "estratos": "procedencia",
        "metrica_principal": "concordancia en solo_npass, declarada antes de correr",
        "solo_escala": solo_escala,
        "entrena_con": {"aft": "todas las censuradas por la derecha",
                        "aft_huellas": "idem, con las huellas dentro del pliegue",
                        "xgb_sin_censura": "solo las exactas (SoloExactas)",
                        "aft_filtro": "también las censuradas por la izquierda"},
        "arboles": "100 rondas, profundidad 6, todos los brazos",
        "escala_aft": {"aft": 1.0, "aft_escala_equivalente": round(ESCALA_EQUIVALENTE, 4)}
                      if solo_escala else 1.0,
        "nota_seg": "tiempo de ajuste con dieciséis núcleos; no comparable con la corrida "
                    "de la 2.13, que corrió en otra máquina",
    }
    nombre = "sensibilidad-escala-aft" if solo_escala else "comparativa-aft-huellas-y-censura"
    with Corrida(nombre, decision="2.13", params=params,
                 semillas=SEMILLAS, datos=[PARES, DESCRIPTORES]) as c:
        partes = []
        for nombre, (matriz, modelo) in catalogo.items():
            t = time.perf_counter()
            r = evaluar_baselines(d[matriz], d["inferior"], d["superior"], d["grupos"],
                                  d["procedencia"], d["clase"], semillas=SEMILLAS,
                                  pliegues=PLIEGUES, modelos={nombre: modelo})
            partes.append(r)
            pd.concat(partes, ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
            print(f"{nombre:18}{time.perf_counter() - t:7.0f} s", flush=True)
        res = pd.concat(partes, ignore_index=True)
        c.metricas(resumen(res))
    print(f"\ncorrida: experimentos/{c.id}", flush=True)
    for estrato in ESTRATOS:
        sub = res[res["estrato"] == estrato]
        if sub.empty:
            continue
        print(f"\n=== {estrato}")
        print(sub.groupby("modelo")[["concordancia", "spearman", "rmse", "mcc", "auroc"]]
              .mean().round(4).to_string())


if __name__ == "__main__":
    main()
