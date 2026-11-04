#!/usr/bin/env python3
"""E6 (fase 1) · ¿lo que aportan las huellas depende del tamaño de la molécula? (#215)

Primera hipótesis de representación: en la fase 2 las huellas ayudan y en la fase 1 no. Una
lectura es que depende del **tamaño**: los fragmentos describirían mejor a las moléculas grandes
(donde la química es más variada) que a las pequeñas (donde el tamaño y la polaridad ya dicen
casi todo, E0). Esta corrida mide, en la fase 1, cuánto cambia el desempeño al añadir las huellas
Sort & Slice a los descriptores **por tramo de peso molecular**, con los seis modelos del
Avance 4 sin afinar.

**Lo que se declara antes de correr.**
- Brazos: `descriptores` (los 151 de siempre) y `descriptores+huellas` (los 151 más 2,048 bits,
  el vocabulario relearned dentro de cada pliegue). Mismas semillas (0, 1, 2) y mismos pliegues.
- Tramos: los cortes fijos de `etiquetas_por_tamano` (#216), los mismos para las dos fases.
- Lectura principal: la diferencia **pareada** (huellas − descriptores) del AUROC por tramo, la
  media y en cuántas de las 15 evaluaciones es positiva, por modelo. Se reportan también las
  medias de MCC. **No se reporta AUPRC por estrato** (#187).
- Qué diría que la hipótesis se sostiene: que la ganancia sea mayor en los tramos pesados que en
  los ligeros en la mayoría de los modelos. Qué diría que no: que sea plana o con signo cambiante.
  Un resultado plano no se reinterpreta.
- Esta pasada **no iguala** el tamaño de los tramos por submuestreo: el tramo ligero es más
  pequeño y tiene más ruido. Si el patrón aparece, la igualación y el control por rareza son la
  siguiente corrida. No toca la prueba reservada.

    ./env/bin/python scripts/experimento_tamano_fase1.py
"""
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.pipeline import make_pipeline

from src.evaluation.cv import evaluar
from src.features.huellas import AgregarHuellas, agrupar_iguales, identificadores_morgan
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
N_BITS = 2048
CLAVES = ("logistica", "arbol", "knn", "bayes", "svm_rbf", "mlp")


def main() -> None:
    t = cargar("permeabilidad", estratos="tamano")
    X = np.asarray(t.X, dtype=float)
    n_densas = X.shape[1]
    huellas, ident = identificadores_morgan(t.meta["SMILES"].tolist())
    huellas, ident, _ = agrupar_iguales(huellas, ident)
    X_mixta = sparse.hstack([sparse.csr_matrix(X), huellas]).tocsr()
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"modelos": list(CLAVES), "brazos": ["descriptores", "descriptores+huellas"],
              "semillas": list(SEMILLAS), "pliegues": 5, "n_bits": N_BITS, "estratos": "tamano",
              "filas": int(len(t.y)), "toca_prueba": False,
              "metrica_principal": "diferencia pareada de AUROC por tramo de peso",
              "iguala_tramos": False}
    with Corrida("tamano-huellas-permeabilidad", decision="1.3", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        partes = {}
        for brazo, (M, envolver) in {
                "descriptores": (X, lambda m: m),
                "descriptores+huellas": (X_mixta,
                                         lambda m: make_pipeline(AgregarHuellas(n_densas, n_bits=N_BITS), m)),
        }.items():
            t0 = time.perf_counter()
            modelos = {k: envolver(v) for k, v in seleccion(CLAVES).items()}
            res, _ = evaluar(modelos, M, t.y, t.grupos, estratos=t.estratos,
                             semillas=SEMILLAS, verboso=False)
            res["brazo"] = brazo
            partes[brazo] = res
            print(f"{brazo}: {time.perf_counter() - t0:.0f} s", flush=True)

        a, b = partes["descriptores"], partes["descriptores+huellas"]
        llave = ["modelo", "semilla", "pliegue", "estrato"]
        m = a.merge(b, on=llave, suffixes=("_d", "_h"))
        m["d_auroc"] = m["auroc_h"] - m["auroc_d"]
        m["d_mcc"] = m["mcc_h"] - m["mcc_d"]
        g = m.groupby(["estrato", "modelo"])
        tabla = g.agg(n_medio=("n_d", "mean"), evaluaciones=("d_auroc", "size"),
                      d_auroc=("d_auroc", "mean"), mejora_en=("d_auroc", lambda s: int((s > 0).sum())),
                      d_mcc=("d_mcc", "mean"), auroc_desc=("auroc_d", "mean")).round(4).reset_index()
        print(tabla.to_string(index=False))
        resumen = (m.groupby("estrato")["d_auroc"].agg(["mean", "size"]).round(4)
                   .rename(columns={"mean": "d_auroc_medio_6_modelos", "size": "evaluaciones"}))
        print("\nganancia media de AUROC por tramo, todos los modelos:\n", resumen.to_string())
        c.metricas({"por_tramo_y_modelo": tabla.to_dict("records"),
                    "por_tramo": resumen.reset_index().to_dict("records")})


if __name__ == "__main__":
    main()
