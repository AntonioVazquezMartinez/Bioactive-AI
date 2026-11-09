# Cómo medir una representación nueva

Esta guía es para quien trae **una tabla de columnas por compuesto** —ómicas, propiedades calculadas con otro programa, un descriptor propio— y quiere saber si **predicen mejor que lo que ya tenemos**. Sirve con la misma vara que usa el proyecto: los mismos compuestos, los mismos grupos y los mismos pliegues, de modo que la diferencia que se ve es de la representación y no del azar de la partición.

Es una de las dos cosas que el proyecto deja como método, además de los modelos: **qué columnas ayudan** se contesta con esta herramienta, y **cómo agrupar y medir sin engañarse** es lo que sigue en la segunda mitad.

## En cinco líneas

```python
from src.models import cargar
from src.models.baseline import canalizaciones
from src.models.representaciones import columnas_al_azar, comparar, con_tabla

base = cargar("permeabilidad", representacion="descriptores")        # la referencia
mia = con_tabla(base, mi_tabla, nombre="mi_tabla")                    # mi_tabla: una columna `smiles` + numéricas
ruido = columnas_al_azar(base, mia.X.shape[1])                        # el control
resumen, _ = comparar({"descriptores": base, "mi_tabla": mia, "ruido": ruido},
                      canalizaciones(), referencia="descriptores")
```

`scripts/ejemplo_representacion_propia.py` lo corre de punta a punta con una tabla que calcula él mismo. El código vive en `src/models/representaciones.py` y no obliga a editar nada de `src/`.

## Qué hace cada pieza

| pieza | qué hace | qué no hace |
|:--|:--|:--|
| `con_tabla` | une tu tabla a los compuestos de la tarea por SMILES (los canoniza con RDKit en los dos lados). `modo="reemplaza"` mide tus columnas solas; `modo="agrega"` las pega a los descriptores para ver si **añaden** | **no imputa**: si falta un compuesto o hay un valor no finito, falla diciendo cuántos |
| `columnas_al_azar` | el control: la misma tarea con ruido del mismo ancho que tu tabla | |
| `comparar` | evalúa cada representación con validación cruzada agrupada (3 semillas × 5 pliegues = 15 evaluaciones) y compara **cada una contra la referencia, pliegue a pliegue** | no entrena nada que no sea la canalización que le pases |

La tabla de salida trae, por modelo, estrato y métrica, la **diferencia media contra la referencia**, su **intervalo de Nadeau y Bengio**, en cuántas de las 15 evaluaciones mejora y si el intervalo excluye el cero (`distingue`).

## Lo que la herramienta no puede saber, y es lo primero

**Si tus columnas se calcularon mirando las etiquetas, o todas las filas a la vez, el resultado vale menos de lo que parece.** Un escalado, una selección de columnas, una reducción de dimensión o una imputación ajustados sobre el conjunto completo filtran al pliegue de evaluación lo que aprendieron de él. Esto es lo que más pesa y es lo único que ninguna prueba detecta desde fuera. Dos formas de evitarlo: entregar las columnas **crudas**, y dejar que la canalización de `comparar` las escale dentro del pliegue; o, si la transformación es parte de tu método, que se ajuste dentro de la canalización y no antes.

## Los gotchas de agrupar

1. **Nunca partas al azar.** Una partición aleatoria deja análogos casi idénticos a los dos lados y **infla los resultados entre 7 y 13 puntos** ([decisión 1.2](decisiones.md#d1-2)). **Cuánto depende del modelo y de la métrica, así que no supongas que tu caso cae en ese rango:** con el `svm_rbf` que se entrega, pasar de pliegues al azar a `grupos_cv` cuesta 5 puntos de MCC (0.752 → 0.702), y lo que de verdad hunde la cifra es el peldaño estricto —0.419 cuando ningún compuesto de entrenamiento puede parecerse más de 0.4 a uno de validación—, 33 puntos en total. Con el bosque la inflación de agrupar solo por andamio es de 2.2 de AUROC y 7.1 de MCC, y con el mismo `svm_rbf` de 1.3 y 1.9.
2. **Agrupa por andamio *y* por esqueleto de conectividad, no por andamio solo.** Un mismo esqueleto puede aparecer con andamios distintos, y separarlos pone estereoisómeros del mismo compuesto a los dos lados del pliegue. Con andamio solo son 2,239 grupos; con ambos, 1,048. `cargar` ya te da `grupos_cv`; si armas tu propia tarea, usa `src.data_prep.splits.grupos_cv`.
3. **Una cifra que no dice cómo agrupó no se puede comparar.** Cuando cites un resultado, di con qué criterio se agrupó.
4. **Separar por fuente o por artículo no funciona** ([decisión 2.7](decisiones.md#d2-7)): la fuente no es un atributo del par, y un solo componente conexo de artículos contiene el 55.9% de los pares.
5. **Si tu tabla trae dos filas por compuesto con valores distintos, `con_tabla` falla.** Promedia o escoge antes: no hay forma honesta de elegir en su lugar.

## Los gotchas de medir

1. **Una corrida no decide nada.** La misma regresión logística da 0.481, 0.489 o 0.497 de MCC según el sistema operativo y la versión de Python. Se decide con las 15 evaluaciones y su intervalo, no con un número.
2. **Las 15 evaluaciones no son 15 réplicas independientes**: las semillas comparten las mismas filas. La desviación estándar de `resumen()` sirve para ver dispersión, no para decidir. Por eso `comparar` usa el intervalo de Nadeau y Bengio ([error estándar corregido](glosario.md)), que suma `n_prueba / n_ajuste` dentro de la raíz y es bastante más ancho que el ingenuo.
3. **«Mejora en 12 de 15» no es un resultado por sí solo.** En el experimento de tamaño de la molécula (decisión 1.3), la **condición de recuento** «positivo en 10 de 15 o más» tenía solo 49% de potencia en el umbral que la regla nombraba, y bajo el nulo la regla dictaminaba «se aplana» en ~85% de los casos: el veredicto que salió era el que el ruido produce por defecto. Mira siempre el intervalo y no solo el conteo, y fija el umbral contra la dispersión de la intervención y no contra la del nulo.
4. **Compara siempre contra el ruido.** Una representación que no se distingue de columnas aleatorias del mismo ancho no aporta nada. Una que mejora al ruido pero no a los descriptores aporta, pero no más que lo que ya había.
5. **Reporta por subgrupo, no solo el agregado.** Un modelo que solo ve de dónde viene el compuesto ya alcanza el 65% del MCC de la química, y en los pares que solo tiene NPASS el AUROC cae de 0.83 a 0.57 ([decisión 2.3](decisiones.md#d2-3)). `comparar` devuelve una fila por estrato, y una representación puede ayudar en un estrato y perjudicar en otro: las huellas mejoran a cinco de seis modelos en la fase 2 y a ninguno en la fase 1, y la ganancia se concentra donde el proyecto no la necesita ([decisión 1.3](decisiones.md#d1-3)).
6. **Cuál métrica ordena es una decisión del equipo** ([C.1](decisiones.md#dc-1)): MCC y AUPRC de la clase minoritaria, con el AUROC al lado, que no depende de la prevalencia.
7. **La prueba reservada no se toca.** `cargar` la deja fuera por omisión; leerla está registrado en `experimentos/prueba.csv` y cada lectura gasta lo que la hace una estimación honesta ([1.2](decisiones.md#d1-2)).
8. **El corte de «activo» es otra decisión.** En la fase 2 la etiqueta sale de un intervalo de potencia con corte en 10 µM (1 µM como análisis de sensibilidad); cambiarlo es `cargar("actividad", umbral_um=1.0)` y no rehace nada ([2.3](decisiones.md#d2-3), [2.10](decisiones.md#d2-10)).

## Un ejemplo con números

Las tres propiedades de los filtros de la literatura de permeabilidad —TPSA, donadores de hidrógeno y peso—, calculadas con RDKit, contra los 151 descriptores del proyecto, en la fase 1, con regresión logística y las 15 evaluaciones. Corrida `2026-11-08-ingrid-1.3-ejemplo-representacion-propia` (`scripts/ejemplo_representacion_propia.py`), sin tocar la prueba reservada:

| representación | métrica | diferencia contra los descriptores | IC95% de Nadeau y Bengio | mejora en |
|:--|:--|--:|:--|--:|
| TPSA + donadores + peso (3 columnas) | MCC | −0.0826 | [−0.1312, −0.0340] | 1 de 15 |
| | AUROC | −0.0618 | [−0.0979, −0.0256] | 0 de 15 |
| ruido, 3 columnas | MCC | −0.6870 | [−0.7667, −0.6073] | 0 de 15 |
| | AUROC | −0.4031 | [−0.4390, −0.3671] | 0 de 15 |

Se lee así: tres propiedades bien elegidas se quedan **8 puntos de MCC por debajo** de los 151 descriptores, con el intervalo lejos del cero, mientras que el control de ruido cae a un MCC cercano a cero (0.70 menos 0.69). La representación pequeña **sí aprende** —0.62 contra 0.01 del ruido—; solo que no iguala a la grande. La regresión logística es el modelo más simple; con otro, las cifras cambian, y por eso `comparar` acepta varias canalizaciones.

**Y el ejemplo no es arbitrario: es una réplica de un hallazgo del propio proyecto.** Esas tres columnas son los filtros con que la literatura de permeabilidad descarta compuestos, y la fase 1 ya había medido por su cuenta que **TPSA no domina** (puesto 40 por permutación y 10 por SHAP sobre el `svm_rbf` entregado) mientras los **donadores sí entran** (puesto 4). Que las tres juntas se queden 8 puntos por debajo es coherente con eso: la regla de la literatura captura parte de la señal y no la mayor parte.

**Esta cifra pasa su propio *gotcha* 1.** Se midió en Linux con `requirements.lock` y Python 3.12, y la primera medición, hecha en macOS, dio las mismas cifras a cuatro decimales; por eso la corrida queda registrada con su `sha256`, su commit y sus versiones, y no como un número en prosa.

## Lo que esta herramienta no es

- **No es un servicio ni una interfaz.** Es Python, y hay que reproducir el entorno (`requirements.lock`, Python 3.12). Lo que se entrega a la patrocinadora para usar los modelos con SMILES nuevos sigue siendo `notebooks/06_Uso_de_los_modelos.ipynb`.
- **Mide clasificación.** La fase 2 como regresión de supervivencia (`aft`) no pasa por `comparar`; su experimento de huellas está en `scripts/experimento_aft_huellas.py`.
- **`data/processed/` no está en el repositorio**: se regenera con los scripts de `src/data_prep/` y `scripts/` (ver `docs/recorrido-del-dato.md`) antes de poder correr nada.
- **No sustituye la lectura del registro.** Antes de concluir que una representación no sirve, mira si ya está medida en [`decisiones.md`](decisiones.md) (entrada 1.3 para huellas, descriptores y sus tamaños).
