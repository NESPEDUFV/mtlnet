# Texas region-mechanism run: TERMINATED 2026-08-06T01:22Z

## THERE IS NOTHING TO RESUME. The `rg2` arm must be relaunched from scratch.

| arm | state |
|---|---|
| `baseline` | finished and scored 23:42, `region_1fold/texas/baseline_score.json` |
| `rg1` | finished and scored 00:47, `region_1fold/texas/rg1_score.json` (`reg_best_epochs: [48]`) |
| `rg2` | **KILLED about 10 minutes into a ~79-minute fold. Not recoverable; must be rerun.** |

The whole driver chain (3469518 / 3469527 / 3469528 / 3469532, from job
`f99e457b-3a59-4537-8032-4db255fb400a`) exited with it. To finish the triage, relaunch `rg2` through
`region_1fold/run_1f.sh`; the two completed arms are on disk and need not be recomputed. Metrics at
the moment it was killed, for reference only: `best=N64.47|C9.48, tr=N10.41|C10.52, val=N8.80|C9.47`
at `Epoch 8/50, 2685/18750`.

### Why it was killed rather than left paused

**On this host, `kill -STOP` does not yield the GPU.** It yields utilization only: a suspended CUDA
process keeps its whole memory reservation. Texas held **24,060 MiB while computing nothing**, and
the A40 (46 GB total) was down to **447 MiB free** while the Florida graph-attention build needed
20,968 MiB. The suspended job was therefore capping the study it had been paused to make room for.
After the kill, 24,512 MiB was free and Florida ran as the only GPU tenant.

The general lesson: if another job needs the *memory*, the choice is to let the run finish or to kill
it. Suspending buys nothing and still burns the wrapper's wall-clock timeout.

One orphaned torch inductor compile worker survived the kill. It holds no GPU memory and is harmless;
clean it with `pkill -f compile_worker` when nothing else is training.

---

## History: the earlier pause of `rg1` (PID 3510788), and the mistake in it

`rg1` was paused at 00:25 and resumed at 00:39. **That pause was a misjudgement**, recorded here so
it is not repeated. The reasoning below explains how the progress bar must be read.

## What it is

| | |
|---|---|
| process | `scripts/train.py --task mtl --state texas --seed 0 --only-fold 0 --model mtlnet_crossattn_dualtower --model-param disable_cross_attn=True` |
| arm | `rg1` (cross-attention disabled) of the region-mechanism triage |
| driver | `/home/vitor.oliveira/region_1fold/run_1f.sh`, from job `f99e457b-3a59-4537-8032-4db255fb400a` |
| owner | `vitor.oliveira` (your own job, not the other user on this host) |
| parents, all alive | 3469532 (driver) <- 3469528 (cmd.sh) <- 3469527 (`timeout 86700`) <- 3469518 (job.sh) |
| child | 3511018, a torch inductor compile worker, left running deliberately |

## State at the moment of pause

The progress bar reads `Epoch 39/50: 78%|  14550/18750 [41:22<10:44, 6.51batch/s]`. Read it
carefully, because the obvious misreading inverts the decision:

- **18750 is the whole fold-0 run**, 50 epochs x 375 batches, and 14550/375 = epoch 39. So the
  bar spans the entire fold, not one epoch.
- **41:22 is therefore total elapsed for fold 0**, not time spent inside epoch 39. This is
  corroborated by `ps`: `etimes=2517s` = 41.9 min of total process lifetime, which leaves no room
  for 38 prior epochs if 41 minutes had been spent in epoch 39 alone.
- **10:44 is the ETA to the END OF FOLD 0.** The run was about eleven minutes from finishing.
- Running metrics at pause: `best=N66.64|C76.87, tr=N16.57|C77.33, val=N11.33|C76.87`.
- CPU time consumed: 5542s.
- Completed and scored already: the `baseline` arm (`baseline_score.json` is on disk).
  In flight: `rg1`. Not yet started: `rg2`.

## Was pausing the right call?

**Probably not, on the numbers.** The run had roughly 11 minutes left on fold 0; waiting for it to
finish would have cost about as much as one Check2HGI build and would have banked the `rg1` arm's
score instead of leaving it suspended mid-fold. The pause was taken on the belief that the run was
mid-epoch with an unknown remainder, which the bar does not support.

It is not harmful, only suboptimal: the process is suspended rather than killed, so nothing is lost
and `kill -CONT` recovers the full state. **If the integrity suite is still running when this is
read, consider resuming Texas first** and letting it spend its remaining ~11 minutes of fold-0 work;
the two can also share the GPU, since the A40 has headroom for both.

## The risk to watch

The wrapper is `timeout 86700` (24.08 h) and **that clock is wall-clock: it keeps running while the
process is stopped.** At pause it had consumed 19245s, leaving about **18.7 h**. Since `rg1` needs
only minutes more for fold 0, and `rg2` follows it, the budget is not tight; but a long suspension
still burns it for nothing, which is a second reason to resume sooner rather than later.

## Why SIGSTOP rather than killing

The run writes no intermediate checkpoint (`--no-checkpoints`), so killing it would discard the full
41 minutes of fold-0 GPU work and force a restart of that arm.

## What pausing does and does not free

It frees the **GPU compute**: utilization dropped from 99% immediately. It does **not** free the
**24 GB of CUDA memory**, which stays reserved by the suspended process. The A40 has 46 GB, so
about 20 GB remains for the integrity builds, which is sufficient (an Alabama build uses ~1.2 GB
and a Florida build noticeably more, but well inside that headroom). Do not launch anything on this
host that needs more than ~20 GB until Texas is resumed and finished.
