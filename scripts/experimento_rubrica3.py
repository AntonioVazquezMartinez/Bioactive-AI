#!/usr/bin/env python3
"""Lo que el baseline necesita para responderse a sí mismo: ajuste, importancia y piso.

`experimento_baseline.py` mide **cuánto acierta** cada canalización. Eso deja
tres preguntas abiertas que un modelo de referencia tiene que contestar antes
de servir como referencia, y las tres se miden aquí:

1. **¿Sobreajusta?** No se puede leer de una sola cifra de validación. Hace
   falta la misma métrica sobre el pliegue de ajuste y sobre el de evaluación,
   y la brecha entre las dos. Y para distinguir «sobreajusta» de «le faltan
   datos», la curva de aprendizaje: si la brecha se cierra al crecer el
   entrenamiento, el problema es de tamaño; si no, es de capacidad.
2. **¿Qué características pesan?** Con dos métodos y no con uno: la impureza
   del bosque, que es barata y sesgada hacia variables de muchos valores, y la
   permutación sobre el pliegue de evaluación, que mide lo que el modelo
   pierde al romper esa columna. Se reportan juntas porque discrepan, y la
   discrepancia es informativa ([C.2](../docs/decisiones.md#dc-2) pide dos
   métodos independientes).
3. **¿Contra qué piso se compara?** No existe un desempeño histórico de la
   patrocinadora, así que el piso lo ponen los clasificadores triviales
   —siempre la clase mayoritaria, al azar con la proporción observada— medidos
   con la **misma** partición agrupada. Un MCC de 0.70 solo significa algo
   contra el 0.00 que da no mirar la molécula.

Todo dentro de entrenamiento y validación; la prueba reservada no se toca
([2.6](../docs/decisiones.md#d2-6)).

    python scripts/experimento_rubrica3.py

Salida: tres CSV en `notebooks/datos/` y una corrida en `experimentos/`.
"""

import platform
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.base import clone  # noqa: E402
from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.inspection import permutation_importance  # noqa: E402
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402

from src.evaluation.cv import _medir  # noqa: E402
from src.models import canalizaciones, cargar  # noqa: E402
from src.tracking import Corrida  # noqa: E402

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
FRACCIONES = (0.2, 0.4, 0.6, 0.8, 1.0)
REPETICIONES_PERMUTACION = 5
DATOS = RAIZ / "notebooks" / "datos"


def _particion(X, y, grupos, semilla):
    cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=semilla)
    return list(cv.split(X, y, grupos))


def ajuste(t) -> pd.DataFrame:
    """La misma métrica sobre ajuste y sobre evaluación, con su brecha."""
    filas = []
    for semilla in SEMILLAS:
        for pliegue, (tr, va) in enumerate(_particion(t.X, t.y, t.grupos, semilla), 1):
            for nombre, canal in canalizaciones(semilla).items():
                m = clone(canal).fit(t.X[tr], t.y[tr])
                p_tr = m.predict_proba(t.X[tr])[:, 1]
                p_va = m.predict_proba(t.X[va])[:, 1]
                met_tr, met_va = _medir(t.y[tr], p_tr), _medir(t.y[va], p_va)
                filas.append({"modelo": nombre, "semilla": semilla, "pliegue": pliegue,
                              **{f"{k}_ajuste": v for k, v in met_tr.items()},
                              **{f"{k}_validacion": v for k, v in met_va.items()},
                              "brecha_mcc": met_tr["mcc"] - met_va["mcc"],
                              "brecha_auroc": met_tr["auroc"] - met_va["auroc"]})
            print(f"  ajuste · semilla {semilla} · pliegue {pliegue}", flush=True)
    return pd.DataFrame(filas)


def curva(t) -> pd.DataFrame:
    """Curva de aprendizaje: se submuestrea por **grupo**, no por fila.

    Tomar filas al azar partiría andamios entre lo que entra y lo que no, y la
    curva mediría otra cosa: cuánto ayuda ver más análogos del mismo esqueleto.
    Lo que interesa es cuánto ayuda ver más estructuras distintas.
    """
    filas = []
    for semilla in SEMILLAS:
        rng = np.random.default_rng(semilla)
        for pliegue, (tr, va) in enumerate(_particion(t.X, t.y, t.grupos, semilla), 1):
            gr = np.unique(t.grupos[tr])
            for frac in FRACCIONES:
                k = max(2, int(round(len(gr) * frac)))
                elegidos = set(rng.choice(gr, size=k, replace=False).tolist())
                sub = tr[[g in elegidos for g in t.grupos[tr]]]
                if len(np.unique(t.y[sub])) < 2:
                    continue
                for nombre, canal in canalizaciones(semilla).items():
                    m = clone(canal).fit(t.X[sub], t.y[sub])
                    met_tr = _medir(t.y[sub], m.predict_proba(t.X[sub])[:, 1])
                    met_va = _medir(t.y[va], m.predict_proba(t.X[va])[:, 1])
                    filas.append({"modelo": nombre, "semilla": semilla,
                                  "pliegue": pliegue, "fraccion": frac,
                                  "grupos": k, "n_ajuste": len(sub),
                                  "mcc_ajuste": met_tr["mcc"],
                                  "mcc_validacion": met_va["mcc"],
                                  "auroc_ajuste": met_tr["auroc"],
                                  "auroc_validacion": met_va["auroc"]})
            print(f"  curva · semilla {semilla} · pliegue {pliegue}", flush=True)
    return pd.DataFrame(filas)


def importancias(t, nombres: list[str]) -> pd.DataFrame:
    """Impureza y permutación, las dos sobre los mismos pliegues.

    La permutación se mide **sobre el pliegue de evaluación**: medida sobre el
    de ajuste diría qué memorizó el bosque, no qué necesita para generalizar.
    """
    filas = []
    for pliegue, (tr, va) in enumerate(_particion(t.X, t.y, t.grupos, 0), 1):
        bosque = clone(canalizaciones(0)["bosque"]).fit(t.X[tr], t.y[tr])
        imp = bosque.named_steps["modelo"].feature_importances_
        perm = permutation_importance(bosque, t.X[va], t.y[va],
                                      n_repeats=REPETICIONES_PERMUTACION,
                                      random_state=0, n_jobs=-1,
                                      scoring="roc_auc")
        logistica = clone(canalizaciones(0)["logistica"]).fit(t.X[tr], t.y[tr])
        coef = logistica.named_steps["modelo"].coef_[0]
        filas.append(pd.DataFrame({"pliegue": pliegue, "caracteristica": nombres,
                                   "impureza": imp,
                                   "permutacion": perm.importances_mean,
                                   "permutacion_de": perm.importances_std,
                                   "coef_logistica": coef}))
        print(f"  importancias · pliegue {pliegue}", flush=True)
    return pd.concat(filas, ignore_index=True)


def piso(t) -> pd.DataFrame:
    """Los triviales, con la misma partición: el cero contra el que se lee todo."""
    triviales = {
        "mayoritaria": DummyClassifier(strategy="most_frequent"),
        "al azar (proporción)": DummyClassifier(strategy="stratified"),
        "proporción constante": DummyClassifier(strategy="prior"),
    }
    filas = []
    for semilla in SEMILLAS:
        for pliegue, (tr, va) in enumerate(_particion(t.X, t.y, t.grupos, semilla), 1):
            for nombre, d in triviales.items():
                m = clone(d)
                if hasattr(m, "random_state"):
                    m.set_params(random_state=semilla)
                m.fit(t.X[tr], t.y[tr])
                p = m.predict_proba(t.X[va])[:, 1]
                filas.append({"modelo": nombre, "semilla": semilla,
                              "pliegue": pliegue, **_medir(t.y[va], p)})
    return pd.DataFrame(filas)


def main() -> None:
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    with Corrida("rubrica3", decision="1.5",
                 params={"tarea": "permeabilidad", "representacion": "descriptores",
                         "pliegues": PLIEGUES, "fracciones": list(FRACCIONES),
                         "repeticiones_permutacion": REPETICIONES_PERMUTACION},
                 semillas=list(SEMILLAS)) as corrida:
        t = cargar("permeabilidad")
        print(f"{t}\n", flush=True)
        nombres = list(pd.read_parquet(
            RAIZ / "data/processed/bbb_descriptores_filtrados_sin_normalizar.parquet").columns)

        t0 = time.time()
        a = ajuste(t); a.to_csv(DATOS / "rubrica3_ajuste.csv", index=False)
        c = curva(t); c.to_csv(DATOS / "rubrica3_curva.csv", index=False)
        i = importancias(t, nombres); i.to_csv(DATOS / "rubrica3_importancias.csv", index=False)
        p = piso(t); p.to_csv(DATOS / "rubrica3_piso.csv", index=False)
        print(f"\n[guardado] cuatro CSV en notebooks/datos/ · {time.time()-t0:.0f} s")

        br = a.groupby("modelo")[["brecha_mcc", "brecha_auroc"]].mean().round(4)
        print("\nBrecha media ajuste menos validación")
        print(br.to_string())
        print("\nPiso de los clasificadores triviales (MCC y AUROC medios)")
        print(p.groupby("modelo")[["mcc", "auroc"]].mean().round(4).to_string())

        corrida.metricas({
            "brecha_mcc": {m: round(float(v), 4) for m, v in br["brecha_mcc"].items()},
            "brecha_auroc": {m: round(float(v), 4) for m, v in br["brecha_auroc"].items()},
            "piso_mcc": {m: round(float(v), 4)
                         for m, v in p.groupby("modelo")["mcc"].mean().items()},
            "piso_auroc": {m: round(float(v), 4)
                           for m, v in p.groupby("modelo")["auroc"].mean().items()},
            "n_caracteristicas": len(nombres),
        })


if __name__ == "__main__":
    main()
