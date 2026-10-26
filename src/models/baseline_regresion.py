"""Los baselines de la regresión de la potencia (fase 2): piso, sin censura y con censura.

El baseline del Avance 3 clasificaba a 10 µM. La variable objetivo de la fase 2 es
ahora la **potencia** y la clase se deriva de ella ([2.9](../../docs/decisiones.md#d2-9)),
así que el baseline también cambia. Son tres, y la diferencia entre los dos últimos
es justo lo que se quiere medir:

| Baseline | Qué ve | Para qué |
|:--|:--|:--|
| `media` | las exactas; predice siempre su promedio | el piso: un modelo que no le gane no aprendió nada |
| `ridge_exactas` | solo las exactas | la regresión lineal que un baseline sencillo haría |
| `ridge_cota_imputada` | las exactas **y** las censuradas, tomando la cota como si fuera el valor | lo ingenuo de quien no quiere tirar los inactivos ni implementar una verosimilitud |
| `tobit` | las exactas y las censuradas como cotas, con su verosimilitud | la misma recta, tratando la censura como lo que es |

Los tres últimos son la misma recta con la misma penalización. `ridge_exactas` contra
`ridge_cota_imputada` mide lo que vale **no tirar los censurados**; `ridge_cota_imputada`
contra `tobit` mide lo que vale **tratarlos con una verosimilitud** en lugar de como un
valor. Sin el segundo control, un Tobit que gana sobre `ridge_exactas` no distingue las dos
cosas: el Tobit ve más filas *y* usa otra pérdida.
"""

from __future__ import annotations

import time
from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from ..evaluation.regresion import metricas_regresion, rmse_exactas
from .tobit import RegresionTobit

ALFA_RIDGE = 100.0        # penalización de Ridge; el Tobit usa la misma en su escala
CORTE_10_UM = 5.0         # pActividad 5 = 10 µM
MIN_POR_CLASE = 20        # un estrato se reporta si tiene 20 casos de cada clase derivada


class SoloExactas:
    """Entrena un modelo de sklearn con las mediciones exactas y descarta las cotas."""

    def __init__(self, modelo):
        self.modelo = modelo

    def fit(self, X, inferior, superior):
        exacta = np.isfinite(inferior) & (inferior == superior)
        self.modelo.fit(X[exacta], inferior[exacta])
        return self

    def predict(self, X):
        return self.modelo.predict(X)


class ImputadaEnCota:
    """Entrena un modelo de sklearn con las exactas y con cada censurada **tomando su cota
    como si fuera el valor medido**: un `(−∞, 5]` entra como 5 y un `[6, ∞)` como 6. Es lo
    que haría quien no quiere tirar los inactivos y no implementa una verosimilitud; sirve
    de control del Tobit. Descarta las filas sin ninguna cota y las de cotas cruzadas."""

    def __init__(self, modelo):
        self.modelo = modelo

    def fit(self, X, inferior, superior):
        util = intervalo_util(inferior, superior)
        valor = np.where(np.isfinite(inferior), inferior, superior)
        self.modelo.fit(X[util], valor[util])
        return self

    def predict(self, X):
        return self.modelo.predict(X)


class TobitComparable(RegresionTobit):
    """El Tobit con la penalización de Ridge escrita en su escala (`alfa = A / n`)."""

    def __init__(self, alfa_ridge: float = ALFA_RIDGE, max_iter: int = 300):
        super().__init__(alfa=0.0, max_iter=max_iter)
        self.alfa_ridge = alfa_ridge

    def fit(self, X, inferior, superior):
        valida = np.asarray(inferior) <= np.asarray(superior)
        self.alfa = self.alfa_ridge / max(int(valida.sum()), 1)
        return super().fit(X, inferior, superior)


def baselines() -> dict:
    return {
        "media": SoloExactas(DummyRegressor()),
        "ridge_exactas": SoloExactas(make_pipeline(StandardScaler(), Ridge(alpha=ALFA_RIDGE))),
        "ridge_cota_imputada": ImputadaEnCota(
            make_pipeline(StandardScaler(), Ridge(alpha=ALFA_RIDGE))),
        "tobit": TobitComparable(),
    }


def intervalo_util(inferior: np.ndarray, superior: np.ndarray) -> np.ndarray:
    """Las filas que informan algo: con alguna cota y sin cotas que se contradigan."""
    sin_cota = np.isneginf(inferior) & np.isposinf(superior)
    return ~sin_cota & (inferior <= superior)


def evaluar_baselines(X, inferior, superior, grupos, estratos, clase,
                      semillas: Sequence[int] = (0, 1, 2), pliegues: int = 5) -> pd.DataFrame:
    """Validación cruzada agrupada de los tres baselines; una fila por (modelo, semilla,
    pliegue, estrato).

    `clase` es la etiqueta derivada a 10 µM (1, 0 o NaN si el intervalo no decide); con ella
    se calculan MCC y AUROC cortando la potencia predicha en 5. Las métricas de regresión
    usan el intervalo completo: la concordancia con las censuradas, y Spearman y RMSE solo
    con las exactas. El estrato se reporta si tiene `MIN_POR_CLASE` casos de cada clase.
    """
    X = np.asarray(X, dtype=float)
    inferior = np.asarray(inferior, dtype=float)
    superior = np.asarray(superior, dtype=float)
    clase = np.asarray(clase, dtype=float)
    estratificar = np.where(np.isnan(clase), -1, clase).astype(int)
    filas = []
    for semilla in semillas:
        cv = StratifiedGroupKFold(pliegues, shuffle=True, random_state=semilla)
        for k, (ajuste, val) in enumerate(cv.split(X, estratificar, grupos), 1):
            for nombre, modelo in baselines().items():
                reloj = time.perf_counter()
                modelo.fit(X[ajuste], inferior[ajuste], superior[ajuste])
                seg = time.perf_counter() - reloj
                pred = modelo.predict(X[val])
                rmse_ent, _ = rmse_exactas(inferior[ajuste], superior[ajuste],
                                           modelo.predict(X[ajuste]))
                grupos_val = [("todos", np.ones(len(val), dtype=bool))]
                grupos_val += [(e, np.asarray(estratos)[val] == e)
                               for e in np.unique(np.asarray(estratos)[val])]
                for estrato, sel in grupos_val:
                    c = clase[val][sel]
                    c = c[~np.isnan(c)]
                    if estrato != "todos" and min(c.sum(), (1 - c).sum()) < MIN_POR_CLASE:
                        continue
                    m = metricas_regresion(inferior[val][sel], superior[val][sel], pred[sel])
                    decide = ~np.isnan(clase[val][sel])
                    ok = len(np.unique(clase[val][sel][decide])) == 2
                    fila = {"modelo": nombre, "semilla": semilla, "pliegue": k,
                            "estrato": estrato, "seg": seg, "rmse_entrenamiento": rmse_ent,
                            "concordancia": m["concordancia"],
                            "spearman": m["spearman_exactas"], "rmse": m["rmse_exactas"],
                            "n_exactas": m["n_exactas"],
                            "mcc": np.nan, "auroc": np.nan}
                    if ok:
                        y = clase[val][sel][decide].astype(int)
                        p = pred[sel][decide]
                        fila["mcc"] = matthews_corrcoef(y, p >= CORTE_10_UM)
                        fila["auroc"] = roc_auc_score(y, p)
                    filas.append(fila)
    return pd.DataFrame(filas)


def tabla(res: pd.DataFrame, estrato: str = "todos") -> pd.DataFrame:
    """Media por modelo, ordenada por concordancia. `desv_*` es dispersión entre
    evaluaciones, no error estándar: las semillas comparten filas."""
    r = res[res["estrato"] == estrato]
    t = r.groupby("modelo")[["concordancia", "spearman", "rmse", "mcc", "auroc",
                             "rmse_entrenamiento", "seg"]].mean()
    t.insert(1, "desv_concordancia", r.groupby("modelo")["concordancia"].std())
    return t.sort_values("concordancia", ascending=False).round(3)
