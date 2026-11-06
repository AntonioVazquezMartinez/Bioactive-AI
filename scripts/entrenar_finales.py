#!/usr/bin/env python3
"""Entrena y guarda los dos modelos finales para el cuaderno de la patrocinadora (`models/finales/`).

**Con qué filas.** Las de **ajuste** (entrenamiento y validación), nunca la prueba reservada: es la decisión del
4 de noviembre. En la fase 1 la curva de aprendizaje está en meseta (+0.002 de AUROC del 75 al 100%); en la fase 2
sigue subiendo (+0.0076 de concordancia) y se renuncia a esa ganancia para poder evaluar y repetir la cifra
registrada. Este script **no lee ninguna etiqueta de la prueba** y no llama a `tomar_prueba`.

| fase | modelo | filas | columnas |
|:--|:--|--:|:--|
| 1 | `svm_rbf` calibrado (el del catálogo, sin cambios) | 6,306 | 151 descriptores |
| 2 | `aft` censurado (σ = 1.0, 100 rondas, profundidad 6, semilla 0) | 56,241 | 201 descriptores y la diana (26) |

Escribe en `models/finales/`: los dos modelos, `meta.json` (columnas, dianas, versiones, commit, `sha256` de los
datos y 25 predicciones de referencia sobre compuestos de B3DB para comprobar el artefacto sin los datos), y las
huellas de los compuestos de ajuste (bits empaquetados) con las que el cuaderno dice qué tan cerca queda cada
consulta de lo ya visto. **Las cifras de desempeño no se recalculan aquí**: son las de las corridas registradas
(1.5 y 2.13).

    ./env312/bin/python scripts/entrenar_finales.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import json
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import joblib
import numpy as np
import pandas as pd

from src.inferencia import CARPETA, huellas_empaquetadas
from src.models.alternativos import seleccion
from src.models.aft import RegresionAFT
from src.models.tareas import DESCRIPTORES as DESC1, PROCESADOS, cargar
from src.tracking import Corrida

PARES = PROCESADOS / "fase2_pares.parquet"
DESC2 = PROCESADOS / "fase2_descriptores_limpios.parquet"
VERIFICACION = 25
SEMILLA = 0


def fase2():
    """Las filas de ajuste de la fase 2 (como el 05b), con sus SMILES y los nombres de las dianas."""
    pares, desc = pd.read_parquet(PARES), pd.read_parquet(DESC2)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [c for c in desc.columns if c != "smiles"]
    inf, sup = d["limite_inferior"].to_numpy(float), d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inf) & np.isposinf(sup)) & (inf <= sup)
    d = d[util].reset_index(drop=True)
    inf, sup = inf[util], sup[util]
    fuera = (d["particion"] != "prueba").to_numpy()
    diana = pd.get_dummies(d["target_gene"])
    X = np.hstack([d[cols].to_numpy("float32"), diana.to_numpy("float32")])
    assert fuera.sum() == 56_241, "las filas de ajuste cambiaron respecto al 05b"
    assert not (d["particion"].to_numpy()[fuera] == "prueba").any()
    return {"X": X[fuera], "inferior": inf[fuera], "superior": sup[fuera], "smiles": d["smiles"].to_numpy()[fuera],
            "columnas": cols, "dianas": list(diana.columns)}


def main() -> None:
    CARPETA.mkdir(parents=True, exist_ok=True)
    columnas1 = list(pd.read_parquet(PROCESADOS / DESC1["descriptores"]).columns)
    params = {"fase1": "svm_rbf, 6,306 filas de ajuste, 151 descriptores", "fase2": "aft, 56,241 filas de ajuste, 201 + 26",
              "filas": "solo ajuste (decisión del 4 de noviembre)", "semilla": SEMILLA, "toca_prueba": False,
              "destino": str(CARPETA.relative_to(RAIZ))}
    with Corrida("entrenar-modelos-finales", decision="1.5", params=params, semillas=[SEMILLA],
                 datos=[PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESC1["descriptores"], PARES, DESC2]) as c:
        t0 = time.perf_counter()
        t = cargar("permeabilidad")                       # por omisión no incluye la prueba
        assert len(t.y) == 6_306 and t.X.shape[1] == len(columnas1) == 151
        modelo1 = seleccion(("svm_rbf",))["svm_rbf"].fit(t.X, t.y)
        joblib.dump(modelo1, CARPETA / "fase1_svm_rbf.joblib", compress=3)
        seg1 = time.perf_counter() - t0
        print(f"fase 1 · svm_rbf entrenado y guardado ({seg1:.0f} s)", flush=True)

        t0 = time.perf_counter()
        d2 = fase2()
        modelo2 = RegresionAFT(semilla=SEMILLA).fit(d2["X"], d2["inferior"], d2["superior"])
        modelo2.booster_.save_model(str(CARPETA / "fase2_aft.json"))
        seg2 = time.perf_counter() - t0
        print(f"fase 2 · aft entrenado y guardado ({seg2:.0f} s)", flush=True)

        h1 = huellas_empaquetadas(t.meta["SMILES"].tolist())
        h2 = huellas_empaquetadas(sorted(set(d2["smiles"])))
        np.savez_compressed(CARPETA / "huellas_fase1.npz", bits=h1)
        np.savez_compressed(CARPETA / "huellas_fase2.npz", bits=h2)

        # 25 compuestos de B3DB (CC0) con lo que predicen los dos modelos: referencia para comprobar el artefacto
        from src.inferencia import Modelos, predecir
        base = t.meta["SMILES"].sample(VERIFICACION, random_state=SEMILLA).tolist()
        dianas = d2["dianas"]
        meta = {
            "descripcion": "Modelos finales de Bioactive AI para el cuaderno de la patrocinadora. Entrenados con las "
                           "filas de ajuste; la prueba reservada no entra. Uso no comercial (NPASS es CC BY-NC).",
            "columnas_fase1": columnas1, "columnas_fase2": d2["columnas"], "dianas": dianas,
            "fase2_parametros": {k: v for k, v in modelo2.get_params().items()},
            "filas": {"fase1": int(len(t.y)), "fase2": int(len(d2["inferior"]))},
            "cifras_registradas": {
                "fase1_svm_rbf": "MCC 0.7017 y AUROC 0.9190 en validación cruzada agrupada; en la prueba reservada MCC 0.3385 y "
                                 "AUROC 0.7928 (corridas 2026-11-01-artemio-1.5-ensambles-permeabilidad y …-modelo-final-permeabilidad)",
                "fase2_aft": "concordancia 0.7610 en validación cruzada agrupada (0.6322 en solo NPASS); en la prueba reservada "
                             "0.7200 (0.530 en solo NPASS, 117 pares) (corridas 2026-10-31-antonio-2.13 y 2026-11-01-ingrid-2.13)"},
            "umbral_extrapolacion": 0.4,
            "generado_con": "scripts/entrenar_finales.py",
        }
        (CARPETA / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")

        # recarga desde disco y referencia
        from src.inferencia import cargar as cargar_modelos
        m = cargar_modelos()
        ref = predecir(base, m)
        # el modelo que se acaba de entrenar en memoria debe dar lo mismo que el que se recargó
        mem = Modelos(fase1=modelo1, fase2=modelo2, meta=meta, huellas_fase1=h1, huellas_fase2=h2)
        ref_mem = predecir(base, mem)
        cols_p = ["p_bbb_mas", *[f"pActividad_{d}" for d in dianas]]
        dif = float(np.nanmax(np.abs(ref[cols_p].to_numpy() - ref_mem[cols_p].to_numpy())))
        print(f"recarga == memoria: diferencia máxima {dif:.2e}", flush=True)
        assert dif < 1e-6, "el modelo recargado no reproduce al entrenado"
        meta["verificacion"] = {"smiles": base,
                                "p_bbb_mas": [float(v) for v in ref["p_bbb_mas"]],
                                "pActividad": {d: [float(v) for v in ref[f"pActividad_{d}"]] for d in dianas[:3]},
                                "dianas_verificadas": dianas[:3], "tolerancia": 1e-5}
        (CARPETA / "meta.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False), encoding="utf-8")
        c.metricas({"filas": meta["filas"], "columnas": {"fase1": len(columnas1), "fase2": len(d2["columnas"]) + len(dianas)},
                    "segundos": {"fase1": round(seg1, 1), "fase2": round(seg2, 1)},
                    "recarga_menos_memoria_max": dif,
                    "tamano_bytes": {p.name: p.stat().st_size for p in sorted(CARPETA.iterdir())}})
        for p in sorted(CARPETA.iterdir()):
            print(f"  {p.name:26}{p.stat().st_size / 1e6:8.2f} MB")


if __name__ == "__main__":
    main()
