# 04 — Datos de neuroactividad (etapa 2)

Investigación del 2026-09-22. Cubre las tres bases que mencionaron los asesores y la construcción de etiquetas para la segunda etapa: dado que el compuesto llega al cerebro, ¿tiene efecto neuroprotector y contra qué diana?

## Estimación honesta de tamaño — leer esto primero

Es el dato más importante de esta rama.

**El cruce final de "producto natural + diana relevante para neuroprotección + con SMILES + con valor de potencia usable" da entre unos cientos y 2,000–4,000 filas compuesto-diana, y por debajo de 1,000 compuestos únicos tras deduplicar por InChIKey.**

El número que lo ancla: CMAUP tiene 60,222 ingredientes, pero **solo 2,979 son "potentes" (<1 µM) contra las 758 dianas juntas**, antes de cualquier filtro de SNC. Restringir a ~15 dianas neuroprotectoras lo reduce mucho más.

Los precedentes confirman el orden de magnitud: Gürbüz et al. 2025 trabajó con 23 fenólicos naturales; Kato et al. 2025 tamizó ~1,700 constituyentes y obtuvo datos usables de BBB para solo 611; el modelo de AChE de Yasir et al. 2026 usó 6,880 compuestos, pero para una sola diana y sobre todo el espacio químico, no solo productos naturales.

**Consecuencias:**

- Es suficiente para ML clásico (Random Forest, gradient boosting, regresión logística sobre fingerprints) con validación cruzada rigurosa.
- **Es demasiado poco para entrenar deep learning desde cero con confianza.**
- Mitigaciones posibles: (a) quedarse con ML clásico más fingerprints, (b) un esquema multi-tarea que agrupe las ~15 dianas en vez de un modelo por diana, para subir el N efectivo, o (c) transfer learning desde una representación preentrenada, afinada sobre este conjunto pequeño.

*Esta estimación es una extrapolación razonada a partir de cifras verificadas, no un número leído directamente de una fuente.*

## Estado de las tres bases

### CMAUP 2.0 — viva

Sitio: http://bidd.group/CMAUP/ — carga con normalidad. Del grupo BIDD (Universidad de Fudan).

Paper: Hou et al., *Nucleic Acids Research* 52(D1):D1508–D1518 (2024). Leído completo.

- **60,222 ingredientes químicos**, de los cuales **2,979 tienen actividad "potente" (<1 µM)** contra al menos una diana. CMAUP ya trae integrado su propio corte activo/inactivo en el esquema (`Ingredients_All` contra `Ingredients_onlyActive`).
- 7,865 plantas, 758 dianas, 1,399 enfermedades, 238 rutas KEGG.
- Tipos de actividad para definir "activo": IC50, EC50, ED50, AC50, Ki o Potency < 1 µM.
- Referencias cruzadas a PubChem, ZINC, ChEMBL, NCBI TaxonomyDB.
- Curada a partir de ChEMBL, ClinicalTrials.gov, NPASS y TTD. Las actividades se describen explícitamente como derivadas de experimentos, no predichas in silico.
- Descarga: 13 archivos planos separados por tabuladores. No hay API.
- **No tiene curación específica de SNC ni etiquetado sistemático de neurodegeneración.**

*Parcialmente verificado:* el texto del sitio no dice "SMILES" por nombre entre los datos estructurales. Hay que abrir `Ingredients_All.txt` y su Readme para confirmar la columna exacta.

### NPASS v3.0 — viva, más grande de lo esperado

Sitio: http://bidd.group/NPASS/ — v3.0, publicada el 15 de junio de 2025.

Paper a citar: Lin et al., *Nucleic Acids Research* 54(D1):D1519–D1527 (2026). Es el que corresponde al sitio vivo.

- **204,023 productos naturales**, 48,940 organismos fuente, **8,764 dianas moleculares**, **1,048,756 registros experimentales de actividad** (221,541 a nivel molecular, 681,970 in vitro, 145,245 in vivo).
- Novedades de v3.0: 34,975 registros cuantitativos de toxicidad y 9,713 de ADME.
- **InChIKey es el identificador primario de referencia cruzada.** Los SMILES están en el archivo de estructura, confirmado en la página de descarga.
- **No hay escala estandarizada tipo pChEMBL.** Los registros traen valores y unidades como los reportó el estudio original, o sea crudos y heterogéneos: **el equipo tendrá que normalizar unidades.**
- **Licencia CC BY-NC 4.0**, declarada en el texto del paper. Es **no comercial**, más estricta que CMAUP y ChEMBL. Conviene avisarlo a los asesores si el proyecto tuviera aspiraciones comerciales.
- Descarga: archivos planos de 48–130 MB. No hay API.
- Es la más activamente mantenida de las tres por cadencia de actualización.

### ChEMBL — sitio web vivo, API caída

**Hallazgo negativo verificado dos veces, con `curl` y con fetch:** los endpoints `https://www.ebi.ac.uk/chembl/api/data/status.json`, `.../target/search.json`, `.../target.json` y `.../molecule/CHEMBL25.json` (aspirina, la consulta más básica posible) devolvieron **los cuatro HTTP 500**, mientras `https://www.ebi.ac.uk/` respondía 200 al mismo tiempo. Eso descarta un bloqueo de red local: es el servidor de EBI.

**Implicación:** `chembl_webresource_client` envuelve esa misma API y hereda el problema.

**FTP confirmado vivo:** `https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/` responde 200 y contiene `chembl_37`, o sea **ChEMBL release 37 es la versión actual**. Desde septiembre de 2025 hay dumps en SQLite para todos los releases, que es el formato más práctico para un equipo estudiantil: un solo archivo, sin montar PostgreSQL, consultable con `sqlite3` o pandas.

**Recomendación de acceso: usar el dump SQLite del release 37 como fuente primaria.** Es consultable con SQL, versionado y reproducible (se puede citar el release exacto, lo que importa para la tesis) e inmune a caídas de la API. Dejar el cliente de Python para consultas interactivas pequeñas, una vez confirmado que la API volvió.

Licencia: CC BY-SA 3.0, declarada en el sitio.

## pChEMBL y estandarización

Leído completo de la documentación de interfaz de ChEMBL.

**pChEMBL = −log10** del valor molar de IC50, XC50, EC50, AC50, Ki, Kd o Potency. Un IC50 de 1 nM da pChEMBL 9; uno de 10 µM da 5.

Se calcula **solo** cuando: `standard_type` está en el conjunto permitido, `standard_relation` es "=" (o sea, excluye datos censurados como ">10000"), `standard_units` es nM, `standard_value` > 0, y `data_validity_comment` es nulo o "Manually validated". ChEMBL además marca filas problemáticas ("Outside typical range", "Potential author error") que conviene excluir o revisar.

**La clasificación de dianas es una jerarquía curada a medida, no un árbol uniforme**: las quinasas siguen el kinoma de Manning, los GPCR siguen IUPHAR/GPCRdb, las proteasas MEROPS, las enzimas números EC. **No hay categoría "CNS" ni "neurodegeneración" integrada**: hay que construir la lista de dianas a mano y consultar por `target_chembl_id`.

## Lista de dianas relevantes para neuroprotección

Como no existe categoría navegable, hay que armar una lista blanca explícita. *Parcialmente verificada: no se contrastó diana por diana contra los IDs vivos de ChEMBL, porque la API estaba caída. Verificar los `target_chembl_id` al implementar.*

- **Acetilcolinesterasa (AChE) y butirilcolinesterasa (BuChE)** — dianas sintomáticas clásicas de Alzheimer.
- **Monoamino oxidasa A y B (MAO-A, MAO-B)** — relevantes en Parkinson y Alzheimer.
- **BACE1 (β-secretasa 1)** — vía amiloidogénica.
- **Subunidades del receptor NMDA (GRIN1/2A/2B)** — excitotoxicidad.
- **Receptores de adenosina (A1, A2A, A2B, A3)** — el antagonismo de A2A es un mecanismo validado en Parkinson (precedente: istradefilina).
- **Receptores sigma-1 y sigma-2** — neuroprotección y estrés de retículo.
- **GSK-3β y CK-1δ** — patología de tau. Confirmadas como par de cribado real en un estudio de productos naturales.
- **Componentes de la vía Nrf2/KEAP1** — respuesta antioxidante. La cobertura en ChEMBL suele ser escasa (es un factor de transcripción, difícil de ensayar por IC50): esperar N bajo.
- **Marcadores de neuroinflamación: COX-2, iNOS, NLRP3** — lecturas secundarias comunes en la literatura de productos naturales.

## Enlace y deduplicación entre bases

- **InChIKey es la llave práctica universal.** NPASS lo usa explícitamente; ChEMBL tiene el campo `standard_inchi_key`; CMAUP cruza con PubChem/ZINC/ChEMBL.
- **UniChem**, el servicio de referencias cruzadas de EBI, es la herramienta recomendada para resolver los mapeos a escala, en vez de programarlos a mano.
- Deduplicar por InChIKey completo (coincidencia exacta de estereoquímica), con respaldo en los primeros 14 caracteres (esqueleto, ignorando estéreo e isótopos) cuando la exacta falle. *Es buena práctica general del campo, no una cita verificada.*

## El problema de etiquetado

La preocupación de los asesores está fundamentada y el campo tiene una respuesta estándar, aunque imperfecta.

**1. Usar pChEMBL, no el número crudo de actividad.** Ya normaliza IC50/EC50/Ki/Kd sobre una escala log-molar única, bajo reglas documentadas y reproducibles. Para NPASS y CMAUP, que **no** traen un equivalente precalculado, hay que computar el −log10 del valor molar desde los campos crudos, tras filtrar a relación "=" únicamente. Los valores censurados (">" o "<") se descartan o se tratan aparte como evidencia unilateral, **nunca como falsos negativos**.

**2. Agregar por par compuesto-diana, no tratar cada ensayo como ejemplo independiente.** Conservar el valor **más potente** reportado (o la mediana si varios ensayos independientes concuerdan). Si no, el mismo compuesto medido a 1 µM (inactivo) y a 10 µM (activo) se convierte en señal contradictoria de entrenamiento en vez de un problema de agregación. **Esto es lo que resuelve directamente la advertencia de los asesores.**

**3. Umbrales con precedente en la literatura, no inventados:**

- CMAUP usa **<1 µM = potente/activo** para construir su propio subconjunto de activos. Es un corte estricto, tipo fármaco.
- **ExCAPE-DB** usa **pXC50 ≥ 5 (≤10 µM) = activo**, y además exige ≥20 activos por diana para que esa diana sea modelable. Es una convención más laxa y de alta cobertura, común para construir conjuntos grandes de entrenamiento.
- Otros papers usan cortes más estrictos (pChEMBL > 6.5 o ≥ 7) cuando el objetivo se acerca a "candidato a fármaco". *Recogido de síntesis de búsqueda, no de una fuente primaria única.*

**Recomendación: etiqueta de dos niveles.**

| Nivel | Umbral | Uso |
|---|---|---|
| 1 — "activo" | pChEMBL ≥ 5 (≤10 µM), convención ExCAPE-DB | Objetivo principal de clasificación binaria; maximiza el N usable |
| 2 — "potente" | ≥ 6 (≤1 µM), coincide con la definición de CMAUP | Comprobación secundaria de robustez |

Esto responde directamente a los asesores: hace explícita y defendible la dependencia de la concentración en vez de esconderla en un corte arbitrario único, y se alinea con lo que una de las tres bases que ellos nombraron ya hace internamente, lo cual da precedente citable en vez de un umbral inventado.

**4. Excluir o marcar** las filas con `data_validity_comment` y las relaciones distintas de "=", en vez de conservarlas en silencio.

## Precedentes: ¿existe ya este pipeline de dos etapas?

**No se encontró ningún paper publicado que haga exactamente lo que propone este proyecto**: un clasificador ML de permeabilidad BBB alimentando un clasificador ML de actividad neuroprotectora, específicamente para productos naturales, sobre CMAUP/NPASS/ChEMBL. Parece un hueco genuino, útil para el encuadre de novedad. *La búsqueda usó varios ángulos y leyó completos los hits más cercanos, pero no fue exhaustiva de toda la literatura, así que no se puede descartar con certeza un precedente más cercano.*

Los tres precedentes más próximos, leídos completos:

- **Kato et al. (2025)**, *Scientific Reports* 15:7431. Biblioteca interna de NCATS, ~1,700 constituyentes → ensayo PAMPA-BBB (611 resultados usables, 255 permeables) → **segunda etapa** de neurotoxicidad por crecimiento de neuritas sobre los 247 más permeables (83 hits). Es el más cercano en arquitectura a un diseño de dos etapas, pero es de laboratorio, no ML, y mide neurotoxicidad, no neuroprotección: un encuadre inverso que vale la pena notar.
- **Gürbüz et al. (2025)**, *Drug Development Research* 86(8):e70193. Estudio pequeño (n=23) de fenólicos naturales, etapa PAMPA-BBB → etapa de inhibición de dianas (GSK-3β, CK-1δ, AChE). Directamente relevante para Alzheimer y para el encuadre del proyecto, pero N diminuto y de laboratorio.
- **Yasir et al. (2026)**, *Pharmaceuticals* 19(7):1120. **La plantilla metodológica más cercana**: Random Forest entrenado sobre 6,880 inhibidores de AChE de ChEMBL (regresión de pIC50, R²=0.65 en prueba, umbral de hit pIC50 > 7) → filtro fisicoquímico de permeabilidad BBB → docking y dinámica molecular → validación experimental. No son productos naturales, pero demuestra el mismo orden de etapas que propone este proyecto y sirve de modelo para redactar la sección de metodología (split, elección de umbral, control de Y-randomization).

## Pasos prácticos

- http://bidd.group/CMAUP/download.html — 13 archivos planos con Readme de columnas.
- http://bidd.group/NPASS/downloadnpass.php — archivos de estructura, actividad y especies.
- https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/latest/ — confirmado vivo, `chembl_37` presente. Preferir el dump SQLite sobre la API.
- https://chembl.gitbook.io/chembl-interface-documentation/ — definición de pChEMBL y FAQ de clasificación de dianas.

## Lo que no se pudo verificar

- **Esquema exacto de los archivos de CMAUP** (nombres de columnas, si hay SMILES o solo InChI): no se descargaron los archivos planos.
- **Licencia formal de reutilización de datos de CMAUP**: solo se confirmó la licencia CC BY del *paper*; no se halló una página de términos de la base.
- **Versión y licencia exactas del paquete `chembl_webresource_client`**: la página de PyPI falló al renderizar dos veces. Correr `pip show` localmente.
- **Si la caída de la API de ChEMBL es transitoria o sistémica**: solo hay confirmación puntual del 2026-09-22. Reverificar al implementar.
- **Si las referencias cruzadas de CMAUP/NPASS son suficientemente completas** para evitar huecos grandes de deduplicación: se confirmó el mecanismo, no la cobertura empírica.
- **Búsqueda exhaustiva de precedentes** del pipeline de dos etapas: se leyeron completos los tres hits más cercanos, sin agotar todas las variantes de consulta.
