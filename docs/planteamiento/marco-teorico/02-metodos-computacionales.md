# Métodos computacionales

Cómo se predice actividad biológica a partir de la estructura química, y cómo se convierte una molécula en algo que un modelo pueda consumir.

> **Estado: borrador para revisión del equipo y los asesores.** Se construyó a partir de siete ramas de investigación documentadas en [`docs/referencias/`](../../referencias/README.md), que conservan la evidencia completa y las advertencias de acceso. La bibliografía está en [`bibliografia.bib`](../../referencias/bibliografia.bib), con 208 entradas.
>
> **Antes de entregar:** verificar contra doi.org toda referencia marcada como de acceso parcial o sin acceso. Varias entradas tienen metadatos que nadie del equipo ha leído.

---

## 4. Fundamentos de la predicción computacional de actividad

### 4.1 Orígenes históricos del QSAR

La legitimidad de predecir actividad biológica a partir de estructura química tiene su origen formal en 1964, en dos trabajos independientes y conceptualmente distintos.

**Hansch y Fujita** establecieron la ecuación que lleva su nombre: un modelo de regresión lineal múltiple que relaciona la actividad biológica con parámetros fisicoquímicos de los sustituyentes — el parámetro hidrofóbico π, precursor directo del logP; la constante electrónica de Hammett σ; y el parámetro estérico de Taft `hansch1964`. La contribución conceptual fue tratar la interacción fármaco-receptor con la misma lógica de las relaciones lineales de energía libre de la química orgánica física.

La razón para adoptar el sistema octanol-agua como sustituto de la hidrofobicidad es que el octanol posee simultáneamente una cabeza polar y una cola hidrofóbica larga, lo que lo convierte en un mimetismo razonable del entorno anfipático que una molécula debe atravesar.

**Free y Wilson** propusieron un enfoque distinto: en lugar de regresar sobre parámetros fisicoquímicos continuos, codifican la presencia o ausencia de cada sustituyente como variables indicadoras binarias, expresando la actividad como suma de contribuciones aditivas `freewilson1964`. El contraste conviene establecerlo con claridad: **Hansch es paramétrico y mecanicista**, con descriptores físicamente interpretables y transferibles entre series; **Free-Wilson es puramente estructural-aditivo**, sin requerir datos externos pero con contribuciones no transferibles a otro andamiaje. Ambos son lineales y ambos son precursores directos del QSAR moderno `gogishvili2021`.

La evolución hacia alta dimensionalidad y aprendizaje automático está documentada en dos revisiones extensas `cherkasov2014, muratov2020`: los descriptores estéricos evolucionaron de Taft a STERIMOL a campos 3D; la expansión hacia índices de conectividad e índices topológicos permitió trabajar con conjuntos estructuralmente diversos y no congenéricos; y el QSAR de clasificación extendió el marco más allá de la regresión continua. Un dato útil para justificar el uso de modelos clásicos: **las redes neuronales profundas mostraron en promedio solo ~0.04 más de R² que *random forests*** a través de varios benchmarks `muratov2020`.

> **Advertencia:** los artículos originales de 1964 están tras muro de pago de ACS y no están indexados con resumen. Su contenido se confirmó indirectamente a través de las revisiones históricas citadas.

### 4.2 El principio de similitud y sus límites

El supuesto sobre el que descansa todo el proyecto —que moléculas estructuralmente similares tienden a tener propiedades similares— se conoce como **principio de similitud-propiedad** y se atribuye convencionalmente al libro editado por Johnson y Maggiora en 1990.

Un matiz importante para el rigor de la tesis: **el libro de 1990 nunca usa literalmente esa frase** `dalke2020`. El término se formaliza años después `maggiora2014`. Las convenciones de cita correctas son, entonces: citar Johnson y Maggiora (1990) como la obra que consolidó el concepto, y Maggiora et al. (2014) como la fuente donde se acuñó formalmente el término.

La crítica central que la tesis debe reconocer: *"la similitud es un concepto subjetivo y multifacético… Los métodos de similitud y las lecturas numéricas de cálculos de similitud están probablemente entre los enfoques computacionales peor entendidos en química medicinal"* `maggiora2014`. La similitud molecular **no es una propiedad intrínseca y objetivamente medible**, sino que depende del descriptor, el fingerprint y la métrica de distancia elegidos `bajorath2017`.

El punto donde el principio se rompe empíricamente es el de los **acantilados de actividad**: pares de compuestos estructuralmente muy similares con diferencias grandes de potencia. El comentario que dio visibilidad al fenómeno corrigió la práctica previa de descartarlos como valores atípicos, reencuadrándolos como fenómeno estructural fundamental `maggiora2006, stumpfe2019`. Son instancias de discontinuidad de la relación estructura-actividad que resultan perjudiciales para el modelado. El marco de doble filo es directamente relevante: *"mientras que los químicos medicinales pueden aprovechar regiones del espacio químico ricas en acantilados de actividad, los practicantes de QSAR necesitan escapar de dichas regiones"* `cruzmonteagudo2014`.

### 4.3 Dominio de aplicabilidad

El concepto de que un modelo solo es válido dentro de la región del espacio químico representada por sus datos de entrenamiento se formalizó en un reporte del taller ECVAM `netzeva2005`, y su desarrollo más citable revisa las familias de métodos `sahigara2012`: basados en rango, en distancia geométrica, en densidad de probabilidad y en *leverage*.

El método de *leverage* se define a partir de la matriz sombrero **H = X(XᵀX)⁻¹Xᵀ**, con un umbral convencional **h\* = 3p/n**; los compuestos con h > h* se consideran fuera del dominio.

> **Nota metodológica:** existe una discrepancia real en la literatura entre las convenciones h* = 3p/n y h* = 3(p+1)/n, según si el intercepto se cuenta entre los parámetros. **El capítulo de metodología debe declarar explícitamente cuál se usa.**

Un marco más moderno es la **predicción conforme** `norinder2014, norinder2015`, que reformula el dominio de manera estadística en lugar de geométrica: en vez de trazar un límite binario en el espacio de descriptores, emite para cada compuesto una región de predicción calibrada sobre un conjunto separado. Bajo intercambiabilidad, esa región contiene el valor verdadero con al menos la confianza especificada, y **se ensancha automáticamente para compuestos distintos a los del entrenamiento**.

Esto es metodológicamente atractivo para este trabajo precisamente porque los productos naturales se ubicarán en el borde —o fuera— de la distribución de entrenamiento de cualquier conjunto de BBB, y un predictor conforme se degrada de forma controlada en lugar de extrapolar silenciosamente.

### 4.4 El espacio químico de los productos naturales

La comparación cuantitativa más sólida entre fármacos aprobados de origen natural y sintético `stratton2015` reporta:

| Métrica | Productos naturales | Totalmente sintéticos |
|---|---|---|
| Peso molecular medio | 626 | 343 |
| Fracción de carbonos sp³ | 0.68 | 0.37 |
| Anillos aromáticos | 0.8 | 1.9 |
| Lipofilicidad (ALOGPs) | 1.5 | 2.7 |

El número de estereocentros es de 2 a 6 veces mayor en los de origen natural. La fracción sp³ como medida de complejidad se originó al demostrar que tanto ella como la quiralidad **aumentan sistemáticamente conforme los compuestos avanzan de descubrimiento a ensayo clínico a fármaco aprobado** `lovering2009`.

Un hallazgo que matiza el argumento: una vez controlado el peso molecular, **el cumplimiento de la regla de cinco es similar** entre compuestos no-drug-like, drug-like y productos naturales (86.8%, 88.3% y 85.4%). Es decir, **la regla de cinco por sí sola tiene poder discriminante débil**.

> **Dos afirmaciones sin entrada bibliográfica.** La comparación de cumplimiento de la regla de cinco (86.8 / 88.3 / 85.4%) proviene de un estudio de *drug-likeness* de medicina tradicional china (PMC3538521) cuya revista no se pudo confirmar, y la taxonomía por dimensionalidad 0D–4D de un artículo de *Molecular Informatics* cuyo año de publicación quedó en duda. Ambas se omitieron deliberadamente de `bibliografia.bib` en vez de adivinar los campos. **Hay que completarlas o retirar la afirmación antes de entregar.**

Esto refuerza el argumento sobre dominio de aplicabilidad: la divergencia real entre productos naturales y compuestos tipo fármaco no está en el cumplimiento de la regla de cinco, sino en la fracción sp³, los estereocentros y la complejidad de los sistemas de anillos — variables que justifican una evaluación explícita del dominio de aplicabilidad antes de aplicar el modelo `feher2003, rodrigues2016, chen2017`.

### 4.5 Los cinco principios de la OCDE

El documento de la OCDE establece, verbatim, que para considerar un modelo QSAR con fines regulatorios debe asociarse a: **(1) un *endpoint* definido; (2) un algoritmo inequívoco; (3) un dominio de aplicabilidad definido; (4) medidas apropiadas de bondad de ajuste, robustez y capacidad predictiva; (5) una interpretación mecanística, cuando sea posible** `oecd2007`.

Su origen se remonta a los principios de Setúbal, propuestos en 2002 y finalizados en 2004.

**Un matiz importante:** la OCDE es explícita en que estos principios **no constituyen criterios de aceptación regulatoria en sí mismos**, sino un marco conceptual para guiar la validación. Adherirse a él fortalece la credibilidad, transparencia y reproducibilidad, y ofrece una estructura clara para organizar la metodología:

| Principio | Correspondencia en este trabajo |
|---|---|
| Endpoint definido | Definición operacional de permeabilidad BBB y de actividad neuroprotectora |
| Algoritmo inequívoco | Pipeline de ML documentado y versionado |
| Dominio de aplicabilidad | Caracterización del espacio químico, crítica al puntuar productos naturales |
| Bondad de ajuste y predictividad | Validación interna y externa, scaffold split, Y-randomization |
| Interpretación mecanística | Descriptores interpretables consistentes con el mecanismo de permeabilidad |

### 4.6 Metodología de validación

**Scaffold split.** El concepto de andamiaje proviene del análisis de 5,120 fármacos conocidos, cuyos armazones 2D se reducen a solo 1,179 distintos, con los 32 más frecuentes describiendo la mitad de la base `bemis1996properties`. La justificación de dividir por andamiaje es explícita: *"dado que el scaffold splitting intenta separar moléculas estructuralmente diferentes en subconjuntos distintos, ofrece un desafío mayor para los algoritmos de aprendizaje que la división aleatoria"*, y *"imita el desarrollo real en el campo"* `wu2018moleculenet`.

> No se localizó en ese artículo una tabla numérica comparando directamente ambas divisiones sobre datos idénticos, por lo que el argumento debe presentarse como cualitativo.

Un ángulo complementario es la división temporal, que produce estimaciones que son mejor sustituto del desempeño prospectivo real `sheridan2013`. Como contrapunto necesario para no presentar la literatura como monolítica: una división racional puede lucir mejor estadísticamente sin que ello implique ganancia real en capacidad predictiva `martin2012rational`.

**Y-randomization.** Consiste en permutar aleatoriamente los valores de la variable respuesta manteniendo fijos los descriptores, y comparar el ajuste del modelo original contra los reajustados `rucker2007`. La lógica es directa: si permutar las etiquetas y reajustar aún produce buen ajuste, la correlación original probablemente sea artefacto de sobreajuste o azar — riesgo alto en situaciones de muchos descriptores y pocas muestras.

**Validación interna contra externa.** El artículo metodológicamente más influyente del campo muestra que la suposición generalizada de que un q² alto de validación cruzada demuestra capacidad predictiva es *"generalmente incorrecta"*: no encontraron correlación entre q² interno alto y desempeño real sobre un conjunto independiente `golbraikh2002`. Solo los modelos validados externamente, después de la validación interna, pueden considerarse confiables `gramatica2007`.

**Diseño que adopta este trabajo:** la validación cruzada es necesaria pero no suficiente; debe complementarse con un conjunto de prueba genuinamente externo —nunca tocado durante construcción, selección de variables ni ajuste de hiperparámetros— y dividido por andamiaje.

### 4.7 Desbalance de clases

Los conjuntos de bioactividad rara vez están balanceados. La razón por la que la exactitud engaña se ilustra canónicamente: en un ejemplo de mamografía con 98% normal y 2% anormal, un clasificador que siempre predice la clase mayoritaria alcanza **98% de exactitud siendo clínicamente inútil** `chawla2002smote`. El sobremuestreo ingenuo por replicación produce sobreajuste; el submuestreo descarta información real. SMOTE genera puntos sintéticos a lo largo del segmento hacia vecinos minoritarios, generalizando las regiones de decisión en vez de estrecharlas.

**Métricas apropiadas.** El coeficiente de correlación de Matthews es *"la única tasa de clasificación binaria que genera una puntuación alta solo si el predictor fue capaz de predecir correctamente la mayoría de las instancias positivas y la mayoría de las negativas"*, a diferencia de F1, que es independiente de los verdaderos negativos `chicco2020`. Su ejemplo numérico es ilustrativo: exactitud 0.90 y F1 0.95 sugieren excelente desempeño, mientras **MCC = −0.03** revela correctamente que el clasificador es inútil.

Sobre AUROC contra AUPRC: la tasa de falsos positivos se calcula sobre una clase negativa muy grande, de modo que un número absoluto fijo de falsos positivos se traduce en una tasa numéricamente pequeña, **haciendo que las curvas ROC luzcan casi idénticas independientemente del desbalance** `saito2015`. La curva de precisión-*recall* tiene como línea base la prevalencia, ofreciendo una referencia consciente del desbalance. **Para conjuntos BBB+/BBB− desbalanceados, el AUPRC es más diagnóstico que el AUROC.**

---

## 5. Representación molecular

### 5.1 SMILES, SELFIES e InChI

La representación de entrada del proyecto tiene su origen en el trabajo de Weininger `weininger1988`, con su continuación algorítmica que introdujo el algoritmo CANGEN para notación canónica `weininger1989`. Un grafo molecular se serializa mediante una gramática pequeña: un subconjunto orgánico de átomos escribibles sin corchetes, símbolos de enlace, ramificaciones con paréntesis y cierres de anillo con dígitos pareados.

**La SMILES canónica no es única entre herramientas.** No existe una forma estándar de generar una representación canónica: Daylight, OpenEye, ChemAxon y OpenBabel desarrollaron cada uno su propio algoritmo, no publicado y mutuamente incompatible, de modo que **la misma molécula produce cadenas canónicas distintas según el toolkit** `oboyle2012`. Es una consideración práctica para la deduplicación entre bases de datos.

**SELFIES** responde al problema de validez sintáctica: bajo una sola mutación de carácter, una cadena SMILES conserva su validez **solo el 9.9% de las veces**, frente al 100% de SELFIES; con dos mutaciones, 3.0% `krenn2020selfies`. Es relevante en contextos generativos, no en este proyecto, que no genera moléculas.

**InChI e InChIKey** no son descriptores sino **identificadores** `heller2015inchi`: su objetivo de diseño es que la misma etiqueta siempre se refiera a la misma sustancia, pensado para deduplicación y búsqueda. El InChIKey es un hash de 27 caracteres, unidireccional, que requiere una base de consulta para revertirse. Es la llave de unión entre las bases de datos de este proyecto, no una entrada del modelo.

#### Longitud variable: el problema que resuelve la featurización

Una propiedad del SMILES que condiciona toda la arquitectura del modelo es que **su longitud es variable**. Medido sobre los 7,805 compuestos válidos de B3DB (ver [`notebooks/01_EDA.ipynb`](../../notebooks/01_EDA.ipynb)):

| Estadístico | Caracteres |
|---|---|
| Mínimo | 1 (`O`, agua; `C`, metano) |
| Percentil 25 | 36 |
| Mediana | 49 |
| Percentil 75 | 70 |
| Percentil 95 | 117 |
| Máximo | 383 |

La cadena más larga es 383 veces la más corta, y la longitud correlaciona **0.908** con el número de átomos pesados: es esencialmente un proxy del tamaño molecular, sin información química propia.

A esto se suma que la longitud **no es estable ni para una misma molécula**. La cafeína escrita de dos formas válidas distintas produce cadenas de 28 y 26 caracteres, ambas con el mismo InChIKey. Es la consecuencia práctica del problema de canonicalización descrito arriba: la longitud depende de la herramienta y del orden de recorrido del grafo, no solo de la molécula.

**De aquí se sigue el papel de la featurización.** Los modelos de ensamble que adopta este trabajo exigen que todas las observaciones tengan el mismo número de variables. Los descriptores y los fingerprints convierten una entrada de longitud variable en un vector de longitud fija:

| Molécula | SMILES | Átomos pesados | Fingerprint Morgan | Descriptores RDKit |
|---|---|---|---|---|
| Agua | 1 carácter | 1 | 2,048 bits | 217 |
| Cafeína | 28 caracteres | 14 | 2,048 bits | 217 |
| Ciclosporina | 224 caracteres | 85 | 2,048 bits | 217 |

Esta es una razón adicional —independiente de la interpretabilidad y del costo computacional— para no usar un modelo de lenguaje sobre SMILES en este proyecto: exigiría relleno o truncamiento, y los límites de longitud de contexto empezarían a afectar a las moléculas grandes precisamente cuando su tamaño es una característica relevante para la permeabilidad.

**Implicación operativa para la deduplicación:** dado que la cadena no es un identificador estable, la deduplicación entre fuentes debe hacerse por InChIKey recalculado desde la estructura, nunca comparando cadenas SMILES. El EDA del Avance 1 aplica ese criterio.

### 5.2 Taxonomía de descriptores

La referencia canónica `todeschini2000handbook` clasifica los descriptores en familias: **constitucionales** (conteos simples), **topológicos** (derivados del grafo 2D), **geométricos** (requieren coordenadas 3D), **electrónicos** (distribución de carga) y **termodinámicos** `suaygarcia2022`. Una taxonomía complementaria por dimensionalidad va de 0D a 4D, ubicando explícitamente el índice de Wiener y el TPSA como descriptores 2D.

La base grafo-teórica se remonta al **índice de Wiener** `wiener1947`, definido como la suma de las distancias de camino más corto entre todos los pares de vértices del grafo molecular, y al **índice de conectividad de Randić** `randic1975`, que pondera cada enlace según el grado de los átomos que conecta.

Ambos son invariantes de grafo: el de Wiener crece con el tamaño y disminuye con la ramificación, lo que explica su correlación histórica con puntos de ebullición; el de Randić distingue isómeros ramificados de lineales a igual fórmula. **El TPSA es un descendiente conceptual directo**: se calcula de forma aditiva sobre el mismo grafo de conectividad, sin requerir coordenadas 3D, razón por la cual se clasifica como topológico pese a describir formalmente una propiedad de superficie.

### 5.3 Por qué TPSA y logP predicen permeabilidad: la razón física

El TPSA es un método fragmento-aditivo cuyo resultado prácticamente coincide con el área polar 3D real (r = 0.99 sobre 34,810 moléculas), siendo dos o tres órdenes de magnitud más rápido de calcular `ertl2000tpsa`.

El mecanismo físico es la **desolvatación**: *"la interfaz lípido-agua está asociada con una capa de moléculas de agua perturbadas con propiedades de polarización significativamente distintas. Por ello, la capacidad de estas moléculas de agua para formar puentes de hidrógeno con moléculas de fármaco se reduce dramáticamente y forma parte del proceso de desolvatación"* `pajouhesh2005`.

En síntesis: para cruzar una bicapa lipídica, un soluto debe abandonar el agua a granel —donde sus grupos polares están completamente enlazados por puentes de hidrógeno— e ingresar a un interior no polar incapaz de satisfacer esos enlaces. **La penalización de energía libre de ese paso escala con la cantidad de superficie polar que la molécula expone**, que es exactamente lo que el TPSA cuantifica de forma aditiva. El logP es el resumen experimental directo del mismo balance de energía libre.

Los umbrales son más estrictos en la barrera hematoencefálica que en la absorción intestinal (≲90 Å² frente a ≤140 Å² `clark1999`) porque las uniones estrechas abolen la ruta paracelular, dejando la difusión transcelular como mecanismo dominante. Existe además un límite superior de lipofilicidad: un logP excesivo atrapa la molécula en la membrana y favorece la unión inespecífica y el eflujo. La regla de cinco `lipinski2001` aproxima el mismo balance de forma más burda.

### 5.4 Familias de representación y evidencia comparativa

| Familia | Dimensión | Interpretabilidad por substructura |
|---|---|---|
| Descriptores fisicoquímicos 2D (RDKit) | 217 | Por propiedad, no por substructura |
| Mordred | ~1,826 | Mixta |
| Morgan / ECFP | 1024–4096 bits | **Directa**, vía mapeo bit → substructura |
| MACCS keys | 167 bits | **Trivial**: cada bit es un SMARTS nombrado |
| Embeddings preentrenados | ~768 | Débil |
| Redes de grafos | 300 | Fuerte solo con módulos específicos |

**Fingerprints de conectividad extendida.** Una precisión de nomenclatura: **el número del nombre es el diámetro**, de modo que `radius=2` en RDKit corresponde a ECFP4 `rogers2010ecfp`. El identificador nativo es un hash de 32 bits sin límite; plegarlo introduce **colisiones**, con consecuencias para la interpretabilidad tratadas en la sección 7.

**Evidencia comparativa.** Al evaluar 25 modelos preentrenados como embeddings congelados contra ECFP, sobre 25 conjuntos con scaffold split y análisis bayesiano, casi todos los modelos neuronales muestran mejora insignificante o nula `praski2026benchmarking`:

| Representación | AUROC medio | Rango (de 25) |
|---|---|---|
| ECFP | 79.89% | 7.52 |
| ChemBERTa (MTR) | 79.99% | 7.32 |
| MolFormer | 79.80% | 9.50 |
| SELFormer | 73.18% | 20.04 |

**Precisión importante sobre el alcance:** esta conclusión aplica a embeddings **congelados** alimentando un modelo clásico. MolFormer-XL **afinado de extremo a extremo** reporta 93.7 en BBBP contra 71.4 de Random Forest `ross2022molformer`. Este trabajo adopta descriptores y fingerprints por la combinación de evidencia comparable, costo en CPU e interpretabilidad directa.

En estudios específicos de BBB, **los descriptores solos superan a Morgan solo**: AUC 0.866 contra 0.771 sobre BBBP `zhu2025featureguided`, y R² de 0.418 contra 0.312 bajo scaffold split sobre B3DB `tiwari2026conformeros3d`. Combinar nunca resultó perjudicial.

---
