"""Los notebooks tienen que poder ejecutarse de principio a fin, en orden.

La rúbrica del curso lo exige, y es además lo que permite reproducir las
cifras. No lo garantiza nada automático: el notebook versionado guarda sus
salidas, así que **parece** ejecutado aunque su código no corra en orden.

Pasó con el `02`: la celda 48 usaba `LogisticRegression` y la importaba hasta
la 55, de modo que ejecutarlo secuencialmente fallaba con `NameError` mientras
las salidas guardadas —de una corrida hecha en otro orden— se veían bien
(issue #87). Lo encontró una revisión al regenerar `data/processed/`.

Esta comprobación es estática: recorre las celdas de código en orden y marca
los nombres que se usan antes de que ninguna celda anterior los defina. No
ejecuta nada, así que es barata y corre en CI, pero por lo mismo no detecta
fallos en tiempo de ejecución.
"""

import ast
import builtins
import json
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((RAIZ / "notebooks").glob("*.ipynb"))

# Los nombres que IPython define por su cuenta y que `ast` no puede ver.
DE_IPYTHON = {"get_ipython", "display", "In", "Out", "exit", "quit"}


def _nombres(arbol: ast.AST) -> tuple[set[str], set[str]]:
    """Los nombres que el árbol lee y los que define."""
    leidos = {n.id for n in ast.walk(arbol)
              if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    definidos: set[str] = set()
    for n in ast.walk(arbol):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            definidos |= {(a.asname or a.name).split(".")[0] for a in n.names}
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
            definidos.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            definidos.add(n.name)
        elif isinstance(n, ast.arg):
            definidos.add(n.arg)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            definidos.add(n.name)
        elif isinstance(n, ast.alias):
            definidos.add((n.asname or n.name).split(".")[0])
    return leidos, definidos


@pytest.mark.parametrize("ruta", NOTEBOOKS, ids=lambda p: p.name)
def test_no_usa_nombres_antes_de_definirlos(ruta: Path):
    celdas = json.loads(ruta.read_text(encoding="utf-8"))["cells"]
    # `dir(__builtins__)` no sirve aquí: dentro de un módulo importado
    # `__builtins__` es el diccionario y no el módulo, así que devuelve
    # los métodos del dict y no `print`, `len` ni el resto.
    disponibles = set(dir(builtins)) | DE_IPYTHON
    faltantes = []

    for i, celda in enumerate(celdas):
        if celda["cell_type"] != "code":
            continue
        fuente = "".join(celda["source"])
        # Las líneas mágicas de IPython (%, !) no son Python válido.
        fuente = "\n".join(l for l in fuente.splitlines()
                           if not l.lstrip().startswith(("%", "!", "?")))
        try:
            arbol = ast.parse(fuente)
        except SyntaxError:
            continue
        leidos, definidos = _nombres(arbol)
        sin_definir = leidos - disponibles - definidos
        if sin_definir:
            faltantes.append(f"celda {i}: {', '.join(sorted(sin_definir))}")
        disponibles |= definidos

    assert not faltantes, (
        f"{ruta.name} no se ejecuta en orden; usa nombres antes de definirlos:\n  "
        + "\n  ".join(faltantes))
