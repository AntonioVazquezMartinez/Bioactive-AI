"""Pisos de la regresión de la fase 2: lo que se predice sin mirar la química.

El único piso del 04b es predecir siempre el promedio de todas las mediciones. Pero el corte
de 10 µM no significa lo mismo en cada diana (deja a `LRRK2` en 98.1% de activos y a `NFE2L2`
en 50.7%), y un modelo que solo sepa contra qué diana se midió ya supera ese promedio sin
entender nada de química. `MediaPorDiana` es el piso que separa las dos cosas: predice la
potencia media de la diana del par, y lo que un modelo gane sobre él es lo que aporta la
estructura de la molécula.
"""

from __future__ import annotations

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class MediaPorDiana(BaseEstimator, RegressorMixin):
    """Predice la media de la variable objetivo de la diana de cada fila.

    `columnas` son las posiciones de las columnas de diana (una por diana, con 1 en la que
    corresponde y 0 en las demás). Una diana que no aparece en las filas de ajuste recibe la
    media de todas ellas.
    """

    def __init__(self, columnas: tuple[int, ...]):
        self.columnas = columnas

    def fit(self, X, y):
        diana = np.asarray(X)[:, list(self.columnas)]
        y = np.asarray(y, dtype=float)
        self.media_global_ = float(y.mean())
        n = diana.sum(axis=0)
        suma = diana.T @ y
        self.medias_ = np.where(n > 0, suma / np.maximum(n, 1), self.media_global_)
        return self

    def predict(self, X):
        diana = np.asarray(X)[:, list(self.columnas)]
        sin_diana = diana.sum(axis=1) == 0
        p = diana @ self.medias_
        p[sin_diana] = self.media_global_
        return p
