# cat-arizona-p1s1

`78f399aec0b3b383` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **arizona** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 25s |
| 1 | ? | ? | 25s |
| 2 | ? | ? | 25s |
| 3 | ? | ? | 25s |
| 4 | ? | ? | 25s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 43,
 "best_value": 0.3244507908821106,
 "clipped_fraction_mean": 0.0478,
 "clipped_fraction_per_epoch": [
  1.0,
  0.6667,
  0.1667,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1111,
  0.0,
  0.1667,
  0.1667,
  0.0,
  0.0,
  0.0,
  0.0556,
  0.0556,
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
  "frames_ok": 4,
  "frames_total": 4,
  "graph_breaks": 2,
  "unique_graph_breaks": 1
 },
 "epochs_to_95pct": 11,
 "epochs_to_99pct": 26,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 9.591088,
 "grad_norm_max_per_epoch": [
  9.591088,
  2.191058,
  1.231766,
  0.851105,
  0.901581,
  0.9346,
  0.992131,
  1.136151,
  0.930651,
  1.400665,
  1.114916,
  0.912675,
  0.94354,
  0.839799,
  1.017454,
  1.154604,
  0.94668,
  0.7557,
  0.796801,
  0.687656,
  0.80381,
  0.652483,
  0.756394,
  0.468123,
  0.535515,
  0.646059,
  0.619501,
  0.808283,
  0.545848,
  0.560082,
  0.550868,
  0.730703,
  0.599198,
  0.562767,
  0.543204,
  0.579096,
  0.576481,
  0.586589,
  0.615978,
  0.570176,
  0.544228,
  0.505541,
  0.48347,
  0.688445,
  0.611,
  0.529287,
  0.510837,
  0.532989,
  0.516131,
  0.658809
 ],
 "grad_norm_mean": 0.522727,
 "grad_norm_per_epoch": [
  4.045976,
  1.387714,
  0.772683,
  0.553772,
  0.539477,
  0.51199,
  0.568335,
  0.730544,
  0.594698,
  0.774325,
  0.697108,
  0.493248,
  0.66331,
  0.493382,
  0.498688,
  0.613334,
  0.524348,
  0.421524,
  0.485331,
  0.522311,
  0.466993,
  0.455402,
  0.514287,
  0.354113,
  0.311224,
  0.427673,
  0.395678,
  0.425619,
  0.361926,
  0.371672,
  0.375072,
  0.359116,
  0.37777,
  0.386716,
  0.340083,
  0.359379,
  0.368682,
  0.364474,
  0.291237,
  0.330722,
  0.299026,
  0.264256,
  0.267625,
  0.2603,
  0.263305,
  0.26267,
  0.261274,
  0.244668,
  0.227106,
  0.256172
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   2.528e-05
  ],
  "last": [
   1e-08
  ],
  "max_observed": [
   0.0005
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
 "peak_memory_gb": 3.267,
 "tail_spread_pct_of_best": 0.285,
 "train_seconds_per_epoch": 0.487,
 "train_seconds_total": 24.37,
 "val_seconds_per_epoch": 0.016,
 "val_seconds_total": 0.82,
 "val_share_of_wall": 0.0325
}
```
