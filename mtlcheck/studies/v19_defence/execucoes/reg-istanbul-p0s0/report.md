# reg-istanbul-p0s0

`eb3da881d4f2b999` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
- 50 epochs · batch 2048 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.003
- reg head `next_stan_flow` {'d_model': 128, 'num_heads': 4, 'dropout': 0.3, 'seq_length': 9, 'freeze_alpha': True, 'alpha_init': 0.0}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 20s |
| 1 | ? | ? | 11s |
| 2 | ? | ? | 11s |
| 3 | ? | ? | 11s |
| 4 | ? | ? | 11s |

## Worth a look

- ties at the decision boundary: [(3, {'top1': 0, 'top5': 0, 'top10': 1})]

## Diagnostics

```json
{
 "best_epoch": 42,
 "best_value": 0.7406412363052368,
 "clipped_fraction_mean": 0.0959,
 "clipped_fraction_per_epoch": [
  0.6452,
  0.0,
  0.0108,
  0.1398,
  0.3011,
  0.5591,
  0.7849,
  0.5914,
  0.5161,
  0.4839,
  0.3871,
  0.1505,
  0.1398,
  0.043,
  0.0215,
  0.0215,
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
 "epochs_to_95pct": 6,
 "epochs_to_99pct": 23,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 2.490927,
 "grad_norm_max_per_epoch": [
  2.490927,
  0.824813,
  1.054753,
  1.226587,
  1.390749,
  1.413763,
  1.47719,
  1.327592,
  1.40129,
  1.270161,
  1.414103,
  1.141821,
  1.196726,
  1.218783,
  1.106829,
  1.079147,
  0.99617,
  0.837898,
  0.821727,
  0.838964,
  0.75993,
  0.745142,
  0.798925,
  0.757677,
  0.769297,
  0.652283,
  0.700699,
  0.653571,
  0.648794,
  0.634097,
  0.652485,
  0.623412,
  0.644522,
  0.650029,
  0.644477,
  0.605585,
  0.594965,
  0.621026,
  0.628058,
  0.588676,
  0.587748,
  0.612943,
  0.559511,
  0.552124,
  0.568712,
  0.546813,
  0.569839,
  0.559171,
  0.535859,
  0.550828
 ],
 "grad_norm_mean": 0.658398,
 "grad_norm_per_epoch": [
  1.236528,
  0.681495,
  0.697096,
  0.879243,
  0.957731,
  1.040157,
  1.08115,
  1.040775,
  1.026322,
  1.002218,
  0.98455,
  0.879618,
  0.875333,
  0.848848,
  0.772395,
  0.744421,
  0.724423,
  0.656851,
  0.660434,
  0.631633,
  0.60376,
  0.599238,
  0.606199,
  0.575908,
  0.571758,
  0.56168,
  0.556785,
  0.545306,
  0.534823,
  0.521337,
  0.522753,
  0.505848,
  0.520185,
  0.513485,
  0.519177,
  0.501761,
  0.495799,
  0.504452,
  0.496486,
  0.495629,
  0.488603,
  0.488636,
  0.472693,
  0.475828,
  0.472983,
  0.471748,
  0.476085,
  0.469904,
  0.464444,
  0.465386
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
 "peak_memory_gb": 0.931,
 "tail_spread_pct_of_best": 0.035,
 "train_seconds_per_epoch": 0.366,
 "train_seconds_total": 18.31,
 "val_seconds_per_epoch": 0.035,
 "val_seconds_total": 1.76,
 "val_share_of_wall": 0.0877
}
```
