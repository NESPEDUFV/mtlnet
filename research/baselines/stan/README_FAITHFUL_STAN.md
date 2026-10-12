# Faithful STAN baseline (next-region) — implementation + run guide

Faithful reimplementation of **STAN** (Luo, Liu, Liu — *Spatio-Temporal Attention Network for Next
Location Recommendation*, WWW 2021; arXiv:2102.04095; reference repo
`yingtaoluo/Spatial-Temporal-Attention-Network-for-POI-Recommendation`), adapted to our
**next-region** task and run on our data + seed-0 user-disjoint 5-fold split. It is STAN's OWN
embeddings + OWN sequence construction + OWN spatio-temporal interval attention, learned **from raw**
(NOT fed our HGI/Check2HGI substrate — that is a separate, optional `stl_hgi` ablation).

> **Correction (2026-10-01):** "our seed-0 user-disjoint 5-fold split" was the intent, never implemented. `train.py` (`run()`)
> builds its own seed-0 user-grouped `StratifiedGroupKFold` over STAN's own rows (`etl.py`: prefix expansion,
> `MIN_HISTORY = 5`), so STAN's rows and folds are not the ones our models use.

Files: `model.py` (architecture), `etl.py` (data → windows), `train.py` (5-fold trainer),
`profile_forward.py` (perf observer). Audit table: `../../../docs/baselines/next_region/stan.md`.

---

## 1. Why a rewrite (the audit)

The prior **v4** numbers (AL 34.46 / AZ 38.96, below the Markov floor) were a **COLLAPSE artifact** —
do not cite. A two-agent audit vs the paper + reference code, then an independent code review (verdict
GO), found and fixed **six faithfulness/correctness gaps**:

| # | Component | Was (v4) | Fixed to (reference) |
|---|---|---|---|
| 1 | **Matching layer** | additive Δd bias + softmax-mean over positions | **multiplicative** Δd gate (`content * bias`) + learned **`Linear(seq,1)`** position collapse, **no softmax** (`layers.Attn`) — was collapsing to a proximity prior |
| 2 | **Embedding init** | std 0.02 (+ `/√d`) → content ~25× below the bias at init (dead channel) | std ≈ `1/√d` |
| 3 | **`/√d` scaling** | divided QKᵀ / content by √d | removed (reference omits it) |
| 4 | **Sequence construction** | non-overlapping **stride-9** windows, 1 target/window (~9× data-starved + biased) | STAN-native **prefix-expansion**: every position t from its causal prefix, `CONTEXT_LEN` cap |
| 5 | **Convergence** | 50 ep **OneCycleLR** → LR≈0 by ep50, "best@49/50" never plateaued | **constant LR + early-stop** (patience 20, cap 200); best-epoch interior |
| 6 | **Precision / seed** | bf16 autocast + TF32, seed 42 | fp32 default, seed 0 (per-fold `seed+fold`) |

Task-driven deviations kept (documented, not handicaps): next-**region** target (not next-POI),
CrossEntropy (not BPR), single-head, user-embedding dropped (cold-user CV).

**Honest-result rule:** if audited-faithful + converged STAN still lands below the Markov floor, that
is the reportable result. In practice it clears it comfortably (AL ~61, AZ ~50, Istanbul ~62).

---

## 2. Performance (the matching layer is O(regions))

The matching layer is mathematically irreducibly **O(B·n·R·D)** (output is `[B,R]`; each entry needs a
content dot + a per-region distance gate; the gate is full-rank in R so no reassociation removes it).
But the *runtime* was ~60× above that FLOP floor — **memory-bound** on materialized `[n_pois,R]` /
`[B,n,R]` fp32 intermediates + their backward scatter. Optimizations applied (all numerically
identical / validated quality-neutral) took it from **~530 → ~2 s/epoch (small states), ~85×**:

- **dd_poi precompute** — POI→region haversine computed once + gathered (not per-batch trig).
- **per-poi bias precompute** — interp the Δd interval bias over `[n_pois,R]` once/forward, gather.
- **`F.embedding`** for the table/row gathers — the generic `tensor[idx]` backward was a slow
  atomic `indexing_backward` (profiled = 97.7% of the backward); `F.embedding` uses the fast
  `embedding_dense_backward`. **This was the single biggest fix (23×).**
- **`torch.compile`** (`--compile`) — fuses the elementwise interp (~2.6–4.7×), numerically faithful.
- **bf16** (`--amp bf16`) — halves memory traffic on the big states; A/B-validated **quality-neutral**
  (0.07 pp vs fp32 on AL). Used for the large-R states (FL/CA/TX); small states stay fp32+compile.

Per-epoch (FL, R=4703): fp32+compile ~332 s; bf16 ~166 s. Small states (AL/AZ/Istanbul, R≤1.5K) run in
minutes. CA (R=8501) / TX (R=6553) are ~1.4–1.8× FL and remain heavy on a single A40 (~8–12 h each).

**Parallelism:** fold/stream parallelism does NOT help on one GPU (the GPU is compute+memory saturated
post-compile; 5-fold-parallel OOMs the A40 and time-slices anyway). The only on-GPU lever is bf16 +
`torch.compile`. Fold-fan-out helps only **across machines** (e.g. an H100's 80 GB + ~4.8× bandwidth
fits all 5 bf16 folds and they genuinely overlap). Further single-GPU speedup needs a custom
Triton fused matching kernel (recompute geometry in-SRAM, never materialize) — high effort, not done.

`--only-fold k` is provided for cross-machine fold-parallel runs (aggregate the per-fold JSONs after).

---

## 3. How to run

### Gowalla states (AL/AZ/FL/CA/TX) — TIGER-tract regions, `data/checkins/<State>.parquet`
```bash
export PYTHONPATH=src
# 1) build prefix-expansion windows (RAM-heavy — run ALONE, never alongside a training run)
python -m research.baselines.stan.etl --state alabama          # [--context-len 50]
# 2) train: seed 0, 5-fold, constant-LR + early-stop, to convergence
#    small states -> fp32+compile ; large-R states (FL/CA/TX) -> add --amp bf16
python -m research.baselines.stan.train --state alabama --folds 5 --epochs 200 \
       --seed 0 --patience 20 --compile --tag v5
python -m research.baselines.stan.train --state florida --folds 5 --epochs 200 \
       --seed 0 --patience 20 --amp bf16 --compile --tag v5_bf16c
#    -> docs/results/baselines/faithful_stan_<state>_5f_200ep_<tag>.json
```

### Istanbul (Massive-STEPS) — OSM **mahalle** regions, FSQ check-ins
```bash
# one-time data acquisition (needs huggingface_hub; install via uv if absent):
#   VIRTUAL_ENV=.venv uv pip install huggingface_hub
python -m scripts.second_dataset.acquire --city istanbul        # FSQ tabular -> data/massive_steps_istanbul/raw/
python scripts/second_dataset/acquire_istanbul_mahalle.py       # OSM admin_level=8 -> .../istanbul_mahalle.geojson
# build the STAN checkins parquet from the tabular FSQ (userid/placeid/datetime/lat/lon/category):
#   concat data/massive_steps_istanbul/raw/tabular/{train,val,test}.parquet, factorize user_id/venue_id,
#   rename to the schema, write data/checkins/Istanbul.parquet   (481,850 rows / 23,697 users)
python -m research.baselines.stan.etl --state istanbul          # 520 mahalle regions
python -m research.baselines.stan.train --state istanbul --folds 5 --epochs 200 \
       --seed 0 --patience 20 --amp bf16 --compile --tag v5_bf16c
```
The ETL auto-detects the region-id column (TIGER `GEOID` vs mahalle `@id`) and reads `.geojson`.

### Observe / profile
The trainer logs **per-epoch** `val_Acc@10`, best-epoch, and the **train/val time split** (run with
`python -u`). To pinpoint the forward bottleneck:
```bash
python -m research.baselines.stan.profile_forward --state florida   # full fwd / fwd+bwd / component breakdown
```

### Acceptance
- macro-F1 above floor and Acc@1 sane per fold (NOT the v4 collapse); **best-epoch interior** (not at
  the cap); no NaN-collapsed fold.
- Compare STAN Acc@10 to our MTL reg (AL 69.81 / AZ 59.34 / FL 77.28 / CA 65.66 / TX 67.02 /
  Istanbul 74.28). STAN should sit below (we beat); report whatever the converged number is.

---

## 4. Results (seed 0, 5-fold, audited + converged)

| State | regions | Acc@10 | our MTL reg | precision |
|---|---:|---:|---:|---|
| AL | 1109 | 60.72 ±5.20 | 69.81 (we beat) | fp32+compile |
| AZ | 1547 | 49.86 ±11.52 | 59.34 (we beat) | fp32+compile |
| Istanbul | 520 | 61.86 ±0.61 | 74.28 (we beat) | bf16+compile |
| FL | 4703 | _running_ | 77.28 | bf16+compile |
| CA / TX | 8501 / 6553 | pending (heavy) | 65.66 / 67.02 | bf16+compile |

JSONs: `docs/results/baselines/faithful_stan_<state>_5f_200ep_*.json`. The v4 / seed-42 numbers are
**superseded — do not cite.**
