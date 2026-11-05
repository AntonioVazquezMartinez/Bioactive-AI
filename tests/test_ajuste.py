"""La búsqueda de hiperparámetros no puede elegir la rejilla sobre una fuga.

El error que estas pruebas atan es el que no se ve en ninguna métrica: la
evaluación externa sigue agrupada y se ve honesta, pero si la validación interna
parte al azar, los hiperparámetros se eligieron con análogos del mismo andamio a
los dos lados.
"""

import numpy as np
import pytest
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.tree import DecisionTreeClassifier

from src.evaluation.cv import evaluar
from src.models.ajuste import BusquedaAnidada
from src.models.alternativos import FAMILIAS, catalogo, seleccion


@pytest.fixture
def datos():
    rng = np.random.default_rng(0)
    n = 300
    grupos = np.repeat(np.arange(n // 3), 3)
    y = (rng.random(n) < 0.4).astype(int)
    X = rng.normal(size=(n, 5)) + y[:, None] * 0.8
    return X, y, grupos


def test_sin_grupos_se_niega_a_ajustar(datos):
    """Fallar es correcto: en silencio elegiría la rejilla sobre una fuga."""
    X, y, _ = datos
    b = BusquedaAnidada(DecisionTreeClassifier(), {"max_depth": [2, 3]})
    with pytest.raises(ValueError, match="grupos"):
        b.fit(X, y)


def test_la_particion_interna_tampoco_cruza_grupos(datos):
    """La misma propiedad de la 1.2, una capa más adentro."""
    X, y, grupos = datos
    b = BusquedaAnidada(DecisionTreeClassifier(), {"max_depth": [2, 3]}, pliegues=3)
    b.fit(X, y, grupos=grupos)
    interno = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=0)
    for ajuste, val in interno.split(X, y, grupos):
        assert not set(grupos[ajuste]) & set(grupos[val])
    assert b.elegidos_["max_depth"] in (2, 3)


def test_el_arnes_le_pasa_los_grupos_del_pliegue(datos):
    """`necesita_grupos` es lo que conecta las dos capas; sin eso, fuga silenciosa."""
    X, y, grupos = datos
    afinado = BusquedaAnidada(catalogo()["arbol"],
                              {"modelo__max_depth": [2, 5, None]}, pliegues=3)
    assert afinado.necesita_grupos
    res, fdp = evaluar({"arbol afinado": afinado}, X, y, grupos,
                       semillas=(0,), pliegues=3, verboso=False)
    assert not np.isnan(fdp["arbol afinado"]).any()
    assert (res.segundos_ajuste > 0).all()


def test_el_catalogo_no_trae_ensambles():
    """Un bosque o un boosting aquí invalidaría los seis del Avance 4."""
    prohibidos = ("Forest", "Boosting", "Bagging", "Voting", "Stacking", "AdaBoost")
    for nombre, canalizacion in catalogo().items():
        tipo = type(canalizacion.named_steps["modelo"]).__name__
        assert not any(p in tipo for p in prohibidos), f"{nombre} es un ensamble"


def test_todas_las_familias_dan_probabilidades():
    """Sin `predict_proba` el arnés no puede medir AUROC ni AUPRC."""
    for nombre, canalizacion in catalogo().items():
        assert hasattr(canalizacion, "predict_proba"), nombre


def test_seleccion_falla_con_una_clave_inventada():
    with pytest.raises(ValueError, match="catálogo"):
        seleccion(("logistica", "inexistente"))
    assert tuple(seleccion(("arbol", "knn"))) == ("arbol", "knn")
    assert len(FAMILIAS) == len(catalogo())


def test_el_resultado_guarda_que_hiperparametros_eligio_cada_pliegue(datos):
    """Sin esta columna no se distingue un ajuste estable de uno afortunado."""
    X, y, grupos = datos
    afinado = BusquedaAnidada(catalogo()["arbol"],
                              {"modelo__max_depth": [2, 5, None]}, pliegues=3)
    res, _ = evaluar({"afinado": afinado}, X, y, grupos, semillas=(0,), pliegues=3,
                     verboso=False)
    assert "elegidos" in res.columns
    assert res.elegidos.notna().all()
    assert all("max_depth" in e for e in res.elegidos)


def test_una_canalizacion_normal_no_agrega_la_columna(datos):
    """La columna solo aparece si alguien ajustó algo; si no, ensucia el CSV."""
    X, y, grupos = datos
    res, _ = evaluar(seleccion(("arbol",)), X, y, grupos, semillas=(0,), pliegues=3,
                     verboso=False)
    assert "elegidos" not in res.columns
