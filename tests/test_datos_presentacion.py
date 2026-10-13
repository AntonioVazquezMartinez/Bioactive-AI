"""`recursos/datos.js` tiene que seguir correspondiendo a los datos de los que salió.

El archivo lo genera `scripts/cifras_presentacion.py` y alimenta las nueve gráficas
de la presentación. Como está versionado y los archivos de la patrocinadora también,
es fácil que uno cambie y el otro se quede: la presentación seguiría mostrando
cifras de una versión anterior sin que nada avisara. El generador guarda la huella
de cada archivo de entrada; esto comprueba que esas huellas sigan siendo las buenas.

También revisa que las cifras que el mazo afirma sigan estando en el JSON, para que
borrar un campo del generador no deje gráficas vacías sin que nadie se entere.
"""

import importlib.util
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "recursos/datos.js"

# El archivo de actividad va por Git LFS y en CI se obtiene como puntero, no como
# contenido: hashearlo daría la huella del puntero. `verificar_datos.huella` ya
# resuelve ese caso leyendo el `oid` del puntero, así que se reutiliza en vez de
# repetir la lógica —y de que las dos versiones se separen con el tiempo—.
_spec = importlib.util.spec_from_file_location(
    "verificar_datos", RAIZ / "scripts/verificar_datos.py")
_vd = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vd)


def cargar() -> dict:
    texto = DATOS.read_text(encoding="utf-8")
    m = re.search(r"window\.DATOS = (.*);\s*$", texto, re.S)
    assert m, "datos.js no tiene la forma «window.DATOS = {...};»"
    return json.loads(m.group(1))


@pytest.fixture(scope="module")
def datos() -> dict:
    if not DATOS.exists():
        pytest.skip("falta recursos/datos.js; se genera con scripts/cifras_presentacion.py")
    return cargar()


def test_las_huellas_corresponden_a_los_archivos_actuales(datos):
    """Si esto falla, hay que volver a correr `scripts/cifras_presentacion.py`."""
    huellas = datos.get("huellas") or {}
    assert huellas, "datos.js no guardó las huellas de sus archivos de entrada"

    desfasados = []
    for nombre, esperada in huellas.items():
        ruta = RAIZ / "data/external/profesora" / nombre
        if not ruta.exists():
            pytest.skip(f"{nombre} no está en esta copia del repositorio")
        if not _vd.huella(ruta)["sha256"].startswith(esperada):
            desfasados.append(nombre)

    assert not desfasados, (
        "estos archivos cambiaron desde que se generó recursos/datos.js: "
        + ", ".join(desfasados)
        + ". Corre «python3 scripts/cifras_presentacion.py»."
    )


@pytest.mark.parametrize("ruta", [
    "esqueletos.filas", "esqueletos.esqueletos", "esqueletos.techo_exactitud",
    "filtrado_ab.completo.n", "filtrado_ab.ab.pct_minoritaria",
    "tpsa.cortes", "tpsa.series.completo", "tpsa.optimos.completo.cortes_meseta",
    "etapas.ambos", "etapas.actividad", "etapas.permeabilidad",
    "actividad.registros", "actividad.registros_diccionario",
    "actividad.cortes.10.seguros", "actividad.dianas", "actividad.enfermedades",
])
def test_las_graficas_tienen_de_donde_leer(datos, ruta):
    """Cada campo que alguna de las nueve gráficas lee tiene que existir."""
    nodo = datos
    for parte in ruta.split("."):
        assert parte in nodo, f"falta «{ruta}» en datos.js"
        nodo = nodo[parte]
    assert nodo not in (None, [], {}), f"«{ruta}» viene vacío"


def test_las_dos_fases_cuadran(datos):
    """Los esqueletos comunes no pueden exceder a ninguna de las dos fases."""
    e = datos["etapas"]
    assert e["ambos"] <= min(e["permeabilidad"], e["actividad"])
    assert e["permeabilidad"] == datos["esqueletos"]["esqueletos"]


def test_la_meseta_sale_de_un_bootstrap_y_no_de_una_tolerancia(datos):
    """La afirmación «no se distingue del mejor» tiene que tener remuestreo detrás."""
    for nombre, opt in datos["tpsa"]["optimos"].items():
        assert opt.get("remuestreos", 0) >= 1000, f"{nombre}: muy pocas remuestras"
        cortes = opt["cortes_meseta"]
        assert opt["corte"] in cortes, f"{nombre}: el mejor corte no está en su propia meseta"
        assert [min(cortes), max(cortes)] == opt["meseta"]


# ---------------------------------------------------------------------------
# Las cifras que la patrocinadora va a leer
#
# `consulta.qmd` y `docs/acta-patrocinadora.md` son texto: sus números están
# escritos a mano y no pasan por `datos.js`. Si los datos cambian, se desfasan en
# silencio, que es justo lo que el resto de este archivo quiere evitar. Esto los
# ata: cada cifra que esos dos documentos afirman tiene que seguir saliendo del
# generador. Cuando una falla, el arreglo es corregir el documento, no la prueba.
# ---------------------------------------------------------------------------

CONSULTA = RAIZ / "consulta.qmd"
ACTA = RAIZ / "docs/acta-patrocinadora.md"


def mil(n: int) -> str:
    return f"{n:,}"


def cifras_esperadas(datos: dict) -> dict[str, str]:
    a = datos["actividad"]
    dianas = sorted(a["dianas"], key=lambda d: d["declaradas"])
    resto = [d for d in dianas if d["declaradas"] >= 10]
    return {
        "registros recibidos": mil(a["registros"]),
        "registros del diccionario": mil(a["registros_diccionario"]),
        "diferencia entre los dos archivos": mil(a["registros_diccionario"] - a["registros"]),
        "censurados que sirven a 10 µM": mil(a["cortes"]["10"]["seguros"]),
        "censurados que sirven a 1 µM": mil(a["cortes"]["1"]["seguros"]),
        "ambiguos a 10 µM": mil(a["cortes"]["10"]["ambiguos"]),
        "ambiguos a 1 µM": mil(a["cortes"]["1"]["ambiguos"]),
        "filas de una sola referencia": mil(a["cortes"]["10"]["de_una_referencia"]),
        "la diana con más registros declarados": mil(resto[-1]["declaradas"]),
        "la diana escasa más grande que las excluidas": mil(resto[0]["declaradas"]),
    }


@pytest.mark.parametrize("documento", [CONSULTA, ACTA], ids=["consulta", "acta"])
def test_las_cifras_que_ella_lee_siguen_saliendo_del_generador(datos, documento):
    if not documento.exists():
        pytest.skip(f"no está {documento.name}")
    texto = documento.read_text(encoding="utf-8")
    esperadas = cifras_esperadas(datos)
    # El acta no repite el detalle de las dianas: su tabla es la de las cuatro
    # excluidas, que comprueba la prueba siguiente.
    if documento is ACTA:
        for k in ("la diana con más registros declarados",
                  "la diana escasa más grande que las excluidas"):
            esperadas.pop(k, None)
    faltantes = {k: v for k, v in esperadas.items() if v not in texto}
    assert not faltantes, (
        f"{documento.name} cita cifras que ya no corresponden a recursos/datos.js: "
        + "; ".join(f"{k} debería decir {v}" for k, v in faltantes.items())
    )


@pytest.mark.parametrize("documento", [CONSULTA, ACTA], ids=["consulta", "acta"])
def test_las_cuatro_dianas_excluidas_son_las_que_dicen_los_datos(datos, documento):
    if not documento.exists():
        pytest.skip(f"no está {documento.name}")
    texto = documento.read_text(encoding="utf-8")
    vacias = [d["gen"] for d in datos["actividad"]["dianas"] if d["declaradas"] < 10]
    assert len(vacias) == 4, f"ya no son cuatro las dianas sin datos, son {len(vacias)}"
    faltan = [g for g in vacias if g not in texto]
    assert not faltan, f"{documento.name} no nombra {', '.join(faltan)}"


def test_el_mejor_corte_lo_es_de_verdad_en_la_serie(datos):
    """Que `optimos` y `series` no se contradigan: sin esto la meseta podría
    describir un máximo que la curva publicada no tiene."""
    for nombre, opt in datos["tpsa"]["optimos"].items():
        serie = datos["tpsa"]["series"][nombre]
        js = []
        for tp, fn, fp, tn in serie:
            sens = tp / (tp + fn) if tp + fn else 0
            esp = tn / (tn + fp) if tn + fp else 0
            js.append(sens + esp - 1)
        i = datos["tpsa"]["cortes"].index(opt["corte"])
        assert js[i] == pytest.approx(max(js)), f"{nombre}: el corte declarado no maximiza J"
        assert opt["j"] == pytest.approx(max(js), abs=5e-4), f"{nombre}: J publicado no cuadra"


def test_el_bootstrap_agrupa_por_esqueleto(datos):
    """Las filas no son independientes; remuestrear compuestos angosta los
    intervalos y subestima la meseta. Tiene que remuestrear esqueletos."""
    for nombre, opt in datos["tpsa"]["optimos"].items():
        assert opt.get("unidad") == "esqueleto de conectividad", f"{nombre}: unidad equivocada"
        assert 0 < opt["clusteres"] <= datos["tpsa"]["n"][nombre], f"{nombre}: clústeres raros"
