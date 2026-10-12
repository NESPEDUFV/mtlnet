# reg-istanbul-p13s13

`34cb92e99ff3b97e` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **13** · split_seed **13** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 11s |
| 1 | ? | ? | 11s |
| 2 | ? | ? | 11s |
| 3 | ? | ? | 12s |
| 4 | ? | ? | 12s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2, 3] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 0}), (2, {'top1': 1, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 44,
 "best_value": 0.7438804507255554,
 "clipped_fraction_mean": 0.0892,
 "clipped_fraction_per_epoch": [
  0.8172,
  0.0,
  0.0,
  0.1613,
  0.3333,
  0.4409,
  0.5161,
  0.5054,
  0.6237,
  0.3871,
  0.2473,
  0.2903,
  0.0753,
  0.043,
  0.0108,
  0.0108,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_95pct": 6,
 "epochs_to_99pct": 24,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.942268,
 "grad_norm_max_per_epoch": [
  1.942268,
  0.892308,
  0.948826,
  1.254505,
  1.298256,
  1.375029,
  1.432204,
  1.416192,
  1.398397,
  1.276804,
  1.296109,
  1.313731,
  1.129753,
  1.11517,
  1.037921,
  1.001305,
  0.902431,
  0.924794,
  0.94265,
  0.786563,
  0.766794,
  0.813474,
  0.775641,
  0.742482,
  0.765493,
  0.72863,
  0.715933,
  0.751814,
  0.659321,
  0.639074,
  0.688481,
  0.626612,
  0.63685,
  0.597287,
  0.599817,
  0.672597,
  0.585775,
  0.584396,
  0.555647,
  0.587669,
  0.574545,
  0.577308,
  0.571752,
  0.561696,
  0.560884,
  0.57613,
  0.570472,
  0.587101,
  0.554768,
  0.551431
 ],
 "grad_norm_mean": 0.653148,
 "grad_norm_per_epoch": [
  1.242413,
  0.71019,
  0.671853,
  0.862177,
  0.946625,
  0.988611,
  1.01193,
  1.021988,
  1.043282,
  0.975397,
  0.936006,
  0.937471,
  0.844949,
  0.804623,
  0.770532,
  0.738188,
  0.705822,
  0.686286,
  0.655678,
  0.630931,
  0.618788,
  0.608693,
  0.584148,
  0.572713,
  0.576099,
  0.560636,
  0.555454,
  0.539517,
  0.534389,
  0.522684,
  0.507655,
  0.516647,
  0.511624,
  0.510349,
  0.515682,
  0.507982,
  0.498843,
  0.49478,
  0.496174,
  0.486452,
  0.491374,
  0.486469,
  0.481344,
  0.472306,
  0.483506,
  0.468199,
  0.473423,
  0.464986,
  0.462896,
  0.468648
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015151
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
 "peak_memory_gb": 0.875,
 "tail_spread_pct_of_best": 0.049,
 "train_seconds_per_epoch": 0.21,
 "train_seconds_total": 10.51,
 "val_seconds_per_epoch": 0.011,
 "val_seconds_total": 0.55,
 "val_share_of_wall": 0.0499
}
```
