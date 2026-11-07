"""Generación de características moleculares a partir de SMILES.

Tres familias, todas de salida fija:

- **Descriptores 2D de RDKit** (217 en la versión actual): interpretables por
  propiedad, dominados por TPSA y HBD para permeabilidad BBB.
- **Morgan / ECFP4 plegado**: trazable a substructura vía el mapa de bits.
- **Sort & Slice**: alternativa libre de colisiones, que ordena las
  substructuras por frecuencia en el conjunto de entrenamiento y conserva las
  L más frecuentes.

Notas de API, verificadas con RDKit 2026.03.6:

- Se usa `rdFingerprintGenerator`, no `GetMorganFingerprintAsBitVect`, que está
  obsoleto y solo avisa por el logger de C++, fácil de pasar por alto.
- `radius=2` produce **ECFP4**: el número del nombre es el diámetro.
- El plegado a longitud fija introduce colisiones, donde substructuras distintas
  comparten bit. Eso corrompe la atribución por SHAP, de ahí Sort & Slice.

Ver `docs/referencias/01-representaciones-moleculares.md` para la evidencia.
"""

from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors, rdCIPLabeler, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")

# Descriptores que la investigación identificó como los de mayor poder
# discriminante para permeabilidad BBB, en ese orden.
DESCRIPTORES_CLAVE = ["TPSA", "NumHDonors", "MolLogP", "MolWt", "NumHAcceptors"]


def a_mol(smiles: str) -> Chem.Mol | None:
    """SMILES a molécula. Devuelve None si no parsea, sin lanzar excepción."""
    if not isinstance(smiles, str) or not smiles:
        return None
    try:
        return Chem.MolFromSmiles(smiles)
    except Exception:
        return None


def descriptores_rdkit(mols: list[Chem.Mol]) -> pd.DataFrame:
    """Los 217 descriptores 2D de RDKit. Las columnas con valores no finitos se
    reportan pero no se eliminan: esa decisión es del pipeline, no de aquí."""
    filas = [Descriptors.CalcMolDescriptors(m) for m in mols]
    return pd.DataFrame(filas)


_ENLACES_E = (Chem.BondStereo.STEREOE, Chem.BondStereo.STEREOTRANS)
_ENLACES_Z = (Chem.BondStereo.STEREOZ, Chem.BondStereo.STEREOCIS)
CONTEOS_ESTEREO = ("n_R", "n_S", "n_E", "n_Z")


def conteos_estereo(mols: list[Chem.Mol]) -> pd.DataFrame:
    """Cuatro conteos de configuración: centros R, centros S, enlaces E y enlaces Z.

    **Ninguno de los 217 descriptores de RDKit codifica configuración.** Los dos que hay
    —`NumAtomStereoCenters` y `NumUnspecifiedAtomStereoCenters`— cuentan cuántos centros tiene la
    molécula y cuántos no están declarados, nunca cuál de las dos formas es, así que dos
    enantiómeros dan vectores idénticos en los 217. Estas cuatro columnas son el arreglo más
    pequeño que los distingue: un enantiómero da (1, 0) y el otro (0, 1).

    **Son conteos globales, no posicionales, y eso tiene un límite medido.** Dos estereoisómeros
    con los mismos conteos y los centros en otras posiciones siguen dando el mismo vector. En la
    fase 1 las cuatro columnas resuelven **157 de las 183 filas** que los 151 descriptores no
    pueden separar (56 de 69 grupos); **las 26 que quedan son exactamente ese caso**, con los dos
    lados declarando por ejemplo (3 R, 3 S). La versión posicional son las huellas con
    `includeChirality` (la [1.9](../../docs/decisiones.md#d1-9)); esto cubre lo que puede cubrir
    una columna por molécula, y cuánto rinde está en la [1.8](../../docs/decisiones.md#d1-8).

    Las etiquetas R/S salen de `rdCIPLabeler`, que implementa las reglas CIP completas, y **no se
    reutilizan las que `MolFromSmiles` ya deja puestas**: esas son del asignador heredado, que
    resuelve mal los desempates lejanos, y en 104 de las 6,306 moléculas de la fase 1 no coinciden.
    Se etiqueta sobre una copia porque `AssignCIPLabels` sobrescribe esas propiedades, y el
    llamador no tiene por qué recibir las nuestras. Un centro o un enlace sin declarar no cuenta en
    ninguna de las cuatro: no se infiere lo que el registro no dice.
    """
    filas = []
    for m in mols:
        copia = Chem.Mol(m)
        rdCIPLabeler.AssignCIPLabels(copia)
        cip = [a.GetProp("_CIPCode") for a in copia.GetAtoms() if a.HasProp("_CIPCode")]
        enlaces = [b.GetStereo() for b in copia.GetBonds()]
        filas.append({"n_R": cip.count("R"), "n_S": cip.count("S"),
                      "n_E": sum(e in _ENLACES_E for e in enlaces),
                      "n_Z": sum(e in _ENLACES_Z for e in enlaces)})
    return pd.DataFrame(filas, columns=list(CONTEOS_ESTEREO))


def limpiar_descriptores(desc: pd.DataFrame, verbose: bool = True
                        ) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Descarta las columnas de descriptores inservibles para un modelo.

    Cuatro criterios, en orden:

    1. **Constantes**: no aportan información.
    2. **Con NaN**: sklearn no las acepta sin imputar.
    3. **No finitas**: inf o -inf.
    4. **Fuera del rango de float32.** Este es el que muerde en la práctica:
       `Ipc` de RDKit —el índice de contenido de información— alcanza valores
       del orden de 1e41 en moléculas grandes, finitos en float64 pero por
       encima del máximo de float32 (~3.4e38). Random Forest y otros modelos de
       sklearn convierten a float32 internamente y fallan con
       "Input X contains infinity or a value too large for dtype('float32')".
       Es un desbordamiento conocido de ese descriptor.

    Devuelve el DataFrame limpio y un diccionario con lo descartado por motivo,
    para poder reportarlo en vez de perderlo en silencio.
    """
    MAX_F32 = float(np.finfo(np.float32).max)
    num = desc.select_dtypes("number")

    motivos = {
        "constantes": desc.columns[desc.nunique() <= 1].tolist(),
        "con_nan": desc.columns[desc.isna().any()].tolist(),
        "no_finitas": num.columns[~np.isfinite(num).all()].tolist(),
    }
    # se evalúa el rango solo sobre las que sobrevivirían a los criterios previos
    ya = set().union(*motivos.values())
    candidatas = [c for c in num.columns if c not in ya]
    motivos["fuera_de_float32"] = [
        c for c in candidatas if num[c].abs().max() > MAX_F32
    ]

    descartar = sorted(set().union(*motivos.values()))
    limpio = desc.drop(columns=descartar)

    if verbose:
        for motivo, cols in motivos.items():
            if cols:
                muestra = ", ".join(cols[:4]) + ("…" if len(cols) > 4 else "")
                print(f"  descartadas por {motivo}: {len(cols)}  ({muestra})")
        print(f"  descriptores utilizables: {limpio.shape[1]} de {desc.shape[1]}")
    return limpio, motivos


def generador_morgan(radio: int = 2, n_bits: int = 2048):
    """Generador Morgan. `radio=2` es ECFP4."""
    return rdFingerprintGenerator.GetMorganGenerator(radius=radio, fpSize=n_bits)


def morgan_plegado(mols: list[Chem.Mol], radio: int = 2, n_bits: int = 2048,
                   conteos: bool = False) -> np.ndarray:
    """Matriz (n_moléculas, n_bits) de fingerprints Morgan plegados.

    `conteos=True` devuelve conteos en vez de binario. No se encontró un
    benchmark controlado que compare ambos, así que el binario queda por
    convención, no por evidencia.
    """
    gen = generador_morgan(radio, n_bits)
    fn = gen.GetCountFingerprintAsNumPy if conteos else gen.GetFingerprintAsNumPy
    return np.vstack([fn(m) for m in mols]).astype(np.uint8 if not conteos else np.uint16)


def mapa_bit_substructura(mol: Chem.Mol, radio: int = 2, n_bits: int = 2048
                          ) -> dict[int, list[tuple[int, int]]]:
    """Bits activos de una molécula y los entornos atómicos que los activaron.

    Es el mecanismo central de explicabilidad: permite pasar de un bit con peso
    SHAP alto a la substructura concreta que lo produjo.
    """
    gen = generador_morgan(radio, n_bits)
    salida = rdFingerprintGenerator.AdditionalOutput()
    salida.AllocateBitInfoMap()
    gen.GetFingerprint(mol, additionalOutput=salida)
    return {bit: list(envs) for bit, envs in salida.GetBitInfoMap().items()}


def substructura_de_bit(mol: Chem.Mol, bit: int, radio: int = 2, n_bits: int = 2048
                        ) -> str | None:
    """SMILES de la substructura que activó un bit. None si el bit no está activo."""
    info = mapa_bit_substructura(mol, radio, n_bits)
    if bit not in info:
        return None
    idx, r = info[bit][0]
    if r == 0:
        return mol.GetAtomWithIdx(idx).GetSymbol()
    entorno = Chem.FindAtomEnvironmentOfRadiusN(mol, r, idx)
    return Chem.MolToSmiles(Chem.PathToSubmol(mol, entorno))


class SortAndSlice:
    """Fingerprint libre de colisiones por frecuencia de substructura.

    En vez de plegar por hash —lo que hace que substructuras distintas compartan
    bit—, ordena los identificadores de substructura por frecuencia en el
    conjunto de entrenamiento y conserva los `n_bits` más frecuentes. Cada
    columna corresponde entonces a **una** substructura, lo que hace válida la
    atribución.

    El vocabulario se aprende SOLO del entrenamiento: ajustarlo sobre todo el
    conjunto filtraría información de la partición de prueba.

    Referencia: Dablander et al., J. Cheminformatics 16:135 (2024).
    """

    def __init__(self, radio: int = 2, n_bits: int = 2048):
        self.radio = radio
        self.n_bits = n_bits
        self.vocabulario: list[int] = []
        self._indice: dict[int, int] = {}

    def _identificadores(self, mol: Chem.Mol) -> list[int]:
        # generador no plegado: los identificadores son el hash de 32 bits nativo
        gen = rdFingerprintGenerator.GetMorganGenerator(radius=self.radio)
        return list(gen.GetSparseCountFingerprint(mol).GetNonzeroElements().keys())

    def fit(self, mols: list[Chem.Mol]) -> "SortAndSlice":
        frecuencias: Counter[int] = Counter()
        for m in mols:
            frecuencias.update(self._identificadores(m))
        # empates resueltos por identificador para que el orden sea reproducible
        ordenados = sorted(frecuencias.items(), key=lambda kv: (-kv[1], kv[0]))
        self.vocabulario = [ident for ident, _ in ordenados[: self.n_bits]]
        self._indice = {ident: i for i, ident in enumerate(self.vocabulario)}
        return self

    def transform(self, mols: list[Chem.Mol]) -> np.ndarray:
        if not self.vocabulario:
            raise RuntimeError("hay que llamar fit() antes de transform()")
        X = np.zeros((len(mols), len(self.vocabulario)), dtype=np.uint8)
        for i, m in enumerate(mols):
            for ident in self._identificadores(m):
                j = self._indice.get(ident)
                if j is not None:
                    X[i, j] = 1
        return X

    def fit_transform(self, mols: list[Chem.Mol]) -> np.ndarray:
        return self.fit(mols).transform(mols)

    def cobertura(self, mols: list[Chem.Mol]) -> float:
        """Fracción de las substructuras presentes que el vocabulario cubre.

        Útil para elegir `n_bits`: si la cobertura es baja se está descartando
        información estructural real.
        """
        vistas = total = 0
        for m in mols:
            ids = self._identificadores(m)
            total += len(ids)
            vistas += sum(1 for i in ids if i in self._indice)
        return vistas / total if total else 0.0
