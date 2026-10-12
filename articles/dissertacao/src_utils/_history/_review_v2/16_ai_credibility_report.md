# 16 · AI-credibility reviewer report (v2) — the external-perception simulation

> Persona: `reviewers/16_ai_credibility.md`. Two readers in one report: (1) the **screener**
> (a 2026-grade detector pass, Pangram-class, with the hybrid-text windowing caveat) and (2) the
> **suspicious expert** (a well-read CS examiner keying on gestalt). Evidence base:
> `reviewers/research/ai_detection_landscape_2026-07-20.md` + `reviewers/research/ai_writing_evidence_2026-07-18.md`,
> refreshed this session (§8). **Read-only.** I edited no file except this report; I ran no git
> command and no build.
>
> **Scope of this run.** `src/dissertacao.pdf` (102 pp, defense build) and
> `src/build/main_final.pdf` (97 pp, AcademicoPG build), both written 2026-07-27 02:39, against
> `src/chapters/*.tex` and `src/0_main.tex` at the same timestamps. Both PDFs were text-extracted
> and page-mapped; every locus below carries `file:line` **and** the page in BOTH builds.
>
> **Protocol note on persona 03.** The persona file says I do not re-run 03's counted sweeps and
> reference its report instead. That is not available for the passages this round is about:
> `_history/_review_v2/03_style_auditor_report.md` is dated 2026-07-26 01:36, against a 94/89-page build,
> and it contains **zero mentions of Appendix D, Appendix E, or the label-history rename**
> (verified by grep). Appendix E did not exist when 03 ran; Appendix D was rewritten after it. So
> for the three new/rewritten passages I measured the residual myself and say so at each number.
> 03's chapter-level figures are cited, not re-derived.
>
> **Mission framing.** AI use here is disclosed and legitimate. The job is not camouflage; it is
> that the text earns full credibility anyway. Nothing below recommends evading detection of
> disclosed use.

---

## VERDICT (per channel)

**SCREENER RISK: MEDIUM** (windowing caveat stated, as always). Unchanged from v1 in level and in
reason: the frame chapters and all five appendices are disclosed *substantive generation from
author-approved outlines*, which is the mode NeurIPS 2026 verified a Pangram-class model does flag,
as opposed to light copy-editing, which it verified does not. Any single score on this document
would be a window-size artifact rather than a measurement (NeurIPS: 42.7% of position papers in the
high-AI range at 250–350-word windows, 12.7% at ~100-word windows), and must be reported to any
committee with that caveat. Two things still hold the risk at MEDIUM rather than HIGH: the prose is
lexically rich and syntactically varied, so it does not additionally trip the L2-simplicity
false-positive channel that flags Brazilian-authored English (Liang 61.3% → 11.6% once vocabulary
was enriched), and the provenance shield (§6) converts a flag into a documented-process question.
One item moved **against** the author this round, and it is small but real: **Appendix E is
790 words of continuous new prose in one place, the smallest-context, highest-uniformity unit added
to the document since v1** (§4). A window-based screener sees appendices as their own documents.

**EXPERT-SUSPICION RISK: LOW, with one localized MEDIUM.** The document-level gestalt is still
strongly human, and for the reason v1 identified: it is saturated with concrete research detail a
generator cannot fabricate, and it argues against its own results in public. The rescoped
cross-attention paragraphs are the best new evidence of that — a passage that discloses a null
result *against* the author's own attribution is the single least AI-shaped move in the document.
The localized MEDIUM is **Appendix D**, which reads as the same author but with the rhythm turned
down: 10 of its 12 paragraphs open on a short declarative topic label, and five consecutive
paragraphs open on the frame *The/Two + noun + copula* (§3). That is the outline-shaped uniformity
an examiner keys on, in the one appendix a skeptical examiner is most likely to read closely,
because it is the one that exists to defend an integrity claim.

**Answer to the question you asked directly** — do Appendices D and E and the rescoped
cross-attention paragraphs read as the same author as the least-edited chapter? **Yes for E and for
the cross-attention paragraphs; qualified yes for D.** Details in §3, with the measurements.

---

## TOP 3 FINDINGS

1. **[BLOCKER · both channels · `src/chapters/5_mobiwac.tex:704` · defense p. 73, final p. 68]
   A broken LaTeX macro renders as literal machine debris in the middle of the round's own
   rescoped sentence, and no reviewer of this round caught it.** The source reads
   `$-0.04 \\pm 0.13$` (a doubled backslash). Both PDFs render:
   *"moved next-category macro-F1 by −0.04 𝑝𝑚0.13, which a paired test cannot separate from zero."*
   The `\\` starts a line break and leaves `pm` set as italic math variables, so the reader sees
   `pm0.13` where `± 0.13` belongs, with a line break jammed before it. The identical sentence in
   Chapter 6 (`6_conclusion.tex:98`) is correct and renders `−0.04 ± 0.13`, which proves the intent
   and localizes the defect to one character. Why this is the top finding *for this persona* rather
   than a typography nit: this is the exact page where the document performs its intellectual
   honesty, and it is the exact failure mode a suspicious examiner reads as "generated, pasted, and
   never read by a human" — an artifact of the machinery visible on the page. It also directly
   contradicts Appendix C's "the author reviewed and takes responsibility for every word." One
   character fixes it (`\\pm` → `\pm`). I verified `\\<letter>` appears nowhere else in prose in
   either chapter; the only other hits are legitimate `\\` row breaks inside the Table 8 header.

2. **[BLOCKER · human channel · `src/chapters/6_conclusion.tex:110–111` · defense p. 77,
   final p. 72] A sentence begins in lowercase mid-page because its opening word is trapped inside
   a LaTeX comment — the ninth instance of a failure this repo has now tooled against, and the new
   tool does not catch it.** The rendered text reads:
   *"...we do not offer the ablation as evidence that the trunk contributes nothing. a
   capacity-matched dedicated baseline, run after the Chapter 5 manuscript was submitted..."*
   The word `Second,` sits at the end of the audit comment on line 110
   (`% ... rests on the freeze control and the capacity-matched control. [NEEDS SIGN-OFF: AUTHOR] Second,`),
   so the "First… Second…" pair the paragraph is built on loses its second half and the sentence
   opens on a lowercase article. This is the round's own regression: the same locus
   (`6_conclusion.tex:105`, "a capacity-matched dedicated baseline...") is listed **by name** in
   `src_utils/check_trapped_prose.py:14` as one of the historical defects the new detector was
   built to catch. I ran the detector and the full lint this session: `trapped-prose suspects: 0`,
   `check.sh` exit 0, 9/9 fixtures pass. The detector misses this one because
   `MIN_TAIL_WORDS = 2` and the trapped tail is one word (`Second`) — I traced it through the
   detector's own regex to confirm. So the round's "lint exit 0" claim is true and is not evidence.
   Direction: restore `Second,` to the body line; separately, the detector's floor needs to admit
   one-word tails when the following line begins lowercase (that is 03/tooling scope, flagged here
   because the prose defect is mine).

3. **[MAJOR · human channel · Appendix D, `apx_d_ceiling.tex:59–83` · defense pp. 99–100,
   final pp. 94–95] Five consecutive paragraphs open on the same short-declarative frame, in the
   one appendix whose purpose is to be audited.** In order: *"The screening comparison is
   unaffected."* (5 w) → *"The absolute reading is the weaker one."* (7 w) → *"The gap is not by
   itself evidence of a leak."* (10 w) → *"The benchmark is also not an upper bound."* (8 w) →
   *"Two coverage limits apply."* (4 w). Measured: 10 of 12 paragraphs in this appendix open with a
   first sentence of ≤12 words (83%), against 17% in Chapter 5, 11% in Chapter 3 and 30% in
   Appendix E; sentence-initial *The + noun + is/are* runs at 12.8 per 1,000 words here against
   1.0–4.6 everywhere else in the document. Each label is individually good writing (this is the
   Viegas topic-sentence pattern, and 15 would praise it), and the appendix's *content* is
   excellent. The defect is the run: five in a row makes the section read as a filled-in template
   rather than as an argument, which is tell #2 on the current human catalog (uniform paragraph
   rhythm / outline-shaped sections). Direction is **rhythm variation, not deletion**: break two
   of the five by opening on the measurement or the consequence instead of the label (e.g. begin
   the fourth from its own second clause, "It is the best score of four named predictors, so…"),
   and let one paragraph open on a subordinate clause. Do not touch the two that carry the
   honesty content (*"not an upper bound"*, *"not by itself evidence of a leak"*) — those earn
   their emphasis.

---

## 1 · v1 FINDINGS: WHAT PERSISTS, WHAT IS CLOSED

The only prior run is `_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md (sec. 16_ai_credibility_report.md)` (snapshot 2026-07-23, against an
87-page build that no longer exists). Its six ranked findings, re-checked against the current text:

| v1 finding | Status now | Evidence this session |
|---|---|---|
| 1. No up-front disclosure line; disclosure only in Appendix C | **OPEN, unchanged** | Grep for `artificial intelligence`/`Claude`/`generative`/`apx:ai` across `0_main.tex`, `main.tex`, `main_defense.tex` prose: zero hits. No page of either build before the appendix mentions AI use; the string "Appendix C" appears nowhere outside p. 97 itself. Disclosure now sits on p. 97 of 102 (final: p. 92 of 97) — one page *deeper* than in v1, because the bibliography grew. |
| 2. Do not sterilize Ch3/Ch4 when acting on the -ly finding | **HELD, correctly** | Ch3 1.50%, Ch4 1.15%, Ch5 0.43% (my count, excluding only/early/family/apply/supply/reply/likely). The published chapters were not scrubbed toward the band. That is the right call and it survived the round. |
| 3. Negative parallelism: freeze the count, do not let edit waves raise it | **VIOLATED, mildly** | On v1's own counting basis (regex `, not <lowercase>`, single-line, same eight files): `, not` 35 against v1's 27, `rather than` 50 against v1's 28. Ch5's own `, not` count is 23 against the audited 21. Some of the delta is measurement basis (v1's grep could not see wrapped lines; wrap-aware totals are higher still), so I do not present this as a clean +8/+22. What is not basis-dependent: **Ch2 now carries 14 `rather than` in 4,019 words and Ch5 carries 15 in 6,913**, and three of this round's new passages add one each (`apx_d_ceiling.tex:81`, `5_mobiwac.tex:779`, `:795`). See §5. |
| 4. Notation-dialect seam is a credibility asset; keep per-chapter texture if harmonizing | **HELD** | Ch3 still says "Single", Ch4 "baseline"/"MTLnet", Ch5 "dedicated". Three provenances still visibly differ. Protect. |
| 5. "move the needle" idiom, Ch6 §6.1 | **CLOSED** | Zero occurrences of `needle` anywhere in the chapters. |
| 6. Two bold-header-colon description lists (§1.6, Appendix C) | **REGRESSED to three** | `\begin{description}` now at `1_introduction.tex:230` (p. 17), `apx_c_ai_disclosure.tex:28` (p. 97), and **`apx_d_ceiling.tex:31` (p. 98, new this round)**. Appendix D's is the two-quantity definition list; it is defensible (a definition list is the right form for "each is given one name here"), but it moves the document from two conventional instances to three, and the third sits adjacent to the second. Note only. |

**One v1 claim I could not confirm and one I can correct.** v1 reported the frame CV figures from
03; my own measurement on the current source agrees closely (Ch1 48%, Ch2 57%, Ch6 67%), so that
finding stands on new data. v1 also reported "no over-correction detected in the frame" — still
true, and now true of the new appendices as well (§7).

## 2 · GESTALT PASS (human channel)

Read as a suspicious, LLM-fluent CS examiner (Russell et al. ACL 2025: this population detects at
~92%, keying on formality, originality and clarity, "too clean, too even," plus lexical tells).
Chapter openings, section transitions, the Ch5 §5.6.2 results discussion and all five appendices
were read on the rendered PDF for rhythm and on source for quoting.

**What an examiner would not flag, and why the document is in good shape:**

- **The friction is real and it is public.** This round *increased* it. Ch5 p. 73 and Ch6 p. 77 now
  disclose an ablation whose null result cuts against the author's own attribution, and say in
  plain words what it does and does not license: *"We therefore do not name the shared trunk as the
  source, and we do not present the ablation as evidence against it either."* Generators smooth
  toward a clean story; that sentence refuses both directions at once. Same for the Markov-floor
  rewrite on p. 73: *"Neither fact establishes why the floor lies above the three systems, and we
  do not claim a single explanation."* Replacing a causal story with an admitted protocol asymmetry
  is a move that costs the author rhetorical force and buys accuracy. It reads as a person.
- **Copulas are plain.** `serves as` / `functions as` / `boasts` appear 3 times total in the whole
  document, all inside re-typeset Ch3 prose (`3_cbic.tex:143`, `:209`, `:224`) plus one in Ch2's
  dataset sentence (`2_fundamentals.tex:449`, "Two check-in datasets serve as the ground"). No
  systematic copula avoidance. Appendix E in particular is built on plain `is`.
- **Appendix E takes positions instead of hedging.** *"Pseudonymity is not anonymity."* (p. 102).
  *"It records no approval and no exemption, because none was sought and none is claimed."*
  *"That is how a close precedent handled the question, not a determination of the rule."* A
  generator asked for an ethics appendix produces reassurance; this one produces four named
  unresolved items and declines to claim an exemption it does not have. This is the strongest new
  writing in the document from my channel.
- **Section openers still vary.** Appendix openers: A on a scope statement ("Beyond the three
  studies…"), B on the re-typeset convention, C on the tool, D on a question, E on the data
  provenance. Five appendices, five different opening moves. No template.
- **Banned-vocabulary channel is clean.** My own sweep over all eleven files for
  delve/intricate/showcase/underscore/pivotal/leverage/seamless/testament and for the Claude-family
  aidiolect list (genuine/genuinely, comprehensive, crucially, notably): **zero** in the frame and
  the appendices; the only hits are 3 in Ch3 and 2 in Ch5, inside re-typeset published prose where
  the errata regime governs.

**Residual gestalt tells, ranked:**

- **Appendix D's five-in-a-row opener run** — Top Finding 3.
- **The "Two/Three + noun" announce-opener frame is now a document-wide habit: 16 instances.**
  Verbatim, with pages: *"Two observations from that line matter downstream."* (Ch2, p. 19);
  *"Two qualifications belong with that use."* (`2_fundamentals.tex:165`, p. 20);
  *"Two check-in datasets serve as the ground."* (Ch2, p. 23); *"Two limits keep us from reading
  that as an absence of contribution."* (`5_mobiwac.tex:705`, p. 73); *"Two facts about how these
  numbers were produced bear on that comparison."* (`5_mobiwac.tex:781`, p. 73); *"Three limits
  qualify these results."* (Ch5, p. 74); *"Two qualifications bound this reading"*
  (`5_mobiwac.tex:830`, p. 74); *"Two controls separate this claim from wishful attribution."*
  (`6_conclusion.tex:92`, p. 77); *"Three elements of the published article were deliberately
  preserved…"* (ApxB, p. 89); *"Two quantities are involved in that comparison."*
  (`apx_d_ceiling.tex:29`, p. 98); *"Two readings follow from the table…"* (ApxD, p. 99);
  *"Two coverage limits apply."* (ApxD, p. 100); *"Two qualifications belong with that label, and
  both come from the record itself."* (`apx_e_ethics.tex:28`, p. 101). **MAJOR as a set, MINOR
  individually.** Two of these are near-verbatim twins across a chapter boundary
  (`2_fundamentals.tex:165` "belong with that use" / `apx_e_ethics.tex:28` "belong with that
  label"), and both new passages of this round add one. The construction is a genuine honesty
  device — it announces the count so the reader can check that all of them arrived — which is why
  I do not recommend removing it. I recommend capping it: keep it where the enumeration is load
  bearing (the two controls, the two quantities, the three limits), and rewrite two or three of the
  softer ones into the surrounding prose so a reader does not meet the frame five times in fifteen
  pages. Priority order for rewriting: `apx_e_ethics.tex:28` (the twin), `apx_d_ceiling.tex:29`,
  `2_fundamentals.tex:165`.
- **`works as follows`, `apx_d_ceiling.tex:22`, p. 98.** *"The screening procedure works as
  follows."* One instance; the only other "as follows" uses in the document are the conventional
  organization and contributions sentences. Low signal on its own, but it is a canonical
  procedure-template opener and it happens to be the second paragraph of the appendix an examiner
  audits. NIT-to-MINOR; if the opener run in Top Finding 3 is addressed, address this in the same
  pass.
- **Three bold-label description lists, now adjacent** (v1 finding 6, above). Note only.

## 3 · THE DIRECT COMPARISON YOU ASKED FOR: DO THE NEW PASSAGES READ AS THE SAME AUTHOR?

Comparator: **Chapter 3** (the re-typeset CBIC paper), the chapter this round did not touch
(`3_cbic.tex` mtime 2026-07-25 22:39, before the round) and the most nearly-human-published prose
in the document. Measurements are mine, on comment-stripped source, environments removed.

| | ApxD (rewritten) | ApxE (new) | Ch5 crossattn block | Ch6 crossattn block | Ch3 (comparator) |
|---|---:|---:|---:|---:|---:|
| words | 938 | 789 | 129 | 85 | 4,125 |
| sentences | 47 | 35 | 4 | 2 | 178 |
| mean sentence length | 20.0 | 22.5 | 32.3 | 42.5 | 23.1 |
| sentence-length CV | **57%** | **50%** | — | — | 46% |
| ≤12-word sentences | 32% | 17% | — | — | 13% |
| ≥45-word sentences | 2% | 3% | 50% | 50% | 5% |
| paragraph-length CV | 69% | 37% | — | — | 54% |
| paragraphs opening ≤12 w | **83%** | 30% | — | — | 11% |
| `The <noun> is/are` openers /1k | **12.8** | 1.3 | — | — | 0.7 |
| -ly density | 0.43% | 0.38% | 0.0% | 0.0% | 1.50% |

**Reading, passage by passage.**

- **Appendix E: same author, and the best of the three.** Sentence CV 50%, paragraph CV 37%,
  openers varied (only 3 of 10 paragraphs open on a short label), first-person restrained and
  deliberate (`the author` ×3, no `we`, matching the frame's convention where Ch1/Ch2 use neither).
  It alternates long provenance sentences against short verdicts (*"Pseudonymity is not
  anonymity."* / *"No check-in data is redistributed."*), which is the burstiness signature the law
  asks for. Its paragraph-length CV is the lowest number in the table (37%) and that is the one
  thing I would watch, but at 10 paragraphs the statistic is thin and the reading does not feel
  even. **No credibility concern.**
- **Appendix D: same author, rhythm sanded down.** Its sentence-level CV is the highest of the
  three (57%, above Ch3's 46%), so at the sentence scale it is *not* variance-compressed. The
  compression is one level up, in the paragraph opener (83% short-label, 12.8/1k copula frames).
  That is a specific, fixable defect and not a voice problem: the vocabulary, the hedging habits,
  and the willingness to name what the measurement does not support are all the same author.
  **Qualified yes; fix the opener run.**
- **The two cross-attention blocks: unmistakably the same author, and the most human writing this
  round produced.** They are long-sentence, zero-adverb, heavily-qualified prose that says less
  than the author would like to say. The rescoping is visible in the syntax: both blocks end on a
  double refusal (*"we do not name the shared trunk as the source, and we do not present the
  ablation as evidence against it either"*). No generator volunteers a paragraph whose function is
  to weaken the paper's own attribution.
  **One caution, MINOR:** the two blocks share a 6-gram overlap of 31/80 (39% of the Ch6 block),
  including a 21-word verbatim run (*"on an earlier configuration whose region head was driven by a
  transition prior the models reported here do not use, and"*) and a 14-word run (*"We therefore do
  not name the shared trunk as the source, and we do not"*). Ch5 p. 73 and Ch6 p. 77 are four
  rendered pages apart. Cross-chapter near-duplication is 04's scope, but it is also a mild
  perception item from mine: an examiner who reads both notices copy-paste. Direction: keep both
  disclosures (Ch6 must carry it, since that is where the attribution is made), but let Ch6 state
  it in its own compressed words rather than reusing Ch5's clause order.

## 4 · SPECIFICITY AUDIT (the highest-yield check)

The strongest human signal is the *presence* of concrete research detail a generator cannot
fabricate. **This audit PASSES, and this round strengthened it.** Every new passage carries lived
detail, traceable to a repository artifact I opened:

| New/rewritten passage | Lived detail present | Traced to |
|---|---|---|
| ApxD table (p. 99) | Four named predictors × five datasets, window counts (12,709 / 26,396 / 159,175 / 358,302 / 58,075), fold standard deviations, per-dataset majority floors | `docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.json` — I read it: every printed cell matches, including the floors and the ±sd |
| ApxD coverage limits (p. 100) | Texas absent because `checkin_graph.pt` was not retained; Istanbul 196 of 29,816 places multi-category; strict variant 55,946 of 58,075 windows → 0.3009 vs 0.3016 | same JSON, `skipped` and `sensitivity_strict_drop_ambiguous_last_place` blocks — matches to four decimals |
| ApxD the one exception (p. 99) | A relation-typed graph encoder at 0.3328 standardized rising to 0.4142 raw | `leak_sniff_fl.csv` row `check2hgi_rgcn`: 0.3328098… / 0.4141676… Correct, and correctly named by architecture rather than by an acronym absent from the GLOSSARY |
| ApxE provenance (p. 101) | Figshare DOI, CC0 applied *by the depositor*, depositor identified by a single name, upstream address no longer serving the data | `src_utils/evidence/DATASET_LICENSING_FINDINGS.md` §1.2–1.3 + §4.2 (the upstream now 301-redirects to an unrelated domain) |
| ApxE pipeline (p. 102) | Friendship and profile files present but never read; non-numeric ids replaced by a discarded position index; `/data/*` gitignored | same note §4.4, each row tied to a file:line in the ETL |
| Ch5/Ch6 rescope (pp. 73, 77) | −0.04 ± 0.13 at Florida, one dataset, earlier configuration, prior-driven region head, the record's own "compensation effect" reading | the chapter's own audit comments naming `F50_T1_5_CROSSATTN_ABSORPTION.md` |
| Ch5 Markov paragraph (p. 73) | HMT-GRN below the floor at 6 of 6, ReHDM at 3, STAN at 4; Alabama 22.4% genuine-revisit share; three different protocol footings named individually | the chapter's own comment trail, with per-file sources |

**Nothing in the new material reads as filler that should have carried detail and did not.** The
appendices are, if anything, *more* specific than the chapters they support.

**Two specificity gaps worth naming, both additive fixes:**

1. **[MINOR · `apx_e_ethics.tex:84–87`, p. 102] The precedent dissertation is described but never
   identified, and nothing in the document lets a reader find it.** The text says "A comparable
   dissertation defended in this program in 2024, on location-based social network data and under
   the same advisor, was consulted on the point." Appendix E carries three citations
   (`cho2011gowalla,jure2014snap`, `wongso2025massivesteps`, `luca2021mobilitysurvey`) and none is
   the precedent; `references.bib` contains no `@phdthesis` or `@mastersthesis` entry at all. From
   my channel this is the one place in the new appendix where the prose has the *shape* of vague
   attribution ("a comparable dissertation… was consulted"), which is tell #8. It is not actually
   vague — I verified the underlying claim myself: the file is
   `exemples/germano/Dissertação_Mestrado___Germano.pdf`, its §2.6 "Ethical Statement" (PDF p. 22
   of 96) does discuss location privacy and does state that latitude and longitude were left
   unmasked, and a word-boundary search of its full text layer for `CEP`, `comitê|comite`,
   `ethics committee`, `IRB`, `institutional review` returns **zero** hits, exactly as
   `DATASET_LICENSING_FINDINGS.md` §4.5 records. So the claim is true and checkable; the *reader*
   just cannot check it. Direction (additive): cite the dissertation formally. It converts a
   vague-attribution shape into the document's strongest kind of sentence.
2. **[MINOR · `apx_e_ethics.tex:71`, p. 102] "The mobility literature treats the residual risk as
   open" is the one sentence in the new appendix that generalizes over a literature from a single
   citation** (`luca2021mobilitysurvey`). The specific clause that follows it is properly sourced;
   the framing clause is broader than one survey supports. Direction: attribute the claim to the
   survey rather than to "the literature," or add the second source. (Citation sufficiency is 05's
   gate; I flag the *perception* shape.)

## 5 · RHYTHM / VARIANCE PASS (residual after 03, plus what 03 could not see)

03 measured the six chapters on the 2026-07-26 build and found no variance compression (CV
0.414–0.640). My independent measurement on the current source agrees: Ch1 48%, Ch2 57%, Ch3 46%,
Ch4 43%, Ch5 51%, Ch6 67%. The round's edits did not flatten the chapters.

**What 03 has never measured, because these files postdate its run:** ApxA 42%, ApxB 52%,
ApxC 70%, **ApxD 57%, ApxE 50%**. All in band; the new appendices are not variance-compressed at
the sentence level. The compression that exists is at the paragraph-opener level in Appendix D
(§3, Top Finding 3).

**Negative parallelism, the item v1 asked to freeze.** I reproduced v1's counting basis exactly
(regex `, not <lowercase>`, single-line, same eight files) to make the comparison honest:

| basis | v1 (2026-07-23) | now | note |
|---|---:|---:|---|
| `, not <lowercase>` | 27 | 35 | Ch5 alone 23, against its audited 21 |
| `rather than` | 28 | 50 | Ch2 14, Ch5 15, ApxB 11 |

Part of the increase is measurement basis rather than new text: a single-line grep cannot see the
construction across a wrapped source line, and the wrap-aware count is higher still (45 in the
chapters, 61 document-wide). I therefore do **not** present +8/+22 as clean deltas, and I flag the
basis discrepancy so the author does not treat either number as a tracked metric without fixing the
measurement first. What is basis-independent, and is the finding: **the direction of travel is up,
and three of this round's new sentences each add one** (`apx_d_ceiling.tex:81` "not any of them
against an absolute standard", `5_mobiwac.tex:779` "rather than being left for the reader to
assemble", `:795` "rather than as the standard for this task"). **MAJOR as a trend, MINOR per
site.** Direction: do not scrub the load-bearing ones (the thesis clause "the input representation,
not the sharing architecture"; the region-verdict clauses; "a screen rather than a proof"). Cap the
count, and prefer a plain positive statement in the softer new instances. This construction is #5
on the current human-tell catalog and the explicit target of public de-slop tooling; density is
what convicts.

## 6 · DETECTOR SIMULATION (screener channel)

**No local detector was run, by design and per the persona's own rule.** A Pangram-class screener is
API-gated and unavailable here; the only open-weights option is the RoBERTa family, which the
evidence base shows misclassifies 30–69% of *human* text, so a score from it would be noise a
committee could misread. The screener channel is therefore a qualitative estimate, stated as such,
and no number below is a verdict.

- **L2-simplicity false-positive channel: LOW, unchanged.** The document's prose is lexically rich
  and syntactically varied, which is the state Liang et al. showed drops L2 false positives from
  61.3% to 11.6%. Nothing this round moved toward simplification.
- **Substantive-generation channel: MEDIUM, with one new local elevation.** Appendix E is 790 words
  of continuous new generated prose that a window-based screener will treat as its own short
  document, and short documents are where scores are least stable in *both* directions. Appendix D
  is similar at 938 words but is dominated by a table and by four-decimal figures, which changes
  its surface. I would expect the appendices to score higher than the chapters if anyone scans
  them; that expectation is not a defect in the text and it is not something to write around.
- **Reporting rule for the author, restated because it is the whole point:** if any detector score
  is ever produced on this document, on hybrid text it is unstable by measurement, not by opinion.
  The correct response is never to argue the number. It is to present the provenance (§7), which is
  the officially-recognized corroboration path (NeurIPS 2026 appeal protocol), and this author has
  the material to walk it.

## 7 · PROVENANCE-SHIELD STATUS TABLE (process, not prose — the real defense)

I did not run git, per the protocol. Rows that depended on git in v1 are marked as inherited and
unverified this session.

| Shield element | Status | Basis |
|---|---|---|
| Git AI/author commit discipline | **INHERITED, NOT RE-VERIFIED** | v1 verified `draft(ai):` / `edit(author):` labels. I ran no git command this round. Treat as standing unless contradicted. |
| Layered disclosure (short front + full appendix) | **STILL PARTIAL — the one structural gap, now slightly worse** | Appendix C exists and is well drafted; the up-front one-liner is still absent, and the appendix has moved from p. 87/102 to p. 97/102 (final p. 92/97). The detail-on-demand pattern that the 2026 evidence identifies as minimizing the trust penalty is still half-built. |
| Task-precise wording (generation vs editing) | **PRESENT (exemplary) — protect verbatim** | Appendix C p. 97 discloses frame chapters and **the appendices** as "drafted by the assistant" (generation named as generation, the honest higher-penalty framing) and the paper chapters as "re-typeset reproductions" plus a fidelity-checked translation. Note that its scope sentence already covers Appendices D and E without amendment, which is correct and lucky. **Do not soften "drafted" to "edited."** |
| Disclosure's own accuracy after this round | **ONE MISMATCH TO RULE ON** | Appendix C says the review panel was "eighteen-reviewer." `_history/_review_v2/README.md` records **nine** personas on the corrected build, and this round is a partial re-run (12 reports in `_history/_review_v2/`, of which mine is the 13th). The sentence is scoped to "the complete first version," which was reviewed by eighteen, so it is defensible as written — but an examiner who opens `src_utils/_history/_review_v2/` sees a different number. MINOR; author's call whether to time-index the sentence ("the complete first version passed an eighteen-reviewer panel; later corrections were re-reviewed by a subset"). |
| PT-BR thinking trail | **INHERITED (rich)** | v1 verified `storyline/`, the `AVAL_NECESSARIA_ptBR.md` docs, beat budgets. `src_utils/_history/_archive/reviews_v1/DECISOES_PENDENTES_ptBR.md` is present on disk this session. Recommend preserving through and past the defense; it is the near-unforgeable authorship evidence. |
| Per-chapter pre/post/final checkpoints (NeurIPS format) | **ADEQUATE via git (inherited)** | Author-approved outline → `draft(ai)` → author edit commits. Optional hardening only. |
| Oral defensibility | **SUPPORTED, with two exceptions** | §4's specificity is itself the evidence. The two exceptions are Top Findings 1 and 2: a passage that renders `pm0.13` and a sentence that starts lowercase are the two places where "I read and approved every word" is hardest to say out loud. |
| Verification-claim integrity | **STRONG, and it audits itself** | `src_utils/check_trapped_prose.py` is unusually honest engineering: its docstring records what did *not* work as a discriminator, and states that an earlier version of the docstring listed validation results for a detector version that had never been run. `check.sh` runs the detector's fixtures *before* the detector so a green document cannot be presented as evidence when the checker is broken. That is a real shield. Its one gap is Top Finding 2. |

## 8 · REFRESH PASS (bounded web check, 2026-07-27 — proposed updates for author sign-off)

The persona mandates a bounded refresh before a full-document run. The evidence files are 7–9 days
old. **Nothing fundamental has moved on the stylometric-tells side**, which is consistent with what
the July-2026 baseline already predicted. Genuinely new, datable items, none auto-applied:

1. **Peer-reviewed master's-thesis-scale Pangram deployment (International Journal for Educational
   Integrity, Springer, ~June 2026).** A faculty-wide study screened master's theses with Pangram
   after validating it in a controlled experiment; <cite index="11-4,11-5,11-6">the authors report that they used Pangram on 1,163 master's theses from one faculty and that it flagged 529 of them, 45.5%, as containing AI-generated content</cite>. **This is the most directly relevant new datapoint the persona has ever had**: it is *theses*, not conference papers, and it establishes that ~45% flag rates are now the observed baseline in a real program. Two consequences for this author: a flag would place him in a very large cohort rather than in an outlier class, and screening at thesis scale is now a documented institutional practice rather than a hypothetical. → add to the `detector_landscape_2026` section of `ai_detection_landscape_2026-07-20.md`.
2. **Popular Science ran a hands-on five-detector test on 2026-07-19** <cite index="2-3">(published July 19, 2026)</cite>, i.e. the mainstream-press scrutiny of detector reliability continues past the evidence file's date. Context only; it does not change the threat model. → optional one-line note.
3. **Wikipedia WP:AISIGNS remains the best-maintained human catalog and is actively contested.** Its
   talk page carries a July 2026 thread arguing the guidance page itself exhibits the tells it
   documents, and the rule-of-three item is unchanged. The practical read for us: **the catalog is
   still the right reference and still names uniform paragraph rhythm and rule-of-three as
   structural tells**, which is exactly what Top Finding 3 and §2's announce-opener finding are
   about. No change needed to the evidence file's characterization.
4. **No new detector-bias literature surfaced** past the ACL 2026 Pindrop/Authors Guild audit
   already recorded. The L2 double-bind calibration stands.

**Proposed law/evidence edits for author sign-off (I applied none):** (a) add item 1 above to the
detector-landscape section; (b) consider adding "the numeric announce-opener frame (*Two X apply /
Three Y qualify*)" to WRITING_LAW §4's watch list — it is not on any public catalog, but at 16
instances it has become this document's own signature, and the law's §4.1 explicitly says the ban
table is versioned and rotting and must be re-audited with fresh eyes per pass. This is that
finding.

## 9 · OVER-CORRECTION GUARD

The persona is charged with flagging tell-scrubbing that produces defensive, sterile, or
vocabulary-flattened prose, a failure mode that harms L2 authors specifically and reads as its own
red flag.

- **No over-correction in the new material.** ApxD -ly 0.43%, ApxE 0.38% — below the 0.8% band but
  not at zero, and the adverbs that survive are functional and load-bearing (*honestly*,
  *legitimately*, *equally*, *plainly*, *exactly*, *directly*). Nothing reads as scrubbed.
- **The published chapters were correctly left alone** (Ch3 1.50%, Ch4 1.15%). v1's finding 2 held.
  Keep holding it.
- **One place where scrubbing would be a mistake, pre-emptively:** the *"X, not Y"* clauses that
  carry the region verdict and the thesis claim. If the count in §5 is addressed, address it in the
  soft new instances, never in the honesty devices. Flattening those trades a perception gain for a
  substantive loss, which is the wrong trade in both channels.
- **`co-equal` ×3** (`2_fundamentals.tex:97`, `:390`, `:596`; pp. 19, 23, 25) — v1 noted the
  awkwardness. Still present. If reworded, keep the meaning (neither target subordinate); do not
  flatten to "both."

## 10 · WHAT READS CREDIBLY HUMAN (protect it — do not push toward sterility)

- **The rescoped cross-attention paragraphs are now the document's best credibility asset**,
  ahead of the capacity-matched numbers. A passage that discloses a disconfirming null and then
  declines to use it in either direction is something no generator produces and no author writes
  unless they mean it. Protect the double-refusal sentence verbatim.
- **The Markov-floor rewrite** (p. 73): replacing one causal explanation with a stated protocol
  asymmetry, and saying "we do not claim a single explanation," is a downgrade in rhetorical force
  and an upgrade in credibility. Keep.
- **Appendix E's refusals**: no approval claimed, no exemption claimed, four named open items,
  "Pseudonymity is not anonymity," and the explicit statement that the work adds no
  de-identification of its own. An examiner reading this will conclude a person with something at
  stake wrote it.
- **Appendix D's retirement of its own word.** *"Calling it a ceiling, as the internal screening
  record does, would assert more than the measurement supports."* The document correcting its own
  vocabulary in public, and saying that the released filenames keep the older word because they
  predate the naming, is the opposite of machine polish. Keep both sentences.
- **The specificity (§4)** and **the burstiness** (frame CV 48–67%, appendices 42–70%). Protect
  against any smoothing pass.
- **The notation-dialect seam** across Ch3/Ch4/Ch5. Three visibly different provenances is what
  genuinely different human papers look like. If 15's harmonization is applied, retain per-chapter
  texture.
- **`check_trapped_prose.py`'s self-critical docstring.** Not reader-facing, but if the author is
  ever asked to demonstrate process control, that file is exhibit A: a checker that records its own
  four wrong versions and refuses to let a green result stand as evidence unless its fixtures pass.

## 11 · RANKED FINDINGS (channel · severity · locus · direction — never applied)

1. **[both · BLOCKER · `5_mobiwac.tex:704` · defense p. 73, final p. 68]** `$-0.04 \\pm 0.13$`
   renders as `−0.04 𝑝𝑚0.13` with a jammed line break, inside this round's own rescoped sentence.
   → `\\pm` → `\pm`. Ch6:98 is the correct comparand.
2. **[human · BLOCKER · `6_conclusion.tex:110–111` · defense p. 77, final p. 72]** `Second,` is
   trapped at the end of an audit comment; the sentence renders starting lowercase
   ("...contributes nothing. a capacity-matched dedicated baseline") and the First/Second pair
   loses its second half. → restore `Second,` to the body line; separately, admit one-word tails in
   `check_trapped_prose.py` (`MIN_TAIL_WORDS = 2` is why the round's lint reported 0 suspects here).
3. **[human · MAJOR · `apx_d_ceiling.tex:59–83` · defense pp. 99–100, final pp. 94–95]** Five
   consecutive short-declarative paragraph openers; 83% of the appendix's paragraphs open ≤12 words;
   `The <noun> is/are` at 12.8/1k against 0.7–4.6 elsewhere. → vary two or three openers (start from
   the measurement or the consequence); do not touch the two honesty labels.
4. **[human · MAJOR as a set · thirteen loci quoted in §2, pp. 19–101]** The "Two/Three + noun"
   announce-opener has become the document's own signature (16 instances), including near-verbatim
   twins at `2_fundamentals.tex:165` and `apx_e_ethics.tex:28`. → cap it; rewrite the softer ones
   into surrounding prose, keep the load-bearing enumerations. Candidate for WRITING_LAW §4.
5. **[human · MAJOR as a trend · document-wide, §5]** Negative parallelism up on v1's basis
   (`, not` 27→35; `rather than` 28→50), with three new instances from this round; measurement basis
   also differs, which the author should fix before treating either number as tracked. → cap, do
   not scrub the honesty devices.
6. **[credibility · MEDIUM · front matter, all builds]** Still no up-front disclosure line; Appendix
   C now sits at p. 97 of 102 (final p. 92 of 97). → add one front-matter sentence naming the tool
   and pointing to Appendix C. Placement mechanics are 13's call. **This is the same finding as v1
   #1 and it remains the single highest-value credibility edit.**
7. **[human · MINOR · `apx_e_ethics.tex:84–87` · p. 102]** The 2024 precedent dissertation is
   consulted but never cited; `references.bib` has no thesis entry. The claim is true (I verified
   §2.6 of `exemples/germano/…pdf`, p. 22, and the zero-hit ethics-committee search) but the reader
   cannot check it, and the sentence has the shape of vague attribution. → cite it formally.
8. **[human · MINOR · Ch5 p. 73 / Ch6 p. 77]** The two cross-attention blocks share a 21-word
   verbatim run and 39% 6-gram overlap four pages apart. → keep both disclosures; let Ch6 say it in
   its own words. (04 owns the duplication as such.)
9. **[credibility · MINOR · `apx_c_ai_disclosure.tex` · p. 97]** "eighteen-reviewer panel" is
   accurate for the complete first version but `_history/_review_v2/` records nine personas on the corrected
   build. → optionally time-index the sentence.
10. **[human · MINOR · `apx_e_ethics.tex:71` · p. 102]** "The mobility literature treats the
    residual risk as open" generalizes over a literature from one survey citation. → attribute to
    the survey, or add a second source.
11. **[human · NIT · `apx_d_ceiling.tex:22` · p. 98]** "The screening procedure works as follows."
    → fold into the procedure sentence if the §3 opener pass happens anyway.
12. **[human · NIT/watch · `1_introduction.tex:230` p. 17, `apx_c_ai_disclosure.tex:28` p. 97,
    `apx_d_ceiling.tex:31` p. 98]** Three bold-label description lists, now adjacent (v1 recorded
    two). All three sit in conventional contexts with specific content. → note only.
13. **[human · NIT · defense pp. 80, 84; final pp. 75, 79]** Reference-list casing artifacts leak
    the BibTeX pipeline onto the page: "Tme: Tree-guided…", "Mtpr: A multi-task…", and four
    lowercase "poi" in titles. Not an AI tell as such, but it is machine-artifact texture in the
    part of the document that just gained visual prominence by moving from `\footnotesize` to 12 pt.
    → brace-protect the acronyms in `references.bib`. (05/18 scope; flagged from the
    "was this read by a person" angle.)

## 12 · APPENDIX C's CLAIM, ASSESSED DIRECTLY

You asked whether the document's state is consistent with Appendix C's claim that "the author
reviewed and takes responsibility for every word of the final text."

**Mostly yes, with two exceptions that are exactly the kind a reader tests it against.** The claim
is about responsibility, not about perfection, and the document earns it in the places that matter
most: the results prose is dense with numbers traceable to named files, the honesty devices are
consistent, the errata are ledgered, and this round's rescoping shows an author overruling his own
earlier attribution on the evidence. That is what "reviewed" looks like.

The two exceptions are Top Findings 1 and 2, and they are worth naming plainly because they are
both on pages the claim is most likely to be tested against. A reader who sees `pm0.13` in the
middle of a statistical claim (p. 73) and a sentence beginning "a capacity-matched dedicated
baseline" in lowercase (p. 77) has two data points suggesting those two paragraphs were assembled
and not re-read. Both are one-character or one-word fixes. Once fixed, the claim is unqualified as
far as this channel can judge.

**Does any passage read as though nobody with domain knowledge checked it?** No. I looked
specifically for this, and the opposite is true in the places where it would be easiest to fake:
Appendix D names its one exceptional encoder by architecture rather than by an acronym absent from
the GLOSSARY, and explains *why* that encoder is not a counterexample; Appendix E distinguishes the
Figshare deposit from the SNAP release as two different artifacts with different licence status and
different category annotation, which is a distinction only someone who read both pages would make.
There is, however, one clause I could not source and would flag to 06: **Appendix D p. 100 says the
196 Istanbul multi-category places arise "because those places were re-categorized over time."**
The count is in the JSON; the *explanation* is not. Its only support in the repo that I could find
is a docstring line in `scripts/embedding_eval/autocorrelation_ceiling.py:38`. That is a plausible
and probably correct reading, but as written the appendix asserts a mechanism where the artifact
records a count. → either drop the causal clause or mark it as the computation's own assumption.

## OUT-OF-SCOPE HANDOFFS (one line each)

- **Persona 03 (style gate):** the round's new appendices were never seen by 03 (its v2 report
  predates them); my §3/§5 measurements are a stopgap, not its gate. Also: `check_trapped_prose.py`
  `MIN_TAIL_WORDS = 2` is why lint reported 0 suspects at `6_conclusion.tex:110`.
- **Persona 04 (concordance):** the 21-word verbatim run shared by Ch5 p. 73 and Ch6 p. 77.
- **Persona 05 (citations):** the uncited 2024 precedent dissertation (no thesis entry in
  `references.bib`); the "mobility literature" generalization from one survey; the reference-list
  casing artifacts.
- **Persona 06 (numbers):** ApxD p. 100's "re-categorized over time" is a mechanism claim where the
  source records only a count.
- **Persona 07 (claims):** ApxD p. 99 says one candidate "falls below the benchmark on the
  standardized run" while Ch5 p. 66 still asserts "Every encoder screened, including the clean
  references, therefore lies above the label-history benchmark." The appendix's own comment
  (`apx_d_ceiling.tex:78–82`) reports this and declines to edit Ch5. That reconciliation is a claim
  gate, not a perception item, but from my channel a reader who reads both pages meets a
  contradiction and the appendix is the one that resolves it.
- **Persona 13 (compliance):** placement of the front-matter disclosure line (finding 6).
- **Persona 18 (visual):** the `pm0.13` render is a typography defect as well as a credibility one.

## OPEN QUESTIONS (author only)

1. **Front-matter disclosure line** — same question v1 asked and it is still open. Do you want the
   one-liner, and where (folha-de-rosto footnote, preface, or beside the Abstract)? Highest-value
   credibility edit in the document, and the appendix has drifted one page deeper since v1.
2. **Appendix D's shape** — the appendix's own header offers you the alternative of folding it into
   Chapter 5 as one paragraph. From this channel, keeping it is right (a separately auditable
   appendix is provenance), and the opener run in Top Finding 3 is a small fix rather than a reason
   to fold. Confirm you want it kept, so 03 and 15 can pass on its final shape.
3. **The precedent dissertation** — are you willing to cite it formally in Appendix E? It converts
   your one vague-shaped sentence into a checkable one. If you would rather not name a colleague's
   work in an ethics context, say so and the fix is to drop the sentence rather than to leave it
   uncited.
4. **The "Two X apply" frame** — do you want it capped (finding 4)? It is your own device and it is
   doing honest work; I am reporting that it has become frequent enough to read as a habit, not
   asking you to abandon it.
5. **Detector posture** — unchanged from v1: if the banca or CAPES ever runs a detector, are you
   prepared to present provenance rather than argue the score? Item 1 of §8 is new ammunition: a
   peer-reviewed study screening 1,163 theses in one faculty found 45.5% flagged, so a flag places
   you in a large documented cohort. Assembling a one-page authorship-evidence packet pre-emptively
   remains the recommendation.

---
_End of report. **Screener risk MEDIUM** (windowing caveat, always). **Expert-suspicion risk LOW**
document-wide, with a localized MEDIUM at Appendix D's paragraph rhythm. Appendix E and the rescoped
cross-attention paragraphs read as the same author as the least-edited chapter, and the
cross-attention rescoping is the strongest new credibility evidence in the document. Two BLOCKERs
are rendering defects in this round's own new prose, both one character or one word from fixed, and
both sit on the pages where Appendix C's "every word" claim is most exposed. Re-run after they land._


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
