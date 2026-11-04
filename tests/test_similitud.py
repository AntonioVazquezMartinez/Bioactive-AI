"""La similitud y los grupos por similitud tienen que dar lo que la escalera registró."""
import numpy as np
import pytest

from src.features.similitud import (grupos_por_similitud, huellas, matriz_densa,
                                    matriz_dispersa, resumen_grupos, similitud_al_vecino,
                                    similitud_al_vecino_de)
from src.models.tareas import PROCESADOS, cargar

SMILES = ["CCO", "CCCO", "CCCCO", "c1ccccc1", "Cc1ccccc1", "CCc1ccccc1", "CC(=O)O", "CCC(=O)O",
          "C1CCCCC1", "CC1CCCCC1", "NCCN", "NCCCN"]


def test_smiles_ilegible_falla_con_su_posicion():
    with pytest.raises(ValueError, match="posición 1"):
        huellas(["CCO", "esto no es un smiles"])


def test_densa_es_simetrica_con_diagonal_cero_y_en_0_1():
    S = matriz_densa(huellas(SMILES))
    assert np.allclose(S, S.T)
    assert np.all(np.diag(S) == 0)
    assert S.min() >= 0 and S.max() <= 1


def test_dispersa_y_densa_dan_los_mismos_grupos_en_cada_umbral():
    fps = huellas(SMILES)
    S = matriz_densa(fps)
    D = matriz_dispersa(fps, 0.2)
    for u in (0.2, 0.3, 0.5, 0.8):
        a, b = grupos_por_similitud(S, u), grupos_por_similitud(D, u)
        # mismas particiones aunque las etiquetas numéricas puedan permutarse
        assert len(set(a)) == len(set(b))
        assert len(set(zip(a, b, strict=True))) == len(set(a))


def test_grupos_son_monotonos_apretar_el_umbral_nunca_junta():
    S = matriz_densa(huellas(SMILES))
    n = [len(set(grupos_por_similitud(S, u))) for u in (0.2, 0.4, 0.6, 0.9)]
    assert n == sorted(n)          # más umbral, más grupos


def test_vecino_mas_cercano_coincide_con_y_sin_matriz():
    fps = huellas(SMILES)
    S = matriz_densa(fps)
    ajuste, val = np.arange(0, 8), np.arange(8, 12)
    assert np.allclose(similitud_al_vecino(S, ajuste, val), similitud_al_vecino_de(fps, ajuste, val), atol=1e-6)


@pytest.mark.skipif(not (PROCESADOS / "bbb_meta.parquet").exists(),
                    reason="faltan los datos procesados (no se versionan)")
def test_reproduce_los_grupos_de_la_escalera_registrada():
    """Corrida 2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad: 1413, 1017 y 631 grupos."""
    smiles = cargar("permeabilidad", estratos="tamano").meta["SMILES"].tolist()
    fps = huellas(smiles)
    D = matriz_dispersa(fps, 0.4)
    esperado = {0.6: 1413, 0.5: 1017, 0.4: 631}
    for u, grupos in esperado.items():
        assert resumen_grupos(grupos_por_similitud(D, u))["grupos"] == grupos, u


def test_vecino_matricial_coincide_con_la_version_por_huellas_y_con_la_matriz_densa():
    from src.features.similitud import bits_como_matriz, similitud_al_vecino_matricial
    fps = huellas(SMILES)
    S = matriz_densa(fps)
    A = bits_como_matriz(fps)
    ajuste, val = np.arange(0, 8), np.arange(8, 12)
    a = similitud_al_vecino_matricial(A, ajuste, val, bloque=3)     # bloque chico: ejerce el ciclo
    assert np.allclose(a, similitud_al_vecino_de(fps, ajuste, val), atol=1e-6)
    assert np.allclose(a, similitud_al_vecino(S, ajuste, val), atol=1e-6)


def test_vecino_matricial_de_una_molecula_con_su_copia_es_uno():
    from src.features.similitud import bits_como_matriz, similitud_al_vecino_matricial
    A = bits_como_matriz(huellas(["CCO", "CCO", "c1ccccc1"]))
    assert similitud_al_vecino_matricial(A, np.array([0]), np.array([1]))[0] == pytest.approx(1.0)
