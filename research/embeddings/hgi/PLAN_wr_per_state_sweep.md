# Plan — per-state `w_r` sweep for Arizona, Texas, California, Florida

**Status:** pending
**Owner:** unassigned
**Prereqs:** PR #13 (paper alignment + `CROSS_REGION_WEIGHT_PER_STATE`) merged
**Context file:** `research/embeddings/hgi/README.md` §5, `plans/hgi_paper_alignment.md`

---

## Goal

Empirically validate or correct the density-interpolated `w_r` defaults for the
four states that were NOT swept during PR #13. Only **Alabama** was empirically
swept there — the Arizona / Texas / California / Florida values are
extrapolations from a single anchor point (Alabama) plus the paper's anchors
(Xiamen / Shenzhen). This plan converts those guesses into measurements.

## Non-goals

- Not sweeping any other HGI hyperparameter (`alpha`, `lr`, `attention_head`,
  etc.).
- Not changing the MTLnet architecture, loss, or optimizer.
- Not sweeping `w_r` outside the `{0.4, 1.0}` interval.
- Not running full 5×50 — that can be a follow-up only if a state's sweep is
  inconclusive at the fast protocol.

## Hypothesis under test

> The optimum `w_r` scales inversely with POI density. Sparser states want a
> milder cross-region penalty; denser states want a stronger penalty. The
> paper's 0.4 is tuned for Chinese cities (26-150 POI/km²) and is a local
> pessimum on all US states.

If true, the sweep should show:
- Arizona / Texas → Cat F1 peaks at `w_r ∈ [0.7, 1.0]` (like Alabama).
- California / Florida → Cat F1 peaks at `w_r ∈ [0.6, 0.7]` (between Alabama
  and the paper).
- All four states clearly prefer `w_r > 0.4`.

If the hypothesis fails (e.g. Florida peaks at 0.4), the density interpolation
was wrong and we fall back to per-state sweeping with no global rule.

---

## Experimental protocol

### Sweep grid

Three-point bracket per state:

| `w_r` | Purpose                                  |
|-------|------------------------------------------|
| 0.4   | Paper lower bound (known pessimum on AL) |
| 0.7   | Alabama-swept optimum / interpolated default |
| 1.0   | Upper bound (no cross-region penalty)    |

Total: **4 states × 3 points = 12 sweep runs**, plus **2 calibration runs on
Alabama** (details below) = **14 total**.

### Reduced MTLnet training

Per sweep point: regenerate HGI embeddings (2000 HGI epochs, 100 POI2Vec
epochs — unchanged) and run MTLnet at **2 folds × 15 epochs** instead of the
full 5 folds × 50 epochs.

Rationale: the Alabama sweep in PR #13 showed Cat F1 stabilizes by ~epoch 12-15
and the fold-to-fold variance is smaller than the w_r-induced gap. `2f15e`
should therefore preserve the ranking even if it slightly compresses absolute
numbers. We explicitly **validate this** with the calibration step before
trusting the downstream state sweeps.

HGI hyperparameters are NOT reduced — the paper's lr=0.006 + warmup=40 + 2000
epochs recipe must stay, otherwise we're comparing broken embeddings.

### Calibration step (run FIRST, blocks the rest)

Before touching the four unknown states, run **Alabama at the reduced
protocol** for two `w_r` points whose ranking we already know from the full
sweep:

| Run | `w_r` | Protocol | Known full-sweep result | Pass criterion |
|-----|-------|----------|------------------------|----------------|
| AL-cal-0.4 | 0.4 | 2f15e | Cat F1 ≈ 0.739 at 5f50e | Cat F1 at least 2σ below AL-cal-0.7 |
| AL-cal-0.7 | 0.7 | 2f15e | Cat F1 ≈ 0.819 at 5f50e | Cat F1 at least 2σ above AL-cal-0.4 |

If the 2f15e protocol **cannot** separate these two points (they end up within
1σ), the reduced protocol is too noisy and we must fall back to 3f25e or
abandon the fast sweep. **This is a Go/No-Go gate.**

Wall-clock cost: 2 × 13 min ≈ 26 min.

### State sweeps (blocked by calibration)

After calibration passes, sweep each state across `{0.4, 0.7, 1.0}` at 2f15e.

| Pair | States | Rationale |
|---|---|---|
| Pair 1 | Arizona + Texas | Both sparse (like Alabama). If our density heuristic is right, we expect `w_r ≥ 0.7` to win here. |
| Pair 2 | California + Florida | Both denser. Stress test for the heuristic — Florida is the densest (~0.54 POI/km²) and the most likely place the heuristic breaks. |

### Parallelization

**Axis:** across states, NOT across `w_r` values within a state.

- Different states write to `output/hgi/{state}/…` → no file collision.
- Within a state, `w_r=0.4` → `w_r=0.7` → `w_r=1.0` must run **sequentially**
  (shared `embeddings.parquet` path).
- Pair 1 and Pair 2 run **sequentially** (after pair 1 validates runtime).
- Inside each pair, the two states run **concurrently** as two independent
  Python subprocesses.

**Thread budget.** HGI's `_hgi_thread_context()` pins each run to
`HGI_NUM_THREADS=6` by default. Two concurrent runs would book 12 threads;
on a machine with ~8-10 perf cores that's contention. For parallel pair runs,
set `HGI_NUM_THREADS=4` in the environment so each pair uses 8 total. First
pair acts as the empirical benchmark — if it's not ~1.7× faster than
sequential, drop to 3 threads per process for pair 2.

### Runtime estimate

Assuming `HGI_NUM_THREADS=4` and the pair runs at 1.5× speedup over sequential:

| Phase | Runs | Wall clock |
|---|---|---|
| Calibration (Alabama 2f15e × 2) | 2 | ~26 min |
| Pair 1: Arizona + Texas concurrently (each 3 sweep points) | 6 | ~52 min |
| Pair 2: California + Florida concurrently (each 3 sweep points) | 6 | ~52 min |
| **Total** | **14** | **~130 min (~2h10)** |

Compared to naively running everything sequentially at the original 5f50e
protocol: 12 × 24 min ≈ 290 min (~5h). Savings: ~3 hours.

If pair-parallelism turns out to be contention-bound and delivers <1.3×, fall
back to fully sequential at 2f15e: 14 × 13 min ≈ 182 min (~3h). Still a big
win vs 5h.

---

## Success criteria per state

For each state, the sweep produces a table like:

```
w_r=0.4: Cat F1 a ± σa, Next F1 b ± σb
w_r=0.7: Cat F1 c ± σc, Next F1 d ± σd
w_r=1.0: Cat F1 e ± σe, Next F1 f ± σf
```

**Decision rule** (applied in order):

1. **Clear winner on Cat F1** (best minus second-best ≥ 1σ of the second-best):
   pin the state to that `w_r`.
2. **All points within 1σ** (inconclusive): keep the density-interpolated
   default and log "inconclusive at 2f15e, requires full 5f50e sweep" in the
   follow-up note.
3. **Next F1 contradicts Cat F1**: default to maximizing Cat F1 (the paper's
   primary metric). Log the Next F1 divergence so future work can look at it.

---

## Deliverables

1. **Updated per-state defaults** in `pipelines/embedding/hgi.pipe.py`
   (`CROSS_REGION_WEIGHT_PER_STATE`).
2. **Sweep results table** appended to `research/embeddings/hgi/README.md` §5,
   one sub-table per state, documenting the swept points and the chosen value.
3. **Raw artifacts** saved under
   `results_save/{state}_wr0{4,7,10}_2f15e_<ts>/` for each point:
   - `embeddings.parquet`
   - `region_embeddings.parquet`
   - `input/` dir
   - `mtl_2f15e/` (MTLnet results dir)
4. **Follow-up tasks** for any state that comes back inconclusive:
   - Full 5f50e sweep at the same grid.
   - Or a finer grid `{0.5, 0.6, 0.7, 0.8, 0.9}` if the peak isn't where we
     expect.

---

## Risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| 2f15e is too noisy to separate adjacent `w_r` points | Medium | Calibration step catches this up-front (Go/No-Go gate). |
| Parallel runs contend on CPU / memory and are <1.5× faster | Medium | First pair is the empirical benchmark; drop thread count or go sequential for pair 2 based on what we see. |
| Another worktree's pipeline overwrites `output/hgi/{state}/` mid-run (c.f. the incident during the Alabama full sweep) | Low but happened once | Snapshot each point's outputs to `results_save/…` immediately after the run, before the next point overwrites them. Scripted, not manual. |
| HGI training collapses at `w_r=1.0` (no cross-region penalty → degenerate graph) | Low | `w_r=1.0` is still a valid input — intra and cross edges have the same weight, but the log-distance factor `w_spatial` still differentiates them. If training does collapse, best-loss will be ~0 and Cat F1 ≈ random; we'll detect this and flag the state. |
| POI density is a bad proxy and the real driver is something else (e.g. region size distribution) | Medium | A failed hypothesis IS a result — document it in the README and switch to per-state sweeps as the recommended practice. |

---

## Out of scope / explicitly deferred

- **Georgia** is in `STATES` but has no POI-count reading yet. Defer its sweep
  until `data/checkins/Georgia.parquet` is confirmed or the state is removed
  from the pipeline.
- **`w_r > 1.0`** (amplify cross-region edges instead of penalise). The
  Alabama sweep didn't even flatten at 0.7, so `w_r > 1.0` is worth trying if
  `w_r = 1.0` keeps winning — but that's a separate investigation, not part of
  this plan.
- **Re-tuning the paper's `lr=0.006` or `warmup=40`** for sparse US datasets.
  If HGI training is unstable at high `w_r`, the instinct will be to blame
  the optimizer schedule — resist that and first investigate whether it's a
  graph-structure problem.

---

## When to revisit this plan

- Before running: if the machine available has fewer than 6 perf cores, drop
  the parallelization and do fully sequential 2f15e (still ~3h, still a win).
- After pair 1 results are in: decide whether pair 2 should use the same
  thread budget, a reduced one, or go fully sequential.
- If calibration fails: rewrite the protocol section to use 3f25e (~20 min
  per point, ~4h total) instead of 2f15e.
