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

**Vence el 11 de octubre de 2026 · reporte pendiente ([issue 24](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/24))**

**Análisis:** [notebook de características](../../notebooks/02_Feature_Eng.ipynb): descriptores, fingerprints, partición por andamio, normalización y selección de características.

Se entrega como **propuesta**: la normalización y la reducción de dimensión son la [decisión 12](../decisiones.md#d12), que decide la patrocinadora. El notebook ejecuta una opción, deja nombrada la alternativa y guarda la matriz filtrada en dos versiones, transformada y sin transformar.

## Próximas entregas

| Entrega | Fecha | Fase de CRISP-ML(Q) |
|:--------|:------|:--------------------|
| Avance 3 · Modelo de referencia | 18 de octubre | Ingeniería del modelo (a) |
| Avance 4 · Modelos alternativos | 25 de octubre | Ingeniería del modelo (b) |
| Avance 5 · Ensambles | 1 de noviembre | Ingeniería del modelo (c) |
