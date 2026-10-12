# JOINT_BEST_SCORING — the two epoch-selection conventions (and how not to mix them up)

> **Why this doc exists (2026-07-09).** The MobiWac Table-3 MTL cells are **per-task diagnostic-best**
> (`a40_score_matched.py` / `h100_score_matched.py`), but training saves a **single joint checkpoint** per fold —
> and the author believed Table 3 reported that checkpoint. Nobody had ever scored it. The submission stays
> diag-best (disclosed in the paper §6.2); joint-best is now producible programmatically (the J1 lane, camera-ready /
> response-letter). This doc defines both conventions precisely, gives the re-scoring procedure, and specifies the
> `standard_scores.json` contract every future MTL run emits so no agent ever re-derives scoring ad hoc again.
> Single source of truth for the selection logic: [`src/tracking/scoring.py`](../../../src/tracking/scoring.py).

## 1 · The two conventions, precisely

Both read the same per-epoch validation series (`metrics/fold{N}_next_{category,region}_val.csv`; values are
fractions, `epoch` column is 1-based).

| | **diag-best** (per-task diagnostic-best) | **joint-best** (single checkpoint) |
|---|---|---|
| cat | macro-F1 (`f1` col) at the **cat-F1-best** epoch | macro-F1 at **e\*** |
| reg | `top10_acc_indist · (1 − ood_fraction)` at the **indist-best** epoch | same formula at **e\*** |
| epochs/fold | **two different epochs** (e.g. AL s0: cat [17,17,16,17,17] vs reg [27,25,28,22,37]) | one epoch e\* for both heads |
| e\* definition | — | `argmax_e selector(e)` over epochs with **0-based index ≥ min_best_epoch**; ties → earliest (training's strict `>` rule) |
| selector | — | `geom_simple` (default) = `sqrt(cat_f1(e) · reg_top10_acc_indist(e))`; training falls back to reg F1 if no `top10_acc_indist` |
| what it measures | per-head headroom of ONE training run | what the ONE saved deployable checkpoint actually delivers |
| scorer | `scripts/closing_data/a40_score_matched.py` | `scripts/closing_data/score_joint_best.py` |
| paper status | **Table 3 (submission)** — disclosed §6.2 | **J1 lane** — camera-ready / response-letter |

The joint-best definition is exactly the training-time joint-checkpoint gate
(`mtl_cv._compute_joint_selectors` + `joint_eligible = epoch_idx >= joint_min_epoch`), so a post-hoc joint-best
re-score recovers the epoch of the checkpoint that was actually saved — no retraining, no GPU.

**min_best_epoch:** the v16/v17 canon bundles (`src/configs/canon.py` `_V16`) and the board drivers (`--canon
none` + explicit v17 recipe, e.g. `run_catx_v17_n20.sh`) do **not** pin `--min-best-epoch`, so the whole v17 board
trained with the `ExperimentConfig` default **0** — the scorer's default matches. Only the B9-recipe versions
(v11/v12/v15, `_CROSSATTN_B9`) pinned `--min-best-epoch 5`; pass `--min-best-epoch 5` when scoring those runs.

## 2 · How the confusion happened

Training gates ONE joint checkpoint per fold on the `geom_simple` selector (C21). The matched scorers, written for
STL-vs-MTL ceiling comparisons, score per-task diagnostic-best from the per-epoch CSVs. When the board cells were
filled, the diag-best numbers became "the MTL numbers" — and since the joint checkpoint was never scored, nothing
ever surfaced that Table 3's two heads come from *different epochs*. The author believed Table 3 = joint checkpoint;
it is diag-best. Decision (2026-07-09): submission keeps diag-best **with explicit disclosure in §6.2**; joint-best
becomes the standard, programmatically producible second lane (J1).

## 3 · Producing joint-best for the existing board (J1 — CPU-only, minutes)

Run the scorer on each board rundir, on whichever machine holds it (all board rundirs live on the **A40**;
`results/check2hgi_dk_ovl/{state}/mtlnet_*`):

```bash
.venv/bin/python scripts/closing_data/score_joint_best.py <rundir> --seed <S> --tag <cell_tag>
# defaults already correct for the v17 board: --min-best-epoch 0 --selector geom_simple
# writes <rundir>/joint_best_score.json (committable, C28) + a 4dp printout of BOTH conventions
```

Rundir families to cover (see [`v17_completion/README.md`](v17_completion/README.md) task **J1**):

- **perhead_lr_n20** — AL / AZ / FL, n=20 {0,1,7,100}×5f (`perhead_lr_n20.md`; driver `run_n20_perhead.sh`,
  per-PID rundirs — see `train_perf_multifold/BATCH_SIZE_SWEEP.md` for the rundir→seed mapping caveat).
- **catx_v17_seed0_5f** — CA / TX seed-0 5f (`catx_v17_seed0_5f/RESULTS.md`) + the CA/TX n=20 rundirs (A1 done
  2026-07-11 on the A40 — `docs/results/closing_data/catx_v17_n20/`; the n=20 *joint-best* re-score is the still-pending CPU task T6).
- **h3_istanbul** — Istanbul dk_ovl+v17 n=20 (`v17_completion/h3_istanbul/RESULTS.md`, `step3_runs`).

Legacy rundirs (pre-fix) have no `standard_scores.json`; the scorer falls back to the CSVs automatically.
Diag-best parity vs `a40_score_matched.py` is verified (identical mean±sd and epochs on a real AL rundir).

## 4 · The `standard_scores.json` contract (all future runs)

Every MTL fold now self-reports BOTH conventions at fold end: `metrics/fold{N}_standard_scores.json` (named by
REAL fold id, fan-out safe; write-only; exception-proof; default-on; zero effect on metrics/checkpoints/selector).
Written by `HistoryStorage._save_fold_standard_scores` from the pure functions in `src/tracking/scoring.py` —
full schema in that module's docstring. Key fields per fold:

```
cat_diag_best  {epoch, f1}                       reg_diag_best {epoch, top10_indist, ood_fraction, top10_full}
joint_best     {epoch, selector, cat_f1, top10_indist, ood_fraction, top10_full}
selector_name · min_best_epoch · checkpoint_epoch (cross-check vs the actually-saved checkpoint) · warnings
```

Units are **fractions** (like the CSVs), epochs **1-based** (like the CSV `epoch` column). The scorer prefers these
artifacts when present (and matching selector + min-best-epoch) and prints **percent** (like a40).

## 5 · ⛔ DO-NOT-REPEAT (future agents)

- **Never report an MTL number without stating its epoch-selection convention** (diag-best vs joint-best, plus
  selector + min-best-epoch for joint). "cat X / reg Y" with no convention is under-specified and was the root
  cause here.
- **Prefer `standard_scores.json`** over re-deriving from CSVs; if you must re-derive, import
  `tracking/scoring.py` — do not re-implement argmax/gate/full-top10 logic (tie-breaking and the 0-based gate are
  easy to get subtly wrong).
- **Do not compare a diag-best cell against a joint-best cell** (or against a single-checkpoint baseline) without
  flagging the convention mismatch — diag-best is an upper bound on the deployable single checkpoint.
- **Check `min_best_epoch` per run family** before scoring: v17 board = 0; B9-recipe (v11/v12/v15) = 5.

## 6 · Results (J1 executed 2026-07-09) → `docs/studies/closing_data/joint_best/`

All 18 v17/`dk_ovl` MTL rundirs were joint-best-scored (AL/AZ/FL/Istanbul n=20, CA/TX seed-0 5f). **The served
single checkpoint reproduces the diag-best Table 3 within ≤ 0.06 pp (category) / ≤ 0.11 pp (region) on every
dataset (largest deviations 0.051 / 0.107, both at AZ); no verdict changes.** cat beats everywhere; reg beats at Istanbul/FL/TX/CA (Istanbul +0.28→+0.19, still
positive and 20/20 folds) and matches at AL/AZ (AL −0.31→−0.41, far inside the ±2 pp bound — the flagged AL tail
risk did not materialize). Validated by three parity gates (diag-best 18/18, joint-epoch 90/90, paper 6/6) + a
4-agent independent audit (from-scratch re-derivation bit-identical to 4 dp). Full corrected table, Δ-vs-ceiling
analysis, decision memo, provenance, and audit: **this folder** (`joint_best/`)
(`JOINT_BEST_RESULTS.md` is the table; `data/j1_results.json` + `score_all.py` reproduce it).
