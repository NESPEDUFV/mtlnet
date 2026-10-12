# mtlnet

Code and result records for the master's dissertation

> **Multitask Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the
> Check-in-Level Representation.** Vitor Hugo De Oliveira Silva. Advisor: Fabrício Aguiar Silva.
> Programa de Pós-Graduação em Ciência da Computação, Universidade Federal de Viçosa, 2026.

The dissertation's appendices name files in this repository by path, for example
`src/data/folds.py`. Each of those paths resolves here as named.

## What is in it

| path | what it is |
|---|---|
| `src/` | the system that produced every number in the dissertation: models, losses, training, fold construction (`src/data/folds.py`), scoring (`src/tracking/score_joint_best.py`) |
| `research/embeddings/` | the representation trainers (Check2HGI in `check2hgi/`, plus DGI, HGI and the others compared) |
| `research/baselines/`, `scripts/baselines/` | the external baselines (STAN, POI-RGNN, ReHDM, CTLE, HMT-GRN) |
| `research/reproducibility/` | the statistical scripts of Chapter 5 (`mobiwac_v18/wilcoxon_v18.py`) |
| `scripts/` | the command-line entry point (`scripts/train.py`) and the study drivers |
| `pipelines/`, `experiments/` | input generation and declarative configurations |
| `tests/` | the test suite of `src/` |
| `docs/studies/closing_data/v18/` | the final study (v18): recipe, provenance of every cell, methodology |
| `docs/results/closing_data/v18/` | its per-seed outputs, including `joint_best_perfold.json` |
| `docs/reproducibility/mobiwac_v17/` | the statistical protocol and the joint-model scoring record |
| `articles/dissertacao/` | the LaTeX source of the dissertation (`src/`), its review history and the defense material |
| `mtlcheck/` | a later, independent reimplementation; see below |

## Two implementations: do not mix their numbers

The root of this repository is the system that produced the dissertation's results.

`mtlcheck/` is a reimplementation written from scratch after the dissertation was submitted. It
uses a different evaluation protocol (nested 70/10/20 user splits, out-of-fold pooled metrics), so
**its numbers are not comparable with the dissertation's**. It installs on its own
(`mtlcheck/pyproject.toml`); its tests are in `mtlcheck/tests/`.

## Data is not included

No check-in data is redistributed. Obtain the two collections from their sources:

- Gowalla, the U.S. states: Figshare, DOI `10.6084/m9.figshare.22126586.v2` (CC0).
- Istanbul: Massive-STEPS on Hugging Face, `CRUISEResearchGroup/Massive-STEPS-Istanbul` (Apache-2.0).

Place them under `data/` (or set `DATA_ROOT`). `src/configs/paths.py` shows the layout. `data/` and
`output/` are excluded by `.gitignore`.

## Reproducing

**Check the statistics, no data needed.** The per-fold outputs are committed, so the Chapter 5
tests rerun as they are:

```bash
pip install -r requirements.txt
python research/reproducibility/mobiwac_v18/wilcoxon_v18.py
```

The script first reproduces each delivered cell mean (it prints `ok` per state), then runs the
pre-registered tests.

**Retrain from the data.** The recipe for every cell, with the commit each was produced from, is in
[`docs/studies/closing_data/v18/PROVENANCE.md`](docs/studies/closing_data/v18/PROVENANCE.md). Pass
`--canon none` and write the recipe out in full. A bare `scripts/train.py --task mtl` injects an older
default recipe and an older representation, and reproduces nothing in the dissertation.

## Provenance

This repository starts without history. It is a snapshot of
[`VitorHugoOli/PoiMtlNet`](https://github.com/VitorHugoOli/PoiMtlNet) at commit `f96f79cf`, trimmed to
what the dissertation needs, plus the `mtlcheck/` package at commit `9be7897a` of the author's development branch
`rewrite/mtlcheck`, which is not published.

Comments and documents here sometimes name files that were left out. Every such path resolves in the
source repository at that commit:
`https://github.com/VitorHugoOli/PoiMtlNet/tree/f96f79cf/<path>`.

## License

The code is under the MIT licence; see [`LICENSE`](LICENSE). The dissertation text in
`articles/dissertacao/` and the published articles it reproduces keep their own copyright; see
[`articles/dissertacao/COPYRIGHT.md`](articles/dissertacao/COPYRIGHT.md).
