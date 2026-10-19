"""Validación cruzada agrupada, con desglose por subgrupo.

Es el arnés que el proyecto venía repitiendo en cada script (MLOps 0.3). Lo que
hace distinto a un `cross_val_score` cualquiera, y es lo que el proyecto
necesita:

- **Agrupa por estructura, nunca al azar.** Una partición aleatoria infla los
  resultados entre 7 y 13 puntos porque deja análogos casi idénticos a los dos
  lados ([1.2](../../docs/decisiones.md#d1-2)).
- **Recibe canalizaciones, no modelos.** Todo lo que aprende de los datos
  —escalado, selección, imputación— tiene que ajustarse dentro del pliegue. Un
  `StandardScaler` ajustado antes de partir filtra la media y la varianza del
  pliegue de evaluación.
- **Desglosa por subgrupo en la misma pasada.** El control de atajo mostró que
  un AUROC agregado no describe a los productos naturales: el modelo separa los
  pares de ChEMBL y mucho menos los de NPASS ([2.3](../../docs/decisiones.md#d2-3)).
  Por eso `evaluar` acepta `estratos` y devuelve una fila por pliegue **y por
  estrato**, en vez de dejar que cada script lo recalcule a su manera.
- **No toca la prueba.** Recibe solo lo que se le da; reservar la prueba es de
  quien construye la matriz ([2.7](../../docs/decisiones.md#d2-7)).

El resultado es un `DataFrame` largo —una fila por (modelo, semilla, pliegue,
estrato)— porque es la forma que admite promediar, agrupar y graficar sin
rehacer el cálculo.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, clone
from sklearn.metrics import (average_precision_score, balanced_accuracy_score,
                             matthews_corrcoef, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold

# El mínimo de casos de la clase minoritaria para que un subgrupo se reporte.
# Por debajo, el AUROC es ruido: en la fase 2, `ACHE` tiene 221 pares de NPASS y
# tres activos, y su AUROC salía 0.763 (ver la 2.3).
MIN_MINORITARIA = 20


def _auprc_minoritaria(y: np.ndarray, p: np.ndarray) -> float:
    """AUPRC sobre la clase menos frecuente **de este subconjunto**.

    Medida sobre la mayoritaria, la línea base es más alta y los valores
    parecen mejores de lo que son. Cuál es la minoritaria cambia entre fases
    —en permeabilidad es BBB−, en actividad es la inactiva— y entre estratos,
    así que se decide aquí y no se fija por convención.
    """
    positiva_es_minoritaria = y.mean() <= 0.5
    if positiva_es_minoritaria:
        return average_precision_score(y, p)
    return average_precision_score(1 - y, 1 - p)


METRICAS: Mapping[str, Callable[[np.ndarray, np.ndarray], float]] = {
    "mcc": lambda y, p: matthews_corrcoef(y, (p >= 0.5).astype(int)),
    "auprc_minoritaria": _auprc_minoritaria,
    "auroc": roc_auc_score,
    "exactitud_balanceada": lambda y, p: balanced_accuracy_score(
        y, (p >= 0.5).astype(int)),
}


def _medir(y: np.ndarray, p: np.ndarray) -> dict[str, float]:
    if len(np.unique(y)) < 2:
        return {k: float("nan") for k in METRICAS}
    return {k: float(f(y, p)) for k, f in METRICAS.items()}


def evaluar(
    canalizaciones: Mapping[str, BaseEstimator],
    X: np.ndarray | pd.DataFrame,
    y: np.ndarray,
    grupos: np.ndarray,
    *,
    estratos: np.ndarray | None = None,
    semillas: Sequence[int] = (0, 1, 2),
    pliegues: int = 5,
    min_minoritaria: int = MIN_MINORITARIA,
    verboso: bool = True,
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    """Evalúa cada canalización con validación cruzada agrupada.

    Devuelve dos cosas:

    - el `DataFrame` largo con una fila por (modelo, semilla, pliegue, estrato);
    - las **predicciones fuera de pliegue**, de forma `(semillas, filas)` por
      canalización, que son las que permiten cortar después por cualquier
      columna y remuestrear sin reentrenar.

    `estratos` es opcional y puede ser cualquier etiqueta por fila: procedencia,
    diana, grupo A–D. Un subgrupo se reporta solo si su clase minoritaria llega
    a `min_minoritaria`.
    """
    X_arr = X.to_numpy() if isinstance(X, pd.DataFrame) else X
    y = np.asarray(y)
    filas: list[dict] = []
    fuera_de_pliegue = {
        nombre: np.full((len(semillas), len(y)), np.nan) for nombre in canalizaciones}

    for s, semilla in enumerate(semillas):
        cv = StratifiedGroupKFold(n_splits=pliegues, shuffle=True, random_state=semilla)
        for pliegue, (ajuste, val) in enumerate(cv.split(X_arr, y, grupos), 1):
            for nombre, canalizacion in canalizaciones.items():
                modelo = clone(canalizacion)
                # **La semilla cambia la partición, no el modelo.** Aquí había
                # un `if hasattr(modelo, "random_state"): set_params(...)` que
                # no se ejecutaba nunca —un `Pipeline` no expone
                # `random_state`— y que habría lanzado `ValueError` si se
                # hubiera ejecutado. Así que las tres semillas siempre
                # entrenaron con el `random_state` con el que se construyó la
                # canalización, y lo que varía entre ellas es el reparto en
                # pliegues. Para este arnés es lo que importa, porque el
                # agrupamiento pesa más que la aleatoriedad interna del
                # modelo; variar también la del modelo ensancharía el error
                # estándar y queda para el Avance 4. Lo que no se puede es
                # decir que se varía cuando no se varía.
                modelo.fit(X_arr[ajuste], y[ajuste])
                p = modelo.predict_proba(X_arr[val])[:, 1]
                fuera_de_pliegue[nombre][s, val] = p

                filas.append({"modelo": nombre, "semilla": semilla, "pliegue": pliegue,
                              "estrato": "todos", "n": len(val),
                              "activos": float(y[val].mean()), **_medir(y[val], p)})
                if estratos is None:
                    continue
                for e in pd.unique(estratos[val]):
                    sel = estratos[val] == e
                    ys = y[val][sel]
                    if min(int(ys.sum()), int((1 - ys).sum())) < min_minoritaria:
                        continue
                    filas.append({"modelo": nombre, "semilla": semilla,
                                  "pliegue": pliegue, "estrato": str(e),
                                  "n": int(sel.sum()), "activos": float(ys.mean()),
                                  **_medir(ys, p[sel])})
            if verboso:
                print(f"  semilla {semilla} · pliegue {pliegue} listo", flush=True)

    return pd.DataFrame(filas), fuera_de_pliegue


def resumen(resultados: pd.DataFrame,
            metricas: Iterable[str] = ("mcc", "auprc_minoritaria", "auroc"),
            ) -> pd.DataFrame:
    """Promedio y desviación por modelo y estrato.

    **La desviación no es un error estándar.** Las semillas comparten las mismas
    filas, así que los 15 valores no son quince réplicas independientes; sirve
    para ver dispersión, no para decidir si dos modelos se distinguen. Para eso
    está `intervalo_por_grupos`.
    """
    return (resultados.groupby(["estrato", "modelo"])[list(metricas)]
            .agg(["mean", "std"]).round(4))


def intervalo_por_grupos(y: np.ndarray, p: np.ndarray, grupos: np.ndarray,
                         metrica: Callable[[np.ndarray, np.ndarray], float] = roc_auc_score,
                         *, remuestras: int = 2000, semilla: int = 0,
                         ) -> tuple[float, float, float]:
    """La métrica y su intervalo del 95%, remuestreando **grupos** y no filas.

    La fila no es la unidad independiente: los pares del mismo andamio comparten
    química y van juntos en la partición, así que un bootstrap sobre filas da un
    intervalo demasiado estrecho. Es la forma fácil de concluir que algo se
    distingue cuando no se distingue.
    """
    y, p, grupos = np.asarray(y), np.asarray(p), np.asarray(grupos)
    if len(np.unique(y)) < 2:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(semilla)
    unicos = np.unique(grupos)
    indices = {g: np.flatnonzero(grupos == g) for g in unicos}
    muestras = []
    for _ in range(remuestras):
        elegidos = rng.choice(unicos, size=len(unicos), replace=True)
        idx = np.concatenate([indices[g] for g in elegidos])
        if len(np.unique(y[idx])) < 2:
            continue
        muestras.append(metrica(y[idx], p[idx]))
    if not muestras:
        return float(metrica(y, p)), float("nan"), float("nan")
    lo, hi = np.percentile(muestras, [2.5, 97.5])
    return float(metrica(y, p)), float(lo), float(hi)
