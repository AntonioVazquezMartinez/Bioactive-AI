"""El cuaderno 05 muestra el código de sus ensambles, y es el de `src/`.

Mismo criterio que las pruebas del 03c y el 04c: lo mostrado y lo importado se comparan por
su árbol sintáctico, sin docstrings. Además el 05 no puede definir sus propios modelos
—tienen que venir del catálogo y de `ensambles.py`, porque su fila de referencia debe
comparar con lo que el 04 registró— y la prueba reservada solo puede salir por `tomar_prueba`,
que es la guarda del #54.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "05_Modelo_Final.ipynb"
FUNCIONES = {
    "StackingAgrupado": "src/models/ensambles.py",
    "ensambles": "src/models/ensambles.py",
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


@pytest.fixture(scope="module")
def celdas() -> list[dict]:
    return json.loads(CUADERNO.read_text(encoding="utf-8"))["cells"]


@pytest.fixture(scope="module")
def codigo(celdas) -> str:
    return "\n".join("".join(c["source"]) for c in celdas if c["cell_type"] == "code")


@pytest.fixture(scope="module")
def mostrado(celdas) -> dict[str, str]:
    out: dict[str, str] = {}
    for c in celdas:
        if c["cell_type"] == "markdown":
            for bloque in re.findall(r"```python\n(.*?)```", "".join(c["source"]), re.S):
                out.update(_definiciones(bloque))
    return out


@pytest.mark.parametrize("nombre,archivo", FUNCIONES.items())
def test_cada_definicion_mostrada_es_la_de_src(nombre, archivo, mostrado):
    de_src = _definiciones((RAIZ / archivo).read_text(encoding="utf-8"))
    assert nombre in de_src, f"{nombre} ya no existe en {archivo}"
    assert nombre in mostrado, f"{nombre} no se muestra en el cuaderno 05"
    assert mostrado[nombre] == de_src[nombre], (
        f"{nombre}: el cuaderno 05 y {archivo} dicen cosas distintas")


def test_lo_que_se_ejecuta_se_importa_de_src(codigo):
    for linea in ("from src.models import cargar, seleccion",
                  "from src.models.ensambles import ensambles",
                  "from src.models.ajuste import BusquedaAnidada",
                  "from src.tracking import tomar_prueba"):
        assert linea in codigo, linea


def test_no_define_sus_propios_modelos(codigo):
    """Los individuales salen del catálogo y los ensambles de `ensambles.py`."""
    for ajeno in ("RandomForestClassifier(", "HistGradientBoostingClassifier(",
                  "LogisticRegression(", "KNeighborsClassifier(", "MLPClassifier(",
                  "SVC(", "VotingClassifier(", "StackingClassifier(", "BaggingClassifier("):
        assert ajeno not in codigo, f"el 05 define {ajeno} en vez de usar src/"


def test_la_prueba_solo_sale_por_la_guarda(codigo):
    """La partición de prueba se toca una vez y con bitácora (#54): nunca filtrando a mano.

    Se cuentan llamadas del árbol sintáctico y no apariciones del texto, porque la celda de
    registro nombra la guarda dentro de una cadena y eso no es tocar la prueba.
    """
    llamadas = [n for n in ast.walk(ast.parse(codigo))
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "tomar_prueba"]
    assert len(llamadas) == 1, "la prueba se toca una sola vez"
    pasados = {k.arg for k in llamadas[0].keywords}
    assert {"final", "motivo"} <= pasados, "la guarda necesita final=True y un motivo"
    # Comparar una columna contra "prueba" es filtrar la partición a mano, que es justo lo
    # que la guarda existe para evitar: se saltaría la bitácora sin que nadie lo note.
    for comparacion in ast.walk(ast.parse(codigo)):
        if isinstance(comparacion, ast.Compare):
            valores = [comparacion.left, *comparacion.comparators]
            assert not any(isinstance(v, ast.Constant) and v.value == "prueba" for v in valores), (
                "no se filtra la partición a mano")


def test_la_busqueda_de_hiperparametros_agrupa_por_dentro(codigo):
    """Con `GridSearchCV` suelto la rejilla se elegiría sobre una medición inflada (1.2)."""
    assert "BusquedaAnidada(" in codigo
    assert "GridSearchCV" not in codigo and "RandomizedSearchCV" not in codigo


def test_los_graficos_usan_predicciones_fuera_de_pliegue(codigo):
    """Un gráfico sobre datos que el modelo vio describe su memoria, no su desempeño."""
    assert "p_fdp = fdp[FINAL][0]" in codigo
    for grafico in ("curva_roc(y, p_fdp", "curva_precision_exhaustividad(y, p_fdp",
                    "matriz_confusion(y, p_fdp"):
        assert grafico in codigo, grafico
