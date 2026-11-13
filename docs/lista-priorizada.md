# Lista priorizada de compuestos naturales

> **Es una lista exploratoria, no una validada.** La ordena el modelo de potencia de la fase 2, que **en los productos naturales no supera a una línea base sencilla** (concordancia 0.530 contra 0.565 de peso, TPSA y diana, en 117 pares de la prueba reservada, [C.5](decisiones.md#dc-5)). Sirve para decidir **qué probar primero**, no para afirmar que un compuesto actúa. Ninguna fila es un resultado de laboratorio.

## Cómo se hizo

- **Universo:** 1,821 compuestos de las filas de ajuste que NPASS o CMAUP aportan a la fase 2 (la prueba reservada no se lee). Salen 223 con alerta PAINS y 315 con puntaje de semejanza a productos naturales menor de 0 (Ertl et al., 2008, `ertl2008natural`), porque esas bases traen algunos fármacos sintéticos; quedan 1,280.
- **Por diana:** los 10 de mayor potencia predicha entre los que **no tienen medición contra esa diana** (los pares ya medidos no son hipótesis nuevas) y con **barrera probable** (probabilidad de cruzar la barrera de 0.5 o más). Es lo que pide el objetivo del proyecto: llegar al cerebro **y** actuar sobre su diana. El 0.5 no es un corte calibrado y **combinar las dos fases no está validado** ([C.3](decisiones.md#dc-3)); por eso la lista sin ese criterio también se guarda (`por_diana_solo_potencia.csv` en `experimentos/2026-11-12-artemio-C.5-lista-priorizada-naturales`).
- **Por enfermedad:** lo mismo, con el máximo entre las dianas de esa categoría (las categorías son las del archivo de la patrocinadora).
- **Un compuesto con barrera baja no queda descartado** (un BBB− no descarta, [C.5](decisiones.md#dc-5)): el criterio solo ordena.

## Cómo leerla

- **Potencia predicha:** pActividad (5 es unos 10 µM, 6 es 1 µM, 7 es 0.1 µM). El modelo predice potencia, **sin saber en qué sentido** debe actuar el compuesto (inhibir o activar): el efecto buscado viene del archivo de dianas de la patrocinadora.
- **Parecido a lo visto:** «bajo» si el compuesto se parece menos de 0.4 a lo que los modelos vieron al entrenarse; entonces su lugar vale menos.
- **Se repiten:** la química que pesa es casi la misma en todas las dianas (la diana pone el 15% de la atribución, ver el anexo F del artículo), así que **los mismos compuestos suben en varias listas**: las 260 filas por diana tienen solo 84 compuestos distintos. Lo que dice la lista es qué compuestos de entrada parecen potentes, más que cuál es el mejor para cada diana.
- **Identificadores:** si el dato no trae un nombre usable, el compuesto va con su identificador de NPASS (`NPASS:NPC...`). SMILES, esqueleto y todas las columnas están en los CSV de la corrida.

Corrida: `2026-11-12-artemio-C.5-lista-priorizada-naturales` (`scripts/lista_priorizada_naturales.py`).

## Por enfermedad

### Alzheimer

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | APP (reducir niveles) | 8.1 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | GRIN1 (antagonismo) | 7.4 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | GRIN1 (antagonismo) | 7.0 | 0.61 | razonable |
| 4 | Staurosporine | GRIN1 (antagonismo) | 7.0 | 0.80 | bajo (extrapola) |
| 5 | NPASS:NPC53144 | MAPT (reducir agregación) | 6.9 | 0.75 | bajo (extrapola) |
| 6 | NPASS:NPC200836 | MAPT (reducir agregación) | 6.9 | 0.74 | bajo (extrapola) |
| 7 | NPASS:NPC610126 | APP (reducir niveles) | 6.8 | 0.90 | bajo (extrapola) |
| 8 | Pterostilbene | APP (reducir niveles) | 6.8 | 0.82 | razonable |
| 9 | NPASS:NPC192674 | GRIN1 (antagonismo) | 6.8 | 0.72 | razonable |
| 10 | NPASS:NPC53222 | APP (reducir niveles) | 6.8 | 0.93 | bajo (extrapola) |

### Depresión

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | GRIN2B (antagonismo) | 7.8 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | GRIN2B (antagonismo) | 7.0 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC481153 | GRIN2B (antagonismo) | 7.0 | 0.89 | bajo (extrapola) |
| 4 | Sanguinine | GRIN2B (antagonismo) | 6.7 | 0.92 | razonable |
| 5 | NPASS:NPC195075 | GRIN2B (antagonismo) | 6.6 | 0.94 | razonable |
| 6 | NPASS:NPC483655 | GRIN2B (antagonismo) | 6.6 | 0.61 | razonable |
| 7 | NPASS:NPC224774 | GRIN2B (antagonismo) | 6.5 | 0.81 | bajo (extrapola) |
| 8 | NPASS:NPC483652 | GRIN2B (antagonismo) | 6.5 | 0.63 | bajo (extrapola) |
| 9 | NPASS:NPC470693 | GRIN2B (antagonismo) | 6.5 | 0.74 | bajo (extrapola) |
| 10 | Indirubin | MAOA (inhibición) | 6.5 | 0.80 | bajo (extrapola) |

### Estrés oxidativo

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | NFE2L2 (activación) | 7.4 | 0.88 | razonable |
| 2 | NPASS:NPC483655 | KEAP1 (inhibición) | 6.8 | 0.61 | razonable |
| 3 | NPASS:NPC483651 | KEAP1 (inhibición) | 6.8 | 0.61 | bajo (extrapola) |
| 4 | Sanguinine | NFE2L2 (activación) | 6.4 | 0.92 | razonable |
| 5 | NPASS:NPC483652 | KEAP1 (inhibición) | 6.3 | 0.63 | bajo (extrapola) |
| 6 | Indirubin | KEAP1 (inhibición) | 6.2 | 0.80 | bajo (extrapola) |
| 7 | NPASS:NPC32028 | NFE2L2 (activación) | 6.1 | 0.83 | bajo (extrapola) |
| 8 | NPASS:NPC268602 | NFE2L2 (activación) | 6.1 | 0.71 | bajo (extrapola) |
| 9 | NPASS:NPC607967 | NFE2L2 (activación) | 6.1 | 0.67 | bajo (extrapola) |
| 10 | NPASS:NPC53222 | KEAP1 (inhibición) | 6.1 | 0.93 | bajo (extrapola) |

### Neuroinflamación

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | NPASS:NPC483651 | TNF (inhibición) | 8.5 | 0.61 | bajo (extrapola) |
| 2 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | TSPO (activación) | 8.3 | 0.88 | razonable |
| 3 | Kamebanin | TNF (inhibición) | 8.0 | 0.74 | bajo (extrapola) |
| 4 | NPASS:NPC479630 | TNF (inhibición) | 7.9 | 0.95 | bajo (extrapola) |
| 5 | NPASS:NPC119252 | TNF (inhibición) | 7.8 | 0.59 | bajo (extrapola) |
| 6 | Tetramethoxycurcumin | TSPO (activación) | 7.7 | 0.59 | razonable |
| 7 | NPASS:NPC71848 | TNF (inhibición) | 7.7 | 0.90 | bajo (extrapola) |
| 8 | NPASS:NPC268602 | TNF (inhibición) | 7.7 | 0.71 | bajo (extrapola) |
| 9 | hydrocortisone-hemisuccinate | TNF (inhibición) | 7.7 | BBB+ medido | razonable |
| 10 | NPASS:NPC479631 | TNF (inhibición) | 7.6 | 0.95 | bajo (extrapola) |

### Parkinson

| Lugar | Compuesto | Diana (efecto buscado) | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | LRRK2 (inhibición) | 7.8 | 0.88 | razonable |
| 2 | Sanguinine | DRD2 (agonismo o antagonismo (según enfermedad)) | 7.0 | 0.92 | razonable |
| 3 | NPASS:NPC53144 | SNCA (reducir agregación) | 7.0 | 0.75 | bajo (extrapola) |
| 4 | NPASS:NPC483655 | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.9 | 0.61 | razonable |
| 5 | levallorphan | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.9 | BBB+ medido | razonable |
| 6 | NPASS:NPC259545 | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.8 | 0.77 | bajo (extrapola) |
| 7 | (2-Methyl-4-Oxo-3-Phenylchromen-7-Yl) Acetate | COMT (inhibición) | 6.8 | 0.86 | bajo (extrapola) |
| 8 | NPASS:NPC483651 | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.8 | 0.61 | bajo (extrapola) |
| 9 | NPASS:NPC479630 | COMT (inhibición) | 6.8 | 0.95 | bajo (extrapola) |
| 10 | NPASS:NPC482954 | DRD2 (agonismo o antagonismo (según enfermedad)) | 6.8 | 0.80 | bajo (extrapola) |

## Por diana (los cinco primeros)

### ACHE: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC53222 | 6.0 | 0.93 | bajo (extrapola) |
| 2 | Bavachinin | 5.7 | 0.80 | bajo (extrapola) |
| 3 | NPASS:NPC234053 | 5.6 | 0.97 | bajo (extrapola) |
| 4 | NPASS:NPC39753 | 5.6 | 0.85 | bajo (extrapola) |
| 5 | NPASS:NPC34764 | 5.6 | 0.94 | bajo (extrapola) |

### APP: Alzheimer (reducir niveles)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 8.1 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 7.1 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC610126 | 6.8 | 0.90 | bajo (extrapola) |
| 4 | Pterostilbene | 6.8 | 0.82 | razonable |
| 5 | NPASS:NPC53222 | 6.8 | 0.93 | bajo (extrapola) |

### BACE1: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.4 | 0.88 | razonable |
| 2 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |
| 3 | Staurosporine | 6.3 | 0.80 | bajo (extrapola) |
| 4 | NPASS:NPC483652 | 6.2 | 0.63 | bajo (extrapola) |
| 5 | NPASS:NPC53144 | 6.1 | 0.75 | bajo (extrapola) |

### BCHE: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC483655 | 6.4 | 0.61 | razonable |
| 2 | NPASS:NPC483651 | 6.1 | 0.61 | bajo (extrapola) |
| 3 | cas-113-42-8 | 6.1 | BBB+ medido | razonable |
| 4 | NPASS:NPC259545 | 6.0 | 0.77 | bajo (extrapola) |
| 5 | NPASS:NPC281883 | 5.9 | 0.67 | razonable |

### COMT: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.2 | 0.88 | razonable |
| 2 | (2-Methyl-4-Oxo-3-Phenylchromen-7-Yl) Acetate | 6.8 | 0.86 | bajo (extrapola) |
| 3 | NPASS:NPC479630 | 6.8 | 0.95 | bajo (extrapola) |
| 4 | NPASS:NPC53222 | 6.7 | 0.93 | bajo (extrapola) |
| 5 | Staurosporine | 6.6 | 0.80 | bajo (extrapola) |

### CX3CR1: Neuroinflamación (dirección no establecida)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 6.9 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.9 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC53222 | 6.6 | 0.93 | bajo (extrapola) |
| 4 | NPASS:NPC483655 | 6.4 | 0.61 | razonable |
| 5 | NPASS:NPC65045 | 6.4 | 0.56 | bajo (extrapola) |

### DRD2: Parkinson (agonismo o antagonismo (según enfermedad))

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.6 | 0.88 | razonable |
| 2 | Sanguinine | 7.0 | 0.92 | razonable |
| 3 | NPASS:NPC483655 | 6.9 | 0.61 | razonable |
| 4 | levallorphan | 6.9 | BBB+ medido | razonable |
| 5 | NPASS:NPC259545 | 6.8 | 0.77 | bajo (extrapola) |

### GRIN1: Alzheimer (antagonismo)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.6 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 7.4 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 7.0 | 0.61 | razonable |
| 4 | Staurosporine | 7.0 | 0.80 | bajo (extrapola) |
| 5 | NPASS:NPC192674 | 6.8 | 0.72 | razonable |

### GRIN2B: Depresión (antagonismo)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.8 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 7.0 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC481153 | 7.0 | 0.89 | bajo (extrapola) |
| 4 | Sanguinine | 6.7 | 0.92 | razonable |
| 5 | NPASS:NPC195075 | 6.6 | 0.94 | razonable |

### GSK3B: Alzheimer (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.5 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.7 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC22783 | 6.0 | 0.81 | bajo (extrapola) |
| 4 | NPASS:NPC482954 | 6.0 | 0.80 | bajo (extrapola) |
| 5 | NPASS:NPC53222 | 6.0 | 0.93 | bajo (extrapola) |

### IL1B: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 8.2 | 0.88 | razonable |
| 2 | NPASS:NPC483655 | 7.3 | 0.61 | razonable |
| 3 | NPASS:NPC483651 | 7.3 | 0.61 | bajo (extrapola) |
| 4 | \[(3as)-3,4,8b-trimethyl-2,3a-dihydro-1h-pyrrolo\[2,3-b]indol-... | 6.9 | BBB+ medido | razonable |
| 5 | NPASS:NPC43648 | 6.7 | 0.68 | bajo (extrapola) |

### IL6: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 8.0 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 7.8 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 7.1 | 0.61 | razonable |
| 4 | NPASS:NPC483652 | 6.9 | 0.63 | bajo (extrapola) |
| 5 | NPASS:NPC482954 | 6.6 | 0.80 | bajo (extrapola) |

### KEAP1: Estrés oxidativo (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC483655 | 6.8 | 0.61 | razonable |
| 2 | NPASS:NPC483651 | 6.8 | 0.61 | bajo (extrapola) |
| 3 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 6.7 | 0.88 | razonable |
| 4 | NPASS:NPC483652 | 6.3 | 0.63 | bajo (extrapola) |
| 5 | Indirubin | 6.2 | 0.80 | bajo (extrapola) |

### LRRK2: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.8 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.6 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC480265 | 6.6 | 0.86 | razonable |
| 4 | NPASS:NPC65045 | 6.6 | 0.56 | bajo (extrapola) |
| 5 | Sanguinine | 6.5 | 0.92 | razonable |

### MAOA: Depresión (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | Indirubin | 6.5 | 0.80 | bajo (extrapola) |
| 2 | NPASS:NPC176538 | 6.5 | 0.86 | razonable |
| 3 | NPASS:NPC479095 | 6.4 | 0.79 | bajo (extrapola) |
| 4 | NPASS:NPC191415 | 6.3 | 0.90 | razonable |
| 5 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 6.2 | 0.88 | razonable |

### MAOB: Parkinson (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC22783 | 6.6 | 0.81 | bajo (extrapola) |
| 2 | 5-Methoxy-2-Phenylchromen-4-One | 6.6 | 0.94 | bajo (extrapola) |
| 3 | NPASS:NPC53222 | 6.6 | 0.93 | bajo (extrapola) |
| 4 | NPASS:NPC483655 | 6.5 | 0.61 | razonable |
| 5 | NPASS:NPC129443 | 6.5 | 0.93 | bajo (extrapola) |

### MAPT: Alzheimer (reducir agregación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.6 | 0.88 | razonable |
| 2 | NPASS:NPC53144 | 6.9 | 0.75 | bajo (extrapola) |
| 3 | NPASS:NPC200836 | 6.9 | 0.74 | bajo (extrapola) |
| 4 | NPASS:NPC483651 | 6.8 | 0.61 | bajo (extrapola) |
| 5 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |

### NFE2L2: Estrés oxidativo (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.4 | 0.88 | razonable |
| 2 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |
| 3 | NPASS:NPC483651 | 6.5 | 0.61 | bajo (extrapola) |
| 4 | Sanguinine | 6.4 | 0.92 | razonable |
| 5 | NPASS:NPC483652 | 6.2 | 0.63 | bajo (extrapola) |

### NLRP3: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.8 | 0.88 | razonable |
| 2 | Staurosporine | 7.2 | 0.80 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 7.1 | 0.61 | razonable |
| 4 | NPASS:NPC268602 | 6.6 | 0.71 | bajo (extrapola) |
| 5 | mefloquine | 6.6 | BBB+ medido | razonable |

### NOS2: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.3 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.6 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 6.5 | 0.61 | razonable |
| 4 | Staurosporine | 6.3 | 0.80 | bajo (extrapola) |
| 5 | NPASS:NPC53222 | 6.3 | 0.93 | bajo (extrapola) |

### PPARG: Alzheimer (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.3 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.8 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 6.5 | 0.61 | razonable |
| 4 | NPASS:NPC483652 | 6.4 | 0.63 | bajo (extrapola) |
| 5 | Indirubin | 6.1 | 0.80 | bajo (extrapola) |

### PTGS2: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.2 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.7 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |
| 4 | Staurosporine | 6.5 | 0.80 | bajo (extrapola) |
| 5 | Indirubin | 6.1 | 0.80 | bajo (extrapola) |

### SNCA: Parkinson (reducir agregación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.3 | 0.88 | razonable |
| 2 | NPASS:NPC53144 | 7.0 | 0.75 | bajo (extrapola) |
| 3 | NPASS:NPC200836 | 6.7 | 0.74 | bajo (extrapola) |
| 4 | NPASS:NPC483651 | 6.6 | 0.61 | bajo (extrapola) |
| 5 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |

### TLR4: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 7.5 | 0.88 | razonable |
| 2 | NPASS:NPC483651 | 6.7 | 0.61 | bajo (extrapola) |
| 3 | NPASS:NPC483655 | 6.6 | 0.61 | razonable |
| 4 | NPASS:NPC53222 | 6.0 | 0.93 | bajo (extrapola) |
| 5 | sertraline | 6.0 | BBB+ medido | razonable |

### TNF: Neuroinflamación (inhibición)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | NPASS:NPC483651 | 8.5 | 0.61 | bajo (extrapola) |
| 2 | Kamebanin | 8.0 | 0.74 | bajo (extrapola) |
| 3 | NPASS:NPC479630 | 7.9 | 0.95 | bajo (extrapola) |
| 4 | NPASS:NPC119252 | 7.8 | 0.59 | bajo (extrapola) |
| 5 | NPASS:NPC71848 | 7.7 | 0.90 | bajo (extrapola) |

### TSPO: Neuroinflamación (activación)

| Lugar | Compuesto | Potencia predicha | Cruzar la barrera | Parecido a lo visto |
|--:|:--|--:|--:|:--|
| 1 | \[(3As,8Bs)-4,8B-Dimethyl-2,3A-Dihydro-1H-Furo\[2,3-B]Indol-7-... | 8.3 | 0.88 | razonable |
| 2 | Tetramethoxycurcumin | 7.7 | 0.59 | razonable |
| 3 | NPASS:NPC483651 | 7.5 | 0.61 | bajo (extrapola) |
| 4 | Piplartine | 7.4 | 0.94 | razonable |
| 5 | NPASS:NPC485642 | 7.3 | 0.93 | bajo (extrapola) |
