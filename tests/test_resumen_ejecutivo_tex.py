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
    assert round(al_mes * 5430, -1) == 2770 and round(al_mes * 8390, -1) == 4290
    # neto del año contra los 51,840 de implementación y operación
    assert round((al_mes * 5430 * 12 - 51840) / 100) * 100 == -18500
    assert round((al_mes * 8390 * 12 - 51840) / 100) * 100 == -400
    # más permeables a igual número de ensayos y los que se pierden
    assert round(d * 0.573 * 20, 1) == 1.8 and round((1 - 0.8533) * 0.573 * 20, 1) == 1.7
    plano = TEX.replace("{,}", ",")
    for cifra in ("2,770", "4,290", "8,450", "28,300", "18,500", "1.8 permeables", "1.7 permeables"):
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


def test_el_costo_de_confirmar_un_candidato_cuadra_en_los_dos_mercados():
    """Compuesto (promedio de dos estándares USP) más ensayo, a 17.5 pesos por dólar; México con IVA del 16%."""
    compuesto = round((266 + 317) / 2, -1)
    assert compuesto == 290
    ensayo = {"bajo": 5, "medio": 20, "alto": 2000}
    eeuu = {k: comercial_a_decena((compuesto + v) * 17.5) for k, v in ensayo.items()}
    assert eeuu == {"bajo": 5160, "medio": 5430, "alto": 40080}
    mexico_bajo = comercial_a_decena((compuesto + ensayo["bajo"]) * 17.5 * 1.16)
    mexico_medio = comercial_a_decena(compuesto * 17.5 * 1.16 + 2500)
    assert (mexico_bajo, mexico_medio) == (5990, 8390)
    plano = TEX.replace("{,}", ",")
    for cifra in ("5,160", "5,430", "40,080", "5,990", "8,390", "9,905", "2,962"):
        assert cifra in plano, f"falta {cifra}"
    assert round(173340 / 17.5) == 9905 and round(51840 / 17.5) == 2962


def test_el_ahorro_al_mes_de_cada_escenario():
    al_mes = _evitados_por_candidato() * 20 / 6
    ahorro = {costo: round(costo * al_mes / 10) * 10 for costo in (5160, 5430, 40080, 5990, 8390)}
    assert ahorro == {5160: 2640, 5430: 2770, 40080: 20480, 5990: 3060, 8390: 4290}
    plano = TEX.replace("{,}", ",")
    for cifra in ("2,640", "2,770", "20,480", "3,060", "4,290"):
        assert cifra in plano
