# cat-alabama-p7s7

`5037aaf2737f396a` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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
 "best_epoch": 18,
 "best_value": 0.3054664731025696,
 "clipped_fraction_mean": 0.06,
 "clipped_fraction_per_epoch": [
  1.0,
  0.3333,
  0.0,
  0.1111,
  0.0,
  0.1111,
  0.0,
  0.5556,
  0.1111,
  0.3333,
  0.3333,
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
 "epochs_to_99pct": 16,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.968739,
 "grad_norm_max_per_epoch": [
  5.968739,
  1.248882,
  0.773966,
  1.190551,
  0.777111,
  1.059028,
  0.971746,
  1.707892,
  1.37956,
  1.506908,
  1.257491,
  1.156385,
  0.97727,
  0.710233,
  0.61192,
  0.999147,
  0.862132,
  0.76354,
  0.787419,
  0.75619,
  0.555999,
  0.683279,
  0.978275,
  0.543835,
  0.456252,
  0.758646,
  0.584723,
  0.663917,
  0.556471,
  0.53398,
  0.584375,
  0.524573,
  0.806459,
  0.718547,
  0.614819,
  0.678708,
  0.770956,
  0.671628,
  0.704924,
  0.789968,
  0.965209,
  0.709596,
  0.893084,
  0.752956,
  0.779615,
  0.805487,
  0.724014,
  0.736637,
  0.718905,
  0.747466
 ],
 "grad_norm_mean": 0.570023,
 "grad_norm_per_epoch": [
  2.356441,
  0.927968,
  0.608163,
  0.705154,
  0.501981,
  0.684648,
  0.624603,
  1.058593,
  0.668308,
  1.019906,
  0.812539,
  0.64707,
  0.71553,
  0.525586,
  0.499131,
  0.595862,
  0.481053,
  0.531022,
  0.469672,
  0.430984,
  0.375134,
  0.424419,
  0.581328,
  0.389572,
  0.351004,
  0.496977,
  0.409232,
  0.452154,
  0.413881,
  0.425235,
  0.439383,
  0.419408,
  0.496757,
  0.555803,
  0.522387,
  0.463419,
  0.523004,
  0.510282,
  0.519783,
  0.49018,
  0.540005,
  0.47681,
  0.462757,
  0.446549,
  0.443275,
  0.423158,
  0.398878,
  0.399558,
  0.39595,
  0.390677
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
 "tail_spread_pct_of_best": 0.966,
 "train_seconds_per_epoch": 0.231,
 "train_seconds_total": 11.57,
 "val_seconds_per_epoch": 0.008,
 "val_seconds_total": 0.4,
 "val_share_of_wall": 0.033
}
```
