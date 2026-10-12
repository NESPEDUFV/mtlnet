# cat-istanbul-p13s13

`e81a2b768886e18d` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **13** · split_seed **13** · engine `check2hgi_v18`
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
| 2 | ? | ? | 35s |
| 3 | ? | ? | 34s |
| 4 | ? | ? | 34s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 40,
 "best_value": 0.3502086400985718,
 "clipped_fraction_mean": 0.0317,
 "clipped_fraction_per_epoch": [
  1.0,
  0.2917,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.125,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.0,
  0.0417,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 19,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 6.670525,
 "grad_norm_max_per_epoch": [
  6.670525,
  1.547079,
  0.918506,
  0.926205,
  0.682494,
  1.160278,
  1.059317,
  0.777259,
  0.983736,
  0.875777,
  0.863178,
  1.128696,
  0.90078,
  1.01064,
  0.902138,
  0.953176,
  0.762326,
  1.012908,
  0.789207,
  0.724107,
  0.755131,
  0.993376,
  0.6094,
  0.712172,
  0.690672,
  0.713205,
  0.760773,
  0.542854,
  0.854237,
  0.734851,
  0.877342,
  0.577969,
  0.706977,
  0.547535,
  0.630101,
  0.668078,
  0.563316,
  0.631198,
  0.680957,
  0.564435,
  0.48994,
  0.499461,
  0.540398,
  0.501212,
  0.661399,
  0.654693,
  0.647804,
  0.625497,
  0.549212,
  0.567893
 ],
 "grad_norm_mean": 0.50094,
 "grad_norm_per_epoch": [
  2.725851,
  0.831325,
  0.503525,
  0.471157,
  0.468468,
  0.599409,
  0.69996,
  0.499034,
  0.666426,
  0.625557,
  0.479679,
  0.680673,
  0.615917,
  0.638921,
  0.533211,
  0.540047,
  0.459655,
  0.456454,
  0.500178,
  0.422414,
  0.490317,
  0.610971,
  0.406087,
  0.464023,
  0.435674,
  0.483113,
  0.395257,
  0.365771,
  0.488664,
  0.456651,
  0.448428,
  0.376432,
  0.439178,
  0.372326,
  0.427947,
  0.41938,
  0.416677,
  0.418665,
  0.42213,
  0.350474,
  0.308292,
  0.329397,
  0.296128,
  0.321186,
  0.297563,
  0.296758,
  0.283335,
  0.293794,
  0.258125,
  0.256402
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
 "tail_spread_pct_of_best": 0.161,
 "train_seconds_per_epoch": 0.654,
 "train_seconds_total": 32.71,
 "val_seconds_per_epoch": 0.021,
 "val_seconds_total": 1.04,
 "val_share_of_wall": 0.0307
}
```
