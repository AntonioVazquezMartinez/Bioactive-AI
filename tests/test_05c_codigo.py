"""El 05c muestra el código de su envoltura, y es el de `src/`.

Mismo criterio que las pruebas del 03c, el 04c y el 05: lo mostrado y lo importado se
comparan por su árbol sintáctico, sin docstrings. Lo específico de este cuaderno es que
atan tres invariantes suyas: que no redefine ningún modelo —los nueve vienen del catálogo
y de `ensambles_clasificacion.py`, porque su brazo de control debe reproducir lo que el 05
registró—, que el vocabulario de las huellas se aprende dentro de la canalización y no
antes, y que **no toca la partición de prueba**, que se lee una sola vez y se lee en el 05.
"""

import ast
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "05c_Ensambles_permeabilidad_huellas.ipynb"
FUNCIONES = {"CanalizacionConGrupos": "src/models/ensambles_clasificacion.py"}


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
    """Lo mostrado se compara sin docstring: el cuaderno enseña el cuerpo, no la prosa."""
    de_src = _definiciones((RAIZ / archivo).read_text(encoding="utf-8"))
    assert nombre in de_src, f"{nombre} ya no existe en {archivo}"
    assert nombre in mostrado, f"{nombre} no se muestra en el cuaderno 05c"
    assert mostrado[nombre] == de_src[nombre], (
        f"{nombre}: el cuaderno 05c y {archivo} dicen cosas distintas")


def test_lo_que_se_ejecuta_se_importa_de_src(codigo):
    for linea in ("from src.models import cargar, seleccion",
                  "from src.models.ensambles_clasificacion import CanalizacionConGrupos, ensambles",
                  "from src.features.huellas import AgregarHuellas, agrupar_iguales, "
                  "identificadores_morgan"):
        assert linea in codigo, linea


def test_no_define_sus_propios_modelos(codigo):
    """Los nueve salen del catálogo y de `ensambles_clasificacion.py`, sin tocar su definición.

    Si el 05c armara su propio bosque, su brazo de control dejaría de reproducir el 05 y la
    diferencia con las huellas se mezclaría con la diferencia entre dos bosques distintos.
    """
    for ajeno in ("RandomForestClassifier(", "HistGradientBoostingClassifier(",
                  "LogisticRegression(", "KNeighborsClassifier(", "MLPClassifier(",
                  "SVC(", "VotingClassifier(", "StackingClassifier(", "BaggingClassifier("):
        assert ajeno not in codigo, f"el 05c define {ajeno} en vez de usar src/"


def test_el_vocabulario_se_aprende_dentro_de_la_canalizacion(codigo):
    """`AgregarHuellas` va dentro del ajuste; elegirlo antes sería una fuga sin métrica.

    Y tiene que ir dentro de `CanalizacionConGrupos` y no de un `make_pipeline`, porque esa
    es la subclase que mantiene el paso de los grupos hasta el `stacking`.
    """
    assert "CanalizacionConGrupos([(\"huellas\", AgregarHuellas(" in codigo
    assert "make_pipeline" not in codigo
    arbol = ast.parse(codigo)
    llamadas = [n for n in ast.walk(arbol)
                if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "AgregarHuellas"]
    assert len(llamadas) == 1, "una sola construcción, la de `con_huellas`"


def test_no_toca_la_particion_de_prueba(codigo):
    """La prueba se lee una vez en todo el proyecto, y es en el 05; aquí ni la guarda aparece."""
    assert "tomar_prueba" not in codigo
    assert "incluir_prueba" not in codigo
    for comparacion in ast.walk(ast.parse(codigo)):
        if isinstance(comparacion, ast.Compare):
            valores = [comparacion.left, *comparacion.comparators]
            assert not any(isinstance(v, ast.Constant) and v.value == "prueba" for v in valores), (
                "no se filtra la partición a mano")


def test_la_regla_de_mejora_es_la_misma_de_los_demas(codigo):
    """Umbral igual a la dispersión del control, doce de quince, las dos métricas a la vez."""
    assert "MINIMO_PLIEGUES = 12" in codigo
    assert 'PRINCIPALES = ("mcc", "auprc_minoritaria")' in codigo
    assert '.std().max()), 3) for m in PRINCIPALES' in codigo
    assert '.unstack("metrica")[list(PRINCIPALES)].all(axis=1)' in codigo


def test_el_control_se_contrasta_con_una_corrida_registrada(codigo):
    """Una cifra citada necesita una corrida detrás, y el control necesita reproducir."""
    assert "2026-10-29-ingrid-1.5-ensambles-permeabilidad" in codigo
    assert 'json.loads(REGISTRO.read_text())["comparativa"]' in codigo
