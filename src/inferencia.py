"""Usar los dos modelos finales con SMILES nuevos, sin los datos de entrenamiento.

La patrocinadora no recibe un servicio sino un cuaderno (`notebooks/06_Uso_de_los_modelos.ipynb`, decisión
del 3 de noviembre). Este módulo es lo que ese cuaderno llama. **No depende de `data/processed/`**, que no se
versiona: todo lo que necesita está en `models/finales/` (los dos modelos, la lista de columnas, las dianas y
las huellas de los compuestos de entrenamiento para decir qué tan cerca queda cada consulta de lo ya visto).

Los artefactos los escribe `scripts/entrenar_finales.py`. Se entrenan con las **filas de ajuste** (la decisión
del 4 de noviembre): la prueba reservada no entra en ninguno.

| fase | modelo | entrada | salida |
|:--|:--|:--|:--|
| 1 | `svm_rbf` calibrado | 151 descriptores RDKit | probabilidad de cruzar la barrera (BBB+) |
| 2 | `aft` censurado | 201 descriptores y la diana (26) | pActividad predicha por diana |

**Lo que este módulo no hace**, a propósito: no decide un corte. La probabilidad de la fase 1 se entrega tal
cual: cortarla en 0.5 es un punto fijo que, bajo un cambio de distribución, cambia de sesgo (decisión 1.2,
E15), y la fase 2 predice potencia, no «activo/inactivo».
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")

RAIZ = Path(__file__).resolve().parents[1]
CARPETA = RAIZ / "models" / "finales"
UMBRAL_EXTRAPOLACION = 0.4     # similitud al vecino más cercano por debajo de la cual se avisa (heurística, E14)


@dataclass
class Modelos:
    fase1: object
    fase2: object
    meta: dict
    huellas_fase1: np.ndarray        # bits empaquetados de los compuestos de ajuste
    huellas_fase2: np.ndarray

    @property
    def columnas_fase1(self) -> list[str]:
        return self.meta["columnas_fase1"]

    @property
    def columnas_fase2(self) -> list[str]:
        return self.meta["columnas_fase2"]

    @property
    def dianas(self) -> list[str]:
        return self.meta["dianas"]


def faltan_artefactos(carpeta: Path = CARPETA) -> list[str]:
    nombres = ("meta.json", "fase1_svm_rbf.joblib", "fase2_aft.json", "huellas_fase1.npz", "huellas_fase2.npz")
    return [n for n in nombres if not (carpeta / n).exists() or (carpeta / n).stat().st_size < 200]


def cargar(carpeta: Path = CARPETA) -> Modelos:
    """Lee los artefactos. Falla con un mensaje claro si no están o si son punteros de Git LFS sin bajar."""
    import joblib
    import xgboost as xgb

    from src.models.aft import RegresionAFT

    faltan = faltan_artefactos(carpeta)
    if faltan:
        raise FileNotFoundError(
            f"faltan o no se bajaron (¿`git lfs pull`?) estos archivos de {carpeta}: {faltan}. "
            "Se regeneran con `python scripts/entrenar_finales.py`.")
    meta = json.loads((carpeta / "meta.json").read_text(encoding="utf-8"))
    fase1 = joblib.load(carpeta / "fase1_svm_rbf.joblib")
    booster = xgb.Booster()
    booster.load_model(str(carpeta / "fase2_aft.json"))
    fase2 = RegresionAFT(**meta["fase2_parametros"])
    fase2.booster_ = booster
    fase2.n_features_in_ = len(meta["columnas_fase2"]) + len(meta["dianas"])
    return Modelos(fase1=fase1, fase2=fase2, meta=meta,
                   huellas_fase1=np.load(carpeta / "huellas_fase1.npz")["bits"],
                   huellas_fase2=np.load(carpeta / "huellas_fase2.npz")["bits"])


def a_mol(smiles) -> Chem.Mol | None:
    if not isinstance(smiles, str) or not smiles.strip():
        return None
    try:
        return Chem.MolFromSmiles(smiles.strip())
    except Exception:
        return None


# Dos de las 151 columnas de la fase 1 no salen de RDKit: se derivaron en el Avance 2 (`scripts/experimento_derivadas.py`).
DERIVADAS = {
    "regla_2p": lambda d: float((d["TPSA"] < 67) and (d["NumHDonors"] <= 1)),      # la regla de dos parámetros
    "tpsa_por_mw": lambda d: d["TPSA"] / d["MolWt"],                               # polaridad por unidad de tamaño
}


def descriptores(smiles: Sequence[str], columnas: Sequence[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Los descriptores RDKit pedidos, una fila por SMILES, y por qué no se pudo calcular cada uno que falla.

    Es el mismo cálculo con el que se construyeron las matrices de entrenamiento
    (`Descriptors.CalcMolDescriptors` sobre `Chem.MolFromSmiles`); `tests/test_inferencia.py` comprueba que
    reproduce las filas guardadas. Una fila con algún valor no finito o fuera del rango de `float32` queda en
    NaN y con su motivo: los modelos no deben recibirla.
    """
    filas, motivos = [], []
    maximo = float(np.finfo(np.float32).max)
    for s in smiles:
        mol = a_mol(s)
        if mol is None:
            filas.append({c: np.nan for c in columnas})
            motivos.append("SMILES ilegible")
            continue
        try:
            d = Descriptors.CalcMolDescriptors(mol)
            fila = {c: float(DERIVADAS[c](d) if c in DERIVADAS else d[c]) for c in columnas}
        except Exception as e:                                   # un descriptor puede fallar en moléculas raras
            filas.append({c: np.nan for c in columnas})
            motivos.append(f"descriptores no calculables ({type(e).__name__})")
            continue
        v = np.array(list(fila.values()), dtype=float)
        if not np.isfinite(v).all() or (np.abs(v) > maximo).any():
            filas.append({c: np.nan for c in columnas})
            motivos.append("descriptor no finito o fuera de float32")
        else:
            filas.append(fila)
            motivos.append("")
    return pd.DataFrame(filas, columns=list(columnas)), pd.Series(motivos, name="motivo", dtype=object)


def huellas_empaquetadas(smiles: Sequence[str], radio: int = 2, n_bits: int = 2048) -> np.ndarray:
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radio, fpSize=n_bits)
    salida = []
    for s in smiles:
        mol = a_mol(s)
        if mol is None:
            salida.append(np.zeros(n_bits // 8, dtype=np.uint8))
            continue
        fp = gen.GetFingerprint(mol)
        arr = np.zeros((n_bits,), dtype=np.uint8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        salida.append(np.packbits(arr))
    return np.vstack(salida)


def similitud_al_vecino(consulta: np.ndarray, entrenamiento: np.ndarray, bloque: int = 4096) -> np.ndarray:
    """Mayor Tanimoto de cada consulta con los compuestos de entrenamiento (bits empaquetados)."""
    q = np.unpackbits(consulta, axis=1).astype(np.float32)
    cq = q.sum(axis=1)
    mejor = np.zeros(len(q), dtype=np.float32)
    for i in range(0, len(entrenamiento), bloque):
        e = np.unpackbits(entrenamiento[i:i + bloque], axis=1).astype(np.float32)
        inter = q @ e.T
        union = cq[:, None] + e.sum(axis=1)[None, :] - inter
        with np.errstate(divide="ignore", invalid="ignore"):
            sim = np.where(union > 0, inter / union, 0.0)
        mejor = np.maximum(mejor, sim.max(axis=1))
    return mejor


def matriz_fase2(desc: pd.DataFrame, dianas: Sequence[str]) -> np.ndarray:
    """Una fila por (compuesto, diana): los descriptores y la diana en 0/1, en el orden del entrenamiento."""
    n, k = len(desc), len(dianas)
    X = np.repeat(desc.to_numpy(np.float32), k, axis=0)
    uno_hot = np.tile(np.eye(k, dtype=np.float32), (n, 1))
    return np.hstack([X, uno_hot])


def predecir(smiles: Sequence[str], modelos: Modelos | None = None) -> pd.DataFrame:
    """Una fila por SMILES: probabilidad BBB+, potencia predicha por diana y qué tan cerca queda de lo visto.

    Columnas: `p_bbb_mas`; `pActividad_<diana>` para cada diana; `mejor_diana` y `pActividad_max`;
    `similitud_fase1` y `similitud_fase2` (Tanimoto al compuesto de ajuste más cercano, Morgan radio 2) y
    `aviso_extrapolacion` si alguna queda por debajo de `UMBRAL_EXTRAPOLACION`. Un SMILES que no se puede usar
    sale con NaN y su motivo en `motivo`.
    """
    m = modelos or cargar()
    smiles = list(smiles)
    d1, motivo1 = descriptores(smiles, m.columnas_fase1)
    d2, motivo2 = descriptores(smiles, m.columnas_fase2)
    ok = (motivo1 == "") & (motivo2 == "")
    salida = pd.DataFrame({"smiles": smiles})
    salida["motivo"] = np.where(motivo1 != "", motivo1, motivo2)
    salida["p_bbb_mas"] = np.nan
    for d in m.dianas:
        salida[f"pActividad_{d}"] = np.nan
    idx = np.flatnonzero(ok.to_numpy())
    if len(idx):
        salida.loc[idx, "p_bbb_mas"] = m.fase1.predict_proba(d1.iloc[idx].to_numpy(np.float32))[:, 1]
        pred = m.fase2.predict(matriz_fase2(d2.iloc[idx], m.dianas)).reshape(len(idx), len(m.dianas))
        for j, d in enumerate(m.dianas):
            salida.loc[idx, f"pActividad_{d}"] = pred[:, j]
    cols = [f"pActividad_{d}" for d in m.dianas]
    valores = salida[cols].to_numpy(float)
    con = ~np.isnan(valores).all(axis=1)
    mejor = np.full(len(salida), None, dtype=object)
    if con.any():
        mejor[con] = np.array(m.dianas, dtype=object)[np.nanargmax(valores[con], axis=1)]
    salida["mejor_diana"] = mejor
    salida["pActividad_max"] = np.where(con, np.nanmax(np.where(np.isnan(valores), -np.inf, valores), axis=1), np.nan)
    h = huellas_empaquetadas(smiles)
    salida["similitud_fase1"] = np.where(ok, similitud_al_vecino(h, m.huellas_fase1), np.nan)
    salida["similitud_fase2"] = np.where(ok, similitud_al_vecino(h, m.huellas_fase2), np.nan)
    lejos = (salida[["similitud_fase1", "similitud_fase2"]] < UMBRAL_EXTRAPOLACION).any(axis=1) & ok
    salida["aviso_extrapolacion"] = lejos
    return salida
