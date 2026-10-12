# fairgrad

`fairgrad` implements a FairGrad-style scalarization that derives task weights from
the shared-parameter gradient interaction matrix (`G G^T`). It solves the FairGrad
fixed-point condition with a projected iterative solver and applies the resulting
weights to the task losses.

## Why This
- FairGrad-style weighting can reduce task imbalance by solving weights from
  shared-gradient interactions.

## Runtime Mapping
- Registry key: `fairgrad`
- Runtime class: `losses.fairgrad.loss.FairGradLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/fairgrad/loss.py`
- Variant notes: `docs/mtl_optimizers/fairgrad/README.md`
- Paper: [Fair Resource Allocation in Multi-Task Learning (ICML 2024)](https://openreview.net/forum?id=KLmWRMg6nL)
