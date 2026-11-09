"""`Tarea.columnas` nombra cada columna de `X` en el orden de la matriz (el cuaderno 05 rotulaba por índice)."""
import pytest

from src.models.tareas import PROCESADOS, cargar

pytestmark = pytest.mark.skipif(not (PROCESADOS / "bbb_meta.parquet").exists(),
                                reason="faltan los datos procesados (no se versionan)")


@pytest.mark.parametrize("representacion", ["descriptores"])
def test_hay_un_nombre_por_columna(representacion):
    t = cargar("permeabilidad", representacion=representacion)
    assert len(t.columnas) == t.X.shape[1]
    assert len(set(t.columnas)) == len(t.columnas)


def test_los_descriptores_se_llaman_por_su_nombre():
    t = cargar("permeabilidad")
    assert {"TPSA", "NumHDonors", "MolLogP"} <= set(t.columnas)
