# excess_mtl

`excess_mtl` implements an ExcessMTL-style robust update that accumulates squared
shared gradients per task and updates task weights with an exponential robust-risk
step. This follows the excess-risk weighting idea while fitting the current loss
registry API.

## Why This
- ExcessMTL-style robust weighting targets excess-risk control under task
  imbalance/noise.

## Runtime Mapping
- Registry key: `excess_mtl` (alias: `excessmtl`)
- Runtime class: `losses.excess_mtl.loss.ExcessMTLLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/excess_mtl/loss.py`
- Variant notes: `docs/mtl_optimizers/excess_mtl/README.md`
- Paper: [Robust Multi-Task Learning with Excess Risks (ICML 2024)](https://openreview.net/forum?id=JzWFmMySpn)
- LibMTL reference implementation: [LibMTL/weighting/ExcessMTL.py](https://github.com/median-research-group/LibMTL/blob/main/LibMTL/weighting/ExcessMTL.py)
