# CODEX_VS_PERSONAS — the seam between two independent reviews

> **PREMISE ANNOTATION, 2026-08-04.** Row 006 of the table below carries "n=4 over one fixed partition"
> and quotes the Ch.5 sentence "The four seeds also reuse one fixed fold partition, so the reported
> intervals cover variation across random initializations and not across resampled user splits". **That
> premise is refuted.** `src/data/folds.py` passes the run's seed into
> `StratifiedGroupKFold(random_state=...)`, so each seed draws its own user partition; the code path and a
> measured control are in `../../science/fold_partition_and_seeds.md`. The quoted sentence was later deleted
> from Ch.5 on the author's instruction, and `[mobiwac]/ERRATA.md` now records that the reason given for
> that deletion at the time was itself wrong.
>
> **This file is NOT edited beyond this note, and it is not frozen history either.** It is a dated record
> of what two independent reviews saw on 2026-07-27, and its value is that it reports them faithfully;
> rewriting the rows would destroy that. But it sits outside the archive directories, so a reader can
> mistake it for current, which is why the correction is stated here at the top rather than left implicit.
> The disposition of row 006's two wording items is unchanged and is recorded in `codex_reviewer.md` under
> COD-006: "well powered" was removed, and "before any result was read" was KEPT because the author judged
> it accurate (probe `COD-006b` exists to keep a later agent from "fixing" it).

**Written:** 2026-07-27. **Task:** audit `src_utils/codex_reviewer.md` (1,419 lines, 18 COD
findings) against the independent persona suite, and against the source of record.
**Read-only.** This file is the only file written. No file under `src/` was edited; no git
command was run.

**What each review saw, and why that matters on every line below.**

| Review | Artifact it read | Page count it records |
|---|---|---|
| `codex_reviewer.md` | `src/build/main.pdf`, `src/build/main_final.pdf`, repo state `70d3888d`, review date 26 July | 97 / 92 (`codex_reviewer.md:5-6`) |
| `_history/_review_v2/*` (personas 01, 03, 04, 05, 06, 07, 08, 09, 18) | `src/dissertacao.pdf`, `src/build/main_final.pdf` written 2026-07-25 23:42–23:43 | 94 / 89 (`_history/_review_v2/README.md:3-5`) |
| `_history/_review_v2/11`, `_history/_review_v2/10` (later passes) | same sources, re-pinned after the 07-26 edits | 97 (`11_poi_mobility_expert_report.md:8`) and 96 (`10_mtl_expert_report.md:39`) |
| `_history/_review_v2/15`, `_history/_review_v2/16` (2026-07-27) | `src/dissertacao.pdf` rebuilt 07-27 | 102 (`15_readability_editor_report.md:11`; `16_ai_credibility_report.md:10`) |
| `_history/_specialists_v2/BANCA_v3.md` | same 07-27 build | 102 / 97 (`BANCA_v3.md:5-6`) |
| `_history/_specialists_v2/FACT_GATE_v3.md` | builds created 07-27 06:40 / 06:42 | 102 / 97 (`FACT_GATE_v3.md:8-9`) |
| **This audit** | `src/dissertacao.pdf` and `src/build/main_final.pdf` as they stand now | **102 / 97** (measured, `pypdfium2` page count) |

**Consequence, stated once so it is not repeated eighteen times:** codex reviewed a build that
is two correction rounds behind the current one. Every `file:line` in `codex_reviewer.md` has
drifted; I re-pinned each locus by content rather than by number, and where codex's line
reference now lands on unrelated text I say so. Codex's *findings* are still mostly live; its
*coordinates* are not.

---

## Section 1 · Overlap map — the 18 COD findings against the persona suite

Legend for the verdict column, applied against the current source and the current builds:

- **REDUNDANT** — a persona reported the same defect AND the defect is fixed. Do not pay twice.
- **PARTLY REDUNDANT** — a persona reported it, it is partly fixed, a named residue remains.
- **LIVE, CO-REPORTED** — a persona reported it and it is still open.
- **LIVE, CODEX-ONLY** — see Section 3.
- **WRONG** — the finding does not hold against source. Stated as such, not softened.

| COD | Codex's claim (abridged) | Personas covering the same object | Verdict against current source |
|---|---|---|---|
| 001 | Three sentences broken by comment-swallowed prose (`2_fundamentals` "Nash-MTL treats"; `6_conclusion` "a capacity-matched dedicated baseline"; `apx_b` "The emphasis convention"). The new checker misses them. | 15 (`X-1`, one-word `Second,`), 16 (top-3 #2), 01 (`C-05` corrections-inside-sentences), BANCA_v3 (BLOCKER-1) | **REDUNDANT on the prose; PARTLY on the tooling.** All three render: `2_fundamentals.tex:359` → defense p23; `6_conclusion.tex:111-112` → defense p77 ("…contributes nothing. **Second,** a capacity-matched dedicated baseline…"); `apx_b_errata.tex:174` → defense p89. The detector now carries **10 fixtures** (`test_trapped_prose.py:28-82`), including the one-word `Second,` case as fixture 7, and `check.sh:56-73` runs the fixtures *before* trusting the detector (`:68`: "the checker itself is broken, its result is not evidence"); both pass, `trapped-prose suspects: 0`, `check.sh` exit 0. **Codex's tooling sentence ("the new checker misses them") was true of the build it read and is false of the current checker.** Residue: `MIN_TAIL_WORDS = 2` still stands at `check_trapped_prose.py:67`, with a one-word escape hatch at `:98-104` (fires only when the next line opens lowercase). That is narrower than "lower the floor to 1", which is what BANCA_v3:263 asked for. |
| 002 | Ch.4 static category result is target-derived (`fclass` → category is deterministic); the shuffle control collapses static macro-F1 0.7855 → 0.1437 while sequential moves 0.2383 → 0.1988; the PDF does not render it, and Ch.1/Ch.6 still rest the diagnosis on the 20.2–22.0-point gain. | **11 (`B-1`, BLOCKER, the strongest version)**, BANCA_v3 (MAJOR-3 not addressed; SUG-7; Q6 "the candidate is fully exposed"), 09 (prior round), `_history/_archive/reviews_v1/dissertation_review_v2.md:135-165` | **LIVE, CO-REPORTED — and codex's numbers check out.** `comparison.json` in `docs/archive/fusion-study/results/P0/leakage_ablation/alabama/` gives baseline `cat_f1 0.7855417…`, `C_fclass_shuffle 0.14366…`, `next_f1 0.23834…` → `0.19880…`. `fclass_purity.json` gives purity 1.0 at five states (284–365 `fclass` values, zero crossing a target class). Florida replicates (`florida/README.md`: 0.7649 → 0.1506 cat; 0.3627 → 0.2982 next). **Nothing reaches the reader**: `fclass` appears once in 102 pages (defense p51, inside Ch.4's encoder description); `shortcut`, `determin*`, `target's own category` appear zero times. `1_introduction.tex:113-116` still reads "Category performance rose sharply at every state tested. The diagnosis followed: at that stage of the research, the input representation, not the sharing architecture, was the bottleneck" (defense p14), and `6_conclusion.tex:46-55` still carries the 20.2–22.0 figure as the diagnosis (defense p76). One correction to codex: the chain it describes is HGI/`poi2vec.py:487`, and the shuffle arm ran the **HGI** pipeline (`run_log.json`: `shuffle_fclass_seed 42`, seed 42, 1 fold). Ch.3's DGI path is a different construction (`dgi/preprocess.py:115,121-130` plus `dgi/dgi.py:55-56`: one-hot of `category`, then a neighbour mean that becomes the GNN input) — codex says this correctly in its own reconciliation at `codex_reviewer.md:1149-1157`, and the author's ruling at `PENDENCIAS.md:173-177` says the same. That ruling also authorized an appendix and a Chapter 4 preface pointer; neither exists yet. See Section 2.1. |
| 003 | Check2HGI's exact shipped lineage is untested against the future-edge channel; status is "unverified", not clean. | 09 (leakage attack surface, `S-01`-adjacent; four grounds verified), 11 (`M-3` window-population mismatch), BANCA_v3 (Q7), 07 (four-grounds audit) | **LIVE, CO-REPORTED, and the text already says most of it.** `5_mobiwac.tex:376` states the three limits verbatim ("the probe is linear, it was run at Florida alone at one random initialization over five user-grouped folds, and it was run on those ancestor builds of the representation rather than on the one that produced the results reported here", defense p66-67) and volunteers the counter-evidence (one encoder passed the screen and leaked under a sequence model). Persona 09 verified every figure to four decimals and called the paragraph the round's strongest methodological work. **What codex adds that no persona does: the word "leakage-guarded" survives at `1_introduction.tex:158`** (objective 4, defense p16) — a closure word in the objectives list, against a chapter that says the channel is bounded and not closed. That single word is codex's real contribution here and it is worth one edit. |
| 004 | Operational joint-model success conflated with MTL transfer and a trunk mechanism; the discussion still says "the shared trunk carries the semantic context that lifts" category. | **10 (`F-01`, BLOCKER, the original find)**, 07 (`NEW-CLAIM` #2), 09 (`S-03`), 04 (`F-03`), BANCA_v3 (Q10), 01 (`C-07`) | **PARTLY REDUNDANT — and the residue codex names is real.** The attribution *is* downgraded: `5_mobiwac.tex:705-713` now reads "we attribute the gain to the joint architecture rather than to any named component of it … we do not name the shared trunk as the source, and we do not present the ablation as evidence against it either" (defense p72-73), and `6_conclusion.tex:101-103` mirrors it, "We therefore do not name the shared trunk as the source, and we do not offer the ablation as evidence that the trunk contributes nothing" (defense p77). The disconfirming F50 ablation is disclosed with its limits. **But `5_mobiwac.tex:872` still opens the Discussion with "the shared trunk carries the semantic context that lifts the next-category task"** — renders defense p74, final p69. That is the contrary attribution codex reports, still standing sixteen lines after the paragraph that refuses it. Persona 10's `F-01` attacked the mechanism paragraph that has since been rewritten (`5_mobiwac.tex:700-713`, the freeze-control passage) and did not name `:872`; **codex is the only reviewer whose finding still points at live text.** |
| 005 | PCGrad named in a "none of the balancers improved" claim the audit says was never a valid PCGrad test; Nash equal-weight collapse; the "two matrix-vector products" cost claim is unsupported and live. | 10 (`F-02` PCGrad, `F-06` Nash cost, `F-07` Nash correction), 07, 05 | **PARTLY REDUNDANT, and one half is an author ruling codex did not read.** PCGrad: `5_mobiwac.tex:183,185-187` still names it ("at their default configurations", defense p61). The author's decision is recorded and deliberate: *"eu estou relutante de remover, pq mesmo quando não usavamos a torre provada ele não havia gerado resultado, e como o PCGRAD e um dos mais fortes da literatura eu quero deixar ele"* (`PENDENCIAS.md:180-184`). Codex re-files a settled decision as an open defect without noting it is settled. Nash cost: **already disclosed** — `apx_b_errata.tex:164-173` names the preservation, gives the implementation evidence (twenty concave-convex passes, each a convex solve, plus one backward per task), and says the correction "would run in this dissertation's own favour" (defense p89). That closes persona 10's `F-06`. Nash "improves every loss": `3_cbic.tex:224` still says "yielding a compromise descent direction that improves every loss" — reproduced published text, unflagged, and **no persona reports it**; see Section 3. |
| 006 | Statistical wording exceeds the design: n=4 over one fixed partition, fold-Wilcoxon read as n=20, "before any result was read" false, "well powered" post-hoc, "identically" false. | **09 (`S-01` well-powered, `S-02` fixed partition, `S-08` pre-registration, `S-04` selection)**, 07 (`C-02`), 06 (`N-03`), 04 (`F-01`), BANCA_v3 (Q9) | **MIXED — three of five items live, two already answered.** Live: "The equivalence is well powered" (`5_mobiwac.tex:418`, defense p67) — persona 09's `S-01` and 07's `C-02` reached this independently, and I confirmed `STATISTICAL_PROTOCOL.md` pins no target power (§3.2 pins δ_reg = 2 pp as a user-confirm parameter; the word "power" appears only in a *post-hoc* section at `:156-157`). Live: "the selection rule is applied identically to both arms" (`5_mobiwac.tex:880`) while `:523-526` states two different selectors (each dedicated model at its task's best epoch; the joint model at a geometric-mean joint selector). Live: "fixed during development and before any result was read" (`:418`). **Answered:** the fixed-partition caveat that persona 09 called the one finding it would not ship without is now IN Chapter 5 — `5_mobiwac.tex:880`, "The four seeds also reuse one fixed fold partition, so the reported intervals cover variation across random initializations and not across resampled user splits" (defense p75). **Answered:** the n=20/n=4 distinction is stated at all four sites and the fold-Wilcoxon is explicitly the *registered* test reported alongside (`:418`, `:656-657`); see the disagreement in Section 2.4. |
| 007 | Ch.3 does not recover split axis, seed count, tuning budget, checkpoint rule; Ch.4's checkpoint rule unspecified; untested "significant"/"outperforms" survive; CoUrb's 20.2–22.0 is an oracle envelope. | 10 (`F-04` tuning budget), 11 (`m-6` floors), 08 (CoUrb protocol), BANCA_v3 (MODERATE), `_history/_archive/reviews_v1/dissertation_review_v2.md` REV-012 | **PARTLY REDUNDANT; the record half is LIVE and largely codex-only.** Confirmed by grep: `3_cbic.tex:294` gives "5-fold cross-validation" and nothing else — no split axis, no seed, no tuning vocabulary (`hyperparam|Optuna|grid|sweep|tun(ed|ing)|learning rate` all absent from the chapter), no checkpoint rule. Ch.2 discloses the gap honestly (`2_fundamentals.tex:500-507`: "Chapter 3 reports five-fold cross-validation without identifying the split axis … the tests set out below license verbs in Chapter 5 alone"), which is the scoping codex asks for, one chapter earlier than codex looked. The untested-verb half is **half wrong**: Appendix B already substituted four "significant" uses and, this round, added the disclosure that "Two more remain that do read against this chapter's own results" with the reason (`apx_b_errata.tex:200-208`, defense p91) — that is exactly BANCA_v3's `SUG-3`, applied. What survives untested is "outperform HMRM in every POI category" (`3_cbic.tex:302`) and the oracle framing: `4_courb.tex:419` does say "considering the better of the two spatial encoders in each combination", but `0_main.tex:280` (Abstract) and `1_introduction.tex:113-114` say only "rose sharply", and `6_conclusion.tex:46` gives the range with no per-cell-best qualifier. **The oracle-envelope point is live in the frame, and no persona filed it.** |
| 008 | Four citation defects: sklearn 2011 cannot support `StratifiedGroupKFold`; the earlier Word2Vec paper is hierarchical softmax, not negative sampling; Standley does not support the hard-sharing claim; UberNet/Sphere2Vec cite preprints; Standley lacks PMLR volume/pages. | 05 (own three findings: `R-01`, `R-02`, `R-03` — none of these four), 10 (`F-15` Standley claim) | **LIVE, and this is codex's strongest technical block. Two items are new, one is right against a persona's silence, one collides with an author ruling.** ① **Negative sampling: codex is correct.** `4_courb.tex:208` cites `mikolov2013word2vec` for "skip-gram with negative sampling"; that key is arXiv **1301.3781**, *Efficient Estimation of Word Representations in Vector Space* (resolved this session), which proposes CBOW/skip-gram. Negative sampling is **1310.4546**, *Distributed Representations of Words and Phrases*, whose abstract describes "a simple alternative to the hierarchical softmax called negative sampling". The substitution is itself an applied erratum (`apx_b_errata.tex:520-522` replaced `church2017word2vec`), so the wrong-paper-of-two problem was introduced by a correction. **No persona caught it.** ② **UberNet:** `references.bib:395-400` is `@article … arXiv preprint arXiv:1609.02132`; Crossref gives CVPR 2017, DOI `10.1109/cvpr.2017.579`, pp. 5454–5463. Correct. ③ **Sphere2Vec:** `references.bib:640-648` is `@misc … eprint 2306.17624`; the arXiv record's own `journal_ref` reads "ISPRS Journal of Photogrammetry and Remote Sensing, 2023" and Crossref gives DOI `10.1016/j.isprsjprs.2023.06.016`, vol. 202, pp. 439–462. Correct. ④ **Standley** `references.bib:960-965` carries `booktitle = {Proc. Int. Conf. Machine Learning (ICML)}, year 2020, note arXiv:1905.07553` and no volume/pages; the arXiv comment says "Presented to ICML 2020". Codex's PMLR request is reasonable and its claim-support point duplicates persona 10's `F-15` (which correctly notes `3_cbic.tex:210` is reproduced published text and cannot be silently changed). ⑤ **scikit-learn: codex re-opens a settled author ruling.** `references.bib:753-757` records it verbatim: use the 2011 paper as the single citation for both the library and the splitter, name the class defensively in prose, "Do not add a second URL/API-docs citation." `2_fundamentals.tex:497-499` does exactly that. FACT_GATE_v3 §4.9 accepted it on the same basis. Codex is right that the 2011 paper does not describe a 2021 feature; it is wrong to file that as an open defect without recording that the author already ruled. |
| 009 | CoUrb provenance/ledger drift: the single-seed statement is a code inference presented as fact about the published run; the adaptation inventory is stale; the ledger treats the English donor as source of record; the chapter's "no claim altered" contradicts Appendix B. | **08 (L5 gate FAIL — the whole report is this object; `F1`–`F9`)**, 04 (`F-02`), 11 (scope notes) | **MIXED — one part right, two parts already correct, one part wrong.** Right: `4_courb_ADAPTATION_LEDGER.md:3` does name `articles/CoUrb_2026/src_en/` (the EN translation) as "Source of record", where the published record is the Portuguese article, DOI `10.5753/courb.2026.22960`. Persona 08 devotes its §0 to establishing exactly this and verified the PT source equals the published PDF character-for-character. Already correct: the chapter's single-seed sentence **is** scoped to the released implementation — `4_courb.tex:257`: "The released code of record pins a single random seed, so the five folds constitute one repetition … and the reported standard deviations are the spread across folds at that seed". That is the fix codex asks for, already in the text. **Wrong:** codex says "The chapter also says no result, claim, or conclusion was altered while Appendix B lists claim-scope corrections". Grep finds no such universal in `4_courb.tex`; the only "no claim" string is a LaTeX comment at `:200` scoped to one equation re-layout. Codex appears to have read the MobiWac section's "every number and claim in Chapter 5 reproduces the submitted text" (`apx_b_errata.tex:364-365`) and attached it to Chapter 4. |
| 010 | "Three training configurations and all twenty fitted models" miscounts (twenty per arm, sixty total); 56.16 is the best arm's mean (SD 1.89), not a maximum over twenty models. | 06 (`N-03`, convention blur in the same sentence), 07 (`C-03`, same), 10 (`F-14` residue: 56.16 carries no spread, README gives std 1.89), 01 (`C-06`, eleven numbers in prose) | **LIVE, CO-REPORTED — and codex's arithmetic is right where the personas' was adjacent.** The sentence is unchanged at `6_conclusion.tex:118-120` and renders on defense p77: "across three training configurations and all twenty fitted models, the best of them reaches 56.16 macro-F1". `capacity_matched_summary.json` gives **three Alabama arms at n=20 each** (`bs2048_lr0.0025` 56.1611 ± 1.885; `bs2048_lr0.005` 55.6098; `bs8192_lr0.005` 55.74) → **60 fits at Alabama**, and two California arms → 40. And 56.16 is a per-arm **mean**, not "the best of twenty models". So both halves of COD-010 hold. Persona 06/07 caught the *convention* blur in the same sentence (56.16 and 56.82 on the diagnostic-best-family scorer, 64.51 on joint-best) and persona 10 caught the missing 1.89; **only codex caught the count**. Note the task brief lists COD-010 as "partly addressed" — I find no change to that sentence. |
| 011 | No privacy/ethics/licensing/governance text in the PDF. | 12/BANCA_v2 (MAJOR-4), 07, 01, 13 | **REDUNDANT.** Appendix E, "Data Ethics and Governance", renders on defense pp. 101–102 and final pp. 96–97, with the sections "Where the data came from", the pseudonymity sentence, the no-de-identification concession, and the human-subjects position ("the author's position is that review by a research ethics committee was not required. This appendix records that position and its basis. It records no approval…"). BANCA_v3:75 marks MAJOR-4 **CLOSED** and says the appendix "answers it better than I expected". FACT_GATE_v3 §4.5 re-verified every licence at its source of record. Two residues belong to FACT_GATE, not codex (see Section 3's silence column): `M-1` (the upstream address redirects to an unrelated commercial site rather than being dead) and `M-2` (the Foursquare upstream is access-gated). |
| 012 | Both artifacts fail the UFV gate: no cover, literal approval placeholder, committee/date placeholders, bibliography in `\footnotesize` ≈10 pt against a 12 pt rule, TeX Gyre Termes not the named font, process documents pending. | 13/BANCA_v2, 18 (`V-09`), BANCA_v3 (§1 table) | **PARTLY REDUNDANT.** **Bibliography is fixed and measured:** the `\footnotesize` wrapper is gone (`0_main.tex:393-396` records the removal), and per-character measurement gives **11.96 pt on bibliography pp. 81–85, identical to body p60's 11.96 pt**. Campus is set (`0_main.tex:124`). **Still open, and correctly reported:** defense p1 is the folha de rosto, not a cover; defense **p2 renders the literal string "[Approval sheet placeholder — PPG signature-page model is inserted here for the defense; signed version replaces it afterward]"** (`0_main.tex:165-172`); committee and date are placeholders (`:126-128`). **Font:** the build log names `TeXGyreTermesX` / `qtmr` / `ntx*` — a Times-metric substitute, against `UFV_COMPLIANCE.md:32` "Arial or Times New Roman, size 12". Codex is factually right that the recorded rule names neither face; whether a substitute is accepted is a secretariat question, exactly as codex says. These belong to the author. |
| 013 | Appendix C claims the author reviewed every word while **27** `[NEEDS SIGN-OFF]` markers remain; family-level model naming; disclosure only on p95 with no front-matter pointer. | 16 (§12, "Appendix C's claim, assessed directly"), BANCA_v3 (`SUG-1`), 03 | **LIVE, CO-REPORTED — with codex's count wrong in the direction that strengthens the finding.** The current count is **31** markers across ten files (`0_main.tex` 6, `6_conclusion` 6, `5_mobiwac` 5, `apx_a` 4, `apx_b` 3, `1_introduction` 2, `2_fundamentals` 2, `apx_c` 1, `apx_d` 1, `apx_e` 1), which matches `PENDENCIAS.md:312-330`'s own inventory ("TOTAL 31, contagem medida em 10 arquivos, 2026-07-27"). The claim is unchanged in the text (defense p97: "The complete first version passed an eighteen-reviewer panel"; "the author reviewed and takes responsibility for every word"), and the appendix carrying that claim is itself marked `[NEEDS SIGN-OFF]` at `apx_c_ai_disclosure.tex:11-12`. The author has ruled Appendix C stays as written (`_history/_archive/reviews_v1/dissertation_review_v2.md` REV-025); that makes the sign-off list, not the appendix, the path to making the sentence true. Page is now 97, not 95. |
| 014 | Calling a maximum over four label-only predictors a "ceiling" is not an upper bound; the new Markov paragraph asserts a common causal story and mis-describes HMT-GRN/STAN output domains. | 11 (`M-3`, and `B-2` for the floor/externals pair), 06, 15 (`D-1`, `D-2`), 10 (`F-20`) | **REDUNDANT, both halves, and verified in the build.** Naming: `apx_d_ceiling.tex:13` is titled "A Label-History Benchmark for the Next-Category Task"; `:121-123` says "The benchmark is also not an upper bound. It is the best score of four named predictors…"; `5_mobiwac.tex:376` says the same inline ("It is not an upper bound on what a model may score"), and `GLOSSARY.md:51-52` registers the term and retires "label-only ceiling" by name. FACT_GATE_v3 §4.2 audited all 19 surviving uses of "ceiling" and found every one to be the surviving correct sense (the dedicated single-task arm), a label, or a disclosed filename. Markov: `5_mobiwac.tex:803-807` now reads "Neither fact establishes why the floor lies above the three systems, and we do not claim a single explanation", and the output-domain error codex describes was the reviewer-side error the author's own record corrected (`5_mobiwac.tex:836-838`; `PENDENCIAS.md:231-234`). FACT_GATE_v3 §4.4 verified the 6/3/4 below-floor counts exactly. |
| 015 | Six cross-chapter seams: Ch.3 preface says later chapters revise by representation not architecture although Ch.5 changes topology and task pair; "Next-POI" defined as exact place in a chapter predicting category; Gowalla vintage 2009–2010 vs 2009–2011; Ch.2 promises MRR and relative multi-task change, neither delivered; two cross-references point at sections that do not define the claim; gradient scope is four Gowalla states, not "three of six". | 11 (`M-5`, `M-6`, `M-7`, `m-6`, `m-7`), 10 (`F-03` gradient scope), 04 (cross-ref lint), 15, BANCA_v3 (`SUG-5`) | **MIXED, item by item.** ① Ch.3 preface: **live** — `3_cbic.tex:23-25` still says the later chapters "revise that verdict by changing the input representation rather than the architecture", while `1_introduction.tex:123-126` says Ch.5 "also redesigns the sharing topology". ② Next-POI: **already handled** — `3_cbic.tex:79` carries a footnote scoping the published sentence to the category variant, and the preface bridge is at `:27-31`; persona 11's `m-7` judged this "sufficient but fragile" (front matter and running heads still carry the old name). ③ Vintage: **live** — `4_courb.tex:425` "collected between February 2009 and October 2010" against `6_conclusion.tex:188-189` "collected between 2009 and 2011"; personas 11 (`M-6`) and BANCA_v3 (`SUG-5`) both filed it, and Appendix E now makes it reconcilable. ④ Metric promises: **live and confirmed** — `2_fundamentals.tex:471` (MRR) and `:476` (relative multi-task performance change) render on defense p24 only; `MRR`, `Acc@5`, and `relative multi-task` appear in no result chapter. Persona 11's `M-7` is the same finding. ⑤ Cross-references: **wrong as stated** — full lint over all eleven chapter files plus `0_main.tex` gives 99 labels, 224 `\ref`-family calls, **zero dangling**; the two codex names resolve to sections that do define their claims (`5_mobiwac.tex:518` → `sec:mobiwac:setup-metrics`, which defines Acc@10 and its reference point; `:528` → the checkpoint convention it states in place). ⑥ Gradient scope: **fixed in Ch.5, live in Ch.6** — `5_mobiwac.tex:205` now reads "four seeds each on four Gowalla states: Alabama, Arizona and Florida, which are three of the five United States datasets reported here, and Georgia, which this dissertation does not report" (defense p62), which is persona 10's `F-03` applied; but `6_conclusion.tex:169-170` still says "over four seeds on three of the six datasets" (defense p78). Codex is right that a site is unsynchronized; it is the Chapter 6 site, not the Chapter 5 one. |
| 016 | A bounded language pass is still needed: `3_cbic.tex:340` "unbalanced result … lead to the worse of other results" is unrecoverable; the four-channel integrity paragraph and the mechanism-control paragraph carry too much; the abstract compresses design and result into one sentence; the internal style audit fails its own density rules. | 15 (`X-3` 591 words, `X-4`, `X-5`, `X-7`), 01 (`C-02`, `C-05`, `C-06`), 03 (`S-01`, `S-02`, `S-03`), 16 (§5) | **PARTLY REDUNDANT, with one codex-only item.** The unrecoverable sentence is **live and codex-only**: `3_cbic.tex:340` ends "since we have an unbalanced result for the MTL and single, this could lead to the worse of other results" (defense p38). No persona quotes it. The paragraph-burden half is thoroughly covered: persona 15's `X-3` measured the four-grounds paragraph at **591 words**, up 45 from the 546 of the previous build (`15_readability_editor_report.md:194,197`), and personas 09 and 15 disagree about what to do — a disagreement `_history/_review_v2/README.md:67-72` already reconciles: 15's recommendation is break-insertion with zero words changed, "which 09's concern does not touch". Codex's "the internal style audit also fails its own density/ban rules" is **wrong against the current source**: `check.sh` returns exit 0 on em-dashes, contractions, banned words, and codenames, and persona 03 recorded **GATE PASS** with zero em-dashes, zero contractions, zero codenames, zero registry violations; the fourteen banned-word hits it counted all sit in reproduced paper text or Appendix B quotations. |
| 017 | Visual/typographic pass needed: approval placeholder on p2; nearly blank p4 with orphaned Resumo keywords; `Float too large for page by 21.55853pt` for the Appendix B bibliography-errata table in both logs; diagrams on pp. 35, 48, 62, 64 below body size; Ch.4 spatial panels on p53 too small; Appendix B tables in a cramped ruled style. | 18 (`V-01`…`V-10`), 01 (`C-09`), BANCA_v3 | **MIXED, and three sub-claims are wrong.** Confirmed: approval placeholder on defense p2; defense p4 carries only the three Portuguese keywords; **`Float too large for page by 21.55853pt` is present in both current logs** (`build/main.log:1932`, `build/main_final.log:1916`) for the Appendix B bibliography-errata table, which renders on defense p96 / final p91 (codex's p94/p89 is the stale pagination). Measured font sizes: **defense pp. 62 and 64 do carry 6.97 pt in-figure text** (350 and 312 characters), and Ch.3/Ch.4 diagram pages run 8.77 pt — so the small-label finding holds, with persona 18's `V-06` naming the same 6.97 pt. **Wrong:** "Appendix B tables visibly switch to a cramped, ruled paper style" — `apx_b_errata.tex` has **zero** `\hline` and five `\toprule` blocks; the tables are booktabs at `\small`, measured 10.91 pt. **Wrong:** the p35/p48/p53 pages codex names measure 11.96 pt body with 8.77 pt minima, not "substantially below body size" in the 6.97 pt sense. **Superseded:** persona 18's `V-01` (Portuguese `Encoder Espacial` labels) and `V-03` (four `(??)` markers) are both **absent from the current builds** — those two blockers are closed. |
| 018 | Governance drift: page counts stale (89/84, 94/89, 96/91 against a 97/92 build); Appendix D missing from inventories; the Ch.5 adaptation ledger claims every departure recorded while omitting recent additions; the trapped-prose checker returns success on live failures; `make check` fails because `pypdfium2` is undeclared; the log-flattening check is locale-fragile. | 16 (§7 provenance-shield table), 04 (tracking drift), BANCA_v3 (§1) | **LIVE, CO-REPORTED, and every mechanical sub-claim reproduces — including the two most technical ones.** Page counts: `CLAUDE.md:28-29` says 89/84, `PLAN.md:17-18` 89/84, `_history/_archive/handoffs/HANDOFF_v1.md:71,130` 89/84, `PENDENCIAS.md:13` 96/91, against a measured **102/97**. Ch.5 ledger: `5_mobiwac_ADAPTATION_LEDGER.md` (mtime 2026-07-23 22:49) says at `:10` "This ledger lists EVERY departure from the source text" and contains zero mentions of the label-history benchmark, the Markov-floor rewrite, the capacity-matched control, the cross-attention rescoping, or the fixed-partition sentence — all added after it. `pypdfium2`: **no `requirements.txt`, `pyproject.toml`, or equivalent exists anywhere under `articles/dissertacao/`**, and the detector imports it at `check_trapped_prose.py:71`. Locale: **reproduced.** `build/main.log` contains an invalid UTF-8 byte at offset 75,361; I injected a synthetic `Citation ... undefined` warning *after* that byte and re-ran the exact `check.sh:38` pipeline (`tr -d '\n' < "$LOG" | grep -oE ...`). Under `LC_ALL=C` it is found (rc 0). Under `LC_ALL=en_US.UTF-8` and `LC_ALL=pt_BR.UTF-8`, `tr` aborts with "Illegal byte sequence" and the check returns **rc 1 with no output — a silent pass on a real undefined citation**. This sandbox runs `LC_CTYPE=C`, which is why the check works here; a developer machine with a UTF-8 locale would miss it. **Codex is right, and this is the single most consequential tooling finding in either review.** The checker sub-claim is stale (see COD-001). |

**Redundancy tally.** Of eighteen: **3 fully redundant** (001 prose half, 011, 014) — a persona
found each AND it is fixed, so the author should not pay again. **5 partly redundant** (004, 005,
007, 012, 016) — the persona finding was applied and codex names a surviving residue, which is
worth reading for the residue only. **6 live and co-reported** (002, 003, 006, 010, 013, 018).
**4 carry material that is wrong or contradicts a settled author decision** (008's sklearn item,
009's "no claim altered", 015's cross-reference item, 017's Appendix B table-style item, plus
016's style-gate claim).

---

## Section 2 · Disagreements, stated sharply

### 2.1 The Chapter 3 leakage question — codex vs personas 09/11/12

**The disagreement is between codex and the personas it is reporting**, and codex wins it.

Persona 11 states the determinism as a property of the "static category task of Chapters 3 **and
4**" (`11_poi_mobility_expert_report.md:26`, heading of `B-1`), derives it from
`research/embeddings/hgi/poi2vec.py:487` and `research/embeddings/dgi/preprocess.py:115`, and
concludes "Composition: input determines label exactly, for the static task" (`:52`). BANCA_v3
files the same conflation as `MAJOR-3`, "Ch.3/4 static category task is evaluated on inputs
containing the target's own category" (`:80`), and builds arguição question Q6 on it (`:495-513`).
Codex reconciles the same evidence differently:

> "The code inspection shows a material distinction from Chapter 4: Chapter 3 replaces a node's
> own one-hot with averages of its neighbors' categories before the GAT. Therefore, direct
> self-label lookup is **not confirmed**." — `codex_reviewer.md:1152-1154`

**Codex is better supported, and one file codex did not cite settles it.** `dgi/preprocess.py:115`
builds the one-hot of a node's own category as `self.embedding_array`; `:121-130` builds a second
matrix, `self.embedding_array_test`, in which each node's row is
`self.embedding_array.iloc[neighbors].mean(axis=0)` — the mean over its Delaunay neighbours, with
the node's own row **not** included (nodes with no neighbours get a zero vector, `:128`). Both are
serialized (`:186-187`), and `dgi/dgi.py:55-56` decides which one the network sees: **`x`, the GNN
input, is `embedding_array_test`**; the raw one-hot is attached to the `Data` object as
`embedding_array` and is referenced nowhere in training or loss. So Chapter 3's encoder is fed
label propagation over a spatial graph, not a lookup of the node's own label. `hgi/poi2vec.py:487`
is the lookup (`poi_embeddings[valid] = fclass_embeddings[fclass_values[valid]]`), and it is HGI,
which is Chapter 4's path. The shuffle control ran the HGI pipeline
(`.../leakage_ablation/alabama/run_log.json`: `shuffle_fclass_seed 42`, frozen folds under
`output/hgi/alabama/`), so the 0.7855 → 0.1437 collapse is evidence about Chapter 4's construction,
not directly about Chapter 3's.

**A related observation that belongs to neither review, filed here as new.** The chapter's own
description does not match the released implementation's resolution of this question:
`3_cbic.tex:145` says "The node feature matrix is based on category one-hot encoding of each POI,
represented by $X \in \mathbb{R}^{n_c}$", which is what both persona 11 (`:48`) and BANCA_v3
(`MAJOR-3`, "p. 32 still states the node features are 'category one-hot encoding of each POI'")
read as the node's own label in its own input. The code substitutes the neighbour mean. Two
consequences, and the author should choose between them rather than let an examiner choose: the
milder reading is that the chapter's phrase is loose and the construction is better than the
reviewers assumed; the harsher reading is that the published sentence does not describe what was
run. **Limit on this evidence, stated because it is load-bearing:** the files above are the current
repository state, and Chapter 3's own run records are lost (`_history/_archive/reviews_v1/dissertation_review_v2.md` REV-012),
so the code cannot be tied to the 2025 numbers with certainty. That uncertainty is exactly codex's
"unverified split/embedding-fit boundaries" (`codex_reviewer.md:1154-1156`) and it argues for
codex's disposition, not against it.

The author reached the same conclusion independently and it is on the record, in the ruling that
also authorized an appendix on the topic and a pointer to it from the Chapter 4 preface:

> *"esse não se aplica ao DGI que usamos no cbic, então a tarega estatica ela só possui problema no
> courb … eu acredito que valha um appendix para isso ou inserimos essa discução em um dos
> appendix, e no prefacio do courb apontamos para esse apendix."* — `PENDENCIAS.md:174-177`

**What this changes for the author.** Persona 11's `B-1` and codex's COD-002 must not be merged
into one disclosure. Chapter 4's static task is a confirmed deterministic mapping. Chapter 3's is
transductive label propagation with an unverified split boundary — a weaker and different defect,
which is codex's phrase "major scope/method uncertainty" (`:1156`). Writing one sentence that
covers both would overstate Chapter 3 and understate Chapter 4. **Codex's distinction is the more
careful one and should govern the wording.**

### 2.2 Does MTL "help" — COD-004 vs persona 10 vs the chapter's own controls

Persona 10 filed the original BLOCKER against the sentence that then existed:

> "the attribution 'a stronger shared trunk' outruns its control … The chapter jumps from that to a
> named component" — `10_mtl_expert_report.md:45,65-66`

Codex, reading a later build, says the fix did not take:

> "The discussion later says that 'the shared trunk carries the semantic context that lifts'
> category." — `codex_reviewer.md:236-237`

**Both are right about different sentences, and codex's is the one still in the document.** The
sentence persona 10 attacked is gone: `5_mobiwac.tex:700-713` now withholds the attribution
explicitly and discloses the disconfirming Florida ablation with both of its limits. But
`5_mobiwac.tex:872` opens §5.7 with "One model serves both tasks: the shared trunk carries the
semantic context that lifts the next-category task, and the private spatial path keeps the
next-region task competitive" — rendered on defense p74 and final p69, sixteen lines after the
refusal. `6_conclusion.tex:101-103` is clean. So the frame is synchronized and the chapter is
not.

**On the substantive question, the chapter's own controls settle it and neither reviewer disputes
the settlement.** The freeze control rules out region-teaches-category, and the chapter says so in
the terms persona 10 asked for: "It rules out the region task teaching the category one, since the
gain survives with the region pathway untrained. What it leaves is the joint architecture itself,
and the control does not say which part of it" (`5_mobiwac.tex:700-703`). The capacity-matched arm (`capacity_matched_summary.json`)
rules out parameter count. Neither locates a component. BANCA_v3's Q10 reads the resulting text
as the round's best work — *"Refusing to bank an ablation that ran in your favour, and saying why
in the text, is the behaviour that most raises my confidence in the rest"* (`BANCA_v3.md:641-642`).
**The disagreement is therefore not about the science; it is about one un-updated topic sentence,
and codex is the only reviewer pointing at it.** Fix `:872` and both findings close.

### 2.3 The label-history benchmark's status — COD-014 vs personas 06/11/15

**No disagreement survives; codex's finding is closed and its own remedy is what shipped.**

Codex asked for the rename and the explicit non-bound statement (`codex_reviewer.md:665-666`).
Both are in the document: `apx_d_ceiling.tex:13` (title), `:121-123` ("also not an upper bound …
Calling it a ceiling, as the internal screening record does, would assert more than the
measurement supports"), `5_mobiwac.tex:376` inline, and `GLOSSARY.md:51-52` as the registry entry
that retires the old name. Persona 15 verified the rewrite fixed the concept collision it was
aimed at ("2 uses in 928 words, and both are meta-mentions", `15_readability_editor_report.md:35`)
and persona 10's `F-20` records it as "label-only and correctly bounded"
(`10_mtl_expert_report.md:600`).

**The live residue is persona-only, not codex's:** persona 11's `M-3` shows Appendix D's window
counts (`apx_d_ceiling.tex:81`, Alabama 12,709) come from a different windowing than Table 8's
(`5_mobiwac.tex:355`, 96,326), so the
"four to six points" gap compares two numbers measured on two window populations. Neither the
appendix nor Chapter 5 says so. That is a real open item and **codex does not report it.**

### 2.4 The statistical footing, n=4 vs n=20 — COD-006 vs persona 09

Codex:

> "The fold-level Wilcoxon pool reuses the same folds across seeds and should not be read as
> twenty independent population draws." — `codex_reviewer.md:328-329`, with the required action
> "Treat the fold-level Wilcoxon as supporting/sensitivity evidence, not an independent n=20
> footing" (`:348-349`)

Persona 09, on the same sentence, records the opposite disposition:

> "The prior version of this text reported only the *t* and characterized the Wilcoxon as
> under-powered without running it at its registered footing; the round both ran it and disclosed
> the departure. **Finding closed.**" — `09_stats_leakage_skeptic_report.md:47-49`

**Persona 09 is better supported on the Wilcoxon, and codex is better supported on two adjacent
items it bundles into the same finding. Separating them is the whole value of this seam.**

On the Wilcoxon: the chapter does not present n=20 as an independent footing. `5_mobiwac.tex:418`
states the arithmetic and the unit in one clause ("both models use four seeds ($4\times5=20$
measurements) and the tests pair the per-seed means ($n{=}4$)") and labels the fold test as *the
registered* one reported alongside; `:656-657` reports it as agreement, not as primary evidence.
`GLOSSARY.md:79` pins the same reading and forbids the phrasing codex fears ("never write
'n = 20 paired repetitions' for the reported test"), and I confirmed that phrasing appears
nowhere. Codex's recommendation asks for a reframing the document already performs.

On the two items codex bundles in and persona 09 also flags, **codex is right**:
"well powered" (`5_mobiwac.tex:418`) has no pre-registered referent — `STATISTICAL_PROTOCOL.md`
§3.2 pins only the margin as a user-confirm parameter, and its only power discussion is
retrospective (`:156-157`, computed from observed σ_d); and "the selection rule is applied
identically to both arms" (`:880`) is contradicted by `:523-526`, which states two different
selectors. Persona 09's `S-01` reaches the first independently; **the "identically" contradiction
is codex's alone**, and it sits inside the sentence the chapter uses to defend its deltas.

**Ruling for the author:** apply codex's wording fixes to "well powered" and "identically". Do
**not** apply its Wilcoxon reframing; persona 09 audited the executed test against
`m2_prereg_output.txt` (20/20 folds at all six datasets, exact p = 9.5367e-07, Holm-adjusted
5.7220e-06) and the chapter's presentation matches the registry.

### 2.5 Whether the correction round's own tooling is a valid gate — codex vs BANCA_v3 vs this audit

Codex: "the trapped-prose checker returns success despite the three live COD-001 failures"
(`codex_reviewer.md:820-821`). BANCA_v3, on a later build: "A gate that returns clean on the
defect it was written to catch is worse than no gate" (`BANCA_v3.md:261-262`), naming
`MIN_TAIL_WORDS = 2` as the reason a one-word tail escaped.

**Both were right when written; both are now stale, and the residue is narrower than either
says.** The detector was rebuilt around a render test, carries ten fixtures including the
one-word `Second,` case, and `check.sh:56-73` runs the fixtures before trusting it. I ran both:
`10/10 fixtures pass`, `trapped-prose suspects: 0`, `check.sh` exit 0, with all three COD-001
sentences verified rendering in the PDF. What remains is that `MIN_TAIL_WORDS` is still 2, with
a conditional one-word escape at `:98-104` that fires only when the following line opens
lowercase — so a swallowed one-word tail before a capitalized continuation would still pass.
That is a real gap and it is smaller than "lower the floor to 1".

**The larger and unfixed tooling problem is the one both reviews under-weighted: the locale
fragility of the undefined-citation check** (Section 1, COD-018). That check silently passes
under a UTF-8 locale, and it is the check that was introduced *because* four undefined citations
shipped.

---

## Section 3 · What only codex found, ranked by defense exposure

Criterion for inclusion: no persona report and no specialist report (`BANCA_v3`, `FACT_GATE_v3`)
raises the same object. I searched all thirteen persona reports in `_history/_review_v2/` (01, 03, 04, 05,
06, 07, 08, 09, 10, 11, 15, 16, 18) plus both specialists and the prior synthesis for each item.
Ranking is by what an examiner can do with it at the table, not by codex's own severity label.

### Rank 1 — The Chapter 6 capacity-control miscount (COD-010)

**Locus:** `6_conclusion.tex:118-120`, rendered defense p77 / final p72.
**The defect:** "across three training configurations and all twenty fitted models, the best of
them reaches 56.16 macro-F1". The artifact holds **three Alabama arms of twenty fits each**
(`capacity_matched_summary.json` → `results.alabama_h672`: `bs2048_lr0.0025` n 20 mean 56.1611
std 1.885; `bs2048_lr0.005` n 20; `bs8192_lr0.005` n 20), so twenty is the per-arm count and
sixty is the total; and 56.16 is the best arm's **mean**, not the maximum over twenty models.
**Persona silence:** personas 06 (`N-03`) and 07 (`C-03`) quote this exact sentence and both
audit only the *convention* mix (56.16 and 56.82 on the diagnostic-best-family scorer, 64.51 on
joint-best). Persona 10 (`F-14`) notes only the missing 1.89. Persona 01 (`C-06`) says the reader
cannot hold eleven numbers. **Four reviewers read the sentence; none checked the count.**
**Exposure:** highest in the document. This is the sentence introducing the control that answers
"the joint model just has more parameters" — BANCA_v3 calls that control "the single strongest
argument that this collection is a dissertation rather than three papers" (`:249-250`). An
examiner who opens the committed folder finds twelve JSONs at Alabama and eight at California and
concludes the author cannot count his own runs, on the page where the mechanism claim lives.
Cost to fix: one clause plus a dispersion figure.

### Rank 2 — The wrong Mikolov paper for negative sampling (COD-008, item 2)

**Locus:** `4_courb.tex:208`, rendered defense p51.
**The defect:** the sentence says the model learns embeddings "using the *skip-gram* strategy with
*negative sampling* `\cite{mikolov2013word2vec}`". That key is arXiv **1301.3781**, *Efficient
Estimation of Word Representations in Vector Space* (`references.bib:669-677`), which introduces
CBOW and skip-gram. Negative sampling is introduced in arXiv **1310.4546**, *Distributed
Representations of Words and Phrases and their Compositionality*, whose abstract reads: negative
sampling is described there as an alternative to the hierarchical softmax. Both records resolved
against the arXiv API this session.
**Aggravating fact codex does not mention:** the citation was *introduced by an applied
erratum*. `apx_b_errata.tex:520-522` records replacing `church2017word2vec` with
`mikolov2013word2vec` because the former "resolves to a commentary column, not the skip-gram
method". The repair fixed one defect and installed another, and it is declared in the appendix
that exists to prove correction discipline.
**Persona silence:** persona 05 ran a claim-support audit over twelve sites and 38 of 99 entries
and did not sample this one; the string "negative sampling" appears in no persona or specialist
report. FACT_GATE_v3 §4.9 audited the references new to the changed appendices, which did not
include this key.
**Exposure:** high and cheap for an examiner to find, because the equation immediately below the
sentence is the SGNS loss. One-key fix.

### Rank 3 — The unrecoverable Chapter 3 sentence (COD-016)

**Locus:** `3_cbic.tex:340`, rendered defense p38, final p33.
**The defect:** the paragraph ends "Also, it is important to notice that since we have an
unbalanced result for the MTL and single, this could lead to the worse of other results." The
meaning is not recoverable from the text; it is reproduced published prose, so it cannot be
silently rewritten.
**Persona silence:** persona 15 swept the document for reading burden and named the long
paragraphs, not this sentence; persona 03 measured Chapter 3's adverb density (1.69%) and
explicitly declined to recommend changes to reproduced prose; persona 01's cold readers reported
Chapter 3 as followable. No report quotes the sentence.
**Exposure:** moderate, and asymmetric — it costs nothing at the table unless an examiner reads
it aloud, at which point there is no available answer except "that sentence is unclear in the
published article." The right move is the one codex names: the author states the intended
meaning, and it goes in Appendix B as a wording correction with the original quoted.

### Rank 4 — "leakage-guarded" survives in the objectives (COD-003, the wording half)

**Locus:** `1_introduction.tex:158`, rendered defense p16.
**The defect:** objective 4 promises to "Anchor the final answer to the research question in a
**leakage-guarded** statistical protocol". Chapter 5's own integrity paragraph says the opposite
about the channel it can measure: "The measurement bounds this channel rather than closing it"
(`5_mobiwac.tex:391`), with three named limits. A closure adjective in the objectives, against a
bounded claim in the chapter.
**Persona silence:** personas 07 and 09 both audited the four grounds exhaustively and verified
every figure; neither swept the *frame* for closure vocabulary. BANCA_v3's Q7 presses the
leakage question hard and quotes the chapter, not the objectives list.
**Exposure:** high per unit of text. It is one adjective, in the numbered list an examiner reads
first, and it is the exact word a hostile examiner would quote back. One-word fix.

### Rank 5 — Chapter 3's missing protocol record, as a record rather than as verbs (COD-007)

**Locus:** `3_cbic.tex:294` is the whole of the chapter's evaluation protocol: "all experiments
were conducted using a 5-fold cross-validation methodology". I grepped the chapter for split
axis, seed count, tuning budget (`hyperparam|Optuna|grid|sweep|tun(ed|ing)|learning rate`), and
checkpoint rule: none is stated.
**Persona coverage, partial:** persona 10's `F-04` names the tuning-budget gap specifically, as
the condition a negative-transfer diagnosis requires. No report inventories the four missing
records together, and none notes that Chapter 2 already discloses the split-axis and
significance-test halves (`2_fundamentals.tex:500-507`) while leaving seed count, tuning budget,
and checkpoint rule undisclosed anywhere.
**Exposure:** moderate-to-high, because it is the reproducibility question and the honest answer
is partly "the records are lost" (`_history/_archive/reviews_v1/dissertation_review_v2.md` REV-012 records exactly that). The
value of codex's version is that it converts a vague weakness into a four-item list the author
can answer item by item, three with a disclosure and one with a recovery attempt.

### Rank 6 — The CoUrb ledger names the English donor as source of record (COD-009, the part that holds)

**Locus:** `src_utils/adaptation_ledgers/4_courb_ADAPTATION_LEDGER.md:3` — "Source of record:
`articles/CoUrb_2026/src_en/` (the verified EN translation of the published paper …)".
**The defect:** the published record is the Portuguese article. Persona 08 devotes its §0 to
establishing that the repo PT source equals the published PDF (character-stream comparison after
normalizing the SBC PDF's accents and hyphenation, all 126 F1 cells matched) and gives three
independent reasons `src_en/` is a derived tree, including that it retains Portuguese inside
commented-out blocks. So persona 08 supplies the evidence; **codex is the only reviewer that
names the ledger header as the thing to change.**
**Exposure:** low at the defense, high in the trust model. It is a governance file the committee
will not read, but it is the file a later agent reads to decide what the source of record is.
Same class as the ledger drift in COD-018.

### Rank 7 — Nash-MTL "improves every loss" (COD-005, the part with no coverage)

**Locus:** `3_cbic.tex:224`, rendered defense p35: Nash-MTL "yielding a compromise descent
direction that improves every loss while maximizing the joint progress of the entire system".
**Status:** reproduced published text. Appendix B corrects the neighbouring gradient-scale clause
(`apx_b_errata.tex`, Table 11) and now names the cost clause as deliberately preserved
(`:164-173`). This third clause is in neither list.
**Persona coverage:** persona 10 audited Nash-MTL against arXiv:2202.01017 and filed `F-06` (the
cost clause) and `F-07` (the corrected scale clause). It did not file the "improves every loss"
claim.
**Exposure:** low-to-moderate. An MTL examiner may note that Nash-MTL's guarantee is conditional
on the utilities being positive (which the chapter's own Equation `eq:cbic:nbs` states as the
constraint $u_k > 0\ \forall k$), so the unconditional prose overstates it slightly. Cheapest
resolution is one line in Appendix B's deliberately-preserved paragraph, which already exists and
already carries two items.

### Rank 8 — The oversized Appendix B float, still in both current logs (COD-017, the measured half)

**Locus:** `build/main.log:1932` and `build/main_final.log:1916`, both reading `LaTeX Warning:
Float too large for page by 21.55853pt on input line 556` — the bibliography-errata table
(`apx_b_errata.tex:556`), rendering on defense p96 / final p91.
**Persona coverage:** persona 18's `V-07` reports the same warning against the 94-page build. It
is therefore not strictly codex-only, but codex is the only reviewer that verified it **survives
into the current builds**, and BANCA_v3 §1 does not list it.
**Exposure:** low. It is a warning, the table renders, and codex's own advice not to reflow floats
before the prose stabilizes is correct. Listed here so it is not lost at the production pass.

### Items codex found that turn out to be someone else's, recorded so they are not double-counted

- The **Alabama revisit share** was codex-adjacent but was found and fixed by
  `FACT_GATE_v3` B-1: the old sentence quoted a place-level 22.4% on non-overlapping windows;
  `5_mobiwac.tex:788` now reads "At Alabama the target region is the last visited region in $32.1$
  percent of windows", sourced to `markov_floor_stride1/alabama.json` `acc1_mean` on the same
  96,326 windows as the floor (`:790-795`).
- **Appendix E's two disclosure gaps** (upstream address behaviour; upstream access gating) are
  `FACT_GATE_v3` M-1/M-2, not COD-011.
- **B.4's Texas and California counts** are still unreconciled (`apx_b_errata.tex:426-432` names
  Florida only, while `4_courb.tex:288-289` gives CA 2,535,573 / TX 3,355,419 against
  `5_mobiwac.tex:358-359`'s 4,089,892 / 3,171,380). That is BANCA_v3 `SUG-6`; codex folds it into
  COD-015's vintage item without the counts.
- **"encodersthat"** at `4_courb.tex:141` still renders on defense p49. BANCA_v3 `MINOR-1`; codex
  does not report it.
- **The `2_fundamentals.tex:174` `[VERIFY]`** on the swept "Cat F1" averaging convention is still
  open, and it is the number persona 11's `M-4` shows belongs to the label-determined static task.
  BANCA_v3 `MINOR-2`. Codex does not connect the two.

Two persona blockers that codex never saw are now **closed**, and are recorded here so they are not
re-litigated from the older reports:

- Persona 16's top finding — a doubled backslash rendering `\pm` as literal `pm0.13` at
  `5_mobiwac.tex:704` — is fixed. The source now reads a single `\pm` at `5_mobiwac.tex:708` and
  `6_conclusion.tex:98`, and both builds render `−0.04 ± 0.13` (defense pp. 73 and 77).
- Persona 05's `R-01` (four citation keys rendering as `(??)`) and persona 18's `V-03` are closed by
  the rebuild: full lint gives **98 cited keys, 98 bibliography entries, 98 `\bibitem`s, zero
  uncited entries, zero undefined keys**, `build/main.blg` is error-free, and the string `(??)`
  appears on no page of either build.

---

## Provenance of this audit

Every verdict above rests on one of: a line read from the current source under
`src/chapters/` or `src/0_main.tex`; a page of `src/dissertacao.pdf` or `src/build/main_final.pdf`
extracted with `pypdfium2` and quoted; a per-character font measurement of those PDFs; a committed
result file named at the point of use (`capacity_matched_summary.json`,
`.../leakage_ablation/{alabama,florida}/`, `fclass_purity.json`, `STATISTICAL_PROTOCOL.md`,
`markov_floor_stride1/alabama.json`); a build log line; a re-run of `check.sh`,
`check_trapped_prose.py`, and `test_trapped_prose.py`; a Crossref or arXiv record resolved this
session (Mikolov 1301.3781 and 1310.4546, Standley 1905.07553, Kokkinos 1609.02132 and
`10.1109/cvpr.2017.579`, Mai 2306.17624 and `10.1016/j.isprsjprs.2023.06.016`); or a persona
report line. Nothing is asserted from model memory.

**Deliberately not done:** no file under `src/` was modified, no git command was run, and no
finding was resolved on the author's behalf. Where a finding needs the author, Section 1 says who
owns it.
