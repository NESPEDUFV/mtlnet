# mtlnet_ple

## Why This
- PLE (Progressive Layered Extraction) stacks multiple CGC layers
  progressively. Since CGC s2t2 is the best architecture on HGI, PLE
  is the natural multi-level extension. Each level's experts receive
  the gated outputs from the previous level, enabling progressive
  refinement of shared and task-specific representations.

## Runtime Mapping
- Model registry key: `mtlnet_ple`
- Runtime class: `models.mtl.mtlnet_ple.model.MTLnetPLE`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-13`

## Sources
- In-repo implementation: `src/models/mtl/mtlnet_ple/model.py`
- Paper: Tang et al., "Progressive Layered Extraction (PLE)", RecSys 2020
