"""`recursos/datos.js` tiene que seguir correspondiendo a los datos de los que salió.

El archivo lo genera `scripts/cifras_presentacion.py` y alimenta las nueve gráficas
de la presentación. Como está versionado y los archivos de la patrocinadora también,
es fácil que uno cambie y el otro se quede: la presentación seguiría mostrando
cifras de una versión anterior sin que nada avisara. El generador guarda la huella
de cada archivo de entrada; esto comprueba que esas huellas sigan siendo las buenas.

También revisa que las cifras que el mazo afirma sigan estando en el JSON, para que
borrar un campo del generador no deje gráficas vacías sin que nadie se entere.
"""

import hashlib
import json
import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
DATOS = RAIZ / "recursos/datos.js"


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
            pytest.skip(f"{nombre} no está disponible aquí (Git LFS)")
        h = hashlib.sha256()
        with open(ruta, "rb") as f:
            for bloque in iter(lambda: f.read(1 << 20), b""):
                h.update(bloque)
        if not h.hexdigest().startswith(esperada):
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
