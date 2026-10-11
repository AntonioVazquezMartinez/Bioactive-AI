# Fundamentos desde cero

La teoría que el proyecto da por sabida, explicada sin suponer nada: química, biología del cerebro e inteligencia artificial, en el orden en que se necesitan. Está pensada para leerse de principio a fin la primera vez.

Es la entrada accesible. El [marco teórico](planteamiento/marco-teorico/README.md) desarrolla los mismos temas con las fuentes y la evidencia, y la [investigación](referencias/README.md) documenta cada decisión técnica. Para los términos sueltos, el [glosario](glosario.md) es la versión canónica. Los números salen de los datos y de los documentos del repositorio; donde algo no se verificó, se dice.

## 1. ¿Qué es una molécula y cómo se "escribe"?

Todo en este proyecto empieza en el mismo punto: un compuesto químico, representado como texto.

**Compuesto** y **molécula** se usan aquí como sinónimos: es una sustancia definida por cómo están unidos sus átomos entre sí. El agua es una molécula. La cafeína es una molécula. La morfina es una molécula.

Dentro de esta familia hay una distinción que el proyecto usa constantemente:

- Un **producto natural** es un compuesto que produce un organismo vivo —casi siempre una planta, en este proyecto— sin que nadie lo haya diseñado en un laboratorio. La morfina, que viene de la amapola, es un producto natural.
- Un compuesto **sintético** es uno fabricado por síntesis química, sin que ningún organismo lo produzca de forma natural.

Esta distinción importa porque el objetivo final del proyecto es encontrar productos naturales prometedores, pero la mayoría de los datos disponibles para entrenar modelos de inteligencia artificial son de compuestos sintéticos (fármacos ya estudiados). Es un desajuste que aparece una y otra vez más adelante.

### Cómo se le "dice" a una computadora qué molécula es

Una computadora no entiende un dibujo de una molécula. Necesita una representación en texto. La que usa este proyecto se llama **SMILES** (*Simplified Molecular Input Line Entry System*): una cadena de caracteres que describe los átomos y cómo están conectados, sin necesidad de dibujar nada.

Ejemplo concreto: el alcohol común, **etanol**, se escribe `CCO`. Se lee así: dos carbonos (`C`) pegados uno al otro, y luego un oxígeno (`O`) pegado al segundo carbono. Eso es toda la molécula.

Dos cosas del SMILES que van a aparecer seguido:

- **Su longitud varía mucho.** Puede ir de 1 carácter (el agua, `O`) a varios cientos para una molécula grande. En el archivo de la patrocinadora, la mediana es 49 caracteres y el máximo es 338 (en los archivos crudos de B3DB llega a 383).
- **No es único.** La misma molécula se puede escribir de más de una forma válida, y distintos programas (RDKit, OpenEye, etc.) generan cadenas distintas para la misma molécula. Esto tiene una consecuencia práctica importante: **nunca se puede usar el SMILES para saber si dos filas de una base de datos son "la misma molécula"**, porque podrían estar escritas diferente y parecer distintas sin serlo.

### El identificador que sí es confiable: el InChIKey

Para resolver ese problema existe el **InChIKey**: un identificador (no una representación completa, solo una "huella digital") que se calcula a partir de la estructura real de la molécula, no de cómo se escribió el SMILES. Lo importante es que **la misma molécula siempre produce el mismo InChIKey**, sin importar qué programa lo calcule ni cómo se haya escrito el SMILES original. Por eso, en este proyecto, **toda comparación entre compuestos se hace por InChIKey, nunca por el texto del SMILES ni por el nombre del compuesto** (los nombres, como vas a ver más adelante, a veces están de plano equivocados en las bases de datos).

El InChIKey tiene 27 caracteres. Sus primeros 14 caracteres codifican únicamente el **esqueleto de conectividad**: la estructura de la molécula ignorando los detalles de cómo están acomodados sus átomos en el espacio (lo que se llama **estereoquímica**). Esto importa porque una misma molécula puede tener varias versiones que solo difieren en ese acomodo espacial —se llaman **estereoisómeros**— y dos estereoisómeros pueden comportarse de forma biológicamente distinta aunque compartan fórmula y conectividad. Vas a ver que este detalle tiene consecuencias reales en los datos (los [problemas de calidad](datos-contenido.md) traen ejemplos).

---

## 2. El obstáculo central: la barrera hematoencefálica

Este es, literalmente, el problema que resuelve la primera mitad del proyecto. Vale la pena entenderlo bien.

### ¿Qué es?

El cerebro no deja entrar cualquier cosa que traiga la sangre. Alrededor de los vasos sanguíneos que irrigan el cerebro hay una capa de células muy unidas entre sí —mucho más que en cualquier otro tejido del cuerpo— que actúa como un filtro selectivo. A esto se le llama **barrera hematoencefálica**, y en este proyecto (y en toda la literatura) se abrevia **BBB**, por sus siglas en inglés (*blood-brain barrier*).

No es una membrana pasiva como un colador: es una interfaz activa, formada por células del endotelio (la pared interior de los vasos sanguíneos) selladas entre sí por unas estructuras llamadas **uniones estrechas**, y rodeadas por otros tipos de célula que ayudan a mantenerla (**pericitos**, y los **pies terminales de astrocitos**, que son prolongaciones de células llamadas astrocitos). Al conjunto completo —endotelio, uniones, pericitos y astrocitos trabajando juntos— se le llama **unidad neurovascular**.

¿Por qué existe? Para proteger al cerebro: las neuronas necesitan un ambiente químico muy estable (de iones, de neurotransmisores) para funcionar bien, y el torrente sanguíneo tiene fluctuaciones constantes que serían dañinas si llegaran libremente al cerebro.

### El problema que esto crea para cualquier medicamento

La barrera no distingue entre "cosas malas" y "medicamentos útiles". Bloquea casi todo por igual. Esto significa que un compuesto puede tener un efecto excelente contra alguna enfermedad del cerebro **en un experimento de laboratorio con células aisladas**, y ser completamente inútil como medicamento real porque nunca logra llegar al tejido cerebral.

Por eso, a cualquier compuesto se le puede asignar una etiqueta:

- **BBB+**: logra cruzar la barrera y llegar al cerebro.
- **BBB−**: no logra cruzar.

### Cómo cruzan las cosas que sí cruzan

Hay varias rutas posibles. Las dos que más importan para este proyecto:

- **Difusión pasiva**: la molécula simplemente atraviesa las células por sí sola, sin ayuda de ningún mecanismo biológico. Es la ruta relevante para moléculas pequeñas, y favorece a las que son poco polares (poco "amigas del agua") y no demasiado pesadas. El ejemplo clásico: la morfina, si se modifica químicamente para volverse menos polar, se convierte en heroína, y penetra el cerebro mucho mejor, aunque ambas moléculas son casi iguales.
- **Eflujo activo**: aquí está la parte que más le importa a este proyecto, porque es contraintuitiva. Existen unas "bombas" en las células de la barrera —la más importante se llama **glicoproteína-P**, o **P-gp**— cuyo trabajo es *expulsar de regreso a la sangre* cualquier compuesto que ya haya logrado entrar por difusión pasiva. Es decir: un compuesto puede cumplir perfectamente las reglas físico-químicas para cruzar, entrar... y ser devuelto a la sangre de inmediato por una de estas bombas, sin que nunca llegue a hacer efecto.

**Esta es la razón por la que no basta con mirar el tamaño o la polaridad de una molécula para predecir si cruza.** Un modelo que solo considere las propiedades de "permeación pasiva" se puede equivocar justo en los casos donde el eflujo activo domina.

### Por qué la concentración importa (y por qué "cruza o no cruza" no es tan simple)

La difusión pasiva y el eflujo activo están compitiendo dentro de la misma célula, al mismo tiempo. A **concentraciones bajas** del compuesto, el eflujo tiene capacidad de sobra para expulsarlo todo, y el compuesto se comporta como BBB−. Pero las bombas de eflujo tienen un límite de capacidad: si subes la concentración lo suficiente, el eflujo **se satura** (ya no da abasto) y entonces la difusión pasiva puede dominar, haciendo que el mismo compuesto se comporte como BBB+.

La consecuencia de diseño es importante y aparece seguido en este proyecto: **BBB+/BBB− no es una propiedad fija del compuesto**, como podría ser su peso molecular. Es una clasificación que depende de las condiciones del experimento (a qué concentración se probó) y de qué convención de umbral usó quien reportó el dato. Por eso una de las bases de datos que usa el proyecto (la de Spielvogel et al., más adelante) no fuerza una etiqueta binaria, sino que tiene una tercera categoría: **eflujo**, para los compuestos cuyo comportamiento depende justamente de esto.

### Cómo se mide realmente si algo cruza

No hay un único experimento "oficial". Existen varios, y cada uno mide algo ligeramente distinto:

- **logBB**: el logaritmo de la razón entre la concentración del compuesto en el cerebro y en la sangre. Es la medida más citada, pero tiene un defecto conocido: mide, en parte, cuánto se queda "pegado" el compuesto en el tejido o unido a proteínas de la sangre, no solo cuánto realmente cruza de forma utilizable. El umbral clásico para decir "sí cruza" es logBB ≥ −1.
- **Kp,uu**: la razón entre la concentración *libre* (no pegada a nada) en el cerebro y en la sangre. Es conceptualmente más limpia que logBB, pero se mide con menos frecuencia, así que hay menos datos públicos con esta medida.
- **PAMPA-BBB**: un experimento con una membrana artificial, sin células vivas. Es rápido y barato, pero **solo mide difusión pasiva**: es ciego a las bombas de eflujo.
- **MDCK-MDR1**: un experimento con células vivas que sí tienen la bomba P-gp. En teoría debería ser más realista, pero en la práctica, cuando se comparó contra mediciones directas en animales, **no mostró buena correlación** —un resultado contraintuitivo, porque uno esperaría que la membrana artificial (sin células) fuera la menos representativa, y resultó ser la más consistente.
- **Perfusión cerebral in situ**: la medición más directa en animales vivos, pero invasiva y de bajo rendimiento (no se puede hacer a gran escala).

**Consecuencia práctica para los datos del proyecto:** las etiquetas BBB+/BBB− que se usan para entrenar los modelos vienen de una mezcla de estos experimentos distintos, con lógicas distintas. Eso introduce ruido en las etiquetas que no es aleatorio, sino que depende de qué experimento se usó para cada compuesto. Es una limitación real que hay que reconocer, no esconder.

---

## 3. Las reglas que predicen si algo cruza

Antes de que existiera inteligencia artificial para esto, los químicos ya habían encontrado reglas simples, basadas en propiedades fáciles de calcular de una molécula, que predicen razonablemente bien si algo cruza la barrera. Vale la pena conocerlas porque el proyecto las usa como punto de comparación obligatorio: **si un modelo complicado de IA no supera claramente a estas reglas simples, eso en sí mismo es un resultado que hay que reportar**.

Las propiedades que importan (todas se calculan directamente de la estructura de la molécula, sin necesidad de ningún experimento):

- **TPSA** (*área de superficie polar topológica*, medida en Å², ángstrom cuadrado): qué tanta superficie de la molécula es "polar", es decir, atrae o forma enlaces con el agua. Es, por mucho margen, **el predictor individual más fuerte** que existe para esto.
- **logP**: qué tan "amiga de la grasa" (lipofílica) es la molécula, en vez de amiga del agua. Se mide comparando cuánto se disuelve en una mezcla de aceite (octanol) contra cuánto se disuelve en agua.
- **MW** (*peso molecular*): literalmente cuánto pesa la molécula.
- **HBD** y **HBA**: cuántos **donadores** y cuántos **aceptores de puente de hidrógeno** tiene la molécula (grupos de átomos que pueden formar ese tipo de enlace débil con el agua).

### Por qué estas propiedades funcionan, explicado con física simple

Para que una molécula cruce la bicapa de grasa que forma la membrana de una célula, tiene que "soltar" el agua a la que está pegada. Cuantos más puentes de hidrógeno forme con el agua (más polar sea, medido por TPSA), más energía cuesta ese proceso de "soltarse" — y por eso penetra peor. Es, literalmente, el mismo motivo por el que el aceite y el agua no se mezclan, aplicado a nivel de una sola molécula tratando de cruzar una membrana.

El logP mide algo relacionado, pero no es lo mismo: demasiado poco logP (muy polar) y la molécula no puede dejar el agua; demasiado logP (demasiado lipofílica) y la molécula queda "atrapada" dentro de la grasa de la membrana en vez de atravesarla limpiamente, lo que además favorece que se pegue de forma inespecífica a otras cosas y que las bombas de eflujo la reconozcan mejor. Hay un punto intermedio óptimo, no "mientras más lipofílica, mejor".

### Los números concretos (verificados sobre los datos reales de este proyecto)

El umbral clásico de TPSA que se enseña en los libros de texto es ≤ 90 Å². La literatura reporta un óptimo más estricto, **66.8 Å²**, y una regla de dos condiciones, **TPSA < 67 Å² y HBD ≤ 1**, con 96.6% de precisión para BBB+. Al verificarlo sobre los datos de este proyecto (Avance 1):

| Conjunto | Regla TPSA < 67 Å² y HBD ≤ 1 | Lectura |
|---|---|---|
| Grupo A (subconjunto con logBB, el de la literatura) | precisión 0.966 · sensibilidad 0.589 · AUC 0.720 | reproduce la cifra publicada, pero solo marca como BBB+ al 54% de los compuestos |
| Conjunto completo (7,805) | precisión 0.853 · sensibilidad 0.515 · AUC 0.680 | el AUC queda por debajo de TPSA < 90 Å² (0.729) y de TPSA < 67 Å² sola (0.701) |

Es decir: la regla de dos condiciones es muy precisa cuando acierta, pero **no supera a las alternativas simples en todo el conjunto**. Se usa como referencia obligatoria y como verificación de las explicaciones del modelo, no como un modelo ganador.

Una advertencia importante: el umbral óptimo de TPSA **no es un número fijo universal**. Cambia según el subconjunto con que se calcule: 66.6 Å² en el grupo A, 83.6 en A+B, 101.9 en el conjunto completo y 107.0 calculado solo con entrenamiento (Avance 2). No es una constante física de la barrera, sino algo que depende de qué compuestos se midieron, y aún no tiene intervalos de confianza. Hay que decir siempre sobre qué datos se calculó un umbral, nunca presentarlo como una ley universal.

---

## 4. Enfermedades del cerebro y qué significa "neuroprotección"

La segunda mitad del proyecto busca compuestos que protejan al cerebro de enfermedades degenerativas, principalmente Alzheimer y Parkinson. Aquí va lo mínimo que hay que saber de esas enfermedades para entender por qué se eligieron las "dianas" (más adelante se explica qué es una diana) que usa el proyecto.

### Alzheimer, en lo esencial

Hay dos proteínas centrales en esta enfermedad:

- **Amiloide-β (Aβ)**: un fragmento de proteína que se acumula en forma de placas en el tejido cerebral de pacientes con Alzheimer. Se produce cuando una proteína más grande (la proteína precursora amiloide) se corta de cierta forma. La **hipótesis de la cascada amiloide** propone que esta acumulación es el evento que desencadena el resto de la enfermedad. Es una hipótesis influyente, pero **está seriamente cuestionada**: varios medicamentos que reducen el amiloide no han logrado detener la enfermedad de forma convincente, y algunos expertos argumentan abiertamente que el amiloide podría no ser la causa principal.
- **Tau**: otra proteína, que en el Alzheimer se modifica químicamente de más (se "hiperfosforila") y forma agregados llamados ovillos neurofibrilares.

También existe la **hipótesis colinérgica**: la idea de que la pérdida de una sustancia llamada acetilcolina (que usan las neuronas para comunicarse) contribuye a los síntomas, en particular la pérdida de memoria. Es la base de los medicamentos para Alzheimer que ya existen en el mercado (como el donepezilo).

### Parkinson, en lo esencial

Aquí el actor central es otra proteína, la **α-sinucleína**, que se agrega de forma anormal dentro de las neuronas (formando los llamados cuerpos de Lewy). También hay evidencia sólida de que las mitocondrias (las "plantas de energía" de la célula) funcionan mal en las neuronas afectadas, y varios genes relacionados con el Parkinson hereditario apuntan en esa misma dirección.

### Lo que comparten ambas enfermedades, y por qué importa para el proyecto

Varios mecanismos aparecen en ambas enfermedades, y son justamente los que el proyecto intenta atacar con las dianas que eligió: estrés oxidativo y disfunción mitocondrial, **neuroinflamación** (inflamación causada por las propias células del sistema inmune del cerebro), y **excitotoxicidad** (sobreestimulación de las neuronas hasta dañarlas, por exceso de una sustancia llamada glutamato).

### "Diana molecular": la pieza que falta explicar

Una **diana** (en inglés *target*) es la proteína específica sobre la que un compuesto actúa para producir su efecto. Por ejemplo, si un compuesto inhibe a la proteína que fabrica una enzima dañina, esa proteína es la diana del compuesto. El proyecto trabaja con **37 dianas identificadas por gen más 2 receptores completos** (39 filas en el archivo de etiquetas), curadas a mano por la patrocinadora, cada una asociada a alguno de estos mecanismos de enfermedad. Más adelante ([contenido de los datos](datos-contenido.md)) se explica cómo están organizadas.

### La advertencia más importante de esta sección: "neuroprotector" es una palabra peligrosa

Aquí hay un dato duro que cambia cómo hay que hablar de los resultados del proyecto: de **1,026 tratamientos neuroprotectores** que mostraron buenos resultados en estudios experimentales (animales, cultivos de células) para el caso de la isquemia cerebral (derrame), solo 114 llegaron a probarse en personas, y **ninguno demostró eficacia clínica convincente**. Es decir: que algo "funcione" en un experimento de laboratorio casi nunca predice que vaya a funcionar como medicamento real en una persona. Esto no es una excepción rara: es, históricamente, la norma en este campo.

Por eso, en este proyecto, el lenguaje correcto es siempre **"actividad neuroprotectora predicha según su mecanismo molecular"**, nunca llamar a un compuesto directamente "neuroprotector" sin esa salvedad. Es una diferencia de honestidad científica, no un simple matiz de redacción.

---

## 5. Productos naturales como fuente de medicamentos

### El caso de éxito que justifica la idea completa del proyecto

La **galantamina** es un alcaloide (un tipo de compuesto natural) que se extrae de una flor (*Galanthus nivalis*, la campanilla de invierno). Se usó durante generaciones en medicina tradicional antes de que la ciencia moderna confirmara su mecanismo (inhibe una enzima relacionada con la hipótesis colinérgica mencionada arriba) y se convirtiera en un medicamento aprobado para Alzheimer. Es la prueba de que la ruta "producto natural → mecanismo validado → medicamento" sí funciona.

**Pero es la excepción, no la norma**, y el proyecto tiene que ser honesto sobre eso.

### El problema de los falsos positivos: PAINS

Muchos compuestos naturales aparecen una y otra vez en estudios como "activos" contra decenas de enfermedades distintas, lo cual, pensado con cuidado, es sospechoso: es poco probable que una sola molécula tenga un mecanismo específico contra tantas cosas diferentes. A este fenómeno se le conoce con las siglas **PAINS** (*compuestos de interferencia pan-ensayo*): sustancias que dan resultados positivos en los experimentos no por un efecto biológico específico, sino por mecanismos de interferencia —reaccionan químicamente de forma inespecífica, alteran la forma en que se mide el experimento, o simplemente perturban la membrana de las células sin actuar sobre ninguna proteína en particular.

El ejemplo más documentado es la **curcumina** (el pigmento amarillo de la cúrcuma): ha acumulado más de 120 ensayos clínicos en humanos, y **ninguno controlado y riguroso ha mostrado un beneficio real**. La explicación más probable es que buena parte de su "actividad" reportada en estudios de laboratorio es justamente este tipo de interferencia, no un efecto farmacológico genuino.

**Consecuencia para el proyecto:** antes de reportar cualquier compuesto como candidato prometedor, hay que pasarlo por filtros diseñados para detectar este tipo de interferencia, y desconfiar en particular de resultados "demasiado buenos" para compuestos de esta familia química (polifenoles, catecoles).

### Por qué los productos naturales son "distintos" desde el punto de vista de la computadora

Comparados con los compuestos sintéticos que dominan las bases de datos de entrenamiento, los productos naturales que sí llegaron a ser medicamentos aprobados tienden a ser más pesados (peso molecular promedio de 626, contra 343 en los sintéticos), con una estructura tridimensional más compleja y más puntos de unión posibles. Esto importa porque significa que **cualquier modelo entrenado principalmente con compuestos sintéticos puede comportarse mal cuando se le pide evaluar un producto natural**, simplemente porque nunca vio suficientes ejemplos parecidos durante su entrenamiento. Este punto vuelve a aparecer en la sección 7.

---

## 6. Cómo "aprende" una inteligencia artificial de esto

Esta sección explica, en términos simples, qué hace realmente un modelo de IA en este proyecto.

### La idea básica: aprender de ejemplos, no de reglas escritas a mano

En vez de que una persona escriba a mano todas las reglas ("si TPSA es mayor a tanto, entonces..."), se le muestran al modelo miles de ejemplos ya resueltos: miles de compuestos, cada uno con su SMILES y su etiqueta correcta conocida (BBB+ o BBB−, por ejemplo). El modelo "estudia" esos ejemplos y encuentra patrones estadísticos que relacionan la estructura con la etiqueta. Una vez entrenado, se le puede dar un compuesto **nuevo que nunca vio**, y el modelo intenta predecir su etiqueta basándose en los patrones que aprendió.

A este tipo de aprendizaje se le llama **aprendizaje supervisado**: "supervisado" porque durante el entrenamiento el modelo sí conoce la respuesta correcta de cada ejemplo (a diferencia del aprendizaje no supervisado, que busca patrones sin que nadie le diga la respuesta correcta). Y es de **clasificación** porque la respuesta que se busca es una categoría (BBB+ o BBB−), no un número continuo.

### El problema de convertir una molécula en números

Un modelo de este tipo necesita que cada ejemplo esté representado como una lista de números de **tamaño fijo** — es decir, que todas las moléculas tengan la misma cantidad de "columnas" de información, aunque sus estructuras sean muy distintas. Pero, como vimos en la sección 1, el SMILES tiene longitud variable. Hay que convertirlo en algo de tamaño fijo. A este paso se le llama **featurización**, y este proyecto usa dos técnicas complementarias:

- **Descriptores fisicoquímicos**: propiedades numéricas calculadas de la molécula, como las que ya conoces (TPSA, logP, MW, HBD, HBA) más otras parecidas. El proyecto calcula 217 de estos con una librería llamada **RDKit**; 203 quedan utilizables tras descartar los constantes, los que tienen valores faltantes y los que desbordan el rango numérico (como `Ipc`).
- **Fingerprints** (huellas digitales moleculares): una forma distinta de resumir la estructura, como un vector de miles de "sí/no" que indican la presencia o ausencia de ciertos fragmentos pequeños de la molécula. El tipo que usa este proyecto se llama **Morgan** o **ECFP**, y tiene una ventaja clave: cada posición del vector se puede rastrear de vuelta al fragmento exacto de la molécula que la activó, lo cual es esencial para la explicabilidad (sección 8).

### Por qué este proyecto no usa modelos de lenguaje tipo ChatGPT para esto

Podría pensarse que, como el SMILES es texto, convendría usar un modelo de lenguaje (como los que generan texto) directamente sobre esa cadena. Hay dos razones por las que este proyecto no lo hace: primero, exigiría rellenar o cortar las cadenas para que todas tuvieran el mismo tamaño, lo cual afecta justo a las moléculas más grandes, cuyo tamaño es información relevante. Segundo, hay evidencia comparativa directa: cuando se compararon 25 modelos de este tipo (preentrenados) contra los fingerprints clásicos, bajo las condiciones de evaluación correctas (ver sección 7), **casi ninguno mostró una mejora real**. El proyecto elige un enfoque más simple porque, con esta evidencia, no hay ganancia clara por complicarlo, y sí se gana en interpretabilidad y en costo de cómputo (estos modelos corren en una computadora normal, sin necesitar hardware especializado).

### Qué tipo de modelo se usa una vez que la molécula ya es un vector de números

El proyecto usa **modelos de ensamble** (en particular, Random Forest y XGBoost): modelos que combinan muchas decisiones simples (como muchos árboles de decisión pequeños) para llegar a una predicción más robusta que cualquiera de las decisiones individuales. Se eligieron por tres razones: funcionan bien con la cantidad de datos disponible (miles, no millones), corren rápido en una computadora normal, y —muy importante para este proyecto— permiten rastrear qué tan importante fue cada variable de entrada para una predicción concreta.

---

## 7. Por qué hay que evaluar el modelo con cuidado

Esta es, quizás, la sección más importante de toda la teoría del proyecto, porque es la fuente del error metodológico más común y más grave en este tipo de trabajos.

### El experimento mental que lo explica

Imagina que divides tus compuestos en dos grupos, "para entrenar" y "para probar si el modelo funciona", de forma completamente al azar. Ahora imagina que, por pura casualidad, varias versiones ligeramente distintas de la *misma molécula base* (lo que llamamos estereoisómeros, sección 1) terminan una en el grupo de entrenamiento y otra en el grupo de prueba. El modelo, durante el entrenamiento, básicamente "memoriza" esa estructura. Cuando luego se le pide predecir sobre la versión que quedó en el grupo de prueba, le va a ir muy bien... pero no porque haya aprendido algo generalizable sobre química, sino porque ya había visto casi la misma molécula antes. El resultado va a parecer excelente, pero es una ilusión.

Esto no es hipotético: en los datos de este proyecto, una molécula como la morfina aparece **ocho veces** en el conjunto, como distintos estereoisómeros o con nombres distintos. Y hay grupos enteros de compuestos que comparten el mismo "esqueleto" estructural (llamado **andamio**, explicado abajo) y tienen casi siempre la misma etiqueta —un grupo de 410 compuestos es 99.5% BBB+, por ejemplo—. Si el modelo solo necesita "reconocer el andamio" en vez de aprender la relación real entre estructura y permeabilidad, un split aleatorio se lo va a permitir sin que nadie se dé cuenta.

### La solución: partición por andamio (scaffold split)

Un **andamio** (en el sentido de Bemis-Murcko, los autores que definieron el concepto) es el esqueleto de anillos de una molécula y los enlaces que los conectan, sin contar los grupos que cuelgan de ese esqueleto. Dos moléculas comparten andamio si tienen el mismo sistema de anillos base, aunque tengan decoraciones distintas alrededor.

Un **scaffold split** (partición por andamio) agrupa primero todos los compuestos por su andamio, y luego reparte **andamios completos** entre entrenamiento y prueba —nunca mezclando compuestos del mismo andamio entre los dos grupos—. Esto es deliberadamente más difícil para el modelo que una partición al azar, y por una buena razón: **imita la situación real** en la que el modelo tendrá que evaluar, en el futuro, compuestos con estructuras que nunca vio durante el entrenamiento. Es exactamente el escenario en el que se va a usar el modelo cuando evalúe productos naturales nuevos.

La diferencia de resultados entre un split aleatorio y uno por andamio, medida en estudios comparativos, suele ser de **7 a 13 puntos porcentuales**: el split aleatorio infla artificialmente qué tan bueno parece el modelo. Por eso este proyecto nunca usa particiones aleatorias.

### Otros cuidados relacionados

- **También hay que verificar los estereoisómeros**, no solo los andamios: agrupar por "esqueleto de conectividad" (sección 1) asegura que distintas versiones espaciales de la misma molécula queden siempre del mismo lado de la partición.
- **El conjunto de prueba nunca se toca** durante la construcción del modelo, la elección de variables ni el ajuste de parámetros. Solo se usa al final, una vez, para medir qué tan bien funciona de verdad.
- Existe incluso el riesgo de que el modelo aprenda "atajos" que no tienen que ver con la química: por ejemplo, si ciertos laboratorios reportan solo compuestos activos y otros solo inactivos, el modelo podría aprender a reconocer el laboratorio de origen en vez de la química real. Por eso, cuando es posible, conviene que la partición también separe por fuente de los datos, no solo por andamio.

### Cómo medir si el modelo realmente funciona (no solo "qué tan seguido acierta")

Si el 63.5% de los compuestos del conjunto son BBB+, un modelo inútil que siempre responda "BBB+" sin importar la pregunta ya "acertaría" el 63.5% de las veces. Por eso medir solo la **exactitud** (porcentaje de aciertos) es engañoso cuando las clases están desbalanceadas. El proyecto usa en su lugar:

- **MCC** (coeficiente de correlación de Matthews): un número que solo es alto si el modelo acierta bien *tanto* en la clase positiva *como* en la negativa. Es mucho más difícil de "hacer trampa" con esta métrica.
- **AUPRC** (área bajo la curva de precisión-exhaustividad): más informativa que su prima más conocida, el AUROC, precisamente cuando las clases están desbalanceadas.

---

## 8. Explicabilidad: por qué no basta con que adivine bien

Los asesores del proyecto fueron claros desde la primera reunión: no quieren solo una predicción, quieren saber **qué parte de la molécula** llevó al modelo a esa predicción. A esto se le llama **explicabilidad**, y es un requisito, no un extra.

### Por qué los fingerprints (sección 6) son clave para esto

Como cada posición de un fingerprint tipo Morgan/ECFP corresponde a un fragmento concreto de la molécula, es posible preguntarle al modelo "¿qué tanto pesó esta posición en tu decisión?" y luego dibujar exactamente ese fragmento. Esto es mucho más difícil (casi imposible de forma confiable) con representaciones más abstractas, como las que produce un modelo de lenguaje.

### La herramienta principal: SHAP

**SHAP** es un método que reparte el "crédito" de una predicción entre todas las variables de entrada, basado en una idea tomada de la teoría de juegos (los valores de Shapley). Con un modelo de fingerprints, esto permite decir algo como "este bit del fingerprint, que corresponde a tal anillo químico, fue el que más empujó la predicción hacia BBB−".

Tiene límites importantes que el proyecto reconoce explícitamente: al plegar un fingerprint a un tamaño fijo, fragmentos distintos a veces terminan compartiendo la misma posición (una **colisión**), lo que obliga al modelo a darles un solo "peso" aunque tengan efectos opuestos en la realidad. Y, sobre todo: que una variable sea importante *para el modelo* no significa automáticamente que sea la causa biológica real del efecto. Es una pista fuerte, no una prueba.

### La regla del proyecto: no confiar en un solo método

Como ningún método de explicabilidad es perfecto por sí solo, el proyecto usa **al menos dos métodos independientes** y solo reporta como confirmados los fragmentos en los que ambos coinciden. También se entrena, en paralelo, un modelo más simple que es interpretable *por diseño* (no necesita un método externo para explicarse), como punto de control.

### El sanity check obligatorio

Antes de aceptar cualquier explicación nueva que dé el modelo, se contrasta contra lo que ya se sabe que domina empíricamente: TPSA bajo (< 67 Å²) y pocos donadores de puente de hidrógeno (HBD ≤ 1). Si una explicación del modelo contradice esto sin una buena razón, es señal de que hay que revisar el modelo antes de creerle, no de que se descubrió algo nuevo.

---

