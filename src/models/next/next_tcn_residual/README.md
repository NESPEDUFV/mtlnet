# next_tcn_residual

## Why This
- Canonical TCN with residual blocks and exponential dilation scheduling
  (Bai et al. 2018). Direct upgrade over next_temporal_cnn: adds skip
  connections for better gradient flow and explicit dilation [1,2,4,8]
  covering the full 9-step window.

## Runtime Mapping
- Model registry key: `next_tcn_residual`
- Runtime class: `models.next.next_tcn_residual.head.NextHeadTCNResidual`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/models/next/next_tcn_residual/head.py`
- Paper: Bai et al., "An Empirical Evaluation of Generic Convolutional and Recurrent Networks for Sequence Modeling", 2018
