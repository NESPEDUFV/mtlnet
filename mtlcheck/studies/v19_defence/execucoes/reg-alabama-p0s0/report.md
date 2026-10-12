# reg-alabama-p0s0

`9a2fd6af5c546ca8` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 5s |
| 1 | ? | ? | 4s |
| 2 | ? | ? | 4s |
| 3 | ? | ? | 4s |
| 4 | ? | ? | 4s |

## Worth a look

- ties at the decision boundary: [(3, {'top1': 1, 'top5': 0, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 36,
 "best_value": 0.7396284937858582,
 "clipped_fraction_mean": 0.117,
 "clipped_fraction_per_epoch": [
  0.5758,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0303,
  0.2121,
  0.4545,
  0.3333,
  0.3939,
  0.6364,
  0.5152,
  0.6667,
  0.3636,
  0.3333,
  0.4848,
  0.2727,
  0.2121,
  0.0909,
  0.1515,
  0.0,
  0.0606,
  0.0303,
  0.0303,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 27,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.570402,
 "grad_norm_max_per_epoch": [
  1.570402,
  0.890468,
  0.811604,
  0.717456,
  0.80463,
  1.024822,
  1.243597,
  1.345174,
  1.227058,
  1.200278,
  1.481207,
  1.464621,
  1.317677,
  1.169152,
  1.19047,
  1.396436,
  1.16985,
  1.207144,
  1.070933,
  1.222774,
  0.996888,
  1.051869,
  1.039579,
  1.02787,
  0.908657,
  0.937859,
  0.903035,
  0.943284,
  0.895451,
  0.972054,
  0.890391,
  0.846156,
  0.83671,
  0.924345,
  0.78995,
  0.855265,
  0.83954,
  0.845457,
  0.815348,
  0.778698,
  0.784952,
  0.836005,
  0.855921,
  0.799412,
  0.751674,
  0.804297,
  0.802295,
  0.730373,
  0.728509,
  0.746119
 ],
 "grad_norm_mean": 0.806996,
 "grad_norm_per_epoch": [
  1.108945,
  0.840042,
  0.72142,
  0.635655,
  0.662653,
  0.786945,
  0.898792,
  0.98061,
  0.957701,
  0.972797,
  1.093939,
  1.038399,
  1.04031,
  0.967327,
  0.96432,
  1.000079,
  0.92906,
  0.915546,
  0.899243,
  0.898767,
  0.813848,
  0.842132,
  0.839064,
  0.807676,
  0.775373,
  0.810405,
  0.782643,
  0.77093,
  0.771917,
  0.760385,
  0.766633,
  0.757367,
  0.740023,
  0.763934,
  0.710328,
  0.73488,
  0.726614,
  0.733608,
  0.691357,
  0.70193,
  0.706026,
  0.690569,
  0.688153,
  0.673393,
  0.666352,
  0.671818,
  0.666618,
  0.665394,
  0.649814,
  0.658042
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
 "peak_memory_gb": 0.505,
 "tail_spread_pct_of_best": 0.307,
 "train_seconds_per_epoch": 0.088,
 "train_seconds_total": 4.4,
 "val_seconds_per_epoch": 0.01,
 "val_seconds_total": 0.51,
 "val_share_of_wall": 0.1038
}
```
