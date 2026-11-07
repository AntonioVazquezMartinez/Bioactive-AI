#!/usr/bin/env python3
"""¿Arreglar la configuración en los descriptores recupera algo? (fase 1, #28 y #183)

Los 217 descriptores de RDKit **no codifican configuración**. Los dos que hablan de
estereoquímica, `NumAtomStereoCenters` y `NumUnspecifiedAtomStereoCenters`, cuentan cuántos
centros hay y cuántos están sin declarar, nunca cuál de las dos formas es: dos enantiómeros dan
vectores idénticos en los 217. Medido sobre las 6,306 filas de ajuste, **183 filas (2.9%) tienen
el vector de 151 descriptores idéntico al de otra fila de clase contraria, y los 69 grupos de
choque son todos conjuntos de estereoisómeros** —misma conectividad, configuración distinta—,
ninguno por otra causa. `conteos_estereo` añade cuatro columnas (`n_R`, `n_S`, `n_E`, `n_Z`) que
distinguen la configuración, y con ellas las 183 filas bajan a **26** y los 69 grupos a 13: resuelve
157 filas y deja justo el caso que los conteos globales no pueden resolver, dos estereoisómeros con
los mismos conteos y los centros en otras posiciones.

Las huellas, que son la otra forma de meter la configuración (la [1.9](../docs/decisiones.md#d1-9)),
**no entran en esta corrida**: la [1.3](../docs/decisiones.md#d1-3) ya midió que en la fase 1
perjudican a los nueve modelos, así que la fase 1 no las va a usar con bandera ni sin ella y
medirlas otra vez no cambiaría ningún commit.

**Lo que se declara antes de correr.**

- **Brazos:** `descriptores` (los 151 de siempre) y `descriptores+estereo` (los 151 más las
  cuatro columnas). Mismos nueve modelos, semillas y pliegues que el 05c.
- **El brazo de control no es un brazo a decidir, es el arnés.** Las cifras por origen del 05c
  salieron del cuaderno y no de un script; `descriptores` tiene que reproducir las que quedaron
  registradas en `2026-10-31-artemio-1.3-ensambles-permeabilidad-huellas` (en el estrato
  `análogo estereoquímico`, 0.6958 de MCC para `svm_rbf` y 0.6187 para `knn`). Si no las
  reproduce, no se compara nada. Es el mismo control que llevaba la corrida de quiralidad.
- **Lectura 1, el techo de la representación.** Para un grupo de filas con vector idéntico, lo
  mejor que puede hacer cualquier modelo es darles a todas la clase mayoritaria del grupo. Eso
  define un oráculo exacto, sin ajustar nada, y su MCC y su AUPRC son el techo del brazo. Es lo
  que pide el [#28](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/28) y lo que la
  [1.8](../docs/decisiones.md#d1-8) dice que falta: en exactitud el techo ya estaba medido (98.1%)
  y no aprieta; en las métricas del proyecto no estaba. **Se calcula sobre las filas de ajuste**,
  no sobre las 7,805, porque la prueba reservada no se lee: la cifra publicada del 98.1% usa el
  otro denominador y las dos no son la misma.
- **Lectura 2, la sensible.** Acierto fuera de pliegue **sobre esas 183 filas**, pareado por
  modelo y semilla. Es la lectura con poder: son el 2.9% del conjunto, así que el agregado puede
  quedar plano aunque el mecanismo funcione, y por eso se declara aquí cuál de las dos manda.
- **Lectura 3, la que el equipo accionaría.** Diferencia pareada de MCC y AUPRC de la minoritaria,
  agregada y por origen, con la regla del 05c: supera el umbral —la mayor desviación del control
  entre sus 15 evaluaciones— y mejora en al menos 12 de las 15, en las dos métricas a la vez.
- **Qué diría que el arreglo sirve:** que el acierto sobre las 183 suba, y que la diferencia
  pareada de MCC en `análogo estereoquímico` sea positiva en la mayoría de los modelos. **Qué
  diría que no:** que el acierto sobre las 183 quede plano. Un agregado plano con la lectura 2
  positiva **no** refuta el mecanismo, dice que el mecanismo es pequeño; eso se escribe así y no
  se reinterpreta después.
- **Techo del alcance, medido antes de correr:** las cuatro columnas son conteos globales, así que
  13 de los 69 grupos (26 filas) siguen sin poder separarse y ningún modelo de esta corrida puede
  acertar en los dos lados de esos. Resolverlos pediría columnas posicionales, que no es esto.
- No toca la prueba reservada.

    ./env/bin/python scripts/experimento_estereo_descriptores.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"   # un hilo por modelo, como el 05c: los tiempos comparan

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from src.evaluation.cv import METRICAS, clase_minoritaria, evaluar
from src.features.molecular import CONTEOS_ESTEREO, a_mol, conteos_estereo
from src.models.ensambles_clasificacion import ensambles
from src.models.alternativos import seleccion
from src.models.tareas import DESCRIPTORES, PROCESADOS, cargar

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
BASE = ("svm_rbf", "logistica", "mlp", "knn")
ORDEN = list(BASE) + ["bosque", "boosting", "bagging_svm", "votacion", "stacking"]
PRINCIPALES = ("mcc", "auprc_minoritaria")
MINIMO_PLIEGUES = 12
CONTROL = "descriptores"
TRATAMIENTO = "descriptores+estereo"


def grupos_identicos(X: np.ndarray) -> np.ndarray:
    """Un entero por fila: filas con el mismo vector reciben el mismo."""
    _, inverso = np.unique(np.ascontiguousarray(X, dtype=float), axis=0, return_inverse=True)
    return inverso.ravel()


def oraculo(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """La mejor puntuación que esta representación permite: la prevalencia de cada grupo idéntico.

    Sirve a la vez para umbralizar —la clase mayoritaria del grupo— y para ordenar, así que da el
    techo de las tres métricas sin ajustar ningún modelo.
    """
    return pd.Series(y).groupby(grupos_identicos(X)).transform("mean").to_numpy()


def inseparables(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Máscara de las filas cuyo grupo de vector idéntico reúne las dos clases."""
    g = grupos_identicos(X)
    mezclados = pd.Series(y).groupby(g).nunique()
    return pd.Series(g).isin(set(mezclados.index[mezclados > 1])).to_numpy()


def techo(X: np.ndarray, y: np.ndarray, estratos: np.ndarray) -> dict:
    """MCC, AUPRC y exactitud del oráculo, en el agregado y por estrato."""
    p = oraculo(X, y)
    salida = {}
    for nombre, sel in {"todos": np.ones(len(y), bool),
                        **{str(e): estratos == e for e in pd.unique(estratos)}}.items():
        m = clase_minoritaria(y[sel])
        salida[nombre] = {k: round(float(f(y[sel], p[sel])), 4) for k, f in METRICAS.items()
                          if k != "auprc_minoritaria"}
        salida[nombre]["auprc_minoritaria"] = round(
            float(METRICAS["auprc_minoritaria"](y[sel], p[sel], m)), 4)
        salida[nombre]["inseparables"] = int(inseparables(X, y)[sel].sum())
        salida[nombre]["n"] = int(sel.sum())
    return salida


def acierto_en(mascara: np.ndarray, fdp: dict, y: np.ndarray) -> pd.DataFrame:
    """Acierto fuera de pliegue sobre `mascara`, una fila por (modelo, semilla)."""
    filas = []
    for modelo, p in fdp.items():
        for s, semilla in enumerate(SEMILLAS):
            pred = (p[s][mascara] >= 0.5).astype(int)
            filas.append({"modelo": modelo, "semilla": semilla,
                          "acierto": float((pred == y[mascara]).mean())})
    return pd.DataFrame(filas)


def comparacion(res: pd.DataFrame, umbrales: dict, estrato: str = "todos") -> pd.DataFrame:
    """Diferencia pareada del tratamiento contra el control, evaluación por evaluación."""
    r = res[res["estrato"] == estrato]
    filas = []
    for metrica in ("mcc", "auprc_minoritaria", "auroc"):
        p = r.pivot_table(index=["modelo", "semilla", "pliegue"], columns="brazo", values=metrica)
        if TRATAMIENTO not in p or CONTROL not in p:
            continue
        dif = (p[TRATAMIENTO] - p[CONTROL]).dropna()
        for modelo, v in dif.groupby("modelo"):
            filas.append({"modelo": modelo, "metrica": metrica, "evaluaciones": len(v),
                          "dif_media": round(float(v.mean()), 4),
                          "dif_desv": round(float(v.std()), 4),
                          "mejor_en": int((v > 0).sum())})
    c = pd.DataFrame(filas)
    c["cumple"] = (c["dif_media"] > c["metrica"].map(umbrales).fillna(np.inf)) & \
                  (c["mejor_en"] >= MINIMO_PLIEGUES)
    return c


def main() -> None:
    from src.tracking import Corrida

    t = cargar("permeabilidad", estratos="origen")
    y, g, origen = np.asarray(t.y), t.grupos, t.estratos
    # **float32, que es lo que `cargar` devuelve y lo que usó el 05c.** Pasarlo a float64 mueve
    # las cifras en el tercer decimal y el brazo de control dejaría de reproducir el registro.
    X_control = t.X
    assert X_control.dtype == np.float32
    n_control = X_control.shape[1]

    mols = [a_mol(s) for s in t.meta["SMILES"]]
    ilegibles = [s for s, m in zip(t.meta["SMILES"], mols) if m is None]
    if ilegibles:   # quitarlas en silencio desalinearía las columnas con las de descriptores
        raise ValueError(f"{len(ilegibles)} SMILES no se pueden leer (el primero: {ilegibles[0]!r})")
    estereo = conteos_estereo(mols)
    X_estereo = np.hstack([X_control, estereo.to_numpy(dtype=np.float32)])

    mascara = inseparables(X_control, y)
    print(f"{len(y):,} filas · {n_control} descriptores · +{estereo.shape[1]} columnas de estereoquímica")
    print(f"inseparables con los {n_control}: {mascara.sum()} · "
          f"con las cuatro columnas: {inseparables(X_estereo, y).sum()}\n", flush=True)

    modelos = {**seleccion(BASE), **ensambles(BASE)}
    assert set(modelos) == set(ORDEN)
    brazos = {CONTROL: X_control, TRATAMIENTO: X_estereo}

    params = {"modelos": ORDEN, "brazos": list(brazos), "semillas": list(SEMILLAS),
              "pliegues": PLIEGUES, "estratos": "origen", "filas": int(len(y)),
              "columnas_nuevas": list(CONTEOS_ESTEREO),
              "etiquetas_cip": "rdCIPLabeler (reglas completas), no el asignador heredado",
              "control_registrado": "2026-10-31-artemio-1.3-ensambles-permeabilidad-huellas",
              "huellas": "fuera a propósito: la 1.3 ya midió que en la fase 1 perjudican",
              "lectura_1": "techo del oráculo por representación (MCC y AUPRC, no solo exactitud)",
              "lectura_2": "acierto fuera de pliegue sobre las filas inseparables, pareado",
              "lectura_3": f"diferencia pareada de {list(PRINCIPALES)}, regla del 05c",
              "manda": "la lectura 2; el agregado puede quedar plano con el mecanismo vivo",
              "alcance": "conteos globales: un diastereómero que invierta dos centros no se separa",
              "toca_prueba": False}

    with Corrida("estereo-descriptores-fase1", decision="1.8", params=params,
                 semillas=list(SEMILLAS),
                 datos=[PROCESADOS / "bbb_meta.parquet",
                        PROCESADOS / DESCRIPTORES["descriptores"]]) as c:
        partes, fdp, aciertos = [], {}, []
        for brazo, M in brazos.items():
            t0 = time.perf_counter()
            r, pred = evaluar(modelos, M, y, g, estratos=origen, semillas=SEMILLAS,
                              pliegues=PLIEGUES, verboso=False)
            partes.append(r.assign(brazo=brazo))
            fdp[brazo] = pred
            aciertos.append(acierto_en(mascara, pred, y).assign(brazo=brazo))
            print(f"  {brazo:<22} {(time.perf_counter() - t0) / 60:5.1f} min", flush=True)
        res = pd.concat(partes, ignore_index=True)

        # Lectura 1
        techos = {b: techo(M, y, origen) for b, M in brazos.items()}

        # Lectura 2
        ac = pd.concat(aciertos, ignore_index=True)
        pareado = ac.pivot_table(index=["modelo", "semilla"], columns="brazo", values="acierto")
        dif = (pareado[TRATAMIENTO] - pareado[CONTROL])
        lectura2 = {"filas": int(mascara.sum()),
                    "acierto_control": round(float(pareado[CONTROL].mean()), 4),
                    "acierto_tratamiento": round(float(pareado[TRATAMIENTO].mean()), 4),
                    "dif_media": round(float(dif.mean()), 4),
                    "mejor_en": int((dif > 0).sum()), "de": int(len(dif)),
                    "por_modelo": {m: round(float(v.mean()), 4) for m, v in dif.groupby("modelo")}}

        # Lectura 3
        ctrl = res[(res["brazo"] == CONTROL) & (res["estrato"] == "todos")]
        umbrales = {m: round(float(ctrl.groupby("modelo")[m].std().max()), 3) for m in PRINCIPALES}
        estratos = ["todos"] + [e for e in pd.unique(res.loc[res["estrato"].ne("todos"), "estrato"])]
        lectura3 = {e: comparacion(res, umbrales, e).set_index(["modelo", "metrica"]).to_dict("index")
                    for e in estratos}
        mcc = {e: res[res["estrato"] == e].groupby(["brazo", "modelo"])["mcc"].mean().round(4)
               .unstack("brazo").to_dict("index") for e in estratos}

        c.metricas({"techo_oraculo": techos, "umbrales": umbrales,
                    "acierto_en_inseparables": lectura2,
                    "diferencia_pareada": lectura3, "mcc_medio": mcc})

        print("\nLectura 1 · techo de cada representación (filas de ajuste)")
        for b in brazos:
            d = techos[b]["todos"]
            print(f"  {b:<22} MCC {d['mcc']:.4f} · AUPRC {d['auprc_minoritaria']:.4f} · "
                  f"exactitud bal. {d['exactitud_balanceada']:.4f} · inseparables {d['inseparables']}")
        print("\nLectura 2 · acierto fuera de pliegue sobre las "
              f"{lectura2['filas']} filas inseparables")
        print(f"  control {lectura2['acierto_control']:.4f} → tratamiento "
              f"{lectura2['acierto_tratamiento']:.4f} "
              f"(dif {lectura2['dif_media']:+.4f}; mejor en {lectura2['mejor_en']}/{lectura2['de']})")
        print(f"\nLectura 3 · umbrales {umbrales}")
        for e in estratos:
            cmp = comparacion(res, umbrales, e)
            sub = cmp[cmp["metrica"].isin(PRINCIPALES)]
            print(f"  {e}: dif_media MCC {sub[sub.metrica=='mcc']['dif_media'].mean():+.4f} · "
                  f"cumplen la regla {int(sub.groupby('modelo')['cumple'].all().sum())}/{len(ORDEN)}")
        print(f"\n  carpeta: experimentos/{c.id}")


if __name__ == "__main__":
    main()
