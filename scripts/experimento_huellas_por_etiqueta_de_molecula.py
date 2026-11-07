#!/usr/bin/env python3
"""¿Las huellas dejan de ayudar cuando la etiqueta pasa de «encuentro» a «molécula entera»? (E10)

La hipótesis de **granularidad** (A del artículo) dice que las huellas ayudan en la fase 2 porque su
etiqueta describe un encuentro entre una molécula y una diana, y no ayudan en la fase 1 porque la
etiqueta es una propiedad de la molécula entera. Esto la pone a prueba con los datos de la fase 2:
se cambia **solo** la etiqueta, de «el par molécula–diana es activo a 10 µM» a «la molécula es activa
contra alguna diana», con las mismas moléculas, el mismo tamaño de datos (≈46,000 moléculas de ajuste,
no las 6,300 de la fase 1) y la misma partición por `grupo_cv`. Si A es cierta, aquí tendría que pasar
lo de la fase 1: las huellas no ayudan.

**Qué se mide.** Clasificación binaria por molécula. Tres brazos, como el 03c: `descriptores`,
`huellas` (sin descriptores) y `descriptores+huellas`, con el vocabulario Sort & Slice (2,048) aprendido
dentro de cada pliegue. Cuatro modelos baratos del catálogo de la fase 1 (`logistica`, `arbol`,
`bayes`, `svm_sgd`); el `svm_rbf` y el `mlp` no caben en el tiempo con 46,000 filas y 2,249 columnas.
15 evaluaciones (5 pliegues × 3 semillas), AUROC y MCC.

**La etiqueta.** Molécula = 1 si alguno de sus pares tiene `activo_10um` = 1; 0 si tiene pares
decididos y ninguno es activo; fuera si ningún par decide la etiqueta. **Tiene un sesgo que se mide y no
se corrige:** una molécula probada contra muchas dianas tiene más oportunidades de ser activa. Se
reporta el AUROC de un control que solo ve el número de pares (`n_pares`).

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Una huella **ayuda** a un modelo con la regla del proyecto: diferencia pareada media positiva y mejor
   en 12 de 15 evaluaciones, **en AUROC y en MCC a la vez**.
2. **A se apoya** si ningún modelo es ayudado por `descriptores+huellas` y la diferencia media de AUROC es
   negativa en al menos 3 de 4 modelos (el patrón de la fase 1). **A se contradice** si al menos 3 de 4
   modelos son ayudados. Cualquier otro caso es **no concluyente** y se reporta así.
3. Los cuatro modelos no son los seis de la fase 1; se dice así y no se generaliza.
4. Si el control de `n_pares` tiene AUROC ≥ 0.70, el sesgo de la etiqueta es grande y la conclusión se
   degrada a «no concluyente» aunque la regla 2 dé un veredicto.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_huellas_por_etiqueta_de_molecula.py
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
from scipy import sparse
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline

from src.evaluation.cv import evaluar
from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan
from src.models.alternativos import seleccion
from src.tracking import Corrida

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
SEMILLAS = (0, 1, 2)
N_BITS = 2048
MODELOS = ("logistica", "arbol", "bayes", "svm_sgd")
REGLA_EVALUACIONES = 12
MIN_MODELOS = 3
SESGO_MAXIMO = 0.70


def moleculas() -> dict:
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    fuera = pares[pares["particion"] != "prueba"]
    decididos = fuera.dropna(subset=["activo_10um"])
    por = decididos.groupby("smiles").agg(y=("activo_10um", "max"), n_pares=("activo_10um", "size"),
                                         grupo=("grupo_cv", "nunique"))
    assert (por["grupo"] == 1).all(), "una molécula cae en más de un grupo_cv"
    grupo = decididos.groupby("smiles")["grupo_cv"].first()
    cols = [c for c in desc.columns if c != "smiles"]
    d = desc.set_index("smiles").loc[por.index, cols]
    huellas, ids = identificadores_morgan(por.index.tolist())
    huellas, ids, _ = agrupar_iguales(huellas, ids)
    X = sparse.hstack([sparse.csr_matrix(d.to_numpy("float32")), huellas]).tocsr()
    return {"X": X, "n_densas": len(cols), "y": por["y"].to_numpy(int), "grupos": grupo.loc[por.index].to_numpy(),
            "n_pares": por["n_pares"].to_numpy(float)}


def brazos(n_densas: int) -> dict:
    variantes = {"descriptores": dict(n_bits=0),
                 "huellas": dict(densas=(), n_bits=N_BITS),
                 "descriptores+huellas": dict(n_bits=N_BITS)}
    salida = {}
    for modelo, p in seleccion(MODELOS).items():
        for nombre, kw in variantes.items():
            salida[f"{modelo}|{nombre}"] = Pipeline([("huellas", AgregarHuellas(n_densas, **kw))] + list(p.steps))
    return salida


def contra_descriptores(res: pd.DataFrame) -> dict:
    todos = res[res["estrato"] == "todos"].copy()
    todos[["modelo", "brazo"]] = todos["modelo"].str.split("|", expand=True)
    salida = {}
    for modelo, g in todos.groupby("modelo"):
        fila = {}
        for brazo in ("huellas", "descriptores+huellas"):
            d = {}
            for m in ("auroc", "mcc"):
                a = g[g["brazo"] == "descriptores"].set_index(["semilla", "pliegue"])[m]
                b = g[g["brazo"] == brazo].set_index(["semilla", "pliegue"])[m]
                dif = (b - a).dropna()
                d[m] = {"dif_media": round(float(dif.mean()), 4), "dif_desv": round(float(dif.std()), 4),
                        "mejor_en": int((dif > 0).sum()), "evaluaciones": int(len(dif))}
            d["ayuda"] = bool(all(d[m]["dif_media"] > 0 and d[m]["mejor_en"] >= REGLA_EVALUACIONES for m in d))
            fila[brazo] = d
        fila["auroc_descriptores"] = round(float(g[g["brazo"] == "descriptores"]["auroc"].mean()), 4)
        salida[modelo] = fila
    return salida


def main() -> None:
    m = moleculas()
    print(f"{len(m['y']):,} moléculas · {len(np.unique(m['grupos'])):,} grupos · {m['y'].mean():.1%} activas", flush=True)
    params = {"modelos": list(MODELOS), "brazos": ["descriptores", "huellas", "descriptores+huellas"],
              "semillas": list(SEMILLAS), "pliegues": 5, "n_bits_sortslice": N_BITS,
              "etiqueta": "molécula activa si algún par tiene activo_10um = 1",
              "moleculas": int(len(m["y"])), "prevalencia": round(float(m["y"].mean()), 4),
              "regla_evaluaciones": REGLA_EVALUACIONES, "min_modelos": MIN_MODELOS,
              "sesgo_maximo_auroc_n_pares": SESGO_MAXIMO, "toca_prueba": False}
    with Corrida("huellas-por-etiqueta-de-molecula-actividad", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=[PARES, DESCRIPTORES]) as c:
        sesgo = float(roc_auc_score(m["y"], m["n_pares"]))
        print(f"control n_pares: AUROC {sesgo:.3f}", flush=True)
        partes = []
        t0 = time.perf_counter()
        for nombre, pipe in brazos(m["n_densas"]).items():
            t = time.perf_counter()
            r, _ = evaluar({nombre: pipe}, m["X"], m["y"], m["grupos"], semillas=SEMILLAS, verboso=False)
            partes.append(r)
            pd.concat(partes, ignore_index=True).to_csv(c.carpeta / "pliegues.csv", index=False)
            print(f"  {nombre:28}{time.perf_counter() - t:6.0f} s (total {time.perf_counter() - t0:.0f} s)", flush=True)
        res = pd.concat(partes, ignore_index=True)
        tabla = contra_descriptores(res)
        ayudados = [k for k, v in tabla.items() if v["descriptores+huellas"]["ayuda"]]
        negativos = [k for k, v in tabla.items() if v["descriptores+huellas"]["auroc"]["dif_media"] < 0]
        if len(ayudados) >= MIN_MODELOS:
            veredicto = "A se contradice"
        elif not ayudados and len(negativos) >= MIN_MODELOS:
            veredicto = "A se apoya"
        else:
            veredicto = "no concluyente"
        if sesgo >= SESGO_MAXIMO:
            veredicto = "no concluyente (sesgo de la etiqueta)"
        c.metricas({"por_modelo": tabla, "ayudados": ayudados, "auroc_negativo": negativos,
                    "auroc_control_n_pares": round(sesgo, 4), "veredicto_declarado": veredicto})
        print(f"\nayudados por descriptores+huellas: {ayudados}\nAUROC negativo: {negativos}\nveredicto: {veredicto}")
        for k, v in tabla.items():
            print(k, v["descriptores+huellas"]["auroc"], v["descriptores+huellas"]["mcc"], "| huellas solas:",
                  v["huellas"]["auroc"]["dif_media"])


if __name__ == "__main__":
    main()
