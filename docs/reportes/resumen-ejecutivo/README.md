# Resumen ejecutivo

Entrega 8, **15 de noviembre de 2026**. PDF de 3 páginas más anexos, nombre
`resumen_ejecutivo.#Equipo`.

| archivo | qué es |
|:--|:--|
| `resumen_ejecutivo.tex` | la plantilla del curso, con la bibliografía del proyecto |
| `bibliografia.bib` | enlace simbólico a `docs/referencias/bibliografia.bib` |
| `logo.jpeg` | enlace simbólico a `docs/reportes/logo-tec.jpeg` |

Se compila igual que el artículo: **pdfLaTeX + Biber** en Overleaf, resolviendo los enlaces
simbólicos antes de subir. Ver `../articulo/README.md`.

## La plantilla está escrita para otro tipo de proyecto

Sus ocho recuadros de cifras asumen un proceso de negocio que se automatiza. Rellenarlos tal
cual sería inventar, y la rúbrica pide «beneficios cuantificables con supuestos razonables y
coherentes con el contexto de la patrocinadora» (30 pts).

| recuadro de la plantilla | qué asume | qué tiene este proyecto |
|:--|:--|:--|
| Métrica · Mejora | un modelo en servicio | MCC 0.3385 en la prueba reservada de la fase 1 |
| Cobertura · Latencia | peticiones atendidas | no hay servicio desplegado |
| Ahorro de tiempo (h/mes) | trabajo manual que se sustituye | no hay proceso operativo que reemplazar |
| Costos operativos (MXN/mes) | un gasto corriente que baja | la patrocinadora es un departamento de bioingeniería |
| Reducción de errores · Capacidad de atención | un flujo con volumen | el entregable es priorización de candidatos |

Lo defendible es reencuadrarlos sobre la unidad real —compuestos triados por lote de ensayo,
costo de ensayo evitado por candidato descartado, fracción de la biblioteca que hay que medir
para recuperar los activos— con el cálculo y los supuestos en el Anexo A, que es donde la
plantilla los pide.

**Y el recuadro «Mejora» tiene una trampa.** La rúbrica exige que todos los valores coincidan
con el artículo, y el artículo ya fijó su regla de cita: el 0.6322 de `solo_npass` no viaja
sin el 0.530 de la prueba reservada al lado. Un recuadro con un porcentaje suelto contradice
esa regla.

## La declaración de uso de IA

La plantilla trae un marcador que cita `anthropic2026claude` «para [indicar la finalidad]».
Los cuadernos ya tienen una declaración mejor —tabla con herramienta, propósito, alcance por
sección y qué validó el equipo—: reutilizarla es lo más barato del criterio de estructura.
**El modelo concreto lo tiene que escribir quien firme la declaración**, no esta carpeta.
