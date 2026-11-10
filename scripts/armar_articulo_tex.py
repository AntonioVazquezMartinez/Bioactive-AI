#!/usr/bin/env python3
"""Arma `docs/reportes/articulo/articulo.tex` desde `borrador.md` y la plantilla del curso.

El borrador en Markdown es la única fuente del texto: ahí se revisan las cifras y se hacen los
cambios. Este script solo lo traslada a la plantilla (`plantilla.tex`: preámbulo, APA 7 con Biber,
encabezado con logo), así que el `.tex` nunca se edita a mano y no se desfasa del borrador.

    python3 scripts/armar_articulo_tex.py            # reescribe articulo.tex
    python3 scripts/armar_articulo_tex.py --revisar  # falla si articulo.tex no coincide con el borrador

Necesita `pandoc` (3.x). Qué hace, en orden:

1. Parte el borrador por sección. El resumen (primer párrafo de «Resumen») va al `abstract`;
   la figura 1 queda justo después. La numeración es la de la plantilla del curso: el resumen y
   las referencias no llevan número, «Contexto de negocio y problema» es la 1 e «Implementación
   y operación» la 5 (la rúbrica dice «en la sección 5»).
2. Las claves de bibliografía que el borrador escribe entre comillas invertidas se vuelven citas
   (`\\autocite`), y un grupo entre paréntesis de solo claves se junta en una sola cita.
3. Cada figura (imagen más su pie en cursiva) pasa a un entorno `figure` con el PNG, no el SVG:
   pdfLaTeX no incluye SVG.
4. La tabla de la sección 6 se ensancha por columna, porque el Markdown solo da anchos iguales.
5. Pandoc convierte el resto; lo que no es texto corrido (figuras, tablas) se reinserta después.

**No compila aquí**: la máquina no tiene pdfLaTeX ni Biber. Compila en Overleaf (ver el README de
la carpeta). `tests/test_articulo_tex.py` revisa lo que sí se puede revisar sin compilar.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "docs" / "reportes" / "articulo"
BORRADOR = CARPETA / "borrador.md"
PLANTILLA = CARPETA / "plantilla.tex"
SALIDA = CARPETA / "articulo.tex"
BIB = RAIZ / "docs" / "referencias" / "bibliografia.bib"

AUTORES = ("Ingrid Pamela Ruiz Puga", "Artemio Santiago Padilla Robles", "José Antonio Vázquez Martínez")
# Ancho relativo de las columnas de la tabla de la sección 6 (el Markdown no da más que iguales).
# Va primero la de 4 columnas: la de 3 es subcadena de ella.
ANCHO_TABLA = {"|:--|:--|:--|:--|": "|:-------|:-----------|:--------------------|:--------|",
               "|:--|:--|:--|": "|:---------|:-----------|:----------------|"}
PENDIENTE = r"\textcolor{red}{[%s]}"

# Lo que pdfLaTeX no conoce, y cómo se dibuja.
UNICODE = {
    "2212": r"\ensuremath{-}",
    "2265": r"\ensuremath{\geq}",
    "2192": r"\ensuremath{\rightarrow}",
    "00B5": r"\ensuremath{\mu}",
}

EXTRA_PREAMBULO = r"""
% --- Añadidos para el artículo generado desde borrador.md (scripts/armar_articulo_tex.py) ---
\usepackage{longtable}
\usepackage{array}
\usepackage{calc}
\usepackage{xcolor}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\addto\captionsspanish{\renewcommand{\tablename}{Tabla}} % babel-spanish dice «Cuadro»; la plantilla pide «Tabla»
\newcounter{none} % el longtable de pandoc declara \LTcaptype{none} y espera que el contador exista
% El campo `note` de bibliografia.bib son anotaciones internas del equipo («LEÍDO PARCIAL», cómo se verificó
% cada entrada): sirven en docs/referencias y no deben salir impresas en las referencias del artículo.
\AtEveryBibitem{\clearfield{note}}
\setlength{\emergencystretch}{3em}
""" + "".join(f"\\DeclareUnicodeCharacter{{{h}}}{{{d}}}\n" for h, d in UNICODE.items())


def claves_bib() -> set[str]:
    return set(re.findall(r"^@\w+\{([^,\s]+),", BIB.read_text(encoding="utf-8"), re.M))


def pandoc(texto: str, ancho_tabla: bool = False) -> str:
    if shutil.which("pandoc") is None:
        sys.exit("hace falta pandoc (brew install pandoc)")
    r = subprocess.run(
        ["pandoc", "-f", "markdown-tex_math_dollars-smart-auto_identifiers-raw_tex-yaml_metadata_block",
         "-t", "latex", "--biblatex", "--wrap=none"],
        input=texto, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def citas(texto: str, claves: set[str]) -> str:
    """`clave` entre comillas invertidas → cita; un paréntesis de solo claves → una sola cita."""
    clave = r"`([A-Za-z][A-Za-z0-9_:+-]*)`"

    def grupo(m):
        ks = re.findall(clave, m.group(0))
        if ks and all(k in claves for k in ks):
            return "[" + "; ".join(f"@{k}" for k in ks) + "]"
        return m.group(0)

    texto = re.sub(r"\(\s*" + clave + r"(?:\s*,\s*" + clave + r")*\s*\)", grupo, texto)
    return re.sub(clave, lambda m: f"[@{m.group(1)}]" if m.group(1) in claves else m.group(0), texto)


def figuras(texto: str) -> tuple[str, dict[str, str]]:
    """Cada imagen con su pie en cursiva pasa a un marcador; devuelve los entornos `figure`."""
    patron = re.compile(r"!\[[^\]]*\]\(figuras/(\w+)\.svg\)\n\n\*Figura (C?)(\d+)\.\s+(.*?)\*(?:\n|$)", re.S)
    bloques: dict[str, str] = {}

    def sustituye(m):
        nombre, anexo, pie = m.group(1), m.group(2), " ".join(m.group(4).split())
        marca = f"FIGURAMARCA{len(bloques)}"
        prefijo = ""
        if anexo and not any("renewcommand" in b for b in bloques.values()):
            prefijo = "\\setcounter{figure}{0}\\renewcommand{\\thefigure}{C\\arabic{figure}}\n"
        bloques[marca] = (prefijo + "\\begin{figure}[H]\n  \\centering\n"
                          f"  \\includegraphics[width=0.9\\linewidth]{{figuras/{nombre}.png}}\n"
                          f"  \\caption{{{pandoc(pie)}}}\n  \\label{{fig:{nombre}}}\n\\end{{figure}}")
        return marca + "\n"

    return patron.sub(sustituye, texto), bloques


def seccion_a_latex(titulo: str, cuerpo: str, claves: set[str], numerada: bool = True) -> str:
    cuerpo = citas(cuerpo, claves)
    for viejo, nuevo in ANCHO_TABLA.items():
        cuerpo = cuerpo.replace(viejo, nuevo)
    cuerpo = re.sub(r"^### \d+(\.\d+)* ", "## ", cuerpo, flags=re.M)     # subsecciones sin su número
    cuerpo, bloques = figuras(cuerpo)
    tex = pandoc(cuerpo)
    for marca, bloque in bloques.items():
        tex = tex.replace(marca, bloque)
    orden = "\\section" if numerada else "\\section*"
    return f"{orden}{{{titulo}}}\n{tex}\n"


def partir(md: str) -> tuple[str, dict[str, str], str]:
    """(título, {encabezado de sección: cuerpo}, anexos)."""
    titulo = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    cuerpo = md[md.index("\n## Resumen"):]
    partes = re.split(r"^## ", cuerpo, flags=re.M)[1:]
    return titulo, {p.split("\n", 1)[0].strip(): p.split("\n", 1)[1] for p in partes}, ""


def construir() -> str:
    claves = claves_bib()
    md = BORRADOR.read_text(encoding="utf-8")
    titulo, secciones, _ = partir(md)
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    preambulo = plantilla[:plantilla.index("% --- Título ---")].rstrip() + "\n" + EXTRA_PREAMBULO

    resumen_md = secciones["Resumen"]
    primero, resto = resumen_md.strip().split("\n\n", 1)
    resumen = pandoc(citas(primero, claves))
    resto_tex, bloques = figuras(citas(resto, claves))
    resto_tex = pandoc(resto_tex)
    for marca, bloque in bloques.items():
        resto_tex = resto_tex.replace(marca, bloque)

    cuerpo = []
    for encabezado, texto in secciones.items():
        if encabezado in ("Resumen", "Anexos"):
            continue
        if encabezado == "Referencias y anexos":     # sin número, como pide la plantilla
            cuerpo.append(seccion_a_latex(encabezado, texto, claves, numerada=False))
        else:
            cuerpo.append(seccion_a_latex(re.match(r"\d+\. (.+)", encabezado).group(1), texto, claves))
    anexos = seccion_a_latex("Anexos", secciones["Anexos"], claves, numerada=False)

    autores = "\\quad ".join(AUTORES[:2]) + "\\\\[2pt] " + AUTORES[2]
    encabezado = (
        "% Generado por scripts/armar_articulo_tex.py desde borrador.md y plantilla.tex.\n"
        "% No se edita a mano: se cambia el borrador y se vuelve a generar.\n"
        + preambulo
        + "\n% --- Título ---\n"
        + f"\\title{{\\textbf{{{pandoc(titulo)}}}}}\n"
        + f"\\author{{{autores}\\\\[6pt]\n"
        + "  \\normalsize Proyecto Integrador · Maestría en Inteligencia Artificial Aplicada \\\\[6pt]\n"
        + "  \\normalsize Asesora: Dra. Grettel Barceló Alonso \\quad·\\quad "
        + "Patrocinadora: Dra. Mariana Martínez Ávila \\\\[2pt]\n"
        + "  \\normalsize 13 de noviembre de 2026}\n"
        + "\\date{\\vspace{-2ex}}\n\n\\begin{document}\n\n\\maketitle\n\n"
        + f"\\begin{{abstract}}\n{resumen}\n\\end{{abstract}}\n\n{resto_tex}\n\n"
    )
    ia = (
        "\\section*{Declaración de uso de inteligencia artificial}\n"
        "Se utilizó \\textcite{anthropic2026claude} con los modelos Claude Opus~5 y Claude Sonnet~5.5, "
        "y Claude Sonnet~5 cuando las restricciones de seguridad del modelo en temas de biología y química "
        "impidieron usar el 5.5, "
        "para escribir el código de los experimentos y sus pruebas, "
        "generar con ese código las figuras a partir de las corridas registradas y redactar y dar formato al "
        "borrador de este artículo. "
        "Las preguntas, las reglas de decisión escritas antes de cada corrida, la interpretación de los "
        "resultados y las conclusiones son del equipo, que contrastó cada cifra con su corrida. "
        "La responsabilidad final sobre el contenido entregado recae en los autores.\n"
    )
    cierre = (
        "\n" + ia + "\n\\printbibliography[title={Referencias}]\n\n"
        "\\clearpage\n\\appendix\n" + anexos + "\n\\end{document}\n"
    )
    return encabezado + "\n".join(cuerpo) + cierre


def permitir_saltos(tex: str) -> str:
    """Un `\\texttt` largo (el nombre de una carpeta de corrida) no se parte y se sale del margen:
    se permite el salto de línea después de cada guion, barra o guion bajo."""
    def parte(m):
        return "\\texttt{" + re.sub(r"(-|/|\\_)", r"\1\\allowbreak{}", m.group(1)) + "}"
    return re.sub(r"\\texttt\{([^{}]{30,})\}", parte, tex)


def main() -> None:
    nuevo = permitir_saltos(construir())
    if "--revisar" in sys.argv:
        if not SALIDA.exists() or SALIDA.read_text(encoding="utf-8") != nuevo:
            sys.exit("articulo.tex no coincide con borrador.md: corre scripts/armar_articulo_tex.py")
        print("articulo.tex está al día")
        return
    SALIDA.write_text(nuevo, encoding="utf-8")
    print(f"escrito {SALIDA.relative_to(RAIZ)} ({len(nuevo.splitlines())} líneas)")


if __name__ == "__main__":
    main()
