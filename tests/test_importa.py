"""Prueba mínima: los módulos de src/ se importan con el entorno del lock.

Detecta un lock roto o un import perdido en el PR, no después de fusionar. Las pruebas de
comportamiento (partición sin fuga, SortAndSlice, limpiar_descriptores) son la fase 0.7.
"""

import importlib

import pytest


@pytest.mark.parametrize("modulo", ["src.data_prep.splits", "src.features.molecular"])
def test_modulo_importa(modulo):
    importlib.import_module(modulo)
