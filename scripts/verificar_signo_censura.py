#!/usr/bin/env python3
"""Comprueba, con datos reales, que la censura entra al modelo del lado correcto.

La regresión de la potencia ([2.9](../docs/decisiones.md#d2-9)) ajusta
`survival:aft` de XGBoost en **concentración (µM)**, donde un `> 10 µM` es
censura por la derecha. El artefacto guarda el intervalo en pActividad, donde
el mismo `> 10 µM` es «menor que 5»: la conversión invierte el sentido, y un
signo equivocado no falla, solo enseña lo contrario (que los compuestos
inactivos son muy potentes).

La prueba unitaria (`tests/test_regresion.py`) ata la conversión sobre casos
armados a mano. Esto la ata sobre los pares reales, de tres maneras que no
dependen de afinar nada:

1. **La predicción respeta la cota.** De los pares de validación censurados por
   la derecha en concentración (`> L µM`), qué fracción queda predicha con
   concentración mayor que `L`. Con el signo bueno debe ser mucha; con el
   invertido, poca.
2. **Control negativo.** El mismo ajuste con el sentido de la censura invertido
   a propósito (`> L` leído como `< L`). Si la comprobación no distingue los dos,
   no comprueba nada.
3. **El orden de las exactas.** Spearman y concordancia de Harrell sobre la
   validación, para ver que el signo bueno no cuesta lo que ya se sabe predecir.

Entrena con el 70% de entrenamiento y evalúa en el 10% de validación; la prueba
reservada no se toca ([2.7](../docs/decisiones.md#d2-7)). No es el modelo final:
es una comprobación de signo, sin afinar.

    python scripts/verificar_signo_censura.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.evaluation.regresion import limites_en_micromolar, metricas_regresion  # noqa: E402
from src.tracking import Corrida  # noqa: E402

PROCESADOS = RAIZ / "data" / "processed"
SEMILLA = 0
RONDAS = 300
PARAMS = {
    "objective": "survival:aft",
    "eval_metric": "aft-nloglik",
    "aft_loss_distribution": "normal",
    "aft_loss_distribution_scale": 1.0,
    "learning_rate": 0.1,
    "max_depth": 6,
    "subsample": 0.8,
    "colsample_bytree": 0.5,
    "tree_method": "hist",
    "seed": SEMILLA,
}


def invertir_censura(inferior_um: np.ndarray, superior_um: np.ndarray
                     ) -> tuple[np.ndarray, np.ndarray]:
    """El error que se quiere detectar: leer cada censura del lado contrario.

    Un `> L` (inferior L, superior ∞) pasa a `< L` (inferior 0, superior L), y un
    `< U` (inferior 0, superior U) pasa a `> U`. Las exactas no cambian."""
    inf, sup = inferior_um.copy(), superior_um.copy()
    derecha = np.isinf(superior_um)
    izquierda = (inferior_um == 0) & np.isfinite(superior_um)
    inf[derecha], sup[derecha] = 0.0, inferior_um[derecha]
    inf[izquierda], sup[izquierda] = superior_um[izquierda], np.inf
    return inf, sup


def ajustar(X_ent, inferior_um, superior_um, X_val) -> np.ndarray:
    """Ajusta `survival:aft` en µM y devuelve la potencia predicha (pActividad)."""
    ent = xgb.DMatrix(X_ent)
    ent.set_float_info("label_lower_bound", inferior_um)
    ent.set_float_info("label_upper_bound", superior_um)
    modelo = xgb.train(PARAMS, ent, num_boost_round=RONDAS)
    um = modelo.predict(xgb.DMatrix(X_val))              # la concentración, en µM
    return 6.0 - np.log10(um)


def _medir(corrida: Corrida) -> None:
    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")
    d = pares[pares["particion"].ne("prueba")].merge(desc, on="smiles", how="inner")
    d = d.reset_index(drop=True)
    columnas = [c for c in desc.columns if c != "smiles"]
    X = np.hstack([d[columnas].to_numpy(dtype=np.float32),
                   pd.get_dummies(d["target_gene"]).to_numpy(dtype=np.float32)])

    inf_pa = d["limite_inferior"].to_numpy(dtype=float)
    sup_pa = d["limite_superior"].to_numpy(dtype=float)
    inferior_um, superior_um = limites_en_micromolar(inf_pa, sup_pa)

    ent = (d["particion"] == "entrenamiento").to_numpy()
    val = (d["particion"] == "validacion").to_numpy()
    derecha_val = val & np.isinf(superior_um)          # `> L µM` en validación
    print(f"entrenamiento {ent.sum():,} · validación {val.sum():,} · "
          f"censurados por la derecha en validación {derecha_val.sum():,}")

    variantes = {
        "signo_correcto": (inferior_um, superior_um),
        "signo_invertido": invertir_censura(inferior_um, superior_um),
    }
    resultados = {}
    for nombre, (lo, hi) in variantes.items():
        pred = ajustar(X[ent], lo[ent], hi[ent], X[val])
        # La pActividad predicha de los `> L`: respeta la cota si la
        # concentración predicha supera L, es decir si pActividad < 6 − log10 L.
        pred_todo = np.full(len(d), np.nan)
        pred_todo[val] = pred
        cota_pa = 6.0 - np.log10(inferior_um[derecha_val])
        respeta = float(np.mean(pred_todo[derecha_val] < cota_pa))
        m = metricas_regresion(inf_pa[val], sup_pa[val], pred)
        m["respeta_la_cota"] = respeta
        m["pa_media_censurados_derecha"] = float(np.mean(pred_todo[derecha_val]))
        resultados[nombre] = m
        print(f"\n{nombre}")
        for k, v in m.items():
            print(f"  {k:30s} {v:.3f}" if isinstance(v, float) else f"  {k:30s} {v}")

    exactas = val & np.isfinite(inf_pa) & (inf_pa == sup_pa)
    resultados["referencia"] = {
        "pa_media_exactas_validacion": float(np.mean(inf_pa[exactas])),
        "pa_media_censurados_derecha_cota": float(np.mean(
            6.0 - np.log10(inferior_um[derecha_val]))),
    }
    bueno = resultados["signo_correcto"]["respeta_la_cota"]
    malo = resultados["signo_invertido"]["respeta_la_cota"]
    resultados["distingue_los_signos"] = bool(bueno > malo + 0.2)
    print(f"\nrespeta la cota: correcto {bueno:.1%} · invertido {malo:.1%} "
          f"→ la comprobación {'distingue' if bueno > malo + 0.2 else 'NO distingue'} "
          "los dos signos")
    corrida.metricas(resultados)


def main() -> None:
    with Corrida("signo-censura-aft", decision="2.9",
                 params={"modelo": "xgboost survival:aft normal, sin afinar",
                         "rondas": RONDAS, "escala_de_ajuste": "µM",
                         "entrena_con": "entrenamiento", "evalua_en": "validación",
                         "variantes": ["signo_correcto", "signo_invertido"]},
                 semillas=[SEMILLA],
                 datos=[PROCESADOS / "fase2_pares.parquet",
                        PROCESADOS / "fase2_descriptores_limpios.parquet"]) as corrida:
        _medir(corrida)


if __name__ == "__main__":
    main()
