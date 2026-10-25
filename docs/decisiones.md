# La ruta del proyecto

Bitácora de lo que se decide en cada fase y de las posibilidades que siguen abiertas. Se alimenta **por fase, no por avance**: la fase 1 es la permeabilidad de la barrera hematoencefálica (BBB+/BBB−) y la fase 2, la actividad neuroprotectora por diana. Ambas parten de los archivos que entregó la patrocinadora el 25 de septiembre. Cada fase tiene sus **decisiones** (lo que se resolvió o se propone), sus **supuestos** (lo que se dio por cierto para avanzar y puede ser falso) y, en cada entrada, la pregunta que queda por resolver.

Los términos están en el [glosario](glosario.md). Cuando una decisión cambia se deja visible la versión anterior.

## Estado de un vistazo

**Marco común** (aplica a las dos fases)

| # | Decisión | Estado | Consulta |
|:--|:--|:--|:--|
| [C.1](#dc-1) | Métricas: MCC y AUPRC en clasificación; Spearman y concordancia en regresión | Vigente · revisada | |
| [C.2](#dc-2) | Dos métodos de atribución independientes | Vigente | |
| [C.3](#dc-3) | Comprobar si combinar las dos predicciones mejora la selección | Propuesta | |
| [C.4](#dc-4) | PAINS: aplicarlos a los resultados finales | Propuesta | |
| [C.5](#dc-5) | El entregable es una lista priorizada; métricas de ranking por escenario | Vigente | 17 oct · 24 oct |
| [C.6](#dc-6) | Licencia y uso académico de los resultados | Propuesta | |
| [C.7](#dc-7) | La ventana terapéutica: potencia contra citotoxicidad | Propuesta | |

**Fase 1 · Permeabilidad**

| # | Decisión | Estado | Consulta |
|:--|:--|:--|:--|
| [1.1](#d1-1) | No filtrar por la columna de grupo A–D | Vigente · revisada | |
| [1.2](#d1-2) | Partición por andamio, nunca aleatoria | Vigente | |
| [1.3](#d1-3) | Descriptores RDKit más Morgan/ECFP4 | Vigente | |
| [1.4](#d1-4) | Las 6 filas con logBB sin clase | Propuesta | |
| [1.5](#d1-5) | Tres modelos candidatos; de ahí, si escalar y si reducir dimensión | Propuesta | |
| [1.6](#d1-6) | Naturales en la fase 1: evaluar por origen, no entrenar por separado | Vigente | 17 oct |
| [1.7](#d1-7) | Tamaño L de Sort & Slice: 2048 de trabajo; 512 es posible con XGBoost o Random Forest | Propuesta | |
| [1.8](#d1-8) | Los 131 esqueletos con etiquetas contradictorias | Abierta | |

**Fase 2 · Actividad**

| # | Decisión | Estado | Consulta |
|:--|:--|:--|:--|
| [2.1](#d2-1) | El alcance: cinco categorías de enfermedad | **Ratificada** · revisada | 17 oct |
| [2.2](#d2-2) | Por diana, con multitarea como comparación | Vigente · revisada | 17 oct |
| [2.3](#d2-3) | De dónde sale la potencia y dónde se corta «activo» | Vigente · revisada | 17 oct · 24 oct |
| [2.4](#d2-4) | Los 88,098 registros sin diana de la lista | Propuesta | 24 oct |
| [2.5](#d2-5) | La fuente confundida con el etiquetado | Vigente · medida | 24 oct |
| [2.6](#d2-6) | La partición de prueba que sí se había reservado | **Ratificada** · revisada | 17 oct · 24 oct |
| [2.7](#d2-7) | Partición de la fase 2 | Vigente · revisada | |
| [2.8](#d2-8) | El cruce con COCONUT lo calcula el equipo | Vigente · revisada | 17 oct |
| [2.9](#d2-9) | Regresión de la potencia; la clasificación se deriva de ella | Vigente | 24 oct |
| [2.10](#d2-10) | El objetivo se guarda como intervalo, no como etiqueta | Vigente | 24 oct |
| [2.11](#d2-11) | Dirección del efecto: la afinidad cuenta | Vigente | 24 oct |
| [2.12](#d2-12) | Los inactivos de DrugMatrix | Propuesta | 24 oct |

Estados: **vigente** (se trabaja sobre ella, y es reversible), **revisada** (se decidió, se midió y cambió; conserva visible la versión superada), **propuesta** (hay recomendación del equipo, aún sin adoptar), **abierta** (sin recomendación) y **ratificada** (la patrocinadora la revisó y la decidió: la 2.1 y la 2.6, el 15 de octubre de 2026). *Consulta* es la fecha en que la patrocinadora recibió la entrada: el 17 de octubre la [consulta](../consulta.qmd) con lo decidido por el equipo y el 24 el correo con las dudas, cuya respuesta está [en la fase 2](#respuesta-correo-24-oct).

---

## Marco común {#comun}

Lo que vale para las dos fases.

### Decisiones

#### C.1 · Métricas: MCC y AUPRC en clasificación; Spearman y concordancia en regresión {#dc-1 .vigente .revisada}

**Estado:** vigente · revisada el 25 de octubre: la fase 2 pasa a regresión ([2.9](#d2-9))

> **Pregunta:** ¿Qué punto de operación corresponde? Ver [C.5](#dc-5).

**Qué pasó.** Hay 1.74 positivos por negativo: un modelo que prediga siempre BBB+ acierta el 63.5% sin aprender nada. El Avance 2 reportó AUPRC sobre la clase positiva, que es la mayoritaria, con línea base 0.573; los valores de 0.70–0.86 parecían buenos y eran poco informativos. Quedó documentado en el notebook.

**Se decidió.** En la **fase 1**, que clasifica, las métricas principales son MCC y AUPRC sobre la clase minoritaria; exactitud y AUROC no se reportan solos. En la **fase 2**, que hace regresión, son el índice de concordancia de Harrell y Spearman, que toleran la censura, y RMSE solo sobre las mediciones no censuradas. Las de clasificación se calculan además sobre la clase derivada del corte, y las de ranking están en la [C.5](#dc-5).

#### C.2 · Dos métodos de atribución independientes {#dc-2 .vigente}

**Estado:** vigente · requisito de la patrocinadora

**Se decidió.** Al menos dos métodos de atribución independientes; solo se reportan como confirmadas las subestructuras en que coinciden. Un modelo interpretable simple se entrena en paralelo como control. Toda afirmación estructural se contrasta primero contra TPSA (<67 Å²) y HBD (≤1), que dominan empíricamente. Aplica a las dos fases.

### Propuestas

#### C.3 · Comprobar si combinar las dos predicciones mejora la selección {#dc-3 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Vale la pena probar, como experimento aparte con los 1,033 compuestos que tienen las dos mediciones, si combinar la predicción de permeabilidad con la de actividad elige mejor que cada una por separado?

**Qué pasó.** Hay dos modelos, uno de permeabilidad y uno de actividad, y el ranking final usará los dos. Falta saber si juntarlos ayuda. Solo 1,033 esqueletos tienen medición en los dos conjuntos (1.0% de la fase 2, 25.7% de la fase 1), así que son el único lugar donde se puede comprobar contra datos reales. Reservarlos obligaría a sacarlos también del entrenamiento de la fase 1, o habría fuga, y costaría una cuarta parte de sus datos.

**Se propone.** Condicionada a que la patrocinadora considere que vale la pena. Cada fase se entrena y evalúa con su protocolo ([1.2](#d1-2), [2.7](#d2-7)), sin reservar nada. Si la patrocinadora lo aprueba, el experimento va en dos pasos:

1. **Con datos solamente, sin modelos.** Cruzar las mediciones reales de los 1,033: permeabilidad medida (BBB+ o BBB−) contra actividad medida, por diana. Se plantea sin umbral: comparar la distribución de la potencia medida entre los BBB+ y los BBB−. Si los BBB− son tan potentes como los BBB+, la permeabilidad cambiaría el orden del ranking; si no, aporta poco. No hay que decidir qué es «activo», porque el corte se aplica al final y cambia el resultado (con ≥ 5 queda 61.7% de activos por registro y con ≥ 6, 44.4%, [2.3](#d2-3)): una lectura del tipo «casi todos los activos son BBB+» podría salir verdadera con un corte y falsa con el otro. Así se puede hacer en cuanto se apruebe, sin esperar a la 2.3 ni a ningún modelo.
2. **Con los modelos ya entrenados.** Medir si la combinación acierta más que cada predicción sola. Como el modelo de la fase 1 habrá visto parte de esos compuestos, se usan predicciones fuera de muestra (validación cruzada agrupada por andamio). Necesita el modelo de actividad ([2.9](#d2-9)) y los modelos afinados de los Avances 3 a 5. Cuántos de los 1,033 caen en la prueba de ambas fases no está medido.

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

**Por qué una curva.** No hay que elegir **un** punto de operación: entregando la curva, mover el corte no cuesta reentrenar nada, es leer otra fila de la misma tabla. Ejemplo: de una lista de veinte donde acierte cuatro de cada cinco se pasa a una de cien donde acierte una de cada dos, sin tocar el modelo.

**Métricas del ranking (propuesta; la principal se declara antes de ver resultados).** Cuántos compuestos se pueden ensayar no se sabe, así que se resuelve como análisis de escenarios y se dice cuál gobierna bajo cada supuesto. Ejemplo: si el laboratorio ensaya 20 compuestos, importa que los primeros 20 funcionen; si ensaya 1,000, importa no dejar fuera candidatos reales.

| Escenario | Qué manda | Métricas |
|:--|:--|:--|
| Pocos compuestos (el realista) | ordenar bien; el falso positivo es el caro porque gasta presupuesto de ensayo | **enriquecimiento al 1%** (principal), enriquecimiento al 5%, precisión en los primeros 100, BEDROC, área bajo la curva de precisión-recall |
| Cribado amplio | la sensibilidad: no perder candidatos reales | recall a precisión fija, enriquecimiento al 5% |

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

**Qué criterio decide si una característica derivada se queda, cuando el desempeño no distingue.** Dos corridas independientes —la del equipo y la de un contraste con otra rejilla y otro selector— coinciden en que ninguna de las tres derivadas mueve el MCC: todos los intervalos incluyen el cero. Con eso, **el desempeño no puede ser el criterio**, ni para conservarlas ni para quitarlas. El que se adopta es **interpretabilidad con costo cero**: se quedan las que se pueden leer y no cuestan nada medible.

Por ese criterio se conserva `regla_2p`, que es la regla publicada —TPSA < 67 Å² y HBD ≤ 1— y sirve para contrastar lo que el modelo aprende con lo que ya se sabía; y se conserva `tpsa_por_mw`, porque quitarla no mejora nada y moverla cambiaría cifras en el notebook 02, en el baseline y en el reporte por un cambio sin efecto. `lipo_neta` no entra, pero por otra razón: correlaciona 0.975 con `MolLogP`, que está protegido.

**Qué lo cambiaría:** que con los modelos afinados del Avance 4 alguna derivada estorbe con un intervalo que excluya el cero, o que la explicabilidad muestre que `tpsa_por_mw` confunde más de lo que aclara.

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
- **Sin escalar y con el `C` que se usa, la regresión logística no converge**, y eso es lo que justifica escalar. Agota las 3,000 iteraciones de `lbfgs` en los 15 pliegues y avisa de no haber convergido en los 15; con cualquiera de las tres transformaciones converge sin aviso, en 53 iteraciones con min–max y 137 a 144 con las otras dos. Su MCC de 0.687 no es el desempeño de «no escalar»: es donde se detuvo el optimizador al agotar su presupuesto, así que esa fila no es comparable con el resto. El tiempo (0.437 s contra 0.007 s) es la consecuencia visible; las iteraciones y el aviso son la prueba. El Random Forest tarda lo mismo con las cuatro, lo que descarta que los datos sean más difíciles sin escalar.
- **El escalado no arregla el condicionamiento**, y conviene no atribuírselo: el número de condición de la matriz va de 5.9e+17 a 1.2e+21 con las cuatro transformaciones. Viene de las columnas casi colineales —120 pares con |r| > 0.95— y lo trata la selección, no el escalado.
- **La desventaja de Yeo-Johnson era del `C`, no de la transformación**, y eso lo cambió la revisión del Avance 2. Con el mismo `C = 1` para las cuatro, Yeo-Johnson queda 0.030 de MCC por debajo de min–max y pierde en 12 de los 15 pliegues; con el `C` que cada transformación elige para sí, **las dos empatan en 0.695** y la mejor pasa a ser estandarización por 0.004 (t = 0.5). Los `C` elegidos están a dos órdenes de magnitud de distancia —0.01 con estandarización y con Yeo-Johnson, 1.0 con min–max—, así que un solo `C` compara la transformación y la regularización a la vez, y el valor fijado resultó ser el que min–max prefiere.
- **Versión superada (12 de octubre), y qué la cambió.** Esta entrada decía que Yeo-Johnson era «consistentemente la peor» y proponía como hipótesis que la potencia comprimiera las colas, donde vive parte de la señal. El apoyo de esa hipótesis era que comparar Yeo-Johnson con estandarización aísla el paso de potencia —`PowerTransformer(standardize=True)` es potencia y luego estandarización— y daba +0.025 (t = 1.5). Con el `C` propio ese contraste cae a +0.004: **no había efecto que explicar**. Es el mismo modo de fallar que la 2.3 ya tuvo: una explicación construida sobre un número antes de comprobar que el número mide lo que parece. Queda el hecho sin consecuencia: Yeo-Johnson corrige mejor la asimetría, de 106 a 66 descriptores muy asimétricos, y eso no se traduce en mejor predicción.

- **Pero «no converge» sin más es más fuerte que la medición, y la versión anterior de esta entrada lo decía así.** Sin escalar, sobre las 5,557 filas de entrenamiento y las mismas 206 columnas, la convergencia depende del `C`: con `C = 1e-4` converge en 914 iteraciones y con `C = 1e-3` en 2,829; con `C ≥ 0.01` agota las 3,000 y avisa. Lo medido es que **no converge con el `C` que se usa**, no que no converja con ninguno. **Qué no se midió:** qué desempeño da sin escalar con una regularización tan fuerte — la búsqueda de `C` se omitió ahí por costo, así que «no escalar» sigue sin tener una cifra comparable, pero por una razón distinta de la que esta entrada daba.
- **La tabla mide las 206 columnas anteriores a la selección**, con las tres derivadas, no las 151 de la matriz final. Es a propósito —el escalado se decide antes de seleccionar— pero no se puede leer como medido sobre lo que entra al Avance 3.

El error estándar se corrige como en la [1.7](#d1-7), por Nadeau y Bengio, y la diferencia se toma pareada por pliegue. Se reportan intervalos y no un veredicto de «dentro del ruido»: ese umbral de un error estándar sirve para elegir el menor L —ahí ser laxo es conservador— pero no para afirmar que una diferencia existe, donde apenas es t = 1.

**Se propone.** Tres modelos con la misma partición:

| Modelo | Por qué | ¿Escalar? |
|:--|:--|:--|
| **Regresión logística regularizada** | Control interpretable exigido por la [C.2](#dc-2) | **Sí** |
| **Random Forest** | Baseline estándar; tolera descriptores correlacionados | No |
| **Gradient boosting** (XGBoost o LightGBM) | Suele ser el más fuerte con descriptores tabulares | No |

Solo la logística necesita escalar, así que cada modelo lleva su canalización y los árboles reciben la matriz sin transformar. Para la logística **se propone escalar**, porque sin escalar no converge con el `C` que se usa, y **min–max como opción de partida**, no como conclusión: entre las tres formas de escalar la medición no da base para elegir, y la alternativa de no escalar deja un modelo que agotó sus iteraciones. Ya no hay un motivo medido para evitar Yeo-Johnson: lo había mientras el `C` era el mismo para todas, y con el suyo la diferencia desaparece. **Cuál de las tres se adopta lo cierra el equipo**, no la patrocinadora: la medición no las distingue en desempeño y la razón para escalar resultó ser la convergencia, así que no queda un criterio que dependa de su conocimiento del dominio. Lo que sí depende de ella es la pregunta de arriba, entre explicabilidad y reducción de dimensión, porque eso se decide por lo que quiere poder leer en el resultado y no por una cifra. Se resuelve en el Avance 3, con los modelos afinados y suficientes evaluaciones para cerrar los intervalos. El Avance 2 guarda la matriz filtrada en dos versiones, transformada con Yeo-Johnson y sin transformar, con las mismas columnas; y **cambiar la transformación de trabajo ya no obliga a repetir la selección**: la §9 filtra por valor modal y por correlación de Spearman sobre los valores crudos, y el notebook comprueba que las 151 columnas son las mismas con estandarización, con min–max y con Yeo-Johnson. El PCA no se adopta, por explicabilidad, y **tampoco se guarda**: el notebook lo conserva solo como vista del espacio químico. Lo que ejecutó el Avance 2 es una propuesta: la alternativa (no escalar, no reducir dimensión) sigue en pie hasta que se acuerde. SHAP con `TreeExplainer` sirve a los árboles y Chemprop queda como comparación opcional del Avance 4.

#### 1.6 · Naturales en la fase 1: evaluar por origen, no entrenar por separado {#d1-6 .vigente}

**Estado:** vigente · decidida por el equipo el 17 de octubre de 2026

**Qué se decidió.** Un solo modelo, con el desempeño reportado por origen **dentro de cada grupo A–D** y no solo en el global. La causa de la brecha —curación o química— queda como **limitación declarada**, no como pregunta abierta.

**Por qué se decide y no se pregunta.** La pregunta era si existe una razón de curación que explique que los naturales crucen igual en el grupo A y 21 y 17 puntos menos en B y C. Solo ella podría saberlo, pero la respuesta **no cambia lo que hay que hacer**: con cualquiera de las dos lecturas la decisión es la misma —un modelo, evaluado por origen dentro de cada grupo— porque es esa evaluación la que distingue las dos explicaciones. Si el modelo rinde peor en naturales solo en B y C, está aprendiendo ruido de curación; si falla también en A, es química. *Versión superada (17 de octubre):* esa prueba, medida, no distinguió las dos lecturas, porque el modelo baja en A con los dos orígenes que se pueden medir (ver «Evaluación por origen»). La causa sigue como limitación declarada.

**Qué lo cambiaría.** *Propuesta pendiente de revisión del equipo*, escrita el 21 de octubre de 2026 con los resultados de la evaluación por origen: que, **a igual grupo A–D, el modelo rinda peor en los naturales exactos que en los compuestos sin equivalente natural**, con un intervalo de la diferencia de AUROC que excluya el cero. Un estrato cuenta como evaluado solo si ese intervalo es lo bastante estrecho para detectar el efecto que importaría, que el equipo fija en 0.05 de AUROC: medio ancho ≤ 0.05. El 0.05 se fijó el 21 de octubre con los resultados ya a la vista, así que no es un valor preregistrado. Un número mínimo de BBB− no sirve para eso, porque los dos orígenes comparados en A (34 y 42 BBB−) superan los 20 casos que el arnés exige para *reportar* un estrato y aun así su intervalo no permite concluir. Con los datos actuales (ancho del intervalo con los tres modelos, `notebooks/datos/analisis_origen_fase1.csv`): C es evaluable (0.061 a 0.091) y el criterio no se cumple; B queda en la frontera (0.093 a 0.113) y tampoco se cumple, porque ahí los naturales rinden mejor; **A no es evaluable** (0.220 a 0.233) y queda como límite declarado, no como un umbral que se baje hasta que quepa. Hacerlo evaluable pediría unas cinco veces más BBB− en A, porque el ancho baja con la raíz del tamaño. Con estos datos el criterio solo lo pueden sostener C, que cumple el ancho con los tres modelos, y B, que lo cumple solo con el bosque (ver «Evaluación por origen» más abajo, que explica por qué la redacción anterior ya no basta). Ahí sí habría que considerar entrenar aparte.

*Versión superada (17 de octubre de 2026):* «Que la evaluación por origen muestre que el modelo falla en naturales dentro del grupo A, que es el que tiene logBB medido. Ahí sí habría que considerar entrenar aparte.» Se sustituye porque, medida, es ambigua: dentro del grupo A el rendimiento es bajo con los dos orígenes que se pueden medir y no solo con los naturales.

**Dos cosas que quedan como supuesto declarado,** por si alguien las necesita: los compuestos con análogo natural que difiere solo en estereoquímica (1,005 en las 7,811 filas del archivo de la patrocinadora; 1,003 en las 7,805 que tienen clase) **no** cuentan como naturales, porque la definición que sostiene el hallazgo del Avance 1 es la coincidencia exacta con COCONUT; y no se fija un rango de TPSA propio para naturales, porque el óptimo ya se midió y sube con la diversidad del conjunto.

**Qué pasó.** El archivo de la patrocinadora marca como natural lo que coincide exactamente con COCONUT (columna `coconut_id_exact_match`): 3,366 compuestos, el 43.1% de los 7,805 con clase. Lo demás no es «sintético»: el diccionario distingue 3,366 naturales exactos, 1,005 análogos que difieren solo en estereoquímica y 3,440 sin equivalente natural conocido. Esas tres cifras cuentan las **7,811 filas** del archivo; **sobre las 7,805 con clase** son 3,366, 1,003 y 3,436 (los 3,366 naturales tienen todos clase; faltan 2 análogos y 4 sin equivalente). Las cifras del baseline por origen (más abajo) cuentan otra cosa: las 6,306 filas que evalúa el baseline (`n_filas` de su `metricas.json`), que no incluyen la prueba reservada.

**Los tres orígenes cruzan distinto** (sección 5 del [notebook 01](../notebooks/01_EDA.ipynb), revisada el 19 de octubre): naturales exactos 52.7% BBB+ [49.7, 55.8], análogos estereoquímicos 39.7% [34.6, 44.8] y sin equivalente natural 81.0% [79.1, 82.8], intervalos bootstrap por esqueleto de conectividad que no se solapan (los de Wilson, que tratan como independientes a los estereoisómeros, son entre 1.4 y 1.8 veces más angostos). La brecha entre naturales y compuestos sin equivalente es de **28.3 puntos**. *Versión superada:* el Avance 1 juntaba análogos y compuestos sin equivalente en un grupo «sintético» y reportaba 18.9 puntos (52.7% contra 71.7%). Ese grupo no era sintético —más de una quinta parte (1,003 de los 4,439 con clase) son estereoisómeros de un natural, que cruzan todavía menos— y diluía la brecha. **La regla TPSA/HBD no la explica por completo.** Entre los compuestos que la cumplen, que en TPSA y HBD son casi iguales en los tres orígenes (mediana de TPSA de 37.3, 37.3 y 36.7 Å²), los naturales cruzan 80.9% contra 90.9%. Entre los que no la cumplen la diferencia es mayor (37.8% contra 72.6%), pero ese estrato no es comparable, porque los naturales que no la cumplen son más polares (mediana de TPSA de 108.4 contra 86.5 Å²). Eso descarta que la regla de dos parámetros baste, no que la química explique la brecha.

**La brecha no es uniforme.** Repartida por el grupo de B3DB, casi no existe en el grupo A y aparece en B y C. Lo que distingue a los grupos en el archivo es solo esto: todas las filas de A, y solo ellas, traen `logBB` (1,052 de 1,058); todas las de B, y solo ellas, traen `b3db_threshold` = −1, el valor del corte de logBB de la clase, sin el logBB; C y D no traen ninguno de los dos. *Versión superada:* esta entrada decía que en B y C «la etiqueta viene de una clasificación publicada». Eso no está en el archivo: B3DB no publica el criterio completo de asignación, y la columna de B contradice que B y C se etiquetaran igual. La revisión independiente del notebook 01 lo encontró el 19 de octubre.

| Grupo de B3DB | No natural (BBB+) | Natural (BBB+) | Diferencia (puntos), IC 95% |
|:--|--:|--:|:--|
| A (con logBB medido) | 87.6% (n = 644) | 88.4% (n = 414) | −0.8 [−4.8, +3.2] |
| B | 77.2% (n = 2,166) | 55.9% (n = 1,455) | +21.4 [+18.3, +24.5] |
| C | 58.1% (n = 1,624) | 40.9% (n = 1,451) | +17.2 [+13.7, +20.7] |

Con los tres orígenes por separado (natural exacto, análogo y sin equivalente) el patrón es el mismo: 88.4%, 86.6% y 87.7% en el grupo A; 55.9%, 43.5% y 83.6% en el B; 40.9%, 30.7% y 73.0% en el C (notebook 01, sección 5).

En el grupo A la brecha no es solo «casi inexistente»: queda **acotada a unos ±5 puntos**, lo que excluye cualquier cosa parecida a los 19 globales; en B y C es grande y en la dirección contraria. El grupo D (n = 5 y 46) no permite concluir. Esto es descriptivo y no prueba la causa. Caben dos lecturas que estos datos no distinguen: que la brecha refleje en parte de dónde viene la etiqueta, o un **efecto techo**, porque el grupo A es 88% BBB+ y con casi todo del mismo lado queda poco margen para que los orígenes difieran. Quedan además el eflujo, descriptores no medidos o el sesgo de qué se ensayó. *Versión superada:* esta entrada comparaba la proporción de naturales que cumple la regla TPSA/HBD (6.6 puntos menos, 34.6% contra 41.2%) con la diferencia en la etiqueta. Son dos diferencias de proporciones que no se descomponen una en otra (#85), y la comparación correcta es la de arriba, a igual cumplimiento de la regla.

**Se propone.** Un solo modelo, con el desempeño reportado por separado en naturales y en el resto y declarando siempre qué definición de «natural» se usó. No entrenar por separado: la permeabilidad depende de la estructura y no del origen, habría 3,366 compuestos de un lado y 4,439 del otro, y el segundo grupo mezcla análogos, fármacos y moléculas que simplemente no están en COCONUT. Tampoco el origen como variable, porque en parte sería una pista de la procedencia de la etiqueta. **La evaluación por origen se hace también dentro de cada grupo A, B y C**, no solo en el global: es la misma lógica de la [1.1](#d1-1), que usa A–D para estratificar y nunca para excluir, que se pensó para distinguir las dos explicaciones y, medida, no las distingue (ver abajo). Si un modelo rinde peor en naturales solo en B y C, eso apunta a ruido de curación más que a química, siempre leído contra la tasa base de cada grupo por el efecto techo de A. Se revisa la propuesta solo si se cumple el criterio de «Qué lo cambiaría», que con los resultados de abajo es comparativo (naturales contra compuestos sin equivalente, a igual grupo) y no solo «falla en naturales». Es una **propuesta pendiente de revisión del equipo**, no un criterio adoptado.

##### Evaluación por origen: qué midió el baseline

La herramienta es `cargar("permeabilidad", estratos="origen" | "origen_grupo")` en `src/models/tareas.py` y su opción `scripts/experimento_baseline.py --estratos`; las preguntas que esas cifras dejaban abiertas las contesta `scripts/analisis_origen_fase1.py`. Las cifras son de un modelo, **boosting por histogramas (`HistGradientBoostingClassifier`)**, que es el de mayor [MCC](glosario.md) global del baseline (0.702; `mejor_por_mcc` de la primera corrida); entre paréntesis van el bosque aleatorio y la logística cuando cambian algo. Todo con descriptores, validación cruzada agrupada por andamio y esqueleto (1,048 grupos), 6,306 filas, intervalos del 95% por bootstrap de grupos.

| Estrato | n (BBB−) | [AUROC](glosario.md) [IC 95%] | MCC |
|:--|--:|:--|--:|
| Natural exacto | 2,920 (1,345) | 0.942 [0.922, 0.959] | 0.721 |
| Análogo estereoquímico | 768 (438) | 0.928 [0.891, 0.954] | 0.692 |
| Sin equivalente natural | 2,618 (426) | 0.892 [0.847, 0.930] | 0.514 |
| Natural exacto · A | 348 (34) | 0.870 [0.799, 0.930] | 0.361 |
| Sin equivalente · A | 340 (42) | 0.813 [0.724, 0.891] | 0.250 |
| Natural exacto · B | 1,327 (613) | 0.951 [0.930, 0.969] | 0.766 |
| Sin equivalente · B | 1,470 (230) | 0.882 [0.825, 0.934] | 0.470 |
| Natural exacto · C | 1,229 (683) | 0.945 [0.920, 0.965] | 0.702 |
| Sin equivalente · C | 806 (152) | 0.932 [0.900, 0.957] | 0.656 |

El MCC de la tabla es el promedio del MCC por semilla sobre las predicciones fuera de pliegue; el 0.702 global es el promedio de los 15 pliegues: son estimadores distintos.

Los análogos en el grupo A (64 filas, 8 BBB−) y todos los estratos del D no se reportan, porque la clase minoritaria no llega a los 20 casos que exige el arnés. Los análogos en B y C dan 0.951 y 0.921 de AUROC.

**1. El modelo no rinde peor con los naturales exactos que con los compuestos sin equivalente natural.** Rinde mejor: la diferencia global de AUROC es +0.050 [+0.017, +0.085] (bosque +0.053 [+0.023, +0.086]; logística +0.056 [+0.016, +0.099]). Dentro de cada grupo, el intervalo excluye el cero solo en el B (+0.069 [+0.019, +0.120]); en el A (+0.057 [−0.048, +0.173]) y en el C (+0.013 [−0.015, +0.046]) lo incluye. Las diferencias son pareadas, con remuestreo conjunto de grupos (958 grupos, 166 compartidos entre los dos orígenes).

**2. Dentro del grupo A el rendimiento baja, y no solo en los naturales.** Natural exacto · A queda en 0.870 contra 0.951 en B, una diferencia de −0.081 [−0.157, −0.019] que excluye el cero (bosque −0.090 [−0.177, −0.022]; logística −0.084 [−0.158, −0.015]). Sin equivalente · A queda en 0.813 contra 0.882 en B: −0.069 [−0.175, +0.030], que **no** excluye el cero, aunque va en la misma dirección y tiene un tamaño parecido. Y entre los dos orígenes del grupo A la diferencia es +0.057 [−0.048, +0.173] (bosque +0.041 [−0.069, +0.164]; logística +0.061 [−0.043, +0.186]): no se detecta. **Con 34 y 42 BBB− eso es ausencia de evidencia, no evidencia de ausencia**: un intervalo de ese ancho no descarta una diferencia moderada en cualquiera de los dos sentidos.

**3. La tasa base explica solo una parte.** En A el 90.2% de los naturales y el 87.6% de los otros son BBB+, y el MCC baja con la prevalencia aunque la discriminación no cambie. Un modelo con la sensibilidad y la especificidad globales (0.926 y 0.763) daría en A un MCC de 0.588 en naturales y 0.620 en sin equivalente; el observado es 0.340 y 0.232 (el 0.361 y 0.250 de la tabla promedian el MCC por semilla, estos lo calculan sobre la probabilidad promediada entre semillas). La diferencia está en la especificidad, que cae a 0.500 y 0.286: el modelo manda a BBB+ la mitad y el 71% de los BBB− de A. En sin equivalente la especificidad es baja también fuera de A (0.417 en B, 0.664 en C; global 0.491), y su MCC queda por debajo del esperado en B (0.451 contra 0.649); en natural exacto · B el observado (0.769) supera al esperado (0.704).

Dos observaciones sobre por qué los BBB− de A son difíciles, ambas descriptivas:

- **[Negativos frontera](glosario.md).** El 44% de los BBB− de natural exacto · A (15 de 34) tiene |logBB + 1| < 0.3, es decir, está a menos de 0.3 del corte de −1.0 que define la etiqueta; en sin equivalente · A es el 33% (14 de 42). Con el boosting, el 30.2% de los 116 errores del grupo A cae ahí, contra el 7.8% de sus 631 aciertos. Solo el grupo A trae logBB (cobertura 99.3%; en el B es 0%), así que esto no se puede mirar en los otros.
- **TPSA.** La mediana de TPSA de los BBB− de natural exacto · A es de 91.7 Å², contra 147.2 en natural exacto · B: está por debajo del umbral óptimo de este conjunto (101.9 Å² en el completo, 107.0 en entrenamiento; ver «Umbral de TPSA»), del lado donde la mayoría de los compuestos son BBB+, lo que podría hacerlos difíciles para el modelo. Es una hipótesis: no se midió qué descriptores usa el modelo en estos compuestos, y no explica la caída en los sin equivalente, cuya mediana casi no cambia entre A y B (83.9 contra 87.4 Å²).

Y una advertencia: los descriptores predicen la pertenencia al grupo A con AUROC 0.844 (el grupo A es el 11.9% de las filas) y al origen natural exacto con 0.773 (46.3%). Eso indica que la información del grupo está disponible y que el modelo *podría* estar aprendiendo el prior de BBB+ del grupo en vez de la química; no lo demuestra, porque probarlo exigiría quitar esa información y medir qué cambia. No se hizo.

**4. El corte de 0.5 mezcla discriminación, calibración y prevalencia.** Por eso, para comparar estratos con prevalencias de 0.12 a 0.90, la medida primaria es el AUROC y el MCC va al lado, no en su lugar. Aquí el AUROC se usa como medida primaria porque no depende de la prevalencia; la regla general del proyecto ([C.1](#dc-1)) sigue siendo MCC y AUPRC de la clase minoritaria, que son las que miden el desempeño sobre BBB− en cada estrato.

**Límites.** Los intervalos remuestrean grupos y cubren la variación entre grupos, no la de reentrenar (las tres semillas comparten filas). El script calcula también el AUPRC de BBB− menos su línea base, y esa medida va en contra de los naturales en el grupo C (boosting −0.229 [−0.314, −0.134], igual con los tres modelos). No se usa porque no es comparable entre estratos de prevalencia distinta: su máximo es 1 − π, y los naturales tienen más BBB− (55.6% frente a 18.9% en C), así que la resta los penaliza por construcción. Los contrastes (cuatro entre orígenes y dos entre grupos, por tres modelos y cuatro medidas (AUROC, dos variantes de MCC y AUPRC menos línea base)) no están corregidos por comparaciones múltiples: se lee el patrón entre modelos y no un intervalo suelto. Los números salen de `experimentos/2026-10-21-antonio-1.6-baseline-permeabilidad-descriptores-origen/`, `…-origen_grupo/` y `…-analisis-origen/` (`metricas.json`), y de `notebooks/datos/analisis_origen_fase1.csv`.

**La decisión no cambia.** Sigue siendo un solo modelo, evaluado por origen dentro de cada grupo. El motivo: la caída en A no es propia de los naturales: en los compuestos sin equivalente se observa una de tamaño parecido (−0.069 de AUROC, con un intervalo que incluye el cero; en MCC lo excluye con boosting y logística), así que entrenar aparte para los naturales no la resolvería. Lo que sí cambia, como **propuesta pendiente de revisión del equipo**, es el criterio que reabriría la decisión (ver «Qué lo cambiaría»); y la lectura de la prueba de la sección «Por qué se decide» —«si falla también en A, es química»— deja de distinguir las dos explicaciones, porque el modelo sí falla en A con ambos orígenes y la medición no separa curación de química.

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
| S1.5 | La brecha entre naturales y el resto es química | Sin comprobar | Con tres orígenes es de 28.3 puntos contra los compuestos sin equivalente natural (52.7% contra 81.0% BBB+; la versión de dos grupos daba ~19), pero no existe en el grupo A (88.4%, 86.6% y 87.7% en los tres orígenes, con un posible efecto techo porque A es 88% BBB+) y sí en B y C ([1.6](#d1-6)); entre los que cumplen la regla TPSA/HBD persiste (80.9% contra 90.9%). El baseline no rinde peor con los naturales exactos que con los compuestos sin equivalente (AUROC 0.942 contra 0.892 con boosting); en el grupo A rinde bajo con ambos orígenes (0.870 y 0.813), así que no distingue curación de química ([1.6](#d1-6)) | Hecho ([1.6](#d1-6)). Pendiente: quitar a los descriptores la información del grupo y medir qué cambia en A; más BBB− en A para tener potencia |
| S1.6 | Los valores atípicos son alertas, no errores | Asumido | No se recortan ni eliminan | — |
| S1.7 | Mandar los 312 acíclicos a entrenamiento es una regla razonable | Sin comprobar | Es el valor por omisión de `scaffold_split` y no sale de ninguna medición; ninguno entra a validación ni a prueba. Dentro del entrenamiento hay 127 filas en 44 esqueletos compartidos (estereoisómeros) | Escribir y justificar la regla antes del baseline; en la validación cruzada se agrupan por esqueleto de conectividad |
| S1.8 | El conjunto externo de Spielvogel sirve para validar | Desmentido | 154 nombres, sin SMILES ni InChI | Conseguir las estructuras |
| S1.9 | Yeo-Johnson es una buena transformación | Sin comprobar · **revisado** | La validación cruzada del 12 de octubre la dejaba por debajo de min–max en 12 de los 15 pliegues, y esta fila la daba por «desmentida en parte». Era un artefacto del `C` fijo: con el `C` que cada transformación elige para sí, Yeo-Johnson y min–max empatan en 0.695 de MCC ([1.5](#d1-5)). Ni mejor ni peor que las otras dos; la matriz guardada la asume y nada en la medición obliga a cambiarla | Cambiar de transformación y reentrenar: la selección de la §9 ya no depende de ella —se hace sobre los valores crudos y el notebook comprueba que da las mismas 151 columnas con las tres— y las dos versiones de la matriz, transformada y sin transformar, están guardadas |
| S1.10 | El PCA no aporta | Sin comprobar | No adoptado por explicabilidad, y ya no se mide: el notebook vigente conserva el PCA solo como vista del espacio químico. La comparación de desempeño que esta fila citaba —diferencia de −0.008 en Random Forest, IC 95% −0.070 a +0.055— es de una versión anterior del notebook ([1.5](#d1-5)) | Solo como exploración (visualizar el espacio químico, comparar particiones); no es candidato del Avance 3 por la explicabilidad |
| S1.11 | Las tres características derivadas aportan | **Desmentido** | Medido con el modelo y no con el AUC individual (`scripts/experimento_derivadas.py`, corrida `experimentos/2026-10-18-artemio-1.5-derivadas/`): diferencia pareada de MCC contra no usarlas, 15 evaluaciones, con el error estándar corregido por Nadeau y Bengio como en la [1.7](#d1-7) — logística, las tres, +0.0001 ± 0.0031; Random Forest, las tres, −0.0062 ± 0.0086 (IC 95% [−0.025, +0.012]); `tpsa_por_mw` sola, +0.0009 ± 0.0073. Todos los intervalos incluyen el cero: no hay evidencia de que ninguna aporte, y tampoco de que con árboles las tres juntas estorben, aunque su estimación puntual sea negativa. *Versión superada (22 de octubre):* esta fila citaba el error estándar ingenuo (±0.0014, ±0.0039, ±0.0034), 2.2 veces menor, y concluía que con árboles las tres juntas «quedan por debajo»; con el corregido, que es el que guarda la corrida, esa lectura no se sostiene. `lipo_neta` además ya no entra: correlaciona 0.975 con `MolLogP`, que está protegido | Nada que rehacer; `regla_2p` y `tpsa_por_mw` siguen en la matriz, y retirarlas es un cambio de una línea en la §6. El criterio para conservarlas está en la [1.5](#d1-5): interpretabilidad con costo cero |
| S1.12 | Todo lo que aprende de los datos se ajusta solo con entrenamiento | Comprobado | Media tras escalar: 0.0000 en entrenamiento, 0.0048 en evaluación | — |
| S1.13 | L = 2048 es un tamaño razonable de vocabulario | Acotado | Medido: el MCC no distingue tamaños desde ~128 y en AUPRC 2048 es el menor L dentro del ruido en dos de tres modelos ([1.7](#d1-7)); falta repetirlo con modelos afinados | Elegir L por modelo en el Avance 3 |
| S1.14 | El nombre del compuesto lo identifica | Desmentido | 1,109 filas (14.2%) no traen nombre; de las que sí, 347 de los 5,091 nombres apuntan a más de una estructura (945 filas) y 1,075 esqueletos cargan más de un nombre; «ritonavir» aparece con cuatro estructuras ([1.8](#d1-8), `scripts/cifras_nombres_fase1.py`) | Cruzar siempre por estructura, nunca por nombre; afecta a la S1.8 |

---

## Fase 2 · Actividad {#fase2}

202,647 mediciones (ChEMBL 187,354, NPASS 11,992, CMAUP 3,301) sobre 99,585 esqueletos. Cada fila es un compuesto contra una proteína, con tipo (IC50, Ki, EC50…), relación (`=`, `>`, `<`), valor y unidad. Solo 1,033 esqueletos están también en el conjunto de permeabilidad, por eso las dos fases casi no se tocan. La matriz de pares ya está construida —70,384 pares compuesto-diana sobre 59,532 compuestos, con 201 descriptores por compuesto— y la partición con la prueba reservada también ([2.7](#d2-7)). **El objetivo principal es la regresión de la potencia ([2.9](#d2-9)); la clasificación se deriva de ella.** Evidencia: [notebook 01b](../notebooks/01b_EDA_actividad_snc.ipynb) (los datos), [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb) (la matriz y la partición), [notebook 03](../notebooks/03_Baseline.ipynb) (el baseline) y [datos del proyecto](datos-contenido.md).

### Respuesta de la patrocinadora al correo del 24 de octubre {#respuesta-correo-24-oct}

El 24 de octubre se envió a la Dra. Martínez Ávila, con copia a Jorge Uribe, un correo con las dudas de la fase 2: el alcance de «no hacer inferencia», la dirección del efecto, la regresión frente al corte, el tejido y tres preguntas más. Esto contestó (correo, documento interno). Pidió a Jorge Uribe que diera su visto bueno.

| Tema | Lo que respondió |
|:--|:--|
| **Alcance de «no inferir»** | Su punto era la lectura (a): descartó que el equipo dedujera una etiqueta de actividad donde la fuente no la trae. No descartó las columnas `_used` que Jorge armó y documentó. |
| **Relaciones «inferida»** (2,001) | Pidió incluirlas, marcadas, y reportar en una línea una sensibilidad sin ellas. |
| **Fuente** | No entra como variable de entrada. Pidió estratificar la validación por fuente y reportar el desempeño por fuente. |
| **Dirección del efecto** | Eligió la opción 1: la afinidad cuenta y la etiqueta no se invierte. Pidió una variable objetivo agnóstica a la dirección y una columna `direccion_consistente` con los valores consistente, ambigua y contradictoria, derivada del tipo de actividad, el tipo de ensayo y el efecto buscado. El modelo principal usa todo; la sensibilidad, el subconjunto consistente. |
| **`Potency` y `AC50`** | Etiquetas genéricas de cribado: pidió tratarlas como potencia agnóstica a la dirección. |
| **IC50** | Un IC50 en ensayo de unión es afinidad. Solo un IC50 funcional sobre una diana de activación es contradictorio: se marca y se excluye de la sensibilidad, sin invertirlo. |
| **DRD2** | Fuera del alcance de la fase 2. Distinguir agonista de antagonista es una segunda tarea, con su propio conjunto de registros funcionales; pidió dejarla planteada como trabajo futuro. |
| **API de ChEMBL** | De acuerdo con consultarla. Indicó tipo de ensayo, formato BAO, puntaje de confianza, organismo y `action_type`. Pidió guardar las respuestas y anotar la fecha de descarga. Estos campos no entran como variables de entrada; sirven como filtro de sensibilidad y como descriptor del reporte. |
| **Potencia** | Pidió la potencia como variable principal y la clasificación derivada de aplicar el corte a las predicciones continuas al final. |
| **Censura** | Indicó que en escala `pActividad` «> 10 µM» es censura por la izquierda y que `survival:aft` de XGBoost está pensado para la derecha. Sugirió ajustar en µM, donde «> 10» es censura por la derecha, convertir a `pActividad` al final y verificar el signo antes de procesar todo el conjunto. |
| **Evaluación de la regresión** | Índice de concordancia de Harrell y Spearman; RMSE solo sobre las mediciones no censuradas, declarado como tal. Pidió buscar y citar la reproducibilidad experimental documentada (alrededor de 0.7 unidades logarítmicas para IC50 y 0.5 para Ki) y dejar ese techo escrito en el informe. |
| **Agregación por par** | Mediana de `pActividad`, con el número de mediciones y el rango, marcando los pares con dispersión mayor a cien veces. El filtro de dirección se aplica antes de agregar. |
| **Tejido** | No como variable de entrada. Pidió usarlo solo para auditar los pares en conflicto y como métrica de diagnóstico del sesgo. |
| **Partición del 10% apartado** | Pidió a Jorge Uribe compartir cómo se separó. Si fue aleatoria, pidió reportar en paralelo una partición por esqueleto molecular y deduplicar por esqueleto antes de partir. |

Tres puntos los dejó al criterio del equipo, con estas indicaciones:

- **Dianas fuera de la lista** (88,098 mediciones). Su posición es que no entren en la variable objetivo; el equipo decide si las aprovecha como tareas auxiliares o como descriptor de selectividad. Sobre los ensayos celulares, indicó que no son evidencia de neuroprotección por sí mismos (BV-2 es microglía, SH-SY5Y un modelo neuronal, U-251 un glioma) y pidió tratarlos como anotación de citotoxicidad, separada, para la etapa de priorización.
- **Inactivos de DrugMatrix** (29,730 filas). El equipo decide. Pidió considerar el argumento de que «Inhibition < 50% @ 10 uM» es un experimento real con protocolo uniforme. Si se incluyen, que sea como negativos censurados, con la columna de documento y agrupando por documento en la validación cruzada. En cualquier caso, pidió ver el desempeño con y sin ellos, y verificar con un análisis de esqueletos si los 772 compuestos, que describió como mayormente fármacos conocidos, sesgan el espacio químico.
- **Qué error pesa más.** El equipo lo resuelve como análisis de escenarios, dejándolos explícitos. Su expectativa es que el escenario realista sea el de pocos compuestos, con el falso positivo como el error caro. Pidió para ese escenario enriquecimiento al 1% y 5%, BEDROC, precisión en los primeros 100 y área bajo la curva de precisión-recall; y, para el cribado amplio, las métricas de sensibilidad, explicando cuál gobierna bajo cada supuesto. Pidió que la métrica principal quede declarada antes de ver resultados.

### Decisiones

#### 2.1 · El alcance: cinco categorías de enfermedad {#d2-1 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes preguntaba por cuatro dianas sueltas

**Qué se decidió.** Cinco categorías: Alzheimer, Parkinson, neuroinflamación, depresión y estrés oxidativo. Las demás salen (acta de la reunión, documento interno).

| Categoría | Registros | |
|:--|--:|:--|
| Alzheimer | 52,676 | queda |
| Parkinson | 32,372 | queda |
| Neuroinflamación | 12,331 | queda |
| Depresión | 10,888 | queda |
| **Estrés oxidativo** | **2,456** | **queda, por decisión de la patrocinadora** |
| Epilepsia · Neurodegeneración · Deterioro cognitivo · Ansiedad · Huntington · ELA | 3,826 en total | fuera |

Son 110,723 registros, el 96.7% de los 114,549 que tienen categoría de diana.

**Criterio.** Al menos 50 registros por categoría. No es una cota derivada: por debajo de unas decenas de pares un modelo propio no se sostiene (ELA tiene 53 registros, Huntington 153). Se escribe como regla para que datos nuevos no obliguen a decidir de nuevo. Estrés oxidativo, la más pequeña, se conserva por criterio de la patrocinadora: es el extremo general de la escala (casi toda enfermedad lo implica). Queda revisable si el análisis la muestra anómala.

**Dianas sin datos.** `GABRB2` y `GABRG2` (epilepsia) y `TARDBP` (ELA) salen con sus categorías. `AIF1` tiene 0 filas y su etiqueta dice «marcador de microglía activada; no es diana farmacológica». `SIRT1` tiene 1,110 mediciones pero su categoría, «Neurodegeneración (general)», no está entre las cinco: aporta 0 pares.

#### 2.2 · Por diana, con multitarea como comparación {#d2-2 .vigente .revisada}

**Estado:** vigente · revisada el 17 de octubre: antes era abierta, y la [2.1](#d2-1) la desbloqueó

**Qué se decidió.** Un modelo por diana donde hay datos suficientes (hoy once) y un multitarea sobre las 26, que además se queda con las dianas que no alcanzan. Orden por volumen: `BACE1`, `DRD2`, `ACHE`, `MAOB`, `MAOA`. **Por categoría no:** Alzheimer reúne a `BACE1` (una proteasa), `ACHE` (una esterasa) y `PPARG` (un receptor nuclear), tres farmacologías distintas, y un modelo sobre la mezcla aprende el promedio. La categoría se usa para reportar.

**Por qué.** El 85.0% de los compuestos se midió contra una sola diana; solo 8,934 (15.0%) tienen dos o más y aportan el 28.1% de los pares. Compartir información entre dianas llega a pocos compuestos, aunque el multitarea sigue compartiendo la representación química.

| Dianas | Pares que cubren |
|:--|--:|
| Las 14 con 1,000 pares o más, sobre los 70,384 pares | 94.3% |
| Las 13 con 1,000 o más, sobre los 54,369 de entrenamiento y validación | 93.5% |
| **Las 11 con clase minoritaria suficiente en todos los pliegues** | **85.6%** (46,534 de 54,369) |

**Cómo se eligieron las once, y qué cambia con la regresión.** El criterio era de clasificación: mil pares y cincuenta casos de la clase minoritaria en cada pliegue. Dejó fuera a `LRRK2` (96.8% de activos, 13 negativos en un pliegue) y a `GRIN2B` (96.9%, 5 negativos). Ese problema lo crea el corte: con 10 µM, `LRRK2` queda casi constante porque su potencia mediana es 7.40 y la de `NFE2L2` 5.02 (241 veces). **Con regresión la clase minoritaria deja de ser el criterio**; lo que importa es cuántas mediciones exactas tiene la diana y cuánto varía su pActividad. Eso no está medido: hasta medirlo se conserva la lista de once y se revisa si `LRRK2` y `GRIN2B` merecen modelo propio.

**Qué lo cambiaría.** Que la regresión por diana no supere al multitarea en alguna diana, y entonces esa se queda en el multitarea. `GRIN1` (88 pares) es el caso extremo: no se le entrena modelo, se reporta como subgrupo del multitarea. La curva de la [C.5](#dc-5) se entrega por diana.

#### 2.3 · De dónde sale la potencia y dónde se corta «activo» {#d2-3 .vigente .revisada}

**Estado:** vigente · revisada el 7, el 17 y el 24 de octubre

**Qué se decidió.**

1. **Las tres fuentes entran**, con las columnas `_used` de la sección 5 del diccionario (informadas y homogéneas para las tres). Ninguna etiqueta se traslada de una fuente a otra: cada fila se convierte con su propio valor.
2. **La potencia es `pActividad` = 6 − log₁₀(µM)**, recortada a [2, 12]. Reproduce el pChEMBL: sobre las 72,955 filas que traen los dos, la diferencia tiene mediana 0.0021 y máximo 0.005. Es la misma aritmética, no una inferencia.
3. **Las 2,001 relaciones «inferida»** entran marcadas (el diccionario les da 98.4% de acierto). Se reporta una sensibilidad sin ellas.
4. **Los inactivos declarados por texto** quedan fuera del principal ([2.12](#d2-12)); **la dirección del efecto** está en la [2.11](#d2-11); **el tejido** no entra (abajo).
5. **El corte de «activo» se aplica al final**, sobre la predicción continua ([2.9](#d2-9)): 10 µM principal y 1 µM sensibilidad, siempre juntos.

**Por qué las tres fuentes y no solo ChEMBL.** Dentro de ChEMBL hay 8,984 ensayos distintos, y el desacuerdo entre mediciones del mismo par es ligeramente peor ahí (28.0% de los pares con dos o más exactas discrepan más de 10 veces) que con las tres fuentes (25.5%; recalculado sobre `fase2_pares.parquet`). La heterogeneidad está entre ensayos, no entre fuentes. Y quedarse con ChEMBL cuesta los 15,293 registros de naturales: estrés oxidativo, por ejemplo, es 47.7% NPASS y CMAUP, y pasaría de 2,456 a 1,285 filas.

**Tejido y tipo de experimento: existen, pero no donde se modela.** 72,003 filas (35.5%) traen tejido, y casi todas (71,691) están en la ruta `neuronal_assay`, cuyas dianas son sobre todo de fuera de la lista ([2.4](#d2-4)). La ruta `cns_target`, por la que entran las dianas de la lista, tiene 0 de 108,640. Por eso solo 312 filas con tejido llegan a los pares: **286 pares de 70,384 (0.4%)**, y quince de las 26 dianas no tienen ninguno. Esos pares son 96.1% activos contra 72.7% de los demás, así que como entrada darían una pista sobre cómo se armó el archivo, no sobre la química. Decisión: el tejido **no entra al modelo**; sirve para auditar los pares en conflicto (donde la cobertura sube a 3.8%) y como diagnóstico. Tampoco permite aislar su efecto del de la diana: solo `APP` tiene dos formatos con diez o más mediciones exactas cada uno, y ahí la mediana difiere en 1.26 unidades. Lo calcula `scripts/cifras_contexto_ensayo.py`; corrida `experimentos/2026-10-24-ingrid-2.3-contexto-ensayo/`. Los campos que la API de ChEMBL da por ensayo (tejido, formato, organismo, confianza) cubrirían solo a ChEMBL; si entraran como variable, su ausencia delataría la fuente ([2.5](#d2-5)), así que se usan como filtro de sensibilidad y descriptor del reporte.

**Dónde se corta.** Con regresión el corte solo define la clase derivada. Lo que cuesta cada uno, por registro:

| «Activo» se corta en | Censurados que sirven como negativo | Activos | Razón de clases |
|:--|--:|--:|--:|
| **10 µM** (pChEMBL ≥ 5) | 48,480 (89%) | 61.7% | 1.6:1 |
| **1 µM** (pChEMBL ≥ 6) | 53,359 (98%) | 44.4% | 0.8:1 |

Un censurado `> L` solo sirve como negativo si su límite es igual o mayor que el corte (sección 7 del diccionario); por eso el «10 µM» aparece como dos cosas distintas, el corte y el límite de las filas censuradas. **De dónde sale el 10 µM:** el 67.4% de las 54,377 censuradas lo están exactamente en 10 µM, y el comentario de ChEMBL de las 29,730 filas con texto dice «Inhibition < 50% @ 10 uM». Es la concentración a la que estos ensayos dejaron de mirar. No hay un argumento farmacológico a favor ni en contra: una versión anterior lo justificaba como concentración libre alcanzable con una dosis oral, sin fuente, y se retiró; los datos que se encontraron sobre concentración libre cerebral apuntan a que es menor que 10 µM, pero no bastan para apoyar 1 µM. Lo medible favorece 1 µM (más negativos, clases balanceadas, 67,266 pares etiquetados contra 66,121); 10 µM es el principal por ser el corte del diccionario. Cambiar de uno a otro es leer otra columna ([2.10](#d2-10)).

**El mismo corte no exige lo mismo a cada diana.** Con 10 µM, `LRRK2` tiene 98.1% de activos y `NFE2L2` 50.7%. Mientras se clasifique, la tasa de activos se publica por diana junto con cualquier cifra agregada; la regresión elimina el problema ([2.9](#d2-9)).

El desarrollo por medición y por par está en [la propuesta de variable objetivo](variable-objetivo-fase2.md); las cifras se recalculan con `scripts/cifras_fase2.py` y `scripts/cifras_etiqueta_fase2.py`.

#### 2.4 · Los 88,098 registros sin diana de la lista {#d2-4 .propuesta}

**Estado:** propuesta

**Qué pasó.** El 43.5% de los registros (88,098) no corresponde a ninguna de las 39 dianas curadas; entraron por la ruta `neuronal_assay`. Por tipo de ensayo: 67,347 (76.4%) son de unión sobre proteínas, 15,746 (17.9%) funcionales, 789 de farmacocinética, 482 de toxicidad y 3,734 (las de NPASS) sin tipo (`scripts/cifras_fase2.py`). Entre las proteínas hay receptores que no son de la lista, como sigma-1, serotonina 1A y mu-opioide; ChEMBL no asigna diana a 30,511 filas (`Unchecked`) y marca 3,113 como `NON-PROTEIN TARGET`. Los ensayos sobre células son una minoría, y no todos miden protección: **BV-2 es microglía, SH-SY5Y un modelo neuronal y U-251 un glioma, y un ensayo de crecimiento (GI50, TGI: 859 filas) en U-251 mide sobre todo citotoxicidad.** Premiarlo como actividad favorable premiaría compuestos tóxicos.

**Se propone.**

1. No entran a la variable objetivo; se conservan aparte.
2. Los ensayos celulares se tratan como **anotación de citotoxicidad**, separada, para la priorización ([C.7](#dc-7)). Separar los que sí miden protección exige la descripción del ensayo, que el archivo no trae.
3. Los de unión sobre otras proteínas no entran como tarea auxiliar en la fase 2. Quedan como opción para después: sigma-1 y 5-HT1A comparten quimiotipos con `DRD2`, así que podrían servir de descriptor de selectividad.

#### 2.5 · La fuente confundida con el etiquetado {#d2-5 .vigente}

**Estado:** vigente · medida el 7 y el 18 de octubre

**Qué pasó.** NPASS y CMAUP no traen pChEMBL, así que etiquetar solo por él habría vuelto la fuente una variable perfectamente predictora de la vía de etiquetado. Con las columnas `_used` ([2.3](#d2-3)) ese vínculo ya no existe por registro, pero la fuente sigue llevando señal por la química: los esqueletos se reparten en 95,413 solo en ChEMBL, 1,445 solo en NPASS o CMAUP y 2,727 en ambas.

**Control del atajo** (#32; `scripts/experimento_atajo.py`; Random Forest, 54,369 pares de entrenamiento y validación, cinco pliegues agrupados, tres semillas; clasificación a 10 µM):

| Lo que el modelo ve | MCC | AUROC |
|:--|--:|--:|
| Solo la procedencia (sin mirar la molécula) | 0.280 | 0.579 |
| Solo química (201 descriptores) | 0.428 | 0.837 |
| Las dos | **0.451** | 0.843 |

La química supera a la procedencia por 0.148 de MCC, pero la procedencia sola llega al 65% del MCC de la química (más de lo que debería poder una columna de tres valores) y añadirla suma 0.023. La fuente lleva señal de la etiqueta.

**Y dentro de cada estrato**, donde ya no hay fuente que distinguir (AUROC, intervalo del 95% por bootstrap de grupos):

| Lo que el modelo ve | Estrato | Pares | Activos | AUROC |
|:--|:--|--:|--:|--:|
| Química | Solo ChEMBL | 50,671 | 74.8% | 0.831 [0.821, 0.841] |
| Química | Mixtos | 1,588 | 40.3% | 0.610 [0.570, 0.658] |
| Química | **Solo NPASS** | **2,109** | **12.3%** | **0.574 [0.534, 0.609]** |
| Química y diana | Solo NPASS | 2,109 | 12.3% | 0.613 [0.574, 0.648] |

El intervalo de 0.574 no toca 0.5: discrimina poco, y discrimina. Parte del déficit es de la diana y no del origen (dentro de `solo_npass` las tasas base van de 1.2% a 29.7%; dándole la diana sube a 0.613). **A igual diana, solo tres se pueden comparar** (veinte casos de cada clase en cada fuente): `NFE2L2` casi sin brecha (0.639 NPASS contra 0.672 ChEMBL), `MAPT` con brecha clara (0.540 contra 0.884, intervalos que no se tocan) y `PTGS2` indecidible (0.515 [0.397, 0.709] contra 0.705). Con esto no se puede afirmar que el modelo no sirva para naturales, ni lo contrario. Corrida `experimentos/2026-10-18-artemio-2.3-atajo-procedencia/`; tablas `notebooks/datos/resultados_atajo.csv` y `atajo_por_diana.csv`.

**Se decidió.**

- La fuente **nunca** entra como variable.
- La validación se estratifica por procedencia y todo desempeño se reporta por estrato. La fuente no es un atributo del par (827 de los 828 pares de CMAUP comparten par con otra fuente, y el 42.4% de los de NPASS), así que los estratos son **disjuntos**: solo ChEMBL 66,324 pares, mixtos 1,828, solo NPASS 2,231 y solo CMAUP 1.
- «Solo ChEMBL» queda como análisis de sensibilidad.
- La cifra que contesta la pregunta del proyecto es la de `solo_npass` **por diana**, con su intervalo.

**Pendiente.** Repetir el control con la regresión (Spearman o índice de concordancia en lugar de MCC y AUROC). **Qué lo cambiaría:** que el patrón de `MAPT` se repita en la mayoría de las dianas comparables; entonces no cambia el etiquetado, se reporta que el modelo no sirve para productos naturales, que es un resultado válido.

#### 2.6 · La partición de prueba que sí se había reservado {#d2-6 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes era una pregunta abierta

**Qué se decidió.** La partición reservada sí existía, se hizo al azar, y la patrocinadora entrega el archivo completo para que el equipo la rehaga con criterio. Su condición, repetida cuatro veces: que se reserve una prueba que el modelo nunca vea ([2.7](#d2-7)).

**Qué pasó.** El archivo se llama `..._Entrenamiento.csv`: el diccionario describe 225,513 filas y el recibido tiene 202,647 (89.9%). Un 10% extraído al azar comparte andamios, ensayos y artículos con el 90%: prueba filas nuevas, no química nueva. Ejemplo: si hay cincuenta análogos de la morfina y el 10% se llevó cinco, el modelo memoriza el andamiaje y la evaluación sale inflada. Si el reporte final la llama «validación externa», sobrevende lo que compra. En la fase 1 la prueba reservada resultó la parte difícil (57.3% BBB+ contra 72.0% en validación), así que sus cifras se reportan sobre validación y no son comparables con las anteriores.

**Pendiente.** Jorge Uribe debe compartir el método con que se separó ese 10%. Si fue aleatorio, se reporta en paralelo una partición por esqueleto molecular, deduplicando por esqueleto antes de partir.

#### 2.7 · Partición de la fase 2 {#d2-7 .vigente .revisada}

**Estado:** vigente · construida el 18 de octubre de 2026 · revisada: antes proponía además disjuntar por fuente

**Qué se decidió.** El criterio de la fase 1 (andamio de Bemis-Murcko agrupado con el esqueleto de conectividad, con verificación de fuga), con 70% entrenamiento, 10% validación y 20% **prueba reservada** ([2.6](#d2-6)). La calcula `particion_de_pares` en `src/data_prep/pares_fase2.py` y viaja en `fase2_pares.parquet`, no en una celda del notebook. Cero andamios y cero esqueletos cruzan. La validación cruzada de cinco pliegues corre sobre los 54,369 pares de entrenamiento y validación y no toca la prueba.

| Partición | Pares | Grupos | Activos a 10 µM |
|:--|--:|--:|--:|
| Entrenamiento | 49,425 | 6,640 | 71.6% |
| Validación | 6,986 | 3,617 | 69.6% |
| **Prueba** | **13,973** | 13,973 | 78.7% |

**Lo que cuesta** (sección 6.1 del [notebook 02b](../notebooks/02b_Feature_Eng_actividad.ipynb)):

- La prueba son 13,973 pares en 13,973 grupos: los andamios frecuentes alimentan el modelo y los raros evalúan química nueva. Mide generalización, no representatividad.
- Tiene 7 puntos más de activos que el entrenamiento: es otra población, no una prueba más difícil. Cada métrica se reporta con la tasa base de su partición al lado; en regresión, con la distribución de pActividad (por calcular).
- Los naturales se concentran en entrenamiento: solo 117 de los 2,231 pares de solo NPASS (5.2%) caen en la prueba, y 346 de 4,059 con los mixtos (8.5%). Alcanza para una señal gruesa, no para comparar con intervalos.

**Lo que se descartó.** Disjuntar por fuente: la fuente no es un atributo del par ([2.5](#d2-5)); lo que hace ese trabajo es el control del atajo más el reporte por estrato. Disjuntar por artículo: un solo componente conectado reúne 39,362 pares (55.9%); se reporta el desempeño por referencia dentro de la validación cruzada.

**Cómo se protege la prueba.** `cargar` (`src/models/tareas.py`) la deja fuera por omisión y exige `incluir_prueba=True`, pero es una convención: pedirla no falla ni deja registro. La guarda está abierta en el [#54](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/54) y conviene tenerla antes de afinar modelos.

**Qué lo cambiaría.** Que haga falta evaluar los naturales sobre la prueba con intervalos: la partición se estratifica por origen (reconstruir el artefacto, no rehacer el modelado).

#### 2.8 · El cruce con COCONUT lo calcula el equipo {#d2-8 .vigente .revisada}

**Estado:** vigente · decidida por el equipo el 17 de octubre de 2026 · revisada: antes se le pedía a ella

**Qué se decidió.** El equipo calcula el cruce con COCONUT desde `smiles_raw`. Hasta que esté, la **fuente** es la definición provisional de «natural» y se declara así en todo lo que se reporte. Un solo modelo, con el desempeño por origen.

**Por qué.** El archivo de actividad no trae marca de «natural» (el de permeabilidad sí, cruzado contra COCONUT). La fuente es una definición imperfecta: el 65.4% de los esqueletos naturales (2,727 de 4,172) también está en ChEMBL, y solo 1,445 existen únicamente en NPASS y CMAUP. Un cruce propio no será idéntico al de la patrocinadora, pero la discrepancia es medible (cuántos compuestos cambian de clase) y esperar dejaría sin contestar la pregunta central del proyecto. `inchikey_source` viene vacío en los 187,354 registros de ChEMBL, así que el solapamiento se calcula desde `smiles_raw`.

**Qué lo cambiaría.** Que la patrocinadora aporte su cruce: pasa a ser la definición y el nuestro queda como comprobación. No obliga a rehacer nada, porque el origen es una columna de metadatos, no una característica.

#### 2.9 · Regresión de la potencia; la clasificación se deriva de ella {#d2-9 .vigente}

**Estado:** vigente · el 24 de octubre la patrocinadora pidió la potencia como variable principal

**Qué se decidió.** Un solo modelo que predice **`pActividad`**, con los censurados como cotas y no como datos faltantes. La clase (activo o inactivo a 10 µM o 1 µM) sale de aplicar el corte a la predicción continua, al final: se entrena una vez y el corte deja de ser una decisión de modelado.

**Ejemplo de por qué.** Con el corte en 10 µM, un compuesto de 0.05 µM y otro de 9 µM reciben la misma etiqueta «activo», y el ranking los empata. Con 10 µM, `LRRK2` queda en 98.1% de activos y la etiqueta no informa. La regresión conserva el orden dentro de cada clase, que es lo que se entrega ([C.5](#dc-5)).

**Por qué censurada y no solo exactas.** El 98.0% de los pares activos tiene una medición exacta, pero solo el 50.6% de los negativos: la mitad de la evidencia de inactividad existe solo como censurada. Entrenar solo con exactas pierde 8,938 negativos y da un ranking optimista.

| Forma | Pares | Negativos | Qué pierde |
|:--|--:|--:|:--|
| Clasificación a 10 µM | 66,121 | 18,107 · 27.4% | el orden dentro de cada clase |
| Regresión sobre exactas | 56,229 | 9,169 · 16.3% | **8,938 negativos**, el 49.4% de la clase |
| **Regresión censurada** | **66,121** | — | nada de la población |

**Cómo se trata la censura.** Un `> 10 µM` es censura **por la derecha** si se mide en µM (la concentración real es mayor que 10) y **por la izquierda** en `pActividad` (menor que 5). El objetivo `survival:aft` de XGBoost está pensado para la derecha, así que se ajusta en µM, con cota inferior 10 y superior infinita, y se convierte a `pActividad` al final. El diccionario pide lo mismo: los censurados «se excluyen o se usa un método para valores censurados». La prueba sintética hecha antes (Spearman 0.946) no es evidencia sobre datos reales: **el signo se verifica con una muestra antes de procesar todo el conjunto.**

**Cómo se evalúa.**

- **Índice de concordancia de Harrell y Spearman**, que toleran la censura. **RMSE solo sobre las mediciones no censuradas**, declarado como tal.
- **Techo de reproducibilidad.** La patrocinadora indicó que la reproducibilidad experimental del IC50 en ChEMBL ronda 0.7 unidades logarítmicas (0.5 en Ki); **la fuente falta citarla.** Como el 25–28% de los pares discrepa más de diez veces (una unidad logarítmica), un RMSE muy por debajo de ese orden no sería un buen resultado sino una señal de fuga de datos. El techo se escribe en el informe desde ahora.
- Las métricas de clasificación (MCC, AUPRC, [C.1](#dc-1)) se calculan sobre la clase derivada. Las de ranking están en la [C.5](#dc-5).

**El baseline de clasificación se conserva como piso.** Tres canalizaciones sin afinar, sobre los 54,369 pares de entrenamiento y validación (10,071 grupos, 71.4% de activos), con la diana como característica y la validación cruzada agrupada (`scripts/experimento_baseline.py --tarea actividad`; corrida `experimentos/2026-10-18-artemio-2.3-baseline-actividad-descriptores-diana-10um/`):

| Canalización | AUROC | IC 95% | MCC |
|:--|--:|:--|--:|
| Bosque aleatorio | 0.866 | [0.859, 0.874] | 0.495 |
| Boosting por histogramas | 0.857 | [0.848, 0.865] | 0.486 |
| Regresión logística | 0.796 | [0.786, 0.806] | 0.387 |

La logística queda 6–7 puntos abajo, con intervalos que no se tocan; entre el bosque y el boosting no se distingue. **El agregado no describe a los naturales:** el AUROC del bosque es 0.858 sobre los pares solo ChEMBL, 0.637 sobre los mixtos y **0.611 [0.572, 0.647]** sobre los de solo NPASS ([2.5](#d2-5)). La regresión tiene que superar este piso en la clase derivada.

**Qué cuesta.** La pérdida censurada es más maquinaria y su calibración importa. SHAP corre sobre `survival:aft`, pero atribuye sobre log-potencia, más difícil de narrar a un biólogo que «esta subestructura empujó hacia activo». La [C.2](#dc-2) sigue siendo viable, pero el relato cambia.

**Por qué conviene.** El ranking final combina las dos fases ([C.3](#dc-3)). Si la componente de actividad es un número y no una clase, se puede comparar la potencia predicha contra la exposición alcanzable: un compuesto BBB− llega a menos concentración en el cerebro y necesita más potencia para servir.

#### 2.10 · El objetivo se guarda como intervalo, no como etiqueta {#d2-10 .vigente}

**Estado:** vigente · decisión del equipo

**Qué se decidió.** La matriz (`src/data_prep/pares_fase2.py`, construida con `scripts/construir_pares_fase2.py`) tiene 70,384 pares sobre 59,532 compuestos y 26 dianas. De cada par se guarda **el intervalo donde cae la potencia**, no una etiqueta; la binaria se deriva de él.

| Columna | Qué es |
|:--|:--|
| `pActividad` | la potencia como número, 6 − log₁₀ µM; `NaN` si el par solo tiene cotas |
| `limite_inferior`, `limite_superior` | el intervalo, con ±∞ donde no hay cota |
| `n_mediciones`, `n_exactas`, `rango_exactas` | cuántas mediciones y cuánto se separan |
| `activo_10um`, `activo_1um` | la etiqueta binaria, **derivada** del intervalo |

**Por qué.** Cambiar el corte o pasar a regresión ([2.9](#d2-9)) no reconstruye nada: la clasificación, la regresión sobre exactas y la censurada leen el mismo archivo. Guardar solo `activo_10um` tendría el defecto que tuvo la fase 1, donde la selección de columnas se congeló sobre una matriz ya transformada ([1.5](#d1-5)). El intervalo también reproduce la regla del diccionario sin programarla aparte: un `> 1 µM` da cota superior 6, que no alcanza para declarar inactivo con T = 10 µM y sí con T = 1 µM.

**La llave del par es esqueleto de conectividad × `target_gene`**, no el identificador del compuesto. `source_compound_id` usa prefijos distintos por fuente (`CHEMBL…` contra `NPC…`) y no comparte ni un valor: con esa llave, un compuesto medido en dos fuentes entraría como dos pares y sus contradicciones, 164 entre ChEMBL y las fuentes naturales, quedarían invisibles. Es la misma llave que usa `grupos_cv` para la partición.

**Cómo se agrega un par.**

1. **Mediana de las exactas, no el valor más potente.** El máximo sesga hacia la clase positiva. La dispersión queda en `rango_exactas`.
2. **Conflicto es evidencia incompatible, no dispersión.** Un par se marca en conflicto cuando su mediana cae fuera de lo que permiten sus cotas, o cuando las cotas se cruzan: bajan de 1,784 a **1,126**, y solo 15 dan un intervalo vacío.
3. **El empate en el umbral se resuelve a favor de activo.** Una exacta justo en 10 µM es activa («igual o menor») y un censurado `> 10 µM` es inactivo; tienen la misma relación numérica con el corte y significan lo contrario. Mueve 409 pares.
4. **El filtro de dirección ([2.11](#d2-11)) se aplica antes de agregar**, en ambas variantes.
5. **Falta:** una bandera para los pares con dispersión mayor a cien veces (`rango_exactas` mayor que 2).

**Recortes.** La potencia se recorta a [2, 12], que es el rango del pChEMBL observado (2.35 a 12.00); ChEMBL no asignó pChEMBL a ninguna de las 319 filas fuera. Las filas en unidades de masa quedan fuera porque sin peso molecular no hay conversión a molar: son 181, y por eso el conteo es 70,384 y no 70,497.

**Cifras.** 57,832 pares con potencia y 12,552 solo con cotas; 67,736 con etiqueta a 10 µM (72.8% activos, 2,648 sin decidir) y 69,632 a 1 µM (50.2%, 752 sin decidir); 24,230 grupos para la partición; 201 de 217 descriptores utilizables.

#### 2.11 · Dirección del efecto: la afinidad cuenta {#d2-11 .vigente}

**Estado:** vigente · el 24 de octubre la patrocinadora eligió esta opción

**Qué se decidió.** La afinidad (`Ki`, `Kd`, IC50 de unión) cuenta como evidencia de actividad y ninguna medición se invierte. La variable objetivo es agnóstica a la dirección. Se agrega una columna **`direccion_consistente`** ∈ {consistente, ambigua, contradictoria}, derivada del tipo de actividad, el tipo de ensayo y `diana_efecto_buscado`. El modelo principal usa todo; la sensibilidad, solo el subconjunto consistente. `Potency` y `AC50` son etiquetas genéricas de cribado y se tratan como potencia agnóstica. `DRD2` no se resuelve con Ki: distinguir agonista de antagonista es una segunda tarea, con registros funcionales, fuera de la fase 2.

**El problema, con un ejemplo.** `PPARG` es una diana donde se busca **activar**. Un IC50 sobre ella puede venir de un ensayo de **unión**: `CHEMBL2342574` mide el desplazamiento de [3H]-rosiglitazona, un agonista, y mide cuánto se une, no si activa (afinidad). Otro IC50 viene de un ensayo funcional, como `CHEMBL1116169` («Inhibition of PPARgamma assessed as transcriptional activity»): ahí sí mide inhibición, lo contrario de lo buscado. El nombre «IC50» no distingue las dos cosas; el ensayo sí. Por eso solo un **IC50 funcional sobre una diana de activación es contradictorio**: se marca y sale de la sensibilidad, sin invertirlo.

**Cómo se lee el ensayo.** El archivo trae `assay_type` solo en la ruta `neuronal_assay`, y está vacío en las 2,015 mediciones IC50 de las tres dianas de activación que aportan pares (`PPARG`, `NFE2L2`, `TSPO`). Se piden a ChEMBL por `assay_chembl_id` el tipo y la descripción (`scripts/descargar_tipos_ensayo.py`; `notebooks/datos/tipos_ensayo_chembl.csv`; 9,894 ensayos). El tipo `B` (unión) es grueso: hay ensayos `B` cuya descripción es funcional, así que además se lee la descripción con una regla de palabras (inhibir o antagonizar sin hablar de unión → inhibición funcional), estrecha y sin validar fila por fila. Resultado: **1,429 mediciones (71%) afinidad, 399 (20%) inhibición funcional, 187 (9%) sin tipo** (NPASS y CMAUP no traen identificador de ensayo, o el ensayo es de farmacocinética o toxicidad). Una lectura manual de las descripciones dio 17% de funcionales entre los IC50 de ChEMBL. Consultar la API no es inferir, es recuperar un dato registrado; el tipo, el formato BAO, la confianza, el organismo y `action_type` se piden con la fecha de descarga anotada.

**Cuánto está en juego** (`scripts/medicion_dianas_activacion.py`; corrida `experimentos/2026-10-24-ingrid-2.3-dianas-activacion-descripcion/`). De los 6,140 pares de las dianas de activación:

| Pares | Cuántos |
|:--|--:|
| Con una medición de activación | 4,093 |
| Solo afinidad | 1,011 |
| Solo de tipo ambiguo | 822 |
| Solo inhibición funcional | 155 |
| Mezclas | 59 |

Exigir que la medición sea de activación cambia 67 etiquetas y deja **2,047 pares sin ninguna medición**; quitar solo la inhibición funcional cambia 2 y deja 155. Es un problema de cobertura, no de etiquetado, y por eso la afinidad cuenta. Ejemplo: `TSPO` es un marcador de PET que se caracteriza por desplazamiento de radioligando, no por EC50; con el criterio estricto pasaría de 260 pares a 5.

**Los pares que dependen de `AC50`.** Existe solo en NPASS: 1,374 mediciones, 1,246 censuradas. 1,208 pares dependen solo de `AC50` (todos de solo NPASS, 1,161 inactivos): son el 61% de los 1,914 negativos de ese estrato. Quitarlo dejaría a los naturales casi sin clase negativa. Se conserva y se reporta con y sin esos pares.

**`DRD2`** tiene 9,618 pares y `diana_efecto_buscado` «agonismo o antagonismo (según enfermedad)»: agonistas en Parkinson, antagonistas en esquizofrenia. En 14,732 mediciones, 11,230 son Ki (conteo manual, sin script). Queda como trabajo futuro.

**Pendiente.** Definir `direccion_consistente` para las 26 dianas (la tabla de tipos hoy solo cubre las tres de activación; por ejemplo, un EC50 sobre `GSK3B`, de inhibición). Medir cuánto cubre la API de los campos pedidos en nuestros compuestos.

#### 2.12 · Los inactivos de DrugMatrix {#d2-12 .propuesta}

**Estado:** propuesta

**Qué pasó.** 29,730 filas traen texto de inactividad («Not active»; ChEMBL: «Inhibition < 50% @ 10 uM and thus dose-response curve not measured»). Son una sola campaña de tamizaje (`CHEMBL1909046`, el panel DrugMatrix), 772 compuestos, todas `> 10 µM`. Se excluyen del principal. De ellas, 5,658 filas caen en dianas de la lista y sumarían **2,169 pares** (70,384 → 72,553) en solo cuatro dianas (`MAOA`, `PTGS2`, `ACHE`, `DRD2`), sobre 729 esqueletos.

**Con regresión aportan poco.** Las 5,658 filas dicen lo mismo: `pActividad` < 5, sin cuánto menos. Como clasificación pesaban mucho (61% de los negativos por registro, 10.8% por par); como cota de regresión son una sola cota repetida, concentrada en una campaña, cuatro dianas y fármacos conocidos (espacio químico sesgado).

**Se propone.** Fuera del modelo principal. Una sensibilidad con ellas como negativos censurados y sin ellas, reportada al lado, con un análisis de esqueletos de los 772 compuestos. Como todas son de un solo documento, agrupar por documento en la validación cruzada las deja juntas en un pliegue, y eso hay que declararlo. El valor que podrían tener es el déficit de negativos verdaderos de cualquier conjunto derivado de la literatura, donde se publica lo que funciona.

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| S2.1 | «Activo» sobre una proteína es señal de neuroprotección | Sin comprobar | Es una inferencia, casi siempre medida fuera de un organismo; no implica que llegue al cerebro ni que sea selectivo | El modelo solo afirma actividad sobre dianas |
| S2.2 | Una potencia describe un compuesto bajo un ensayo, no una propiedad del compuesto | Asumido | El mismo compuesto cambia de clase según la concentración y el ensayo; 25.5% de los pares discrepan más de diez veces | Se declara el ensayo y el corte en cada reporte |
| S2.3 | El pChEMBL basta para etiquetar | Desmentido | Solo existe para ChEMBL ([2.3](#d2-3)) | Columnas `_used` y potencia en `pActividad` |
| S2.4 | Un censurado «> 10 µM» sirve como negativo | Acotado | Solo si el límite es ≥ al corte; 29,730 están en un documento ([2.12](#d2-12)) | Reportar con y sin ellos |
| S2.5 | «Activo» tiene una dirección clara | Desmentido en parte | `diana_efecto_buscado` existe y el tipo de medida no basta para cruzarlo: un IC50 mide inhibición solo si el ensayo es funcional ([2.11](#d2-11)). Declara el efecto buscado como tratamiento, no lo que hizo el compuesto | `direccion_consistente` y sensibilidad sobre el subconjunto consistente |
| S2.6 | Hay datos para las 39 dianas | Desmentido | Cuatro sin datos; Alzheimer 52,676 y ELA 53 ([2.1](#d2-1)) | Excluir; multitarea |
| S2.7 | Un mismo esqueleto y gen tienen mediciones consistentes | Desmentido en parte | 1,126 pares en conflicto ([2.10](#d2-10)) | Regla de resolución reproducible y sensibilidad |
| S2.8 | El archivo recibido es el conjunto completo | Acotado | 89.9% de lo descrito en el diccionario ([2.6](#d2-6)) | Pedir la partición reservada |
| S2.9 | La fuente no explica la etiqueta | Acotado | La procedencia sola llega al 65% del MCC de la química ([2.5](#d2-5)) | Estratificar y reportar por procedencia |
| S2.10 | La matriz de características sirve para la fase 2 | Acotado | 70,384 pares, 201 descriptores más 26 indicadores de diana; AUROC 0.866 en el baseline, pero 0.611 sobre solo NPASS ([2.9](#d2-9)) | Reportar por procedencia; si sigue cerca del azar, decir que no sirve para naturales |
| S2.11 | La fuente identifica a los productos naturales | Sin comprobar | El 65.4% de los naturales también está en ChEMBL ([2.8](#d2-8)) | Cruce con COCONUT |
| S2.12 | La regresión censurada con XGBoost funciona sobre estos datos | Sin comprobar | Solo hay una prueba sintética; el signo de la censura no se ha verificado en datos reales ([2.9](#d2-9)) | Regresión sobre exactas más un clasificador de censura, o clasificación como piso |
