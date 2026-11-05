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
    "agrupar_iguales": "src/features/huellas.py",
    "AgregarHuellas": "src/features/huellas.py",
    "poder_spearman": "src/features/seleccion.py",
    "DepuracionDescriptores": "src/features/seleccion.py",
    "SeleccionL1": "src/features/seleccion.py",
    "MediaPorDiana": "src/models/pisos.py",
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
    assert "from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan" in codigo
    assert "from src.features.seleccion import DepuracionDescriptores, SeleccionL1" in codigo
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


def _modelos(ruta: Path) -> dict[str, str]:
    """`MODELOS` como nombre → definición sin espacios, ignorando los comentarios del bloque."""
    for c in _celdas(ruta):
        fuente = "".join(c["source"])
        if c["cell_type"] == "code" and "MODELOS = {" in fuente:
            bloque = fuente.split("MODELOS = {", 1)[1].split("\n}", 1)[0]
            pares = {}
            for linea in bloque.splitlines():
                if not linea.strip() or linea.strip().startswith("#"):
                    continue
                nombre, definicion = linea.split(":", 1)
                pares[nombre.strip().strip('"')] = re.sub(r"\s+", "", definicion).rstrip(",")
            return pares
    raise AssertionError(f"{ruta.name} no define MODELOS")


def test_los_modelos_del_04b_estan_iguales_en_el_04c():
    """Cada modelo del 04b se copia con sus hiperparámetros: de eso depende que el brazo de control
    repita la corrida registrada, y que cada fila de la comparativa sea un par.

    El 04c **puede añadir** modelos y no puede cambiar ninguno de los seis. `linear_svr` está de más
    a propósito: el SVR con núcleo no cabe en los brazos anchos (un solo ajuste pasó de 27 minutos),
    así que la familia de márgenes se cubre ahí con el núcleo lineal, y para que sea comparable se
    corre también en los tres brazos estrechos. No tiene par en el 04b, y la lectura lo dice.
    """
    del_04c, del_04b = _modelos(CUADERNO), _modelos(CUADERNO_04B)
    faltan = sorted(set(del_04b) - set(del_04c))
    assert not faltan, f"el 04c perdió modelos del 04b: {faltan}"
    distintos = {n: (del_04b[n], del_04c[n]) for n in del_04b if del_04c[n] != del_04b[n]}
    assert not distintos, f"definiciones que difieren del 04b: {distintos}"
