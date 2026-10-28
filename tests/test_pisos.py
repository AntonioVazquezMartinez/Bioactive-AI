import numpy as np
from sklearn.base import clone

from src.models.pisos import MediaPorDiana


def _datos():
    # dos descriptores y tres dianas (columnas 2, 3 y 4); la tercera no aparece al ajustar
    X = np.array([[1, 5, 1, 0, 0], [2, 6, 1, 0, 0], [3, 7, 0, 1, 0], [4, 8, 0, 1, 0]], dtype=np.float32)
    y = np.array([4.0, 6.0, 8.0, 10.0])
    return X, y


def test_predice_la_media_de_cada_diana_sin_mirar_los_descriptores():
    X, y = _datos()
    m = MediaPorDiana((2, 3, 4)).fit(X, y)
    assert np.allclose(m.predict(X), [5, 5, 9, 9])
    X2 = X.copy()
    X2[:, :2] = 99                                   # cambiar la química no cambia la predicción
    assert np.allclose(m.predict(X2), [5, 5, 9, 9])


def test_una_diana_sin_filas_de_ajuste_recibe_la_media_global():
    X, y = _datos()
    m = MediaPorDiana((2, 3, 4)).fit(X, y)
    nueva = np.array([[0, 0, 0, 0, 1]], dtype=np.float32)
    assert np.allclose(m.predict(nueva), y.mean())
    assert np.allclose(m.predict(np.zeros((1, 5), dtype=np.float32)), y.mean())


def test_se_puede_clonar_y_acepta_un_ajuste_nuevo():
    X, y = _datos()
    m = clone(MediaPorDiana((2, 3, 4))).fit(X, y + 1)
    assert np.allclose(m.predict(X), [6, 6, 10, 10])
