# Modelado, explicabilidad y hueco identificado

Qué se ha hecho en aprendizaje automático sobre permeabilidad BBB, cómo se justifica una predicción a nivel de subestructura, y qué trabajo no existe todavía y este proyecto pretende hacer.

> **Estado: borrador para revisión del equipo y los asesores.** Se construyó a partir de siete ramas de investigación documentadas en [`docs/referencias/`](../../referencias/README.md), que conservan la evidencia completa y las advertencias de acceso. La bibliografía está en [`bibliografia.bib`](../../referencias/bibliografia.bib), con 208 entradas.
>
> **Antes de entregar:** verificar contra doi.org toda referencia marcada como de acceso parcial o sin acceso. Varias entradas tienen metadatos que nadie del equipo ha leído.

---

## 6. Aprendizaje automático aplicado a permeabilidad BBB

### 6.1 Conjuntos de datos

| Dataset | Tamaño | Balance | Licencia |
|---|---|---|---|
| B3DB | 7,807–7,982 | 63.5% / 36.5% | CC0 |
| BBBP (MoleculeNet) | ~1,955–2,050 | 76% / 24% | No explícita |
| TDC BBB_Martins | 1,975 | No verificado | No especificada |
| LightBBB | 7,162 | 5,453 / 1,709 | No explícita |

B3DB se compiló a partir de 50 recursos publicados `meng2021b3db`. BBBP y TDC BBB_Martins derivan del mismo estudio `martins2012bayesian`, de modo que **no son fuentes independientes**.

### 6.2 Incertidumbre experimental y construcción de etiquetas

La documentación inicial de B3DB describía grupos A–D según el tipo de evidencia y propuso usarlos para seleccionar observaciones. Sin embargo, el diccionario del archivo curado por la patrocinadora indica que B3DB no publica el criterio completo de asignación y que sus categorías de clasificación y regresión no son intercambiables. La auditoría del archivo recibido encontró, además, que la categoría está asociada con la distribución de BBB+/BBB−: filtrar A+B modifica la prevalencia de BBB− de 36.5% a 27.0%, mientras que la cantidad de referencias no sigue un orden de calidad (D tiene mediana de tres referencias frente a una en C).

Por ello, para el EDA vigente se incluyen las **7,805 filas etiquetadas** del archivo curado y se conserva A–D para descripción y estratificación, no como escala de confiabilidad ni como criterio automático de exclusión. La comparación de subconjuntos puede plantearse como análisis de sensibilidad, pero no permite por sí sola concluir que las etiquetas de una categoría sean más confiables. En las seis filas que tienen `logBB` pero no clase integrada, el diccionario de la patrocinadora atribuye la falta de unión a una diferencia de forma estereoquímica entre los registros de regresión y clasificación; no se les asigna clase a partir de la conectividad. El umbral de conversión informado para los registros categóricos basados en `logBB` es **−1.0**.

### 6.3 Desempeño esperable

| Contexto | Resultado |
|---|---|
| Scaffold split, mejor del leaderboard de TDC | 0.924 ± 0.003 AUROC |
| Rango esperable para un modelo bien construido | **0.85–0.92 AUROC** |
| Split aleatorio / Kennard-Stone | 98.7% exactitud `yuan2018improved` |

La brecha de 7 a 13 puntos entre ambos regímenes es el efecto de la fuga de información entre particiones. Una auditoría de 51 configuraciones de benchmarks encontró que, al endurecer las particiones, **el modelo de primer lugar perdió su posición en 15 de 28 conjuntos** `schuh2026auditing`.

Los baselines publicados para el mismo conjunto BBBP varían entre 0.681 y 0.7194 para Random Forest según la fuente, producto de implementaciones distintas del scaffold split. **Este trabajo no adopta cifras de la literatura como referencia, sino que construye su propio baseline.**

---

## 7. Explicabilidad en modelos moleculares

### 7.1 Justificación

La explicabilidad no es un complemento: los asesores la plantearon como requisito y el objetivo declarado es una interpretación biológica capaz de sostener una publicación. Esto condiciona la elección de representación, que debe permitir atribución a nivel de substructura.

### 7.2 Atribución sobre fingerprints y sus limitaciones

El mapeo de un bit de Morgan a la substructura que lo activó es directo mediante la API de RDKit. Tres limitaciones condicionan el diseño:

**Colisiones de bits.** Substructuras químicamente distintas comparten bit, forzando una atribución única a fragmentos con efectos opuestos. La solución adoptada es **Sort & Slice** `dablander2024sortslice`, que ordena las substructuras por frecuencia y conserva las más frecuentes, libre de colisiones por construcción, con más de un año de validación. Existe una alternativa más reciente `li2026collisionfree` que **se validó solo con splits aleatorios, no scaffold**, según admiten sus autores, y cuyo paquete está en estado alfa con adopción casi nula; se considera piloto comparativo, no base del pipeline.

**Moléculas fantasma.** El muestreo de fondo de SHAP perturba el vector de bits directamente, generando combinaciones que **no corresponden a ninguna molécula ensamblable** `tamura2021mmpkernel`. La atribución puede premiar un fragmento inexistente.

**Brecha semántica.** *"Las características decisivas para las predicciones pueden o no ser responsables de actividades específicas"* `rodriguezperez2020shapley`. Importancia para el modelo no equivale a causalidad biológica `kumar2020problems`.

### 7.3 Métodos complementarios

Siete criterios de evaluación permiten concluir que **SHAP es completo pero débil en accionabilidad y parsimonia, mientras que los contrafactuales son fuertes en ambas y débiles en completitud: son complementarios, no sustitutos** `wellawatte2023perspective, wellawatte2022mmace`.

Sobre redes de grafos, al comparar seis métodos contra substructuras de referencia y siete químicos medicinales, **Integrated Gradients alcanzó AUROC de atribución de 0.675 mientras que los métodos basados en atención quedaron cerca del azar** (0.467 y 0.520) `rao2022patterns`.

De ahí la decisión metodológica central: **emplear al menos dos métodos independientes y reportar como confirmadas únicamente las substructuras en que coinciden**, declarando los desacuerdos. El desacuerdo entre métodos está documentado como la norma.

Una explicación post-hoc es un modelo aproximador distinto del original, sin garantía de reflejar su razonamiento `rudin2019stop`. Por eso se entrena en paralelo un modelo inherentemente interpretable como control.

### 7.4 Del nivel molecular al enunciado agregado

Debe señalarse con franqueza que **no existe un método establecido y citable que realice este procedimiento de extremo a extremo**. Lo propuesto es una síntesis de componentes establecidos: agrupación por andamios `bemis1996properties`, matriz de presencia de fragmentos, prueba exacta de Fisher con corrección de Benjamini-Hochberg, y contraste contra la magnitud media de atribución. El antecedente más cercano son las redes de andamios `varin2011scaffoldnetworks, schuffenhauer2007scaffoldtree`.

La validación propuesta es por **triangulación**: que el enriquecimiento estadístico coincida con quimiotipos privilegiados del SNC ya conocidos `evans1988privileged`.

### 7.5 Riesgos documentados

**Acantilados de actividad.** Todos los métodos fallan desproporcionadamente en pares de estructura casi idéntica y actividad discontinua `vantilborg2022activitycliffs`. Los métodos de atribución suaves producirán explicaciones casi idénticas para estructuras casi idénticas, **justamente donde la relación real es discontinua**. Las explicaciones serán menos confiables en los compuestos limítrofes, que son los de mayor interés.

**Aprendizaje de atajos.** Sobre benchmarks derivados de ChEMBL, un modelo alimentado únicamente con el identificador de la diana y el laboratorio inferido iguala a los baselines estructurales `blevins2025cleverhans`. De ahí la recomendación de particiones disjuntas por fuente, no solo por andamio.

> **Advertencia:** esa última fuente es un preprint sin revisión por pares y debe citarse como tal.

---

## 8. Estado del arte y hueco identificado

No se identificó ningún trabajo publicado que implemente un clasificador de permeabilidad BBB basado en aprendizaje automático alimentando un clasificador de actividad neuroprotectora, específicamente sobre productos naturales y construido a partir de CMAUP, NPASS y ChEMBL.

Los antecedentes más próximos:

**Kato et al. (2025)** es el más cercano en arquitectura: biblioteca de ~1,700 constituyentes, ensayo PAMPA-BBB (611 resultados usables, 255 permeables), y una segunda etapa de neurotoxicidad sobre los 247 más permeables `kato2025bbbnp`. Es experimental, no computacional, y mide neurotoxicidad en lugar de neuroprotección.

**Gürbüz et al. (2025)** aplica la misma secuencia de dos etapas —permeabilidad seguida de inhibición de GSK-3β, CK-1δ y AChE— sobre 23 compuestos fenólicos naturales `gurbuz2025phenolic`. Directamente pertinente, pero de escala reducida y experimental.

**Yasir et al. (2026)** es la plantilla metodológica más próxima: Random Forest sobre 6,880 inhibidores de AChE de ChEMBL, seguido de filtro fisicoquímico de permeabilidad, acoplamiento molecular y validación experimental `yasir2026cnsache`. No trabaja con productos naturales, pero establece el mismo orden de etapas.

> **Advertencia de alcance:** la búsqueda leyó completos los tres trabajos más cercanos, pero no fue exhaustiva. La afirmación de novedad debe enunciarse con esa reserva.

---
