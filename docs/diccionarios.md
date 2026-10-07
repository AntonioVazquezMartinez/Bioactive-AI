# Lo que dicen los diccionarios de la patrocinadora

La patrocinadora entregó dos diccionarios en PDF junto con los datos, el 25 de septiembre. **No se leyeron a fondo hasta el 7 de octubre**, y en ese tiempo el equipo rehízo por su cuenta análisis que ya estaban ahí.

Este documento reconcilia las dos fuentes: qué dice cada diccionario, qué medimos nosotros, dónde coinciden y dónde ella tiene más. Existe para que no vuelva a pasar, y para no preguntarle cosas que ya nos respondió.

Los originales están en el repositorio: [permeabilidad BBB](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_permeabilidad_bbb.pdf) y [actividad en SNC](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_actividad_snc.pdf).

## Lo que confirmó que medimos bien

En estos puntos nuestras cifras y las suyas coinciden exactamente. Vale como verificación cruzada independiente: ella las calculó sobre el archivo completo, nosotros desde el CSV con RDKit.

| Lo que medimos | Nosotros | El diccionario |
|:--|:--|:--|
| Esqueletos de conectividad en permeabilidad | 4,018 etiquetados | 4,019 en las 7,811 filas |
| Duplicados por InChIKey completo | 3 pares, misma clase | 3, y los nombra: ampicilina/sultamicilina, colestipol, probenecid |
| Esqueletos con clases contradictorias | 131, que afectan 429 filas | 131 y 429 |
| SMILES inválidos en el B3DB crudo | 2, con `[C+]` imposible | 2, y los nombra: mepenzolato y tiotidina |
| Filas con logBB pero sin clase | 6 | 6, y las nombra: zidovudina, miltefosina y otras cuatro |
| Umbral `b3db_threshold` | −1.0 donde está presente | −1.0 en 3,621 filas |

## Lo que ella ya sabía y nosotros presentamos como hallazgo

### Las categorías A–D no son una escala de calidad

El Avance 1 lo presentó como resultado del EDA. **El diccionario ya lo dice**, y con más detalle del que nosotros teníamos:

> *No es una escala de calidad A > B > C > D. En clasificación el grupo indica de qué tipo de dato salió la etiqueta. En regresión indica cuántas mediciones independientes hay, y ahí el grupo A es el de menos respaldo, con una sola medida.*
>
> *Filtrar «solo A» no tiene respaldo documentado.*

El reporte del Avance 1 sí la acredita en dos lugares, pero el encuadre general lo presenta como descubrimiento propio. **Lo que sí aportamos de nuevo es la cuantificación**: que filtrar a A+B baja la clase minoritaria del 36.5% al 27.0%. Eso no está en el diccionario.

Y ella tiene una observación que nosotros no hicimos: **las columnas de clasificación y de regresión no son comparables entre sí.** Los 1,058 compuestos presentes en ambos archivos son todos grupo A en clasificación, pero en regresión se reparten entre los cuatro grupos y **difieren en el 77% de los casos**. Por eso se guardan separadas y nunca se promedian.

### El criterio para las mediciones censuradas

Estuvimos a punto de proponerle un corte de 10 µM derivado por nosotros. **La sección 7 de su diccionario ya trae la tabla hecha**, sobre las 61,001 filas con `>` o `>=`:

| Umbral de «activo» | Negativos seguros | Ambiguos |
|:--|--:|--:|
| 1 µM | 59,859 (98%) | 1,142 |
| 10 µM | 54,419 (89%) | 6,582 |
| 100 µM | 7,474 (12%) | 53,527 |

Con la regla explícita: *«solo sirve como negativo si el límite es igual o mayor que el umbral de "activo" que se use»*, y la advertencia de que *«en regresión no deben usarse como si el valor fuera exacto: se excluyen o se usa un método para valores censurados»*.

**Esto corrige nuestra propuesta.** Nuestro corte de 10 µM recupera el 89% de los censurados como negativos seguros; con un umbral de 1 µM —que corresponde a pChEMBL ≥ 6— se recupera el 98%. Es un argumento a favor de ≥ 6 que no teníamos, y es suyo.

También documenta que **33,574 de las 41,291 filas con límite de 10 µM vienen de DrugMatrix**, una sola fuente. Eso concentra la evidencia censurada y es relevante para el riesgo de sesgo por fuente.

## Lo que no habíamos usado

### Los nombres de compuesto no son de fiar

> *En B3DB hay una fila llamada «ritonavir» cuya estructura es en realidad etambutol sin estereoquímica. Usa siempre `inchikey` o `smiles_std` como identificador, nunca `compound_name`.*

Verificado: hay cinco filas llamadas «ritonavir» con cuatro esqueletos distintos, y uno de ellos coincide con el del etambutol. Nuestro pipeline ya identifica por estructura, así que no hay error, pero `compound_name` viaja en los metadatos del Avance 2 y **no debe usarse para agrupar ni para unir**.

### Hay tres categorías de origen natural, no dos

Hemos trabajado con una división binaria desde la coincidencia exacta con COCONUT. El diccionario distingue tres:

| | Compuestos |
|:--|--:|
| Producto natural exacto, estereoquímica incluida | 3,366 |
| **Análogo natural que difiere solo en estereoquímica** | **1,005** |
| Sin equivalente natural conocido | 3,440 |

Los 1,005 intermedios no son sintéticos. Al reportar la brecha de permeabilidad por origen hay que decir qué definición se usó: con coincidencia exacta la alerta PAINS da 7.5% contra 3.6%, y con coincidencia por esqueleto 6.9% contra 3.2%.

### 112 esqueletos tienen más de un valor de logBB

Con diferencias de hasta **1.4 unidades logarítmicas** entre isómeros del mismo esqueleto. Es el equivalente continuo de las 131 clases contradictorias, y pone un techo a cualquier modelo de regresión sobre logBB agrupado por esqueleto.

### Son 37 dianas, no 39

El archivo `etiquetas_dianas` tiene 39 filas, pero el diccionario distingue:

- **37 dianas** identificadas por gen, con 121,522 filas en el archivo completo.
- **2 receptores completos** —NMDA y GABA-A— que ChEMBL registra sin especificar subunidad: 3,112 filas.
- Más 2,581 filas etiquetadas por nombre de diana, casi siempre en rata o ratón.

**Dos dianas de la lista tienen cero filas**: `GABRG2` (receptor GABA-A subunidad γ2) e `AIF1` (Iba1, que el propio diccionario marca como «marcador», sin dirección de efecto). `GABRB2` tiene 1 fila y `TARDBP` 8.

### Cómo se curaron las etiquetas de diana

> *Curadas a mano a partir de la farmacología conocida; no vienen de las bases de datos. La categoría principal es la enfermedad con más respaldo para esa diana (fármaco aprobado; si no lo hay, evidencia genética o investigación clínica), o el proceso cuando la diana es común a varias enfermedades.*

Responde por qué una diana está en una categoría y no en otra, que era una de nuestras preguntas abiertas.

## Lo que el diccionario afirma y conviene matizar

> *Es una tabla independiente de la de actividad en SNC: no comparten filas ni hace falta cruzarlas.*

Es cierto a nivel de filas: son dos tablas con esquemas distintos y no hay que unirlas para trabajar. Pero **sí comparten compuestos**, y eso importa para el pipeline de dos etapas: 1,033 esqueletos tienen medición en ambas, el 1.0% del conjunto de actividad y el 25.7% del de permeabilidad.

Es el único subconjunto donde se puede medir la cadena completa de extremo a extremo. No contradice al diccionario —ella habla de cómo usar las tablas, no de validar el encadenamiento— pero es un uso que su nota no contempla y conviene plantearlo así al consultarla.

## Lo que sigue sin responder

El diccionario no cubre, y por tanto sí hay que preguntar:

- Si los `Not active` declarados por texto son negativos confiables.
- Qué criterio de «activo» usa ella, más allá de cómo tratar los censurados.
- La forma del modelo de la etapa 2: por diana, por categoría o multitarea.
- Si existe una partición de prueba ya reservada. El diccionario describe 225,513 filas y recibimos 202,647, el **89.9%**, lo que sugiere que sí.
- Qué error pesa más en el laboratorio y cómo presentar el ranking.
- Si el proyecto tiene aspiraciones comerciales, por la licencia CC BY-NC de NPASS.
