"""Búsqueda de hiperparámetros que no filtra: la validación interna también agrupa.

La rúbrica del Avance 4 pide ajustar los dos mejores modelos, y la del Avance 5
pide optimizar los relevantes. El modo fácil de hacerlo mal es ajustar la
rejilla sobre una partición aleatoria: la evaluación externa sigue agrupada y se
ve honesta, pero **los hiperparámetros se eligieron sobre una medición inflada
entre 7 y 13 puntos** ([1.2](../../docs/decisiones.md#d1-2)), y eso no aparece en
ninguna métrica del reporte.

Por eso la búsqueda vive aquí y no en una llamada suelta a `GridSearchCV`:

- parte hacia adentro con `StratifiedGroupKFold`, con los grupos del pliegue
  externo, que `evaluar` le pasa porque esta clase declara `necesita_grupos`;
- se ajusta **dentro** del pliegue externo, así que la prueba del arnés nunca
  participa en elegir la rejilla;
- deja ver qué eligió en cada pliegue: `evaluar` copia `elegidos_` a la columna
  `elegidos` del resultado, porque el objeto que se le pasa nunca queda ajustado
  —`clone` deja lo ajustado en la copia del pliegue— y sin esa columna no se
  puede decir si la elección fue estable o cambió con la partición.

Cuál rejilla y cuántas combinaciones son decisión del equipo; aquí solo se
reciben como argumento.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.metrics import make_scorer, matthews_corrcoef
from sklearn.model_selection import (GridSearchCV, RandomizedSearchCV,
                                     StratifiedGroupKFold)

MCC = make_scorer(matthews_corrcoef)


class BusquedaAnidada(BaseEstimator, ClassifierMixin):
    """Una canalización que elige sus hiperparámetros dentro del pliegue.

    Se usa igual que cualquier otra canalización del arnés::

        from src.models.ajuste import BusquedaAnidada
        from src.models.alternativos import catalogo

        afinada = BusquedaAnidada(catalogo()["arbol"],
                                  {"modelo__max_depth": [3, 5, 10, None]})
        res, fdp = evaluar({"arbol afinado": afinada}, X, y, grupos)

    `n_iter` decide la estrategia: sin él la búsqueda es exhaustiva sobre la
    rejilla; con él se muestrean esas combinaciones al azar, que es lo razonable
    cuando la rejilla crece. `pliegues` es el de la validación **interna**, y
    tres suele bastar: cada pliegue interno se ajusta tantas veces como
    combinaciones haya, así que subirlo multiplica el costo del avance entero.
    """

    necesita_grupos = True

    def __init__(self, canalizacion: BaseEstimator, rejilla: Mapping[str, Sequence[Any]],
                 *, pliegues: int = 3, n_iter: int | None = None,
                 metrica: Any = MCC, semilla: int = 0, n_jobs: int | None = None):
        self.canalizacion = canalizacion
        self.rejilla = rejilla
        self.pliegues = pliegues
        self.n_iter = n_iter
        self.metrica = metrica
        self.semilla = semilla
        self.n_jobs = n_jobs

    def fit(self, X, y, grupos=None):
        if grupos is None:
            raise ValueError(
                "BusquedaAnidada necesita `grupos`: sin ellos la validación interna "
                "partiría al azar y elegiría la rejilla sobre una medición inflada. "
                "El arnés los pasa solo; fuera de él, llame fit(X, y, grupos=...).")
        y = np.asarray(y)
        grupos = np.asarray(grupos)
        interno = StratifiedGroupKFold(n_splits=self.pliegues, shuffle=True,
                                       random_state=self.semilla)
        particiones = list(interno.split(X, y, grupos))
        comunes = dict(estimator=clone(self.canalizacion), scoring=self.metrica,
                       cv=particiones, n_jobs=self.n_jobs, refit=True)
        if self.n_iter is None:
            busqueda = GridSearchCV(param_grid=dict(self.rejilla), **comunes)
        else:
            busqueda = RandomizedSearchCV(param_distributions=dict(self.rejilla),
                                          n_iter=self.n_iter,
                                          random_state=self.semilla, **comunes)
        busqueda.fit(X, y)
        self.busqueda_ = busqueda
        self.best_estimator_ = busqueda.best_estimator_
        self.elegidos_ = busqueda.best_params_
        self.puntaje_interno_ = float(busqueda.best_score_)
        self.classes_ = busqueda.best_estimator_.classes_
        return self

    def predict(self, X):
        return self.best_estimator_.predict(X)

    def predict_proba(self, X):
        return self.best_estimator_.predict_proba(X)
