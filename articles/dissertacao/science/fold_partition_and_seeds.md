# The fold partition and the seeds: what varies with what

> **Written 2026-08-04, after the author caught a false claim in Appendix A.** The claim was that the fold
> partition is fixed at seed 42 and that only the initialization varies across the four seeds. It is wrong
> in both halves. This document exists so the next agent does not reintroduce it: the mistake is easy to
> make, because the number 42 IS in the code, as a default that the reported runs never use.
>
> **Everything below traces to a file that was opened. No claim here comes from memory.**

---

## 1 · The one-sentence answer

**Each seed draws its own fold partition.** The seed is passed straight into
`StratifiedGroupKFold(random_state=...)`, so changing the seed re-partitions the users. It is not an
initialization-only axis, and the four seeds are therefore not four repetitions over one fixed split.

## 2 · The code path, in order

| step | file:line | what it establishes |
|---|---|---|
| the split call | `src/data/folds.py:1159`, `:1247`, `:1453` | every `StratifiedGroupKFold` / `StratifiedKFold` is constructed with `shuffle=True, random_state=self.seed` |
| where `self.seed` comes from | `src/data/folds.py:1061`, `:1071` | `FoldCreator.__init__(..., seed: int = 42, ...)`, then `self.seed = seed`. **That 42 is a DEFAULT PARAMETER VALUE, and it is the only occurrence of the literal 42 in the whole file.** |
| what the runner passes | `scripts/train.py:1874` | `seed=config.seed` inside the `FoldCreator(...)` construction |
| where `config.seed` comes from | `scripts/train.py:1375-1376` | `if args.seed is not None: config = dataclasses.replace(config, seed=args.seed)`, that is, `--seed` |

The chain is `--seed` -> `config.seed` -> `FoldCreator(seed=...)` -> `random_state=`. The partition is a
function of the seed. The default 42 applies only when `--seed` is omitted.

## 3 · The code says so itself

`scripts/train.py:1961-1962`, the canon guard, emits when `--seed` is not set:

> `[canon-guard] --seed not set -> development seed 42 (overshoots §0.1 by ~+3pp CA / +8pp TX).`
> `Paper-grade numbers require --seed in {0,1,7,100}.`

**42 is the development seed and is explicitly not paper-grade.** The reported runs pass 0, 1, 7 and 100.
Prose that describes the reported protocol as using seed 42 describes the wrong runs.

## 4 · The project's own protocol already said it

The appendix that carried the false claim cited
`docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md`. That file, line 15, points at
`docs/studies/pre_freeze_gates/LANE2_OVERLAP_VALIDATION.md` for

> the overlap-vs-non-overlap **unpaired-across-seed** rule (different fold partitions per arm)

and LANE2 line 75 states:

> (b) Folds are generated on-the-fly per arm (different windowed rows) -> partitions are **NOT
> bit-identical** across arms -> use **unpaired across-seed** stats, not paired per-fold.

## 5 · Measured, not argued

`sklearn.model_selection.StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=s)` on a synthetic
300-user, 12-visits-per-user frame with a 7-class label, comparing each paper seed's partition against the
seed-42 partition:

```
seed   0: rows identical to the seed-42 partition = 21.7% | users in a different fold = 235/300
seed   1: rows identical to the seed-42 partition = 22.3% | users in a different fold = 233/300
seed   7: rows identical to the seed-42 partition = 22.3% | users in a different fold = 233/300
seed 100: rows identical to the seed-42 partition = 26.0% | users in a different fold = 222/300
seed  42: rows identical to the seed-42 partition = 100.0% | users in a different fold = 0/300
```

The last row is the **control**: the instrument reports 100 percent identical when the seed is unchanged,
so the roughly 78 percent user movement in the other rows is a property of the seed and not of a matcher
that always says "different". About four users in five land in a different fold when the seed changes.

## 6 · The frozen-fold cache, and why it does not rescue the old wording

There IS a mechanism that would pin one partition across seeds. `scripts/study/freeze_folds.py` writes
`output/{engine}/{state}/folds/fold_indices_{task}.pt`, and `_resolve_folds` in `scripts/train.py:1844-1860`
prefers that cache when its input signatures still match. **The cache filename carries no seed**
(`freeze_folds.py:121`), so a cache frozen once and reused would give every seed the same partition.

That is not what the reported runs did, and the evidence is in their own logs:

- every reported-run log that mentions folds says `Generating folds on the fly (no cache at .../folds/fold_indices_*.pt)`, in
  `docs/studies/closing_data/archive/run_logs/bf16_island_runs/{alabama,arizona,florida}/champG_bf16.log`
- no `fold_indices*.pt` exists anywhere under `output/` in this checkout (`find output -name 'fold_indices*'` returns nothing)

`docs/studies/closing_data/RUN_MATRIX.md:77` does list "frozen folds" among the T3 prerequisites, so the
INTENT was to freeze. The logs show that the runs behind the reported numbers found no cache and generated
per seed. **If a future round freezes the folds and re-runs, re-measure this document before changing the
prose back.**

## 7 · What the prose may and may not say

**MAY:** each seed is a complete repetition of the five-fold experiment, drawing its own user partition and
its own initialization, so the four seeds vary both axes together.

**MAY NOT, and every one of these was in the document before 2026-08-04:**

- "a fixed partition seed of 42" -- 42 is a default the reported runs override
- "only the initialization varies across the four; the folds do not" -- inverted
- "the same fixed folds" / "one fixed set of five folds" / "over the same folds"
- the limitation "the reported intervals do not include uncertainty from resampling the user splits" --
  they DO include it, because each seed resamples the split

That last one deserves care. The old sentence UNDERSTATED the reported intervals, so correcting it makes
the result stronger, and a claim that grows on correction earns more scrutiny rather than less. What the
corrected sentence must not do is convert this into a claim that the intervals are a full account of split
variability: four draws sample that variability, they do not characterize it.

**A CONSEQUENCE FOR THE TESTS, flagged rather than resolved here.** Paired tests require the two arms to
share folds. Pairing the joint model against the dedicated model WITHIN one seed is still sound, because
both arms run under the same seed and therefore the same partition. What is not available is the
assumption that fold k of seed 0 is fold k of seed 1. The reported tests pair per-seed MEANS (n=4), which
never requires cross-seed fold identity, so the reported procedure survives this correction. Any future
analysis that pairs per (seed, fold) across seeds does not.

## 8 · How to re-verify in three commands

```
grep -n 'random_state' src/data/folds.py                          # every call takes self.seed
grep -n 'config.seed' scripts/train.py                            # what the runner passes
grep -rn 'Generating folds on the fly' docs/studies/closing_data/ # what the reported runs did
```

## 9 · The exhaustive sweep: everywhere the claim had reached

The author asked, after the first five files were corrected, whether the finding had touched any other
appendix or documentation. It had. This section records the sweep so it does not have to be re-run blind.

**The sweep, four patterns over every `.tex` (comments stripped) and every `.md` under the dissertation:**

```
fixed/same/one partition   : fixed (fold )?partition|same fold partition|one fixed (set of )?(five )?folds
                             |the same fixed folds|over the same folds|reuse one fixed|identical folds
seed = initialization only : only the initialization|a different random initialization
denies split variability   : not across resampl|do not (include|measure|cover) uncertainty from resampl
literal seed 42 as protocol: seed of 42|seed 42|seed-42|seed=42
```

**Result: 3 live `.tex` hits, 96 `.md` hits across 204 files scanned.** What each turned out to be.

**Read the directory column before skipping anything.** The first version of this table itemised five `.md`
sites and disposed of "the remaining ~85" as archive history. Three of them were not archive history:
`CODEX_VS_PERSONAS.md`, `etl_tooling_contribution_evidence.md` and `handoff/ch5_mechanism_evidence.md` sit
outside every archive directory, and the first of them carries the retracted premise verbatim. A reviewer
caught it. Since this document exists so the sweep does not have to be re-run blind, a wrong disposition
here would have propagated as a blind spot, which is worse than no table at all.

| site | verdict | action |
|---|---|---|
| `src/chapters/6_conclusion.tex:115` "four seeds over one fixed set of five folds" | FALSE, the last live prose occurrence | corrected; probe `R13-foldseed9` |
| `src/chapters/apx_h_check2hgi_joint_model.tex:229`, `:432` "Seed 42" | **TRUE, different claim** | left alone. This is the seed of the representation-training stage, a single fit, not the fold partition. Appendix H's own audit (`_history/_round14/80_apx_check2hgi_audit.md:84`) traced it to `check2hgi.py` defaults. |
| `GLOSSARY.md:81` the **seed** registry row | FALSE, and the most load-bearing site in the tree, because every chapter defers to it | corrected: the row now says a seed sets initialization **and** partition, and bans "same folds" as an across-seed property |
| `GLOSSARY.md:102` the **n = 20 / n = 4** row | FALSE in its prose, PRECISE in its citation | corrected. Worth recording why the row was wrong while its own source was right: `STATISTICAL_PROTOCOL.md:187-190` says the arms share the **same frozen folds**, which is the pairing condition and is true; the row generalized that to "across seeds", which is the false step. The row now cites both sides, including `LANE2:75` for the across-seed difference. |
| `WRITING_LAW.md:181` the repetition-unit row | FALSE | corrected, with the retracted phrasings added to its banned column |
| `science/mtl_v17_complete_picture.md:281` "fold seed 42" | FALSE, a live spec table | corrected in place |
| `science/check2hgi_v17_complete_picture.md:625` `--seed 42` | **TRUE, different claim** | left alone: a reproduction command line for the representation build |
| `src_utils/codex_reviewer.md:381` COD-006, status **Open** | premise PARTLY refuted | ANNOTATED, not rewritten: revising a reviewer's verdict is the reviewer's call. The two overstatements it flagged stand; the reason it gave for distrusting the fold-level pool does not. The correct reason is that five folds within one seed partition one dataset, not that the partition is shared across seeds. |
| `src_utils/codex_reviewer.md:1059` remedy "Condition intervals on the fixed partition" | instruction now wrong | struck through in place with the reason |
| `src_utils/_history/CODEX_VS_PERSONAS.md:45` (row 006) | premise REFUTED, and the file is **not** under an archive directory | ANNOTATED at the top of the file. It is a dated record of what two reviews saw on 2026-07-27 and its rows are left intact, because reporting them faithfully is the file's whole value; but it can be mistaken for current, so the correction is stated where a reader meets it first. |
| `src_utils/evidence/etl_tooling_contribution_evidence.md:158` "Default seed 42" | **TRUE, no action** | left alone. It says *default*, which is exactly what 42 is (`folds.py:1061`, `src/configs/experiment.py`). |
| `src_utils/_history/handoff/ch5_mechanism_evidence.md:31-32,163` "seed 42" | **TRUE, no action** | left alone. These record ablations that were genuinely run at seed 42 (single-arm mechanism probes, not the reported multi-seed protocol). |
| the remaining ~82 `.md` hits, all under `_history/_archive/`, `_review_v1..v3/`, `_history/_round6/`, `_history/_round9/`, `_history/_round13/_snapshot/`, `_history/_round14/`, `_history/_specialists_v2/`, `reviews/` | **historical record, correct as history** | LEFT ALONE, deliberately: each is a dated record of what was believed when written, and editing one to match today's knowledge falsifies the history that makes it worth keeping. `_history/_round13/_snapshot/GLOSSARY.md` is additionally a pinned copy taken for a measurement and must not be touched. **This row covers ONLY those directories.** Any future hit outside them is live until read. |

**The distinction that decided most of these:** "seed 42" is not by itself a defect. It is false only when
it describes the FOLD PARTITION of the reported experiment. It is true when it describes the seed of a
single training stage (Appendix H's representation build) or appears in a reproduction command. A future
sweep must read the surrounding sentence before touching a hit.
