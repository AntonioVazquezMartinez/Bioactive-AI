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

> **Cuánta semejanza se permite entre lo que se entrena y lo que se evalúa mueve el resultado
> más que elegir el modelo: 33.3 puntos de MCC sobre el modelo que se entrega, contra 4.2 entre
> los once. La prueba reservada rinde como los peldaños más estrictos de la escalera (en AUROC),
> pero su similitud al ajuste no lo anticipa: es más difícil de lo que esa medida predice.**

*(Corregido el 4 de noviembre: la versión anterior decía «cae sobre esa escalera» y que lo raro de su
química explicaba la caída. E14 mostró que la similitud al vecino predice un AUROC de 0.89 y el real es
0.79; lo raro explica la ventaja de la fase 1 sobre la línea base de tamaño, no el nivel de la prueba.)*

La vara con la que se comparan todas las filas es **la dispersión entre los once modelos de
la comparativa de la fase 1, que es de 4.2 puntos de MCC** —de 0.6692 el `knn` a 0.7109 el
`stacking`—, medida en la corrida que se entregó.

### Lo que el equipo eligió

| qué se cambia | cuánto mueve el MCC | contra la dispersión entre modelos |
|:--|:--|--:|
| el modelo, entre los once | 4.2 puntos | — |
| añadir ensambles sobre el mejor individual | +0.9 puntos, **indistinguible** | 0.2× |
| el criterio de partición, con el `svm_rbf` entregado ([1.2](../../decisiones.md#d1-2)) | 1.9 puntos (7.1 con el bosque) | 0.45× |
| cuánta semejanza se permite entre entrenamiento y validación (la escalera de E1) | **33.3 puntos**, de 0.752 a 0.419 | **7.9×** |
| la representación, en la fase 2 ([1.3](../../decisiones.md#d1-3)) | las huellas **reemplazan** a los descriptores | no comparable |

### Lo que el problema impone

| qué cambia | cuánto mueve | |
|:--|:--|--:|
| cómo se compiló RDKit en esa máquina | hasta 0.6 puntos, y **0.0 en cinco de los once** | 0.1× |
| evaluar sobre esqueletos nunca vistos | **36.3 puntos**: el MCC se parte por la mitad | **8.7×** |

**Las dos tablas no son la misma escalera, y por eso van separadas.** Arriba hay palancas que
el equipo movió; abajo hay condiciones del problema. Juntarlas haría parecer que evaluar
sobre datos difíciles es una decisión de diseño, y la fila más llamativa del artículo está
precisamente en la tabla de abajo.

**Y una advertencia que el artículo tiene que llevar escrita:** *ninguna corrida se diseñó
para esta comparación*. Cada fila viene de una corrida distinta, con otro propósito y otra
base, así que indican el orden de magnitud y no miden el efecto de cada factor. La única fila
con un control propio es la de la representación, y la del tamaño de molécula que el
[#215](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/215) viene a añadir.

Leído así, el eje convierte el resultado negativo en la evidencia central en vez de en una
disculpa: **que ningún ensamble mejore al modelo simple no es un fracaso del modelado, es el
peldaño más bajo de una escalera donde el modelo nunca iba a ser el factor grande.**

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

> **Corregido el 4 de noviembre: esta hipótesis se puso a prueba y no se sostuvo.** Con la etiqueta
> **por molécula** («activa contra alguna diana») y los datos de la fase 2, las huellas siguen
> ayudando a los cuatro modelos probados (E10, #248), así que la granularidad de la etiqueta no es la
> causa. Y tampoco el tamaño de datos: con el ajuste de la fase 2 reducido a 5,000 filas la ganancia
> es mayor, no menor (E9, #247). **El artículo ya no debe presentar la granularidad como su
> aportación**: afirma solo que la representación no se traslada entre fases. La densidad del espacio
> químico se midió a igual peso (E11, #254) y es **no concluyente**; queda que la permeabilidad dependa
> de propiedades globales que los descriptores ya capturan, sin medir.

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
| 4 | Metodología y modelos | Avances 3, 4 y 5 | la regla escrita antes de correr —no pre-registrada— y que no se bajó |
| 5 | Resultados y validación | Avance 5 | la prueba reservada contra la validación cruzada |
| 6 | Implementación y operación | **no existe** | arquitectura, requisitos con responsables, monitoreo |
| 7 | Conclusiones clave | — | la escalera, las limitaciones y el #215 como trabajo futuro |
| 8 | Referencias y anexos | `docs/referencias/` | 222 entradas en `bibliografia.bib` |

**La aparente incoherencia de la sección 5 contra la 6 no existe, y la plantilla lo zanja.**
El `\section` de «Implementación y operación» es el **5**, no el 6. La plantilla declara que
«el resumen y las referencias no llevan número; las demás secciones sí», y lo demuestra con
`\setcounter{section}{3}` antes de «Resultados y validación» para que salga como **4**. Así
que es la **parte** 6 de ocho y la **sección numerada** 5: la rúbrica y la lista cuentan lo
mismo de dos maneras. Escribirlo en la 6 lo habría puesto dentro de Conclusiones, y son 25
puntos.

| parte | sección numerada |
|:--|--:|
| Resumen | *sin número* |
| Contexto de negocio y problema | 1 |
| Datos y preparación | 2 |
| Metodología y modelos | 3 |
| Resultados y validación | 4 |
| **Implementación y operación** | **5** |
| Conclusiones clave | 6 |
| Referencias y anexos | *sin número* |

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
| modelos que pasan la regla | **ninguno de 10**: cada uno se juzga en MCC y AUPRC a la vez; el AUROC no decide y las «30» comparaciones son casillas de tabla | ídem |
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
| concordancia en `solo_npass`, `aft`, **en validación cruzada** | **0.6322** | ídem |
| control sin censura, en `solo_npass` | 0.5073, pierde **60 de 60** pareadas | `2026-11-01-ingrid-2.13-comparativa-aft-huellas-y-censura` |
| concordancia en la prueba reservada, agregada | 0.7200 | `2026-10-31-antonio-2.13-comparativa-regresion-ensambles` |
| **concordancia en la prueba reservada, solo `solo_npass`** | **0.530**, sobre **117 pares** (114 exactos) | ídem |
| Spearman en la prueba reservada, solo `solo_npass` | 0.083 | ídem |

**Regla de cita para esta fase: el 0.6322 no viaja sin el 0.530 al lado.** El primero es de validación cruzada y **no está verificado sobre esqueletos nuevos**; el segundo es lo que pasó cuando se midió ahí, y es el único estrato que aterriza en el azar. La prueba no refuta el 0.6322 —con 117 pares no hay potencia para distinguir 0.530 de 0.632, y los 117 no son la misma población, porque la prevalencia de activos pasa del 12.3% al 44.4%— pero tampoco lo confirma. Citar uno sin el otro es afirmar más de lo que los números sostienen.

### Representación

| cifra | valor | corrida |
|:--|--:|:--|
| fase 2, huellas mejoran a | 5 de 6 modelos, en 15 de 15 | `2026-10-28-artemio-1.3-comparativa-regresion-huellas` |
| fase 1, huellas mejoran a | ninguno | `2026-10-28-artemio-1.3-comparativa-permeabilidad-huellas` |
| fase 1, ensambles con huellas | **0 de 27** comparaciones | `2026-10-31-artemio-1.3-ensambles-permeabilidad-huellas` |
| fase 1, la brecha con huellas | se ensancha en 7 de 9 modelos | ídem |
| atribución fase 1 (`svm_rbf` entregado), lo que coinciden los dos métodos | `fr_lactam`, `NumHDonors`, `NumAliphaticCarbocycles`, `VSA_EState3`, `fr_Ar_OH`, `fr_ether` (Spearman entre métodos 0.37; `MolLogP` sale de la intersección) | `2026-11-04-artemio-C.2-atribucion-fase1-svm-dos-metodos` |
| atribución fase 1, con el bosque (superada) | `fr_lactam`, `NumHDonors`, `VSA_EState3`, `MolLogP` | `2026-11-01-ingrid-C.2-atribucion-fase1-con-nombres` |
| atribución fase 2 (`aft` final), dos métodos | TreeSHAP y permutación concuerdan (Spearman 0.93) | `2026-11-04-artemio-2.13-atribucion-aft-treeshap-y-permutacion` |
| atribución fase 2 por subestructura (brazo `aft_huellas`), corrida definitiva | los métodos concuerdan: Spearman 0.577 sobre la unión de los 100 primeros y 11 de 15 en común, con cinco repeticiones de permutación; la medición previa con una repetición (0.378) era ruido | `2026-11-06-antonio-C.2-atribucion-fase2-con-nombres` (#281) |

### Prueba reservada, lecturas y rareza (E2)

Corrida `2026-11-03-artemio-1.5-prueba-por-rareza`. Terciles de similitud al vecino más cercano del ajuste, **dentro de cada tramo de peso**.

| cifra | valor |
|:--|:--|
| fase 1, ventaja de `svm_rbf` sobre peso y TPSA (AUROC) | +0.036 en lo más raro (incluye el cero), +0.067, +0.106 en lo más parecido |
| fase 1, diferencia de ventajas parecido − raro | **+0.069** (IC95% 0.011 a 0.124) |
| fase 2, diferencia de ventajas en concordancia | +0.018 (0.005 a 0.030), unas cuatro veces menor |
| fase 2, `solo_npass` en la prueba | `aft` 0.511 contra 0.565 de la línea base (117 pares); registrada 0.530 |
| lecturas de la prueba (`prueba.csv`) | 14, contadas de `prueba.csv`: fase 1 diez (evaluación, la octava lectura con su verificación independiente, dos accesos solo de SMILES —E1+ y E14—, E2, la proporción de andamios ausentes, las dos de la 1.11 —el reparto y su prevalencia— y el MCC a cuatro cortes con el umbral congelado en validación, C.5 y #191); fase 2 cuatro (dos de Antonio, E2 y la proporción de andamios ausentes) |

### Ranking (E5), tamaño (E6) y curva de aprendizaje (E8)

| cifra | valor | corrida |
|:--|:--|:--|
| enriquecimiento del `aft`, `todos` | 1.40 en el 1% (544 de 544), techo 1/tasa base = 1.40 | `2026-11-03-artemio-C.5-ranking-fase2-aft` |
| enriquecimiento del `aft`, `solo_npass` | 3.09 en el 1% (8 de 21, IC 1.6–5.2); ordenar por diana, 1.16 | ídem |
| huellas por tramo de peso, fase 1 | media negativa en los cuatro tramos, sin tendencia | `2026-11-03-artemio-1.3-tamano-huellas-permeabilidad` |
| huellas por tramo de peso, fase 2 | −0.0035, +0.0023, +0.0085, +0.0089 de concordancia, creciente | `2026-11-03-artemio-1.3-tamano-huellas-actividad` |
| curva de aprendizaje, fase 1 | +0.002 de AUROC del 75 al 100% (8 de 15): meseta | `2026-11-03-artemio-1.5-curva-aprendizaje-modelos-finales` |
| curva de aprendizaje, fase 2 | +0.0076 de concordancia (15 de 15): sigue subiendo | ídem |

### Partición y tamaño

Corrida `2026-11-03-artemio-1.2-escalera-agrupacion-permeabilidad`, sin tocar la prueba reservada. El detalle y sus límites están en la [1.2](../../decisiones.md#d1-2).

| cifra | valor |
|:--|:--|
| `svm_rbf`, AUROC según cómo se agrupa | 0.947 al azar → 0.919 actual → 0.835 con similitud ≥ 0.5 → 0.780 con similitud ≥ 0.4 |
| prueba reservada, AUROC | 0.793, entre las filas de similitud ≥ 0.5 y ≥ 0.4 **por su AUROC**; por su similitud al vecino más cercano (0.414) está al nivel de la fila ≥ 0.6 (0.422) |
| `logistica` menos `svm_rbf`, AUROC pareado | −0.013 al azar, +0.003 a ≥ 0.5 y +0.025 a ≥ 0.4; los dos últimos con intervalo que incluye el cero: ruido |
| línea base de solo peso y TPSA, AUROC | 0.847, contra 0.919 de `svm_rbf` |
| ventaja de `svm_rbf` sobre esa línea base | 0.032 en grupos de 2 a 4 filas, 0.076 en los de 5 o más |
| lo que sube la cifra al agrupar solo por andamio | 1.3 de AUROC con `svm_rbf`, 1.0 con `logistica`; los 2.2 de la 1.2 son del bosque |

**Qué aporta al relato.** La caída de 0.919 a 0.793 no es solo sobreajuste: la escalera de agrupamiento muestra cuánto cae un modelo cuando se le quitan los vecinos, pero **la prueba no es tan lejana al entrenamiento como la fila donde su AUROC cae**: algo más que la similitud explica su caída (E2). Y la línea base muestra que, donde la química es rara, el modelo sabe poco más que tamaño y polaridad. **Falta** repetir la línea base dentro de la prueba y separar rareza de tamaño (E2). La idea de que la `logistica` resiste mejor el agrupamiento estricto se probó con intervalo y no se sostiene en AUROC.

## Estructura: cuerpo, anexos y trabajo futuro

**Decisión del 4 de noviembre: el artículo del 8 lleva todo lo que tiene una corrida detrás.** El cuerpo sigue un solo hilo para que la rúbrica lea *la* decisión; los resultados completos van a anexos; dos artículos derivados quedan como trabajo futuro destilado. **La extensión quedó decidida el 4 de noviembre: 6 a 8 páginas** (entre las 3 de la plantilla y las 12 a 18 de la rúbrica), con el cuerpo de un solo hilo y el detalle en anexos A a F. **«Implementación y operación» va en la sección 6**, y la sección 5 cierra con una línea que remite a ella. **Los dos modelos se sirven con las filas de ajuste** (no con las de validación): en la fase 2 se renuncia a unos +0.007 de concordancia a cambio de poder evaluar y repetir la cifra registrada.

| parte | contenido | corridas |
|:--|:--|:--|
| **Cuerpo** | la escalera de agrupación (33.3 puntos sobre el modelo entregado); la prueba por rareza (E2); la representación entre fases, con el tamaño (E6); los modelos finales y sus límites | `…escalera-agrupacion…`, `…prueba-por-rareza`, `…tamano-huellas-*` |
| **Anexo A** | la escalera con seis modelos y las diferencias pareadas (E1+): la `logistica` no se degrada menos de forma distinguible | `…escalera-ampliada-permeabilidad` |
| **Anexo B** | la línea base de peso y TPSA (E0), por tramo y por tamaño del grupo | `…escalera-agrupacion…` |
| **Anexo C** | métricas de ranking de la C.5 en la fase 2 (E5) | `…C.5-ranking-fase2-aft` |
| **Anexo D** | la curva de aprendizaje y con qué filas se sirven los modelos (E8) | `…curva-aprendizaje-modelos-finales` |
| **Anexo E** | cómo repetir cada corrida, con tiempos y `sha256` de los datos | `experimentos/README.md` |
| **Trabajo futuro 1** | *Evaluar bien un clasificador de permeabilidad*: la escalera como metodología, el agrupamiento por similitud, la lectura por rareza. Falta: una segunda fuente de datos y el control por pre-registro | — |
| **Trabajo futuro 2** | *Qué representación para qué fenómeno*: tamaño contra densidad de datos. Falta: igualar los tramos por submuestreo, controlar la rareza, y el brazo de huellas solas del `aft` (E3) | — |

## Las limitaciones que entran al relato

La rúbrica pide que estén «integradas al relato, no omitidas», y da puntos por ello. Las que
el proyecto midió y declara, doce. **Las numeradas 7 a 9 son del mismo tipo: la prosa afirma más de lo que sus números sostienen**, que es el defecto que la auditoría encontró en el propio repositorio y que no debe repetirse en el artículo, que es público:

1. **El estrato de origen mide dos cosas a la vez.** Un natural cuyo registro no declara la
   estereoquímica cae en «análogo» sin diferencia estereoquímica real, así que «natural
   exacto» es más puro pero más pequeño de lo que debería
   ([#203](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/203)). Afecta a toda
   lectura por origen, que es el eje de los dos modelos finales.
2. **La matriz de descriptores no es idéntica entre máquinas**
   ([#166](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/166)).
3. **La explicabilidad por subestructura tiene un límite declarado**: los dos métodos concuerdan
   en el brazo con huellas de la fase 2, pero 618 de 2,534 columnas (24.4%, todas huellas)
   existen en menos de cinco pliegues y no pueden llegar arriba
   ([#146](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/146)).
4. **La regla de mejora resultó conservadora en la fase 1**, y se reportó así en vez de
   bajarla.
5. **El umbral publicado no es el que su prosa define**
   ([#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188)); la conclusión
   no cambia, porque con el umbral mayor tampoco pasa nadie.
6. **Las etiquetas dependen de la concentración**: 10 µM es la concentración de cribado
   heredada del archivo, no un criterio del proyecto.
7. **El resultado de los naturales en la fase 2 no está verificado sobre química nueva.** El 0.6322 es de validación cruzada. Sobre la prueba reservada la concordancia de los compuestos que solo tiene NPASS es 0.530 con 117 pares (114 exactos) y un Spearman de 0.083. Es el estrato que justifica elegir el `aft`, y es el único que aterriza en el azar cuando se mide sobre esqueletos nuevos. Va junto a toda cita del 0.6322, no en un anexo.
8. **El enriquecimiento en naturales no se puede presentar como resultado.** La lectura del gráfico 3 del 05b dice que el modelo alcanza 1.92× al 1% (el 85% del techo) en `solo_npass` y que los cortes al 1% y al 5% «certifican su utilidad práctica». El 1% de 117 pares es 1.17 compuestos, y la corrida registra que ahí se encontró el 0.0192 de los 52 activos, es decir **uno solo**. La propia auditoría lo dejó anotado como salvedad y es la única que no pasó a issue; «certifican» no se sostiene. `2026-11-01-antonio-2.13-cifras-graficos`.
9. **El AUPRC por estrato no es comparable entre filas** ([#187](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/187)): promedia dos clases distintas, así que ninguna cifra de AUPRC por estrato debe ir al artículo como si se pudiera leer contra la de otro estrato.
10. **La prueba reservada se leyó catorce veces, no «una».** Fase 1 diez: la evaluación, la octava lectura con su verificación independiente, dos accesos solo de SMILES (E1+ y E14), E2, la proporción de andamios, las dos de la 1.11 (el reparto y su prevalencia) y el MCC a cuatro cortes con el umbral congelado en validación (C.5, #191); fase 2 cuatro: dos de Antonio, E2 y la proporción de andamios. Ningún modelo se ajustó ni se eligió después de ver la prueba, y en la última el corte se congeló antes de leerla. Es lo primero que un revisor querrá verificar, y `prueba.csv` lo permite ([#200](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/200)).
11. **Los modelos finales todavía no se sirven.** `models/` está vacío: los dos se entrenan en los cuadernos y se descartan. El reajuste de la fase 2 no reproduce la prueba exactamente (0.7234 contra 0.7200). Entregar un modelo a la patrocinadora es trabajo del 9 al 15, con una decisión pendiente sobre con qué filas se sirve la fase 2 (E8).
12. **El efecto del agrupamiento depende del modelo.** El 2.2 de AUROC y el 7.1 de MCC son del bosque; con el `svm_rbf` son 1.3 y 1.9 ([#237](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/237)).

## Lo que todavía no existe y hay que construir

- **La sección 6 entera.** Arquitectura de despliegue con diagrama, requisitos de operación
  **con responsables** y qué se supervisa. La rúbrica sugiere valorar AWS, Azure, Google Cloud
  e IBM Watson.
- **El abstract**, que tiene que comprenderse de forma independiente.
- **La declaración de uso de IA** con herramienta, modelo y finalidad.
- ~~La plantilla de LaTeX, sin bajar.~~ Está en esta misma carpeta: `articulo.tex`,
  con APA 7 fijado y la bibliografía del proyecto por enlace simbólico.
- **Los modelos servidos y el cuaderno para la profesora**, del 9 al 15.

## Lo que salió de la reunión del 3 de noviembre

Notas del equipo, sin transcripción:

- **Prueba reservada:** profundizar. Medir el desempeño entre compuestos parecidos y raros, caracterizar los grupos y probar con el conjunto de prueba de la profesora.
- **Resumen ejecutivo:** supuestos, costo de pruebas y ROI de detectar un buen candidato.
- **Operación:** no habrá endpoint productivo; se le deja a la profesora un notebook.

La plantilla del curso numera «Implementación y operación» como sección 5, así que la incoherencia con la rúbrica que registra más abajo no existe. La extensión se decidió el 4 de noviembre en 6 a 8 páginas (la plantilla dice 3 sin anexos y la rúbrica 12 a 18). No se habló de la hipótesis de representaciones.

## Lo que dependía de la reunión del 3 de noviembre

El eje de este esqueleto supone que **un resultado negativo bien medido puntúa**. Si la
dirección dice lo contrario, la escalera deja de ser la columna vertebral y hay que
reorganizar alrededor de lo que sí mejoró —la fase 2 con huellas y censura—, con la fase 1
como estudio de validación. Son dos artículos distintos y la respuesta llega cinco días antes
de la entrega.

Las otras dos respuestas que condicionan: si la sección de operación es diseño o despliegue, y
dónde se evalúa realmente.
