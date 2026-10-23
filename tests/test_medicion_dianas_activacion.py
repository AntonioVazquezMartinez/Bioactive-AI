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
    assert med.DIRECCION_DE_TIPO["IC50"] == "inhibicion"
    assert med.DIRECCION_DE_TIPO["EC50"] == "activacion"
    # «sin_contrarias» conserva todo menos lo que contradice; «solo_activacion»
    # exige medir en la dirección. Si eso se invierte, la medición miente.
    assert "inhibicion" not in med.VARIANTES["sin_contrarias"]
    assert med.VARIANTES["solo_activacion"] == ("activacion",)
    # Y «solo_inhibicion» es la que permite tratar los IC50 aparte: tiene que
    # ser la complementaria exacta, o la comparación entre las dos no dice nada.
    assert med.VARIANTES["solo_inhibicion"] == ("inhibicion",)


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
