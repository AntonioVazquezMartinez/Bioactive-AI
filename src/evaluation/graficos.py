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


def concordantes(importancias: pd.DataFrame, *, n: int = 15,
                 columna: str = "impureza") -> list[str]:
    """Las características que están en el top `n` de **los dos** métodos.

    Es lo que la [C.2](../../docs/decisiones.md#dc-2) exige antes de afirmar algo
    estructural: solo se reporta aquello en que dos métodos independientes
    coinciden. La permutación se mide sobre el pliegue de evaluación, y el otro
    método responde otra pregunta. Discrepan, y la intersección es la parte
    defendible.

    **`columna` es el primer método, y cuál es depende de la fase**, porque no es el
    mismo en las dos: en la fase 1 es `impureza`, la ganancia interna de los árboles,
    barata y sesgada hacia variables de muchos valores; en la fase 2 es
    `shap_media_abs`, la media de |[TreeSHAP](../../docs/glosario.md)| en pActividad.
    Llamar `impureza` a las dos cosas fue un defecto real: dos corridas hermanas de la
    C.2 traían esa columna con métodos distintos dentro. El nombre se pasa explícito
    para que la corrida diga cuál usó; el valor por omisión es el de la fase 1, que es
    quien ya llamaba a esta función.
    """
    medias = importancias.groupby("caracteristica")[[columna, "permutacion"]].mean()
    top_primero = set(medias.nlargest(n, columna).index)
    top_permutacion = set(medias.nlargest(n, "permutacion").index)
    orden = medias.nlargest(n, "permutacion").index
    return [c for c in orden if c in top_primero & top_permutacion]


def importancias_dos_metodos(importancias: pd.DataFrame, *,
                             ax: plt.Axes | None = None, n: int = 15,
                             columna: str = "impureza") -> plt.Axes:
    """Top `n` por permutación, marcando las que también están en el top del otro método.

    Las barras llevan la desviación entre pliegues porque sin ella el orden de la
    cola no se puede leer: una media de 0.0004 con desviación de 0.0012 no está
    ordenada respecto a su vecina. `columna` nombra el otro método, y el título lo
    dice, porque no es el mismo en las dos fases: ver `concordantes`.
    """
    ax = _eje(ax)
    g = importancias.groupby("caracteristica")["permutacion"]
    medias = g.mean().nlargest(n).iloc[::-1]
    desv = g.std().reindex(medias.index)
    coinciden = set(concordantes(importancias, n=n, columna=columna))
    colores = ["#1f77b4" if c in coinciden else "#b0c4de" for c in medias.index]
    ax.barh(medias.index, medias.values, xerr=desv.values, color=colores,
            error_kw={"elinewidth": 1, "ecolor": "0.4"})
    ax.set_xlabel("caída de desempeño al permutar")
    ax.set_title(f"azul fuerte: también en el top {n} por {columna}", fontsize="small")
    return ax


def dispersion_censurada(inferior: np.ndarray, superior: np.ndarray, pred: np.ndarray, *,
                         ax: plt.Axes | None = None) -> plt.Axes:
    """Diagrama de dispersi?n entre pActividad predicha y observada, separando exactas de censuradas.

    Las mediciones exactas se grafican como puntos sobre la diagonal ideal y las
    censuradas como cotas para comprobar visualmente si el modelo respeta el
    sentido y escala de las cotas experimentales.
    """
    ax = _eje(ax)
    inf, sup, p = np.asarray(inferior), np.asarray(superior), np.asarray(pred)
    exacta = np.isfinite(inf) & (inf == sup)
    cens = ~exacta

    if exacta.any():
        ax.scatter(inf[exacta], p[exacta], alpha=0.3, s=14, color="#1f77b4",
                   label=f"exactas ({exacta.sum():,})", edgecolors="none")
        vals = inf[exacta]
        lo, hi = vals.min(), vals.max()
        ax.plot([lo, hi], [lo, hi], "--", color="0.5", linewidth=1, label="identidad")

    if cens.any():
        cota_sup = np.isneginf(inf) & np.isfinite(sup)
        if cota_sup.any():
            ax.scatter(sup[cota_sup], p[cota_sup], alpha=0.25, s=12, marker="<",
                       color="#ff7f0e", label=f"cota sup. ({cota_sup.sum():,})", edgecolors="none")
        resto = cens & ~cota_sup
        if resto.any():
            ax.scatter(inf[resto], p[resto], alpha=0.25, s=12, marker=">",
                       color="#2ca02c", label=f"otras cotas ({resto.sum():,})", edgecolors="none")

    ax.set_xlabel("pActividad observada")
    ax.set_ylabel("pActividad predicha")
    ax.legend(loc="upper left", fontsize="small")
    if exacta.any() and lo < hi:
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_aspect("equal", adjustable="box")
    return ax


def concordancia_por_estrato(res: pd.DataFrame, modelos: list[str], *,
                             ax: plt.Axes | None = None) -> plt.Axes:
    """Comparativa de concordancia de Harrell por estrato de procedencia qu?mica.

    Compara los modelos seleccionados a lo largo de los estratos ('todos',
    'solo_chembl', 'solo_npass', 'mixto') con barras de error que reflejan la
    desviaci?n est?ndar entre semillas y pliegues.
    """
    ax = _eje(ax)
    orden_estratos = [e for e in ["todos", "solo_chembl", "solo_npass", "mixto"]
                      if e in res["estrato"].unique()]
    sub = res[res["modelo"].isin(modelos) & res["estrato"].isin(orden_estratos)]

    piv_mean = sub.pivot_table(index="estrato", columns="modelo", values="concordancia",
                               aggfunc="mean").reindex(orden_estratos)
    piv_std = sub.pivot_table(index="estrato", columns="modelo", values="concordancia",
                              aggfunc="std").reindex(orden_estratos)

    mods = [m for m in modelos if m in piv_mean.columns]
    x = np.arange(len(orden_estratos))
    ancho = 0.8 / max(len(mods), 1)

    for i, mod in enumerate(mods):
        offset = (i - (len(mods) - 1) / 2) * ancho
        yerr = piv_std[mod].values if mod in piv_std else None
        ax.bar(x + offset, piv_mean[mod].values, width=ancho, yerr=yerr,
               label=mod, capsize=3, error_kw={"elinewidth": 1, "ecolor": "0.3"})

    ax.axhline(0.5, linestyle="--", color="0.6", linewidth=1, label="azar (0.500)")
    ax.set_xticks(x, orden_estratos)
    ax.set_ylabel("concordancia de Harrell")
    ax.set_ylim(0.35, 0.82)
    ax.legend(loc="lower left", fontsize="small")
    return ax


def curva_enriquecimiento(y: np.ndarray, pred: np.ndarray, *,
                          ax: plt.Axes | None = None,
                          etiqueta: str | None = None) -> plt.Axes:
    """Curva de enriquecimiento de activos ordenando por la potencia predicha.

    Calcula la fracci?n acumulada de compuestos activos conforme se inspecciona
    una fracci?n creciente de la biblioteca ordenada por potencia predicha.
    """
    ax = _eje(ax)
    y_arr = np.asarray(y)
    p_arr = np.asarray(pred)
    valido = ~np.isnan(y_arr) & ~np.isnan(p_arr)
    y_v = y_arr[valido].astype(int)
    p_v = p_arr[valido]

    if len(y_v) > 0 and y_v.sum() > 0:
        orden = np.argsort(p_v)[::-1]
        y_ord = y_v[orden]
        cum_activos = np.insert(np.cumsum(y_ord) / y_ord.sum(), 0, 0.0)
        frac_cribada = np.linspace(0, 1, len(y_ord) + 1)
        nombre = f"{etiqueta or 'modelo'} ({y_ord.sum():,} activos)"
        ax.plot(frac_cribada * 100, cum_activos * 100, label=nombre)

    if not any(ln.get_linestyle() == "--" for ln in ax.lines):
        ax.plot([0, 100], [0, 100], "--", color="0.6", linewidth=1, label="azar")

    ax.set_xlabel("% del conjunto cribado (ordenado por predicci?n)")
    ax.set_ylabel("% de activos encontrados")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 102)
    ax.legend(loc="lower right", fontsize="small")
    return ax


def ganancia_arboles(ganancias: pd.Series, *,
                     ax: plt.Axes | None = None, n: int = 20) -> plt.Axes:
    """Top `n` de variables por ganancia media de cortes.

    **Es descriptivo y no es una afirmaci?n de explicabilidad.** La C.2 exige dos
    m?todos independientes coincidiendo antes de sostener algo estructural, y la
    ganancia es uno solo, con el sesgo de la impureza. Para eso est?n `concordantes`
    e `importancias_dos_metodos` de este mismo m?dulo.
    """
    ax = _eje(ax)
    top = ganancias.nlargest(n).iloc[::-1]
    ax.barh(top.index, top.values, color="#1f77b4")
    ax.set_xlabel("ganancia media (gain)")
    return ax
