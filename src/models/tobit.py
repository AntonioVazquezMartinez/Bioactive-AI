"""Regresión de Tobit: el modelo lineal que acepta mediciones censuradas.

Es un modelo **individual**, no un ensamble, y es la forma más sencilla de usar
una medición que solo dice «la potencia es menor que 5» sin tratarla como si
valiera 5 ni tirarla ([2.9](../../docs/decisiones.md#d2-9)). Supone que la
potencia es normal alrededor de una combinación lineal de las entradas,

    pActividad ~ Normal(X·w + b, σ²),

y maximiza la verosimilitud de lo que cada fila **sí** dice:

- una medición exacta aporta la densidad en su valor;
- un `> L µM` (potencia menor que `U`) aporta la probabilidad de caer por debajo
  de `U`; un `< L µM` (potencia mayor que `V`), la de caer por encima.

Cada fila se da como un intervalo `[inferior, superior]` de pActividad, el mismo
que guarda el artefacto ([2.10](../../docs/decisiones.md#d2-10)): exacta si los
dos extremos coinciden, censurada si uno es infinito. Con todas exactas es la
regresión lineal por mínimos cuadrados (con la penalización L2 si `alfa > 0`).

Se ajusta con L-BFGS y gradiente analítico; las entradas se estandarizan dentro
de `fit`, así que cada pliegue aprende su propia media y varianza.
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import log_ndtr

_LOG_2PI = np.log(2.0 * np.pi)


def _log_phi(z):
    return -0.5 * z * z - 0.5 * _LOG_2PI


def _log_masa(zi, zs):
    """log(Φ(zs) − Φ(zi)) sin perder la cola: la diferencia se hace en la cola
    donde las dos probabilidades son pequeñas, no entre dos números cercanos a 1."""
    out = np.empty_like(zi)
    baja = zs <= 0
    alta = zi >= 0
    medio = ~(baja | alta)
    a, b = log_ndtr(zs[baja]), log_ndtr(zi[baja])
    out[baja] = a + np.log1p(-np.exp(b - a))
    a, b = log_ndtr(-zi[alta]), log_ndtr(-zs[alta])
    out[alta] = a + np.log1p(-np.exp(b - a))
    out[medio] = np.log(np.maximum(
        np.exp(log_ndtr(zs[medio])) - np.exp(log_ndtr(zi[medio])), 1e-300))
    return out


def verosimilitud(theta, X, inferior, superior, alfa):
    """Menos la log-verosimilitud media más la penalización, y su gradiente.

    `theta` = (pesos, sesgo, log σ).
    """
    n, p = X.shape
    w, b, s = theta[:p], theta[p], theta[p + 1]
    sigma = np.exp(s)
    mu = X @ w + b

    exacta = inferior == superior
    izq = np.isneginf(inferior) & np.isfinite(superior)       # (−∞, U]
    der = np.isfinite(inferior) & np.isposinf(superior)       # [V, +∞)
    otra = ~(exacta | izq | der) & ~(np.isneginf(inferior) & np.isposinf(superior))

    ll = np.zeros(n)
    d_mu = np.zeros(n)
    d_sigma = np.zeros(n)

    z = (superior[exacta] - mu[exacta]) / sigma
    ll[exacta] = -s + _log_phi(z)
    d_mu[exacta] = z / sigma
    d_sigma[exacta] = (z * z - 1.0) / sigma

    # (−∞, U]: log Φ(z_U); la razón φ/Φ en escala logarítmica por estabilidad
    z = (superior[izq] - mu[izq]) / sigma
    ll[izq] = log_ndtr(z)
    razon = np.exp(_log_phi(z) - ll[izq])
    d_mu[izq] = -razon / sigma
    d_sigma[izq] = -razon * z / sigma

    # [V, +∞): log Φ(−z_V)
    z = (inferior[der] - mu[der]) / sigma
    ll[der] = log_ndtr(-z)
    razon = np.exp(_log_phi(z) - ll[der])
    d_mu[der] = razon / sigma
    d_sigma[der] = razon * z / sigma

    if otra.any():                                  # intervalo finito, poco común
        zi = (inferior[otra] - mu[otra]) / sigma
        zs = (superior[otra] - mu[otra]) / sigma
        lm = _log_masa(zi, zs)
        ll[otra] = lm
        fi = np.exp(_log_phi(zi) - lm)
        fs = np.exp(_log_phi(zs) - lm)
        d_mu[otra] = (fi - fs) / sigma
        d_sigma[otra] = (fi * zi - fs * zs) / sigma

    perdida = -ll.mean() + 0.5 * alfa * float(w @ w)
    g_w = -(X.T @ d_mu) / n + alfa * w
    g_b = -d_mu.mean()
    g_s = -(d_sigma * sigma).mean()
    return perdida, np.concatenate([g_w, [g_b, g_s]])


class RegresionTobit:
    """Regresión lineal con censura por intervalos.

    No hereda de `BaseEstimator`: `fit` recibe los dos extremos del intervalo en
    lugar de un solo `y`, y una canalización de sklearn solo pasa uno.
    """

    def __init__(self, alfa: float = 1e-3, max_iter: int = 300):
        self.alfa = alfa
        self.max_iter = max_iter

    def fit(self, X, inferior, superior):
        X = np.asarray(X, dtype=float)
        inferior = np.asarray(inferior, dtype=float)
        superior = np.asarray(superior, dtype=float)
        # Un intervalo vacío (inferior > superior) es una evidencia incompatible,
        # no una medición: no tiene verosimilitud y se descarta.
        valida = inferior <= superior
        X, inferior, superior = X[valida], inferior[valida], superior[valida]
        self.n_descartadas_ = int((~valida).sum())
        self.media_ = X.mean(axis=0)
        self.escala_ = X.std(axis=0)
        self.escala_[self.escala_ == 0] = 1.0
        Z = (X - self.media_) / self.escala_

        exactas = inferior == superior
        y0 = float(np.mean(inferior[exactas])) if exactas.any() else 0.0
        s0 = float(np.log(np.std(inferior[exactas]))) if exactas.sum() > 1 else 0.0
        theta0 = np.concatenate([np.zeros(Z.shape[1]), [y0, s0]])
        r = minimize(verosimilitud, theta0, args=(Z, inferior, superior, self.alfa),
                     jac=True, method="L-BFGS-B", options={"maxiter": self.max_iter})
        p = Z.shape[1]
        self.pesos_, self.sesgo_, self.sigma_ = r.x[:p], r.x[p], float(np.exp(r.x[p + 1]))
        self.convergio_ = bool(r.success)
        return self

    def predict(self, X):
        """La potencia esperada (pActividad)."""
        Z = (np.asarray(X, dtype=float) - self.media_) / self.escala_
        return Z @ self.pesos_ + self.sesgo_
