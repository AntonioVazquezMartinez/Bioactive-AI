"""El cuaderno 04c muestra el código de sus huellas y de su depuración, y es el de `src/`.

El cuaderno ejecuta las huellas importándolas de `src/features/`, y una celda de texto las
muestra para que se lea sin abrir otro archivo. Esta prueba ata las dos cosas con el mismo
criterio que la del 04b (el árbol sintáctico, sin docstrings), y comprueba además que la
función `medir`, que el 04c repite del 04b para que sus cifras sean comparables, no se separe
de la original.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "04c_Regresion_actividad_huellas.ipynb"
CUADERNO_04B = RAIZ / "notebooks" / "04b_Regresion_actividad.ipynb"
FUNCIONES = {
    "identificadores_morgan": "src/features/huellas.py",
    "AgregarHuellas": "src/features/huellas.py",
    "poder_spearman": "src/features/seleccion.py",
    "DepuracionDescriptores": "src/features/seleccion.py",
}


def _sin_docstring(nodo):
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


def _celdas(ruta: Path) -> list[dict]:
    return json.loads(ruta.read_text(encoding="utf-8"))["cells"]


@pytest.fixture(scope="module")
def celdas() -> list[dict]:
    return _celdas(CUADERNO)


@pytest.fixture(scope="module")
def mostrado(celdas) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in celdas:
        if c["cell_type"] == "markdown":
            for bloque in re.findall(r"```python\n(.*?)```", "".join(c["source"]), re.S):
                out.update(_definiciones(bloque))
    return out


@pytest.mark.parametrize("nombre,archivo", FUNCIONES.items())
def test_cada_funcion_mostrada_es_la_de_src(nombre, archivo, mostrado):
    de_src = _definiciones((RAIZ / archivo).read_text(encoding="utf-8"))
    assert nombre in de_src, f"{nombre} ya no existe en {archivo}"
    assert nombre in mostrado, f"{nombre} no se muestra en el cuaderno 04c"
    assert mostrado[nombre] == de_src[nombre], (
        f"{nombre}: el cuaderno 04c y {archivo} dicen cosas distintas")


def test_lo_que_se_ejecuta_se_importa_de_src(celdas):
    codigo = "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")
    assert "from src.features.huellas import AgregarHuellas, identificadores_morgan" in codigo
    assert "from src.features.seleccion import DepuracionDescriptores" in codigo
    assert "from src.evaluation.regresion import concordancia_harrell, rmse_exactas" in codigo


def _medir(ruta: Path) -> str:
    for c in _celdas(ruta):
        if c["cell_type"] == "code":
            definiciones = _definiciones("".join(c["source"]))
            if "medir" in definiciones:
                return definiciones["medir"]
    raise AssertionError(f"{ruta.name} no define `medir`")


def test_medir_es_la_del_04b():
    """Si cambia una, la otra tiene que cambiar: el brazo de control debe repetir el 04b."""
    assert _medir(CUADERNO) == _medir(CUADERNO_04B)


def test_los_modelos_son_los_del_04b(celdas):
    """Los seis modelos y sus hiperparámetros se copian del 04b: la comparación depende de eso."""
    def modelos(ruta):
        for c in _celdas(ruta):
            fuente = "".join(c["source"])
            if c["cell_type"] == "code" and "MODELOS = {" in fuente:
                bloque = fuente.split("MODELOS = {", 1)[1].split("\n}", 1)[0]
                return re.sub(r"\s+", "", bloque)
        raise AssertionError(f"{ruta.name} no define MODELOS")
    assert modelos(CUADERNO) == modelos(CUADERNO_04B)
