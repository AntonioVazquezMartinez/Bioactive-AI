"""El reparto de la 1.11 mueve grupos enteros y deja el mismo núcleo de evaluación a todos los brazos."""
import numpy as np
import pytest

from src.models.raros_al_ajuste import repartir, similitud_fuera_del_grupo, terciles_de_grupos


def _datos(n_grupos=240, seed=0, cruzados=0):
    """Grupos de 1 a 3 filas; el 25% de los grupos va a la prueba; tercil al azar por grupo."""
    rng = np.random.default_rng(seed)
    tam = rng.integers(1, 4, n_grupos)
    grupos = np.repeat(np.arange(n_grupos), tam)
    prueba_g = rng.random(n_grupos) < 0.25
    terc_g = rng.integers(0, 3, n_grupos)
    particion = np.where(prueba_g[grupos], "prueba", "entrenamiento")
    for g in range(cruzados):                  # grupos que tienen una fila en cada lado
        filas = np.flatnonzero(grupos == g)
        if len(filas) > 1:
            particion[filas[0]], particion[filas[1]] = "prueba", "entrenamiento"
    return particion, grupos, terc_g[grupos]


def test_se_mueven_grupos_enteros_y_no_se_cruzan_con_la_evaluacion():
    particion, grupos, terc = _datos()
    r = repartir(particion, grupos, terc, semilla=1)
    for brazo in "ABCD":
        entrena = r.entrenamiento(brazo)
        assert not set(grupos[entrena]) & set(grupos[r.evaluacion]), brazo
    for movidas in (r.movidas_raras, r.movidas_azar):
        for g in set(grupos[movidas]):
            assert set(np.flatnonzero(grupos == g)) <= set(movidas), "grupo partido al moverlo"


def test_la_evaluacion_es_la_misma_en_todos_los_brazos_y_viene_de_la_prueba():
    particion, grupos, terc = _datos()
    r = repartir(particion, grupos, terc, semilla=2)
    assert set(r.evaluacion) <= set(np.flatnonzero(particion == "prueba"))
    assert not set(r.evaluacion) & set(r.movibles)
    for brazo in "ABCD":
        assert not set(r.entrenamiento(brazo)) & set(r.evaluacion)


def test_b_mueve_solo_raras_y_c_tiene_al_menos_su_tamano():
    particion, grupos, terc = _datos()
    r = repartir(particion, grupos, terc, semilla=3)
    assert len(r.movidas_raras) > 0
    assert set(terc[r.movidas_raras]) == {0}
    assert len(r.movidas_azar) >= len(r.movidas_raras)
    # B, C y D tienen casi el mismo tamaño: B − C no mezcla «más raro» con «más datos»
    # (C se pasa a lo más un grupo de 3 filas).
    assert 0 <= len(r.entrenamiento("C")) - len(r.entrenamiento("B")) <= 2
    assert len(r.entrenamiento("B")) - len(r.entrenamiento("D")) == len(r.movidas_raras)


def test_lo_que_sale_del_ajuste_son_comunes_del_ajuste():
    particion, grupos, terc = _datos()
    r = repartir(particion, grupos, terc, semilla=4)
    assert len(r.quitadas) >= len(r.movidas_raras)
    assert set(terc[r.quitadas]) == {2}
    assert set(r.quitadas) <= set(r.ajuste)
    assert set(r.entrenamiento("D")) == set(r.ajuste) - set(r.quitadas)


def test_el_brazo_a_es_el_ajuste_original_sin_la_prueba():
    particion, grupos, terc = _datos()
    r = repartir(particion, grupos, terc, semilla=5)
    assert set(r.entrenamiento("A")) == set(np.flatnonzero(particion != "prueba"))


def test_un_grupo_que_cruza_ajuste_y_prueba_no_se_evalua_ni_se_mueve():
    particion, grupos, terc = _datos(cruzados=30)
    r = repartir(particion, grupos, terc, semilla=6)
    assert r.cruzados > 0
    cruzan = set(grupos[particion == "prueba"]) & set(grupos[particion != "prueba"])
    assert not cruzan & set(grupos[r.evaluacion])
    assert not cruzan & set(grupos[r.movibles])
    assert not (set(r.quitadas) & set(np.flatnonzero(particion == "prueba")))


def test_la_misma_semilla_da_el_mismo_reparto_y_otra_da_otro():
    particion, grupos, terc = _datos()
    a, b, c = (repartir(particion, grupos, terc, s) for s in (7, 7, 8))
    assert np.array_equal(a.evaluacion, b.evaluacion) and np.array_equal(a.quitadas, b.quitadas)
    assert not np.array_equal(a.evaluacion, c.evaluacion)


def test_falla_si_el_ajuste_no_tiene_tantas_comunes():
    particion = np.array(["entrenamiento"] * 4 + ["prueba"] * 6)
    grupos = np.arange(10)
    terc = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])      # ningún común en el ajuste
    with pytest.raises(ValueError, match="comunes"):
        repartir(particion, grupos, terc, semilla=0)


def test_similitud_fuera_del_grupo_ignora_al_propio_grupo():
    s = np.array([[1.0, 0.9, 0.2], [0.9, 1.0, 0.3], [0.2, 0.3, 1.0]], dtype=np.float32)
    out = similitud_fuera_del_grupo(s, np.array([0, 0, 1]), bloque=2)
    assert np.allclose(out, [0.2, 0.3, 0.3])


def test_terciles_de_grupos_son_por_grupo_y_dentro_del_tramo():
    sim = np.array([.1, .1, .5, .5, .9, .9, .2, .4, .8], float)
    grupos = np.array([0, 0, 1, 1, 2, 2, 3, 4, 5])
    tramo = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1])
    t = terciles_de_grupos(sim, grupos, tramo)
    assert t[0] == t[1] and t[2] == t[3] and t[4] == t[5]    # un tercil por grupo
    assert list(t[[0, 2, 4]]) == [0, 1, 2]                    # el menos parecido es el más raro
    assert list(t[[6, 7, 8]]) == [0, 1, 2]                    # y por separado en el otro tramo
