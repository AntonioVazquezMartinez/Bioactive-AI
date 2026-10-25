"""El control negativo de la comprobación del signo tiene que invertir de verdad.

Si `invertir_censura` no cambiara el sentido de las censuras, la comprobación
«la predicción respeta la cota» daría lo mismo con los dos signos y no
comprobaría nada.
"""

import importlib.util
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "verificar_signo_censura", RAIZ / "scripts" / "verificar_signo_censura.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_invertir_cambia_el_lado_de_cada_censura_y_deja_las_exactas():
    inf = np.array([10.0, 0.0, 0.1])          # `> 10`, `< 2`, exacta 0.1 µM
    sup = np.array([np.inf, 2.0, 0.1])
    i, s = mod.invertir_censura(inf, sup)
    assert (i[0], s[0]) == (0.0, 10.0)        # `> 10` pasa a `< 10`
    assert (i[1], s[1]) == (2.0, np.inf)      # `< 2` pasa a `> 2`
    assert (i[2], s[2]) == (0.1, 0.1)         # la exacta no cambia
