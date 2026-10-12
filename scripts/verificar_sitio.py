#!/usr/bin/env python3
"""Comprueba que ningún enlace interno del sitio construido esté roto.

Vive aquí y no dentro del workflow por dos razones: se puede correr en local
antes de subir, y el YAML no es sitio para lógica que conviene leer.

Revisa **todos** los enlaces internos, no solo los `.html`. La versión anterior,
embebida en el workflow, solo miraba `.html` y dejaba ciegos 159 de 788 enlaces
— entre ellos los PDF de los reportes, que es justo lo que la página de
entregables ofrece descargar.

Y revisa el **fragmento**, el `#ancla`, no solo el archivo. Mientras no lo hacía,
un enlace a una sección renombrada pasaba en verde: el índice de la guía del
proyecto apuntó durante un PR entero a `#5-decisiones-técnicas-ya-tomadas-y-por-qué`
después de que el encabezado pasara a `## 5. Decisiones técnicas`, y ninguna
verificación lo vio. Es el caso que justifica esta mitad del script.
"""

import glob
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]
SITIO = RAIZ / "_site"

EXTERNOS = ("http://", "https://", "//", "mailto:", "tel:", "javascript:", "data:", "#")


def crudos(html: str) -> list[str]:
    """Los href y src internos del documento, tal como están escritos."""
    return [h for h in re.findall(r'(?:href|src)="([^"]+)"', html)
            if h and not h.startswith(EXTERNOS[:-1])]


def enlaces(html: str) -> set[str]:
    """Los destinos del documento, sin ancla ni cadena de consulta.

    Se decodifica el porcentaje —`%20` y compañía— porque en disco el archivo
    lleva el espacio literal, y un enlace sin decodificar daría falso positivo.
    """
    return {unquote(h.split("#")[0].split("?")[0]) for h in crudos(html)
            if not h.startswith("#")}


def anclas(html: str) -> set[str]:
    """Los identificadores de la página a los que un fragmento puede apuntar.

    Son los `id` de cualquier etiqueta más los `name` de los anclajes antiguos.
    Quarto genera el `id` de cada encabezado, así que un `#ancla` roto es un
    enlace a una sección que se renombró o se borró.
    """
    return (set(unquote(i) for i in re.findall(r'\sid="([^"#]+)"', html))
            | set(unquote(i) for i in re.findall(r'<a\b[^>]*\sname="([^"#]+)"', html)))


def main() -> int:
    if not SITIO.exists():
        sys.exit(f"no existe {SITIO.relative_to(RAIZ)}: hay que correr `quarto render` primero")

    paginas = sorted(glob.glob(str(SITIO / "**" / "*.html"), recursive=True))
    html = {f: open(f, encoding="utf-8").read() for f in paginas}
    propias = {f: anclas(t) for f, t in html.items()}

    def resolver(base: str, destino: str) -> str:
        # una ruta absoluta es relativa a la raíz del sitio, no del sistema:
        # os.path.join descartaría la base y daría un falso positivo
        raiz = SITIO if destino.startswith("/") else base
        ruta = os.path.normpath(os.path.join(raiz, destino.lstrip("/")))
        # un enlace a un directorio sirve su index.html, y es ahí donde está el
        # ancla: sin esto los fragmentos de `../reportes/` no se comprobaban
        indice = os.path.join(ruta, "index.html")
        return indice if os.path.isdir(ruta) and os.path.exists(indice) else ruta

    rotos, sin_ancla, revisados, fragmentos = [], [], 0, 0
    for f in paginas:
        base = os.path.dirname(f)
        for destino in enlaces(html[f]):
            revisados += 1
            if not os.path.exists(resolver(base, destino)):
                rotos.append(f"{os.path.relpath(f, SITIO)} -> {destino}")

        for h in crudos(html[f]):
            archivo, _, frag = h.partition("#")
            frag = unquote(frag.split("?")[0])
            if not frag:
                continue
            # un fragmento sobre un PDF u otro formato no es un ancla de HTML
            destino = f if not archivo else resolver(base, unquote(archivo.split("?")[0]))
            if destino not in propias:
                continue
            fragmentos += 1
            if frag not in propias[destino]:
                rotos.append(f"{os.path.relpath(f, SITIO)} -> {h}")
                sin_ancla.append(h)

    print(f"{len(paginas)} páginas · {revisados} enlaces internos "
          f"y {fragmentos} anclas revisadas")
    if rotos:
        print(f"\n{len(set(rotos))} rotos:")
        for r in sorted(set(rotos)):
            print("  ", r)
        if sin_ancla:
            print("\nlos que fallan por el fragmento apuntan a una sección que ya no existe:"
                  " hay que actualizar el enlace o devolverle el ancla al encabezado")
        return 1
    print("todos resuelven")
    return 0


if __name__ == "__main__":
    sys.exit(main())
