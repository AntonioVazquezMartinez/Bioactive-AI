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
| [1.5](#d1-5) | Tres modelos candidatos; de ahí, si escalar y si reducir dimensión | Vigente · revisada | |
| [1.6](#d1-6) | Naturales en la fase 1: evaluar por origen, no entrenar por separado | Vigente | 17 oct |
| [1.7](#d1-7) | Tamaño L de Sort & Slice: 2048 de trabajo; 512 es posible con XGBoost o Random Forest | Propuesta | |
| [1.8](#d1-8) | Los 131 esqueletos con etiquetas contradictorias | Abierta | |
| [1.10](#d1-10) | Entrenar dando más peso a la química rara: se mide en validación, con la regla declarada antes | Propuesta | |

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
| [2.13](#d2-13) | Ensambles para la regresión de potencia | Vigente | |

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

**Qué par es cada fase, porque no es el mismo.** En la fase 1 son la ganancia interna de los árboles y la importancia por permutación (`scripts/importancias_fase1.py`, corrida `2026-11-01-ingrid-C.2-atribucion-fase1-con-nombres`). En la fase 2 el primer método es **TreeSHAP** sobre el booster del `aft` con huellas, porque la ganancia interna no da dirección y aquí hace falta decir hacia qué lado empuja una subestructura (`scripts/atribucion_fase2.py`). El segundo sigue siendo la permutación, medida sobre la caída de concordancia de Harrell en el pliegue de evaluación. **La columna del primer método se nombra en cada corrida** (`columna_metodo_1` en sus `params`): llamarla `impureza` en las dos fases fue un defecto real, porque dos corridas hermanas traían el mismo nombre con métodos distintos dentro.

**Y TreeSHAP en el `aft` trae una trampa de signo.** Explica el **margen**, que con `survival:aft` está en ln(µM), donde más alto es **menos** potente; verificado numéricamente, el margen reproduce `log` de lo que el booster predice y SHAP reproduce el margen. Para leerlo en [pActividad](glosario.md) hay que invertirlo y reescalarlo (−SHAP / ln 10). Sin eso, toda afirmación estructural sale al revés, y saldría al revés de forma plausible, que es lo peligroso.

**La intersección se calcula solo sobre las características presentes en todos los pliegues.** El vocabulario Sort & Slice se reaprende en cada pliegue —y así debe ser, o la validación decidiría qué columnas existen—, así que una huella puede faltar en alguno. Promediar una media de un pliegue junto a una de cinco premia a las huellas raras justo en el top que esta decisión reporta; las incompletas quedan en el CSV de la corrida, pero no entran en la afirmación. Cuántas quedaron fuera se registra en `metricas.json`.

**Lo que la corrida definitiva de la fase 2 encontró, sobre el brazo `aft_huellas`.** Corrida `2026-11-06-antonio-C.2-atribucion-fase2-con-nombres`, cinco pliegues, cinco repeticiones de permutación y 2,048 bits. Los dos métodos **concuerdan**: Spearman 0.577 sobre la unión de sus 100 primeras y 11 de las 15 primeras compartidas, con la regla que ese brazo declaró antes de correr (ρ ≥ 0.50 y 8 de 15). Eso corrige la lectura de la corrida previa `2026-11-05-artemio-2.13-atribucion-aft-huellas-subestructuras`, que con 1,500 filas y una sola repetición daba 0.378 y no pasaba esa misma regla: el desacuerdo era ruido de la permutación, no un resultado. **El umbral no es el de la atribución del `aft` final** (ρ ≥ 0.70, [2.13](#d2-13)): cada corrida declaró el suyo antes de medir y el del brazo con huellas es el más laxo, y la razón que da esa corrida previa para su propio ruido es permutar unas 2,270 columnas casi todas cercanas a cero, contra las 227 del modelo final. Una cifra de acuerdo se compara contra su propio umbral o no se compara. En la intersección hay once características, dos de ellas huellas —los identificadores Morgan `2041434490` y `3777168895`, que la corrida previa describe como un nitrógeno de anillo aromático tipo piridina y un CH aromático vecino a un N aromático—, cinco dianas (MAOA, MAOB, DRD2, LRRK2, BCHE) y los descriptores `BertzCT`, `SMR_VSA3`, `MolLogP` y `fr_halogen`. **El contraste obligatorio no reproduce la jerarquía de la fase 1**: TPSA queda en los puestos 54 y 48 y HBD en 247 y 308, así que la dominancia de TPSA y donadores que la fase 1 encuentra aquí no aparece, y una afirmación estructural de una fase no se traslada a la otra. La convención del párrafo anterior no mueve el acuerdo (0.577 contando solo las completas, 0.576 contándolas todas), aunque dejó fuera 618 de 2,534 características, todas huellas.

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

**Métricas del ranking (propuesta; la principal se declara antes de ver resultados; se implementan en el Avance 5).** Cuántos compuestos se pueden ensayar no se sabe, así que se resuelve como análisis de escenarios y se dice cuál gobierna bajo cada supuesto. Ejemplo: si el laboratorio ensaya 20 compuestos, importa que los primeros 20 funcionen; si ensaya 1,000, importa no dejar fuera candidatos reales.

| Escenario | Qué manda | Métricas |
|:--|:--|:--|
| Pocos compuestos (el realista) | ordenar bien; el falso positivo es el caro porque gasta presupuesto de ensayo | **enriquecimiento al 1%** (principal), enriquecimiento al 5%, precisión en los primeros 100, BEDROC, área bajo la curva de precisión-recall |
| Cribado amplio | la sensibilidad: no perder candidatos reales | recall a precisión fija, enriquecimiento al 5% |

**Primera medición de estas métricas, fase 2 (4 de noviembre).** Corrida `2026-11-03-artemio-C.5-ranking-fase2-aft`: `aft` con predicciones fuera de pliegue (una semilla, 5 pliegues, sin tocar la prueba), α de BEDROC = 20 declarado antes, ordenando los pares por potencia predicha. Dos controles: azar y ordenar solo por la potencia media de la diana. Enriquecimiento, activos recuperados y tasa base:

| estrato | tasa base | EF 1% (activos / k) | EF 5% | precisión en 100 | BEDROC | `solo_diana`, EF 1% |
|:--|--:|:--|--:|--:|--:|--:|
| todos | 71.4% | 1.40 (544/544) | 1.39 | 1.00 | 0.99 | 1.36 |
| solo ChEMBL | 74.8% | 1.34 (507/507) | 1.33 | 1.00 | 0.99 | 1.30 |
| mixto | 40.3% | 1.55 (10/16), IC 0.86–2.24 | 1.51 | 0.59 | 0.59 | 1.40 |
| solo NPASS | 12.3% | 3.09 (8/21), IC 1.59–5.16 | 2.40 | 0.31 | 0.29 | 1.16 |

- **El enriquecimiento tiene un techo de 1/tasa base**, 1.40 con 71.4% de activos: en `todos` y `solo_chembl` el `aft` ya está en el techo (544 de 544) y el número no discrimina. Ahí se lee mejor la precisión en 100 y el control: **saber la diana ya da casi todo** (1.36 contra 1.40), así que el ranking global mide sobre todo qué diana, no qué molécula.
- **En `solo_npass`, el único estrato donde el techo no estorba, el `aft` pone 8 activos entre los 21 primeros del 1% (3.1×) y 31 de 105 en el 5% (2.4×)**, contra 1.2× y 0.6× de ordenar por diana. El intervalo del 1% es ancho (1.6–5.2) porque son 21 pares y 8 aciertos: es la forma de cuidar de no repetir el 1.92× que era un compuesto. Con el azar el 1% dio 4 de 21 (1.5×), lo que muestra el ruido de esa celda.
- Una semilla, ranking sobre pares y no sobre compuestos. La curva por diana de la C.5 sigue sin calcular.

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

**2.2 puntos de AUROC y 7.1 de MCC.** Lo que sigue compara, en cada métrica, **el par de modelos más lejano de esa métrica**, que no es el mismo par: en MCC son el boosting y la logística (0.0222; el bosque contra la logística da 0.0178) y en AUROC el bosque y la logística. Las dos cifras de MCC son de una semilla y media de pliegues, **la misma medida que el 7.1**. Comparar siempre el mismo par subestimaría la distancia entre familias en una de las dos. *Versión superada:* esta línea daba 0.0153 y 0.0130, que son las mismas dos distancias sobre las medias de 15 evaluaciones — el estimador que el párrafo siguiente descarta, y de donde salía el «1.5 puntos».

En MCC, con la misma medida en las dos comparaciones —una semilla, media de pliegues—, el agrupamiento mueve 7.1 puntos y la elección de modelo 2.2 entre la logística y el boosting: algo más de tres veces. **Una versión anterior de esta entrada decía 1.5 puntos y casi cinco veces, y comparaba dos estimadores**: el 1.5 es la diferencia entre las medias de 15 evaluaciones (0.7019 contra 0.6866) y el 7.1 sale de una sola semilla. Y cuánto separa a los modelos depende de cuántos se comparen: 2.2 con las tres canalizaciones del 03, 4.2 con los once del Avance 5; un múltiplo tiene que decir entre cuál de ellos divide. **En AUROC no**, y la versión anterior de esta entrada decía que sí: con el mismo estimador —una semilla, predicciones fuera de pliegue, bootstrap de grupos— el agrupamiento mueve 0.0223 y la distancia entre el bosque y la logística 0.0225. La afirmación salía de comparar los 2.2 puntos de ese estimador contra el «menos de 2» del promedio de 15 pliegues, que es otro. Con cualquiera de los dos se sostiene lo que de verdad importa: **una cifra que no diga cómo agrupó no se puede comparar** con las de este registro. El criterio vive en `grupos_cv`, en `src/data_prep/splits.py`, y lo usan las dos fases.

**Corrección del 4 de noviembre.** El «2.2 puntos de AUROC y 7.1 de MCC» de esta entrada y de todo lo que la cita es **del bosque**. Con el `svm_rbf` que se entrega son 1.3 y 1.9, así que «el agrupamiento mueve más que la elección de modelo» no se sostiene para el modelo final (1.9 contra 4.2 entre los once). Lo que sí se sostiene es la escalera de abajo: 33.3 puntos de MCC sobre el modelo entregado, en una corrida registrada. Las copias en otros documentos se corrigieron en el mismo cambio.

**La escalera de agrupación, medida con otros dos modelos (3 de noviembre).** Las dos filas de arriba son del bosque. La corrida `2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad` repite la comparación con `svm_rbf` y `logistica`, sobre las 6,306 filas de entrenamiento y validación y la matriz de 151 columnas, con 3 semillas y 5 pliegues, **sin tocar la prueba reservada**, y agrega agrupamientos más estrictos que el actual: componentes conexas de similitud de Tanimoto (Morgan radio 2, 2048 bits) con umbral 0.6, 0.5 y 0.4, fijados antes de correr.

| Agrupamiento | Grupos | `svm_rbf` AUROC / MCC | `logistica` AUROC / MCC | Similitud al vecino más cercano |
|:--|--:|:--|:--|--:|
| Al azar | 6,306 | 0.947 / 0.752 | 0.934 / 0.720 | 0.90 |
| Por esqueleto | 2,626 | 0.934 / 0.725 | 0.927 / 0.714 | 0.62 |
| Por andamio | 2,239 | 0.932 / 0.721 | 0.923 / 0.698 | 0.75 |
| **Andamio ∪ esqueleto (actual)** | 1,048 | **0.919 / 0.702** | **0.913 / 0.687** | 0.50 |
| Similitud ≥ 0.6 | 1,413 | 0.913 / 0.688 | 0.897 / 0.659 | 0.42 |
| Similitud ≥ 0.5 | 1,017 | 0.835 / 0.486 | 0.848 / 0.573 | 0.33 |
| Similitud ≥ 0.4 | 631 | 0.780 / 0.419 | 0.816 / 0.513 | 0.28 |
| *Prueba reservada, `svm_rbf`, ya registrada* | | *0.793 / 0.339* | | |

Lo que se lee, con sus límites:

- **Cuánto ayuda a la cifra agrupar mal depende del modelo.** Con «solo andamio» el resultado sube 1.3 puntos de AUROC y 1.9 de MCC con `svm_rbf`, y 1.0 y 1.1 con `logistica`, contra los 2.2 y 7.1 del bosque. Es coherente con que un modelo con más capacidad para memorizar aproveche más a los estereoisómeros a los dos lados del pliegue, pero **eso no se midió aquí**: es una lectura. Los 2.2 y 7.1 de esta entrada son del bosque y no deben citarse como un efecto general del agrupamiento.
- **La escalera baja de forma ordenada en la cadena azar → actual → similitud**, tanto en desempeño como en la similitud al vecino más cercano. Entre «por esqueleto» y «por andamio» no hay orden porque ninguno contiene al otro: «por andamio» separa estereoisómeros del mismo compuesto, y por eso su vecino más cercano es más parecido (0.75 contra 0.62), que es la razón de unirlos.
- **Ubicar la prueba reservada en la escalera por su AUROC engaña.** El AUROC de la prueba (0.793) cae entre las filas ≥ 0.5 (0.835) y ≥ 0.4 (0.780) de `svm_rbf`, pero la **similitud de la propia prueba con el ajuste, medida sin etiquetas** (corrida `2026-11-03-artemio-1.2-escalera-ampliada-permeabilidad`, un acceso estructural anotado en `experimentos/prueba.csv`), es 0.414 de media al vecino más cercano (mediana 0.372; terciles 0.308 y 0.459). Eso es el nivel de la fila ≥ 0.6 (0.422), donde `svm_rbf` da 0.913, y no el de ≥ 0.5 (0.331) ni el de ≥ 0.4 (0.277). **Cuánto se parece la prueba al entrenamiento no explica por sí solo su caída**: queda lo que la prueba tiene de distinto además de la similitud (tamaño, composición de andamios raros, prevalencia). Es lo que mide E2. La comparación es ligeramente favorable a la prueba: sus vecinos se buscan entre las 6,306 filas completas y los de la validación entre el 80%.
- **Con agrupamiento estricto el modelo simple NO se degrada menos de forma distinguible.** Con seis modelos y la diferencia pareada de AUROC `logistica − svm_rbf` (semilla 0, bootstrap de grupos): −0.013 con pliegues al azar y −0.008 por andamio (los dos distinguibles de cero), −0.007 con el agrupamiento actual, −0.011 a ≥ 0.6, **+0.003 a ≥ 0.5 y +0.025 a ≥ 0.4, con intervalos que incluyen el cero** (−0.014 a 0.024 y −0.027 a 0.079). La lectura de E1 («`logistica` supera a `svm_rbf` en AUROC a 0.5 y 0.4») era ruido y se retira como hallazgo. Lo que sí queda: la ventaja de `svm_rbf` sobre `logistica` se **cierra** al apretar el agrupamiento, de 0.013 con pliegues al azar a cero, y en MCC a ≥ 0.5 la `logistica` queda 0.115 por encima, con intervalo que apenas excluye el cero (0.002 a 0.197). La diferencia pareada de MCC usa un corte fijo en 0.5 y es la lectura menos confiable.
- **Seis modelos, misma dirección.** Al pasar de pliegues al azar a similitud ≥ 0.4, el AUROC baja 0.167 en `svm_rbf`, 0.118 en `logistica`, 0.157 en `boosting`, 0.152 en `bosque`, 0.173 en `knn` y 0.204 en `mlp`: todos bajan mucho, y la `logistica` es la que menos baja. A ≥ 0.4 `logistica`, `bosque` y `boosting` (0.816, 0.822, 0.816) quedan por encima de `svm_rbf`, `knn` y `mlp` (0.780, 0.776, 0.760), pero con una semilla pareada y diferencias de intervalo ancho solo se puede decir que **el orden de los modelos cambia con el agrupamiento**, no cuál es mejor.

- **La caída de la prueba reservada (AUROC 0.793) cae entre las filas de similitud ≥ 0.5 (0.835) y ≥ 0.4 (0.780)**, lo que apunta a que buena parte de la caída respecto a la validación cruzada es química nueva. El MCC de esas dos filas (0.486 y 0.419) queda por encima del de la prueba (0.339), y el MCC depende de la prevalencia, que no es la misma. **Falta medir la similitud de la propia prueba con el entrenamiento**, que no necesita etiquetas, para ubicarla en la escalera.
- **Con agrupamiento estricto el modelo simple se degrada menos.** En similitud ≥ 0.5 y ≥ 0.4 la `logistica` supera en AUROC a `svm_rbf` (0.848 contra 0.835 y 0.816 contra 0.780). Es una sola corrida con tres semillas y no hay intervalo de la diferencia pareada: hay que verlo antes de apoyarse en ello.
- **Límites:** los grupos por similitud son desiguales (el mayor reúne entre 12% y 16% de las filas), la similitud al vecino más cercano es solo de la semilla 0, y el estrato de grupos de una sola fila no se reporta porque no llega al mínimo de 20 casos minoritarios por pliegue.

**Una línea base de peso molecular y TPSA, en la misma corrida.** Una regresión logística que solo ve esas dos columnas da AUROC 0.847 y MCC 0.579, contra 0.919 y 0.702 de `svm_rbf` y 0.913 y 0.687 de `logistica`. Por tamaño del grupo de la fila, la ventaja de `svm_rbf` sobre esa línea base es de 0.032 de AUROC en los grupos de 2 a 4 filas y de 0.076 en los de 5 o más: en la química más rara, el modelo sabe poco más que tamaño y polaridad. Por tramo de peso (cortes de #216), la ventaja es de 0.077 en ≤ 250 Da, 0.072 en 250–350, 0.10 en 350–500 y 0.059 en > 500. El número de grupos de una sola fila y el de los estratos por tamaño de grupo son propiedades de las 6,306 filas, no de la prueba.

**Los andamios grandes son más raros y más pesados.** En un análisis aparte sobre el archivo de la profesora, con un compuesto por esqueleto (4,018) y el andamio de Murcko, el número de moléculas por andamio cae con su tamaño: 9.3 en los de 6 átomos pesados o menos y 1.12 en los de más de 24, donde el 92% de los andamios son solitarios; el tamaño del andamio y el peso molecular correlacionan 0.75 en Spearman, y el % BBB+ baja de 64–71% a 48% en los de más de 24 átomos. Como `scaffold_split` manda los grupos grandes a entrenamiento y deja los pequeños a la prueba, **rareza y tamaño van mezclados en la prueba**. Ese análisis es de un script sin corrida registrada y cuenta esqueletos, no las 6,306 filas ni los 1,048 grupos: no se cita hasta que se registre.

**Qué pasó.** Los andamios grandes tienen pureza de clase extrema: el más frecuente, de 410 compuestos, es 99.5% BBB+. Con partición aleatoria al modelo le basta reconocer el andamio, y la literatura reporta que así se infla el resultado entre 7 y 13 puntos.

**Se decidió.** Bemis-Murcko, agrupando también por esqueleto de conectividad para que los estereoisómeros no se separen. Los andamios frecuentes van a entrenamiento y los raros a prueba (convención de DeepChem): 5,557 / 749 / 1,499, sin andamio ni esqueleto compartido. **Los 312 compuestos acíclicos** (cadenas sin anillos, que no tienen andamio) **van todos a entrenamiento**: no comparten estructura de anillo con nada, así que no filtran información a la prueba, pero tampoco ayudan a medir generalización estructural.

**Consecuencias.** La prueba tiene 1,390 andamios en 1,499 compuestos y 57.3% BBB+ contra 64.0% del entrenamiento: se evalúa sobre una distribución distinta de la que aprendió, que es lo realista. Construida al revés, con los frecuentes en prueba, daba 45 andamios con el benceno ocupando el 26%; la dirección de la asignación es el detalle crítico.

**¿Cuánto del derrumbe del MCC en la escalera es colocación del corte? Una parte, pero el corte de igual prevalencia no la recupera (4 de noviembre).** Corrida `2026-11-04-artemio-1.2-mcc-en-la-escalera-permeabilidad` (`scripts/experimento_mcc_en_la_escalera.py`), sin tocar la prueba reservada. A lo largo de la escalera el AUROC del `svm_rbf` baja de 0.947 a 0.780 y el MCC de 0.752 a 0.419, y en la prueba el MCC cae más que el AUROC; el MCC corta la probabilidad en 0.5, un punto fijo. Se lee el MCC de tres maneras con las mismas predicciones fuera de pliegue: `fijo` (0.5), `prevalencia` (el cuantil que declara positiva la misma fracción que el ajuste; no usa etiquetas de validación) y `óptimo` (el mejor corte del pliegue: cota optimista, usa etiquetas). La regla se declaró antes: la colocación explica parte del derrumbe si lo `recuperado` (prevalencia − fijo) en ≥ 0.5 o ≥ 0.4 supera 0.020 y es mayor que en el peldaño del proyecto.

| peldaño | MCC fijo | MCC igual prevalencia | MCC óptimo (cota) | recuperado | fracción BBB+ a 0.5 |
|:--|--:|--:|--:|--:|--:|
| al azar | 0.7515 | 0.7521 | 0.7634 | +0.0006 | 0.710 |
| por andamio | 0.7209 | 0.7122 | 0.7330 | −0.0087 | 0.707 |
| andamio + esqueleto (el del proyecto) | 0.7017 | 0.6791 | 0.7135 | −0.0225 | 0.709 |
| similitud ≥ 0.6 | 0.6876 | 0.6767 | 0.7072 | −0.0109 | 0.698 |
| similitud ≥ 0.5 | 0.4859 | 0.5327 | 0.6554 | **+0.0468** | 0.606 |
| similitud ≥ 0.4 | 0.4190 | 0.4233 | 0.5598 | +0.0043 | 0.590 |

La prevalencia real del ajuste es 0.650. **Los seis controles pasan** (el MCC fijo es el de la escalera registrada). Por la regla declarada la colocación explica parte del derrumbe, **pero solo en el peldaño de 0.5** (+0.047) y no en el de 0.4 (+0.004), y en el peldaño del proyecto el corte de igual prevalencia es *peor* que el de 0.5 (−0.023): no es una mejora gratuita. **Lo que sí se ve es la cota:** con un corte óptimo el MCC sería 0.655 en ≥ 0.5 y 0.560 en ≥ 0.4, contra 0.486 y 0.419 con el fijo, es decir, **0.17 y 0.14 de MCC dependen de dónde se corta**; y el corte fijo declara BBB+ al 71% de los compuestos en los peldaños laxos contra una prevalencia de 65%, y a 61% y 59% en los estrictos. Es decir, bajo un cambio de distribución el modelo cambia de sesgo (de declarar de más a declarar de menos), y ningún corte fijo ni de igual prevalencia lo sigue. Para la prueba reservada (AUROC 0.793, MCC 0.339), un AUROC parecido al de los peldaños de 0.5 y 0.4 con un MCC menor que el fijo de ellos (0.486 y 0.419) es consistente con esa colocación extra, pero **no se afirma como causa**. **Verificado de forma independiente:** recalculé el peldaño ≥ 0.5 con una matriz densa de RDKit, un MCC escrito a mano y el corte como el k-ésimo mayor puntaje: 0.4859 y 0.5326 contra 0.4859 y 0.5327 (la diferencia de 0.0001 es el empate en el cuantil). **Límites:** un solo modelo (el `svm_rbf`); el corte óptimo usa las etiquetas del pliegue y no es un resultado; y ninguna de las tres lecturas es el umbral elegido con validación interna agrupada, que sigue sin medirse.

**¿La escalera depende de cómo se define «parecido»? La forma sí, la caída total no tanto (4 de noviembre).** Corrida `2026-11-04-artemio-1.2-escalera-definicion-de-parecido-permeabilidad` (`scripts/experimento_escalera_definicion_de_parecido.py`), sin tocar la prueba reservada. La escalera agrupa con Tanimoto sobre Morgan radio 2 (ECFP4); se repite con ECFP6 (radio 3) y con atom-pair, 2,048 bits. Un umbral de 0.5 no significa lo mismo en dos huellas, así que **se comparan peldaños de igual severidad**: para cada huella se elige el umbral (en pasos de 0.01) cuyo número de grupos queda más cerca de los de ECFP4 (1,413, 1,017 y 631). La regla se declaró antes: la escalera es robusta a la definición si en cada peldaño el AUROC del `svm_rbf` difiere de ECFP4 en menos de 0.020.

| huella | umbral | grupos | mayor grupo | AUROC `svm_rbf` | MCC `svm_rbf` | diferencia de AUROC con ECFP4 |
|:--|--:|--:|--:|--:|--:|--:|
| ECFP4 | 0.60 / 0.50 / 0.40 | 1,413 / 1,017 / 631 | 12.1 / 14.4 / 15.9% | 0.9127 / 0.8348 / 0.7798 | 0.688 / 0.486 / 0.419 | control |
| ECFP6 | 0.52 / 0.42 / 0.32 | 1,422 / 1,043 / 608 | 11.8 / 13.2 / 14.9% | 0.9157 / 0.8688 / 0.8088 | 0.676 / 0.636 / 0.434 | +0.003 / **+0.034** / **+0.029** |
| atom-pair | 0.65 / 0.56 / 0.48 | 1,407 / 1,010 / 645 | 13.7 / **32.7** / **62.4**% | 0.8939 / no evaluable / no evaluable | 0.663 / | −0.019 |

**Los controles pasan** (los grupos de ECFP4 y sus AUROC son los de la escalera registrada). **Por la regla declarada la escalera depende de la definición:** ECFP6 difiere 0.034 y 0.029 en los dos peldaños estrictos y con atom-pair no se pueden construir (un grupo reúne el 32.7% y el 62.4% de las filas). La lectura: **la caída total es parecida** (MCC de 0.752 al azar a 0.419 con ECFP4 y a 0.434 con ECFP6 en el peldaño más estricto), pero **la forma no**: con ECFP4 casi todo el derrumbe ocurre entre el peldaño de 0.6 y el de 0.5 (de 0.688 a 0.486 de MCC), con ECFP6 es gradual. Por eso el artículo tiene que decir qué huella usó y no presentar el peldaño intermedio como una propiedad del problema. **Verificado de forma independiente:** los grupos y el mayor grupo de ECFP6 y atom-pair se reproducen con la matriz densa de RDKit, y el AUROC 0.8688 de ECFP6 a 0.42 con un ciclo de pliegues escrito aparte. **Límites:** los grupos de igual número no son igual de estrictos (hay una diferencia de hasta 26 grupos), un solo modelo para la regla (el `svm_rbf`), y las huellas son de estructura, no de farmacóforo.

**¿La escalera de semejanza existe también en la fase 2? Sí, y a partir de 0.5 de similitud no se puede ni partir (4 de noviembre).** Corrida `2026-11-04-artemio-1.2-escalera-agrupacion-actividad` (`scripts/experimento_escalera_fase2.py`), sin tocar la prueba reservada. El `aft`, con los mismos peldaños que la fase 1 y una sola familia de modelos: por par al azar, por molécula, `grupo_cv` (el del proyecto) y por similitud (componentes conexas de Tanimoto sobre Morgan radio 2, 45,662 moléculas únicas). La regla se declaró antes: la escalera existe si el peldaño evaluable más estricto cae al menos 0.030 (el doble de la dispersión de 0.015 entre los siete modelos competitivos de la 2.13) por debajo de «por molécula».

| peldaño | grupos | mayor grupo | concordancia `todos` | `solo_npass` | similitud media al vecino más cercano |
|:--|--:|--:|--:|--:|--:|
| por par al azar | 56,241 | 0.0% | 0.8100 | 0.6697 | 0.844 |
| por molécula | 45,662 | 0.0% | 0.8071 | 0.6408 | 0.769 |
| `grupo_cv` (el del proyecto) | 10,242 | 2.2% | 0.7609 | 0.6308 | 0.645 |
| similitud ≥ 0.6 | 5,286 | 16.1% | 0.6953 | 0.6233 | 0.439 |
| similitud ≥ 0.5 | 2,512 | **69.1%** | no evaluable | | |
| similitud ≥ 0.4 | 1,028 | **90.5%** | no evaluable | | |

**El control pasa** (0.7609 contra 0.761 de la 2.13) y la caída del peldaño de «por molécula» al evaluable más estricto es de **0.112, siete veces el umbral declarado**: la escalera existe en la fase 2. **Dos hallazgos que la fase 1 no tenía.** (1) A 0.5 y 0.4 de similitud casi todo el espacio químico queda en una sola componente conexa (69.1% y 90.5% de las filas), así que **no hay forma de evaluar la fase 2 con química realmente nueva a esos niveles**: el `grupo_cv`, con similitud al vecino de 0.645, es mucho más laxo que lo que la fase 1 pudo medir (0.277 en su peldaño más estricto). Es una limitación del conjunto, no de la escalera. (2) En `solo_npass` la caída es mucho menor (de 0.670 a 0.623, contra 0.810 a 0.695 en `todos`); no se puede distinguir si es robustez o un suelo cercano al azar, porque ese estrato ronda 0.63 aun con partición laxa. **Verificado de forma independiente:** los vecinos ≥ 0.4 de la matriz dispersa coinciden con la similitud exacta de RDKit en 150 de 150 moléculas al azar; el vecino más cercano matricial difiere de `BulkTanimoto` en menos de 3×10⁻⁸; y los 5,286 grupos y el 16.1% del mayor se reproducen con una unión-búsqueda propia. **Límites:** una sola familia de modelos (el `aft`) y una métrica distinta (concordancia, no AUROC), así que las magnitudes **no son comparables** con las de la fase 1; solo el patrón. El vecino más cercano se mide sobre 1,500 filas de validación por pliegue de la semilla 0. Primera versión de la medición, con `BulkTanimoto` sobre una lista de 36,000 huellas, no terminó un peldaño en 30 minutos y se detuvo; se reemplazó por un producto de matrices exacto (`src/features/similitud.py`).

#### 1.3 · Descriptores RDKit más Morgan/ECFP4 {#d1-3 .vigente}

**Estado:** vigente

> **Pregunta:** ¿Se conoce una representación más eficiente o más interpretable para productos naturales?

**Se decidió.** 217 descriptores 2D de RDKit (203 utilizables) más Morgan/ECFP4 de 2,048 bits con `rdFingerprintGenerator`. Con `radius=2` se obtiene ECFP4, porque el número del nombre es el diámetro. Se descartaron los *embeddings* congelados de transformers, que no superan a esta combinación bajo partición por andamio.

**Qué pasó.** `Ipc` alcanza ~1e41, finito en float64 pero fuera de float32, y sklearn convierte internamente; `isfinite` no lo detecta y costó una ejecución fallida, así que se descarta. El fingerprint plegado además mezcla subestructuras en un mismo bit; por eso se evalúa **Sort & Slice**, sin colisiones y con el vocabulario aprendido solo del entrenamiento. Con 2048 columnas cubre el 84.8% de las subestructuras del entrenamiento y el 68.0% de las del conjunto de prueba (el vocabulario se aprende solo con el entrenamiento, y la prueba trae los andamios raros). Esa brecha de 16.8 puntos crece con el vocabulario: 13.6 con 512 columnas y 17.8 con 4096. No es la cobertura en validación de la tabla de más abajo (71.0% con 2048), que se mide dentro de la validación cruzada.

**Lo que se midió.** Los modelos de los Avances 3, 4 y 4b se entrenaron solo con los descriptores: el cargador (`src/models/tareas.py`) usa `descriptores` por defecto y nadie lo cambió, no fue una decisión. Los cuadernos `04c_Regresion_actividad_huellas` (fase 2) y `03c_Permeabilidad_huellas` (fase 1) lo midieron con cinco brazos —descriptores, depurados, seleccionados por Lasso, descriptores+huellas y huellas solas—, el vocabulario de Sort & Slice reaprendido dentro de cada pliegue y los modelos individuales del Avance 4. El orden se invirtió respecto a lo planeado porque la fase 2 tenía ya el cuaderno armado. Corridas `2026-10-28-artemio-1.3-comparativa-regresion-huellas` y `2026-10-28-artemio-1.3-comparativa-permeabilidad-huellas`.

**El resultado es distinto en cada fase, y por eso la decisión se parte en dos.**

- **Fase 2, la potencia contra una diana: las huellas mejoran.** A cinco de los seis modelos que entran a los brazos anchos, en las 15 evaluaciones de cada uno, con diferencias de 1.9 a 6.5 veces el umbral: `knn` de 0.739 a 0.756 de concordancia, `bayesian_ridge` de 0.692 a 0.728, `ridge` de 0.691 a 0.724, `linear_svr` de 0.690 a 0.722, `arbol` de 0.670 a 0.716 con huellas solas. El `mlp` es la excepción y empeora (−0.027), con la mayor brecha entre entrenamiento y validación del cuaderno (0.255). El `svr` con núcleo quedó fuera de los brazos anchos por costo, así que 0.756 es la mejor cifra de lo que se midió y no de todo lo posible.
- **Fase 1, la permeabilidad: no mejoran a ningún modelo.** El brazo `huellas` baja el MCC de cinco de los seis modelos y solo el árbol sube (+0.013). El caso más cercano a la regla es el árbol en AUPRC (+0.035, mejor en 13 de 15), que cumple el mínimo de evaluaciones y no el umbral. Es coherente con que la permeabilidad dependa de propiedades de la molécula entera —TPSA y los donadores de hidrógeno dominan empíricamente— y no de qué fragmentos tiene.
- **Los fragmentos reemplazan a los descriptores en la fase 2 y no en la fase 1.** Allá el brazo `huellas` queda a 0.002 o menos del brazo ancho en cuatro modelos y lo supera en dos; aquí `descriptores+huellas` supera a `huellas` en los seis.
- **La ganancia no está donde el proyecto la necesita.** En la fase 2 la mejora amplia está en los pares que solo tiene ChEMBL; en los que solo tiene NPASS mejora un solo modelo (`knn`, +0.085 en 15 de 15) y lo deja apenas por encima del azar. En la fase 1 las huellas ayudan en los compuestos sin equivalente natural y no en los naturales exactos ni en los análogos. Dos cuadernos independientes, el mismo sesgo.
- **Depurar o seleccionar descriptores no cambia nada en ninguna fase.** La depuración quita entre el 23% y el 26% de las columnas y el Lasso más de la mitad (95 de 201 en la fase 2, 90 de 203 en la fase 1), y ninguno de los dos pierde nada medible, salvo `bayes` en la fase 1. Así que se puede prescindir de **la mitad** de los descriptores sin perder nada, y tampoco se gana por hacerlo.

**Se decide, entonces:** la fase 2 entra con huellas al Avance 5 (#155) y la fase 1 no, **por desempeño**. En la fase 1 el argumento que queda en pie es la explicabilidad, porque una columna Sort & Slice es una subestructura concreta y permite la atribución a nivel de fragmento que pide la [C.2](#dc-2), y los descriptores no; si se usan para eso se dice así —para explicar, no porque midan mejor— y se reportan los dos brazos.

**La regla con la que se leyó, y lo que no es.** Un brazo mejora a un modelo si la diferencia media contra el brazo de control supera un umbral **y** es positiva en al menos 12 de las 15 evaluaciones (3 semillas × 5 pliegues), comparando siempre la misma evaluación contra la misma. El umbral es **la mayor dispersión de la métrica entre las evaluaciones del propio control**: una diferencia menor que lo que varía el mismo modelo al cambiar de pliegue no se distingue del reparto. En la fase 2 salió 0.007 de concordancia, tomado del 04b, y el control del 04c lo confirmó (0.0072); en la fase 1 salió 0.094 de MCC y 0.058 de AUPRC, porque el MCC de esa fase varía mucho más entre pliegues. El Avance 5 llama a la suya la misma regla y aplica una variante más laxa: solo la desviación del mejor individual, 0.073 y 0.041 ([1.5](#d1-5)). Tres advertencias que acompañan a la regla:

- **No está pre-registrada.** Se fijó después de explorar un pliegue del 04b, y así lo dicen los `params` de las dos corridas. Lo que sí se cumple es que quedó escrita antes de ejecutar y no se ajustó al ver los resultados.
- **Los 12 de 15 no son una probabilidad.** Las semillas comparten filas y los pliegues parten los mismos datos, así que las 15 evaluaciones no son independientes: es una prueba de signos con esa limitación.
- **En la fase 1 resultó conservadora, y se reportó así.** El umbral se compara contra una diferencia pareada, que fluctúa bastante menos que el MCC absoluto del que sale. Por eso ahí «sin mejora medible» dice tanto de la regla como de las huellas, y la lectura del 03c publica la diferencia pareada y la cuenta de evaluaciones junto al veredicto. El umbral no se bajó al ver que nadie lo pasaba.

**¿Las huellas ayudan en la fase 2 porque su etiqueta es de un encuentro y no de la molécula entera? No: con la etiqueta por molécula siguen ayudando (4 de noviembre).** Corrida `2026-11-04-artemio-1.3-huellas-por-etiqueta-de-molecula-actividad` (`scripts/experimento_huellas_por_etiqueta_de_molecula.py`), sin tocar la prueba reservada. Se cambia **solo** la etiqueta, de «el par molécula–diana es activo a 10 µM» a «la molécula es activa contra alguna diana», con las mismas moléculas y el tamaño de datos de la fase 2 (44,174 moléculas de ajuste, 10,071 grupos, 79.1% activas) y la misma partición por `grupo_cv`. Tres brazos como el 03c y cuatro modelos baratos del catálogo de la fase 1, en 15 evaluaciones. La regla se declaró antes: la hipótesis de granularidad se contradice si al menos 3 de 4 modelos son ayudados por `descriptores+huellas` con la regla del proyecto (diferencia pareada positiva y mejor en 12 de 15, en AUROC y MCC a la vez).

| modelo | AUROC con descriptores | ΔAUROC con huellas añadidas (desv.) | mejor en | ΔMCC |
|:--|--:|:--|--:|--:|
| `arbol` | 0.6728 | +0.0172 (0.0119) | 14 de 15 | +0.0285 |
| `bayes` | 0.5865 | +0.0848 (0.0270) | 15 de 15 | +0.0974 |
| `logistica` | 0.7443 | +0.0736 (0.0110) | 15 de 15 | +0.1531 |
| `svm_sgd` | 0.7437 | +0.0452 (0.0151) | 15 de 15 | +0.1267 |

**Ayudan a los cuatro modelos, y el brazo de solo huellas queda al nivel del ancho** (+0.040 a +0.083 de AUROC contra los descriptores): el patrón de la fase 2 se repite con la etiqueta por molécula. Por la regla declarada **la granularidad de la etiqueta no explica la diferencia entre fases.** El control declarado del sesgo de la etiqueta (una molécula probada contra más dianas tiene más ocasiones de ser activa) es bajo: el AUROC de `n_pares` solo es 0.451. Dos comprobaciones independientes dan diferencia 0: reconstruir la tabla por molécula con pandas (44,174 y 0.791) y recalcular la semilla 0 de `logistica` con un ciclo de pliegues escrito aparte (AUROC 0.74377 y 0.81803, idénticos al guardado). **Límites:** son cuatro modelos y no los seis de la fase 1; las moléculas y la etiqueta siguen siendo de actividad, no de permeabilidad, así que **esto no prueba qué pasa en la fase 1**, solo que la etiqueta de un encuentro no es la causa; y queda una explicación sin medir: que la permeabilidad dependa de propiedades globales que los descriptores ya capturan, mientras la unión depende de subestructuras. Con E9 (el tamaño tampoco lo explica), quedan en pie la densidad del espacio químico (E11) y esa naturaleza de la propiedad.

**¿Las huellas ayudan en la fase 2 y no en la 1 solo porque la 2 tiene nueve veces más datos? No: el tamaño no lo explica (4 de noviembre).** Corrida `2026-11-04-artemio-1.3-huellas-por-tamano-de-datos-actividad` (`scripts/experimento_huellas_por_tamano_de_datos.py`), sin tocar la prueba reservada. Se ajusta el `aft` con y sin huellas con un submuestreo **por grupos** (`grupo_cv`) a 5,000, 10,000, 20,000 filas y completo, y se evalúa siempre sobre el pliegue completo, en las mismas 15 evaluaciones. 5,000 es el tamaño de un ajuste de la fase 1 (0.8 × 6,306 = 5,045). La regla se declaró antes: el tamaño explica la diferencia si la ganancia con 5,000 filas es ≤ 0, o menor que la mitad de la del ajuste completo y en menos de 12 de 15 evaluaciones.

| filas de ajuste | `aft` | `aft` + huellas | diferencia pareada (desviación) | huellas mejor en |
|--:|--:|--:|:--|--:|
| 5,000 | 0.6917 | 0.7022 | **+0.0105** (0.0060) | 14 de 15 |
| 10,000 | 0.7164 | 0.7278 | +0.0114 (0.0037) | 15 de 15 |
| 20,000 | 0.7392 | 0.7470 | +0.0078 (0.0034) | 15 de 15 |
| completo (≈45,000) | 0.7609 | 0.7666 | +0.0057 (0.0035) | 15 de 15 |

El control del ajuste completo reproduce la corrida de la 2.13 (0.7610 y 0.7659) dentro de 0.003, y recalcular de forma independiente la semilla 0 con 5,000 filas da diferencia 0.0. **La ganancia no desaparece al achicar los datos; si algo, es mayor con menos filas.** La ventaja de las huellas en la fase 2 no es un efecto de tener más datos. **Límites:** es una sola familia de modelos (el `aft`), y no los seis de la fase 1; 5,000 *pares* contienen menos moléculas distintas que 5,045 compuestos; y en `solo_npass` la ganancia no existe a ningún tamaño (de −0.001 a −0.014, 4 a 8 de 15). Descarta la explicación C (tamaño de datos); no separa la granularidad (A) de la densidad (B), que mide E10 y E11.

**¿La ganancia de las huellas sigue a la densidad del espacio químico, a igual peso molecular? No se puede decir: el resultado es no concluyente (4 de noviembre).** Corrida `2026-11-04-artemio-1.3-huellas-por-densidad-del-espacio-quimico` (`scripts/experimento_huellas_por_densidad.py`), sin tocar la prueba reservada. Es la última explicación en pie tras E9 (el tamaño de datos no la explica) y E10 (la granularidad de la etiqueta tampoco). La densidad de cada molécula es cuántas moléculas del ajuste con similitud de Tanimoto ≥ 0.4 hay **en otro grupo** (`grupo_cv`), y se parte en terciles **dentro de cada tramo de peso** (los cortes fijos de E6). Se mide la ganancia de añadir huellas por celda (tramo × tercil) en las mismas 15 evaluaciones: ΔAUROC con `logistica`, `svm_rbf` y `knn` en la fase 1, y Δconcordancia del `aft` en la fase 2. La regla se declaró antes: la densidad explica la ganancia si la media de D (ganancia del tercil alto − ganancia del bajo, promediada sobre los tramos) es positiva, mayor que su desviación entre evaluaciones y positiva en 12 de 15; no la explica si es ≤ 0 o positiva en menos de 8 de 15.

| | D medio | desviación | D > 0 en | veredicto por la regla |
|:--|--:|--:|--:|:--|
| fase 1, `knn` | +0.037 | 0.079 | 11 de 15 | no concluyente |
| fase 1, `svm_rbf` | +0.018 | 0.044 | 11 de 15 | no concluyente |
| fase 1, `logistica` | +0.011 | 0.067 | 7 de 15 | la densidad no la explica |
| fase 2, `aft` | +0.0025 | 0.011 | 9 de 15 | no concluyente |

**Por la regla declarada el veredicto es no concluyente en las dos fases:** en ningún caso la diferencia supera a su desviación. Dos cosas que se ven y que **no** son un resultado de la regla. (1) En la fase 1 la ganancia por tercil es de −0.037, −0.018 y −0.020 de AUROC (`knn`, `logistica`, `svm_rbf`) en el tercil menos denso, y de −0.005 a +0.013 en los otros dos, es decir, **la pérdida por añadir huellas se concentra en el tercio más disperso**, en la dirección que predice la hipótesis de densidad, pero con celdas muy ruidosas. (2) En la fase 2 el patrón no es monótono y cambia de signo entre tramos (en 350–500 Da sube de +0.0045 a +0.0142 con la densidad; en >500 Da baja de +0.0162 a +0.0043), así que no hay un efecto uniforme. La densidad media en el ajuste es de 33.8 vecinos fuera del grupo en la fase 1 y de 61.9 en la fase 2: **la fase 2 es unas 1.8 veces más densa**, un hecho descriptivo compatible con la hipótesis pero que no la prueba. Controles: la ganancia en `todos` reproduce la de E6 en las dos fases dentro de 0.003. **Verificado de forma independiente:** la densidad por la matriz densa (fase 1) y la dispersa (fase 2) coincide con `BulkTanimoto` fila por fila en 100 y 60 moléculas al azar (0 discrepancias). **Límites:** celdas pequeñas (tercios de un tramo, y el tramo ≤ 250 Da de la fase 2 tiene pocas evaluaciones); tres modelos en la fase 1 y uno en la fase 2; la densidad se mide con ECFP4 y a 0.4, y la E13 muestra que la definición de «parecido» cambia lo que se ve; y la densidad va junto con otras cosas. **No resuelve la pregunta:** quedan sin separar la densidad y que la permeabilidad dependa de propiedades globales que los descriptores ya capturan. Resolverla pide igualar las celdas por submuestreo, o más datos de la fase 1.

**Las 151 columnas de la fase 1 se eligieron una vez, con las etiquetas de entrenamiento, y la validación cruzada corre sobre entrenamiento más validación** ([#195](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/195)). Cada pliegue de evaluación contiene filas cuya etiqueta ayudó a decidir qué columnas existen. La prueba reservada no participó. Es una fuga de selección y se declara como tal. Su magnitud ya está medida, sin proponérselo, por el brazo `depurados` del 03c, que repite el filtro **dentro de cada pliegue** (`notebooks/datos/03c_brazos.csv`, estrato `todos`, diferencia pareada `depurados` − `descriptores` en 15 evaluaciones):

| métrica | media de la diferencia, rango entre los seis modelos | una evaluación suelta, rango |
|:--|:--|:--|
| MCC | de −0.0141 (`bayes`) a +0.0102 (`knn`) | de −0.107 a +0.060 |
| AUROC | de −0.0045 (`knn`) a +0.0022 (`arbol`) | de −0.033 a +0.027 |

Para el modelo que se entrega, `svm_rbf`: −0.0003 de MCC (desviación pareada 0.0100) y +0.0005 de AUROC. Ninguno de los seis cumple la regla de mejora, y el signo no es el de una ventaja del brazo sin fuga: `knn` mejora en MCC y empeora en AUROC. Contra la desviación del control (0.094 de MCC) **el sesgo no es medible**, y eso es todo lo que se afirma: no que no exista. **En consecuencia, «el brazo `descriptores` es el control» del 03c y del 05c quiere decir que repite la corrida registrada, no que esté libre de esta fuga.** No se reejecuta nada: el cierre es la declaración.


**Las huellas por tramo de peso, fase 2 (4 de noviembre).** Corrida `2026-11-03-artemio-1.3-tamano-huellas-actividad` (`scripts/experimento_tamano_fase2.py`): `aft` contra `aft_huellas`, mismas semillas, pliegues y 56,241 filas que la 2.13, concordancia de Harrell por tramo de peso con los mismos cortes fijos de la fase 1. La lectura se declaró antes: la hipótesis se sostendría si la ganancia creciera con el tramo, y si fuera plana no se sostendría.

| tramo | pares de validación por pliegue | evaluaciones | `aft` | `aft_huellas` | diferencia | mejora en |
|:--|--:|--:|--:|--:|--:|--:|
| ≤ 250 Da | 1,049 | 3 | 0.661 | 0.658 | −0.0035 | 1 de 3 |
| 250–350 Da | 2,941 | 15 | 0.723 | 0.726 | +0.0023 | 9 de 15 |
| 350–500 Da | 5,830 | 15 | 0.761 | 0.769 | +0.0085 | 15 de 15 |
| > 500 Da | 1,689 | 15 | 0.757 | 0.766 | +0.0089 | 12 de 15 |
| todos | 11,248 | 15 | 0.761 | 0.767 | +0.0057 | 15 de 15 |

- **La ganancia crece con el peso, y en la fase 1 no.** De −0.0035 a +0.0089 en la fase 2, con el orden monótono entre los cuatro tramos (los dos últimos casi iguales); en la fase 1 la misma pregunta dio una media negativa en los cuatro tramos y sin tendencia. Cumple la regla declarada, pero **las magnitudes son pequeñas** (menos de 0.01 de concordancia) y el tramo ligero solo se reporta en 3 de las 15 evaluaciones, así que su signo es la parte más débil.
- **No es solo cuántas filas hay.** El tramo > 500 Da tiene menos pares de validación que el de 250–350 (1,689 contra 2,941) y gana más con las huellas. Eso va contra la lectura de que el efecto sea sobre todo de densidad de datos, pero **no la descarta**: no se igualó el tamaño de los tramos por submuestreo, ni se controló la rareza.
- **El tramo de arriba cubre poblaciones distintas** (hasta 1,449 Da en la fase 1 y hasta 4,114 en la 2), así que el cruce de las dos fases es más sólido en los tres tramos de abajo.
- **Qué falta para sostener la hipótesis:** igualar los tramos por submuestreo y repetirlo con el control de rareza. Hasta entonces se reporta como un patrón consistente con la hipótesis de tamaño, no como su prueba.

**Las huellas por tramo de peso, fase 1 (4 de noviembre).** Corrida `2026-11-03-artemio-1.3-tamano-huellas-permeabilidad` (`scripts/experimento_tamano_fase1.py`): los seis modelos del Avance 4 sin afinar, `descriptores` contra `descriptores+huellas` (2,048 bits, vocabulario relearned dentro de cada pliegue), 3 semillas × 5 pliegues, sin tocar la prueba. La lectura se declaró antes: la hipótesis de tamaño se sostendría si la ganancia fuera mayor en los tramos pesados que en los ligeros en la mayoría de los modelos.

| tramo | n medio | diferencia media de AUROC (huellas − descriptores), 6 modelos |
|:--|--:|--:|
| ≤ 250 Da | 238 | −0.032 |
| 250–350 Da | 349 | −0.015 |
| 350–500 Da | 480 | −0.009 |
| > 500 Da | 205 | −0.019 |
| todos | 1,261 | −0.021 |

- **Las huellas no ayudan en ningún tramo de la fase 1, y no hay tendencia con el peso.** La media es negativa en los cuatro. Comparando el tramo ligero con el pesado, la ganancia sube en 3 modelos (`arbol`, `bayes`, `mlp`) y baja en 3 (`knn`, `logistica`, `svm_rbf`): no cumple la regla declarada. El `svm_rbf`, el modelo final, empeora más en el tramo pesado (−0.027) que en el ligero (−0.013).
- **La media la arrastra `bayes`** (−0.12 a −0.05 por tramo; las huellas violan su supuesto de independencia). Sin él las medias son −0.015, −0.003, −0.003 y −0.011 por tramo de menor a mayor peso: cerca de cero y sin subir con el peso.
- **Es la mitad de la pregunta.** Falta la fase 2 con el mismo diseño: la hipótesis se contrasta con el cruce de las dos. Esta pasada no iguala los tramos por submuestreo (el ligero y el pesado tienen ~200 filas y más ruido, y el ligero solo se reporta en 13 de las 15 evaluaciones), así que **no distingue tamaño de densidad de datos**. Como en la fase 1 no hay efecto que separar, la igualación importa sobre todo en la fase 2.

### Propuestas

#### 1.4 · Las 6 filas con logBB sin clase BBB {#d1-4 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Pueden completarse desde B3DB?

**Qué pasó.** Seis filas (zidovudina, miltefosina y otras cuatro) traen `logbb` pero no clase integrada. Según el diccionario sí tienen clase en B3DB, pero su fila de clasificación es de otra forma estereoquímica y no empató por estructura.

**Se propone.** Excluirlas de la clasificación y no imputar una etiqueta desde la conectividad, porque la estereoquímica puede cambiar la clase.

#### 1.5 · Tres modelos candidatos; de ahí, si escalar y si reducir dimensión {#d1-5 .vigente .revisada}

**Estado:** vigente · revisada el 12 de octubre y el 2 de noviembre

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

**El piso es 0.000 de MCC, 0.500 de AUROC y 0.350 de AUPRC sobre la minoritaria.** El tercero importa justamente porque no es cero: el 0.88 del baseline se lee contra 0.350, no contra 0. No hay desempeño histórico con el que comparar —la patrocinadora no tenía modelo previo— así que el piso lo ponen los clasificadores triviales con la misma partición agrupada. Importa decirlo porque con 65.0% de BBB+ un clasificador que diga siempre «permeable» acierta dos de cada tres veces, y esa exactitud del 65% parecería un resultado. **El desempeño mínimo que el Avance 4 tenía que superar quedó fijado en el 0.70 de MCC y el 0.93 de AUROC de este baseline**, medido con esta partición y estas semillas. Es una vara de **validación cruzada**, y por eso no es comparable con la cifra de la prueba reservada del apartado siguiente. *Versión superada (2 de noviembre):* esta entrada dejaba la frase sola, sin el resultado del Avance 5, así que quien entrara por el registro —que es el documento canónico— se llevaba 0.70 donde la cifra sobre datos no vistos es 0.3385, el doble de lo que el modelo hace (#190).

**El modelo final de la fase 1 es `svm_rbf`, y lo eligió el Avance 5 por descarte.** Ninguna de las treinta comparaciones —los otros diez modelos por tres métricas: los cinco ensambles (15), sus dos versiones afinadas (6) y los otros tres individuales (9)— contra el mejor individual pasó la regla de mejora, que se escribió antes de correr la comparación y no se bajó después, aunque no está pre-registrada: se fijó después de ver el control de los cuadernos anteriores, y el valor de su umbral sale de la propia corrida que juzga, así que el final es el mejor individual del Avance 4. La estabilidad y los intervalos solapados de AUROC apuntan al mismo modelo. Reajustado con entrenamiento y validación, y evaluado **una sola vez** sobre los 1,499 compuestos reservados (`notebooks/05_Modelo_Final.ipynb` celda 30, corrida `experimentos/2026-11-01-artemio-1.5-modelo-final-permeabilidad/`):

| | MCC | AUROC | AUPRC min. | exactitud bal. |
|:--|--:|--:|--:|--:|
| validación cruzada | 0.7017 | 0.9190 | 0.8842 | |
| **prueba reservada** | **0.3385** | **0.7928** | 0.7198 | 0.6386 |
| · natural exacto | 0.2567 | 0.7802 | 0.7613 | 0.5960 |
| · análogo estereoquímico | 0.2788 | 0.7304 | 0.5652 | 0.6537 |
| · sin equivalente natural | 0.3173 | 0.7934 | 0.5997 | 0.6249 |

Se esperaba que bajaran: la prueba tiene los andamios raros a propósito y otra prevalencia (57.3% de BBB+ contra 65.0% de las 6,306 filas con las que se reajustó). Bajan más de lo que esa advertencia prepara. El MCC se parte por la mitad, y el AUROC pierde 0.126 sin depender del umbral, así que la prevalencia no lo explica: **sobre esqueletos que no se parecen a los de entrenamiento el modelo ordena peor**. El estrato más flojo en exactitud balanceada es `natural exacto` (0.596), que es justo el que el proyecto quiere priorizar. La distancia entre las dos primeras filas **es** el resultado del Avance 5: mide cuánto de lo que promete la validación cruzada sobrevive a un esqueleto nuevo, y que sobreviva poco es un resultado válido, que es el que va al artículo. Parte de la caída del MCC es de colocación del umbral y no de orden, y recuperarla pide reportarlo a un umbral elegido en validación, que es lo que queda abierto en el #191.

**El umbral de esa regla está mal definido y mal escalado, y el veredicto no depende de él** ([#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188)). Son dos defectos distintos. La celda 12 del cuaderno definía el umbral como «la mayor desviación» mientras el código usa la desviación estándar: 0.073 de MCC y 0.041 de AUPRC, contra los 0.1298 y 0.0811 que produce el texto, y ninguno de los dos es el de la [1.3](#d1-3), que toma la mayor de las desviaciones entre los modelos del control (0.094 y 0.058). Y el umbral mide dispersión entre pliegues mientras el estadístico que juzga es una diferencia pareada, donde la dificultad del pliegue se cancela: la desviación pareada va de 0.0096 a 0.0188 de MCC, así que el umbral está entre casi cuatro y casi ocho veces inflado en las unidades de lo que mide —3.9 contra la mayor desviación pareada y 7.6 contra la menor—, y pedía más ganancia que los 0.0417 que separan al mejor de los once modelos del peor. Con cualquiera de las cuatro lecturas el veredicto es el mismo, porque la mayor ganancia observada es de 0.0093. **Se sostiene además por dos caminos que no usan el umbral:** ninguno de los dos candidatos llega a 12 de 15 evaluaciones en las dos métricas a la vez —el `stacking` 12 en MCC y 11 en AUPRC, la `votacion` 9 y 14— y los cuatro intervalos corregidos por Nadeau y Bengio como en la [1.7](#d1-7) incluyen el cero: en MCC `stacking` +0.0093 [−0.0101, +0.0287] y `votacion` +0.0075 [−0.0113, +0.0263]; en AUPRC de la minoritaria `votacion` +0.0108 [−0.0009, +0.0224] y `stacking` +0.0093 [−0.0034, +0.0221]. **Esos dos caminos alcanzan a las dos métricas principales y a nada más:** el AUROC no entra en la regla —la celda 11 del cuaderno lo llama tercera lectura— y su diferencia pareada se mide aparte, así que de aquí no se sigue nada sobre él. Lo que queda abierto en el #188 es reescribir el argumento del cuaderno para que apoye en esos dos caminos y no en el umbral, que es criterio de equipo, y mostrar la columna `dif_desv` en la tabla, que pide reejecutar la comparativa.

**Qué cambiaría la elección del modelo final:** que el umbral elegido en validación recupere buena parte del MCC de la prueba, lo que cambiaría la lectura de la caída pero no la del AUROC; o que la matriz canónica de la fase 1 quede decidida (#166) y mueva el orden de los once modelos, aunque el `svm_rbf` es uno de los cinco que salen idénticos al cuarto decimal entre las dos máquinas.

**Superado el 4 de noviembre, se deja visible: la intersección de abajo mezclaba la permutación sobre el `svm_rbf` con la impureza de un bosque, que son dos modelos distintos** (comentario de Grettel del 3 de noviembre). Con los dos métodos sobre el **mismo** `svm_rbf` —permutación y KernelSHAP, corrida `2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos`, regla escrita antes de correr— la intersección de las 15 primeras son **seis** columnas (`fr_lactam`, `NumHDonors`, `NumAliphaticCarbocycles`, `VSA_EState3`, `fr_Ar_OH`, `fr_ether`), estables entre dos muestras de compuestos explicados; `MolLogP` sale (puesto 12 y 27) y **TPSA no entra** (puesto 40 por permutación, 10 por SHAP, por su racimo de columnas redundantes). La correlación de Spearman entre los dos rankings completos es de 0.37: coinciden en la cabeza y poco en el resto. Comprobación independiente: el ranking recalculado por otra ruta da la misma intersección, y permutar `fr_lactam` a mano da 0.040 de caída de MCC contra 0.045 de la corrida. Los nombres salen de `Tarea.columnas`.

**Versión anterior.** Dos métodos de atribución coinciden en 11 de sus 15 primeras características, que es lo que la [C.2](#dc-2) exige antes de afirmar nada estructural: la impureza del bosque pone a TPSA arriba, la permutación sobre el pliegue de evaluación pone a `fr_lactam` y `fr_COO`. En la intersección están TPSA, donadores de hidrógeno y `MolLogP`, y los coeficientes de la logística les dan el signo esperado —TPSA −1.42, donadores −2.43—, de modo que la regla de los dos parámetros sale de tres caminos independientes en vez de citarse. **24 de las 151 columnas no dañan al modelo al permutarlas**, y la cuenta lleva su ruido: en solo 4 de esas 24 la media supera en magnitud a su propia desviación entre repeticiones, y en toda la matriz solo 75 de 151. El orden de la cola no está medido; el de la cabeza sí —`fr_lactam` da 0.0058 ± 0.0012— y es de donde sale la intersección. Retirarlas es candidato de poda para el Avance 4, no una decisión que una sola configuración pueda tomar.

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

**La prueba reservada por rareza (4 de noviembre; sugerencia de la reunión del 3).** Corrida `2026-11-03-artemio-1.5-prueba-por-rareza` (`scripts/experimento_prueba_rareza.py`), con **dos lecturas de la prueba**, una por fase, anotadas en `experimentos/prueba.csv` con su motivo. Se reajustaron los modelos finales con las filas de ajuste y no se tocó nada después de ver la prueba. La rareza son los **terciles de la similitud de Tanimoto al vecino más cercano del ajuste, dentro de cada tramo de peso**, para no mezclar rareza con tamaño. La línea base es una regresión logística sobre peso y TPSA en la fase 1, y un `aft` sobre peso, TPSA y diana en la fase 2. La regla se declaró antes: «lo raro explica la caída» se sostiene si la ventaja del modelo sobre su línea base es menor en el tercil más raro que en el más parecido, con el intervalo de la diferencia sin el cero.

*Control de validez.* El reajuste de la fase 1 reproduce la cifra registrada (AUROC 0.7928). **El de la fase 2 no la reproduce exactamente:** da 0.7234 de concordancia (registrada 0.7200) y 0.511 en `solo_npass` (registrada 0.530). La diferencia es del orden del ruido del reajuste de un modelo de árboles, y se reporta antes de interpretar; la cifra citable sigue siendo la registrada.

**Fase 1, AUROC de la prueba (1,499 compuestos):**

| tercil de rareza | n | similitud media | `svm_rbf` | línea base de peso y TPSA | ventaja (IC95%) |
|:--|--:|--:|--:|--:|--:|
| 1 más raro | 497 | 0.260 | 0.693 | 0.656 | +0.036 (−0.008 a +0.078) |
| 2 intermedio | 497 | 0.379 | 0.807 | 0.740 | +0.067 (0.033 a 0.104) |
| 3 más parecido | 505 | 0.599 | 0.865 | 0.760 | +0.106 (0.070 a 0.142) |

La diferencia de ventajas entre el más parecido y el más raro es **+0.069 (IC95% 0.011 a 0.124)**, sin el cero: **la regla se cumple**. En la química más rara el `svm_rbf` sabe poco más que el tamaño y la polaridad (su ventaja incluye el cero), y en la más parecida llega a 0.865, cerca de lo que se ve en validación. Esto dice que **lo raro explica buena parte de la caída de 0.919 a 0.793** y que lo hace a través de la química nueva, no del tamaño (los terciles están dentro de cada tramo). Límites: los tramos extremos son pequeños (≤ 250 Da y > 500 Da tienen unos 55–65 compuestos por tercil y la mayoría de sus celdas no llega a 20 casos minoritarios, así que no se reportan); los intervalos son por grupos de la prueba; y es una sola lectura.

**Fase 2, concordancia de la prueba (13,944 pares):**

| tercil de rareza | n | similitud media | `aft` | línea base (peso, TPSA, diana) | ventaja |
|:--|--:|--:|--:|--:|--:|
| 1 más raro | 4,633 | 0.469 | 0.663 | 0.594 | +0.069 (0.060 a 0.078) |
| 2 intermedio | 4,627 | 0.679 | 0.722 | 0.635 | +0.087 (0.079 a 0.095) |
| 3 más parecido | 4,684 | 0.811 | 0.764 | 0.678 | +0.087 (0.078 a 0.095) |

La diferencia de ventajas es **+0.018 (IC95% 0.005 a 0.030)**: la regla se cumple, pero **el efecto es unas cuatro veces menor que en la fase 1**. El `aft` conserva una ventaja clara sobre la línea base incluso en lo raro (+0.069). Del tercil más parecido al más raro el `aft` baja 0.101 y la línea base 0.084: casi toda la caída hacia lo raro es compartida con un modelo que solo ve peso, TPSA y diana.

- **En `solo_npass` la línea base le gana al `aft`** (0.565 contra 0.511 con 117 pares): para los naturales, el modelo no supera a «peso, TPSA y diana». Es la cifra más honesta del apartado y coincide con el 0.530 (Spearman 0.083) que el proyecto ya reportaba como no distinguible del azar. Con 117 pares no hay intervalo útil y no se interpreta más.
- La similitud media de la fase 2 es mayor que la de la fase 1 porque son pares y un compuesto aparece en varios.
- Límites: una lectura por fase; la línea base de la fase 2 usa la misma librería que el modelo; la rareza se midió con una sola huella (Morgan radio 2).

**¿La similitud al vecino más cercano explica por qué la prueba rinde 0.793 de AUROC? No: la prueba es más difícil de lo que su similitud predice (4 de noviembre).** Corrida `2026-11-04-artemio-1.5-dificultad-de-la-prueba-permeabilidad` (`scripts/experimento_dificultad_de_la_prueba.py`). **Es un acceso estructural a la prueba, solo SMILES, sin etiquetas ni predicciones**, anotado en `experimentos/prueba.csv` por `tomar_prueba` con su motivo: **es la séptima lectura registrada de la prueba** una vez fusionados los PR de E1+ (#231) y E2 (#236), que traen las suyas (con ellas, las seis que cuenta el esqueleto del artículo; de la fase 1 son ahora cuatro). La similitud media de la prueba al ajuste (0.414) se parece a la del peldaño de ≥ 0.6 de la escalera (0.422), pero su AUROC (0.793) es el de los peldaños de ≥ 0.5 y ≥ 0.4. La pregunta es si la **distribución completa** de esa similitud, y no su media, lo explica. Se juntan las predicciones fuera de pliegue del `svm_rbf` en cuatro agrupamientos (75,672 predicciones), cada una con la similitud al vecino más cercano de su ajuste, y se **reponderan** para que su distribución sea la de la prueba (deciles de la prueba como cubetas). La regla se declaró antes: la similitud explica el nivel si el AUROC reponderado queda a menos de 0.030 de 0.7928.

| lectura | AUROC |
|:--|--:|
| validación, sin ponderar | 0.8786 |
| validación reponderada a la similitud de la prueba (vecino más cercano) | **0.8895** |
| ídem, con el promedio de los cinco vecinos más cercanos | 0.8822 |
| prueba reservada, registrado | **0.7928** |

**Por la regla declarada, la similitud al vecino no basta:** reponderar sube el AUROC esperado, porque la prueba no es más lejana que la validación agrupada (similitud media 0.414 contra 0.384), y deja una brecha de **0.097** (0.089 con cinco vecinos) que esa medida no ve. **La prueba es difícil por algo distinto de qué tan lejos queda de lo visto.** Lo que esta corrida no dice: qué es. Candidatos sin medir, todos sobre la prueba y por eso fuera de lo que esta corrida puede hacer sin etiquetas: la prevalencia de BBB+ (el ajuste tiene 65%), el peso molecular y la polaridad, la curación distinta de los datos, y que la prueba contenga los andamios raros a propósito. **Verificado de forma independiente:** con el vecino más cercano por la matriz densa (y no por el producto de matrices), cubetas por cuartiles de la prueba (y no deciles) y un AUROC ponderado escrito a mano, la validación sin ponderar da 0.8786 (idéntico) y la reponderada 0.8876 (0.8895 con deciles): la conclusión no depende de la discretización. Además la media (0.4139) y la mediana (0.3721) de la similitud de la prueba coinciden con las de la corrida E1+ (`…escalera-ampliada-permeabilidad`), calculadas con otro código. **Límites:** una sola familia de modelos (el `svm_rbf`), una definición de parecido (ECFP4; la E13 muestra que importa) y un solo vecino o cinco; ponderar por cubetas supone que la dificultad depende solo de la similitud dentro de cada cubeta.

**¿Cuánto de lo que llamamos «ruido» es la semilla del modelo? Para cuatro de los seis modelos, nada; para dos, tanto como la mitad de la dispersión entre modelos (4 de noviembre).** Corrida `2026-11-04-artemio-1.5-semilla-del-modelo-permeabilidad` (`scripts/experimento_semilla_del_modelo.py`), sin tocar la prueba reservada. El arnés lo dice en su propio código: las semillas cambian el reparto en pliegues y **no el modelo**, así que los intervalos del proyecto no incluyen esta fuente. Aquí, con la partición fija (3 semillas × 5 pliegues), se ajusta cada uno de los seis modelos de la escalera con cinco semillas de modelo y se mide, en cada evaluación, la desviación del MCC entre ellas. La regla se declaró antes: la semilla del modelo importa si esa desviación es de al menos 0.005 de MCC, del orden de la menor desviación pareada con la que se ha leído una diferencia (0.0054).

| modelo | desviación del MCC entre semillas de modelo | máximo en una evaluación | desviación del AUROC | ¿importa? |
|:--|--:|--:|--:|:--|
| `svm_rbf`, `logistica`, `knn`, `boosting` | **0.0000** | 0.0000 | 0.0000 | no: deterministas |
| `bosque` | 0.0074 | 0.0196 | 0.0012 | **sí** |
| `mlp` | 0.0173 | 0.0264 | 0.0062 | **sí** |

**Consecuencias.** (1) Cuatro modelos, incluido el que se entrega, dan exactamente la misma predicción con cualquier semilla: para ellos los intervalos del proyecto no omiten nada. (2) Para el `mlp` y el `bosque` sí: **en el mismo pliegue, el `mlp` pasa de 0.7206 a 0.6820 de MCC cambiando solo la semilla** (0.039, casi la dispersión de 4.2 puntos entre los once modelos de la comparativa), así que cualquier comparación de esos dos modelos con diferencias menores a unos 0.02 de MCC se lee como empate, y sus desviaciones de 15 evaluaciones no son un error estándar completo. (3) En AUROC el efecto es mucho menor (0.006 y 0.001). **Verificado de forma independiente:** recalculé el pliegue 1 de la semilla 0 con el `mlp` y semillas de modelo 0 y 3, y los MCC coinciden al sexto decimal con los guardados (0.720588 y 0.681985); y el `svm_rbf` con semillas 0 y 4 da probabilidades idénticas (diferencia máxima 0.0). **Límites:** la comparación solo cubre la fase 1 y los seis modelos de la escalera; no se midió la fase 2 (el `aft` fija `random_state` y no usa muestreo de filas, pero no se verificó).

**¿Importa que la calibración interna del `svm_rbf` no agrupe? No se distingue de ruido (4 de noviembre).** Corrida `2026-11-04-artemio-1.5-calibracion-svm-agrupada-permeabilidad` (`scripts/experimento_calibracion_svm.py`), sin tocar la prueba reservada ([#191](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/191)). `CalibratedClassifierCV(SVC, ensemble=False)` ajusta Platt con cinco pliegues internos al azar, la única partición interna del proyecto que no agrupa. Se comparó, con las mismas 15 evaluaciones agrupadas, esa calibración contra una con `StratifiedGroupKFold` sobre los grupos de las filas de ajuste. La regla se declaró antes de correr: efecto distinto de ruido si la diferencia pareada media de MCC supera su desviación pareada **y** el signo se cumple en 12 de 15.

| | sin agrupar (`main`) | agrupada | diferencia pareada |
|:--|--:|--:|:--|
| AUROC | 0.9190 | 0.9190 | 0 exacto, como debe ser: Platt es monótona |
| AUPRC de la minoritaria | 0.8842 | 0.8842 | 0 exacto |
| MCC | 0.7017 | 0.7004 | −0.0012, desviación 0.0054, mejor en 6 de 15 y peor en 8 |
| exactitud balanceada | 0.8344 | 0.8324 | −0.0020, desviación 0.0029, mejor en 5 de 15 y peor en 9 |

El control del catálogo reproduce el brazo «sin agrupar» al decimal en cada evaluación, así que la comparación mide solo la partición. **El efecto está dentro de la dispersión y, si algo, agrupar no mejora el MCC.** Por lo tanto la cifra publicada del `svm_rbf` no cambia y la calibración se queda como está, con la excepción declarada aquí. El sesgo que el #191 anticipaba en contra del modelo no aparece. Lo que sí se ve es otra cosa: a 0.5 el modelo declara BBB+ al 70.9% de las filas (71.3% con la agrupada) cuando la prevalencia real es 64.97%, es decir, el punto de operación fijo sobrepredice la mayoritaria con cualquiera de las dos calibraciones; es la lectura que el #191 pedía hacer sobre la caída del MCC en la prueba, y no está medida aquí. **Queda abierto del #191** revisar qué corrigió de verdad el #118, porque la declaración de uso de IA del Avance 4 dice que la calibración se agrupó y el código no lo hace.

**¿Importa que el escalador del `svm_rbf` quede fuera de la calibración? No se distingue de ruido, y es lo correcto ponerlo dentro (4 de noviembre, comentario de Grettel del 3 de noviembre).** Corrida `2026-11-04-artemio-1.5-escalador-dentro-del-svm-permeabilidad` (`scripts/experimento_escalador_dentro_del_svm.py`), sin tocar la prueba reservada. `svm_rbf` es `Pipeline([MinMaxScaler, CalibratedClassifierCV(SVC, ensemble=False)])`: el escalador se ajusta con todas las filas de ajuste antes de que la calibración parta en cinco pliegues internos, así que los mínimos y máximos usan también las filas con las que Platt se calibra. Se comparó, con las mismas 15 evaluaciones agrupadas, contra `CalibratedClassifierCV(Pipeline([MinMaxScaler, SVC]))`, donde cada pliegue interno escala solo con su entrenamiento. La regla se declaró antes: el cambio importa si la diferencia pareada de MCC supera su desviación y el signo se cumple en 12 de 15.

| | `fuera` (el entregado) | `dentro` | diferencia pareada (desviación) |
|:--|--:|--:|:--|
| MCC | 0.7017 | 0.7015 | −0.0001 (0.0013); 3 a favor, 3 en contra, el resto idéntico |
| AUROC | 0.9190 | 0.9190 | **0 exacto** |
| AUPRC de la minoritaria | 0.8842 | 0.8842 | **0 exacto** |
| exactitud balanceada | | | +0.0001 (0.0006) |

El control pasa (0.7017 y 0.9190). **No se distingue de ruido.** Por qué el AUROC y el AUPRC son idénticos: con `ensemble=False` el SVC final se ajusta con **todas** las filas de ajuste y el mismo escalado en los dos brazos (verificado: mismos mínimos y máximos), y solo cambia la calibración de Platt, que es monótona. La diferencia máxima de probabilidad entre los dos brazos en un pliegue es 0.0019 y el orden es el mismo (Spearman 1.0). **La observación de Grettel es correcta en la forma** (el escalador veía las filas con que se calibra) **y su efecto es despreciable.** **Recomendación: adoptar la forma correcta** aunque no cambie la cifra, porque no cuesta nada y cierra la objeción; cambiarla toca `src/models/alternativos.py`, el cuaderno 04 y el 05 (que muestran ese código) y regenera `models/finales/`, así que es decisión del equipo. **Límites:** una sola familia (el `svm_rbf`); el escalado interno tampoco afecta a los modelos finales entregados, cuyo SVC se ajusta con todo.

**¿Algún ensamble supera al `svm_rbf` en AUROC, con la diferencia pareada y su intervalo? Dos lo hacen sin corregir por comparaciones múltiples, y ninguno con la corrección (4 de noviembre, comentario de Grettel del 3 de noviembre).** Corrida `2026-11-04-artemio-1.7-auroc-pareado-ensambles-permeabilidad` (`scripts/experimento_auroc_pareado_ensambles.py`), sin entrenar nada ni tocar la prueba reservada: lee el `pliegues.csv` de la corrida de los ensambles. Grettel señaló que el traslape de intervalos individuales no prueba que no haya diferencia y que hay que estimar **la diferencia de AUROC con su intervalo**; el 05 lo hacía para MCC y AUPRC (con la corrección de Nadeau y Bengio de la [1.7](#d1-7)) y no para el AUROC, que decidió «no decide». Para los diez modelos distintos del individual, en las mismas 15 evaluaciones: diferencia pareada, y su IC del 95% corregido (error × √(1/15 + 1/4), t de 14 grados de libertad). La regla se declaró antes: supera si el límite inferior del IC es mayor que 0. **El control pasa:** la misma implementación reproduce los intervalos de MCC que publica el #188 para `stacking` (+0.0093 [−0.0101, +0.0287]) y `votacion` (+0.0075 [−0.0113, +0.0263]).

| modelo | ΔAUROC contra `svm_rbf` | IC95% corregido | gana en | p (Nadeau–Bengio) | p con Holm (10 comparaciones) |
|:--|--:|:--|--:|--:|--:|
| `votacion` | +0.0139 | [+0.0038, +0.0239] | 15 de 15 | 0.010 | 0.103 |
| `stacking` | +0.0128 | [+0.0023, +0.0233] | 14 de 15 | 0.020 | 0.180 |
| `bosque` | +0.0138 | [−0.0011, +0.0288] | 14 de 15 | 0.067 | 0.535 |
| `bosque afinado` | +0.0135 | [−0.0012, +0.0283] | 15 de 15 | 0.069 | 0.535 |
| `boosting afinado` | +0.0103 | [−0.0022, +0.0229] | 12 de 15 | 0.100 | 0.599 |
| `boosting` | +0.0112 | [−0.0042, +0.0265] | 12 de 15 | 0.141 | 0.707 |
| `bagging_svm` | +0.0022 | [−0.0010, +0.0054] | 11 de 15 | 0.155 | 0.707 |
| `mlp`, `logistica`, `knn` | −0.0080 a −0.0049 | todos incluyen el cero | 3 a 7 de 15 | 0.25 a 0.56 | 0.75 |

**Lo que cambia, y es una corrección a lo que decíamos.** Por la regla declarada, `stacking` y `votacion` **sí superan al individual en AUROC**: su IC excluye el cero. La afirmación «ningún ensamble mejora de forma distinguible al mejor individual» **valía para MCC y AUPRC, no para el AUROC**, y el 05 la extendía por no tener un umbral para el AUROC. Dos matices que impiden convertirlo en una ventaja: (1) las magnitudes son de **1.3 y 1.4 puntos de AUROC** y, en las métricas de decisión (MCC y AUPRC), el mismo par no pasa; (2) son **diez comparaciones sin corregir**: con la de Holm, los valores p suben a 0.10 y 0.18 y **ninguno sobrevive**. La lectura honesta es: *hay una señal consistente de que los ensambles ordenan un poco mejor (los de bosque ganan en 14 o 15 de las 15 evaluaciones), que la corrección conservadora por pliegues compartidos no alcanza a separar del ruido una vez que se cuentan las diez comparaciones.* La elección del `svm_rbf` por MCC y AUPRC no cambia, pero el artículo y el 05 **no deben decir que ningún ensamble mejora en nada**. **Verificado de forma independiente:** los valores p se recalcularon por otra ruta (pivote de pandas y t explícita), coinciden con los intervalos, y la prueba de Wilcoxon (que ignora la dependencia entre pliegues y por eso no se usa para decidir) da valores mucho menores, el síntoma de por qué hace falta la corrección. **Límites:** una sola semilla de modelo; los pliegues comparten datos de entrenamiento (de ahí la corrección); el `mlp` y el `bosque` varían con la semilla del modelo (E16).

**Con qué filas se sirven los modelos finales, y cómo se entregan (4 de noviembre).** Decisión del equipo, tomada tras la curva de aprendizaje (`2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales`): **los dos modelos se sirven con las filas de ajuste y no con las de validación**. En la fase 1 la ganancia de usar el 100% sobre el 75% de las filas es +0.002 de AUROC (meseta), así que no hay nada que ganar; en la fase 2 sigue subiendo (+0.0076 de concordancia, 15 de 15) y **se renuncia a esa ganancia** a cambio de poder evaluar el modelo servido y repetir la cifra registrada (la prueba nunca entra). **Se entregan en `models/finales/` y se usan desde `notebooks/06_Uso_de_los_modelos.ipynb`, sin servicio** (reunión del 3 de noviembre). Corrida `…-entrenar-modelos-finales` (`scripts/entrenar_finales.py`): 6,306 filas en la fase 1 y 56,241 en la fase 2, los artefactos pesan unos 3 MB y van en git normal. **Verificado de forma independiente:** los descriptores que `src/inferencia.py` calcula desde un SMILES coinciden bit a bit con los de entrenamiento en 150 moléculas de cada fase (diferencia 0.0; las dos columnas `regla_2p` y `tpsa_por_mw` de la fase 1 son derivadas y se reproducen con su fórmula), y el modelo recargado desde disco reproduce al entrenado en memoria (diferencia 0.0). **Límites:** el `joblib` depende de la versión de scikit-learn; una predicción sobre un par (compuesto, diana) que nunca se midió es una extrapolación; y el cuaderno entrega la probabilidad sin corte porque a 0.5 el modelo cambia de sesgo bajo un cambio de distribución (E15).

**Octava lectura de la prueba: la caída contra la similitud, por origen** (4 de noviembre, corrida `2026-11-04-artemio-1.5-octava-lectura-origen-similitud`; pregunta 6.3 de Grettel). Aclaración: el AUROC de la prueba **por origen** ya estaba registrado desde la corrida del modelo final (natural exacto 0.780, análogo estereoquímico 0.730, sin equivalente natural 0.793, global 0.793), así que esa parte no requería lectura nueva; lo que se leyó es el cruce con la similitud de cada compuesto de prueba al ajuste, que pide las etiquetas. Regla escrita y commiteada antes de correr; el control reproduce el AUROC global (0.7928) y el MCC (0.3385) registrados. Terciles de similitud con cortes fijos sobre toda la prueba (0.308 y 0.459).

| AUROC por tercil de similitud | menos parecido | medio | más parecido | más − menos, IC95% (esqueletos) |
|:--|--:|--:|--:|:--|
| todos (1,499) | 0.697 | 0.793 | 0.875 | **+0.178** [+0.119, +0.238] |
| sin equivalente natural (818) | 0.679 | 0.774 | 0.902 | **+0.223** [+0.142, +0.306] |
| natural exacto (446) | 0.737 | 0.765 | 0.823 | +0.086 [−0.029, +0.204] |
| análogo estereoquímico (235) | 0.600 | 0.714 | — | no reportable |

- **La caída sí baja con la similitud**, en el agregado y en los compuestos sin equivalente natural, con el IC excluyendo el cero. **En los naturales exactos el sentido es el mismo pero el intervalo incluye el cero**, así que con 446 compuestos no se distingue; y en los análogos el tercil más parecido tiene menos de 20 casos de la minoritaria, por lo que su diferencia no se reporta (el intervalo que el script imprime para ese origen sale de las réplicas donde sí hay 20 casos, está sesgado y no se usa).
- **Lo que esto no dice:** es una correlación dentro de la prueba, no que la similitud cause la caída; en E14 la similitud pronosticaba un AUROC de 0.89 y el real fue 0.79, así que la similitud no explica toda la brecha.
- **Verificado dos veces:** el control de arriba, y un cálculo independiente (similitud con RDKit `BulkTanimotoSimilarity` y AUROC por Mann-Whitney) que da los mismos cortes y los mismos AUROC por tercil. Esa verificación **también leyó la prueba** y por eso dejó su propia línea en `experimentos/prueba.csv`.

**Modelos finales regenerados con el escalador dentro del SVM** (4 de noviembre, corrida `…-entrenar-modelos-finales-escalador-dentro`; consecuencia de adoptar #267, cuyo efecto medido en E17 es nulo). Solo cambia el de la fase 1: el `aft`, las huellas y la fase 2 salen idénticos byte a byte. Las 25 predicciones de referencia de `meta.json` cambian en la fase 1 hasta 0.00065 de probabilidad y mantienen la misma clase a 0.5. El cuaderno 06, ejecutado de nuevo en una copia, cambia tres cifras de probabilidad en la tercera cifra decimal (resveratrol 0.182 a 0.181, curcumina 0.184 a 0.183, metano 0.914 a 0.915). **Versión anterior:** el escalador fuera de la calibración, el que entregaba el commit anterior.

**Medición · andamios de la prueba reservada** (4 nov, corrida `2026-11-04-artemio-1.6-andamios-de-la-prueba`). Pregunta del comentario de Grettel del 3 de noviembre: qué proporción de la prueba tiene andamio o esqueleto que el entrenamiento no vio. Regla escrita y commiteada antes de correr; solo columnas estructurales, sin etiquetas.

- **Resultado:** la proporción es **1.000** en las dos fases, por andamio y por esqueleto, también en validación y en naturales y no naturales. Es consecuencia del agrupamiento (el reparto separa por andamio y esqueleto a la vez), no una propiedad medida del modelo: confirma que el reparto se cumple, pero **no dice qué tan lejos queda la prueba del entrenamiento**, que es lo que miden la escalera de similitud y el vecino más cercano.
- **Lo que sí aporta:** la prueba es de estructuras sueltas. Fase 1: 1,499 filas en 1,390 andamios (1,392 esqueletos). Fase 2: 13,973 filas con 13,973 esqueletos y 13,973 andamios distintos, es decir, ninguno se repite, frente a 49,425 filas con 40,047 esqueletos y 6,344 andamios en entrenamiento. En la fase 2 las filas de la prueba son independientes entre sí por andamio; en entrenamiento hay andamios con muchos pares.
- **Las 29 filas de diferencia, resueltas:** el parquet tiene 13,973 pares de prueba y el 05b cita 13,944 porque el 05b descarta los pares sin información en el intervalo (límite inferior −∞ y superior +∞) o con el intervalo invertido. Aplicado el mismo filtro del 05b al parquet salen 29 pares de prueba, 170 de ajuste (145 de entrenamiento y 25 de validación) y quedan 13,944, 56,241 y 70,185 en total, que son exactamente las cifras del 05b. Las cifras de estructuras sueltas de arriba (13,973) son del parquet sin ese filtro.
- **Registro:** dos líneas nuevas en `experimentos/prueba.csv` (una por fase), sin etiquetas.

**¿Faltan datos? La curva de aprendizaje de los dos modelos finales (4 de noviembre).** Corrida `2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales` (`scripts/experimento_curva_aprendizaje.py`), sin tocar la prueba reservada. Para cada pliegue agrupado (3 semillas × 5) el modelo final de cada fase se ajusta con el 25, 50, 75 y 100% de los **grupos** del pliegue de ajuste y se mide siempre sobre el mismo pliegue de validación. La regla se declaró antes: *faltan datos* si la ganancia del último escalón (75% → 100%) es positiva en al menos 12 de 15 evaluaciones y supera 0.005. Sirve para decidir con qué filas se entrena el modelo que se entrega a la patrocinadora, sin que cuente el deseo de subir una cifra.

| fase y métrica | 25% | 50% | 75% | 100% | ganancia 75 → 100% | positiva en | proyección con las filas de prueba | ¿faltan datos? |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| fase 1, AUROC (`svm_rbf`) | 0.894 | 0.910 | 0.917 | 0.919 | +0.002 | 8 de 15 | +0.004 | **no** |
| fase 1, MCC | 0.641 | 0.684 | 0.696 | 0.702 | +0.005 | 10 de 15 | +0.010 | **no** |
| fase 2, concordancia (`aft`) | 0.719 | 0.742 | 0.753 | 0.761 | +0.0076 | 15 de 15 | +0.007 | **sí** |

- **La fase 1 está en meseta:** del 75% al 100% el AUROC apenas se mueve y no de forma consistente. La proyección de añadir las 1,499 filas de la prueba es de +0.004 de AUROC, menos que el ruido (desviación de la ganancia: 0.007). **No hay evidencia de que más filas mejoren el modelo de la fase 1**, así que el modelo servido se entrena con las filas de ajuste, el que se evaluó.
- **La fase 2 sigue subiendo:** la ganancia del último escalón es positiva en las 15 evaluaciones (+0.0076, con desviación de 0.0026). La proyección de añadir los 13,944 pares de prueba es de +0.007 de concordancia. Aquí sí hay un argumento para entrenar el servido con todas las filas, **a cambio de que ese modelo ya no se pueda evaluar**: sus cifras serían las del modelo de ajuste, rotuladas, y no se cita ninguna métrica del servido.
- **La proyección es un ajuste `a + b·ln(n)` sobre cuatro puntos, no una medición.** Además la prueba contiene los andamios raros a propósito, así que sus filas pueden aportar más o menos que filas parecidas a las de ajuste; la curva no lo mide. La decisión final sobre la fase 2 queda en manos del equipo, con esta evidencia a la vista.

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

**4. El corte de 0.5 mezcla discriminación, calibración y prevalencia.** Por eso, para comparar estratos con prevalencias de 0.12 a 0.90, la medida primaria es el AUROC y el MCC va al lado, no en su lugar. Aquí el AUROC se usa como medida primaria porque no depende de la prevalencia; la regla general del proyecto ([C.1](#dc-1)) sigue siendo MCC y AUPRC de la clase minoritaria, que miden el desempeño sobre la clase minoritaria. **Esa clase no es siempre BBB− dentro de un estrato** ([#187](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/187)): el arnés la decidía por pliegue, y en natural exacto las cifras por estrato publicadas promedian las dos clases (BBB− en 12 de 15 evaluaciones, BBB+ en 3), en análogo estereoquímico igual (BBB+ en 12 de 15). Desde el arreglo la clase se fija con todo el estrato y la tabla trae la columna `clase_medida`; las cifras de AUPRC por estrato anteriores quedan **superadas, no recalculadas**. Las comparaciones pareadas entre modelos no cambian, porque ambos brazos volteaban juntos.

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

#### 1.10 · Entrenar dando más peso a la química rara {#d1-10 .propuesta}

**Estado:** propuesta

> **Pregunta:** ¿Entrenar con más peso en las filas de química rara (poco parecidas al resto del ajuste) mejora al `svm_rbf` en lo raro sin empeorarlo en lo parecido? Se mide solo en validación agrupada; la prueba reservada no se lee.

**Qué pasó.** La prueba cae de 0.919 a 0.793 de AUROC y la corrida `2026-11-03-artemio-1.5-prueba-por-rareza` mostró que lo raro explica buena parte de esa caída: en el tercil más raro la ventaja del `svm_rbf` sobre peso y TPSA es +0.036 con el cero dentro del intervalo, y en el más parecido es +0.106. La escalera de agrupación mostró la misma palanca desde el otro lado: con pliegues al azar el MCC es 0.752, con `grupos_cv` 0.702 y con similitud ≥ 0.4 entre ajuste y validación 0.419 (corrida `2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`). Tener análogos cercanos en el entrenamiento mueve más la cifra que cambiar de modelo. Lo que nadie midió es entrenar *a propósito* con más peso en lo raro: la curva de aprendizaje (corrida `2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales`) añade filas en general y dice en sus propios límites que no mide si las filas raras aportan más o menos que las parecidas.

**Qué se propone medir (nada se ha corrido).**

| pieza | diseño |
|:--|:--|
| modelo y datos | `svm_rbf` de la fase 1 con los 151 descriptores, como se entrega; solo la fase 1 |
| rareza de una fila de ajuste | Tanimoto al vecino más cercano **dentro del pliegue de ajuste, excluyendo las filas de su mismo grupo** (`grupos_cv`): si no se excluyen, sus estereoisómeros y compañeros de andamio la hacen parecer común. Terciles dentro de cada tramo de peso, como en la corrida de prueba por rareza |
| brazo A | sin cambios (referencia) |
| brazo B | peso por fila 1, 2 y 3 en los terciles de más parecido, intermedio y más raro, vía `sample_weight`, calculado dentro del pliegue |
| brazo C | las mismas proporciones pero duplicando filas (×1, ×2, ×3) en lugar de pesarlas, para ver si el efecto depende del mecanismo |
| brazo D | **control**: los mismos pesos 1, 2 y 3 asignados al azar, sin relación con la rareza |
| evaluación | validación cruzada agrupada, 3 semillas × 5 pliegues, pareada contra A; la prueba reservada **no se lee** |
| qué se reporta | AUROC y MCC global y por tercil de rareza de la validación (misma definición que la corrida de prueba por rareza); un tercil solo se reporta si su clase minoritaria llega a 20 casos |
| error | Nadeau y Bengio, como en la [1.7](#d1-7) |

Los pesos 1, 2 y 3 son fijos y se declaran aquí: no se afinan, porque afinarlos favorecería al brazo con más intentos.

**La regla, declarada antes de correr.** El brazo B *sirve* si se cumplen las tres:
1. la ganancia de AUROC contra A en el tercil más raro es positiva en al menos 12 de las 15 evaluaciones y su media supera 0.005;
2. en el tercil más parecido la media no pierde más de 0.005 y la pérdida no pasa de 0.010 en más de 3 de las 15 evaluaciones;
3. en el tercil más raro, B supera a D por una media mayor que cero (el control: cualquier cambio de pesos mueve algo).

**El intercambio se acepta a propósito.** El 0.005 aparece con dos papeles: lo que B debe ganar donde es raro y lo que se le permite perder donde es parecido. Como los terciles son casi del mismo tamaño (2,072, 2,109 y 2,125 filas), la regla puede declarar «sirve» con una ganancia neta cercana a cero. Se acepta, porque la prueba reservada es química rara y es ahí donde se quiere mejorar; contra la desviación nula pareada del `svm_rbf` (0.0006, medida en el #280) ese 0.005 es unas ocho desviaciones de ruido de la intervención nula, es decir, un permiso de pérdida real. Eso es una afirmación sobre el ruido y no sobre la potencia: la dispersión que la corrida encontró en el tercil más raro fue 0.0095, unas dieciséis veces la del nulo global (ver el resultado). Por eso el AUROC y el MCC globales se reportan aunque no entren en la regla, y el tercil intermedio, que recibe peso 2, se reporta sin criterio. Quien lea un «sirve» con el global plano o a la baja debe leerlo como este intercambio y no como una mejora general.

**La peor forma admisible.** Con la media en −0.005 y el recuento en 3, lo peor que la regla 2 deja pasar son tres evaluaciones perdiendo 0.025 cada una y las otras doce planas.

**Los umbrales se eligieron contra el `svm_rbf` y no se heredan.** La escala se midió donde toca, en subgrupos del tamaño de un tercil, con la intervención que no hace nada del #280: en `sin equivalente natural` (524 filas de media) y `natural exacto` (584) la desviación pareada es de 0.0008 y 0.0007, y la peor pérdida de una evaluación suelta es −0.0017, sin ninguna de 15 por encima de 0.010. El 0.010 es unas seis veces esa peor pérdida, así que no se dispara por azar. El 3 se deja en 3 porque aquí los terciles se recalculan dentro de cada pliegue y una fila puede cambiar de tercil, lo que añade una varianza que esa tabla no contiene. Con el `mlp` y la misma intervención nula la escala es otra: desviación de 0.0129 y 3 de 15 evaluaciones con pérdida mayor que 0.010 en `análogo estereoquímico`, y 0.0302 con 3 de 15 y peor pérdida −0.0518 en `sin equivalente natural`; ahí el recuento quedaría en su límite con ruido puro. Ni el 0.005 ni el 0.010 se trasladan a otro modelo sin medir su ruido.

Si no se cumple, la entrada queda como resultado negativo medido y no se afina nada para rescatarlo. El brazo C solo se reporta como contraste del mecanismo y no decide.

**Lo que no hace.** No toca la prueba reservada. Si B sirve, adoptarlo en el modelo entregado es **otra decisión**, con su propia lectura registrada en `experimentos/prueba.csv` y con su motivo. Tampoco incluye la fase 2: el `aft` con huellas se mide en horas y su respuesta ha sido distinta de la de la fase 1 en cada experimento anterior, así que solo se haría si la fase 1 muestra algo y hay margen de revisión.

**Qué costaría equivocarse.** Si los pesos distorsionan la calibración, el AUROC puede subir y el MCC bajar; por eso se reportan los dos. Si la rareza por tramo de peso resulta correlacionada con la clase, B podría premiar un atajo; el control D y el reporte por tercil lo acotan, pero no lo eliminan.

**Qué lo cambiaría.** Que la regla se cumpla (se abre la propuesta de adoptarlo) o que no se cumpla (queda como resultado negativo y como el límite declarado de la corrida `2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales`).

**Decide sin esperar a la patrocinadora.** Es una medición interna, reversible y sin datos nuevos.

**Resultado (7 de noviembre): B no sirve; la regla falla en la 1.** Corrida `2026-11-07-artemio-1.10-rareza-en-el-entrenamiento-permeabilidad` (`scripts/experimento_rareza_en_entrenamiento.py`), con el script y la regla en git antes de correr y sin tocar la prueba reservada. Las dos comprobaciones previas pasan: el brazo A reproduce al `svm_rbf` del catálogo con diferencia de MCC de 0 en las 15 evaluaciones, y los tres terciles de validación miden 407 a 434 filas, con 115 a 179 casos de la minoritaria (todas las celdas pasan el mínimo de 20).

| AUROC, diferencia pareada contra A | tercil más raro | intermedio | más parecido | global |
|:--|--:|--:|--:|--:|
| B (pesos 3, 2, 1) | −0.0005 (desv. 0.0095), mejor en 9 de 15 | +0.0022, 9 de 15 | +0.0041, 11 de 15 | +0.0022, 12 de 15 |
| D (los mismos pesos al azar) | −0.0009, 10 de 15 | | +0.0034, 9 de 15 | |
| C (duplicando filas) | −0.0004, 9 de 15 | | +0.0041, 11 de 15 | |

- **Regla 1, no se cumple:** la ganancia en el tercil más raro es −0.0005, no más de 0.005, y positiva en 9 de 15 y no en 12. **Regla 2, se cumple** (media +0.0041; ninguna pérdida mayor que 0.010). **Regla 3, se cumple de forma vacía:** B supera a D por +0.0004, que es cero dentro de una desviación de 0.0069.
- **Lo que se ve, y no es un resultado de la regla.** (1) Cualquier cambio de pesos mueve lo mismo: B y D dan +0.0022 y +0.0015 de AUROC global y tienen el mismo patrón por tercil, así que lo que B hace no se distingue de lo que hace barajar los pesos. (2) Si algo, la ganancia va al revés de lo esperado: en el más parecido (+0.0041) y no en el más raro (−0.0005). (3) El MCC global baja −0.0022 (mejor en 6 de 15, con 4 evaluaciones por debajo de −0.010; en el tercil más raro −0.0083), el costo en el punto fijo de 0.5 que la entrada anticipaba. (4) `C` y `B` coinciden en el AUROC global (+0.0022 los dos, desviación 0.0049 y peor −0.0071 los dos) y en el tercil más raro difieren en una unidad del cuarto decimal (−0.0005 contra −0.0004): el mecanismo no importa. Como `C` duplica filas y no pasa por el enrutamiento de metadatos, que coincida con `B` es prueba independiente de que el peso llegó al `SVC`.
- **Qué queda dicho.** En el `svm_rbf` de la fase 1 y con pesos 3, 2 y 1, entrenar dando más peso a lo raro no mejora lo raro. El límite del que partía la propuesta (la curva de aprendizaje no mide si las filas raras aportan más) sigue en pie como pregunta, pero esta medición la responde en un sentido: no en esa forma. **No se adopta nada, no se afinan los pesos y la prueba reservada no se lee.** Límites: un solo modelo, una sola terna de pesos, y lo raro se midió con Tanimoto de Morgan a 2048 bits, cuya definición de «parecido» ya se vio que cambia lo que se ve (corrida `2026-11-04-artemio-1.2-escalera-definicion-de-parecido-permeabilidad`).
- **Qué dice y qué no dice el negativo: la potencia de la regla.** La desviación pareada observada en el tercil más raro (0.0095) es mucho mayor que la del nulo con que se pensó el 0.005, y parte es el tamaño del subgrupo pero la mayor parte es que repesar tiene un efecto heterogéneo entre pliegues, algo que no se podía saber antes de correr. Simulando la regla con esa dispersión (40,000 sorteos de 15 evaluaciones; la revisión lo calculó y se reprodujo): con efecto real 0 la regla 1 pasa el 0.8% de las veces (excelente contra un falso positivo), con 0.005 el 26.6%, con 0.0073 el 55.4%, con 0.010 el 83.2% y con 0.012 el 93.8%. Para 80% de potencia hace falta un efecto de unos 0.0096, el doble del umbral declarado, y la condición que aprieta es el 12 de 15 y no la media. **Por eso lo que el negativo establece es «no hay un efecto de unos 0.010 o más en el tercil más raro», y no «no hay un efecto de 0.005».** Cualquier cita de este resultado debe llevar esa frase. Para la próxima regla declarada de antemano: el umbral se fija contra la dispersión de la intervención, no contra la del nulo, que solo acota el falso positivo.
- **Detalles de la corrida.** El nivel de A (AUROC 0.9190, MCC 0.7015) difiere en 0.0002 de MCC del 0.7017 de la [1.5](#d1-5) porque el escalador pasó dentro de la calibración; esta entrada solo reporta diferencias pareadas, pero quien cite el nivel de A debe saberlo. El control D se siembra con la semilla del modelo, así que arranca igual en los 5 pliegues de una semilla: son 15 sorteos distintos pero 3 semillas independientes.
- **Lectura revisada** por quien no la corrió: recalculó el veredicto desde `metricas.json`, comprobó que la rareza se calcula dentro del pliegue (en el ajuste excluyendo el grupo, en la validación sin excluirlo porque el grupo ya no está) y que la partición de la lectura por tercil es exactamente la del arnés.

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

El desarrollo por medición y por par está en [la página de variables objetivo](variable-objetivo-fase2.md); las cifras se recalculan con `scripts/cifras_fase2.py` y `scripts/cifras_etiqueta_fase2.py`.

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
- **El «cero andamios cruzan» vale para la columna con la que se partió, no para el andamio recalculado.** `tabla_de_pares` guarda `andamio=("andamio", "first")` y `smiles=("smiles_raw", mode)`, así que el andamio es el de la primera medición del par y el SMILES el de la más frecuente; como el par agrupa por esqueleto de conectividad, pueden ser tautómeros distintos. Difieren en 418 de las 56,411 filas de ajuste (0.74%), y recalculando el andamio a los dos lados la validación comparte andamio con el entrenamiento en el 0.5% de sus pares. **No es fuga:** con las columnas guardadas el cruce es cero, y el esqueleto —que sí es reproducible desde el SMILES— da cero recalculado también, así que ningún compuesto está en los dos lados. Lo que impide es comparar este conjunto con uno externo sin recalcular el andamio en los dos, porque entonces la cifra mide la discrepancia de definición. Medido en `2026-11-04-ingrid-2.13-contaminacion-externa`, que también sitúa el piso: la similitud de Tanimoto mediana de la validación a su vecino más cercano del entrenamiento es 0.679.
- **Resultado de la parte externa** (4 de noviembre, corrida `2026-11-04-artemio-2.13-contaminacion-externa`, con la regla de Pame sin cambios): **el 64.9% de los 8,151 pares de la base externa tiene un andamio de Bemis-Murcko que ya está en el ajuste**, contra el 0.5% del control; el 6.7% comparte además el esqueleto de conectividad (estereoisómeros), la similitud mediana al vecino más cercano es 0.787 (la referencia **en la misma fase** es la de la validación contra el entrenamiento, 0.679, es decir +0.108; el 0.414 que esta entrada citó antes era la prueba reservada de la **fase 1**, otra fase, y lo corrigió Pame en el #273) y el 87% de los pares pasa de 0.6. La similitud de la prueba reservada de la fase 2 no está medida. Según su regla, **la base externa no es comparable con la prueba reservada sin decirlo**: está más cerca del ajuste y el 0.792 de concordancia no se pone al lado del 0.720 como si midieran lo mismo. Eso es lo que la tesis del artículo predice, pero ahora está medido. Comprobación independiente: recalculando el andamio con RDKit sobre los SMILES únicos del ajuste sale 66.7%, la misma conclusión (la diferencia de dos puntos es de definición: ese cálculo usa los SMILES únicos del ajuste y no los del par). Para correrla hizo falta un cambio mínimo en el script: `Corrida` solo acepta rutas dentro del repositorio, así que la huella del archivo externo va en los parámetros.

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

**Cómo se trata la censura.** Un `> 10 µM` es censura **por la derecha** si se mide en µM (la concentración real es mayor que 10) y **por la izquierda** en `pActividad` (menor que 5). Un modelo que acepte intervalos lo usa tal cual en la escala que tenga, y lo que importa es que el intervalo quede del lado correcto. **Avance 4 (modelos individuales, sin ensambles):** `RegresionTobit` (`src/models/tobit.py`), una regresión lineal con censura por intervalos, ajustada en `pActividad`; las otras familias sencillas se entrenan sobre las exactas. **Avance 5:** `survival:aft` de XGBoost, que pide la escala de µM (cota inferior 10, superior infinita) y convierte a `pActividad` al final. El diccionario pide lo mismo: los censurados «se excluyen o se usa un método para valores censurados».

**El signo se verificó sobre los pares reales** con el Tobit (#139, `experimentos/2026-10-25-ingrid-2.9-signo-censura-tobit/`; validación de 6,961 pares, una semilla, sin afinar). Con el signo bueno, el 17.5% de los `> L µM` queda predicho del lado de la cota; con el invertido a propósito, el 2.1%; la pActividad media predicha de esos pares es 5.54 contra 6.24, para una cota media de 4.75. **La dirección es clara, pero por el criterio fijado de antemano (más de 20 puntos de diferencia) la comprobación no pasa: la diferencia es de 15.** Contra una `Ridge` entrenada solo con las exactas, el Tobit sube la concordancia (0.694 contra 0.681) y coloca mejor los censurados (17.5% contra 3.4%), pero no mejora las exactas (Spearman 0.496 contra 0.507, RMSE 1.210 contra 1.177). Un modelo lineal predice mucho peor que uno de árboles. Falta repetirlo con varias semillas, intervalos y los modelos afinados.

**Cómo se evalúa.**

- **Índice de concordancia de Harrell y Spearman**, que toleran la censura. **RMSE solo sobre las mediciones no censuradas**, declarado como tal.
- **Techo de reproducibilidad.** La patrocinadora indicó que la reproducibilidad experimental del IC50 en ChEMBL ronda 0.7 unidades logarítmicas (0.5 en Ki). Las fuentes: Kalliokoski et al. (2013, `kalliokoski2013ic50`), con desviaciones de 0.68 en pIC50 y 0.47 en Ki, y Kramer et al. (2012, `kramer2012ki`). **No es un número de consenso:** Landrum y Riniker (2024, `landrum2024ruido`) encuentran, con curación mínima, más ruido, y que exigir que coincidan los metadatos del ensayo mejora el acuerdo a costa de tamaño, que es el razonamiento de la [2.11](#d2-11). Como el 25–28% de los pares discrepa más de diez veces (una unidad logarítmica), un RMSE muy por debajo de ese orden no sería un buen resultado sino una señal de fuga de datos. El techo se escribe en el informe desde ahora.
- Las métricas de clasificación (MCC, AUPRC, [C.1](#dc-1)) se calculan sobre la clase derivada. Las de ranking están en la [C.5](#dc-5).

**El baseline de clasificación se conserva como piso.** Tres canalizaciones sin afinar, sobre los 54,369 pares de entrenamiento y validación (10,071 grupos, 71.4% de activos), con la diana como característica y la validación cruzada agrupada (`scripts/experimento_baseline.py --tarea actividad`; corrida `experimentos/2026-10-18-artemio-2.3-baseline-actividad-descriptores-diana-10um/`):

| Canalización | AUROC | IC 95% | MCC |
|:--|--:|:--|--:|
| Bosque aleatorio | 0.866 | [0.859, 0.874] | 0.495 |
| Boosting por histogramas | 0.857 | [0.848, 0.865] | 0.486 |
| Regresión logística | 0.796 | [0.786, 0.806] | 0.387 |

La logística queda 6–7 puntos abajo, con intervalos que no se tocan; entre el bosque y el boosting no se distingue. **El agregado no describe a los naturales:** el AUROC del bosque es 0.858 sobre los pares solo ChEMBL, 0.637 sobre los mixtos y **0.611 [0.572, 0.647]** sobre los de solo NPASS ([2.5](#d2-5)). La regresión tiene que superar este piso en la clase derivada.

**Qué cuesta.** La pérdida censurada es más maquinaria y su calibración importa. En un modelo de árboles con `survival:aft`, SHAP atribuye sobre log-potencia, más difícil de narrar a un biólogo que «esta subestructura empujó hacia activo». La [C.2](#dc-2) sigue siendo viable, pero el relato cambia.

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

**Pendiente, para el Avance 5.** Definir `direccion_consistente` para las 26 dianas (la tabla de tipos hoy solo cubre las tres de activación; por ejemplo, un EC50 sobre `GSK3B`, de inhibición) y su sensibilidad, declarada en la [página de variables objetivo](variable-objetivo-fase2.md). Medir cuánto cubre la API de los campos pedidos en nuestros compuestos: en todo ChEMBL, `action_type` está en 582,238 de unos 24.5 millones de actividades (2.4%).

#### 2.12 · Los inactivos de DrugMatrix {#d2-12 .propuesta}

**Estado:** propuesta

**Qué pasó.** 29,730 filas traen texto de inactividad («Not active»; ChEMBL: «Inhibition < 50% @ 10 uM and thus dose-response curve not measured»). Son una sola campaña de tamizaje (`CHEMBL1909046`, el panel DrugMatrix), 772 compuestos, todas `> 10 µM`. Se excluyen del principal. De ellas, 5,658 filas caen en dianas de la lista y sumarían **2,169 pares** (70,384 → 72,553) en solo cuatro dianas (`MAOA`, `PTGS2`, `ACHE`, `DRD2`), sobre 729 esqueletos.

**Con regresión aportan poco.** Las 5,658 filas dicen lo mismo: `pActividad` < 5, sin cuánto menos. Como clasificación pesaban mucho (61% de los negativos por registro, 10.8% por par); como cota de regresión son una sola cota repetida, concentrada en una campaña, cuatro dianas y fármacos conocidos (espacio químico sesgado).

**Se propone.** Fuera del modelo principal. **La medición del desempeño con y sin ellas queda para el Avance 5.** Una sensibilidad con ellas como negativos censurados y sin ellas, reportada al lado, con un análisis de esqueletos de los 772 compuestos. Como todas son de un solo documento, agrupar por documento en la validación cruzada las deja juntas en un pliegue, y eso hay que declararlo. El valor que podrían tener es el déficit de negativos verdaderos de cualquier conjunto derivado de la literatura, donde se publica lo que funciona.

**Medición · base externa de la patrocinadora** (4 nov, corrida `2026-11-04-artemio-2.13-muestra-de-jorge`). El archivo `…_Testeo.csv` (22,866 mediciones; huella sha256 en `params.yaml`; **no se copia al repositorio**) no comparte ningún identificador ni SMILES canónico con el de entrenamiento. Regla y script commiteados antes de correr; el `aft` guardado en `models/finales/` se evalúa sin reentrenar. Control: el constructor de pares reproduce los 70,384 pares de `fase2_pares.parquet` desde el archivo de entrenamiento (pasó).

- **Alcance:** de 8,151 pares (esqueleto × gen) con las 26 dianas del modelo quedan 8,134 con predicción (17 sin descriptores). Las otras 10 dianas del archivo no se pueden evaluar.
- **Resultado global:** concordancia **0.792** [0.787, 0.797] (IC95% remuestreando esqueletos), Spearman 0.733 sobre 6,664 exactas, 18.1% censurado. La prueba reservada dio 0.720: no está dentro del intervalo, y la externa sale **mejor**, no peor.
- **Por procedencia:** `solo_chembl` 0.786 (7,681 pares); `mixto` 0.615 (204); `solo_npass` 0.667 (249 pares, 113 exactas, Spearman 0.309; sin intervalo por tener menos de 500). En la prueba reservada el `solo_npass` dio 0.530 con 117 pares. Los naturales siguen siendo el estrato débil, con muestras pequeñas.
- **Con/sin hermano estereoisomérico** (esqueleto presente entre los de ajuste): con 541 pares 0.818 [0.794, 0.836]; sin 7,593 pares 0.790 [0.783, 0.795]. Solo 6.7% de los pares tiene hermano, y la diferencia es pequeña.
- **Qué no dice:** que el modelo generalice mejor de lo medido. Al correr esta medición no se había medido qué tan cerca están estos compuestos del ajuste; **después se midió** (corrida `2026-11-04-artemio-2.13-contaminacion-externa`, #272): el 64.9% de los pares tiene un andamio ya presente en el ajuste, contra 0.5% en el control, y la similitud mediana al vecino más cercano es 0.787 contra 0.679 de la validación en la misma fase (el 0.414 de la prueba reservada es de la fase 1 y no se compara aquí). Se separó por compuesto y no por andamio, así que **el 0.792 no es comparable con el 0.720**. Con dos comprobaciones independientes: predicciones una a una contra en lote (diferencia 0) y concordancia por doble bucle sobre 1,500 pares contra la función (0.78967 las dos).
- **Lectura única** de esta base; una variante nueva se declara como corrida aparte.

#### 2.13 · Ensambles para la regresión de potencia {#d2-13 .vigente}

**Estado:** vigente

**Qué se decidió.** Se definen e implementan cinco familias de ensamble para la predicción continua de potencia (`pActividad`), cubriendo tanto estrategias homogéneas como heterogéneas, además de un modelo acelerado de tiempo de falla (AFT) con manejo nativo de censura:

1. **Ensambles homogéneos (tres familias):**
   - `bosque` (`RandomForestRegressor`): ensamble paralelo por embolsado (bagging) sobre árboles de decisión, reduciendo la varianza mediante el promediado de estimadores independientes.
   - `boosting` (`HistGradientBoostingRegressor`): ensamble secuencial por potenciación de gradiente sobre árboles discretizados por histogramas, reduciendo el sesgo de forma computacionalmente eficiente.
   - `bagging_knn` (`BaggingRegressor` sobre `KNeighborsRegressor`): ensamble homogéneo no basado en árboles, aplicando bagging sobre un regresor local por vecinos cercanos para estabilizar estimaciones basadas en distancias químicas.
2. **Ensambles heterogéneos (dos familias):**
   - `votacion` (`VotingRegressor`): combinación lineal directa por promedio simple de estimadores de distinta naturaleza inductiva (`Ridge` como control lineal regularizado global y `kNN` como modelo local no paramétrico). No introduce meta-parámetros ni requiere particiones internas.
   - `apilado` (`ApiladoAgrupado`): ensamble de apilamiento (stacking) que entrena un meta-estimador (`Ridge`) sobre las predicciones fuera de pliegue generadas por los estimadores base.

La selección de las bases heterogéneas (`Ridge` y `kNN`) responde a los hallazgos de la [1.3](#d1-3) / #164, donde ambas familias obtuvieron la mayor concordancia al incorporar huellas estructurales (kNN alcanzó 0.756 con descriptores y huellas; 0.739 con descriptores solos; Ridge 0.724), mientras que el perceptrón multicapa (MLP) quedó descartado por degradar el desempeño (−0.027) y mostrar sobreajuste severo.

**El apilado agrupa su partición interna.** Para que el apilamiento (`ApiladoAgrupado`) estime honestamente los coeficientes del meta-regresor sin sesgo optimista, las predicciones fuera de pliegue deben generarse respetando estrictamente los grupos de andamio (`GroupKFold`). Como se demostró empíricamente en la [1.2](#d1-2), no respetar el agrupamiento estructural infla las métricas del bosque en **2.2 puntos de AUROC y 7.1 puntos de MCC** (con el `svm_rbf`, 1.3 y 1.9) por fuga de información entre análogos moleculares de los pliegues. En regresión, una partición aleatoria interna asignaría análogos del mismo andamio a entrenamiento y validación de las bases, produciendo predicciones artificialmente precisas y distorsionando las ponderaciones asignadas por el meta-modelo.

**El AFT entra sin envoltorio sobre la matriz densa.** `RegresionAFT` (`survival:aft` con XGBoost) utiliza directamente las observaciones censuradas por intervalos convirtiendo los límites de potencia a escala micromolar (cota inferior y superior), según lo resuelto en la [2.9](#d2-9) y [2.10](#d2-10). A diferencia de los regresores clásicos, que requieren el envoltorio `SoloExactas` para omitir los registros censurados durante el ajuste, el AFT entra sin envoltorio porque modela la verosimilitud de supervivencia con censura de forma nativa. Entró sobre la matriz densa (227 columnas: descriptores fisicoquímicos 2D de RDKit más variables indicadoras de diana, sin las huellas dispersas de Morgan / Sort & Slice). La razón **era** mecánica —`RegresionAFT.fit(X, inferior, superior)` recibe tres argumentos posicionales y no cabe en un `Pipeline`, que solo pasa una `y`— y ya no lo es: `ConHuellasCensurado` resuelve eso en doce líneas y el brazo con huellas está medido más abajo. **Ahora la razón es medida, y es otra.** Esto genera una consecuencia directa y transparente en la columna de tiempos de ejecución (`seg`), que contrasta con la de los ensambles evaluados sobre la matriz mixta.

**El afinado corre con una semilla y su métrica interna no es la principal.** La búsqueda de hiperparámetros (`AfinadoAgrupado` sobre kNN, con la rejilla tomada del `params.yaml` de la corrida `2026-10-26-antonio-2.9-baseline-regresion-sencilla-exactas`) se evalúa con una sola semilla (`SEMILLAS[0]`), preservando el protocolo del notebook 04b para no multiplicar el costo computacional. Su métrica interna de optimización (`neg_root_mean_squared_error`) no es la métrica principal del proyecto: el afinado corre envuelto en `SoloExactas`, por lo que la búsqueda interna nunca ve las mediciones censuradas. La evaluación externa del modelo final se rige por la concordancia de Harrell y la correlación de Spearman ([C.1](#dc-1), [2.9](#d2-9)), calculadas sobre la totalidad de los datos (exactos e intervalos censurados).

**Las tres semillas mueven el reparto y no el azar del modelo.** Para la evaluación final con tres semillas (`SEMILLAS = (0, 1, 2)`), el cambio de semilla controla la asignación de pliegues en la validación cruzada agrupada por andamio (`GroupKFold(shuffle=True, random_state=semilla)`), modificando el reparto de compuestos y análogos entre pliegues. A diferencia del notebook 04c, donde cada semilla movía simultáneamente el reparto en `StratifiedGroupKFold` y el azar interno del estimador (`random_state`), en el 05b las semillas mueven exclusivamente el reparto entre pliegues al mantener fijas las semillas de los estimadores base. Esto evalúa la estabilidad de los ensambles frente a distintas distribuciones de familias químicas en entrenamiento y validación.

**Resultado.** La corrida `2026-10-31-antonio-2.13-comparativa-regresion-ensambles` evaluó los nueve modelos sobre la misma partición agrupada, con tres semillas y cinco pliegues (una sola semilla para el afinado), de modo que los tiempos y las métricas son comparables entre sí. La corrida completa tardó **7 h 16 min** en un contenedor con dieciséis núcleos, de las cuales 5 h 56 min son el bucle de los nueve modelos y los 80 minutos restantes se reparten entre la lectura de datos, el armado de las huellas, la evaluación sobre la prueba reservada y las figuras.

| modelo | concordancia | NPASS | AUROC | MCC | ajuste s/pliegue | reloj total |
|:--|--:|--:|--:|--:|--:|--:|
| `bosque` | **0.765 ± 0.006** | 0.511 | 0.833 | 0.310 | 163.6 | 2,486 |
| `aft` | 0.761 ± 0.005 | **0.632** | **0.846** | **0.467** | **3.9** | **74** |
| `apilado` | 0.761 ± 0.006 | 0.527 | 0.832 | 0.298 | 44.7 | 3,512 |
| `knn_afinado` | 0.761 ± 0.006 | 0.554 | 0.828 | 0.376 | 88.2 | 1,362 |
| `votacion` | 0.757 ± 0.006 | 0.514 | 0.829 | 0.339 | 4.1 | 2,875 |
| `knn_referencia` | 0.756 ± 0.005 | 0.547 | 0.823 | 0.369 | 0.8 | 2,772 |
| `boosting` | 0.750 ± 0.006 | 0.511 | 0.825 | 0.291 | 49.0 | 781 |
| `bagging_knn` | 0.673 ± 0.006 | 0.518 | 0.711 | 0.221 | 19.8 | 7,467 |
| `media_por_diana` | 0.642 ± 0.006 | 0.403 | 0.720 | 0.000 | 0.8 | 37 |

**El modelo final de la fase 2 es el `aft`, y no el que gana el agregado.** El `bosque` queda por encima en concordancia global y lo hace de forma consistente, en catorce de los quince pliegues, así que no es un empate. Pero el `aft` gana en AUROC, en MCC y, sobre todo, en la concordancia de los compuestos que solo aparecen en NPASS, que son los que este proyecto existe para priorizar. Ahí le gana a los ocho modelos restantes en todas las evaluaciones de cada uno: quince de quince contra siete de ellos, y cinco de cinco contra el `knn_afinado`, que corrió con una sola semilla (`semillas_afinado: [0]`) y por eso tiene cinco evaluaciones y no quince. El segundo mejor es precisamente ese `knn_afinado`, con 0.554. Los conteos por pliegue se pueden recomputar desde `pliegues.csv` en la carpeta de la corrida, que trae una fila por modelo, semilla, pliegue y estrato.

**El mecanismo está medido y no supuesto.** En el conjunto de ajuste, el 53.5% de las filas de NPASS vienen censuradas contra el 16.6% de las de ChEMBL. Como los ensambles corren envueltos en `SoloExactas`, que descarta las censuradas, reciben 982 de las 2,114 filas de NPASS, mientras el `aft` las recibe todas. La ventaja no viene de una química mejor sino de ver datos que a los demás se les quitan.

**La razón «gana en MCC, 0.467 contra 0.310» es sobre todo colocación, no discriminación (4 de noviembre, [#185](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/185)).** El mismo par ordena peor (concordancia −0.004) y yerra más (RMSE), con un AUROC casi empatado, y el MCC corta la potencia predicha en pActividad 5, donde cae la distribución de cada modelo. Corrida `2026-11-04-artemio-2.13-mcc-por-umbral-aft-contra-bosque` (`scripts/experimento_mcc_por_umbral.py`), las mismas 15 evaluaciones, un ajuste por pliegue y tres lecturas del MCC con las mismas predicciones. La regla se declaró antes: el corte fijo debía reproducir la comparativa (0.466 y 0.3106 contra 0.4668 y 0.3103: lo hace) y la ventaja se sostiene si, con el corte que declara activa la misma fracción que tiene el ajuste, la diferencia pareada es positiva, mayor que su desviación y en 12 de 15.

| estrato `todos` | `aft` | `bosque` | diferencia pareada (desviación) | `aft` mejor en |
|:--|--:|--:|:--|--:|
| MCC, corte fijo en 5 (la comparativa) | 0.466 | 0.311 | **+0.155** (0.015) | 15 de 15 |
| MCC, corte de igual prevalencia | 0.495 | 0.467 | **+0.028** (0.013) | 15 de 15 |
| MCC, mejor corte del pliegue (cota optimista) | 0.498 | 0.471 | +0.027 (0.011) | 15 de 15 |
| AUROC | 0.845 | 0.833 | +0.012 (0.004) | 15 de 15 |
| fracción que declara activa a 5 | 0.816 | 0.936 | −0.120 | 0 de 15 |

**Cinco sextas partes de la ventaja eran dónde cae la distribución**: el `bosque`, que se ajusta solo con las exactas, declara activo el 93.6% de los pares a 5 contra 81.6% del `aft`. Al quitar eso la ventaja baja de +0.155 a +0.028, que sigue siendo positiva en las 15 evaluaciones y 2.1 veces su desviación, y coincide en tamaño con el AUROC (+0.012). Por la regla declarada **la razón se sostiene, pero con otra magnitud**, y tiene que citar el AUROC y el MCC de igual prevalencia, no el corte fijo. En `solo_npass`, el estrato por el que se eligió el modelo, la lectura de igual prevalencia da +0.072 (desviación 0.042, 13 de 15) contra +0.055 con corte fijo (14 de 15), el AUROC +0.111 y la concordancia +0.121 (15 de 15 las dos): ahí no hay encogimiento, y la diferencia de colocación va en el mismo sentido (0.325 contra 0.701 declarado activo). **La elección del `aft` no cambia**; cambia cuánto pesa su primera razón, y el argumento de NPASS no dependía de ella. Límites: el corte de igual prevalencia usa la tasa del ajuste y no un umbral elegido con validación interna, que el issue sugería y que con el bosque cuesta horas; la cota optimista usa las etiquetas del pliegue y no es un resultado. Queda por reescribir la celda 14 del 05b (§5.1), que no toco aquí porque el #229 edita ese cuaderno.

**La limitación que esta corrida dejaba abierta ya está medida, y está abajo.** El `aft` difiere de los ensambles en más de una cosa a la vez, así que el apartado «Los tres confundidos del `aft`, separados» es el que cierra esta advertencia. *Versión superada (2 de noviembre):* esta entrada decía que «esta corrida no permite atribuir la ganancia en NPASS solo a la censura, y separarlas exige una corrida adicional con los ensambles sobre la matriz densa». Esa corrida adicional existe desde el #181 y está once líneas más abajo, de modo que la entrada se contradecía consigo misma (#211).

**Sobre la partición reservada.** Primera toma de la prueba en el proyecto, registrada en `experimentos/prueba.csv`. El `aft` da 0.720 de concordancia global sobre los 13,944 pares, con AUROC de 0.793 y MCC de 0.277. En los 117 pares que solo tiene NPASS baja a 0.530 con un Spearman de 0.083, que es ruido alrededor del azar. Eso no respalda el argumento de NPASS ni lo contradice, porque la prevalencia de activos pasa del 12.3% en ajuste al 44.4% en prueba sobre esos 117 pares. El argumento se sostiene en los quince pliegues de la validación cruzada. El punto 6 de la lectura del [05b](../notebooks/05b_Ensambles_actividad.ipynb) resuelve ahí la condición de refutación que el punto 5 había declarado y dejado anotada (#186): trae el desglose de la prueba por procedencia, y concluye que el estrato de naturales no refuta el 0.632 ni lo confirma, así que la ventaja del AFT en productos naturales está medida en validación cruzada y no verificada sobre esqueletos nuevos.

**Tres advertencias para leer la tabla.**

*Las dos columnas de tiempo no miden lo mismo, y hacen falta las dos.* `ajuste s/pliegue` es la que registra `metricas.json`: solo la llamada a `fit`, promediada entre pliegues. `reloj total` es el tiempo de pared de evaluar ese modelo entero —quince pliegues, cinco en el `knn_afinado`— e incluye las **dos** predicciones que el arnés hace en cada pliegue, sobre validación y sobre el conjunto de ajuste completo para calcular el `rmse_entrenamiento`. De ahí que el `knn_referencia` ajuste en 0.8 s y gaste 2,772 s: en los modelos por vecinos el costo está en predecir, no en ajustar, y con una sola columna la lectura sale al revés. Las dos se tomaron con dieciséis núcleos (`n_jobs=-1`), así que ninguna es comparable con las mono-hilo del 04b ni del 04c. El `nota_seg` que quedó registrado en el `params.yaml` de la corrida describe la columna `seg` como tiempo de reloj, y eso es lo que aquí se corrige; el archivo no se reescribe porque es el registro de la corrida.

**Los tres confundidos del `aft`, separados.** La elección se apoyaba en un modelo que difiere
de los demás en **tres** cosas a la vez: la librería (XGBoost contra el `HistGradientBoosting` de
sklearn, que es lo que el `boosting` de esta corrida usa), la pérdida censurada, y las 227 columnas
densas. Corrida `2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura`: cuatro brazos sobre los
mismos pliegues y semillas, con la métrica principal —la concordancia en `solo_npass`— declarada en
el script antes de ejecutarlo. Diferencia pareada contra el `aft` y evaluaciones ganadas:

| Brazo | todos | solo_chembl | mixto | solo_npass |
|:--|--:|--:|--:|--:|
| `xgb_sin_censura` | −0.0154 · 0/15 | −0.0133 · 0/15 | −0.0548 · 0/15 | −0.1248 · 0/15 |
| `aft_huellas` | +0.0048 · 14/15 | +0.0051 · 14/15 | −0.0120 · 6/15 | −0.0076 · 4/15 |
| `aft_filtro` | +0.0007 · 10/15 | +0.0010 · 10/15 | −0.0047 · 6/15 | +0.0021 · 8/15 |

**La ventaja es de la censura, no de la librería.** `xgb_sin_censura` es XGBoost con
`reg:squarederror` sobre las mismas 227 columnas, los mismos 100 árboles y la misma profundidad 6,
ajustando solo con las exactas: **pierde las sesenta evaluaciones pareadas**. En `solo_npass` cae a
0.5073, que es donde quedan todos los modelos que descartan las censuradas —`bosque` 0.5107,
`boosting` 0.5108, `votacion` 0.5143— independientemente de su familia. En MCC, 0.4668 contra
0.3485. Eso es lo que cerraba el confundido de la librería, y lo cierra en la dirección que el
argumento necesitaba.

**Las huellas ganan donde hay ChEMBL y no cuestan nada distinguible.** En `todos` y en `solo_chembl`
mejoran la concordancia (+0.005 con dispersión propia de 0.003), el RMSE (−0.017, 15 de 15) y el
AUROC (+0.005). En `mixto` y en `solo_npass` todas las diferencias quedan **entre 0.1 y 0.9 de su
propia dispersión**: la pérdida apunta a la baja en los cinco indicadores de los dos estratos, y
esta corrida sola **no la establece**. Lo que sí es consistente es la dirección, y es la tercera vez
que aparece: el 04c y el 03c ya la midieron ([1.3](#d1-3)), siempre con la ganancia del lado de
ChEMBL. Y una advertencia de lectura: con huellas la concordancia agregada sube a 0.7659 y supera al
`bosque` (0.7650), así que **el brazo que gana el agregado es el que va peor en los dos estratos con
naturales** — el mismo reparto por volumen que ya tenía el agregado, con el 93% de las filas de
ChEMBL.

**Las huellas entran en la fase 2 para explicar, no porque midan mejor**, igual que la
[1.3](#d1-3) lo resolvió para la fase 1. El modelo entregado es el `aft` sin ellas, porque es el que
corrió, el que tomó la partición reservada y el que este cuaderno sostiene. El brazo `aft_huellas`
queda como **modelo de explicación**: es el mismo XGBoost con la misma pérdida, los mismos datos y
los mismos pliegues, y lo único que cambia es la representación, con la medición de arriba diciendo
que esa diferencia no se distingue del ruido en ninguno de los cuatro estratos. Una columna
Sort & Slice es una subestructura concreta, así que es lo que permite la atribución a nivel de
fragmento que pide la [C.2](#dc-2), y los descriptores no. Se reportan los dos brazos. **Si el
ranking final sale peor en los naturales, esto es lo primero que hay que revisar**, porque la
dirección de la pérdida ya apareció en tres cuadernos independientes.

**Las 745 filas que el filtro descarta no costaban nada medible.** `aft_filtro` da +0.0021 en
`solo_npass` con 8 de 15. El defecto es real —el filtro conserva las 9,396 censuradas por la derecha
y 0 de las 745 por la izquierda, que son las potentes: cota inferior mediana de pActividad 7.00 y 726
de 745 activas al corte de 10 µM— y queda **acotado**: las cifras agregadas del `aft` eran un piso de
dos milésimas, no de más. Arreglarlo es una línea, y lo único que rechaza el cero es el `inf_um > 0`
del propio filtro, porque `limites_en_micromolar` devuelve `0.0` y XGBoost admite
`label_lower_bound = 0`. No hace falta reejecutar las 7 h 16.

**Y una regularidad que ordena las tres lecturas:** el RMSE y el Spearman los gana siempre quien
ajusta solo con exactas —`xgb_sin_censura` saca el mejor RMSE agregado de la corrida, 0.9967, y el
mejor Spearman de `solo_npass`, 0.2586—, porque son las métricas que se calculan sobre ese mismo
subconjunto ([C.1](#dc-1)). La censura compra concordancia y MCC, que es donde vive el umbral, y el
entregable es una lista priorizada con un corte ([C.5](#dc-5)).

*La ventaja en tiempo del `aft` mezcla el modelo con la representación.* Corre sobre las 227 columnas densas, mientras los ensambles pagan `AgregarHuellas` dentro de cada ajuste. En ajuste puro son 3.9 s contra 163.6 s del bosque, cuarenta y dos veces; en reloj total, 74 s contra 2,486 s, treinta y tres. La dirección es la misma por los dos caminos, pero no son la misma cuenta, y la parte que corresponde a no construir las huellas no se separó.

**Atribución por subestructura: se hizo con el brazo `aft_huellas`, y los métodos no concuerdan según la regla declarada (4 de noviembre, [#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146)).** Corrida `2026-11-05-artemio-2.13-atribucion-aft-huellas-subestructuras` (`scripts/experimento_atribucion_subestructuras.py`), sin tocar la prueba reservada. La [C.2](#dc-2) pide atribución por subestructura y el `aft` final no usa huellas, así que se repitió el diseño de dos métodos (TreeSHAP y permutación, cinco pliegues, semilla 0) sobre el brazo con descriptores, 2,048 huellas Sort & Slice y la diana; cada columna de huella es un identificador de Morgan de radio 2 y se tradujo a un fragmento. **Es el brazo, no el modelo final**, que no mejora en NPASS (E3). La regla se declaró antes: concuerdan si el Spearman sobre la unión de las 100 primeras de cada método es al menos 0.50 y comparten 8 de sus 15 primeras; solo se afirman las subestructuras que están en el top 30 de los dos.

**Una limitación de la regla de promedio, medida:** cada columna se divide entre cinco pliegues aunque su vocabulario Sort & Slice no exista en alguno, así que lo que vive en pocos pliegues no puede llegar arriba. De las 2,534 columnas que existen en algún pliegue, 1,916 están en los cinco y **618 (24.4%), todas huellas, en menos**; las 37 que la corrida reporta están todas en los cinco, de modo que el orden que se reporta no se deforma, pero una subestructura específica de pocos pliegues quedaba fuera por construcción. La corrida se repitió el 5 de noviembre para guardar este conteo y la columna `en_pliegues` en el CSV; las demás cifras salieron idénticas.

**Superada por la corrida definitiva ([#281](https://github.com/AntonioVazquezMartinez/Bioactive-AI/pull/281), `2026-11-06-antonio-C.2-atribucion-fase2-con-nombres`, 6 de noviembre):** con cinco repeticiones de permutación sobre 11,248 filas el Spearman sobre la unión de los 100 primeros sube a 0.577 y las compartidas del top 15 siguen en 11, así que por la misma regla los métodos **sí concuerdan**. El «no concuerdan» de abajo era ruido de la permutación, como esta corrida suponía como causa probable, y no un resultado; se conserva porque es la medición previa y su límite (una repetición, 1,500 filas) es lo que la explica. Para citar la atribución de la fase 2 se usa la definitiva.

**Resultado: Spearman 0.38 (no llega a 0.50) y 11 de 15 en común; por la regla declarada los métodos NO concuerdan en este brazo**, a diferencia del modelo final (0.93). La causa probable es ruido: la permutación sobre 1,500 filas con una repetición por columna reparte ~2,270 columnas casi todas cercanas a cero. Lo que los dos ven en el top 30:

| columna | tipo | TreeSHAP (rango) | permutación (rango) |
|:--|:--|--:|--:|
| `BertzCT`, `SMR_VSA3`, `fr_halogen`, `MolLogP`, `PEOE_VSA7`, `FpDensityMorgan3`, `SMR_VSA7`, `SlogP_VSA2` | descriptor | 1 a 25 | 3 a 18 |
| `MAOA`, `DRD2`, `MAOB`, `LRRK2`, `BCHE`, `ACHE` | diana | 2 a 21 | 1 a 12 |
| id 2041434490 | **subestructura**: nitrógeno de anillo de grado 2 sin H (tipo piridina) | 0.232 (3) | 0.0027 (9) |
| id 3777168895 | **subestructura**: CH aromático vecino a un N aromático (`c(c)n`) | 0.162 (4) | 0.0021 (10) |
| id 2246699815 | **subestructura**: carbono alifático de grado 3 sin H fuera de anillo (tipo carbonilo) | 0.058 (16) | 0.0012 (21) |

**Qué se afirma, y qué no.** Las tres subestructuras que ven los dos métodos son **genéricas y frecuentes**: aparecen en el 57%, 21% y 52% de las moléculas de una muestra de 6,000. Dicen que el modelo usa la presencia de heterociclos nitrogenados y de grupos carbonilo, no un farmacóforo específico. Las que podrían ser más específicas (un sulfonamida aromático, `S(N)(=O)(=O)c(c)c`, y `C(CO)c(c)n`) las ve solo la permutación y **no se afirman**. Las columnas de huella reúnen el 42% de la atribución de TreeSHAP en este brazo. Contraste con TPSA y HBD: TPSA en los lugares 51 (TreeSHAP) y 20 (permutación) y `NumHDonors` en el 259 y el 274: no dominan, como en el modelo final. **Qué cambia para la C.2:** se cumple en la forma (dos métodos, una subestructura nombrada) y **no en el fondo**: no hay una subestructura específica en que los dos métodos concuerden, y el acuerdo global es débil. No se afirma ninguna. **Verificado de forma independiente:** TreeSHAP suma al margen con diferencia 1.4×10⁻⁶ y coincide exacto con `shap.TreeExplainer`; los identificadores coinciden con otra API de RDKit (`GetMorganFingerprint`) en 20 moléculas (0 discrepancias); y cada subestructura se caracterizó por los invariantes del átomo central en 6,000 moléculas (un fragmento de radio 0 como «n» o «C» no basta para identificarla, porque el identificador codifica también grado, hidrógenos y anillo). **Límites:** una semilla; permutación ruidosa; el brazo no es el modelo final; y un identificador de radio 0 o 1 es un entorno atómico, no un grupo funcional.

**Qué pesa en el `aft` final, con dos métodos independientes (4 de noviembre, [#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146)).** Corrida `2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion` (`scripts/experimento_atribucion_aft.py`), sin tocar la prueba reservada. La [C.2](#dc-2) exige al menos dos métodos de atribución independientes y reportar solo lo en que concuerdan; la fase 2 no tenía ninguno. Sobre el modelo final (201 descriptores y la diana), cinco pliegues agrupados de la semilla 0: **TreeSHAP** (cuánto aporta cada columna a la predicción, de la estructura de los propios árboles) y **permutación** (cuánta concordancia se pierde al barajar una columna en la validación, que solo usa la salida y la etiqueta). La regla se declaró antes: concuerdan si el Spearman entre sus importancias es ≥ 0.70 y comparten al menos 8 de sus 15 primeras columnas.

**Los métodos concuerdan: Spearman 0.93 y 12 de 15 en común.** Las que están en el top 15 de **los dos**, que son las únicas que se afirman:

| columna | TreeSHAP (rango) | pérdida de concordancia al barajar (rango) |
|:--|--:|--:|
| `BertzCT` (complejidad topológica) | 0.378 (1) | 0.0168 (3) |
| diana `MAOA` | 0.295 (2) | 0.0326 (1) |
| `fr_halogen` (halógenos) | 0.165 (3) | 0.0052 (8) |
| diana `MAOB` | 0.161 (4) | 0.0227 (2) |
| `SMR_VSA3` | 0.145 (5) | 0.0058 (6) |
| diana `DRD2` | 0.143 (6) | 0.0069 (5) |
| `FpDensityMorgan3` | 0.137 (7) | 0.0039 (11) |
| `SlogP_VSA10` | 0.134 (8) | 0.0036 (15) |
| diana `LRRK2` | 0.115 (9) | 0.0071 (4) |
| `MolLogP` | 0.106 (11) | 0.0038 (12) |
| diana `BCHE` | 0.097 (13) | 0.0056 (7) |
| `BalabanJ` | 0.090 (14) | 0.0036 (14) |

**Qué dice.** (1) La diana pesa mucho pero no todo: seis dianas (`MAOA`, `MAOB`, `DRD2`, `LRRK2`, `BCHE`, y `ACHE` solo en la permutación) están entre las primeras, y las 26 columnas de diana reúnen el 15.5% de la atribución de TreeSHAP; el 85% es química. (2) **El contraste que pide `CLAUDE.md` con TPSA y HBD**: TPSA queda en el lugar 44 (TreeSHAP) y 40 (permutación) y `NumHDonors` en el 165 en los dos, así que **no dominan la potencia**, a diferencia de lo que se espera para la permeabilidad de la fase 1; la afirmación vale para la fase 2 y no se traslada. (3) Las dos características químicas de arriba son de complejidad y forma (`BertzCT`, `BalabanJ`, `FpDensityMorgan3`), de lipofilia (`MolLogP`, `SlogP_VSA10`) y los halógenos. **Controles:** TreeSHAP suma al margen del modelo con diferencia 2×10⁻⁶ y coincide exactamente con `shap.TreeExplainer` en 200 filas; la estabilidad entre pliegues es de 0.91 para TreeSHAP y de 0.67 para la permutación, que es más ruidosa. **Verificado de forma independiente:** la permutación de scikit-learn sobre un pliegue y otra muestra da el mismo orden de magnitud (MAOA 0.027, BertzCT 0.023, TPSA 0.0015, `NumHDonors` 0.0002) y correlaciona 0.85 con la guardada.

**Lo que esta corrida no cumple de la C.2.** Pide también atribución **por subestructura**, y el `aft` final **no usa huellas**: sus columnas son descriptores y dianas. Esa parte no se puede cumplir con este modelo; haría falta el brazo `aft_huellas` (que no mejora en NPASS y no es el modelo final) y mapear cada columna Sort & Slice a su subestructura. **Límites:** una sola semilla; la permutación sobre 3,000 filas de cada pliegue con dos repeticiones; columnas correlacionadas se reparten la importancia (la permutación puede subestimarlas); y la atribución dice qué usa el modelo, no por qué funciona.

**Los cuatro brazos del `aft`, completos: ni filtrar los descriptores ni quitarlos mejora en NPASS (4 de noviembre).** Corrida `2026-11-04-artemio-2.13-brazos-aft-filtrados-y-huellas-solas` (`scripts/experimento_aft_brazos.py`), sin tocar la prueba reservada. La corrida de Ingrid midió `aft` y `aft_huellas`; faltaban dos de los cuatro brazos del plan (E3): los **descriptores filtrados** (el filtro de la 03c y la 04c, aprendido dentro de cada pliegue, con TPSA y HBD protegidos) y las **huellas solas** con la diana, sin ningún descriptor. Los cuatro con los mismos pliegues y semillas. La regla se declaró antes: la métrica principal es la concordancia en `solo_npass`; un brazo supera al `aft` si su diferencia pareada es positiva, mayor que su desviación y en 12 de 15 evaluaciones.

| brazo | `solo_npass`: concordancia | diferencia con `aft` (desviación) | mejor / peor en | veredicto | `todos`: diferencia (desviación) |
|:--|--:|:--|:--|:--|:--|
| `aft` (201 descriptores y diana) | 0.6308 | — | — | el control | — |
| `aft_filtrados` (≈150–156 de 201) | 0.6329 | +0.0021 (0.0213) | 11 / 4 | empate dentro del ruido | +0.0014 (0.0027), 12 / 3: empate |
| `aft_huellas_diana` (huellas y diana) | 0.5895 | **−0.0413** (0.0278) | 0 / **15** | **empeora al `aft`** | +0.0029 (0.0042), 11 / 4: empate |
| `aft_huellas` (descriptores, huellas y diana) | 0.6187 | −0.0121 (0.0186) | 5 / 10 | empate dentro del ruido | +0.0057 (0.0035), 15 / 0: supera |

**Lectura.** (1) **Filtrar los descriptores no cambia nada que se distinga del ruido** (+0.002 en NPASS con una desviación de 0.021), y el filtro deja 156 de 201 con todo el ajuste. Es coherente con lo que ya se medía en la fase 1 (el 03c, #195): la depuración no mueve el resultado. (2) **Quitar los descriptores cuesta en NPASS**: las huellas solas pierden 0.041 de concordancia y **empeoran al `aft` en las 15 evaluaciones**, aunque en `todos` empatan. Esto matiza la lectura de la fase 2 de que los descriptores se pueden tirar (las huellas solas casi igualaban al brazo ancho): en el estrato por el que se eligió el modelo **no se pueden**. (3) Las huellas con descriptores ayudan en `todos` y no en NPASS, como ya medía Ingrid. **El modelo final no cambia**: ningún brazo supera al `aft` donde se eligió.

**Un control declarado no pasó, y se dice.** Los tres controles `aft` en `todos` (0.7609 contra 0.7610), `aft` en `solo_npass` (0.6308 contra 0.6322) y `aft_huellas` en `todos` (0.7666 contra 0.7659) pasan; **`aft_huellas` en `solo_npass` da 0.6187 contra 0.6246 de Ingrid, diferencia de 0.0059 con una tolerancia de 0.003**. La regla decía que entonces hay un error y el resto no se lee; se investigó en vez de omitirla. Los paquetes son idénticos (xgboost 3.4.1, scikit-learn 1.9.1, numpy 2.5.4) y el sistema no: la de Ingrid corrió en Linux WSL2 x86 y esta en macOS arm64, y `CLAUDE.md` ya documenta que las corridas no son idénticas entre sistemas. Dos pruebas de que es del entorno y no del código: la corrida E9 (otro código, esta máquina) da exactamente 0.6187 para ese brazo, y las diferencias que ven los demás brazos son de otro orden (0.04). La diferencia es 0.2 veces la desviación pareada del brazo (0.027). **Por eso la lectura anterior vale con esa salvedad**: la comparación de `aft_huellas` en `solo_npass` (−0.012) está dentro del ruido en cualquiera de las dos cifras. **Verificado de forma independiente:** recalculé el brazo `aft_filtrados` de la semilla 0 con un ciclo de pliegues escrito aparte y la concordancia coincide en los cinco pliegues (diferencia máxima 0.0); y las huellas solas ven 2,074 columnas (26 de diana y 2,048 huellas, ningún descriptor). **Límites:** una sola σ (1.0), una sola semilla del modelo, 15 evaluaciones; el `aft_filtro` (las 745 filas censuradas por la izquierda) y la sensibilidad de σ están en las corridas de Ingrid y no se repiten; y falta el SHAP con un segundo método de atribución (#146), que pide elegir el brazo.

*El `knn_afinado` sale con un RMSE de entrenamiento de 0.000* porque cada punto de entrenamiento se predice a sí mismo, lo que solo ocurre con `weights="distance"`. La corrida no dejó registrado qué punto de la rejilla eligió —es lo primero que habría que añadir a la siguiente—, pero de las dos opciones de la rejilla (`uniform` y `distance`) esa es la única que da exactamente 0. Su brecha entre entrenamiento y validación no es comparable con la de los demás.

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
| S2.12 | La regresión con censura aporta algo sobre usar solo las exactas | Acotado | El signo está comprobado en datos reales con el Tobit (#139), pero la comprobación no pasa su propio criterio y la censura no mejora las exactas ([2.9](#d2-9)) | Regresión sobre las exactas más un clasificador de censura, o clasificación como piso |
