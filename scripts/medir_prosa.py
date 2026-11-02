#!/usr/bin/env python3
"""Mide la prosa de los cuadernos: celdas sin título, párrafos y frases.

Existe porque el defecto que arregló el #205 no lo encontró ninguna
comprobación: **nadie medía**. La lectura de las cuatro figuras del 05b había
llegado a 11,119 caracteres en una sola celda, y el 05c pasó de 2,453 a 6,845
en un PR, porque rellenar un hueco cae siempre en la celda que ya era la mayor.
El #205 partió esas celdas, y entonces apareció el defecto siguiente: partió en
las entradillas en negrita **sin ascenderlas a título**, así que el 05 pasó de 2
a 7 celdas de markdown sin ningún encabezado y el 05c de 0 a 5. Dos ciclos del
mismo problema, los dos encontrados leyendo y no midiendo.

    python scripts/medir_prosa.py

Las tres medidas, y por qué cada una:

- **Celdas huérfanas**: una celda de markdown sin ningún encabezado no aparece
  en el índice del cuaderno, ni en el TOC del sitio, ni da corte al deck
  (`armar_deck.py` corta en cada encabezado). El lector pierde el hilo.
- **Párrafo**: es la unidad de escaneo, no la celda. Una celda de 2,000
  caracteres con cinco párrafos cortos se sigue; un párrafo de 2,000 no.
- **Frase**: 150 caracteres son unas 25 palabras, y a partir de ahí hay que
  releer para saber cuál era el sujeto.

**La prosa se mide sin los bloques de código cercado**, como pide el
`CLAUDE.md`: la celda de montaje del 05b tiene 14,909 caracteres de los que
13,694 son un módulo de `src/` mostrado a propósito y atado por
`tests/test_05b_codigo.py`. Contándolo, esa celda parece la peor del
repositorio y su prosa está muy por debajo del techo.

Las celdas con la etiqueta `sin-diapositiva` quedan fuera: son la declaración
de uso de IA, que sigue una plantilla de Canvas y no se redacta.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUADERNOS = RAIZ / "notebooks"

CERCADO = re.compile(r"```.*?```", re.S)
FIN_DE_FRASE = re.compile(r"(?<=[.:;?!])\s+")


def prosa(celda: dict) -> str:
    """El markdown de una celda sin sus bloques de código cercado."""
    return CERCADO.sub("", "".join(celda.get("source", [])))


def tiene_titulo(texto: str) -> bool:
    return any(linea.lstrip().startswith("#") for linea in texto.split("\n"))


def parrafos(texto: str):
    """Los bloques que se leen de corrido: ni títulos, ni tablas, ni sangrados.

    Un elemento de lista sí cuenta, porque se lee como un bloque: el término de
    HTS del glosario del 05b son 1,510 caracteres en un solo guion.
    """
    for bloque in texto.split("\n\n"):
        bloque = bloque.strip()
        if not bloque or bloque.startswith(("|", "#", "    ", "\t")):
            continue
        yield bloque


def frases(parrafo: str):
    for frase in FIN_DE_FRASE.split(parrafo):
        frase = frase.strip()
        if frase:
            yield frase


def medir(ruta: Path) -> dict:
    """Las tres medidas de un cuaderno, con dónde está cada peor caso."""
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    huerfanas, peor_parrafo, peor_frase = [], (0, None), (0, None)
    for i, celda in enumerate(nb.get("cells", [])):
        if celda.get("cell_type") != "markdown":
            continue
        if "sin-diapositiva" in celda.get("metadata", {}).get("tags", []):
            continue
        texto = prosa(celda)
        if not tiene_titulo(texto):
            huerfanas.append(i)
        for parrafo in parrafos(texto):
            if len(parrafo) > peor_parrafo[0]:
                peor_parrafo = (len(parrafo), i)
            for frase in frases(parrafo):
                if len(frase) > peor_frase[0]:
                    peor_frase = (len(frase), i)
    return {"huerfanas": huerfanas, "parrafo": peor_parrafo, "frase": peor_frase}


def main() -> None:
    print(f"{'cuaderno':<44}{'huérfanas':>10}{'párrafo máx':>13}{'frase máx':>11}")
    for ruta in sorted(CUADERNOS.glob("*.ipynb")):
        m = medir(ruta)
        hu = len(m["huerfanas"])
        marca = "" if not hu else f"  celdas {m['huerfanas']}"
        print(f"{ruta.name:<44}{hu:>10}{m['parrafo'][0]:>13,}{m['frase'][0]:>11,}{marca}")
    print("\nLa prosa se mide sin los bloques de código cercado.")


if __name__ == "__main__":
    sys.exit(main())
