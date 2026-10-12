# cat-alabama-p0s0

`8b370bb1feffeaea` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0025
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 13s |
| 1 | ? | ? | 12s |
| 2 | ? | ? | 12s |
| 3 | ? | ? | 12s |
| 4 | ? | ? | 12s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 18,
 "best_value": 0.3133586049079895,
 "clipped_fraction_mean": 0.0489,
 "clipped_fraction_per_epoch": [
  0.6667,
  0.1111,
  0.0,
  0.1111,
  0.3333,
  0.2222,
  0.1111,
  0.1111,
  0.2222,
  0.1111,
  0.1111,
  0.0,
  0.2222,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1111,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0
 ],
 "compile_counters": {
  "frames_ok": 9,
  "frames_total": 10,
  "graph_breaks": 3,
  "unique_graph_breaks": 1
 },
 "epochs_to_95pct": 11,
 "epochs_to_99pct": 18,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 3.319203,
 "grad_norm_max_per_epoch": [
  3.319203,
  1.19639,
  0.688161,
  1.139733,
  1.086922,
  1.11516,
  1.065384,
  1.175847,
  1.319571,
  1.020046,
  1.394364,
  0.981462,
  1.237495,
  0.923359,
  0.780979,
  0.887115,
  0.989323,
  1.158267,
  0.742056,
  0.973515,
  0.80378,
  0.595931,
  0.838448,
  0.989921,
  0.691832,
  0.552933,
  0.544916,
  0.597545,
  0.539206,
  0.511842,
  0.546115,
  0.745935,
  0.565646,
  0.535414,
  0.548977,
  0.600284,
  0.685091,
  0.747075,
  0.666212,
  0.653702,
  0.699036,
  0.722593,
  0.753124,
  0.7237,
  0.694833,
  0.721582,
  0.726967,
  0.692654,
  0.761659,
  0.764486
 ],
 "grad_norm_mean": 0.549753,
 "grad_norm_per_epoch": [
  1.555112,
  0.801084,
  0.558931,
  0.798641,
  0.795068,
  0.764599,
  0.781565,
  0.742767,
  0.799161,
  0.700074,
  0.626929,
  0.679963,
  0.720317,
  0.563673,
  0.54495,
  0.629368,
  0.651197,
  0.646862,
  0.545959,
  0.51053,
  0.519857,
  0.366022,
  0.498957,
  0.498166,
  0.362478,
  0.455113,
  0.428493,
  0.458479,
  0.388379,
  0.383523,
  0.387857,
  0.500977,
  0.435614,
  0.38078,
  0.391395,
  0.420565,
  0.474432,
  0.558861,
  0.487319,
  0.446531,
  0.476952,
  0.455674,
  0.466936,
  0.46939,
  0.416222,
  0.394176,
  0.401386,
  0.386393,
  0.379106,
  0.380874
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00012661
  ],
  "last": [
   7e-08
  ],
  "max_observed": [
   0.00249994
  ],
  "note": "sampled after the epoch's final scheduler.step(); not the applied peak"
 },
 "nonfinite_batches": 0,
 "nonfinite_per_epoch": [
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0,
  0
 ],
 "peak_memory_gb": 3.04,
 "tail_spread_pct_of_best": 0.189,
 "train_seconds_per_epoch": 0.241,
 "train_seconds_total": 12.07,
 "val_seconds_per_epoch": 0.01,
 "val_seconds_total": 0.51,
 "val_share_of_wall": 0.0407
}
```
