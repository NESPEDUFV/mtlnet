# reg-florida-p0s0

`534adacafd54ca0d` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **florida** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 64s |
| 1 | ? | ? | 64s |
| 2 | ? | ? | 63s |
| 3 | ? | ? | 63s |
| 4 | ? | ? | 63s |

## Worth a look

- ties at the decision boundary: [(0, {'top1': 0, 'top5': 1, 'top10': 0}), (1, {'top1': 0, 'top5': 0, 'top10': 1}), (2, {'top1': 1, 'top5': 1, 'top10': 1}), (3, {'top1': 0, 'top5': 1, 'top10': 0}), (4, {'top1': 0, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 47,
 "best_value": 0.7669509649276733,
 "clipped_fraction_mean": 0.0752,
 "clipped_fraction_per_epoch": [
  0.4381,
  0.0,
  0.0115,
  0.1789,
  0.4954,
  0.6972,
  0.695,
  0.6284,
  0.3807,
  0.1927,
  0.0298,
  0.0092,
  0.0023,
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
  "frames_ok": 3,
  "frames_total": 3,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 5,
 "epochs_to_99pct": 22,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 4.602212,
 "grad_norm_max_per_epoch": [
  4.602212,
  0.82739,
  1.037619,
  1.181009,
  1.34688,
  1.351426,
  1.37169,
  1.300782,
  1.253766,
  1.183768,
  1.096731,
  1.044147,
  1.001562,
  0.896231,
  0.865774,
  0.79216,
  0.770034,
  0.801299,
  0.685632,
  0.645404,
  0.630599,
  0.61998,
  0.595659,
  0.594923,
  0.572428,
  0.548573,
  0.537104,
  0.556508,
  0.565766,
  0.537188,
  0.535243,
  0.52733,
  0.512045,
  0.499364,
  0.523415,
  0.51372,
  0.525572,
  0.544495,
  0.570009,
  0.521099,
  0.505885,
  0.518411,
  0.499762,
  0.520658,
  0.50082,
  0.490367,
  0.497933,
  0.522583,
  0.49953,
  0.4995
 ],
 "grad_norm_mean": 0.574197,
 "grad_norm_per_epoch": [
  1.13325,
  0.645511,
  0.795241,
  0.92657,
  1.000707,
  1.049228,
  1.053327,
  1.031813,
  0.983464,
  0.923327,
  0.852062,
  0.787522,
  0.739315,
  0.693055,
  0.65302,
  0.610699,
  0.58992,
  0.559636,
  0.535102,
  0.520587,
  0.504702,
  0.491292,
  0.479192,
  0.469883,
  0.459558,
  0.448727,
  0.443156,
  0.436492,
  0.429618,
  0.429643,
  0.426245,
  0.418557,
  0.414454,
  0.414139,
  0.407689,
  0.408032,
  0.408049,
  0.403021,
  0.405222,
  0.400977,
  0.397281,
  0.397159,
  0.397797,
  0.395586,
  0.394828,
  0.389045,
  0.390355,
  0.388046,
  0.390058,
  0.387694
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015148
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
 "peak_memory_gb": 3.167,
 "tail_spread_pct_of_best": 0.059,
 "train_seconds_per_epoch": 1.194,
 "train_seconds_total": 59.69,
 "val_seconds_per_epoch": 0.079,
 "val_seconds_total": 3.96,
 "val_share_of_wall": 0.0622
}
```
