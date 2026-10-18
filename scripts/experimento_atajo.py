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

Salida: `notebooks/datos/resultados_atajo.csv`, versionado, y una corrida en
`experimentos/`. Tarda unos 3 minutos.

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
    d = d.merge(desc, on="smiles", how="inner")
    y = d["activo_10um"].astype(int).to_numpy()
    grupos = d["grupo_cv"].to_numpy()
    estrato = d["estrato"].to_numpy()

    columnas = [c for c in desc.columns if c != "smiles"]
    X_quimica = d[columnas].to_numpy(dtype=np.float32)
    # El estrato como indicadores: es todo lo que un modelo «de procedencia» ve.
    X_fuente = pd.get_dummies(d["estrato"]).reindex(
        columns=ESTRATOS, fill_value=False).to_numpy(dtype=np.float32)
    conjuntos = {
        "procedencia": X_fuente,
        "química": X_quimica,
        "ambos": np.hstack([X_quimica, X_fuente]),
    }

    print(f"{len(d):,} pares · {len(columnas)} descriptores · "
          f"{d['grupo_cv'].nunique():,} grupos · {y.mean():.1%} activos", flush=True)

    filas = []
    for semilla in SEMILLAS:
        cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
        for pliegue, (ajuste, val) in enumerate(cv.split(X_quimica, y, grupos), 1):
            for nombre, X in conjuntos.items():
                clf = modelo(semilla).fit(X[ajuste], y[ajuste])
                p = clf.predict_proba(X[val])[:, 1]
                fila = {"semilla": semilla, "pliegue": pliegue, "conjunto": nombre,
                        "estrato": "todos", "n": len(val), **metricas(y[val], p)}
                filas.append(fila)
                # Y dentro de cada estrato, donde ya no hay fuente que distinguir.
                for e in ESTRATOS:
                    sel = estrato[val] == e
                    if sel.sum() < 50 or len(np.unique(y[val][sel])) < 2:
                        continue
                    filas.append({"semilla": semilla, "pliegue": pliegue,
                                  "conjunto": nombre, "estrato": e, "n": int(sel.sum()),
                                  **metricas(y[val][sel], p[sel])})
            print(f"  semilla {semilla} pliegue {pliegue} listo", flush=True)

    res = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(SALIDA, index=False)
    print(f"\n[guardado] {SALIDA.relative_to(RAIZ)}")

    resumen = (res.groupby(["estrato", "conjunto"])[["mcc", "auprc_minoritaria", "auroc"]]
               .agg(["mean", "std"]).round(4))
    print("\nPromedio de las 15 evaluaciones")
    print(resumen.to_string())

    global_ = res[res["estrato"].eq("todos")].groupby("conjunto")["mcc"].mean()
    brecha = global_["química"] - global_["procedencia"]
    print(f"\nMCC: procedencia {global_['procedencia']:.4f} ·"
          f" química {global_['química']:.4f} · ambos {global_['ambos']:.4f}")
    print(f"La química supera a la procedencia por {brecha:.4f} de MCC")
    print("El control dispara si esa diferencia es pequeña:"
          " querría decir que basta la fuente")

    quimica = res[res.conjunto.eq("química")]
    corrida.metricas({
        "mcc_procedencia": float(global_["procedencia"]),
        "mcc_quimica": float(global_["química"]),
        "mcc_ambos": float(global_["ambos"]),
        "brecha_quimica_menos_procedencia": float(brecha),
        # El desglose va en AUROC y no en MCC: el MCC usa el umbral fijo de 0.5
        # y los estratos tienen tasas base muy distintas (74.8%% contra 12.3%%),
        # así que compararlos con un umbral común castiga al minoritario por una
        # razón que no es su señal.
        "auroc_por_estrato": {
            e: float(quimica[quimica.estrato.eq(e)]["auroc"].mean())
            for e in ESTRATOS if quimica.estrato.eq(e).any()},
        "auroc_global": float(quimica[quimica.estrato.eq("todos")]["auroc"].mean()),
    })


if __name__ == "__main__":
    main()
