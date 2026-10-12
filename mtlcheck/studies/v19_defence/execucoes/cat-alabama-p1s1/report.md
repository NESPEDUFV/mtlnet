# cat-alabama-p1s1

`55e531e6bc8a9283` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0025
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 12s |
| 1 | ? | ? | 12s |
| 2 | ? | ? | 12s |
| 3 | ? | ? | 12s |
| 4 | ? | ? | 12s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 15,
 "best_value": 0.30379214882850647,
 "clipped_fraction_mean": 0.0533,
 "clipped_fraction_per_epoch": [
  1.0,
  0.6667,
  0.2222,
  0.0,
  0.2222,
  0.0,
  0.0,
  0.1111,
  0.0,
  0.0,
  0.1111,
  0.3333,
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
 "epochs_to_95pct": 8,
 "epochs_to_99pct": 15,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 8.663741,
 "grad_norm_max_per_epoch": [
  8.663741,
  2.021243,
  1.081979,
  0.880543,
  1.211475,
  0.849383,
  0.964872,
  1.008769,
  0.81222,
  0.972232,
  1.408703,
  1.214223,
  0.896123,
  0.775313,
  0.833127,
  0.780134,
  0.829929,
  0.972239,
  0.889936,
  0.508377,
  0.55751,
  0.60866,
  0.495402,
  0.501902,
  0.554413,
  0.763879,
  0.831495,
  0.655647,
  0.671082,
  0.665157,
  0.676452,
  0.678234,
  0.685849,
  0.752611,
  0.635452,
  0.7739,
  0.786341,
  0.741523,
  0.800401,
  0.716041,
  0.72434,
  0.817642,
  0.941187,
  0.755697,
  0.725905,
  0.728262,
  0.750799,
  0.811727,
  0.762322,
  0.788855
 ],
 "grad_norm_mean": 0.599535,
 "grad_norm_per_epoch": [
  3.249537,
  1.282714,
  0.821632,
  0.66247,
  0.799883,
  0.486887,
  0.675967,
  0.616003,
  0.596089,
  0.688013,
  0.838246,
  0.781921,
  0.574497,
  0.540761,
  0.613151,
  0.602745,
  0.534858,
  0.614093,
  0.691361,
  0.340167,
  0.350324,
  0.457969,
  0.343407,
  0.36276,
  0.378073,
  0.427251,
  0.463933,
  0.489692,
  0.506588,
  0.485734,
  0.498203,
  0.442517,
  0.474874,
  0.49067,
  0.483343,
  0.470329,
  0.588116,
  0.507438,
  0.51333,
  0.620399,
  0.566421,
  0.500328,
  0.509605,
  0.50048,
  0.474576,
  0.438152,
  0.422803,
  0.41114,
  0.39606,
  0.391214
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
 "tail_spread_pct_of_best": 0.76,
 "train_seconds_per_epoch": 0.232,
 "train_seconds_total": 11.58,
 "val_seconds_per_epoch": 0.008,
 "val_seconds_total": 0.39,
 "val_share_of_wall": 0.0329
}
```
