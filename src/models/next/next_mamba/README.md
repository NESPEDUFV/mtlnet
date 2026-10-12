# next_mamba

## Why This
- A dependency-free, pure-PyTorch **selective state-space (Mamba-lite)** next head: diagonal SSM
  recurrence with input-dependent Δ/B/C selectivity + SiLU gate + D skip, sequential scan over the
  9-step window. Probes whether an SSM encoder beats the recurrent/attention incumbents.

## Runtime Mapping
- Model registry key: `next_mamba`
- Runtime class: `models.next.next_mamba.head.NextHeadMamba`
- Runtime file: `src/models/next/next_mamba/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: Mamba selective SSM (Gu & Dao, 2023) — a faithful selective-SSM block (conv1d short
  filter and hardware parallel scan omitted, irrelevant at L=9), not the full Mamba repo.
- mtl_improvement Tier-S Prong-B: built, unit-test-gated, AL-screened — **loses both tasks**
  (cat 41.44 vs `next_gru` 49.97, −8.53; reg 61.66 vs `next_stan_flow` α=0 62.88, −1.22) →
  no promotion. See `docs/studies/archive/mtl_improvement/log.md` (2026-06-03 Prong-B Mamba) and
  `docs/results/mtl_improvement/TIER01_RESULTS.md`.
