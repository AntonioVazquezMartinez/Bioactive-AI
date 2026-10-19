#!/usr/bin/env python3
"""¿Por qué las tres características derivadas no mejoran el modelo?

Complementa `scripts/experimento_derivadas.py` (decisión 1.3 del registro). Aquel script
midió, con validación cruzada agrupada, que `regla_2p`, `tpsa_por_mw` y `lipo_neta` no
cambian el MCC (diferencias entre −0.005 y +0.002, con intervalos que incluyen el cero).
Este contesta **por qué**, con una medición por hipótesis y solo con las filas de
entrenamiento (la validación y la prueba no se tocan):

1. Redundancia: la información de cada derivada ya está en los descriptores base. Se
   reconstruye cada derivada a partir de los descriptores que sobreviven a la selección
   sin derivadas (`FiltroCasiConstante(10)` y `FiltroCorrelacion(0.95)`, ajustados con
   el entrenamiento) y se mide el R² de validación cruzada agrupada (`GroupKFold(5)`) con
   regresión lineal y Random Forest; `regla_2p`, que es binaria, además con el AUROC de un
   clasificador. También se reporta qué componentes (TPSA, MolWt, MolLogP, NumHDonors)
   sobreviven y, si no, con qué columna quedaron correlacionados (Spearman > 0.95).
2. `lipo_neta` es una combinación lineal de dos columnas: `MolLogP − 0.01·TPSA`. Un
   modelo lineal que ya tiene ambas puede representarla con sus coeficientes.
3. `regla_2p` son dos cortes: un árbol de profundidad 2 sobre TPSA y NumHDonors la
   reproduce, así que un bosque de árboles también puede formarla.
4. Una variable buena por sí sola no aporta si su información ya está: AUROC individual
   de cada derivada y de sus componentes, e importancia por permutación en un Random
   Forest con y sin las derivadas (5 pliegues agrupados, AUPRC de la clase minoritaria),
   para ver si la importancia se redistribuye de los componentes a las derivadas
   (sustitución) en lugar de aparecer como información nueva.

Por qué así: reconstruir la derivada con los demás descriptores responde directamente a
«¿hay algo que el modelo no tenga ya?», y es independiente del modelo de clasificación
y de su ruido. Los criterios de veredicto están escritos en cada hipótesis, antes de ver
la cifra, **salvo el de la 4, que se corrigió después de la primera corrida**: exigía
además que las tres derivadas tuvieran AUROC individual ≥ 0.80, un umbral que no contesta
la hipótesis (que algo buena sola no aporta si su información ya está) y que hacía fallar
el veredicto por `regla_2p`, que es binaria. Se deja escrito para que se vea. La 4 es
además la evidencia más débil: importancias de milésimas, repartidas entre columnas
casi iguales por la correlación.

Salida: tablas por hipótesis en pantalla y `notebooks/datos/analisis_derivadas.csv` en
formato largo (`hipotesis, derivada, medida, valor, detalle`).

Uso: `python scripts/analisis_derivadas.py [--sin-registro]`
"""
import argparse
import platform
import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import (GroupKFold, StratifiedGroupKFold, cross_val_predict,
                                     cross_val_score)
from sklearn.tree import DecisionTreeClassifier

from data_prep.splits import (andamio_murcko, esqueleto_conectividad, grupos_cv,
                              scaffold_split)
from features.molecular import a_mol, descriptores_rdkit, limpiar_descriptores
from features.seleccion import FiltroCasiConstante, FiltroCorrelacion
from tracking import Corrida

DERIVADAS = ("regla_2p", "tpsa_por_mw", "lipo_neta")
COMPONENTES = {"regla_2p": ("TPSA", "NumHDonors"), "tpsa_por_mw": ("TPSA", "MolWt"),
               "lipo_neta": ("MolLogP", "TPSA")}
TODOS_COMP = ("TPSA", "MolLogP", "NumHDonors", "MolWt")
U = 67.0
RHO = 0.95
PLIEGUES = 5

FILAS: list[dict] = []


def anota(hip: str, der: str, medida: str, valor, detalle: str = "") -> None:
    FILAS.append(dict(hipotesis=hip, derivada=der, medida=medida, valor=valor, detalle=detalle))


def tabla(titulo: str, df: pd.DataFrame) -> None:
    print(f"\n{titulo}")
    print(df.to_string(index=False, float_format=lambda v: f"{v:.4f}"), flush=True)


def derivadas_de(limpio: pd.DataFrame) -> pd.DataFrame:
    """Las tres derivadas con los descriptores crudos (U = 67 Å²), como en el experimento."""
    return pd.DataFrame({
        "regla_2p": ((limpio["TPSA"] < U) & (limpio["NumHDonors"] <= 1)).astype(float),
        "tpsa_por_mw": limpio["TPSA"] / limpio["MolWt"],
        "lipo_neta": limpio["MolLogP"] - limpio["TPSA"] / 100})


def seleccion(X: pd.DataFrame, y: np.ndarray) -> list[str]:
    """Columnas que sobreviven a los dos filtros, ajustados con las filas dadas."""
    v = X.values.astype(float)
    casi = FiltroCasiConstante(min_distintas=10).fit(v)
    nombres = np.array(X.columns)[casi.get_support()]
    corr = FiltroCorrelacion(umbral=RHO).fit(casi.transform(v), y)
    return list(nombres[corr.get_support()])


def correlacionadas(X: pd.DataFrame, col: str, candidatas: list[str]) -> list[tuple[str, float]]:
    """Columnas de `candidatas` con |Spearman| > RHO respecto a `col`, de mayor a menor."""
    r = X[candidatas + [col]].rank().corr()[col].drop(col, errors="ignore")
    r = r[r.abs() > RHO].sort_values(key=lambda s: -s.abs())
    return list(r.items())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-registro", action="store_true", help="no crea carpeta en experimentos/")
    args = ap.parse_args()
    print(f"python {platform.python_version()} · {platform.platform()}", flush=True)
    t0 = time.time()

    # --- datos y partición: idénticos a experimento_derivadas.py ---
    datos = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
    b = pd.read_csv(datos)
    b.columns = [c.strip().lstrip("﻿") for c in b.columns]
    b = b.rename(columns={"smiles_std": "SMILES", "bbb_class": "BBB+/BBB-"})
    b["mol"] = b["SMILES"].map(a_mol)
    d = b.dropna(subset=["mol", "BBB+/BBB-"]).reset_index(drop=True)
    d["y"] = (d["BBB+/BBB-"] == "BBB+").astype(int)
    d["andamio"] = [andamio_murcko(m) for m in d["mol"]]
    d["esqueleto"] = [esqueleto_conectividad(m) for m in d["mol"]]
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1,
                                    semilla=42, acíclicos_a="entrenamiento")
    desc = descriptores_rdkit(list(d["mol"]))
    limpio, _ = limpiar_descriptores(desc, verbose=False)
    limpio = limpio.reset_index(drop=True)

    tr = np.where((d["particion"] == "entrenamiento").values)[0]
    X = limpio.iloc[tr].reset_index(drop=True)
    y = d["y"].values[tr]
    g = grupos_cv(d)[tr]
    der = derivadas_de(limpio).iloc[tr].reset_index(drop=True)
    print(f"entrenamiento: {len(tr)} filas, {X.shape[1]} descriptores, "
          f"{y.mean():.3f} BBB+", flush=True)

    base = seleccion(X, y)
    print(f"sobreviven a la selección sin derivadas: {len(base)} de {X.shape[1]}", flush=True)
    anota("0", "-", "descriptores_base_sobrevivientes", len(base), f"de {X.shape[1]}")

    # supervivencia de componentes y, si no sobreviven, su sustituta correlacionada
    sustituta: dict[str, list[str]] = {}
    filas = []
    for c in TODOS_COMP:
        vive = c in base
        if vive:
            sustituta[c] = [c]
            filas.append(dict(componente=c, sobrevive="sí", correlacionada_con="-"))
        else:
            cor = correlacionadas(X, c, base)
            sustituta[c] = [n for n, _ in cor]
            txt = ", ".join(f"{n} (ρ={r:.3f})" for n, r in cor[:4]) or "ninguna con |ρ|>0.95"
            filas.append(dict(componente=c, sobrevive="no", correlacionada_con=txt))
        anota("0", "-", f"sobrevive_{c}", int(vive), filas[-1]["correlacionada_con"])
    tabla("Componentes en la selección base (solo entrenamiento)", pd.DataFrame(filas))

    # --- Hipótesis 1: redundancia por reconstrucción ---
    Xb = X[base].values.astype(float)
    gkf = GroupKFold(n_splits=PLIEGUES)
    filas = []
    for dv in DERIVADAS:
        t = der[dv].values
        r2l = cross_val_score(LinearRegression(), Xb, t, groups=g, cv=gkf, scoring="r2").mean()
        r2f = cross_val_score(RandomForestRegressor(n_estimators=200, n_jobs=-1, random_state=0),
                              Xb, t, groups=g, cv=gkf, scoring="r2").mean()
        fila = dict(derivada=dv, R2_LinearRegression=r2l, R2_RandomForest=r2f, AUROC_RF=np.nan)
        anota("1", dv, "R2_cv_LinearRegression", r2l, "descriptores base sobrevivientes")
        anota("1", dv, "R2_cv_RandomForest", r2f, "descriptores base sobrevivientes")
        if dv == "regla_2p":
            p = cross_val_predict(RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0),
                                  Xb, t.astype(int), groups=g, cv=gkf, method="predict_proba")[:, 1]
            fila["AUROC_RF"] = roc_auc_score(t, p)
            anota("1", dv, "AUROC_cv_RandomForest", fila["AUROC_RF"], "clasificador de la regla")
        filas.append(fila)
    h1 = pd.DataFrame(filas)
    tabla("H1. Reconstrucción de cada derivada con los descriptores base (R² de CV agrupada)", h1)
    mejor = h1[["R2_LinearRegression", "R2_RandomForest"]].max(axis=1)
    ok1 = bool((mejor >= 0.90).all())
    cifra1 = ", ".join(f"{dv} {m:.3f}" for dv, m in zip(h1.derivada, mejor))
    print(f"H1 (criterio: mejor R² >= 0.90 en las tres): {'SE SOSTIENE' if ok1 else 'NO SE SOSTIENE'}"
          f" — mejor R² por derivada: {cifra1}")
    anota("1", "-", "veredicto_se_sostiene", int(ok1), f"mejor R2: {cifra1}")

    # --- Hipótesis 2: lipo_neta es lineal en MolLogP y TPSA ---
    t = der["lipo_neta"].values
    lin = LinearRegression().fit(X[["MolLogP", "TPSA"]].values, t)
    r2_dir = lin.score(X[["MolLogP", "TPSA"]].values, t)
    anota("2", "lipo_neta", "R2_entrenamiento_MolLogP_TPSA", r2_dir,
          f"coef MolLogP={lin.coef_[0]:.4f}, coef TPSA={lin.coef_[1]:.4f}")
    filas = [dict(medida="R² lipo_neta ~ MolLogP + TPSA", valor=r2_dir,
                  detalle=f"coef MolLogP {lin.coef_[0]:.4f}, TPSA {lin.coef_[1]:.4f}")]
    if "MolLogP" not in base:
        cols = [n for n, _ in correlacionadas(X, "MolLogP", base)]
        if cols:
            ajuste = LinearRegression().fit(X[cols + ["TPSA"]].values if "TPSA" in base else X[cols].values, t)
            usadas = cols + (["TPSA"] if "TPSA" in base else [])
            r2s = ajuste.score(X[usadas].values, t)
            filas.append(dict(medida="R² con la sustituta de MolLogP en la base", valor=r2s,
                              detalle=" + ".join(usadas)))
            anota("2", "lipo_neta", "R2_entrenamiento_sustituta", r2s, " + ".join(usadas))
    r2_base = cross_val_score(LinearRegression(), Xb, t, groups=g, cv=gkf, scoring="r2").mean()
    filas.append(dict(medida="R² CV con todos los descriptores base", valor=r2_base,
                      detalle="mismo de H1"))
    tabla("H2. Lipo_neta como combinación lineal", pd.DataFrame(filas))
    ok2 = r2_dir > 0.999999
    print(f"H2 (criterio: R² >= 0.999999): {'SE SOSTIENE' if ok2 else 'NO SE SOSTIENE'}"
          f" — R² = {r2_dir:.6f}"
          + ("" if "MolLogP" in base else
             f"; MolLogP no sobrevive a la base, así que en un modelo sin derivadas la combinación "
             f"solo es exacta con su sustituta (R² {filas[1]['valor']:.3f})" if len(filas) > 2 else ""))
    anota("2", "-", "veredicto_se_sostiene", int(ok2), f"R2={r2_dir:.6f}")

    # --- Hipótesis 3: regla_2p son dos cortes ---
    Xr = X[["TPSA", "NumHDonors"]].values
    tr_reg = der["regla_2p"].values.astype(int)
    arbol = DecisionTreeClassifier(max_depth=2, random_state=0).fit(Xr, tr_reg)
    ex_tr = arbol.score(Xr, tr_reg)
    pred = cross_val_predict(DecisionTreeClassifier(max_depth=2, random_state=0), Xr, tr_reg,
                             groups=g, cv=gkf)
    ex_cv = float((pred == tr_reg).mean())
    umbrales = [f"x{arbol.tree_.feature[i]}<={arbol.tree_.threshold[i]:.2f}"
                for i in range(arbol.tree_.node_count) if arbol.tree_.feature[i] >= 0]
    nombres_cols = ["TPSA", "NumHDonors"]
    umbrales = [u.replace("x0", nombres_cols[0]).replace("x1", nombres_cols[1]) for u in umbrales]
    tabla("H3. Árbol de profundidad 2 sobre TPSA y NumHDonors que predice regla_2p",
          pd.DataFrame([dict(medida="exactitud entrenamiento", valor=ex_tr, cortes="; ".join(umbrales)),
                        dict(medida="exactitud CV agrupada", valor=ex_cv, cortes="")]))
    anota("3", "regla_2p", "exactitud_entrenamiento", ex_tr, "; ".join(umbrales))
    anota("3", "regla_2p", "exactitud_cv_agrupada", ex_cv, "")
    ok3 = ex_cv >= 0.99
    print(f"H3 (criterio: exactitud CV >= 0.99): {'SE SOSTIENE' if ok3 else 'NO SE SOSTIENE'}"
          f" — exactitud {ex_cv:.4f}")
    anota("3", "-", "veredicto_se_sostiene", int(ok3), f"exactitud_cv={ex_cv:.4f}")

    # --- Hipótesis 4: AUROC individual e importancia por permutación ---
    def auroc(v: np.ndarray) -> float:
        a = roc_auc_score(y, v)
        return max(a, 1 - a)

    filas = []
    for nombre, v in [*[(c, X[c].values) for c in TODOS_COMP], *[(dv, der[dv].values) for dv in DERIVADAS]]:
        filas.append(dict(variable=nombre, tipo="derivada" if nombre in DERIVADAS else "componente",
                          AUROC_individual=auroc(v)))
        anota("4", nombre, "AUROC_individual_entrenamiento", filas[-1]["AUROC_individual"],
              filas[-1]["tipo"])
    tabla("H4a. AUROC individual en entrenamiento (signo con AUROC >= 0.5)", pd.DataFrame(filas))
    au_der = {f["variable"]: f["AUROC_individual"] for f in filas if f["tipo"] == "derivada"}

    def scorer(est, Xe, ye):
        return average_precision_score(1 - ye, est.predict_proba(Xe)[:, 0])

    conjuntos = {"sin": X, "con": pd.concat([X, der], axis=1)}
    imp = {k: [] for k in conjuntos}   # por pliegue: Series nombre -> importancia
    vivas = {k: [] for k in conjuntos}
    cv = StratifiedGroupKFold(n_splits=PLIEGUES, shuffle=True, random_state=0)
    for k, (ia, ib) in enumerate(cv.split(np.zeros(len(y)), y, g)):
        for clave, M in conjuntos.items():
            cols = seleccion(M.iloc[ia], y[ia])
            rf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=0)
            rf.fit(M.iloc[ia][cols].values, y[ia])
            r = permutation_importance(rf, M.iloc[ib][cols].values, y[ib], scoring=scorer,
                                       n_repeats=5, random_state=0)
            imp[clave].append(pd.Series(r.importances_mean, index=cols))
            vivas[clave].append(set(cols))
        print(f"H4 pliegue {k} listo ({time.time()-t0:.0f}s)", flush=True)

    def importancia(clave: str, nombres: list[str]) -> tuple[float, float]:
        """Suma de importancias de `nombres` por pliegue (0 si la columna se descartó) y
        fracción de pliegues en que alguna sobrevivió."""
        vals = [sum(s.get(n, 0.0) for n in nombres) for s in imp[clave]]
        vivo = np.mean([any(n in v for n in nombres) for v in vivas[clave]])
        return float(np.mean(vals)), float(vivo)

    filas = []
    caida_total = 0.0
    for c in TODOS_COMP:
        grupo = sustituta[c]   # la columna misma o, si no sobrevive a la base, sus correlacionadas
        if c in base:
            grupo = [c]
        elif not grupo:
            grupo = [c]
        i_sin, v_sin = importancia("sin", grupo)
        i_con, v_con = importancia("con", grupo)
        caida_total += i_sin - i_con
        filas.append(dict(columna=c, grupo="+".join(grupo[:3]), imp_sin=i_sin, imp_con=i_con,
                          cambio=i_con - i_sin, viva_sin=v_sin, viva_con=v_con))
        anota("4", c, "importancia_sin_derivadas", i_sin, f"grupo {'+'.join(grupo[:3])}; viva {v_sin:.1f}")
        anota("4", c, "importancia_con_derivadas", i_con, f"grupo {'+'.join(grupo[:3])}; viva {v_con:.1f}")
    ganancia = 0.0
    for dv in DERIVADAS:
        i_con, v_con = importancia("con", [dv])
        ganancia += i_con
        filas.append(dict(columna=dv, grupo=dv, imp_sin=0.0, imp_con=i_con, cambio=i_con,
                          viva_sin=0.0, viva_con=v_con))
        anota("4", dv, "importancia_con_derivadas", i_con, f"viva en {v_con:.1f} de los pliegues")
    tabla("H4b. Importancia por permutación (caída de AUPRC BBB−), media de 5 pliegues agrupados",
          pd.DataFrame(filas))
    cambio_comp = -caida_total
    anota("4", "-", "caida_componentes", caida_total, "suma de (sin − con) en los 4 componentes")
    anota("4", "-", "ganancia_derivadas", ganancia, "suma de importancias de las 3 derivadas")
    # El AUROC individual es descriptivo, no parte del criterio: la hipótesis es que una
    # variable buena por sí sola no aporta si su información ya está en otras columnas, y eso
    # se ve en si la importancia que gana la derivada sale de sus componentes. Un umbral de
    # AUROC individual no contesta esa pregunta (una versión anterior lo usaba).
    redistrib = ganancia > 0 and caida_total >= 0.5 * ganancia
    ok4 = redistrib
    print(f"H4 (criterio: los componentes pierden al menos la mitad de lo que ganan las "
          f"derivadas): {'SE SOSTIENE' if ok4 else 'NO SE SOSTIENE'}"
          f" — componentes pierden {caida_total:.4f}, derivadas ganan {ganancia:.4f} "
          f"(cambio neto de componentes {cambio_comp:+.4f}). AUROC individual de las derivadas, "
          f"solo descriptivo: mín {min(au_der.values()):.3f}, máx {max(au_der.values()):.3f}.")
    print("   Cautela: son importancias de milésimas y con descriptores muy correlacionados la "
          "permutación se reparte entre columnas casi iguales; es la evidencia más débil de las cuatro.")
    anota("4", "-", "veredicto_se_sostiene", int(ok4),
          f"AUROC_min={min(au_der.values()):.3f}; caida={caida_total:.4f}; ganancia={ganancia:.4f}")

    # --- salida ---
    res = pd.DataFrame(FILAS)
    salida = RAIZ / "notebooks/datos/analisis_derivadas.csv"
    salida.parent.mkdir(parents=True, exist_ok=True)
    res.to_csv(salida, index=False)
    print("\nescrito", salida)
    print(f"tiempo total {time.time()-t0:.0f}s")

    if not args.sin_registro:
        params = dict(seleccion=dict(casi_constante_min_distintas=10, correlacion_spearman=RHO),
                      pliegues=PLIEGUES, U=U, rf=dict(n_estimators=200, random_state=0),
                      permutacion=dict(n_repeats=5, scoring="AUPRC clase minoritaria"),
                      partición=dict(fraccion_prueba=0.2, fraccion_validacion=0.1, semilla=42,
                                     acíclicos_a="entrenamiento"))
        with Corrida("derivadas-por-que", decision="1.3", params=params, semillas=[0, 42],
                     datos=[datos]) as registro:
            registro.metricas({
                "h1": {r.derivada: {"R2_lineal": float(r.R2_LinearRegression),
                                    "R2_rf": float(r.R2_RandomForest)} for r in h1.itertuples()},
                "h2_R2_directo": float(r2_dir),
                "h3": {"exactitud_entrenamiento": float(ex_tr), "exactitud_cv": ex_cv},
                "h4": {"auroc_derivadas": {k: float(v) for k, v in au_der.items()},
                       "caida_componentes": float(caida_total), "ganancia_derivadas": float(ganancia)},
                "veredictos": {"h1": ok1, "h2": bool(ok2), "h3": ok3, "h4": ok4}})


if __name__ == "__main__":
    main()
