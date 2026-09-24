# 01 — Representaciones moleculares: de SMILES a tabla

Investigación del 2026-09-22.

## Recomendación

**Descriptores fisicoquímicos 2D de RDKit (217 en la versión actual) concatenados con un fingerprint Morgan/ECFP4 binario de 2048 bits (`radius=2`), generados con la API vigente `rdFingerprintGenerator`.**

No es un compromiso por falta de recursos. Es lo que el benchmark más riguroso disponible encuentra estadísticamente indistinguible de, o mejor que, casi cualquier embedding congelado de un modelo de lenguaje químico bajo scaffold split. Y es la única familia que da atribución directa por substructura sin capas adicionales, que es justo el requisito de los asesores.

Opcionales, en orden de prioridad:

1. **MACCS keys (167 bits)** como fingerprint secundario auditable: cada bit *es* un patrón SMARTS con nombre, así que no requiere decodificación.
2. **Mordred (~1,826 descriptores)** solo si hacen falta descriptores 3D. Ver la advertencia de dependencias más abajo.
3. **Chemprop (D-MPNN)** si se quiere una comparación con GNN, no por ventaja predictiva sino por su módulo de racionalización por MCTS, el único enfoque de aprendizaje de representaciones encontrado que produce explicaciones por substructura de forma nativa.
4. **Embeddings congelados de ChemBERTa-2** solo como prueba de robustez.

## Familias disponibles

| Familia | Dimensión | Costo | ¿GPU? | Interpretabilidad por substructura |
|---|---|---|---|---|
| Descriptores RDKit 2D | 217 | ~1.7 ms/molécula | No | Por propiedad (logP, TPSA), no por substructura |
| Mordred | ~1,826 | ~18 ms/molécula | No | Mixta; muchos abstractos |
| Morgan/ECFP | 1024–4096 bits | <1 ms/molécula | No | **Sí, directa** vía `BitInfoMap` |
| MACCS | 167 bits fijos | <1 ms/molécula | No | **Sí, trivial**: cada bit es un SMARTS nombrado |
| ChemBERTa / ChemBERTa-2 | ~768 | Preentrenamiento ~48 h en V100 | Sí para entrenar | Débil, solo visualización de atención |
| MolFormer-XL | 768 | ~208 h·GPU en 16×V100 | Sí para entrenar | Débil |
| SELFormer | 58–87 M parámetros | ~11 días en 2×A5000 | Sí para entrenar | Débil |
| D-MPNN / Chemprop | 300 | Modesto a esta escala | Recomendable | **Fuerte** con el módulo MCTS |

El conteo de 217 descriptores se verificó ejecutando `Descriptors._descList` sobre RDKit 2026.03.6. Los papers más viejos citan 208; el número creció con las versiones.

## La evidencia: ¿los embeddings preentrenados le ganan a los fingerprints?

**En el régimen de este proyecto, no de forma confiable.**

La fuente decisiva es Praski, Adamczyk y Czech (2026), construida específicamente para responder esta pregunta: 25 modelos preentrenados evaluados como embeddings **congelados** alimentando clasificadores clásicos, contra fingerprints ECFP de conteo, sobre 25 datasets —incluyendo BBBP con n=2,039—, con **scaffold split explícito** y análisis bayesiano de Bradley-Terry en vez de comparación de medias.

Su conclusión, textual: *"casi todos los modelos neuronales muestran una mejora insignificante o nula sobre el fingerprint molecular ECFP base. Solo el modelo CLAMP, que también se basa en fingerprints moleculares, rinde significativamente mejor."*

| Representación | AUROC medio | Rango (de 25) |
|---|---|---|
| ECFP | 79.89% | 7.52 |
| ChemBERTa (MTR) | 79.99% | 7.32 |
| MolFormer | 79.80% | 9.50 |
| SELFormer | 73.18% | 20.04 |

Su recomendación práctica: *"Incluir siempre el fingerprint ECFP de conteo como baseline, junto con un clasificador basado en árboles."*

**Advertencia:** es un preprint de arXiv; no se identificó publicación con revisión por pares.

### La distinción que cambia la lectura

Congelado no es lo mismo que afinado. MolFormer-XL **afinado de extremo a extremo** reporta 93.7 en BBBP contra 71.4 de Random Forest: 22 puntos de diferencia, no un empate.

Eso no cambia la recomendación, porque el fine-tuning exige GPU, renuncia a la simplicidad de "embedding → modelo clásico" y no aporta explicación por substructura. Pero la tesis debe decir que los transformers no funcionan *en el flujo congelado que usamos*, no que no funcionan.

### Estudios específicos de BBB

- **Zhu y Liu (2025)**, BBBP, 1,955 compuestos, SVM: descriptores RDKit solos AUC **0.866**; Morgan de 2048 bits solo **0.771**; combinados 89.08% de exactitud. El split se describe solo como validación cruzada de 10 pliegues, no explícitamente scaffold.
- **Tiwari et al. (2026)**, B3DB, 1,054 compuestos, LightGBM, **con split aleatorio y scaffold, 30 repeticiones**: descriptores 2D solos R²=0.567 (aleatorio) / 0.418 (scaffold); ECFP4 solo 0.441 / 0.312; combinados 0.572 / 0.421. TopoPSA domina la importancia SHAP.

Conclusión: **los descriptores solos superan a Morgan solo**. Combinar nunca perjudicó, pero la contribución principal viene de los descriptores.

## Inconsistencia entre papers — advertencia metodológica

Los baselines reportados para el **mismo** dataset BBBP varían de forma notable:

- Random Forest: 0.681 / 0.714 / 0.7194 según la fuente.
- Embeddings: ChemBERTa-1 0.643, ChemBERTa-2 0.728, SELFormer 0.902, MolFormer-XL 0.937.

Esto refleja problemas conocidos de reproducibilidad en cómo cada grupo implementa "el" scaffold split de MoleculeNet. **No citar ningún número de BBBP de la literatura como referencia directa en la tesis. Correr el baseline propio.**

## Hiperparámetros de Morgan

De Rogers y Hahn (2010), el paper original de ECFP:

- **Radio contra diámetro.** El número del nombre es el *diámetro*: `radius=2` en RDKit equivale a ECFP4, y `radius=3` a ECFP6. Es un error frecuente al redactar metodología.
- **FCFP contra ECFP.** ECFP usa invariantes atómicos tipo Daylight; FCFP los sustituye por un código farmacofórico de 6 bits (donador/aceptor de H, ionizable, aromático, halógeno), para capturar características más abstractas basadas en el rol.
- **Longitud del vector.** El identificador nativo es un hash de 32 bits sin límite; plegarlo a 2048 pierde, según el paper, "solo una pequeña cantidad de información". **No se encontró ningún estudio controlado que compare 1024 contra 2048 contra 4096** midiendo el efecto en el modelo. Tratar 2048 como convención, no como evidencia.
- **Conteos contra binario.** RDKit soporta conteos de forma nativa. **Tampoco se encontró un benchmark riguroso** que los compare. Se espera que los modelos de árboles aprovechen la información de conteo, pero es expectativa, no dato.

## Código con la API vigente

`AllChem.GetMorganFingerprintAsBitVect` sigue funcionando pero emite advertencia de obsolescencia desde el logger de C++, no desde `warnings` de Python, lo que la hace fácil de pasar por alto. La API de generadores se amplió en el release 2023.03.1.

```python
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator, MACCSkeys, Descriptors
from rdkit.Avalon import pyAvalonTools

m = Chem.MolFromSmiles("CC(=O)Oc1ccccc1C(=O)O")  # aspirina

# Morgan / ECFP4 — API recomendada actual
mgen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
fp_bits  = mgen.GetFingerprint(m)
fp_arr   = mgen.GetFingerprintAsNumPy(m)
fp_count = mgen.GetCountFingerprintAsNumPy(m)

# Variante FCFP (invariantes farmacofóricos)
fcfp_gen = rdFingerprintGenerator.GetMorganGenerator(
    radius=2, fpSize=2048,
    atomInvariantsGenerator=rdFingerprintGenerator.GetMorganFeatureAtomInvGen())

# Bit -> substructura: el mecanismo central de explicabilidad
ao = rdFingerprintGenerator.AdditionalOutput(); ao.AllocateBitInfoMap()
fp = mgen.GetFingerprint(m, additionalOutput=ao)
bit_info = ao.GetBitInfoMap()          # {bit: ((atomIdx, radius), ...)}
atom_idx, radius = bit_info[389][0]
env = Chem.FindAtomEnvironmentOfRadiusN(m, radius, atom_idx)
submol = Chem.PathToSubmol(m, env)
print(Chem.MolToSmiles(submol))        # SMILES de la substructura

# Otros generadores (mismo patrón de AdditionalOutput)
rdkgen = rdFingerprintGenerator.GetRDKitFPGenerator(fpSize=2048)
apgen  = rdFingerprintGenerator.GetAtomPairGenerator(fpSize=2048)
ttgen  = rdFingerprintGenerator.GetTopologicalTorsionGenerator(fpSize=2048)

# MACCS: 167 bits fijos, API heredada pero vigente
maccs = MACCSkeys.GenMACCSKeys(m)

# Avalon
avfp = pyAvalonTools.GetAvalonFP(m, nBits=512)

# 217 descriptores fisicoquímicos
desc_dict = Descriptors.CalcMolDescriptors(m)
```

Este código va en `src/features/`.

## Trampa práctica: Mordred

El **21% de los descriptores de Mordred fallan con numpy ≥ 1.24**, porque se eliminó `np.float`. Hay que fijar una versión anterior de numpy o usar el fork comunitario. El repo original se reporta sin mantenimiento (fuente secundaria, sin confirmar). Si no hacen falta descriptores 3D específicos, evitarlo.

## Lo que no se pudo verificar

- **MolFormer-XL, versión publicada** en Nature Machine Intelligence: sin acceso, muro de login. Se usó el preprint de arXiv, que corresponde en esencia al manuscrito aceptado pero no se garantiza idéntico.
- **MoleculeNet** en el sitio de RSC: HTTP 403 pese a figurar como acceso abierto. Se usó arXiv v3; el apéndice con las tablas numéricas (pp. 36–65) no se leyó.
- **Gilmer et al. 2017 (MPNN)**: sin acceso al texto completo; se cita solo como contexto, sin extraer cifras.
- **Jin, Barzilay y Jaakkola 2020 (método MCTS)**: sin acceso directo; descrito vía la documentación de Chemprop.
- **GNNExplainer (Ying et al. 2019)**: leído parcial, vía resumen secundario.
- **Rogers y Hahn 2010**: ACS, PubMed y Europe PMC devolvieron 403 o muro de cookies. Se leyó vía un espejo verificado de la versión de registro, contrastado con los metadatos de Crossref.
- **Mapeo de bit a substructura para Avalon**: no se resolvió si existe.
- **Ablación de longitud de bits y conteos contra binario**: no se encontró ningún estudio controlado.
- **Praski et al. 2026**: no se identificó publicación con revisión por pares.
- **Dimensión del embedding de ChemBERTa (768)**: plausible por la convención de RoBERTa-base, no confirmada en el texto recuperado.
- **Li et al. 2026 (fingerprints libres de colisión)**: leído vía resumen automático del texto en PMC, no línea por línea. Menor confianza.
- **Mordred sin mantenimiento**: fuente secundaria.

Ningún paper encontrado dio señales de estar fabricado o mal atribuido; autores, revistas y DOIs se contrastaron contra Crossref o la página del editor.
