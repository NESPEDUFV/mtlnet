# reg-istanbul-p1s1

`91ee4d9245587f12` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 11s |
| 1 | ? | ? | 11s |
| 2 | ? | ? | 11s |
| 3 | ? | ? | 12s |
| 4 | ? | ? | 12s |

## Worth a look

- selection landed on the FIRST or LAST epoch in fold(s) [4] — the schedule is probably mis-sized (50 epochs)

## Diagnostics

```json
{
 "best_epoch": 41,
 "best_value": 0.7484725713729858,
 "clipped_fraction_mean": 0.108,
 "clipped_fraction_per_epoch": [
  0.6237,
  0.0,
  0.0108,
  0.1828,
  0.5269,
  0.6559,
  0.6452,
  0.7634,
  0.5484,
  0.4624,
  0.3871,
  0.2796,
  0.1398,
  0.129,
  0.0323,
  0.0,
  0.0108,
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
 "epochs_to_95pct": 6,
 "epochs_to_99pct": 22,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.756854,
 "grad_norm_max_per_epoch": [
  2.756854,
  0.853698,
  1.010953,
  1.234173,
  1.324616,
  1.37925,
  1.481646,
  1.551066,
  1.486186,
  1.313938,
  1.439007,
  1.183645,
  1.142241,
  1.18363,
  1.030465,
  0.948088,
  1.119821,
  0.970991,
  0.824428,
  0.945309,
  0.783973,
  0.761107,
  0.724883,
  0.729266,
  0.727311,
  0.723059,
  0.667884,
  0.718286,
  0.667806,
  0.695668,
  0.644628,
  0.646873,
  0.643511,
  0.685535,
  0.712012,
  0.61365,
  0.610628,
  0.592025,
  0.619007,
  0.577455,
  0.568104,
  0.565126,
  0.603125,
  0.545248,
  0.58368,
  0.563401,
  0.554114,
  0.546242,
  0.557701,
  0.546346
 ],
 "grad_norm_mean": 0.666939,
 "grad_norm_per_epoch": [
  1.24768,
  0.704386,
  0.734307,
  0.872761,
  1.016309,
  1.050531,
  1.078082,
  1.096481,
  1.019811,
  1.000003,
  0.987225,
  0.934518,
  0.877737,
  0.845121,
  0.790144,
  0.759975,
  0.716761,
  0.688078,
  0.658919,
  0.652522,
  0.623727,
  0.622581,
  0.598876,
  0.587688,
  0.572216,
  0.554934,
  0.548632,
  0.558662,
  0.522943,
  0.542719,
  0.530929,
  0.53148,
  0.516073,
  0.522508,
  0.507012,
  0.505746,
  0.503788,
  0.495083,
  0.495337,
  0.491388,
  0.495,
  0.492268,
  0.482034,
  0.481592,
  0.478316,
  0.481669,
  0.473098,
  0.469546,
  0.468569,
  0.461206
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015151
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
 "peak_memory_gb": 0.874,
 "tail_spread_pct_of_best": 0.029,
 "train_seconds_per_epoch": 0.208,
 "train_seconds_total": 10.41,
 "val_seconds_per_epoch": 0.011,
 "val_seconds_total": 0.55,
 "val_share_of_wall": 0.0506
}
```
