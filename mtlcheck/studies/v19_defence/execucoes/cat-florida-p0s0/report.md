# cat-florida-p0s0

`4d2f4f9c08aa3f03` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **florida** · model_seed **0** · split_seed **0** · engine `check2hgi_v18`
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

- every fold peaked in the first third of the schedule (latest was epoch 11 of 50) — a shorter schedule may score HIGHER, not just faster; at alabama that was worth +0.35 pp

## Diagnostics

```json
{
 "best_epoch": 11,
 "best_value": 0.3872221112251282,
 "clipped_fraction_mean": 0.0009,
 "clipped_fraction_per_epoch": [
  0.0459,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
  0.0,
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
 "grad_norm_max": 3.989495,
 "grad_norm_max_per_epoch": [
  3.989495,
  0.647285,
  0.641118,
  0.813761,
  0.600872,
  0.693247,
  0.541737,
  0.488671,
  0.467151,
  0.401718,
  0.435849,
  0.3929,
  0.315095,
  0.312939,
  0.270524,
  0.184111,
  0.16218,
  0.16066,
  0.147223,
  0.155872,
  0.137093,
  0.123416,
  0.116654,
  0.126086,
  0.121827,
  0.12472,
  0.121914,
  0.111585,
  0.115861,
  0.110287,
  0.113654,
  0.11434,
  0.119769,
  0.117,
  0.124191,
  0.122343,
  0.126103,
  0.133091,
  0.138478,
  0.144042,
  0.147909,
  0.154794,
  0.154896,
  0.15647,
  0.158728,
  0.167217,
  0.159476,
  0.16424,
  0.163075,
  0.163254
 ],
 "grad_norm_mean": 0.176244,
 "grad_norm_per_epoch": [
  0.506402,
  0.39141,
  0.400987,
  0.402807,
  0.336715,
  0.346458,
  0.301884,
  0.301129,
  0.298987,
  0.254194,
  0.254596,
  0.224903,
  0.197481,
  0.180213,
  0.151107,
  0.134815,
  0.124311,
  0.116801,
  0.112805,
  0.10716,
  0.104747,
  0.1015,
  0.098653,
  0.098403,
  0.098848,
  0.10078,
  0.100147,
  0.100289,
  0.101127,
  0.102403,
  0.104444,
  0.106627,
  0.108608,
  0.110543,
  0.113994,
  0.116967,
  0.119872,
  0.124722,
  0.128963,
  0.133705,
  0.13659,
  0.141484,
  0.14496,
  0.147468,
  0.150511,
  0.152659,
  0.15374,
  0.154164,
  0.155201,
  0.154933
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
 "peak_memory_gb": 5.584,
 "tail_spread_pct_of_best": 0.214,
 "train_seconds_per_epoch": 3.104,
 "train_seconds_total": 155.2,
 "val_seconds_per_epoch": 0.108,
 "val_seconds_total": 5.39,
 "val_share_of_wall": 0.0335
}
```
