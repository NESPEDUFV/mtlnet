# reg-florida-p100s100

`6c5acd37b474b87a` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **florida** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 64s |
| 1 | ? | ? | 64s |
| 2 | ? | ? | 64s |
| 3 | ? | ? | 64s |
| 4 | ? | ? | 64s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [0, 4] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(1, {'top1': 0, 'top5': 1, 'top10': 1}), (3, {'top1': 1, 'top5': 1, 'top10': 0}), (4, {'top1': 0, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 50,
 "best_value": 0.7692047953605652,
 "clipped_fraction_mean": 0.0745,
 "clipped_fraction_per_epoch": [
  0.4679,
  0.0,
  0.0138,
  0.1445,
  0.4885,
  0.7202,
  0.6835,
  0.6399,
  0.3876,
  0.1445,
  0.0298,
  0.0069,
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
 "epochs_to_95pct": 5,
 "epochs_to_99pct": 23,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.520774,
 "grad_norm_max_per_epoch": [
  4.520774,
  0.834202,
  1.116035,
  1.24457,
  1.303472,
  1.411659,
  1.300445,
  1.329525,
  1.358937,
  1.273777,
  1.191241,
  1.040851,
  0.913062,
  0.881402,
  0.824696,
  0.782287,
  0.728618,
  0.761975,
  0.702582,
  0.644117,
  0.675675,
  0.606319,
  0.656598,
  0.599365,
  0.642379,
  0.563172,
  0.558876,
  0.543193,
  0.532964,
  0.559214,
  0.514151,
  0.508623,
  0.530799,
  0.517618,
  0.505443,
  0.505573,
  0.492822,
  0.514314,
  0.492722,
  0.519492,
  0.540504,
  0.51744,
  0.489213,
  0.487869,
  0.487564,
  0.527729,
  0.483364,
  0.476364,
  0.495449,
  0.517477
 ],
 "grad_norm_mean": 0.573894,
 "grad_norm_per_epoch": [
  1.208065,
  0.641487,
  0.793682,
  0.91149,
  1.004402,
  1.063233,
  1.04566,
  1.034786,
  0.986332,
  0.919363,
  0.859481,
  0.793288,
  0.740175,
  0.684428,
  0.644532,
  0.619738,
  0.58313,
  0.55863,
  0.537621,
  0.521995,
  0.503499,
  0.48913,
  0.47699,
  0.466432,
  0.458192,
  0.44942,
  0.444094,
  0.433293,
  0.428212,
  0.425117,
  0.420148,
  0.416398,
  0.415741,
  0.409915,
  0.409442,
  0.409832,
  0.400171,
  0.401551,
  0.397291,
  0.397747,
  0.394866,
  0.393374,
  0.393069,
  0.391562,
  0.388416,
  0.386692,
  0.387028,
  0.38569,
  0.384763,
  0.38509
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015148
  ],
  "last": [
   1e-08
  ],
  "max_observed": [
   0.003
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
 "peak_memory_gb": 3.168,
 "tail_spread_pct_of_best": 0.035,
 "train_seconds_per_epoch": 1.19,
 "train_seconds_total": 59.52,
 "val_seconds_per_epoch": 0.075,
 "val_seconds_total": 3.74,
 "val_share_of_wall": 0.0592
}
```
