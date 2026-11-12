"""El artículo científico a doble columna se escribe a mano, así que necesita sus propias guardas.

El entregable de la rúbrica se genera desde su borrador y `tests/test_articulo_tex.py` compara los
dos; aquí no hay borrador que comparar, porque este documento no sigue la numeración de ocho
secciones de la plantilla del curso y no puede salir de la misma fuente (ver el README de la
carpeta). Lo que queda es comprobar sin compilar lo que más a menudo rompe una compilación —una
cita cuya clave no está en la bibliografía, una figura que apunta a un SVG o a un archivo que no
existe, un entorno sin cerrar— y lo que distingue a este documento: que sea a doble columna y que
toda figura y toda tabla esté referenciada desde el texto.

No hay pdfLaTeX ni Biber en CI, así que el PDF no se compila aquí: se compila con
`sh scripts/compilar_articulo.sh articulo-cientifico`, que necesita Docker.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "docs" / "reportes" / "articulo-cientifico"
TEX = CARPETA / "articulo-cientifico.tex"
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
        assert (CARPETA / r).exists(), f"{r} no existe (las figuras son un enlace a ../articulo/figuras)"


def test_los_entornos_estan_balanceados():
    tex = _tex()
    for entorno in set(re.findall(r"\\begin\{(\w+\*?)\}", tex)):
        assert tex.count(f"\\begin{{{entorno}}}") == tex.count(f"\\end{{{entorno}}}"), entorno


def test_va_a_doble_columna():
    """Es la razón de ser de este documento frente al entregable de la rúbrica."""
    assert re.search(r"\\documentclass\[[^\]]*twocolumn", _tex()), "no está declarado a doble columna"


def test_toda_figura_y_toda_tabla_se_referencia_desde_el_texto():
    tex = _tex()
    etiquetas = set(re.findall(r"\\label\{((?:fig|tab):[^}]+)\}", tex))
    assert etiquetas, "no hay figuras ni tablas etiquetadas"
    referidas = {r for grupo in re.findall(r"\\ref\{([^}]*)\}", tex) for r in grupo.split(",")}
    assert etiquetas <= referidas, f"sin mención en el texto: {sorted(etiquetas - referidas)}"


def test_no_queda_markdown_sin_convertir():
    """Se escribe a mano desde el borrador en Markdown; es fácil arrastrar su sintaxis."""
    cuerpo = _tex()[_tex().index(r"\begin{document}"):]
    assert "`" not in cuerpo, "quedó una comilla invertida sin convertir"
    assert not re.search(r"\*\*|\[@|!\[", cuerpo), "quedó sintaxis de Markdown o de citas sin convertir"


def test_el_resumen_cabe_en_lo_que_pide_una_revista():
    tex = _tex()
    resumen = tex[tex.index(r"\resumenancho{"):tex.index(r"\begin{figure*}")]
    palabras = len(re.sub(r"\\[a-zA-Z]+\*?\{?|[{}%]", " ", resumen).split())
    assert 150 <= palabras <= 350, f"el resumen tiene {palabras} palabras; se busca entre 150 y 350"


def test_lleva_declaracion_de_ia_con_su_modelo_y_las_referencias():
    tex = _tex()
    assert "\\printbibliography" in tex, "faltan las referencias"
    declaracion = tex[tex.index("Declaración de uso de inteligencia artificial"):]
    assert "Claude Opus" in declaracion and "Claude Sonnet" in declaracion, \
        "la declaración no dice el modelo"
