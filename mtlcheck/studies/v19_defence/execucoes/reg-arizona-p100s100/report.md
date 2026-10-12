# reg-arizona-p100s100

`06f40192e4918bf6` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **arizona** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 9s |
| 1 | ? | ? | 9s |
| 2 | ? | ? | 9s |
| 3 | ? | ? | 9s |
| 4 | ? | ? | 9s |

## Worth a look

- ties at the decision boundary: [(4, {'top1': 0, 'top5': 1, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 39,
 "best_value": 0.6573419570922852,
 "clipped_fraction_mean": 0.0554,
 "clipped_fraction_per_epoch": [
  0.2319,
  0.0,
  0.0,
  0.0,
  0.0145,
  0.1304,
  0.1884,
  0.3768,
  0.3478,
  0.3768,
  0.3478,
  0.4203,
  0.1449,
  0.0725,
  0.0725,
  0.029,
  0.0145,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "grad_norm_max": 1.467879,
 "grad_norm_max_per_epoch": [
  1.467879,
  0.754926,
  0.657551,
  0.936993,
  1.06829,
  1.18442,
  1.242294,
  1.208025,
  1.208616,
  1.273445,
  1.286025,
  1.154436,
  1.194355,
  1.222474,
  1.03667,
  1.045542,
  1.064008,
  0.911983,
  0.947602,
  0.858045,
  0.863899,
  0.951486,
  0.894499,
  0.817848,
  0.853166,
  0.81228,
  0.815351,
  0.788292,
  0.759593,
  0.78706,
  0.75225,
  0.745179,
  0.77913,
  0.721374,
  0.757475,
  0.769336,
  0.756383,
  0.703307,
  0.806885,
  0.708335,
  0.758458,
  0.732175,
  0.695719,
  0.6828,
  0.725265,
  0.671372,
  0.650089,
  0.725115,
  0.74608,
  0.669255
 ],
 "grad_norm_mean": 0.716322,
 "grad_norm_per_epoch": [
  0.932214,
  0.658789,
  0.58462,
  0.65935,
  0.750185,
  0.864483,
  0.91727,
  0.971583,
  0.966582,
  0.986502,
  0.976219,
  0.97107,
  0.931502,
  0.877939,
  0.876702,
  0.847311,
  0.801835,
  0.774134,
  0.754275,
  0.728984,
  0.716392,
  0.717314,
  0.708262,
  0.685968,
  0.695419,
  0.681176,
  0.673067,
  0.653708,
  0.64475,
  0.640284,
  0.657334,
  0.627766,
  0.642966,
  0.629513,
  0.621285,
  0.621083,
  0.630255,
  0.601771,
  0.611036,
  0.606473,
  0.599744,
  0.604746,
  0.59767,
  0.59362,
  0.595092,
  0.58906,
  0.588862,
  0.584712,
  0.583004,
  0.582238
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015153
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
 "peak_memory_gb": 0.741,
 "tail_spread_pct_of_best": 0.114,
 "train_seconds_per_epoch": 0.165,
 "train_seconds_total": 8.25,
 "val_seconds_per_epoch": 0.009,
 "val_seconds_total": 0.45,
 "val_share_of_wall": 0.0515
}
```
