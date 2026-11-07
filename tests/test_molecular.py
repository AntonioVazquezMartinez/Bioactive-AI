"""SortAndSlice y limpiar_descriptores: lo que el notebook 02 da por hecho."""

from collections import Counter

import numpy as np
import pandas as pd
import pytest

from src.features.molecular import (CONTEOS_ESTEREO, SortAndSlice, a_mol, conteos_estereo,
                                    descriptores_rdkit, limpiar_descriptores)


def _mols(*smiles):
    return [a_mol(s) for s in smiles]


def test_el_vocabulario_sale_solo_del_entrenamiento():
    entrenamiento = _mols("c1ccccc1", "Cc1ccccc1", "CCO")
    prueba = _mols("c1ccncc1C(=O)N", "FC(F)(F)c1ccc(Cl)cc1")
    ss = SortAndSlice(n_bits=2048).fit(entrenamiento)
    vocabulario = list(ss.vocabulario)

    X = ss.transform(prueba)
    assert ss.vocabulario == vocabulario                      # transformar no lo toca
    assert X.shape == (2, len(vocabulario))                   # ni agrega columnas
    # las subestructuras que solo existen en la prueba no tienen columna: cobertura < 1
    assert ss.cobertura(prueba) < 1.0
    # ajustar con la prueba sí cambiaría el vocabulario: la separación importa
    assert SortAndSlice(n_bits=2048).fit(entrenamiento + prueba).vocabulario != vocabulario


def test_conserva_las_mas_frecuentes_y_es_reproducible():
    mols = _mols("c1ccccc1", "c1ccccc1", "c1ccccc1", "Oc1ccccc1")
    a = SortAndSlice(n_bits=5).fit(mols)
    b = SortAndSlice(n_bits=5).fit(mols)
    assert a.vocabulario == b.vocabulario and len(a.vocabulario) == 5
    cuenta = Counter(i for m in mols for i in a._identificadores(m))
    frecuencias = [cuenta[i] for i in a.vocabulario]
    assert frecuencias == sorted(frecuencias, reverse=True)   # de más a menos frecuente
    assert min(frecuencias) >= max(c for i, c in cuenta.items() if i not in a.vocabulario)


def test_transform_exige_fit():
    with pytest.raises(RuntimeError):
        SortAndSlice().transform(_mols("CCO"))


def test_transform_es_binario():
    ss = SortAndSlice(n_bits=64)
    X = ss.fit_transform(_mols("c1ccccc1", "CCO"))
    assert X.dtype == np.uint8 and set(np.unique(X)) <= {0, 1}


def test_limpiar_descriptores_descarta_cada_motivo_y_conserva_lo_util():
    desc = pd.DataFrame({
        "constante": [1.0, 1.0, 1.0],
        "con_nan": [1.0, np.nan, 3.0],
        "con_inf": [1.0, np.inf, 3.0],
        "Ipc": [1.0, 2.0, 1e41],           # finito en float64, desborda float32
        "bueno": [1.0, 2.0, 3.0],
    })
    limpio, motivos = limpiar_descriptores(desc, verbose=False)
    assert list(limpio.columns) == ["bueno"]
    assert motivos["constantes"] == ["constante"]
    assert motivos["con_nan"] == ["con_nan"]
    assert "con_inf" in motivos["no_finitas"]       # un NaN también cuenta como no finito
    assert motivos["fuera_de_float32"] == ["Ipc"]              # y no se cuenta dos veces


def test_limpiar_descriptores_deja_un_marco_que_sklearn_acepta():
    from sklearn.ensemble import RandomForestClassifier
    desc = pd.DataFrame({"Ipc": [1.0, 2.0, 1e41, 4.0], "x": [0.1, 0.5, 0.2, 0.9]})
    limpio, _ = limpiar_descriptores(desc, verbose=False)
    RandomForestClassifier(n_estimators=3).fit(limpio, [0, 1, 0, 1])   # no lanza


# --- conteos_estereo: lo que los 217 descriptores no distinguen (1.8) -------------------------

ALANINA = ("C[C@@H](N)C(=O)O", "C[C@H](N)C(=O)O")   # los dos enantiómeros


def test_los_217_descriptores_no_distinguen_dos_enantiomeros():
    """La premisa de la entrada: el arreglo hace falta porque ninguna de las 217 columnas cambia."""
    desc = descriptores_rdkit(_mols(*ALANINA))
    assert desc.shape[1] == 217
    assert not (desc.iloc[0] != desc.iloc[1]).any()
    # y las dos columnas de estereoquímica que sí existen cuentan, no configuran
    assert desc["NumAtomStereoCenters"].tolist() == [1, 1]
    assert desc["NumUnspecifiedAtomStereoCenters"].tolist() == [0, 0]


def test_dos_enantiomeros_intercambian_los_conteos_r_y_s():
    c = conteos_estereo(_mols(*ALANINA))
    assert list(c.columns) == list(CONTEOS_ESTEREO)
    assert c[["n_R", "n_S"]].values.tolist() in ([[1, 0], [0, 1]], [[0, 1], [1, 0]])
    assert (c[["n_E", "n_Z"]] == 0).all().all()


def test_una_molecula_sin_estereoquimica_da_cuatro_ceros():
    c = conteos_estereo(_mols("CCO", "c1ccccc1"))
    assert (c == 0).all().all()


def test_un_centro_sin_declarar_no_se_infiere():
    """`CC(N)C(=O)O` no dice la configuración: no cuenta ni como R ni como S."""
    c = conteos_estereo(_mols("CC(N)C(=O)O"))
    assert c.iloc[0].tolist() == [0, 0, 0, 0]


def test_los_enlaces_e_y_z_se_cuentan_por_separado():
    c = conteos_estereo(_mols(r"C/C=C/C", r"C/C=C\C", "CC=CC"))
    assert c["n_E"].tolist() == [1, 0, 0]
    assert c["n_Z"].tolist() == [0, 1, 0]


def test_no_reescribe_las_etiquetas_de_la_molecula_que_recibe():
    """`MolFromSmiles` ya deja `_CIPCode` puesto por el asignador heredado, y en 104 de las 6,306
    moléculas de la fase 1 no coincide con `rdCIPLabeler`. Se etiqueta una copia para que el
    llamador conserve las etiquetas de RDKit y no las de esta función."""
    def etiquetas(m):
        return {a.GetIdx(): a.GetProp("_CIPCode") for a in m.GetAtoms() if a.HasProp("_CIPCode")}

    mol = _mols(ALANINA[0])[0]
    antes = etiquetas(mol)
    assert antes, "MolFromSmiles ya debería haber etiquetado el centro"
    conteos_estereo([mol])
    assert etiquetas(mol) == antes
