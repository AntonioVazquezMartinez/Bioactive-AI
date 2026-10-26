"""Los gráficos del Avance 5 dibujan lo que la tabla mide, no otra cosa.

Lo que estas pruebas atan es la correspondencia: que la curva de
precisión-exhaustividad sea la de la clase que el AUPRC de la tabla mide, que la
matriz respete el umbral que se le pide, y que la intersección de los dos
métodos de importancia siga dando la cifra que el registro de decisiones cita.
"""

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.evaluation.cv import orientar_minoritaria  # noqa: E402
from src.evaluation.graficos import (concordantes, curva_precision_exhaustividad,  # noqa: E402
                                     curva_roc, importancias_dos_metodos,
                                     matriz_confusion)

RAIZ_DATOS = "notebooks/datos/rubrica3_importancias.csv"


@pytest.fixture
def prediccion():
    rng = np.random.default_rng(0)
    y = (rng.random(400) < 0.3).astype(int)      # la positiva es la minoritaria
    p = np.clip(y * 0.4 + rng.normal(0.3, 0.2, 400), 0, 1)
    return y, p


@pytest.fixture(autouse=True)
def cierra_figuras():
    yield
    plt.close("all")


def test_la_orientacion_elige_siempre_la_clase_menos_frecuente():
    y = np.array([1, 1, 1, 0])
    ym, _, volteada = orientar_minoritaria(y, np.zeros(4))
    assert volteada and ym.mean() == 0.25


def test_la_curva_pr_no_cambia_si_se_renombran_las_clases(prediccion):
    """Voltear etiqueta y puntaje describe la misma situación: la curva es la misma."""
    y, p = prediccion
    _, ax1 = plt.subplots()
    _, ax2 = plt.subplots()
    curva_precision_exhaustividad(y, p, ax=ax1)
    curva_precision_exhaustividad(1 - y, 1 - p, ax=ax2)
    a = ax1.lines[0].get_xydata()
    b = ax2.lines[0].get_xydata()
    assert np.allclose(a, b)


def test_la_curva_pr_dibuja_su_linea_base(prediccion):
    """Un AUPRC sin su línea base no se puede leer; la recta tiene que estar."""
    y, p = prediccion
    _, ax = plt.subplots()
    curva_precision_exhaustividad(y, p, ax=ax)
    base = [ln for ln in ax.lines if ln.get_linestyle() == "--"]
    assert base, "falta la línea base"
    assert np.isclose(base[0].get_ydata()[0], y.mean(), atol=1e-9)


def test_la_matriz_respeta_el_umbral(prediccion):
    """Mover el umbral tiene que cambiar los conteos, o la figura miente."""
    y, p = prediccion
    textos = {}
    for umbral in (0.3, 0.9):
        _, ax = plt.subplots()
        matriz_confusion(y, p, ax=ax, umbral=umbral)
        textos[umbral] = [t.get_text() for t in ax.texts]
    assert textos[0.3] != textos[0.9]


def test_roc_dibuja_la_diagonal_del_azar(prediccion):
    y, p = prediccion
    _, ax = plt.subplots()
    curva_roc(y, p, ax=ax)
    assert any(ln.get_linestyle() == "--" for ln in ax.lines)


def test_los_dos_metodos_coinciden_en_once_de_quince():
    """La cifra que cita el registro de decisiones, recalculada desde el CSV.

    Si esta prueba falla es porque cambió la corrida de importancias, y entonces
    hay que actualizar la 2.x del registro en el mismo PR, no relajar la prueba.
    """
    imp = pd.read_csv(RAIZ_DATOS)
    coinciden = concordantes(imp, n=15)
    assert len(coinciden) == 11
    for esperada in ("TPSA", "NumHDonors", "MolLogP"):
        assert esperada in coinciden


def test_la_barra_de_importancias_marca_las_concordantes():
    imp = pd.read_csv(RAIZ_DATOS)
    _, ax = plt.subplots()
    importancias_dos_metodos(imp, ax=ax, n=15)
    # Con `xerr`, el contenedor es el de las barras de error; las barras
    # mismas quedan en `ax.patches`.
    colores = {tuple(b.get_facecolor()) for b in ax.patches}
    assert len(colores) == 2, "deben verse dos colores: concordante y no"
