# cat-texas-p1s1

`62a60be12331fec4` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **texas** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 479s |
| 1 | ? | ? | 479s |
| 2 | ? | ? | 479s |
| 3 | ? | ? | 479s |
| 4 | ? | ? | 479s |

## Worth a look

- ties at the decision boundary: [(3, {'top3': 1, 'top5': 1})]

## Diagnostics

```json
{
 "best_epoch": 46,
 "best_value": 0.3653697371482849,
 "clipped_fraction_mean": 0.001,
 "clipped_fraction_per_epoch": [
  0.0488,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
 },
 "epochs_to_95pct": 1,
 "epochs_to_99pct": 6,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 7.432402,
 "grad_norm_max_per_epoch": [
  7.432402,
  0.689976,
  0.690634,
  0.495484,
  0.568265,
  0.459097,
  0.472678,
  0.432138,
  0.350828,
  0.247302,
  0.163717,
  0.132323,
  0.129385,
  0.098522,
  0.102654,
  0.100654,
  0.101959,
  0.102593,
  0.10706,
  0.106805,
  0.106012,
  0.106333,
  0.114354,
  0.116352,
  0.117908,
  0.117367,
  0.109521,
  0.111046,
  0.10875,
  0.118721,
  0.118438,
  0.111363,
  0.115274,
  0.120654,
  0.109761,
  0.118459,
  0.12453,
  0.107712,
  0.108113,
  0.117719,
  0.108004,
  0.117572,
  0.108818,
  0.108008,
  0.114851,
  0.106857,
  0.12075,
  0.11258,
  0.119651,
  0.119147
 ],
 "grad_norm_mean": 0.105118,
 "grad_norm_per_epoch": [
  0.475329,
  0.337308,
  0.331559,
  0.279157,
  0.267014,
  0.240246,
  0.241829,
  0.205283,
  0.164777,
  0.123737,
  0.095869,
  0.079456,
  0.070525,
  0.065135,
  0.061143,
  0.060285,
  0.060319,
  0.06131,
  0.062857,
  0.06236,
  0.063607,
  0.063577,
  0.065351,
  0.066262,
  0.066297,
  0.064683,
  0.066624,
  0.065835,
  0.065269,
  0.067312,
  0.068175,
  0.064829,
  0.065971,
  0.065599,
  0.065432,
  0.063807,
  0.06363,
  0.062498,
  0.062055,
  0.062242,
  0.061601,
  0.062158,
  0.061113,
  0.061319,
  0.060995,
  0.061022,
  0.06095,
  0.060776,
  0.060836,
  0.060562
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
 "peak_memory_gb": 11.101,
 "tail_spread_pct_of_best": 0.087,
 "train_seconds_per_epoch": 9.22,
 "train_seconds_total": 461.01,
 "val_seconds_per_epoch": 0.344,
 "val_seconds_total": 17.21,
 "val_share_of_wall": 0.036
}
```
