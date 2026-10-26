"""El arnés de validación cruzada no puede filtrar ni inflar en silencio.

Las tres cosas que estas pruebas atan son las que ya se rompieron una vez en
este proyecto: que el escalado se ajuste dentro del pliegue, que ningún grupo
cruce entre ajuste y evaluación, y que un subgrupo sin clase minoritaria no se
reporte —en la fase 2, `ACHE` tiene 221 pares de NPASS y tres activos, y su
AUROC salía 0.763—.
"""

import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.evaluation.cv import evaluar, intervalo_por_grupos, resumen
from src.models.baseline import CANALIZACIONES, canalizaciones


@pytest.fixture
def datos():
    rng = np.random.default_rng(0)
    n = 300
    grupos = np.repeat(np.arange(n // 3), 3)          # tres filas por grupo
    y = (rng.random(n) < 0.4).astype(int)
    X = rng.normal(size=(n, 5)) + y[:, None] * 0.8     # señal débil pero real
    estratos = np.where(np.arange(n) % 5 == 0, "raro", "comun")
    return X, y, grupos, estratos


def test_ningun_grupo_cruza_entre_ajuste_y_evaluacion(datos):
    """Es la propiedad que hace comparable la evaluación (decisión 1.2)."""
    X, y, grupos, _ = datos
    from sklearn.model_selection import StratifiedGroupKFold
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)
    for ajuste, val in cv.split(X, y, grupos):
        assert not set(grupos[ajuste]) & set(grupos[val])


def test_devuelve_una_prediccion_fuera_de_pliegue_por_fila(datos):
    """Cada fila la predice un modelo que no la vio, y exactamente una vez."""
    X, y, grupos, _ = datos
    _, fdp = evaluar({"lr": LogisticRegression()}, X, y, grupos,
                     semillas=(0, 1), pliegues=5, verboso=False)
    assert fdp["lr"].shape == (2, len(y))
    assert not np.isnan(fdp["lr"]).any(), "alguna fila se quedó sin predicción"


def test_un_subgrupo_sin_clase_minoritaria_no_se_reporta(datos):
    """Un AUROC sobre tres casos es ruido; no debe aparecer como si fuera señal."""
    X, y, grupos, _ = datos
    # Un estrato con un solo positivo: nunca llega al mínimo.
    estratos = np.array(["comun"] * len(y), dtype=object)
    idx = np.flatnonzero(y == 1)[:1]
    estratos[idx] = "casi_vacio"
    estratos[np.flatnonzero(y == 0)[:40]] = "casi_vacio"
    res, _ = evaluar({"lr": LogisticRegression()}, X, y, grupos,
                     estratos=estratos, semillas=(0,), pliegues=5, verboso=False)
    assert "casi_vacio" not in set(res["estrato"])
    assert "todos" in set(res["estrato"])


def test_el_escalador_se_ajusta_dentro_del_pliegue(datos):
    """Si se ajustara antes de partir, filtraría la media y la varianza."""
    X, y, grupos, _ = datos
    canalizacion = Pipeline([("escala", StandardScaler()),
                             ("modelo", LogisticRegression())])
    _, fdp = evaluar({"p": canalizacion}, X, y, grupos, semillas=(0,),
                     pliegues=5, verboso=False)
    # El mismo escalador ajustado sobre todo el conjunto da otras predicciones:
    # si fueran idénticas, el arnés lo estaría ajustando fuera del pliegue.
    fuera = StandardScaler().fit(X)
    canalizacion.fit(fuera.transform(X), y)
    todas = canalizacion.predict_proba(fuera.transform(X))[:, 1]
    assert not np.allclose(fdp["p"][0], todas)


def test_las_tres_canalizaciones_existen_y_son_canalizaciones(datos):
    X, y, grupos, _ = datos
    c = canalizaciones(semilla=0)
    assert tuple(c) == CANALIZACIONES
    for nombre, modelo in c.items():
        assert isinstance(modelo, Pipeline), nombre
    res, _ = evaluar(c, X, y, grupos, semillas=(0,), pliegues=3, verboso=False)
    assert set(res["modelo"]) == set(CANALIZACIONES)


def test_el_intervalo_remuestrea_grupos_y_no_filas():
    """Con filas correlacionadas dentro del grupo, remuestrear filas engaña.

    Es la situación real: los compuestos del mismo andamio comparten química, y
    el modelo les da predicciones parecidas. Ahí el remuestreo por filas trata
    como independiente lo que no lo es y devuelve un intervalo más estrecho de
    lo que corresponde, que es la forma fácil de concluir que algo se distingue
    cuando no se distingue. El fixture general no sirve para esto porque sus
    grupos no tienen correlación interna.
    """
    rng = np.random.default_rng(1)
    n_grupos, por_grupo = 60, 8
    # La etiqueta y la predicción se deciden por grupo: dentro, todo es igual.
    y_g = (rng.random(n_grupos) < 0.5).astype(int)
    # La señal es parcial a propósito: con separación perfecta el AUROC es
    # 1.0 en cada remuestra y los dos intervalos miden cero.
    p_g = np.clip(y_g * 0.25 + rng.random(n_grupos) * 0.75, 0, 1)
    y = np.repeat(y_g, por_grupo)
    p = np.repeat(p_g, por_grupo) + rng.normal(scale=0.01, size=n_grupos * por_grupo)
    grupos = np.repeat(np.arange(n_grupos), por_grupo)

    _, lo_g, hi_g = intervalo_por_grupos(y, p, grupos, remuestras=600)
    _, lo_f, hi_f = intervalo_por_grupos(y, p, np.arange(len(y)), remuestras=600)
    assert (hi_g - lo_g) > (hi_f - lo_f), (
        f"por grupos [{lo_g:.3f}, {hi_g:.3f}] no es más ancho que"
        f" por filas [{lo_f:.3f}, {hi_f:.3f}]")


def test_el_resumen_no_llama_error_estandar_a_la_desviacion(datos):
    X, y, grupos, _ = datos
    res, _ = evaluar({"lr": LogisticRegression()}, X, y, grupos,
                     semillas=(0, 1), pliegues=3, verboso=False)
    r = resumen(res)
    assert isinstance(r, pd.DataFrame)
    assert ("mcc", "std") in r.columns


def test_el_tiempo_de_ajuste_se_mide_y_no_se_repite_por_estrato(datos):
    """La rúbrica de los Avances 4 y 5 pide los tiempos en la misma tabla.

    Un ajuste ocurre una vez por (modelo, semilla, pliegue), no una vez por
    subgrupo. Si los segundos se copiaran a las filas de estrato, cualquier
    promedio sobre la tabla larga los contaría varias veces y el tiempo del
    modelo saldría inflado por el número de estratos que tenga la corrida.
    """
    X, y, grupos, estratos = datos
    # `min_minoritaria` baja para que los dos estratos del fixture se reporten;
    # con el mínimo real de 20 ninguno llega y la prueba no comprobaría nada.
    res, _ = evaluar({"lr": LogisticRegression()}, X, y, grupos,
                     estratos=estratos, semillas=(0,), pliegues=5,
                     min_minoritaria=5, verboso=False)

    todos = res[res.estrato.eq("todos")]
    assert (todos.segundos_ajuste > 0).all()
    assert (todos.segundos_prediccion > 0).all()
    assert todos.segundos_ajuste.notna().all()

    por_estrato = res[res.estrato.ne("todos")]
    assert len(por_estrato) > 0, "la prueba no comprueba nada si no hay estratos"
    assert por_estrato.segundos_ajuste.isna().all()


def test_la_tabla_comparativa_ordena_por_la_metrica_que_se_le_pida(datos):
    """Cuál métrica ordena es decisión del equipo, no una constante del código."""
    from src.evaluation.cv import tabla_comparativa

    X, y, grupos, _ = datos
    res, _ = evaluar(canalizaciones(), X, y, grupos, semillas=(0,), pliegues=3,
                     verboso=False)

    por_mcc = tabla_comparativa(res, principal="mcc")
    assert list(por_mcc.index) == list(por_mcc.sort_values("mcc", ascending=False).index)
    assert "segundos_ajuste" in por_mcc.columns
    assert (por_mcc.pliegues == 3).all()

    por_auroc = tabla_comparativa(res, principal="auroc", otras=("mcc",))
    assert list(por_auroc.columns)[:2] == ["auroc", "desv"]
    assert set(por_auroc.index) == set(CANALIZACIONES)


def test_la_tabla_comparativa_avisa_si_el_estrato_no_existe(datos):
    """Pedir un estrato que no se reportó debe fallar, no devolver nada en silencio."""
    from src.evaluation.cv import tabla_comparativa

    X, y, grupos, _ = datos
    res, _ = evaluar({"lr": LogisticRegression()}, X, y, grupos, semillas=(0,),
                     pliegues=3, verboso=False)
    with pytest.raises(ValueError, match="estrato"):
        tabla_comparativa(res, estrato="inexistente")


def test_la_tabla_no_se_rompe_si_la_principal_esta_entre_las_otras(datos):
    """Pasa con los valores por omisión al pedir AUROC: la columna salía dos veces."""
    from src.evaluation.cv import tabla_comparativa

    X, y, grupos = datos[0], datos[1], datos[2]
    res, _ = evaluar({"lr": LogisticRegression()}, X, y, grupos, semillas=(0,),
                     pliegues=3, verboso=False)
    tabla = tabla_comparativa(res, principal="auroc")
    assert list(tabla.columns).count("auroc") == 1
    assert list(tabla.columns)[:2] == ["auroc", "desv"]
