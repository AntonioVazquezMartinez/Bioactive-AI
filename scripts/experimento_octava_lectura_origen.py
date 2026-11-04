#!/usr/bin/env python3
"""Octava lectura de la prueba reservada (fase 1): ¿la caída baja con la similitud, y en cuál de los tres orígenes?

Pregunta 6.3 de Grettel (3 de noviembre). **El AUROC de la prueba por origen ya estaba registrado** en
`2026-11-01-artemio-1.5-modelo-final-permeabilidad` (natural exacto 0.780, análogo 0.730, sin equivalente 0.793),
así que el desglose por origen a secas no necesitaba una lectura nueva. Lo que no existe es el cruce con la
**similitud de cada compuesto de prueba al ajuste**, y eso sí pide las etiquetas.

**Regla declarada antes de correr.**

1. *Control (aborta si falla):* el `svm_rbf` entregado, ajustado con entrenamiento y validación, reproduce el
   AUROC global de la prueba registrado (0.7928) y el MCC (0.3385) con tolerancia 0.001.
2. Similitud de cada compuesto de prueba = Tanimoto máximo (Morgan radio 2, 2048 bits) contra los compuestos
   de ajuste. Los cortes de los terciles se fijan **una vez, sobre toda la prueba**, para que el mismo tercil
   signifique lo mismo en los tres orígenes.
3. Se reporta, por origen y global, el AUROC de cada tercil (solo si la minoritaria llega a 20 casos, el mismo
   mínimo del arnés) y la diferencia tercil más parecido menos tercil menos parecido, con IC95% remuestreando
   esqueletos de la prueba (1,000 réplicas, percentiles, semilla 0).
4. «La caída baja con la similitud» solo se afirma en un origen si el IC de esa diferencia excluye el cero y
   es positiva; si no, el resultado es que no se distingue. No se ajusta nada tras ver las cifras.

Una sola lectura, por `tomar_prueba` con motivo.

    python scripts/experimento_octava_lectura_origen.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import matthews_corrcoef, roc_auc_score

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import inferencia  # noqa: E402
from src.models import cargar, seleccion  # noqa: E402
from src.tracking import Corrida, tomar_prueba  # noqa: E402

META = RAIZ / "data" / "processed" / "bbb_meta.parquet"
MOTIVO = ("Cruce del AUROC de la prueba con la similitud al ajuste, por origen (pregunta 6.3 de Grettel); "
          "el desglose por origen a secas ya estaba registrado")
REPLICAS = 1000
MINIMO = 20


def auroc(y, p):
    if min(int(y.sum()), int((1 - y).sum())) < MINIMO:
        return float("nan")
    return float(roc_auc_score(y, p))


def diferencia(d, esqueletos, rng) -> dict:
    """AUROC del tercil más parecido menos el del menos parecido, con IC remuestreando esqueletos."""
    def una(x):
        a, b = x[x["tercil"] == 2], x[x["tercil"] == 0]
        return auroc(a["y"].to_numpy(), a["p"].to_numpy()) - auroc(b["y"].to_numpy(), b["p"].to_numpy())
    punto = una(d)
    grupos = {k: v for k, v in d.groupby(esqueletos)}
    claves = list(grupos)
    valores = []
    for _ in range(REPLICAS):
        elegidos = rng.integers(0, len(claves), len(claves))
        valores.append(una(pd.concat([grupos[claves[i]] for i in elegidos])))
    ic = [float(np.nanpercentile(valores, 2.5)), float(np.nanpercentile(valores, 97.5))]
    return {"diferencia": punto, "ic95": ic, "excluye_cero": bool(np.isfinite(punto) and (ic[0] > 0 or ic[1] < 0))}


def main() -> None:
    meta = pd.read_parquet(META).assign(fila=lambda d: np.arange(len(d)))
    completo = cargar("permeabilidad", estratos="origen", incluir_prueba=True, motivo=MOTIVO)
    ajuste = meta["particion"].ne("prueba").to_numpy()
    modelo = clone(seleccion(("svm_rbf",))["svm_rbf"])
    with Corrida("octava-lectura-origen-similitud", decision="1.5",
                 params={"regla": "terciles de similitud fijos sobre toda la prueba; IC por esqueleto",
                         "replicas": REPLICAS, "minimo_minoritaria": MINIMO, "motivo": MOTIVO},
                 semillas=[0], datos=[META]) as c:
        prueba = tomar_prueba(meta.assign(estrato=completo.estratos), final=True, motivo=MOTIVO)
        idx = prueba["fila"].to_numpy()
        # `completo.X` ya trae las filas de ajuste y las de prueba en el orden de `meta`
        modelo.fit(completo.X[ajuste], completo.y[ajuste])
        p = modelo.predict_proba(completo.X[idx])[:, 1]
        y = completo.y[idx]
        g, mcc = auroc(y, p), float(matthews_corrcoef(y, (p >= 0.5).astype(int)))
        assert abs(g - 0.7928) < 0.001 and abs(mcc - 0.3385) < 0.001, f"CONTROL NO PASADO: {g:.4f} {mcc:.4f}"
        print(f"control pasado: AUROC {g:.4f} · MCC {mcc:.4f}")

        smiles = meta["SMILES"].tolist()
        h_ajuste = inferencia.huellas_empaquetadas([smiles[i] for i in np.flatnonzero(ajuste)])
        h_prueba = inferencia.huellas_empaquetadas([smiles[i] for i in idx])
        sim = inferencia.similitud_al_vecino(h_prueba, h_ajuste)
        cortes = np.quantile(sim, [1 / 3, 2 / 3])
        d = pd.DataFrame({"y": y, "p": p, "sim": sim, "origen": completo.estratos[idx],
                          "tercil": np.digitize(sim, cortes)})
        esq = meta["esqueleto"].to_numpy()[idx]
        rng = np.random.default_rng(0)
        res = {"cortes_similitud": [float(x) for x in cortes], "auroc_global": g, "mcc_global": mcc, "por_origen": {}}
        for nombre, x, e in [("todos", d, esq)] + [(o, d[d["origen"] == o], esq[(d["origen"] == o).to_numpy()])
                                                    for o in sorted(d["origen"].unique())]:
            res["por_origen"][nombre] = {
                "n": int(len(x)),
                "auroc": auroc(x["y"].to_numpy(), x["p"].to_numpy()),
                "por_tercil": {int(t): {"n": int((x["tercil"] == t).sum()),
                                        "prevalencia": float(x.loc[x["tercil"] == t, "y"].mean()),
                                        "auroc": auroc(x.loc[x["tercil"] == t, "y"].to_numpy(),
                                                       x.loc[x["tercil"] == t, "p"].to_numpy())}
                               for t in (0, 1, 2)},
                "parecido_menos_lejano": diferencia(x, e, rng)}
        c.metricas(res)
    for k, v in res["por_origen"].items():
        print(k, v["n"], round(v["auroc"], 3), {t: (w["n"], round(w["auroc"], 3)) for t, w in v["por_tercil"].items()},
              v["parecido_menos_lejano"])


if __name__ == "__main__":
    main()
