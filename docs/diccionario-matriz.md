# Diccionario de la matriz de entrenamiento

Qué columna es cada cosa en lo que produce el [notebook 02](../notebooks/02_Feature_Eng.ipynb). Los diccionarios de la patrocinadora describen **lo que recibimos**; este describe **lo que entra al modelo**, que no es lo mismo: entre uno y otro hay un cálculo de descriptores, una limpieza y dos filtros.

Las cifras salen de los artefactos de `data/processed/`, que el notebook regenera de principio a fin.

## De 217 columnas a 171

| Paso | Quedan | Qué pasó |
|:--|--:|:--|
| RDKit calcula sus descriptores 2D | 217 | uno por molécula, sin elegir |
| `limpiar_descriptores` | **203** | se van 14: 5 constantes, 8 con NaN (los `BCUT2D_*`) y `Ipc` |
| más tres derivadas del dominio | 206 | `regla_2p`, `tpsa_por_mw`, `lipo_neta` |
| umbral de varianza (> 0.01) | 205 | se va `fr_azo` |
| correlación \|r\| > 0.95 | **171** | se van 34 |

`Ipc` es el que muerde: el índice de contenido de información alcanza ~1e41, finito en float64 pero por encima del máximo de float32, y scikit-learn convierte internamente. Un chequeo de `isfinite` no lo detecta.

## Las cinco familias de descriptores

De los 203 utilizables:

| Familia | Cuántos | Qué mide | Sobreviven |
|:--|--:|:--|--:|
| `fr_*` | 82 | conteo de un grupo funcional (aminas, ésteres, halógenos, nitro…) | 72 |
| VSA | 55 | área superficial repartida en rangos de logP (`SlogP_VSA`), refractividad (`SMR_VSA`), carga parcial (`PEOE_VSA`) y estado electrotopológico (`EState_VSA`, `VSA_EState`) | 54 |
| Conteos estructurales | 27 | donadores y aceptores de hidrógeno, anillos, átomos pesados, enlaces rotables, criterios de Lipinski | |
| Topológicos | 19 | índices de conectividad y forma: `Chi`, `Kappa`, `HallKier`, `BertzCT`, `BalabanJ` | |
| Fisicoquímicos globales | 16 | TPSA, peso molecular, `MolLogP`, `qed`, `LabuteASA` | |

**Dos tercios de la matriz son conteos de subestructuras**, no propiedades físicas. Eso importa al explicar una predicción: un `fr_*` alto significa «esta molécula tiene tres de estos grupos», no «esta propiedad vale tanto».

Rangos de los que más se citan, sobre las 7,805 filas etiquetadas:

| | mínimo | mediana | máximo |
|:--|--:|--:|--:|
| TPSA (Å²) | 0.00 | 72.55 | 662.41 |
| Peso molecular | 6.94 | 362.47 | 1,882.33 |
| `MolLogP` | −8.90 | 2.55 | 12.61 |
| Donadores de H | 0 | 1 | 24 |
| Aceptores de H | 0 | 4 | 33 |
| Enlaces rotables | 0 | 4 | 53 |

## Las tres derivadas del dominio

| Columna | Cómo se construye | Para qué |
|:--|:--|:--|
| `regla_2p` | 1 si TPSA < 67 Å² **y** donadores ≤ 1 | la regla clásica de permeabilidad, como indicador binario |
| `tpsa_por_mw` | TPSA / peso molecular | polaridad por unidad de tamaño |
| `lipo_neta` | `MolLogP` − TPSA / 100 | lipofilia descontando la polaridad |

No son reglas validadas: son candidatas evaluadas en el notebook con su AUC y su correlación contra las columnas base.

## Dos ausencias que sorprenden

De los cinco descriptores que `CLAUDE.md` nombra como los de mayor poder discriminante, **dos no llegan a las 171**:

- **`MolLogP`** correlaciona **0.975** con `lipo_neta`, la derivada que lo contiene. El filtro conserva la derivada, que tiene mayor F de ANOVA, y descarta el original.
- **`MolWt`** correlaciona **0.999** con `HeavyAtomMolWt`: son la misma variable medida dos veces.

Sobreviven TPSA, donadores y aceptores de hidrógeno, que son los que el proyecto usa para verificar cualquier afirmación estructural.

## Columnas casi vacías, y por qué siguen ahí

**21 de las 82 `fr_*` valen cero en el 99% o más de las moléculas**, y 19 de ellas llegan a la matriz de trabajo. `fr_diazo` es distinto de cero en **una sola molécula** de 7,805; `fr_azo` en 5, `fr_azide` en 9, `fr_nitroso` en 10.

El umbral de varianza no las quita, y la razón es el orden de las operaciones: **se aplica sobre la matriz ya transformada con Yeo-Johnson y `standardize=True`**, donde por construcción toda columna tiene varianza 1. Sobre esa matriz solo cae `fr_azo`, que la transformación vuelve constante. Sobre los valores sin transformar caerían **26 columnas**.

Esto no es un error de cálculo —los filtros se ajustan solo con entrenamiento, como debe ser— pero sí significa que **el umbral de varianza, tal como está puesto, casi no filtra**. Es una de las cosas que cambian si la [decisión 1.5](decisiones.md#d1-5) cambia la transformación de trabajo, y conviene medirlo antes del baseline.

## Las otras matrices

| Artefacto | Qué contiene |
|:--|:--|
| `bbb_meta.parquet` | identidad y etiqueta: nombre, SMILES, InChI, `y`, `group`, `natural`, andamio, esqueleto y partición |
| `bbb_descriptores.parquet` | los 203 utilizables, sin transformar |
| `bbb_descriptores_filtrados.parquet` | las 171, transformadas con Yeo-Johnson |
| `bbb_descriptores_filtrados_sin_normalizar.parquet` | las mismas 171, sin transformar, en el mismo orden |
| `bbb_categoricas_codificadas.parquet` | `grupo_A` a `grupo_D` y `natural_False`/`natural_True` en one-hot |
| `bbb_morgan2048.npz` | Morgan/ECFP4 plegado a 2,048 bits |
| `bbb_sortslice2048.npz` | Sort & Slice, 2,048 columnas, una subestructura por columna |
| `bbb_sortslice_vocabulario.npy` | sin él no se puede transformar un compuesto nuevo |
| `bbb_preprocesamiento.joblib` | escalador, selectores y PCA, ajustados **solo con entrenamiento** |

Las dos versiones de la matriz filtrada existen porque la transformación sigue sin decidirse: los árboles reciben la original y la regresión logística la transformada.

**Las categóricas se codifican pero no entran al modelo.** `group` está confundida con la etiqueta ([decisión 1.1](decisiones.md#d1-1)) y `natural` es el eje sobre el que hay que reportar el desempeño por separado, no una variable que el modelo deba usar para compensar.
