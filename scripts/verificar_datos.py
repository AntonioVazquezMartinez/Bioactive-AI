#!/usr/bin/env python3
"""Comprueba que los datos versionados no hayan cambiado, contra `data/MANIFEST.json`.

Fase 0.5 de `docs/roadmap-mlops.md`. El manifiesto guarda el `sha256` y el tamaño de cada
archivo de `data/` que git sigue (menos `.gitkeep` y los `.md`). Falla si un archivo cambió,
falta o apareció uno sin registrar.

    python3 scripts/verificar_datos.py             # comprobar
    python3 scripts/verificar_datos.py --escribir  # regenerar tras un cambio de datos deliberado

Un cambio de datos deliberado es una decisión: regenerar el manifiesto va en el mismo PR que
explica por qué cambió el archivo. El archivo de actividad va por Git LFS; si el árbol trae
solo el puntero (como en el CI, que no baja LFS), su huella es el `oid` del puntero, que es
el `sha256` del contenido real.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "data" / "MANIFEST.json"
PUNTERO = re.compile(rb"^version https://git-lfs\.github\.com/spec/v1\noid sha256:([0-9a-f]{64})\nsize (\d+)\n$")


def archivos(raiz: Path = RAIZ) -> list[str]:
    """Rutas (relativas a la raíz) de los datos que git sigue, ordenadas."""
    salida = subprocess.run(["git", "ls-files", "data"], cwd=raiz, capture_output=True,
                            text=True, check=True).stdout.split("\n")
    return sorted(r for r in salida
                  if r and not r.endswith((".md", ".gitkeep", "MANIFEST.json")))


def huella(ruta: Path) -> dict:
    """`sha256` y tamaño del contenido; si es un puntero LFS, los del archivo real."""
    if ruta.stat().st_size < 200:
        m = PUNTERO.match(ruta.read_bytes())
        if m:
            return {"sha256": m.group(1).decode(), "bytes": int(m.group(2))}
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return {"sha256": h.hexdigest(), "bytes": ruta.stat().st_size}


def calcular(raiz: Path = RAIZ, rutas: list[str] | None = None) -> dict:
    return {r: huella(raiz / r) for r in (archivos(raiz) if rutas is None else rutas)}


def comparar(esperado: dict, actual: dict) -> list[str]:
    """Una frase por cada diferencia entre el manifiesto y los archivos."""
    problemas = [f"cambió: {r}" for r in sorted(esperado.keys() & actual.keys())
                 if esperado[r] != actual[r]]
    problemas += [f"falta: {r}" for r in sorted(esperado.keys() - actual.keys())]
    problemas += [f"sin registrar: {r}" for r in sorted(actual.keys() - esperado.keys())]
    return problemas


def main() -> int:
    actual = calcular()
    if "--escribir" in sys.argv:
        MANIFIESTO.write_text(json.dumps(actual, indent=2, sort_keys=True) + "\n")
        print(f"escrito {MANIFIESTO.relative_to(RAIZ)} ({len(actual)} archivos)")
        return 0
    problemas = comparar(json.loads(MANIFIESTO.read_text()), actual)
    for p in problemas:
        print(p)
    if problemas:
        print("Si el cambio es deliberado: python3 scripts/verificar_datos.py --escribir "
              "y explícalo en el PR.")
        return 1
    print(f"{len(actual)} archivos de datos coinciden con el manifiesto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
