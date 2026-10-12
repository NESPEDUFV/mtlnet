# reg-california-p1s1

`4b7c9eb6b9fc09ab` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **california** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
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
| 1 | ? | ? | 174s |
| 2 | ? | ? | 175s |
| 3 | ? | ? | 175s |
| 4 | ? | ? | 175s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 1}), (3, {'top1': 1, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 1, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 49,
 "best_value": 0.622462809085846,
 "clipped_fraction_mean": 0.1569,
 "clipped_fraction_per_epoch": [
  0.013,
  0.111,
  0.856,
  0.998,
  1.0,
  1.0,
  1.0,
  0.998,
  0.957,
  0.663,
  0.216,
  0.03,
  0.003,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_99pct": 29,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.906327,
 "grad_norm_max_per_epoch": [
  1.308348,
  1.241222,
  1.508681,
  1.768564,
  1.782746,
  1.835255,
  1.906327,
  1.662626,
  1.568114,
  1.353884,
  1.336708,
  1.138541,
  1.028916,
  0.932195,
  0.870756,
  0.85733,
  0.804529,
  0.824555,
  0.716387,
  0.726409,
  0.679531,
  0.666857,
  0.724037,
  0.668935,
  0.65311,
  0.613803,
  0.632389,
  0.612438,
  0.614848,
  0.639671,
  0.606,
  0.596349,
  0.613838,
  0.587784,
  0.596709,
  0.572825,
  0.609936,
  0.573537,
  0.589339,
  0.562241,
  0.551503,
  0.564023,
  0.54956,
  0.590452,
  0.543506,
  0.553145,
  0.548256,
  0.537651,
  0.548292,
  0.551015
 ],
 "grad_norm_mean": 0.654616,
 "grad_norm_per_epoch": [
  0.616448,
  0.85248,
  1.10934,
  1.283767,
  1.381137,
  1.406505,
  1.364497,
  1.269947,
  1.163252,
  1.04679,
  0.936357,
  0.851622,
  0.771929,
  0.721568,
  0.67119,
  0.63485,
  0.607289,
  0.581013,
  0.562629,
  0.553178,
  0.535619,
  0.525783,
  0.520738,
  0.513472,
  0.503848,
  0.501107,
  0.49331,
  0.490815,
  0.487559,
  0.483528,
  0.480943,
  0.479901,
  0.477799,
  0.476908,
  0.4751,
  0.469627,
  0.467805,
  0.46692,
  0.466214,
  0.466297,
  0.463724,
  0.462679,
  0.46054,
  0.46009,
  0.456074,
  0.453018,
  0.454403,
  0.45158,
  0.450328,
  0.449274
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
 "tail_spread_pct_of_best": 0.026,
 "train_seconds_per_epoch": 3.193,
 "train_seconds_total": 159.66,
 "val_seconds_per_epoch": 0.287,
 "val_seconds_total": 14.36,
 "val_share_of_wall": 0.0825
}
```
