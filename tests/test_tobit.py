"""La regresión de Tobit tiene que usar la censura del lado correcto.

Lo que estas pruebas atan: que el gradiente analítico coincida con el numérico
(sin eso L-BFGS converge a cualquier parte), que con datos exactos recupere la
recta, y que con censura recupere la pendiente verdadera donde borrar o tratar
como exactos los censurados la sesga.
"""

import numpy as np
from scipy.optimize import check_grad
from sklearn.linear_model import LinearRegression

from src.models.tobit import RegresionTobit, verosimilitud

INF = np.inf


def _datos(n=4000, seed=0, corte=5.0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    y = 6.0 + X @ np.array([1.0, -0.5, 0.0]) + rng.normal(scale=0.7, size=n)
    inferior, superior = y.copy(), y.copy()
    cens = y < corte                       # «< 5»: lo único que se sabe es que cae por debajo
    inferior[cens], superior[cens] = -INF, corte
    return X, y, inferior, superior


def test_el_gradiente_analitico_coincide_con_el_numerico():
    X, _, inf, sup = _datos(n=300)
    # una derecha y un intervalo finito para tocar todas las ramas
    inf[0], sup[0] = 7.0, INF
    inf[1], sup[1] = 5.0, 6.0
    theta = np.array([0.3, -0.2, 0.1, 5.5, 0.1])
    f = lambda t: verosimilitud(t, X, inf, sup, 1e-3)[0]   # noqa: E731
    g = lambda t: verosimilitud(t, X, inf, sup, 1e-3)[1]   # noqa: E731
    assert check_grad(f, g, theta) < 1e-4


def test_con_datos_exactos_recupera_la_recta():
    X, y, _, _ = _datos()
    m = RegresionTobit(alfa=0.0).fit(X, y, y)
    ols = LinearRegression().fit(X, y)
    np.testing.assert_allclose(m.predict(X), ols.predict(X), atol=1e-2)


def test_con_censura_recupera_la_pendiente_donde_tratarlos_como_exactos_la_sesga():
    X, y, inf, sup = _datos()
    tobit = RegresionTobit(alfa=0.0).fit(X, inf, sup)
    pendiente = tobit.pesos_[0] / tobit.escala_[0]
    # tratar la cota como si fuera el valor medido aplana la recta
    y_cota = np.where(np.isfinite(inf), inf, sup)
    ingenuo = LinearRegression().fit(X, y_cota).coef_[0]
    assert abs(pendiente - 1.0) < 0.05
    assert abs(ingenuo - 1.0) > abs(pendiente - 1.0) + 0.05


def test_leer_la_censura_al_reves_se_nota():
    X, y, inf, sup = _datos()
    alreves_inf, alreves_sup = inf.copy(), sup.copy()
    izq = np.isneginf(inf)
    alreves_inf[izq], alreves_sup[izq] = sup[izq], INF       # «< 5» leído como «> 5»
    bien = RegresionTobit(alfa=0.0).fit(X, inf, sup)
    mal = RegresionTobit(alfa=0.0).fit(X, alreves_inf, alreves_sup)
    err = lambda m: np.mean((m.predict(X) - y) ** 2)         # noqa: E731
    # `bien` queda en el piso del ruido (0.7² = 0.49); `mal` lo supera con holgura
    assert err(mal) > 1.3 * err(bien)
