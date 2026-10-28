"""El piso por diana tiene que promediar por diana y no mirar la química.

Atan las tres cosas que lo hacen un piso válido: que devuelva exactamente el
promedio de cada diana, que una diana que no cayó en el pliegue de entrenamiento
caiga al promedio global, y que una matriz cuyo bloque final dejó de ser one-hot
reviente en vez de responder un número creíble y equivocado.
"""

import numpy as np
import pytest

from src.models.pisos import MediaPorDiana


def _matriz(dianas, k, n_descriptores=3, seed=0):
    """`X` con columnas de ruido y el one-hot de `dianas` al final, como `tareas.py`.

    `k` se pasa aparte y no se deduce de `dianas`, porque hay que poder armar una
    matriz de entrenamiento a la que le falte una de las dianas.
    """
    rng = np.random.default_rng(seed)
    dianas = np.asarray(dianas)
    ruido = rng.normal(size=(len(dianas), n_descriptores))
    onehot = np.eye(k)[dianas]
    return np.hstack([ruido, onehot])


def test_predice_el_promedio_de_cada_diana():
    # Dos filas de la diana 0, con promedio 6.5, y tres de la 1, con promedio 5.0.
    X = _matriz([0, 0, 1, 1, 1], k=2)
    y = np.array([7.0, 6.0, 5.0, 5.5, 4.5])

    piso = MediaPorDiana(2).fit(X, y)

    np.testing.assert_allclose(piso.predict(X), [6.5, 6.5, 5.0, 5.0, 5.0])


def test_no_distingue_moleculas_dentro_de_la_misma_diana():
    """La propiedad que lo define: la química de la fila no cambia su predicción."""
    X = _matriz([0, 0, 1, 1, 1], k=2)
    y = np.array([7.0, 6.0, 5.0, 5.5, 4.5])
    piso = MediaPorDiana(2).fit(X, y)

    # Se cambian los descriptores sin tocar el bloque de dianas.
    otra = X.copy()
    otra[:, :-2] = otra[:, :-2] * 100.0 + 7.0

    np.testing.assert_allclose(piso.predict(X), piso.predict(otra))


def test_con_tres_dianas_ninguna_se_funde_con_otra():
    """Con dos dianas, confundir el índice solo las renombra y se cancela entre el
    ajuste y la predicción. Hacen falta tres para que mezclarlas se note."""
    X = _matriz([0, 0, 1, 1, 2, 2], k=3)
    y = np.array([7.0, 8.0, 5.0, 6.0, 3.0, 4.0])

    piso = MediaPorDiana(3).fit(X, y)

    np.testing.assert_allclose(piso.predict(X), [7.5, 7.5, 5.5, 5.5, 3.5, 3.5])


def test_una_diana_ausente_cae_al_promedio_global():
    # El entrenamiento solo trae la diana 0; el promedio global de y es 6.0.
    X_entrena = _matriz([0, 0, 0], k=2)
    y = np.array([7.0, 6.0, 5.0])
    piso = MediaPorDiana(2).fit(X_entrena, y)

    X_valida = _matriz([1], k=2)

    assert piso.predict(X_valida)[0] == pytest.approx(6.0)


def test_un_bloque_que_no_es_onehot_revienta():
    X = _matriz([0, 0, 1], k=2)
    X[0, -2:] = 0.0                      # una fila que ya no declara diana
    y = np.array([7.0, 6.0, 5.0])

    with pytest.raises(ValueError, match="one-hot"):
        MediaPorDiana(2).fit(X, y)


def test_tambien_revienta_al_predecir_y_no_solo_al_ajustar():
    """La comprobación vive en el ayudante, así que protege los dos caminos."""
    X = _matriz([0, 0, 1], k=2)
    y = np.array([7.0, 6.0, 5.0])
    piso = MediaPorDiana(2).fit(X, y)

    roto = X.copy()
    roto[1, -2:] = 1.0                   # dos dianas a la vez

    with pytest.raises(ValueError, match="one-hot"):
        piso.predict(roto)
