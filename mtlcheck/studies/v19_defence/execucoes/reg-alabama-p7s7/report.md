# reg-alabama-p7s7

`c387ce1476103d3b` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 4s |
| 1 | ? | ? | 4s |
| 2 | ? | ? | 4s |
| 3 | ? | ? | 4s |
| 4 | ? | ? | 4s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 39,
 "best_value": 0.7319034934043884,
 "clipped_fraction_mean": 0.1067,
 "clipped_fraction_per_epoch": [
  0.5455,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0303,
  0.1515,
  0.3636,
  0.4848,
  0.3939,
  0.4848,
  0.5455,
  0.6667,
  0.4545,
  0.303,
  0.2121,
  0.2727,
  0.2727,
  0.0606,
  0.0303,
  0.0303,
  0.0303,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 31,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.683486,
 "grad_norm_max_per_epoch": [
  1.683486,
  0.913449,
  0.769284,
  0.750787,
  0.712478,
  1.069984,
  1.13787,
  1.27821,
  1.223144,
  1.310543,
  1.163564,
  1.314918,
  1.241977,
  1.228033,
  1.331388,
  1.238157,
  1.103189,
  1.282729,
  1.094422,
  1.07718,
  1.049747,
  1.022883,
  0.876357,
  0.980251,
  0.974664,
  0.850508,
  0.914267,
  0.976279,
  0.863499,
  0.857202,
  0.796595,
  0.826366,
  0.837141,
  0.835117,
  0.812832,
  0.768671,
  0.868152,
  0.772585,
  0.862107,
  0.799925,
  0.763566,
  0.77965,
  0.793182,
  0.779824,
  0.74219,
  0.746714,
  0.770988,
  0.775513,
  0.714562,
  0.719319
 ],
 "grad_norm_mean": 0.792142,
 "grad_norm_per_epoch": [
  1.127057,
  0.822297,
  0.700209,
  0.63995,
  0.630633,
  0.732977,
  0.87204,
  0.979445,
  0.996642,
  0.995367,
  1.001052,
  1.004224,
  1.031358,
  0.994802,
  0.950319,
  0.921869,
  0.932834,
  0.920463,
  0.896784,
  0.860053,
  0.832198,
  0.827315,
  0.793562,
  0.806735,
  0.798237,
  0.745527,
  0.775028,
  0.762633,
  0.738136,
  0.74371,
  0.714749,
  0.736168,
  0.720764,
  0.744535,
  0.712988,
  0.694898,
  0.712452,
  0.685449,
  0.70758,
  0.702129,
  0.680431,
  0.675524,
  0.677782,
  0.668601,
  0.667914,
  0.658204,
  0.658822,
  0.655227,
  0.649559,
  0.649882
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015159
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.00299999
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
 "peak_memory_gb": 0.506,
 "tail_spread_pct_of_best": 0.042,
 "train_seconds_per_epoch": 0.076,
 "train_seconds_total": 3.82,
 "val_seconds_per_epoch": 0.005,
 "val_seconds_total": 0.24,
 "val_share_of_wall": 0.0601
}
```
