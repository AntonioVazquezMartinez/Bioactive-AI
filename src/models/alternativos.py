"""Catálogo de familias **sin ensamble**, para que el equipo elija las seis del Avance 4.

La rúbrica del Avance 4 pide seis modelos «individuales, no ensambles», y la del
Avance 5 pide ensambles homogéneos y heterogéneos. Leídas juntas, el bosque
aleatorio y el boosting del baseline son ensambles homogéneos por construcción y
**pertenecen al Avance 5**: de las tres canalizaciones de `baseline.py` solo la
logística cuenta como modelo individual.

Este módulo es un catálogo, no una elección. Ofrece ocho familias con sesgos
inductivos distintos para que el equipo escoja seis y pueda explicar por qué
esas; la decisión no está escrita aquí ni se toma por omisión.

| clave | familia | escala | ¿llega a la fase 2? |
|:--|:--|:--|:--|
| `logistica` | lineal, el control interpretable de la [C.2](../../docs/decisiones.md#dc-2) | sí | sí |
| `lda` | discriminante lineal, supone covarianza común | sí | sí |
| `arbol` | un solo árbol, legible de principio a fin | no | sí |
| `knn` | basado en instancias, sin modelo explícito | sí | lento |
| `bayes` | generativo, supone independencia condicional | sí | sí |
| `svm_rbf` | núcleo, frontera no lineal | sí | caro, ver abajo |
| `svm_sgd` | lineal con pérdida de bisagra suave, por descenso estocástico | sí | sí |
| `mlp` | red de una capa oculta | sí | sí |

**El costo de `svm_rbf` está medido, no supuesto.** Sobre la matriz de la fase 2,
un solo ajuste tarda 0.59 s con 2,000 filas, 2.25 s con 4,000, 8.78 s con 8,000 y
41.62 s con 16,000: cada vez que se duplican las filas el tiempo se multiplica
por algo menos de cuatro. Extrapolando esa curva, el pliegue completo de la fase
2 —unas 43,500 filas de ajuste— queda cerca de cinco minutos, así que una sola
configuración con tres semillas y cinco pliegues ronda la hora y cuarto y una
búsqueda de hiperparámetros sobre esa familia no cabe en el calendario. En la
fase 1, con 6,306 filas, el ajuste tarda 1.1 s y no hay problema. `svm_sgd` es la
alternativa lineal que sí escala.

**Todas escalan dentro de la canalización**, nunca antes de partir. Para vecinos,
núcleo y red no es cosmético: son familias cuya distancia o cuyo gradiente
dependen de la unidad de cada columna. Se usa min–max por consistencia con la
[1.5](../../docs/decisiones.md#d1-5), que lo eligió por convergencia y no por
acierto.
"""

from __future__ import annotations

from sklearn.calibration import CalibratedClassifierCV
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

FAMILIAS = ("logistica", "lda", "arbol", "knn", "bayes", "svm_rbf", "svm_sgd", "mlp")

# Las que no terminan en un tiempo razonable sobre los 54,369 pares de la fase 2.
CARAS_EN_FASE2 = ("svm_rbf",)


def _con_escala(modelo) -> Pipeline:
    return Pipeline([("escala", MinMaxScaler()), ("modelo", modelo)])


def catalogo(semilla: int = 0) -> dict[str, Pipeline]:
    """Las ocho familias, listas para `evaluar`. Elegir seis es del equipo."""
    return {
        "logistica": _con_escala(
            LogisticRegression(max_iter=3000, random_state=semilla)),
        "lda": _con_escala(LinearDiscriminantAnalysis()),
        "arbol": Pipeline([
            ("modelo", DecisionTreeClassifier(min_samples_leaf=5,
                                              random_state=semilla))]),
        "knn": _con_escala(KNeighborsClassifier(n_neighbors=15)),
        "bayes": _con_escala(GaussianNB()),
        # SVC no da `predict_proba` por sí solo y sin ella el arnés no puede
        # medir AUROC ni AUPRC. La calibración se la agrega por fuera: en
        # scikit-learn 1.9 `probability=True` quedó deprecado a favor de esto, y
        # con `ensemble=False` ajusta un solo modelo en vez de uno por pliegue.
        "svm_rbf": _con_escala(
            CalibratedClassifierCV(SVC(random_state=semilla), ensemble=False)),
        # `modified_huber` es la pérdida que sí expone `predict_proba` en SGD.
        "svm_sgd": _con_escala(
            SGDClassifier(loss="modified_huber", max_iter=3000,
                          random_state=semilla)),
        "mlp": _con_escala(
            MLPClassifier(hidden_layer_sizes=(64,), max_iter=600,
                          random_state=semilla)),
    }


def seleccion(claves: tuple[str, ...], semilla: int = 0) -> dict[str, Pipeline]:
    """Las familias que el equipo haya elegido, por clave, fallando si no existen."""
    disponible = catalogo(semilla)
    faltan = [c for c in claves if c not in disponible]
    if faltan:
        raise ValueError(f"no están en el catálogo: {faltan}; hay {FAMILIAS}")
    return {c: disponible[c] for c in claves}
