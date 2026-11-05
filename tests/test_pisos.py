"""El piso por diana tiene que promediar por diana y no mirar la química.

Atan las tres cosas que lo hacen un piso válido: que devuelva exactamente el promedio de cada
diana, que una diana que no cayó en el pliegue de entrenamiento caiga al promedio global, y que
unas columnas que no son un one-hot revienten en vez de responder un número creíble y equivocado.
"""

import numpy as np
import pytest
from sklearn.base import clone

from src.models.pisos import MediaPorDiana


def _matriz(dianas, k, n_descriptores=3, seed=0):
    """`X` con columnas de ruido y el one-hot de `dianas` al final.

    `k` se pasa aparte y no se deduce de `dianas`, porque hay que poder armar una matriz de
    entrenamiento a la que le falte una de las dianas.
    """
    rng = np.random.default_rng(seed)
    dianas = np.asarray(dianas)
    ruido = rng.normal(size=(len(dianas), n_descriptores))
    return np.hstack([ruido, np.eye(k)[dianas]])


def _posiciones(k, n_descriptores=3):
    return tuple(range(n_descriptores, n_descriptores + k))


def test_predice_el_promedio_de_cada_diana():
    X = _matriz([0, 0, 1, 1, 1], k=2)
    y = np.array([7.0, 6.0, 5.0, 5.5, 4.5])
    piso = MediaPorDiana(_posiciones(2)).fit(X, y)
    np.testing.assert_allclose(piso.predict(X), [6.5, 6.5, 5.0, 5.0, 5.0])


def test_no_distingue_moleculas_dentro_de_la_misma_diana():
    """La propiedad que lo define: la química de la fila no cambia su predicción."""
    X = _matriz([0, 0, 1, 1, 1], k=2)
    y = np.array([7.0, 6.0, 5.0, 5.5, 4.5])
    piso = MediaPorDiana(_posiciones(2)).fit(X, y)
    otra = X.copy()
    otra[:, :-2] = otra[:, :-2] * 100.0 + 7.0
    np.testing.assert_allclose(piso.predict(X), piso.predict(otra))


def test_con_tres_dianas_ninguna_se_funde_con_otra():
    """Con dos dianas, confundir el índice solo las renombra y se cancela entre el ajuste y la
    predicción. Hacen falta tres para que mezclarlas se note."""
    X = _matriz([0, 0, 1, 1, 2, 2], k=3)
    y = np.array([7.0, 8.0, 5.0, 6.0, 3.0, 4.0])
    piso = MediaPorDiana(_posiciones(3)).fit(X, y)
    np.testing.assert_allclose(piso.predict(X), [7.5, 7.5, 5.5, 5.5, 3.5, 3.5])


def test_las_columnas_de_diana_pueden_ir_en_cualquier_posicion():
    """En los brazos anchos las huellas van después de la diana: no siempre está al final."""
    X = _matriz([0, 0, 1, 1, 2, 2], k=3)
    y = np.array([7.0, 8.0, 5.0, 6.0, 3.0, 4.0])
    ancha = np.hstack([X, np.random.default_rng(1).integers(0, 2, size=(6, 10))]).astype(float)
    piso = MediaPorDiana(_posiciones(3)).fit(ancha, y)
    np.testing.assert_allclose(piso.predict(ancha), [7.5, 7.5, 5.5, 5.5, 3.5, 3.5])


def test_una_diana_ausente_cae_al_promedio_global():
    X_entrena = _matriz([0, 0, 0], k=2)
    y = np.array([7.0, 6.0, 5.0])
    piso = MediaPorDiana(_posiciones(2)).fit(X_entrena, y)
    assert piso.predict(_matriz([1], k=2))[0] == pytest.approx(6.0)


def test_unas_columnas_que_no_son_onehot_revientan():
    X = _matriz([0, 0, 1], k=2)
    y = np.array([7.0, 6.0, 5.0])
    with pytest.raises(ValueError, match="one-hot"):
        MediaPorDiana((0, 1)).fit(X, y)              # posiciones equivocadas: son descriptores
    sin_diana = X.copy()
    sin_diana[0, -2:] = 0.0                          # una fila que ya no declara diana
    with pytest.raises(ValueError, match="one-hot"):
        MediaPorDiana(_posiciones(2)).fit(sin_diana, y)
    piso = MediaPorDiana(_posiciones(2)).fit(X, y)
    with pytest.raises(ValueError, match="one-hot"):
        piso.predict(sin_diana)


def test_se_puede_clonar_y_acepta_un_ajuste_nuevo():
    X = _matriz([0, 0, 1, 1], k=2)
    y = np.array([4.0, 6.0, 8.0, 10.0])
    m = clone(MediaPorDiana(_posiciones(2))).fit(X, y + 1)
    np.testing.assert_allclose(m.predict(X), [6, 6, 10, 10])
