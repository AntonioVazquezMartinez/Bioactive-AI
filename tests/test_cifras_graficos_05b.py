"""Las dos cuentas del enriquecimiento, que son las que cambian una lectura.

El resto del script son conteos y un `polyfit`. Estas dos no: de ellas depende
decir que el modelo satura el techo en vez de que apenas supera al azar.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))

from cifras_graficos_05b import enriquecimiento, techo_enriquecimiento  # noqa: E402


def test_un_orden_perfecto_encuentra_todo_lo_que_cabe():
    # 100 compuestos, 50 activos, y la predicción los ordena perfecto.
    y = np.array([1] * 50 + [0] * 50, dtype=float)
    pred = np.arange(100, 0, -1, dtype=float)
    # Al cribar el 10% caben 10 activos de los 50, o sea el 20%.
    assert enriquecimiento(y, pred, 0.10) == pytest.approx(0.20)
    # Y ese 2.0x es exactamente el techo que permite una prevalencia del 50%.
    assert techo_enriquecimiento(0.5) == pytest.approx(2.0)


def test_el_azar_no_enriquece_y_el_orden_invertido_castiga():
    y = np.array([1, 0] * 50, dtype=float)
    # Ordenando al revés, el 10% cribado cae entero en los inactivos.
    peor = np.where(y == 1, 0.0, 1.0)
    assert enriquecimiento(y, peor, 0.10) == 0.0


def test_la_prediccion_solo_importa_por_su_orden():
    # Reescalar la predicción no puede mover la curva, porque solo se ordena.
    rng = np.random.default_rng(0)
    y = (rng.random(200) < 0.3).astype(float)
    pred = rng.normal(size=200)
    assert (enriquecimiento(y, pred, 0.05)
            == enriquecimiento(y, pred * 7.5 + 3.0, 0.05))


def test_los_nan_de_la_etiqueta_no_cuentan_como_inactivos():
    # Media tabla sin etiqueta: si contaran como 0 el denominador cambiaría.
    y = np.array([1.0, 1.0, 0.0, 0.0, np.nan, np.nan])
    pred = np.array([6.0, 5.0, 4.0, 3.0, 9.0, 8.0])
    # Quedan 4 filas con 2 activos; el 50% cribado son 2 y ambas son activas.
    assert enriquecimiento(y, pred, 0.50) == pytest.approx(1.0)


def test_sin_activos_no_hay_enriquecimiento_que_medir():
    y = np.zeros(10)
    assert np.isnan(enriquecimiento(y, np.arange(10, dtype=float), 0.1))
