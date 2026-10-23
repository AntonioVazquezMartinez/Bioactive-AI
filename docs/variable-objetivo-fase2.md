# Propuesta: cómo definir la variable objetivo de la fase 2

**Estado:** propuesta del equipo, sin ratificar. Es la versión detallada de la decisión [2.3](decisiones.md#d2-3).
**Qué contiene:** qué vamos a modelar en la fase 2, con qué reglas se construye la etiqueta «activo» o «inactivo», qué problemas tiene y cómo se acotan.

## 1. Qué se modela

La fase 2 responde una pregunta: **¿este compuesto es activo sobre esta diana?**

- **Diana:** la proteína o el proceso sobre el que actúa el compuesto (por ejemplo, la acetilcolinesterasa). Ya viene en el archivo (`target_gene`).
- **Variable objetivo:** lo que el modelo debe predecir. El archivo **no la trae**: no hay una columna «activo» o «inactivo», hay que construirla a partir de las mediciones.
- **Unidad de predicción:** el **par compuesto-diana**, con una sola etiqueta por par (1 = activo, 0 = inactivo). Cada fila del archivo es una *medición* y un mismo par puede tener varias.
- **Alcance:** las dianas de las categorías que la patrocinadora aprobó: Alzheimer, Parkinson, neuroinflamación, depresión y estrés oxidativo. Las otras categorías quedan fuera.
- **Las dos fases son independientes:** la fase 1 (permeabilidad) y la fase 2 (actividad) no forman una cascada.
- **Dos ejercicios:** la **clasificación** (activo o inactivo) es el modelo principal. A petición de la patrocinadora se hace además un **ejercicio de predicción de la potencia** como número (sección 8).

## 2. De dónde sale la información

El archivo de actividad (`data/external/profesora/snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv`) tiene 202,647 mediciones de tres fuentes. En las cinco categorías, con gen y estructura calculable, quedan 106,645 filas, y con la definición de abajo forman estos pares:

| Fuente | Qué es | Pares | pChEMBL | Contexto del ensayo |
|:--|:--|--:|:--|:--|
| ChEMBL | Moléculas tipo fármaco; sobre todo sintéticas, pero también incluye productos naturales | 67,834 | Sí | Solo en la ruta `neuronal_assay` (sección 7) |
| NPASS | Base de productos naturales | 4,024 | No | Solo línea celular |
| CMAUP | Base de plantas medicinales y sus ingredientes | 1,005 | No | Ninguno |

**La fuente no es el origen.** Que una fila sea de NPASS o CMAUP no equivale a que el compuesto sea natural, ni al revés: ChEMBL también contiene naturales. Según la decisión [2.8](decisiones.md#d2-8), el 65.4% de los esqueletos naturales (2,727 de 4,172) aparece también en ChEMBL, y solo 1,445 existen únicamente en NPASS y CMAUP. El archivo de actividad no trae una marca de origen natural.

**Por qué no basta el pChEMBL.** Es −log10 de la concentración molar (6 equivale a 1 µM) y solo existe para ChEMBL. Etiquetar solo con él deja fuera NPASS y CMAUP y las mediciones con relación `>`.

**Qué columnas se usan.** Las de la sección 5 del diccionario, a las que el propio diccionario remite («para entrenar conviene usar las columnas de la sección 5»). Existen en las tres fuentes y siempre traen valor:

| Columna | Qué contiene |
|:--|:--|
| `activity_relation_used` | `=` (72% de las filas), `>` (27%) y, con menos del 1% entre todas, `<`, `<=`, `>=`, `~`, `>>` |
| `activity_value_used` | Número mayor que 0 |
| `activity_units_used` | nM (85%), uM (15%) y unas pocas unidades más |

**Qué se deja fuera, y por qué.** Se usa **solo la relación y el valor**, que son homogéneos entre fuentes. No se mezclan los **inactivos declarados por texto** (`evidence_kind` = `inactivo_por_texto`, 29,730 filas): ChEMBL solo dice «Not active» —el comentario completo es «Inhibition < 50% @ 10 uM and thus dose-reponse curve not measured», así que el límite de 10 µM **sí viene de la fuente** y la codificación como `> 10 µM` es una traducción fiel—, pero todas salen de un **único documento** (`CHEMBL1909046`, el panel DrugMatrix) con 772 compuestos y sin curva dosis-respuesta. Es eso lo que las excluye: una sola campaña de tamizaje definiría el 61% de la clase negativa por registro. Entran solo como sensibilidad (sección 9).

## 3. Cómo se clasifica cada medición

Primero, el valor se pasa a µM: nM × 0.001, uM × 1. Se excluyen las **662 filas en masa por volumen** (`ug.mL-1`, `ug ml-1`, `pg/ml`, `ng/L`; 0.3%), porque convertirlas exige el peso molecular de cada compuesto. Otras 68 filas en unidades molares escritas de otra forma (`10^3nM`, `10^2 uM`, `10^6uM`, `M`, `mM`, `umol/L`, `um`) sí se convierten.

Después se compara con el corte **T** según la relación, con la lectura de `>` de la sección 7 del diccionario («un `>` solo sirve como negativo si su límite es igual o mayor que el umbral de activo»):

| Relación | Condición | Resultado |
|:--|:--|:--|
| `=` o `~` | valor ≤ T | **activa** |
| `<` o `<=` | valor ≤ T | **activa** |
| `=` o `~` | valor > T | **inactiva** (medida) |
| `>` o `>=` | límite ≥ T | **inactiva** (por límite) |
| `<` o `<=` | valor > T | sin decisión |
| `>` o `>=` | límite < T | sin decisión |
| cualquier otra | | sin decisión |

Un `>` con límite menor que T no demuestra nada: si el ensayo llegó a 1 µM sin efecto, no sabemos qué pasa a 10 µM. Esas mediciones no cuentan como activas ni como inactivas.

## 4. El corte T

**T = 10 µM (pChEMBL ≥ 5) para las tres fuentes.** Es la convención de ExCAPE-DB que recoge la investigación [04](referencias/04-datos-neuroactividad.md) (pXC50 ≥ 5), la concentración estándar de cribado y la que maximiza el número de pares utilizables. **El diccionario no fija el corte**: deja «el umbral de activo que se use». Es una decisión del equipo con precedente.

**1 µM (pChEMBL ≥ 6) se reporta siempre como sensibilidad.** Cambiar el corte cambia el balance: con 1 µM los activos pasan de 72.6% a 49.4%.

## 5. Cómo se arma la etiqueta del par

**Llave del par:** el **esqueleto de conectividad** del compuesto (primeros 14 caracteres del InChIKey, `key14`, calculado desde `smiles_raw`) × `target_gene`, la misma llave que `grupos_cv` usa en `src/data_prep/splits.py`. No se usa `source_compound_id`: ChEMBL usa identificadores `CHEMBL…` y NPASS y CMAUP `NPC…`, que no comparten ningún valor, así que un compuesto medido en dos fuentes entraría como dos pares independientes y sus contradicciones serían invisibles. Las filas sin gen o sin estructura calculable no forman par.

**Regla:**
1. Si alguna medición del par es **activa** y ninguna es **inactiva** → **activo (1)**.
2. Si alguna es **inactiva** y ninguna es **activa** → **inactivo (0)**.
3. Si el par tiene una medición activa **y** una inactiva (**conflicto**) → **se quita**: no entra al entrenamiento ni a la evaluación. Su número se reporta.
4. Si todas quedan sin decisión → sin etiqueta.

**Ejemplos (ilustrativos), con T = 10 µM:**

| Mediciones del par | Etiqueta |
|:--|:--|
| IC50 = 0.3 µM | **1** |
| IC50 = 25 µM; IC50 = 40 µM | **0** |
| IC50 > 10 µM | **0** |
| IC50 = 2 µM; IC50 = 30 µM | se quita (conflicto) |
| IC50 > 1 µM | sin etiqueta |

## 6. Cuánto queda

Con T = 10 µM, en las cinco categorías y sin los inactivos por texto:

| Conjunto | Pares | En conflicto (se quitan) | Con etiqueta | Activos |
|:--|--:|--:|--:|--:|
| **Las tres fuentes** | 70,384 | 1,784 (11.8% de los 15,153 con varias mediciones) | 66,121 | 72.6% |
| ChEMBL | 67,834 | 1,561 (11.7%) | 63,796 | 74.8% |
| NPASS | 4,024 | 321 (32.4%) | 3,688 | 22.9% |
| CMAUP | 1,005 | 148 (38.9%) | 857 | 46.2% |

Con T = 1 µM, las tres fuentes dan 67,266 pares etiquetados y 49.4% de activos (2,535 en conflicto).

## 7. Qué problemas tiene esta etiqueta, declarados

1. **La fuente y la etiqueta quedan confundidas, y este es el riesgo mayor.** Al unir las tres fuentes con el mismo corte, el porcentaje de activos va de 74.8% (ChEMBL) a 46.2% (CMAUP) y 22.9% (NPASS). Un modelo podría acertar solo con «viene de NPASS, entonces inactivo». Por eso el desempeño se reporta **siempre por fuente**, no solo en total, y se entrena el control de atajo de la sección 10. La sensibilidad «solo ChEMBL» es la alternativa si el control muestra que la fuente filtra la etiqueta.
2. **Quitar los conflictos no es neutro.** Se pierde el 11.8% de los pares con varias mediciones, y más en NPASS y CMAUP (32% y 39%). El conjunto que queda es el más consistente, no el más representativo, y su desempeño será optimista para los pares difíciles. El número de pares quitados se reporta por fuente.
3. **Medidas distintas en una misma columna.** `activity_type` tiene 41 tipos (IC50, Ki, EC50, Kd, GI50 y «Potency» de PubChem, entre otros). «Potency» pesa mucho en NPASS (2,427 filas) y CMAUP (775) y casi nada en ChEMBL. **Y los tipos tienen dirección:** un IC50 mide potencia de inhibir y un EC50, de activar, pero la etiqueta no mira el tipo, así que en las dianas donde se busca *activar* (`PPARG`, `SIRT1`, `NFE2L2`, `TSPO`; el 29% de sus filas son IC50) un compuesto puede quedar «activo» por inhibir. La propuesta de esta sección no lo trata; está abierto en la [decisión 2.3](decisiones.md#d2-3) y en el [#95](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/95).
4. **El mismo corte no significa lo mismo en todos los ensayos, y el contexto está ausente justo en las filas que se modelan.** Tipo de ensayo, formato, tejido y línea celular dependen por completo de la ruta por la que entró la fila (`selection_route`). En ChEMBL, `neuronal_assay` (89,470 filas) trae formato en el 100%, `both` (784) en el 100% y `cns_target` (97,100 filas, la ruta de casi todas las dianas de la lista) en **0**. No es dato faltante: son dos rutas anotadas de forma distinta al construir el archivo. Por eso no se puede comprobar con los datos si el tejido explica los conflictos; el vacío no es evidencia de que el tejido no influya, porque el experimento ocurrió en algún tejido y lo que falta es la columna. Lo que sí está en el 100% de las filas es `assay_chembl_id` (8,803 ensayos distintos) y `reference_id`.
5. **Relaciones inferidas.** 2,001 filas de NPASS no traían relación; el equipo de la patrocinadora asignó `=` con una regla que el diccionario da con 98.4% de acierto. Se usan como vienen; la sensibilidad sin ellas está en la sección 9.
6. **Filas marcadas por ChEMBL.** 5,287 filas (2.6%) llevan «Outside typical range» en `chembl_data_validity_comment`. Se mantienen y se repite el análisis sin ellas.
7. **Copias.** 1,014 filas tuvieron copias idénticas que ya se quitaron (`n_registros_identicos` > 1); no hace falta deduplicar de nuevo.
8. **El corte cae donde la medición es menos fiable.** Entre las mediciones exactas de las cinco categorías (sin los inactivos por texto y con pActividad entre 2 y 12), el 20.7% queda a menos de 0.5 unidades logarítmicas de 10 µM (18.2% en ChEMBL) y el 24.3% a esa distancia de 1 µM. Y entre los pares con al menos dos mediciones exactas (12,612), el rango mediano es 0.43 unidades, el 25.5% supera una unidad y el 9.0% tiene mediciones a los dos lados de 10 µM. Una etiqueta binaria con corte fijo es, por tanto, poco estable justo para esos pares; es la razón de fondo de la [2.9](decisiones.md#d2-9). *Cifras calculadas con las funciones de `scripts/cifras_etiqueta_fase2.py`; falta incorporarlas al script para que tengan una corrida versionada.*

## 8. Ejercicio de predicción de la potencia

A petición de la patrocinadora, que quiere encontrar a partir de qué valor un compuesto se vuelve significativo, se hace además un modelo que **predice la potencia como número** y no necesita un corte.

- **Variable:** pActividad = −log10 de la concentración molar (= 6 − log10 del valor en µM); en ChEMBL coincide con el pChEMBL.
- **Qué mediciones entran:** las exactas (`=` o `~`) en µM, que dan 58,001 pares con al menos una. Las censuradas (`<`, `>`) no se usan como si fueran valores exactos, como indica el diccionario.
- **Cómo se agrega por par:** la **mediana** de sus mediciones exactas. Evita el concepto de conflicto (el rango mediano entre mediciones de un par es 0.44 unidades; el percentil 90, 1.85).
- **Valores fuera de rango:** hay pares con pActividad de −6.7 a 16.4, que son errores de unidades o de captura; se revisan y se recortan antes de entrenar.
- **Qué entrega:** el desempeño en función de la potencia y, a partir de él, el valor en el que el modelo empieza a separar bien. Es la respuesta a su pregunta sobre el umbral.

## 9. Protocolo de robustez

La variabilidad entre ensayos no se resuelve con los datos disponibles; se **acota**. La etiqueta se construye una vez y el análisis se repite bajo estas variantes (T = 10 µM, cinco categorías):

| Variante | Pares con etiqueta | Activos |
|:--|--:|--:|
| **Definición principal** (tres fuentes, sin inactivos por texto, sin conflictos) | 66,121 | 72.6% |
| Conflictos como activos | 67,905 | 73.3% |
| Con los inactivos por texto | 68,265 | 70.3% |
| Sin las 2,001 relaciones inferidas | 65,368 | 73.2% |
| Solo IC50 | 45,050 | 71.0% |
| Solo Ki | 15,418 | 86.8% |
| Solo ChEMBL | 63,796 | 74.8% |
| Por tipo de ensayo o tejido | no es viable hoy | — |
| Por artículo disjunto | no es viable: 55.9% en un componente | — |

- **Por tipo de ensayo o tejido** exige que la ruta `cns_target` esté anotada. Dos caminos, en orden: (1) **pedirle a Jorge la misma anotación para esa ruta**, que su equipo ya hizo con la misma tubería para 93,204 filas; no es una capacidad nueva y mantiene una sola versión de ChEMBL, con las dos fases comparables; (2) como plan B y en paralelo, el volcado de ChEMBL 37 uniendo por `assay_chembl_id`, que el proyecto ya declara como alternativa de la fase 2.
- **Validación por artículo disjunto: en su versión estricta no es viable.** La idea era agrupar también por `reference_id` para probar el modelo en artículos que no vio. Con las referencias que `fase2_pares.parquet` ya guarda, conectando dos pares que comparten al menos una referencia, **un solo componente reúne 39,362 pares, el 55.9%**, y el siguiente tiene 601. El 93.8% de los pares tiene una sola referencia, que es lo que lo hace parecer fácil; lo que los enlaza son los compuestos medidos en varios artículos. Separar por componentes pondría más de la mitad de los datos de un lado y la prueba sería un solo bloque.

  Quedan dos versiones aproximadas, las dos posibles con lo que el artefacto ya trae, y **no se elige todavía**: reportar el desempeño **por referencia** dentro de la validación cruzada, sin exigir que los grupos sean disjuntos; o agrupar cada par por su **referencia principal**, aceptando que algunos compuestos aparezcan en más de un artículo. La primera no cambia la partición y solo añade un corte al reporte; la segunda sí la cambia y hay que medir cuánta fuga deja. Se decide en el Avance 3, con la cifra de fuga de la segunda medida. El cálculo está en la sección 6.4 del [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb).

Si el resultado no cambia entre variantes, el modelo no depende de esas diferencias; si cambia, se reporta cuánto.

## 10. Regla para variables y fuentes

La fuente, el tipo de ensayo, el tejido y el artículo **no entran como características** del modelo: la entrada del sistema es un SMILES y un compuesto nuevo no las tiene. Se entrena además un **control de atajo** que solo ve esas variables, sin estructura química. Si ese control se acerca al desempeño del modelo con química, esas variables llevan información de la etiqueta; se quedan fuera y el desempeño se reporta por estrato. Si, al revisar la importancia de las características, aparecieran variables que actúan como identificador de fuente o de ensayo, se descartan esas variables (o la fuente). Es el control del issue #32. La diana sí es una entrada válida.

## 11. Qué queda por confirmar

Nada de esta lista bloquea el modelado: las cinco entradas que esperaban a la patrocinadora quedaron vigentes por decisión del equipo (el 17 de octubre), cada una con lo que la haría cambiar. Lo que sigue es lo que **se le informa** y lo que **falta construir**.

1. **Con la patrocinadora: informar, no esperar.**
   - **Que las tres fuentes se etiquetan con el mismo corte** ([2.3](decisiones.md#d2-3)). En su correo del 16 de octubre descartó «hacer la inferencia, al menos no de forma directa». Aquí se lee como respuesta a lo que se le preguntó en la reunión (construir el valor en las otras bases para partir en activo e inactivo), y no como rechazo de las columnas que cada fuente ya informa. Es una lectura del equipo, no una respuesta suya, así que se le muestra con filas reales y con la pregunta literal: *las columnas de la sección 5 dan una concentración y una relación en las tres bases; ¿descartó usarlas con el mismo corte, o solo inferir lo que no viene informado, como las 2,001 relaciones de NPASS?* Si dice que descartó usarlas, el análisis «solo ChEMBL» pasa a ser el principal; no hay que reconstruir nada, porque ya se reporta al lado.
   - **Su petición de revisar la distribución por tejido y tipo de experimento.** La respuesta es un hallazgo: esas columnas están vacías en las filas que se modelan (la ruta `cns_target`, 108,640 filas), así que no se puede revisar con este archivo.
   - **Que estrés oxidativo es 47.7% NPASS y CMAUP.** Si además se descartara el etiquetado de esas dos fuentes, la categoría que ella pidió conservar pasaría de 2,456 filas a 1,285. Sus dos decisiones se restan entre sí.
   - **El método con que se separó el 10%**, que Jorge va a compartir, y el experimento que Artemio ofreció: comparar el desempeño contra ese 10% y contra la partición por andamio, que debería salir inflado.
   - Lo que **ya no se le pregunta**: el cruce con COCONUT del archivo de actividad lo calcula el equipo ([2.8](decisiones.md#d2-8)), y el punto de operación del entregable no se fija: se entrega la curva ([C.5](decisiones.md#dc-5)).
2. **Con Jorge.** Anotar la ruta `cns_target` con tipo de ensayo, formato, tejido y línea celular, o el volcado de ChEMBL 37 como plan B (los dos caminos están en la sección 9). No es necesario para entrenar; sirve para comprobar si el tejido y el tipo de ensayo explican los conflictos.
3. **Del lado del equipo.**
   - **El control de atajo** ([#32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32)) tiene que correrse antes de citar cualquier cifra por fuente: es lo que sostiene la decisión de etiquetar las tres.
   - **La sección 8** de este documento describe la potencia como un ejercicio sobre mediciones exactas con la mediana por par. La [2.9](decisiones.md#d2-9) propone en cambio un solo modelo de regresión con los censurados como observaciones censuradas, y la [2.10](decisiones.md#d2-10) guarda el objetivo como intervalo. Hay que alinearlas cuando se decida la 2.9 (Avance 4).
   - **Las cifras** de este documento salen de `scripts/cifras_etiqueta_fase2.py`, que las reproduce (70,384 pares). La diferencia con una versión anterior eran las filas en µg/mL, que no pueden etiquetarse sin el peso molecular.

## 12. Cómo se calcularon las cifras

Todas salen del archivo de actividad recibido (202,647 filas). Las filas se restringen a las cinco categorías, con `target_gene` y estructura calculable (`smiles_raw`). Las cifras del diccionario (225,513 filas) corresponden al archivo completo, no al recibido. Los porcentajes por registro y por par se declaran como tales.
