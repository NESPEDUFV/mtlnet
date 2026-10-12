# reg-istanbul-p100s100

`8c28ba4598ad0423` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
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

- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 39,
 "best_value": 0.753128707408905,
 "clipped_fraction_mean": 0.1045,
 "clipped_fraction_per_epoch": [
  0.6989,
  0.0,
  0.0108,
  0.2366,
  0.3011,
  0.5376,
  0.5376,
  0.6667,
  0.6452,
  0.5914,
  0.4301,
  0.3333,
  0.129,
  0.043,
  0.0645,
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
 "epochs_to_95pct": 6,
 "epochs_to_99pct": 23,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.467617,
 "grad_norm_max_per_epoch": [
  2.467617,
  0.858738,
  1.059952,
  1.187798,
  1.420187,
  1.297713,
  1.358849,
  1.39898,
  1.456385,
  1.30252,
  1.738247,
  1.189406,
  1.311857,
  1.138724,
  1.119032,
  0.989825,
  0.921675,
  0.944011,
  0.803001,
  0.833426,
  0.787322,
  0.802483,
  0.840965,
  0.737899,
  0.712008,
  0.731612,
  0.77928,
  0.698669,
  0.734081,
  0.68092,
  0.676125,
  0.705856,
  0.604093,
  0.664657,
  0.637382,
  0.681342,
  0.65908,
  0.596752,
  0.664585,
  0.603933,
  0.622172,
  0.582191,
  0.58212,
  0.577939,
  0.579504,
  0.575008,
  0.579267,
  0.556469,
  0.570802,
  0.545404
 ],
 "grad_norm_mean": 0.67153,
 "grad_norm_per_epoch": [
  1.26162,
  0.705707,
  0.711262,
  0.894838,
  0.968202,
  1.022742,
  1.026166,
  1.07549,
  1.048132,
  1.029565,
  1.003959,
  0.95524,
  0.893756,
  0.830047,
  0.807189,
  0.768591,
  0.727198,
  0.693072,
  0.672285,
  0.667749,
  0.631178,
  0.613597,
  0.602385,
  0.584594,
  0.587211,
  0.574738,
  0.562587,
  0.55278,
  0.537464,
  0.542132,
  0.539513,
  0.531043,
  0.522189,
  0.531409,
  0.531002,
  0.508425,
  0.520248,
  0.512625,
  0.513822,
  0.496667,
  0.49626,
  0.488606,
  0.490794,
  0.482933,
  0.486166,
  0.476053,
  0.477272,
  0.475378,
  0.471695,
  0.472926
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
 "tail_spread_pct_of_best": 0.059,
 "train_seconds_per_epoch": 0.209,
 "train_seconds_total": 10.44,
 "val_seconds_per_epoch": 0.011,
 "val_seconds_total": 0.55,
 "val_share_of_wall": 0.0503
}
```
