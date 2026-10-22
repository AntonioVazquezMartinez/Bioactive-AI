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


# ---------------------------------------------------------------------------
# Los dos experimentos del Avance 2
#
# `datos.js` guarda la huella de los archivos de la patrocinadora, pero no la de
# los CSV de los experimentos: si uno se vuelve a correr, el mazo sigue dibujando
# la versión anterior sin que nada avise. Esto los recalcula desde el CSV, que es
# además la única prueba del error estándar corregido —el factor de Nadeau y
# Bengio ya estuvo mal una vez (contaba los 5 pliegues donde van las 15
# evaluaciones, 1.118 en lugar de 2.179) y ninguna prueba lo vio—.
# ---------------------------------------------------------------------------

VOCABULARIO = RAIZ / "notebooks/datos/resultados_L_sortslice.csv"
ESCALADO = RAIZ / "notebooks/datos/resultados_escalado.csv"


def test_el_barrido_de_l_es_el_de_su_csv(datos):
    if not VOCABULARIO.exists():
        pytest.skip("no está resultados_L_sortslice.csv")
    import numpy as np
    import pandas as pd

    cv = pd.read_csv(VOCABULARIO).query("eval == 'cv'")
    prop = (1 / cv["fold"].nunique()) / (1 - 1 / cv["fold"].nunique())
    publicado = {(p["L"], p["modelo"]): p
                 for p in datos["experimentos"]["vocabulario"]["puntos"]}

    for (L, modelo), g in cv.groupby(["L", "modelo"]):
        p = publicado.get((int(L), modelo))
        assert p, f"falta L={L} con {modelo} en datos.js"
        assert p["mcc"] == pytest.approx(g["MCC"].mean(), abs=5e-5)
        # Nadeau y Bengio: el ingenuo por sqrt(1 + J · n_prueba/n_entrenamiento),
        # con J las evaluaciones de la celda, no los pliegues.
        ingenuo = g["MCC"].std(ddof=1) / np.sqrt(len(g))
        assert p["ee"] == pytest.approx(ingenuo * np.sqrt(1 + len(g) * prop), abs=5e-5), (
            f"L={L} con {modelo}: el error estándar publicado no es el corregido"
        )
        assert p["ee"] > ingenuo * 2, "el error publicado no está corregido por dependencia"


def test_el_escalado_es_el_de_su_csv(datos):
    if not ESCALADO.exists():
        pytest.skip("no está resultados_escalado.csv")
    import pandas as pd

    cv = pd.read_csv(ESCALADO).query("eval == 'cv'")
    publicado = {(f["transformacion"], f["modelo"]): f
                 for f in datos["experimentos"]["escalado"]}

    for (trans, modelo), g in cv.groupby(["transformacion", "modelo"]):
        f = publicado.get((trans, modelo))
        assert f, f"falta «{trans}» con {modelo} en datos.js"
        assert f["mcc"] == pytest.approx(g["MCC"].mean(), abs=5e-5)
        assert f["evaluaciones"] == len(g)
        assert f["sin_converger"] == int(g["sin_converger"].sum() or 0)

    # el hallazgo del que cuelga la 1.4: sin escalar no converge, con escalar sí
    sin = publicado[("sin escalar", "LogReg")]
    assert sin["sin_converger"] == sin["evaluaciones"], (
        "la gráfica afirma que la regresión logística no converge en ningún pliegue sin escalar"
    )


# ---------------------------------------------------------------------------
# El mazo no puede contradecir a la Ruta
#
# `presentacion.qmd` no está bajo `docs/`, así que ninguna búsqueda sobre el
# registro lo encuentra, y el verificador del sitio comprueba enlaces y no
# contenido. El resultado fue que el mazo publicado siguió anunciando «siete
# entradas esperan la definición de la patrocinadora» un día después de que el
# registro se quedara sin ninguna. Esto ata las dos afirmaciones.
# ---------------------------------------------------------------------------

MAZO = RAIZ / "presentacion.qmd"
REGISTRO = RAIZ / "docs/decisiones.md"
MARCA = "necesita su definición"


def _entradas_bloqueadas() -> list[str]:
    """Las entradas cuyo encabezado lleva la clase `.definir`."""
    texto = REGISTRO.read_text(encoding="utf-8")
    return re.findall(r"^#{3,4} ([C\d]\.\d+) · .+?\{#[^}]*\.definir[^}]*\}",
                      texto, re.M)


def test_el_mazo_no_anuncia_entradas_bloqueadas_que_no_existen():
    bloqueadas = _entradas_bloqueadas()
    anuncios = [l.strip() for l in MAZO.read_text(encoding="utf-8").splitlines()
                if MARCA in l and "llevaban" not in l and "quedó" not in l]
    assert not (anuncios and not bloqueadas), (
        f"el mazo dice «{MARCA}» pero el registro no tiene ninguna entrada con"
        f" la clase .definir:\n  " + "\n  ".join(anuncios))


def test_el_mazo_declara_el_estado_que_el_registro_declara():
    """Cada entrada que el mazo enlaza existe y su estado es legible."""
    registro = REGISTRO.read_text(encoding="utf-8")
    estados = dict(re.findall(
        r"^#{3,4} [C\d]\.\d+ · .+?\{#(d[c\d]-\d+)[^}]*\}\n\n\*\*Estado:\*\* *([^·\n]+)",
        registro, re.M))
    citadas = set(re.findall(r"decisiones\.html#(d[c\d]-\d+)",
                             MAZO.read_text(encoding="utf-8")))
    huerfanas = sorted(citadas - set(estados))
    assert not huerfanas, (
        "el mazo enlaza entradas que el registro no tiene: " + ", ".join(huerfanas))


def test_el_mazo_cuenta_los_estados_que_el_registro_tiene():
    """El reparto por estado que anuncia el mazo es el del registro.

    La guarda de arriba solo comprobaba que las entradas enlazadas existieran,
    así que el mazo pudo publicar durante semanas un reparto que no cuadraba
    con ninguna versión del registro: lo encontró una auditoría sumando a mano.
    Aquí se cuentan los encabezados y se comparan con la frase, porque es una
    cifra que cambia cada vez que se decide algo y nadie vuelve a sumarla.

    `revisada` no entra en el reparto a propósito: es un estado que se añade
    sobre otro —una entrada revisada sigue siendo vigente o ratificada— y el
    mazo la cuenta aparte en la misma línea.
    """
    registro = REGISTRO.read_text(encoding="utf-8")
    encabezados = re.findall(r"^#{3,4} [C\d]\.\d+ · .+?\{#d[c\d]-\d+([^}]*)\}",
                             registro, re.M)
    cuenta = {}
    for clases in encabezados:
        for clase in re.findall(r"\.([a-zá-ú]+)", clases):
            cuenta[clase] = cuenta.get(clase, 0) + 1

    mazo = MAZO.read_text(encoding="utf-8")
    frase = re.search(
        r"\*\*(\w+) entradas\*\* en \[la Ruta\][^:]*: *(.+?)\. ", mazo)
    assert frase, "el mazo ya no declara el reparto por estado en la Ruta"
    declarado = {}
    for n, nombre in re.findall(r"(\d+) (ratificadas?|vigentes?|propuestas?"
                                r"|abiertas?|revisadas?)", frase.group(2)):
        declarado[nombre.rstrip("s")] = int(n)

    singular = {"ratificada": "ratificada", "vigente": "vigente",
                "propuesta": "propuesta", "abierta": "abierta"}
    real = {k: v for k, v in cuenta.items() if k in singular}
    assert declarado == real, (
        f"el mazo declara {declarado} y el registro tiene {real}; "
        "son los encabezados de docs/decisiones.md")

    # Y el total, que va en la misma frase y en la diapositiva de la Ruta.
    total = len(encabezados)
    assert sum(real.values()) == total, (
        f"{total} entradas pero {sum(real.values())} con estado de reparto")


def test_el_mazo_cita_el_agrupamiento_que_da_el_generador(datos):
    """Las cifras del agrupamiento del mazo son las de `recursos/datos.js`.

    Es la afirmación metodológica central del proyecto y ya ha estado mal dos
    veces: primero con las cifras de la matriz de 171 columnas, después con una
    razón que dividía dos estimadores distintos. Las dos las encontró alguien
    leyendo, no una comprobación — y la segunda sobrevivió a la corrección de
    la primera. Esta las ata al generador.
    """
    a = datos["agrupamiento"]
    texto = MAZO.read_text(encoding="utf-8")

    # Los dos AUROC no se escriben en el mazo: los pone la gráfica leyendo este
    # mismo archivo, que es por lo que dejaron de poder desviarse. Lo que sí se
    # escribe a mano son las distancias, y son las que hay que atar.
    assert 'data-grafica="particion"' in texto, (
        "la diapositiva del agrupamiento ya no dibuja la gráfica, así que sus "
        "AUROC vuelven a estar escritos a mano: átalos aquí")
    esperadas = {
        "distancia de AUROC entre los dos agrupamientos":
            f"{a['solo_andamio']['auroc'] - a['andamio_esqueleto']['auroc']:.4f}",
        "distancia de AUROC entre modelos": f"{a['entre_modelos']['auroc']:.4f}",
    }
    faltantes = {k: v for k, v in esperadas.items() if v not in texto}
    assert not faltantes, (
        "presentacion.qmd cita cifras de agrupamiento que no son las de "
        "recursos/datos.js: "
        + "; ".join(f"{k} deberia decir {v}" for k, v in faltantes.items()))

    # Y la razon entre lo que mueve el agrupamiento y lo que mueve el modelo,
    # que es donde se colo la comparacion entre estimadores.
    razon = ((a["solo_andamio"]["mcc"] - a["andamio_esqueleto"]["mcc"])
             / a["entre_modelos"]["mcc"])
    assert 3.0 <= razon < 3.5, (
        f"la razon entre agrupamiento y modelo en MCC es {razon:.1f}; el mazo "
        "dice «algo mas de tres veces» y habria que reescribirlo")
