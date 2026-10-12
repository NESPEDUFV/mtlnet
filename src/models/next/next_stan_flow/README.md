# next_stan_flow

## Why This
- STAN attention backbone + an `α·log_T[last_region_idx]` trajectory-flow prior using the
  **hard** observed last-region index (gathered via the aux side-channel), rather than a soft
  probe. This is the paper-facing name for the champion reg head (legacy alias
  `next_getnext_hard` / `NextHeadGETNextHard`).

## Runtime Mapping
- Model registry key: `next_stan_flow` (legacy alias `next_getnext_hard`, same class object)
- Runtime class: `models.next.next_stan_flow.head.NextHeadStanFlow`
- Runtime file: `src/models/next/next_stan_flow/head.py`

## Evidence Status
- Current: `promoted`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: trajectory-flow prior inspired by GETNext (Yang et al., SIGIR 2022), adapted from
  next-POI to next-region (TIGER tracts); STAN attention backbone (Luo et al., WWW 2021).
- Champion reg head of the committed B9 / H3-alt recipe: `--reg-head next_getnext_hard`
  (`docs/NORTH_STAR.md §Champion`, `docs/PAPER_BASELINES_STRATEGY.md §"STAN-Flow naming"`).
- Hard-index recovery of +3 to +9 pp Acc@10 over the soft probe — `docs/findings/B5_HARD_VS_SOFT_INFERENCE.md`.
