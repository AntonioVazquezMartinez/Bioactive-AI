# 03 — Explicabilidad e interpretación

Investigación del 2026-09-22. Es la rama más importante del proyecto: los asesores pusieron la explicabilidad como requisito duro, y el objetivo final es una interpretación biológica que sostenga una publicación.

## Pipeline recomendado

1. **Modelo interpretable de control.** Regresión logística o árbol poco profundo sobre TPSA, cLogP, peso molecular, HBD, HBA, entrenado en paralelo al modelo principal. Sirve para contrastar: cuando las explicaciones del modelo complejo coinciden con los coeficientes del simple, eso es evidencia a favor; cuando discrepan, hay que investigar antes de publicar una afirmación biológica.
2. **Representación libre de colisiones.** Sort & Slice como opción principal.
3. **Al menos dos métodos de atribución independientes.** SHAP (`TreeExplainer` si el modelo es de árboles) más mapas de similitud de RDKit, que son estructuralmente distintos y resistentes al modo de falla de las moléculas fantasma. Opcionalmente contrafactuales con exmol para narrativas accionables por molécula.
4. **Mapeo de bit o átomo a substructura** con la API de `rdFingerprintGenerator` y `Draw.DrawMorganBit`, o mapas de similitud para atribución continua por átomo.
5. **Construcción del enunciado grupal**: agrupación por andamios de Murcko, matriz de presencia de fragmentos, test exacto de Fisher con corrección FDR, contrastado contra la magnitud media de atribución.
6. **Verificación contra la química conocida.** Toda afirmación estructural debe checarse contra TPSA, HBD, cLogP y CNS MPO. Una contradicción es señal de investigar el modelo o los datos, no de publicar.
7. **Reportar como confirmadas solo las substructuras donde coinciden dos métodos independientes.** Declarar los desacuerdos explícitamente.
8. **Verificar la procedencia de los datos** antes de confiar en todo lo anterior (ver la sección de Clever Hans).

## El problema de colisiones de bits

Morgan/ECFP comprime substructuras en un vector de longitud fija mediante hashing. Las colisiones están garantizadas en cuanto el número de substructuras supera el número de bits, y corrompen la interpretación: SHAP se ve forzado a asignar un solo valor a fragmentos con efectos químicos opuestos.

El problema es real. La solución que circula, en cambio, es más frágil de lo que aparenta.

### CF-MF — verificado con escepticismo

Li, Qu, Zhang y Zhong, *Journal of Cheminformatics* 18:46 (2026). Leído completo vía PMC.

El método hace crecer iterativamente la longitud del vector hasta eliminar colisiones, y luego compacta. Los autores reportan reducciones de RMSE del 8–17% y afirman que los fingerprints estándar de 512 bits ya presentan tasas de colisión del 11–75%, y los de 2048 bits entre 1% y 23%.

**Limitaciones, varias reconocidas por los propios autores:**

- **La validación usó splits aleatorios, no scaffold.** Los autores lo admiten. Es justo la debilidad metodológica que este proyecto no puede permitirse.
- Solo se probaron radios 1 a 3.
- La búsqueda iterativa es costosa a escala, y agregar moléculas nuevas puede exigir recalcular.
- **Adopción prácticamente nula.** Una sola cita, vista solo en un resumen de buscador y sin confirmar. No se encontraron herramientas de terceros que lo usen.
- El paquete `bit-collision-free-MF` existe en PyPI (v1.0.0, abril 2026, licencia MIT, clasificado como **Alpha**), con historial real desde v0.2.0 en mayo de 2025.

**Discrepancia importante:** el repo `github.com/Shifa-Zhong/CF-MF-project` **no es el código del paquete**. Es un volcado de resultados: sin README, 1 estrella, 0 forks, un solo commit. Los metadatos de PyPI apuntan a otro repo con guiones bajos, `bit_collision_free_MF`, **que no se verificó**. Hay que revisarlo antes de depender del paquete.

**Veredicto: método aislado, de un solo grupo, con ~6 meses de vida y en estado alpha. No es un estándar adoptado.** Pilotearlo, no construir el pipeline sobre él.

### Sort & Slice — la alternativa más segura

Dablander, Hanser, Lambiotte y Morris, *J. Cheminformatics* 16:135 (2024). Ordena las substructuras del conjunto de entrenamiento por frecuencia y conserva las L más frecuentes como fingerprint de longitud fija, libre de colisiones por construcción. Más simple que CF-MF, con más de un año de validación, y supera al plegado por hash.

**Recomendación: Sort & Slice como representación principal libre de colisiones**, con CF-MF como piloto comparativo si sobra tiempo.

Alternativas sin paquetes nuevos: subir `fpSize` (con rendimientos decrecientes) o usar el fingerprint de conteo no plegado nativo de RDKit, libre de colisiones por construcción.

## Trampas de SHAP sobre fingerprints

**1. SHAP puede atribuir importancia a moléculas fantasma.** Tamura, Jasial, Miyao y Funatsu, *Molecules* 26(16):4916 (2021), leído completo. El muestreo de fondo de `KernelExplainer` perturba el vector de bits directamente y produce combinaciones que **no corresponden a ninguna molécula ensamblable**. SHAP puede premiar un "fragmento" que no existe en ningún compuesto real del dataset. Su alternativa, un SVM con kernel de pares moleculares emparejados, se validó contra cristalografía de rayos X.

**2. Bits correlacionados y anidados.** Los entornos de radio 1 son subconjuntos de sus padres de radio 2, así que el reparto de valores de Shapley diluye el crédito entre features redundantes. Fundamento formal en Kumar et al., ICML 2020.

**3. La elección del conjunto de fondo cambia las atribuciones** de forma medible.

**4. Sensibilidad a hiperparámetros.** Las atribuciones se mueven con `fpSize` y el radio, que son decisiones sin contenido químico.

**5. Inestabilidad entre pliegues y semillas:** se afirma de manera informal en fuentes de practicantes, pero **no se encontró ningún estudio revisado por pares** que lo aísle para fingerprints moleculares. No citarlo como hecho establecido.

## Alternativas a SHAP

**Contrafactuales — exmol / MMACE.** Wellawatte, Seshadri y White, *Chemical Science* 13(13):3697–3705 (2022). Codifica la molécula como SELFIES, aplica mutaciones STONED, puntúa los mutantes con el modelo caja negra, agrupa por DBSCAN sobre distancia de Tanimoto y devuelve la molécula más cercana que invierte la predicción. Todos los candidatos son moléculas válidas y dibujables.

Un paper acompañante propone siete criterios para evaluar explicaciones moleculares y concluye que **SHAP es completo pero débil en accionabilidad y parsimonia, mientras que los contrafactuales son fuertes en ambas pero débiles en completitud: son complementarios, no sustitutos**. Su propio caso de estudio sobre permeabilidad BBB encontró que quitar o modificar grupos de ácido carboxílico era el factor clave — consistente con la química medicinal conocida, ya que un ácido ionizable sube TPSA y HBD. Es un precedente directo para este proyecto.

**Pares moleculares emparejados (MMP).** Herramienta madura y mantenida: `mmpdb` (BSD-3, ahora bajo la organización de RDKit en GitHub). Encuentra pares que difieren en exactamente una transformación y agrega la distribución del cambio de propiedad entre todos los pares que comparten esa transformación. Es **inherentemente grupal, no por molécula**, y produce justo el tipo de enunciado que quieren los asesores: "intercambiar el fragmento A por B cambia la probabilidad de cruce en una mediana Δ sobre N pares". Requiere densidad de datos suficiente; hay que verificarla antes de comprometerlo como método principal.

**Pesos de atención de GNN — usar con cautela.** La evidencia específica para moléculas es contundente: Rao, Zheng, Lu y Yang, *Patterns* 3(12):100628 (2022), leído completo, construyó 5 benchmarks con substructuras de referencia y comparó 6 métodos de atribución contra 7 químicos medicinales.

| Método | AUROC de atribución |
|---|---|
| Integrated Gradients | **0.675** |
| CAM | 0.520 |
| SmoothGrad | 0.467 |

Los métodos cercanos a la atención rinden **casi como el azar**. La mejor combinación (CMPNN + Integrated Gradients) superó a los químicos en identificación de substructuras hepatotóxicas (92% contra 50–68%).

**No usar pesos de atención como canal principal de explicación.** Si se usa una GNN, preferir Integrated Gradients y validar contra un segundo método.

**Mapas de similitud de RDKit.** `SimilarityMaps.GetSimilarityMapForModel`: para cada átomo recalcula el fingerprint sin su contribución, reevalúa el modelo y usa la diferencia como peso, pintado como mapa de calor sobre la estructura 2D. No es teórico-de-juegos, son diferencias finitas, pero como perturba un átomo de una molécula **real** en vez de un vector de bits hasheado, **evita estructuralmente el modo de falla de las moléculas fantasma**. Recomendado como capa de verificación visual por defecto.

## Críticas que conviene conocer antes de construir

**1. "Importante para el modelo" no es "importante biológicamente."** Rodríguez-Pérez y Bajorath, *J. Comput.-Aided Mol. Des.* 34(10):1013–1026 (2020), leído completo. Cita: *"las características decisivas para las predicciones pueden o no ser responsables de actividades específicas."* Hallazgo secundario útil: kernel-SHAP y tree-SHAP concuerdan bien sobre ensambles de árboles (correlación 0.83–0.84), así que en modelos de árboles el riesgo principal no es la inestabilidad numérica sino la brecha semántica entre importancia para el modelo y causalidad biológica.

**2. Aprendizaje de atajos en predicción de bioactividad.** Blevins y Quigley, arXiv:2512.20924 (diciembre 2025), **preprint sin revisión por pares**, leído completo. Sobre benchmarks derivados de ChEMBL, un modelo alimentado únicamente con el ID de la diana y el laboratorio inferido que corrió el ensayo **iguala a los baselines basados en estructura**. Buena parte de la señal aparente de relación estructura-actividad es identidad del laboratorio.

**Acción concreta:** si los datos vienen de fuentes públicas, verificar que los splits sean disjuntos **por autor o laboratorio**, no solo por andamio. Si no, tanto la exactitud como las explicaciones pueden reflejar quién hizo el experimento. Es un prerrequisito, no un detalle opcional.

**3. Los acantilados de actividad son un punto ciego sistemático.** van Tilborg, Alenicheva y Grisoni, *JCIM* 62(23):5938–5951 (2022). 24 métodos sobre 30 dianas: todos fallan desproporcionadamente en pares con estructura casi idéntica y actividad discontinua; el ML clásico con descriptores supera ahí a los modelos profundos. Implicación: los métodos de atribución suaves darán explicaciones casi idénticas para estructuras casi idénticas, **justo donde la relación real es discontinua**. Las explicaciones serán menos confiables precisamente en los compuestos BBB+/BBB− limítrofes, que son los que más importan.

**4. Crítica general a la explicación post-hoc.** Rudin, *Nature Machine Intelligence* 1(5):206–215 (2019). Una explicación post-hoc es un modelo aproximador aparte, sin garantía de reflejar el razonamiento real del modelo original. De ahí el punto 1 del pipeline.

**5. El desacuerdo entre métodos es lo esperado, no la excepción.** El benchmark de *Patterns* muestra AUROC de atribución entre 0.467 y 0.675 para 6 métodos sobre los mismos modelos y datos. **Nunca presentar la salida de un solo método como "la razón".**

## Del nivel molécula al enunciado grupal

Dato que conviene comunicar a los asesores: **no existe un método citable listo para usar** que haga "enriquecimiento de fragmentos ponderado por SHAP" de punta a punta. Es una síntesis defendible de piezas establecidas, no un estándar con una cita única. Decirlo así es más honesto que implicar un precedente inexistente.

**Andamios de Murcko** (API vigente de RDKit):

```python
from rdkit.Chem.Scaffolds import MurckoScaffold
MurckoScaffold.GetScaffoldForMol(mol)        # anillos + conectores
MurckoScaffold.MakeScaffoldGeneric(mol)      # esqueleto topológico
MurckoScaffold.MurckoScaffoldSmiles(smiles=...)
```

Para cada molécula predicha BBB+, calcular el andamio y agrupar por cadena idéntica. Eso es literalmente "estas N moléculas comparten el fragmento X".

**Jerarquías de andamios** cuando la agrupación plana fragmenta demasiado: el Scaffold Tree (Schuffenhauer et al. 2007) y sobre todo **las redes de andamios de Varin et al. (2011)**, que calculan enriquecimiento estadístico de andamios entre activos e inactivos. Es el trabajo previo más cercano a lo que piden los asesores.

**Estadística de enriquecimiento:** test exacto de Fisher o hipergeométrico sobre una tabla 2×2 (fragmento presente/ausente × BBB+/BBB−), con corrección FDR de Benjamini-Hochberg sobre todos los fragmentos evaluados. Fragmentación vía BRICS/RECAP de RDKit o coincidencia directa de SMARTS. **No hay un paper canónico único para esta combinación genérica**; conviene declarar ese vacío en vez de fabricar un precedente.

**Estructuras privilegiadas.** El término viene de Evans et al. (1988): "un solo marco molecular capaz de proveer ligandos para receptores diversos". Para este proyecto: minar andamios enriquecidos entre los BBB+ activos y contrastarlos contra quimiotipos privilegiados conocidos del SNC (benzodiazepina, fenotiazina, indol, piperazina). **Esa triangulación —enriquecimiento estadístico independiente que coincide con quimiotipos ya conocidos— es la forma más defendible de enunciar la afirmación para una publicación.**

### Pipeline concreto

1. Puntuar todas las moléculas y extraer atribuciones por molécula.
2. Mapear bits o átomos importantes de vuelta a substructuras reales.
3. Calcular andamio de Murcko y marco genérico por molécula.
4. Construir la matriz fragmento × molécula.
5. Test de Fisher por fragmento, corrección FDR, ordenar por razón de momios y significancia.
6. Para los fragmentos más enriquecidos, agregar por separado la magnitud media de atribución con y sin el fragmento. Son dos líneas de evidencia que se refuerzan: prevalencia estadística **y** atribución del modelo.
7. Contrastar contra quimiotipos privilegiados del SNC y las reglas de propiedades antes de escribir cualquier interpretación biológica.
8. Presentar como rejilla de estructuras agrupada por andamio más una tabla de enriquecimiento (fragmento, N, razón de momios, p con FDR, atribución media).
9. Donde la densidad de datos lo permita, complementar con MMP, que responde la pregunta de sabor causal que el enriquecimiento puro no puede.

## Química medicinal establecida: valores de verificación

La referencia principal recomendada es **Tiwari, Mądra-Gackowska, Gackowski y Szeleszczuk**, *Pharmaceutics* 18(8):967 (2026), acceso abierto, leído completo. Rederiva los umbrales sobre B3DB (los mismos 1,058 compuestos con logBB).

- **TPSA es el mejor predictor individual**, con umbral óptimo en **66.8 Å²** (AUC 0.746), notablemente más estricto que el clásico ~90 Å², que el paper califica de "demasiado permisivo".
- **Regla de dos features: TPSA < 67 Å² y HBD ≤ 1** → 96.6% de precisión para BBB+, especificidad 0.852, cubre el 53.5% del dataset.
- Sobre el mismo dataset, esa regla simple **supera** a las compuestas clásicas: CNS MPO ≥ 4 da AUC 0.625, Lipinski 0.546, Veber 0.566.
- Individuales más débiles: peso molecular ≤442 Da (AUC 0.583), cLogP > 2.3 (0.617), HBD ≤ 1 (0.699), HBA ≤ 4 (0.673).

**Implicación práctica: verificar las explicaciones del modelo primero contra TPSA y HBD, que dominan empíricamente. No dar el mismo peso a peso molecular o logP.**

Nota sobre el desbalance: en ese subconjunto de 1,058 compuestos con logBB, la proporción es 930 BBB+ (87.9%) contra 128 BBB− (12.1%), bastante más desbalanceada que el conjunto categórico completo de B3DB. Conviene tenerlo en cuenta al comparar.

**CNS MPO** (Wager et al. 2010): seis parámetros —cLogP, cLogD a pH 7.4, peso molecular, TPSA, HBD y pKa del centro más básico— cada uno puntuado de 0 a 1 mediante una función de deseabilidad, sumando un compuesto de 0 a 6.

## Lo que no se pudo verificar

- **El repo fuente real del paquete CF-MF** (`bit_collision_free_MF`): **nunca se abrió**, solo se infirió de los metadatos de PyPI. Verificar antes de depender de él.
- La cifra de ~1 cita de CF-MF: solo de un resumen de buscador.
- Texto completo en pubs.acs.org de: Clark 1999, Wager et al. 2010 (CNS MPO), Ghose et al. 1999, Zhong y Guan 2023, Hussain y Rea 2010, Bemis y Murcko 1996, Schuffenhauer et al. 2007, Varin et al. 2011 — todos devolvieron 403. Se usaron abstracts o corroboración secundaria.
- **Rudin 2019** en Nature Machine Intelligence: muro de pago; el preprint arXiv:1811.10154 se localizó pero no se leyó a fondo.
- **Sanchez-Lengeling et al. (NeurIPS 2020)**: PDF localizado, no leído a fondo; no se extrajeron resultados numéricos.
- **Wu et al. 2023** (Nature Communications, enmascaramiento de substructuras en GNN): solo resumen de buscador. **No citar sin verificar.**
- Un segundo paper de Rodríguez-Pérez y Bajorath en *J. Med. Chem.*: solo resúmenes. Excluido de la bibliografía.
- Seguimiento de CNS MPO de 2016 y la extensión "TEMPO": DOIs solo vía búsqueda. Excluidos.
- La inestabilidad de SHAP entre pliegues y semillas como afirmación general: sin estudio dedicado.
