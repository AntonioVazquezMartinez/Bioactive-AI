#!/usr/bin/env python3
"""¿Entrenar con más peso en la química rara mejora al `svm_rbf` en lo raro sin empeorarlo en lo parecido?
(decisión 1.10, fase 1)

El diseño, los pesos y la regla están declarados en la entrada 1.10 de `docs/decisiones.md`, antes de
correr. Este script los aplica sin cambiarlos. **No toca la prueba reservada**: `cargar` por omisión
excluye esas filas, y este archivo no está ni debe estar en `PERMITIDOS`.

**Qué se mide.** El mismo `svm_rbf` del catálogo, los mismos datos y las mismas 15 evaluaciones
agrupadas (`grupos_cv`, 5 pliegues × 3 semillas) en cuatro brazos (`src/models/rareza_entrenamiento.py`):
`A` referencia, `B` pesos 3, 2 y 1 por tercil de rareza, `C` lo mismo duplicando filas y `D` los mismos
pesos barajados dentro de su tramo. Los terciles de **validación** se toman dentro de cada pliegue y de
cada tramo de peso, con la similitud al vecino más cercano del ajuste de ese pliegue.

**Comprobaciones, antes de leer nada:**
1. el brazo `A` y el `svm_rbf` del catálogo dan el mismo MCC en cada evaluación (es el mismo modelo);
2. los terciles de validación tienen tamaño parecido y su clase minoritaria llega a 20 casos en las 15
   evaluaciones. Si no, la regla no es evaluable y se dice.

**La regla** (la 1.10, sin retoques). `B` *sirve* si se cumplen las tres:
1. la ganancia de AUROC contra `A` en el tercil más raro es positiva en al menos 12 de las 15
   evaluaciones y su media supera 0.005;
2. en el tercil más parecido la media no pierde más de 0.005 y la pérdida no pasa de 0.010 en más de 3
   de las 15 evaluaciones;
3. en el tercil más raro, `B` supera a `D` por una media mayor que cero.

`C` se reporta como contraste del mecanismo y no decide. El AUROC y el MCC globales y el tercil
intermedio se reportan sin criterio. Si la regla no se cumple, se dice y no se afina nada.

    ./env312/bin/python scripts/experimento_rareza_en_entrenamiento.py
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
from scipy import stats
from sklearn.metrics import matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.rareza_entrenamiento import (
    BRAZOS, SVMRareza, fijar_contexto, matriz_similitud, rareza_de_validacion, terciles_en_tramos)
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
MIN_MINORITARIA = 20
GANANCIA_MINIMA = 0.005        # regla 1: media mínima en el tercil más raro
PERDIDA_MAXIMA = 0.005         # regla 2: pérdida media permitida en el más parecido
PERDIDA_SUELTA = 0.010         # regla 2: pérdida de una evaluación que cuenta
MAX_PERDIDAS_SUELTAS = 3       # regla 2: cuántas evaluaciones pueden pasarla
MIN_EVALUACIONES = 12          # regla 1: en cuántas de 15 debe ganar
ROTULOS = {0: "raro", 1: "intermedio", 2: "parecido"}


def intervalo_nb(dif: np.ndarray) -> dict:
    """Media, desviación pareada y el IC del 95% corregido por Nadeau y Bengio (J evaluaciones, k pliegues)."""
    dif = dif[~np.isnan(dif)]
    j = len(dif)
    media, desv = float(dif.mean()), float(dif.std(ddof=1))
    ee = desv * np.sqrt(1 / j + (1 / PLIEGUES) / (1 - 1 / PLIEGUES))
    t = float(stats.t.ppf(0.975, j - 1))
    return {"media": round(media, 4), "desviacion": round(desv, 4),
            "ic95": [round(media - t * ee, 4), round(media + t * ee, 4)],
            "evaluaciones": j, "positivas": int((dif > 0).sum()),
            "perdidas_mayores_a_0.010": int((dif < -PERDIDA_SUELTA).sum()),
            "peor": round(float(dif.min()), 4)}


def medidas_por_tercil(t, oof, brazos) -> pd.DataFrame:
    """AUROC y MCC por (brazo, semilla, pliegue, tercil de rareza de la validación)."""
    X, y, g, tramo = np.asarray(t.X), np.asarray(t.y), np.asarray(t.grupos), np.asarray(t.estratos)
    filas = []
    for s, semilla in enumerate(SEMILLAS):
        cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
        for pliegue, (ajuste, val) in enumerate(cv.split(X, y, g), 1):
            sim = rareza_de_validacion(ajuste, val)
            terc = terciles_en_tramos(sim, tramo[val])
            for k in range(3):
                sel = terc == k
                ys = y[val][sel]
                ok = min(int(ys.sum()), int((1 - ys).sum())) >= MIN_MINORITARIA
                for b in brazos:
                    p = oof[b][s, val][sel]
                    filas.append({
                        "brazo": b, "semilla": semilla, "pliegue": pliegue, "tercil": ROTULOS[k],
                        "n": int(sel.sum()), "minoritaria": int(min(ys.sum(), (1 - ys).sum())),
                        "similitud_media": float(sim[sel].mean()),
                        "auroc": roc_auc_score(ys, p) if ok else np.nan,
                        "mcc": matthews_corrcoef(ys, (p >= 0.5).astype(int)) if ok else np.nan})
    return pd.DataFrame(filas)


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    n = len(t.y)
    smiles = t.meta["SMILES"].to_numpy()
    X_aug = np.hstack([np.asarray(t.X, float), np.arange(n, dtype=float)[:, None]])
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"brazos": list(BRAZOS), "pesos_por_tercil": [3, 2, 1], "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "filas": int(n), "toca_prueba": False,
              "regla": {"ganancia_minima": GANANCIA_MINIMA, "evaluaciones_minimas": MIN_EVALUACIONES,
                        "perdida_maxima": PERDIDA_MAXIMA, "perdida_suelta": PERDIDA_SUELTA,
                        "max_perdidas_sueltas": MAX_PERDIDAS_SUELTAS}}
    with Corrida("rareza-en-el-entrenamiento-permeabilidad", decision="1.10", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        print(f"{n:,} filas · {len(np.unique(t.grupos)):,} grupos · {t.y.mean():.1%} BBB+\n")
        fijar_contexto(matriz_similitud(smiles), t.estratos, t.grupos)

        # El control: el catálogo tal cual, con la matriz sin la columna de índice.
        res_cat, _ = evaluar({"catalogo": seleccion(("svm_rbf",))["svm_rbf"]}, t.X, t.y, t.grupos,
                             semillas=SEMILLAS, verboso=False)
        res, oof = evaluar({b: SVMRareza(brazo=b) for b in BRAZOS}, X_aug, t.y, t.grupos,
                           semillas=SEMILLAS, verboso=True)
        todos = res[res["estrato"] == "todos"].set_index(["modelo", "semilla", "pliegue"])
        cat = res_cat[res_cat["estrato"] == "todos"].set_index(["modelo", "semilla", "pliegue"])

        # Comprobación 1: A es el catálogo.
        d_cat = float(np.abs(todos.loc["A"]["mcc"].to_numpy()
                             - cat.loc["catalogo"]["mcc"].to_numpy()).max())
        print(f"comprobación 1 · máx |MCC(A) − MCC(catálogo)|: {d_cat:.2e}")
        if d_cat > 1e-9:
            raise SystemExit("el brazo A no reproduce el catálogo; el resto no se lee")

        # Medidas por tercil de rareza de la validación.
        m = medidas_por_tercil(t, oof, BRAZOS)
        tam = m[m["brazo"] == "A"].groupby("tercil")[["n", "minoritaria", "similitud_media"]].agg(
            ["min", "mean", "max"]).round(3)
        print("\ncomprobación 2 · tamaño de los terciles y su clase minoritaria:\n", tam.to_string())
        evaluable = bool(m["auroc"].notna().all())
        print("todas las celdas con ≥ 20 casos de la minoritaria:", evaluable)

        ancho = m.pivot_table(index=["semilla", "pliegue", "tercil"], columns="brazo",
                              values=["auroc", "mcc"])

        def diferencia(a, b, metrica, tercil):
            d = ancho[metrica][a] - ancho[metrica][b]
            return d.xs(tercil, level="tercil").to_numpy()

        efectos = {}
        for (a, b) in [("B", "A"), ("D", "A"), ("C", "A"), ("B", "D")]:
            for tercil in ("raro", "intermedio", "parecido"):
                for metrica in ("auroc", "mcc"):
                    efectos[f"{a}-{b}|{tercil}|{metrica}"] = intervalo_nb(
                        diferencia(a, b, metrica, tercil))
        globales = {}
        for (a, b) in [("B", "A"), ("D", "A"), ("C", "A")]:
            for metrica in ("auroc", "mcc"):
                d = (todos.loc[a][metrica] - todos.loc[b][metrica]).to_numpy()
                globales[f"{a}-{b}|todos|{metrica}"] = intervalo_nb(d)

        print("\nB − A en AUROC, por tercil de rareza:")
        for tercil in ("raro", "intermedio", "parecido"):
            print(f"  {tercil:10s} {efectos[f'B-A|{tercil}|auroc']}")
        print("B − D en AUROC, tercil raro:", efectos["B-D|raro|auroc"])
        print("global B − A:", globales["B-A|todos|auroc"], globales["B-A|todos|mcc"])

        # La regla, tal como está escrita en la 1.10.
        raro, parecido = efectos["B-A|raro|auroc"], efectos["B-A|parecido|auroc"]
        control = efectos["B-D|raro|auroc"]
        r1 = raro["positivas"] >= MIN_EVALUACIONES and raro["media"] > GANANCIA_MINIMA
        r2 = (parecido["media"] >= -PERDIDA_MAXIMA
              and parecido["perdidas_mayores_a_0.010"] <= MAX_PERDIDAS_SUELTAS)
        r3 = control["media"] > 0
        sirve = bool(evaluable and r1 and r2 and r3)
        print(f"\nregla 1 {r1} · regla 2 {r2} · regla 3 {r3} → B sirve: {sirve}"
              + ("" if evaluable else "  (NO evaluable: hay celdas con < 20 casos)"))

        c.metricas({
            "control_A_vs_catalogo_max_abs_dmcc": d_cat,
            "evaluable": evaluable,
            "medias_globales": {b: {k: round(float(v), 4) for k, v in
                                    todos.loc[b][["auroc", "mcc", "auprc_minoritaria",
                                                  "exactitud_balanceada"]].mean().items()}
                                for b in BRAZOS},
            "efectos_por_tercil": efectos,
            "efectos_globales": globales,
            "regla": {"regla_1": bool(r1), "regla_2": bool(r2), "regla_3": bool(r3),
                      "b_sirve": sirve},
        })
        m.to_csv(c.carpeta / "terciles.csv", index=False)
        res.to_csv(c.carpeta / "pliegues.csv", index=False)


if __name__ == "__main__":
    main()
