"""De las mediciones del archivo de actividad a una fila por par compuesto-diana.

El archivo de actividad trae **mediciones**: 202,647 filas, varias por la misma
combinación de compuesto y diana. El modelo de la fase 2 predice sobre el
**par**, así que aquí se agrupa. Es el equivalente, para la fase 2, de lo que
`features/molecular.py` hace con los descriptores de la fase 1.

Lo que distingue este módulo de una agregación cualquiera es que **no guarda una
sola etiqueta**. Guarda cuatro columnas objetivo, y la binaria se **deriva** de
las otras:

| Columna | Qué es |
|:--|:--|
| `pActividad` | la potencia como número, 6 − log10 µM. `NaN` si el par solo tiene cotas |
| `limite_inferior`, `limite_superior` | el intervalo donde cae la potencia, con ±∞ cuando no hay cota |
| `activo_10um`, `activo_1um` | la etiqueta binaria, **derivada** del intervalo |

El motivo es una lección de la fase 1: el Avance 2 seleccionó sus 171 columnas
sobre la matriz transformada con Yeo-Johnson y congeló ese artefacto, así que
cambiar la transformación obliga a repetir la selección y a reejecutar el
notebook. La versión de fase 2 de esa trampa sería guardar solo `activo_10um`:
adoptar después la regresión de la decisión 2.9 obligaría a reconstruir todo. Con
el intervalo guardado, la clasificación, la regresión sobre mediciones exactas y
la regresión censurada leen el mismo archivo, y **el umbral pasa a ser una
decisión de lectura**.

## El intervalo reproduce la regla del diccionario

En escala de potencia, una medición censurada es una cota:

- `> L µM` quiere decir que el ensayo llegó a L sin ver efecto, así que la
  potencia real es **menor** que 6 − log10 L: cota superior.
- `< L µM` es lo contrario: cota inferior.

Con eso, «activo con umbral T» es `limite_inferior ≥ 6 − log10 T`, e «inactivo»
es `limite_superior ≤ 6 − log10 T`. Eso **es** la regla de la sección 7 del
diccionario de la patrocinadora —un `>` sirve de negativo solo si su límite
llega al umbral— sin programarla aparte: un `> 1 µM` da cota superior 6, que no
alcanza para declarar inactivo con T = 10 µM (que pide ≤ 5) y sí con T = 1 µM.

## Cómo se agrega un par con varias mediciones

Las exactas manda sobre las cotas, porque un número es más informativo que un
límite: si el par tiene alguna medición exacta se usa la **mediana** de ellas y
las censuradas se ignoran. Si solo tiene cotas, se intersectan. Y si las cotas se
contradicen —un `<` que exige más potencia que la que un `>` permite— el par
queda marcado en `conflicto`, que es el mismo concepto que la propuesta de
variable objetivo define sobre etiquetas, visto sobre el intervalo.

`conflicto` no se filtra aquí: se marca. Quitarlo o conservarlo es decisión del
modelado, y la propuesta vigente lo quita.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..features.molecular import a_mol
from .splits import SIN_ANDAMIO, andamio_murcko, esqueleto_conectividad

# Las cinco categorías que la patrocinadora ratificó el 15 de octubre de 2026
# (decisión 2.1). Las demás salen del alcance de la fase 2.
CINCO_CATEGORIAS = ("Alzheimer", "Parkinson", "Neuroinflamación", "Depresión",
                    "Estrés oxidativo")

# A µM. Las másicas quedan fuera: sin peso molecular no hay conversión a molar.
A_MICROMOLAR = {"nM": 1e-3, "uM": 1.0, "um": 1.0, "mM": 1e3, "M": 1e6,
                "10^3nM": 1.0, "10^2 uM": 1e2, "10^6uM": 1e6, "umol/L": 1.0}

EXACTA = ("=", "~")
COTA_INFERIOR_DE_POTENCIA = ("<", "<=")      # `< L µM` ⇒ potencia > 6 − log10 L
COTA_SUPERIOR_DE_POTENCIA = (">", ">=", ">>")  # `> L µM` ⇒ potencia < 6 − log10 L

# El pChEMBL observado en el archivo va de 2.35 a 12.00, y ChEMBL no lo calcula
# para valores implausibles: ninguna de las filas que caen fuera de este rango
# trae pChEMBL. Sirve de recorte declarado en lugar de un percentil a mano.
RANGO_POTENCIA = (2.0, 12.0)

ESTRATOS = ("solo_chembl", "solo_npass", "solo_cmaup", "mixto")


def a_potencia(valor: pd.Series, unidad: pd.Series) -> pd.Series:
    """pActividad = 6 − log10(µM). NaN si la unidad no se puede convertir."""
    micromolar = (pd.to_numeric(valor, errors="coerce")
                  * unidad.fillna("").map(A_MICROMOLAR))
    micromolar = micromolar.where(micromolar > 0)
    return 6 - np.log10(micromolar)


def _estrato(fuentes: pd.Series) -> str:
    """Procedencia de la evidencia del par, en estratos disjuntos.

    No se usa `source` directamente porque **la fuente no es un atributo del
    par**: 827 de los 828 pares de CMAUP comparten par con otra fuente, así que
    «activos de CMAUP» describiría un grupo que casi no existe por su cuenta.
    """
    unicas = set(fuentes)
    if len(unicas) > 1:
        return "mixto"
    return f"solo_{unicas.pop()}"


def tabla_de_pares(actividad: pd.DataFrame,
                   categorias: tuple[str, ...] = CINCO_CATEGORIAS,
                   recorte: tuple[float, float] = RANGO_POTENCIA,
                   ) -> pd.DataFrame:
    """Una fila por par esqueleto × gen, con el intervalo de potencia.

    `actividad` es el archivo de la patrocinadora tal como se lee del CSV. Se
    queda con las filas que tienen categoría en `categorias`, gen, estructura
    parseable y unidad convertible, y descarta los inactivos declarados por
    texto: su `> 10 µM` lo asignó el equipo que armó el archivo y no el ensayo
    original (ver la propuesta de variable objetivo).
    """
    df = actividad
    df = df[df["diana_categoria"].isin(categorias)]
    df = df[df["target_gene"].notna()]
    df = df[df["evidence_kind"].ne("inactivo_por_texto")]

    potencia = a_potencia(df["activity_value_used"], df["activity_units_used"])
    df = df.assign(potencia=potencia)
    df = df[df["potencia"].notna()]

    # Estructura: una sola pasada por SMILES distinto, que es lo caro.
    estructuras = {}
    for smiles in df["smiles_raw"].dropna().unique():
        mol = a_mol(smiles)
        if mol is None:
            continue
        try:
            estructuras[smiles] = (esqueleto_conectividad(mol),
                                   andamio_murcko(mol))
        except Exception:
            continue
    df = df.assign(
        esqueleto=df["smiles_raw"].map(lambda s: estructuras.get(s, (None,))[0]),
        andamio=df["smiles_raw"].map(
            lambda s: estructuras[s][1] if s in estructuras else None),
    )
    df = df[df["esqueleto"].notna()]

    relacion = df["activity_relation_used"].fillna("")
    es_exacta = relacion.isin(EXACTA)
    dentro = df["potencia"].between(*recorte)
    df = df.assign(
        exacta=np.where(es_exacta & dentro, df["potencia"], np.nan),
        # Una cota fuera del rango plausible tampoco es creíble como cota.
        cota_inf=np.where(relacion.isin(COTA_INFERIOR_DE_POTENCIA) & dentro,
                          df["potencia"], -np.inf),
        cota_sup=np.where(relacion.isin(COTA_SUPERIOR_DE_POTENCIA) & dentro,
                          df["potencia"], np.inf),
    )

    pares = df.groupby(["esqueleto", "target_gene"], sort=False).agg(
        pActividad=("exacta", "median"),
        n_exactas=("exacta", "count"),
        n_mediciones=("potencia", "size"),
        cota_inf=("cota_inf", "max"),
        cota_sup=("cota_sup", "min"),
        rango_exactas=("exacta", lambda s: s.max() - s.min()),
        diana_categoria=("diana_categoria", "first"),
        andamio=("andamio", "first"),
        smiles=("smiles_raw", lambda s: s.mode().iat[0]),
        estrato=("source", _estrato),
        n_referencias=("reference_id", "nunique"),
        n_ensayos=("assay_chembl_id", "nunique"),
    ).reset_index()

    # El intervalo: una exacta lo colapsa a un punto; si solo hay cotas, quedan
    # las cotas.
    tiene_exacta = pares["n_exactas"] > 0
    pares["limite_inferior"] = np.where(tiene_exacta, pares["pActividad"],
                                        pares["cota_inf"])
    pares["limite_superior"] = np.where(tiene_exacta, pares["pActividad"],
                                        pares["cota_sup"])
    # Conflicto es que la evidencia no se pueda satisfacer a la vez: con
    # mediciones exactas, que su mediana caiga fuera de lo que permiten las
    # cotas; sin ellas, que las cotas se cruzen. No se marca por la dispersión
    # entre exactas, que es ruido de medición y la mediana absorbe —esa queda
    # descrita en `rango_exactas`.
    pares["conflicto"] = np.where(
        tiene_exacta,
        ~pares["pActividad"].between(pares["cota_inf"], pares["cota_sup"]),
        pares["cota_inf"] > pares["cota_sup"])
    pares = pares.drop(columns=["cota_inf", "cota_sup"])

    for umbral_um, nombre in ((10.0, "activo_10um"), (1.0, "activo_1um")):
        pares[nombre] = etiqueta_binaria(pares, umbral_um)
    return pares


def etiqueta_binaria(pares: pd.DataFrame, umbral_um: float = 10.0) -> pd.Series:
    """La etiqueta derivada del intervalo, para un umbral en µM.

    Activo si todo el intervalo llega al umbral, inactivo si no lo alcanza, y
    `NA` si el intervalo lo contiene: ahí la evidencia no decide. Devuelve
    `boolean` de pandas, que admite nulos, y no `bool`.

    **El empate se resuelve a favor de activo**, y no es un detalle de estilo:
    una medición exacta justo en el umbral —IC50 de 10 µM con umbral de 10 µM—
    es activa por la convención de «concentración igual o menor», mientras que
    un censurado `> 10 µM` con el mismo umbral es inactivo por la regla del
    diccionario. Los dos tienen la misma relación numérica con el corte y
    significan cosas opuestas; lo que los distingue es que el censurado tiene
    `limite_inferior = -∞`, así que nunca entra por la rama de activo.
    """
    corte = 6 - np.log10(umbral_um)
    activo = pares["limite_inferior"] >= corte
    inactivo = (pares["limite_superior"] <= corte) & ~activo
    etiqueta = pd.Series(pd.NA, index=pares.index, dtype="boolean")
    etiqueta[activo] = True
    etiqueta[inactivo] = False
    return etiqueta


def grupos_de_pares(pares: pd.DataFrame) -> np.ndarray:
    """Grupos para la partición y la validación cruzada de la fase 2.

    Delega en `grupos_cv`, que une andamio y esqueleto salvo en los acíclicos.
    Se expone aparte porque la tabla de pares ya trae las dos columnas con el
    nombre que esa función espera, y así la fase 2 no reimplementa el criterio
    de la fase 1.
    """
    from .splits import grupos_cv

    return grupos_cv(pares.assign(
        andamio=pares["andamio"].fillna(SIN_ANDAMIO)), "andamio", "esqueleto")
