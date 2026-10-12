# reg-istanbul-p7s7

`10cb523e036433ab` from `recipes/v19/reg.toml`

## Recipe

- family **reg** · state **istanbul** · model_seed **7** · split_seed **7** · engine `check2hgi_v18`
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
| 3 | ? | ? | 11s |
| 4 | ? | ? | 11s |

## Worth a look

- ties at the decision boundary: [(4, {'top1': 0, 'top5': 1, 'top10': 0})]

## Diagnostics

```json
{
 "best_epoch": 46,
 "best_value": 0.746493935585022,
 "clipped_fraction_mean": 0.1026,
 "clipped_fraction_per_epoch": [
  0.7419,
  0.0,
  0.043,
  0.1505,
  0.3548,
  0.6237,
  0.5484,
  0.6452,
  0.6237,
  0.5914,
  0.2903,
  0.2581,
  0.1183,
  0.0968,
  0.0215,
  0.0108,
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
 "grad_norm_max": 2.330233,
 "grad_norm_max_per_epoch": [
  2.330233,
  0.899522,
  1.255464,
  1.221477,
  1.26308,
  1.433377,
  1.367333,
  1.457808,
  1.439049,
  1.429479,
  1.246768,
  1.457303,
  1.186736,
  1.095463,
  1.0619,
  1.006488,
  1.009855,
  0.883506,
  0.864198,
  0.821,
  0.798169,
  0.755207,
  0.702564,
  0.691621,
  0.73902,
  0.705347,
  0.68742,
  0.664811,
  0.722232,
  0.633764,
  0.687705,
  0.683543,
  0.636789,
  0.613111,
  0.624167,
  0.638265,
  0.601228,
  0.599701,
  0.616699,
  0.626192,
  0.593326,
  0.573044,
  0.58986,
  0.607285,
  0.577223,
  0.578162,
  0.563213,
  0.527914,
  0.529636,
  0.541982
 ],
 "grad_norm_mean": 0.665097,
 "grad_norm_per_epoch": [
  1.277795,
  0.726424,
  0.727332,
  0.871789,
  0.957405,
  1.048607,
  1.033863,
  1.070724,
  1.052773,
  1.02165,
  0.953816,
  0.956452,
  0.877521,
  0.855085,
  0.79888,
  0.761956,
  0.732425,
  0.677828,
  0.666695,
  0.634828,
  0.626596,
  0.601056,
  0.591215,
  0.569901,
  0.584451,
  0.571512,
  0.54779,
  0.540886,
  0.54402,
  0.534196,
  0.528534,
  0.517655,
  0.521015,
  0.51143,
  0.504297,
  0.508459,
  0.499388,
  0.50617,
  0.507,
  0.480015,
  0.489939,
  0.485639,
  0.484033,
  0.483402,
  0.481033,
  0.470665,
  0.467087,
  0.466629,
  0.464903,
  0.462075
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
 "tail_spread_pct_of_best": 0.049,
 "train_seconds_per_epoch": 0.207,
 "train_seconds_total": 10.34,
 "val_seconds_per_epoch": 0.011,
 "val_seconds_total": 0.55,
 "val_share_of_wall": 0.0505
}
```
