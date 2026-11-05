"""Sort & Slice dentro de una canalización: el vocabulario se aprende en cada ajuste.

`SortAndSlice` (en `molecular.py`) aprende el vocabulario de una lista de moléculas, y eso
sirve para una partición fija. Dentro de una validación cruzada el vocabulario tiene que
reaprenderse **con las filas de entrenamiento de cada pliegue**: si se calcula una vez con todo
lo que hay, la validación ya influyó en qué columnas existen, y es una fuga que no aparece en
ninguna métrica.

Para que eso cueste segundos y no minutos, las moléculas se leen una sola vez. `identificadores_morgan`
devuelve una matriz dispersa con **una columna por subestructura distinta** (el identificador de 32
bits de RDKit, sin plegar), y `AgregarHuellas` se queda en cada ajuste con las `n_bits` columnas más
frecuentes entre las filas de entrenamiento. Es lo mismo que hace `SortAndSlice.fit`, con la
diferencia de que la frecuencia se cuenta por fila y no por molécula (en la fase 2 un compuesto
aparece en 1.18 pares en promedio); `tests/test_huellas.py` comprueba la equivalencia cuando cada
molécula aparece una vez.
"""

from __future__ import annotations

import numpy as np
from rdkit.Chem import rdFingerprintGenerator
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin

from .molecular import a_mol


def identificadores_morgan(smiles, radio: int = 2) -> tuple[sparse.csr_matrix, np.ndarray]:
    """Matriz binaria dispersa (filas × subestructuras distintas) y los identificadores.

    Una columna por subestructura, sin plegar, ordenadas por identificador. Cada SMILES se lee
    una vez aunque aparezca en varias filas. Falla si alguno no se puede leer: quitarlo en
    silencio desalinearía la matriz con la de descriptores.
    """
    smiles = np.asarray(smiles, dtype=object)
    unicos, inverso = np.unique(smiles, return_inverse=True)
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radio)
    ids_por_molecula = []
    ilegibles = []
    for s in unicos:
        mol = a_mol(s)
        if mol is None:
            ilegibles.append(s)
            ids_por_molecula.append(np.empty(0, dtype=np.int64))
        else:
            ids_por_molecula.append(
                np.fromiter(gen.GetSparseCountFingerprint(mol).GetNonzeroElements().keys(),
                            dtype=np.int64))
    if ilegibles:
        raise ValueError(f"{len(ilegibles)} SMILES no se pueden leer (el primero: {ilegibles[0]!r})")
    identificadores = np.unique(np.concatenate(ids_por_molecula))
    columnas = np.concatenate([np.searchsorted(identificadores, ids) for ids in ids_por_molecula])
    filas = np.repeat(np.arange(len(unicos)), [len(ids) for ids in ids_por_molecula])
    por_molecula = sparse.csr_matrix(
        (np.ones(len(columnas), dtype=np.uint8), (filas, columnas)),
        shape=(len(unicos), len(identificadores)))
    return por_molecula[inverso], identificadores


def agrupar_iguales(huellas: sparse.csr_matrix, identificadores: np.ndarray
                    ) -> tuple[sparse.csr_matrix, np.ndarray, list[tuple[int, ...]]]:
    """Deja una sola columna por cada grupo de subestructuras que valen lo mismo en todas las filas.

    Dos subestructuras que siempre aparecen juntas (el `S` y el `O=S` de un sulfonilo, por ejemplo)
    son la misma variable para cualquier modelo, y si ambas entran el modelo reparte su peso entre
    ellas de forma arbitraria. No se mira la etiqueta, y lo que es idéntico en todas las filas lo es
    también en cualquier subconjunto, así que hacerlo una vez sobre todo el conjunto no filtra
    información de la validación. Se queda la primera columna de cada grupo y se devuelve, para cada
    columna conservada, la tupla con los identificadores de todas las que representa (la propia
    primero), para poder nombrar la variable con todas sus subestructuras.
    """
    columnas = huellas.tocsc()
    columnas.sort_indices()
    grupos: dict[bytes, list[int]] = {}
    for j in range(columnas.shape[1]):
        grupos.setdefault(columnas.indices[columnas.indptr[j]:columnas.indptr[j + 1]].tobytes(),
                          []).append(j)
    conservadas = [g[0] for g in grupos.values()]
    equivalentes = [tuple(int(i) for i in identificadores[g]) for g in grupos.values()]
    return columnas[:, conservadas].tocsr(), identificadores[conservadas], equivalentes


class AgregarHuellas(BaseEstimator, TransformerMixin):
    """Entrada mixta → matriz densa con las columnas `densas` y las `n_bits` huellas más frecuentes.

    `X` es una matriz dispersa cuyas primeras columnas son las densas (descriptores y diana) y el
    resto es la salida de `identificadores_morgan`. En `fit` cuenta cuántas filas de entrenamiento
    tiene cada subestructura y se queda con las `n_bits` más frecuentes (los empates se resuelven por
    la posición de la columna, que sigue el orden del identificador, para que sea reproducible).
    `transform` devuelve las columnas densas indicadas y esas huellas, en `float32`.

    Con `densas=()` solo salen las huellas.
    """

    def __init__(self, n_densas: int, densas: tuple[int, ...] | None = None, n_bits: int = 2048):
        self.n_densas = n_densas
        self.densas = densas
        self.n_bits = n_bits

    def fit(self, X, y=None):
        huellas = sparse.csr_matrix(X)[:, self.n_densas:]
        frecuencia = np.asarray(huellas.sum(axis=0)).ravel()
        orden = np.lexsort((np.arange(len(frecuencia)), -frecuencia.astype(np.int64)))
        usadas = orden[:self.n_bits]
        self.columnas_ = usadas[frecuencia[usadas] > 0]
        return self

    def transform(self, X):
        X = sparse.csr_matrix(X)
        densas = np.arange(self.n_densas) if self.densas is None else np.asarray(self.densas, int)
        partes = [X[:, densas].toarray().astype(np.float32),
                  X[:, self.n_densas:][:, self.columnas_].toarray().astype(np.float32)]
        return np.hstack(partes)
