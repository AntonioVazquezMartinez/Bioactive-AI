# Corridas

Una carpeta por corrida, `experimentos/<id>/`, escrita por `src/tracking.py` y versionada en git
(son archivos de texto de unos kilobytes). Plan completo: `docs/roadmap-mlops.md`.

| Archivo | Contenido |
|:--|:--|
| `params.yaml` | decisión a la que sirve, semillas y parámetros: con esto se repite |
| `metricas.json` | las métricas; nunca registros de los datos (licencias, entrada C.6) |
| `entorno.json` | commit y si el árbol estaba sucio, sistema, Python, versiones, `sha256` del lock y de los datos |
| `comando.txt` | el comando que la lanzó |

El `id` es `AAAA-MM-DD-<autor>-<decisión>-<nombre>`, por ejemplo `2026-10-14-ingrid-1.7-L`. El
autor sale de `BIOACTIVE_AUTOR` o del primer nombre de `git config user.name`. Una corrida no se
sobrescribe, y si el script falla su carpeta se borra: se repite con otra fecha o nombre.

```python
from tracking import Corrida   # los scripts ponen src/ en sys.path

with Corrida("L", decision="1.7", params={"L": 64}, semillas=[0, 1, 2], datos=[ruta]) as c:
    ...
    c.metricas({"MCC": 0.71})
```

Si MLflow está instalado, la corrida también se registra en `mlruns/` (ignorado por git), que es
solo un visor. Una corrida no decide: se compara con validación cruzada agrupada, no con una
partición.
