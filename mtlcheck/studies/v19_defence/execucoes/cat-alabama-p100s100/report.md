# cat-alabama-p100s100

`6ff14e4ab71e21aa` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **alabama** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.0025
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 12s |
| 1 | ? | ? | 12s |
| 2 | ? | ? | 12s |
| 3 | ? | ? | 12s |
| 4 | ? | ? | 12s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 12,
 "best_value": 0.3034484386444092,
 "clipped_fraction_mean": 0.0622,
 "clipped_fraction_per_epoch": [
  1.0,
  0.1111,
  0.4444,
  0.0,
  0.0,
  0.0,
  0.0,
  0.2222,
  0.3333,
  0.0,
  0.1111,
  0.0,
  0.0,
  0.6667,
  0.1111,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1111,
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
 "epochs_to_95pct": 4,
 "epochs_to_99pct": 12,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 5.90804,
 "grad_norm_max_per_epoch": [
  5.90804,
  1.192458,
  1.255988,
  0.957386,
  0.782565,
  0.661002,
  0.784814,
  1.322879,
  1.194152,
  0.895563,
  1.063644,
  0.82842,
  0.842022,
  1.757481,
  1.000498,
  0.587761,
  0.582583,
  0.64826,
  0.662681,
  1.16618,
  0.582395,
  0.47076,
  0.648765,
  0.634467,
  0.556828,
  0.500374,
  0.457173,
  0.589227,
  0.579563,
  0.717294,
  0.78303,
  0.796055,
  0.765439,
  0.772855,
  0.766133,
  0.757348,
  0.8635,
  0.701583,
  0.677046,
  0.730173,
  0.726216,
  0.726744,
  0.676494,
  0.811816,
  0.774656,
  0.756804,
  0.73477,
  0.776525,
  0.747104,
  0.762646
 ],
 "grad_norm_mean": 0.567116,
 "grad_norm_per_epoch": [
  2.133686,
  0.85381,
  0.893038,
  0.648396,
  0.554823,
  0.47756,
  0.598016,
  0.827979,
  0.90708,
  0.686404,
  0.666077,
  0.582693,
  0.550916,
  1.187888,
  0.586485,
  0.424539,
  0.355134,
  0.435403,
  0.506438,
  0.648848,
  0.445254,
  0.358155,
  0.460256,
  0.496991,
  0.432264,
  0.391829,
  0.363997,
  0.483998,
  0.424084,
  0.466177,
  0.608152,
  0.514401,
  0.52338,
  0.530883,
  0.461441,
  0.517254,
  0.573237,
  0.504121,
  0.458211,
  0.459496,
  0.481127,
  0.481461,
  0.448854,
  0.456255,
  0.4459,
  0.451055,
  0.411181,
  0.404173,
  0.395999,
  0.380993
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00012661
  ],
  "last": [
   7e-08
  ],
  "max_observed": [
   0.00249994
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
 "peak_memory_gb": 3.04,
 "tail_spread_pct_of_best": 0.309,
 "train_seconds_per_epoch": 0.232,
 "train_seconds_total": 11.6,
 "val_seconds_per_epoch": 0.008,
 "val_seconds_total": 0.39,
 "val_share_of_wall": 0.0329
}
```
