# 05 — Fuentes de datos abiertas

Verificación del 2026-09-23/24. Complementa los documentos [02](02-datasets-bbb.md) y [04](04-datos-neuroactividad.md), que ya cubren B3DB, CMAUP, NPASS, ChEMBL y TDC. Aquí se verifican las bases que quedaban pendientes.

Todas las URLs se consultaron con `curl` para obtener el código HTTP real. Donde el sitio era una aplicación renderizada en cliente y no se pudo extraer contenido, se dice explícitamente.

## Recomendación

Agregar tres, en este orden:

1. **COCONUT 2.0** — el universo de compuestos más amplio, con la licencia más permisiva.
2. **LOTUS** — por su taxonomía curada, no por su conteo de moléculas.
3. **UniChem** — como infraestructura de mapeo entre bases, no como fuente de compuestos.

No integrar por ahora: ZINC, DrugBank, NPAtlas, SuperNatural ni TTD. Las razones están abajo.

## Tabla comparativa

| Base | Estado | Escala confirmada | Licencia de los datos | Sin registro | Solapa con CMAUP/NPASS |
|---|---|---|---|---|---|
| **COCONUT 2.0** | Vivo | 738,829 moléculas, 71 colecciones fuente | **CC0** | Sí | **Sí, los incluye a ambos** |
| **LOTUS** | Vivo (sitio no legible) | 750,000+ pares estructura-organismo | **CC BY 4.0** | Sí, vía Zenodo | Parcial |
| **PubChem** | Vivo, API probada | 124.67M compuestos, 1.89M bioensayos | Dominio público (no reconfirmado) | Sí | Fuente ascendente |
| **UniChem** | Vivo, API probada | Servicio de mapeo | **No declarada** | Sí | No aplica |
| NPAtlas | Vivo | Versión 2024_09 | CC BY-NC 4.0 | Sí | Mínimo, solo microbiano |
| DrugBank | **Descargas pausadas** | Versión 5.1.22 | CC BY-NC 4.0 | No, requiere cuenta | Marginal |
| ZINC | UI con CAPTCHA | No verificada | **Redistribución restringida** | Archivos masivos sí | Su subconjunto NP ya está en COCONUT |
| TTD | Vivo, sin contenido accesible | No verificada | No verificada | No verificado | No verificado |
| SuperNatural 3.0 | **Caído (DNS)** | No verificable | No verificable | — | Ya incorporado en COCONUT |

---

## COCONUT 2.0 — prioridad máxima

`https://coconut.naturalproducts.net/` responde HTTP 200. Versión activa 2.0.

- **738,829 moléculas**, cifra leída del snapshot de estadísticas del sitio.
- **71 colecciones fuente**, confirmado paginando la lista completa.
- Anotaciones: SMILES, InChI, propiedades moleculares y clases NPClassifier.
- **Licencia CC0**, citada textualmente de la página de descarga: los datos se liberan bajo CC0, permitiendo uso, modificación y distribución libres sin restricciones. El código es MIT.
- Descarga sin registro: CSV lite 191 MB, CSV completo 207.9 MB, SDF 2D lite 287.6 MB, SDF 2D completo 691.7 MB, SDF 3D 305.3 MB, volcado SQL completo 31.91 GB.

**El hallazgo central**: COCONUT ya incorpora, deduplicadas, las colecciones de **NPASS, CMAUP, NPAtlas, SuperNatural 3.0 y el subconjunto de productos naturales de ZINC**, junto con unas 65 fuentes adicionales (NANPDB, NPACT, CMNPD, DrugBank NPs, ChEMBL NPs, ChEBI NPs, Phyto4Health, CyanoMetNP, entre otras).

> **Advertencia importante, no verificada por la investigación:** COCONUT aporta estructuras y clasificación, pero **no se confirmó que incluya registros de actividad biológica**. CMAUP y NPASS sí los traen. Por lo tanto COCONUT **no sustituye** a esas dos para la etapa 2: amplía el universo de compuestos, no la información de actividad. Verificar las columnas del CSV antes de fijar la arquitectura de datos.

La ruta `/api-documentation` devolvió 404, así que el endpoint REST documentado no se pudo confirmar.

`Cita: chandrasekhar2025coconut`

---

## LOTUS — segunda prioridad, por la taxonomía

El sitio responde HTTP 200 pero es una aplicación React renderizada completamente en cliente: el HTML crudo son 366 bytes. **No se pudo leer ninguna cifra ni licencia desde la interfaz web.**

La verificación se hizo por rutas alternativas:

- La organización de GitHub confirma que LOTUS usa **Wikidata como backend** y publica volcados congelados en Zenodo.
- La API de Zenodo confirma el dataset congelado, publicado el 2022-09-16, con el archivo de pares estructura-organismo validados de ~290 MB y **licencia CC BY 4.0** (campo devuelto por la API, no inferido).
- El abstract del paper confirma **más de 750,000 pares estructura-organismo referenciados**.

**Su valor único no es el conteo de moléculas**, que probablemente solapa fuerte con COCONUT y NPASS, sino los pares estructura-organismo con taxonomía curada: qué organismo produce qué compuesto. Ni CMAUP ni NPASS ofrecen esa profundidad taxonómica, y abre la puerta a featurización por origen biológico.

**Limitación operativa:** hay que trabajar con el volcado de Zenodo o con consultas SPARQL sobre Wikidata, no con el sitio.

`Cita: rutz2022lotus`

---

## UniChem — infraestructura de mapeo

La API REST v1 se probó en vivo con el InChIKey del diazepam y devolvió HTTP 200 con el mapeo completo a ChEMBL, DrugBank, RCSB PDB, Guide to Pharmacology, ChEBI, PubChem, BindingDB, EPA CompTox, DrugCentral, BRENDA, ClinicalTrials.gov y más.

No requiere clave de API.

Es la pieza que permite unir COCONUT, LOTUS, NPASS, CMAUP, ChEMBL y PubChem por InChIKey **sin recalcular estructuras**. Dado que este proyecto fusiona varias fuentes, tiene alto valor práctico aunque no aporte compuestos.

> **Licencia de datos: no declarada.** No aparece en ninguna página accesible. Se reporta como no declarada en vez de asumir que es abierta.

`Cita: chambers2013unichem`

---

## PubChem

Verificado en vivo:

- **PUG-REST funcional**: la consulta de propiedades de la aspirina devolvió HTTP 200 con la fórmula y el SMILES correctos.
- **FTP vivo**, con listado de archivos actualizado.
- Cifras vía E-utils al 2026-09-24: **124,665,670 compuestos**, **1,886,628 bioensayos**, **349,346,126 sustancias**.

> **No reconfirmado en esta sesión:** los límites de tasa vigentes y la política de licencia. Ambas páginas son aplicaciones renderizadas en cliente sin contenido extraíble. Los valores históricamente documentados (5 solicitudes por segundo, 400 por minuto) son estables y conocidos, pero no se pudieron verificar hoy.

---

## Las que no conviene integrar ahora

### DrugBank — descargas académicas pausadas

La página de releases responde 200 y dice textualmente que **todas las descargas académicas están temporalmente pausadas** mientras actualizan cómo distribuyen los datos. Cada dataset aparece marcado como no disponible en la versión 5.1.22, publicada el 2026-06-27.

No es un problema de acceso del equipo: es un cambio de política en curso de DrugBank.

Además, los datasets abiertos son **CC BY-NC 4.0**, o sea no comercial, y su enfoque son fármacos aprobados, no productos naturales. Las páginas legales devolvieron 403, así que el texto exacto de la licencia académica no se pudo leer.

`Cita: knox2024drugbank`

### ZINC — incompatible con repo público

Tanto `zinc.docking.org` como `zinc20.docking.org` exigen pasar un reto de verificación humana antes de mostrar datos. El portal de archivos masivos sí es accesible sin reto.

El problema es la licencia. Texto literal leído en el portal de archivos: se pueden compartir libremente los resultados derivados del uso de los archivos, pero **no se pueden redistribuir porciones grandes sin permiso escrito de John Irwin**. Eso descarta subir volcados al repo público.

Su subconjunto de productos naturales ya está dentro de COCONUT.

`Citas: irwin2020zinc20, tingle2023zinc22`

### NPAtlas — ya contenido, y acotado

Vivo, versión de base de datos 2024_09, con descargas en TSV, Excel, JSON, SDF y GraphML sin registro. Licencia **CC BY-NC 4.0**, citada textualmente del sitio.

Se descarta por dos razones: está acotado a **productos naturales de origen microbiano** (bacterias y hongos), mientras que el foco del proyecto y las bases que ya tienen son mayormente de plantas; y ya es una de las 71 fuentes de COCONUT.

`Cita: poynton2024npatlas`

### SuperNatural 3.0 — aparentemente caído

El dominio no resuelve en DNS, mientras que el dominio padre de la institución sí. Se probaron variantes HTTP y dominios alternativos, todos inalcanzables.

Su contenido figura como una de las colecciones fuente de COCONUT, así que probablemente ya esté incorporado ahí.

### TTD — sin contenido verificable

Responde HTTP 200 en tres dominios. Es una aplicación Vue con backend Django; se extrajo el bundle de JavaScript y se sondearon rutas plausibles de la API, todas con 404.

**No se pudo obtener** ningún conteo, término de licencia ni formato de descarga. Haría falta un navegador con ejecución de JavaScript.

De todos modos no es una base de productos naturales, sino de dianas terapéuticas y fármacos.

`Cita: zhang2026ttd`

---

## Lo que no se pudo verificar

- Contenido de **LOTUS** en su propia interfaz web.
- Todo el contenido, conteos y licencia de **TTD**.
- Conteos y licencia de **ZINC** vía su interfaz.
- Texto legal exacto de la licencia académica de **DrugBank** (403).
- Cualquier dato de **SuperNatural 3.0** (dominio inalcanzable).
- Límites de tasa vigentes de **PubChem** y su página de política de licencia.
- Ruta real de la API REST de **COCONUT** y de **NPAtlas** (ambas dieron 404 en las rutas probadas).
- Licencia de datos de **UniChem**.
- **Si COCONUT incluye datos de actividad biológica** además de estructuras. Es la verificación más importante de esta lista para la arquitectura de datos del proyecto.
