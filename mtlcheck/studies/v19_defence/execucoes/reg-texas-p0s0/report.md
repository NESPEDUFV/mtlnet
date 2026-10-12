# reg-texas-p0s0

`3639e8a8504fa513` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **texas** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 216s |
| 1 | ? | ? | 210s |
| 2 | ? | ? | 209s |
| 3 | ? | ? | 210s |
| 4 | ? | ? | 210s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2, 3] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 2, 'top5': 1, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 1}), (3, {'top1': 0, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 1, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 49,
 "best_value": 0.6389665007591248,
 "clipped_fraction_mean": 0.1622,
 "clipped_fraction_per_epoch": [
  0.0527,
  0.6809,
  0.9969,
  1.0,
  1.0,
  1.0,
  0.9992,
  0.9931,
  0.8718,
  0.4214,
  0.0847,
  0.0053,
  0.0008,
  0.0008,
  0.0008,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0008,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
  "frames_ok": 3,
  "frames_total": 3,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 4,
 "epochs_to_99pct": 28,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.744538,
 "grad_norm_max_per_epoch": [
  1.695001,
  2.157894,
  2.364578,
  2.479295,
  2.744538,
  2.527835,
  2.545089,
  2.193934,
  1.657044,
  1.558814,
  1.379662,
  1.35812,
  1.240981,
  1.125972,
  1.017993,
  0.921998,
  0.889994,
  0.882875,
  0.984772,
  1.000123,
  0.998207,
  0.885558,
  0.854829,
  0.874518,
  0.921017,
  0.756775,
  0.841306,
  0.852834,
  0.80809,
  0.892401,
  0.885082,
  0.906407,
  0.839768,
  0.93012,
  0.83939,
  0.837896,
  0.9331,
  0.794696,
  0.85688,
  0.907254,
  0.86756,
  0.841779,
  0.976933,
  0.860067,
  0.822796,
  0.757324,
  0.846973,
  0.808226,
  0.855711,
  0.964978
 ],
 "grad_norm_mean": 0.640651,
 "grad_norm_per_epoch": [
  0.741777,
  1.067924,
  1.310612,
  1.456482,
  1.518126,
  1.495844,
  1.393318,
  1.270821,
  1.1236,
  0.984632,
  0.872219,
  0.788516,
  0.715919,
  0.662686,
  0.6167,
  0.579522,
  0.553541,
  0.531392,
  0.517132,
  0.500988,
  0.490957,
  0.482993,
  0.472057,
  0.471139,
  0.463029,
  0.460422,
  0.45685,
  0.453776,
  0.451735,
  0.447574,
  0.444368,
  0.444385,
  0.442768,
  0.439778,
  0.439372,
  0.439646,
  0.44071,
  0.439313,
  0.437187,
  0.436328,
  0.434911,
  0.433727,
  0.430427,
  0.430176,
  0.428563,
  0.425847,
  0.425822,
  0.423482,
  0.422077,
  0.421384
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
 "peak_memory_gb": 8.766,
 "tail_spread_pct_of_best": 0.037,
 "train_seconds_per_epoch": 4.004,
 "train_seconds_total": 200.21,
 "val_seconds_per_epoch": 0.31,
 "val_seconds_total": 15.48,
 "val_share_of_wall": 0.0718
}
```
