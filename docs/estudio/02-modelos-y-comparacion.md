# Capa 2 · Los modelos y cómo se comparan (Avances 3 y 4)

Cuadernos `03_Baseline`, `03b_Baseline_regresion_actividad`, `03c_Permeabilidad_huellas`,
`04_Models`, `04b_Regresion_actividad` y `04c_Regresion_actividad_huellas`.

Se asume la [capa 1](01-datos-y-etiquetas.md): qué es una fila, qué significa «activo» y cómo
se partió. Misma estructura de siempre: **qué se hizo → por qué → la cifra y dónde está → la
pregunta del profesor → qué no sabemos.**

**El hilo de esta capa, en una frase:** lo que fue apareciendo es que el modelo importa menos
que cómo se evalúa, qué se hace con las mediciones censuradas y qué representación recibe, y
cada cuaderno añade una pieza de esa conclusión sin proponérsela.

## Mapa de los seis cuadernos

| cuaderno | fase | la pregunta que contesta | lo que decide o deja establecido |
|:--|:--|:--|:--|
| `03` | 1 | ¿contra qué se compara un 0.70? | el piso, la brecha y el mínimo aceptable (0.70 de MCC, 0.93 de AUROC) |
| `04` | 1 y 2 | ¿qué familia de modelo? | SVM RBF **sin afinar** como individual final; la clasificación de la fase 2 queda como piso |
| `03b` | 2 | ¿qué gana usar las censuradas? | los cuatro baselines de regresión; la ganancia sobre naturales tiene **dos escalones** |
| `04b` | 2 | ¿qué regresor? | kNN, SVR y MLP empatan; **ninguno** sirve en NPASS |
| `03c` | 1 | ¿las huellas ayudan a la permeabilidad? | **no**: ninguna de las 24 combinaciones modelo × brazo cumple la regla |
| `04c` | 2 | ¿las huellas ayudan a la potencia? | **sí**, a cinco de seis modelos, y reemplazan a los descriptores |

---

# Fase 1 · permeabilidad

## 1 · El baseline (`03`)

**Qué es y qué no.** Tres canalizaciones **sin afinar** sobre la misma partición y las mismas
métricas. Son **dos familias y no tres**: el bosque y el boosting son los dos ensambles de
árboles. «Sin afinar» no es «por omisión»: el bosque lleva 300 árboles y
`min_samples_leaf=2`, y la logística `max_iter=3000` para que converja. Son valores **fijados
una vez y no buscados**, que es lo que hace comparable el ejercicio. No es un modelo final ni
un ganador: con una sola configuración por familia, decir que una gana no se sostiene.

**Cómo se evita la fuga.** El escalado va dentro de la canalización, que se reajusta en cada
pliegue; ajustarlo antes de partir filtra la media y la varianza del pliegue de evaluación.

> **P. ¿Por qué no comparan contra los resultados publicados de BBBP?**
> Porque no son comparables: el mismo conjunto da baselines de 0.681 a 0.7194 de AUROC según
> quién los reporte, con otra implementación del scaffold split. El piso se mide aquí, con la
> misma partición.

## 2 · Contra qué se lee un número (`03` §2.4)

| clasificador que no mira la molécula | MCC | AUROC | AUPRC |
|:--|--:|--:|--:|
| al azar (proporción) | −0.0125 | 0.494 | 0.348 |
| siempre la mayoritaria | 0.000 | 0.500 | 0.350 |

**Por qué la métrica no es la exactitud.** Con 65.0% de BBB+, decir siempre «permeable»
acierta dos de cada tres veces y parecería un resultado. MCC y AUROC le dan 0.000 y 0.500, que
es lo que vale no mirar la molécula. **El AUPRC no tiene piso cero**: el trivial alcanza 0.350,
la proporción de la clase minoritaria, así que un 0.88 se lee contra 0.350 y no contra 0. Es la
misma trampa que la exactitud, en la métrica que la evita.

**El mínimo aceptable queda fijado aquí:** cualquier modelo que no supere de forma clara 0.70
de MCC y 0.93 de AUROC **medidos con esta partición y estas semillas** no justifica su
complejidad. Es un piso del proyecto y no de la literatura, a propósito.

## 3 · Ningún modelo gana, y por qué se dice así

Los intervalos del 95% de AUROC, remuestreando **grupos** y no filas (`03` §2):

| modelo | AUROC | intervalo |
|:--|--:|:--|
| logística | 0.9138 | [0.889, 0.935] |
| bosque | 0.9363 | [0.912, 0.955] |
| boosting | 0.9356 | [0.910, 0.955] |

Se solapan. **La desviación de la tabla no es un error estándar**: las tres semillas comparten
las mismas filas, así que los quince valores no son quince réplicas independientes.

> **P. La logística queda por debajo en los 15 pliegues. ¿Por qué no dicen que pierde?**
> Porque aplicarían dos criterios opuestos a la misma evidencia: su intervalo se solapa con el
> del bosque en más de lo que separa a sus estimaciones puntuales. Distinguirlas pediría el
> intervalo de la **diferencia pareada**, que no está medido en el 03.

## 4 · Cuánto pesa agrupar mal frente a elegir modelo (`03` §2.1)

| agrupamiento | grupos | AUROC | MCC |
|:--|--:|--:|--:|
| andamio ∪ esqueleto (el correcto) | 1,048 | 0.9363 | 0.6989 |
| solo andamio | 2,239 | 0.9586 | 0.7694 |

**Agrupar solo por andamio infla el AUROC en 2.2 puntos y el MCC en 7.1.**

> **P. ¿Eso es más o menos que elegir bien el modelo?**
> **Depende del estimador, y el 03 lo advierte.** Con el mismo estimador en las dos
> comparaciones, en MCC el agrupamiento mueve 7.1 contra 2.2 entre las tres canalizaciones:
> algo más de tres veces. **En AUROC es lo mismo**: 0.0223 contra 0.0225. Con estimadores
> distintos salía 4.6 veces y el resultado se invertía. Por eso la conclusión fuerte es solo la
> de MCC, y la frase que sí se sostiene con cualquiera es: **una cifra que no diga cómo agrupó
> no se puede comparar.**

## 5 · ¿Sobreajusta? (`03` §2.3)

| | MCC en ajuste | MCC en validación | brecha |
|:--|--:|--:|--:|
| bosque | 0.955 | 0.698 | 0.26 |
| boosting | 0.972 | 0.702 | 0.27 |
| logística | 0.739 | 0.687 | 0.05 |

Los árboles **memorizan**: su línea de ajuste es plana desde 168 estructuras. La brecha sí se
cierra con más datos, pero poco: quintuplicar las estructuras quitó una quinta parte. **El
último 20% aporta menos de una centésima de MCC en los tres modelos**, así que más compuestos
del mismo tipo ayudarían poco; lo que falta es regularizar los árboles.

## 6 · Qué características pesan (`03` §2.2)

Regla del proyecto: **no creerle a un solo método de atribución.** Dos que miden cosas
distintas:

- **Impureza del bosque**: barata, pero favorece variables con muchos valores distintos.
- **Permutación sobre el pliegue de evaluación**: cuánto AUROC pierde al barajar la columna;
  mide lo que el modelo *necesita para generalizar*, no lo que memorizó.

Coinciden en **11 de las 15** primeras y discrepan en el orden: la impureza pone a TPSA arriba;
la permutación a `fr_lactam` y `fr_COO`. Se reporta la **intersección**.

> **P. 24 de 151 columnas no dañan al modelo al permutarlas. ¿Las quitan?**
> No, y la cuenta tiene ruido: en solo 4 de esas 24 la media supera su propia desviación.
> En toda la matriz solo 75 de 151 tienen una media mayor que su desviación, así que **el orden
> de la cola no está medido; el de la cabeza sí**.

## 7 · Una limitación declarada desde el principio

Las 151 columnas se eligieron mirando todo el entrenamiento, y la validación cruzada reparte
esas mismas filas: cada pliegue de evaluación contiene filas cuyas etiquetas ayudaron a elegir
columnas. Los filtros de casi constancia y de Spearman son casi insensibles a la etiqueta, pero
el desempate entre columnas correlacionadas usa la F de ANOVA contra ella, **así que la fuga
existe aunque sea pequeña**. Se declara en el 03 y se dejó a medirse. Una auditoría posterior
la midió ([#195](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/195)) y la
encontró de magnitud cero, con la salvedad de que el brazo de descriptores no es un control
limpio.

---

## 8 · Las seis familias y el modelo individual final (`04`)

**Seis familias sin ensamble**, con sesgos distintos: lineal (logística, el control
interpretable), árbol, vecinos, generativo (Naive Bayes), núcleo (SVM con RBF) y red pequeña.
La rúbrica evalúa que sean **variadas**, no que sean las seis de mayor métrica: el árbol y
Naive Bayes entran aunque queden últimos. Se descartaron LDA, por parecerse a la logística, y
el SVM lineal por SGD, porque el SVM con RBF ya cubre esa familia.

| modelo | MCC | AUROC | AUPRC min. | seg/ajuste |
|:--|--:|--:|--:|--:|
| `svm_rbf` | **0.703** | **0.919** | 0.884 | 0.54 |
| `logistica` | 0.688 | 0.913 | 0.872 | 0.03 |
| `mlp` | 0.674 | 0.913 | 0.865 | 5.7 |
| `knn` | 0.669 | 0.914 | 0.863 | 0.004 |
| árbol | 0.568 | — | — | — |
| Naive Bayes | 0.566 | — | — | — |

**Cuatro quedan arriba y no se distinguen**: entre el primero y el cuarto hay ~0.03 y el
resultado se mueve más que eso entre evaluaciones (0.065 a 0.094).

### Por qué el SVM sin afinar, y no solo «porque gana»

- **Afinarlo no ayudó**: 0.699 afinado contra 0.703 sin afinar, y **veinte veces más lento**
  (10.8 s contra 0.54 s por evaluación).
- **No hay un `C` estable.** Lo que eligió en los 15 pliegues: 1 (siete veces), 10 (cuatro),
  100 (dos) y 0.1 (dos). Toca los dos extremos de la rejilla: no es que el mejor valor esté
  fuera de ella, es que **el que gana cambia según cómo caiga la partición**. Estaba ajustando
  ruido. El kNN es lo contrario: 15 vecinos en 13 de 15, que es lo que ya tenía.
- **Gana por consistencia, no por distinguirse**: su ventaja sobre el kNN (0.034) es menor que
  lo que oscila el resultado (~0.08).

> **P. La logística tiene mejor MCC que el kNN y es interpretable. ¿Por qué la dejaron fuera?**
> La regla de «los dos mejores» se fijó antes de correr y **ordena por AUROC**, no por MCC: la
> logística quedó fuera por **0.001** (0.913 contra 0.914). No se cambió la regla al ver los
> números, y el propio 04 lo reconoce: **el criterio de selección y la métrica principal no
> coinciden**, y eso quedó para el Avance 5.

> **P. ¿Por qué corrieron los seis modelos también en la fase 2?**
> Porque **el orden cambia**: en la fase 2 (clasificación a 10 µM) encabezan la red (0.499) y el
> kNN (0.496), el SVM baja al tercer lugar (0.441) y la logística cae de 0.688 a 0.387. Elegir
> el modelo de una fase mirando la otra habría sido un error. La explicación del cambio
> («a los modelos que se adaptan les sirve más tener nueve veces más filas») es razonable y
> **el cuaderno dice que no la prueba**.

---

# Fase 2 · potencia, con censura

## 9 · Por qué una regresión (decisión [2.9](../decisiones.md#d2-9))

La fase 2 empezó como clasificación a 10 µM (el `04` §3.1). Después, una aclaración de la
patrocinadora sobre qué debía predecirse cambió el enfoque: **se predice cuánta potencia tiene
(`pActividad`) y la clase se deriva al final**. La tabla de clasificación del 04 queda como
**piso**, no como ejercicio principal.

El motivo, ya visto en la capa 1: el corte de 10 µM no significa lo mismo en cada diana (deja
a `LRRK2` en 98.1% de activos y a `NFE2L2` en 50.7%), y clasificar tira el orden dentro de cada
clase.

## 10 · Los cuatro baselines (`03b`)

Cuatro, y **dos son Ridge a propósito**, para no confundir dos efectos:

| baseline | qué ve | para qué |
|:--|:--|:--|
| `media` | las exactas; predice siempre su promedio | el **piso** |
| `ridge_exactas` | solo las exactas | lo que haría un baseline sencillo |
| `ridge_cota_imputada` | exactas y censuradas, **tomando la cota como si fuera el valor** | lo ingenuo de quien no quiere tirar los inactivos |
| `tobit` | exactas y censuradas **como cotas, con su verosimilitud** | la misma recta tratando la censura como lo que es |

El Tobit ve más filas que `ridge_exactas` **y** usa otra pérdida, así que su ventaja admite dos
lecturas. `ridge_exactas` contra `ridge_cota_imputada` mide **lo que vale no tirar los
censurados**; `ridge_cota_imputada` contra `tobit` mide **lo que vale la verosimilitud**. La
primera versión del diseño mezclaba las dos y lo corrigió una revisión.

**La métrica principal es la concordancia de Harrell**: compara solo pares cuyos intervalos no
se solapan (`superior_i < inferior_j`), porque solo de esos se sabe cuál es más potente. Un par
es concordante si el modelo predice más potencia para el más potente, y un empate cuenta medio.
**Es la única que usa las censuradas.** Spearman y RMSE van solo sobre las exactas y devuelven su
`n`, porque una cifra sin su `n` no se puede leer.

**El Tobit en una frase:** supone que la potencia es normal alrededor de una recta y maximiza la
verosimilitud de lo que cada fila *sí* dice: una exacta aporta su densidad, un `> 10 µM` aporta
la probabilidad de caer por debajo de pActividad 5.

| | `ridge_exactas` | `ridge_cota_imputada` | `tobit` |
|:--|--:|--:|--:|
| concordancia, agregado | 0.693 | 0.698 | 0.700 |
| MCC de la clase derivada | 0.225 | 0.293 | 0.363 |
| concordancia, **solo NPASS** | 0.533 | 0.586 | **0.639** |
| RMSE sobre exactas | 1.156 | 1.186 | 1.234 |

**El hallazgo del 03b: la ganancia sobre los naturales tiene dos escalones de tamaño parecido**
(+0.053 y +0.053, de 1.5 a 1.8 veces la dispersión; el total, 3.4 veces). Uno llega solo por
**no tirar los censurados**; el otro, **por tratarlos con su verosimilitud**. Ninguno cabe solo
fuera del ruido; juntos sí. Y **la censura cuesta exactitud en las exactas**: el RMSE sube
1.156 → 1.234.

> **P. ¿Qué es el «techo de ruido» y por qué importa?**
> Repetir el mismo ensayo da diferencias de unas 0.7 unidades logarítmicas en IC50 y 0.5 en Ki.
> Un error muy por debajo de eso **no sería buen resultado sino señal de fuga**. Los modelos
> quedan en 1.16 a 1.23, de 1.7 a 1.8 veces el ruido: lejos del techo y sin indicio de fuga.

> **P. El Tobit atribuye σ = 1.31, más que el techo de 0.7. ¿La medición es tan ruidosa?**
> No: ese σ dice cuánto **deja sin explicar la recta**, no que la medición sea tan ruidosa.

## 11 · Seis regresores (`04b`)

Una tabla de correspondencia con el 04: logística → `Ridge`, árbol → `DecisionTreeRegressor`,
kNN → `KNeighborsRegressor`, Naive Bayes → `BayesianRidge` (que no tiene versión de
regresión), SVM → `SVR`, MLP → `MLPRegressor`. `media` va aparte porque es el piso y **no es un
algoritmo**. Se entrenan **solo con las exactas** y se valida con las censuradas incluidas.

La métrica principal se fijó **antes de ver los resultados**: la primera versión ordenaba por
Spearman, que solo mira exactas, y se cambió a la concordancia.

| modelo | concordancia |
|:--|--:|
| `knn` | 0.739 |
| `svr` | 0.738 |
| `mlp` | 0.735 |
| `ridge`, `bayesian_ridge` | 0.691, 0.692 |
| árbol | 0.670 |

Tres se despegan y **entre ellos no hay ganador** (0.001 a 0.004 de diferencia contra 0.004 a
0.006 de oscilación).

**El resultado que anuncia todo lo que viene:**

> En los pares que solo tiene NPASS, **los seis modelos están cerca del azar: entre 0.464 y
> 0.551** de concordancia (el kNN queda **por debajo de 0.5**). Y el baseline del 03b, **que es
> solo una recta**, saca 0.639 en esos mismos pares.

Es decir: **tratar bien la censura rinde más que un modelo más flexible.** Y el 04b ofrece una
lectura de por qué, que él mismo declara que no demuestra: el kNN y el SVR son los que mejor
ordenan las exactas de NPASS (Spearman 0.34 y 0.31) y los que tienen la concordancia más baja,
así que *predicen bien lo exacto y colocan mal lo censurado*, que es la mayor parte de los
negativos de NPASS.

**Y por qué importa dejar fuera las censuradas:** esta regresión descarta **7,535 de los 15,554
pares inactivos, el 48.4%**, que existen solo como cotas y son justo los compuestos flojos.
(La capa 1 cita 49.4%: es el mismo hecho sobre otro conjunto, los 70,384 pares completos contra
los 56,241 de ajuste.) Esa es la razón de que el Avance 5 entre con un modelo que sí use la
censura.

---

# Las huellas, en las dos fases (`03c` y `04c`)

## 12 · Qué se compara y cómo se lee

**Cinco brazos con los mismos modelos, filas, pliegues y semillas**; cambia una sola cosa, qué
información de la estructura reciben:

| brazo | qué recibe |
|:--|:--|
| `descriptores` | el control: **tiene que repetir** la corrida registrada |
| `depurados` | los descriptores sin casi constantes ni redundantes, **aprendido en cada pliegue** |
| `seleccionados` | los que un Lasso no manda a cero, en cada pliegue |
| `descriptores+huellas` | los descriptores y las 2,048 huellas |
| `huellas` | solo las huellas |

**Lo que más importa de los dos cuadernos:** el vocabulario de Sort & Slice se **reaprende
dentro de cada pliegue**. Si se contaran las subestructuras frecuentes con todas las filas, la
validación ya habría influido en qué columnas existen, y es una fuga que no aparece en ninguna
métrica y hace que las huellas parezcan mejores de lo que son. Antes de eso se agrupan las
subestructuras que valen lo mismo en todas las filas (el `S` y el `O=S` de un sulfonilo): no
mira la etiqueta, así que no filtra.

**La regla de mejora:** un brazo mejora a un modelo solo si la diferencia media pareada supera
un umbral **y** es positiva en al menos **12 de las 15** evaluaciones (3 semillas × 5
pliegues). En la fase 1 son **dos** métricas a la vez, MCC y AUPRC.

> **P. ¿La regla estaba pre-registrada?**
> **No, y los cuadernos lo dicen:** «se fijó después de explorar un pliegue del 04b». Lo que sí
> se cumple es que quedó escrita antes de ejecutar y **no se ajustó al ver los resultados**.
> No es lo mismo que «fijada antes de medir», y conviene no decirlo así. Los 12 de 15 no son una
> probabilidad: las semillas comparten filas, es una prueba de signos con esa limitación.

> **P. ¿Por qué el umbral cambia entre cuadernos?**
> Cada cuaderno lo calcula con **su propio control**, y salen distintos: 0.094 de MCC y 0.058
> de AUPRC en el 03c (la mayor desviación entre los seis modelos), 0.007 de concordancia en el
> 04c, 0.073 y 0.041 en el 05. Es consistente con la regla, pero un lector que los vea juntos
> pregunta. Y la definición escrita en el 05 («la mayor desviación») no es la que calcula el
> código (`.std()` del mejor individual):
> [#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188).

**El control es parte del resultado.** El brazo `descriptores` reproduce la corrida registrada:
en la fase 2 con diferencia **0.000**; en la fase 1 en **17 de 18 casillas**. La 18ª era el
AUPRC de Naive Bayes y exigió **arreglar el arnés**: la clase minoritaria se puntuaba con
`1 − p`, y toda `p` menor que la mitad del épsilon de la máquina da `1 − p == 1.0`, lo que
dejaba empatadas en la cima 504 filas (154 de ellas de la clase mayoritaria). Se cambió a `-p`.
Nunca afectó al AUROC de la tabla.

## 13 · Fase 2: las huellas mejoran (`04c`)

| modelo | `descriptores` | `descriptores+huellas` | diferencia | `huellas` solas |
|:--|--:|--:|:--|--:|
| `knn` | 0.739 | **0.756** | +0.017, 15 de 15 | 0.755 |
| `bayesian_ridge` | 0.692 | 0.728 | +0.036, 15 de 15 | 0.726 |
| `ridge` | 0.691 | 0.724 | +0.033, 15 de 15 | 0.722 |
| `linear_svr` | 0.690 | 0.722 | +0.032, 15 de 15 | 0.720 |
| árbol | 0.670 | 0.684 | +0.014, 15 de 15 | **0.716** |
| `mlp` | 0.735 | 0.708 | **−0.027, 0 de 15** | 0.714 |

Los cinco mejoran **en las 15 evaluaciones**, de dos a cinco veces el umbral (0.007). Y **los
fragmentos reemplazan a los descriptores, no se suman**: el brazo de solo huellas queda a 0.002
o menos del ancho en cuatro modelos y lo supera en el árbol y el `mlp`.

> **P. ¿Por qué empeora el `mlp`?**
> Su brecha entre entrenamiento y validación pasa de 0.088 a **0.255** (0.962 contra 0.708).
> Es el único que memoriza las huellas.

> **P. ¿Y el SVR, que era el mejor con descriptores?**
> **No está medido con huellas**: un solo ajuste pasó de 27 minutos y se sustituyó por un
> `LinearSVR`. Así que 0.756 es la mejor cifra *de lo que se midió*, no de todo lo posible.

**Cuánto de eso es química y cuánto saber la diana.** El piso `media_por_diana` —que no mira la
molécula— da **0.642** contra 0.500 del promedio de todo. De los 0.239 que el kNN separa por
encima de 0.5, unos 0.142 los separa quien solo sabe contra qué diana se midió. Lo que queda es
la parte química: de 0.097 a 0.114 en el kNN, de ~0.05 a ~0.08 en los lineales. **Son ganancias
reales, en 15 de 15, pero sobre una base pequeña.**

**Por procedencia** (exploratorio): en `solo_chembl` mejoran cinco de seis; en `solo_npass`
**solo el `knn` mejora (+0.085, 15 de 15)** y los lineales empeoran; y ahí **todo queda cerca
del azar** (el mejor, 0.548). Además el piso por diana en NPASS es **0.403, por debajo del
azar**: la potencia media de una diana, dominada por ChEMBL, ordena al revés los pares de
NPASS. Por eso las diferencias contra el piso salen grandes en NPASS sin que se aprenda más
química.

## 14 · Fase 1: las huellas no mejoran (`03c`)

Umbrales **0.094 de MCC y 0.058 de AUPRC**, y **ningún brazo mejora a ningún modelo**. Lo más
cercano: el árbol con solo huellas en AUPRC, +0.035 en 13 de 15; cumple el mínimo de pliegues y
no el umbral, y su MCC sube solo 0.013. La regla es conservadora a propósito y **no se baja**.

- **Las huellas no sustituyen a los descriptores**: `descriptores+huellas` supera a `huellas`
  en los seis modelos (logística +0.039, SVM +0.031, MLP +0.028, kNN +0.018 de MCC).
- **Sí ensanchan el sobreajuste**: la brecha de la logística pasa de 0.029 a 0.091 con huellas,
  y la de Naive Bayes de 0.021 a 0.082. El árbol es el único que no la ensancha.
- **Naive Bayes es el caso extremo** (−0.242 de AUPRC en 15 de 15) y tiene explicación:
  asume independencia entre variables, y 2,048 fragmentos que coocurren son donde más falla.
- **Quitar descriptores no cambia nada**: se puede prescindir de un tercio sin perder nada
  medible, y no se gana nada por hacerlo.
- **Por origen** (exploratorio): ayudan donde el proyecto menos las necesita, en los
  compuestos sin equivalente natural, y no mejoran nada en naturales exactos ni en análogos.

## 15 · Por qué se invierte entre fases

El 03c lo dice así: allá se predice la potencia de un par compuesto-diana y aquí una propiedad
de transporte que los descriptores ya describen bien. La [1.3](../decisiones.md#d1-3) lo recoge:
**la permeabilidad depende de propiedades de la molécula entera** (TPSA y donadores de
hidrógeno dominan) **y la potencia contra una diana depende de qué fragmentos tiene.**

**Es una hipótesis razonable con evidencia a favor, no un resultado establecido**, y tiene una
rival que los datos no descartan: que las huellas ganen donde el espacio químico está
densamente muestreado, que es lo que también cuadra con que en la fase 1 ayuden en el estrato
más denso. Separarlas es el experimento del
[#215](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/215), todavía sin correr.

**Dónde convergen los dos cuadernos, que es lo más sólido:** la ganancia amplia está del lado
no natural en los dos. En ChEMBL para la fase 2, en los compuestos sin equivalente natural para
la fase 1.

**Qué se decide para el Avance 5:** la fase 2 entra **con** huellas, y la fase 1 **sin**, por
desempeño. Ojo con lo que eso significa: entran los ensambles; el `aft`, que acaba siendo el
modelo final de la fase 2, corre **sin** ellas, y por qué —y qué costó no haberlo medido antes—
es de la capa siguiente. En la fase 1 el argumento que queda es la explicabilidad —una columna es una
subestructura—, y hay que decir que se usan *para explicar, no porque midan mejor*.

---

# Lo que un profesor encontraría en esta capa

| # | dónde | qué | qué hacer con ello |
|--:|:--|:--|:--|
| 1 | `05` §4 y su declaración | decían que la regla «se fijó antes de medir» | los tres cuadernos que la crearon dicen **«no pre-registrada»**, y el propio 05 también en su celda de parámetros. Lo correcto: escrita antes de correr, **después de ver el control**, sin ajustarse. Corregido en el #222; **el mismo error estaba en el sitio y en el esqueleto del artículo**, y también se corrigió |
| 2 | `03c`, `04c`, `05`, `05c` | cuatro umbrales distintos (0.094, 0.007, 0.073, 0.081) | cada uno sale de su control; explicarlo antes de que se pregunte. Más el [#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188) |
| 3 | proyecto entero | tres denominadores para «cuánto separa a los modelos»: 1.5 puntos (decisión 1.2), 2.2 (`03` §2.1, tres canalizaciones, mismo estimador) y 4.2 (`05`, once modelos) | cuánto separa a los modelos depende de **cuántos modelos se comparen**; decir siempre cuál se usa |
| 4 | `03c` §3.1 y `04c` §3.1 | el primero dice que en NPASS las huellas mejoran a «dos de seis» y el segundo a «solo el `knn`» | **medido aquí, sobre `04c_brazos.csv`**: con el brazo ancho 2 de 6 tienen media positiva (árbol +0.0155 en 11/15, kNN +0.0829 en 15/15); bajo la regla de 12 de 15 y con el brazo de solo huellas, 1 de 6. Son dos criterios sobre los mismos datos y ninguno lo dice |
| 5 | `04` §6 | prometen implementar SHAP | **no hay una sola línea de SHAP** en el código; la explicabilidad es permutación e impureza |
| 6 | `04` §4 | la selección de «los dos mejores» ordena por AUROC y la métrica principal es MCC | declarado en el propio cuaderno; es la razón de que la logística quede fuera por 0.001 |
| 7 | `03b` y `02b` | 48.4% y 49.4% de los negativos solo existen como cotas | mismo hecho sobre conjuntos distintos (56,241 y 70,384 pares); decir el conjunto |
| 8 | `04b` | «Vamos a proponer un modelo que trata las censuradas» | cumplido en el 05b; es el hilo que une esta capa con la siguiente |

## Dónde profundizar

| si te preguntan por… | lee |
|:--|:--|
| por qué esas métricas | decisión [C.1](../decisiones.md#dc-1) |
| los tres candidatos y escalar o no | decisión [1.5](../decisiones.md#d1-5) |
| regresión con censura | decisión [2.9](../decisiones.md#d2-9) |
| qué añaden las huellas | decisión [1.3](../decisiones.md#d1-3) |
| un término | [`glosario.md`](../glosario.md) |
