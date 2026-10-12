# next_transformer_relpos

## Why This
- Lightweight Transformer with learned relative position bias (ALiBi-inspired)
  instead of absolute positional encodings. For a fixed 9-step check-in
  window, relative distance ("3 steps ago") is more informative than
  absolute position index. Smaller than default: 2 layers, 4 heads.

## Runtime Mapping
- Model registry key: `next_transformer_relpos`
- Runtime class: `models.next.next_transformer_relpos.head.NextHeadTransformerRelPos`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/models/next/next_transformer_relpos/head.py`
- Paper: Press et al., "Train Short, Test Long: Attention with Linear Biases" (ALiBi), ICLR 2022
- Paper: Shaw et al., "Self-Attention with Relative Position Representations", NAACL 2018
