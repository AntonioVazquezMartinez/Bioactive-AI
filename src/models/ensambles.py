"""Los ensambles del Avance 5 en la fase 1: homogéneos y heterogéneos, sin fuga.

La rúbrica pide al menos cuatro ensambles que cubran las dos estrategias y que el
stacking use los mejores individuales del Avance 4. Aquí están armados como
canalizaciones del arnés, igual que los individuales, para que entren a la misma
tabla con los mismos pliegues.

| clave | estrategia | qué combina |
|:--|:--|:--|
| `bosque` | homogénea, bagging de árboles con columnas al azar | árboles de decisión |
| `boosting` | homogénea, secuencial | árboles poco profundos |
| `bagging_svm` | homogénea, bagging | copias del SVM RBF sobre remuestreos |
| `votacion` | heterogénea, promedio de probabilidades | los individuales base |
| `stacking` | heterogénea, un modelo aprende a combinarlos | los individuales base |

**El stacking es el único que puede filtrar sin que se note.** El meta-modelo se
entrena con predicciones de los modelos base hechas fuera de pliegue, y esos
pliegues internos se arman por defecto al azar. Con análogos del mismo esqueleto a
los dos lados, las predicciones de entrenamiento del meta-modelo salen mejores de
lo que serán en validación, y aprende a confiar de más en el modelo que memoriza.
`StackingAgrupado` parte por dentro con los grupos del pliegue externo, por la
misma razón que `BusquedaAnidada` ([1.2](../../docs/decisiones.md#d1-2)).

Cuáles individuales entran y con qué hiperparámetros es decisión del equipo; aquí
solo se reciben como argumento.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin, clone
from sklearn.ensemble import BaggingClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from .alternativos import seleccion
from .baseline import canalizaciones


class StackingAgrupado(BaseEstimator, ClassifierMixin):
    """Stacking cuya validación interna agrupa con los grupos del pliegue externo.

    `estimadores` es una lista de `(nombre, canalización)`. El meta-modelo recibe la
    probabilidad de la clase positiva de cada uno, calculada fuera de los pliegues
    internos, y por defecto es una regresión logística: con tantas entradas como
    modelos base, y correlacionadas, un meta-modelo flexible sobreajusta.
    """

    necesita_grupos = True

    def __init__(self, estimadores: Sequence[tuple[str, BaseEstimator]],
                 final: BaseEstimator | None = None, *, pliegues: int = 3,
                 semilla: int = 0):
        self.estimadores = estimadores
        self.final = final
        self.pliegues = pliegues
        self.semilla = semilla

    def fit(self, X, y, grupos=None):
        if grupos is None:
            raise ValueError(
                "StackingAgrupado necesita `grupos`: sin ellos el meta-modelo aprendería "
                "de predicciones hechas con análogos del mismo esqueleto a los dos lados. "
                "El arnés los pasa solo; fuera de él, llame fit(X, y, grupos=...).")
        y = np.asarray(y)
        interno = StratifiedGroupKFold(n_splits=self.pliegues, shuffle=True,
                                       random_state=self.semilla)
        particiones = list(interno.split(X, y, np.asarray(grupos)))
        final = LogisticRegression(max_iter=3000) if self.final is None else clone(self.final)
        self.stacking_ = StackingClassifier(
            [(n, clone(e)) for n, e in self.estimadores], final_estimator=final,
            cv=particiones, stack_method="predict_proba").fit(X, y)
        self.classes_ = self.stacking_.classes_
        return self

    def predict(self, X):
        return self.stacking_.predict(X)

    def predict_proba(self, X):
        return self.stacking_.predict_proba(X)


def ensambles(base: Sequence[str], semilla: int = 0) -> dict[str, BaseEstimator]:
    """Los cinco ensambles, con `base` como los individuales de la votación y el stacking.

    `base` son claves del catálogo de `alternativos.py`; el bagging copia el SVM RBF
    porque es el mejor individual del Avance 4. El bosque y el boosting son los del
    baseline del 03, sin cambios, para que su fila se pueda contrastar con la que ya
    está registrada.
    """
    individuales = seleccion(tuple(base), semilla)
    referencia = canalizaciones(semilla)
    # El bosque del baseline usa todos los núcleos; aquí uno solo, como los demás, para que
    # la columna de tiempos compare modelos y no paralelismo. No cambia sus predicciones.
    referencia["bosque"].set_params(modelo__n_jobs=1)
    svm = seleccion(("svm_rbf",), semilla)["svm_rbf"]
    return {
        "bosque": referencia["bosque"],
        "boosting": referencia["boosting"],
        "bagging_svm": Pipeline([
            ("modelo", BaggingClassifier(svm, n_estimators=10, random_state=semilla))]),
        "votacion": Pipeline([
            ("modelo", VotingClassifier(list(individuales.items()), voting="soft"))]),
        "stacking": StackingAgrupado(list(individuales.items()), semilla=semilla),
    }
