#!/usr/bin/env python3
"""El AFT final contra la base de prueba externa que la patrocinadora y su colega separaron.

El archivo `snc_activity_crudo_v3_final_2026-09-25_Testeo.csv` (22,866 mediciones) no comparte
ni un identificador ni un SMILES canónico con el de entrenamiento. Es la primera vez que el
modelo se mide con datos que ninguna decisión del equipo ha visto.

**Regla declarada antes de correr.**

1. *Control (aborta si falla):* el constructor de pares aplicado al archivo de entrenamiento
   da exactamente los mismos pares (esqueleto, gen) que `fase2_pares.parquet`.
2. Se construyen los pares del archivo externo con `tabla_de_pares` (los mismos filtros), y se
   conservan solo los de las 26 dianas del modelo.
3. Se predice con el `aft` guardado en `models/finales/` sin reentrenar ni ajustar nada; la
   predicción de cada par es la columna `pActividad_<gen del par>`.
4. Métrica principal: concordancia de Harrell sobre todos los pares, con intervalo del 95%
   por remuestreo de **esqueletos** (200 réplicas, percentiles). Secundarias: Spearman sobre
   las exactas y fracción censurada. Se reportan por procedencia (`estrato`) y por
   «con/sin hermano»: el esqueleto aparece o no entre los de ajuste (entrenamiento y validación).
5. **Nada se decide con esto ni se compara contra un umbral inventado.** Es descriptivo: se
   reporta si 0.720 (concordancia global en la prueba reservada) cae dentro del intervalo.
   Lectura única: no se vuelve a correr con otra variante tras ver el resultado; si hay que
   cambiar algo, se declara como una corrida nueva.

No copia mediciones al repositorio: el archivo se lee de donde esté y la corrida guarda solo
agregados y la huella sha256 del archivo.

    python scripts/experimento_muestra_de_jorge.py [ruta_testeo]
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src import inferencia  # noqa: E402
from src.data_prep.pares_fase2 import tabla_de_pares  # noqa: E402
from src.evaluation.regresion import concordancia_harrell, metricas_regresion  # noqa: E402
from src.tracking import Corrida, sha256  # noqa: E402

ENTRENAMIENTO = RAIZ / "data" / "external" / "profesora" / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv"
TESTEO = Path.home() / "Downloads" / "snc_activity_crudo_v3_final_2026-09-25_Testeo.csv"
PARES = RAIZ / "data" / "processed" / "fase2_pares.parquet"
REPLICAS = 200


def intervalo(inf, sup, pred, esqueletos, rng) -> list[float]:
    """IC95% de la concordancia remuestreando esqueletos completos."""
    grupos = pd.Series(np.arange(len(esqueletos))).groupby(np.asarray(esqueletos)).apply(list)
    indices = list(grupos)
    valores = []
    for _ in range(REPLICAS):
        elegidos = rng.integers(0, len(indices), len(indices))
        idx = np.concatenate([indices[i] for i in elegidos])
        valores.append(concordancia_harrell(inf[idx], sup[idx], pred[idx]))
    return [float(np.nanpercentile(valores, 2.5)), float(np.nanpercentile(valores, 97.5))]


def resumen(d: pd.DataFrame, rng, con_intervalo: bool) -> dict:
    inf, sup, pred = (d[c].to_numpy(float) for c in ("limite_inferior", "limite_superior", "prediccion"))
    m = metricas_regresion(inf, sup, pred)
    m["pares"] = int(len(d))
    m["esqueletos"] = int(d["esqueleto"].nunique())
    if con_intervalo:
        m["concordancia_ic95"] = intervalo(inf, sup, pred, d["esqueleto"].to_numpy(), rng)
    return m


def main() -> None:
    testeo = Path(sys.argv[1]) if len(sys.argv) > 1 else TESTEO
    # 1. control
    fit = pd.read_parquet(PARES, columns=["esqueleto", "target_gene", "particion"])
    ent = tabla_de_pares(pd.read_csv(ENTRENAMIENTO, low_memory=False))
    clave = lambda t: set(zip(t["esqueleto"], t["target_gene"]))  # noqa: E731
    if clave(ent) != clave(fit):
        raise SystemExit(f"CONTROL NO PASADO: {len(clave(ent))} pares reconstruidos contra {len(clave(fit))}")
    print(f"control pasado: {len(clave(ent)):,} pares idénticos a fase2_pares.parquet")

    # 2. pares externos
    modelos = inferencia.cargar()
    pares = tabla_de_pares(pd.read_csv(testeo, low_memory=False))
    n_todos = len(pares)
    pares = pares[pares["target_gene"].isin(modelos.dianas)].reset_index(drop=True)
    # 3. predicción
    pred = inferencia.predecir(pares["smiles"].unique().tolist(), modelos).set_index("smiles")
    columna = {g: f"pActividad_{g}" for g in modelos.dianas}
    pares["prediccion"] = [pred.at[s, columna[g]] for s, g in zip(pares["smiles"], pares["target_gene"])]
    pares = pares[pares["prediccion"].notna()].reset_index(drop=True)
    vistos = set(fit.loc[fit["particion"].isin(["entrenamiento", "validacion"]), "esqueleto"])
    pares["hermano"] = np.where(pares["esqueleto"].isin(vistos), "con_hermano", "sin_hermano")

    # 4. cifras
    rng = np.random.default_rng(0)
    res = {"pares_externos_todas_las_dianas": int(n_todos), "pares_con_dianas_del_modelo": int(len(pares)),
           "global": resumen(pares, rng, True)}
    for col in ("estrato", "hermano"):
        res[f"por_{col}"] = {str(k): resumen(g, rng, len(g) >= 500) for k, g in pares.groupby(col)}
    res["prueba_reservada_global"] = 0.720
    ic = res["global"]["concordancia_ic95"]
    res["0.720_dentro_del_ic"] = bool(ic[0] <= 0.720 <= ic[1])
    with Corrida("muestra-de-jorge", decision="2.13", params={"replicas": REPLICAS, "semilla": 0, "testeo_sha256": sha256(testeo)},
                 semillas=[0], datos=[PARES]) as c:
        c.metricas(res)
    print(pd.json_normalize(res).T.to_string())


if __name__ == "__main__":
    main()
