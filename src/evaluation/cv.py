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
- **Cronometra el ajuste.** Las rúbricas de los Avances 4 y 5 piden los
  tiempos de entrenamiento en la misma tabla que las métricas, así que se miden
  donde ocurre el ajuste y no en un script aparte que los volvería a medir con
  otra partición.
- **No toca la prueba.** Recibe solo lo que se le da; reservar la prueba es de
  quien construye la matriz ([2.7](../../docs/decisiones.md#d2-7)).

El resultado es un `DataFrame` largo —una fila por (modelo, semilla, pliegue,
estrato)— porque es la forma que admite promediar, agrupar y graficar sin
rehacer el cálculo.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from time import perf_counter

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


def orientar_minoritaria(y: np.ndarray, p: np.ndarray) -> tuple[np.ndarray, np.ndarray, bool]:
    """Devuelve `(y, puntaje)` vistos desde la clase menos frecuente, y si hubo que voltear.

    Cuál es la minoritaria cambia entre fases —en permeabilidad es BBB−, en
    actividad es la inactiva— y entre estratos, así que se decide aquí sobre los
    datos y no se fija por convención. Vive en una función propia porque la usan
    el AUPRC y la curva de precisión-exhaustividad, y si cada uno la resolviera a
    su manera la curva podría dibujar una clase distinta de la que mide la tabla.

    **Al voltear devuelve `-p` y no `1 - p`, y el segundo valor deja de ser una
    probabilidad: es un puntaje que solo sirve para ordenar.** Los dos invierten el
    orden, pero `1 - p` lo hace perdiendo resolución y `-p` no, porque negar es exacto
    en punto flotante y restar no.

    El daño cae donde más pesa. Toda `p` menor que la mitad del épsilon de la máquina
    da `1 - p == 1.0`, así que las filas que el modelo considera minoritarias con más
    confianza quedan empatadas **en la cima** del orden, y en el mismo empate entran
    filas de la clase mayoritaria con `p` igual de pequeña. La precisión de los
    primeros puestos se desploma y el AUPRC con ella. Solo pasa con modelos que
    saturan: `GaussianNB` es el caso de este repositorio.

    La prueba de que `-p` es lo correcto no exige saber de punto flotante, es una
    identidad que tiene que cumplirse: el AUROC no depende de la orientación, así que
    `roc_auc_score(1-y, -p)` tiene que dar lo mismo que `roc_auc_score(y, p)`. Con
    `1 - p` no lo daba. `tests/test_evaluacion.py` ata eso y la pérdida de resolución.

    Esto nunca afectó al AUROC de la tabla, que se calcula con `p` sin voltear y no
    pasa por aquí; movía solo el AUPRC. Y quien necesite una probabilidad para
    umbralizar —la matriz de confusión, por ejemplo— tiene que usar `p` sin voltear:
    estas dos salidas son para ordenar.
    """
    if y.mean() <= 0.5:
        return y, p, False
    return 1 - y, -p, True


def _auprc_minoritaria(y: np.ndarray, p: np.ndarray) -> float:
    """AUPRC sobre la clase menos frecuente **de este subconjunto**.

    Medida sobre la mayoritaria, la línea base es más alta y los valores
    parecen mejores de lo que son.
    """
    ym, pm, _ = orientar_minoritaria(y, p)
    return average_precision_score(ym, pm)


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

    **Los tiempos van solo en la fila `todos`.** Son `segundos_ajuste` y
    `segundos_prediccion`, de reloj de pared, y se miden una vez por (modelo,
    semilla, pliegue): un ajuste no es un atributo del estrato, así que
    repetirlos en cada fila de subgrupo haría que cualquier promedio los
    contara varias veces. En las filas de estrato quedan vacíos a propósito.

    **Y el tiempo de reloj no es comparable entre canalizaciones que paralelizan
    distinto.** El bosque del baseline trae `n_jobs=-1` y las demás no, así que
    su cifra es la de un ajuste en todos los núcleos frente a ajustes en uno.
    Para que la columna de la tabla comparativa signifique lo mismo en todas las
    filas hay que fijar el mismo `n_jobs` en las canalizaciones que se comparen,
    o declarar cuál usa cada una. El arnés mide lo que de verdad tardó; igualar
    las condiciones es de quien arma la comparativa.
    """
    X_arr = X.to_numpy() if isinstance(X, pd.DataFrame) else X
    y = np.asarray(y)
    grupos = np.asarray(grupos)
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
                reloj = perf_counter()
                # Una canalización que ajusta hiperparámetros por dentro necesita
                # **los grupos de su parte del pliegue**: si su validación interna
                # parte al azar, deja análogos del mismo andamio a los dos lados y
                # elige los hiperparámetros sobre una medición inflada. El ajuste
                # externo seguiría siendo honesto y la rejilla elegida no, que es
                # la fuga difícil de ver. Lo declara con `necesita_grupos`.
                if getattr(canalizacion, "necesita_grupos", False):
                    modelo.fit(X_arr[ajuste], y[ajuste], grupos=grupos[ajuste])
                else:
                    modelo.fit(X_arr[ajuste], y[ajuste])
                segundos_ajuste = perf_counter() - reloj
                reloj = perf_counter()
                p = modelo.predict_proba(X_arr[val])[:, 1]
                segundos_prediccion = perf_counter() - reloj
                fuera_de_pliegue[nombre][s, val] = p

                fila = {"modelo": nombre, "semilla": semilla, "pliegue": pliegue,
                        "estrato": "todos", "n": len(val),
                        "activos": float(y[val].mean()),
                        "segundos_ajuste": segundos_ajuste,
                        "segundos_prediccion": segundos_prediccion,
                        **_medir(y[val], p)}
                # Lo que la canalización haya elegido por dentro se guarda aquí y
                # no en el objeto que se pasó: `clone` deja lo ajustado en la
                # copia del pliegue, así que fuera de esta función se perdería.
                # Sin esta columna no se puede decir si la elección fue estable
                # entre pliegues o si cambió con la partición, que es justo lo
                # que distingue un ajuste fino de una corrida afortunada.
                elegidos = getattr(modelo, "elegidos_", None)
                if elegidos is not None:
                    fila["elegidos"] = str(elegidos)
                filas.append(fila)
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


def tabla_comparativa(resultados: pd.DataFrame,
                      *,
                      principal: str = "mcc",
                      otras: Iterable[str] = ("auprc_minoritaria", "auroc"),
                      estrato: str = "todos",
                      ) -> pd.DataFrame:
    """La tabla que piden las rúbricas de los Avances 4 y 5, en un solo lugar.

    Una fila por canalización, ordenada por `principal` de mayor a menor, con
    las otras métricas y el tiempo medio de ajuste por pliegue. `principal` es
    un argumento y no una constante **a propósito**: cuál es la métrica que
    ordena es una decisión del equipo ([C.1](../../docs/decisiones.md#dc-1)), y
    cambiarla no debe obligar a tocar este código ni a rehacer la corrida.

    Dos cosas que esta tabla **no** dice, y que hay que escribir al lado:

    - **El orden no es un ganador.** Ordenar por la media no prueba que la
      primera fila se distinga de la segunda; las semillas comparten filas, así
      que `desv` es dispersión y no error estándar. Para afirmar que dos
      canalizaciones se distinguen está `intervalo_por_grupos`, que remuestrea
      grupos. El Avance 3 cerró con que ninguna de las tres se distinguía.
    - **El tiempo compara condiciones, no solo modelos.** Es reloj de pared, así
      que una canalización con `n_jobs=-1` frente a otra en un núcleo mide dos
      cosas distintas. Igualar el paralelismo antes de comparar es de quien arma
      la corrida; aquí solo se promedia lo que se midió.
    """
    # `principal` puede venir también en `otras` —pasa con los valores por
    # omisión si se pide ordenar por AUROC—, y entonces la columna sale dos
    # veces y `sort_values` no sabe por cuál ordenar.
    columnas = [principal, *(c for c in otras if c != principal)]
    d = resultados[resultados["estrato"].eq(estrato)]
    if d.empty:
        raise ValueError(f"no hay filas con estrato {estrato!r}")

    agregado = d.groupby("modelo")[columnas].mean()
    agregado.insert(1, "desv", d.groupby("modelo")[principal].std())
    if "segundos_ajuste" in d.columns:
        agregado["segundos_ajuste"] = d.groupby("modelo")["segundos_ajuste"].mean()
    agregado["pliegues"] = d.groupby("modelo")[principal].size()
    return agregado.sort_values(principal, ascending=False).round(4)


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
