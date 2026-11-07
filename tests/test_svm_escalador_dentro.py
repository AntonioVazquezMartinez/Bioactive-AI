"""El `svm_rbf` lleva el escalador dentro de la calibración, no fuera (E17)."""
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

from src.models.alternativos import catalogo


def test_el_escalador_esta_dentro_de_la_calibracion():
    m = catalogo()["svm_rbf"]
    assert [n for n, _ in m.steps] == ["modelo"]
    cal = m.named_steps["modelo"]
    assert isinstance(cal, CalibratedClassifierCV)
    assert [n for n, _ in cal.estimator.steps] == ["escala", "svc"]


def test_sigue_dando_probabilidades_utiles():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 5)) * [1, 10, 100, 1, 1]
    y = (X[:, 0] + X[:, 1] / 10 > 0).astype(int)
    p = catalogo()["svm_rbf"].fit(X[:200], y[:200]).predict_proba(X[200:])[:, 1]
    assert roc_auc_score(y[200:], p) > 0.9
