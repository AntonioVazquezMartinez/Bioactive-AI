# Corridas

Una carpeta por corrida, `experimentos/<id>/`, escrita por `src/tracking.py` y versionada en git
(son archivos de texto de unos kilobytes). Plan completo: `docs/roadmap-mlops.md`.

| Archivo | Contenido |
|:--|:--|
| `params.yaml` | decisión a la que sirve, semillas y parámetros: con esto se repite |
| `metricas.json` | las métricas; nunca registros de los datos (licencias, entrada C.6) |
| `entorno.json` | commit y si el árbol estaba sucio, sistema, Python, versiones, `sha256` del lock y de los datos |
| `comando.txt` | el comando que la lanzó |

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

**Commitea cada corrida antes de lanzar la siguiente.** `entorno.json` toma `arbol_sucio` de
`git status --porcelain`, que cuenta los archivos sin seguimiento: una carpeta de `experimentos/`
recién creada ensucia el árbol para la corrida que venga después y la hace registrar
`arbol_sucio: true` sin que nadie haya tocado el código. Al retropoblar las dos mediciones de la
fase 0.8 hubo que intercalar un commit entre las dos para que las dos salieran en `false`.

<<<<<<< HEAD
**La partición de prueba solo sale por `tomar_prueba`** (`src/tracking.py`). Exige `final=True` y un
`motivo`, imprime cuántas filas hay por estrato y agrega una línea a `experimentos/prueba.csv`
(fecha, autor, commit, filas, motivo). No impide una segunda lectura, porque a veces hay que
corregir una corrida; la deja a la vista en el `git diff` del PR. Para desarrollo se filtra con
`pares[pares["particion"] != "prueba"]`. Hoy la guarda solo protege a quien la llama: el 04b
todavía filtra a mano, y el primer cuaderno que la usa es el 05b.
=======
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
>>>>>>> main
