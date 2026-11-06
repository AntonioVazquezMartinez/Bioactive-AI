#!/usr/bin/env python3
"""Qué tanto cambia el desempeño según cómo se agrupa, y qué hace el tamaño de la molécula.

Dos mediciones baratas de la fase 1, pedidas al cerrar la reunión del 3 de noviembre
(`docs/estudio/`, plan del equipo). **No tocan la prueba reservada**: todo ocurre dentro de las
6,306 filas de entrenamiento y validación.

**E0 · una línea base de tamaño.** Se compara `svm_rbf` y `logistica` con una regresión logística
que solo ve el peso molecular y el TPSA, por tramo de peso (los cortes fijos de #216) y por
tamaño del grupo de la fila. Pregunta: ¿cuánto del desempeño es solo tamaño y polaridad?

**E1 · una escalera de agrupación.** Los mismos modelos y los mismos datos, cambiando solo cómo se
parten los pliegues: al azar, por esqueleto de conectividad, por andamio, andamio unido a esqueleto
(la que usa el proyecto) y por similitud (componentes conexas de Tanimoto ≥ 0.6, 0.5 y 0.4). Para
cada una se reporta AUROC, MCC, número de grupos, el grupo más grande y **qué tan parecido es en
promedio cada compuesto de validación a su vecino más cercano de ajuste**, que es lo que mide qué
tan nueva es la química que se evalúa.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado): esperamos que el
desempeño baje y que la similitud al vecino más cercano baje al apretar el agrupamiento, sin
afirmar cuánto. Los tres umbrales de similitud se fijaron aquí, no se ajustan después. Si el orden
no es monótono, se reporta así. Un grupo mayor al 20% de las filas hace inservible la partición en 5
pliegues y esa fila se marca como no evaluable.

Es el primer paso de una comparación mayor: la prueba reservada tiene los andamios raros a
propósito, y esa escalera es lo que permite decir cuánto de la caída de 0.9190 a 0.7928 viene de
la química nueva y cuánto del tamaño.
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

RDLogger.DisableLog("rdApp.*")
SEMILLAS = (0, 1, 2)
UMBRALES_SIMILITUD = (0.6, 0.5, 0.4)
MAX_GRUPO = 0.20
MODELOS = ("svm_rbf", "logistica")
# Cifras ya registradas del modelo final (corrida 2026-11-01-artemio-1.5-modelo-final-permeabilidad):
# solo como referencia de lectura, no se vuelven a medir aquí.
PRUEBA_REGISTRADA = {"auroc": 0.7928, "mcc": 0.3385}


def pipelines(columnas: list[str]) -> dict:
    p = seleccion(MODELOS)
    idx = [columnas.index("MolWt"), columnas.index("TPSA")]
    p["base_peso_tpsa"] = Pipeline([
        ("cols", ColumnTransformer([("c", "passthrough", idx)])),
        ("escala", MinMaxScaler()),
        ("modelo", LogisticRegression(max_iter=3000, random_state=0))])
    return p


def tamano_de_grupo(grupos: np.ndarray) -> np.ndarray:
    _, inv, cuenta = np.unique(grupos, return_inverse=True, return_counts=True)
    n = cuenta[inv]
    return np.where(n == 1, "grupo de 1", np.where(n <= 4, "grupo de 2-4", "grupo de 5 o más"))


def resumen_estratos(res: pd.DataFrame) -> pd.DataFrame:
    g = res.groupby(["estrato", "modelo"])
    t = g.agg(evaluaciones=("auroc", "size"), n_medio=("n", "mean"), activos=("activos", "mean"),
              auroc=("auroc", "mean"), mcc=("mcc", "mean")).round(4)
    return t


def similitudes(smiles: list[str]) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in smiles]
    n = len(fps)
    S = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        S[i] = DataStructs.BulkTanimotoSimilarity(fps[i], fps)
    np.fill_diagonal(S, 0.0)
    return S


def grupos_por_similitud(S: np.ndarray, umbral: float) -> np.ndarray:
    _, etiquetas = connected_components(sparse.csr_matrix(S >= umbral), directed=False)
    return etiquetas


def vecino_mas_cercano(S: np.ndarray, y: np.ndarray, grupos: np.ndarray) -> float:
    """Media, sobre los compuestos de validación de la semilla 0, de su mayor similitud con el ajuste."""
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)
    valores = []
    for ajuste, val in cv.split(S, y, grupos):
        valores.append(S[np.ix_(val, ajuste)].max(axis=1))
    return float(np.concatenate(valores).mean())


def escalera(t, S) -> tuple[pd.DataFrame, dict]:
    meta = t.meta
    sin = "SIN_ANDAMIO"
    andamio = meta["andamio"].fillna(sin).to_numpy()
    esqueleto = meta["esqueleto"].to_numpy()
    # Por andamio solo: los acíclicos conservan su esqueleto como grupo, igual que en el 03 §2.1.
    solo_andamio = np.where(andamio == sin, esqueleto, andamio)
    opciones = {
        "1 al azar": np.arange(len(meta)),
        "2 por esqueleto": esqueleto,
        "3 por andamio": solo_andamio,
        "4 andamio + esqueleto (actual)": t.grupos,
    }
    for u in UMBRALES_SIMILITUD:
        opciones[f"5 similitud ≥ {u}"] = grupos_por_similitud(S, u)

    filas, detalle = [], {}
    for nombre, g in opciones.items():
        g = np.asarray(g)
        _, cuenta = np.unique(g, return_counts=True)
        mayor = float(cuenta.max() / len(g))
        fila = {"agrupacion": nombre, "grupos": len(cuenta), "mayor_grupo_pct": round(100 * mayor, 1)}
        if mayor > MAX_GRUPO:
            fila["nota"] = "no evaluable: un grupo pasa del 20% de las filas"
            filas.append(fila)
            continue
        res, _ = evaluar({k: v for k, v in pipelines(list(t.columnas)).items() if k in MODELOS},
                         t.X, t.y, g, semillas=SEMILLAS, verboso=False)
        todos = res[res["estrato"] == "todos"]
        for modelo, d in todos.groupby("modelo"):
            fila[f"auroc_{modelo}"] = round(float(d["auroc"].mean()), 4)
            fila[f"mcc_{modelo}"] = round(float(d["mcc"].mean()), 4)
        fila["vecino_mas_cercano"] = round(vecino_mas_cercano(S, t.y, g), 4)
        filas.append(fila)
        detalle[nombre] = fila
    return pd.DataFrame(filas), detalle


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    columnas = list(pd.read_parquet(PROCESADOS / DESCRIPTORES["descriptores"]).columns)
    object.__setattr__(t, "columnas", columnas)   # Tarea está congelada; las columnas no vienen en ella
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelos": list(MODELOS) + ["base_peso_tpsa"], "semillas": list(SEMILLAS), "pliegues": 5,
              "umbrales_similitud": list(UMBRALES_SIMILITUD), "grupo_maximo": MAX_GRUPO,
              "filas": int(len(t.y)), "toca_prueba": False,
              "nota": "similitud: componentes conexas de Tanimoto sobre Morgan radio 2, 2048 bits"}
    with Corrida("escalera-agrupacion-permeabilidad", decision="1.2", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        print(f"{len(t.y):,} filas · {len(np.unique(t.grupos)):,} grupos · {t.y.mean():.1%} BBB+\n")

        print("== E0 · línea base de peso molecular y TPSA, por tramo de peso ==")
        e0a, _ = evaluar(pipelines(columnas), t.X, t.y, t.grupos, estratos=t.estratos,
                         semillas=SEMILLAS, verboso=False)
        r0a = resumen_estratos(e0a)
        print(r0a.to_string(), "\n")

        print("== E0 · por tamaño del grupo de la fila ==")
        e0b, _ = evaluar(pipelines(columnas), t.X, t.y, t.grupos, estratos=tamano_de_grupo(t.grupos),
                         semillas=SEMILLAS, verboso=False)
        r0b = resumen_estratos(e0b)
        print(r0b.to_string(), "\n")

        print("== E1 · escalera de agrupación ==")
        S = similitudes(t.meta["SMILES"].tolist())
        esc, _ = escalera(t, S)
        print(esc.to_string(index=False), "\n")
        print("referencia, ya registrada (no se mide aquí):", PRUEBA_REGISTRADA)

        c.metricas({
            "e0_por_tramo": {f"{e}|{m}": {"auroc": float(r["auroc"]), "mcc": float(r["mcc"]),
                                          "n_medio": float(r["n_medio"])}
                             for (e, m), r in r0a.iterrows()},
            "e0_por_grupo": {f"{e}|{m}": {"auroc": float(r["auroc"]), "mcc": float(r["mcc"]),
                                          "n_medio": float(r["n_medio"])}
                             for (e, m), r in r0b.iterrows()},
            "e1_escalera": json_seguro(esc),
            "prueba_registrada_referencia": PRUEBA_REGISTRADA,
        })


def json_seguro(df: pd.DataFrame) -> list[dict]:
    return [{k: (None if (isinstance(v, float) and np.isnan(v)) else v) for k, v in fila.items()}
            for fila in df.to_dict("records")]


if __name__ == "__main__":
    main()
