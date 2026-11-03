# Esqueleto del producto de difusión

Documento de trabajo para la entrega 7 del 8 de noviembre de 2026. **No es el artículo**:
es dónde vive su argumento, su tabla de cifras y su mapa a la rúbrica mientras se escribe,
para que nada de eso exista solo en una conversación. Como `roadmap-mlops.md`, es interno y
no se publica en el sitio.

El artículo final sale en PDF desde la plantilla de LaTeX del curso (`Articulo.zip`), que
todavía hay que bajar.

## El eje: una sola decisión, y por qué esta

La rúbrica es explícita en lo que premia y en lo que castiga: **«destacando *la* decisión que
importó y su porqué, no todo lo que se hizo»**, y baja a «bien» lo que llama *enciclopédico:
cuenta todo*. Así que el artículo necesita una columna vertebral, no un recorrido.

La propuesta es esta:

> **En este problema, qué datos se usan, cómo se parten y cómo se representan mueven el
> resultado entre cinco y veinte veces más que elegir un modelo.**

No es una opinión. Es la escalera que el proyecto midió, ordenada por cuánto mueve el MCC de
la fase 1:

| qué se cambia | cuánto mueve | dónde está medido |
|:--|:--|:--|
| el modelo, entre familias | 1.5 puntos | [1.2](../../decisiones.md#d1-2) |
| añadir ensambles sobre el mejor individual | +0.9 puntos, **indistinguible** | `2026-11-01-artemio-1.5-ensambles-permeabilidad` |
| cómo se compiló RDKit en la máquina | hasta 0.6 puntos y **cuatro puestos** | `2026-10-29-{artemio,ingrid}-1.5-ensambles-permeabilidad` |
| el criterio de partición | **7.1 puntos** | [1.2](../../decisiones.md#d1-2) |
| evaluar sobre esqueletos nunca vistos | **el MCC se parte por la mitad** | `2026-11-01-artemio-1.5-modelo-final-permeabilidad` |
| la representación, en la fase 2 | las huellas **reemplazan** a los descriptores | [1.3](../../decisiones.md#d1-3) |

Leída así, la escalera convierte el resultado negativo en la evidencia central en vez de en
una disculpa: **que ningún ensamble mejore al modelo simple no es un fracaso del modelado, es
el peldaño más bajo de la escalera.**

### El capítulo principal: la representación

Dentro de ese eje, el hallazgo propio es que **las dos fases miden el mismo cruce de
representaciones y les sale al revés**:

- En la **fase 2**, la potencia contra una diana, las huellas mejoran a cinco de los seis
  modelos en las 15 evaluaciones, y el brazo de *solo huellas* queda a 0.002 o menos del
  brazo ancho en cuatro modelos y lo supera en dos. **Se pueden tirar los descriptores.**
- En la **fase 1**, la permeabilidad, no mejoran a ningún modelo, bajan el MCC de cinco de
  seis, y `descriptores+huellas` gana a `huellas` **en los seis**. **No se pueden tirar.**

La hipótesis que lo explica, y que es la aportación del artículo: **la representación tiene
que igualar la granularidad de la etiqueta.** En la fase 1 la etiqueta es una propiedad de la
molécula entera —cruza o no cruza—, así que resumirla *es* la tarea. En la fase 2 la etiqueta
describe un encuentro entre dos objetos, y ahí importa qué partes tiene cada uno.

### La explicación rival, que el artículo nombra

La [1.3](../../decisiones.md#d1-3) dice también que «la ganancia no está donde el proyecto la
necesita»: en la fase 1 las huellas ayudan en los compuestos **sin equivalente natural**, que
es el estrato más denso. Eso abre una explicación que no es química:

- **A** — la representación debe igualar la física del fenómeno.
- **B** — las huellas ganan donde el espacio químico está densamente muestreado, porque son
  una mejor llave de similitud. A favor de B: en la fase 2 el modelo que más gana es el `knn`.

B explica las dos asimetrías; A explica la de entre fases y tropieza con la de dentro de la
fase 1. **El artículo presenta las dos y dice cuál medición las separa**, que es el
[#215](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/215): estratificar por
tamaño de molécula con cortes fijos en daltons, e igualar los tramos por submuestreo para que
el experimento no vuelva a medir densidad.

## Las ocho secciones, y qué va en cada una

| # | sección | de dónde sale | qué aporta al eje |
|--:|:--|:--|:--|
| 1 | Resumen, 150–250 palabras | nuevo | tiene que comprenderse solo: problema, escalera, resultado |
| 2 | Contexto de negocio y problema | Avance 0 revisado | el cambio de enfoque: la fase 1 deja de ser filtro duro |
| 3 | Datos y preparación | Avances 1 y 2 | el peldaño de la partición, que es el más alto de los controlables |
| 4 | Metodología y modelos | Avances 3, 4 y 5 | la regla fijada antes de medir, y que no se bajó |
| 5 | Resultados y validación | Avance 5 | la prueba reservada contra la validación cruzada |
| 6 | Implementación y operación | **no existe** | arquitectura, requisitos con responsables, monitoreo |
| 7 | Conclusiones clave | — | la escalera, las limitaciones y el #215 como trabajo futuro |
| 8 | Referencias y anexos | `docs/referencias/` | 211 entradas en `bibliografia.bib` |

**Una incoherencia del material del curso que hay que resolver antes de maquetar:** la lista
de secciones pone «Implementación y operación» en la **6**, y la rúbrica dice que esos
elementos se evalúan «en la sección **5**». Son 25 puntos. Preguntarlo en la reunión del 3 de
noviembre; mientras tanto, escribirlo en la 6 y anunciarlo al final de la 5.

## La tabla de cifras decisivas

El criterio de 35 puntos pide «cifras exactas y consistentes con los notebooks calificados: la
métrica primaria final, el lift respecto al baseline, el umbral establecido, el resultado
observado y la brecha». Cada una con su corrida, que es lo que las hace verificables.

### Fase 1 · permeabilidad, modelo final `svm_rbf`

| cifra | valor | corrida |
|:--|--:|:--|
| MCC en validación cruzada | 0.7017 | `2026-11-01-artemio-1.5-ensambles-permeabilidad` |
| AUROC en validación cruzada | 0.9190 | ídem |
| umbral de la regla (MCC / AUPRC) | 0.073 / 0.041 | ídem — ver [#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188) |
| comparaciones que pasan la regla | **0 de 30** | ídem |
| mejor ganancia pareada observada | +0.0093 de MCC, 12 de 15 | ídem |
| **MCC en la prueba reservada** | **0.3385** | `2026-11-01-artemio-1.5-modelo-final-permeabilidad` |
| **AUROC en la prueba reservada** | **0.7928** | ídem |
| compuestos de la prueba | 1,499 | ídem |
| reproducibilidad en la misma máquina | 0.00e+00 de diferencia en MCC | las dos corridas de macOS |
| divergencia entre máquinas | 6 de 11 modelos se mueven | `2026-10-29-ingrid-1.5-ensambles-permeabilidad` |

### Fase 2 · potencia, modelo final `aft` censurado

| cifra | valor | corrida |
|:--|--:|:--|
| concordancia agregada, `bosque` | 0.7650 | `2026-10-31-antonio-2.13-comparativa-regresion-ensambles` |
| concordancia agregada, `aft` | 0.7610 | ídem |
| el agregado es 93% ChEMBL | 52,529 de 56,241 | ídem |
| concordancia en `solo_npass`, `bosque` | 0.5107 | ídem |
| concordancia en `solo_npass`, `aft` | **0.6322** | ídem |
| control sin censura, en `solo_npass` | 0.5073, pierde **60 de 60** pareadas | `2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura` |
| concordancia en la prueba reservada | 0.7200 | `2026-10-31-antonio-2.13-comparativa-regresion-ensambles` |

### Representación

| cifra | valor | corrida |
|:--|--:|:--|
| fase 2, huellas mejoran a | 5 de 6 modelos, en 15 de 15 | `2026-10-28-artemio-1.3-comparativa-regresion-huellas` |
| fase 1, huellas mejoran a | ninguno | `2026-10-28-artemio-1.3-comparativa-permeabilidad-huellas` |
| fase 1, ensambles con huellas | **0 de 27** comparaciones | `2026-10-31-artemio-1.3-ensambles-permeabilidad-huellas` |
| fase 1, la brecha con huellas | se ensancha en 7 de 9 modelos | ídem |
| atribución, lo que coinciden los dos métodos | `fr_lactam`, `NumHDonors`, `VSA_EState3`, `MolLogP` | `2026-11-01-ingrid-C.2-atribucion-fase1-con-nombres` |

## Las limitaciones que entran al relato

La rúbrica pide que estén «integradas al relato, no omitidas», y da puntos por ello. Las que
el proyecto midió y declara:

1. **El estrato de origen mide dos cosas a la vez.** Un natural cuyo registro no declara la
   estereoquímica cae en «análogo» sin diferencia estereoquímica real, así que «natural
   exacto» es más puro pero más pequeño de lo que debería
   ([#203](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/203)). Afecta a toda
   lectura por origen, que es el eje de los dos modelos finales.
2. **La matriz de descriptores no es idéntica entre máquinas**
   ([#166](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/166)).
3. **La explicabilidad no está cerrada**: falta el segundo método de atribución sobre
   fragmentos ([#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146)).
4. **La regla de mejora resultó conservadora en la fase 1**, y se reportó así en vez de
   bajarla.
5. **El umbral publicado no es el que su prosa define**
   ([#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188)); la conclusión
   no cambia, porque con el umbral mayor tampoco pasa nadie.
6. **Las etiquetas dependen de la concentración**: 10 µM es la concentración de cribado
   heredada del archivo, no un criterio del proyecto.

## Lo que todavía no existe y hay que construir

- **La sección 6 entera.** Arquitectura de despliegue con diagrama, requisitos de operación
  **con responsables** y qué se supervisa. La rúbrica sugiere valorar AWS, Azure, Google Cloud
  e IBM Watson.
- **El abstract**, que tiene que comprenderse de forma independiente.
- **La declaración de uso de IA** con herramienta, modelo y finalidad.
- **La plantilla de LaTeX**, sin bajar.

## Lo que depende de la reunión del 3 de noviembre

El eje de este esqueleto supone que **un resultado negativo bien medido puntúa**. Si la
dirección dice lo contrario, la escalera deja de ser la columna vertebral y hay que
reorganizar alrededor de lo que sí mejoró —la fase 2 con huellas y censura—, con la fase 1
como estudio de validación. Son dos artículos distintos y la respuesta llega cinco días antes
de la entrega.

Las otras dos respuestas que condicionan: si la sección de operación es diseño o despliegue, y
dónde se evalúa realmente.
