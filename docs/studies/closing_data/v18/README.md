# v18 — the v17 recipe on a leak-free substrate

> **Status: COMPLETE** — board at 72/72 (6 states × 4 seeds × 3 families, n=20), finished 2026-08-10.
> Started 2026-08-06 from commit `f281a709`. Open items are in [`GAPS.md`](GAPS.md); charter
> compliance in [`CHARTER_COMPLIANCE.md`](CHARTER_COMPLIANCE.md).
> Live state: [`status.json`](status.json) (machine-readable) · [`PROGRESS.md`](PROGRESS.md) (human).
> Charter: [`V18_AGENT_PROMPT.md`](V18_AGENT_PROMPT.md).

**v18 = the frozen v17 recipe, with the consecutive-visit leak fixed, plus elapsed-time node
features.** Not an architecture change. The check-in graph is **forward-only** in training and at
readout, and node features carry 4 elapsed-time columns (`in_channels = 15`).

> ⚠ **[`PRECISION_CAVEAT.md`](PRECISION_CAVEAT.md) — READ BEFORE CITING ANY CATEGORY NUMBER.**
> A shell `export` leak meant the dedicated-category cells ran fp16 or fp32 depending on resume
> state, and the `precision` field in the cat sidecars is **false for 8 of 10 cells**. Two specific
> results are void (florida cross-seed cat; texas s0 Δcat). Region and joint are unaffected.

## Read in this order

1. [`METHODOLOGY.md`](METHODOLOGY.md) — what v18 is, why forward-only, why elapsed time, what was
   excluded and on what evidence. **Start here.**
2. [`V18_RESULTS.md`](V18_RESULTS.md) — the tables. Per state: dedicated cat, dedicated reg, joint
   (diag-best **and** joint-best), Δ vs the v17 published values, current `n` stated in every table.
3. [`LOSS_WEIGHT_PROBE.md`](LOSS_WEIGHT_PROBE.md) — **mechanism result.** Is the 0.75/0.25 split a
   leak artifact, and are the two heads competing? Answer to both: no. The shared-trunk gradients are
   orthogonal (cos ≈ +0.001 over 750 measurements), rebalancing to 0.50/0.50 buys +0.29 pp (p = 0.42),
   and PCGrad buys +0.20 pp (p = 0.26) because it has nothing to project. The category collapse is
   **not** a multi-task optimization problem.
4. [`READOUT_EQUIVALENCE.md`](READOUT_EQUIVALENCE.md) — why the v18 engine is materialized from the
   one-shot full-graph export rather than the per-window readout, the full-coverage evidence, and
   the guard that stops the shortcut being applied to a bidirectional arm. **Read before touching
   Phase 0.**
5. [`AUDIT.md`](AUDIT.md) — the §6 self-checks with their measured values, and anything that failed.
6. [`PROVENANCE.md`](PROVENANCE.md) — every rundir: state, seed, PID, path, recipe, commit SHA.
7. [`data/v18_results.json`](data/v18_results.json) + [`score_all.py`](score_all.py) — the
   machine-readable record and the reproducer that regenerates it from the rundirs. **Every number
   in every markdown table here is traceable to that JSON.**
8. [`MAJORITY_CLASS_FLOOR_PER_STATE.md`](MAJORITY_CLASS_FLOOR_PER_STATE.md) — not a v18 run: a
   closed-form derivation, from the published Table 8 majority share, of which dataset gives each
   end of the dissertation's "5.7 to 7.3 macro-F1" majority-class-floor range (Florida min / Alabama
   max — Alabama was never named in the delivered text).

## What to expect (so a real result is not mistaken for a bug)

- **Category falls a long way.** At Alabama the honest forward-only arm scores ~28.3 where v17
  reported ~56.9. The v17 number was inflated by the leak; the drop is the point of the exercise.
  A v18 category number landing **within 5 pp of its v17 value** means the forward-only path is
  broken — `run_wave.sh` raises a `[VERIFY]` flag automatically and it is investigated, not reported.
- **Region barely moves.** The region tower consumes region embeddings indexed by historical places,
  which are per-region dataset constants, so the leak cannot reach it. A move **> 2 pp** is likewise
  flagged and investigated.

## Scope guardrails

- **Do not** add place identity or region identity to the node features. Every variant was measured
  at Alabama and every one hurt (−0.41 to −1.86); only elapsed time gained (+0.83). See
  METHODOLOGY §3 for the mechanism and the one recorded unexplained ordering.
- **Do not** re-sweep encoder width or depth. 32/64/128 and 1/2/3/4 are settled at 64 and 2.
- **Do not** change the output width 64 — it is a hard constant in three places.
- **Do not** write into `output/check2hgi_dk_ovl/`, `output/check2hgi_design_k_resln_mae_l0_1/`, or
  any other existing engine directory. Those are the frozen v17 artifacts behind the published
  table. `build_study_repr.py` refuses to; do not work around it.
- **Do not** report a v18 number as beating or matching anything without the test §10 requires:
  paired superiority for "outperforms", TOST non-inferiority for "matches".

## Layout

```
run_phase0_fast.sh     Phase 0 as run: build + materialize from the one-shot export  <- USE THIS
run_phase0_build.sh    Phase 0 via the per-window readout. Superseded for forward-only arms
                       (identical output, ~17 h slower at FL/CA/TX); kept as the reference path
                       and REQUIRED for any bidirectional arm. See READOUT_EQUIVALENCE.md
run_wave.sh <SEED>     one wave: 6 states x 3 families at one seed (resumable, idempotent)
run_lossweight_probe.sh  the 0.75 vs 0.50 vs pcgrad probe at alabama -> LOSS_WEIGHT_PROBE.md
run_florida_cw050.sh     the same 0.50/0.50 arm at florida (stronger category signal)
verify_engines.py      the SS6 self-checks -> AUDIT.md + data/v18_audit.json
status_update.py       rewrites status.json + PROGRESS.md from the per-cell sidecars
score_all.py           the reproducer: regenerates data/v18_results.json from the rundirs
smoke_alabama.sh       1-fold/2-epoch validation of the full training path
logs/                  driver + per-cell logs (gitignored)
```

Per-cell score sidecars live at `docs/results/closing_data/v18/<state>_s<seed>_<family>.json` and
are the resumability source of truth: a cell is done iff its sidecar exists.

## Engine

`EmbeddingEngine.CHECK2HGI_V18 = "check2hgi_v18"`. A new engine must be registered in **FOUR**
allowlists, not the two the charter warns about — miss one and the failure is late and confusing:

| # | where | symptom if missed |
|---|---|---|
| 1 | `EmbeddingEngine` enum — `src/configs/paths.py` | nothing resolves |
| 2 | `MTL_CHECK2HGI_ALLOWED_ENGINES` — `src/configs/paths.py` | joint runs rejected |
| 3 | `IoPaths.get_next_region` `supported` — `src/configs/paths.py` | trains fine on category, **dies at the region tower** |
| 4 | `--engine-override` `choices` — `scripts/p1_region_head_ablation.py` | dedicated-region family dies at argparse, `rc=2`, 3 s in |

(#4 cost a wave-1 cell before it was found; fixed in `82bca519` with a comment at the site.)

One engine per state at `output/check2hgi_v18/<state>/`, shared by all four seeds; the representation
does not depend on the downstream seed.
