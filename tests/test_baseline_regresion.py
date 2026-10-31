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
    assert set(res["modelo"]) == {"media", "ridge_exactas", "ridge_cota_imputada", "tobit"}
    assert len(res[(res.estrato == "todos")]) == 4 * 3
    t = tabla(res)
    assert t.loc["media", "concordancia"] == 0.5          # predecir siempre lo mismo
    assert t.loc["tobit", "concordancia"] > 0.8


def test_intervalo_util_descarta_sin_cota_y_vacio():
    inf = np.array([-INF, 5.0, 6.0, -INF])
    sup = np.array([INF, 4.0, 6.0, 5.0])
    assert intervalo_util(inf, sup).tolist() == [False, False, True, True]


def test_la_imputada_toma_la_cota_como_valor_y_ridge_exactas_no_la_ve():
    X, inf, sup, *_ = _datos()
    imp = baselines()["ridge_cota_imputada"].fit(X, inf, sup)
    # a mano: el valor que debió ver es la cota donde el límite inferior es -inf
    valor = np.where(np.isfinite(inf), inf, sup)
    ridge = baselines()["ridge_exactas"].modelo.fit(X, valor)
    np.testing.assert_allclose(imp.predict(X), ridge.predict(X))
    solo = baselines()["ridge_exactas"].fit(X, inf, sup)
    assert not np.allclose(imp.predict(X), solo.predict(X))


def test_solo_exactas_propaga_grupos_filtrados():
    """`SoloExactas` debe exponer `necesita_grupos` y pasar solo los grupos de las filas exactas."""
    class EspiaAgrupado:
        necesita_grupos = True
        def fit(self, X, y, grupos=None):
            self.grupos_recibidos_ = grupos
            return self
        def predict(self, X):
            return np.zeros(len(X))

    espia = EspiaAgrupado()
    from src.models.baseline_regresion import SoloExactas
    envoltorio = SoloExactas(espia)
    assert envoltorio.necesita_grupos is True

    X = np.ones((5, 2))
    inf = np.array([1.0, -INF, 3.0, -INF, 5.0])
    sup = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    grupos = np.array(["g1", "g2", "g3", "g4", "g5"])

    envoltorio.fit(X, inf, sup, grupos=grupos)
    # Solo las filas 0, 2 y 4 son exactas
    assert list(espia.grupos_recibidos_) == ["g1", "g3", "g5"]


def test_imputada_en_cota_propaga_grupos_filtrados():
    """`ImputadaEnCota` debe exponer `necesita_grupos` y pasar solo los grupos de las filas útiles."""
    class EspiaAgrupado:
        necesita_grupos = True
        def fit(self, X, y, grupos=None):
            self.grupos_recibidos_ = grupos
            return self
        def predict(self, X):
            return np.zeros(len(X))

    espia = EspiaAgrupado()
    from src.models.baseline_regresion import ImputadaEnCota
    envoltorio = ImputadaEnCota(espia)
    assert envoltorio.necesita_grupos is True

    X = np.ones((4, 2))
    # fila 0: sin cota (-inf, inf) -> no util
    # fila 1: cota cruzada (6, 4) -> no util
    # fila 2: censurada finita (-inf, 5) -> util
    # fila 3: exacta (3, 3) -> util
    inf = np.array([-INF, 6.0, -INF, 3.0])
    sup = np.array([INF, 4.0, 5.0, 3.0])
    grupos = np.array(["g0", "g1", "g2", "g3"])

    envoltorio.fit(X, inf, sup, grupos=grupos)
    assert list(espia.grupos_recibidos_) == ["g2", "g3"]


def test_evaluar_baselines_con_modelo_personalizado_que_necesita_grupos():
    """`evaluar_baselines` debe permitir pasar modelos y entregar grupos al pliegue."""
    from sklearn.linear_model import Ridge
    from src.models.baseline_regresion import SoloExactas
    from src.models.ensambles import ApiladoAgrupado

    X, inf, sup, _, est, clase = _datos(n=120)
    # 10 grupos con 12 muestras cada uno
    grupos = np.repeat(np.arange(10), 12)
    modelo_apilado = SoloExactas(ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=2))

    res = evaluar_baselines(X, inf, sup, grupos, est, clase, semillas=(0,), pliegues=2,
                            modelos={"apilado": modelo_apilado})
    assert set(res["modelo"]) == {"apilado"}
    assert len(res) > 0
    assert np.isfinite(res["concordancia"]).all()


def test_solo_exactas_con_apilado_grupo_totalmente_censurado():
    """Si un grupo entero no tiene mediciones exactas, SoloExactas lo filtra y ApiladoAgrupado
    debe ajustarse correctamente con los grupos únicos restantes si superan los pliegues."""
    from sklearn.linear_model import Ridge
    from src.models.baseline_regresion import SoloExactas
    from src.models.ensambles import ApiladoAgrupado

    X = np.ones((6, 2))
    # g0 tiene exactas, g1 tiene exactas, g2 está totalmente censurado (-inf, 5)
    inf = np.array([2.0, 2.5, 3.0, 3.5, -INF, -INF])
    sup = np.array([2.0, 2.5, 3.0, 3.5, 5.0, 5.0])
    grupos = np.array(["g0", "g0", "g1", "g1", "g2", "g2"])

    # pliegues=2, quedan 2 grupos únicos ('g0', 'g1') post-filtrado
    apilado = SoloExactas(ApiladoAgrupado(bases=[("r", Ridge())], pliegues=2))
    apilado.fit(X, inf, sup, grupos=grupos)
    preds = apilado.predict(X)
    assert preds.shape == (6,)
    assert np.isfinite(preds).all()


def test_evaluar_baselines_acepta_matriz_dispersa():
    """`evaluar_baselines` debe aceptar `scipy.sparse.csr_matrix` sin tronar ni densificar."""
    from scipy import sparse
    from sklearn.base import BaseEstimator, RegressorMixin
    from src.models.baseline_regresion import SoloExactas

    vio_dispersa = []

    class _EspiaDispersa(BaseEstimator, RegressorMixin):
        def fit(self, X, y=None):
            vio_dispersa.append(sparse.issparse(X))
            return self

        def predict(self, X):
            vio_dispersa.append(sparse.issparse(X))
            return np.zeros(X.shape[0])

    X, inf, sup, _, est, clase = _datos(n=60)
    grupos = np.repeat(np.arange(6), 10)
    X_sp = sparse.csr_matrix(X)
    modelo = SoloExactas(_EspiaDispersa())
    res = evaluar_baselines(X_sp, inf, sup, grupos, est, clase, semillas=(0,), pliegues=2,
                            modelos={"espia": modelo})
    assert len(res) > 0
    assert np.isfinite(res["concordancia"]).all()
    assert len(vio_dispersa) > 0 and all(vio_dispersa)




