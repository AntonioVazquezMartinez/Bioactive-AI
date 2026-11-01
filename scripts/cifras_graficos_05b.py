#!/usr/bin/env python3
"""Las cifras que acompañan a los cuatro gráficos del 05b, recalculadas.

Los gráficos de la sección 5 del notebook `05b_Ensambles_actividad.ipynb` se
leen con números que la figura no imprime: dónde se apilan las cotas, cuánto
comprime el modelo, qué factor de enriquecimiento alcanza y qué fracción de la
ganancia se lleva la diana frente a la química. Sin una orden detrás, esos
números vivirían solo en la prosa de la interpretación, que es justo lo que el
CLAUDE.md prohíbe.

    python scripts/cifras_graficos_05b.py

Tarda unos quince segundos: lee la matriz, reajusta el AFT con las 56,241
filas de ajuste y predice sobre la prueba. Las cifras del gráfico 2 no se
recalculan aquí porque ya están en `pliegues.csv` de la corrida, una fila por
modelo, semilla, pliegue y estrato.

Deja corrida en `experimentos/<id>/`, igual que cualquier otra cifra del
proyecto: lo que hace verificable un número de la lectura no es el script sino
el commit, el entorno y la huella de los datos con los que salió. Lo que
imprime es la versión legible y `metricas.json` guarda lo mismo para poder
compararlo con una corrida posterior.

**Toca la partición de prueba, y por eso pasa por `tomar_prueba`.** Es un
segundo acceso legítimo y queda registrado como tal: el modelo final ya está
elegido y commiteado, así que este recálculo no puede influir en esa elección;
solo describe figuras que ya existen. Cada ejecución añade una línea a
`experimentos/prueba.csv`, que es exactamente lo que hace visible el uso
repetido durante la revisión.

El techo del enriquecimiento es la cifra que cambia la lectura del gráfico 3.
Con prevalencia `p`, cribar una fracción `f` no puede encontrar más de `f / p`
de los activos, porque no hay más activos que encontrar. En la prueba la
prevalencia pasa del 78%, de modo que el techo del factor queda cerca de 1.27x
y el modelo lo alcanza: la curva se ve plana porque no tiene a dónde subir, no
porque el modelo falle.
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.models.aft import RegresionAFT  # noqa: E402
from src.tracking import Corrida, tomar_prueba  # noqa: E402

PROCESADOS = RAIZ / "data" / "processed"
SEMILLA = 0
FRACCIONES = (0.01, 0.05, 0.10)
# Cuántas cotas superiores hay que apilar en un mismo valor para que la franja
# vertical del gráfico 1 se vea; por debajo de esto es ruido y no se reporta.
MIN_PARA_FRANJA = 100


def enriquecimiento(y: np.ndarray, prediccion: np.ndarray,
                    fraccion: float) -> float:
    """Fracción de los activos que aparece al cribar `fraccion` del conjunto.

    Ordena por potencia predicha de mayor a menor, toma la primera `fraccion`
    y devuelve qué proporción del total de activos cayó ahí. El azar daría
    `fraccion`, de modo que el factor de enriquecimiento es el cociente.
    """
    valido = ~np.isnan(y) & ~np.isnan(prediccion)
    etiquetas = y[valido].astype(int)
    if etiquetas.sum() == 0:
        return float("nan")
    orden = np.argsort(prediccion[valido])[::-1]
    k = max(1, round(fraccion * len(etiquetas)))
    return etiquetas[orden][:k].sum() / etiquetas.sum()


def techo_enriquecimiento(prevalencia: float) -> float:
    """El factor máximo alcanzable: con prevalencia `p` nadie supera `1 / p`.

    Al cribar una fracción pequeña no se pueden encontrar más activos de los
    que caben en ella, así que un modelo perfecto encuentra `f / p` y el factor
    se topa en `1 / p`. Sin esta referencia, una curva de enriquecimiento sobre
    un conjunto desbalanceado hacia los activos se lee como fracaso del modelo.
    """
    return float("inf") if prevalencia == 0 else 1.0 / prevalencia


def cargar() -> dict:
    """La misma lectura que hacen las celdas 5 y 7 del notebook, sin huellas."""
    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    columnas = [c for c in desc.columns if c != "smiles"]

    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    util = (~(np.isneginf(inferior) & np.isposinf(superior))
            & (inferior <= superior))
    d = d[util].reset_index(drop=True)
    inferior, superior = inferior[util], superior[util]

    diana = pd.get_dummies(d["target_gene"])
    X = np.hstack([d[columnas].to_numpy("float32"),
                   diana.to_numpy("float32")])
    nombres = columnas + [f"diana={t}" for t in diana.columns]
    return {"d": d, "X": X, "nombres": nombres, "inferior": inferior,
            "superior": superior,
            "es_prueba": (d["particion"] == "prueba").to_numpy(),
            "clase": d["activo_10um"].to_numpy(float),
            "estrato": d["estrato"].to_numpy()}


def grafico_1(inf_p, sup_p, pred, cifras: dict) -> None:
    """Dónde se apilan las cotas y cuánto comprime el modelo las exactas."""
    exacta = inf_p == sup_p
    solo_cota = np.isneginf(inf_p)

    print("GRÁFICO 1 · dispersión sobre la prueba reservada\n")
    print(f"  exactas          {exacta.sum():>7,}")
    print(f"  cotas superiores {solo_cota.sum():>7,}")
    print(f"  otras cotas      {(~exacta & ~solo_cota).sum():>7,}")
    print("\n  dónde se apilan las cotas superiores, que es de dónde salen las "
          "franjas verticales")

    valores, cuentas = np.unique(sup_p[solo_cota], return_counts=True)
    franjas = {}
    for n, v in sorted(zip(cuentas, valores), reverse=True):
        if n < MIN_PARA_FRANJA:
            break
        print(f"    pActividad {v:.1f}   n={n:>5,}   "
              f"= {10 ** (6 - v):>7,.0f} µM")
        franjas[f"{v:.1f}"] = {"n": int(n), "um": round(10 ** (6 - v), 1)}
    en_franjas = sum(f["n"] for f in franjas.values())
    print(f"  las franjas listadas suman {en_franjas:,} de las "
          f"{solo_cota.sum():,} cotas superiores")
    print("  son las concentraciones de cribado de biblioteca, no valores "
          "cualesquiera (decisión 2.3)")

    pendiente, _ = np.polyfit(inf_p[exacta], pred[exacta], 1)
    print(f"\n  pendiente de predicho contra observado, solo exactas: "
          f"{pendiente:.3f}  (1.000 sería sin compresión)")
    print(f"  rango observado {inf_p[exacta].min():.1f} a "
          f"{inf_p[exacta].max():.1f}   predicho {pred[exacta].min():.1f} a "
          f"{pred[exacta].max():.1f}")

    cifras["grafico_1"] = {
        "n_prueba": int(len(inf_p)),
        "exactas": int(exacta.sum()),
        "cotas_superiores": int(solo_cota.sum()),
        "otras_cotas": int((~exacta & ~solo_cota).sum()),
        "franjas": franjas,
        "cotas_en_franjas": en_franjas,
        "pendiente": round(float(pendiente), 3),
        "rango_observado": [round(float(inf_p[exacta].min()), 1),
                            round(float(inf_p[exacta].max()), 1)],
        "rango_predicho": [round(float(pred[exacta].min()), 1),
                           round(float(pred[exacta].max()), 1)],
    }


def grafico_3(clase_p, estrato_p, pred, cifras: dict) -> None:
    """El enriquecimiento de cada estrato contra su techo, que es `1 / p`."""
    print("\n\nGRÁFICO 3 · enriquecimiento\n")
    cifras["grafico_3"] = {}
    estratos = [("todos", np.ones(len(clase_p), bool)),
                ("solo_npass", estrato_p == "solo_npass")]
    for nombre, selector in estratos:
        valido = selector & ~np.isnan(clase_p)
        prevalencia = float(clase_p[valido].mean())
        techo = techo_enriquecimiento(prevalencia)
        print(f"  {nombre}   n={valido.sum():,}   "
              f"activos={int(clase_p[valido].sum()):,}   "
              f"prevalencia={prevalencia:.1%}   techo del factor {techo:.2f}x")
        fila = {"n": int(valido.sum()),
                "activos": int(clase_p[valido].sum()),
                "prevalencia": round(prevalencia, 4),
                "techo": round(float(techo), 3)}
        for fraccion in FRACCIONES:
            encontrado = enriquecimiento(clase_p[selector], pred[selector],
                                         fraccion)
            factor = encontrado / fraccion
            print(f"    al {fraccion:.0%} cribado encuentra "
                  f"{encontrado:>6.1%} de los activos   factor {factor:.2f}x   "
                  f"= {factor / techo:.0%} del máximo posible")
            fila[f"al_{fraccion:.0%}"] = {
                "encontrado": round(float(encontrado), 4),
                "factor": round(float(factor), 3),
                "del_techo": round(float(factor / techo), 3)}
        cifras["grafico_3"][nombre] = fila
        print()
    print("  el 1% y el 5% son las dos métricas de ranking que pide la C.5 "
          "(#132)")


def grafico_4(modelo, nombres: list[str], cifras: dict) -> None:
    """Cómo se reparte la ganancia de los cortes entre química y diana."""
    print("\n\nGRÁFICO 4 · ganancia de los cortes\n")
    ganancia = pd.Series(modelo.booster_.get_score(importance_type="gain"))
    ganancia.index = [nombres[int(c[1:])] for c in ganancia.index]
    total = float(ganancia.sum())
    es_diana = ganancia.index.str.startswith("diana=")
    n_diana_total = sum(1 for n in nombres if n.startswith("diana="))
    n_quimica_total = len(nombres) - n_diana_total

    print(f"  columnas con al menos un corte   {len(ganancia)} de "
          f"{len(nombres)}")
    print(f"    de química  {(~es_diana).sum()} de {n_quimica_total}")
    print(f"    de diana    {es_diana.sum()} de {n_diana_total}")

    dos = ganancia.nlargest(2)
    mayor = str(dos.index[0])
    print(f"  la mayor, {mayor}, se lleva {dos.iloc[0] / total:.1%} de la "
          f"ganancia total (ganancia {dos.iloc[0]:,.0f})")
    print(f"  la segunda, {dos.index[1]}, {dos.iloc[1] / total:.1%} "
          f"(ganancia {dos.iloc[1]:,.0f}); la razón entre las dos es "
          f"{dos.iloc[0] / dos.iloc[1]:.1f}x")
    print(f"  las {es_diana.sum()} columnas de diana juntas   "
          f"{ganancia[es_diana].sum() / total:.1%}")
    print(f"  las {(~es_diana).sum()} columnas de química juntas   "
          f"{ganancia[~es_diana].sum() / total:.1%}")
    arriba = ganancia.nlargest(20).index
    dianas_top = sum(1 for col in arriba if col.startswith("diana="))
    print(f"  dianas dentro del top 20   {dianas_top}")

    cifras["grafico_4"] = {
        "columnas_totales": len(nombres),
        "columnas_con_corte": int(len(ganancia)),
        "quimica_con_corte": int((~es_diana).sum()),
        "quimica_totales": n_quimica_total,
        "diana_con_corte": int(es_diana.sum()),
        "diana_totales": n_diana_total,
        "mayor": mayor,
        "mayor_ganancia": round(float(dos.iloc[0]), 1),
        "mayor_fraccion": round(float(dos.iloc[0] / total), 4),
        "segunda": str(dos.index[1]),
        "segunda_fraccion": round(float(dos.iloc[1] / total), 4),
        "razon_primera_segunda": round(float(dos.iloc[0] / dos.iloc[1]), 2),
        "fraccion_quimica": round(float(ganancia[~es_diana].sum() / total), 4),
        "fraccion_diana": round(float(ganancia[es_diana].sum() / total), 4),
        "dianas_en_top_20": int(dianas_top),
    }
    print("\n  la ganancia está sesgada hacia variables con muchos valores "
          "distintos y no dice la dirección\n  del efecto, así que es un "
          "diagnóstico y no uno de los dos métodos de atribución de la C.2")


def main() -> None:
    datos = cargar()
    ajuste = ~datos["es_prueba"]
    prueba = datos["es_prueba"]
    cifras: dict = {}

    with Corrida("cifras-graficos", decision="2.13",
                 params={"modelo": "aft", "fracciones": list(FRACCIONES),
                         "min_para_franja": MIN_PARA_FRANJA},
                 semillas=[SEMILLA],
                 datos=[PROCESADOS / "fase2_pares.parquet",
                        PROCESADOS / "fase2_descriptores_limpios.parquet"]) as c:
        # Dentro del `with`: el entorno ya se capturó al entrar, así que la
        # línea que esta llamada añade a `prueba.csv` no marca árbol sucio.
        tomar_prueba(datos["d"], final=True,
                     motivo=("Recálculo de las cifras que acompañan a los "
                             "cuatro gráficos del 05b, con el modelo final ya "
                             "elegido"))
        print()

        modelo = clone(RegresionAFT(semilla=SEMILLA))
        modelo.fit(datos["X"][ajuste], datos["inferior"][ajuste],
                   datos["superior"][ajuste])
        pred = modelo.predict(datos["X"][prueba])

        grafico_1(datos["inferior"][prueba], datos["superior"][prueba], pred,
                  cifras)
        grafico_3(datos["clase"][prueba], datos["estrato"][prueba], pred,
                  cifras)
        grafico_4(modelo, datos["nombres"], cifras)

        c.metricas(cifras)
        print(f"\n\nCorrida: experimentos/{c.id}/")


if __name__ == "__main__":
    main()
