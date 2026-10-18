# Acta de la reunión con la patrocinadora

**Documento de trabajo, no se publica en el sitio.** Se llena **durante** la reunión y al terminar
**es la minuta**: de aquí se copian las respuestas a [la ruta del proyecto](decisiones.md), en los
términos de ella y con la fecha. Nada pasa a *ratificada* antes de eso.

| | |
|:--|:--|
| **Fecha** | **15 de octubre de 2026** (51 min) · «Checkpoint 1» |
| **Asistentes** | Dra. Mariana Martínez Ávila · Pamela Ruiz Puga · José Antonio Vázquez Martínez · Artemio Padilla Robles |
| **Levanta el acta** | Transcripción de la reunión, más el correo del 16 de octubre |
| **Material enviado antes** | [Presentación](https://antoniovazquezmartinez.github.io/Bioactive-AI/presentacion.html) · [Consulta](https://antoniovazquezmartinez.github.io/Bioactive-AI/consulta.html) · [La ruta](https://antoniovazquezmartinez.github.io/Bioactive-AI/contenido/decisiones.html) |
| **Respuestas asíncronas recibidas** | **sí** · correo del 16 de octubre de 2026, con copia a Jorge Alberto Uribe Echeverría |

> **Cómo leer esta minuta.** La sesión no siguió el orden de este documento: empezó a las 3:35 a.m.
> hora de la patrocinadora, que estaba fuera del país, y los primeros ocho minutos se fueron
> localizando la carpeta compartida, así que discutió el archivo sin tenerlo abierto. De las siete
> entradas marcadas «necesita su definición» se tocaron **dos** (P1 y, de pasada, E3), y en cambio se
> resolvió algo que no estaba en la agenda: el alcance de enfermedades. Lo que quedó sin tocar se
> marca como tal en lugar de darlo por respondido.

Si ya mandó respuestas por la página de consulta, **pégalas al final** antes de la reunión y usa esta
sesión para confirmarlas y resolver lo que haya quedado abierto, no para repetirlas.

---

## Cómo está ordenado

Las siete entradas marcadas «necesita su definición». **Cuatro son elecciones** —basta marcar una
opción— y **tres son peticiones**: necesitamos información o un archivo que solo ella tiene. Están
separadas porque se responden distinto y conviene no mezclarlas.

Cada una trae la recomendación del equipo. Si la confirma, se marca y listo; lo que hay que
registrar con cuidado es **cuando diga otra cosa**, porque eso es lo que el equipo no podía deducir.

---

## Parte 1 · Peticiones: lo que solo ella tiene

### P1 · ¿El archivo de actividad ya trae una prueba apartada? {#p1}

> Entrada [2.6](decisiones.md#d2-6) · bloquea el Avance 3

El archivo se llama `..._Entrenamiento.csv` y trae 202,647 de los 225,513 registros que describe su
diccionario: el 89.9%. Faltan 22,866.

- [x] **Sí, hay una partición reservada.** Cómo se separó: **al azar, sin criterio**, «en vez de tener 500 pues tomamos 250… no te hicimos ningún filtrado» (33:46, 34:15)
- [ ] **No, la diferencia es por otra razón:** ______________________________
- [ ] No lo recuerda / hay que revisarlo

**Si fue aleatoria**, hay compuestos casi idénticos a los dos lados y no sirve como evaluación
estructural; habría que decirlo en el reporte. **Si existe y es por andamio**, el equipo no
construye otra.

**Notas.** Fue aleatoria, y al explicarle por qué eso importa —que si hay cincuenta análogos de la
morfina y el 10% se llevó cinco, el modelo memoriza el andamiaje y la proyección sale inflada
(35:24)— lo aceptó sin reservas: «lo hicimos muy a la ligera… si hay una forma de hacerlo con
mejores criterios, adelante» (44:00).

**Lo que concedió, y es la concesión más grande de la sesión:** entrega el archivo completo y el
equipo hace la partición. «Partamos de la base de datos completa que se las podemos pasar… ustedes
que son los expertos tengan la base completa y hagan bien esas separaciones» (40:00).

**Con una condición, que repitió cuatro veces:** que se reserve una prueba que el modelo nunca vea.
Su razón es que no espera encontrar otra base de datos con la que validar después: «no creo que
encontremos otra base de datos completamente distinta de otra plataforma con la misma información»
(41:40).

**Y una limitación que hay que declarar en el reporte, no se la dijimos:** un 10% extraído al azar
del mismo archivo comparte andamios, ensayos y artículos con el 90%. Es una partición interna con
otro nombre: prueba filas nuevas, no química nueva ni protocolos nuevos. Llamarla «validación
externa» sería sobrevender lo que compra.

**Compromiso suyo:** Jorge comparte el método con el que separó ese 10% y verifica con el equipo si
introduce sesgo (correo del 16 de octubre).

---

### P2 · ¿Puede aportar el cruce con COCONUT del archivo de actividad? {#p2}

> Entrada [2.8](decisiones.md#d2-8)

El archivo de permeabilidad llegó con tres columnas de COCONUT y es lo que sostiene el hallazgo
central del Avance 1. El de actividad no trae ninguna: sus únicas columnas de procedencia son
`source` e `inchikey_source`.

- [ ] **Sí**, lo puede generar · para cuándo: ____________
- [ ] **No**, el equipo lo hace por su cuenta *(y entonces no será comparable entre fases)*
- [ ] Hay otra forma de identificar los naturales ahí: ______________________________

El equipo podría cruzarlo desde `smiles_raw`, pero sería otra versión del catálogo y otra regla de
estandarización, así que las dos fases dejarían de ser comparables. Mientras tanto se usa la
**fuente** (NPASS y CMAUP) como definición provisional, declarada como tal.

**Notas:**

---

### P3 · La brecha de los naturales aparece solo donde la etiqueta no es medida {#p3}

> Entrada [1.6](decisiones.md#d1-6)

| Grupo de B3DB | No natural | Natural | Diferencia (IC 95%) |
|:--|--:|--:|:--|
| **A** (con logBB medido) | 87.6% | 88.4% | **−0.8** [−4.8, +3.2] |
| B | 77.2% | 55.9% | **+21.4** [+18.3, +24.5] |
| C | 58.1% | 40.9% | **+17.2** [+13.7, +20.7] |

- [ ] **Hay una razón de curación que lo explica:** ______________________________
- [ ] **Es química real**

*La [1.6](decisiones.md#d1-6) propone de todos modos **un solo modelo**, con el desempeño reportado por origen dentro de cada grupo; entrenar aparte solo si esa evaluación muestra que falla en naturales.*
- [ ] No lo sabe; queda como limitación declarada en el reporte

**Notas:**

---

## Parte 2 · Elecciones

### E1 · ¿Dónde se corta «activo»? {#e1}

> Entrada [2.3](decisiones.md#d2-3) · bloquea el Avance 3

**Es una sola decisión, no dos:** la regla de censura de su diccionario ata el corte de los
inactivos al de los activos, así que mover uno mueve el otro.

| | **10 µM** (pChEMBL ≥ 5) | **1 µM** (pChEMBL ≥ 6) |
|:--|--:|--:|
| Censurados que sirven de negativo | 48,480 | 53,359 |
| Quedan ambiguos | 6,018 | 1,139 |
| Activos por registro | 61.7% | 44.4% |
| Razón de clases | 1.6:1 | 0.8:1 |
| **De una sola referencia de ChEMBL** | **61.3%** | 55.7% |

- [ ] **10 µM** — [ ] **1 µM** — [ ] otro: ____________

**El argumento más fuerte contra 10 µM no es el balance de clases:** con ese corte, 29,730 de los
48,480 negativos —tres de cada cinco— salen de un solo experimento (`CHEMBL1909046`, todos con el
texto «Not active»). Ninguna partición arregla eso.

**Preguntas que cuelgan de esta, si hay tiempo:** ¿son confiables los inactivos declarados por
texto? Si un mismo esqueleto y gen tienen observaciones activas e inactivas, ¿qué evidencia manda?
¿«Activo» incluye cualquier dirección del efecto, inhibir o activar?

**Notas · sin respuesta, y por una razón que vale documentar.** La pregunta no llegó como está
escrita aquí. En sus primeros tres minutos contestó otra: habló del umbral como algo *a descubrir*
—«a partir de qué valor ya se vuelve algo significativo» (1:01)— y lo ilustró con un marcador en un
paciente, «una persona sana puede tener un valor de 5 y una persona enferma punto uno» (2:04). Eso
es un umbral **diagnóstico**, que se calibra contra un desenlace; el nuestro es un **corte de
etiqueta** sobre un IC50. Nunca se cruzaron.

**Y su versión de la pregunta no es contestable con este archivo:** no hay columna de desenlace,
nada registra si un compuesto *funcionó*. Sin desenlace un umbral no se estima, se elige. De ahí
sale la petición nueva de la P4.

Lo que sí dejó claro es que no puede nombrar el valor: «no te puedo yo decir un umbral… eso es lo
que no te puedo decir ahorita» (2:04). El corte queda entonces como **decisión declarada del
equipo** en la [2.3](decisiones.md#d2-3), con su justificación de alcanzabilidad, no como respuesta
suya.

---

### E2 · ¿Se excluyen las cuatro dianas sin datos? {#e2}

> Entrada [2.1](decisiones.md#d2-1) · bloquea el Avance 3 · se resuelve antes de la E3

| Gen | Diana | Registros |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | **0** |
| `AIF1` | Iba1 | **0** |
| `GABRB2` | Receptor GABA-A, subunidad β2 | **1** |
| `TARDBP` | TDP-43 | **8** |

- [ ] **Sí, se excluyen las cuatro** *(propuesta del equipo)*
- [ ] Se excluyen solo: ______________________________
- [ ] Falta alguna diana en la lista: ______________________________
- [ ] Sobra alguna otra: ______________________________

**Notas:**

---

### E3 · ¿Un modelo por diana, por categoría o multitarea? {#e3}

> Entrada [2.2](decisiones.md#d2-2) · bloquea el Avance 3 · después de la E2

Alzheimer 52,676 registros · Parkinson 32,372 · Neuroinflamación 12,331 · Depresión 10,888 ·
Estrés oxidativo 2,456 · Epilepsia 1,862 · Neurodegeneración 1,110 · Deterioro cognitivo 488 ·
Ansiedad 160 · Huntington 153 · **ELA 53**.

- [ ] **Uno por diana**, solo donde haya volumen
- [ ] **Uno por categoría** de enfermedad
- [ ] **Multitarea**, que es la única forma de incluir las pequeñas
- [ ] otra: ______________________________

**Y antes que la forma: ¿qué dianas son prioritarias para su pregunta de investigación?** Eso no
sale de los datos.

**Las cinco categorías: Alzheimer, Parkinson, neuroinflamación, depresión y estrés oxidativo.**

**Notas · la forma del modelo no se tocó; el alcance sí, y quedó cerrado.** «Sí se pueden resumir a
esas… y si los demás adelante los pueden remover» (22:37, 29:55).

**Pidió el criterio, dos veces, y es lo que hay que escribir.** «Aquí la pregunta es, ¿cuál es el
criterio para eliminar el resto, solo porque tienen pocas entradas?» (22:37) y «¿cuánto sería, cómo
debería ser esa distribución para que no haga ruido?» (23:56), con una cota propia: «hablar tal vez
de un menos de 10% no es algo confiable». El equipo ofreció **≥ 50 registros** como regla
conservadora (25:01). Eso va a la [2.1](decisiones.md#d2-1) como regla, no como lista.

**Estrés oxidativo entra por decisión suya y con su razonamiento explícito**, que conviene conservar
porque es el criterio biológico que el equipo no podía deducir: va de lo general a lo específico,
«es solo un dolor de cabeza o te está tratando Alzheimer» (27:41), y el estrés oxidativo es el
extremo general —«toda enfermedad, desde la gripa, desde hacer ejercicio, el acné»—. Lo dejó
revisable: «si empiezan a notar que es algo raro en el análisis, lo podríamos pensar en quitarlo».

**Una interacción que no vio, y hay que mostrarle:** estrés oxidativo es **47.7% NPASS y CMAUP**. Si
además se descarta el etiquetado de esas dos fuentes (su correo del 16), la categoría que defendió
pasa de 2,456 filas a 1,285. Sus dos decisiones se restan entre sí.

---

### E4 · ¿Qué espera recibir, y qué error le cuesta más? {#e4}

> Entrada [C.5](decisiones.md#dc-5)

**Qué espera recibir:**

- [ ] Una lista de candidatos priorizados
- [ ] Un modelo que pueda correr ella misma
- [ ] El material de un artículo
- [ ] otra: ______________________________

**Qué error pesa más.** Si el laboratorio puede ensayar unos veinte compuestos este semestre:

- [ ] **Lista corta y precisa:** veinte, acertando cuatro de cada cinco
- [ ] **Lista amplia:** cien, acertando una de cada dos
- [ ] Depende de: ______________________________

**Cómo presentar el ranking:** [ ] lista ordenada · [ ] con un corte · [ ] agrupado por diana

**Y un caso que hay que saber presentar:** un compuesto con BBB− predicho y actividad documentada.
______________________________

**Notas:**

---

## Parte 3 · Lo que no estaba en la agenda

### A1 · Descarta inferir activo/inactivo entre bases {#a1}

> Entrada [2.3](decisiones.md#d2-3) · respondido por correo el 16 de octubre

**Qué se le preguntó.** Si para NPASS y CMAUP, que no traen pChEMBL, se podía construir la etiqueta
desde la concentración que sí traen: «¿está bien si en las otras bases construimos el KPI, el valor,
y desde ahí podemos ya partir en activo, inactivo?» (12:20) y «para los que no traen este dato, que
son las otras 2 bases, si usted considera que es homogéneo construir el valor» (16:40).

**Qué contestó.** En la sesión no se decidió —«me quedo con la primera… denme chance de revisarlo»
(46:40)— y al día siguiente por correo: **«Descartado hacer la inferencia, al menos no de forma
directa.»** Sus razones: la tabla trae una columna de tejido, hay alrededor de ocho líneas celulares
neuronales, y «aunque una diana esté validada y tenga medición, el threshold no necesariamente
significa lo mismo en todos los casos». Añade que una misma molécula aparece activa e inactiva según
tejido y tipo de experimento, y **sugiere revisar cómo se distribuyen los registros por tejido y
tipo de experimento antes de decidir cómo abordarlo**.

**Lo que el equipo midió al hacer lo que pidió,** y que cambia qué se le puede contestar:

| | |
|:--|--:|
| Pares compuesto-diana con mediciones activas e inactivas a la vez | 1,784 · 12.1% de los que tienen más de una |
| De los conflictos de ChEMBL, con tejido anotado en alguna fila | 6 de 1,373 |
| Filas de la ruta `cns_target` con formato de ensayo anotado | **0 de 108,640** |

El contexto del ensayo **no está escaso, está ausente** en la población que se modela: las columnas
de tejido, línea celular y tipo de ensayo existen solo para las filas que entraron por la ruta
`neuronal_assay` (96% anotadas). No es dato faltante, son dos rutas anotadas distinto al construir
el archivo. **Así que la estratificación que sugiere no se puede hacer**, y el vacío tampoco
demuestra que el tejido no influya: el experimento ocurrió en algún tejido y lo que falta es la
columna.

**Lo que sí se puede medir, y es su preocupación en una forma verificable:** el corte de 10 µM cae
casi en la mediana de las mediciones de NPASS (6.56 µM) y a treinta veces de la de ChEMBL (0.335
µM). Para los naturales la etiqueta la decide el ruido de medición; para ChEMBL es estable. Tenía el
instinto correcto con un mecanismo que no es el que nombró.

**Y su remedio no alcanza su diagnóstico:** quedarse solo con ChEMBL no compra comparabilidad. Dentro
de ChEMBL hay 8,984 ensayos distintos, y el desacuerdo entre mediciones del mismo par es
ligeramente **peor** ahí solo (28.7% discrepan más de 10×) que juntando las tres fuentes (26.0%).

**Decisión del equipo, declarada como tal y no como respuesta suya** ([2.3](decisiones.md#d2-3)):
etiquetar las tres fuentes con las columnas de la sección 5 del diccionario, que vienen informadas
y homogéneas para las tres, con 10 µM principal y 1 µM de sensibilidad. «Solo ChEMBL» se conserva
como análisis de sensibilidad y es la salida si el control de atajo muestra que la fuente filtra la
etiqueta. **Queda por preguntarle** la versión estrecha de la pregunta, con filas reales de cada
fuente a la vista: ¿descartó usar esas columnas con el mismo corte, o solo inferir lo que no viene
informado, como las 2,001 relaciones de NPASS?

### P4 · La petición que falta: un desenlace {#p4}

> Entrada [2.3](decisiones.md#d2-3)

Ella quiere saber a partir de qué valor un compuesto se vuelve significativo. Esa pregunta **no es
contestable con este archivo**, porque no hay ninguna columna que diga si un compuesto funcionó.
Todo lo que hay son mediciones de potencia.

No hace falta un ensayo clínico. Basta el peldaño de **eficacia celular**: qué compuestos rescataron
neuronas en sus ensayos y a qué concentración. Con eso el umbral deja de elegirse y empieza a
estimarse, y su pregunta se vuelve un problema de calibración con respuesta.

- [ ] **Puede aportarlo** · qué contiene y para cuándo: ______________________________
- [ ] **No existe** · el umbral queda como convención declarada del equipo
- [ ] Hay otra forma de obtener un desenlace: ______________________________

---

## Cierre

### Lo que no se alcanzó a ver

**E1** (dónde se corta «activo»), **E2** (las cuatro dianas sin datos), **E4** (qué espera recibir y
qué error pesa más), **P2** (el cruce con COCONUT) y **P3** (la brecha de los naturales en la fase
1). De las siete entradas de la agenda se tocó una, la P1.

### Compromisos

| Qué | Quién | Para cuándo |
|:--|:--|:--|
| Compartir el método con que se separó el 10% y verificar si sesga | Jorge Uribe | correo del 16 de octubre, pendiente |
| Entregar el archivo completo, sin el 10% apartado | Patrocinadora / Jorge | acordado el 15 de octubre, pendiente |
| Anotar la ruta `cns_target` con tipo de ensayo, formato, tejido y línea celular | Jorge Uribe | por pedir |
| Mostrarle filas reales de cada fuente con las columnas de la sección 5 | Equipo | antes de la siguiente sesión |
| Mostrarle que estrés oxidativo es 47.7% NPASS/CMAUP | Equipo | antes de la siguiente sesión |

### Siguiente paso del equipo

Pasar cada respuesta a su entrada de [la ruta](decisiones.md), marcarla **ratificada** con esta
fecha, y quitarle la marca «necesita su definición». Las entradas que queden sin respuesta se
mantienen como *propuesta* y así se declaran en el reporte del Avance donde se usen.

---

## Anexo · Respuestas asíncronas, si las hubo

Pegar aquí el bloque que genera la [página de consulta](https://antoniovazquezmartinez.github.io/Bioactive-AI/consulta.html).

```
```
