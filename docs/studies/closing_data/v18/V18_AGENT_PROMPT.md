# v18 run charter — prompt for the agent on `nespedgpu`

> Paste everything below the line into the agent working on `nespedgpu`. It is written to be executed
> without further clarification. Where a decision is genuinely open, the prompt says STOP AND ASK
> rather than inviting a guess.

---

You are running a large multi-seed evaluation on the GPU host for a master's dissertation. Read this
whole charter before running anything. The work is expensive (about 36 hours of GPU time with two
concurrent jobs) and it produces numbers that go into a defended document, so correctness of protocol
matters more than speed.

## 0 · What v18 is, and what it is not

**v18 = the frozen v17 recipe, with the consecutive-visit leak fixed, plus elapsed-time node features.**

Three components, and all three are load-bearing:

1. **v17 recipe, unchanged.** Same model, same heads, same optimizer, same learning rates, same epoch
   counts, same selector, same scorers. v18 is not an architecture change.
2. **Forward-only check-in graph.** The canonical preprocessor emits BOTH directions of every
   consecutive-visit edge (`research/embeddings/check2hgi/preprocess.py`, the block that does
   `edges.append([src, tgt])` then `edges.append([tgt, src])`). v18 drops the backward direction, in
   TRAINING and at READOUT. This is the fix: under v17 a visit's vector is convolved over a
   neighbourhood that includes the visit AFTER it, so the category head sees a feature of the target it
   is being asked to predict.
3. **Elapsed-time node columns.** Four columns appended to the canonical eleven: log time since the
   previous visit, log time since the user's first visit, the same-day gap clipped at 24 hours, and a
   first-visit indicator. All measured UP TO the visit itself. The gap to the target is never added;
   that would reintroduce the leak in a new form.

Everything needed for this already exists in `scripts/integrity_v2/`, which is on the host. Do not
rewrite it. The relevant flags on `scripts/integrity_v2/build_study_repr.py` are
`--forward-only --add-continuous-time`, and the matching readout on
`scripts/integrity_v2/infer_checkins.py` is `--readout prefix_forward_only`.

**What v18 is NOT.** Do not add place identity or region identity to the node features. Both were
measured at Alabama, on the dedicated protocol, against the forward-only baseline of 27.5127, and every
variant HURT:

| variant | macro-F1 | vs forward-only |
|---|---:|---:|
| place, standardized, projected to 8 (the best place arm) | 27.1047 | −0.41 |
| place, standardized, full 64 | 25.7683 | −1.74 |
| place, raw 64 (the worst) | 25.6506 | −1.86 |
| region, standardized, projected to 8 | 26.9601 | −0.55 |
| **elapsed time (the only gain)** | **28.3461** | **+0.83** |

The mechanism: a spatial block the graph can already anticipate from a node's neighbourhood becomes a
shortcut for the pretext discriminator, whose negatives are row-permuted node features, so "real or
shuffled?" becomes answerable from that block alone. The pretext loss collapses (0.2112 → 0.064 with
region, → 0.088 with raw place) while downstream accuracy falls. The elapsed-time gap is the one feature
tested that is barely above chance in neighbourhood predictability, which is the working explanation for
why it is the only one that helps. One honest caveat: that account does not explain why region collapses
the objective harder than place, since place has the higher predictability lift. That ordering is
recorded as unexplained.

Do not change the encoder width or depth: sweeps at 32/64/128 dimensions and 1/2/3/4 layers found 64 and
2 at or near optimum, with one layer equal to three within 0.014 points. These are settled; re-running
them is waste.

## 1 · What you must know before you start (read the evidence, do not re-derive it)

Read these first. They are the scientific context and they will stop you from misreading your own
results:

- `articles/dissertacao/science/consecutive_link_causal_audit.md` — the leak, measured. The key number:
  at Alabama on the reported dedicated model, withholding the target visit costs **28.63 macro-F1
  points** (56.86 → 28.23). The audit reproduces the published dedicated column (55.87 published
  seed-0 vs 56.86 here).
- `articles/dissertacao/science/checkin_graph_enrichment_options.md` — why elapsed time is in and place
  and region are out.
- `articles/dissertacao/science/checkin_repr_scaling_and_capacity.md` — the depth, width and data-scaling
  sweeps, all flat or negative.
- `docs/studies/closing_data/joint_best/README.md` and `JOINT_BEST_SCORING.md` — the methodology and the
  scoring convention you must follow.
- `docs/studies/closing_data/v17_completion/CEILINGS_N20_FINAL.md` — the exact per-state dedicated
  recipes, reproduced in §3 below.

**Expect the category numbers to fall a long way.** At Alabama the honest forward-only arm scores about
28.3 where v17 reported about 56.9. That is the point of the exercise, not a bug: the v17 number was
inflated by the leak. If your v18 category numbers come out near the v17 values, something is wrong
with the forward-only path and you must investigate rather than report. **Expect region to be
essentially unchanged**: the region tower consumes region embeddings indexed by historical places, which
are per-region dataset constants, so the leak cannot reach it. At Alabama the joint region result moved
by +0.01 points under the strict readout. A large region change is also a signal to investigate.

## 2 · Git hygiene, first, before any compute

Do this on the LOCAL repo state you find on the host, and be conservative:

1. `git status --porcelain`. Classify every untracked and modified path into: (a) real scientific
   content that belongs in the repository, (b) scratch or generated files that do not, (c) unclear.

   **`git status` is not sufficient here.** `.git/info/exclude` contains a bare `results` pattern, which
   hides `docs/results/check2hgi_integrity_v2/` — 32 scorer-written result records that ARE real content
   and are the traceability backing for every number in the integrity study documents. Check with
   `git check-ignore -v <path>` and `git status --porcelain --ignored` before concluding a directory is
   absent. If those records are meant to be committed, force-add them
   (`git add -f docs/results/check2hgi_integrity_v2/`); if the exclusion is deliberate, say so in your
   report and leave them. **STOP AND ASK on this one** — whether machine-readable results belong in the
   repository or stay local is the author's call, not yours.

2. Commit only (a). A triage of the state at the time of writing, which you should re-derive rather than
   trust:

   | verdict | paths |
   |---|---|
   | commit | `articles/dissertacao/science/*.md` (the integrity study documents), `scripts/integrity_v2/`, `src/configs/paths.py` (engine registrations), `docs/NEXT_STEPS.md`, `docs/baselines/`, `docs/future_works/` |
   | do not commit | `handoff/`, `tmp/`, `.temp/`, `.integrity_stage/`, `.antigravitycli/`, `articles/dissertacao/tmp/`, `*.tar.gz` bundles, `*.log`, root-level ad-hoc scripts (`audit_claims.py`, `collapse_check.py`, `detailed_audit.py`), `leak_audit_Florida.json`, `plan_*.json` |
   | ask | `docs/results/check2hgi_integrity_v2/` (currently git-excluded, see above), `articles/dissertacao/science/RESUME_*.md` (operational notes that may be stale), `banca_architecture_detail.md` (defense material at the repo root, unclear whether it belongs there) |

   Note that 25 tracked files are also modified, most of them dissertation `.tex` and `.pdf` files from
   other sessions' work. **Those are not yours to commit as part of this task.** Commit them only if the
   author confirms, and never bundle prose edits into a v18 infrastructure commit; separate commits with
   honest messages.

   **If a path is unclear, leave it untracked and list it in your report. Do not commit something you
   cannot justify.**
3. Add scratch patterns to `.gitignore` rather than deleting the files.
4. Then: fetch, update the current branch from `origin/main`, push, merge to `main`, and check out
   `main`. Resolve conflicts by preferring the remote for files you did not author in this session.
   **If the merge is not clean and the conflict is in a `.tex` chapter or any dissertation prose file,
   STOP AND ASK. Do not resolve prose conflicts unilaterally.**
5. Record the commit SHA you start the run from. Every result file must carry it.

## 3 · The experiment matrix

Six datasets: `istanbul`, `alabama`, `arizona`, `florida`, `california`, `texas`.
Four seeds: `0, 1, 7, 100`. Five folds each. **n = 20 per cell.**

Three model families per dataset and seed:

**(a) Dedicated next-category.** `scripts/train.py --task next --model next_gru`, 50 epochs, 5 folds,
scored by `scripts/closing_data/score_stl_cat_ceiling.py` (macro-F1 at the f1-best epoch, fold-mean).
The batch and learning rate are PER STATE, from `CEILINGS_N20_FINAL.md`:

| tier | states | recipe |
|---|---|---|
| small | alabama | `--batch-size 2048 --max-lr 0.005` |
| small† | arizona | `--batch-size 8192 --max-lr 0.005` |
| large | florida, california, texas | `--batch-size 8192 --max-lr 0.005` |
| istanbul | istanbul | STOP AND ASK — `CEILINGS_N20_FINAL.md` does not tier Istanbul; do not guess a recipe |

Pass `--embedding-dim 64` explicitly. `next_gru` takes its GRU input width from the configured
embedding dimension and does NOT infer it from the artifact; it defaults to 64, which is correct here,
but state it so a future width change fails loudly instead of silently.

**(b) Dedicated next-region.** `scripts/p1_region_head_ablation.py --heads next_stan_flow --input-type
region --region-emb-source check2hgi_design_k_resln_mae_l0_1 --engine-override <v18 engine>
--override-hparams freeze_alpha=True alpha_init=0.0 --max-lr 0.003 --target region`, 50 epochs, 5 folds.
The prior is OFF (α frozen at 0), so `log_T` is inert and `--per-fold-transition-dir` is omitted; that
parity was validated at Alabama (no-dir 70.00 vs board 69.99).

**(c) Joint model, joint-best setting.** v17 is defined in `catx_v17_seed0_5f/RESULTS.md` as
"v16 + **bs8192** + per-head cat-lr 1e-3 via `MTL_ONECYCLE_PER_HEAD_LR`", and
`perhead_lr_n20.md` confirms bs8192 with cat-lr 1e-3 as the selected recipe at AL, AZ and FL. Use that,
not the bs2048 that appears in some older launcher scripts:

```
export MTL_ONECYCLE_PER_HEAD_LR=1          # WITHOUT this the per-head LRs are INERT under onecycle
                                           # (a scalar max_lr broadcasts to all groups) and you are
                                           # silently running v16, not v17
scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine <v18 engine> \
  --state <STATE> --seed <SEED> --epochs 50 --folds 5 --batch-size 8192 \
  --mtl-loss static_weight --category-weight 0.75 \
  --no-reg-class-weights --no-cat-class-weights \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --tf32 \
  --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/<STATE> --no-checkpoints
```

Two flags there are easy to lose and both change what you are measuring. `MTL_ONECYCLE_PER_HEAD_LR=1`
is what makes the per-head learning rates take effect at all; without it `--cat-lr` and `--reg-lr` are
inert and the run is v16. `--checkpoint-selector geom_simple` with `min_best_epoch=0` is the Table-3
convention and the basis of the joint-best reading. **Verify both against `perhead_lr_n20.md` and
`joint_best/PROVENANCE.md` before wave 1, and if any source disagrees, STOP AND ASK.**

Score the joint runs with `scripts/closing_data/a40_score_matched.py`, which is the convention: category
is macro-F1 at the f1-best epoch; region is `top10_acc_indist * (1 - ood_fraction) * 100` at the
indist-best epoch, i.e. **Acc@10**. The region macro-F1 column in the same CSV is a different quantity
and is NOT what the dissertation reports. Also compute the joint-best (`geom_simple` single-checkpoint)
reading per `JOINT_BEST_SCORING.md`, since the request asks for the joint-best setting.

## 3b · Preflight, already verified on this host (re-verify, do not assume)

As of the writing of this charter, all six states have the four inputs a v18 build and evaluation need,
checked directly on `nespedgpu`:

| state | `check2hgi/<s>/temp/checkin_graph.pt` | `check2hgi_dk_ovl/<s>/input/next.parquet` | `.../temp/sequences_next.parquet` | `check2hgi_design_k_resln_mae_l0_1/<s>/region_embeddings.parquet` |
|---|---|---|---|---|
| istanbul, alabama, arizona, florida, california, texas | yes | yes | yes | yes |

Disk at the time of writing: 55 GB free on `/home` (86 percent used). GPU idle, about 45 GB free.
No training processes running.

**Disk is the real risk in this run, not GPU.** Each v18 engine directory carries a full
`next.parquet`; Alabama's is about 264 MB and California is roughly 28 times Alabama's size, so six
engines could plausibly consume 30 GB or more against 55 GB free. Before Phase 0, estimate the total
from each state's `dk_ovl` `next.parquet` size and report it. If the estimate exceeds about 35 GB, STOP
AND ASK before building — do not fill the disk and do not delete anything to make room.

Re-run this preflight yourself and report the table. A missing `sequences_next.parquet` or
`region_embeddings.parquet` at a large state costs hours if it surfaces mid-wave.

## 4 · Execution order — interleaved by seed

This is a hard requirement, because it makes partial results usable at every stage.

```
Phase 0   build the v18 representation for all 6 states           (once, ~3 h)
Wave 1    seed 0   -> all 6 states, all 3 families -> AGGREGATE + WRITE REPORT
Wave 2    seed 1   -> all 6 states, all 3 families -> AGGREGATE + WRITE REPORT
Wave 3    seed 7   -> ...
Wave 4    seed 100 -> ...
```

Do NOT run seed 0 through 100 for one state and then move on. After every wave, regenerate the
aggregate JSON and the markdown so the study is readable at n=5, n=10, n=15, n=20, with the current n
stated in every table.

Within a wave, order states smallest first: `istanbul, alabama, arizona, florida, texas, california`.
A failure then surfaces on a cheap dataset rather than after eight hours on California.

**Two concurrent jobs, not more.** The card holds two of these comfortably. Before dispatching a second,
check `nvidia-smi --query-gpu=memory.free --format=csv,noheader`; the largest joint run at California
needs about 21 GB. Two builds sharing the card roughly halves throughput of each, which is an acceptable
trade.

## 4b · Naming, and resumability

Name the v18 engines `check2hgi_v18/<state>` and the representation runs
`results/check2hgi_v18/<state>/`, registered as `EmbeddingEngine.CHECK2HGI_V18 = "check2hgi_v18"`. One
engine per state, shared across all four seeds: **the representation is built once per state and does not
depend on the downstream seed.** Only the downstream training seed varies across waves. Use a fixed
representation seed (42, matching the study builds) and record it.

Do NOT write into `output/check2hgi_dk_ovl/`, `output/check2hgi_design_k_resln_mae_l0_1/`, or any other
existing engine directory. Those are the frozen v17 artifacts behind the published table and behind the
region-embedding symlink. `build_study_repr.py` already refuses to write into the frozen paths; do not
work around it.

**Every stage must be resumable and idempotent.** A 36-hour run will be interrupted. Skip any cell whose
scored output already exists, and make the skip explicit in the log so a resumed run is auditable rather
than mysterious. Persist each cell's rundir path to disk as it completes — deriving rundirs by
newest-mtime globbing breaks when two jobs run concurrently, which is exactly the configuration you are
told to use.

## 5 · Operational traps on this host (all of these have already bitten someone)

- **A suspended CUDA process does NOT release GPU memory.** `kill -STOP` yields utilization but keeps
  the whole reservation. If you need memory back, the process must exit.
- **Progress bars span the WHOLE FOLD, not one epoch.** A bar reading `Epoch 39/50: 78%|
  14550/18750 [41:22<10:44]` means 41 minutes elapsed for the entire fold-0 run and about 11 minutes
  remain. Reading the elapsed time as time-within-epoch will badly misestimate completion.
- **Never let two jobs edit `src/configs/paths.py` concurrently.** Each reads the file, adds its enum
  entry, and writes back, so the later write silently drops the earlier one's. This happened twice.
  Serialize with a lock directory (`mkdir` as the mutex) and assert by import BEFORE spending training
  time: `python -c "from configs.paths import EmbeddingEngine as E; E.<YOUR_ENGINE>"`.
- **An engine must be registered in TWO allowlists.** The `EmbeddingEngine` enum plus the separate
  region-specific `supported` tuple inside `IoPaths.get_next_region`. A run that trains fine on
  category will fail at the region tower otherwise.
- **A v18 engine directory needs four things**, not just the embeddings: `input/next.parquet`,
  `input/next_region.parquet`, `temp/sequences_next.parquet` (the PLACE sequence, which is data and
  identical across arms — copy it and verify the `userid` order matches), and
  `region_embeddings.parquet` (**symlink** this from the source engine so the two provably share one
  table; a region contrast must not be confounded by different region vectors).
- **Column naming differs between tables.** The place table uses `placeid` plus digit-named dimensions
  `0..63`. The region table uses `region_id` plus `reg_0..reg_63`. Assuming one convention for the other
  silently produced a zero-width feature block once, which made two arms byte-equivalent to their own
  baselines and briefly looked like a real result.
- **The output width 64 is a hard constant in at least three places**: the encoder, the Delaunay
  place-table anchor (a fixed 64-d distillation target that crashes on any other width), and the
  downstream head's configured embedding dimension. Do not change it.
- Jobs occasionally report `orphaned` in the harness while running fine. Trust the job's own
  `_status.json` and its log, not that status.

## 6 · Self-checks that must pass before a number is reported

Fail closed on all of these. A silent wrong number is far worse than a crash.

1. **The readout matches the training graph.** A forward-only checkpoint must be read with
   `--readout prefix_forward_only`. `infer_checkins.py` already refuses a mismatch; do not pass
   `--allow-direction-mismatch` to make an error go away.
2. **Feature width matches the checkpoint.** Assert the artifact's per-visit width equals the encoder's
   `in_channels` (15 for v18: canonical 11 plus elapsed 4).
3. **Enrichment actually landed.** Read `build.json` and confirm `node_enrichment.layout` is
   `['canonical_11', 'continuous_time_4']` and `in_channels == 15`. A requested block that contributes
   zero columns is now a hard failure, but check the manifest anyway.
4. **Row pairing across arms.** Any two arms compared on the same windows must agree on row ids, labels
   AND userids, and retain at least 95 percent of the smaller arm. This caught a collapse to 2,731 of
   23,679 windows once.
5. **Held-out user encodability.** The check-in graph has zero cross-user edges, so a validation user
   encoded alone must reproduce the vectors it gets inside the full graph. `--self-test` checks this;
   run it at least once per state.
6. **Per-state sanity.** Category should fall far below the v17 value; region should barely move. Flag
   any state where category lands within 5 points of v17, or region moves more than 2 points.

## 7 · Deliverables

Create `docs/studies/closing_data/v18/` following the shape of `joint_best/`:

```
docs/studies/closing_data/v18/
  README.md              what v18 is, status, read-in-this-order, scope guardrails
  TASKS.md               the charter and task list
  V18_RESULTS.md         the tables: per state, dedicated cat / dedicated reg / joint (diag-best AND
                         joint-best), Δ vs the v17 published values, current n stated in every table
  PROVENANCE.md          every rundir: state, seed, PID, path, recipe, commit SHA
  AUDIT.md               the self-checks of §6 with their measured values, and anything that failed
  METHODOLOGY.md         the v18 definition, why forward-only, why elapsed time, what was excluded
  score_all.py           the reproducer that regenerates data/v18_results.json from the rundirs
  data/v18_results.json  machine-readable, schema mirroring joint_best/data/j1_results.json
```

`data/v18_results.json` must mirror the `j1_results.json` schema: a `per_run` array with one object per
(state, seed) carrying at least `state`, `seed`, `pid`, `rundir`, the per-fold vectors, the selected
epochs, and the audit sub-objects. Add v18-specific fields (`v18_config`, `commit_sha`,
`forward_only: true`, `in_channels: 15`) rather than repurposing existing ones. Every number in a
markdown table must be traceable to this JSON.

**Write the wave-1 report before starting wave 2.** Partial results that nobody can read are not
partial results.

## 8 · Progress reporting, so the run can be monitored

Maintain `docs/studies/closing_data/v18/PROGRESS.md`, rewritten after every completed cell, containing:
a matrix of the 6 states by 4 seeds by 3 families with per-cell status (pending, running, done, failed);
wall-clock per completed cell and a revised estimate for what remains; the current n per state; and any
`[VERIFY]` flags or investigations open. Also append a one-line timestamped entry per event to
`docs/studies/closing_data/v18/log.md`, matching the style of `closing_data/log.md`.

Budget estimate, extrapolated from measured Alabama timings scaled by dataset size, NOT measured at the
large states: builds about 3 hours total; one seed across all six states about 17 hours; four seeds
about 69 hours serial, about 36 hours with two concurrent jobs. **Re-time wave 1 and report actuals**;
if the extrapolation is off by more than about 50 percent, say so before committing to waves 2 to 4.

### A machine-readable heartbeat, so progress can be checked without reading logs

Alongside the markdown, maintain `docs/studies/closing_data/v18/status.json`, rewritten atomically
(write to a temp name, then rename) after every state transition:

```json
{
  "updated_at": "<ISO-8601 UTC>",
  "commit_sha": "<the SHA the run started from>",
  "phase": "build | wave1 | wave2 | wave3 | wave4 | aggregate | done | blocked",
  "current_n": {"alabama": 5, "florida": 5, "...": 0},
  "cells": [{"state": "alabama", "seed": 0, "family": "joint",
             "status": "done", "wall_seconds": 684, "rundir": "<abs path>",
             "cat": 0.0, "reg": 0.0}],
  "running": [{"state": "florida", "seed": 0, "family": "joint", "pid": 0,
               "started_at": "<ISO-8601>", "eta_seconds": 0}],
  "gpu_free_mib": 0,
  "disk_free_gb": 0,
  "blocked_on": null,
  "verify_flags": []
}
```

Set `phase: "blocked"` and populate `blocked_on` with a plain-language sentence whenever you stop to ask
something. That single field is what makes a 36-hour run monitorable: a reader can tell at a glance
whether the run is progressing or waiting on them, without parsing a log.

Write a terse progress line to stdout on every cell start and finish, including wall time. Avoid
per-epoch chatter in the log — it makes the real events unfindable.

## 9 · When to stop and ask

Stop and ask rather than guessing if: the Istanbul dedicated-category recipe is not documented; the MTL
batch size for a state disagrees between sources; a git merge conflicts in dissertation prose; a v18
category number lands near its v17 value; region moves more than 2 points at any state; or a self-check
in §6 fails and the cause is not obvious. Report what you found and what you propose. Do not smooth
over a discrepancy to keep the run moving.

## 10 · Honesty rules for anything you write

- Every number carries its convention: which metric, which selector, and `n = seeds × folds`.
- Never compare across protocols. A value from one model or fold count may not be differenced against a
  value from another. If you need a baseline, measure it on the same protocol.
- "Outperforms" requires a paired superiority test; "matches" requires TOST non-inferiority within the
  stated margin. Never upgrade a non-inferior result to a win.
- Report what you measured, not what you expected. If v18 is worse than v17 on category, that IS the
  result, and it is the honest one.
