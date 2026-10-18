# La ruta del proyecto

Bitácora de lo que se decide en cada fase y de las posibilidades que siguen abiertas. Se alimenta **por fase, no por avance**: la fase 1 es la permeabilidad de la barrera hematoencefálica (BBB+/BBB−) y la fase 2, la actividad neuroprotectora por diana. Ambas parten de los archivos que entregó la patrocinadora el 25 de septiembre. Cada fase tiene sus **decisiones** (lo que se resolvió o se propone), sus **supuestos** (lo que se dio por cierto para avanzar y puede ser falso) y, en cada entrada, la pregunta que queda por resolver.

Nada es *ratificado* hasta que la patrocinadora lo revise; lo que el equipo adopta sigue siendo reversible, y dos decisiones ya se revirtieron al medir. Cuando algo cambia se deja la versión anterior visible. Los términos están en el [glosario](glosario.md).

**Cómo se cierra una entrada.** Pasa a *ratificada* con la minuta de la reunión con la patrocinadora: de ahí se toman las respuestas y se registran aquí, en sus términos y con la fecha. Mientras no haya minuta, lo que el equipo adopta se queda en *propuesta*, lo que obliga a declararlo como no ratificado en el reporte donde se use. **Las entradas marcadas «necesita su definición» son las que más urge que ella defina**, porque sin su criterio el equipo solo puede avanzar con un supuesto propio. Esas siete están reunidas, con su contexto y una casilla para responder, en la [consulta a la patrocinadora](../consulta.qmd); contestar ahí no cierra nada —sigue siendo la minuta la que ratifica— pero deja la reunión para lo que haga falta discutir.

## Estado de un vistazo

**Marco común** (aplica a las dos fases)

| # | Decisión | Estado |
|:--|:--|:--|
| [C.1](#dc-1) | MCC y AUPRC sobre la clase minoritaria | Vigente |
| [C.2](#dc-2) | Dos métodos de atribución independientes | Vigente |
| [C.3](#dc-3) | Comprobar si combinar las dos predicciones mejora la selección | Propuesta |
| [C.4](#dc-4) | PAINS: aplicarlos a los resultados finales | Propuesta |
| [C.5](#dc-5) | Qué se entrega al final y qué error cuesta más | Abierta · **necesita su definición** |
| [C.6](#dc-6) | Licencia y uso académico de los resultados | Propuesta |

**Fase 1 · Permeabilidad**

| # | Decisión | Estado |
|:--|:--|:--|
| [1.1](#d1-1) | No filtrar por la columna de grupo A–D | Vigente · revisada |
| [1.2](#d1-2) | Partición por andamio, nunca aleatoria | Vigente |
| [1.3](#d1-3) | Descriptores RDKit más Morgan/ECFP4 | Vigente |
| [1.4](#d1-4) | Las 6 filas con logBB sin clase | Propuesta |
| [1.5](#d1-5) | Tres modelos candidatos; de ahí, si escalar y si reducir dimensión | Propuesta |
| [1.6](#d1-6) | Naturales en la fase 1: evaluar por origen, no entrenar por separado | Propuesta · **necesita su definición** |
| [1.7](#d1-7) | Tamaño L de Sort & Slice: 2048 de trabajo; 512 es posible con XGBoost o Random Forest | Propuesta |
| [1.8](#d1-8) | Los 131 esqueletos con etiquetas contradictorias | Abierta |

**Fase 2 · Actividad**

| # | Decisión | Estado |
|:--|:--|:--|
| [2.1](#d2-1) | El alcance: cinco categorías de enfermedad | **Ratificada** · revisada |
| [2.2](#d2-2) | Forma del modelo: por diana, por categoría o multitarea | Abierta · **necesita su definición** |
| [2.3](#d2-3) | Etiquetado por tres vías y criterio de «activo» | Propuesta · **necesita su definición** |
| [2.4](#d2-4) | Los 88,098 registros fenotípicos | Propuesta |
| [2.5](#d2-5) | La fuente confundida con el etiquetado | Vigente · medida |
| [2.6](#d2-6) | La partición de prueba que sí se había reservado | **Ratificada** · revisada |
| [2.7](#d2-7) | Partición de la fase 2 | Propuesta |
| [2.8](#d2-8) | Origen natural en la fase 2: cómo se define y si se entrena aparte | Abierta · **necesita su definición** |

Estados: **vigente** (se trabaja sobre ella), **revisada** (se decidió, se midió y cambió), **propuesta** (hay recomendación del equipo, aún sin adoptar), **abierta** (sin recomendación) y **ratificada** (la patrocinadora la revisó y la decidió; las primeras son la 2.1 y la 2.6, del 15 de octubre de 2026). La marca **«necesita su definición»** no es un estado: señala las entradas donde el criterio de la patrocinadora es lo que falta, y son las que más urge resolver con ella.

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

**Se propone.** PAINS no entra al entrenamiento ni a la prueba, para no sesgar contra los naturales. Se aplica a la salida: cada candidato del ranking lleva su alerta y el ranking se reporta con y sin esos compuestos. Una molécula que agrega no falsea un logBB, así que en la fase 1 la alerta es información; en la fase 2 sí condiciona cómo leer el ranking.

**Versión anterior, descartada como primaria.** Tres brazos: sin filtrar, filtrado solo en entrenamiento y evaluación estratificada. Puede retomarse si el ranking resulta dominado por alertas; su regla sigue valiendo: nunca filtrar la prueba y declarar el protocolo antes de correrlo.

#### C.5 · Qué se entrega al final y qué error cuesta más {#dc-5 .abierta .definir}

**Estado:** abierta · necesita su definición

> **Pregunta:** Si el laboratorio puede ensayar unos veinte compuestos este semestre, ¿prefiere una lista corta de veinte donde acierte cuatro de cada cinco, o una de cien donde acierte una de cada dos? ¿Y qué espera recibir: una lista de candidatos, un modelo que pueda correr ella misma, o el material de un artículo?
>
> *Secundarias:* ¿el ranking se presenta como lista ordenada, con un corte, o agrupado por diana? ¿Cómo se presenta un compuesto con BBB− predicho y actividad documentada?

**Qué pasó.** El umbral de decisión depende de qué error es más caro, y eso no lo decide la estadística. Un falso activo manda al laboratorio a ensayar algo que no funciona (tiempo y reactivos); un falso inactivo descarta un candidato real y nadie se entera. Las métricas están fijadas ([C.1](#dc-1)); el punto de operación no.

**Por qué está preguntada así.** La versión anterior preguntaba «¿qué error pesa más?», que es la pregunta correcta y es casi imposible de contestar en frío. Planteada como una elección entre dos listas concretas se responde de inmediato y da lo mismo: la proporción entre precisión y exhaustividad que el laboratorio tolera, que es el punto de operación. La segunda mitad —qué espera recibir— es la que más arrastra: de ella dependen la forma del entregable, buena parte de la [C.6](#dc-6) y qué tan agregado conviene que sea el modelo de la [2.2](#d2-2). Es también la única pregunta de esta página que el equipo no puede contestar ni aproximar con una medición.

#### C.6 · Licencia y uso académico de los resultados {#dc-6 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Se autoriza publicar los resultados, y qué datos derivados, bajo uso académico no comercial? ¿Hay aspiraciones comerciales? NPASS (CC BY-NC) lo impediría.

**Esta entrada va aparte de las demás.** No es un criterio técnico sino administrativo, y la mitad de lo que falta no depende de ella sino del departamento y del Tec: propiedad intelectual, orden de autoría, foro. Tratarla en la misma sesión que el criterio de «activo» hace que ninguna de las dos se cierre. Se plantea por escrito y con tiempo, no en la reunión donde se resuelven las entradas marcadas «necesita su definición».

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
- **Sin escalar, la regresión logística no converge**, y eso es lo que justifica escalar. Agota las 3,000 iteraciones de `lbfgs` en los 15 pliegues y avisa de no haber convergido en los 15; con cualquiera de las tres transformaciones converge sin aviso, en 53 iteraciones con min–max y 137 a 144 con las otras dos. Su MCC de 0.687 no es el desempeño de «no escalar»: es donde se detuvo el optimizador al agotar su presupuesto, así que esa fila no es comparable con el resto. El tiempo (0.437 s contra 0.007 s) es la consecuencia visible; las iteraciones y el aviso son la prueba. El Random Forest tarda lo mismo con las cuatro, lo que descarta que los datos sean más difíciles sin escalar.
- **El escalado no arregla el condicionamiento**, y conviene no atribuírselo: el número de condición de la matriz va de 5.9e+17 a 1.2e+21 con las cuatro transformaciones. Viene de las columnas casi colineales —120 pares con |r| > 0.95— y lo trata la selección, no el escalado.
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

Solo la logística necesita escalar, así que cada modelo lleva su canalización y los árboles reciben la matriz sin transformar. Para la logística **se propone escalar**, porque sin escalar no converge, y **min–max como opción de partida**, no como conclusión: entre las tres formas de escalar la medición no da base para elegir, y la alternativa de no escalar deja un modelo que agotó sus iteraciones. Yeo-Johnson es la única con un motivo medido para evitarla, y aun así por una diferencia que no alcanza significancia. **Cuál de las tres se adopta lo cierra el equipo**, no la patrocinadora: la medición no las distingue en desempeño y la razón para escalar resultó ser la convergencia, así que no queda un criterio que dependa de su conocimiento del dominio. Lo que sí depende de ella es la pregunta de arriba, entre explicabilidad y reducción de dimensión, porque eso se decide por lo que quiere poder leer en el resultado y no por una cifra. Se resuelve en el Avance 3, con los modelos afinados y suficientes evaluaciones para cerrar los intervalos, y arrastra rehacer la selección de la §9. El Avance 2 guarda la matriz filtrada en dos versiones, transformada con Yeo-Johnson y sin transformar, con las mismas columnas. El PCA no se adopta, por explicabilidad, y se guarda ajustado como brazo de comparación. Lo que ejecutó el Avance 2 es una propuesta: la alternativa (no escalar, no reducir dimensión) sigue en pie hasta que se acuerde. SHAP con `TreeExplainer` sirve a los árboles y Chemprop queda como comparación opcional del Avance 4.

#### 1.6 · Naturales en la fase 1: evaluar por origen, no entrenar por separado {#d1-6 .propuesta .definir}

**Estado:** propuesta · necesita su definición

> **Pregunta:** Los naturales cruzan la barrera igual que el resto en el grupo A de B3DB, que es el que tiene logBB medido, y 21 y 17 puntos menos en B y C, que vienen de una clasificación publicada. ¿Conoce alguna razón de curación que lo explique, o hay que leerlo como química? De ahí cuelga el resto: si es curación, un solo modelo con el desempeño reportado por origen basta; si es química, habría que considerar entrenar aparte.
>
> *Secundarias, si queda tiempo:* ¿Los 1,005 compuestos con análogo natural que difiere solo en estereoquímica cuentan como naturales? ¿Qué rango de TPSA es razonable para naturales neuroactivos?

**Qué pasó.** El archivo de la patrocinadora marca como natural lo que coincide exactamente con COCONUT (columna `coconut_id_exact_match`): 3,366 compuestos, el 43.1% de los 7,805 con clase. Lo demás no es «sintético»: el diccionario distingue 3,366 naturales exactos, 1,005 análogos que difieren solo en estereoquímica y 3,440 sin equivalente natural conocido. Los naturales cruzan unos 19 puntos menos (52.7% contra 71.7% BBB+, notebook 01 del Avance 1).

**La brecha no es uniforme.** Repartida por el grupo de confiabilidad de B3DB, casi no existe donde hay un logBB medido y aparece donde la etiqueta viene de una clasificación publicada:

| Grupo de B3DB | No natural (BBB+) | Natural (BBB+) | Diferencia (puntos), IC 95% |
|:--|--:|--:|:--|
| A (con logBB medido) | 87.6% (n = 644) | 88.4% (n = 414) | −0.8 [−4.8, +3.2] |
| B | 77.2% (n = 2,166) | 55.9% (n = 1,455) | +21.4 [+18.3, +24.5] |
| C | 58.1% (n = 1,624) | 40.9% (n = 1,451) | +17.2 [+13.7, +20.7] |

En el grupo A la brecha no es solo «casi inexistente»: queda **acotada a unos ±5 puntos**, lo que excluye cualquier cosa parecida a los 19 globales; en B y C es grande y en la dirección contraria. El grupo D (n = 5 y 46) no permite concluir. Esto es descriptivo y no prueba la causa, pero sugiere que la brecha puede reflejar de dónde viene la etiqueta y no solo la química. La regla TPSA < 67 Å² y HBD ≤ 1 la cumple una proporción de naturales 6.6 puntos menor que la de los demás (41.2% contra 34.6%): es una diferencia de proporciones menor que la de la etiqueta, no una parte de ella, así que esa regla no alcanza para explicarla (quedan el eflujo, descriptores no medidos o el sesgo de qué se ensayó).

**Una inferencia que no debe repetirse.** El reporte del Avance 1 (`Avance1.0.qmd`, línea 282) da bien esos números y concluye que «la química da cuenta de aproximadamente un tercio de la diferencia», que es 6.6 entre 18.9. Esa operación no es válida: son dos diferencias de proporciones distintas, no una descomposición. El reporte entregado no se reescribe, pero el del Avance 3 no debe reutilizar ese párrafo.

**Se propone.** Un solo modelo, con el desempeño reportado por separado en naturales y en el resto y declarando siempre qué definición de «natural» se usó. No entrenar por separado: la permeabilidad depende de la estructura y no del origen, habría 3,366 compuestos de un lado y 4,439 del otro, y el segundo grupo mezcla análogos, fármacos y moléculas que simplemente no están en COCONUT. Tampoco el origen como variable, porque en parte sería una pista de la procedencia de la etiqueta. **La evaluación por origen se hace también dentro de cada grupo A, B y C**, no solo en el global: es la misma lógica de la [1.1](#d1-1), que usa A–D para estratificar y nunca para excluir, y es la medición que distingue las dos explicaciones. Si un modelo rinde peor en naturales solo en B y C, está aprendiendo ruido de curación y no química. Se revisa la propuesta solo si la evaluación por origen muestra que el modelo falla en naturales.

**Umbral de TPSA.** El óptimo sube con la diversidad del conjunto: 66.8 Å² (publicado), 66.6 (grupo A), 83.6 (A+B), 101.9 (completo) y 107.0 (entrenamiento). Aún no hay intervalos de confianza.

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

> **Pregunta:** 131 esqueletos de conectividad reúnen estereoisómeros con clases BBB distintas. ¿Es una diferencia real de permeabilidad entre formas estereoquímicas, o son etiquetas que vienen de ensayos que no deberían compararse? Si es lo primero, ¿vale la pena conservar la estereoquímica en la representación?

**Qué pasó.** Las 7,805 filas con clase son 4,018 esqueletos de conectividad, y en 131 de ellos (429 filas, el 5.5% del conjunto) dos estereoisómeros del mismo compuesto llevan etiquetas opuestas. La partición los mantiene juntos para que no haya fuga ([1.2](#d1-2)), así que no contaminan la evaluación, pero sí acotan el techo: un modelo que trabaja sobre descriptores sin estereoquímica no puede separarlos ni en principio, y cada par discordante aporta un error inevitable.

**Cuánto pesa, y en qué métrica.** En **exactitud** ya está medido y no aprieta: son **151 errores inevitables sobre 7,805**, un techo del **98.1%** que ningún modelo realista alcanza, así que no explica nada de lo que falte ([los datos del proyecto](datos-contenido.md)). En **MCC y AUPRC sobre la clase minoritaria**, que son las métricas del proyecto por la [C.1](#dc-1), no está medido, y ahí sí podría apretar: los 429 compuestos no se reparten por igual entre las dos clases. Eso es lo que falta del [issue #28](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/28), cuyo enunciado pide calcular un techo que en exactitud ya existe.

**Por qué se pregunta.** Es una de las dos lecturas y no se distinguen desde los datos. Si la estereoquímica cambia de verdad el paso por la barrera —cosa plausible, porque los transportadores son estereoselectivos—, entonces la representación actual pierde información y hay que decir en el reporte que el techo está acotado por diseño. Si en cambio los pares vienen de ensayos distintos que se compararon mal, entonces son ruido de curación y la cota es menor de lo que parece. Su criterio farmacológico es lo que decide cuál de las dos pesa más.

### Supuestos

| # | Supuesto | Estado | Qué se sabe | Si falla |
|:--|:--|:--|:--|:--|
| S1.1 | Cada fila es una observación independiente | Desmentido | 7,805 filas son 4,018 esqueletos; 131 esqueletos reúnen estereoisómeros con etiquetas distintas (429 filas), lo que acota el techo alcanzable ([1.8](#d1-8)) | Partición y reportes agrupan por esqueleto |
| S1.2 | Los grupos A–D son una escala de confiabilidad | Desmentido | Ver [1.1](#d1-1). BBB− es 12.1% en A y 92.2% en D | Estratificar, no excluir |
| S1.3 | El umbral de TPSA publicado es una constante | Acotado | Cambia con el subconjunto (ver [1.6](#d1-6)) | Derivarlo solo sobre entrenamiento |
| S1.4 | «Natural» es una categoría limpia | Acotado | Es coincidencia exacta con COCONUT | Declarar la definición usada |
| S1.5 | La brecha entre naturales y el resto es química | Sin comprobar | Es de ~19 puntos, pero no existe en el grupo A (87.6% contra 88.4% BBB+) y sí en B y C ([1.6](#d1-6)); la regla TPSA/HBD difiere solo 6.6 puntos entre los dos | Evaluar por origen global y dentro de cada grupo A, B y C |
| S1.6 | Los valores atípicos son alertas, no errores | Asumido | No se recortan ni eliminan | — |
| S1.7 | Mandar los 312 acíclicos a entrenamiento es una regla razonable | Sin comprobar | Es el valor por omisión de `scaffold_split` y no sale de ninguna medición; ninguno entra a validación ni a prueba. Dentro del entrenamiento hay 127 filas en 44 esqueletos compartidos (estereoisómeros) | Escribir y justificar la regla antes del baseline; en la validación cruzada se agrupan por esqueleto de conectividad |
| S1.8 | El conjunto externo de Spielvogel sirve para validar | Desmentido | 154 nombres, sin SMILES ni InChI | Conseguir las estructuras |
| S1.9 | Yeo-Johnson es una buena transformación | Desmentido en parte | La matriz guardada la asume, pero la validación cruzada del 12 de octubre la deja por debajo de min–max en 12 de los 15 pliegues y de estandarización en 13, sin que la diferencia alcance significancia ([1.5](#d1-5)) | Rehacer la selección de la §9 sobre otra transformación y reejecutar el notebook; las dos versiones de la matriz, transformada y sin transformar, ya están guardadas |
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

#### 2.1 · El alcance: cinco categorías de enfermedad {#d2-1 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes preguntaba por cuatro dianas sueltas

**Qué se decidió.** El alcance de la fase 2 son **cinco categorías**: Alzheimer, Parkinson, neuroinflamación, depresión y estrés oxidativo. Las demás se remueven. La patrocinadora lo cerró en la reunión del 15 de octubre: «sí se pueden resumir a esas… y si los demás adelante los pueden remover» ([acta](acta-patrocinadora.md#e3)).

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

#### 2.2 · Forma del modelo: por diana, por categoría o multitarea {#d2-2 .abierta .definir}

**Estado:** abierta · necesita su definición · después de la [2.1](#d2-1)

> **Pregunta:** Con la lista ya fijada, ¿un modelo por diana, uno por categoría de enfermedad o uno multitarea con todas? ¿Qué dianas son prioritarias?

**Qué pasó.** Los volúmenes difieren en tres órdenes de magnitud: Alzheimer 52,676 registros, Parkinson 32,372, neuroinflamación 12,331, depresión 10,888, Huntington 153 y ELA 53. Con 53 registros ELA no sostiene un modelo propio; con 52,676 Alzheimer sí. Un modelo multitarea comparte representación entre dianas y es la única forma de incluir las pequeñas, a costa de mezclar señales.

#### 2.3 · Etiquetado por tres vías y criterio de «activo» {#d2-3 .propuesta .revisada .definir}

**Estado:** propuesta · revisada el 7 y el 17 de octubre · necesita su definición

> **Pregunta, ya estrecha:** las columnas de la sección 5 del diccionario dan una concentración y una relación **en las tres fuentes**. En su correo del 16 de octubre descartó «hacer la inferencia, al menos no de forma directa». ¿Descartó usar esas columnas con el mismo corte, o solo inferir lo que no viene informado, como las 2,001 relaciones de NPASS? Se le muestra con filas reales de cada fuente a la vista.
>
> *Y una petición nueva:* un **desenlace** —qué compuestos rescataron neuronas en sus ensayos y a qué concentración— que es lo que haría estimable el umbral que ella quiere ([P4](acta-patrocinadora.md#p4)).

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
| **Par compuesto-diana** | 19,488 | 2,756 · **14.1%** |
| Par, sin los inactivos por texto *(definición vigente)* | 18,107 | 13 · **0.1%** |

Las 29,730 filas son **772 compuestos**, así que al agrupar por par su peso cae a una cuarta parte. Y la definición que adopta la [propuesta](variable-objetivo-fase2.md) los deja fuera por otra razón —el `>` de 10 µM lo asignó el equipo que armó el archivo, no el ensayo original— con lo que la objeción **se extingue por construcción**.

Esto se escribe así porque la versión anterior de esta entrada llamaba al 61% «el argumento más fuerte contra el corte en 10 µM», y lo era solo mientras la unidad fuera el registro. Deja de ser una razón para preferir 1 µM.

**Por qué estas cifras no son las de antes, y las dos están bien.** La versión anterior de esta tabla contaba 61,001 filas censuradas y daba 59,859 / 54,419 / 7,474 negativos seguros, todas tomadas de la **sección 7 del diccionario de la patrocinadora**, que describe el **archivo completo de 225,513 registros**. El que recibimos tiene 202,647, el 89.9% ([2.6](#d2-6)). La razón entre los dos archivos es 1.113 y las razones entre cada par de cifras van de 1.109 a 1.127, así que la diferencia es de población y no de método: los porcentajes coinciden exactos (98%, 89%, 12%). Aquí se usan las del archivo recibido, que son las que el modelo va a ver, y cada cifra del sitio declara de cuál de los dos archivos sale, como en [los datos del proyecto](datos-contenido.md).

**Denominadores.** Las proporciones dependen de la unidad. «Registro etiquetado» es todo el archivo, fenotípicos incluidos; «par esqueleto × gen» es un esqueleto de conectividad contra un gen (`target_gene`):

| Unidad | Umbral | Denominador | Activos | Inactivos | % activos | Razón |
|:---|:--|--:|--:|--:|--:|--:|
| Registro etiquetado | ≥ 5 | 194,086 | 119,835 | 74,251 | 61.7% | 1.6:1 |
| Registro etiquetado | ≥ 6 | 194,086 | 86,238 | 107,848 | 44.4% | 0.8:1 |
| Par esqueleto × gen | ≥ 5 | 71,145 | 50,177 | 20,968 | 70.5% | 2.4:1 |
| Par esqueleto × gen | ≥ 6 | 71,145 | 35,966 | 35,179 | 50.6% | 1.0:1 |

El conteo por par no es todavía el conjunto de entrenamiento: de 114,549 registros con categoría de diana, 109,264 reciben etiqueta; se excluyen 4,810 sin gen y 327 sin esqueleto calculable, y quedan 104,127 agrupables en 71,145 pares. El recuento marca un par como activo si alguna observación lo es, y con esa regla hay 1,810 pares discordantes con ≥ 5 y 2,426 con ≥ 6. El máximo de etiquetas no selecciona la medición más potente.

**Umbral.** Con pChEMBL, ≥ 5 daba 87.1% de activos (6.7:1) y llevó a proponer ≥ 6; con las tres vías la razón baja a 1.6:1 por registro. El sesgo de los registros con pChEMBL es una explicación posible, no demostrada. Se conserva ≥ 5 como primario y ≥ 6 como robustez: el balance de clases no determina el umbral biológico.

**La llave del par es el esqueleto × gen, y no el identificador del compuesto.** `source_compound_id` usa prefijos distintos por fuente —`CHEMBL…` contra `NPC…`— y **no comparte ni un valor** entre ellas, así que con esa llave un compuesto medido en dos fuentes entra como dos pares independientes y sus contradicciones quedan invisibles: son **164 pares** en conflicto entre ChEMBL y las fuentes naturales que así no se verían. Se usa el [esqueleto de conectividad](glosario.md#par-compuesto-diana) × `target_gene`, que además es la misma llave que `grupos_cv` usa en `src/data_prep/splits.py` para la validación cruzada agrupada, de modo que la unidad de etiquetado y la de partición coinciden.

**Y «por fuente» no se puede reportar sobre el par, porque la fuente no es un atributo del par.** Con la llave por esqueleto, 827 de los 828 pares de CMAUP comparten par con otra fuente, y 42.4% de los de NPASS: **CMAUP tiene exactamente un par propio**. Así que el desempeño se reporta en **estratos disjuntos por procedencia de la evidencia**, que sí son aditivos:

| Estrato | Pares | Activos |
|:--|--:|--:|
| Solo ChEMBL | 62,414 | 75.6% |
| Solo NPASS | 2,114 | 12.1% |
| Solo CMAUP | 1 | — |
| Mixtos | 1,592 | 37.5% |

La brecha real entre ChEMBL y los naturales es de **63 puntos**, no los 52 que sugería contar cada par en todas sus fuentes. Es el riesgo de la [2.5](#d2-5) cuantificado sobre la unidad correcta, y lo que vigila el control de atajo del [issue #32](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/32).

**El corte es una convención declarada, no un hallazgo, y conviene decir por qué 10 µM.** El archivo **no tiene columna de desenlace**: nada registra si un compuesto funcionó, así que no hay nada contra lo que calibrar y un umbral no es estimable. Todo candidato que se puede construir falla por eso: un percentil de la distribución de la diana es circular, y la moda del límite de censura está condicionada al fracaso —se midió, y deja seis dianas con 93–96% de activos, peor que el corte global—. Lo que sí sostiene el 10 µM es otra cosa: es aproximadamente **la concentración libre máxima alcanzable con una dosis oral convencional sin toxicidad**, y por encima de ella la actividad medida rara vez se traduce in vivo y dominan los artefactos de agregación que mira la [C.4](#dc-4). Es una cota de alcanzabilidad, no una constante biológica — y es un argumento mejor que «es el valor modal».

**Pero el mismo corte no significa lo mismo en cada diana, y eso se reporta.** La mediana de potencia va de 7.40 en `LRRK2` a 5.02 en `NFE2L2`, **241 veces**, así que con 10 µM `LRRK2` queda en 98.1% de activos —casi constante, inútil como objetivo— y `NFE2L2` en 50.7%. Mientras el corte siga siendo global, **se publica la tasa de activos por diana** junto con cualquier cifra agregada, para que se vea que la etiqueta no mide lo mismo en todas. La salida de fondo es no cortar, y está en la [2.9](#d2-9).

#### 2.4 · Los 88,098 registros fenotípicos {#d2-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Van dentro de un modelo específico, aparte o fuera del alcance?

**Qué pasó.** El 43.5% de los registros no corresponde a ninguna diana de la lista; entraron por la ruta `neuronal_assay`: sistemas celulares neuronales donde se midió un efecto sin identificar la proteína responsable. Responden «¿hace algo en un sistema neuronal?», no «¿actúa sobre esta diana?».

**Se propone.** Los 114,549 con categoría de diana alimentan el modelo (el conteo agrupable, 104,127 en 71,145 pares, no es el tamaño final). Los 88,098 fenotípicos se conservan aparte para otra pregunta; no se descartan.

#### 2.6 · La partición de prueba que sí se había reservado {#d2-6 .ratificada .revisada}

**Estado:** ratificada · el 15 de octubre de 2026 · revisada: antes era una pregunta abierta

**Qué se decidió.** Sí había una partición reservada, **se hizo al azar y sin criterio**, y la patrocinadora entrega el archivo completo para que el equipo la rehaga. «Partamos de la base de datos completa que se las podemos pasar… ustedes que son los expertos tengan la base completa y hagan bien esas separaciones» ([acta](acta-patrocinadora.md#p1)).

**Qué pasó.** El archivo se llama `..._Entrenamiento.csv`: el diccionario describe 225,513 filas y el recibido tiene 202,647, el 89.9%. La sospecha era correcta. Al explicarle por qué el azar no sirve —si hay cincuenta análogos de la morfina y el 10% se llevó cinco, el modelo memoriza el andamiaje y la evaluación sale inflada— lo aceptó sin reservas: «lo hicimos muy a la ligera… si hay una forma de hacerlo con mejores criterios, adelante».

**Su condición, que repitió cuatro veces:** que se reserve una prueba que el modelo nunca vea. Su razón no es metodológica sino práctica: no espera que aparezca otra base de datos con la que validar después. Eso se respeta en la [2.7](#d2-7), que ya particiona por andamio.

**La limitación que hay que declarar en el reporte.** Un 10% extraído al azar del mismo archivo comparte andamios, ensayos y artículos con el 90%: es una partición interna con otro nombre. Prueba filas nuevas, no química nueva ni protocolos nuevos. Si el reporte final la llama «validación externa», sobrevende lo que compra. Con el archivo completo en mano el punto es casi histórico, pero queda escrito porque ella descansa mucho en ese conjunto.

**Pendiente de Jorge Uribe:** el método con que separó el 10%, y verificar con el equipo si introduce sesgo (ofrecido en el correo del 16 de octubre).

#### 2.7 · Partición de la fase 2 {#d2-7 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Hay agrupaciones por familia química o laboratorio de origen que respetar, más allá del andamio?

**Se propone.** El criterio de la fase 1: Bemis-Murcko sobre los 99,585 esqueletos, agrupando por esqueleto de conectividad y verificando que no haya fuga, y además disjunta por fuente si los datos lo permiten. Es la mitigación natural de la [2.5](#d2-5): si entrenamiento y prueba no comparten fuente, un modelo que aprendió la fuente se delata. Depende de la [2.6](#d2-6).

#### 2.8 · Origen natural en la fase 2: cómo se define y si se entrena aparte {#d2-8 .abierta .definir}

**Estado:** abierta · necesita su definición

> **Pregunta:** ¿Puede aportar el cruce con COCONUT del archivo de actividad, como ya lo hizo con el de permeabilidad? Ese archivo trae `coconut_id_exact_match` y el de actividad no trae ninguna columna de origen natural, así que hoy lo único disponible es la fuente, que no separa limpiamente. Y con esa definición resuelta: ¿hay una razón biológica para tratar distinto a los productos naturales en la actividad, o basta con reportar el desempeño por origen?

**Qué pasó.** Priorizar productos naturales con actividad neuroprotectora es el objetivo del proyecto, y es esta fase la que lo cumple. Pero el archivo de actividad no trae una marca de «natural»: lo más cercano es la **fuente**, porque NPASS y CMAUP son bases de naturales y ChEMBL es sobre todo sintético. Esa fuente está confundida con la vía de etiquetado ([2.5](#d2-5)): los 15,293 registros de NPASS y CMAUP no traen pChEMBL. Además, el 65.4% de los esqueletos naturales (2,727 de 4,172) también aparece en ChEMBL, así que la fuente no separa limpiamente el origen, y solo 1,445 esqueletos existen únicamente en NPASS y CMAUP. Ojo con el método: `inchikey_source` viene vacío en los 187,354 registros de ChEMBL, así que el solapamiento se calcula desde `smiles_raw`. A diferencia de la fase 1, aquí hay un desplazamiento de dominio real: casi todo el entrenamiento es ChEMBL y el uso final son naturales.

**Por qué se le pregunta a ella y no lo resuelve el equipo.** El archivo de permeabilidad llegó ya cruzado contra COCONUT, con tres columnas (`coconut_id_exact_match`, `coconut_ids_key14_match`, `coconut_matches_key14`), y ese cruce es el que sostiene el hallazgo central del Avance 1. El de actividad no trae ninguna: las únicas columnas de procedencia son `source` y `inchikey_source`, y el diccionario no menciona COCONUT. El equipo podría intentarlo por su cuenta desde `smiles_raw`, que está en los 202,647 registros, pero sería un cruce distinto del suyo —otra versión del catálogo, otra regla de estandarización— y los dos no serían comparables entre fases, que es justamente lo que el proyecto necesita. Pedírselo cuesta una pregunta; rehacerlo cuesta una fuente de discrepancia permanente.

**Se propone, mientras tanto.** Usar la **fuente como definición provisional** de «natural», declarándola como tal en todo lo que se reporte. Entrenar un solo modelo y reportar el desempeño por origen, con la partición disjunta por fuente de la [2.7](#d2-7) para ver si falla al pasar de ChEMBL a naturales. Un modelo aparte, o ponderar a los naturales, solo si esa evaluación lo muestra. Si llega el cruce, la definición pasa a ser ese cruce y la fuente queda como comprobación.

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
| S2.11 | La fuente (NPASS y CMAUP) identifica a los productos naturales | Sin comprobar | El 65.4% de los naturales también está en ChEMBL y solo 1,445 esqueletos son exclusivos de NPASS y CMAUP ([2.8](#d2-8)) | Definir «natural» por cruce con COCONUT si se puede |

