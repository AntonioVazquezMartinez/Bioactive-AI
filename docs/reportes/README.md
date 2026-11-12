# Entregables

Lo que el equipo ha entregado en el Proyecto Integrador, en orden cronológico: el reporte de cada avance y el análisis que lo respalda. Cada reporte se escribe en Quarto y se renderiza a PDF con typst; el `.qmd` fuente vive junto al PDF en el repositorio, así que cualquier cifra del documento se puede rastrear hasta el notebook que la produjo.

El calendario completo de entregas está en la [tabla de fases de CRISP-ML(Q)](avance-0/Avance0.7.pdf) del Avance 0.

## Avance 0 · Propuesta de proyecto

**Entregado el 27 de septiembre de 2026 · 17 páginas · [descargar PDF](avance-0/Avance0.7.pdf)**

**Análisis:** no tiene notebook; es la propuesta y la auditoría preliminar de los datos.

Formulación del problema, objetivos, involucrados y auditoría preliminar de calidad de los datos. Corresponde a la fase 1 de CRISP-ML(Q), entendimiento del negocio y de los datos.

Define la arquitectura de dos etapas —permeabilidad de la barrera hematoencefálica y actividad neuroprotectora— y fija una precisión de diseño que condiciona todo lo demás: **la etapa 1 no opera como filtro duro sobre la etapa 2**, porque un resultado BBB− no descarta al compuesto. También establece la explicabilidad a nivel de subestructura como requisito no negociable de la patrocinadora, y contiene el calendario de entregas del proyecto mapeado contra las fases de CRISP-ML(Q).

## Avance 1 · Análisis exploratorio de datos

**Entregado el 4 de octubre de 2026 · 15 páginas · [descargar PDF](avance-1/Avance1.0.pdf)**

EDA del conjunto de permeabilidad BBB curado por la patrocinadora.

**Análisis:** [notebook del EDA de permeabilidad](../../notebooks/01_EDA.ipynb), el entregable formal de la actividad, y su compañero [EDA de actividad en SNC](../../notebooks/01b_EDA_actividad_snc.ipynb), que hace lo mismo para la etapa 2 y no es un entregable aparte.

Sus tres resultados —el tamaño efectivo es menor que el número de filas, las categorías A–D no son una escala de calidad y los productos naturales cruzan la barrera menos— están desarrollados con sus cifras en [los datos del proyecto](../datos-contenido.md).

## Avance 2 · Ingeniería de características

**Entregable formal:** notebook ejecutado de principio a fin, con fecha de entrega del 11 de octubre. El PDF es un reporte complementario y permanece en borrador mientras se integran los comentarios del EDA y se consultan las decisiones pendientes ([issue #24](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/24)).

**Análisis:** [notebook de características](../../notebooks/02_Feature_Eng.ipynb): descriptores, fingerprints, partición por andamio, normalización y selección de características.

El EDA se extiende una semana, en paralelo con el cierre documental de ingeniería de características; no se pospone el notebook, que ya está ejecutado. El escalamiento medido se aplica a la regresión logística por convergencia y se omite en los árboles. Qué entradas necesitan el criterio de la patrocinadora está en [la Ruta](../decisiones.md), que es la lista única: aquí no se repite, porque dos listas de lo mismo se desincronizan.

Las integraciones de registro de corridas, manifiesto de datos y pruebas del flujo (#67, #71 y #73) refuerzan la trazabilidad sin alterar las salidas científicas del notebook. También se integró el registro retrospectivo de las mediciones de escalamiento y del vocabulario Sort & Slice de tamaño L, con sus parámetros, métricas y entorno.

## Avance 3 · Modelo de referencia

Entregado el 18 de octubre: [`notebooks/03_Baseline.ipynb`](../../notebooks/03_Baseline.ipynb). Las tres canalizaciones candidatas de la [1.5](../decisiones.md#d1-5) sobre las dos fases, con validación cruzada agrupada por estructura y desglose por estrato de procedencia.

Tres cosas que deja establecidas, y que condicionan cómo se leen las cifras siguientes:

- **Ninguna canalización gana.** Los intervalos del 95% se solapan; con una configuración por familia, declarar un ganador sería prematuro. Afinar es del Avance 4.
- **Cuánta semejanza se permite entre entrenamiento y validación mueve más que elegir modelo.** Agrupar solo por andamio, en vez de unirlo al esqueleto de conectividad, infla el AUROC 2.2 puntos y el MCC 7.1 con el bosque, pero solo 1.3 y 1.9 respectivamente con el `svm_rbf` que se entrega: ese efecto depende del modelo. Lo que sí es general es la escalera (`2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`): el `svm_rbf` baja de 0.752 de MCC con pliegues al azar a 0.419 cuando ningún compuesto de entrenamiento se parece más de 0.4 a uno de validación, 33.3 puntos.
- **El desempeño de la fase 2 no es un número.** Por estrato de procedencia: 0.855 de AUROC donde solo hay ChEMBL y 0.607 donde solo hay NPASS, que son los productos naturales que el proyecto existe para priorizar.

La prueba reservada no se ha mirado.

## Avance 4 · Modelos alternativos

Entregado el 25 de octubre: [`notebooks/04_Models.ipynb`](../../notebooks/04_Models.ipynb). Seis familias **sin ensamble** en las dos fases, ordenadas por la métrica principal, con los tiempos de ajuste y el ajuste fino de las dos mejores.

- **El modelo individual final de la fase 1 es el SVM con núcleo RBF, sin afinar**, con 0.703 de MCC. No gana por distinguirse: entre los dos afinados la diferencia es menor que la dispersión entre evaluaciones, así que gana por consistencia. Afinarlo no mejoró nada, y eso es un resultado: su `C` no tiene un óptimo estable, se acomoda a cada partición.
- **En la fase 2 el objetivo es la potencia, no una clase.** El corte de 10 µM no significa lo mismo en cada diana —deja a `LRRK2` en 98.1% de activos y a `NFE2L2` en 50.7%— y clasificar tira el orden dentro de cada clase, así que la fase 2 es una regresión con censura ([2.9](../decisiones.md#d2-9)) y la tabla de clasificación queda solo como referencia. Mejor concordancia de Harrell: kNN con 0.739.
- **La misma comparativa en dos máquinas da las mismas cifras a tres decimales, pero no los mismos tiempos** (el SVR, 247 s en una y 51 s en otra). La columna de tiempos solo se compara dentro de una misma corrida.

Dos análisis acompañantes miden qué añaden las huellas moleculares Sort & Slice, y la respuesta **depende de la fase** ([1.3](../decisiones.md#d1-3)): en la [fase 2](../../notebooks/04c_Regresion_actividad_huellas.ipynb) mejoran a cinco de los seis modelos en las 15 evaluaciones y en buena medida *sustituyen* a los descriptores; en la [fase 1](../../notebooks/03c_Permeabilidad_huellas.ipynb) no mejoran a nadie y ensanchan la brecha entre entrenamiento y validación. En las dos fases la ganancia se concentra donde el proyecto no la necesita: en los pares que solo tiene ChEMBL y en los compuestos sin equivalente natural.

Hasta aquí la prueba reservada no se había mirado: se toca una vez por fase, en el Avance 5.

## Avance 5 · Modelo final

Entregado el 1 de noviembre, en tres cuadernos: [`05_Modelo_Final`](../../notebooks/05_Modelo_Final.ipynb) (fase 1, permeabilidad), [`05b_Ensambles_actividad`](../../notebooks/05b_Ensambles_actividad.ipynb) (fase 2, potencia) y [`05c_Ensambles_permeabilidad_huellas`](../../notebooks/05c_Ensambles_permeabilidad_huellas.ipynb) (las huellas sobre los ensambles de la fase 1). El 05b lleva el modelo final de la fase 2 aunque su letra lo haga parecer un acompañante.

- **El modelo final de la fase 1 es el `svm_rbf`, y lo decide la regla, no la tabla.** La regla de mejora se escribió antes de correr la comparación, no está pre-registrada, y **ninguna de las 30 comparaciones la pasa**, así que el final es el mejor individual. No es la primera fila: el `stacking` y la `votacion` quedan por encima en la media, con intervalos de AUROC que se solapan por completo. Desglosada por origen, la ventaja de los ensambles vive casi entera en los compuestos sin equivalente natural, que son los que el proyecto no prioriza.
- **La cifra que se defiende es la de la prueba reservada.** En validación cruzada el `svm_rbf` da 0.9190 de AUROC y 0.7017 de MCC; sobre los 1,499 compuestos reservados, **0.7928 y 0.3385**. La partición de prueba trae los andamios raros a propósito, así que la distancia mide cuánto de lo que promete la validación cruzada sobrevive a un esqueleto que el modelo no vio.
- **El modelo final de la fase 2 es el `aft` censurado, y no el que gana el promedio.** El `bosque` gana la concordancia agregada (0.7650 contra 0.7610), pero ese agregado es 93% ChEMBL. En los pares que solo tiene NPASS el `bosque` queda en 0.5107 y el `aft` en 0.6322 en validación cruzada; sobre la prueba reservada esos pares dan 0.530 con 117 compuestos, que ni refuta ni confirma ese 0.6322. Un control con la misma librería y sin pérdida censurada da 0.5073 y pierde las 60 evaluaciones pareadas: la ventaja es de la censura y no de XGBoost.
- **Las huellas, sobre los ensambles de la fase 1, no pasan la regla en ninguna de las 27 comparaciones**, y cambian qué familia de ensamble parece la mejor: sin ellas mandan los heterogéneos, con ellas los de árboles ([1.3](../decisiones.md#d1-3)).
- **La misma comparativa en dos máquinas no da lo mismo.** Con el mismo commit, el mismo archivo de versiones fijadas y los mismos metadatos, cambia solo la huella de la matriz de descriptores ([#166](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/166)), y con ella se mueven seis de los once modelos. El `svm_rbf` es uno de los cinco que salen idénticos.

La prueba reservada se tomó una vez en la fase 1 y quedó registrada con su motivo en `experimentos/prueba.csv`, igual que cada acceso de la fase 2, incluido el recálculo de las cifras de los gráficos. Una auditoría posterior abrió como issues, etiquetados `deuda`, las correcciones de prosa y de método que encontró.

## Próximas entregas

| Entrega | Fecha | Fase de CRISP-ML(Q) |
|:--------|:------|:--------------------|
| Producto de difusión · artículo de 12–18 páginas | 15 de noviembre, el equipo entrega el 13 | Evaluación y despliegue |
| Resumen ejecutivo · tres páginas para la dirección | 15 de noviembre | Evaluación y despliegue |

Las dos traen ya su plantilla del curso versionada, con APA 7 fijado y la bibliografía del
proyecto por enlace simbólico. Cómo se compila cada una, qué quedó decidido y qué falta está
en el repositorio, en `docs/reportes/articulo/README.md` y
`docs/reportes/resumen-ejecutivo/README.md`: son notas de trabajo y no se publican en el
sitio, igual que el esqueleto del artículo.

Las dos últimas no son libretas sino documentos en PDF, y entre las dos piden lo que el proyecto todavía no tiene escrito: una arquitectura de despliegue con su monitoreo, y una evaluación económica con beneficios mensuales, costo total de propiedad a doce meses y riesgos con su mitigación.

## Fuera del curso · artículo científico

Además del artículo que cubre la rúbrica, el mismo trabajo está escrito con la forma de un artículo de
investigación en `docs/reportes/articulo-cientifico/`: doble columna, estructura de introducción, datos, métodos,
resultados y discusión, y el hallazgo en el título en vez del nombre del proyecto. **No es un entregable del
curso** y existe para circular fuera de él: **9 páginas · [descargar PDF](articulo-cientifico/articulo-cientifico.pdf)**. Usa las mismas figuras y las mismas cifras que el entregable, con la
salvedad de que se edita a mano y la coincidencia entre los dos es manual; su README explica por qué y qué queda
pendiente.

## Póster

`docs/reportes/poster/poster.tex` es el póster de la presentación final (A1 horizontal, tres columnas), armado sobre la plantilla del curso con el encabezado, la paleta y la tipografía que pide. Se compila con `sh scripts/compilar_articulo.sh poster`. Las cifras son las del artículo y del resumen ejecutivo, y las dos figuras son las del artículo.
