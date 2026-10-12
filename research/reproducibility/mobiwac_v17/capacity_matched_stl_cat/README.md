# Capacity-matched dedicated category baseline — raw results (POST-SUBMISSION)

> **What this is.** The negative control for the Chapter 5 joint-model win: a dedicated
> (single-task) category model widened until its parameter count matches the joint model's, run
> under the same protocol as the published STL ceilings. It answers the examiner question *"if the
> gain comes from the trunk, would a dedicated model of the same capacity recover it?"*
>
> **Status: POST-SUBMISSION.** These runs happened after the MobiWac manuscript was submitted.
> They are frame-level analysis (Chapter 6 / appendix) and **never** enter Chapter 5.
>
> **This folder is the stable source of record for these numbers** (closes fact-gate finding
> NEW-1 / REV-013: the earlier summary was uncommitted). It was promoted from
> `docs/results/closing_data/capacity_matched_stl_cat/` so Appendix F does not depend on a
> working results directory. The former location remains a compatibility copy. Design and
> licensing contract:
> `articles/dissertacao/storyline/audit/capacity_baseline_experiment.md`.

## Protocol

- Model: `next_gru` (the dedicated category head used for the published category ceilings),
  width scaled via `--model-param hidden_dim=<w>`; nothing else changed.
- Engine `check2hgi_dk_ovl`, 5 folds × seeds {0, 1, 7, 100} = **n=20 per arm**.
- Scorer `scripts/closing_data/score_stl_cat_ceiling.py` — macro-F1 at the f1-best epoch,
  fold-mean: the **same convention as the published ceilings**, so the values are comparable.
- Recipes swept around the published ceiling's winners (batch size / max-lr).

## Parameter audit (local, `numel` over trainable params)

| Dataset | joint v17 | dedicated cat (h=256, ceiling width) | capacity-matched width | matched count |
|---|---|---|---|---|
| Alabama | 4,197,621 | 644,359 | `hidden_dim=672` | 4,207,399 (100.2%) |
| California | 5,151,189 | 644,359 | `hidden_dim=752` | 5,249,719 (101.9%) |

Reproduces the parameter figures quoted in the MobiWac method section.

## Results (n=20 per arm; macro-F1)

**Alabama** (`alabama_h672/`, jobs `d38a1382` + pilot cell `c0cc0edd`)

| Arm (h=672, ~4.2M params) | n | mean | std |
|---|---|---|---|
| bs2048 @ lr 0.0025 (**best**) | 20 | **56.16** | 1.89 |
| bs8192 @ lr 0.005 | 20 | 55.74 | 2.00 |
| bs2048 @ lr 0.005 (the ceiling's recipe) | 20 | 55.61 | 2.05 |

**California** (`california_h752/`, job `4cff4b00`)

| Arm (h=752, ~5.2M params) | n | mean | std |
|---|---|---|---|
| bs8192 @ lr 0.0025 (**best**) | 20 | **69.88** | 0.26 |
| bs8192 @ lr 0.005 (the ceiling's recipe) | 20 | 68.21 | 0.54 |

## Reference points (same scorer, n=20; `v17_completion/CEILINGS_N20_FINAL.md`)

| Dataset | dedicated ceiling (h=256, best-vs-best) | capacity-matched (best arm) | joint v17 (diagnostic-best) |
|---|---|---|---|
| Alabama | 56.82 ±0.03 | 56.16 ±1.89 (**−0.66**) | 64.54 (**−8.38** from the matched arm) |
| California | 70.60 ±0.07 | 69.88 ±0.26 (**−0.72**) | 77.05 (**−7.17** from the matched arm) |

Convention note: the joint values above are **diagnostic-best**, the convention in which the
ceiling deltas are reported in `CEILINGS_N20_FINAL.md`. Chapter 6 quotes the **joint-best** AL
value (64.51) to match Chapter 5's Table 3; the verdict is identical under either basis, but the
two conventions must never be mixed inside one comparison (`AGENT_GUARDRAILS` N5).

## Reading

At both datasets, giving the dedicated category model the joint model's parameter budget leaves
it **at or slightly below its own tuned narrow optimum** (−0.66 AL, −0.72 CA) and recovers **none**
of the joint model's margin (−8.38 AL, −7.17 CA). Parameter count alone, without the second task's
training signal, does not reproduce the gain **in this setting** — category task, two of six
datasets, one width point per dataset, width scaling rather than depth.

**Correction to an interim reading (recorded deliberately).** A partial California read taken at
seeds {0,1,7} of the *first* arm only (bs8192@0.005) gave 68.35 and was described as "the same
direction, larger magnitude" than Alabama. The completed sweep refutes the magnitude half: the
second arm (lr 0.0025) reaches 69.88, so California's shortfall (−0.72) is **essentially the same
as Alabama's** (−0.66), not larger. Any prose still carrying the interim characterization must be
corrected. The direction of the verdict never changed.

**Methodological observation.** At both datasets the widened arm's optimum sits at a **lower
learning rate** than the narrow ceiling's winning recipe (AL 0.0025 vs 0.005; CA 0.0025 vs 0.005).
The sweep therefore did not merely re-run the ceiling recipe at a larger width: it found the wide
model's own better setting, and the verdict holds at that setting. This strengthens the fairness
argument, but the asymmetry remains and must travel with the number: the ceiling was tuned
best-vs-best over a wider recipe grid than the 3-recipe (AL) / 2-recipe (CA) sweeps here.

## Files

- `alabama_h672/alabama_h672_bs{BS}_lr{LR}_s{SEED}.json` — 12 cells (3 arms × 4 seeds), each with
  `cat_per_fold` (5 folds). The `bs2048_lr0.005_s0` cell came from the pilot job `c0cc0edd`
  (renamed from `capmatch_al_h672_s0.json` to the canonical pattern; contents unmodified).
- `california_h752/california_h752_bs8192_lr{LR}_s{SEED}.json` — 8 cells (2 arms × 4 seeds).
- `param_audit_pilot.txt` — in-job parameter count, Alabama widths.
- `capacity_matched_summary.json` — per-arm aggregates recomputed from the JSONs in this folder.
