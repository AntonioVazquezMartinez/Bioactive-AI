"""Evaluación: el arnés de validación cruzada agrupada, sus métricas y sus gráficos."""

from .cv import METRICAS, evaluar, resumen, tabla_comparativa
from .graficos import (concordantes, curva_precision_exhaustividad, curva_roc,
                       importancias_dos_metodos, matriz_confusion)

__all__ = ["METRICAS", "evaluar", "resumen", "tabla_comparativa",
           "concordantes", "curva_roc", "curva_precision_exhaustividad",
           "matriz_confusion", "importancias_dos_metodos"]
