# next_getnext_hard

## Why This
- Legacy registry alias (renamed 2026-05-01 → `next_stan_flow`) for the **champion reg head**:
  STAN backbone + `α·log_T[last_region_idx]` trajectory-flow prior using the hard observed
  last-region index. Result-file paths and ~60 historical scripts still use the `gethard`
  segment, so the alias is preserved.

## Runtime Mapping
- Model registry key: `next_getnext_hard` (canonical key `next_stan_flow`, same class object)
- Runtime class: `models.next.next_stan_flow.head.NextHeadStanFlow`
- Runtime file: `src/models/next/next_stan_flow/head.py`
  (this folder's `head.py` re-exports it for the legacy import path)

## Evidence Status
- Current: `promoted`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: GETNext-style `α·log_T` prior (Yang et al., SIGIR 2022) on a STAN backbone (Luo et
  al., WWW 2021), adapted next-POI → next-region.
- Champion reg head of the committed B9 / H3-alt recipe (`--reg-head next_getnext_hard`):
  `docs/NORTH_STAR.md §Champion`, `docs/PAPER_BASELINES_STRATEGY.md §"STAN-Flow naming"`.
- Hard index beats the soft probe (`next_getnext`) +3 to +9 pp Acc@10 —
  `docs/findings/B5_HARD_VS_SOFT_INFERENCE.md`.
