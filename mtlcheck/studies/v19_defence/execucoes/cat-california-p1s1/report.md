# cat-california-p1s1

`5733dffb76975882` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **california** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 368s |
| 1 | ? | ? | 367s |
| 2 | ? | ? | 367s |
| 3 | ? | ? | 367s |
| 4 | ? | ? | 367s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [2] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(2, {'top3': 1, 'top5': 1})]

## Diagnostics

```json
{
 "best_epoch": 43,
 "best_value": 0.35614579916000366,
 "clipped_fraction_mean": 0.0008,
 "clipped_fraction_per_epoch": [
  0.04,
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
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 6,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 7.683243,
 "grad_norm_max_per_epoch": [
  7.683243,
  0.723213,
  0.791673,
  0.659092,
  0.658777,
  0.465084,
  0.558271,
  0.483519,
  0.381825,
  0.355361,
  0.218564,
  0.158008,
  0.11604,
  0.109733,
  0.100568,
  0.10061,
  0.088077,
  0.084565,
  0.081805,
  0.089162,
  0.086762,
  0.084516,
  0.0877,
  0.08136,
  0.085557,
  0.080676,
  0.080378,
  0.091856,
  0.085028,
  0.079694,
  0.086226,
  0.085757,
  0.083724,
  0.077752,
  0.077785,
  0.083218,
  0.077452,
  0.074752,
  0.076716,
  0.076115,
  0.083741,
  0.074177,
  0.077017,
  0.078285,
  0.075061,
  0.074602,
  0.077275,
  0.075928,
  0.077262,
  0.07457
 ],
 "grad_norm_mean": 0.114633,
 "grad_norm_per_epoch": [
  0.488624,
  0.349215,
  0.3437,
  0.329523,
  0.280584,
  0.248387,
  0.271707,
  0.236644,
  0.197568,
  0.170074,
  0.131763,
  0.103577,
  0.08399,
  0.077414,
  0.071271,
  0.067289,
  0.065489,
  0.063107,
  0.064251,
  0.063492,
  0.06413,
  0.065581,
  0.066336,
  0.065769,
  0.066043,
  0.066278,
  0.067213,
  0.067628,
  0.069873,
  0.067747,
  0.068875,
  0.06909,
  0.06828,
  0.067305,
  0.068091,
  0.068661,
  0.068431,
  0.067302,
  0.067309,
  0.067084,
  0.067675,
  0.067103,
  0.067344,
  0.067552,
  0.067558,
  0.067794,
  0.067884,
  0.068033,
  0.068061,
  0.067937
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025247
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.005
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
 "peak_memory_gb": 9.148,
 "tail_spread_pct_of_best": 0.041,
 "train_seconds_per_epoch": 7.081,
 "train_seconds_total": 354.06,
 "val_seconds_per_epoch": 0.261,
 "val_seconds_total": 13.03,
 "val_share_of_wall": 0.0355
}
```
