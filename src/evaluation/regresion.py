"""Métricas de la regresión de la potencia con mediciones censuradas.

El objetivo de la fase 2 es la potencia, y una parte de las mediciones no la
dan exacta: un `> 10 µM` solo dice que la concentración es mayor que 10
([2.9](../../docs/decisiones.md#d2-9)). Una métrica que trate ese 10 como el
valor medido premia al modelo que lo repite, así que estas no lo hacen:

- **Concordancia de Harrell.** Compara solo los pares de mediciones cuyos
  intervalos no se solapan, porque solo de esos se sabe cuál es más potente.
  Tolera la censura, y es la métrica de ordenamiento para el ranking.
- **Spearman y RMSE, solo sobre las exactas.** No toleran la censura, y por eso
  se calculan sobre el subconjunto no censurado y devuelven cuántas filas lo
  forman: una cifra sin su `n` no se puede leer.

Todo está en **pActividad** (6 − log₁₀ µM, mayor es más potente) porque es la
<<<<<<< HEAD
escala del artefacto ([2.10](../../docs/decisiones.md#d2-10)). Un modelo que
ajuste en concentración (como `survival:aft` de XGBoost, candidato del Avance 5)
necesita la escala de µM, donde el sentido de la censura es el contrario;
`limites_en_micromolar` hace esa conversión y su prueba ata el signo.
=======
escala del artefacto ([2.10](../../docs/decisiones.md#d2-10)). Para ajustar
`survival:aft` hace falta la escala de concentración, donde el sentido de la
censura es el contrario; `limites_en_micromolar` hace esa conversión y su
prueba ata el signo.
>>>>>>> origin/feat/avance-4-andamiaje
"""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

# Reproducibilidad experimental de la potencia pública en ChEMBL, en unidades
# logarítmicas: es el piso del error que tiene sentido esperar. Un RMSE muy por
# debajo no es un buen resultado sino una señal de fuga de datos
# ([2.9](../../docs/decisiones.md#d2-9)). Fuentes: IC50, Kalliokoski et al. (2013),
# PLoS ONE 8(4):e61007 (σ de pIC50 ≈ 0.68); Ki, Kramer et al. (2012), J Med Chem
# 55:5165 (≈ 0.47 según Kalliokoski). La lectura contraria, que con curación
# mínima el ruido es mayor, es Landrum y Riniker (2024), J Chem Inf Model
# 64(5):1560; el número no es un consenso.
RUIDO_EXPERIMENTAL_IC50 = 0.7
RUIDO_EXPERIMENTAL_KI = 0.5


def limites_en_micromolar(limite_inferior: np.ndarray,
                          limite_superior: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pasa el intervalo de pActividad al de concentración en µM.

    La conversión **invierte el sentido**: a más potencia, menos concentración.
    Un `> 10 µM` es, en pActividad, «menor que 5» (inferior −∞, superior 5), y
<<<<<<< HEAD
    en µM es «mayor que 10» (inferior 10, superior +∞): censura por la derecha.
    Devuelve `(inferior_um, superior_um)`.
=======
    en µM es «mayor que 10» (inferior 10, superior +∞): censura por la derecha,
    que es la que `survival:aft` espera. Devuelve `(inferior_um, superior_um)`.
>>>>>>> origin/feat/avance-4-andamiaje
    """
    inf = np.asarray(limite_inferior, dtype=float)
    sup = np.asarray(limite_superior, dtype=float)
    with np.errstate(over="ignore"):
        inferior_um = np.where(np.isposinf(sup), 0.0, 10.0 ** (6.0 - sup))
        superior_um = np.where(np.isneginf(inf), np.inf, 10.0 ** (6.0 - inf))
    # Un intervalo vacío (inferior > superior: cotas que se contradicen) no tiene
    # concentración posible; se devuelve nan en los dos extremos para que quien
    # lo use lo descarte, en vez de una cota inferior mayor que la superior.
    vacio = inf > sup
    inferior_um = np.where(vacio, np.nan, inferior_um)
    superior_um = np.where(vacio, np.nan, superior_um)
    return inferior_um, superior_um


def _exactas(limite_inferior: np.ndarray, limite_superior: np.ndarray) -> np.ndarray:
    inf = np.asarray(limite_inferior, dtype=float)
    sup = np.asarray(limite_superior, dtype=float)
    return np.isfinite(inf) & (inf == sup)


def concordancia_harrell(limite_inferior: np.ndarray, limite_superior: np.ndarray,
                         prediccion: np.ndarray, bloque: int = 2000) -> float:
    """Fracción de pares comparables que el modelo ordena bien.

    Un par (i, j) es **comparable** si los intervalos no se solapan
    (`superior_i < inferior_j`): solo entonces se sabe que j es más potente. Es
    concordante si la predicción de j es mayor; un empate de predicciones cuenta
    medio. Con todas las mediciones exactas es el índice de concordancia
    ordinario. Devuelve `nan` si no hay pares comparables.
    """
    inf = np.asarray(limite_inferior, dtype=float)
    sup = np.asarray(limite_superior, dtype=float)
    pred = np.asarray(prediccion, dtype=float)
    concordantes = 0.0
    comparables = 0
    for a in range(0, len(pred), bloque):
        s = sup[a:a + bloque, None]
        p = pred[a:a + bloque, None]
        comparable = s < inf[None, :]          # i (fila) es menos potente que j
        comparables += int(comparable.sum())
        concordantes += float((comparable & (p < pred[None, :])).sum())
        concordantes += 0.5 * float((comparable & (p == pred[None, :])).sum())
    return concordantes / comparables if comparables else float("nan")


def spearman_exactas(limite_inferior: np.ndarray, limite_superior: np.ndarray,
                     prediccion: np.ndarray) -> tuple[float, int]:
    """Spearman sobre las mediciones exactas; devuelve `(rho, n)`."""
    e = _exactas(limite_inferior, limite_superior)
    if e.sum() < 3:
        return float("nan"), int(e.sum())
    rho = spearmanr(np.asarray(limite_inferior, dtype=float)[e],
                    np.asarray(prediccion, dtype=float)[e]).statistic
    return float(rho), int(e.sum())


def rmse_exactas(limite_inferior: np.ndarray, limite_superior: np.ndarray,
                 prediccion: np.ndarray) -> tuple[float, int]:
    """RMSE sobre las mediciones exactas; devuelve `(rmse, n)`. Es solo del
    subconjunto no censurado, y así hay que declararlo donde se reporte."""
    e = _exactas(limite_inferior, limite_superior)
    if not e.any():
        return float("nan"), 0
    error = (np.asarray(limite_inferior, dtype=float)[e]
             - np.asarray(prediccion, dtype=float)[e])
    return float(np.sqrt(np.mean(error ** 2))), int(e.sum())


def metricas_regresion(limite_inferior: np.ndarray, limite_superior: np.ndarray,
                       prediccion: np.ndarray) -> dict[str, float]:
    """Las tres métricas con las cuentas que permiten leerlas."""
    rho, n_rho = spearman_exactas(limite_inferior, limite_superior, prediccion)
    rmse, n_rmse = rmse_exactas(limite_inferior, limite_superior, prediccion)
    return {
        "concordancia": concordancia_harrell(limite_inferior, limite_superior, prediccion),
        "spearman_exactas": rho,
        "rmse_exactas": rmse,
        "n_exactas": n_rmse,
        "n_total": int(len(prediccion)),
        "fraccion_censurada": 1.0 - n_rmse / max(len(prediccion), 1),
    }
