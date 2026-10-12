# cat-florida-p100s100

`31c1b74489290f5d` from `recipes/v19/cat.toml`

## Recipe

- family **cat** · state **florida** · model_seed **100** · split_seed **100** · engine `check2hgi_v18`
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

- ties at the decision boundary: [(0, {'top3': 0, 'top5': 1})]
- every fold peaked in the first third of the schedule (latest was epoch 12 of 50) — a shorter schedule may score HIGHER, not just faster; at alabama that was worth +0.35 pp

## Diagnostics

```json
{
 "best_epoch": 7,
 "best_value": 0.39438870549201965,
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
  "frames_ok": 0,
  "frames_total": 0,
  "graph_breaks": 0,
  "unique_graph_breaks": 0
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
 "grad_norm_max": 4.046538,
 "grad_norm_max_per_epoch": [
  4.046538,
  0.641059,
  0.523954,
  0.920614,
  0.600917,
  0.592687,
  0.583473,
  0.509724,
  0.450813,
  0.567664,
  0.572655,
  0.415643,
  0.358814,
  0.268071,
  0.225525,
  0.215158,
  0.208956,
  0.199061,
  0.138346,
  0.131045,
  0.142369,
  0.113878,
  0.123338,
  0.11808,
  0.124673,
  0.12241,
  0.110882,
  0.112485,
  0.114898,
  0.113867,
  0.111335,
  0.116503,
  0.117763,
  0.12121,
  0.122147,
  0.136134,
  0.129893,
  0.138513,
  0.137253,
  0.143209,
  0.144244,
  0.151551,
  0.150712,
  0.154974,
  0.157058,
  0.162441,
  0.161577,
  0.160314,
  0.163608,
  0.164382
 ],
 "grad_norm_mean": 0.177413,
 "grad_norm_per_epoch": [
  0.533424,
  0.384653,
  0.343456,
  0.422828,
  0.389619,
  0.342911,
  0.322869,
  0.303713,
  0.259353,
  0.26391,
  0.268893,
  0.219964,
  0.207837,
  0.16958,
  0.149947,
  0.143925,
  0.132667,
  0.120502,
  0.114508,
  0.108284,
  0.104698,
  0.101989,
  0.100478,
  0.099038,
  0.100405,
  0.099628,
  0.099041,
  0.100293,
  0.101137,
  0.10241,
  0.104471,
  0.106488,
  0.109732,
  0.111896,
  0.11367,
  0.118685,
  0.120812,
  0.12524,
  0.128666,
  0.133101,
  0.136522,
  0.140249,
  0.144083,
  0.146902,
  0.149824,
  0.151857,
  0.153471,
  0.154146,
  0.154159,
  0.154726
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
 "tail_spread_pct_of_best": 0.122,
 "train_seconds_per_epoch": 3.107,
 "train_seconds_total": 155.34,
 "val_seconds_per_epoch": 0.108,
 "val_seconds_total": 5.4,
 "val_share_of_wall": 0.0336
}
```
