# Research Tooling / Data-Engineering Codebase — Evidence Ledger

**Purpose.** Concrete, verifiable evidence for a possible "Other Scientific
Contributions" appendix item describing the research tooling and
data-engineering codebase built during the dissertation research.

**Method.** Read-only survey of `/Users/vitor/Desktop/mestrado/ingred` this
session. Every number below is annotated with the command or file path that
produced it. Nothing is estimated. Where a documentation claim and the code
disagree, both are reported.

**Fail-closed labels used throughout:**
- **[code]** — implementation file(s) exist on disk; path given.
- **[doc]** — described in `docs/context/*.md`; verified against code where possible.
- **[disk-artifact]** — a data file exists on disk (evidences an output, not necessarily the current code path that produced it).

---

## 1. The Gowalla ETL (concrete)

**Entry point.** `pipelines/etl/gowalla.pipe.py` → `src/etl/gowalla/main.py::run()`. **[code]**

**Family size.** 7 Python files, 543 LOC.
`find src/etl/gowalla -name '*.py' -not -path '*/__pycache__/*' | wc -l` → 7;
`… | xargs cat | wc -l` → 543.

**Three stages** (`src/etl/gowalla/main.py` docstring + stage files):

1. **Stage 1 — `stage_1.py` (179 LOC): categorise.** Loads raw Gowalla
   check-ins; drops exact `(userid, placeid, datetime)` duplicates; builds a
   hierarchical category map from `gowalla_category_structure.json` +
   `callback_categories.json` + `extra_categories.json` (super → sub →
   sub-sub); merges check-ins with two POI spot tables
   (`gowalla_spots_subset1.csv`, `subset2.csv`) on `placeid`; maps each POI's
   leaf category up to a super-category; drops rows with unmapped categories.
   Output: `data/temp/gowalla/stage1_categorised.parquet`. **[code]**
2. **Stage 2 — `stage_2.py` (103 LOC): localise (optional).** Spatial-joins
   check-in points against timezone polygons (`timezone-boundary-builder`
   combined-with-oceans shapefile) to attach `local_datetime`. Skippable
   (`skip_localise=True`); the wrapper defaults to skipping it. Output:
   `stage2_localised.parquet`. **[code]**
3. **Stage 3 — `stage_3.py` (103 LOC): split per U.S. state.** Builds a
   GeoDataFrame of check-in points, spatial-joins against the U.S. Census
   TIGER 2022 state polygons (`tl_2022_us_state.shp`), attaches `state_name`,
   and writes one file per state under `data/checkins/`. **[code]**

**Inputs → outputs (from `src/configs/paths.py` + `main.py` docstring):**

| Direction | Artefact |
|---|---|
| Raw in | `gowalla_checkins.parquet`, `gowalla_spots_subset1.csv`, `subset2.csv`, 3 category JSONs |
| Geo in | `tl_2022_us_state.shp` (Census TIGER 2022); timezone shapefile (optional) |
| Intermediate | `stage1_categorised.parquet`, `stage2_localised.parquet`, `stage3_states.parquet` |
| Final | per-state files under `data/checkins/<State>` (symlink → external `checkins_by_state/`) |

**Number of U.S. states split — 56 US-level partition files on disk.** **[disk-artifact]**
`cd /Users/vitor/Desktop/mestrado/data/checkins_by_state && find . -maxdepth 1 -type f -name '*.parquet' | wc -l` → 58 total regular files; two of them (`Nyc.parquet`, `Istanbul.parquet`) belong to other dataset families sharing the directory, leaving **56 US-level files = 50 states + District of Columbia + 5 territories** (American Samoa, Commonwealth of the Northern Mariana Islands, Guam, Puerto Rico, United States Virgin Islands). All 50 states are present (verified by set difference). A further 9 entries are symlinks (category-variant aliases), excluded from the count.

**Evidence the pipeline actually ran at scale.** `label_categories.log` (repo
root, timestamped 2026-07-23) records a real run: **36,001,959** raw
check-ins loaded → 43,599 duplicates removed → super-category map of **398**
entries → **35,620,879** categorised check-ins retained; Stage-3 spatial join
matched **51.22%** of check-ins to U.S. states. **[disk-artifact / log]**
(These are log values from one run, not dataset statistics for the paper; the
paper's per-dataset counts are governed separately by the frame's number
protocol.)

**Honest code-vs-artifact caveat (report, do not smooth over).** Stage 3 as
currently written emits **per-state CSV** (`state_df.to_csv(...)`); the
per-state `.to_parquet(...)` line is **commented out** (stage_3.py line 98).
The 56 `.parquet` files on disk therefore evidence the **partition
cardinality** (56-way U.S. split) but were not produced by the current
stage_3 code path exactly as written — likely by an earlier version or a
separate segregation step. `src/configs/paths.py` defines both a `checkins`
(CSV) and a `checkins_parquet` output directory, consistent with a CSV→parquet
history. This is a factual gap between the code-as-written and the on-disk
parquet artefacts; treat "56-way U.S.-state split" as the defensible claim,
not "stage_3.py writes 56 parquet files."

---

## 2. Tooling inventory (modules that EXIST, with the doc that describes each)

Format: **[code]** path — verified against **[doc]** where a context doc exists.

### 2.1 ETL — 3 dataset families **[code]** `src/etl/` (23 files, 2,315 LOC)

| Family | Files | LOC | Stages | Scope | Doc |
|---|---|---|---|---|---|
| gowalla | 7 | 543 | 3 | U.S. 56-way state split | DATASETS.md |
| massive_steps | 6 | 573 | 2 | 15 cities incl. Istanbul (main.py docstring) | DATASETS.md |
| foursquare | 6 | 349 | 2 | 2 cities: nyc, tokyo (TIST2015) | DATASETS.md |

`massive_steps/main.py` docstring enumerates 15 supported city slugs (New
York, Tokyo, Sao Paulo, Melbourne, Sydney, Beijing, Shanghai, Moscow,
Istanbul, Jakarta, Bandung, Tangerang, Palembang, Petaling Jaya, Kuwait City).
`foursquare/main.py` configures `nyc` + `tokyo`. Datasets with on-disk
evidence used by the papers: the 56 U.S. Gowalla partitions + `Istanbul.parquet`
(Massive-STEPS) + `Nyc.parquet`.

### 2.2 Embedding engines — 8 with code **[code]** `research/embeddings/` (13,271 LOC)

`find research/embeddings -name '*.py' -not -path '*/__pycache__/*' | xargs cat | wc -l` → 13,271. All 8 are documented in `EMBEDDINGS.md` **[doc]** and match code:

| Engine | Files | LOC | Level | Pipeline wrapper |
|---|---|---|---|---|
| check2hgi | 10 | 5,240 | check-in | yes |
| hgi | 10 | 2,201 | POI | yes |
| space2vec | 6 | 1,939 | POI | yes |
| sphere2vec | 5 | 1,205 | POI | yes |
| hmrm | 3 | 981 | POI | **no** |
| time2vec | 6 | 706 | check-in | yes |
| poi2hgi | 3 | 513 | POI | yes |
| dgi | 6 | 486 | POI | yes |

7 of 8 have a runnable wrapper under `pipelines/embedding/`; HMRM has none.
(Note: these live in `research/`, a sibling of `src/`, so they are **not** part
of the 192-module / 28,644-LOC `src/` count in §3.)

### 2.3 MTL loss / gradient balancers — 21 with code **[code]** `src/losses/` (2,435 LOC)

`src/losses/registry.py` imports and registers **21 canonical** methods + **3
aliases**. Each has a real implementation file (`loss.py`), verified:
`equal_weight, static_weight, scheduled_static, uncertainty_weighting, uw_so,
random_weight, dwa, famo, pcgrad, gradnorm, nash_mtl, cagrad, aligned_mtl,
db_mtl, fairgrad, bayesagg_mtl, go4align, excess_mtl, stch, naive, focal`
(aliases: `rlw, bayesagg, excessmtl`). LOC per method ranges 33 (equal_weight)
to 347 (nash_mtl).

### 2.4 MTL backbone architectures — 13 with code **[code]** `src/models/mtl/`

Every subdir has a `model.py`: `mtlnet` (564 LOC), `mtlnet_cgc, mtlnet_mmoe,
mtlnet_dselectk, mtlnet_ple` (the documented five), plus a cross-attention
family and cross-stitch: `mtlnet_crossattn, _crossattn_dualtower,
_crossattn_dualtower_catpriv, _crossattn_dualtower_swiglu, _crossattn_mult,
_crossattn_swiglu, _crossattn_xstitch, mtlnet_crossstitch`.

### 2.5 Task heads / single-task models — model registry: 43 registered **[code]**

`grep -rn '^@register_model(' src/models --include='*.py' | wc -l` → 43 (the
`my_model` in `registry.py` is a docstring example, not counted). Breakdown:
9 category heads (`src/models/category/`), 21 next-task heads
(`src/models/next/`, incl. GRU/LSTM/Mamba/TCN/transformer/STAN variants), 13
MTL backbones (§2.4). `src/models/` totals 68 files / 6,931 LOC.

### 2.6 Cross-validation + evaluation protocol **[code]** + **[doc]**

- **Folds:** `src/data/folds.py` (1,633 LOC), 11 references to
  `StratifiedGroupKFold`; user-disjoint splits, MTL fold pairing on a shared
  user partition, leak-free per-fold region-transition prior. Matches
  `DATA_SPLITS.md` **[doc]**.
- **Metrics:** `src/tracking/metrics.py` implements macro-F1
  (`compute_classification_metrics`), top-k accuracy (`_top_k_accuracy`, incl.
  Acc@10), MRR (`_mean_reciprocal_rank`), nDCG (`_ndcg_at_k`). Matches
  `METRICS.md` **[doc]**.
- **Significance:** paired Wilcoxon across `scripts/analysis/*.py`; TOST
  (equivalence) in `scripts/finalize_phase3.py`,
  `scripts/analysis/substrate_paired_test.py`. Default seed 42
  (`src/configs/experiment.py`); multi-seed pool {0,1,7,100} referenced in
  `scripts/mtl_improvement/*.py`. Matches `METRICS.md`/`DATA_SPLITS.md` **[doc]**.

### 2.7 Supporting subsystems **[code]**
`src/data/inputs/` (window/fusion/next-region builders), `src/training/`
(15 files, 4,735 LOC; runners for STL, MTL-CV, MTL-eval), `src/tracking/`
(16 files, 3,062 LOC; metrics + parameter logging), `src/tasks/` (TaskSet
presets: legacy category+next; check2hgi next+region), `src/ablation/`
(1,850 LOC), `src/configs/` (1,706 LOC).

---

## 3. Verifiable scale numbers (each with its command)

| Metric | Value | Command / path |
|---|---:|---|
| `src/` Python modules | **192** | `find src -name '*.py' -not -path '*/__pycache__/*' | wc -l` |
| `src/` total LOC | **28,644** | `find src -name '*.py' … | xargs wc -l | tail -1` |
| Embedding engine LOC (`research/embeddings/`) | **13,271** | `find research/embeddings -name '*.py' … | xargs cat | wc -l` |
| `scripts/` Python files | **264** | `find scripts -name '*.py' | wc -l` |
| `scripts/` LOC | **48,981** | `find scripts -name '*.py' … | xargs cat | wc -l` |
| Test modules | **114** | `find tests -name '*.py' -not -path '*/__pycache__/*' | wc -l` |
| Test LOC | **22,998** | `find tests -name '*.py' … | xargs cat | wc -l` |
| MTL balancers with code | **21** (+3 aliases) | `src/losses/registry.py` + 21 `loss.py` files |
| MTL backbones with code | **13** | `find src/models/mtl -maxdepth 1 -type d` (each has `model.py`) |
| Embedding engines with code | **8** | `research/embeddings/` subdirs |
| Registered models total | **43** | `grep -rn '^@register_model(' src/models | wc -l` |
| ETL dataset families | **3** | `src/etl/{gowalla,massive_steps,foursquare}` |
| U.S. state partition files | **56** | `find …/checkins_by_state -type f -name '*.parquet'` = 58 − 2 non-US |
| Git commits (HEAD) | **1,692** | `git rev-list --count HEAD` |

`src/` LOC by subdir: models 6,931 · training 4,735 · data 4,325 · tracking
3,062 · losses 2,435 · etl 2,315 · ablation 1,850 · configs 1,706 · utils
995 · tasks 289.

---

## 4. Doc-vs-code gaps (fail-closed reporting)

1. **Optimizer count.** `MTL_OPTIMIZERS.md` says "**20** canonical + 3
   aliases." The registry has **21** canonical + 3 aliases. The undocumented
   extra is **`scheduled_static`** (`src/losses/scheduled_static/loss.py`,
   119 LOC). *Direction: code exceeds doc.*
2. **Architecture count.** `MTL_ARCHITECTURES.md` documents **5** backbones;
   the code has **13** (the 8 extra are the cross-attention family +
   cross-stitch, which the doc does not describe). *Direction: code exceeds
   doc.*
3. **Gowalla Stage-3 output format.** Doc/docstring imply per-state files
   feed downstream embeddings; the current `stage_3.py` writes **CSV** (the
   parquet line is commented out), yet the consumed artefacts on disk are
   **parquet**. Gap between code-as-written and on-disk artefacts (see §1
   caveat). *Direction: on-disk artefact not reproduced by current code path
   as written.*
4. **Embedding location.** `EMBEDDINGS.md` gives `research/embeddings/<engine>/`
   directories; confirmed present. These are **outside `src/`** — do not fold
   their 13,271 LOC into the `src/` total.
5. **HMRM.** Documented (107-dim) and has code (981 LOC) but no
   `pipelines/embedding/` wrapper and is flagged incompatible with the default
   64-dim config; treat as implemented-but-not-wired.

No case was found where a doc claims a module that has **no** code. All
gaps are in the direction of code exceeding or diverging from documentation,
not documentation overclaiming beyond code — **except** the Stage-3
CSV/parquet artefact gap in §1/§3.3.

---

## 5. Honest assessment

**Is this a substantial software/infrastructure contribution?** Yes, on the
evidence. The repository is a purpose-built, registry-driven research platform
for MTL POI prediction, not a thin set of experiment scripts: a 192-module /
28,644-LOC `src/` core, a 13,271-LOC embedding-engine suite, and a
22,998-LOC / 114-module test layer, developed over 1,692 commits. It supplies
plug-replaceable implementations across every axis the dissertation studies —
3 ETL dataset families, 8 embedding engines, 21 MTL loss/gradient balancers,
13 MTL backbones, 43 registered models — behind name-keyed registries
(`losses/registry.py`, `models/registry.py`) with a documented, leak-controlled
cross-validation and significance protocol (user-disjoint StratifiedGroupKFold,
per-fold transition priors, paired Wilcoxon + TOST). The one material accuracy
caveat is the Gowalla Stage-3 CSV-vs-parquet artefact gap (§1); the ETL's
**56-way U.S.-state spatial partition** and its logged 35.6M-check-in run are
otherwise directly evidenced.

**Strongest defensible one-paragraph characterization (no undefendable adjectives):**

> During this research we built and maintained a registry-driven experimental
> platform for multi-task point-of-interest prediction, comprising a
> 192-module, 28,644-line `src/` core, a 13,271-line embedding-engine suite,
> and a 114-module, 22,998-line test layer, developed across 1,692 commits.
> The platform provides interchangeable, name-keyed implementations of 3 ETL
> dataset families (Gowalla, Massive-STEPS, Foursquare), 8 POI/check-in
> embedding engines (including DGI, HGI, and the check-in-level Check2HGI),
> 21 multi-task loss and gradient-balancing methods, and 13 multi-task
> backbone architectures spanning the hard-to-soft parameter-sharing spectrum,
> exposed through 43 registered models. A refined Gowalla ETL geospatially
> partitions the SNAP check-in dump into 56 U.S. state-level datasets (50
> states, the District of Columbia, and 5 territories) via a three-stage,
> resumable pipeline (category mapping over a 398-entry hierarchy, optional
> timezone localisation, and Census-TIGER state spatial join), and a
> user-disjoint cross-validation and significance protocol (StratifiedGroupKFold
> with per-fold leak-free transition priors, macro-F1 / Acc@10 / MRR, paired
> Wilcoxon and TOST) standardises every single-task-versus-multi-task
> comparison in the dissertation.

*(Every count in this paragraph is traceable to §1–§3 and to
`_history/_archive/handoffs/handoff_tooling.json`. Adjectives are limited to ones the numbers support;
no performance or novelty claim is made here — those belong to the results
chapters under the frame's number protocol.)*

---

*Generated by a read-only repo survey. Companion machine-readable counts:
`articles/dissertacao/_archive/handoffs/handoff_tooling.json`.*
