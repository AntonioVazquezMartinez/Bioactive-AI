"""El AFT y la censura por la izquierda, que su filtro por omisión descarta."""
import numpy as np

from src.models.aft import AftConCensuraIzquierda, RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado


def _datos():
    """Nueve filas: tres exactas, tres censuradas por la derecha en µM, tres por la izquierda.

    En pActividad: una exacta es `inf == sup`; un «> 10 µM» es (−inf, 5] y en µM queda
    [10, +inf), censura por la derecha; un «< 0.1 µM» es [7, +inf) y en µM queda [0, 0.1],
    censura por la izquierda. La última fila de cada bloque repite para que haya señal.
    """
    rng = np.random.default_rng(0)
    X = rng.normal(size=(9, 4))
    inferior = np.array([6.0, 5.5, 6.5, -np.inf, -np.inf, -np.inf, 7.0, 7.5, 8.0])
    superior = np.array([6.0, 5.5, 6.5, 5.0, 4.5, 4.0, np.inf, np.inf, np.inf])
    return X, inferior, superior


def test_por_omision_descarta_la_censura_por_la_izquierda():
    """El comportamiento por omisión es el de la corrida de la 2.13 y no cambia."""
    X, inferior, superior = _datos()
    m = RegresionAFT(rondas=5, semilla=0).fit(X, inferior, superior)
    assert m.n_descartadas_ == 3, "las tres [0, c] en µM tendrían que quedar fuera"


def test_la_variante_las_conserva_y_xgboost_las_admite():
    """Un `[0, c]` reescrito a `[1e-12, c]` sobrevive al filtro y XGBoost lo ajusta."""
    X, inferior, superior = _datos()
    m = AftConCensuraIzquierda(rondas=5, semilla=0)
    m.fit(X, inferior, superior)
    assert m.n_descartadas_ == 0, "con la variante no sobra ninguna de las nueve"
    assert m.n_recuperadas_ == 3, "las tres por la izquierda son las recuperadas"
    pred = m.predict(X)
    assert pred.shape == (9,) and np.all(np.isfinite(pred))


def test_la_variante_sigue_descartando_lo_que_no_informa():
    """Un (−inf, +inf) en pActividad es [0, +inf) en µM: no informa, y se va igual."""
    X, inferior, superior = _datos()
    inferior = np.append(inferior, -np.inf)
    superior = np.append(superior, np.inf)
    X = np.vstack([X, X[:1]])
    m = AftConCensuraIzquierda(rondas=5, semilla=0)
    m.fit(X, inferior, superior)
    assert m.n_descartadas_ == 1, "la fila sin ninguna cota tiene que salir"


def test_contradictorio_se_descarta_en_las_dos_clases():
    X, inferior, superior = _datos()
    inferior = np.append(inferior, 8.0)       # inferior > superior: intervalo vacío
    superior = np.append(superior, 4.0)
    X = np.vstack([X, X[:1]])
    for clase in (RegresionAFT, AftConCensuraIzquierda):
        m = clase(rondas=5, semilla=0)
        m.fit(X, inferior, superior)
        assert m.n_descartadas_ >= 1


def test_con_huellas_censurado_pasa_el_intervalo_completo():
    """El envoltorio no descarta filas y el vocabulario se aprende solo con la X que recibe."""
    from scipy import sparse
    X, inferior, superior = _datos()
    # Dos columnas densas y cuatro de «huellas» 0/1, la última siempre cero para que se caiga.
    huellas = np.array([[1, 0, 1, 0], [1, 1, 0, 0], [0, 1, 1, 0]] * 3, dtype=float)
    mixta = sparse.csr_matrix(np.hstack([X[:, :2], huellas]))
    m = ConHuellasCensurado(AftConCensuraIzquierda(rondas=5, semilla=0),
                            n_densas=2, n_bits=3)
    m.fit(mixta, inferior, superior)
    assert m.modelo.n_descartadas_ == 0, "el envoltorio no debe perder filas"
    assert m.huellas_.columnas_.shape[0] == 3, "la columna de ceros no entra al vocabulario"
    assert m.modelo.n_features_in_ == 2 + 3
    assert m.predict(mixta).shape == (9,)


def test_con_huellas_censurado_se_puede_clonar():
    """El arnés llama a `clone` en cada pliegue."""
    from sklearn.base import clone
    m = ConHuellasCensurado(RegresionAFT(semilla=0), n_densas=2, n_bits=3)
    c = clone(m)
    assert c.n_densas == 2 and c.n_bits == 3 and isinstance(c.modelo, RegresionAFT)
