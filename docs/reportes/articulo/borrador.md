# Qué mueve el resultado al predecir la actividad de compuestos naturales

**Borrador del 4 de noviembre.** Cada cifra sale de una corrida registrada en `experimentos/`; las
figuras se generan con `scripts/figuras_articulo.py`. Las secciones 6 y 8 están por escribir.

## 1. Resumen

Buscamos compuestos naturales con potencial neuroprotector con dos modelos en paralelo: uno que
clasifica si una molécula cruza la barrera hematoencefálica (fase 1) y otro que predice su potencia
contra una diana, usando también las mediciones censuradas (fase 2). Comparamos once modelos y
ningún ensamble mejora de forma distinguible al mejor modelo individual. Lo que sí mueve el resultado es **cuánta
semejanza se permite entre lo que se entrena y lo que se evalúa**: con el modelo que entregamos,
el MCC baja 33.3 puntos al exigir que ningún compuesto de entrenamiento se parezca más de 0.4 a uno
de validación, contra 4.2 puntos entre los once modelos. La prueba reservada, con química más
nueva, cae donde esa escalera predice (AUROC 0.793 contra 0.919 en validación cruzada), y cuánta de
esa caída es química rara depende de la fase. Las huellas moleculares no ayudan en la fase 1 y sí
en la 2, sobre todo en moléculas pesadas. El modelo de potencia, que se eligió por funcionar en
compuestos que solo existen en NPASS, no se sostiene en la prueba en ese grupo (117 pares).

![Qué mueve el resultado](figuras/f0_palancas.svg)

*Figura 1. Cada barra viene de una corrida distinta, con otro propósito; indican el orden de
magnitud, no miden el efecto de cada factor por separado.*

## 2. Problema

Un compuesto natural bioactivo solo sirve si llega al cerebro y si actúa sobre una diana. El
equipo con el Departamento de Bioingeniería necesita priorizar candidatos, no descartarlos: que una
molécula sea predicha **BBB−** no la excluye, porque esa predicción no está verificada para la
mayoría. Por eso los dos modelos son evidencia paralela que se combina en un ranking, no una
cascada.

## 3. Datos y partición

- **Fase 1:** 7,805 compuestos con clase del archivo curado de la patrocinadora (derivado de B3DB), 65% BBB+;
  6,306 para ajustar y validar, 1,499 reservados.
- **Fase 2:** 202,647 registros de actividad (ChEMBL, NPASS, CMAUP) convertidos en intervalos de
  potencia; 56,241 pares para ajustar y 13,944 reservados. Se guarda el intervalo, no una etiqueta,
  porque el umbral de 10 µM es una decisión que puede cambiar.
- **Partición.** Nunca al azar: se agrupa por andamio de Bemis–Murcko *unido* al esqueleto de
  conectividad, para que los estereoisómeros no caigan a los dos lados (1,048 grupos).

## 4. Métodos

**Modelos.** Once modelos de clasificación (de regresión logística a ensambles) y nueve de
regresión. Final de la fase 1: `svm_rbf` sobre 151 descriptores RDKit. Final de la fase 2: un
modelo de supervivencia acelerada (AFT, XGBoost) que aprende de las mediciones censuradas.

**Rigor.** Las reglas de decisión se escribieron antes de cada corrida y no se ajustaron después
(no están pre-registradas). Los intervalos remuestrean grupos, no filas. La prueba reservada se leyó
**seis veces** y quedó registrada en `experimentos/prueba.csv`; ningún modelo se eligió después de
verla. Todo se repite con los comandos de `experimentos/README.md`.

## 5. Resultados

### 5.1 La escalera de semejanza

Entre los once modelos hay 4.2 puntos de MCC. Con el `svm_rbf`, pasar de pliegues al azar a pliegues
donde ningún compuesto de entrenamiento supera 0.4 de similitud con uno de validación cuesta 33.3
puntos (0.752 → 0.419). El MCC del modelo entregado en validación cruzada es 0.702 y su AUROC 0.919.

![Escalera](figuras/f1_escalera.svg)

*Figura 2. AUROC por peldaño, seis modelos. La línea naranja es la prueba reservada: no es un
peldaño más, es el AUROC que obtuvimos al leerla.*

En la prueba reservada el AUROC es 0.793 y el MCC 0.339 (1,499 compuestos). El AUROC equivale a los
peldaños de 0.5 y 0.4. El MCC cae más porque corta en un punto fijo (0.5) sobre un cambio de
distribución, así que **la caída en MCC exagera la pérdida de discriminación**.

### 5.2 Cuánto es química rara

Dentro de la prueba, la ventaja del modelo sobre una línea base de peso molecular y TPSA crece
con lo parecido que es cada compuesto al entrenamiento (+0.036 en el tercil más raro, +0.106 en el
más parecido; diferencia +0.069, IC95% 0.011 a 0.124). En la fase 2 la diferencia es cuatro veces
menor (+0.018).

![Rareza](figuras/f2_rareza.svg)

*Figura 3. Ventaja sobre la línea base por tercil de rareza, con IC95% por bootstrap de grupos.*

### 5.3 La representación, y por qué no se puede trasladar entre fases

Las huellas de Morgan con Sort & Slice **no mejoran a ningún modelo de la fase 1** y bajan el MCC de
cinco de seis; en la fase 2 mejoran a cinco de seis en las 15 evaluaciones y sustituyen a los
descriptores. Por tramo de peso, en la fase 1 la media es negativa en los cuatro tramos, sin
tendencia; en la fase 2 la ganancia crece con el peso.

![Huellas](figuras/f3_huellas.svg)

*Figura 4. Cambio por añadir huellas, por tramo de peso. Magnitudes menores a 0.01 en la fase 2.*

Una hipótesis: la representación tiene que igualar la granularidad de la etiqueta. En la fase 1 la
etiqueta es de la molécula entera; en la fase 2 describe un encuentro entre dos objetos. **No es la
única lectura**: las huellas también pueden ganar donde el espacio químico está más denso. Lo que
separa las dos explicaciones es igualar los tramos de peso por submuestreo, y no está hecho.

### 5.4 El modelo de potencia en NPASS

El AFT se eligió porque en los pares que solo tiene NPASS aprende de mediciones censuradas que los
demás descartan. En validación cruzada su concordancia ahí es 0.632 contra 0.511 del bosque. En la
prueba (117 pares) baja a 0.530 en la corrida registrada (0.511 al reajustarlo, que es lo que muestra
la figura) y la línea base de peso y TPSA da 0.565. Con 117 pares no hay
potencia para distinguir 0.511 de 0.632, y los pares no son la misma población (12.3% de activos
contra 44.4%): **no refuta el resultado, pero tampoco lo confirma.** Además, su ventaja de MCC sobre
el bosque (+0.155 con corte fijo) se reduce a +0.028 con un corte de igual prevalencia; sigue
siendo positiva en las 15 evaluaciones y coincide con su ventaja de AUROC (+0.012).

![AFT](figuras/f4_aft.svg)

*Figura 5. Izquierda: concordancia solo-NPASS. Derecha: ventaja en MCC del AFT sobre el bosque.*

## 6. Implementación y operación

*Por escribir.* Sin servicio: un cuaderno que el equipo de la patrocinadora ejecuta con sus propios
compuestos, con modelos reentrenables y requisitos con responsable. Uso no comercial (NPASS es
CC BY-NC).

## 7. Conclusiones y limitaciones

1. **Los ensambles no mejoran al modelo simple; no es un fracaso**, es el peldaño más bajo de una
   escalera donde el modelo nunca fue el factor grande.
2. **Una cifra de validación cruzada no describe a la química nueva.** En la fase 1 la prueba
   reservada cae 12.6 puntos de AUROC; en la fase 2, la concordancia agregada baja de 0.761 a 0.720.
3. **La representación no se traslada entre fases**; la hipótesis de granularidad está por separar de la de densidad.

Limitaciones: la prueba se leyó seis veces; los modelos finales todavía no se sirven; las 151
columnas de la fase 1 se eligieron con etiquetas de entrenamiento (sesgo no medible contra la
dispersión); el efecto de la agrupación depende del modelo (1.3 puntos de AUROC con el `svm_rbf`,
2.2 con el bosque); y ninguna corrida se diseñó para comparar las palancas de la Figura 1.

## 8. Referencias y anexos

*Por escribir.* Bibliografía en `docs/referencias/bibliografia.bib` (211 entradas). Anexos A–E según
`esqueleto.md`.
