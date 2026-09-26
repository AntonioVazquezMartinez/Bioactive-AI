# Datos externos

> **Los datos autoritativos del proyecto son los de [`profesora/`](profesora/)**, entregados por la Dra. Martínez el 2026-09-25 con sus diccionarios de columnas. Lo que sigue son las descargas que hicimos antes, que quedan como referencia de procedencia y como fuente de los archivos que la patrocinadora no incluyó (el subconjunto de regresión y el de validación externa).

Descargados el 2026-09-24 con `python src/data_prep/download_data.py`. Ese script fija el commit de origen y reporta los SHA-256, así que la descarga es reproducible.

Los archivos ligeros están versionados en el repo. Los pesados están en `.gitignore` y se traen con `--extended`.

---

## B3DB — permeabilidad de la barrera hematoencefálica (etapa 1)

**Fuente:** [github.com/theochem/B3DB](https://github.com/theochem/B3DB), commit `75dab1cc607bb7a03f3de5c576cffd223e767844` (2025-09-10).
**Licencia de los datos: CC0** (dominio público). Por eso se pueden versionar aquí.
**Cita:** `meng2021b3db` en [`docs/referencias/bibliografia.bib`](../../docs/referencias/bibliografia.bib).

| Archivo | Filas | Contenido |
|---|---|---|
| `B3DB_classification.tsv` | **7,807** | Conjunto principal con etiquetas BBB+/BBB− |
| `B3DB_classification_external.tsv` | **175** | Compuestos agregados en agosto de 2025 |
| `B3DB_regression.tsv` | **1,058** | Subconjunto con logBB numérico |
| `B3DB_classification_extended.tsv.gz` | 7,807 | Igual que el principal, más descriptores mordred precalculados (68 MB) |
| `B3DB_regression_extended.tsv.gz` | 1,058 | Igual, con descriptores (8.7 MB) |

### Composición verificada del conjunto principal

Los conteos se midieron sobre el archivo descargado, no se tomaron del paper:

- **4,956 BBB+ (63.5%)** contra **2,851 BBB− (36.5%)**.
- **1,058** compuestos con logBB numérico.
- **Cero SMILES faltantes.**
- Columnas: `NO., compound_name, IUPAC_name, SMILES, CID, logBB, BBB+/BBB-, Inchi, threshold, reference, group, comments`.

**Distribución por grupo de confiabilidad** (la columna `group`, el motivo principal para elegir B3DB):

| Grupo | Compuestos | Significado |
|---|---|---|
| A | 1,058 | Tienen logBB numérico |
| B | 3,621 | Fuentes que declararon el umbral −1 y coincidieron |
| C | 3,077 | Coinciden en la etiqueta, sin declarar umbral |
| D | 51 | Etiquetas contradictorias entre fuentes |

Solo los 3,621 registros del grupo B declaran umbral en la columna `threshold`, todos −1.0. Los demás lo tienen vacío.

**Plan de uso:** entrenar con A+B (4,679 registros), usar C como aumentación, reservar D como conjunto diagnóstico de casos ambiguos.

### Aclaración sobre el conteo: 7,807 contra 7,982

El README de B3DB dice que el conjunto tiene 7,982 compuestos, mientras que el archivo principal tiene 7,807. **No es una discrepancia de versión.** Los 175 compuestos agregados en agosto de 2025 (171 BBB+ y 4 BBB−) están en un **archivo aparte**, `B3DB_classification_external.tsv`, y no se fusionaron al principal. 7,807 + 175 = 7,982.

> **Cuidado al concatenar:** hay **11 compuestos que aparecen en ambos archivos** (coincidencia exacta por InChI). Si se unen sin deduplicar, quedan 11 duplicados. El archivo externo tiene las mismas columnas que el principal.

---

## Spielvogel et al. 2025 — validación externa

**Fuente:** [OSF, proyecto cvhe9](https://osf.io/cvhe9/), archivo `BBB penetration database.csv`.
**Licencia: CC BY 4.0** — requiere atribución al reutilizarse.
**Cita:** `spielvogel2025standardized`.

154 compuestos marcados radiactivamente y evaluados *in vivo*. Su valor está en que **no fuerza una etiqueta binaria**: separa los sustratos de eflujo como clase propia, que es justo la ambigüedad por concentración que señalaron los asesores.

| Clase | Compuestos |
|---|---|
| positive | 68 |
| efflux | 44 |
| negative | 42 |

> **Limitación importante, verificada sobre el archivo: no trae columna de SMILES ni de InChI.** Son 26 columnas con el nombre del compuesto y 25 descriptores precalculados (MW, PSA, HBD, HBA, logP, logD, CNS MPO score, BBB score, entre otros).
>
> Para usarlo con un pipeline basado en SMILES hay que **resolver los 154 nombres a estructura**, por ejemplo vía PubChem. La resolución por nombre es propensa a errores con entradas como `Fluoroethyl-Carfentanilhydrochloride` o `SCH-23388hydrochloride`, así que conviene revisar a mano los que no resuelvan de forma limpia.
>
> El separador del CSV es **punto y coma**, no coma.

---

## Pendientes de descarga

No están aquí todavía. Ver [`docs/referencias/05-fuentes-de-datos.md`](../../docs/referencias/05-fuentes-de-datos.md).

- **ChEMBL 37** (dump SQLite, vía FTP de EBI) — necesario para la etapa 2. Es pesado; conviene bajarlo en segundo plano.
- **COCONUT 2.0** (CC0, CSV de ~191 MB) — amplía el universo de productos naturales. **Falta verificar si trae datos de actividad o solo estructuras.**
- **LOTUS** (CC BY 4.0, volcado de Zenodo, ~290 MB) — aporta la taxonomía organismo-compuesto.
- **NPASS v3.0** (CC BY-NC, no comercial) y **CMAUP 2.0** — actividad de productos naturales.
