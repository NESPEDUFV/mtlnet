# cat-california-p0s0

`1c267bdae79bdd5d` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **california** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 366s |
| 1 | ? | ? | 365s |
| 2 | ? | ? | 365s |
| 3 | ? | ? | 365s |
| 4 | ? | ? | 365s |

## Worth a look

Nothing flagged.

## Diagnostics

```json
{
 "best_epoch": 42,
 "best_value": 0.3602713644504547,
 "clipped_fraction_mean": 0.0007,
 "clipped_fraction_per_epoch": [
  0.036,
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
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 5,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.953514,
 "grad_norm_max_per_epoch": [
  2.953514,
  0.746235,
  0.707828,
  0.661559,
  0.493266,
  0.633766,
  0.530265,
  0.73621,
  0.435515,
  0.307036,
  0.22377,
  0.192179,
  0.126851,
  0.112139,
  0.105357,
  0.085987,
  0.083551,
  0.08978,
  0.081358,
  0.085634,
  0.082453,
  0.078972,
  0.083598,
  0.083151,
  0.080606,
  0.077371,
  0.081731,
  0.079449,
  0.07778,
  0.077363,
  0.082678,
  0.081325,
  0.077199,
  0.077782,
  0.080502,
  0.077151,
  0.077077,
  0.080252,
  0.076161,
  0.075126,
  0.074256,
  0.074169,
  0.076338,
  0.074317,
  0.076713,
  0.073261,
  0.079657,
  0.074435,
  0.074873,
  0.073256
 ],
 "grad_norm_mean": 0.113833,
 "grad_norm_per_epoch": [
  0.471807,
  0.367416,
  0.33187,
  0.335762,
  0.279371,
  0.277458,
  0.250288,
  0.234089,
  0.204598,
  0.160386,
  0.127559,
  0.105618,
  0.084651,
  0.077562,
  0.070915,
  0.066591,
  0.066195,
  0.065244,
  0.063912,
  0.064005,
  0.064142,
  0.064987,
  0.065615,
  0.065352,
  0.067211,
  0.067163,
  0.068898,
  0.066594,
  0.066958,
  0.066506,
  0.066095,
  0.066228,
  0.065957,
  0.065827,
  0.065892,
  0.065597,
  0.065785,
  0.065304,
  0.065586,
  0.065992,
  0.066259,
  0.066278,
  0.066226,
  0.066641,
  0.066429,
  0.06635,
  0.066743,
  0.066544,
  0.066687,
  0.066502
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025247
  ],
  "last": [
   2e-08
  ],
  "max_observed": [
   0.005
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
 "peak_memory_gb": 9.148,
 "tail_spread_pct_of_best": 0.111,
 "train_seconds_per_epoch": 7.048,
 "train_seconds_total": 352.41,
 "val_seconds_per_epoch": 0.259,
 "val_seconds_total": 12.95,
 "val_share_of_wall": 0.0354
}
```
