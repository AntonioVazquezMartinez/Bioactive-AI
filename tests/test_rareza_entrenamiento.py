"""Las piezas de la propuesta 1.10 (entrenar con más peso en la química rara).

Lo que estas pruebas protegen es lo que la regla da por supuesto antes de correr:
la rareza no cuenta al mismo grupo, los terciles son por tramo, los pesos son 3, 2 y 1,
el control D los baraja sin tocar su distribución y los pesos de 1 no cambian nada.
"""
import numpy as np
import pytest

from src.models import rareza_entrenamiento as r


def _contexto(n=60, seed=0):
    rng = np.random.default_rng(seed)
    a = rng.random((n, n)).astype(np.float32)
    s = (a + a.T) / 2
    np.fill_diagonal(s, 1.0)
    grupos = np.repeat(np.arange(n // 2), 2)          # parejas del mismo grupo
    tramo = np.tile([0, 1, 2], n // 3)
    r.fijar_contexto(s, tramo, grupos)
    return s, grupos, tramo


def test_la_rareza_no_cuenta_al_mismo_grupo():
    s, grupos, _ = _contexto()
    s[0, 1] = s[1, 0] = 0.999                         # filas 0 y 1: mismo grupo, casi idénticas
    r.fijar_contexto(s, np.zeros(len(grupos), int), grupos)
    sim = r.rareza_en_ajuste(np.arange(len(grupos)))
    assert sim[0] < 0.999 and sim[0] == pytest.approx(
        np.delete(s[0], [0, 1]).max())                # el máximo ignora a ella misma y a su pareja


def test_la_rareza_de_validacion_mira_solo_el_ajuste():
    s, _, _ = _contexto()
    ajuste, val = np.arange(0, 40), np.arange(40, 60)
    sim = r.rareza_de_validacion(ajuste, val)
    assert np.allclose(sim, s[np.ix_(val, ajuste)].max(axis=1))


def test_terciles_por_tramo_con_cero_el_mas_raro():
    sim = np.concatenate([np.linspace(0, 1, 30), np.linspace(0.5, 0.6, 30)])
    tramo = np.repeat([0, 1], 30)
    t = r.terciles_en_tramos(sim, tramo)
    for u in (0, 1):
        assert np.bincount(t[tramo == u], minlength=3).tolist() == [10, 10, 10]
    assert sim[(tramo == 0) & (t == 0)].max() < sim[(tramo == 0) & (t == 2)].min()


def test_los_pesos_son_tres_dos_y_uno_y_el_mas_raro_pesa_mas():
    _, _, _ = _contexto()
    idx = np.arange(60)
    w = r.pesos_de_rareza(idx)
    assert set(np.unique(w)) == {1.0, 2.0, 3.0}
    sim = r.rareza_en_ajuste(idx)
    tramo = r._CTX["tramo"][idx]
    for u in np.unique(tramo):
        sel = tramo == u
        assert sim[sel][w[sel] == 3].max() <= sim[sel][w[sel] == 1].min()


def test_el_control_baraja_dentro_del_tramo_sin_cambiar_la_distribucion():
    _, _, tramo = _contexto()
    w = r.pesos_de_rareza(np.arange(60))
    d = r.pesos_al_azar(w, tramo, semilla=0)
    for u in np.unique(tramo):
        assert sorted(d[tramo == u]) == sorted(w[tramo == u])
    assert not np.array_equal(d, w)                    # y no es el mismo orden
    assert np.array_equal(d, r.pesos_al_azar(w, tramo, semilla=0))   # pero es reproducible


def _datos(n=60, seed=1):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 4))
    y = (X[:, 0] + rng.normal(scale=0.5, size=n) > 0).astype(int)
    return np.hstack([X, np.arange(n, dtype=float)[:, None]]), y


def test_pesos_de_uno_dan_lo_mismo_que_no_pasar_pesos(monkeypatch):
    _contexto()
    X, y = _datos()
    monkeypatch.setattr(r, "PESOS_POR_TERCIL", np.ones(3))
    pa = r.SVMRareza("A").fit(X, y).predict_proba(X)
    pb = r.SVMRareza("B").fit(X, y).predict_proba(X)
    assert np.array_equal(pa, pb)


def test_con_pesos_de_verdad_el_brazo_b_cambia_la_prediccion():
    _contexto()
    X, y = _datos()
    pa = r.SVMRareza("A").fit(X, y).predict_proba(X)
    pb = r.SVMRareza("B").fit(X, y).predict_proba(X)
    assert not np.allclose(pa, pb)


def test_la_columna_de_indice_no_entra_al_svm():
    _contexto()
    X, y = _datos()
    X2 = X.copy()
    X2[:, -1] = X[::-1, -1]                           # otro indice en la ultima columna
    p1 = r.SVMRareza("A").fit(X, y).predict_proba(X)
    p2 = r.SVMRareza("A").fit(X2, y).predict_proba(X2)
    assert np.array_equal(p1, p2)


def test_el_brazo_c_duplica_filas_en_la_proporcion_de_los_pesos(monkeypatch):
    _contexto()
    X, y = _datos()
    vistas = {}

    class Espia(r.SVMRareza):
        def _base(self):
            base = super()._base()
            original = base.fit

            def fit(Xd, yd, **kw):
                vistas["n"] = len(yd)
                return original(Xd, yd, **kw)
            base.fit = fit
            return base

    w = r.pesos_de_rareza(X[:, -1].astype(int))
    Espia("C").fit(X, y)
    assert vistas["n"] == int(w.sum())


def test_un_brazo_desconocido_falla():
    _contexto()
    X, y = _datos()
    with pytest.raises(ValueError):
        r.SVMRareza("Z").fit(X, y)
