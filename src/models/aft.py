"""Regresión de tiempo de falla acelerado (AFT) con XGBoost: árboles para mediciones censuradas.

A diferencia del Tobit (lineal y paramétrico), el AFT con árboles potenciados modela
relaciones no lineales entre los descriptores y la potencia tolerando mediciones
censuradas por intervalos o por la derecha ([2.9](../../docs/decisiones.md#d2-9)).

El modelo ajusta:

    ln(Y) = f(X) + σ Z,

donde `Y` es la concentración biológica en µM (mayor concentración es menor potencia).
La función de pérdida minimiza la verosimilitud de supervivencia bajo censura (`survival:aft`),
recibiendo `label_lower_bound` y `label_upper_bound` en la interfaz nativa `xgb.DMatrix`.

**Distribución de pérdida (`aft_loss_distribution`):**
XGBoost admite `"normal"`, `"logistic"` y `"extreme"`. La elección por omisión es
`"normal"`, adoptada como supuesto vigente comparable a la hipótesis gaussiana del
Tobit y a la dispersión experimental reportada en ChEMBL (σ ≈ 0.7 en pActividad).
Cambiar esta distribución requiere contrastar en validación cruzada agrupada si las
colas pesadas (`"logistic"`) o asimétricas (`"extreme"`) mejoran la concordancia.

**Conversión de escala:**
XGBoost devuelve predicciones en concentración (µM). Para interoperar con el arnés y
evitar invertir el sentido del ordenamiento (que produciría una concordancia 1 − c),
`predict` convierte el resultado a pActividad:

    pActividad = 6 − log₁₀(µM).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import xgboost as xgb
from sklearn.base import BaseEstimator, RegressorMixin, check_is_fitted

from ..evaluation.regresion import limites_en_micromolar


class RegresionAFT(BaseEstimator, RegressorMixin):
    """Regresor no lineal para datos censurados mediante Accelerated Failure Time (XGBoost).

    Envuelve la interfaz de supervivencia de XGBoost adaptándola al contrato de
    `fit(X, inferior, superior)` del proyecto y convirtiendo las predicciones a pActividad.
    """

    def __init__(
        self,
        distribucion: str = "normal",
        escala: float = 1.0,
        rondas: int = 100,
        profundidad: int = 6,
        semilla: int = 0,
        n_jobs: int | None = None,
    ) -> None:
        self.distribucion = distribucion
        self.escala = escala
        self.rondas = rondas
        self.profundidad = profundidad
        self.semilla = semilla
        self.n_jobs = n_jobs

    def fit(
        self,
        X: Any,
        inferior: Any,
        superior: Any,
        grupos: Any = None,
    ) -> RegresionAFT:
        """Ajusta el modelo AFT sobre las mediciones en escala de concentración (µM).

        1. Convierte las cotas de pActividad a micromolar con `limites_en_micromolar`.
        2. Descarta filas sin cota informativa, mal definidas o contradictorias.
        3. Configura `label_lower_bound` y `label_upper_bound` en un `DMatrix`.
        4. Entrena el ensamble de árboles con la pérdida `survival:aft`.
        """
        inf_um, sup_um = limites_en_micromolar(inferior, superior)

        # Descartar lo que no informa o está mal definido:
        # inf_um > 0 y finito elimina intervalos no informativos [0, +inf], ceros e infinitos;
        # sup_um >= inf_um asegura que sup_um no sea NaN (p. ej. cota inferior en pActividad NaN)
        # ni contradictorio (sup_um < inf_um).
        valida = (inf_um > 0) & np.isfinite(inf_um) & (sup_um >= inf_um)
        self.n_descartadas_ = int((~valida).sum())

        if not np.any(valida):
            raise ValueError(
                "No hay filas válidas con cota inferior positiva en µM (inf_um > 0) para ajustar el AFT."
            )

        X_arr = np.asarray(X, dtype=float)[valida]
        inf_valid = inf_um[valida].astype(np.float32)
        sup_valid = sup_um[valida].astype(np.float32)

        self.n_features_in_ = X_arr.shape[1]

        dtrain = xgb.DMatrix(X_arr)
        dtrain.set_float_info("label_lower_bound", inf_valid)
        dtrain.set_float_info("label_upper_bound", sup_valid)

        params: dict[str, Any] = {
            "objective": "survival:aft",
            "eval_metric": "aft-nloglik",
            "aft_loss_distribution": self.distribucion,
            "aft_loss_distribution_scale": self.escala,
            "tree_method": "hist",
            "max_depth": self.profundidad,
            "seed": self.semilla,
        }
        if self.n_jobs is not None:
            params["nthread"] = self.n_jobs

        self.booster_ = xgb.train(params, dtrain, num_boost_round=self.rondas)
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predice la potencia esperada en escala de pActividad (6 − log₁₀ µM)."""
        check_is_fitted(self, "booster_")

        X_arr = np.asarray(X, dtype=float)
        dtest = xgb.DMatrix(X_arr)
        pred_um = self.booster_.predict(dtest)

        # Asegurar positividad antes del logaritmo
        pred_um_pos = np.maximum(pred_um, 1e-12)
        return 6.0 - np.log10(pred_um_pos)
