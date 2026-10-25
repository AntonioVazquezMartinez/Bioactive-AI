#!/usr/bin/env python3
"""Comprueba, con datos reales, que la censura entra al modelo del lado correcto.

La regresión de la potencia ([2.9](../docs/decisiones.md#d2-9)) usa los censurados
como cotas: un `> 10 µM` no es el valor 10 ni un dato faltante, es «la potencia
es menor que 5». En el artefacto el intervalo está en pActividad, y un `> L µM`
es `(−∞, 6 − log₁₀ L]`; leerlo del lado contrario no falla, solo enseña que los
compuestos inactivos son muy potentes.

La prueba unitaria (`tests/test_tobit.py`) ata la verosimilitud sobre datos
sintéticos. Esto la ata sobre los pares reales, con el modelo individual y
lineal del Avance 4 (`RegresionTobit`, sin ensambles), de tres maneras que no
dependen de afinar nada:

1. **La predicción respeta la cota.** De los pares de validación `> L µM`, qué
   fracción queda predicha más débil que la cota. Con el signo bueno debe ser
   mucha más que con el invertido.
2. **Control negativo.** El mismo ajuste con cada censura leída del lado
   contrario. Si la comprobación no distingue los dos, no comprueba nada.
3. **Contra la misma recta sin censura** (`Ridge` entrenada solo con las
   exactas, que es lo que hace un baseline sencillo): qué aporta usar la censura
   cuando el modelo es el mismo y solo cambia lo que ve.

Entrena con el 70% de entrenamiento y evalúa en el 10% de validación; la prueba
reservada no se toca ([2.7](../docs/decisiones.md#d2-7)). No es el modelo final.
Las filas sin ninguna cota no informan nada y se cuentan aparte.

    python scripts/verificar_signo_censura.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.evaluation.regresion import metricas_regresion  # noqa: E402
from src.models.tobit import RegresionTobit  # noqa: E402
from src.tracking import Corrida  # noqa: E402

PROCESADOS = RAIZ / "data" / "processed"
SEMILLA = 0
ALFA_RIDGE = 100.0        # la misma penalización, en la escala de cada modelo


def invertir_censura(inferior: np.ndarray, superior: np.ndarray
                     ) -> tuple[np.ndarray, np.ndarray]:
    """El error que se quiere detectar: leer cada censura del lado contrario.

    Un `(−∞, U]` pasa a `[U, +∞)` y un `[V, +∞)` a `(−∞, V]`. Las exactas no
    cambian."""
    inf, sup = inferior.copy(), superior.copy()
    izq = np.isneginf(inferior) & np.isfinite(superior)
    der = np.isfinite(inferior) & np.isposinf(superior)
    inf[izq], sup[izq] = superior[izq], np.inf
    inf[der], sup[der] = -np.inf, inferior[der]
    return inf, sup


def _medir(corrida: Corrida) -> None:
    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")
    d = pares[pares["particion"].ne("prueba")].merge(desc, on="smiles", how="inner")
    d = d.reset_index(drop=True)
    columnas = [c for c in desc.columns if c != "smiles"]
    X = np.hstack([d[columnas].to_numpy(dtype=np.float32),
                   pd.get_dummies(d["target_gene"]).to_numpy(dtype=np.float32)])

    inf = d["limite_inferior"].to_numpy(dtype=float)
    sup = d["limite_superior"].to_numpy(dtype=float)
    ent = (d["particion"] == "entrenamiento").to_numpy()
    val = (d["particion"] == "validacion").to_numpy()
    exacta = np.isfinite(inf) & (inf == sup)
    sin_cota = np.isneginf(inf) & np.isposinf(sup)
    # `> L µM` en concentración = `(−∞, U]` en pActividad
    debil_val = val & np.isneginf(inf) & np.isfinite(sup)
    print(f"entrenamiento {ent.sum():,} · validación {val.sum():,} · "
          f"`> L µM` en validación {debil_val.sum():,} · sin ninguna cota {sin_cota.sum():,}")

    inv_inf, inv_sup = invertir_censura(inf, sup)
    usa = ent & ~sin_cota
    variantes = {
        "tobit_signo_correcto": ("tobit", inf, sup, usa),
        "tobit_signo_invertido": ("tobit", inv_inf, inv_sup, usa),
        "ridge_solo_exactas": ("ridge", inf, sup, ent & exacta),
    }
    resultados = {"sin_ninguna_cota": int(sin_cota.sum())}
    for nombre, (modelo, lo, hi, filas) in variantes.items():
        if modelo == "tobit":
            ajuste = RegresionTobit(alfa=ALFA_RIDGE / filas.sum()).fit(
                X[filas], lo[filas], hi[filas])
            pred = ajuste.predict(X[val])
        else:
            esc = StandardScaler().fit(X[filas])
            pred = Ridge(alpha=ALFA_RIDGE).fit(esc.transform(X[filas]), inf[filas]
                                               ).predict(esc.transform(X[val]))
        pred_todo = np.full(len(d), np.nan)
        pred_todo[val] = pred
        m = metricas_regresion(inf[val], sup[val], pred)
        m["respeta_la_cota"] = float(np.mean(pred_todo[debil_val] < sup[debil_val]))
        m["pa_media_de_los_mayor_que"] = float(np.mean(pred_todo[debil_val]))
        m["n_entrenamiento"] = int(filas.sum())
        resultados[nombre] = m
        print(f"\n{nombre}")
        for k, v in m.items():
            print(f"  {k:30s} {v:.3f}" if isinstance(v, float) else f"  {k:30s} {v}")

    resultados["referencia"] = {
        "cota_media_de_los_mayor_que": float(np.mean(sup[debil_val])),
        "pa_media_exactas_validacion": float(np.mean(inf[val & exacta])),
    }
    bueno = resultados["tobit_signo_correcto"]["respeta_la_cota"]
    malo = resultados["tobit_signo_invertido"]["respeta_la_cota"]
    resultados["distingue_los_signos"] = bool(bueno > malo + 0.2)
    print(f"\nrespeta la cota: correcto {bueno:.1%} · invertido {malo:.1%} "
          f"→ la comprobación {'distingue' if bueno > malo + 0.2 else 'NO distingue'} "
          "los dos signos")
    corrida.metricas(resultados)


def main() -> None:
    with Corrida("signo-censura-tobit", decision="2.9",
                 params={"modelo": "RegresionTobit (lineal, individual) y Ridge",
                         "alfa_ridge": ALFA_RIDGE, "escala_de_ajuste": "pActividad",
                         "entrena_con": "entrenamiento", "evalua_en": "validación",
                         "variantes": ["tobit_signo_correcto", "tobit_signo_invertido",
                                       "ridge_solo_exactas"]},
                 semillas=[SEMILLA],
                 datos=[PROCESADOS / "fase2_pares.parquet",
                        PROCESADOS / "fase2_descriptores_limpios.parquet"]) as corrida:
        _medir(corrida)


if __name__ == "__main__":
    main()
