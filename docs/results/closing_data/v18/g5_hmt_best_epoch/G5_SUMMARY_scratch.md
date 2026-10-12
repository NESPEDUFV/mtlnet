# G5: HMT-GRN-style at its best epoch, 2026-10-01 (M2 Pro, MPS)

**Run.** `scripts/baselines/b3_hmt_grn.py --state <st> --seed 0 --folds 5 --epochs 50 --engine check2hgi_dk_ovl
--epoch-select per_task`, at commit 82dbe843. Inputs (`check2hgi_dk_ovl` next, next_region and sequences_next)
are md5-equal to nespedgpu. `OUTPUT_DIR`, `DATA_ROOT` and `RESULTS_ROOT` point at this scratch root.

**Selection.** `per_task` evaluates after every epoch on the **evaluation fold** and reports each head at its own
best epoch: category macro-F1 at the cat-best epoch, region Acc@10-indist at the reg-best epoch. This is the same
diag-best convention as the printed dedicated cells. Each JSON also keeps the epoch-50 block (`last_epoch`) and
the full per-epoch history.

**Folds.** HMT's split equals train.py's delivered folds 5/5 at AL, AZ and IST (int64 StratifiedGroupKFold on the
same rows), asserted before training.

**Patch check, AL fold 0.** The per-epoch evaluation does not change training. The train loss is identical at
every epoch across `none` ×2 and `per_task` ×2. The epoch-50 values equal `none` exactly in 2 of 2 comparisons
after the first. The first `per_task` run's epoch-50 category value differed by 0.054 pp (evaluation-time MPS
numeric noise; region was identical; it did not reproduce).

| state | cat, best epoch | reg Acc@10, best epoch | cat / reg at epoch 50 (this run) | printed June (epoch 50) |
|---|---|---|---|---|
| AL | **20.99** ± 1.05 (ep 13–29) | **63.19** ± 3.67 (ep 8–11) | 19.32 / 57.13 | 19.37 / 57.05 |
| AZ | **22.09** ± 0.73 (ep 13–17) | **52.11** ± 1.56 (ep 5–7) | 18.54 / 43.91 | 18.04 / 43.70 |
| IST | **24.85** ± 0.66 (ep 8–20) | **68.06** ± 0.79 (ep 9–12) | 19.10 / 60.44 | 19.10 / 60.42 |

Epoch 50 on today's folds reproduces the printed June cells (category within 0.5, region within 0.2), so the
printed cells read an over-trained epoch. HMT peaks early and degrades by epoch 50.

**Resources.** AL 163 s, AZ 347 s, IST 407 s; peak RSS ≤ 1.0 GB; no swap growth.
