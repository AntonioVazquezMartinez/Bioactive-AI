# Consulta de decisiones a la patrocinadora

Versión del 10 de octubre de 2026. Redactada por Ingrid Pamela Ruiz Puga, revisada contra los datos y contra los diccionarios de la patrocinadora.

Cada punto enlaza a su entrada del [registro de decisiones](decisiones.md), donde está el contexto completo y lo que cuesta cada opción. `scripts/verificar_decisiones.py` comprueba que ninguna decisión con pregunta formulada quede fuera de este documento.

---

Dra. Martínez:

Antes del Avance 3 —baseline de la etapa 1, 18 de octubre— necesitamos su validación de las decisiones de diseño. Ninguna queda cerrada hasta que usted la revise, incluidas las que ya usamos para trabajar.

Primero, gracias por los diccionarios: la sección 7 del de actividad resolvió cómo tratar las mediciones censuradas, y el de permeabilidad nos ahorró rehacer la verificación de duplicados y de etiquetas contradictorias. Varias de las preguntas que teníamos preparadas salieron de la lista al leerlos.

**Necesitamos cuatro respuestas, porque cambian cómo se construye el modelo:**

| | Decisión | Registro |
|:--|:--|:--|
| **A** | Criterio de «activo» para la etapa 2 | [7](decisiones.md#d7) |
| **B** | Un modelo por diana, por categoría de enfermedad o multitarea | [13](decisiones.md#d13) |
| **C** | Validar la cadena completa o conservar datos de entrenamiento | [10](decisiones.md#d10) |
| **D** | Modelos separados para naturales y sintéticos, o el origen como variable | [5](decisiones.md#d5) |

## A · Etiquetado de la etapa 2

El `pChEMBL` solo existe para los registros de ChEMBL. Etiquetar únicamente por él dejaría fuera 15,293 registros de NPASS y CMAUP, 54,498 mediciones censuradas y 29,730 inactivos declarados por texto.

Proponemos tres vías, pendientes de ratificación: pChEMBL donde exista; concentración exacta para el resto, que recupera 12,809 registros de productos naturales; e inactivo declarado para los textos y los censurados. Para el corte de censura usamos provisionalmente 10 µM, la concentración modal y mediana del conjunto.

**Para los censurados aplicamos su criterio de la sección 7**, no uno nuestro: un `>` solo sirve como negativo si el límite es igual o mayor que el umbral de «activo». Su tabla muestra que con umbral de 1 µM quedan 59,859 negativos seguros (98%) y con 10 µM quedan 54,419 (89%), lo que favorece el umbral más estricto.

Indíquenos **qué criterio de «activo» recomienda** y si los `Not active` declarados por texto son negativos confiables. Esos dos puntos no están en el diccionario.

### Observaciones discordantes para una misma estructura y diana

Al agrupar por los primeros 14 caracteres del InChIKey (clave de conectividad, que no distingue estereoquímica) y por gen, el recuento exploratorio encuentra **1,810 pares discordantes con ≥ 5 y 2,426 con ≥ 6**: dentro del mismo par hay al menos una observación etiquetada activa y otra inactiva. Esos conteos usan la regla provisional de marcar el par como activo si cualquier observación es activa; no son una resolución validada ni el tamaño final del entrenamiento.

¿Considera comparables las mediciones de esos pares entre ensayos o fuentes? ¿Existe una jerarquía de evidencia que debamos aplicar —por ejemplo, según tipo de ensayo, concentración, fuente o calidad de la medición—, o hay casos que debamos tratar como inconclusos? Usaremos su criterio biológico para orientar una regla reproducible y compararemos el efecto de esa regla antes de cerrar el conjunto de modelado.

## B · Forma del modelo de la etapa 2

Son 37 dianas identificadas por gen, más los dos receptores completos (NMDA y GABA-A), con volúmenes muy distintos: Alzheimer tiene 52,676 registros y ELA 53.

Cuatro dianas de la lista no tienen datos suficientes para un modelo propio, según los conteos de su diccionario:

| Gen | Diana | Filas |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | 0 |
| `AIF1` | Iba1 | 0 |
| `GABRB2` | Receptor GABA-A, subunidad β2 | 1 |
| `TARDBP` | TDP-43 | 8 |

**Proponemos excluirlas del modelado y confirmarlo con usted.** `AIF1` además lo marca su diccionario como marcador, sin dirección de efecto.

Confírmenos si el modelo es **por diana, por categoría de enfermedad o multitarea**, y qué dianas son prioritarias.

## C · Encadenar las dos etapas

Su diccionario señala que las dos tablas son independientes y no hace falta cruzarlas. Es cierto a nivel de filas, pero sí comparten compuestos: **1,033 esqueletos tienen medición en ambas**, el 1.0% del conjunto de actividad y el 25.7% del de permeabilidad.

Es el único subconjunto donde se puede medir la cadena completa de extremo a extremo. Reservarlo obliga a sacarlo también del entrenamiento de la etapa 1, o habría fuga, y eso cuesta un cuarto de los datos de esa etapa.

Un BBB− no descartará al compuesto: eso lo respaldan los datos.

Lo que sí queremos confirmar con usted es el **encuadre**. El planteamiento inicial fue «si cruza, ¿tiene efecto?», en cascada. Nuestros datos sugieren tratarlas como dos evidencias que se combinan al final, pero es un cambio de diseño y no queremos darlo por hecho.

Defina si priorizamos **validar la cadena completa o conservar los datos de entrenamiento**, y cómo debe presentarse un compuesto con BBB− predicho pero actividad documentada.

## D · Naturales frente a sintéticos

El 43.1% del conjunto de permeabilidad son productos naturales por coincidencia exacta con COCONUT, y cruzan 18.9 puntos menos (52.7% contra 71.7% BBB+). La regla TPSA < 67 Å² y HBD ≤ 1 muestra una diferencia de 6.6 puntos entre los dos grupos, menor que la de la etiqueta.

Usamos la coincidencia exacta. Su diccionario distingue además **1,005 compuestos con análogo natural que difiere solo en estereoquímica**; indíquenos si deben contar como naturales.

Indíquenos si procede entrenar **modelos separados, un modelo con el origen como variable, o ambos**.

---

## El resto de las decisiones

**Archivo de actividad** ([30](decisiones.md#d30)). Se llama `..._Entrenamiento.csv`. Su diccionario describe 225,513 filas y recibimos 202,647, el **89.9%**, lo que indica que reservó cerca de un 10%. Necesitamos saber si existe una partición de prueba ya definida y cómo se hizo. Si fue aleatoria, hay compuestos casi idénticos en ambos lados y no sería comparable con una partición por andamio. Si existe, no construiremos la nuestra.

**Representación** ([4](decisiones.md#d4), en uso). Descriptores RDKit (203 utilizables de 217) más Morgan/ECFP4 de 2,048 bits. Evaluamos Sort & Slice, que evita colisiones de bits y permite atribuir una predicción a una subestructura concreta. Cubre el 84.8% de las subestructuras en entrenamiento y el 68.0% en prueba, y esa brecha crece con el vocabulario. Indíquenos si conoce una representación más eficiente o interpretable para productos naturales.

**Partición** ([3](decisiones.md#d3), en uso). Por andamio de Bemis-Murcko, agrupando por esqueleto de conectividad: 7,805 filas son 4,018 estructuras. Quedan 5,557 / 749 / 1,499 sin andamio ni esqueleto compartido. Confirme si debemos separar también por laboratorio o por fuente.

**Umbral de TPSA** (hallazgo). El óptimo sube con la diversidad: 66.8 Å² (publicado), 66.6 (grupo A), 83.6 (A+B), 101.9 (completo) y 107.0 (entrenamiento). Reproducimos la cifra publicada en su subconjunto, pero no es una constante. Aún no tenemos intervalos de confianza. Indíquenos qué rango considera razonable para naturales neuroactivos.

**Categorías de B3DB** ([2](decisiones.md#d2), en uso). Seguimos su indicación de no usarlas como filtro. Medimos además que filtrar a A+B bajaría la clase BBB− de 36.5% a 27.0%.

**Registros fenotípicos** ([14](decisiones.md#d14)). El 43.5% (88,098) son ensayos neuronales sin diana identificada. Los 114,549 restantes tienen una categoría de diana; 109,264 reciben etiqueta por las tres vías propuestas. Al excluir 4,810 sin gen y 327 sin clave de conectividad calculable, quedan 71,145 pares exploratorios, aún sin resolver discordancias ni construir la partición final. Proponemos mantener los fenotípicos en un análisis aparte, no descartarlos. Confirme si van dentro de un modelo específico, aparte o fuera del alcance.

**Sesgo por fuente** ([15](decisiones.md#d15), medido). NPASS y CMAUP son naturales y no traen pChEMBL; ChEMBL es sobre todo sintético y sí. El 65.4% de los naturales también aparece en ChEMBL, así que el riesgo se concentra en 1,445 compuestos. Su diccionario señala además que 33,574 de las filas censuradas a 10 µM vienen de DrugMatrix. Indíquenos qué otros sesgos de curación conoce entre las tres fuentes.

**Filtros PAINS** ([11](decisiones.md#d11)). Proponemos marcar, no excluir: 413 compuestos (5.3%) llevan alerta, con el doble de frecuencia entre naturales. Defina si se marcan o se excluyen, y qué otros filtros de reactividad o toxicidad aplican a naturales.

**Evaluación** ([16](decisiones.md#d16)). Reportaremos por diana y por origen, con MCC y AUPRC. Indíquenos qué error pesa más, un falso activo o un falso inactivo, y cómo debe presentarse el ranking para que sea accionable en laboratorio.

**Dianas** ([17](decisiones.md#d17)). Confirme si la lista sigue vigente más allá de las cuatro sin datos del punto B.

**Seis filas** ([18](decisiones.md#d18)) del archivo de permeabilidad traen logBB pero sin clase BBB —zidovudina, miltefosina y otras cuatro, según su diccionario—. Indíquenos si puede completarlas.

**Licencia** ([19](decisiones.md#d19)). NPASS es CC BY-NC (11,992 registros). Indíquenos si el proyecto tiene aspiraciones comerciales.

**Partición de la etapa 2** ([20](decisiones.md#d20)). Proponemos el mismo criterio por andamio, y disjunta por fuente si los datos lo permiten. Confirme si hay agrupaciones por familia química o laboratorio que debamos respetar.

Quedamos atentos a sus respuestas. Con A a D resueltas avanzamos el baseline sin riesgo de rehacerlo.

Equipo 7 · Bioactive AI
