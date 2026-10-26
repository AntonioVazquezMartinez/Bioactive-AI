"""El cuaderno 04b trae el código de sus métricas y `src/` guarda la misma lógica.

Que el cuaderno se lea solo es el motivo de tener el código en sus celdas; que `src/`
lo pruebe es el motivo de tenerlo allá. Si las dos copias se separan, el cuaderno dejaría
de describir lo que `src/` prueba, así que esta prueba compara el árbol sintáctico de
cada función: los espacios y los comentarios no cuentan, la lógica sí.
"""

import ast
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "04b_Regresion_actividad.ipynb"
FUNCIONES = ["_exactas", "concordancia_harrell", "rmse_exactas"]


def _definiciones(fuente: str) -> dict[str, str]:
    return {n.name: ast.dump(n) for n in ast.parse(fuente).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


@pytest.fixture(scope="module")
def del_cuaderno() -> dict[str, str]:
    celdas = json.loads(CUADERNO.read_text(encoding="utf-8"))["cells"]
    out: dict[str, str] = {}
    for c in celdas:
        if c["cell_type"] == "code":
            out.update(_definiciones("".join(c["source"])))
    return out


@pytest.mark.parametrize("nombre", FUNCIONES)
def test_cada_funcion_del_cuaderno_es_la_de_src(nombre, del_cuaderno):
    de_src = _definiciones(
        (RAIZ / "src" / "evaluation" / "regresion.py").read_text(encoding="utf-8"))
    assert nombre in del_cuaderno, f"{nombre} no está en el cuaderno 04b"
    assert del_cuaderno[nombre] == de_src[nombre], (
        f"{nombre}: el cuaderno 04b y src/evaluation/regresion.py dicen cosas distintas")
