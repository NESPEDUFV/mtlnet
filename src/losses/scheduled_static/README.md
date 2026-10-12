# scheduled_static

## Why This
- Static-weight scalarization whose `category_weight` is interpolated (linear ramp or hard
  step) from `cat_weight_start` toward `cat_weight_end` across training, so the gradient budget
  can shift from the cat task to the reg task in the second half (F40/F62 two-phase hypothesis).

## Runtime Mapping
- Loss registry key: `scheduled_static`
- Runtime class: `losses.scheduled_static.loss.ScheduledStaticWeightLoss`
- Runtime file: `src/losses/scheduled_static/loss.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- In-repo implementation: `src/losses/scheduled_static/loss.py` (extends `EqualWeightLoss`).
- F62 two-phase (step mode, `cat_weight_start=0` → `cat_weight_end=0.75` at ep 10) was run
  clean at full n=5 and **REJECTED**: reg 60.25 ± 1.26 Acc@10, sub-anchor (−10.87 pp vs the
  P4 champion). Coarse two-phase scheduling does not replicate P4's per-batch alternating
  granularity. See `docs/findings/F50_T4_FINAL_SYNTHESIS.md §3.3` and
  `docs/findings/F50_T4_PRIORITIZATION.md`.
