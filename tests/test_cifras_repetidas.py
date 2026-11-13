"""Una cifra citada en varios documentos dice lo mismo en todos.

El mismo número vive en hasta doce archivos —el 1,048 de los grupos— y cada corrección se
hace en el que alguien estaba leyendo. Así tres copias de una razón que el #223 retiró le
sobrevivieron, una de ellas en un documento creado en la misma ronda, y el propio registro
conservó el estimador superado dos líneas por encima de su corrección.

Esta prueba **no** comprueba que la cifra sea cierta: eso lo ata la corrida que la entrada
cita. Comprueba que las copias coincidan, que es la parte barata y la que se rompe sola.
Exime una copia marcada como superada: el registro tiene que conservarlas visibles.
"""

import csv
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SUPERADO = re.compile(r"versi[oó]n anterior|versi[oó]n superada|superad\w+|dec[ií]a", re.I)
ESPACIOS = re.compile(r"\s+")
N = r"(\d\.\d)"

# Cuántas veces se leyó la prueba: se cuenta de `experimentos/prueba.csv`, no se escribe a mano.
# Esa cifra derivó 6 → 7 → 9 → 11 en tres días y cada corrección se hizo en el documento que
# alguien estaba leyendo; ahora añadir una lectura al CSV sin actualizar las copias falla aquí.
_LECTURAS = len(list(csv.DictReader((RAIZ / "experimentos" / "prueba.csv").open(encoding="utf-8"))))
_EN_PALABRAS = {9: "nueve", 10: "diez", 11: "once", 12: "doce", 13: "trece", 14: "catorce",
                15: "quince"}

# (nombre, patrón con un grupo, valor canónico). Añadir una cifra vigilada es una línea.
CIFRAS = [
    ("los compuestos del gráfico de puntos de la fase 1", r"fase[~ ]1 \((\d+), los mismos", "300"),
    ("los pares del gráfico de puntos de la fase 2", r"\(([\d,]+), una submuestra de", "3,000"),
    ("las filas por pliegue de esa submuestra", r"submuestra de (\d+) filas por pliegue", "600"),
    ("las lecturas de la prueba, en palabras",
     r"se ley[óo] \**(\w+) veces", _EN_PALABRAS.get(_LECTURAS, f"<{_LECTURAS}: añádela a _EN_PALABRAS>")),
    ("las lecturas de la prueba, en cifras",
     r"lecturas de la prueba \(`prueba\.csv`\) \| (\d+)", str(_LECTURAS)),
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
    # El cruce entre las dos fases tiene dos valores verdaderos que cuentan archivos distintos, y el
    # registro citaba solo el del archivo crudo. Se vigila el del archivo que ve el modelo, que es el
    # que acota la C.3; el 1,033 del crudo se queda y no se vigila porque no es el que deriva.
    ("los esqueletos comunes en el archivo que ve el modelo",
     r"([\d,]{3,5}) esqueletos en el archivo que ve el modelo", "612"),
    ("los esqueletos comunes en el archivo que ve el modelo, en inglés",
     r"([\d,]{3,5}) skeletons in the file the model sees", "612"),
    # La prevalencia tiene tres valores verdaderos sobre poblaciones distintas —63.5% en los 7,805
    # con clase, 65.0% en las 6,306 de ajuste y 57.3% en la prueba— y se vigila solo la primera,
    # atada a la frase que la nombra. El #313 la corrigió en el entregable y el artículo científico
    # se quedó con el 65%, que es la del ajuste: el documento escrito a mano quedó fuera de la
    # cadena del borrador y nada lo detectó. Las otras dos no se vigilan porque su contexto dice de
    # qué población habla, y el piso de AUPRC de 0.350 las ata aparte.
    # Va anclada a la población y no solo a «% son BBB+»: sin el ancla enganchaba el 99.5% de los
    # 410 compuestos de un componente conexo del Avance 0, que es otra cifra verdadera.
    ("la prevalencia de BBB+ en los 7,805 compuestos con clase",
     r"7,805 compuestos con clase.{0,260}?([\d.]{2,4})\s*\\?,?\\?%\s*(?:son|de ellos) BBB\+", "63.5"),
    # Meter los decks al corpus no bastó: citan las mismas cifras con su propia redacción, más corta,
    # y ningún patrón anclado en una frase de la prosa las alcanzaba. Así que cada cifra que el deck
    # repite necesita su propia entrada, igual que la versión en inglés de los 612.
    ("la prevalencia de BBB+, como la dice el deck",
     r"([\d.]{2,4})\s*\\?,?\\?%\s*es el archivo completo", "63.5"),
    ("los esqueletos medidos en las dos fases, como lo dice el deck",
     r"\*{0,2}([\d,]{3,5})\s*esqueletos\*{0,2}\s*est[áa]n medidos en las dos", "612"),
    # La lista priorizada (C.5, 12 de noviembre) vive en el deck, los dos artículos, el resumen, el sitio y el
    # registro. Sus tres cifras de lectura se escriben cada una con su frase.
    ("los compuestos distintos de la lista priorizada, como lo dice el deck",
     r"(\d+) compuestos distintos en 260", "84"),
    ("los compuestos distintos de la lista priorizada, en prosa",
     r"260 (?:filas|lugares) por diana[^.]{0,40}?(\d+) compuestos distintos", "84"),
    ("los candidatos con barrera probable de la lista priorizada",
     r"([\d,]+) candidatos (?:con barrera probable|de 1,821)", "752"),
    ("los candidatos que quedan en la lista priorizada",
     r"quedan ([\d,]+) candidatos", "752"),
]


def _corpus() -> dict[str, str]:
    textos: dict[str, str] = {}
    # Los `.tex` entran por los dos artículos. El de la rúbrica se genera desde su borrador, así
    # que ahí la cifra ya venía vigilada en el Markdown; el científico se escribe a mano y queda
    # fuera de esa cadena, de modo que sin esto una cifra podía corregirse en un artículo y no en
    # el otro. La plantilla del curso también es `.tex` y no cita cifras, así que no molesta.
    # Los dos decks viven en la raíz y no bajo `docs/`, así que el glob de abajo no los veía: con el
    # #310 y el #314 `presentacion-final.qmd` ya repite el 0.752, el 0.419, el 1,048, el 4.2, el 63.5,
    # el 57.3 y los 612, y quedaban fuera de la red. Entran por nombre y no con `*.qmd` de la raíz,
    # porque `index.qmd`, `consulta.qmd` y `visualizador.qmd` son páginas del sitio que no citan cifras.
    for p in [RAIZ / "CLAUDE.md", RAIZ / "presentacion.qmd", RAIZ / "presentacion-final.qmd",
              *RAIZ.glob("docs/**/*.md"), *RAIZ.glob("docs/**/*.qmd"),
              *RAIZ.glob("docs/**/*.tex")]:
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
    # Por valor y no por índice: el #268 insertó dos entradas al principio de CIFRAS y
    # esta prueba, que direccionaba CIFRAS[0] y CIFRAS[1], quedó comparando el patrón de
    # las lecturas contra «7.1». Pasó en vacío hasta que alguien lo probó a mano.
    vigiladas = [(p, v) for _, p, v in CIFRAS if v in ("7.1", "2.2")]
    assert len(vigiladas) == 2, (
        "las entradas del 7.1 y del 2.2 cambiaron de valor o salieron de CIFRAS")

    sueltas, vistas = [], 0
    for ruta, texto in corpus.items():
        for patron, valor in vigiladas:
            for m in re.finditer(patron, texto):
                if valor not in next(g for g in m.groups() if g):
                    continue
                vistas += 1
                contexto = texto[max(0, m.start() - 220):m.end() + 260]
                if re.search(r"bosque|forest|svm_rbf|superad|dec[ií]a", contexto, re.I):
                    continue
                sueltas.append(f"{ruta} cita {valor} sin decir que es del bosque")
    assert vistas, (
        "la guarda no encontró ninguna cita del 7.1 ni del 2.2: el patrón o la redacción "
        "cambiaron y dejó de vigilar sin que nada falle")
    assert not sueltas, "; ".join(sueltas)
