# ReHDM audit changes — faithfulness fixes + quality-neutral optimizations

Applied 2026-07 per the faithfulness + optimization audit. Scope: files under
`research/baselines/rehdm/` only. The `n_regions` output-domain swap (an allowed
adaptation) is untouched, as are the public entry points (`etl.py` main,
`train.py` CLI). No git commit; no GPU training run — validated by import +
a CPU forward/backward smoke test (both collab-present and legacy no-geo paths)
+ seeded-eval collate.

Legend: **F** = faithfulness fix, **P** = perf (quality-neutral), **D** = doc/cleanup.

---

## Faithfulness fixes

### A1 (F, correctness-critical) — bf16 autocast escape hatch + skip-count visibility
- **Files**: `train.py` (autocast in `evaluate` + train loop; new gate in
  `train_one_run`), `README.md` (new "AMP / precision" section).
- **What**: added a `REHDM_DISABLE_AMP` env gate (mirrors `MTL_DISABLE_AMP`):
  `1`→force fp32, `0`→force bf16 (CUDA only), unset→auto (fp32 when
  `n_regions > REHDM_AMP_REGION_CAP`, default 3000). Threaded `amp_enabled` into
  both `torch.autocast(...)` calls (previously unconditional `enabled=cuda`).
  Added per-run `skipped_batches` counters (`loss`, `grad`) → logged to result JSON
  + an end-of-run WARNING.
- **Why**: this box grad-NaNs on bf16 backward at large C (FL/CA/TX region,
  C≈4.7k–8.5k); the NaN guards then silently skip most batches, yielding a
  "successful" but data-starved run with no visibility.
- **Citation**: CLAUDE.local.md "A40 bf16 backward grad-NaNs at large C"; audit A1.

### A3 (F) — POI-level self-attention applied to target trajectory only
- **File**: `model.py` `ReHDM.forward`.
- **What**: collaborators now use raw embeddings `self.embed(collab_ids)` instead
  of `self.encode_pois(...)` (which runs `poi_block` MSA+FFN). Removed the now-dead
  `kpm_c`.
- **Why**: paper §4.3 + trap #2 — the POI-level refinement is applied only to the
  target; collaborators keep raw `E(q)` until the V→E stage.
- **Citation**: audit A3 (paper §4.3).

### A2 (F, major — verify-needed) — restore spatio-temporal message terms t_ij, s_ij
- **Files**: `model.py` (`ReHDMConfig.n_{time,dist}_buckets`; `HGTransformerLayer`
  optional `time_emb`/`dist_emb` + `forward` bucket args; e2e layers instantiated
  with bucket counts; `ReHDM.forward` threads buckets), `train.py` (bucket
  constants + `_time_bucket`/`_haversine_km`/`_dist_bucket`; per-trajectory
  centroids in `TrajectoryStore`; `make_collate` emits `time_buckets`/`dist_buckets`
  and the batch tuple grows 7→9), `etl.py` (persist `latitude`/`longitude`),
  `debug_nan.py` (unpack the 9-tuple).
- **What**: message is now `m_ij = h_j + r_ij + t_ij + s_ij` (paper Eq. 9). `t_ij`
  = log-width bucket of inter-trajectory Δt (`target.start − collab.end`, ≥0 by the
  precedence filter); `s_ij` = log-width bucket of haversine Δd between trajectory
  centroids. Both → `nn.Embedding` added into the message (STHGCN
  `DistanceEncoderSimple`+`TimeEncoder` convention). The prior code dropped these,
  claiming they were "not defined for hyperedge messages" — contradicted by the
  cited STHGCN ancestor (`layer/st_encoder.py`).
- **verify-needed / TODO(verify)**: ReHDM itself does not fix the encoder family or
  the exact bucketization (paper ambiguity #4). We chose 32 log2-width buckets each;
  `# TODO(verify)` markers are in `model.py` (`HGTransformerLayer.forward`) and
  `train.py` (bucket-constant block) flagging this must be confirmed against the
  authors' released code before it is treated as canonical.
- **Backward-compat**: legacy `inputs.parquet` without lat/lon → `has_geo=False`
  → `s_ij` degrades to a single (index-0) bucket; `t_ij` is always available.
  Re-run `etl.py` to regenerate parquets with coordinates for the full `s_ij` term.
- **Note**: the v2e aggregation layer (Eq. 12/13) is instantiated with 0 buckets
  and is unchanged — Eq. 9's t_ij/s_ij is the hyperedge-propagation message (§4.4).
- **Citation**: audit A2 (paper Eq. 9; STHGCN open-code).

### A2-init (F, correctness — 2026-07-08 AL investigation) — zero-init the Eq.9 st-embeddings
- **File**: `model.py` `HGTransformerLayer.__init__`.
- **What**: `time_emb`/`dist_emb` are now **zero-initialized by default** (was default
  random `nn.Embedding` N(0,1)). `REHDM_ST_RANDOM_INIT=1` restores the old init for
  reproduction. (The A2-off isolation used a temporary `REHDM_ST_BUCKETS` toggle in
  train.py; it was investigation-only and reverted once the finding was established.)
- **Why**: the A2 message is `m_ij = h_j + r_ij + t_ij + s_ij`. With random init, `t_ij`
  and `s_ij` inject two 192-d N(0,1) vectors into **every** message from step 1 — the
  pre-A2 message was just `h_j + r_ij`. This noise cost **~4.8 pp at AL**. Zero-init makes
  the terms **learned from identity** (the standard additive-residual pattern — exactly the
  cascade's zero-init `cond_proj`, `CSLSL_CASCADE.md`).
- **Evidence (AL, test acc@10)**: A2-on random-init **60.16** (bug) → A2-on **zero-init 64.41**
  ≈ A2-off **64.97** (Eq.9 done right is NEUTRAL, not harmful) ≈ old-code **66.06** minus the
  ~1 pp legitimate A3/A6 eval-seeding correction. So the −6 pp was **an init bug + a real eval
  fix**, NOT "Eq.9 hurts". The faithful AL number is **~64.4** (Eq.9 included, correctly).
- **verify-needed (unchanged)**: the encoder family + bucket widths are still the paper's
  ambiguity #4 — but now the term is numerically well-behaved (neutral at AL), lowering the
  risk. Confirm against the authors' code if released.
- **Citation**: this investigation; audit A2.

### A4 (F, minor–moderate; e2e verify-needed) — L2 at V→E, documented LN at e2e
- **File**: `model.py` (removed `self.v2e_post = LayerNorm`; `initial_trajectory_rep`
  now `F.normalize(F.relu(v2e_mlp(h)), dim=-1)`), `README.md`.
- **What**: the V→E output is an explicit L2 step to match Eq. 13
  (`h = L2(ReLU(...))`), not LayerNorm. Eq. 14's e2e `Norm` is genuinely ambiguous
  (LN or L2) — kept as `LayerNorm` for stability at large region domains, now with a
  `# TODO(verify)` note to A/B against L2 if the authors' code disambiguates. README
  "identical L2" claim corrected to reflect L2(V→E)/LN(e2e).
- **Citation**: audit A4 (Eq. 13 explicit; Eq. 14 ambiguous).

### A5 (F, minor — no behavior change) — √d_head vs paper's √d comment
- **File**: `model.py` `HGTransformerLayer.forward`.
- **What**: added a comment noting paper Eq. 5 literally writes `√d` (likely a typo);
  we follow STHGCN's / standard-MHA `√d_head`. No code change (our choice is the
  defensible one).
- **Citation**: audit A5.

### A6 (F, reproducibility) — seeded eval RNG decoupled from collaborator-building
- **File**: `train.py` (`make_collate` gains `seeded` param; `evaluate` passes
  `seeded=True`), `README.md`.
- **What**: `rng = random.Random(0) if (seeded or not training) else None`. Eval
  passes `training=True` (so the sub-hypergraph IS built per §4.2) **and**
  `seeded=True`, so inter-user sampling is deterministic. Previously the seed was
  keyed off `training`, so the eval path (training=True) fell back to the global
  `random` and was not actually seeded (contradicting README "verified-fixed bug #3").
- **Citation**: audit A6.

### A7 (F/cleanup) — remove `collaborators()` tautology + dead else
- **File**: `train.py` `TrajectoryStore.collaborators`.
- **What**: dropped the `(rng or random).random() < 1.0` guard (always True → dead
  `else`, one wasted RNG draw that perturbed the stream). Now
  `if len(pool) > max_inter: sample(...) else pool[:max_inter]`.
- **Citation**: audit A7. (Folded with A6 so the eval RNG stream is clean.)

## Doc / cleanup

### A8 (D) — LR default vs README reconciled
- **File**: `README.md`.
- **What**: README now documents the actual argparse defaults (AdamW lr 5e-5,
  wd 0.01 + OneCycleLR max_lr 5e-4) instead of the stale "1e-4 / 1e-3". Chose to
  fix the doc (not the code defaults) to avoid changing the runtime behavior of
  default-flag runs. Neither value is paper-specified.
- **Citation**: audit A8.

### A9 (D) — delete dead `_sessionize_24h`
- **File**: `etl.py`.
- **What**: removed the never-called `_sessionize_24h`; `build_inputs` already
  implements the identical 24h-window sessionization inline (single source of
  truth). Left a breadcrumb comment.
- **Citation**: audit A9.

---

## Quality-neutral optimizations (kept separate, clearly commented)

### B4 (P, numerics-consistency — no speed claim) — TF32 gated off under fp32 path
- **File**: `train.py` `train_one_run`.
- **What**: TF32 (`allow_tf32` + `set_float32_matmul_precision`) is enabled only
  when `amp_enabled` (bf16, where matmuls are bf16 anyway). Under the A1 fp32-faithful
  path it is disabled (`"highest"`) so "fp32" means true fp32 (board protocol).
- **Quality tag**: numerics cleanup; restores true-fp32 on CA/TX; no speed loss
  under bf16.
- **Citation**: audit B4; guardrails ("TF32 ... breaks the true-fp32 board protocol").

### B2 (P, bit-exact after A6) — snapshot best-val weights, single end-of-training test eval
- **File**: `train.py` `train_one_run`.
- **What**: instead of a full **test** eval on every val@10 improvement, snapshot
  `copy.deepcopy(model.state_dict())` at the best-val epoch, then load + eval test
  once after the loop. Removes 5–15 redundant full test passes/run.
- **Quality tag**: bit-exact **because A6 landed** — the deferred test eval is
  deterministic (`model.eval()` + seeded collaborators), so it reproduces the number
  the in-epoch eval would have produced at the same weights. Ordered after A6 per the
  audit.
- **Citation**: audit B2.

### B1 (P) — bf16(small)/fp32(large) speed lever = the A1 gate
- Not a separate change: the `REHDM_DISABLE_AMP` auto behavior (bf16 at small
  states, fp32 at large) IS the B1 lever. A/B one AL run (bf16 vs fp32) to confirm
  within-fold-noise before adopting bf16 as the small-state default. Commented at
  the A1 gate in `train.py`.

---

## Optimization eval (2026-07-08 — B0 done; the bottleneck is the box, not the code)

**Profiled.** ReHDM is **CPU-bound**: GPU sits at ~45 % even though the loader already
runs **12 workers + persistent + prefetch=4**. The wall is the per-batch sub-hypergraph
build in `make_collate`. Per-epoch (clean box): AL ~5.5 s, CA ~123 s, TX ~206 s
(→ CA ~8.5 h / TX ~14 h for 5 seeds × 50 ep) — batched per-**trajectory** (CA ~378 k /
TX ~514 k trajectories), NOT per-row, so ~10× under the handoff's 75-120 h guess.

**Collate precompute attempt — bit-exact but NOT shipped.** Tried precomputing the Eq.9
edge features `(tb, db)` once (they're deterministic) + sampling collaborator **indices**
instead of values (`random.sample(range(n),k)` is RNG-identical to `sample(pool,k)` —
proven: selection + post-state match over 200 trials). **Reverted** because: (a) at AL
(the only state measurable) it was **neutral-to-slower** (~6 s vs 5.5 s — small states are
np-overhead-bound, not haversine-bound), and (b) the CA measurement — where the ~3 M
haversine/epoch it removes would actually matter — was **impossible to validate**: a
neighbor's 30 GB / 93 % Jupyter kernel swamped the shared GPU (inflated AL to 22 s/epoch).
Shipping an unvalidated "speedup" that measured slower on the one clean state is not sound.
It stays a **documented bit-exact candidate** for a clean-box re-test.

**The real bottleneck is shared-box contention, which no code change fixes.** Best approach
to run ReHDM: the validated v4 code (zero-init Eq.9), fp32 for CA/TX (A1 auto-gate, avoids
the bf16 grad-NaN wall), **fold/seed-by-seed + resumable, launched when the box is quiet**.
bf16 for CA/TX would NOT help while CPU/contention-bound (GPU already idle 55 %).

## Deferred

- **B0 (profile first)** — **DONE** (above): CPU-bound, collate is the hotspot; the
  precompute lever was bit-exact but unvalidatable due to neighbor GPU contention.
- **B3 (torch.compile(dynamic=True) + warm shared inductor cache)** — deferred
  (audit: low priority, default-off, A/B-gated). Collaborator count `Bn` and seq
  length vary per batch → dynamic shapes likely trigger recompiles/graph-breaks that
  dominate; cannot A/B without the GPU. `mode="max-autotune"` is a proven segfault
  trap on this stack and was never a candidate.
- **A2 s_ij on existing states** — the model + plumbing are in place, but the full
  Δd term needs `etl.py` re-run so `inputs.parquet` carries lat/lon. Until then
  `s_ij` uses a single bucket (graceful degrade); `t_ij` is fully active.

## Guardrails honored
No `mode="max-autotune"`, no fused/foreach AdamW, no unconditional TF32 (now gated),
no `num_workers>0` change, no larger-batch-for-speed. Every perf change (B2, B4) is
bit-exact or numerics-only and is commented `# B2`/`# B4`, never entangled with a
faithfulness fix.

## Files touched
- `model.py` — A2, A3, A4, A5
- `train.py` — A1, A2, A6, A7, B1(comment), B2, B4
- `etl.py` — A2 (persist lat/lon), A9
- `debug_nan.py` — A2 (9-tuple unpack)
- `README.md` — A1, A2, A3, A4, A6, A8
- `REHDM_AUDIT_CHANGES.md` — this file (new)
