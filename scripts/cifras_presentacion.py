#!/usr/bin/env python3
"""Los datos que alimentan las gráficas interactivas de la presentación.

Escribe `recursos/datos.js`, que la presentación carga con una etiqueta
`<script>`. Cada número que se ve en una gráfica sale de aquí, recalculado
desde los archivos de la patrocinadora, y no de una cifra copiada a mano.

    python scripts/cifras_presentacion.py

Lo que calcula, y para qué gráfica:

- **Esqueletos.** Filas contra esqueletos de conectividad, los que reúnen
  etiquetas contradictorias y el techo de exactitud que imponen.
- **Grupos A–D.** Tamaño y reparto de clases por grupo, para la gráfica donde
  se filtra a A+B y se ve empeorar el desbalance en vez de limpiarlo.
- **Naturales por grupo.** La brecha entre naturales y el resto dentro de cada
  grupo, con su intervalo de confianza: es la medición que distingue entre
  química y artefacto de curación (decisión 1.6).
- **Barrido de TPSA.** Para cada corte de 0 a 200 Å² y cada subconjunto, la
  matriz de confusión de la regla «TPSA < corte ⇒ BBB+». Con eso el control
  deslizante de la presentación recalcula sensibilidad, especificidad y MCC en
  el navegador sin volver a tocar los datos. Es lo que hace ver que el umbral
  no es una constante sino el óptimo de un subconjunto.
- **Etiquetado.** Qué cuesta cortar «activo» en 1 µM o en 10 µM, con el peso
  que tiene una sola referencia de ChEMBL entre los negativos.

**Qué no recalcula, y hay que decirlo.** El reparto de activos e inactivos
(`balance`: 61.7% con ≥ 5 y 44.4% con ≥ 6) viene del notebook 01b, porque
depende de toda la canalización de etiquetado por tres vías y no de un conteo.
Está marcado en el código donde se usa. Todo lo demás —incluidos los 99,585
esqueletos de la fase 2 y los 1,033 que comparte con la fase 1, que antes
estaban escritos a mano— sale de los archivos en cada corrida.

El script tarda cerca de dos minutos: la partición por andamio, el bootstrap de
las mesetas y los esqueletos de conectividad del archivo de actividad.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

PERMEABILIDAD = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
DIANAS = RAIZ / "data/external/profesora/etiquetas_dianas_2026-09-25.csv"
ACTIVIDAD = (RAIZ / "data/external/profesora"
             / "snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv")
SALIDA = RAIZ / "recursos/datos.js"
ESCALADO = RAIZ / "notebooks/datos/resultados_escalado.csv"
VOCABULARIO = RAIZ / "notebooks/datos/resultados_L_sortslice.csv"

CORTES_TPSA = list(range(0, 201))
CENSURA = (">", ">=", ">>")
A_MICROMOLAR = {"nM": 1e-3, "uM": 1.0, "um": 1.0, "mM": 1e3, "M": 1e6,
                "10^3nM": 1.0}


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def ic_diferencia(p1: float, n1: int, p2: float, n2: int) -> list[float]:
    """Intervalo del 95% para la diferencia de dos proporciones, en puntos."""
    ee = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    return [round(100 * (d - 1.96 * ee), 1), round(100 * (d + 1.96 * ee), 1)]


def mcc(tp: int, fn: int, fp: int, tn: int) -> float:
    den = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    return ((tp * tn - fp * fn) / den) if den else 0.0


def barrido(tpsa: pd.Series, positivo: pd.Series) -> list[list[int]]:
    """Matriz de confusión de «TPSA < corte ⇒ BBB+», para cada corte."""
    filas = []
    for corte in CORTES_TPSA:
        pred = tpsa < corte
        tp = int((pred & positivo).sum())
        fp = int((pred & ~positivo).sum())
        fn = int((~pred & positivo).sum())
        tn = int((~pred & ~positivo).sum())
        filas.append([tp, fn, fp, tn])
    return filas


REMUESTREOS = 2000     # bootstrap sobre los compuestos, para la meseta
SEMILLA_BOOTSTRAP = 42


def indice_j(filas: list[list[int]]) -> list[float]:
    js = []
    for tp, fn, fp, tn in filas:
        sens = tp / (tp + fn) if tp + fn else 0
        esp = tn / (tn + fp) if tn + fp else 0
        js.append(sens + esp - 1)
    return js


def meseta_bootstrap(tpsa: pd.Series, positivo: pd.Series, grupo: pd.Series,
                     mejor: int) -> dict:
    """Qué cortes no se distinguen del mejor, con bootstrap **por esqueleto**.

    La primera versión usaba una tolerancia fija de 0.005 en J, que es un número
    inventado: decía «indistinguible» sin medición detrás. La segunda remuestreaba
    compuestos, y eso también estaba mal: las 7,805 filas son 4,018 esqueletos de
    conectividad, con andamios de hasta 410 compuestos, así que tratarlas como
    independientes da intervalos demasiado angostos y **subestima** la meseta,
    justo en la dirección contraria a la que conviene equivocarse. Aquí se
    remuestrean **esqueletos enteros**, que es la misma unidad con la que el
    proyecto parte los datos (decisiones 1.2, 1.5 y 1.7).

    Cada corte se compara contra el mejor **dentro de la misma remuestra**, que
    elimina la varianza común, y se conservan aquellos cuyo intervalo del 95% de
    la diferencia incluye el cero: *no se distingue del mejor con estos datos*.

    **Un sesgo que queda y conviene declarar:** el corte de referencia es el que
    gana en la muestra completa, no el ganador de cada remuestra. Eso favorece
    levemente a ese corte y, por tanto, ensancha un poco la meseta. Se prefiere
    así porque la alternativa —el mejor de cada remuestra— compara contra un
    objetivo móvil y mezcla dos preguntas distintas.

    El truco para que 2,000 remuestras sean baratas: un compuesto entra en la
    predicción del corte `c` si `tpsa < c`, o sea desde `k = floor(tpsa) + 1` en
    adelante. Así la matriz de confusión de todos los cortes sale de dos
    histogramas acumulados por remuestra, en vez de recorrer 201 cortes.
    """
    import numpy as np

    k = np.floor(tpsa.to_numpy()).astype(int) + 1
    k = np.clip(k, 0, len(CORTES_TPSA))
    pos = positivo.to_numpy().astype(bool)
    P, N = int(pos.sum()), int((~pos).sum())
    if not P or not N:
        return {"meseta": [mejor, mejor], "contigua": True, "remuestreos": 0,
                "unidad": "esqueleto de conectividad", "clusteres": 0}

    # las filas de cada esqueleto, para remuestrear el esqueleto completo
    codigos = pd.factorize(grupo.to_numpy())[0]
    orden = np.argsort(codigos, kind="stable")
    cortes_cluster = np.searchsorted(codigos[orden], np.arange(codigos.max() + 2))
    clusteres = [orden[cortes_cluster[i]:cortes_cluster[i + 1]]
                 for i in range(codigos.max() + 1)]
    n_cl = len(clusteres)

    def js_de(idx):
        kp = np.bincount(k[idx][pos[idx]], minlength=len(CORTES_TPSA) + 1)
        kn = np.bincount(k[idx][~pos[idx]], minlength=len(CORTES_TPSA) + 1)
        tp = np.cumsum(kp)[: len(CORTES_TPSA)]
        fp = np.cumsum(kn)[: len(CORTES_TPSA)]
        tot_p, tot_n = kp.sum(), kn.sum()
        sens = tp / tot_p if tot_p else np.zeros_like(tp, dtype=float)
        esp = (tot_n - fp) / tot_n if tot_n else np.zeros_like(fp, dtype=float)
        return sens + esp - 1

    rng = np.random.default_rng(SEMILLA_BOOTSTRAP)
    i_mejor = CORTES_TPSA.index(mejor)
    difs = np.empty((REMUESTREOS, len(CORTES_TPSA)))
    for b in range(REMUESTREOS):
        elegidos = rng.integers(0, n_cl, n_cl)
        idx = np.concatenate([clusteres[c] for c in elegidos])
        js = js_de(idx)
        difs[b] = js[i_mejor] - js          # pareado dentro de la misma remuestra

    bajo, alto = np.percentile(difs, [2.5, 97.5], axis=0)
    sin_distinguir = [c for c, lo, hi in zip(CORTES_TPSA, bajo, alto) if lo <= 0 <= hi]
    if not sin_distinguir:
        sin_distinguir = [mejor]
    rango = range(min(sin_distinguir), max(sin_distinguir) + 1)
    return {
        "meseta": [min(sin_distinguir), max(sin_distinguir)],
        # el conjunto exacto, porque casi nunca es contiguo y pintar solo el
        # mínimo y el máximo daría una banda llena donde hay huecos
        "cortes_meseta": sin_distinguir,
        "contigua": len(sin_distinguir) == len(rango),
        "remuestreos": REMUESTREOS,
        "unidad": "esqueleto de conectividad",
        "clusteres": n_cl,
    }


def optimo(filas: list[list[int]], tpsa: pd.Series, positivo: pd.Series,
           grupo: pd.Series) -> dict:
    """El corte que maximiza el índice J de Youden, y la meseta a su alrededor.

    El óptimo por sí solo engaña: en el conjunto completo J vale 0.4824 en 101 Å²
    y 0.4833 en 107, una diferencia de 0.0009. La meseta dice hasta dónde llega
    esa indistinguibilidad, y sale de un bootstrap, no de una tolerancia a ojo.
    """
    js = indice_j(filas)
    mejor_j = max(js)
    mejor = CORTES_TPSA[js.index(mejor_j)]
    tp, fn, fp, tn = filas[CORTES_TPSA.index(mejor)]
    return {"corte": mejor, "j": round(mejor_j, 3), "mcc": round(mcc(tp, fn, fp, tn), 3),
            **meseta_bootstrap(tpsa, positivo, grupo, mejor)}


def permeabilidad() -> dict:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors
    from data_prep.splits import andamio_murcko, esqueleto_conectividad, scaffold_split

    RDLogger.DisableLog("rdApp.*")
    df = pd.read_csv(PERMEABILIDAD, low_memory=False)
    d = df[df["bbb_class"].notna()].copy()
    d["key14"] = d["inchikey"].astype(str).str[:14]
    d["positivo"] = d["bbb_class"].astype(str).str.upper().str.startswith("BBB+")
    d["natural"] = d["coconut_id_exact_match"].notna()
    d["grupo"] = d["b3db_uncertainty_classification"].astype(str).str.strip().str.upper()

    print(f"  {len(d):,} filas con clase · {d['key14'].nunique():,} esqueletos")

    # --- esqueletos y el techo que imponen las etiquetas contradictorias ---
    por_esqueleto = d.groupby("key14")["bbb_class"]
    aciertos = int(por_esqueleto.agg(lambda s: s.value_counts().iloc[0]).sum())
    contradictorios = por_esqueleto.nunique()
    contradictorios = contradictorios[contradictorios > 1]
    esqueletos = {
        "filas": len(d),
        "esqueletos": int(d["key14"].nunique()),
        "contradictorios": int(len(contradictorios)),
        "filas_contradictorias": int(d["key14"].isin(contradictorios.index).sum()),
        "errores_inevitables": len(d) - aciertos,
        "techo_exactitud": round(100 * aciertos / len(d), 2),
    }

    # --- grupos A–D: lo que cuesta filtrar a A+B ---
    grupos = []
    for g in ("A", "B", "C", "D"):
        sub = d[d["grupo"] == g]
        if not len(sub):
            continue
        grupos.append({
            "grupo": g,
            "n": len(sub),
            "pos": int(sub["positivo"].sum()),
            "neg": int((~sub["positivo"]).sum()),
        })
    ab = d[d["grupo"].isin(["A", "B"])]
    filtrado = {
        "completo": {"n": len(d), "pct_minoritaria": round(100 * (~d["positivo"]).mean(), 1)},
        "ab": {"n": len(ab), "pct_minoritaria": round(100 * (~ab["positivo"]).mean(), 1)},
    }

    # --- naturales dentro de cada grupo: química o curación ---
    naturales = []
    for g in ("A", "B", "C", "D"):
        sub = d[d["grupo"] == g]
        nat, res = sub[sub["natural"]], sub[~sub["natural"]]
        if len(nat) < 5 or len(res) < 5:
            continue
        p_nat, p_res = nat["positivo"].mean(), res["positivo"].mean()
        naturales.append({
            "grupo": g,
            "nat_n": len(nat), "nat_pct": round(100 * p_nat, 1),
            "res_n": len(res), "res_pct": round(100 * p_res, 1),
            "dif": round(100 * (p_res - p_nat), 1),
            "ic": ic_diferencia(p_res, len(res), p_nat, len(nat)),
        })
    global_nat, global_res = d[d["natural"]], d[~d["natural"]]
    naturales_global = {
        "nat_n": len(global_nat), "nat_pct": round(100 * global_nat["positivo"].mean(), 1),
        "res_n": len(global_res), "res_pct": round(100 * global_res["positivo"].mean(), 1),
        "dif": round(100 * (global_res["positivo"].mean() - global_nat["positivo"].mean()), 1),
    }

    # --- TPSA y el barrido por subconjunto ---
    print("  calculando TPSA con RDKit…")
    d["mol"] = d["smiles_std"].map(lambda s: Chem.MolFromSmiles(s) if isinstance(s, str) else None)
    d = d[d["mol"].notna()].copy()
    d["tpsa"] = d["mol"].map(Descriptors.TPSA)

    print("  repitiendo la partición por andamio…")
    d["andamio"] = d["mol"].map(andamio_murcko)
    d["esqueleto"] = d["mol"].map(esqueleto_conectividad)
    d["particion"] = scaffold_split(d, fraccion_prueba=0.2, fraccion_validacion=0.1,
                                    semilla=42)

    subconjuntos = {
        "completo": d,
        "ab": d[d["grupo"].isin(["A", "B"])],
        "a": d[d["grupo"] == "A"],
        "entrenamiento": d[d["particion"] == "entrenamiento"],
    }
    tpsa = {"cortes": CORTES_TPSA, "series": {}, "optimos": {}, "n": {}}
    for nombre, sub in subconjuntos.items():
        filas = barrido(sub["tpsa"], sub["positivo"])
        tpsa["series"][nombre] = filas
        tpsa["optimos"][nombre] = optimo(filas, sub["tpsa"], sub["positivo"],
                                         sub["esqueleto"])
        tpsa["n"][nombre] = len(sub)
        o = tpsa["optimos"][nombre]
        print(f"    {nombre:<14} n={len(sub):>5,} · óptimo {o['corte']} Å²"
              f" · {o['clusteres']:,} esqueletos"
              f" · no se distingue de {o['meseta'][0]}–{o['meseta'][1]}"
              f"{'' if o['contigua'] else ' (no contigua)'}")

    return {"_esqueletos_permeabilidad": sorted(d["key14"].unique()),
            "esqueletos": esqueletos, "grupos": grupos, "filtrado_ab": filtrado,
            "naturales": naturales, "naturales_global": naturales_global, "tpsa": tpsa}


def esqueletos_actividad(df: pd.DataFrame) -> set[str]:
    """Los esqueletos de conectividad del archivo de actividad.

    `inchikey_source` viene vacío en los 187,354 registros de ChEMBL, así que se
    calcula desde `smiles_raw`. Se resuelve sobre los SMILES **únicos** (108,076
    de 202,647 filas), que es lo que lo vuelve barato: unos doce segundos.
    """
    from rdkit import Chem, RDLogger

    RDLogger.DisableLog("rdApp.*")
    unicos = df["smiles_raw"].dropna().unique()
    fuera = set()
    for s in unicos:
        m = Chem.MolFromSmiles(s)
        if m is not None:
            fuera.add(Chem.MolToInchiKey(m)[:14])
    return fuera


def actividad() -> dict:
    df = pd.read_csv(ACTIVIDAD, low_memory=False)
    relacion = df["activity_relation_used"]
    censurado = relacion.isin(CENSURA)
    texto = df["chembl_standard_text_value"].notna()
    valor = pd.to_numeric(df["activity_value_used"], errors="coerce")
    micromolar = valor * df["activity_units_used"].fillna("").map(A_MICROMOLAR)

    cortes = {}
    for umbral in (1, 10):
        seguros = censurado & (micromolar >= umbral)
        cortes[str(umbral)] = {
            "seguros": int(seguros.sum()),
            "ambiguos": int(censurado.sum() - seguros.sum()),
            "de_una_referencia": int((seguros & texto).sum()),
            "pct_una_referencia": round(100 * (seguros & texto).sum() / seguros.sum(), 1),
        }

    # volúmenes por enfermedad: de ahí sale la pregunta de la forma del modelo
    categorias = df["diana_categoria"].value_counts()
    enfermedades = [{"nombre": k, "n": int(v)} for k, v in categorias.items()
                    if k != "Sin diana de la lista"]

    # Las 39 dianas curadas a mano. Dos cuentas distintas y hay que no confundirlas:
    # `filas_v3` es la que declara el archivo de la patrocinadora, sobre el archivo
    # completo; `nuestras` es la que sale de unir por `target_gene` en el que
    # recibimos. Los dos receptores completos (NMDA y GABA-A) no son genes, así que
    # esa unión no los encuentra y su cuenta propia queda en None en vez de en cero:
    # publicarlos como «0 registros» los haría parecer candidatos a excluir sin serlo.
    dianas = []
    if DIANAS.exists():
        dd = pd.read_csv(DIANAS)
        por_gen = df["target_gene"].value_counts()
        for _, fila in dd.iterrows():
            gen = str(fila["gen"])
            es_gen = "receptor completo" not in gen
            dianas.append({"gen": gen, "diana": str(fila["diana"]),
                           "categoria": str(fila["diana_categoria"]),
                           "declaradas": int(fila["filas_v3"]),
                           "nuestras": int(por_gen.get(gen, 0)) if es_gen else None})
        dianas.sort(key=lambda d: d["declaradas"])

    print("  resolviendo esqueletos de conectividad…")
    esqueletos = esqueletos_actividad(df)

    print(f"  {len(df):,} registros · {int(censurado.sum()):,} censurados")
    print(f"  {len(esqueletos):,} esqueletos de conectividad")
    print(f"  {len(dianas)} dianas · "
          f"{sum(1 for d in dianas if d['declaradas'] < 10)} con menos de 10 registros declarados")
    return {
        "registros": len(df),
        "esqueletos": sorted(esqueletos),   # se usa para cruzar con la fase 1
        "registros_diccionario": 225513,   # el archivo completo, sección 1 del diccionario
        "enfermedades": enfermedades,
        "dianas": dianas,
        "naturales": int(df["source"].isin(["npass", "cmaup"]).sum()),
        "naturales_exactos": int((df["source"].isin(["npass", "cmaup"])
                                  & relacion.eq("=")).sum()),
        "censurados": int(censurado.sum()),
        "texto": int(texto.sum()),
        "referencia_dominante": str(df.loc[texto, "reference_id"].mode().iloc[0]),
        "cortes": cortes,
        # el balance de clases sale del notebook 01b, no de aquí
        "balance": {"1": {"pct_activos": 44.4, "razon": "0.8:1"},
                    "10": {"pct_activos": 61.7, "razon": "1.6:1"}},
    }


def experimentos() -> dict:
    """Los dos experimentos del Avance 2, resumidos desde sus CSV versionados.

    No se vuelven a correr aquí: `scripts/experimento_escalado.py` y
    `scripts/experimento_L_sortslice.py` ya dejaron sus resultados, con su
    corrida registrada en `experimentos/`. Esto solo los agrega para que las
    diapositivas los dibujen, de modo que si alguien repite un experimento la
    presentación cambia con él.

    El error estándar se corrige por Nadeau y Bengio, porque las 15 evaluaciones
    (3 semillas × 5 pliegues) comparten datos de entrenamiento y el ingenuo las
    trataría como independientes. El factor sale de la proporción entre el
    pliegue de evaluación y el de entrenamiento.
    """
    import numpy as np

    fuera: dict = {}

    if ESCALADO.exists():
        e = pd.read_csv(ESCALADO)
        cv = e[e["eval"] == "cv"]
        filas = []
        for (trans, modelo), g in cv.groupby(["transformacion", "modelo"]):
            filas.append({
                "transformacion": trans, "modelo": modelo,
                "mcc": round(g["MCC"].mean(), 4),
                "auprc": round(g["AUPRC_neg"].mean(), 4),
                "iteraciones": int(g["n_iter"].median()) if g["n_iter"].notna().any() else None,
                "sin_converger": int(g["sin_converger"].sum()) if g["sin_converger"].notna().any() else 0,
                "evaluaciones": len(g),
                "segundos": round(g["ajuste_s"].median(), 4) if g["ajuste_s"].notna().any() else None,
            })
        fuera["escalado"] = sorted(filas, key=lambda f: (f["modelo"], -f["mcc"]))
        print(f"  escalado: {len(filas)} combinaciones de {len(cv)} evaluaciones")

    if VOCABULARIO.exists():
        v = pd.read_csv(VOCABULARIO)
        cv = v[v["eval"] == "cv"]
        # corrección de Nadeau y Bengio para pliegues que comparten entrenamiento
        n_pl = cv["fold"].nunique() or 5
        factor = np.sqrt(1 + (1 / n_pl) / (1 - 1 / n_pl))
        filas = []
        for (L, modelo), g in cv.groupby(["L", "modelo"]):
            ee = g["MCC"].std(ddof=1) / np.sqrt(len(g))
            filas.append({"L": int(L), "modelo": modelo,
                          "mcc": round(g["MCC"].mean(), 4),
                          "auprc": round(g["AUPRC_neg"].mean(), 4),
                          "ee": round(float(ee * factor), 4)})
        cob = v[v["eval"] == "cov"]
        fuera["vocabulario"] = {
            "puntos": sorted(filas, key=lambda f: (f["modelo"], f["L"])),
            "cobertura": [{"L": int(r.L), "entrenamiento": round(float(r.cob_entrenamiento), 3),
                           "validacion": round(float(r.cob_validacion), 3)}
                          for r in cob.itertuples()] if len(cob) else [],
            "vocabulario_total": int(cob["vocabulario_total"].iloc[0]) if len(cob) else None,
        }
        print(f"  vocabulario: {len(filas)} combinaciones · "
              f"{fuera['vocabulario']['vocabulario_total']:,} subestructuras en total")

    return fuera


def main() -> None:
    for ruta in (PERMEABILIDAD, ACTIVIDAD):
        if not ruta.exists():
            raise SystemExit(f"falta {ruta.relative_to(RAIZ)}")

    print("Permeabilidad…")
    datos = permeabilidad()
    print("Actividad…")
    datos["actividad"] = actividad()

    # el cruce entre las dos fases: antes estaban escritos a mano el 99,585 y el
    # 1,033, que son justo las cifras de las que cuelga la decisión C.3
    de_actividad = set(datos["actividad"].pop("esqueletos"))
    de_permeabilidad = set(datos.pop("_esqueletos_permeabilidad"))
    ambos = de_actividad & de_permeabilidad
    datos["etapas"] = {"permeabilidad": len(de_permeabilidad),
                       "actividad": len(de_actividad), "ambos": len(ambos)}
    print(f"\nCruce de fases: {len(ambos):,} esqueletos en ambas "
          f"({100 * len(ambos) / len(de_actividad):.1f}% de la fase 2, "
          f"{100 * len(ambos) / len(de_permeabilidad):.1f}% de la fase 1)")
    print("Experimentos del Avance 2…")
    datos["experimentos"] = experimentos()
    datos["generado"] = date.today().isoformat()
    datos["huellas"] = {PERMEABILIDAD.name: sha256(PERMEABILIDAD)[:16],
                        ACTIVIDAD.name: sha256(ACTIVIDAD)[:16]}
    try:
        datos["commit"] = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ,
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        datos["commit"] = None

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    cuerpo = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    SALIDA.write_text(
        "// Generado por scripts/cifras_presentacion.py — no editar a mano.\n"
        f"window.DATOS = {cuerpo};\n", encoding="utf-8")
    print(f"\n{SALIDA.relative_to(RAIZ)} · {SALIDA.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
