# reg-istanbul-p3s3

`777c78d8876bbc1c` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **3** · split_seed **3** · engine `check2hgi_v18`
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
| 3 | ? | ? | 11s |
| 4 | ? | ? | 12s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [1] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 0, 'top5': 1, 'top10': 0}), (1, {'top1': 0, 'top5': 1, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 45,
 "best_value": 0.7461164593696594,
 "clipped_fraction_mean": 0.1166,
 "clipped_fraction_per_epoch": [
  0.6882,
  0.0,
  0.0,
  0.129,
  0.5161,
  0.7204,
  0.7204,
  0.6989,
  0.6667,
  0.6237,
  0.4839,
  0.3118,
  0.1505,
  0.086,
  0.0215,
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
 "grad_norm_max": 2.56425,
 "grad_norm_max_per_epoch": [
  2.56425,
  0.880925,
  0.945036,
  1.491074,
  1.245277,
  1.537901,
  1.524382,
  1.378099,
  1.418553,
  1.38503,
  1.535362,
  1.223107,
  1.146128,
  1.117823,
  1.091197,
  1.027547,
  0.97132,
  0.895287,
  0.858483,
  0.848683,
  0.856925,
  0.824619,
  0.763733,
  0.766742,
  0.764666,
  0.722071,
  0.709146,
  0.670674,
  0.645818,
  0.701625,
  0.722171,
  0.681584,
  0.598718,
  0.635729,
  0.619027,
  0.600338,
  0.602636,
  0.635456,
  0.570866,
  0.60996,
  0.574542,
  0.577627,
  0.58875,
  0.5665,
  0.575706,
  0.598339,
  0.583218,
  0.559453,
  0.562012,
  0.578512
 ],
 "grad_norm_mean": 0.673664,
 "grad_norm_per_epoch": [
  1.269703,
  0.705723,
  0.707426,
  0.88078,
  1.000047,
  1.089245,
  1.073536,
  1.073073,
  1.073098,
  1.052785,
  1.022542,
  0.952346,
  0.8845,
  0.860597,
  0.78661,
  0.744626,
  0.733566,
  0.70931,
  0.665634,
  0.651422,
  0.63775,
  0.609246,
  0.611603,
  0.578153,
  0.577816,
  0.561739,
  0.565436,
  0.552069,
  0.531209,
  0.548448,
  0.544455,
  0.517616,
  0.521403,
  0.520117,
  0.525279,
  0.508652,
  0.502511,
  0.509917,
  0.491952,
  0.506791,
  0.507391,
  0.485427,
  0.492029,
  0.486894,
  0.480539,
  0.473919,
  0.472638,
  0.473427,
  0.472532,
  0.479679
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
 "peak_memory_gb": 0.874,
 "tail_spread_pct_of_best": 0.054,
 "train_seconds_per_epoch": 0.209,
 "train_seconds_total": 10.45,
 "val_seconds_per_epoch": 0.011,
 "val_seconds_total": 0.55,
 "val_share_of_wall": 0.0502
}
```
