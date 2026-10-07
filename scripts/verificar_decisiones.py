#!/usr/bin/env python3
"""Comprueba que el registro de decisiones y la consulta a la patrocinadora no se separen.

Son dos artefactos para dos lectores. El registro guarda el contexto, lo que se
descartó y la historia; la consulta es la vista filtrada de lo que necesita su
respuesta, escrita a mano porque la priorización es juicio y no se genera.

Lo único que vale la pena automatizar es la deriva: que no se agregue una
decisión que necesita a la patrocinadora sin que aparezca en la consulta.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "docs" / "decisiones.md"
CONSULTA = RAIZ / "docs" / "consulta-patrocinadora.md"


def decisiones(texto: str) -> list[dict]:
    """Cada sección `## N · Título {#dN}` con su estado y quién decide."""
    bloques = re.split(r"\n(?=## \d+ · )", texto)
    out = []
    for b in bloques:
        m = re.match(r"## (\d+) · (.+?) \{#d\d+\}", b)
        if not m:
            continue
        estado = re.search(r"\*\*Estado:\*\* *([^·\n]+)", b)
        # solo el `Decide:` de la línea de estado: el de la línea de Pregunta
        # repite el mismo valor y lo contaba dos veces
        linea = re.search(r"\*\*Estado:\*\*[^\n]*", b)
        decide = re.search(r"\*\*Decide:\*\* *([^·\n*]+)", linea.group(0)) if linea else None
        out.append({
            "n": int(m.group(1)),
            "titulo": m.group(2).strip(),
            "estado": (estado.group(1).strip().lower() if estado else ""),
            "decide": (decide.group(1).strip().lower() if decide else ""),
            "pregunta": "**Pregunta:**" in b,
        })
    return out


def main() -> int:
    if not REGISTRO.exists():
        sys.exit(f"no se encontró {REGISTRO.relative_to(RAIZ)}")
    ds = decisiones(REGISTRO.read_text(encoding="utf-8"))
    print(f"{len(ds)} decisiones en el registro")

    problemas = []
    for d in ds:
        if not d["estado"]:
            problemas.append(f"#{d['n']} «{d['titulo']}» no declara estado")
        if not d["decide"]:
            problemas.append(f"#{d['n']} «{d['titulo']}» no declara quién decide")
        # si la decide la patrocinadora, tiene que haber una pregunta que hacerle
        if d["decide"] not in ("equipo", "patrocinadora", "ambos"):
            problemas.append(f"#{d['n']} «{d['titulo']}» declara «{d['decide']}»; debe ser equipo, patrocinadora o ambos")
        if d["decide"] in ("patrocinadora", "ambos") and not d["pregunta"]:
            problemas.append(f"#{d['n']} «{d['titulo']}» la decide ella y no formula la pregunta")

    # la regla real: lo que tenga pregunta formulada va a la consulta, lo decida quien lo decida
    de_ella = [d for d in ds if d["pregunta"]]
    por_decisor = {k: sum(1 for d in ds if d["decide"] == k) for k in ("equipo", "patrocinadora", "ambos")}
    print(f"decide el equipo: {por_decisor['equipo']} · la patrocinadora: {por_decisor['patrocinadora']} · ambos: {por_decisor['ambos']}")
    print(f"{len(de_ella)} formulan una pregunta para ella y deben aparecer en la consulta")

    if CONSULTA.exists():
        texto = CONSULTA.read_text(encoding="utf-8")
        faltan = [d for d in de_ella if not re.search(rf"\[?#?{d['n']}\]?\b|decisi[óo]n {d['n']}\b", texto)]
        if faltan:
            problemas += [f"#{d['n']} «{d['titulo']}» necesita a la patrocinadora y no aparece en la consulta"
                          for d in faltan]
        else:
            print("la consulta cubre todas las que necesitan su respuesta")
    else:
        print(f"AVISO: no existe {CONSULTA.relative_to(RAIZ)}; solo se valida el registro")

    if problemas:
        print(f"\n{len(problemas)} problemas:")
        for p in problemas:
            print("  ", p)
        return 1
    print("\nsin problemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
