# aligned_mtl

## Why This
- Aligned-MTL decomposes the gradient matrix via eigendecomposition to
  align principal components, making aligned gradients orthogonal and of
  equal magnitude. For 2 tasks the eigendecomposition is on a 2x2 matrix
  (negligible cost). No hyperparameters required.

## Runtime Mapping
- Registry key: `aligned_mtl`
- Runtime class: `losses.aligned_mtl.loss.AlignedMTLLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/losses/aligned_mtl/loss.py`
- Paper: Senushkin et al., "Independent Component Alignment for Multi-Task Learning", CVPR 2023
- Official code: https://github.com/SamsungLabs/MTL
