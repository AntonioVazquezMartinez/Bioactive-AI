#!/usr/bin/env python3
"""¿El modelo de la fase 2 aprende la actividad o aprende la fuente?

Evidencia de la decisión [2.3](../docs/decisiones.md#d2-3), que etiqueta las
tres bases con el mismo corte, y del [issue #32]. Es la condición que esa
decisión se impuso a sí misma: **ninguna cifra por fuente se cita antes de
correr esto**.

## El riesgo, y por qué no basta con mirarlo

Los pares que solo tiene ChEMBL son 75.8%% activos y los que solo tiene NPASS,
14.0%%. Sesenta y tres puntos. Hay dos explicaciones y la brecha no las separa:

1. **Química real.** Los productos naturales que se midieron son menos potentes
   sobre estas dianas, o se midieron a concentraciones más altas.
2. **Atajo.** La procedencia está tan correlacionada con la etiqueta que a un
   modelo le basta reconocer de qué base viene el compuesto.

Lo que las separa es medir **cuánto de la etiqueta se puede predecir sin
química**. Eso es lo que hace este script, con tres modelos sobre la misma
partición y la misma validación cruzada agrupada:

| Modelo | Qué ve | Qué significa que acierte |
|:--|:--|:--|
| **procedencia** | solo el estrato (`solo_chembl`, `solo_npass`, `mixto`) | el techo de lo que se consigue sin mirar la molécula |
| **química** | los 201 descriptores de RDKit | lo que se quiere: estructura → actividad |
| **ambos** | descriptores + estrato | si sube sobre química, el estrato aporta algo que la química no tiene |

**La comparación que decide es «procedencia» contra «química».** Si el modelo
que solo ve la fuente se acerca al que ve química, la fuente está filtrando la
etiqueta y la 2.3 se revierte a «solo ChEMBL». Si queda muy por debajo, la
brecha de 63 puntos es química y no atajo.

## Y una segunda medición, que es la que de verdad importa

El atajo podría estar escondido: un modelo con química puede *inferir* la
procedencia (los productos naturales tienen esqueletos distintos) y usarla como
atajo sin que la columna exista. Por eso se mide también el desempeño
**dentro de cada estrato por separado**. Un modelo que aprendió química acierta
en los dos; uno que aprendió procedencia se desploma dentro de cada uno, porque
ahí ya no hay fuente que distinguir.

Esta segunda parte es la que contesta la pregunta del proyecto —si el modelo
sirve para productos naturales— y no se puede leer de la primera.

## Dos correcciones de la primera versión

La primera versión concluyó que «el modelo no funciona sobre los naturales»
con un AUROC de 0.569 dentro de `solo_npass`, y Pame señaló dos problemas al
revisar el [#90]:

1. **El modelo no recibe la diana**, solo los descriptores. Dentro de
   `solo_npass` conviven dianas con tasas base muy distintas, así que ese
   0.569 mezclaba «no separa naturales» con «no sabe de qué diana se trata».
   Esta versión compara **ChEMBL contra NPASS a igual diana**, en las siete que
   tienen al menos 100 pares de NPASS y las dos clases, y añade un cuarto
   conjunto de características con la diana dentro.
2. **Tres semillas sobre los mismos pares no son tres réplicas.** La
   desviación entre los 15 pliegues no es un error estándar y no sirve para
   decir si algo se distingue de 0.5. Los intervalos salen de un **bootstrap
   por grupos** —se remuestrean los grupos de la partición, no las filas, que
   es la unidad independiente— sobre las predicciones fuera de pliegue.

Salida: `notebooks/datos/resultados_atajo.csv` con las métricas por corte y
`notebooks/datos/atajo_por_diana.csv` con la comparación por diana, los dos
versionados, y una corrida en `experimentos/`. Tarda unos 5 minutos.

    python scripts/experimento_atajo.py
"""
import platform
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold

from tracking import Corrida

PROCESADOS = RAIZ / "data/processed"
SALIDA = RAIZ / "notebooks/datos/resultados_atajo.csv"
SEMILLAS = (0, 1, 2)
PLIEGUES = 5
ESTRATOS = ("solo_chembl", "solo_npass", "mixto")
SALIDA_DIANA = RAIZ / "notebooks/datos/atajo_por_diana.csv"
# Una diana entra a la comparación por el tamaño de su **clase minoritaria**,
# no por el de la diana. Exigir solo pares deja pasar casos vacíos: `ACHE`
# tiene 221 pares de NPASS y **3 activos**, así que su AUROC es ruido —y en una
# primera versión de esta tabla salía 0.763, que parecía tranquilizador—. Lo
# señaló Pame al revisar el #90.
MIN_PARES = 100
MIN_MINORITARIA = 20
REMUESTRAS = 2000


def auroc_con_intervalo(y: np.ndarray, p: np.ndarray, grupos: np.ndarray,
                        semilla: int = 0) -> tuple[float, float, float]:
    """AUROC y su intervalo del 95%, remuestreando **grupos** y no filas.

    La fila no es la unidad independiente: los pares del mismo andamio comparten
    química y van juntos en la partición. Un bootstrap sobre filas daría un
    intervalo demasiado estrecho, que es la forma fácil de concluir que algo se
    distingue del azar cuando no se distingue.
    """
    if len(np.unique(y)) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(semilla)
    unicos = np.unique(grupos)
    por_grupo = {g: np.flatnonzero(grupos == g) for g in unicos}
    muestras = []
    for _ in range(REMUESTRAS):
        elegidos = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([por_grupo[g] for g in elegidos])
        if len(np.unique(y[idx])) < 2:
            continue
        muestras.append(roc_auc_score(y[idx], p[idx]))
    if not muestras:
        return roc_auc_score(y, p), float("nan"), float("nan")
    lo, hi = np.percentile(muestras, [2.5, 97.5])
    return roc_auc_score(y, p), float(lo), float(hi)


def modelo(semilla: int) -> RandomForestClassifier:
    """Random Forest, que es el que menos supuestos impone sobre la escala.

    El mismo para los tres conjuntos de características: si cambiara entre
    ellos, la comparación mezclaría el efecto del modelo con el de lo que ve.
    """
    return RandomForestClassifier(n_estimators=200, random_state=semilla,
                                  n_jobs=-1, min_samples_leaf=2)


def metricas(y: np.ndarray, puntuacion: np.ndarray) -> dict:
    """MCC, AUPRC sobre la clase minoritaria y AUROC, como pide la C.1.

    La clase minoritaria de la fase 2 es la **inactiva** (27.2%% con 10 µM), al
    revés que en la fase 1, así que el AUPRC se calcula sobre `1 - y`.
    """
    return {"mcc": matthews_corrcoef(y, (puntuacion >= 0.5).astype(int)),
            "auprc_minoritaria": average_precision_score(1 - y, 1 - puntuacion),
            "auroc": roc_auc_score(y, puntuacion)}


def main() -> None:
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    # La corrida envuelve el cálculo entero y no solo el registro de métricas: el
    # entorno se captura al empezar, antes de escribir el CSV, que es lo que
    # `experimentos/README.md` pide para que `arbol_sucio` describa el árbol con
    # el que se midió y no el que el propio script ensució.
    with Corrida("atajo-procedencia", decision="2.3",
                 params={"modelo": "RandomForest(200, min_samples_leaf=2)",
                         "pliegues": PLIEGUES, "semillas": list(SEMILLAS),
                         "umbral_um": 10.0,
                         "conjuntos": ["procedencia", "química", "ambos"]},
                 semillas=list(SEMILLAS),
                 datos=[PROCESADOS / "fase2_pares.parquet",
                        PROCESADOS / "fase2_descriptores_limpios.parquet"]) as corrida:
        _medir(corrida)


def _medir(corrida: Corrida) -> None:
    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")

    # Entrenamiento y validación; la prueba reservada no se toca (2.7).
    d = pares[pares["activo_10um"].notna() & pares["particion"].ne("prueba")]
    d = d.merge(desc, on="smiles", how="inner").reset_index(drop=True)
    y = d["activo_10um"].astype(int).to_numpy()
    grupos = d["grupo_cv"].to_numpy()
    estrato = d["estrato"].to_numpy()
    diana = d["target_gene"].to_numpy()

    columnas = [c for c in desc.columns if c != "smiles"]
    X_quimica = d[columnas].to_numpy(dtype=np.float32)
    # El estrato como indicadores: es todo lo que un modelo «de procedencia» ve.
    X_fuente = pd.get_dummies(d["estrato"]).reindex(
        columns=ESTRATOS, fill_value=False).to_numpy(dtype=np.float32)
    # La diana como indicadores. Sin ella el modelo no sabe contra qué se mide,
    # y las tasas base por diana van de 34.8% a 96.9%, así que parte de lo que
    # parece «no separa» puede ser «no sabe de qué diana se trata».
    X_diana = pd.get_dummies(d["target_gene"]).to_numpy(dtype=np.float32)
    conjuntos = {
        "procedencia": X_fuente,
        "química": X_quimica,
        "química+diana": np.hstack([X_quimica, X_diana]),
        "ambos": np.hstack([X_quimica, X_fuente]),
    }

    print(f"{len(d):,} pares · {len(columnas)} descriptores · "
          f"{d['grupo_cv'].nunique():,} grupos · {y.mean():.1%} activos", flush=True)

    # --- validación cruzada, guardando la predicción fuera de pliegue --------
    # Cada par recibe exactamente una predicción por semilla y conjunto, hecha
    # por un modelo que no lo vio. Son las que permiten cortar después por
    # diana y por estrato sin reentrenar, y las que alimentan el bootstrap.
    filas = []
    fdp = {n: np.full((len(SEMILLAS), len(y)), np.nan) for n in conjuntos}
    for s, semilla in enumerate(SEMILLAS):
        cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
        for pliegue, (ajuste, val) in enumerate(cv.split(X_quimica, y, grupos), 1):
            for nombre, X in conjuntos.items():
                clf = modelo(semilla).fit(X[ajuste], y[ajuste])
                p = clf.predict_proba(X[val])[:, 1]
                fdp[nombre][s, val] = p
                filas.append({"semilla": semilla, "pliegue": pliegue,
                              "conjunto": nombre, "estrato": "todos",
                              "n": len(val), **metricas(y[val], p)})
                for e in ESTRATOS:
                    sel = estrato[val] == e
                    if sel.sum() < 50 or len(np.unique(y[val][sel])) < 2:
                        continue
                    filas.append({"semilla": semilla, "pliegue": pliegue,
                                  "conjunto": nombre, "estrato": e,
                                  "n": int(sel.sum()), **metricas(y[val][sel], p[sel])})
            print(f"  semilla {semilla} pliegue {pliegue} listo", flush=True)

    res = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA, index=False)
    print(f"\n[guardado] {SALIDA.relative_to(RAIZ)}")

    # Las predicciones se promedian entre semillas: tres semillas sobre los
    # mismos pares no son tres réplicas, así que no dan un error estándar, pero
    # promediarlas sí reduce la varianza del propio Random Forest.
    medias = {n: np.nanmean(v, axis=0) for n, v in fdp.items()}

    global_ = res[res["estrato"].eq("todos")].groupby("conjunto")["mcc"].mean()
    brecha = global_["química"] - global_["procedencia"]
    print(f"\nMCC sobre todo el conjunto · procedencia {global_['procedencia']:.4f}"
          f" · química {global_['química']:.4f}"
          f" · química+diana {global_['química+diana']:.4f}"
          f" · ambos {global_['ambos']:.4f}")
    print(f"La química supera a la procedencia por {brecha:.4f} de MCC."
          " El control dispararía si fuera pequeña")

    # --- AUROC por estrato, con intervalo por bootstrap de grupos -----------
    print("\nAUROC por estrato, intervalo del 95% remuestreando grupos")
    por_estrato = []
    for nombre in conjuntos:
        for e in ("todos", *ESTRATOS):
            sel = np.ones(len(y), bool) if e == "todos" else (estrato == e)
            if sel.sum() < MIN_PARES or len(np.unique(y[sel])) < 2:
                continue
            a, lo, hi = auroc_con_intervalo(y[sel], medias[nombre][sel], grupos[sel])
            por_estrato.append({"conjunto": nombre, "estrato": e, "n": int(sel.sum()),
                                "activos": float(y[sel].mean()),
                                "auroc": a, "ic_bajo": lo, "ic_alto": hi})
            if nombre in ("química", "química+diana"):
                print(f"  {nombre:<14} {e:<12} n={sel.sum():>6,}"
                      f"  activos {y[sel].mean():>5.1%}"
                      f"  AUROC {a:.3f}  [{lo:.3f}, {hi:.3f}]")

    # --- Y la comparación que separa las dos explicaciones ------------------
    # A igual diana, ¿separa el modelo los pares de NPASS tan bien como los de
    # ChEMBL? Si sí, el 0.569 agregado era composición de dianas; si no, el
    # modelo no sirve para naturales y hay que decirlo.
    print(f"\nA igual diana, ChEMBL contra NPASS (≥{MIN_PARES} pares y"
          f" ≥{MIN_MINORITARIA} casos de la clase minoritaria en cada fuente)")
    por_diana = []
    for g in sorted(set(diana)):
        for e in ("solo_chembl", "solo_npass"):
            sel = (diana == g) & (estrato == e)
            if sel.sum() < MIN_PARES or len(np.unique(y[sel])) < 2:
                continue
            minoritaria = min(int(y[sel].sum()), int((1 - y[sel]).sum()))
            if minoritaria < MIN_MINORITARIA:
                continue
            for conjunto in ("química", "química+diana"):
                a, lo, hi = auroc_con_intervalo(y[sel], medias[conjunto][sel], grupos[sel])
                por_diana.append({"diana": g, "estrato": e, "conjunto": conjunto,
                                  "n": int(sel.sum()), "minoritaria": minoritaria,
                                  "activos": float(y[sel].mean()),
                                  "auroc": a, "ic_bajo": lo, "ic_alto": hi})
    pdi = pd.DataFrame(por_diana)
    # Solo las dianas donde se puede comparar: las dos fuentes presentes.
    completas = pdi.groupby("diana")["estrato"].nunique().loc[lambda s: s == 2].index
    pdi = pdi[pdi["diana"].isin(completas)]
    pdi.to_csv(SALIDA_DIANA, index=False)
    print(f"[guardado] {SALIDA_DIANA.relative_to(RAIZ)}\n")
    for conjunto in ("química", "química+diana"):
        print(f"\n  con {conjunto}:")
        sub = pdi[pdi.conjunto.eq(conjunto)]
        for g in completas:
            f = sub[sub.diana.eq(g)].set_index("estrato")
            print(f"    {g:<8}"
                  + "   ".join(
                      f"{e.replace('solo_', ''):<6} n={int(f.loc[e, 'n']):>5,}"
                      f" min={int(f.loc[e, 'minoritaria']):>4}"
                      f" AUROC {f.loc[e, 'auroc']:.3f}"
                      f" [{f.loc[e, 'ic_bajo']:.3f}, {f.loc[e, 'ic_alto']:.3f}]"
                      for e in ("solo_chembl", "solo_npass")))

    pe = pd.DataFrame(por_estrato).set_index(["conjunto", "estrato"])
    corrida.metricas({
        "mcc_procedencia": float(global_["procedencia"]),
        "mcc_quimica": float(global_["química"]),
        "mcc_quimica_diana": float(global_["química+diana"]),
        "mcc_ambos": float(global_["ambos"]),
        "brecha_quimica_menos_procedencia": float(brecha),
        "auroc_quimica": {
            e: {"auroc": round(float(pe.loc[("química", e), "auroc"]), 4),
                "ic95": [round(float(pe.loc[("química", e), "ic_bajo"]), 4),
                         round(float(pe.loc[("química", e), "ic_alto"]), 4)]}
            for e in ("todos", *ESTRATOS) if ("química", e) in pe.index},
        "auroc_quimica_diana_npass": round(
            float(pe.loc[("química+diana", "solo_npass"), "auroc"]), 4)
        if ("química+diana", "solo_npass") in pe.index else None,
        "dianas_comparables": len(completas),
        "auroc_por_diana": {
            g: {e.replace("solo_", ""): round(float(
                pdi[(pdi.diana == g) & (pdi.estrato == e)
                    & (pdi.conjunto == "química+diana")]["auroc"].iloc[0]), 4)
                for e in ("solo_chembl", "solo_npass")}
            for g in completas},
    })


if __name__ == "__main__":
    main()
