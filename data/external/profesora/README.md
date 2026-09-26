# Datos entregados por la patrocinadora

Recibidos el 2026-09-25 de la Dra. Mariana Martínez Ávila, en la carpeta *Archivos Iniciales*. **Son la fuente autoritativa del proyecto**; los archivos de [`../b3db/`](../b3db/) quedan como referencia de procedencia.

## Contenido

| Archivo | Tamaño | Qué es |
|---|---|---|
| `bbb_permeability_experimental.csv` | 1.6 MB | Etapa 1: permeabilidad de la barrera hematoencefálica |
| `etiquetas_dianas_2026-09-25.csv` | 7 KB | Las 39 dianas moleculares, curadas a mano |
| `DICCIONARIO_permeabilidad_bbb.pdf` | 106 KB | Diccionario de columnas del primero |
| `DICCIONARIO_actividad_snc.pdf` | 118 KB | Diccionario de columnas del conjunto de actividad |
| `snc_activity_crudo_v3_final_2026-09-25_Entrenamiento.csv` | **74 MB** | Etapa 2: actividad en SNC. Versionado con **Git LFS**, ver abajo |

**Lean los diccionarios antes de tocar los datos.** Documentan la procedencia columna por columna y varios problemas de calidad que no son evidentes.

## El archivo de actividad usa Git LFS

Pesa 74 MB, por encima de lo que conviene guardar directamente en git. Se versiona con [Git LFS](https://git-lfs.com), que deja un puntero de 74 bytes en el historial y guarda el contenido aparte.

**Hay que instalar LFS antes de clonar el repositorio**, o el archivo llegará como un puntero de texto en vez de los datos:

```bash
brew install git-lfs      # macOS; en Linux: apt install git-lfs
git lfs install           # una sola vez por máquina
git clone https://github.com/AntonioVazquezMartinez/Bioactive-AI.git
```

Si ya clonaron sin LFS instalado:

```bash
git lfs install
git lfs pull
```

Para comprobar que el archivo bajó completo y no es un puntero:

```bash
head -c 100 data/external/profesora/snc_activity_*.csv
# debe verse el encabezado del CSV, no "version https://git-lfs.github.com/..."
```

> **Cuota:** GitHub da 1 GB de almacenamiento y 1 GB de ancho de banda al mes en LFS para cuentas gratuitas. Este archivo consume 74 MB de almacenamiento, y cada clon completo gasta 74 MB de ancho de banda. Con un equipo de tres no hay problema, pero conviene no agregar muchos archivos pesados más sin revisar la cuota.

## Qué aporta sobre lo que ya teníamos

El archivo de permeabilidad deriva de B3DB, igual que [`../b3db/`](../b3db/), pero viene procesado:

- **SMILES estandarizados** con RDKit: sal retirada, cargas neutralizadas, tautómero canónico.
- **`key14` precalculado**, el esqueleto de conectividad sin estereoquímica.
- **Cruce con COCONUT**: 4,371 filas tienen equivalente en el catálogo de productos naturales, lo que permite separar naturales de sintéticos sin integrar COCONUT nosotros.
- **Clasificación y regresión unidas** por estructura: 1,058 filas traen `logbb` numérico.

Tiene 7,811 filas contra las 7,807 del archivo original de clasificación, porque incorpora también el archivo de regresión.

> **Diferencia de conteo:** el archivo de la patrocinadora reporta 2,849 compuestos BBB− y el original 2,851. La diferencia son 2 filas que el original tiene y este no: los compuestos con SMILES inválido, que RDKit rechaza. El diccionario lo documenta en su sección 7.

## Licencias

| Fuente | Licencia | Implicación |
|---|---|---|
| B3DB | CC0 | Sin restricción |
| COCONUT | CC0 | Sin restricción |
| ChEMBL | CC BY-SA 3.0 | Requiere atribución; las obras derivadas comparten licencia |
| **NPASS** | **CC BY-NC 4.0** | **No comercial.** Permite uso y redistribución académica con atribución |
| CMAUP | CC BY (del artículo) | Términos de la base sin confirmar |

> **A tener presente:** el conjunto de actividad mezcla fuentes, y NPASS impone la restricción **no comercial**. Un repositorio académico público cumple, pero si el proyecto tuviera continuidad comercial habría que revisarlo. Conviene comentarlo con la patrocinadora.

## Advertencias de calidad, verificadas

Confirmadas contra los datos, no tomadas del diccionario:

- **El tamaño efectivo es menor que el número de filas.** 7,805 filas con clase corresponden a 4,019 esqueletos de conectividad. La morfina aparece ocho veces.
- **Dos SMILES del B3DB original no parsean** (mepenzolato y tiotidina, con `[C+](O)`). Ya vienen excluidos de este archivo.
- **Los nombres de compuesto no son confiables.** El diccionario documenta una fila llamada "ritonavir" cuya estructura es etambutol. Deduplicar siempre por `inchikey`, nunca por nombre.
- **131 esqueletos tienen clases contradictorias** entre estereoisómeros, afectando 429 filas.
- **Las columnas de grupo A–D no son una escala de calidad.** B3DB no publica el criterio; el grupo D tiene más respaldo bibliográfico que el C, y el grupo está correlacionado con la etiqueta, así que filtrar por él sesga la distribución de clases.

## Pendiente de confirmar con la patrocinadora

El diccionario describe un archivo de **225,513 filas**, y el que recibimos tiene **202,647** y se llama `_Entrenamiento`. Es el 89.9%, lo que sugiere que se reservó cerca de un 10% como conjunto de prueba.

Si es así, **no debemos construir nuestra propia partición de prueba para la etapa 2**, y conviene preguntar cómo se hizo la separación: si fue aleatoria, tendría el problema de fuga por andamio que documentamos en [`docs/referencias/02-datasets-bbb.md`](../../../docs/referencias/02-datasets-bbb.md).
