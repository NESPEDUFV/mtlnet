# cat-istanbul-p0s0

`7919c99e1d8af33c` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
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
| 1 | ? | ? | 33s |
| 2 | ? | ? | 34s |
| 3 | ? | ? | 34s |
| 4 | ? | ? | 34s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 25,
 "best_value": 0.351933091878891,
 "clipped_fraction_mean": 0.0308,
 "clipped_fraction_per_epoch": [
  0.9167,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.0,
  0.0417,
  0.0,
  0.0417,
  0.4167,
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
  0.0
 ],
 "compile_counters": {
  "frames_ok": 9,
  "frames_total": 10,
  "graph_breaks": 3,
  "unique_graph_breaks": 1
 },
 "epochs_to_95pct": 13,
 "epochs_to_99pct": 18,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.737722,
 "grad_norm_max_per_epoch": [
  4.737722,
  0.873247,
  0.66347,
  0.877345,
  0.74004,
  0.692049,
  1.046455,
  0.776545,
  1.17217,
  0.936562,
  1.014871,
  1.470387,
  1.172541,
  0.827074,
  0.967673,
  0.924115,
  0.927122,
  0.854922,
  0.706692,
  0.606144,
  0.712731,
  0.682108,
  0.708344,
  0.748298,
  0.904049,
  1.034794,
  0.758377,
  0.477841,
  0.629558,
  0.578568,
  0.943223,
  0.815058,
  0.557762,
  0.726849,
  0.829154,
  0.748782,
  0.536528,
  0.450972,
  0.668371,
  0.628754,
  0.502889,
  0.573998,
  0.643569,
  0.472044,
  0.672873,
  0.393987,
  0.589141,
  0.582393,
  0.611896,
  0.488971
 ],
 "grad_norm_mean": 0.462403,
 "grad_norm_per_epoch": [
  1.710237,
  0.684946,
  0.502226,
  0.503771,
  0.510033,
  0.478711,
  0.562618,
  0.528479,
  0.624687,
  0.616419,
  0.549944,
  0.909705,
  0.665243,
  0.651949,
  0.554612,
  0.532399,
  0.522846,
  0.473925,
  0.438877,
  0.424614,
  0.428388,
  0.406215,
  0.480654,
  0.485317,
  0.47256,
  0.460568,
  0.462845,
  0.339183,
  0.344716,
  0.413602,
  0.415927,
  0.459124,
  0.359713,
  0.35279,
  0.392922,
  0.378544,
  0.333268,
  0.314285,
  0.305412,
  0.300808,
  0.317411,
  0.283376,
  0.301836,
  0.282484,
  0.295795,
  0.259104,
  0.262995,
  0.271197,
  0.235694,
  0.257153
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
 "tail_spread_pct_of_best": 0.168,
 "train_seconds_per_epoch": 0.654,
 "train_seconds_total": 32.68,
 "val_seconds_per_epoch": 0.023,
 "val_seconds_total": 1.14,
 "val_share_of_wall": 0.0337
}
```
