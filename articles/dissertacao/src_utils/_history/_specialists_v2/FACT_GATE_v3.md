# FACT_GATE_v3 — G2 fact verification (citations, numbers, claims)

> 🛑 **GERACAO SUPERADA — nenhum numero deste ficheiro pode ser citado.**
>
> Isto e o fact gate G3, corrido em 27 de julho de 2026, **antes** de a geracao v18 fechar o vazamento de rotulo
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


**Reviewer:** Dissertation Fact Gate (personas 05 citation auditor, 06 number auditor,
07 claim-honesty auditor, 08 translation fidelity).
**Scope:** the correction round of 2026-07-27 — Appendix A.2 removal, Appendix D rewrite,
Appendix E (new), MTLnet normalization in Ch.4, bibliography font, the rescoped
cross-attention clause in Ch.5/Ch.6, the rewritten Markov-floor paragraph in Ch.5.
**Builds audited:** `src/dissertacao.pdf` (102 pp, created 2026-07-27 06:40) and
`src/build/main_final.pdf` (97 pp, created 2026-07-27 06:42).
**Read-only.** No file in the repository was modified except this report. No git, no build.

---

## VERDICT

# GATE FAIL

One BLOCKER, four MAJOR and four MINOR findings. The BLOCKER is a number that does not trace to any
committed source under the reading the chapter gives it: the Alabama revisit share in the
Markov-floor paragraph is a **place-level** figure measured on a **different windowing**,
presented as a **region-level** share of the shipped sliding windows. Reproduced from the
repository's own artifacts, the quantity the sentence describes is **62.9 percent**, not
22.4.

Everything else in the round that could be checked, checks out. Appendix D's table is
correct in all 45 cells. Both licence claims in Appendix E resolve at the source of record.
The rescoped ablation clause is supported by the finding it cites and by the champion
configuration. The MTLnet errata entry's count and its "no effect on any quantity or
reference" claim are both correct.

### Mid-session build replacement — disclosure

The two PDFs and three chapter sources (`5_mobiwac.tex` 06:38, `6_conclusion.tex` 06:32,
`apx_d_ceiling.tex` 06:31) were rewritten **while this audit was running**. An earlier pass
of mine found two defects that the 06:40/06:42 build no longer contains, and I re-ran every
check against the current bytes:

| defect found in the superseded build | status in the current build |
|---|---|
| `\\pm` (doubled backslash) in `5_mobiwac.tex` leaked the macro name onto the page as `−0.04 𝑝𝑚0.13` | **FIXED.** Both files now hold a single `\pm`; p73 / p68 render `−0.04 ± 0.13`. |
| Ch.5 asserted "Every encoder screened … lies above the label-history benchmark", which `leak_sniff_fl.csv:8` contradicts | **FIXED.** The quantifier is now scoped to the clean references plus the raw run, and the exception is named. |

Both are cleared. **Every finding below is against the 06:40/06:42 build**, verified page by
page. Reviewers working from an earlier extraction of these PDFs are reading stale bytes.

---

## 1. BLOCKER

### B-1 — The Alabama revisit share is a place-level number on the wrong windowing

**Locus:** `src/chapters/5_mobiwac.tex:789` · defense p73 · final p68.
**Rendered sentence:** "At Alabama, 22.4 percent of windows contain their own target region
as a genuine revisit."
**Its only committed source:** `docs/studies/archive/mtl_improvement/PIPELINE_AUDIT_2026-06-03.md:24`
(named in the chapter's own ledger comment at `:801`), which reads: the 22.4% "target
reappears in its own 9-history" rate is legitimate user revisits, unchanged by overlap.

Two things separate the source from the sentence:

1. **Level.** The audit line says "target", with no mention of region. It sits inside a
   discussion of the non-overlapping *place*-level substrate. The chapter reads it as a
   *region* share.
2. **Windowing.** The audit's 9-history is the frozen non-overlapping build (stride 9,
   12,709 Alabama windows). The floor the paragraph is defending is computed on the
   stride-1 board windowing (96,326 Alabama windows) — the paragraph says so itself, one
   sentence earlier ("Those windows advance one visit at a time").

Under AGENT_GUARDRAILS the number should be quoted, not computed. It is not quotable as
written, so I applied the reproduce-first rule: rebuilt both windowings from
`output/check2hgi/alabama/temp/checkin_graph.pt` and `sequences_next.parquet`, using the
closed form documented in `scripts/closing_data/compute_markov_floor_stride1.py:1-40`.

| quantity | windowing | n | value |
|---|---|---|---|
| target **POI** in own 9-history | non-overlapping | 12,709 | **22.38 %** ← reproduces the audit's 22.4 |
| target **POI** in own 9-history | stride-1 | 96,326 | 22.18 % |
| target **REGION** in own 9-history | non-overlapping | 12,709 | 60.11 % |
| **target REGION in own 9-history** | **stride-1 (shipped)** | **96,326** | **62.88 %** |
| target region == last visited region | stride-1 | 96,326 | 32.91 % |

The stride-1 rebuild lands on exactly 96,326 windows, the count
`markov_floor_stride1/alabama.json` records, so the reconstruction is sound. Reproducing the
recorded 22.38 % on the non-overlapping build confirms what the audit line actually measured.

**Why this is a BLOCKER and not a MAJOR.** The sentence exists to explain why the floor is
high. A 22.4 % revisit share is a *weak* explanation for a floor at 62.26 Acc@10; the true
62.9 % is a strong one. The number as printed **understates the author's own argument by a
factor of nearly three** while attaching a wrong-level, wrong-protocol figure to it. A
banca member who recomputes it finds both a wrong number and a wrong claim about what was
measured.

**Fix (author's ruling, three options):**
- Quote the region-level stride-1 share and record its provenance. It is not in a committed
  file today, so it needs a small committed artifact first (the guardrails forbid a prose
  number with no file behind it).
- Or quote the region-persistence rate instead (32.91 % — "the target region is the last
  visited region in about a third of windows"), which is the quantity a *first-order*
  transition table actually reads and is therefore the tighter argument. Same provenance
  requirement.
- Or delete the sentence. The paragraph's protocol-asymmetry point survives without it: the
  preceding clause ("the region of the last visit is a strong predictor of the next one")
  already carries the mechanism, and it needs no number.

---

## 2. MAJOR

### M-1 — Appendix E's "no longer serves the dataset" is not what the address does

**Locus:** `src/chapters/apx_e_ethics.tex:31` · defense p101 · final p96.
**Claim:** "The record also names a further site as the origin of the files, and that
address no longer serves the dataset, so its terms could not be read."

The Figshare description does name the origin (`http://www.yongliu.org/datasets/`,
verified live in the API record for article 22126586, 2026-07-27). But probing that host
with redirects suppressed returns:

```
http://www.yongliu.org/datasets/  -> HTTP 301, Location: https://idnpokerasia.net/
https://www.yongliu.org/datasets/ -> HTTP 301, Location: https://idnpokerasia.net/
http://www.yongliu.org/           -> HTTP 301, Location: https://idnpokerasia.net/
```

The domain does not fail to serve the dataset. It has been **repurposed** and now redirects
every path to an unrelated commercial site. "No longer serves the dataset" is defensible as
a consequence, but it describes a dead link, and what the record shows is a live host under
different control. In an appendix whose entire value is that its institutional claims are
literally true, the gap matters: an examiner who clicks the address does not see a 404, they
see a gambling site, and the appendix did not prepare them for that.

**Fix:** state what was observed. For example: "the address the record names now redirects
to an unrelated site, so its terms could not be read." One clause, and it is exactly true.

### M-2 — Appendix E does not disclose that one upstream is access-gated

**Locus:** `src/chapters/apx_e_ethics.tex:45` · defense p101 · final p96.
**Claim:** "One check is outstanding: the Foursquare product terms were not read, only the
licence tag on the distribution."

Correct as far as it goes, and the honesty of flagging it is right. What it omits: the
Foursquare Open Source Places distribution is **gated**. The Hugging Face API returns
`gated: "auto"` for `foursquare/fsq-os-places`, with an `extra_gated_prompt` that requires
the reader to agree to terms on behalf of themselves or their organization before download.
The licence tag is `apache-2.0`, as the appendix implies, but the artifact is not freely
retrievable the way the sentence's framing suggests.

This bears directly on the appendix's own reproducibility claim two sections later ("a
reader reproducing the results obtains both collections from the sources named above") — for
the Istanbul lineage's upstream, that reader must accept an agreement first.

**Fix:** add the fact. "That distribution is additionally access-gated behind an agreement
prompt" — and note that the Massive-STEPS copy actually used is *not* gated (verified:
`gated: false` on `CRUISEResearchGroup/Massive-STEPS-Istanbul`), which is the reassuring
half of the disclosure and is currently missing too.

### M-3 — Ch.5's "22.4 percent" ledger comment names a source that does not support it

**Locus:** `src/chapters/5_mobiwac.tex:801` (the hidden ledger) · same rendered pages as B-1.
The ledger says "Every figure QUOTED, none computed here" and lists
`PIPELINE_AUDIT_2026-06-03.md:24 (AL 22.4%)`. Per B-1, that line does not state a region
share and was not measured on the shipped windowing. The ledger's own honesty device —
naming the file and line for each number — is what makes the defect findable, and it is also
what makes the defect a documented mis-citation rather than a slip. It needs to be corrected
together with the prose, not after it.

Recorded separately from B-1 because fixing the sentence without fixing the ledger leaves a
false provenance pointer in the source for the next reviewer to trust.

### M-4 — Appendix D's own ledger comment cites a Ch.5 defect that no longer exists

**Locus:** `src/chapters/apx_d_ceiling.tex:112` (source comment; not rendered).
Text: "5_mobiwac.tex:376 still asserts 'Every encoder screened ... sits above'; reported for
narrowing, not edited here (not my file)."

`5_mobiwac.tex:376` no longer asserts that — it was narrowed in the 06:38 revision, and the
current build renders the scoped version. The comment is now false. It is invisible to a
reader of the PDF, so it endangers no result, but it is the kind of stale cross-file note
that a later agent reads as a live finding and "fixes" by reverting a correct sentence.

**Fix:** delete the last two lines of that comment, or replace them with the resolution
("narrowed at 5_mobiwac.tex:376 on 2026-07-27").

---

## 3. MINOR

### N-1 — "MtlNet" appears on four rendered pages

**Locus:** `src/chapters/3_cbic.tex:66` (defense p28 / final p23) and
`src/chapters/5_mobiwac.tex:55` (defense p59 / final p54).
Both are the public repository URL, `github.com/VitorHugoOli/PoiMtlNet`. GLOSSARY.md:41
pins `MTLnet` as canonical; `PoiMtlNet` is a third casing and it is printed. It is a real
repository name and cannot be silently re-cased in a URL. Flagged only because Appendix B
now claims the spelling was standardized, and a reader who greps the PDF finds this.
**Fix:** none needed to the URLs. If Appendix B's paragraph is to be exhaustive, one clause
noting that the repository name keeps its own casing would close the loop.

### N-2 — The Markov margin range still has no ledger basis

**Locus:** `src/chapters/5_mobiwac.tex:779` · defense p73 · final p68 ("exceeds it by $4.9$
to $10.3$ points").
The floor range (51 to 72) traces to `MARKOV_FLOOR_STRIDE1.md`. The margin range does not:
that document computes **+4.95 to +10.38** from joint cells `Ist 75.44 / FL 77.42`, whereas
the chapter's own Table 10 prints `Ist 75.35 / FL 77.41`. Recomputing from the chapter's
table against the committed floors gives **4.94 to 10.29**, which rounds to the printed
"4.9 to 10.3" — so the number is right, and it is right *because* it was re-derived from the
shipped cells rather than copied from the study document. That derivation is nowhere
recorded. FACT_GATE_v2 (D-3) already raised this; it is still open.
**Fix:** one ledger line naming the two inputs (Table 10 joint column, `markov_floor_stride1/<state>.json`
key `markov_1step_region_acc10_mean`) and the subtraction.

### N-3 — One uncited bibliography entry

`references.bib` defines 99 entries; 98 are cited and 98 render. `liu2014geographical` is
defined and never cited. Harmless (BibTeX omits it), but it is dead weight in a file that
otherwise lints clean.

---

### N-4 — The built Appendix B undercounts the MTLnet sites by one

**Locus:** defense p92 · final p87 (rendered); superseded by `apx_b_errata.tex:306-308` on
disk, rewritten 07:08:45 **after** the audited builds.
The audited builds print "all **24** places … 21 in prose, one in a figure caption, and two
in table headings" — a breakdown that omits the subsection heading at `4_courb.tex:122`
("Baseline: MTLnet with DGI"), which is reproduced published structure and was normalized.
My census gives 25. The source on disk has already been corrected to 25 with the heading
included, and its comment records the re-measurement, so this is **fixed in source and stale
only in the PDF**. It clears on the next build.
Recorded rather than dropped for two reasons: the version the banca would read today is
wrong, and a reviewer diffing this report's loci against the current PDFs needs the split
documented. **No action beyond rebuilding.**

## 4. ALL-CLEAR — verified this session, no defect

### 4.1 Appendix D (rewritten) — every number traces

Source of truth: `docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.json`.
Table 16 (defense p99 / final p94) reconstructed **cell by cell** and compared
programmatically — all **45 cells match exactly**: 5 window counts, 20 per-predictor
scores, 5 benchmarks, 5 standard deviations, 5 floors, and the bolded best-predictor in
each row.

| dataset | windows | pers. | one-hot | counts | positional | benchmark | floor | bold |
|---|---|---|---|---|---|---|---|---|
| Alabama | 12,709 | 0.2800 | 0.2800 | 0.2783 | 0.2791 | 0.2800 ± 0.0138 | 0.0727 | persistence ✓ |
| Arizona | 26,396 | 0.3080 | 0.3080 | 0.3191 | 0.3232 | 0.3232 ± 0.0163 | 0.0725 | positional ✓ |
| Florida | 159,175 | 0.3417 | 0.3417 | 0.3503 | 0.3617 | 0.3617 ± 0.0069 | 0.0566 | positional ✓ |
| California | 358,302 | 0.3160 | 0.3160 | 0.3148 | 0.3242 | 0.3242 ± 0.0057 | 0.0704 | positional ✓ |
| Istanbul | 58,075 | 0.2588 | 0.2588 | 0.2947 | 0.3016 | 0.3016 ± 0.0058 | 0.0715 | positional ✓ |

Prose numbers also verified against the JSON and the two screen CSVs:

- range "0.2800 to 0.3617" = JSON min/max of `ceiling_macro_f1`. ✓
- Istanbul "196 of the 29,816 places" = `places_multi_category` / `places`. ✓
- strict variant "keeps 55,946 of the 58,075 windows and gives 0.3009, against 0.3016" =
  `sensitivity_strict_drop_ambiguous_last_place[0]`. ✓
- Texas absence: JSON `skipped` records `FileNotFoundError: missing
  output/check2hgi/texas/temp/checkin_graph.pt`. Independently confirmed on disk —
  `output/check2hgi/texas/` is empty while all five other states hold `checkin_graph.pt`
  and `sequences_next.parquet` at exactly the row counts the table prints. ✓
- clean reference encoders "0.4090 / 0.4074" and "0.4197 / 0.4182" = `leak_sniff_fl.csv`
  and `leak_sniff_resln_fl.csv`, `perstep` / `perstep_raw`, rounded to 4 dp. ✓
- discarded attention encoder "clears the clean reference encoder by 8.9 points" =
  `delta_std` 0.08864 → 8.86 pts. ✓
- exception "0.3328 … rises to 0.4142" = the relation-typed encoder's `perstep` /
  `perstep_raw`. It is the **only** candidate below the benchmark on the standardized run
  and **none** is below on the raw run — which is exactly the scoped claim now made. ✓
- "screening margin of three points" = `leak_sniff.py:63,99` default `margin=0.03`. ✓
- "four to six points" at Florida = 0.4090−0.3617 = 0.0473 and 0.4197−0.3617 = 0.0580. ✓
- protocol claims (five-fold, grouped by user, balanced class weights, macro-F1 over seven
  categories) match `autocorrelation_ceiling.py:52,125,136` and the JSON `protocol` string,
  and the "same protocol the screen itself uses" claim matches `leak_sniff.py:38,45`
  (`GroupKFold(5)` by user in both). ✓
- floor definition "predicts the training portion of each fold's majority class" matches
  `autocorrelation_ceiling.py:143-146` (argmax of the train-fold bincount). ✓

The disqualification narrative for the exception ("passed this screen and then leaked under
a downstream sequence model") is supported by `RESCREEN.md:47-52,92`: the per-step linear
gate marks it clean, and it was disqualified at the L2 sequence stage. Describing it by
architecture rather than acronym is consistent with the fail-closed GLOSSARY rule.

### 4.2 The "ceiling" retirement holds

19 printed uses of the word remain in the chapter sources. Every one is legitimate under
GLOSSARY.md:52, which retires the term **for the label-history quantity only** and
explicitly keeps it for the dedicated single-task arm:

- 8 refer to the **dedicated single-task model** (Ch.2 ×2, Ch.5 ×5, Ch.6 ×1) — the surviving
  correct sense.
- 1 in Ch.2 explicitly *denies* a ceiling reading of the predictability limit.
- 4 are cross-reference and table labels (`apx:ceiling`, `tab:apx:ceiling`) — mechanical,
  invisible to the reader.
- 3 are the released script and output filenames, which Appendix D discloses in prose
  ("Those file names keep the older word").
- 2 are Appendix D naming the retired usage in order to retire it, and one Ch.5 mention of
  "single-task ceilings" as the comparison level.

No printed sentence uses "ceiling" for the label-history benchmark. The retirement is
complete in the sense the GLOSSARY defines.

### 4.3 The rescoped cross-attention clause is supported

**Loci:** `5_mobiwac.tex:707-715` (defense p73 / final p68); `6_conclusion.tex:97-103`
(defense p77 / final p72).

- The value `−0.04 ± 0.13` is `F50_T1_5_CROSSATTN_ABSORPTION.md:19` verbatim
  (cat F1 68.36 ± 0.74 vs 68.32 ± 0.67). ✓
- "a paired test cannot separate from zero": F50:5 records paired Wilcoxon p = 0.6250. ✓
- **The prior claim is the load-bearing new assertion, and it holds.** F50:5, :66, :84, :229
  all name "the reg head's α·log_T graph prior" as the mechanism that leaves the shared
  backbone nothing to do. And the shipped configuration does not use it:
  `src/configs/canon.py:51-52` pins `freeze_alpha=True` and `alpha_init=0.0`, which
  `src/models/next/next_stan_flow/head.py:95-104` documents as disabling the α·log_T prior
  entirely ("output = stan_logits alone"). So "an earlier configuration whose region head
  was driven by a transition prior the models reported here do not use" is accurate on both
  halves. ✓
- The configuration difference is corroborated independently: F50:223-224 gives run dirs
  under `results/check2hgi/florida/…bs2048_ep50_20260429…`, while every shipped record in
  `docs/results/closing_data/catx_v17_n20/*.json` (and `joint_best/*.json`) carries
  `rundir: results/check2hgi_dk_ovl/<state>/…bs8192_ep50_2026070*/…` — a different
  representation build and batch size. ✓
- "its own record reads the null as a compensation effect": F50:229 calls its own null
  "misleading" and "a hidden compensation effect". ✓
- Verb discipline: both chapters withhold attribution in both directions ("we do not name
  the shared trunk as the source, and we do not present the ablation as evidence against
  it"). No superiority verb is attached to a null. ✓

### 4.4 The Markov-floor paragraph — everything except the revisit share

All counts re-derived from `markov_floor_stride1/<state>.json` key
`markov_1step_region_acc10_mean` and the chapter's own Table 10:

| dataset | floor | joint | margin | dedicated | HMT-GRN | ReHDM | STAN |
|---|---|---|---|---|---|---|---|
| Istanbul | 65.06 | 75.35 | +10.29 | 75.16 | 60.40 ↓ | 69.33 | 61.86 ↓ |
| Alabama | 62.26 | 69.70 | +7.44 | 70.11 | 57.05 ↓ | 65.38 | 60.72 ↓ |
| Arizona | 51.23 | 59.46 | +8.23 | 59.46 | 43.70 ↓ | 53.00 | 49.86 ↓ |
| Florida | 72.47 | 77.41 | +4.94 | 76.70 | 63.74 ↓ | 64.49 ↓ | 72.99 |
| Texas | 60.10 | 67.06 | +6.96 | 64.95 | 53.85 ↓ | 48.81 ↓ | 61.67 |
| California | 59.09 | 65.69 | +6.60 | 63.49 | 49.61 ↓ | 50.26 ↓ | 58.52 ↓ |

- "reaches 51 to 72 Acc@10" — floors span 51.23 to 72.47. ✓
- "exceeds it by 4.9 to 10.3 points on all six" — 4.94 to 10.29, all positive. ✓ (provenance: N-2)
- "HMT-GRN falls below it at all six, the ReHDM reference at three, and STAN at four" —
  **6 / 3 / 4 exactly.** ✓
- "The dedicated and joint models are above the floor at every dataset" — dedicated margins
  +4.23 to +10.10, all positive. ✓
- The three protocol-asymmetry clauses (HMT-GRN same data/folds/initialization; STAN same
  folds but own embeddings and sequences; ReHDM under its own published protocol) match the
  baselines subsection at `5_mobiwac.tex:422` clause for clause. ✓
- The paragraph states an asymmetry and explicitly declines a single causal explanation
  ("Neither fact establishes why the floor lies above the three systems, and we do not claim
  a single explanation"). That is the rewrite the round claimed. ✓

### 4.5 Appendix E's licence and institutional claims — verified at the source of record

Every record below was opened live this session (2026-07-27), not taken from
`DATASET_LICENSING_FINDINGS.md`, which I audited rather than trusted.

| appendix claim | source of record | result |
|---|---|---|
| Gowalla deposit at DOI `10.6084/m9.figshare.22126586.v2` carries CC0 | Figshare API, article 22126586 | `doi: 10.6084/m9.figshare.22126586.v2`, `license: {name: "CC0", url: creativecommons.org/publicdomain/zero/1.0/}`, version 2 ✓ |
| "dedication was applied by the depositor … identified there by a single name" | same record | `authors: ["Yang"]` ✓ |
| "Four of its files enter the pipeline: the check-in table, two place tables, and the category structure file" | `src/etl/gowalla/main.py:22-27` + deposit file list | deposit holds 6 files; ETL declares check-ins, both place tables, structure file, plus two *local* category JSONs ✓ |
| "seven place categories … are the top-level names in that structure file" | `data/gowalla/gowalla_category_structure.json` vs `src/configs/globals.py:26` | 7 top-level names, identical and in order: Community, Entertainment, Food, Nightlife, Outdoors, Shopping, Travel ✓ |
| "what the pipeline adds is the mapping … plus a short local supplement" | `src/etl/gowalla/stage_1.py:102,104` | reads `callback_categories.json` and `extra_categories.json` ✓ |
| SNAP release "carries no place categories, and its page states no license" | `snap.stanford.edu/data/loc-gowalla.html` | fetched; zero occurrences of licen/terms/copyright/categor in the page text ✓ |
| Massive-STEPS "distributed on Hugging Face under the Apache License 2.0" | HF API, `CRUISEResearchGroup/Massive-STEPS-Istanbul` | `cardData.license: apache-2.0`, tag `license:apache-2.0` ✓ |
| "The project repository carries the same license" | GitHub API, `cruiseresearchgroup/Massive-STEPS` | `Apache-2.0`, `LICENSE` ✓ |
| "documentation names the Semantic Trails Dataset and Foursquare Open Source Places as its sources" | HF raw dataset card | both named verbatim as the derivation sources ✓ |
| "no upstream term more restrictive than the Apache License 2.0 appeared" | figshare 7429076 (CC0); `D2KLab/semantic-trails` (Apache-2.0); `foursquare/fsq-os-places` (apache-2.0) | none more restrictive ✓ (but see M-2 on gating) |
| card carries the Foursquare copyright notice | HF raw card | "Copyright 2024 Foursquare Labs, Inc. … Licensed under the Apache License, Version 2.0" ✓ |

**Blocked by the network allowlist, so verified by another route:** `creativecommons.org`
(the CC0 deed the appendix footnotes) and the `figshare.com` HTML landing page. The
deposit's own API record carries the same licence name and the same
`creativecommons.org/publicdomain/zero/1.0/` URL, so the CC0 claim itself is verified; what
I could not do is read the deed text at the footnoted address. Recorded under
COULD-NOT-VERIFY below.

**The no-de-identification claim (`apx_e:58`) — independently re-derived, correct.** A
repo-wide search over privacy-mechanism vocabulary (differential privacy, ε, Laplace or
Gaussian noise, geo-masking, k-anonymity, anonymize, de-identify, obfuscate, coordinate
jitter or perturbation) returns **zero hits** outside the excluded worktrees. No rounding
or truncation is applied to latitude or longitude anywhere in `src/`. `stage_3.py:38-43`
builds geometry directly from the published coordinates at EPSG:4326. ✓
One nuance worth the author's attention, not a defect: a spatial discretization *does* exist
in the repository — `research/baselines/rehdm/etl.py:60,201` maps coordinates to level-10
quadkeys — but that is an **external baseline's** own input preparation, not the study's
pipeline, so the appendix's claim about "this work" holds.

**The restriction claims (`apx_e:66-72`) — all four confirmed.**
- Social-graph and profile files never read: `gowalla_friendship.csv` and
  `gowalla_userinfo.csv` exist in the deposit and on disk; a repo-wide search for any
  reader of either returns **zero hits**, and neither appears in `main.py`'s declared
  inputs. ✓
- "User identifiers are carried as opaque integers exactly as the sources supply them, and a
  non-numeric identifier is replaced by a position index that is not kept":
  `src/etl/massive_steps/stage_1.py:84-90` casts to int64 and falls back to an in-memory
  `uid_index` dict that is never persisted. ✓
- Data directory excluded from version control: `.gitignore` lines 5-7 exclude `/data/*`,
  `/temp/`, `/output/*`. ✓
- "Nothing in the code links a user across the two collections": no cross-collection user
  join exists; the two ETL paths are separate. ✓

**The human-subjects paragraph (`apx_e:76-91`) — sound.** The precedent dissertation
(`exemples/germano/`, 96 pp, cover reads FLORESTAL 2024, advisor Fabrício Aguiar Silva) was
searched over both Portuguese and English ethics-board vocabulary (comitê/comite, CAAE,
Plataforma Brasil, CEP, IRB, institutional review, ethics committee/board/approval,
Resolução, parecer): **zero hits**, while a positive control (privacy/privacidade) returns
hits on 7 pages — so the text layer is searchable and the negative is real. Its "Ethical
Statement" (p23) matches the appendix's description: it discusses location privacy and says
the latitude and longitude were kept unmasked. The appendix's framing ("That is how a close
precedent handled the question, not a determination of the rule") is exactly what the
evidence supports. The paragraph claims **no** approval and **no** exemption, and no
approval language appears anywhere in either build — the only ethics vocabulary on any
rendered page is Appendix E's own heading and its "research ethics committee" phrase
(defense pp. 12, 101, 102). ✓

### 4.6 MTLnet normalization — source count correct (build stale, N-4); no quantity or reference touched

**Appendix B (`apx_b_errata.tex:306-308`, defense p92 / final p87)** claims normalization at
"all 25 places where the name appears in the printed chapter: 21 in prose, one in a
subsection heading, one in a figure caption, and two in table headings."

> **Source and build disagree — see N-4.** `apx_b_errata.tex` was rewritten again at
> **07:08:45**, after the 06:40/06:42 builds. The **source on disk** now claims 25 places
> (21 prose + 1 subsection heading + 1 caption + 2 table headings) and its own comment
> records the re-measurement. The **audited builds still render 24** (defense p92 / final
> p87), with a breakdown that omits the subsection heading. The census below vindicates the
> source's 25 and finds the built 24 short by one; N-4 records that against the build.

Census of `4_courb.tex`, LaTeX comments stripped, `ST-MTLNet` excluded: **28 printed bare
`MTLnet`** — 23 prose, 2 subsection headings, 1 caption, 2 table headings. The rendered
Chapter 4 span (defense pp. 43-57) confirms **28**.

Three of the 28 are the dissertation's **own added frame**, not reproduced published text:
2 in the italic preface (`:18`) and 1 in the recap subsection heading (`:86`, "The MTLnet
framework"), both of which Appendix B separately declares as additions in the same section.
The reproduced-text total is therefore **25**, and its classes are 21 prose (23 − 2 preface)
+ **1 subsection heading** (`:122`, "Baseline: MTLnet with DGI", which *is* reproduced
published structure) + 1 caption + 2 table headings.

- The **source's** current 25 and its four-way breakdown match this census exactly. ✓
- The **built** 24 does not: its breakdown is 21 + 1 caption + 2 table headings, which omits
  `:122` and undercounts by one. See N-4.

The 2 residual capital-N sites (`:38`, `:248`) are both `ST-MTLNet (\textit{Spatial-Temporal
MTLNet})` — the proposed model's published expansion, which the entry explicitly reserves.
✓

**"No quantity, claim, or reference is affected" — verified on all three:**
- Citation keys unchanged: `silva2025mtlnet` and `paiva2026stmtlnet` are the only
  mtlnet-bearing keys, both lowercase-`net`, both cited and both resolving. ✓
- Figure filename unchanged: `figures/cbic_mtlnet_arch.png`, referenced from
  `3_cbic.tex`, present on disk under that exact name. ✓
- Quoted titles unchanged: the CoUrb entry keeps `{ST-MTLNet}: Representa{\c{c}}{\~o}es
  Espa{\c{c}}o-Temporais…` as published, and the preface at `4_courb.tex:18` quotes the
  Portuguese title verbatim with the published casing. ✓
- No number moved: no quantity appears on any of the 28 lines other than the table headings,
  which carry column names only. ✓

### 4.7 Appendix A.2 removal is clean

- `0_main.tex` includes exactly five appendices (A-E); no A.2 file remains in the include
  list.
- Appendix A renders as one unsectioned statement (defense p88 / final p86): no "A.1", no
  "A.2", no section numbering, and the TOC lists Appendix A with no sub-entries while
  B still shows B.1-B.5.
- Zero occurrences of "BRACIS" anywhere in `src/` (source or comments) and zero on any
  rendered page of either build.
- Dangling-reference lint across all `src/**/*.tex`: **zero** `\ref`/`\autoref`/`\nameref`
  targets without a matching `\label`. Both builds show **zero** `??` markers.
- Appendix A's platform counts were spot-reproduced live: `src/` holds exactly **192**
  Python modules and **28,644** LOC, and `src/losses/` holds **21** `loss.py`
  implementations — matching the appendix's "192-module, 28,644-line source tree" and
  "twenty-one multi-task loss and gradient-balancing methods". The "thirteen multi-task
  backbone architectures" is 13 real subdirectories under `src/models/mtl/` (14 entries
  minus `__pycache__`), and "eight … embedding engines" is 8 under `research/embeddings/`.
  ✓

### 4.8 Bibliography font

Per-span measurement on rendered pages: bibliography pp. 81-85 set at **11.96 pt**,
identical to body p60's **11.96 pt**, with only 12 characters of page furniture at 9.96 pt
per page. The `\footnotesize` wrapper is gone and the bibliography sets at body size, as
`0_main.tex:393-395` records. ✓

### 4.9 Citation audit — references new to the changed appendices

Each was resolved against the source of record **and** opened this session; the citing
sentence was checked against what the source says.

| key | identifier resolved | attributes | claim located |
|---|---|---|---|
| `luca2021mobilitysurvey` | Crossref `10.1145/3485125` | Luca, Barlacchi, Lepri, Pappalardo; *ACM Comput. Surv.* 55(1), pp. 7:1-7:44, 2021 — matches the bib entry and the rendered entry [3] | **Full text fetched and read.** p21, §"Privacy": DL models raise privacy issues in training as well as prediction, and in the training phase the risk of leaking private data is high regardless of the task, as the portions of information used cannot be controlled directly. Appendix E's sentence at `:53-56` is a faithful paraphrase, not a strength drift. ✓ |
| `wongso2025massivesteps` | arXiv 2505.11239 landing page opened; OpenAlex record | Wongso, Xue, Salim, 2025; title matches; rendered entry [62] carries the arXiv id | Cited for the Istanbul collection's identity and for cross-city evaluation; the card and abstract support both. ✓ |
| `sokolova2009measures` | Crossref `10.1016/j.ipm.2009.03.002` | Sokolova & Lapalme; *Information Processing & Management* 45(4), pp. 427-437, 2009 — matches rendered entry [64] exactly | Cited for macro-F1 counting classes equally. Full text is closed access (Unpaywall, S2, PMC, TDM all returned no OA copy) — see COULD-NOT-VERIFY. |
| `kohavi1995crossval` | OpenAlex, via re-deposit DOI `10.5281/zenodo.19712698` | Kohavi 1995, pp. 1137-1143 — matches the rendered entry [67] pagination and year | Cited conventionally for k-fold cross-validation. Original IJCAI-95 landing page not reachable — see COULD-NOT-VERIFY. |
| `pedregosa2011sklearn` | Semantic Scholar via DOI `10.5555/1953048.2078195` | *J. Mach. Learn. Res.* **12**, pp. **2825-2830**, 2011 — matches rendered entry [68] exactly | Cited for the library and the user-grouped splitter. `2_fundamentals.tex:573` already records the author's single-cite ruling (the splitter is a 2021 feature; the 2011 paper stands for the library and the splitter behaviour is stated defensively in prose). Consistent. ✓ |
| `cho2011gowalla` | rendered entry [12]; Crossref `10.1145/2020408.2020579` resolved earlier | Cho, Myers, Leskovec; KDD 2011, pp. 1082-1090 | Cited in Appendix E as the collection reference for the older SNAP release. ✓ |
| `jure2014snap` | rendered entry [73], SNAP page fetched | Leskovec & Krevl, 2014 | Same. ✓ |
| own papers | Crossref `10.5753/courb.2026.22960` → Paiva, Silva, dos Santos, Silva; *Anais do X Workshop de Computação Urbana (CoUrb 2026)*, pp. 323-336, SBC. Crossref `10.21528/CBIC2025-1191324` → Silva, Almeida, Paiva, Santos, Silva, Sousa; *Anais do XVII CBIC*, pp. 1-8 | both match their bib entries and the preface text at `4_courb.tex:18` | ✓ |

Bibliography lint: 99 defined keys, 0 duplicates, 0 cited-but-undefined, 98 cited, 98
rendered, 0 unresolved-reference markers in either build.

### 4.10 Never-cite sweep

Swept both builds and all printed source text for the eight forbidden values (STAN
v4-collapse 34.46/38.96; ReHDM v2 66.06/54.65/65.68/55.82; old non-overlap Markov-1
47.01/42.96). **One numeric hit, and it is not a never-cite violation:** `54.65` appears at
`5_mobiwac.tex:471` (defense p70 / final p65) as the Istanbul check-in-level cell of the
representation-comparison table. Its provenance is a different file —
`docs/results/closing_data/baseline_compare/istanbul_check2hgi_sc.json`, `macro_f1_mean:
54.649`, `macro_f1_std: 0.562` — confirmed by reading the JSON. Coincidence with the
superseded ReHDM v2 Arizona figure; no forbidden row is cited. ✓

---

## 5. COULD NOT VERIFY

Fail-closed: these are reported as unverified, not as verified or as defects.

1. **The CC0 deed text at the footnoted address.** `creativecommons.org` is outside the
   sandbox allowlist (proxy 403). The CC0 claim itself is verified from the Figshare API
   record, which carries the same licence name and the same deed URL, so the appendix's
   substantive claim stands; what I could not do is read the deed at that address.
2. **The Figshare HTML landing page** (`figshare.com/articles/dataset/gowalla_data/22126586`,
   footnoted at `5_mobiwac.tex:55`, defense p59). Blocked (proxy 403). The API record for
   the same article resolves and matches, so the deposit exists and carries CC0; the
   human-facing page was not opened.
3. **`sokolova2009measures` full text.** Closed access — Unpaywall, Semantic Scholar, PMC
   and Crossref TDM all returned no retrievable copy, and `doi.org` is blocked. Bibliographic
   attributes are confirmed against Crossref, so the reference is real and correctly
   described; the specific claim (macro-F1 as the unweighted mean of per-class F1) was
   **not** located in the source this session. `2_fundamentals.tex:530` records an earlier
   "VERIFIED PDF" by the author. Treat as author-verified, not gate-verified.
4. **`kohavi1995crossval` original venue text.** The IJCAI-95 proceedings page is not
   reachable from here; the work is confirmed to exist via a re-deposit identifier with
   matching pagination. `2_fundamentals.tex:575` already carries the author's own
   "claim PLAUSIBLE (Zenodo re-deposit id), author to confirm original IJCAI-95 text" note.
   That note is still correct and still open.
5. **`www.jmlr.org` and `dblp.org`** are blocked, so the scikit-learn volume and pagination
   rest on the Semantic Scholar record (v.12, pp. 2825-2830) rather than on the publisher
   page. arXiv's API and one Semantic Scholar endpoint rate-limited (429) during the
   session; the arXiv HTML landing page was opened successfully instead.
6. **Whether the program requires a formal human-subjects determination for secondary
   analysis of public data.** This is a question for PPGCC, not a fact in any repository or
   public record. Appendix E already frames it that way and says where it would go. Not a
   defect; recorded because it is the appendix's own open item and no reviewer can close it.
7. **The region-level revisit share as a *quotable* number.** B-1's 62.88 % is my
   reproduction, not a committed value. Under the guardrails it cannot go into prose until it
   exists in a committed artifact. The author must run and commit it (or choose the delete
   option).

---

## 6. What the round claimed, and what I found

| the round's claim | verdict |
|---|---|
| Appendix A.2 removed | **Confirmed clean** — no residual sectioning, no dangling refs, no venue mention in either build. |
| Appendix D rewritten, every number traces | **Confirmed** — 45/45 table cells and every prose figure trace to the JSON and the two screen CSVs. |
| "Ceiling" retired for that quantity | **Confirmed** — all 19 residual uses are the surviving correct sense, labels, or disclosed filenames. |
| Appendix E new (~790 words) | **Mostly confirmed** — both licences verified at source; de-identification, restriction, taxonomy and precedent claims all verified. Two disclosure gaps (M-1 upstream address behaviour, M-2 gating). |
| MTLnet standardized in Ch.4 with a B errata entry | **Confirmed in source** — 25 reproduced-text sites, class counts exact, no key, filename, or quoted title altered. The audited build still prints 24 with the subsection heading omitted (N-4); corrected in source at 07:08:45, clears on rebuild. |
| Bibliography now sets at 12 pt | **Confirmed by measurement** — 11.96 pt, identical to body. |
| Cross-attention clause rescoped, value unchanged, inference narrowed | **Confirmed** — value verbatim from F50, prior claim supported by F50 and by `canon.py` + the head implementation, run-configuration difference corroborated. |
| Markov-floor paragraph rewritten to state a protocol asymmetry | **Confirmed for the asymmetry and all counts; FAILS on the revisit share (B-1).** |

## 7. Fix order

1. **B-1** — the Alabama revisit share. Blocks the gate. Choose: commit a region-level
   stride-1 measurement, switch to region persistence, or delete the sentence.
2. **M-3** — the ledger pointer for that number, in the same edit.
3. **M-1, M-2** — two clauses in Appendix E (upstream address behaviour; upstream gating,
   plus the reassuring fact that the copy used is not gated).
4. **M-4** — delete the stale two lines in `apx_d_ceiling.tex:112`.
5. **N-2** — one ledger line for the 4.9-to-10.3 derivation. Third time it has been raised.
6. **N-4** — no edit; already fixed in source at 07:08:45. Rebuild so the PDF stops printing
   the 24-site count.
7. **N-1, N-3** — optional polish.

Nothing above requires a re-run of any experiment. B-1 needs one small measurement committed,
or a sentence deleted; everything else is prose, comments, and one rebuild.

---

*Verified this session by: Crossref API, OpenAlex API, Semantic Scholar API, arXiv landing
page, Figshare API, Hugging Face API, GitHub API, the SNAP dataset page, full-text retrieval
of `10.1145/3485125`, per-span font measurement and page-by-page text extraction of both
current builds, and reproduce-first recomputation from `checkin_graph.pt` /
`sequences_next.parquet` for B-1. Nothing in this report is asserted from model memory.
Self-reported success is not trusted; the author audits independently.*


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
