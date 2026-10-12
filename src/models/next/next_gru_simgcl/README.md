# next_gru_simgcl

## Why This
- The incumbent GRU cat encoder + a **SimGCL auxiliary contrastive loss** bolt-on (norm-bounded
  sign-preserving noise → two views → InfoNCE consistency term via `model.aux_loss`). Isolates
  "does a contrastive regularizer help?" orthogonally to the encoder-architecture axis; eval-mode
  forward is identical to `next_gru`.

## Runtime Mapping
- Model registry key: `next_gru_simgcl`
- Runtime class: `models.next.next_gru_simgcl.head.NextHeadGRUSimGCL`
- Runtime file: `src/models/next/next_gru_simgcl/head.py`

## Evidence Status
- Current: `ablated`
- Last Reviewed: `2026-06-16`

## Sources
- Lineage: SimGCL (Yu et al., SIGIR 2022) auxiliary contrastive regularizer; GRU incumbent cat
  encoder (`next_gru`).
- mtl_improvement Tier-S Prong-B: built, unit-test-gated, and screened — **ties the frozen tuned
  floor** (+0.06, real but not a win) and was dropped. See
  `docs/studies/archive/mtl_improvement/log.md` (2026-06-03 Prong-B SimGCL) and
  `docs/results/mtl_improvement/TIER01_RESULTS.md`.
