# v1_assembly_prompt.md — build the complete LaTeX v1 under src/

> **Purpose.** The third prompt for the SAME Claude Science project (the agent context from
> `science.md §3` stays installed: the papers, the arc, the writing law, the fail-closed
> protocol). This one commissions the **v1 build**: audit readiness against the plan, re-typeset
> the three paper chapters, assemble the full dissertation in LaTeX under
> `articles/dissertacao/src/`, run the review suite (Claude Science specialists + the 18
> `reviewers/` personas on the **Fable model**), and update the planning docs. Paste
> **§THE PROMPT** as a new message in the project.
>
> **Author rulings baked in (2026-07-23):** chapters 3–5 re-typesets are THIS agent's job (they
> do not exist yet); the title stays a **placeholder + #1 blocker flag**; Claude Science runs
> **all** reviews itself using the Fable model for the reviewer personas; the PLAN.md schedule
> has **slipped** and the agent re-plans it honestly.

---

## THE PROMPT

```
TASK
Build the complete first version (v1) of my master's dissertation in LaTeX under
articles/dissertacao/src/. Work in phases, in order: (0) readiness audit against the plan;
(1) skeleton; (2) re-typeset the three paper chapters; (3) integrate the frame chapters;
(4) global bibliography; (5) front/back matter; (6) full-document gates; (7) the review suite
run with the Fable model; (8) planning-doc updates + handoff. Obey the project custom
instructions already installed, plus, for every phase, the repo's own law files:
articles/dissertacao/{CLAUDE.md, WRITING_LAW.md, GLOSSARY.md, AGENT_GUARDRAILS.md, NORTH_STAR.md,
TEMPLATE.md, UFV_COMPLIANCE.md, PLAN.md}. Nothing enters the text from model memory; every
number and citation traces to its sanctioned source; when uncertain, flag [VERIFY] and continue
or STOP per the gate rules — never improvise.

PHASE 0 — READINESS AUDIT (gate: GO / NO-GO before any assembly)
Reconstruct the planned structure from NORTH_STAR.md §3 (chapter map + bridging devices +
time-capsule rule), §4 (per-chapter adaptation notes + errata owners), §6 (story spine), the
CLAUDE.md §2 decisions ledger, and PLAN.md. Then inventory what actually exists:
  - Ch.1 draft:  articles/dissertacao/storyline/drafts/1_introduction.tex (+ 1_citations.md)
  - Ch.2 draft:  articles/dissertacao/fundamentals/ (fundamentals.tex wrapper + the five section
                 .tex files + model_lineage_table.tex + _bib/new_references_ch2.bib + the
                 DRAFT_LEDGER.md and _review/ gate reports)
  - Ch.6 draft:  articles/dissertacao/storyline/drafts/6_conclusion.tex (+ 6_citations.md)
  - Paper sources: articles/CBIC___MTL/ (paper + references.bib + ERRATA.md),
                 articles/CoUrb_2026/src_en/ (the EN translation, version for Ch.4, + ERRATA.md
                 at articles/CoUrb_2026/), articles/[mobiwac]/src/ (version of record + ERRATA.md
                 at articles/[mobiwac]/)
  - Storyline beats + audits: articles/dissertacao/storyline/ (01–07 beat folders, audit/)
Produce a GAP TABLE: every planned component -> exists / partial / missing, with evidence.
Classify gaps: BLOCKING (assembly cannot proceed or would require inventing content — e.g. a
frame draft absent, a required number with no sanctioned source) vs NON-BLOCKING (work this
prompt already covers — the chapters 3–5 re-typesets, the bib merge, front matter — or a
cosmetic TODO). If any BLOCKING gap exists: STOP, report it, and wait. Otherwise: report the
table and proceed. Known-in-advance items (do NOT stop for these; handle as instructed below):
the dissertation title is OPEN by design (placeholder), and the CoUrb figure asset
imagens/subáreas/distribuicao_estados.png is known-absent from the repo.

PHASE 1 — SKELETON (articles/dissertacao/src/)
Follow TEMPLATE.md §0 (decision: start from the Germano tree) and §2 (the ordered checklist):
  - Copy the machinery of exemples/germano/Dissertação_Mestrado___Germano/ (0_main.tex,
    abntex2-UFV.sty, abntex2-num.bst structure) into articles/dissertacao/src/; strip Germano's
    content and personal macros; commit-style note what was kept vs stripped.
  - Font -> Times (newtxtext,newtxmath); citations -> the settled single global NUMERIC scheme
    (Viegas-style; abntex2cite [num] variant or natbib numeric — whichever survives the .sty);
    margins / page-number position / numbering measured against UFV_COMPLIANCE §2 (fix the .sty
    if it carries pre-manual geometry).
  - The TWO BUILD MODES toggle (\ifdefensebuild): defense build = full front matter (cover,
    approval placeholder, Resumo/Abstract, lists, sumário); final/AcademicoPG build = starts at
    the lists per UFV_COMPLIANCE §1, empty pagestyle on pre-body pages, page counter tuned.
  - Coletânea layout: one \include per chapter; a chapter-preface environment (one italic
    paragraph: venue, status, what later chapters revise — the time-capsule device).
  - Lint hook (make check or a script): greps for em-dashes, "this paper" inside chapters,
    unresolved \ref/\cite, and the WRITING_LAW §4 banned words.
The skeleton must COMPILE with stub chapters before Phase 2 starts. Timebox the Germano-tree
compliance checks; if abnTeX2 fights the numeric-citation swap or the two-build split, fall back
to LucasBraganca/ModeloLatexTeseUFV per TEMPLATE.md §1 and say so.

PHASE 2 — RE-TYPESET CHAPTERS 3–5 (the largest work item; per NORTH_STAR §4, one chapter at a time)
Common rules for all three: IEEE/SBC 2-col -> dissertation 1-col; "this paper"/"this article" ->
"this chapter"; renumber sections/figures/tables into the dissertation scheme; captions per
WRITING_LAW §5 (tables ABOVE, booktabs, lead takeaway sentences; figures BELOW, self-contained);
add the italic time-capsule preface; add the mandatory bridging Related-Work recap subsections
(Ch.4 recaps "The MTLnet framework" by name; Ch.5 recaps both MTLnet and the CoUrb finding);
apply the errata from each paper folder's ERRATA.md SILENTLY in the chapter text (author ruling,
PLAN Day 2–3 note) while logging every departure for Appendix B; the originals are never edited.
Figures: regenerate from sources at 1-col width where sources exist (MobiWac src/figs/*.py,
TikZ recompiled); redraw with "adapted from" credit where they do not; NEVER stretch a 2-col
bitmap. Numbers: N1 sources only — the published tables for Ch.3/Ch.4 (with ERRATA.md as the
only sanctioned corrections; CoUrb audited win-count/means from slides/judge_feedback.md), the
results board + claim whitelist for Ch.5. If an erratum value is not resolved inside ERRATA.md
(e.g. the CBIC dataset placeholders need the repo recompute script), do NOT invent it: keep a
clearly-marked placeholder + [VERIFY] flag and list it in the handoff as an author action.
  - Ch.3 CBIC: source articles/CBIC___MTL/; claim discipline: "MTL does not help" is
    time-indexed; the Nash-MTL benefit claims are NOT amplified (preface may note the later
    solver finding).
  - Ch.4 CoUrb: source articles/CoUrb_2026/src_en/ (the verified EN translation); carry the
    contribution note (Vitor: 2nd author, presenter, author of the baseline MTLnet); state it is
    a translated reproduction citing DOI 10.5753/courb.2026.22960; use the AUDITED numbers per
    ERRATA.md; the missing distribuicao_estados.png: rebuild from data if a source script
    exists, else insert a placeholder box + [VERIFY] and list it as an author action.
  - Ch.5 MobiWac: source articles/[mobiwac]/src/ (version of record); the paper GLOSSARY governs
    its prose — do not re-technicalize; claim whitelist verbatim (region verbs bound to tests;
    never upgrade AZ; status = "submitted to MobiWac 2026, under review"); the dissertation MAY
    restore the compressed leak-audit and statistical-protocol prose per NORTH_STAR §4 Ch.5
    notes — mark any such restoration [NEEDS SIGN-OFF] since it is new-to-chapter text.

PHASE 3 — FRAME INTEGRATION
Import Ch.1 (storyline/drafts/1_introduction.tex), Ch.2 (fundamentals/, the wrapper + five
sections + lineage table), Ch.6 (storyline/drafts/6_conclusion.tex) into src/ chapter files.
Adapt \section levels to the skeleton, wire every cross-chapter \ref, and verify the frame's
promises against the assembled chapters (the storyline audit already checked the intent; you
check the ASSEMBLED text): Ch.1's per-chapter organization bullets match reality; Ch.2 §2.5's
hinge pre-motivates exactly Ch.3/4/5; Ch.6 answers Ch.1 (the intro-conclusion loop). Fix only
mechanical mismatches (numbering, names); any WORDING change in the frame that alters a claim
is [NEEDS SIGN-OFF]. New connective prose you must write (transitions, preface paragraphs) obeys
AGENT_GUARDRAILS L1 (small bounded units) and the WRITING_LAW register.

PHASE 4 — GLOBAL BIBLIOGRAPHY (single, numeric, Viegas-style; decision #5)
Merge into one src/references.bib: the MobiWac verified entries (preferred donor per R1), the
CBIC and CoUrb entries actually cited by the re-typeset chapters, the Ch.2 set
(fundamentals/_bib/new_references_ch2.bib), and the Ch.1/Ch.6 citations (storyline/drafts/
*_citations.md). Rules: deduplicate multiple key spellings of one work (e.g. the three DGI keys)
to ONE canonical key with a mapping table; apply the R4 bibliography errata (per the ERRATA.md
files: the POI-RGNN wrong-paper fix, HMRM author names, GAT -> ICLR version, silva2025mtlnet
venue fix); every entry keeps/gets its provenance comment; no new entry without a resolvable
identifier; zero key collisions against the whole file; zero dangling \cite after the merge.

PHASE 5 — FRONT MATTER, BACK MATTER, APPENDICES
  - TITLE: placeholder ("[TITLE — open decision NORTH_STAR §5.8]") on the folha de rosto and
    everywhere it echoes, with the three candidates as a LaTeX comment beside it. This is the #1
    blocker in the handoff note.
  - Resumo (PT) + Abstract (EN): draft as a claim-parity PAIR from Ch.1/Ch.6 content only
    (WRITING_LAW §5 abstract formula + §6 PT rules, GLOSSARY §6 equivalents); same claims, same
    numbers, same hedges; both marked [NEEDS SIGN-OFF].
  - Lists of figures / tables / abbreviations (seed the abbreviations from GLOSSARY §5).
  - Appendix A — other scientific contributions: BRACIS as an unpublished intermediate
    iteration, per the C4 containment rule.
  - Appendix B — errata: compiled from the three ERRATA.md files; every silent fix applied in
    Phase 2 must appear here (the reconciliation is a gate: fixes applied == fixes listed).
  - AI-use disclosure appendix: drafted from the git provenance trail per AGENT_GUARDRAILS §6
    (tools + model versions + scope per part + the verification gates used); one page max;
    [NEEDS SIGN-OFF].
  - Both build modes compile clean (pdflatex + bibtex, zero errors, zero unresolved refs).

PHASE 6 — FULL-DOCUMENT GATES (fail-closed; fresh-eyes rule L6 — the gate runner is never the
drafter of the text under audit; use separate sub-agent instances)
Run, in order, and fix-and-rerun until green or explicitly waived-with-reason:
  - N4 numeral-extraction audit: every numeral+unit in the document matched to its ledger source
    (the chapter ledgers + the published tables + the results board); orphans block.
  - R3 citation claim-support sample: >=20% of all citations, 100% of entries new in this build —
    the citing sentence is supported by the opened source.
  - L3 cross-chapter duplication sweep (sanctioned recaps exempt); L4 cross-ref lint (every
    \ref/\cite resolves to the right target).
  - WRITING_LAW §7 checklist: canonical names, zero repo codenames, AI-tell + idiom sweep,
    em-dash count = 0, verbs-bound-to-tests spot check, Resumo<->Abstract parity.
  - The two-build check: defense PDF and AcademicoPG PDF both correct per UFV_COMPLIANCE §1–§2.

PHASE 7 — REVIEW SUITE (run it ALL here, using the FABLE MODEL for every reviewer persona)
First read articles/dissertacao/reviewers/README.md (roster, pipeline, common protocol). Then
execute the review plan from PLAN.md §3 on the assembled v1:
  - Per-chapter pipeline on every chapter: fact trio (05 citation auditor, 06 number auditor,
    07 claim honesty) -> style (03) -> deep domain (09 stats/leakage, 10 MTL expert, 11
    POI/mobility expert) -> change gate (14 adversarial advisor).
  - Ch.4 additionally passes 08 translation fidelity (the L5 gate — mandatory, sentence-level
    claim-strength comparison against articles/CoUrb_2026/src/).
  - Full-document panel on the BUILT defense PDF: 01 cold reader, 02 line editor, 15
    readability editor, 16 AI-credibility (after 03), 18 visual presentation, 13 UFV
    compliance, and — because this is the complete v1 — 12 banca simulator and 17 excellence
    assessor.
Execution rules: each persona runs as a FRESH sub-agent on the Fable model, given ONLY its
persona file and what that file's "Read first" section names (respect 01's blindness rule: the
cold reader gets NO project context); each obeys its own output contract and hard limits; the
drafting agent never reviews its own text (L6). Then the FIX LOOP: apply fixes per persona 14's
change-gate discipline — mechanical/defect fixes land directly with the affected gates re-run;
anything touching a claim, a number's meaning, scope, or the author's voice is queued
[NEEDS SIGN-OFF], never self-approved. Produce a consolidated review report: per-persona verdict
summary, fixes applied, fixes queued, and the re-run gate statuses.

PHASE 8 — CALIBRATION, DOC UPDATES, HANDOFF
  - Calibration against real dissertations: you already hold the two local exemplars — imitate
    exemples/viegas/VIEGAS_ANALYSIS.md (the quality bar + structure devices) and the Germano
    tree (the defended same-advisor precedent). ADDITIONALLY, search the web for other UFV
    PPGCC (Ciência da Computação) master's dissertations — the UFV institutional repository
    Locus (locus.ufv.br) is the primary source; prefer renowned ones (award-listed, SBC CTD,
    highly cited, or praised examples) and coletânea-format ones if findable. Timebox this;
    verify anything you cite; report a SHORT comparison note (structure, front matter, chapter
    shape, bibliography style) and fold any concrete improvement into the build only if it does
    not conflict with the settled decisions ledger.
  - Update PLAN.md honestly: the v1 date has SLIPPED past Jul 24 — log what actually happened
    per day (the PLAN's own rule: log slips honestly, never absorb silently), then re-plan
    backwards from the defense window (banca needs the text >=20 days before the defense;
    late-August defense, early-September fallback per the risk table), and flag explicitly that
    the ADVISOR MUST BE TOLD about the slip (author action, top of the handoff note).
  - Update the state sections: CLAUDE.md §1 (current state: v1 assembled, where, what is open),
    NORTH_STAR §5 statuses if any decision state changed, and a README or pointer in
    storyline/ + fundamentals/ marking their drafts as IMPORTED into src/ (single-source rule:
    src/ is now the working copy; the draft folders freeze).
  - HANDOFF NOTE (the final deliverable, one document): the Phase-0 gap table; what was built
    where; the numbers/citations ledger pointers; EVERY [VERIFY] and [NEEDS SIGN-OFF] item
    ranked (the title first); the gate statuses; the consolidated review verdicts; the exact
    author to-do list (decide title, approve Resumo/Abstract + disclosures + restorations,
    resolve flagged numbers, message the advisor about the slip, re-sync check below).
  - LAST STEP, after everything else: re-diff Ch.5 against articles/[mobiwac]/src/ (the author
    refines the paper in parallel; the single re-sync point is here) — apply mechanical drift,
    queue anything substantive.

HARD LIMITS
Fail closed everywhere: no number, citation, name, date, or claim from memory; the claim
whitelist and verbs-bound-to-tests override every stylistic preference; new frame claims are
proposed, never asserted; self-certification is not acceptance (the gates + the author decide).
Do not edit the source paper folders, the law files' rules, or anything outside
articles/dissertacao/ except NOTHING — all writes stay under articles/dissertacao/ (src/, the
planning docs named above, and the handoff note). If a phase cannot complete under these rules,
report exactly where and why, deliver what is green, and stop.
```

---

## Notes for the author (not part of the prompt)

- **What this prompt adds beyond your message** (the "am I forgetting something" answer):
  the chapters 3–5 re-typeset work (they did not exist in the repo — biggest single item), the
  Germano-based skeleton with the **two build modes** (defense vs AcademicoPG), the **global
  bibliography merge** with dedup + the R4 errata fixes, the **front/back matter** (placeholder
  title as #1 blocker, Resumo↔Abstract claim-parity pair, lists, Appendix A/B, AI-use
  disclosure), the **errata reconciliation gate** (silent fixes applied == Appendix B lines),
  the **figure pipeline** (1-col regeneration; the known-missing CoUrb PNG), the **Ch.5
  re-sync** as the last step, the **L5 translation gate** for Ch.4, and the honest **PLAN.md
  slip re-plan** with the explicit tell-the-advisor flag.
- **The review suite runs inside Claude Science on Fable** (your ruling): each persona is a
  fresh sub-agent fed only its own file, the cold reader stays blind, and the drafter never
  reviews itself. Fixes that touch claims/numbers/scope queue as [NEEDS SIGN-OFF] — expect a
  decision list, not a silently-polished text.
- **Your critical path after the run:** decide the title; read the handoff note's sign-off
  queue; message the advisor about the schedule slip; approve/adjust the re-planned PLAN.md.
- If Claude Science cannot run LaTeX compiles in its environment, it will say so at Phase 1
  (skeleton must compile) — in that case have it deliver the full source tree and I compile
  locally here as the verification step.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
