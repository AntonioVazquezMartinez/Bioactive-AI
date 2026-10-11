# Guía del proyecto

Qué hace Bioactive AI, quién participa, cómo se organiza el trabajo y qué lecciones ya costó aprender. Para la teoría desde cero, los [fundamentos](fundamentos-desde-cero.md); para el contenido de los datos, [datos](datos-contenido.md); para el estado de cada decisión y lo que sigue abierto, el [registro de decisiones](decisiones.md); para los términos, el [glosario](glosario.md). Esta guía orienta y no sustituye a esos documentos. **Última verificación contra los datos y los documentos del repositorio: 7 de octubre de 2026.**

**El proyecto**
1. [Quiénes son y qué problema resuelven](#1-quiénes-son-y-qué-problema-resuelven)
2. [La pregunta central y las dos etapas](#2-la-pregunta-central-y-las-dos-etapas)
3. [Reglas de diseño que no se negocian](#3-reglas-de-diseño-que-no-se-negocian)
4. [Cómo se organiza el trabajo](#4-cómo-se-organiza-el-trabajo-metodología-y-calendario)

**El trabajo técnico**
5. [Decisiones técnicas ya tomadas, y por qué](#5-decisiones-técnicas-ya-tomadas-y-por-qué)
6. [Estado actual del repositorio](#6-estado-actual-del-repositorio)
7. [Trampas y advertencias para no repetir errores](#7-trampas-y-advertencias-para-no-repetir-errores)
8. [Pendientes y preguntas abiertas](#8-pendientes-y-preguntas-abiertas)

---

## 1. Quiénes son y qué problema resuelven

**El proyecto.** Bioactive AI es el Proyecto Integrador (TC5035.10) de la Maestría en Inteligencia Artificial Aplicada del Tec de Monterrey, hecho por el **Equipo 7**: Ingrid Pamela Ruiz Puga, Artemio Santiago Padilla Robles y José Antonio Vázquez Martínez.

**Profesora titular y patrocinadora.** Son dos personas con dos roles distintos. La **Dra. Grettel Barceló Alonso** es la profesora titular del curso y evalúa las entregas. La **Dra. Mariana Martínez Ávila**, del Departamento de Bioingeniería, es la patrocinadora: la investigadora que plantea el problema real y entregó los datos.

**El proceso de trabajo que el proyecto quiere mejorar.** Hoy, el laboratorio de la Dra. Martínez identifica candidatos a medicamentos neuroprotectores en tres pasos: (1) revisan literatura científica y bases de datos buscando compuestos reportados con alguna actividad interesante, (2) eligen, con su criterio experto, cuáles vale la pena ensayar, y (3) los prueban en el laboratorio. Este proceso tiene tres límites reales:

- **El espacio de búsqueda es gigantesco.** Solo una base de datos de productos naturales (COCONUT) tiene 738,829 moléculas distintas. Revisarlas una por una a mano no es viable.
- **La barrera hematoencefálica descarta a la mayoría de los candidatos** ([fundamentos](fundamentos-desde-cero.md), sección 2), y comprobar eso experimentalmente para cada compuesto es costoso.
- **La tasa histórica de éxito es muy baja** ([fundamentos](fundamentos-desde-cero.md), sección 4): la mayoría de lo que funciona en el laboratorio nunca funciona como medicamento real. Priorizar mejor antes de invertir en experimentos no es un detalle menor: es el principal cuello de botella del campo.

## 2. La pregunta central y las dos etapas

**La pregunta que responde el proyecto:** dado solamente el SMILES de un compuesto, ¿se puede predecir si llegará al cerebro, si tendrá actividad neuroprotectora, y explicar qué característica estructural sustenta esa predicción?

Esto se divide en dos etapas, ambas recibiendo el mismo SMILES como entrada. El equipo las plantea como **independientes**; ese planteamiento está pendiente de confirmar con la patrocinadora (decisión 5 del registro):

```
SMILES ──► vector de longitud fija ──┬─► Etapa 1: ¿cruza la barrera hematoencefálica? (BBB+ / BBB−)
        (descriptores + fingerprint) │
                                     └─► Etapa 2: ¿es activo sobre alguna de las 37 + 2 dianas de neuroprotección?
                                                   │
                                                   └─► Priorización final + atribución a subestructuras
```

**El punto de diseño más importante de entender:** la etapa 1 **no filtra** a la etapa 2. Un compuesto que sale BBB− no se descarta del análisis, porque existen estrategias conocidas de química farmacéutica para ayudar a un compuesto a cruzar después (convertirlo en un profármaco, modificarlo para que sea menos polar, usar nanopartículas transportadoras, etc.). Y el dato que lo cierra: solo 1,033 esqueletos tienen medición en los dos conjuntos, así que para el 99% restante la permeabilidad sería una **predicción sin verificar** — descartar con ella eliminaría candidatos con actividad real documentada. Por eso las salidas de ambas etapas se calculan y se conservan por separado, y solo se combinan al final, al momento de decidir qué candidatos priorizar. Lo que los datos respaldan con firmeza es que un BBB− no descarta al compuesto: solo 1,033 esqueletos tienen medición en los dos conjuntos, así que para el resto la permeabilidad sería una predicción sin verificar.

## 3. Reglas de diseño que no se negocian

Estas ideas aparecieron desde la primera reunión con los asesores y condicionan cada decisión técnica del proyecto:

- **La explicabilidad es un requisito, no un extra** ([fundamentos](fundamentos-desde-cero.md), sección 8). Sin poder decir *qué fragmento* de la molécula sustenta una predicción, el resultado no le sirve al laboratorio.
- **"No encontramos ningún patrón aprendible" es un resultado válido.** En la primera reunión se planteó que incluso no encontrar un patrón puede ser un buen resultado: se prefiere un resultado negativo honesto a un modelo forzado para que se vea bien. Dado el historial de fracasos del campo ([fundamentos](fundamentos-desde-cero.md), sección 4), reportar la ausencia de señal con rigor es, en sí mismo, un aporte.
- **La actividad depende de la concentración** ([fundamentos](fundamentos-desde-cero.md), sección 2, para la permeabilidad, y también aplica a la actividad biológica en general): el mismo compuesto puede pasar de "inactivo" a "activo" simplemente subiendo la dosis probada. El proyecto tiene que elegir y documentar un umbral de concentración para convertir mediciones en etiquetas binarias, y ser transparente sobre esa elección.

## 4. Cómo se organiza el trabajo (metodología y calendario)

El curso pide seguir la metodología **CRISP-ML(Q)**, un marco de trabajo por fases para proyectos de machine learning con control de calidad en cada paso, y usa los **5 principios de la OCDE** para validar modelos de este tipo (endpoint definido, algoritmo inequívoco, dominio de aplicabilidad, bondad de ajuste y predictividad, e interpretación mecanística) como lista de verificación final.

El trabajo se entrega en avances semanales (ver `docs/Entregas_canvas.md` para el detalle completo de fechas y rúbricas):

| Avance | Qué es | Fecha |
|---|---|---|
| 0 | Propuesta del proyecto | 27 de septiembre |
| 1 | Análisis exploratorio de datos (EDA) | 4 de octubre |
| 2 | Ingeniería de características y partición de los datos | 11 de octubre |
| 3 | Modelo de referencia (baseline) | 18 de octubre |
| 4 | Modelos alternativos | 25 de octubre |
| 5 | Modelo final | 1 de noviembre |

---



## 5. Decisiones técnicas

Cada decisión técnica, con su contexto, lo que se descartó, lo que cuesta, su estado y quién la toma, está en el [registro de decisiones](decisiones.md); esta guía no las repite. El resumen de una línea por decisión está en la tabla al inicio del registro, y la teoría que las sustenta, en los [fundamentos](fundamentos-desde-cero.md).

## 6. Estado actual del repositorio

El proyecto ya tiene trabajo real hecho, no es solo una estructura vacía:

| Avance | Entregable | Estado (7 de octubre de 2026) |
|---|---|---|
| 0 | Propuesta del proyecto | Entregado (PDF) |
| 1 | Análisis exploratorio de datos (`notebooks/01_EDA.ipynb`) | Entregado el 4 de octubre |
| — | EDA de la etapa 2 (`notebooks/01b_EDA_actividad_snc.ipynb`) | Hecho; acompaña al Avance 1 y no es un entregable |
| 2 | Ingeniería de características (`notebooks/02_Feature_Eng.ipynb`) | Notebook ejecutado y fusionado como propuesta, con la decisión de normalización por acordar con la patrocinadora; falta el reporte · vence el 11 de octubre |
| 3 | Modelo de referencia (baseline) | Pendiente · vence el 18 de octubre |
| 4–5 | Modelos alternativos y modelo final | Pendiente |

**Resultado ya obtenido de la partición por andamio** (Avance 2, sobre las 7,805 filas con clase, **sin filtrar por `group`** — ver [por qué ya no se filtra](datos-contenido.md)):

| Partición | Compuestos | Andamios distintos | % BBB+ |
|---|---|---|---|
| Entrenamiento | 5,557 | 1,741 | 64.0% |
| Validación | 749 | 498 | 72.0% |
| Prueba | 1,499 | 1,390 | 57.3% |

Se verificó que cero andamios y cero esqueletos de conectividad se repiten entre particiones distintas, que es justo lo que se busca con un scaffold split bien hecho. La prueba queda con menos BBB+ que el entrenamiento (57.3% contra 64.0%) porque los andamios raros —los que le tocan a la prueba— son menos permeables que los frecuentes; es una característica esperada del scaffold split, no un error, y no se corrige.

## 7. Trampas y advertencias para no repetir errores

Las trampas sobre los datos —el tamaño efectivo, los nombres como identificadores, los grupos A–D, las mediciones censuradas, el archivo completo contra el recibido— están en [los datos del proyecto](datos-contenido.md), junto a la evidencia. Las que quedan son de método:

1. Cualquier umbral, como el de TPSA, se calcula **solo con los datos de entrenamiento**, nunca con todo el conjunto, o se usa información de la prueba.
2. Un resultado BBB− no descarta un candidato: la etiqueta depende de la concentración ([fundamentos](fundamentos-desde-cero.md), sección 2).
3. Desconfiar de resultados muy favorables para la curcumina y su familia, y aplicar filtros PAINS antes de reportar un candidato ([fundamentos](fundamentos-desde-cero.md), sección 5).
4. **Usar siempre el archivo de la patrocinadora** como fuente de la etapa 1, no los archivos de B3DB que el equipo descargó. Esos quedan solo como verificación cruzada (ver el recuadro siguiente: es justo el error que ya cometimos una vez).
5. No elegir el umbral de actividad por el balance de clases que deja, que cambia según qué registros se miren; lo que justifica el corte es la concentración ([decisión 7](decisiones.md#d7)).

> ### Qué pasó el 4 de octubre, y por qué no se puede repetir
>
> El Avance 1 original (y esta guía, en su primera versión) se construyó sobre los archivos de B3DB descargados directamente por el equipo, no sobre el archivo curado de la patrocinadora. Con esos datos "crudos" se llegó a dos conclusiones que resultaron **falsas** al revisarlas contra el archivo correcto: que el grupo D significaba "etiquetas contradictorias", y que había 2 SMILES inválidos en el conjunto de trabajo. Ninguna de las dos era cierta en los datos reales del proyecto — eran artefactos de usar el archivo equivocado.
>
> Peor todavía: sobre esa base equivocada, el Avance 2 adoptó un filtro (quedarse solo con los grupos A+B) que **empeoraba el desbalance de clases** en vez de mejorar la calidad de los datos, y nadie lo cuestionó a fondo durante varios días, porque la premisa de la que partía (que el grupo D era ruido) sonaba razonable y nadie la verificó contra el archivo correcto.
>
> El equipo lo detectó y lo corrigió el 4 de octubre: se re-centró el Avance 1 en el archivo de la patrocinadora, se quitó el filtro A+B del Avance 2, y se corrigió `CLAUDE.md`. De paso salió un hallazgo real y útil (la brecha de permeabilidad entre naturales y sintéticos, en [los datos](datos-contenido.md)).
>
> **La lección, para que no se repita:** cuando exista un archivo "oficial" entregado por quien patrocina el proyecto y una versión descargada por el propio equipo, **el archivo oficial manda siempre**, y cualquier análisis nuevo se verifica contra él antes de construir más cosas encima. Si algo que parece una verdad establecida (como "el grupo D son etiquetas contradictorias") nunca se contrastó directamente contra el archivo oficial, no se trata como un hecho: se marca como pendiente de verificar y se resuelve antes de seguir construyendo, no después.

## 8. Pendientes y preguntas abiertas

Lo abierto vive en dos sitios, y esta guía no los duplica: las **decisiones**, con su estado y quién decide, en [`decisiones.md`](decisiones.md), y la **consulta a la patrocinadora** en [`consulta-patrocinadora.md`](consulta-patrocinadora.md). El trabajo pendiente vive en los issues de GitHub, etiquetados por el avance que bloquean.

Las preguntas que más cambian cómo se construye el modelo, a la fecha:

- Qué criterio de «activo» usa la patrocinadora en la etapa 2 (decisión 7).
- Un modelo por diana, por categoría de enfermedad o multitarea (decisión 13).
- Reservar o no los 1,033 compuestos con medición en las dos etapas (decisión 10): cuesta el 25.7% de los datos de la etapa 1.
- Modelos separados para naturales y sintéticos, o el origen como variable.
- Si el archivo de actividad, que recibimos con el 89.9% de las filas, ya trae una partición de prueba reservada y cómo se hizo.

**Pendientes técnicos del equipo:** el reporte del Avance 2, el notebook del Avance 3 (baseline) y resolver los 154 nombres del conjunto de Spielvogel a estructuras químicas.
