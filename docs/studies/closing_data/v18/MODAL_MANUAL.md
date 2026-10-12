# Running v18_2 cells on Modal — the manual

Written 2026-08-10 after a night in which roughly $13 of rented GPU bought one usable data
point. Every rule below is the residue of a specific failure, and each one is cheap to obey and
expensive to skip. Read it before submitting anything.

---

## 0 · The one-paragraph version

Upload data with the Modal CLI **from the GPU host**, never through the agent workspace. Put the
repo and the data on a persistent Volume so jobs submit with `inputs=[]`. Write results to a mounted Volume (durable) and copy small summaries into `./out/`
**as you go**, not at the end of the script. Run `run_lane.sh`, never a hand-written training command. And
before you trust any timing, confirm `--compile` is on both sides of the comparison.

---

## 0.1 · Which harness are you? Read this before anything else

This manual was written from a **Claude Science** session, whose agent has a `host.compute` API
(`byoc:modal`, `submit_job`, `./out/` harvest, `host.compute.ledger()`). **A Claude Code agent
does not have that API** — it has a terminal, the `modal` client and a token. An agent that
follows the `submit_job` instructions from a Claude Code session burns a turn discovering the
tool does not exist. Find your row first:

| you have | entry point | notes |
|---|---|---|
| `host.compute` (Claude Science) | `scripts/run_modal_cell.py` | §11. Harvests via `./out/`, sweeps sandboxes. Bound to the **primary** account (§9). |
| a terminal + `modal` client (**Claude Code**) | **`scripts/modal_lane.py`** | Sandbox-based. Live stdout, harvest onto the Volume, verified teardown. Works on **either** account. |
| a shell on the A40 | `scripts/run_wave_a40.sh` → `run_lane.sh` | `HARVEST=0`; nothing to bring back. |

### The Claude Code path, end to end

```bash
pip install modal                     # the only dependency; no ~/.modal.toml is written
cd pipelines/modal

# 0. what would this cost? nothing is submitted.
python modal_lane.py --state alabama --seed 7 --cells cat,reg --dry-run

# 1. cheap CPU preflight: what is staged, what is materialized, does preflight.py pass
python modal_lane.py --state texas,alabama --preflight-only --stage-scripts

# 2. the lane. stdout streams live; results land in
#    docs/results/closing_data/v18_2/modal_runs/<state>_s<seed>_lane_<stamp>/
python modal_lane.py --state alabama --seed 7 --cells cat,reg --gpu A100-40GB

# 3. a second, independent view while it runs (another terminal)
python watch_modal.py --state alabama --seed 7 --follow
```

`--stage-scripts` re-uploads this `scripts/` directory to the Volume as
`/scripts/v18_2_scripts.tgz`. **Pass it whenever you have edited a script**, or the container
runs the bundle from the last upload and your fix is not in the run.

### What differs, and why it is not a downgrade

`modal_lane.py` uses a **Sandbox**, not `submit_job`. Three consequences, all improvements:

- **The run is never invisible.** §7 says a running job cannot be tailed. That is true of
  `submit_job`, whose stdout is captured and returned at harvest; it is **not** true of a
  Sandbox, where `sb.exec()` returns a live stream. The committed heartbeat becomes a second
  view rather than the only one.
- **There is no `./out/` and no harvest window.** The lane harvests to `/data/harvest/...` on the
  Volume, which already survives teardown and the run clock, and the driver downloads from
  there. The whole `harvest_failed`-on-a-multi-GB-`out/` failure mode stops existing.
- **Teardown is verified, not assumed.** `sb.terminate()` runs in a `finally`, then the driver
  polls until the sandbox reports an exit code and lists any strays. §6 records a ledger that
  showed sandboxes alive minutes after they were terminated — so a successful call is not
  evidence, and a driver that trusts one is how six live sandboxes accumulated.

**The one thing a Sandbox does not give you** is Modal's unconditional `./out/` staging at a
deadline. Protection here comes from the same place it always really came from: everything is
written to the Volume as it lands. If the driver is SIGKILLed the `finally` never runs, so the
sandbox's own run clock is the last line of defence — `modal_lane.py` therefore defaults it to
900 s for a preflight and 10800 s for a lane, and you should size it to the work, not to comfort.

---

## 1 · Uploading data: 114x

`modal volume put` works from anywhere the client is installed, which includes the GPU host.

| route | measured |
|---|---|
| agent workspace `inputs=` | 0.44 MiB/s |
| **`modal volume put` from nespedgpu** | **~50 MB/s** |

California and Texas seeds (1.9 GB total) uploaded **in parallel, in 41 s**. The same payload
through the workspace path was on track for ~73 minutes.

```bash
# on nespedgpu, once:
cd /home/vitor.oliveira/PoiMtlNet
.venv/bin/python -m ensurepip --upgrade      # the venv ships without pip
.venv/bin/python -m pip install modal
export PATH=$PWD/.venv/bin:$PATH

# per account (tokens come from host.credentials; NEVER hardcode them in a file)
env MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=... \
  modal volume put poimtl-v18-data /tmp/payload /seed/<state> --force
```

**Always pass the tokens explicitly.** `modal volume put` without `MODAL_TOKEN_ID` /
`MODAL_TOKEN_SECRET` uses the host's default profile, which may be the *other* account. Two
launches died because the scripts bundle and `region_embeddings.parquet` had been uploaded to
lane 2 while the job ran on lane 1. The upload reports success either way; only the job fails.
Verify with `Volume.iterdir` on the account you are about to run on.

Three traps, all hit for real:

- **Do not delete the staging directory in the same script that uploads it.** A cleanup line ran
  while a backgrounded upload was still reading, and the file landed at 0 bytes.
- **`modal volume put` printing a checkmark does not mean the file is there.** One upload
  reported success and left nothing on the volume. Always verify with `Volume.iterdir` and
  check the byte count before depending on it.

## 2 · Ship the seed, not the engine

The built engine is 7-16 GB per state. The seed it is built from is under 1 GB, and
materialization on Modal takes ~96 s. Three compounding reductions took CA+TX from 34 GB to
~1.9 GB:

1. ship `embeddings_insample.parquet`, not `next.parquet`
2. recompress snappy to zstd (CA 916 -> 739 MiB; verify with `table.equals()`)
3. `next.parquet` is only read for two columns by the materializer: 8.8 GiB -> 1.2 MiB

**But `next_region.parquet` (7-9 GB) is NOT derivable** and must be shipped whole. It is a
straight copy from `check2hgi_dk_ovl`, engine-independent because the region tower consumes
region embeddings rather than check-in vectors. Only the joint and reg cells need it; a cat-only
job does not, which is why a cat gate can pass while every joint cell fails.

## 3 · Two durable paths: `./out/` and the Volume

**Correction (2026-08-10).** An earlier version of this section said a timed-out job loses
everything. That is wrong, and the error mattered: it was used to write off a 3.6 h California
joint run as a total loss. It was not. **Four of its five folds were on the Volume the whole
time** — `fold1`–`fold4` score JSONs and 48 per-fold metric CSVs, still there after the sandbox
was destroyed.

There are two distinct destinations, and they answer different questions.

### `./out/` — what returns to the workspace

Modal tars `./out/` plus `stdout.log` / `stderr.log` and harvests it back into `hpc/<job_id>/`.
Per the provider skill this staging is **unconditional — on success, timeout, failure, and crash
alike**. So a deadline does not forfeit `./out/`; it forfeits whatever you had not yet written
there.

That is exactly what went wrong. The harvest copy sat at the *end* of the script, after training:

```bash
bash run_lane.sh ...          # 3.6 h, killed by the run clock here
cp -r /data/repo/out/* "$J/out/"   # never reached
```

The rule is not "harvest or lose everything." It is **write to `./out/` as you go**. A job that
checkpoints every N minutes loses at most one interval to a deadline, never the run.

Keep `./out/` **small — roughly ≤100 MB compressed.** The harvest stream runs in a bounded (~2
min) window, and a multi-GB `./out/` risks `harvest_failed`, which strands the only copy on a
sandbox that then self-terminates. Deliverables and small summaries here; bulk elsewhere.

`outputs=[...]` globs select within `./out/`; `exclude=[...]` subtracts. Omit `outputs` and all of
`./out/` comes back. The run's own `stdout.log`/`stderr.log` always land but are not counted in
`output_files`.

### The Volume — what survives the sandbox

A mounted Volume is **not** part of the sandbox filesystem and is not destroyed with it. Anything
written under the mount (here `/data`) persists across jobs, across container teardown, and across
a run-clock kill. Because the job ran with `cwd=/data/repo`, every rundir it produced was already
durable — which is why four folds survived a kill I had called total.

This is the right home for anything large or resumable: engines, rundirs, per-fold checkpoints,
intermediate tensors. It also costs zero upload per submit, unlike `inputs=`.

### How to use both

| write it to | what goes there |
|---|---|
| **Volume** (`/data/...`) | rundirs, per-fold checkpoints, anything multi-GB or resumable |
| **`./out/`** | the score JSONs and small summaries you want in the workspace |

Concretely, for `run_lane.sh` with `REPO=/data/repo`: the rundir is already on the Volume, so
`HARVEST=1` only needs to copy the small score files into `./out/` — **and it should do that after
each cell, not once at the end.** The reg family's deliverable
(`docs/results/P1/region_head_*.json`) lives outside any rundir and must be copied explicitly.

### Recovering from a Volume after a kill

Nothing is lost while the Volume holds it. A cheap CPU job can copy it into `./out/` and harvest
it back:

```python
c = host.compute.create("byoc:modal", provider_params={
    "image": "...", "cpu": 4, "memory": 16384,
    "volumes": {"/data": "poimtl-v18-data"}})
c.submit_job(command='mkdir -p out && cp -r /data/repo/results/<engine>/<state>/<rundir>/metrics out/',
             intent="recover fold results left on the volume by a timed-out job")
```

The provider's `Volume.read_file` is not reachable from the local kernel (the proxy refuses the
block URL), so a job is the way to read Volume contents back.

## 4 · Always run `run_lane.sh`

Do not hand-write a training command. The night's most expensive bug was exactly that: a
hand-rolled benchmark omitted `--compile`, which the version of record passes on all three
cells. The consequences were two, and the second is worse than the first:

- the A100 looked barely faster than the A40, because the comparison was **compiled A40 vs
  uncompiled A100** — a software artifact read as a hardware fact, which nearly caused the
  entire rented-GPU plan to be abandoned;
- the sidecar records `"compile": true` as protocol, so an uncompiled cell **crosses protocols**
  against the published v17 comparands. Wrong numbers that do not crash.

`run_lane.sh` is flag-equivalent to `v18/run_wave.sh`, by a mechanical per-cell diff. Re-verified
after the 2026-08-10 audit edits:

| cell | flags |
|---|---|
| REG | identical |
| JOINT | identical |
| CAT | identical **plus `--task-a-input-type checkin`**, which is the argparse default (`train.py:541`) and therefore inert |

Two cautions when re-running that diff, both learned by getting it wrong. Anchor the block on the
**invocation**, not the first textual mention: the record names `p1_region_head_ablation.py` in a
comment first, and a parser that matches it compares comment prose and reports nonsense. And
`$ENVCOMMON` must be expanded before comparing environments or every variable inside it reads as
missing.

### A flag diff is not a protocol diff

This is the trap the earlier version of this section fell into. It concluded "flag-equivalent,
one intentional difference on REG" — but the diff it ran only compared **CLI flags**, and the
divergences that mattered were all somewhere else: the environment, the control flow, and what
the script does with the result. Six of them were live at once. When you re-verify equivalence,
diff four things, not one:

1. **flags** — the table above;
2. **the `env` prefix** — `$ENVCOMMON` puts `MTL_STRICT=1` and `MTL_CHUNK_VAL_METRIC=1` on the
   **cat and reg** cells, where the record has neither. (The old text said REG only. It is both.)
   See the note below on what `MTL_STRICT` actually does per cell;
3. **how the rundir is resolved** — the record anchors it to the launched PID at all 22 of its
   call sites and says so outright: *"Rundirs are captured by the launched PID, never by
   newest-mtime globbing (two jobs run concurrently by design)."* `run_lane.sh` globbed by mtime
   until 2026-08-10. Under §12's recommended one-job-per-seed packing, several containers share
   one Volume at `cwd=/data/repo`, and the heartbeat's `Volume.commit()` makes their rundirs
   mutually visible — so "newest" was a race that would have scored another seed's rundir and
   written a sidecar attesting to it. Now anchored, with a loud WARN if the anchor ever misses;
4. **what happens on failure** — the record checks the exit code and writes no sidecar; a
   sidecar means "this cell produced results", never "this cell was attempted".

**`MTL_STRICT=1` does not mean one thing.** `guard_finite_step` lives only in `mtl_cv.py`, so the
fail-loud non-finite abort applies to the **joint** cell alone. On cat and reg the same variable
instead hard-fails two guards that would otherwise warn: the torch-build check
(`train.py::_preflight_canon_guards`, which fires for every task) and the stride-1 overlap
provenance check (`folds.py::_warn_if_ungated_overlap`). That is a deliberate fail-closed choice
and it is stricter than the record, but read it as a **crash surface**, not a numerical one — and
do not repeat the old claim that it protects cat/reg from a silent NaN collapse. It does not.

One deliberate divergence: **`MTL_RAM_HEADROOM_GB=12` is omitted.** It exists because the A40 box
is RAM-constrained; on an H100 container the guard has nothing to protect and a lower headroom
only makes the build guard likelier to refuse a cell.

Set `TORCHINDUCTOR_CACHE_DIR` to a **persistent** path (`INDUCTOR_ROOT`, ideally on the Volume).
The container default is ephemeral, so every cell re-pays the full `torch.compile` warm-up and
compile stops paying for itself.

## 5 · Preflight: run `scripts/preflight.py`, never a hand-written list

Do not write the file list inline. It has been wrong four separate times, each costing a launch:

| launch | missing | which cells care |
|---|---|---|
| 1 | `next_region.parquet` | joint |
| 2 | stale sidecar from the failed run | joint |
| 3 | `region_embeddings.parquet` (engine ROOT, not `input/`) | joint |
| 4 | `checkin_graph.pt` | joint **and** reg |

```bash
python scripts/preflight.py --state alabama --cells cat,reg,joint || exit 9
```

The critical asymmetry: **the cat cell needs almost none of these.** It reads only
`next.parquet`, so a cat-only gate passes while joint and reg die on the same missing file. A
green gate is not evidence the other two cells can run — that mistake produced a "successful"
lane in which one of three cells worked.

Empty files count as missing (`st_size == 0`): a `modal volume put` that reported success has
landed a 0-byte file at least once.

Stale sidecars: drop any whose rundir is empty before starting. A sidecar means "this cell
produced results", never "this cell was attempted".

## 6 · Money

Billing is **per container-second**, so N parallel containers cost exactly what N serial ones do.
Wall-clock compresses for free; only total container-time bills. "One job with everything inside"
is therefore strictly worse than N jobs: same money, N times the wait. And a saturated GPU
(measured SM 96-100 %) gains nothing from running cells concurrently on one card.

### The price table

Fetched from `modal.com/pricing` on **2026-08-10**. Modal quotes per second; the per-hour column
is `×3600`. Re-fetch before any large plan — these are list prices and they move.

| resource | $/second | **$/hour** |
|---|---:|---:|
| B300 | 0.001972 | 7.099 |
| B200 | 0.001736 | 6.250 |
| H200 | 0.001261 | 4.540 |
| **H100** | 0.001097 | **3.949** |
| A100-80GB | 0.000694 | 2.498 |
| **A100-40GB** | 0.000583 | **2.099** |
| L40S | 0.000542 | 1.951 |
| A10 | 0.000306 | 1.102 |
| L4 | 0.000222 | 0.799 |
| T4 | 0.000164 | 0.590 |
| CPU, per physical core (min 0.125) | 0.0000131 | 0.0472 |
| memory, per GiB | 0.00000222 | 0.00799 |

The bill is **GPU + CPU + memory**, all three, per container-second:

```
rate($/h) = gpu$/h + cores × 0.0472 + GiB × 0.00799
```

`scripts/modal_lane.py` carries this table and prints the computed rate before it submits, so
the number in a plan is calculated rather than remembered.

### Correction (2026-08-10): the earlier correction was itself too low

This section used to say an A100-40GB at 8 CPU / 64 GB bills "about $2.73/h" and that ignoring
CPU+memory understated a plan by "roughly 29 %". Both figures are wrong:

```
2.099 (A100-40GB) + 8 × 0.0472 (CPU) + 64 × 0.00799 (memory)
  = 2.099 + 0.377 + 0.511 = $2.988/h
```

so the real rate is **$2.99/h**, and the understatement against the $2.10 headline is
**42 %**, not 29 %. An H100 on the same shape is **$4.84/h**, not $3.95.

`EXECUTION_PLAN.md` §5 priced phase C at the bare GPU rate, so it inherits the whole 42 %:

| | as planned | at the real rate |
|---|---:|---:|
| phase C, both lanes (23 container-h) | $48.55 | **$68.72** |
| phase A, H100 1.87 h | $7.39 | $9.05 |
| total | $57.54 | **$79.37** |
| against $60 of credit | +$2.46 | **−$19.4** |

The plan does not close at the real rate. Two levers before adding funds. **Free credits are
$30/month per workspace and they recur** — the plan treated $30 × 2 accounts as a one-time $60,
so work that straddles a month boundary gets a second allocation. And **CPU/memory is a request,
not a constant**: 4 CPU / 32 GB drops the A100-40GB container to $2.54/h, 15 % off, though the
image pins `OMP_NUM_THREADS=8` and the data path wants the cores, so measure before trimming.

### Plan limits, and the balance query that does exist

Two of `EXECUTION_PLAN.md` §7's open risks are closed:

- **Concurrency is not a constraint here.** The Starter plan allows **100 containers + 10 GPU
  concurrency** (Team: 5000 + 50). The plan's 3-wide fan-out was never at risk of queueing, and
  since billing is per container-second, 9-wide finishes phase C in 2.59 h for exactly the same
  money as 3-wide's 3.83 h.
- **"The SDK exposes no balance query" is out of date.** Client 1.5.3 ships `modal billing`:

  ```bash
  modal billing summary
  modal billing report --for "this month" --show-resources
  modal billing report --for "last month" --csv > spend.csv
  ```

  Read the ledger from Modal instead of reconstructing it from job walls.

  ⚠ **But the ledger posts in discrete blocks, so you cannot measure a burn rate from it over
  minutes.** It sat at exactly `$31.37` across a four-minute window mid-run, which makes a
  short-sample rate read as `$0.00/h`; an earlier sample straddling a block boundary read
  `$7.4/h` for a container whose real rate was `$4.77/h`. Sample over ≥15 min, or compute the
  rate from the container spec instead. The one thing the ledger gives you exactly is the
  **credit balance**, the moment `Billed` goes non-zero: `metered − billed` — that is how this
  workspace's balance was pinned at exactly **$30.03**.

  ⚠ **Credit is workspace-wide, and another session can spend it.** On 2026-08-10 a second,
  uncoordinated app (`poimtl-fl-joint`, two A100 containers) burned **$11.72 — 42 % of the
  night's spend** — alongside this session's own runs, and pushed the workspace past its credit
  while a long cell was mid-flight. Before committing to a long run, check
  `modal container list` for **foreign apps**, not just your own ledger. And when you sweep,
  terminate **by sandbox id**: `close()` is host-scoped and would kill the other session's work.

### ⚠ Correction 2026-08-10 (third): on a GPU container, requested CPU/RAM is a FLOOR, not a cap

The rate formula above — `gpu + cores × 0.0472 + GiB × 0.00799` — is right for a **CPU-only**
container and **understates a GPU container by about half**. Measured against the ledger on the
texas s7 joint (H100, requested 8 CPU / 128 GiB, ran 1.83 h):

| line | modelled from the request | actually billed | ratio |
|---|---:|---:|---:|
| H100 | $7.23 | $7.22 | 1.00 |
| CPU | $0.69 | $2.07 | **3.0×** |
| memory | $1.87 | $5.61 | **3.0×** |
| **cell total** | **$9.79** | **$14.92** | **1.52×** |

Exactly 3.0× on **both** lines. The reading that fits: a GPU slot carries the host's per-GPU
share of CPU and RAM (an 8-GPU H100 node ÷ 8 ≈ 24 cores), so asking for 8 cores and 128 GiB does
not buy you a cheaper container — it only sets a minimum. The alabama A100 cells show the same
effect at roughly 2.5–2.7×.

**Consequences, and they are not small.** The effective rate for that cell was **$8.15/h**, not
the $5.35/h printed before submit. Every budget built on the list formula is ~50 % optimistic for
GPU work: what was planned as "TX 7+100 = $22.97" is really ~$35, and "CA 7+100 = $17.88" is
really ~$27 — neither fits a $28.86 credit. `scripts/modal_lane.py` now applies a measured
`GPU_HOST_SHARE = 3.0` to the CPU/memory terms of GPU tiers (CPU-only tiers are unaffected) and
reproduces the billed figure. Treat that constant as an **empirical measurement to re-check**,
not a documented rate — Modal publishes no such multiplier.

Corollary: **trimming `--cpu` / `--memory` on a GPU container saves nothing.** The earlier advice
in this section that 4 CPU / 32 GB would shave 15 % off an A100 is withdrawn. Ask for the memory
the job actually needs (the CA/TX MTL build peaks ~66 GB, so 128 GiB is the right request) and
spend the effort on picking the right card instead.

### ⚠ How to estimate a cell — and the four ways this manual got it wrong

Every cost figure in this study before 2026-08-10 was produced by extrapolation, and each
extrapolation failed in a different way. If you are an agent about to quote a price, read these
four before you do; they are all measured, and together they moved one estimate by **3×**.

**1. Requested CPU/RAM is a floor on a GPU container (3×).** Covered above: modelled $9.79,
billed $14.92. Never cost a GPU cell from the request alone.

**2. Do not transfer a speed ratio between states.** The A40→A100 ratios (cat 2.5×, reg 1.3×)
were measured on **alabama**, whose region head has 1109 classes and whose epoch is 10 batches.
Applying them to florida — 3.5 GB of `next.parquet`, a far wider softmax — produced a 50-minute
estimate for work that is taking about two hours. A ratio is a property of a *cell*, not of a
pair of cards.

**3. Packing only pays when the GPU is IDLE. Measure it, do not assume it.** The rule the earlier
sections give — "billing is per container-second, so N cells in one container cost the wall, not
the sum" — is true only when the cells actually interleave. The GPU is a serial resource: if it is
already busy, packing converts nothing and you pay the same compute plus a bigger RAM
reservation.

| workload | util of ONE cell | packing verdict |
|---|---:|---|
| large-state **joint** | 89–99 % (A40 98–100 %) | **never pack** — zero throughput gain, and the extra RAM reservation loses money |
| cat/reg **beside** a long joint | reg ~65 % | packs well — they hide inside the joint (2.98× measured at alabama) |
| **4 × florida cat/reg on one A100** | ~99 % combined | **packs well** — cheapest of the options, see below |

**The florida measurement.** Four cat/reg cells on one A100-40GB run at **8.4 s/epoch each** →
420 s/fold → **~35 min per cell**, and because all four run concurrently the **lane wall is also
~40 min**, not the sum. Two consequences that must be read together:

- *per cell*, packed is **1.15× slower** than the same cell alone on the free A40 (35 vs 30 min) —
  the A100 is ~2.5× faster per cell, but split four ways each one falls slightly behind the A40;
- *per batch of four*, packed finishes in **~40 min for ~$3.3**, against **~2 h serially on the
  A40** and **~$5.3 in four separate containers** (which would be ~21 min, paying the sum of four
  container lives instead of one).

So for cat/reg the ranking is: **packed 1 container (cheapest) < 4 containers (fastest, +60 %) <
A40 (free, slowest)**. Packing is right here and wrong for the joint, and the discriminator is
whether **one** cell already saturates the card.

**Before packing, get the number for free:** run one cell of that family on the A40 and read
`nvidia-smi --query-gpu=utilization.gpu`. If a *single* cell sustains >85 %, packing buys nothing.

⚠ **Read the progress bar correctly, or you will mis-estimate by 3×.** The trainer's bar is
**per fold** (`Epoch n/50`), not per run: 50 epochs × 8.4 s = 420 s is *one* fold of five. Reading
it as the whole cell produced a "~2 h" ETA for a run that took ~40 min, mid-flight, and nearly
triggered a needless kill-and-relaunch. Multiply by `--folds`, and cross-check against
`folds_done` in the heartbeat.

**3b. The bottleneck may not be the GPU at all — check before you pay for silicon.** The `reg`
cell scores its validation metric **on CPU** by design: `p1_region_head_ablation` logs
`scoring val metric on CPU (full val logit ≈ 4.8 GB, N_val=254883 × C=4703) to avoid GPU OOM at
overlap scale`. That phase does not touch the GPU. Measured on florida: **455 s/fold packed 2-wide
on an A100 against 332 s/fold alone on the A40** — 1.37× *slower* on the faster card, because the
container had **8 cores against the A40 box's 32** (i9-14900K) and `OMP_NUM_THREADS` was pinned to
8 in the image.

And it is billed at ~3× the request (§"floor, not a cap"), so that run **paid for ~24 cores while
the container held 8** — on the cell whose bottleneck is CPU.

⚠ **Correction, measured 2026-08-10 15:08.** The first fix here was to export
`OMP_NUM_THREADS=$(nproc)` in the job, on the theory that the container had the host's ~24 cores
and only the thread cap was holding it back. It does not: the container prints
`CPU: nproc=8 OMP_NUM_THREADS=8` for a `--cpu 8` request, so the cgroup really does hand you what
you asked for and `$(nproc)` is a no-op. `modal_lane.py` still exports and prints it — printing it
is how this was caught, and it becomes live the moment `--cpu` goes up — but **the actual lever is
`--cpu N`, not the thread cap.**

**Open, and cheap to settle:** whether raising `--cpu` to the ~24 you are already billed costs
nothing (a *floor*) or triples the CPU line (a *multiplier*). Both fit the single 3× observation.
Run one cell at `--cpu 24` and compare the CPU line in `modal billing report --show-resources`
against this run's. Until that is measured, do not assume more CPU is free. It matters most at
CA/TX, where the region head has 8501/6553 classes and that CPU-scored logit tensor is
correspondingly larger.

**3b-fix. `MTL_CHUNK_VAL_METRIC=1` looks like waste on small states — it is, but it STAYS. The
equivalence argument did not survive measurement.** Written up in full because the reasoning is
the useful part, and because the first version of this section asserted the opposite.

The flag forces p1 to move the full `[N_val × C]` val logit to CPU and score it there. It is a
real OOM guard at texas (20.1 GB) / california (19.9 GB) scale — but
`_should_chunk_val_metric` **already auto-enables** above `P1_S2_AUTO_BUDGET_GB` (4 GB), so
forcing it adds nothing there and pushes a tiny tensor onto the CPU for the small states
(alabama 0.09 GB, arizona 0.25 GB, istanbul 0.11 GB — C=520, not the ~1500 first written here).
Measured cost: **arizona reg 343 s on a rented H100 against 185 s alone on the A40**, the only
family slower on faster silicon.

> ⚠ **That comparison was unfair to the container and it took a while to notice.** The 343 s was
> measured at `--cpu 8`; the A40 box has **32 cores**, and this cell's bottleneck is CPU-side
> scoring. Same container, same cell, varying only threads: **8 -> 41 s, 32 -> 23 s (1.78x),
> GPU-scored -> 18 s**, all three returning identical metrics. A rented reg cell with `--cpu 32`
> is at **~1.04x the A40 wall**, not 1.85x. It is still not worth renting — 32 cores cost
> $4.53/h against 8 cores' $1.13/h, so you would pay ~$62 for parity with a free machine — but
> the reason is price, not speed. **Match the container to the cell's bottleneck: a config sized
> for the joint (GPU-bound, 8 cores fine) starves the reg.**

**So it was dropped — and then restored the same day.** The justification was that scoring is
device-independent "by construction", because `_rank_of_target` computes
`1 + #{logits strictly greater}`, an exact integer count. That is true, and **it does not cover
the metric this cell reports.** `top10_acc` comes from `_top_k_accuracy`
(`src/tracking/metrics.py:102-110`), which uses `logits.topk(k).indices` — and the tie-break *at
the k-boundary* is a kernel/arch detail. Only mrr/ndcg go through the strict-`>` rank.

Measured on an **H100**, the card these cells run on
(`scripts/check_cpu_gpu_scoring_equiv.py`):

| case | boundary ties | rows where top-k index set differs | worst Δ | |
|---|---:|---:|---:|---|
| continuous logits — AL / AZ / IST / TX shapes | **0.0 %** | 0 | ~1e-9 | pass |
| heavy exact ties (`randint 0-5`) | 100 % | 0 | 4.7e-10 | pass |
| **exact ties AT the k-boundary** | 100 % | **19 950 / 20 000** | **3.0e-04** | **300× over** |

`top10_acc` came out `cpu 0.009850` vs `gpu 0.009550` in the worst case. The reporting quantum is
4 dp on a percentage = **1e-6 on the 0-1 scale** (an earlier version of this section said 1e-4 and
claimed a 3350× margin; the real margin on the passing cases is ~34×).

**Verdict: keep forcing the CPU path.** The failure needs an exact fp32 tie at the top-k boundary,
which continuous logits do not produce and which p1's fp32 eval does not manufacture — every
banked reg cell in the study is CPU-scored, and the prize was ~40 s per small-state cell. Mixing
scoring devices inside one pooled n=20 cell is not worth that. `P1_GPU_VAL=1` opts out if you have
evidence for your own shapes. *(The "rate on real reg logits is unmeasured" clause that used to
justify this is now obsolete — it was measured at **0 / 100 448** on both boundaries; see the
table below. The flag stays forced for homogeneity, not for fear of ties.)*

**The right fix is a different one — and it is now IMPLEMENTED and MEASURED (2026-08-10).** p1
streams the val metric the way `mtl_eval.py` already does for the joint (`_streamed_cls_metrics`,
`src/tracking/metrics.py`): per-row accumulators, O(N) memory, no `[N × C]` buffer on any device.
Two independent switches, because they answer two different questions:

| env | default | what it controls |
|---|---|---|
| `P1_STREAM_VAL` | **1** (ON for `C > 256`) | stream vs materialise the full logit. **Bit-identical** on the same device — 0.000e+00 across 8 shapes incl. forced boundary ties and batch size 1 (`/tmp/stream_equiv.py` pattern). Removes the OOM at any scale. |
| `P1_STREAM_GPU` | **0** (score on CPU when `_chunk_val`) | *where* the per-row ops run. The only part that is not bit-identical, and the reason the default stays OFF. |

**The device question, answered on REAL logits instead of by argument** (arizona reg, H100,
`P1_SCORE_AB=1` — which scores the *same* logits on both devices inside one run, so the comparison
cannot be confounded by `--compile` nondeterminism the way a fresh-run-vs-banked-value diff would):

> ⚠ **The two tie rows below were measured at EPOCH 0 ONLY and that gave a false all-clear —
> corrected further down. Re-measuring every epoch found real ties.** Kept as recorded because the
> mistake is the lesson.

| measurement (epoch 0) | result |
|---|---|
| boundary ties, 10th == 11th | **0 / 100 448** (0.0000 %) |
| boundary ties, 5th == 6th | **0 / 100 448** (0.0000 %) |
| same logits, CPU vs GPU, worst Δ any metric | **5.96e-08** (`ndcg_5`) — 17× *under* the 1e-6 quantum |
| same logits, CPU vs GPU, `top10_acc` | **bit-identical** to 10 dp (0.3960158527) |
| end-to-end run diff, 67 numeric keys | **65 identical**, 2 at ≤ 2.98e-08 (fp32 sum-reduction order) |
| **wall, 1 fold × 8 epochs** | **57 s CPU → 18 s GPU = 3.2×** |

**CORRECTION, same day — trained fp32 logits DO produce boundary ties, and the epoch-0
diagnostic missed them.** A review pointed out that the banked number comes from `per_metric_best`
over ALL epochs while the check ran once, at epoch 0. Re-running the same arizona cell with the
diagnostic on every epoch:

| epoch | 10th == 11th | 5th == 6th |
|---|---|---|
| 0 | 0 / 100 448 | 0 / 100 448 |
| 2, 4, 5 | 0 / 100 448 | **1 / 100 448 (0.0010 %)** |

One tied row is small but not negligible against the reporting quantum: it can move `top5_acc` by
up to 1/100 448 = **9.96e-06**, ~10x the 1e-6 quantum, so it can change the 4th decimal of a
reported percentage. The **headline reg metric is Acc@10, which showed 0 ties in every epoch** —
but `top5_acc` is also banked in `per_metric_best`, so the precondition is not clean.

**Verdict: `P1_STREAM_GPU` stays OFF for study cells, and the 3.2x is not collectable on them.**
The earlier "measured safe, opt in when the wall is worth it" was written from the epoch-0 sample
and is withdrawn. `run_lane.sh` sets `MTL_STRICT=1` on every cell, so enabling GPU scoring in the
lane now **aborts the cell** at the first tied epoch rather than banking a number that may not
match its CPU-scored siblings — which is the behaviour we want.

**The lesson is about sampling, not about ties.** A precondition checked once per run, on the
epoch least likely to violate it (an untrained model's logits are the most spread out they will
ever be), reports the answer you hoped for. Check it wherever the quantity you bank is produced.

**The precondition is checked per run, not assumed.** The epoch-0 diagnostic measures the tie rate
on the actual logits at both boundaries (via `topk(11)`, 2.9 ms/batch — a full `sort` costs 83.5 ms
and would have added ~26 min/fold at texas). Under `P1_STREAM_GPU=1` a non-zero rate raises a
`WARNING` naming the cell as possibly non-homogeneous with its CPU-scored siblings, and hard-fails
under `MTL_STRICT=1`. The arizona zero does not have to be extrapolated to texas — texas will
measure itself and say so.

**Two lessons worth more than the flag.** A "by construction" argument must be checked against the
metric you actually *report*, not the one that makes the argument work. And an equivalence checker
that skips a key it cannot find (`if k in m_cpu`) reports coverage it does not have — the first
version silently never tested `f1` because it asked for `f1_macro`.

**3c. For GPU-serial work, container count changes the WALL, not the price.** Costed over the 11
missing istanbul+arizona cells: 1 A100 with everything, 2 A100 split by state, and 4 A100 split by
seed all come to **$4.75** — identical, because the joint cells saturate the card and the total
GPU work is the same however you slice it. Choose the split for latency and blast radius, not for
cost. (Packing only changes the price when the cells leave the GPU idle — §3.)

**4. Rent the bottleneck, not the cheap cells — but "bottleneck" means wall you cannot recover.**
The A40 is free and idle between waves, so a large-state **joint** is worth renting (6.24 h →
1.82 h on an H100, measured). cat/reg are worth renting only when the A40 is *busy* and you need
the wall: four of them cost ~$3.3 and 40 min rented, versus free and ~2 h queued behind a wave.
Ask what the free card is slow at **and** whether you can wait for it.

### Image builds bill, and a per-run estimate does not include them

Measured on lane 2, 2026-08-10: two runs (a CPU preflight and the alabama s100 lane) estimated
**$0.038 + $0.237 = $0.275** of container time, while `modal billing summary` reported **$0.38
metered**. The ~$0.10 gap is the **image build** — the torch+PyG image pulls roughly 6 GB of CUDA
wheels and that build runs on Modal's infrastructure, on Modal's clock.

It is a one-off per image recipe, not per run, and it is cached afterwards: the second run
created its sandbox in seconds. But budget it once per account and once per edit to the image
definition, and remember that **`modal_lane.py`'s printed cost covers container time only**. The
ledger is the truth; the estimate is a planning aid.

(That whole session — image build, a preflight, and a complete 5-fold cat + reg lane — came to
$0.38 metered, entirely inside the $30/month free credit: **$0.00 billed**.)

Set `run_timeout_s` with margin. A job that hits the run clock is killed and lands as
`state == 'timed_out'` with whatever was in `./out/` **already harvested** — the deadline ends the
run, not the results. Anything on a mounted Volume survives too. What is lost is only what lived
in the sandbox filesystem outside `./out/`.

Close handles: `c.close(intent=...)` after the last job on a handle. An idle sandbox
self-terminates after 15 minutes, but that is 15 minutes of billing per forgotten handle.

**A failed job leaves its sandbox warm and billing.** Two launch failures on 2026-08-10 each left
an idle sandbox burning its full 15-minute window *after* the job had already exited. Check
`host.compute.ledger()` after any failure.

`c.close()` is **host-scoped**: it terminates every sandbox for the target and cancels running
jobs. To kill idle leftovers while a real job continues, terminate by id instead:

```python
sb = modal.Sandbox.from_id("sb-...")   # in the provider kernel
sb.terminate()
```

Verify against Modal, not the ledger — the ledger is cached and showed all three sandboxes alive
for minutes after two were terminated. `Sandbox.poll()` returns `None` while running and an exit
code once stopped.

## 7 · Job status is not always the truth

- `status: "orphaned"` on the SSH target is usually a stale poller, not a dead job. Check the
  actual process (`pgrep`) or the artifact on disk before concluding failure. Several uploads
  reported orphaned while running to completion.
- `job.result()` raises `JobPending` until the poller harvests; park on `wait_for_notification`
  rather than looping on it.
- Volume writes from a running job are **not visible** to a second sandbox until committed, so
  progress cannot be tailed from outside. Print progress from inside the job instead.

## 8 · Monitoring: let the run report on itself

**Prefer in-run logging to an external monitor.** A separate monitoring container cannot see into
a running job — Modal volume writes are not visible across sandboxes until committed — and
`Sandbox.exec` into a live sandbox fails outright once the task ends (`ConflictError: Task has
already finished with status terminated`). Worse, an external monitor costs a second container
and tells you nothing after the job is gone, which is precisely when you need the post-mortem.

`run_lane.sh` therefore reports on itself, writing into the **harvested** directory so the
evidence travels back with the results and survives a run-clock kill:

- **`out/heartbeat.jsonl`** — one JSON line per minute: GPU utilization, memory, temperature,
  decoded throttle reasons, how many training processes are alive, `folds_done`, and the size of
  `out/`. This is the timeline you read when a job dies at 3.6 h.
- **`out/logs/<state>_s<seed>_<family>.log`** — on failure, the tail of that cell's stdout is
  copied into `out/`. Without it, diagnosing a failed cell costs an entire extra job just to read
  a log file off the volume. That happened; it is avoidable.
- **`out/logs/<state>_s<seed>.log`** — the lane log, harvested at the end.

`scripts/monitor.sh` remains useful for the **local A40**, where you have a shell on the machine:
it lists drivers and trainers, flags two trainers on the same state+seed (a duplicate wave was
started once while an older driver was 11/12 through the same seed), counts score files written
in the last 30 minutes, and decodes the GPU throttle bitmask. `utilization.gpu` is a liar — it
reads 100 % while clocks are capped. On first run it found **the A40 at 88 °C with `SW_THERMAL`
active**, meaning every wall measured on that card while hot is slower than its own reference.

It is container-portable now (falls back to `/proc` when `pgrep`/`free` are absent, and takes
`DATA_FS=` for the filesystem to check), but on Modal the heartbeat is the better instrument.

## 9 · Second account

**Corrected 2026-08-10.** This section used to say the second account cannot submit jobs. That is
true of *one* path and false in general, and the distinction matters because it decides whether a
whole lane is usable.

- **Through the agent harness:** `host.compute.create` binds to the registered `byoc:modal`
  target, which is the primary account. There is no credential selector on that API, so the
  second account is upload-only there. To submit through the harness, register it as a
  Modal-type compute provider first.
- **Through the `modal` client:** the second account can do **everything** — submit, run,
  monitor, tear down. The limitation is a property of the harness's provider registry, not of
  Modal and not of the account. `scripts/modal_lane.py` takes that path and needs nothing but a
  token pair.

Verified on `vitor-h-oliveira` (lane 2) on 2026-08-10: `modal volume ls`, `modal app list`,
`modal container list` and `modal billing` all authenticate and answer.

**Always pass tokens explicitly and know which account you are on.** Two launches died because a
scripts bundle went to lane 2 while the job ran on lane 1; the upload reports success either way.
`modal volume ls <vol> /` is the cheapest way to confirm you are looking at the account you think.

### Which account holds what (2026-08-10)

| | lane 1 `vho2009` | lane 2 `vitor-h-oliveira` |
|---|---|---|
| token | not in the repo | `v18_2/.env` |
| staged | california, alabama (the §10 AL run happened here) | texas only: `seed/texas`, `texas_nr` (9.3 GiB), `texas_keys`, `texas_graph` |
| `output/` engines materialized | yes | **no** — `/data/repo` is `docs research src scripts pipelines`, no `output/`, no `.venv` |
| spend | the ~$13 night | **$0.00 metered, $0.00 billed** — never ran a GPU job |

A state can only be run on the account that holds its engine, or its seed plus the ~96 s
materialization. Check before planning a lane: `modal volume ls poimtl-v18-data /seed`.

---

## 10 · Measured numbers (2026-08-10)

The first rented-hardware figures produced with the corrected script. Everything earlier in this
session was measured without `--compile` and is void.

Alabama seed 7, all three cells **in parallel on one A100-SXM4-80GB** (lane wall 564 s against
1678 s for the same three cells run serially on the A40):

**end-to-end packing gain: 2.98x.**

That is the one ratio this run supports. The per-cell walls below are recorded for completeness
but are **not hardware ratios**:

| cell | A40 (serial, uncontended) | A100 (3-way contended) |
|---|---:|---:|
| cat | 322 s | 154 s |
| reg | 189 s | 197 s |
| joint | 1167 s | 563 s |

The heartbeat shows three training processes sharing the card for the first ~125 s at 96-99 %
utilization. Every A100 wall in that column therefore includes contention, while every A40 wall
is uncontended. Dividing one by the other measures *packing*, not silicon. In particular the reg
column must not be read as "reg is slower on rented hardware": its 197 s is dominated by the
window in which it shared the GPU with two other cells. A per-cell hardware ratio needs each cell
run alone on each card, which has not been done.

```
t=63    cells=3  util=96%   7062 MiB  51C
t=125   cells=3  util=99%  14120 MiB  54C
t=307   cells=1  folds=1   util=90%
t=549   cells=1  folds=5   util=0%
```

What the packing gain does establish: cat and reg together (154 + 197 s of contended work) hide
almost entirely inside joint's 563 s, so the lane costs barely more than its longest cell. That
is the property worth planning around.

**On cross-hardware agreement.** Alabama now has three seeds in the v18 aggregate, seeds 0 and 1
from the local A40 and seed 7 from a rented A100, all under the same protocol and scored by the
same scorers:

| seed | stl_cat | stl_reg | db_cat | db_reg | machine |
|---:|---:|---:|---:|---:|---|
| 0 | 30.7654 | 69.9956 | 30.6985 | 69.5928 | A40 |
| 1 | 30.8745 | 70.1929 | 30.6275 | 69.7112 | A40 |
| 7 | 30.7304 | 70.2084 | 30.7022 | 69.6281 | A100 |

State the evidence carefully. Seed 7 lies **outside** the seed-0/seed-1 interval on three of the
four metrics (only db_reg is between them), so "the rented seed falls inside the local spread" is
false and must not be claimed. Nor would containment mean much if it held: with two local seeds,
a third exchangeable draw lands between them only a third of the time.

What the numbers do support is that the deviations are **small against the noise of the cells
themselves**. Seed 7 sits 0.035 points below the local minimum on stl_cat, against a per-fold
standard deviation of 1.19 within that very cell -- roughly 0.03 sd. The db_cat excess is 0.004
points against a per-fold sd of 1.09. The machine-to-machine differences are two orders of
magnitude smaller than the fold-to-fold variation the metric already carries.

That is consistent with pooling but does not establish it. A clean test is one cell run on both
machines with `--compile` on each side and everything else fixed; three seeds spread across two
machines cannot separate a seed effect from a machine effect. Until that test exists, record the
machine in each sidecar (`lane_host`, written by `run_lane.sh`) and do not assert equivalence.

Note the device: Modal served an **A100-SXM4-80GB** for a request of `A100-40GB` on 2026-08-09
and an **A100-SXM4-40GB** for the same request on 2026-08-10. Budget the tier you asked for and
read the actual device from the job's own `nvidia-smi` line — `modal_lane.py` records it in
`run_metadata.json` as `device_served`.

### Seed 100 — the missing alabama cell, run 2026-08-10 on **lane 2** via `modal_lane.py`

Seeds 0/1/7 were already banked, so **100 was the one alabama cell missing from n=20**. Run
**serial** rather than `PARALLEL` on purpose: with only two cells the packing gain is small, and
serial is what makes the per-cell walls uncontended and therefore interpretable.

| | value | fold SD | per fold | wall |
|---|---:|---:|---|---:|
| **cat** macro-F1 | **30.7296** | 1.256 | 32.31 / 31.36 / 29.06 / 29.44 / 31.48 | 127 s |
| **reg** Acc@10 | **70.0727** | 3.483 | 71.62 / 69.30 / 73.45 / 71.57 / 64.43 | 149 s |

Lane wall 280 s, container 286 s, **$0.237** at the real $2.988/h. Exit 0; sandbox terminated and
verified (`strays=[]`, and `modal container list` independently empty). Archived to
`docs/results/closing_data/v18_2/modal_runs/alabama_s100_lane_20260810_021901/`.

Alabama with all four seeds, machine recorded:

| seed | stl_cat | stl_reg | machine |
|---:|---:|---:|---|
| 0 | 30.7654 | 69.9956 | A40 |
| 1 | 30.8745 | 70.1929 | A40 |
| 7 | 30.7304 | 70.2084 | A100-SXM4-80GB (3-way `PARALLEL`) |
| **100** | **30.7296** | **70.0727** | **A100-SXM4-40GB (serial)** |
| **mean, n=20** | **30.775** | **70.117** | |

The seed-100 addition does not change the verdict above, and it is worth being explicit about
why. Grouped by machine, cat is 30.820 (A40, seeds 0/1) against 30.730 (A100, seeds 7/100) — a
gap of 0.090, about **0.07** of the 1.256 fold SD; reg is 70.094 against 70.141, a gap of 0.046
against a 3.483 fold SD. Both are far inside the noise the cells already carry. But **seed and
machine remain perfectly confounded** — the two local cells are seeds 0/1 and the two rented ones
are 7/100 — so a machine effect and a seed effect still cannot be separated. Four seeds across
two machines is no better at that than three was. The clean test is unchanged and still undone:
**one seed, both machines**. Note also that `replication_gate.md` cannot be run as written — the
`data/alabama_s0_cat.json` comparand it cites was deleted on 2026-08-10.

### Small states on H100 — measured 2026-08-10, use these instead of extrapolating

arizona s7, three families packed on one H100 (`PARALLEL=1`):

```
lane wall 659 s   VRAM peak 13.9 GiB / 79.6   median util 75 %   no throttle
cat   145 s  (A40 296 s)  = 2.04x faster
joint 659 s  (A40 1133 s) = 1.72x faster   <- clears the 1.39x H100 break-even
reg   343 s  (A40 185 s)  = 1.85x SLOWER   <- the CPU-scoring path, see section 3b-fix
```

The 75 % median utilisation is what makes packing worthwhile here: a small state leaves the card
with room, unlike a large-state joint at 89-99 %. Projecting the remaining eight cells from this
measurement (rather than from alabama-derived ratios) gave $5.15; the actual bill was **$3.51**,
32 % under — extrapolated ratios had been optimistic in the other direction all day, so measure
one cell of a new shape before costing the rest.

Eight cells, three H100 containers in parallel, one per state+seed:

| container | cells | wall |
|---|---|---:|
| arizona s100 | cat+reg+joint | 518 s |
| istanbul s7 | reg+joint | 657 s |
| istanbul s100 | cat+reg+joint | 622 s |

Also: cut the run clock to ~2.5x the projection. Left at the 10800 s default these three would
have carried a $59.55 worst case; at 2700 s it was $14.90.

### Per-cell speed, with `--compile` on both sides

The first legitimate A40→A100 per-cell comparison in this study; it supersedes the void 2.42×.

| cell | A40 | A100 (serial) | ratio |
|---|---:|---:|---:|
| cat | 322 s (s0) / 325 s (s1) | **127 s** | **≈2.5×** |
| reg | 189 s (s0) / 169 s (s1) | **149 s** | ≈1.2× |

Two caveats, both of which *understate* the A100:

- its inductor cache was **cold** (first cell on that account), so the wall includes the full
  `torch.compile` warm-up — see §13 on why sharing that cache across cells is opt-in;
- the A40 reference walls come from `run_wave.sh`, which runs **istanbul and alabama 2-wide**, so
  they may carry contention of their own — and `monitor.sh` has caught that card at 88 °C with
  `SW_THERMAL` active, at which point every wall it produces is slower than its own reference.

The cat/reg split is the useful part: reg peaked at ~1.1 GB and 65 % utilisation on the A100, so
it is not GPU-bound and rented silicon buys it little. **Rent for cat and joint; reg is nearly as
cheap at home.**

## 10b · O rundir viaja com o resultado

`score_all.py` **nao usa os numeros do sidecar**. Ele le o sidecar apenas para o mapeamento
`(estado, seed, familia) -> rundir` e depois releh cada valor de dentro do rundir. Uma celula que
roda no Modal deixa o rundir no volume, entao o sidecar sozinho produz:

```
seed 7   stl_cat=None   warn=['cat sidecar present but stl_cat_ceiling_score.json unreadable']
```

Perda silenciosa: o A40 pula a celula (o sidecar existe) e a agregacao nao tem o numero.

A solucao esta **no script**, nao numa etapa manual. `harvest_rundir_scores()` copia cada score
JSON para `out/rundirs/<caminho literal do rundir>/<nome>`, e `push_to_host()` espelha essa
arvore no host. O destino e uma copia literal do caminho de origem, sem adivinhacao.

Isto e novo e **nao foi usado no seed 7**. Aquela lane rodou com o `OUT` padrao (`v18_2`), e os
sidecars em `v18` mais os quatro score JSONs foram escritos depois, por um passo separado e
manual -- exatamente a etapa que esta funcao existe para eliminar. O seed 7 e portanto a prova do
problema, nao da solucao; a primeira lane a exercitar o caminho automatico ainda esta por rodar.

Isso importa: a versao anterior derivava o destino do campo `rundir` de dentro de cada JSON, e
uma lane paralela produziu **dois** rundirs da mesma familia (`..._83` da tentativa serial,
`..._134` da paralela). O arquivo foi para o errado.

### Baixar um rundir inteiro do volume

`modal volume get <vol> <diretorio> <destino>` **nao entrega o diretorio** neste volume (cliente
1.5.3). O que foi medido, em `/seed/california`, que contem tres parquets:

| arquivo no volume | tamanho |
|---|---:|
| embeddings_insample.parquet | 739,3 MiB |
| sequences_next.parquet | 102,0 MiB |
| region_embeddings.parquet | 3,1 MiB |

O comando reportou `Finished downloading files to local!` e escreveu **um unico arquivo de
775.257.519 B (739,3 MiB)** -- exatamente o tamanho do maior parquet, nao a soma dos tres
(~844 MiB). Ou seja: escreveu **um** dos arquivos no caminho de destino, nao os tres, e nao criou
diretorio algum. As outras quatro sintaxes testadas (destino inexistente, `--force`, barra final,
caminho remoto sem barra inicial) todas falharam com `[Errno 21] Is a directory`.

O mecanismo exato nao foi determinado (nao verifiquei se o destino termina com o ultimo ou o
primeiro arquivo enumerado). O que esta estabelecido e o suficiente para a regra: **nao confie em
`volume get` para trazer um diretorio** -- ele nao falha, apenas devolve menos do que voce pediu.

Ler arquivo a arquivo pela API tambem e ruim: um diretorio reportando `size > 0` quebrou duas
tentativas, e a terceira levou 7 minutos para 3,7 MiB.

**O caminho que funciona** e um job que empacota e devolve pelo harvest:

```python
c.submit_job(command='cd /data/repo && tar czf "$(pwd)/out/rd.tgz" <rundirs...>',
             intent="empacotar rundirs", run_timeout_s=600)
```

8,5 MiB voltaram em **62 segundos** assim. Nao tente mover o tarball pela linha de comando do
ssh: acima de ~100 KB da `E2BIG`, e enviar em blocos truncou silenciosamente (92 KB de 8,9 MB
chegaram).

## 11 · Never leave a container alive: `scripts/run_modal_cell.py`

A finished or crashed job **leaves its sandbox warm and billing** until the 15-minute idle window
closes. On 2026-08-10 a single sweep terminated **six** live sandboxes; `host.compute.ledger()`
had listed two. The ledger under-reports, so never conclude "nothing is billing" from it.

Submit through the wrapper rather than by hand:

```python
from run_modal_cell import run_cell, finish
res = run_cell(host, state="florida", seed=7, gpu="A100-40GB", parallel=True)
# ... park on wait_for_notification ...
out = finish(host, payload, state="florida", seed=7, gpu="A100-40GB", parallel=3)
```

`finish()` does three things in a fixed order, and the last one is in a `finally` so it runs on
success, failure, timeout and interrupt alike:

1. **archive** every harvested file into `modal_runs/<state>_s<seed>_<job8>/` with a
   `run_metadata.json` recording job id, GPU, parallel-cell count, job state, exit code, wall
   seconds and the file list. Results reach local disk *before* anything is destroyed.
2. **parse** the metrics out of whatever landed, so the caller sees numbers rather than
   filenames.
3. **sweep** the sandboxes.

The sweep guards itself. `close()` is host-scoped -- it terminates every sandbox for the target
and cancels running jobs -- so `sweep_sandboxes()` first scans the ledger for `state=running` or
`state=harvesting` and returns `{"skipped": True}` rather than killing live work. Both branches
are tested: a busy ledger never calls close, an idle one always does.

The in-container script also ships the tail of every cell log home unconditionally
(`out/logs/`). Without that, diagnosing a failed cell costs an entire extra job just to read a
file off the volume, which happened twice.

## 12 · Parallelism: one GPU vs many

Billing is per container-second, so **N containers cost what 1 container of the same total work
costs.** Wall-clock compresses for free. The only question is which packing finishes soonest.

### Within one GPU — `PARALLEL=1`

```bash
PARALLEL=1 HARVEST=1 HARVEST_OUT="$J/out" bash run_lane.sh <state> <seed> <engine> <v14> <out>
```

Forks cat, reg and joint onto the same card and waits on all three. Measured at 2.98x end-to-end
on Alabama, better than any individual cell, because the short cells hide inside the long one.

Use it when the cells fit together in VRAM (Alabama peaked at 14.1 GB of 40) and one cell clearly
dominates the runtime -- the short cells then cost almost nothing, since they finish inside the
long one. Do **not** expect it to help on a card already saturated by a single cell:
on the A40, concurrent cells measured roughly half speed each, so the packing gained nothing. The
heartbeat's `cells_running` and `util` columns tell you which regime you are in.

### Um handle é SEQUENCIAL — lanes concorrentes exigem handles distintos

Medido em 2026-08-10: o segundo `submit_job` no mesmo handle é recusado enquanto o primeiro roda.

```
Busy: host.compute.submit: Cannot reuse sandbox while job '<id>' is still running.
Each byoc submit wipes /work — byoc is sequential-only per handle.
```

Para rodar duas lanes ao mesmo tempo, crie **dois handles com `provider_params` diferentes** —
qualquer diferença basta (`memory: 65536` vs `65537`). Um `sandbox_label` **não** existe e é
rejeitado com `InvalidResource: Unrecognized key(s)`.

```python
c1 = host.compute.create("byoc:modal", provider_params={..., "memory": 65536})
c2 = host.compute.create("byoc:modal", provider_params={..., "memory": 65537})
j1 = c1.submit_job(command=lane(7),   ...)     # GPU dedicada
j2 = c2.submit_job(command=lane(100), ...)     # GPU dedicada
```

**PERIGO com `c.close()` em lanes concorrentes.** `close()` NÃO é por handle: é **host-scoped** —
encerra todos os sandboxes do target nesta conversa e **cancela os jobs ainda em execução**,
mesmo os criados por outro handle. Medido em 2026-08-10: um único `close()` devolveu
`terminated=['sb-E0a7am...', 'sb-ka7wCF...', 'sb-6cCJNc...']`, três sandboxes de três handles
diferentes. Chamá-lo enquanto a outra lane roda **mata a outra lane**.

Com duas lanes no ar, portanto:

- **nunca** chame `c.close()` até a última lane cair;
- para matar apenas um sandbox ocioso, use o id: `modal.Sandbox.from_id("sb-...").terminate()`;
- `finish()` já protege isso — o `sweep_sandboxes()` varre o ledger por `state=running` /
  `state=harvesting` e devolve `{"skipped": True}` em vez de fechar. Chame `finish()` para cada
  lane quando ela cair: a primeira chamada arquiva e faz o push mas pula o teardown, e a última
  arquiva e encerra tudo.

### GPU a 0% não é necessariamente travamento

`torch.compile` frio gasta a fase de aquecimento em codegen do inductor e autotuning do Triton,
que são **CPU-bound**. Nesse intervalo a GPU fica genuinamente ociosa e o log da lane só tem
`START`, sem nada entre ele e o `DONE`. A combinação lê exatamente como um job travado e não é.

Observado no joint de alabama s100: o primeiro batch levou 120 s e os batches 2-9 custaram
aproximadamente 0 s cada.

O que distingue "compilando" de "travado" é a linha de progresso do próprio treinador, não a
utilização da GPU. `watch_modal.py` já a espelha, e o sinal de alerta correto é
**primeiros batches lentos + util 0% ao mesmo tempo**.

### Ler o progresso de fora: `read_file` é bloqueado, `iterdir` passa

`Volume.read_file()` chamado do kernel local falha com
`ProxyError 403 Forbidden (port not allowed for host localhost)`, então o leitor "puro Python"
não funciona daqui. `Volume.iterdir()` passa, mas só devolve nomes e tamanhos.

Reverificado em 2026-08-10 contra a lane `florida_s7` **em execução**: `read_file` falhou nos
dois arquivos testados, `iterdir` passou e mostrou o heartbeat crescendo (2413 B). Consequência
prática: `scripts/watch_modal.py` usa `read_file` e **não funciona a partir do kernel Claude
Science** — continua sendo a ferramenta certa a partir de um terminal Claude Code, que não passa
pelo proxy.

Para ler o conteúdo do heartbeat ao vivo, use um job CPU de segundos:

```python
c.submit_job(command='tail -8 /data/live/<estado>_s<seed>/heartbeat.jsonl', run_timeout_s=300)
```

Isso custa centavos e é a única rota verificada. Um `iterdir` mostrando o arquivo crescer já
serve como sinal de vida sem gastar nada.

### Across GPUs — one job per unit of work

Each `submit_job` gets its own container and its own GPU. Wall-clock is then the **longest single
job**, not the total:

```python
c = host.compute.create("byoc:modal", provider_params={"gpu": "A100-40GB", ...})
jobs = [c.submit_job(command=lane_cmd(st, sd), intent=f"{st} s{sd}", run_timeout_s=...)
        for sd in (7, 100)]          # 2 containers, 2 GPUs, same total cost
```

Choosing the split, for six Florida cells (2 seeds x 3 families):

| packing | containers | wall | note |
|---|---:|---|---|
| 1 job, all serial | 1 | total / speedup | slowest, same price |
| 1 job per seed, `PARALLEL=1` inside | 2 | longest seed | **usually best** |
| 1 job per cell | 6 | longest cell (joint) | fastest; most containers to babysit |

The middle row is normally right: it gets the intra-lane packing gain *and* seed-level
parallelism, while keeping one harvest and one heartbeat per seed. Go to one job per cell only
when a single joint cell is the whole critical path.

Two cautions. Each container re-pays cold start and `torch.compile` warm-up, so point
`INDUCTOR_ROOT` at the Volume to share the compile cache. And a failure costs one container's
work, which is an argument for smaller jobs when a cell is long.

## 13 · The 2026-08-10 audit: what changed in `run_lane.sh`, and what still needs care

An independent audit of `run_lane.sh` against the version of record found eight defects that a
flag diff cannot see. Six are fixed in the script; two are structural and need a decision.

### Fixed

| # | defect | why it mattered |
|---|---|---|
| 1 | `HW=$(harvest_watch ...)` **hung forever** under `HARVEST=1` | The backgrounded loop inherited the command-substitution pipe, which then never reached EOF. The joint cell would have burned its entire run clock at 0 % GPU. `HARVEST=0` short-circuited before the `&`, so the A40 never saw it — this was live only on the path it was written for. Reproduced, then fixed by assigning the pid to a global and closing the subshell's stdout. |
| 2 | rundir resolved by **newest mtime**, not by the launched pid | See §4. A race under §12's own recommended packing, made reachable by the heartbeat's `Volume.commit()`. Now `rundir_for <prefix> <pid>`, with a loud WARN if the anchor misses. |
| 3 | a **failed cell still wrote a sidecar** | The skip-guard then swallowed the relaunch — the exact failure §5 warns about, in the script that creates them. Now: check `rc`, save the log tail, write no sidecar. |
| 4 | reg seed glob `*reg_s${SEED}*` matched **`s100` when `SEED=1`** | `ls -t ... \| head -1` returned the seed-100 file whenever it was newer, so a seed-1 sidecar would attest seed-100 numbers. Reproduced. Now the exact filename the ablation writes is constructed, as the record does. |
| 5 | `PY` defaulted to `$REPO/.venv/bin/python`, which **does not exist on the Volume** | `/data/repo` has no `.venv`. Every rented cell depended on the submit wrapper passing `PY=`. Now resolved in-script with a PATH fallback and a loud failure. |
| 6 | the **lane log was harvested only from runs that failed** | `$HARVEST_OUT/logs` is created by `save_log()`, which only runs on failure, so the final `cp` silently no-op'd on a clean run. Now `mkdir -p` first, and the sidecars are copied home too. |

Also added, to close the gap with the record: the joint cell now **scores in-container**
(`a40_score_matched.py` + `score_joint_best.py`) instead of coming home unscored; sidecars now
carry the **values, commit, protocol block and recipe** rather than five fields, matching
`run_wave.sh::sidecar_write` so a rented cell is as mergeable and auditable as a local one; the
charter §6.6 v17 sanity guard runs on the joint result; `python -u` is restored on reg; and
`lane_host` + `train_pid` are recorded, because §10 has **not** established that rented and
local cells may be pooled and every cell must therefore say where it ran.

### Verificação independente das seis correções (2026-08-10, Claude Science)

Cada uma foi **executada**, não apenas lida. O que os testes mostraram:

| # | como foi exercitada | resultado |
|---|---|---|
| 1 | `harvest_watch` com intervalo de 2 s sob `HARVEST=1`, fold novo aparecendo durante a espera | retorna na hora, bancou 2 folds durante a execução, parou limpo no `harvest_watch_stop` |
| 2 | dois rundirs `*_111` (antigo) e `*_222` (novo); pedido o pid 111 | devolveu o **antigo**, que um `ls -t` nunca escolheria; sem pid e com pid inexistente emitiu o WARN e caiu no mais novo |
| 3 | cinco casos no gate: `rc≠0`, rundir vazio, rundir inexistente, treinou sem score, tudo certo | sidecar escrito **só** no último; nos quatro primeiros zero sidecars e o log salvo |
| 4 | três seeds (1, 7, 100) com o `s100` mais recente por mtime | o glob antigo devolve **seed 100 quando SEED=1**; a construção exata acerta os três |
| 5 | `REPO` sem `.venv` (o caso Modal), com `.venv` (o caso A40), e `PY` explícito | cai no PATH, prefere o venv, respeita o explícito — interpretador executou nos três |
| 6 | `save_log` com `out/logs` inexistente | criou o diretório e preservou o tail (linha 300 presente) |

**Precisão sobre a correção 4:** o glob `*reg_s${SEED}*` erra **apenas em SEED=1**, porque
`*s1*` casa com `reg_s100`. Em 7 e 100 ele acerta. O `run_wave.sh` de registro (linha 154) já
constrói o nome exato, portanto o driver em produção nunca esteve exposto — inclusive o
`texas seed 1` que rodava durante esta auditoria.

Três armadilhas encontradas ao escrever os próprios testes, registradas porque custaram turnos:
`harvest_watch` recebe quatro argumentos (prefixo, família, intervalo, pid) e passar dois faz a
família virar o intervalo; o subshell do watcher redireciona para `/dev/null`, então um
`command not found` de dependência não carregada fica invisível; e `kill -0 "${PID:-0}"` com pid
vazio sinaliza o **grupo de processos**, o que faz um watcher já morto parecer vivo.

### Still open — decide, do not drift

- **Sidecars do not reach the board.** `v18/score_all.py` hardcodes
  `SIDE = docs/results/closing_data/v18`; `run_lane.sh` defaults `OUT` to `.../v18_2`. Nothing
  merges the second directory, so a rented cell is invisible to the aggregator and simply reads
  as missing. Either pass `OUT=docs/results/closing_data/v18` when a cell is meant for the
  board, or teach `score_all.py` both roots. Do not leave it implicit.
- **`TORCHINDUCTOR_CACHE_DIR` on cat/reg is a genuine tension, left OFF.** §4 says point it
  somewhere persistent; the record sets it on the joint cell only, so on Modal every rented
  cat/reg cell re-pays the full `torch.compile` warm-up into an ephemeral `/tmp`. Turning that on
  would be a real saving — and it would also change how every rented cell is produced, including
  cells being produced right now against cells already banked with a cold cache. A compiled
  number is governed by the inductor session and is within-fold-σ rather than bit-reproducible
  (`CLAUDE.md`), so this is not a protocol change; it is still not a change to make silently on
  another lane's behalf. It is therefore **opt-in via `INDUCTOR_SHARE_CELLS=1`** and off by
  default: unset, cat/reg behave exactly as they always have. Decide it deliberately, and if you
  turn it on, say so in the sidecar note for the cells it produced.

Two smaller things worth knowing: `replication_gate.md` still cites `data/alabama_s0_cat.json`
for its 30.7654 comparand, and `data/` was deleted on 2026-08-10 — the gate has lost its
reference value. And `v18/run_regen.sh:62` counts sidecars at `$BASE/../../results/...`, which
resolves to `docs/studies/results/...` and does not exist, so the end-of-wave line always logs
`0/18 cells present`.

## Checklist

1. **know which harness you are** (§0.1) — `modal_lane.py` for Claude Code, `run_modal_cell.py`
   for Claude Science; and know **which account** holds the state you are about to run (§9)
2. inputs uploaded with **explicit tokens for the account you will run on**, verified by byte
   count with `modal volume ls --json` / `Volume.iterdir`
3. `scripts/preflight.py --cells cat,reg,joint` passes; stale sidecars dropped
4. scripts bundle re-staged (`--stage-scripts`) **if you edited anything under `scripts/`** —
   otherwise the container silently runs the previous upload
5. `run_lane.sh` used, never a hand-written training command; `--compile` on all three cells
6. `HARVEST=1` with `HARVEST_OUT` on a durable path — the Volume for `modal_lane.py`, `$J/out`
   for `submit_job`
7. run clock set with margin above the estimate, and small enough that a dead driver cannot
   leave a container billing for hours
8. cost computed at **GPU + CPU + memory** (§6), on the **tier actually served** — read the
   device from the job's own `nvidia-smi` line, not from what you requested
9. nothing already running that duplicates this work
10. teardown **verified**, not assumed: `Sandbox.list()` / `host.compute.ledger()` shows no live
    sandbox. The ledger under-reports; poll until each reports an exit code
11. results archived locally with metadata **before** teardown, and `run_metadata.json` says
    where the cell ran
12. before reporting progress, read `state` / `exit_code` / wall from the run — never infer
    elapsed time from a returned wait

## 13 · What the 2026-08-11 reg night changed (read before choosing a card or trusting a log)

Seven corrections, each one measured after an argument turned out to be wrong. They are here
because every one of them cost a relaunch, a wrong number, or a wasted container.

### 13.1 · The card ranking for **reg** is H100 > A100 ≈ A40 — and the H100 is also CHEAPER

Measured on one fold of california s100, same state, same data, same code, separate tag:

| | s/fold | $/h | $/cell (5 folds) |
|---|---:|---:|---:|
| A40 (i9-14900K, free) | 555.7 | — | $0 |
| A100-40GB | 677 | $4.00 | **$3.76** |
| **H100** | **268.8** | $5.85 | **$2.60** |

The H100 is **2.07x the A40** and returns the same numbers: `Acc@1 0.3344 / Acc@10 0.6283 /
MRR 0.4346` identical to 4 dp against the A40's own fold, differing only 1e-4 on Acc@5 and F1.
Because it finishes in less than half the wall, it costs **less per cell** than the A100 despite
the higher hourly rate. §6's break-even framing is still correct arithmetic; what was wrong was
feeding it an estimate.

### 13.2 · Small states understate GPU gain. Never carry their ratio to a large one.

This produced two wrong projections in one day:

| cell | ratio measured at **arizona** | ratio at the **large state** |
|---|---|---|
| dedicated-cat | 2.04x | **3.84x** (texas) |
| dedicated-reg | 1.26x | **2.07x** (california) |

At a small state the fixed costs — data load, `torch.compile` warm-up, per-fold setup — are a
large fraction of the wall and they do not shrink with a faster card, so the ratio is diluted.
Measure the ratio **at the size you intend to run**, or state plainly that the number is a lower
bound.

### 13.3 · The Volume holds its own copy of `src/`. `git push` does NOT update it.

The container imports from `/data/repo/src`, which is a copy you upload by hand. A fix committed
and pushed is **not** in the container until `modal volume put` runs. This cost two relaunches on
2026-08-11: the abort message in the traceback was the **old wording**, which is what finally gave
it away — the behaviour looked identical, only the text differed. Before any launch that depends
on a change you just made:

```bash
for f in src/tracking/metrics.py scripts/p1_region_head_ablation.py; do
  modal volume put poimtl-v18-data "$f" "/repo/$f" --force
done
# and VERIFY, do not assume:
modal volume get poimtl-v18-data /repo/src/tracking/metrics.py /tmp/v.py --force
md5 -q src/tracking/metrics.py; md5 -q /tmp/v.py    # must match
```

### 13.4 · A PID is not an identity on a shared Volume

`rundir_for()` matched the output directory by the trainer's pid. Every container starts its pid
space from scratch, so four concurrent cells all handed the trainer **pid 76**. texas s100 matched
**texas s7's** rundir — and because a Modal Volume gives a container the snapshot it had **at
start**, that directory appeared with 1 of its 5 folds. The cell banked `n_folds=1, 36.4189`,
which was *fold 1 of texas s7*, and overwrote s7's score file on the way out. Only the pre-declared
sanity anchor caught it.

Fixed by requiring `-newer "$LANE_MARK"` in addition to the pid, and by warning (never silently
accepting) when a pid matches a directory that predates the lane. The same marker already guarded
the heartbeat; the fix had simply never been carried across.

### 13.5 · Packing is per-family, and cat does not fit twice on one card

| family | GPU util (1 cell) | VRAM | 2 on one 80 GB card? |
|---|---:|---:|---|
| dedicated-cat | 90-95 % | **46.7 GB** | **No** — 93.4 GB > 81.6 GB, arithmetic, not contention |
| dedicated-reg | ~40-60 % | ~10 GB | Yes, and it raises throughput ~1.3x |

Two families of the same study with opposite bottlenecks. Measure the family you are about to
pack; do not carry the other one's utilisation over. Note the reg figures are **after** scoring
moved onto the GPU — the older "10-57 %, 1.8 GB" numbers were taken while it scored on the CPU and
must not be reused.

### 13.6 · `MTL_AMBIGUITY_STRICT` — accept a tie deliberately without disarming everything else

The rank-derived hit path certifies itself: it counts rows whose hit@k is genuinely undetermined
(`n_gt < k < n_gt + n_eq`) and aborts under `MTL_STRICT=1`. Both large states trip it at ~1-2 rows
in 766 083 (0.00013 pp, at the edge of the 4-dp quantum), which forced an all-or-nothing choice:
keep `MTL_STRICT` and lose the cell, or drop it and also disarm the canon-recipe, overlap-provenance
and fp16 guards.

`MTL_AMBIGUITY_STRICT=0` disables **only** the tie abort. The count is still measured every epoch
and still lands in the artifact (`ambiguous_rows` per fold), so an accepted cell records what it
accepted. `run_lane.sh` forwards it; `modal_lane.py` injects it into the container when set in the
driver's environment.

### 13.7 · Read progress with the progress tool, not with `grep`

`watch_modal.py` and the heartbeat exist because `modal container logs` returns empty for a sandbox
(§8). On 2026-08-11 two **healthy** containers were killed because progress was read from a WARNING
line that only fires when a tie is present — its absence was taken for "no progress". The real
per-fold times were 742-994 s; packed 2-wide the A100 was delivering **1.3x the A40's throughput**
at the moment it was terminated. Two further traps in the same family:

* the tqdm bar writes with `\r`, so `tail | grep` returns a **stale** "Epoch 1/50" long after the
  run has moved on — pipe through `tr '\r' '\n'` first;
* the heartbeat's own `folds_done` counts rundir artifacts that `p1` does not produce, so it reads
  `0` for a reg cell that has finished four folds. For p1, count `fold N:` lines in the cell log.

```bash
python pipelines/modal/watch_modal.py --state texas --seed 100 --follow
```

### 13.8 · Upload from the A40, not through your laptop

The A40 box already has the Modal client in `~/PoiMtlNet/.venv`. Uploading from there measured
**16.6 GB in ~18 s** — the "~50 MB/s from nespedgpu" figure in §1 is stale by more than an order of
magnitude, and routing the same bytes through a laptop is minutes-to-hours slower.

```bash
ssh nespedgpu "cd ~/PoiMtlNet && MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=... \
  .venv/bin/modal volume put poimtl-v18-data <path> /repo/<path> --force"
```

Always verify by **byte count** against the source afterwards; a size match is what caught that the
transfer really had completed when it finished suspiciously fast.
