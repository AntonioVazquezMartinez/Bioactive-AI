"""La cobertura del contexto del ensayo se cuenta por par, y `n.a.` no es una línea celular."""

import importlib.util
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "cifras_contexto_ensayo", RAIZ / "scripts/cifras_contexto_ensayo.py")
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


def _fila(esqueleto, gen, tejido=None, celula=None, formato=None):
    return {"esqueleto": esqueleto, "target_gene": gen, "assay_tissue_raw": tejido,
            "assay_cell_type_raw": celula, "assay_format": formato}


def test_un_par_tiene_el_dato_si_alguna_medicion_lo_trae():
    filas = pd.DataFrame([_fila("A", "ACHE"), _fila("A", "ACHE", tejido="Brain"),
                          _fila("B", "ACHE")])
    cob = _c.cobertura_por_par(filas).set_index("esqueleto")
    assert cob.loc["A", "tejido"] and not cob.loc["B", "tejido"]
    assert cob.loc["A", "alguno"] and not cob.loc["B", "alguno"]


def test_la_celula_n_a_no_cuenta_como_linea_celular():
    filas = pd.DataFrame([_fila("A", "ACHE", celula="n.a."),
                          _fila("B", "ACHE", celula="SH-SY5Y")])
    cob = _c.cobertura_por_par(filas).set_index("esqueleto")
    assert not cob.loc["A", "celula"] and cob.loc["B", "celula"]


def test_el_mismo_compuesto_en_dos_dianas_son_dos_pares():
    filas = pd.DataFrame([_fila("A", "ACHE", tejido="Brain"), _fila("A", "MAOB")])
    cob = _c.cobertura_por_par(filas)
    assert len(cob) == 2
    assert cob.set_index("target_gene").loc["MAOB", "tejido"] == False  # noqa: E712


def test_una_diana_con_un_solo_formato_no_se_compara():
    exactas = pd.DataFrame({
        "target_gene": ["A"] * 20 + ["B"] * 20,
        "assay_format": ["cell-based format"] * 10 + ["tissue-based format"] * 10
                        + ["cell-based format"] * 20,
        "pActividad": [5.0] * 10 + [6.5] * 10 + [5.0] * 20})
    dos = _c.dianas_con_dos_formatos(exactas, minimo=10)
    assert list(dos["diana"]) == ["A"] and dos.loc[0, "rango_pActividad"] == 1.5
