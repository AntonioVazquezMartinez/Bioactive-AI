# Acta de la reunión con la patrocinadora

**Documento de trabajo, no se publica en el sitio.** Se llena **durante** la reunión y al terminar
**es la minuta**: de aquí se copian las respuestas a [la ruta del proyecto](decisiones.md), en los
términos de ella y con la fecha. Nada pasa a *ratificada* antes de eso.

| | |
|:--|:--|
| **Fecha** | ______________________ |
| **Asistentes** | Dra. Mariana Martínez Ávila · ______________________ |
| **Levanta el acta** | ______________________ |
| **Material enviado antes** | [Presentación](https://antoniovazquezmartinez.github.io/Bioactive-AI/presentacion.html) · [Consulta](https://antoniovazquezmartinez.github.io/Bioactive-AI/consulta.html) · [La ruta](https://antoniovazquezmartinez.github.io/Bioactive-AI/contenido/decisiones.html) |
| **Respuestas asíncronas recibidas** | sí / no · fecha ____________ |

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

- [ ] **Sí, hay una partición reservada.** Cómo se separó: ______________________________
- [ ] **No, la diferencia es por otra razón:** ______________________________
- [ ] No lo recuerda / hay que revisarlo

**Si fue aleatoria**, hay compuestos casi idénticos a los dos lados y no sirve como evaluación
estructural; habría que decirlo en el reporte. **Si existe y es por andamio**, el equipo no
construye otra.

**Notas:**

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
- [ ] **Es química real**, y entonces conviene considerar entrenar aparte
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

**Notas:**

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

______________________________

**Notas:**

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

## Cierre

### Lo que no se alcanzó a ver

______________________________

### Compromisos

| Qué | Quién | Para cuándo |
|:--|:--|:--|
| | | |

### Siguiente paso del equipo

Pasar cada respuesta a su entrada de [la ruta](decisiones.md), marcarla **ratificada** con esta
fecha, y quitarle la marca «necesita su definición». Las entradas que queden sin respuesta se
mantienen como *propuesta* y así se declaran en el reporte del Avance donde se usen.

---

## Anexo · Respuestas asíncronas, si las hubo

Pegar aquí el bloque que genera la [página de consulta](https://antoniovazquezmartinez.github.io/Bioactive-AI/consulta.html).

```
```
