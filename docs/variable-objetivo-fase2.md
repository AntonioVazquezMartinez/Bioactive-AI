# Las variables objetivo de las dos fases

**Estado:** vigente. Es la versión larga de las decisiones [2.3](decisiones.md#d2-3), [2.9](decisiones.md#d2-9), [2.10](decisiones.md#d2-10) y [2.11](decisiones.md#d2-11) para la fase 2, y de la [1.1](decisiones.md#d1-1) para la fase 1.

## En una tabla

| | Fase 1 · Permeabilidad | Fase 2 · Actividad |
|:--|:--|:--|
| **Pregunta** | ¿el compuesto cruza la barrera hematoencefálica? | ¿qué tan potente es el compuesto sobre esta diana? |
| **Unidad** | el compuesto (un SMILES) | el **par** esqueleto de conectividad × diana |
| **Variable objetivo** | la clase BBB+ o BBB− | la **potencia**, `pActividad` (regresión con censura) |
| **Clase derivada** | — | activo o inactivo, aplicando un corte a la potencia predicha |
| **Métricas** | MCC y AUPRC de la clase minoritaria | concordancia de Harrell, Spearman y RMSE sobre las exactas |

La diferencia de fondo: en la fase 1 la etiqueta viene dada y se predice como clase; en la fase 2 **no existe una columna «activo»**, existen mediciones de concentración, y lo que se predice es la concentración.

## Fase 1 · La clase de permeabilidad

La variable es `BBB+` o `BBB−`, del archivo curado de permeabilidad: 7,811 filas, 7,805 con clase. Cuando el compuesto trae un logBB medido, la clase sale del umbral −1.0 (logBB ≥ −1.0 es BBB+). Seis filas traen logBB sin clase ([1.4](decisiones.md#d1-4)). Hay 1.74 positivos por negativo, así que predecir siempre BBB+ acierta el 63.5% sin aprender nada: por eso se reporta MCC y AUPRC de la clase minoritaria ([C.1](decisiones.md#dc-1)). La columna de grupo A–D no se usa para filtrar ([1.1](decisiones.md#d1-1)).

## Fase 2 · La potencia de un par compuesto-diana

### 1. Qué es una fila del archivo

Una medición: un compuesto contra una proteína, con tipo de medida (`IC50`, `Ki`, `EC50`…), relación (`=`, `>`, `<`), valor y unidad. Dos ejemplos: «Ki = 50 nM» y «IC50 > 10 µM». La primera da la concentración exacta; la segunda solo dice que, hasta 10 µM, no se vio el efecto.

### 2. De la concentración a la potencia

Todo se pasa a µM (nM × 0.001, µM × 1). Las filas en unidades de masa (`ug/mL`) quedan fuera: sin el peso molecular no hay conversión a molar. La potencia es

> **pActividad = 6 − log₁₀(concentración en µM)**

Ejemplos: 10 µM da 5; 1 µM da 6; 0.1 µM da 7. Es solo la concentración en escala logarítmica y con el sentido invertido (más potente, número mayor): no agrega información ni ruido, y en ChEMBL coincide con el pChEMBL (sobre 72,955 filas que traen los dos, la diferencia tiene mediana 0.0021). Se usa porque las concentraciones abarcan doce órdenes de magnitud. Se recorta a [2, 12], el rango del pChEMBL observado.

La relación de cada fila decide qué dice del valor:

| Relación | Qué dice la medición |
|:--|:--|
| `=` o `~` | la concentración, exacta |
| `>` | la concentración es **mayor** que el límite (potencia menor que 6 − log₁₀ límite) |
| `<` | la concentración es **menor** que el límite |

### 3. Qué entra como evidencia

- **Las tres fuentes** (ChEMBL, NPASS, CMAUP), con las columnas `_used` del diccionario, que vienen informadas y homogéneas ([2.3](decisiones.md#d2-3)). Las 2,001 relaciones inferidas entran marcadas.
- **La afinidad cuenta** (`Ki`, `Kd`, IC50 de unión) y ninguna medición se invierte ([2.11](decisiones.md#d2-11)). Ejemplo: un IC50 sobre `PPARG` (diana donde se busca activar) puede venir de un ensayo de unión, que mide cuánto se une, o de uno funcional de inhibición, que va en sentido contrario. Cada medición lleva una marca `direccion_consistente` (consistente, ambigua o contradictoria) y la sensibilidad se repite solo con las consistentes. `Potency` y `AC50` son potencia sin dirección.
- **Fuera:** los inactivos declarados por texto (el panel DrugMatrix, [2.12](decisiones.md#d2-12)) y las 88,098 mediciones sobre proteínas fuera de la lista de dianas ([2.4](decisiones.md#d2-4)).

### 4. Del conjunto de mediciones al par

La llave del par es **esqueleto de conectividad × gen**, no el identificador del compuesto, porque cada fuente numera los suyos y no comparten ninguno ([2.10](decisiones.md#d2-10)). De cada par se guarda el **intervalo** donde cae la potencia, no una etiqueta:

| Columna | Qué es |
|:--|:--|
| `pActividad` | la mediana de las mediciones exactas; vacío si solo hay cotas |
| `limite_inferior`, `limite_superior` | el intervalo, con ±∞ donde no hay cota |
| `n_mediciones`, `n_exactas`, `rango_exactas` | cuántas hay y cuánto se separan |
| `conflicto` | las mediciones son incompatibles entre sí |

Dos ejemplos. Un par con Ki = 50 nM (pActividad 7.30) y IC50 = 120 nM (6.92) tiene mediana 7.11 y rango 0.38: es consistente. Si además trae un `> 10 µM` de otro ensayo, que exige potencia menor que 5, la mediana cae fuera de lo que permite esa cota y el par se marca en **conflicto**. Un par con 0.01 µM y 5 µM tiene rango 2.7, más de dos unidades logarítmicas (cien veces), y se marca como de **dispersión alta**.

La mediana, y no la medición más potente, porque el máximo sesga hacia los activos. El filtro de dirección se aplica antes de agregar.

### 5. Cómo se ajusta la regresión

El modelo aprende la potencia con los censurados como cotas, no como valores ni como datos faltantes. Un `> 10 µM` es, en concentración, censura **por la derecha** (el valor real es mayor que 10) y, en pActividad, por la izquierda (menor que 5): lo que importa es que el intervalo quede del lado correcto. El modelo lineal con censura (Tobit) lo usa en pActividad; un ajuste en concentración, como el de los árboles con `survival:aft`, necesita convertir a µM y volver al final. Excluir los censurados perdería el 49.4% de los negativos ([2.9](decisiones.md#d2-9)).

### 6. La clase derivada

La clase sale de aplicar un corte a la potencia predicha: **10 µM** (pActividad ≥ 5) como principal y **1 µM** (≥ 6) como sensibilidad, siempre juntos. El corte no se estima: no hay columna de desenlace que lo calibre. Los 10 µM vienen de que el 67.4% de las mediciones censuradas lo están exactamente ahí, la concentración a la que esos ensayos dejaron de mirar.

Ejemplo de por qué no es el objetivo: con 10 µM, un compuesto de 0.05 µM y otro de 9 µM son ambos «activos», aunque difieren 180 veces. Y el mismo corte exige distinto según la diana: con 10 µM, `LRRK2` queda en 98.1% de activos y `NFE2L2` en 50.7%.

Para derivar la clase de un par, un `> L` solo cuenta como inactivo si su límite es igual o mayor que el corte; con `> 1 µM` y corte de 10 µM no se sabe nada. Una exacta justo en el corte es activa.

### 7. Cómo se evalúa

- **Concordancia de Harrell:** de los pares de mediciones cuyo orden se conoce, qué fracción ordena bien el modelo. Tolera la censura.
- **Spearman y RMSE**, solo sobre las mediciones exactas, declarado así.
- **Un techo:** repetir el mismo ensayo da diferencias de unas 0.7 unidades logarítmicas en IC50 y 0.5 en Ki (fuente por citar), y el 25.5% de los pares con dos o más exactas discrepa más de una unidad. Un RMSE muy por debajo no es un buen resultado, es una señal de fuga.
- **Siempre por procedencia** (solo ChEMBL, mixtos, solo NPASS): el modelo separa mucho peor los pares que solo tiene NPASS ([2.5](decisiones.md#d2-5)).
- Las métricas de ranking (enriquecimiento, precisión en los primeros 100) están en la [C.5](decisiones.md#dc-5).

### 8. Cómo se acotan los problemas

La variabilidad entre ensayos no se resuelve con los datos que hay; se acota repitiendo el análisis bajo variantes (corte de 10 µM, cinco categorías). Cifras de `scripts/cifras_etiqueta_fase2.py` (pares con etiqueta binaria, no con potencia):

| Variante | Pares con etiqueta | Activos |
|:--|--:|--:|
| **Definición principal** (tres fuentes, sin inactivos por texto, sin conflictos) | 66,121 | 72.6% |
| Conflictos como activos | 67,905 | 73.3% |
| Con los inactivos por texto | 68,265 | 70.3% |
| Sin las 2,001 relaciones inferidas | 65,368 | 73.2% |
| Solo IC50 | 45,050 | 71.0% |
| Solo Ki | 15,418 | 86.8% |
| Solo ChEMBL | 63,796 | 74.8% |

Si el resultado no cambia entre variantes, el modelo no depende de esas diferencias; si cambia, se reporta cuánto. Problemas que no se pueden quitar y se declaran:

1. **La fuente y la potencia están correlacionadas.** El porcentaje de activos va de 74.8% (ChEMBL) a 22.9% (NPASS). Un modelo podría acertar con «viene de NPASS, entonces débil». La fuente, el tipo de ensayo, el tejido y el artículo **no entran como entrada del modelo**; un control de atajo que solo ve la procedencia mide cuánta señal llevan ([2.5](decisiones.md#d2-5)).
2. **El contexto del ensayo falta justo donde se modela.** Solo 286 de los 70,384 pares (0.4%) traen tejido, porque la anotación existe en una ruta del archivo y las dianas de la lista entran por otra ([2.3](decisiones.md#d2-3)). Sirve para auditar los pares en conflicto, no como variable.
3. **Quitar los conflictos no es neutro:** se pierde el 11.8% de los pares con varias mediciones, más en NPASS y CMAUP, y el conjunto que queda es más consistente que representativo.
4. **Medidas distintas en una columna:** `activity_type` tiene 41 tipos; `Potency` pesa en NPASS (2,427 filas) y CMAUP (775) y casi nada en ChEMBL.
5. **El corte cae donde la medición es menos fiable:** el 20.7% de las exactas queda a menos de 0.5 unidades logarítmicas de 10 µM.
6. **Filas marcadas por ChEMBL** («Outside typical range», 5,287 filas, 2.6%): se mantienen y se repite el análisis sin ellas.
7. **Por artículo disjunto no es viable:** un solo componente conectado reúne el 55.9% de los pares; se reporta el desempeño por referencia.

### 9. Cifras y cómo se calcularon

Las cifras salen del archivo recibido (202,647 filas; el diccionario describe 225,513 del archivo completo), restringido a las cinco categorías, con `target_gene` y estructura calculable: 70,384 pares sobre 59,532 compuestos y 26 dianas; 57,832 con potencia y 12,552 solo con cotas. Los reproducen `scripts/cifras_fase2.py`, `scripts/cifras_etiqueta_fase2.py` y `scripts/cifras_contexto_ensayo.py`; porcentajes por registro y por par se declaran como tales.
