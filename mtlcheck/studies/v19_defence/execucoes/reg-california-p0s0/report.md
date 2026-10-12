# reg-california-p0s0

`0dafa08e466cbcbe` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **california** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 183s |
| 1 | ? | ? | 173s |
| 2 | ? | ? | 174s |
| 3 | ? | ? | 175s |
| 4 | ? | ? | 175s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2, 4] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(0, {'top1': 1, 'top5': 0, 'top10': 1}), (1, {'top1': 1, 'top5': 1, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 1}), (3, {'top1': 1, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 47,
 "best_value": 0.6278350353240967,
 "clipped_fraction_mean": 0.1595,
 "clipped_fraction_per_epoch": [
  0.014,
  0.124,
  0.865,
  1.0,
  1.0,
  1.0,
  1.0,
  0.998,
  0.976,
  0.692,
  0.264,
  0.039,
  0.004,
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
  "frames_ok": 3,
  "frames_total": 3,
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
 "grad_norm_max": 1.899612,
 "grad_norm_max_per_epoch": [
  1.373802,
  1.399679,
  1.513054,
  1.794992,
  1.899612,
  1.855509,
  1.885645,
  1.795782,
  1.739233,
  1.335525,
  1.233078,
  1.116325,
  1.148141,
  0.929677,
  0.902579,
  0.863469,
  0.844533,
  0.748532,
  0.716078,
  0.69658,
  0.675728,
  0.682976,
  0.676846,
  0.666656,
  0.64734,
  0.645565,
  0.646819,
  0.63966,
  0.612286,
  0.626524,
  0.629707,
  0.625269,
  0.597056,
  0.590744,
  0.580691,
  0.600229,
  0.573748,
  0.587511,
  0.567513,
  0.561468,
  0.553043,
  0.561052,
  0.560872,
  0.566447,
  0.553864,
  0.548258,
  0.553565,
  0.55202,
  0.540756,
  0.572958
 ],
 "grad_norm_mean": 0.659592,
 "grad_norm_per_epoch": [
  0.623607,
  0.86657,
  1.127884,
  1.297427,
  1.402187,
  1.425362,
  1.390021,
  1.305439,
  1.186676,
  1.051872,
  0.942437,
  0.853384,
  0.779391,
  0.721896,
  0.672277,
  0.635794,
  0.612044,
  0.586909,
  0.565418,
  0.553303,
  0.535257,
  0.530154,
  0.519113,
  0.514119,
  0.507129,
  0.499787,
  0.497151,
  0.492223,
  0.489042,
  0.486347,
  0.481894,
  0.482609,
  0.475086,
  0.477845,
  0.474415,
  0.471715,
  0.472191,
  0.469801,
  0.467238,
  0.467348,
  0.463217,
  0.461828,
  0.46012,
  0.460182,
  0.457732,
  0.455899,
  0.454266,
  0.452276,
  0.451799,
  0.451892
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
 "peak_memory_gb": 6.866,
 "tail_spread_pct_of_best": 0.042,
 "train_seconds_per_epoch": 3.337,
 "train_seconds_total": 166.86,
 "val_seconds_per_epoch": 0.309,
 "val_seconds_total": 15.47,
 "val_share_of_wall": 0.0849
}
```
