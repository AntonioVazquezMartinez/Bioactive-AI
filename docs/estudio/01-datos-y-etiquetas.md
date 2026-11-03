# Capa 1 · Los datos, las etiquetas y la partición

Cuadernos `01_EDA`, `02_Feature_Eng`, `01b_EDA_actividad_snc` y `02b_Feature_Eng_actividad`.

**Por qué esta capa va primero:** casi todo lo que se decide después descansa en qué es una
fila, qué significa «activo» y cómo se partieron los datos. Una pregunta mal contestada aquí
tira lo que viene encima, y un profesor empieza por aquí.

Cada tema sigue el mismo orden: **qué se hizo → por qué → la cifra y dónde está → la pregunta
que haría un profesor → qué no sabemos**. Las cifras salen de los cuadernos entregados y
llevan su sección; las que dicen «medido aquí» se ejecutaron al preparar esta guía.

La teoría que sostiene esto está en [`fundamentos-desde-cero.md`](../fundamentos-desde-cero.md)
y los términos en [`glosario.md`](../glosario.md); no se repiten.

---

## Vocabulario mínimo

| término | qué es, en una línea |
|:--|:--|
| **BBB+ / BBB−** | el compuesto cruza / no cruza la barrera hematoencefálica |
| **logBB** | cociente de concentración cerebro/sangre en escala log; la clase sale de cortarlo en −1 |
| **TPSA, HBD** | superficie polar y donadores de hidrógeno: las dos propiedades que dominan la permeabilidad |
| **andamio (Bemis-Murcko)** | el esqueleto de anillos y conectores de una molécula, sin sustituyentes |
| **`key14`** | los 14 primeros caracteres del InChIKey: la conectividad **sin** estereoquímica |
| **estereoisómeros** | moléculas con los mismos enlaces y distinta disposición en el espacio |
| **ECFP4 / Morgan** | huella: bits que marcan qué entornos atómicos contiene la molécula |
| **Sort & Slice** | huella sin colisiones: cada columna es **una** subestructura |
| **pChEMBL** | −log10 de la potencia en molar; solo existe para registros de ChEMBL |
| **censurada** | una medición `> X` dice «no se vio efecto hasta X», no cuánto vale |
| **MCC, AUPRC** | las métricas del proyecto, elegidas por el desbalance de clases |

---

# Fase 1 · permeabilidad (Avances 1 y 2)

## 1.1 · De dónde salen los datos

**Qué se hizo.** La fuente es el archivo curado que entregó la patrocinadora, no los archivos
de B3DB que el equipo descargó; esos quedan como verificación.

**Por qué.** Trae tres cosas que el original no: SMILES estandarizados, `key14` precalculado
y, sobre todo, el cruce con **COCONUT**, que es lo que permite separar productos naturales de
sintéticos. Sin ese cruce no se puede preguntar si los compuestos que el proyecto quiere
priorizar se comportan distinto frente a la barrera.

**Cifras** (`01` §2): 7,811 filas, **7,805 con clase**, 1,058 con logBB, 3,366 con equivalente
exacto en COCONUT. Las seis sin clase tienen logBB pero su clase de B3DB no se integró por
una diferencia de estereoquímica en la unión.

> **P. ¿Por qué no usaron B3DB directo, que es público y con licencia abierta?**
> Porque el archivo curado ya resuelve la unión clasificación-regresión, estandariza las
> estructuras y trae el cruce con COCONUT, que no se puede reconstruir sin el catálogo. B3DB
> se conserva para contrastar.

> **P. ¿El archivo incluye todo lo que B3DB publica?**
> **No.** El suplemento de agosto de 2025 trae 175 compuestos y solo 11 están en el archivo
> curado; 164 faltan (`01` §2.1). Es una limitación conocida y se declara en lugar de
> fusionar archivos a ciegas, porque concatenar duplicaría 11.

## 1.2 · Cuántos datos hay de verdad

**La cifra clave: el tamaño efectivo es 4,018, no 7,805** (`01` §2.4).

**Por qué.** Cada fila es un registro, no un compuesto: la morfina aparece ocho veces como
estereoisómero o duplicado de nombre distinto. Agrupando por esqueleto de conectividad quedan
**4,018 esqueletos**. Solo 3 filas repiten el InChIKey completo, pero 3,787 repiten un
esqueleto ya visto.

> **P. ¿Entonces con cuántos ejemplos entrenan?**
> Con 7,805 filas que son 4,018 unidades independientes. Hay que decir las dos cifras, y por
> eso todo el proyecto agrupa por esqueleto al partir y al remuestrear.

**Un hallazgo menor que conviene tener a mano:** 131 esqueletos (429 compuestos, 5.5%) traen
etiquetas **contradictorias entre sus estereoisómeros**. Entre duplicados exactos no hay
ninguna contradicción. Son candidatos a acantilados de actividad reales o a errores de
etiquetado, y están pendientes de revisar (decisión 1.8).

## 1.3 · La columna `group` A–D: por qué NO se filtra

**Qué se hizo.** Se usa para describir y estratificar, **nunca para excluir ni como
predictor** ([1.1](../decisiones.md#d1-1)).

**Por qué.** B3DB sugiere que A–D ordenan la calidad de la etiqueta, pero no publica el
criterio. Medido (`01` §3.1):

| grupo | filas | % BBB− | mediana de referencias |
|:--|--:|--:|--:|
| A | 1,058 | 12.1 | 5 |
| B | 3,621 | 31.3 | 3 |
| C | 3,075 | 50.0 | 1 |
| D | 51 | 92.2 | 3 |

El grupo D tiene **más** respaldo bibliográfico que el C, lo contrario de una escala de
calidad. Y filtrar a A+B **baja la clase minoritaria de 36.5% a 27.0%**: empeora el
desbalance en vez de limpiar ruido. Además, la ausencia de datos se asocia a la clase casi
siempre a través del grupo (solo A trae logBB, solo B trae `threshold`), de modo que **que un
campo exista o no filtra la etiqueta** y ningún indicador de «presente» entra al modelo.

> **P. ¿No sería más limpio entrenar solo con el grupo A, que tiene logBB medido?**
> Es lo que parece, y los datos lo desaconsejan: el grupo A es 88% BBB+ y solo tiene 1,058
> filas. Entrenar ahí deja sin ejemplos negativos y sin los productos naturales que el
> proyecto quiere priorizar.

## 1.4 · Los tres orígenes: natural, análogo, sin equivalente

**Qué se hizo.** El cruce con COCONUT da **tres** grupos, no dos (`01` §5):

| origen | cómo se define | n | % BBB+ |
|:--|:--|--:|--:|
| natural exacto | estructura completa, con estereoquímica, en COCONUT | 3,366 | 52.7 |
| análogo estereoquímico | solo el esqueleto está en COCONUT | 1,003 | 39.7 |
| sin equivalente natural | ni la estructura ni el esqueleto | 3,436 | 81.0 |

**La brecha es de 28.3 puntos** entre naturales y compuestos sin equivalente. Una versión
anterior los comparaba contra un único grupo «sintético» que juntaba los análogos con los
sin equivalente y daba 18.9; **ese grupo no es sintético** (más de una quinta parte son
estereoisómeros de un natural). Los intervalos no se solapan entre ninguno de los tres.

> **P. ¿Esa brecha es química o es cómo se etiquetó?**
> **No lo sabemos, y el 01 lo dice.** La regla TPSA/HBD no la explica: entre los que
> *cumplen* la regla, químicamente casi iguales, los naturales cruzan 80.9% contra 90.9%. Y en
> el grupo A, donde la clase sale de un logBB que sí está en el archivo, los tres orígenes
> cruzan igual (88.4%, 86.6%, 87.7%). Caben dos lecturas que los datos no separan: parte de la
> brecha viene de cómo se etiquetó B y C, o es un **efecto techo** (A es 88% BBB+, queda poco
> margen para diferir).

> **P. ¿Por qué evalúan por origen en vez de entrenar un modelo para naturales?**
> Porque solo 3,366 filas son naturales, y separar el entrenamiento dejaría un modelo débil.
> Se evalúa por origen dentro del mismo modelo ([1.6](../decisiones.md#d1-6)).

**Una salvedad que ya es un issue ([#203](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/203)):**
`natural exacto` exige la llave completa, así que un natural cuyo registro no declara la
estereoquímica no puede coincidir y cae en `análogo`. La contaminación va en **un solo
sentido**: `natural exacto` es más puro pero más pequeño de lo que debería, y el 52.7% está
medido sobre un subconjunto con registro estereoquímico completo.

## 1.5 · Los descriptores y el umbral de TPSA

**Qué se hizo.** Se calculan los 217 descriptores 2D de RDKit; quedan **203 utilizables**.
`Ipc` alcanza ~1e41, finito en float64 pero fuera de float32, y Random Forest convierte
internamente: **un chequeo de `isfinite` no lo detecta**, costó una ejecución fallida.

**El hallazgo que hay que saber contar: el umbral de TPSA no es una constante.**

| medición | TPSA óptimo (Å²) |
|:--|--:|
| publicado, sobre 1,058 compuestos | 66.8 |
| Avance 1, grupo A | 66.6 |
| Avance 1, A+B | 83.6 |
| Avance 1, conjunto completo | 101.9 |
| Avance 2, **solo entrenamiento** | **107.0** |

Cuatro subconjuntos del mismo archivo, cuatro umbrales que difieren en 40 Å². Los intervalos
bootstrap (remuestreando **esqueletos**, no filas) miden 26 a 28 Å² de ancho: dentro de cada
subconjunto el óptimo está poco determinado.

> **P. Entonces, ¿por qué verifican las explicaciones del modelo contra TPSA < 67?**
> **Es una tensión real y conviene reconocerla.** El criterio de explicabilidad (C.2) y la
> variable `regla_2p` usan 67 Å² de la literatura, mientras el propio proyecto derivó 107 Å²
> sobre su entrenamiento y mostró que se mueve. El 02 lo deja anotado como pendiente («derivarlo
> del entrenamiento o retirar la variable», punto 3c) y no está resuelto.

## 1.6 · La partición por andamio

**Qué se hizo.** Se parte por andamio de Bemis-Murcko **y** por esqueleto de conectividad, y
la prueba (20%) queda reservada. Nunca aleatoria ([1.2](../decisiones.md#d1-2)).

**Por qué.** Los andamios grandes tienen pureza de clase extrema: uno de 410 compuestos es
99.5% BBB+. Con partición aleatoria basta reconocer el andamio. Medido en la fase 1: agrupar
solo por andamio da 2,239 grupos contra 1,048 y **infla 2.2 puntos de AUROC y 7.1 de MCC**,
algo más de tres veces lo que separa a las familias de modelos en MCC, medido igual —una
semilla, media de pliegues— ([1.2](../decisiones.md#d1-2)). En AUROC no: ahí las dos
distancias son casi la misma.

| partición | filas | andamios | % BBB+ |
|:--|--:|--:|--:|
| entrenamiento | 5,557 | 1,741 | 64.0 |
| validación | 749 | 498 | 72.0 |
| prueba | 1,499 | 1,390 | 57.3 |

**Cero andamios y cero esqueletos en más de una partición** (`02` §3.2).

> **P. ¿Por qué los andamios frecuentes van a entrenamiento y los raros a prueba?**
> Es el detalle crítico. Construida al revés, la prueba salía con **45** andamios y el
> benceno ocupaba el 26%: el número de desempeño habría reflejado tres quimiotipos. Con la
> convención de DeepChem la prueba tiene casi un andamio por molécula, que es lo que mide
> generalización a química nueva.

> **P. La prueba tiene 57.3% de BBB+ y el entrenamiento 64.0%. ¿No es un defecto?**
> No se corrige a propósito: ajustar la partición para balancear debilitaría justo lo que la
> hace exigente, y los andamios raros resultan menos permeables. Se reporta la tasa base de
> cada partición al lado de cualquier métrica.

## 1.7 · Las huellas: Morgan, Sort & Slice y por qué 2,048

**Qué se hizo.** Morgan/ECFP4 de 2,048 bits (`radius=2`: el número del nombre es el
diámetro) y **Sort & Slice**, con el vocabulario aprendido solo del entrenamiento.

**Por qué Sort & Slice.** El plegado por hash hace que subestructuras distintas compartan
bit, lo que corrompe la atribución: el modelo tiene que asignar un solo valor a fragmentos de
efecto opuesto. En Sort & Slice **cada columna es una subestructura**, y eso es lo que permite
decir «este fragmento carga la señal» (`02` §5.2). Se prefirió sobre CF-MF, la alternativa más
reciente, porque esta se validó solo con particiones aleatorias.

**Por qué 2,048.** Es un compromiso, no un óptimo. El MCC sube despacio con el tamaño y el
mejor medido es 4,096 en los tres modelos, pero las diferencias (0.001 a 0.014) son menores
que la desviación entre pliegues (~0.09 a 0.11). La cobertura del vocabulario es **84.8% en
entrenamiento y 68.0% en prueba**, y esa brecha de 16.8 puntos **crece** con el vocabulario:
cerca de un tercio de las subestructuras de la prueba no existe en el entrenamiento, que es
extrapolación estructural y no ruido.

## 1.8 · Lo que se midió y NO ayudó

Esto vale oro ante un profesor porque muestra que se midió en vez de afirmar.

| qué se probó | resultado | dónde |
|:--|:--|:--|
| tres características derivadas del dominio (`regla_2p`, `tpsa_por_mw`, `lipo_neta`) | **ninguna mejora el modelo**: ΔMCC +0.0001 ± 0.0031 (logística), −0.0062 ± 0.0086 (RF) | `02` §6 |
| escalar, entre las tres formas | la medición **no distingue** (0.699, 0.695, 0.695 con el `C` propio de cada una) | `02` §8.2 |
| reducir dimensión con 50 columnas por información mutua | contra el filtrado de 151, el MCC **baja** en los dos (0.497 → 0.484 en la logística, 0.562 → 0.534 en el bosque) | `02` §9 |
| PCA como brazo de modelado | **se descarta por explicabilidad**, no por número | `02` §9 |

**Por qué se escala igualmente:** sin escalar, la regresión logística **no converge** con el
`C` que se usa (agota 3,000 iteraciones en los 15 pliegues); con cualquier escalado converge
en 53 a 144. Para los árboles escalar es irrelevante (diferencias de 0.000 a 0.001, con intervalos de ±0.002 a ±0.005).

> **P. ¿Por qué descartan el PCA si reduce dimensión?**
> Porque un componente es una combinación lineal de 151 columnas y **no se traduce a una
> subestructura**, y la explicabilidad es un requisito de la patrocinadora, no una preferencia.
> La diferencia de MCC frente al filtrado no es concluyente (el intervalo cruza el cero), así
> que la decisión se sostiene por el requisito y no por el número.

**La selección final:** 206 columnas → 182 tras quitar casi constantes (un valor reúne ≥99%) →
**151** tras quitar redundantes por Spearman |ρ| > 0.95. Sale la **misma** con las tres
transformaciones (medido, `True` tres veces), porque se hace sobre valores crudos.

---

# Fase 2 · actividad contra dianas (01b y 02b)

## 2.1 · Qué es una fila, y qué es la etiqueta

Aquí **ninguna de las dos cosas está dada**, y es la diferencia con la fase 1 que organiza
todo el cuaderno 02b:

1. El archivo trae **mediciones**, no compuestos: 202,647 filas (ChEMBL 187,354, NPASS 11,992,
   CMAUP 3,301), varias por la misma combinación compuesto-diana. La unidad del modelo, el
   **par compuesto-diana**, hay que construirla. Se llavea por esqueleto de conectividad ×
   gen, no por identificador de compuesto, porque los identificadores no se comparten entre
   fuentes y 164 conflictos quedarían invisibles.
2. **No existe una columna «activo».** Hay concentraciones, y convertirlas en etiqueta exige
   un umbral que los datos no pueden estimar.

El tamaño efectivo otra vez: 202,647 filas son **99,585 esqueletos**.

## 2.2 · Por qué no se etiqueta solo con pChEMBL

**Es la decisión metodológica más delicada de la fase 2** (`01b` §6, decisión [2.3](../decisiones.md#d2-3)).

| qué se pierde si se etiqueta solo con pChEMBL | registros |
|:--|--:|
| todo NPASS y CMAUP, las bases de **productos naturales** (ninguno trae pChEMBL) | 15,293 |
| todas las mediciones **censuradas** | 54,498 |
| todos los **inactivos declarados por texto** | 29,730 |

Las tres pérdidas apuntan al mismo lado: queda la evidencia de ChEMBL con curva
dosis-respuesta, sesgada hacia sintéticos bien caracterizados, y se excluye en silencio justo
lo que el proyecto existe para priorizar. Por eso se etiqueta por tres vías: pChEMBL donde
exista, concentración exacta para el resto, e inactivo declarado.

> **P. ¿Qué significa que una medición esté «censurada» y por qué no la tiran?**
> Un `IC50 > 10 µM` no dice cuánto vale la potencia: dice que el ensayo llegó a 10 µM sin ver
> efecto. Es evidencia real de inactividad. Tirarla —que es lo que hace cualquier regresión
> sobre mediciones exactas— quita el **49.4% de los negativos**, y no al azar, porque el 98% de
> los activos sí tiene medición exacta.

## 2.3 · El objetivo se guarda como intervalo, no como etiqueta

**Qué se hizo** (`02b` §2, decisión [2.10](../decisiones.md#d2-10)): el objetivo son **cuatro
columnas**: `pActividad` (6 − log10 µM), `limite_inferior`, `limite_superior` (con ±∞ cuando
no hay cota) y las etiquetas binarias, **derivadas** del intervalo.

**Por qué.** Es una lección de la fase 1 aplicada al revés: guardar solo `activo_10um` obligaría
a reconstruir todo si se adopta la regresión. Con el intervalo guardado **el umbral pasa a ser
una decisión de lectura** y los tres modelos candidatos leen el mismo archivo.

Y la regla del diccionario de la patrocinadora sale como consecuencia, no como caso especial:
`IC50 = 10 µM` es activo a 10 µM, y `IC50 > 10 µM` es inactivo, porque el censurado no tiene
cota inferior.

## 2.4 · Dónde se corta «activo»: 10 µM, y por qué no es un hallazgo

| umbral | con etiqueta | % activos | razón | sin decidir |
|:--|--:|--:|:--|--:|
| 10 µM | 67,736 | 72.8 | 2.68 : 1 | 2,648 |
| 1 µM | 69,632 | 50.2 | 1.01 : 1 | 752 |

> **P. ¿Por qué 10 µM?**
> **Es la concentración de cribado heredada del archivo, no un criterio farmacológico.** Dos
> tercios de las mediciones censuradas lo están exactamente en 10 µM, y el comentario de
> ChEMBL de los inactivos declarados dice «Inhibition < 50% @ 10 uM». Se conserva como
> principal por comparabilidad con el diccionario y se reporta 1 µM al lado.

> **P. Entonces, ¿por qué no 1 µM, que deja las clases balanceadas?**
> Porque elegir el umbral por cuál desbalancea menos sería un argumento de conveniencia
> estadística, no de farmacología. Lo medible **sí** favorece 1 µM (más censurados
> aprovechables, más pares etiquetados) y por eso los dos se reportan. El corte es reversible
> precisamente porque el objetivo es un intervalo.

**Una advertencia de procedencia del número**: el registro dice que cuando algo descansa en
lo que decidió la patrocinadora hay que escribir *quién lo decidió y de dónde viene*, no
inventarle una justificación farmacológica. Ese error ya ocurrió con el 10 µM durante tres
semanas y lo cazó una revisión.

## 2.5 · Lo que la etiqueta esconde: tres cosas que acompañan a toda métrica

**1. El mismo corte no mide lo mismo en cada diana** (`02b` §4.1). Con un solo umbral,
`LRRK2` queda con 96.5% de pares activos y `MAOA` con 35.0%; la potencia mediana va de 5.02 a
7.40, **241 veces**. En `LRRK2` la etiqueta es casi constante y como objetivo de clasificación
aporta poco. Se intentó un umbral por diana a partir de la moda de censura y **falló**: esa
moda es el techo de los ensayos que no encontraron nada, y dejaba seis dianas con 93-96% de
activos.

**2. La procedencia está confundida con la etiqueta** (`02b` §4.2):

| estrato | pares | % activos |
|:--|--:|--:|
| solo ChEMBL | 66,324 | 75.8 |
| solo NPASS | 2,231 | 14.0 |
| mixto | 1,828 | 40.0 |

Es **química real y no un artefacto**: la mediana de potencia de NPASS es 6.56 µM contra
0.335 µM en ChEMBL, unas veinte veces, así que **el corte de 10 µM cae casi en la mediana de
los naturales y a treinta veces de la de ChEMBL**. Para los naturales la etiqueta la decide el
ruido de medición. Consecuencia: la procedencia **nunca** entra como característica (un
compuesto nuevo no la tiene) y todo se reporta por estrato. Y hay un control de atajo: un
modelo que solo ve la procedencia ya alcanza el 65% del MCC de la química.

**3. Las mediciones del mismo par discrepan** (`02b` §4.3): el **25.5%** de los pares con
varias mediciones difiere más de 10×. Por eso se agrega con la **mediana** y no con el valor
más potente, que sesgaría hacia los activos. Así los conflictos bajan de 1,784 a 1,126.

## 2.6 · ¿Se pueden encadenar las dos fases?

**Solo 1,033 esqueletos tienen medición en las dos** (`01b` §4): el 1.0% del conjunto de
actividad y el 25.7% del de permeabilidad.

**Esto es lo que sostiene que la fase 1 no sea un filtro duro.** Para el 99% de los
compuestos con actividad documentada la permeabilidad sería una *predicción sin verificar*, y
descartarlos con ella eliminaría candidatos con actividad real.

> **P. ¿Por qué no usan esos 1,033 para evaluar la cadena completa?**
> Es una **decisión abierta**: reservarlos cuesta un cuarto de los datos de la fase 1, porque
> tendrían que salir también de su entrenamiento para no filtrar. El `01b` la deja como paso
> pendiente, y la propuesta C.3 —que prueba si combinar las dos predicciones selecciona mejor—
> se mediría solo sobre esos esqueletos y espera a la patrocinadora.

## 2.7 · La partición de la fase 2, y sus tres límites

La patrocinadora había reservado un 10% **al azar**; en la reunión del 15 de octubre aceptó
el argumento y entregó el archivo completo para rehacerla. Su única condición: reservar una
prueba que el modelo nunca vea.

Se agrupa por esqueleto + andamio. **24,230 grupos para 70,384 pares**, y el 59.8% de los
grupos tiene un solo par. Tres límites, **medidos y no escondidos**:

1. **La prueba son 13,973 pares en 13,973 grupos**: un andamio por par. Mide generalización a
   química nueva, pero no es una muestra representativa del conjunto.
2. **Tiene más activos que el entrenamiento**: 78.7% contra 71.6%. No es una prueba
   uniformemente más difícil, es una población distinta. La tasa base va al lado de toda métrica.
3. **Los naturales se concentran en entrenamiento**: solo el 5.2% de los pares de NPASS cae en
   la prueba, porque comparten andamios en familias grandes y `scaffold_split` manda los
   grupos grandes a entrenar. La evaluación por origen sobre la prueba descansa en **346
   pares** (117 de NPASS y 229 mixtos): una señal gruesa, no una comparación con intervalos.

> **P. ¿Por qué no particionan por artículo, para probar en estudios que el modelo no vio?**
> Se intentó y **no es viable**: los compuestos medidos en varios artículos enlazan las
> referencias entre sí, y un solo componente conexo reúne el **55.9%** de los pares. Cualquier
> partición por artículo pondría más de la mitad de los datos de un lado.

> **P. ¿Hacen un modelo por diana?**
> Se decidió para las dianas grandes, pero el criterio «mil pares o más» **no sobrevivió a la
> comprobación**: `LRRK2` deja un pliegue con 13 negativos y `GRIN2B` con 5, sin los que no hay
> métrica por pliegue ni punto de operación elegible. El criterio pasó a ser una condición
> —mil pares **y** cincuenta casos de la clase minoritaria en todos los pliegues—, que deja
> **once** dianas, el 85.6% de los pares ajustables.

---

# Lo que un profesor encontraría hoy en los cuadernos

Medido o comprobado al preparar esta guía. **Ninguna cambia una conclusión**, pero son cosas
que se ven al leer con cuidado y es mejor decirlas antes de que se pregunten.

| # | dónde | qué | qué es lo correcto |
|--:|:--|:--|:--|
| 1 | `02` celdas 0 y 61 | dicen que los naturales cruzan «18.9 puntos menos» | 28.3, con los tres orígenes. El 18.9 es la cifra con el grupo «sintético» que el propio `01` §5 superó |
| 2 | `02` §12.0 | dice que cambiar la transformación obligaría a rehacer el filtrado | falso en la versión actual: §8.2 y §9 del mismo cuaderno miden que la selección sale **igual** con las tres |
| 3 | `02b` §2 | habla de las «171 columnas» del Avance 2 | son **151** |
| 4 | `02b` §4.2 | «63 puntos» de diferencia entre `solo_chembl` y `solo_npass` | la tabla del propio cuaderno da 75.8 − 14.0 = **61.8** |
| 5 | `01` §6 y `02` §3 | 2,126 andamios en uno y 3,629 en otro | **misma definición con y sin estereoquímica**, medido aquí: 2,126 sin ella y 3,628 con ella (el 02 cuenta además el marcador de acíclicos). Ningún cuaderno lo dice |
| 6 | `01b` §6.5 y `02b` | 71,145 pares en uno y 70,384 en el otro | el `01b` los marca como exploratorios con otra regla; **no encontré la conciliación escrita**, así que no sé decir por qué difieren |
| 7 | `02` §12.7 | la prueba de humo (RF con descriptores+Morgan, MCC 0.594) se cita como apoyo de la 1.3 | es una sola partición de validación y el propio cuaderno dice que «nada de esto está asentado»; la comparación agrupada posterior (03c) no encuentra que las huellas cumplan la regla de mejora en ningún modelo de la fase 1 (solo el árbol sube, +0.013). **No citar esa tabla como evidencia** |
| 8 | C.2 y `regla_2p` | verifican contra TPSA < 67 | el proyecto derivó 107 y mostró que se mueve (ver §1.5) |

**Las filas 1 a 4 tienen issue propio, [#224](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/224)**, porque tocan una cifra publicada: una lista dentro de un documento no se asigna ni se cierra. Las filas 5 a 8 son diferencias de definición o preguntas sin respuesta escrita, y viven aquí.

## Qué sigue sin ratificarse

Los cuadernos lo repiten y el registro lo confirma: **la escala, la reducción de dimensión
([1.5](../decisiones.md#d1-5)), el corte de 10 µM ([2.3](../decisiones.md#d2-3)) y la
evaluación de la cadena completa (C.3) siguen como propuestas con su medición al lado**.
Nada es *ratificada* hasta que la patrocinadora lo revise. La columna de estado del registro
es la fuente.

## Dónde profundizar

| si te preguntan por… | lee |
|:--|:--|
| qué trae cada archivo y sus defectos | [`datos-contenido.md`](../datos-contenido.md) |
| la teoría detrás de una técnica | [`fundamentos-desde-cero.md`](../fundamentos-desde-cero.md) |
| un término | [`glosario.md`](../glosario.md) |
| qué se descartó y por qué | [`decisiones.md`](../decisiones.md), entradas 1.1 a 1.8 y 2.1 a 2.12 |
