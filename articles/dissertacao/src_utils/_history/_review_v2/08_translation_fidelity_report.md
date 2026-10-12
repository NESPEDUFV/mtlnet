# 08 · Translation fidelity checker — L5 gate report (CoUrb PT → EN)

**Reviewer:** persona `reviewers/08_translation_fidelity.md` (the mandatory L5 gate,
`AGENT_GUARDRAILS.md` §4). Read-only pass. Run 2026-07-26 on the current text, after the two
correction rounds. This gate had never been run on the current text.

**Target:** `src/chapters/4_courb.tex` (383 lines), rendered at `src/dissertacao.pdf` pp. 43–57
and `src/build/main_final.pdf` pp. 38–52.

---

## VERDICT

**L5 FAIL** — on one defect: a clause of the published methodology is inside a LaTeX comment
and does not render. It is a silent omission of published content from the reproduced body,
which is the persona's own fail condition ("silent omission/addition"). Everything else that
this gate exists to catch **holds**: zero number mismatches against the published record, zero
claim-strength drifts, and both errata corrections correctly applied and declared.

The fix is one line and mechanical. Nothing in the drift table below requires re-verifying a
result, and no reported number is wrong.

| Severity | Count | Findings |
|---|---|---|
| **BLOCKER** | 1 | F1 |
| **MAJOR** | 2 | F2, F3 |
| **MINOR** | 3 | F4, F5, F6 |
| **NIT** | 3 | F7, F8, F9 |
| **[UNVERIFIED]** | 0 | — |

Nine findings total. Eight of the nine concern dissertation-authored or declared-correction
prose; only F1 touches reproduced published text.

**Top 3 findings:** F1 (BLOCKER, commented-out published clause), F2 (MAJOR, an added
universal claim about a metric the tables do not report), F3 (MAJOR, the audited gain range
inserted into a Results paragraph that the published article never gave a range in, and
Appendix B does not declare it).

---

## 0 · Sources of record: which file is which, and how I determined it

The persona requires that I establish the version of record rather than assume it. I did, and
one thing changed as a result: **I obtained the published article itself**, which is not in the
repository.

| Artifact | Path / identifier | Role established |
|---|---|---|
| **The published record** | DOI `10.5753/courb.2026.22960`, retrieved this session (gold OA via Unpaywall → `sol.sbc.org.br/index.php/courb/article/download/42559/42326`), 14 pp. | **The version of record.** All numbers and claims below are quoted against THIS, not against the repo. |
| Repo PT source | `articles/CoUrb_2026/src/` (`main.tex` + `sections/*.tex` + `resultados/*.tex`) | The LaTeX that produced the published PDF. Verified equivalent to it (see below). |
| Repo EN translation | `articles/CoUrb_2026/src_en/` (same file structure, + `TRANSLATION_NOTES.md`) | A **derived translation**, not a record. `src_en/TRANSLATION_NOTES.md`:6-7 states it: "The Portuguese original is in [`../src/`](../src/); this folder is the English mirror." |
| The chapter under review | `src/chapters/4_courb.tex` | Re-typeset from `src_en/`, per its own header comment (:2-3). |

**How I established the direction of derivation** (three independent signals, not just the
`TRANSLATION_NOTES` assertion):

1. The published PDF is Portuguese in body, and `src/main.tex`:29 carries the Portuguese title
   that the PDF prints; `src_en/main.tex`:36 carries an English title that appears nowhere in
   the published record.
2. `src_en/main.tex`:16-22 adds `\addto\captionsbrazil{\renewcommand{\figurename}{Figure}...}`,
   a patch that exists only to un-Portuguese the auto-generated labels of the babel option the
   PT source set. A source tree does not patch itself into its own language.
3. `src_en/` retains Portuguese inside commented-out blocks byte-identically
   (`src_en/sections/related.tex`:8,16 — the HAVANA and Space2Vec `%` paragraphs are still in
   Portuguese), which is the signature of a translation that skipped non-rendering material.

**Verification that the repo PT source equals the published PDF** (so a PT-source quote is a
published quote): character-stream comparison after normalizing the SBC PDF's scattered
combining accents, `ı`-ligatures, and hyphenation, and removing the running header. Every claim
and number I cite below was additionally confirmed by direct string search in the published PDF
text. All 126 F1 cells of the repo PT tables appear in the published PDF (the PDF yields 130
`±` cells; the 4 extra are the four values the published *prose* repeats from the tables:
62,44±2,00 / 64,89±1,20 / 63,59±1,45 / 51,28±0,57). Dataset counts, every hyperparameter, and
the two errata claims were matched individually.

**Two facts about the published record worth recording, because the repo's own notes are silent
on one of them:**

- The published PDF's printed page numbers run **1–14**, not 323–336. The 323–336 range in the
  preface and in `references.bib` is the *anais* pagination, which the article PDF as served by
  SBC SOL does not print. This is normal for SBC volumes and I raise it only so nobody "fixes"
  the preface against the PDF's own footer. Page 6 of the PDF additionally prints "192" as an
  in-text artifact of the `\mathbb{R}^{192}` display, not a page number.
- The published PT article cites the Gowalla dataset in its Results section as **[Liu et al.
  2014]** (published PDF p. 9: "o *dataset* Gowalla [Liu et al. 2014]"), the CIKM
  location-recommendation paper. The chapter replaced it with `cho2011gowalla,jure2014snap`.
  That correction is real and is declared (Appendix B, `apx_b_errata.tex`:496-501). Verified
  correctly applied at `4_courb.tex`:258.

---

## 1 · The drift table (published PT ↔ chapter EN)

Every row quotes both languages verbatim. "Published" = the retrieved PDF of record;
`src/` and `src_en/` line numbers are given for locating the same text in the repo.

### F1 — BLOCKER · Silent omission: a published clause sits inside a LaTeX comment and does not render

**Location:** `src/chapters/4_courb.tex`:175 and :187 (§4.3.5.1 POI Encoder).
Rendered: `src/dissertacao.pdf` p. 51; `src/build/main_final.pdf` p. 46.

The round-4 fix for an overfull hbox (ledger row B10, REV-021) reversed the clause order of the
POI Encoder sentence and inserted a 12-line explanatory comment between the two halves of the
paragraph. The second half of the *content* was left appended to the last comment line, so it
is commented out.

`4_courb.tex`:175 (verbatim, the line ends there):

> `The category \textit{embedding} $\mathbf{E}_{\text{POI\_category}} \in \mathbb{R}^{64}$ is generated by the POI Encoder, which is trained independently. The POIs are organized into a spatial graph`

`4_courb.tex`:187 (verbatim — note the leading `%`):

> `% needed 468.2 pt; the reordered run-up puts the whole expression at about 227 pt. built by Delaunay triangulation over the geographic coordinates, with edges weighted by logarithmic decay of the Haversine distance and penalization for connections between distinct counties (GEOIDs).`

**Published PT** (PDF p. 9; `src/sections/metodology.tex`, POI Encoder subsection):

> "Os POIs sao organizados em um grafo espacial construído por Triangulação de Delaunay sobre as coordenadas geográficas, com arestas ponderadas por decaimento logarítmico da distância Haversine e penalização para conexões entre condados (GEOIDs) distintos."

**EN source of record** (`src_en/sections/metodology.tex`:106): the same sentence, complete.

**What the reader gets instead** (quoted from `dissertacao.pdf` p. 51, and identical on
`main_final.pdf` p. 46):

> "The category embedding E_POI_category ∈ R^64 is generated by the POI Encoder, which is trained independently. The POIs are organized into a spatial graph
> Over this graph, random walks (random walks) are executed following the Node2Vec methodology (27)."

The sentence ends mid-clause at "a spatial graph", with no period, and the next sentence begins
on a new line. Three published method facts are lost with it: the graph is built by **Delaunay
triangulation over the geographic coordinates**, edges are weighted by **logarithmic decay of
the Haversine distance**, and connections between **distinct counties (GEOIDs)** are penalized.
Confirmed absent from both rendered builds by string search: "Haversine" = 0 occurrences,
"GEOIDs" = 0, "Delaunay triangulation over the geographic coordinates" = 0. All three are
present in the published record and in `src_en/`.

Severity is BLOCKER on two grounds, not one: it is a silent omission of published content from
a chapter presented as a faithful reproduction, and it is also a visible broken sentence on a
defense page. Note that it also makes the ledger's own B10 justification false as applied
("Every content word is preserved") — the ledger describes an edit that was not the edit
performed.

Direction: move the text after `at about 227 pt.` on :187 back onto :175, or onto its own
uncommented line, so the sentence closes.

---

### F2 — MAJOR · Added universal claim about a quantity the tables do not report ("higher mean F1 in every category and state")

**Location:** `4_courb.tex`:284 (the category-table lead sentence; ledger C5, declared in
Appendix B as one of the three table lead sentences). Rendered `dissertacao.pdf` p. 54.

**Chapter (added, no published counterpart):**

> "The results of the POI Category Classification task are presented in Table \ref{tab:courb:category}: the two ST-MTLNet variants reach higher mean F1 than the original MTLNet in every category and state."

**Published PT** (PDF p. 8): the corresponding sentence is only
"Os resultados da tarefa de classificação de categoria de POI são apresentados na Tabela 2." —
the lead clause after the colon is dissertation-authored.

Two problems, in order of weight.

1. **The metric name is wrong for this table, in the direction that matters.** Table 4.2 reports
   the *Average F1-Score per category* (its own caption; the published caption is "F1-Score
   Médio (%) por modelo e estado"). "Mean F1" in this dissertation's registry is a different
   quantity: GLOSSARY §4 defines **macro-F1** as "Mean of per-category F1", and the frame uses
   "mean" for the average over folds/seeds. The added sentence reads as a claim about a
   *mean-over-categories* score, then says it holds "in every category" — the claim is
   internally incoherent as phrased, and it is the only place in the chapter where a
   metric name not used by the published article is asserted.
2. **It is a bare universal without its convention.** WRITING_LAW §3 requires every number and
   claim to carry its convention (which metric, which selection rule, n). The published
   universal it paraphrases carries one; this one does not, and it is stated *before* the reader
   reaches the table.

I verified the underlying arithmetic and the universal is true on the values: in all 21
category-state rows of Table 4.2, both variant cells exceed the MTLNet cell (checked cell by
cell from the chapter's own table). So this is a wording defect, not a false claim, which is
why it is MAJOR and not BLOCKER.

Direction: name the table's own metric, e.g. "reach a higher Average F1-Score per category than
the original MTLNet in every category-state combination", or delete the clause and let the
published sentence stand (the next sentence already states the 21-of-21 result).

The same defect class, milder, in the sibling lead sentence at `4_courb.tex`:327 (ledger C6):
"the proposed variants keep the higher mean F1 in most category-state combinations, while the
*baseline* retains a few categories." Same "mean F1" naming; "a few categories" is vaguer than
the audited 6 it summarizes. Fold into the same fix.

---

### F3 — MAJOR · Errata number inserted into a Results paragraph that carried no range in the published article, and Appendix B does not declare that placement

**Location:** `4_courb.tex`:284, third sentence. Rendered `dissertacao.pdf` p. 54.

**Chapter:**

> "The average gains per state are 20.2 to 22.0 percentage points, considering the better of the two spatial encoders in each combination."

**Published PT — the Results section states no gain range at all.** I searched the published
record's entire category-results section (between "4.2 Classificação de Categoria de POI" and
"4.3 Predição do Próximo POI") for `pontos percentuais`, `ganhos médios`, and `20 a 24`: zero
occurrences. The published article gives the range in exactly three places, and Results is not
one of them: the Abstract/Resumo (PDF p. 1), the Introduction (PDF p. 2, `src/sections/intro.tex`:16),
and the Conclusion (PDF p. 11, `src/sections/conclusion.tex`:3).

The chapter states it in three places too — `:35` (Introduction), `:284` (**Results**), `:375`
(Conclusion) — but the third slot is the Results section, not the abstract, because the abstract
was legitimately dropped (Appendix B, `apx_b_errata.tex`:92-97). So a corrected number migrated
into a section of the reproduced article that never carried it.

Why this matters and is not pedantry: Appendix B's Chapter 4 errata row (`apx_b_errata.tex`:256-260)
tells the reader the correction applies to "Introduction, results, and conclusion" — which
describes the *chapter*, not the published article, and so silently asserts that the published
Results section carried the defective range. It did not. The declaration is inaccurate about the
published record in the one appendix whose whole job is to be exact about it. Separately, the
ledger's own A2 row lists the same three sites, so the ledger inherits the same inaccuracy.

The number itself is correct and correctly sourced: `slides/judge_feedback.md`:11 gives the
per-state best-of-two means FL +20,24 / CA +20,91 / TX +21,98, and the "better of the two
spatial encoders" qualifier is exactly the disclosure that file demands ("precisa estar no
rodapé (ex.: '20–24 pp considerando o melhor dos dois encoders por linha')"). The 22.0 endpoint
is the sanctioned rounding of 21,98. **No number is wrong here.** The defect is placement plus
an Appendix B sentence that misdescribes the published article.

Direction (author's call, two clean options): (a) keep the sentence at :284 and correct Appendix
B to say the published article carried the range in its abstract, introduction and conclusion,
and that the chapter reports the audited range in its introduction, results and conclusion
because the abstract is not reproduced; or (b) drop the :284 sentence, leaving the corrected
range in the two sections the published article actually used.

---

### F4 — MINOR · "16 of the 21" → "15 of the 21": correctly applied, correctly declared, one verb consequence to note

**Locations:** `4_courb.tex`:327 (Results) and :375 (Conclusion).

**Published PT** (PDF p. 9, Results): "os modelos espaço-temporais superam o MTLNet original em
**16 das 21** combinações avaliadas." (PDF p. 11, Conclusion): "que **vence em 16 das 21**
combinações avaliadas". Also the Abstract/Resumo: "em **76%** das combinações".

**Chapter** (:327): "counting the better of the two spatial encoders per combination, the
spatio-temporal models outperform the original MTLNet in **15 of the 21** evaluated
combinations, with one additional technical tie in *Outdoors* in Florida, where the *baseline*
mean exceeds the best variant by 0.02 percentage points, a gap within one standard deviation."

This is the audited count from `slides/judge_feedback.md`:12 ("contagem estrita por média
(best-of-two > baseline) dá **15/21**... O caso ambíguo é **Florida Outdoors**: baseline 21,61
vs Sphere 21,59 — baseline ainda vence por 0,02 pp (dentro de σ ≈ 1–2 pp)"), it is declared in
Appendix B (`apx_b_errata.tex`:250-254), and I reproduced it independently from the chapter's own
Table 4.3: best-of-two exceeds the baseline in exactly 15 rows; the baseline holds 6 (FL
Outdoors by 0.02, FL Travel by 19.47, CA Entertainment by 2.10, CA Nightlife by 1.90, CA
Outdoors by 0.17, CA Travel by 8.23). The 21,61 / 21,59 pair is present in the published PDF.
Correct, and the "76%" of the published abstract falls away with the abstract.

Two things to flag, neither a number error:

- **The verb is now unbound at a finer grain than the published one was.** WRITING_LAW §3 binds
  "outperforms" to a paired superiority test. This chapter reports no test anywhere (I searched:
  zero occurrences of Wilcoxon, *t*-test, TOST, p-value, "significant", "confidence interval",
  "paired"), because the published study ran none. Under the reproduction rules that is correct
  and the preface time-indexes it. But the chapter *also* now adjudicates a single 0.02 pp cell
  as a "technical tie... within one standard deviation" — a per-cell significance judgment made
  in dissertation-authored prose, with no test, sitting beside an "outperforms" verb for the
  other 15. A banca member who has read Chapter 5's TOST discipline may ask why the tie
  threshold here is one standard deviation and where that rule is stated. The honest answer is
  that `judge_feedback.md` proposed it; the chapter does not say so.
- **CA Outdoors is 0.17 pp**, an order of magnitude tighter than the other four real losses and
  well inside its own σ (±0.81 / ±1.70 / ±2.46). By the same one-standard-deviation reasoning
  applied to FL Outdoors it would also be a tie, which would make the count "15 wins, 2 ties, 4
  losses". I raise this **not** as a correction to make — the audited 15/21 + 1 tie is the
  settled, sourced number and I am not proposing to recount it — but because the asymmetry is
  visible in the printed table and is the obvious follow-up question.

Direction: no number change. Consider one clause naming the tie criterion as the internal
audit's, or accept the question as answerable aloud.

---

### F5 — MINOR · "wins" → "outperforms the baseline": a verb substitution that is fine, and one it exposes

**Location:** `4_courb.tex`:35 (Introduction) and :375 (Conclusion).

**Published PT** (PDF p. 2): "o modelo proposto **vence** na maioria dos cenários".
**Chapter** (:35): "the proposed model **outperforms the *baseline*** in most scenarios".

Declared (Appendix B `apx_b_errata.tex`:262-264; ledger A3) and justified: WRITING_LAW §2 bans
"wins"/"beats" as verdict verbs. Claim strength is unchanged — "most scenarios" is preserved
verbatim, and the substituted verb is not stronger in English than *vencer* is in Portuguese.
Zero occurrences of "wins"/"won"/"beats" remain in the chapter. This holds.

What it exposes: at `:327` the chapter reproduces "outperforming DGI by a wide **margin**"
(published: "superando com ampla **margem** o DGI", PDF p. 9). GLOSSARY §4 reserves "margin" for
the TOST non-inferiority margin and directs representation differences to be called "gaps". This
is faithfully reproduced published prose, so under the time-capsule rule it should stay; I note
it only so the concordance checker does not later "fix" it and so nobody reads it as a statistical
margin. One occurrence.

---

### F6 — MINOR · "mostra"/"mostram" → "shows" is faithful here, but the Conclusion's evidential chain is worth a second look

I checked every hedge and evidential verb pair across all five sections. The inventory maps 1:1
in kind and in count, with no strengthening: PT `indicam`→"indicate", `sugere/sugerindo`→
"suggests/suggesting", `pode/podem`→"may", `poderia`→"could", `permitiria`→"would allow",
`tende/tendem`→"tends/tend", `ainda assim`→"even so", `mesmo com`→"even with",
`majoritariamente`→"mostly", `consistentemente`→"consistently", `sempre`→"always",
`todas/todos`→"all", `apenas/somente`→"only". Counts per section: intro 8/8, related 3/3,
methodology 14/13 (the one-token difference is PT `demonstrado` + `indica` collapsing onto
"shown"/"indicates" with an "all" gained in an enumeration, not a hedge loss), results 17/19,
conclusion 14/16 (the surplus is English function words "still"/"only", not added certainty).

**No `sugere`/`indica` was rendered as "shows" or "demonstrates" anywhere.** That is the drift
this gate exists to catch and it is absent.

Where PT does say `mostra`/`mostram`, EN says "shows" — correct, e.g. published Conclusion "A
comparação entre SIREN e Sphere2Vec-M também **mostra** que não há um único *encoder* espacial
universalmente superior" → chapter `:377` "also **shows** that there is no single universally
superior spatial *encoder*." Faithful.

The one thing I flag: the published Conclusion opens with the hedge "Os resultados obtidos nos
três estados avaliados **indicam** que sim" and the chapter renders it "indicate that it can"
(`:373`) — correct. But two sentences later the reproduced text says these results "**show**
that decomposing the representation ... allows capturing patterns that DGI, by itself, does not
model sufficiently" (published: "esses resultados **mostram** que"). Both are faithful
individually. As a pair in English the chain reads stronger than the Portuguese does, because
English "show" carries more evidential weight than *mostrar* does in BR academic register, where
it often functions closer to "display/present". This is a translation-register observation, not a
drift finding — the words map correctly. Recording it because it is exactly the kind of thing
the author should be able to defend aloud, and the answer ("the published Portuguese says
*mostram*") is a good one.

---

### F7 — NIT · Terminology landing: correct, with one deliberate divergence to keep declared

Sweep of `4_courb.tex` against GLOSSARY §1/§3 (comments stripped):

| Registry rule | Result |
|---|---|
| never "venue" | 0 occurrences ✓ |
| never "event" for check-in | 0 ✓ (only "check-in", "visit") |
| never "area"/"cell" for region | 0 ✓ |
| "place" / "POI" | used; POI expanded at first use (`:20`) ✓ |
| next place named once to delimit | `:13`, preface, exactly once ✓ |
| no em-dash | 0 ✓ |
| no contractions | 0 ✓ (4 apostrophes are all possessives: "model's", "frame's", "user's" ×2) |
| no repo codenames | 0 ✓ |
| "this paper/work/article" swept to "this chapter" | 0 leftovers ✓ (11 substitutions, ledger B1) |

The PT→EN task-name landing is handled the way the persona requires — not by renaming the
published task inside the reproduced body, but by a preface bridge (`:13`): "As in Chapter 3, the
term ``Next-POI Prediction'' used here denotes the frame's *next category* task (the category of
the next visited place), not the exact-place task the dissertation calls *next place*." Correct,
and it matches GLOSSARY §1's per-paper mapping table.

The deliberate divergence: **the chapter uses `MTLNet` (46 times) where the frame uses `MTLnet`**.
GLOSSARY §2 registers the artifact as **MTLnet**; Chapters 1, 2, 5, 6 and Appendix B all use
`MTLnet` exclusively (4 / 3 / 3 / 2 / 1 occurrences, zero `MTLNet` outside quoted material).
Chapter 4 declares the exception in-text at `:84`: "the published paper typesets the name as
MTLNet, and this chapter preserves that form", which is the right call under the time-capsule
rule and the right place to say it. Verified the published PDF does print `MTLNet`. Consistent
and declared; no action. Flagging only so a future concordance pass does not "normalize" it.

---

### F8 — NIT · Additions and omissions sweep: eight additions, all present, all declared; count now correct

I ran an 8-gram diff of the chapter against the union of `src_en/main.tex`, `sections/*.tex` and
`resultados/*.tex`, then confirmed each hit against the published PDF. Result: the chapter's
non-published content is exactly the eight items the ledger lists (C1–C8), and Appendix B
(`apx_b_errata.tex`:282-296) enumerates all eight. The round-4 correction of the earlier
"three marked additions" undercount is confirmed applied and accurate.

| # | Addition | At | Declared |
|---|---|---|---|
| C1 | Chapter preface (reproduction statement + DOI + authorship + protocol note + time-index + task bridge) | `:13` | ✓ B §B.2 |
| C2 | §4.2.5 "The MTLnet framework" recap subsection | `:81`-`:86` | ✓ |
| C3 | Sample-stratified split disclosure | `:238` | ✓ |
| C8 | Single-random-seed disclosure | `:238` | ✓ |
| C4 | Dataset-table lead ("Texas concentrates the largest volume…") | `:258` | ✓ |
| C5 | Category-table lead | `:284` | ✓ (see F2) |
| C6 | Next-POI-table lead | `:327` | ✓ (see F2) |
| C7 | Figure 4.2 reading instruction | `:278` | ✓ |

**Omissions:** the only content omissions are the front matter (title block, authors, address,
abstract, `\resumo`, Acknowledgments) and the commented-out source blocks. Front matter is
declared as a class in Appendix B (`:92-97`), which names the CoUrb `\resumo` and the CoUrb
acknowledgments explicitly. I verified the acknowledgments are genuinely absent from the chapter
(no "MCTI", no CNPq project number 421548/2022-3) and that this is the declared intent, not a
slip. The commented blocks do not render in the published article either
(`src/sections/related.tex`:8,16 — HAVANA, Space2Vec-grid — and `conclusion.tex`:13, the
alternative future-work paragraph); I confirmed none of them appears in the published PDF.
Correct to drop, correctly not itemized.

**No other published sentence is missing** apart from F1. Every claim-bearing sentence of the
published Results, Conclusion, Introduction and Related Work has a counterpart in the chapter,
and I matched each of the four table-derived values the published prose repeats.

---

### F9 — NIT · Two protocol disclosures (C3, C8) verified firsthand against the code, and they are correctly hedged

These are additions, so this gate has to check they are true, not just declared.

**Chapter `:238`:** "The split is stratified by sample, not by user, so the *check-ins* of one
user may appear in both training and validation; Chapter 5 adopts a stricter user-disjoint
protocol. The released code of record pins a single random seed, so the five folds constitute one
repetition of the experiment rather than several, and the reported standard deviations are the
spread across folds at that seed; Chapter 5 repeats its five-fold experiment at four random
initializations."

Verified in the author-provided CoUrb-era codebase at `/Users/vitor/Desktop/mestrado/temp/tarik-new`
(`PoiMtlNet_Novo/src/etl/mtl/create_fold.py`): `random_state: int = 42` at :162;
`torch.manual_seed(random_state)` :180; `np.random.seed(random_state)` :181; both splitters plain
`StratifiedKFold(n_splits=k_splits, shuffle=True, random_state=random_state)` at :226 and :229,
**neither taking a `groups=` argument**; `pipelines/mtlnet_trainer.py`:52-57 calls `create_folds`
without overriding `random_state`. At :189-191 the code reads `userid`, and at :198-199 drops it
from the feature frame before splitting. A repo-wide grep of project code (excluding `.venv`)
finds **no** `GroupKFold` or `StratifiedGroupKFold` anywhere; the only other splitters,
`src/etl/next/fold.py`:34 and `src/etl/category/fold.py`:32, are also plain `StratifiedKFold`.
Both disclosures are accurate.

The hedging is also right, and worth crediting explicitly since it is the kind of thing that
usually goes wrong: the prose says "the released **code of record** pins" rather than claiming
the published runs used that file, and it keeps the literal `42` out of the text (a fact about
the code, not a reported parameter of the paper). The chapter's own source comment at :253-256
records that this restraint was deliberate. Nothing to change.

---

## 2 · Terminology-landing report (summary)

Landing is clean. PT terms reach the registry's canonical EN names, and the two places where the
published article's own vocabulary conflicts with the registry are handled by declaration rather
than by silent renaming — which is what GLOSSARY's own preamble instructs ("When a definition
here conflicts with a source paper's local usage, the chapter keeps the paper's usage and the
frame uses this registry"):

- `Predição do Próximo POI` → "Next-POI Prediction" (paper's term) **+ preface bridge** to the
  frame's *next category*. ✓
- `Classificação de Categoria de POI` → "POI Category Classification". Matches GLOSSARY §1
  "category classification". ✓
- `check-ins` → "check-ins" (never "events"); `local`/`POI` → "place"/"POI" (never "venue");
  `embedding` kept as the loanword the published paper uses, italicized as in the source. ✓
- `MTLNet` kept in the paper's typesetting, declared at `:84`. ✓ (F7)
- `margem` → "margin" in reproduced prose, registry-reserved elsewhere. Left as published. ✓ (F5)

The one term that does **not** land on the registry is "mean F1" in the two dissertation-authored
lead sentences — it is not a registered metric name and the table reports Average F1-Score per
category. That is F2.

---

## 3 · Errata-policy check result: PASS

The persona requires that the two known published errata be either corrected with an Appendix-B
note or reproduced verbatim with a note, and never silently either way.

| Erratum | Published value (verified in the PDF of record) | Chapter | Appendix B | Verdict |
|---|---|---|---|---|
| Win count on the sequential task | "16 das 21" (PDF pp. 9, 11); "76%" (PDF p. 1) | "15 of the 21 ... with one additional technical tie" (`:327`, `:375`) | `:250-254` ✓ | **Corrected + declared** |
| Category gain range | "ganhos médios de 20 a 24 pontos percentuais" (PDF pp. 1, 2, 11) | "20.2 to 22.0 percentage points, considering the better of the two spatial encoders" (`:35`, `:284`, `:375`) | `:256-260` ✓ (but see F3 on the site list) | **Corrected + declared** |
| `silva2025mtlnet` bib entry (venue conflated, stale "Submetido", author list) | published article's bibliography | not a chapter-text change | `:480-485` ✓ | **Corrected + declared** |
| FL *Outdoors* baseline cell bolded in the published table | `\textbf{21,61 ± 0,99}` | bold **preserved** as published (`:342`) | `:269-271` ✓ | **Preserved + declared** |
| Gowalla cited via [Liu et al. 2014] in the published Results | PDF p. 9 | replaced by `cho2011gowalla,jure2014snap` (`:258`) | `:496-501` ✓ | **Corrected + declared** |
| `church2017word2vec` → `mikolov2013word2vec` at the skip-gram site | published cites [Church 2017] (PDF p. 9) | `mikolov2013word2vec` (`:189`) | `:468-470` ✓ | **Corrected + declared** |
| `huang2023learning` → `huang2023hgi`, `rußwurm…` → `russwurm…` (ASCII key rename) | key spellings only | keys swapped, same works | `:67-73` covering sentence ✓ | **Declared as key consolidation** |

Nothing silently fixed, nothing silently reproduced. The Nash-MTL caveat remains deliberately
not added, by the author's standing ruling recorded in the ledger §E — correct to leave, and out
of this gate's scope.

Cross-checked the two audited numbers against their source of truth
(`articles/CoUrb_2026/slides/judge_feedback.md`:11-12, the file the reviewers' README names as
the CoUrb source) and reproduced both from the chapter's printed tables. They agree.

---

## 4 · Sections verified clean (coverage statement)

Full sentence-by-sentence alignment on claim-bearing text; paragraph grain on methods, as the
persona allows. Everything below was compared against the **published PDF of record**, with the
repo PT/EN trees used to locate line numbers.

| Chapter section | Grain | Result |
|---|---|---|
| Preface (`:13`) | sentence | Dissertation-authored frame material. Reproduction statement, DOI, pages, authorship + second-author role, protocol note, time-index, task bridge — all present, all declared. **Clean.** |
| §4.1 Introduction (`:17`-`:44`) | sentence | Clean except the two declared errata substitutions (F3, F5). Contribution list, GitHub footnote, roadmap all faithful. |
| §4.2 Related Work (`:48`-`:86`) | sentence | **Clean.** All four axes' claims, every cited system, all hedges map 1:1. §4.2.5 (`:81`) is a declared addition (C2). |
| §4.3 Methodology (`:88`-`:231`) | paragraph + every numeral | **F1 sits here** (§4.3.5.1, `:173`-`:200`). Otherwise clean: every equation, symbol, and hyperparameter matches (see below). |
| §4.4.1 Experimental Setup (`:236`-`:280`) | sentence | Clean; carries three declared additions (C3, C8, C4) and the Figure 4.2 instruction (C7), all verified true (F9). |
| §4.4.2 Category results (`:282`-`:323`) | sentence + every cell | Table cells clean; prose carries F2 and F3. |
| §4.4.3 Next-POI results (`:325`-`:368`) | sentence + every cell | Table cells clean; prose carries F4 and the F2 sibling. |
| §4.5 Conclusion (`:370`-`:383`) | sentence | Clean except the declared errata substitutions (F3, F4, F5); both limitation paragraphs and the future-work paragraph faithful. See F6 note. |

**Numbers: zero mismatches.** Every numeral in the chapter was checked against the published
record, digit by digit, in both directions.

- **All 126 F1 cells** of Tables 4.2 and 4.3 are digit-identical to the published tables,
  **including which cell is bold in each row** (63 category cells + 63 next-POI cells; value,
  standard deviation, and bold state all matched as triples). The FL *Outdoors* baseline bold is
  preserved exactly as published.
- **Dataset counts** (Table 4.1): 990,518 / 65,009 / 20,301; 2,535,573 / 148,314 / 36,106;
  3,355,419 / 135,570 / 37,522 — all nine present in the published PDF, locale converted only
  (PT `990.518` → EN `990,518`).
- **Hyperparameters**, each present once in both and nowhere altered: 64-d, 192-d,
  d_shared = 256, 9 × 192 = 1728, 9 × 64 = 576, L_h = 9, 7 classes, 8 attention heads, 4 layers,
  three MLPs of 2/3/4 layers, four shared residual blocks, τ = 0.15, ≤10 km / ≥70 km, α = 0.5,
  S = 16, 10 km–10,000 km, 5 folds, 80%/20%, "fewer than five visits", February 2009–October 2010.
- **No p-value, confidence interval, or test statistic exists** in either the published article
  or the chapter, so there is none to mismatch.

**What reads well and should not be touched.** The preface is the strongest thing in this
chapter: in five sentences it states the reproduction, the DOI, the second-author role, the
weaker split, the time-indexing, and the task-name bridge — a banca member who reads only that
paragraph cannot be misled about what Chapter 4 is or what it claims. The two protocol
disclosures at `:238` are model instances of the honesty law: they volunteer weaknesses the
published paper left implicit, they are recoverable from the released code, and they are hedged
to exactly what the evidence supports rather than to what would sound stronger. The Portuguese
title, venue and DOI are reproduced correctly. The decision to keep `MTLNet` and the published
bold cell, and to declare both rather than normalize them, is the right reading of the
time-capsule rule.

---

## 5 · Out-of-scope handoffs (one line each)

- **Number auditor / concordance:** the "mean F1" metric naming at `:284` and `:327` (F2) is
  also a metric-registry inconsistency against GLOSSARY §4, worth confirming from that angle.
- **Claim-honesty auditor:** the one-standard-deviation tie criterion at `:327` (F4) is a
  significance judgment made without a named test; the CA *Outdoors* 0.17 pp asymmetry is its
  visible consequence.
- **Visual/presentation:** F1 renders as a sentence broken mid-clause on `dissertacao.pdf` p. 51
  and `main_final.pdf` p. 46; it will be visible to a page-proof pass as well as to this one.
- **Citation auditor:** the published article's `[Church 2017]` at the skip-gram site is a real
  mis-citation in the record (the Church piece is a commentary column, not the skip-gram method);
  the chapter's replacement with `mikolov2013word2vec` is declared, but the substitution is a
  content change inside reproduced prose and may deserve a sentence rather than the covering
  key-consolidation clause.
- **Build note (not a finding):** the preface's "pages 323 to 336" is the anais pagination; the
  article PDF as served by SBC prints 1–14. Both can be right; do not reconcile one to the other.

## 6 · Open questions only the author can answer

1. **F3 placement:** keep the audited gain range in the chapter's Results section and correct
   Appendix B's site list, or drop it from Results so the corrected number sits only where the
   published article carried a range?
2. **F4 tie criterion:** state in-text that the one-standard-deviation technical-tie reading
   comes from the internal audit, or leave it and answer the question aloud at the defense?
3. **F2 wording:** replace "mean F1" with the table's own "Average F1-Score per category", or
   delete the two added lead clauses and let the published sentences introduce the tables?

## 7 · What this pass could not verify

Nothing material. The published record was obtained and read, both builds were read, the
codebase claims were checked firsthand, and both audited numbers were reproduced from the
printed tables. No finding in this report rests on an unverified assumption, and no `[VERIFY]`
or `[UNVERIFIED]` flag is carried forward.

One limitation to state plainly: the published PDF's text layer scatters combining accents and
`ı`-ligatures, so all Portuguese comparisons were run on an accent-stripped, whitespace-stripped
character stream. That method cannot detect a divergence that is purely diacritical. It detects
every word, number, and claim difference, which is what this gate is for.

---

*Read-only pass. No file was edited and no build was run. Findings only; the author rules on each.*


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
