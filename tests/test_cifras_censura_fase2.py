"""Censurada es lo que `SoloExactas` tira, y el desglose se cuenta por estrato.

El valor de estas pruebas está en el primer test: fija que la definición de
«exacta» del script es la misma que la del envoltorio con el que se compara el
AFT. Si `SoloExactas` cambia de criterio, los cinco conteos que el 05b publica
dejan de medir lo que su prosa dice y esta prueba falla.
"""

import importlib.util
from pathlib import Path

import numpy as np

from src.models.baseline_regresion import SoloExactas

RAIZ = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "cifras_censura_fase2", RAIZ / "scripts/cifras_censura_fase2.py")
_c = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_c)


class _Espia:
    """Un modelo que solo anota con cuántas filas lo mandaron ajustar."""

    def __init__(self):
        self.vistas = None

    def fit(self, X, y):
        self.vistas = len(y)
        return self


def test_exacta_es_lo_mismo_que_entrena_soloexactas():
    # Un punto, una cota superior, una inferior y un intervalo abierto.
    inferior = np.array([5.0, -np.inf, 6.0, 4.0])
    superior = np.array([5.0, 5.0, np.inf, 7.0])
    espia = _Espia()
    SoloExactas(espia).fit(np.zeros((4, 1)), inferior, superior)

    exacta = _c.es_exacta(inferior, superior)
    assert list(exacta) == [True, False, False, False]
    assert espia.vistas == int(exacta.sum())


def test_el_desglose_separa_filas_censuradas_y_exactas_por_estrato():
    estrato = np.array(["solo_chembl"] * 3 + ["solo_npass"] * 2)
    inferior = np.array([5.0, 5.0, -np.inf, 5.0, -np.inf])
    superior = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
    tabla = _c.censura_por_estrato(estrato, inferior, superior).set_index("estrato")

    assert tabla.loc["solo_chembl", "filas"] == 3
    assert tabla.loc["solo_chembl", "exactas"] == 2
    assert tabla.loc["solo_chembl", "censuradas"] == 1
    assert tabla.loc["solo_npass", "pct_censuradas"] == 50.0


def test_los_estratos_salen_en_el_orden_del_cuaderno():
    estrato = np.array(["mixto", "solo_npass", "solo_chembl"])
    inferior = superior = np.array([5.0, 5.0, 5.0])
    tabla = _c.censura_por_estrato(estrato, inferior, superior)
    assert list(tabla["estrato"]) == ["solo_chembl", "solo_npass", "mixto"]


def test_un_estrato_que_no_esta_en_la_lista_no_se_pierde():
    estrato = np.array(["solo_chembl", "inventado"])
    inferior = superior = np.array([5.0, 5.0])
    tabla = _c.censura_por_estrato(estrato, inferior, superior)
    assert set(tabla["estrato"]) == {"solo_chembl", "inventado"}
    assert tabla["filas"].sum() == 2
