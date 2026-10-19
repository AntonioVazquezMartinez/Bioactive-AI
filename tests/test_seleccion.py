import numpy as np

from src.features.seleccion import FiltroCasiConstante, FiltroCorrelacion, descartar_correlacionadas


def test_casi_constante_no_depende_de_la_escala():
    rng = np.random.default_rng(1)
    carga = rng.normal(scale=0.05, size=500)          # varianza ~0.0025, no es constante
    rara = np.zeros(500)
    rara[:3] = 1                                       # solo 3 filas distintas del modo
    X = np.column_stack([carga, rara, carga * 1000])
    soporte = FiltroCasiConstante(min_distintas=10).fit(X).get_support()
    assert soporte.tolist() == [True, False, True]


def test_una_descartada_no_elimina_a_otra():
    # A se parece a B y a C; B y C no se parecen. Puntajes B > A > C.
    # Lo correcto es quitar solo A: C ya no tiene con quién ser redundante.
    C = np.array([[1.0, 0.99, 0.99],
                  [0.99, 1.0, 0.10],
                  [0.99, 0.10, 1.0]])
    puntaje = np.array([2.0, 3.0, 1.0])
    assert descartar_correlacionadas(C, puntaje, 0.95) == {0}


def test_conserva_la_de_mayor_puntaje():
    C = np.array([[1.0, 0.98], [0.98, 1.0]])
    assert descartar_correlacionadas(C, np.array([5.0, 1.0]), 0.95) == {1}
    assert descartar_correlacionadas(C, np.array([1.0, 5.0]), 0.95) == {0}


def test_no_depende_de_transformaciones_monotonas():
    rng = np.random.default_rng(0)
    x = rng.lognormal(size=(300, 1))
    X = np.hstack([x, np.log(x), x ** 3, rng.normal(size=(300, 1))])
    y = (X[:, 3] + rng.normal(scale=0.5, size=300) > 0).astype(int)
    crudo = FiltroCorrelacion().fit(X, y).get_support()
    escalado = (X - X.min(0)) / (X.max(0) - X.min(0))
    assert (FiltroCorrelacion().fit(escalado, y).get_support() == crudo).all()
    # las tres primeras son la misma variable en rangos: sobrevive una
    assert crudo[:3].sum() == 1 and crudo[3]
