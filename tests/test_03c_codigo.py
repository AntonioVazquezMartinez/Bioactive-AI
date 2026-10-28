"""El cuaderno 03c muestra el código de sus huellas y de su depuración, y es el de `src/`.

Mismo criterio que la prueba del 04c: lo mostrado y lo importado se comparan por su árbol
sintáctico, sin docstrings. Además el 03c no puede redefinir los modelos: tienen que venir de
`src/models/alternativos.py`, porque su brazo de control debe repetir la corrida registrada de los
seis modelos del 04.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "03c_Permeabilidad_huellas.ipynb"
FUNCIONES = {
    "identificadores_morgan": "src/features/huellas.py",
    "agrupar_iguales": "src/features/huellas.py",
    "AgregarHuellas": "src/features/huellas.py",
    "poder_spearman": "src/features/seleccion.py",
    "DepuracionDescriptores": "src/features/seleccion.py",
    "SeleccionL1": "src/features/seleccion.py",
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
    assert "from src.models import cargar, seleccion" in codigo


def test_los_modelos_son_los_seis_del_04(celdas):
    """El cuaderno no define sus propios modelos: usa `seleccion()` del catálogo, con las seis claves del 04."""
    codigo = "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")
    for ajeno in ("RandomForestClassifier(", "LogisticRegression(", "HistGradientBoostingClassifier(",
                  "KNeighborsClassifier(", "MLPClassifier(", "SVC("):
        assert ajeno not in codigo, f"el 03c define {ajeno} en vez de usar el catálogo"
    assert 'CLAVES = ("logistica", "arbol", "knn", "bayes", "svm_rbf", "mlp")' in codigo
