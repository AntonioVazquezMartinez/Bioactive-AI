# La ruta del proyecto

Bitácora de lo que se decide en cada fase y de las posibilidades que siguen abiertas. Se alimenta **por fase, no por avance**: la fase 1 es la permeabilidad de la barrera hematoencefálica (BBB+/BBB−) y la fase 2, la actividad neuroprotectora por diana. Ambas parten de los archivos que entregó la patrocinadora el 25 de septiembre. Cada fase tiene sus **decisiones** (lo que se resolvió o se propone), sus **supuestos** (lo que se dio por cierto para avanzar y puede ser falso) y, en cada entrada, la pregunta que queda por resolver.

Nada es *ratificado* hasta que la patrocinadora lo revise; lo que el equipo adopta sigue siendo reversible, y dos decisiones ya se revirtieron al medir. Cuando algo cambia se deja la versión anterior visible. Los términos están en el [glosario](glosario.md).

**Cómo se cierra una entrada.** Pasa a *ratificada* con la minuta de la reunión con la patrocinadora: de ahí se toman las respuestas y se registran aquí, en sus términos y con la fecha. Lo que el equipo adopta por su cuenta se queda en *vigente*, que es reversible y obliga a declararlo como no ratificado en el reporte donde se use.

**El 17 de octubre de 2026 el registro dejó de tener entradas bloqueadas esperando su criterio.** Había siete, y durante semanas fueron el cuello de botella: dos las ratificó ella el 15 de octubre, y las otras cinco —[C.5](#dc-5), [1.6](#d1-6), [2.2](#d2-2), [2.3](#d2-3) y [2.8](#d2-8)— las decidió el equipo. El motivo no es impaciencia: en cada una, esperar costaba más que equivocarse. Tres de ellas resultaron contestables con una medición que nadie había hecho, y en las otras dos la respuesta no cambiaba lo que había que construir. **Cada una dice ahora qué la haría cambiar**, que es la forma de dejarlas abiertas sin dejarlas detenidas, y ninguna se declara ratificada. La [consulta a la patrocinadora](../consulta.qmd) sigue en pie, pero ya no pide definiciones: muestra lo decidido y lo que costó, para que ella corrija lo que quiera corregir.

## Estado de un vistazo

**Marco común** (aplica a las dos fases)

| # | Decisión | Estado |
|:--|:--|:--|
| [C.1](#dc-1) | MCC y AUPRC sobre la clase minoritaria | Vigente |
| [C.2](#dc-2) | Dos métodos de atribución independientes | Vigente |
| [C.3](#dc-3) | Comprobar si combinar las dos predicciones mejora la selección | Propuesta |
| [C.4](#dc-4) | PAINS: aplicarlos a los resultados finales | Propuesta |
| [C.5](#dc-5) | El entregable es una lista priorizada, y el punto de operación va como curva | Vigente |
| [C.6](#dc-6) | Licencia y uso académico de los resultados | Propuesta |
| [C.7](#dc-7) | La ventana terapéutica: potencia contra citotoxicidad | Propuesta |

**Fase 1 · Permeabilidad**

| # | Decisión | Estado |
|:--|:--|:--|
| [1.1](#d1-1) | No filtrar por la columna de grupo A–D | Vigente · revisada |
| [1.2](#d1-2) | Partición por andamio, nunca aleatoria | Vigente |
| [1.3](#d1-3) | Descriptores RDKit más Morgan/ECFP4 | Vigente |
| [1.4](#d1-4) | Las 6 filas con logBB sin clase | Propuesta |
| [1.5](#d1-5) | Tres modelos candidatos; de ahí, si escalar y si reducir dimensión | Propuesta |
| [1.6](#d1-6) | Naturales en la fase 1: evaluar por origen, no entrenar por separado | Vigente |
| [1.7](#d1-7) | Tamaño L de Sort & Slice: 2048 de trabajo; 512 es posible con XGBoost o Random Forest | Propuesta |
| [1.8](#d1-8) | Los 131 esqueletos con etiquetas contradictorias | Abierta |

**Fase 2 · Actividad**

| # | Decisión | Estado |
|:--|:--|:--|
| [2.1](#d2-1) | El alcance: cinco categorías de enfermedad | **Ratificada** · revisada |
| [2.2](#d2-2) | Por diana, con multitarea como comparación | Vigente · revisada |
| [2.3](#d2-3) | Etiquetado por tres vías y criterio de «activo» | Vigente · revisada |
| [2.4](#d2-4) | Los 88,098 registros fenotípicos | Propuesta |
| [2.5](#d2-5) | La fuente confundida con el etiquetado | Vigente · medida |
| [2.6](#d2-6) | La partición de prueba que sí se había reservado | **Ratificada** · revisada |
| [2.7](#d2-7) | Partición de la fase 2 | Vigente · revisada |
| [2.8](#d2-8) | El cruce con COCONUT lo calcula el equipo | Vigente · revisada |
| [2.9](#d2-9) | Clasificar con un corte o predecir la potencia | Propuesta |
| [2.10](#d2-10) | El objetivo se guarda como intervalo, no como etiqueta | Vigente |

Estados: **vigente** (se trabaja sobre ella, y es reversible), **revisada** (se decidió, se midió y cambió; conserva visible la versión superada), **propuesta** (hay recomendación del equipo, aún sin adoptar), **abierta** (sin recomendación) y **ratificada** (la patrocinadora la revisó y la decidió; son la 2.1 y la 2.6, del 15 de octubre de 2026). **Ninguna entrada espera ya su definición para avanzar**, y cada una declara qué la haría cambiar.

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

**Se propone.** Condicionada a que la patrocinadora considere que vale la pena. Cada fase se entrena y evalúa con su protocolo ([1.2](#d1-2), [2.7](#d2-7)), sin reservar nada. Si la patrocinadora lo aprueba, el experimento va en dos pasos:

1. **Con datos solamente, sin modelos.** Cruzar las mediciones reales de los 1,033: permeabilidad medida (BBB+ o BBB−) contra actividad medida, por diana. Se plantea sin umbral: comparar la distribución de la potencia medida entre los BBB+ y los BBB−. Si los BBB− son tan potentes como los BBB+, la permeabilidad cambiaría el orden del ranking; si no, aporta poco. No hay que decidir qué es «activo», porque ese corte depende de la decisión [2.3](#d2-3), abierta, y con ≥ 5 queda 61.7% de activos y con ≥ 6, 44.4%: una lectura del tipo «casi todos los activos son BBB+» podría salir verdadera con un corte y falsa con el otro. Así se puede hacer en cuanto se apruebe, sin esperar a la 2.3 ni a ningún modelo.
2. **Con los modelos ya entrenados.** Medir si la combinación acierta más que cada predicción sola. Como el modelo de la fase 1 habrá visto parte de esos compuestos, se usan predicciones fuera de muestra (validación cruzada agrupada por andamio). Necesita el modelo de actividad, que depende de las etiquetas pendientes de la decisión [2.3](#d2-3), y los modelos afinados de los Avances 3 a 5. Cuántos de los 1,033 caen en la prueba de ambas fases no está medido.

Es exploratorio: los 1,033 no son una muestra representativa (son los compuestos con las dos mediciones, probablemente los más estudiados), así que un buen resultado ahí no se generaliza sin más.

**Criterio de diseño.** Un BBB− no descarta al compuesto: de los 99,585 esqueletos con actividad, el 99% no tiene permeabilidad medida, y filtrar con una predicción sin verificar eliminaría candidatos con actividad documentada. Las dos fases son dos evidencias que se combinan al presentar el ranking, no una cascada.

#### C.4 · PAINS: aplicarlos a los resultados finales {#dc-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿En el ranking final los compuestos con alerta PAINS se marcan o se excluyen? ¿Qué otros filtros de reactividad o toxicidad son aceptables para productos naturales?

**Qué pasó.** 413 compuestos del conjunto de permeabilidad (5.3%) llevan alerta PAINS, 2.1 veces más frecuente en naturales (7.5% contra 3.6%), justo los que se quiere priorizar; con coincidencia por esqueleto son 6.9% contra 3.2%. PAINS no quiere decir inactivo: la actividad medida puede no venir del mecanismo supuesto. Los filtros son de `baell2010pains`, derivados de ~93,000 compuestos en ensayos AlphaScreen de una institución; `capuzzi2017phantom` documenta su baja precisión como predictores de promiscuidad y `baell2018seven` es el propio autor revisando su mal uso. Con datos propios, el compuesto mediano toca 1 diana y el percentil 99, 4; la curcumina aparece contra 32, la quercetina contra 31 y el resveratrol contra 28.

**Se propone.** PAINS no entra al entrenamiento ni a la prueba, para no sesgar contra los naturales. Se aplica a la salida: cada candidato del ranking lleva su alerta y el ranking se reporta con y sin esos compuestos. Nunca se filtra la prueba. El protocolo de tres brazos (sin filtrar, filtrado solo en entrenamiento y evaluación estratificada) puede retomarse si el ranking resulta dominado por alertas, declarándolo antes de correrlo. Una molécula que agrega no falsea un logBB, así que en la fase 1 la alerta es información; en la fase 2 sí condiciona cómo leer el ranking.

#### C.5 · El entregable es una lista priorizada, y el punto de operación se entrega como curva {#dc-5 .vigente}

**Estado:** vigente · decidida por el equipo el 17 de octubre de 2026

**Qué se decidió.** El entregable es **una lista de candidatos priorizados**, con la marca de origen natural, la alerta PAINS de la [C.4](#dc-4) y la diana predicha. Y el punto de operación **no se fija**: se entrega la curva de precisión contra profundidad, con un corte **sugerido** en los veinte primeros compuestos, que es lo que un laboratorio puede ensayar en un semestre.

**Qué pasó.** El umbral de decisión depende de qué error es más caro, y eso no lo decide la estadística: un falso activo manda al laboratorio a ensayar algo que no funciona, y un falso inactivo descarta un candidato real sin que nadie se entere. Las métricas están fijadas ([C.1](#dc-1)); el punto de operación era lo que faltaba.

**Por qué se decide y no se pregunta.** Era la única entrada que el equipo no podía ni medir ni aproximar, y por eso se planteó como una elección entre dos listas concretas. Pero preguntarla tenía un supuesto escondido: que hay que elegir **un** punto de operación. No hay que elegirlo. Entregando la curva, mover el corte no cuesta reentrenar nada: es leer otra fila de la misma tabla. Así la pregunta deja de bloquear y se convierte en algo que ella puede ajustar cuando vea los resultados, que es cuando de verdad se puede contestar.

**Qué arrastra.** La forma del entregable define buena parte de la [C.6](#dc-6) y qué tan agregado conviene que sea el modelo de la [2.2](#d2-2).

**Qué lo cambiaría.** Que pida un modelo ejecutable en vez de una lista —lo que arrastra empaquetado y la [C.6](#dc-6)— o que el laboratorio tenga una capacidad de ensayo muy distinta de veinte compuestos, que mueve el corte sugerido pero no la forma del entregable.

**El caso que hay que saber presentar:** un compuesto con BBB− predicho y actividad documentada. No se descarta, porque la [1.1 del planteamiento](#comun) trata las dos fases como evidencia paralela y no como cascada: aparece en la lista con las dos predicciones visibles y la advertencia de que la permeabilidad es predicha y no medida.

#### C.6 · Licencia y uso académico de los resultados {#dc-6 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Se autoriza publicar los resultados, y qué datos derivados, bajo uso académico no comercial? ¿Hay aspiraciones comerciales? NPASS (CC BY-NC) lo impediría.

**Esta entrada va aparte de las demás.** No es un criterio técnico sino administrativo, y la mitad de lo que falta no depende de ella sino del departamento y del Tec: propiedad intelectual, orden de autoría, foro. Tratarla en la misma sesión que el criterio de «activo» hace que ninguna de las dos se cierre. Se plantea por escrito y con tiempo, no en la reunión donde se discuten los criterios técnicos.

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

#### C.7 · La ventana terapéutica: potencia contra citotoxicidad {#dc-7 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿El ranking final debe considerar la citotoxicidad, y con qué dato? ¿Tiene mediciones de viabilidad celular de los compuestos que le interesan?

**Qué pasó.** El proyecto predice potencia y permeabilidad, y con eso ordena candidatos. Falta el otro extremo: un compuesto no sirve por ser potente, sirve porque su concentración efectiva está lejos de la tóxica. Eso es la **ventana terapéutica**, y hoy no se puede calcular:

| | |
|:--|--:|
| Compuestos con medición de eficacia | 85,685 |
| Compuestos con medición citotóxica | 674 |
| **Con ambas** | **203** |

Son 925 filas con desenlace citotóxico (`GI50`, `TGI`, `CC50`, `ID50`, `MIC`, `MNTD`) y 483 con `assay_type` de toxicidad, de 202,647. El eje no existe en este archivo.

**Por qué importa más aquí que en un proyecto cualquiera.** Muchos productos naturales son potentes **precisamente porque son citotóxicos**: así los usa la planta. Y el proyecto ya lo midió sin proponérselo en la [C.4](#dc-4): los naturales llevan alerta PAINS 2.1 veces más seguido, y la curcumina aparece contra 32 dianas, la quercetina contra 31 y el resveratrol contra 28. Un ranking de naturales que ignore la citotoxicidad va a poner arriba justo a los promiscuos tóxicos. No es un riesgo teórico, es el resultado esperado dado lo que ya se midió.

**Se propone.** **No modelar la toxicidad**, sino usarla como **bandera sobre el ranking de salida**, con el mismo patrón que la [C.4](#dc-4) ya adoptó para los PAINS: no entra al entrenamiento ni a la prueba, acompaña a cada candidato y el ranking se reporta con y sin los marcados. Modelarla exigiría armonizar líneas celulares y desenlaces distintos, que es el mismo problema de comparabilidad de la [2.3](#d2-3) en un eje nuevo.

**De dónde saldría el dato, en orden de costo.** Primero el volcado de ChEMBL 37, que ya es la alternativa declarada de la fase 2: la citotoxicidad de estos mismos compuestos está ahí y el recorte que recibimos la filtró, así que es el mejor solapamiento posible y una sola procedencia. Después **Tox21**, público y de dominio público vía PubChem BioAssay, que incluye contra-tamices de viabilidad y ensayos de la vía Nrf2/ARE —la diana de estrés oxidativo—, con la duda de cuánto solapa su biblioteca de químicos ambientales con nuestros naturales, que se mide antes de invertir. **ToxCast** al final, por volumen.

**Si no se resuelve:** el ranking se entrega declarando que ordena por potencia y permeabilidad, y que no distingue un compuesto selectivo de uno citotóxico. Eso cambia qué significa el entregable, así que toca la [C.3](#dc-3) y la [C.5](#dc-5).

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| SC.1 | La estructura molecular basta para predecir permeabilidad y actividad | Sin comprobar | Es la hipótesis de trabajo | Se reporta como resultado: «sin patrón aprendible» es válido |
| SC.2 | Los 1,033 compuestos comunes bastan para medir la combinación de las dos predicciones | Sin comprobar | No se ha medido cuántos caen en la prueba de ambas fases ([C.3](#dc-3)) | Usar predicciones fuera de muestra o reportar que no alcanza |

---

## Fase 1 · Permeabilidad {#fase1}

El conjunto tiene 7,811 filas, 7,805 con clase, que son 4,018 esqueletos de conectividad: ese es el tamaño efectivo. Evidencia: [reporte del Avance 1](reportes/README.md), [notebook 01](../notebooks/01_EDA.ipynb), [notebook 02](../notebooks/02_Feature_Eng.ipynb) (la matriz de 151 columnas y la partición) y [notebook 03](../notebooks/03_Baseline.ipynb) (el modelo de referencia).

### Decisiones

#### 1.1 · No filtrar por la columna de grupo A–D {#d1-1 .vigente .revisada}

**Estado:** vigente · revisada el 4 de octubre

**Qué pasó.** [02 · Datasets BBB](referencias/02-datasets-bbb.md) leía las categorías A–D de B3DB como escala de confiabilidad y proponía entrenar con A+B. El EDA del Avance 1 lo desmintió: el grupo D tiene mediana de 3 referencias contra 1 del C; ningún registro duplicado tiene etiquetas contradictorias; y la columna está confundida con la etiqueta, porque filtrar a A+B baja la clase minoritaria de 36.5% a 27.0%. Esa recomendación sigue visible en el documento, marcada como superada.

**Se decidió.** La columna describe y estratifica, nunca excluye. El entrenamiento pasa de 4,679 a 7,805 compuestos (+67%). Las caídas de AUC por partición por andamio son mayores que las medidas sobre A+B (logP pierde 0.198 contra 0.175) porque el conjunto es más diverso: el número anterior estaba inflado.

#### 1.2 · Partición por andamio, nunca aleatoria {#d1-2 .vigente}

**Estado:** vigente

> **Pregunta:** ¿Hay razón experimental para separar también por laboratorio o por fuente, más allá del andamio?

**El grupo es el andamio unido al esqueleto de conectividad, y la diferencia no es cosmética.** Un esqueleto puede aparecer con andamios distintos —un tautómero que cambia el anillo—, así que agrupar solo por andamio pone estereoisómeros del mismo compuesto a los dos lados del pliegue. Medido en el Avance 3 sobre la fase 1:

| Agrupamiento | Grupos | AUROC | MCC |
|:--|--:|:--|--:|
| Andamio ∪ esqueleto | 1,048 | 0.936 [0.912, 0.955] | 0.699 |
| Solo andamio | 2,239 | **0.959** [0.941, 0.973] | **0.769** |

Las dos filas son del bosque aleatorio con una semilla, celda 10 del [notebook 03](../notebooks/03_Baseline.ipynb), sobre la matriz de 151 columnas. (Con la matriz anterior, de 171, daban 0.937 / 0.705 y 0.959 / 0.767: la diferencia entre agrupamientos no se mueve.)

**2.2 puntos de AUROC y 7.1 de MCC.** Lo que sigue compara, en cada métrica, **el par de modelos más lejano de esa métrica**, que no es el mismo par: en MCC son el boosting y la logística (0.0153; el bosque contra la logística da 0.0130) y en AUROC el bosque y la logística. Comparar siempre el mismo par subestimaría la distancia entre familias en una de las dos.

En MCC la elección de modelo mueve 1.5 puntos entre la logística y el boosting, así que el criterio de agrupamiento pesa casi cinco veces más. **En AUROC no**, y la versión anterior de esta entrada decía que sí: con el mismo estimador —una semilla, predicciones fuera de pliegue, bootstrap de grupos— el agrupamiento mueve 0.0223 y la distancia entre el bosque y la logística 0.0225. La afirmación salía de comparar los 2.2 puntos de ese estimador contra el «menos de 2» del promedio de 15 pliegues, que es otro. Con cualquiera de los dos se sostiene lo que de verdad importa: **una cifra que no diga cómo agrupó no se puede comparar** con las de este registro. El criterio vive en `grupos_cv`, en `src/data_prep/splits.py`, y lo usan las dos fases.

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

> **Pregunta:** ¿Se prioriza la explicabilidad (matriz de 151 columnas, cada una una propiedad o subestructura) sobre la reducción de dimensión con PCA, que no se traduce a subestructuras?

**Medido en el Avance 3, con el arnés agrupado y las tres como canalizaciones.** Ninguna gana: los intervalos del 95% se solapan. **Tampoco se distingue la logística**, aunque quede por debajo en los 15 pliegues: su intervalo se solapa con el del bosque en más de lo que separa a las estimaciones puntuales. Una versión anterior de esta entrada la daba por distinguible, que es aplicar dos criterios opuestos a la misma evidencia en dos frases seguidas. Separarlas pediría el intervalo de la **diferencia pareada**, no los de cada modelo por separado, y no está medido.

| Canalización | AUROC | IC 95% | MCC |
|:--|--:|:--|--:|
| Boosting por histogramas | 0.938 | [0.915, 0.956] | 0.702 |
| Bosque aleatorio | 0.937 | [0.913, 0.955] | 0.700 |
| Regresión logística (min–max) | 0.918 | [0.893, 0.939] | 0.687 |

El AUROC es el de las predicciones fuera de pliegue promediadas entre las tres semillas, con intervalo por bootstrap de grupos; el MCC es el promedio de las 15 evaluaciones. La celda 8 del notebook recalcula el intervalo con una sola semilla y da cifras algo distintas (0.936, 0.936 y 0.914): es otro estimador, no otra medición.

Con una sola configuración por familia **no se declara ganador**, que es el error que esta misma entrada ya cometió una vez con el escalado y tuvo que retirar. Afinar es del Avance 4. **Y el orden entre las dos basadas en árboles se invirtió al pasar de la matriz de 171 columnas a la de 151** —antes el MCC más alto era del bosque (0.7017 contra 0.6986), ahora del boosting (0.7019 contra 0.6996)— por diferencias de dos o tres milésimas: es el mismo argumento, visto dos veces. Las cifras salen de `scripts/experimento_baseline.py` y del [notebook 03](../notebooks/03_Baseline.ipynb); la corrida está en `experimentos/2026-10-18-artemio-1.5-baseline-permeabilidad-descriptores/` y la anterior, sobre las 171 columnas, en `experimentos/2026-10-18-artemio-1.5-baseline-permeabilidad-171col/`.

**Los tres sobreajustan de forma muy distinta, y eso dice dónde buscar en el Avance 4.** Medido con la misma partición, la misma métrica sobre el pliegue de ajuste y sobre el de evaluación (`scripts/experimento_rubrica3.py`, corrida `experimentos/2026-10-18-artemio-1.5-rubrica3/`):

| Canalización | MCC ajuste | MCC validación | Brecha | AUROC ajuste | AUROC validación |
|:--|--:|--:|--:|--:|--:|
| Regresión logística | 0.739 | 0.687 | **0.052** | 0.943 | 0.913 |
| Bosque aleatorio | 0.955 | 0.698 | 0.256 | 0.998 | 0.933 |
| Boosting por histogramas | 0.972 | 0.702 | 0.270 | 0.999 | 0.930 |

Y la curva de aprendizaje —submuestreando **por grupo**, no por fila, porque tomar filas al azar partiría andamios y mediría cuánto ayuda ver más análogos en vez de más estructuras— separa los dos diagnósticos: en los árboles la línea de ajuste es plana desde 168 estructuras; en la logística baja de 0.81 a 0.74 y se acerca a la de validación. **La brecha de los árboles sí se cierra** —de 0.327 a 0.270 en boosting y de 0.299 a 0.256 en el bosque, más que la brecha entera de la logística, que es 0.052— pero por el lado equivocado: no porque el ajuste baje, que es plano, sino porque la validación sube. Quintuplicar las estructuras quitó una quinta parte de la brecha, así que cerrarla por este camino pediría órdenes de magnitud más compuestos. Las tres líneas de validación suben cada vez menos, y el último 20% de estructuras aporta menos de 0.01 de MCC en los tres. **Más compuestos del mismo tipo ayudarían poco**: lo que falta es regularizar los árboles.

**El piso es 0.000 de MCC, 0.500 de AUROC y 0.350 de AUPRC sobre la minoritaria.** El tercero importa justamente porque no es cero: el 0.88 del baseline se lee contra 0.350, no contra 0. No hay desempeño histórico con el que comparar —la patrocinadora no tenía modelo previo— así que el piso lo ponen los clasificadores triviales con la misma partición agrupada. Importa decirlo porque con 65.0% de BBB+ un clasificador que diga siempre «permeable» acierta dos de cada tres veces, y esa exactitud del 65% parecería un resultado. **El desempeño mínimo que el Avance 4 tiene que superar queda fijado en el 0.70 de MCC y el 0.93 de AUROC de este baseline**, medido con esta partición y estas semillas.

**Dos métodos de atribución coinciden en 11 de sus 15 primeras características**, que es lo que la [C.2](#dc-2) exige antes de afirmar nada estructural: la impureza del bosque pone a TPSA arriba, la permutación sobre el pliegue de evaluación pone a `fr_lactam` y `fr_COO`. En la intersección están TPSA, donadores de hidrógeno y `MolLogP`, y los coeficientes de la logística les dan el signo esperado —TPSA −1.42, donadores −2.43—, de modo que la regla de los dos parámetros sale de tres caminos independientes en vez de citarse. **24 de las 151 columnas no dañan al modelo al permutarlas**, y la cuenta lleva su ruido: en solo 4 de esas 24 la media supera en magnitud a su propia desviación entre repeticiones, y en toda la matriz solo 75 de 151. El orden de la cola no está medido; el de la cabeza sí —`fr_lactam` da 0.0058 ± 0.0012— y es de donde sale la intersección. Retirarlas es candidato de poda para el Avance 4, no una decisión que una sola configuración pueda tomar.

**Las 151 columnas rinden como las 171.** Mismas particiones, mismas semillas y la misma máquina: la diferencia pareada por pliegue va de −0.006 a +0.003 de MCC y de −0.001 a 0.000 de AUROC, con error estándar del mismo tamaño que la diferencia. Veinte columnas menos no cuestan desempeño, que es lo que hacía falta comprobar antes de adoptar la matriz nueva.

**La selección de características se ajustó antes de partir, y queda como limitación declarada.** Las 151 columnas salieron del notebook 02 mirando todo el entrenamiento, y la validación cruzada del Avance 3 reparte esas mismas filas entre pliegues: cada pliegue de evaluación contiene filas cuyas etiquetas ayudaron a elegir las columnas. El filtro de casi constancia y el de Spearman son casi insensibles a la etiqueta, pero el desempate entre dos columnas correlacionadas usa la F de ANOVA contra la etiqueta, así que la fuga existe aunque sea pequeña. Es **la misma clase de fuga** que la decisión de abajo evita al no usar la matriz transformada, y se declara en vez de callarse. **Qué la cerraría:** meter la selección dentro de la canalización, que la reajustaría por pliegue, y reejecutar — con lo que las cifras de esta entrada cambiarían en una cantidad hoy desconocida. Es trabajo del Avance 4.

**Y el baseline usa la matriz sin transformar.** La guardada trae Yeo-Johnson ajustado sobre todas las filas de entrenamiento, así que usarla en validación cruzada mete en cada pliegue de evaluación información ajustada con él. Se midió la diferencia y es pequeña —alrededor de 0.001 de AUROC—, pero no se sabía hasta medirla. El escalado va dentro de la canalización, que se reajusta por pliegue.

**Qué pasó.** El Avance 2 pedía escalamiento y selección de características. Escalar no es una decisión independiente: depende del modelo. Medido en el notebook 02: 120 pares de descriptores con correlación mayor a 0.95; Yeo-Johnson corrige mejor la asimetría, de 106 a 66 descriptores muy asimétricos. La selección dejó **151 de 206** descriptores: 24 casi constantes —un valor reúne el 99% del entrenamiento— y 31 redundantes por correlación de Spearman. El brazo de PCA al 95% se midió en la versión anterior del notebook (85 componentes; MCC 0.512 contra 0.500 con la logística, 0.558 contra 0.566 con Random Forest, AUROC 0.872 contra 0.916, con el bootstrap de la diferencia cruzando el cero) y **ya no se reejecuta**: el notebook vigente conserva el PCA solo como vista del espacio químico, porque la decisión se sostiene por explicabilidad y no por esa diferencia. Esas cuatro cifras son de la corrida anterior, no de la vigente.

**Versión superada (7 de octubre), y qué la cambió.** La versión anterior de esta entrada decía que Yeo-Johnson quedaba *a la par* de min–max en la regresión logística, con MCC 0.484 contra 0.481. Esa comparación era de **una sola corrida sobre una sola partición de validación**, y su orden cambiaba con el entorno: min–max daba 0.481 en Linux, 0.489 en macOS con Python 3.12 y 0.497 en macOS con Python 3.14, contra un 0.484 estable de Yeo-Johnson. La conclusión dependía de quién ejecutara.

`scripts/experimento_escalado.py` la repite con validación cruzada de 5 pliegues agrupada por andamio y esqueleto de conectividad, 3 semillas, la transformación **reajustada dentro de cada pliegue** y la prueba sin tocar (resultados en `notebooks/datos/resultados_escalado.csv`, sección 8.2 del [notebook 02](../notebooks/02_Feature_Eng.ipynb)). MCC medio y AUPRC sobre BBB−:

| Transformación | LogReg, MCC | LogReg-C, MCC | `C` elegido | LogReg, AUPRC | RF, MCC |
|:--|--:|--:|--:|--:|--:|
| sin escalar | 0.687 | — | — | 0.867 | 0.704 |
| estandarización | 0.690 | **0.699** | 0.01 | 0.864 | 0.705 |
| min-max | 0.695 | 0.695 | 1.00 | 0.878 | 0.704 |
| Yeo-Johnson | 0.665 | 0.695 | 0.01 | 0.862 | 0.705 |

`LogReg` usa el mismo `C = 1` para las cuatro; `LogReg-C` deja que cada transformación elija el suyo por validación cruzada interna. El AUPRC de la columna `LogReg-C` va de 0.874 a 0.877, y el del Random Forest es 0.901 con las cuatro.

- **Ningún intervalo del 95% excluye el cero.** Con quince evaluaciones que comparten datos de entrenamiento, la medición no establece que una transformación supere a otra. Con el mismo `C` la diferencia mayor —min–max contra Yeo-Johnson en la regresión logística— es de 0.030 de MCC con un error estándar corregido de 0.019: t = 1.6, intervalo [−0.010, +0.071]; con el `C` propio de cada una la mayor es de 0.004, t = 0.5. Lo que esta medición aporta es sobre todo **la cota**: la incertidumbre es mayor que cualquier diferencia entre transformaciones.
- **En Random Forest la transformación es irrelevante, y eso sí queda establecido**: diferencias de 0.000 a 0.001 con intervalos de ±0.002 a ±0.005, tan estrechos que descartan cualquier efecto que importe. La invariancia de los árboles deja de ser solo un argumento.
- **Sin escalar, la regresión logística no converge**, y eso es lo que justifica escalar. Agota las 3,000 iteraciones de `lbfgs` en los 15 pliegues y avisa de no haber convergido en los 15; con cualquiera de las tres transformaciones converge sin aviso, en 53 iteraciones con min–max y 137 a 144 con las otras dos. Su MCC de 0.687 no es el desempeño de «no escalar»: es donde se detuvo el optimizador al agotar su presupuesto, así que esa fila no es comparable con el resto. El tiempo (0.437 s contra 0.007 s) es la consecuencia visible; las iteraciones y el aviso son la prueba. El Random Forest tarda lo mismo con las cuatro, lo que descarta que los datos sean más difíciles sin escalar.
- **El escalado no arregla el condicionamiento**, y conviene no atribuírselo: el número de condición de la matriz va de 5.9e+17 a 1.2e+21 con las cuatro transformaciones. Viene de las columnas casi colineales —120 pares con |r| > 0.95— y lo trata la selección, no el escalado.
- **La desventaja de Yeo-Johnson era del `C`, no de la transformación**, y eso lo cambió la revisión del Avance 2. Con el mismo `C = 1` para las cuatro, Yeo-Johnson queda 0.030 de MCC por debajo de min–max y pierde en 12 de los 15 pliegues; con el `C` que cada transformación elige para sí, **las dos empatan en 0.695** y la mejor pasa a ser estandarización por 0.004 (t = 0.5). Los `C` elegidos están a dos órdenes de magnitud de distancia —0.01 con estandarización y con Yeo-Johnson, 1.0 con min–max—, así que un solo `C` compara la transformación y la regularización a la vez, y el valor fijado resultó ser el que min–max prefiere.
- **Versión superada (12 de octubre), y qué la cambió.** Esta entrada decía que Yeo-Johnson era «consistentemente la peor» y proponía como hipótesis que la potencia comprimiera las colas, donde vive parte de la señal. El apoyo de esa hipótesis era que comparar Yeo-Johnson con estandarización aísla el paso de potencia —`PowerTransformer(standardize=True)` es potencia y luego estandarización— y daba +0.025 (t = 1.5). Con el `C` propio ese contraste cae a +0.004: **no había efecto que explicar**. Es el mismo modo de fallar que la 2.3 ya tuvo: una explicación construida sobre un número antes de comprobar que el número mide lo que parece. Queda el hecho sin consecuencia: Yeo-Johnson corrige mejor la asimetría, de 106 a 66 descriptores muy asimétricos, y eso no se traduce en mejor predicción.

El error estándar se corrige como en la [1.7](#d1-7), por Nadeau y Bengio, y la diferencia se toma pareada por pliegue. Se reportan intervalos y no un veredicto de «dentro del ruido»: ese umbral de un error estándar sirve para elegir el menor L —ahí ser laxo es conservador— pero no para afirmar que una diferencia existe, donde apenas es t = 1.

**Se propone.** Tres modelos con la misma partición:

| Modelo | Por qué | ¿Escalar? |
|:--|:--|:--|
| **Regresión logística regularizada** | Control interpretable exigido por la [C.2](#dc-2) | **Sí** |
| **Random Forest** | Baseline estándar; tolera descriptores correlacionados | No |
| **Gradient boosting** (XGBoost o LightGBM) | Suele ser el más fuerte con descriptores tabulares | No |

Solo la logística necesita escalar, así que cada modelo lleva su canalización y los árboles reciben la matriz sin transformar. Para la logística **se propone escalar**, porque sin escalar no converge, y **min–max como opción de partida**, no como conclusión: entre las tres formas de escalar la medición no da base para elegir, y la alternativa de no escalar deja un modelo que agotó sus iteraciones. Ya no hay un motivo medido para evitar Yeo-Johnson: lo había mientras el `C` era el mismo para todas, y con el suyo la diferencia desaparece. **Cuál de las tres se adopta lo cierra el equipo**, no la patrocinadora: la medición no las distingue en desempeño y la razón para escalar resultó ser la convergencia, así que no queda un criterio que dependa de su conocimiento del dominio. Lo que sí depende de ella es la pregunta de arriba, entre explicabilidad y reducción de dimensión, porque eso se decide por lo que quiere poder leer en el resultado y no por una cifra. Se resuelve en el Avance 3, con los modelos afinados y suficientes evaluaciones para cerrar los intervalos. El Avance 2 guarda la matriz filtrada en dos versiones, transformada con Yeo-Johnson y sin transformar, con las mismas columnas; y **cambiar la transformación de trabajo ya no obliga a repetir la selección**: la §9 filtra por valor modal y por correlación de Spearman sobre los valores crudos, y el notebook comprueba que las 151 columnas son las mismas con estandarización, con min–max y con Yeo-Johnson. El PCA no se adopta, por explicabilidad, y **tampoco se guarda**: el notebook lo conserva solo como vista del espacio químico. Lo que ejecutó el Avance 2 es una propuesta: la alternativa (no escalar, no reducir dimensión) sigue en pie hasta que se acuerde. SHAP con `TreeExplainer` sirve a los árboles y Chemprop queda como comparación opcional del Avance 4.

#### 1.6 · Naturales en la fase 1: evaluar por origen, no entrenar por separado {#d1-6 .vigente}

**Estado:** vigente · decidida por el equipo el 17 de octubre de 2026

**Qué se decidió.** Un solo modelo, con el desempeño reportado por origen **dentro de cada grupo A–D** y no solo en el global. La causa de la brecha —curación o química— queda como **limitación declarada**, no como pregunta abierta.

**Por qué se decide y no se pregunta.** La pregunta era si existe una razón de curación que explique que los naturales crucen igual en el grupo A y 21 y 17 puntos menos en B y C. Solo ella podría saberlo, pero la respuesta **no cambia lo que hay que hacer**: con cualquiera de las dos lecturas la decisión es la misma —un modelo, evaluado por origen dentro de cada grupo— porque es esa evaluación la que distingue las dos explicaciones. Si el modelo rinde peor en naturales solo en B y C, está aprendiendo ruido de curación; si falla también en A, es química. La medición contesta lo que la pregunta pedía.

**Qué lo cambiaría.** Que la evaluación por origen muestre que el modelo falla en naturales dentro del grupo A, que es el que tiene logBB medido. Ahí sí habría que considerar entrenar aparte.

**Dos cosas que quedan como supuesto declarado,** por si alguien las necesita: los 1,005 compuestos con análogo natural que difiere solo en estereoquímica **no** cuentan como naturales, porque la definición que sostiene el hallazgo del Avance 1 es la coincidencia exacta con COCONUT; y no se fija un rango de TPSA propio para naturales, porque el óptimo ya se midió y sube con la diversidad del conjunto.

**Qué pasó.** El archivo de la patrocinadora marca como natural lo que coincide exactamente con COCONUT (columna `coconut_id_exact_match`): 3,366 compuestos, el 43.1% de los 7,805 con clase. Lo demás no es «sintético»: el diccionario distingue 3,366 naturales exactos, 1,005 análogos que difieren solo en estereoquímica y 3,440 sin equivalente natural conocido.

**Los tres orígenes cruzan distinto** (sección 5 del [notebook 01](../notebooks/01_EDA.ipynb), revisada el 19 de octubre): naturales exactos 52.7% BBB+ [49.7, 55.8], análogos estereoquímicos 39.7% [34.6, 44.8] y sin equivalente natural 81.0% [79.1, 82.8], intervalos bootstrap por esqueleto de conectividad que no se solapan (los de Wilson, que tratan como independientes a los estereoisómeros, son entre 1.4 y 1.8 veces más angostos). La brecha entre naturales y compuestos sin equivalente es de **28.3 puntos**. *Versión superada:* el Avance 1 juntaba análogos y compuestos sin equivalente en un grupo «sintético» y reportaba 18.9 puntos (52.7% contra 71.7%). Ese grupo no era sintético —más de una quinta parte (1,003 de los 4,439 con clase) son estereoisómeros de un natural, que cruzan todavía menos— y diluía la brecha. **La regla TPSA/HBD no la explica por completo.** Entre los compuestos que la cumplen, que en TPSA y HBD son casi iguales en los tres orígenes (mediana de TPSA de 37.3, 37.3 y 36.7 Å²), los naturales cruzan 80.9% contra 90.9%. Entre los que no la cumplen la diferencia es mayor (37.8% contra 72.6%), pero ese estrato no es comparable, porque los naturales que no la cumplen son más polares (mediana de TPSA de 108.4 contra 86.5 Å²). Eso descarta que la regla de dos parámetros baste, no que la química explique la brecha.

**La brecha no es uniforme.** Repartida por el grupo de B3DB, casi no existe en el grupo A y aparece en B y C. Lo que distingue a los grupos en el archivo es solo esto: todas las filas de A, y solo ellas, traen `logBB` (1,052 de 1,058); todas las de B, y solo ellas, traen `b3db_threshold` = −1, el valor del corte de logBB de la clase, sin el logBB; C y D no traen ninguno de los dos. *Versión superada:* esta entrada decía que en B y C «la etiqueta viene de una clasificación publicada». Eso no está en el archivo: B3DB no publica el criterio completo de asignación, y la columna de B contradice que B y C se etiquetaran igual. La revisión independiente del notebook 01 lo encontró el 19 de octubre.

| Grupo de B3DB | No natural (BBB+) | Natural (BBB+) | Diferencia (puntos), IC 95% |
|:--|--:|--:|:--|
| A (con logBB medido) | 87.6% (n = 644) | 88.4% (n = 414) | −0.8 [−4.8, +3.2] |
| B | 77.2% (n = 2,166) | 55.9% (n = 1,455) | +21.4 [+18.3, +24.5] |
| C | 58.1% (n = 1,624) | 40.9% (n = 1,451) | +17.2 [+13.7, +20.7] |

Con los tres orígenes por separado (natural exacto, análogo y sin equivalente) el patrón es el mismo: 88.4%, 86.6% y 87.7% en el grupo A; 55.9%, 43.5% y 83.6% en el B; 40.9%, 30.7% y 73.0% en el C (notebook 01, sección 5).

En el grupo A la brecha no es solo «casi inexistente»: queda **acotada a unos ±5 puntos**, lo que excluye cualquier cosa parecida a los 19 globales; en B y C es grande y en la dirección contraria. El grupo D (n = 5 y 46) no permite concluir. Esto es descriptivo y no prueba la causa. Caben dos lecturas que estos datos no distinguen: que la brecha refleje en parte de dónde viene la etiqueta, o un **efecto techo**, porque el grupo A es 88% BBB+ y con casi todo del mismo lado queda poco margen para que los orígenes difieran. Quedan además el eflujo, descriptores no medidos o el sesgo de qué se ensayó. *Versión superada:* esta entrada comparaba la proporción de naturales que cumple la regla TPSA/HBD (6.6 puntos menos, 34.6% contra 41.2%) con la diferencia en la etiqueta. Son dos diferencias de proporciones que no se descomponen una en otra (#85), y la comparación correcta es la de arriba, a igual cumplimiento de la regla.

**Se propone.** Un solo modelo, con el desempeño reportado por separado en naturales y en el resto y declarando siempre qué definición de «natural» se usó. No entrenar por separado: la permeabilidad depende de la estructura y no del origen, habría 3,366 compuestos de un lado y 4,439 del otro, y el segundo grupo mezcla análogos, fármacos y moléculas que simplemente no están en COCONUT. Tampoco el origen como variable, porque en parte sería una pista de la procedencia de la etiqueta. **La evaluación por origen se hace también dentro de cada grupo A, B y C**, no solo en el global: es la misma lógica de la [1.1](#d1-1), que usa A–D para estratificar y nunca para excluir, y es la medición que distingue las dos explicaciones. Si un modelo rinde peor en naturales solo en B y C, eso apunta a ruido de curación más que a química, siempre leído contra la tasa base de cada grupo por el efecto techo de A. Se revisa la propuesta solo si la evaluación por origen muestra que el modelo falla en naturales.

**Umbral de TPSA.** El óptimo sube con la diversidad del conjunto: 66.8 Å² (publicado), 66.6 (grupo A), 83.6 (A+B), 101.9 (completo) y 107.0 (entrenamiento). Los intervalos bootstrap por esqueleto (§4.3 del notebook 01, 1,000 remuestras) son anchos: [57.3, 83.6] en el grupo A, [81.5, 107.2] en A+B y [81.5, 109.5] en el completo. Lo único que distinguen es el grupo A, cuyo punto queda fuera de los otros dos.

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

#### 1.8 · Los 131 esqueletos con etiquetas contradictorias {#d1-8 .abierta}

**Estado:** abierta

> **Pregunta:** 131 esqueletos de conectividad reúnen estereoisómeros con clases BBB distintas. ¿Es una diferencia real de permeabilidad entre formas estereoquímicas, o son etiquetas que vienen de ensayos que no deberían compararse? En 42 de los 131 hay una tercera posibilidad y conviene descartarla primero: el nombre de la fila también se usa en el archivo para otra estructura, así que puede llevar la etiqueta de otro compuesto. Si es lo primero, ¿vale la pena conservar la estereoquímica en la representación?

**Qué pasó.** Las 7,805 filas con clase son 4,018 esqueletos de conectividad, y en 131 de ellos (429 filas, el 5.5% del conjunto) dos estereoisómeros del mismo compuesto llevan etiquetas opuestas. La partición los mantiene juntos para que no haya fuga ([1.2](#d1-2)), así que no contaminan la evaluación, pero sí acotan el techo: un modelo que trabaja sobre descriptores sin estereoquímica no puede separarlos ni en principio, y cada par discordante aporta un error inevitable.

**No todos son el mismo caso, y el corte no es por cuántos nombres lleva cada uno.** De los 131, **26 llevan un solo nombre** y 105 llevan varios, lo que por sí solo es esperable —el etambutol y el meso-etambutol son nombres distintos de la misma conectividad—. Lo que separa los casos es otra cosa: **42 de los 131 usan un nombre que el archivo asigna además a otra estructura**, y se reparten en los dos grupos —**34 de los 105** y **8 de los 26**—, así que los 26 «limpios» no lo son todos (S1.14). El ejemplo del propio esqueleto del etambutol: una de sus cuatro filas se llama «ritonavir» y el ritonavir real tiene dos anillos de tiazol y 721 de peso molecular, contra los 204 de esa fila. Para esos 42 lo que está en duda es la identidad antes que la etiqueta, y es la patrocinadora quien puede decir de dónde salió el nombre ([los datos del proyecto](datos-contenido.md)).

**Cuánto pesa, y en qué métrica.** En **exactitud** ya está medido y no aprieta: son **151 errores inevitables sobre 7,805**, un techo del **98.1%** que ningún modelo realista alcanza, así que no explica nada de lo que falte ([los datos del proyecto](datos-contenido.md)). En **MCC y AUPRC sobre la clase minoritaria**, que son las métricas del proyecto por la [C.1](#dc-1), no está medido, y ahí sí podría apretar: los 429 compuestos no se reparten por igual entre las dos clases. Eso es lo que falta del [issue #28](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/28), cuyo enunciado pide calcular un techo que en exactitud ya existe.

**Por qué se pregunta.** Es una de las dos lecturas y no se distinguen desde los datos. Si la estereoquímica cambia de verdad el paso por la barrera —cosa plausible, porque los transportadores son estereoselectivos—, entonces la representación actual pierde información y hay que decir en el reporte que el techo está acotado por diseño. Si en cambio los pares vienen de ensayos distintos que se compararon mal, entonces son ruido de curación y la cota es menor de lo que parece. Su criterio farmacológico es lo que decide cuál de las dos pesa más.

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| S1.1 | Cada fila es una observación independiente | Desmentido | 7,805 filas son 4,018 esqueletos; 131 esqueletos reúnen estereoisómeros con etiquetas distintas (429 filas), lo que acota el techo alcanzable ([1.8](#d1-8)) | Partición y reportes agrupan por esqueleto |
| S1.2 | Los grupos A–D son una escala de confiabilidad | Desmentido | Ver [1.1](#d1-1). BBB− es 12.1% en A y 92.2% en D | Estratificar, no excluir |
| S1.3 | El umbral de TPSA publicado es una constante | Acotado | Cambia con el subconjunto (ver [1.6](#d1-6)) | Derivarlo solo sobre entrenamiento |
| S1.4 | «Natural» es una categoría limpia | Acotado | Es coincidencia exacta con COCONUT | Declarar la definición usada |
| S1.5 | La brecha entre naturales y el resto es química | Sin comprobar | Con tres orígenes es de 28.3 puntos contra los compuestos sin equivalente natural (52.7% contra 81.0% BBB+; la versión de dos grupos daba ~19), pero no existe en el grupo A (88.4%, 86.6% y 87.7% en los tres orígenes, con un posible efecto techo porque A es 88% BBB+) y sí en B y C ([1.6](#d1-6)); entre los que cumplen la regla TPSA/HBD persiste (80.9% contra 90.9%) | Evaluar por origen global y dentro de cada grupo A, B y C |
| S1.6 | Los valores atípicos son alertas, no errores | Asumido | No se recortan ni eliminan | — |
| S1.7 | Mandar los 312 acíclicos a entrenamiento es una regla razonable | Sin comprobar | Es el valor por omisión de `scaffold_split` y no sale de ninguna medición; ninguno entra a validación ni a prueba. Dentro del entrenamiento hay 127 filas en 44 esqueletos compartidos (estereoisómeros) | Escribir y justificar la regla antes del baseline; en la validación cruzada se agrupan por esqueleto de conectividad |
| S1.8 | El conjunto externo de Spielvogel sirve para validar | Desmentido | 154 nombres, sin SMILES ni InChI | Conseguir las estructuras |
| S1.9 | Yeo-Johnson es una buena transformación | Sin comprobar · **revisado** | La validación cruzada del 12 de octubre la dejaba por debajo de min–max en 12 de los 15 pliegues, y esta fila la daba por «desmentida en parte». Era un artefacto del `C` fijo: con el `C` que cada transformación elige para sí, Yeo-Johnson y min–max empatan en 0.695 de MCC ([1.5](#d1-5)). Ni mejor ni peor que las otras dos; la matriz guardada la asume y nada en la medición obliga a cambiarla | Cambiar de transformación y reentrenar: la selección de la §9 ya no depende de ella —se hace sobre los valores crudos y el notebook comprueba que da las mismas 151 columnas con las tres— y las dos versiones de la matriz, transformada y sin transformar, están guardadas |
| S1.10 | El PCA no aporta | Sin comprobar | No adoptado por explicabilidad, y ya no se mide: el notebook vigente conserva el PCA solo como vista del espacio químico. La comparación de desempeño que esta fila citaba —diferencia de −0.008 en Random Forest, IC 95% −0.070 a +0.055— es de una versión anterior del notebook ([1.5](#d1-5)) | Solo como exploración (visualizar el espacio químico, comparar particiones); no es candidato del Avance 3 por la explicabilidad |
| S1.11 | Las tres características derivadas aportan | **Desmentido** | Medido con el modelo y no con el AUC individual (`scripts/experimento_derivadas.py`, corrida `experimentos/2026-10-18-artemio-1.5-derivadas/`): diferencia pareada de MCC contra no usarlas, 15 evaluaciones — logística, las tres, +0.0001 ± 0.0014; Random Forest, las tres, **−0.0062** ± 0.0039; `tpsa_por_mw` sola, +0.0009 ± 0.0034. Ninguna aporta, y con árboles las tres juntas quedan por debajo. `lipo_neta` además ya no entra: correlaciona 0.975 con `MolLogP`, que está protegido | Nada que rehacer; `regla_2p` y `tpsa_por_mw` siguen en la matriz porque no estorban, y retirarlas es un cambio de una línea en la §6 |
| S1.12 | Todo lo que aprende de los datos se ajusta solo con entrenamiento | Comprobado | Media tras escalar: 0.0000 en entrenamiento, 0.0048 en evaluación | — |
| S1.13 | L = 2048 es un tamaño razonable de vocabulario | Acotado | Medido: el MCC no distingue tamaños desde ~128 y en AUPRC 2048 es el menor L dentro del ruido en dos de tres modelos ([1.7](#d1-7)); falta repetirlo con modelos afinados | Elegir L por modelo en el Avance 3 |
| S1.14 | El nombre del compuesto lo identifica | Desmentido | 1,109 filas (14.2%) no traen nombre; de las que sí, 347 de los 5,091 nombres apuntan a más de una estructura (945 filas) y 1,075 esqueletos cargan más de un nombre; «ritonavir» aparece con cuatro estructuras ([1.8](#d1-8), `scripts/cifras_nombres_fase1.py`) | Cruzar siempre por estructura, nunca por nombre; afecta a la S1.8 |

---

## Fase 2 · Actividad {#fase2}

202,647 mediciones (ChEMBL 187,354, NPASS 11,992, CMAUP 3,301) sobre 99,585 esqueletos. Cada fila es una medición: un compuesto contra una proteína, con tipo (IC50, Ki, EC50), relación (`=`, `>`, `<`), valor y unidad. El pChEMBL es −log₁₀ de la concentración molar: 5 equivale a 10 µM y 6 a 1 µM. Solo 1,033 esqueletos están también en el conjunto de permeabilidad, por eso las dos fases casi no se tocan. **La matriz de pares ya está construida** —70,384 pares compuesto-diana sobre 59,532 esqueletos de conectividad, con 201 descriptores por compuesto— **y la partición con la prueba reservada también** ([2.7](#d2-7)); el modelo de referencia del Avance 3 corre sobre ellas ([2.9](#d2-9)). Evidencia: [notebook 01b](../notebooks/01b_EDA_actividad_snc.ipynb) (los datos), [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb) (la matriz y la partición), [notebook 03](../notebooks/03_Baseline.ipynb) (el modelo de referencia) y [datos del proyecto](datos-contenido.md).

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

**Medido el 18 de octubre: el riesgo era real.** El control del [#32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32) muestra que un modelo que solo ve la procedencia alcanza 0.280 de MCC —el 65% de lo que consigue la química— y que dentro de los pares que solo tiene NPASS el AUROC de la química baja a **0.574 [0.534, 0.609]**, contra 0.831 dentro de ChEMBL. El confundido por compuesto no era tan benigno como el reparto de esqueletos sugería. Cuánto de esa caída es origen y cuánto es composición de dianas se desarrolla en la [2.3](#d2-3), con la comparación a igual diana.

El 65.4% de los naturales también está en ChEMBL, así que el riesgo se concentra en 1,445 compuestos. Los 2,727 solapados sirven de calibración: donde hay pChEMBL y concentración exacta se puede ajustar el corte de concentración y medir cuánto discrepan. **Pendiente:** hacer esa calibración antes de fijar la [2.3](#d2-3).

#### 2.1 · El alcance: cinco categorías de enfermedad {#d2-1 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes preguntaba por cuatro dianas sueltas

**Qué se decidió.** El alcance de la fase 2 son **cinco categorías**: Alzheimer, Parkinson, neuroinflamación, depresión y estrés oxidativo. Las demás se remueven. La patrocinadora lo cerró en la reunión del 15 de octubre: «sí se pueden resumir a esas… y si los demás adelante los pueden remover» (acta de la reunión, documento interno).

| Categoría | Registros | |
|:--|--:|:--|
| Alzheimer | 52,676 | queda |
| Parkinson | 32,372 | queda |
| Neuroinflamación | 12,331 | queda |
| Depresión | 10,888 | queda |
| **Estrés oxidativo** | **2,456** | **queda, por decisión suya** |
| Epilepsia · Neurodegeneración · Deterioro cognitivo · Ansiedad · Huntington · ELA | 3,826 en total | fuera |

Son 110,723 registros, el 96.7% de los 114,549 que tienen categoría de diana: el recorte cuesta 3,826 filas.

**El criterio, que es lo que ella pidió dos veces.** Preguntó «¿cuál es el criterio para eliminar el resto, solo porque tienen pocas entradas?» y «¿cómo debería ser esa distribución para que no haga ruido?», con una cota propia: menos del 10% no le parece confiable. La regla que queda es **≥ 50 registros por categoría**, ofrecida como conservadora. No es una cota derivada: por debajo de unas decenas de pares un modelo propio no se sostiene, y ELA tiene 53 registros y Huntington 153. Se escribe como regla y no como lista para que el día que lleguen datos nuevos no haya que volver a preguntar.

**Estrés oxidativo entra por decisión suya, y su razonamiento es el criterio biológico que el equipo no podía deducir:** la escala va de lo general a lo específico, «es solo un dolor de cabeza o te está tratando Alzheimer», y el estrés oxidativo es el extremo general —«toda enfermedad, desde la gripa, desde hacer ejercicio, el acné»—. Con 2,456 registros es la categoría más chica que queda, y ella misma la dejó revisable: si el análisis la muestra anómala, se reconsidera.

**Las cuatro dianas sin datos quedan resueltas sin preguntarle.** Era la pregunta anterior de esta entrada, y el alcance la contesta: `GABRB2` y `GABRG2` son de Epilepsia y `TARDBP` de ELA, categorías que salen. Solo `AIF1` está en una categoría que queda, y se excluye por sí sola: tiene 0 filas y la etiqueta de la propia patrocinadora dice «marcador de microglía activada; **no es diana farmacológica**».

**Lo que hay que mostrarle, porque sus dos decisiones se restan entre sí.** Estrés oxidativo es **47.7% NPASS y CMAUP**. Si además se descartara el etiquetado de esas dos fuentes (su correo del 16, [2.3](#d2-3)), la categoría que defendió pasaría de 2,456 filas a 1,285. No lo vio, y conviene decírselo antes de que decida otra cosa sobre la 2.3.

#### 2.6 · La partición de prueba que sí se había reservado {#d2-6 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes era una pregunta abierta

**Qué se decidió.** Sí había una partición reservada, **se hizo al azar y sin criterio**, y la patrocinadora entrega el archivo completo para que el equipo la rehaga. «Partamos de la base de datos completa que se las podemos pasar… ustedes que son los expertos tengan la base completa y hagan bien esas separaciones» (acta de la reunión, documento interno).

**Qué pasó.** El archivo se llama `..._Entrenamiento.csv`: el diccionario describe 225,513 filas y el recibido tiene 202,647, el 89.9%. La sospecha era correcta. Al explicarle por qué el azar no sirve —si hay cincuenta análogos de la morfina y el 10% se llevó cinco, el modelo memoriza el andamiaje y la evaluación sale inflada— lo aceptó sin reservas: «lo hicimos muy a la ligera… si hay una forma de hacerlo con mejores criterios, adelante».

**Su condición, que repitió cuatro veces:** que se reserve una prueba que el modelo nunca vea. Su razón no es metodológica sino práctica: no espera que aparezca otra base de datos con la que validar después. Eso se respeta en la [2.7](#d2-7), que reserva el 20% y lo deja fuera de la validación cruzada.

**La limitación que hay que declarar en el reporte.** Un 10% extraído al azar del mismo archivo comparte andamios, ensayos y artículos con el 90%: es una partición interna con otro nombre. Prueba filas nuevas, no química nueva ni protocolos nuevos. Si el reporte final la llama «validación externa», sobrevende lo que compra. Con el archivo completo en mano el punto es casi histórico, pero queda escrito porque ella descansa mucho en ese conjunto.

**Dónde se nota en la fase 1.** La prueba de humo del notebook 02 (§11) evaluaba sobre la prueba reservada; ahora evalúa sobre validación, que es lo que esta condición exige. **Las cifras subieron, no bajaron**, y por eso conviene no compararlas: la prueba se quedó con los andamios raros (57.3% BBB+ contra 72.0% de la validación), así que es el conjunto difícil. Descriptores con Random Forest pasan de 0.346 de MCC sobre la prueba a 0.558 sobre validación, y la línea base del AUPRC sobre BBB− pasa de 0.427 a 0.280, de modo que tampoco las columnas de AUPRC son comparables entre las dos versiones.

**Pendiente de Jorge Uribe:** el método con que separó el 10%, y verificar con el equipo si introduce sesgo (ofrecido en el correo del 16 de octubre).

#### 2.10 · El objetivo se guarda como intervalo, no como etiqueta {#d2-10 .vigente}

**Estado:** vigente · decisión del equipo, no necesita a la patrocinadora

*No hay nada que preguntarle.* Se registra porque fija el formato del artefacto que todo el modelado de la fase 2 va a leer, y porque tres de sus reglas de agregación difieren de lo que dice la [propuesta de variable objetivo](variable-objetivo-fase2.md).

**Qué pasó.** La matriz de la fase 2 (`src/data_prep/pares_fase2.py`, construida con `scripts/construir_pares_fase2.py`) deja 70,384 pares sobre 59,532 compuestos y 26 dianas. La decisión no es cómo agregarla sino **qué se guarda**: no una etiqueta, sino el intervalo donde cae la potencia, con la binaria derivada de él.

| Columna | Qué es |
|:--|:--|
| `pActividad` | la potencia como número, 6 − log10 µM; `NaN` si el par solo tiene cotas |
| `limite_inferior`, `limite_superior` | el intervalo, con ±∞ donde no hay cota |
| `activo_10um`, `activo_1um` | la etiqueta binaria, **derivada** del intervalo |

**Por qué.** Es la lección de la fase 1 aplicada al revés. El Avance 2 seleccionó sus 171 columnas sobre la matriz transformada con Yeo-Johnson y congeló ese artefacto, así que cambiar la transformación obliga a repetir la selección y a reejecutar el notebook ([1.5](#d1-5)). Guardar solo `activo_10um` tendría el mismo defecto: adoptar la regresión de la [2.9](#d2-9) obligaría a reconstruir todo. Con el intervalo guardado, la clasificación, la regresión sobre exactas y la censurada leen el mismo archivo, y **el umbral pasa a ser una decisión de lectura**.

**Y el intervalo reproduce la regla del diccionario sin programarla aparte.** En escala de potencia un `> L µM` es cota superior, así que «inactivo con umbral T» es `limite_superior ≤ 6 − log10 T`. Un `> 1 µM` da cota superior 6, que no alcanza para declarar inactivo con T = 10 µM y sí con T = 1 µM: es la sección 7 del diccionario como consecuencia, y no como caso especial.

**Tres reglas de agregación que difieren de la propuesta**, y conviene que se vean porque mueven cifras:

1. **Mediana de las mediciones exactas, no el valor más potente.** El máximo sesga hacia la clase positiva, que es el primer problema que la propuesta declara de su propia regla. La dispersión no se pierde: queda en `rango_exactas`, así que un análisis de robustez puede excluir los pares dispersos sin volver a leer el archivo.
2. **Conflicto es evidencia incompatible, no dispersión.** Con la mediana, dos mediciones a los lados del corte son ruido de medición y no contradicción. Un par se marca en conflicto cuando su mediana cae fuera de lo que permiten sus cotas, o cuando las cotas se cruzan. Así bajan de **1,784 a 1,126**, y solo 15 dan un intervalo vacío. Eso alivia el segundo problema de la propuesta: quitar los conflictos pesaba más en NPASS y CMAUP (32% y 39% de sus pares con varias mediciones).
3. **El empate en el umbral se resuelve a favor de activo.** Una medición exacta justo en el umbral es activa por la convención de «concentración igual o menor»; un censurado `> 10 µM` con el mismo umbral es inactivo por la regla del diccionario. Tienen la misma relación numérica con el corte y significan lo contrario, y lo que los distingue es que el censurado no tiene cota inferior. Resolverlo así mueve **409 pares** con el corte de 10 µM, porque los valores redondos son frecuentes. Lo encontró una prueba, no una lectura.

**Dos recortes declarados.** La potencia se recorta a **[2, 12]**, que no es un percentil elegido a mano: es el rango del pChEMBL observado en este archivo (2.35 a 12.00), y ChEMBL no asignó pChEMBL a ninguna de las 319 filas que caen fuera —su propia tubería ya las marcó—. Y las filas en unidades de masa quedan fuera, porque sin peso molecular no hay conversión a molar: son 181 de las que podrían formar par, y por eso el conteo da 70,384 y no 70,497.

**Cifras del artefacto.** 57,832 pares con potencia y 12,552 solo con cotas; 67,736 con etiqueta a 10 µM (72.8% activos, 2,648 sin decidir) y 69,632 a 1 µM (50.2%, 752 sin decidir); 24,230 grupos para la partición. Los descriptores quedan **201 de 217** utilizables, dos menos que los 203 de la fase 1, porque el conjunto de compuestos es otro y cambia qué columnas salen constantes o no finitas. Esa cifra pertenece al diccionario de la matriz y se mueve ahí cuando el #83 se fusione.

### Propuestas

#### 2.2 · Por diana, con multitarea como comparación {#d2-2 .vigente .revisada}

**Estado:** vigente · revisada el 17 de octubre: antes era abierta, y la [2.1](#d2-1) la desbloqueó

**Qué se decidió.** Un modelo por diana para **once** dianas, el multitarea para las quince restantes, y el orden lo decide el **volumen**: de más pares a menos, empezando por `BACE1`, `DRD2`, `ACHE`, `MAOB` y `MAOA`. No se espera una lista de prioridades suya.

**Once y no catorce, y la diferencia la encontró una comprobación que faltaba.** El 18 de octubre, al reservar la prueba del 20% y mirar los pliegues diana por diana —lo pidió Pame al revisar el [#86](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/86)—, el conteo de «1,000 pares o más» bajó de 14 a **13** sobre lo que queda para ajustar. Y de esas 13, dos no sostienen un modelo propio aunque tengan volumen: `LRRK2` (96.8% de activos) deja un pliegue con **13** negativos y `GRIN2B` (96.9%, y solo 172 grupos para 1,592 pares) deja uno con **5**. Con esa clase minoritaria no hay métrica por pliegue con error estándar interpretable ni punto de operación elegible, así que las dos pasan al multitarea y se reportan como subgrupo. El criterio queda escrito como condición y no como número: **mil pares o más y cincuenta casos de la clase minoritaria en todos los pliegues.**

**Qué pasó.** Con el alcance fijo y la matriz de pares construida, los volúmenes ya no se cuentan en registros sino en pares, que es la unidad del modelo:

| Dianas | Pares que cubren |
|:--|--:|
| Las 14 con 1,000 pares o más, sobre los 70,384 pares | **94.3%** |
| Las 13 con 1,000 o más, sobre los 54,369 que quedan al reservar la prueba | 93.5% |
| **Las 11 que además tienen clase minoritaria en todos los pliegues** | **85.6%** (46,534 de 54,369) |
| Las 21 con 200 o más | 99.3% |
| Las 5 restantes | 466 pares en total |

Y el dato que decide entre las tres formas: **el 85.0% de los compuestos se midió contra una sola diana.** Solo 8,934 compuestos (15.0%) tienen dos dianas o más, y aportan el 28.1% de los pares.

**Se propone.** **Un modelo por diana para las que pasan el criterio** —once, el 85.6% de los pares ajustables— y **un multitarea** sobre las 26, que deja de ser solo un brazo de comparación: es donde viven `LRRK2` y `GRIN2B`, que tienen volumen pero no clase minoritaria. El multitarea no se descarta: es la única forma de incluir las cinco chicas, y aunque su palanca directa —compuestos medidos contra varias dianas, donde el reparto es inmediato— alcanza solo al 15% de los compuestos, sigue compartiendo la representación química, que es lo que podría sostener a las dianas pequeñas.

**Por categoría de enfermedad, no.** La categoría agrupa genes que no comparten mecanismo: en Alzheimer conviven `BACE1` (una proteasa), `ACHE` (una esterasa) y `PPARG` (un receptor nuclear). Un modelo sobre esa mezcla aprende el promedio de tres farmacologías. Y como cada gen pertenece a exactamente una categoría, «por categoría» es solo una agrupación más gruesa de los mismos genes, sin nada que la haga preferible. **La categoría se usa para reportar**, que es donde sí aporta: permite decir «el modelo acierta mejor en Alzheimer que en neuroinflamación», que es la lectura que importa para priorizar candidatos.

**Qué lo cambiaría.** Que ella señale dianas prioritarias, y entonces cambia solo el **orden** en que se entrenan, no la forma ni el resultado: son modelos independientes, así que reordenarlos no cuesta rehacer nada. Por eso no vale la pena esperar esa respuesta. Lo que sí cambiaría la forma es que pida una diana que no pasa el criterio —`GRIN1`, con 88 pares y un pliegue sin negativos, es el caso extremo—: ahí la respuesta no es entrenarle un modelo, es decirle con la cifra por qué no se puede y ofrecerle el subgrupo del multitarea.

**Lo que esto arrastra.** Once modelos son once conjuntos de hiperparámetros sobre la misma partición, así que el arnés de validación cruzada agrupada (MLOps 0.3) deja de ser cómodo y pasa a ser necesario. Y la tasa de activos por diana va de 34.8% en `MAOA` a 96.9% en `GRIN2B`, así que el punto de operación no puede ser el mismo para todas: la curva de la [C.5](#dc-5) se entrega por diana.

La tabla por diana con pares, grupos y el mínimo de cada clase en los pliegues está en la sección 6.3 del [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb), que es de donde salen estas cifras.

#### 2.3 · Etiquetado por tres vías y criterio de «activo» {#d2-3 .vigente .revisada}

**Estado:** vigente · revisada el 7 y el 17 de octubre · decidida por el equipo

**Qué se decidió.** Las **tres fuentes** se etiquetan con las columnas de la sección 5 del diccionario, que vienen informadas y homogéneas para las tres. Corte **10 µM** como principal y **1 µM** como análisis de sensibilidad, reportado siempre al lado. Sin los inactivos declarados por texto, y con los pares en conflicto marcados ([2.10](#d2-10)).

**Por qué se decide y no se espera su respuesta.** En su correo del 16 de octubre descartó «hacer la inferencia, al menos no de forma directa», contestando a lo que se le preguntó en la reunión: construir el valor en las otras dos bases. Su preocupación es legítima —el umbral no significa lo mismo en todos los ensayos— pero el remedio que propuso no se puede ejecutar y el que implica tampoco alcanza:

- **Revisar por tejido y tipo de experimento no es posible** sobre la población que se modela: esas columnas están vacías en las 108,640 filas de la ruta `cns_target`, y en el 99.6% de los pares en conflicto el tejido no está ni anotado.
- **Quedarse solo con ChEMBL no compra comparabilidad.** Dentro de ChEMBL hay 8,984 ensayos distintos, y el desacuerdo entre mediciones del mismo par es ligeramente **peor** ahí solo (28.7% discrepan más de 10×) que juntando las tres fuentes (26.0%).
- **Y cuesta la mitad de la categoría que ella defendió:** estrés oxidativo es 47.7% NPASS y CMAUP.

Lo que sí se midió es que la regla de concentración **reproduce el pChEMBL hasta el redondeo**: sobre las 72,955 filas que traen los dos, la diferencia tiene mediana 0.0021 y máximo 0.005. Etiquetar por concentración no es una inferencia entre bases, es la misma aritmética aplicada fila por fila: ninguna etiqueta se traslada de una base a otra, cada fila se etiqueta con su propio valor.

**Lo que sí se solapa, y con la llave que importa.** Una versión anterior de este párrafo añadía que «los compuestos casi no se solapan: 283 SMILES entre ChEMBL y NPASS». La cifra es correcta por SMILES exacto y engañosa aquí, porque la llave del par es el **esqueleto de conectividad**, no el SMILES: con ella hay 1,592 pares mixtos y el 42.4% de los pares con evidencia de NPASS comparte par con otra fuente. El solapamiento es sustancial, y por eso el desempeño se reporta en estratos disjuntos y no «por fuente».

**El riesgo se vigila en lugar de evitarse.** «Solo ChEMBL» queda como análisis de sensibilidad, el desempeño se reporta por estrato de procedencia ([2.10](#d2-10)), y el control de atajo del [#32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32) decide.

**El control ya se corrió, y el resultado no es el que esperábamos.** `scripts/experimento_atajo.py`, Random Forest sobre los 54,369 pares de entrenamiento y validación, cinco pliegues agrupados y tres semillas, con tres conjuntos de características:

| Lo que el modelo ve | MCC | AUROC |
|:--|--:|--:|
| Solo la procedencia (el estrato, sin mirar la molécula) | 0.280 | 0.579 |
| Solo química (los 201 descriptores) | 0.428 | 0.837 |
| Las dos | **0.451** | 0.843 |

**El criterio que la entrada se había fijado no dispara:** la química supera a la procedencia por 0.148 de MCC, así que no basta con saber de qué base viene el compuesto. Pero la procedencia sola llega al 65% del MCC de la química, que es más de lo que debería poder una columna de tres valores, y añadirla a la química todavía suma 0.023. La fuente **sí** lleva señal de la etiqueta.

**Y la segunda medición es la que importa, porque es la pregunta del proyecto.** Un modelo con química puede inferir la procedencia —los productos naturales tienen esqueletos distintos— y usarla de atajo sin que la columna exista. Eso se ve midiendo **dentro de cada estrato**, donde ya no hay fuente que distinguir. En AUROC, que no depende del umbral y por tanto compara entre estratos con tasas base muy distintas, con intervalo del 95% por bootstrap **de grupos**:

| Lo que el modelo ve | Estrato | Pares | Activos | AUROC |
|:--|:--|--:|--:|--:|
| Química | Solo ChEMBL | 50,671 | 74.8% | 0.831 [0.821, 0.841] |
| Química | Mixtos | 1,588 | 40.3% | 0.610 [0.570, 0.658] |
| Química | **Solo NPASS** | **2,109** | **12.3%** | **0.574 [0.534, 0.609]** |
| Química **y diana** | Solo NPASS | 2,109 | 12.3% | 0.613 [0.574, 0.648] |

**El modelo separa mucho peor los pares de NPASS que los de ChEMBL**, y eso no se puede reportar en un agregado. Pero hay dos cosas que una primera versión de esta entrada afirmó de más, y las dos las corrigió Pame al revisar el [#90](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/90):

- **Decía «casi no funciona» y «indistinguible del azar».** No lo es: el intervalo de 0.574 es [0.534, 0.609] y **no toca 0.5**. Discrimina poco, y discrimina.
- **Y atribuía todo el déficit al origen, cuando parte es de la diana.** El modelo del control no recibe la diana, y dentro de `solo_npass` conviven dianas con tasas base de 1.2% a 29.7%; dándosela, el AUROC sube a 0.613. Parte de lo que parecía «no separa naturales» era «no sabe de qué diana se trata».

**A igual diana, solo tres dianas se pueden comparar, y el resultado es heterogéneo.** El criterio no puede ser el número de pares sino **el tamaño de la clase minoritaria**: `ACHE` tiene 221 pares de NPASS y **3 activos**, así que su AUROC es ruido. Exigiendo veinte casos de cada clase en cada fuente quedan tres dianas (con química y diana, el bootstrap sobre grupos):

| Diana | NPASS: pares · minoritaria | AUROC NPASS | AUROC ChEMBL |
|:--|:--|:--|:--|
| `NFE2L2` | 579 · 126 | 0.639 [0.571, 0.691] | 0.672 [0.550, 0.785] |
| `PTGS2` | 262 · 20 | 0.515 [0.397, 0.709] | 0.705 [0.665, 0.744] |
| `MAPT` | 118 · 35 | 0.540 [0.425, 0.652] | **0.884 [0.817, 0.937]** |

**En `NFE2L2` la brecha prácticamente desaparece; en `MAPT` es clara y los intervalos no se tocan; en `PTGS2` no se decide.** Una versión anterior de esta tabla traía siete dianas, incluidas `ACHE`, `MAOA` y `DRD2` con tres, cinco y catorce activos entre sus 221, 411 y 260 pares de NPASS, cuyos AUROC altos hacían parecer que la brecha se cerraba. Lo señaló Pame al revisar el [#90](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/90), que corrió la medición por su cuenta y llegó a las mismas tres dianas.

**Lo que sostiene la evidencia, y nada más:** el agregado de `solo_npass` está deprimido en parte por la composición de dianas; a igual diana hay **señal débil y heterogénea** —una diana sin brecha, una con brecha clara, una indecidible—; y solo hay tres dianas con datos para medirlo. **No se puede afirmar todavía que el modelo no sirva para productos naturales, ni lo contrario.** Lo que sí está establecido es que un desempeño agregado no los describe.

**Nota sobre las cifras.** Las de aquí salen de agrupar las predicciones fuera de pliegue y calcular un AUROC; promediar el AUROC de cada pliegue, que es la otra forma razonable, da 0.569 y 0.607 donde aquí sale 0.574 y 0.613. La diferencia es el estimador, no los datos; se agrupan las predicciones porque es lo que permite el bootstrap por grupos, con cada par contado una sola vez.

**Qué cambia en cómo se reporta.** No invalida etiquetar las tres fuentes: la alternativa —«solo ChEMBL»— no tendría productos naturales en absoluto. Invalida **reportar un desempeño agregado como si describiera a los naturales**: toda métrica va con su desglose por estrato, y la cifra que contesta la pregunta del proyecto es la de `solo_npass` **por diana**, con su intervalo. La corrida está en `experimentos/2026-10-18-artemio-2.3-atajo-procedencia/` y las tablas en `notebooks/datos/resultados_atajo.csv` y `atajo_por_diana.csv`.

**Qué lo cambiaría.** Que con los modelos afinados el patrón de `MAPT` —brecha clara, intervalos que no se tocan— se repita en la mayoría de las dianas comparables en vez de en una de tres, y entonces la conclusión no es cambiar el etiquetado sino **decir que el modelo no sirve para productos naturales**, que es un resultado válido y así hay que reportarlo; que el desempeño con 1 µM sea mejor en el Avance 3, que cuesta una columna por el intervalo de la [2.10](#d2-10); que aparezca un **desenlace** —qué compuestos rescataron neuronas y a qué concentración—, que es lo único que haría estimable el umbral en vez de elegible; o que ella lo ratifique de otro modo al ver estas cifras.

**El desarrollo completo está en [la propuesta de variable objetivo](variable-objetivo-fase2.md)**, que detalla las reglas por medición y por par, los problemas declarados y el protocolo de robustez. Esta entrada guarda la decisión y lo que está en juego.

**Qué pasó.** Primero se planteó «pChEMBL ≥ 5 primario, ≥ 6 como robustez», sin decir cómo etiquetar lo que no tiene pChEMBL. El EDA mostró que el pChEMBL solo existe para ChEMBL: etiquetar solo por él descarta 15,293 registros de NPASS y CMAUP (los naturales) y 54,498 mediciones censuradas (`> X nM`), de las cuales 29,730 traen además un texto que las declara inactivas. **Los dos últimos grupos no se suman:** los 29,730 están dentro de los 54,498, así que para esas filas la segunda y la tercera vía son la misma fila vista de dos maneras.

**Se propone.** Tres vías: pChEMBL donde exista; **concentración exacta** para el resto, que recupera 12,809 de los 15,293 naturales —los que traen relación `=`, contra 2,484 censurados o aproximados—; e **[inactivo declarado](glosario.md)** para los textos y para las **[mediciones censuradas](glosario.md)** cuyo límite llegue al umbral. Las cifras de esta entrada se recalculan con `scripts/cifras_fase2.py`.

**Cuidado con el «10 µM», que aparece como dos cosas distintas.** Una es el **umbral de «activo»**: 10 µM equivale a pChEMBL ≥ 5 y 1 µM a pChEMBL ≥ 6. La otra es el **límite de un censurado**, el número que viene después del `>` en cada fila. La regla del diccionario de la patrocinadora (sección 7) las ata: un `>` solo sirve como negativo si su límite es igual o mayor que el umbral de «activo». Por eso no se pueden contestar por separado.

**Qué cuesta cada corte.** Las dos primeras columnas salen del archivo y se recalculan con el script; las dos últimas vienen del notebook 01b y se tendrán que rederivar cuando el etiquetado se implemente, porque dependen de esta misma regla:

| Si «activo» se corta en | Censurados que sirven como negativo | Ambiguos | Activos por registro | Razón de clases |
|:--|--:|--:|--:|--:|
| **10 µM** = pChEMBL ≥ 5 | 48,480 (89%) | 6,018 | 61.7% | 1.6:1 |
| **1 µM** = pChEMBL ≥ 6 | 53,359 (98%) | 1,139 | 44.4% | 0.8:1 |
| 100 µM, como referencia | 6,737 (12%) | 47,761 | — | — |

Cortar en 1 µM es más exigente con los activos y, por la misma regla, más generoso con los negativos: recupera 4,879 censurados más y deja el conjunto casi balanceado. Cortar en 10 µM conserva más activos y desperdicia seis mil censurados. El 10 µM del equipo se había propuesto por ser el valor modal de los límites, que no es una razón farmacológica.

**Un solo experimento pesaba demasiado, y resultó que no tanto: la cifra era por registro y el modelo entrena por par.** Las 29,730 filas con texto de inactividad son exactamente el mismo conjunto: todas censuradas con `>`, todas con límite de 10 µM, todas con el texto «Not active» y **todas de la misma referencia, `CHEMBL1909046`**, que es el panel de toxicogenómica DrugMatrix. Son 36,653 los censurados con límite en 10 µM, así que esa referencia sola aporta el 81% de ellos.

| Unidad, con el corte en 10 µM | Negativos | De `CHEMBL1909046` |
|:--|--:|--:|
| Registro etiquetado | 48,480 | 29,730 · **61%** |
| **Par compuesto-diana** | 20,281 | 2,187 · **10.8%** |
| Par, sin los inactivos por texto *(definición vigente)* | 18,107 | 13 · **0.1%** |

Las dos últimas filas las imprime `scripts/cifras_etiqueta_fase2.py` en sus dos variantes. La fila del medio decía antes 19,488 y 2,756 · 14.1%, de una versión del conteo anterior a que la llave del par y los filtros quedaran fijos; es la cifra que Pame no pudo reproducir al revisar el [#86](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/86).

Las 29,730 filas son **772 compuestos**, así que al agrupar por par su peso cae casi a una sexta parte (61% a 10.8%). Y la definición vigente los deja fuera, con lo que baja al 0.1%: **el riesgo se quita al excluirlos, no se demostró que no existiera**, y se vigila con la sensibilidad «con los inactivos por texto», que el script imprime al lado de la principal.

**La razón para excluirlos no es que el límite sea inventado.** Una versión anterior de esta entrada decía que el `>` de 10 µM «lo asignó el equipo que armó el archivo, no el ensayo original». El comentario de ChEMBL de esas 29,730 filas dice literalmente «Inhibition < 50% @ 10 uM and thus dose-reponse curve not measured», así que el límite viene del ensayo y la codificación como `> 10 µM` es una traducción fiel. Lo que sostiene la exclusión es la **concentración en un solo documento**: las 29,730 filas son una sola campaña de tamizaje (`CHEMBL1909046`, el panel DrugMatrix) con 772 compuestos y sin curva dosis-respuesta, así que dejarlas dentro hace que un protocolo defina el 61% de la clase negativa por registro. Lo señaló Pame al revisar el [#86](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/86).

Esto se escribe así porque la versión anterior de esta entrada llamaba al 61% «el argumento más fuerte contra el corte en 10 µM», y lo era solo mientras la unidad fuera el registro. Deja de ser una razón para preferir 1 µM.

Las cifras son las del archivo recibido (202,647 registros, el 89.9% del completo de 225,513, [2.6](#d2-6)), que es el que verá el modelo. Los porcentajes coinciden con los del diccionario de la patrocinadora (98%, 89%, 12%).

**Denominadores.** Las proporciones dependen de la unidad. «Registro etiquetado» es todo el archivo, fenotípicos incluidos; «par esqueleto × gen» es un esqueleto de conectividad contra un gen (`target_gene`):

| Unidad | Umbral | Denominador | Activos | Inactivos | % activos | Razón |
|:---|:--|--:|--:|--:|--:|--:|
| Registro etiquetado | ≥ 5 | 194,086 | 119,835 | 74,251 | 61.7% | 1.6:1 |
| Registro etiquetado | ≥ 6 | 194,086 | 86,238 | 107,848 | 44.4% | 0.8:1 |
| Par esqueleto × gen | ≥ 5 | 71,145 | 50,177 | 20,968 | 70.5% | 2.4:1 |
| Par esqueleto × gen | ≥ 6 | 71,145 | 35,966 | 35,179 | 50.6% | 1.0:1 |

El conteo por par no es todavía el conjunto de entrenamiento: de 114,549 registros con categoría de diana, 109,264 reciben etiqueta; se excluyen 4,810 sin gen y 327 sin esqueleto calculable, y quedan 104,127 agrupables en 71,145 pares. El recuento marca un par como activo si alguna observación lo es, y con esa regla hay 1,810 pares discordantes con ≥ 5 y 2,426 con ≥ 6. El máximo de etiquetas no selecciona la medición más potente.

**Umbral.** Con pChEMBL, ≥ 5 daba 87.1% de activos (6.7:1) y llevó a proponer ≥ 6; con las tres vías la razón baja a 1.6:1 por registro. El sesgo de los registros con pChEMBL es una explicación posible, no demostrada. Se conserva ≥ 5 como primario y ≥ 6 como robustez: el balance de clases no determina el umbral biológico.

**La llave del par es el esqueleto × gen, y no el identificador del compuesto.** `source_compound_id` usa prefijos distintos por fuente —`CHEMBL…` contra `NPC…`— y **no comparte ni un valor** entre ellas, así que con esa llave un compuesto medido en dos fuentes entra como dos pares independientes y sus contradicciones quedan invisibles: son **164 pares** en conflicto entre ChEMBL y las fuentes naturales que así no se verían. Se usa el [esqueleto de conectividad](glosario.md) × `target_gene`, que además es la misma llave que `grupos_cv` usa en `src/data_prep/splits.py` para la validación cruzada agrupada, de modo que la unidad de etiquetado y la de partición coinciden.

**Y «por fuente» no se puede reportar sobre el par, porque la fuente no es un atributo del par.** Con la llave por esqueleto, 827 de los 828 pares de CMAUP comparten par con otra fuente, y 42.4% de los de NPASS: **CMAUP tiene exactamente un par propio**. Así que el desempeño se reporta en **estratos disjuntos por procedencia de la evidencia**, que sí son aditivos:

| Estrato | Pares | Activos |
|:--|--:|--:|
| Solo ChEMBL | 62,414 | 75.6% |
| Solo NPASS | 2,114 | 12.1% |
| Solo CMAUP | 1 | — |
| Mixtos | 1,592 | 37.5% |

La brecha real entre ChEMBL y los naturales es de **63 puntos**, no los 52 que sugería contar cada par en todas sus fuentes. Es el riesgo de la [2.5](#d2-5) cuantificado sobre la unidad correcta, y lo que vigila el control de atajo del [issue #32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32).

**El corte es una convención del protocolo de tamizaje, heredada del archivo.** El archivo **no tiene columna de desenlace**: nada registra si un compuesto funcionó, así que no hay nada contra lo que calibrar y un umbral no es estimable. Todo candidato que se puede construir falla por eso: un percentil de la distribución de la diana es circular, y la moda del límite de censura está condicionada al fracaso —se midió, y deja seis dianas con 93–96% de activos, peor que el corte global—. Lo que sí está medido es de dónde sale el 10 µM. De las 54,377 mediciones censuradas del archivo, el **67.4% está censurada exactamente en 10 µM**, y el comentario de ChEMBL de las 29,730 filas con texto lo dice literalmente, «Inhibition < 50% @ 10 uM». Eso sostiene una sola afirmación: **es la concentración a la que estos ensayos dejaron de mirar**. Llamarla «la concentración estándar de tamizaje de bibliotecas» sería generalizar una medición de este archivo a una práctica de la industria que nadie verificó —el mismo error del párrafo siguiente en pequeño—, así que no se dice.

**Una versión anterior de este párrafo decía otra cosa, y estaba mal.** Afirmaba que 10 µM es «aproximadamente la concentración libre máxima alcanzable con una dosis oral convencional sin toxicidad». No tenía fuente y se retira. Lo señaló Pame al revisar el [#86](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/86), con el argumento de que las concentraciones libres cerebrales de los fármacos del SNC quedan en general por debajo de 1 µM, así que el razonamiento favorecería 1 µM.

Esa objeción **tampoco se pudo cerrar con una fuente**, y conviene decirlo en vez de cambiar una afirmación sin respaldo por otra. Lo que se encontró al buscarla es indirecto y apunta en su dirección: la concentración libre cerebral es la que gobierna la unión a la diana, y en 18 inhibidores de los transportadores de serotonina y dopamina la concentración libre quedó a 3.3 ± 2.1 y 4.1 ± 4.0 veces de la Ki, mientras que la concentración **total** quedaba 408 ± 368 y 410 ± 395 veces por encima («Unbound Brain Concentration Determines Receptor Occupancy…», *Drug Metabolism and Disposition*, 2009; leído del resumen, no del texto completo, y medido en rata). Como las Ki de las dianas del SNC son nanomolares, eso sitúa las concentraciones libres muy por debajo de 10 µM. Es suficiente para no apoyar el corte en farmacología; no es suficiente para apoyarlo en la dirección contraria. **De modo que la entrada no se apoya en ningún argumento farmacológico**, ni a favor ni en contra.

**Y lo medible favorece 1 µM, así que 10 µM queda como principal solo por convención.** Tres criterios van en contra del 10 µM: con 1 µM sirven 4,879 censurados más (53,359 contra 48,480), el conjunto queda casi balanceado (0.8:1 contra 1.6:1) y se etiquetan más pares (67,266 contra 66,121). Uno va a favor: con 10 µM cae a ±0.5 unidades logarítmicas del corte el 20.7% de las mediciones exactas, contra el 24.3% con 1 µM (sección 7 de [la propuesta](variable-objetivo-fase2.md)). Se conserva 10 µM como principal porque es el corte de la sección 7 del diccionario y mantiene la comparabilidad con lo que la patrocinadora revisó, **y porque la [2.10](#d2-10) guarda el objetivo como intervalo: cambiar de principal es cambiar qué columna se lee, no reconstruir la matriz**. Los dos se reportan siempre al lado.

**Pero el mismo corte no significa lo mismo en cada diana, y eso se reporta.** La mediana de potencia va de 7.40 en `LRRK2` a 5.02 en `NFE2L2`, **241 veces**, así que con 10 µM `LRRK2` queda en 98.1% de activos —casi constante, inútil como objetivo— y `NFE2L2` en 50.7%. Mientras el corte siga siendo global, **se publica la tasa de activos por diana** junto con cualquier cifra agregada, para que se vea que la etiqueta no mide lo mismo en todas. La salida de fondo es no cortar, y está en la [2.9](#d2-9).

#### 2.4 · Los 88,098 registros fenotípicos {#d2-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Van dentro de un modelo específico, aparte o fuera del alcance?

**Qué pasó.** El 43.5% de los registros no corresponde a ninguna diana de la lista; entraron por la ruta `neuronal_assay`: sistemas celulares neuronales donde se midió un efecto sin identificar la proteína responsable. Responden «¿hace algo en un sistema neuronal?», no «¿actúa sobre esta diana?».

**Se propone.** Los 114,549 con categoría de diana alimentan el modelo (el conteo agrupable, 104,127 en 71,145 pares, no es el tamaño final). Los 88,098 fenotípicos se conservan aparte para otra pregunta; no se descartan.

#### 2.7 · Partición de la fase 2 {#d2-7 .vigente .revisada}

**Estado:** vigente · construida el 18 de octubre de 2026 · revisada: antes proponía además disjuntar por fuente

**Qué se decidió, y ya está construido.** El criterio de la fase 1 —andamio de Bemis-Murcko agrupado con el esqueleto de conectividad, con verificación de fuga— con las mismas fracciones: 70% entrenamiento, 10% validación, 20% **prueba reservada**, que es la condición que la patrocinadora repitió cuatro veces ([2.6](#d2-6), ratificada). La calcula `particion_de_pares` en `src/data_prep/pares_fase2.py` y viaja en `fase2_pares.parquet`, no en una celda del notebook: si viviera ahí, cada reejecución podría moverla.

| Partición | Pares | Grupos | Activos a 10 µM |
|:--|--:|--:|--:|
| Entrenamiento | 49,425 | 6,640 | 71.6% |
| Validación | 6,986 | 3,617 | 69.6% |
| **Prueba** | **13,973** | 13,973 | 78.7% |

Cero andamios y cero esqueletos cruzados. La validación cruzada de cinco pliegues corre sobre los 54,369 pares etiquetados de entrenamiento y validación, y no toca la prueba.

**Lo que cuesta, medido y no escondido.** Tres cosas, todas en la sección 6.1 del [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb):

- **La prueba son 13,973 pares en 13,973 grupos**, un andamio por par: es la semántica de `scaffold_split` —los andamios frecuentes alimentan el modelo y los raros evalúan química nueva— llevada al límite por la cola larga de la fase 2, donde el 59.8% de los grupos tiene un solo par. Mide generalización, no representatividad.
- **Tiene 7 puntos más de activos que el entrenamiento**, así que no es una prueba más difícil sino otra población. La fase 1 tiene la misma propiedad y mayor (57.3% contra 64.0%), porque agrupar por estructura no estratifica por clase. Cada métrica se reporta con la tasa base de su partición al lado.
- **Y los naturales se concentran en entrenamiento:** solo el 5.2% de los pares con evidencia de NPASS cae en la prueba, porque comparten andamios en familias grandes. La evaluación por origen sobre la prueba descansa en 346 pares, suficiente para una señal gruesa y no para comparar con intervalos.

**Disjuntar por fuente se descarta, y por qué.** La versión anterior lo proponía como mitigación de la [2.5](#d2-5). No se puede: la fuente no es un atributo del par, y 827 de los 828 pares de CMAUP comparten par con otra fuente ([2.3](#d2-3)). Lo que hace ese trabajo es el **control de atajo** del [#32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32) más el reporte por estrato disjunto de procedencia.

**Y disjuntar por artículo tampoco, en su versión estricta.** Con las referencias que el artefacto ya guarda, conectando dos pares que comparten al menos una: **un solo componente reúne 39,362 pares, el 55.9%**, y el siguiente tiene 601. El 93.8% de los pares tiene una sola referencia, lo que lo hace parecer fácil, pero los compuestos medidos en varios artículos enlazan las referencias entre sí. Queda en su lugar reportar el desempeño **por referencia** dentro de la validación cruzada. Lo midió Pame al revisar el [#86](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/86).

**Cómo se protege hoy la prueba, y lo que falta.** `cargar` (`src/models/tareas.py`) la deja fuera por omisión y exige `incluir_prueba=True` para devolverla, y el modelo de referencia no la pide. Pero eso es una convención: pedirla no falla ni deja registro. La guarda que lo exigiría —evaluar sobre la prueba sin declararlo falla con un mensaje claro y queda anotado— sigue abierta en el [#54](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/54), y conviene tenerla antes de afinar modelos, que es cuando más tienta mirarla.

**Qué lo cambiaría.** Que haga falta evaluar los naturales sobre la prueba con intervalos, y entonces la partición se estratifica por origen —cuesta reconstruir el artefacto y reejecutar el notebook, no rehacer el modelado—; o que ella señale una agrupación por familia química o laboratorio que el andamio no capture.

#### 2.8 · El cruce con COCONUT lo calcula el equipo {#d2-8 .vigente .revisada}

**Estado:** vigente · decidida por el equipo el 17 de octubre de 2026 · revisada: antes se le pedía a ella

**Qué se decidió.** El equipo **calcula el cruce con COCONUT por su cuenta**, desde `smiles_raw`, en lugar de esperarlo. Hasta que esté, la **fuente** es la definición provisional de «natural» y se declara como tal en todo lo que se reporte. Un solo modelo, con el desempeño reportado por origen; la fuente nunca entra como característica.

**Por qué se decide y no se pide.** La versión anterior de esta entrada argumentaba que pedírselo «cuesta una pregunta» y rehacerlo «cuesta una fuente de discrepancia permanente». Que los dos cruces no serán idénticos sigue siendo cierto, pero la comparación estaba mal planteada: con la fuente como proxy, **el 65.4% de los esqueletos naturales también está en ChEMBL**, así que la definición provisional se equivoca en dos de cada tres. Una discrepancia declarada entre dos versiones de COCONUT es un error mucho menor, y sobre todo **medible**: se puede reportar cuántos compuestos cambian de clase entre las dos definiciones. Esperar deja sin forma de contestarse la pregunta central del proyecto, que es si el modelo sirve para productos naturales.

**Qué lo cambiaría.** Que ella aporte el cruce, y entonces pasa a ser la definición y el nuestro queda como comprobación. Eso no obliga a rehacer nada: la definición de origen es una columna de metadatos, no una característica del modelo.

**Qué pasó.** Priorizar productos naturales con actividad neuroprotectora es el objetivo del proyecto, y es esta fase la que lo cumple. Pero el archivo de actividad no trae una marca de «natural»: lo más cercano es la **fuente**, porque NPASS y CMAUP son bases de naturales y ChEMBL es sobre todo sintético. Esa fuente está confundida con la vía de etiquetado ([2.5](#d2-5)): los 15,293 registros de NPASS y CMAUP no traen pChEMBL. Además, el 65.4% de los esqueletos naturales (2,727 de 4,172) también aparece en ChEMBL, así que la fuente no separa limpiamente el origen, y solo 1,445 esqueletos existen únicamente en NPASS y CMAUP. Ojo con el método: `inchikey_source` viene vacío en los 187,354 registros de ChEMBL, así que el solapamiento se calcula desde `smiles_raw`. A diferencia de la fase 1, aquí hay un desplazamiento de dominio real: casi todo el entrenamiento es ChEMBL y el uso final son naturales.

**Por qué se le pregunta a ella y no lo resuelve el equipo.** El archivo de permeabilidad llegó ya cruzado contra COCONUT, con tres columnas (`coconut_id_exact_match`, `coconut_ids_key14_match`, `coconut_matches_key14`), y ese cruce es el que sostiene el hallazgo central del Avance 1. El de actividad no trae ninguna: las únicas columnas de procedencia son `source` y `inchikey_source`, y el diccionario no menciona COCONUT. El equipo podría intentarlo por su cuenta desde `smiles_raw`, que está en los 202,647 registros, pero sería un cruce distinto del suyo —otra versión del catálogo, otra regla de estandarización— y los dos no serían comparables entre fases, que es justamente lo que el proyecto necesita. Pedírselo cuesta una pregunta; rehacerlo cuesta una fuente de discrepancia permanente.

**Se propone, mientras tanto.** Usar la **fuente como definición provisional** de «natural», declarándola como tal en todo lo que se reporte. Entrenar un solo modelo y reportar el desempeño por origen, con la partición disjunta por fuente de la [2.7](#d2-7) para ver si falla al pasar de ChEMBL a naturales. Un modelo aparte, o ponderar a los naturales, solo si esa evaluación lo muestra. Si llega el cruce, la definición pasa a ser ese cruce y la fuente queda como comprobación.

#### 2.9 · Clasificar con un corte o predecir la potencia {#d2-9 .propuesta}

**Estado:** propuesta · se decide en el Avance 4, no bloquea el Avance 3

> **Pregunta:** ninguna para la patrocinadora. Es decisión del equipo, y de hecho **resuelve** una de las suyas: con regresión, el corte pasa a ser una decisión de lectura y la [2.3](#d2-3) deja de necesitar su ratificación.

**Qué pasó.** La [2.3](#d2-3) construye una etiqueta binaria con un corte global, y hay tres razones medidas para dudar de ese formato: el corte no es estimable sin desenlace, el mismo corte deja `LRRK2` en 98.1% de activos y `NFE2L2` en 50.7%, y la clasificación tira el orden dentro de cada clase —un compuesto a 0.05 µM y otro a 9 µM reciben la misma etiqueta— cuando lo que se entrega es un **ranking**.

**Qué cuesta cada forma:**

| Forma | Pares | Negativos | Qué pierde |
|:--|--:|--:|:--|
| Clasificación a 10 µM | 66,121 | 18,107 · 27.4% | el orden dentro de cada clase |
| Regresión sobre exactas | 56,229 | 9,169 · 16.3% | **8,938 negativos**, el 49.4% de la clase |
| **Regresión censurada** | **66,121** | — | nada de la población |

La regresión sobre mediciones exactas no pierde al azar: el 98.0% de los pares activos tiene medición exacta y solo el 50.6% de los negativos, porque la mitad de la evidencia de inactividad **existe solo como censurada**. Un segundo modelo entrenado así tendría un ranking optimista de un modo difícil de auditar.

**Se propone.** Un solo modelo: **regresión sobre [pActividad](glosario.md) con los censurados como observaciones censuradas por la izquierda**, no borrados. Un `>` de 10 µM no es dato faltante, es la información «pActividad < 5», y el propio diccionario de la patrocinadora lo pide así: «en regresión no deben usarse como si el valor fuera exacto: se excluyen o **se usa un método para valores censurados**». No es maquinaria nueva: XGBoost lo trae como objetivo `survival:aft` con límite inferior y superior por observación, y XGBoost ya es candidato en la [1.5](#d1-5).

Con eso la clasificación sale gratis umbralando la predicción, así que el MCC y el AUPRC de la [C.1](#dc-1) siguen reportándose y comparándose contra el baseline. **La clasificación a 10 µM se conserva como baseline del Avance 3**, que es el papel que le toca: ser el piso que la censurada tiene que superar. Dos modelos principales no, porque producirían dos rankings y nada diría cuál obedecer.

**Ese baseline ya existe, y dice dos cosas.** Las tres canalizaciones de la [1.5](#d1-5), sin afinar, sobre los 54,369 pares de entrenamiento y validación (10,071 grupos, 71.4% de activos), con la diana como característica y la misma validación cruzada agrupada de la fase 1; la prueba no se toca (`scripts/experimento_baseline.py --tarea actividad`, corrida `experimentos/2026-10-18-artemio-2.3-baseline-actividad-descriptores-diana-10um/`):

| Canalización | AUROC | IC 95% | MCC |
|:--|--:|:--|--:|
| Bosque aleatorio | 0.866 | [0.859, 0.874] | 0.495 |
| Boosting por histogramas | 0.857 | [0.848, 0.865] | 0.486 |
| Regresión logística | 0.796 | [0.786, 0.806] | 0.387 |

Aquí sí se distingue la logística, por 6 a 7 puntos de AUROC y con intervalos que no se tocan, al revés que en la fase 1. Entre el bosque y el boosting no se distingue. **Y el agregado no describe a los naturales:** por procedencia, el AUROC del bosque es 0.858 sobre los pares que solo tiene ChEMBL, 0.637 sobre los mixtos y **0.611 [0.572, 0.647]** sobre los que solo tiene NPASS (boosting 0.629 y logística 0.585), que coincide con la medición de la [2.3](#d2-3), hecha con otra configuración del bosque (0.613). Es un solo modelo con la diana como característica, no uno por diana como propone la [2.2](#d2-2); afinar y separar por diana es del Avance 4.

**Qué cuesta.** La pérdida censurada es más maquinaria y su calibración importa. SHAP corre sobre `survival:aft`, pero atribuye sobre log-potencia, que es más difícil de narrar a un biólogo que «esta subestructura empujó hacia activo»; la [C.2](#dc-2) pide dos métodos que concuerden y sigue siendo viable, pero el relato cambia. Y las métricas de clasificación saldrían de un modelo que no las optimizó directamente.

**Por qué conviene aunque cueste.** El ranking final combina las dos fases ([C.3](#dc-3)). Si la componente de actividad es una clase y no un número, la combinación pierde resolución; y la forma principista de combinarlas no es sumar dos puntajes, es **comparar la potencia predicha contra la exposición alcanzable**, que es lo que la fase 1 predice. Un compuesto BBB− alcanza menos concentración en cerebro, así que necesita más potencia para servir.

**Y es la respuesta a lo que la patrocinadora pidió** —«a partir de qué valor ya se vuelve algo significativo»— hasta donde se puede contestar sin desenlace: el modelo dice qué potencia espera, y el desempeño en función de la potencia dice desde dónde el modelo separa bien.

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
| S2.10 | La matriz de características sirve para la fase 2 | Acotado | Ya existe y se usa: 70,384 pares sobre 59,532 esqueletos, 201 descriptores más 26 indicadores de diana (227 columnas), y con ella el modelo de referencia da AUROC 0.866 sobre entrenamiento y validación ([2.9](#d2-9)). Pero **no describe a los naturales**: sobre los pares que solo tiene NPASS baja a 0.611 [0.572, 0.647] ([2.9](#d2-9); la [2.3](#d2-3) lo mide con otro bosque y da 0.613) | Reportar siempre por procedencia; si con los modelos afinados sigue cerca del azar, decir que el modelo no sirve para naturales |
| S2.11 | La fuente (NPASS y CMAUP) identifica a los productos naturales | Sin comprobar | El 65.4% de los naturales también está en ChEMBL y solo 1,445 esqueletos son exclusivos de NPASS y CMAUP ([2.8](#d2-8)) | Definir «natural» por cruce con COCONUT si se puede |

