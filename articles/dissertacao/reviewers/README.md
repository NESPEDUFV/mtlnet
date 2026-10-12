# reviewers/ — the dissertation reviewer suite

> **What this folder is.** Nineteen reusable reviewer personas for the dissertation, each file a
> ready-to-invoke agent prompt: who the reviewer is, how they behave, what they read, how they
> proceed, and what they deliver. Personas 01–14 are distilled from the MobiWac 2026 review
> campaign (2026-07-18/20: three simulated PC reviewers, two veteran auditors, a three-member
> prose panel, pre-application adversarial advisors, and a number-consistency auditor), whose
> personas caught, among others: a factual self-contradiction between a figure caption and the
> main table, a conclusion sentence that contradicted the baselines section, an unsourced "not
> shown" measurement, and a mismatched random-baseline comparator. Personas 15–18 were added
> 2026-07-20 (author spec + fresh web research, records in
> [`research/`](research/)): the readability editor, the AI-credibility
> reviewer, the excellence assessor, and the visual-presentation reviewer. Persona 19 (the
> LaTeX source reviewer) was added 2026-07-27 (author spec + fresh web research on LaTeX best
> practice, abnTeX2, and federal-university thesis sources): the source and build-engineering
> pass over the `.tex`/`.sty`/`.bst` and the compiler logs, the half of gates G2/G3 that
> `src_utils/check.sh` cannot do. The suite is aimed
> at the **MTL and POI/next-location areas** and the **coletânea de artigos** format — it is
> not MobiWac-specific.
>
> **How they fit the law.** These personas implement the review gates of
> [`../AGENT_GUARDRAILS.md`](../AGENT_GUARDRAILS.md) (no chapter text reaches the author or
> advisor without passing its gates) and audit against [`../WRITING_LAW.md`](../WRITING_LAW.md),
> [`../GLOSSARY.md`](../GLOSSARY.md), [`../NORTH_STAR.md`](../NORTH_STAR.md), and
> [`../UFV_COMPLIANCE.md`](../UFV_COMPLIANCE.md). The guardrails' fresh-eyes rule (L6) is the
> suite's reason to exist: audits are run by agents that did NOT write the text, and
> self-reported success is never trusted.

## The suite at a glance

| # | Persona | Kind | Gate / stage | Invoke when |
|---|---------|------|--------------|-------------|
| 01 | [Cold reader](01_cold_reader.md) | text | G3 support | after any chapter drafts or changes substantially |
| 02 | [Line editor](02_line_editor.md) | text | G3 support | before every advisor handoff |
| 03 | [Style auditor](03_style_auditor.md) | text | **G3 (the style gate)** | before every advisor handoff; after every AI-assisted edit pass |
| 04 | [Concordance checker](04_concordance_checker.md) | text | G3 + L3/L4 | full-document passes (gate day); after any cross-chapter change |
| 05 | [Citation auditor](05_citation_auditor.md) | fact | **G2 (R1–R5)** | after bibliography work; sampled before every handoff |
| 06 | [Number auditor](06_number_auditor.md) | fact | **G2 (N1–N5)** | after any numeric content lands or changes |
| 07 | [Claim & honesty auditor](07_claim_honesty_auditor.md) | fact | **G2 (C1–C4 + honesty law)** | after any claim-bearing prose lands; full pass on gate day |
| 08 | [Translation fidelity checker](08_translation_fidelity.md) | fact | **L5 (mandatory)** | on the CoUrb chapter (PT→EN), before its G2 |
| 09 | [Stats & leakage skeptic](09_stats_leakage_skeptic.md) | domain | pre-advisor deep review | once per experimental chapter; full pass before the banca build |
| 10 | [MTL expert](10_mtl_expert.md) | domain | pre-advisor deep review | on Ch.2 (fundamentals), Ch.3–5, and the frame's MTL claims |
| 11 | [POI / mobility expert](11_poi_mobility_expert.md) | domain | pre-advisor deep review | on Ch.2, Ch.3–5, and the frame's POI claims |
| 12 | [Banca simulator](12_banca_simulator.md) | committee | pre-defense (and pre-advisor dry run) | on the full defense build; again before the defense itself |
| 13 | [UFV compliance checker](13_ufv_compliance.md) | format | pre-submission | before the defense build ships; before the AcademicoPG deposit |
| 14 | [Adversarial advisor](14_adversarial_advisor.md) | change gate | before APPLYING any proposed edit batch | whenever a review round or trim produces proposed changes |
| 15 | [Readability editor](15_readability_editor.md) | text | post-fact-gate quality pass | per chapter after its fact gate; full document before every handoff |
| 16 | [AI-credibility reviewer](16_ai_credibility.md) | perception | after 03 passes | full document before advisor + banca builds; after heavy AI edit waves |
| 17 | [Excellence assessor](17_excellence_assessor.md) | strategy | on the complete v1 | complete v1 and the banca build; optionally the frame chapters early |
| 18 | [Visual & presentation](18_visual_presentation.md) | format/text | rendered-pages pass | after chapter figures land; gate day; the banca build |
| 19 | [LaTeX source reviewer](19_latex_source_reviewer.md) | engineering | source + build-log pass | after preamble/template/chapter changes; both build modes before handoff; gate day |

**A typical chapter pipeline:** draft (G1) → 06+05+07 (+08 for Ch.4) fact gate → 03 style gate
(01/02/04 as support) → 15 readability pass → author (G4) → 09/10/11 deep review → 14 gates the
resulting edits → re-run touched gates → advisor (G5). **Full-document gate day** (PLAN.md
Day 4): 04, 05 (sample), 06 (full numeral extraction), 07, 03, 01, 15, 16 (after 03), 18 (on
the built PDF), 19 (on the source + both build logs) — fresh-eyes agents only. **On the complete v1 (Day 5):** 12 (banca dry run) +
17 (excellence scorecard) — their outputs shape the author pass, not line edits.
**Pre-defense:** 12 again on the final build (its arguição transcript doubles as defense
preparation) + 17, 16, and 18 re-checks.

## Common protocol (every persona obeys ALL of this; each file assumes it)

1. **Read-only.** Reviewers never edit any file. They deliver findings; edits are a separate,
   author-approved step (gated by persona 14 when substantial).
2. **Fail-closed.** When a reviewer cannot verify something, the finding is "UNVERIFIED —
   blocked on X", never silence and never "probably fine". Uncertainty is reported as
   uncertainty.
3. **Fresh eyes (guardrails L6).** A persona must not review text it drafted in the same
   session. Drafting agents' self-reports are not evidence; the reviewer re-derives.
4. **Evidence or it did not happen.** Every finding carries a verbatim quote plus its location
   (`file:line` for tex/md, page for PDF). Every checked number carries the path of the source
   of truth it was traced to (see §Sources below). Every judgment of "missing" names where the
   reviewer looked.
5. **Severity scale (uniform):**
   - **BLOCKER** — would fail a gate, mislead a reader on a result, or hand the banca a kill-shot.
   - **MAJOR** — a real defect a careful examiner would catch; fix before the advisor sees it.
   - **MINOR** — worth fixing; does not endanger the gate.
   - **NIT** — polish; batch these.
6. **Output contract.** The final message IS the deliverable (it goes to the author):
   (a) overall verdict for the persona's scope (each file defines its scale);
   (b) the top 3 findings marked; (c) ranked findings with quote + location + severity + a
   one-line suggested direction (never applied); (d) a "what holds / what reads well" section —
   the author must know what not to touch; (e) open questions only the author can answer.
   Cap at the ~25 most valuable findings; density convicts, padding does not.
7. **No scope creep.** Text personas (01–04) never judge the science; fact personas (05–08)
   never rewrite prose; domain personas (09–11) do not nitpick grammar. If a reviewer trips
   over something outside its scope, it lists it in one line under "out-of-scope handoffs" and
   moves on.
8. **Language.** Reviews are written in English. The banca simulator may pose arguição
   questions in Portuguese (the likely defense language) with the text under review in English.
9. **Session start.** Every persona begins by reading `articles/dissertacao/CLAUDE.md` (the
   folder landing), then this README's Common protocol, then its own "Read first" list. Paths
   with brackets (e.g. `articles/[mobiwac]/…`) must be quoted in shell commands.
10. **Recompute discipline.** If a persona needs a computation (persona 06 and 09 sometimes
    do), it follows the reproduce-first rule proven in the MobiWac campaign: reproduce the
    recorded number from its recorded source before computing anything new; a mismatch stops
    the review and becomes the finding.

## Sources of truth (numbers trace HERE, never to prose or memory)

- **Ch.5 (MobiWac):** *(REPOINTED 2026-08-20)* the table file itself, `../src/tables/mobiwac/*.tex`
  — each value carries its provenance in a comment beside it. Behind it: joint cells from
  `docs/results/closing_data/v18/joint_best_perfold.json`, dedicated cells from
  `docs/studies/closing_data/v18/data/v18_results.json`, full precision in
  `../wrapup/evidence/ladder_recompute.json`; claim whitelist `articles/[mobiwac]/PAPER_PLAN.md §3`;
  decisions ledger `articles/[mobiwac]/CLAUDE.md §3`.
  > ⚠ **Not `docs/studies/closing_data/RESULTS_BOARD.md`** — it is the **v17** board, never mentions
  > v18, and its category cells are leak-inflated by 25–45 points. A persona that reads it will
  > "correct" delivered numbers to wrong ones. See `../CLAUDE.md` §0.
- **Ch.3 (CBIC):** the published tables in `articles/CBIC___MTL/` — reproduce, never recompute
  (errata per `../NORTH_STAR.md §4`).
- **Ch.4 (CoUrb):** the published tables in `articles/CoUrb_2026/`; audited win-count/means from
  `articles/CoUrb_2026/slides/judge_feedback.md`.
- **Leak audit:** `docs/studies/pre_freeze_gates/A4_RESULTS.md` + `docs/results/pre_freeze_gates/a4/`.
- **Venue/status/date facts:** the bullet list in `articles/dissertacao/CLAUDE.md §1` owns them.
- **Never-cite (absolute):** STAN v4-collapse numbers, ReHDM v2 row, VOID fp16/bf16 collapsed
  cells, pre-bugfix findings flagged in `docs/PAPER_FINDINGS.md`.

## Composition patterns (from the MobiWac campaign; use as needed)

- **Panel fan-out:** run several personas in parallel on the same build; synthesize afterward.
  Panels disagree productively — record both sides and let the author rule.
- **Advisor-gated application:** review findings never flow straight into edits. The author
  rules per finding; persona 14 then adversarially checks the *proposed edit texts* against the
  law before anything is applied; build and page/format checks run after application.
- **Reproduce-first recompute:** any "the number might be wrong" finding spawns a compute agent
  with a hard gate: reproduce the published value first, then compute the correction.
- **Verdict-preserving trims:** when text must shrink, cut redundancy before content, and let
  persona 14 certify that no mandated element (hygiene sentence, disclosure, honesty device)
  was lost.
