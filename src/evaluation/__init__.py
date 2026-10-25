"""Evaluación: el arnés de validación cruzada agrupada, sus métricas y sus gráficos."""

from .cv import METRICAS, evaluar, resumen, tabla_comparativa
from .regresion import (concordancia_harrell, limites_en_micromolar,
                        metricas_regresion, rmse_exactas, spearman_exactas)
from .graficos import (concordantes, curva_precision_exhaustividad, curva_roc,
                       importancias_dos_metodos, matriz_confusion)

__all__ = ["METRICAS", "evaluar", "resumen", "tabla_comparativa",
           "concordancia_harrell", "limites_en_micromolar", "metricas_regresion",
           "rmse_exactas", "spearman_exactas",
           "concordantes", "curva_roc", "curva_precision_exhaustividad",
           "matriz_confusion", "importancias_dos_metodos"]
