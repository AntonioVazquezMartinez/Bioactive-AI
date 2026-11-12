#!/usr/bin/env python3
"""Reparte `recursos/paleta.json` a los tres sitios que pintan algo.

**Por qué existe.** Los hex vivían duplicados en `animaciones/comun.py`,
`recursos/graficas.js`, `estilos.scss` y `estilos-slides.scss`, y tres se habían
desviado entre sí sin que nadie lo notara: el azul, el verde y el naranja. Lo
bastante parecidos para parecer un descuido y no una decisión. Con una fuente y
un reparto, desviarse deja de ser posible.

Genera dos archivos y deja el tercero en manos de quien lo lee:

- `recursos/paleta.js`   — lo carga `graficas.js` antes que nada.
- `_paleta.scss`         — lo importan `estilos.scss` y `estilos-slides.scss`.
- `animaciones/comun.py` lee el JSON directamente, porque Python puede.

    python scripts/paleta.py            # escribe
    python scripts/paleta.py --revisar  # falla si algo quedó desfasado

El modo `--revisar` es el que corre en CI: si alguien edita un hex a mano en
cualquiera de los destinos, la comprobación lo marca.
"""

import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
FUENTE = RAIZ / "recursos" / "paleta.json"
AVISO = "/* Generado por scripts/paleta.py desde recursos/paleta.json. No editar a mano. */"


def cargar() -> dict:
    return json.loads(FUENTE.read_text(encoding="utf-8"))


def _roles(p: dict) -> list[tuple[str, str, str]]:
    """(nombre, claro, oscuro) de cada rol, en orden estable."""
    salida = []
    for nombre in p["categoricos"]["_orden"]:
        d = p["categoricos"][nombre]
        salida.append((nombre, d["claro"], d["oscuro"]))
    for nombre, d in p["estado"].items():
        if not nombre.startswith("_"):
            salida.append((nombre, d["claro"], d["oscuro"]))
    for nombre, d in p["tintas"].items():
        if not nombre.startswith("_"):
            salida.append((nombre, d["claro"], d["oscuro"]))
    return salida


def js(p: dict) -> str:
    lineas = [
        "// " + AVISO.strip("/* ").strip(" */"),
        "//",
        "// `PALETA.oscuro` y `PALETA.claro` llevan los mismos roles. Las gráficas",
        "// eligen según el tema; el orden de `categoricos` es el de asignación y",
        "// no se cicla: una cuarta serie se pliega en «otros».",
        "window.PALETA = {",
        '  categoricos: ' + json.dumps(p["categoricos"]["_orden"]) + ",",
    ]
    for modo in ("claro", "oscuro"):
        lineas.append(f"  {modo}: {{")
        for nombre, claro, oscuro in _roles(p):
            lineas.append(f'    {nombre}: "{claro if modo == "claro" else oscuro}",')
        lineas.append("  },")
    lineas.append("};")
    return "\n".join(lineas) + "\n"


def scss(p: dict) -> str:
    lineas = [AVISO, "//", "// Un mapa por modo, y variables CSS para quien las prefiera."]
    for modo in ("claro", "oscuro"):
        lineas.append(f"$paleta-{modo}: (")
        for nombre, claro, oscuro in _roles(p):
            lineas.append(f'  "{nombre}": {claro if modo == "claro" else oscuro},')
        lineas.append(");")
    lineas.append("")
    lineas.append(":root {")
    for nombre, claro, _ in _roles(p):
        lineas.append(f"  --bio-{nombre}: {claro};")
    lineas.append("}")
    lineas.append("")
    lineas.append('@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {')
    for nombre, _, oscuro in _roles(p):
        lineas.append(f"  --bio-{nombre}: {oscuro};")
    lineas.append("} }")
    lineas.append('[data-theme="dark"] {')
    for nombre, _, oscuro in _roles(p):
        lineas.append(f"  --bio-{nombre}: {oscuro};")
    lineas.append("}")
    return "\n".join(lineas) + "\n"


DESTINOS = {
    RAIZ / "recursos" / "paleta.js": js,
    RAIZ / "_paleta.scss": scss,
}


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--revisar", action="store_true",
                     help="no escribe; falla si algún destino quedó desfasado")
    args = cli.parse_args()

    p = cargar()
    desfasados = []
    for ruta, generar in DESTINOS.items():
        nuevo = generar(p)
        viejo = ruta.read_text(encoding="utf-8") if ruta.exists() else None
        if args.revisar:
            if viejo != nuevo:
                desfasados.append(ruta.relative_to(RAIZ))
        elif viejo != nuevo:
            ruta.write_text(nuevo, encoding="utf-8")
            print(f"[escrito] {ruta.relative_to(RAIZ)}")
        else:
            print(f"[al día]  {ruta.relative_to(RAIZ)}")

    if desfasados:
        print("Desfasados respecto a recursos/paleta.json: "
              + ", ".join(str(d) for d in desfasados)
              + "\nCórrelo sin --revisar para regenerarlos.", file=sys.stderr)
        raise SystemExit(1)
    if args.revisar:
        print("la paleta está al día en todos los destinos")


if __name__ == "__main__":
    main()
