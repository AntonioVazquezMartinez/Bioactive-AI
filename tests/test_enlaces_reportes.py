"""Los enlaces simbólicos de los reportes tienen que resolver.

Cada carpeta de `docs/reportes/` llega a la bibliografía y al CSL por un enlace
simbólico, porque typst rechaza rutas fuera de su propia raíz y tres copias ya
habían divergido (ver `CLAUDE.md`).

Esta prueba existe porque uno de esos enlaces estuvo roto y nadie lo vio: el
destino de `avance-2/apa.csl` traía un salto de línea al final —26 bytes en vez
de 25— así que apuntaba a un archivo llamado «apa.csl\\n» que no existe. El
modo era el correcto, el destino se veía idéntico en `ls`, y git lo guardaba
sin quejarse. Lo único que fallaba era renderizar el PDF, que no está en CI, y
una revisión que comprobó el modo y el texto del destino lo dio por bueno.
"""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
REPORTES = RAIZ / "docs" / "reportes"

ENLACES = sorted(p for p in REPORTES.rglob("*") if p.is_symlink())


def test_hay_enlaces_que_revisar():
    """Si alguien los convierte en copias, esta prueba deja de proteger nada."""
    assert ENLACES, f"no hay enlaces simbólicos en {REPORTES.relative_to(RAIZ)}"


@pytest.mark.parametrize("enlace", ENLACES, ids=lambda p: str(p.relative_to(REPORTES)))
def test_el_enlace_resuelve(enlace: Path):
    destino = enlace.readlink()
    assert str(destino) == str(destino).strip(), (
        f"el destino de {enlace.relative_to(RAIZ)} trae espacios o saltos de"
        f" línea: {str(destino)!r}")
    assert enlace.exists(), (
        f"{enlace.relative_to(RAIZ)} apunta a {destino}, que no existe;"
        " typst fallará al renderizar ese reporte")
