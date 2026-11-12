"""El resumen ejecutivo (entrega 8): que no quede relleno de la plantilla, que sus citas existan, que la
aritmética del costo cuadre y que sus cifras sean las del artículo y las de la corrida que las mide.
No compila: el conteo de páginas se verifica al compilar (3 hasta las referencias, anexos aparte)."""
import csv
import math
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


def _evitados_por_candidato() -> float:
    """Fracción de candidatos que el modelo evita frente a un sorteo a igual recuperación de permeables:
    el sorteo tendría que confirmar la cobertura del modelo, así que se evita (cobertura − fracción)."""
    carpeta = next((RAIZ / "experimentos").glob("*ahorro-por-priorizacion-fase1"))
    with open(carpeta / "ahorro.csv", encoding="utf-8") as f:
        fila = next(r for r in csv.DictReader(f) if abs(float(r["fraccion_ensayada"]) - 0.7) < 1e-9)
    return round(float(fila["cobertura_permeables"]), 4) - 0.7


def test_la_base_del_ahorro_es_el_modelo_contra_el_sorteo_y_no_el_30_por_ciento():
    d = _evitados_por_candidato()
    assert round(d, 4) == 0.1533  # 15.3 puntos, no 30
    al_mes = d * 20 / 6
    assert round(al_mes, 2) == 0.51
    # ahorro al mes de los dos escenarios (insumos propios y servicio contratado), con precios de EE. UU.
    assert round(al_mes * 6390, -1) == 3270 and round(al_mes * 35700, -1) == 18240
    # neto del año contra los 51,840 de implementación y operación
    assert round((al_mes * 6390 * 12 - 51840) / 100) * 100 == -12700
    assert al_mes * 35700 * 12 - 51840 > 0
    # más permeables a igual número de ensayos y los que se pierden
    assert round(d * 0.573 * 20, 1) == 1.8 and round((1 - 0.8533) * 0.573 * 20, 1) == 1.7
    plano = TEX.replace("{,}", ",")
    for cifra in ("3,270", "18,240", "8,450", "28,300", "12,700", "1.7 permeables"):
        assert cifra in plano, f"falta {cifra}"


def test_el_punto_de_equilibrio_sale_de_la_base_honesta():
    d = _evitados_por_candidato()
    for volumen, sin, con in ((10, 16908, 56536), (20, 8454, 28268), (40, 4227, 14134), (100, 1691, 5654)):
        evitados = d * volumen / 6
        assert round(4320 / evitados) == sin and round(14445 / evitados) == con
        assert f"{sin:,}" in TEX and f"{con:,}" in TEX


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


def comercial_a_decena(v):
    return math.floor(v / 10 + 0.5) * 10


def test_el_costo_de_confirmar_un_candidato_cuadra_en_los_dos_escenarios_y_mercados():
    """Compuesto (promedio de dos estándares USP) más dos pruebas, a 17.5 pesos por dólar; México con 16% de IVA."""
    compuesto = round((266 + 317) / 2, -1)
    assert compuesto == 290
    pruebas = {"propios": 15 + 60, "servicio": 250 + 1500}  # permeabilidad más actividad celular
    usd = {k: compuesto + v for k, v in pruebas.items()}
    assert usd == {"propios": 365, "servicio": 2040}
    eeuu = {k: comercial_a_decena(v * 17.5) for k, v in usd.items()}
    assert eeuu == {"propios": 6390, "servicio": 35700}
    mexico = {k: comercial_a_decena(v * 17.5 * 1.16) for k, v in usd.items()}
    assert mexico == {"propios": 7410, "servicio": 41410}
    plano = TEX.replace("{,}", ",")
    for cifra in ("6,390", "35,700", "7,410", "41,410", "9,905", "2,962", "31,590"):
        assert cifra in plano, f"falta {cifra}"
    assert round(173340 / 17.5) == 9905 and round(51840 / 17.5) == 2962 and (80 + 76) * 202.5 == 31590


def test_el_ahorro_al_mes_de_cada_escenario():
    al_mes = _evitados_por_candidato() * 20 / 6
    ahorro = {costo: round(costo * al_mes / 10) * 10 for costo in (6390, 7410, 35700, 41410)}
    assert ahorro == {6390: 3270, 7410: 3790, 35700: 18240, 41410: 21160}
    plano = TEX.replace("{,}", ",")
    for cifra in ("3,270", "3,790", "18,240", "21,160"):
        assert cifra in plano
