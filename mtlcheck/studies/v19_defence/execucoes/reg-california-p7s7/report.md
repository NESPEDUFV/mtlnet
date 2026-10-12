# reg-california-p7s7

`c21cac50115126c6` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **california** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 174s |
| 1 | ? | ? | 174s |
| 2 | ? | ? | 175s |
| 3 | ? | ? | 175s |
| 4 | ? | ? | 174s |

## Worth a look

- ties at the decision boundary: [(0, {'top1': 1, 'top5': 1, 'top10': 1}), (1, {'top1': 0, 'top5': 1, 'top10': 1}), (2, {'top1': 2, 'top5': 1, 'top10': 1}), (3, {'top1': 1, 'top5': 1, 'top10': 1}), (4, {'top1': 1, 'top5': 1, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 47,
 "best_value": 0.6275935769081116,
 "clipped_fraction_mean": 0.1575,
 "clipped_fraction_per_epoch": [
  0.008,
  0.115,
  0.796,
  1.0,
  1.0,
  1.0,
  1.0,
  0.999,
  0.961,
  0.713,
  0.247,
  0.032,
  0.002,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 5,
 "epochs_to_99pct": 30,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.854972,
 "grad_norm_max_per_epoch": [
  1.111187,
  1.288956,
  1.465121,
  1.756323,
  1.831113,
  1.803401,
  1.854972,
  1.716754,
  1.564076,
  1.401291,
  1.231562,
  1.074031,
  1.07744,
  0.964986,
  0.860545,
  0.809415,
  0.806269,
  0.755292,
  0.738672,
  0.704328,
  0.690122,
  0.698723,
  0.684222,
  0.632161,
  0.648181,
  0.635641,
  0.676804,
  0.624262,
  0.590508,
  0.605751,
  0.611846,
  0.575478,
  0.584512,
  0.577781,
  0.560031,
  0.577832,
  0.583871,
  0.573752,
  0.571379,
  0.565288,
  0.567951,
  0.547651,
  0.557404,
  0.557905,
  0.552409,
  0.556595,
  0.562392,
  0.54344,
  0.565608,
  0.550709
 ],
 "grad_norm_mean": 0.658241,
 "grad_norm_per_epoch": [
  0.625808,
  0.852932,
  1.098899,
  1.293024,
  1.398161,
  1.415822,
  1.382163,
  1.284553,
  1.179462,
  1.057671,
  0.942957,
  0.8507,
  0.77793,
  0.724264,
  0.674031,
  0.634761,
  0.609713,
  0.585722,
  0.568324,
  0.552553,
  0.538092,
  0.531686,
  0.520799,
  0.510571,
  0.506796,
  0.498913,
  0.498709,
  0.493227,
  0.488919,
  0.484957,
  0.483009,
  0.479139,
  0.481815,
  0.476439,
  0.475514,
  0.475685,
  0.47268,
  0.469921,
  0.469339,
  0.467312,
  0.46569,
  0.463541,
  0.461013,
  0.461489,
  0.457336,
  0.45633,
  0.455443,
  0.453456,
  0.451675,
  0.453103
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015147
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
 "peak_memory_gb": 6.868,
 "tail_spread_pct_of_best": 0.045,
 "train_seconds_per_epoch": 3.184,
 "train_seconds_total": 159.19,
 "val_seconds_per_epoch": 0.287,
 "val_seconds_total": 14.35,
 "val_share_of_wall": 0.0827
}
```
