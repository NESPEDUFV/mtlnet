# dwa

## Why This
- Dynamic Weight Average adjusts task weights based on loss rate of change.
  Cheapest possible adaptive method: zero gradient computation overhead,
  only uses loss values. Good diagnostic baseline between static weighting
  and gradient-based methods.

## Runtime Mapping
- Registry key: `dwa`
- Runtime class: `losses.dwa.loss.DWALoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/losses/dwa/loss.py`
- Paper: Liu et al., "End-to-End Multi-Task Learning with Attention", CVPR 2019
