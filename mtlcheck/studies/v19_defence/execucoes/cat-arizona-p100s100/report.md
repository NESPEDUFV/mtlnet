# cat-arizona-p100s100

`04590e05324a0c1f` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **arizona** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 25s |
| 1 | ? | ? | 25s |
| 2 | ? | ? | 25s |
| 3 | ? | ? | 25s |
| 4 | ? | ? | 25s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 32,
 "best_value": 0.3212296664714813,
 "clipped_fraction_mean": 0.0311,
 "clipped_fraction_per_epoch": [
  1.0,
  0.3889,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0556,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0556,
  0.0,
  0.0,
  0.0556,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 10,
 "epochs_to_99pct": 26,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.980248,
 "grad_norm_max_per_epoch": [
  5.980248,
  1.221119,
  0.832637,
  0.909068,
  0.860519,
  0.96728,
  0.772262,
  0.838816,
  0.873201,
  0.881675,
  1.064364,
  0.947666,
  0.917888,
  0.980956,
  0.907857,
  1.013988,
  0.969322,
  0.7154,
  1.010963,
  0.90779,
  0.682322,
  0.487357,
  0.618302,
  0.610193,
  0.609261,
  0.528956,
  0.650162,
  0.563362,
  0.800717,
  0.74903,
  0.48883,
  0.479402,
  0.604342,
  0.515987,
  0.592459,
  0.672172,
  0.419512,
  0.5797,
  0.403755,
  0.50493,
  0.565637,
  0.425102,
  0.483468,
  0.652184,
  0.451017,
  0.523334,
  0.594654,
  0.697181,
  0.420309,
  0.644933
 ],
 "grad_norm_mean": 0.459963,
 "grad_norm_per_epoch": [
  2.669929,
  0.922177,
  0.602892,
  0.456971,
  0.485096,
  0.499547,
  0.420113,
  0.541114,
  0.551777,
  0.495718,
  0.534349,
  0.627666,
  0.495013,
  0.701886,
  0.591178,
  0.59646,
  0.577949,
  0.493212,
  0.474753,
  0.502451,
  0.402173,
  0.324039,
  0.382548,
  0.382594,
  0.40064,
  0.339507,
  0.367902,
  0.349285,
  0.352873,
  0.473199,
  0.352606,
  0.340823,
  0.310483,
  0.32681,
  0.323422,
  0.315103,
  0.313543,
  0.381557,
  0.290196,
  0.315625,
  0.33863,
  0.276466,
  0.273909,
  0.288153,
  0.276859,
  0.247137,
  0.24733,
  0.279939,
  0.241179,
  0.24337
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   2.528e-05
  ],
  "last": [
   1e-08
  ],
  "max_observed": [
   0.0005
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
 "peak_memory_gb": 3.266,
 "tail_spread_pct_of_best": 0.337,
 "train_seconds_per_epoch": 0.484,
 "train_seconds_total": 24.22,
 "val_seconds_per_epoch": 0.015,
 "val_seconds_total": 0.77,
 "val_share_of_wall": 0.0308
}
```
