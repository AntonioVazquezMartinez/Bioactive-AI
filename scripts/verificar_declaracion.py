#!/usr/bin/env python3
"""Comprueba que las libretas entregables cierren con la declaración de uso de IA.

Desde el Avance 4, el Proyecto Integrador exige una celda final con tres partes:
uso de IA con su cita en APA, contribución por integrante y las tres decisiones
que más pesaron, cada una con la alternativa descartada. No declararlo es una
falta de integridad académica, no un olvido de formato, y la rúbrica no da
puntos por ello: no hay ninguna señal que avise si falta.

Se revisan solo las libretas **entregables** desde la cuarta. Un sufijo de letra
—`01b`, `02b`— marca un análisis acompañante que no se entrega, y los Avances 1
a 3 se entregaron antes de que la regla existiera.

    python3 scripts/verificar_declaracion.py
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUADERNOS = RAIZ / "notebooks"
PRIMER_AVANCE_CON_REGLA = 4

# Lo que la plantilla de Canvas pide, en el orden en que lo pide.
PARTES = ("Uso de herramientas de IA", "Contribución individual", "Decisiones principales")


def entregables() -> list[Path]:
    """Las libretas con número de avance y sin sufijo de letra, desde la cuarta."""
    out = []
    for p in sorted(CUADERNOS.glob("*.ipynb")):
        m = re.match(r"^(\d+)_", p.name)
        if m and int(m.group(1)) >= PRIMER_AVANCE_CON_REGLA:
            out.append(p)
    return out


def texto_final(cuaderno: Path, celdas: int = 3) -> str:
    """Las últimas celdas de texto, que es donde la declaración tiene que ir."""
    nb = json.loads(cuaderno.read_text(encoding="utf-8"))
    markdown = [c for c in nb.get("cells", []) if c.get("cell_type") == "markdown"]
    return "\n".join("".join(c.get("source", [])) for c in markdown[-celdas:])


def main() -> int:
    libretas = entregables()
    if not libretas:
        print(f"todavía no hay libretas de avance {PRIMER_AVANCE_CON_REGLA} o posterior")
        return 0

    problemas = []
    for libreta in libretas:
        final = texto_final(libreta)
        faltan = [parte for parte in PARTES if parte.lower() not in final.lower()]
        if faltan:
            problemas.append(f"{libreta.name}: falta en la celda final {faltan}")
            continue
        if "Nombre Estudiante" in final:
            problemas.append(f"{libreta.name}: quedaron los nombres del ejemplo de Canvas")
        if "Borrar esta nota" in final:
            problemas.append(f"{libreta.name}: quedó la nota interna de la plantilla")
        print(f"{libreta.name}: declaración completa")

    if problemas:
        print(f"\n{len(problemas)} problemas:")
        for q in problemas:
            print("  ", q)
        return 1
    print("\nsin problemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
