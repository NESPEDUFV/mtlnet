# cat-california-p100s100

`3f64f40996b69a3e` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **california** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 367s |
| 1 | ? | ? | 367s |
| 2 | ? | ? | 367s |
| 3 | ? | ? | 367s |
| 4 | ? | ? | 367s |

## Worth a look

- ties at the decision boundary: [(1, {'top3': 1, 'top5': 0}), (2, {'top3': 0, 'top5': 1})]

## Diagnostics

```json
{
 "best_epoch": 47,
 "best_value": 0.35927632451057434,
 "clipped_fraction_mean": 0.0005,
 "clipped_fraction_per_epoch": [
  0.024,
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
 "epochs_to_99pct": 6,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.172354,
 "grad_norm_max_per_epoch": [
  5.172354,
  0.667225,
  0.727508,
  0.651272,
  0.543634,
  0.464779,
  0.494197,
  0.439991,
  0.385429,
  0.304092,
  0.312875,
  0.186191,
  0.142901,
  0.123903,
  0.097181,
  0.095127,
  0.08128,
  0.084472,
  0.093674,
  0.087867,
  0.082811,
  0.080357,
  0.082404,
  0.078763,
  0.076871,
  0.085062,
  0.082239,
  0.081935,
  0.080557,
  0.082171,
  0.085186,
  0.079874,
  0.081533,
  0.085015,
  0.086208,
  0.080811,
  0.080243,
  0.079139,
  0.079602,
  0.080868,
  0.079134,
  0.074193,
  0.078133,
  0.076467,
  0.231158,
  0.074834,
  0.075644,
  0.077216,
  0.075076,
  0.077465
 ],
 "grad_norm_mean": 0.114303,
 "grad_norm_per_epoch": [
  0.450451,
  0.351676,
  0.330092,
  0.332199,
  0.292721,
  0.275168,
  0.25511,
  0.234538,
  0.198166,
  0.159009,
  0.129813,
  0.105378,
  0.086352,
  0.077511,
  0.071116,
  0.068916,
  0.064638,
  0.064077,
  0.064714,
  0.065398,
  0.066176,
  0.064802,
  0.066457,
  0.067109,
  0.066597,
  0.0663,
  0.067489,
  0.068435,
  0.068655,
  0.068551,
  0.070492,
  0.069813,
  0.070102,
  0.069698,
  0.068389,
  0.068731,
  0.068144,
  0.067775,
  0.067224,
  0.06752,
  0.067698,
  0.067519,
  0.067852,
  0.067707,
  0.068752,
  0.067833,
  0.067981,
  0.067866,
  0.068342,
  0.068099
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
 "tail_spread_pct_of_best": 0.098,
 "train_seconds_per_epoch": 7.071,
 "train_seconds_total": 353.57,
 "val_seconds_per_epoch": 0.26,
 "val_seconds_total": 12.99,
 "val_share_of_wall": 0.0354
}
```
