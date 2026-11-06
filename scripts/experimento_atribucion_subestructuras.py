#!/usr/bin/env python3
"""¿Qué subestructuras pesan en el `aft` con huellas, según dos métodos independientes? (#146, C.2)

La C.2 pide atribución **por subestructura** y el `aft` final no usa huellas (ver la entrada de la 2.13 sobre
`2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion`). El brazo `aft_huellas` (201 descriptores,
2,048 huellas Sort & Slice y la diana) sí: cada columna de huella es un identificador de Morgan de radio 2, es
decir, **un fragmento molecular concreto**. Aquí se atribuye con TreeSHAP y con permutación, como en el modelo
final, y cada columna de huella se traduce a su fragmento.

**Es el brazo, no el modelo final**: no mejora al `aft` en NPASS (E3). Sirve para cumplir la parte de la C.2
que el modelo final no puede, y se dice así.

**Cómo.** Semilla 0, cinco pliegues agrupados. En cada pliegue se ajusta el brazo con las filas de ajuste y se
atribuye sobre la validación: TreeSHAP (`pred_contribs`) sobre todas las filas, y permutación sobre 1,500 filas al
azar con una repetición por columna (el costo crece con las ~2,270 columnas). Se promedia por columna sobre los
pliegues; una columna que no está en el vocabulario de un pliegue cuenta 0 en él.

**Lo que se declara antes de correr** (escrito antes de ver ningún resultado):
1. Control: la suma de contribuciones más el sesgo reproduce el margen del modelo (< 1e-3) y coincide con
   `shap.TreeExplainer` en 200 filas (< 1e-3). Y el nombre de cada fragmento se verifica: el identificador sale
   de la molécula de ejemplo con otra API de RDKit (`GetMorganFingerprint`) en 20 moléculas al azar.
2. **Los métodos concuerdan** si el Spearman entre sus importancias, sobre la unión de las 100 columnas más
   importantes de cada uno, es al menos 0.50 y comparten al menos 8 de sus 15 primeras. Es una vara más
   baja que la del modelo final (0.70 sobre 227 columnas) porque aquí hay ~2,270 columnas y casi todas valen ~0.
3. **Solo se afirman las subestructuras que están en el top 30 de los dos métodos**, con su fragmento. Las que
   solo ve uno se listan aparte y no se afirman.
4. Contraste con TPSA (< 67 Å²) y HBD (≤ 1): su lugar en cada método.
5. Un fragmento que representa varias subestructuras (`agrupar_iguales`) se nombra con la primera y se dice
   cuántas equivalentes tiene.

No toca la prueba reservada.

    ./env312/bin/python scripts/experimento_atribucion_subestructuras.py
"""
import os

os.environ["OMP_NUM_THREADS"] = "1"

import sys
import time
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator, rdMolDescriptors
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.model_selection import StratifiedGroupKFold

from src.evaluation.regresion import concordancia_harrell
from src.features.huellas import agrupar_iguales, identificadores_morgan
from src.models.aft import RegresionAFT
from src.models.baseline_regresion import ConHuellasCensurado
from src.tracking import Corrida

PROCESADOS = RAIZ / "data" / "processed"
PARES = PROCESADOS / "fase2_pares.parquet"
DESCRIPTORES = PROCESADOS / "fase2_descriptores_limpios.parquet"
SEMILLA = 0
PLIEGUES = 5
N_BITS = 2048
FILAS_PERMUTACION = 1_500
TOP_ACUERDO = 15
TOP_AFIRMAR = 30
UNION_TOP = 100
RHO_MINIMO = 0.50
COMPARTIDAS_MINIMO = 8
TOLERANCIA = 1e-3


def datos() -> dict:
    pares = pd.read_parquet(PARES)
    desc = pd.read_parquet(DESCRIPTORES)
    d = pares.merge(desc, on="smiles").reset_index(drop=True)
    cols = [c for c in desc.columns if c != "smiles"]
    inferior = d["limite_inferior"].to_numpy(float)
    superior = d["limite_superior"].to_numpy(float)
    util = ~(np.isneginf(inferior) & np.isposinf(superior)) & (inferior <= superior)
    d = d[util].reset_index(drop=True)
    inferior, superior = inferior[util], superior[util]
    fuera = (d["particion"] != "prueba").to_numpy()
    diana = pd.get_dummies(d["target_gene"])
    X = np.hstack([d[cols].to_numpy("float32"), diana.to_numpy("float32")])
    huellas, ids = identificadores_morgan(d["smiles"])
    huellas, ids, equivalentes = agrupar_iguales(huellas, ids)
    X_mixta = sparse.hstack([sparse.csr_matrix(X), huellas]).tocsr()
    assert fuera.sum() == 56_241
    return {"X_mixta": X_mixta[fuera], "inferior": inferior[fuera], "superior": superior[fuera],
            "grupos": d["grupo_cv"].to_numpy()[fuera], "clase": d["activo_10um"].to_numpy(float)[fuera],
            "smiles": d["smiles"].to_numpy()[fuera], "n_densas": X.shape[1], "ids": ids,
            "equivalentes": equivalentes, "nombres_densas": cols + [f"diana:{c}" for c in diana.columns]}


def fragmentos(smiles_unicos, ids_buscados: set[int]) -> dict:
    """Para cada identificador, un fragmento de ejemplo (SMILES enraizado) y la molécula de donde sale."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2)
    pendientes, salida = set(int(i) for i in ids_buscados), {}
    for s in smiles_unicos:
        if not pendientes:
            break
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            continue
        ao = rdFingerprintGenerator.AdditionalOutput()
        ao.AllocateBitInfoMap()
        gen.GetSparseCountFingerprint(mol, additionalOutput=ao)
        info = ao.GetBitInfoMap()
        for i in list(pendientes):
            if i in info:
                atomo, radio = info[i][0]
                if radio == 0:
                    frag = mol.GetAtomWithIdx(atomo).GetSmarts()
                else:
                    enlaces = Chem.FindAtomEnvironmentOfRadiusN(mol, radio, atomo)
                    atomos = {atomo}
                    for b in enlaces:
                        bond = mol.GetBondWithIdx(b)
                        atomos.update((bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()))
                    frag = Chem.MolFragmentToSmiles(mol, atomsToUse=sorted(atomos), bondsToUse=list(enlaces),
                                                    rootedAtAtom=atomo, canonical=True)
                salida[i] = {"fragmento": frag, "radio": int(radio), "molecula_de_ejemplo": s}
                pendientes.discard(i)
    return salida


def permutacion(predecir, X, inferior, superior, rng) -> np.ndarray:
    idx = rng.choice(len(X), size=min(FILAS_PERMUTACION, len(X)), replace=False)
    Xs, inf, sup = X[idx].copy(), inferior[idx], superior[idx]
    base = concordancia_harrell(inf, sup, predecir(Xs))
    perdida = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        original = Xs[:, j].copy()
        Xs[:, j] = rng.permutation(original)
        perdida[j] = base - concordancia_harrell(inf, sup, predecir(Xs))
        Xs[:, j] = original
    return perdida


def main() -> None:
    d = datos()
    n_dens = d["n_densas"]
    clase = np.where(np.isnan(d["clase"]), -1, d["clase"]).astype(int)
    params = {"modelo": "aft_huellas (201 descriptores, 2,048 huellas Sort & Slice y la diana)", "semilla": SEMILLA,
              "pliegues": PLIEGUES, "metodos": ["TreeSHAP", "permutación sobre la concordancia"],
              "filas_permutacion": FILAS_PERMUTACION, "top_acuerdo": TOP_ACUERDO, "top_afirmar": TOP_AFIRMAR,
              "rho_minimo": RHO_MINIMO, "compartidas_minimo": COMPARTIDAS_MINIMO, "toca_prueba": False}
    with Corrida("atribucion-aft-huellas-subestructuras", decision="2.13", params=params, semillas=[SEMILLA],
                 datos=[PARES, DESCRIPTORES]) as c:
        nombres_todos: dict[str, int] = {n: i for i, n in enumerate(d["nombres_densas"])}   # columna -> posición global
        for i in d["ids"]:
            nombres_todos[f"id:{int(i)}"] = len(nombres_todos)
        n_total = len(nombres_todos)
        suma_shap, suma_perm = np.zeros(n_total), np.zeros(n_total)
        en_pliegue = np.zeros(n_total)
        control_adit, control_exp = [], []
        rng = np.random.default_rng(SEMILLA)
        cv = StratifiedGroupKFold(PLIEGUES, shuffle=True, random_state=SEMILLA)
        for k, (aj, val) in enumerate(cv.split(d["X_mixta"], clase, d["grupos"]), 1):
            t0 = time.perf_counter()
            m = ConHuellasCensurado(RegresionAFT(semilla=SEMILLA), n_dens, N_BITS)
            m.fit(d["X_mixta"][aj], d["inferior"][aj], d["superior"][aj])
            Xv = m.huellas_.transform(d["X_mixta"][val])                       # (n, 227 + k)
            columnas_huella = m.huellas_.columnas_                              # posiciones dentro de las huellas
            global_ = np.r_[np.arange(n_dens), n_dens + np.asarray(columnas_huella)]
            assert Xv.shape[1] == len(global_)
            contrib = m.modelo.booster_.predict(xgb.DMatrix(Xv.astype(float)), pred_contribs=True)
            suma_shap[global_] += np.abs(contrib[:, :-1]).mean(axis=0)
            en_pliegue[global_] += 1
            if k == 1:
                margen = m.modelo.booster_.predict(xgb.DMatrix(Xv[:200].astype(float)), output_margin=True)
                control_adit.append(float(np.abs(contrib[:200].sum(axis=1) - margen).max()))
                ex = shap.TreeExplainer(m.modelo.booster_).shap_values(Xv[:200].astype(float))
                control_exp.append(float(np.abs(ex - contrib[:200, :-1]).max()))
            predecir = lambda X, mm=m: mm.modelo.predict(X)                      # noqa: E731
            suma_perm[global_] += permutacion(predecir, Xv.astype(float), d["inferior"][val], d["superior"][val], rng)
            print(f"  pliegue {k}: {time.perf_counter() - t0:.0f} s", flush=True)
        imp_shap, imp_perm = suma_shap / PLIEGUES, suma_perm / PLIEGUES
        nombres = np.array(list(nombres_todos))
        top_s = np.argsort(-imp_shap)[:UNION_TOP]
        top_p = np.argsort(-imp_perm)[:UNION_TOP]
        union = np.union1d(top_s, top_p)
        rho, _ = spearmanr(imp_shap[union], imp_perm[union])
        t15_s, t15_p = set(np.argsort(-imp_shap)[:TOP_ACUERDO]), set(np.argsort(-imp_perm)[:TOP_ACUERDO])
        t30_s, t30_p = np.argsort(-imp_shap)[:TOP_AFIRMAR], np.argsort(-imp_perm)[:TOP_AFIRMAR]
        afirmadas = [j for j in t30_s if j in set(t30_p)]
        solo_uno = [j for j in np.r_[t30_s, t30_p] if j not in afirmadas]
        rango_s = (-imp_shap).argsort().argsort() + 1
        rango_p = (-imp_perm).argsort().argsort() + 1
        # nombrar los fragmentos de las columnas de huella que se mencionan
        ids_mencionados = {int(nombres[j].split(":")[1]) for j in set(afirmadas) | set(solo_uno)
                           if nombres[j].startswith("id:")}
        smiles_unicos = np.unique(d["smiles"])
        frags = fragmentos(smiles_unicos, ids_mencionados)
        equiv = {int(i): e for i, e in zip(d["ids"], d["equivalentes"], strict=True)}
        # verificación del identificador con otra API de RDKit, en 20 moléculas al azar
        discrepancias = 0
        for s in rng.choice(smiles_unicos, 20, replace=False):
            mol = Chem.MolFromSmiles(s)
            a = set(rdFingerprintGenerator.GetMorganGenerator(radius=2).GetSparseCountFingerprint(mol).GetNonzeroElements())
            b = set(rdMolDescriptors.GetMorganFingerprint(mol, 2).GetNonzeroElements())
            discrepancias += int(a != b)

        def fila(j):
            nombre = str(nombres[j])
            out = {"columna": nombre, "shap": round(float(imp_shap[j]), 4),
                   "perdida_de_concordancia": round(float(imp_perm[j]), 5),
                   "rango_shap": int(rango_s[j]), "rango_permutacion": int(rango_p[j]),
                   "en_pliegues": int(en_pliegue[j])}
            if nombre.startswith("id:"):
                i = int(nombre.split(":")[1])
                out.update({"tipo": "subestructura", **frags.get(i, {"fragmento": None}),
                            "subestructuras_equivalentes": len(equiv[i])})
            else:
                out["tipo"] = "diana" if nombre.startswith("diana:") else "descriptor"
            return out

        resultado = {
            "control_aditividad_max": max(control_adit), "control_contra_shap_explainer_max": max(control_exp),
            "control_tratamiento_pasa": bool(max(control_adit) < TOLERANCIA and max(control_exp) < TOLERANCIA),
            "identificadores_con_otra_api_discrepancias_de_20": discrepancias,
            "spearman_union_top100": round(float(rho), 4), "compartidas_top15": len(t15_s & t15_p),
            "concuerdan": bool(rho >= RHO_MINIMO and len(t15_s & t15_p) >= COMPARTIDAS_MINIMO),
            "afirmadas_top30_de_los_dos": [fila(j) for j in afirmadas],
            "solo_un_metodo_no_se_afirman": [fila(j) for j in dict.fromkeys(solo_uno)][:20],
            "subestructuras_entre_las_afirmadas": int(sum(nombres[j].startswith("id:") for j in afirmadas)),
            "tpsa_y_hbd": {n: {"rango_shap": int(rango_s[nombres_todos[n]]), "rango_permutacion": int(rango_p[nombres_todos[n]])}
                           for n in ("TPSA", "NumHDonors")},
            "fraccion_shap_en_huellas": round(float(imp_shap[n_dens:].sum() / imp_shap.sum()), 4),
            # El tamaño del punto ciego de dividir entre PLIEGUES siempre: una columna que no está en el
            # vocabulario de un pliegue cuenta 0 en él, así que lo específico (lo que vive en pocos
            # pliegues) no puede llegar arriba. Sin este conteo el lector no separa la química de la regla.
            "columnas_con_menos_de_todos_los_pliegues": int((en_pliegue < PLIEGUES).sum()),
            "huellas_con_menos_de_todos_los_pliegues": int((en_pliegue[n_dens:] < PLIEGUES).sum()),
            "columnas_totales": int(n_total),
            "huellas_totales": int(n_total - n_dens)}
        pd.DataFrame({"columna": nombres, "shap": imp_shap, "perdida_de_concordancia": imp_perm,
                      "rango_shap": rango_s, "rango_permutacion": rango_p,
                      "en_pliegues": en_pliegue.astype(int)}).sort_values("rango_shap").head(300).to_csv(
            c.carpeta / "importancias_top300.csv", index=False)
        c.metricas(resultado)
        for kk, v in resultado.items():
            if kk in ("afirmadas_top30_de_los_dos", "solo_un_metodo_no_se_afirman"):
                print(f"{kk}:")
                for f in v:
                    print("   ", f)
            else:
                print(f"{kk}: {v}")


if __name__ == "__main__":
    main()
