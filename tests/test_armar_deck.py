"""La presentación sale del notebook sin modificarlo, y cabe en la pantalla.

Las dos cosas que estas pruebas atan son las que harían inútil la herramienta:
que el marcado se filtre al `.ipynb` —que es el entregable, y su diff no debe
llenarse de metadatos de presentación— y que una diapositiva crezca por encima
de lo que el equipo ya proyectó sin que nada avise. Lo segundo importa sobre
todo en el 04, cuyas celdas de hallazgo están vacías a propósito: cuando se
llenen, esta prueba es lo que dice si el corte sigue sirviendo.
"""

import json
from pathlib import Path

import pytest

from scripts.armar_deck import CON_DECK, TECHO, diapositivas, marcar

RAIZ = Path(__file__).resolve().parent.parent
NOTEBOOKS = [RAIZ / "notebooks" / f"{n}.ipynb" for n in CON_DECK]


@pytest.fixture
def nb_03():
    return json.loads((RAIZ / "notebooks" / "03_Baseline.ipynb").read_text())


def test_marcar_no_modifica_el_notebook_que_recibe(nb_03):
    antes = json.dumps(nb_03, sort_keys=True)
    marcar(nb_03)
    assert json.dumps(nb_03, sort_keys=True) == antes


@pytest.mark.parametrize("ruta", NOTEBOOKS, ids=lambda p: p.stem)
def test_ninguna_diapositiva_pasa_el_techo(ruta):
    """El techo son 1,761 caracteres, el máximo medido en presentacion.qmd."""
    marcado, _ = marcar(json.loads(ruta.read_text()))
    largos = [len(d) for d in diapositivas(marcado)]
    assert largos, f"{ruta.name} no produjo ninguna diapositiva"
    peor = max(largos)
    assert peor <= TECHO, (
        f"{ruta.name}: la diapositiva más cargada tiene {peor} caracteres."
        " Pártela en el notebook o acomoda la prosa en párrafos más cortos.")


@pytest.mark.parametrize("ruta", NOTEBOOKS, ids=lambda p: p.stem)
def test_cada_celda_marcada_lleva_un_tipo_valido(ruta):
    marcado, _ = marcar(json.loads(ruta.read_text()))
    validos = {"slide", "subslide", "fragment", "skip"}
    for i, celda in enumerate(marcado["cells"]):
        tipo = celda["metadata"]["slideshow"]["slide_type"]
        assert tipo in validos, f"{ruta.name} celda {i}: {tipo}"


def test_la_etiqueta_sin_diapositiva_saca_la_celda():
    """Es lo que mantiene la declaración de uso de IA fuera de la exposición."""
    nb = {"cells": [
        {"cell_type": "markdown", "source": ["## Uno\n"], "metadata": {}},
        {"cell_type": "markdown", "source": ["## Secreto\n"],
         "metadata": {"tags": ["sin-diapositiva"]}},
    ]}
    marcado, _ = marcar(nb)
    textos = "".join(diapositivas(marcado))
    assert "Uno" in textos
    assert "Secreto" not in textos


def test_la_declaracion_del_04_no_sale_en_la_presentacion():
    marcado, _ = marcar(json.loads((RAIZ / "notebooks" / "04_Models.ipynb").read_text()))
    assert "Declaración de uso de IA" not in "".join(diapositivas(marcado))


def test_una_lista_larga_se_parte_y_arrastra_su_encabezado():
    """El cierre del 03 son cinco numerados seguidos: un solo párrafo de 2,024."""
    puntos = "\n".join(f"{i}. " + "palabra " * 60 for i in range(1, 6))
    nb = {"cells": [{"cell_type": "markdown", "metadata": {},
                     "source": [f"## Conclusiones\n\n{puntos}\n"]}]}
    marcado, _ = marcar(nb)
    partes = diapositivas(marcado)
    assert len(partes) > 1, "la lista no se partió"
    assert all(len(p) <= TECHO for p in partes)
    assert "(sigue)" in partes[1], "la continuación quedó sin encabezado"


def test_una_celda_de_codigo_sin_salida_no_ocupa_diapositiva():
    nb = {"cells": [
        {"cell_type": "markdown", "source": ["## Uno\n"], "metadata": {}},
        {"cell_type": "code", "source": ["x = 1\n"], "metadata": {}, "outputs": []},
    ]}
    marcado, _ = marcar(nb)
    assert marcado["cells"][1]["metadata"]["slideshow"]["slide_type"] == "skip"
