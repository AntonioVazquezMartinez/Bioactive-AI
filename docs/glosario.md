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

**InChIKey**
: Identificador estándar de 27 caracteres derivado de la estructura. A diferencia del SMILES, la misma molécula produce siempre el mismo InChIKey sin importar qué programa lo calcule. **Por qué importa:** es la forma correcta de detectar duplicados.

**Esqueleto de conectividad (`key14`)**
: Los primeros 14 caracteres del InChIKey. Codifican qué átomos hay y cómo se conectan, ignorando la disposición espacial. Dos estereoisómeros comparten esqueleto. **Por qué importa:** revela que nuestras 7,805 filas son solo 4,018 estructuras distintas. El tamaño efectivo de la muestra es la mitad de lo que sugiere el conteo de filas.

**Estereoisómero**
: Molécula con los mismos átomos conectados igual, pero dispuestos distinto en el espacio —por ejemplo, la imagen en espejo de otra—. **Por qué importa:** pueden tener actividad biológica distinta, y de hecho 131 esqueletos de nuestro conjunto reúnen estereoisómeros con etiquetas BBB contradictorias. Pero son tan parecidos que repartirlos entre entrenamiento y prueba sería hacer trampa.

**Producto natural**
: Sustancia producida por un organismo vivo, no sintetizada en laboratorio. **Por qué importa:** son los compuestos que el proyecto quiere priorizar. El conjunto los identifica cruzando estructuras contra COCONUT, el catálogo abierto de productos naturales.

**Transportador de eflujo / glicoproteína-P**
: Proteína de la barrera que agarra ciertas moléculas que ya entraron y las devuelve a la sangre, gastando energía. **Por qué importa:** explica por qué las propiedades fisicoquímicas no bastan. Un compuesto puede tener el perfil ideal para cruzar y aun así no acumularse en el cerebro porque lo expulsan activamente.

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

---

## Datos y metodología

**B3DB**
: Base de datos abierta de permeabilidad de la barrera hematoencefálica, con 7,807 compuestos clasificados. Es el origen de nuestros datos de la etapa 1. Datos en CC0.

**Categorías A–D de B3DB**
: Agrupación que B3DB asigna a cada registro según la evidencia disponible. **Por qué importa, y es un punto delicado:** parecen una escala de calidad, pero no lo son. El grupo D tiene más respaldo bibliográfico que el C, y filtrar a A+B dejaría la clase minoritaria en 27.0% frente al 36.5% del conjunto completo. Se usan para describir y estratificar, **nunca para excluir**.

**COCONUT**
: Catálogo abierto de productos naturales conocidos. **Por qué importa:** el cruce contra COCONUT es lo que permite separar naturales de sintéticos, y de ahí sale el hallazgo central del Avance 1.

**ChEMBL y pChEMBL**
: ChEMBL es la base de datos de bioactividad. El pChEMBL es la potencia de un compuesto sobre una diana en escala logarítmica: pChEMBL ≥ 5 significa actividad a concentración micromolar o menor. **Por qué importa:** es la fuente de la etapa 2, y el pChEMBL es el umbral con el que se convertirán las mediciones en etiquetas de actividad.

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
| Fundamentos biológicos y computacionales | [Marco teórico](planteamiento/marco-teorico.md) |
| De SMILES a una tabla de características | [01 · Representaciones moleculares](referencias/01-representaciones-moleculares.md) |
| Datos de permeabilidad y particiones | [02 · Datasets de BBB](referencias/02-datasets-bbb.md) |
| Métodos de atribución | [03 · Explicabilidad](referencias/03-explicabilidad.md) |
| Datos de actividad en SNC | [04 · Datos de neuroactividad](referencias/04-datos-neuroactividad.md) |
| Procedencia y licencias de los datos | [Datos](../data/external/README.md) |
