# reg-florida-p7s7

`374a72eb9b877409` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **florida** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 63s |
| 1 | ? | ? | 63s |
| 2 | ? | ? | 63s |
| 3 | ? | ? | 63s |
| 4 | ? | ? | 63s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [4] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 0}), (2, {'top1': 1, 'top5': 1, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 48,
 "best_value": 0.7699345350265503,
 "clipped_fraction_mean": 0.0656,
 "clipped_fraction_per_epoch": [
  0.4817,
  0.0,
  0.0138,
  0.1101,
  0.3647,
  0.6353,
  0.6307,
  0.5596,
  0.3303,
  0.1284,
  0.0206,
  0.0046,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_99pct": 21,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.503732,
 "grad_norm_max_per_epoch": [
  4.503732,
  0.861375,
  1.104686,
  1.194186,
  1.354015,
  1.437613,
  1.355719,
  1.365295,
  1.261408,
  1.160871,
  1.087871,
  1.01236,
  0.943939,
  0.922555,
  0.879767,
  0.82268,
  0.790659,
  0.694678,
  0.683857,
  0.648863,
  0.626283,
  0.632198,
  0.67115,
  0.600224,
  0.554058,
  0.569023,
  0.566655,
  0.529922,
  0.552462,
  0.517515,
  0.512947,
  0.548299,
  0.503595,
  0.508328,
  0.52627,
  0.496939,
  0.499743,
  0.53103,
  0.517284,
  0.495941,
  0.469222,
  0.5123,
  0.512898,
  0.532439,
  0.522616,
  0.504755,
  0.492988,
  0.460331,
  0.483149,
  0.485788
 ],
 "grad_norm_mean": 0.57025,
 "grad_norm_per_epoch": [
  1.226961,
  0.64526,
  0.785239,
  0.89746,
  0.979219,
  1.037606,
  1.036158,
  1.019077,
  0.964351,
  0.910349,
  0.838723,
  0.789531,
  0.729273,
  0.68087,
  0.640402,
  0.616001,
  0.58064,
  0.553499,
  0.532246,
  0.515567,
  0.501696,
  0.48724,
  0.476913,
  0.460267,
  0.45439,
  0.446989,
  0.442103,
  0.433277,
  0.430912,
  0.42408,
  0.418569,
  0.417011,
  0.412933,
  0.408278,
  0.410811,
  0.405005,
  0.404388,
  0.401603,
  0.398206,
  0.395524,
  0.396829,
  0.396384,
  0.395756,
  0.391656,
  0.391457,
  0.387777,
  0.386818,
  0.386384,
  0.385728,
  0.385106
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
 "peak_memory_gb": 3.167,
 "tail_spread_pct_of_best": 0.034,
 "train_seconds_per_epoch": 1.185,
 "train_seconds_total": 59.23,
 "val_seconds_per_epoch": 0.074,
 "val_seconds_total": 3.7,
 "val_share_of_wall": 0.0588
}
```
