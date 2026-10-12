# bayesagg_mtl


`bayesagg_mtl` implements a Bayesian uncertainty-inspired gradient aggregation
approximation for our current two-task setup. It estimates per-task gradient
uncertainty from running second moments on shared-parameter gradients and uses
precision-weighted task scalarization.

## Why This
- BayesAgg-style weighting approximates uncertainty-aware gradient aggregation
  while staying lightweight enough for staged ablations.

## Runtime Mapping
- Registry key: `bayesagg_mtl` (alias: `bayesagg`)
- Runtime class: `losses.bayesagg_mtl.loss.BayesAggMTLLoss`


## Evidence Status
- Current: `implemented`
- Last Reviewed: `2026-04-11`

## Sources
- In-repo implementation: `src/losses/bayesagg_mtl/loss.py`
- Variant notes: `docs/mtl_optimizers/bayesagg_mtl/README.md`
- Paper: [Bayesian Uncertainty for Gradient Aggregation in Multi-Task Learning (ICML 2024)](https://arxiv.org/abs/2402.04005)
- Official code: [ssi-research/BayesAgg_MTL](https://github.com/ssi-research/BayesAgg_MTL)
- Core reference module: [BayesAgg_MTL/BayesAggMTL.py](https://github.com/ssi-research/BayesAgg_MTL/blob/main/BayesAgg_MTL/BayesAggMTL.py)
