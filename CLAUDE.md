# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Bioactive AI is a Tec de Monterrey MNA capstone (TC5035.10, Team 7) with the Bioengineering Department. It uses supervised ML to predict the biological activity of natural bioactive compounds and to rank them, with a focus on neuroprotective and nootropic potential. The inputs are chemical, structural, biological and multi-omics descriptors. The README and the project deliverables are in Spanish, so keep new docs and notebook prose in Spanish unless told otherwise.

## Problem framing

The full notes and open questions from the advisor meetings are in `docs/planteamiento/`, and that folder is the source of truth. What matters for code:

- **Two-stage pipeline, SMILES in:** (1) classify BBB permeability (BBB+ / BBB-); (2) predict neuroprotective activity and the likely target. **A BBB− result does not discard a compound** — that much the data supports, since only 1,033 skeletons have measurements in both sets and the other 99% would be filtered on an unverified prediction. Whether the stages are therefore independent, or sequential without filtering, is a framing the sponsor has not confirmed: see decision 5. Candidate data sources are CMAUP, NPASS and ChEMBL. The primary BBB dataset is the sponsor's curated B3DB-derived file documented below. A BBB- result doesn't rule a compound out, so don't treat stage 1 as a hard filter.
- **Explainability is required, not optional.** The advisors want to know which structural features drive a prediction, so favor interpretable models or substructure-level attributions.
- **Activity labels depend on concentration.** The same compound can flip between inactive and active depending on the µM tested, so pick and document a threshold when turning activity measurements into labels.
- **"No learnable pattern" is a valid result.** Report it honestly instead of tuning until something looks good.

## Technical decisions

Quick reference. The full context of each one — what was discarded, what it costs, and what changed it — is in `docs/decisiones.md`; the evidence is in `docs/referencias/`. Read both before changing any of them, and update the register in the same PR.

- **Data, stage 1:** the sponsor's curated file, `data/external/profesora/bbb_permeability_experimental.csv` — not the B3DB files we downloaded ourselves, which stay as a cross-check. It derives from B3DB but comes standardized and, crucially, cross-matched against COCONUT, which is what lets us separate natural products from synthetics. 7,811 rows, 7,805 with a class. logBB threshold −1.0. B3DB is CC0, so the data can live in the repo.
- **Do not filter by the `Group` column.** The Avance 1 EDA disproved the reading that group D means "conflicting labels": D has 3+ references (median 3) against C's median of 1, and no duplicated record anywhere in the set carries contradictory labels. The column is confounded with the label — filtering to A+B drops the minority class from 36.5% to 27.0%, which worsens the imbalance instead of removing noise. Use it to stratify, never to exclude.
- **Data, stage 2:** the sponsor's SNC activity file (202,647 records from ChEMBL, NPASS and CMAUP), with the ChEMBL 37 SQLite dump as a fallback — not the REST API, which was returning HTTP 500 as of 2026-09-22. Labels on two axes, which are easy to confuse: **how to label** (three routes, next bullet) and **where to cut** (pChEMBL ≥ 5 primary, ≥ 6 as a robustness check), keeping the most potent value per compound-target pair.
- **Label through three routes, not pChEMBL alone** — vigente, pending the sponsor's ratification (decision 7 is open). pChEMBL only exists for ChEMBL records, so labelling by it silently drops all 15,293 NPASS and CMAUP rows — the natural products this project exists to prioritize — plus 54,498 censored measurements and 29,730 text-declared inactives. Use pChEMBL where it exists, exact concentration for the rest (which recovers 12,809 of the natural-product rows), and declared-inactive for the text comments and for censored records whose cutoff is ≥ 10 µM, the standard screening concentration. With all three applied, ≥ 5 leaves the set near balance at 1.6:1; the 6.7:1 that argued for ≥ 6 was an artifact of looking only at the dose-response subset.
- **Features:** RDKit 2D descriptors (217 in current RDKit) plus Morgan/ECFP4, 2048 bits, via `rdFingerprintGenerator` — not the deprecated `GetMorganFingerprintAsBitVect`. Note `radius=2` means ECFP4, since the name carries the diameter. Frozen embeddings from pretrained transformers do not beat this under scaffold splits.
- **Splits:** scaffold (Bemis-Murcko), never random. Random splits inflate results by 7–13 points. Where the data allows, make splits disjoint by source lab too.
- **Explainability:** at least two independent attribution methods, reporting only the substructures they agree on. Train a simple interpretable model alongside as a control. Sanity-check every structural claim against TPSA (<67 Å²) and HBD (≤1) first, since those dominate empirically.

Do not cite published BBBP performance numbers as a target — the same dataset yields Random Forest baselines anywhere from 0.681 to 0.7194 depending on who reports it. Run the baseline in-house.

## Current state

What exists:

- `notebooks/`: `01_EDA` (Avance 1, delivered), `01b_EDA_actividad_snc` (stage-2 EDA), `02_Feature_Eng` (Avance 2, notebook done, report pending).
- `src/data_prep/` (`download_data.py`, `splits.py`) and `src/features/molecular.py`. No `src/models/` yet.
- `docs/`: `planteamiento/` (problem statement, marco teórico in three parts), `referencias/` (5 research documents plus `bibliografia.bib`, 210 entries), `reportes/avance-0/` and `avance-1/` (Quarto `.qmd` + rendered PDF), plus `glosario.md`, `decisiones.md` and `linaje-datos.md`.
- `data/external/profesora/` holds the sponsor's data with a README documenting licenses and caveats. The SNC activity file goes through Git LFS (see `.gitattributes`); NPASS is CC BY-NC, so it is non-commercial.
- The site is built from `_quarto.yml` + `scripts/prepare_site.py`; `visualizador.qmd` and `presentacion.qmd` are standalone pages.
- `requirements.txt` and `.gitignore` exist. There is still no test or lint setup — don't invent build or test commands, add them here once they exist. The only checks that run are the link checker in CI and `scripts/verificar_decisiones.py`.

`models/` and `src/models/` still hold an empty `Nuevo.txt` placeholder so git tracks them. Delete the placeholder when you add real content.

Open work lives in GitHub issues, labelled by which deliverable it blocks. Open decisions live in `docs/decisiones.md`. Neither belongs in this file.

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

### The decision register

Every technical decision in this file has an entry in `docs/decisiones.md` with its context, what was discarded, what it costs, and two fields that make it actionable: **who decides** (team, sponsor, or both) and, when the sponsor decides, **the literal question** to ask.

Status vocabulary: *vigente* (we work on this basis, reversible), *propuesta*, *abierta*, *revisada* (decided, measured, changed — keeps the superseded version visible), *ratificada*. **Nothing is ratificada until the sponsor reviews it.** That is not a formality: two decisions have already been reversed by measuring, and the register keeps both versions.

When a decision changes, never rewrite it silently. Mark the previous version as superseded and say what changed it. `scripts/verificar_decisiones.py` checks that every decision needing the sponsor states its question and appears in the consultation.

### The site does not auto-discover files

This is the part that bites. A new document under `docs/` stays invisible until it is registered in **two** places: the `DOCUMENTOS` list in `scripts/prepare_site.py` and the navbar in `_quarto.yml`.

`prepare_site.py` copies documents into `contenido/`, converts backtick citation keys to `@key`, adds the YAML frontmatter Quarto needs, rewrites `.md`/`.ipynb` links to `.html` and copies the report PDFs. Run it by hand the first time you add a document — Quarto builds its file list before the pre-render hook. `.github/workflows/pages.yml` publishes on push to `main` and runs a link checker that fails the build; if you add content outside its watched paths, add the path.

**A document with mermaid blocks must be published as `.qmd`, not `.md`.** Quarto treats them as executable code and fails the whole site render otherwise. Mermaid also ignores the dark theme, so `estilos.scss` forces node, subgraph and edge-label colours per scheme — check any new diagram in both themes before shipping.

Use mermaid rather than image files for diagrams, so they can be edited in a PR and reviewed as a diff.

### Write so that nobody has to ask

Every reader is missing half the vocabulary: the AI side does not know what an efflux transporter is, the bioengineering side does not know what AUPRC is. **Define a term the first time it appears and link it to `docs/glosario.md`, which is the canonical definition.** If a term is not there yet, add it in the same PR — that is how the glossary stays complete without anyone auditing it.

**Organise a document by its subject, not by how we came to know it.** Headings like «what we hadn't used» or «what confirmed we measured right» describe our process; a reader who wasn't here needs the fact, not our relationship to it. Corrections belong inline, in a sentence, where the fact lives — not in a section of their own. The exception is the decision register, where the superseded version *is* the content.

Say **why** a choice was made and not only what it was. Keep every number attached to where it came from — a figure with no notebook behind it cannot be checked, and this project has already had to retract two conclusions that looked solid until someone recomputed them.

## Keep this file honest, and keep the project small

**This file goes stale like any other document.** It has already been wrong twice: it said to train on groups A+B after the Avance 1 EDA disproved that, and it listed the reports as unpublished after they were published. Both were found by someone reading it, not by a check.

So: when you learn something that would have saved you an hour, write it here. When something here turns out wrong, fix it in the same PR that discovered it — do not leave it for later, because later is how it got wrong in the first place.

**Before adding anything, check whether it already has a home.** When a canonical place appears, the scattered copies become redundant and should go. This section replaced a list of eighteen glossary terms that was useful before `docs/glosario.md` existed and became duplication the day it did.

**Simplify continuously, but not at the cost of value or of the reader.** A shorter document that makes someone ask a teammate is not simpler, it moved the cost. The test for a cut is whether a competent reader with no context still gets there alone. Good candidates: anything stated twice, anything stale, any mechanism explained where its own code already explains it. Bad candidates: the *why* behind a decision, the evidence under a number, and the caveats — those are what make the rest trustworthy.

## Environment

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
