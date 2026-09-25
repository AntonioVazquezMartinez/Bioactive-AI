"""Particiones por andamio molecular, con verificación de fuga.

Por qué importa, medido sobre B3DB en el Avance 1:

- Los andamios grandes tienen **pureza de clase extrema**: el más frecuente
  (410 compuestos, esqueleto esteroideo) es 99.5% BBB+, otro de 59 es 0.0%. Con
  una partición aleatoria, al modelo le basta reconocer el andamio.
- El tamaño efectivo de muestra es de ~4,022 esqueletos de conectividad, no
  7,805 filas. La morfina aparece ocho veces. Una partición aleatoria pondría
  estereoisómeros del mismo compuesto en entrenamiento y prueba.

De ahí que la partición agrupe por andamio de Bemis-Murcko **y** verifique que
ningún esqueleto de conectividad cruce entre particiones.

Ver `docs/referencias/02-datasets-bbb.md` §"Desempeño realista y splits".
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

SIN_ANDAMIO = "<aciclico>"


def andamio_murcko(mol: Chem.Mol, generico: bool = False) -> str:
    """Andamio de Bemis-Murcko como SMILES.

    Los compuestos acíclicos no tienen andamio y devuelven `SIN_ANDAMIO`: en
    B3DB son 311 y hay que decidir explícitamente qué hacer con ellos, no
    dejarlos caer en silencio.
    """
    try:
        esqueleto = MurckoScaffold.GetScaffoldForMol(mol)
        if generico:
            esqueleto = MurckoScaffold.MakeScaffoldGeneric(esqueleto)
        smiles = Chem.MolToSmiles(esqueleto)
        return smiles if smiles else SIN_ANDAMIO
    except Exception:
        return SIN_ANDAMIO


def esqueleto_conectividad(mol: Chem.Mol) -> str:
    """Bloque de conectividad del InChIKey: identifica al compuesto ignorando
    estereoquímica e isótopos. Dos estereoisómeros comparten esqueleto."""
    return Chem.MolToInchiKey(mol)[:14]


def scaffold_split(
    df: pd.DataFrame,
    col_andamio: str = "andamio",
    col_esqueleto: str = "esqueleto",
    fraccion_prueba: float = 0.2,
    fraccion_validacion: float = 0.0,
    semilla: int = 42,
    acíclicos_a: str = "entrenamiento",
) -> pd.Series:
    """Asigna cada fila a entrenamiento, validación o prueba.

    Estrategia: se unen los andamios que comparten esqueleto de conectividad en
    un mismo grupo —para que los estereoisómeros no se separen— y los grupos se
    recorren de mayor a menor asignando primero a **entrenamiento**, que es la
    convención de DeepChem y la semántica correcta: los andamios frecuentes
    alimentan el modelo y los raros quedan para evaluar generalización a
    química nueva.

    Llenar la prueba con los grupos grandes produce un conjunto de evaluación
    dominado por unos pocos quimiotipos —al construirlo así, el benceno solo
    ocupaba el 26% de la prueba y esta tenía 45 andamios contra 2,112 del
    entrenamiento—, lo que hace que el desempeño medido refleje esos andamios y
    no la capacidad real del modelo.

    `acíclicos_a` decide el destino de los compuestos sin andamio. Por defecto
    van a entrenamiento: no comparten estructura de anillo con nada, así que no
    filtran información, pero tampoco evalúan generalización estructural.
    """
    if not 0 < fraccion_prueba < 1:
        raise ValueError("fraccion_prueba debe estar entre 0 y 1")
    if fraccion_validacion < 0 or fraccion_prueba + fraccion_validacion >= 1:
        raise ValueError("las fracciones de prueba y validación suman demasiado")

    # --- unir andamios que comparten esqueleto de conectividad -----------------
    # Un esqueleto puede aparecer con andamios distintos (p. ej. un tautómero
    # que cambia el anillo). Si se separan, hay fuga por estereoisomería.
    padre: dict[str, str] = {}

    def raiz(x: str) -> str:
        while padre.get(x, x) != x:
            x = padre[x]
        return x

    def unir(a: str, b: str) -> None:
        ra, rb = raiz(a), raiz(b)
        if ra != rb:
            padre[ra] = rb

    for a in df[col_andamio].unique():
        padre.setdefault(a, a)
    for esq, sub in df.groupby(col_esqueleto)[col_andamio]:
        andamios = sub.unique()
        for a in andamios[1:]:
            unir(andamios[0], a)

    grupo = df[col_andamio].map(raiz)

    # los acíclicos se tratan aparte: no son un grupo estructural real
    es_aciclico = df[col_andamio] == SIN_ANDAMIO
    grupos_reales = grupo[~es_aciclico]

    tamanos = grupos_reales.value_counts()
    rng = np.random.default_rng(semilla)
    # orden determinista: por tamaño descendente, desempatando al azar
    orden = sorted(tamanos.items(), key=lambda kv: (-kv[1], rng.random()))

    n_elegibles = len(grupos_reales)
    objetivo_train = int(round(n_elegibles * (1 - fraccion_prueba - fraccion_validacion)))
    objetivo_val = int(round(n_elegibles * fraccion_validacion))

    destino: dict[str, str] = {}
    n_train = n_val = 0
    for g, tam in orden:
        # los grupos grandes van a entrenamiento; los raros quedan para evaluar
        if n_train + tam <= objetivo_train:
            destino[g] = "entrenamiento"
            n_train += tam
        elif objetivo_val and n_val + tam <= objetivo_val:
            destino[g] = "validacion"
            n_val += tam
        else:
            destino[g] = "prueba"

    particion = grupo.map(destino).fillna("entrenamiento")
    particion[es_aciclico] = acíclicos_a
    return particion.rename("particion")


def verificar_fuga(df: pd.DataFrame, col_particion: str = "particion",
                   col_andamio: str = "andamio",
                   col_esqueleto: str = "esqueleto") -> dict:
    """Comprueba que ninguna estructura cruce entre particiones.

    Devuelve un informe; `sin_fuga` es True solo si ni un andamio ni un
    esqueleto aparecen en más de una partición. Los acíclicos se excluyen del
    conteo de andamios porque todos comparten el marcador SIN_ANDAMIO.
    """
    reales = df[df[col_andamio] != SIN_ANDAMIO]

    and_cruzados = (reales.groupby(col_andamio)[col_particion].nunique() > 1)
    esq_cruzados = (df.groupby(col_esqueleto)[col_particion].nunique() > 1)

    informe = {
        "andamios_cruzados": int(and_cruzados.sum()),
        "esqueletos_cruzados": int(esq_cruzados.sum()),
        "ejemplos_andamios": list(and_cruzados[and_cruzados].index[:5]),
        "ejemplos_esqueletos": list(esq_cruzados[esq_cruzados].index[:5]),
        "tamanos": df[col_particion].value_counts().to_dict(),
        "balance": df.groupby(col_particion)["y"].mean().round(4).to_dict()
        if "y" in df.columns else {},
    }
    informe["sin_fuga"] = (informe["andamios_cruzados"] == 0
                           and informe["esqueletos_cruzados"] == 0)
    return informe


def umbral_youden(y: np.ndarray, puntuacion: np.ndarray, mayor_es_positivo: bool = True
                  ) -> tuple[float, float]:
    """Umbral óptimo por el estadístico J de Youden, y su AUC.

    Se calcula SOLO sobre entrenamiento. Derivarlo del conjunto completo
    filtraría información de la prueba — y el Avance 1 mostró que el umbral de
    TPSA se mueve de 66.6 a 83.6 Å² según el subconjunto, así que no es un
    detalle menor.
    """
    from sklearn.metrics import roc_auc_score, roc_curve

    s = puntuacion if mayor_es_positivo else -puntuacion
    fpr, tpr, thr = roc_curve(y, s)
    j = tpr - fpr
    umbral = thr[int(np.argmax(j))]
    return (umbral if mayor_es_positivo else -umbral), roc_auc_score(y, s)
