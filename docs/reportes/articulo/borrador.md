# Qué mueve el resultado al predecir la actividad de compuestos naturales

**Borrador del 4 de noviembre, tercera versión, para 6 a 8 páginas** (decisión del 4 de noviembre: el cuerpo
lleva un hilo y el detalle va a anexos). Cada cifra sale de una corrida registrada en
`experimentos/`; las figuras se generan con `scripts/figuras_articulo.py`. Las secciones 6 y 8 están escritas
en primera versión.

## 1. Resumen

Buscamos compuestos naturales con potencial neuroprotector con dos modelos en paralelo: uno que
clasifica si una molécula cruza la barrera hematoencefálica (fase 1) y otro que predice su potencia
contra una diana, usando también las mediciones censuradas (fase 2). Comparamos once modelos y
ningún ensamble mejora de forma distinguible al mejor modelo individual. Lo que sí mueve el resultado
es una lección conocida (`sheridan2013`), medida aquí con sus magnitudes: **cuánta semejanza se permite entre lo que
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
  conectividad, para que los estereoisómeros no caigan a los dos lados (1,048 grupos en la fase 1).

## 4. Métodos

**Modelos.** Once modelos de clasificación (de regresión logística a ensambles) y nueve de
regresión. Final de la fase 1: `svm_rbf` sobre 151 descriptores RDKit. Final de la fase 2: un
modelo de supervivencia acelerada (AFT, XGBoost) que aprende de las mediciones censuradas.

**Rigor.** Las reglas de decisión se escribieron antes de cada corrida y no se ajustaron después
(no están pre-registradas); cada corrida reproduce una cifra ya registrada como control, y cada
resultado nuevo se recalculó con un segundo código. Los intervalos remuestrean grupos, no filas. De
los seis modelos de la fase 1, cuatro (incluido el entregado) dan la misma predicción con cualquier
semilla; el `mlp` y el `bosque` no (desviación de 0.017 y 0.007 de MCC). La prueba reservada se leyó
**siete veces**, la última solo como SMILES, todas registradas en `experimentos/prueba.csv`; ningún
modelo se eligió después de verla.

## 5. Resultados

### 5.1 La escalera de semejanza

Entre los once modelos hay 4.2 puntos de MCC. Con el `svm_rbf`, pasar de pliegues al azar a pliegues
donde ningún compuesto de entrenamiento supera 0.4 de similitud con uno de validación cuesta 33.3
puntos (0.752 → 0.419). En validación cruzada, el modelo entregado da MCC 0.702 y AUROC 0.919.

![Escalera](figuras/f1_escalera.svg)

*Figura 2. AUROC por peldaño, seis modelos. La línea naranja es la prueba reservada (0.793).*

**La fase 2 muestra lo mismo, con una limitación del conjunto.** La concordancia del `aft` baja de
0.807 (por molécula) a 0.695 con similitud ≥ 0.6, siete veces la dispersión entre los modelos
competitivos. A 0.5 y 0.4 no se puede ni construir la partición: el 69% y el 90% de las filas caen en
un solo grupo. No hay manera de evaluar la fase 2 con química realmente nueva a esos niveles.

![Escalera fase 2](figuras/f6_escalera_fase2.svg)

*Figura 3. Concordancia del `aft` por peldaño; en gris, solo pares de NPASS.*

**Dos matices que el artículo tiene que llevar.** La *forma* de la escalera depende de cómo se defina
«parecido»: con ECFP6 la caída es gradual y con ECFP4 casi todo ocurre entre 0.6 y 0.5, aunque la caída
total es parecida (0.419 contra 0.434 de MCC); con atom-pair no se pueden construir los peldaños
estrictos. Y el MCC exagera: con el mejor corte posible sería 0.655 y 0.560 en los dos peldaños
estrictos, contra 0.486 y 0.419 con el corte fijo en 0.5. Un corte de igual prevalencia solo recupera
+0.047 en el primero, así que no es una solución.

### 5.2 La prueba reservada es más difícil de lo que su similitud predice

En la prueba el AUROC es 0.793 y el MCC 0.339 (1,499 compuestos). Su similitud media al vecino más
cercano (0.414) es mayor que la de la validación agrupada (0.384), así que por similitud tendría que
rendir *mejor*: reponderar las predicciones de validación a su distribución de similitud da un AUROC
esperado de **0.89**, y el real es **0.79**. La brecha de 0.10 no se explica por qué tan lejos queda de
lo visto; qué es, no está medido (candidatos: prevalencia, peso y polaridad, curación de los datos,
andamios raros a propósito).

Dentro de la prueba, la ventaja del modelo sobre una línea base de peso molecular y TPSA crece con lo
parecido que es cada compuesto (+0.036 en el tercil más raro, +0.106 en el más parecido; diferencia
+0.069, IC95% 0.011 a 0.124); en la fase 2 la diferencia es cuatro veces menor.

![Rareza](figuras/f2_rareza.svg)

*Figura 4. Ventaja sobre la línea base por tercil de rareza, con IC95% por bootstrap de grupos.*

### 5.3 La representación no se traslada entre fases

Las huellas Sort & Slice **no mejoran a ningún modelo de la fase 1** y bajan el MCC de cinco de seis;
en la fase 2 mejoran a cinco de seis en las 15 evaluaciones. Por tramo de peso la media es negativa en
la fase 1 sin tendencia y crece con el peso en la fase 2.

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
prueban qué pasa en la fase 1.

### 5.4 El modelo de potencia en NPASS

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

*La operación de estos modelos —un cuaderno, no un servicio— está en la sección 6.*

## 6. Implementación y operación

**Qué se entrega: un cuaderno, no un servicio.** En la reunión del 3 de noviembre la patrocinadora
dijo que no habrá un punto de acceso productivo; lo que conviene es dejarle un cuaderno que ella
ejecute con sus propios compuestos. La entrada es una lista de SMILES; la salida, para cada
compuesto, la probabilidad de cruzar la barrera (fase 1), la potencia predicha con su intervalo
(fase 2) y los dos juntos como evidencia paralela para un ranking, **no como cascada**: un BBB− no
descarta un compuesto.

**Estado hoy.** Los dos modelos finales están guardados en `models/finales/` (unos 3 MB), con un módulo de
inferencia que no necesita los datos de entrenamiento, un script que los regenera y el cuaderno que los usa
(`notebooks/06_Uso_de_los_modelos.ipynb`, #261). Está comprobado que los descriptores calculados desde un
SMILES coinciden bit a bit con los de entrenamiento (150 moléculas de cada fase) y que el modelo recargado
reproduce al entrenado. Falta que el equipo los revise. El reajuste de la fase 2 con las filas de ajuste no
reproduce exactamente la cifra de la prueba (0.7234 contra 0.7200). **Con qué filas se entrenan** lo decide la curva de aprendizaje y la decisión del 4 de noviembre: **los
dos modelos se sirven con las filas de ajuste**. En la fase 1 la ganancia de usar el 100% sobre el 75% es
+0.002 de AUROC (meseta); en la fase 2 sigue subiendo (+0.0076 de concordancia en 15 de 15), y se renuncia a
esa ganancia a cambio de poder evaluar y repetir la cifra registrada.

| requisito | por qué | responsable |
|:--|:--|:--|
| script que entrena y guarda los dos modelos finales, con el comando y los `sha256` de los datos | que cualquiera pueda reconstruirlos (`experimentos/README.md` ya lo hace para las corridas) | hecho (#261), por revisar |
| cuaderno de uso con SMILES propios | es la forma de operación acordada | hecho (#261), por revisar |
| **advertencia de extrapolación**: la similitud de cada compuesto consultado a su vecino más cercano de entrenamiento | una cifra de validación cruzada no describe a la química nueva; la escalera de la sección 5.1 muestra cuánto | equipo |
| reentrenar al llegar datos nuevos y **reevaluar con la escalera**, no con un corte al azar | evita celebrar una cifra inflada | patrocinadora, con apoyo del equipo |
| decidir si hay una evaluación externa con su conjunto de prueba | la prueba reservada es nuestra, no la de ella; puede solaparse con el entrenamiento | por asignar |

**Dos límites que el cuaderno tiene que decir.** La advertencia de extrapolación es una heurística:
la similitud al vecino más cercano no anticipa bien la dificultad de la prueba (sección 5.2), así que
una similitud alta no garantiza un buen resultado. Y la probabilidad de la fase 1 se corta en 0.5,
un punto fijo que bajo un cambio de distribución cambia de sesgo (sección 5.1): conviene mostrar la
probabilidad y no solo la clase. **Uso no comercial**: NPASS es CC BY-NC. El **retorno de detectar un
buen candidato** va en el resumen ejecutivo como un supuesto, no como una cifra medida.

## 7. Conclusiones y limitaciones

1. **Los ensambles no mejoran al modelo simple; no es un fracaso**, es el peldaño más bajo de una
   escalera donde el modelo nunca fue el factor grande.
2. **Una cifra de validación cruzada no describe a la química nueva**, y la similitud al vecino más
   cercano no basta para anticipar cuánto cae: en la fase 1 la prueba cae 12.6 puntos de AUROC, 10
   más de lo que su similitud predice; en la fase 2 la concordancia agregada baja de 0.761 a 0.720.
3. **La representación no se traslada entre fases**, y no por tamaño de datos ni por tipo de etiqueta;
   la densidad del espacio químico queda como pista sin confirmar.

Limitaciones: la prueba se leyó siete veces; los modelos finales todavía no se sirven; las 151
columnas de la fase 1 se eligieron con etiquetas de entrenamiento (sesgo no medible contra la
dispersión); el efecto de la agrupación depende del modelo (1.3 puntos de AUROC con el `svm_rbf`, 2.2
con el bosque) y de la definición de «parecido»; los experimentos de la representación usan una o
cuatro familias de modelos, no las seis de la fase 1; los dos métodos de atribución
no concuerdan a nivel de subestructura; el `mlp` y el `bosque` varían con la semilla del modelo; y ninguna corrida se diseñó para
comparar las palancas de la Figura 1.

## 8. Referencias y anexos

**Fuentes de datos:** B3DB `meng2021b3db`; NPASS `zhao2023npass` y `lin2026npass`; CMAUP `hou2024cmaup`;
ChEMBL `zdrazil2024chembl`. **Representación y partición:** huellas de Morgan / ECFP `rogers2010ecfp`;
RDKit `rdkit`; andamios de Bemis–Murcko `bemis1996properties`. **La lección de la escalera:** la
partición por tiempo como estimación de la predicción prospectiva `sheridan2013`; hay literatura
equivalente de validación por bloques en ecología que falta buscar y citar.

**Por añadir a `docs/referencias/bibliografia.bib` antes de maquetar** (no están y no se inventan
aquí): XGBoost (Chen y Guestrin, 2016), la concordancia de Harrell (Harrell et al., 1982) y la
corrección de Nadeau y Bengio (2003) para los intervalos.

**Código y datos.** Cada cifra tiene su corrida en `experimentos/` (parámetros, commit, `sha256` de los
datos, comando) y se repite con `experimentos/README.md`; las lecturas de la prueba reservada están en
`experimentos/prueba.csv`.

## Anexos

**A. La escalera con seis modelos y con otra definición de «parecido»** (E1+, E13): la logística no se
degrada menos que el `svm_rbf` de forma distinguible; con ECFP6 la caída es gradual y con atom-pair los
peldaños estrictos no se pueden construir. **B. La línea base de peso y TPSA** (E0). **C. Las huellas por
tramo de peso**, con la figura de abajo. **D. El ranking de la fase 2** (E5) y **la curva de aprendizaje**
(E8). **E. La densidad del espacio químico a igual peso** (E11, no concluyente) y **cómo repetir cada corrida**,
con tiempos y `sha256` de los datos.

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

**Por subestructura.** El modelo final no usa huellas, así que se repitió el diseño con el brazo que sí
(`aft_huellas`, que no mejora en NPASS). **Ahí los dos métodos no concuerdan según la regla declarada**
(Spearman 0.38 contra 0.50, aunque comparten 11 de 15; la permutación es ruidosa con ~2,270 columnas). Las
tres subestructuras que ven los dos son genéricas y frecuentes (un nitrógeno de anillo tipo piridina, un
CH aromático vecino a ese nitrógeno y un carbono de tipo carbonilo, en el 57%, 21% y 52% de las moléculas):
indican que el modelo usa heterociclos nitrogenados y carbonilos, no un farmacóforo específico. **No se
afirma ninguna subestructura específica.**
