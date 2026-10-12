# reg-arizona-p7s7

`9ca76270cfd0feb0` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **arizona** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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

- selection landed on the FIRST or LAST epoch in fold(s) [0] — the schedule is probably mis-sized (50 epochs)
- ties at the decision boundary: [(4, {'top1': 1, 'top5': 0, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 50,
 "best_value": 0.6467894315719604,
 "clipped_fraction_mean": 0.0443,
 "clipped_fraction_per_epoch": [
  0.2899,
  0.0,
  0.0,
  0.0,
  0.029,
  0.0725,
  0.1594,
  0.3188,
  0.2899,
  0.2754,
  0.3188,
  0.1304,
  0.1739,
  0.1014,
  0.0,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 11,
 "epochs_to_99pct": 25,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.50628,
 "grad_norm_max_per_epoch": [
  1.50628,
  0.788874,
  0.68164,
  0.805282,
  1.104676,
  1.072346,
  1.25473,
  1.173376,
  1.126312,
  1.239188,
  1.225429,
  1.187684,
  1.124577,
  1.242451,
  0.997664,
  1.082071,
  1.054658,
  0.989266,
  0.904601,
  0.925491,
  0.876071,
  0.849737,
  0.807215,
  0.862593,
  0.802506,
  0.790179,
  0.845781,
  0.820791,
  0.757024,
  0.828802,
  0.747157,
  0.793701,
  0.718693,
  0.723501,
  0.682733,
  0.752492,
  0.766563,
  0.722544,
  0.724767,
  0.691262,
  0.706083,
  0.726925,
  0.727916,
  0.732017,
  0.734145,
  0.654705,
  0.733352,
  0.678511,
  0.776146,
  0.705459
 ],
 "grad_norm_mean": 0.706981,
 "grad_norm_per_epoch": [
  0.962363,
  0.662336,
  0.599454,
  0.623437,
  0.789148,
  0.847302,
  0.908897,
  0.941163,
  0.95232,
  0.960991,
  0.954398,
  0.915628,
  0.927036,
  0.871676,
  0.828895,
  0.814912,
  0.805064,
  0.772459,
  0.751696,
  0.734394,
  0.702234,
  0.705468,
  0.687819,
  0.680831,
  0.660584,
  0.672349,
  0.65584,
  0.66384,
  0.64839,
  0.631491,
  0.629708,
  0.627687,
  0.622766,
  0.628265,
  0.616546,
  0.621079,
  0.614525,
  0.609566,
  0.604834,
  0.589987,
  0.594685,
  0.594115,
  0.59273,
  0.592653,
  0.579836,
  0.58347,
  0.577121,
  0.577172,
  0.579162,
  0.580715
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
 "tail_spread_pct_of_best": 0.146,
 "train_seconds_per_epoch": 0.165,
 "train_seconds_total": 8.23,
 "val_seconds_per_epoch": 0.009,
 "val_seconds_total": 0.45,
 "val_share_of_wall": 0.0518
}
```
