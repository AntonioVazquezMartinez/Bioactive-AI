# Investigación de referencia — Bioactive AI

Investigación documental realizada el 2026-09-22 para fundamentar las decisiones técnicas del proyecto. Se organizó en cuatro ramas independientes; cada una tiene su documento.

| Documento | Pregunta que responde |
|---|---|
| [01 — Representaciones moleculares](01-representaciones-moleculares.md) | ¿Cómo pasar de SMILES a una tabla de features? |
| [02 — Datasets de BBB](02-datasets-bbb.md) | ¿Qué datos usar para la etapa 1? |
| [03 — Explicabilidad](03-explicabilidad.md) | ¿Cómo justificar *por qué* el modelo predice lo que predice? |
| [04 — Datos de neuroactividad](04-datos-neuroactividad.md) | ¿Qué datos usar para la etapa 2? |

La bibliografía consolidada está en [`bibliografia.bib`](bibliografia.bib).

## Cómo leer estos documentos

Cada afirmación viene etiquetada según el nivel de acceso que se tuvo a la fuente:

- **Leído completo** — se abrió y leyó el texto primario.
- **Leído parcial** — solo resumen, abstract o una sección.
- **Sin acceso** — se cita el metadato, pero nadie del equipo ha leído el contenido.

Esta distinción no es burocracia. Cada documento cierra con una lista explícita de lo que **no** se pudo verificar. Antes de que cualquier cifra de aquí entre a un entregable, hay que confirmarla contra la fuente primaria, sobre todo si está marcada como parcial o sin acceso.

## Decisiones que salieron de esta investigación

**Etapa 1 — permeabilidad BBB.** Usar [B3DB](https://github.com/theochem/B3DB), filtrado por su columna `Group` de confiabilidad experimental. Umbral logBB = −1.0. Datos en CC0, así que se pueden commitear al repo.

**Etapa 2 — neuroactividad.** ChEMBL vía el dump SQLite del release 37, no vía API. Complementar con NPASS v3.0 y CMAUP 2.0. Etiquetado en dos niveles: pChEMBL ≥ 5 como primario, ≥ 6 como prueba de robustez.

**Representación.** Descriptores fisicoquímicos de RDKit (217) concatenados con Morgan/ECFP4 de 2048 bits. No embeddings preentrenados congelados.

**Explicabilidad.** Al menos dos métodos independientes, reportando como confirmadas solo las substructuras donde coinciden. Modelo interpretable simple entrenado en paralelo como control.

**Validación.** Scaffold split, nunca aleatorio. Idealmente también disjunto por fuente o laboratorio.

## Tres advertencias transversales

Aparecieron en más de una rama y conviene tenerlas presentes desde el inicio.

**No citar números de desempeño de la literatura como referencia.** Los baselines reportados para el *mismo* dataset BBBP varían entre 0.681 y 0.7194 para Random Forest según quién los reporte, porque cada grupo implementa el scaffold split a su manera. Hay que correr el baseline propio.

**El split aleatorio infla los resultados.** La brecha documentada entre split aleatorio (~98% de exactitud) y scaffold split (~0.92 AUROC) es de 7 a 13 puntos. Un resultado sospechosamente bueno casi siempre es fuga de datos, no mérito del modelo.

**Cuidado con el aprendizaje de atajos.** Hay evidencia preliminar de que, en benchmarks derivados de ChEMBL, la identidad del laboratorio que corrió el ensayo explica tanto como la estructura química. Conviene verificar que los splits sean disjuntos por fuente, no solo por andamio.

## Ruta de implementación sugerida

1. Bajar B3DB fijando un commit específico. Hacer el EDA del Avance 1.
2. Generar features: descriptores RDKit + Morgan, con la API vigente de `rdFingerprintGenerator`.
3. Baseline con scaffold split: Random Forest o XGBoost, más un modelo interpretable simple como control.
4. Explicabilidad: SHAP más un segundo método independiente; mapear bits a substructuras.
5. Análisis de enriquecimiento de fragmentos para llegar al enunciado grupal que piden los asesores.
6. Etapa 2 sobre ChEMBL/NPASS, con la lista de dianas curada a mano.
