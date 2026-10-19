"""Selección de columnas que no depende de cómo se transformen los descriptores.

Los dos filtros corren sobre los datos **crudos de entrenamiento**, no sobre la
matriz transformada. Es lo que se cambió tras la revisión del Avance 2, por dos
razones medidas:

- Sobre Yeo-Johnson con `standardize=True` toda columna tiene varianza 1, así que
  un umbral de varianza menor que 1 solo elimina las constantes y da lo mismo
  con cualquier valor: el filtro no filtraba.
- La correlación de Pearson y la F de ANOVA sobre la matriz transformada hacían
  que la lista de columnas dependiera de la transformación elegida. La
  correlación de Spearman y el AUROC univariado solo usan el orden de los valores,
  así que dan la misma selección con cualquier transformación monótona (y
  Yeo-Johnson, min-max y la estandarización lo son).
"""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score


def casi_constantes(X: np.ndarray, frecuencia_modal: float = 0.99) -> np.ndarray:
    """Máscara de las columnas que se conservan.

    Se descarta una columna cuando un solo valor reúne al menos
    `frecuencia_modal` de las filas. Se usa la frecuencia del valor más común y
    no la varianza porque la varianza depende de la escala de cada descriptor:
    un umbral de 0.01 sobre datos crudos quitaría tanto un conteo de subestructuras
    raro como un descriptor continuo pequeño pero informativo.
    """
    n = len(X)
    conserva = np.ones(X.shape[1], dtype=bool)
    for j in range(X.shape[1]):
        _, cuentas = np.unique(X[:, j], return_counts=True)
        conserva[j] = cuentas.max() / n < frecuencia_modal
    return conserva


def poder_univariado(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """|AUROC − 0.5| de cada columna contra la etiqueta: cuánto separa por sí sola."""
    return np.array([abs(roc_auc_score(y, X[:, j]) - 0.5) for j in range(X.shape[1])])


def filtro_correlacion(X: np.ndarray, poder: np.ndarray, umbral: float = 0.95,
                       protegidas: tuple[int, ...] = ()) -> np.ndarray:
    """Máscara de las columnas que se conservan tras quitar las casi duplicadas.

    Recorre las columnas en orden y, de cada par con |Spearman| > `umbral`, se
    queda con la de mayor `poder`. **Cuando la descartada es la columna `i`, el
    recorrido de `i` termina**: seguir comparándola descartaría columnas por estar
    correlacionadas con una que ya no está, y quitaría variables que no eran
    redundantes.

    Las columnas de `protegidas` ganan cualquier par en el que estén: son las que
    el equipo usa para comprobar que una explicación tiene sentido (TPSA, HBD), y
    quedarse con un sustituto casi igual rompería esa lectura.
    """
    poder = np.asarray(poder, dtype=float).copy()
    poder[list(protegidas)] = np.inf
    rangos = np.apply_along_axis(rankdata, 0, X)
    C = np.corrcoef(rangos, rowvar=False)
    C = np.nan_to_num(C)
    descartar: set[int] = set()
    for i in range(X.shape[1]):
        if i in descartar:
            continue
        for j in range(i + 1, X.shape[1]):
            if j in descartar:
                continue
            if abs(C[i, j]) > umbral:
                if poder[i] >= poder[j]:
                    descartar.add(j)
                else:
                    descartar.add(i)
                    break
    return np.array([i not in descartar for i in range(X.shape[1])])
