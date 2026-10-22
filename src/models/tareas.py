"""Qué se predice, con qué entradas: la tarea como argumento y no como código.

El proyecto tiene dos fases y en las dos están abiertas las preguntas de **qué
es el objetivo** y **qué entra como entrada**: el corte de «activo» es 10 µM
con 1 µM al lado ([2.3](../../docs/decisiones.md#d2-3)), la representación
puede ser descriptores, Morgan o Sort & Slice ([1.3](../../docs/decisiones.md#d1-3)),
y la [2.9](../../docs/decisiones.md#d2-9) propone cambiar la clasificación por
una regresión.

Si cada una de esas decisiones vive dentro del código del baseline, cambiarla
obliga a reescribirlo. Aquí viven como **argumentos**:

```python
t = cargar("actividad", umbral_um=1.0, representacion="descriptores")
res, fdp = evaluar(canalizaciones(), t.X, t.y, t.grupos, estratos=t.estratos)
```

Cambiar el umbral es cambiar un número, y cambiar la entrada es cambiar una
palabra. Es la lección que la fase 1 aprendió al revés: el Avance 2 seleccionó
sus columnas sobre la matriz de Yeo-Johnson, así que cambiar la transformación
obligaba a repetir la selección. Se corrigió filtrando sobre los valores
crudos —valor modal para las casi constantes, Spearman para las redundantes— y
el notebook comprueba que las 151 columnas salen iguales con las tres.

**Cómo se importa.** Con la raíz del repositorio en `sys.path` y no con `src/`:
`from src.models import cargar`. Es la misma convención que exige
`src.data_prep.pares_fase2`, que importa de `src.features`, y la que usan el
notebook 02b y las pruebas. El notebook 02 y los scripts antiguos insertan
`src/`, que es la otra convención del repositorio; mezclarlas rompe los
imports relativos.

**Lo que esta capa no hace**, a propósito: no entrena, no escala y no parte.
Escalar es de la canalización, que lo ajusta dentro del pliegue; partir es de
quien construyó la matriz, y la prueba reservada se queda fuera salvo que se
pida explícitamente con `incluir_prueba=True`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from ..data_prep.splits import SIN_ANDAMIO, grupos_cv

RAIZ = Path(__file__).resolve().parents[2]
PROCESADOS = RAIZ / "data/processed"

TAREAS = ("permeabilidad", "actividad")
ESTRATOS = ("grupo", "origen", "origen_grupo")
ARCHIVO_PATROCINADORA = RAIZ / "data/external/profesora/bbb_permeability_experimental.csv"
ORIGENES = ("natural exacto", "análogo estereoquímico", "sin equivalente natural")
REPRESENTACIONES = ("descriptores", "descriptores_transformados", "morgan",
                    "sortslice", "descriptores+morgan")


@dataclass(frozen=True)
class Tarea:
    """Una tarea lista para evaluar, con lo que hace falta para reportarla."""

    nombre: str
    X: np.ndarray
    y: np.ndarray
    grupos: np.ndarray
    estratos: np.ndarray
    meta: pd.DataFrame
    objetivo: str
    representacion: str

    def __repr__(self) -> str:  # pragma: no cover - solo para inspección
        return (f"Tarea({self.nombre}, {self.X.shape[0]:,}×{self.X.shape[1]:,}, "
                f"objetivo={self.objetivo}, {self.y.mean():.1%} positivos, "
                f"{len(np.unique(self.grupos)):,} grupos)")


def _denso(ruta: Path) -> np.ndarray:
    z = np.load(ruta)
    m = sparse.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    return m.toarray().astype(np.float32)


# La matriz **sin normalizar**, no la transformada. La guardada en
# `bbb_descriptores_filtrados.parquet` ya trae Yeo-Johnson aplicado, y ese
# transformador vio todas las filas de entrenamiento: usarla en validación
# cruzada mete en cada pliegue de evaluación información ajustada con él. El
# escalado tiene que ocurrir dentro de la canalización, que se reajusta por
# pliegue. La transformada queda disponible como `descriptores_transformados`
# justamente para poder medir cuánto infla.
DESCRIPTORES = {
    "descriptores": "bbb_descriptores_filtrados_sin_normalizar.parquet",
    "descriptores_transformados": "bbb_descriptores_filtrados.parquet",
}


def _entradas_permeabilidad(representacion: str, filas: np.ndarray) -> np.ndarray:
    if representacion in DESCRIPTORES:
        d = pd.read_parquet(PROCESADOS / DESCRIPTORES[representacion])
        return d.to_numpy(dtype=np.float32)[filas]
    if representacion == "morgan":
        return _denso(PROCESADOS / "bbb_morgan2048.npz")[filas]
    if representacion == "sortslice":
        return _denso(PROCESADOS / "bbb_sortslice2048.npz")[filas]
    if representacion == "descriptores+morgan":
        d = pd.read_parquet(PROCESADOS / DESCRIPTORES["descriptores"])
        return np.hstack([d.to_numpy(dtype=np.float32),
                          _denso(PROCESADOS / "bbb_morgan2048.npz")])[filas]
    raise ValueError(f"representación {representacion!r}; use una de {REPRESENTACIONES}")


def asignar_origen(exacto: pd.Series, key14: pd.Series) -> np.ndarray:
    """Origen de tres categorías a partir de las dos columnas de COCONUT.

    Es la definición del notebook 01 (§5): **natural exacto** si hay
    coincidencia exacta (`coconut_id_exact_match`), **análogo estereoquímico**
    si solo coincide la llave de conectividad (`coconut_ids_key14_match`), y
    **sin equivalente natural** si ninguna de las dos. La coincidencia exacta
    manda: un compuesto con las dos columnas presentes es natural exacto.
    """
    return np.select([exacto.notna().to_numpy(), key14.notna().to_numpy()],
                     [ORIGENES[0], ORIGENES[1]], default=ORIGENES[2])


def _origen_por_fila(meta: pd.DataFrame) -> np.ndarray:
    """Origen de cada fila de `meta`, cruzando con el archivo de la patrocinadora.

    `bbb_meta.parquet` no guarda las columnas de COCONUT, solo `natural`. La
    llave es el InChIKey (`Inchi` en `meta` es un InChIKey, no un InChI): tiene
    3 repetidos tanto en `meta` como en el archivo, de modo que no cruza 1 a 1.
    Se acepta porque en los tres casos las filas repetidas tienen el mismo
    origen, y eso se comprueba abajo en lugar de suponerse; si el archivo
    cambiara y dejara de cumplirse, falla aquí.
    """
    arch = pd.read_csv(ARCHIVO_PATROCINADORA)
    arch.columns = [c.strip().lstrip("\ufeff") for c in arch.columns]
    arch = arch[arch["bbb_class"].notna()].copy()
    arch["origen"] = asignar_origen(arch["coconut_id_exact_match"],
                                    arch["coconut_ids_key14_match"])
    ambiguas = arch.groupby("inchikey")["origen"].nunique()
    if not (ambiguas == 1).all():
        raise ValueError("InChIKeys repetidos con origen distinto: "
                         f"{ambiguas[ambiguas > 1].index.tolist()}")
    por_llave = arch.drop_duplicates("inchikey").set_index("inchikey")["origen"]
    origen = meta["Inchi"].map(por_llave)
    if origen.isna().any():
        raise ValueError(
            f"{int(origen.isna().sum())} filas de bbb_meta sin origen: su InChIKey "
            "no está en el archivo de la patrocinadora")
    # El origen «natural exacto» tiene que ser exactamente la columna `natural`
    # que ya traía `meta`; si no, el cruce o alguna de las dos definiciones falló.
    if not (origen.eq(ORIGENES[0]).to_numpy() == meta["natural"].to_numpy(dtype=bool)).all():
        raise ValueError("«natural exacto» no coincide con la columna `natural` de bbb_meta")
    return origen.to_numpy()


def _etiquetas_estratos(estratos: str, grupo: np.ndarray, origen: np.ndarray) -> np.ndarray:
    """Etiqueta de estrato por fila; `origen` solo se usa si `estratos` lo pide."""
    if estratos == "grupo":
        return grupo
    if estratos == "origen":
        return origen
    return np.char.add(np.char.add(origen.astype(str), "·"), grupo.astype(str))


def _permeabilidad(representacion: str, incluir_prueba: bool,
                   estratos: str = "grupo") -> Tarea:
    meta = pd.read_parquet(PROCESADOS / "bbb_meta.parquet")
    if estratos != "grupo":
        meta = meta.assign(origen=_origen_por_fila(meta))
    # La prueba se reserva (1.2); el baseline mide sobre entrenamiento y validación.
    filas = np.flatnonzero(meta["particion"].ne("prueba").to_numpy()
                           | incluir_prueba)
    m = meta.iloc[filas].reset_index(drop=True)
    return Tarea(
        nombre="permeabilidad",
        X=_entradas_permeabilidad(representacion, filas),
        y=m["y"].astype(int).to_numpy(),
        # `grupos_cv` y no el andamio a secas: un esqueleto de conectividad
        # puede aparecer con andamios distintos, y separarlos pone
        # estereoisómeros del mismo compuesto a los dos lados del pliegue.
        # Sobre lo que esta función devuelve —entrenamiento y validación, sin
        # la prueba— son 1,048 grupos contra 2,239 por andamio solo, que es lo
        # que mide la §2.1 del notebook 03. Las cifras de 2,373 y 3,629 que
        # este comentario traía son del conjunto completo, con la prueba
        # dentro, y no son las que nadie puede reproducir desde aquí.
        grupos=grupos_cv(m.assign(andamio=m["andamio"].fillna(SIN_ANDAMIO)),
                         "andamio", "esqueleto"),
        # El grupo A–D estratifica, nunca excluye (1.1).
        estratos=_etiquetas_estratos(
            estratos, m["group"].astype(str).to_numpy(),
            m["origen"].to_numpy() if "origen" in m else np.array([])),
        meta=m,
        objetivo="bbb_class (BBB+ = 1)",
        representacion=representacion,
    )


def _actividad(representacion: str, umbral_um: float, incluir_prueba: bool) -> Tarea:
    from ..data_prep.pares_fase2 import etiqueta_binaria

    pares = pd.read_parquet(PROCESADOS / "fase2_pares.parquet")
    desc = pd.read_parquet(PROCESADOS / "fase2_descriptores_limpios.parquet")
    # El umbral es una decisión de lectura, no de construcción: la etiqueta se
    # deriva del intervalo guardado, así que cambiarlo no reconstruye nada (2.10).
    etiqueta = etiqueta_binaria(pares, umbral_um)
    d = pares.assign(objetivo=etiqueta)
    d = d[d["objetivo"].notna()]
    if not incluir_prueba:
        d = d[d["particion"].ne("prueba")]
    d = d.merge(desc, on="smiles", how="inner").reset_index(drop=True)

    columnas = [c for c in desc.columns if c != "smiles"]
    if representacion == "descriptores":
        X = d[columnas].to_numpy(dtype=np.float32)
    elif representacion == "descriptores+diana":
        # La diana importa: sobre las 25 dianas de esta matriz con 50 pares o
        # más, la tasa de activos va de 34.8% en `MAOA` a 98.4% en `IL6`, y sin
        # ella el modelo no sabe contra qué se mide (2.2, y el control del #32).
        X = np.hstack([d[columnas].to_numpy(dtype=np.float32),
                       pd.get_dummies(d["target_gene"]).to_numpy(dtype=np.float32)])
    else:
        raise ValueError(
            f"representación {representacion!r} no disponible para actividad; "
            "use «descriptores» o «descriptores+diana»")

    return Tarea(
        nombre="actividad",
        X=X,
        y=d["objetivo"].astype(int).to_numpy(),
        grupos=d["grupo_cv"].to_numpy(),
        # La procedencia, que es lo que el control de atajo obliga a desglosar.
        estratos=d["estrato"].to_numpy(),
        meta=d[["esqueleto", "target_gene", "estrato", "particion", "diana_categoria"]],
        objetivo=f"activo a {umbral_um:g} µM",
        representacion=representacion,
    )


def cargar(tarea: str = "permeabilidad", *, representacion: str = "descriptores",
           umbral_um: float = 10.0, incluir_prueba: bool = False,
           estratos: str = "grupo") -> Tarea:
    """Arma una tarea. `umbral_um` solo aplica a «actividad».

    `estratos` elige cómo se desglosa el resultado en permeabilidad:

    - `"grupo"` (por omisión): los grupos A–D de B3DB.
    - `"origen"`: natural exacto, análogo estereoquímico o sin equivalente
      natural, según COCONUT (`asignar_origen`).
    - `"origen_grupo"`: las dos etiquetas juntas, p. ej. `"natural exacto·B"`.

    Existe por la [1.6](../../docs/decisiones.md#d1-6) y el #102. Juntar los
    análogos con los compuestos sin equivalente natural diluye la brecha entre
    naturales y el resto (18.9 contra 28.3 puntos, notebook 01 §5), y el grupo A
    tiene 88% de BBB+: cada estrato se lee contra su propia tasa base, no contra
    la global. La columna `origen` solo se añade a `meta` cuando se pide.

    En «actividad» los estratos son de procedencia y no se pueden cambiar:
    cualquier valor distinto de `"grupo"` da error.
    """
    if estratos not in ESTRATOS:
        raise ValueError(f"estratos {estratos!r}; use uno de {ESTRATOS}")
    if tarea == "permeabilidad":
        return _permeabilidad(representacion, incluir_prueba, estratos)
    if tarea == "actividad":
        if estratos != "grupo":
            raise ValueError("en «actividad» los estratos son de procedencia; "
                             f"estratos={estratos!r} no aplica")
        return _actividad(representacion, umbral_um, incluir_prueba)
    raise ValueError(f"tarea {tarea!r}; use una de {TAREAS}")
