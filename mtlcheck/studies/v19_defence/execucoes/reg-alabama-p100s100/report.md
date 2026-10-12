# reg-alabama-p100s100

`6b070f1a1677efe1` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **alabama** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
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
 "best_epoch": 40,
 "best_value": 0.7376186847686768,
 "clipped_fraction_mean": 0.1242,
 "clipped_fraction_per_epoch": [
  0.7273,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0909,
  0.2424,
  0.6364,
  0.5455,
  0.6667,
  0.6667,
  0.4545,
  0.5758,
  0.5455,
  0.3333,
  0.1818,
  0.0909,
  0.1515,
  0.0,
  0.1212,
  0.0303,
  0.0,
  0.0303,
  0.0606,
  0.0303,
  0.0,
  0.0303,
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
 "epochs_to_99pct": 24,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.505061,
 "grad_norm_max_per_epoch": [
  1.419642,
  0.943239,
  0.806383,
  0.708812,
  0.96118,
  0.868311,
  1.051621,
  1.376636,
  1.372179,
  1.505061,
  1.366046,
  1.29933,
  1.369002,
  1.37155,
  1.257081,
  1.367471,
  1.228391,
  1.057782,
  1.197834,
  0.934464,
  1.03393,
  1.024657,
  0.936242,
  1.084606,
  1.051485,
  1.012677,
  0.94411,
  1.133927,
  0.950621,
  0.850796,
  0.941472,
  0.856467,
  0.834465,
  0.88199,
  0.924997,
  0.870612,
  0.859848,
  0.8334,
  0.74271,
  0.809695,
  0.80343,
  0.804333,
  0.824995,
  0.80593,
  0.752481,
  0.767731,
  0.753248,
  0.72992,
  0.747235,
  0.733087
 ],
 "grad_norm_mean": 0.81172,
 "grad_norm_per_epoch": [
  1.127372,
  0.85728,
  0.723921,
  0.637241,
  0.659995,
  0.744086,
  0.858436,
  0.957373,
  1.053369,
  1.035279,
  1.087897,
  1.071817,
  1.026399,
  1.015408,
  0.9971,
  0.970575,
  0.928239,
  0.884307,
  0.91632,
  0.833503,
  0.856949,
  0.844643,
  0.81221,
  0.852238,
  0.858475,
  0.814586,
  0.783907,
  0.787044,
  0.782236,
  0.762141,
  0.745895,
  0.738466,
  0.736451,
  0.753599,
  0.736835,
  0.754161,
  0.731834,
  0.723212,
  0.6896,
  0.689147,
  0.686365,
  0.698676,
  0.704641,
  0.676683,
  0.66879,
  0.685108,
  0.666961,
  0.652207,
  0.659133,
  0.64789
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
 "peak_memory_gb": 0.504,
 "tail_spread_pct_of_best": 0.126,
 "train_seconds_per_epoch": 0.076,
 "train_seconds_total": 3.82,
 "val_seconds_per_epoch": 0.005,
 "val_seconds_total": 0.24,
 "val_share_of_wall": 0.0601
}
```
