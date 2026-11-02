# Auditoría científica y de método del Avance 5

**Qué es este documento.** Una revisión de solo lectura del Avance 5, hecha sobre `main` en
`9d9b62b` el 1 de noviembre de 2026 por una sesión de Claude Code que no participó en construir
nada de lo que revisa, a petición de un integrante del equipo. No modificó ningún archivo del
repositorio. Se guarda aquí, y se declara en los cuadernos, por el mismo criterio con que el
Avance 4 llevó a su declaración de uso de IA una auditoría hecha por un agente que no participó
en la tarea.

**Por qué se entrega con el avance en vez de después.** Lo que encontró no invalida ninguna
conclusión: no hay fuga de datos que infle una cifra, ninguna de las 65 cifras cotejadas está
inventada, y los dos modelos finales se sostienen. Lo que encontró es que **la prosa afirma más de
lo que sus números sostienen**, en cuatro lugares independientes. Reescribir esos cuatro
argumentos con prisa habría sido peor que publicarlos con el defecto señalado, así que se publican
con el defecto señalado y cada hallazgo abierto como issue.

## Lo que se comprobó de forma independiente

Antes de aceptar la auditoría, otro integrante verificó sus afirmaciones de más peso contra las
corridas registradas. Las cinco se sostienen, y una de ellas corrige al propio equipo:

| hallazgo | resultado de la verificación |
|:--|:--|
| §1.3 · el AUPRC por estrato promedia dos clases | **confirmado.** 12 de 15 pliegues miden BBB− en `natural exacto` y 12 de 15 miden BBB+ en `análogo estereoquímico`; la prevalencia por pliegue va de 0.438 a 0.594 y de 0.234 a 0.585 |
| §1.4 · la celda 8 dice «la mayor desviación» y la 16 usa `.std()` | **confirmado** en el código |
| §2.6 · el registro no recoge la fase 1 | **confirmado.** `svm` aparece cero veces en `docs/decisiones.md` y la 1.5 sigue marcada como propuesta |
| §2.1 · la calibración del SVM parte sin agrupar | **confirmado.** `CalibratedClassifierCV(SVC(...), ensemble=False)` sin `cv`, y `alternativos.py` solo se tocó en el #118 |
| §3.1 · cinco conteos sin corrida detrás | **las cinco cifras son correctas.** La auditoría no pudo comprobarlas porque su contenedor no tenía los datos; recomputadas sobre `fase2_pares.parquet` dan 52,529 · 16.6% · 2,114 · 53.5% · 982, exactas. Lo que queda en pie es que no tienen corrida, no que estén mal |

## Los hallazgos, como issues

| § | issue |
|:--|:--|
| 1.1 · la razón 1 del modelo final de la fase 2 mide colocación de umbral | [#185](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/185) |
| 1.2 · la condición de refutación de la fase 2 quedó sin comprobar | [#186](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/186) |
| 1.3 · el AUPRC por estrato promedia dos clases | [#187](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/187) |
| 1.4 · el umbral de la regla | [#188](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/188) |

Los de prioridad 2 y 3 se abren a continuación. El [#183](https://github.com/AntonioVazquezMartinez/Bioactive-AI/issues/183), abierto antes de esta auditoría, guarda el caso de las huellas y el estrato de análogos estereoquímicos.

---

## Lo primero, porque suele ser lo que preocupa

**No hay fuga de datos que infle ninguna cifra reportada.** El arnés recibe canalizaciones y no
modelos, clona por pliegue, remuestrea grupos y no filas, y donde los envoltorios fallan, fallan con
una excepción en vez de partir al azar en silencio. El stacking agrupado está bien construido: sin
grupos lanza `ValueError` y no existe rama que caiga a una partición aleatoria.

**De 65 cifras cotejadas contra su corrida, ninguna está inventada.** Cuatro son distintas, cinco no
tienen corrida detrás. Las quince celdas de la tabla por procedencia de la fase 2 salen idénticas.

La concordancia de Harrell con censura se verificó numéricamente: los pares censurados del mismo
lado dan cero pares comparables, que es lo correcto, y el sentido de la censura es el que corresponde
a cada escala. Y la trampa evidente de la fase 2 no está: todos los modelos se evalúan sobre las
mismas filas de validación con el intervalo completo, porque el filtrado de exactas ocurre solo en
`fit`.

Los problemas están concentrados en otro sitio: **la prosa afirma más de lo que sus números
sostienen**, y lo hace de forma independiente en cuatro lugares. El código es más honesto que el
texto que lo describe.

---

## Prioridad 1 · Hallazgos que afectan una conclusión publicada

### 1.1 · La razón principal para elegir el AFT mide colocación de umbral, no discriminación

El argumento del modelo final de la fase 2 dice «gana donde el proyecto decide, MCC 0.467 contra
0.310» (cuaderno 05b, celda 14 §5.1, y `docs/decisiones.md:830`). El resto de las métricas del mismo
par lo contradice. Recomputado de
`experimentos/2026-10-31-antonio-2.13-comparativa-regresion-ensambles/pliegues.csv`, estrato `todos`,
media de 15 evaluaciones:

| modelo | concordancia | Spearman | RMSE | MCC | AUROC |
|:--|--:|--:|--:|--:|--:|
| `bosque` | 0.7650 | 0.7160 | 0.9385 | 0.3103 | 0.8333 |
| `aft` | 0.7610 | 0.6592 | 1.0315 | 0.4668 | 0.8459 |

El AFT ordena peor (−0.004 de concordancia, −0.057 de Spearman) y yerra más (+0.093 de RMSE), con el
AUROC casi empatado (+0.013). Un modelo que ordena peor y erra más no puede clasificar mucho mejor
por discriminar mejor: la diferencia de 0.157 en MCC, que es doce veces la de AUROC, está en dónde
cae su distribución predicha respecto del corte fijo de pActividad 5
(`src/models/baseline_regresion.py:42,181`). Eso lo mueve `SoloExactas` por construcción, porque
entrena solo con el subconjunto exacto, rico en activos. El propio cuaderno lo documenta sin
conectarlo: pendiente 0.423 y rango predicho 2.4–9.4 contra 2.1–12.0 observado (celda 22, gráfico 1).

**El argumento de NPASS no depende de esta línea y se sostiene solo.** La elección del AFT
probablemente aguante. Lo que hay que hacer es reescribir esa razón o respaldarla con el MCC a un
umbral elegido en validación, por modelo.

### 1.2 · La fase 2 escribió su condición de refutación y no fue a comprobarla

El 05b declara por escrito, antes de medir: «Lo que cambiaría esta elección es cualquiera de tres
cosas. Que el AFT con huellas no sostenga la ventaja en NPASS. Que el `solo_npass` de la prueba
reservada la contradiga. O que el criterio del proyecto deje de ser priorizar productos naturales.»

La prueba reservada dice esto (`.../comparativa-regresion-ensambles/metricas.json`, clave
`prueba_por_origen`):

| estrato | concordancia | AUROC | MCC | Spearman | n |
|:--|--:|--:|--:|--:|--:|
| todos | 0.720 | 0.793 | 0.277 | 0.600 | 13,944 |
| solo ChEMBL | 0.717 | 0.789 | 0.260 | 0.591 | 13,598 |
| **solo NPASS** | **0.530** | **0.536** | **0.065** | **0.083** | **117** |

En validación cruzada el AFT daba 0.632 en NPASS, y esa cifra es la razón número dos de las tres por
las que se eligió. En la prueba queda en el azar. El cuaderno **calcula** ese desglose y lo escribe
en la corrida, pero ninguno de esos cinco valores aparece en su prosa; se buscaron uno por uno.

Matiz necesario: son 117 pares, así que el intervalo es ancho y tampoco refuta el 0.632. Lo que no
hace es sostenerlo. La condición que el equipo declaró apunta exactamente ahí y quedó sin resolver.

La fase 1 hizo esto bien y conviene decirlo: su celda 25 confronta la caída, señala que el AUROC
pierde 0.126 y que eso no depende del umbral, y cierra con que «la cifra honesta del Avance 5 es la
de la prueba». Es el modelo a seguir.

### 1.3 · El AUPRC por estrato promedia dos clases distintas

`src/evaluation/cv.py:80` decide la clase minoritaria en cada llamada, es decir por modelo, semilla,
pliegue y estrato. En los estratos cuya prevalencia por pliegue cruza 0.5, la clase medida cambia
entre pliegues, y `resumen`, la tabla y el JSON registrado promedian las dos. El resultado no es
ninguna de las dos cantidades y su línea base salta.

| estrato | pliegues que miden BBB− | que miden BBB+ |
|:--|--:|--:|
| natural exacto | 36 de 45 | 9 de 45 |
| análogo estereoquímico | 9 de 45 | 36 de 45 |

Las dos cantidades distan hasta 0.050 de AUPRC. El 0.9016 publicado del `bosque` en análogos es la
mezcla de 0.9116 sobre 108 pliegues y 0.8616 sobre 27. Igual en
`notebooks/datos/baseline_permeabilidad-descriptores-origen.csv`, `03c_brazos.csv` y `05c_brazos.csv`.

Y `docs/decisiones.md:410` afirma que esas métricas «miden el desempeño sobre BBB− en cada estrato».
En análogos la minoritaria es BBB+ en cuatro de cada cinco pliegues, así que ahí mide BBB+. El
confundido es «minoritaria» con «BBB−»: cierto en el agregado, falso en esos dos estratos.

**Qué lo salva de invalidar decisiones:** toda comparación que decide algo (1.3, 1.5, 2.13) es
pareada por evaluación, y el volteo depende solo de las etiquetas del pliegue y no del modelo, así
que los dos brazos voltean juntos. Y los umbrales de la regla se calculan sobre el estrato `todos`,
cuya prevalencia es siempre 0.65. Lo que está mal es la cifra absoluta por estrato y su etiqueta, que
es justo lo que se publica en los desgloses por origen.

**Arreglo barato:** `orientar_minoritaria` ya devuelve `volteada` (`cv.py:82`) y solo la usa
`graficos.py` para rotular. Guardarla como columna en la tabla larga y en el JSON, o fijar la clase
por fase. Ninguna prueba lo cubre hoy.

### 1.4 · El umbral de la regla no es lo que su prosa dice, ni está en la escala que compara

Dos problemas encadenados en el cuaderno 05.

**La definición escrita no produce el número publicado.** La celda 8 define el umbral como «la mayor
desviación de esa métrica entre las 15 evaluaciones del mejor individual». La celda 16 usa `.std()`.

| | con `.std()` (publicado) | con «la mayor desviación» |
|:--|--:|--:|
| MCC | 0.073 | 0.1298 |
| AUPRC minoritaria | 0.041 | 0.0811 |

Quien siga el texto no reproduce la cifra, y obtiene una regla casi el doble de conservadora.

**El umbral mide dispersión entre pliegues; el estadístico es una diferencia pareada**, donde la
dificultad del pliegue se cancela. La desviación pareada es entre 2.3 y 19 veces menor, así que el
umbral está unas cuatro o cinco veces inflado en las unidades de lo que juzga. La columna `dif_desv`
de la propia celda 16 ya calcula la dispersión correcta y no se muestra.

**La conclusión aguanta, por otro camino.** Aplicando el error estándar corregido de Nadeau y
Bengio, con la misma fórmula que ya usa `scripts/experimento_derivadas.py:125` en el supuesto S1.11:

| métrica | modelo | diferencia | IC 95% corregido |
|:--|:--|--:|:--|
| MCC | `stacking` | +0.0093 | [−0.0085, +0.0270] |
| MCC | `votacion` | +0.0075 | [−0.0097, +0.0247] |
| AUPRC | `votacion` | +0.0108 | [+0.0001, +0.0214] |
| AUPRC | `stacking` | +0.0093 | [−0.0023, +0.0210] |

Todos incluyen el cero o lo tocan. «Ningún ensamble mejora al mejor individual» es correcto; el
argumento escrito no lo es, y el instrumento correcto ya está en el repositorio y ya se usó en otra
entrada del registro.

---

## Prioridad 2 · Defectos reales con impacto acotado

### 2.1 · La única partición interna que no agrupa, y está en el modelo final de la fase 1

`src/models/alternativos.py:79-80`: `CalibratedClassifierCV(SVC(...), ensemble=False)` con el `cv`
por omisión parte internamente en cinco pliegues estratificados **al azar**. Es el tipo de partición
contra la que argumentan los docstrings de `ajuste.py` y `ensambles_clasificacion.py`.

- No es fuga hacia el pliegue externo: todo ocurre dentro del subconjunto de ajuste.
- El AUROC y el AUPRC no se afectan, porque Platt es monótona.
- El MCC y la exactitud balanceada sí, porque cortan en 0.5 sobre esa probabilidad. **El sesgo
  probablemente va en contra del modelo**, no a favor.
- Pesa porque el `svm_rbf` es el modelo final de la fase 1 y viaja dentro de `bagging_svm` y de las
  bases de `votacion` y `stacking`.
- `tests/test_ensambles_clasificacion.py:39-52` no lo detectaría: espía `StratifiedGroupKFold.split`
  y esto usa `StratifiedKFold`.

**Punto a aclarar con el equipo.** La declaración de IA del Avance 4 afirma que se corrigió «la
validación interna de la calibración del SVM no agrupaba (revisión del #118)». `alternativos.py` solo
se tocó en ese PR y sigue sin `cv` agrupado. Puede ser una confusión con `BusquedaAnidada`, que sí
agrupa. Conviene revisarlo porque está en un entregable calificado.

**Señal diagnóstica útil, y toca la lectura de la fase 1.** En la prueba reservada el MCC cae un 52%
(0.702 → 0.338) mientras el AUROC cae un 14% (0.919 → 0.793). Esa asimetría es la firma de un punto
de operación fijo encima de un cambio de distribución, no solo de pérdida de discriminación. Parte de
la caída es recuperable reportando el MCC a un umbral elegido en validación. La conclusión del
cuaderno sigue siendo válida; su magnitud está exagerada por la métrica.

Relacionado: la decisión C.5 (`decisiones.md:107-115`) dice que el punto de operación no se fija,
mientras el MCC y la exactitud balanceada a 0.5 son exactamente un punto de operación fijo y se
reportan como métrica principal.

### 2.2 · El parámetro de dispersión del AFT está en unidades equivocadas

`src/models/aft.py:15-20` justifica el valor por omisión como «comparable a la dispersión
experimental reportada en ChEMBL (σ ≈ 0.7 en pActividad)», con `escala=1.0` (`aft.py:50`). σ vive en
ln(µM): 1.0 son **0.434 en pActividad**, no 0.7. El equivalente sería 1.6118.

El modelo supone las mediciones 1.6 veces más precisas de lo que cita su propia justificación, y σ es
justo el parámetro que gobierna cuánta información lleva un intervalo censurado, que es el mecanismo
en el que descansa la elección del AFT. El equipo ya lo midió en el PR #181: con 1.6118 gana 0.0192
de concordancia en NPASS, en 13 de 15 pliegues.

**El #181 ya está fusionado y no corrigió el docstring.** Todas las cifras publicadas de la 2.13 y
del 05b se produjeron con el valor viejo. Hay que corregir la justificación o decir que las cifras
usan 0.434 y no 0.7.

### 2.3 · El filtro del AFT y su prueba unitaria

`src/models/aft.py:84` exige `inf_um > 0` y con eso descarta 745 de las 56,241 filas de ajuste: 740
de ChEMBL, 5 mixtas, **0 de NPASS**. Son censuras por la izquierda («más potente que c µM»), que
XGBoost admite de forma nativa con cota inferior 0. Su cota inferior mediana es pActividad 7.00 y 726
son activas al corte de 10 µM.

El #181 ya llevó el defecto al registro, que es lo que faltaba. Quedan tres cosas:

- `src/models/aft.py:80-83`: el comentario dice que el filtro «elimina intervalos no informativos»,
  lo cual es falso: elimina además 745 filas informativas, y son las más potentes.
- `tests/test_aft.py:70-87`: la prueba **consagra el criterio equivocado**, tratando esas filas como
  no informativas. Una prueba que afirma que el defecto es el comportamiento correcto es peor que no
  tenerla.
- `scripts/descartadas_aft.py:5-7` dice ser evidencia de algo que la 2.13 ahora sí cita; conviene
  actualizar la referencia.

Impacto en cifras: nulo sobre el argumento de NPASS, marginal sobre la concordancia agregada.

### 2.4 · Un error estándar presentado como dispersión

El 05b escribe que el `bosque` mejora al kNN en «+0.0094 ± 0.0014». La desviación pareada real entre
las 15 evaluaciones es **0.0053**; 0.0014 es esa desviación dividida por la raíz de 15, es decir un
error estándar. Es lo que `cv.resumen` prohíbe en su propio docstring, porque las semillas comparten
filas. El efecto es que la ventaja parece de siete desviaciones cuando es de 1.8, y eso importa
porque el argumento del modelo final descansa en que esa ventaja agregada no basta.

Dos líneas más abajo el mismo párrafo cita «desviación de 0.0015» para el `apilado`, y ahí sí es una
desviación. Dos números con la misma apariencia que son cosas distintas.

Conviene precisar algo a favor del código: **ningún módulo ni celda divide por la raíz del número de
pliegues.** Los únicos errores estándar del repositorio son los corregidos por Nadeau y Bengio. Ese
`±` se escribió a mano en la prosa.

Relacionado y menor: `docs/decisiones.md:829-837` escribe `0.765 ± 0.006` sin decir qué es el `±`, en
el registro canónico, donde un `±` se lee como intervalo. Y `src/evaluation/graficos.py:145,216-217`
dibujan esa desviación como barras de error, que se leen visualmente como precisión.

### 2.5 · Fuga real de selección de características, con magnitud medida en cero

Las 151 columnas de la fase 1 se eligieron una vez usando las etiquetas de la partición de
entrenamiento (`notebooks/02_Feature_Eng.ipynb:1950,1965,2197`), y la validación cruzada corre sobre
entrenamiento más validación (`src/models/tareas.py:92-95`). Cada pliegue de evaluación contiene
filas cuya etiqueta ayudó a decidir qué columnas existen. La prueba reservada no participó.

El propio proyecto ya la midió sin saberlo: el brazo `depurados` del 03c reajusta el filtro dentro de
cada pliegue. Diferencia pareada en 15 evaluaciones: MCC entre −0.014 y +0.010, AUROC entre −0.004 y
+0.002, con el criterio de mejora sin cumplirse en los seis modelos, y en kNN el brazo honesto gana.
Contra una desviación del control de 0.094 de MCC, el sesgo no es medible.

**No hay nada urgente que rehacer.** Lo que sí hay que corregir es el lenguaje: la frase «el brazo
`descriptores` es el control» del 03c y del 05c no es exacta, porque ese control no está libre de
fuga. Un renglón en la decisión 1.3 con esas cifras cierra el tema.

### 2.6 · El registro no recoge el Avance 5 de la fase 1

- La palabra `svm` aparece **cero veces** en `docs/decisiones.md`.
- La decisión 1.5 sigue marcada como propuesta.
- El resultado de la prueba reservada no está en ninguna parte del registro.
- `decisiones.md` §290 sigue fijando la vara del proyecto en «el 0.70 de MCC y el 0.93 de AUROC de
  este baseline», cuando la cifra sobre datos no vistos es **0.3385 de MCC y 0.7928 de AUROC**.

El `CLAUDE.md` pide que el registro cambie en el mismo PR que la decisión. El PR #171 eligió el
modelo final de la fase 1, leyó la prueba reservada y no tocó el registro. Hoy el registro anuncia
0.70 y la cifra honesta es 0.34, que el propio cuaderno ya dice.

---

## Prioridad 3 · Cifras y registro

### 3.1 · Cinco conteos sin corrida detrás, y son el argumento central de la 2.13

`52,529` filas de ChEMBL con `16.6%` censuradas, `2,114` de NPASS con `53.5%`, y las `982` que deja
el filtro de exactas. Están escritos a mano en el markdown del 05b. Ninguna celda los imprime, ningún
`metricas.json` los guarda y ningún script los produce. Son aritméticamente consistentes entre sí y
con los asertos que sí tienen salida guardada, así que casi con seguridad son correctos.

Son el hueco más caro de los cinco porque sostienen la explicación de por qué el AFT gana en
productos naturales, y el proyecto los publica fuera de su propia regla.

### 3.2 · Tres tiempos de la fase 1 pertenecen a una corrida superada

Los 309 s por ajuste del `bosque afinado`, los 4,637 s en total y los 2.4 s del bosque sin afinar son
de `2026-10-29-artemio-1.5-ensambles-permeabilidad`. La corrida que el cuaderno registra e imprime es
la del 1 de noviembre: **340.6 s, 5,109.6 s y 2.49 s**.

Lo revelador es por qué difieren. Las dos corridas tienen el mismo `datos_sha256`, el mismo
`lock_sha256`, la misma máquina y el mismo Python. Todas las métricas salen idénticas y **solo se
mueven los tiempos**, un 10% arriba. La columna `segundos_ajuste` no se repite ni en el mismo
portátil, así que cualquier prosa que la cite tiene que nombrar su corrida.

### 3.3 · Una inconsistencia interna entre dos párrafos seguidos del 05

El texto dice «+0.0093 contra 0.073», que es el valor pareado y es correcto. La tabla de la línea
siguiente pone **+0.0092** para el `stacking`, que es la resta de las medias redondeadas
(0.7109 − 0.7017). Es justo lo que la celda 8 declara que no se hace. Las otras dos filas de esa tabla
sí traen el valor pareado.

### 3.4 · El estimador puntual del intervalo no es el de la tabla

`intervalo_por_grupos` remuestrea grupos y es percentil puro, lo cual es correcto. Pero su cifra
puntual es la métrica sobre las predicciones fuera de pliegue reunidas, mientras la tabla reporta la
media de los valores por pliegue. Son dos estimadores distintos de la misma cantidad, y aquí difieren
lo bastante para cambiar el orden.

Peor: `scripts/experimento_baseline.py:124` promedia **entre semillas** antes de medir, que es un
ensamble de tres corridas y no un modelo. En
`experimentos/2026-10-18-artemio-1.5-baseline-permeabilidad-descriptores/metricas.json` eso da
`boosting 0.9376 > bosque 0.9367`, **el orden de AUROC invertido** respecto a la tabla del cuaderno.
Quien verifique una cifra contra su corrida, que es la regla del proyecto, obtiene el orden contrario.

No invalida ninguna conclusión: el 03 cierra con que los tres se solapan. La celda 11 del 03 advierte
este problema muy bien para otra comparación; entre las celdas 6 y 8 no hay nota.

### 3.5 · Dos cosas de higiene del registro

- La corrida de la fase 1 **no deja `pliegues.csv`** en su carpeta. El «gana 12 de 15» está como
  agregado, pero el detalle que permite recontarlo vive en `notebooks/datos/05_ensambles.csv`, al
  revés de lo que pide `experimentos/README.md`. La fase 2 sí lo hace bien.
- La partición de prueba se ha leído **tres veces**, y la bitácora lo registra bien, que es su
  trabajo. La segunda lectura de la fase 2 es defendible, porque el modelo final ya estaba elegido y
  commiteado. Pero el 05b y el 05 siguen afirmando que se toca «una sola vez», y en la fase 2 eso ya
  no es cierto en la letra. Conviene ajustar la frase.
- `src/models/tareas.py` permite `incluir_prueba=True` sin exigir motivo ni dejar rastro, mientras
  `tomar_prueba` sí lo exige. Hoy nadie abusa de ello, verificado camino por camino, pero es la puerta
  ancha.

### 3.6 · Dos imprecisiones de signo y de método, y una está en el glosario publicado

- El glosario del 05b (celda 22) dice que la base registra «una cota superior de inactividad
  (≤ 10 µM)». En concentración un inactivo a 10 µM es **> 10 µM**; es cota superior en pActividad, no
  en µM. Es precisamente el signo que el proyecto más cuida.
- `scripts/analisis_origen_fase1.py:136,285` calculan el AUPRC de BBB− con `1 - p` en vez de usar
  `orientar_minoritaria`. Es la forma que `cv.py:58-73` documenta como incorrecta; con esos modelos el
  daño es pequeño, pero es la duplicación que el helper existe para evitar.

### 3.7 · Riesgos latentes menores

- `src/models/ensambles.py:137-142` deja el meta-modelo del apilado por omisión, que selecciona su
  regularización por validación dejando uno fuera, sin agrupar. Magnitud despreciable sobre dos
  columnas, pero el docstring del módulo afirma que la partición interna está agrupada y esa excepción
  queda sin declarar.
- `CanalizacionConGrupos.necesita_grupos` solo inspecciona el último paso. Hoy el stacking siempre va
  último, así que no falla, pero un `assert` en el constructor cerraría la invariante.
- `requirements.txt:29` admite `scikit-learn>=1.5`, donde `GroupKFold(shuffle=True, random_state=...)`
  es un `TypeError`. El lock fija 1.9.1 y el CI pasa, pero quien instale por las cotas mínimas puede
  no poder importar el apilado.
- `rmse_entrenamiento` del `aft` se calcula sobre todas las exactas del pliegue, incluidas las 745 que
  nunca vio, así que para ese modelo no es «RMSE sobre lo que entrenó».

---

## Legibilidad de los cuadernos nuevos

Pregunta aparte, medida en los cuatro cuadernos de los Avances 4 y 5.

**Ninguno menciona `CLAUDE.md`.** Cero en los cuatro. Limpio.

**Autocontención.** El 04 no tiene un solo enlace a `docs/`. El 05 tiene 11, el 05c tiene 8 y el 05b
tiene 3. Al leer los contextos, casi todos van glosados en la misma frase («la decisión 1.6: un
promedio de todos no dice cómo le va al modelo con los naturales»), así que el lector no tiene que
salir. La excepción es el 05b, que en el argumento del modelo final dice «el detalle está en la 2.13»
y ahí sí manda fuera.

**Densidad de prosa**, en caracteres por celda markdown:

| cuaderno | media | mediana | celda mayor |
|:--|--:|--:|--:|
| `04_Models` | 956 | 669 | 4,909 |
| `05_Modelo_Final` | 1,619 | 540 | 7,094 |
| `05b_Ensambles_actividad` | **4,122** | 1,157 | **14,909** |
| `05c_Ensambles_permeabilidad_huellas` | 848 | 624 | 2,453 |

El techo que el propio repositorio fija para una diapositiva es 1,761 caracteres
(`scripts/armar_deck.py:43`). El 05b tiene una celda de 14,909, ocho veces ese techo, y promedia
cuatro veces la densidad del 04. El 05c es el más parecido al 04, incluso más apretado.

Y un dato que lo confirma desde el repositorio: `CON_DECK` solo vigila `03_Baseline` y `04_Models`
(`scripts/armar_deck.py:53`). Ninguno de los tres cuadernos nuevos está en la lista, así que nadie
comprueba si se pueden presentar.

**Dos arreglos concretos:** partir las celdas 14 y 22 del 05b, que son las monstruosas, y añadir los
tres cuadernos nuevos a `CON_DECK`.

---

## Lo que está bien hecho y no es obvio

Se registra para que no se vuelva a revisar, y porque es lo que hace creíble al resto.

- `orientar_minoritaria` devuelve `-p` y no `1 - p`, con la identidad
  `roc_auc_score(1-y,-p) == roc_auc_score(y,p)` como prueba. Es un cuidado de punto flotante que casi
  nadie pone.
- `intervalo_por_grupos` remuestrea grupos, y la prueba **demuestra** que el intervalo sale más ancho
  que por filas en vez de solo afirmarlo.
- `grupos_cv`: la unión-búsqueda se verificó a mano. La transitividad funciona y los acíclicos quedan
  fuera de la unión para no fusionarse en un grupo gigante. `verificar_fuga` revisa todas las filas,
  acíclicos incluidos.
- El filtro de correlación corta el recorrido al descartar una columna, evitando el error clásico de
  descartar otras por estar correlacionadas con una que ya no está.
- Las pruebas de agrupamiento comprueban que agrupar **cambia** los pesos del meta-modelo y el
  hiperparámetro elegido, no solo que el código corre.
- La etiqueta binaria se deriva del intervalo y nunca se almacena, con la convención del empate
  razonada explícitamente.
- `decisiones.md:494` (S1.11) conserva visible la conclusión que el error estándar ingenuo sostenía y
  el corregido tumbó. Es el modelo de cómo registrar una corrección.
- Los pisos triviales se calculan dentro del pliegue, y el `raise` de `_dianas` impide que unas
  posiciones equivocadas devuelvan una cifra creíble y falsa.
- La búsqueda de hiperparámetros agrupa en todos sus caminos y en ninguno se elige mirando el pliegue
  de evaluación externo. Se comprobaron las dos vías por las que podría pasar.
- El vocabulario Sort & Slice se reaprende dentro de cada pliegue, no mira la etiqueta y descarta las
  subestructuras de frecuencia cero. La afirmación del 05c sobre que el stacking hereda vocabulario y
  eso toca al meta-modelo pero no a la evaluación externa es correcta tal como está escrita.

---

## Lo que no se pudo verificar

- **Las pruebas no se ejecutaron.** No hay entorno de Python del proyecto ni `pytest` en el contenedor
  donde corrió esta auditoría, así que la afirmación de que pasan 289 de 293 no está comprobada aquí.
  La evidencia disponible es que el CI quedó verde en los PR fusionados.
- **Los cinco conteos de la §3.1** exigirían regenerar `fase2_pares.parquet`: `data/processed/` está
  vacío y el archivo de actividad es un puntero de Git LFS.
- Una cifra confirmada que conviene leer con cuidado: el «85% del techo de enriquecimiento al 1%» en
  productos naturales descansa en 117 pares con 52 activos, así que el 1% es algo más de una molécula.
  La cifra tiene corrida detrás; la conclusión que carga no aguanta ese tamaño.

---

## Orden sugerido de trabajo

Antes del artículo del 8 de noviembre:

1. Reescribir la razón 1 del modelo final de la fase 2 (§1.1), o respaldarla con el MCC a umbral
   elegido en validación.
2. Llevar al 05b el desglose de la prueba por procedencia y resolver la condición que el propio
   cuaderno declaró (§1.2).
3. Registrar qué clase midió el AUPRC, o fijarla por fase, y corregir `decisiones.md:410` (§1.3).
4. Reemplazar el argumento del umbral por el error estándar corregido que ya existe en el repositorio
   (§1.4).
5. Actualizar la decisión 1.5 y la vara del 0.70 en el registro con el resultado de la prueba (§2.6).
6. Agrupar o declarar el `cv` interno de la calibración, y revisar qué se corrigió en el #118 (§2.1).
7. Corregir la justificación de σ y el criterio de `tests/test_aft.py` (§2.2, §2.3).

Lo demás puede ir después del artículo sin coste.

**La lectura de conjunto, en una frase.** La infraestructura es sólida y en varios puntos mejor que
la media de un proyecto de este tamaño; lo que falla es que el texto afirma más de lo que sus números
sostienen, y eso es lo que un revisor externo encuentra primero.
