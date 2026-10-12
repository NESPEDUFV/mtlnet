# reg-alabama-p3s3

`18fa81d7b9fa3762` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **3** · split_seed **3** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 4s |
| 1 | ? | ? | 4s |
| 2 | ? | ? | 4s |
| 3 | ? | ? | 4s |
| 4 | ? | ? | 4s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 37,
 "best_value": 0.7336429357528687,
 "clipped_fraction_mean": 0.1176,
 "clipped_fraction_per_epoch": [
  0.4848,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1515,
  0.4242,
  0.4848,
  0.6364,
  0.5758,
  0.5152,
  0.5152,
  0.6061,
  0.4242,
  0.3333,
  0.2727,
  0.0909,
  0.2121,
  0.0,
  0.0606,
  0.0,
  0.0909,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_99pct": 23,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.498617,
 "grad_norm_max_per_epoch": [
  1.428416,
  0.874757,
  0.806459,
  0.709487,
  0.864628,
  0.919578,
  1.129115,
  1.130991,
  1.289823,
  1.498617,
  1.489552,
  1.290822,
  1.212011,
  1.230414,
  1.191978,
  1.163366,
  1.284784,
  1.028044,
  1.190814,
  0.98608,
  1.029852,
  0.971675,
  1.107339,
  0.999998,
  0.961624,
  0.926095,
  0.968181,
  0.853647,
  0.848732,
  0.873552,
  0.84934,
  0.889857,
  0.852981,
  0.858473,
  0.878393,
  0.861292,
  0.820264,
  0.836578,
  0.800038,
  0.762285,
  0.753957,
  0.743926,
  0.771286,
  0.724564,
  0.757353,
  0.768091,
  0.766822,
  0.717241,
  0.719838,
  0.724429
 ],
 "grad_norm_mean": 0.80499,
 "grad_norm_per_epoch": [
  1.067931,
  0.834117,
  0.727777,
  0.644207,
  0.654575,
  0.728007,
  0.884385,
  0.965611,
  0.998673,
  1.071998,
  1.041305,
  1.025451,
  1.018213,
  1.022111,
  0.965982,
  0.956282,
  0.949164,
  0.907385,
  0.931799,
  0.827432,
  0.859212,
  0.816751,
  0.868392,
  0.814222,
  0.805928,
  0.772401,
  0.802406,
  0.758666,
  0.748188,
  0.74758,
  0.768271,
  0.739618,
  0.742942,
  0.729957,
  0.761216,
  0.733449,
  0.7176,
  0.732579,
  0.714187,
  0.690933,
  0.702531,
  0.677752,
  0.691089,
  0.665215,
  0.671109,
  0.666488,
  0.665477,
  0.652335,
  0.650454,
  0.660163
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015159
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.00299999
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
 "peak_memory_gb": 0.505,
 "tail_spread_pct_of_best": 0.098,
 "train_seconds_per_epoch": 0.076,
 "train_seconds_total": 3.79,
 "val_seconds_per_epoch": 0.005,
 "val_seconds_total": 0.24,
 "val_share_of_wall": 0.0605
}
```
