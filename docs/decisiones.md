# La ruta del proyecto

Bitácora de lo que se decide en cada fase y de las posibilidades que siguen abiertas. Se alimenta **por fase, no por avance**: la fase 1 es la permeabilidad de la barrera hematoencefálica (BBB+/BBB−) y la fase 2, la actividad neuroprotectora por diana. Ambas parten de los archivos que entregó la patrocinadora el 25 de septiembre. Cada fase tiene sus **decisiones** (lo que se resolvió o se propone), sus **supuestos** (lo que se dio por cierto para avanzar y puede ser falso) y, en cada entrada, la pregunta que queda por resolver.

Nada es *ratificado* hasta que la patrocinadora lo revise; lo que el equipo adopta sigue siendo reversible, y dos decisiones ya se revirtieron al medir. Cuando algo cambia se deja la versión anterior visible. Los términos están en el [glosario](glosario.md).

## Estado de un vistazo

**Marco común** (aplica a las dos fases)

| # | Decisión | Estado |
|:--|:--|:--|
| [C.1](#dc-1) | MCC y AUPRC sobre la clase minoritaria | Vigente |
| [C.2](#dc-2) | Dos métodos de atribución independientes | Vigente |
| [C.3](#dc-3) | Comprobar si combinar las dos predicciones mejora la selección (solo si la patrocinadora lo considera útil) | Propuesta |
| [C.4](#dc-4) | PAINS: aplicarlos a los resultados finales | Propuesta |
| [C.5](#dc-5) | Qué error cuesta más y cómo presentar el ranking | Abierta |
| [C.6](#dc-6) | Licencia y uso académico de los resultados | Propuesta |

**Fase 1 · Permeabilidad**

| # | Decisión | Estado |
|:--|:--|:--|
| [1.1](#d1-1) | No filtrar por la columna de grupo A–D | Vigente · revisada |
| [1.2](#d1-2) | Partición por andamio, nunca aleatoria | Vigente |
| [1.3](#d1-3) | Descriptores RDKit más Morgan/ECFP4 | Vigente |
| [1.4](#d1-4) | Las 6 filas con logBB sin clase | Propuesta |
| [1.5](#d1-5) | Tres modelos candidatos; de ahí, si escalar y si reducir dimensión | Propuesta |
| [1.6](#d1-6) | Naturales y sintéticos: ¿modelos separados u origen como variable? | Abierta |
| [1.7](#d1-7) | Tamaño L de Sort & Slice: 2048 de trabajo; 512 es posible con XGBoost o Random Forest | Propuesta |

**Fase 2 · Actividad**

| # | Decisión | Estado |
|:--|:--|:--|
| [2.1](#d2-1) | Excluir las dianas sin datos | Propuesta · bloquea el Avance 3 |
| [2.2](#d2-2) | Forma del modelo: por diana, por categoría o multitarea | Abierta · bloquea el Avance 3 |
| [2.3](#d2-3) | Etiquetado por tres vías y criterio de «activo» | Propuesta · bloquea el Avance 3 |
| [2.4](#d2-4) | Los 88,098 registros fenotípicos | Propuesta |
| [2.5](#d2-5) | La fuente confundida con el etiquetado | Vigente · medida |
| [2.6](#d2-6) | La partición de prueba que pudo reservarse | Abierta · bloquea el Avance 3 |
| [2.7](#d2-7) | Partición de la fase 2 | Propuesta |

Estados: **vigente** (se trabaja sobre ella), **revisada** (se decidió, se midió y cambió), **propuesta** (hay recomendación del equipo, aún sin adoptar), **abierta** (sin recomendación) y **ratificada** (ninguna todavía). Si una pregunta de la 2.1 a la 2.3 o la 2.6 no llega a tiempo, el Avance 3 avanza con la propuesta del equipo, marcada como no ratificada.

---

## Marco común {#comun}

Lo que vale para las dos fases.

### Decisiones

#### C.1 · MCC y AUPRC sobre la clase minoritaria {#dc-1 .vigente}

**Estado:** vigente

> **Pregunta:** ¿Qué punto de operación corresponde? Ver [C.5](#dc-5).

**Qué pasó.** Hay 1.74 positivos por negativo: un modelo que prediga siempre BBB+ acierta el 63.5% sin aprender nada. El Avance 2 reportó AUPRC sobre la clase positiva, que es la mayoritaria, con línea base 0.573; los valores de 0.70–0.86 parecían buenos y eran poco informativos. Quedó documentado en el notebook.

**Se decidió.** Métricas principales: MCC y AUPRC sobre la clase minoritaria. Exactitud y AUROC no se reportan solos.

#### C.2 · Dos métodos de atribución independientes {#dc-2 .vigente}

**Estado:** vigente · requisito de la patrocinadora

**Se decidió.** Al menos dos métodos de atribución independientes; solo se reportan como confirmadas las subestructuras en que coinciden. Un modelo interpretable simple se entrena en paralelo como control. Toda afirmación estructural se contrasta primero contra TPSA (<67 Å²) y HBD (≤1), que dominan empíricamente. Aplica a las dos fases.

### Propuestas

#### C.3 · Comprobar si combinar las dos predicciones mejora la selección {#dc-3 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Vale la pena probar, como experimento aparte con los 1,033 compuestos que tienen las dos mediciones, si combinar la predicción de permeabilidad con la de actividad elige mejor que cada una por separado?

**Qué pasó.** Hay dos modelos, uno de permeabilidad y uno de actividad, y el ranking final usará los dos. Falta saber si juntarlos ayuda. Solo 1,033 esqueletos tienen medición en los dos conjuntos (1.0% de la fase 2, 25.7% de la fase 1), así que son el único lugar donde se puede comprobar contra datos reales. Reservarlos obligaría a sacarlos también del entrenamiento de la fase 1, o habría fuga, y costaría una cuarta parte de sus datos.

**Se propone.** Condicionada a que la patrocinadora considere que vale la pena: no hacer nada de esto hasta que la patrocinadora diga si el experimento vale la pena. Cada fase se entrena y evalúa con su protocolo ([1.2](#d1-2), [2.7](#d2-7)), sin reservar nada. Si la patrocinadora lo aprueba, el experimento va en dos pasos:

1. **Con datos solamente, sin modelos.** Cruzar las mediciones reales de los 1,033: permeabilidad medida (BBB+ o BBB−) contra actividad medida, por diana. Muestra si hay algo que combinar: si casi todos los activos son BBB+, la permeabilidad aporta poco al ranking; si hay muchos activos BBB−, cambia el orden. Se puede hacer en cuanto se apruebe, porque no depende de las etiquetas de actividad ni de ningún modelo.
2. **Con los modelos ya entrenados.** Medir si la combinación acierta más que cada predicción sola. Como el modelo de la fase 1 habrá visto parte de esos compuestos, se usan predicciones fuera de muestra (validación cruzada agrupada por andamio). Necesita el modelo de actividad, que depende de las etiquetas pendientes de la decisión [2.3](#d2-3), y los modelos afinados de los Avances 3 a 5. Cuántos de los 1,033 caen en la prueba de ambas fases no está medido.

Es exploratorio: los 1,033 no son una muestra representativa (son los compuestos con las dos mediciones, probablemente los más estudiados), así que un buen resultado ahí no se generaliza sin más.

**Criterio de diseño.** Un BBB− no descarta al compuesto: de los 99,585 esqueletos con actividad, el 99% no tiene permeabilidad medida, y filtrar con una predicción sin verificar eliminaría candidatos con actividad documentada. Las dos fases son dos evidencias que se combinan al presentar el ranking, no una cascada.

#### C.4 · PAINS: aplicarlos a los resultados finales {#dc-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿En el ranking final los compuestos con alerta PAINS se marcan o se excluyen? ¿Qué otros filtros de reactividad o toxicidad son aceptables para productos naturales?

**Qué pasó.** 413 compuestos del conjunto de permeabilidad (5.3%) llevan alerta PAINS, 2.1 veces más frecuente en naturales (7.5% contra 3.6%), justo los que se quiere priorizar; con coincidencia por esqueleto son 6.9% contra 3.2%. PAINS no quiere decir inactivo: la actividad medida puede no venir del mecanismo supuesto. Los filtros son de `baell2010pains`, derivados de ~93,000 compuestos en ensayos AlphaScreen de una institución; `capuzzi2017phantom` documenta su baja precisión como predictores de promiscuidad y `baell2018seven` es el propio autor revisando su mal uso. Con datos propios, el compuesto mediano toca 1 diana y el percentil 99, 4; la curcumina aparece contra 32, la quercetina contra 31 y el resveratrol contra 28.

**Se propone.** PAINS no entra al entrenamiento ni a la prueba, para no sesgar contra los naturales. Se aplica a la salida: cada candidato del ranking lleva su alerta y el ranking se reporta con y sin esos compuestos. Una molécula que agrega no falsea un logBB, así que en la fase 1 la alerta es información; en la fase 2 sí condiciona cómo leer el ranking.

**Versión anterior, descartada como primaria.** Tres brazos: sin filtrar, filtrado solo en entrenamiento y evaluación estratificada. Puede retomarse si el ranking resulta dominado por alertas; su regla sigue valiendo: nunca filtrar la prueba y declarar el protocolo antes de correrlo.

#### C.5 · Qué error cuesta más y cómo presentar el ranking {#dc-5 .abierta}

**Estado:** abierta

> **Pregunta:** ¿Qué error pesa más? ¿Cómo se presenta el ranking para que sea accionable en laboratorio: lista ordenada, umbral con corte o agrupado por diana? ¿Cómo se presenta un compuesto con BBB− predicho y actividad documentada?

**Qué pasó.** El umbral de decisión depende de qué error es más caro, y eso no lo decide la estadística. Un falso activo manda al laboratorio a ensayar algo que no funciona (tiempo y reactivos); un falso inactivo descarta un candidato real y nadie se entera. Las métricas están fijadas ([C.1](#dc-1)); el punto de operación no.

#### C.6 · Licencia y uso académico de los resultados {#dc-6 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Se autoriza publicar los resultados, y qué datos derivados, bajo uso académico no comercial? ¿Hay aspiraciones comerciales? NPASS (CC BY-NC) lo impediría.

**Se propone.** Los archivos de la patrocinadora son la fuente y el producto puede ser un texto académico de investigación. Qué hace falta:

| Qué hace falta | Estado |
|:--|:--|
| **Licencias compatibles.** B3DB y COCONUT: CC0. NPASS: CC BY-NC 4.0 (uso y redistribución académicos con atribución; 11,992 registros, 5.9% del archivo). ChEMBL: CC BY-SA 3.0 (atribución, y lo derivado comparte licencia). CMAUP: CC BY según el artículo, términos de la base sin confirmar | Falta confirmar CMAUP y la licencia de lo derivado |
| **Autorización escrita** para publicar resultados y, si se quiere, datos derivados: los archivos están curados por ella (SMILES estandarizados, cruce con COCONUT, 39 dianas a mano) | Pendiente |
| **Cómo citar** sus archivos y diccionarios (autoría, versión, entrega del 25 de septiembre de 2026) y las fuentes originales con versión (ChEMBL 37, B3DB, COCONUT, NPASS, CMAUP) | Pendiente |
| **Disponibilidad de datos y código.** Qué se publica (código, particiones, etiquetas) y qué solo se referencia (el archivo de 74 MB va por Git LFS) | Por definir |
| **Reproducibilidad.** Versiones de RDKit y librerías, semillas, huella de los datos | Parcial: hay `requirements.txt` |
| **Lo que un revisor pedirá.** Baseline propio con intervalos de confianza, partición por andamio y por fuente, validación externa, «activo» definido y un resultado sin patrón reportado tal cual | En curso |
| **Marco institucional.** Políticas de propiedad intelectual y autoría del Tec y del departamento, orden de autoría, foro | Por confirmar |

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| SC.1 | La estructura molecular basta para predecir permeabilidad y actividad | Sin comprobar | Es la hipótesis de trabajo | Se reporta como resultado: «sin patrón aprendible» es válido |
| SC.2 | Los 1,033 compuestos comunes bastan para medir la combinación de las dos predicciones | Sin comprobar | No se ha medido cuántos caen en la prueba de ambas fases ([C.3](#dc-3)) | Usar predicciones fuera de muestra o reportar que no alcanza |

---

## Fase 1 · Permeabilidad {#fase1}

El conjunto tiene 7,811 filas, 7,805 con clase, que son 4,018 esqueletos de conectividad: ese es el tamaño efectivo. Evidencia: [reporte del Avance 1](reportes/README.md), [notebook 01](../notebooks/01_EDA.ipynb) y [notebook 02](../notebooks/02_Feature_Eng.ipynb).

### Decisiones

#### 1.1 · No filtrar por la columna de grupo A–D {#d1-1 .vigente .revisada}

**Estado:** vigente · revisada el 4 de octubre

**Qué pasó.** [02 · Datasets BBB](referencias/02-datasets-bbb.md) leía las categorías A–D de B3DB como escala de confiabilidad y proponía entrenar con A+B. El EDA del Avance 1 lo desmintió: el grupo D tiene mediana de 3 referencias contra 1 del C; ningún registro duplicado tiene etiquetas contradictorias; y la columna está confundida con la etiqueta, porque filtrar a A+B baja la clase minoritaria de 36.5% a 27.0%. Esa recomendación sigue visible en el documento, marcada como superada.

**Se decidió.** La columna describe y estratifica, nunca excluye. El entrenamiento pasa de 4,679 a 7,805 compuestos (+67%). Las caídas de AUC por partición por andamio son mayores que las medidas sobre A+B (logP pierde 0.198 contra 0.175) porque el conjunto es más diverso: el número anterior estaba inflado.

#### 1.2 · Partición por andamio, nunca aleatoria {#d1-2 .vigente}

**Estado:** vigente

> **Pregunta:** ¿Hay razón experimental para separar también por laboratorio o por fuente, más allá del andamio?

**Qué pasó.** Los andamios grandes tienen pureza de clase extrema: el más frecuente, de 410 compuestos, es 99.5% BBB+. Con partición aleatoria al modelo le basta reconocer el andamio, y la literatura reporta que así se infla el resultado entre 7 y 13 puntos.

**Se decidió.** Bemis-Murcko, agrupando también por esqueleto de conectividad para que los estereoisómeros no se separen. Los andamios frecuentes van a entrenamiento y los raros a prueba (convención de DeepChem): 5,557 / 749 / 1,499, sin andamio ni esqueleto compartido. **Los 312 compuestos acíclicos** (cadenas sin anillos, que no tienen andamio) **van todos a entrenamiento**: no comparten estructura de anillo con nada, así que no filtran información a la prueba, pero tampoco ayudan a medir generalización estructural.

**Consecuencias.** La prueba tiene 1,390 andamios en 1,499 compuestos y 57.3% BBB+ contra 64.0% del entrenamiento: se evalúa sobre una distribución distinta de la que aprendió, que es lo realista. Construida al revés, con los frecuentes en prueba, daba 45 andamios con el benceno ocupando el 26%; la dirección de la asignación es el detalle crítico.

#### 1.3 · Descriptores RDKit más Morgan/ECFP4 {#d1-3 .vigente}

**Estado:** vigente

> **Pregunta:** ¿Se conoce una representación más eficiente o más interpretable para productos naturales?

**Se decidió.** 217 descriptores 2D de RDKit (203 utilizables) más Morgan/ECFP4 de 2,048 bits con `rdFingerprintGenerator`. Con `radius=2` se obtiene ECFP4, porque el número del nombre es el diámetro. Se descartaron los *embeddings* congelados de transformers, que no superan a esta combinación bajo partición por andamio.

**Qué pasó.** `Ipc` alcanza ~1e41, finito en float64 pero fuera de float32, y sklearn convierte internamente; `isfinite` no lo detecta y costó una ejecución fallida, así que se descarta. El fingerprint plegado además mezcla subestructuras en un mismo bit; por eso se evalúa **Sort & Slice**, sin colisiones y con el vocabulario aprendido solo del entrenamiento. Con 2048 columnas cubre el 84.8% de las subestructuras del entrenamiento y el 68.0% de las del conjunto de prueba (el vocabulario se aprende solo con el entrenamiento, y la prueba trae los andamios raros). Esa brecha de 16.8 puntos crece con el vocabulario: 13.6 con 512 columnas y 17.8 con 4096. No es la cobertura en validación de la tabla de más abajo (71.0% con 2048), que se mide dentro de la validación cruzada.

### Propuestas

#### 1.4 · Las 6 filas con logBB sin clase BBB {#d1-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Pueden completarse desde B3DB?

**Qué pasó.** Seis filas (zidovudina, miltefosina y otras cuatro) traen `logbb` pero no clase integrada. Según el diccionario sí tienen clase en B3DB, pero su fila de clasificación es de otra forma estereoquímica y no empató por estructura.

**Se propone.** Excluirlas de la clasificación y no imputar una etiqueta desde la conectividad, porque la estereoquímica puede cambiar la clase.

#### 1.5 · Tres modelos candidatos; de ahí, si escalar y si reducir dimensión {#d1-5 .propuesta .revisada}

**Estado:** propuesta · revisada el 12 de octubre

> **Pregunta:** ¿Se prioriza la explicabilidad (matriz de 171 columnas, cada una una propiedad o subestructura) sobre la reducción de dimensión con PCA, que no se traduce a subestructuras?

**Qué pasó.** El Avance 2 pedía escalamiento y selección de características. Escalar no es una decisión independiente: depende del modelo. Medido en el notebook 02: 120 pares de descriptores con correlación mayor a 0.95; Yeo-Johnson corrige mejor la asimetría, de 106 a 66 descriptores muy asimétricos. El PCA al 95% (85 componentes) da un MCC algo mayor con la regresión logística (0.512 contra 0.500) y algo menor con Random Forest (0.558 contra 0.566); el AUROC del Random Forest empeora (0.872 contra 0.916) y el intervalo del bootstrap de la diferencia cruza el cero. La selección dejó 171 de 206 descriptores.

**Qué cambió, y con qué.** La versión anterior de esta entrada decía que Yeo-Johnson quedaba *a la par* de min–max en la regresión logística, con MCC 0.484 contra 0.481. Esa comparación era de **una sola corrida sobre una sola partición de validación**, y su orden cambiaba con el entorno: min–max daba 0.481 en Linux, 0.489 en macOS con Python 3.12 y 0.497 en macOS con Python 3.14, contra un 0.484 estable de Yeo-Johnson. La conclusión dependía de quién ejecutara.

`scripts/experimento_escalado.py` la repite con validación cruzada de 5 pliegues agrupada por andamio y esqueleto de conectividad, 3 semillas, la transformación **reajustada dentro de cada pliegue** y la prueba sin tocar (resultados en `notebooks/datos/resultados_escalado.csv`, sección 8.2 del [notebook 02](../notebooks/02_Feature_Eng.ipynb)). MCC medio y AUPRC sobre BBB−:

| Transformación | LogReg, MCC | LogReg, AUPRC | RF, MCC | RF, AUPRC |
|:--|--:|--:|--:|--:|
| sin escalar | 0.687 | 0.867 | 0.704 | 0.901 |
| estandarización | 0.690 | 0.864 | 0.705 | 0.901 |
| min-max | 0.695 | 0.878 | 0.704 | 0.901 |
| Yeo-Johnson | 0.665 | 0.862 | 0.705 | 0.901 |

- **Ningún intervalo del 95% excluye el cero.** Con quince evaluaciones que comparten datos de entrenamiento, la medición no establece que una transformación supere a otra. La diferencia mayor —min–max contra Yeo-Johnson en la regresión logística— es de 0.030 de MCC con un error estándar corregido de 0.019: t = 1.6, intervalo [−0.010, +0.071]. Lo que esta medición aporta es sobre todo **la cota**: la incertidumbre es mayor que todas las diferencias entre transformaciones menos una.
- **En Random Forest la transformación es irrelevante, y eso sí queda establecido**: diferencias de 0.000 a 0.001 con intervalos de ±0.002 a ±0.005, tan estrechos que descartan cualquier efecto que importe. La invariancia de los árboles deja de ser solo un argumento.
- **Yeo-Johnson es consistentemente la peor para la regresión logística**: por debajo de min–max en 12 de los 15 pliegues y de estandarización en 13. La dirección es estable; la magnitud no alcanza significancia con esta cantidad de evaluaciones dependientes. Entre las otras tres la medición **no distingue** en MCC (+0.005 y +0.009).
- **Corregir la asimetría y predecir mejor parecen ser cosas distintas**, y el por qué queda como **hipótesis, no como explicación**: puede ser que la potencia comprima las colas, donde vive parte de la señal (el umbral útil de TPSA cae en 107 Å²), o que sus parámetros, ajustados en cada pliegue, extrapolen mal en variables de cola pesada. Ninguna de las dos está medida. Lo acotable: comparar Yeo-Johnson con estandarización aísla el paso de potencia, porque `PowerTransformer(standardize=True)` es potencia y luego estandarización, y ese contraste da +0.025 (t = 1.5); el costo está en la potencia, no en el escalado que la acompaña.

El error estándar se corrige como en la [1.7](#d1-7), por Nadeau y Bengio, y la diferencia se toma pareada por pliegue. Se reportan intervalos y no un veredicto de «dentro del ruido»: ese umbral de un error estándar sirve para elegir el menor L —ahí ser laxo es conservador— pero no para afirmar que una diferencia existe, donde apenas es t = 1.

**Lo que esto no cambia todavía.** El Avance 2 seleccionó sus 171 columnas sobre la matriz de Yeo-Johnson y guardó ese artefacto. Cambiar la transformación de trabajo obliga a repetir la selección —los filtros de varianza y correlación operan sobre los valores transformados, así que las 171 pueden no ser las mismas— y a reejecutar el notebook. Queda para el Avance 3, con los modelos afinados. Las dos versiones de la matriz, transformada y sin transformar, siguen guardadas con las mismas columnas.

**Se propone.** Tres modelos con la misma partición:

| Modelo | Por qué | ¿Escalar? |
|:--|:--|:--|
| **Regresión logística regularizada** | Control interpretable exigido por la [C.2](#dc-2) | **Sí** |
| **Random Forest** | Baseline estándar; tolera descriptores correlacionados | No |
| **Gradient boosting** (XGBoost o LightGBM) | Suele ser el más fuerte con descriptores tabulares | No |

Solo la logística necesita escalar, así que cada modelo lleva su canalización y los árboles reciben la matriz sin transformar. La transformación de la logística **sigue sin decidirse**: la validación cruzada no separa no escalar, estandarización y min–max, y solo deja a Yeo-Johnson como la que conviene evitar. Se resuelve en el Avance 3, con los modelos afinados y suficientes evaluaciones para cerrar los intervalos, y arrastra rehacer la selección de la §9. El Avance 2 guarda la matriz filtrada en dos versiones, transformada con Yeo-Johnson y sin transformar, con las mismas columnas. El PCA no se adopta, por explicabilidad, y se guarda ajustado como brazo de comparación. Lo que ejecutó el Avance 2 es una propuesta: la alternativa (no escalar, no reducir dimensión) sigue en pie hasta que se acuerde. SHAP con `TreeExplainer` sirve a los árboles y Chemprop queda como comparación opcional del Avance 4.

#### 1.6 · Naturales y sintéticos: ¿modelos separados u origen como variable? {#d1-6 .abierta}

**Estado:** abierta

> **Pregunta:** ¿Procede entrenar modelos separados, un modelo con el origen como variable, o ambos? ¿Los 1,005 compuestos con análogo natural que difiere solo en estereoquímica cuentan como naturales? ¿Qué rango de TPSA es razonable para naturales neuroactivos?

**Qué pasó.** El 43.1% del conjunto son productos naturales por coincidencia exacta con COCONUT, y cruzan 18.9 puntos menos (52.7% contra 71.7% BBB+). La regla TPSA < 67 Å² y HBD ≤ 1 explica 6.6 puntos de esa brecha; el resto está sin explicar (eflujo, descriptores no medidos o sesgo de qué se ensayó). El diccionario distingue 3,366 naturales exactos, 1,005 análogos que difieren solo en estereoquímica y 3,440 sin equivalente conocido.

**Umbral de TPSA.** El óptimo sube con la diversidad del conjunto: 66.8 Å² (publicado), 66.6 (grupo A), 83.6 (A+B), 101.9 (completo) y 107.0 (entrenamiento). Aún no hay intervalos de confianza.

**Mientras tanto.** Se reporta el desempeño por separado en naturales y sintéticos, y se declara siempre qué definición de «natural» se usó.

#### 1.7 · Tamaño L del vocabulario de Sort & Slice {#d1-7 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Cómo conviene abordar el tamaño del vocabulario: un L fijo (hoy 2048, con 512 como posibilidad en árboles), un L mayor, todas las subestructuras o una frecuencia mínima? ¿Hay subestructuras raras de productos naturales que importen y que un corte por frecuencia perdería?

**Qué pasó.** Sort & Slice conserva las L subestructuras más frecuentes del entrenamiento y cada columna es una sola subestructura. Todos los compuestos tienen el mismo vector de L columnas; lo que cambia es cuáles valen 1 (con L = 2048 un compuesto activa unas 39, el 1.9%). El entrenamiento tiene **11,475 subestructuras distintas**, así que cualquier L hasta ese número se puede llenar; con 2048 se conserva el 18% del vocabulario. El Avance 2 usó L = 2048, igual que el Morgan plegado, y solo midió cobertura. Faltaba saber si ese tamaño es suficiente.

**Qué dice la literatura.** No hay un L óptimo universal. `dablander2024sortslice` probó exactamente L ∈ {512, 1024, 2048, 4096}, dice que las opciones comunes son 1024 o 2048, no recomienda una y encuentra que la ventaja de Sort & Slice sobre el plegado por hash crece cuando L baja. El tamaño se decide con los datos propios.

**Qué se midió.** `scripts/experimento_L_sortslice.py` (resultados en `notebooks/datos/resultados_L_sortslice.csv` y sección 5.1 del [notebook 02](../notebooks/02_Feature_Eng.ipynb)): validación cruzada de 5 pliegues agrupada por andamio y esqueleto de conectividad (los acíclicos, solo por esqueleto, para que los estereoisómeros no se separen), 3 semillas, vocabulario reaprendido en cada pliegue, hiperparámetros fijos y la prueba sin tocar. MCC medio:

| L | Cobertura (entrenamiento / validación) | Regresión logística | Random Forest | XGBoost |
|--:|:--|--:|--:|--:|
| 64 | 36.8% / 33.6% | 0.642 | 0.664 | 0.656 |
| 128 | 46.1% / 39.9% | 0.653 | 0.680 | 0.662 |
| 256 | 56.4% / 45.8% | 0.654 | 0.671 | 0.655 |
| 512 | 67.0% / 55.2% | 0.656 | 0.673 | 0.662 |
| 1024 | 76.8% / 63.8% | 0.666 | 0.678 | 0.664 |
| **2048** | **84.8% / 71.0%** | **0.669** | **0.677** | **0.662** |
| 4096 | 91.9% / 77.2% | 0.670 | 0.691 | 0.674 |

- **Sube despacio y casi todo cabe en el ruido.** El mejor tamaño medido es 4096 en los tres modelos, pero la desviación entre pliegues es de 0.09 a 0.11 de MCC. Pasar de 2048 a 4096 cambia el MCC en +0.001, +0.014 y +0.012, y el AUPRC sobre BBB− en +0.002, +0.004 y +0.006, a cambio de duplicar las columnas.
- **El error estándar hay que corregirlo.** Las 15 evaluaciones (3 semillas × 5 pliegues) comparten datos de entrenamiento, así que no son independientes. Con la corrección de Nadeau y Bengio el error estándar es unas 2.2 veces mayor que el ingenuo; con ella, en MCC y por modelo casi cualquier L desde 128 queda a un error estándar del mejor, y la medición no distingue tamaños; solo el promedio de los tres modelos señala 4096 por poco (0.009 de diferencia contra un error estándar de 0.007). Sin la corrección el criterio sesga hacia L grandes.
- **En AUPRC, 2048 es el menor L dentro del ruido** para la regresión logística y para Random Forest (4096 para XGBoost). Es la métrica que más se parece al uso final: ordenar candidatos.
- **No se probó más allá de 4096**, y la tendencia no se ha aplanado.
- **Corrección respecto a una medición anterior.** Los acíclicos se agrupaban uno por uno, lo que separaba estereoisómeros del mismo compuesto en pliegues distintos (127 filas en 44 esqueletos, 2.3% del entrenamiento). Al corregirlo, el MCC cambió entre −0.022 y +0.012 según el modelo y el tamaño, y el criterio de «menor L dentro del ruido» pasó de 2048 a 4096 con el error estándar ingenuo; con el corregido, la lectura es la de arriba.

**Se propone.** Mantener **L = 2048 como valor de trabajo**, como compromiso: es el menor tamaño que el AUPRC no distingue del mejor en dos de los tres modelos, conserva el 85% de la cobertura y coincide con una de las dos opciones comunes. **4096 es la alternativa** si el número de columnas no importa. La prueba no se usa para elegir L. Límites de esta medición: hiperparámetros sin afinar, una sola partición base y un conjunto de 4,018 esqueletos efectivos.

**Posibilidad: L = 512 si el modelo es XGBoost.** Reduce el espacio de características a una cuarta parte, con menos subestructuras que explicar y menos riesgo de sobreajuste. Lo que respalda la medición: con XGBoost el MCC es el mismo en 512 y en 2048 (0.662 en los dos) y el AUPRC pasa de 0.874 a 0.870. Con Random Forest la pérdida es de 0.004 de MCC y con la regresión logística de 0.013. Lo que no respalda: la cobertura baja de 84.8% a 67.0% en entrenamiento (de 71.0% a 55.2% en validación). Se decide en el Avance 3, con el modelo ya afinado y la misma comparación.

**Experimentos posibles, no realizados.** La tendencia no se había aplanado en 4096, así que quedan por medir, con la misma partición y la misma validación cruzada:

- **L mayor**, por ejemplo 8192, para ver si el desempeño sigue subiendo o se aplana.
- **Todas las subestructuras** del entrenamiento (11,475), sin elegir L. Quita una decisión y mantiene una subestructura por columna, pero con 4,018 esqueletos efectivos añade muchas columnas casi vacías (algunas aparecen en un solo compuesto), diluye la atribución y alarga el entrenamiento.
- **Frecuencia mínima** en lugar de un número de columnas: conservar solo las subestructuras que aparecen en al menos 2, 5, 10 o 20 compuestos de entrenamiento. Sigue siendo un parámetro, pero con un sentido directo: no aprender de lo que se ha visto una o dos veces.
- **Dejar que el modelo elija**: regresión logística con penalización L1 sobre todas las subestructuras, que lleva a cero los coeficientes de las inútiles.

No se han corrido: se prefirió discutir primero el enfoque.

**Para hablarlo con la patrocinadora en la reunión.** Qué se ha hecho hasta ahora, para llegar con el problema planteado:

1. Se midió el desempeño con L entre 64 y 4096 (siete tamaños) en tres modelos, con validación cruzada agrupada por andamio y esqueleto, tres semillas y la prueba sin tocar.
2. Se corrigió un defecto del primer intento (los acíclicos separaban estereoisómeros entre pliegues) y se corrigió el error estándar por la dependencia entre pliegues.
3. Resultado: el MCC casi no distingue tamaños desde ~128; en AUPRC, 2048 es el menor L dentro del ruido en dos de tres modelos; el mejor tamaño medido es 4096, y la tendencia no se ha aplanado.
4. Quedó una propuesta de trabajo (L = 2048), una alternativa (4096) y una posibilidad (512 con XGBoost).

Lo que falta decidir con ella es la estrategia, no el número: si el criterio es el desempeño, la parsimonia para poder explicar, o la relevancia química de las subestructuras raras. Su conocimiento de los productos naturales es lo que puede inclinar la balanza entre una frecuencia mínima y conservarlas todas.

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| S1.1 | Cada fila es una observación independiente | Desmentido | 7,805 filas son 4,018 esqueletos; 131 esqueletos reúnen estereoisómeros con etiquetas distintas (429 filas) | Partición y reportes agrupan por esqueleto |
| S1.2 | Los grupos A–D son una escala de confiabilidad | Desmentido | Ver [1.1](#d1-1). BBB− es 12.1% en A y 92.2% en D | Estratificar, no excluir |
| S1.3 | El umbral de TPSA publicado es una constante | Acotado | Cambia con el subconjunto (ver [1.6](#d1-6)) | Derivarlo solo sobre entrenamiento |
| S1.4 | «Natural» es una categoría limpia | Acotado | Es coincidencia exacta con COCONUT | Declarar la definición usada |
| S1.5 | La brecha natural/sintético es química | Sin comprobar | TPSA y HBD explican solo 6.6 de 18.9 puntos | Reportar por separado |
| S1.6 | Los valores atípicos son alertas, no errores | Asumido | No se recortan ni eliminan | — |
| S1.7 | Mandar los 312 acíclicos a entrenamiento es una regla razonable | Sin comprobar | Es el valor por omisión de `scaffold_split` y no sale de ninguna medición; ninguno entra a validación ni a prueba. Dentro del entrenamiento hay 127 filas en 44 esqueletos compartidos (estereoisómeros) | Escribir y justificar la regla antes del baseline; en la validación cruzada se agrupan por esqueleto de conectividad |
| S1.8 | El conjunto externo de Spielvogel sirve para validar | Desmentido | 154 nombres, sin SMILES ni InChI | Conseguir las estructuras |
| S1.9 | Yeo-Johnson es una buena transformación | Sin comprobar | La matriz guardada la asume; en la regresión logística queda a la par de min–max (0.484 contra 0.481) y una corrida no las distingue | Validación cruzada en el Avance 3; cambiarla obliga a recalcular |
| S1.10 | El PCA no aporta | Sin comprobar | No adoptado por explicabilidad; no mejora de forma concluyente (el bootstrap de la diferencia en Random Forest da −0.008, IC 95% −0.070 a +0.055) ([1.5](#d1-5)) | Mantenerlo como brazo de comparación |
| S1.11 | Las tres características derivadas aportan | Acotado | AUC individual: `tpsa_por_mw` 0.810, `lipo_neta` 0.795, `regla_2p` 0.684 (TPSA: 0.844). `lipo_neta` correlaciona 0.975 con `MolLogP` y lo desplaza | Reevaluar con validación cruzada |
| S1.12 | Todo lo que aprende de los datos se ajusta solo con entrenamiento | Comprobado | Media tras escalar: 0.0000 en entrenamiento, 0.0048 en evaluación | — |
| S1.13 | L = 2048 es un tamaño razonable de vocabulario | Acotado | Medido: el MCC no distingue tamaños desde ~128 y en AUPRC 2048 es el menor L dentro del ruido en dos de tres modelos ([1.7](#d1-7)); falta repetirlo con modelos afinados | Elegir L por modelo en el Avance 3 |

---

## Fase 2 · Actividad {#fase2}

202,647 mediciones (ChEMBL 187,354, NPASS 11,992, CMAUP 3,301) sobre 99,585 esqueletos. Cada fila es una medición: un compuesto contra una proteína, con tipo (IC50, Ki, EC50), relación (`=`, `>`, `<`), valor y unidad. El pChEMBL es −log₁₀ de la concentración molar: 5 equivale a 10 µM y 6 a 1 µM. Solo 1,033 esqueletos están también en el conjunto de permeabilidad, por eso las dos fases casi no se tocan. Todavía no hay matriz de características ni partición. Evidencia: [notebook 01b](../notebooks/01b_EDA_actividad_snc.ipynb) y [datos del proyecto](datos-contenido.md).

### Decisiones

#### 2.5 · La fuente confundida con el etiquetado {#d2-5 .vigente}

**Estado:** vigente · medida el 7 de octubre

> **Pregunta:** ¿Se conocen sesgos de curación entre ChEMBL, NPASS y CMAUP?

**Qué pasó.** NPASS y CMAUP no traen pChEMBL; ChEMBL sí. Si la vía de etiquetado cambia con la fuente, el modelo podría aprender la fuente en vez de la actividad. Medido: el confundido es perfecto por registro (los 15,293 de NPASS y CMAUP tienen cero pChEMBL) pero no por compuesto:

| | Esqueletos |
|:--|--:|
| Solo en ChEMBL | 95,413 |
| **Solo en NPASS/CMAUP** | **1,445** |
| En ambas fuentes | 2,727 |

El 65.4% de los naturales también está en ChEMBL, así que el riesgo se concentra en 1,445 compuestos. Los 2,727 solapados sirven de calibración: donde hay pChEMBL y concentración exacta se puede ajustar el corte de concentración y medir cuánto discrepan. **Pendiente:** hacer esa calibración antes de fijar la [2.3](#d2-3).

### Propuestas

#### 2.1 · Excluir las dianas sin datos {#d2-1 .propuesta .bloquea}

**Estado:** propuesta · bloquea el Avance 3 · se resuelve antes de la [2.2](#d2-2)

> **Pregunta:** ¿Se confirma excluir `GABRG2`, `AIF1`, `GABRB2` y `TARDBP`? ¿Falta o sobra alguna otra diana?

**Qué pasó.** El archivo de dianas tiene 39 filas: 37 dianas por gen y 2 receptores completos (NMDA y GABA-A, sin subunidad). Las etiquetas se curaron a mano desde la farmacología conocida; la categoría principal es la enfermedad con más respaldo, fármaco aprobado primero y luego evidencia genética. Cuatro no tienen datos para un modelo:

| Gen | Diana | Filas |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | **0** |
| `AIF1` | Iba1 (el diccionario lo marca «marcador», sin dirección de efecto) | **0** |
| `GABRB2` | Receptor GABA-A, subunidad β2 | 1 |
| `TARDBP` | TDP-43 | 8 |

**Se propone.** Excluir las cuatro. Primero se fija la lista y después la forma del modelo.

#### 2.2 · Forma del modelo: por diana, por categoría o multitarea {#d2-2 .abierta .bloquea}

**Estado:** abierta · bloquea el Avance 3 · después de la [2.1](#d2-1)

> **Pregunta:** Con la lista ya fijada, ¿un modelo por diana, uno por categoría de enfermedad o uno multitarea con todas? ¿Qué dianas son prioritarias?

**Qué pasó.** Los volúmenes difieren en tres órdenes de magnitud: Alzheimer 52,676 registros, Parkinson 32,372, neuroinflamación 12,331, depresión 10,888, Huntington 153 y ELA 53. Con 53 registros ELA no sostiene un modelo propio; con 52,676 Alzheimer sí. Un modelo multitarea comparte representación entre dianas y es la única forma de incluir las pequeñas, a costa de mezclar señales.

#### 2.3 · Etiquetado por tres vías y criterio de «activo» {#d2-3 .propuesta .revisada .bloquea}

**Estado:** propuesta · revisada el 7 de octubre · bloquea el Avance 3

> **Pregunta:** ¿Qué criterio de «activo» corresponde? ¿Son confiables los inactivos declarados por texto? ¿Cómo se tratan las mediciones censuradas? Si un mismo esqueleto y gen tienen observaciones activas e inactivas, ¿qué ensayos son comparables y qué evidencia tiene prioridad? ¿«Activo» incluye cualquier dirección del efecto (inhibir o activar)?

**Qué pasó.** Primero se planteó «pChEMBL ≥ 5 primario, ≥ 6 como robustez», sin decir cómo etiquetar lo que no tiene pChEMBL. El EDA mostró que el pChEMBL solo existe para ChEMBL: etiquetar solo por él descarta 15,293 registros de NPASS y CMAUP (los naturales), 54,498 mediciones censuradas (`> X nM`) y 29,730 inactivos declarados por texto.

**Se propone.** Tres vías: pChEMBL donde exista; concentración exacta para el resto (recupera 12,809 de los 15,293 naturales); e inactivo declarado para los textos y los censurados con corte ≥ 10 µM. El 10 µM es propuesta del equipo, no decisión ratificada.

**La regla de censura es de la patrocinadora.** Su diccionario, sección 7: un `>` solo sirve como negativo si el límite es igual o mayor que el umbral de «activo». Sobre las 61,001 filas con `>` o `>=`:

| Umbral de «activo» | Negativos seguros | Ambiguos |
|:--|--:|--:|
| 1 µM | 59,859 (98%) | 1,142 |
| 10 µM | 54,419 (89%) | 6,582 |
| 100 µM | 7,474 (12%) | 53,527 |

Esto corrige la propuesta anterior del equipo (10 µM por ser el valor modal): con 1 µM, que equivale a pChEMBL ≥ 6, se recuperan 5,440 negativos seguros más. Además, 33,574 de las 41,291 filas con límite de 10 µM vienen de DrugMatrix, una sola fuente.

**Denominadores.** Las proporciones dependen de la unidad. «Registro etiquetado» es todo el archivo, fenotípicos incluidos; «par esqueleto × gen» es un esqueleto de conectividad contra un gen (`target_gene`):

| Unidad | Umbral | Denominador | Activos | Inactivos | % activos | Razón |
|:---|:--|--:|--:|--:|--:|--:|
| Registro etiquetado | ≥ 5 | 194,086 | 119,835 | 74,251 | 61.7% | 1.6:1 |
| Registro etiquetado | ≥ 6 | 194,086 | 86,238 | 107,848 | 44.4% | 0.8:1 |
| Par esqueleto × gen | ≥ 5 | 71,145 | 50,177 | 20,968 | 70.5% | 2.4:1 |
| Par esqueleto × gen | ≥ 6 | 71,145 | 35,966 | 35,179 | 50.6% | 1.0:1 |

El conteo por par no es todavía el conjunto de entrenamiento: de 114,549 registros con categoría de diana, 109,264 reciben etiqueta; se excluyen 4,810 sin gen y 327 sin esqueleto calculable, y quedan 104,127 agrupables en 71,145 pares. El recuento marca un par como activo si alguna observación lo es, y con esa regla hay 1,810 pares discordantes con ≥ 5 y 2,426 con ≥ 6. El máximo de etiquetas no selecciona la medición más potente.

**Umbral.** Con pChEMBL, ≥ 5 daba 87.1% de activos (6.7:1) y llevó a proponer ≥ 6; con las tres vías la razón baja a 1.6:1 por registro. El sesgo de los registros con pChEMBL es una explicación posible, no demostrada. Se conserva ≥ 5 como primario y ≥ 6 como robustez: el balance de clases no determina el umbral biológico.

#### 2.4 · Los 88,098 registros fenotípicos {#d2-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Van dentro de un modelo específico, aparte o fuera del alcance?

**Qué pasó.** El 43.5% de los registros no corresponde a ninguna diana de la lista; entraron por la ruta `neuronal_assay`: sistemas celulares neuronales donde se midió un efecto sin identificar la proteína responsable. Responden «¿hace algo en un sistema neuronal?», no «¿actúa sobre esta diana?».

**Se propone.** Los 114,549 con categoría de diana alimentan el modelo (el conteo agrupable, 104,127 en 71,145 pares, no es el tamaño final). Los 88,098 fenotípicos se conservan aparte para otra pregunta; no se descartan.

#### 2.6 · La partición de prueba que pudo reservarse {#d2-6 .abierta .bloquea}

**Estado:** abierta · bloquea el Avance 3

> **Pregunta:** ¿El archivo de actividad ya trae una partición de prueba reservada y cómo se hizo?

**Qué pasó.** El archivo se llama `..._Entrenamiento.csv`. El diccionario describe 225,513 filas y el archivo tiene 202,647, el 89.9%: se reservó cerca de un 10%. Si esa partición fue aleatoria, hay compuestos casi idénticos a ambos lados y no es comparable con una por andamio. Si existe, no se construye otra.

#### 2.7 · Partición de la fase 2 {#d2-7 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Hay agrupaciones por familia química o laboratorio de origen que respetar, más allá del andamio?

**Se propone.** El criterio de la fase 1: Bemis-Murcko sobre los 99,585 esqueletos, agrupando por esqueleto de conectividad y verificando que no haya fuga, y además disjunta por fuente si los datos lo permiten. Es la mitigación natural de la [2.5](#d2-5): si entrenamiento y prueba no comparten fuente, un modelo que aprendió la fuente se delata. Depende de la [2.6](#d2-6).

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| S2.1 | «Activo» sobre una proteína es señal de neuroprotección | Sin comprobar | Es una inferencia, casi siempre medida fuera de un organismo; no implica que llegue al cerebro ni que sea selectivo | El modelo solo afirma actividad sobre dianas |
| S2.2 | Una etiqueta describe una clase bajo un umbral y un ensayo, no una propiedad del compuesto | Asumido | El mismo compuesto cambia de clase según la concentración | Se declara el umbral en cada reporte |
| S2.3 | El pChEMBL basta para etiquetar | Desmentido | Solo existe para ChEMBL ([2.3](#d2-3)) | Tres vías |
| S2.4 | Un censurado «> 10 µM» sirve como negativo | Acotado | Solo si el límite es ≥ al umbral de «activo»; concentrado en DrugMatrix | Reportar el desempeño por vía |
| S2.5 | «Activo» tiene una dirección clara | Sin comprobar | Falta verificar si el archivo distingue inhibir de activar | Aclararlo en la [2.3](#d2-3) antes de etiquetar |
| S2.6 | Hay datos para las 39 dianas | Desmentido | Cuatro sin datos suficientes; Alzheimer 52,676 y ELA 53 | Excluir; modelo por categoría o multitarea |
| S2.7 | Un mismo esqueleto y gen tienen etiquetas consistentes | Desmentido en parte | 1,810 pares discordantes con ≥ 5 y 2,426 con ≥ 6 | Regla de resolución reproducible y análisis de sensibilidad |
| S2.8 | El archivo recibido es el conjunto completo | Acotado | 89.9% de lo descrito en el diccionario ([2.6](#d2-6)) | Pedir la partición reservada |
| S2.9 | La fuente no explica la etiqueta | Acotado | Perfecta por registro, rota para el 65.4% de los naturales ([2.5](#d2-5)) | Calibrar con los 2,727 solapados; partición disjunta por fuente |
| S2.10 | La matriz de características sirve para la fase 2 | Desmentido por ahora | Todo el Avance 2 es de la fase 1 | Replicar el pipeline sobre los 99,585 esqueletos |

