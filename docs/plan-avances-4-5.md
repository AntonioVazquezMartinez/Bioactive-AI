# Plan de ejecución · Avances 4 y 5

Plan interno de trabajo, igual que [`roadmap-mlops.md`](roadmap-mlops.md): **no se publica en el sitio** y no sustituye a nada. Lo que aquí se decida y cambie una decisión se escribe en [`decisiones.md`](decisiones.md) en el mismo PR; lo que sea trabajo abierto se vuelve issue. Este archivo solo ordena el trabajo de dos semanas.

| Entrega | Fecha | Qué se entrega |
|:--|:--|:--|
| Avance 4 · Modelos alternativos | domingo 25 de octubre | liga a `notebooks/04_Models.ipynb` |
| Avance 5 · Modelo final | domingo 1 de noviembre | liga a `notebooks/05_Modelo_Final.ipynb` |

Entre las dos hay una reunión semanal, y en ella la asesora pregunta por decisiones. Eso es parte del entregable, no un trámite.

## 1. La lectura de «no ensambles», y por qué cambia el plan

El Avance 4 pide seis modelos «individuales, **no ensambles**». El Avance 5 pide al menos cuatro ensambles que cubran estrategias **homogéneas y heterogéneas**, usando como base los mejores modelos individuales del avance anterior.

Leídas juntas, las dos instrucciones no dejan ambigüedad: un bosque aleatorio es un ensamble homogéneo por construcción, y el boosting también. Los dos pertenecen al Avance 5 y **no cuentan entre los seis del Avance 4**.

Esto corrige la lectura contraria, que es la habitual en otros cursos y la que se consideró primero. La consecuencia es concreta: de las tres canalizaciones del baseline, **solo la logística sirve como modelo individual**. No vamos 3 de 6, vamos 1 de 6.

**Cómo se cubre la duda sin apostar:** los seis individuales son familias sin ensamble, y bosque y boosting aparecen en la tabla del Avance 4 como referencia del Avance 3, etiquetados como ensambles y fuera del conteo. Si la asesora lee lo contrario, la tabla ya los trae. Se pregunta en la reunión de todas formas.

## 2. Qué pide cada avance y cómo vamos

### Avance 4

| Criterio | Puntos | Estado |
|:--|--:|:--|
| 6 modelos individuales, ordenados por la métrica principal | 60 | catálogo de 8 familias sin ensamble; **elegir 6 es H1** |
| Métrica principal más dos, y **tiempos de entrenamiento** | incluido | 4 métricas y los tiempos, en la tabla comparativa |
| Ajuste fino de los dos mejores | 30 | la búsqueda anidada corre; **la rejilla es H3** |
| Modelo individual final, argumentado más allá de la métrica | 10 | evidencia sí, argumento no |

### Avance 5

| Criterio | Puntos | Estado |
|:--|--:|:--|
| 4 ensambles, homogéneos **y** heterogéneos | 60 | bosque y boosting ya medidos cuentan como homogéneos |
| Comparativa con el mejor individual, ordenada, con tiempos | 20 | el constructor sirve igual; depende del Avance 4 |
| 4 gráficos del modelo final, cada uno interpretado | 20 | los cuatro ya se dibujan; falta interpretarlos |

## 3. Lo que ya está construido y no hay que repetir

| Pieza | Qué nos da |
|:--|:--|
| `src/evaluation/cv.py` | validación cruzada agrupada por andamio y esqueleto, 3 semillas × 5 pliegues, predicciones fuera de pliegue, desglose por subgrupo en la misma pasada |
| Las métricas del arnés | MCC, AUPRC de la minoritaria, AUROC y exactitud balanceada, por pliegue |
|  | la fase 2 es una regresión de la potencia con censura ([2.9](decisiones.md#d2-9)): concordancia de Harrell, Spearman y RMSE solo sobre las exactas, y la conversión a µM que invierte el sentido de la censura. Las de ranking (enriquecimiento al 1% y 5%, BEDROC, precisión en los 100 primeros) están propuestas en la [C.5](decisiones.md#dc-5) y aún no se implementan |
| `src/models/tareas.py` | las dos tareas con una llamada, y con el #113 el desglose por procedencia |
| `scripts/experimento_rubrica3.py` | brecha de ajuste, curvas de aprendizaje, dos métodos de importancia, pisos triviales |
| `src/tracking.py` y `experimentos/` | 9 corridas registradas con comando, entorno, métricas y parámetros |
| `tests/` y el CI | pruebas, orden secuencial de celdas, enlaces del sitio, manifiesto de datos |

Las dos tareas, con la prueba reservada fuera:

| Fase | Filas | Clase positiva |
|:--|--:|--:|
| 1 · permeabilidad | 6,306 | 65.0% BBB+ |
| 2 · actividad a 10 µM | 54,369 pares | 71.4% activos |

Las dos filas se cuentan sobre los pliegues de la semilla 0 de las corridas del Avance 3, `2026-10-18-artemio-1.5-baseline-permeabilidad-descriptores` y `2026-10-18-artemio-2.3-baseline-actividad-descriptores-diana-10um`.

## 4. El reparto: andamiaje con IA, criterio del equipo

La regla que separa las dos columnas es **temporal**: nada que dependa de un número se escribe antes de que el número exista. El andamiaje es todo lo que se puede construir sin haber visto un resultado.

### Andamiaje, con IA y declarado

Al 21 de octubre está hecho todo menos lo que depende de H1 y H3.

| # | Qué | Por qué es andamiaje |
|:--|:--|:--|
| A1 ✅ | Cronometrar el ajuste dentro de `evaluar` y devolverlo como columna | plomería; cambia la firma de salida, no una conclusión |
| A2 ✅ | `src/models/alternativos.py`: ocho familias sin ensamble, cada una con su escalador dentro | catálogo; elegir seis sigue siendo H1 |
| A3 ✅ | `BusquedaAnidada`: la validación interna **también agrupa** | evita fuga; la rejilla la pone el equipo |
| A4 ✅ | `src/evaluation/graficos.py`: ROC, precisión-exhaustividad, matriz de confusión, importancias concordantes | dibuja lo que haya; no interpreta |
| A5 ✅ | `tabla_comparativa`, con la métrica principal como argumento | formato |
| A6 ◐ | `notebooks/04_Models.ipynb`: 28 celdas, con las de hallazgo **vacías** y marcadas. Falta la del 05 | estructura derivada del registro, no de la rúbrica |
| A7 ✅ | `docs/plantilla-declaracion-ia.md`, ya pegada como última celda del 04 | formato |
| A8 ✅ | `scripts/verificar_declaracion.py`, conectado al CI | comprobación |

### Criterio del equipo, sin IA

| # | Qué | Quién responde en la reunión |
|:--|:--|:--|
| H1 | **Cuáles seis familias** y por qué esas | quien la defienda |
| H2 | **Qué métrica principal** ordena la tabla, consistente con la C.1 | todos |
| H3 | **Rangos y presupuesto** de la búsqueda de hiperparámetros | quien la corra |
| H4 | La lectura de la comparativa, incluido si los intervalos se solapan y nadie gana | todos |
| H5 | El argumento del modelo final: interpretabilidad, costo, desempeño con naturales | todos |
| H6 | La interpretación de los cuatro gráficos del Avance 5 | quien los lea |
| H7 | Las tres decisiones y la tabla de contribución de la declaración | cada quien la suya |

El H4 importa más de lo que parece: el Avance 3 cerró con que ningún modelo gana porque los intervalos se solapan. Si eso se repite con seis, decirlo es el resultado, y la rúbrica del modelo final premia justamente el argumento que no es la métrica.

## 5. Qué del Avance 5 se adelanta ahora

Casi todo el andamiaje sirve dos veces, porque el Avance 5 pide **la misma tabla** con tiempos y **los mismos** modelos individuales como base del stacking.

- **A1, A4 y A5 son literalmente compartidos.** Los tiempos y la tabla ordenada los piden las dos rúbricas, y los cuatro gráficos del Avance 5 se escriben hoy porque el arnés ya devuelve predicciones fuera de pliegue.
- **A3 también.** El Avance 5 exige optimización de hiperparámetros de los modelos relevantes, así que la envoltura de búsqueda se escribe una vez.
- **Los ensambles homogéneos ya están medidos.** Bosque y boosting del baseline cubren esa mitad del criterio de 60 puntos; faltan los heterogéneos, que son votación y stacking sobre los mejores individuales del Avance 4.
- **La guarda de la prueba reservada, el issue #54, hay que cerrarla antes del Avance 5.** El objetivo 3.6 pide evaluar en datos no vistos, y es la única vez que se toca la prueba. Sin la guarda, el riesgo de tocarla dos veces es real.
- **Lo que no se adelanta** es el stacking concreto, porque su base son los dos mejores individuales, y esos no se conocen hasta el Avance 4.

## 6. Calendario

Hoy es miércoles 21. Propuesta de reparto; confírmenla ustedes.

| Día | Qué | Quién |
|:--|:--|:--|
| jue 22, mañana | Fusionar #113, #111 y #110. Parar el #98 hasta después del 25 | Artemio |
| jue 22 | A1, A2, A3, A5 y el esqueleto A6 de la libreta 04 | andamiaje |
| jue 22 | **H1 y H2 cerradas por escrito** antes de correr nada | los tres, 30 minutos |
| vie 23 | Corrida de los 6 individuales en fase 1, con tiempos, registrada | Antonio |
| vie 23 | A4, el módulo de gráficos, probado contra la corrida del baseline | andamiaje |
| sáb 24 | Ajuste fino de los dos mejores, con la rejilla de H3 | Artemio |
| sáb 24 | Auditoría de cifras de la tabla contra los CSV de la corrida | Pamela |
| sáb 24, tarde | H4 y H5 escritas a mano, mirando la tabla | los tres |
| dom 25, mañana | Declaración, ejecución secuencial en copia con el kernel del lock, revisión de todas las páginas | Pamela y Artemio |
| dom 25 | Entrega | quien tenga Canvas abierto |
| lun 26 a mié 28 | Ensayo de la reunión: cada quien defiende dos decisiones del registro | los tres |
| mié 28 | Issue #54, la guarda de la prueba | Antonio |
| jue 29 a vie 30 | Ensambles heterogéneos y la comparativa del Avance 5 | Artemio y Antonio |
| sáb 31 | Los cuatro gráficos interpretados a mano | Pamela |
| dom 1 nov | Declaración, ejecución secuencial, entrega | los tres |

El reparto no es cosmético. La tabla de contribución de la declaración pide una línea por integrante, y la evaluación de la reunión es individual. Hoy los commits están en 176, 54 y 12 entre tres personas.

## 7. Riesgos, con su medida

| Riesgo | Medida | Qué hacer |
|:--|:--|:--|
| El arnés exige `predict_proba` | la máquina de soporte no lo trae por omisión | calibrar o activar la bandera, y declarar el costo |
| Soporte cuadrático en la fase 2 | 54,369 pares | usar la variante lineal o el descenso estocástico, o submuestrear dejándolo dicho |
| Vecinos, soporte y perceptrón sin escalar | la 1.5 ya midió que sin escalar la logística agota iteraciones | escalador **dentro** de la canalización, siempre |
| Las semillas cambian la partición, no el modelo | lo dice el comentario de `cv.py`, que lo dejó para este avance | decidirlo y escribirlo; con seis familias los intervalos salen angostos |
| Ejecutar con el intérprete equivocado | una cifra de asimetría ya cambió por esto, de 154 a 150 de 201 | kernel del lock, desde `notebooks/`, sobre una copia |
| Presupuesto de cómputo | 6 familias × 3 semillas × 5 pliegues × 2 fases, más la búsqueda | decidir el jueves si la comparativa completa es solo fase 1 |

## 8. La declaración de uso de IA

Desde el Avance 4 cada libreta cierra con la declaración, en tres partes, según la plantilla de Canvas. Tres cosas que ya sabemos:

- **El alcance se declara por sección, no por celda.** Los números de celda se mueven en cada reejecución.
- **La columna de responsabilidad pide un cambio concreto**, no una promesa de haber revisado. El ejemplo oficial dice qué corrigieron y qué descartaron.
- **Las tres decisiones salen del registro**, comprimidas a una línea de justificación y una de alternativa descartada. El registro ya guarda las dos cosas.

Y hay algo que declarar con nombre: las auditorías del #113 las hizo un agente que no participó en la tarea, incluyendo la revisión de redacción que contrastó unas 90 cifras. Eso es más que fragmentos de código y va en la declaración tal como fue.

## 9. Lo que pasa al Avance 5

Del correo de la patrocinadora del 25 de octubre quedan pendientes los puntos siguientes. Ninguno es un criterio de la rúbrica del Avance 4, y todos importan cuando se evalúa el modelo final, así que pasan al Avance 5 en este orden:

| Orden | Qué | Dónde está escrito |
|:--|:--|:--|
| 1 | Las **sensibilidades**, declaradas de antemano: sin inferidas, solo dirección consistente, con y sin DrugMatrix, y el corte de 1 µM junto al de 10 µM. La declaración **ya está hecha** ([variable objetivo, §9](variable-objetivo-fase2.md)); falta medirlas | [2.11](decisiones.md#d2-11), [2.12](decisiones.md#d2-12) |
| 2 | **DrugMatrix:** el desempeño con y sin los 29,730 inactivos, y el análisis de esqueletos de los 772 compuestos | [2.12](decisiones.md#d2-12) |
| 3 | En la matriz: la **marca de las relaciones inferidas**, la **bandera de dispersión** mayor a cien veces y `direccion_consistente` para las 26 dianas | [2.10](decisiones.md#d2-10), [2.11](decisiones.md#d2-11) |
| 4 | Las **métricas de ranking** (enriquecimiento al 1% y 5%, BEDROC, precisión en los primeros 100, área bajo la curva de precisión-recall) y el análisis de escenarios, con la métrica principal declarada antes de ver resultados | [C.5](decisiones.md#dc-5) |
| 5 | Los **campos de la API de ChEMBL** (formato BAO, confianza, organismo, `action_type`), con caché y fecha de descarga, como filtro y descriptor del reporte, nunca como entrada; antes hay que medir cuánto cubren nuestras filas (en todo ChEMBL, `action_type` está en el 2.4% de las actividades) | [2.3](decisiones.md#d2-3), [2.11](decisiones.md#d2-11) |
| 6 | Los ensayos celulares como **anotación de citotoxicidad**, separada, para la priorización | [2.4](decisiones.md#d2-4), [C.7](decisiones.md#dc-7) |
| 7 | El método del 10% apartado, que debe compartir Jorge Uribe, y la partición por esqueleto en paralelo | [2.6](decisiones.md#d2-6) |

Lo que no alcance a medirse en el Avance 5 se declara en el informe como trabajo pendiente.

