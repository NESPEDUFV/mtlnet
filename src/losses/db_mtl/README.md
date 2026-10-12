# db_mtl

`db_mtl` implements a Dual-Balancing-style weighting that applies log transform
to task losses, maintains a moving buffer of task gradients, and rescales tasks
by inverse buffered gradient magnitude to reduce imbalance.

## Why This
- Dual-balancing weighting rescales tasks by smoothed gradient/loss signals to
  reduce domination by easier objectives.

## Runtime Mapping
- Registry key: `db_mtl`
- Runtime class: `losses.db_mtl.loss.DBMTLLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/db_mtl/loss.py`
- Variant notes: `docs/mtl_optimizers/db_mtl/README.md`
- Paper: [Dual-Balancing for Multi-Task Learning](https://arxiv.org/abs/2308.12029)
- LibMTL reference implementation: [LibMTL/weighting/DB_MTL.py](https://github.com/median-research-group/LibMTL/blob/main/LibMTL/weighting/DB_MTL.py)
