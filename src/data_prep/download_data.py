#!/usr/bin/env python3
"""Descarga los datasets públicos del proyecto a data/external/.

Uso:
    python src/data_prep/download_data.py           # solo los archivos ligeros
    python src/data_prep/download_data.py --extended # incluye los .tsv.gz pesados (~77 MB)

Los archivos ligeros ya están versionados en el repo; este script sirve para
reproducir la descarga desde cero y para traer los pesados, que están en
.gitignore. Las fuentes, licencias y advertencias están en data/external/README.md.
"""

import argparse
import hashlib
import io
import sys
import tarfile
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "data" / "external"

# Commit fijado de B3DB. Anclarlo importa: el repo sigue recibiendo compuestos
# nuevos y el conteo cambia entre versiones.
B3DB_COMMIT = "75dab1cc607bb7a03f3de5c576cffd223e767844"
B3DB_TAR = f"https://github.com/theochem/B3DB/archive/{B3DB_COMMIT}.tar.gz"

B3DB_LIGEROS = [
    "B3DB/B3DB_classification.tsv",
    "B3DB/B3DB_classification_external.tsv",
    "B3DB/B3DB_regression.tsv",
]
B3DB_PESADOS = [
    "B3DB/B3DB_classification_extended.tsv.gz",
    "B3DB/B3DB_regression_extended.tsv.gz",
]

SPIELVOGEL_URL = "https://osf.io/download/bfxdp/"
SPIELVOGEL_DEST = "spielvogel2025/bbb_penetration_database.csv"


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def descargar_b3db(incluir_pesados: bool) -> list[Path]:
    queridos = B3DB_LIGEROS + (B3DB_PESADOS if incluir_pesados else [])
    print(f"B3DB, commit {B3DB_COMMIT[:12]} ...")
    with urllib.request.urlopen(B3DB_TAR) as r:
        datos = r.read()

    escritos = []
    with tarfile.open(fileobj=io.BytesIO(datos), mode="r:gz") as tar:
        for miembro in tar.getmembers():
            # el tarball trae un directorio raíz con el hash: B3DB-<sha>/...
            relativo = "/".join(miembro.name.split("/")[1:])
            if relativo not in queridos:
                continue
            salida = DESTINO / "b3db" / Path(relativo).name
            salida.parent.mkdir(parents=True, exist_ok=True)
            extraido = tar.extractfile(miembro)
            if extraido is None:
                continue
            salida.write_bytes(extraido.read())
            escritos.append(salida)
            print(f"  {salida.relative_to(RAIZ)}  ({salida.stat().st_size:,} bytes)")
    return escritos


def descargar_spielvogel() -> Path:
    print("Spielvogel et al. 2025 (OSF cvhe9) ...")
    salida = DESTINO / SPIELVOGEL_DEST
    salida.parent.mkdir(parents=True, exist_ok=True)
    peticion = urllib.request.Request(SPIELVOGEL_URL, headers={"User-Agent": "bioactive-ai"})
    with urllib.request.urlopen(peticion) as r:
        salida.write_bytes(r.read())
    print(f"  {salida.relative_to(RAIZ)}  ({salida.stat().st_size:,} bytes)")
    return salida


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--extended", action="store_true",
                   help="incluye los .tsv.gz de B3DB con descriptores mordred precalculados (~77 MB)")
    args = p.parse_args()

    DESTINO.mkdir(parents=True, exist_ok=True)
    escritos = descargar_b3db(args.extended)
    escritos.append(descargar_spielvogel())

    print("\nSHA-256:")
    for ruta in escritos:
        print(f"  {sha256(ruta)}  {ruta.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
