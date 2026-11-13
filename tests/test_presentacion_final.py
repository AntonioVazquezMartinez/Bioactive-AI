"""La presentación final (#303): 16 diapositivas para 15 minutos de charla y 10 de preguntas, cada una con sus notas y dentro del
presupuesto de texto que ya mide `test_armar_deck` (techo de 1,761 caracteres por diapositiva).

La propuesta del #303 eran 13. La catorce es «Cómo se vuelve números una molécula»: el mazo no decía en
ninguna parte cómo se convierte un SMILES en columnas, que es el Avance 2 completo. Se paga con minuto y
medio recortado de otras tres del mismo bloque, así que el reparto de #303 no cambia.

Las de respaldo son 6: la figura de rareza salió del hilo porque mide la ventaja sobre la línea base
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


def test_son_dieciseis_diapositivas_en_el_hilo_y_seis_de_respaldo():
    hilo, respaldo = _diapositivas()
    assert len(hilo) == 16, f"{len(hilo)} diapositivas en el hilo; son 16 (las 13 del #303 más tres: cómo se vuelve números una molécula, qué pesa en cada fase y el modelo de potencia)"
    assert len(respaldo) == 6


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
    """13 minutos de diapositivas, más 1.5 del resumen en Zoom y 0.5 de transiciones, son los 15 de charla.

    Nadie lo estaba midiendo: al añadir la diapositiva de la fase 2 el hilo se habría ido a 14 sin que
    fallara nada. Si esta prueba falla, hay que rebalanceárselo a alguien, no subir el número.
    """
    hilo, _ = _diapositivas()
    minutos = []
    for d in hilo:
        m = re.search(r"\*\*\w+ · ([\d.]+) min", d)
        assert m, f"«{d.splitlines()[0]}» no dice cuántos minutos dura"
        minutos.append(float(m.group(1)))
    assert sum(minutos) == 13.0, (
        f"el hilo suma {sum(minutos)} minutos y el presupuesto son 13.0; "
        "si una diapositiva crece, otra tiene que bajar")
