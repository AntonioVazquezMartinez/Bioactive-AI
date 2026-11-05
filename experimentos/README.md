# Corridas

Una carpeta por corrida, `experimentos/<id>/`, escrita por `src/tracking.py` y versionada en git
(son archivos de texto de unos kilobytes). Plan completo: `docs/roadmap-mlops.md`.

| Archivo | Contenido |
|:--|:--|
| `params.yaml` | decisión a la que sirve, semillas y parámetros: con esto se repite |
| `metricas.json` | las métricas; nunca registros de los datos (licencias, entrada C.6) |
| `entorno.json` | commit y si el árbol estaba sucio, sistema, Python, versiones, `sha256` del lock y de los datos |
| `comando.txt` | el comando que la lanzó |
| `pliegues.csv` | opcional: una fila por modelo, semilla, pliegue y estrato, cuando la decisión se apoya en conteos y no solo en medias |

El `id` es `AAAA-MM-DD-<autor>-<decisión>-<nombre>`, por ejemplo `2026-10-14-ingrid-1.7-L`. La fecha del `id` es la local de quien corre (el commit que registra puede caer en otro día en UTC). El
autor sale de `BIOACTIVE_AUTOR` o del primer nombre de `git config user.name`. Una corrida no se
sobrescribe, el entorno (commit y árbol sucio) se captura al empezar, antes de que el script escriba su propio producto, y si el script falla su carpeta se borra: se repite con otra fecha o nombre.

```python
from tracking import Corrida   # los scripts ponen src/ en sys.path

with Corrida("L", decision="1.7", params={"L": 64}, semillas=[0, 1, 2], datos=[ruta]) as c:
    ...
    c.metricas({"MCC": 0.71})
```

Si MLflow está instalado, la corrida también se registra en `mlruns/` (ignorado por git), que es
solo un visor. Una corrida no decide: se compara con validación cruzada agrupada, no con una
partición.

**`pliegues.csv` existe porque un agregado no deja verificar un conteo.** `metricas.json` guarda
medias y desviaciones, y con eso no se puede comprobar una afirmación del tipo «gana en 15 de los
15 pliegues», que es sobre la que descansa la elección del modelo final de la
[2.13](../docs/decisiones.md#d2-13). La primera que lo trae es
`2026-10-31-antonio-2.13-comparativa-regresion-ensambles`, con una fila por modelo, semilla,
pliegue y estrato. No lo escribe `Corrida`, lo deja el cuaderno al ir anotando sus parciales, y se
copia a la carpeta al cerrar. Son decenas de kilobytes, así que solo vale la pena cuando el
argumento es un conteo.

**Commitea cada corrida antes de lanzar la siguiente.** `entorno.json` toma `arbol_sucio` de
`git status --porcelain`, que cuenta los archivos sin seguimiento: una carpeta de `experimentos/`
recién creada ensucia el árbol para la corrida que venga después y la hace registrar
`arbol_sucio: true` sin que nadie haya tocado el código. Al retropoblar las dos mediciones de la
fase 0.8 hubo que intercalar un commit entre las dos para que las dos salieran en `false`.

**La partición de prueba solo sale por `tomar_prueba`** (`src/tracking.py`). Exige `final=True` y un
`motivo`, imprime cuántas filas hay por estrato y agrega una línea a `experimentos/prueba.csv`
(fecha, autor, commit, filas, motivo). No impide una segunda lectura, porque a veces hay que
corregir una corrida; la deja a la vista en el `git diff` del PR. Para desarrollo se filtra con
`pares[pares["particion"] != "prueba"]`. Hoy la guarda solo protege a quien la llama: el 04b
todavía filtra a mano, y el primer cuaderno que la usa es el 05b.

**Y la bitácora cae en el aviso de arriba, así que el orden importa:** `prueba.csv` no está
versionado hasta que alguien lo escriba, así que la primera llamada a `tomar_prueba` ensucia el
árbol. Llamarla **dentro** del `with Corrida(...)` está bien, porque el entorno se captura al
entrar al contexto; llamarla antes hace que la corrida registre `arbol_sucio: true` sin que nadie
haya tocado el código. No se arregla ignorando el archivo: que una reejecución cante en el
`git diff` es justamente para lo que la bitácora existe.

**Qué se puede reparar y qué no, porque no es lo mismo una carpeta de corrida que una bitácora.**
`experimentos/<id>/` es el registro de lo que una corrida produjo y **no se reescribe**: si
`params.yaml` dice algo, eso es lo que la corrida escribió, y corregirlo haría que el registro
afirmara algo que no pasó. Cuando ese contenido está mal, la corrección va en el registro de
decisiones citando la corrida, no en la carpeta. `experimentos/prueba.csv` es otra cosa: es una
bitácora del proyecto, se agrega línea por línea y la lee una persona. Ahí sí se repara lo que no
es un hecho de la corrida —un acento perdido en el `motivo`— y nunca una fecha, un commit, un
conteo, ni un motivo distinto del que se dio.

El caso que obligó a escribir la regla: la corrida del 05b se lanzó con el código sin acentos, así
que dejó un `?` literal en los dos sitios. En `prueba.csv` se restauró el texto; en `params.yaml`
el `nota_seg` sigue diciendo `diecis?is n?cleos`, y lo que esa nota afirma de más —describe la
columna `seg` como tiempo de reloj, y no lo es— queda corregido en la
[2.13](../docs/decisiones.md#d2-13). Arreglar uno y no el otro parece incoherente hasta que la
regla está dicha, y de hecho lo pareció en revisión: la carpeta se queda como quedó, la bitácora
se lee.

## El AUPRC de la minoritaria de antes del arreglo de `orientar_minoritaria`

Hasta `fix/auprc-minoritaria`, el AUPRC de la clase minoritaria se medía puntuando con `1 - p`,
que pierde resolución cuando el modelo satura. Afecta solo a las corridas que cumplan las tres
condiciones a la vez: que la métrica salga de `orientar_minoritaria`, que la minoritaria sea la
clase 0 (la función solo voltea si `y.mean() > 0.5`) y que el modelo sature sus probabilidades.
Del catálogo, el único que satura así es `GaussianNB`. Ninguna cifra de AUROC está afectada: el
AUROC de la tabla se calcula con `p` sin voltear y no pasa por esa función.

De las corridas registradas, las que cumplen las tres son las cuatro que incluyen `bayes`. Qué
pasa en cada fase se midió, no se supuso:

| Fase | AUPRC de `bayes` con la resta | Negando | Diferencia |
|:--|--:|--:|--:|
| 1 (permeabilidad) | 0.697 | 0.801 | **+0.104** |
| 2 (actividad) | 0.3995 | 0.3993 | −0.0002 |

**En la fase 1 la cifra sí estaba mal y ya está corregida.** El 03c se reejecutó con el arreglo y
da 0.801, que es además el valor que `2026-10-24-antonio-1.5-comparativa-6-modelos-fase-1` y la
tabla de `04_Models.ipynb` ya publicaban: esas dos no hay que tocarlas.

**En la fase 2 no hace falta corregir nada.** Las dos corridas `2026-10-2{4,5}-antonio-2.3-…`
registran 0.399, y medido de las dos formas sale 0.3995 y 0.3993: la diferencia es dos órdenes de
magnitud menor que el redondeo a tres decimales con el que se guarda el registro. La razón de que
allá no muerda es que el orden es débil (AUROC 0.629): el empate que la resta provoca en la cima
se lleva 948 de 10,874 filas de una lista que ya estaba mezclada arriba, así que aplanarla no
cuesta casi nada. En la fase 1 el orden es fuerte (AUROC 0.857) y la cima es justo donde se decide
el AUPRC, con 504 de 1,260 filas empatadas y 154 de ellas de la clase mayoritaria.

La comprobación de la fase 2 se hizo ajustando solo `GaussianNB` sobre la misma matriz y los
mismos pliegues, no reejecutando las dos comparativas de seis modelos: la pregunta era únicamente
cómo se distribuye su `p`, y los otros cinco modelos no pasan por el camino afectado. Se midió en
macOS con la matriz de esta máquina, que es la salvedad del #166; que el 0.399 registrado coincida
con las dos formas de medir aquí es la razón para no pedir una reejecución en la máquina original.

## Cómo repetir las corridas del 3 de noviembre

Todas se lanzan desde la raíz con el intérprete del lock (`env312/bin/python`, Python 3.12) y
registran su carpeta solas. **Commitea el script antes de lanzarlo**: `entorno.json` anota si el
árbol estaba sucio. Los tiempos son de macOS arm64 con 16 núcleos y salen de `duracion_s` de cada
`entorno.json`; en otro sistema las cifras pueden cambiar en el tercer decimal (#166).

| corrida | script | tiempo | datos que necesita |
|:--|:--|--:|:--|
| `…-1.2-escalera-agrupacion-permeabilidad` | `scripts/experimento_agrupacion.py` | 227 s | fase 1 |
| `…-1.2-escalera-ampliada-permeabilidad` | `scripts/experimento_escalera_ampliada.py` | 480 s | fase 1; **una lectura estructural de la prueba** (solo SMILES) |
| `…-C.5-ranking-fase2-aft` | `scripts/experimento_ranking_fase2.py` | 25 s | fase 2 |
| `…-1.3-tamano-huellas-permeabilidad` | `scripts/experimento_tamano_fase1.py` | 431 s | fase 1 |
| `…-1.3-tamano-huellas-actividad` | `scripts/experimento_tamano_fase2.py` | 159 s | fase 2 |
| `…-1.5-curva-aprendizaje-modelos-finales` | `scripts/experimento_curva_aprendizaje.py` | 217 s | fases 1 y 2 |
| `…-1.5-prueba-por-rareza` | `scripts/experimento_prueba_rareza.py` | 118 s | fases 1 y 2; **dos lecturas de la prueba** |

Todas son `2026-11-03-artemio-…`. Cada script trae en su encabezado el diseño, **la regla de
lectura declarada antes de correr** y el comando, y cada resultado tiene su entrada en
[`docs/decisiones.md`](../docs/decisiones.md).

**Los datos de `data/processed/` no están en git y hay que generarlos con el mismo intérprete.**
Para la fase 1 salen del cuaderno 02; para la fase 2, del 02b
(`fase2_pares.parquet` y `fase2_descriptores_limpios.parquet`). Una corrida que use un archivo
distinto lo delata: `entorno.json` guarda el `sha256` de cada uno. Los de estas siete corridas
son:

| archivo | `sha256` |
|:--|:--|
| `bbb_meta.parquet` | `d4e96e57520cf0b8984ff80f4df568427c1f89bc4545abc5d728f7f3afe56727` |
| `bbb_descriptores_filtrados_sin_normalizar.parquet` | `7907c916d3bb6e90f61283e1097b9e1e9a408a0df65e53e90ea3d866bebc4a1a` |
| `fase2_pares.parquet` | `177773855b1c16be6c4ad2d4358dbb9d879eea2584412152b98b17eccf90bc5a` |
| `fase2_descriptores_limpios.parquet` | `7491515858cad9a3d30b321c04d07906065aca21b820b78411674d850d499d1f` |

**Qué se puede comprobar al repetir.** El reajuste de la fase 1 en `…-prueba-por-rareza`
reproduce el AUROC registrado de la prueba (0.7928). El de la fase 2 da 0.7234 de concordancia
contra 0.7200 registrada, y 0.511 contra 0.530 en `solo_npass`: la diferencia es del orden del
ruido de un modelo de árboles y se reporta en la [1.5](../docs/decisiones.md#d1-5), no se
oculta. Quien repita y obtenga algo distinto de esto debe decirlo en el PR antes de interpretar.

**Lectura de la prueba reservada.** Cada corrida que la toca llama a `tomar_prueba` con su
motivo, y `prueba.csv` lo acumula. No se escriben predicciones a git.
