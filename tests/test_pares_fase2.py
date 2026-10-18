"""La etiqueta de la fase 2 se deriva del intervalo, y el intervalo respeta el diccionario."""

import numpy as np
import pandas as pd
import pytest

from src.data_prep.pares_fase2 import (CINCO_CATEGORIAS, a_potencia,
                                       etiqueta_binaria, tabla_de_pares)

# Etanol y benceno: dos SMILES que RDKit parsea y que dan esqueletos distintos.
ETANOL = "CCO"
BENCENO = "c1ccccc1"


def _medicion(smiles=ETANOL, gen="ACHE", relacion="=", valor=1.0, unidad="uM",
              fuente="chembl", categoria="Alzheimer", referencia="R1",
              ensayo="A1", evidencia="concentracion"):
    return {
        "smiles_raw": smiles, "target_gene": gen,
        "activity_relation_used": relacion, "activity_value_used": valor,
        "activity_units_used": unidad, "source": fuente,
        "diana_categoria": categoria, "reference_id": referencia,
        "assay_chembl_id": ensayo, "evidence_kind": evidencia,
    }


def _tabla(*mediciones):
    return tabla_de_pares(pd.DataFrame(list(mediciones)))


def test_la_potencia_es_la_del_pchembl():
    """6 − log10 µM: 1 µM da 6 y 1 nM da 9, como el pChEMBL del diccionario."""
    p = a_potencia(pd.Series([1.0, 1.0, 1000.0]), pd.Series(["uM", "nM", "nM"]))
    assert list(np.round(p, 6)) == [6.0, 9.0, 6.0]


def test_las_unidades_de_masa_no_se_convierten():
    """Sin peso molecular no hay molaridad, así que esas filas no forman par."""
    assert a_potencia(pd.Series([5.0]), pd.Series(["ug.mL-1"])).isna().all()
    assert len(_tabla(_medicion(unidad="ug.mL-1"))) == 0


def test_una_medicion_exacta_colapsa_el_intervalo_a_un_punto():
    t = _tabla(_medicion(valor=1.0, unidad="uM"))
    fila = t.iloc[0]
    assert fila["pActividad"] == pytest.approx(6.0)
    assert fila["limite_inferior"] == pytest.approx(6.0)
    assert fila["limite_superior"] == pytest.approx(6.0)


def test_el_par_agrega_por_mediana_y_no_por_el_valor_mas_potente():
    """Tres mediciones de 6, 6 y 9: la mediana es 6, el máximo sería 9.

    Importa porque la regla de «conservar el valor más potente» sesga hacia la
    clase positiva, que es el primer problema declarado de la propuesta.
    """
    t = _tabla(_medicion(valor=1.0, unidad="uM"),
               _medicion(valor=1.0, unidad="uM"),
               _medicion(valor=1.0, unidad="nM"))
    assert t.iloc[0]["pActividad"] == pytest.approx(6.0)
    assert t.iloc[0]["n_exactas"] == 3
    assert t.iloc[0]["rango_exactas"] == pytest.approx(3.0)


@pytest.mark.parametrize(
    "limite_um, activo_10um, activo_1um",
    [
        # Un «> 10 µM» alcanza para declarar inactivo con los dos umbrales.
        (10.0, False, False),
        # Un «> 1 µM» no dice nada con umbral de 10 µM, y sí con umbral de 1 µM:
        # es exactamente la regla de la sección 7 del diccionario.
        (1.0, None, False),
        # Un «> 100 µM» alcanza para los dos, con más holgura.
        (100.0, False, False),
    ],
)
def test_una_cota_superior_sigue_la_regla_del_diccionario(limite_um, activo_10um,
                                                          activo_1um):
    t = _tabla(_medicion(relacion=">", valor=limite_um, unidad="uM"))
    fila = t.iloc[0]
    assert np.isnan(fila["pActividad"])
    assert fila["limite_inferior"] == -np.inf
    for columna, esperado in (("activo_10um", activo_10um),
                              ("activo_1um", activo_1um)):
        obtenido = fila[columna]
        if esperado is None:
            assert pd.isna(obtenido), f"{columna} debería quedar sin decidir"
        else:
            assert bool(obtenido) is esperado


def test_la_etiqueta_binaria_se_deriva_del_intervalo():
    """Es la propiedad que permite cambiar de umbral sin reconstruir la matriz."""
    pares = pd.DataFrame({"limite_inferior": [6.0, -np.inf, -np.inf, 5.0],
                          "limite_superior": [6.0, 4.0, 6.0, np.inf]})
    assert list(etiqueta_binaria(pares, 10.0)) == [True, False, pd.NA, True]
    assert list(etiqueta_binaria(pares, 1.0)) == [True, False, False, pd.NA]


def test_el_empate_en_el_umbral_se_resuelve_a_favor_de_activo():
    """Un IC50 exacto de 10 µM con umbral de 10 µM es activo; un «> 10 µM» no.

    Los dos tienen la misma relación numérica con el corte y significan lo
    contrario. Lo que los separa es que el censurado no tiene cota inferior.
    """
    exacto = _tabla(_medicion(valor=10.0, unidad="uM"))
    assert bool(exacto.iloc[0]["activo_10um"]) is True
    censurado = _tabla(_medicion(relacion=">", valor=10.0, unidad="uM"))
    assert bool(censurado.iloc[0]["activo_10um"]) is False


def test_la_dispersion_entre_exactas_no_es_conflicto():
    """Dos mediciones a los lados del corte son ruido, no contradicción."""
    t = _tabla(_medicion(valor=2.0, unidad="uM"),
               _medicion(valor=50.0, unidad="uM"))
    assert not t.iloc[0]["conflicto"]
    assert t.iloc[0]["rango_exactas"] > 1


def test_una_cota_que_contradice_la_mediana_si_es_conflicto():
    """Las exactas dicen 10 µM y un «< 0.001 µM» exige mucha más potencia."""
    t = _tabla(_medicion(valor=10.0, unidad="uM"),
               _medicion(relacion="<", valor=0.001, unidad="uM"))
    assert t.iloc[0]["conflicto"]


def test_los_estratos_son_disjuntos_y_nombran_la_procedencia():
    t = _tabla(_medicion(fuente="chembl"),
               _medicion(smiles=BENCENO, fuente="npass"),
               _medicion(smiles=BENCENO, gen="MAOA", fuente="npass"),
               _medicion(smiles=BENCENO, gen="MAOA", fuente="chembl"))
    estratos = dict(zip(t["esqueleto"] + "|" + t["target_gene"], t["estrato"]))
    assert sorted(set(estratos.values())) == ["mixto", "solo_chembl", "solo_npass"]


def test_los_inactivos_por_texto_quedan_fuera():
    """Su «> 10 µM» lo asignó quien armó el archivo, no el ensayo original."""
    assert len(_tabla(_medicion(evidencia="inactivo_por_texto",
                                relacion=">", valor=10.0))) == 0


def test_solo_entran_las_cinco_categorias_ratificadas():
    assert len(_tabla(_medicion(categoria="Epilepsia"))) == 0
    assert len(_tabla(_medicion(categoria="Huntington"))) == 0
    for categoria in CINCO_CATEGORIAS:
        assert len(_tabla(_medicion(categoria=categoria))) == 1


def test_una_fila_sin_gen_no_forma_par():
    assert len(_tabla(_medicion(gen=None))) == 0


def test_la_potencia_fuera_del_rango_plausible_no_entra():
    """Hay IC50 de 1e-6 nM y de 4.4e16 nM: la unidad viene bien y el valor no."""
    t = _tabla(_medicion(valor=1e-6, unidad="nM"), _medicion(valor=2.0, unidad="uM"))
    assert t.iloc[0]["n_exactas"] == 1
    assert t.iloc[0]["pActividad"] == pytest.approx(6 - np.log10(2.0))
