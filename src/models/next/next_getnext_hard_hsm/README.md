# next_getnext_hard_hsm

## Why This
- Legacy registry alias (renamed 2026-05-01 → `next_stan_flow_hsm`) for the
  hierarchical-additive STAN-Flow reg head (F50 T1.2): `parent_logit[c(r)] + child_logit[r] +
  α·log_T[last][r]`, decomposing the flat ~4.7K-class softmax into cluster + region heads.

## Runtime Mapping
- Model registry key: `next_getnext_hard_hsm` (canonical key `next_stan_flow_hsm`, same class)
- Runtime class: `models.next.next_stan_flow_hsm.head.NextHeadStanFlowHSM`
- Runtime file: `src/models/next/next_stan_flow_hsm/head.py`
  (this folder's `head.py` re-exports it for the legacy import path)

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: STAN-Flow reg head + additive hierarchical bias (cf. hierarchical softmax, Mikolov
  2013 / Mnih NIPS 2008); STAN backbone (Luo et al., WWW 2021); GETNext prior (Yang et al., SIGIR 2022).
- F50 T1.2 ran at full n=5 and was **REJECTED**: MTL HSM reg 70.60 ± 10.78 vs H3-alt 73.61
  (Δ = −3.01 pp), failing the +3 pp bar (cat-encoder-absorption pattern). STL HSM matched flat
  STL at FL. See `docs/findings/MTL_FLAWS_AND_FIXES.md §2.7`.
