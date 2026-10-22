"""Los cuatro gráficos que pide la rúbrica del Avance 5, sobre predicciones fuera de pliegue.

Están aquí y no en la libreta por dos razones. La primera es que se usan dos
veces, en las dos fases, y una función copiada en dos celdas se desincroniza. La
segunda es de reparto: **estas funciones dibujan, no interpretan.** La rúbrica
pide una interpretación detallada de cada gráfico y esa la escribe el equipo
mirando el resultado; aquí no hay ninguna conclusión escrita de antemano.

Todas reciben `y` y `p` **fuera de pliegue** —las que devuelve `evaluar`— y no
predicciones de un modelo reajustado sobre todo el conjunto. Un gráfico hecho
sobre datos que el modelo vio en el ajuste describe la memoria del modelo y no
su desempeño, y es el mismo error que la partición agrupada existe para evitar.

Todas aceptan un `ax` y devuelven el `ax`, para que la libreta componga la
figura y controle el tamaño sin que este módulo decida por ella.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix,
                             precision_recall_curve, roc_auc_score, roc_curve)

from .cv import orientar_minoritaria


def _eje(ax: plt.Axes | None) -> plt.Axes:
    return plt.gca() if ax is None else ax


def curva_roc(y: np.ndarray, p: np.ndarray, *, ax: plt.Axes | None = None,
              etiqueta: str | None = None) -> plt.Axes:
    """Curva ROC con su AUROC, y la diagonal del azar como referencia.

    El AUROC no depende de la prevalencia, que es la razón por la que sirve para
    comparar estratos de distinta proporción de clases. Por lo mismo **no** dice
    cuánto acierta el modelo en la clase minoritaria: para eso está la curva de
    precisión-exhaustividad, que sí se mueve con la prevalencia.
    """
    ax = _eje(ax)
    y, p = np.asarray(y), np.asarray(p)
    fpr, tpr, _ = roc_curve(y, p)
    nombre = etiqueta or "modelo"
    ax.plot(fpr, tpr, label=f"{nombre} · AUROC {roc_auc_score(y, p):.3f}")
    ax.plot([0, 1], [0, 1], "--", color="0.6", linewidth=1, label="azar")
    ax.set_xlabel("tasa de falsos positivos")
    ax.set_ylabel("tasa de verdaderos positivos")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", fontsize="small")
    return ax


def curva_precision_exhaustividad(y: np.ndarray, p: np.ndarray, *,
                                  ax: plt.Axes | None = None,
                                  etiqueta: str | None = None) -> plt.Axes:
    """Precisión contra exhaustividad **de la clase minoritaria**, con su línea base.

    La orientación la decide `orientar_minoritaria`, la misma que usa el AUPRC de
    la tabla, para que la curva dibuje la clase que la tabla mide.

    **La línea base va dibujada a propósito.** Un AUPRC de 0.88 suena alto y no
    significa nada hasta saber contra qué: el azar da la prevalencia de esa
    clase, así que la distancia a esa recta horizontal es lo único legible del
    gráfico.
    """
    ax = _eje(ax)
    y, p = np.asarray(y), np.asarray(p)
    ym, pm, volteada = orientar_minoritaria(y, p)
    precision, exhaustividad, _ = precision_recall_curve(ym, pm)
    ap = average_precision_score(ym, pm)
    nombre = etiqueta or ("clase 0" if volteada else "clase 1")
    ax.plot(exhaustividad, precision, label=f"{nombre} · AUPRC {ap:.3f}")
    ax.axhline(ym.mean(), linestyle="--", color="0.6", linewidth=1,
               label=f"línea base {ym.mean():.3f}")
    ax.set_xlabel("exhaustividad")
    ax.set_ylabel("precisión")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower left", fontsize="small")
    return ax


def matriz_confusion(y: np.ndarray, p: np.ndarray, *, ax: plt.Axes | None = None,
                     umbral: float = 0.5,
                     nombres: tuple[str, str] = ("clase 0", "clase 1"),
                     ) -> plt.Axes:
    """Matriz de confusión al `umbral` que se le pase, con conteos y porcentaje de fila.

    **El umbral es un argumento, no 0.5 por decreto.** Las métricas de la tabla
    que usan una decisión binaria, como el MCC, se calculan a 0.5, así que ese es
    el valor que reproduce la tabla. Con clases desbalanceadas 0.5 no es el corte
    que un uso real elegiría, y moverlo cambia esta figura por completo: si se
    reporta otro umbral hay que decir cuál y por qué.
    """
    ax = _eje(ax)
    y = np.asarray(y)
    pred = (np.asarray(p) >= umbral).astype(int)
    m = confusion_matrix(y, pred, labels=[0, 1])
    ax.imshow(m / m.sum(axis=1, keepdims=True), cmap="Blues", vmin=0, vmax=1)
    for i in range(2):
        for j in range(2):
            fila = m[i].sum()
            pct = m[i, j] / fila if fila else float("nan")
            ax.text(j, i, f"{m[i, j]:,}\n{pct:.1%}", ha="center", va="center",
                    color="white" if pct > 0.5 else "black")
    ax.set_xticks([0, 1], [f"pred. {n}" for n in nombres])
    ax.set_yticks([0, 1], [f"real {n}" for n in nombres])
    ax.set_title(f"umbral {umbral:g}", fontsize="small")
    return ax


def concordantes(importancias: pd.DataFrame, *, n: int = 15) -> list[str]:
    """Las características que están en el top `n` de **los dos** métodos.

    Es lo que la [C.2](../../docs/decisiones.md#dc-2) exige antes de afirmar algo
    estructural: solo se reporta aquello en que dos métodos independientes
    coinciden. La impureza es barata y se sesga hacia variables de muchos
    valores; la permutación se mide sobre el pliegue de evaluación y responde
    otra pregunta. Discrepan, y la intersección es la parte defendible.
    """
    medias = importancias.groupby("caracteristica")[["impureza", "permutacion"]].mean()
    top_impureza = set(medias.nlargest(n, "impureza").index)
    top_permutacion = set(medias.nlargest(n, "permutacion").index)
    orden = medias.nlargest(n, "permutacion").index
    return [c for c in orden if c in top_impureza & top_permutacion]


def importancias_dos_metodos(importancias: pd.DataFrame, *,
                             ax: plt.Axes | None = None, n: int = 15) -> plt.Axes:
    """Top `n` por permutación, marcando las que también están en el top por impureza.

    Las barras llevan la desviación entre pliegues porque sin ella el orden de la
    cola no se puede leer: una media de 0.0004 con desviación de 0.0012 no está
    ordenada respecto a su vecina.
    """
    ax = _eje(ax)
    g = importancias.groupby("caracteristica")["permutacion"]
    medias = g.mean().nlargest(n).iloc[::-1]
    desv = g.std().reindex(medias.index)
    coinciden = set(concordantes(importancias, n=n))
    colores = ["#1f77b4" if c in coinciden else "#b0c4de" for c in medias.index]
    ax.barh(medias.index, medias.values, xerr=desv.values, color=colores,
            error_kw={"elinewidth": 1, "ecolor": "0.4"})
    ax.set_xlabel("caída de desempeño al permutar")
    ax.set_title(f"azul fuerte: también en el top {n} por impureza", fontsize="small")
    return ax
