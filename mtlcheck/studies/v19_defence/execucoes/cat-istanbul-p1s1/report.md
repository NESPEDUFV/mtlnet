# cat-istanbul-p1s1

`f0a36f603cdb5e1f` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **istanbul** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
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
 "best_epoch": 46,
 "best_value": 0.34822455048561096,
 "clipped_fraction_mean": 0.0367,
 "clipped_fraction_per_epoch": [
  0.9583,
  0.2083,
  0.0,
  0.0,
  0.0,
  0.0417,
  0.125,
  0.0,
  0.0,
  0.2083,
  0.0417,
  0.0417,
  0.0417,
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
  0.0833,
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
 "epochs_to_99pct": 21,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 6.732355,
 "grad_norm_max_per_epoch": [
  6.732355,
  1.291008,
  0.847918,
  0.651687,
  0.650475,
  1.000766,
  1.124458,
  0.877004,
  0.970324,
  1.385162,
  1.013884,
  1.521446,
  1.063144,
  1.059187,
  1.038635,
  0.924396,
  0.844321,
  0.679668,
  0.848696,
  0.842845,
  0.682886,
  0.639125,
  0.8741,
  1.34308,
  0.595837,
  0.659119,
  0.809732,
  0.542883,
  0.759147,
  0.713016,
  0.772385,
  0.645179,
  0.54683,
  0.506377,
  0.710801,
  0.480464,
  0.486157,
  0.439106,
  0.541782,
  0.508082,
  0.628759,
  0.606018,
  0.697738,
  0.568432,
  0.502088,
  0.536961,
  0.536749,
  0.560818,
  0.536008,
  0.540253
 ],
 "grad_norm_mean": 0.474617,
 "grad_norm_per_epoch": [
  2.297799,
  0.806142,
  0.557114,
  0.424294,
  0.439695,
  0.469613,
  0.67807,
  0.503843,
  0.605272,
  0.817301,
  0.598367,
  0.576649,
  0.542642,
  0.59636,
  0.463811,
  0.530539,
  0.511585,
  0.457466,
  0.479478,
  0.470121,
  0.401966,
  0.437926,
  0.485164,
  0.627169,
  0.403596,
  0.385872,
  0.496868,
  0.383562,
  0.400723,
  0.41393,
  0.497574,
  0.411689,
  0.3872,
  0.347656,
  0.387996,
  0.337574,
  0.288,
  0.307689,
  0.360923,
  0.351313,
  0.315763,
  0.320873,
  0.295653,
  0.277548,
  0.260069,
  0.280292,
  0.261459,
  0.264497,
  0.256972,
  0.25715
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
 "tail_spread_pct_of_best": 0.414,
 "train_seconds_per_epoch": 0.65,
 "train_seconds_total": 32.51,
 "val_seconds_per_epoch": 0.021,
 "val_seconds_total": 1.04,
 "val_share_of_wall": 0.0309
}
```
