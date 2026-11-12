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


def test_toda_figura_nombrada_en_el_texto_existe_como_pie():
    """Una «Figura C2» en el texto sin un pie que la numere así se queda apuntando a nada.

    La numeración de los anexos se hace con un contador que el `.tex` reinicia en la primera figura de anexo
    (`\\renewcommand{\\thefigure}{C\\arabic{figure}}`), así que el número real depende del orden: aquí se
    reconstruye contando los entornos `figure` y se compara con lo que el texto nombra.
    """
    tex = _tex()
    etiquetas, n, anexo = set(), 0, False
    for m in re.finditer(r"\\renewcommand\{\\thefigure\}\{C|\\begin\{figure\*?\}", tex):
        if m.group(0).startswith("\\renewcommand"):
            anexo, n = True, 0
        else:
            n += 1
            etiquetas.add(f"C{n}" if anexo else str(n))
    sin_pies = re.sub(r"\\caption\{.*?\}\n", "", tex, flags=re.S)
    nombradas = set(re.findall(r"Figura (C?\d+)\b", sin_pies))
    assert etiquetas, "no se encontró ningún entorno figure"
    assert nombradas <= etiquetas, f"el texto nombra figuras sin pie: {sorted(nombradas - etiquetas)}"


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
    # Los nombres son los de la plantilla del curso y de la rúbrica, en este orden.
    orden = ["\\section{Contexto de negocio y problema}", "\\section{Datos y preparación}",
             "\\section{Metodología y modelos}", "\\section{Resultados y validación}",
             "\\section{Implementación y operación}", "\\section{Conclusiones clave}",
             "\\section*{Referencias y anexos}"]
    posiciones = []
    for parte in orden:
        assert parte in tex, f"falta {parte}"
        posiciones.append(tex.index(parte))
    assert posiciones == sorted(posiciones), "las secciones no van en el orden de la rúbrica"
    for parte in ("\\printbibliography", "Declaración de uso de inteligencia artificial"):
        assert parte in tex, f"falta {parte}"


def test_no_se_desplaza_la_numeracion_de_la_plantilla():
    """La plantilla numera «Resultados y validación» como 4 e «Implementación» como 5: sin \\setcounter."""
    assert "\\setcounter{section}" not in _tex()


def test_cada_tabla_lleva_pie_y_la_declaracion_dice_el_modelo():
    tex = _tex()
    assert tex.count("\\begin{longtable}") == tex.count("\\caption{") - tex.count("\\begin{figure}"), \
        "hay tablas sin pie"
    declaracion = tex[tex.index("Declaración de uso de inteligencia artificial"):]
    assert "Claude Opus" in declaracion and "Claude Sonnet" in declaracion, "la declaración no dice el modelo"


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="sin pandoc no se puede regenerar")
def test_el_tex_coincide_con_el_borrador():
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "armar_articulo_tex.py"), "--revisar"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr or r.stdout
