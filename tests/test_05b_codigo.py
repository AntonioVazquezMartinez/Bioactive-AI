"""El cuaderno 05b muestra el código de sus ensambles y del AFT, y es el de `src/`.

El cuaderno ejecuta los modelos importándolos de `src/models/`, y celdas de texto
los muestran para que se lean sin abrir otro archivo. Esta prueba compara el árbol
sintáctico de cada definición mostrada contra la de `src/` (los espacios y comentarios
no cuentan, la lógica sí) y comprueba que lo que se ejecuta se importe de `src/`.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "05b_Ensambles_actividad.ipynb"
DONDE = {
    "src/models/ensambles.py": ["AfinadoAgrupado", "ApiladoAgrupado", "ensambles"],
    "src/models/aft.py": ["RegresionAFT"],
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


@pytest.mark.parametrize("archivo,nombres", DONDE.items())
def test_cada_funcion_mostrada_es_la_de_src(archivo, nombres, mostrado):
    de_src = _definiciones((RAIZ / archivo).read_text(encoding="utf-8"))
    for nombre in nombres:
        assert nombre in de_src, f"{nombre} ya no existe en {archivo}"
        assert nombre in mostrado, f"{nombre} no se muestra en el cuaderno 05b"
        assert mostrado[nombre] == de_src[nombre], (
            f"{nombre}: el cuaderno 05b y {archivo} dicen cosas distintas")


def test_lo_que_se_ejecuta_se_importa_de_src(celdas):
    codigo = "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")
    assert "from src.models.ensambles import AfinadoAgrupado, ApiladoAgrupado, ensambles" in codigo
    assert "from src.models.aft import RegresionAFT" in codigo
    assert "from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan" in codigo
    assert "from src.models.baseline_regresion import SoloExactas, evaluar_baselines, tabla" in codigo
    assert "from src.models.pisos import MediaPorDiana" in codigo
    assert "from src.tracking import Corrida" in codigo


def test_las_celdas_de_codigo_no_tienen_salidas_guardadas(celdas):
    """El cuaderno 05b debe mantener sus salidas limpias antes de la corrida completa."""
    for i, c in enumerate(celdas):
        if c["cell_type"] == "code":
            assert not c.get("outputs"), f"La celda de código {i} tiene salidas guardadas"
            assert c.get("execution_count") is None, f"La celda {i} tiene execution_count no nulo"
