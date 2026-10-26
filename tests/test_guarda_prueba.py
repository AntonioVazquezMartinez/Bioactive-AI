"""La guarda de la partición de prueba (roadmap-mlops 0.4, #54)."""

from __future__ import annotations

import pandas as pd
import pytest

from src.tracking import tomar_prueba


@pytest.fixture
def pares():
    return pd.DataFrame({
        "particion": ["entrenamiento", "validacion", "prueba", "prueba"],
        "estrato": ["solo_chembl", "solo_npass", "solo_chembl", "solo_npass"],
    })


def test_sin_la_marca_falla_y_no_devuelve_nada(pares, tmp_path):
    with pytest.raises(RuntimeError, match="una sola vez"):
        tomar_prueba(pares, raiz=tmp_path)
    assert not (tmp_path / "experimentos" / "prueba.csv").exists()


def test_la_marca_sin_motivo_tampoco(pares, tmp_path):
    with pytest.raises(ValueError, match="motivo"):
        tomar_prueba(pares, final=True, motivo="   ", raiz=tmp_path)


def test_devuelve_solo_la_prueba_y_deja_constancia(pares, tmp_path, capsys):
    prueba = tomar_prueba(pares, final=True, motivo="el stacking elegido", raiz=tmp_path)
    assert list(prueba["particion"]) == ["prueba", "prueba"]

    bitacora = (tmp_path / "experimentos" / "prueba.csv").read_text(encoding="utf-8")
    assert bitacora.startswith("fecha,autor,commit,filas,motivo\n")
    assert "el stacking elegido" in bitacora
    assert ",2," in bitacora                      # las filas que se tocaron
    assert "solo_npass 1" in capsys.readouterr().out   # el aviso de los estratos chicos


def test_la_segunda_vez_se_ve_en_el_archivo(pares, tmp_path):
    """Tocarla dos veces no se bloquea: se hace visible, que es lo que la revisión puede atrapar."""
    tomar_prueba(pares, final=True, motivo="primera", raiz=tmp_path)
    tomar_prueba(pares, final=True, motivo="segunda", raiz=tmp_path)

    lineas = (tmp_path / "experimentos" / "prueba.csv").read_text(encoding="utf-8").splitlines()
    assert len(lineas) == 3        # encabezado y dos corridas
