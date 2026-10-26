"""El cuaderno 04b muestra el código de sus métricas, y es el de `src/`, que es el que corre.

El cuaderno ejecuta las métricas importándolas de `src/evaluation/regresion.py`, y una celda
de texto las muestra para que se lea sin abrir otro archivo. Si el código que se muestra
dejara de ser el que se ejecuta, el cuaderno describiría algo que no corrió. Esta prueba ata
las dos cosas: compara el árbol sintáctico de cada función mostrada contra la de `src/`
(los espacios y los comentarios no cuentan, la lógica sí) y comprueba que la celda de código
siga importándolas de `src/`.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "04b_Regresion_actividad.ipynb"
FUNCIONES = ["_exactas", "concordancia_harrell", "rmse_exactas"]


def _sin_docstring(nodo):
    """Quita el docstring de la función o clase y de lo que contiene: se compara la lógica."""
    for hijo in ast.walk(nodo):
        if isinstance(hijo, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            cuerpo = hijo.body
            if (cuerpo and isinstance(cuerpo[0], ast.Expr)
                    and isinstance(cuerpo[0].value, ast.Constant)
                    and isinstance(cuerpo[0].value.value, str)):
                hijo.body = cuerpo[1:] or [ast.Pass()]
    return nodo


def _definiciones(fuente: str) -> dict[str, str]:
    return {n.name: ast.dump(_sin_docstring(n)) for n in ast.parse(fuente).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


@pytest.fixture(scope="module")
def celdas() -> list[dict]:
    return json.loads(CUADERNO.read_text(encoding="utf-8"))["cells"]


@pytest.fixture(scope="module")
def mostrado(celdas) -> dict[str, str]:
    """Las funciones que el cuaderno muestra en bloques de código de sus celdas de texto."""
    out: dict[str, str] = {}
    for c in celdas:
        if c["cell_type"] == "markdown":
            for bloque in re.findall(r"```python\n(.*?)```", "".join(c["source"]), re.S):
                out.update(_definiciones(bloque))
    return out


@pytest.mark.parametrize("nombre", FUNCIONES)
def test_cada_funcion_mostrada_es_la_de_src(nombre, mostrado):
    de_src = _definiciones(
        (RAIZ / "src" / "evaluation" / "regresion.py").read_text(encoding="utf-8"))
    assert nombre in de_src, f"{nombre} ya no existe en src/evaluation/regresion.py"
    assert nombre in mostrado, f"{nombre} no se muestra en el cuaderno 04b"
    assert mostrado[nombre] == de_src[nombre], (
        f"{nombre}: el cuaderno 04b y src/evaluation/regresion.py dicen cosas distintas")


def test_lo_que_se_ejecuta_se_importa_de_src(celdas):
    codigo = "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")
    assert "from src.evaluation.regresion import concordancia_harrell, rmse_exactas" in codigo


def test_la_comparacion_ignora_la_documentacion_y_ve_la_logica():
    con_doc = 'def f(x):\n    """Explica."""\n    return x + 1\n'
    sin_doc = "def f(x):\n    return x + 1\n"
    otra = 'def f(x):\n    """Explica."""\n    return x + 2\n'
    assert _definiciones(con_doc) == _definiciones(sin_doc)
    assert _definiciones(con_doc) != _definiciones(otra)
