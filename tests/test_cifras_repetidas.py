"""Una cifra citada en varios documentos dice lo mismo en todos.

El mismo número vive en hasta doce archivos —el 1,048 de los grupos— y cada corrección se
hace en el que alguien estaba leyendo. Así tres copias de una razón que el #223 retiró le
sobrevivieron, una de ellas en un documento creado en la misma ronda, y el propio registro
conservó el estimador superado dos líneas por encima de su corrección.

Esta prueba **no** comprueba que la cifra sea cierta: eso lo ata la corrida que la entrada
cita. Comprueba que las copias coincidan, que es la parte barata y la que se rompe sola.
Exime una copia marcada como superada: el registro tiene que conservarlas visibles.
"""

import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SUPERADO = re.compile(r"versi[oó]n anterior|versi[oó]n superada|superad\w+|dec[ií]a", re.I)
ESPACIOS = re.compile(r"\s+")
N = r"(\d\.\d)"

# (nombre, patrón con un grupo, valor canónico). Añadir una cifra vigilada es una línea.
CIFRAS = [
    ("el MCC que infla agrupar solo por andamio",
     rf"infla\w*.{{0,90}}?(?:MCC (?:en |de )?{N}|{N} (?:puntos )?de MCC)", "7.1"),
    ("el AUROC que infla agrupar solo por andamio",
     rf"infla\w*.{{0,90}}?(?:AUROC (?:en |de )?{N}|{N} (?:puntos )?de AUROC)", "2.2"),
    ("los grupos que da el andamio solo",
     r"solo por andamio d[ai]\w* ([\d,]{5})", "2,239"),
    ("el par más lejano en MCC, con una semilla",
     r"en MCC son el boosting y la log[ií]stica \((0\.\d{4})", "0.0222"),
    ("cuántas veces pesa más el agrupamiento que el modelo",
     r"(?:agrupamiento|andamio).{0,170}?"
     r"((?:casi |algo más de |más de )?(?:dos|tres|cuatro|cinco)) veces", "tres"),
]


def _corpus() -> dict[str, str]:
    textos: dict[str, str] = {}
    for p in [RAIZ / "CLAUDE.md", *RAIZ.glob("docs/**/*.md"), *RAIZ.glob("docs/**/*.qmd")]:
        textos[str(p.relative_to(RAIZ))] = ESPACIOS.sub(" ", p.read_text(encoding="utf-8"))
    for nb in RAIZ.glob("notebooks/*.ipynb"):
        celdas = json.loads(nb.read_text(encoding="utf-8"))["cells"]
        md = " ".join("".join(c["source"]) for c in celdas if c["cell_type"] == "markdown")
        textos[str(nb.relative_to(RAIZ))] = ESPACIOS.sub(" ", md)
    return textos


@pytest.fixture(scope="module")
def corpus() -> dict[str, str]:
    return _corpus()


@pytest.mark.parametrize("nombre,patron,valor", CIFRAS, ids=[c[0][:34] for c in CIFRAS])
def test_cada_copia_dice_lo_mismo(nombre, patron, valor, corpus):
    discrepan = []
    for ruta, texto in corpus.items():
        for m in re.finditer(patron, texto):
            visto = next(g for g in m.groups() if g)
            if valor in visto:
                continue
            if SUPERADO.search(texto[max(0, m.start() - 220):m.start()]):
                continue  # declarada superada a propósito
            discrepan.append(f"{ruta} dice «{visto}»")
    assert not discrepan, (
        f"{nombre}: el valor canónico es «{valor}» y " + "; ".join(discrepan)
        + ". Corrige la copia, o márcala como versión superada si es deliberado.")


def test_la_guarda_encuentra_las_citas_que_vigila(corpus):
    """Si un patrón deja de encontrar nada, dejó de vigilar sin que nada falle."""
    muertos = [n for n, p, _ in CIFRAS if not any(re.search(p, t) for t in corpus.values())]
    assert not muertos, (
        f"estos patrones ya no encuentran ninguna cita: {muertos}. La redacción cambió y la "
        "guarda quedó muerta: ajusta el patrón o quítalo con su cifra.")


def test_el_7_1_y_el_2_2_se_atribuyen_al_bosque(corpus):
    """El 2.2 de AUROC y el 7.1 de MCC son del bosque; con el `svm_rbf` entregado son 1.3 y 1.9.

    Una copia que los cite sin decir de qué modelo son los presenta como un efecto general,
    que es lo que la corrida 2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad desmintió.
    """
    sueltas = []
    for ruta, texto in corpus.items():
        for patron, valor in ((CIFRAS[0][1], "7.1"), (CIFRAS[1][1], "2.2")):
            for m in re.finditer(patron, texto):
                if valor not in next(g for g in m.groups() if g):
                    continue
                contexto = texto[max(0, m.start() - 220):m.end() + 260]
                if re.search(r"bosque|forest|svm_rbf|superad|dec[ií]a", contexto, re.I):
                    continue
                sueltas.append(f"{ruta} cita {valor} sin decir que es del bosque")
    assert not sueltas, "; ".join(sueltas)
