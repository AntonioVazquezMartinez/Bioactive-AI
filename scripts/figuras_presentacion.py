"""Figuras que solo usa la presentación final, no el artículo.

Son siete, y cada una existe porque una idea no se puede explicar a tiempo con palabras:

- `anatomia.svg`: las dos formas de agrupar una molécula. Las cifras del pie salen del
  archivo curado de la patrocinadora al generar la figura, no de este texto.
- `huella.svg`: cómo se vuelve bits una molécula y qué es el Tanimoto.
- `dificultad.svg`: la semejanza ordena pero no explica el nivel. Sale de las corridas
  `2026-11-04-artemio-1.5-dificultad-de-la-prueba-permeabilidad` y `…-octava-lectura-origen-similitud`.
- `corte.svg`: dónde cae el corte y cuánto se declara permeable con cada uno. Sale de
  `experimentos/2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba`.
- `medir.svg`: lo que dice la herramienta de medir columnas nuevas en un ejemplo. Sale de
  `experimentos/2026-11-08-ingrid-1.3-ejemplo-representacion-propia`.
- `importancias.svg`: qué columnas pesan en cada fase, en un gráfico de puntos de SHAP: un punto por fila,
  su posición es el efecto de la columna en la predicción y su color el valor de la columna. **Los puntos salen de
  `experimentos/2026-11-12-artemio-C.2-puntos-shap-por-compuesto-fase1` y `…-fase2`** (`scripts/puntos_shap.py`):
  300 compuestos en la fase 1 y 3,000 **pares compuesto-diana** (una muestra) en la 2. Las dos corridas de atribución
  del 4 de noviembre (`2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos` y
  `2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion`) solo aportan la marca «confirmada por permutación»,
  y los confirmados van primero.
- `fase2_origen.svg`: la prueba de la fase 2 por procedencia de los datos, el modelo contra la línea base de peso
  molecular y TPSA. Sale de `experimentos/2026-11-03-artemio-1.5-prueba-por-rareza`: **modelo y línea base de la
  misma corrida** (reajuste), por eso en NPASS el modelo da 0.511 y no el 0.530 de la corrida registrada.
- `ranking.svg`: el ranking por fase de seis compuestos **de la prueba reservada** (sorteados con semilla 0; ningún
  modelo los vio), con la etiqueta BBB real y la mayor potencia medida junto a lo predicho. Sale de
  `experimentos/2026-11-12-artemio-C.5-ranking-por-fase-ejemplo-prueba`. El naranja marca la similitud de **esa
  fase** por debajo de `UMBRAL_EXTRAPOLACION`, no la bandera del compuesto.
- Todas se escriben en `docs/reportes/presentacion/figuras/`.

Se regenera con `python scripts/figuras_presentacion.py` y no hace falta en el CI: las
figuras están versionadas.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator as rfg
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.Scaffolds import MurckoScaffold

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from src.data_prep.splits import andamio_murcko, esqueleto_conectividad  # noqa: E402
from src.inferencia import UMBRAL_EXTRAPOLACION  # noqa: E402

RDLogger.DisableLog("rdApp.*")

SALIDA = RAIZ / "docs" / "reportes" / "presentacion" / "figuras"
DATOS = RAIZ / "data" / "external" / "profesora" / "bbb_permeability_experimental.csv"
CORTES = RAIZ / "experimentos" / "2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba" / "metricas.json"
DIFICULTAD = RAIZ / "experimentos" / "2026-11-04-artemio-1.5-dificultad-de-la-prueba-permeabilidad" / "metricas.json"
TERCILES = RAIZ / "experimentos" / "2026-11-04-artemio-1.5-octava-lectura-origen-similitud" / "metricas.json"
EJEMPLO = RAIZ / "experimentos" / "2026-11-08-ingrid-1.3-ejemplo-representacion-propia" / "metricas.json"
ATRIB1 = RAIZ / "experimentos" / "2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos"
ATRIB2 = RAIZ / "experimentos" / "2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion" / "importancias.csv"
RANKING = RAIZ / "experimentos" / "2026-11-12-artemio-C.5-ranking-por-fase-ejemplo-prueba"
RAREZA = RAIZ / "experimentos" / "2026-11-03-artemio-1.5-prueba-por-rareza" / "metricas.json"

# La morfina: alcaloide natural, BBB+, y su familia de andamios está en el archivo.
MORFINA = "CN1CCC23c4c5ccc(O)c4O[C@@H]2[C@@H](O)C=C[C@@H]3C1C5"
CODEINA = "COc1ccc2c3c1O[C@H]1[C@@H](O)C=C[C@H]4[C@@H](C2)N(C)CC[C@@]341"
AZUL, NARANJA, GRIS, GRIS_CLARO = "#1f4e79", "#d9730d", "#6b6b6b", "#c9c9c9"


def _png(mol: Chem.Mol, ancho: int = 420, alto: int = 330, resaltar=None) -> "mpimg.ArrayLike":
    d = rdMolDraw2D.MolDraw2DCairo(ancho, alto)
    o = d.drawOptions()
    o.clearBackground = False
    o.bondLineWidth = 2
    rdMolDraw2D.PrepareAndDrawMolecule(
        d, mol, highlightAtoms=list(resaltar) if resaltar else [],
        highlightAtomColors={a: (0.85, 0.45, 0.05) for a in resaltar} if resaltar else {},
    )
    d.FinishDrawing()
    return mpimg.imread(io.BytesIO(d.GetDrawingText()), format="png")


def limpiar(ax) -> None:
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)


def _panel(ax, imagen, titulo: str, pie: str) -> None:
    ax.imshow(imagen)
    ax.set_axis_off()
    ax.set_title(titulo, fontsize=12, fontweight="bold", color=AZUL, pad=6)
    ax.text(0.5, -0.06, pie, transform=ax.transAxes, ha="center", va="top",
            fontsize=8.6, color=GRIS, wrap=True)


def cifras_de_la_familia() -> dict:
    """Cuántos registros junta el esqueleto de la morfina y en cuántos andamios los parte."""
    d = pd.read_csv(DATOS, encoding="utf-8-sig").dropna(subset=["smiles_std"])
    d["mol"] = [Chem.MolFromSmiles(s) for s in d["smiles_std"]]
    d = d.dropna(subset=["mol"]).copy()
    d["andamio"] = [andamio_murcko(m) for m in d["mol"]]
    d["esqueleto"] = [esqueleto_conectividad(m) for m in d["mol"]]

    def plano(mol: Chem.Mol) -> str:
        sc = MurckoScaffold.GetScaffoldForMol(mol)
        Chem.RemoveStereochemistry(sc)
        return Chem.MolToSmiles(sc)

    d["andamio_plano"] = [plano(m) for m in d["mol"]]
    morfina = Chem.MolFromSmiles(MORFINA)
    esq = esqueleto_conectividad(morfina)
    mismo_esqueleto = d[d["esqueleto"] == esq]
    mismo_andamio = d[d["andamio_plano"] == plano(morfina)]
    return {
        "esqueleto": esq,
        "registros_del_esqueleto": len(mismo_esqueleto),
        "andamios_del_esqueleto": int(mismo_esqueleto["andamio"].nunique()),
        "esqueletos_del_andamio": int(mismo_andamio["esqueleto"].nunique()),
        "registros_del_andamio": len(mismo_andamio),
        "clases_del_andamio": mismo_andamio["bbb_class"].value_counts().to_dict(),
    }


def fig_anatomia(c: dict) -> None:
    """Las dos formas de agrupar una molécula, dibujadas sobre un alcaloide natural."""
    morfina = Chem.MolFromSmiles(MORFINA)
    andamio = MurckoScaffold.GetScaffoldForMol(morfina)
    plana = Chem.MolFromSmiles(MORFINA)
    Chem.RemoveStereochemistry(plana)

    fig = plt.figure(figsize=(12.4, 4.6))
    rejilla = fig.add_gridspec(1, 3, wspace=0.06, left=0.01, right=0.99, top=0.83, bottom=0.2)
    _panel(fig.add_subplot(rejilla[0, 0]), _png(morfina), "La molécula",
           "Morfina, un alcaloide natural que sí llega al cerebro.\nEntra como SMILES, una cadena de texto.")
    _panel(fig.add_subplot(rejilla[0, 1]), _png(andamio), "Su andamio (Bemis-Murcko)",
           f"Los anillos, sin las cadenas colgantes. Lo comparten\n{c['esqueletos_del_andamio']} compuestos del archivo "
           f"(codeína, heroína, nalorfina…):\n{c['registros_del_andamio']} registros, y los {c['registros_del_andamio']} son BBB+. "
           "Si cae entero de un\nlado, al modelo le basta con reconocerlo.")
    _panel(fig.add_subplot(rejilla[0, 2]), _png(plana), "Su esqueleto de conectividad",
           f"La misma molécula sin estereoquímica. Junta los\n{c['registros_del_esqueleto']} registros de la morfina, "
           f"que el andamio repartiría\nen {c['andamios_del_esqueleto']} grupos. Por eso agrupamos por los dos.")
    fig.suptitle("Dos formas de agrupar la misma molécula, y ninguna contiene a la otra",
                 fontsize=13.5, fontweight="bold", y=0.97)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"anatomia.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)


def fig_huella() -> dict:
    """Cómo se vuelve bits una molécula, y qué es comparar dos huellas."""
    morfina, codeina = Chem.MolFromSmiles(MORFINA), Chem.MolFromSmiles(CODEINA)
    gen = rfg.GetMorganGenerator(radius=2, fpSize=2048)
    salida = rfg.AdditionalOutput()
    salida.AllocateBitInfoMap()
    hm = gen.GetFingerprint(morfina, additionalOutput=salida)
    hc = gen.GetFingerprint(codeina)
    info = salida.GetBitInfoMap()
    bit = next(b for b in sorted(hm.GetOnBits()) if any(r == 2 for _, r in info[b]))
    centro, radio = info[bit][0]
    entorno = Chem.FindAtomEnvironmentOfRadiusN(morfina, radio, centro)
    atomos = {morfina.GetBondWithIdx(b).GetBeginAtomIdx() for b in entorno}
    atomos |= {morfina.GetBondWithIdx(b).GetEndAtomIdx() for b in entorno}
    atomos.add(centro)

    pm, pc = set(hm.GetOnBits()), set(hc.GetOnBits())
    comunes, union = pm & pc, pm | pc
    tanimoto = DataStructs.TanimotoSimilarity(hm, hc)

    fig = plt.figure(figsize=(13.0, 3.9))
    rejilla = fig.add_gridspec(1, 3, width_ratios=[1, 2.1, 1.9], wspace=0.14,
                               left=0.015, right=0.985, top=0.8, bottom=0.17)

    eje = fig.add_subplot(rejilla[0, 0])
    eje.imshow(_png(morfina, 420, 320, resaltar=atomos))
    eje.set_axis_off()
    eje.set_title("1. Un fragmento", fontsize=11.5, fontweight="bold", color=AZUL, pad=6)
    eje.text(0.5, -0.04, "Cada átomo con lo que tiene\na dos enlaces de distancia.",
             transform=eje.transAxes, ha="center", va="top", fontsize=9, color=GRIS)

    eje = fig.add_subplot(rejilla[0, 1])
    columnas, filas = 64, 32
    for i in range(filas * columnas):
        eje.add_patch(Rectangle((i % columnas, i // columnas), 0.86, 0.86, linewidth=0,
                                facecolor=NARANJA if i in pm else "#e9e9e9"))
    eje.add_patch(Rectangle((bit % columnas - 2.2, bit // columnas - 2.2), 5.2, 5.2,
                            linewidth=1.8, edgecolor=AZUL, facecolor="none"))
    eje.annotate(f"prende la casilla {bit}", (bit % columnas + 0.5, bit // columnas - 2.4),
                 xytext=(columnas * 0.5, -4.2), fontsize=9.5, color=AZUL, ha="center",
                 fontweight="bold", arrowprops={"arrowstyle": "->", "color": AZUL, "lw": 1.2})
    eje.set_xlim(-1, columnas + 1)
    eje.set_ylim(filas + 1, -6)
    eje.set_axis_off()
    eje.set_title("2. Una casilla de 2,048", fontsize=11.5, fontweight="bold", color=AZUL, pad=6)
    eje.text(0.5, -0.04, f"La morfina prende {len(pm)} de las 2,048. Eso es su huella.",
             transform=eje.transAxes, ha="center", va="top", fontsize=9, color=GRIS)

    eje = fig.add_subplot(rejilla[0, 2])
    orden = sorted(union)
    for i, b in enumerate(orden):
        for fila, prendidos in ((0, pm), (1, pc)):
            color = (AZUL if b in comunes else NARANJA) if b in prendidos else "#e9e9e9"
            eje.add_patch(Rectangle((i, fila), 0.85, 0.85, linewidth=0, facecolor=color))
    eje.set_xlim(-1, len(orden) + 1)
    eje.set_ylim(2.6, -1.2)
    eje.set_yticks([])
    eje.set_xticks([])
    eje.set_axis_off()
    for fila, nombre in ((0, "morfina"), (1, "codeína")):
        eje.text(-1.5, fila + 0.45, nombre, ha="right", va="center", fontsize=9.5, color=GRIS)
    eje.set_title("3. Comparar dos huellas: Tanimoto", fontsize=11.5, fontweight="bold",
                  color=AZUL, pad=6)
    eje.text(0.5, -0.04, f"Solo las casillas que alguna de las dos prende. En azul las {len(comunes)}\n"
             f"que comparten, de {len(union)} en total: {len(comunes)}/{len(union)} = {tanimoto:.2f}.\n"
             "Los ceros compartidos no cuentan, y por eso no es una correlación.",
             transform=eje.transAxes, ha="center", va="top", fontsize=9, color=GRIS)

    fig.suptitle("Cómo se vuelve números una molécula, y cómo se mide que dos se parezcan",
                 fontsize=13.5, fontweight="bold", y=0.985)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"huella.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"bit": bit, "morfina": len(pm), "codeina": len(pc), "comunes": len(comunes),
            "union": len(union), "tanimoto": round(tanimoto, 4)}


def fig_dificultad() -> dict:
    """Las dos mitades de la 9: la semejanza ordena dentro de la prueba, y no explica su nivel."""
    d = json.loads(DIFICULTAD.read_text(encoding="utf-8"))
    tod = json.loads(TERCILES.read_text(encoding="utf-8"))["por_origen"]["todos"]
    terciles = [tod["por_tercil"][k]["auroc"] for k in ("0", "1", "2")]
    dif = tod["parecido_menos_lejano"]

    fig, (izq, der) = plt.subplots(1, 2, figsize=(11.6, 4.2), width_ratios=[1, 1.25],
                                   gridspec_kw={"wspace": 0.3})

    barras = [("Lo que su semejanza\npredecía", d["auroc_reponderado_vecino_1"], GRIS_CLARO),
              ("Lo que de verdad\ndio la prueba", d["auroc_prueba_registrado"], NARANJA)]
    for x, (nombre, v, color) in enumerate(barras):
        izq.bar(x, v, color=color, width=0.55)
        izq.text(x, v + 0.006, f"{v:.3f}", ha="center", fontsize=12, fontweight="bold", color=GRIS)
    izq.annotate("", (1, d["auroc_prueba_registrado"]), xytext=(1, d["auroc_reponderado_vecino_1"]),
                 arrowprops={"arrowstyle": "<->", "color": AZUL, "lw": 1.6})
    izq.text(1.1, (d["auroc_prueba_registrado"] + d["auroc_reponderado_vecino_1"]) / 2,
             f"{d['diferencia_vecino_1']:.3f}\nsin explicar", fontsize=10, color=AZUL, fontweight="bold",
             va="center")
    izq.set_xticks([0, 1], [b[0] for b in barras], fontsize=10)
    izq.set_ylim(0.7, 0.93)
    izq.set_ylabel("AUROC")
    izq.set_title(f"La prueba está MÁS cerca de lo entrenado\nque la validación "
                  f"({d['similitud_prueba_media']:.3f} contra {d['similitud_validacion_media']:.3f})",
                  fontsize=11.5, fontweight="bold", color=AZUL)
    limpiar(izq)

    nombres = ["el tercio\nmás raro", "el tercio\nde en medio", "el tercio\nmás parecido"]
    for x, (nombre, v) in enumerate(zip(nombres, terciles, strict=True)):
        der.bar(x, v, color=[GRIS_CLARO, GRIS, AZUL][x], width=0.55)
        der.text(x, v + 0.006, f"{v:.3f}", ha="center", fontsize=12, fontweight="bold", color=GRIS)
    der.annotate("", (2, terciles[2] + 0.028), xytext=(0, terciles[0] + 0.028),
                 arrowprops={"arrowstyle": "->", "color": AZUL, "lw": 1.6,
                             "connectionstyle": "arc3,rad=-0.25"})
    der.text(1, terciles[2] + 0.05, f"+{dif['diferencia']:.3f}  "
             f"[{dif['ic95'][0]:.3f}, {dif['ic95'][1]:.3f}]", ha="center", fontsize=10.5,
             color=AZUL, fontweight="bold")
    der.set_xticks([0, 1, 2], nombres, fontsize=10)
    der.set_ylim(0.6, 0.95)
    der.set_title("Dentro de la prueba, la semejanza sí ordena\n(terciles cortados en 0.31 y 0.46 de Tanimoto)",
                  fontsize=11.5, fontweight="bold", color=AZUL)
    limpiar(der)

    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"dificultad.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"esperado": d["auroc_reponderado_vecino_1"], "real": d["auroc_prueba_registrado"],
            "terciles": terciles, "diferencia": dif["diferencia"]}


def fig_corte() -> dict:
    """Dónde cae el corte, cuánto declara permeable y qué MCC sale."""
    m = json.loads(CORTES.read_text(encoding="utf-8"))["fase_b"]
    real = m["prevalencia"]
    lecturas = [
        ("Elegido en validación", m["congelado"], NARANJA, "lo que haría cualquiera"),
        ("Fijo en 0.5", m["fijo_0.5"], GRIS, "la convención heredada"),
        ("Igual prevalencia", m["igual_prevalencia"], AZUL, "sin etiquetas de la prueba"),
    ]
    fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(11.4, 5.6), height_ratios=[1, 1.25],
                                        gridspec_kw={"hspace": 0.95})

    arriba.axhspan(0, 1, 0, 1, color="#f4f4f4")
    for nombre, d, color, _ in lecturas:
        x = d["corte"]
        arriba.axvline(x, color=color, lw=2.4, ymin=0.02, ymax=0.98)
        arriba.text(x, 1.12, f"{nombre}\n{x:.3f}", ha="center", va="bottom", fontsize=9,
                    color=color, fontweight="bold")
    arriba.text(0.14, 0.5, "se declara NO permeable", ha="center", va="center", fontsize=11,
                color=GRIS, fontweight="bold")
    arriba.text(0.88, 0.5, "se declara permeable", ha="center", va="center", fontsize=11,
                color=GRIS, fontweight="bold")
    arriba.set_xlim(0, 1)
    arriba.set_ylim(0, 1)
    arriba.set_yticks([])
    arriba.set_xticks([0, 0.25, 0.5, 0.75, 1])
    arriba.set_xlabel("probabilidad que da el modelo", fontsize=9.5)
    for lado in ("left", "right", "top"):
        arriba.spines[lado].set_visible(False)

    etiquetas, posiciones = [], range(len(lecturas))
    for y, (nombre, d, color, nota) in zip(posiciones, lecturas, strict=True):
        abajo.barh(y, d["fraccion_positiva"] * 100, color=color, height=0.52)
        abajo.text(d["fraccion_positiva"] * 100 + 1.2, y, f"declara {d['fraccion_positiva'] * 100:.1f}%  ·  "
                   f"MCC {d['mcc']:.3f}", va="center", fontsize=9.5, color=color, fontweight="bold")
        etiquetas.append(f"{nombre}\n{nota}")
    abajo.axvline(real * 100, color="#111111", lw=1.8, ls=(0, (5, 3)))
    abajo.text(real * 100 - 1.2, 2.62, f"lo que de verdad es permeable: {real * 100:.1f}%",
               ha="right", va="top", fontsize=9.5, fontweight="bold")
    abajo.set_yticks(list(posiciones), etiquetas, fontsize=9.5)
    abajo.set_ylim(3.1, -0.6)
    abajo.set_xlim(0, 100)
    abajo.set_xlabel("% de la prueba reservada que el modelo declara permeable", fontsize=9.5)
    for lado in ("left", "right", "top"):
        abajo.spines[lado].set_visible(False)
    abajo.set_title("Mover el corte no cambia el orden: cambia cuántos compuestos declaramos permeables",
                    fontsize=12.5, fontweight="bold", color=AZUL, loc="left", pad=14)

    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"corte.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {n: (d["corte"], d["fraccion_positiva"], d["mcc"]) for n, d, _, _ in lecturas} | {"real": real}


def fig_medir() -> dict:
    """La herramienta en un ejemplo: tres propiedades contra los 151 descriptores y contra ruido."""
    filas = {
        (d["representacion"], d["metrica"]): d
        for d in json.loads(EJEMPLO.read_text(encoding="utf-8"))["todos"]
    }
    tres = filas[("tpsa_hbd_peso", "mcc")]
    ruido = filas[("ruido_3_columnas", "mcc")]
    barras = [
        ("151 descriptores\n(la referencia)", 0.0, None, GRIS_CLARO, "referencia"),
        ("TPSA, donadores\ny peso (3 columnas)", tres["dif_media"], (tres["ic95_inf"], tres["ic95_sup"]), AZUL,
         f"{tres['dif_media']:+.3f}"),
        ("ruido, 3 columnas\n(el control)", ruido["dif_media"], (ruido["ic95_inf"], ruido["ic95_sup"]), NARANJA,
         f"{ruido['dif_media']:+.3f}"),
    ]
    fig, ax = plt.subplots(figsize=(11.4, 4.2))
    for y, (nombre, valor, ic, color, texto) in enumerate(barras):
        ax.barh(y, valor, color=color, height=0.5)
        if ic:
            ax.errorbar(valor, y, xerr=[[valor - ic[0]], [ic[1] - valor]], color="#111111", capsize=5, lw=1.6)
        x_txt = (ic[0] if ic else 0) - 0.02
        ax.text(x_txt, y, texto, va="center", ha="right", fontsize=11, fontweight="bold",
                color=color if ic else GRIS)
    ax.axvline(0, color="#111111", lw=1.4)
    ax.set_yticks(range(len(barras)), [b[0] for b in barras], fontsize=10.5)
    ax.set_ylim(2.6, -0.6)
    ax.set_xlim(-0.95, 0.1)
    ax.set_xlabel("diferencia de MCC contra los 151 descriptores, fase 1 (con intervalo de 95 %)", fontsize=10)
    for lado in ("left", "right", "top"):
        ax.spines[lado].set_visible(False)
    ax.set_title("Tres propiedades bien elegidas aprenden; el ruido no", fontsize=12.5, fontweight="bold",
                 color=AZUL, loc="left", pad=12)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"medir.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"tres": tres["dif_media"], "ruido": ruido["dif_media"]}


# nombre en español y, aparte, el código de RDKit con el que aparece en el cuaderno
NOMBRES = {
    # fase 1
    "fr_lactam": ("Lactamas", "fr_lactam"),
    "qed": ("Parecido a un fármaco", "qed"),
    "NumAliphaticCarbocycles": ("Anillos de carbono no aromáticos", "NumAliphaticCarbocycles"),
    "NumHDonors": ("Donadores de hidrógeno", "NumHDonors"),
    "EState_VSA10": ("Estado electrónico y superficie, tramo 10", "EState_VSA10"),
    "VSA_EState3": ("Estado electrónico y superficie, tramo 3", "VSA_EState3"),
    "fr_COO": ("Ácidos carboxílicos", "fr_COO"),
    "NumAtomStereoCenters": ("Centros estereogénicos", "NumAtomStereoCenters"),
    "fr_Ar_OH": ("Hidroxilos aromáticos", "fr_Ar_OH"),
    "fr_ether": ("Éteres", "fr_ether"),
    "MolLogP": ("Lipofilia", "MolLogP"),
    "TPSA": ("Superficie polar", "TPSA"),
    # fase 2
    "BertzCT": ("Complejidad topológica", "BertzCT"),
    "diana:MAOA": ("Diana MAOA", "monoamino oxidasa A"),
    "diana:MAOB": ("Diana MAOB", "monoamino oxidasa B"),
    "diana:DRD2": ("Diana DRD2", "receptor de dopamina D2"),
    "diana:LRRK2": ("Diana LRRK2", "quinasa LRRK2"),
    "fr_halogen": ("Halógenos", "fr_halogen"),
    "SMR_VSA3": ("Refractividad y superficie", "SMR_VSA3"),
    "FpDensityMorgan3": ("Densidad de la huella Morgan", "FpDensityMorgan3"),
    "SlogP_VSA10": ("Lipofilia y superficie", "SlogP_VSA10"),
    "fr_Ar_N": ("Nitrógenos aromáticos", "fr_Ar_N"),
    "PEOE_VSA1": ("Carga parcial y superficie", "PEOE_VSA1"),
}


def _puntos(ax, d: pd.DataFrame, confirmadas: set, titulo: str, etiqueta_x: str, n: int = 6) -> list:
    """Gráfico de puntos de SHAP: una fila por columna, un punto por compuesto, color = valor de la columna."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap

    mapa = LinearSegmentedColormap.from_list("bajo_alto", [AZUL, "#e4e4e4", NARANJA])
    por_shap = list(d.assign(a=d["shap"].abs()).groupby("columna")["a"].mean().sort_values(ascending=False).index)
    orden = ([c for c in por_shap if c in confirmadas] + [c for c in por_shap if c not in confirmadas])[:n]
    rng = np.random.default_rng(0)
    for y, col in enumerate(orden):
        f = d[d["columna"] == col]
        v = f["valor"].to_numpy(float)
        lo, hi = np.percentile(v, 2), np.percentile(v, 98)
        color = np.clip((v - lo) / (hi - lo), 0, 1) if hi > lo else np.full(len(v), 0.0)
        ax.scatter(f["shap"], y + rng.uniform(-0.3, 0.3, len(f)), c=color, cmap=mapa, s=11, alpha=0.9,
                   linewidths=0, vmin=0, vmax=1)
        ax.axhline(y + 0.5, color="#efefef", lw=0.8)
    ax.axvline(0, color="#333333", lw=1)
    ax.set_yticks([])
    ax.set_ylim(len(orden) - 0.45, -0.55)
    ax.set_xlabel(etiqueta_x, fontsize=10.5, color="#333333")
    ax.tick_params(axis="x", labelsize=9.5, colors=GRIS)
    for lado in ("left", "right", "top"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color("#cccccc")
    ax.set_title(titulo, fontsize=13.5, fontweight="bold", color=AZUL, loc="left", pad=30)
    # etiquetas: nombre en español y, debajo, el código; a la derecha, si la permutación lo confirma
    for y, col in enumerate(orden):
        nombre, codigo = NOMBRES.get(col, (col, ""))
        ax.text(-0.02, y - 0.1, nombre, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=11, color="#111111", fontweight="bold")
        ax.text(-0.02, y + 0.17, codigo, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=8.6, color=GRIS)
        ok = col in confirmadas
        ax.text(1.02, y, "confirmada por\npermutación" if ok else "solo SHAP", transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=8.8, color=AZUL if ok else "#a0a0a0", linespacing=1.1)
    return orden


def fig_importancias(salida: Path | None = None, nombre: str = "importancias") -> dict:
    """Qué pesa en cada fase: gráfico de puntos de SHAP por compuesto, y si la permutación lo confirma.

    Por defecto escribe `importancias` en la carpeta del deck; el artículo la llama con su carpeta y otro nombre.
    """
    salida = salida or SALIDA
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import LinearSegmentedColormap, Normalize

    carpetas = {f: sorted((RAIZ / "experimentos").glob(f"*puntos-shap-por-compuesto-{f}"))[-1] for f in ("fase1", "fase2")}
    d1 = pd.read_csv(carpetas["fase1"] / "shap_fase1.csv")
    d2 = pd.read_csv(carpetas["fase2"] / "shap_fase2.csv")
    a1 = pd.read_csv(ATRIB1 / "atribucion_semilla0.csv")
    conf1 = set(a1[(a1["r_perm"] <= 15) & (a1["r_shap"] <= 15)]["caracteristica"])
    a2 = pd.read_csv(ATRIB2)
    conf2 = set(a2[(a2["rango_shap"] <= 15) & (a2["rango_permutacion"] <= 15)]["columna"])

    fig, ejes = plt.subplots(1, 2, figsize=(11.8, 4.9), gridspec_kw={"wspace": 1.55})
    o1 = _puntos(ejes[0], d1, conf1, "Fase 1 · permeabilidad",
                 "efecto en la probabilidad de cruzar la barrera")
    o2 = _puntos(ejes[1], d2, conf2, "Fase 2 · potencia",
                 "efecto en la potencia predicha (pActividad)")
    for ax in ejes:   # guía de lectura dentro de la figura, bajo el eje
        x0, x1 = ax.get_xlim()
        ax.text(0, 1.015, "← baja la predicción", transform=ax.get_xaxis_transform(), ha="right", va="bottom",
                fontsize=8.8, color=GRIS)
        ax.text(0, 1.015, "  la sube →", transform=ax.get_xaxis_transform(), ha="left", va="bottom",
                fontsize=8.8, color=GRIS)
    mapa = LinearSegmentedColormap.from_list("bajo_alto", [AZUL, "#e4e4e4", NARANJA])
    barra = fig.colorbar(ScalarMappable(norm=Normalize(0, 1), cmap=mapa), ax=ejes, orientation="horizontal",
                         fraction=0.03, pad=0.17, aspect=45, shrink=0.28)
    barra.set_ticks([0, 1])
    barra.set_ticklabels(["valor bajo de la columna", "valor alto"], fontsize=9.5)
    barra.outline.set_visible(False)
    fig.text(0.5, -0.03, "Cada punto es un compuesto en la fase 1 (300) y un par compuesto-diana en la 2 (3,000, una muestra). "
             "Su posición dice cuánto empuja esa columna la predicción; su color, qué valor tiene.\nLos confirmados por los dos "
             "métodos van primero.", fontsize=9.6, color=GRIS, ha="center")
    for ext in ("svg", "png"):
        fig.savefig(salida / f"{nombre}.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"fase1": o1, "fase2": o2}


def fig_ranking() -> dict:
    """Seis compuestos de la prueba reservada, una lista por fase, con lo predicho junto a lo medido."""
    f1 = pd.read_csv(RANKING / "ranking_fase1.csv")
    f2 = pd.read_csv(RANKING / "ranking_fase2.csv")
    fig, ejes = plt.subplots(1, 2, figsize=(11.6, 3.9), gridspec_kw={"wspace": 0.9})
    a1, a2 = ejes
    # fase 1: probabilidad predicha y, al lado, la etiqueta real
    colores = [NARANJA if s < UMBRAL_EXTRAPOLACION else AZUL for s in f1["similitud_fase1"]]
    a1.barh(range(len(f1)), f1["p_bbb_mas"], color=colores, height=0.62)
    for yi, (_, r) in enumerate(f1.iterrows()):
        real = "cruza" if r["bbb_real"] == 1 else "no cruza"
        a1.text(1.03, yi, f"{r['p_bbb_mas']:.2f}   real: {real}", va="center", fontsize=9,
                color="#111111" if r["bbb_real"] == 1 else "#b3261e", fontweight="bold" if r["bbb_real"] == 0 else "normal")
    # fase 2: potencia predicha (barra) y la mayor medida (rombo)
    colores = [NARANJA if s < UMBRAL_EXTRAPOLACION else AZUL for s in f2["similitud_fase2"]]
    a2.barh(range(len(f2)), f2["pActividad_max"], color=colores, height=0.62)
    for yi, (_, r) in enumerate(f2.iterrows()):
        a2.scatter([r["pActividad_medida"]], [yi], marker="D", s=46, color="#111111", zorder=3)
        a2.text(10.3, yi,
                f"predicha {r['pActividad_max']:.1f} ({r['mejor_diana']})  ·  medida {r['pActividad_medida']:.1f} ({r['diana_medida']})",
                va="center", fontsize=8.6, color=GRIS)
    for ax, d, titulo, tope in ((a1, f1, "Fase 1 · probabilidad de cruzar la barrera", 1.0),
                                 (a2, f2, "Fase 2 · potencia máxima (pActividad)", 10.0)):
        ax.set_yticks(list(range(len(d))), [f"{int(l)}. {n}" for l, n in zip(d["lugar"], d["nombre"], strict=True)], fontsize=9.5)
        ax.invert_yaxis()
        ax.set_xlim(0, tope * 1.75 if ax is a1 else tope * 2.2)
        ax.set_xticks([])
        for lado in ("left", "right", "top", "bottom"):
            ax.spines[lado].set_visible(False)
        ax.set_title(titulo, fontsize=11, fontweight="bold", color=AZUL, loc="left")
    fig.text(0.01, -0.05, "Seis compuestos de la prueba reservada, que ninguno de los modelos vio, sorteados con semilla 0; no son candidatos ni una "
             "métrica. Rombo: la mayor potencia medida.\nEn naranja, similitud menor de 0.4 con lo que el modelo vio en esa fase. "
             "Cada fase se ordena por separado, sin combinarlas.", fontsize=8.8, color=GRIS)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"ranking.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"fase1": list(f1["nombre"]), "fase2": list(f2["nombre"])}


LISTA = RAIZ / "experimentos" / "2026-11-12-artemio-C.5-lista-priorizada-naturales"


def fig_lista(salida: Path | None = None, nombre: str = "lista_priorizada") -> dict:
    """Los tres primeros naturales de cada enfermedad de la lista priorizada, con su diana, potencia y barrera."""
    salida = salida or SALIDA
    d = pd.read_csv(LISTA / "por_enfermedad.csv")
    d = d[d["lugar"] <= 3]
    enfermedades = list(dict.fromkeys(d["enfermedad"]))
    fig, ax = plt.subplots(figsize=(11.6, 5.6))
    y = 0.0
    marcas, etiquetas = [], []
    for enf in enfermedades:
        g = d[d["enfermedad"] == enf]
        ax.text(0, y, enf, ha="left", va="center", fontsize=11.5, fontweight="bold", color=AZUL)
        y += 0.95
        for _, r in g.iterrows():
            nom = str(r["nombre_corto"])
            nom = "carbamato de furoindol" if nom.startswith("[(3As") else nom
            ax.barh(y, r["pActividad_predicha"], color=NARANJA if r["aviso_extrapolacion"] else AZUL, height=0.72)
            ax.text(r["pActividad_predicha"] + 0.08, y,
                    f"{r['diana']}  {r['pActividad_predicha']:.1f}  ·  cruza la barrera {r['p_bbb_mas']:.2f}", va="center",
                    fontsize=8.8, color=GRIS)
            marcas.append(y)
            etiquetas.append(nom)
            y += 1
        y += 0.45
    ax.set_yticks(marcas, etiquetas, fontsize=9.2)
    ax.set_ylim(y - 0.4, -0.7)
    ax.set_xlim(0, 12.5)
    ax.set_xticks([])
    for lado in ("left", "right", "top", "bottom"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)
    fig.text(0.01, -0.03, "Los tres primeros por enfermedad: mayor potencia predicha (pActividad) sin medición contra esa diana, con barrera "
             "probable y sin alerta PAINS. En naranja, parecido menor de 0.4 a lo visto (extrapola).\nExploratoria: el modelo de potencia no "
             "supera a una línea base en productos naturales. Sale de la corrida `2026-11-12-artemio-C.5-lista-priorizada-naturales`.",
             fontsize=8.6, color=GRIS)
    for ext in ("svg", "png"):
        fig.savefig(salida / f"{nombre}.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"enfermedades": enfermedades}


def fig_fase2_origen() -> dict:
    """La fase 2 en la prueba, por procedencia: el modelo supera a la línea base solo donde hay ChEMBL."""
    estratos = {f["estrato"]: f for f in json.loads(RAREZA.read_text(encoding="utf-8"))["fase2"]["por_estrato"]}
    orden = [("solo_chembl", "Solo ChEMBL"), ("mixto", "Mixto"), ("solo_npass", "Solo NPASS\n(productos naturales)")]
    fig, ax = plt.subplots(figsize=(7.2, 3.3))
    ancho = 0.36
    for i, (clave, _) in enumerate(orden):
        e = estratos[clave]
        ax.bar(i - ancho / 2, e["conc_aft"], ancho, color=AZUL)
        ax.bar(i + ancho / 2, e["conc_base"], ancho, color=GRIS_CLARO)
        ax.text(i - ancho / 2, e["conc_aft"] + 0.01, f"{e['conc_aft']:.3f}", ha="center", fontsize=10.5, fontweight="bold", color=AZUL)
        ax.text(i + ancho / 2, e["conc_base"] + 0.01, f"{e['conc_base']:.3f}", ha="center", fontsize=10.5, color=GRIS)
    ax.axhline(0.5, color="#333333", lw=1, ls=(0, (4, 3)))
    ax.text(2.62, 0.503, "azar", fontsize=9, color="#333333", ha="right", va="bottom")
    ax.set_xticks(range(len(orden)), [f"{o[1]}\n{estratos[o[0]]['n']:,} pares" for o in orden], fontsize=10.5)
    ax.set_ylim(0.4, 0.8)
    ax.set_xlim(-0.6, 2.7)
    ax.set_ylabel("concordancia en la prueba reservada", fontsize=10)
    for lado in ("right", "top"):
        ax.spines[lado].set_visible(False)
    ax.set_title("El modelo gana a la línea base donde hay ChEMBL\ny la pierde en los productos naturales", fontsize=12,
                 fontweight="bold", color=AZUL, loc="left", pad=12)
    ax.bar([0], [0], color=AZUL, label="modelo (aft)")
    ax.bar([0], [0], color=GRIS_CLARO, label="línea base: peso molecular, TPSA y diana")
    ax.legend(loc="upper right", fontsize=8.8, frameon=False)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"fase2_origen.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {k: (round(v["conc_aft"], 3), round(v["conc_base"], 3), v["n"]) for k, v in estratos.items()}

CV_FASE2 = RAIZ / "experimentos" / "2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura" / "metricas.json"
PRUEBA_FASE2 = RAIZ / "experimentos" / "2026-10-31-antonio-2.13-comparativa-regresion-ensambles" / "metricas.json"
EXTERNA = RAIZ / "experimentos" / "2026-11-04-artemio-2.13-muestra-de-jorge" / "metricas.json"
CONTAMINACION = RAIZ / "experimentos" / "2026-11-04-artemio-2.13-contaminacion-externa" / "metricas.json"


def fig_fase2_desempeno() -> dict:
    """Las tres mediciones del modelo de potencia —ajuste, prueba reservada y base externa— y las mismas
    tres solo en productos naturales, que es donde el proyecto las necesita y donde no gana a dos columnas."""
    cv = json.loads(CV_FASE2.read_text(encoding="utf-8"))["todos"]["aft"]["concordancia"]
    pr = json.loads(PRUEBA_FASE2.read_text(encoding="utf-8"))
    ext = json.loads(EXTERNA.read_text(encoding="utf-8"))
    base = {f["estrato"]: f for f in json.loads(RAREZA.read_text(encoding="utf-8"))["fase2"]["por_estrato"]}
    cont = json.loads(CONTAMINACION.read_text(encoding="utf-8"))["base_externa"]

    nat_prueba = pr["prueba_por_origen"]["solo_npass"]
    todos = [
        ("Validación cruzada\nen el ajuste", cv, "5 pliegues agrupados", GRIS, False, None),
        ("Prueba reservada\nquímica nueva", pr["prueba"]["aft"]["concordancia"],
         f"{pr['prueba']['aft']['n_total']:,} pares", AZUL, False, None),
        ("Prueba externa\notro equipo", ext["global"]["concordancia"], f"{ext['global']['n_total']:,} pares",
         NARANJA, True, ext["global"]["concordancia_ic95"]),
    ]
    naturales = [
        ("Prueba reservada\nsolo NPASS", nat_prueba["concordancia"], f"{nat_prueba['n_total']} pares", AZUL, False, None),
        ("Línea base\npeso y TPSA", base["solo_npass"]["conc_base"], f"{base['solo_npass']['n']} pares",
         GRIS_CLARO, False, None),
        ("Prueba externa\nsolo NPASS", ext["por_estrato"]["solo_npass"]["concordancia"],
         f"{ext['por_estrato']['solo_npass']['n_total']} pares", NARANJA, True, None),
    ]

    fig, ax = plt.subplots(figsize=(10.4, 3.9))
    xs, etiquetas = [], []
    for grupo, inicio in ((todos, 0), (naturales, 3.8)):
        for i, (nombre, v, pie, color, rayado, ic) in enumerate(grupo):
            x = inicio + i
            xs.append(x)
            ax.bar(x, v - 0.45, bottom=0.45, color=color, width=0.62,
                   hatch="///" if rayado else None, edgecolor="white", linewidth=0)
            if ic:
                ax.errorbar(x, v, yerr=[[v - ic[0]], [ic[1] - v]], fmt="none", ecolor="#333333", capsize=4, lw=1.3)
            ax.text(x, v + 0.012, f"{v:.3f}", ha="center", fontsize=12, fontweight="bold",
                    color=color if color != GRIS_CLARO else GRIS)
            etiquetas.append(f"{nombre}\n{pie}")

    ax.axhline(0.5, color="#333333", lw=1, ls=(0, (4, 3)))
    ax.text(-0.62, 0.503, "azar", fontsize=9, color="#333333", ha="left", va="bottom")
    ax.axvline(2.4, color=GRIS_CLARO, lw=1.2)
    ax.text(1.0, 0.845, "Todos los pares", ha="center", fontsize=11, fontweight="bold", color=GRIS)
    ax.text(4.8, 0.845, "Solo productos naturales", ha="center", fontsize=11, fontweight="bold", color=GRIS)
    ax.set_xticks(xs, etiquetas, fontsize=8.6)
    ax.set_ylim(0.45, 0.87)
    ax.set_xlim(-0.65, 6.15)
    ax.set_ylabel("concordancia", fontsize=10)
    limpiar(ax)
    ax.set_title("El agregado se sostiene fuera de casa; en productos naturales no gana a dos columnas",
                 fontsize=12, fontweight="bold", color=AZUL, loc="left", pad=22)
    fig.text(0.5, -0.13, f"La prueba externa (rayada) no es comparable con la reservada: se separó por compuesto y no por "
             f"andamio, y el {cont['andamio_fraccion_pares'] * 100:.1f}% de sus pares tiene un andamio que el modelo ya vio, "
             f"contra el {cont['piso_del_control'] * 100:.1f}% del control.", fontsize=8.8, color=GRIS, ha="center")
    for ext_ in ("svg", "png"):
        fig.savefig(SALIDA / f"fase2_desempeno.{ext_}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"cv": round(cv, 3), "prueba": round(pr["prueba"]["aft"]["concordancia"], 3),
            "externa": round(ext["global"]["concordancia"], 3),
            "nat_prueba": round(nat_prueba["concordancia"], 3),
            "nat_base": round(base["solo_npass"]["conc_base"], 3),
            "nat_externa": round(ext["por_estrato"]["solo_npass"]["concordancia"], 3)}


DIANA_POR_DIANA = RAIZ / "experimentos" / "2026-11-12-artemio-C.2-shap-por-diana-fase2"
# Columnas de la figura por diana, escogidas a mano por peso **y** especificidad: las que pesan en casi todas, y las
# que más distinguen a una diana de las demás (máximo entre las dianas dividido por la mediana, y de peso apreciable).
# Una regla automática por especificidad sale peor: lo más «específico» de las 201 columnas es ruido (`fr_quatN`, `fr_SH`,
# con 0.002 y 0.000). `SMR_VSA7` se quitó: pesa 0.11 en LRRK2 y es rango 20 de SHAP y 13 de permutación en la corrida de
# dos métodos, es decir una columna común y no el rasgo de una diana.
COMUNES = [("BertzCT", "complejidad"), ("fr_halogen", "halógenos"), ("FpDensityMorgan3", "densidad de huella"),
           ("SlogP_VSA10", "lipofilia/superficie"), ("PEOE_VSA1", "carga/superficie")]
PROPIAS = [("fr_hdrzone", "hidrazonas"), ("fr_ketone", "cetonas"), ("fr_prisulfonamd", "sulfonamidas"),
           ("fr_oxime", "oximas"), ("NumSpiroAtoms", "átomos espiro"), ("fr_COO", "ácidos carboxílicos"),
           ("PEOE_VSA5", "carga/superficie 5"),
           ("fr_unbrch_alkane", "alcanos sin ramas"), ("NumAromaticHeterocycles", "heterociclos aromáticos")]


def fig_shap_por_diana(salida: Path | None = None, nombre: str = "shap_por_diana") -> dict:
    """La fase 2 separada por diana: cuánto sube o baja la predicción ser esa diana, y qué química pesa en cada una."""
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

    salida = salida or SALIDA
    carpeta = DIANA_POR_DIANA
    ef = pd.read_csv(carpeta / "efecto_diana.csv")
    por = pd.read_csv(carpeta / "shap_por_diana.csv")
    ef = ef[ef["n_pares"] >= 500].sort_values("efecto_diana_media", ascending=False).reset_index(drop=True)
    dianas = ef["diana"].tolist()
    cols = [c for c, _ in COMUNES + PROPIAS]
    celdas = np.zeros((len(dianas), len(cols)))
    for i, dn in enumerate(dianas):
        f = por[por["diana"] == dn].set_index("columna")
        for j, col in enumerate(cols):
            s = f.loc[col, "spearman_valor_shap"]
            celdas[i, j] = f.loc[col, "media_abs"] * (0 if np.isnan(s) else np.sign(s))

    fig, (a, b) = plt.subplots(1, 2, figsize=(12.6, 6.0), gridspec_kw={"width_ratios": [1, 2.7], "wspace": 0.04},
                               sharey=True)
    y = np.arange(len(dianas))
    a.barh(y, ef["efecto_diana_media"], color=[NARANJA if v > 0 else AZUL for v in ef["efecto_diana_media"]], height=0.7)
    a.axvline(0, color="#333333", lw=1)
    a.set_yticks(y, [f"{d}  ({n:,})" for d, n in zip(ef["diana"], ef["n_pares"])], fontsize=10)
    a.set_ylim(len(dianas) - 0.4, -0.6)
    a.set_xlabel("efecto de ser esa diana en la potencia\n(unidades de pActividad)", fontsize=9.5, color="#333333")
    a.set_title("Lo que pone la diana", fontsize=12.5, fontweight="bold", color=AZUL, loc="left", pad=34)
    a.tick_params(axis="x", labelsize=9, colors=GRIS)
    for lado in ("right", "top", "left"):
        a.spines[lado].set_visible(False)
    a.text(0, 1.012, "← baja la predicción", transform=a.get_xaxis_transform(), ha="right", va="bottom", fontsize=8.6, color=GRIS)
    a.text(0, 1.012, "  la sube →", transform=a.get_xaxis_transform(), ha="left", va="bottom", fontsize=8.6, color=GRIS)

    tope = np.abs(celdas).max()
    im = b.imshow(celdas, aspect="auto", cmap=LinearSegmentedColormap.from_list("baja_sube", [AZUL, "#f4f4f4", NARANJA]), norm=TwoSlopeNorm(0, -tope, tope))
    for i in range(len(dianas)):
        for j in range(len(cols)):
            v = celdas[i, j]
            if abs(v) >= 0.03:
                b.text(j, i, f"{abs(v):.2f}", ha="center", va="center", fontsize=7.6,
                       color="white" if abs(v) > tope * 0.55 else "#222222")
    etiquetas = [f"{c}\n{g}" for c, g in COMUNES + PROPIAS]
    b.set_xticks(range(len(cols)), etiquetas, fontsize=7.6, rotation=60, ha="left")
    b.xaxis.tick_top()
    b.axvline(len(COMUNES) - 0.5, color="#333333", lw=1.4)
    b.tick_params(length=0)
    for lado in b.spines.values():
        lado.set_visible(False)
    b.text(len(COMUNES) / 2 - 0.5, len(dianas) + 0.15, "pesan en casi todas", ha="center", va="top", fontsize=9.5, color=GRIS)
    b.text(len(COMUNES) + len(PROPIAS) / 2 - 0.5, len(dianas) + 0.15, "pesan más en una diana que en las demás",
           ha="center", va="top", fontsize=9.5, color=GRIS)
    barra = fig.colorbar(im, ax=b, orientation="horizontal", fraction=0.04, pad=0.1, aspect=40, shrink=0.45)
    barra.set_ticks([-tope, 0, tope])
    barra.set_ticklabels(["valor alto de la columna\nbaja la potencia", "", "valor alto\nsube la potencia"], fontsize=8.6)
    barra.outline.set_visible(False)
    fig.text(0.5, -0.04, "Dianas con 500 pares o más (entre paréntesis, los pares). Cada celda es la media de |SHAP| de esa columna en los pares "
             "de esa diana; el color da la dirección.\nSon 56,241 pares, cada uno explicado por el modelo que no lo vio. "
             "Lo que el modelo aprendió, no un mecanismo.", fontsize=9, color=GRIS, ha="center")
    for ext in ("svg", "png"):
        fig.savefig(salida / f"{nombre}.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"dianas": dianas, "columnas": cols}


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    familia = cifras_de_la_familia()
    print("familia de la morfina:", familia)
    fig_anatomia(familia)
    print("huella:", fig_huella())
    print("dificultad:", fig_dificultad())
    print("cortes:", fig_corte())
    print("medir:", fig_medir())
    print("importancias:", fig_importancias())
    print("ranking:", fig_ranking())
    print("lista:", fig_lista())


    print("fase2_origen:", fig_fase2_origen())
    print("fase2_desempeno:", fig_fase2_desempeno())
    print("por diana:", fig_shap_por_diana())
    print("escritas en", SALIDA)
