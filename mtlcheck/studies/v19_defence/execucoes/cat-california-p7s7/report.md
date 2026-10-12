# cat-california-p7s7

`dd9009547c62c9ae` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **california** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 366s |
| 1 | ? | ? | 365s |
| 2 | ? | ? | 365s |
| 3 | ? | ? | 365s |
| 4 | ? | ? | 365s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2] — the schedule is probably mis-sized (50 epochs)

## Diagnostics

```json
{
 "best_epoch": 8,
 "best_value": 0.3579864799976349,
 "clipped_fraction_mean": 0.0006,
 "clipped_fraction_per_epoch": [
  0.028,
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
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 7,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.800356,
 "grad_norm_max_per_epoch": [
  5.800356,
  0.732002,
  0.760234,
  0.655611,
  0.618958,
  0.447098,
  0.65653,
  0.575114,
  0.519374,
  0.385927,
  0.234667,
  0.210045,
  0.13419,
  0.114289,
  0.105113,
  0.093835,
  0.086505,
  0.086146,
  0.087028,
  0.077603,
  0.076862,
  0.078793,
  0.080042,
  0.07869,
  0.084287,
  0.085847,
  0.079484,
  0.088786,
  0.080491,
  0.084306,
  0.082262,
  0.083319,
  0.08229,
  0.08538,
  0.079615,
  0.080173,
  0.081004,
  0.081459,
  0.079767,
  0.083843,
  0.077844,
  0.08037,
  0.077387,
  0.079113,
  0.07758,
  0.076811,
  0.077795,
  0.078745,
  0.080549,
  0.076573
 ],
 "grad_norm_mean": 0.116254,
 "grad_norm_per_epoch": [
  0.471925,
  0.355564,
  0.338337,
  0.33444,
  0.286424,
  0.268428,
  0.272791,
  0.243379,
  0.207161,
  0.159806,
  0.132712,
  0.105985,
  0.08955,
  0.078008,
  0.07178,
  0.068651,
  0.066167,
  0.065164,
  0.06469,
  0.06373,
  0.064466,
  0.065628,
  0.06437,
  0.066854,
  0.067417,
  0.066706,
  0.06665,
  0.069484,
  0.067658,
  0.069976,
  0.069486,
  0.069987,
  0.070798,
  0.071173,
  0.070036,
  0.069398,
  0.069179,
  0.070083,
  0.069684,
  0.06906,
  0.06985,
  0.070029,
  0.070049,
  0.069904,
  0.069987,
  0.070141,
  0.070034,
  0.070001,
  0.070053,
  0.06989
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025247
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.005
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
 "peak_memory_gb": 9.148,
 "tail_spread_pct_of_best": 0.08,
 "train_seconds_per_epoch": 7.045,
 "train_seconds_total": 352.27,
 "val_seconds_per_epoch": 0.26,
 "val_seconds_total": 12.99,
 "val_share_of_wall": 0.0356
}
```
