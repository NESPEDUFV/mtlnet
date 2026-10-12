# reg-arizona-p0s0

`b761cdd52dc877b0` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **arizona** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 19s |
| 1 | ? | ? | 9s |
| 2 | ? | ? | 9s |
| 3 | ? | ? | 9s |
| 4 | ? | ? | 9s |

## Worth a look

- ties at the decision boundary: [(0, {'top1': 0, 'top5': 0, 'top10': 1})]
- fold wall-clock spread 9s to 19s — one fold took more than twice another, which is usually contention, not data

## Diagnostics

```json
{
 "best_epoch": 36,
 "best_value": 0.64534592628479,
 "clipped_fraction_mean": 0.0716,
 "clipped_fraction_per_epoch": [
  0.2609,
  0.0,
  0.0,
  0.0,
  0.0,
  0.1159,
  0.4638,
  0.3623,
  0.4783,
  0.4638,
  0.5362,
  0.4058,
  0.2609,
  0.1159,
  0.087,
  0.029,
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
 "epochs_to_95pct": 12,
 "epochs_to_99pct": 25,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 1.538046,
 "grad_norm_max_per_epoch": [
  1.538046,
  0.763182,
  0.687367,
  0.863847,
  0.955314,
  1.088643,
  1.379116,
  1.22636,
  1.361219,
  1.335137,
  1.273718,
  1.319214,
  1.186334,
  1.171821,
  1.184628,
  1.05237,
  0.973376,
  0.949651,
  0.912895,
  0.987787,
  0.844091,
  0.941358,
  0.886638,
  0.837946,
  0.870745,
  0.859626,
  0.782528,
  0.797401,
  0.753045,
  0.771389,
  0.749154,
  0.809472,
  0.754622,
  0.751087,
  0.811302,
  0.723808,
  0.744497,
  0.750778,
  0.715012,
  0.783565,
  0.701059,
  0.729171,
  0.723208,
  0.732929,
  0.717794,
  0.703529,
  0.702076,
  0.664471,
  0.739821,
  0.684656
 ],
 "grad_norm_mean": 0.732242,
 "grad_norm_per_epoch": [
  0.941158,
  0.667252,
  0.593353,
  0.657148,
  0.766344,
  0.880482,
  0.987714,
  0.982478,
  1.012403,
  1.002015,
  1.023247,
  0.990839,
  0.941627,
  0.919641,
  0.891598,
  0.847476,
  0.823336,
  0.792073,
  0.759169,
  0.763042,
  0.747641,
  0.742856,
  0.724022,
  0.703428,
  0.686792,
  0.707752,
  0.685127,
  0.676274,
  0.652384,
  0.659405,
  0.665259,
  0.666676,
  0.658337,
  0.633476,
  0.640279,
  0.625031,
  0.635683,
  0.619734,
  0.62712,
  0.616389,
  0.61366,
  0.611182,
  0.608982,
  0.607727,
  0.5978,
  0.590286,
  0.593766,
  0.590406,
  0.585362,
  0.59686
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00015153
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
 "peak_memory_gb": 0.743,
 "tail_spread_pct_of_best": 0.123,
 "train_seconds_per_epoch": 0.353,
 "train_seconds_total": 17.63,
 "val_seconds_per_epoch": 0.033,
 "val_seconds_total": 1.63,
 "val_share_of_wall": 0.0844
}
```
