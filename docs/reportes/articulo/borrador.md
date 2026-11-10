# Cuánto confiar en una predicción depende de la molécula, no del modelo: permeabilidad y potencia en compuestos naturales

**Nota de trabajo, no llega al `.tex`.** Borrador para la entrega del **13 de noviembre de 2026**; el plazo
del curso es el 15. El cuerpo lleva un hilo y el detalle va a anexos, por la decisión del 4 de noviembre.
Cada cifra sale de una corrida registrada en `experimentos/` y las figuras se generan con
`scripts/figuras_articulo.py`. El cuerpo, del título a las referencias, ocupa 16 de las 12 a 18 páginas que
pide la rúbrica, así que lo que se añada conviene que sustituya.

## Resumen

Buscamos compuestos naturales con potencial neuroprotector con dos modelos en paralelo: uno que
clasifica si una molécula cruza la barrera hematoencefálica (fase 1) y otro que predice su potencia
contra una diana, usando también las mediciones censuradas (fase 2). Comparamos once modelos y
ningún ensamble mejora de forma distinguible al mejor modelo individual en MCC ni en AUPRC; en AUROC dos ensambles lo superan por 1.3 puntos, diferencia que no sobrevive a la corrección por diez comparaciones. Lo que sí mueve el resultado
es una lección conocida (`sheridan2013`, `roberts2017crossvalidation`), medida aquí con sus magnitudes: **cuánta semejanza se permite entre lo que
se entrena y lo que se evalúa**. Con el modelo que entregamos, el MCC baja 33.3 puntos al exigir que
ningún compuesto de entrenamiento se parezca más de 0.4 a uno de validación, contra 4.2 puntos entre
los once modelos; la fase 2 muestra la misma escalera. Tres hallazgos propios: la prueba reservada es
**más difícil de lo que su similitud predice** (AUROC esperado 0.89, observado 0.79); el MCC exagera
esa caída porque corta en un punto fijo; y las huellas moleculares ayudan en la fase 2 y no en la 1,
sin que lo expliquen el tamaño de los datos ni el tipo de etiqueta. El modelo de potencia, elegido por
funcionar en compuestos que solo existen en NPASS, no se sostiene en la prueba en ese grupo (117 pares).

![Qué mueve el resultado](figuras/f0_palancas.svg)

*Figura 1. Cada barra viene de una corrida distinta, con otro propósito; indican el orden de
magnitud, no miden el efecto de cada factor por separado.*

## 1. Contexto de negocio y problema

La patrocinadora, del Departamento de Bioingeniería del Tec de Monterrey, busca priorizar compuestos naturales
con potencial neuroprotector y nootrópico antes de ensayarlos en el laboratorio, donde cada ensayo gasta tiempo
y presupuesto. Un compuesto natural bioactivo solo sirve si llega al cerebro y si actúa sobre una diana, así que
el problema tiene dos preguntas: si la molécula cruza la barrera hematoencefálica (fase 1, clasificación
BBB+/BBB−) y con qué potencia actúa sobre cada una de 26 dianas del sistema nervioso central (fase 2,
regresión). La entrada es la estructura (SMILES) y la salida es una lista priorizada, no una decisión
automática.

**El enfoque que se adoptó.** El planteamiento inicial encadenaba las dos preguntas: lo que saliera BBB− se
descartaba. Se abandonó porque esa predicción no está verificada para la mayoría de los compuestos: de los
99,585 esqueletos con actividad medida, solo 1,033 tienen además permeabilidad medida, y el otro 99% se
filtraría con una predicción no comprobada.
Los dos modelos son, por eso, evidencia paralela que se combinará en un ranking y no una cascada (la
combinación sigue pendiente, decisión C.3).

**Qué significa equivocarse.** Un falso permeable manda al laboratorio a ensayar algo que no funciona; un falso
no permeable descarta un candidato real sin que nadie se entere. Cuál error cuesta más lo decide el
laboratorio, y por eso el entregable es un orden y no un punto de corte (decisión C.5).

## 2. Datos y preparación

- **Fase 1 (permeabilidad).** 7,805 compuestos con clase, del archivo curado de la patrocinadora (derivado de
  B3DB y cruzado con COCONUT, lo que permite separar los naturales de los sintéticos); 65% BBB+; 6,306 para
  ajustar y validar y 1,499 reservados. No se filtra por la columna de grupo de confiabilidad (A a D): el
  análisis exploratorio mostró que está confundida con la clase, y filtrar empeora el desbalance en vez de
  limpiar ruido.
- **Fase 2 (potencia).** 202,647 registros de actividad (ChEMBL, NPASS, CMAUP); 56,241 pares para ajustar y
  13,944 reservados. Las tres fuentes se etiquetan con las mismas columnas, porque la medida que solo trae
  ChEMBL descartaría justo los naturales de NPASS y CMAUP. Se guarda el intervalo de potencia y no una
  etiqueta, porque el corte de 10 µM, heredado del cribado, es una decisión que puede cambiar y porque el mismo
  compuesto cambia de clase según la concentración. Los resultados se reportan por procedencia: un modelo que
  solo ve de dónde viene un compuesto ya alcanza 65% del MCC de la química.
- **Variables.** Descriptores 2D de RDKit (151 tras quitar los casi constantes y los redundantes, con la
  selección hecha sobre valores crudos) y, en la fase 2, la diana. Las huellas moleculares se midieron aparte
  (sección 4.4).
- **Partición.** Nunca al azar: se agrupa por andamio de Bemis–Murcko *unido* al esqueleto de
  conectividad, para que los estereoisómeros no caigan a los dos lados (1,048 grupos en la fase 1).

## 3. Metodología y modelos

**Del baseline al modelo final.** *Baseline* (Avance 3): tres canalizaciones con validación cruzada agrupada, 3
semillas × 5 pliegues: boosting por histogramas, bosque aleatorio y regresión logística (MCC 0.702, 0.700 y
0.687; los intervalos del 95% se solapan y ninguna gana). Su resultado fijó el desempeño mínimo que había que
superar, **0.70 de MCC** (y 0.93 de AUROC), contra un piso de 0 de MCC, 0.5 de AUROC y 0.35 de AUPRC que dan los
clasificadores triviales. *Candidatos* (Avances 4 y 5): once modelos de clasificación, de la regresión logística
a cinco ensambles y dos versiones afinadas, con una regla de mejora escrita antes de correr: una diferencia
pareada media por encima de un umbral y positiva en al menos 12 de las 15 evaluaciones. *Modelo final:*
ninguna de las treinta comparaciones contra el mejor individual pasó la regla, así que el final de la fase 1 es
ese mejor individual, `svm_rbf` sobre 151 descriptores; se eligió por descarte y no porque ganara. En la fase 2,
tras comparar nueve modelos de regresión, el final es un modelo de supervivencia acelerada (AFT, XGBoost
`chen2016xgboost`) que aprende de las mediciones censuradas.

**Rigor.** Las reglas de decisión se escribieron antes de cada corrida y no se ajustaron después
(no están pre-registradas); cada corrida reproduce una cifra ya registrada como control, y cada
resultado nuevo se recalculó con un segundo código. Los intervalos remuestrean grupos, no filas. De
los seis modelos de la fase 1, cuatro (incluido el entregado) dan la misma predicción con cualquier
semilla; el `mlp` y el `bosque` no (desviación de 0.017 y 0.007 de MCC). La prueba reservada se leyó
**catorce veces**, cuatro de ellas sin etiquetas —dos solo como SMILES (la escalera ampliada y la distribución de similitud de la prueba) y dos solo
estructurales (la proporción de andamios, una por fase)—, todas registradas en `experimentos/prueba.csv`; ningún modelo se eligió después
de verla.

**Qué hicieron las tres lecturas con etiquetas más recientes.** Dos reparten la prueba entre ajuste y
evaluación y reajustan el modelo, midiéndolo en 15 sorteos sobre el núcleo que queda; **no reevalúan el
modelo final que se entrega** (sección 4.3). La tercera sí lo evalúa, y lee su MCC a cuatro cortes: el corte
se eligió y se congeló en validación **antes** de abrir la prueba (sección 4.1).

**Métricas.** El AUROC mide qué tan bien el modelo ordena a los compuestos permeables por encima de los no
permeables, sin fijar un corte. El MCC (coeficiente de correlación de Matthews) resume en un número entre −1 y 1
las cuatro casillas de la matriz de confusión y **sí exige un corte**, aquí 0.5; por eso se mueve más que el AUROC
cuando cambia la distribución de los datos. El AUPRC sobre la clase minoritaria se lee contra su tasa base
(0.35 en la fase 1), no contra cero. En la fase 2, donde la respuesta es una potencia con mediciones censuradas, se
usa la concordancia de Harrell: la probabilidad de que, de dos pares, el modelo ordene bien al más potente (0.5 es
el azar). Los modelos se comparan con la diferencia pareada en las mismas 15 evaluaciones (3 semillas × 5
pliegues), con el intervalo corregido de Nadeau y Bengio `nadeau2003inference`.

## 4. Resultados y validación

### 4.1 El modelo final contra el baseline y el umbral

Contra el umbral de 0.70 de MCC que fijó el baseline, el modelo entregado lo iguala en validación cruzada y no
lo supera: MCC 0.7017 (el boosting del baseline daba 0.7019), AUROC 0.919 y AUPRC de la clase minoritaria 0.884,
contra un piso de 0.35. **El lift sobre el baseline es cero**, y es un resultado: elegir el modelo no fue la
palanca. En la prueba reservada, leída una sola vez con el modelo final, el MCC es 0.339, el AUROC 0.793 y el
AUPRC 0.720: una **brecha de 0.363 de MCC (52%) y de 0.126 de AUROC (14%)** frente a la validación cruzada. En
la fase 2 la concordancia baja de 0.761 a 0.720. El AUROC de 0.93 del baseline sale de predicciones promediadas
entre semillas y no se compara con el 0.919, que es el promedio de las 15 evaluaciones.

**Qué significan los errores para el laboratorio.** A 0.5 el modelo declara permeable al 70.9% de los
compuestos cuando la prevalencia real es 64.97%: de más, que es el error que gasta un ensayo. Pero la caída del
MCC es mayor que la del AUROC porque el MCC exige un corte fijo y, bajo un cambio de distribución, el modelo
cambia de sesgo (sección 4.2). Por eso el cuaderno entrega la probabilidad y no una clase, y lo que el
laboratorio debe leer es el orden.

**El corte no es parte del modelo, y moverlo recupera la mitad del margen.** El 0.339 es con el corte fijo en
0.5, que es una convención heredada y no una decisión. Sobre la prueba, ese corte declara BBB+ al 79.3% de los
compuestos cuando la prevalencia real es 57.3%: **22 puntos de desajuste**, frente a los 6 que hay en el
ajuste. Igualar la tasa declarada a una prevalencia supuesta, sin usar las etiquetas de la prueba, sube el MCC
a **0.4095**, es decir **+0.0712 con IC95% [+0.0303, +0.1099]** remuestreando los grupos de andamio. Y no hace
falta acertar la prevalencia: el corte se fijó suponiendo la del ajuste, 65.0%, cuando la de la prueba era
57.3%, un error de 7.7 puntos, y la ganancia se sostuvo igual. En cambio **elegir el corte con las etiquetas de
validación no recupera nada**, +0.0065 [−0.0224, +0.0341].

Tres cosas que esas cifras no dicen. Las dos lecturas salen del modelo entregado y de una sola apertura de la
prueba, con el corte congelado antes, y sus dos controles reproducen el 0.3385 y el AUROC 0.793 ya registrados.
La brecha de 0.363 de MCC contra validación cruzada se mide con el corte fijo en los dos lados, así que no
cambia. Y el techo de 0.485 **elige el corte con las etiquetas de la prueba**, de modo que no es alcanzable: lo
que mide es el margen que queda, no un resultado.

### 4.2 La escalera de semejanza

Entre los once modelos hay 4.2 puntos de MCC. Con el `svm_rbf`, pasar de pliegues al azar a pliegues
donde ningún compuesto de entrenamiento supera 0.4 de similitud con uno de validación cuesta 33.3
puntos (0.752 → 0.419). En validación cruzada, el modelo entregado da MCC 0.702 y AUROC 0.919.

![Escalera](figuras/f1_escalera.svg)

*Figura 2. AUROC por peldaño, seis modelos. La línea naranja es la prueba reservada (0.793).*

**La fase 2 muestra lo mismo, con una limitación del conjunto.** La concordancia del `aft` baja de
0.807 (por molécula) a 0.695 con similitud ≥ 0.6: una caída de 0.112, unas siete veces la dispersión de
0.015 entre los siete modelos competitivos de la fase 2 (el doble, 0.030, era el umbral declarado). A 0.5 y 0.4 no se puede ni construir la partición: el 69% y el 90% de las filas caen en
un solo grupo. No hay manera de evaluar la fase 2 con química realmente nueva a esos niveles.

![Escalera fase 2](figuras/f6_escalera_fase2.svg)

*Figura 3. Concordancia del `aft` por peldaño; en gris, solo pares de NPASS.*

**Dos matices que el artículo tiene que llevar.** La *forma* de la escalera depende de cómo se defina
«parecido»: con ECFP6 la caída es gradual y con ECFP4 casi todo ocurre entre 0.6 y 0.5, aunque la caída
total es parecida (0.419 contra 0.434 de MCC); con atom-pair no se pueden construir los peldaños
estrictos. Y el MCC exagera: con el mejor corte posible sería 0.655 y 0.560 en los dos peldaños
estrictos, contra 0.486 y 0.419 con el corte fijo en 0.5. Un corte de igual prevalencia solo recupera
+0.047 en el primero, así que no es una solución.

### 4.3 La prueba reservada es más difícil de lo que su similitud predice

En la prueba el AUROC es 0.793 y el MCC 0.339 (1,499 compuestos). Su similitud media al vecino más
cercano (0.414) es mayor que la de la validación agrupada (0.384), así que por similitud tendría que
rendir *mejor*: reponderar las predicciones de validación a su distribución de similitud da un AUROC
esperado de **0.89**, y el real es **0.79**. La brecha de 0.10 no se explica por qué tan lejos queda de
lo visto; qué es, no está medido (candidatos: prevalencia, peso y polaridad, curación de los datos,
andamios raros a propósito).

Dentro de la prueba, la ventaja del modelo sobre una línea base de peso molecular y TPSA crece con lo
parecido que es cada compuesto (+0.036 en el tercil más raro, +0.106 en el más parecido; diferencia
+0.069, IC95% 0.011 a 0.124); en la fase 2 la diferencia es cuatro veces menor.

**La caída baja con la similitud.** Dividiendo la prueba en terciles de similitud al ajuste (cortes 0.31 y 0.46), el AUROC sube de 0.697 a 0.793 y a 0.875: +0.178 entre el tercil más parecido y el menos parecido, IC95% [+0.119, +0.238] remuestreando esqueletos. En los compuestos sin equivalente natural la diferencia es +0.223 [+0.142, +0.306]; en los naturales exactos es +0.086 con un intervalo que incluye el cero [−0.029, +0.204], así que con 446 compuestos no se distingue, y en los análogos estereoquímicos el tercil más parecido tiene menos de 20 casos de la minoritaria y no se reporta. Es una correlación dentro de la prueba y la similitud no explica toda la brecha (0.89 esperado contra 0.79).

![Rareza](figuras/f2_rareza.svg)

*Figura 4. Ventaja sobre la línea base por tercil de rareza, con IC95% por bootstrap de grupos.*

**Dar más peso a lo raro durante el entrenamiento no ayuda.** Como la ventaja del modelo se pierde justo
en lo raro, probamos repesar las filas raras que ya están en el ajuste: peso 3, 2 y 1 según el tercil de
similitud al vecino más cercano de otro grupo, dentro de cada tramo de peso molecular (`svm_rbf`, 15
evaluaciones agrupadas, regla escrita antes de correr, sin leer la prueba; decisión 1.10). En el tercil más raro
de validación la ganancia de AUROC es −0.0005, positiva en 9 de 15 evaluaciones, cuando la regla pedía más de
0.005 en 12. Un control con los mismos pesos asignados al azar mueve el AUROC global casi igual
(+0.0015 contra +0.0022) y el MCC global baja 0.0022. **La regla tiene poca potencia para efectos chicos:**
con la dispersión observada (0.0095) solo detectaría con 80% de probabilidad una mejora de unos 0.010, así
que el resultado descarta una mejora grande, no una de 0.005.

**Pasar compuestos raros de la prueba al entrenamiento tampoco cierra la brecha.** Probamos la otra forma de
aprender de lo raro (decisión 1.11, lecturas 12 y 13 de la prueba —la segunda solo mide la prevalencia del reparto, sin
entrenar—, regla escrita antes de correr). La mitad de los
grupos de la prueba de cada tercil de rareza forma un núcleo de evaluación; de la otra mitad se pasan al ajuste
las filas del tercil más raro (285 de media) y se devuelven a la prueba otras tantas filas comunes del ajuste,
en 15 sorteos. En lo raro del núcleo el AUROC sube +0.003 (mejor en 9 de 15), y pasar el mismo número de filas de
la prueba **elegidas al azar** da +0.006: lo que ayuda es recibir filas de la prueba, no cuáles. El MCC pasa de
0.33 a 0.36 (+0.035, en los 15 sorteos), lejos del 0.70 de la validación, mientras el AUROC apenas cambia
(+0.002): el orden casi no cambia y el corte sí, así que no lo leemos como ganancia. Descomponerlo con los tres
brazos, sin otra lectura de la prueba, dice de dónde sale: quitar solo las 295 filas comunes del ajuste no lo
mueve (−0.001); recibir filas de la prueba sí, raras (+0.035, 15 de 15 sorteos) o al azar (+0.023, 13 de 15). El
MCC sube por recibir filas de la distribución sobre la que se evalúa, no por cuáles. No
lo explica la prevalencia del entrenamiento, que casi no se mueve (de 65.0% a 64.5% de BBB+). Lo más útil de la
corrida es otra cosa: los compuestos comunes que pasan a la prueba se miden con AUROC 0.94 y los raros que
quedaban en 0.68, con el mismo modelo y sin reentrenar; recomponer la prueba cambia el número que se reporta y
no lo que el modelo sabe. Los 15 sorteos comparten las mismas 1,499 filas, así que el resultado descarta una
ganancia grande y no una pequeña. No se adopta nada: 285 filas más de química rara no cierran la brecha entre
0.70 y 0.34 de MCC.

**Recomponer con cuáles filas se entrena tampoco ayuda.** La tercera forma (decisión 1.12) fija el tamaño, la
prevalencia y el número de grupos del ajuste y cambia solo su composición. Empezar por lo raro cuesta −0.060 de
AUROC contra el orden al azar con el 25% del ajuste (IC95% [−0.110, −0.011], a favor en 1 de 15 evaluaciones; es
una comparación secundaria, declarada antes y sin corrección por comparaciones múltiples, y el estadístico
principal incluye el cero); con el 75% la composición deja de importar (±0.0004), y ni siquiera mejora el
tercil más raro de la validación (+0.003, 8 de 15). **Ninguna de las formas que probamos de aprender de lo
raro —repesar, pasar filas de la prueba al ajuste y recomponer— cierra la brecha**, y añadir filas al azar ya
estaba en meseta en la curva de aprendizaje. El límite de la fase 1 no es de cuántas filas ni de cuáles; lo
que queda por medir es el punto de operación.

**El punto de operación sí mueve el MCC, pero no se elige con validación.** A 0.5 el modelo entregado declara
permeable al 79.3% de la prueba contra una prevalencia real de 57.3%: 22 puntos de desajuste, contra 6 en el ajuste
(decisión C.5, lectura 14 de la prueba). Un corte elegido en validación interna agrupada, congelado antes de leerla, no
recupera nada (MCC 0.3455 contra 0.3385; diferencia +0.0065, IC95% [−0.022, +0.034]), porque se elige donde la
prevalencia es 65.0% y no puede saber que la de llegada es otra. Igualar la tasa declarada a una prevalencia
supuesta (aquí la del ajuste, 65.0%) sube el MCC a 0.4095 (+0.071, IC95% [+0.030, +0.110]), casi la mitad del margen
que deja el corte óptimo de la prueba (0.485), que usa sus etiquetas. Exige tener el lote completo y suponer una
prevalencia; con el AUROC igual (0.793), el MCC dice cuánto cambió la tasa de aciertos de un punto de corte y no la
capacidad de ordenar.

### 4.4 La representación no se traslada entre fases

Las huellas Sort & Slice **no mejoran a ningún modelo de la fase 1** y bajan el MCC de cinco de seis;
en la fase 2 mejoran a cinco de seis en las 15 evaluaciones. Por tramo de peso la media es negativa en
la fase 1 sin tendencia; en la fase 2 la ganancia parece crecer con el peso, pero esa tendencia no se
sostiene (su intervalo incluye el cero) y se aplana al igualar los tramos por submuestreo.

El detalle por tramo de peso está en el Anexo C.

Dos explicaciones simples se **descartaron** con experimentos propios. **No es el tamaño de los
datos**: con el ajuste de la fase 2 reducido a 5,000 filas (el de la fase 1) la ganancia del `aft` es
+0.0105 en 14 de 15 evaluaciones, mayor que con el ajuste completo (+0.0057). **No es la granularidad
de la etiqueta**: con la etiqueta «molécula activa contra alguna diana» las huellas ayudan a los cuatro
modelos probados (AUROC +0.017 a +0.085).

![Rivales](figuras/f5_rivales.svg)

*Figura 5. Las huellas ayudan aunque se achiquen los datos o se cambie la etiqueta.*

Quedan en pie dos hipótesis. **La densidad del espacio químico** (que las huellas ganen donde hay muchos
vecinos) se midió a igual peso molecular y el resultado es **no concluyente**: la fase 2 es 1.8 veces
más densa que la 1 (61.9 contra 33.8 vecinos fuera del grupo), y en la fase 1 la pérdida por añadir
huellas se concentra en el tercio más disperso, pero las diferencias no superan su desviación. Y que
**la permeabilidad dependa de propiedades globales** que los descriptores ya capturan mientras la unión
depende de subestructuras: no está medida. Los resultados valen para esas familias de modelos y no
prueban qué pasa en la fase 1. Igualar los tramos de peso por submuestreo (decisión 1.3) quita el argumento
del tamaño de la molécula: la ganancia de las huellas no sigue a cuántos pares tiene cada tramo en el ajuste
(la relación no es monótona), y lo que mueve la diferencia entre tramos es la composición del ajuste y no
su tamaño total. Con una regla de baja potencia y un efecto original que no excluía el cero, eso es
«no se puede sostener» y no «se demostró que es densidad».

### 4.5 El modelo de potencia en NPASS

El AFT se eligió porque en los pares que solo tiene NPASS aprende de mediciones censuradas que los
demás descartan. En validación cruzada su concordancia ahí es 0.632 contra 0.511 del bosque. En la
prueba (117 pares) baja a 0.530 en la corrida registrada (0.511 al reajustarlo, que es lo que muestra
la figura) y la línea base de peso y TPSA da 0.565. Con 117 pares no hay potencia para distinguir 0.511
de 0.632, y los pares no son la misma población (12.3% de activos contra 44.4%): **no refuta el
resultado, pero tampoco lo confirma.** Además, su ventaja de MCC sobre el bosque (+0.155 con corte fijo)
se reduce a +0.028 con un corte de igual prevalencia; sigue siendo positiva en las 15 evaluaciones y
coincide con su ventaja de AUROC (+0.012).

![AFT](figuras/f4_aft.svg)

*Figura 6. Izquierda: concordancia solo-NPASS. Derecha: ventaja en MCC del AFT sobre el bosque.*

Ningún otro brazo supera al `aft` en NPASS (filtrar los descriptores no cambia nada y quitarlos lo
empeora 0.041), y dos métodos de atribución independientes concuerdan en lo que pesa, con la diana en
primer plano y TPSA y los donadores de hidrógeno lejos (Anexo F).

*La operación de estos modelos —un cuaderno, no un servicio— está en la sección 5.*

## 5. Implementación y operación

**Qué se entrega: un cuaderno, no un servicio.** En la reunión del 3 de noviembre la patrocinadora
dijo que no habrá un punto de acceso productivo; lo que conviene es dejarle un cuaderno que ella
ejecute con sus propios compuestos. La entrada es una lista de SMILES; la salida, para cada
compuesto, la probabilidad de cruzar la barrera (fase 1), la potencia predicha contra cada una de las 26 dianas
(fase 2, una pActividad por diana y sin intervalo) y qué tan cerca queda de lo que los modelos vieron. **El cuaderno
no combina las dos fases en un ranking**: esa combinación sigue pendiente (decisión C.3), y cuando exista será
evidencia paralela y **no una cascada**, porque un BBB− no descarta un compuesto.

**Un segundo entregable: la vara con que se mide.** Además de los modelos, el proyecto deja una herramienta
para que la patrocinadora compruebe si **una tabla de columnas propia** —ómicas, propiedades calculadas con
otro programa— predice mejor que los descriptores, sin tocar el código del proyecto. La tabla se une a los
compuestos por SMILES canónico, se evalúa con la misma validación cruzada agrupada y se compara contra la
referencia pliegue a pliegue, con un control de ruido y el intervalo de Nadeau y Bengio
(`src/models/representaciones.py`, #297).

**Y una guía, porque la herramienta sola no basta.** Reúne lo que costó aprender sobre dos cosas. **Cómo
agrupar:** nunca al azar, que infla de 7 a 13 puntos, y por andamio y esqueleto juntos y no por andamio solo.
**Cómo medir:** una corrida no decide, las 15 evaluaciones comparten filas, «mejora en 10 de 15» tiene 49% de
potencia en el umbral que esa regla nombra, y el resultado se reporta por subgrupo. La guía dice también lo
único que la herramienta no puede verificar por nadie: que las columnas no se hayan calculado usando las
etiquetas, ni usando todas las filas a la vez.

El ejemplo que la acompaña usa datos reales y replica un hallazgo del propio proyecto: las tres propiedades de
los filtros de la literatura —TPSA, donadores de hidrógeno y peso— quedan 0.082 de MCC por debajo de los 151
descriptores (IC95% [−0.131, −0.034], mejoran en 1 de 15 evaluaciones). La herramienta es Python y no una
interfaz, y mide clasificación, no la regresión de supervivencia de la fase 2.

**Estado hoy.** Los dos modelos finales están guardados en `models/finales/` (unos 3 MB), con un módulo de
inferencia que no necesita los datos de entrenamiento, un script que los regenera y el cuaderno que los usa
(`notebooks/06_Uso_de_los_modelos.ipynb`, #261). Está comprobado que los descriptores calculados desde un
SMILES coinciden bit a bit con los de entrenamiento (150 moléculas de cada fase) y que el modelo recargado
reproduce al entrenado. Falta que el equipo los revise. El reajuste de la fase 2 con las filas de ajuste no
reproduce exactamente la cifra de la prueba (0.7234 contra 0.7200). **Con qué filas se entrenan** lo decide la curva de aprendizaje y la decisión del 4 de noviembre: **los
dos modelos se sirven con las filas de ajuste**. En la fase 1 la ganancia de usar el 100% sobre el 75% es
+0.002 de AUROC (meseta); en la fase 2 sigue subiendo (+0.0076 de concordancia en 15 de 15), y se renuncia a
esa ganancia a cambio de poder evaluar y repetir la cifra registrada.

![Despliegue](figuras/f7_despliegue.svg)

*Figura 7. Arquitectura de despliegue: la patrocinadora ejecuta un cuaderno local que llama a un módulo de inferencia y a dos modelos guardados; no hay servicio. Abajo, lo que mantiene el equipo.*

La Tabla 1 lista los requisitos para operar y quién responde de cada uno.

| requisito | por qué | responsable |
|:--|:--|:--|
| script que entrena y guarda los dos modelos finales, con el comando y los `sha256` de los datos | que cualquiera pueda reconstruirlos (`experimentos/README.md` ya lo hace para las corridas) | hecho (#261), por revisar |
| cuaderno de uso con SMILES propios | es la forma de operación acordada | hecho (#261), por revisar |
| **advertencia de extrapolación**: la similitud de cada compuesto consultado a su vecino más cercano de entrenamiento | una cifra de validación cruzada no describe a la química nueva; la escalera de la sección 4.2 muestra cuánto | hecho en el cuaderno (#261), por revisar |
| reentrenar al llegar datos nuevos y **reevaluar con la escalera**, no con un corte al azar | evita celebrar una cifra inflada | patrocinadora, con apoyo del equipo |
| evaluación externa con su conjunto de prueba | la prueba reservada es nuestra, no la de ella | **hecha una vez** con el `aft` final: concordancia 0.792 [0.787, 0.797] en 8,134 pares (`solo_npass` 0.667, 249 pares), pero **no comparable**: el 64.9% de sus pares tiene andamio ya visto; ver abajo |

Table: Requisitos para operar los modelos, por qué se piden y quién responde de cada uno. «Por revisar» indica lo que el equipo aún no ha revisado.

**La base externa de la patrocinadora (4 nov).** El archivo `Testeo` no comparte identificador ni SMILES canónico con el de
entrenamiento. Con el `aft` guardado, sin reentrenar, la concordancia en 8,134 pares de las 26 dianas del modelo es **0.792**
(IC95% remuestreando esqueletos: 0.787 a 0.797), mayor que el 0.720 de la prueba reservada; en `solo_chembl` 0.786, en `mixto`
0.615 y en `solo_npass` 0.667 (249 pares, Spearman 0.309). **Esa base no es comparable con la prueba reservada:** se separó por compuesto y no por
andamio, y el 64.9% de sus pares tiene un andamio que ya está en el ajuste (contra 0.5% en el control interno), con una similitud mediana al vecino
más cercano de 0.787 (0.679 en la validación de la misma fase). Que salga mejor es lo que predice la tesis del artículo, no una prueba de mejor
generalización. Los naturales siguen siendo el estrato débil. Es una lectura única; el control reconstruye los 70,384 pares del
entrenamiento sin diferencia.

**Qué se supervisa durante la operación.** Como no hay servicio, la supervisión es una revisión periódica de lo que
el cuaderno ya produce más una reevaluación cuando llegan datos etiquetados. Las referencias son cifras medidas en
este trabajo; **los umbrales de alerta son propuestas y no se midieron** (Tabla 2).

| aspecto | señal | referencia y alerta propuesta | responsable |
|:--|:--|:--|:--|
| extrapolación | proporción de los compuestos consultados cuya similitud al vecino más cercano de entrenamiento es menor que 0.31 | 0.31 es el corte del tercil más raro de la prueba (sección 4.3); si la mayoría de las consultas cae ahí, las cifras de validación no aplican | patrocinadora, con la advertencia del cuaderno |
| desempeño | AUROC y MCC (fase 1) y concordancia (fase 2) sobre datos etiquetados nuevos, con intervalo remuestreando grupos | 0.793, 0.339 y 0.720 en la prueba reservada; una caída mayor que la desviación entre pliegues pide revisar | equipo, al llegar datos |
| punto de operación | proporción declarada permeable al cortar en 0.5 contra la prevalencia de los datos nuevos | en el ajuste 70.9% contra 64.97%, y en la prueba reservada 79.3% contra 57.3%: la diferencia crece cuando la química cambia (sección 4.2) | equipo |
| integridad | `sha256` de modelos y datos contra `data/MANIFEST.json`; versiones del lock | el CI lo verifica en cada cambio; el reajuste de la fase 2 no repite la cifra de la prueba exactamente (0.7234 contra 0.7200) | equipo |
| datos y etiquetas | cuántos pares activos aporta cada fuente y qué concentración de corte se usa | el 10 µM es el de cribado heredado del archivo (decisión 2.3); NPASS es CC BY-NC, solo uso no comercial | patrocinadora y equipo |

Table: Qué se supervisa durante la operación: la señal, su referencia medida en este trabajo con la alerta propuesta, y el responsable.

**Riesgos y su mitigación.** Cinco, dos de ellos del modelo y de los datos:

1. **Química fuera de lo visto** (del modelo): una cifra de validación no describe a la química nueva. *Mitigación:*
   la advertencia de extrapolación del cuaderno y la reevaluación con la escalera, no con un corte al azar.
2. **Validez de las etiquetas** (de los datos): el corte de 10 µM es el del cribado heredado del archivo, no un
   umbral biológico, y la misma molécula cambia de clase según la concentración. *Mitigación:* se guarda el
   intervalo de potencia y no la etiqueta, de modo que cambiar el corte no reconstruye nada (decisión 2.10).
3. **Punto de operación**: un MCC a 0.5 exagera la caída bajo un cambio de distribución. *Mitigación:* el
   cuaderno entrega la probabilidad y no una clase.
4. **Reproducibilidad**: la misma regresión logística da 0.481, 0.489 o 0.497 de MCC según el sistema operativo y la
   versión de Python. *Mitigación:* un lock de dependencias, `sha256` de los datos y decidir con 15
   evaluaciones y su error, no con una corrida.
5. **Licencia**: NPASS es CC BY-NC. *Mitigación:* declarar el uso no comercial y revisar la licencia con la
   patrocinadora antes de cualquier otro uso.

**Dos límites que el cuaderno tiene que decir.** La advertencia de extrapolación es una heurística:
la similitud al vecino más cercano no anticipa bien la dificultad de la prueba (sección 4.3), así que
una similitud alta no garantiza un buen resultado. Y la probabilidad de la fase 1 **no se corta**: a 0.5 sería
un punto fijo que bajo un cambio de distribución cambia de sesgo (sección 4.2), y por eso el cuaderno entrega
la probabilidad y no una clase. **Uso no comercial**: NPASS es CC BY-NC. El **retorno de detectar un
buen candidato** va en el resumen ejecutivo como un supuesto, no como una cifra medida.

## 6. Conclusiones clave

1. **Los ensambles no mejoran al modelo simple en MCC ni AUPRC; no es un fracaso**, es el peldaño más bajo de una
   escalera donde el modelo nunca fue el factor grande. En AUROC, votación (+0.0139 [+0.0038, +0.0239]) y stacking
   (+0.0128 [+0.0023, +0.0233]) sí superan al `svm_rbf` con el intervalo corregido de Nadeau y Bengio, pero con Holm sobre
   diez comparaciones los valores p son 0.103 y 0.180: ninguno sobrevive. Acomodar el escalador dentro de la calibración
   del SVM no cambia nada (MCC 0.7015 contra 0.7017; AUROC y AUPRC idénticos).
2. **Una cifra de validación cruzada no describe a la química nueva**, y la similitud al vecino más
   cercano no basta para anticipar cuánto cae: en la fase 1 la prueba cae 12.6 puntos de AUROC, 10
   más de lo que su similitud predice; en la fase 2 la concordancia agregada baja de 0.761 a 0.720.
3. **La representación no se traslada entre fases**, y no por tamaño de datos, por tipo de etiqueta ni por
   el peso de la molécula; la densidad del espacio químico queda como pista sin confirmar.
4. **Para la patrocinadora:** usar el cuaderno para priorizar candidatos y no para descartarlos (un BBB− no
   excluye un compuesto); leer la probabilidad de la fase 1 junto con la advertencia de similitud y no como una clase;
   y medir cualquier mejora donde el resultado se mueve, que es qué tan lejos queda la química evaluada de la de
   entrenamiento (Figura 1), no solo con el modelo que se prueba. Ninguna de las formas de aprender de lo raro
   que probamos cerró la brecha. Para probar columnas nuevas hay una herramienta y una guía (sección 5) que
   aplican la misma validación agrupada, y son parte de lo que se entrega junto con los modelos.
5. **Trabajo futuro, ligado a lo medido.** Cinco cosas, cada una con la medición que la deja planteada:

   a. *El punto de operación.* Reportar el MCC con un corte de igual prevalencia junto al de 0.5 (0.4095
      contra 0.3385 en la prueba) y medirlo con una prevalencia de llegada conocida de los datos de la
      patrocinadora. El corte elegido en validación no sirve (decisión C.5).
   b. *Una evaluación externa separada por andamio y no por compuesto.* La base externa de la patrocinadora
      no mide generalización: el 64.9% de sus pares ya tiene su andamio en el ajuste.
   c. *Combinar las dos fases en el ranking*, como evidencia paralela, y medir si seleccionar con ambas supera
      a cada una por separado. Se puede comprobar sobre los 612 esqueletos con medición en los dos archivos
      que usan los modelos, que son 1,594 pares sobre 23 dianas: poca potencia, así que la regla de lectura
      tiene que admitir «no alcanza» como veredicto (decisión C.3).
   d. *Confirmar o descartar la densidad del espacio químico* como la razón por la que las huellas ayudan en
      la fase 2 y no en la 1, separándola de la composición del ajuste con varios sorteos por pliegue. Los
      tramos de peso ya se igualaron (decisión 1.3) y queda el control de rareza.
   e. *Medir el modelo de potencia con más pares de NPASS.* Con 117 no hay potencia para distinguirlo de la
      línea base (sección 4.5).

**Limitaciones.** Lo que acota lo que se puede concluir de aquí:

- La prueba reservada **se leyó catorce veces**, y los modelos finales están guardados a falta de la revisión
  del equipo.
- Las 151 columnas de la fase 1 se eligieron **con etiquetas de entrenamiento**, así que su sesgo de selección
  no es medible contra la dispersión.
- El efecto de agrupar **depende del modelo** (1.3 puntos de AUROC con el `svm_rbf` y 2.2 con el bosque) y de
  qué se llame «parecido».
- Los experimentos de la representación usan **una o cuatro familias** de modelos, no las seis de la fase 1.
- La atribución por subestructura **excluye 618 de 2,534 columnas**, todas huellas, por existir en menos de
  cinco pliegues.
- El `mlp` y el `bosque` **varían con la semilla** del modelo.
- **Ninguna corrida se diseñó para comparar las palancas de la Figura 1**, así que sus barras indican el orden
  de magnitud y no miden el efecto de cada factor por separado.
- Las tres formas de aprender de lo raro que probamos —repesar, pasar filas de la prueba al ajuste y
  recomponer— **usan un solo modelo**, el `svm_rbf`, y la segunda comparte las mismas 1,499 filas en sus 15
  sorteos.

## Referencias y anexos

**Fuentes de datos:** B3DB `meng2021b3db`; NPASS `zhao2023npass` y `lin2026npass`; CMAUP `hou2024cmaup`;
ChEMBL `zdrazil2024chembl`. **Representación y partición:** huellas de Morgan / ECFP `rogers2010ecfp`;
RDKit `rdkit`; andamios de Bemis–Murcko `bemis1996properties`. **La lección de la escalera:** la
partición por tiempo como estimación de la predicción prospectiva `sheridan2013`, y la validación por
bloques que corrige la subestimación del error cuando los datos tienen estructura `roberts2017crossvalidation`.
**Modelos y métricas:** XGBoost `chen2016xgboost`; la concordancia de Harrell `harrell1982yield`; la corrección de
Nadeau y Bengio para los intervalos de la validación cruzada `nadeau2003inference`.
**Código y datos.** Cada cifra tiene su corrida en `experimentos/` (parámetros, commit, `sha256` de los
datos, comando) y se repite con `experimentos/README.md`; las lecturas de la prueba reservada están en
`experimentos/prueba.csv`.

## Anexos

Cada anexo viene de una corrida registrada; su carpeta está en `experimentos/` del repositorio.

- **A. La escalera con seis modelos y con otra definición de «parecido».** La logística no se degrada menos que
  el `svm_rbf` de forma distinguible; con ECFP6 la caída es gradual y con atom-pair los peldaños estrictos no se
  pueden construir. Corridas:
  `2026-11-03-artemio-1.2-escalera-ampliada-permeabilidad`,
  `2026-11-04-artemio-1.2-escalera-definicion-de-parecido-permeabilidad`.
- **B. La línea base de peso y TPSA.** Corrida: `2026-11-03-artemio-1.5-prueba-por-rareza`.
- **C. Las huellas por tramo de peso**, con la figura de abajo.
- **D. El ranking de la fase 2 y la curva de aprendizaje.** Corridas:
  `2026-11-03-artemio-C.5-ranking-fase2-aft`,
  `2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales`.
- **E. La densidad del espacio químico a igual peso** (no concluyente), **los tramos de peso igualados por
  submuestreo** —el control que deja sin sostén la tendencia de la sección 4.4— y **cómo repetir cada
  corrida**, con tiempos y `sha256` de los datos. Corridas:
  `2026-11-04-artemio-1.3-huellas-por-densidad-del-espacio-quimico`,
  `2026-11-08-artemio-1.3-tamano-huellas-actividad-igualado`.

![Huellas](figuras/f3_huellas.svg)

*Figura C1. Cambio por añadir huellas, por tramo de peso. Magnitudes menores a 0.01 en la fase 2.*

**F. Los cuatro brazos del `aft` y la atribución.**

**Qué ve el modelo.** De los cuatro brazos con los mismos pliegues, ninguno supera al `aft` en NPASS:
filtrar los descriptores no cambia nada que se distinga del ruido (+0.002), y **quitar los descriptores y
dejar solo huellas y diana lo empeora en las 15 evaluaciones** (−0.041), aunque en el agregado empata. Esto
matiza la lectura del registro (1.3) de que en la fase 2 se pueden tirar los descriptores, porque las huellas
solas casi igualaban al brazo ancho: en el estrato por el que se eligió el modelo no se pueden.

**Qué pesa.** Dos métodos independientes, TreeSHAP (lee los árboles) y permutación (solo la salida),
concuerdan (Spearman 0.93; 12 de sus 15 columnas más importantes son las mismas). Pesan la diana (`MAOA`,
`MAOB`, `DRD2`, `LRRK2`, `BCHE`, el 15% de la atribución) y, en la química, la complejidad topológica
(`BertzCT`), la lipofilia y los halógenos. **TPSA y los donadores de hidrógeno, que dominan la
permeabilidad, no dominan la potencia** (lugares 44 y 165).

**Qué pesa en la fase 1.** Los dos métodos (permutación y KernelSHAP) miran el mismo `svm_rbf`; una versión anterior mezclaba la permutación con la impureza de un bosque, que son dos modelos, y se quitó. Coinciden en seis descriptores entre sus quince primeros (`fr_lactam`, `NumHDonors`, `NumAliphaticCarbocycles`, `VSA_EState3`, `fr_Ar_OH`, `fr_ether`), estables entre dos muestras de compuestos; la correlación entre los dos rankings completos es 0.37. Los donadores de hidrógeno entran (puesto 4 en ambos); **TPSA no** (40 por permutación y 10 por SHAP), porque comparte información con un racimo de columnas. No se afirma ninguna estructura: son seis nombres de descriptor, no un mecanismo.

**Por subestructura.** El modelo final no usa huellas, así que se repitió el diseño con el brazo que sí
(`aft_huellas`, que no mejora en NPASS). **Con cinco repeticiones de permutación sobre las 11,248 filas, los dos métodos concuerdan según la regla declarada**
(Spearman 0.577 sobre la unión de los 100 primeros, contra el 0.50 fijado de antemano, y 11 de 15 en común). Una medición previa con una
repetición sobre 1,500 filas había dado 0.378 y «no concuerdan»; era ruido de la permutación, no un resultado. En la intersección
hay dos subestructuras, un nitrógeno de anillo tipo piridina y un CH aromático vecino a ese nitrógeno, genéricas y frecuentes
(en el 57% y 21% de las moléculas): indican que el modelo usa heterociclos nitrogenados, no un farmacóforo específico. **No se
afirma ninguna subestructura específica.** Un límite declarado: 618 de 2,534 columnas (24.4%, todas huellas) existen en menos de
cinco pliegues y se excluyen de la intersección; ninguna estaba arriba.
