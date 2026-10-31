"""Modelos de ensamble para la regresión de potencia (Avance 5).

La fase 2 predice la potencia biológica continua (`pActividad`). Los ensambles
combinan múltiples estimadores buscando reducir varianza o sesgo, divididos en
familias homogéneas y heterogéneas:

1. **Ensambles homogéneos:**
   - Embolsado (Bagging): `RandomForestRegressor` (árboles) y `BaggingRegressor`
     sobre vecinos más cercanos (`KNeighborsRegressor`).
   - Aumento de gradiente (Boosting): `HistGradientBoostingRegressor`.

2. **Ensambles heterogéneos:**
   - Promedio simple (`VotingRegressor`): promedio no ponderado de modelos base,
     sin particionamiento interno.
   - Apilado agrupado (`ApiladoAgrupado`): meta-regresión (`StackingRegressor`)
     ajustada sobre predicciones fuera de pliegue.

**Prevención de fuga en la partición interna:**
El apilado entrena un metamodelo sobre las predicciones cruzadas de sus modelos
base. Si esta partición interna se realizara al azar, análogos del mismo
esqueleto o andamio estructural quedarían simultáneamente en el ajuste de las
bases y en la evaluación del metamodelo, inflando la medición entre 7 y 13
puntos ([1.2](../../docs/decisiones.md#d1-2)). `ApiladoAgrupado` exige `grupos`
y genera pliegues internos con `GroupKFold(..., shuffle=True, random_state=semilla)`,
garantizando que la partición interna no filtre y que varíe honestamente con la
semilla.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, check_is_fitted, clone
from sklearn.ensemble import (
    BaggingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.neighbors import KNeighborsRegressor


class ApiladoAgrupado(BaseEstimator, RegressorMixin):
    """Ensamble heterogéneo apilado (stacking) con validación cruzada agrupada.

    Envuelve `StackingRegressor` garantizando que las predicciones fuera de pliegue
    empleadas para entrenar el meta-estimador respeten la partición por andamios
    estructurales (`GroupKFold`).

    Declara `necesita_grupos = True` para que los arneses de evaluación externa
    (`cv.evaluar` o `evaluar_baselines`) le suministren los grupos del pliegue.
    """

    necesita_grupos: bool = True

    def __init__(
        self,
        bases: Sequence[tuple[str, Any]] | Mapping[str, Any],
        final: Any = None,
        *,
        pliegues: int = 3,
        semilla: int = 0,
        n_jobs: int | None = None,
        passthrough: bool = False,
    ) -> None:
        self.bases = bases
        self.final = final
        self.pliegues = pliegues
        self.semilla = semilla
        self.n_jobs = n_jobs
        self.passthrough = passthrough

    def _obtener_lista_bases(self) -> list[tuple[str, Any]]:
        """Normaliza la colección de estimadores base a una lista de tuplas (nombre, estimador)."""
        if isinstance(self.bases, Mapping):
            return list(self.bases.items())
        return list(self.bases)

    def fit(
        self,
        X: Any,
        y: Any,
        grupos: Any = None,
        sample_weight: Any = None,
    ) -> ApiladoAgrupado:
        """Ajusta el ensamble apilado respetando los grupos en la partición interna."""
        if grupos is None:
            raise ValueError(
                "ApiladoAgrupado requiere 'grupos' para la validación cruzada interna "
                "por andamio (scaffold) para evitar fuga de datos entre pliegues."
            )

        grupos_arr = np.asarray(grupos)
        y_arr = np.asarray(y).ravel()

        if len(grupos_arr) != len(y_arr):
            raise ValueError(
                f"La longitud de 'grupos' ({len(grupos_arr)}) debe coincidir con la cantidad "
                f"de muestras en 'y' ({len(y_arr)})."
            )

        if self.pliegues < 2:
            raise ValueError(
                f"El número de pliegues debe ser al menos 2, pero se recibió pliegues={self.pliegues}."
            )

        n_grupos_unicos = len(np.unique(grupos_arr))
        if self.pliegues > n_grupos_unicos:
            raise ValueError(
                f"El número de pliegues (pliegues={self.pliegues}) no puede ser mayor que "
                f"el número de grupos únicos ({n_grupos_unicos})."
            )

        lista_bases = self._obtener_lista_bases()
        if not lista_bases:
            raise ValueError("ApiladoAgrupado requiere al menos un modelo base en 'bases'.")

        for item in lista_bases:
            if (
                not isinstance(item, (tuple, list))
                or len(item) != 2
                or not isinstance(item[0], str)
            ):
                raise ValueError(
                    "Cada elemento de 'bases' debe ser una tupla (nombre, estimador) con un nombre de tipo str."
                )

        cv = GroupKFold(n_splits=self.pliegues, shuffle=True, random_state=self.semilla)
        particiones = list(cv.split(X, y_arr, grupos_arr))
        self.particiones_ = particiones

        estimador = StackingRegressor(
            estimators=lista_bases,
            final_estimator=self.final,
            cv=particiones,
            n_jobs=self.n_jobs,
            passthrough=self.passthrough,
        )
        if sample_weight is not None:
            estimador.fit(X, y_arr, sample_weight=sample_weight)
        else:
            estimador.fit(X, y_arr)

        self.estimador_ = estimador
        self.estimators_ = estimador.estimators_
        self.named_estimators_ = estimador.named_estimators_
        self.final_estimator_ = estimador.final_estimator_
        if hasattr(estimador, "stack_method_"):
            self.stack_method_ = estimador.stack_method_
        if hasattr(estimador, "n_features_in_"):
            self.n_features_in_ = estimador.n_features_in_
        if hasattr(estimador, "feature_names_in_"):
            self.feature_names_in_ = estimador.feature_names_in_
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Delega la predicción al estimador apilado ajustado."""
        check_is_fitted(self, "estimador_")
        return self.estimador_.predict(X)

    def transform(self, X: Any) -> np.ndarray:
        """Retorna las predicciones de los estimadores base sobre X (meta-características)."""
        check_is_fitted(self, "estimador_")
        return self.estimador_.transform(X)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        """Obtiene los nombres de las características de salida transformadas."""
        check_is_fitted(self, "estimador_")
        return self.estimador_.get_feature_names_out(input_features)


class AfinadoAgrupado(BaseEstimator, RegressorMixin):
    """Búsqueda de hiperparámetros con validación cruzada interna agrupada por andamio.

    Envuelve `GridSearchCV` asegurando que las particiones internas respeten los
    grupos estructurales (`GroupKFold`), evitando la sobreestimación por fuga de
    información entre análogos moleculares.

    Utiliza `GroupKFold` y no `StratifiedGroupKFold` porque la variable objetivo
    (`pActividad`) es continua en regresión (a diferencia de `BusquedaAnidada` en
    `src/models/ajuste.py`, diseñada para clasificación binaria). Esta clase duplica
    temporalmente a `BusquedaAnidada` para no romper la entrega del Avance 5;
    ambas se fusionarán en un estimador unificado tras la entrega.
    """

    necesita_grupos: bool = True

    def __init__(
        self,
        canalizacion: Any,
        rejilla: Mapping[str, Sequence[Any]] | Any,
        *,
        pliegues: int = 3,
        metrica: str = "neg_root_mean_squared_error",
        semilla: int = 0,
        n_jobs: int | None = None,
    ) -> None:
        self.canalizacion = canalizacion
        self.rejilla = rejilla
        self.pliegues = pliegues
        self.metrica = metrica
        self.semilla = semilla
        self.n_jobs = n_jobs

    def fit(self, X: Any, y: Any, grupos: Any = None) -> AfinadoAgrupado:
        """Ajusta la búsqueda de hiperparámetros respetando los grupos en la partición interna."""
        if grupos is None:
            raise ValueError(
                "AfinadoAgrupado requiere 'grupos' para la validación cruzada interna "
                "por andamio (scaffold) para evitar fuga de datos entre pliegues."
            )

        grupos_arr = np.asarray(grupos)
        y_arr = np.asarray(y).ravel()

        if len(grupos_arr) != len(y_arr):
            raise ValueError(
                f"La longitud de 'grupos' ({len(grupos_arr)}) debe coincidir con la cantidad "
                f"de muestras en 'y' ({len(y_arr)})."
            )

        if self.pliegues < 2:
            raise ValueError(
                f"El número de pliegues debe ser al menos 2, pero se recibió pliegues={self.pliegues}."
            )

        n_grupos_unicos = len(np.unique(grupos_arr))
        if self.pliegues > n_grupos_unicos:
            raise ValueError(
                f"El número de pliegues (pliegues={self.pliegues}) no puede ser mayor que "
                f"el número de grupos únicos ({n_grupos_unicos})."
            )

        particiones = list(
            GroupKFold(n_splits=self.pliegues, shuffle=True, random_state=self.semilla).split(
                X, y_arr, grupos_arr
            )
        )
        self.busqueda_ = GridSearchCV(
            clone(self.canalizacion),
            dict(self.rejilla),
            scoring=self.metrica,
            cv=particiones,
            n_jobs=self.n_jobs,
            refit=True,
        ).fit(X, y_arr)
        self.best_estimator_ = self.busqueda_.best_estimator_
        self.elegidos_ = self.busqueda_.best_params_
        self.puntaje_interno_ = float(self.busqueda_.best_score_)
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predice utilizando el mejor estimador ajustado."""
        check_is_fitted(self, "busqueda_")
        return self.busqueda_.best_estimator_.predict(X)


def ensambles(
    bases: Sequence[tuple[str, Any]] | Mapping[str, Any] | None = None,
    semilla: int = 0,
    n_jobs: int | None = None,
) -> dict[str, Any]:
    """Catálogo de modelos de ensamble para regresión de potencia.

    Devuelve un diccionario con las cinco familias de ensamble requeridas:
    1. `bosque`: `RandomForestRegressor` (homogéneo, bagging de árboles).
    2. `boosting`: `HistGradientBoostingRegressor` (homogéneo, boosting de gradiente).
    3. `bagging_knn`: `BaggingRegressor` sobre `KNeighborsRegressor` (homogéneo, bagging).
    4. `votacion`: `VotingRegressor` (heterogéneo, promedio simple sin partición interna).
    5. `apilado`: `ApiladoAgrupado` (heterogéneo, apilado con validación interna agrupada).

    Las bases heterogéneas por omisión son `Ridge` y `KNeighborsRegressor`:
    en el #164 kNN obtuvo la mejor concordancia del cuaderno (0.756 con
    descriptores y huellas; 0.739 con descriptores solos) y Ridge representa el
    control lineal regularizado. El MLP queda fuera porque fue el único modelo
    que empeoró (−0.027).
    """
    if bases is None:
        bases_apilado = [
            ("ridge", Ridge()),
            ("knn", KNeighborsRegressor()),
        ]
        bases_votacion = list(bases_apilado)
    elif isinstance(bases, Mapping):
        bases_apilado = bases
        bases_votacion = list(bases.items())
    elif not isinstance(bases, (list, tuple)):
        bases_apilado = list(bases)
        bases_votacion = list(bases_apilado)
    else:
        bases_apilado = bases
        bases_votacion = list(bases)

    return {
        "bosque": RandomForestRegressor(random_state=semilla, n_jobs=n_jobs),
        "boosting": HistGradientBoostingRegressor(random_state=semilla),
        "bagging_knn": BaggingRegressor(
            estimator=KNeighborsRegressor(),
            random_state=semilla,
            n_jobs=n_jobs,
        ),
        "votacion": VotingRegressor(estimators=bases_votacion, n_jobs=n_jobs),
        "apilado": ApiladoAgrupado(
            bases=bases_apilado,
            semilla=semilla,
            n_jobs=n_jobs,
        ),
    }
