"""Pruebas unitarias para los ensambles de regresión (Avance 5).

Verifica el envoltorio `ApiladoAgrupado` y la fábrica `ensambles` de
`src/models/ensambles.py`, asegurando el cumplimiento de contratos de scikit-learn,
la prevención de fuga de datos en particiones internas agrupadas y la correcta
configuración de modelos homogéneos y heterogéneos.
"""

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp
from sklearn.base import clone
from sklearn.ensemble import (
    BaggingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor,
    VotingRegressor,
)
from sklearn.exceptions import NotFittedError
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor

from src.models.ensambles import ApiladoAgrupado, ensambles


@pytest.fixture
def datos_regresion():
    """Genera datos sintéticos de regresión con estructura de grupos."""
    rng = np.random.default_rng(42)
    n = 120
    # 20 grupos con 6 muestras cada uno
    grupos = np.repeat(np.arange(20), 6)
    X = rng.normal(size=(n, 8))
    # y depende de X y de una componente por grupo
    efecto_grupo = rng.normal(size=20)[grupos]
    y = 5.0 + X[:, 0] * 1.5 - X[:, 1] * 0.8 + efecto_grupo * 0.5 + rng.normal(scale=0.2, size=n)
    return X, y, grupos


def test_necesita_grupos_es_true():
    """`ApiladoAgrupado` debe exponer `necesita_grupos = True` tanto en clase como en instancia."""
    assert ApiladoAgrupado.necesita_grupos is True
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor())]
    modelo = ApiladoAgrupado(bases=bases)
    assert modelo.necesita_grupos is True


def test_fit_sin_grupos_lanza_value_error(datos_regresion):
    """`fit(X, y)` sin el argumento `grupos` debe lanzar ValueError explicando la fuga."""
    X, y, _ = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor())]
    modelo = ApiladoAgrupado(bases=bases)

    with pytest.raises(ValueError, match="grupos"):
        modelo.fit(X, y)

    with pytest.raises(ValueError, match="scaffold|fuga"):
        modelo.fit(X, y, grupos=None)


def test_clonacion_sklearn_clone():
    """`ApiladoAgrupado` debe cumplir el contrato de clonación de scikit-learn."""
    bases = [("ridge", Ridge(alpha=10.0)), ("arbol", DecisionTreeRegressor(max_depth=3))]
    final = Ridge(alpha=1.0)
    modelo = ApiladoAgrupado(bases=bases, final=final, pliegues=4, semilla=123)

    clon = clone(modelo)
    assert clon is not modelo
    assert clon.pliegues == 4
    assert clon.semilla == 123
    assert clon.final.alpha == 1.0
    assert len(clon.bases) == 2
    assert clon.bases[0][0] == "ridge"
    assert not hasattr(clon, "estimador_")


def test_clonacion_modelo_ajustado(datos_regresion):
    """Clonar un modelo ya ajustado debe devolver una instancia limpia sin ajustar."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]
    modelo = ApiladoAgrupado(bases=bases, pliegues=3)
    modelo.fit(X, y, grupos=grupos)

    assert hasattr(modelo, "estimador_")
    clon = clone(modelo)
    assert not hasattr(clon, "estimador_")
    assert not hasattr(clon, "particiones_")


def test_el_apilado_de_adentro_recibe_las_particiones_agrupadas(datos_regresion):
    """Que particiones_ tenga particiones agrupadas no es evidencia de que el modelo las haya usado.

    Son dos líneas independientes: guardar las particiones en el atributo no evita
    la fuga si no se le inyectan al StackingRegressor. Esta prueba afirma que el
    estimador interno recibió exactamente esa lista mediante identidad (`is`).
    """
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]
    modelo = ApiladoAgrupado(bases=bases, pliegues=3)
    modelo.fit(X, y, grupos=grupos)

    assert hasattr(modelo, "particiones_")
    assert modelo.estimador_.cv is modelo.particiones_

    for fold_idx, (ajuste_idx, val_idx) in enumerate(modelo.particiones_):
        grupos_ajuste = set(grupos[ajuste_idx])
        grupos_val = set(grupos[val_idx])
        interseccion = grupos_ajuste & grupos_val
        assert not interseccion, f"Fuga de grupos detectada en pliegue interno {fold_idx}: {interseccion}"


def test_agrupar_la_validacion_interna_cambia_los_pesos_del_metamodelo():
    """Demuestra que agrupar por scaffold altera los pesos aprendidos por el metamodelo.

    Con partición al azar, el vecino más cercano (1-NN) de cada muestra cae en su mismo
    grupo en entrenamiento; predice casi perfecto fuera de pliegue y el metamodelo le
    asigna un peso dominante. Con partición agrupada, todo su grupo queda fuera, el
    vecino pertenece a otro grupo con otro desplazamiento, predice mal y el metamodelo
    lo castiga con un coeficiente sustancialmente menor que en la versión al azar.
    """
    rng = np.random.default_rng(0)
    n_grupos = 8
    filas_por_grupo = 15
    n = n_grupos * filas_por_grupo
    grupos = np.repeat(np.arange(n_grupos), filas_por_grupo)

    centros_x = rng.normal(0.0, 5.0, size=(n_grupos, 4))
    X = centros_x[grupos] + rng.normal(0.0, 0.2, size=(n, 4))

    desplazamiento = rng.normal(0.0, 10.0, size=n_grupos)
    y = 0.1 * X[:, 0] + desplazamiento[grupos] + rng.normal(0.0, 0.05, size=n)

    # Permutar para que los grupos no queden como bloques contiguos triviales
    perm = rng.permutation(n)
    X, y, grupos = X[perm], y[perm], grupos[perm]

    bases = [("knn", KNeighborsRegressor(n_neighbors=1)), ("ridge", Ridge(alpha=1.0))]
    final = Ridge(alpha=1.0)
    pliegues = 3
    semilla = 0

    # 1. ApiladoAgrupado (partición interna agrupada por scaffold)
    mod_agrupado = ApiladoAgrupado(bases=bases, final=final, pliegues=pliegues, semilla=semilla)
    mod_agrupado.fit(X, y, grupos=grupos)

    # 2. StackingRegressor con KFold al azar
    cv_azar = KFold(n_splits=pliegues, shuffle=True, random_state=semilla)
    mod_azar = StackingRegressor(estimators=bases, final_estimator=clone(final), cv=cv_azar)
    mod_azar.fit(X, y)

    coef_agrupado = mod_agrupado.final_estimator_.coef_
    coef_azar = mod_azar.final_estimator_.coef_

    # El coeficiente del 1-NN (índice 0) sale claramente más bajo en la versión agrupada
    assert coef_agrupado[0] < coef_azar[0] - 0.5


def test_semilla_cambia_particion_interna(datos_regresion):
    """La semilla debe gobernar el barajado de grupos en la partición interna."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge())]

    m0 = ApiladoAgrupado(bases=bases, pliegues=3, semilla=0).fit(X, y, grupos=grupos)
    m1 = ApiladoAgrupado(bases=bases, pliegues=3, semilla=1).fit(X, y, grupos=grupos)

    assert len(m0.particiones_) == 3
    assert len(m1.particiones_) == 3

    difieren = any(
        not (np.array_equal(p0[0], p1[0]) and np.array_equal(p0[1], p1[1]))
        for p0, p1 in zip(m0.particiones_, m1.particiones_)
    )
    assert difieren, "Las particiones internas no deben ser idénticas cuando cambia la semilla"


def test_predict_antes_de_fit_lanza_error(datos_regresion):
    """Llamar a `predict` antes de `fit` debe lanzar error de estimador no ajustado."""
    X, _, _ = datos_regresion
    bases = [("ridge", Ridge())]
    modelo = ApiladoAgrupado(bases=bases)

    with pytest.raises((NotFittedError, ValueError)):
        modelo.predict(X)


def test_apilado_ajuste_y_prediccion(datos_regresion):
    """`ApiladoAgrupado` debe ajustar correctamente y predecir valores continuos válidos."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]
    modelo = ApiladoAgrupado(bases=bases, pliegues=3)
    retorno = modelo.fit(X, y, grupos=grupos)

    assert retorno is modelo
    preds = modelo.predict(X)
    assert isinstance(preds, np.ndarray)
    assert preds.shape == (len(y),)
    assert np.isfinite(preds).all()


def test_apilado_con_estimador_final(datos_regresion):
    """Verifica que el estimador meta final especificado sea respetado en el ajuste."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]
    final = Ridge(alpha=5.0)
    modelo = ApiladoAgrupado(bases=bases, final=final, pliegues=3)
    modelo.fit(X, y, grupos=grupos)

    assert hasattr(modelo, "final_estimator_")
    assert isinstance(modelo.final_estimator_, Ridge)
    assert modelo.final_estimator_.alpha == 5.0


def test_ensambles_retorna_cinco_claves_y_tipos_correctos():
    """`ensambles()` debe devolver exactamente las 5 claves esperadas con los tipos correctos."""
    modelos = ensambles()
    claves_esperadas = {"bosque", "boosting", "bagging_knn", "votacion", "apilado"}
    assert set(modelos.keys()) == claves_esperadas

    assert isinstance(modelos["bosque"], RandomForestRegressor)
    assert isinstance(modelos["boosting"], HistGradientBoostingRegressor)
    assert isinstance(modelos["bagging_knn"], BaggingRegressor)
    assert isinstance(modelos["bagging_knn"].estimator, KNeighborsRegressor)
    assert isinstance(modelos["votacion"], VotingRegressor)
    assert isinstance(modelos["apilado"], ApiladoAgrupado)

    # Las bases por omisión reflejan las mediciones del #164 (Ridge y kNN)
    assert [n for n, _ in modelos["votacion"].estimators] == ["ridge", "knn"]
    assert isinstance(modelos["votacion"].estimators[1][1], KNeighborsRegressor)
    assert [n for n, _ in modelos["apilado"].bases] == ["ridge", "knn"]
    assert isinstance(modelos["apilado"].bases[1][1], KNeighborsRegressor)


def test_voting_regressor_no_envuelto_ni_agrupado():
    """`VotingRegressor` no debe estar envuelto en lógica agrupada ni exponer `necesita_grupos`."""
    modelos = ensambles()
    votacion = modelos["votacion"]

    assert type(votacion) is VotingRegressor
    assert not getattr(votacion, "necesita_grupos", False)


def test_bases_personalizadas_en_votacion_y_apilado():
    """Pasar `bases` personalizadas a `ensambles` debe transmitirlas a `votacion` y `apilado`."""
    bases_personalizadas = [
        ("r_baja", Ridge(alpha=0.1)),
        ("r_alta", Ridge(alpha=100.0)),
    ]
    modelos = ensambles(bases=bases_personalizadas)

    assert modelos["votacion"].estimators == bases_personalizadas
    assert modelos["apilado"].bases == bases_personalizadas


def test_bases_personalizadas_como_tupla(datos_regresion):
    """`ensambles` debe aceptar `bases` como tupla de pares y permitir su ajuste."""
    X, y, grupos = datos_regresion
    bases_tupla = (
        ("r_baja", Ridge(alpha=0.1)),
        ("r_alta", Ridge(alpha=100.0)),
    )
    modelos = ensambles(bases=bases_tupla)

    assert modelos["apilado"].bases == bases_tupla
    # VotingRegressor convierte tupla a lista internamente para cumplir validación de sklearn
    assert list(modelos["votacion"].estimators) == list(bases_tupla)

    # Comprobar que ambos pueden ajustarse y predecir
    modelos["votacion"].fit(X, y)
    preds_vot = modelos["votacion"].predict(X)
    assert preds_vot.shape == (len(y),)
    assert np.isfinite(preds_vot).all()

    modelos["apilado"].fit(X, y, grupos=grupos)
    preds_api = modelos["apilado"].predict(X)
    assert preds_api.shape == (len(y),)
    assert np.isfinite(preds_api).all()


def test_todos_los_ensambles_ajustan_y_predicen(datos_regresion):
    """Todos los 5 modelos de `ensambles()` deben poder ajustarse y predecir sobre datos de regresión."""
    X, y, grupos = datos_regresion
    modelos = ensambles(semilla=42)

    for nombre, modelo in modelos.items():
        if getattr(modelo, "necesita_grupos", False):
            modelo.fit(X, y, grupos=grupos)
        else:
            modelo.fit(X, y)

        preds = modelo.predict(X)
        assert isinstance(preds, np.ndarray), f"Modelo {nombre} no devolvió ndarray"
        assert preds.shape == (len(y),), f"Modelo {nombre} devolvió forma incorrecta {preds.shape}"
        assert np.isfinite(preds).all(), f"Modelo {nombre} devolvió NaN o infinitos"


def test_dataframe_con_indices_string_y_grupos_smiles():
    """`ApiladoAgrupado` debe tolerar DataFrames con índices string y andamios SMILES como grupos."""
    idx = [f"mol_{i}" for i in range(12)]
    X_df = pd.DataFrame(
        {
            "descriptor_1": np.linspace(0.1, 2.0, 12),
            "descriptor_2": np.linspace(10.0, 50.0, 12),
        },
        index=idx,
    )
    y_ser = pd.Series(np.linspace(4.0, 8.5, 12), index=idx)
    scaffolds = [
        "c1ccccc1", "c1ccccc1", "c1ccccc1", "c1ccccc1",
        "c1ccncc1", "c1ccncc1", "c1ccncc1", "c1ccncc1",
        "c1ccc2ccccc2c1", "c1ccc2ccccc2c1", "c1ccc2ccccc2c1", "c1ccc2ccccc2c1",
    ]
    grupos_ser = pd.Series(scaffolds, index=idx)

    modelo = ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=3)
    modelo.fit(X_df, y_ser, grupos=grupos_ser)

    assert hasattr(modelo, "n_features_in_")
    assert modelo.n_features_in_ == 2
    assert hasattr(modelo, "feature_names_in_")
    assert list(modelo.feature_names_in_) == ["descriptor_1", "descriptor_2"]

    preds = modelo.predict(X_df)
    assert preds.shape == (12,)
    assert np.isfinite(preds).all()


def test_matriz_dispersa_scipy_csr():
    """`ApiladoAgrupado` debe operar correctamente sobre matrices dispersas scipy CSR."""
    rng = np.random.default_rng(99)
    X_sp = sp.csr_matrix(rng.normal(size=(15, 6)))
    y = rng.normal(size=15)
    grupos = np.repeat([0, 1, 2], 5)

    modelo = ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=3)
    modelo.fit(X_sp, y, grupos=grupos)

    assert modelo.n_features_in_ == 6
    preds = modelo.predict(X_sp)
    assert preds.shape == (15,)
    assert np.isfinite(preds).all()


def test_columna_vector_2d_y():
    """`ApiladoAgrupado` debe tolerar `y` con forma bidimensional (n, 1) sin advertencias."""
    import warnings

    rng = np.random.default_rng(101)
    X = rng.normal(size=(12, 4))
    y_2d = rng.normal(size=(12, 1))
    grupos = np.repeat([0, 1, 2], 4)

    modelo = ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=3)
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        modelo.fit(X, y_2d, grupos=grupos)

    # Ninguna advertencia de conversión de vector columna a 1D
    conversion_warns = [
        w for w in record if "DataConversionWarning" in str(w.category.__name__)
    ]
    assert not conversion_warns

    preds = modelo.predict(X)
    assert preds.shape == (12,)
    assert np.isfinite(preds).all()


def test_bases_como_iterador_o_generador():
    """`ensambles` debe admitir generadores sin agotar los estimadores para `apilado`."""
    generador_bases = (b for b in [("r1", Ridge(alpha=1.0)), ("r2", Ridge(alpha=10.0))])
    modelos = ensambles(bases=generador_bases)

    assert len(modelos["votacion"].estimators) == 2
    assert len(modelos["apilado"].bases) == 2

    rng = np.random.default_rng(42)
    X = rng.normal(size=(12, 3))
    y = rng.normal(size=12)
    grupos = np.repeat([0, 1, 2], 4)

    modelos["apilado"].fit(X, y, grupos=grupos)
    preds = modelos["apilado"].predict(X)
    assert preds.shape == (12,)
    assert np.isfinite(preds).all()


def test_score_r2_valido(datos_regresion):
    """`ApiladoAgrupado` debe implementar `.score(X, y)` heredado de RegressorMixin."""
    X, y, grupos = datos_regresion
    modelo = ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=3)
    modelo.fit(X, y, grupos=grupos)

    r2 = modelo.score(X, y)
    assert isinstance(r2, float)
    assert np.isfinite(r2)


def test_transform_meta_caracteristicas(datos_regresion):
    """`ApiladoAgrupado.transform(X)` debe generar matriz (n, n_bases) con predicciones base."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]
    modelo = ApiladoAgrupado(bases=bases, pliegues=3)

    with pytest.raises(NotFittedError):
        modelo.transform(X)

    modelo.fit(X, y, grupos=grupos)
    assert hasattr(modelo, "stack_method_")
    meta_features = modelo.transform(X)
    assert isinstance(meta_features, np.ndarray)
    assert meta_features.shape == (len(y), 2)
    assert np.isfinite(meta_features).all()



def test_bases_como_diccionario_mapping(datos_regresion):
    """`ensambles` y `ApiladoAgrupado` deben aceptar diccionarios como `bases`."""
    X, y, grupos = datos_regresion
    dict_bases = {
        "m_ridge": Ridge(alpha=1.0),
        "m_arbol": DecisionTreeRegressor(max_depth=4, random_state=42),
    }

    # Probar fábrica ensambles
    modelos = ensambles(bases=dict_bases)
    assert len(modelos["votacion"].estimators) == 2
    assert len(modelos["apilado"].bases) == 2

    modelos["votacion"].fit(X, y)
    preds_vot = modelos["votacion"].predict(X)
    assert preds_vot.shape == (len(y),)
    assert np.isfinite(preds_vot).all()

    modelos["apilado"].fit(X, y, grupos=grupos)
    preds_api = modelos["apilado"].predict(X)
    assert preds_api.shape == (len(y),)
    assert np.isfinite(preds_api).all()

    # Probar ApiladoAgrupado directo con diccionario
    api_directo = ApiladoAgrupado(bases=dict_bases, pliegues=3)
    clon_directo = clone(api_directo)
    assert set(clon_directo.bases.keys()) == set(dict_bases.keys())
    assert clon_directo.bases["m_ridge"] is not dict_bases["m_ridge"]
    assert isinstance(clon_directo.bases["m_ridge"], Ridge)
    api_directo.fit(X, y, grupos=grupos)
    assert api_directo.predict(X).shape == (len(y),)


def test_n_jobs_y_passthrough(datos_regresion):
    """`ApiladoAgrupado` y `ensambles` deben soportar concurrencia (`n_jobs`) y `passthrough`."""
    X, y, grupos = datos_regresion
    bases = [("ridge", Ridge()), ("arbol", DecisionTreeRegressor(random_state=0))]

    modelo = ApiladoAgrupado(bases=bases, pliegues=3, n_jobs=1, passthrough=True)
    clon = clone(modelo)
    assert clon.n_jobs == 1
    assert clon.passthrough is True

    modelo.fit(X, y, grupos=grupos)
    assert modelo.estimador_.n_jobs == 1
    preds = modelo.predict(X)
    assert preds.shape == (len(y),)
    assert np.isfinite(preds).all()

    # Verificar que ensambles propaga n_jobs
    catalogo = ensambles(n_jobs=2)
    assert catalogo["bosque"].n_jobs == 2
    assert catalogo["bagging_knn"].n_jobs == 2
    assert catalogo["votacion"].n_jobs == 2
    assert catalogo["apilado"].n_jobs == 2


def test_validaciones_pliegues_y_longitud_grupos():
    """`ApiladoAgrupado.fit` debe validar dimensiones y restricciones de pliegues y grupos."""
    X = np.ones((8, 3))
    y = np.ones(8)
    bases = [("ridge", Ridge())]

    # Longitud de grupos no coincide con y
    modelo = ApiladoAgrupado(bases=bases, pliegues=3)
    with pytest.raises(ValueError, match="longitud de 'grupos'"):
        modelo.fit(X, y, grupos=[0, 1, 2])

    # Pliegues < 2
    modelo_p1 = ApiladoAgrupado(bases=bases, pliegues=1)
    with pytest.raises(ValueError, match="al menos 2"):
        modelo_p1.fit(X, y, grupos=np.repeat([0, 1, 2, 3], 2))

    # Pliegues > número de grupos únicos
    modelo_p5 = ApiladoAgrupado(bases=bases, pliegues=5)
    with pytest.raises(ValueError, match="número de grupos únicos"):
        modelo_p5.fit(X, y, grupos=np.repeat([0, 1], 4))

    # Bases vacías
    modelo_vacio = ApiladoAgrupado(bases=[], pliegues=2)
    with pytest.raises(ValueError, match="al menos un modelo base"):
        modelo_vacio.fit(X, y, grupos=np.repeat([0, 1], 4))



def test_fit_con_sample_weight(datos_regresion):
    """`ApiladoAgrupado.fit` debe aceptar y propagar `sample_weight` sin fallar."""
    X, y, grupos = datos_regresion
    pesos = np.ones_like(y)
    pesos[: len(pesos) // 2] = 2.0

    modelo = ApiladoAgrupado(bases=[("ridge", Ridge())], pliegues=3)
    modelo.fit(X, y, grupos=grupos, sample_weight=pesos)
    preds = modelo.predict(X)
    assert preds.shape == (len(y),)
    assert np.isfinite(preds).all()


def test_get_feature_names_out(datos_regresion):
    """`get_feature_names_out` debe requerir ajuste previo y listar características transformadas."""
    X, y, grupos = datos_regresion
    modelo = ApiladoAgrupado(
        bases=[("m_ridge", Ridge()), ("m_arbol", DecisionTreeRegressor())],
        pliegues=3,
        passthrough=True,
    )

    with pytest.raises(NotFittedError):
        modelo.get_feature_names_out()

    modelo.fit(X, y, grupos=grupos)
    nombres = modelo.get_feature_names_out()
    assert isinstance(nombres, np.ndarray)
    # Con passthrough=True, hay 2 estimadores meta + 8 características originales = 10
    assert len(nombres) == 10


def test_validacion_formato_bases_invalido():
    """`ApiladoAgrupado.fit` debe validar que cada base sea una tupla (nombre, estimador)."""
    X = np.ones((8, 2))
    y = np.ones(8)
    grupos = np.repeat([0, 1], 4)

    # Base sin tupla (solo estimador)
    m1 = ApiladoAgrupado(bases=[Ridge()], pliegues=2)
    with pytest.raises(ValueError, match=r"tupla \(nombre, estimador\)"):
        m1.fit(X, y, grupos=grupos)

    # Base con tupla de 1 elemento
    m2 = ApiladoAgrupado(bases=[("ridge",)], pliegues=2)
    with pytest.raises(ValueError, match=r"tupla \(nombre, estimador\)"):
        m2.fit(X, y, grupos=grupos)

    # Base con nombre que no es string
    m3 = ApiladoAgrupado(bases=[(123, Ridge())], pliegues=2)
    with pytest.raises(ValueError, match=r"tupla \(nombre, estimador\)"):
        m3.fit(X, y, grupos=grupos)



