"""Todo cuaderno que el sitio publica tiene una entrada en su navegación, y al revés.

Existe porque el 05 y el 05c se registraron en `prepare_site.py` y en la lista de `render` de
`_quarto.yml`, y no en el navbar: las dos páginas se construían y se publicaban, y no se llegaba a
ellas desde ninguna parte. El verificador de enlaces no lo ve, porque comprueba que los enlaces
resuelvan y no que una página sea alcanzable, así que el CI se quedaba en verde.

Se lee `_quarto.yml` con una expresión regular y no con un analizador de YAML, para no añadir una
dependencia al CI por una comprobación de dos listas.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CUADERNO = r"contenido/notebooks/[^\s]+\.ipynb"


def _quarto() -> str:
    return (RAIZ / "_quarto.yml").read_text(encoding="utf-8")


def test_cada_cuaderno_publicado_esta_en_el_navbar():
    texto = _quarto()
    publicados = set(re.findall(rf"^    - ({CUADERNO})\s*$", texto, re.M))
    navegacion = set(re.findall(rf"href: ({CUADERNO})", texto))
    assert publicados, "no se encontró la lista de render de _quarto.yml"
    assert not publicados - navegacion, (
        f"se publican y no se llega a ellos desde la navegación: {sorted(publicados - navegacion)}")


def test_cada_entrada_del_navbar_se_publica():
    texto = _quarto()
    publicados = set(re.findall(rf"^    - ({CUADERNO})\s*$", texto, re.M))
    navegacion = set(re.findall(rf"href: ({CUADERNO})", texto))
    assert not navegacion - publicados, (
        f"el navbar enlaza cuadernos que no se renderizan: {sorted(navegacion - publicados)}")
