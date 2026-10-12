# ⚠ CAVEAT: the dedicated-category cells did NOT all run at the precision the sidecars claim

> **Found 2026-08-07 by audit. Affects every v18 dedicated-category number produced before the fix.**
> The region and joint families are **unaffected**.

## The bug

`run_wave.sh` `cell_joint` sets `export MTL_DISABLE_AMP=1`. A bare `export` inside a shell function
persists into **later cells in the same shell**. `cell_cat` never sets or unsets it, and the STL
trainer gates fp16 autocast on exactly that variable
(`src/training/runners/_single_task_train.py:60-78`). So a dedicated-cat cell ran **fp32 if some
earlier joint cell had run in the same shell, and fp16 otherwise** — which depends on whether the
wave was resumed, because on resume the earlier cells are `SKIP`ped and never export anything.

`run_state istanbul &` / `alabama &` are subshells (exports die there); `arizona` and the
`florida/texas/california` loop run in the main shell. `run_chain.sh` launches each wave as its own
`bash`, so waves do not cross-contaminate.

## What actually ran

| cell | precision | wall |
|---|---|---:|
| istanbul cat s0 / s1 | fp16 | 465 / 436 s |
| alabama cat s0 / s1 | fp16 | 201 / 200 s |
| arizona cat s0 / s1 | fp16 | 178 / 178 s |
| **florida cat s0** | **fp32** | 1903 s |
| florida cat s1 | fp16 | 1080 s |
| texas cat s0 | fp16 | 3266 s |
| **california cat s0** | **fp32** | 4190 s |
| all joint cells | fp32 (sets it itself) | — |
| all reg cells | fp32 (`p1` never autocasts) | — |

Corroborated by wall time: florida s0/s1 = **1.76×** on an identical cell, while istanbul/alabama/
arizona are 1.00–1.07× across seeds. Texas (3266 s, fp16) is *faster* than California (4190 s, fp32)
despite being the larger corpus.

## The false field

Every cat sidecar hardcodes `"protocol": {"precision": "fp32 (MTL_DISABLE_AMP=1)"}`
(`run_wave.sh:79`). **That is false for 8 of the 10 cat cells**, and it propagated into
`PROVENANCE.md` and `V18_RESULTS.md`. Do not trust that field on any cat cell produced before the
fix; trust this table.

`TORCHINDUCTOR_CACHE_DIR` leaks by the same mechanism, so florida cat s0 compiled against arizona's
inductor cache and california cat s0 against texas's.

## What it does and does not invalidate

**VOID — do not cite:**
- the florida cross-seed category comparison (35.9711 s0 **fp32** vs 36.1544 s1 **fp16**); under a
  final-epoch read the sign even flips (+0.183 → −0.707)
- the texas s0 Δcat of **+0.96** (dedicated **fp16** vs MTL **fp32**) — the only "beats" verdict in
  the category column

**Subtlety that cuts the other way.** v17's own ceiling sweep (`cat_ceiling_sweep/sweep.sh`) sets
**no AMP flag either**, so **v17's Gowalla dedicated-cat ceiling also ran fp16**, against its fp32
MTL arm. v17's published Δcat therefore crosses the same precision boundary. For the fp16 v18 cells
(AL/AZ/TX/FL-s1) the v18-vs-v17 delta comparison is *protocol-matched*; the two fp32 cells
(FL s0, CA s0) are the ones that deviate from v17. v17's **Istanbul** dedicated cat ran fp32 (the
same leak, from `h3_istanbul/run_step3_n20.sh` calling `mtl_run` before `cat_ceil`), so Istanbul is
mismatched the other way.

So "pin fp32 everywhere" is **not** obviously the right fix — it makes the within-v18 §1 contrast
internally consistent but breaks the match with v17's fp16 dedicated ceiling used in §3. That is a
protocol decision, not a bug fix, and it is recorded here as open.

**UNAFFECTED:** everything in the region column; every joint-vs-joint comparison; the whole
[`LOSS_WEIGHT_PROBE.md`](LOSS_WEIGHT_PROBE.md) (all arms fp32); and the headline that the v17
category advantage of +5…+9 pp is gone (both precision and selector artefacts are ≤2.6 pp against a
shift of −5.4…−9.7 pp).
