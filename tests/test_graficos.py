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
from src.evaluation.graficos import (concordancia_por_estrato, concordantes,  # noqa: E402
                                     curva_enriquecimiento,
                                     curva_precision_exhaustividad,
                                     curva_roc, dispersion_censurada,
                                     ganancia_arboles, importancias_dos_metodos,
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


def test_el_primer_metodo_se_nombra_y_no_siempre_es_la_impureza():
    """La fase 2 pasa `shap_media_abs`, porque su primer método es TreeSHAP y no la impureza.

    Llamar `impureza` a las dos cosas fue un defecto real: dos corridas hermanas de la C.2
    traían esa columna con métodos distintos dentro. El valor por omisión sigue siendo el de
    la fase 1, que es quien ya llamaba a esta función.
    """
    imp = pd.read_csv(RAIZ_DATOS)
    # Una columna con el orden invertido: si `columna` no se usara, el resultado no cambiaría.
    imp = imp.assign(shap_media_abs=-imp["impureza"])
    por_impureza = concordantes(imp, n=15)
    por_shap = concordantes(imp, n=15, columna="shap_media_abs")
    assert por_impureza == concordantes(imp, n=15, columna="impureza"), "el defecto es el mismo"
    assert por_shap != por_impureza, "`columna` no está llegando al cálculo"

    _, ax = plt.subplots()
    importancias_dos_metodos(imp, ax=ax, n=15, columna="shap_media_abs")
    assert "shap_media_abs" in ax.get_title(), "el título debe decir qué método se comparó"


def test_la_barra_de_importancias_marca_las_concordantes():
    imp = pd.read_csv(RAIZ_DATOS)
    _, ax = plt.subplots()
    importancias_dos_metodos(imp, ax=ax, n=15)
    # Con `xerr`, el contenedor es el de las barras de error; las barras
    # mismas quedan en `ax.patches`.
    colores = {tuple(b.get_facecolor()) for b in ax.patches}
    assert len(colores) == 2, "deben verse dos colores: concordante y no"


def test_la_dispersion_pone_el_observado_en_x_y_el_predicho_en_y():
    """Transponer los ejes no rompe nada y deja el gráfico mintiendo sobre sus etiquetas."""
    inf = np.array([5.0, 6.0])
    sup = np.array([5.0, 6.0])
    p = np.array([5.2, 5.8])
    _, ax = plt.subplots()
    dispersion_censurada(inf, sup, p, ax=ax)
    assert np.allclose(ax.collections[0].get_offsets(), np.column_stack([inf, p]))
    assert ax.get_xlabel() == "pActividad observada"
    assert ax.get_ylabel() == "pActividad predicha"
    plt.close("all")


def test_la_dispersion_marca_la_cota_superior_en_su_limite_finito():
    """La censurada con `-inf` abajo va en `sup`: dibujada en `-inf`, matplotlib la descarta."""
    inf = np.array([5.0, -np.inf])
    sup = np.array([5.0, 4.5])
    p = np.array([5.1, 4.9])
    _, ax = plt.subplots()
    dispersion_censurada(inf, sup, p, ax=ax)
    cotas = np.asarray(ax.collections[1].get_offsets())
    assert np.isfinite(cotas).all(), "quedó una coordenada infinita y el punto desaparece"
    assert np.allclose(cotas, [[4.5, 4.9]])
    plt.close("all")


def test_las_barras_por_estrato_son_la_media_y_no_otro_resumen():
    """Con `max` o `median` las barras se ven igual de bien y dicen otra cosa."""
    res = pd.DataFrame({
        "modelo": ["aft"] * 4 + ["bosque"] * 4,
        "estrato": ["todos", "todos", "solo_npass", "solo_npass"] * 2,
        "concordancia": [0.70, 0.80, 0.60, 0.64, 0.76, 0.78, 0.50, 0.52],
        "semilla": [0, 1] * 4,
        "pliegue": [1, 1, 2, 2] * 2,
    })
    _, ax = plt.subplots()
    concordancia_por_estrato(res, ["aft", "bosque"], ax=ax)
    alturas = sorted(round(b.get_height(), 3) for b in ax.patches)
    assert alturas == [0.51, 0.62, 0.75, 0.77]
    plt.close("all")


def test_el_enriquecimiento_criba_primero_lo_mas_potente():
    """Si ordenara al revés la curva caería bajo la diagonal y nadie lo notaría."""
    y = np.array([1, 1, 1, 0, 0, 0, 0, 0])
    p = np.array([9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0])
    _, ax = plt.subplots()
    curva_enriquecimiento(y, p, ax=ax)
    cribado = np.asarray(ax.lines[0].get_xdata())
    hallados = np.asarray(ax.lines[0].get_ydata())
    assert np.all(hallados >= cribado - 1e-9), "la curva va bajo el azar: ordena al revés"
    assert hallados[np.argmax(cribado >= 37.5)] == 100.0, \
        "los tres activos deben estar en el primer 37.5% del listado"
    plt.close("all")


def test_el_enriquecimiento_no_cambia_si_la_prediccion_se_reescala():
    """Solo usa el orden, así que una transformación monótona no lo mueve."""
    y = np.array([1, 0, 1, 1, 0, 0, 1, 0])
    p = np.array([9.0, 1.0, 8.0, 7.0, 2.0, 3.0, 6.0, 4.0])
    curvas = []
    for q in (p, 2 * p + 100):
        _, ax = plt.subplots()
        curva_enriquecimiento(y, q, ax=ax)
        curvas.append(np.asarray(ax.lines[0].get_ydata()))
        plt.close("all")
    assert np.allclose(*curvas)


def test_la_ganancia_dibuja_el_top_de_menor_a_mayor_hacia_arriba():
    """`nsmallest`, o un reverso de más, deja el gráfico mostrando lo irrelevante."""
    ganancias = pd.Series({"MolLogP": 12.0, "TPSA": 8.0, "diana=DRD2": 15.0, "ruido": 0.3})
    _, ax = plt.subplots()
    ganancia_arboles(ganancias, ax=ax, n=2)
    assert [t.get_text() for t in ax.get_yticklabels()] == ["MolLogP", "diana=DRD2"]
    assert [round(b.get_width(), 3) for b in ax.patches] == [12.0, 15.0]
    plt.close("all")
