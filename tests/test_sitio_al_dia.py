"""El sitio no se queda atrás de lo que el repositorio tiene (plan anti-stale, `docs/plan-anti-stale.md`).

Cuatro cosas que ya se desfasaron en silencio y que el verificador de enlaces no ve, porque comprueba que los
enlaces resuelvan y no que una página exista en la navegación ni que un estado esté vigente:

1. Un cuaderno de `notebooks/` que ni se publica ni está declarado como excluido: el 06, el cuaderno de la
   patrocinadora, estuvo fuera del sitio sin que nada lo dijera.
2. Una página `.qmd` de la raíz que se construye y a la que no se llega: `presentacion-final.qmd` se construía y
   solo se llegaba a ella con la URL.
3. Un PDF enlazado en el menú que `prepare_site.py` no copia, o que ya no existe.
4. Frases de estado que caducan («en curso», «sin redactar», «próximas entregas»): la portada decía «Avance 4 en
   curso · vence el 25 oct» dos semanas después.

Se lee con expresiones regulares y no con un analizador de YAML, para no añadir una dependencia al CI.
"""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Cuadernos que no se publican a propósito: nombre -> por qué. Vacío hoy; añadir uno exige decir el motivo.
CUADERNOS_EXCLUIDOS: dict[str, str] = {}

# Páginas de la raíz que se construyen y no están en el menú a propósito: nombre -> por qué.
PAGINAS_SIN_MENU = {
    "consulta.qmd": "sigue construyéndose y su URL sirve, pero sale del menú: sus preguntas ya se contestaron",
}

# Frases de estado que caducan, por archivo. Si una vuelve a aparecer, el estado quedó viejo.
FRASES_CADUCAS = {
    "index.qmd": ["En curso", "vence el 25 oct"],
    "README.md": ["En curso", "vence el 25 oct"],
    "docs/guia-del-proyecto.md": ["sin redactar", "afinar los modelos (Avance 4)"],
    "docs/reportes/README.md": ["Próximas entregas", "sin redactar"],
}


def _leer(ruta: str) -> str:
    return (RAIZ / ruta).read_text(encoding="utf-8")


def test_todo_cuaderno_se_publica_o_esta_declarado_como_excluido():
    prepare = _leer("scripts/prepare_site.py")
    quarto = _leer("_quarto.yml")
    for nb in sorted((RAIZ / "notebooks").glob("*.ipynb")):
        if nb.name in CUADERNOS_EXCLUIDOS:
            continue
        assert f"notebooks/{nb.name}" in prepare, f"{nb.name} no está en la lista de prepare_site.py"
        assert f"contenido/notebooks/{nb.name}" in quarto, f"{nb.name} no está en la lista render de _quarto.yml"


def test_las_paginas_de_la_raiz_son_alcanzables():
    quarto = _leer("_quarto.yml")
    indice = _leer("index.qmd")
    render = re.findall(r"^    - ([\w-]+\.qmd)\s*$", quarto, re.M)
    assert render, "no se encontró la lista render de _quarto.yml"
    for pagina in render:
        if pagina == "index.qmd" or pagina in PAGINAS_SIN_MENU:
            continue
        alcanzable = f"href: {pagina}" in quarto or pagina.replace(".qmd", ".html") in indice
        assert alcanzable, f"{pagina} se construye y no está en el menú ni enlazada desde la portada"


def test_los_pdf_del_menu_se_copian_y_existen():
    quarto = _leer("_quarto.yml")
    prepare = _leer("scripts/prepare_site.py")
    for carpeta, archivo in re.findall(r"href: contenido/reportes/([\w-]+)/([\w.-]+\.pdf)", quarto):
        origen = f"docs/reportes/{carpeta}/{archivo}"
        assert origen in prepare, f"el menú enlaza {origen} y prepare_site.py no lo copia"
        assert (RAIZ / origen).exists(), f"el menú enlaza {origen} y no existe"


def test_los_estados_que_caducan_no_estan_en_la_prosa():
    for archivo, frases in FRASES_CADUCAS.items():
        texto = _leer(archivo)
        for frase in frases:
            assert frase not in texto, f"{archivo} dice «{frase}»: un estado que ya caducó"


def test_toda_pagina_qmd_de_la_raiz_se_construye():
    render = set(re.findall(r"^    - ([\w-]+\.qmd)\s*$", _leer("_quarto.yml"), re.M))
    for pagina in sorted(RAIZ.glob("*.qmd")):
        assert pagina.name in render, f"{pagina.name} está en la raíz y no está en la lista render de _quarto.yml"
