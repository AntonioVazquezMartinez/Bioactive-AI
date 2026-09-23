# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Bioactive AI is a Tec de Monterrey MNA capstone (TC5035.10, Team 7) with the Bioengineering Department. It uses supervised ML to predict the biological activity of natural bioactive compounds and to rank them, with a focus on neuroprotective and nootropic potential. The inputs are chemical, structural, biological and multi-omics descriptors. The README and the project deliverables are in Spanish, so keep new docs and notebook prose in Spanish unless told otherwise.

## Problem framing

The full notes and open questions from the advisor meetings are in `docs/planteamiento/`, and that folder is the source of truth. What matters for code:

- **Two-stage pipeline, SMILES in:** (1) classify BBB permeability (BBB+ / BBB-); (2) for compounds that can reach the brain, predict neuroprotective activity and the likely target. Candidate data sources are CMAUP, NPASS and ChEMBL. The BBB dataset is still to be confirmed. A BBB- result doesn't rule a compound out, so don't treat stage 1 as a hard filter.
- **Explainability is required, not optional.** The advisors want to know which structural features drive a prediction, so favor interpretable models or substructure-level attributions.
- **Activity labels depend on concentration.** The same compound can flip between inactive and active depending on the µM tested, so pick and document a threshold when turning activity measurements into labels.
- **"No learnable pattern" is a valid result.** Report it honestly instead of tuning until something looks good.

## Current state

The repo is only a scaffold for now. Each directory holds an empty `Nuevo.txt` placeholder so git will track it. There is no code, no `requirements.txt`, no `.gitignore` and no test or lint setup yet. When you add real content to a directory, delete its placeholder. Don't invent build or test commands. Add them here once they exist.

## Intended layout and workflow

The work is organized around the course's weekly deliverables ("Avances"):

- `notebooks/`: numbered notebooks, one per deliverable: `01_EDA` (Avance 1), `02_Feature_Eng` (Avance 2), `03_Baseline` (Avance 3), `04_Models` (Avances 4–5, alternative models and evaluation).
- `src/`: reusable Python code taken out of the notebooks. `data_prep/` handles cleaning and transforms, `features/` generates chemical descriptors, and `models/` handles training and evaluation.
- `data/`: `raw/` holds untouched originals, `external/` holds third-party sources (PubChem, LipidMaps, etc.) and `processed/` holds model-ready data. Keep raw and heavy data out of git.
- `models/`: serialized trained models (`.pkl`, `.h5`).
- `docs/`: `planteamiento/` for the week 1–2 problem statement, `reportes/` for the executive summary and outreach piece, and `referencias/` for literature.

## Environment

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt   # requirements.txt not yet created
```
