#!/usr/bin/env python3
"""¿Importa que la calibración interna del SVM no agrupe? (#191, fase 1)

`svm_rbf` (`src/models/alternativos.py`) envuelve `SVC` en `CalibratedClassifierCV(...,
ensemble=False)` sin `cv`, así que Platt se ajusta con cinco pliegues internos **al azar**: un
análogo del mismo andamio puede caer a los dos lados. Es la única partición interna del proyecto
que no agrupa. Platt es monótona, así que el AUROC y el AUPRC no pueden cambiar; el MCC y la
exactitud balanceada sí, porque cortan en 0.5 sobre esa probabilidad.

**Lo que se mide.** El mismo modelo, los mismos datos y las mismas particiones externas
(`grupos_cv`, 5 pliegues, 3 semillas = 15 evaluaciones), cambiando una sola cosa: cómo parte la
calibración interna.

| brazo | calibración interna |
|:--|:--|
| `actual` | 5 pliegues estratificados al azar (lo que hay en `main`) |
| `agrupada` | 5 pliegues `StratifiedGroupKFold` con los grupos de las filas de ajuste |
| `catalogo` | `seleccion(("svm_rbf",))` tal cual: control de que `actual` reproduce lo que se publicó |

No toca la prueba reservada: todo ocurre dentro de las 6,306 filas de ajuste y validación.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. El AUROC y el AUPRC de `actual` y `agrupada` deben coincidir (hasta 1e-6 en promedio). Si no,
   hay un error en la comparación y el resto no se lee.
2. `catalogo` y `actual` deben dar el mismo MCC en cada evaluación (es el mismo modelo).
3. El efecto sobre el MCC se declara **distinto de ruido** si la diferencia pareada media
   (`agrupada` − `actual`) supera en valor absoluto a su desviación pareada **y** el signo se
   cumple en al menos 12 de las 15 evaluaciones. En otro caso es ruido y el #191 se cierra con
   esta cifra y la excepción declarada. No se ajusta ninguna de las dos reglas después.
4. Si hay efecto, se reporta aunque favorezca al modelo entregado.
"""
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

from src.evaluation.cv import evaluar
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar
from src.tracking import Corrida

SEMILLAS = (0, 1, 2)
PLIEGUES_INTERNOS = 5
REGLA_EVALUACIONES = 12


class SVMCalibrado(ClassifierMixin, BaseEstimator):
    """`svm_rbf` con la calibración interna agrupada o no, para aislar esa sola diferencia.

    Declara `necesita_grupos` para que `evaluar` le pase los grupos de su parte del pliegue.
    El brazo `actual` los ignora. El escalado va fuera de la calibración, como en el catálogo.
    """

    necesita_grupos = True

    def __init__(self, agrupar: bool = False, semilla: int = 0):
        self.agrupar = agrupar
        self.semilla = semilla

    def fit(self, X, y, grupos=None):
        self.escala_ = MinMaxScaler().fit(X)
        Xs = self.escala_.transform(X)
        cv = None   # el valor por omisión de scikit-learn: 5 pliegues estratificados, sin barajar
        if self.agrupar:
            cv = list(StratifiedGroupKFold(PLIEGUES_INTERNOS, shuffle=True,
                                           random_state=self.semilla).split(Xs, y, grupos))
        self.modelo_ = CalibratedClassifierCV(SVC(random_state=self.semilla),
                                              ensemble=False, cv=cv).fit(Xs, y)
        self.classes_ = self.modelo_.classes_
        return self

    def predict_proba(self, X):
        return self.modelo_.predict_proba(self.escala_.transform(X))

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]


def main() -> None:
    t = cargar("permeabilidad")
    datos = [PROCESADOS / "bbb_meta.parquet", PROCESADOS / DESCRIPTORES["descriptores"]]
    params = {"brazos": ["actual", "agrupada", "catalogo"], "semillas": list(SEMILLAS),
              "pliegues_externos": 5, "pliegues_internos": PLIEGUES_INTERNOS,
              "regla_evaluaciones": REGLA_EVALUACIONES, "filas": int(len(t.y)),
              "toca_prueba": False}
    with Corrida("calibracion-svm-agrupada-permeabilidad", decision="1.5", params=params,
                 semillas=list(SEMILLAS), datos=datos) as c:
        print(f"{len(t.y):,} filas · {len(np.unique(t.grupos)):,} grupos · {t.y.mean():.1%} BBB+\n")
        brazos = {"actual": SVMCalibrado(agrupar=False),
                  "agrupada": SVMCalibrado(agrupar=True),
                  "catalogo": seleccion(("svm_rbf",))["svm_rbf"]}
        res, oof = evaluar(brazos, t.X, t.y, t.grupos, semillas=SEMILLAS, verboso=False)
        todos = res[res["estrato"] == "todos"]

        medias = todos.groupby("modelo")[["auroc", "auprc_minoritaria", "mcc",
                                          "exactitud_balanceada"]].mean().round(4)
        print(medias.to_string(), "\n")

        ancho = todos.pivot_table(index=["semilla", "pliegue"], columns="modelo",
                                  values=["mcc", "exactitud_balanceada", "auroc",
                                          "auprc_minoritaria"])
        # 1 y 2: las dos comprobaciones declaradas, antes de leer nada más.
        d_auroc = float((ancho["auroc"]["agrupada"] - ancho["auroc"]["actual"]).abs().max())
        d_auprc = float((ancho["auprc_minoritaria"]["agrupada"]
                         - ancho["auprc_minoritaria"]["actual"]).abs().max())
        d_catalogo = float((ancho["mcc"]["catalogo"] - ancho["mcc"]["actual"]).abs().max())
        print(f"máx |ΔAUROC| agrupada−actual: {d_auroc:.2e}   máx |ΔAUPRC|: {d_auprc:.2e}")
        print(f"máx |ΔMCC| catalogo−actual:   {d_catalogo:.2e}\n")

        efecto = {}
        for m in ("mcc", "exactitud_balanceada"):
            d = ancho[m]["agrupada"] - ancho[m]["actual"]
            mejor = int((d > 0).sum())
            peor = int((d < 0).sum())
            efecto[m] = {"diferencia_media": round(float(d.mean()), 4),
                         "desviacion_pareada": round(float(d.std()), 4),
                         "mejor_en": mejor, "peor_en": peor, "evaluaciones": int(len(d))}
            print(f"{m}: Δ medio {d.mean():+.4f} · desviación pareada {d.std():.4f} · "
                  f"mejor en {mejor}/{len(d)}, peor en {peor}")

        # Qué cambia en la práctica: la fracción que el corte de 0.5 declara positiva.
        positivos = {}
        for nombre in ("actual", "agrupada"):
            p = oof[nombre]
            positivos[nombre] = round(float((p >= 0.5).mean()), 4)
        print(f"\nfracción declarada BBB+ a 0.5: {positivos} (real {t.y.mean():.4f})\n")

        d = efecto["mcc"]
        distinto_de_ruido = (abs(d["diferencia_media"]) > d["desviacion_pareada"]
                             and max(d["mejor_en"], d["peor_en"]) >= REGLA_EVALUACIONES)
        print("regla 3 (efecto distinto de ruido):", distinto_de_ruido)

        c.metricas({
            "medias": {m: {k: float(v) for k, v in fila.items()} for m, fila in medias.iterrows()},
            "comprobaciones": {"max_abs_dauroc": d_auroc, "max_abs_dauprc": d_auprc,
                               "max_abs_dmcc_catalogo_vs_actual": d_catalogo},
            "efecto_agrupada_menos_actual": efecto,
            "fraccion_positiva_a_0.5": positivos,
            "prevalencia_real": round(float(t.y.mean()), 4),
            "efecto_distinto_de_ruido": bool(distinto_de_ruido),
        })
        res.to_csv(c.carpeta / "pliegues.csv", index=False)


if __name__ == "__main__":
    main()
