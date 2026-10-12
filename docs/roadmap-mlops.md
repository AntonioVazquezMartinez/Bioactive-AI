# Roadmap de MLOps

Plan de trabajo para dotar al proyecto de seguimiento de experimentos y reproducibilidad. **Es un documento interno: no se publica en el sitio** (no está en `DOCUMENTOS` de `scripts/prepare_site.py` ni en el navbar) y está pensado para que otra sesión de trabajo lo retome sin más contexto. Fecha de redacción: 11 de octubre de 2026.

## Cómo retomar

1. Leer `CLAUDE.md` y la página de decisiones (`docs/decisiones.md`): el trabajo de MLOps tiene que servir a lo que ahí se decide, no al revés.
2. Entorno: `uv venv --python 3.12 env && source env/bin/activate && uv pip install -r requirements.lock`.
3. Comprobar que todo corre antes de tocar nada: `python3 scripts/prepare_site.py && quarto render && python3 scripts/verificar_sitio.py && python3 scripts/verificar_decisiones.py`.
4. El ejemplo a imitar es `scripts/experimento_L_sortslice.py`: un script, validación cruzada agrupada, resultados en un CSV versionado (`notebooks/datos/`) y un notebook que solo los lee.
5. Trabajar en una rama y una copia aparte (`git worktree`) si hay otra sesión usando la misma carpeta.

## Objetivo

Que cada resultado del proyecto se pueda **repetir, comparar y rastrear hasta la decisión que lo motivó**, con el mínimo de herramientas que un equipo de tres personas pueda mantener. La regla de fondo es la que ya rige el proyecto: *una corrida no decide* (ver la entrada 1.7 y la §8.2 del notebook 02, donde el mismo código dio cifras distintas en macOS y en Linux).

## Punto de partida

| Qué | Hoy | Falta |
|:--|:--|:--|
| Entorno | `requirements.lock` con Python 3.12; la primera celda del notebook 02 imprime las versiones | Nada garantiza el mismo sistema operativo: la regresión logística con min–max difiere ~0.016 de MCC entre macOS y Linux |
| Seguimiento de experimentos | Un script y un CSV (`experimento_L_sortslice.py`); cifras sueltas en notebooks | Convención común, identificador de corrida, registro de parámetros, semillas, versión del código y de los datos |
| Datos | Archivos de la patrocinadora en git (el de actividad por LFS); `data/processed/` ignorado | Huella (`sha256`) de cada archivo y comprobación automática |
| Pruebas | Ninguna | Pruebas de la partición (sin fuga), de las funciones de `src/`, y de que la prueba no se use para elegir nada |
| Calidad de código | Ninguna (sin linter ni formateador) | `ruff` y `pre-commit` |
| CI | Un workflow que publica el sitio **solo al fusionar a `main`** y corre los dos verificadores | Checks en cada PR: hoy un PR roto no se detecta hasta fusionarlo |
| Modelos | `src/models/` vacío | Estructura de entrenamiento, evaluación y guardado |
| Trazabilidad con decisiones | Solo en prosa | Que cada corrida cite la decisión (`1.7`, `2.3`…) a la que sirve |

## Principios

1. **Lo mínimo que se mantenga.** Nada que requiera un servidor, una cuenta de pago o más de una persona pendiente.
2. **Lo que se compara se mide igual.** Un solo arnés de validación cruzada agrupada por andamio y esqueleto, con el error estándar corregido por dependencia entre pliegues (Nadeau y Bengio), que sirva para elegir L, la transformación, el modelo.
3. **La prueba se toca una vez.** El código debe negarse a evaluar en la prueba salvo con una marca explícita de evaluación final, y dejar registro de cada vez que se usa. Ya hubo una contaminación así en el Avance 2 (decisiones mirando validación y prueba juntas).
4. **Nada de datos en servicios externos.** NPASS es CC BY-NC y ChEMBL exige compartir igual lo derivado (entrada C.6): los seguidores en la nube reciben métricas, nunca registros.
5. **Lo regenerable no entra a git; lo pequeño y decisivo, sí.** Los resúmenes de corridas (CSV o JSON) se versionan; las matrices derivadas y los artefactos pesados, no.

## Herramientas: opciones y recomendación

| Necesidad | Opciones | Recomendación | Por qué |
|:--|:--|:--|:--|
| Seguimiento de experimentos | MLflow local · Weights & Biases · DVC experiments · solo archivos | **MLflow con almacén local (SQLite) más un resumen versionado en git** | Sin servidor ni cuenta, interfaz para explorar, y el resumen en git es lo que se comparte entre máquinas |
| Pipeline | Makefile · `just` · DVC · Snakemake | **Makefile** | Ya hay scripts; basta encadenarlos. DVC solo si los datos derivados empiezan a pesar |
| Versionado de datos | Git LFS (hoy) · DVC | **Seguir con LFS para el archivo de la patrocinadora y un manifiesto de `sha256` para el resto** | Un solo mecanismo; cambiar de herramienta no resuelve nada hoy |
| Entorno | `requirements.lock` · devcontainer o Docker | **Mantener el lock y añadir un devcontainer (Linux, Python 3.12)** | Es lo único que quita la diferencia de sistema operativo, que ya midió su efecto |
| Calidad | ruff · black · flake8 | **ruff (linter y formateador) con pre-commit** | Una herramienta, configuración mínima |
| Pruebas | pytest | **pytest** | Estándar |
| CI | GitHub Actions | **Un workflow nuevo en cada PR** | Ya se usa Actions para el sitio |
| Registro de modelos | MLflow Registry · carpeta `models/` con tarjeta | **Carpeta `models/` con una tarjeta por modelo, hasta que haya más de uno que comparar** | Los modelos son pequeños y sklearn los guarda en un archivo |

## Fases

Las fechas son las de los Avances del curso. El esfuerzo es relativo: S (horas), M (un día), L (varios días).

### Fase 0 · Lo mínimo para el Avance 3 (hasta el 18 de octubre)

El baseline necesita comparar muchas configuraciones sin perder el hilo.

| # | Entregable | Aceptación | Esfuerzo |
|:--|:--|:--|:--|
| 0.1 | **Convención de una corrida**: carpeta `experimentos/<id>/` con `params.yaml`, `metricas.json`, `entorno.json` (commit y si el árbol estaba sucio, versiones, sistema operativo, huella del lock y de los datos) y semillas | Cualquier corrida se puede repetir leyendo su carpeta | M |
| 0.2 | **`src/tracking.py`**: función que crea la corrida, escribe lo anterior y, si MLflow está instalado, lo registra también | Un experimento nuevo se registra con tres líneas | M |
| 0.3 | **Arnés de validación cruzada** (`src/evaluation/cv.py`): pliegues agrupados por andamio y esqueleto (acíclicos por esqueleto), semillas repetidas, error estándar corregido, comparación pareada. Generaliza lo que hoy vive en `experimento_L_sortslice.py` | El experimento de L y la §8.2 salen del mismo arnés con las mismas cifras | M |
| 0.4 | **Guarda de la prueba**: la evaluación en prueba exige `final=True` y deja registro | Un intento sin la marca falla con un mensaje claro | S |
| 0.5 | **Manifiesto de datos** (`data/MANIFEST.json` con `sha256`) y script de comprobación | La comprobación falla si un archivo cambió | S |
| 0.6 | **Checks en cada PR** (`.github/workflows/checks.yml`): sitio, los dos verificadores, `ruff`, `pytest` | Un PR roto no se puede fusionar sin verlo | M |
| 0.7 | **Pruebas mínimas**: partición sin fuga (`verificar_fuga`), `SortAndSlice` (vocabulario solo del entrenamiento), `limpiar_descriptores` (`Ipc`) | Pasan en el CI | M |
| 0.8 | **Retropoblar** las dos mediciones existentes (L y transformaciones) como las dos primeras corridas | Aparecen en el registro con su decisión | S |

### Fase 1 · Para el Avance 4 (25 de octubre)

| # | Entregable | Aceptación | Esfuerzo |
|:--|:--|:--|:--|
| 1.1 | **Resumen versionado** `experimentos/registro.csv` (una fila por corrida: id, fecha, decisión, métrica principal, enlace) generado por `tracking.py` | Se puede comparar entre máquinas sin abrir MLflow | S |
| 1.2 | **MLflow local** documentado (`mlflow ui`) y `mlruns/` ignorado | Cada integrante explora sus corridas | S |
| 1.3 | **Devcontainer** (Linux, Python 3.12, el lock) | Dos integrantes obtienen las mismas cifras en la regresión logística | M |
| 1.4 | **Estructura de `src/models/`**: entrenamiento y evaluación con el arnés, modelos de `docs/decisiones.md` (1.5) | El baseline de tres modelos sale de un comando | M |
| 1.5 | **Ligar corridas y decisiones**: cada entrada de la ruta cita las corridas que la sostienen | Se llega de una decisión a sus cifras en un clic | S |
| 1.6 | **Pre-commit** con `ruff`, la comprobación de decisiones y el manifiesto de datos | Se ejecuta antes de cada commit | S |

### Fase 2 · Para el Avance 5 y el texto académico (1 de noviembre)

| # | Entregable | Aceptación | Esfuerzo |
|:--|:--|:--|:--|
| 2.1 | **Evaluación final única** en la prueba, con registro de que se hizo una sola vez | Hay una corrida marcada `final` por modelo | S |
| 2.2 | **Artefactos de explicabilidad** guardados por corrida: atribuciones con dos métodos y las subestructuras en que coinciden (decisión C.2) | Se pueden regenerar a partir del modelo guardado | L |
| 2.3 | **Tarjeta de cada modelo** en `models/`: datos, partición, métricas con intervalos, límites conocidos | Una persona ajena la entiende sin preguntar | M |
| 2.4 | **Página de experimentos en el sitio**, generada desde `registro.csv` | Se publica sin editarla a mano | M |
| 2.5 | **Paquete para publicar** (código, particiones, etiquetas, resultados) para un repositorio con DOI | Solo después de resolver la entrada C.6 (licencias y autorización) | M |

## Qué no se hace (por ahora)

Orquestadores (Airflow, Prefect), Kubernetes, almacenes de características, entrenamiento en la nube, servicio de modelos en línea, seguidores que suban datos, y DVC mientras los datos derivados sigan en unos pocos megabytes. Si cambia la escala, se revisa.

## Riesgos

- **Sistemas operativos distintos.** Mientras no haya devcontainer, las cifras de la regresión logística pueden cambiar entre macOS y Linux. Mitigación: comparar siempre con el arnés de validación cruzada y no con una corrida.
- **MLflow es por máquina.** El almacén local no se comparte; por eso el resumen en git (1.1) es lo que importa.
- **Cuota de LFS** (1 GB de ancho de banda al mes): no añadir archivos pesados sin avisar.
- **Sobreingeniería.** Con tres personas y tres Avances, cada herramienta nueva compite con el trabajo del modelo. Si una fase se atrasa, se recorta por el final.
- **Licencias.** Cualquier artefacto que viaje fuera del repositorio debe revisarse contra la entrada C.6.

## Decisiones que necesita el equipo

1. ¿Se acepta un devcontainer como entorno de referencia para quien use macOS o Windows, aunque se pierda velocidad?
2. ¿Dónde viven los resúmenes de corridas (`experimentos/registro.csv` en git) y quién los revisa en cada PR?
3. ¿Se exige que todo resultado citado en el reporte tenga una corrida registrada?
4. ¿Se crean issues con la etiqueta `mlops` por cada fila de las fases 0 y 1? Las issues abiertas (#24 a #32) siguen hablando del Avance 2 y 3 y la #31 se refiere a una consulta que ya no existe como documento.
