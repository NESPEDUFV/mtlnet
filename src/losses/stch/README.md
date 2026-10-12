# stch

`stch` implements Smooth Tchebycheff scalarization with warmup and nadir-vector
normalization. During warmup it optimizes summed log-losses; after warmup it
applies smoothed max-risk scalarization across normalized task losses.


## Why This
- Smooth Tchebycheff scalarization is a principled multi-objective alternative
  that emphasizes worst-performing tasks after warmup.

## Runtime Mapping
- Registry key: `stch`
- Runtime class: `losses.stch.loss.STCHLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/stch/loss.py`
- Variant notes: `docs/mtl_optimizers/stch/README.md`
- Paper: [Smooth Tchebycheff Scalarization for Multi-Objective Optimization (ICML 2024)](https://openreview.net/forum?id=m4dO5L6eCp)
- LibMTL reference implementation: [LibMTL/weighting/STCH.py](https://github.com/median-research-group/LibMTL/blob/main/LibMTL/weighting/STCH.py)
