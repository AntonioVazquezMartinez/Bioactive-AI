"""La herramienta para medir una representación propia (#295): alineación por SMILES, fallos ruidosos,
control de ruido y comparación pareada. Todo con datos sintéticos, sin `data/processed/`."""
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.models.representaciones import (columnas_al_azar, comparar, con_tabla,
                                         intervalo_nadeau_bengio)
from src.models.tareas import Tarea

N = 300
RNG = np.random.default_rng(0)
SMILES = [("C" * (i % 12 + 1)) + ("O" * (i // 12 % 5)) + ("N" * (i // 60)) for i in range(N)]


def _tarea() -> Tarea:
    señal = RNG.normal(size=N)
    y = (señal + RNG.normal(scale=0.7, size=N) > 0).astype(int)
    meta = pd.DataFrame({"SMILES": SMILES})
    grupos = np.arange(N) // 3
    return Tarea(nombre="prueba", X=RNG.normal(size=(N, 4)).astype(np.float32), y=y, grupos=grupos,
                 estratos=np.array(["unico"] * N), meta=meta, objetivo="y", representacion="base",
                 columnas=("a", "b", "c", "d")), señal


def _canalizaciones():
    return {"logistica": Pipeline([("escala", StandardScaler()),
                                   ("modelo", LogisticRegression(max_iter=500))])}


def test_la_tabla_se_alinea_por_smiles_aunque_venga_en_otro_orden():
    t, señal = _tarea()
    tabla = pd.DataFrame({"smiles": SMILES, "x": señal}).sample(frac=1, random_state=1)
    nueva = con_tabla(t, tabla, nombre="mia", canonizar=False)
    assert nueva.X.shape == (N, 1) and nueva.columnas == ("x",)
    assert np.allclose(nueva.X[:, 0], señal, atol=1e-5)
    assert nueva.representacion == "mia"


def test_modo_agrega_pega_las_columnas_a_las_que_ya_habia():
    t, señal = _tarea()
    nueva = con_tabla(t, pd.DataFrame({"smiles": SMILES, "x": señal}), nombre="s", modo="agrega",
                      canonizar=False)
    assert nueva.X.shape == (N, 5) and nueva.columnas[-1] == "x"


def test_faltar_un_compuesto_falla_diciendo_cuantos_y_no_imputa():
    t, señal = _tarea()
    tabla = pd.DataFrame({"smiles": SMILES, "x": señal}).iloc[:-7]
    with pytest.raises(ValueError, match="a 7 de 300"):
        con_tabla(t, tabla, nombre="m", canonizar=False)


def test_smiles_repetidos_con_valores_distintos_fallan_y_con_los_mismos_no():
    t, señal = _tarea()
    tabla = pd.DataFrame({"smiles": SMILES + [SMILES[0]], "x": list(señal) + [0.0]})
    with pytest.raises(ValueError, match="valores distintos"):
        con_tabla(t, tabla, nombre="m", canonizar=False)
    igual = pd.DataFrame({"smiles": SMILES + [SMILES[0]], "x": list(señal) + [señal[0]]})
    assert con_tabla(t, igual, nombre="m", canonizar=False).X.shape == (N, 1)


def test_un_valor_no_finito_falla():
    t, señal = _tarea()
    señal = señal.copy()
    señal[3] = np.inf
    with pytest.raises(ValueError, match="infinitos"):
        con_tabla(t, pd.DataFrame({"smiles": SMILES, "x": señal}), nombre="m", canonizar=False)


def test_canonizar_une_dos_escrituras_de_la_misma_molecula():
    meta = pd.DataFrame({"SMILES": ["OCC", "c1ccccc1O"]})
    t = Tarea("p", np.zeros((2, 1), np.float32), np.array([0, 1]), np.array([0, 1]),
              np.array(["unico"] * 2), meta, "y", "base", ("a",))
    tabla = pd.DataFrame({"smiles": ["CCO", "Oc1ccccc1"], "x": [1.0, 2.0]})
    nueva = con_tabla(t, tabla, nombre="m")
    assert nueva.X[:, 0].tolist() == [1.0, 2.0]


def test_columnas_constantes_avisan():
    t, _ = _tarea()
    with pytest.warns(UserWarning, match="constantes"):
        con_tabla(t, pd.DataFrame({"smiles": SMILES, "k": 1.0}), nombre="m", canonizar=False)


def test_el_ruido_conserva_filas_etiquetas_y_grupos():
    t, _ = _tarea()
    r = columnas_al_azar(t, 10)
    assert r.X.shape == (N, 10) and np.array_equal(r.y, t.y) and np.array_equal(r.grupos, t.grupos)


def test_nadeau_bengio_es_mas_ancho_que_el_intervalo_ingenuo():
    d = np.random.default_rng(1).normal(0.01, 0.02, 15)
    media, lo, hi = intervalo_nadeau_bengio(d)
    ingenuo = 2.145 * d.std(ddof=1) / np.sqrt(15)
    assert hi - media > ingenuo and lo < media < hi


def test_comparar_distingue_la_columna_informativa_del_ruido():
    t, señal = _tarea()
    buena = con_tabla(t, pd.DataFrame({"smiles": SMILES, "x": señal}), nombre="buena", canonizar=False)
    ruido = columnas_al_azar(t, 4, nombre="ruido")
    resumen, resultados = comparar({"base": t, "buena": buena, "ruido": ruido}, _canalizaciones(),
                                   referencia="base")
    mcc = resumen[(resumen["metrica"] == "mcc") & (resumen["estrato"] == "todos")].set_index("representacion")
    assert mcc.loc["buena", "dif_media"] > 0.2 and bool(mcc.loc["buena", "distingue"])
    assert mcc.loc["buena", "evaluaciones"] == 15
    assert not bool(mcc.loc["ruido", "distingue"])
    assert set(resultados["representacion"]) == {"base", "buena", "ruido"}


def test_comparar_rechaza_tareas_con_distintas_etiquetas():
    t, _ = _tarea()
    otra = Tarea(**{**t.__dict__, "y": 1 - t.y})
    with pytest.raises(ValueError, match="no tiene las mismas etiquetas"):
        comparar({"a": t, "b": otra}, _canalizaciones(), referencia="a")
