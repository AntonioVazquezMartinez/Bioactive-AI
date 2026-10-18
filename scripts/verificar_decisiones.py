#!/usr/bin/env python3
"""Comprueba que cada entrada de la bitácora de decisiones declare su estado.

Las entradas son los encabezados `#### 1.2 · Título {#d1-2 .vigente}`. Una
decisión vigente puede traer una **Pregunta:** de confirmación; lo que no puede
es estar ratificada y seguir con una pregunta pendiente.

Comprueba además dos cosas que ya fallaron en silencio:

- **Que la clase del encabezado diga lo mismo que la línea «Estado:».** Es lo
  que colorea la entrada en el sitio, así que una entrada puede leerse
  «vigente» y pintarse como propuesta pendiente de definición. Pasó con la 2.2
  y la 2.3 en el #86.
- **Que ningún identificador se repita.** Dos entradas con `{#s1-10}` publican
  un ancla duplicada y los enlaces van a la primera. Pasó con la S1.10 en
  el #83.
"""

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
REGISTRO = RAIZ / "docs" / "decisiones.md"
ESTADOS = ("vigente", "revisada", "propuesta", "abierta", "ratificada")


def entradas(texto: str) -> list[dict]:
    """Cada sección `#### N · Título {#dN}` con su estado y si trae pregunta."""
    out = []
    for b in re.split(r"\n(?=#{2,4} )", texto):
        m = re.match(r"#{3,4} ([C\d]\.\d+) · (.+?) \{(#d[c\d]-\d+)([^}]*)\}", b)
        if not m:
            continue
        estado = re.search(r"\*\*Estado:\*\* *([^·\n]+)", b)
        out.append({
            "n": m.group(1),
            "titulo": m.group(2).strip(),
            "id": m.group(3),
            "clases": {c.lstrip(".").lower() for c in m.group(4).split()},
            "estado": estado.group(1).strip().lower() if estado else "",
            "pregunta": "**Pregunta:**" in b,
        })
    return out


def main() -> int:
    if not REGISTRO.exists():
        sys.exit(f"no se encontró {REGISTRO.relative_to(RAIZ)}")
    es = entradas(REGISTRO.read_text(encoding="utf-8"))
    print(f"{len(es)} entradas en la bitácora")

    problemas = []
    for e in es:
        if not e["estado"]:
            problemas.append(f"{e['n']} «{e['titulo']}» no declara estado")
        elif e["estado"] not in ESTADOS:
            problemas.append(f"{e['n']} «{e['titulo']}» declara «{e['estado']}»; debe ser uno de {', '.join(ESTADOS)}")
        elif e["pregunta"] and e["estado"] == "ratificada":
            problemas.append(f"{e['n']} «{e['titulo']}» está ratificada y aún trae una pregunta")
        if e["estado"] in ESTADOS and e["estado"] not in e["clases"]:
            problemas.append(
                f"{e['n']} «{e['titulo']}» dice «{e['estado']}» pero su encabezado"
                f" lleva {sorted(e['clases']) or 'ninguna clase'}: el sitio la"
                " pinta con la clase, no con la línea de estado")

    # Identificadores repetidos, aquí y en los supuestos `{#s1-10}` del mismo archivo.
    todos = re.findall(r"^#{3,4} .+? \{(#[\w-]+)", REGISTRO.read_text(encoding="utf-8"),
                       flags=re.MULTILINE)
    for ident in sorted({i for i in todos if todos.count(i) > 1}):
        problemas.append(f"el identificador {{{ident}}} está en {todos.count(ident)}"
                         " encabezados: el ancla publicada apunta solo al primero")

    print(f"{sum(e['pregunta'] for e in es)} traen una pregunta pendiente")
    if problemas:
        print(f"\n{len(problemas)} problemas:")
        for q in problemas:
            print("  ", q)
        return 1
    print("\nsin problemas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
