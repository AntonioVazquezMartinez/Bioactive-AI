"""Las tres canalizaciones candidatas del modelo de referencia.

Son las que fija la [1.5](../../docs/decisiones.md#d1-5), y aquí van como
`Pipeline` de scikit-learn y no como modelos sueltos **a propósito**: todo lo
que aprende de los datos tiene que ajustarse dentro del pliegue. Un escalador
ajustado antes de partir filtra la media y la varianza del pliegue de
evaluación, que es el mismo error que el proyecto evita con el vocabulario de
Sort & Slice y con el umbral de TPSA.

| Canalización | Por qué está | ¿Escala? |
|:--|:--|:--|
| `logistica` | el control interpretable que exige la [C.2](../../docs/decisiones.md#dc-2) | **sí** |
| `bosque` | línea base estándar; tolera descriptores correlacionados | no |
| `boosting` | suele ser el más fuerte con descriptores tabulares | no |

**El escalado no es por el acierto, es por la convergencia.** La medición de la
1.5 encontró que entre las tres formas de escalar el desempeño no se
distingue, y que sin escalar la regresión logística agota sus iteraciones en
los 15 pliegues. Por eso solo la logística lleva escalador, y es min–max por
ser el de convergencia más rápida, no por ser mejor.
"""

from __future__ import annotations

from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

CANALIZACIONES = ("logistica", "bosque", "boosting")


def canalizaciones(semilla: int = 0, *, escalador=None) -> dict[str, Pipeline]:
    """Las tres, listas para `evaluar`.

    `escalador` permite cambiar min–max por otro sin tocar nada más, que es lo
    que la 1.5 deja abierto hasta el Avance 3.
    """
    escala = MinMaxScaler() if escalador is None else escalador
    return {
        "logistica": Pipeline([
            ("escala", escala),
            ("modelo", LogisticRegression(max_iter=3000, random_state=semilla)),
        ]),
        "bosque": Pipeline([
            ("modelo", RandomForestClassifier(n_estimators=300, min_samples_leaf=2,
                                              random_state=semilla, n_jobs=-1)),
        ]),
        "boosting": Pipeline([
            ("modelo", HistGradientBoostingClassifier(random_state=semilla)),
        ]),
    }
