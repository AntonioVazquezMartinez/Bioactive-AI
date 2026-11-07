"""`articulo.tex` se arma desde `borrador.md` y no se edita a mano.

Aquí no hay pdfLaTeX ni Biber, así que el PDF no se compila en CI (solo en Overleaf). Lo que sí se
puede comprobar sin compilar es lo que más a menudo rompe una compilación: una cita cuya clave no
está en la bibliografía, una figura que apunta a un SVG o a un archivo que no existe, un restos de
Markdown que quedó sin convertir, y que el `.tex` coincida con el borrador del que sale.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "docs" / "reportes" / "articulo"
TEX = CARPETA / "articulo.tex"
BIB = RAIZ / "docs" / "referencias" / "bibliografia.bib"


def _tex() -> str:
    return TEX.read_text(encoding="utf-8")


def test_las_claves_citadas_estan_en_la_bibliografia():
    claves = set(re.findall(r"^@\w+\{([^,\s]+),", BIB.read_text(encoding="utf-8"), re.M))
    citadas = {k.strip() for grupo in re.findall(r"\\(?:auto|text|paren)cite\{([^}]*)\}", _tex())
               for k in grupo.split(",")}
    assert citadas, "el artículo no cita nada"
    assert citadas <= claves, f"claves sin entrada en la bibliografía: {sorted(citadas - claves)}"


def test_las_figuras_son_png_y_existen():
    rutas = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", _tex())
    figuras = [r for r in rutas if r.startswith("figuras/")]
    assert figuras, "el artículo no trae ninguna figura"
    for r in figuras:
        assert r.endswith(".png"), f"{r}: pdfLaTeX no incluye SVG"
        assert (CARPETA / r).exists(), f"{r} no existe"


def test_no_queda_markdown_sin_convertir():
    tex = _tex()
    cuerpo = tex[tex.index(r"\begin{document}"):]
    assert "`" not in cuerpo, "quedó una comilla invertida sin convertir"
    assert "FIGURAMARCA" not in tex and "pandocbounded" not in tex
    assert not re.search(r"\*\*|\[@", cuerpo), "quedó sintaxis de Markdown o de citas sin convertir"


def test_los_entornos_estan_balanceados():
    tex = _tex()
    for entorno in set(re.findall(r"\\begin\{(\w+\*?)\}", tex)):
        assert tex.count(f"\\begin{{{entorno}}}") == tex.count(f"\\end{{{entorno}}}"), entorno


def test_el_resumen_cabe_en_lo_que_pide_la_rubrica():
    tex = _tex()
    resumen = tex[tex.index(r"\begin{abstract}"):tex.index(r"\end{abstract}")]
    palabras = len(re.sub(r"\\[a-zA-Z]+\*?\{?|[{}]", " ", resumen).split()) - 1
    assert 150 <= palabras <= 250, f"el resumen tiene {palabras} palabras, la rúbrica pide 150 a 250"


def test_las_seccion_de_la_plantilla_estan_todas():
    tex = _tex()
    for parte in ("\\section{Problema}", "\\section{Datos y partición}", "\\section{Métodos}",
                  "\\section{Resultados}", "\\section{Implementación y operación}",
                  "\\section{Conclusiones y limitaciones}", "\\printbibliography",
                  "Declaración de uso de inteligencia artificial"):
        assert parte in tex, f"falta {parte}"


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="sin pandoc no se puede regenerar")
def test_el_tex_coincide_con_el_borrador():
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "armar_articulo_tex.py"), "--revisar"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout
