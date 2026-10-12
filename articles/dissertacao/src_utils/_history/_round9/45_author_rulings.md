# 45 · The author's rulings, applied — round 9c

> **What this is.** One section per ruling the author wrote in `PENDENCIAS.md` as a
> `> **AUTHOR:**` block, with his words, what was changed, and the rendered evidence. His words are
> final; where I would have chosen differently it is stated and his way is what shipped.
>
> **Baseline, measured at `5c074a2a` before any edit.** defense 101 pp / 0 TeX errors, academico 98,
> ppgc 102, extra 20; `count_errata_rows.py` rc=0 at 44 rows; `check.sh` rc=1 on three pre-existing
> findings. The brief's baseline said defense 102 pp — that figure predates phase 0, whose Appendix F
> rework removed a page. Not a defect, a stale reference point.
>
> **After this round.** defense 101 pp / 0 errors, academico 98, ppgc 102, extra 22;
> `count_errata_rows.py` rc=0 at 50 rows; `check.sh` as recorded in §Gates below.
>
> **Not mine, reported and left alone.** `1_introduction.tex` carried an uncommitted 161-line rewrite
> written at 18:17 by another track in this checkout. I did not author it and, on instruction, reverted
> it; both versions are preserved at `_UNCOMMITTED_1_introduction_1817.{diff,tex.bak}` and
> `_UNCOMMITTED_1_introduction_final.{diff,tex.bak}`. See §Introduction below.

---

## 2.11 · Region asymmetry — his option B

> **AUTHOR (his ruling, and my recommendation confirmed in session):** option B — promote the caveat
> in BOTH the MobiWac manuscript and the dissertation, so both read "four wins plus two statistically
> non-inferior".

**Applied. Two sites, not nine, and the correction to the premise is part of the deliverable.**

The item states the frame prose says only "category everywhere, region at four" and drops the TOST
caveat at nine sites. Two sweeps were run over all 54 live `.tex` files of the dissertation and the 16
of the paper, comments stripped via `check_audit_claims.live_text` and matching across line wraps.

| sweep | what it looked for | result |
|---|---|---|
| 1 | sites stating the partition (`four of six`, `four of the six`, `quatro deles`, `at four of`) | **15 sites, 14 of which already paired the TOST caveat** |
| 2 | region-claim sentences with a comparative verb and **no** partition at all | **exactly 2 defects** |

Sweep 1 could only find sites where the partition was *present*, so it could not answer the question
the item asks. Sweep 2 is the complementary class and it found the real defects. The nine-site figure
in the tracker was an inventory of where the claim *appears*, not of where the caveat is *missing*.

**Defect 1 — `6_conclusion.tex:115`, the consolidated answer.** Rendered defense p. 80:

> "…at quality that outperforms the dedicated models on the category task at all six datasets and on
> the region task at four of the six. At the other two it is statistically non-inferior to them within
> a two-point margin (TOST)."

Two faults in one clause: the partition was collapsed to "outperforms or matches", and bare
"everywhere" is banned by name at `WRITING_LAW.md:83`. Split into two sentences rather than one
three-clause sentence. "non-inferior" is TOST language and is not upgraded.

**Defect 2 — the Chapter 5 results subsection lead, in BOTH trees.** Rendered defense p. 63:

> "One model outperforms the dedicated models on next category at all six datasets, and on next region
> it outperforms them at four of the six and is statistically non-inferior within a two-point margin at
> the other two."

Applied to `5_mobiwac/06_results.tex` and `[mobiwac]/src/sections/06_results.tex` in the same pass and
**verified textually identical afterward** with the comment-stripping sweep. Recorded in the paper's
`ERRATA.md` under a 2026-07-30 heading.

**The introduction needed no edit, measured not assumed.** It already carries the caveat at `:142`
("…on the region task at four of six, with statistical non-inferiority within a two-point margin
(TOST) at the other two") and has since `70e794f1`. All three region-comparative sentences in that
file carry it.

**One overlap I did not decide for you.** The Chapter 6 sentence is also **BLQ-2** in `PENDENCIAS` §6.10,
which carries no ruling. The wording applied is BLQ-2's own option 1, so the two agree; if you want it
reverted it is one sentence.

---

## 2.9 · Both Chapter 5 trees now editable

> **AUTHOR:** "como estamos um fase de revisão no mobiwac, conseguimos mandar uma revisão ainda"

**Used twice.** It is the permission that makes 2.11's second defect fixable in the paper, and I judged
that the cosine appendix's seven-dataset result **does** warrant a mention in Chapter 5 — this is what
readability finding R-6 asked for and closed as unavailable ("Ch.5 is under review and its body is
deliberately untouched, so the natural fix is closed").

Added at `5_mobiwac/02_related.tex`, rendered p. 63:

> "Appendix~D of this dissertation measures the same quantity on the final model across seven datasets
> and reaches the same conclusion."

**This one sentence is deliberately NOT mirrored into the paper** — the single exception to keeping the
two texts identical — because it cites a dissertation appendix whose referent does not exist in the
submitted manuscript. That is the same class as the two corrections already in Table B.5, whose banner
reads "each depends on material the article has no room for". A third row in Table B.5 declares it.

---

## 2.12 · The Pareto-stationary registry gap, and the MGDA imprecision

> **AUTHOR:** "Ótimo trabalho, pode adicionar essa linha no appendix B, para termos conhecimento desse
> detalhe menor e não deixar passar batido."

**Applied — and the row required a prose change, which is the half I nearly got wrong.** The finding
was offered to him as *"Se quiser corrigir, é uma linha de errata no Apêndice B, e a decisão é sua"*.
The errata line he authorized exists only if the sentence is corrected, so both halves are applied; a
row describing a narrowing that had not happened would have told a reader the chapter says something
its page does not.

`3_cbic/basis.tex:44` and `CBIC___MTL/sections/basis.tex:52`, identical in both, rendered p. 31:

> "MGDA finds a direction that decreases every task loss, unless the current point is already
> Pareto-stationary"

**Why the published clause was wrong.** It read "finds Pareto-optimal descent directions", attaching
Pareto *optimality* to the per-step direction. `sener2018mgda`'s abstract, read at arXiv:1810.04650
this session, claims Pareto optimality for an **upper bound** on the multi-objective loss and under
stated assumptions ("we prove that optimizing this upper bound yields a Pareto optimal solution under
realistic assumptions"), not for the step. This chapter does not use MGDA, so no result depends on it.
`Pareto-stationary` is registered in the glossary under your decision (a) on this same item, so the
replacement wording is admissible under the fail-closed rule.

Errata row: Table B.1, which grew 8 → 10 rows.

---

## 2.14 · The Nash-MTL entry, against your PMLR paste

> **AUTHOR:** supplied the PMLR BibTeX verbatim (pages 16428–16446, PMLR v162).

**Applied to all five bibliographies, field by field. Your paste is from the publisher's own page, so
it outranks every other copy, including the previous entry here.**

| bib | key | what differed | now |
|---|---|---|---|
| `dissertacao/src/references.bib` | `nash` | booktitle was `Proc. ICML`; volume, series, publisher, month, url absent | matches paste |
| `[mobiwac]/src/references.bib` | `navon2022nashmtl` | same | matches paste |
| `CBIC___MTL/references.bib` | `nash` | **`@article` with `journal = {arXiv preprint arXiv:2202.01017}`**, title downcased | matches paste |
| `CoUrb_2026/src/references.bib` | `nash` | same as CBIC | matches paste |
| `CoUrb_2026/src_en/references.bib` | `nash` | same as CBIC | matches paste |

The three article bibs cited the work as a **preprint**, which is an entry-type defect and not merely
missing fields. Pages `16428--16446` and the year were already correct in the dissertation and are
unchanged. Verified programmatically: all five now match the paste on type and on all ten fields.

Errata row: Table B.4, 18 → 19 rows.

**One note on style, since it is visible.** Your paste spells the venue out in full. That is not a
breach of this file's convention: 18 of its 61 `booktitle` fields already carry full venue names.

---

## 2.15 · Three unsupported citations and one banned term — path A

> **AUTHOR:** "Vamos de troca em ambas, seguindo o caminho A, modificando os artigos originais e
> adicionando uma entrada no appendix B."

**Applied in both the original article trees and the dissertation, with an errata row for each.**
Every substitute was verified at its source of record **this session**, not retyped from another
paper's bibliography.

**1. `ruder2017sluice` → `baxter2000model`** (`3_cbic/method.tex:97`, `CBIC___MTL/sections/method.tex:84`).
The bullet argues that constraining the hypothesis space regularizes. Ruder et al. is a **soft**-sharing
method presented as an improvement on fixed sharing, so it argues against the bullet. Baxter, *A Model
of Inductive Bias Learning*, JAIR 12:149–198, DOI `10.1613/jair.731`, read at Crossref: its abstract
states the argument the bullet makes, choosing a hypothesis space "large enough to contain a solution …
yet small enough to ensure reliable generalization", searched over an environment of related tasks.
Already in every relevant bibliography; no entry added. `ruder2017sluice` remains correctly cited at
`3_cbic/basis.tex:40` and `:48`.

**2. `sun2020go` — claim narrowed, not re-cited** (`4_courb/methodology.tex`, plus CoUrb PT and EN).
The sentence attributed to it that temporal cycles carry information about the **functional nature** of
places. `sun2020go` is LSTPM (AAAI 2020), which models user preference for next-POI recommendation and
claims nothing of the kind. Split: the temporal-regularity half now cites the dataset paper
(`cho2011gowalla` / `cho2011friendship`, already cited in the same chapters), `sun2020go` is kept for
what it does establish, and **the place-semantics half is dropped rather than re-attributed** because
nothing in the bibliography supports it.

**3. `belkin2003laplacian` → `Xu2023`** (same three files). The cited object is an L2 penalty pulling a
subcategory embedding toward its parent over a known label tree. Laplacian eigenmaps is nonlinear
dimensionality reduction; the link is a shared graph Laplacian and nothing more. `Xu2023` is TME, ACM
TOIS 41(4), DOI `10.1145/3582553`, whose abstract, read at Crossref, says it "utilizes the predefined
category hierarchy to regularize the relatedness among categories" — the same construction. Already in
each bibliography; no entry added.

**4. The banned term `fclass` → "fine class"**, three occurrences in `4_courb/methodology.tex` and the
same in both CoUrb sources. `GLOSSARY.md:73` registers the reader-facing name and forbids the code
identifier in prose. The italics go with it: `fclass` was italicized as a code token and "fine class"
is ordinary English, so it is roman.

**Verified after editing across all five trees** (54 + 9 + 9 + 9 + 16 files, comments stripped):
`fclass` in prose = **0**; the three unsupported citation-claim pairings = **0**. The pattern was proved
able to find the term when present, so the zeros are absences rather than a broken instrument.

Errata rows: Table B.3, 4 → 7 rows. Each published source carries a comment stating that its **PDF of
record is not edited**.

---

## 2.16 · Publishing the four diverged artifacts — PREPARED, NOT PUSHED

> **AUTHOR:** "Vamos publicar as alterações na branch do mobiwac."

**I cannot push from this sandbox** (the credential helper is interactive and `.git/config` is not
writable here). The change is prepared and verified in a clean clone; the commands below are yours to
run. **I did not fabricate a push.**

Clone: `.tmp/mobiwac_pub_96069`, branch `mobiwac` at `0288cb70`. The four local files copied over their
published counterparts, all four of which live under `scripts/closing_data/` on that branch:

| file | added | removed | net |
|---|---:|---:|---:|
| `m1_stats_n20.py` | 80 | 4 | +76 |
| `superiority_wilcoxon.py` | 31 | 10 | +21 |
| `m2_prereg_perfold.py` | 14 | **22** | −8 |
| `region_match_tost.py` | 1 | 1 | 0 |

**The diff is NOT purely additive, and you should read this before running the commands.** Three of the
four remove lines, and the removals are not incidental: on the `mobiwac` branch these scripts were
**rewritten for the published layout**. The branch has no `docs/` tree — it keeps artifacts under
`analysis_protocol/` — and the published copies were edited to match, including a `RESULTS_ROOT`
environment override and docstrings pointing at `analysis_protocol/…`. The local copies point at
`docs/studies/…` and `docs/results/…` paths, which **do not exist on that branch** (18, 11, 7 and 7
references respectively).

So publishing the local versions replaces working published scripts with copies whose paths are wrong
for the branch. Your ruling is to publish, and this is your call to make; I am flagging it rather than
quietly doing it, because a reader who clones the branch and runs them would hit missing paths.
`region_match_tost.py` is the one clean case: a single docstring path, 2 lines.

```bash
# Run from a shell that can authenticate to the remote.
cd /Users/vitor/Desktop/mestrado/ingred/.tmp/mobiwac_pub_96069
git status --porcelain           # expect exactly the four scripts/closing_data/*.py as ' M'
git diff --numstat               # expect 80/4, 31/10, 14/22, 1/1 as tabulated above
git -c user.name="Vitor Hugo" -c user.email="vitor@Vitors-MacBook-Pro.local" \
    commit -am "publish the local versions of the four diverged analysis scripts"
git push origin mobiwac          # this is the step I cannot run
```

If you prefer only the clean one:

```bash
cd /Users/vitor/Desktop/mestrado/ingred/.tmp/mobiwac_pub_96069
git checkout -- scripts/closing_data/m1_stats_n20.py \
                scripts/closing_data/m2_prereg_perfold.py \
                scripts/closing_data/superiority_wilcoxon.py
git -c user.name="Vitor Hugo" -c user.email="vitor@Vitors-MacBook-Pro.local" \
    commit -am "publish the corrected pre-registration pointer in region_match_tost.py"
git push origin mahalle 2>/dev/null || git push origin mobiwac
```

---

## 2.18 · The published notes ref — option 2 + 3, ONE HALF BLOCKED

> **AUTHOR:** "2+3"

**Option 3, part 2: measured, and there is nothing to fix.** `git config --get-all
remote.origin.push` returns **nothing** at any scope (rc=1), and `push.default` is likewise unset. No
broad refspec is pushing notes from this configuration.

**Option 3, part 1: BLOCKED.** `git config --local notes.rewriteRef ""` exits **4** with
`error: could not write config file .git/config: Operation not permitted` — the sandbox protects
`.git/config`. The key remains unset (verified reading the exit code directly, not through a pipe;
`git config --local --get-all notes.rewriteRef` → rc=1, 0 bytes).

**Option 2: BLOCKED, same reason as 2.16** — deleting a published ref requires a push.

The remote still has `refs/notes/commits` at `99c0a34b1a`. Local notes now number **24**, not the 15
the item recorded; the item's own count was taken earlier in the round. Both commands are yours:

```bash
cd /Users/vitor/Desktop/mestrado/ingred
git push origin :refs/notes/commits        # option 2: delete the published ref, keep notes locally
git config --local notes.rewriteRef ""     # option 3: stop it coming back
git config --get-all remote.origin.push    # expect no output (already true, measured 2026-07-30)
git ls-remote origin | grep notes          # expect no output after the push
```

---

## 2.19 · The word-count convention

> **AUTHOR:** "310/271 no relatorio, eu não entendi porque há 3, mas o quantidade de plavras no resumo
> hoje são essas."

**Applied as a durable, reproducible record:
[`src_utils/WORDCOUNT_CONVENTION.md`](../../WORDCOUNT_CONVENTION.md).** It states the convention, carries
the command, and names the tree it was measured against — which was the durable defect the item
identified: a measurement with no stated tree state can only be re-taken, never re-checked.

The convention that reproduces your figures: rendered PDF, header and keyword block stripped,
soft-break marker removed, split on whitespace, **numerals counted**. Run today it returns **Resumo
310** — your figure exactly — and **Abstract 274**.

**The three-word gap is not an instrument disagreement.** The Abstract's prose changed after the report
was written: measured on the source with identical cleaning, `35fe46cc` = 270 words, HEAD = 275. The
word-level diff is one wording change ("every state" → "the three states", "so" → "indicating that in
that configuration"). So 271 is the correct count of the Abstract **as it stood when you read it**, and
274 is the same convention on today's text. Both readings are written up in the file; the choice of
which to carry to deposit is yours.

**Nothing in the document prints a word count** — measured across all live `.tex` files, with a positive
control proving the pattern finds the figures where they do exist. So no printed claim is wrong today.
The round-6 reports are left as written: they were correct against the tree they measured, and this file
is the pointer that says which tree that was.

---

## 2.20 · Chapter 4's italicized ordinary English — option 2

> **AUTHOR:** "2."

**Applied: 105 italic macros removed** from the six chapter files plus 2 from a data table. Your option
2, verbatim: *"Remover o italico de vocabulario corrente (embedding, baseline, encoder e plurais),
mantendo italico so em termo tecnico em primeiro uso."*

Measured with `live_text`, HEAD versus now over the same file set: **153 → 48** italic macros in the six
chapter files (155 → 48 including the three data tables). Removed, by word: embedding 18, baseline 16,
encoders 15, encoder 14, embeddings 12, check-ins 7, check-in 4, `fclass` 3 (item 2.15), head 2,
timestamp 2, and one each of heads, timesteps, pipeline, bias, framework, benchmark, folds, dataset,
grid, skip-gram, negative sampling, random walks.

**Kept italic, because your option 2 keeps technical terms at first use:** the named models and methods
(Deep Graph Infomax, Hierarchical Graph Infomax, Spatial-Temporal MTLNet, Feature-wise Linear
Modulation, Sinusoidal Representation Networks, Category-Aware Location Embedding, Long- and Short-Term
Preference Modeling, Transformers, sphereM), the method-internal terms at first use (one-hot,
skip-gram, negative sampling), the architecture-figure module names, the seven taxonomy category names,
and the two frame task names in the preface. That matches the rest of the document, which sets ordinary
vocabulary roman: outside Chapter 4, `embedding` is roman 54 times of 55, `encoder` 27 of 27, `baseline`
21 of 21.

**One translation artifact fixed with it.** The published PT read "caminhadas aleatórias
(*random walks*)", where the italic parenthetical glossed the Portuguese with the English loan term. In
English the gloss repeats the words it glosses, so it is dropped rather than de-italicized.

**A measurement caught a defect in my own edit.** Predicted 155 − 101 = 54 remaining; measured 49. The
five-word gap was real: my provenance comment had absorbed the rest of a source line, commenting out a
live sentence. That prompted a prose-delta audit of every changed file (see §Self-audit).

---

## 2.21 · "license the verbs" — your advisor's flag

> **AUTHOR:** his advisor flagged one term, `license the verbs`, in the fundamentals chapter.

**Applied at the two sites where it is opaque; the third is kept deliberately.** All **13** occurrences
of the license family in live prose were read one by one, not sampled.

| site | rendered | verdict |
|---|---|---|
| §2.4 opener | p. 24 | **rewritten** — first occurrence in the document, no antecedent |
| §2.4.4 scope | p. 25 | **rewritten** — "license verbs", no object, most compressed form |
| §2.4.4 body | p. 26 | **kept** — names the verb in quotation marks, which is where the usage becomes concrete |
| Ch. 6 ×2, AI-disclosure appendix ×1 | — | kept — ordinary English with a concrete object |
| gradient-cosine appendix ×2 (`apx_f_cosine.tex`) | p. 98 | kept — same statistical sense, and each names what is licensed in its own sentence |
| data-ethics appendix ×5 (`apx_e_ethics.tex`) | p. 95 onward | untouched — unrelated sense (dataset licensing, Apache License 2.0) |

**Appendices are named by subject here, not by letter, because the filenames and the printed letters
do not correspond.** Measured in the rendered 101-page defense build, the main volume prints exactly
three appendix headers: **A** (p. 91, Other Scientific Contributions), **C** (p. 95, Data Ethics and
Governance) and **D** (p. 98, Why the Two Tasks Do Not Compete on the Shared Trunk). So
`apx_f_cosine.tex` prints as **Appendix D** — phase 0 relettered it F → D — `apx_e_ethics.tex` prints
as **C**, and `apx_d_ceiling.tex` is in the supplementary volume entirely. A letter inferred from a
filename is wrong in this tree, in both directions.

The buckets sum to 13: **eight verb-sense** occurrences (2 rewritten, 6 kept) and **five**
dataset-licensing. Re-measured after the rewrites: 11 remain, 6 verb-sense and 5 dataset.

New wording, p. 24: "…and the statistical tests that decide which verb a comparison may be reported
with." p. 25: "…so the tests set out below govern the comparison verbs of Chapter 5 alone."

**The term is legitimate and is not banned** — a test does license a verb, and `AGENT_GUARDRAILS` §4b
uses that framing. The advisor's objection is about a reader meeting it cold, and it holds at exactly
those two sites. Rewriting the p. 26 sentence would have removed the definition rather than the
opacity.

---

## 5.6b · The Gowalla window, and the resolved sign-off markers

> **AUTHOR:** "Vamos usar só as datas que encontramos no database de 2009 a 2011, pode omitir que no
> artigo eles comentam que é de 2009 a 20010. O need sing-off assim como os demais já resolvidos que
> estão no latex pode ser removidos não precisam fica lá. Se quider documentar isso tem que ser em
> algum lugar do src_util."

**Both halves applied.**

**One window, the measured one.** `6_conclusion.tex`, rendered p. 81:

> "**Data vintage.** The five state datasets come from Gowalla [17]. The extraction used here spans
> January 2009 to August 2011 across the five states; mobility patterns, place inventories, and
> check-in behavior have changed since."

The clause reporting the paper's own window (February 2009 to October 2010) is removed; the citation
stays on the dataset, which is what it is for. The measurement that produced the printed span is
preserved in full in the provenance comment: five parquet files, per-state ranges, union
2009-01-21 to 2011-08-16, with the command that reads them. **The paper's stated window is recorded
here rather than lost**, per the second half of your instruction: Cho, Myers and Leskovec report
collecting public check-ins between February 2009 and October 2010 (KDD 2011, DOI
`10.1145/2020408.2020579`, §2 p. 2).

**Markers: 56 → 54.** A full catalogue was built by walking each bracketed marker across its wrapped
comment lines. Two were removed, and each is named with why it is settled:

1. `6_conclusion.tex` — the 5.6b marker itself. It asked which window to print and named the cut ("If
   he prefers only the paper's window, the clause after the comma is the one to cut"). You chose the
   other direction, so the clause that came out is the paper's. **Nothing left to decide.**
2. `apx_b_errata.tex` — the 2.7 marker. Item 2.7 is archived as closed ("FECHADO como não-recuperável")
   and the sentence it guards was added on your own quoted instruction. It **recorded an executed
   decision rather than asking one**.

**One marker in the same family was deliberately KEPT:** `6_conclusion.tex:324`, also tagged 5.6. Its
question is live and unanswered — it reports that your premise "ambos usaram o mesmo recorte" does not
match the repository's measurement, since Chapter 5's pipeline reads a 36-million-check-in figshare dump
while Chapter 4 prints the SNAP collection window. That is a fact about your own runs, so it stays until
you settle it. Removing it because it shares a number with a settled item would have been the wrong
reading of "os demais já resolvidos".

---

## 2.23 · The four approved RECOMMENDED

> **AUTHOR:** "Aplique o R-3,5,6 e o EX-6, seguindo a recomendação do 42_excellence, não aplique o EX-9."

**R-5 — the 66-word guarantees sentence.** Split at the first semicolon, the fix the report prescribes.
Sentence one keeps Nash-MTL with its two-part claim; sentence two takes CAGrad and Aligned-MTL, which
are genuinely parallel. Rendered p. 23: "…that a deep network does not satisfy [47]. The fixed points of
CAGrad are Pareto-stationary [48], and Aligned-MTL converges to such a point for task weights fixed in
advance [49]." No content moved and no citation changed.

**R-3 — §2.3 opens a thread §2.5 does not close.** One clause added after "fixed-weight baseline",
rendered p. 26:

> "For the task pair studied here the reason is measurable: the two tasks' gradients are close to
> orthogonal on the shared parameters, so there was little for a balancer to correct."

No new claim; it restates p. 23 in the section built to restate. The report offered a
replace-rather-than-add variant on the strength of a prior pass's SF-10; **add** was chosen because the
sentences SF-10 names carry the "measured against the dedicated model" convention the honesty rules
require, and cutting one to fit a clause would trade a rule for a rhythm. Cost: three lines of a
532-word section.

**R-6 — Appendix D reachable from one sentence.** Half was already in place: a prior round's EX-3 landed
the Chapter 6 pointer R-6 asks for (p. 80, "Appendix D reports the same quantity on the final model over
seven datasets"). The half R-6 closed as unavailable — the Chapter 5 site — is now applied under your
2.9 permission. See §2.9. **Note the letter:** both reports say "Appendix F"; phase 0 relettered it **D**,
and the references are by label, so they render correctly.

**EX-6 — the sentence the appendix's own table contradicts.** Applied following `42_excellence`, as you
instructed where the two reports disagree. Rendered p. 101:

> "Equivalence holds at both ends: the result is not a quirk of Florida, and it is not an artifact of
> small data."

The dropped clause claimed "the two largest states behave like the two smallest". Ascending by
check-ins the states run AL 113,846 · AZ 236,450 · FL 1,407,034 · CA 3,171,380 · TX 4,089,892, so the
two smallest are Alabama and Arizona — and **Alabama carries the largest mean in the table, +0.0112**,
with five of five positive folds, while Texas and California sit at −0.0003 and +0.0007 with mixed
folds. All are equivalent to zero, which is the claim that matters; they do not "behave like" each other
in the sense a reader will check against the table on the same page. Nothing is hidden: the two datasets
with a positive tendency are reported two pages earlier.

**EX-9 — NOT applied**, per your instruction.

---

## The introduction, and why it is not in this report's changes

You asked a scope question about `1_introduction.tex` and then instructed a revert. Both are done.

**The edit was not mine.** Measured: the file's mtime was 18:17:17, after my only build (18:01:33), and
I had written no `.tex` file at that point. Two other artifacts written in the same window —
`build/main_ppgc.pdf` and the `src_utils/_fixtures/**` self-test harness — correspond to targets I never
invoked, which places a second writer in this checkout.

**It was also outside 2.11's scope**, measured: the file already pairs its region claim with the TOST
caveat at `:142`, and has since `70e794f1`. All three of its region-comparative sentences carry it.

**Reverted, and verified by the three checks you named:**

| check | result |
|---|---|
| `grep -c 'records that user'` | **1** |
| `git diff --stat` on the file | **empty** |
| `make defense` | **rc=0**, 101 pp, 0 TeX errors |

The `scale,and` typo is gone (0 occurrences) and the file's `\emph`/`\textit` convention is restored
(0 `\textit`, as at HEAD). **Both versions are preserved** at
`_UNCOMMITTED_1_introduction_1817.{diff,tex.bak}` (the 161-line state) and
`_UNCOMMITTED_1_introduction_final.{diff,tex.bak}` (the 163-line state), so nothing was destroyed.

**One thing worth your attention.** The revert restores the FAB-12 plural, "a check-in records that
users visited a given place", where a singular record takes a plural subject. `42_excellence_r9b.md` §3
item 8 already flagged that construction and noted it is the advisor's call, not a defect. It is back in
the document, as instructed.

---

## Self-audit: four defects I introduced and caught

Recorded because a track that hides its own errors is worse than one that makes them.

**Comment blocks absorbing live prose — four instances.** A provenance comment ending without a newline
before the following prose comments out that prose: it builds clean and the reader silently loses a
sentence. Found by measuring live-prose word deltas per changed file rather than by reading my own
edits:

| file | sentence absorbed | how found |
|---|---|---|
| `4_courb/methodology.tex` | "Each walk is converted into a sequence of secondary categories…" | italic arithmetic off by 5 |
| `CoUrb_2026/src/sections/metodology.tex` ×2 | "O modelo aprende os embeddings…", "A perda total é…" | prose delta −31 words |
| `CoUrb_2026/src_en/sections/metodology.tex` ×2 | "The model learns the embeddings…", "The total loss is…" | prose delta −34 words |
| `2_fundamentals.tex` | "Comparisons there are made across the folds and repetitions…" | prose delta −4 words |
| `2_fundamentals.tex` | "Not every method claims even that much." | the torn-sentence gate |

All repaired. The prose-delta audit is now the check I would run again: for every changed file, diff
`live_text` at HEAD against `live_text` now and require that every removed word be intentional. Its
final state shows removals in 14 files, each traced to a specific ruling.

**A pipe hid an exit code — the trap this project has been burned by.** I read `get_rc=0` from
`git config … | cat -v`, which is `cat`'s status. Re-measured without the pipe: rc=1, the key is unset.

**A `printf` wrote a literal `%%`** so my cleanup `sed` never matched and a test line survived two
"restore" steps. Caught by reading the gate's output rather than trusting the restore; the file was then
restored with `git checkout` and verified clean.

---

## Gates and builds

**Builds, exit codes read directly, after all edits:**

| target | rc | pages | TeX errors |
|---|---:|---:|---:|
| `defense` | 0 | 101 | 0 |
| `academico` | 0 | 98 | 0 |
| `ppgc` | 0 | 102 | 0 |
| `extra` | 0 | 22 | 0 |

`extra` grew 20 → 22 pages: the errata tables gained six rows.

**`count_errata_rows.py` rc=0**, at B.1 10 · B.2 14 · B.3 7 · B.4 19 · total 50, and Table B.5 at 3
counted separately. The gate failed loudly in between (rc=1, "measured 50 claimed 44") when the rows
landed before the count claim, which is the gate working.

**One gate was blind and is now fixed: `check_tracker_refs.py`.** It could not express a lettered
tracker item. `HEADING` required a word boundary after the second digit, and in `5.6b` the digit and
letter are both word characters, so the live heading `### 5.6b` was invisible; `CITE` stopped at the
digits, so three round-9c comments citing **your own item number** were reported as pointing at a
section that does not exist. The suffix is now part of the key on both sides, and the fix was validated
in both directions: citing `5.6b` (live) → rc=0; citing `5.6` (archived) → rc=1, so the behavior that
caught the 2.2 renumber is intact.

**Two `VERIFY_LIST` expectations were made false by the rulings and are updated**, each with the reason:
the `four of six` block moves 3 → 4 prose hits (Chapter 6's sentence now carries the partition), and the
`fclass` block moves from three occurrences to an empty dict.

---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
