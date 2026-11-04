#!/usr/bin/env python3
"""E2 · la prueba reservada por rareza: ¿lo raro explica la caída, o es otra cosa? (Grettel, 3 nov)

La prueba tiene los andamios raros a propósito, y los modelos pasan de 0.919 (validación) a 0.793
de AUROC en la fase 1 y de 0.761 a 0.720 de concordancia en la fase 2. E1+ mostró que la
similitud al vecino más cercano de la prueba (0.414) es la de la fila ≥ 0.6 de la escalera, donde
`svm_rbf` da 0.913: la similitud sola no explica la caída. Esta corrida separa en la propia
prueba lo raro de lo grande y mide cuánto sabe el modelo más allá de una línea base de tamaño.

**Qué hace.** Reajusta los dos modelos finales con las filas de ajuste (`svm_rbf` en la fase 1,
`aft` en la fase 2; nada se vuelve a ajustar después de ver la prueba) y predice la prueba. A cada
compuesto de la prueba se le calcula su **similitud de Tanimoto (Morgan radio 2, 2048 bits) con
su vecino más cercano del ajuste**. La rareza son los **terciles de esa similitud dentro de cada
tramo de peso** (los cortes fijos de `etiquetas_por_tamano`): así rareza y tamaño no vienen
mezclados, que es lo que el análisis de andamios mostró que pasaba. Las líneas base son una
regresión logística sobre MolWt y TPSA (fase 1) y un `aft` sobre MolWt, TPSA y la diana (fase 2).

**Lo que se declara antes de correr.**
- Métrica principal: la **ventaja** del modelo sobre su línea base (AUROC en la fase 1,
  concordancia en la fase 2) en cada tercil de rareza, con los terciles definidos dentro de cada
  tramo y juntando los tramos. Intervalo del 95% por bootstrap de **grupos** (1,000 remuestras en
  la fase 1, 200 en la fase 2).
- Qué sostendría que **lo raro explica la caída**: que la ventaja en el tercil más raro sea menor
  que en el más parecido, con el intervalo de la diferencia de ventajas sin el cero. Qué diría
  que **no**: que la ventaja sea igual en los tres terciles; entonces la caída viene de otra cosa
  (prevalencia, tamaño, composición) y se dice así. No se reinterpreta.
- Se reportan también el desempeño absoluto por tercil y por tramo, **sin AUPRC por estrato** (#187),
  y solo en celdas con al menos 20 casos de la clase minoritaria.
- Control de validez: la corrida debe reproducir, con el reajuste, las cifras ya registradas de la
  prueba (fase 1: AUROC 0.7928; fase 2: concordancia 0.7200 y 0.530 en `solo_npass`). Si no, se
  reporta la discrepancia antes de interpretar nada.
- **Dos lecturas de la prueba**, una por fase, anotadas en `experimentos/prueba.csv` con su
  motivo. No se escriben predicciones a git.

    ./env/bin/python scripts/experimento_prueba_rareza.py     # unos 5 min en macOS
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
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.evaluation.regresion import concordancia_harrell
from src.models.aft import RegresionAFT
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar, etiquetas_por_tamano
from src.tracking import Corrida, tomar_prueba

RDLogger.DisableLog("rdApp.*")
MIN_MINORITARIA = 20
PARES = PROCESADOS / "fase2_pares.parquet"
DESC2 = PROCESADOS / "fase2_descriptores_limpios.parquet"
REGISTRADO = {"fase1_auroc": 0.7928, "fase2_concordancia": 0.7200, "fase2_solo_npass": 0.530}
ROTULOS = {0: "1 más raro", 1: "2 intermedio", 2: "3 más parecido"}


def similitud_al_vecino(smiles_prueba, smiles_ajuste) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    unicos = sorted(set(smiles_ajuste))
    fa = [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in unicos]
    cache = {}
    out = np.zeros(len(smiles_prueba))
    for i, s in enumerate(smiles_prueba):
        if s not in cache:
            cache[s] = max(DataStructs.BulkTanimotoSimilarity(gen.GetFingerprint(Chem.MolFromSmiles(s)), fa))
        out[i] = cache[s]
    return out


def terciles_en_tramos(similitud, tramo) -> np.ndarray:
    """0, 1, 2 según el tercil de similitud dentro de cada tramo de peso (0 = el más raro)."""
    t = np.zeros(len(similitud), int)
    for u in np.unique(tramo):
        sel = tramo == u
        cortes = np.quantile(similitud[sel], [1 / 3, 2 / 3])
        t[sel] = np.digitize(similitud[sel], cortes)
    return t


def ic_por_grupos(grupos, tercil, ventaja, remuestras, semilla=0):
    """`ventaja(idx)` devuelve la ventaja de cada tercil sobre las filas `idx`."""
    rng = np.random.default_rng(semilla)
    unicos, inv = np.unique(grupos, return_inverse=True)
    por_grupo = [np.flatnonzero(inv == i) for i in range(len(unicos))]
    punto = ventaja(np.arange(len(grupos)))
    muestras = []
    for _ in range(remuestras):
        e = rng.integers(0, len(unicos), len(unicos))
        idx = np.concatenate([por_grupo[g] for g in e])
        v = ventaja(idx)
        if not np.isnan(v).any():
            muestras.append(v)
    m = np.array(muestras)
    dif = m[:, 2] - m[:, 0]
    return {"ventaja": [round(float(x), 4) for x in punto],
            "ic95": [[round(float(np.percentile(m[:, k], 2.5)), 4),
                      round(float(np.percentile(m[:, k], 97.5)), 4)] for k in range(3)],
            "dif_parecido_menos_raro": round(float(punto[2] - punto[0]), 4),
            "ic95_dif": [round(float(np.percentile(dif, 2.5)), 4), round(float(np.percentile(dif, 97.5)), 4)],
            "remuestras_validas": int(len(m))}


def fase1(c):
    t = cargar("permeabilidad", estratos="tamano", incluir_prueba=True,
               motivo="E2: la prueba por rareza, lectura registrada con tomar_prueba más abajo")
    meta = t.meta.reset_index(drop=True)
    es_prueba = (meta["particion"] == "prueba").to_numpy()
    X, y = np.asarray(t.X, float), np.asarray(t.y)
    columnas = list(pd.read_parquet(PROCESADOS / DESCRIPTORES["descriptores"]).columns)
    idx_base = [columnas.index("MolWt"), columnas.index("TPSA")]
    modelos = {
        "svm_rbf": seleccion(("svm_rbf",))["svm_rbf"],
        "base_peso_tpsa": Pipeline([("cols", ColumnTransformer([("c", "passthrough", idx_base)])),
                                    ("escala", MinMaxScaler()),
                                    ("modelo", LogisticRegression(max_iter=3000, random_state=0))]),
    }
    ajuste = np.flatnonzero(~es_prueba)
    prueba = tomar_prueba(meta, final=True,
                          motivo="E2 fase 1: la prueba por rareza (terciles de similitud dentro de cada "
                                 "tramo de peso) contra una línea base de peso y TPSA; modelos reajustados "
                                 "con las filas de ajuste")
    p_idx = prueba.index.to_numpy()
    pred = {k: clone(m).fit(X[ajuste], y[ajuste]).predict_proba(X[p_idx])[:, 1] for k, m in modelos.items()}
    yt, g = y[p_idx], np.asarray(t.grupos)[p_idx]
    tramo = np.asarray(t.estratos)[p_idx]
    sim = similitud_al_vecino(meta["SMILES"].to_numpy()[p_idx], meta["SMILES"].to_numpy()[ajuste])
    terc = terciles_en_tramos(sim, tramo)
    auroc_total = roc_auc_score(yt, pred["svm_rbf"])
    print(f"fase 1: AUROC de la prueba con el reajuste {auroc_total:.4f} "
          f"(registrado {REGISTRADO['fase1_auroc']}) · n={len(yt)} · similitud media {sim.mean():.3f}")

    def auroc_en(sel, p):
        ys = yt[sel]
        if min(ys.sum(), (1 - ys).sum()) < MIN_MINORITARIA:
            return float("nan")
        return roc_auc_score(ys, p[sel])

    def ventaja(idx):
        out = []
        for k in range(3):
            s = idx[terc[idx] == k]
            ys = yt[s]
            if len(np.unique(ys)) < 2:
                out.append(np.nan)
                continue
            out.append(roc_auc_score(ys, pred["svm_rbf"][s]) - roc_auc_score(ys, pred["base_peso_tpsa"][s]))
        return np.array(out)

    celdas = []
    for u in sorted(np.unique(tramo)):
        for k in range(3):
            sel = (tramo == u) & (terc == k)
            celdas.append({"tramo": u, "tercil": ROTULOS[k], "n": int(sel.sum()),
                           "activos": int(yt[sel].sum()),
                           "auroc_svm": round(auroc_en(sel, pred["svm_rbf"]), 4),
                           "auroc_base": round(auroc_en(sel, pred["base_peso_tpsa"]), 4)})
    por_tercil = []
    for k in range(3):
        sel = terc == k
        por_tercil.append({"tercil": ROTULOS[k], "n": int(sel.sum()),
                           "similitud_media": round(float(sim[sel].mean()), 3),
                           "auroc_svm": round(auroc_en(sel, pred["svm_rbf"]), 4),
                           "auroc_base": round(auroc_en(sel, pred["base_peso_tpsa"]), 4)})
    ic = ic_por_grupos(g, terc, ventaja, 1000)
    print(pd.DataFrame(por_tercil).to_string(index=False))
    print(pd.DataFrame(celdas).to_string(index=False))
    print("ventaja por tercil e IC:", ic)
    return {"auroc_reajuste": round(float(auroc_total), 4), "n": int(len(yt)),
            "similitud_media": round(float(sim.mean()), 4), "por_tercil": por_tercil,
            "por_tramo_y_tercil": celdas, "ventaja": ic}


def fase2(c):
    pares, desc = pd.read_parquet(PARES), pd.read_parquet(DESC2)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [x for x in desc.columns if x != "smiles"]
    inf, sup = d["limite_inferior"].to_numpy(float), d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inf) & np.isposinf(sup)) & (inf <= sup)
    d, inf, sup = d[util].reset_index(drop=True), inf[util], sup[util]
    diana = pd.get_dummies(d["target_gene"]).to_numpy("float32")
    X = np.hstack([d[cols].to_numpy("float32"), diana])
    Xb = np.hstack([d[["MolWt", "TPSA"]].to_numpy("float32"), diana])
    ajuste = np.flatnonzero((d["particion"] != "prueba").to_numpy())
    prueba = tomar_prueba(d, final=True,
                          motivo="E2 fase 2: la prueba por rareza (terciles de similitud dentro de cada "
                                 "tramo de peso) contra una línea base de peso, TPSA y diana; modelos "
                                 "reajustados con las filas de ajuste")
    p_idx = prueba.index.to_numpy()
    aft = RegresionAFT(semilla=0).fit(X[ajuste], inf[ajuste], sup[ajuste])
    base = RegresionAFT(semilla=0).fit(Xb[ajuste], inf[ajuste], sup[ajuste])
    pa, pb = aft.predict(X[p_idx]), base.predict(Xb[p_idx])
    li, ls, g = inf[p_idx], sup[p_idx], d["grupo_cv"].to_numpy()[p_idx]
    tramo = etiquetas_por_tamano(d["MolWt"].to_numpy(float)[p_idx])
    estrato = d["estrato"].to_numpy()[p_idx]
    sim = similitud_al_vecino(d["smiles"].to_numpy()[p_idx], d["smiles"].to_numpy()[ajuste])
    terc = terciles_en_tramos(sim, tramo)
    conc = concordancia_harrell(li, ls, pa)
    npass = concordancia_harrell(li[estrato == "solo_npass"], ls[estrato == "solo_npass"], pa[estrato == "solo_npass"])
    print(f"fase 2: concordancia de la prueba con el reajuste {conc:.4f} (registrada "
          f"{REGISTRADO['fase2_concordancia']}) · solo_npass {npass:.4f} (registrada "
          f"{REGISTRADO['fase2_solo_npass']}) · n={len(li)}")

    def conc_en(sel, p):
        return concordancia_harrell(li[sel], ls[sel], p[sel])

    def ventaja(idx):
        out = []
        for k in range(3):
            s = idx[terc[idx] == k]
            out.append(concordancia_harrell(li[s], ls[s], pa[s]) - concordancia_harrell(li[s], ls[s], pb[s]))
        return np.array(out)

    por_tercil = [{"tercil": ROTULOS[k], "n": int((terc == k).sum()),
                   "similitud_media": round(float(sim[terc == k].mean()), 3),
                   "conc_aft": round(conc_en(terc == k, pa), 4),
                   "conc_base": round(conc_en(terc == k, pb), 4)} for k in range(3)]
    por_estrato = [{"estrato": e, "n": int((estrato == e).sum()),
                    "conc_aft": round(conc_en(estrato == e, pa), 4),
                    "conc_base": round(conc_en(estrato == e, pb), 4)}
                   for e in ("solo_chembl", "mixto", "solo_npass") if (estrato == e).sum() >= 100]
    ic = ic_por_grupos(g, terc, ventaja, 200)
    print(pd.DataFrame(por_tercil).to_string(index=False))
    print(pd.DataFrame(por_estrato).to_string(index=False))
    print("ventaja por tercil e IC:", ic)
    return {"concordancia_reajuste": round(float(conc), 4), "solo_npass_reajuste": round(float(npass), 4),
            "n": int(len(li)), "similitud_media": round(float(sim.mean()), 4),
            "por_tercil": por_tercil, "por_estrato": por_estrato, "ventaja": ic}


def main() -> None:
    params = {"modelos": {"fase1": "svm_rbf", "fase2": "aft"},
              "lineas_base": {"fase1": "logistica sobre MolWt y TPSA",
                              "fase2": "aft sobre MolWt, TPSA y diana"},
              "rareza": "terciles de similitud de Tanimoto (Morgan r2, 2048) al vecino más cercano "
                        "del ajuste, dentro de cada tramo de peso",
              "min_minoritaria_celda": MIN_MINORITARIA, "registrado": REGISTRADO,
              "remuestras": {"fase1": 1000, "fase2": 200},
              "toca_prueba": "sí: dos lecturas anotadas en experimentos/prueba.csv, una por fase"}
    with Corrida("prueba-por-rareza", decision="1.5", params=params, semillas=[0],
                 datos=[PROCESADOS / "bbb_meta.parquet", PARES, DESC2]) as c:
        r1 = fase1(c)
        r2 = fase2(c)
        c.metricas({"fase1": r1, "fase2": r2})


if __name__ == "__main__":
    main()
