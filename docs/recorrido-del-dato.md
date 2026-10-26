# De un SMILES a una lista de candidatos

El recorrido completo del dato, paso a paso, y **por qué cada paso se hace así y no de otra forma**. Cada «por qué» lleva la cifra que lo sostiene; el contexto largo de cada decisión vive en [la ruta del proyecto](decisiones.md) y los términos en el [glosario](glosario.md).

Se lee sin saber de química ni de modelado.

---

## El recorrido en doce pasos

| | Paso | En una línea |
|--:|:--|:--|
| 1 | Entra una estructura | Un texto que describe la molécula |
| 2 | Se convierte en números | 217 descriptores y una huella de 2,048 bits |
| 3 | Se quitan columnas inútiles | Quedan 151 |
| 4 | Se agrupan las moléculas parecidas | 1,048 grupos |
| 5 | Se parte sin que un grupo cruce | 70% / 10% / 20% |
| 6 | Cada modelo prepara sus columnas | El escalado se decide por modelo |
| 7 | Se entrenan seis familias y se elige una | Con un piso contra el que compararse |
| 8 | **Fase 1:** ¿cruza al cerebro? | Una clase: BBB+ o BBB− |
| 9 | **Fase 2:** ¿qué tan potente es contra cada diana? | Un número: la potencia |
| 10 | La potencia se puede cortar en una clase | Activo o inactivo a 10 µM |
| 11 | Se ordena la lista | De más a menos prometedor |
| 12 | Cada candidato sale con sus marcas | Natural, PAINS, dirección, citotoxicidad |

---

## 1 · Entra una estructura

La entrada del sistema es un **SMILES**: un texto corto que describe la molécula, como `CC(=O)Oc1ccccc1C(=O)O` para la aspirina.

**Por qué un SMILES y no un nombre.** Un compuesto natural puede tener cinco nombres y ninguno identifica su estructura. El SMILES sí, y es lo que las tres bases de datos comparten.

## 2 · Se convierte en números

RDKit calcula **217 descriptores 2D** —peso, polaridad, flexibilidad— y una **huella Morgan de 2,048 bits** que marca qué subestructuras tiene.

**Por qué esto y no un modelo de lenguaje químico.** Se midió: los *embeddings* congelados de transformadores preentrenados **no superan** a esta representación cuando la partición es por andamio ([1.3](decisiones.md#d1-3)). Y un descriptor se puede leer uno por uno, que es lo que exige la explicabilidad.

## 3 · Se quitan columnas inútiles

De 206 quedan **151**: se van 24 casi constantes —un solo valor reúne el 99% de las filas— y 31 redundantes por correlación.

**Por qué se filtra sobre los valores crudos y no transformados.** Es una lección cara. El Avance 2 eligió las columnas sobre una matriz ya transformada y congeló ese artefacto, así que cambiar la transformación obligaba a repetir la selección entera. Filtrando sobre lo crudo, las mismas 151 columnas salen con las tres transformaciones ([1.5](decisiones.md#d1-5)).

## 4 · Se agrupan las moléculas parecidas

Dos moléculas van al mismo grupo si comparten **andamio** —el esqueleto de anillos— **o esqueleto de conectividad**. Salen 1,048 grupos de 7,805 compuestos.

**Por qué se agrupa por las dos cosas y no solo por andamio.** Está medido: el andamio solo da 2,239 grupos e **infla el AUROC 2.2 puntos y el MCC 7.1** ([1.2](decisiones.md#d1-2)). Un mismo esqueleto puede aparecer bajo andamios distintos, y separarlos pone estereoisómeros del mismo compuesto a los dos lados.

## 5 · Se parte sin que un grupo cruce

70% entrenamiento, 10% validación, **20% prueba reservada que el modelo nunca ve**.

**Por qué no al azar.** Una partición aleatoria **infla el resultado entre 7 y 13 puntos**, porque deja análogos casi idénticos a los dos lados. El modelo parece reconocer química nueva cuando en realidad reconoce a un primo hermano.

**Por qué una prueba reservada.** No se espera encontrar otra base de datos con la que validar después, así que la única evaluación sobre química que el modelo nunca vio es la que se aparte ahora ([2.6](decisiones.md#d2-6)).

**Y todo lo que aprende de los datos se ajusta dentro del pliegue** —escalar, seleccionar, imputar—. Un escalador ajustado antes de partir filtra la media y la varianza del pliegue de evaluación, y el resultado sale mejor de lo que es.

## 6 · Cada modelo prepara sus columnas

Un descriptor mide gramos por mol y otro cuenta anillos. Algunos modelos necesitan que esas escalas se parezcan y otros no.

| Necesita escalar | No necesita |
|:--|:--|
| Regresión logística, kNN, SVM, red neuronal | Árboles |

**Por qué se decide por modelo y no de una vez.** Un árbol parte por umbrales, así que la escala le da igual; una distancia o un gradiente sí dependen de ella. Cada canalización lleva su propio escalado dentro, y así se ajusta solo con el pliegue de entrenamiento.

**Y el escalado de la logística se eligió por convergencia, no por desempeño.** Entre las tres formas de escalar la medición no las distingue; sin escalar, el modelo agota sus iteraciones ([1.5](decisiones.md#d1-5)).

**Reducir dimensión se midió y se descartó.** El PCA resume las 151 columnas en 85 componentes sin cambiar el resultado de forma distinguible, pero una componente no se puede leer. Se prefiere explicar antes que comprimir.

## 7 · Se entrenan seis familias y se elige una

Seis algoritmos distintos, **individuales y sin ensambles**: logística, árbol, kNN, bayesiano, SVM y red neuronal.

**Por qué seis y no el mejor de entrada.** Ninguna familia gana siempre; cuál conviene depende de los datos, y eso se mide, no se supone.

**Cómo se valida.** Tres semillas por cinco pliegues, quince evaluaciones. La dispersión entre ellas **no es un error estándar**: las semillas comparten filas, así que sirve para saber si dos modelos se distinguen, no para un intervalo de confianza.

**Siempre hay un piso.** En regresión es un modelo que predice el promedio y nada más. Si uno elaborado no le gana, lo elaborado no está aportando, y decirlo es un resultado válido.

**El ajuste fino va dentro del pliegue.** Probar combinaciones de parámetros mirando los datos de evaluación los contamina: el modelo parece mejor porque ya los vio.

**Y afinar no siempre sirve.** Medido en la fase 1: el SVM **empeoró** cuatro milésimas de MCC al afinarse y tardó veintiuna veces más. La razón es que su parámetro principal no tiene un óptimo estable —recorre toda la rejilla y toca los dos extremos—, así que la búsqueda está ajustando ruido de partición.

**El mejor por métrica no es automáticamente el elegido.** También pesan cuánto cuesta entrenarlo y si se puede explicar por qué predice lo que predice. En la fase 1 cuatro familias empatan dentro de la dispersión, así que la métrica sola no decide.

## 8 · Fase 1 · ¿cruza al cerebro?

Sale una clase: **BBB+** si el compuesto atraviesa la barrera hematoencefálica, **BBB−** si no.

**Por qué no se usa la exactitud para medir.** Hay 1.74 positivos por cada negativo, así que un modelo que diga siempre BBB+ acierta el 63.5% sin aprender nada. Se reportan **MCC y AUPRC sobre la clase minoritaria** ([C.1](decisiones.md#dc-1)).

**Y un BBB− no descarta al compuesto.** Solo 1,033 esqueletos tienen medición en las dos fases, así que filtrar por una predicción no verificada tiraría el 99% restante. Las dos fases son evidencia paralela que se combina al ordenar, no una cascada.

## 9 · Fase 2 · ¿qué tan potente es contra cada diana?

La unidad **no es el compuesto, es el par compuesto-diana**: 70,384 pares de 59,532 compuestos contra 26 dianas.

**Por qué el par y no el compuesto.** Una medición solo es comparable con otra sobre la misma proteína. «Activo» en abstracto no significa nada.

Cada medición se convierte a **potencia**: `pActividad = 6 − log₁₀(concentración en µM)`. Más alto es más potente, porque hace falta menos concentración.

**Por qué esa escala.** Es la misma que el pChEMBL, que ChEMBL calcula pero NPASS y CMAUP no traen. Al calcularla nosotros, las tres fuentes quedan en la misma escala; sobre las filas que traen ambos valores, la diferencia con el pChEMBL tiene mediana de **0.0021**.

**Las mediciones censuradas no se tiran ni se toman como exactas.** Un «> 10 µM» significa «la potencia es menor que 5», y se guarda como cota.

**Por qué importa tanto.** El 98% de los pares activos tiene una medición exacta, pero **solo el 50.6% de los negativos**: la mitad de la evidencia de inactividad existe únicamente como cota. Y se midió lo que cuesta tirarla: entrenando solo con exactas, **las seis familias de modelos quedan en el azar sobre los productos naturales**, mientras que una recta que sí usa las cotas alcanza 0.639 de concordancia en ese mismo grupo ([2.9](decisiones.md#d2-9)).

## 10 · La potencia se puede cortar en una clase

Lo que se guarda es **el intervalo donde cae la potencia**, no una etiqueta. La clase «activo a 10 µM» sale de aplicar el corte a la predicción, al final.

**Por qué el intervalo y no la etiqueta.** Porque el corte no es estimable: no hay ninguna columna que diga si un compuesto funcionó, así que el umbral se elige, no se mide. Y no significa lo mismo en cada diana: con el mismo corte, `LRRK2` queda en 98.1% de activos y `NFE2L2` en 50.7%.

Guardarlo así tuvo una consecuencia concreta. Al revisar de dónde venían los datos y qué mide cada ensayo apareció una ambigüedad sobre qué debía predecir la fase 2; se consultó y se resolvió que lo que se predice es la potencia. **El cambio no obligó a reconstruir nada**, porque la clase y la potencia salen del mismo archivo ([2.10](decisiones.md#d2-10)).

**Y la dirección del efecto no entra en la etiqueta, viaja como marca.** Una diana se quiere frenar y otra encender, pero muchas mediciones solo dicen cuánto se pega el compuesto, no qué le hace. **Por qué no se invierte la etiqueta:** un antagonista potente es estructuralmente casi idéntico a un agonista potente, así que marcarlo como negativo metería moléculas gemelas con etiquetas contrarias, que no es información sino ruido que ningún modelo puede aprender ([2.11](decisiones.md#d2-11)).

## 11 · Se ordena la lista

El entregable es **una lista de candidatos priorizados**, no un sí o un no.

**Por qué no se fija dónde cortar la lista.** Depende de qué error cuesta más, y eso no lo decide la estadística: un falso positivo manda al laboratorio a ensayar algo que no sirve, y un falso negativo descarta un candidato sin que nadie se entere. Se entrega **la curva de precisión contra profundidad**, con un corte sugerido en los veinte primeros, que es lo que un laboratorio ensaya en un semestre ([C.5](decisiones.md#dc-5)).

## 12 · Cada candidato sale con sus marcas

| Marca | Qué dice | Por qué |
|:--|:--|:--|
| Origen natural | Si viene de NPASS o CMAUP | Son los que el proyecto quiere priorizar |
| PAINS | Si es un falso positivo frecuente | Los naturales llevan esa alerta **2.1 veces más seguido**; la curcumina aparece contra 32 dianas ([C.4](decisiones.md#dc-4)) |
| Dirección | Si la evidencia dice en qué sentido actúa | Ver el paso 10 |
| Citotoxicidad | Si lo que se midió fue que mata células | Propuesta: un ranking que la ignore pondría arriba a los promiscuos tóxicos ([C.7](decisiones.md#dc-7)) |

**Y todo se reporta por procedencia, nunca solo en agregado.** Un modelo que solo ve de dónde viene el compuesto ya alcanza el **65% del MCC** que consigue la química. Una cifra global no describe a los productos naturales, que son el 5.8% de los pares y la razón de ser del proyecto ([2.5](decisiones.md#d2-5)).

---

## Lo que este recorrido todavía no hace

| | Dónde se sigue |
|:--|:--|
| Decir **qué** características pesan: se mide la importancia pero no se nombra ninguna | [#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146) |
| El segundo método de atribución, que la [C.2](decisiones.md#dc-2) exige | [#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146) |
| Las métricas con que se juzga una lista ordenada | [C.5](decisiones.md#dc-5) |
| La marca de citotoxicidad | [C.7](decisiones.md#dc-7) |
