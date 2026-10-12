# next_stan_flow_dualtower

## Why This
- Reg-private dual-tower STAN-Flow head: a **private** full-STAN backbone on the raw
  `[B,9,64]` region sequence (the STL reg pathway) is fused (`gated` / `private_only` / `aux`)
  with the cross-attn **shared** pathway, then a single classifier + the `α·log_T` prior. It
  restores the private backbone the cross-attn MTL regime was missing (the "regime finding").

## Runtime Mapping
- Model registry key: `next_stan_flow_dualtower`
- Runtime class: `models.next.next_stan_flow_dualtower.head.NextHeadStanFlowDualTower`
- Runtime file: `src/models/next/next_stan_flow_dualtower/head.py`

## Evidence Status
- Current: `promoted`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: STAN-Flow (`next_stan_flow`) reg head extended with a private reg tower; STAN
  attention backbone (Luo et al., WWW 2021); GETNext-style `α·log_T` prior (Yang et al., SIGIR 2022).
- Champion-G component (`fusion_mode=aux freeze_alpha=True alpha_init=0.0`, with
  `mtlnet_crossattn_dualtower`): a single joint MTL model that matches the STL reg ceiling and
  beats the cat ceiling (+~3 pp) at 4 states × 4 seeds. See `docs/NORTH_STAR.md` (2026-06-06
  banner) and `docs/studies/archive/mtl_improvement/FINAL_SYNTHESIS.md` / `CHAMPION.md`.
