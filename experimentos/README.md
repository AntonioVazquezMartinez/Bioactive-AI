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

**La partición de prueba solo sale por `tomar_prueba`** (`src/tracking.py`). Exige `final=True` y un
`motivo`, imprime cuántas filas hay por estrato y agrega una línea a `experimentos/prueba.csv`
(fecha, autor, commit, filas, motivo). No impide una segunda lectura, porque a veces hay que
corregir una corrida; la deja a la vista en el `git diff` del PR. Para desarrollo se filtra con
`pares[pares["particion"] != "prueba"]`. Hoy la guarda solo protege a quien la llama: el 04b
todavía filtra a mano, y el primer cuaderno que la usa es el 05b.
