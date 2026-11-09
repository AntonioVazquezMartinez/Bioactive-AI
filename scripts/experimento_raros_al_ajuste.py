#!/usr/bin/env python3
"""¿Mejora el `svm_rbf` en lo raro si el ajuste recibe química rara que hoy solo está en la prueba?
(decisión 1.11, fase 1)

**Toca la prueba reservada, con etiquetas**, a propósito: mover compuestos de la prueba al ajuste es el
experimento. Por eso este script está en `PERMITIDOS` de `tests/test_guarda_acceso_prueba.py` y pasa por
`tomar_prueba`, que deja la línea en `experimentos/prueba.csv`. **No cambia la partición del proyecto ni
el modelo entregado**: los resultados no se usan para elegir nada de lo que ya se midió en la prueba.

El diseño, los brazos y la regla están en la entrada 1.11 de `docs/decisiones.md`, escritos antes de
correr. Este script los aplica sin cambiarlos. El reparto está en `src/models/raros_al_ajuste.py`.

**Comprobaciones, antes de leer ningún resultado:**
1. los cuatro brazos usan el mismo núcleo de evaluación `E` y ningún grupo está a los dos lados;
2. `B`, `C` y `D` tienen el mismo tamaño de entrenamiento (salvo un grupo);
3. el brazo `A` es el `svm_rbf` del catálogo sobre el ajuste original, ajustado una sola vez;
4. cada tercil de `E` tiene al menos 20 casos de su clase minoritaria en suficientes sorteos; si no, la
   regla correspondiente no es evaluable y se dice.

**La regla** (la 1.11, sin retoques). Con `Δ_x` = AUROC del brazo `x` menos el de `A`, sobre las mismas
filas raras de `E`, en cada uno de los 15 sorteos, y `σ_C` la desviación de `Δ_C`:
1. `B` mejora lo raro si la media de `Δ_B` supera a max(0.005, σ_C) y es positiva en al menos 12 de 15;
2. no es solo «más datos»: la media de `Δ_B − Δ_C` es mayor que cero;
3. no cuesta lo común: la media de AUROC(B) − AUROC(A) en los comunes de `E` no baja de −0.005.

Los 15 sorteos comparten las mismas 1,499 filas de prueba: **no son 15 evaluaciones independientes**, y el
intervalo que se reporta es condicional a esta prueba.

    ./env312/bin/python scripts/experimento_raros_al_ajuste.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy import stats
from sklearn.base import clone
from sklearn.metrics import matthews_corrcoef, roc_auc_score

from src.models.alternativos import seleccion
from src.models.rareza_entrenamiento import matriz_similitud
from src.models.raros_al_ajuste import repartir, similitud_fuera_del_grupo, terciles_de_grupos
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida, tomar_prueba

SORTEOS = 15
MIN_MINORITARIA = 20
GANANCIA_MINIMA = 0.005       # regla 1: piso de la ganancia media en lo raro
SORTEOS_POSITIVOS = 12        # regla 1: en cuántos de 15 debe ganar
PERDIDA_MAXIMA = 0.005        # regla 3: lo que se permite perder en lo común
SORTEOS_EVALUABLES = 12       # una celda se lee si tiene ≥ 20 casos de la minoritaria en tantos sorteos
BRAZOS = ("B", "C", "D")
ROTULOS = {0: "raro", 1: "intermedio", 2: "comun"}
MOTIVO = ("1.11: pasar los raros de la prueba al ajuste y devolver comunes a la prueba; la prueba se "
          "reparte, no se evalúa con el modelo final")


def auroc(y, p):
    """AUROC, o NaN si la clase minoritaria no llega al mínimo."""
    if min(int(y.sum()), int((1 - y).sum())) < MIN_MINORITARIA:
        return np.nan
    return float(roc_auc_score(y, p))


def un_sorteo(r, X, y, particion, grupos, terc, pA):
    rep = repartir(particion, grupos, terc, r)
    filas = {"sorteo": r, "n_E": len(rep.evaluacion), "n_movidas_raras": len(rep.movidas_raras),
             "n_movidas_azar": len(rep.movidas_azar), "n_quitadas": len(rep.quitadas),
             "cruzados": rep.cruzados}
    for brazo in "BCD":
        filas[f"n_entrena_{brazo}"] = len(rep.entrenamiento(brazo))
    E, Q = rep.evaluacion, rep.quitadas
    evaluar_en = {k: E[terc[E] == k] for k in (0, 1, 2)}
    for k, e in evaluar_en.items():
        ys = y[e]
        filas[f"n_{ROTULOS[k]}"] = len(e)
        filas[f"minoritaria_{ROTULOS[k]}"] = int(min(ys.sum(), (1 - ys).sum()))
        filas[f"A_auroc_{ROTULOS[k]}"] = auroc(ys, pA[e])
    filas["A_auroc_E"] = auroc(y[E], pA[E])
    filas["A_mcc_E"] = float(matthews_corrcoef(y[E], (pA[E] >= 0.5).astype(int)))
    for brazo in BRAZOS:
        ent = rep.entrenamiento(brazo)
        modelo = clone(seleccion(("svm_rbf",))["svm_rbf"]).fit(X[ent], y[ent])
        pE = modelo.predict_proba(X[E])[:, 1]
        pQ = modelo.predict_proba(X[Q])[:, 1]
        p = np.zeros(len(y))
        p[E] = pE
        for k, e in evaluar_en.items():
            filas[f"{brazo}_auroc_{ROTULOS[k]}"] = auroc(y[e], p[e])
        filas[f"{brazo}_auroc_E"] = auroc(y[E], pE)
        filas[f"{brazo}_mcc_E"] = float(matthews_corrcoef(y[E], (pE >= 0.5).astype(int)))
        filas[f"{brazo}_auroc_Q"] = auroc(y[Q], pQ)
    return filas, rep


def resumen(d: np.ndarray) -> dict:
    """Media, desviación, IC95% de t (condicional a esta prueba), signos y peor sorteo."""
    d = d[~np.isnan(d)]
    n = len(d)
    if n < 2:
        return {"sorteos": n}
    media, desv = float(d.mean()), float(d.std(ddof=1))
    t = float(stats.t.ppf(0.975, n - 1))
    ee = desv / np.sqrt(n)
    return {"media": round(media, 4), "desviacion": round(desv, 4),
            "ic95_condicional": [round(media - t * ee, 4), round(media + t * ee, 4)],
            "sorteos": n, "positivos": int((d > 0).sum()), "peor": round(float(d.min()), 4)}


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano", incluir_prueba=True, motivo=MOTIVO)
    tomar_prueba(t.meta, final=True, motivo=MOTIVO)
    n = len(t.y)
    X, y = np.asarray(t.X, float), np.asarray(t.y)
    particion, grupos = t.meta["particion"].to_numpy(), np.asarray(t.grupos)
    tramo = np.asarray(t.estratos)
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"sorteos": SORTEOS, "filas": int(n), "toca_prueba": True,
              "regla": {"ganancia_minima": GANANCIA_MINIMA, "sorteos_positivos": SORTEOS_POSITIVOS,
                        "perdida_maxima_en_comunes": PERDIDA_MAXIMA, "min_minoritaria": MIN_MINORITARIA}}
    with Corrida("raros-al-ajuste-permeabilidad", decision="1.11", params=params,
                 semillas=list(range(SORTEOS)), datos=datos) as c:
        en_prueba = particion == "prueba"
        print(f"{n:,} filas · {len(np.unique(grupos)):,} grupos · {int(en_prueba.sum()):,} de prueba\n")
        sim = similitud_fuera_del_grupo(matriz_similitud(t.meta["SMILES"].to_numpy()), grupos)
        terc = terciles_de_grupos(sim, grupos, tramo)

        comp = pd.crosstab(np.where(en_prueba, "prueba", "ajuste"), terc)
        comp.columns = [ROTULOS[k] for k in comp.columns]
        print("composición por tercil de rareza (filas):\n", comp.to_string(), "\n")
        print("rareza media (similitud al vecino de otro grupo): "
              f"ajuste {sim[~en_prueba].mean():.3f} · prueba {sim[en_prueba].mean():.3f}\n")

        # El brazo A: el catálogo sobre el ajuste original, una sola vez; predice toda la prueba.
        ajuste = np.flatnonzero(~en_prueba)
        mA = clone(seleccion(("svm_rbf",))["svm_rbf"]).fit(X[ajuste], y[ajuste])
        pA = np.zeros(n)
        pA[en_prueba] = mA.predict_proba(X[en_prueba])[:, 1]
        print(f"A sobre toda la prueba: AUROC {roc_auc_score(y[en_prueba], pA[en_prueba]):.4f} "
              f"(el registrado es 0.7928)\n")

        salida = Parallel(n_jobs=4)(delayed(un_sorteo)(r, X, y, particion, grupos, terc, pA)
                                    for r in range(SORTEOS))
        sorteos = pd.DataFrame([s for s, _ in salida])
        rep0 = salida[0][1]

        tam = sorteos[["n_E", "n_movidas_raras", "n_movidas_azar", "n_quitadas", "n_entrena_B",
                       "n_entrena_C", "n_entrena_D"]].agg(["min", "mean", "max"]).round(0)
        print("comprobaciones 1 y 2 · tamaños por sorteo:\n", tam.to_string(), "\n")
        print("comprobación 4 · sorteos en que cada tercil de E llega a 20 casos de la minoritaria:")
        evaluables = {}
        for k in ROTULOS.values():
            evaluables[k] = int(sorteos[f"A_auroc_{k}"].notna().sum())
            print(f"  {k:10s} {evaluables[k]:2d} de {SORTEOS} · minoritaria "
                  f"{sorteos[f'minoritaria_{k}'].min()}–{sorteos[f'minoritaria_{k}'].max()}")

        def delta(brazo, k):
            return (sorteos[f"{brazo}_auroc_{k}"] - sorteos[f"A_auroc_{k}"]).to_numpy()

        efectos = {}
        for brazo in BRAZOS:
            for k in ROTULOS.values():
                efectos[f"{brazo}-A|{k}"] = resumen(delta(brazo, k))
            efectos[f"{brazo}-A|E"] = resumen(delta(brazo, "E"))
        efectos["B-C|raro"] = resumen(delta("B", "raro") - delta("C", "raro"))
        efectos["B-D|raro"] = resumen(delta("B", "raro") - delta("D", "raro"))
        efectos["B-D|Q"] = resumen((sorteos["B_auroc_Q"] - sorteos["D_auroc_Q"]).to_numpy())
        efectos["C-D|Q"] = resumen((sorteos["C_auroc_Q"] - sorteos["D_auroc_Q"]).to_numpy())
        for clave in ("B-A|raro", "C-A|raro", "D-A|raro", "B-C|raro", "B-A|intermedio", "B-A|comun",
                      "B-A|E", "B-D|Q"):
            print(f"  {clave:15s} {efectos[clave]}")

        sigma_c = efectos["C-A|raro"].get("desviacion", float("nan"))
        piso = max(GANANCIA_MINIMA, sigma_c)
        raro, comun, bc = efectos["B-A|raro"], efectos["B-A|comun"], efectos["B-C|raro"]
        ev_raro = evaluables["raro"] >= SORTEOS_EVALUABLES
        ev_comun = evaluables["comun"] >= SORTEOS_EVALUABLES
        r1 = bool(ev_raro and raro["media"] > piso and raro["positivos"] >= SORTEOS_POSITIVOS)
        r2 = bool(ev_raro and bc["media"] > 0)
        r3 = bool(ev_comun and comun["media"] >= -PERDIDA_MAXIMA)
        evaluable = bool(ev_raro and ev_comun)
        mejora = bool(evaluable and r1 and r2 and r3)
        print(f"\npiso de la regla 1 = max({GANANCIA_MINIMA}, σ_C={sigma_c:.4f}) = {piso:.4f}")
        print(f"regla 1 {r1} · regla 2 {r2} · regla 3 {r3} → B mejora lo raro: {mejora}"
              + ("" if evaluable else "  (NO evaluable: hay celdas con < 20 casos en muchos sorteos)"))

        c.metricas({
            "composicion_por_tercil": {str(i): {k: int(v) for k, v in fila.items()}
                                       for i, fila in comp.iterrows()},
            "rareza_media": {"ajuste": round(float(sim[~en_prueba].mean()), 4),
                             "prueba": round(float(sim[en_prueba].mean()), 4)},
            "auroc_A_sobre_toda_la_prueba": round(float(roc_auc_score(y[en_prueba], pA[en_prueba])), 4),
            "sorteos_evaluables": evaluables,
            "medias_por_brazo": {b: {k: round(float(sorteos[f"{b}_auroc_{k}"].mean()), 4)
                                     for k in (*ROTULOS.values(), "E")} for b in ("A", *BRAZOS)},
            "efectos": efectos, "sigma_C": round(float(sigma_c), 4), "piso_regla_1": round(float(piso), 4),
            "regla": {"regla_1": r1, "regla_2": r2, "regla_3": r3, "evaluable": evaluable,
                      "b_mejora_lo_raro": mejora},
        })
        sorteos.to_csv(c.carpeta / "sorteos.csv", index=False)

        # La partición alternativa del sorteo 0 con el brazo B: ajuste − Q + M_raro; prueba = el resto.
        nueva = np.where(np.isin(np.arange(n), rep0.entrenamiento("B")), "entrenamiento", "prueba")
        pd.DataFrame({
            "fila": np.arange(n), "grupo": grupos, "tercil_rareza": [ROTULOS[k] for k in terc],
            "particion_original": particion, "particion_alternativa": nueva,
            "movida_de_la_prueba": np.isin(np.arange(n), rep0.movidas_raras),
            "devuelta_a_la_prueba": np.isin(np.arange(n), rep0.quitadas),
            "nucleo_de_evaluacion": np.isin(np.arange(n), rep0.evaluacion),
        }).to_csv(c.carpeta / "particion_alternativa_sorteo0.csv", index=False)


if __name__ == "__main__":
    main()
