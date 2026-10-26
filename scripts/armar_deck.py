#!/usr/bin/env python3
"""Arma una presentación a partir de un notebook, **sin modificar el notebook**.

`nbconvert --to slides` necesita `slideshow.slide_type` en cada celda para saber
dónde cortar. Ninguno de nuestros notebooks lo trae, así que convertido tal cual
el 03 produce **una sola diapositiva** con sus 27 celdas encima. Marcarlas a
mano dentro del `.ipynb` arreglaría eso y traería dos problemas peores: el
notebook es el entregable y su diff se llenaría de metadatos de presentación, y
cualquier reejecución o celda nueva dejaría el marcado desfasado en silencio.

Así que el marcado se hace sobre una **copia derivada** y el notebook queda byte
por byte igual. El corte sale de lo que el notebook ya dice:

- un encabezado `##` abre diapositiva y un `###` abre subdiapositiva;
- una celda de código sin salida visible se salta, porque no tiene nada que
  mostrar cuando el código va oculto;
- una celda con la etiqueta `sin-diapositiva` se salta siempre —es para lo que
  pertenece al entregable pero no a la exposición, como la declaración de uso
  de IA.

**Y parte las diapositivas que no caben.** El presupuesto no es inventado: sale
de medir `presentacion.qmd`, la presentación que el equipo ya da por buena, que
corre con una mediana de 873 caracteres por diapositiva y un techo de 1,761. Lo
que pase el techo se corta en el límite de párrafo más cercano y arrastra su
encabezado con «(sigue)», porque una diapositiva sin título no se entiende
cuando alguien la proyecta.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Medidos sobre presentacion.qmd: mediana 873, máxima 1,761. El techo es el
# máximo que el equipo ya proyectó, no una estimación de lo que cabe.
TECHO = 1761
OBJETIVO = 900

# Los notebooks de los que se presenta algo, y por tanto los que la prueba
# vigila. No están los anteriores porque sus diapositivas que pasan el techo
# son **salidas impresas**, no prosa: una tabla de 5,380 caracteres en el 02 y
# tres de más de 2,400 en el 01. Partir por párrafo no las arregla —habría que
# bajarles la letra o quitarles columnas, que es decisión de cada tabla— y
# nadie expone el EDA, así que meterlas aquí sería dejar la prueba roja desde
# el primer día. Agrega un notebook a esta lista cuando vayas a presentarlo.
CON_DECK = ("03_Baseline", "04_Models")


def _texto(celda: dict) -> str:
    """Lo que esa celda va a ocupar en pantalla, con el código ya oculto."""
    if celda["cell_type"] == "markdown":
        return "".join(celda["source"])
    visto = ""
    for salida in celda.get("outputs", []):
        datos = salida.get("data", {})
        if "image/png" in datos:
            # Una figura ocupa alto, no caracteres. Se cuenta como media
            # diapositiva para que no se le apile un párrafo al lado.
            visto += " " * (OBJETIVO // 2)
        visto += "".join(salida.get("text", "")) or str(datos.get("text/plain", ""))
    return visto


def _encabezado(fuente: str) -> tuple[int, str] | None:
    m = re.match(r"^(#+)\s+(.*)", fuente)
    return (len(m.group(1)), m.group(2).strip()) if m else None


def _secciones(fuente: str) -> list[str]:
    """Corta en cada encabezado, porque una celda puede traer varios.

    La primera celda del 03 trae el título y **dos** encabezados `##` dentro de
    sus 2,101 caracteres. Mirando solo la primera línea, esa celda era una sola
    diapositiva y los dos apartados terminaban arrastrados detrás del título.
    """
    partes, actual = [], []
    for linea in fuente.splitlines(keepends=True):
        if re.match(r"^#{1,3}\s", linea) and actual and "".join(actual).strip():
            partes.append("".join(actual))
            actual = []
        actual.append(linea)
    if actual:
        partes.append("".join(actual))
    return [p for p in partes if p.strip()]


def _partir(celda: dict) -> list[dict]:
    """Parte una celda de markdown en el límite de párrafo, si no cabe."""
    fuente = "".join(celda["source"])
    secciones = _secciones(fuente)
    if len(secciones) > 1:
        trozos = []
        for seccion in secciones:
            sub = copy.deepcopy(celda)
            sub["source"] = seccion.splitlines(keepends=True)
            sub.pop("id", None)
            trozos.extend(_partir(sub))
        return trozos
    if len(fuente) <= TECHO:
        return [celda]

    enc = _encabezado(fuente)
    parrafos = []
    for bloque in fuente.split("\n\n"):
        if not bloque.strip():
            continue
        # Una lista no lleva línea en blanco entre sus puntos, así que es un
        # solo párrafo y el corte por párrafo no la toca: el cierre del 03 son
        # cinco numerados seguidos, 2,024 caracteres en un bloque. Cuando un
        # bloque así no cabe, se parte en el límite de punto, que es donde un
        # lector ya esperaba una pausa.
        puntos = re.split(r"\n(?=\s*(?:[-*+]|\d+\.)\s)", bloque)
        parrafos.extend(puntos if len(bloque) > OBJETIVO and len(puntos) > 1
                        else [bloque])
    trozos: list[list[str]] = [[]]
    for p in parrafos:
        actual = sum(len(x) + 2 for x in trozos[-1])
        # Un párrafo entra si la diapositiva sigue por debajo del objetivo; el
        # techo se respeta aunque un párrafo suelto lo pase, porque partir
        # dentro de un párrafo deja una frase huérfana.
        if trozos[-1] and actual + len(p) > OBJETIVO:
            trozos.append([p])
        else:
            trozos[-1].append(p)

    celdas = []
    for i, trozo in enumerate(trozos):
        cuerpo = "\n\n".join(trozo)
        if i and enc:
            nivel, titulo = enc
            cuerpo = f"{'#' * nivel} {titulo} (sigue)\n\n{cuerpo}"
        nueva = copy.deepcopy(celda)
        nueva["source"] = cuerpo.splitlines(keepends=True)
        nueva.pop("id", None)
        celdas.append(nueva)
    return celdas


def marcar(nb: dict) -> tuple[dict, dict[str, int]]:
    """Devuelve una copia marcada y la cuenta por tipo. No toca la entrada."""
    nb = copy.deepcopy(nb)
    salida, cuenta = [], {}
    primera = True
    for celda in nb["cells"]:
        etiquetas = celda.get("metadata", {}).get("tags", [])
        if "sin-diapositiva" in etiquetas:
            tipo = "skip"
            trozos = [celda]
        elif celda["cell_type"] == "markdown":
            trozos = _partir(celda)
            enc = _encabezado("".join(celda["source"]))
            if enc:
                tipo = "slide" if enc[0] <= 2 else "subslide"
            else:
                tipo = "slide" if primera else "fragment"
        else:
            trozos = [celda]
            # La salida se queda **con la prosa que la presenta**: el 03 tiene
            # celdas que terminan en dos puntos y la tabla venía detrás, en
            # otra diapositiva, dejando los dos puntos apuntando a nada. Si no
            # cabe, la pasada de abajo la asciende a subdiapositiva.
            tipo = "fragment" if _texto(celda).strip() else "skip"

        for i, trozo in enumerate(trozos):
            # Un trozo partido abre su propia diapositiva, nunca un fragmento.
            # Si trae encabezado propio, manda su nivel: un `##` que venía
            # dentro de otra celda sigue siendo un apartado, no una continuación.
            propio = _encabezado("".join(trozo["source"])) if trozo["cell_type"] == "markdown" else None
            if i == 0:
                suyo = tipo
            elif propio:
                suyo = "slide" if propio[0] <= 2 else "subslide"
            else:
                suyo = "subslide" if tipo != "slide" else "slide"
            trozo.setdefault("metadata", {})["slideshow"] = {"slide_type": suyo}
            cuenta[suyo] = cuenta.get(suyo, 0) + 1
            salida.append(trozo)
        primera = False

    # Partir celda por celda no basta: una diapositiva es la celda que la abre
    # **más sus fragmentos**, así que tres celdas cortas seguidas rebasan el
    # techo sin que ninguna lo rebase por su cuenta. Esta pasada asciende el
    # fragmento que no cabe a subdiapositiva, que es el corte más barato: no
    # reordena nada y deja la prosa intacta.
    acumulado = 0
    for celda in salida:
        marca = celda["metadata"]["slideshow"]
        largo = len(_texto(celda))
        if marca["slide_type"] == "skip":
            continue
        if marca["slide_type"] == "fragment" and acumulado + largo > TECHO:
            cuenta["fragment"] -= 1
            marca["slide_type"] = "subslide"
            cuenta["subslide"] = cuenta.get("subslide", 0) + 1
        if marca["slide_type"] in ("slide", "subslide"):
            acumulado = largo
        else:
            acumulado += largo

    nb["cells"] = salida
    return nb, cuenta


def diapositivas(nb: dict) -> list[str]:
    """El texto de cada diapositiva de un notebook ya marcado."""
    acumulado: list[str] = []
    for celda in nb["cells"]:
        tipo = celda["metadata"]["slideshow"]["slide_type"]
        if tipo == "skip":
            continue
        if tipo in ("slide", "subslide") or not acumulado:
            acumulado.append(_texto(celda))
        else:
            acumulado[-1] += _texto(celda)
    return acumulado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("notebook", type=Path)
    p.add_argument("--salida", type=Path, default=RAIZ / "_decks")
    p.add_argument("--solo-medir", action="store_true",
                   help="Imprime el reparto sin llamar a nbconvert.")
    args = p.parse_args()

    origen = args.notebook if args.notebook.is_absolute() else RAIZ / args.notebook
    nb = json.loads(origen.read_text())
    marcado, cuenta = marcar(nb)
    largos = [len(d) for d in diapositivas(marcado)]

    print(f"{origen.name}: {len(largos)} diapositivas · "
          f"mediana {sorted(largos)[len(largos) // 2]} caracteres")
    print("  reparto:", " · ".join(f"{k}: {v}" for k, v in sorted(cuenta.items())))
    exceden = [x for x in largos if x > TECHO]
    if exceden:
        print(f"  ⚠ {len(exceden)} por encima del techo de {TECHO}: "
              f"{sorted(exceden, reverse=True)}")
    if args.solo_medir:
        return 0

    args.salida.mkdir(parents=True, exist_ok=True)
    intermedio = args.salida / f"_{origen.stem}.marcado.ipynb"
    intermedio.write_text(json.dumps(marcado, ensure_ascii=False, indent=1))
    orden = [sys.executable, "-m", "jupyter", "nbconvert", "--to", "slides",
             "--no-input", "--output-dir", str(args.salida),
             "--output", origen.stem, str(intermedio)]
    hecho = subprocess.run(orden, capture_output=True, text=True)
    intermedio.unlink()
    if hecho.returncode:
        print(hecho.stderr, file=sys.stderr)
        return hecho.returncode
    print(f"  → {args.salida / (origen.stem + '.slides.html')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
