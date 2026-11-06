"""Los modelos finales guardados se pueden usar con SMILES nuevos y reproducen lo que se entrenó.

Lo que estas pruebas atan, en el orden en que se rompería:

1. los artefactos de `models/finales/` existen y cargan (si no, el cuaderno de la patrocinadora no corre);
2. **reproducen las predicciones de referencia** que `scripts/entrenar_finales.py` guardó en `meta.json`, sin
   necesitar los datos de entrenamiento (así se detecta una versión de librería que cambie las cifras);
3. los descriptores que se calculan desde un SMILES **son los mismos que se usaron para entrenar** (esta prueba sí
   necesita `data/processed/`, que no se versiona, y se salta sin él);
4. un SMILES ilegible no rompe a los demás y sale con su motivo;
5. el entrenamiento no toca la prueba reservada.
"""
import json
import re

import numpy as np
import pandas as pd
import pytest

from src import inferencia

RAIZ = inferencia.RAIZ
TIENE_ARTEFACTOS = not inferencia.faltan_artefactos()
con_artefactos = pytest.mark.skipif(not TIENE_ARTEFACTOS, reason="faltan los artefactos de models/finales/")
procesados = pytest.mark.skipif(not (RAIZ / "data/processed/bbb_descriptores_filtrados_sin_normalizar.parquet").exists(),
                                reason="faltan los datos procesados (no se versionan)")


@pytest.fixture(scope="module")
def modelos():
    return inferencia.cargar()


@con_artefactos
def test_los_artefactos_cargan_con_las_columnas_esperadas(modelos):
    assert len(modelos.columnas_fase1) == 151
    assert len(modelos.columnas_fase2) == 201
    assert len(modelos.dianas) == 26
    assert modelos.meta["filas"] == {"fase1": 6306, "fase2": 56241}
    assert modelos.huellas_fase1.shape == (6306, 256)               # 2048 bits empaquetados


@con_artefactos
def test_reproducen_las_predicciones_de_referencia_sin_los_datos(modelos):
    ref = modelos.meta["verificacion"]
    r = inferencia.predecir(ref["smiles"], modelos)
    tol = ref["tolerancia"]
    assert np.allclose(r["p_bbb_mas"], ref["p_bbb_mas"], atol=tol)
    for d in ref["dianas_verificadas"]:
        assert np.allclose(r[f"pActividad_{d}"], ref["pActividad"][d], atol=tol), d


@con_artefactos
def test_las_probabilidades_son_probabilidades_y_no_se_corta_ninguna(modelos):
    r = inferencia.predecir(["Cn1cnc2c1c(=O)n(C)c(=O)n2C", "CN1CCC[C@H]1c1cccnc1"], modelos)
    assert r["p_bbb_mas"].between(0, 1).all()
    assert not any("clase" in c.lower() or "bbb_mas_" in c for c in r.columns)     # nada de «BBB+/BBB−» a 0.5


@con_artefactos
def test_un_smiles_ilegible_no_rompe_a_los_demas(modelos):
    r = inferencia.predecir(["Cn1cnc2c1c(=O)n(C)c(=O)n2C", "esto no es un smiles", "", "CCO"], modelos)
    assert list(r["smiles"]) == ["Cn1cnc2c1c(=O)n(C)c(=O)n2C", "esto no es un smiles", "", "CCO"]
    assert r.loc[[0, 3], "p_bbb_mas"].notna().all()
    assert r.loc[[1, 2], "p_bbb_mas"].isna().all()
    assert (r.loc[[1, 2], "motivo"] == "SMILES ilegible").all()
    assert not r.loc[[1, 2], "aviso_extrapolacion"].any()


@con_artefactos
def test_un_compuesto_de_entrenamiento_queda_a_similitud_uno_y_uno_lejano_avisa(modelos):
    visto = modelos.meta["verificacion"]["smiles"][:3]
    r = inferencia.predecir(visto + ["C"], modelos)            # el metano no se parece a nada de lo entrenado
    assert (r.loc[:2, "similitud_fase1"] > 0.999).all()
    assert bool(r.loc[3, "aviso_extrapolacion"])


def test_las_derivadas_de_la_fase_1_son_las_del_avance_2():
    """`regla_2p` y `tpsa_por_mw` no salen de RDKit: se derivaron de TPSA, HBD y MolWt."""
    cols = ["TPSA", "NumHDonors", "MolWt", "regla_2p", "tpsa_por_mw"]
    d, motivo = inferencia.descriptores(["CCO", "Oc1ccccc1O"], cols)
    assert (motivo == "").all()
    assert d.loc[0, "regla_2p"] == 1.0          # etanol: TPSA 20 y un donador
    assert d.loc[1, "regla_2p"] == 0.0          # catecol: dos donadores
    assert d.loc[1, "NumHDonors"] == 2
    assert d["tpsa_por_mw"].tolist() == pytest.approx((d["TPSA"] / d["MolWt"]).tolist())


@procesados
@pytest.mark.parametrize("fase", [1, 2])
def test_los_descriptores_desde_smiles_son_los_que_se_usaron_para_entrenar(fase):
    p = RAIZ / "data/processed"
    rng = np.random.default_rng(0)
    if fase == 1:
        meta = pd.read_parquet(p / "bbb_meta.parquet")
        d = pd.read_parquet(p / "bbb_descriptores_filtrados_sin_normalizar.parquet")
        smiles, columnas, guardado = meta["SMILES"], list(d.columns), d
    else:
        d = pd.read_parquet(p / "fase2_descriptores_limpios.parquet")
        columnas = [c for c in d.columns if c != "smiles"]
        smiles, guardado = d["smiles"], d[columnas]
    idx = rng.choice(len(smiles), 40, replace=False)
    mio, motivo = inferencia.descriptores(smiles.iloc[idx].tolist(), columnas)
    assert (motivo == "").all()
    assert np.array_equal(mio.to_numpy(np.float32), guardado.iloc[idx].to_numpy(np.float32))


def test_el_entrenamiento_no_toca_la_prueba_reservada():
    codigo = (RAIZ / "scripts" / "entrenar_finales.py").read_text(encoding="utf-8")
    assert "incluir_prueba" not in re.sub(r'"""[\s\S]*?"""', "", codigo, count=1)      # fuera de la docstring
    assert "tomar_prueba" not in re.sub(r'"""[\s\S]*?"""', "", codigo, count=1)
    meta = json.loads((RAIZ / "models/finales/meta.json").read_text(encoding="utf-8"))
    assert meta["filas"]["fase1"] == 6306 and meta["filas"]["fase2"] == 56241        # solo las filas de ajuste
