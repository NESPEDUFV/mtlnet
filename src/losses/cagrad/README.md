# cagrad

## Why This
- CAGrad maximizes the worst local improvement of any task within a
  conflict-averse ball around the average gradient. For 2 tasks the
  subproblem is cheap (scalar optimization). Provides a principled
  middle ground between equal_weight and NashMTL.

## Runtime Mapping
- Registry key: `cagrad`
- Runtime class: `losses.cagrad.loss.CAGradLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/losses/cagrad/loss.py`
- Paper: Liu et al., "Conflict-Averse Gradient Descent for Multi-task Learning", NeurIPS 2021
- Official code: https://github.com/Cranial-XIX/CAGrad
