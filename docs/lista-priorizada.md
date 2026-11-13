# Lista priorizada de compuestos naturales

> **Es una lista exploratoria, no una validada.** La ordena el modelo de potencia de la fase 2, que **en los productos naturales no supera a una línea base sencilla** (concordancia 0.530 contra 0.565 de peso, TPSA y diana, en 117 pares de la prueba reservada, [C.5](decisiones.md#dc-5)). Sirve para decidir **qué probar primero**, no para afirmar que un compuesto actúa. Ninguna fila es un resultado de laboratorio.

## Cómo se hizo

- **Universo:** 1,821 compuestos de las filas de ajuste que NPASS o CMAUP aportan a la fase 2 (la prueba reservada no se lee). Salen 223 con alerta PAINS y 569 con puntaje de semejanza a productos naturales menor de 0.5 (Ertl et al., 2008, `ertl2008natural`), porque esas bases traen algunos fármacos sintéticos; quedan 1,026.
- **Por diana:** los 10 de mayor potencia predicha entre los que **no tienen medición contra esa diana** (los pares ya medidos no son hipótesis nuevas). **Ordena solo la potencia: la barrera hematoencefálica no filtra**, porque un compuesto que no cruza por difusión puede llegar al cerebro por un transportador o con una formulación, y un BBB− no descarta ([C.5](decisiones.md#dc-5)). La probabilidad de cruzar va en su columna, al lado; la variante que exige barrera probable (0.5 o más) se guarda aparte (`por_diana_con_barrera_probable.csv` en `experimentos/2026-11-12-artemio-C.5-lista-priorizada-naturales-corte-np-05`).
- **Por enfermedad:** lo mismo, con el máximo entre las dianas de esa categoría (las categorías son las del archivo de la patrocinadora).

## Cómo leerla

- **Potencia predicha:** pActividad (5 es unos 10 µM, 6 es 1 µM, 7 es 0.1 µM). El modelo predice potencia, **sin saber en qué sentido** debe actuar el compuesto (inhibir o activar): el efecto buscado viene del archivo de dianas de la patrocinadora.
- **Parecido a lo visto:** «bajo» si el compuesto se parece menos de 0.4 a lo que los modelos vieron al entrenarse; entonces su lugar vale menos.
- **Se repiten:** la química que pesa es casi la misma en todas las dianas (la diana pone el 15% de la atribución, ver el anexo F del artículo), así que **los mismos compuestos suben en varias listas**: las 260 filas por diana tienen solo 75 compuestos distintos. Lo que dice la lista es qué compuestos de entrada parecen potentes, más que cuál es el mejor para cada diana.
- **Identificadores:** si el dato no trae un nombre usable, el compuesto va con su identificador de NPASS (`NPASS:NPC...`). SMILES, esqueleto y todas las columnas están en los CSV de la corrida.

Corrida: `2026-11-12-artemio-C.5-lista-priorizada-naturales-corte-np-05` (`scripts/lista_priorizada_naturales.py`).

## Por enfermedad

### Alzheimer

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | Fisovenina | APP (reducir niveles) | 8.1 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | GRIN1 (antagonismo) | 7.4 | 0.61 | bajo (extrapola) |
| 3 | Calcimycin | GRIN1 (antagonismo) | 7.2 | 0.37 | bajo (extrapola) |
| 4 | NPASS:NPC607165 | GRIN1 (antagonismo) | 7.1 | 0.25 | bajo (extrapola) |
| 5 | NPASS:NPC184932 | GRIN1 (antagonismo) | 7.1 | 0.25 | bajo (extrapola) |
| 6 | 3-(3,4-dimetoxifenil)serina | GRIN1 (antagonismo) | 7.0 | 0.61 | razonable |
| 7 | NPASS:NPC603739 | GRIN1 (antagonismo) | 7.0 | 0.09 | razonable |
| 8 | NPASS:NPC607395 | GRIN1 (antagonismo) | 7.0 | 0.28 | bajo (extrapola) |
| 9 | Staurosporine | GRIN1 (antagonismo) | 7.0 | 0.80 | bajo (extrapola) |
| 10 | NPASS:NPC74259 | GRIN1 (antagonismo) | 7.0 | 0.08 | razonable |

### Depresión

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | Fisovenina | GRIN2B (antagonismo) | 7.8 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | GRIN2B (antagonismo) | 7.0 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC323597 | GRIN2B (antagonismo) | 7.0 | 0.31 | razonable |
| 4 | Sanguinine | GRIN2B (antagonismo) | 6.7 | 0.92 | razonable |
| 5 | Calcimycin | GRIN2B (antagonismo) | 6.6 | 0.37 | bajo (extrapola) |
| 6 | NPASS:NPC195075 | GRIN2B (antagonismo) | 6.6 | 0.94 | razonable |
| 7 | 3-(3,4-dimetoxifenil)serina | GRIN2B (antagonismo) | 6.6 | 0.61 | razonable |
| 8 | NPASS:NPC323045 | GRIN2B (antagonismo) | 6.5 | 0.20 | razonable |
| 9 | NPASS:NPC314573 | GRIN2B (antagonismo) | 6.5 | 0.49 | bajo (extrapola) |
| 10 | NPASS:NPC224774 | GRIN2B (antagonismo) | 6.5 | 0.81 | bajo (extrapola) |

### Estrés oxidativo

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | Fisovenina | NFE2L2 (activación) | 7.4 | 0.88 | razonable |
| 2 | 3-(3,4-dimetoxifenil)serina | KEAP1 (inhibición) | 6.8 | 0.61 | razonable |
| 3 | Lignano (NPC483651) | KEAP1 (inhibición) | 6.8 | 0.61 | bajo (extrapola) |
| 4 | Calcimycin | KEAP1 (inhibición) | 6.6 | 0.37 | bajo (extrapola) |
| 5 | Sanguinine | NFE2L2 (activación) | 6.4 | 0.92 | razonable |
| 6 | NPASS:NPC607165 | KEAP1 (inhibición) | 6.3 | 0.25 | bajo (extrapola) |
| 7 | NPASS:NPC603739 | KEAP1 (inhibición) | 6.3 | 0.09 | razonable |
| 8 | NPASS:NPC483652 | KEAP1 (inhibición) | 6.3 | 0.63 | bajo (extrapola) |
| 9 | NPASS:NPC607395 | KEAP1 (inhibición) | 6.2 | 0.28 | bajo (extrapola) |
| 10 | NPASS:NPC610464 | NFE2L2 (activación) | 6.2 | 0.43 | bajo (extrapola) |

### Neuroinflamación

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | Lignano (NPC483651) | TNF (inhibición) | 8.5 | 0.61 | bajo (extrapola) |
| 2 | Fisovenina | TSPO (activación) | 8.3 | 0.88 | razonable |
| 3 | NPASS:NPC74259 | TNF (inhibición) | 8.2 | 0.08 | razonable |
| 4 | NPASS:NPC313921 | TNF (inhibición) | 8.2 | 0.50 | bajo (extrapola) |
| 5 | Deslanoside | TNF (inhibición) | 8.1 | 0.09 | razonable |
| 6 | Kamebanin | TNF (inhibición) | 8.0 | 0.74 | bajo (extrapola) |
| 7 | NPASS:NPC117445 | TNF (inhibición) | 7.9 | 0.10 | razonable |
| 8 | NPASS:NPC479630 | TNF (inhibición) | 7.9 | 0.95 | bajo (extrapola) |
| 9 | NPASS:NPC484494 | TNF (inhibición) | 7.8 | 0.44 | bajo (extrapola) |
| 10 | NPASS:NPC610464 | TNF (inhibición) | 7.8 | 0.43 | bajo (extrapola) |

### Parkinson

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | Fisovenina | LRRK2 (inhibición) | 7.8 | 0.88 | razonable |
| 2 | NPASS:NPC603594 | COMT (inhibición) | 7.1 | 0.08 | bajo (extrapola) |
| 3 | NPASS:NPC603739 | LRRK2 (inhibición) | 7.0 | 0.09 | razonable |
| 4 | Sanguinine | DRD2 (agonismo o antagonismo (según enfermedad)) | 7.0 | 0.92 | razonable |
| 5 | Hidroxi-cantin-6-ona (NPC53144) | SNCA (reducir agregación) | 7.0 | 0.75 | bajo (extrapola) |
| 6 | NPASS:NPC609876 | COMT (inhibición) | 7.0 | 0.08 | bajo (extrapola) |
| 7 | 3-(3,4-dimetoxifenil)serina | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.9 | 0.61 | razonable |
| 8 | NPASS:NPC56109 | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.9 | 0.15 | razonable |
| 9 | levallorphan | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.9 | BBB+ medido | razonable |
| 10 | NPASS:NPC184932 | LRRK2 (inhibición) | 6.8 | 0.25 | bajo (extrapola) |

## Por diana (los cinco primeros)

### ACHE: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC603594 | 6.3 | 0.08 | bajo (extrapola) |
| 2 | NPASS:NPC603739 | 6.2 | 0.09 | razonable |
| 3 | Calcimycin | 6.2 | 0.37 | bajo (extrapola) |
| 4 | NPASS:NPC609876 | 6.2 | 0.08 | bajo (extrapola) |
| 5 | NPASS:NPC469878 | 6.1 | 0.23 | bajo (extrapola) |

### APP: Alzheimer (reducir niveles)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 8.1 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 7.1 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC610126 | 6.8 | 0.90 | bajo (extrapola) |
| 4 | NPASS:NPC53222 | 6.8 | 0.93 | bajo (extrapola) |
| 5 | NPASS:NPC313921 | 6.7 | 0.50 | bajo (extrapola) |

### BACE1: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.4 | 0.88 | razonable |
| 2 | Calcimycin | 6.8 | 0.37 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |
| 4 | NPASS:NPC603739 | 6.5 | 0.09 | razonable |
| 5 | NPASS:NPC607165 | 6.4 | 0.25 | bajo (extrapola) |

### BCHE: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | 3-(3,4-dimetoxifenil)serina | 6.4 | 0.61 | razonable |
| 2 | Lignano (NPC483651) | 6.1 | 0.61 | bajo (extrapola) |
| 3 | cas-113-42-8 | 6.1 | BBB+ medido | razonable |
| 4 | NPASS:NPC607165 | 6.0 | 0.25 | bajo (extrapola) |
| 5 | NPASS:NPC259545 | 6.0 | 0.77 | bajo (extrapola) |

### COMT: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.2 | 0.88 | razonable |
| 2 | NPASS:NPC603594 | 7.1 | 0.08 | bajo (extrapola) |
| 3 | NPASS:NPC609876 | 7.0 | 0.08 | bajo (extrapola) |
| 4 | NPASS:NPC479630 | 6.8 | 0.95 | bajo (extrapola) |
| 5 | NPASS:NPC53222 | 6.7 | 0.93 | bajo (extrapola) |

### CX3CR1: Neuroinflamación (dirección no establecida)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 6.9 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 6.9 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC313921 | 6.7 | 0.50 | bajo (extrapola) |
| 4 | NPASS:NPC53222 | 6.6 | 0.93 | bajo (extrapola) |
| 5 | NPASS:NPC607165 | 6.5 | 0.25 | bajo (extrapola) |

### DRD2: Parkinson (agonismo o antagonismo (según enfermedad))

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.6 | 0.88 | razonable |
| 2 | Sanguinine | 7.0 | 0.92 | razonable |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.9 | 0.61 | razonable |
| 4 | NPASS:NPC56109 | 6.9 | 0.15 | razonable |
| 5 | levallorphan | 6.9 | BBB+ medido | razonable |

### GRIN1: Alzheimer (antagonismo)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.6 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 7.4 | 0.61 | bajo (extrapola) |
| 3 | Calcimycin | 7.2 | 0.37 | bajo (extrapola) |
| 4 | NPASS:NPC607165 | 7.1 | 0.25 | bajo (extrapola) |
| 5 | NPASS:NPC184932 | 7.1 | 0.25 | bajo (extrapola) |

### GRIN2B: Depresión (antagonismo)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.8 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 7.0 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC323597 | 7.0 | 0.31 | razonable |
| 4 | Sanguinine | 6.7 | 0.92 | razonable |
| 5 | Calcimycin | 6.6 | 0.37 | bajo (extrapola) |

### GSK3B: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.5 | 0.88 | razonable |
| 2 | Calcimycin | 6.8 | 0.37 | bajo (extrapola) |
| 3 | Lignano (NPC483651) | 6.7 | 0.61 | bajo (extrapola) |
| 4 | NPASS:NPC607165 | 6.3 | 0.25 | bajo (extrapola) |
| 5 | NPASS:NPC603739 | 6.2 | 0.09 | razonable |

### IL1B: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 8.2 | 0.88 | razonable |
| 2 | 3-(3,4-dimetoxifenil)serina | 7.3 | 0.61 | razonable |
| 3 | Lignano (NPC483651) | 7.3 | 0.61 | bajo (extrapola) |
| 4 | NPASS:NPC469878 | 6.9 | 0.23 | bajo (extrapola) |
| 5 | \[(3as)-3,4,8b-trimethyl-2,3a-dihydro-1h-pyrrolo\[2,3-b]indol-... | 6.9 | BBB+ medido | razonable |

### IL6: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 8.0 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 7.8 | 0.61 | bajo (extrapola) |
| 3 | Calcimycin | 7.2 | 0.37 | bajo (extrapola) |
| 4 | 3-(3,4-dimetoxifenil)serina | 7.1 | 0.61 | razonable |
| 5 | NPASS:NPC483652 | 6.9 | 0.63 | bajo (extrapola) |

### KEAP1: Estrés oxidativo (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | 3-(3,4-dimetoxifenil)serina | 6.8 | 0.61 | razonable |
| 2 | Lignano (NPC483651) | 6.8 | 0.61 | bajo (extrapola) |
| 3 | Fisovenina | 6.7 | 0.88 | razonable |
| 4 | Calcimycin | 6.6 | 0.37 | bajo (extrapola) |
| 5 | NPASS:NPC607165 | 6.3 | 0.25 | bajo (extrapola) |

### LRRK2: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.8 | 0.88 | razonable |
| 2 | NPASS:NPC603739 | 7.0 | 0.09 | razonable |
| 3 | NPASS:NPC184932 | 6.8 | 0.25 | bajo (extrapola) |
| 4 | NPASS:NPC607165 | 6.8 | 0.25 | bajo (extrapola) |
| 5 | NPASS:NPC607395 | 6.7 | 0.28 | bajo (extrapola) |

### MAOA: Depresión (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 6.2 | 0.88 | razonable |
| 2 | NPASS:NPC184932 | 6.1 | 0.25 | bajo (extrapola) |
| 3 | Heliomycin | 6.1 | 0.04 | bajo (extrapola) |
| 4 | Lignano (NPC483651) | 6.0 | 0.61 | bajo (extrapola) |
| 5 | 3-(3,4-dimetoxifenil)serina | 5.9 | 0.61 | razonable |

### MAOB: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC22783 | 6.6 | 0.81 | bajo (extrapola) |
| 2 | 5-Methoxy-2-Phenylchromen-4-One | 6.6 | 0.94 | bajo (extrapola) |
| 3 | NPASS:NPC53222 | 6.6 | 0.93 | bajo (extrapola) |
| 4 | 3-(3,4-dimetoxifenil)serina | 6.5 | 0.61 | razonable |
| 5 | NPASS:NPC39753 | 6.5 | 0.85 | bajo (extrapola) |

### MAPT: Alzheimer (reducir agregación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.6 | 0.88 | razonable |
| 2 | Hidroxi-cantin-6-ona (NPC53144) | 6.9 | 0.75 | bajo (extrapola) |
| 3 | NPASS:NPC200836 | 6.9 | 0.74 | bajo (extrapola) |
| 4 | Lignano (NPC483651) | 6.8 | 0.61 | bajo (extrapola) |
| 5 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |

### NFE2L2: Estrés oxidativo (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.4 | 0.88 | razonable |
| 2 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |
| 3 | Lignano (NPC483651) | 6.5 | 0.61 | bajo (extrapola) |
| 4 | Sanguinine | 6.4 | 0.92 | razonable |
| 5 | NPASS:NPC483652 | 6.2 | 0.63 | bajo (extrapola) |

### NLRP3: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.8 | 0.88 | razonable |
| 2 | Staurosporine | 7.2 | 0.80 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 7.1 | 0.61 | razonable |
| 4 | NPASS:NPC268602 | 6.6 | 0.71 | bajo (extrapola) |
| 5 | Lignano (NPC483651) | 6.5 | 0.61 | bajo (extrapola) |

### NOS2: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.3 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 6.6 | 0.61 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.5 | 0.61 | razonable |
| 4 | Calcimycin | 6.5 | 0.37 | bajo (extrapola) |
| 5 | NPASS:NPC313921 | 6.3 | 0.50 | bajo (extrapola) |

### PPARG: Alzheimer (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.3 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 6.8 | 0.61 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.5 | 0.61 | razonable |
| 4 | NPASS:NPC483652 | 6.4 | 0.63 | bajo (extrapola) |
| 5 | NPASS:NPC603739 | 6.3 | 0.09 | razonable |

### PTGS2: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.2 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 6.7 | 0.61 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |
| 4 | Calcimycin | 6.5 | 0.37 | bajo (extrapola) |
| 5 | Staurosporine | 6.5 | 0.80 | bajo (extrapola) |

### SNCA: Parkinson (reducir agregación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.3 | 0.88 | razonable |
| 2 | Hidroxi-cantin-6-ona (NPC53144) | 7.0 | 0.75 | bajo (extrapola) |
| 3 | NPASS:NPC200836 | 6.7 | 0.74 | bajo (extrapola) |
| 4 | Lignano (NPC483651) | 6.6 | 0.61 | bajo (extrapola) |
| 5 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |

### TLR4: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 7.5 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 6.7 | 0.61 | bajo (extrapola) |
| 3 | 3-(3,4-dimetoxifenil)serina | 6.6 | 0.61 | razonable |
| 4 | NPASS:NPC74259 | 6.2 | 0.08 | razonable |
| 5 | NPASS:NPC53222 | 6.0 | 0.93 | bajo (extrapola) |

### TNF: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Lignano (NPC483651) | 8.5 | 0.61 | bajo (extrapola) |
| 2 | NPASS:NPC74259 | 8.2 | 0.08 | razonable |
| 3 | NPASS:NPC313921 | 8.2 | 0.50 | bajo (extrapola) |
| 4 | Deslanoside | 8.1 | 0.09 | razonable |
| 5 | Kamebanin | 8.0 | 0.74 | bajo (extrapola) |

### TSPO: Neuroinflamación (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Fisovenina | 8.3 | 0.88 | razonable |
| 2 | Lignano (NPC483651) | 7.5 | 0.61 | bajo (extrapola) |
| 3 | Piplartine | 7.4 | 0.94 | razonable |
| 4 | NPASS:NPC485642 | 7.3 | 0.93 | bajo (extrapola) |
| 5 | Bavachinin A | 7.2 | 0.78 | bajo (extrapola) |
