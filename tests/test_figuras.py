"""Las primitivas de gráfica traducen datos a cuadro, y avisan si no caben.

Son pruebas de geometría, no de dibujo: comprueban que `punto` coloca un dato
donde dice y que las guardas disparan. Lo que no se puede probar aquí es si la
figura **se lee**, y para eso no hay sustituto de mirar el fotograma.

Se saltan enteras si no está `manim`, porque el entorno del lock no lo trae:
las animaciones tienen el suyo (`requirements-animaciones.txt`) y el CI las
renderiza en un paso aparte.
"""

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "animaciones"))

pytest.importorskip("manim", reason="animaciones tiene su propio entorno")

from figuras import Ejes, abanico, columna_naciendo, reduccion  # noqa: E402


def test_punto_coloca_los_extremos_en_las_esquinas():
    e = Ejes((0, 10), (0, 100), ancho=8.0, alto=4.0)
    izq_abajo, der_arriba = e.punto(0, 0), e.punto(10, 100)
    assert der_arriba[0] - izq_abajo[0] == pytest.approx(8.0)
    assert der_arriba[1] - izq_abajo[1] == pytest.approx(4.0)


def test_punto_es_lineal_en_las_dos_direcciones():
    e = Ejes((512, 4096), (50, 100), ancho=6.0, alto=3.0)
    medio = e.punto((512 + 4096) / 2, 75)
    assert medio[0] == pytest.approx(e.grupo.get_center()[0] + 0.0, abs=1e-6)
    a, b = e.punto(512, 50), e.punto(4096, 50)
    assert (medio[0] - a[0]) == pytest.approx((b[0] - medio[0]))


def test_un_rango_invertido_no_se_dibuja_al_reves_en_silencio():
    with pytest.raises(ValueError, match="rangos"):
        Ejes((10, 0), (0, 1))


def test_unos_ejes_que_no_dejan_sitio_al_titulo_fallan():
    with pytest.raises(ValueError, match="no dejan sitio"):
        Ejes((0, 1), (0, 1), ancho=13.5, alto=3.0)


def test_el_area_entre_dos_series_necesita_dos_series():
    e = Ejes((0, 1), (0, 1), ancho=4.0, alto=2.0)
    with pytest.raises(ValueError, match="dos series"):
        e.area_entre([(0, 0)], [(0, 0), (1, 1)])


def test_una_curva_de_un_punto_no_es_una_curva():
    e = Ejes((0, 1), (0, 1), ancho=4.0, alto=2.0)
    with pytest.raises(ValueError, match="dos puntos"):
        e.curva([(0, 0)])


def test_el_histograma_pone_una_barra_por_valor():
    e = Ejes((0, 4), (0, 10), ancho=4.0, alto=2.0)
    assert len(e.histograma([1, 5, 10, 2])) == 4


def test_una_reduccion_que_crece_es_un_error_de_quien_la_pide():
    with pytest.raises(ValueError, match="reducción imposible"):
        reduccion("al revés", de=100, a=500)


def test_la_reduccion_dibuja_la_barra_en_proporcion():
    mitad = reduccion("mitad", de=100, a=50)
    entera = reduccion("entera", de=100, a=100)
    assert (mitad.barra.height / entera.barra.height) == pytest.approx(0.5)


def test_el_abanico_tiene_un_radio_por_diana_mas_el_punto():
    # Un radio por diana, más el `Dot` del compuesto.
    assert len(abanico([0, 0, 0], 9, largo=1.0)) == 10
    with pytest.raises(ValueError, match="al menos un radio"):
        abanico([0, 0, 0], 0)


def test_la_columna_naciente_tiene_sus_filas():
    assert len(columna_naciendo(filas=6)) == 6
