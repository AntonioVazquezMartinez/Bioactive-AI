#!/usr/bin/env python3
"""El modelo de referencia del Avance 3, para cualquier tarea y cualquier objetivo.

Entrega de la [1.5](../docs/decisiones.md#d1-5): las tres canalizaciones
candidatas, evaluadas con validación cruzada agrupada por estructura y
desglosadas por estrato.

**Está escrito como canalización a propósito.** Lo que todavía puede cambiar en
este proyecto es qué se predice y con qué entradas —el corte de «activo» entre
10 µM y 1 µM, la representación entre descriptores, Morgan y Sort & Slice, y la
[2.9](../docs/decisiones.md#d2-9), que propone regresión en vez de
clasificación—. Ninguna de esas decisiones vive dentro de este script: son
argumentos.

    python scripts/experimento_baseline.py                       # permeabilidad
    python scripts/experimento_baseline.py --tarea actividad
    python scripts/experimento_baseline.py --tarea actividad --umbral 1
    python scripts/experimento_baseline.py --representacion sortslice
    python scripts/experimento_baseline.py --estratos origen_grupo   # 1.6 y #102

Y el escalado tampoco se aplica antes de partir: va dentro de la canalización,
que se reajusta en cada pliegue. Ajustarlo sobre todo el entrenamiento y
después partir filtraría la media y la varianza del pliegue de evaluación.

**La prueba no se toca.** Todo ocurre dentro de entrenamiento y validación; la
prueba reservada espera al Avance 5 y su guarda es el
[#54](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/54).

Salida: un CSV por tarea en `notebooks/datos/`, versionado para que el notebook
lo lea sin volver a correr nada, y una corrida en `experimentos/`.
"""

import argparse
import platform
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.metrics import matthews_corrcoef  # noqa: E402

from src.evaluation.cv import evaluar, intervalo_por_grupos, resumen  # noqa: E402
from src.models import canalizaciones, cargar  # noqa: E402
from src.models.tareas import ARCHIVO_PATROCINADORA  # noqa: E402
from src.tracking import Corrida  # noqa: E402

SEMILLAS = (0, 1, 2)
PLIEGUES = 5


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--tarea", default="permeabilidad",
                     choices=["permeabilidad", "actividad"])
    cli.add_argument("--representacion", default="descriptores")
    cli.add_argument("--umbral", type=float, default=10.0,
                     help="umbral de «activo» en µM; solo para --tarea actividad")
    cli.add_argument("--estratos", default="grupo",
                     choices=["grupo", "origen", "origen_grupo"],
                     help="desglose de permeabilidad; con uno distinto de «grupo» el CSV "
                          "y la corrida llevan sufijo para no sobrescribir el existente")
    cli.add_argument("--semillas", type=int, nargs="+", default=list(SEMILLAS))
    cli.add_argument("--pliegues", type=int, default=PLIEGUES)
    args = cli.parse_args()

    decision = "1.5" if args.tarea == "permeabilidad" else "2.3"
    if args.estratos != "grupo":
        decision = "1.6"   # el desglose por origen es la evidencia que pide la 1.6
    etiqueta = f"{args.tarea}-{args.representacion}".replace("+", "-")
    if args.tarea == "actividad":
        etiqueta += f"-{args.umbral:g}um"
    if args.estratos != "grupo":
        etiqueta += f"-{args.estratos}"
    salida = RAIZ / f"notebooks/datos/baseline_{etiqueta}.csv"

    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    with Corrida(f"baseline-{etiqueta}", decision=decision,
                 params={"tarea": args.tarea, "representacion": args.representacion,
                         "umbral_um": args.umbral if args.tarea == "actividad" else None,
                         "estratos": args.estratos,
                         "pliegues": args.pliegues,
                         "canalizaciones": ["logistica", "bosque", "boosting"]},
                 semillas=list(args.semillas),
                 # con el desglose por origen, el archivo de la patrocinadora es una
                 # entrada más del experimento y su huella tiene que quedar registrada
                 datos=[] if args.estratos == "grupo" else [ARCHIVO_PATROCINADORA]) as corrida:
        _correr(args, salida, corrida)


def _correr(args, salida: Path, corrida: Corrida) -> None:
    t = cargar(args.tarea, representacion=args.representacion, umbral_um=args.umbral,
               estratos=args.estratos)
    print(f"{t}\n  objetivo: {t.objetivo}", flush=True)
    # La tasa base de cada estrato, para leer sus cifras contra ella y no contra
    # la global (el grupo A tiene 88% de BBB+).
    print("\nEstratos (n y tasa de positivos)")
    for e in sorted(pd.unique(t.estratos)):
        sel = t.estratos == e
        print(f"  {e:<32} n={sel.sum():>6,}  positivos {t.y[sel].mean():>5.1%}")

    resultados, fuera_de_pliegue = evaluar(
        canalizaciones(), t.X, t.y, t.grupos, estratos=t.estratos,
        semillas=args.semillas, pliegues=args.pliegues)
    resultados.insert(0, "tarea", t.nombre)
    resultados.insert(1, "objetivo", t.objetivo)
    resultados.insert(2, "representacion", t.representacion)
    salida.parent.mkdir(parents=True, exist_ok=True)
    resultados.to_csv(salida, index=False)
    print(f"\n[guardado] {salida.relative_to(RAIZ)}")

    print("\nPromedio de las evaluaciones, por estrato")
    print(resumen(resultados).to_string())

    # Las predicciones se promedian entre semillas y el intervalo sale de
    # remuestrear grupos: las semillas comparten filas, así que su desviación
    # no es un error estándar (ver `cv.resumen`).
    print("\nAUROC con intervalo del 95% por bootstrap de grupos")
    intervalos = {}
    for nombre, p in fuera_de_pliegue.items():
        media = np.nanmean(p, axis=0)
        a, lo, hi = intervalo_por_grupos(t.y, media, t.grupos)
        intervalos[nombre] = {"auroc": round(a, 4), "ic95": [round(lo, 4), round(hi, 4)]}
        print(f"  {nombre:<10} {a:.4f}  [{lo:.4f}, {hi:.4f}]")
        for e in pd.unique(t.estratos):
            sel = t.estratos == e
            ys = t.y[sel]
            if min(int(ys.sum()), int((1 - ys).sum())) < 20:
                continue
            ae, loe, hie = intervalo_por_grupos(ys, media[sel], t.grupos[sel])
            intervalos[f"{nombre}·{e}"] = {"auroc": round(ae, 4),
                                           "ic95": [round(loe, 4), round(hie, 4)]}
            # El MCC del estrato, igual que su AUROC: sobre las predicciones fuera
            # de pliegue del estrato completo, uno por semilla y su promedio, con el
            # corte de 0.5 que usa `cv.evaluar`. Promediar las filas de `resultados`
            # no sirve aquí: `evaluar` solo las crea en los pliegues donde la
            # minoritaria del estrato llega a 20 *dentro del pliegue*, y un estrato
            # pequeño (natural exacto·A, que es el que nombra la 1.6) se quedaba
            # sin ningún pliegue y sin MCC aunque pasara el corte en conjunto.
            mcc_e = float(np.mean([matthews_corrcoef(ys, (p[s, sel] >= 0.5).astype(int))
                                   for s in range(p.shape[0])]))
            intervalos[f"{nombre}·{e}"]["mcc"] = round(mcc_e, 4)
            print(f"    {e:<32} n={sel.sum():>6,}  positivos {ys.mean():>5.1%}"
                  f"  {ae:.4f}  [{loe:.4f}, {hie:.4f}]  MCC {mcc_e:.4f}")

    global_ = resultados[resultados.estrato.eq("todos")].groupby("modelo")["mcc"].mean()
    mejor = global_.idxmax()
    print(f"\nMCC más alto: {mejor} ({global_[mejor]:.4f}).")
    print("Una sola corrida no establece un ganador: ver los intervalos de arriba")

    corrida.metricas({
        "n_filas": int(len(t.y)), "n_columnas": int(t.X.shape[1]),
        "n_grupos": int(len(np.unique(t.grupos))),
        "positivos": round(float(t.y.mean()), 4),
        "mcc": {m: round(float(v), 4) for m, v in global_.items()},
        "auroc": intervalos,
        "mejor_por_mcc": mejor,
    })


if __name__ == "__main__":
    main()
