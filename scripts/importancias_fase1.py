#!/usr/bin/env python3
"""Las caracteristicas de la fase 1, con nombre: los dos metodos de atribucion de la C.2.

El cuaderno 05 ya calcula los dos metodos y marca su interseccion, pero **rotula por
indice de columna y no nombra ni una caracteristica**: la celda pide los nombres con
`t.meta.attrs.get("columnas", range(X.shape[1]))` y ese canal no existe —`Tarea` no tiene
ese campo y `src/models/tareas.py` nunca escribe `meta.attrs`, aunque tiene la lista en su
linea 214—, asi que el `.get` cae en su valor por omision sin que nada falle. El resultado
es una figura sin un solo nombre, que es justo lo que denuncia el #146.

Esto recomputa los dos metodos **con los nombres**, leyendo las columnas del parquet en
orden, sin reejecutar el cuaderno y sin tocar la particion reservada. Imprime la tabla que
la figura no tiene y hace el contraste contra TPSA y los donadores de hidrogeno que la
[C.2](../docs/decisiones.md#dc-2) exige antes de cualquier afirmacion estructural.

**Los dos metodos miden dos modelos distintos, y hay que decirlo:** la permutacion sobre el
modelo final y la impureza sobre el bosque, porque el SVM no tiene importancia interna. La
interseccion es entre una lectura del SVM y una lectura de un bosque, no dos lecturas del
mismo modelo. Es el punto flojo de la C.2 en esta fase, y va declarado.

    ./env/bin/python scripts/importancias_fase1.py
"""
from __future__ import annotations

import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
from pathlib import Path

import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance
from sklearn.model_selection import StratifiedGroupKFold

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.models import cargar, seleccion                                  # noqa: E402
from src.models.ensambles_clasificacion import ensambles                  # noqa: E402
from src.tracking import Corrida                                          # noqa: E402

FINAL = "svm_rbf"
BASE = ("svm_rbf", "logistica", "mlp", "knn")
PARQUET = RAIZ / "data" / "processed" / "bbb_descriptores_filtrados_sin_normalizar.parquet"
PLIEGUES = 5
REPETICIONES = 5
PRIMERAS = 15
UMBRAL_RACIMO = 0.76      # por encima de esto, permutar una columna no destruye su informacion

PARAMS = {
    "modelo_final": FINAL, "segundo_metodo": "impureza del bosque",
    "puntuacion_permutacion": "matthews_corrcoef", "repeticiones": REPETICIONES,
    "pliegues": PLIEGUES, "primeras": PRIMERAS, "umbral_racimo": UMBRAL_RACIMO,
    "nota": "la permutacion mide el modelo final y la impureza el bosque, porque el SVM no "
            "tiene importancia interna: la interseccion es entre dos modelos distintos",
}


def importancias(X, y, g, nombres: list[str]) -> pd.DataFrame:
    """Una fila por caracteristica, con la media de los dos metodos entre pliegues."""
    modelos = {**seleccion(BASE), **ensambles(BASE)}
    filas = []
    cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=0)
    for k, (ajuste, val) in enumerate(cv.split(X, y, g), 1):
        final = clone(modelos[FINAL]).fit(X[ajuste], y[ajuste])
        perm = permutation_importance(final, X[val], y[val], n_repeats=REPETICIONES,
                                      random_state=k, scoring="matthews_corrcoef")
        bosque = clone(modelos["bosque"]).fit(X[ajuste], y[ajuste])
        imp = bosque.named_steps["modelo"].feature_importances_
        for j, nombre in enumerate(nombres):
            filas.append({"caracteristica": nombre, "indice": j, "pliegue": k,
                          "permutacion": perm.importances_mean[j], "impureza": imp[j]})
        print(f"  pliegue {k} de {PLIEGUES}", flush=True)
    d = pd.DataFrame(filas).groupby(["caracteristica", "indice"], as_index=False)[
        ["permutacion", "impureza"]].mean()
    d["r_perm"] = d["permutacion"].rank(ascending=False)
    d["r_imp"] = d["impureza"].rank(ascending=False)
    return d


def main() -> None:
    t = cargar("permeabilidad", estratos="origen")
    X, y, g = t.X, t.y, t.grupos
    nombres = list(pd.read_parquet(PARQUET).columns)
    assert len(nombres) == X.shape[1], f"{len(nombres)} nombres contra {X.shape[1]} columnas"
    print(f"{len(y):,} compuestos, {X.shape[1]} descriptores, {len(nombres)} nombres", flush=True)

    with Corrida("atribucion-fase1-con-nombres", decision="C.2", params=PARAMS,
                 semillas=[0], datos=[PARQUET]) as c:
        d = importancias(X, y, g, nombres)
        d.to_csv(c.carpeta / "importancias.csv", index=False)
        inter = (set(d.nsmallest(PRIMERAS, "r_perm")["caracteristica"])
                 & set(d.nsmallest(PRIMERAS, "r_imp")["caracteristica"]))
        c.metricas({
            "interseccion": {f["caracteristica"]: {
                "indice": int(f["indice"]),
                "permutacion": round(float(f["permutacion"]), 5),
                "impureza": round(float(f["impureza"]), 5)}
                for _, f in d[d["caracteristica"].isin(inter)].iterrows()},
            "contraste_c2": {n: {
                "puesto_permutacion": int(d.loc[d["caracteristica"] == n, "r_perm"].iloc[0]),
                "puesto_impureza": int(d.loc[d["caracteristica"] == n, "r_imp"].iloc[0])}
                for n in ("TPSA", "NumHDonors")},
            "n_en_interseccion": len(inter),
        })

    print(f"\ncorrida: experimentos/{c.id}")
    for metodo, col in (("permutacion (el modelo final)", "r_perm"),
                        ("impureza (el bosque)", "r_imp")):
        print(f"\n=== las {PRIMERAS} primeras por {metodo} ===")
        print(d.nsmallest(PRIMERAS, col)[["indice", "caracteristica", "permutacion", "impureza"]]
              .to_string(index=False, float_format=lambda v: f"{v:.5f}"))
    print(f"\n=== la interseccion, que es lo unico reportable ({len(inter)} de {PRIMERAS}) ===")
    print(d[d["caracteristica"].isin(inter)].sort_values("r_perm")[
        ["indice", "caracteristica", "permutacion", "impureza"]]
          .to_string(index=False, float_format=lambda v: f"{v:.5f}"))

    print("\n=== el contraste que pide la C.2 ===")
    for n in ("TPSA", "NumHDonors"):
        f = d[d["caracteristica"] == n].iloc[0]
        print(f"  {n:<12} indice {int(f['indice']):3d}  puesto {int(f['r_perm']):3d} por "
              f"permutacion y {int(f['r_imp']):3d} por impureza")
    corr = pd.read_parquet(PARQUET).corr(method="spearman")["TPSA"].drop("TPSA").abs()
    racimo = corr[corr >= UMBRAL_RACIMO]
    print(f"  TPSA esta en un racimo de {len(racimo)} columnas con |rho| >= {UMBRAL_RACIMO}: "
          + ", ".join(f"{n} {corr[n]:.3f}" for n in racimo.nlargest(len(racimo)).index))


if __name__ == "__main__":
    main()
