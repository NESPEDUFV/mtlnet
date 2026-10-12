# reg-arizona-p1s1

`08eb019626d58d65` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **arizona** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 10s |
| 1 | ? | ? | 9s |
| 2 | ? | ? | 9s |
| 3 | ? | ? | 9s |
| 4 | ? | ? | 9s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 42,
 "best_value": 0.6496764421463013,
 "clipped_fraction_mean": 0.0612,
 "clipped_fraction_per_epoch": [
  0.2464,
  0.0,
  0.0,
  0.0,
  0.0,
  0.087,
  0.2754,
  0.3333,
  0.5507,
  0.3623,
  0.4638,
  0.2899,
  0.2029,
  0.1594,
  0.029,
  0.029,
  0.029,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 28,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.363063,
 "grad_norm_max_per_epoch": [
  1.363063,
  0.804556,
  0.730573,
  0.805329,
  0.990886,
  1.179149,
  1.170843,
  1.295231,
  1.33289,
  1.165271,
  1.299251,
  1.138803,
  1.201968,
  1.112936,
  1.108519,
  1.043399,
  1.128094,
  0.96674,
  0.974428,
  0.810974,
  0.95496,
  0.854983,
  0.851773,
  0.86927,
  0.844426,
  0.803958,
  0.846627,
  0.776743,
  0.775595,
  0.763063,
  0.82196,
  0.750061,
  0.740223,
  0.745526,
  0.790864,
  0.81432,
  0.730163,
  0.766928,
  0.777021,
  0.730085,
  0.745578,
  0.71852,
  0.706136,
  0.67789,
  0.72349,
  0.703311,
  0.700223,
  0.737994,
  0.729747,
  0.740904
 ],
 "grad_norm_mean": 0.724757,
 "grad_norm_per_epoch": [
  0.924072,
  0.677924,
  0.604213,
  0.65482,
  0.773192,
  0.871402,
  0.945225,
  0.979573,
  1.016969,
  0.969043,
  1.005581,
  0.948908,
  0.936712,
  0.92009,
  0.863804,
  0.828164,
  0.829157,
  0.787043,
  0.77044,
  0.719755,
  0.732689,
  0.725607,
  0.700773,
  0.706471,
  0.694172,
  0.673877,
  0.682666,
  0.66312,
  0.656653,
  0.646703,
  0.652474,
  0.653818,
  0.648045,
  0.626076,
  0.628957,
  0.628997,
  0.63362,
  0.619959,
  0.614853,
  0.624017,
  0.617455,
  0.609833,
  0.607806,
  0.605334,
  0.604689,
  0.595821,
  0.589078,
  0.591719,
  0.589119,
  0.587358
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
 "tail_spread_pct_of_best": 0.061,
 "train_seconds_per_epoch": 0.176,
 "train_seconds_total": 8.8,
 "val_seconds_per_epoch": 0.014,
 "val_seconds_total": 0.7,
 "val_share_of_wall": 0.0735
}
```
