"""Las submuestras de la 1.11 comparan composición química, no prevalencia ni tamaño.

El valor de estas pruebas está en las dos primeras: si `submuestra` deja de igualar el número
de filas o la proporción de BBB+ entre los órdenes, la diferencia `raros − parecidos` que la
entrada 1.11 reporta deja de medir la química y nadie se enteraría mirando la cifra. El
confundido es real y grande: sin el equilibrado, en el primer pliegue el 25% «raros primero»
traía 68.1% de BBB+ y el «parecidos primero» 53.9%.
"""

import importlib.util
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "composicion_rareza", RAIZ / "scripts/experimento_composicion_rareza.py")
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def _caso():
    """200 grupos; los raros (índice bajo) son pequeños y más BBB+, como en los datos reales."""
    rng = np.random.default_rng(0)
    grupos, y, rareza = [], [], []
    for i in range(200):
        n = 2 if i < 100 else 8                      # los raros, más pequeños
        p = 0.85 if i < 100 else 0.45                # y con otra prevalencia: el confundido
        grupos += [f"g{i:03d}"] * n
        y += list((rng.random(n) < p).astype(int))
        rareza += [i / 200] * n                      # g000 es el más raro
    return (np.array(grupos), np.array(y), np.array(rareza, float),
            np.arange(len(grupos)))


def test_el_equilibrado_conserva_la_prevalencia_del_pliegue():
    g, y, rar, idx = _caso()
    objetivo = y.mean()
    for orden in ("raros", "parecidos"):
        sec, _ = _c.orden_de_grupos(rar, g, idx, orden, np.random.default_rng(0))
        for f in (0.25, 0.5, 0.75):
            sub = _c.submuestra(idx, g, y, sec, f, equilibrar=True)
            assert abs(y[sub].mean() - objetivo) <= 0.02, (orden, f, y[sub].mean())


def test_el_equilibrado_conserva_el_numero_de_filas():
    g, y, rar, idx = _caso()
    for orden in ("raros", "parecidos", "azar"):
        sec, _ = _c.orden_de_grupos(rar, g, idx, orden, np.random.default_rng(0))
        for f in (0.25, 0.5, 0.75):
            sub = _c.submuestra(idx, g, y, sec, f, equilibrar=True)
            assert abs(len(sub) - f * len(idx)) / (f * len(idx)) <= 0.15, (orden, f, len(sub))


def test_el_equilibrado_mantiene_el_contraste_de_rareza():
    """Igualar la clase no puede borrar lo que se quiere medir: los raros siguen siendo raros."""
    g, y, rar, idx = _caso()
    por_fila = dict(zip(g, rar))
    medias = {}
    for orden in ("raros", "parecidos"):
        sec, _ = _c.orden_de_grupos(rar, g, idx, orden, np.random.default_rng(0))
        sub = _c.submuestra(idx, g, y, sec, 0.25, equilibrar=True)
        medias[orden] = float(np.mean([por_fila[u] for u in np.unique(g[sub])]))
    assert medias["raros"] + 0.2 < medias["parecidos"], medias


def test_el_crudo_respeta_el_orden_de_la_cola():
    g, y, rar, idx = _caso()
    sec, _ = _c.orden_de_grupos(rar, g, idx, "raros", np.random.default_rng(0))
    sub = _c.submuestra(idx, g, y, sec, 0.25, equilibrar=False)
    elegidos = set(np.unique(g[sub]))
    # Sin equilibrar solo puede desviarse del prefijo por el afinado del tamaño, que mira la ventana.
    assert elegidos <= set(sec[:len(elegidos) + _c.VENTANA])
    assert sec[0] in elegidos


def test_al_cien_por_ciento_los_tres_ordenes_son_el_mismo_conjunto():
    g, y, rar, idx = _caso()
    for orden in ("raros", "parecidos", "azar"):
        sec, _ = _c.orden_de_grupos(rar, g, idx, orden, np.random.default_rng(0))
        for equilibrar in (True, False):
            assert np.array_equal(_c.submuestra(idx, g, y, sec, 1.0, equilibrar), idx)


def test_la_rareza_no_mira_las_filas_del_propio_grupo():
    """Un grupo de moléculas idénticas entre sí debe salir raro, no común."""
    sim = np.array([[1.0, 1.0, 0.1, 0.1],
                    [1.0, 1.0, 0.1, 0.1],
                    [0.1, 0.1, 1.0, 0.9],
                    [0.1, 0.1, 0.9, 1.0]], dtype=np.float32)
    g = np.array(["a", "a", "b", "c"])
    rar = _c.rareza_de_filas(sim, g, np.arange(4))
    assert rar[0] == rar[1] == 0.1               # su gemela no la hace común
    assert rar[2] == rar[3] == 0.9


def test_el_orden_de_grupos_va_del_mas_raro_al_mas_parecido():
    g, y, rar, idx = _caso()
    sec, por_grupo = _c.orden_de_grupos(rar, g, idx, "raros", np.random.default_rng(0))
    valores = por_grupo.loc[sec].to_numpy()
    assert np.all(np.diff(valores) >= 0)
    sec_p, _ = _c.orden_de_grupos(rar, g, idx, "parecidos", np.random.default_rng(0))
    assert np.all(np.diff(por_grupo.loc[sec_p].to_numpy()) <= 0)


def test_los_terciles_parten_en_tres_partes_parecidas():
    t = _c.terciles(np.linspace(0, 1, 300))
    assert sorted(np.bincount(t)) == [100, 100, 100]
