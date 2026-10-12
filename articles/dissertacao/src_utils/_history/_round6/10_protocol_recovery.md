# 10 · Protocol recovery: the Ch.3/Ch.4 records, the Ch.5 screen scope, the Nash guarantee

**Written 2026-07-28.** Three items: COD-007 (the eight missing protocol cells), COD-005's one open
gap (the balancer screen's scope), and COD-005 sub-claim 4 (the Nash-MTL "ensures" wording). Plus
a fourth item the task asked for as part of the Standley evaluation, kept separate below because
its verdict is a negative.

**No file under `src/` was edited.** Every sentence below is a draft handed over for another pass
to apply. Build state is therefore unchanged from `7343c8ad`: 104/99 pp, `tex_errors=0`.

## 0 · The headline, and the one thing the previous audit got wrong

`CODEX_AUDIT.md:362-363` records COD-007's recoverability as **NEEDS-AUTHOR** on the ground that
"the CBIC codebase was not provided to this audit". **The CBIC-era codebase is in this repository.**
It is the tree at commit `9b06053f`, whose message is `VERSION PUBLISHED`
(2025-07-24 00:48:58 -0300), and the run artifacts that produced three of the four published result
columns are committed inside it under `results_save/florida_dgi_new/bests/`. Seven of the eight
COD-007 cells are therefore recoverable, and six of them are now established from code plus
artifacts rather than from recollection.

The reason the tie is strong and not merely "same pipeline family": I compared every cell of the
published CBIC tables against the committed run summaries, all three metrics and all seven
categories, and three of the four columns reproduce **exactly**, 21 of 21 cells each. Details in §1.5.

## 1 · ITEM 1 — the eight COD-007 cells

### 1.1 The verdict table

| Record | Ch.3 (CBIC) | Ch.4 (CoUrb) |
|---|---|---|
| **Split axis** | **ESTABLISHED** — stratified on the label, over samples, not user-disjoint (§1.2) | ESTABLISHED already, and already in prose at `4_courb.tex:257` |
| **Seed count** | **ESTABLISHED** — one fixed fold seed at all three published runs (§1.3) | ESTABLISHED already, and already in prose at `4_courb.tex:257` |
| **Tuning budget** | **NOT RECOVERABLE as a budget** — no harness ever existed, and the losing configurations were not committed (§1.4) | **NOT RECOVERABLE as a budget**, same reason; the author's "we did not change much" is consistent with the code but is not a record (§1.4) |
| **Checkpoint rule** | **ESTABLISHED** (§1.6) | **ESTABLISHED, and byte-identical to Ch.3's** (§1.6) |

The author's three recollections, tested rather than taken on trust:

- *"Ch.3 and Ch.4 use the same split methodology"* — **CONFIRMED.** Both are plain
  `StratifiedKFold(n_splits=5, shuffle=True, random_state=...)` with no `groups=` argument, in both
  codebases and on every path (§1.2).
- *"For both, only one seed was used"* — **CONFIRMED for the fold partition.** One qualification
  matters and is stated in §1.3: in the CBIC single-task paths nothing seeds the weight
  initialization at all, so "one seed" there is a fact about the folds, not about initialization.
- *"The checkpoint rule must be recovered from the commits, and it was the same for CBIC and CoUrb"*
  — **CONFIRMED, and recovered.** The rule is per-task best-validation-macro-F1 checkpointing with
  no early stopping, and the two codebases' implementations differ only in import paths (§1.6).

### 1.2 Split axis

**Ch.3, ESTABLISHED.** At `9b06053f`, the joint model's fold builder is `src/data/create_fold.py`:

| Coordinate | Content |
|---|---|
| `:159` | `random_state: int = 42,` (the default of `create_folds`) |
| `:176` | `torch.manual_seed(random_state)` |
| `:177` | `np.random.seed(random_state)` |
| `:194` | `x_next = df_next.drop(target_cols, axis=1).drop('userid', axis=1)` — the user identifier is dropped from the features |
| `:205` | `places_ids = df_category['placeid'].unique().astype(int)` |
| `:209` | `df_category = df_category.set_index('placeid')` — one row per place |
| `:217` | `next_skf  = StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=random_state)` |
| `:220` | `place_skf = StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=random_state)` |
| `:231-233` | `for ... in zip(next_skf.split(x_next, y_next), place_skf.split(x_category, y_category))` — **no `groups=` argument on either call** |

The two single-task paths are the same shape: `src/model/next/head/data/fold.py:34` and
`src/model/category/head/data/fold.py:32`, both
`StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)`, both split without `groups=`.
I grepped all five files for `groups=` and `GroupKFold`: zero occurrences.

The precise reading, which is stronger than "stratified by sample" and worth putting in the prose:
the two tasks have **different sample units**. For the next-category task each sample is a
nine-visit window, and since the user identifier is dropped and no grouping is applied, one user's
windows can fall on both sides of a fold. For the category task each sample is a place
(`placeid` is the index and is unique), so places do not span folds by construction, but that is a
property of the unit rather than a leakage guard on users.

**Ch.4, already established and already disclosed.** `4_courb.tex:257` states it, and the chapter's
own comment at `:258-275` carries the file-and-line trail. I re-verified all five cited coordinates
against the live worktree at `/Users/vitor/Desktop/mestrado/temp/tarik-new`
(`PoiMtlNet_Novo/src/etl/mtl/create_fold.py` :162, :180, :181, :226, :229) and all five hold
verbatim. The comment's second set of coordinates also holds. Its parenthetical at `:271` says the
committed file reads ":159, :177, :178, :223, :226"; measured at
`git show 58fd219b:PoiMtlNet_Novo/src/etl/mtl/create_fold.py`, that file carries
`random_state: int = 42` at :159, `torch.manual_seed` at :177, `np.random.seed` at :178, `next_skf`
at :223 and `place_skf` at :226, in that order. Ten coordinates checked, ten correct. Recorded
because the round's premise is that a quarter of the repository's cited coordinates have gone
stale, and these have not.

**One caution on the worktree.** `git status` in `tarik-new` reports
`PoiMtlNet_Novo/src/etl/mtl/create_fold.py`, `src/configs/model.py` and `pipelines/mtlnet_trainer.py`
as **modified relative to `58fd219b`**. The modifications do not touch the seed or the splitters
(they are an embedding-dimension inference change, `EMBEDDING_DIM 64*3` → `128`, and a `sys.path`
shim), so the Ch.4 claim is unaffected. But the working tree is not the commit, and any future
citation of that path should say which.

### 1.3 Seed count

**Ch.3, ESTABLISHED as one, with a qualification.** The three published runs are dated by their own
artifact directories: `next_lr1.0e-04_bs1024_ep100_20250518_2044`,
`category_lr1.0e-04_bs512_ep100_20250520_1114`, `mtlnet_lr1.0e-04_bs1024_ep50_20250523_1415`. At
every commit spanning those dates (checked at `5bcc9c8b` 05-18 20:16, `de0a23ca` 05-18 22:38,
`8a557aa3` 05-23 13:22, `ea18c2cb` 05-23 14:02, `6976242a` 05-23 14:07):

- `pipelines/next_head_trainer.py:46` reads `seed=42,`
- `pipelines/category_head_trainer.py:46` reads `seed=42,`
- `pipelines/mtlnet_trainer.py:32-37` calls `create_folds(...)` **without** `random_state`, so it
  takes the `create_fold.py:159` default of 42
- `src/model/next/head/configs/next_config.py:24` and
  `src/model/category/head/configs/category_config.py:22` both carry `SEED = 42`

The randomization arrived **after** all three runs: commit `f29d51aa`, 2025-07-24 00:45:41, replaces
`seed=42` with `seed=random.randint(1, 10000)` in both head trainers. That is three minutes before
`9b06053f VERSION PUBLISHED`. So the tree tagged as published contains a randomized seed that no
published run used, and reading the seed off the tagged tree alone would give the wrong answer.
The seed fact must be dated to the run, which is what the coordinates above do.

**The qualification.** `create_fold.py:176-177` seeds torch and numpy **once**, inside
`create_folds`, before the five-fold loop builds any model. So the joint model's five folds draw
from one initialization stream rather than from a per-fold reseed. The single-task paths are weaker
still: no `torch.manual_seed` or `np.random.seed` call exists anywhere on those paths (grepped
across both trainers, both fold builders, both cross-validation drivers and the trainer), and the
one seeded object, a `torch.Generator` at `src/model/next/head/data/fold.py:64`, feeds a
`WeightedRandomSampler` that is **commented out** at `:78`. For the two single-task columns,
therefore, "a single seed" is a statement about the fold partition and not about weight
initialization. The drafted sentence in §1.7 is scoped accordingly.

**Ch.4, already in prose.** `4_courb.tex:257` says the released code of record pins a single random
seed and that the five folds are one repetition. Verified independently this session at
`create_fold.py:162` in the worktree and `:159` in the commit.

### 1.4 Tuning budget

**NOT RECOVERABLE as a budget, for both chapters.** What I established:

- **No tuning harness has ever existed in either codebase.** `git ls-tree -r 9b06053f` returns no
  file whose name contains sweep, tune, grid, search, optuna or hparam. `requirements_colab.txt` at
  that commit lists no tuning library. In `tarik-new`, a grep across every `.py`, `.sh`, `.yaml` and
  `.json` outside `results/` for `optuna|ray.tune|grid_search|GridSearch|hyperopt|sweep` returns
  nothing; `requirements.txt` lists `wandb==0.19.11` and no search library. So whatever "several
  configurations" means, it means manual re-runs.
- **The repository does show manual variation in the CBIC window.** `configs/model.py`'s
  `MTLModelConfig.BATCH_SIZE` was changed twice, 2\*\*9 at `64c9baef` (2025-05-06), 2\*\*10 at
  `829858b0` (2025-05-07) and 2\*\*11 at `8a557aa3` (2025-05-23), while `MTLModelConfig.EPOCHS` read
  50 and both head configs read `EPOCHS = 100` at every commit spanning the three run dates. So batch
  size was varied by hand and epoch count was not. Whether any of those edits was an evaluated
  configuration or merely a fit to the machine at hand, the commits do not say.
- **The losing configurations were not kept.** `.gitignore` at `9b06053f` is `/results/*`, `/data/*`,
  `/temp/` — so run outputs were ignored by default, and only the hand-copied
  `results_save/florida_dgi_new/**bests**/` survives. The directory name is the record: these are
  the retained best runs, and there is nothing to count the discarded ones against.

**Therefore the number of configurations tried is not recoverable, and no sentence should assert
one.** What *is* defensible is the negative form: that the study reports one configuration per
model and that no systematic search was run. I draft that in §1.7 as an optional clause and
recommend the author decide whether to include it, because it is a statement about what the study
did not do and Ch.3 currently makes no claim either way.

**A live [VERIFY] this raised.** The committed run
`mtlnet_lr1.0e-04_bs1024_ep50_20250523_1415/model/model_params.json` records
`"batch_size": 1024`, but the committed `configs/model.py` at every commit from 13:22 that day
onward reads `BATCH_SIZE = 2**11` (2048). The run at 14:15 therefore executed against a working copy
whose config was 2\*\*10, uncommitted. **Consequence for anyone reading these files later: the
config file at a commit is not a witness for what a run used; the run's own
`model_params.json` is.** Everything in §1.2, §1.3 and §1.6 is sourced from code whose behavior is
invariant across that window, so no conclusion here depends on the config value.

### 1.5 Which runs produced the published tables

I compared the published CBIC tables cell-for-cell against the committed run summaries. Convention:
per-category precision, recall and F1 as `mean ± SD` over the five folds, macro row excluded, LaTeX
emphasis markup stripped, string equality (no rounding tolerance). 21 cells per column.

| Published column | Committed run | Result |
|---|---|---|
| Category table, **Single** | `category_lr1.0e-04_bs512_ep100_20250520_1114` | **21/21 exact** |
| Category table, **MTL** | `mtlnet_lr1.0e-04_bs1024_ep50_20250523_1415` | **21/21 exact** |
| Next table, **Single** | `next_lr1.0e-04_bs1024_ep100_20250518_2044` | **21/21 exact** |
| Next table, **MTL** | none in this repository | **0/21** |

The fourth row is a finding, not a failure of the search. The published joint-model next-category
column is close to the committed run but not equal to it (F1 Travel 64.61 ± 1.11 published against
64.67 ± 0.66 committed; Community 34.79 ± 1.05 against 35.12 ± 1.49; Food 28.06 ± 3.55 against
24.14 ± 3.77). I then tested that column's seven F1 means against **every**
`summary_next_metrics_formatted.csv` ever committed to this repository, across `9b06053f` and
`419761fa` and all six states: the best match is 1 of 7 means. So the artifacts of the run that
produced that one published column were never committed.

This does not weaken the protocol cells. The split code, the seed values and the checkpoint code
are identical across the entire 2025-05-04 to 2025-07-24 window, so a run inside that window is
covered by the same records whether or not its artifacts survive. It does mean **no sentence should
claim that the published joint-model next-category numbers are reproducible from this repository**,
and I flag it below.

### 1.6 Checkpoint rule — the recovery the author asked for

**The rule, in one paragraph.** Within each fold, training runs for the full configured number of
epochs. After every epoch the model is evaluated on that fold's validation split. The state
dictionary is deep-copied whenever the validation **macro-F1** is greater than or equal to the best
value seen so far in that fold, and this is done **per task**: the next-category task and the
category task each keep their own best state and their own best epoch, from the same shared model.
The per-fold classification report that becomes the reported number is then computed by reloading
each task's own best state. There is no patience counter and no early stopping in the main
experiments; the only two `break` statements are a target-F1 cutoff and a wall-clock timeout, both
`None` in the committed configuration. Epoch selection reads the same fold the score is reported on,
so there is no third split.

**Ch.3 evidence, at `9b06053f`:**

| Coordinate | Content |
|---|---|
| `src/model/mtlnet/engine/mtl_train.py:81` | `for epoch_idx in progress:` — the loop over `num_epochs`, which `pipelines/mtlnet_trainer.py:58-65` passes as `MTLModelConfig.EPOCHS` |
| `.../mtl_train.py:206` | `state = model.state_dict()` |
| `.../mtl_train.py:214-221` | `fold_history.to('next').add_val(..., model_state=state, best_metric='val_f1', ...)` |
| `.../mtl_train.py:222-229` | `fold_history.to('category').add_val(..., model_state=state, best_metric='val_f1', ...)` |
| `.../mtl_train.py:240-249` | the target-F1 cutoff `break`, guarded by `next_target_cutoff is not None` |
| `.../mtl_train.py:251-254` | the timeout `break`, guarded by `timeout is not None` |
| `configs/model.py:6, 9, 10` | `TIMEOUT_TEST = None`, `NEXT_TARGET = None`, `CATEGORY_TARGET = None` — and at `:7-8` the two target values sit commented out, `# NEXT_TARGET = 32.2` and `# CATEGORY_TARGET = 47.0`, which is how the convergence experiment was run |
| `utils/ml_history/metrics.py:88-90` | `def add_val(..., best_metric: str = 'val_f1', ...)` |
| `.../metrics.py:107` | `comparison = lambda x, y: x >= y` |
| `.../metrics.py:108-110` | `if best_metric == 'val_f1': metric_value = val_f1; prev_best = max(self.task_metrics.val_f1, default=0)` |
| `.../metrics.py:119-122` | `if comparison(metric_value, prev_best): self.best_model = deepcopy(model_state); self.best_epoch = len(...) - 1` |
| `src/model/mtlnet/engine/mtl_train.py:387-393` | `validation_best_model(..., to('next').best_model, to('category').best_model, model)` |
| `src/model/mtlnet/engine/validation.py:18, 29` | `model.load_state_dict(best_next)` then `model.load_state_dict(best_category)` — two passes, one per task |

Single-task paths, same commit: `src/model/next/head/engine/trainer.py:45` loops
`range(CfgNextTraining.EPOCHS)`; `:100-106` calls `add_val(..., model_state=model.state_dict(), ...)`
taking the `'val_f1'` default; `:118-121` is the same cutoff-or-timeout `break`;
`src/model/next/head/engine/cross_validation.py:165` calls
`evaluate(model, val_loader, DEVICE, best_state=...best_model)`; and
`src/model/next/head/engine/evaluation.py:11-15` loads that state before predicting. The category
path is the same at `trainer.py:100-106` and `cross_validation.py:100`.

**Artifact confirmation.** The committed `fold*_info.json` files record a per-task `best_epochs`
object, which is exactly what the code above would write. For
`mtlnet_lr1.0e-04_bs1024_ep50_20250523_1415`, of 50 epochs: fold 1 next epoch 40 / category epoch 4;
fold 2 next 35 / category 4; fold 3 next 38 / category 7; fold 4 next 31 / category 5; fold 5 next
36 / category 4. Two different epochs per fold, one per task, no fold stopping early.

**Ch.4 evidence: the same rule, and the same code.** I diffed the two files directly.

- `mtl_train.py`: CBIC-era `9b06053f:src/model/mtlnet/engine/mtl_train.py` against CoUrb-era
  `tarik-new/PoiMtlNet_Novo/src/train/mtlnet/mtl_train.py`. The diff is import paths, an added
  `FocalLoss` class, a `feature_size` parameter, a commented-out `clear_mps_cache`, a class-weight
  removal on `next_criterion`, and an FLOPs block. **The checkpoint block itself is
  character-identical**, `state = model.state_dict()` through both `add_val(..., best_metric='val_f1',
  ...)` calls, at CoUrb-era `:226-249`.
- `ml_history/metrics.py`: the diff is **five import lines and nothing else**. The comparison, the
  `deepcopy`, the `best_epoch` assignment are the same bytes.
- `validation.py`: the diff is one import, one import path, and two added confusion-matrix prints.
  Both `load_state_dict` calls are unchanged.
- Artifact confirmation on the CoUrb side:
  `results/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260226_1131/folds/fold1_info.json` records
  `category` epoch 26 and `next` epoch 19, of `"num_epochs": 50` in the sibling
  `model/model_params.json`.

So the author's recollection is right and the record is now recoverable for both chapters from one
statement.

### 1.7 The sentences each chapter can defend

Both chapters are **published prose**, so each of these is a marked addition and belongs in the
Appendix B trail for its article. Ch.4 already has an eight-addition paragraph
(`apx_b_errata.tex:200-214`) that these extend; Ch.3 has no additions paragraph yet, and one would
need to be written.

#### Ch.3, at `3_cbic.tex:303`, after "using a 5-fold cross-validation methodology."

> The folds are formed by a stratified splitter over the samples rather than over the users, so the
> check-ins of one user may appear in both training and validation; Chapter~\ref{ch:mobiwac} adopts
> a stricter user-disjoint protocol. For the category task the sample unit is the place, so no place
> spans two folds. The codebase of record pins a single fold seed, so the five folds constitute one
> repetition of the experiment rather than several, and every mean and standard deviation reported
> below is the spread across those five folds at that one seed;
> Chapter~\ref{ch:mobiwac} repeats its five-fold experiment at four random initializations.
> Within a fold, training runs for the full number of epochs configured, without early stopping, and
> each task is read at the epoch of its own highest validation macro-F1, measured on the same fold
> the score is reported on.

Notes on the wording, so the applying pass does not have to re-derive them.

- "the codebase of record" mirrors Ch.4's "The released code of record pins a single random seed",
  which the audit already accepted as correctly scoped (`CODEX_AUDIT.md:445-455`). Do **not**
  upgrade it to a claim that these files produced the published runs. For three of the four
  published columns that claim would in fact hold (§1.5), but the fourth column does not reproduce
  and one sentence covers all four.
- The literal value 42 stays out of the prose, following the Ch.4 precedent recorded at
  `4_courb.tex:274-275`: it is a fact about the code, not a reported parameter of the paper.
- "without early stopping" is scoped to the main experiments by placement. It must not be extended
  to the convergence subsection at `3_cbic.tex:339-347`, which deliberately stops each model at a
  target F1 because stopping is the quantity that experiment measures. If the applying pass prefers
  belt and braces, append to the last sentence: *", except in the convergence comparison of
  Section~\ref{sec:cbic:convergence}, where reaching a target score is what is measured"*. I did not
  put it in the main draft because the subsection already states its own mechanism.
- The epoch count itself is deliberately not quoted. The committed configuration and the committed
  run record disagree on batch size for the joint model's published run (§1.4), which is enough
  reason not to put a config-sourced integer into published prose.

**Optional clause on the tuning budget, author's call.** If he wants the gap named rather than left
silent, this is the strongest form the evidence supports, and it asserts nothing about a count:

> No systematic hyperparameter search was performed; the reported configuration of each model is a
> single configuration arrived at during development.

I recommend including it only if he is comfortable stating it, because it is a new claim about the
study's conduct rather than a recovered record, and §1.4 cannot corroborate the "several
configurations" half of his recollection from any artifact.

#### Ch.4, at `4_courb.tex:257`, appended to the existing protocol sentence

The split axis and the seed are already there. Only the checkpoint rule is missing:

> Within a fold, training runs for the full number of epochs configured, without early stopping, and
> each task is read at the epoch of its own highest validation macro-F1, measured on the same fold
> the score is reported on.

This is the same sentence as Ch.3's last one, deliberately: the code is the same code, and
WRITING_LAW's one-name-per-concept rule argues for one phrasing across both chapters. Ch.2's
protocol paragraph can then stop disclosing the gap.

#### The consequential edit in Chapter 2, outside my remit

`2_fundamentals.tex:466-470` currently reads that the protocol "strengthened from one study to the
next: Chapter~\ref{ch:cbic} reports five-fold cross-validation **without identifying the split
axis**, Chapter~\ref{ch:courb} states that its split is stratified by sample rather than by user
... and only Chapter~\ref{ch:mobiwac} splits by user." Once Ch.3 carries the sentence above, the
clause "without identifying the split axis" is false. The minimal repair, which also shortens the
sentence:

> Chapters~\ref{ch:cbic} and~\ref{ch:courb} both stratify by sample rather than by user, so the
> check-ins of one user may appear in both training and validation, and only
> Chapter~\ref{ch:mobiwac} splits by user.

I am not editing that file. Flagging it because applying the Ch.3 addition without this repair
would leave the frame contradicting the chapter it describes.

## 2 · ITEM 2 — the balancer screen's scope for Ch.5

### 2.1 The source, quoted exactly

`docs/results/mtl_improvement/T4_audit_and_verdict.md:8-10`, opened this session:

> ⚠ **Evidence-strength precision (2026-06-12 re-audit; supersedes earlier "per-method-tuned +
> arch-wired" phrasing).** What actually ran: the full screen at **registry DEFAULTS, seed 0,
> AL+FL**; only **GradNorm** genuinely retuned (lr=0.05, α=1.5); [...]

The same file states it a second time at `:111-112`, under "Caveats / scope":

> Single-seed (seed0) screen + corrected re-run, FL+AL (the cosine≈0 + literature + monotone cw-trade
> make multi-seed unnecessary — there is no candidate to promote).

**Confirmed: one seed, and the two datasets are Alabama and Florida.** The "AL+FL" expansion is not
inferred from the abbreviation: `docs/results/mtl_improvement/T4_full_screen.json` has exactly two
top-level keys, `alabama` and `florida`, and each holds exactly **19** arms
(`aligned_mtl, bayesagg_mtl, cagrad, db_mtl, dwa, equal_weight, excess_mtl, fairgrad, famo,
go4align, gradnorm, nash_mtl, pcgrad, scale_norm, scheduled_static, static_weight, stch,
uncertainty_weighting, uw_so`), which is the source of the chapter's "nineteen".

### 2.2 A correction to ANCHORS.md §3

ANCHORS's row for this item reads: `5_mobiwac.tex:186` "names the default configurations and the two
datasets (`including the two named above`, that is Alabama and Florida)". **Measured: that reading
is wrong.** Neither state is named before `:186`. In `5_mobiwac.tex`, the first occurrence of
"Alabama" is `:188` and of "Florida" is `:210`, both after the sentence. What *is* named immediately
above, at `:183`, is the pair of **balancers**, PCGrad and Nash-MTL. So "the two named above"
resolves to the two methods, and the sentence identifies neither state.

The residue is therefore larger than ANCHORS records: **the screen's prose states neither the seed
nor which two datasets it ran on.** The clause below closes both. The number nineteen, the two
exception values 0.68 and 0.19, and the verdict are untouched.

### 2.3 The clause

At `5_mobiwac.tex:185-188`, replacing only the scope phrase:

> We confirm this at scale: of nineteen loss and gradient balancers screened at their default
> configurations at a single seed on two datasets, Alabama and Florida, including the two named
> above, none improved on a tuned fixed task weighting across both tasks and both datasets.

Diff, for the applying pass: the words `on two datasets, including the two` become
`at a single seed on two datasets, Alabama and Florida, including the two`. Nine words added, no
number changed, no verb changed.

The literal string "seed 0" stays out of the prose and goes in the source comment, following the
Ch.4 precedent for the literal 42 and the MobiWac glossary's own instruction (`GLOSSARY.md:113`)
to write "a single seed" and never the banned compound "single-seed states".

Suggested comment to place with it, since `:205` currently carries the gap as an unaddressed note
("Also unstated: the screen is seed 0 at two states (AL+FL) -- see T4:8-17"):

```latex
% [round6] Scope added, per T4_audit_and_verdict.md:8-10 ("the full screen at registry DEFAULTS,
% seed 0, AL+FL") and :111-112 ("Single-seed (seed0) screen ... FL+AL"). The two states are named
% because neither appeared before this sentence: measured 2026-07-28, the first "Alabama" in this
% file is the next line and the first "Florida" is 24 lines below. The literal "seed 0" is kept out
% of the prose (fact about the run configuration, not a reported parameter); GLOSSARY.md:113 gives
% "a single seed" as the phrasing. The count nineteen is the 19 arms per state in
% T4_full_screen.json. Supersedes the "Also unstated" note previously at this site.
```

### 2.4 Why `:211` is a different measurement, stated plainly

`5_mobiwac.tex:209-211` reports "four seeds each on four Gowalla states: Alabama, Arizona and
Florida ... and Georgia". That is the **gradient-cosine measurement**, whose source is
`docs/results/mtl_improvement/R0_matched_metric_bar.json` per the chapter's own comment at
`:215-222`, and whose pool is four states at four seeds each. The **balancer screen** is a different
measurement with a different source (`T4_full_screen.json`), a different pool (two states) and a
different repetition count (one seed). They sit two sentences apart and their scopes differ in both
dimensions, which is precisely why the screen's scope has to be stated rather than inherited from
its neighbor. Nothing in the drafted clause touches `:211`.

### 2.5 The parity obligation

Ch.5 is **under review**, so the round-6 errata regime (`AGENT_BRIEF.md` §4) requires the same edit
in the submitted source, `articles/[mobiwac]/src/sections/02_related.tex:87-89`, which carries the
sentence verbatim, and then a line in `articles/[mobiwac]/ERRATA.md` under "Corrections applied in
the source during review" rather than an Appendix B row. That file's existing entry for this
sentence is at `ERRATA.md:64-72`. **Note that the two texts have already diverged at the very next
sentence**: the dissertation at `:209-211` names the four states, while the paper at
`src/sections/02_related.tex:96` still reads "three of our six datasets", which is the wording
`dccf45d2` corrected on the dissertation side. That divergence is outside this task, but whoever
applies the parity edit will be looking straight at it.

## 3 · ITEM 3 — the Nash-MTL "ensures" wording at `4_courb.tex:120`

### 3.1 What the method actually guarantees, from its own paper

Source of record: **arXiv:2202.01017v2**, *Multi-Task Learning as a Bargaining Game*, Navon,
Shamsian, Achituve, Maron, Kawaguchi, Chechik, Fetaya. Fetched from the arXiv API and the PDF
downloaded and read this session (19 pages). The arXiv comment field reads "ICML 2022"; OpenAlex
returns only the arXiv preprint record for this title (`W4225981399`, type `preprint`, no page
range), so the `pages = {16428--16446}` currently in `src/references.bib:741` is **not confirmed by
a source of record I could reach**; see the flag in §5. The venue itself, ICML 2022, is confirmed by
the paper's own arXiv comment.

The guarantee is real, and it is conditional. Three statements, quoted:

1. **The abstract, p.1:** "Under certain assumptions, the bargaining problem has a unique solution,
   known as the Nash Bargaining Solution".
2. **The utility definition and the constraint, p.3:** the utility of task *i* is
   `u_i(Δθ) = g_i^T Δθ`, and the Nash bargaining solution is
   `arg max Σ_i log(u_i − d_i) s.t. ∀i : u_i > d_i` (Eq. 1), with the disagreement point at
   `Δθ = 0`. Every task's utility is therefore strictly positive at the solution.
3. **The consequence, stated by the authors, p.6:** "Since our update rule is a descent direction
   for all tasks, we can reasonably assume that our algorithm avoids local maxima points."

And three conditions on it:

- **p.3:** "Our main assumption, besides the ones used by Nash, is that if θ is not Pareto
  stationary then the gradients are linearly independent". Formalized as **Assumption 5.1**, p.6.
- **Claim 3.1, p.3**, characterizing the solution as `Σ_i α_i g_i` with `G^T G α = 1/α`, is stated
  for the case "if θ is not on the Pareto front".
- **p.4:** the α is not solved exactly. It is approximated by a concave-convex procedure, and "we
  limit the sequence of CCP to 20 in all experiments".

So "ensures" overstates in one specific way: the descent-direction property is a property **of the
bargaining solution, at points that are not Pareto stationary, under the linear-independence
assumption** — not an unconditional property of every step the optimizer takes. Equally, the
correction must not go soft: this is a derived property the authors state, not an aspiration, so
"aims to", "is intended to" or "seeks to make" would be **weaker than the paper**, which is the
other failure mode the task names.

### 3.2 The narrowed sentence

At `4_courb.tex:120`, replacing "which ensures that the update is beneficial for all tasks
simultaneously":

> Multi-task training uses the Nash-MTL regularizer \cite{nash}, which formulates gradient balancing
> as a cooperative Nash bargaining game among $K$ tasks. Given the gradients of each task, Nash-MTL
> seeks the update direction that maximizes the product of the utilities of all tasks; at points
> that are not Pareto stationary, and under the method's assumption that the task gradients there
> are linearly independent, that direction is a descent direction for every task, avoiding the
> dominance of one task over the other.

Why this form:

- It keeps the strength. "is a descent direction for every task" is the authors' own phrasing (p.6),
  and it is stronger and more precise than "beneficial", which the published sentence used loosely.
- It names both conditions in the paper's own terms, and only those two. It does not import the
  twenty-iteration approximation, which is an implementation fact rather than part of the stated
  guarantee; that belongs in the Appendix B row, where the neighboring Nash cost correction already
  discusses it (`tables/cbic/errata.tex:54-60`).
- "avoiding the dominance of one task over the other" is retained from the published sentence and is
  independently supported: p.3 on Axiom 2.4, "the solution does not take into account the gradients'
  norms but rather treats all of them the same, as if they were normalized. Without enforcing this
  assumption, the solution can easily be dominated by a single direction".
- No em-dash, no contraction, American English. The semicolon replaces the published comma splice
  and is a single clause join, not a braid.

**If the author prefers the published sentence intact with the correction externalized**, the
chapter already has the device, at `3_cbic.tex:241-244`: reproduce the sentence, cut the offending
words, and footnote the correction with a pointer to the errata table. That variant:

> ... maximizes the product of the utilities of all tasks, which makes the update a descent
> direction for all tasks simultaneously,\footnote{The published sentence read ``which ensures that
> the update is beneficial for all tasks simultaneously''. The guarantee is narrowed here rather
> than reproduced unconditionally: the method's own paper derives it at points that are not Pareto
> stationary and under the assumption that the task gradients there are linearly independent, and it
> approximates the bargaining solution rather than solving it exactly. See
> Table~\ref{tab:apx:courb-errata}.} avoiding the dominance of one task over the other.

I recommend the in-line form in preference to the footnote, because Ch.4 is a translated chapter
whose prose is already dense with parentheticals, and because one clause is cheaper for the reader
than a footnote.

### 3.3 The Appendix B row

For `src/tables/courb/errata.tex`, in the existing two-column format:

```latex
\addlinespace
The methodology states that maximizing the product of the task utilities ``ensures that the
update is beneficial for all tasks simultaneously''. The guarantee is unconditional as written. &
Narrowed to the guarantee the method's own paper derives: at points that are not Pareto
stationary, and under its assumption that the task gradients there are linearly independent, the
update direction is a descent direction for every task. The paper states the property in those
terms and approximates the bargaining solution by an iterative procedure rather than solving it
exactly. The claim is weaker than the published one, and no result depends on it. \\
```

**One adjacent change this requires**, which I am not making: the CoUrb section's introductory
sentence at `apx_b_errata.tex:158-160` says the corrections in that table "replace the published
numbers by the values of an internal audit". A wording narrowing is not a number, so that sentence
needs one clause widened, for example *"replace the published numbers by the values of an internal
audit of the same results, performed after publication, and narrow one claim to the guarantee its
source states"*. The alternative is to give the CoUrb section a second table, as the CBIC section
has, which is more structure than one row justifies.

## 4 · The fourth item — the Standley citation and its history

The task's step 3 asked whether `3_cbic.tex:214` survives a narrowing and **whether a different
reference was used earlier**. Both answers, and the drafted prose.

### 4.1 Was a different reference ever used? NOT-SUPPORTED

- I extracted the "Empirical Performance" bullet from **every** version of both the article source
  and the chapter source that exists in this repository: 29 blobs across the 16 commits that touch
  either path, from the original upload `223f5df7` (2025-10-21) to `HEAD`. Deduplicating the 29
  extracted strings leaves **exactly one**, and it cites `\cite{standley2020tasks}`. No commit ever
  changed the key or the wording at that site.
- `git log --all -S "standley"` across 1,787 commits returns only commits that add the key elsewhere
  or discuss the defect in review documents; none rewrites the citing sentence.
- The scope of that negative has a hard limit worth stating: **the CBIC LaTeX entered this
  repository only on 2025-10-21, after the paper was published.** `git log --diff-filter=A --until=2025-10-20 -- "*.tex"`
  returns nothing. So pre-submission drafts of the bullet are not in this repository at all, and the
  question "did we cite something else while writing it" cannot be answered from here in either
  direction. What *can* be said is that no substitution happened after the paper entered version
  control.
- The key was also not silently repurposed: `standley2020tasks` is cited at four sites in the
  chapter (`3_cbic.tex:114` data heterogeneity, `:118` task clustering, `:191` FiLM and negative
  transfer, `:214` this bullet), and only `:214` overreaches. The CBIC-era bib entry
  (`223f5df7:CBIC___MTL/references.bib:43-49`) named CVPR 2020 with pages 3713--3724; the
  dissertation bib at `src/references.bib:973-979` already carries the corrected venue, ICML 2020,
  with the unverifiable page range dropped, and its provenance comment records why.

### 4.2 Does the sentence survive a narrowing? PARTLY, and the surviving half is well supported

Source of record: **arXiv:1905.07553v4** (2020-09-03), *Which Tasks Should Be Learned Together in
Multi-task Learning?*, Standley, Zamir, Chen, Guibas, Malik, Savarese. Comment field: "Presented to
ICML 2020". PDF downloaded and read this session (13 pages).

The published bullet makes three claims. Taking them one at a time against the paper:

The paper's own framing has to be read first, because it is what makes the bullet's error precise
rather than approximate. Its introduction, p.1, lists the potential benefits of joint training:
"In addition to reduced inference time, solving a set of tasks jointly rather than independently
can, **in theory**, have other benefits such as improved prediction accuracy, increased data
efficiency, and reduced training time" (emphasis added). Accuracy and training time are therefore
both named in the paper, hedged as theoretical possibilities, in the sentence that sets up the
question the paper then answers empirically. The bullet reproduces two of those possibilities as
established fact, opening "In practice".

| Claim in the bullet | Verdict at source |
|---|---|
| hard parameter sharing "frequently matches or exceeds the performance of more complex architectures on many benchmarks" | **Contradicted empirically, and its theoretical form is the paper's premise rather than its finding.** Named as a possible benefit "in theory" at p.1, then: abstract, p.1, multi-task learning "often leads to inferior overall performance as task objectives can compete"; Prior Work, p.2, on the paper's own hard-sharing exemplar UberNet, it "experiences a rapid degradation in performance as more tasks are added to the network"; also p.2, "Similarly to us, they find that multi-task learning is often inferior to single task learning with multiple networks." |
| "while offering faster ... inference" | **Supported.** Abstract, p.1: "This can save computation at inference time as only a single network needs to be evaluated." |
| "faster training" | **Named as a theoretical possibility, never as a measured result, and the paper's own training-cost material runs the other way.** "reduced training time" appears at p.1 inside the "in theory" list above. Every other training-time passage concerns the cost of the paper's own task-grouping search: §5.3, p.6, "Approximations for Reducing Training Time" reduces the burden of training the candidate networks; p.7 compares 45 percent against 95 percent savings between two such approximations; and the conclusion, p.9, concedes of its framework that "it can be costly at training time". Nothing in the paper measures hard sharing as cheaper to train than a more complex architecture. |

The paper's actual headline is neither pole: "Our framework offers a time-accuracy trade-off and can
produce better accuracy using less inference time than not only a single large multi-task neural
network but also many single-task networks" (abstract, p.1). The contribution is the **grouping**.

So the sentence survives a narrowing to its inference-cost half, and only that half.

**A correction to an earlier version of this section, recorded rather than silently fixed.** The
first draft of the table above asserted that the paper "makes no claim about training speed" and
that a full-text search returned zero hits. That was wrong, and the way it was wrong is instructive
enough to leave on the record: I searched for the string `faster train`, got no hits, and promoted
one surface form's absence into a claim about the paper's content. The paper does name reduced
training time, at p.1, hedged as theoretical. Two consequences. First, the corrected reading is
**stronger** against the bullet, not weaker: the bullet takes two items from a list the paper
explicitly marks "in theory" and reproduces them under the opening "In practice", which is a
sharper mischaracterization than a bare absence would have been. Second, the method that failed is
the one to avoid in this repository: an absence claim needs the concept searched under several
phrasings, not one string. Every quotation attributed to either paper in this report was then
re-checked against the extracted text of the session's own PDF copies by exact substring match,
after normalizing the extractor's hyphenation artifacts and curly quotation marks: **Standley 10 of
10 verbatim, Nash-MTL 8 of 8 verbatim.** I also ran the inverse test on the Nash paper, since the
same error class would show up there as an over-narrowing: it contains no instance of
"unconditional" or "guarantees that", and neither of its two uses of "always" bears on the
descent-direction property, so nothing in it contradicts the narrowing drafted in §3.2.

### 4.3 The drafted correction

Mirroring the device this same chapter already uses for the Nash cost claim at `3_cbic.tex:241-244`,
so the two corrections in one chapter read consistently:

```latex
    \item \textbf{Empirical Performance:} In practice, sharing one network across tasks reduces
    inference cost, since a single network is evaluated rather than one network per
    task \cite{standley2020tasks}.\footnote{The published sentence read ``hard parameter sharing
    frequently matches or exceeds the performance of more complex architectures on many benchmarks,
    while offering faster training and inference''. The accuracy and training-speed halves are
    corrected here rather than reproduced. The cited work names improved accuracy and reduced
    training time as benefits joint training may have ``in theory'', and then argues the other way
    empirically, reporting that multi-task learning ``often leads to inferior overall performance as
    task objectives can compete''; its contribution is a framework for assigning tasks to several
    networks so that competing tasks are separated, and it describes that framework as costly at
    training time. See Table~\ref{tab:apx:cbic-errata}.}
```

And the matching errata row for `src/tables/cbic/errata.tex`:

```latex
\addlinespace
The rationale for hard parameter sharing states that it ``frequently matches or exceeds the
performance of more complex architectures on many benchmarks, while offering faster training and
inference'', citing a work on task grouping. &
Narrowed to the inference-cost claim the cited work supports, with the accuracy and
training-speed claims removed and the cited work's own position stated in a footnote: it names
both as benefits joint training may have in theory, then reports empirically that joint training
often performs worse than separate networks, and its contribution is a framework for splitting
tasks across networks. The correction removes a stated advantage of the architecture this chapter
adopts, so it runs against the chapter's own interest. \\
```

Note the direction: this narrowing **weakens the chapter's own rationale**, which is the same
property Appendix B already records approvingly for the Nash cost correction
(`tables/cbic/errata.tex:59-60`, "runs against the chapter's own interest"). The author approved
this route in his own words at `CODEX_AUDIT.md:437-441`.

The alternative, preservation with the defect named, is available and cheaper: leave the published
bullet intact and add one sentence to the Appendix B preservation paragraph at
`apx_b_errata.tex:110-118`, which already preserves two elements. I do not recommend it here,
because the two currently preserved elements are preserved for reasons that do not apply: one is
time-indexed by the chapter preface, the other is a table convention. This one is a plain
misattribution of a claim to a paper that argues the other way, and it is the kind of thing an
MTL-literate examiner checks.

## 5 · Source ledger

### References

| Reference | Identifier | Where I opened it | Claim it supports here |
|---|---|---|---|
| Navon et al., *Multi-Task Learning as a Bargaining Game* | arXiv:2202.01017v2; arXiv API record fetched 2026-07-28; PDF read, 19 pp.; OpenAlex `W4225981399` queried with the stored key | arXiv API + PDF text extraction, this session | The guarantee is conditional: abstract p.1 "Under certain assumptions"; utility and constraint p.3 Eq. 1; Assumption 5.1 p.6; "our update rule is a descent direction for all tasks" p.6; Claim 3.1 scoped to points off the Pareto front p.3; CCP limited to 20 p.4; Axiom 2.4 and the domination discussion p.3 |
| Standley et al., *Which Tasks Should Be Learned Together in Multi-task Learning?* | arXiv:1905.07553v4, comment "Presented to ICML 2020"; PDF read, 13 pp. | arXiv API + PDF text extraction, this session | Abstract p.1 for the inference saving and for "often leads to inferior overall performance as task objectives can compete" and for the framework's time-accuracy claim; p.2 for UberNet's degradation and for "multi-task learning is often inferior to single task learning with multiple networks"; p.1 introduction for the "in theory" list naming improved accuracy and reduced training time as possible benefits; §5.3 p.6, p.7 and the conclusion p.9 for the training-cost material, all of which concerns the paper's own grouping search, with p.9 conceding the framework "can be costly at training time" |

### Numbers

| Number | Source | Field | Convention |
|---|---|---|---|
| nineteen balancers | `docs/results/mtl_improvement/T4_full_screen.json` | 19 keys under each of `alabama` and `florida` | count of screened arms per dataset; counted this session, not recomputed from prose |
| seed 0; Alabama and Florida | `docs/results/mtl_improvement/T4_audit_and_verdict.md:8-10` and `:111-112` | the precision banner and the caveats section | the screen's own run scope, quoted verbatim in §2.1 |
| 42 (fold seed, Ch.3) | `9b06053f:src/data/create_fold.py:159`; `6976242a:pipelines/next_head_trainer.py:46`; `...:category_head_trainer.py:46`; `next_config.py:24`; `category_config.py:22` | default argument and literal call arguments | the value in force at the three published run dates; kept out of prose by the Ch.4 precedent |
| 42 (fold seed, Ch.4) | worktree `create_fold.py:162`; commit `58fd219b:...:159` | default argument | as above; worktree and commit both checked |
| per-fold best epochs, Ch.3 joint model | `9b06053f:results_save/florida_dgi_new/bests/mtlnet_lr1.0e-04_bs1024_ep50_20250523_1415/folds/fold{1..5}_info.json` | `best_epochs.{next,category}.epoch` | validation macro-F1 argmax within the fold, per task, of 50 configured epochs |
| per-fold best epochs, Ch.4 joint model | `tarik-new/.../results/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260226_1131/folds/fold1_info.json` and sibling `model/model_params.json` | `best_epochs`, `hyperparameters.num_epochs` | same convention, 50 configured epochs |
| 21/21 cell matches on three published columns | published `articles/CBIC___MTL/tables/{category,next}_result.tex` against the three committed `summary_*_metrics_formatted.csv` files listed in §1.5 | per-category precision, recall, F1 as `mean ± SD` | five folds, macro row excluded, emphasis markup stripped, string equality, no rounding tolerance |
| batch_size 1024 against config 2048 | run `model_params.json` `hyperparameters.batch_size` against `configs/model.py:9` at `8a557aa3`/`ea18c2cb`/`6976242a` | as named | the discrepancy of §1.4; both values quoted, neither computed |

No number is written into any drafted sentence. The drafted prose adds only scope words.

### Coordinate audit of this report

ANCHORS's premise is that a quarter of the repository's durably cited coordinates have drifted, so I
re-resolved my own before committing rather than after. Every `file:line` this report cites was
checked mechanically: read the line at that number in that blob, assert the named token is present.
**53 coordinates, 53 correct** — 40 in the CBIC-era tree at `9b06053f` and `6976242a`, 5 in the
CoUrb-era commit `58fd219b`, 8 in the `tarik-new` worktree. The eight live-source coordinates in
`src/chapters/` were checked the same way and all eight matched their anchor phrase, with one
exception noted in §2.2, where ANCHORS's line number for the gradient-cosine sentence is `:211` and
the phrase "four seeds each on four Gowalla" is at `:209`. Line numbers here are as of 2026-07-28
and will drift; the phrase in each row is the stable key.

## 6 · [VERIFY] flags

1. **[VERIFY: nash page range]** `src/references.bib:741` gives `pages = {16428--16446}` for the
   Nash-MTL entry. OpenAlex returns only the arXiv preprint record for this title, with no page
   range, and `proceedings.mlr.press` is outside the network allowlist, so I could not check the
   PMLR record. The venue, ICML 2022, is confirmed by the paper's own arXiv comment field. Per
   `AGENT_GUARDRAILS R2` the page range is currently unverified; the precedent set for
   `standley2020tasks` in this same bib was to drop an unverifiable page range rather than carry it.
   Consistency argues for the same treatment or for a check against the PMLR page by someone with
   access.
2. **[VERIFY: the published joint-model next-category column]** No run artifact in this repository
   reproduces `articles/CBIC___MTL/tables/next_result.tex`'s MTL column (§1.5). Any future statement
   that the CBIC results are reproducible from this repository must exclude that column.
3. **[VERIFY: "several configurations" for CBIC]** The author recalls testing several
   configurations. The repository corroborates that configurations varied during the CBIC window and
   that no search harness existed, but it does not preserve any losing configuration, so the
   recollection cannot be turned into a record (§1.4). The optional clause in §1.7 is the strongest
   form I can defend and it is a claim about conduct, so it is `[NEEDS SIGN-OFF]`-class.
4. **[VERIFY: parity divergence in the MobiWac source]** `articles/[mobiwac]/src/sections/02_related.tex:96`
   still reads "three of our six datasets" where the dissertation at `5_mobiwac.tex:209-211` names
   four Gowalla states including Georgia. The two texts are supposed to stay identical under the
   Ch.5 errata regime. Outside this task; named because §2.5's parity edit lands two lines away.

## 7 · What I could not confirm

- **Whether the CBIC paper's pre-submission drafts cited a different work at the Standley site.**
  The repository's earliest `.tex` of any kind is the 2025-10-21 post-publication upload, so the
  history before that date does not exist here. What I established is narrower and stated as such:
  no substitution occurred after the LaTeX entered version control (§4.1).
- **The exact number of configurations tried for either chapter.** Not recoverable from artifacts
  (§1.4).
- **Whether the epoch counts in the committed configs are the epoch counts the published runs used.**
  For the joint model's published CBIC run the batch size in the config and in the run record
  disagree, which is enough to distrust the config as a witness. This is why no drafted sentence
  quotes an epoch count.
- **The Nash-MTL page range**, per flag 1.
- **Anything about the rendered PDF.** I edited nothing under `src/`, so I made no build claim and
  ran no build. The last measured state stands: 104/99 pp, `tex_errors=0`, at `7343c8ad`.

## 8 · Handover checklist for the pass that applies this

1. `3_cbic.tex:303` — append the four-sentence protocol addition (§1.7). Marked addition; needs an
   Appendix B additions paragraph for Article 1, which does not exist yet.
2. `4_courb.tex:257` — append the one checkpoint sentence (§1.7). Extends the eight-addition
   paragraph at `apx_b_errata.tex:200-214`, whose count becomes nine.
3. `2_fundamentals.tex:466-470` — repair the "without identifying the split axis" clause, which
   becomes false the moment step 1 lands (§1.7).
4. `5_mobiwac.tex:186` — nine-word scope insertion (§2.3), plus the same edit in
   `articles/[mobiwac]/src/sections/02_related.tex:87-89` and a line in that article's `ERRATA.md`
   (§2.5). Retire the "Also unstated" comment at `:205`.
5. `4_courb.tex:120` — the narrowed Nash sentence (§3.2) plus the errata row (§3.3), plus one clause
   widened at `apx_b_errata.tex:158-160`.
6. `3_cbic.tex:214` — the narrowed Standley bullet with its footnote (§4.3) plus the errata row.
7. Then build: `source ../src_utils/texenv.sh && make defense && make final && bash ../src_utils/build.sh . both`,
   and expect pagination to move, since items 1, 2, 5 and 6 all add text.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
