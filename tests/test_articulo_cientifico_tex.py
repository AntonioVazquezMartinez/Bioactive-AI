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


def test_el_orden_combinado_de_las_dos_fases_se_dice_pendiente():
    """La combinación de las dos fases en un solo ranking no existe, y el texto no puede darla por hecha.

    La [C.5](docs/decisiones.md) se revisó el 12 de noviembre: lo que se entrega es el cuaderno que
    ordena **por fase**, no una lista combinada, y la combinación sigue pendiente (C.3). Este
    artículo decía «sus salidas son evidencia que se combina en un único orden de prioridad» —en
    presente— dos oraciones antes de llamar pendiente a esa misma combinación, y la guarda de cifras
    no lo veía porque no es una cifra. Así que: toda mención de ese orden único lleva al lado la
    palabra que lo marca pendiente.
    """
    tex = _tex()
    menciones = list(re.finditer(r"(?:[úu]nico orden|un solo ranking|orden de prioridad|orden combinado)", tex))
    assert menciones, (
        "el artículo ya no menciona el orden combinado de las dos fases: si se quitó a propósito, "
        "quita esta guarda; si cambió la redacción, ajusta el patrón")
    sueltas = []
    for m in menciones:
        contexto = tex[max(0, m.start() - 320):m.end() + 320]
        if re.search(r"pendiente|todav[ií]a no|no existe|queda\b|cuando exista", contexto, re.I):
            continue
        sueltas.append(re.sub(r"\s+", " ", tex[max(0, m.start() - 80):m.end() + 80]))
    assert not sueltas, (
        "estas menciones presentan como hecho el orden que combina las dos fases, que no existe: "
        + "; ".join(f"«…{s}…»" for s in sueltas))
