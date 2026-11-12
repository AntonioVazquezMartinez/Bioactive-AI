"""El resumen ejecutivo (entrega 8): que no quede relleno de la plantilla, que sus citas existan, que la
aritmética del costo cuadre y que sus cifras sean las del artículo y las de la corrida que las mide.
No compila: el conteo de páginas se verifica al compilar (3 hasta las referencias, anexos aparte)."""
import csv
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TEX = (RAIZ / "docs/reportes/resumen-ejecutivo/resumen_ejecutivo.tex").read_text(encoding="utf-8")
BIB = (RAIZ / "docs/referencias/bibliografia.bib").read_text(encoding="utf-8")
ARTICULO = (RAIZ / "docs/reportes/articulo/borrador.md").read_text(encoding="utf-8")


def test_no_queda_relleno_de_la_plantilla():
    assert "lorem" not in TEX.lower()
    assert "\\textcolor{red}" not in TEX
    assert "[indicar" not in TEX
    assert "Título del proyecto" not in TEX


def test_toda_clave_citada_esta_en_la_bibliografia():
    claves = set()
    for m in re.finditer(r"\\(?:parencite|textcite|cite)\{([^}]*)\}", TEX):
        claves.update(c.strip() for c in m.group(1).split(","))
    existentes = set(re.findall(r"^@\w+\{([^,]+),", BIB, re.M))
    assert not claves - existentes, f"claves sin entrada: {claves - existentes}"


def test_el_costo_cuadra_por_servicio_y_en_total():
    tarifa = round(24000 * 1.35 / 160, 2)
    assert tarifa == 202.5
    horas = {"desarrollo": 400 + 140 + 60, "implementacion": 32 + 24 + 24, "operacion": 96 + 80}
    costo = {k: round(v * tarifa) for k, v in horas.items()}
    assert costo == {"desarrollo": 121500, "implementacion": 16200, "operacion": 35640}
    assert sum(costo.values()) == 173340 and sum(horas.values()) == 856
    for cifra in ("121,500", "16,200", "35,640", "173,340", "51,840", "4,320", "14,445"):
        assert cifra in TEX.replace("{,}", ","), f"falta {cifra}"
    assert costo["implementacion"] + costo["operacion"] == 51840


def test_el_punto_de_equilibrio_sale_de_las_dos_bases():
    for volumen, sin, con in ((20, 720, 2408), (50, 288, 963), (100, 144, 482), (200, 72, 241)):
        evitados = 0.3 * volumen
        assert round(4320 / evitados) == sin and round(14445 / evitados) == con
        assert f"{sin:,}" in TEX or str(sin) in TEX
    assert 15 * 350 == 5250 and 15 * 90 == 1350 and 15 * 35000 == 525000


def test_las_cifras_de_desempeno_son_las_del_articulo():
    for cifra in ("0.793", "0.339", "0.720", "0.919"):
        assert cifra in TEX and cifra in ARTICULO, f"{cifra} no coincide con el artículo"
    assert "0.410" in TEX and "0.4095" in ARTICULO


def test_la_tabla_de_ahorro_es_la_de_la_corrida():
    carpeta = next((RAIZ / "experimentos").glob("*ahorro-por-priorizacion-fase1"))
    with open(carpeta / "ahorro.csv", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert len(filas) == 7
    for fila in filas:
        fraccion = round(float(fila["fraccion_ensayada"]) * 100)
        if fraccion < 40:
            continue
        cobertura = f"{float(fila['cobertura_permeables']) * 100:.1f}"
        acierto = f"{float(fila['aciertos_entre_lo_ensayado']) * 100:.1f}"
        renglon = next(r for r in TEX.splitlines() if r.lstrip().startswith(f"{fraccion}\\,\\%") and "&" in r)
        assert cobertura in renglon and acierto in renglon, f"la fila de {fraccion}% no coincide con la corrida"


def test_los_dos_mercados_de_precios_cuadran():
    """EE. UU. convertido a 17.5 pesos por dólar y México: el bajo con IVA del 16%, el medio de un centro público."""
    assert round(5 * 17.5, -1) == 90 and round(20 * 17.5) == 350 and 2000 * 17.5 == 35000
    assert round(90 * 1.16) == 104 and 15 * 104 == 1560 and 15 * 2500 == 37500
    plano = TEX.replace("{,}", ",")
    for cifra in ("1,560", "37,500", "9,905", "2,962"):
        assert cifra in plano, f"falta {cifra}"
    assert round(173340 / 17.5) == 9905 and round(51840 / 17.5) == 2962
