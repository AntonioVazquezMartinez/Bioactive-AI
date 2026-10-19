# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Bioactive AI is a Tec de Monterrey MNA capstone (TC5035.10, Team 7) with the Bioengineering Department. It uses supervised ML to predict the biological activity of natural bioactive compounds and to rank them, with a focus on neuroprotective and nootropic potential. The inputs are chemical, structural, biological and multi-omics descriptors. The README and the project deliverables are in Spanish, so keep new docs and notebook prose in Spanish unless told otherwise.

## Problem framing

The full notes and open questions from the advisor meetings are in `docs/planteamiento/`, and that folder is the source of truth. What matters for code:

- **Two-stage pipeline, SMILES in:** (1) classify BBB permeability (BBB+ / BBB-); (2) predict neuroprotective activity and the likely target. **A BBB− result does not discard a compound** — that much the data supports, since only 1,033 skeletons have measurements in both sets and the other 99% would be filtered on an unverified prediction. The team therefore treats the two stages as parallel evidence combined in the ranking, not as a cascade; whether combining the two predictions actually selects better than either alone is tested only on those 1,033 skeletons, as a separate proposal still waiting on the sponsor (decision C.3). Candidate data sources are CMAUP, NPASS and ChEMBL. The primary BBB dataset is the sponsor's curated B3DB-derived file documented below. A BBB- result doesn't rule a compound out, so don't treat stage 1 as a hard filter.
- **Explainability is required, not optional.** The advisors want to know which structural features drive a prediction, so favor interpretable models or substructure-level attributions.
- **Activity labels depend on concentration.** The same compound can flip between inactive and active depending on the µM tested, so pick and document a threshold when turning activity measurements into labels.
- **"No learnable pattern" is a valid result.** Report it honestly instead of tuning until something looks good.

## Technical decisions

Quick reference. The full context of each one — what was discarded, what it costs, and what changed it — is in `docs/decisiones.md`; the evidence is in `docs/referencias/`. Read both before changing any of them, and update the register in the same PR.

- **Data, stage 1:** the sponsor's curated file, `data/external/profesora/bbb_permeability_experimental.csv` — not the B3DB files we downloaded ourselves, which stay as a cross-check. It derives from B3DB but comes standardized and, crucially, cross-matched against COCONUT, which is what lets us separate natural products from synthetics. 7,811 rows, 7,805 with a class. logBB threshold −1.0. B3DB is CC0, so the data can live in the repo.
- **Do not filter by the `Group` column.** The Avance 1 EDA disproved the reading that group D means "conflicting labels": D has 3+ references (median 3) against C's median of 1, and no duplicated record anywhere in the set carries contradictory labels. The column is confounded with the label — filtering to A+B drops the minority class from 36.5% to 27.0%, which worsens the imbalance instead of removing noise. Use it to stratify, never to exclude.
- **Data, stage 2:** the sponsor's SNC activity file (202,647 records from ChEMBL, NPASS and CMAUP), with the ChEMBL 37 SQLite dump as a fallback — not the REST API, which was returning HTTP 500 as of 2026-09-22. Labels on two axes, which are easy to confuse: **how to label** (next bullet) and **where to cut** (10 µM primary, 1 µM as a sensitivity analysis shown alongside; 10 µM is pChEMBL ≥ 5).
- **Label all three sources with the same columns, not pChEMBL alone** — decided by the team on 17 October and still reversible, not ratified (decision 2.3). pChEMBL only exists for ChEMBL records, so labelling by it silently drops all 15,293 NPASS and CMAUP rows — the natural products this project exists to prioritize. The sponsor's dictionary (section 5) gives informed, homogeneous columns for the three sources; text-declared inactives are not used, and pairs with conflicting evidence are marked. **What is stored is the potency interval, not a label** (decision 2.10): the binary label at 10 µM or 1 µM is derived from it, so changing the cut or moving to regression (2.9) rebuilds nothing. **Report every metric by provenance**: a model that only sees where a compound came from already reaches 65% of the MCC of the chemistry, and on pairs that only NPASS has the AUROC drops from 0.83 to 0.57 (2.3).
- **Features:** RDKit 2D descriptors (217 in current RDKit) plus Morgan/ECFP4, 2048 bits, via `rdFingerprintGenerator` — not the deprecated `GetMorganFingerprintAsBitVect`. Note `radius=2` means ECFP4, since the name carries the diameter. Frozen embeddings from pretrained transformers do not beat this under scaffold splits.
- **Splits:** scaffold (Bemis-Murcko), never random. Random splits inflate results by 7–13 points. **And group by scaffold *and* connectivity skeleton, not by scaffold alone** — one skeleton can appear under different scaffolds, and separating them puts stereoisomers of the same compound on both sides of a fold. Measured on phase 1: scaffold alone gives 2,239 groups against 1,048 and inflates AUROC by 2.2 points and MCC by 6.2, which is more than what separates the three model families from each other. `grupos_cv` in `src/data_prep/splits.py` is the criterion; a figure that does not say how it grouped cannot be compared. Splitting disjointly by source does not work — source is not an attribute of the pair (decision 2.7) — and neither does splitting by article: one connected component holds 55.9% of the pairs.
- **Explainability:** at least two independent attribution methods, reporting only the substructures they agree on. Train a simple interpretable model alongside as a control. Sanity-check every structural claim against TPSA (<67 Å²) and HBD (≤1) first, since those dominate empirically.

Do not cite published BBBP performance numbers as a target — the same dataset yields Random Forest baselines anywhere from 0.681 to 0.7194 depending on who reports it. Run the baseline in-house.

## Current state

What exists:

- `notebooks/`: `01_EDA` (Avance 1), `01b_EDA_actividad_snc` (stage-2 EDA), `02_Feature_Eng` (Avance 2), `02b_Feature_Eng_actividad` (the phase-2 matrix and its reserved test) and `03_Baseline` (Avance 3). All five delivered.
- `src/data_prep/` (`download_data.py`, `splits.py`, `pares_fase2.py`), `src/features/molecular.py`, `src/evaluation/cv.py` and `src/models/` (`baseline.py`, `tareas.py`).

**`src/models/tareas.py` is what keeps the open decisions out of the code.** What is still open here is *what* is predicted, *from what*, and *where the cut falls* — so none of it lives inside the baseline: `cargar("actividad", umbral_um=1.0, representacion="descriptores+diana")`. Changing the threshold is changing a number, changing the representation is changing a word. The phase-1 matrix is the counter-example: Avance 2 first froze its columns over an already-transformed matrix, so changing the transform meant redoing the selection. That was fixed by filtering on raw values — modal value for near-constants, Spearman for redundancy — and the notebook now checks that the same 151 columns come out under all three transforms.

**And `src/evaluation/cv.py` is the harness, which takes pipelines rather than models.** Everything learned from the data — scaling, selection, imputation — has to be fitted inside the fold; a scaler fitted before splitting leaks the evaluation fold's mean and variance. It also breaks results down by subgroup in the same pass, because an aggregate figure does not describe the natural products, and it reports a subgroup only when its minority class reaches 20 cases. Its interval resamples **groups**, not rows: the row is not the independent unit, and `resumen()` says in its own docstring that its standard deviation is not a standard error, because the seeds share rows.
- `docs/`: `planteamiento/` (problem statement, marco teórico in three parts), `referencias/` (5 research documents plus `bibliografia.bib`, 211 entries), `reportes/avance-0/`, `avance-1/` and `avance-2/` (Quarto `.qmd` + rendered PDF), plus `glosario.md`, `decisiones.md` (the single page: decisions, proposals and assumptions by phase, each with the question still open; update it with each Avance), `fundamentos-desde-cero.md` (theory), `datos-contenido.md` (what each data file holds, its defects and the lineage diagram) and `guia-del-proyecto.md` (project and team). `roadmap-mlops.md` is an internal work plan (experiment tracking, reproducibility, CI) and is deliberately not published on the site.
- `data/external/profesora/` holds the sponsor's data with a README documenting licenses and caveats. The SNC activity file goes through Git LFS (see `.gitattributes`); NPASS is CC BY-NC, so it is non-commercial.
- The site is built from `_quarto.yml` + `scripts/prepare_site.py`; `visualizador.qmd` and `presentacion.qmd` are standalone pages.
- `requirements.txt` and `.gitignore` exist. `pyproject.toml` configures `ruff` (only errors and unused imports, not style; notebooks excluded) and `pytest` (`tests/`); install them with `pip install -r requirements-dev.txt`. `.github/workflows/checks.yml` runs on every PR to `main`: the site build, `scripts/verificar_sitio.py` (every internal link of the built site, not just `.html`), `scripts/verificar_decisiones.py`, `scripts/verificar_datos.py` (sha256 of every tracked data file against `data/MANIFEST.json`; if you change data on purpose, run it with `--escribir` and explain why in the PR), `ruff check` and `pytest`. All run locally too — run them before pushing. Every result goes through `src/tracking.py` into `experimentos/<id>/` (see `experimentos/README.md`); a number in a report needs a run behind it.

`models/` still holds an empty `Nuevo.txt` placeholder so git tracks it. Delete it when real serialized models arrive; `src/models/` already has real content.

Open work lives in GitHub issues, labelled by which deliverable it blocks. Open decisions live in `docs/decisiones.md`. Neither belongs in this file.

Each report folder reaches the bibliography and the CSL through a **symlink** to `docs/referencias/`, because typst refuses paths outside its own root and three copies had already drifted apart. Symlinks work on Linux and macOS; on native Windows without developer mode git checks them out as text files holding the path, and typst then fails on an invalid bibliography. Work on Linux, macOS or WSL.

Reports are rendered with Quarto to typst (no LaTeX). The rubric wants a cover page *and* a table of contents as separate pages, which Quarto's `toc` puts adjacent — hence the raw typst block at the top of each `.qmd`. Check every page of a rendered PDF before calling it done; typst sizes table columns by header length and silently produces broken tables.

## Intended layout and workflow

The work is organized around the course's weekly deliverables ("Avances"):

- `notebooks/`: a number means a deliverable — `01_EDA` (Avance 1), `02_Feature_Eng` (Avance 2), `03_Baseline` (Avance 3), `04_Models` (Avances 4–5). A **letter suffix means a companion analysis that is not itself a deliverable** but belongs with that number: `01b_EDA_actividad_snc` is the stage-2 EDA, companion to the stage-1 EDA of Avance 1.
- `src/`: reusable Python code taken out of the notebooks. `data_prep/` handles cleaning and transforms, `features/` generates chemical descriptors, and `models/` handles training and evaluation.
- `data/`: `raw/` holds untouched originals, `external/` holds third-party sources (PubChem, LipidMaps, etc.) and `processed/` holds model-ready data. Keep raw and heavy data out of git.
- `models/`: serialized trained models (`.pkl`, `.h5`).
- `docs/`: `planteamiento/` for the week 1–2 problem statement, `reportes/` for the executive summary and outreach piece, and `referencias/` for literature.

## Documentation is part of the work, not a pass at the end

Documentation lives in three places and each has a different job. Keeping them apart is what stops them from rotting.

| Where | Its job | Reader |
|:--|:--|:--|
| **This file** | how to work in this repo | whoever picks up the code |
| **The published site** | what the project does and why | advisor, sponsor, grader, new teammate |
| **`docs/decisiones.md`** | what was decided, what was discarded, what changed | the team, and the sponsor when consulted |

**Update them in the same PR as the change they describe**, never in a cleanup pass later. A decision reversed in code but still documented is worse than no documentation. If a PR changes a number, a decision or a file layout, the PR carries the doc change too.

**Close the issue from the PR body, and in English.** GitHub only acts on `Closes #N` / `Fixes #N` / `Resolves #N`; the Spanish «Cierra #N» reads fine and does nothing, so five finished issues (#51, #52, #55, #56, #57) sat open after their PRs merged and had to be closed by hand. The rest of the repo is in Spanish — this one line is not.

### The decision register

Every technical decision in this file has an entry in `docs/decisiones.md` with its context, what was discarded, what it costs, and, when it needs the sponsor, **the literal question** to ask. It does not record who decides.

The register is split by phase (common, 1, 2; ids like `1.3`, `2.5`, `C.2`) and by kind: decisions, proposals and assumptions (each with its status and what to do if it fails). Status vocabulary: *vigente* (we work on this basis, reversible), *propuesta*, *abierta*, *revisada* (decided, measured, changed — keeps the superseded version visible), *ratificada*. **Nothing is ratificada until the sponsor reviews it.** That is not a formality: two decisions have already been reversed by measuring, and the register keeps both versions.

When a decision changes, never rewrite it silently. Mark the previous version as superseded and say what changed it. `scripts/verificar_decisiones.py` checks that every entry declares a valid status.

**Don't let an entry sit blocked on the sponsor. Decide it, write what would change it, and keep it reversible.** Seven entries carried a «necesita su definición» marker and were the bottleneck for weeks. When the team finally went through them, three turned out to be answerable by a measurement nobody had run, and in two more the answer didn't change what had to be built — so only two actually needed her, and she ratified those in one meeting. A *vigente* entry that says what would change it costs almost nothing to reverse; an *abierta* entry waiting for an answer costs the whole week. Asking is still right when the criterion is genuinely hers (which activity types count as neuroprotection, whether a holdout exists), but the test is whether her answer would change the next commit, not whether it would be nice to have.

**And deciding an entry is not the same as arguing for it. A number that came from the sponsor needs its provenance recorded, not a justification invented for it.** Decision 2.3 carried, for three weeks, the claim that 10 µM is «approximately the maximum free concentration reachable with a conventional oral dose». It had no source, it is probably false in direction — free brain concentrations of CNS drugs are generally below 1 µM, so the argument favors 1 µM — and the same entry already held the evidence against it: its own table showed 1 µM recovers 4,879 more censored negatives and leaves the classes nearly balanced. The entry had the measurement and an argument written on top of it. What belongs there instead is where the number came from: 67.4% of the censored measurements are censored at exactly 10 µM and the ChEMBL comment on the declared-inactive rows says «Inhibition < 50% @ 10 uM», so 10 µM is the library screening concentration, inherited from the file. **The failure mode is specific: taking her number and supplying the reasoning she didn't give.** It was caught by a teammate reading the entry, not by any check, and the same review found the register's stated reason for excluding the text-inactives was false too — in both cases the real reason was already written one paragraph away. So: when an entry rests on something she decided, write *she decided it and here is where it comes from*; when it rests on a measurement, cite the run. Never fill the gap with plausible pharmacology.

### The site does not auto-discover files

This is the part that bites. A new document under `docs/` stays invisible until it is registered in **two** places: the `DOCUMENTOS` list in `scripts/prepare_site.py` and the navbar in `_quarto.yml`.

`prepare_site.py` copies documents into `contenido/`, converts backtick citation keys to `@key`, adds the YAML frontmatter Quarto needs, rewrites `.md`/`.ipynb` links to `.html` and copies the report PDFs. Run it by hand the first time you add a document — Quarto builds its file list before the pre-render hook. `.github/workflows/pages.yml` publishes on push to `main` and runs a link checker that fails the build; if you add content outside its watched paths, add the path.

**A document with mermaid blocks must be published as `.qmd`, not `.md`.** Quarto treats them as executable code and fails the whole site render otherwise. Mermaid also ignores the dark theme, so `estilos.scss` forces node, subgraph and edge-label colours per scheme — check any new diagram in both themes before shipping.

Use mermaid rather than image files for diagrams, so they can be edited in a PR and reviewed as a diff.

### Write so that nobody has to ask

Every reader is missing half the vocabulary: the AI side does not know what an efflux transporter is, the bioengineering side does not know what AUPRC is. **Define a term the first time it appears and link it to `docs/glosario.md`, which is the canonical definition.** If a term is not there yet, add it in the same PR — that is how the glossary stays complete without anyone auditing it.

**Organise a document by its subject, not by how we came to know it.** Headings like «what we hadn't used» or «what confirmed we measured right» describe our process; a reader who wasn't here needs the fact, not our relationship to it. Corrections belong inline, in a sentence, where the fact lives — not in a section of their own.

Two kinds of document are the exception, and in them the superseded version **is** the content: the decision register, and the research documents under `docs/referencias/`. There a recommendation that was later disproved stays visible as its own marked section, because the point is to show what changed and why — `02-datasets-bbb.md` is the model.

Say **why** a choice was made and not only what it was. Keep every number attached to where it came from — a figure with no notebook behind it cannot be checked, and this project has already had to retract two conclusions that looked solid until someone recomputed them. The record-level phase-2 figures the register cites come from `scripts/cifras_fase2.py`; run it rather than copying a number out of prose. **Say which file a figure counts**: the sponsor's dictionary describes the full 225,513-record activity file and we received 202,647, so the same quantity differs by ~11% between the two, and decision 2.3 carried the dictionary's numbers for a while as if they were ours.

## Keep this file honest, and keep the project small

**This file goes stale like any other document.** It has already been wrong twice: it said to train on groups A+B after the Avance 1 EDA disproved that, and it listed the reports as unpublished after they were published. Both were found by someone reading it, not by a check.

So: when you learn something that would have saved you an hour, write it here. When something here turns out wrong, fix it in the same PR that discovered it — do not leave it for later, because later is how it got wrong in the first place.

**Before adding anything, check whether it already has a home.** When a canonical place appears, the scattered copies become redundant and should go. This section replaced a list of eighteen glossary terms that was useful before `docs/glosario.md` existed and became duplication the day it did.

**Simplify continuously, but not at the cost of value or of the reader.** A shorter document that makes someone ask a teammate is not simpler, it moved the cost. The test for a cut is whether a competent reader with no context still gets there alone. Good candidates: anything stated twice, anything stale, any mechanism explained where its own code already explains it. Bad candidates: the *why* behind a decision, the evidence under a number, and the caveats — those are what make the rest trustworthy.

## Environment

```bash
# reproducible: las versiones exactas con las que se ejecutó el trabajo (Python 3.12, la del CI)
uv venv --python 3.12 env && source env/bin/activate
uv pip install -r requirements.lock

# o, si no usas uv: cotas mínimas, sin garantía de repetir las cifras
python -m venv env && source env/bin/activate && pip install -r requirements.txt
```

`requirements.txt` fija solo cotas inferiores, y entre versiones cambian en el tercer decimal las cifras de Random Forest; `requirements.lock` fija todo. Se genera con `uv pip compile requirements.txt --universal --python-version 3.12 -o requirements.lock --no-header`, y **`--universal` no es opcional**: sin él el lock sale resuelto para la plataforma donde se compiló y fija `nvidia-nccl-cu13`, que solo tiene wheels de Linux, así que `uv pip install -r requirements.lock` falla en macOS — justo en la máquina donde haría falta para comparar. Con `--universal` las dependencias de una sola plataforma llevan su marcador y las versiones son las mismas. Se usa **Python 3.12 por ser la versión en la que el trabajo se ejecutó y se verificó**, no por el CI (que no ejecuta los notebooks): pasar a otra obliga a reejecutar los notebooks y los experimentos y a revisar cada cifra. Ni siquiera eso hace idénticas las corridas entre sistemas operativos: la regresión logística con min–max da 0.481 de MCC en Linux, 0.489 en macOS con 3.12 y 0.497 en macOS con 3.14, así que **no se decide con una sola corrida**: lo que dependía de eso se mide con validación cruzada agrupada y su error estándar (`scripts/experimento_L_sortslice.py` y `scripts/experimento_escalado.py`, cada uno con su CSV versionado), y la primera celda del notebook 02 imprime las versiones con las que se ejecutó.

**Y para ejecutar un notebook hay que apuntar al intérprete del lock, no al que tenga a mano `jupyter`.** `nbconvert --execute` usa el kernel `python3` registrado en el sistema, que no tiene por qué ser el del entorno: el 02b se ejecutó así con Python 3.14 y RDKit 2026.03.6 en lugar de 3.12 y 2026.09.1, y una cifra cambió —los descriptores con |asimetría| > 2 pasaron de 154 a 150 de 201— sin que nada fallara. La primera celda imprime las versiones justamente para que esto se vea, y lo encontró una revisión leyendo esa salida, no una comprobación. Así que:

```bash
./env/bin/python -m ipykernel install --user --name bioactive --display-name "Python (lock)"
./env/bin/python -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.kernel_name=bioactive notebooks/02b_Feature_Eng_actividad.ipynb
```

Y los artefactos de `data/processed/` que el notebook lee se generan con el **mismo** intérprete, porque los descriptores los calcula RDKit.

**Y un notebook versionado con sus salidas parece ejecutado aunque su código no corra en orden.** El `02` tenía `LogisticRegression` usado en la celda 48 e importado en la 55: ejecutarlo secuencialmente fallaba con `NameError` mientras las salidas guardadas —de una corrida hecha en otro orden— se veían perfectas, y la rúbrica exige justamente que corra secuencialmente. Lo encontró una revisión al regenerar `data/processed/`, no una comprobación. `tests/test_notebooks_secuenciales.py` lo revisa ahora de forma estática en CI, recorriendo las celdas en orden y marcando los nombres que se usan antes de definirlos; es barato pero no detecta fallos en tiempo de ejecución, así que **antes de dar por bueno un notebook hay que ejecutarlo de principio a fin en una copia**:

```bash
cd notebooks && cp 02_Feature_Eng.ipynb _tmp.ipynb
../env/bin/python -m jupyter nbconvert --to notebook --execute --output-dir /tmp \
    --output ejecutado.ipynb --ExecutePreprocessor.kernel_name=bioactive _tmp.ipynb
rm _tmp.ipynb
```

Se ejecuta **una copia** y desde `notebooks/`, por dos razones: el notebook calcula `RAIZ` desde el directorio de trabajo, y reejecutar el original sobre otro sistema operativo cambiaría cifras que la documentación ya cita — el `02` quedó ejecutado en Linux y las corridas no son idénticas entre sistemas.
