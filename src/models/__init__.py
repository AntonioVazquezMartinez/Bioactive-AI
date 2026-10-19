"""Modelos: las canalizaciones candidatas y las tareas sobre las que corren."""

from .baseline import CANALIZACIONES, canalizaciones
from .tareas import TAREAS, Tarea, cargar

__all__ = ["CANALIZACIONES", "canalizaciones", "TAREAS", "Tarea", "cargar"]
