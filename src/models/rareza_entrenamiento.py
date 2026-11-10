"""Entrenar dando más peso a la química rara (decisión 1.10, fase 1).

La rareza de una fila de ajuste es su similitud de Tanimoto (Morgan radio 2, 2048 bits) con su vecino
más cercano **dentro del pliegue de ajuste, sin contar las filas de su mismo grupo** (`grupos_cv`): si
se contaran, sus estereoisómeros y compañeros de andamio la harían parecer común. Los terciles se
toman **dentro de cada tramo de peso**, como en la corrida de prueba por rareza, para que rareza y
tamaño no vayan mezclados.

Cuatro brazos, con el mismo `svm_rbf` del catálogo (escalador dentro de la calibración):

| brazo | qué hace con la rareza |
|:--|:--|
| `A` | nada: la referencia |
| `B` | peso por fila 3, 2 y 1 en los terciles más raro, intermedio y más parecido, vía `sample_weight` |
| `C` | las mismas proporciones duplicando filas (×3, ×2, ×1) en lugar de pesar |
| `D` | control: los mismos pesos, barajados entre las filas de su mismo tramo, sin relación con la rareza |

El modelo recibe en la **última columna de X** el índice global de la fila. Con ese índice busca su
huella y su tramo en un contexto que se fija una sola vez (`fijar_contexto`); no entra al SVM. Así el
arnés (`evaluar`) sigue pasándole solo matrices, y la rareza se calcula dentro de cada pliegue.
"""
from __future__ import annotations

import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from sklearn import config_context
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

RDLogger.DisableLog("rdApp.*")

# Peso de cada tercil de rareza: 0 = el más raro, 1 = intermedio, 2 = el más parecido.
# Fijos y declarados en la 1.10: no se afinan.
PESOS_POR_TERCIL = np.array([3.0, 2.0, 1.0])
BRAZOS = ("A", "B", "C", "D")

_CTX: dict = {}


def matriz_similitud(smiles) -> np.ndarray:
    """Tanimoto de todas contra todas (Morgan radio 2, 2048 bits), en float32."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    huellas = np.zeros((len(smiles), 2048), dtype=np.float32)
    for i, s in enumerate(smiles):
        huellas[i] = gen.GetFingerprintAsNumPy(Chem.MolFromSmiles(s))
    comunes = huellas @ huellas.T
    tam = huellas.sum(axis=1)
    union = tam[:, None] + tam[None, :] - comunes
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(union > 0, comunes / union, 0.0)
    return s.astype(np.float32)


def fijar_contexto(similitud: np.ndarray, tramo: np.ndarray, grupos: np.ndarray) -> None:
    """Deja a mano lo que el modelo necesita para mirar la rareza de sus filas por índice global."""
    _CTX.clear()
    _CTX.update(similitud=similitud, tramo=np.asarray(tramo), grupos=np.asarray(grupos))


def rareza_en_ajuste(idx_ajuste: np.ndarray) -> np.ndarray:
    """Similitud de cada fila de ajuste con su vecino más cercano de otro grupo, dentro del ajuste."""
    s = _CTX["similitud"][np.ix_(idx_ajuste, idx_ajuste)].copy()
    g = _CTX["grupos"][idx_ajuste]
    s[g[:, None] == g[None, :]] = -1.0          # su mismo grupo no cuenta, tampoco ella misma
    return s.max(axis=1)


def rareza_de_validacion(idx_ajuste: np.ndarray, idx_val: np.ndarray) -> np.ndarray:
    """Similitud de cada fila de validación con su vecino más cercano del ajuste."""
    return _CTX["similitud"][np.ix_(idx_val, idx_ajuste)].max(axis=1)


def terciles_en_tramos(similitud: np.ndarray, tramo: np.ndarray) -> np.ndarray:
    """0, 1, 2 según el tercil de similitud dentro de cada tramo (0 = el más raro)."""
    t = np.zeros(len(similitud), int)
    for u in np.unique(tramo):
        sel = tramo == u
        cortes = np.quantile(similitud[sel], [1 / 3, 2 / 3])
        t[sel] = np.digitize(similitud[sel], cortes)
    return t


def pesos_de_rareza(idx_ajuste: np.ndarray) -> np.ndarray:
    """Peso por fila de ajuste (3, 2 o 1) según su tercil de rareza dentro de su tramo."""
    terc = terciles_en_tramos(rareza_en_ajuste(idx_ajuste), _CTX["tramo"][idx_ajuste])
    return PESOS_POR_TERCIL[terc]


def pesos_al_azar(pesos: np.ndarray, tramo: np.ndarray, semilla: int) -> np.ndarray:
    """Los mismos pesos barajados dentro de cada tramo: misma distribución, sin relación con la rareza."""
    rng = np.random.default_rng(semilla)
    out = pesos.copy()
    for u in np.unique(tramo):
        pos = np.flatnonzero(tramo == u)
        out[pos] = pesos[rng.permutation(pos)]
    return out


class SVMRareza(ClassifierMixin, BaseEstimator):
    """`svm_rbf` del catálogo, con el peso de rareza del brazo que le toque.

    La estructura es la del catálogo (`CalibratedClassifierCV(Pipeline(escala, SVC), ensemble=False)`),
    de modo que el brazo `A` reproduce el modelo entregado. El peso llega al `SVC` y a la calibración
    por enrutamiento de metadatos; con todos los pesos en 1 el resultado es idéntico al de no pasarlos.
    """

    necesita_grupos = True

    def __init__(self, brazo: str = "A", semilla: int = 0):
        self.brazo = brazo
        self.semilla = semilla

    def _base(self):
        svc = SVC(random_state=self.semilla).set_fit_request(sample_weight=True)
        return CalibratedClassifierCV(
            Pipeline([("escala", MinMaxScaler()), ("svc", svc)]), ensemble=False)

    def fit(self, X, y, grupos=None):
        if self.brazo not in BRAZOS:
            raise ValueError(f"brazo {self.brazo!r} no está en {BRAZOS}")
        X = np.asarray(X, float)
        y = np.asarray(y)
        idx, Xd = X[:, -1].astype(int), X[:, :-1]
        # `grupos` de `evaluar` es el de las filas de ajuste; el contexto trae el global por índice.
        # Se usa el global porque coincide fila a fila y no depende de que el arnés lo pase.
        with config_context(enable_metadata_routing=True):
            if self.brazo == "A":
                self.modelo_ = self._base().fit(Xd, y)
            else:
                w = pesos_de_rareza(idx)
                if self.brazo == "D":
                    w = pesos_al_azar(w, _CTX["tramo"][idx], self.semilla)
                if self.brazo == "B" or self.brazo == "D":
                    self.modelo_ = self._base().fit(Xd, y, sample_weight=w)
                else:   # C: duplicar filas en lugar de pesarlas
                    rep = np.repeat(np.arange(len(y)), w.astype(int))
                    self.modelo_ = self._base().fit(Xd[rep], y[rep])
        self.classes_ = self.modelo_.classes_
        return self

    def predict_proba(self, X):
        return self.modelo_.predict_proba(np.asarray(X, float)[:, :-1])

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]
