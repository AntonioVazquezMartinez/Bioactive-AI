#!/usr/bin/env python3
"""¿El baseline de la fase 1 rinde distinto según el origen y el grupo A–D? Y si sí, ¿por qué?

Complementa `scripts/experimento_baseline.py --estratos origen_grupo` (decisión 1.6 del
registro, #102). Aquel script reporta cifras por estrato; este contesta las preguntas que
esas cifras dejan abiertas, con una medición por pregunta. Reentrena la evaluación igual
que el baseline (`cargar("permeabilidad", estratos="origen_grupo")`, las mismas
`canalizaciones()`, semillas 0, 1, 2 y 5 pliegues) para obtener las predicciones fuera de
pliegue, y no toca la prueba reservada.

Qué se mide y por qué así
-------------------------
1. **Diferencias pareadas con intervalo bootstrap de grupos de la CV.** Dos estratos con
   AUROC distinto en el baseline no son necesariamente distintos: cada cifra trae su propio
   intervalo, y comparar dos intervalos que se solapan no equivale a probar la diferencia.
   Se calcula la diferencia directamente (AUROC y MCC de un estrato menos los del otro) y
   se remuestrean **grupos de la CV, no filas**, porque la fila no es la unidad
   independiente (`cv.intervalo_por_grupos`). El remuestreo es *conjunto*: en cada réplica
   se eligen grupos de la unión de los dos estratos y se calcula la diferencia sobre lo
   elegido, de modo que un grupo que aporta filas a los dos estratos (hay 34 en el grupo A,
   95 en el B) mueve las dos medidas a la vez, como debe. Contrastes: natural exacto contra
   sin equivalente (global, en A, en B y en C) y A contra B dentro de cada origen. Se usa la
   probabilidad promediada entre semillas; el MCC se da de dos maneras, sobre esa
   probabilidad media y como promedio de los MCC por semilla, que es como lo reporta el
   baseline. También se da la diferencia de AUPRC de BBB− menos su línea base (la
   prevalencia de BBB−), porque el AUPRC cruda depende de la prevalencia del estrato y la
   resta la quita.
2. **Perfil por estrato.** n, BBB−, sensibilidad y especificidad con corte 0.5,
   probabilidad media de los BBB−, fracción de BBB− que el modelo manda a BBB+ (p ≥ 0.5)
   y AUPRC de BBB− junto a su línea base.
3. **MCC esperado por prevalencia.** El MCC no es comparable entre estratos de distinta
   prevalencia aunque el modelo discrimine igual: un modelo con la misma sensibilidad y
   especificidad que el global, aplicado a un estrato con 88% de BBB+, da un MCC menor.
   Se calcula ese MCC y se pone junto al observado: lo que queda por encima o por debajo
   ya no es prevalencia.
4. **Negativos frontera.** El grupo A tiene logBB; el B no (su columna es nula, y el
   script lo dice en vez de suponerlo). Si muchos BBB− de A están a menos de 0.3 de
   logBB = −1, el corte de la etiqueta, el modelo no puede acertarlos porque la etiqueta
   misma es casi arbitraria ahí. Se reporta esa fracción y la de errores contra aciertos
   cerca del corte.
5. **TPSA de los BBB−.** Mediana por estrato: TPSA domina empíricamente la permeabilidad
   (<67 Å²), así que unos BBB− con TPSA baja son difíciles por construcción.
6. **Control de fuga de prior.** Si los descriptores predicen «natural exacto» o «grupo A»
   en CV agrupada, el modelo *podría* aprender, de los descriptores, el prior de BBB+ del
   estrato en vez de la química de la permeabilidad. Se mide con un boosting por defecto
   y la misma CV agrupada.

Límites, escritos antes de ver la cifra
---------------------------------------
- **Potencia.** Los estratos de A tienen 34 y 42 BBB−. Un intervalo que incluye el cero en
  esos contrastes dice que no se detecta diferencia, **no** que no la haya. Y el AUPRC de
  BBB− y el MCC de esos estratos se apoyan en esas 34 y 42 filas.
- **El corte de 0.5 mezcla** discriminación, calibración y prevalencia: una sensibilidad
  baja en un estrato puede ser un modelo que no distingue o uno cuyas probabilidades están
  corridas hacia donde está la mayoría. El AUROC y el AUPRC sí son independientes del
  corte; por eso se reportan ambos tipos.
- **El MCC esperado por prevalencia** supone que la sensibilidad y la especificidad del
  estrato serían las globales. Es una referencia, no una explicación causal.
- **El control de fuga es una indicación, no una demostración.** Que los descriptores
  predigan el origen o el grupo no prueba que el modelo de permeabilidad use ese atajo; solo
  muestra que la información está disponible para él. Probarlo exigiría quitarla y medir
  qué cambia.
- **Los intervalos remuestrean grupos**, así que cubren la variación entre grupos pero no
  la de reentrenar (las tres semillas comparten filas). Son 2000 remuestras, semilla 0,
  las del auditor y las de `intervalo_por_grupos`.
- Muchos contrastes (4 + 2 por 3 modelos por 2 medidas): ninguno está corregido por
  comparaciones múltiples. Se lee el patrón entre modelos, no un intervalo suelto.

Salida: tablas en pantalla y `notebooks/datos/analisis_origen_fase1.csv` en formato largo
(`prueba, modelo, estrato_o_contraste, medida, valor, ic_inf, ic_sup, detalle`).

Uso: `python scripts/analisis_origen_fase1.py [--sin-registro]`
"""
import argparse
import platform
import sys
import time
from contextlib import ExitStack
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.ensemble import HistGradientBoostingClassifier  # noqa: E402
from sklearn.metrics import (average_precision_score, confusion_matrix,  # noqa: E402
                             matthews_corrcoef, roc_auc_score)
from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402

from src.evaluation.cv import evaluar  # noqa: E402
from src.models import canalizaciones, cargar  # noqa: E402
from src.models.tareas import ARCHIVO_PATROCINADORA, ORIGENES, PROCESADOS  # noqa: E402
from src.tracking import Corrida  # noqa: E402

SEMILLAS = (0, 1, 2)
PLIEGUES = 5
REMUESTRAS = 2000
SEMILLA_BOOT = 0
MIN_MINORITARIA = 5       # para mostrar un estrato en las tablas (el baseline pide 20 para intervalos)
CERCA = 0.3               # |logBB + 1| < CERCA es «frontera»
NA, AN, SE = ORIGENES
SALIDA = RAIZ / "notebooks/datos/analisis_origen_fase1.csv"

FILAS: list[dict] = []


def anota(prueba: str, modelo: str, estrato: str, medida: str, valor, lo=None, hi=None,
          detalle: str = "") -> None:
    FILAS.append(dict(prueba=prueba, modelo=modelo, estrato_o_contraste=estrato,
                      medida=medida, valor=valor, ic_inf=lo, ic_sup=hi, detalle=detalle))


def tabla(titulo: str, df: pd.DataFrame) -> None:
    print(f"\n{titulo}")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.3f}"), flush=True)


def mcc_de(sens: float, espec: float, prev: float) -> float:
    """MCC de un clasificador con esa sensibilidad y especificidad en un estrato con esa prevalencia."""
    tp, fn = sens * prev, (1 - sens) * prev
    tn, fp = espec * (1 - prev), (1 - espec) * (1 - prev)
    return float((tp * tn - fp * fn) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))


def medidas(y, p, pk):
    """AUROC, MCC (p media), MCC (media por semilla) y AUPRC(BBB−) − línea base; None si falta una clase."""
    if len(np.unique(y)) < 2:
        return None
    return np.array([
        roc_auc_score(y, p),
        matthews_corrcoef(y, (p >= 0.5).astype(int)),
        np.mean([matthews_corrcoef(y, (pk[k] >= 0.5).astype(int)) for k in range(pk.shape[0])]),
        average_precision_score(1 - y, 1 - p) - (1 - y).mean()])


def diferencia_pareada(a, b, arr, y, p, pk, g):
    """Medidas de `a` menos las de `b`, con bootstrap de grupos de la CV sobre la unión.

    Devuelve (estimación, inf, sup, n_grupos, remuestras_válidas); cada uno de los
    cuatro valores es un vector en el orden de `medidas`.
    """
    s = np.isin(arr, [a, b])
    yy, pp, gg, ee, kk = y[s], p[s], g[s], arr[s], pk[:, s]

    def estadistico(idx):
        r = []
        for e in (a, b):
            j = idx[ee[idx] == e]
            m = medidas(yy[j], pp[j], kk[:, j])
            if m is None:
                return None
            r.append(m)
        return r[0] - r[1]

    completo = estadistico(np.arange(len(yy)))
    unicos = np.unique(gg)
    indices = {u: np.flatnonzero(gg == u) for u in unicos}
    rng = np.random.default_rng(SEMILLA_BOOT)
    muestras = []
    for _ in range(REMUESTRAS):
        elegidos = rng.choice(unicos, len(unicos))
        r = estadistico(np.concatenate([indices[u] for u in elegidos]))
        if r is not None:
            muestras.append(r)
    lo, hi = np.percentile(np.array(muestras), [2.5, 97.5], axis=0)
    return completo, lo, hi, len(unicos), len(muestras)


NOMBRES_MEDIDA = ("dAUROC", "dMCC_p_media", "dMCC_media_semillas", "dAUPRC_menos_base")


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    cli.add_argument("--sin-registro", action="store_true",
                     help="no crea carpeta en experimentos/")
    args = cli.parse_args()
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    t0 = time.time()

    params = dict(tarea="permeabilidad", representacion="descriptores",
                  estratos="origen_grupo", pliegues=PLIEGUES,
                  canalizaciones=["logistica", "bosque", "boosting"],
                  bootstrap=dict(remuestras=REMUESTRAS, semilla=SEMILLA_BOOT,
                                 unidad="grupos de la CV"),
                  frontera_logbb=dict(corte=-1.0, cerca=CERCA),
                  min_minoritaria_tablas=MIN_MINORITARIA,
                  control_fuga="HistGradientBoostingClassifier(random_state=0), "
                               "StratifiedGroupKFold(5, shuffle, 0)")
    # El registro se abre ANTES de calcular y de escribir el CSV: `entorno.json` toma
    # `arbol_sucio` de `git status` al entrar, y el CSV nuevo lo ensuciaría.
    with ExitStack() as pila:
        corrida = None if args.sin_registro else pila.enter_context(
            Corrida("analisis-origen", decision="1.6", params=params,
                    semillas=list(SEMILLAS), datos=[ARCHIVO_PATROCINADORA]))
        resumen = _calcular()
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(FILAS).to_csv(SALIDA, index=False)
        print(f"\n[guardado] {SALIDA.relative_to(RAIZ)}  ({len(FILAS)} filas, "
              f"{time.time() - t0:.0f} s)")
        if corrida is not None:
            corrida.metricas(resumen)


def _calcular() -> dict:
    t = cargar("permeabilidad", representacion="descriptores", estratos="origen_grupo")
    print(f"{t}", flush=True)
    y, g, est, X, meta = t.y, t.grupos, t.estratos.astype(str), t.X, t.meta
    ori = meta["origen"].to_numpy().astype(str)
    gr = meta["group"].astype(str).to_numpy()
    modelos = list(canalizaciones())

    _, fdp = evaluar(canalizaciones(), X, y, g, estratos=est, semillas=SEMILLAS,
                     pliegues=PLIEGUES, verboso=False)
    P = {m: fdp[m] for m in modelos}              # (semillas, filas)
    pm = {m: P[m].mean(0) for m in modelos}       # probabilidad promediada entre semillas

    # --- 0. Estratos ------------------------------------------------------------------
    filas = []
    for etiqueta, arr in (("origen", ori), ("origen_grupo", est)):
        for e in sorted(set(arr)):
            s = arr == e
            filas.append(dict(nivel=etiqueta, estrato=e, n=int(s.sum()),
                              bbb_neg=int((1 - y[s]).sum()), prev_pos=y[s].mean(),
                              grupos_cv=len(np.unique(g[s]))))
            anota("estratos", "", e, "n", int(s.sum()), detalle=f"BBB− {int((1 - y[s]).sum())}")
    tabla("Estratos", pd.DataFrame(filas))

    resumen: dict = {}

    # --- 1. Diferencias pareadas ------------------------------------------------------
    contrastes = [("NA−SE global", NA, SE, ori)]
    contrastes += [(f"NA−SE {G}", f"{NA}·{G}", f"{SE}·{G}", est) for G in "ABC"]
    contrastes += [("NA A−B", f"{NA}·A", f"{NA}·B", est),
                   ("SE A−B", f"{SE}·A", f"{SE}·B", est)]
    print("\nDiferencias pareadas (bootstrap de grupos de la CV, "
          f"{REMUESTRAS} remuestras, semilla {SEMILLA_BOOT})")
    filas = []
    for nombre, a, b, arr in contrastes:
        compartidos = len(set(g[arr == a]) & set(g[arr == b]))
        for m in modelos:
            est_, lo, hi, ng, nv = diferencia_pareada(a, b, arr, y, pm[m], P[m], g)
            for i, medida in enumerate(NOMBRES_MEDIDA):
                anota("diferencia_pareada", m, nombre, medida, float(est_[i]),
                      float(lo[i]), float(hi[i]),
                      f"{a} − {b}; grupos {ng} ({compartidos} compartidos); "
                      f"remuestras válidas {nv}")
            resumen.setdefault(m, {})[nombre] = {
                "dAUROC": [round(float(est_[0]), 4), round(float(lo[0]), 4), round(float(hi[0]), 4)],
                "dMCC_p_media": [round(float(est_[1]), 4), round(float(lo[1]), 4),
                                 round(float(hi[1]), 4)],
                "dMCC_media_semillas": [round(float(est_[2]), 4), round(float(lo[2]), 4),
                                        round(float(hi[2]), 4)]}
            filas.append({"contraste": nombre, "modelo": m, "compartidos": compartidos,
                          **{f"{k} [IC95]": f"{est_[i]:+.3f} [{lo[i]:+.3f}, {hi[i]:+.3f}]"
                             for i, k in enumerate(NOMBRES_MEDIDA)}})
    tabla("Diferencias (primero − segundo); el IC que excluye el cero es la señal", pd.DataFrame(filas))

    # --- 2 y 3. Perfil por estrato y MCC esperado por prevalencia ---------------------
    estratos = [NA, AN, SE] + [f"{o}·{G}" for G in "ABC" for o in (NA, AN, SE)]
    for m in modelos:
        yh = (pm[m] >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y, yh).ravel()
        se_g, sp_g = tp / (tp + fn), tn / (tn + fp)
        anota("perfil", m, "global", "sensibilidad", float(se_g))
        anota("perfil", m, "global", "especificidad", float(sp_g))
        filas = []
        for e in estratos:
            arr = ori if e in ORIGENES else est
            s = arr == e
            if s.sum() == 0:
                continue
            ys, ps = y[s], pm[m][s]
            if min(ys.sum(), (1 - ys).sum()) < MIN_MINORITARIA:
                continue
            tn, fp, fn, tp = confusion_matrix(ys, (ps >= 0.5).astype(int), labels=[0, 1]).ravel()
            sens, espec, prev = tp / (tp + fn), tn / (tn + fp), ys.mean()
            neg = 1 - ys
            fila = dict(estrato=e, n=int(s.sum()), bbb_neg=int(neg.sum()), prev_pos=prev,
                        sens=sens, espec=espec, p_media_neg=ps[ys == 0].mean(),
                        frac_neg_p_ge_05=(ps[ys == 0] >= 0.5).mean(),
                        auprc_neg=average_precision_score(neg, 1 - ps), base_neg=neg.mean(),
                        mcc_obs=matthews_corrcoef(ys, (ps >= 0.5).astype(int)),
                        mcc_esp=mcc_de(se_g, sp_g, prev))
            filas.append(fila)
            det = f"n={fila['n']}, BBB−={fila['bbb_neg']}"
            for k, v in fila.items():
                if k not in ("estrato", "n", "bbb_neg"):
                    anota("perfil", m, e, k, float(v), detalle=det)
        tabla(f"Perfil por estrato · {m} (global: sens {se_g:.3f}, espec {sp_g:.3f}; "
              "corte 0.5, probabilidad media entre semillas)", pd.DataFrame(filas))

    # --- 4. Negativos frontera --------------------------------------------------------
    arch = pd.read_csv(ARCHIVO_PATROCINADORA)
    arch.columns = [c.strip().lstrip("﻿") for c in arch.columns]
    lb = arch.drop_duplicates("inchikey").set_index("inchikey")["logbb"]
    logbb = meta["Inchi"].map(lb).to_numpy(dtype=float)   # `Inchi` es un InChIKey (ver tareas.py)
    dist = np.abs(logbb + 1.0)
    print("\nNegativos frontera (logBB del archivo de la patrocinadora, cruzado por InChIKey)")
    for G in ("A", "B"):
        cob = float(np.mean(~np.isnan(logbb[gr == G])))
        anota("frontera", "", f"grupo {G}", "cobertura_logbb", cob,
              detalle="fracción de filas del grupo con logBB no nulo")
        print(f"  grupo {G}: logBB disponible en {cob:.1%} de las filas"
              + ("" if cob > 0 else "  -> sin logBB, no se puede medir la frontera"))
    if np.mean(~np.isnan(logbb[gr == "A"])) > 0:
        filas = []
        for e in (f"{NA}·A", f"{AN}·A", f"{SE}·A"):
            s = (est == e) & (y == 0) & ~np.isnan(dist)
            if s.sum() == 0:
                continue
            fr = float((dist[s] < CERCA).mean())
            anota("frontera", "", e, "frac_bbb_neg_cerca_corte", fr,
                  detalle=f"BBB− con logBB: {int(s.sum())}; |logBB+1|<{CERCA}")
            filas.append(dict(estrato=e, bbb_neg=int(s.sum()), frac_cerca=fr,
                              logbb_mediana=float(np.median(logbb[s]))))
        tabla(f"BBB− del grupo A con |logBB + 1| < {CERCA}", pd.DataFrame(filas))
        A = (gr == "A") & ~np.isnan(dist)
        filas = []
        for m in modelos:
            err = (pm[m] >= 0.5).astype(int) != y
            fe, fa = float((dist[A & err] < CERCA).mean()), float((dist[A & ~err] < CERCA).mean())
            anota("frontera", m, "grupo A", "frac_errores_cerca_corte", fe,
                  detalle=f"errores {int((A & err).sum())}")
            anota("frontera", m, "grupo A", "frac_aciertos_cerca_corte", fa,
                  detalle=f"aciertos {int((A & ~err).sum())}")
            filas.append(dict(modelo=m, errores=int((A & err).sum()), errores_cerca=fe,
                              aciertos=int((A & ~err).sum()), aciertos_cerca=fa))
        tabla("Grupo A: fracción cerca del corte entre errores y aciertos", pd.DataFrame(filas))

    # --- 5. TPSA de los BBB− ---------------------------------------------------------
    nombres = pd.read_parquet(PROCESADOS / "bbb_descriptores_filtrados_sin_normalizar.parquet"
                              ).columns.tolist()
    tpsa = X[:, nombres.index("TPSA")]
    filas = []
    for e in [NA, AN, SE] + [f"{o}·{G}" for G in "ABC" for o in (NA, SE)]:
        arr = ori if e in ORIGENES else est
        s = (arr == e) & (y == 0)
        if s.sum() == 0:
            continue
        med = float(np.median(tpsa[s]))
        anota("tpsa", "", e, "mediana_tpsa_bbb_neg", med, detalle=f"BBB− {int(s.sum())}")
        filas.append(dict(estrato=e, bbb_neg=int(s.sum()), tpsa_mediana=med))
    tabla("TPSA mediana de los BBB− (Å²)", pd.DataFrame(filas))

    # --- 6. Control de fuga de prior --------------------------------------------------
    print("\nControl: ¿predicen los descriptores el origen o el grupo? "
          "(indicación, no demostración)")
    for nombre, objetivo in (("natural exacto", (ori == NA).astype(int)),
                             ("grupo A", (gr == "A").astype(int))):
        po = np.zeros(len(objetivo))
        for tr, va in StratifiedGroupKFold(5, shuffle=True, random_state=0).split(X, objetivo, g):
            po[va] = HistGradientBoostingClassifier(random_state=0).fit(
                X[tr], objetivo[tr]).predict_proba(X[va])[:, 1]
        a = float(roc_auc_score(objetivo, po))
        anota("fuga_prior", "boosting", nombre, "auroc_descriptores_a_estrato", a,
              detalle=f"prevalencia {objetivo.mean():.3f}")
        resumen.setdefault("fuga_prior", {})[nombre] = round(a, 4)
        print(f"  AUROC descriptores → {nombre}: {a:.3f}  (prevalencia {objetivo.mean():.3f})")
    for nombre, arr in (("origen", ori), ("origen·grupo", est)):
        tasa = pd.Series(y).groupby(arr).transform("mean").to_numpy()
        a = float(roc_auc_score(y, tasa))
        anota("fuga_prior", "", nombre, "auroc_solo_tasa_del_estrato", a,
              detalle="referencia: predecir BBB+ con la tasa del estrato; "
                      "el origen·grupo no se conoce al inferir")
        print(f"  AUROC de BBB+ usando solo la tasa por {nombre}: {a:.3f}")
    return resumen


if __name__ == "__main__":
    main()
