# next_getnext

## Why This
- STAN attention backbone + a GETNext-style `α·log_T` region-transition prior, where the
  last-region identity is approximated by a **soft probe** (`softmax(probe(last_emb)) @ log_T`)
  because `next_region.parquet` carries no explicit per-step region index.

## Runtime Mapping
- Model registry key: `next_getnext`
- Runtime class: `models.next.next_getnext.head.NextHeadGETNext`
- Runtime file: `src/models/next/next_getnext/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: GETNext (Yang, Liu, Zhao, SIGIR 2022, arXiv:2303.04741) — adapted from next-POI to
  next-region; this is the graph-prior pattern only, not a faithful reproduction.
- B5 inference-time ablation (`docs/findings/B5_HARD_VS_SOFT_INFERENCE.md`): the soft probe is
  beaten by the hard last-region index (`next_stan_flow` / `next_getnext_hard`) by +3 to +9 pp
  Acc@10 near convergence. The hard-index variant was adopted as the champion reg head; the
  soft-probe predecessor was dropped. See `docs/PAPER_BASELINES_STRATEGY.md`.
