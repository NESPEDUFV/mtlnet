# v18 — what is missing, for future audit

> **Status: the board is COMPLETE and the numbers are sound. Nothing below invalidates a result.**
> What is missing is **traceability** — the ability for a future reader to prove *which code, which
> machine, and which recipe* produced a given number. The charter (§7 "PROVENANCE.md — every rundir:
> state, seed, PID, path, recipe, commit SHA") asks for this explicitly and we are short of it on
> 30 of 72 cells.
>
> Written 2026-08-11 so the gaps can be assigned. Each item states **what to add, where, and how to
> get it** — no re-training is required for any of them.
>
> **Where this stands (updated 2026-08-11 after three working sessions).** Each gap now carries a
> **VERDICT** block under its heading giving the outcome and pointing at the addendum holding the
> evidence. In short: **B, E and F are closed; C went from 43 undeclared to 4; A and D cannot be
> closed because their sources do not exist**, and saying so is the honest end state rather than a
> pending task. The audit text below each verdict is the **original finding, left unedited** — the
> separation between what was found and what was later done is deliberate.
>
> | gap | outcome |
> |---|---|
> | **A** `commit_sha` | **closed as unrecoverable** — no `.git` on any of the three accounts; 30 cells keep a `commit_sha_note` |
> | **B** `recipe_version` | **closed** — 10 to 0, copied from sibling cells |
> | **C** `lane_host` | **largely closed** — 43 to 4 undeclared; 28 of 29 modal labels confirmed against heartbeats; 1 disputed |
> | **D** tie certificate | **exhausted at source** — superseded by `scoring_path` on all 24 `reg` cells |
> | **E** display bugs | **both closed**, each verified by execution |
> | **F** `TASKS.md` | **closed** |

## 0 · Board state (verified 2026-08-11 01:50)

| | |
|---|---|
| cells | **72 / 72** — 6 states × 4 seeds {0,1,7,100} × 3 families (cat, reg, joint) |
| n per cell | 20 (4 seeds × 5 folds) |
| missing results | **none** |
| seed spread, region | texas 0.023 · florida 0.035 · istanbul 0.036 · california 0.058 · arizona 0.166 · alabama 0.213 pp |

All spreads are far below the region effect at the large states (+1.93 texas / +1.96 california), so
the headline result is not in question.

---

## 1 · GAP A — 30 cells have no traceable `commit_sha` (HIGH)

> **VERDICT 2026-08-11 — CLOSED AS UNRECOVERABLE (admitted, with cause). Still 30 cells.**
> The source does not exist and cannot be made to exist: `/repo` was uploaded to Modal as a **tar
> of the worktree**, with no `.git`, and this was verified by direct listing on **all three
> accounts** (A6, A7). The two commits nearest the upload are *later* than it, so HEAD at upload
> time was never recorded — and a recovered SHA would not certify a worktree anyway. Two lane cells
> that *do* carry real SHAs prove the mechanism works; the 30 are a driver capture gap of the time.
> **No back-fill is possible or honest here.** Each affected sidecar carries a `commit_sha_note`
> stating the cause. Note for tooling (A4): the field is present with the literal string
> `"unknown"`, so `if not d.get("commit_sha")` reports zero missing and passes.
> Evidence: A4, A6, A7, A9.

`commit_sha` is absent or literally `"unknown"`. These cells cannot be tied to a state of the code.

| seed | family | states affected |
|---|---|---|
| 7 | cat | arizona, california, florida, istanbul, texas |
| 7 | joint | arizona, california, florida, istanbul, texas |
| 7 | reg | arizona, florida, istanbul |
| 100 | cat | alabama, arizona, california, florida, istanbul, texas |
| 100 | joint | alabama, arizona, california, florida, istanbul, texas |
| 100 | reg | alabama, arizona, florida, istanbul, texas |

**All 30 are seed 7 / seed 100 — i.e. the rented-lane cells.** The local seed 0/1 cells all carry a
SHA (`run_wave.sh` captures `git rev-parse HEAD` at wave start).

**What to add:** the SHA the lane image was built from, into each sidecar's `commit_sha`.
**Where to get it:** the Modal driver, now at `pipelines/modal/` (moved out of the retired
`v18_2/` folder on 2026-08-11) — whatever
commit was baked into the image, or the checkout the lane ran. If a single SHA covers all lane cells,
one value fills all 30. **If the SHA is genuinely unrecoverable, say so in PROVENANCE.md rather than
back-filling a guess** — an invented SHA is worse than an admitted gap.

**Update 2026-08-11 (florida s7/s100 joint, 2 of the 30):** unrecoverable, and the reason
generalises to the other rented cells. The `/repo` on the Modal Volume was uploaded at
2026-08-10T03:28Z as a **tar of the worktree**, not `git archive`, and carries no `.git`. The two
nearest commits (`a0df1fe3` 03:44Z, `d8a4cf04` 04:47Z) are both **later** than the upload, so HEAD
at upload time was an earlier commit that was never recorded. Even a recovered SHA would not certify
the code, because the payload was the worktree rather than a committed tree. Recorded as
`commit_sha_note` in each sidecar instead of a back-filled value.

## 2 · GAP B — 10 cells have no `recipe_version` (MEDIUM)

> **VERDICT 2026-08-11 — CLOSED. 10 → 0.**
> All 10 were seed-0/1 `reg` cells banked before the field existed. The 14 `reg` cells that *do*
> carry it hold a **single** value, `v18-approved-2026-08-09 (FINAL_SETTINGS.md)`, and region was
> never retuned (`max_lr 3e-3`, `freeze_alpha=True`, `alpha_init=0.0`, `logit_adjust_tau=0`), so the
> value was **copied from the sibling cells** rather than inferred from a run record. Each carries a
> `post_hoc_fields` entry naming that basis.
> Evidence: A9.

| seed | family | states |
|---|---|---|
| 0 | reg | all six |
| 1 | reg | alabama, arizona, florida, istanbul |

These are the **kept** region cells — banked before `recipe_version` was introduced on 2026-08-09.
Their recipe is known and unchanged (region was never retuned: `max_lr 3e-3`, `freeze_alpha=True`,
`alpha_init=0.0`, `logit_adjust_tau=0`).

**What to add:** `"recipe_version": "v18-approved-2026-08-09 (FINAL_SETTINGS.md)"` plus the `recipe`
string already used by the newer reg sidecars. Pure metadata back-fill, no re-run.

## 3 · GAP C — hardware is mixed and mostly undeclared (HIGH for the write-up)

> **VERDICT 2026-08-11 — LARGELY CLOSED. 43 → 4 undeclared, plus 1 disputed label.**
> Three findings, in order of how much they change the picture:
> **(a) The mixing is universal, not a texas-region quirk.** Every `(state, family)` pool has seeds
> 0/1 local and 7/100 rented. Re-running "the one odd cell" was never the option it looked like;
> disclosure is the only realistic close (A7).
> **(b) The labels are sound.** 18 heartbeats recovered from the three accounts let each cell's
> silicon be re-derived from `memory.total` and confronted with its declared `lane_host`:
> **28 of 29 confirm** (A8).
> **(c) 36 of the 43 were locals that simply never said so.** Declared `local:NVIDIA A40` on two
> independent grounds: no seed-0/1 cell anywhere declares a modal lane, and **no `_s0`/`_s1` lane
> exists under `/live` or `/harvest` on any of the three accounts** (A9).
> **Still open:** 4 cells (`alabama_s7` × 3, `istanbul_s7_cat`) have no heartbeat that can be tied
> to them and are left **undeclared rather than guessed**; and `texas_s100_reg` declares
> `A100-SXM4-40GB` while the lane that banked texas s100's folds ran on an H100 (A8).
> **Resolved along the way:** the `[VERIFY]` on the florida joint cells — they ran on an
> **A100-80GB** while `A100-40GB` was requested. The tier you ask for is not always the part you get.
> Evidence: A3, A6, A7, A8, A9.

| hardware | cells |
|---|---:|
| local A40 (declared or presumed) | 45 |
| `modal:NVIDIA H100 80GB HBM3` | 19 |
| `modal:NVIDIA A100-SXM4-40GB` | 8 |

**42 cells carry no `lane_host` field at all.** They are presumed local, but presumption is not
provenance.

Two things follow:

1. **Back-fill `lane_host` on the 42** (e.g. `"local:NVIDIA A40"`), so every cell declares its
   machine.
2. **The mixing is not uniform across a state's pool, and that must be disclosed.** The clearest
   case: **texas region has 3 seeds on the local A40 and 1 (seed 100) on a Modal A100** — and that
   Modal cell is the lowest of the four (64.9295 vs 64.9436 / 64.9514 / 64.9528).

   This matters more than it looks. `v18_2/EXECUTION_PLAN.md` measured cross-hardware deviation on
   one identical cell at **~0.086 pp** (A40 30.7654 / A100 30.6790 / H100 30.7049). That is
   **3.7× the entire seed spread of texas region (0.023 pp)**. So for this metric the *machine* is a
   larger source of variation than the *seed*.

   It does not threaten the +1.93/+1.96 region result. But describing these cells as "4 seeds"
   without stating that one ran on different silicon would be inaccurate. Either disclose it in
   `METHODOLOGY.md`, or close it: **re-running texas s100 reg locally costs ~57 min** and makes that
   pool single-machine.

**Update 2026-08-11 — the mixing is not confined to texas region.** Enumerating every
`(state, family)` pool by the silicon each seed ran on shows that **essentially every pool is
mixed**: seeds 0 and 1 are local, seeds 7 and 100 are rented, across all six states and all three
families. Texas region is not the exception, it is one instance of the rule. The disclosure in
`METHODOLOGY.md` therefore cannot be a footnote about one cell; it has to state the design
honestly — *seeds 0/1 local, seeds 7/100 rented* — and note that the measured cross-hardware
deviation (0.086 pp) exceeds the seed spread of several region pools.

Closing this by re-running is no longer a 57-minute job: it would mean re-running every seed
7/100 cell locally, which is the whole rented wave. The realistic close is disclosure, not
homogenisation.

**florida s7/s100 joint `lane_host` back-filled 2026-08-11**, with a caveat worth checking:
the requested tier was `A100-40GB`, but every heartbeat sample from both cells reports
`memory.total = 81920 MiB` (80 GiB). The device *name* had already rolled out of the captured
`.out` tail, so the sidecars record `modal:A100-class 80GB` with an explicit `[VERIFY]` rather than
a model name nobody measured. **Whoever audits this should confirm which tier Modal actually
served** — the other 8 cells are labelled `A100-SXM4-40GB`, and if those were also 80 GiB parts the
existing labels are wrong too.

## 4 · GAP D — the tie certificate exists on only 3 of 24 region cells (MEDIUM)

> **VERDICT 2026-08-11 — EXHAUSTED AT THE SOURCE, and superseded by a field that can be filled.**
> Only **4 of the 24** p1 result JSONs contain an ambiguous-row count, and all four are already in
> their sidecars. The other 20 ran on the legacy scorer, where the quantity was never computed:
> there is nothing to recover, now or later. What §4 actually wanted — telling the two scoring
> populations apart — is now satisfied directly: **every one of the 24 `reg` cells carries a
> `scoring_path`** saying which scorer produced it (4 tie-aware, 20 legacy).
> The underlying defect was also fixed at the source: `run_lane.sh` never copied `ambiguous_rows`
> while the A40 driver did, so the disclosure depended on which machine you happened to use (A2).
> Evidence: A2, A9.

`ambiguous_rows` (how many validation rows have an undecidable hit@k) is recorded on **3 of 24**
region cells — the ones produced after 2026-08-10. Measured values where it exists: 1–2 rows out of
585 092 (california) and 1 of 766 083 (texas), i.e. **≤ 0.0003 pp** of Acc@10 — negligible, and ~1 %
of the seed spread.

The remaining 21 cells were scored on the legacy topk path where the question does not arise, so
there is nothing to measure retroactively. **What to add:** a one-line `"scored_on"` /
`"scoring_path"` field on those 21 stating they used the legacy full-logit + topk CPU path, so a
reader can tell the two populations apart without archaeology.

## 5 · GAP E — two display bugs in the generated report (LOW, but user-visible)

> **VERDICT 2026-08-11 — BOTH ITEMS CLOSED.**
> **Item 1** (the `n` column that could not represent a row whose halves disagree) now prints
> `n_cat/n_reg` when they differ. **Tested by execution, not inspection**, which mattered:
> `make_results.py` re-runs `score_all.py` before rendering, so editing the results JSON proves
> nothing — the edit is overwritten before the table is built, and the first attempt reported a
> false failure for exactly that reason. With `score_all.py` stubbed and florida's region half
> forced to n=15 against a category half of 20, the row renders **`20/15`**; restored, it renders
> `20`.
> **Item 2** (`current_n` derived from joint cells only) is closed — see §5b.
> Evidence: §5b, A9.

1. **`V18_RESULTS.md` §1 `n` column is wrong for texas and california.** It prints `20`, taken from
   `joint_cat_paired["n"]` (`make_results.py:156`), but it labels a row whose **region half** may
   have a different n. Now that the board is 72/72 both halves are 20, so **this is currently
   correct by accident** — the bug is that the column cannot represent a row whose two halves
   disagree, which was the case for ~26 h. Fix: print n per half, or assert they match.
2. **`status.json` says `phase: "done"` while cells were still running** (`updated_at`
   2026-08-11T01:44). `status_update.py:107-109` derives `current_n` from **joint cells only** ×5,
   so it structurally cannot see a lagging cat or reg family. Fix: count all three families.

## 5b · GAP E item 2 — CLOSED 2026-08-11

`status_update.py` derived `current_n` from **joint cells only**, so a state whose joint cells were
all banked reported its full n while its dedicated cells were still missing. Observed live on
florida 2026-08-10: joint s7/s100 landed and the state read n=20 while `florida_s7_cat`,
`florida_s7_reg`, `florida_s100_cat` and `florida_s100_reg` did not yet exist.

Fixed: a seed now counts toward `current_n` only when **all three families** are banked for it, and
the status file gained a `seeds_complete` map so a reader sees *which* seeds are complete rather
than inferring it from a total. Verified by execution, not inspection: hiding `florida_s7_cat` drops
florida from 20 to 15 with `seeds_complete: [0, 1, 100]`, and restoring it returns 20.

Item 1 of GAP E (the `n` column that cannot represent a row whose halves disagree) is **still
open** — it remains correct only because both halves happen to be 20.

## 6 · GAP F — charter deliverable `TASKS.md` was never created (LOW)

> **VERDICT 2026-08-11 — CLOSED.** `TASKS.md` was written (commit `4bc3e1b0`). Every §7 charter
> deliverable now exists.

§7 lists `TASKS.md` ("the charter and task list"). Every other §7 deliverable exists: `README.md`,
`V18_RESULTS.md`, `PROVENANCE.md`, `AUDIT.md`, `METHODOLOGY.md`, `score_all.py`,
`data/v18_results.json`, `PROGRESS.md`, `status.json`, `log.md`.

## 7 · Open scientific decisions (NOT data gaps — author calls)

Recorded here so they are not mistaken for missing data:

1. **Practical-significance floor.** The generator awards "**beats**" to deltas as small as
   +0.04 pp because pairing on identical folds collapses the variance. Three independent arguments
   say those should not be reported as wins: fold dependence (folds within a seed share ~80 % of
   training data), the tuned-comparator bias (the dedicated arm got a per-state LR search the MTL
   arm did not), and effect size (~+0.04 pp is not a claim anyone can defend). ~~Not yet decided.~~ **CLOSED 2026-10-06 by the
   author (E2 of the deposit dossier): the text stays as it is.** The delivered Ch.5 already reads
   the category differences as small ("every difference is small in both directions … Florida is
   the only one the tests resolve"), so no generator "beats" reaches the text as a win.
2. **P1 capacity-matched region control** (`POSTPONED.md`) — the experiment that would decide whether
   the +1.93/+1.96 region advantage is multi-task sharing or simply the dual-tower's extra
   parameters. The 1-fold triage already showed it survives severing the trunk *and* deleting the
   category task, which points at capacity. Still held.

---

## Priority for whoever picks this up

Everything the data on hand could settle **is settled**. What is left is not a queue of back-fills:

| # | what remains | why it is not a task |
|---|---|---|
| 1 | **A** - 30 cells with `commit_sha: "unknown"` | the source does not exist on any account; a back-fill would be invented provenance |
| 2 | **D** - 20 `reg` cells with no tie certificate | never computed by the legacy scorer; `scoring_path` now marks the two populations instead |
| 3 | **C** - 4 cells with no `lane_host` | no heartbeat can be tied to them; left undeclared rather than guessed |
| 4 | **C** - `texas_s100_reg`'s disputed label | needs its rundir tied to one of two heartbeat windows; see A8 for why the obvious rule fails |
| 5 | section 7 - the two scientific decisions | author calls, not data gaps |

**Nothing here requires re-training.** Items 1-3 are closed as far as evidence allows; item 4 is
the only one where more archaeology could still change an answer.

## A1 · What this session closed

| gap | before | after | basis |
|---|---|---|---|
| **C** — `lane_host` | 43 missing | **42 missing** (this session's 3; the parallel session filled 2 more, and re-generation reset some keys to an explicit `None`) | declared `local:NVIDIA A40` on texas s7, california s7, california s100 — the three cells this session launched and watched on nespedgpu. **Not** inferred; the other 40 are left undeclared deliberately. |
| **D** — tie certificate | 21 of 24 reg cells missing | **20 of 24** | texas s100 back-filled from its own p1 result JSON (`[{2,2},{1,1},{1,2},{2,1},{1,0}]`), copied verbatim, not recomputed. |

Both back-filled fields carry a `post_hoc_fields` block in the sidecar naming who added them and on
what basis, so a reader can tell a driver-written field from a hand-written one.

## A2 · A defect behind gap D, now fixed at the source

The three reg cells that *had* the certificate all ran on the **A40**; the one that lacked it ran on
**Modal**. That was not a coincidence: `run_lane.sh`'s `sidecar_write` never copied
`ambiguous_rows`, while the A40 driver did. Identical recipe, identical code, and the disclosure
depended on which machine you happened to use.

`run_lane.sh` now reads the certificate from the p1 result JSON the cell just wrote and emits it in
the sidecar. **Future rented reg cells will not need this back-fill.**

## A3 · Cross-hardware: the accumulated evidence says the effect is at or below the reporting quantum

Gap C's concern rests on a cross-hardware deviation of **~0.086 pp**, and the section above
(written by the session that enumerated the pools) establishes something the original text missed:
**the mixing is universal**, not a texas-region quirk. Seeds 0/1 are local and 7/100 are rented
across all six states and all three families. That removes "re-run the one odd cell" as an option
and makes disclosure the only realistic close — which is the right conclusion.

What this session adds is a tighter measurement of *how much it actually matters*. Same fold, same
seed, same data, same code, A40 against H100 (california s100, fold 0):

| | Acc@1 | Acc@5 | Acc@10 | MRR | s/fold |
|---|---|---|---|---|---|
| local A40 | 0.3344 | 0.5455 | **0.6283** | 0.4346 | 555.7 |
| Modal H100 | 0.3344 | 0.5456 | **0.6283** | 0.4346 | 268.8 |

**Acc@10 — the banked metric — is identical to 4 dp.** Only Acc@5 and F1 move, by 1e-4.

This is consistent with the other cross-machine agreements the board already contains rather than
standing alone: texas cat has three seeds inside **0.008 pp** while spanning an A40 and an H100
(s0/s1 local 36.3225/36.3144, s7 rented 36.3190), and california reg's two rented-vs-local seeds
sit **0.0055 pp** apart. Several independent pairs, all agreeing at or below the quantum.

**How to read it.** The 0.086 pp figure came from an uncontrolled comparison (different family,
whole cells, three machines at once); the controlled pairs put the effect at ~0. Three honest
limits remain: the controlled pair is *one fold*; it compares A40↔H100 while several banked cells
ran on an **A100**, which no controlled pair covers; and none of this is a proof of bit-identity —
it is repeated agreement at the precision the board reports.

**Practical consequence:** disclose the design (seeds 0/1 local, 7/100 rented) because it is true
and cheap to state, but do not treat the mixture as a threat to the results. The evidence available
does not support re-running anything on those grounds.

## A4 · Gap A is worse than "missing" — the 30 cells carry a literal `"unknown"`

The field exists; its value is the string `unknown`. That matters for tooling: a naive
`if not d.get("commit_sha")` audit reports **0 missing** and passes. Any future check must test the
value, not the key.

Two lane cells now carry real SHAs (`85bcc588`, `25942582`), so the mechanism works — the 30 are a
capture gap in the driver at the time, not a limitation. This session did **not** back-fill them:
the runs predate it and assigning a SHA to someone else's execution would be exactly the invented
provenance the gap text warns against.

## A5 · Untouched

**B** (10 cells without `recipe_version`), **E** (both display bugs — `status.json` still derives
`current_n` from joint cells only, so it structurally cannot see a lagging cat or reg family), and
**F** (`TASKS.md`) are unchanged. The remaining 40 `lane_host` and 30 `commit_sha` back-fills are
left open for the same reason: they concern cells this session did not run.

## A6 · Volume forensics on all three Modal accounts — gap A closed as unrecoverable, and the `[VERIFY]` resolved

Read-only inspection of every volume on the three accounts that ran cells
(`vitor-h-oliveira`, `vholiviera`, `vitor-oliveira`), 2026-08-11.

**Gap A: `/repo/.git` is absent from every volume on all three accounts.** This independently
confirms the reason recorded above — the payload was a worktree tar, so there is no commit to
recover, on any account. **Recommend closing gap A as "admitted, with cause" rather than leaving it
open as a back-fill**: `commit_sha_note` already states why, and no further evidence exists to find.

> Method note, because it nearly produced a false result: the Modal SDK authenticates once per
> process, so setting the token env vars and re-importing inside one script returns **the first
> account three times**. The first pass here reported identical contents for all three and was
> wrong. Each account must be probed in its own process.

**The `[VERIFY]` on the florida joint cells is resolved, and it does not generalise.** The heartbeat
records `memory.total`, which separates the three parts cleanly: **40960 MiB = A100-40GB**,
**81559 MiB = H100 80GB HBM3**, **81920 MiB = A100-80GB**. Cross-checking every cell that declares a
`lane_host` against the memory its own heartbeat recorded:

| declared | cells | heartbeat says | verdict |
|---|---|---|---|
| `modal:NVIDIA A100-SXM4-40GB` | 6 (alabama s100, florida s7/s100 cat+reg) | 40960 MiB | **correct** |
| `modal:NVIDIA H100 80GB HBM3` | 8 (arizona, istanbul, texas s7) | 81559 MiB | **correct** |
| `modal:A100-class 80GB [VERIFY]` | 2 (florida s7/s100 joint) | 81920 MiB | **correct — and it is an A100-80GB** |

**Zero divergences across 16 labelled cells.** So the concern that "the 8 cells labelled
A100-SXM4-40GB may be mislabelled too" does **not** hold: they ran on genuine 40 GB parts. What is
true is narrower and still worth knowing — **the tier you request is not the part you get**: a
`A100-40GB` request returned an 80 GiB part for the two joint cells. The `[VERIFY]` label can now be
replaced with `modal:NVIDIA A100-SXM4-80GB (tier requested: A100-40GB)`, though the device *name*
itself was never captured for those two and the memory is the only direct evidence.

**A trap for anyone reading heartbeats later:** `$LIVE_DIR` is keyed `<state>_s<seed>` for cat and
reg but `<state>_s<seed>_joint` for the joint, so a cell's directory **accumulates across families**
and across re-runs. `florida_s7` (40960) and `florida_s7_joint` (81920) are different cells on
different hardware; reading either as "florida s7" conflates them. Two of this session's own
directories hold both 40960 and 81559 samples for the same reason — cat on an H100, reg on an A100,
same directory.


## A7 · Storage sweep of the PRIMARY account — the hardware labels are now independently verified, and one lane was found that no session had recorded

Requested by the author 2026-08-11: look in the **primary (vho2009)** storage for anything the
other sessions missed. Read-only, top-level folders only.

**What was there.** The primary volume `poimtl-v18-data` holds `/seed`, `/scripts`, `/inductor`,
`/repo`, `/live` and `lane_probe_primary.txt`. `/live` contains **three** lanes:
`istanbul_s7`, `florida_s7`, `florida_s100`. Lane 2 holds ten more, and its second volume
`poimtl-v18-data-2` is **empty**.

**A6's `/repo/.git` finding is confirmed on the primary account, by direct listing.** The primary's `/repo` holds `scripts`, `research`, `out`, `src`, `output`, `results`, `docs` — and `modal volume ls poimtl-v18-data /repo/.git` returns *No such file or directory*. (An earlier draft of this section asserted this for *both* volumes before the primary's `/repo` had actually been listed; the listing was then performed and is what is reported here.)

**11 heartbeats recovered**, archived at
`docs/results/closing_data/v18_2/heartbeats_from_modal_storage/`. This matters because the host
itself held only **4**, all florida: 23 of the 29 modal-labelled cells had no local evidence at all.

**A6's claim is confirmed, on 22 cells rather than 16.** Re-deriving each cell's silicon from
`memory.total` in its own heartbeat and confronting it with the declared `lane_host`:

| declared | cells confirmed | heartbeat |
|---|---:|---|
| `modal:NVIDIA H100 80GB HBM3` | 11 | 81559 MiB |
| `modal:NVIDIA A100-SXM4-40GB` | 6 | 40960 MiB |
| `modal:A100-class 80GB` (florida joint) | 2 | 81920 MiB |
| via sibling lane heartbeat | 3 | consistent |

**CONFERE = 22, DIVERGE = 0, still without evidence = 7.** So the labels are sound, and the
`[VERIFY]` this session raised on the florida joint cells is closed by measurement: they ran on an
**A100-80GB** while `A100-40GB` was requested.

**A finding no session had recorded: `istanbul_s7` ran twice, on two different accounts.**
Primary at 06:11 UTC on an A100-80GB (81920 MiB), reaching `folds_done=0`; lane 2 at 16:24 UTC on
an H100 (81559 MiB), reaching `folds_done=4`. The primary run produced no banked result. This is
worth knowing for two reasons: the board's istanbul s7 numbers come from the H100 lane, not the
A100 one; and `istanbul_s7_cat` is the one istanbul cell whose `lane_host` is still `None` while
its `reg` and `joint` siblings declare H100. Its 268 s wall cannot be tied to either heartbeat on
its own, so it was left **undeclared with a `lane_host_note`** rather than inferred — the same rule
A1 applied.

**Still without evidence (7 cells):** california s7/s100 (cat, joint), texas s100 (cat, joint, reg).
Their lanes are not in `/live` on either account.

**Method note, confirming A6's warning the hard way.** `modal.Volume.list` does not exist in client
1.5.3 — the volume inventory has to come from the `modal volume list` CLI with the tokens in the
environment, one invocation per account. A full recursive `iterdir` walk of a volume is also
impractically slow (10 min without finishing one volume); listing the folders that matter is the
workable approach.


## A8 · The two remaining accounts — all 29 modal cells now have heartbeat evidence, 28 labels confirmed, one unresolved

The author supplied credentials for the two profiles named in A6 but never probed here
(`vholiviera`, `vitor-oliveira`). **The seven cells A7 listed as "no evidence" were on them**:
`vholiviera` holds `/live/{california_s7, california_s100, texas_s100}`, `vitor-oliveira` holds
`/live/{california_s7, california_s100, texas_s7, texas_s100}`. Seven more heartbeats pulled;
**18 in total**, archived under `docs/results/closing_data/v18_2/heartbeats_from_modal_storage/`.

**28 of 29 modal-labelled cells confirm**, one does not resolve:

| declared | cells | verdict |
|---|---:|---|
| `H100 80GB HBM3` | 13 | confirmed by `memory.total = 81559` on the lane that banked folds |
| `A100-SXM4-40GB` | 6 | confirmed by `40960` |
| `A100-class 80GB` (florida joint) | 2 | confirmed by `81920` — an A100-80GB where 40 GB was requested |
| others via sibling lane | 7 | consistent |
| **`texas_s100_reg`** | 1 | **unresolved** — see below |

**`texas_s100_reg` declares `A100-SXM4-40GB`; the lane that banked texas s100's folds ran on an
H100.** Two runs of that lane exist: `vholiviera` 13:56 UTC on an H100 (`81559`, folds 0→4, rundir
`..._135751_72`), and `vitor-oliveira` 21:58 UTC whose single heartbeat file spans **two different
GPUs** — an H100 window to 22:20, then an A100-40GB window from 23:31 with `out_kb` still
climbing. The cell's 3384 s wall matches neither window cleanly. **Left as declared, flagged here**,
rather than rewritten on a rule that does not hold.

**Two properties of the heartbeat that invalidate the obvious attribution rule**, worth recording
because the next reader will reach for it:

1. **`folds_done = 0` does not mean a lane failed.** It counts train.py rundirs, and the `reg`
   family runs through `p1_region_head_ablation.py`. A lane running only `reg` sits at 0 for its
   whole life while producing a real result — visible as `out_kb` growing with `folds_done` pinned.
2. **One `heartbeat.jsonl` can hold more than one lane.** `LIVE_DIR` is keyed by *(state, seed)*,
   not by cell, so a relaunch on the same day appends to the same file. Reading such a file as one
   run merges two GPUs into one lane and produces a false "this lane used two cards".

A rule built on (1) alone — "the productive run is the one with folds > 0" — gives a unique answer
for all 13 lanes and would have silently rewritten `texas_s100_reg`'s label. It was not applied.


## A9 · What the accumulated data could close, closed 2026-08-11

Asked by the author: *which gaps are still open, and can we work on them with the data we have?*
Each gap was tested against what is actually on disk rather than assumed.

| gap | before | after | basis |
|---|---:|---:|---|
| **B** — `recipe_version` | 10 missing | **0** | the 10 are all seed-0/1 `reg` cells; the 14 `reg` cells that carry the field hold a **single** value, and region was never retuned. Copied from siblings. |
| **C** — `lane_host` | 40 missing | **4** | 36 are seed 0/1. Two independent checks: no seed-0/1 cell anywhere declares a modal lane, and **no `_s0`/`_s1` lane exists under `/live` or `/harvest` on any of the three accounts**. Declared `local:NVIDIA A40`. |
| **D2** — scoring path | 24 unmarked | **0** | every `reg` cell now states which scorer produced it, derived from whether its own p1 JSON carries an ambiguous-row count (4 new path, 20 legacy). This is what §4 asks for. |
| **E item 1** — the `n` column | wrong by construction | **fixed** | prints `n_cat/n_reg` when the halves disagree. |

Every back-filled field carries a `post_hoc_fields` entry naming the basis, so a reader can tell a
driver-written value from a hand-written one.

**The E-1 fix was tested by execution, not inspection.** `make_results.py` re-runs `score_all.py`
before rendering, so simply editing the results JSON proves nothing — the edit is overwritten
before the table is built. With `score_all.py` stubbed and florida's region half forced to n=15
against a category half of 20, the row renders **`20/15`**; unstubbed and restored, it renders `20`.
The first attempt at this test reported a false failure for exactly the overwrite reason.

### What cannot be closed, and why

- **Gap A (30 cells, `commit_sha`).** The source does not exist. `/repo` was uploaded as a worktree
  tar with no `.git`, verified on **all three accounts**. There is no commit to recover, and a
  recovered SHA would not certify a worktree anyway. **Recommend closing as "admitted, with
  cause".**
- **Gap D (20 cells, `ambiguous_rows`).** Exhausted at the source: only **4 of the 24** p1 result
  JSONs contain the field, and all four are already in their sidecars. The other 20 ran on the
  legacy scorer, where the quantity was never computed. Nothing to back-fill — which is why D2
  above records the *scoring path* instead, so the two populations are distinguishable.
- **4 cells still without `lane_host`:** `alabama_s7` × 3 and `istanbul_s7_cat`. No `alabama_s7`
  heartbeat exists on any account; `istanbul_s7` has two candidate lanes and its `cat` cell cannot
  be tied to either. Left undeclared rather than guessed.
- **`texas_s100_reg`** (A8) remains the one label whose declared hardware disagrees with the lane
  that banked its folds.

**Remaining after this session: gap A (30, unrecoverable), gap D (20, exhausted), 4 undeclared
`lane_host`, and 1 disputed label.** Everything that the data on hand could settle, is settled.

---

## Addendum 2 — independent verification of the seed 0/1 back-fills (2026-08-11)

> Written by the session that **produced** the seed 0 and seed 1 cells, cross-checking the post-hoc
> fields another session added, against run records that only this session has: the wave driver logs
> and the rundirs on disk. **All 36 cells verify. No correction was needed.**

### What was checked, and against what

| back-filled field | cells | verified against | result |
|---|---:|---|---|
| `lane_host = local:NVIDIA A40` | 36 | every wave ran on this host; all 36 rundirs resolve locally | ✅ correct |
| `recipe_version` (copied from siblings) | 10 | region was never retuned — `FINAL_SETTINGS.md` keeps τ=0 and `max_lr 3e-3` | ✅ correct |
| `scoring_path = legacy full-logit + topk CPU` | 12 reg | the `[p1 S2] scoring val metric on CPU` line in each cell's own log | ✅ correct |

### A stronger check the field values make possible

`commit_sha` on these 36 cells was **driver-written, not back-filled**, and its distribution is an
independent confirmation that the recipe decision is faithfully recorded:

| commit | family | cells |
|---|---|---:|
| `e351d4b0` (seed 0) · `5075d77d` (seed 1) | **cat + joint** | 24 |
| `496cdab4`, `c17ee729`, `da179081`, `5075d77d` | **reg** | 12 |

Every **cat and joint** cell carries a SHA from *after* the recipe was approved on 2026-08-09 —
they were regenerated. Every **reg** cell carries an *older* SHA, spread over four commits, because
region was deliberately **not** regenerated (its recipe did not change). The provenance therefore
reproduces the FINAL_SETTINGS decision without anyone having asserted it.

⚠ **Do not "fix" the four different SHAs on the reg cells.** They look like an inconsistency and are
the opposite: each records the commit its wave process actually started from, and those waves were
restarted several times across 2026-08-06…08-09 as work landed. Normalising them would destroy
real information.

### On GAP A, from this side

The 30 cells without `commit_sha` are **all** seed 7/100, i.e. none were produced here. This session
independently confirmed the other session's verdict that they cannot be recovered from the run
artifacts: `summary/full_summary.json` and the p1 result JSONs carry **no** git/commit/host key
(checked directly), so no manifest route exists — the finding is not merely that the Modal tar
lacked `.git`.
