# Lo que documentan los diccionarios

La patrocinadora entregó dos diccionarios en PDF junto con los datos. Esta página recoge lo que establecen sobre cada conjunto, con las cifras que verificamos de forma independiente y las que corrigen nuestro trabajo.

Los originales: [permeabilidad BBB](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_permeabilidad_bbb.pdf) y [actividad en SNC](https://github.com/AntonioVazquezMartinez/Bioactive-AI/blob/main/data/external/profesora/DICCIONARIO_actividad_snc.pdf).

## Permeabilidad · 7,811 compuestos

Todo viene de B3DB. El único añadido de la patrocinadora es la estructura estandarizada y el cruce con COCONUT.

### Identidad

El archivo trae 7,808 InChIKey distintos sobre 7,811 filas: **3 se repiten** —ampicilina con sultamicilina, colestipol, probenecid— y en los tres casos ambas filas coinciden en la clase. Ignorando estereoquímica quedan **4,019 esqueletos**, así que varios estereoisómeros comparten estructura.

**Los nombres no son identificadores.** Hay una fila llamada «ritonavir» cuya estructura es etambutol sin estereoquímica. Verificado: cinco filas con ese nombre y cuatro esqueletos distintos. El identificador es `inchikey` o `smiles_std`.

### Las categorías A–D

B3DB dice que caracterizan la incertidumbre de las mediciones, pero no publica el criterio. El diccionario lo examina sobre los datos y concluye:

> *No es una escala de calidad A > B > C > D. En clasificación el grupo indica de qué tipo de dato salió la etiqueta. En regresión indica cuántas mediciones independientes hay, y ahí el grupo A es el de menos respaldo, con una sola medida.*
>
> *Filtrar «solo A» no tiene respaldo documentado.*

Las dos columnas de grupo —clasificación y regresión— **no son comparables entre sí**: los 1,058 compuestos presentes en ambos archivos son todos grupo A en clasificación, pero en regresión se reparten entre los cuatro y difieren en el **77%** de los casos.

El [EDA del Avance 1](../notebooks/01_EDA.ipynb) añade la cuantificación: filtrar a A+B baja la clase minoritaria del 36.5% al 27.0%.

### Origen natural

Tres categorías, no dos:

| | Compuestos |
|:--|--:|
| Producto natural exacto, estereoquímica incluida | 3,366 |
| Análogo que difiere solo en estereoquímica | 1,005 |
| Sin equivalente natural conocido | 3,440 |

Toda cifra por origen debe declarar cuál usa. La alerta PAINS da 7.5% contra 3.6% con coincidencia exacta, y 6.9% contra 3.2% por esqueleto.

### Defectos conocidos

- **2 compuestos de B3DB no sobreviven**: mepenzolato y tiotidina, con un carbono de carga imposible que RDKit rechaza.
- **6 filas traen logBB sin clase** —zidovudina, miltefosina y otras cuatro—: tienen clase en B3DB, pero su fila de clasificación registra otra forma estereoquímica y no empató al unir.
- **131 esqueletos tienen clases contradictorias**, que afectan 429 filas. El ejemplo que da: el meso-etambutol es BBB+ y los demás isómeros, BBB−.
- **112 esqueletos tienen más de un valor de logBB**, con diferencias de hasta 1.4 unidades logarítmicas.

Los dos últimos ponen un techo a cualquier modelo que agrupe por esqueleto: si la etiqueta es contradictoria, ninguno acierta las dos.

## Actividad en SNC · 225,513 registros

Recibimos 202,647, el **89.9%**. El sufijo `_Entrenamiento` y esa diferencia indican que existe una partición reservada, lo cual está [pendiente de confirmar](consulta-patrocinadora.md).

### Mediciones censuradas

Un `>` significa que el ensayo llegó hasta esa concentración sin alcanzar el 50% de efecto. Es un límite inferior, no un valor, y **solo sirve como negativo si el límite es igual o mayor que el umbral de «activo» que se use**.

Sobre las 61,001 filas con `>` o `>=`:

| Umbral de «activo» | Negativos seguros | Ambiguos |
|:--|--:|--:|
| 1 µM | 59,859 (98%) | 1,142 |
| 10 µM | 54,419 (89%) | 6,582 |
| 100 µM | 7,474 (12%) | 53,527 |

Cuanto más estricto el umbral de actividad, más censurados se recuperan. Con 1 µM —pChEMBL ≥ 6— se obtienen **5,440 negativos más** que con 10 µM, que era el corte que el equipo había propuesto. En regresión no deben usarse como valores exactos.

De las 41,291 filas con límite de 10 µM, **33,574 vienen de DrugMatrix**: una sola fuente concentra la mayor parte de la evidencia censurada.

### Las dianas

**37 dianas identificadas por gen** con 121,522 filas, más dos receptores completos —NMDA y GABA-A— que ChEMBL registra sin especificar subunidad, con 3,112. El archivo de etiquetas tiene 39 filas porque incluye esos dos.

Las etiquetas se curaron a mano desde la farmacología conocida, no vienen de las bases: la categoría es la enfermedad con más respaldo —fármaco aprobado primero, luego evidencia genética o investigación clínica.

Cuatro no sostienen un modelo propio:

| Gen | Diana | Filas |
|:--|:--|--:|
| `GABRG2` | Receptor GABA-A, subunidad γ2 | 0 |
| `AIF1` | Iba1, marcador sin dirección de efecto | 0 |
| `GABRB2` | Receptor GABA-A, subunidad β2 | 1 |
| `TARDBP` | TDP-43 | 8 |

**98,298 filas (44%)** no corresponden a ninguna diana de la lista: vienen de la vía neuronal, con dianas fuera del alcance o que ChEMBL no identifica.

## Lo que no documentan

- Si los `Not active` declarados por texto son negativos confiables.
- Qué criterio de «activo» usa la patrocinadora.
- Si existe una partición de prueba reservada, y cómo se construyó.
- Qué error pesa más en el laboratorio.

Son parte de la [consulta](consulta-patrocinadora.md).

## Una nota sobre el cruce entre conjuntos

> *Es una tabla independiente de la de actividad en SNC: no comparten filas ni hace falta cruzarlas.*

Cierto a nivel de filas. Pero **1,033 esqueletos aparecen en ambos conjuntos** —el 1.0% del de actividad, el 25.7% del de permeabilidad— y son el único subconjunto donde la cadena de dos etapas se puede validar de extremo a extremo. Es un uso que la nota no contempla, y que motiva la [decisión 10](decisiones.md#d10).
