# reg-california-p100s100

`191ec467e8f6c89b` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **california** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 175s |
| 1 | ? | ? | 175s |
| 2 | ? | ? | 174s |
| 3 | ? | ? | 174s |
| 4 | ? | ? | 175s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2, 4] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 0}), (3, {'top1': 1, 'top5': 2, 'top10': 1}), (4, {'top1': 0, 'top5': 1, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 49,
 "best_value": 0.6274260878562927,
 "clipped_fraction_mean": 0.1562,
 "clipped_fraction_per_epoch": [
  0.012,
  0.08,
  0.859,
  0.999,
  1.0,
  1.0,
  1.0,
  0.998,
  0.96,
  0.67,
  0.206,
  0.026,
  0.002,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_99pct": 30,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.97913,
 "grad_norm_max_per_epoch": [
  1.258672,
  1.234082,
  1.523415,
  1.659673,
  1.97913,
  1.832663,
  1.771956,
  1.679027,
  1.612942,
  1.392387,
  1.234989,
  1.157193,
  1.077001,
  0.956682,
  0.856032,
  0.811019,
  0.80983,
  0.749284,
  0.727617,
  0.707342,
  0.673248,
  0.678929,
  0.663826,
  0.626604,
  0.632471,
  0.637797,
  0.605281,
  0.617152,
  0.655563,
  0.588487,
  0.600793,
  0.597119,
  0.59047,
  0.578354,
  0.584397,
  0.606416,
  0.589128,
  0.581577,
  0.581086,
  0.572596,
  0.563014,
  0.547336,
  0.554991,
  0.550063,
  0.557705,
  0.546541,
  0.536669,
  0.54107,
  0.54593,
  0.561523
 ],
 "grad_norm_mean": 0.654028,
 "grad_norm_per_epoch": [
  0.61406,
  0.850053,
  1.120377,
  1.287791,
  1.39403,
  1.417221,
  1.381183,
  1.283343,
  1.167949,
  1.046426,
  0.930415,
  0.84525,
  0.774322,
  0.71504,
  0.671888,
  0.63323,
  0.604426,
  0.576285,
  0.559875,
  0.547236,
  0.532672,
  0.526956,
  0.517435,
  0.50698,
  0.501446,
  0.497008,
  0.494036,
  0.488864,
  0.488474,
  0.481588,
  0.480064,
  0.476134,
  0.476549,
  0.474158,
  0.471205,
  0.469815,
  0.465222,
  0.465311,
  0.464046,
  0.463737,
  0.460574,
  0.459302,
  0.457742,
  0.456033,
  0.454274,
  0.451861,
  0.451773,
  0.450184,
  0.450239,
  0.44731
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015147
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
 "peak_memory_gb": 6.868,
 "tail_spread_pct_of_best": 0.046,
 "train_seconds_per_epoch": 3.193,
 "train_seconds_total": 159.64,
 "val_seconds_per_epoch": 0.287,
 "val_seconds_total": 14.36,
 "val_share_of_wall": 0.0825
}
```
