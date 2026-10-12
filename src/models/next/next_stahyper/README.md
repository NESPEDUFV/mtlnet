# next_stahyper

## Why This
- STAN backbone + the GETNext `α·log_T` graph prior + a **STA-Hyper-inspired learned cluster
  prior**: `α_cluster · (softmax(cluster_probe(last_emb)) @ C)`, where rows of `C` are
  cluster-specific region-preference biases — a lightweight proxy for STA-Hyper's hypergraph
  hyperedges without full hypergraph convolution.

## Runtime Mapping
- Model registry key: `next_stahyper`
- Runtime class: `models.next.next_stahyper.head.NextHeadSTAHyper`
- Runtime file: `src/models/next/next_stahyper/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: STA-Hyper (Hypergraph-Based Spatio-Temporal Attention Network, KSEM 2025) — adapted
  via learned cluster priors; STAN backbone (Luo et al., WWW 2021); GETNext prior (Yang et al.,
  SIGIR 2022).
- GETNEXT_FINDINGS B6: MTL performance sits within ±0.7 pp of GETNext/TGSTAN (tied); the cluster
  prior `α_cluster` saturates without a corresponding gain → it approximates what the graph prior
  already provides (redundant, not adopted). See `docs/findings/GETNEXT_FINDINGS.md`.
