# next_conv_attn

## Why This
- Conv-Attention hybrid: TCN encoder for local feature extraction followed
  by a single cross-attention pooling layer with a learned query token.
  Tests whether adaptive attention pooling beats average pooling used in
  next_temporal_cnn. Inspired by the Conformer pattern (Gulati et al. 2020).

## Runtime Mapping
- Model registry key: `next_conv_attn`
- Runtime class: `models.next.next_conv_attn.head.NextHeadConvAttn`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/models/next/next_conv_attn/head.py`
- Inspired by: Gulati et al., "Conformer: Convolution-augmented Transformer for Speech Recognition", Interspeech 2020
