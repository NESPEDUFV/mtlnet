# next_tgstan

## Why This
- STAN backbone + the GETNext `α·log_T` graph prior modulated by a **per-sample dynamic gate**:
  `α · gate(last_emb) ⊙ (softmax(probe(last_emb)) @ log_T)`. The gate lets the model amplify or
  suppress specific transitions per-sample, capturing TGSTAN's idea that the transition graph is
  context-modulated rather than static.

## Runtime Mapping
- Model registry key: `next_tgstan`
- Runtime class: `models.next.next_tgstan.head.NextHeadTGSTAN`
- Runtime file: `src/models/next/next_tgstan/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: TGSTAN (Liu, Gao, Chen, "Improving the spatial-temporal aware attention network with
  dynamic trajectory graph learning…", IP&M 2023) — adapted as a dynamic gate on the prior (no
  raw POI IDs / Δt / Δd available); STAN backbone (Luo et al., WWW 2021); GETNext prior (Yang et
  al., SIGIR 2022).
- GETNEXT_FINDINGS B6: MTL performance ties GETNext/STA-Hyper within ±0.7 pp; the learned α is a
  property of scale, not the head variant → the dynamic gate adds no new signal, not adopted. See
  `docs/findings/GETNEXT_FINDINGS.md`.
