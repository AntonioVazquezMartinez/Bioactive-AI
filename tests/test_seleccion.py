import numpy as np

from src.features.seleccion import casi_constantes, filtro_correlacion, poder_univariado


def test_casi_constantes_usa_la_frecuencia_del_valor_mas_comun():
    X = np.column_stack([np.zeros(200),                      # constante
                         np.r_[np.ones(2), np.zeros(198)],   # 99% un valor
                         np.arange(200.0) % 7])              # variada
    assert list(casi_constantes(X, 0.99)) == [False, False, True]


def test_casi_constantes_no_depende_de_la_escala():
    x = np.r_[np.ones(10), np.zeros(190)]
    X = np.column_stack([x, x * 1e-4])
    assert list(casi_constantes(X, 0.99)) == [True, True]


def test_filtro_de_correlacion_no_sigue_comparando_una_columna_descartada():
    """Regresión del `break` ausente. La 0 se parece a la 1 y a la 2, pero la 1 y la
    2 no se parecen entre sí. La 0 pierde contra la 1; sin el `break` seguía
    comparándose con la 2 y, ya fuera, la descartaba por redundante."""
    rng = np.random.default_rng(0)
    z = rng.normal(size=5000)
    ruido = lambda: rng.normal(size=5000)  # noqa: E731
    X = np.column_stack([z,
                         0.97 * z + np.sqrt(1 - 0.97**2) * ruido(),
                         0.97 * z + np.sqrt(1 - 0.97**2) * ruido()])
    C = np.corrcoef(X, rowvar=False)
    assert C[0, 1] > 0.95 and C[0, 2] > 0.95 and C[1, 2] < 0.95
    poder = np.array([0.3, 0.4, 0.1])
    assert list(filtro_correlacion(X, poder, 0.95)) == [False, True, True]


def test_filtro_de_correlacion_es_invariante_a_transformaciones_monotonas():
    rng = np.random.default_rng(1)
    X = rng.lognormal(size=(300, 8))
    X[:, 4] = X[:, 3] * 2 + rng.normal(scale=0.01, size=300)
    y = rng.integers(0, 2, 300)
    poder = poder_univariado(X, y)
    a = filtro_correlacion(X, poder)
    b = filtro_correlacion(np.log(X + 1) * 7 + 3, poder_univariado(np.log(X + 1), y))
    assert list(a) == list(b)


def test_las_protegidas_ganan_el_par_aunque_separen_menos():
    rng = np.random.default_rng(2)
    z = rng.normal(size=400)
    X = np.column_stack([z, z + rng.normal(scale=0.01, size=400)])
    poder = np.array([0.1, 0.4])
    assert list(filtro_correlacion(X, poder)) == [False, True]
    assert list(filtro_correlacion(X, poder, protegidas=(0,))) == [True, False]


def test_depuracion_aprende_con_el_ajuste_y_deja_pasar_la_diana():
    from src.features.seleccion import DepuracionDescriptores

    rng = np.random.default_rng(0)
    n = 2000
    y = rng.normal(size=n)
    util = y + rng.normal(size=n)
    X = np.column_stack([
        util,                                   # 0: informativa
        util + 0.01 * rng.normal(size=n),       # 1: casi duplicada de la 0
        np.r_[np.ones(n - 5), np.zeros(5)],     # 2: casi constante (99.75%)
        rng.normal(size=n),                     # 3: ruido, pero distinta
        (rng.random(n) > .5).astype(float),     # 4: diana en 0/1
    ])
    t = DepuracionDescriptores(n_descriptores=4).fit(X, y)
    assert list(t.columnas_) in ([0, 3, 4], [1, 3, 4])    # una de las dos duplicadas
    assert list(t.quitadas_constantes_) == [2] and len(t.quitadas_redundantes_) == 1
    assert t.transform(X).shape == (n, 3)


def test_depuracion_protege_las_columnas_indicadas():
    from src.features.seleccion import DepuracionDescriptores

    rng = np.random.default_rng(1)
    n = 2000
    y = rng.normal(size=n)
    a = y + rng.normal(size=n)
    X = np.column_stack([a + 0.01 * rng.normal(size=n), a])   # la 0 es peor que la 1
    sin = DepuracionDescriptores(n_descriptores=2).fit(X, y)
    con = DepuracionDescriptores(n_descriptores=2, protegidas=(0,)).fit(X, y)
    assert len(sin.columnas_) == 1 and list(con.columnas_) == [0]


def test_seleccion_l1_conserva_lo_que_explica_el_objetivo_y_protege_lo_pedido():
    from src.features.seleccion import SeleccionL1

    rng = np.random.default_rng(2)
    n = 3000
    X = rng.normal(size=(n, 6))
    y = 2 * X[:, 0] - 1.5 * X[:, 1] + 0.1 * rng.normal(size=n)       # solo la 0 y la 1 importan
    diana = (rng.random((n, 2)) > .5).astype(float)
    Xm = np.hstack([X, diana])
    t = SeleccionL1(n_descriptores=6, alpha=0.05).fit(Xm, y)
    assert list(t.descriptores_) == [0, 1] and list(t.quitadas_) == [2, 3, 4, 5]
    assert t.transform(Xm).shape == (n, 4)                                # 2 descriptores + diana
    con = SeleccionL1(n_descriptores=6, alpha=0.05, protegidas=(4,)).fit(Xm, y)
    assert list(con.descriptores_) == [0, 1, 4]
