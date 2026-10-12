# reg-texas-p7s7

`ce5caae2e22586a2` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **texas** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 209s |
| 1 | ? | ? | 209s |
| 2 | ? | ? | 209s |
| 3 | ? | ? | 209s |
| 4 | ? | ? | 209s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2, 4] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 1, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 2, 'top10': 1}), (3, {'top1': 0, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 1, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 48,
 "best_value": 0.6386035680770874,
 "clipped_fraction_mean": 0.1608,
 "clipped_fraction_per_epoch": [
  0.0328,
  0.6183,
  0.9908,
  0.9992,
  1.0,
  1.0,
  1.0,
  0.9878,
  0.8656,
  0.4519,
  0.0832,
  0.0092,
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
 "epochs_to_99pct": 29,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.757548,
 "grad_norm_max_per_epoch": [
  1.689596,
  2.239531,
  2.295882,
  2.522335,
  2.674372,
  2.757548,
  1.996758,
  2.09117,
  1.708628,
  1.68783,
  1.507642,
  1.361774,
  1.218835,
  1.092162,
  1.103213,
  0.859103,
  0.968452,
  0.878355,
  0.998686,
  0.96082,
  0.826896,
  0.904933,
  0.868308,
  0.812505,
  0.85545,
  0.93837,
  0.835565,
  0.95083,
  0.916998,
  0.949379,
  0.884055,
  0.832853,
  0.84793,
  0.836803,
  0.840446,
  0.746557,
  0.814087,
  0.881981,
  0.874578,
  0.843879,
  0.948091,
  0.961924,
  0.998616,
  0.932937,
  0.915848,
  0.912645,
  0.871858,
  0.877144,
  0.867572,
  0.942759
 ],
 "grad_norm_mean": 0.639006,
 "grad_norm_per_epoch": [
  0.733492,
  1.051897,
  1.287772,
  1.43712,
  1.49152,
  1.468188,
  1.386342,
  1.258613,
  1.123656,
  0.990411,
  0.876032,
  0.787495,
  0.717276,
  0.658608,
  0.61518,
  0.577738,
  0.554119,
  0.530182,
  0.519006,
  0.505026,
  0.493974,
  0.48234,
  0.476473,
  0.469692,
  0.465,
  0.462294,
  0.456191,
  0.452422,
  0.451148,
  0.448824,
  0.44803,
  0.444532,
  0.444672,
  0.443362,
  0.442627,
  0.441227,
  0.441533,
  0.440421,
  0.439904,
  0.438242,
  0.43463,
  0.434696,
  0.434156,
  0.432443,
  0.431453,
  0.42835,
  0.427242,
  0.42547,
  0.425483,
  0.423802
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
 "tail_spread_pct_of_best": 0.047,
 "train_seconds_per_epoch": 3.873,
 "train_seconds_total": 193.63,
 "val_seconds_per_epoch": 0.287,
 "val_seconds_total": 14.35,
 "val_share_of_wall": 0.069
}
```
