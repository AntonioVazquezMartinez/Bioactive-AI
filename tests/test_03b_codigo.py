"""El cuaderno 03b trae el código de sus funciones y `src/` guarda la misma lógica.

Que el cuaderno se lea solo es el motivo de tener el código en sus celdas; que `src/`
lo pruebe es el motivo de tenerlo allá. Si las dos copias se separan, el cuaderno dejaría
de describir lo que `src/` prueba, así que esta prueba compara el árbol sintáctico de
cada función y clase: los espacios y los comentarios no cuentan, la lógica sí.
"""

import ast
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = RAIZ / "notebooks" / "03b_Baseline_regresion_actividad.ipynb"

DONDE = {
    "src/evaluation/regresion.py": ["_exactas", "concordancia_harrell", "spearman_exactas",
                                    "rmse_exactas", "metricas_regresion"],
    "src/models/tobit.py": ["_log_phi", "_log_masa", "verosimilitud", "RegresionTobit"],
    "src/models/baseline_regresion.py": ["SoloExactas", "ImputadaEnCota", "TobitComparable",
                                         "baselines", "intervalo_util", "evaluar_baselines",
                                         "tabla"],
}


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


@pytest.mark.parametrize("ruta,nombres", DONDE.items())
def test_cada_funcion_del_cuaderno_es_la_de_src(ruta, nombres, del_cuaderno):
    de_src = _definiciones((RAIZ / ruta).read_text(encoding="utf-8"))
    for nombre in nombres:
        assert nombre in del_cuaderno, f"{nombre} no está en el cuaderno 03b"
        assert del_cuaderno[nombre] == de_src[nombre], (
            f"{nombre}: el cuaderno 03b y {ruta} dicen cosas distintas")
