"""El detalle por pliegue de la fase 1 vive en la corrida y reproduce lo que la corrida registró (#200).

`experimentos/README.md` pide un `pliegues.csv` cuando la decisión se apoya en conteos («gana 12 de 15»), y
la corrida de la fase 1 solo guardaba el agregado: el detalle estaba en `notebooks/datos/05_ensambles.csv`,
al revés de lo que hace la fase 2. Ahora los dos archivos son el mismo, y esta prueba comprueba que sus
números son los de `metricas.json`: las medias de la comparativa y, para cada comparación pareada contra el
mejor individual, la diferencia media y en cuántas de las 15 evaluaciones gana.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
CORRIDA = RAIZ / "experimentos" / "2026-11-01-artemio-1.5-ensambles-permeabilidad"
DETALLE_CUADERNO = RAIZ / "notebooks" / "datos" / "05_ensambles.csv"
MEJOR_INDIVIDUAL = "svm_rbf"


@pytest.fixture(scope="module")
def metricas():
    return json.loads((CORRIDA / "metricas.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def todos():
    d = pd.read_csv(CORRIDA / "pliegues.csv")
    return d[d["estrato"] == "todos"].set_index(["modelo", "semilla", "pliegue"])


def test_la_corrida_guarda_el_detalle_y_es_el_del_cuaderno():
    assert (CORRIDA / "pliegues.csv").read_bytes() == DETALLE_CUADERNO.read_bytes()


def test_quince_evaluaciones_por_modelo(todos):
    assert (todos.groupby("modelo").size() == 15).all()


def test_las_medias_de_la_comparativa_salen_del_detalle(metricas, todos):
    for modelo, v in metricas["comparativa"].items():
        for k in ("mcc", "auroc", "auprc_minoritaria"):
            assert todos.loc[modelo][k].mean() == pytest.approx(v[k], abs=5e-5), (modelo, k)


def test_las_comparaciones_pareadas_se_recuentan_desde_el_detalle(metricas, todos):
    ref = todos.loc[MEJOR_INDIVIDUAL]
    for clave, v in metricas["comparacion_todos"].items():
        modelo, metrica = clave.split("/")
        dif = todos.loc[modelo][metrica] - ref[metrica]
        assert int((dif > 0).sum()) == v["mejor_en"], clave
        assert float(dif.mean()) == pytest.approx(v["dif_media"], abs=5e-5), clave
