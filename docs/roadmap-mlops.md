# Roadmap de MLOps

Plan de trabajo para dotar al proyecto de seguimiento de experimentos y reproducibilidad. **Es un documento interno: no se publica en el sitio** (no está en `DOCUMENTOS` de `scripts/prepare_site.py` ni en el navbar) y está pensado para que otra sesión de trabajo lo retome sin más contexto. Fecha de redacción: 11 de octubre de 2026.

## Cómo retomar

1. Leer `CLAUDE.md` y la página de decisiones (`docs/decisiones.md`): el trabajo de MLOps tiene que servir a lo que ahí se decide, no al revés.
2. Entorno: `uv venv --python 3.12 env && source env/bin/activate && uv pip install -r requirements.lock`. El lock debe compilarse con `--universal`: sin él queda resuelto solo para Linux y falla en macOS con «your requirements are unsatisfiable» (el de `main` está en ese caso hasta que se fusione el #47, que lo regenera).
3. Comprobar que todo corre antes de tocar nada: `python3 scripts/prepare_site.py && quarto render && python3 scripts/verificar_sitio.py && python3 scripts/verificar_decisiones.py`. Requiere tener **Quarto instalado** (quarto.org); sin él corren `prepare_site.py` y `verificar_decisiones.py`, pero no `quarto render` ni `verificar_sitio.py`.
4. El ejemplo a imitar es `scripts/experimento_L_sortslice.py`: un script, validación cruzada agrupada, resultados en un CSV versionado (`notebooks/datos/`) y un notebook que solo los lee.
5. Trabajar en una rama y una copia aparte (`git worktree`) si hay otra sesión usando la misma carpeta.

## Objetivo

Que cada resultado del proyecto se pueda **repetir, comparar y rastrear hasta la decisión que lo motivó**, con el mínimo de herramientas que un equipo de tres personas pueda mantener. La regla de fondo es la que ya rige el proyecto: *una corrida no decide* (ver la entrada 1.7 y la §8.2 del notebook 02, donde el mismo código dio cifras distintas en macOS y en Linux).

## Punto de partida

| Qué | Hoy | Falta |
|:--|:--|:--|
| Entorno | `requirements.lock` con Python 3.12; la primera celda del notebook 02 imprime las versiones | Nada garantiza el mismo entorno: la regresión logística con min–max da **0.481 en Linux con Python 3.12, 0.489 en macOS con 3.12 y 0.497 en macOS con 3.14** (según las mediciones del #47): unos 0.008 por el sistema operativo y otros 0.008 por la versión de Python |
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
3. **La prueba se toca una vez.** El código debe negarse a evaluar en la prueba salvo con una marca explícita de evaluación final, y dejar registro de cada vez que se usa. Ya hubo una contaminación así en el Avance 2: en `6e0491b` la celda del escalado hacía `idx_ev = np.where(~tr.values)[0]`, es decir, validación **y prueba** juntas, y sobre eso se comparaban las transformaciones y los métodos de selección; se corrigió en `fade019`.
4. **Nada de datos en servicios externos.** NPASS es CC BY-NC y ChEMBL exige compartir igual lo derivado (entrada C.6): los seguidores en la nube reciben métricas, nunca registros.
5. **Lo regenerable no entra a git; lo pequeño y decisivo, sí.** Los resúmenes de corridas (CSV o JSON) se versionan; las matrices derivadas y los artefactos pesados, no.

## Herramientas: opciones y recomendación

| Necesidad | Opciones | Recomendación | Por qué |
|:--|:--|:--|:--|
| Seguimiento de experimentos | MLflow local · MLflow en servidor compartido · Weights & Biases · DVC experiments · solo archivos | **Git como fuente de verdad (una carpeta de texto por corrida) y MLflow local como visor que la importa** | Todos ven y reproducen lo mismo sin servidor ni cuenta; MLflow aporta la interfaz, no la verdad |
| Pipeline | Makefile · `just` · DVC · Snakemake | **Makefile** | Ya hay scripts; basta encadenarlos. DVC solo si los datos derivados empiezan a pesar |
| Versionado de datos | Git LFS (hoy) · DVC | **Seguir con LFS para el archivo de la patrocinadora y un manifiesto de `sha256` para el resto** | Un solo mecanismo; cambiar de herramienta no resuelve nada hoy |
| Entorno | `requirements.lock` · devcontainer o Docker | **Mantener el lock y añadir un devcontainer (Linux, Python 3.12)** | Es lo único que quita la diferencia de sistema operativo, que ya midió su efecto |
| Calidad | ruff · black · flake8 | **ruff (linter y formateador) con pre-commit** | Una herramienta, configuración mínima |
| Pruebas | pytest | **pytest** | Estándar |
| CI | GitHub Actions | **Un workflow nuevo en cada PR** | Ya se usa Actions para el sitio |
| Registro de modelos | MLflow Registry · carpeta `models/` con tarjeta | **Carpeta `models/` con una tarjeta por modelo, hasta que haya más de uno que comparar** | Los modelos son pequeños y sklearn los guarda en un archivo |

## Cómo se comparten, se ven y se reproducen los registros

El almacén local de MLflow vive en la máquina de cada persona, así que **no es lo que se comparte**. Lo que se comparte es git:

1. **Qué se versiona.** Una carpeta pequeña por corrida, `experimentos/<id>/`, con `params.yaml`, `metricas.json`, `entorno.json` (commit, sistema operativo, versiones, huella del lock y de los datos) y `comando.txt`; y `experimentos/registro.csv`, una fila por corrida. Son archivos de texto de unos kilobytes. El `id` lleva fecha, autor y la decisión a la que sirve (por ejemplo `2026-10-14-art-1.7-L`), de modo que dos personas nunca escriben el mismo archivo y no hay conflictos al fusionar. `registro.csv` se regenera con `make registro`, no se edita a mano.
2. **Cómo se ven.** Tres niveles, de menos a más:
   - `make registro` imprime la tabla comparativa en la terminal;
   - `make mlflow-ui` importa `experimentos/` a un almacén local de MLflow (de forma idempotente) y abre la interfaz: ahí se comparan corridas, curvas y artefactos de las de todo el equipo, no solo las propias;
   - la página de experimentos del sitio (Fase 2.4), generada desde `registro.csv`, que ven todos y también la patrocinadora.
3. **Cómo se reproducen.** `make reproducir ID=<id>` lee `entorno.json`, comprueba el manifiesto de datos y la huella del lock, vuelve a correr con `params.yaml` y compara las métricas. En la misma plataforma deben coincidir; en otra, quedar dentro del error estándar de la validación cruzada (ya hay un caso medido: la regresión logística con min–max da **0.481 en Linux con Python 3.12, 0.489 en macOS con 3.12 y 0.497 en macOS con 3.14** (según las mediciones del #47): unos 0.008 por el sistema operativo y otros 0.008 por la versión de Python; para una tolerancia conviene el número limpio, ~0.008 a igual versión de Python). Si no coincide, el comando lo dice y señala qué cambió.
4. **Qué no se versiona.** Matrices derivadas, modelos pesados y artefactos grandes: se regeneran con la corrida o se comparten por un Release con su `sha256`. El resumen de una corrida nunca contiene registros de los datos (licencias de NPASS y ChEMBL).
5. **Si hiciera falta un servidor compartido.** Se puede añadir después sin cambiar nada de lo anterior, porque lo que manda es git. Se revisó DagsHub (octubre de 2026, en sus páginas oficiales de precios y de MLflow) y **hoy no conviene**:
   - El plan gratuito da 20 GB, repositorios privados ilimitados *solo para uso no comercial* y **hasta 2 colaboradores** en los privados. El seguimiento es ilimitado en repositorios públicos, pero **de solo 100 experimentos en los privados**; ese tope se alcanza rápido si cada configuración de una validación cruzada cuenta como experimento. No menciona ninguna condición para estudiantes o académicos.
   - Cada repositorio trae su propio servidor MLflow (`https://dagshub.com/<usuario>/<repo>.mlflow`) con registro de modelos, pero **solo quien tiene permiso de escritura puede ver la interfaz y registrar corridas**: la patrocinadora no vería nada sin ocupar uno de los dos lugares de colaborador o sin hacer público el repositorio. Para enseñarle resultados sirve más la página del sitio (Fase 2.4).
   - El plan de equipo cuesta 119 dólares por persona al mes, relevante si la entrada C.6 resultara en aspiraciones comerciales.
   - Lo que de verdad sostiene la decisión es que, como la fuente de verdad es git, probarlo no compromete nada: la dependencia es reversible. Si el equipo lo quiere más adelante, se añade sin cambiar lo anterior.
   - **No se verificó** si se puede conectar el repositorio de GitHub, si «2 colaboradores» incluye al dueño, ni dónde se alojan los datos.

   Lo razonable es repetirlo solo si el equipo quiere una interfaz compartida en vivo, como un experimento de una hora con un repositorio público que reciba únicamente métricas. La alternativa de un MLflow en una máquina del equipo es frágil: depende de que esté encendida.

## Fases

Las fechas son las de los Avances del curso. El esfuerzo es relativo: S (horas), M (un día), L (varios días).

### Fase 0 · Lo mínimo para el Avance 3 (hasta el 18 de octubre)

El baseline necesita comparar muchas configuraciones sin perder el hilo.

| # | Entregable | Aceptación | Esfuerzo |
|:--|:--|:--|:--|
| 0.1 | **Convención de una corrida**: carpeta `experimentos/<id>/` con `params.yaml`, `metricas.json`, `entorno.json` (commit y si el árbol estaba sucio, versiones, sistema operativo, huella del lock y de los datos) y semillas | Cualquier corrida se puede repetir leyendo su carpeta | M |
| 0.2 | **`src/tracking.py`**: función que crea la corrida, escribe lo anterior y, si MLflow está instalado, lo registra también | Un experimento nuevo se registra con tres líneas | M |
| 0.3 | **Arnés de validación cruzada** (`src/evaluation/cv.py`): pliegues agrupados por andamio y esqueleto (acíclicos por esqueleto), semillas repetidas, error estándar corregido, comparación pareada. Generaliza lo que hoy vive en `experimento_L_sortslice.py` | El experimento de L y el de escalado (§8.2), reejecutados desde el arnés, dan cada uno sus mismas cifras de hoy. La factorización ya empezó: `grupos_cv` está en `src/data_prep/splits.py` (#47) | M |
| 0.4 | **Guarda de la prueba**: la evaluación en prueba exige `final=True` y deja registro | Un intento sin la marca falla con un mensaje claro | S |
| 0.5 | **Manifiesto de datos** (`data/MANIFEST.json` con `sha256`) y script de comprobación | La comprobación falla si un archivo cambió | S |
| 0.6 | **Checks en cada PR** (`.github/workflows/checks.yml`): sitio, los dos verificadores, `ruff`, `pytest` | Un PR roto no se puede fusionar sin verlo | M |
| 0.7 | **Pruebas mínimas**: partición sin fuga (`verificar_fuga`), `SortAndSlice` (vocabulario solo del entrenamiento), `limpiar_descriptores` (`Ipc`) | Pasan en el CI | M |
| 0.8 | **Retropoblar** las dos mediciones existentes (L y transformaciones) como las dos primeras corridas | Aparecen en el registro con su decisión | S |

### Fase 1 · Para el Avance 4 (25 de octubre)

| # | Entregable | Aceptación | Esfuerzo |
|:--|:--|:--|:--|
| 1.1 | **Resumen versionado** `experimentos/registro.csv` (una fila por corrida: id, fecha, decisión, métrica principal, enlace) generado por `tracking.py` y `make registro` | Se puede comparar entre máquinas sin abrir MLflow | S |
| 1.2 | **MLflow como visor local**: `scripts/importar_mlflow.py` carga `experimentos/` (idempotente), `make mlflow-ui`, y `mlruns/` ignorado | Cada integrante ve en la interfaz las corridas de todo el equipo | S |
| 1.2b | **`make reproducir ID=…`** con la comparación de métricas descrita arriba | Repetir una corrida ajena en la misma plataforma da las mismas cifras | M |
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
- **MLflow es por máquina.** El almacén local no se comparte; por eso git es la fuente de verdad y MLflow solo un visor que se reconstruye desde `experimentos/`.
- **Cuota de LFS** (1 GB de ancho de banda al mes): no añadir archivos pesados sin avisar.
- **Sobreingeniería.** Con tres personas y tres Avances, cada herramienta nueva compite con el trabajo del modelo. Si una fase se atrasa, se recorta por el final.
- **Licencias.** Cualquier artefacto que viaje fuera del repositorio debe revisarse contra la entrada C.6.

## Decisiones que necesita el equipo

Voto de Artemio (12 de octubre) entre paréntesis; falta el del resto del equipo.

1. ¿Se acepta un devcontainer como entorno de referencia para quien use macOS o Windows, aunque se pierda velocidad? *(Artemio: sí.)*
2. ¿Dónde viven los resúmenes de corridas (`experimentos/registro.csv` en git) y quién los revisa en cada PR? *(Artemio: en git, y se revisan en el PR como cualquier otro archivo.)*
3. ¿Se exige que todo resultado citado en el reporte tenga una corrida registrada? *(Artemio: sí.)*
4. ¿Basta con git más el visor local, o el equipo prefiere un servidor compartido (propio o un servicio externo) desde el principio? *(Artemio: git más visor local por ahora.)*
5. ¿Se crean issues con la etiqueta `mlops` por cada fila de las fases 0 y 1? *(Artemio: sí.)* Las issues abiertas (#24 a #32) siguen hablando de los Avances 2 y 3. Ya se actualizaron las anclas de las #26, #29, #31 y #32 a la numeración nueva de la Ruta, y la #31 explica que la consulta se fusionó en esa página y que `verificar_decisiones.py` ya no comprueba que una pregunta aparezca en un documento aparte.
