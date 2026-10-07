#!/usr/bin/env python3
"""Comprueba que ningún enlace interno del sitio construido esté roto.

Vive aquí y no dentro del workflow por dos razones: se puede correr en local
antes de subir, y el YAML no es sitio para lógica que conviene leer.

Revisa **todos** los enlaces internos, no solo los `.html`. La versión anterior,
embebida en el workflow, solo miraba `.html` y dejaba ciegos 159 de 788 enlaces
— entre ellos los PDF de los reportes, que es justo lo que la página de
entregables ofrece descargar.
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


def enlaces(html: str) -> set[str]:
    """Los href y src del documento, sin ancla ni cadena de consulta.

    Se decodifica el porcentaje —`%20` y compañía— porque en disco el archivo
    lleva el espacio literal, y un enlace sin decodificar daría falso positivo.
    """
    crudos = re.findall(r'(?:href|src)="([^"]+)"', html)
    return {unquote(h.split("#")[0].split("?")[0]) for h in crudos
            if h and not h.startswith(EXTERNOS)}


def main() -> int:
    if not SITIO.exists():
        sys.exit(f"no existe {SITIO.relative_to(RAIZ)}: hay que correr `quarto render` primero")

    paginas = sorted(glob.glob(str(SITIO / "**" / "*.html"), recursive=True))
    rotos, revisados = [], 0
    for f in paginas:
        base = os.path.dirname(f)
        for destino in enlaces(open(f, encoding="utf-8").read()):
            revisados += 1
            # una ruta absoluta es relativa a la raíz del sitio, no del sistema:
            # os.path.join descartaría la base y daría un falso positivo
            raiz = SITIO if destino.startswith("/") else base
            ruta = os.path.normpath(os.path.join(raiz, destino.lstrip("/")))
            if not os.path.exists(ruta):
                rotos.append(f"{os.path.relpath(f, SITIO)} -> {destino}")

    print(f"{len(paginas)} páginas · {revisados} enlaces internos revisados")
    if rotos:
        print(f"\n{len(set(rotos))} rotos:")
        for r in sorted(set(rotos)):
            print("  ", r)
        return 1
    print("todos resuelven")
    return 0


if __name__ == "__main__":
    sys.exit(main())
