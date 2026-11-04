"""Similitud de Tanimoto entre moléculas y los grupos que se forman con ella.

Sirve para las dos cosas que la escalera de agrupación necesita (corrida
`2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`): **agrupar por similitud** —las
componentes conexas del grafo de pares con similitud ≥ umbral, de modo que ningún compuesto de un
grupo se parezca más que el umbral a uno de otro— y **medir qué tan parecido es lo que se evalúa a
lo que se entrena**.

Hay dos versiones porque la escala lo pide. La **densa** guarda la matriz completa y cabe en la
fase 1 (6,306 moléculas). La **dispersa** guarda solo los pares por encima de un umbral mínimo y
cabe en la fase 2 (unas 59,800 moléculas únicas, donde la densa pesaría más de 14 GB). Ambas dan
los mismos grupos en el mismo umbral; `tests/test_similitud.py` lo comprueba.

La huella es la del resto del proyecto: Morgan de radio 2 (ECFP4) y 2048 bits, con
`rdFingerprintGenerator`, no con la función deprecada.
"""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import rdFingerprintGenerator
from scipy import sparse
from scipy.sparse.csgraph import connected_components

RDLogger.DisableLog("rdApp.*")


def huellas(smiles: Sequence[str], radio: int = 2, n_bits: int = 2048) -> list:
    """Huellas Morgan de cada SMILES; falla con el índice si alguno no se puede leer."""
    gen = rdFingerprintGenerator.GetMorganGenerator(radius=radio, fpSize=n_bits)
    salida = []
    for i, s in enumerate(smiles):
        mol = Chem.MolFromSmiles(s)
        if mol is None:
            raise ValueError(f"SMILES ilegible en la posición {i}: {s!r}")
        salida.append(gen.GetFingerprint(mol))
    return salida


def matriz_densa(fps: list) -> np.ndarray:
    """Similitud de Tanimoto entre todos los pares, con la diagonal en 0 (float32)."""
    n = len(fps)
    S = np.zeros((n, n), dtype=np.float32)
    for i in range(n):
        S[i] = DataStructs.BulkTanimotoSimilarity(fps[i], fps)
    np.fill_diagonal(S, 0.0)
    return S


def matriz_dispersa(fps: list, umbral_minimo: float) -> sparse.csr_matrix:
    """Solo los pares con similitud ≥ `umbral_minimo`, simétrica y con la diagonal vacía.

    Un grupo a un umbral mayor se obtiene de esta misma matriz, pero **no** sirve para medir
    la similitud al vecino más cercano por debajo de `umbral_minimo`: ahí no guarda nada.
    """
    n = len(fps)
    filas, cols, vals = [], [], []
    for i in range(n - 1):
        s = np.asarray(DataStructs.BulkTanimotoSimilarity(fps[i], fps[i + 1:]), dtype=np.float32)
        j = np.flatnonzero(s >= umbral_minimo)
        if j.size:
            filas.append(np.full(j.size, i, dtype=np.int64))
            cols.append(j + i + 1)
            vals.append(s[j])
    if not filas:
        return sparse.csr_matrix((n, n), dtype=np.float32)
    f, c, v = np.concatenate(filas), np.concatenate(cols), np.concatenate(vals)
    M = sparse.coo_matrix((v, (f, c)), shape=(n, n), dtype=np.float32)
    return (M + M.T).tocsr()


def grupos_por_similitud(S, umbral: float) -> np.ndarray:
    """Etiqueta de componente conexa del grafo de pares con similitud ≥ `umbral`."""
    if sparse.issparse(S):
        A = S.copy()
        A.data = (A.data >= umbral).astype(np.int8)
        A.eliminate_zeros()
    else:
        A = sparse.csr_matrix(np.asarray(S) >= umbral)
    return connected_components(A, directed=False)[1]


def similitud_al_vecino(S: np.ndarray, ajuste: np.ndarray, validacion: np.ndarray) -> np.ndarray:
    """Para cada compuesto de validación, su mayor similitud con uno de ajuste (matriz densa)."""
    return S[np.ix_(validacion, ajuste)].max(axis=1)


def similitud_al_vecino_de(fps: list, ajuste: np.ndarray, validacion: np.ndarray) -> np.ndarray:
    """Lo mismo sin matriz: sirve cuando la densa no cabe. Cuesta |validación| × |ajuste|."""
    fps_ajuste = [fps[i] for i in ajuste]
    return np.array([max(DataStructs.BulkTanimotoSimilarity(fps[i], fps_ajuste))
                     for i in validacion])


def bits_como_matriz(fps: list) -> np.ndarray:
    """Las huellas como matriz `float32` de 0 y 1, una fila por molécula, para multiplicar."""
    A = np.zeros((len(fps), fps[0].GetNumBits()), dtype=np.float32)
    fila = np.zeros(A.shape[1], dtype=np.uint8)
    for i, fp in enumerate(fps):
        DataStructs.ConvertToNumpyArray(fp, fila)
        A[i] = fila
    return A


def similitud_al_vecino_matricial(A: np.ndarray, ajuste: np.ndarray, validacion: np.ndarray,
                                  bloque: int = 256) -> np.ndarray:
    """La misma cifra que `similitud_al_vecino_de`, con un producto de matrices por bloques.

    Tanimoto = |a ∧ b| / (|a| + |b| − |a ∧ b|), y el numerador de todos los pares de un bloque es un
    producto de matrices. Es exacto y varios órdenes de magnitud más rápido cuando el ajuste tiene
    decenas de miles de moléculas: `BulkTanimotoSimilarity` sobre una lista de 36,000 huellas, repetido
    por cada compuesto de validación, tardó más de 30 minutos en la fase 2 sin terminar un peldaño.
    """
    cuenta = A.sum(axis=1)
    A_ajuste, cuenta_ajuste = A[ajuste], cuenta[ajuste]
    salida = np.empty(len(validacion), dtype=np.float32)
    for i in range(0, len(validacion), bloque):
        v = validacion[i:i + bloque]
        inter = A[v] @ A_ajuste.T
        union = cuenta[v][:, None] + cuenta_ajuste[None, :] - inter
        with np.errstate(divide="ignore", invalid="ignore"):
            sim = np.where(union > 0, inter / union, 0.0)
        salida[i:i + bloque] = sim.max(axis=1)
    return salida


def resumen_grupos(grupos: np.ndarray) -> dict:
    """Número de grupos y fracción de filas del mayor: la partición en 5 pliegues falla si pasa de 20%."""
    _, cuenta = np.unique(grupos, return_counts=True)
    return {"grupos": int(len(cuenta)), "mayor_grupo_pct": round(100 * float(cuenta.max() / len(grupos)), 1)}
