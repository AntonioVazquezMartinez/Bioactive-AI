"""Los ensambles entran al arnés como cualquier canalización, y el stacking no filtra.

Lo que atan: que el stacking se niegue a ajustar sin grupos y que sus pliegues
internos no crucen grupos, que es la fuga que no aparece en ninguna métrica; y que
los cinco ensambles corran por `evaluar` con predicciones fuera de pliegue.
"""

import numpy as np
import pytest
from sklearn.model_selection import StratifiedGroupKFold

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.ensambles import StackingAgrupado, ensambles

BASE = ("logistica", "knn")


@pytest.fixture
def datos():
    rng = np.random.default_rng(0)
    n = 240
    grupos = np.repeat(np.arange(n // 3), 3)
    y = (rng.random(n) < 0.4).astype(int)
    X = rng.normal(size=(n, 5)) + y[:, None] * 0.8
    return X, y, grupos


def test_el_stacking_sin_grupos_se_niega_a_ajustar(datos):
    X, y, _ = datos
    s = StackingAgrupado(list(seleccion(BASE).items()))
    with pytest.raises(ValueError, match="grupos"):
        s.fit(X, y)


def test_los_pliegues_internos_del_stacking_no_cruzan_grupos(datos, monkeypatch):
    X, y, grupos = datos
    vistos = []
    original = StratifiedGroupKFold.split

    def espia(self, X_, y_, g_):
        for ajuste, val in original(self, X_, y_, g_):
            vistos.append((set(g_[ajuste]), set(g_[val])))
            yield ajuste, val

    monkeypatch.setattr(StratifiedGroupKFold, "split", espia)
    StackingAgrupado(list(seleccion(BASE).items()), pliegues=3).fit(X, y, grupos=grupos)
    assert len(vistos) == 3
    assert all(not a & v for a, v in vistos)


def test_los_cinco_ensambles_corren_por_el_arnes(datos):
    X, y, grupos = datos
    modelos = ensambles(BASE)
    assert set(modelos) == {"bosque", "boosting", "bagging_svm", "votacion", "stacking"}
    assert modelos["stacking"].necesita_grupos
    res, fdp = evaluar(modelos, X, y, grupos, semillas=(0,), pliegues=3, verboso=False)
    for nombre, p in fdp.items():
        assert not np.isnan(p).any(), nombre
        assert ((p >= 0) & (p <= 1)).all(), nombre
    assert set(res["modelo"]) == set(modelos)
