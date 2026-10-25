"""Las métricas de regresión no pueden tratar un límite como si fuera un valor.

Lo que estas pruebas atan: que la conversión a µM invierta el sentido de la
censura (un `> 10 µM` es censura por la derecha en concentración), que la
concordancia ignore los pares cuyo orden no se conoce, y que Spearman y RMSE se
calculen solo sobre lo exacto.
"""

import numpy as np
import pytest

from src.evaluation.regresion import (concordancia_harrell, limites_en_micromolar,
                                      metricas_regresion, rmse_exactas,
                                      spearman_exactas)

INF = np.inf


def test_un_mayor_que_10_um_es_censura_por_la_derecha_en_concentracion():
    # `> 10 µM` en pActividad: menor que 5, es decir (−∞, 5]
    inferior_um, superior_um = limites_en_micromolar([-INF], [5.0])
    assert inferior_um[0] == pytest.approx(10.0)
    assert superior_um[0] == INF


def test_una_exacta_ida_y_vuelta_no_cambia():
    # 0.1 µM = pActividad 7; en µM el intervalo es un punto
    inferior_um, superior_um = limites_en_micromolar([7.0], [7.0])
    assert inferior_um[0] == pytest.approx(0.1) == pytest.approx(superior_um[0])
    assert 6 - np.log10(inferior_um[0]) == pytest.approx(7.0)


def test_una_cota_inferior_de_potencia_es_censura_por_la_izquierda_en_concentracion():
    # `< 1 µM` en pActividad: mayor que 6, es decir [6, +∞)
    inferior_um, superior_um = limites_en_micromolar([6.0], [INF])
    assert inferior_um[0] == 0.0
    assert superior_um[0] == pytest.approx(1.0)


def test_concordancia_perfecta_inversa_y_constante():
    y = np.array([4.0, 5.0, 6.0, 7.0])
    assert concordancia_harrell(y, y, y) == 1.0
    assert concordancia_harrell(y, y, -y) == 0.0
    assert concordancia_harrell(y, y, np.zeros(4)) == 0.5


def test_la_concordancia_ignora_los_pares_cuyo_orden_no_se_conoce():
    # dos censuradas «< 5» (intervalos que se solapan entre sí) y una exacta en 7
    inf = np.array([-INF, -INF, 7.0])
    sup = np.array([5.0, 5.0, 7.0])
    # solo los pares (censurada, exacta) son comparables; el orden entre las
    # dos censuradas no cuenta aunque el modelo las ponga al revés
    pred = np.array([3.0, 2.0, 8.0])
    assert concordancia_harrell(inf, sup, pred) == 1.0
    pred_mala = np.array([3.0, 2.0, 1.0])
    assert concordancia_harrell(inf, sup, pred_mala) == 0.0


def test_rmse_y_spearman_usan_solo_las_exactas():
    inf = np.array([5.0, 6.0, 7.0, -INF])
    sup = np.array([5.0, 6.0, 7.0, 5.0])
    pred = np.array([5.0, 6.0, 8.0, 9.0])          # la censurada, muy mal: no cuenta
    rmse, n = rmse_exactas(inf, sup, pred)
    assert n == 3 and rmse == pytest.approx(np.sqrt(1 / 3))
    rho, n = spearman_exactas(inf, sup, pred)
    assert n == 3 and rho == pytest.approx(1.0)


def test_el_resumen_dice_cuanto_es_censurado():
    inf = np.array([5.0, -INF])
    sup = np.array([5.0, 5.0])
    m = metricas_regresion(inf, sup, np.array([5.0, 3.0]))
    assert m["n_exactas"] == 1 and m["fraccion_censurada"] == 0.5
