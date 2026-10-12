# cat-arizona-p7s7

`a7f0899232ae2698` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **arizona** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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

- ties at the decision boundary: [(1, {'top3': 1, 'top5': 0})]

## Diagnostics

```json
{
 "best_epoch": 42,
 "best_value": 0.32315725088119507,
 "clipped_fraction_mean": 0.0422,
 "clipped_fraction_per_epoch": [
  1.0,
  0.6667,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0556,
  0.0,
  0.0556,
  0.1111,
  0.1111,
  0.0,
  0.0556,
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
 "epochs_to_95pct": 11,
 "epochs_to_99pct": 30,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 6.358084,
 "grad_norm_max_per_epoch": [
  6.358084,
  1.627825,
  0.892442,
  0.848093,
  0.819599,
  0.603487,
  1.094728,
  0.883165,
  1.223847,
  1.03923,
  1.113535,
  0.924454,
  1.135681,
  0.903403,
  1.011373,
  0.866401,
  0.834786,
  0.863482,
  0.837672,
  0.777898,
  0.650117,
  0.816385,
  0.629856,
  0.67278,
  0.79385,
  0.578134,
  0.921038,
  0.76066,
  0.633971,
  0.75541,
  0.799312,
  0.610439,
  0.557463,
  0.670874,
  0.530256,
  0.448885,
  0.495457,
  0.615693,
  0.507165,
  0.648957,
  0.579717,
  0.544154,
  0.60301,
  0.639372,
  0.652777,
  0.503202,
  0.507376,
  0.492816,
  0.665226,
  0.678571
 ],
 "grad_norm_mean": 0.491971,
 "grad_norm_per_epoch": [
  2.803434,
  1.100842,
  0.68264,
  0.610534,
  0.489781,
  0.441987,
  0.709253,
  0.543318,
  0.557198,
  0.659719,
  0.698446,
  0.569793,
  0.626168,
  0.55519,
  0.619896,
  0.560472,
  0.484269,
  0.463234,
  0.472859,
  0.436685,
  0.409668,
  0.490067,
  0.410928,
  0.451056,
  0.456245,
  0.421902,
  0.425861,
  0.454623,
  0.329385,
  0.357551,
  0.47979,
  0.384601,
  0.347559,
  0.34844,
  0.334214,
  0.317861,
  0.30353,
  0.344779,
  0.310422,
  0.286714,
  0.285214,
  0.33074,
  0.352336,
  0.29576,
  0.292781,
  0.26852,
  0.245885,
  0.262769,
  0.245532,
  0.268122
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
 "tail_spread_pct_of_best": 0.441,
 "train_seconds_per_epoch": 0.484,
 "train_seconds_total": 24.21,
 "val_seconds_per_epoch": 0.015,
 "val_seconds_total": 0.77,
 "val_share_of_wall": 0.0309
}
```
