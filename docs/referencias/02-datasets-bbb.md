# 02 — Datasets de barrera hematoencefálica

Investigación del 2026-09-22. Responde el pendiente que quedó abierto con los asesores sobre qué base de datos usar para la etapa 1.

## Recomendación

**B3DB como dataset primario**, usando el archivo de clasificación categórica y filtrando por su propia columna `Group` de confiabilidad.

Como secundarios: **TDC BBB_Martins** para comparar contra el leaderboard público (no para mezclar, ver la advertencia de solapamiento), y el conjunto de 154 compuestos de Spielvogel et al. 2025 como **validación externa**, porque es el único que aborda de frente la ambigüedad por concentración que señalaron los asesores.

### Por qué B3DB y no BBBP

- **Es 4–5 veces más grande**: 7,807–7,982 compuestos categóricos contra ~1,955 de BBBP.
- **Licencia CC0** sobre los datos, o sea dominio público. Es la opción más limpia para un repo público, sin ambigüedad de redistribución.
- **Trae metadatos de incertidumbre experimental**, lo que permite tomar una decisión documentada y defendible sobre qué subconjunto usar, en vez de heredar en silencio el ruido de BBBP.
- **Se mantiene activo** (paquete en PyPI, herramienta B3clf, actualización en 2025), mientras que BBBP es un artefacto estático de 2012–2018 con un bug de parseo documentado y sin corregir.

## Comparación

| Dataset | Tamaño categórico | Balance | logBB numérico | Licencia | Distribución |
|---|---|---|---|---|---|
| **B3DB** | 7,807 (paper 2021) / 7,982 (repo actual) | 63.5% BBB+ / 36.5% BBB− | 1,058 compuestos | **CC0** | GitHub TSV, PyPI `qc-B3DB`, figshare |
| BBBP (MoleculeNet) | ~2,050 crudos / 1,955–1,965 curados | ~76% / 24% | No | No explícita | Loader de DeepChem |
| TDC BBB_Martins | 1,975 | No verificado | No | "Not Specified" | `pip install pytdc` |
| LightBBB | 7,162 | 5,453 / 1,709 | No | No explícita | Material suplementario |
| Spielvogel et al. 2025 | 154 | Pequeño, a propósito | Algunos | **CC BY 4.0** | OSF: osf.io/cvhe9 |

**Advertencia de solapamiento:** BBBP y TDC BBB_Martins vienen ambos del mismo estudio (Martins et al. 2012). No son opciones independientes y compararlos entre sí no valida nada.

## B3DB en detalle

Fuente: Meng, Xi, Huang y Ayers, *Scientific Data* 8:289 (2021). Leído completo vía el espejo abierto de PMC, porque nature.com redirige a un muro de autenticación.

- Compilado a partir de **50 datasets publicados**.
- Categórico (cifras de la publicación de 2021): **7,807 = 4,956 BBB+ (63.5%) + 2,851 BBB− (36.5%)**.
- Subconjunto numérico con logBB: **1,058 compuestos**.
- **El umbral para convertir logBB en etiqueta categórica es logBB = −1.0**, descrito en el paper como "el umbral más ampliamente usado".

### La columna `Group` — lo más útil del dataset

Es el mecanismo que permite tomar una decisión defendible sobre el ruido de etiquetas:

**Datos numéricos:** Grupo A (243, medición única) / B (663, mediciones múltiples que concuerdan dentro del 5%) / C (3, dos valores divergentes, se usó media ponderada) / D (149, más de dos valores divergentes, se usó el más frecuente). Los registros con dispersión mayor a 1 unidad logarítmica (16 compuestos) se **descartaron**.

**Datos categóricos:** Grupo A (1,058, tienen logBB numérico) / B (3,621, de fuentes que declararon el umbral −1 y coincidieron) / C (3,077, coinciden en la etiqueta pero no especifican umbral) / D (51, **etiquetas contradictorias entre fuentes**; se conservó la mayoritaria y se descartaron 45 empates exactos).

**Recomendación:** entrenar con **A+B** (~4,679 registros de alta confianza con umbral conocido), usar C como conjunto de aumentación, y excluir D o reservarlo como conjunto de diagnóstico de casos ambiguos. Esta decisión, documentada, es justo lo que el comité va a querer ver en la metodología.

### Detalles técnicos

- **Deduplicación** por InChI único más SMILES isomérico.
- **Estandarización de SMILES**: se elevaron a SMILES isoméricos vía la API PUG-REST de PubChem; se quitaron sales y se neutralizaron cargas con el ChEMBL Structure Pipeline; se eliminaron moléculas con metales o átomos pesados (número atómico > 20). La estereoquímica se preserva donde la fuente la especificaba.
- **Licencia**: el repo declara explícitamente los archivos de datos como **CC0**. El paper por separado está bajo CC BY 4.0, que cubre el texto y las figuras. Son dos licencias para dos cosas distintas; conviene enunciarlo con precisión en la tesis y no colapsarlas.
- **No hay split oficial recomendado.** Los autores lo dejan al usuario y en cambio sugieren usar los grupos para elegir el subconjunto de confiabilidad.

### Discrepancia de versión — acción requerida

El paper de 2021 dice 7,807 compuestos. El repo vivo reporta **7,982** tras una actualización que sumó 171 BBB+ y 4 BBB−. **Hay que fijar un release o hash de commit específico antes de construir el pipeline, y documentar el conteo efectivamente usado.**

## BBBP — problemas documentados

- **Bug abierto sin corregir**: 12 SMILES del CSV no parsean en RDKit por errores de valencia de nitrógeno. El issue da los índices exactos de las filas afectadas: 59, 61, 391, 614, 642, 645–649, 685, 1998.
- **Desbalance** de ~76.3% BBB+ contra 23.7% BBB−, corroborado en dos fuentes independientes.
- **Duplicados y etiquetas en conflicto**: de ~2,050 filas, un esfuerzo de curación de terceros encontró solo 1,965 moléculas válidas, sin conflicto y canonicalizadas. *Dato parcialmente verificado, vía resúmenes indexados; reverificar antes de citarlo como exacto.*
- **Auditoría sistemática** (Schuh, Daniluk y Sieber, *Chemical Science*, publicación anticipada en línea): auditó 51 configuraciones de benchmarks en MoleculeNet, TDC, Polaris y DTI. Hallazgo clave: al enriquecer deliberadamente los conjuntos de prueba con moléculas del mismo andamio que el entrenamiento, **el modelo #1 del leaderboard original perdió el primer lugar en 15 de 28 datasets**. Los rankings publicados son medible­mente frágiles al rigor del split.

## Desempeño realista y splits

El **scaffold split (Bemis-Murcko) es la práctica estándar** y la recomendada tanto por DeepChem como por TDC, cuyo argumento explícito es que el modelo debe generalizar a fármacos estructuralmente distantes de los conocidos, que es exactamente el caso de uso de este proyecto.

| Contexto | Resultado |
|---|---|
| Scaffold split, leaderboard de TDC (26 modelos, leído directo) | Mejor: MiniMol **0.924 ± 0.003** AUROC |
| Rango realista para un modelo bien hecho | **0.85–0.92 AUROC** |
| Split aleatorio / Kennard-Stone (Yuan et al. 2018) | 98.7% de exactitud, MCC 0.958 |
| B3DB + CMUH-NPRL, split 80/10/10 no confirmado scaffold | AUC 0.88 |

**La brecha de 7 a 13 puntos entre split aleatorio y scaffold es el efecto de la fuga de datos.** Sirve como ilustración directa en la tesis. Los números de 95–99% no son comparables con los de 85–92%.

## El problema de la concentración

Los asesores advirtieron que un compuesto puede cambiar de positivo a negativo según la concentración del ensayo. La preocupación está fundamentada y hay literatura que la respalda.

**Spielvogel et al. (2025)**, *JCIM* 65(6):2773–2784, leído completo vía PMC. Cita textual:

> *"los sustratos pueden definirse como permeables pasivamente pero sufrir transporte activo de regreso al compartimento plasmático. Por lo tanto… la clasificación en sustratos e inhibidores es difícil para algunos compuestos, ya que esto puede depender de la concentración."*

El mecanismo es el eflujo mediado por glicoproteína-P y BCRP compitiendo con la difusión pasiva: a concentración baja domina el eflujo (resultado neto BBB−), a concentración alta el eflujo se satura y puede dominar la difusión pasiva (BBB+). Su dataset separa "sustratos/inhibidores" como clase propia en vez de forzar la binaria — un patrón de modelado que vale la pena citar en la sección de métodos.

### Recomendación de etiquetado

1. Usar el umbral **logBB = −1.0**, que es la convención dominante.
2. Restringir el entrenamiento a **B3DB grupos A+B** para minimizar el ruido de etiqueta inducido por concentración.
3. Excluir o marcar por separado los compuestos conocidos como sustratos de P-gp/BCRP, documentándolo como limitación y citando a Spielvogel et al.
4. **No afirmar que la etiqueta binaria es una propiedad intrínseca del compuesto.** Enmarcarla en la tesis como "clase de permeabilidad BBB predicha bajo las condiciones de ensayo y la convención de umbral usadas por la literatura fuente". Es el encuadre honesto dado todo lo anterior.

## Pasos prácticos

1. Clonar y **fijar un release** de `github.com/theochem/B3DB`. Usar `B3DB_classification_extended.tsv.gz` si se quieren los descriptores mordred precalculados, o `B3DB_classification.tsv` para calcular features propios desde la columna de SMILES isoméricos. Registrar el hash del commit.
2. Opcionalmente `pip install qc-B3DB` para acceso programático.
3. **Filtrar por `Group`**: A/B para entrenar, C como aumentación, D como conjunto ambiguo documentado. Esta lógica y su justificación van en la sección de métodos.
4. **Scaffold split** con la función de andamio de Bemis-Murcko de RDKit (o `ScaffoldSplitter` de DeepChem). Nunca aleatorio para el número principal.
5. Comparación secundaria con `pytdc` y `get_split(method='scaffold')`.
6. Validación externa con el conjunto de Spielvogel et al. desde OSF.
7. **Licencias**: se pueden commitear los TSV de B3DB (CC0). **No** commitear los archivos crudos de TDC ni LightBBB sin resolver su estatus; en el caso de TDC, llamar al loader en tiempo de ejecución (solo código, MIT).

## Lo que no se pudo verificar

- **El conteo actual real de B3DB**: 7,807 contra 7,982. Discrepancia real, dependiente de versión.
- **Métricas reportadas de B3clf**: el PDF en ChemRxiv devolvió 403 en todos los intentos.
- **Balance de clases exacto de TDC BBB_Martins**: no aparece en las páginas leídas; deliberadamente no se estimó.
- **Licencia de datos de TDC para este dataset**: el sitio dice "Not Specified". Sin resolver.
- **Protocolo de split de LightBBB** (aleatorio o scaffold): no encontrado. No hay repo ni paquete, solo material suplementario.
- **Deo, Theil y Nicolas (2013)**, *Molecular Pharmaceutics* 10(5):1581–1595 — el paper cuyo título aborda más directamente la preocupación de los asesores ("Confounding Parameters in Preclinical Assessment of Blood–Brain Barrier Permeation"). Tras muro de pago, sin ruta abierta tras revisar PubMed, CrossRef y ResearchGate. **Recomendado: conseguirlo con el acceso institucional del Tec.**
- **La saturación del eflujo de P-gp cerca de 1 µM**: corroborada solo vía abstract indexado, no fuente primaria.
- **Texto completo de MoleculeNet (Wu et al. 2018)**: RSC devolvió 403; solo se confirmaron metadatos vía CrossRef.
- **Volumen y páginas finales de Schuh et al. (2026)**: publicación anticipada en línea, sin asignar. Reverificar al redactar.
- **La cifra de "1,965 moléculas válidas" de BBBP**: de resúmenes indexados, no de fuente primaria.
