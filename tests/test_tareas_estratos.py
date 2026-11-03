"""El origen de tres categorías y el desglose por estratos de la fase 1 (1.6, #102)."""

import numpy as np
import pandas as pd
import pytest

from src.models import tareas
from src.models.tareas import (_etiquetas_estratos, _pesos_moleculares,
                               asignar_origen, cargar, etiquetas_por_tamano)

NATURAL, ANALOGO, SIN = tareas.ORIGENES

procesados = pytest.mark.skipif(
    not (tareas.PROCESADOS / "bbb_meta.parquet").exists()
    or not (tareas.PROCESADOS / tareas.DESCRIPTORES["descriptores"]).exists()
    or not tareas.ARCHIVO_PATROCINADORA.exists(),
    reason="faltan data/processed (meta o descriptores) o el archivo de la patrocinadora")


def test_origen_de_tres_categorias():
    exacto = pd.Series(["CNP1", None, None])
    key14 = pd.Series([None, "CNP2", None])
    assert list(asignar_origen(exacto, key14)) == [NATURAL, ANALOGO, SIN]


def test_con_las_dos_columnas_presentes_es_natural_exacto():
    exacto = pd.Series(["CNP1"])
    key14 = pd.Series(["CNP1;CNP2"])
    assert list(asignar_origen(exacto, key14)) == [NATURAL]


def test_origen_grupo_combina_las_dos_etiquetas():
    origen = np.array([NATURAL, SIN])
    grupo = np.array(["B", "A"])
    assert list(_etiquetas_estratos("origen_grupo", grupo, origen)) == [
        "natural exacto·B", "sin equivalente natural·A"]
    assert list(_etiquetas_estratos("origen", grupo, origen)) == [NATURAL, SIN]
    assert list(_etiquetas_estratos("grupo", grupo, origen)) == ["B", "A"]


def test_estratos_invalido_da_error():
    with pytest.raises(ValueError, match="estratos"):
        cargar("permeabilidad", estratos="otro")


def test_actividad_solo_admite_estratos_de_procedencia():
    for e in ("origen", "origen_grupo", "tamano"):
        with pytest.raises(ValueError, match="procedencia"):
            cargar("actividad", estratos=e)


@procesados
def test_conteos_de_origen_sobre_las_7805_filas():
    t = cargar("permeabilidad", estratos="origen", incluir_prueba=True)
    assert len(t.y) == 7805
    conteos = pd.Series(t.estratos).value_counts()
    assert conteos[NATURAL] == 3366
    assert conteos[ANALOGO] == 1003
    assert conteos[SIN] == 3436
    # Y por omisión, el comportamiento anterior: grupos A–D y sin columna `origen`.
    g = cargar("permeabilidad", incluir_prueba=True)
    assert set(g.estratos) <= {"A", "B", "C", "D"}
    assert "origen" not in g.meta


# --- El estrato de tamaño (#215) ---------------------------------------------


def test_los_tramos_son_cerrados_por_arriba():
    """Un peso igual al corte cae en el tramo de abajo, y eso se fija aquí."""
    pesos = np.array([100.0, 250.0, 250.1, 350.0, 400.0, 500.0, 500.1, 800.0, 800.1, 4000.0])
    assert list(etiquetas_por_tamano(pesos)) == [
        "≤250 Da", "≤250 Da", "250–350 Da", "250–350 Da", "350–500 Da", "350–500 Da",
        "500–800 Da", "500–800 Da", ">800 Da", ">800 Da"]


def test_la_etiqueta_lleva_el_corte_dentro():
    """Una figura que no dice con qué se partió no se puede comparar con otra."""
    for etiqueta in set(etiquetas_por_tamano(np.array([100.0, 300.0, 400.0, 900.0]))):
        assert "Da" in etiqueta
        assert any(c.isdigit() for c in etiqueta)


def test_otros_cortes_dan_otros_tramos():
    assert list(etiquetas_por_tamano(np.array([100.0, 500.0]), cortes=(300.0,))) == [
        "≤300 Da", ">300 Da"]


def test_los_cortes_tienen_que_crecer():
    for malos in ((), (350.0, 250.0), (250.0, 250.0)):
        with pytest.raises(ValueError, match="crecientes"):
            etiquetas_por_tamano(np.array([100.0]), cortes=malos)


def test_el_estrato_de_tamano_ignora_grupo_y_origen():
    etiquetas = _etiquetas_estratos(
        "tamano", np.array(["A", "A"]), np.array([NATURAL, SIN]),
        np.array([100.0, 900.0]))
    assert list(etiquetas) == ["≤250 Da", ">800 Da"]


@procesados
def test_el_peso_sale_de_la_matriz_de_descriptores_y_no_de_meta():
    """Siempre la misma fuente, o los dos brazos compararían particiones distintas."""
    d = pd.read_parquet(tareas.PROCESADOS / tareas.DESCRIPTORES["descriptores"],
                        columns=["MolWt"])
    filas = np.array([0, 5, 100])
    assert np.allclose(_pesos_moleculares(filas), d["MolWt"].to_numpy()[filas])


@procesados
def test_cargar_con_tamano_da_los_cuatro_tramos_y_ninguno_es_marginal():
    t = cargar("permeabilidad", estratos="tamano")
    conteos = pd.Series(t.estratos).value_counts()
    assert set(conteos.index) == {"≤250 Da", "250–350 Da", "350–500 Da", "500–800 Da",
                                  ">800 Da"}
    assert conteos.sum() == len(t.y)
    # El arnés solo reporta un subgrupo si su clase minoritaria llega a 20 casos.
    for tramo in conteos.index:
        sel = t.estratos == tramo
        assert min(int(t.y[sel].sum()), int((1 - t.y[sel]).sum())) >= 20, tramo
    # Y no se calcula el origen cuando nadie lo pidió.
    assert "origen" not in t.meta


def test_un_peso_ausente_falla_en_vez_de_caer_en_el_tramo_mas_grande():
    """`searchsorted` manda el NaN al final: sin esta guarda quedaria en «>800 Da» y ninguna
    figura lo mostraria."""
    for malo in (np.nan, np.inf, -np.inf):
        with pytest.raises(ValueError, match="ausentes o no finitos"):
            etiquetas_por_tamano(np.array([100.0, malo, 400.0]))


def test_el_mensaje_dice_cuantos_pesos_faltan():
    with pytest.raises(ValueError, match="2 pesos"):
        etiquetas_por_tamano(np.array([100.0, np.nan, np.nan]))


def test_los_cuatro_tramos_de_abajo_estan_acotados_y_solo_el_ultimo_es_abierto():
    """Lo que hace comparables las dos fases: los tramos cerrados significan lo mismo en las dos;
    el abierto no, y por eso es el unico que se declara."""
    cortes = tareas.PESOS_CORTE
    assert cortes == (250.0, 350.0, 500.0, 800.0)
    etiquetas = etiquetas_por_tamano(np.array([1.0, 300.0, 400.0, 600.0, 1e6]))
    assert [e for e in etiquetas if e.startswith(">")] == [">800 Da"]
    assert all("–" in e or e.startswith("≤") for e in etiquetas[:-1])
