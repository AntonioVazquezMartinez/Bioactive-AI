# Los datos del proyecto: contenido, defectos y linaje

Qué contiene cada archivo que entregó la patrocinadora, qué defectos se conocen y cómo llega cada número a la matriz del modelo. Reúne en un solo lugar lo que dicen los dos diccionarios de la patrocinadora y lo que el equipo midió por su cuenta.

**Las cifras de identidad y de defectos coinciden con nuestro cálculo independiente desde el CSV con RDKit**, lo que sirve como verificación cruzada en ambos sentidos. Los originales: [permeabilidad BBB](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_permeabilidad_bbb.pdf) y [actividad en SNC](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_actividad_snc.pdf). De dónde viene cada fuente y bajo qué licencia, en [procedencia y licencias](../data/external/README.md); si un término no se entiende, el [glosario](glosario.md).

## De la fuente a la matriz del modelo

```{mermaid}
flowchart TD
    subgraph fuentes["Datos de la patrocinadora"]
        BBB["bbb_permeability_experimental.csv<br/>7,811 filas · deriva de B3DB<br/>cruzado con COCONUT"]
        SNC["snc_activity_…_Entrenamiento.csv<br/>202,647 registros · ChEMBL + NPASS + CMAUP"]
        DIA["etiquetas_dianas.csv<br/>39 dianas con gen y enfermedad"]
    end

    subgraph e1["Etapa 1 · permeabilidad"]
        B1["7,805 con clase asignada<br/>6 filas sin clase se excluyen"]
        B2["4,018 esqueletos de conectividad<br/>el tamaño efectivo, no 7,805"]
        B3["217 descriptores RDKit → 203 utilizables<br/>más ECFP4 de 2,048 bits"]
        B4["Partición por andamio<br/>5,557 / 749 / 1,499 · sin fuga"]
    end

    subgraph e2["Etapa 2 · actividad"]
        S1["114,549 registros con categoría de diana<br/>109,264 etiquetados · 88,098 fenotípicos aparte"]
        S2["99,585 esqueletos de conectividad"]
        S3["Cohorte descriptiva previa a partición<br/>71,145 pares · regla provisional"]
    end

    BBB --> B1 --> B2 --> B3 --> B4
    SNC --> S1 --> S2 --> S3
    DIA --> S1
    B4 --> M["Modelo etapa 1"]
    S3 -. "tras resolver discordancias<br/>y definir la partición" .-> N["Modelo etapa 2"]
    M --> P["Priorización con atribución<br/>a fragmentos"]
    N --> P
    B2 -. "solo 1,033 esqueletos<br/>en ambos conjuntos" .- S2
```

La línea punteada es el hallazgo del [EDA de la etapa 2](../notebooks/01b_EDA_actividad_snc.ipynb): los dos conjuntos **casi no comparten compuestos**. Solo 1,033 esqueletos tienen medición en ambos, el 1.0% del conjunto de actividad y el 25.7% del de permeabilidad. Por eso la etapa 1 no opera como filtro duro: para el 99% de los esqueletos con actividad no hay permeabilidad medida, y filtrar con una predicción sin verificar eliminaría candidatos con actividad documentada. Es también el único subconjunto donde se puede comprobar contra datos reales si combinar las dos predicciones ayuda. El diccionario dice que las dos tablas son independientes y no hace falta cruzarlas: es cierto a nivel de filas, pero no contempla este uso, que motiva la [decisión C.3](decisiones.md#dc-3).

## Etapa 1 · permeabilidad

Todo viene de B3DB. El único añadido de la patrocinadora es la estructura estandarizada, el esqueleto de conectividad precalculado y el cruce con COCONUT, y reúne la clasificación y la regresión en un solo archivo.

| Dato | Valor |
|:--|--:|
| Filas totales | 7,811 (7,805 con clase asignada) |
| BBB+ / BBB− | 4,956 (63.5%) / 2,849 (36.5%) |
| Con valor numérico de logBB (en las 7,805) | 1,052 |
| Esqueletos de conectividad distintos | **4,018** en las 7,805 filas con clase; 4,019 en las 7,811 |
| Producto natural exacto en COCONUT | 3,366 filas |

**El tamaño efectivo es el número de esqueletos, no el de filas.** Casi la mitad de las filas repiten un esqueleto ya presente (la misma molécula base, medida o escrita de otra forma), así que 7,805 sobreestima cuánta información independiente hay. Al reportar el tamaño del conjunto se dan siempre las dos cifras. La diferencia entre 4,018 y 4,019 es un esqueleto que solo aparece entre las seis filas sin clase.

### Identidad

El archivo trae 7,808 InChIKey distintos sobre 7,811 filas: **3 se repiten** —ampicilina con sultamicilina, colestipol, probenecid— y en los tres casos ambas filas coinciden en la clase.

**Los nombres no son identificadores.** Hay una fila llamada «ritonavir» cuya estructura es etambutol sin estereoquímica: cinco filas con ese nombre y cuatro esqueletos distintos. El identificador es `inchikey` o `smiles_std`, recalculado, nunca el nombre ni el texto del SMILES.

### Las categorías A–D

B3DB dice que caracterizan la incertidumbre de las mediciones, pero no publica el criterio. El diccionario lo examina sobre los datos y concluye:

> *No es una escala de calidad A > B > C > D. En clasificación el grupo indica de qué tipo de dato salió la etiqueta. En regresión indica cuántas mediciones independientes hay, y ahí el grupo A es el de menos respaldo, con una sola medida.*
>
> *Filtrar «solo A» no tiene respaldo documentado.*

| Grupo | Filas | Qué indica en clasificación | % BBB− |
|:--|--:|:--|--:|
| A | 1,058 | Tienen logBB numérico (1,052 de ellas en las 7,805) | 12.1% |
| B | 3,621 | Las fuentes declararon el umbral −1 y coincidieron | 31.3% |
| C | 3,075 | Coinciden en la etiqueta, sin declarar umbral; mediana de **una** referencia | 50.0% |
| D | 51 | Igual que C, pero con mediana de **tres** referencias: más respaldo, **no** etiquetas contradictorias | 92.2% |

Al revisar los duplicados exactos del archivo, ninguno tiene etiquetas en conflicto. Las dos columnas de grupo, clasificación y regresión, **no son comparables entre sí**: los 1,058 compuestos presentes en ambos archivos son todos grupo A en clasificación, pero en regresión se reparten entre los cuatro y difieren en el **77%** de los casos.

**No se filtra por grupo**: quedarse con A+B baja la clase BBB− del 36.5% al 27.0%, así que se usa para describir y estratificar. El razonamiento completo está en la [decisión 1.1](decisiones.md#d1-1).

### Origen natural

El diccionario distingue tres categorías, no dos:

| | Compuestos |
|:--|--:|
| Producto natural exacto, estereoquímica incluida | 3,366 |
| Análogo que difiere solo en estereoquímica | 1,005 |
| Sin equivalente natural conocido | 3,440 |

Toda cifra por origen debe declarar cuál usa y sobre qué base: las tres categorías cuentan sobre las 7,811 filas, y las comparaciones de abajo sobre las 7,805 con clase, por eso 1,005 + 3,440 = 4,445 y no 4,439. La alerta PAINS da 7.5% contra 3.6% con coincidencia exacta, y 6.9% contra 3.2% por esqueleto.

**Los productos naturales cruzan la barrera menos.**

| Grupo | Compuestos | % BBB+ |
|:--|--:|--:|
| Sin equivalente natural exacto (incluye análogos, así que no todos son sintéticos en sentido estricto) | 4,439 | 71.7% |
| **Productos naturales** (estructura idéntica en COCONUT) | **3,366** | **52.7%** |

La diferencia es de 19 puntos, y la regla fisicoquímica clásica (TPSA < 67 Å² y HBD ≤ 1) explica unos 6.6. Queda algo más en juego —posiblemente eflujo activo, o un sesgo en qué compuestos se han llegado a ensayar— que el modelo tendrá que poder capturar. Como los naturales son justo lo que el proyecto quiere priorizar, **el desempeño se reporta por separado para naturales y sintéticos**: un buen número global podría esconder que le va peor justo ahí.

### Reglas fisicoquímicas sobre nuestros datos

El umbral clásico de TPSA es ≤ 90 Å². La literatura reporta un óptimo más estricto, **66.8 Å²**, y una regla de dos condiciones, **TPSA < 67 Å² y HBD ≤ 1**, con 96.6% de precisión para BBB+. Verificada sobre los datos de este proyecto (Avance 1):

| Conjunto | Regla TPSA < 67 Å² y HBD ≤ 1 | Lectura |
|:--|:--|:--|
| Grupo A (subconjunto con logBB, el de la literatura) | precisión 0.966 · sensibilidad 0.589 · AUC 0.720 | reproduce la cifra publicada, pero solo marca como BBB+ al 54% de los compuestos |
| Conjunto completo (7,805) | precisión 0.853 · sensibilidad 0.515 · AUC 0.680 | el AUC queda por debajo de TPSA < 90 Å² (0.729) y de TPSA < 67 Å² sola (0.701) |

La regla es muy precisa cuando acierta, pero **no supera a las alternativas simples en todo el conjunto**: sirve como referencia obligatoria y como verificación de las explicaciones del modelo, no como modelo ganador. Y el umbral óptimo **no es una constante**: cambia con el subconjunto que lo calcula, 66.6 Å² en el grupo A, 83.6 en A+B, 101.9 en el conjunto completo y 107.0 solo con entrenamiento (Avance 2), y aún no tiene intervalos de confianza. Hay que decir siempre sobre qué datos se calculó.

### Por qué la partición agrupa por andamio

En nuestros datos la misma molécula base aparece repetida: la morfina está **ocho veces**, como estereoisómeros distintos o con nombres distintos. Y hay grupos enteros que comparten andamio y casi siempre la misma etiqueta: uno de 410 compuestos es 99.5% BBB+. Con una partición aleatoria, el modelo solo necesitaría reconocer el andamio, sin aprender la relación real entre estructura y permeabilidad, y nadie lo notaría.

### Defectos conocidos

- **2 compuestos de B3DB no sobreviven**: mepenzolato y tiotidina, con un carbono de carga imposible que RDKit rechaza. La patrocinadora ya los excluyó, de modo que los 7,811 SMILES de su archivo son válidos. Solo aparecen en los archivos crudos de B3DB.
- **6 filas traen logBB sin clase** —zidovudina, miltefosina y otras cuatro—: tienen clase en B3DB, pero su fila de clasificación registra otra forma estereoquímica y no empató al unir. Se excluyen del entrenamiento de clasificación ([decisión 1.4](decisiones.md#d1-4)).
- **131 esqueletos tienen clases contradictorias**, que afectan 429 filas. El ejemplo del diccionario: el meso-etambutol es BBB+ y los demás isómeros, BBB−. Hay que decidir si es un caso genuino de «la forma exacta importa» o un error de etiquetado.
- **112 esqueletos tienen más de una medición de logBB**, y de ellos **40 con valores distintos**, con diferencias de hasta 1.4 unidades logarítmicas. El diccionario dice «más de un valor», pero 72 de los 112 repiten el mismo número: el desacuerdo real es 2.8 veces menor de lo que sugiere la cifra.

Los dos últimos ponen un **límite teórico** a cualquier modelo que agrupe por esqueleto: si dos estereoisómeros comparten estructura y llevan etiquetas opuestas, ninguno acierta ambas. Para las 131 clases contradictorias el mínimo de errores inevitables es de **151 compuestos sobre 7,805**, un techo de exactitud del **98.1%** que no restringe a ningún modelo realista. Para el logBB el efecto no está cuantificado.

## Etapa 2 · actividad en el sistema nervioso

El archivo (`snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv`) combina tres fuentes: **ChEMBL** (bioactividad de moléculas tipo fármaco), **NPASS** y **CMAUP** (productos naturales). Pesa 74 MB y se versiona con Git LFS.

> **Archivo completo y archivo recibido.** El diccionario describe **225,513 registros**; recibimos **202,647**, el 89.9%. El sufijo `_Entrenamiento` y esa diferencia indican que existe una partición reservada, [pendiente de confirmar](decisiones.md#d2-6). Las cifras del diccionario son del archivo completo y las del resto del sitio son del nuestro: 114,549 registros con diana en vez de 121,522, y 88,098 sin diana en vez de 98,298. Cada cifra declara cuál usa.

| Dato (archivo recibido) | Valor |
|:--|--:|
| Registros de actividad (cada fila es una *medición*, no un compuesto distinto) | 202,647 |
| Compuestos únicos (por InChIKey) | 105,583 |
| De ChEMBL | 103,877 |
| De NPASS y CMAUP (productos naturales) | 4,472 |
| En ambos grupos a la vez | 2,766 |
| Registros con pChEMBL | 129,243 |
| Registros de inactividad declarada | 29,730 |

### Las dianas

**37 dianas identificadas por gen** con 121,522 filas en el archivo completo, más dos receptores completos —NMDA y GABA-A— que ChEMBL registra sin especificar subunidad, con 3,112. Las 39 filas del archivo de etiquetas se curaron **a mano** desde la farmacología conocida, no vienen de las bases: la categoría es la enfermedad con más respaldo (fármaco aprobado primero, luego evidencia genética o investigación clínica) y describe la intención terapéutica, no necesariamente lo que ocurrió en cada ensayo. Se agrupan en SNC clásico (20), neuroinflamación (10), Parkinson / ELA / Huntington (7) y receptores completos (2).

La cobertura es muy desigual: Alzheimer reúne 52,676 registros y ELA solo 53. Cuatro dianas no sostienen un modelo propio:

| Gen | Diana | Filas |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | 0 |
| `AIF1` | Iba1, marcador sin dirección de efecto | 0 |
| `GABRB2` | Receptor GABA-A, subunidad β2 | 1 |
| `TARDBP` | TDP-43 | 8 en el archivo completo |

El **43.5% de las filas (88,098)** no corresponde a ninguna diana de la lista (44% en el archivo completo, 98,298): entraron por la ruta `neuronal_assay`, ensayos fenotípicos sobre sistemas celulares neuronales donde se midió un efecto sin identificar la proteína. Qué hacer con ellas es la [decisión 2.4](decisiones.md#d2-4).

### Cómo se mide la actividad

- **NPASS y CMAUP no traen pChEMBL** (15,293 registros), porque solo ChEMBL lo calcula. Etiquetar solo por pChEMBL dejaría fuera justo los productos naturales, de ahí el etiquetado por tres vías de la [decisión 2.3](decisiones.md#d2-3), pendiente de ratificar.
- **Las unidades no están convertidas a una sola escala**: la mayoría está en nM, pero hay 29,880 registros en µM y 662 en unidades de masa (µg/mL y similares) que no se pueden pasar a concentración molar sin el peso molecular de cada compuesto.
- **Las mediciones censuradas** dicen «mayor a 10 µM» en vez de dar un número: es un límite inferior, y **solo sirve como negativo si el límite es igual o mayor que el umbral de «activo» que se use**. Sobre las 61,001 filas con `>` o `>=` (54,498 de ellas sin pChEMBL):

Con un umbral de 1 µM el 98% de esas filas son negativos seguros; con 10 µM, el 89%; con 100 µM, solo el 12% (la tabla completa está en la [decisión 2.3](decisiones.md#d2-3)). Cuanto más estricto el umbral, más censurados se recuperan: con 1 µM (pChEMBL ≥ 6) se obtienen **5,440 negativos más** que con 10 µM. En regresión no deben usarse como valores exactos. De las 41,291 filas con límite de 10 µM, **33,574 vienen de DrugMatrix**: una sola fuente concentra la mayor parte de la evidencia censurada.

### Qué denominador usa cada porcentaje

Los porcentajes de actividad dependen de la unidad: **61.7%** con pChEMBL ≥ 5 corresponde a 119,835 activos entre 194,086 registros etiquetados e incluye ensayos fenotípicos. Para los **71,145 pares únicos de esqueleto de conectividad × gen**, el recuento exploratorio da **70.5%** (50,177 pares activos) al clasificar como activo un par con al menos una observación activa. No son el mismo denominador, y la primera cifra no describe el conjunto por diana. Esa agrupación no es un andamio Bemis–Murcko, cuenta como activos pares con observaciones discordantes y todavía debe revisarse; la cohorte también está pendiente de partición. Los conteos de ambos umbrales y las exclusiones están en la [decisión 2.3](decisiones.md#d2-3) y se calculan en el [EDA de actividad SNC](../notebooks/01b_EDA_actividad_snc.ipynb).

## Lo que los diccionarios no documentan

- Si los `Not active` declarados por texto son negativos confiables.
- Qué criterio de «activo» usa la patrocinadora.
- Si existe una partición de prueba reservada, y cómo se construyó.
- Qué error pesa más en el laboratorio.

Son parte de la [ruta del proyecto](decisiones.md#fase2).
