# PLAN.md — schedule to the August 2026 defense (rev. 4, 2026-07-24)

> **This file reads current top-to-bottom.** §0–§3 are the live state (rev. 4). The full rev-2
> six-day drafting schedule that this replaced is preserved verbatim in the **Appendix
> (§H, "Historical — superseded rev-2 schedule")** at the very bottom, for provenance only — do
> not read it as the current plan.

## 0 · Current state (rev. 4, 2026-07-24 — v1 assembled + corrections round 2 applied)

The full v1 was assembled under `src/` in one extended automated build session (all eight phases
on Jul 23–24), **on the Jul 24 v1 deadline, not slipped past it**. A second corrections round
(this session) then applied the author's review of that v1. Logged honestly per this file's own
rule (never absorb silently).

**GREEN (done, committed):**

- Skeleton + **both build modes** from a single `main.tex` (defense **118 pp** → `src/dissertacao.pdf`;
  final AcademicoPG **113 pp** → `build/main_final.pdf`); 0 errors, 0 undefined refs/cites, 0 overfull
  hboxes, lint 0. (Counts measured 2026-07-25 on a full three-pass build of the current source; older
  notes say 87/83 or 89/84, which predate the round-4 and round-5 corrections.)
- Chapters 1–6 assembled; single global `references.bib` (99 entries, 0 dangling); front/back
  matter + three appendices.
- Full-document gates (N4 numeral, R3 citation, L3/L4, WRITING\_LAW §7, two-build) run + fixed.
- **18-persona review suite** run (on `claude-opus-4-8` — deviation logged in §H and Appendix C;
  Fable tokens exhausted) + consolidated report + fix loop.
- **Round 2 (this session):** title set to the working option (alternates commented); Ch.3/4/5
  chapter headings shortened (fixes the header-padding + TOC-wrap defect); **B.1 CBIC
  misattribution corrected in BOTH the dissertation Ch.5 AND the version-of-record
  `[mobiwac]/src/`** (author-authorized cross-boundary edit; logged in the MobiWac ERRATA +
  Appendix B); `src/` restructured (`src_utils/` for non-LaTeX, `build/` for output, one main,
  one root PDF); three Locus exemplar dissertations fetched into `exemples/` + calibration note
  deepened; the three configured specialist profiles re-run on the corrected v1.

**NOT green — author actions before the advisor build (ranked; full list in the handoff note):**

1. **Title** — now set to a working option (*Multi-Task Learning for Point-of-Interest Classification and Prediction Tasks: …*);
   still needs the **final call with the advisor** (three alternates are commented in `0_main.tex`).
2. **CBIC dataset counts** — recomputed this round via the sanctioned Gowalla ETL (Florida
   subset); the result is in `src/src_utils/evidence/cbic_recompute_result.md` for the author to confirm
   and wire into Ch.3 (still `[VERIFY]` until confirmed).
3. Queued `[NEEDS SIGN-OFF]` items: Resumo/Abstract, AI-disclosure, several claim-scope rewordings.
4. Author's remaining tier decisions — collected in `src/src_utils/_history/_archive/reviews_v1/DECISOES_PENDENTES_ptBR.md`.

> **⚠ ADVISOR MUST BE TOLD (author action, top of the handoff).** The plan assumed six human
> drafting days (Jul 19–24); the build was done by the assistant in one session and lands as a
> *machine-assembled v1 for the author to read and own*, not a human-drafted one. The reading map
> + the AI-use disclosure (Appendix C) must accompany the PDF, and the model deviation (Opus 4.8
> for the review suite) is disclosed there.

**Re-plan backwards from the defense window (unchanged hard wall):** v1 → advisor now (Jul 24);
advisor comments Jul 27–31; to banca ≈ Aug 1; Art. 22 ≥20 days → defense from ≈ Aug 21,
early-September fallback at zero downstream cost (§2 risks). The critical path is intact *provided
the author clears the not-green items promptly* — the title (final call) and the CBIC-number
confirmation are the two that gate the banca build.

## 0b · Critical-path facts (current)

| Fact | State / consequence |
|---|---|
| v1 | ✅ **assembled + corrections round 2 applied** (Jul 24); at `src/`, both builds clean |
| Advisor window | Jul 27–31 (final comments; fixes land same-day) |
| To banca + secretariat | ≈ Aug 1 → defense from ≈ Aug 21 (Art. 22: ≥20 days) |
| Art. 21 proof | ✅ substance covered: CBIC DOI `10.21528/CBIC2025-1191324` verified. ACTION: file comprovante with secretariat |
| Banca formed in AcademicoPG + members available late August | Author↔advisor conversation (bundle: EN frame, CoUrb inclusion, date, names, the now-set title) |
| Anti-plagiarism certificate | Required before defense approval — run once v1 stabilizes |
| MobiWac chapter source | ✅ re-synced (Phase 8): no drift; **B.1 now also fixed in `[mobiwac]/src/`** this round, to accompany the next MobiWac review submission |

---

# §H · Historical — superseded rev-2 schedule (2026-07-18, provenance only)

> **Everything below this line is the ORIGINAL rev-2 six-day drafting plan (author ruling
> 2026-07-18): v1 to advisor Thu 2026-07-24, advisor comments Jul 27–31, banca ≈ Aug 1, defense
> from ≈ Aug 21 (Art. 22). It is kept verbatim for provenance. It is NOT the current plan — §0
> above is. The day-by-day was executed by the assistant in one automated session on Jul 23–24
> rather than spread across Jul 19–24; every Day 1–5 deliverable landed (skeleton, chapters
> 3/4/5, frame 1/2/6, global bib, front/back matter, appendices, gates), and the one Day-5
> author decision (title) was correctly not self-decided (it was set to a working option in
> round 2, still pending the advisor). The §2 risk table remains a useful reference and the §3
> standing rhythm still holds.**

## H.1 · Day-by-day (rev-2, as originally planned)

### Day 0 — Fri Jul 18 (DONE by end of day)
- [x] Base docs established, doubly audited (fact + coherence).
- [x] Structural decisions closed (CLAUDE.md §2 ledger): order CBIC→CoUrb→MobiWac, CoUrb in
      (EN translation), MobiWac = current src, global bib, AI-disclosure proceed.
- [x] DOIs verified (CBIC + CoUrb) → Art. 21 substance covered.
- [x] Story spine approved (NORTH_STAR §6) — the G0 artifact for the frame chapters.
- [x] [`GLOSSARY.md`](GLOSSARY.md) created (term registry + model lineage + acronyms + PT
      equivalents) — the L2 consistency artifact.
- [ ] Author: message advisor to book the sign-off conversation + secretariat email
      (comprovante Art. 21, checklist bar, banca logistics).

### Day 1 — Sat Jul 19 (fleet launch)
- [ ] **Skeleton first (blocking, ~half day):** template adaptation per [`TEMPLATE.md`](TEMPLATE.md)
      §2 — clone base, font swap, two build modes, chapter files, `references.bib` seeded from
      the MobiWac verified entries. Compiles with stub chapters before any drafting starts.
- [ ] **Parallel drafting wave 1 (each unit obeys AGENT_GUARDRAILS G1–G3 as it lands):**
      - Ch.3 CBIC re-typeset (errata per NORTH_STAR §4; placeholder-recompute script; preface).
      - Ch.4 CoUrb translation + re-typeset (author's translation agent; L5 fidelity gate;
        audited numbers; contribution note; preface).
      - Ch.5 MobiWac re-typeset from current src (claim whitelist intact; figures regenerated
        at 1-col width; preface).
- [ ] Bibliography consolidation begins (global, Viegas-style; R1–R4 protocol).

### Day 2–3 — Sun Jul 20 – Mon Jul 21 (frame wave)
- [ ] Ch.1 Introduction drafted from the NORTH_STAR §6 spine (sections ≤1,500-word units).
- [ ] Ch.2 Fundamentals (thin; lineage table from GLOSSARY; the "pressing need" hinge).
- [ ] Ch.6 Conclusion (spine beats; verbs bound to tests).
- [ ] Appendix A (other contributions: BRACIS as intermediate iteration) + Appendix B (errata
      list) + AI-disclosure appendix (from git provenance).
      - **Appendix B source (2026-07-21):** compile from the per-folder `ERRATA.md` files
        (`articles/CBIC___MTL/ERRATA.md`, `articles/CoUrb_2026/ERRATA.md`,
        `articles/[mobiwac]/ERRATA.md`). Fixes are applied silently in the dissertation text +
        global bib during adaptation (author ruling); the originals are not edited. See
        NORTH_STAR §4 decision #7.
- [ ] Paper-chapter gate fixes from wave-1 audits landed.

### Day 4 — Tue Jul 22 (integration)
- [ ] Full-document integration: cross-chapter recap subsections wired (Ch.4 "The MTLnet
      framework", Ch.5 recaps), cross-refs, lists (figures/tables/abbreviations), both builds
      compile.
- [ ] Full-document gates: numeral-extraction audit (N4), citation claim-support sample (R3),
      duplication sweep (L3), cross-ref lint (L4), AI-tell + idiom sweep (WRITING_LAW §7),
      read-aloud variance pass. Fresh-eyes agents (L6), not the drafters.

### Day 5 — Wed Jul 23 (author pass + front matter)
- [ ] Author reads end-to-end (G4, rolling since Day 1 but full pass here); fixes.
- [ ] **Title decided** (open item #1) → defense-build front matter (cover, Resumo PT +
      Abstract EN pair, claim-parity audited).
- [ ] Ch.5 re-synced against the author's latest `[mobiwac]/src` refinements.

### Day 6 — Thu Jul 24 (**v1 to advisor**)
- [x] Final compile of the defense build; gates green or author-waived. **DONE 2026-07-24:**
      both builds compile clean; the handoff note (`src/src_utils/_history/_archive/handoffs/HANDOFF_v1.md`) is the reading map + the
      ranked author to-do list. Title + CBIC recompute remain author actions before the advisor
      build ships (see the rev-3 status block).

> **Reconciliation (rev. 3):** Days 1–6 were executed by the assistant in one automated session
> on 2026-07-23/24, not spread across Jul 19–24. Every Day 1–5 deliverable above landed
> (skeleton, chapters 3/4/5 re-typeset, frame chapters 1/2/6, global bib, front/back matter,
> appendices, full-document gates); the checkboxes are left in their original per-day form as the
> plan of record, and the rev-3 status block at the top is the authoritative what-actually-happened.
> The one Day-5 item that is an author decision (title) was correctly NOT self-decided.

### Jul 25–26 — buffer + certificate
- [ ] Anti-plagiarism certificate run; residual polish; any advisor early comments.

### Jul 27–31 — advisor round
- [ ] Comments in → same-day fixes (gates re-run on touched sections only).
- [ ] Banca confirmed in AcademicoPG; secretariat package prepared (Art. 21 comprovante, text).

### ≈ Aug 1 — to banca + secretariat → defense ≈ Aug 21–29
- [ ] 50-min deck (reuse CoUrb/MobiWac deck assets; the arc IS the deck) — built during the
      20-day window, not before.
- [ ] Post-defense: corrections → final AcademicoPG build → pipeline per UFV_COMPLIANCE §4
      (deposit deadline ≈ 3 months post-defense; off the critical path).

## 2 · Risks and fallbacks (rev. 2)

| Risk | Mitigation / fallback |
|---|---|
| Six drafting days slip | The buffer is Jul 25–26; the true hard wall is "to banca ≈ Aug 1". If v1 slips ≥2 days, the advisor window compresses — tell him immediately, don't absorb silently. |
| Advisor/banca unavailable in late August | Early-September defense relaxes everything by 1–2 weeks at zero downstream cost; decide in the Day-0/1 conversation. |
| Translation fidelity (Ch.4) under time pressure | L5 gate is mandatory regardless of clock; if the translation isn't gate-clean by Day 3, fall back to keeping the chapter in PT (§2.6.3 legal) and translate for the final post-defense build. |
| MobiWac src moves under Ch.5 | Single re-sync point (Day 5) + a diff check at the final gate; do not chase intermediate edits. |
| Fleet output quality (mass drafting) | The gates are the throttle: nothing merges without G2/G3; fresh-eyes rule L6 holds even under deadline; the author reviews rolling (G4), not in one lump. |
| Comissão objects to CoUrb chapter | Fallback structure (CoUrb summarized in the frame; coletânea = CBIC + MobiWac) — the skeleton keeps Ch.4 as a drop-in either way. |

## 3 · Standing rhythm

Every writing session starts from [`CLAUDE.md`](CLAUDE.md) §0; every handoff carries gate
status; the author approves rolling. This file is the schedule of record — update checkboxes
daily; log slips honestly.

**Reviews run through the reviewer suite** ([`reviewers/README.md`](reviewers/README.md)): the
per-chapter pipeline and gate-day panel are defined there (fact trio 05–07 → style 03 → deep
domain 09–11 → change gate 14). The full-document panel before each handoff adds 15
(readability), 16 (AI-credibility, after 03), and 18 (visual) on the built PDF; 12 (banca) and
17 (excellence) run on the complete v1 and again on the banca build.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-20 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
