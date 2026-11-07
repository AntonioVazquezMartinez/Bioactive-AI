#!/usr/bin/env python3
"""Las características de la fase 2, con nombre: SHAP y permutación para la C.2.

Aplica los dos métodos independientes de atribución que la decisión C.2 exige
sobre el modelo de regresión AFT con huellas Sort & Slice:

1. **TreeSHAP (TreeExplainer):** Atribución interna del ensamble de árboles XGBoost.
   TreeSHAP explica la salida en escala de margen: ln(µM). La predicción final en
   pActividad se calcula como 6 − log10(µM) = 6 − ln(µM) / ln(10). Por tanto, un valor
   SHAP positivo en ln(µM) indica MAYOR concentración requerida (MENOR potencia).
   Para expresar la atribución en unidades directas de pActividad (donde mayor valor
   significa mayor potencia), el signo se invierte:
       shap_pActividad = - shap_ln_um / ln(10)
   Así, un valor positivo indica que la característica aumenta la potencia biológica.
   La magnitud global se resume como la media de |shap_pActividad|.

2. **Importancia por permutación:** Atribución agnóstica al modelo sobre el pliegue
   de validación, midiendo la caída en la métrica principal del proyecto: la
   concordancia de Harrell sobre el intervalo censurado.

La intersección de ambos métodos se identifica con `concordantes()` y se grafica con
`importancias_dos_metodos()` de `src/evaluation/graficos.py`.

El mapa de nombres traduce cada columna densa (201 descriptores + variables diana) y,
para cada columna j de huellas Sort & Slice, su identificador único Morgan
`identificadores[huellas_.columnas_[j]]` junto con sus subestructuras equivalentes
`equivalentes[huellas_.columnas_[j]]`.

Uso:
    ./env/bin/python scripts/atribucion_fase2.py [--humo]
"""
from __future__ import annotations

import math
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from scipy.stats import spearmanr
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedGroupKFold

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from scripts.experimento_aft_huellas import (DESCRIPTORES, PARES, datos)            # noqa: E402
from src.evaluation.graficos import concordantes, importancias_dos_metodos          # noqa: E402
from src.evaluation.regresion import concordancia_harrell                           # noqa: E402
from src.models.aft import RegresionAFT                                             # noqa: E402
from src.models.baseline_regresion import ConHuellasCensurado                       # noqa: E402
from src.tracking import Corrida, exigir_corrida_reproducible                       # noqa: E402

PLIEGUES = 5
REPETICIONES = 5
PRIMERAS = 15
N_BITS = 2048
RONDAS = 100
PROFUNDIDAD = 6
LN10 = math.log(10)
# El nombre de la columna del primer método. **No es `impureza`**: en la fase 1 esa columna
# lleva la ganancia interna de los árboles, y aquí lleva la media de |TreeSHAP| en
# pActividad. Dos corridas hermanas de la C.2 traían el mismo nombre con métodos distintos
# dentro, así que se pasa explícito a `concordantes()`.
COL_SHAP = "shap_media_abs"
# La permutación son 2,275 columnas x 5 repeticiones x 5 pliegues = 56,880 `predict`, y uno
# sobre 11,248 filas con los 100 árboles tarda 2.3 s con un solo hilo: 36 h. `OMP_NUM_THREADS=1`
# se queda (si no, los hilos de XGBoost y los de joblib se pisan) y el paralelismo va por
# columna, que es trivialmente paralelo. Medido en 8 núcleos: 4.5 h.
NUCLEOS = -1


def scorer_concordancia(estimator, X, y):
    """Evalúa la concordancia de Harrell sobre el intervalo [inferior, superior]."""
    pred = estimator.predict(X)
    return concordancia_harrell(y[:, 0], y[:, 1], pred)


def calcular_atribuciones(d: dict, *, rondas: int, n_bits: int, pliegues: int,
                          repeticiones: int, nucleos: int = NUCLEOS,
                          indices_filas: np.ndarray | None = None) -> tuple[pd.DataFrame, dict]:
    """Calcula SHAP y permutación pliegue a pliegue, mapeando nombres y equivalentes."""
    X_mixta = d["X_mixta"]
    inf = d["inferior"]
    sup = d["superior"]
    grupos = d["grupos"]
    clase = d["clase"]
    n_densas = d["n_densas"]
    n_desc = d["n_desc"]
    identificadores = d["identificadores"]
    equivalentes = d["equivalentes"]

    if indices_filas is not None:
        X_mixta = X_mixta[indices_filas]
        inf = inf[indices_filas]
        sup = sup[indices_filas]
        grupos = grupos[indices_filas]
        clase = clase[indices_filas]

    # Los nombres densos vienen de `datos()`, que los construye del mismo DataFrame del que
    # salen las columnas. Releer el parquet de pares para sacar las dianas, como se hacía
    # antes, los tomaba de **antes** del merge con los descriptores y del filtro `util`: hoy
    # los dos conjuntos coinciden (26 genes), pero un gen que solo viviera en las filas que
    # esos pasos tiran habría desplazado todos los nombres de diana en uno.
    nombres_densas = d["nombres_densas"]
    assert len(nombres_densas) == n_densas, (
        f"{len(nombres_densas)} nombres densos no coinciden con n_densas={n_densas}"
    )

    estratificar = np.where(np.isnan(clase), -1, clase).astype(int)
    cv = StratifiedGroupKFold(pliegues, shuffle=True, random_state=0)

    filas = []
    mapa_equivalentes: dict[str, str] = {}

    for k, (ajuste, val) in enumerate(cv.split(X_mixta, estratificar, grupos), 1):
        print(f"  Ajustando pliegue {k} de {pliegues}...", flush=True)
        t_ini = time.perf_counter()

        m = ConHuellasCensurado(
            RegresionAFT(rondas=rondas, profundidad=PROFUNDIDAD, semilla=k),
            n_densas=n_densas,
            n_bits=n_bits,
        )
        m.fit(X_mixta[ajuste], inf[ajuste], sup[ajuste])

        # Matriz densa transformada del pliegue de validación
        X_val_h = m.huellas_.transform(X_mixta[val])
        y_val_intervalo = np.column_stack([inf[val], sup[val]])

        # Mapear nombres de las columnas para este pliegue
        cols_huellas = m.huellas_.columnas_
        nombres_huellas = []
        for j_huella in range(len(cols_huellas)):
            idx_global = cols_huellas[j_huella]
            bit_id = identificadores[idx_global]
            nombre_h = f"huella_{bit_id}"
            nombres_huellas.append(nombre_h)
            eq = equivalentes[idx_global]
            if len(eq) > 1 and nombre_h not in mapa_equivalentes:
                mapa_equivalentes[nombre_h] = ", ".join(str(x) for x in eq)

        nombres_totales = nombres_densas + nombres_huellas
        assert len(nombres_totales) == X_val_h.shape[1]

        # 1. SHAP vía TreeExplainer sobre el booster de RegresionAFT
        booster = m.modelo.booster_
        explainer = shap.TreeExplainer(booster)
        shap_raw = explainer.shap_values(X_val_h)

        # Inversión de signo: predict hace 6 - log10(µM) = 6 - ln(µM)/ln(10).
        # Un delta positivo en ln(µM) es MENOS potente (más concentración).
        # Invertimos y escalamos para obtener el impacto en pActividad:
        shap_pactividad = -shap_raw / LN10
        shap_media_abs = np.abs(shap_pactividad).mean(axis=0)
        shap_direccion = shap_pactividad.mean(axis=0)

        # 2. Permutation Importance con concordancia de Harrell
        perm = permutation_importance(
            m.modelo,
            X_val_h,
            y_val_intervalo,
            scoring=scorer_concordancia,
            n_repeats=repeticiones,
            random_state=k,
            n_jobs=nucleos,
        )
        perm_mean = perm.importances_mean
        perm_std = perm.importances_std

        for j, nombre in enumerate(nombres_totales):
            tipo = "descriptor" if j < n_desc else ("diana" if j < n_densas else "huella")
            filas.append({
                "caracteristica": nombre,
                "indice": j,
                "tipo": tipo,
                "pliegue": k,
                "permutacion": float(perm_mean[j]),
                "permutacion_std": float(perm_std[j]),
                COL_SHAP: float(shap_media_abs[j]),
                "shap_direccion": float(shap_direccion[j]),
                "equivalentes": mapa_equivalentes.get(nombre, ""),
            })

        print(f"  Pliegue {k} completado en {time.perf_counter() - t_ini:.1f} s", flush=True)

    df_importancias = pd.DataFrame(filas)
    return df_importancias, mapa_equivalentes


def main() -> None:
    humo = "--humo" in sys.argv
    nucleos = NUCLEOS
    if "--nucleos" in sys.argv:
        nucleos = int(sys.argv[sys.argv.index("--nucleos") + 1])
    print(f"Iniciando atribución fase 2 (modo {'humo' if humo else 'completo'})...", flush=True)
    # Antes de los minutos de huellas Morgan, no después.
    exigir_corrida_reproducible(definitiva=not humo,
                                permitir_sucio=humo or "--arbol-sucio" in sys.argv)

    d = datos()
    n_desc = d["n_desc"]
    n_densas = d["n_densas"]
    assert n_desc == 201, f"n_desc esperado 201, se obtuvo {n_desc}"
    assert n_densas > n_desc, f"n_densas={n_densas} debe ser mayor que n_desc={n_desc}"

    if humo:
        # Muestra chica: 1,500 filas de ajuste, 10 rondas, 40 bits de huellas, 2 pliegues
        n_muestras = min(1500, len(d["inferior"]))
        rng = np.random.default_rng(0)
        indices_humo = rng.choice(len(d["inferior"]), size=n_muestras, replace=False)
        rondas = 10
        n_bits = 40
        pliegues = 2
        repeticiones = 2
    else:
        indices_humo = None
        rondas = RONDAS
        n_bits = N_BITS
        pliegues = PLIEGUES
        repeticiones = REPETICIONES

    params = {
        "modelo": "aft_huellas (ConHuellasCensurado + RegresionAFT)",
        "metodo_1": "TreeSHAP (TreeExplainer sobre booster_)",
        "metodo_2": "Permutation importance (caída en concordancia de Harrell)",
        "pliegues": pliegues,
        "repeticiones_permutacion": repeticiones,
        "rondas_arboles": rondas,
        "profundidad_arboles": PROFUNDIDAD,
        "n_bits_sortslice": n_bits,
        "humo": humo,
        "nucleos_permutacion": nucleos,
        "columna_metodo_1": COL_SHAP,
        "nota_columna": (
            "La columna del primer método se llama shap_media_abs y NO impureza: en la "
            "corrida de fase 1 esa columna lleva la ganancia interna de los árboles, que "
            "es otro método. Se pasa explícita a concordantes()."
        ),
        "interseccion_solo_en_todos_los_pliegues": True,
        "nota_pliegues": (
            "El vocabulario Sort & Slice se reaprende en cada pliegue, así que una huella "
            "puede no existir en todos. Promediar sobre distinto número de pliegues le da "
            "a esas una media más ruidosa que puede colarse en el top; la intersección se "
            "calcula solo sobre las características presentes en los %d pliegues." % pliegues
        ),
        "explicacion_signo": (
            "TreeSHAP explica ln(µM). Dado que pActividad = 6 - ln(µM)/ln(10), "
            "un delta positivo en ln(µM) indica menor potencia. El signo de SHAP se "
            "invierte (-shap/ln(10)) para que positivo signifique mayor potencia biológica."
        ),
        "nota_matriz": (
            "Corrida ejecutada sobre matriz local (sha256 en datos_sha256); no es "
            "comparable fila a fila con la de Ingrid y por eso el control se repitió."
        ),
    }

    nombre = "atribucion-fase2-con-nombres" + ("-humo" if humo else "")
    if humo:
        c_check = Corrida(nombre, decision="C.2", params=params, semillas=[0])
        if c_check.carpeta.exists():
            import shutil
            shutil.rmtree(c_check.carpeta)

    with Corrida(nombre, decision="C.2", params=params,
                 semillas=[0], datos=[PARES, DESCRIPTORES]) as c:
        df_imp, mapa_eq = calcular_atribuciones(
            d, rondas=rondas, n_bits=n_bits, pliegues=pliegues,
            repeticiones=repeticiones, nucleos=nucleos, indices_filas=indices_humo,
        )
        # `n_pliegues` por característica, porque no todas están en todos: el vocabulario
        # Sort & Slice se reaprende en cada pliegue (y así debe ser, o la validación
        # decidiría qué columnas existen). Queda en el CSV para que se pueda auditar.
        n_pliegues = df_imp.groupby("caracteristica")["pliegue"].transform("nunique")
        df_imp["n_pliegues"] = n_pliegues
        df_imp.to_csv(c.carpeta / "importancias.csv", index=False)

        # **La intersección se calcula solo sobre las completas.** Una media de 1 pliegue y
        # una de 5 no son comparables, y la de 1 es la más ruidosa, así que ordenarlas juntas
        # premia a las huellas raras justo en el top que la C.2 reporta. Las incompletas se
        # quedan en el CSV; lo que no hacen es entrar en la afirmación estructural.
        completas = df_imp[df_imp["n_pliegues"] == pliegues]
        n_fuera = df_imp["caracteristica"].nunique() - completas["caracteristica"].nunique()
        print(f"\ncaracterísticas en los {pliegues} pliegues: "
              f"{completas['caracteristica'].nunique():,}; fuera de la intersección por "
              f"aparecer en menos: {n_fuera:,}")

        # Resumen promedio por característica
        medias = completas.groupby("caracteristica", as_index=False).agg({
            "permutacion": "mean",
            COL_SHAP: "mean",
            "shap_direccion": "mean",
            "tipo": "first",
            "equivalentes": "first",
        })
        medias["r_perm"] = medias["permutacion"].rank(ascending=False)
        medias["r_shap"] = medias[COL_SHAP].rank(ascending=False)

        inter = concordantes(completas, n=PRIMERAS, columna=COL_SHAP)

        # El Spearman sobre la unión de los 100 primeros de cada método es la regla con la
        # que la corrida 2.13 juzgó el acuerdo, así que se registra para poder comparar.
        union = pd.concat([medias.nlargest(100, COL_SHAP),
                           medias.nlargest(100, "permutacion")])
        union = union.drop_duplicates(subset="caracteristica")
        rho_union = float(spearmanr(union[COL_SHAP], union["permutacion"]).statistic)

        # Generar gráfico con las dos atribuciones y la concordancia marcada
        fig, ax = plt.subplots(figsize=(8, 6))
        importancias_dos_metodos(completas, ax=ax, n=PRIMERAS, columna=COL_SHAP)
        ax.set_title(
            f"Fase 2: Caída de concordancia al permutar (azul fuerte: también en top {PRIMERAS} SHAP)",
            fontsize="small",
        )
        plt.tight_layout()
        fig.savefig(c.carpeta / "importancias_dos_metodos.png", dpi=150)
        plt.close(fig)

        # Contraste de descriptores clave (C.2)
        contraste_c2 = {}
        for feat in ("TPSA", "NumHDonors", "MolLogP", "MolWt"):
            if feat in medias["caracteristica"].values:
                fila = medias[medias["caracteristica"] == feat].iloc[0]
                contraste_c2[feat] = {
                    "puesto_permutacion": int(fila["r_perm"]),
                    "puesto_shap": int(fila["r_shap"]),
                    "caida_concordancia": round(float(fila["permutacion"]), 5),
                    "shap_media_abs_pActividad": round(float(fila[COL_SHAP]), 5),
                    "shap_direccion_pActividad": round(float(fila["shap_direccion"]), 5),
                }

        c.metricas({
            "interseccion": {
                feat: {
                    "tipo": str(medias.loc[medias["caracteristica"] == feat, "tipo"].iloc[0]),
                    "puesto_permutacion": int(medias.loc[medias["caracteristica"] == feat, "r_perm"].iloc[0]),
                    "puesto_shap": int(medias.loc[medias["caracteristica"] == feat, "r_shap"].iloc[0]),
                    "permutacion": round(float(medias.loc[medias["caracteristica"] == feat, "permutacion"].iloc[0]), 5),
                    "shap_media_abs": round(float(medias.loc[medias["caracteristica"] == feat, COL_SHAP].iloc[0]), 5),
                    "shap_direccion": round(float(medias.loc[medias["caracteristica"] == feat, "shap_direccion"].iloc[0]), 5),
                    "equivalentes": str(medias.loc[medias["caracteristica"] == feat, "equivalentes"].iloc[0]),
                }
                for feat in inter
            },
            "n_en_interseccion": len(inter),
            "spearman_union_top100": round(rho_union, 3),
            "n_en_union_top100": int(len(union)),
            "contraste_c2": contraste_c2,
            "caracteristicas_en_todos_los_pliegues": int(completas["caracteristica"].nunique()),
            "caracteristicas_fuera_por_pliegues_incompletos": int(n_fuera),
        })

    print(f"\ncorrida guardada en: experimentos/{c.id}")
    print(f"\n=== Las {PRIMERAS} primeras por Permutación (caída de concordancia) ===")
    print(medias.nsmallest(PRIMERAS, "r_perm")[
        ["caracteristica", "tipo", "permutacion", COL_SHAP, "shap_direccion"]
    ].to_string(index=False, float_format=lambda v: f"{v:+.5f}"))

    print(f"\n=== Las {PRIMERAS} primeras por TreeSHAP (|d pActividad|) ===")
    print(medias.nsmallest(PRIMERAS, "r_shap")[
        ["caracteristica", "tipo", COL_SHAP, "permutacion", "shap_direccion"]
    ].to_string(index=False, float_format=lambda v: f"{v:+.5f}"))

    print(f"\n=== Intersección concordante C.2 ({len(inter)} de {PRIMERAS}) ===")
    if inter:
        sub_inter = medias[medias["caracteristica"].isin(inter)].sort_values("r_perm")
        print(sub_inter[["caracteristica", "tipo", "permutacion", COL_SHAP, "shap_direccion", "equivalentes"]]
              .to_string(index=False, float_format=lambda v: f"{v:+.5f}"))
    else:
        print("  (Ninguna coincidencia en el top 15)")

    print("\n=== Contraste estructural exigido por la C.2 y verificación del signo ===")
    for feat, vals in contraste_c2.items():
        signo_str = "AUMENTA potencia" if vals["shap_direccion_pActividad"] > 0 else "REDUCE potencia"
        print(
            f"  {feat:<12} puesto perm {vals['puesto_permutacion']:3d} | "
            f"puesto SHAP {vals['puesto_shap']:3d} | "
            f"dir SHAP: {vals['shap_direccion_pActividad']:+.4f} ({signo_str})"
        )


if __name__ == "__main__":
    main()
