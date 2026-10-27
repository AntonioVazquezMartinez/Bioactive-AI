import numpy as np
import pytest
from scipy import sparse

from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan
from src.features.molecular import SortAndSlice, a_mol

SMILES = ["CCO", "CCN", "c1ccccc1O", "CC(=O)O", "c1ccccc1", "CCCCO", "CC(C)O", "c1ccncc1",
          "CC(=O)Nc1ccc(O)cc1", "OC(=O)c1ccccc1O"]


def _mixta(smiles, n_densas=3):
    huellas, _ = identificadores_morgan(smiles)
    densas = sparse.csr_matrix(np.arange(len(smiles) * n_densas, dtype=np.float32)
                               .reshape(len(smiles), n_densas))
    return sparse.hstack([densas, huellas]).tocsr()


def test_una_columna_por_subestructura_y_cada_smiles_se_lee_una_vez():
    m, ids = identificadores_morgan(["CCO", "CCN", "CCO"])
    assert m.shape == (3, len(ids)) and len(set(ids)) == len(ids)
    assert (m[0] != m[2]).nnz == 0                       # la misma molécula, la misma fila


def test_smiles_ilegible_falla_en_vez_de_desalinear():
    with pytest.raises(ValueError, match="no se pueden leer"):
        identificadores_morgan(["CCO", "esto no es un smiles"])


@pytest.mark.parametrize("n_bits", [4, 12, 1000])
def test_equivale_a_sort_and_slice_cuando_cada_molecula_aparece_una_vez(n_bits):
    """El vocabulario y la matriz coinciden con `SortAndSlice` (mismo conjunto de columnas)."""
    mols = [a_mol(s) for s in SMILES]
    ref = SortAndSlice(n_bits=n_bits).fit(mols)
    esperado = ref.transform(mols)
    _, ids = identificadores_morgan(SMILES)
    t = AgregarHuellas(n_densas=3, densas=(), n_bits=n_bits).fit(_mixta(SMILES))
    obtenido = t.transform(_mixta(SMILES))
    assert [int(ids[c]) for c in t.columnas_] == ref.vocabulario[:obtenido.shape[1]]
    assert (obtenido == esperado[:, :obtenido.shape[1]]).all()


def test_el_vocabulario_sale_solo_de_las_filas_de_ajuste():
    X = _mixta(SMILES)
    t = AgregarHuellas(n_densas=3, n_bits=50).fit(X[:5])
    solo_validacion = set(np.flatnonzero(np.asarray(X[:5, 3:].sum(axis=0)).ravel() == 0))
    assert not solo_validacion & set(t.columnas_)         # nada que solo exista fuera del ajuste


def test_devuelve_densas_y_huellas_en_float32():
    X = _mixta(SMILES)
    t = AgregarHuellas(n_densas=3, densas=(0, 2), n_bits=8).fit(X)
    out = t.transform(X)
    assert out.dtype == np.float32 and out.shape == (len(SMILES), 2 + len(t.columnas_))
    assert (out[:, :2] == X[:, [0, 2]].toarray()).all()


def test_con_pocas_subestructuras_no_inventa_columnas():
    X = _mixta(["CCO", "CCO"])
    t = AgregarHuellas(n_densas=3, n_bits=2048).fit(X)
    assert len(t.columnas_) == X.shape[1] - 3


def test_agrupar_iguales_deja_una_columna_por_grupo_y_recuerda_las_otras():
    m = sparse.csr_matrix(np.array([[1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 1, 1]], dtype=np.uint8))
    ids = np.array([10, 20, 30, 40])
    unica, ids_u, equivalentes = agrupar_iguales(m, ids)
    assert unica.shape == (3, 2) and list(ids_u) == [10, 30]
    assert equivalentes == [(10, 20, 40), (30,)]
    assert (unica.toarray() == m.toarray()[:, [0, 2]]).all()


def test_agrupar_iguales_no_cambia_nada_si_no_hay_duplicadas():
    m, ids = identificadores_morgan(SMILES)
    unica, ids_u, equivalentes = agrupar_iguales(m, ids)
    n_iguales = m.shape[1] - unica.shape[1]
    assert sum(len(e) - 1 for e in equivalentes) == n_iguales
    assert len(set(ids_u)) == len(ids_u)
    dens = unica.toarray().T
    assert len({c.tobytes() for c in dens}) == dens.shape[0]      # ya no quedan columnas iguales


def test_frecuencia_sin_signo_no_vacia_el_vocabulario():
    huellas, _ = identificadores_morgan(SMILES)
    X = sparse.hstack([sparse.csr_matrix(np.zeros((len(SMILES), 2), dtype=np.uint8)),
                       huellas.astype(np.uint8)]).tocsr()
    assert len(AgregarHuellas(n_densas=2, n_bits=5).fit(X).columnas_) == 5
