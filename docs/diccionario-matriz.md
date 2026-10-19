# Diccionario de la matriz de entrenamiento

Qué columna es cada cosa en lo que produce el [notebook 02](../notebooks/02_Feature_Eng.ipynb). Los diccionarios de la patrocinadora describen **lo que recibimos**; este describe **lo que entra al modelo**, que no es lo mismo: entre uno y otro hay un cálculo de descriptores, una limpieza y dos filtros.

Las cifras salen de los artefactos de `data/processed/`, que el notebook regenera de principio a fin.

## De 217 columnas a 151

| Paso | Quedan | Qué pasó |
|:--|--:|:--|
| RDKit calcula sus descriptores 2D | 217 | uno por molécula, sin elegir |
| `limpiar_descriptores` | **203** | se van 14: 5 constantes, 8 con NaN (los `BCUT2D_*`) y `Ipc` |
| más tres derivadas del dominio | 206 | `regla_2p`, `tpsa_por_mw`, `lipo_neta` |
| casi constantes (valor modal ≥ 99% del entrenamiento) | 182 | se van 24, casi todas `fr_*` |
| correlación de Spearman \|ρ\| > 0.95 | **151** | se van 31, entre ellas `lipo_neta` |

**Los dos filtros se aplican sobre los valores crudos**, no sobre la matriz transformada: el criterio de casi constancia es el valor modal, que no mira la escala, y el de redundancia es la correlación de Spearman, que solo mira el orden. El notebook comprueba que la selección es la misma con estandarización, con min–max y con Yeo-Johnson, así que **cambiar la transformación de trabajo ya no obliga a repetir la selección**. Un filtro de varianza sobre la matriz ya estandarizada —que es lo que había antes— solo quitaba una columna, porque ahí toda columna tiene varianza 1.

**Cinco columnas están protegidas de los dos filtros**: TPSA, donadores y aceptores de hidrógeno, `MolLogP` y el peso molecular. Son las que la literatura usa para explicar permeabilidad y las que `CLAUDE.md` exige para verificar cualquier afirmación estructural, así que perderlas por redundancia estadística costaría más de lo que ahorra.

`Ipc` es el que muerde: el índice de contenido de información alcanza ~1e41, finito en float64 pero por encima del máximo de float32, y scikit-learn convierte internamente. Un chequeo de `isfinite` no lo detecta.

## Las cinco familias de descriptores

De los 203 utilizables:

| Familia | Cuántos | Qué mide | Sobreviven |
|:--|--:|:--|--:|
| `fr_*` | 82 | conteo de un grupo funcional (aminas, ésteres, halógenos, nitro…) | 50 |
| VSA | 55 | área superficial repartida en rangos de logP (`SlogP_VSA`), refractividad (`SMR_VSA`), carga parcial (`PEOE_VSA`) y estado electrotopológico (`EState_VSA`, `VSA_EState`) | 55 |
| Conteos estructurales | 27 | donadores y aceptores de hidrógeno, anillos, átomos pesados, enlaces rotables, criterios de Lipinski | |
| Topológicos | 19 | índices de conectividad y forma: `Chi`, `Kappa`, `HallKier`, `BertzCT`, `BalabanJ` | |
| Fisicoquímicos globales | 16 | TPSA, peso molecular, `MolLogP`, `qed`, `LabuteASA` | |

**Las dos primeras familias son conteos de subestructuras y no propiedades físicas: 137 de los 203 utilizables, dos tercios, y 105 de las 151 que llegan a la matriz de trabajo, el 70%.** Eso importa al explicar una predicción: un `fr_*` alto significa «esta molécula tiene tres de estos grupos», no «esta propiedad vale tanto».

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

No son reglas validadas, y **medidas con el modelo no aportan**. El AUC individual y la correlación dicen si una columna tiene señal, no si añade algo que el modelo no tenga ya; `scripts/experimento_derivadas.py` lo mide como lo segundo, con la misma validación cruzada agrupada, con y sin ellas (diferencia pareada de MCC contra no usarlas, 15 evaluaciones): la logística no se mueve (+0.0001 ± 0.0014) y el Random Forest queda **por debajo** con las tres (−0.0062 ± 0.0039). Corrida en `experimentos/2026-10-18-artemio-1.5-derivadas/`, supuesto S1.11 de [la Ruta](decisiones.md).

**`lipo_neta` ya no entra a la matriz**: correlaciona 0.975 con `MolLogP`, que está protegido, así que ahora cae la derivada y no el original. `regla_2p` y `tpsa_por_mw` siguen, porque no estorban.

## Los cinco clásicos sí llegan, y por qué hubo que protegerlos

Los cinco descriptores fisicoquímicos que cualquiera esperaría encontrar —TPSA, donadores y aceptores de hidrógeno, `MolLogP` y el peso molecular— **están en las 151**, pero dos de ellos solo porque la lista de protegidas los exime del filtro de correlación. Sin esa protección caerían, y por motivos que son estadísticos y no químicos:

- **`MolLogP`** correlaciona **0.975** con `lipo_neta`, la derivada que lo contiene. Antes el filtro conservaba la derivada y descartaba el original; ahora pasa lo contrario, y es la lectura correcta: la derivada no aporta nada medible ([S1.11](decisiones.md)) y el original es el que se puede explicar.
- **`MolWt`** correlaciona **0.999** con `HeavyAtomMolWt`: son la misma variable medida dos veces. Se queda el peso molecular y se va el otro.

Así quedan en la matriz los dos que `CLAUDE.md` exige para verificar cualquier afirmación estructural —TPSA < 67 Å² y donadores ≤ 1— y también `MolLogP`, que es el descriptor más frágil del conjunto: su AUC cae de 0.844 a 0.594 entre entrenamiento y validación (§12.5 del notebook 02). Tenerlo en la matriz es lo que permite enseñar esa fragilidad en vez de heredarla escondida en una derivada.

## Columnas casi vacías, y por qué siguen ahí

**21 de las 82 `fr_*` valen cero en el 99% o más de las 7,805 moléculas**, y ahora solo **tres** llegan a la matriz de trabajo. `fr_diazo` es distinto de cero en **una sola molécula**; `fr_azo` en 5, `fr_azide` en 9, `fr_nitroso` en 10, y las cuatro quedan fuera.

Las que quedan son `fr_aldehyde`, `fr_barbitur` y `fr_term_acetylene`, distintas de cero en 78, 69 y 69 moléculas. No es una excepción: el criterio se mide **sobre el entrenamiento**, donde su valor modal se queda justo por debajo del 99%, y en la matriz ya no hay ninguna columna que lo alcance.

El filtro anterior era un umbral de varianza aplicado sobre la matriz ya transformada con Yeo-Johnson y `standardize=True`, donde por construcción toda columna tiene varianza 1: de las 206 solo caía una. No era un error de cálculo —se ajustaba solo con entrenamiento— pero no filtraba. Por eso el criterio es ahora el valor modal sobre los valores crudos, que no depende de la escala.

## Las otras matrices

| Artefacto | Qué contiene |
|:--|:--|
| `bbb_meta.parquet` | identidad y etiqueta: nombre, SMILES, InChI, `y`, `group`, `natural`, andamio, esqueleto y partición |
| `bbb_descriptores.parquet` | los 203 utilizables, sin transformar |
| `bbb_descriptores_filtrados.parquet` | las 151, transformadas con Yeo-Johnson |
| `bbb_descriptores_filtrados_sin_normalizar.parquet` | las mismas 151, sin transformar, en el mismo orden |
| `bbb_categoricas_codificadas.parquet` | `grupo_A` a `grupo_D` y `natural_False`/`natural_True` en one-hot |
| `bbb_morgan2048.npz` | Morgan/ECFP4 plegado a 2,048 bits |
| `bbb_sortslice2048.npz` | Sort & Slice, 2,048 columnas, una subestructura por columna |
| `bbb_sortslice_vocabulario.npy` | sin él no se puede transformar un compuesto nuevo |
| `bbb_preprocesamiento.joblib` | escalador, las dos máscaras de selección y el orden por información mutua, ajustados **solo con entrenamiento**. El PCA no se guarda: es exploración, no un brazo candidato |

Las dos versiones de la matriz filtrada existen porque la transformación sigue sin decidirse: los árboles reciben la original y la regresión logística la transformada.

**Para evaluar se usa la versión sin normalizar, y la diferencia está medida.** La transformada trae Yeo-Johnson ajustado sobre todas las filas de entrenamiento, así que usarla en validación cruzada mete en cada pliegue de evaluación información ajustada con él; eso infla alrededor de **0.001 de AUROC** ([1.5](decisiones.md#d1-5)). Es poco, pero no se sabía hasta medirlo, y por eso `src/models/tareas.py` carga la sin normalizar por omisión y deja la transformada disponible como `descriptores_transformados` justamente para poder medir cuánto infla. El escalado va dentro de la canalización, que se reajusta en cada pliegue.

**Las categóricas se codifican pero no entran al modelo.** `group` está confundida con la etiqueta ([decisión 1.1](decisiones.md#d1-1)) y `natural` es el eje sobre el que hay que reportar el desempeño por separado, no una variable que el modelo deba usar para compensar.
