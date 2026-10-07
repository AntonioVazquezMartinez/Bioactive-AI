# Linaje de datos y mapa de decisiones

Dos diagramas que responden preguntas distintas. El primero: de dónde sale cada número que entra al modelo. El segundo: qué documento de investigación sustenta cada decisión técnica, y cuáles se revisaron después.

Si algún término no se entiende, el [glosario](glosario.md) lo define.

## De la fuente a la matriz del modelo

```{mermaid}
flowchart TD
    subgraph fuentes["Datos entregados por la patrocinadora"]
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
        S1["114,549 con diana de la lista<br/>88,098 fenotípicos van aparte"]
        S2["99,585 esqueletos de conectividad"]
        S3["Etiquetado pendiente de fijar<br/>pChEMBL deja fuera 3 bloques"]
    end

    BBB --> B1 --> B2 --> B3 --> B4
    SNC --> S1 --> S2 --> S3
    DIA --> S1
    B4 --> M["Modelo etapa 1"]
    S3 --> N["Modelo etapa 2"]
    M --> P["Priorización con atribución<br/>a fragmentos"]
    N --> P
    B2 -. "solo 1,033 esqueletos<br/>en ambos conjuntos" .- S2
```

La línea punteada es el hallazgo del [EDA de la etapa 2](../notebooks/01b_EDA_actividad_snc.ipynb): los dos conjuntos **casi no comparten compuestos**. Solo 1,033 estructuras tienen medición en ambos, el 1.0% del conjunto de actividad. La cadena completa no se puede validar experimentalmente más que sobre ese subconjunto, y por eso la etapa 1 no opera como filtro duro.

## Qué documento sustenta cada decisión

```{mermaid}
flowchart LR
    R1["01 · Representaciones<br/>moleculares"]
    R2["02 · Datasets de BBB"]
    R3["03 · Explicabilidad"]
    R4["04 · Datos de<br/>neuroactividad"]
    R5["05 · Fuentes de datos"]

    A1["EDA Avance 1"]
    A2["EDA etapa 2"]

    D1["Descriptores RDKit<br/>+ ECFP4 2,048"]
    D2["Scaffold split<br/>nunca aleatorio"]
    D3["Dos métodos de<br/>atribución que coincidan"]
    D4["Fuente etapa 2:<br/>ChEMBL + NPASS + CMAUP"]
    D5["Fuente etapa 1:<br/>archivo de la patrocinadora"]
    D6["NO filtrar por grupo A–D"]
    D7["Etiquetado por tres vías<br/>umbral ≥ 5 confirmado"]

    R1 --> D1
    R2 --> D2
    R2 --> D5
    R3 --> D3
    R4 --> D4
    R5 --> D4
    R5 --> D5
    A1 --> D6
    A2 --> D7

    D6 -.->|"corrige"| R2
    D7 -.->|"corrige"| R4
```

Las flechas punteadas marcan las decisiones que **los datos revisaron después**: no salieron de la literatura, salieron de medir sobre el conjunto real y encontrar que la recomendación previa no se sostenía.

## Las decisiones que los datos revisaron

Las flechas punteadas del segundo diagrama marcan dos decisiones que no salieron de la literatura sino de medir sobre el conjunto real:

- **No filtrar por la columna `group`** — [decisión 2](decisiones.md#d2)
- **El etiquetado de la etapa 2 por tres vías** — [decisión 7](decisiones.md#d7)

El registro guarda de cada una el contexto, la versión superada y lo que la cambió.
