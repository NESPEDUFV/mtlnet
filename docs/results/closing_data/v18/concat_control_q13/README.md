# Q13 concatenation control: per-fold run records (provenance for the printed values)

**What this is.** The run records behind the Q13 re-run of the feature-concatenation control
(2026-08-16, nespedgpu), which the author approved to replace the A2 values in Ch. 5 (A2 swap, main
commit `e6ac03c0`). The study's narrative is
`articles/dissertacao/wrapup/post_submission_studies/Q13_concatenation_control.md`.

**Copied 2026-10-01**, read-only, from `~/PoiMtlNet/results/<engine>/<state>/<rundir>/` on nespedgpu.
For each run, only `metrics/` (per-epoch train and val CSVs), `summary/` and `folds/` (per-fold
reports) were copied. Model weights, plots and diagnostics were not. Each run directory carries a
`SOURCE_RUNDIR.txt` with its origin. The driver scripts and their logs come from `wave_logs/`, which is
no longer in the box's working tree; it was read from the stash
`stash@{0}^3:wave_logs/` ("pre-pull-2026-09-08-worker-session"). `MANIFEST.md5` lists every file.

**Metric.** Category macro-F1 at the f1-best epoch of each fold (the `f1` column of
`metrics/fold*_next_val.csv`), the same rule as `scripts/closing_data/score_stl_cat_ceiling.py`. Every
value below was re-computed from the copied CSVs and matches the study document exactly.

## Recipe (all kept runs)

`scripts/train.py --task next --model next_gru --folds 5 --epochs 50 --seed 0 --batch-size 8192
--max-lr <per state> --logit-adjust-tau 0.5`, fp32, `compile + tf32`, CUDA. `max_lr`: AL 0.0025,
AZ 0.0005, FL 0.005, which is the v18 recipe of Table 9. Engines: place = `hgi_dk_ovl`,
place + features = `hgi_ovl_feat`, check-in = `check2hgi_v18`, all on the `dk_ovl` stride-1 rows.
The three arms of each state ran in the same session, so the comparison is between this study's own
re-runs and not against the printed cells directly.

## Q13 (kept) against A2 (the formerly printed source)

| | Q13 (this directory) | A2 pre-freeze (`docs/results/P1/region_head_<st>_checkin_5f_30ep_A2_{hgi,hgifeat}_category_s<S>.json`) |
|---|---|---|
| protocol | train.py, Table-9 recipe above, seed 0, 50 ep | `p1_region_head_ablation.py` harness, stride-9 rows, `max_lr` 0.003 for all states, no logit adjustment, 30 ep; AL/AZ seeds {0,1,7,100}, FL seed 0 only |
| AL place / +feat / check-in | 29.148 / **30.882** / 30.706 → gain **+1.734** | per seed hgi→hgifeat gains 2.52 / 1.66 / 1.75 / 2.16 → **+2.02** |
| AZ | 31.995 / **33.697** / 34.499 → **+1.702** | 1.69 / 1.34 / 1.88 / 1.68 → **+1.65** (printed +1.7) |
| FL | 37.152 / **38.171** / 37.360 → **+1.018** | 36.21 → 37.04 → **+0.83** |

Per fold (kept runs; folds 1–5):

| state | place | place + features | check-in |
|---|---|---|---|
| AL | 29.7261 29.7418 28.0495 28.4391 29.7841 | 31.4458 30.7062 29.5651 30.3514 32.3415 | 32.1877 30.5409 29.4363 29.6200 31.7439 |
| AZ | 32.0441 32.1028 30.9261 31.1953 33.7081 | 33.9335 33.8112 32.8798 32.6200 35.2394 | 34.4036 35.4742 33.2737 33.5472 35.7970 |
| FL | 37.4655 36.8728 36.6941 37.6142 37.1154 | 38.7017 37.7746 37.6127 38.5846 38.1804 | 37.8042 37.2933 36.6961 37.5676 37.4398 |

## Fidelity against Table 9 (`docs/results/closing_data/v18_place_level/` and the v18 seed-0 cells)

- **AL place: exact.** It reproduces the table's record fold by fold (29.7261 / 29.7418 / 28.0495 /
  28.4391 / 29.7841 = 29.1481).
- **AZ place: open.** The mean is within 0.07 (31.9953 against 31.9278), but per fold it differs by up
  to **0.19**, with alternating sign. Training is deterministic: `determinism/arizona_place_repeatA`
  and `repeatB` are identical in every fold and every epoch. So the difference from the 2026-08-11
  record is a real input or configuration difference, not yet identified.
- **FL place: open.** 37.1524 against 37.1301 (per fold up to 0.09).

## Discarded runs (kept here as records, NOT results)

| dir | source rundir | why | mean |
|---|---|---|---:|
| `runs/discarded/alabama_place_wrongrecipe_1` | `…_bs2048_ep50_20260816_190800_2727580` | wrong recipe (batch 2048) | 26.5631 |
| `runs/discarded/alabama_place_wrongrecipe_2` | `…_bs8192_ep50_20260816_191111_2728917` | wrong recipe, recipe search before the fidelity control matched | 26.1827 |

Also discarded and **not copied**: the first-wave Arizona runs (`…_192739`, `…_193234`, `…_193734`)
and the first-wave Florida runs (`…_202612`, `…_205625`, the latter partial). All used Alabama's
`max_lr` 0.0025 (see `drivers/driver_q13_final.sh`, `drivers/driver_q13_fl.sh`) and were re-run in
`drivers/driver_q13_lr.sh` with the per-state rate. The kept AZ and FL runs come from that wave.

## Drivers

| file | wave |
|---|---|
| `drivers/driver_q13_final.sh` + `DRIVER_q13_final.log` | AL feat/check-in (kept), AZ ×3 at 0.0025 (discarded) |
| `drivers/driver_q13_fl.sh` + `DRIVER_q13_fl.log` | FL at 0.0025 (discarded) |
| `drivers/driver_q13_lr.sh` + `DRIVER_q13_lr.log` | AZ and FL with per-state `max_lr` (kept) |

The AL place kept run (`…_191511`) predates these three logs. It is the run whose per-fold values equal
Table 9 exactly.

Uncommitted. `docs/results/` is hidden by `.git/info/exclude` on the laptop, so committing needs
`git add -f docs/results/closing_data/v18/concat_control_q13/`.
