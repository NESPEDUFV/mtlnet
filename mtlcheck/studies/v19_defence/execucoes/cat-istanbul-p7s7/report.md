# cat-istanbul-p7s7

`3f46d9ee8005694c` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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
 "best_epoch": 44,
 "best_value": 0.34474366903305054,
 "clipped_fraction_mean": 0.0317,
 "clipped_fraction_per_epoch": [
  0.9167,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0833,
  0.3333,
  0.0,
  0.0,
  0.0,
  0.1667,
  0.0,
  0.0,
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
  0.0
 ],
 "compile_counters": {
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 13,
 "epochs_to_99pct": 28,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.426726,
 "grad_norm_max_per_epoch": [
  4.426726,
  0.967294,
  0.85791,
  0.758753,
  0.717594,
  0.826947,
  0.90697,
  1.022838,
  1.596199,
  0.7816,
  0.846341,
  0.995967,
  1.187276,
  0.75081,
  0.846049,
  0.924547,
  1.124314,
  1.07461,
  0.800205,
  0.658822,
  0.843887,
  0.835127,
  0.741453,
  0.77251,
  0.681805,
  0.748269,
  0.983704,
  0.657685,
  0.590414,
  0.567189,
  0.710857,
  0.655044,
  0.62878,
  0.604487,
  0.535788,
  0.700676,
  0.513558,
  0.533414,
  0.534542,
  0.680335,
  0.478808,
  0.461165,
  0.664214,
  0.542593,
  0.634641,
  0.49231,
  0.638107,
  0.656167,
  0.52115,
  0.572113
 ],
 "grad_norm_mean": 0.462445,
 "grad_norm_per_epoch": [
  1.695208,
  0.727461,
  0.48487,
  0.517586,
  0.468958,
  0.524104,
  0.570332,
  0.600231,
  0.92261,
  0.460921,
  0.544988,
  0.59625,
  0.754929,
  0.49132,
  0.546523,
  0.53821,
  0.639861,
  0.475306,
  0.579372,
  0.420657,
  0.488001,
  0.488322,
  0.455679,
  0.445058,
  0.391445,
  0.411806,
  0.382193,
  0.359727,
  0.408975,
  0.34061,
  0.461415,
  0.405543,
  0.340293,
  0.388997,
  0.357655,
  0.316148,
  0.317832,
  0.353906,
  0.33986,
  0.329322,
  0.309657,
  0.299213,
  0.272641,
  0.284911,
  0.278072,
  0.281197,
  0.263376,
  0.260828,
  0.262899,
  0.26696
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
 "tail_spread_pct_of_best": 0.33,
 "train_seconds_per_epoch": 0.653,
 "train_seconds_total": 32.63,
 "val_seconds_per_epoch": 0.021,
 "val_seconds_total": 1.04,
 "val_share_of_wall": 0.0307
}
```
