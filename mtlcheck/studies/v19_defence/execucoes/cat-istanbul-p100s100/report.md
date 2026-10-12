# cat-istanbul-p100s100

`c3e89006aee3f3bd` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 34s |
| 1 | ? | ? | 34s |
| 2 | ? | ? | 34s |
| 3 | ? | ? | 34s |
| 4 | ? | ? | 34s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 36,
 "best_value": 0.34880468249320984,
 "clipped_fraction_mean": 0.0325,
 "clipped_fraction_per_epoch": [
  1.0,
  0.125,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.0417,
  0.25,
  0.0417,
  0.0417,
  0.0,
  0.0417,
  0.0417,
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
 "epochs_to_95pct": 13,
 "epochs_to_99pct": 24,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.75408,
 "grad_norm_max_per_epoch": [
  5.75408,
  1.231369,
  0.73694,
  0.923597,
  0.876267,
  0.577006,
  0.981715,
  0.961693,
  1.215527,
  1.046022,
  1.358399,
  1.195118,
  1.119517,
  0.958521,
  1.049945,
  1.330537,
  0.702263,
  0.962899,
  0.805153,
  0.916824,
  0.824336,
  0.710635,
  0.738484,
  0.899674,
  0.666121,
  0.686295,
  0.657164,
  0.821999,
  0.589161,
  0.794158,
  0.739575,
  0.637776,
  0.713953,
  0.575704,
  0.5192,
  0.487619,
  0.713847,
  0.631226,
  0.558246,
  0.440027,
  0.634044,
  0.528911,
  0.544789,
  0.444477,
  0.495164,
  0.424685,
  0.839255,
  0.62176,
  0.468882,
  0.657186
 ],
 "grad_norm_mean": 0.476698,
 "grad_norm_per_epoch": [
  2.259664,
  0.786394,
  0.559078,
  0.479781,
  0.418925,
  0.414436,
  0.488216,
  0.63008,
  0.519566,
  0.59794,
  0.828217,
  0.626937,
  0.682325,
  0.581968,
  0.522244,
  0.603535,
  0.49678,
  0.487549,
  0.512894,
  0.475151,
  0.49464,
  0.425302,
  0.419909,
  0.493278,
  0.390246,
  0.42449,
  0.379709,
  0.478977,
  0.392476,
  0.476907,
  0.415337,
  0.429006,
  0.344506,
  0.376313,
  0.330985,
  0.302032,
  0.369588,
  0.384811,
  0.338154,
  0.319842,
  0.324966,
  0.330048,
  0.310715,
  0.299704,
  0.265267,
  0.269952,
  0.270336,
  0.266399,
  0.263487,
  0.275823
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   2.527e-05
  ],
  "last": [
   0.0
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
 "peak_memory_gb": 3.419,
 "tail_spread_pct_of_best": 0.282,
 "train_seconds_per_epoch": 0.653,
 "train_seconds_total": 32.63,
 "val_seconds_per_epoch": 0.021,
 "val_seconds_total": 1.04,
 "val_share_of_wall": 0.0309
}
```
