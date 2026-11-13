#!/usr/bin/env python3
"""Exporta la presentación final a PDF: una página por diapositiva, para leerla o proyectarla sin navegador.

Se hace con una captura de cada diapositiva porque el PDF nativo de reveal no sale bien en Chrome sin pantalla. El PDF lleva
en sus metadatos (`Subject`) la **huella del mazo**: el sha256 de `presentacion-final.qmd` y de cada imagen que usa.
`tests/test_pdf_del_mazo.py` la recalcula y falla si el PDF se quedó atrás, sin depender del historial de git.

    ./env312/bin/python scripts/exportar_mazo_pdf.py

Necesita `quarto` en el PATH y Chrome (la ruta se cambia con la variable `CHROME`).
"""
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MAZO = RAIZ / "presentacion-final.qmd"
SALIDA = RAIZ / "docs" / "reportes" / "presentacion" / "presentacion-final.pdf"
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PREFIJO = "huella:"


def huella() -> str:
    """sha256 del mazo y de cada imagen local que usa, en orden de ruta."""
    texto = MAZO.read_text(encoding="utf-8")
    h = hashlib.sha256(texto.encode("utf-8"))
    rutas = sorted({m.group(1) for m in re.finditer(r"!\[[^\]]*\]\(([^)\s]+)\)", texto) if not m.group(1).startswith("http")})
    for r in rutas:
        h.update(r.encode("utf-8"))
        h.update((RAIZ / r).read_bytes())
    return h.hexdigest()


def huella_del_pdf(ruta: Path) -> str | None:
    """La huella que lleva el PDF en sus metadatos (Pillow escribe las cadenas en UTF-16 con marca de orden)."""
    datos = ruta.read_bytes()
    marca = b"/Subject (\xfe\xff"
    i = datos.find(marca)
    if i < 0:
        return None
    j = datos.find(b")", i)
    texto = datos[i + len(marca):j].decode("utf-16-be", errors="ignore")
    return texto[len(PREFIJO):] if texto.startswith(PREFIJO) else None


def main() -> int:
    from PIL import Image

    subprocess.run(["quarto", "render", "presentacion-final.qmd", "--to", "revealjs"], cwd=RAIZ, check=True,
                   capture_output=True)
    html = (RAIZ / "_site" / "presentacion-final.html")
    n = len(re.findall(r'<section id="', html.read_text(encoding="utf-8")))
    with tempfile.TemporaryDirectory() as tmp:
        paginas = []
        for i in range(n):
            png = Path(tmp) / f"d{i:02d}.png"
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1600,900",
                            "--virtual-time-budget=6000", f"--screenshot={png}", f"file://{html}#/{i}"],
                           check=True, capture_output=True)
            paginas.append(Image.open(png).convert("RGB"))
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        paginas[0].save(SALIDA, save_all=True, append_images=paginas[1:], resolution=120.0,
                        title="Bioactive: presentación final", subject=PREFIJO + huella())
    print(f"{n} diapositivas -> {SALIDA.relative_to(RAIZ)} ({SALIDA.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
