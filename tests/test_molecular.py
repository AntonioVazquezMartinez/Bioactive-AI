"""SortAndSlice y limpiar_descriptores: lo que el notebook 02 da por hecho."""

from collections import Counter

import numpy as np
import pandas as pd
import pytest

from src.features.molecular import SortAndSlice, a_mol, limpiar_descriptores


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
