# reg-texas-p1s1

`975cad8bfd7783c5` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **texas** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 207s |
| 1 | ? | ? | 208s |
| 2 | ? | ? | 208s |
| 3 | ? | ? | 208s |
| 4 | ? | ? | 208s |

## Worth a look

- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 1}), (3, {'top1': 1, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 1, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 49,
 "best_value": 0.6360607743263245,
 "clipped_fraction_mean": 0.1622,
 "clipped_fraction_per_epoch": [
  0.0427,
  0.6885,
  0.9977,
  1.0,
  1.0,
  1.0,
  1.0,
  0.9885,
  0.871,
  0.4115,
  0.0947,
  0.0107,
  0.0008,
  0.0008,
  0.0008,
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
 "epochs_to_95pct": 4,
 "epochs_to_99pct": 26,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.86723,
 "grad_norm_max_per_epoch": [
  1.823487,
  2.329775,
  2.863641,
  2.86723,
  2.754954,
  2.409874,
  2.717381,
  1.97097,
  2.109366,
  1.599099,
  1.454089,
  1.491531,
  1.111636,
  1.031176,
  1.162156,
  1.109161,
  0.96591,
  0.921636,
  0.941733,
  0.875512,
  0.816764,
  0.799408,
  0.863685,
  0.880799,
  0.890076,
  0.870686,
  0.871579,
  0.854261,
  0.855335,
  0.769532,
  0.895537,
  0.75924,
  0.857358,
  0.88502,
  0.781682,
  0.92218,
  0.799636,
  0.819486,
  0.922256,
  0.939576,
  0.893663,
  0.908706,
  0.933694,
  0.894945,
  0.845876,
  0.872824,
  0.911125,
  0.93335,
  0.862978,
  0.784297
 ],
 "grad_norm_mean": 0.642939,
 "grad_norm_per_epoch": [
  0.743882,
  1.075263,
  1.326303,
  1.456984,
  1.520282,
  1.488038,
  1.404061,
  1.270855,
  1.13065,
  0.984783,
  0.877517,
  0.790451,
  0.721284,
  0.664318,
  0.616842,
  0.583076,
  0.556019,
  0.532847,
  0.519895,
  0.50406,
  0.494616,
  0.486775,
  0.477569,
  0.47019,
  0.466496,
  0.461231,
  0.457558,
  0.45748,
  0.451305,
  0.446646,
  0.448959,
  0.445122,
  0.443462,
  0.442502,
  0.443652,
  0.438884,
  0.439916,
  0.438135,
  0.43713,
  0.437028,
  0.43724,
  0.435052,
  0.433993,
  0.431079,
  0.429043,
  0.42851,
  0.425927,
  0.426401,
  0.423208,
  0.424416
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
 "peak_memory_gb": 8.764,
 "tail_spread_pct_of_best": 0.059,
 "train_seconds_per_epoch": 3.865,
 "train_seconds_total": 193.27,
 "val_seconds_per_epoch": 0.269,
 "val_seconds_total": 13.44,
 "val_share_of_wall": 0.065
}
```
