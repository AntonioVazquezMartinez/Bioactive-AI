"""La comparación de etiquetas entre dos variantes, que es donde estuvo el error.

`activo_10um` es `boolean` de pandas y admite nulos, así que comparar dos
versiones con `!=` **no** funciona: `pd.NA != pd.NA` da `pd.NA`, no `False`. La
primera versión de `scripts/medicion_dianas_activacion.py` contaba así 1,184
pares «con etiqueta distinta» donde solo había 4 — el resto eran pares que
seguían sin decidirse de los dos lados. Estas pruebas fijan el comportamiento
correcto: «sin decidir» es un estado comparable, y pasar a él cuenta como
cambio.
"""

import importlib.util
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "src"))
spec = importlib.util.spec_from_file_location(
    "medicion_dianas_activacion", RAIZ / "scripts/medicion_dianas_activacion.py")
med = importlib.util.module_from_spec(spec)
spec.loader.exec_module(med)


def _pares(etiquetas: list) -> pd.DataFrame:
    """Una tabla mínima de pares, con la llave y la etiqueta derivada."""
    return pd.DataFrame({
        "esqueleto": [f"E{i}" for i in range(len(etiquetas))],
        "target_gene": ["PPARG"] * len(etiquetas),
        "activo_10um": pd.array(etiquetas, dtype="boolean"),
    })


def test_sin_decidir_de_los_dos_lados_no_es_un_cambio():
    antes = _pares([None, None, True])
    cambios = med._comparar(antes, antes, "igual")
    assert cambios == (0, 0)


def test_pasar_a_sin_decidir_si_es_un_cambio():
    antes = _pares([True, False])
    despues = _pares([None, False])
    assert med._comparar(antes, despues, "v") == (0, 1)


def test_un_par_que_desaparece_no_se_cuenta_tambien_como_cambio():
    antes = _pares([True, False])
    despues = antes.iloc[:1]
    desaparecen, cambian = med._comparar(antes, despues, "v")
    assert (desaparecen, cambian) == (1, 0)


def test_ausentes_devuelve_las_filas_cuyo_par_ya_no_esta():
    antes = _pares([True, False, None])
    despues = antes.iloc[[0, 2]]
    ausentes = med._ausentes(antes, despues)
    assert ausentes["esqueleto"].tolist() == ["E1"]


def test_la_direccion_de_cada_tipo_esta_declarada_o_no_esta():
    """Un tipo sin dirección cae en «sin_clasificar», no en una por omisión."""
    direcciones = set(med.DIRECCION_DE_TIPO.values())
    assert direcciones == {"activacion", "inhibicion", "afinidad", "ambigua"}
    # Los dos tipos que deciden la medición, cada uno en su dirección.
    assert med.DIRECCION_DE_TIPO["IC50"] == "ambigua"  # depende del ensayo
    assert med.DIRECCION_DE_TIPO["EC50"] == "activacion"
    # `AC50` suena a activación y no lo es: en cribado puede medir en cualquiera
    # de las dos direcciones. Si alguien lo reclasifica, esta prueba lo frena.
    assert med.DIRECCION_DE_TIPO["AC50"] == "ambigua"
    # «sin_contrarias» conserva todo menos lo que contradice; «solo_activacion»
    # exige medir en la dirección. Si eso se invierte, la medición miente.
    assert "inhibicion" not in med.VARIANTES["sin_contrarias"]
    assert med.VARIANTES["solo_activacion"] == ("activacion",)
    # Y «solo_inhibicion» es la que permite tratar los IC50 aparte: tiene que
    # ser la complementaria exacta, o la comparación entre las dos no dice nada.
    assert med.VARIANTES["solo_inhibicion"] == ("inhibicion",)


def test_sobre_cuanta_evidencia_separa_la_medicion_unica_de_las_varias():
    perdidos = pd.DataFrame({
        "n_mediciones": [1, 1, 3],
        "activo_10um": pd.array([True, None, False], dtype="boolean"),
    })
    r = med._sobre_cuanta_evidencia(perdidos)
    assert r == {"pares": 3, "con_una_sola_medicion": 2, "con_dos_o_mas": 1,
                 "hoy_activos": 1}


def test_el_acuerdo_entre_direcciones_solo_mira_donde_las_dos_deciden():
    """Un par sin decidir por un lado no cuenta como discrepancia."""
    clave = {"esqueleto": ["E0", "E1", "E2"], "target_gene": ["PPARG"] * 3}
    activacion = pd.DataFrame(
        {**clave, "activo_10um": pd.array([True, True, None], dtype="boolean")})
    inhibicion = pd.DataFrame(
        {**clave, "activo_10um": pd.array([False, True, False],
                                          dtype="boolean")})
    r = med._acuerdo(activacion, inhibicion)
    assert r["pares_con_las_dos_direcciones"] == 3
    assert r["pares_donde_las_dos_deciden"] == 2
    assert r["pares_donde_discrepan"] == 1


def test_un_ic50_de_union_es_afinidad_y_solo_el_funcional_es_inhibicion():
    """El tipo del ensayo decide la dirección de un IC, no el nombre de la medida."""
    act = pd.DataFrame({
        "activity_type": ["IC50", "IC50", "IC50", "IC50", "EC50", "Ki"],
        "assay_chembl_id": ["A1", "A2", "A3", None, "A1", "A1"],
        "assay_type": [None, None, None, "F", None, None],
    })
    tipos = pd.DataFrame({"assay_type": ["B", "F", "A"], "description": ["", "", ""]},
                         index=["A1", "A2", "A3"])
    base = act["activity_type"].map(med.DIRECCION_DE_TIPO)
    r = med.resolver_ic(act, base, tipos)
    # unión → afinidad; funcional → inhibición; ADME → ambigua; sin id usa el assay_type de la fila
    assert r.tolist() == ["afinidad", "inhibicion", "ambigua", "inhibicion",
                          "activacion", "afinidad"]


def test_un_tipo_b_descrito_como_inhibicion_funcional_se_lee_como_inhibicion():
    """El tipo B es grueso: «Inhibition of PPARgamma… transcriptional activity» es funcional."""
    act = pd.DataFrame({
        "activity_type": ["IC50"] * 5,
        "assay_chembl_id": ["A", "B", "C", "D", "E"],
        "assay_type": [None] * 5,
    })
    ensayos = pd.DataFrame({
        "assay_type": ["B", "B", "B", "B", "F"],
        "description": [
            "Inhibition of PPARgamma assessed as transcriptional activity",   # funcional
            "Displacement of [3H]-rosiglitazone from PPARgamma",              # unión
            "Inhibition of binding of [125I]ligand to the receptor",          # unión pese a «inhibition»
            "PPARgamma LBD in a Lanthascreen assay",                          # sin palabra de inhibir
            "Agonist activity at PPARgamma",                                  # F manda
        ]}, index=["A", "B", "C", "D", "E"])
    base = act["activity_type"].map(med.DIRECCION_DE_TIPO)
    assert med.resolver_ic(act, base, ensayos).tolist() == [
        "inhibicion", "afinidad", "afinidad", "afinidad", "inhibicion"]


def test_los_tipos_ic_son_los_que_el_mapa_deja_ambiguos_y_los_que_se_descargan():
    """Si alguien añade un IC al mapa o a la descarga, los dos scripts tienen que enterarse."""
    spec2 = importlib.util.spec_from_file_location(
        "descarga", Path(__file__).resolve().parents[1] / "scripts/descargar_tipos_ensayo.py")
    desc = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(desc)
    assert set(med.TIPOS_IC) == set(desc.TIPOS_IC)
    assert all(med.DIRECCION_DE_TIPO[t] == "ambigua" for t in med.TIPOS_IC)


def test_la_evidencia_de_un_par_es_activacion_o_lo_que_le_falta():
    f = med.tipo_de_evidencia
    assert f({"activacion", "afinidad"}) == "con activación"
    assert f({"inhibicion"}) == "solo inhibición funcional"
    assert f({"afinidad"}) == "solo afinidad"
    assert f({"ambigua"}) == "solo tipo ambiguo"
    assert f({"afinidad", "inhibicion"}) == "mezcla sin activación"
