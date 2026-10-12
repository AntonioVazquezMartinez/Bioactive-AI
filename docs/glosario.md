# Glosario

Este proyecto cruza dos disciplinas que no comparten vocabulario. Quien viene de inteligencia artificial no tiene por qué saber qué es un transportador de eflujo; quien viene de bioingeniería no tiene por qué saber qué es el AUPRC. Este glosario define los términos en las dos direcciones, y es el lugar canónico: cuando un documento del sitio usa uno de estos términos, la definición que vale es esta.

Cada entrada dice **qué es** y, sobre todo, **por qué importa aquí**. Un término bien definido pero sin consecuencia para el proyecto no sirve de mucho.

---

## Química y biología

**Barrera hematoencefálica (BBB)**
: Capa de células muy unidas entre sí que recubre los vasos sanguíneos del cerebro y controla qué entra desde la sangre. Es tan selectiva que bloquea a la gran mayoría de los fármacos. **Por qué importa:** es la etapa 1 del proyecto. Un compuesto que no la cruza difícilmente actuará sobre el sistema nervioso central, aunque un resultado negativo no lo descarta.

**BBB+ / BBB−**
: La etiqueta que el modelo de la etapa 1 predice: BBB+ si el compuesto cruza la barrera, BBB− si no. **Por qué importa:** es la variable objetivo. En nuestros datos hay 4,956 BBB+ contra 2,849 BBB−, una razón de 1.74 a 1, y ese desbalance condiciona qué métricas se pueden usar.

**SMILES**
: Forma de escribir una molécula como una cadena de texto, sin dibujarla. `CCO` es el etanol: dos carbonos encadenados y un oxígeno. **Por qué importa:** es la única entrada del sistema. Todo lo demás —descriptores, fingerprints, andamios— se calcula a partir del SMILES. Ojo: una misma molécula admite varios SMILES válidos, así que no sirve como identificador.

**CXSMILES** (SMILES extendido)
: SMILES con información adicional al final, entre llaves, como coordenadas o etiquetas de átomos. **Por qué importa:** aparece en el [visualizador](../visualizador.qmd) como una de las representaciones; el pipeline no lo usa.

**SMARTS**
: Lenguaje para escribir patrones de subestructura: no describe una molécula concreta sino *qué buscar* dentro de muchas. **Por qué importa:** es el lenguaje en que se definen los filtros PAINS. El pipeline no lo usa para representar moléculas.

**Molblock (V2000 y V3000)**
: Formato de archivo clásico de la química computacional: una tabla con los átomos, sus coordenadas y los enlaces. V3000 es la versión moderna, sin el límite de 999 átomos de V2000. **Por qué importa:** es lo que entiende cualquier programa de visualización o de cálculo.

**InChIKey**
: Identificador estándar de 27 caracteres derivado de la estructura. A diferencia del SMILES, la misma molécula produce siempre el mismo InChIKey sin importar qué programa lo calcule. **Por qué importa:** es la forma correcta de detectar duplicados.

**Esqueleto de conectividad (`key14`)**
: Los primeros 14 caracteres del InChIKey. Codifican qué átomos hay y cómo se conectan, ignorando la disposición espacial. Dos estereoisómeros comparten esqueleto. **Por qué importa:** revela que nuestras 7,805 filas son solo 4,018 estructuras distintas. El tamaño efectivo de la muestra es la mitad de lo que sugiere el conteo de filas.

**Estereoisómero**
: Molécula con los mismos átomos conectados igual, pero dispuestos distinto en el espacio —por ejemplo, la imagen en espejo de otra—. **Por qué importa:** pueden tener actividad biológica distinta, y de hecho 131 esqueletos de nuestro conjunto reúnen estereoisómeros con etiquetas BBB contradictorias. Pero son tan parecidos que repartirlos entre entrenamiento y prueba sería hacer trampa.

**Estereocentro y configuración CIP (R/S)**
: Un estereocentro es un átomo, casi siempre un carbono, con cuatro sustituyentes distintos, de modo que existen dos disposiciones espaciales que son imagen en espejo una de otra. Las reglas de Cahn-Ingold-Prelog (CIP) etiquetan cada una como R o S. **Por qué importa:** la morfina tiene cinco estereocentros, y cambiar uno produce un estereoisómero distinto. El [visualizador](../visualizador.qmd) los detecta y los etiqueta.

**Producto natural**
: Sustancia producida por un organismo vivo, no sintetizada en laboratorio. **Por qué importa:** son los compuestos que el proyecto quiere priorizar. El conjunto los identifica cruzando estructuras contra COCONUT, el catálogo abierto de productos naturales.

**Transportador de eflujo / glicoproteína-P**
: Proteína de la barrera que agarra ciertas moléculas que ya entraron y las devuelve a la sangre, gastando energía. **Por qué importa:** explica por qué las propiedades fisicoquímicas no bastan. Un compuesto puede tener el perfil ideal para cruzar y aun así no acumularse en el cerebro porque lo expulsan activamente.

**Diana**
: La proteína sobre la que se mide si un compuesto actúa; en inglés *target*. En este proyecto son 39, casi todas identificadas por su gen (`MAPT`, `ACHE`, `TARDBP`), y cada una está asociada a una enfermedad del sistema nervioso. **Por qué importa:** la etapa 2 no predice «actividad» en abstracto sino actividad **contra una diana**, y una medición solo es comparable con otra de la misma. Cuando un ensayo observa un efecto en células nerviosas sin saber qué proteína lo produjo, se llama **fenotípico** y no tiene diana: son 88,098 de los 202,647 registros.

**PAINS** (*Pan-Assay Interference Compounds*)
: Compuestos que dan positivo en casi cualquier ensayo por mecanismos inespecíficos, no porque actúen sobre la diana. **Por qué importa:** la curcumina es el caso clásico, con más de 120 ensayos clínicos sin un resultado positivo controlado. El modelo los va a rankear alto, así que hay que filtrarlos antes de reportar cualquier candidato.

---

## Descriptores moleculares

**Descriptor molecular**
: Un número calculado a partir de la estructura que resume una propiedad de la molécula: su tamaño, su polaridad, su flexibilidad. Convierte una estructura química en una fila de una tabla, que es lo que un modelo puede consumir. **Por qué importa:** son la representación principal del proyecto. RDKit calcula 217 descriptores 2D, y son interpretables uno por uno, a diferencia de un *embedding*.

**TPSA** (área de superficie polar topológica)
: Suma de la superficie de los átomos polares de la molécula, en Å². Mide qué tan polar es. **Por qué importa:** es el descriptor que mejor separa BBB+ de BBB− por sí solo, con un AUC de 0.850. Las moléculas que cruzan tienden a ser poco polares.

**HBD y HBA** (donadores y aceptores de puente de hidrógeno)
: Cuántos átomos de la molécula pueden donar o aceptar un enlace débil de hidrógeno. Son otra forma de medir polaridad. **Por qué importa:** HBD es el segundo mejor descriptor individual. Pero correlaciona 0.76 con TPSA, así que no aporta una señal independiente: es el mismo eje de polaridad medido distinto.

**logP**
: Qué tanto prefiere la molécula disolverse en grasa frente a agua. Valores altos significan lipofílica. **Por qué importa:** la barrera es una membrana grasa, así que la lipofilicidad ayuda a cruzar — hasta cierto punto, porque los compuestos muy lipofílicos se quedan atrapados en la membrana.

**logBB**
: Medida experimental de la relación entre la concentración del compuesto en el cerebro y en la sangre. **Por qué importa:** es el dato duro del que se derivan las etiquetas BBB+/BBB− con un umbral de −1.0. Solo 1,052 de nuestros 7,805 compuestos lo traen medido; el resto trae la clase sin el valor.

**Fsp3**
: Fracción de los carbonos de la molécula con hibridación sp³, es decir, los que no están en anillos aromáticos planos. Mide qué tan tridimensional es. **Por qué importa:** es de los pocos descriptores que **no** discriminan, con un AUC de 0.501, prácticamente azar. Vale la pena saber qué no sirve.

**Fingerprint / Morgan / ECFP4**
: Representación de la molécula como un vector de bits, donde cada bit indica la presencia de una subestructura concreta. **Por qué importa:** complementa a los descriptores, que resumen la molécula entera; el fingerprint dice qué fragmentos tiene. Cuidado con el nombre: ECFP4 se genera con `radius=2`, porque el número del nombre es el diámetro, no el radio.

**Sort & Slice**
: Forma de construir un fingerprint que, en vez de repartir las subestructuras en un número fijo de casillas mediante una función de dispersión, las ordena por frecuencia en el conjunto de entrenamiento y se queda con las L más comunes, una por columna. **Por qué importa:** el fingerprint plegado mete subestructuras distintas en el mismo bit, y entonces un bit importante no se puede traducir a una estructura concreta —justo lo que la explicabilidad necesita—. Aquí no hay colisiones: cada columna es una sola subestructura y se puede dibujar. El costo es que el vocabulario se aprende de los datos, así que se ajusta **solo con entrenamiento** y las subestructuras que solo aparecen en la prueba quedan fuera. El tamaño L es la decisión [1.7](decisiones.md#d1-7).

**MACCS**
: Fingerprint fijo de 166 preguntas sobre la molécula («¿tiene un anillo de siete miembros?», «¿tiene azufre?»), definidas a mano hace décadas. RDKit lo devuelve en 167 bits porque reserva el primero sin usar. **Por qué importa:** es corto y legible, pero menos específico que Morgan. El proyecto no lo usa; está en el visualizador para comparar.

---

## Partición y evaluación

**Andamio de Bemis-Murcko**
: El esqueleto de la molécula: sus anillos y los enlaces que los conectan, sin los grupos que cuelgan de ellos. Agrupa compuestos que son variaciones del mismo núcleo químico. **Por qué importa:** es el criterio con el que se parten los datos.

**Scaffold split**
: Partición que reparte **andamios completos** entre entrenamiento y prueba, en vez de repartir filas al azar. Así ninguna variación del mismo núcleo aparece en ambos lados. **Por qué importa:** es la diferencia entre medir si el modelo generaliza a química nueva o si solo memorizó andamios. Una partición aleatoria infla los resultados entre 7 y 13 puntos.

**Dominio de aplicabilidad**
: La región del espacio químico donde el modelo fue entrenado y, por tanto, donde sus predicciones son confiables. **Por qué importa:** si los productos naturales ocupan otra región, puntuarlos con un modelo entrenado sobre sintéticos es extrapolar, no interpolar. Es uno de los cinco principios de la OCDE para validar modelos QSAR.

**Desbalance de clases**
: Cuando una clase es mucho más frecuente que la otra. **Por qué importa:** con 1.74 a 1, un modelo que prediga siempre BBB+ acierta el 63.5% de las veces sin haber aprendido nada. Por eso la exactitud no sirve como métrica.

**AUC / AUROC**
: Probabilidad de que el modelo le dé mayor puntaje a un positivo que a un negativo, tomados al azar. 0.5 es azar, 1.0 es perfecto. **Por qué importa:** es útil para comparar descriptores individuales, pero **engaña con clases desbalanceadas**, porque premia el acierto sobre la clase mayoritaria.

**AUPRC** (área bajo la curva de precisión-exhaustividad)
: Como el AUC, pero calculada sobre la clase minoritaria. **Por qué importa:** es la métrica que sí refleja el desempeño sobre lo que cuesta predecir. Hay que leerla siempre contra su línea base, que es la proporción de la clase minoritaria, no 0.5.

**MCC** (coeficiente de correlación de Matthews)
: Métrica que resume la matriz de confusión completa en un número de −1 a 1. Solo da un valor alto si al modelo le va bien en las dos clases a la vez. **Por qué importa:** junto con el AUPRC, es la métrica principal del proyecto.

**Validación cruzada agrupada**
: Partir el entrenamiento en k pliegues y medir k veces, rotando cuál se usa para evaluar, **manteniendo juntos los compuestos que comparten estructura**. **Por qué importa:** es la forma de comparar dos opciones sin que la conclusión dependa de una sola partición. Sin agrupar, dos estereoisómeros del mismo compuesto caerían en pliegues distintos y el resultado saldría inflado por la misma razón que una partición aleatoria.

**Error estándar corregido** (Nadeau y Bengio)
: Cuando se repite la validación cruzada con varias semillas, las mediciones **comparten datos de entrenamiento** y no son independientes, así que el error estándar ingenuo las trata como si lo fueran y sale demasiado estrecho. La corrección multiplica la varianza por (1/n + n_prueba/n_entrenamiento) y, con 5 pliegues y 15 mediciones, resulta unas 2.2 veces mayor. **Por qué importa:** sin ella, diferencias que son ruido parecen reales, y en este proyecto eso ya habría sesgado dos decisiones —el tamaño del vocabulario y la transformación— hacia la opción más grande.

---

## Datos y metodología

**Escalado** (estandarización y min–max)
: Poner los descriptores en escalas comparables. La **estandarización** les deja media 0 y desviación 1; el **min–max** los lleva al rango [0,1]. **Por qué importa:** los descriptores van de menos de una unidad a casi 19,000 de amplitud, y un modelo lineal trataría al más grande como si pesara miles de veces más, por sus unidades y no por su contenido. Los árboles son indiferentes: solo miran el orden de los valores. **Y el costo no es de acierto, es de convergencia:** sin escalar, la regresión logística de este proyecto **no converge** —agota su presupuesto de iteraciones y avisa— y tarda mucho más (1,110 segundos contra 40 en una de las máquinas del equipo), mientras que el Random Forest tarda lo mismo con o sin escalado, porque no itera.

**Yeo-Johnson**
: Transformación de potencia que acerca una variable a la normal y **admite ceros y valores negativos**, a diferencia de Box-Cox y del logaritmo. **Por qué importa:** es la que mejor corrige la asimetría de estos descriptores y, medida con validación cruzada, la que peor predice con la regresión logística —queda por debajo en 12 de 15 pliegues, aunque la diferencia no alcanza significancia—. Corregir la asimetría y predecir mejor no son lo mismo. Por qué, no se ha medido: la hipótesis es que la potencia comprime las colas, que es donde está la señal.

**B3DB**
: Base de datos abierta de permeabilidad de la barrera hematoencefálica, con 7,807 compuestos clasificados. Es el origen de nuestros datos de la etapa 1. Datos en CC0.

**Categorías A–D de B3DB**
: Agrupación que B3DB asigna a cada registro según la evidencia disponible. **Por qué importa, y es un punto delicado:** parecen una escala de calidad, pero no lo son. El grupo D tiene más respaldo bibliográfico que el C, y filtrar a A+B dejaría la clase minoritaria en 27.0% frente al 36.5% del conjunto completo. Se usan para describir y estratificar, **nunca para excluir**.

**COCONUT**
: Catálogo abierto de productos naturales conocidos. **Por qué importa:** el cruce contra COCONUT es lo que permite separar naturales de sintéticos, y de ahí sale el hallazgo central del Avance 1.

**ChEMBL y pChEMBL**
: ChEMBL es la base de datos de bioactividad. El pChEMBL es la potencia de un compuesto sobre una diana en escala logarítmica: pChEMBL ≥ 5 significa actividad a concentración micromolar o menor. **Por qué importa:** es la fuente de la etapa 2, y el pChEMBL es el umbral con el que se convertirán las mediciones en etiquetas de actividad.

**NPASS y CMAUP**
: Las dos bases de productos naturales de la etapa 2, con 11,992 y 3,301 registros contra los 187,354 de ChEMBL. **Por qué importa:** son justo los compuestos que el proyecto quiere priorizar, y **ninguna trae pChEMBL**, porque ese valor lo calcula ChEMBL. Etiquetar solo por pChEMBL los descartaría a todos, que es la razón del etiquetado por tres vías de la [decisión 2.3](decisiones.md#d2-3). NPASS es CC BY-NC, así que su uso es académico y no comercial.

**Medición censurada**
: Una medición que no da un número sino una cota: «> 10 µM» quiere decir que se probó hasta esa concentración y no se vio efecto, sin saber dónde aparecería. Son 54,498 de los 202,647 registros. **Por qué importa:** no se pueden tirar, porque son evidencia de que algo *no* funciona, y son la mayor fuente de negativos. Pero solo sirven como negativo si la cota llega al umbral de «activo»: un «> 1 µM» no dice nada si «activo» se definió en 10 µM. Es la regla de la sección 7 del diccionario de la patrocinadora.

**Inactivo declarado**
: Un registro sin valor numérico donde el texto del ensayo dice que el compuesto no actuó («Inhibition < 50% @ 10 uM»). Son 29,730 registros. **Por qué importa:** es la tercera vía de etiquetado, junto con el pChEMBL y la concentración exacta. Depende de confiar en la redacción del ensayo original, y por eso si es confiable es una de las preguntas abiertas de la [decisión 2.3](decisiones.md#d2-3).

**QSAR** (*Quantitative Structure-Activity Relationship*)
: La disciplina de predecir propiedades biológicas a partir de la estructura química. Es el campo al que pertenece este proyecto, con décadas de literatura y buenas prácticas propias.

**CRISP-ML(Q)**
: Metodología de seis fases para proyectos de machine learning. **Por qué importa:** es la estructura que sigue el calendario de entregas del curso.

**SHAP**
: Método que reparte la predicción del modelo entre sus variables de entrada, diciendo cuánto aportó cada una. **Por qué importa:** es una de las vías para cumplir el requisito de explicabilidad, enlazando un bit del fingerprint con la subestructura que lo activó.

**Explicabilidad a nivel de subestructura**
: Poder señalar qué fragmento concreto de la molécula sustenta la predicción, no solo qué variable pesó más. **Por qué importa:** la patrocinadora lo planteó como requisito no negociable. Un modelo que acierta pero no se puede interpretar no sirve para orientar trabajo de laboratorio.

---

## Dónde se tratan a fondo

| Tema | Documento |
|:-----|:----------|
| Biología de la barrera y de la enfermedad | [Marco teórico · parte 1](planteamiento/marco-teorico/01-biologia.md) |
| De la estructura química a una tabla | [Marco teórico · parte 2](planteamiento/marco-teorico/02-metodos-computacionales.md) |
| Modelado, explicabilidad y hueco | [Marco teórico · parte 3](planteamiento/marco-teorico/03-modelado-y-explicabilidad.md) |
| De SMILES a una tabla de características | [01 · Representaciones moleculares](referencias/01-representaciones-moleculares.md) |
| Datos de permeabilidad y particiones | [02 · Datasets de BBB](referencias/02-datasets-bbb.md) |
| Métodos de atribución | [03 · Explicabilidad](referencias/03-explicabilidad.md) |
| Datos de actividad en SNC | [04 · Datos de neuroactividad](referencias/04-datos-neuroactividad.md) |
| Procedencia y licencias de los datos | [Datos](../data/external/README.md) |
