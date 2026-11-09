#!/usr/bin/env python3
"""Control 2 del #215 · ¿la ganancia de las huellas con el peso sobrevive a igualar los tramos? (fase 2)

La corrida `experimento_tamano_fase2.py` (E6) mostró que la ganancia de las huellas del `aft` crece con
el peso molecular, pero entrenando con los tramos desiguales: el de 350–500 Da pone ~2.5 veces más
pares en el ajuste que el de ≤250. El #215 pedía, antes de llamarlo efecto de tamaño, **igualar los
tramos por submuestreo** y repetir. Si la tendencia se aplana, era cuánta información hay de cada
tramo (densidad) y no el peso.

**Diseño, declarado antes de correr.** Mismas filas, semillas 0, 1, 2 y 5 pliegues que E6, así que
las 15 evaluaciones se parean con las suyas. En cada pliegue de ajuste:
- `equilibrado`: se sortean, sin reemplazo, tantas filas de cada tramo como tiene el más pequeño;
- `azar`: se sortean al azar, sin reemplazo, el mismo número total de filas (4 × el del más pequeño).
  Es el control del control: separa «entrenar con menos filas» de «entrenar con los tramos parejos».
Los dos brazos del modelo son los de E6 (`aft` y `aft_huellas`) y se evalúan sobre el pliegue de
validación completo, por tramo, con la misma regla de reporte (≥ 1,000 pares de validación).

**La regla.** Sea D = ganancia(>500 Da) − ganancia(250–350 Da), pareada por evaluación. En E6 D vale
lo que dice `pliegues.csv` de esa corrida. La tendencia **sobrevive** si, con los tramos igualados,
el D medio es al menos la mitad del D de E6 y es positivo en 10 de las 15 evaluaciones o más. Si el D
medio es menor que la mitad o positivo en menos de 10, **se aplana**: era densidad. La regla se
aplica al brazo `equilibrado`; el `azar` solo dice cuánto del cambio es entrenar con menos filas.
No se reinterpreta después de verlo. No toca la prueba reservada.

    ./env/bin/python scripts/experimento_tamano_iguala_tramos.py
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
sys.path.insert(0, str(RAIZ / "scripts"))

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import StratifiedGroupKFold

from experimento_aft_huellas import DESCRIPTORES, N_BITS, PARES, PLIEGUES, SEMILLAS, datos
from experimento_tamano_fase2 import MIN_PARES, pesos_moleculares
from src.evaluation.regresion import concordancia_harrell
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado
from src.models.tareas import etiquetas_por_tamano
from src.tracking import Corrida

E6 = RAIZ / "experimentos" / "2026-11-03-artemio-1.3-tamano-huellas-actividad" / "pliegues.csv"
LIGERO, PESADO = "250–350 Da", ">500 Da"


def diferencia_pesado_medio(res: pd.DataFrame) -> pd.Series:
    """D por evaluación = ganancia(>500 Da) − ganancia(250–350 Da), indexada por (semilla, pliegue)."""
    t = res.pivot_table(index=["semilla", "pliegue"], columns="tramo", values="dif")
    return (t[PESADO] - t[LIGERO]).dropna()


def main() -> None:
    d = datos()
    peso = pesos_moleculares()
    assert len(peso) == len(d["inferior"]), "los pesos no son de las mismas filas que la matriz"
    tramo = etiquetas_por_tamano(peso)
    tramos = sorted(set(tramo))
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    modelos = {"aft": ("X", RegresionAFT(semilla=SEMILLAS[0])),
               "aft_huellas": ("X_mixta", ConHuellasCensurado(RegresionAFT(semilla=SEMILLAS[0]),
                                                              d["n_densas"], N_BITS))}
    params = {"modelos": list(modelos), "ajustes": ["equilibrado", "azar"], "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "n_bits": N_BITS, "tramos": tramos, "min_pares_validacion": MIN_PARES,
              "filas": int(len(tramo)), "toca_prueba": False, "iguala_tramos": True,
              "regla": "D medio >= mitad del de E6 y positivo en >= 10 de 15",
              "referencia": str(E6.relative_to(RAIZ))}
    with Corrida("tamano-huellas-actividad-igualado", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        filas, tamanos = [], []
        for semilla in SEMILLAS:
            cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=semilla)
            for k, (aj, val) in enumerate(cv.split(d["X"], clase, d["grupos"]), 1):
                rng = np.random.default_rng([semilla, k])
                cuentas = {t: int((tramo[aj] == t).sum()) for t in tramos}
                n_min = min(cuentas.values())
                ajustes = {
                    "equilibrado": np.concatenate([rng.choice(aj[tramo[aj] == t], n_min, replace=False)
                                                   for t in tramos]),
                    "azar": rng.choice(aj, n_min * len(tramos), replace=False)}
                tamanos.append({"semilla": semilla, "pliegue": k, "n_min_por_tramo": n_min,
                                "filas_ajuste": int(len(aj)), **{f"n_{t}": v for t, v in cuentas.items()}})
                for ajuste, idx in ajustes.items():
                    preds = {}
                    for nombre, (matriz, modelo) in modelos.items():
                        t0 = time.perf_counter()
                        m = clone(modelo)
                        m.fit(d[matriz][idx], d["inferior"][idx], d["superior"][idx])
                        preds[nombre] = m.predict(d[matriz][val])
                        print(f"  semilla {semilla} pliegue {k} {ajuste} {nombre} "
                              f"{time.perf_counter() - t0:.0f} s", flush=True)
                    for etiqueta in ("todos", *tramos):
                        sel = np.ones(len(val), bool) if etiqueta == "todos" else tramo[val] == etiqueta
                        if sel.sum() < MIN_PARES:
                            continue
                        fila = {"ajuste": ajuste, "semilla": semilla, "pliegue": k, "tramo": etiqueta,
                                "n": int(sel.sum())}
                        for nombre, p in preds.items():
                            fila[nombre] = concordancia_harrell(d["inferior"][val][sel],
                                                                d["superior"][val][sel], p[sel])
                        filas.append(fila)
        res = pd.DataFrame(filas)
        res["dif"] = res["aft_huellas"] - res["aft"]
        res.to_csv(c.carpeta / "pliegues.csv", index=False)
        pd.DataFrame(tamanos).to_csv(c.carpeta / "tamanos_de_ajuste.csv", index=False)

        e6 = pd.read_csv(E6)
        d_e6 = diferencia_pesado_medio(e6)
        resultados = {"d_e6_media": float(d_e6.mean()), "d_e6_positivas": int((d_e6 > 0).sum()),
                      "d_e6_evaluaciones": int(len(d_e6))}
        tabla = (res.groupby(["ajuste", "tramo"]).agg(
            evaluaciones=("dif", "size"), aft=("aft", "mean"), aft_huellas=("aft_huellas", "mean"),
            dif=("dif", "mean"), mejora_en=("dif", lambda s: int((s > 0).sum())))
            .round(4).reset_index())
        ref = e6.groupby("tramo").agg(dif_e6=("dif", "mean")).round(4).reset_index()
        tabla = tabla.merge(ref, on="tramo", how="left")
        print(tabla.to_string(index=False))
        for ajuste in ("equilibrado", "azar"):
            d_a = diferencia_pesado_medio(res[res["ajuste"] == ajuste])
            veredicto = ("sobrevive" if d_a.mean() >= resultados["d_e6_media"] / 2 and (d_a > 0).sum() >= 10
                         else "se aplana")
            resultados[ajuste] = {"d_media": float(d_a.mean()), "d_positivas": int((d_a > 0).sum()),
                                  "evaluaciones": int(len(d_a)), "d_sd": float(d_a.std()),
                                  "veredicto_por_la_regla": veredicto}
            print(f"{ajuste}: D = {d_a.mean():+.4f} (sd {d_a.std():.4f}), positivo en "
                  f"{int((d_a > 0).sum())} de {len(d_a)} → {veredicto}")
        print(f"E6: D = {resultados['d_e6_media']:+.4f}, positivo en {resultados['d_e6_positivas']} "
              f"de {resultados['d_e6_evaluaciones']}")
        c.metricas({"por_ajuste_y_tramo": tabla.to_dict("records"), **resultados})


if __name__ == "__main__":
    main()
