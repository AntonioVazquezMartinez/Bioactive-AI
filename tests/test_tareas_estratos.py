"""El origen de tres categorías y el desglose por estratos de la fase 1 (1.6, #102)."""

import numpy as np
import pandas as pd
import pytest

from src.models import tareas
from src.models.tareas import _etiquetas_estratos, asignar_origen, cargar

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
    for e in ("origen", "origen_grupo"):
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
