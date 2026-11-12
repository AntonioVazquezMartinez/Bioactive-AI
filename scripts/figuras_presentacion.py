"""Figuras que solo usa la presentación final, no el artículo.

Son tres, y cada una existe porque una idea no se puede explicar a tiempo con palabras:

- `anatomia.svg`: las dos formas de agrupar una molécula. Las cifras del pie salen del
  archivo curado de la patrocinadora al generar la figura, no de este texto.
- `huella.svg`: cómo se vuelve bits una molécula y qué es el Tanimoto.
- `dificultad.svg`: la semejanza ordena pero no explica el nivel. Sale de las corridas
  `2026-11-04-artemio-1.5-dificultad-de-la-prueba-permeabilidad` y `…-octava-lectura-origen-similitud`.
- `importancias.svg`: qué columnas pesan en cada fase. Sale de las dos corridas de atribución
  (`2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos` y
  `2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion`): barras de |SHAP| medio, con el lugar por
  permutación, y en azul lo que los dos métodos ponen entre sus quince primeros.
- `ranking.svg`: el ranking por fase de los compuestos de ejemplo del cuaderno 06. Sale de
  `experimentos/2026-11-12-artemio-C.5-ranking-por-fase-ejemplo`.
- `medir.svg`: lo que dice la herramienta de medir columnas nuevas en un ejemplo. Sale de
  `experimentos/2026-11-08-ingrid-1.3-ejemplo-representacion-propia`.
- `corte.svg`: dónde cae el corte y cuánto se declara permeable con cada uno. Sale de
  `experimentos/2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba`.
- Las dos se escriben en `docs/reportes/presentacion/figuras/`.

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

RDLogger.DisableLog("rdApp.*")

SALIDA = RAIZ / "docs" / "reportes" / "presentacion" / "figuras"
DATOS = RAIZ / "data" / "external" / "profesora" / "bbb_permeability_experimental.csv"
CORTES = RAIZ / "experimentos" / "2026-11-08-ingrid-C.5-umbral-en-validacion-con-prueba" / "metricas.json"
DIFICULTAD = RAIZ / "experimentos" / "2026-11-04-artemio-1.5-dificultad-de-la-prueba-permeabilidad" / "metricas.json"
TERCILES = RAIZ / "experimentos" / "2026-11-04-artemio-1.5-octava-lectura-origen-similitud" / "metricas.json"
EJEMPLO = RAIZ / "experimentos" / "2026-11-08-ingrid-1.3-ejemplo-representacion-propia" / "metricas.json"
ATRIB1 = RAIZ / "experimentos" / "2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos"
ATRIB2 = RAIZ / "experimentos" / "2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion" / "importancias.csv"
RANKING = RAIZ / "experimentos" / "2026-11-12-artemio-C.5-ranking-por-fase-ejemplo"

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


def fig_importancias() -> dict:
    """Qué pesa en cada fase: |SHAP| medio por columna, con el lugar por permutación al lado."""
    m1 = json.loads((ATRIB1 / "metricas.json").read_text(encoding="utf-8"))
    comunes1 = set(m1["interseccion_semilla0"])
    d1 = pd.read_csv(ATRIB1 / "atribucion_semilla0.csv").sort_values("shap", ascending=False).head(8)
    d1 = d1.assign(comun=d1["caracteristica"].isin(comunes1), rango_perm=d1["r_perm"], valor=d1["shap"])
    d1["nombre"] = d1["caracteristica"]
    d2 = pd.read_csv(ATRIB2).sort_values("shap", ascending=False).head(8)
    d2 = d2.assign(comun=(d2["rango_shap"] <= 15) & (d2["rango_permutacion"] <= 15),
                   rango_perm=d2["rango_permutacion"], valor=d2["shap"])
    d2["nombre"] = d2["columna"].str.replace("diana:", "diana ", regex=False)
    fig, ejes = plt.subplots(1, 2, figsize=(11.6, 4.6), gridspec_kw={"wspace": 0.75})
    for ax, d, titulo in ((ejes[0], d1, "Fase 1 · permeabilidad (svm_rbf)"), (ejes[1], d2, "Fase 2 · potencia (aft)")):
        y = range(len(d))
        ax.barh(y, d["valor"] / d["valor"].max(), color=[AZUL if c else GRIS_CLARO for c in d["comun"]], height=0.62)
        for yi, (_, fila) in zip(y, d.iterrows(), strict=True):
            ax.text(fila["valor"] / d["valor"].max() + 0.02, yi, f"perm. {int(fila['rango_perm'])}", va="center",
                    fontsize=8.5, color=AZUL if fila["comun"] else GRIS)
        ax.set_yticks(list(y), list(d["nombre"]), fontsize=9.5)
        ax.invert_yaxis()
        ax.set_xlim(0, 1.32)
        ax.set_xticks([])
        for lado in ("left", "right", "top", "bottom"):
            ax.spines[lado].set_visible(False)
        ax.set_title(titulo, fontsize=11.5, fontweight="bold", color=AZUL, loc="left")
    fig.text(0.01, -0.02, "Largo de la barra: |SHAP| medio relativo al primero. En azul, lo que SHAP y la permutación "
             "ponen los dos entre sus quince primeros;\nel número es el lugar por permutación.", fontsize=8.8, color=GRIS)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"importancias.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"fase1": list(d1["nombre"]), "fase2": list(d2["nombre"])}


def fig_ranking() -> dict:
    """El ranking por fase de los compuestos de ejemplo del cuaderno: una lista por fase, con su similitud."""
    f1 = pd.read_csv(RANKING / "ranking_fase1.csv")
    f2 = pd.read_csv(RANKING / "ranking_fase2.csv")
    fig, ejes = plt.subplots(1, 2, figsize=(11.6, 3.9), gridspec_kw={"wspace": 0.75})
    paneles = (
        (ejes[0], f1, "p_bbb_mas", "similitud_fase1", "Fase 1 · probabilidad de cruzar la barrera", 1.0,
         lambda r: f"{r['p_bbb_mas']:.2f}"),
        (ejes[1], f2, "pActividad_max", "similitud_fase2", "Fase 2 · potencia máxima predicha (pActividad)", 8.0,
         lambda r: f"{r['pActividad_max']:.1f}  ({r['mejor_diana']})"),
    )
    for ax, d, col, sim, titulo, tope, etiqueta in paneles:
        y = range(len(d))
        colores = [NARANJA if a else AZUL for a in d["aviso_extrapolacion"]]
        ax.barh(y, d[col], color=colores, height=0.62)
        for yi, (_, fila) in zip(y, d.iterrows(), strict=True):
            ax.text(fila[col] + tope * 0.015, yi, etiqueta(fila), va="center", fontsize=9, color=GRIS)
        ax.set_yticks(list(y), [f"{int(l)}. {n}" for l, n in zip(d["lugar"], d["nombre"], strict=True)], fontsize=9.5)
        ax.invert_yaxis()
        ax.set_xlim(0, tope * 1.45)
        ax.set_xticks([])
        for lado in ("left", "right", "top", "bottom"):
            ax.spines[lado].set_visible(False)
        ax.set_title(titulo, fontsize=11, fontweight="bold", color=AZUL, loc="left")
    fig.text(0.01, -0.03, "En naranja, compuestos con aviso de extrapolación (lejos de lo que el modelo vio). Son compuestos "
             "conocidos del cuaderno, no candidatos;\nvarios estaban en el entrenamiento. Cada fase se ordena por separado, "
             "sin combinarlas.", fontsize=8.8, color=GRIS)
    for ext in ("svg", "png"):
        fig.savefig(SALIDA / f"ranking.{ext}", bbox_inches="tight", facecolor="white", dpi=190)
    plt.close(fig)
    return {"fase1": list(f1["nombre"]), "fase2": list(f2["nombre"])}


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
    print("escritas en", SALIDA)
