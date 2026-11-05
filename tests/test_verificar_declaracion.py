"""El verificador de la declaración tiene que fallar cuando falta algo.

Una comprobación que siempre pasa es peor que no tenerla: da la señal de que la
declaración está, justo donde no hay ninguna otra señal que avise.
"""

import json
import sys

import pytest

sys.path.insert(0, "scripts")
import verificar_declaracion as vd  # noqa: E402

COMPLETA = """### Uso de herramientas de IA
| Herramienta | Propósito | Alcance | Responsabilidad |
### Contribución individual
| Integrante | Contribución al avance |
### Decisiones principales
**Decisión 1:**
"""


def _libreta(tmp_path, nombre, texto):
    cuaderno = {"cells": [
        {"cell_type": "code", "source": ["1 + 1"]},
        {"cell_type": "markdown", "source": [texto]},
    ]}
    destino = tmp_path / nombre
    destino.write_text(json.dumps(cuaderno), encoding="utf-8")
    return destino


@pytest.fixture
def cuadernos(tmp_path, monkeypatch):
    monkeypatch.setattr(vd, "CUADERNOS", tmp_path)
    return tmp_path


def test_sin_libretas_de_avance_4_no_falla(cuadernos):
    """Hoy no existen todavía; el CI no puede fallar por eso."""
    _libreta(cuadernos, "03_Baseline.ipynb", "sin declaración")
    assert vd.main() == 0


def test_una_libreta_entregable_sin_declaracion_falla(cuadernos):
    _libreta(cuadernos, "04_Models.ipynb", "## Conclusiones\nnada más")
    assert vd.main() == 1


def test_una_declaracion_completa_pasa(cuadernos):
    _libreta(cuadernos, "04_Models.ipynb", COMPLETA)
    assert vd.main() == 0


def test_los_nombres_del_ejemplo_de_canvas_no_pueden_quedarse(cuadernos):
    _libreta(cuadernos, "04_Models.ipynb", COMPLETA + "\n| Nombre Estudiante 1 | |")
    assert vd.main() == 1


def test_el_acompanante_con_sufijo_de_letra_no_se_exige(cuadernos):
    """`04b` es un análisis acompañante, no un entregable."""
    _libreta(cuadernos, "04b_Exploracion.ipynb", "sin declaración")
    assert vd.main() == 0
