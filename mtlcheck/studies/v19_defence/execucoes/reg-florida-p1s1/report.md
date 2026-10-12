# reg-florida-p1s1

`403e5a788a9fd85b` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **florida** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
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
| 2 | ? | ? | 64s |
| 3 | ? | ? | 64s |
| 4 | ? | ? | 64s |

## Worth a look

- ties at the decision boundary: [(0, {'top1': 0, 'top5': 0, 'top10': 1}), (2, {'top1': 1, 'top5': 0, 'top10': 0}), (3, {'top1': 0, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 45,
 "best_value": 0.7722963690757751,
 "clipped_fraction_mean": 0.0763,
 "clipped_fraction_per_epoch": [
  0.4106,
  0.0,
  0.0252,
  0.1858,
  0.4702,
  0.7523,
  0.6972,
  0.6674,
  0.3968,
  0.1697,
  0.0298,
  0.0092,
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
 "grad_norm_max": 4.65008,
 "grad_norm_max_per_epoch": [
  4.65008,
  0.892331,
  1.089801,
  1.214354,
  1.336931,
  1.311716,
  1.520497,
  1.339425,
  1.32239,
  1.180439,
  1.070604,
  1.01739,
  0.978633,
  0.908002,
  0.838511,
  0.831704,
  0.787847,
  0.731394,
  0.742224,
  0.652566,
  0.605137,
  0.621065,
  0.615802,
  0.579277,
  0.607568,
  0.58239,
  0.565156,
  0.543386,
  0.532492,
  0.534411,
  0.525353,
  0.537749,
  0.531565,
  0.589485,
  0.485161,
  0.492143,
  0.504198,
  0.572306,
  0.523299,
  0.529716,
  0.508204,
  0.515166,
  0.507619,
  0.463186,
  0.486057,
  0.48131,
  0.497932,
  0.485878,
  0.475296,
  0.526663
 ],
 "grad_norm_mean": 0.573301,
 "grad_norm_per_epoch": [
  1.121488,
  0.63338,
  0.786173,
  0.926828,
  1.00213,
  1.058866,
  1.056032,
  1.041102,
  0.986785,
  0.922811,
  0.859222,
  0.795028,
  0.734356,
  0.698005,
  0.645118,
  0.613154,
  0.582022,
  0.560133,
  0.541966,
  0.520303,
  0.499434,
  0.487833,
  0.478267,
  0.46484,
  0.458097,
  0.451627,
  0.443287,
  0.437474,
  0.429453,
  0.425855,
  0.42178,
  0.419243,
  0.415612,
  0.407625,
  0.41103,
  0.40794,
  0.407688,
  0.402698,
  0.401587,
  0.398106,
  0.397993,
  0.395997,
  0.394346,
  0.390782,
  0.39297,
  0.39147,
  0.389205,
  0.3854,
  0.387736,
  0.384763
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
 "peak_memory_gb": 3.168,
 "tail_spread_pct_of_best": 0.045,
 "train_seconds_per_epoch": 1.188,
 "train_seconds_total": 59.41,
 "val_seconds_per_epoch": 0.075,
 "val_seconds_total": 3.74,
 "val_share_of_wall": 0.0592
}
```
