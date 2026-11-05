#!/usr/bin/env python3
"""E5 · métricas de ranking de la C.5 para el `aft` de la fase 2 (#132).

Calcula, con predicciones **fuera de pliegue** del modelo final de la fase 2, lo que la C.5 pide y
nadie calculaba: enriquecimiento al 1% y al 5%, BEDROC y precisión en los primeros 100. Todo por
procedencia, porque un agregado no describe a los naturales.

**Lo que se declara antes de correr.**
- Se ordenan los pares por la potencia predicha (mayor = más potente). «Activo» es la etiqueta a
  10 µM (`activo_10um`); los pares cuyo intervalo no decide la etiqueta se excluyen del ranking.
- Enriquecimiento = (activos en el primer k% / tamaño del k%) / tasa de activos del estrato. **Va
  siempre con la tasa base y la cuenta de activos recuperados**, porque un enriquecimiento sin
  ellas no se puede leer (el 1.92× que resultó ser un compuesto).
- BEDROC con α = 20 (≈ 80% del peso en el primer 8% de la lista). Se declara; no se ajusta.
- Intervalo del 95% por bootstrap de **grupos** (`grupo_cv`), 300 remuestras.
- Dos controles: ordenar al azar (esperanza: enriquecimiento 1) y ordenar solo por la potencia
  media de la diana en el ajuste, que dice cuánto del ranking es saber *qué diana* y no *qué
  molécula*.
- Una sola semilla de partición (0), 5 pliegues, las mismas filas que el 05b. No toca la prueba.
- **No se reporta AUPRC por estrato** (#187): promedia dos clases distintas.

    ./env/bin/python scripts/experimento_ranking_fase2.py
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
from rdkit.ML.Scoring.Scoring import CalcBEDROC
from sklearn.model_selection import StratifiedGroupKFold

from src.models.aft import RegresionAFT
from src.tracking import Corrida

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
ALFA = 20.0
REMUESTRAS = 300
ESTRATOS = ("todos", "solo_chembl", "mixto", "solo_npass")


def datos():
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
            "grupos": d["grupo_cv"].to_numpy()[fuera], "estrato": d["estrato"].to_numpy()[fuera],
            "clase": d["activo_10um"].to_numpy(float)[fuera],
            "diana": d["target_gene"].to_numpy()[fuera]}


def fuera_de_pliegue(d, semilla=0, pliegues=5):
    """Predicción del `aft` y de los dos controles para cada par, siempre fuera de pliegue."""
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    cv = StratifiedGroupKFold(pliegues, shuffle=True, random_state=semilla)
    aft = np.zeros(len(clase))
    diana = np.zeros(len(clase))
    media_pact = (d["inferior"] + d["superior"]) / 2   # solo para el control; los infinitos se limitan
    media_pact = np.where(np.isfinite(media_pact), media_pact, np.nan)
    for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
        m = RegresionAFT(semilla=semilla)
        m.fit(d["X"][aj], d["inferior"][aj], d["superior"][aj])
        aft[val] = m.predict(d["X"][val])
        medias = pd.Series(media_pact[aj]).groupby(d["diana"][aj]).mean()
        diana[val] = pd.Series(d["diana"][val]).map(medias).fillna(np.nanmean(media_pact[aj])).to_numpy()
        print(f"  pliegue {k} listo", flush=True)
    return aft, diana


def metricas_ranking(clase, pred):
    """EF 1%, EF 5%, BEDROC y activos en el primer 1% y 5%, con su tasa base."""
    n = len(clase)
    orden = np.argsort(-pred, kind="stable")
    c = clase[orden]
    base = c.mean()
    out = {"n": int(n), "activos": int(c.sum()), "tasa_base": float(base)}
    for pct in (1, 5):
        k = max(1, int(round(n * pct / 100)))
        hit = int(c[:k].sum())
        out[f"activos_en_{pct}pct"] = hit
        out[f"k_{pct}pct"] = k
        out[f"ef_{pct}pct"] = float((hit / k) / base) if base > 0 else float("nan")
    k100 = min(100, n)
    out["precision_100"] = float(c[:k100].mean())
    out["bedroc"] = float(CalcBEDROC([[int(v)] for v in c], 0, ALFA))
    return out


def bootstrap(clase, pred, grupos, rng):
    unicos, inv = np.unique(grupos, return_inverse=True)
    idx = [np.flatnonzero(inv == i) for i in range(len(unicos))]
    muestras = {"ef_1pct": [], "ef_5pct": [], "bedroc": []}
    for _ in range(REMUESTRAS):
        e = rng.integers(0, len(unicos), len(unicos))
        s = np.concatenate([idx[g] for g in e])
        if clase[s].sum() == 0:
            continue
        m = metricas_ranking(clase[s], pred[s])
        for k in muestras:
            muestras[k].append(m[k])
    return {k: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for k, v in muestras.items()}


def main() -> None:
    d = datos()
    rng = np.random.default_rng(0)
    params = {"modelo": "aft", "semilla_particion": 0, "pliegues": 5, "alfa_bedroc": ALFA,
              "remuestras": REMUESTRAS, "controles": ["azar", "solo_diana"], "toca_prueba": False,
              "etiqueta": "activo_10um; se excluyen los pares sin etiqueta",
              "filas_ajuste": int(len(d["clase"]))}
    with Corrida("ranking-fase2-aft", decision="C.5", params=params, semillas=[0],
                 datos=[PARES, DESCRIPTORES]) as c:
        aft, diana = fuera_de_pliegue(d)
        azar = rng.random(len(aft))
        etiquetado = ~np.isnan(d["clase"])
        filas = []
        for estrato in ESTRATOS:
            sel = etiquetado & ((d["estrato"] == estrato) if estrato != "todos" else True)
            clase = d["clase"][sel]
            if clase.sum() < 100 or (1 - clase).sum() < 100:
                continue
            for nombre, pred in (("aft", aft), ("solo_diana", diana), ("azar", azar)):
                m = metricas_ranking(clase, pred[sel])
                if nombre == "aft":
                    m["ic95"] = bootstrap(clase, pred[sel], d["grupos"][sel], rng)
                filas.append({"estrato": estrato, "orden": nombre, **m})
        tabla = pd.json_normalize(filas)
        print(tabla.drop(columns=[c for c in tabla.columns if c.startswith("ic95")]).round(3).to_string(index=False))
        print("\nIC95 del aft:")
        for f in filas:
            if "ic95" in f:
                print(f["estrato"], {k: [round(x, 2) for x in v] for k, v in f["ic95"].items()})
        c.metricas({"ranking": filas})


if __name__ == "__main__":
    main()
