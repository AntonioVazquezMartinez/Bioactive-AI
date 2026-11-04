#!/usr/bin/env python3
"""Las figuras del artículo, leídas de las corridas registradas en `experimentos/`.

Cada figura sale de los `metricas.json` de una corrida; no se teclea ninguna cifra salvo las
dos que vienen de corridas más viejas y se marcan `# de:` con su corrida. Escribe SVG (para el
PDF) y PNG (para el sitio) en `docs/reportes/articulo/figuras/`.

    ./env312/bin/python scripts/figuras_articulo.py

Paleta: la de referencia de `dataviz` (azul = el modelo que se entrega, naranja = lo que se mide
sobre datos nuevos, gris = todo lo demás). Una figura, un mensaje; el título lo dice.
"""
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
EXP = RAIZ / "experimentos"
SALIDA = RAIZ / "docs" / "reportes" / "articulo" / "figuras"

AZUL, NARANJA, GRIS, GRIS_CLARO = "#2a78d6", "#eb6834", "#8d8c85", "#cfcec7"
TINTA, TINTA_2, REJILLA = "#0b0b0b", "#52514e", "#e7e6e1"

ESCALERA = "2026-11-03-artemio-1.2-escalera-ampliada-permeabilidad"
RAREZA = "2026-11-03-artemio-1.5-prueba-por-rareza"
TAM1 = "2026-11-03-artemio-1.3-tamano-huellas-permeabilidad"
TAM2 = "2026-11-03-artemio-1.3-tamano-huellas-actividad"
UMBRAL = "2026-11-04-artemio-2.13-mcc-por-umbral-aft-contra-bosque"
MCC_PRUEBA = 0.3385        # de: 2026-11-01-artemio-1.5-modelo-final-permeabilidad
CONC_CV_NPASS = 0.6322     # de: 2026-10-31-antonio-2.13-comparativa-regresion-ensambles

plt.rcParams.update({
    "font.family": "sans-serif", "font.size": 9.5, "text.color": TINTA,
    "axes.edgecolor": REJILLA, "axes.labelcolor": TINTA_2, "axes.linewidth": 0.8,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 10.5,
    "axes.titlelocation": "left", "figure.dpi": 150, "svg.fonttype": "none",
})


def leer(corrida: str) -> dict:
    return json.loads((EXP / corrida / "metricas.json").read_text(encoding="utf-8"))


def limpiar(ax, y_rejilla=True):
    ax.grid(axis="y" if y_rejilla else "x", color=REJILLA, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def guardar(fig, nombre: str) -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"{nombre}.{ext}", bbox_inches="tight", facecolor="white", dpi=200)
    plt.close(fig)
    print("  ", nombre)


AUROC_PRUEBA = 0.7928      # de: 2026-11-01-artemio-1.5-modelo-final-permeabilidad


def fig_escalera() -> None:
    """AUROC en cada peldaño de la escalera de agrupación, y dónde queda la prueba reservada."""
    d = pd.DataFrame(leer(ESCALERA)["e1_ampliada"])
    pasos = [("1 al azar", "al azar"), ("3 por andamio", "por\nandamio"),
             ("4 andamio + esqueleto (actual)", "andamio +\nesqueleto\n(el del proyecto)"),
             ("5 similitud ≥ 0.6", "similitud\n≥ 0.6"), ("5 similitud ≥ 0.5", "similitud\n≥ 0.5"),
             ("5 similitud ≥ 0.4", "similitud\n≥ 0.4")]
    fig, ax = plt.subplots(figsize=(6.6, 3.5))
    x = np.arange(len(pasos))
    for modelo, g in d.groupby("modelo"):
        if modelo == "svm_rbf":
            continue
        g = g.set_index("agrupacion").loc[[p[0] for p in pasos]]
        ax.plot(x, g["auroc"], color=GRIS_CLARO, lw=1.2, zorder=1)
    s = d[d["modelo"] == "svm_rbf"].set_index("agrupacion").loc[[p[0] for p in pasos]]
    ax.plot(x, s["auroc"], color=AZUL, lw=2.2, marker="o", ms=6, mec="white", mew=1.2, zorder=3)
    for xi, v in zip(x, s["auroc"], strict=True):
        ax.annotate(f"{v:.3f}", (xi, v), textcoords="offset points", xytext=(0, 9), ha="center",
                    fontsize=8.5, color=AZUL, fontweight="bold")
    ax.axhline(AUROC_PRUEBA, color=NARANJA, lw=1.6, ls=(0, (5, 3)), zorder=2)
    ax.text(0.02, AUROC_PRUEBA - 0.013, f"prueba reservada, AUROC {AUROC_PRUEBA:.3f}",
            fontsize=8.5, color=NARANJA, fontweight="bold", va="top")
    ax.text(len(pasos) - 1, 0.7, "gris: los otros cinco modelos", fontsize=8, color=GRIS, ha="right")
    ax.set_xticks(x, [p[1] for p in pasos], fontsize=8)
    ax.set_xlim(-0.3, len(pasos) - 0.7)
    ax.set_ylim(0.68, 1.0)
    ax.set_ylabel("AUROC del svm_rbf")
    ax.set_xlabel("→ ningún compuesto de entrenamiento puede parecerse más a uno de validación", fontsize=8.5)
    limpiar(ax)
    ax.set_title("La prueba reservada equivale a los peldaños más estrictos de la escalera")
    guardar(fig, "f1_escalera")


def fig_palancas() -> None:
    """Qué mueve el MCC: el modelo es la palanca chica."""
    d = pd.DataFrame(leer(ESCALERA)["e1_ampliada"]).dropna(subset=["mcc"])
    s = d[d["modelo"] == "svm_rbf"].set_index("agrupacion")["mcc"]
    azar = s[[k for k in s.index if k.startswith("1 ")][0]]
    estricta = s[[k for k in s.index if "≥ 0.4" in k][0]]
    filas = [  # (etiqueta, puntos de MCC, dato de qué corrida)
        ("añadir ensambles al mejor modelo individual", 0.9, GRIS),
        ("criterio de partición, con el svm_rbf entregado", 1.9, GRIS),
        ("elegir entre once modelos", 4.2, GRIS),
        ("cuánta semejanza se permite entre\nentrenamiento y validación", round(100 * (round(azar, 3) - round(estricta, 3)), 1), AZUL),
    ]
    fig, ax = plt.subplots(figsize=(6.6, 2.6))
    y = np.arange(len(filas))
    ax.barh(y, [f[1] for f in filas], color=[f[2] for f in filas], height=0.55)
    for i, f in enumerate(filas):
        ax.text(f[1] + 0.6, i, f"{f[1]:.1f}", va="center", fontsize=9.5,
                color=AZUL if f[2] == AZUL else TINTA_2, fontweight="bold" if f[2] == AZUL else None)
    ax.set_yticks(y, [f[0] for f in filas])
    ax.set_xlim(0, 38)
    ax.set_xlabel("puntos de MCC que mueve")
    limpiar(ax, y_rejilla=False)
    ax.spines["left"].set_visible(False)
    ax.set_title("Lo que más mueve el resultado no es el modelo")
    guardar(fig, "f0_palancas")


def fig_rareza() -> None:
    """La ventaja sobre la línea base de tamaño, por qué tan rara es la química."""
    r = leer(RAREZA)
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.9), sharey=True)
    fases = [("Fase 1 · permeabilidad (AUROC)", r["fase1"]["ventaja"]),
             ("Fase 2 · potencia (concordancia)", r["fase2"]["ventaja"])]
    etiquetas = ["más raro", "intermedio", "más parecido"]
    for ax, (titulo, v), color in zip(axs, fases, (AZUL, AZUL), strict=True):
        med = np.array(v["ventaja"])
        ic = np.array(v["ic95"])
        x = np.arange(3)
        ax.vlines(x, ic[:, 0], ic[:, 1], color=color, lw=2, alpha=0.35)
        ax.plot(x, med, color=color, lw=1.6, zorder=2)
        ax.scatter(x, med, color=color, s=34, zorder=3, edgecolor="white", linewidth=1)
        for xi, m, hi in zip(x, med, ic[:, 1], strict=True):
            ax.annotate(f"+{m:.3f}", (xi, hi), textcoords="offset points", xytext=(0, 4),
                        ha="center", fontsize=8.5, color=TINTA_2)
        ax.set_xticks(x, etiquetas)
        ax.set_xlim(-0.4, 2.6)
        ax.set_title(titulo, fontsize=9.5)
        limpiar(ax)
    axs[0].set_ylabel("ventaja del modelo sobre\npeso molecular y TPSA")
    axs[0].set_ylim(-0.02, 0.16)
    for ax in axs:
        ax.axhline(0, color=TINTA_2, lw=0.8)
    fig.suptitle("Lo raro de la química explica la caída en la fase 1, mucho menos en la fase 2",
                 x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.02)
    fig.tight_layout()
    guardar(fig, "f2_rareza")


def fig_huellas() -> None:
    """Las huellas, por tramo de peso, en las dos fases."""
    t1 = pd.DataFrame(leer(TAM1)["por_tramo"])
    t2 = pd.DataFrame(leer(TAM2)["por_tramo"])
    orden = ["≤250 Da", "250–350 Da", "350–500 Da", ">500 Da"]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.9))
    paneles = [(axs[0], t1, "d_auroc_medio_6_modelos", "Fase 1 · ΔAUROC al añadir huellas", "evaluaciones"),
               (axs[1], t2, "dif", "Fase 2 · Δconcordancia al añadir huellas", "evaluaciones")]
    for ax, t, col, titulo, ncol in paneles:
        t = t.set_index("estrato" if "estrato" in t.columns else "tramo").loc[orden]
        x = np.arange(len(orden))
        pocas = (t[ncol] < 10).to_numpy()
        ax.axhline(0, color=TINTA_2, lw=0.8)
        ax.plot(x[~pocas], t[col].to_numpy()[~pocas], color=AZUL, lw=1.8, zorder=2)
        ax.scatter(x[~pocas], t[col].to_numpy()[~pocas], color=AZUL, s=34, zorder=3,
                   edgecolor="white", linewidth=1)
        ax.scatter(x[pocas], t[col].to_numpy()[pocas], facecolor="white", edgecolor=GRIS, s=34, zorder=3)
        for xi, v in zip(x, t[col].to_numpy(), strict=True):
            ax.annotate(f"{v:+.3f}".replace("-", "−"), (xi, v), textcoords="offset points",
                        xytext=(0, 7), ha="center", fontsize=8.5, color=TINTA_2)
        ax.set_xticks(x, [o.replace(" Da", "") for o in orden])
        ax.set_xlabel("peso molecular (Da)")
        ax.set_title(titulo, fontsize=9.5)
        limpiar(ax)
    axs[0].set_ylim(-0.045, 0.01)
    axs[1].set_ylim(-0.008, 0.016)
    fig.text(0.0, -0.03, "círculo vacío: solo 3 evaluaciones (tramo con pocos datos)", fontsize=7.5, color=GRIS)
    fig.suptitle("Las huellas no ayudan en la fase 1; en la fase 2 ayudan más cuanto más pesada la molécula",
                 x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.02)
    fig.tight_layout()
    guardar(fig, "f3_huellas")


def fig_aft() -> None:
    """El AFT en NPASS, y de dónde viene su ventaja en MCC."""
    r = leer(RAREZA)["fase2"]["por_estrato"]
    npass = next(f for f in r if f["estrato"] == "solo_npass")
    u = leer(UMBRAL)["todos"]
    fig, axs = plt.subplots(1, 2, figsize=(6.6, 2.9), gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axs[0]
    barras = [("AFT\nvalidación\ncruzada", CONC_CV_NPASS, AZUL),
              ("AFT\nprueba", npass["conc_aft"], NARANJA),
              ("peso + TPSA\nprueba", npass["conc_base"], GRIS_CLARO)]
    ax.bar(range(3), [b[1] for b in barras], color=[b[2] for b in barras], width=0.6)
    for i, b in enumerate(barras):
        ax.text(i, b[1] + 0.008, f"{b[1]:.3f}", ha="center", fontsize=9, color=TINTA_2, fontweight="bold")
    ax.set_xticks(range(3), [b[0] for b in barras], fontsize=8)
    ax.set_ylim(0.4, 0.7)
    ax.set_title("Pares solo-NPASS (concordancia)", fontsize=9.5)
    limpiar(ax)

    ax = axs[1]
    lecturas = [("corte fijo\nen 5", u["mcc_fijo"]), ("corte de igual\nprevalencia", u["mcc_prevalencia"])]
    x = np.arange(2)
    ancho = 0.34
    ax.bar(x - ancho / 2, [l[1]["aft"] for l in lecturas], ancho, color=AZUL)
    ax.bar(x + ancho / 2, [l[1]["bosque"] for l in lecturas], ancho, color=GRIS_CLARO)
    for xi, l in zip(x, lecturas, strict=True):
        ax.text(xi, max(l[1]["aft"], l[1]["bosque"]) + 0.02, f"+{l[1]['dif_media']:.3f}", ha="center",
                fontsize=9, color=TINTA_2, fontweight="bold")
    ax.text(-0.17, 0.02, "AFT", ha="center", fontsize=8, color="white", fontweight="bold")
    ax.text(0.17, 0.02, "bosque", ha="center", fontsize=7.5, color=TINTA_2)
    ax.set_xticks(x, [l[0] for l in lecturas], fontsize=8)
    ax.set_ylim(0, 0.62)
    ax.set_title("Ventaja en MCC (todos los pares)", fontsize=9.5)
    limpiar(ax)
    fig.suptitle("En NPASS el AFT no se sostiene en la prueba, y su ventaja en MCC era colocación",
                 x=0.0, ha="left", fontweight="bold", fontsize=10.5, y=1.02)
    fig.tight_layout()
    guardar(fig, "f4_aft")


def main() -> int:
    print("figuras ->", SALIDA)
    for f in (fig_palancas, fig_escalera, fig_rareza, fig_huellas, fig_aft):
        f()
    return 0


if __name__ == "__main__":
    sys.exit(main())
