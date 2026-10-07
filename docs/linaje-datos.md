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

## Las dos correcciones, con su evidencia

### No filtrar por la columna `group`

La investigación inicial leyó las categorías A–D de B3DB como una escala de confiabilidad y recomendó entrenar solo con A+B. El [EDA del Avance 1](../notebooks/01_EDA.ipynb) lo desmintió sobre los datos:

- El grupo D tiene **mediana de 3 referencias** contra **1** del grupo C: más respaldo, no menos.
- **Ningún registro duplicado** del conjunto tiene etiquetas contradictorias.
- La columna está confundida con la etiqueta: filtrar a A+B baja la clase minoritaria del **36.5% al 27.0%**, empeorando el desbalance en vez de limpiar ruido.

La recomendación superada sigue visible en [02 · Datasets de BBB](referencias/02-datasets-bbb.md), marcada como tal.

### El umbral de etiquetado de la etapa 2

La decisión documentada era pChEMBL ≥ 5 como primario y ≥ 6 como robustez. El [EDA de la etapa 2](../notebooks/01b_EDA_actividad_snc.ipynb) muestra que el criterio, aplicado solo, descarta en silencio tres bloques de evidencia:

| Qué queda fuera | Registros |
|:---|---:|
| NPASS y CMAUP completos, que son las bases de **productos naturales** (12,809 recuperables por concentración exacta) | 15,293 |
| Todas las mediciones **censuradas** (`>= X nM`) | 54,498 |
| Los **inactivos declarados por texto** del artículo original | 29,730 |

Y el umbral mismo cambia el problema: ≥ 5 deja 87.1% de activos, con un desbalance de 6.7 a 1 donde la clase difícil es la inactiva; ≥ 6 deja 63.7%, con 1.8 a 1. La distribución del pChEMBL no tiene un mínimo que sugiera dónde cortar.

Al recalcular el desbalance **con las tres vías de etiquetado aplicadas**, y no solo sobre el subconjunto con pChEMBL, la conclusión se invierte: ≥ 5 deja el conjunto casi equilibrado (61.7% de activos, 1.6 a 1) y ≥ 6 se pasa de largo (44.4%, 0.8 a 1).

**El criterio de `CLAUDE.md` se mantiene —≥ 5 primario, ≥ 6 robustez—**, con una condición que antes no estaba escrita: el etiquetado tiene que usar las tres vías. Lo que se corrige no es el umbral sino el procedimiento, que etiquetando solo por pChEMBL perdía los productos naturales.
