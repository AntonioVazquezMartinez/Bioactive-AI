"""Pisos que separan lo que aporta la química de lo que aporta el contexto.

Un piso es un modelo deliberadamente ciego al problema: si un modelo con química
no le gana por un margen claro, la cifra del modelo dice mucho menos de lo que
parece. El 04b traía un solo piso, `media`, que predice el promedio global y saca
0.500 de concordancia. Ese piso es demasiado bajo para la fase 2, porque la
representación `descriptores+diana` **le entrega la diana al modelo como entrada**
(`tareas.py`, donde se concatena el one-hot de `target_gene`), y la tasa de
activos cambia muchísimo entre dianas: con el corte de 10 µM va de 50.7% en
`NFE2L2` a 98.1% en `LRRK2`. Un modelo que solo supiera la diana ya ordenaría
bastante bien sin entender una sola molécula.

`MediaPorDiana` es ese modelo. Lo que el modelo real saque por encima de él es lo
que de verdad aportó la química.

**Cómo leer su concordancia.** Dentro de una misma diana el piso predice el mismo
número para todas las filas, y `concordancia_harrell` cuenta los empates de
predicción como medio punto. Así que todos los pares que comparten diana le dan
exactamente 0.5, y **toda su concordancia por encima de 0.5 viene de ordenar
dianas entre sí, no moléculas**.
"""

from __future__ import annotations

import numpy as np


class MediaPorDiana:
    """Predice el promedio de `pActividad` de la diana a la que pertenece cada par.

    Se usa envuelto en `SoloExactas`, que es quien descarta las mediciones
    censuradas y le pasa `y` ya limpio, igual que a los demás pisos de
    `baseline_regresion.py`.

    `n_dianas` es cuántas columnas ocupa el bloque one-hot al final de `X`. Sale
    de `t.meta["target_gene"].nunique()`.
    """

    def __init__(self, n_dianas: int):
        if n_dianas < 1:
            raise ValueError(f"n_dianas tiene que ser al menos 1; llegó {n_dianas}")
        self.n_dianas = n_dianas

    def _diana(self, X: np.ndarray) -> np.ndarray:
        """El índice de diana de cada fila, leído del bloque one-hot final de `X`.

        **Depende de que ese bloque vaya al final**, que es como lo arma hoy
        `tareas.py` al concatenar los descriptores con `pd.get_dummies`. Por eso
        se comprueba en vez de confiar: sobre una fila de puros ceros `argmax`
        devuelve 0 sin avisar, y el piso seguiría respondiendo números creíbles y
        equivocados. Si alguien cambia el orden de las columnas, esto revienta
        aquí y no tres pasos más adelante.
        """
        X = np.asarray(X, dtype=float)
        if X.shape[1] < self.n_dianas:
            raise ValueError(
                f"X tiene {X.shape[1]} columnas y el bloque de dianas pide "
                f"{self.n_dianas}")
        bloque = X[:, -self.n_dianas:]
        if not np.allclose(bloque.sum(axis=1), 1.0):
            raise ValueError(
                "las últimas columnas de X no son un one-hot de la diana; "
                "¿cambió la representación en tareas.py?")
        return bloque.argmax(axis=1)

    def fit(self, X, y) -> "MediaPorDiana":
        diana = self._diana(X)
        y = np.asarray(y, dtype=float)

        # El promedio de cada diana, calculado **solo con las filas de este
        # pliegue de entrenamiento**. Calcularlo antes de partir haría que el
        # piso viera las filas de validación y dejaría de ser un piso.
        suma = np.bincount(diana, weights=y, minlength=self.n_dianas)
        cuenta = np.bincount(diana, minlength=self.n_dianas)

        # Respaldo para las dianas que no caigan en este pliegue: sin él, su
        # promedio sería una división entre cero.
        self.global_ = float(y.mean()) if len(y) else float("nan")
        self.medias_ = np.where(cuenta > 0,
                                suma / np.maximum(cuenta, 1),
                                self.global_)
        return self

    def predict(self, X) -> np.ndarray:
        return self.medias_[self._diana(X)]
