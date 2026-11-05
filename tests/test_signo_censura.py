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

INF = np.inf


def test_invertir_cambia_el_lado_de_cada_censura_y_deja_las_exactas():
    inf = np.array([-INF, 6.0, 7.0])          # `> 10 µM` = (−∞, 5], `< 1 µM` = [6, ∞), exacta
    sup = np.array([5.0, INF, 7.0])
    i, s = mod.invertir_censura(inf, sup)
    assert (i[0], s[0]) == (5.0, INF)         # (−∞, 5] pasa a [5, ∞)
    assert (i[1], s[1]) == (-INF, 6.0)        # [6, ∞) pasa a (−∞, 6]
    assert (i[2], s[2]) == (7.0, 7.0)         # la exacta no cambia
