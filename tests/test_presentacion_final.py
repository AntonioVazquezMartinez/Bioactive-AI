"""La presentación final (#303): 13 diapositivas para 30 minutos, cada una con sus notas y dentro del
presupuesto de texto que ya mide `test_armar_deck` (techo de 1,761 caracteres por diapositiva)."""
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


def test_son_trece_diapositivas_en_el_hilo_y_dos_de_respaldo():
    hilo, respaldo = _diapositivas()
    assert len(hilo) == 13, f"{len(hilo)} diapositivas en el hilo; la propuesta del #303 son 13"
    assert len(respaldo) == 2


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
