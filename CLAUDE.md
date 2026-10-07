# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Bioactive AI is a Tec de Monterrey MNA capstone (TC5035.10, Team 7) with the Bioengineering Department. It uses supervised ML to predict the biological activity of natural bioactive compounds and to rank them, with a focus on neuroprotective and nootropic potential. The inputs are chemical, structural, biological and multi-omics descriptors. The README and the project deliverables are in Spanish, so keep new docs and notebook prose in Spanish unless told otherwise.

## Problem framing

The full notes and open questions from the advisor meetings are in `docs/planteamiento/`, and that folder is the source of truth. What matters for code:

- **Two-stage pipeline, SMILES in:** (1) classify BBB permeability (BBB+ / BBB-); (2) predict neuroprotective activity and the likely target. The two stages run in parallel on the same compound and their outputs combine at ranking time — stage 2 is not conditioned on stage 1. Candidate data sources are CMAUP, NPASS and ChEMBL. The primary BBB dataset is the sponsor's curated B3DB-derived file documented below. A BBB- result doesn't rule a compound out, so don't treat stage 1 as a hard filter.
- **Explainability is required, not optional.** The advisors want to know which structural features drive a prediction, so favor interpretable models or substructure-level attributions.
- **Activity labels depend on concentration.** The same compound can flip between inactive and active depending on the µM tested, so pick and document a threshold when turning activity measurements into labels.
- **"No learnable pattern" is a valid result.** Report it honestly instead of tuning until something looks good.

## Technical decisions

These come from the research in `docs/referencias/`, which holds the evidence, the caveats and the bibliography. Read the relevant document before changing any of them.

- **Data, stage 1:** the sponsor's curated file, `data/external/profesora/bbb_permeability_experimental.csv` — not the B3DB files we downloaded ourselves, which stay as a cross-check. It derives from B3DB but comes standardized and, crucially, cross-matched against COCONUT, which is what lets us separate natural products from synthetics. 7,811 rows, 7,805 with a class. logBB threshold −1.0. B3DB is CC0, so the data can live in the repo.
- **Do not filter by the `Group` column.** The Avance 1 EDA disproved the reading that group D means "conflicting labels": D has 3+ references (median 3) against C's median of 1, and no duplicated record anywhere in the set carries contradictory labels. The column is confounded with the label — filtering to A+B drops the minority class from 36.5% to 27.0%, which worsens the imbalance instead of removing noise. Use it to stratify, never to exclude.
- **Data, stage 2:** the sponsor's SNC activity file (202,647 records from ChEMBL, NPASS and CMAUP), with the ChEMBL 37 SQLite dump as a fallback — not the REST API, which was returning HTTP 500 as of 2026-09-22. Labels in two tiers: pChEMBL ≥ 5 primary, ≥ 6 as a robustness check, keeping the most potent value per compound-target pair.
- **Label through three routes, not pChEMBL alone.** pChEMBL only exists for ChEMBL records, so labelling by it silently drops all 15,293 NPASS and CMAUP rows — the natural products this project exists to prioritize — plus 54,498 censored measurements and 29,730 text-declared inactives. Use pChEMBL where it exists, exact concentration for the rest (which recovers 12,809 of the natural-product rows), and declared-inactive for the text comments and for censored records whose cutoff is ≥ 10 µM, the standard screening concentration. With all three applied, ≥ 5 leaves the set near balance at 1.6:1; the 6.7:1 that argued for ≥ 6 was an artifact of looking only at the dose-response subset.
- **Features:** RDKit 2D descriptors (217 in current RDKit) plus Morgan/ECFP4, 2048 bits, via `rdFingerprintGenerator` — not the deprecated `GetMorganFingerprintAsBitVect`. Note `radius=2` means ECFP4, since the name carries the diameter. Frozen embeddings from pretrained transformers do not beat this under scaffold splits.
- **Splits:** scaffold (Bemis-Murcko), never random. Random splits inflate results by 7–13 points. Where the data allows, make splits disjoint by source lab too.
- **Explainability:** at least two independent attribution methods, reporting only the substructures they agree on. Train a simple interpretable model alongside as a control. Sanity-check every structural claim against TPSA (<67 Å²) and HBD (≤1) first, since those dominate empirically.

Do not cite published BBBP performance numbers as a target — the same dataset yields Random Forest baselines anywhere from 0.681 to 0.7194 depending on who reports it. Run the baseline in-house.

## Current state

What exists:

- `notebooks/01_EDA.ipynb` (Avance 1, done) and `notebooks/02_Feature_Eng.ipynb` (Avance 2, in progress).
- `src/data_prep/` (`download_data.py`, `splits.py`) and `src/features/molecular.py`. No `src/models/` yet.
- `docs/planteamiento/` (problem statement, marco teórico), `docs/referencias/` (5 research documents plus `bibliografia.bib`), `docs/reportes/avance-0/` and `avance-1/` (Quarto `.qmd` + rendered PDF).
- `data/external/profesora/` holds the sponsor's data with a README documenting licenses and caveats. The SNC activity file goes through Git LFS (see `.gitattributes`); NPASS is CC BY-NC, so it is non-commercial.
- `requirements.txt` and `.gitignore` exist. There is still no test or lint setup — don't invent build or test commands, add them here once they exist.

`models/` and `src/models/` still hold an empty `Nuevo.txt` placeholder so git tracks them. Delete the placeholder when you add real content.

Reports are rendered with Quarto to typst (no LaTeX). The rubric wants a cover page *and* a table of contents as separate pages, which Quarto's `toc` puts adjacent — hence the raw typst block at the top of each `.qmd`. Check every page of a rendered PDF before calling it done; typst sizes table columns by header length and silently produces broken tables.

## Intended layout and workflow

The work is organized around the course's weekly deliverables ("Avances"):

- `notebooks/`: a number means a deliverable — `01_EDA` (Avance 1), `02_Feature_Eng` (Avance 2), `03_Baseline` (Avance 3), `04_Models` (Avances 4–5). A **letter suffix means a companion analysis that is not itself a deliverable** but belongs with that number: `01b_EDA_actividad_snc` is the stage-2 EDA, companion to the stage-1 EDA of Avance 1.
- `src/`: reusable Python code taken out of the notebooks. `data_prep/` handles cleaning and transforms, `features/` generates chemical descriptors, and `models/` handles training and evaluation.
- `data/`: `raw/` holds untouched originals, `external/` holds third-party sources (PubChem, LipidMaps, etc.) and `processed/` holds model-ready data. Keep raw and heavy data out of git.
- `models/`: serialized trained models (`.pkl`, `.h5`).
- `docs/`: `planteamiento/` for the week 1–2 problem statement, `reportes/` for the executive summary and outreach piece, and `referencias/` for literature.

## The published site is the project's memory

The site at <https://antoniovazquezmartinez.github.io/Bioactive-AI/> is not a byproduct of the repo — it is where the project explains itself. The test it has to pass: an advisor, the sponsor, a grader or a teammate joining late should be able to open it and understand what the project is doing and why, without reading code, digging through git history or asking anyone. Anything that lives only in someone's head, in a Slack thread or in a commit message fails that test.

Keep it current in the same PR as the change it describes, not in a cleanup pass later. A decision that is reversed in code but still documented on the site is worse than no documentation.

**The site does not auto-discover files.** This is the part that bites. A new document under `docs/` stays invisible until it is added in *two* places:

1. the `DOCUMENTOS` list in `scripts/prepare_site.py` (source path, destination path, subtitle), and
2. the navbar in `_quarto.yml`.

`scripts/prepare_site.py` copies the documents into `contenido/`, converts the backtick citation keys to `@key`, adds the YAML frontmatter Quarto needs and rewrites `.md`/`.ipynb` links to `.html`. Run it by hand the first time you add a document — Quarto builds its file list before the pre-render hook, so the target has to exist already. `.github/workflows/pages.yml` publishes on push to `main`, but only when one of its watched paths changes; if you add content somewhere else, add that path to the workflow too.

What belongs on the site:

- **A glossary.** Every domain term gets defined the first time it appears, and the glossary is the canonical definition the rest links to. The audience is mixed — the AI side does not know what an efflux transporter or a Murcko scaffold is, and the bioengineering side does not know what AUPRC or a scaffold split is. Write both directions. Terms we have already had to explain: SMILES, InChIKey, connectivity skeleton, TPSA, HBD/HBA, logP, logBB, Fsp3, BBB+/BBB−, Bemis-Murcko scaffold, scaffold split, ECFP4/Morgan, P-glycoprotein efflux, pChEMBL, MCC, AUPRC, PAINS, applicability domain.
- **Concept and mind maps.** Use Quarto's built-in mermaid blocks rather than image files, so a diagram can be edited in a PR and reviewed as a diff. The two-stage pipeline, the data lineage from each source to the model-ready table, and the map from research document to the decision it supports are the ones worth drawing.
- **The decision record.** Every technical decision in this file should be traceable on the site to the evidence behind it and, when it changes, to what changed it. `docs/referencias/02-datasets-bbb.md` is the model: the superseded recommendation stays visible and is marked as superseded, instead of being quietly rewritten.
- **Data provenance.** Where each file came from, its license, its known problems. `data/external/README.md` already does this and is published as the "Datos" page.
- **The executed notebooks**, which are what the deliverables actually link to.

Current gap worth closing: the reports in `docs/reportes/` are not published at all — `DOCUMENTOS` does not include them, so Avance 0 and Avance 1 exist only as PDFs in the repo.

Write for someone who is competent but has no context. Spell out the acronym the first time, say why a choice was made and not only what it was, and keep the numbers attached to where they came from.

## Environment

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
