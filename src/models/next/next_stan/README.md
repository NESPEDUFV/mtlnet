# next_stan — STAN-inspired next-location head

Reference: Luo, Liu, Liu. *STAN: Spatio-Temporal Attention Network for Next Location Recommendation.* The Web Conference (WWW) 2021. [arXiv:2102.04095](https://arxiv.org/abs/2102.04095) · [Repo](https://github.com/yingtaoluo/Spatial-Temporal-Attention-Network-for-POI-Recommendation).

## Why This
- Bi-layer spatio-temporal self-attention next head, adapted from STAN (Luo et al., WWW 2021).
  It is the shared attention backbone re-used by every STAN-Flow reg head (`next_stan_flow`,
  `next_stan_flow_hsm`, `next_stan_flow_dualtower`, `next_getnext`, `next_tgstan`,
  `next_stahyper`) and beats the `next_gru` prior as a standalone STL region head.

## Runtime Mapping
- Model registry key: `next_stan`
- Runtime class: `models.next.next_stan.head.NextHeadSTAN`
- Runtime file: `src/models/next/next_stan/head.py`

## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: STAN (Luo, Liu, Liu, WWW 2021, arXiv:2102.04095).
- P1 region-head ablation: `next_stan` beats `next_gru` +2.26 pp (AL) / +3.36 pp (AZ) Acc@10.
  See `docs/findings/SOTA_STAN_BASELINE.md`.

## Architecture

Bi-layer self-attention with a fully-learnable pairwise position bias. Layer 1 aggregates trajectory context; Layer 2 is a last-position query attending over all positions (STAN's "matching" layer adapted to classification). Bidirectional (no causal mask — all 9 input positions are past observations of a later target).

```
[B, 9, embed_dim]
    ↓ Linear + LN + Dropout
[B, 9, d_model]
    ↓ Trajectory self-attn (bidir, learnable pair bias) + FFN
[B, 9, d_model]
    ↓ Matching self-attn (last-position query, same bias matrix)
[B, d_model]
    ↓ LayerNorm + Dropout + Linear
[B, num_classes]
```

## Adaptation note

STAN's original paper computes the pairwise bias from raw time-interval `Δt_ij` and great-circle distance `Δd_ij`. Our `next_region.parquet` carries check2HGI embeddings only — no raw timestamps or coordinates. The pairwise bias here is **learnable per (head, i, j) for relative positions** `[0, 9) × [0, 9)`. This is consistent with STAN's "explicit pairwise effect" design: the bias is the same shape and role, but the feature extractor for the pair is check2HGI's encoder (which internalises per-check-in spatio-temporal context) rather than an explicit ΔT/ΔD lookup.

## Results (P1 region-head ablation, 5f×50ep, region-emb input)

| State | next_gru (prior) | **next_stan** | Δ Acc@10 |
|---|---:|---:|---:|
| AL | 56.94 ± 4.01 | **59.20 ± 3.62** | +2.26 |
| AZ | 48.88 ± 2.48 | **52.24 ± 2.38** | **+3.36** |

See `docs/findings/SOTA_STAN_BASELINE.md` for the full comparison table and `docs/findings/POSITIONING_VS_HMT_GRN.md` for positioning against HMT-GRN (SIGIR'22), the canonical hierarchical-MTL next-POI baseline.

## Usage

Standalone (STL next-region on AL):

```bash
python scripts/p1_region_head_ablation.py \
    --state alabama --heads next_stan \
    --folds 5 --epochs 50 --input-type region \
    --tag STAN_al_5f50ep
```

Inside MTL (swap in as region head via `--reg-head`):

```bash
python scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state alabama --engine check2hgi \
    --model mtlnet_crossattn --mtl-loss pcgrad \
    --reg-head next_stan \
    --task-a-input-type checkin --task-b-input-type region \
    --folds 5 --epochs 50 --max-lr 0.003
```
