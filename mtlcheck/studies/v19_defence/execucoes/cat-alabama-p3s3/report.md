# cat-alabama-p3s3

`d5a8fabf1479b5d7` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **3** · split_seed **3** · engine `check2hgi_v18`
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
 "best_epoch": 21,
 "best_value": 0.30189886689186096,
 "clipped_fraction_mean": 0.0644,
 "clipped_fraction_per_epoch": [
  0.7778,
  0.1111,
  0.3333,
  0.2222,
  0.5556,
  0.1111,
  0.0,
  0.5556,
  0.1111,
  0.0,
  0.1111,
  0.0,
  0.2222,
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
 "epochs_to_99pct": 21,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.62865,
 "grad_norm_max_per_epoch": [
  4.62865,
  1.354824,
  1.53073,
  1.1392,
  1.562505,
  1.01253,
  0.818947,
  1.829732,
  1.040863,
  0.766173,
  1.272661,
  0.902363,
  1.226199,
  1.089869,
  0.90978,
  0.985217,
  0.695325,
  0.621398,
  0.958574,
  0.920858,
  0.5154,
  0.572421,
  0.586835,
  0.589565,
  0.420662,
  0.570955,
  0.585977,
  0.632265,
  0.548873,
  0.682912,
  0.565763,
  0.698464,
  0.647314,
  0.658789,
  0.69203,
  0.602368,
  0.681338,
  0.713977,
  0.704875,
  0.741263,
  0.731272,
  0.8324,
  0.681865,
  0.753267,
  0.71429,
  0.73819,
  0.725915,
  0.675155,
  0.755391,
  0.695645
 ],
 "grad_norm_mean": 0.578953,
 "grad_norm_per_epoch": [
  1.807886,
  0.918988,
  1.046958,
  0.847317,
  1.050556,
  0.714467,
  0.600004,
  1.206827,
  0.782738,
  0.549117,
  0.693412,
  0.523747,
  0.770866,
  0.747786,
  0.539744,
  0.755831,
  0.485716,
  0.470862,
  0.570005,
  0.48704,
  0.369234,
  0.410411,
  0.454033,
  0.377126,
  0.315532,
  0.378492,
  0.487167,
  0.445802,
  0.394153,
  0.505309,
  0.457333,
  0.484731,
  0.463763,
  0.512393,
  0.517985,
  0.445863,
  0.5433,
  0.491594,
  0.457187,
  0.474002,
  0.482068,
  0.500561,
  0.488998,
  0.46188,
  0.434464,
  0.403673,
  0.431375,
  0.392172,
  0.414017,
  0.383164
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
 "tail_spread_pct_of_best": 1.2,
 "train_seconds_per_epoch": 0.233,
 "train_seconds_total": 11.63,
 "val_seconds_per_epoch": 0.008,
 "val_seconds_total": 0.4,
 "val_share_of_wall": 0.033
}
```
