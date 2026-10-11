# Registro de decisiones

Las decisiones técnicas del proyecto, cada una con su contexto, lo que se descartó y lo que cuesta. Incluye las que **cambiaron al medir**: la versión anterior queda visible y marcada, en vez de reescribirse en silencio.

::: {.callout-important}
## Nada aquí está en piedra

Ninguna decisión se considera cerrada hasta que **la patrocinadora la revise**. Por eso ninguna aparece hoy como *ratificada*: el equipo trabaja sobre decisiones **vigentes**, que son de trabajo y reversibles. Esto no es una formalidad — dos de ellas ya se revirtieron al contrastarlas con los datos.
:::

## Qué significa cada estado

| Estado | Significa |
|:--|:--|
| **Vigente** | Se trabaja sobre esta base. Reversible. |
| **Propuesta** | Hay una recomendación del equipo, pero no se está actuando sobre ella. |
| **Abierta** | No hay decisión y bloquea trabajo. |
| **Revisada** | Se decidió, se midió y cambió. Guarda la versión anterior. |
| **Ratificada** | La patrocinadora la confirmó. *Ninguna todavía.* |

Cada entrada dice además **quién decide**. Las que necesitan a la patrocinadora son las que viajan en la consulta que se le envía; el resto son del equipo.

Si un término no se entiende, el [glosario](glosario.md) lo define. El [mapa de linaje](linaje-datos.md) muestra qué documento de investigación sustenta cada decisión.

## Estado de un vistazo

| # | Decisión | Estado | Decide |
|:--|:---------|:-------|:-------|
| [1](#d1) | Fuente de la etapa 1: el archivo de la patrocinadora | Vigente | equipo |
| [2](#d2) | No filtrar por la columna de grupo A–D | Vigente · **revisada** | equipo |
| [3](#d3) | Partición por andamio, nunca aleatoria | Vigente | ambos |
| [4](#d4) | Descriptores RDKit más Morgan/ECFP4 | Vigente | ambos |
| [5](#d5) | La etapa 1 no opera como filtro duro | Vigente | ambos |
| [6](#d6) | MCC y AUPRC sobre la clase minoritaria | Vigente | ambos |
| [7](#d7) | **Etiquetado de la etapa 2** | **Abierta** | **patrocinadora** |
| [8](#d8) | Dos métodos de atribución independientes | Vigente | equipo |
| [9](#d9) | El sitio publicado como memoria del proyecto | Vigente | equipo |
| [10](#d10) | ¿Reservar los 1,033 compuestos comunes? | **Abierta** | **patrocinadora** |
| [11](#d11) | PAINS: marcar en vez de excluir | Propuesta | **patrocinadora** |
| [12](#d12) | Escalamiento y selección de características | **Abierta** | equipo |
| [13](#d13) | **Forma del modelo de la etapa 2** | **Abierta** | **patrocinadora** |
| [14](#d14) | Los 88,098 registros fenotípicos | Propuesta | **patrocinadora** |
| [15](#d15) | La fuente confundida con el etiquetado | Vigente · medida | equipo |
| [16](#d16) | Qué error cuesta más y cómo presentar el ranking | **Abierta** | **patrocinadora** |
| [17](#d17) | La lista de 39 dianas | **Abierta** | **patrocinadora** |
| [18](#d18) | Las 6 filas con logBB sin clase BBB | **Abierta** | **patrocinadora** |
| [19](#d19) | Licencia de NPASS: CC BY-NC | **Abierta** | **patrocinadora** |
| [20](#d20) | Partición de la etapa 2 | Propuesta | ambos |

De las veinte, **6 las decide el equipo, 9 la patrocinadora y 5 son compartidas**. Y **15 formulan una pregunta para ella**: las 14 que decide ella o ambos, más la [15](#d15), que decide el equipo pero necesita su conocimiento de las fuentes.

Esa última cifra es la que importa, porque **toda decisión con pregunta formulada tiene que aparecer en la [consulta](consulta-patrocinadora.md)**. Es lo que comprueba `scripts/verificar_decisiones.py`.

Por urgencia, las cuatro que cambian cómo se construye el modelo: [7](#d7), [10](#d10), [13](#d13) y la parte de naturales de [5](#d5).

---

## 1 · Fuente de la etapa 1: el archivo de la patrocinadora {#d1}

**Estado:** vigente · 4 de octubre · **Decide:** equipo

**Contexto.** El equipo descargó B3DB por su cuenta en septiembre y construyó el EDA inicial sobre esos archivos. El 25 de septiembre la patrocinadora entregó un conjunto curado derivado del mismo B3DB.

**Decisión.** La fuente primaria es `bbb_permeability_experimental.csv`. Los archivos descargados se conservan como verificación independiente de conteos, no como base del análisis.

**Por qué.** No es solo procedencia. El archivo de la patrocinadora trae los SMILES estandarizados, el esqueleto de conectividad precalculado y, sobre todo, el **cruce estructural con COCONUT**, que es lo único que permite separar productos naturales de sintéticos. Sin ese cruce no existe el hallazgo central del Avance 1.

**Consecuencias.** Las cifras del Avance 1 se rederivaron enteras: 7,805 filas en vez de 7,807, y 4,018 esqueletos en vez de 4,022. Los dos SMILES inválidos de B3DB no sobreviven a la curación, así que la reducción de 7,811 a 7,805 viene de filas sin clase, no de estructuras rotas.

---

## 2 · No filtrar por la columna de grupo A–D {#d2}

**Estado:** vigente · **revisada** el 4 de octubre · **Decide:** equipo

**Lo que se recomendaba antes.** `docs/referencias/02-datasets-bbb.md` leía las categorías A–D de B3DB como una escala de confiabilidad y proponía entrenar con A+B, usar C como aumentación y reservar D como diagnóstico. Esa recomendación sigue visible en ese documento, marcada como superada.

**Qué la revirtió.** El EDA del Avance 1, midiendo sobre los datos:

- El grupo D tiene **mediana de 3 referencias** contra **1** del grupo C. Tiene más respaldo, no menos.
- **Ningún registro duplicado** del conjunto lleva etiquetas contradictorias.
- La columna está confundida con la etiqueta: filtrar a A+B baja la clase minoritaria del **36.5% al 27.0%**.

**Decisión.** La columna se usa para describir y estratificar, **nunca para excluir**.

**Consecuencias.** El conjunto de entrenamiento pasa de 4,679 a 7,805 compuestos, un 67% más. Las caídas de AUC por partición por andamio son mayores que las medidas sobre A+B —logP pierde 0.198 contra 0.175— porque el conjunto es químicamente más diverso. El número anterior estaba inflado por un conjunto más homogéneo.

---

## 3 · Partición por andamio, nunca aleatoria {#d3}

**Estado:** vigente · **Decide:** ambos
**Pregunta:** ¿Hay razón experimental para separar también por laboratorio o por fuente, más allá del andamio?

**Contexto.** Una partición aleatoria reparte filas al azar, de modo que variaciones del mismo núcleo químico caen a ambos lados.

**Decisión.** Partición por **andamio de Bemis-Murcko**, agrupando además por esqueleto de conectividad para que los estereoisómeros no se separen. Los andamios frecuentes van a entrenamiento y los raros a prueba, que es la convención de DeepChem.

**Por qué.** Los andamios grandes tienen pureza de clase extrema: el más frecuente, de 410 compuestos, es 99.5% BBB+. Con partición aleatoria al modelo le basta reconocer el andamio. La literatura reporta que las particiones aleatorias inflan resultados entre 7 y 13 puntos.

**Consecuencias.** La prueba queda con 1,390 andamios distintos en 1,499 compuestos, casi uno por molécula. También queda con **57.3% BBB+ contra 64.0% del entrenamiento**: los andamios raros son menos permeables. El modelo se evalúa sobre una distribución distinta de aquella en la que aprendió, que es la situación realista.

**Detalle que costó caro.** Construida al revés —llenando la prueba con los andamios frecuentes— daba 45 andamios con el benceno ocupando el 26%. La dirección de la asignación es el detalle crítico.

---

## 4 · Descriptores RDKit más Morgan/ECFP4 {#d4}

**Estado:** vigente · **Decide:** ambos
**Pregunta:** ¿Conoce una representación más eficiente o más interpretable para productos naturales?

**Decisión.** 217 descriptores 2D de RDKit, de los que 203 resultan utilizables, más fingerprint Morgan/ECFP4 de 2,048 bits generado con `rdFingerprintGenerator`.

**Qué se descartó.** Los *embeddings* congelados de transformers preentrenados, que según la investigación no superan a esta combinación bajo partición por andamio.

**Consecuencias.** `Ipc`, el índice de contenido de información, se descarta: alcanza ~1e41, finito en float64 pero por encima del máximo de float32, y los modelos de sklearn convierten internamente. **Un chequeo de `isfinite` no lo detecta** y costó una ejecución fallida encontrarlo.

**Nota de API.** `radius=2` produce ECFP4, porque el número del nombre es el diámetro. Es la confusión más frecuente con esta familia.

---

## 5 · La etapa 1 no opera como filtro duro {#d5}

**Estado:** vigente · confirmada **por los datos**, no por la patrocinadora · **Decide:** ambos
**Pregunta:** ¿Cómo debería presentarse un compuesto con BBB− predicho pero actividad documentada?

**Lo que los datos respaldan.** Un resultado BBB− **no descarta** al compuesto. Eso está medido y es firme.

**Lo que no está confirmado.** Que de ahí se siga que las etapas sean *independientes* o *paralelas* es un reencuadre respecto al planteamiento original de los asesores, que las planteó como «si cruza, ¿tiene efecto?». La patrocinadora no lo ha confirmado, así que el registro no lo da por hecho.

**Por qué, razón original.** Existen estrategias consolidadas para favorecer el cruce: profármacos, lipidización, aprovechamiento de transportadores endógenos, nanoacarreadores.

**Por qué, confirmación empírica.** El EDA de la etapa 2 encontró que de los 99,585 esqueletos con actividad medida, **solo 1,033 tienen también medición de permeabilidad**: el 1.0%. Para el otro 99%, la permeabilidad sería una predicción sin verificar. Descartar con ella eliminaría candidatos con actividad real documentada.

---

## 6 · MCC y AUPRC sobre la clase minoritaria {#d6}

**Estado:** vigente · **Decide:** ambos
**Pregunta:** ver la decisión [16](#d16), que es donde se fija el punto de operación.

**Contexto.** El conjunto de permeabilidad tiene 1.74 positivos por cada negativo. Un modelo que prediga siempre BBB+ acierta el 63.5% sin haber aprendido nada.

**Decisión.** Métricas principales: **MCC** y **AUPRC calculada sobre la clase minoritaria**. La exactitud y el AUROC no se reportan solos.

**Error cometido y corregido.** El Avance 2 reportó AUPRC sobre la clase positiva, que es la mayoritaria, con línea base 0.573. Los valores de 0.70–0.86 parecían buenos y eran poco informativos. Queda documentado en el propio notebook en vez de corregirse en silencio.

---

## 7 · Etiquetado de la etapa 2 por tres vías {#d7}

**Estado:** ABIERTA · **revisada** el 7 de octubre · **Decide:** patrocinadora
**Pregunta:** ¿Qué criterio de «activo» recomienda? ¿Son confiables los inactivos declarados por texto? ¿Cómo debemos tratar las mediciones censuradas? Cuando un mismo esqueleto de conectividad y gen tiene observaciones activas e inactivas, ¿qué tipos de ensayo considera comparables y qué evidencia debe tener prioridad?

**Lo que se decía antes.** «pChEMBL ≥ 5 primario, ≥ 6 como robustez», sin especificar cómo etiquetar los registros sin pChEMBL.

**Qué lo corrigió.** El EDA de la etapa 2 mostró que el pChEMBL **solo existe para los registros de ChEMBL**. Etiquetar únicamente por él descarta en silencio:

| Qué se pierde | Registros |
|:---|---:|
| NPASS y CMAUP, las bases de **productos naturales** | 15,293 |
| Mediciones **censuradas** (`> X nM`) | 54,498 |
| **Inactivos declarados por texto** | 29,730 |

**Propuesta de trabajo, pendiente de ratificación.** Tres vías: pChEMBL donde exista; **concentración exacta** para el resto, que recupera 12,809 de los 15,293 registros naturales; e **inactivo declarado** para los textos y para los censurados con corte ≥ 10 µM. La regla de censura sigue el criterio que describe el diccionario; usar 10 µM como corte operativo es la propuesta del equipo, no una decisión ratificada por la patrocinadora.

**El criterio de censura es de la patrocinadora, no nuestro.** La sección 7 de su diccionario trae la tabla hecha sobre las 61,001 filas con `>` o `>=`, y la regla: *«solo sirve como negativo si el límite es igual o mayor que el umbral de "activo" que se use»*.

| Umbral de «activo» | Negativos seguros | Ambiguos |
|:--|--:|--:|
| 1 µM | 59,859 (98%) | 1,142 |
| 10 µM | 54,419 (89%) | 6,582 |
| 100 µM | 7,474 (12%) | 53,527 |

Eso **corrige la propuesta anterior del equipo**, que fijaba el corte en 10 µM por ser el valor modal. Con 1 µM —que corresponde a pChEMBL ≥ 6— se recuperan 5,440 negativos seguros más. Es un argumento a favor de ≥ 6 que no teníamos y que es suyo.

El diccionario advierte además que **33,574 de las 41,291 filas con límite de 10 µM vienen de DrugMatrix**, una sola fuente, lo que concentra la evidencia censurada.

**Denominadores verificados.** El 61.7% y el 44.4% son proporciones **por registro etiquetado** en todo el archivo de entrenamiento, no el balance del conjunto de modelado por diana. Incluyen ensayos fenotípicos sin diana de la lista:

| Unidad y población | Denominador | ≥ 5: activos / inactivos | ≥ 6: activos / inactivos |
|:---|---:|---:|---:|
| Registro etiquetado, todo el archivo (incluye fenotípicos) | 194,086 | 119,835 / 74,251 · 61.7% activos · 1.6:1 | 86,238 / 107,848 · 44.4% activos · 0.8:1 |
| Par único de esqueleto de conectividad × gen objetivo (`target_gene`) | 71,145 | 50,177 / 20,968 · 70.5% activos · 2.4:1 | 35,966 / 35,179 · 50.6% activos · 1.0:1 |

La segunda fila resume la población observada después de etiquetar y agrupar; **no es todavía el conjunto de entrenamiento definitivo**. De los 114,549 registros que tienen una categoría de diana, 109,264 reciben etiqueta por alguna de las tres vías. Entre estos últimos, 4,810 no tienen el identificador de gen (`target_gene`) y 327 no tienen un esqueleto calculable desde SMILES. Se excluyen esos 5,137 registros al construir los 104,127 registros agrupables en 71,145 pares.

La regla aplicada en este recuento es explícita: un par se cuenta activo si **al menos una** de sus observaciones etiquetadas es activa (máximo de etiquetas binarias). Con esta regla hay 1,810 pares con etiquetas discordantes para ≥ 5 y 2,426 para ≥ 6. Por ello, las proporciones por pares dependen de cómo se resuelvan esos conflictos y **son descriptivas, no una decisión ya validada para el entrenamiento**. El máximo de etiquetas binarias no selecciona por sí mismo la medición de mayor potencia; esa equivalencia no se presupone aquí. La patrocinadora debe aclarar la comparabilidad biológica de los ensayos y posibles prioridades de evidencia; el equipo deberá definir y justificar la regla operativa, evaluar su sensibilidad y acordarla antes de cerrar el conjunto de modelado.

**Una recomendación que cambió al ampliar la población analizada.** En los registros con pChEMBL, ≥ 5 daba 87.1% de activos y una razón de 6.7 a 1; ese resultado motivó proponer ≥ 6. Al incluir las tres vías, las cifras dependen de la unidad: por registro, ≥ 5 da 61.7% de activos y ≥ 6 da 44.4%; por par de esqueleto de conectividad × gen, bajo la regla provisional descrita arriba, ≥ 5 da 70.5% y ≥ 6 da 50.6%. La diferencia entre los resultados por registro no identifica por sí sola la causa del cambio. El sesgo de selección en los registros con pChEMBL es una explicación posible, pero estos conteos no demuestran su mecanismo. **Se conserva ≥ 5 como umbral primario de trabajo y ≥ 6 como análisis de robustez, pendiente de ratificación de la patrocinadora; el balance de clases por sí solo no determina el umbral biológico.**

---

## 8 · Dos métodos de atribución independientes {#d8}

**Estado:** vigente · requisito de la patrocinadora · **Decide:** equipo

**Contexto.** La explicabilidad a nivel de subestructura es un requisito no negociable: hay que poder señalar qué fragmento químico sustenta la predicción.

**Decisión.** Al menos **dos métodos de atribución independientes**, reportando como confirmadas solo las subestructuras en que coinciden. Un modelo interpretable simple se entrena en paralelo como control.

**Verificación obligatoria.** Toda afirmación estructural se contrasta primero contra TPSA (<67 Å²) y HBD (≤1), que son los que dominan empíricamente.

**Consecuencia sobre la representación.** El fingerprint plegado introduce colisiones, donde subestructuras distintas comparten bit, y eso corrompe la atribución. De ahí que se evalúe **Sort & Slice** como alternativa libre de colisiones, con el vocabulario aprendido solo del entrenamiento.

---

## 9 · El sitio publicado como memoria del proyecto {#d9}

**Estado:** vigente · 5 de octubre · **Decide:** equipo

**Decisión.** El sitio es donde el proyecto se explica a sí mismo. La prueba que tiene que pasar: que un asesor, la patrocinadora o quien califique lo abra y entienda qué se hace y por qué, **sin leer código ni preguntar a nadie**. Se actualiza en el mismo PR del cambio que describe.

**Consecuencias.** Los reportes, el glosario, el linaje de datos y este registro viven ahí. Una decisión revertida en código pero todavía documentada en el sitio es peor que no documentar.

**Trampa conocida.** El sitio **no descubre archivos solo**: un documento nuevo es invisible hasta registrarlo en `scripts/prepare_site.py` y en el navbar de `_quarto.yml`.

---

## 10 · ¿Reservar los 1,033 compuestos comunes? {#d10}

**Estado:** ABIERTA · **Decide:** patrocinadora · bloquea el diseño de evaluación del Avance 3
**Pregunta:** ¿Prefiere validar la cadena completa o conservar los datos de entrenamiento de la etapa 1?

**El problema.** Solo 1,033 esqueletos tienen medición en los dos conjuntos. Son el único lugar donde se puede medir si la cadena de dos etapas funciona de extremo a extremo.

**La disyuntiva.**

- **Si se reservan** para evaluar el sistema completo, hay que sacarlos **también del entrenamiento de la etapa 1**, o hay fuga: el modelo de permeabilidad habría visto justo los compuestos sobre los que se mide la cadena. Cuesta el **25.7% de los datos de la etapa 1**.
- **Si no se reservan**, cada etapa se evalúa por separado y la cadena completa no se mide nunca.

**Qué hace falta para decidir.** Una estimación de cuánto se degrada la etapa 1 al perder un cuarto de sus datos. Es medible antes del Avance 3.

---

## 11 · PAINS: filtrar y no filtrar como brazos del mismo experimento {#d11}

**Estado:** propuesta · **Decide:** patrocinadora
**Pregunta:** ¿Marcar o excluir? ¿Hay otros filtros de reactividad o toxicidad aceptables para productos naturales?

**Contexto.** 413 compuestos del conjunto de permeabilidad (5.3%) llevan alerta PAINS. La alerta está **2.1 veces enriquecida en productos naturales** —7.5% contra 3.6%— que son justo los compuestos a priorizar.

**Qué definición de «natural».** El diccionario distingue tres categorías, no dos: 3,366 productos naturales exactos, **1,005 análogos que difieren solo en estereoquímica**, y 3,440 sin equivalente conocido. Las cifras de arriba usan la coincidencia exacta; con coincidencia por esqueleto son 6.9% contra 3.2%. La razón de 2.1× se sostiene con las dos definiciones, pero hay que decir cuál se usó.

**Qué significa la alerta.** PAINS **no quiere decir inactivo**: quiere decir que la actividad medida puede no venir del mecanismo que se supone. Un compuesto PAINS hace cosas, pero muchas y por vías inespecíficas.

**Propuesta.**

1. **Primario: sin filtrar.** Filtrar sesga contra los productos naturales.
2. **Robustez: filtrado**, con la **misma partición** y los mismos hiperparámetros, quitando PAINS **solo del entrenamiento**.
3. **Evaluación estratificada** sobre la prueba fija: desempeño en PAINS contra no-PAINS.

**Regla dura.** Nunca filtrar el conjunto de prueba: cambiaría la pregunta que se responde.

**Disciplina.** Declarar el protocolo antes de correrlo y reportar los tres brazos pase lo que pase. Quedarse con el que da mejor número es sobreajustar a la prueba.

**Qué dice la literatura, con las referencias verificadas.** Los filtros originales son de `baell2010pains`, derivados de ~93,000 compuestos en ensayos AlphaScreen de una sola institución. `capuzzi2017phantom` documenta que tienen baja precisión como predictores de promiscuidad: muchos compuestos con alerta no son *frequent hitters* y muchos *frequent hitters* no llevan alerta. Y `baell2018seven` es el propio autor de los filtros revisando su uso y su mal uso siete años después. Los metadatos de las tres se verificaron contra Crossref el 7 de octubre.

**Evidencia propia, que es más directa.** En nuestro conjunto de actividad el compuesto mediano toca **1 diana** y el percentil 99 toca 4. La curcumina aparece contra **32**, la quercetina contra 31 y el resveratrol contra 28. Una promiscuidad medida sobre nuestros propios datos es más defendible que un prior sobre subestructuras derivado de otro formato de ensayo.

**Un matiz que cambia dónde aplica.** Las alertas PAINS se derivaron de ensayos de actividad tipo AlphaScreen. Una molécula que agrega **no falsea una medición de logBB**, que es distribución fisicoquímica. Así que el experimento tiene sentido fuerte en la etapa 2 y débil en la etapa 1, donde la diferencia observada —11.7 puntos dentro de los naturales— es probablemente química real y no artefacto.

---

## 12 · Escalamiento y selección de características {#d12}

**Estado:** ABIERTA · **Decide:** equipo · la rúbrica del Avance 2 las pide explícitamente

**El problema.** La rúbrica pide «escalamiento y transformaciones; selección y extracción de características». El notebook del Avance 2 las menciona sin ejecutarlas.

**Las opciones.**

- **Justificar que no hacen falta.** Los modelos de árboles previstos no requieren normalizar, y eso es defendible si se dice y se mide.
- **Ejecutarlas** y reportar el efecto.

**Lo que sí está medido** y apunta a que hace falta algo: 120 pares de descriptores con correlación mayor a 0.95, y MW con HeavyAtoms a ρ = 0.98, que son casi la misma variable.

**Urgencia.** El Avance 2 vence el 11 de octubre.

---

## 13 · Forma del modelo de la etapa 2 {#d13}

**Estado:** ABIERTA · **Decide:** patrocinadora · bloquea el diseño del Avance 3

**El problema.** Son 39 dianas con volúmenes que difieren en tres órdenes de magnitud:

| Categoría | Registros |
|:--|--:|
| Alzheimer | 52,676 |
| Parkinson | 32,372 |
| Neuroinflamación | 12,331 |
| Depresión | 10,888 |
| … | |
| Huntington | 153 |
| ELA | 53 |

**Las opciones.** Un modelo por diana, uno por categoría de enfermedad, o uno multitarea que comparta representación entre dianas. Con 53 registros, ELA no sostiene un modelo propio; con 52,676, Alzheimer sí.

**Decide:** patrocinadora · **Pregunta:** ¿Un modelo por diana, por categoría de enfermedad o multitarea? ¿Qué dianas son prioritarias y cuáles se descartan por falta de datos?

---

## 14 · Los 88,098 registros fenotípicos {#d14}

**Estado:** propuesta · **Decide:** patrocinadora

**El problema.** El 43.5% de los registros no corresponde a ninguna diana de la lista. Entraron todos por la ruta `neuronal_assay`: son ensayos sobre sistemas celulares neuronales donde se midió un efecto **sin identificar la proteína responsable**.

Es evidencia de otro tipo. Sirve para «¿este compuesto hace *algo* en un sistema neuronal?», no para «¿actúa sobre esta diana?», que es lo que plantea la etapa 2.

**Propuesta revisada del equipo.** Los 114,549 registros tienen una categoría de diana, pero solo 109,264 reciben etiqueta por las tres vías planteadas. Después se excluyen de la agregación por pares 4,810 registros sin identificador de gen y 327 sin estructura válida para calcular la clave de conectividad; quedan 104,127 registros agrupables en 71,145 pares antes de resolver discordancias y definir la partición. **Este conteo no es el tamaño final del entrenamiento.** Los 88,098 registros fenotípicos sin diana de la lista se conservan aparte para una pregunta distinta; no se descartan.

**Decide:** patrocinadora · **Pregunta:** ¿Los quiere dentro del modelo, aparte o fuera?

---

## 15 · La fuente confundida con el etiquetado {#d15}

**Estado:** vigente · medida el 7 de octubre · **Decide:** equipo

La decide el equipo, pero lleva una pregunta para la patrocinadora porque ella conoce las fuentes.

**La hipótesis.** NPASS y CMAUP son bases de productos naturales y no traen pChEMBL; ChEMBL es sobre todo sintético y sí lo trae. Si el etiquetado usa una vía distinta según la fuente, el modelo podría aprender **la fuente** en vez de la actividad.

**Lo que se midió.** El confundido es perfecto **a nivel de registro** —los 15,289 registros de NPASS y CMAUP tienen cero pChEMBL— pero **no a nivel de compuesto**:

| | Esqueletos |
|:--|--:|
| Solo en ChEMBL | 95,413 |
| **Solo en NPASS/CMAUP** | **1,445** |
| En ambas fuentes | 2,727 |

El **65.4% de los compuestos naturales también aparece en ChEMBL**, así que quedan etiquetados por las dos vías y el confundido se rompe solo para ellos.

**Dos consecuencias.**

1. **El riesgo está concentrado en 1,445 compuestos**, los que existen únicamente en NPASS o CMAUP. No en los 4,172.
2. **Los 2,727 solapados son un conjunto de calibración.** Donde hay pChEMBL *y* concentración exacta se puede ajustar el corte de concentración para que concuerde con el pChEMBL, y medir cuánto discrepan. Eso valida la regla alternativa en vez de suponerla.

**Pendiente.** Hacer esa calibración antes de fijar la decisión [7](#d7). Es lo que convertiría esa pregunta de abierta a «esto proponemos, ¿le parece?».

**Decide:** patrocinadora · **Pregunta:** ¿Conoce sesgos de curación entre ChEMBL, NPASS y CMAUP que debamos tener en cuenta?

---

## 16 · Qué error cuesta más y cómo presentar el ranking {#d16}

**Estado:** ABIERTA · **Decide:** patrocinadora

**El problema.** La elección de umbral de decisión depende de qué error es más caro, y eso no lo decide la estadística.

- Un **falso activo** manda al laboratorio a ensayar un compuesto que no funciona: cuesta tiempo y reactivos.
- Un **falso inactivo** descarta un candidato real, y nadie se entera nunca.

Las métricas ya están fijadas —MCC y AUPRC sobre la clase minoritaria, decisión [6](#d6)—, pero el punto de operación no.

**Decide:** patrocinadora · **Pregunta:** ¿Qué error le cuesta más? ¿Cómo debería presentarse un ranking de candidatos para que sea accionable en laboratorio: una lista ordenada, un umbral con corte, agrupado por diana?

---

## 17 · La lista de 39 dianas {#d17}

**Estado:** ABIERTA · **Decide:** patrocinadora

**Contexto.** El archivo `etiquetas_dianas_2026-09-25.csv` tiene 39 filas, pero su diccionario distingue **37 dianas identificadas por gen** más **2 receptores completos** —NMDA y GABA-A— que ChEMBL registra sin especificar subunidad. Decir «39 dianas» es impreciso.

El criterio de curación también está documentado y responde una pregunta que teníamos abierta: las etiquetas se curaron a mano desde la farmacología conocida, y la categoría principal es la enfermedad con más respaldo —fármaco aprobado primero, luego evidencia genética.

**Lo que sí hay que resolver son las dianas sin datos.** Según el diccionario:

| Gen | Diana | Filas |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | **0** |
| `AIF1` | Iba1 | **0** |
| `GABRB2` | Receptor GABA-A, subunidad β2 | 1 |
| `TARDBP` | TDP-43 | 8 |

`AIF1` el propio diccionario lo marca como «marcador», sin dirección de efecto, así que no es una diana de intervención.

**Decide:** patrocinadora · **Pregunta:** proponemos excluir del modelado `GABRG2`, `AIF1`, `GABRB2` y `TARDBP` por tener 0, 0, 1 y 8 filas. ¿Lo confirma? ¿Falta o sobra alguna otra diana?

---

## 18 · Las 6 filas con logBB sin clase BBB {#d18}

**Estado:** ABIERTA · **Decide:** patrocinadora

**El problema.** Seis filas del archivo de permeabilidad traen valor de `logbb` pero no clase BBB integrada. Según el diccionario, sí tienen clase en B3DB, pero su fila de clasificación corresponde a otra forma estereoquímica y no empató en la unión por estructura.

El equipo las excluye de los análisis de clasificación y **no les imputa una etiqueta desde la conectividad**, porque la estereoquímica puede afectar la clase.

**Decide:** patrocinadora · **Pregunta:** ¿Puede completarlas desde B3DB, o se quedan fuera?

---

## 19 · Licencia de NPASS: CC BY-NC {#d19}

**Estado:** ABIERTA · **Decide:** patrocinadora

**El problema.** NPASS se publica bajo **CC BY-NC**: no comercial. B3DB es CC0 y no tiene restricción. Si el proyecto tuviera aspiraciones comerciales, los datos de NPASS no podrían usarse y habría que rehacer la etapa 2 sin ellos.

Son 11,992 registros, el 5.9% del conjunto de actividad.

**Decide:** patrocinadora · **Pregunta:** ¿El proyecto tiene aspiraciones comerciales, o se queda en el ámbito académico?

---

## 20 · Partición de la etapa 2 {#d20}

**Estado:** propuesta · **Decide:** ambos

**Propuesta.** El mismo criterio que la etapa 1: partición por andamio de Bemis-Murcko sobre los 99,585 esqueletos, agrupando por esqueleto de conectividad y verificando que no haya fuga. Además, disjunta por fuente si los datos lo permiten.

**Por qué disjunta por fuente.** Es la mitigación natural del riesgo de la decisión [15](#d15): si entrenamiento y prueba no comparten fuente, un modelo que haya aprendido la fuente en vez de la actividad se delata.

**Decide:** ambos · **Pregunta:** ¿Hay agrupaciones por familia química o por laboratorio de origen que debamos respetar al partir, más allá del andamio?
