# cat-florida-p1s1

`ba1963708eeef043` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **florida** · model_seed **1** · split_seed **1** · engine `check2hgi_v18`
- 50 epochs · batch 8192 · 5 folds · precision fp32
- scheduler onecycle · max_lr 0.005
- cat head `next_gru` {'hidden_dim': 256, 'num_layers': 4, 'dropout': 0.1}

## Result

**Sealed.** The outer-test metric is not computed here — `mtlcheck compare` reads
the persisted predictions. See `docs/plans/EVALUATION_IMPLEMENTATION.md` §1.

Joint cell — two metrics, no single aggregate.

| fold | cat macro-F1 | reg Acc@10 | wall |
|---:|---:|---:|---:|
| 0 | ? | ? | 161s |
| 1 | ? | ? | 161s |
| 2 | ? | ? | 160s |
| 3 | ? | ? | 160s |
| 4 | ? | ? | 160s |

## Worth a look

- every fold peaked in the first third of the schedule (latest was epoch 12 of 50) — a shorter schedule may score HIGHER, not just faster; at alabama that was worth +0.35 pp

## Diagnostics

```json
{
 "best_epoch": 12,
 "best_value": 0.3734094202518463,
 "clipped_fraction_mean": 0.002,
 "clipped_fraction_per_epoch": [
  0.1009,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "epochs_to_99pct": 7,
 "execution": {
  "compiled": true,
  "device": "cuda",
  "precision": "fp32",
  "probe": "n/a (no shared trunk)",
  "tf32": true
 },
 "grad_norm_max": 7.324234,
 "grad_norm_max_per_epoch": [
  7.324234,
  0.760631,
  0.681789,
  0.694058,
  0.591473,
  0.670042,
  0.502205,
  0.565042,
  0.510408,
  0.500638,
  0.43714,
  0.36566,
  0.313742,
  0.328549,
  0.2267,
  0.230994,
  0.175514,
  0.173223,
  0.178487,
  0.151376,
  0.126817,
  0.1326,
  0.13363,
  0.122233,
  0.115557,
  0.129929,
  0.111768,
  0.111735,
  0.114864,
  0.113867,
  0.115636,
  0.115284,
  0.11777,
  0.124196,
  0.12364,
  0.124708,
  0.129564,
  0.132648,
  0.137536,
  0.142903,
  0.145747,
  0.151726,
  0.153304,
  0.157814,
  0.156725,
  0.161239,
  0.16776,
  0.161363,
  0.1641,
  0.160216
 ],
 "grad_norm_mean": 0.180765,
 "grad_norm_per_epoch": [
  0.618797,
  0.433281,
  0.4109,
  0.372253,
  0.335459,
  0.346009,
  0.320889,
  0.312379,
  0.280007,
  0.271468,
  0.273574,
  0.226448,
  0.193786,
  0.177637,
  0.156152,
  0.142272,
  0.129418,
  0.118034,
  0.119501,
  0.114026,
  0.105182,
  0.104112,
  0.101204,
  0.101292,
  0.098016,
  0.101896,
  0.100263,
  0.100414,
  0.102804,
  0.104385,
  0.10518,
  0.106787,
  0.109641,
  0.11154,
  0.115026,
  0.117873,
  0.121608,
  0.125312,
  0.12885,
  0.133656,
  0.13715,
  0.140948,
  0.144664,
  0.147584,
  0.14969,
  0.152608,
  0.153831,
  0.15469,
  0.155035,
  0.154731
 ],
 "lr_per_group_at_epoch_end": {
  "first": [
   0.00025251
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
 "peak_memory_gb": 5.583,
 "tail_spread_pct_of_best": 0.204,
 "train_seconds_per_epoch": 3.115,
 "train_seconds_total": 155.73,
 "val_seconds_per_epoch": 0.109,
 "val_seconds_total": 5.43,
 "val_share_of_wall": 0.0337
}
```
