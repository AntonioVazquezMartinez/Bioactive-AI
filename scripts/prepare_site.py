#!/usr/bin/env python3
"""Prepara el contenido del sitio antes de que Quarto lo renderice.

Hace tres cosas sobre copias en contenido/, sin tocar los originales de docs/:

1. **Convierte las citas.** Los documentos usan claves BibTeX entre backticks
   (`meng2021b3db`) para leerse bien en GitHub. Quarto necesita `@clave` para
   producir citas reales con bibliografía al final.
2. **Agrega frontmatter YAML.** Sin él, Quarto renderiza el archivo completo
   como un bloque de código en vez de interpretarlo como Markdown.
3. **Reescribe los enlaces** .md e .ipynb a .html. La jerarquía de contenido/
   replica la de docs/, así que los enlaces relativos entre documentos siguen
   siendo válidos sin recalcular profundidades.

Lo ejecuta Quarto vía `pre-render`, pero hay que correrlo a mano la primera
vez: Quarto arma su lista de archivos antes del pre-render, así que el
directorio debe existir para que los detecte.
"""

import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BUILD = RAIZ / "contenido"
BIB = RAIZ / "docs" / "referencias" / "bibliografia.bib"

# (origen, destino relativo a contenido/, subtítulo)
DOCUMENTOS = [
    ("docs/planteamiento/marco-teorico.md",
     "planteamiento/marco-teorico.md",
     "Fundamentos biológicos y computacionales del proyecto"),
    ("docs/planteamiento/reunion-2026-09-22.md",
     "planteamiento/reunion-2026-09-22.md",
     "Notas de la primera reunión con los asesores"),
    ("docs/referencias/README.md",
     "referencias/index.md",
     "Siete ramas de investigación documental"),
    ("docs/referencias/01-representaciones-moleculares.md",
     "referencias/01-representaciones-moleculares.md",
     "De SMILES a una tabla de características"),
    ("docs/referencias/02-datasets-bbb.md",
     "referencias/02-datasets-bbb.md",
     "Qué datos usar para la etapa 1"),
    ("docs/referencias/03-explicabilidad.md",
     "referencias/03-explicabilidad.md",
     "Cómo justificar por qué el modelo predice lo que predice"),
    ("docs/referencias/04-datos-neuroactividad.md",
     "referencias/04-datos-neuroactividad.md",
     "Qué datos usar para la etapa 2"),
    ("docs/referencias/05-fuentes-de-datos.md",
     "referencias/05-fuentes-de-datos.md",
     "Verificación de bases de datos abiertas"),
    ("data/external/README.md",
     "datos.md",
     "Procedencia, licencias y advertencias de los datos descargados"),
]


def claves_bib() -> set[str]:
    if not BIB.exists():
        sys.exit(f"no se encontró la bibliografía: {BIB}")
    return set(re.findall(r"^@\w+\{([^,]+),", BIB.read_text(encoding="utf-8"), re.M))


def convertir_citas(texto: str, claves: set[str]) -> tuple[str, int]:
    """`clave` y `Cita: clave1, clave2` -> [@clave] / [@clave1; @clave2]."""
    n = 0

    def reemplazo(m: re.Match) -> str:
        nonlocal n
        contenido = m.group(1)
        prefijo = re.match(r"^Citas?:\s*", contenido)
        if prefijo:
            contenido = contenido[prefijo.end():]
        partes = [p.strip() for p in contenido.split(",")]
        if not partes or not all(p in claves for p in partes):
            return m.group(0)
        n += len(partes)
        return "[" + "; ".join("@" + p for p in partes) + "]"

    salida, en_bloque = [], False
    for linea in texto.split("\n"):
        if linea.lstrip().startswith("```"):
            en_bloque = not en_bloque
            salida.append(linea)
            continue
        salida.append(linea if en_bloque else re.sub(
            r"`((?:Citas?:\s*)?[A-Za-z][\w]*(?:\s*,\s*[A-Za-z][\w]*)*)`", reemplazo, linea))
    return "\n".join(salida), n


def reescribir_enlaces(texto: str, profundidad: int) -> str:
    """.md e .ipynb -> .html.

    Hay dos raíces distintas: la del sitio (donde vive bibliografia.html) y la de
    contenido/ (donde viven los documentos y los notebooks). Confundirlas rompe
    los enlaces, así que se calculan por separado.
    """
    subir = "../" * profundidad              # hasta la raíz del sitio
    subir_c = "../" * (profundidad - 1)      # hasta la raíz de contenido/

    # la bibliografía .bib se publica como bibliografia.html en la raíz
    texto = re.sub(r"\]\((?:\.\./)*(?:docs/referencias/)?bibliografia\.bib\)",
                   f"]({subir}bibliografia.html)", texto)
    # los notebooks quedan en contenido/notebooks/
    texto = re.sub(r"\]\((?:\.\./)*notebooks/([\w.]+)\.ipynb\)",
                   rf"]({subir_c}notebooks/\1.html)", texto)
    # README.md de referencias -> index.html
    texto = re.sub(r"\]\(((?:\.\./)*)referencias/README\.md\)", r"](\1referencias/index.html)", texto)
    texto = re.sub(r"\]\(README\.md\)", "](index.html)", texto)
    # cualquier otro .md del proyecto -> .html
    texto = re.sub(r"\]\(((?:\.\./)*(?:docs/)?[\w/-]+)\.md\)", r"](\1.html)", texto)
    # docs/ se aplana en contenido/, no en la raíz del sitio
    texto = texto.replace("](../../docs/", f"]({subir_c}")
    texto = texto.replace("](docs/", f"]({subir_c}")
    return texto


def frontmatter(titulo: str, subtitulo: str | None) -> str:
    lineas = ["---", f'title: "{titulo}"']
    if subtitulo:
        lineas.append(f'subtitle: "{subtitulo}"')
    lineas += ["---", ""]
    return "\n".join(lineas)


def main() -> int:
    claves = claves_bib()
    print(f"[sitio] {len(claves)} claves en la bibliografía")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    total = 0
    for origen, destino, subtitulo in DOCUMENTOS:
        src = RAIZ / origen
        if not src.exists():
            print(f"[sitio] AVISO: no existe {origen}, se omite")
            continue

        texto = src.read_text(encoding="utf-8")

        # el título sale del primer H1, que se retira para no duplicarlo
        m = re.match(r"^#\s+(.+?)\s*\n", texto)
        titulo = m.group(1) if m else Path(destino).stem.replace("-", " ").capitalize()
        if m:
            texto = texto[m.end():].lstrip("\n")

        texto, n = convertir_citas(texto, claves)
        texto = reescribir_enlaces(texto, profundidad=len(Path(destino).parts))

        dst = BUILD / destino
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(frontmatter(titulo, subtitulo) + texto, encoding="utf-8")
        total += n
        print(f"[sitio] {origen} -> contenido/{destino}  ({n} citas)")

    # los notebooks se copian reescribiendo los enlaces de sus celdas markdown
    import json
    for nb_rel in ["notebooks/01_EDA.ipynb", "notebooks/02_Feature_Eng.ipynb"]:
        src = RAIZ / nb_rel
        if not src.exists():
            print(f"[sitio] AVISO: no existe {nb_rel}, se omite")
            continue
        nb = json.loads(src.read_text(encoding="utf-8"))
        cambios = 0
        for celda in nb.get("cells", []):
            if celda.get("cell_type") != "markdown":
                continue
            original = "".join(celda["source"])
            # desde contenido/notebooks/ hay que subir un nivel para llegar a la raíz
            nuevo = re.sub(r"\]\((?:\.\./)*docs/([\w/-]+)\.md\)", r"](../\1.html)", original)
            nuevo = re.sub(r"\]\(((?:\.\./)*)referencias/README\.md\)", r"](\1referencias/index.html)", nuevo)
            if nuevo != original:
                celda["source"] = [l + "\n" for l in nuevo.split("\n")[:-1]] + [nuevo.split("\n")[-1]]
                cambios += 1
        dst = BUILD / "notebooks" / Path(nb_rel).name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
        print(f"[sitio] {nb_rel} -> contenido/notebooks/{Path(nb_rel).name}  ({cambios} celdas con enlaces reescritos)")

    print(f"[sitio] {total} citas convertidas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
