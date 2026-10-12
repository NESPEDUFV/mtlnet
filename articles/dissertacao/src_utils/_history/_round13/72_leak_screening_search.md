# 72 · The forward-edge screening study: does it exist, and what does it establish?

**Round 13 · 2026-08-04 · read-only archaeology. No `.tex` file and no `PENDENCIAS.md` entry was
edited by this pass.** Repo root for every path below: `/Users/vitor/Desktop/mestrado/ingred`.

**The question asked.** The author states that screening experiments exist showing that the next
visit's category, although it reaches a check-in vector through the graph, does not create a usable
leak. This pass locates those experiments and reports what they actually measure.

**One-line answer.** The study exists, is local (nothing on the GPU host that is not also in the
local repository), and it is a **relative screen among encoders built the same way, at one dataset,
with a linear probe, on ancestor builds of the shipped representation**. It disqualified two
encoders and cleared the lineage the shipped one descends from. It does **not** establish that the
graph channel carries no usable next-category information, and by its own recorded finding the
linear form of the screen is provably able to miss a leak.

---

## a) Does the study exist?

**Yes, as five committed data files plus one narrative record**, all local. Dates are the last
commit touching each file (`git log -1 --format=%ad --date=short -- <path>`).

| # | Path | Date | What it is |
|---|---|---|---|
| 1 | `docs/results/embedding_eval/rescreen_cat/RESCREEN.md` | 2026-06-01 | The narrative record. Names the channel *"forward-temporal neighbor-category bleed"* (`:56`), states the gate and its result (`:86-95`), and records that the linear gate **missed** one leak (`:94-95`). |
| 2 | `docs/results/embedding_eval/rescreen_cat/leak_sniff_fl.csv` | 2026-06-01 | 7 screened encoders at Florida, per-step probe standardized + raw, `verdict` column. |
| 3 | `docs/results/embedding_eval/rescreen_cat/leak_sniff_resln_fl.csv` | 2026-06-01 | 5 residual-variant encoders at Florida, same protocol, control = `check2hgi_resln`. |
| 4 | `scripts/embedding_eval/leak_sniff.py` | 2026-06-01 | The instrument. Docstring `:1-13` states the mechanism it targets in the same terms Chapter 5 uses. |
| 5 | `docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.{json,csv}` | 2026-07-26 | The label-history benchmark: next category from category history alone, no encoder read. 5 datasets. |
| 6 | `scripts/embedding_eval/autocorrelation_ceiling.py` | 2026-07-26 | The instrument for (5). |

Two earlier, **different** measurements were also found and must not be confused with the above —
they answer other questions and are listed here so a later reader does not promote them:

- `docs/results/canonical_improvement/T1-1_leak_audit_AL_AZ_FL.json` (2026-05-16). A **level check**,
  not a leak screen: the same last-slot probe on the canonical build at AL/AZ/FL, reported as a floor
  to be quoted by later experiments. Its `verdict` field reads *"PASS — canonical leak-probe floor
  reproduces historical AL value within σ (31.04 vs 30.84 ± 2.02)"*. It compares a build to its own
  history, never to a clean control, so it cannot detect a leak the canonical build itself carries.
- `docs/studies/pre_freeze_gates/A4_RESULTS.md`, cited in `05_setup.tex` as the second ground. That is
  the **transductive** channel (a graph fitted over all users versus training users only), a different
  channel from the forward edge. Coverage AL/AZ/FL, per `05_setup.tex:88` comment block.

The channel is also independently re-derived in this round at
`src_utils/_history/_round13/71_graphnode_features.md:216-217` (Alabama, 96,326 windows adjacent, 0 not
adjacent), which is the measurement that prompted this search. That is evidence the channel **is
open**, not evidence about whether it leaks.

**Nothing additional on the GPU host.** `ssh:nespedgpu`, read-only shell only, no job submitted:
`/home` is at 84% with 61G available (so the earlier full-disk blocker has cleared, recorded here
for the next session). A `find` over `/home/vitor.oliveira` for `*leak_sniff*`, `*perstep*`,
`*autocorrelation*`, `*leak_probe*` returned **only** the two Florida CSVs, the three `ijm_leak_probe`
JSONs and the three scripts — each present twice because `PoiMtlNet` and `PoiMtlNet-board-m2pro` are
two checkouts of the same tree. Every one of those files is already in the local repository. A grep
for a `leak_sniff` invocation naming any state other than florida, or naming `dk_ovl`, returned
nothing; the positive control on the same command (grep count of `leak_sniff` in `RESCREEN.md`)
returned 1, so the instrument was not blind. **The primary record is local and complete.**

---

## b) What was actually measured

**The probe.** `scripts/embedding_eval/leak_sniff.py`. A **linear** softmax classifier (`torch.nn.Linear`,
AdamW, 200 full-batch steps, `:52-57`) is trained to predict `next_category` (7 classes) from the
**single last window slot** of the nine-visit input window, that is the 64 dimensions of the most
recent history visit alone (`:71`). Metric: **macro-F1**, mean over folds. Cross-validation:
`GroupKFold(5)` **grouped by `userid`** (`:45`). Run twice per encoder, once on features standardized
per training fold and once on raw features, because raw scale is what catches an amplification leak
(`:74`).

**The decision rule.** Not against the labels and not against an absolute threshold. Each candidate
is compared to a **same-protocol control encoder**, and flagged when it exceeds the control by more
than a **margin of 0.03** on either the standardized or the raw run: `verdict = "LEAK" if (d_std >
margin or d_raw > margin) else "clean"` (`:87`, default `margin: float = 0.03` at `:63`).

**Counts, opened and counted rather than trusted (V8).**

```
awk -F, 'NR>1 && $3!=""{c++} END{print c+0}' leak_sniff_fl.csv        -> 7   (perstep)
awk -F, 'NR>1 && $5!=""{c++} END{print c+0}' leak_sniff_fl.csv        -> 7   (perstep_raw)
awk -F, 'NR>1 && $8!=""{c++} END{print c+0}' leak_sniff_fl.csv        -> 7   (verdict)
awk -F, 'NR>1 && $3!=""{c++} END{print c+0}' leak_sniff_resln_fl.csv  -> 5
awk -F, 'NR>1 && $8!=""{c++} END{print c+0}' leak_sniff_resln_fl.csv  -> 5
awk -F, 'NR>1 && $8!=""{c++} END{print c+0}' autocorrelation_ceiling.csv -> 5   (ceiling_macro_f1)
awk -F, 'NR>1 && $99!=""{c++} END{print c+0}' leak_sniff_fl.csv       -> 0   (instrument control)
```

Twelve encoder rows, no empty cells in the columns that carry the result, and the same `awk` on a
column that does not exist returns 0, so the counter is not printing the row count.

**The values, copied from the CSVs, not from any prose that rounds them.**

| file | engine | perstep (std) | perstep_raw | verdict |
|---|---|---|---|---|
| `leak_sniff_fl.csv` | `check2hgi_gcn_ctrl` (**the control**) | 0.4089797540123382 | 0.40744232906432776 | clean |
| | `check2hgi_v3c_wd05` | 0.4086908729403714 | 0.4074983279442259 | clean |
| | `check2hgi_t24_dropedge` | 0.4090257128524225 | 0.40753915026763526 | clean |
| | `check2hgi_t43_sidefeat` | 0.40875968548433583 | 0.40664672671267593 | clean |
| | `check2hgi_t61_p2p` | 0.40725026875759707 | 0.40576293262152363 | clean |
| | **`check2hgi_gat`** | **0.49761650037538024** | **0.48631035868799294** | **LEAK** |
| | `check2hgi_rgcn` | 0.3328098159387623 | 0.4141676223058579 | clean |
| `leak_sniff_resln_fl.csv` | `check2hgi_resln` (**the control there**) | 0.4196859144977155 | 0.41815720719390814 | clean |
| | `check2hgi_resln_v3c` | 0.4195106950795096 | 0.41844646012492437 | clean |
| | `check2hgi_resln_dropedge` | 0.4198671409315892 | 0.4185441741729707 | clean |
| | `check2hgi_resln_sidefeat` | 0.42103540845720755 | 0.4197321822055513 | clean |
| | `check2hgi_resln_p2p` | 0.4196511428046975 | 0.4180905822188721 | clean |

**Datasets covered by the probe: Florida only.** `state` is the first column of both CSVs and reads
`florida` in all twelve rows. The launch command is committed at
`scripts/embedding_eval/resln_candidates_campaign.sh:42-43` and passes `--state florida`.

**Folds and initializations.** Five folds, `GroupKFold` by user. `GroupKFold` in `leak_sniff.py:45`
is constructed as `GroupKFold(n_folds)` with no `shuffle` and no `random_state`, so the **split is
deterministic and is not a seed axis**. Separately, `grep -c 'seed\|random_state\|manual_seed'
scripts/embedding_eval/leak_sniff.py` returns **0** — the positive control, the same pattern on
`scripts/probe/leak_sniff_ijm.py`, returns line 28 `StratifiedKFold(..., random_state=42)`, so the
grep can see a seed when one is there. **Consequence: the probe's own linear-layer initialization is
unseeded and unrecorded, and there is exactly one run per encoder.** There is no repetition over
seeds anywhere in this study; `n` is 5 folds, not seeds × folds.

**The label-history benchmark** (`autocorrelation_ceiling.json`, 2026-07-26) is a separate quantity
and covers more ground: 5 datasets, all rows used, `GroupKFold(5)` by user, best of four
label-only predictors. AL 0.28 / AZ 0.3232 / FL 0.3617 / CA 0.3242 / IST 0.3016, with
`majority_floor_macro_f1` 0.0566 to 0.0727. The file's own `skipped` field reads
`[{"state":"texas","error":"FileNotFoundError: texas: missing output/check2hgi/texas/temp/checkin_graph.pt"}]`
— Texas is absent for a stated reason, which is a disclosed skip, not a silent one.

---

## c) What it establishes, and what it does not

**Establishes, in one sentence.** At Florida, on a five-fold user-grouped split, a linear probe
reading the last history visit alone recovers the next category no better from the encoders of the
Check2HGI lineage that the shipped representation descends from (0.4090 / 0.4074 standardized / raw
for the GCN control; 0.4197 / 0.4182 for the residual variant) than from the same-protocol control,
while an attention-based encoder screened beside them reached 0.4976 / 0.4863 and was disqualified —
so the screen has demonstrated discriminating power on this exact channel and the shipped lineage's
ancestors sit at the clean level on it.

**Does not establish** — and each of the following is verified against the data, not inferred:

1. **Not "the channel does not leak."** The screen is *relative*: `verdict` is computed as a delta
   against a control drawn from the same lineage (`leak_sniff.py:82-87`). If the control itself
   carries the leak, every candidate compared to it reads clean. The measurement is therefore
   structurally incapable of detecting a leak shared by the whole family. `RESCREEN.md:57` records the
   design intent honestly, and the chapter already says as much at `05_setup.tex:70`.
2. **The linear form provably misses at least one real leak, in this very study.**
   `check2hgi_rgcn` reads 0.3328 standardized / 0.4142 raw in `leak_sniff_fl.csv:8` — **clean** by the
   gate — and `RESCREEN.md:95` records that the same encoder scored 0.754 next-category under a GRU
   against a 0.646 control, and 0.9986 on the POI-pooled probe. `RESCREEN.md:95` states the conclusion
   in its own words: the cheap per-step linear gate *"catches gat but MISSES rgcn."* A passing linear
   score is therefore evidence of no *linear* leak, and nothing more.
3. **One dataset.** Florida. Not Alabama, Arizona, California, Texas or Istanbul. Confirmed by the
   `state` column in both CSVs and by the launch flag in the campaign script; the GPU-host search
   found no run at any other state.
4. **Ancestor builds, not the shipped one.** The board and the reported results run on
   `check2hgi_dk_ovl` (`docs/studies/closing_data/RESULTS_BOARD.md:4`, `docs/NORTH_STAR.md:13`).
   `grep -rn` for `dk_ovl` inside `docs/results/embedding_eval/rescreen_cat/` returns **0 lines**;
   the same pattern across `docs/` and `scripts/` matches **441 files**
   (`grep -rl 'dk_ovl' docs/ scripts/ | wc -l`), so the grep is not broken. The two mentions of `dk_ovl` next to `leak_sniff` anywhere in the tree are both the
   *recommendation to run it*, at
   `src_utils/_history/_archive/reviews_v1/dissertation_review_v1.md:244` and its codex twin. **It was never run.**
5. **No seed axis.** Per the seed evidence in §b: one unseeded run per encoder over a deterministic
   split. The chapter's phrase "at one random initialization" is the correct order of magnitude, but
   note it cannot be read off either instrument — see the [VERIFY] flag below.
6. **The decisive causal control was never run.** `dissertation_review_v1.md:247-248` proposed
   rebuilding Check2HGI at Alabama with backward-only (causal) edges, or with the category one-hot
   removed from node features, and comparing downstream next-category. A grep for
   `backward.only|causal edge|category one.hot removed` across `docs/` and `articles/` returns only
   that recommendation and unrelated `_BACKWARD_ONLY_LOSSES` code hits (a gradient-balancer guard,
   nothing to do with graph edges). No such rebuild exists on disk locally or on the GPU host.

**Verifying the three limits the chapter already states** (`05_setup.tex:87`, comments stripped per V4:
*"the probe is linear, it was run at Florida alone at one random initialization over five user-grouped
folds, and it was run on those ancestor builds of the representation rather than on the one that
produced the results reported here"*). Limit 1 **confirmed** and stronger than stated, because the
study's own R-GCN row shows the linear form failing. Limit 2 **confirmed** for Florida and for the
five folds; the "one random initialization" half is the one clause I cannot source (below). Limit 3
**confirmed**, and the shipped engine name is nowhere in the screening directory. **The three limits
are accurate. They are not, however, the whole residual: limit 1 understates the case, and the
relative-control structure of the screen (point 1 above) is a fourth limit the sentence does not name,
though the chapter does name it in the following clause.**

---

## d) Is this enough for a Chapter 2 sentence saying the graph channel does not create a usable leak?

**No.** A Chapter 2 sentence of that form would be a general claim about the representation, and the
evidence is a relative screen at one of six datasets, with a probe whose blindness is demonstrated
inside the same record, on builds that are not the one Chapter 5 reports. Writing "the channel does
not create a usable leak" would upgrade a bounded screen into an absolute negative, which is the
class of move the honesty rules exist to stop. Chapter 5 gets to make its narrower statement because
it states the mechanism, names the audit, gives the numbers and prints all three limits on the same
page; Chapter 2 is a thin fundamentals chapter with no room for that apparatus, and the claim does
not survive being separated from it.

**The author's standing ruling already resolves this.** The round-13 decision on AUT-20 is that
Chapter 2 fixes the phrasing and stays **silent** on the graph channel until better information
exists. This pass produces no information that changes that ruling: the study it found is the study
Chapter 5 already cites, with the limits Chapter 5 already prints.

**If a sentence is wanted anyway**, the narrowest form the data supports, and it belongs in Chapter 5
rather than Chapter 2:

> A development-time screen at one dataset found that a linear probe reading the last history visit
> alone recovers the next category no better from this lineage of encoders than from a same-protocol
> control, while an attention-based variant screened beside them exceeded that control and was
> discarded on that evidence.

Every clause there is sourced above. What may **not** be written: *the channel does not leak*; *the
representation does not carry the next category*; anything quantified across datasets; anything that
attributes the screen to the shipped representation.

**What would change the answer** — in the order that buys the most per unit of compute, and none of it
was started here:

1. Run the existing `leak_sniff.py` at the remaining five datasets on the shipped `check2hgi_dk_ovl`
   embeddings. No retraining, existing parquet, closes limits 2 and 3 at once.
2. Add a nonlinear per-step probe (small MLP or GRU on the last slot) to close the R-GCN-shaped blind
   spot, which is the limit that actually undermines the claim.
3. The one decisive control: rebuild at Alabama with backward-only edges or with the category one-hot
   removed from node features, and compare downstream next-category. This is a training run; **I did
   not start it and I do not recommend starting it from this pass** — it is an author decision against
   the August calendar.

---

## e) Source ledger

Working directory for every command: `/Users/vitor/Desktop/mestrado/ingred`.

| # | File opened | What it establishes | Command that reads it |
|---|---|---|---|
| 1 | `articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex` | The fourth ground names the channel and the screen; `:87` gives the three limits; the comment block at `:88-107` names the record, the probe, the CSVs and the exact protocol. This is where the trail starts. | `sed -n '60,120p' articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex`; limits sentence via `grep -vE '^[[:space:]]*%' <f> \| grep -n 'three limits'` (V4) |
| 2 | `articles/dissertacao/AGENT_GUARDRAILS.md` | §1 citation, §2 number, §3 claim, §4b V1-V13 process law obeyed by this report. | `sed -n '1,265p' articles/dissertacao/AGENT_GUARDRAILS.md` |
| 3 | `docs/results/embedding_eval/rescreen_cat/RESCREEN.md` | `:56-57` names the channel and the intended reference; `:86-95` the gate, the FL table, and the recorded finding that the linear gate misses R-GCN. Dated 2026-06-01. | `sed -n '1,130p' <f>`; `sed -n '86,96p' <f>` |
| 4 | `docs/results/embedding_eval/rescreen_cat/leak_sniff_fl.csv` | 7 encoder rows, Florida, per-step std/raw + verdict. The three four-decimal values Chapter 5 quotes. | `cat <f>`; counts via the four `awk -F,` lines in §b |
| 5 | `docs/results/embedding_eval/rescreen_cat/leak_sniff_resln_fl.csv` | 5 residual-variant rows, Florida, control `check2hgi_resln` at 0.4197/0.4182. | `cat <f>`; `awk -F, 'NR>1 && $8!=""{c++} END{print c+0}' <f>` |
| 6 | `scripts/embedding_eval/leak_sniff.py` | The instrument: linear probe on the last slot, `GroupKFold(5)` by user, macro-F1, std and raw, verdict = delta vs control > margin 0.03. No seed anywhere. | `sed -n '1,110p' <f>`; `grep -c 'seed\|random_state\|manual_seed' <f>` -> 0 |
| 7 | `scripts/probe/leak_sniff_ijm.py` | **Positive control for the seed grep** (V3): the same pattern returns `:28 StratifiedKFold(..., random_state=42)` here, so the zero at #6 is a real absence. | `grep -n 'seed\|random_state\|shuffle' <f>` |
| 8 | `docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.{json,csv,_predictors.csv}` | Label-history benchmark, 5 datasets, four predictors, majority floors, per-fold values; Texas disclosed as skipped for a missing `checkin_graph.pt`. | `cat autocorrelation_ceiling.csv`; `python3 -c "import json; d=json.load(open(...)); print(d['skipped'])"` |
| 9 | `docs/results/canonical_improvement/T1-1_leak_audit_AL_AZ_FL.json` | A level check, not a screen: canonical build, AL/AZ/FL, `StratifiedKFold` (not user-grouped), compared to its own historical value. Must not be promoted to a leak screen. | `python3 -c "import json; print(json.dumps(json.load(open(...)), indent=1))"` |
| 10 | `docs/results/canonical_improvement/ijm_leak_probe_{canonical,t32_resln,hypD}_FL.json` | Florida last-slot probe on three builds with `user_leak_drift_pp` of 0.10 / -0.02 / 0.02; a user-grouping check, not a forward-edge screen. | same `python3 -c` pattern |
| 11 | `articles/[mobiwac]/archive/LEAK_AUDIT_EXTEND_HANDOFF.md` | The **transductive** audit (A4) is the second ground and a different channel; AL/FL on disk, AZ/CA/TX/IST left as an extension. | `sed -n '1,70p' <f>` |
| 12 | `articles/dissertacao/src_utils/_history/_archive/reviews_v1/dissertation_review_v1.md:205-250` | An independent reviewer's own derivation of the channel, the same four-row table, the three residuals, and the two unrun recommendations (all six datasets on `dk_ovl`; the causal-edge rebuild). | `sed -n '205,250p' <f>` |
| 13 | `docs/studies/closing_data/RESULTS_BOARD.md`, `docs/NORTH_STAR.md` | The shipped engine is `check2hgi_dk_ovl` (`RESULTS_BOARD.md:4`, `NORTH_STAR.md:13`), which is what makes limit 3 bite. | `grep -rn 'dk_ovl' <f>` |
| 14 | `docs/results/embedding_eval/rescreen_cat/` (directory) | `dk_ovl` appears **nowhere** in the screening directory. **Instrument validated (V3):** the same pattern matches 441 files elsewhere in the tree. | `grep -rn 'dk_ovl' docs/results/embedding_eval/rescreen_cat/ \| wc -l` -> 0; `grep -rl 'dk_ovl' docs/ scripts/ \| wc -l` -> 441 |
| 15 | `scripts/embedding_eval/resln_candidates_campaign.sh:42-43` | The committed launch command, `--state florida --control check2hgi_resln`. Florida is a launch fact, not only a CSV fact. | `grep -n -B3 -A6 'leak_sniff' <f>` |
| 16 | `scripts/embedding_eval/rescreen_build.sh` | How the screened variants were built. **No `seed` token in the file**, hence the [VERIFY] below. | `grep -n 'seed\|--state\|florida' <f>` |
| 17 | `articles/dissertacao/src/chapters/apx_d_ceiling.tex` | Appendix D separates the two reference quantities and states the screening procedure in prose consistent with the code. | `sed -n '1,60p' <f> \| grep -vE '^[[:space:]]*%'` |
| 18 | `articles/dissertacao/src_utils/_history/_round13/71_graphnode_features.md:216-217, :242` | This round's own adjacency measurement (96,326 of 96,326 at Alabama, 0 not adjacent) and its pointer to `05_setup.tex:87`. Evidence the channel is open. | `grep -n -i 'leak\|screen\|adjacen' <f>` |
| 19 | `ssh:nespedgpu` (read-only shell, no job submitted) | `/home` 393G, 313G used, **61G available, 84%** — the 2026-07-29 full-disk blocker has cleared. `find` for `*leak_sniff*`, `*perstep*`, `*autocorrelation*`, `*leak_probe*` under `/home/vitor.oliveira` returns only files already present locally, duplicated across the `PoiMtlNet` and `PoiMtlNet-board-m2pro` checkouts. No invocation naming a non-Florida state or `dk_ovl`. Positive control on the same grep returned 1. | `c.call_command("df -h /home \| tail -1; find /home/vitor.oliveira -maxdepth 6 \\( -iname '*leak_sniff*' -o ... \\) ...")` and a second read-only grep call |

---

## [VERIFY] flags

- **[VERIFY: the "one random initialization" clause at `05_setup.tex:87`.]** I could not source it to
  either instrument. `leak_sniff.py` contains no seed token (0 matches; positive control returns a
  match on a sibling file), and its `GroupKFold(5)` is unshuffled, so the split is deterministic and
  the probe's own `torch.nn.Linear` init is unseeded. `scripts/embedding_eval/rescreen_build.sh`
  likewise contains no `seed` token, so the encoder-build seed is a default I did not trace into
  `check2hgi.py`. The clause is very likely right in substance — there is demonstrably one run per
  encoder, which is the point it makes — but the phrase "one random initialization" is not read off a
  file. Weaker and fully sourced alternative: *"one run per encoder over a single deterministic
  five-fold user-grouped split."* Not a blocker for an under-review chapter; flagged so it is not
  quoted as measured.
- **[VERIFY: whether any nonlinear per-step probe was ever run at any dataset.]** I searched for
  `leak_sniff`, `perstep`, `probe`, `shuffle`, `permutation`, `negative control` and `sanity` across
  `.md`/`.json`/`.csv`/`.py` in `docs/` and `articles/`, and on the GPU host for output files. I found
  the *recommendation* (`dissertation_review_v1.md:246`) and the *evidence that one is needed*
  (`RESCREEN.md:95`), and no result file. Absence of a result file is what I can state; I did not
  exhaustively enumerate every JSON in `docs/results/` (thousands of files), so this is a bounded
  negative rather than a proof.
- **[VERIFY: whether `check2hgi_dk_ovl` differs from the screened ResLN ancestor in any way that
  bears on this channel.]** Out of budget. `CANONICAL_VERSIONS.md:42-44` describes `dk_ovl` as a
  gated stride-1 overlap of v14, and stride affects window density rather than graph edge direction,
  which suggests the channel is unchanged; but I did not open the builder to confirm that the edge
  construction and node features are identical, so I am not asserting it.
- **Archaeology budget.** Spent within the 60 minutes. Digging stopped at the three flags above rather
  than continuing into `docs/results/` file-by-file.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
