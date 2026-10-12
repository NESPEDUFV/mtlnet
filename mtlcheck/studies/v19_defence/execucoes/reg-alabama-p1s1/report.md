# reg-alabama-p1s1

`80030709a0b9609d` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
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
 "best_epoch": 32,
 "best_value": 0.7362773418426514,
 "clipped_fraction_mean": 0.1115,
 "clipped_fraction_per_epoch": [
  0.5455,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0909,
  0.1212,
  0.1515,
  0.4545,
  0.5758,
  0.4242,
  0.7879,
  0.4848,
  0.5455,
  0.4848,
  0.1818,
  0.1818,
  0.1212,
  0.1212,
  0.0606,
  0.0303,
  0.0606,
  0.1515,
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
 "epochs_to_99pct": 21,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.471079,
 "grad_norm_max_per_epoch": [
  1.471079,
  0.909798,
  0.783292,
  0.697315,
  0.724818,
  1.116194,
  1.158998,
  1.081208,
  1.298074,
  1.154504,
  1.250428,
  1.462166,
  1.379664,
  1.393287,
  1.417463,
  1.096683,
  1.105509,
  1.081264,
  1.058527,
  1.020406,
  1.129481,
  1.092858,
  1.046063,
  0.991434,
  0.894571,
  0.955188,
  0.875371,
  0.932004,
  0.869022,
  0.864245,
  0.875213,
  0.868374,
  0.833731,
  0.845178,
  0.828371,
  0.789234,
  0.841514,
  0.785566,
  0.802028,
  0.827969,
  0.79379,
  0.756912,
  0.842588,
  0.749324,
  0.747887,
  0.743331,
  0.720753,
  0.717436,
  0.704258,
  0.762657
 ],
 "grad_norm_mean": 0.797479,
 "grad_norm_per_epoch": [
  1.07859,
  0.842567,
  0.723918,
  0.635876,
  0.635472,
  0.823206,
  0.880631,
  0.867188,
  0.989461,
  1.003545,
  0.989543,
  1.083668,
  1.012067,
  1.035449,
  0.99289,
  0.919221,
  0.895486,
  0.909871,
  0.896316,
  0.860026,
  0.837049,
  0.850575,
  0.85616,
  0.831493,
  0.773484,
  0.788382,
  0.745531,
  0.749736,
  0.75433,
  0.740674,
  0.737245,
  0.737828,
  0.727387,
  0.735922,
  0.726349,
  0.689157,
  0.706156,
  0.69943,
  0.69983,
  0.701233,
  0.702392,
  0.68656,
  0.684046,
  0.672563,
  0.667452,
  0.671041,
  0.666068,
  0.655832,
  0.646507,
  0.65854
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
 "peak_memory_gb": 0.504,
 "tail_spread_pct_of_best": 0.098,
 "train_seconds_per_epoch": 0.076,
 "train_seconds_total": 3.81,
 "val_seconds_per_epoch": 0.005,
 "val_seconds_total": 0.25,
 "val_share_of_wall": 0.0606
}
```
