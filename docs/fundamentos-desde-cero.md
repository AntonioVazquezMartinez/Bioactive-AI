# Fundamentos desde cero

La entrada accesible a la teoría del proyecto, sin suponer nada de química, biología ni inteligencia artificial. Cada sección da la idea en pocas líneas y manda al [marco teórico](planteamiento/marco-teorico/README.md) para la evidencia, las cifras y las fuentes, que viven solo allí. Para un término suelto, el [glosario](glosario.md).

Qué contienen los archivos de datos y qué defectos tienen no se cuenta aquí sino en [los datos del proyecto](datos-contenido.md).

## 1. Qué es una molécula y cómo se «escribe»

**Compuesto** y **molécula** se usan como sinónimos: una sustancia definida por cómo están unidos sus átomos. La distinción que el proyecto usa constantemente:

- Un **producto natural** lo produce un organismo vivo, casi siempre una planta, sin que nadie lo diseñe. La morfina, de la amapola, es uno.
- Un compuesto **sintético** se fabrica en un laboratorio.

Importa porque el objetivo es encontrar productos naturales prometedores, pero la mayoría de los datos disponibles para entrenar modelos son de sintéticos (fármacos ya estudiados). Ese desajuste reaparece una y otra vez.

**Cómo se le dice a una computadora qué molécula es.** Con un texto llamado **SMILES**: una cadena que describe los átomos y sus conexiones. El etanol, el alcohol común, es `CCO`: dos carbonos pegados y luego un oxígeno. Dos consecuencias: su longitud varía mucho, y **no es único**, porque la misma molécula se puede escribir de varias formas válidas. Por eso nunca se usa el SMILES para saber si dos filas son la misma molécula.

**El identificador confiable es el InChIKey**, una huella que se calcula de la estructura real: la misma molécula da siempre el mismo InChIKey, sin importar el programa. Toda comparación entre compuestos se hace por InChIKey, no por el SMILES ni por el nombre. Sus primeros 14 caracteres codifican solo el **esqueleto de conectividad**, sin la **estereoquímica**: cómo están acomodados los átomos en el espacio. Dos **estereoisómeros** comparten conectividad y pueden comportarse distinto.

Más detalle y alternativas (SELFIES): [marco teórico, parte 2](planteamiento/marco-teorico/02-metodos-computacionales.md), §5.1.

## 2. El obstáculo central: la barrera hematoencefálica

Alrededor de los vasos que irrigan el cerebro hay una capa de células muy unidas entre sí que actúa como filtro selectivo: la **barrera hematoencefálica**, **BBB** en inglés. Protege a las neuronas de las fluctuaciones de la sangre. No es una membrana pasiva sino una interfaz activa.

Su efecto es que bloquea casi todo por igual, medicamentos útiles incluidos. Un compuesto puede funcionar muy bien contra una enfermedad del cerebro en células aisladas y ser inútil como medicamento porque nunca llega al tejido. De ahí la etiqueta: **BBB+** si cruza, **BBB−** si no.

Cruza por dos rutas que importan aquí:

- **Difusión pasiva**: la molécula atraviesa las células sola. Favorece a las pequeñas y poco polares.
- **Eflujo activo**: bombas como la **glicoproteína-P (P-gp)** *devuelven a la sangre* lo que ya entró. Un compuesto puede cumplir las reglas físicas para cruzar, entrar y ser expulsado. Por eso no basta con mirar tamaño y polaridad.

**BBB+ y BBB− no son una propiedad fija del compuesto.** La difusión y el eflujo compiten en la misma célula. A concentraciones bajas gana el eflujo y el compuesto parece BBB−; a concentraciones altas el eflujo se satura y el mismo compuesto parece BBB+. La etiqueta depende de la concentración probada y del umbral que usó quien reportó el dato. Es también la razón de que un resultado BBB− no descarte un candidato.

Cómo se mide (logBB, Kp,uu, PAMPA-BBB, MDCK-MDR1, perfusión), qué mide cada uno y por qué las etiquetas mezclan experimentos distintos: [marco teórico, parte 1](planteamiento/marco-teorico/01-biologia.md), §1.5.

## 3. Las reglas que predicen si algo cruza

Antes de la inteligencia artificial, los químicos ya tenían reglas simples basadas en propiedades que se calculan directo de la estructura. El proyecto las usa como comparación obligatoria: **si un modelo complejo no supera claramente a estas reglas, eso es un resultado que hay que reportar.**

- **TPSA**: cuánta superficie de la molécula es polar, es decir, atrae agua. Es el predictor individual más fuerte.
- **logP**: qué tan afín a la grasa es, en vez de al agua.
- **MW**: peso molecular.
- **HBD y HBA**: cuántos donadores y aceptores de puente de hidrógeno tiene, los grupos que forman enlaces débiles con el agua.

**Por qué funcionan.** Para cruzar la bicapa de grasa de una membrana, la molécula tiene que soltar el agua a la que está pegada. Cuantos más puentes de hidrógeno forme, es decir, cuanto más polar sea, más cuesta soltarse y peor penetra. Con logP hay un punto intermedio: muy poco y no puede dejar el agua, demasiado y queda atrapada en la grasa; no es «mientras más lipofílica, mejor».

La regla de dos condiciones, **TPSA < 67 Å² y HBD ≤ 1**, es la que domina empíricamente, así que toda explicación del modelo se contrasta primero contra ella. Qué tan bien funciona sobre nuestros datos: [los datos del proyecto](datos-contenido.md). Las cifras publicadas: [marco teórico, parte 1](planteamiento/marco-teorico/01-biologia.md), §1.6, y [parte 2](planteamiento/marco-teorico/02-metodos-computacionales.md), §5.3.

## 4. Enfermedades del cerebro y qué significa «neuroprotección»

La segunda mitad del proyecto busca compuestos que protejan al cerebro de enfermedades degenerativas, sobre todo Alzheimer y Parkinson.

- **Alzheimer.** Dos proteínas centrales: el **amiloide-β**, que forma placas, y **tau**, que se modifica de más y forma ovillos. La **hipótesis de la cascada amiloide** dice que el amiloide desencadena el resto, pero está seriamente cuestionada. La **hipótesis colinérgica** atribuye los síntomas a la pérdida de acetilcolina y es la base de los fármacos actuales, como el donepezilo.
- **Parkinson.** El actor central es la **α-sinucleína**, que se agrega en las neuronas. También hay disfunción mitocondrial.
- **Lo que comparten**: estrés oxidativo, **neuroinflamación** y **excitotoxicidad** (sobreestimulación por exceso de glutamato). Son los mecanismos que las dianas del proyecto intentan atacar.

Una **diana** (*target*) es la proteína específica sobre la que un compuesto actúa para producir su efecto. El proyecto trabaja con 39 dianas curadas a mano por la patrocinadora; cómo están organizadas, en [los datos del proyecto](datos-contenido.md).

**«Neuroprotector» es una palabra peligrosa.** Casi nada de lo que funciona en un experimento de laboratorio llega a funcionar como medicamento en personas; es la norma histórica del campo. Por eso el lenguaje correcto es siempre **«actividad neuroprotectora predicha según su mecanismo molecular»**, nunca llamar a un compuesto «neuroprotector» sin esa salvedad. Las cifras y los casos: [marco teórico, parte 1](planteamiento/marco-teorico/01-biologia.md), §2.

## 5. Productos naturales como fuente de medicamentos

La ruta «producto natural → mecanismo validado → medicamento» sí funciona. El caso que justifica la idea es la **galantamina**, un alcaloide de la campanilla de invierno que pasó de la medicina tradicional a ser un fármaco aprobado para Alzheimer. Pero es la excepción, no la norma.

**El problema de los falsos positivos: PAINS.** Muchos compuestos naturales salen «activos» contra decenas de enfermedades distintas, lo cual es sospechoso: es poco probable que una sola molécula tenga un mecanismo específico contra tantas cosas. Los **PAINS** (*compuestos de interferencia pan-ensayo*) dan positivo no por un efecto biológico específico sino por interferir con la medición o con las membranas. El ejemplo más documentado es la **curcumina**: más de 120 ensayos clínicos y ninguno riguroso mostró beneficio. Antes de reportar un candidato hay que pasarlo por filtros PAINS y desconfiar de los resultados demasiado buenos en esta familia química (polifenoles, catecoles).

**Por qué son distintos para la computadora.** Los naturales que llegaron a ser fármacos son más pesados y más complejos que los sintéticos que dominan los datos de entrenamiento. Un modelo entrenado sobre todo con sintéticos puede fallar con naturales simplemente porque no vio ejemplos parecidos.

Cifras y fuentes: [marco teórico, parte 1](planteamiento/marco-teorico/01-biologia.md), §3.

## 6. Cómo «aprende» una inteligencia artificial de esto

En vez de escribir reglas a mano, se le muestran al modelo miles de compuestos ya resueltos, cada uno con su estructura y su etiqueta conocida, y el modelo encuentra patrones que los relacionan. Es **aprendizaje supervisado**, porque durante el entrenamiento conoce la respuesta, y de **clasificación**, porque la respuesta es una categoría (BBB+ o BBB−). Una vez entrenado, predice sobre compuestos que nunca vio.

**Convertir una molécula en números.** El modelo necesita que cada ejemplo sea una lista de números de **tamaño fijo**, y el SMILES varía de longitud. Ese paso se llama **featurización** y el proyecto usa dos técnicas que se complementan:

- **Descriptores fisicoquímicos**: propiedades numéricas calculadas con **RDKit**, como TPSA, logP o MW.
- **Fingerprints** (huellas moleculares): un vector de «sí/no» que marca si están presentes ciertos fragmentos pequeños. El tipo que se usa, **Morgan/ECFP**, tiene una ventaja clave: cada posición se puede rastrear al fragmento exacto que la activó, lo que es esencial para la explicabilidad.

**Por qué no un modelo de lenguaje sobre el SMILES.** Obligaría a rellenar o cortar las cadenas, afectando justo a las moléculas grandes, y la comparación directa de 25 modelos preentrenados contra los fingerprints clásicos, bajo evaluación correcta, no mostró una mejora real. Con esa evidencia se prefiere lo simple, que además es interpretable y corre en una computadora normal.

**Qué modelo.** Modelos de **ensamble**, como Random Forest y XGBoost, que combinan muchas decisiones simples. Funcionan con miles de ejemplos, corren rápido y permiten rastrear la importancia de cada variable.

Detalle y evidencia: [marco teórico, parte 2](planteamiento/marco-teorico/02-metodos-computacionales.md), §5, y [parte 3](planteamiento/marco-teorico/03-modelado-y-explicabilidad.md), §6.

## 7. Por qué hay que evaluar el modelo con cuidado

Es la sección más importante de la teoría, porque es la fuente del error metodológico más común y más grave en este tipo de trabajo.

**El experimento mental.** Si divides los compuestos al azar en «entrenar» y «probar», es fácil que dos versiones casi idénticas de la misma molécula caigan una en cada lado. El modelo memoriza una y acierta la otra, y el resultado parece excelente sin que haya aprendido nada generalizable. Es una ilusión.

**La solución: partición por andamio.** Un **andamio** (Bemis-Murcko) es el esqueleto de anillos de una molécula, sin los grupos que cuelgan de él. La **partición por andamio** agrupa los compuestos por andamio y reparte andamios completos entre entrenamiento y prueba, nunca separando compuestos del mismo andamio. Es deliberadamente más difícil, e imita el uso real: evaluar estructuras que el modelo no vio. Una partición aleatoria infla los resultados entre 7 y 13 puntos, por eso el proyecto **nunca** la usa. También se agrupa por esqueleto de conectividad, para que los estereoisómeros caigan del mismo lado. Por qué esto importa en nuestros datos: [los datos del proyecto](datos-contenido.md).

**Otros cuidados.** El conjunto de prueba no se toca al construir el modelo ni al elegir variables o parámetros; se usa una sola vez al final. Y el modelo puede aprender atajos ajenos a la química, como reconocer el laboratorio de origen, por lo que conviene separar también por fuente cuando se pueda.

**Cómo medir.** Si el 63.5% de los compuestos son BBB+, un modelo inútil que siempre responda «BBB+» ya «acierta» el 63.5%. Con clases desbalanceadas la exactitud engaña, así que se usan:

- **MCC**: solo es alto si el modelo acierta bien en las dos clases.
- **AUPRC**: más informativa que el AUROC cuando las clases están desbalanceadas.

Detalle de la validación y del desbalance: [marco teórico, parte 2](planteamiento/marco-teorico/02-metodos-computacionales.md), §4.6 y §4.7.

## 8. Explicabilidad: por qué no basta con que adivine bien

Los asesores fueron claros desde la primera reunión: no quieren solo una predicción, quieren saber **qué parte de la molécula** la produjo. Es un requisito, no un extra.

Los fingerprints lo permiten porque cada posición corresponde a un fragmento concreto: se puede preguntar cuánto pesó una posición y dibujar ese fragmento. Con representaciones abstractas, como las de un modelo de lenguaje, es casi imposible hacerlo de forma confiable.

**SHAP** reparte el crédito de una predicción entre las variables, con una idea de la teoría de juegos. Tiene límites: al plegar un fingerprint, fragmentos distintos pueden compartir posición (una **colisión**), y que una variable pese en el modelo no significa que sea la causa biológica; es una pista fuerte, no una prueba.

**La regla del proyecto**: al menos dos métodos independientes, reportando como confirmados solo los fragmentos en que coinciden, y un modelo interpretable por diseño entrenado en paralelo como control. Toda explicación se contrasta antes contra TPSA < 67 Å² y HBD ≤ 1; si las contradice sin razón, es señal de revisar el modelo, no de haber descubierto algo ([decisión C.2](decisiones.md#dc-2)).

Los métodos y sus críticas: [marco teórico, parte 3](planteamiento/marco-teorico/03-modelado-y-explicabilidad.md), §7, y la [investigación sobre explicabilidad](referencias/03-explicabilidad.md).
