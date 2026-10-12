# FACT_GATE_v2 — G2 fact gate on the corrected build (citations, numbers, claims, L4)

> 🛑 **GERACAO SUPERADA — nenhum numero deste ficheiro pode ser citado.**
>
> Isto e o fact gate G2, corrido em 26 de julho de 2026, **antes** de a geracao v18 fechar o vazamento de rotulo
> no grafo de visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 de categoria
> medidas aqui vem da geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta: as questoes ja
> encerradas estao la com a prova, e este ficheiro nao e fonte de nenhuma delas.


**Auditor:** Dissertation Fact Gate (personas 05 citation / 06 number / 07 claim-honesty, plus the
L4 cross-reference lint). Read-only: no file was edited, no build was run, no git command was
issued. Every finding below carries a verbatim quote, its location, and the source-of-truth path
it was traced to. Fresh eyes: no prior report was used as evidence; every number in the ledger was
re-derived from the committed sources this session.

**Build audited (as delivered):**

| Artifact | mtime | pages |
|---|---|---|
| `src/dissertacao.pdf` | 2026-07-25 23:43:53 | 94 |
| `src/build/main_final.pdf` | 2026-07-25 23:43:53 | 89 |
| `src/build/main.pdf` | 2026-07-25 23:42:43 | 94 |
| `src/build/main.bbl` | 2026-07-25 23:41:57 | 97 `\bibitem` |
| `src/references.bib` | 2026-07-25 23:22:10 | 99 `@entry` |

---

## VERDICT: **GATE FAIL**

One BLOCKER. The brief states the build has "0 errors, 0 undefined refs/cites." That statement does
not survive audit: **the bibliography was last processed before the Rußwurm key rename, so the
renamed key resolves nowhere in the current build.** Four citations render as `(??)` in both
delivered PDFs and the work is absent from the printed reference list. Everything else in scope —
numbers, verb–test binding, the changed bibliography entries, the L4 lint, the two named
internal-consistency risks — passes, with three MODERATE and four MINOR items below.

The blocker is a **build-state defect, not a source defect**: `references.bib` and all four citing
sites are internally correct and consistent. It is fixed by re-running BibTeX and two more LaTeX
passes; no prose change is required.

---

## BLOCKER

### B-1 · The renamed Rußwurm key resolves in the source but not in the build; four citations render `(??)` and the reference is missing from the printed bibliography

**What the reader sees.** Verbatim, from the rendered PDF text layer:

> "A related encoder uses spherical harmonics together with sinusoidal representation networks,
> again to honor the spherical domain that flat sine-and-cosine features distort **(??)**."
> — `src/dissertacao.pdf` p. 21 (= `build/main_final.pdf` p. 16)

Four sites in both delivered PDFs:

| PDF | page | context |
|---|---|---|
| `dissertacao.pdf` | 21 | "...flat sine-and-cosine features distort **(??)**." |
| `dissertacao.pdf` | 45 | "The SIREN methodology (Sinusoidal Representation Networks) (36), applied to the geographic context **(??)**, models contin..." |
| `dissertacao.pdf` | 49 | "...distinct spatial encoding paradigms: SIREN **(??)**, which models..." |
| `dissertacao.pdf` | 50 | "4.3.3.1 SIREN The SIREN model (Sinusoidal Representation Networks) **(??)** models a conti..." |
| `main_final.pdf` | 16, 40, 44, 45 | the same four |

**Diagnosis, traced.** The rename went through in the source; the bibliography was compiled before it.

- `src/references.bib:` the entry key is ASCII — `@inproceedings{russwurm2024geographiclocationencodingspherical,`
- all four citing sites use the ASCII key: `2_fundamentals.tex:211`, `4_courb.tex:65`, `4_courb.tex:129`, `4_courb.tex:148`
- the current build's `.aux` files carry the ASCII key: `\citation{russwurm2024geographiclocationencodingspherical}`
- but `build/main.bbl` contains **no** matching `\bibitem`; its 97 entries include no `wurm` key.

**The build ordering that produced this, from the mtimes.** `references.bib` and the four citing
`.tex` files were corrected at 23:22-23:23. BibTeX then ran at **23:41:57**, but BibTeX reads
citation keys from the `.aux`, and at that moment the `.aux` still held the *pre-rename* key from
an earlier LaTeX pass. BibTeX looked up `rußwurm...`, found nothing in the corrected `.bib`
(which now spells the key `russwurm...`), logged its one error, and emitted 97 entries. LaTeX then
ran at **23:42:43** and wrote a *new* `.aux` carrying the correct ASCII key, but BibTeX was never
re-run against it. The `.bbl` therefore answers a question the document no longer asks, and the four
ASCII citations have nothing to resolve against. The sequence is one BibTeX pass short, not one
edit short.
- `build/main.blg` and `build/main_final.blg` both record, verbatim:
  > `Warning--I didn't find a database entry for "rußwurm2024geographiclocationencodingspherical"`
  > `(There was 1 error message)`
- `build/main.log` records, verbatim:
  > `LaTeX Warning: Citation 'russwurm2024geographiclocationencodingspherical' on page 20 undefined on input line 211.`
  and `main_final.log` ends with `LaTeX Warning: There were undefined references.`
- the stale copy at `src/main.bbl` (mtime 2026-07-25 **15:38**, i.e. the pre-rename build) still
  carries the old non-ASCII key: `\bibitem{rußwurm2024geographiclocationencodingspherical}`. That
  is the whole of the 98-vs-97 `\bibitem` count difference the brief asks about.

**Count relationship requested by the brief (item 3), computed:**

| quantity | value |
|---|---|
| `@entry` in `src/references.bib` | 99 |
| distinct `\cite` keys across all `.tex` | 98 |
| `\bibitem` in `build/main.bbl` (current build) | 97 |
| `\bibitem` in `build/main_final.bbl` | 97 |
| `\bibitem` in `src/main.bbl` (STALE, pre-rename) | 98 |
| printed numbered entries in the PDF reference list | 97 (max marker 97) |

99 − 98 = 1 **orphan** (see M-1). 98 − 97 = 1 **cited-but-unresolved** (this blocker).

**Correction needed.** Re-run BibTeX against the current `.aux` and re-run LaTeX twice, for both
targets. Then confirm: zero `(??)` in the text layer, 98 `\bibitem` in `build/main.bbl`, and
"RUßWURM, M. et al." present in the printed reference list. The stale `src/main.bbl` should be
removed or regenerated so it cannot be mistaken for the build's bibliography.

**Not a defect (verified, so the fix is mechanical):** the entry itself is correct and its erratum
claim is true. Verified against two sources of record opened this session — arXiv API id
`2310.06743` returns `<arxiv:journal_ref>` "Published as a conference paper at ICLR 2024", entry
title "Geographic Location Encoding with Spherical Harmonics and Sinusoidal Representation
Networks", authors Rußwurm / Klemmer / Rolf / Zbinden / Tuia (five, matching the entry exactly);
and the OpenReview venue record for `PudduufFLa` (ICLR 2024). Appendix B's row describing this
correction (`apx_b_errata.tex:452-455`) is accurate as written.

---

## MAJOR

*(none)*

---

## MODERATE

### D-1 · The one hard-coded numeric cross-reference in the document is an equation pointer into an external paper, unguarded by `\ref`

**Quote** (`src/chapters/2_fundamentals.tex:170`):

> "the cross-region edge weight of their **Equation 2**, set to 0.4 for the dense Chinese cities
> they study, was raised to 0.7 for the sparser United States state datasets used here"

**Status.** This is the *only* hard-coded `Chapter/Section/Table/Figure/Equation N` pointer in the
whole document; every other cross-reference goes through `\ref` (98 labels, 64 reference sites,
zero dangling, zero duplicates — see the L4 section). The pointer is *correct*: it names Eq. 2 of
Huang et al. (2023), not an internal target, and `research/embeddings/hgi/README.md:539` confirms
"(Eq. 2 of Huang et al., ISPRS 2023)". It cannot break under renumbering because it is external.

**Why MODERATE rather than NIT.** A numeral written as prose is invisible to the lint that would
catch it if the antecedent ever changed, and a reader scanning for internal pointers may mis-read
it as one. **Correction (optional, author's call):** make the external ownership explicit —
"Equation 2 of Huang et al." — so no reader or future lint mistakes it for an internal reference.

### D-2 · The `w_r` = 0.7 claim in Ch. 2 is stated for "the sparser United States state datasets" (plural), but the committed per-state table assigns 0.6 to two of the five states

**Quote** (`src/chapters/2_fundamentals.tex:170-171`):

> "was raised to **0.7 for the sparser United States state datasets used here**"

**Sources of truth traced.**

- `research/embeddings/hgi/preprocess.py:23` — `DEFAULT_CROSS_REGION_WEIGHT = 0.7`
- `pipelines/embedding/hgi.pipe.py:60` — `cross_region_weight=0.7` in the shipped `CONFIG`, and
  every state entry in the `STATES` dict (`hgi.pipe.py:73-77`, all five Gowalla states) carries
  `'cross_region_weight': 0.7`
- **but** `research/embeddings/hgi/README.md:574-580`, the "Current per-state defaults" table,
  gives: Arizona 0.7, Alabama **0.7 (swept)**, Texas 0.7, **California 0.6 (interpolated)**,
  **Florida 0.6 (interpolated)**

**Adjudication.** The two sources disagree, and the *executable* one supports the sentence: the
pipeline's per-state dict pins 0.7 at all five states, the README's 0.6 rows are labeled
"interpolated" (i.e. proposed, not run), and the `CROSS_REGION_WEIGHT_PER_STATE` override dict the
README points to **does not exist** in `hgi.pipe.py` (`grep -c` returns 0; the only repo mention is
a log string in `scripts/run_wr_sweep.py:403`). The prose is therefore defensible as it stands.

**Correction needed.** None to the claim. Flagging it so the author knows the README table is stale
relative to the pipeline and will contradict the sentence if a reader opens it.

### D-3 · Chapter 5's Markov-floor margin ("$4.9$ to $10.3$") is one hundredth below the source's stated range ("+4.9 to +10.4")

**Quote** (`src/chapters/5_mobiwac.tex:701-703`, reproduced verbatim from the version of record
`articles/[mobiwac]/src/sections/06_results.tex:106-108`):

> "reaches $51$ to $72$ Acc@10 across the datasets; the joint model exceeds it by **$4.9$ to
> $10.3$** points on all six datasets."

**Source of truth** — `docs/studies/closing_data/MARKOV_FLOOR_STRIDE1.md:72`:

> "The joint model still clears the protocol-matched floor at **all six datasets**, by **+4.9 to
> +10.4 points**"

and its per-dataset table (`:62-69`) gives the largest margin as Istanbul **+10.38** against the
diagnostic-best joint cell 75.44. Reading the same table against the **joint-best** Istanbul cell
printed in Table 3 (75.35) gives 75.35 − 65.06 = 10.29, which rounds to 10.3 — so the chapter's
figure is the joint-best-consistent one and the source's 10.4 is the diag-best one. The lower
bound (4.9, Florida +4.95) agrees under both.

**Why this is MODERATE and not a number error.** The chapter is a verbatim reproduction of the
submitted manuscript; under the reproduce-not-recompute rule (`NORTH_STAR §4`, reviewers/README
"Ch.5 … reproduce, never recompute") the printed value is *correct as reproduced*. But the
10.3-vs-10.4 gap is exactly the joint-best/diag-best seam that N5 governs, and no committed file
states "10.3" — the number is one rounding step away from any source line.

**Correction needed.** Either (a) leave it and add a hidden-comment ledger line naming the
derivation (75.35 − 65.06 on the joint-best basis, `MARKOV_FLOOR_STRIDE1.md:64` + Table 3), or (b)
add it to Appendix B as a reproduced-value note. Do **not** silently change the digit: it is the
manuscript's own text.

---

## MINOR

### N-1 · One bibliography entry is present and never cited (orphan)

`liu2014geographical` appears in `src/references.bib` and in **no** `\cite` in any `.tex`. It is
excluded from `main.bbl` correctly (BibTeX only emits cited entries), so nothing renders wrong.
This is the deliberate residue of the erratum recorded at `apx_b_errata.tex:496-501`: the CoUrb
chapter's Gowalla citation was moved off that paper onto `cho2011gowalla` + `jure2014snap`.
**Correction:** delete the entry, or keep it and note in Appendix B that it is retained
un-cited for provenance. Either is defensible; silence is not, since 99 − 98 = 1 is otherwise
unexplained.

### N-2 · Three bibliography numbers never appear as a standalone in-text marker

Printed entries 9 (`lipton2015learning`), 57 (`vandenhende2022mtl`) and 75 (`zhang2021survey`)
never appear as a bare `(n)` marker. All three are **not** defects: they render inside grouped
markers — verified on the page, e.g. `dissertacao.pdf` p. 13 "…recurrent models that diagnose over
a hundred clinical conditions simultaneously **(9)**…" (the extraction missed it because the
marker abuts the sentence), and p. 60-ish "(57, 58)" and "(58, 75)". Recorded only so the count
audit is complete.

### N-3 · Ch. 5 prints "$0.3$" for the freeze-control agreement without a unit

`5_mobiwac.tex:668`: "…which it **matched to within $0.3$**, and not to the joint cells reported
here." The neighbouring values are macro-F1 points; `W6_ENCODER_ISOLATION.md:29` states "Δ ≤ 0.3 pp".
**Correction:** write "$0.3$ macro-F1 points" (or "pp") so the numeral carries its unit per N5.

### N-4 · The capacity-matched study's recipe-grid asymmetry does not travel with its numbers

`capacity_matched_stl_cat/README.md` states, in the same paragraph as the verdict:

> "the asymmetry remains and must travel with the number: the ceiling was tuned best-vs-best over a
> wider recipe grid than the 3-recipe (AL) / 2-recipe (CA) sweeps here."

Ch. 6 carries the scope caveat that *is* mandated ("two of the six datasets, one width point per
dataset, and width scaling rather than depth", `6_conclusion.tex:187-188`) and it carries the
fairness point in the favourable direction (`:116-119`, the lower learning rate). It does **not**
carry the grid asymmetry. **Correction:** add the asymmetry to the limitation at `:185-188`, or
record in the handoff why the author judged it subsumed.

---

## SECTION 1 · NUMBERS (AGENT_GUARDRAILS §2, N1–N5) — re-derived independently

### 1.1 Chapter 6 capacity-matched figures — **ALL CLEAR**

Every figure in `6_conclusion.tex:96-119` was matched against
`docs/results/closing_data/capacity_matched_stl_cat/README.md` and `capacity_matched_summary.json`.
Full trace in the ledger below. Highlights the brief asked for by name:

- **California figures.** "a hidden dimension of **752** and **101.9** percent of the joint model's
  parameter count … reaches **69.88** macro-F1, standard deviation **0.26** over its twenty fitted
  models, against **70.60**, standard deviation **0.07**" — every one of these is a quoted cell.
  `README.md:29` gives `hidden_dim=752` / `5,249,719 (101.9%)`; the JSON's
  `results.california_h752.bs8192_lr0.0025` gives `mean 69.8789`, `std 0.2645`, `n 20`;
  `reference_points_diag_best.california` gives `dedicated_ceiling_h256 70.6`, `ceiling_std 0.07`.
- **Matched width.** 752 (CA) and 672 (AL) both in `README.md:28-29`; Ch. 6 quotes only 752, which
  is the value its sentence needs.
- **Spreads.** 0.26 and 0.07 both quoted; neither is computed.
- **Alabama.** "**56.16** macro-F1, against **56.82** … and **64.51** for the joint model" —
  56.16 = `alabama_h672.bs2048_lr0.0025.mean 56.1611` (the best arm, and the chapter says "the best
  of them"); 56.82 = `reference_points_diag_best.alabama.dedicated_ceiling_h256`; 64.51 is the
  **joint-best** cell of Ch. 5 Table 3 (`5_mobiwac.tex:574`), confirmed by
  `JOINT_BEST_RESULTS.md` and independently by the reproduction gate in
  `stats_n20/m2_prereg_output.txt`: "[OK] AL MTL cat (joint-best n=20): recomputed 64.5051 vs board 64.51".
- **The two shortfalls, "0.72 points below at California and 0.66 at Alabama"** — these are the
  README's own bolded cells (`README.md:46-47`: "56.16 ±1.89 (**−0.66**)" and "69.88 ±0.26
  (**−0.72**)"), also `capacity_matched_summary.json.verdict`. **Not computed in prose.**
- **N2 compliance (the brief's specific question).** No delta is computed in Ch. 6 prose. Every
  difference that appears (−0.66, −0.72) is quoted from the README. The two deltas that a reader
  could compute (+8.35 against the capacity arm, +7.69 against the ceiling) appear **only inside a
  hidden comment** at `6_conclusion.tex:106-107`, never in prose. **PASS.**
- **Interim-value hygiene.** The retired partial-California read **68.35** appears nowhere in the
  document (0 hits across all `.tex`). The replacement is recorded at `6_conclusion.tex:120-125`.
  **PASS.**

### 1.2 Chapter 5 leak-audit values — **ALL CLEAR**

`5_mobiwac.tex:367`, fourth ground, checked digit-for-digit against the CSVs:

| printed | CSV | file | row |
|---|---|---|---|
| $0.4090$ | 0.4089797540123382 | `leak_sniff_fl.csv` | `check2hgi_gcn_ctrl` perstep |
| $0.4074$ | 0.40744232906432776 | `leak_sniff_fl.csv` | `check2hgi_gcn_ctrl` perstep_raw |
| $0.4197$ | 0.4196859144977155 | `leak_sniff_resln_fl.csv` | `check2hgi_resln` perstep |
| $0.4182$ | 0.41815720719390814 | `leak_sniff_resln_fl.csv` | `check2hgi_resln` perstep_raw |
| $0.4976$ | 0.49761650037538024 | `leak_sniff_fl.csv` | `check2hgi_gat` perstep (verdict **LEAK**) |
| $0.4863$ | 0.48631035868799294 | `leak_sniff_fl.csv` | `check2hgi_gat` perstep_raw |
| "about $0.41$" ceiling | "clean control ceiling (~0.41)" | `RESCREEN.md` | the per-step gate |

The three stated limits are the audit's own residuals and each is verifiable: linear probe
(`scripts/embedding_eval/leak_sniff.py:59` — `f1_score(..., average="macro")` over
`GroupKFold`), Florida at one initialization over five folds, and the ancestor GCN/ResLN lineage
rather than the shipped build. The disqualification of the attention encoder on the basis of
exceeding the ceiling matches the CSV `verdict` column. The chapter's own caution — "The
measurement bounds this channel rather than closing it" and "one encoder that passed it leaked
under a downstream sequence model" — is supported by `RESCREEN.md` (R-GCN passed per-step and
leaked at L2). **The rewrite from an absolute to four bounded channels is correctly grounded.**

The **second** ground's numbers were traced too: "region $-0.33$ to $+0.01$; category $0.00$ to
$+0.29$" and "67 to 87 percent" all appear in `docs/studies/pre_freeze_gates/A4_RESULTS.md:61-63`
(AL −0.33 / +0.29 @ 66.8%; AZ +0.01 / +0.27 @ 71.9%; FL −0.12 / +0.00 @ 86.9%). The **third**
ground's "13 to 27 points" traces to `docs/context/DATA_SPLITS.md:58` ("leak-inflated by 13–27 pp
on FL-style states") and `research/evaluation_protocol_review.md:39`.

### 1.3 Freeze-control numbers — **ALL CLEAR, and N5 is satisfied**

This was flagged as the highest-risk N5 site. It is clean, and the rewrite is the reason.

`5_mobiwac.tex:659-668` against `W6_ENCODER_ISOLATION.md §2` (the table at `:20-24`):

| printed | W6 column | value |
|---|---|---|
| $63.50$, $63.67$, $79.79$ | "probe cat (freeze-reg)" | 63.50 / 63.67 / 79.79 |
| $+7.63$, $+6.54$, $+4.64$ | "Δ vs ceiling" | +7.63 / +6.54 / +4.64 |
| $63.56$, $63.39$, $79.82$ | "full-MTL cat (§1)" | 63.56 / 63.39 / 79.82 |
| "within $0.3$" | "Δ ≤ 0.3 pp" (§2 reading) | ≤ 0.3 |

**N5 adjudication.** W6 measures its +7.63/+6.54/+4.64 against **STL cat ceiling AL 55.87 / AZ
57.13 / FL 75.15** — which are exactly the *check-in-level* column cells of Ch. 5 **Table 2**
(`5_mobiwac.tex:448-450`), not the per-dataset-tuned n=20 Dedicated cells of **Table 3** (56.82 /
56.43 / 74.51). The rewritten prose points the deltas at **Table 2 by name**
(`\ref{tab:mobiwac:representation}` at `:662`), so an examiner subtracting on the page gets the
printed value. And the "within 0.3" is explicitly bound to "the joint scores of the **development
configuration current at the time** ($63.56$, $63.39$, $79.82$) … **and not to the joint cells
reported here**". **The two conventions are named and separated inside the comparison. N5 PASS.**

The single-seed footing is declared in prose ("measured at **one random initialization over five
folds**"), matching `W6_ENCODER_ISOLATION.md:54` ("**n=5 provisional** (seed 0)"). The 2026-07-01
dropout caveat at `W6:64` is **not** surfaced in prose; W6 itself records the directional
conclusions as standing, so this is a defensible omission, recorded here for the author.

### 1.4 Chapter 2 HGI retuning values — **ALL CLEAR; the [VERIFY] hedge is CORRECT AS WRITTEN, but the convention CAN now be established**

**The values.** `2_fundamentals.tex:170-173`: "0.4 … raised to 0.7 … rose monotonically from
**0.74 to 0.82** across the swept values."

- 0.4 → `research/embeddings/hgi/README.md:548`, `Cat F1 0.7388 ± 0.0205` → 0.74 ✓
- 0.7 → `README.md:551`, `Cat F1 0.8186 ± 0.0123` → 0.82 ✓
- monotonic → `README.md:548-551`: 0.7388 → 0.7678 → 0.7944 → 0.8186 across w_r 0.4/0.5/0.6/0.7 ✓
- "over five folds" → `README.md:544` "(5 folds × 50 epochs)" ✓
- 0.4 as the paper's value → `README.md:541`, `preprocess.py:36`, and the Ch. 2 comment records it
  verified firsthand in the HGI PDF Eq. 2 ✓

**The adjudication the brief asks for.** The editing agent's hedge — writing "category F1" rather
than "macro-F1" because "the sources record 'Cat F1' without naming the averaging convention" — is
**a correct and conservative reading of the two files it cites** (`hgi/CLAUDE.md:117` and
`README.md:544-551` do indeed say only "Cat F1"). But the convention **can** be established from
committed files, by following the metric backwards:

1. `scripts/run_wr_sweep.py:139-142` — `def read_cat_f1(summary)` returns
   `summary["category"]["f1"]["mean"/"std"]` from a `full_summary.json`.
2. `src/tracking/storage.py:120,136` writes that `full_summary.json` from the keys produced by
   `compute_classification_metrics`.
3. `src/tracking/metrics.py:299` — `_key("f1"): f1_macro`, where `f1_macro` is
   `multiclass_f1_score(..., average="macro", zero_division=0)` (`:283-285`); the weighted variant
   is a **separate** key, `_key("f1_weighted")` (`:300`, `:286-288`).
4. The module docstring states it outright (`metrics.py:10,19-21`): "``accuracy`` (micro) and
   ``f1`` (macro)"; "The ``'f1'`` key stays identical to the previous
   ``multiclass_f1_score(..., average='macro')`` value".
5. A committed `full_summary.json` confirms the shape (`category`/`f1`/`mean`, alongside a
   distinct `f1_weighted`).

The chain is complete and there is only one F1 path in `src/`. **The swept "Cat F1" is macro-F1.**

**Correction needed.** The hedge is not *wrong*, but it is now unnecessary and it costs precision:
"category F1" is not a canonical GLOSSARY term while "macro-F1" is, and the surrounding chapter
(§2.4) defines macro-F1 as *the* category metric. Recommended: change "the category F1 on Alabama"
to "the macro-F1 on Alabama" and replace the `[VERIFY]` comment with the five-step trace above
(`run_wr_sweep.py:139-142` → `storage.py:120` → `metrics.py:283-285,299`). **The author's ruling is
required either way; the gate does not rule on prose.** If the author prefers maximum caution, the
current wording may stand — it asserts nothing false.

### 1.5 N5 sweep across the document — **ALL CLEAR**

Every joint-vs-dedicated comparison was checked for convention mixing.

- Ch. 5 Table 3 joint cells are **joint-best**, disclosed at `5_mobiwac.tex:499-504` and confirmed
  cell-for-cell against `JOINT_BEST_RESULTS.md` ("joint-best (deploy)" column: Ist 63.32/75.35, AL
  64.51/69.70, AZ 65.79/59.46, FL 79.84/77.41, TX 77.24/67.06, CA 77.05/65.69) and against the
  24/24 reproduction gate in `stats_n20/m2_prereg_output.txt`.
- The diag-best alternative is disclosed as a robustness bound in the same sentence, quoted from
  the source: "at most $0.06$ (category) and $0.11$ (region)" = `JOINT_BEST_RESULTS.md` "≤ 0.06 pp
  (category) and ≤ 0.11 pp (region)". No mixing.
- Ch. 6's capacity paragraph quotes **64.51** (joint-best), matching Table 3, with the basis switch
  recorded and justified in the hidden comment at `:103-108`. The source README anticipates exactly
  this ("Chapter 6 quotes the **joint-best** AL value (64.51) to match Chapter 5's Table 3").
- The freeze-control site: see §1.3 — separated and named.
- Ch. 6's headline "5.3 to 9.4" and Ch. 5's "$+5.33$ to $+9.35$" are both joint-best
  (`JOINT_BEST_RESULTS.md:65`: "**beats at all six** (+5.33 … +9.35)").

### 1.6 Never-cite sweep — **ALL CLEAR**

Retired and proscribed values swept across all `.tex` (`reviewers/README.md:106-107`;
`AGENT_GUARDRAILS` C3): STAN v4-collapse (34.46, 38.96) **0 hits**; HMT-GRN AL outlier (62.37) **0
hits**; ReHDM v2 row (66.06, 65.68) **0 hits**; interim California 68.35 **0 hits**; AZ ceiling
top-up 57.0 **0 hits**; diag-best AL joint 64.54 **0 hits in prose** (present only in the hidden
comment that explains why it was replaced). The one apparent hit, `54.65`, is Ch. 5 Table 2's
Istanbul check-in-level cell (`5_mobiwac.tex:447`), verified as legitimate against
`articles/[mobiwac]/src/tables/tbl2_substrate.tex` — coincidental digit match with a retired
ReHDM v2 cell, not the proscribed value. The ReHDM row that **is** printed (Ist 69.33 / AL 65.38 /
AZ 53.00 / FL 64.49 / TX 48.81 / CA 50.26) is the **v4** row, confirmed as such in the version of
record's table comment (`tbl3_results.tex:18-19`) which also names the v2 row as the excluded one
(`:27`).

### 1.7 Orphan-numeral audit (N4) — **ALL CLEAR**

Every prose numeral in Ch. 2 (10 values), Ch. 5 (160 values, tables excluded), and Ch. 6 (28
values) was extracted and matched to a source. No orphans. Cross-file numeral tally: 72 decimal
values appear in more than one file; every cross-chapter repeat agrees. Two apparent collisions
were inspected and are coincidental table cells in the reproduced CBIC chapter, not cross-chapter
claims: `56.82` at `3_cbic.tex:333` (a Shopping-row cell) and `0.82` at `3_cbic.tex:325` (a
standard deviation).

---

## SECTION 2 · CLAIMS (AGENT_GUARDRAILS §3, C1–C4; WRITING_LAW §3) — verb–test binding

**Result: ALL CLEAR. No overcorrection found, and no upgrade found.**

Every "outperform*", "matches", "non-inferior", "supera", "equipara" site in the frame chapters
(0_main, 1, 2, 5, 6, apx A, apx B) was read in full-sentence context and matched to the test that
licenses it.

**The law is stated in the document itself** (`2_fundamentals.tex:507-510`, verbatim):

> "Wherever this dissertation reports a test, the verb and the test are bound together:
> ``outperforms'' follows only from a paired superiority test, and ``matches'' only from a
> non-inferiority test within the stated margin."

**The evidence base**, re-derived from `stats_n20/m2_prereg_output.txt` (the registered per-fold
n=20 Wilcoxon, run at all six datasets) and `STATISTICAL_PROTOCOL.md:288-292` (the joint-best CIs):

| dataset | category | region |
|---|---|---|
| AL | +7.690, 20/20, Holm 5.72e-06 → **outperforms** | −0.41 (CI −0.63…−0.20) ⊂ ±2 → **matches (TOST)** |
| AZ | +9.350, 20/20, Holm 5.72e-06 → **outperforms** | 0.00 (CI −0.08…+0.07) → **matches (TOST)** |
| FL | +5.332, 20/20 → **outperforms** | +0.712, 20/20, Holm 3.81e-06 → **outperforms** |
| TX | +7.446, 20/20 → **outperforms** | +2.112, 20/20 → **outperforms** |
| CA | +6.442, 20/20 → **outperforms** | +2.201, 20/20 → **outperforms** |
| Istanbul | +8.584, 20/20 → **outperforms** | +0.194, 20/20 → **outperforms** |

**Checks that passed:**

1. **Arizona is never upgraded.** Every AZ region statement is a match. `5_mobiwac.tex:648`:
   "At Arizona, the interval is centered on zero, so **we report a match, not a gain**." The source
   carries the same instruction verbatim (`m2_prereg_output.txt`: "Never upgrade AZ";
   `stats_n20/RESULTS.md:88`: "do NOT upgrade to 'beats'"). **PASS.**
2. **Alabama's negative point estimate is stated honestly, not smoothed.** `5_mobiwac.tex:649-650`:
   "the whole interval lies below zero, **a small but statistically significant deficit**, still
   well within the two-point margin." This is the harder, more honest reading and it matches
   `RESULTS.md:87`. **PASS.**
3. **No overcorrection.** The brief asks specifically whether the newly-qualified sentences went
   *too* weak. They did not:
   - `6_conclusion.tex:88-89` "outperforms the dedicated models on the category task everywhere and
     **outperforms or matches** them on the region task" — exactly the disjunction the evidence
     supports (4 superiority + 2 TOST), neither over- nor under-stated.
   - `1_introduction.tex:254-255` "outperforming the dedicated models on the category task and
     **outperforming or remaining non-inferior** to them on the region task" — same shape. **PASS.**
   - `5_mobiwac.tex:653-654` reports FL and Istanbul as "outperforms there, **though both gains are
     smaller than the two-point margin**" — an honest qualification that does *not* retract the
     superiority verdict the test supports. **PASS.**
4. **The secondary/post-hoc status of next-region superiority is disclosed**, and correctly:
   `5_mobiwac.tex:394` "It assigned the tests per task, not per dataset, and **did not cover
   next-region superiority, so the four next-region gains … are secondary results outside it.**"
   This matches deviation entry **D-4** in `docs/studies/closing_data/log.md:479-487` exactly.
5. **The n=4 deviation is disclosed with its reason**: `5_mobiwac.tex:394` "at four seeds its exact
   one-sided $p$ cannot fall below $0.0625$, so we report a paired $t$ on the per-seed means …
   and the registered test alongside it" = deviations **D-1/D-2**, `log.md:450-465`. And the
   registered test *was* run: `5_mobiwac.tex:643-645` "The registered Wilcoxon test on the
   individual fold differences agrees at every dataset, with **all 20 folds** favoring the joint
   model (corrected $p<0.001$)" = **D-3**, `log.md:467-477`, and `m2_prereg_output.txt`
   (20/20 at every cell, worst Holm-adjusted 5.72e-06 < 0.001). **PASS.**
6. **Ch. 3 and Ch. 4 verbs are time-indexed and test-free.** `3_cbic.tex:21` "Its conclusions are
   the conclusions of the time, for the configuration studied here"; `4_courb.tex:13` "the
   conclusions reported here are those of the time, for that configuration". Ch. 2's scoping claim
   that these two chapters "report fold means and standard deviations and **run no significance
   test**" (`2_fundamentals.tex:494-495`) was verified by negative grep: `p-value|Wilcoxon|t-test|
   Holm|TOST` returns **one** hit across both chapters, and it is a hidden comment
   (`3_cbic.tex:379`), not prose. **PASS.**
7. **Banned-vocabulary sweep.** Zero em-dashes, zero contractions, zero repo codenames
   (`v11`–`v17`, `champion-G`, `dk_ovl`, `log_T`, `B9`, `H3-alt`), zero "beats/wins/ties/Pareto"
   as verdict verbs. "Frozen" survives at `6_conclusion.tex:93` ("with the region pathway frozen"),
   which `WRITING_LAW.md:60` permits only for frozen weights; see §4 below for the consistency
   reading. "Substrate" appears only inside a quoted paper title in Appendix A, which the file's
   own comment correctly identifies as a proper name.

---

## SECTION 3 · CITATIONS (AGENT_GUARDRAILS §1, R1–R5)

**100 percent of what changed this round: verified. R3 sample of unchanged entries: verified.**

### 3.1 The two changed entries

**Kohavi (`kohavi1995crossval`) — DOI dropped. VERIFIED, and the erratum's justification is true.**

Opened this session: the IJCAI-95 proceedings PDF at
`https://www.ijcai.org/Proceedings/95-2/Papers/016.pdf` (7 pages, 200 OK, `application/pdf`).

- Title page reads "A Study of Cross-Validation and Bootstrap for Accuracy Estimation and Model
  Selection", sole author **Ron Kohavi** — matches the entry.
- Running footers on the seven pages read 1137, 1138, 1139, 1140, 1141, 1142, **1143** — the entry's
  `pages = {1137--1143}` is exact.
- **No DOI string anywhere in the PDF text** (regex `10\.\d{4,9}/` returns zero matches) —
  consistent with "the IJCAI-95 proceedings predate DOI registration".
- **The cited claim was located in the source** (R1(c)): the paper's Summary recommends stratified
  ten-fold cross-validation for model selection.
- **The dropped DOI is what the erratum says it is.** DataCite record for
  `10.5281/zenodo.19712698`: same title, publisher Zenodo, publicationYear **2026**, creator
  "Kohavi, Ron". A 2026 third-party re-deposit, not the conference record — exactly as
  `apx_b_errata.tex:463-466` states. **The erratum row is accurate.**

**Rußwurm (`russwurm2024geographiclocationencodingspherical`) — re-typed to ICLR 2024, key
ASCII-ized. ENTRY VERIFIED; BUILD BROKEN (see B-1).**

- arXiv API `id_list=2310.06743`, opened this session: entry title "Geographic Location Encoding
  with Spherical Harmonics and Sinusoidal Representation Networks"; authors Marc Rußwurm,
  Konstantin Klemmer, Esther Rolf, Robin Zbinden, Devis Tuia (five, in order — matches the entry);
  `<arxiv:journal_ref>` "Published as a conference paper at ICLR 2024". **The re-typing to ICLR
  2024 is correct.**
- OpenReview record `PudduufFLa` corroborates the ICLR 2024 venue; the entry's `url` field points
  there.
- **Key resolution at every citing site:** the ASCII key is used at all four sites
  (`2_fundamentals.tex:211`, `4_courb.tex:65,129,148`) and matches `references.bib`. **Source-side:
  PASS.**
- **Printed bibliography contains the entry:** **NO.** This is B-1.

### 3.2 R3 sample of unchanged entries (≥20 percent required)

Fourteen entries checked against Crossref / arXiv / publisher this session; every field
(authors, venue, year, volume, pages) matched the `.bib` record. No mismatch found.

`silva2025mtlnet` (10.21528/CBIC2025-1191324) · `paiva2026stmtlnet` (10.5753/courb.2026.22960,
pages 323–336 confirmed) · `capanema2023poirgnn` (Ad Hoc Networks 138, 103016) ·
`chen2020modeling` (IEEE TKDE) · `zhang2021survey` (IEEE TKDE) · `misra2016cross`
(10.1109/CVPR.2016.433) · `song2010limits` (Science 327(5968):1018–1021) · `huang2023hgi` (ISPRS
J. 196:134–145) · `sokolova2009measures` (IPM 45(4):427–437) · `maninis2019attentive` (CVPR 2019,
1851–1860) · `gambs2012mmc` (MPM 2012, 1–6) · `wilcoxon1945` (Biometrics Bulletin 1(6)) ·
`lakens2017tost` (SPPS 8(4):355–362) · `Xu2023` (ACM TOIS 41(4)) · plus `caruana1997multitask`,
`lin2021ctle`, `Lim2022`, `luo2021stan`, `cho2011gowalla`, `li2025rehdm`.

Two harmless deviations recorded, neither a defect: Crossref renders `Xu2023` pages as "1-24"
where the entry uses the article number 112 with `numpages = {24}` (both are the publisher's own
forms), and `wilcoxon1945` returns first-page-only "80" where the entry gives "80--83" (the
standard full range).

### 3.3 R5 — AI output as source

No citation in the bibliography or in any chapter attributes a claim to a model or a model's
output. **PASS.**

---

## SECTION 4 · CROSS-REFERENCES (L4)

**Programmatic lint over all `.tex` in `src/chapters` plus `0_main.tex`:**

- 98 `\label`, 64 `\ref` target sites.
- **Duplicate labels: none.**
- **Dangling `\ref` (no matching label): none.**
- **Unresolved at render: none** — zero `[?]` in either PDF.
- Labels never referenced: 34 (section anchors and chapter labels used for navigation). Not
  defects.

**Every `\ref` site resolved against the current build's `.aux` and checked for kind agreement.**
Forty-two sites initially flagged as kind mismatches (e.g. "Table~\ref{tab:fund:lineage}" resolving
to "1", not "2.1") were all traced to the document's **continuous float numbering**, confirmed
against `build/main.lot` (Tables 1–15, unnumbered by chapter) and `build/main.lof` (Figures 1–7).
Not defects.

**The pointers the brief names, checked against what is actually there:**

- "**Section 5.6.2**" resolves to *One model, two tasks* — correct at all nine citing sites
  (verified against `main.toc`; rendered on pp. 7, 59, 61, 62, 67, 71).
- "**Chapter 5 does not rely on it**" (`3_cbic.tex:25-27`, the Nash pointer corrected this round):
  verified. Ch. 5 names Nash-MTL exactly once (`5_mobiwac.tex:183`) and only as a *cited example of
  a balancer that reports do not favour* — it is not used. And the correction was the right one:
  Ch. 4 **does** rely on it (`4_courb.tex:115` "Multi-task training uses the Nash-MTL regularizer"),
  so the earlier "the following chapters do not rely on it" would have been false. **PASS.**
- Appendix B's forward pointer to `\ref{tab:mobiwac:results}` (`apx_b_errata.tex:357`) resolves to
  Table 10 on p. 69. **PASS.**
- All chapter labels resolve to their expected numbers: `ch:fundamentals`→2, `ch:cbic`→3,
  `ch:courb`→4, `ch:mobiwac`→5, `ch:conclusion`→6, `apx:errata`→B, `apx:errata:corpus`→B.4.

**One hard-coded prose pointer**, external, at `2_fundamentals.tex:170` — see D-1.

---

## SECTION 5 · INTERNAL CONSISTENCY

### 5(a) · The freeze control: Ch. 6 vs Ch. 5's rewritten wording — **CONSISTENT, one wording note**

Side by side:

> **Ch. 5** (`5_mobiwac.tex:659`): "We **fix the region pathway at its initial values** at the start
> of training so it can neither learn nor teach the category task, yet the full category gain
> survives at Alabama, Arizona, and Florida"
>
> **Ch. 6** (`6_conclusion.tex:92-96`): "First, the **freeze control** reported in
> Chapter~\ref{ch:mobiwac}: with the region pathway **frozen**, the category gain survives, **at the
> three datasets where the control was run (Alabama, Arizona, Florida)**, so the gain does not come
> from the region task teaching the category task; it comes from a stronger shared trunk."

**Substantively consistent.** Same mechanism, same three datasets, same attribution, and Ch. 6
correctly scopes the claim to three datasets. Ch. 6 does not repeat any of Ch. 5's numbers, so
there is no numeric divergence to find. **No contradiction.**

**Wording note (NIT).** Ch. 5 was rewritten to "fix … at its initial values" per
`WRITING_LAW.md:60` ("'frozen' (write 'fixed', except frozen weights, glossed)"); Ch. 6 still says
"freeze control" and "frozen". Ch. 6's usage is arguably inside the exception — the weights *are*
what is frozen — but the two chapters now name the same control two different ways, which the
"define once, then use consistently" rule disfavours. Author's call; the gate does not rule on
prose. Flagged so it is a decision rather than an oversight.

### 5(b) · The inferential unit across all five locations — **CONSISTENT**

| location | wording |
|---|---|
| `0_main.tex:210-213` (Resumo, PT) | "vinte modelos ajustados por configuração (quatro inicializações aleatórias sobre um único conjunto fixo de cinco partições), testes de significância pareados sobre **as quatro médias por inicialização**" |
| `0_main.tex:285-288` (Abstract, EN) | "twenty fitted models per configuration (four random initializations over one fixed set of five folds), paired significance tests on **the four per-initialization means**" |
| `1_introduction.tex:243-245` | "twenty fitted models per configuration (four seeds over one fixed set of five folds), paired significance tests on **the four per-seed means, that is, four paired observations**" |
| `5_mobiwac.tex:394` | "both models use four seeds ($4\times5=20$ measurements) and the tests pair the per-seed means (**$n{=}4$**)" |
| `6_conclusion.tex:74` | "twenty fitted models per configuration, four seeds over one fixed set of five folds, and paired tests on **the four per-seed means**" |
| `GLOSSARY.md:79` (the authority) | "4 seeds × 5 folds per cell = 20 fitted models … the reported tests pair the four per-seed means, so **the inferential unit is n = 4**" |

All five agree with each other and with the GLOSSARY. The PT/EN pair is a faithful translation
("inicializações" ↔ "initializations", "médias por inicialização" ↔ "per-initialization means"),
verified in the rendered PDF (pp. 3 and the English abstract page). The phrase the GLOSSARY forbids
— "n = 20 paired repetitions" — appears **nowhere**. The fixed-partition caveat travels with the
claim at `1_introduction.tex:245-246` ("All four seeds reuse the same fold partition, so the
reported intervals do not cover uncertainty over resampled user splits"), which matches
`STATISTICAL_PROTOCOL.md:187-190`. **PASS.**

### 5(c) · Extensions beyond the two named risks

- **Study count and publication status.** "three studies" everywhere (10 sites); CBIC "published
  at", CoUrb "published in Portuguese", MobiWac "**submitted** … **under review**" at all five of
  its mentions (`1_introduction.tex:118,210-212`, `2_fundamentals.tex:237`, `5_mobiwac.tex:23-24`).
  The corrected "three published studies" error is gone. BRACIS appears only in Appendix A as an
  earlier unpublished submission (C4 containment). **PASS.**
- **Appendix B addition counts.** Ch. 4's "**eight** marked additions" claim (`apx_b_errata.tex`)
  was verified by locating all eight in `4_courb.tex` (:13 preface, :81 subsection, :238 split
  sentence, :258 dataset-table lead, :278 figure reading instruction, :284 category-table lead,
  :327 next-POI-table lead, plus the terminology bridge). Ch. 5's three declared additions are
  present at `5_mobiwac.tex:19, 88, 462`. **PASS.**
- **Appendix B row counts.** The header comment claims "6 + 13 + 3 + 14 = 36". Recomputed from the
  table bodies: B.1 = 6, B.2 = 13, B.3 = 3, B.4 = 4, B.5 (bibliography) = 14. The arithmetic holds
  for the four tables the comment enumerates. **PASS.**
- **Ch. 2's protocol-scoping claims about Ch. 3 and Ch. 4** — all three verified in the target
  chapters: Ch. 3 reports 5-fold without naming the axis (`3_cbic.tex:294`), Ch. 4 states sample
  stratification (`4_courb.tex:238`), only Ch. 5 splits by user. **PASS.**
- **Ch. 4's single-seed declaration** (added this round) verified against the code of record at
  `/Users/vitor/Desktop/mestrado/temp/tarik-new`: `create_fold.py:162` `random_state: int = 42` as
  the default, `:180-181` `torch.manual_seed` / `np.random.seed`, `:226,229` plain `StratifiedKFold`
  with no `groups=`, and `mtlnet_trainer.py:52-56` calls `create_folds` without overriding it. The
  prose's careful hedge ("the **released code of record** pins a single random seed") is exactly
  right and does not overclaim that these files produced the published runs. **PASS.**
- **Gowalla vintage.** Ch. 4 says "February 2009 and October 2010" (`:381`), which is the published
  paper's own statement; Ch. 6's limitation says "2009 and 2011" (`:167`), which matches Ch. 5's
  measured provenance comment (parquet range 2009-01-21 … 2011-08-16). The GLOSSARY row says
  "2009–2010". These are three different corpora statements (the CoUrb-era SNAP dump vs the
  figshare dump the Ch. 5 ETL consumes), each correct in its own chapter, but the GLOSSARY entry is
  narrower than Ch. 6's frame-level claim. **Recorded for the author** — not a fact error, a
  registry-scope question.
- **Ch. 2's MRR sentence.** `2_fundamentals.tex:460-461` says mean reciprocal rank "accompanies
  [Acc@10] where the joint comparison needs a rank-sensitive figure", but MRR appears in **no**
  results table or prose sentence anywhere else in the document (single hit, document-wide).
  Not false — the metric is defined in `METRICS.md` and computed in `metrics.py` — but the chapter
  promises a figure the document never shows. **Recorded for the author.**

---

## NUMBERS LEDGER (value → file → field)

Every value I re-derived this session. "Quoted" means the digits appear verbatim in the source
file; nothing in this table was computed by me or by any agent in prose.

### Chapter 6 — capacity-matched dedicated category baseline

| value | printed at | source file | field |
|---|---|---|---|
| 4.2 million (AL joint) | `6_conclusion.tex:98` | `capacity_matched_stl_cat/README.md:28` | joint v17 = 4,197,621 |
| 0.6 million (AL dedicated) | `6_conclusion.tex:99` | `README.md:28` | dedicated cat h=256 = 644,359 |
| 56.16 | `6_conclusion.tex:101` | `capacity_matched_summary.json` | `results.alabama_h672.bs2048_lr0.0025.mean = 56.1611` |
| 56.82 | `6_conclusion.tex:101` | `capacity_matched_summary.json` | `reference_points_diag_best.alabama.dedicated_ceiling_h256` |
| 64.51 | `6_conclusion.tex:102` | `5_mobiwac.tex:574` / `JOINT_BEST_RESULTS.md` | AL joint-best cat; gate `m2_prereg_output.txt` "recomputed 64.5051 vs board 64.51" |
| twenty fitted models | `6_conclusion.tex:100,112` | `capacity_matched_summary.json` | `protocol.n_per_arm = 20` (5 folds × seeds {0,1,7,100}) |
| three training configurations (AL) | `6_conclusion.tex:100` | `README.md:36-40` | three arms listed |
| 752 | `6_conclusion.tex:110` | `README.md:29` | matched width `hidden_dim=752` |
| 101.9 percent | `6_conclusion.tex:110` | `README.md:29` | 5,249,719 (101.9%) |
| 69.88 | `6_conclusion.tex:111` | `capacity_matched_summary.json` | `results.california_h752.bs8192_lr0.0025.mean = 69.8789` |
| 0.26 | `6_conclusion.tex:111` | same | `.std = 0.2645` |
| 70.60 | `6_conclusion.tex:112` | `capacity_matched_summary.json` | `reference_points_diag_best.california.dedicated_ceiling_h256 = 70.6` |
| 0.07 | `6_conclusion.tex:112` | same | `ceiling_std = 0.07` |
| 0.72 (CA shortfall) | `6_conclusion.tex:114` | `README.md:47` | "69.88 ±0.26 (**−0.72**)" |
| 0.66 (AL shortfall) | `6_conclusion.tex:115` | `README.md:46` | "56.16 ±1.89 (**−0.66**)" |
| lower learning rate at both | `6_conclusion.tex:116-118` | `README.md` "Methodological observation" | AL 0.0025 vs 0.005; CA 0.0025 vs 0.005 |
| 20.2 to 22.0 | `6_conclusion.tex:46` | `4_courb.tex:35` (published abstract) | per-state average gains |
| 192 / 64 | `6_conclusion.tex:50` | `4_courb.tex` methodology | decomposed encoder width vs place embedding |
| 5.3 to 9.4 | `6_conclusion.tex:75`, `0_main.tex:290` | `JOINT_BEST_RESULTS.md:65` | "+5.33 … +9.35" |
| +0.001 | `6_conclusion.tex:147` | `T4_audit_and_verdict.md:47-49` | pooled cosine mean +0.0008 over 16 runs |
| 2009 and 2011 | `6_conclusion.tex:167` | `5_mobiwac.tex` provenance comment | measured parquet range 2009-01-21 … 2011-08-16 |

### Chapter 5 — leak audit (fourth ground)

| value | printed at | source file | field |
|---|---|---|---|
| ~0.41 ceiling | `5_mobiwac.tex:367` | `RESCREEN.md` | "clean control ceiling (~0.41)" per-step gate |
| 0.4090 / 0.4074 | `:367` | `leak_sniff_fl.csv` | `check2hgi_gcn_ctrl` perstep / perstep_raw |
| 0.4197 / 0.4182 | `:367` | `leak_sniff_resln_fl.csv` | `check2hgi_resln` perstep / perstep_raw |
| 0.4976 / 0.4863 | `:367` | `leak_sniff_fl.csv` | `check2hgi_gat`, verdict `LEAK` |
| linear probe / GroupKFold / 5 folds | `:367` | `scripts/embedding_eval/leak_sniff.py:59` | `f1_score(..., average="macro")`, `GroupKFold` |
| −0.33 to +0.01 (region) | `:367` | `A4_RESULTS.md:61-63` | AL −0.33, AZ +0.01, FL −0.12 |
| 0.00 to +0.29 (category) | `:367` | `A4_RESULTS.md:61-63` | FL +0.00, AZ +0.27, AL +0.29 |
| 67 to 87 percent | `:367` | `A4_RESULTS.md:61-63` | in-coverage 66.8 / 71.9 / 86.9 |
| 13 to 27 points | `:367` | `docs/context/DATA_SPLITS.md:58` | "leak-inflated by 13–27 pp" |

### Chapter 5 — freeze control

| value | printed at | source file | field |
|---|---|---|---|
| 63.50 / 63.67 / 79.79 | `5_mobiwac.tex:660` | `W6_ENCODER_ISOLATION.md:22-24` | column "probe cat (freeze-reg)" |
| +7.63 / +6.54 / +4.64 | `:662` | same | column "Δ vs ceiling" (against Table 2's 55.87/57.13/75.15) |
| 63.56 / 63.39 / 79.82 | `:667` | same | column "full-MTL cat (§1)" |
| within 0.3 | `:668` | `W6_ENCODER_ISOLATION.md:29` | "Δ ≤ 0.3 pp" |
| one initialization, five folds | `:665` | `W6_ENCODER_ISOLATION.md:54` | "n=5 provisional (seed 0)" |

### Chapter 5 — statistics and headline

| value | printed at | source file | field |
|---|---|---|---|
| +5.33 to +9.35 | `:612` | `JOINT_BEST_RESULTS.md:65` | joint-best category range |
| +8.58 (Istanbul cat) | `:613,717` | `JOINT_BEST_RESULTS.md` Δ table | deploy Δcat |
| −0.41; −0.63 to −0.20 (AL reg) | `:647` | `STATISTICAL_PROTOCOL.md:290-291` | TOST AL, 90% CI |
| 0.00; −0.08 to +0.07 (AZ reg) | `:648` | same | TOST AZ, 90% CI |
| +0.71; +0.67 to +0.76 (FL reg) | `:652` | `STATISTICAL_PROTOCOL.md:290` | superiority FL |
| +0.19; +0.15 to +0.23 (Ist reg) | `:652` | same | superiority Istanbul |
| +2.10 to +2.13 (TX) | `:655-656` | `STATISTICAL_PROTOCOL.md:290-291` | CI +2.10..+2.13 |
| +2.19 to +2.21 (CA) | `:656` | same | CI +2.19..+2.21 |
| 20/20 folds, corrected p<0.001 | `:641-645` | `stats_n20/m2_prereg_output.txt` | Holm-adj 5.72e-06 (cat, m=6); 3.81e-06 (reg, m=4) |
| ≤0.06 / ≤0.11 (diag-best bound) | `:504` | `JOINT_BEST_RESULTS.md` headline | "≤ 0.06 pp (category) and ≤ 0.11 pp (region)" |
| Table 3 all 24 cells | `:573-596` | `m2_prereg_output.txt` §0 | 24/24 artifact→board gate, all `[OK]` |
| Table 2 all cells | `:447-452` | `articles/[mobiwac]/src/tables/tbl2_substrate.tex` | character-for-character |
| 51 to 72 Acc@10 (Markov floor) | `:701` | `MARKOV_FLOOR_STRIDE1.md:73` | "spans **51 to 72** Acc@10" |
| 4.9 to 10.3 (margin) | `:702` | `MARKOV_FLOOR_STRIDE1.md:72` | "+4.9 to +10.4" — see D-3 |
| 4.2 / 1.1 / 5.2 / 2.0 million | `:274-276` | `capacity_matched_stl_cat/README.md:28-29` | "Reproduces the parameter figures quoted in the MobiWac method section" |
| about 7 percent (majority floor) | `:492` | VoR `06_results.tex:35` | reproduced verbatim |
| +0.001 gradient cosine | `:205` | `T4_audit_and_verdict.md:47-49` | pooled +0.0008, 16 runs, n=3,797 |

### Chapter 2 — HGI retuning

| value | printed at | source file | field |
|---|---|---|---|
| 0.4 (paper) | `2_fundamentals.tex:170` | `hgi/README.md:541`; `preprocess.py:36` | "paper sets to `0.4` for Xiamen/Shenzhen" |
| 0.7 (here) | `:170` | `preprocess.py:23`; `hgi.pipe.py:60,73-77` | `DEFAULT_CROSS_REGION_WEIGHT = 0.7` |
| 0.74 | `:172` | `hgi/README.md:548` | `w_r 0.4 → Cat F1 0.7388 ± 0.0205` |
| 0.82 | `:172` | `hgi/README.md:551` | `w_r 0.7 → Cat F1 0.8186 ± 0.0123` |
| monotonic | `:172` | `hgi/README.md:548-551` | 0.7388 → 0.7678 → 0.7944 → 0.8186 |
| five folds | `:172` | `hgi/README.md:544` | "(5 folds × 50 epochs)" |
| averaging convention | (hedged) | `metrics.py:283-285,299` + docstring `:10,19-21` | `_key("f1") = f1_macro`, `average="macro"` — **macro-F1**, see §1.4 |
| 93 percent | `:35,476` | `song2010limits` (Science 327:1018–1021) | predictability bound |

---

## COULD NOT VERIFY

Nothing in the audited scope was left unverified. Two items are recorded as *scope* rather than
failure:

1. **The dropout caveat on the freeze control** (`W6_ENCODER_ISOLATION.md:64`, the 2026-07-01
   mode-vs-weights note) is real and is not surfaced in prose. W6 itself records the directional
   conclusions as standing, so omitting it is defensible — but it is an author decision, not a
   verified fact, and I did not rule on it.
2. **Whether the CoUrb-era code files produced the published CoUrb runs** cannot be established
   from the repository. The chapter does not claim it does — `4_courb.tex:253` records the
   non-claim explicitly — so this is correct handling, not a gap.

---

## WHAT TO FIX BEFORE THE NEXT GATE

1. **B-1 (BLOCKER).** Re-run BibTeX + two LaTeX passes for both targets. Verify afterwards: zero
   `(??)` in the text layer of both PDFs, 98 `\bibitem` in `build/main.bbl`, "RUßWURM" present in
   the printed reference list, and both `.blg` files clean of "didn't find a database entry".
   Regenerate or remove the stale `src/main.bbl`.
2. **D-3.** Add a ledger comment for the "4.9 to 10.3" Markov margin naming its joint-best basis, or
   record it in Appendix B as a reproduced value.
3. **§1.4.** Rule on the HGI averaging convention: the trace supports "macro-F1"; the hedge is
   correct but no longer necessary.
4. **D-1, D-2, N-1, N-3, N-4, 5(a) wording, and the two recorded-for-author items (Gowalla vintage
   registry scope; the MRR promise).** Author's call, each recorded above with its specific
   correction.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
