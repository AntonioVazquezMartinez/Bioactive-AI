#!/usr/bin/env python3
"""¿Importa que el escalador del `svm_rbf` quede fuera de la calibración? (E17, comentario de Grettel del 3 de nov)

`svm_rbf` es `Pipeline([MinMaxScaler, CalibratedClassifierCV(SVC, ensemble=False)])`. El escalador se ajusta con todas
las filas de ajuste **antes** de que la calibración parta en cinco pliegues internos, así que los mínimos y máximos
usan también las filas con las que Platt se calibra. Grettel pidió ponerlo **dentro** del estimador que se calibra
(`CalibratedClassifierCV(Pipeline([MinMaxScaler, SVC]))`), de modo que cada pliegue interno escale solo con su
entrenamiento. Es un ajuste del SVM; los demás modelos no cambian.

**Qué se mide.** Los mismos datos y las mismas 15 evaluaciones agrupadas, dos brazos:

| brazo | escalado |
|:--|:--|
| `fuera` | el del catálogo (`seleccion(("svm_rbf",))`), el que se entregó |
| `dentro` | `CalibratedClassifierCV(Pipeline([MinMaxScaler, SVC]), ensemble=False)` |

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: `fuera` reproduce el MCC 0.7017 y el AUROC 0.9190 de la escalera registrada, dentro de 0.003.
2. El cambio **importa** si la diferencia pareada media de MCC (`dentro` − `fuera`) es mayor en valor absoluto que
   su desviación pareada y el signo se cumple en al menos 12 de 15 evaluaciones. Si no, es **ruido** y se dice así,
   **pero igual se recomienda adoptarlo**, porque es lo metodológicamente correcto y no cuesta nada.
3. Se reportan AUROC y AUPRC de la minoritaria al lado (la calibración es monótona: el AUROC de la calibración no
   cambia, el del escalado sí puede).
4. No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_escalador_dentro_del_svm.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
REFERENCIA = {"mcc": 0.7017, "auroc": 0.9190}      # de: 2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad
TOLERANCIA = 0.003
REGLA_EVALUACIONES = 12


def dentro(semilla: int = 0) -> Pipeline:
    return Pipeline([("calibrado", CalibratedClassifierCV(
        Pipeline([("escala", MinMaxScaler()), ("svc", SVC(random_state=semilla))]), ensemble=False))])


def main() -> None:
    t = cargar("permeabilidad")
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"brazos": ["fuera", "dentro"], "semillas": list(SEMILLAS), "pliegues": 5, "filas": int(len(t.y)),
              "referencia_control": REFERENCIA, "tolerancia": TOLERANCIA, "regla_evaluaciones": REGLA_EVALUACIONES,
              "toca_prueba": False}
    with Corrida("escalador-dentro-del-svm-permeabilidad", decision="1.5", params=params, semillas=list(SEMILLAS),
                 datos=datos) as c:
        brazos = {"fuera": seleccion(("svm_rbf",))["svm_rbf"], "dentro": dentro()}
        res, _ = evaluar(brazos, t.X, t.y, t.grupos, semillas=SEMILLAS, verboso=False)
        todos = res[res["estrato"] == "todos"]
        ancho = todos.pivot_table(index=["semilla", "pliegue"], columns="modelo",
                                  values=["mcc", "auroc", "auprc_minoritaria", "exactitud_balanceada"])
        salida = {"medias": {m: {k: round(float(ancho[k][m].mean()), 4) for k in ("mcc", "auroc", "auprc_minoritaria")}
                             for m in brazos}}
        for k in ("mcc", "auroc", "auprc_minoritaria", "exactitud_balanceada"):
            d = ancho[k]["dentro"] - ancho[k]["fuera"]
            salida[f"dif_{k}"] = {"dif_media": round(float(d.mean()), 5), "dif_desv": round(float(d.std()), 5),
                                  "dentro_mejor_en": int((d > 0).sum()), "fuera_mejor_en": int((d < 0).sum()),
                                  "evaluaciones": int(len(d))}
        control = {k: abs(salida["medias"]["fuera"][k] - REFERENCIA[k]) <= TOLERANCIA for k in REFERENCIA}
        m = salida["dif_mcc"]
        importa = bool(abs(m["dif_media"]) > m["dif_desv"]
                       and max(m["dentro_mejor_en"], m["fuera_mejor_en"]) >= REGLA_EVALUACIONES)
        salida.update({"control_dentro_de_tolerancia": control, "el_cambio_importa": importa})
        todos.to_csv(c.carpeta / "pliegues.csv", index=False)
        c.metricas(salida)
        print(pd.DataFrame(salida["medias"]).T.to_string())
        for k in ("mcc", "auroc", "auprc_minoritaria", "exactitud_balanceada"):
            print(k, salida[f"dif_{k}"])
        print("control:", control, "· el cambio importa:", importa)


if __name__ == "__main__":
    main()
