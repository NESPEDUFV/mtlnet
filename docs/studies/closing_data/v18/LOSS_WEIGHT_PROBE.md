# Probe: is the 0.75/0.25 split a leak artifact, and are the heads competing?

> **Asked 2026-08-06 (user).** The joint loss is `0.75·L_cat + 0.25·L_reg`, tuned on the **leaked**
> check2hgi. If the leak is what made the category head productive, that split may no longer be
> right. And separately: are the two heads' losses actually competing?
>
> **Answer: no on both counts.** The heads' gradients are orthogonal, not competing, and neither
> rebalancing the split nor applying gradient surgery recovers anything. The category collapse is
> **not** a multi-task optimization problem.

## Setup

Alabama, seed 0, 5 folds, 50 epochs, v18 engine (forward-only + elapsed time), fp32, `--compile`,
`--tf32`, per-head cat-lr 1e-3 — the frozen v17 recipe in every respect except the loss line. All
three arms run `MTL_TRAIN_DIAGNOSTICS=1`, enabling `mtl_cv._compute_gradient_cosine`: once per epoch,
on batch 0, `cos(∇L_cat, ∇L_reg)` over the **shared trunk parameters**, plus each task's gradient
norm → `<rundir>/diagnostics/fold*_diagnostics.csv`. 250 measurements per arm (50 epochs × 5 folds).

## Results

| arm | loss | cat | reg | cos mean | % epochs cos<0 | ‖∇cat‖ | ‖∇reg‖ | wall |
|---|---|---|---|---:|---:|---:|---:|---:|
| **A** | `static_weight` 0.75/0.25 | 27.3836 ± 1.691 | 69.6831 ± 3.002 | +0.00115 | 50% | 0.1507 | 0.1220 | 1340 s |
| **B** | `static_weight` 0.50/0.50 | 27.6771 ± 1.725 | 69.6873 ± 2.996 | +0.00148 | 46% | 0.1324 | 0.1238 | 1340 s |
| **C** | `pcgrad` (surgery) | 27.5797 ± 1.633 | 69.6063 ± 3.015 | +0.00159 | 46% | 0.1358 | 0.1249 | 1244 s |

Paired per-fold against A (same seed, same folds, n=5):

| contrast | Δcat | p | Δreg | p |
|---|---:|---:|---:|---:|
| B − A (equal split) | **+0.294** | 0.42 | +0.004 | 0.95 |
| C − A (surgery) | **+0.196** | 0.26 | −0.077 | 0.57 |

## 1 · The heads are orthogonal, not competing

Across all three arms and 750 measurements the shared-trunk cosine sits at **+0.001**, sd ≈ 0.012,
and never exceeds **|0.067|** in either direction. Roughly half the epochs are marginally negative
and half marginally positive — symmetric noise around zero, which is the signature of *orthogonal*
task gradients, not competing ones.

**This reproduces the pre-leak finding.** `scripts/mtl_improvement/plot_grad_cosine.py` records
"cosine ≈ 0 → the two tasks' gradients are orthogonal → there is no conflict", measured on the
**leaked** substrate. Removing the leak left the gradient geometry unchanged. The leak was therefore
never creating, nor masking, a gradient conflict.

## 2 · Rebalancing the split does nothing

Moving to 0.50/0.50 buys **+0.29 pp** category (p = 0.42) — about a fifth of the fold-to-fold sd
(1.69), and driven almost entirely by a single fold (the five per-fold diffs are +1.53, −0.26, +0.36,
+0.10, −0.26). Region does not move at all (+0.004, p = 0.95).

The weight *is* doing its mechanical job: lowering the category weight drops its shared-trunk
gradient norm from 0.151 to 0.132, pulling the cat:reg norm ratio from 1.24 to 1.07. The optimization
responds; the metric does not. So the split is not where the ~8.4 pp of lost category advantage went.

## 3 · Gradient surgery does nothing, for the reason the cosine predicts

PCGrad projects a task's gradient onto the normal plane of the other **only when their cosine is
negative**. Here the negative excursions are ~0.01–0.03 in magnitude, so there is essentially nothing
to project — and indeed C lands on A (+0.196 cat, p = 0.26; −0.077 reg, p = 0.57). This was recorded
as a prediction *before* the arm finished, and the arm confirmed it.

## 4 · A reproducibility result worth keeping

Probe arm A reproduces the wave-1 Alabama joint cell **exactly** — 27.3836 / 69.6831 to four decimals
— despite diagnostics being on, which disables inductor's donated-buffer optimization under
`--compile`. Two consequences: the diagnostics are numerically inert (so they can be enabled freely
in mechanism studies), and this configuration is bit-reproducible under `--compile` at this state,
which the canonical docs treat as not guaranteed.

## 5 · Florida — the same probe where the category signal is stronger

Alabama is the smallest state with the shortest per-user histories, so the null was re-tested at
Florida (13× the windows, the best-estimated dedicated ceiling of the six). Only the 0.50 arm was
run: the 0.75 comparand is the wave-1 cell, and §4 established that the diagnostics are numerically
inert.

| arm | cat | reg | ‖∇cat‖ | ‖∇reg‖ | wall |
|---|---|---|---:|---:|---:|
| 0.75/0.25 (wave 1) | 35.8785 ± 0.401 | **77.2552** ± 0.976 | — | — | 7301 s |
| 0.50/0.50 | 35.8995 ± 0.393 | **77.0535** ± 0.955 | 0.0942 | 0.1288 | 7391 s |

Paired per-fold (same seed, same folds, n=5):

| metric | Δ (0.50 − 0.75) | per-fold | t | p |
|---|---:|---|---:|---:|
| cat | **+0.021** | −0.07, +0.16, −0.04, +0.01, +0.04 | +0.52 | 0.63 |
| reg | **−0.202** | −0.28, −0.20, −0.15, −0.18, −0.21 | **−9.66** | **0.001** |

**Category gains nothing** — +0.02 pp, an order of magnitude smaller than Alabama's already-null
+0.29. Whatever the equal split does, it does not feed the category head.

**Region gets significantly worse** — −0.20 pp, negative in **5 of 5 folds**, p = 0.001. This is the
one non-null result in the whole probe, and it runs *opposite* to the naive expectation: the region
task's loss weight was **doubled** (0.25 → 0.50) and its metric **fell**. The gradient norms show why
the naive expectation was wrong — under the equal split at Florida the reg gradient already dominates
the shared trunk (‖∇cat‖/‖∇reg‖ = **0.73**, versus 1.07 at Alabama). Up-weighting a task that is
already driving the trunk, while its head also carries the highest per-head LR (3e-3), overshoots
rather than helps. The 0.75/0.25 split is not compensating for a leak; it is compensating for the two
heads' different gradient scales, and that calibration is still correct on the clean substrate.

**Orthogonality holds, and tightens, at scale.** Florida's shared-trunk cosine is **+0.00081**,
sd 0.0066, range [−0.040, +0.038], 42% of epochs negative — even more tightly centred on zero than
Alabama's (sd 0.0126). So the orthogonality is not a small-state artifact.

### Verdict on the split

**Keep 0.75/0.25.** Across two states the equal split is neutral on category (+0.29 p=0.42;
+0.02 p=0.63) and significantly harmful on region at the larger one (−0.20, p=0.001, 5/5 folds).
The split was not an artifact of the leak.

## What this rules out, and what it doesn't

**Ruled out:** the category collapse is not a loss-balance artifact, not a gradient-conflict problem,
and not something gradient surgery addresses. Three independent interventions on that axis are all
null at n=5, and the mechanism measurement (cosine ≈ 0) explains *why* they are null rather than
leaving it as an empirical accident.

**Not ruled out:** n = 5 at **one seed**, now at two states (alabama, florida). The category nulls
(+0.29 p=0.42; +0.02 p=0.63) are unresolved rather than proven zero, though florida's +0.02 is small
enough that no plausible n rescues it. California and Texas are untested, and they are the two states
where v17 recorded its own cat-lever trade, so they are the least like the two measured here.

The florida region result (−0.20, p=0.001) is a **single-seed** finding: the paired fold test is
powerful because folds are matched, but five folds at one seed cannot separate a true effect from a
seed-specific one. It is consistent in sign across all five folds, which is why it is reported as a
result rather than noise, but it deserves a second seed before it is cited.

The reading these support is that the category signal is simply much weaker once a visit cannot see
its successor — the MTL machinery is dividing a smaller pie, not dividing it badly.

## Reproducing

```bash
bash docs/studies/closing_data/v18/run_lossweight_probe.sh   # resumable; per-arm sidecars
# sidecars: docs/results/closing_data/v18_probe/{A_cw075,B_cw050,C_pcgrad}.json
```
