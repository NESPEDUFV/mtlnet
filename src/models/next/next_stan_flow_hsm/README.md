# next_stan_flow_hsm

## Why This
- Hierarchical-additive variant of STAN-Flow (F50 T1.2): `final_logits = parent_logit[c(r)] +
  child_logit[r] + α·log_T[last][r]`, decomposing the flat ~4.7K-class softmax into a
  cluster-level parent head + a region-level child head to test whether a hierarchical
  inductive bias eases the FL-scale head-side gradient noise. Legacy alias `next_getnext_hard_hsm`.

## Runtime Mapping
- Model registry key: `next_stan_flow_hsm` (legacy alias `next_getnext_hard_hsm`, same class)
- Runtime class: `models.next.next_stan_flow_hsm.head.NextHeadStanFlowHSM`
- Runtime file: `src/models/next/next_stan_flow_hsm/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: STAN-Flow (`next_stan_flow`) reg head + additive hierarchical bias (cf. hierarchical
  softmax, Mikolov 2013 / Mnih NIPS 2008); STAN backbone (Luo et al., WWW 2021).
- F50 T1.2 ran at full n=5 and was **REJECTED**: STL HSM matched flat STL at FL, but MTL HSM reg
  = 70.60 ± 10.78 vs H3-alt 73.61 (Δ = −3.01 pp), failing the +3 pp acceptance bar — the
  cat-encoder-absorption pattern. See `docs/findings/MTL_FLAWS_AND_FIXES.md §2.7`.
