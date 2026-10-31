"""Pruebas unitarias para la regresión AFT con XGBoost (src/models/aft.py).

Verifica el envoltorio `RegresionAFT`, el cumplimiento del contrato de scikit-learn
(`BaseEstimator`, `clone`), el descarte de filas no informativas y cotas inválidas/NaN,
el manejo de censura y la conversión de concentración a pActividad en `predict`.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import spearmanr
from sklearn.base import clone
from sklearn.exceptions import NotFittedError

from src.models.aft import RegresionAFT

INF = np.inf


@pytest.fixture
def datos_censurados():
    """Genera datos sintéticos con relación lineal más ruido y censura a pActividad 5.0 (10 µM)."""
    rng = np.random.default_rng(42)
    n = 200
    X = rng.normal(size=(n, 3))
    # Mayor X[:, 0] implica mayor potencia pActividad (menor concentración en µM)
    y_latente = 5.5 + X[:, 0] * 1.2 - X[:, 1] * 0.6 + rng.normal(scale=0.3, size=n)

    inferior = y_latente.copy()
    superior = y_latente.copy()

    # Censura por la izquierda en pActividad: mediciones < 5.0 (concentración > 10 µM)
    cens = y_latente < 5.0
    inferior[cens] = -INF
    superior[cens] = 5.0

    return X, y_latente, inferior, superior


def test_clonacion_sklearn_clone():
    """`RegresionAFT` debe cumplir con el contrato de clone de scikit-learn."""
    modelo = RegresionAFT(
        distribucion="logistic",
        escala=1.5,
        rondas=50,
        profundidad=4,
        semilla=42,
        n_jobs=2,
    )
    clon = clone(modelo)
    assert clon is not modelo
    assert clon.distribucion == "logistic"
    assert clon.escala == 1.5
    assert clon.rondas == 50
    assert clon.profundidad == 4
    assert clon.semilla == 42
    assert clon.n_jobs == 2
    assert not hasattr(clon, "booster_")


def test_predict_sin_fit_lanza_error():
    """Llamar a predict antes de fit debe lanzar NotFittedError."""
    modelo = RegresionAFT()
    with pytest.raises(NotFittedError):
        modelo.predict(np.zeros((5, 3)))


def test_descarte_de_filas_no_informativas(datos_censurados):
    """Debe descartar filas con nan (contradictorias), [-inf, inf] y cota inferior cero."""
    X, _, inferior, superior = datos_censurados

    # Añadir 3 filas problemáticas:
    # 1. Contradictoria (inf > sup) -> nan en micromolar
    # 2. Sin cotas [-inf, inf] -> [0, inf] en micromolar (inf_um == 0)
    # 3. sup = inf -> inf_um == 0 (concentración [0, L], sin cota inferior positiva)
    X_extra = np.vstack([X, np.zeros((3, 3))])
    inf_extra = np.concatenate([inferior, [6.0, -INF, 5.0]])
    sup_extra = np.concatenate([superior, [4.0, INF, INF]])

    modelo = RegresionAFT(rondas=10, profundidad=2, semilla=0)
    modelo.fit(X_extra, inf_extra, sup_extra)

    # Las 3 filas deben haberse descartado porque inf_um <= 0 o es nan
    assert modelo.n_descartadas_ >= 3
    assert hasattr(modelo, "booster_")


def test_falla_si_no_hay_filas_validas():
    """Debe lanzar ValueError si todas las filas son no informativas."""
    X = np.ones((4, 2))
    # Todas con inf > sup (contradictorias) o [-inf, inf]
    inferior = np.array([6.0, 7.0, -INF, -INF])
    superior = np.array([5.0, 4.0, INF, INF])

    modelo = RegresionAFT()
    with pytest.raises(ValueError, match="inf_um > 0"):
        modelo.fit(X, inferior, superior)


def test_prediccion_en_escala_pactividad_y_signo_correcto(datos_censurados):
    """`predict` debe devolver valores en pActividad (correlación positiva con potencia)."""
    X, y_latente, inferior, superior = datos_censurados

    modelo = RegresionAFT(rondas=80, profundidad=3, semilla=0)
    modelo.fit(X, inferior, superior)

    preds = modelo.predict(X)
    assert preds.shape == (len(X),)
    # Valores plausibles de pActividad (alrededor de 3 a 9, nunca concentraciones gigantes ni negativas)
    assert (preds > 0.0).all()
    assert (preds < 14.0).all()

    # Si se olvidara el signo 6 - log10(µM), la correlación con la potencia sería fuertemente negativa
    corr, _ = spearmanr(preds, y_latente)
    assert corr > 0.8, f"La correlación con la potencia verdadera es baja o invertida: {corr}"


@pytest.mark.parametrize("distribucion", ["normal", "logistic", "extreme"])
def test_distribuciones_soportadas(datos_censurados, distribucion):
    """Las tres opciones de `aft_loss_distribution` deben entrenar y predecir sin error."""
    X, _, inferior, superior = datos_censurados
    modelo = RegresionAFT(distribucion=distribucion, rondas=20, profundidad=2, semilla=0)
    modelo.fit(X, inferior, superior)
    preds = modelo.predict(X)
    assert preds.shape == (len(X),)
    assert np.isfinite(preds).all()


def test_cota_inferior_nan_se_descarta_sin_envenenar_prediccion(datos_censurados):
    """Una fila con cota inferior NaN en pActividad debe ser descartada sin envenenar predicciones."""
    X, _, inferior, superior = datos_censurados

    # Añadir una fila con cota inferior NaN y cota superior 5.0
    X_con_nan = np.vstack([X, [0.0, 0.0, 0.0]])
    inf_con_nan = np.append(inferior, np.nan)
    sup_con_nan = np.append(superior, 5.0)

    modelo = RegresionAFT(rondas=20, profundidad=2, semilla=42)
    modelo.fit(X_con_nan, inf_con_nan, sup_con_nan)

    assert modelo.n_descartadas_ == 1
    preds = modelo.predict(X_con_nan)
    assert preds.shape == (len(X_con_nan),)
    assert np.isfinite(preds).all()
    assert not np.isnan(preds).any()

