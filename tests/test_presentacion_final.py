"""La presentación final (#303): 15 diapositivas para 15 minutos de charla y 10 de preguntas, cada una con sus notas y dentro del
presupuesto de texto que ya mide `test_armar_deck` (techo de 1,761 caracteres por diapositiva).

La propuesta del #303 eran 13. La catorce es «Cómo se vuelve números una molécula»: el mazo no decía en
ninguna parte cómo se convierte un SMILES en columnas, que es el Avance 2 completo. Se paga con minuto y
medio recortado de otras tres del mismo bloque, así que el reparto de #303 no cambia.

La figura de rareza salió del hilo y quedó en el respaldo porque mide la ventaja sobre la línea base
mientras la diapositiva de la escalera habla de AUROC, y las dos cantidades juntas confunden."""
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MAZO = RAIZ / "presentacion-final.qmd"
TECHO = 1761


def _diapositivas():
    texto = MAZO.read_text(encoding="utf-8")
    cuerpo = texto.split("\n---\n", 2)[-1]
    principal, _, respaldo = cuerpo.partition("\n# Respaldo")
    trozos = re.split(r"^## ", principal, flags=re.M)[1:]
    return trozos, re.split(r"^## ", respaldo, flags=re.M)[1:]


def test_son_quince_diapositivas_en_el_hilo_y_nueve_de_respaldo():
    hilo, respaldo = _diapositivas()
    assert len(hilo) == 15, f"{len(hilo)} diapositivas en el hilo; son 15"
    assert len(respaldo) == 9


def test_cada_diapositiva_del_hilo_trae_notas_con_quien_la_presenta():
    for d in _diapositivas()[0]:
        titulo = d.splitlines()[0]
        assert ".notes" in d, f"«{titulo}» no trae notas"
        assert re.search(r"\*\*(Antonio|Pame|Art) · ", d), f"«{titulo}» no dice quién la presenta"


def test_ninguna_diapositiva_pasa_el_techo_de_texto():
    hilo, respaldo = _diapositivas()
    for d in hilo + respaldo:
        visible = re.sub(r"::: \{\.notes\}.*?\n:::", "", d, flags=re.S)
        assert len(visible) <= TECHO, f"«{d.splitlines()[0]}» tiene {len(visible)} caracteres"


def test_las_figuras_existen():
    texto = MAZO.read_text(encoding="utf-8")
    for ruta in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", texto):
        assert (RAIZ / ruta).exists(), f"falta la figura {ruta}"


def test_el_mazo_no_repite_lo_que_se_retiro():
    texto = MAZO.read_text(encoding="utf-8").lower()
    for frase in ("ocho veces", "lista ordenada", "catorce"):
        assert frase not in texto, f"«{frase}» ya se retiró del artículo"


def test_los_minutos_del_hilo_suman_el_presupuesto():
    """12 minutos de diapositivas, más 1.5 del resumen en Zoom y 0.5 de transiciones, dejan un minuto de margen en los 15 de charla.

    Nadie lo estaba midiendo: al añadir la diapositiva de la fase 2 el hilo se habría ido a 14 sin que
    fallara nada. Si esta prueba falla, hay que rebalanceárselo a alguien, no subir el número.
    """
    hilo, _ = _diapositivas()
    minutos = []
    for d in hilo:
        m = re.search(r"\*\*\w+ · ([\d.]+) min", d)
        assert m, f"«{d.splitlines()[0]}» no dice cuántos minutos dura"
        minutos.append(float(m.group(1)))
    assert sum(minutos) == 12.0, (
        f"el hilo suma {sum(minutos)} minutos y el presupuesto son 12.0; "
        "si una diapositiva crece, otra tiene que bajar")


def test_la_tabla_de_la_escalera_es_la_de_la_corrida():
    """Los 18 números de la tabla salen de `2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`.

    La columna de AUROC entró después que las otras dos (es la que dibuja la figura de al lado, y sin
    ella la tabla y la curva contaban cosas distintas). Tres copias a mano de la misma corrida es como
    se desincronizó el 1,048 en doce archivos, así que aquí se comparan contra el JSON.
    """
    import json

    corrida = json.loads((RAIZ / "experimentos" / "2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad"
                          / "metricas.json").read_text(encoding="utf-8"))["e1_escalera"]
    peldanos = {p["agrupacion"]: p for p in corrida}
    filas = {"Al azar": "1 al azar", "Por andamio": "3 por andamio",
             "Andamio + esqueleto": "4 andamio + esqueleto (actual)",
             "Tanimoto < 0.6": "5 similitud ≥ 0.6", "Tanimoto < 0.5": "5 similitud ≥ 0.5",
             "Tanimoto < 0.4": "5 similitud ≥ 0.4"}
    texto = MAZO.read_text(encoding="utf-8")
    for etiqueta, clave in filas.items():
        p = peldanos[clave]
        linea = next((x for x in texto.splitlines() if x.startswith(f"| {etiqueta} |")), None)
        assert linea, f"la tabla de la escalera no tiene la fila «{etiqueta}»"
        celdas = [c.strip().replace("**", "") for c in linea.strip("| \n").split("|")]
        assert len(celdas) == 4, f"«{etiqueta}» no tiene las cuatro columnas: {linea}"
        for valor, clave_corrida in zip(celdas[1:], ("vecino_mas_cercano", "auroc_svm_rbf", "mcc_svm_rbf"),
                                        strict=True):
            # el margen es media unidad del último decimal que la tabla enseña: el JSON guarda 0.7515 y
            # 0.901, y la tabla redondea a 0.752 y 0.90 como el resto del repositorio
            margen = 0.5 * 10 ** -len(valor.partition(".")[2]) + 1e-6
            assert abs(float(valor) - p[clave_corrida]) <= margen, (
                f"«{etiqueta}», {clave_corrida}: la tabla dice {valor} y la corrida {p[clave_corrida]}")


def _identificador(titulo: str) -> str:
    """El id que pandoc le da a un título, que es el que usa reveal en la dirección (`#/id`)."""
    titulo = re.sub(r"\{[^}]*\}", "", titulo).strip().lower()
    titulo = re.sub(r"[^\w\s\-.]", "", titulo)
    return "-".join(titulo.split())


def test_cada_liga_del_indice_del_respaldo_lleva_a_una_diapositiva():
    """El índice del respaldo enlaza por el id de cada título: renombrar una diapositiva sin tocar el índice rompe la
    liga en silencio, y se descubre en la sala, durante las preguntas."""
    texto = MAZO.read_text(encoding="utf-8")
    ids = {_identificador(m.group(1)) for m in re.finditer(r"^## (.+)$", texto, flags=re.M)}
    # `(#id)` y no `(#/id)`: Quarto ya antepone el `/` de reveal al renderizar, y con dos quedaba `#//id`
    ligas = re.findall(r"\]\(#([^/)][^)]*)\)", texto)
    assert len(ligas) >= 8, "el índice del respaldo debería enlazar a las nueve diapositivas"
    rotas = [liga for liga in ligas if liga not in ids]
    assert not rotas, f"estas ligas no llevan a ninguna diapositiva: {rotas}"


def test_la_navegacion_es_lineal_para_que_las_flechas_recorran_el_respaldo():
    """Sin `navigation-mode: linear` el respaldo es una pila vertical y la flecha izquierda sale de ella a las conclusiones."""
    assert "navigation-mode: linear" in MAZO.read_text(encoding="utf-8")
