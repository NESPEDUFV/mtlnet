# cat-istanbul-p3s3

`fdef0abb7bc568a4` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **3** · split_seed **3** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 34s |
| 1 | ? | ? | 34s |
| 2 | ? | ? | 34s |
| 3 | ? | ? | 34s |
| 4 | ? | ? | 34s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 43,
 "best_value": 0.3404060900211334,
 "clipped_fraction_mean": 0.0408,
 "clipped_fraction_per_epoch": [
  1.0,
  0.125,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.0417,
  0.0,
  0.0,
  0.0417,
  0.0833,
  0.0,
  0.125,
  0.125,
  0.375,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.0,
  0.0417,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 24,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 6.58233,
 "grad_norm_max_per_epoch": [
  6.58233,
  1.20525,
  0.679454,
  0.577149,
  0.925166,
  1.055444,
  1.097072,
  0.946379,
  0.990144,
  1.080042,
  1.203667,
  0.94861,
  1.133138,
  1.451923,
  1.372983,
  0.825642,
  0.768058,
  0.706922,
  1.003718,
  0.796677,
  1.128616,
  0.627076,
  0.857507,
  0.873389,
  0.64076,
  0.581418,
  0.629261,
  0.820488,
  0.881468,
  0.669207,
  0.743042,
  0.558012,
  0.620881,
  0.551387,
  0.574081,
  0.460037,
  0.664998,
  0.627144,
  0.505245,
  0.549455,
  0.499222,
  0.622494,
  0.752168,
  0.542791,
  0.564915,
  0.557109,
  0.456412,
  0.503348,
  0.447134,
  0.491607
 ],
 "grad_norm_mean": 0.495097,
 "grad_norm_per_epoch": [
  2.512033,
  0.819419,
  0.522593,
  0.395793,
  0.554339,
  0.594096,
  0.607723,
  0.677844,
  0.699977,
  0.720441,
  0.6107,
  0.619433,
  0.608585,
  0.653723,
  0.865364,
  0.518006,
  0.507033,
  0.508771,
  0.506909,
  0.504567,
  0.478265,
  0.393952,
  0.516956,
  0.545662,
  0.43122,
  0.385549,
  0.365845,
  0.384851,
  0.38759,
  0.379772,
  0.397294,
  0.402216,
  0.440569,
  0.396379,
  0.3921,
  0.301384,
  0.361901,
  0.277704,
  0.318879,
  0.292767,
  0.33876,
  0.359105,
  0.319985,
  0.288597,
  0.284736,
  0.272174,
  0.278753,
  0.267342,
  0.247991,
  0.239216
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   2.527e-05
  ],
  "last": [
   0.0
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
 "peak_memory_gb": 3.419,
 "tail_spread_pct_of_best": 0.079,
 "train_seconds_per_epoch": 0.653,
 "train_seconds_total": 32.65,
 "val_seconds_per_epoch": 0.021,
 "val_seconds_total": 1.04,
 "val_share_of_wall": 0.0309
}
```
