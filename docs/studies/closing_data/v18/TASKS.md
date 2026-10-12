# v18 — task list

> Charter §7 deliverable. Written 2026-08-11, **after** the run finished, so it is a record of what
> the study actually did rather than a plan it was steered by. Everything in "Done" is verifiable
> from an artifact in this repository; the pointer is given so a reader can check rather than trust.
>
> Status of the study: **the data is complete (72/72 cells, n=20 in all three families across all
> six states)**. What remains is metadata hygiene and writing — nothing here requires re-training.

## Done

| # | task | evidence |
|---|---|---|
| 1 | Build the v18 substrate at all six states (forward-only graph, 4 elapsed-time node columns, `in_channels` 15) | `log.md` 2026-08-07; `READOUT_EQUIVALENCE.md` |
| 2 | Prove `prefix_forward_only` is an identity on a forward-only graph | `READOUT_EQUIVALENCE.md` — float32 epsilon over every window, 4 states |
| 3 | Retune the recipe on both arms so Δcat is not biased against MTL (103 arms) | `SWEEP_FINDINGS.md`; `log.md` 2026-08-08 |
| 4 | Replace class weighting with logit adjustment (τ=0.5) | `SWEEP_FINDINGS.md` §logit-adjust; dedicated +2.86, MTL +3.18, p ≤ 0.0014 |
| 5 | Freeze the recipe | `FINAL_SETTINGS.md` (`v18-approved-2026-08-09`) |
| 6 | Run 72 cells: 6 states × 4 seeds {0,1,7,100} × 3 families | `data/v18_results.json`; `status.json` 72/72 |
| 7 | Score every cell from its rundir rather than from a reported value | `score_all.py` — sidecars supply only the (state, seed, family) → rundir mapping |
| 8 | Fix the AMP precision leak and pin precision per command | `PRECISION_CAVEAT.md`; two results voided and re-run |
| 9 | Make the paired ceiling contrast symmetric (`stl_*_paired`) | `log.md` 2026-08-10; `score_all.py` |
| 10 | Remove the O(N·C) val-metric buffer that OOM-killed large-state reg cells | `INVESTIGATION_gpu_cpu_alternation.md`; `src/tracking/metrics.py` `StreamingClsMetrics` |
| 11 | Certify the tie-break exposure per run instead of assuming it | `ambiguous_rows` per fold; `MTL_AMBIGUITY_STRICT` |
| 12 | Establish cross-hardware agreement empirically | `GAPS.md` addendum §A3 — same fold A40 vs H100, Acc@10 identical to 4 dp |
| 13 | Close `GAP E.2` — `status.json` counted joint cells only | `status_update.py`; verified by hiding a cell and watching n fall 20 → 15 |
| 14 | Retire the rented-lane study folder; promote the machinery to `pipelines/modal/` | commit `78d85699` |
| 15 | Audit every declared `lane_host` against the GPU memory its heartbeat recorded | §A6 below — 16 labelled cells, **zero divergences** |

## Open — metadata, no re-training

| # | task | size | why it matters |
|---|---|---|---|
| 16 | `GAP A` — 30 cells carry `commit_sha: "unknown"` | see note | charter §7 wants code traceability. **Now known to be unrecoverable**: the Volume's `/repo` was uploaded as a tar of the worktree with no `.git` (verified 2026-08-11 — none of the three accounts' volumes contains `/repo/.git`). `commit_sha_note` records the reason. **Recommend closing as "admitted, with cause" rather than back-filling.** |
| 17 | `GAP B` — 10 cells without `recipe_version` | trivial | completes the set; the value is known (`v18-approved-2026-08-09`) |
| 18 | `GAP C` — ~40 cells without `lane_host` | metadata | they are presumed local; presumption is not provenance. **Disclosure, not homogenisation** — the mixing is universal (seeds 0/1 local, 7/100 rented, every state and family), and §A3 shows the effect is at or below the reporting quantum |
| 19 | `GAP D` — 20 reg cells without a scoring-path field | metadata | lets a reader separate the legacy topk population from the rank-derived one without archaeology |
| 20 | `GAP E.1` — the `n` column cannot represent a row whose halves disagree | small | currently correct only because both halves are 20 |

## Open — writing

| # | task |
|---|---|
| 21 | State the hardware design in `METHODOLOGY.md`: seeds 0/1 local A40, seeds 7/100 rented, with §A3's agreement evidence |
| 22 | Decide and record the open scientific calls in `GAPS.md` §7 (author's, not an agent's) |

## Not tasks

Re-running cells to homogenise hardware. The controlled comparisons put the cross-machine effect at
or below the last reported digit, and the mixing is study-wide rather than a stray cell — so this
would cost the whole rented wave and buy nothing measurable.
