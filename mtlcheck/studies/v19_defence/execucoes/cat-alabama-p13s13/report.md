# cat-alabama-p13s13

`f2f3c7ae19c297c4` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **13** · split_seed **13** · engine `check2hgi_v18`
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
 "best_epoch": 19,
 "best_value": 0.30077022314071655,
 "clipped_fraction_mean": 0.0844,
 "clipped_fraction_per_epoch": [
  1.0,
  0.7778,
  0.3333,
  0.0,
  0.0,
  0.2222,
  0.0,
  0.3333,
  0.1111,
  0.4444,
  0.2222,
  0.0,
  0.1111,
  0.5556,
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
  0.0
 ],
 "compile_counters": {
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 4,
 "epochs_to_99pct": 11,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 8.233139,
 "grad_norm_max_per_epoch": [
  8.233139,
  1.653462,
  1.321063,
  0.833195,
  0.772571,
  1.069977,
  0.787268,
  1.407377,
  1.288073,
  1.411784,
  1.405879,
  0.87093,
  1.316549,
  1.758814,
  1.240267,
  0.839155,
  0.502824,
  0.940813,
  0.812655,
  0.515766,
  0.65073,
  0.762711,
  0.535239,
  0.555437,
  0.664908,
  0.598227,
  0.579522,
  0.50326,
  0.778766,
  0.602023,
  0.50795,
  0.614738,
  0.568053,
  0.604706,
  0.617362,
  0.658484,
  0.729984,
  0.721987,
  0.648862,
  0.764451,
  0.637748,
  0.686684,
  0.761439,
  0.730972,
  0.814988,
  0.738177,
  0.70842,
  0.690427,
  0.69754,
  0.684204
 ],
 "grad_norm_mean": 0.595784,
 "grad_norm_per_epoch": [
  3.090053,
  1.12649,
  0.880125,
  0.671377,
  0.56541,
  0.621421,
  0.585835,
  0.811371,
  0.60624,
  0.879691,
  0.861361,
  0.65307,
  0.623675,
  1.105742,
  0.550469,
  0.524706,
  0.401947,
  0.700369,
  0.592548,
  0.38314,
  0.415883,
  0.461448,
  0.391588,
  0.394552,
  0.40762,
  0.439795,
  0.472194,
  0.41941,
  0.517342,
  0.424617,
  0.40009,
  0.456477,
  0.405227,
  0.427766,
  0.438307,
  0.508544,
  0.495857,
  0.492591,
  0.50186,
  0.476789,
  0.498169,
  0.502562,
  0.551602,
  0.509312,
  0.520339,
  0.45677,
  0.415002,
  0.385243,
  0.385066,
  0.382142
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
 "tail_spread_pct_of_best": 0.673,
 "train_seconds_per_epoch": 0.232,
 "train_seconds_total": 11.61,
 "val_seconds_per_epoch": 0.008,
 "val_seconds_total": 0.39,
 "val_share_of_wall": 0.0329
}
```
