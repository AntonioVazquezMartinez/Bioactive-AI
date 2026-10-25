"""Los baselines de regresión no pueden mezclar lo que cada uno ve.

Atan que `ridge_exactas` ignore las cotas, que el Tobit las use, y que el
arnés devuelva una fila por (modelo, semilla, pliegue, estrato) sin filtrar la
prueba ni las cotas por su cuenta.
"""

import numpy as np

from src.models.baseline_regresion import (baselines, evaluar_baselines, intervalo_util,
                                           tabla)

INF = np.inf


def _datos(n=1500, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 4))
    y = 6.0 + X @ np.array([1.0, -0.6, 0.3, 0.0]) + rng.normal(scale=0.5, size=n)
    inf, sup = y.copy(), y.copy()
    cens = y < 5.0
    inf[cens], sup[cens] = -INF, 5.0
    clase = np.where(y >= 5.0, 1.0, 0.0)
    grupos = np.arange(n)
    estratos = np.where(np.arange(n) % 2 == 0, "a", "b")
    return X, inf, sup, grupos, estratos, clase


def test_ridge_ignora_las_cotas_y_el_tobit_las_usa():
    X, inf, sup, *_ = _datos()
    solo = baselines()["ridge_exactas"].fit(X, inf, sup)
    # lo que ve Ridge no cambia si las cotas se vuelven basura
    inf2, sup2 = inf.copy(), sup.copy()
    c = np.isneginf(inf)
    inf2[c], sup2[c] = -INF, 99.0
    solo2 = baselines()["ridge_exactas"].fit(X, inf2, sup2)
    np.testing.assert_allclose(solo.predict(X), solo2.predict(X))
    tobit = baselines()["tobit"].fit(X, inf, sup)
    tobit2 = baselines()["tobit"].fit(X, inf2, sup2)
    assert not np.allclose(tobit.predict(X), tobit2.predict(X))


def test_el_arnes_devuelve_una_fila_por_modelo_semilla_pliegue_y_estrato():
    X, inf, sup, g, est, clase = _datos()
    res = evaluar_baselines(X, inf, sup, g, est, clase, semillas=(0,), pliegues=3)
    assert set(res["modelo"]) == {"media", "ridge_exactas", "tobit"}
    assert len(res[(res.estrato == "todos")]) == 3 * 3
    t = tabla(res)
    assert t.loc["media", "concordancia"] == 0.5          # predecir siempre lo mismo
    assert t.loc["tobit", "concordancia"] > 0.8


def test_intervalo_util_descarta_sin_cota_y_vacio():
    inf = np.array([-INF, 5.0, 6.0, -INF])
    sup = np.array([INF, 4.0, 6.0, 5.0])
    assert intervalo_util(inf, sup).tolist() == [False, False, True, True]
