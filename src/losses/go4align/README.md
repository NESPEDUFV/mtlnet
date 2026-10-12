# go4align
`go4align` implements a loss-oriented GO4Align-inspired weighting strategy that
tracks per-task risk (`loss / EMA(loss)`) and dynamic task interactions from
short-window risk correlation, then converts risk-guided indicators to task
weights via temperature-scaled softmax.

## Why This
- GO4Align-style weighting uses risk-alignment indicators to dynamically
  prioritize tasks based on evolving training interactions.

## Runtime Mapping
- Registry key: `go4align`
- Runtime class: `losses.go4align.loss.GO4AlignLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/go4align/loss.py`
- Variant notes: `docs/mtl_optimizers/go4align/README.md`
- Paper: [GO4Align: Group Optimization for Multi-Task Alignment (NeurIPS 2024)](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c98987c5ec4f30920d7190dc699e3daf-Abstract-Conference.html)
- OpenReview page: [GO4Align](https://openreview.net/forum?id=8vCs5U9Hbt)
