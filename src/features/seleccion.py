"""Selección de descriptores que no depende de la transformación.

Dos filtros, ajustados solo con entrenamiento y sobre los valores **crudos**:

- **Casi constantes**: se retira una columna si menos de `min_distintas` moléculas de
  entrenamiento tienen un valor distinto del más frecuente. Sobre una matriz ya
  estandarizada toda columna no constante tiene varianza 1, así que un umbral de varianza
  ahí solo retira constantes (el defecto de la §9 del notebook 02); y sobre los valores
  crudos depende de las unidades: las cargas parciales varían en décimas y caen bajo
  cualquier umbral razonable sin ser casi constantes. Contar moléculas no depende de la
  escala ni de la transformación.
- **Correlación**: Spearman, que es correlación de rangos y por tanto no cambia con
  ningún escalador monótono (min–max, estandarización, Yeo-Johnson). La lista de
  columnas que sobrevive es la misma sea cual sea la transformación que use el modelo.
  De cada par redundante se conserva la de mayor F de ANOVA calculada **sobre rangos**,
  coherente con Spearman y robusta a las colas pesadas de los descriptores.

Los dos son transformadores de sklearn, para que el baseline los reajuste dentro de
cada pliegue de la validación cruzada en lugar de reutilizar una lista fija.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_selection import f_classif
from sklearn.utils.validation import check_is_fitted


def _rangos(X: np.ndarray) -> np.ndarray:
    return np.apply_along_axis(rankdata, 0, np.asarray(X, dtype=float))


def descartar_correlacionadas(C: np.ndarray, puntaje: np.ndarray, umbral: float) -> set[int]:
    """Índices a descartar: de cada par con |C| > umbral, el de menor puntaje.

    Una columna descartada deja de competir: no puede eliminar a otra. La versión
    anterior seguía comparando `i` después de descartarlo, y quitaba columnas por
    parecerse a una que ya no existía.
    """
    descartar: set[int] = set()
    n = C.shape[0]
    for i in range(n):
        if i in descartar:
            continue
        for j in range(i + 1, n):
            if j in descartar or abs(C[i, j]) <= umbral:
                continue
            if puntaje[i] >= puntaje[j]:
                descartar.add(j)
            else:
                descartar.add(i)
                break
    return descartar


class FiltroCasiConstante(BaseEstimator, TransformerMixin):
    """Retira columnas donde menos de `min_distintas` filas difieren del valor modal."""

    def __init__(self, min_distintas: int = 10):
        self.min_distintas = min_distintas

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        self.distintas_ = np.empty(X.shape[1], dtype=int)
        for k in range(X.shape[1]):
            valores, cuentas = np.unique(X[:, k], return_counts=True)
            self.distintas_[k] = len(X) - cuentas.max()
        self.support_ = self.distintas_ >= self.min_distintas
        return self

    def get_support(self) -> np.ndarray:
        check_is_fitted(self, "support_")
        return self.support_

    def transform(self, X):
        check_is_fitted(self, "support_")
        return np.asarray(X)[:, self.support_]


class FiltroCorrelacion(BaseEstimator, TransformerMixin):
    """Retira columnas redundantes por correlación de Spearman (|ρ| > umbral)."""

    def __init__(self, umbral: float = 0.95):
        self.umbral = umbral

    def fit(self, X, y):
        R = _rangos(X)
        C = np.nan_to_num(np.corrcoef(R, rowvar=False))
        F, _ = f_classif(R, y)
        F = np.nan_to_num(F)
        self.descartadas_ = sorted(descartar_correlacionadas(C, F, self.umbral))
        self.support_ = np.ones(R.shape[1], dtype=bool)
        self.support_[self.descartadas_] = False
        return self

    def get_support(self) -> np.ndarray:
        check_is_fitted(self, "support_")
        return self.support_

    def transform(self, X):
        check_is_fitted(self, "support_")
        return np.asarray(X)[:, self.support_]
