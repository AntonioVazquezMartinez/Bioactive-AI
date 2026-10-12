"""Particiones sin fuga: ninguna estructura cruza entre entrenamiento, validación y prueba."""

import numpy as np
import pandas as pd

from src.data_prep.splits import (SIN_ANDAMIO, andamio_murcko, esqueleto_conectividad,
                                  grupos_cv, scaffold_split, verificar_fuga)
from src.features.molecular import a_mol


def _df(filas):
    return pd.DataFrame(filas, columns=["andamio", "esqueleto"])


def _conjunto_sintetico(n_andamios=60, por_andamio=4):
    """Andamios 'A0', 'A1'…; cada tercer andamio comparte esqueleto con el siguiente."""
    filas = []
    for a in range(n_andamios):
        for k in range(por_andamio):
            esq = f"E{a - a % 3}" if a % 3 else f"E{a}"
            filas.append((f"A{a}", esq if k % 2 else f"E{a}"))
    filas += [(SIN_ANDAMIO, f"X{i}") for i in range(10)]
    return _df(filas)


def test_scaffold_split_no_filtra_andamios_ni_esqueletos():
    d = _conjunto_sintetico()
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1)
    informe = verificar_fuga(d)
    assert informe["sin_fuga"], informe
    assert set(d["particion"]) == {"entrenamiento", "validacion", "prueba"}


def test_verificar_fuga_detecta_un_andamio_en_dos_particiones():
    d = _df([("A", "E1"), ("A", "E2"), ("B", "E3")])
    d["particion"] = ["entrenamiento", "prueba", "prueba"]
    informe = verificar_fuga(d)
    assert not informe["sin_fuga"]
    assert informe["andamios_cruzados"] == 1 and informe["ejemplos_andamios"] == ["A"]


def test_verificar_fuga_detecta_un_esqueleto_en_dos_particiones():
    """Dos estereoisómeros (mismo esqueleto) en lados distintos son fuga aunque difiera el andamio."""
    d = _df([("A", "E1"), ("B", "E1")])
    d["particion"] = ["entrenamiento", "prueba"]
    informe = verificar_fuga(d)
    assert not informe["sin_fuga"] and informe["esqueletos_cruzados"] == 1


def test_los_aciclicos_no_cuentan_como_un_andamio_compartido():
    d = _df([(SIN_ANDAMIO, "E1"), (SIN_ANDAMIO, "E2")])
    d["particion"] = ["entrenamiento", "prueba"]
    assert verificar_fuga(d)["sin_fuga"]


def test_andamios_con_esqueleto_comun_caen_juntos():
    d = _df([("A", "E1"), ("B", "E1")] + [(f"C{i}", f"F{i}") for i in range(30)])
    d["particion"] = scaffold_split(d, fraccion_prueba=0.3)
    assert d.particion[0] == d.particion[1]


def test_los_aciclicos_van_adonde_se_pide_y_la_semilla_fija_el_resultado():
    d = _conjunto_sintetico()
    p1 = scaffold_split(d, acíclicos_a="prueba", semilla=7)
    p2 = scaffold_split(d, acíclicos_a="prueba", semilla=7)
    assert (p1 == p2).all()
    assert (p1[d.andamio == SIN_ANDAMIO] == "prueba").all()


def test_particion_con_moleculas_reales():
    smiles = ["c1ccccc1", "Cc1ccccc1", "Oc1ccccc1", "c1ccncc1", "Cc1ccncc1", "c1ccc2ccccc2c1",
              "Cc1ccc2ccccc2c1", "C1CCCCC1", "CC1CCCCC1", "CCO", "CCCC"]
    mols = [a_mol(s) for s in smiles]
    d = pd.DataFrame({"andamio": [andamio_murcko(m) for m in mols],
                      "esqueleto": [esqueleto_conectividad(m) for m in mols]})
    assert andamio_murcko(a_mol("CCO")) == SIN_ANDAMIO
    d["particion"] = scaffold_split(d, fraccion_prueba=0.3, fraccion_validacion=0.1)
    assert verificar_fuga(d)["sin_fuga"]


def test_grupos_cv_junta_andamio_y_esqueleto_y_no_funde_los_aciclicos():
    d = _df([("A", "E1"), ("B", "E1"),            # mismo esqueleto: un grupo
             ("A", "E2"),                          # mismo andamio que la fila 0: ese grupo
             ("C", "E3"),                          # otro grupo
             (SIN_ANDAMIO, "E4"), (SIN_ANDAMIO, "E4"),   # estereoisómeros acíclicos: juntos
             (SIN_ANDAMIO, "E5")])                 # acíclico distinto: aparte
    g = grupos_cv(d)
    assert len({g[0], g[1], g[2]}) == 1
    assert g[3] not in {g[0], g[4], g[6]}
    assert g[4] == g[5] and g[4] != g[6]
    assert isinstance(g, np.ndarray)
