# Guía del proyecto Bioactive AI — desde cero

> Esta guía está pensada para leerse de principio a fin la primera vez, no solo para consultar. Empieza explicando la teoría (biología, química, inteligencia artificial) sin dar nada por sabido, y hasta que esa base está lista entra al proyecto en sí. Al final hay un **glosario** con todos los términos técnicos, por si quieres buscar uno suelto después. Se armó leyendo el README, `CLAUDE.md`, las notas de la reunión, el marco teórico, `docs/referencias/`, el Avance 0, los notebooks y el código de `src/`. Los números vienen de ahí; donde algo no se verificó, se dice explícitamente. **Última verificación contra los datos y los documentos del repositorio: 7 de octubre de 2026.** Para el estado de cada decisión y lo que sigue abierto, la fuente es [`decisiones.md`](decisiones.md); para los términos, [`glosario.md`](glosario.md). Esta guía explica y orienta, no sustituye a esos dos.

## Índice

**Parte 1 — Teoría, desde cero**
1. [¿Qué es una molécula y cómo se "escribe"?](#1-qué-es-una-molécula-y-cómo-se-escribe)
2. [El obstáculo central: la barrera hematoencefálica](#2-el-obstáculo-central-la-barrera-hematoencefálica)
3. [Las reglas que predicen si algo cruza](#3-las-reglas-que-predicen-si-algo-cruza)
4. [Enfermedades del cerebro y qué significa "neuroprotección"](#4-enfermedades-del-cerebro-y-qué-significa-neuroprotección)
5. [Productos naturales como fuente de medicamentos](#5-productos-naturales-como-fuente-de-medicamentos)
6. [Cómo "aprende" una inteligencia artificial de esto](#6-cómo-aprende-una-inteligencia-artificial-de-esto)
7. [Por qué hay que evaluar el modelo con cuidado](#7-por-qué-hay-que-evaluar-el-modelo-con-cuidado)
8. [Explicabilidad: por qué no basta con que adivine bien](#8-explicabilidad-por-qué-no-basta-con-que-adivine-bien)

**Parte 2 — El proyecto**
9. [Quiénes son y qué problema resuelven](#9-quiénes-son-y-qué-problema-resuelven)
10. [La pregunta central y las dos etapas](#10-la-pregunta-central-y-las-dos-etapas)
11. [Reglas de diseño que no se negocian](#11-reglas-de-diseño-que-no-se-negocian)
12. [Cómo se organiza el trabajo (metodología y calendario)](#12-cómo-se-organiza-el-trabajo-metodología-y-calendario)

**Parte 3 — Los datos, a fondo**
13. [Los datos de la etapa 1: permeabilidad (B3DB)](#13-los-datos-de-la-etapa-1-permeabilidad-b3db)
14. [Los datos de la etapa 2: actividad en el sistema nervioso](#14-los-datos-de-la-etapa-2-actividad-en-el-sistema-nervioso)
15. [De dónde viene cada cosa y qué licencia tiene](#15-de-dónde-viene-cada-cosa-y-qué-licencia-tiene)
16. [Problemas de calidad ya encontrados en los datos](#16-problemas-de-calidad-ya-encontrados-en-los-datos)

**Parte 4 — El trabajo técnico**
17. [Decisiones técnicas ya tomadas, y por qué](#17-decisiones-técnicas-ya-tomadas-y-por-qué)
18. [Estado actual del repositorio](#18-estado-actual-del-repositorio)
19. [Trampas y advertencias para no repetir errores](#19-trampas-y-advertencias-para-no-repetir-errores)
20. [Pendientes y preguntas abiertas](#20-pendientes-y-preguntas-abiertas)

**[Glosario](#glosario)** — todos los tecnicismos, en un solo lugar.

---

# Parte 1 — Teoría, desde cero

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

El InChIKey tiene 27 caracteres. Sus primeros 14 caracteres codifican únicamente el **esqueleto de conectividad**: la estructura de la molécula ignorando los detalles de cómo están acomodados sus átomos en el espacio (lo que se llama **estereoquímica**). Esto importa porque una misma molécula puede tener varias versiones que solo difieren en ese acomodo espacial —se llaman **estereoisómeros**— y dos estereoisómeros pueden comportarse de forma biológicamente distinta aunque compartan fórmula y conectividad. Vas a ver que este detalle tiene consecuencias reales en los datos (la sección 16 trae ejemplos).

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

Una **diana** (en inglés *target*) es la proteína específica sobre la que un compuesto actúa para producir su efecto. Por ejemplo, si un compuesto inhibe a la proteína que fabrica una enzima dañina, esa proteína es la diana del compuesto. El proyecto trabaja con **37 dianas identificadas por gen más 2 receptores completos** (39 filas en el archivo de etiquetas), curadas a mano por la patrocinadora, cada una asociada a alguno de estos mecanismos de enfermedad. Más adelante (sección 14) se explica cómo están organizadas.

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

# Parte 2 — El proyecto

Ya con la teoría de la Parte 1, esta parte explica qué hace exactamente Bioactive AI, quién participa y cómo está organizado el trabajo.

## 9. Quiénes son y qué problema resuelven

**El proyecto.** Bioactive AI es el Proyecto Integrador (TC5035.10) de la Maestría en Inteligencia Artificial Aplicada del Tec de Monterrey, hecho por el **Equipo 7**: Ingrid Pamela Ruiz Puga, Artemio Santiago Padilla Robles y José Antonio Vázquez Martínez.

**Profesora titular y patrocinadora.** Son dos personas con dos roles distintos. La **Dra. Grettel Barceló Alonso** es la profesora titular del curso y evalúa las entregas. La **Dra. Mariana Martínez Ávila**, del Departamento de Bioingeniería, es la patrocinadora: la investigadora que plantea el problema real y entregó los datos.

**El proceso de trabajo que el proyecto quiere mejorar.** Hoy, el laboratorio de la Dra. Martínez identifica candidatos a medicamentos neuroprotectores en tres pasos: (1) revisan literatura científica y bases de datos buscando compuestos reportados con alguna actividad interesante, (2) eligen, con su criterio experto, cuáles vale la pena ensayar, y (3) los prueban en el laboratorio. Este proceso tiene tres límites reales:

- **El espacio de búsqueda es gigantesco.** Solo una base de datos de productos naturales (COCONUT) tiene 738,829 moléculas distintas. Revisarlas una por una a mano no es viable.
- **La barrera hematoencefálica descarta a la mayoría de los candidatos** (sección 2), y comprobar eso experimentalmente para cada compuesto es costoso.
- **La tasa histórica de éxito es muy baja** (sección 4): la mayoría de lo que funciona en el laboratorio nunca funciona como medicamento real. Priorizar mejor antes de invertir en experimentos no es un detalle menor: es el principal cuello de botella del campo.

## 10. La pregunta central y las dos etapas

**La pregunta que responde el proyecto:** dado solamente el SMILES de un compuesto, ¿se puede predecir si llegará al cerebro, si tendrá actividad neuroprotectora, y explicar qué característica estructural sustenta esa predicción?

Esto se divide en dos etapas, ambas recibiendo el mismo SMILES como entrada. El equipo las plantea como **independientes**; ese planteamiento está pendiente de confirmar con la patrocinadora (decisión 5 del registro):

```
SMILES ──► vector de longitud fija ──┬─► Etapa 1: ¿cruza la barrera hematoencefálica? (BBB+ / BBB−)
        (descriptores + fingerprint) │
                                     └─► Etapa 2: ¿es activo sobre alguna de las 37 + 2 dianas de neuroprotección?
                                                   │
                                                   └─► Priorización final + atribución a subestructuras
```

**El punto de diseño más importante de entender:** la etapa 1 **no filtra** a la etapa 2. Un compuesto que sale BBB− no se descarta del análisis, porque existen estrategias conocidas de química farmacéutica para ayudar a un compuesto a cruzar después (convertirlo en un profármaco, modificarlo para que sea menos polar, usar nanopartículas transportadoras, etc.). Y el dato que lo cierra: solo 1,033 esqueletos tienen medición en los dos conjuntos, así que para el 99% restante la permeabilidad sería una **predicción sin verificar** — descartar con ella eliminaría candidatos con actividad real documentada. Por eso las salidas de ambas etapas se calculan y se conservan por separado, y solo se combinan al final, al momento de decidir qué candidatos priorizar. Lo que los datos respaldan con firmeza es que un BBB− no descarta al compuesto: solo 1,033 esqueletos tienen medición en los dos conjuntos, así que para el resto la permeabilidad sería una predicción sin verificar.

## 11. Reglas de diseño que no se negocian

Estas ideas aparecieron desde la primera reunión con los asesores y condicionan cada decisión técnica del proyecto:

- **La explicabilidad es un requisito, no un extra** (sección 8). Sin poder decir *qué fragmento* de la molécula sustenta una predicción, el resultado no le sirve al laboratorio.
- **"No encontramos ningún patrón aprendible" es un resultado válido.** En la primera reunión se planteó que incluso no encontrar un patrón puede ser un buen resultado: se prefiere un resultado negativo honesto a un modelo forzado para que se vea bien. Dado el historial de fracasos del campo (sección 4), reportar la ausencia de señal con rigor es, en sí mismo, un aporte.
- **La actividad depende de la concentración** (sección 2, para la permeabilidad, y también aplica a la actividad biológica en general): el mismo compuesto puede pasar de "inactivo" a "activo" simplemente subiendo la dosis probada. El proyecto tiene que elegir y documentar un umbral de concentración para convertir mediciones en etiquetas binarias, y ser transparente sobre esa elección.

## 12. Cómo se organiza el trabajo (metodología y calendario)

El curso pide seguir la metodología **CRISP-ML(Q)**, un marco de trabajo por fases para proyectos de machine learning con control de calidad en cada paso, y usa los **5 principios de la OCDE** para validar modelos de este tipo (endpoint definido, algoritmo inequívoco, dominio de aplicabilidad, bondad de ajuste y predictividad, e interpretación mecanística) como lista de verificación final.

El trabajo se entrega en avances semanales (ver `docs/Entregas_canvas.md` para el detalle completo de fechas y rúbricas):

| Avance | Qué es | Fecha |
|---|---|---|
| 0 | Propuesta del proyecto | 27 de septiembre |
| 1 | Análisis exploratorio de datos (EDA) | 4 de octubre |
| 2 | Ingeniería de características y partición de los datos | 11 de octubre |
| 3 | Modelo de referencia (baseline) | 18 de octubre |
| 4 | Modelos alternativos | 25 de octubre |
| 5 | Modelo final | 1 de noviembre |

---

# Parte 3 — Los datos, a fondo

Esta es la parte que pediste profundizar más. El proyecto trabaja con **dos conjuntos de datos completamente distintos**, uno por cada etapa.

## 13. Los datos de la etapa 1: permeabilidad (B3DB)

### De dónde viene

La fuente es **B3DB** (*Blood-Brain Barrier Database*), una base de datos que reúne mediciones de permeabilidad compiladas de 50 conjuntos de datos publicados. Se eligió, entre otras cosas, porque su licencia (**CC0**, dominio público) permite guardarla directamente en el repositorio sin restricciones.

La patrocinadora entregó una versión ya procesada de B3DB (`data/external/profesora/bbb_permeability_experimental.csv`), con el SMILES ya estandarizado, un cruce con **COCONUT** (el catálogo de productos naturales, lo que permite saber cuáles de estos compuestos son naturales) y la información de clasificación y de valor numérico ya unidas en un solo archivo.

### Cómo está estructurado

| Dato | Valor |
|---|---|
| Filas totales | 7,811 (7,805 con clase asignada) |
| BBB+ / BBB− | 4,956 (63.5%) / 2,849 (36.5%) — una razón de casi 1.74 a 1 |
| Con valor numérico de logBB (en el conjunto con clase) | 1,052 |
| Esqueletos de conectividad distintos | **4,018** (en las 7,805 filas con clase) |
| Con equivalente exacto en COCONUT (es decir, producto natural confirmado) | 3,366 filas |

La fila "esqueletos de conectividad distintos" es la más importante de entender bien: aunque hay 7,805 filas, solo hay 4,018 moléculas realmente distintas si ignoras la estereoquímica (sección 1). **Casi la mitad de las filas son, en el fondo, una repetición de otra fila** (la misma molécula base, escrita o medida de otra forma). Cuando se reporte el tamaño de este conjunto, siempre hay que dar las dos cifras, nunca solo "7,805 compuestos", porque eso sobreestima cuánta información realmente independiente hay.

> **Corrección importante (4 de octubre de 2026).** Las dos filas de abajo —el sistema de grupos y el hallazgo de productos naturales— se corrigieron después de una revisión a fondo del equipo. La versión anterior de esta guía tenía un error real: decía que el grupo D significaba "etiquetas contradictorias", y dejaba sin resolver si había que filtrar por A+B. Ambas cosas eran incorrectas, y se explican abajo tal como quedaron verificadas. Ver la sección 19 para la lección completa de por qué pasó esto.

### El sistema de grupos de confiabilidad (A, B, C, D)

B3DB clasifica cada fila en uno de cuatro grupos. **No son una escala de calidad de mejor a peor**, y B3DB no publica el criterio completo con que los asigna:

- **A** (1,058 filas): casi todos tienen un valor numérico de logBB medido (1,052 de las 1,058).
- **B** (3,621 filas): las fuentes originales declararon explícitamente el umbral −1 y coincidieron en la etiqueta resultante.
- **C** (3,075 filas): las fuentes coinciden en la etiqueta, pero ninguna declaró qué umbral usó; mediana de **una** referencia bibliográfica.
- **D** (51 filas): igual que C (sin valor ni umbral), pero con mediana de **tres** referencias bibliográficas — es decir, **más** respaldo que C, no etiquetas contradictorias. (La lectura de "D = contradictorias" que tenía esta guía antes era un error: al revisar los duplicados exactos del archivo, ninguno tiene etiquetas en conflicto.)

La frecuencia de BBB− sí varía mucho entre grupos (12.1% en A, 31.3% en B, 50.0% en C, 92.2% en D), lo que confirma que el grupo está **asociado** con la etiqueta. Y ahí está la trampa: si filtras el conjunto a solo A+B, la clase minoritaria (BBB−) baja de 36.5% a **27.0%** — es decir, **filtrar empeora el desbalance de clases en vez de limpiar ruido**. Por eso la decisión final del proyecto es: **nunca filtrar por `group`**, usarlo solo para describir y para estratificar el análisis.

### Un hallazgo importante: los productos naturales cruzan menos

Gracias al cruce con COCONUT que trae el archivo de la patrocinadora, se puede comparar directamente cómo se comportan los productos naturales contra los sintéticos:

| Grupo | Compuestos | % BBB+ |
|---|---|---|
| Sin equivalente natural exacto (incluye análogos) | 4,439 | 71.7% |
| **Productos naturales** (estructura idéntica en COCONUT) | **3,366** | **52.7%** |

**Ojo con la etiqueta «sintético».** El diccionario de la patrocinadora distingue tres categorías: 3,366 productos naturales exactos, 1,005 análogos que difieren solo en la estereoquímica y 3,440 sin equivalente natural conocido. La fila de arriba mezcla las dos últimas, así que no todos son sintéticos en sentido estricto.

Las dos cifras no cuadran por una razón que conviene decir: **1,005 + 3,440 = 4,445, no 4,439**. Las tres categorías del diccionario cuentan sobre las 7,811 filas del archivo y la tabla de arriba sobre las 7,805 con clase. Los 6 de diferencia son las filas sin etiqueta. Toda cifra por origen debe declarar su base, y esta nota es el ejemplo de lo fácil que es olvidarlo.

Los productos naturales exactos cruzan la barrera **19 puntos porcentuales menos** que los del otro grupo. Esto importa muchísimo porque los productos naturales son justo lo que el proyecto quiere priorizar. La regla fisicoquímica clásica (TPSA < 67 Å² y HBD ≤ 1, sección 3) solo explica una fracción pequeña de esa diferencia —unos 6.6 de los 19 puntos—, así que hay algo más en juego (posiblemente eflujo activo, o un sesgo en qué compuestos se han llegado a ensayar) que el modelo tendrá que poder capturar. Consecuencia práctica: **el desempeño del modelo se tiene que reportar por separado para naturales y sintéticos**, porque un buen número global podría estar escondiendo que le va peor justo en los compuestos que importan.

## 14. Los datos de la etapa 2: actividad en el sistema nervioso

### De dónde viene y qué tan grande es

El archivo (`snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv`) combina tres fuentes distintas: **ChEMBL** (una base de datos de bioactividad de moléculas tipo fármaco), **NPASS** y **CMAUP** (ambas especializadas en productos naturales). Pesa 74 MB y se guarda en el repositorio usando **Git LFS**, un sistema para versionar archivos grandes sin inflar el historial de git.

| Dato | Valor |
|---|---|
| Registros de actividad (filas) | 202,647 |
| Compuestos únicos (por InChIKey) | 105,583 |
| De ChEMBL | 103,877 |
| De NPASS y CMAUP (productos naturales) | 4,472 |
| En ambos grupos a la vez | 2,766 |
| Registros con una medida de potencia (pChEMBL) | 129,243 |
| Registros de inactividad declarada | 29,730 |

**Un detalle sobre "registros" contra "compuestos":** cada fila es una *medición* (un compuesto, probado contra una diana, en un ensayo concreto), no necesariamente un compuesto distinto. Un mismo compuesto puede aparecer muchas veces, probado contra dianas distintas o en ensayos distintos.

### Las dianas: 37 por gen y 2 receptores completos

Como se explicó en la sección 4, una **diana** es la proteína específica sobre la que actúa un compuesto. Las 39 filas del archivo de etiquetas fueron curadas a mano por la patrocinadora, y se agrupan en cuatro categorías:

- **SNC clásico** (20 dianas): incluye, entre otras, la acetilcolinesterasa (AChE, relacionada con la hipótesis colinérgica), la monoamino oxidasa B (relacionada con Parkinson), GSK-3β y tau (Alzheimer).
- **Neuroinflamación** (10 dianas): COX-2, el inflamasoma NLRP3, entre otras.
- **Parkinson / ELA / Huntington** (7 dianas): incluye la α-sinucleína (SNCA) y LRRK2.
- **Receptores completos** (2): el receptor GABA-A y el receptor NMDA, registrados sin distinguir entre sus distintas subunidades.

### Qué tan "limpio" está este archivo en realidad (verificado contra los datos)

Esto es importante porque condiciona qué tan listo está el archivo para entrenar un modelo directamente:

- **Son 37 dianas identificadas por gen y 2 receptores completos**, y la cobertura es muy desigual: `GABRG2` y `AIF1` tienen **0 filas** en nuestro archivo, `GABRB2` tiene 1 y `TARDBP` 7 (8 en el archivo completo del diccionario). Por categoría de enfermedad, Alzheimer reúne 52,676 registros y ELA solo 53. No se puede entrenar un modelo confiable con tan pocos ejemplos; se propone excluir esas cuatro dianas y decidir cuáles de las demás se modelan (decisiones 13 y 17).
- **El 43.5% de las filas (88,098) no corresponde a ninguna de las dianas de la lista.** Entraron por la ruta `neuronal_assay`: son ensayos fenotípicos sobre sistemas celulares neuronales, donde se midió un efecto sin identificar la proteína responsable. Es otro tipo de evidencia. Se propone entrenar con los 114,549 registros que sí tienen diana y conservar estos aparte (decisión 14).
- **NPASS y CMAUP —justo la fuente de los productos naturales, el objetivo final del proyecto— no traen pChEMBL** (15,293 registros). Esa medida solo la calcula ChEMBL. Etiquetar únicamente por pChEMBL dejaría fuera esas dos bases, por lo que se propone etiquetar por tres vías: pChEMBL donde exista, concentración exacta para el resto (que recupera 12,809 de los 15,293) e inactivo declarado para los textos y los censurados con límite suficiente. Es la decisión 7, pendiente de ratificar por la patrocinadora.
- **Las unidades de medición no están convertidas a una sola escala**: la mayoría está en nanomolar (nM), pero hay 29,880 registros en micromolar (µM) y 662 en unidades de masa (µg/mL y similares), que no se pueden convertir a una concentración molar sin conocer el peso molecular exacto de cada compuesto.
- **Algunas mediciones son "censuradas"**: dicen, por ejemplo, "mayor a 10 µM" en vez de dar un número exacto (54,498 registros sin pChEMBL). Es un límite, no un valor medido. **Solo sirve como negativo si su límite es igual o mayor que el umbral de «activo» que se use.** La tabla del diccionario de la patrocinadora, sobre 61,001 filas con `>`: con un umbral de 1 µM, 59,859 son negativos seguros (98%) y 1,142 ambiguos; con 10 µM, 54,419 (89%) y 6,582; con 100 µM, 7,474 (12%) y 53,527. Cuanto más estricto el umbral, más censurados se recuperan como negativos seguros y menos quedan ambiguos.
- Las etiquetas sobre qué hace cada diana (su mecanismo, el efecto que se busca) **fueron curadas a mano por la patrocinadora**, no vienen de las bases de datos originales, y describen la intención terapéutica —no necesariamente lo que ocurrió específicamente en cada ensayo—.

## 15. De dónde viene cada cosa y qué licencia tiene

Esto importa porque algunas licencias limitan qué se puede hacer con los datos más adelante (por ejemplo, si el proyecto tuviera uso comercial):

| Fuente | Para qué se usa | Licencia |
|---|---|---|
| B3DB | Etapa 1 (permeabilidad) | CC0 (dominio público) |
| COCONUT | Identificar cuáles compuestos son productos naturales | CC0 |
| ChEMBL | Etapa 2 (actividad) | CC BY-SA 3.0 (requiere dar crédito) |
| NPASS | Etapa 2, productos naturales | **CC BY-NC 4.0 — uso no comercial únicamente** |
| CMAUP | Etapa 2, plantas medicinales | CC BY del artículo original; los términos de la base no están confirmados |
| Spielvogel et al. 2025 | Conjunto de validación externa | CC BY 4.0 |

Un proyecto académico como este cumple perfectamente con todas estas licencias. La única que requeriría revisión es NPASS, si el proyecto alguna vez tuviera una continuación con fines comerciales.

## 16. Problemas de calidad ya encontrados en los datos

Esta lista es el resultado de auditar los datos a fondo, no suposiciones. Vale la pena conocerla antes de tocar los datos para no repetir errores ya identificados:

- **El tamaño real es más chico de lo que sugiere el número de filas**, como ya se explicó: 7,805 filas de permeabilidad son, en realidad, 4,018 moléculas distintas (4,019 contando las 7,811 filas).
- **Los nombres de los compuestos no son confiables.** Hay un caso verificado: una fila llamada «ritonavir» tiene la estructura del etambutol (hay cinco filas con ese nombre y cuatro esqueletos distintos). Por eso la regla es siempre identificar compuestos por su InChIKey recalculado, **nunca por el nombre ni por el texto del SMILES**.
- **Los 7,811 SMILES del archivo de la patrocinadora sí son válidos, todos.** Solo en los archivos crudos de B3DB (la referencia de verificación, no la fuente principal) hay 2 SMILES inválidos —mepenzolato y tiotidina, con una carga de carbono imposible— que la patrocinadora ya excluyó al curar su archivo. No es un problema del conjunto que se usa para modelar.
- **131 esqueletos (grupos de estereoisómeros) tienen etiquetas contradictorias entre sí**: un estereoisómero sale BBB+ y otro BBB−. Esto afecta a 429 filas en total, y hay que decidir si tratarlo como un caso genuino de "la forma exacta de la molécula importa" o como un error de etiquetado. Calculamos que, aun así, el techo de exactitud es 98.1% (151 errores inevitables de 7,805), así que no limita al modelo. Para el logBB, 112 esqueletos tienen más de una medición y **40 de ellos valores distintos**, con diferencias de hasta 1.4 unidades. El diccionario dice «más de un valor», pero 72 de los 112 repiten el mismo número.
- El conjunto de validación externa (Spielvogel et al.) **no trae SMILES ni ningún identificador químico**, solo el nombre del compuesto. Hay que resolver esos 154 nombres a una estructura química (por ejemplo, consultando la base de datos pública PubChem) antes de poder usarlo. El CSV separa las columnas con punto y coma y trae una tercera clase, «eflujo» (44 de los 154), que no es BBB+ ni BBB−.

---

# Parte 4 — El trabajo técnico

## 17. Decisiones técnicas ya tomadas, y por qué

Esta tabla resume decisiones de diseño, apoyadas en la teoría de la Parte 1. El contexto, las alternativas descartadas y el estado de cada una (algunas están pendientes de ratificar por la patrocinadora) están en [`decisiones.md`](decisiones.md):

| Decisión | Por qué |
|---|---|
| Usar descriptores RDKit (217, de los que 203 son utilizables) + fingerprints Morgan/ECFP4 (2,048 bits) | Son interpretables, trazables a un fragmento concreto, y corren rápido en CPU. La evidencia comparativa no muestra ventaja real de representaciones más complejas bajo evaluación correcta (sección 6 y 7). |
| Partición por andamio de Bemis-Murcko, nunca aleatoria | Evita la fuga de información explicada en la sección 7; un split aleatorio infla los resultados entre 7 y 13 puntos. |
| Los andamios grandes (frecuentes) van a entrenamiento, los raros a prueba | Así la prueba mide generalización real a química poco común, que es el escenario en el que se usará el modelo con productos naturales nuevos. |
| Etapa 2: etiquetado por tres vías (pChEMBL, concentración exacta e inactivo declarado), con corte en pChEMBL ≥ 5 y ≥ 6 como comprobación de robustez | pChEMBL 5 equivale a 10 µM y 6 a 1 µM. Etiquetar solo por pChEMBL dejaría fuera los productos naturales de NPASS y CMAUP. Un censurado solo cuenta como negativo si su límite es igual o mayor que el umbral usado, y el umbral no se elige por el balance de clases, que depende de qué registros se miren. Pendiente de ratificar por la patrocinadora (decisión 7). |
| Modelos de ensamble (Random Forest, XGBoost), no deep learning | Evidencia comparable, menor costo, e interpretabilidad directa (sección 6). |
| Al menos dos métodos de atribución independientes, reportando solo donde coinciden | El desacuerdo entre métodos de explicabilidad es la norma, no la excepción (sección 8). |
| Métricas principales: MCC y AUPRC, no exactitud | El desbalance de clases hace que la exactitud sea engañosa (sección 7). |
| Construir un baseline propio, sin usar cifras publicadas como meta | Los valores publicados para el mismo conjunto de datos varían mucho según quién los reporte y cómo implementó la partición. |
| Contrastar toda explicación del modelo contra TPSA < 67 Å² y HBD ≤ 1 | Son las reglas que dominan empíricamente (sección 3); una explicación que las contradiga sin razón es sospechosa. |

## 18. Estado actual del repositorio

El proyecto ya tiene trabajo real hecho, no es solo una estructura vacía:

| Avance | Entregable | Estado (7 de octubre de 2026) |
|---|---|---|
| 0 | Propuesta del proyecto | Entregado (PDF) |
| 1 | Análisis exploratorio de datos (`notebooks/01_EDA.ipynb`) | Entregado el 4 de octubre |
| — | EDA de la etapa 2 (`notebooks/01b_EDA_actividad_snc.ipynb`) | Hecho; acompaña al Avance 1 y no es un entregable |
| 2 | Ingeniería de características (`notebooks/02_Feature_Eng.ipynb`) | Notebook ejecutado; la normalización y la selección de características están en revisión; falta el reporte · vence el 11 de octubre |
| 3 | Modelo de referencia (baseline) | Pendiente · vence el 18 de octubre |
| 4–5 | Modelos alternativos y modelo final | Pendiente |

**Resultado ya obtenido de la partición por andamio** (Avance 2, sobre las 7,805 filas con clase, **sin filtrar por `group`** — ver sección 13 sobre por qué ya no se filtra):

| Partición | Compuestos | Andamios distintos | % BBB+ |
|---|---|---|---|
| Entrenamiento | 5,557 | 1,741 | 64.0% |
| Validación | 749 | 498 | 72.0% |
| Prueba | 1,499 | 1,390 | 57.3% |

Se verificó que cero andamios y cero esqueletos de conectividad se repiten entre particiones distintas, que es justo lo que se busca con un scaffold split bien hecho. La prueba queda con menos BBB+ que el entrenamiento (57.3% contra 64.0%) porque los andamios raros —los que le tocan a la prueba— son menos permeables que los frecuentes; es una característica esperada del scaffold split, no un error, y no se corrige.

## 19. Trampas y advertencias para no repetir errores

1. Nunca reportar el tamaño del conjunto de permeabilidad solo como "7,805 filas"; siempre acompañarlo del número real de moléculas distintas (4,018).
2. Nunca deduplicar ni cruzar bases de datos usando el nombre del compuesto o el texto del SMILES; usar siempre el InChIKey recalculado.
3. Al concatenar los archivos de B3DB, hay 11 filas duplicadas que hay que quitar primero.
4. Cualquier umbral (como el de TPSA) debe calcularse **solo con los datos de entrenamiento**, nunca con todo el conjunto, o se estaría usando información de la prueba de forma indebida.
5. Los grupos A–D de B3DB no son una escala simple de calidad; no hay que tratarlos como tal sin justificación.
6. La etiqueta BBB+/BBB− no es una propiedad fija del compuesto (sección 2); un resultado BBB− no descarta un candidato.
7. Desconfiar de resultados muy favorables para compuestos de la familia de la curcumina y similares (sección 5); aplicar filtros PAINS antes de reportar un candidato.
8. **Usar siempre el archivo de la patrocinadora** (`data/external/profesora/bbb_permeability_experimental.csv`) como fuente de la etapa 1, no los archivos de B3DB que el equipo descargó por su cuenta. Esos quedan solo como verificación cruzada de conteos (ver recuadro abajo, es justo el error que ya cometimos una vez).
9. Un registro censurado de actividad (`> X nM`) solo sirve como negativo si su límite es igual o mayor que el umbral de «activo» que se use; la regla se aplica por umbral, no con un corte fijo.
10. No elegir el umbral de actividad por el balance de clases que deja: ese balance cambia según qué registros se miren (todos, solo con pChEMBL, solo con diana, por par compuesto-diana), y lo que justifica el corte es la concentración.
11. Las cifras de los diccionarios de la patrocinadora son del archivo completo (225,513 filas de actividad); el que recibimos tiene 202,647, el 89.9%. Hay que decir cuál se usa en cada cifra.

> ### Qué pasó el 4 de octubre, y por qué no se puede repetir
>
> El Avance 1 original (y esta guía, en su primera versión) se construyó sobre los archivos de B3DB descargados directamente por el equipo, no sobre el archivo curado de la patrocinadora. Con esos datos "crudos" se llegó a dos conclusiones que resultaron **falsas** al revisarlas contra el archivo correcto: que el grupo D significaba "etiquetas contradictorias", y que había 2 SMILES inválidos en el conjunto de trabajo. Ninguna de las dos era cierta en los datos reales del proyecto — eran artefactos de usar el archivo equivocado.
>
> Peor todavía: sobre esa base equivocada, el Avance 2 adoptó un filtro (quedarse solo con los grupos A+B) que **empeoraba el desbalance de clases** en vez de mejorar la calidad de los datos, y nadie lo cuestionó a fondo durante varios días, porque la premisa de la que partía (que el grupo D era ruido) sonaba razonable y nadie la verificó contra el archivo correcto.
>
> El equipo lo detectó y lo corrigió el 4 de octubre: se re-centró el Avance 1 en el archivo de la patrocinadora, se quitó el filtro A+B del Avance 2, y se corrigió `CLAUDE.md`. De paso salió un hallazgo real y útil (la brecha de permeabilidad entre naturales y sintéticos, sección 13).
>
> **La lección, para que no se repita:** cuando exista un archivo "oficial" entregado por quien patrocina el proyecto y una versión descargada por el propio equipo, **el archivo oficial manda siempre**, y cualquier análisis nuevo se verifica contra él antes de construir más cosas encima. Si algo que parece una verdad establecida (como "el grupo D son etiquetas contradictorias") nunca se contrastó directamente contra el archivo oficial, no se trata como un hecho: se marca como pendiente de verificar y se resuelve antes de seguir construyendo, no después.

## 20. Pendientes y preguntas abiertas

Lo abierto vive en dos sitios, y esta guía no los duplica: las **decisiones**, con su estado y quién decide, en [`decisiones.md`](decisiones.md), y la **consulta a la patrocinadora** en [`consulta-patrocinadora.md`](consulta-patrocinadora.md). El trabajo pendiente vive en los issues de GitHub, etiquetados por el avance que bloquean.

Las preguntas que más cambian cómo se construye el modelo, a la fecha:

- Qué criterio de «activo» usa la patrocinadora en la etapa 2 (decisión 7).
- Un modelo por diana, por categoría de enfermedad o multitarea (decisión 13).
- Reservar o no los 1,033 compuestos con medición en las dos etapas (decisión 10): cuesta el 25.7% de los datos de la etapa 1.
- Modelos separados para naturales y sintéticos, o el origen como variable.
- Si el archivo de actividad, que recibimos con el 89.9% de las filas, ya trae una partición de prueba reservada y cómo se hizo.

**Pendientes técnicos del equipo:** el reporte del Avance 2, el notebook del Avance 3 (baseline) y resolver los 154 nombres del conjunto de Spielvogel a estructuras químicas.

---

# Glosario

Los términos técnicos que aparecen en esta guía, para consultar rápido. La versión canónica, que es la que se mantiene al día, es [`glosario.md`](glosario.md).

| Término | Significado |
|---|---|
| **AChE / BuChE** | Acetilcolinesterasa / butirilcolinesterasa; enzimas relacionadas con la hipótesis colinérgica del Alzheimer |
| **Amiloide-β (Aβ)** | Fragmento de proteína que se acumula en placas en el cerebro de pacientes con Alzheimer |
| **Andamio (scaffold, Bemis-Murcko)** | El esqueleto de anillos de una molécula y los enlaces que los conectan, sin los grupos que cuelgan de él |
| **AUC / AUROC** | Área bajo la curva ROC; mide qué tan bien algo separa dos clases (0.5 = azar, 1.0 = perfecto) |
| **AUPRC** | Área bajo la curva de precisión-exhaustividad; más informativa que el AUROC cuando las clases están desbalanceadas |
| **BBB / BHE** | Barrera hematoencefálica (*blood-brain barrier*), el filtro de células que protege al cerebro |
| **BBB+ / BBB−** | Cruza / no cruza la barrera hematoencefálica (una clasificación que depende de las condiciones del experimento, no una propiedad fija) |
| **ChEMBL** | Base de datos pública de bioactividad de moléculas tipo fármaco |
| **CMAUP** | Base de datos de plantas medicinales y sus compuestos |
| **COCONUT** | Catálogo abierto de productos naturales |
| **Compuesto / molécula** | Una sustancia química definida por cómo están unidos sus átomos |
| **Descriptor fisicoquímico** | Una propiedad numérica calculada de una molécula (ej. TPSA, logP, peso molecular) |
| **Diana (target)** | La proteína específica sobre la que actúa un compuesto para producir su efecto |
| **Difusión pasiva** | Ruta por la que una molécula atraviesa una célula sin ayuda de ningún mecanismo biológico |
| **Eflujo activo** | Mecanismo por el que una "bomba" celular expulsa de vuelta a la sangre un compuesto que ya había entrado al cerebro |
| **Esqueleto de conectividad** | La estructura de una molécula ignorando su disposición espacial (estereoquímica); los primeros 14 caracteres del InChIKey |
| **Featurización** | Convertir una molécula (de tamaño variable, como el SMILES) en un vector de números de tamaño fijo |
| **Fingerprint (Morgan / ECFP)** | Una representación de la molécula como un vector de "presente/ausente" para miles de fragmentos pequeños |
| **Glicoproteína-P (P-gp)** | La bomba de eflujo más importante en la barrera hematoencefálica |
| **HBD / HBA** | Donadores / aceptores de puente de hidrógeno de una molécula |
| **InChIKey** | Identificador químico estándar calculado desde la estructura real de una molécula; siempre igual para la misma molécula |
| **logBB** | Logaritmo de la razón entre la concentración de un compuesto en el cerebro y en la sangre |
| **logP** | Medida de qué tan lipofílica (amiga de la grasa, en vez del agua) es una molécula |
| **MCC** | Coeficiente de correlación de Matthews; métrica que exige acertar bien tanto en positivos como en negativos |
| **MW** | Peso molecular |
| **Neuroinflamación** | Inflamación del cerebro causada por sus propias células inmunes |
| **Neuroprotección** | Reducir el daño o la muerte de neuronas causada por una enfermedad; debe hablarse siempre como "predicha según mecanismo", no como un hecho confirmado |
| **NPASS** | Base de datos de actividad biológica de productos naturales |
| **PAINS** | Compuestos que dan resultados positivos falsos en experimentos, por interferencia en vez de actividad biológica real |
| **Parkinson, α-sinucleína** | Enfermedad neurodegenerativa; la α-sinucleína es la proteína que se agrega de forma anormal en ella |
| **pChEMBL** | Medida estándar de potencia de un compuesto; más alto significa más potente |
| **Producto natural** | Compuesto producido por un organismo vivo, no fabricado sintéticamente |
| **QSAR** | Relación cuantitativa entre la estructura de un compuesto y su actividad biológica |
| **RDKit** | Librería de software usada para calcular descriptores y fingerprints a partir de SMILES |
| **Scaffold split** | Partición de los datos que agrupa por andamio, para evitar que el modelo "memorice" en vez de aprender |
| **SHAP** | Método para explicar qué tanto pesó cada variable en una predicción del modelo |
| **SMILES** | Cadena de texto que representa una molécula (ej. `CCO` para el etanol) |
| **Tau** | Proteína que se agrega de forma anormal en el Alzheimer, formando ovillos neurofibrilares |
| **TPSA** | Área de superficie polar topológica; el predictor individual más fuerte de si algo cruza la barrera hematoencefálica |
