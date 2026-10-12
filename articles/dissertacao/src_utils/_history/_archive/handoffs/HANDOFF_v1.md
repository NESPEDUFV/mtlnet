# HANDOFF — Dissertation v1 (assembled 2026-07-24; corrections round 2 applied)

> The single handoff document for the machine-assembled v1. Author owns and approves every
> word; this note is the map, the flag ledger, and the ranked to-do list. Nothing here was
> self-approved past the gates. Repo working copy: `articles/dissertacao/src/`.
> **Your fill-in decisions doc: `src_utils/DECISOES_PENDENTES_ptBR.md` (pt-BR).**

## 0. READ THIS FIRST — what round 2 resolved, and what still needs you

**Round 2 (this session) cleared or advanced the two original blockers:**

1. **Title — SET (confirm with advisor).** Now live at all four echo points as the working
   option *"From Representations to a Single Joint Model: Multi-Task Learning for Point-of-Interest
   Category and Region Prediction"*; the three alternates are commented in `src/0_main.tex`. No
   longer a placeholder. **Remaining:** the final call with your advisor (swap in one line if he
   prefers another).
2. **CBIC dataset counts: SETTLED (author ruling 2026-07-24).** Chapter 3 §3.4.1 states the
   Florida figures of record, the same ones Chapter 4 publishes: **20,301 users / 65,009 POIs /
   990,518 check-ins** (`src/chapters/3_cbic.tex`:246; `src/chapters/4_courb.tex`:238). Ruling and
   rationale: `src_utils/evidence/cbic_recompute_result.md`:1-10. No basis question remains and the
   `[VERIFY]` flag is cleared.
   *Superseded, kept for the trail:* this entry previously reported the fresh-2026-ETL recompute
   (raw 21,052 / 76,544 / 1,407,034; after the <5-visit filter 13,935 / 76,266 / 1,392,262) as the
   filled values with the basis still to confirm, and an interim fix then moved Ch.3 to the
   CBIC-era `filtrado.csv` basis (10,460 / 64,454 / 960,520). Neither is current.
3. **B.1 CBIC misattribution — FIXED in both places.** The false "CBIC studied next-region and
   observed negative transfer" is corrected in Ch.5 AND in the version-of-record
   `articles/[mobiwac]/src/`, logged in the MobiWac ERRATA + Appendix B. **Remaining:** send the
   correction with the next MobiWac review submission.

**Still needs you (full list + fill-in fields in `DECISOES_PENDENTES_ptBR.md`):** the Tier-2
`[NEEDS SIGN-OFF]` content (Resumo/Abstract, Appendices A/C, Ch.5 new-to-chapter text) and the
Tier-3 queued review fixes (§3 below). Tier-2 item 2.5 (gate rewordings) you ruled **leave as-is**.

**⚠ AND — tell the advisor about how v1 was produced.** The plan assumed six human drafting
days (Jul 19–24); the build was instead done by the assistant in one automated session and
lands as a *machine-assembled v1 for you to read and own*. The reading map (this note) + the
AI-use disclosure (Appendix C) must accompany the PDF. The review suite ran on `claude-opus-4-8`
rather than the planned Fable model (Fable tokens were exhausted mid-run; you approved the
switch). This is disclosed here, in PLAN.md rev-4, in CLAUDE.md §1, and in Appendix C.

## 1. Phase-0 gap table — final state

Every planned component, its Phase-0 status, and where it landed in v1.

| Component | Phase-0 | v1 state | Where |
|---|---|---|---|
| Skeleton (Germano tree, 2 builds) | missing | BUILT, compiles | `src/0_main.tex + main_{defense,final}.tex` |
| Ch.1 Introduction | draft exists | IMPORTED | `src/chapters/1_introduction.tex` |
| Ch.2 Fundamentals (+lineage table) | draft exists | IMPORTED (inlined) | `src/chapters/2_fundamentals.tex` |
| Ch.3 CBIC re-typeset | paper source | RE-TYPESET | `src/chapters/3_cbic.tex (+ ADAPTATION_LEDGER)` |
| Ch.4 CoUrb EN re-typeset | EN source | RE-TYPESET, L5 PASS | `src/chapters/4_courb.tex (+ ADAPTATION_LEDGER)` |
| Ch.5 MobiWac re-typeset | VoR source | RE-TYPESET, re-synced (no drift) | `src/chapters/5_mobiwac.tex (+ ADAPTATION_LEDGER)` |
| Ch.6 Conclusion | draft exists | IMPORTED | `src/chapters/6_conclusion.tex` |
| Global bibliography (numeric) | 3 donor bibs | MERGED, 99 entries, 0 dangling | `src/references.bib (+ BIB_MERGE_REPORT)` |
| Front matter (Resumo/Abstract/lists) | planned | DRAFTED [sign-off] | `src/0_main.tex` |
| Appendix A (BRACIS contribution) | planned | DRAFTED [sign-off] | `src/chapters/apx_a_contributions.tex` |
| Appendix B (errata reconciliation) | 3 ERRATA.md | COMPILED | `src/chapters/apx_b_errata.tex` |
| Appendix C (AI-use disclosure) | planned | DRAFTED [sign-off] | `src/chapters/apx_c_ai_disclosure.tex` |
| Full-document gates (N4/R3/L3/L4/§7) | planned | RUN + fixed | `src/_gates/{N4_R3_REPORT,L3_L4_STYLE_BUILD_REPORT}.md` |
| 18-persona review suite | planned | RUN (Opus 4.8) | `src/_review_v1/*.md + CONSOLIDATED_REVIEW_REPORT.md` |
| Title | OPEN by design | STILL OPEN (blocker #1) | `placeholder + candidates in 0_main.tex` |
| CoUrb figure distribuicao_estados.png | thought absent | PRESENT (plan note was stale) | `used in Ch.4` |

**No BLOCKING gap prevented assembly** (Phase-0 verdict was GO). The two remaining blockers
(title, CBIC counts) are author actions known-open from the start, not assembly failures.

## 2. What was built where (+ ledger pointers)

- **Build (round-2 layout):** `cd src && make defense` (→ `build/main.pdf`, copied to
  `src/dissertacao.pdf`, **103 pp**, banca PDF) / `make final` (→ `build/main_final.pdf`, **98 pp**,
  AcademicoPG upload). ONE `main.tex` now (defense default; `make final` sets `\FINALBUILD` on
  the command line — no second main). All compile output goes to `src/build/` (gitignored).
  Recipe + TeX-tree notes: `src_utils/README_SRC.md`.
- **`src/` layout (Overleaf-clean):** `src/` contains ONLY what compiles — LaTeX source +
  `chapters/` (`.tex` only) + `figures/`/`tables/` + the one `dissertacao.pdf` at the root +
  `build/` (gitignored output). Paste `src/` straight into Overleaf. **`src_utils/`** is a
  SIBLING of `src/` (one level up, `articles/dissertacao/src_utils/`) and holds all non-LaTeX
  (this handoff, README, `check.sh`, reports, `_gates/`, `_history/_review_v1/`, `_specialists_v1/`,
  `adaptation_ledgers/`, the CBIC recompute result, the pt_BR
  decisions doc); **`src/build/`** holds compile output.
- **Numbers/citations ledgers:** per-chapter `src/chapters/{3,4,5}_*_ADAPTATION_LEDGER.md`
  (every departure from the published text, feeding Appendix B); `src_utils/evidence/BIB_MERGE_REPORT.md`
  (99-entry key-mapping table + provenance + errata applied); Ch.1/6 citation ledgers in the
  frozen `storyline/drafts/{1,6}_citations.md`; Ch.2 in `fundamentals/DRAFT_LEDGER.md`.
- **Gate + review evidence:** `src_utils/_gates/` (N4 numeral, R3 citation, L3/L4/style/build);
  `src_utils/_history/_review_v1/` (18 persona reports + `CONSOLIDATED_REVIEW_REPORT.md`);
  `src_utils/_specialists_v1/` (the three configured-profile runs on the corrected v1).
- **Exemplars:** `exemples/` now holds five calibration dissertations (germano, viegas, +
  round-2: canesche, passe, lapsusvgi with PROVENANCE.md each); the deepened analysis is
  `reviewers/research/calibration_recheck_2026-07-24.md`. `exemples/` is gitignored (large PDFs).
- **Freeze:** `storyline/` and `fundamentals/` are FROZEN (READMEs carry the pointer); `src/`
  is the single working copy. Edit `src/chapters/` and rebuild — never the draft folders.
- **Commits (this build, `draft(ai):` prefix):** phase0b `415c5cd3`, skeleton `a735b8f3`,
  ch3-5 `1a29b545`, frame `70e794f1`, bib `80fb133c`, front/back `0ccbdebe`, phase-6 gate fixes
  `49a67996`, phase-7 fix loop `5374d511`, reviews `9742ea5c`, phase-8 docs `bb64e220`.

## 3. Ranked flag ledger — [VERIFY] and [NEEDS SIGN-OFF] (title first)

### Tier 1 — BLOCKERS (must clear before the banca build)
1. **[TITLE]** open decision — folha de rosto + Resumo + Abstract + pdftitle. Candidates in source. **Author decides.**
2. **[VERIFY] CBIC dataset counts** — `3_cbic.tex:235`, renders in PDF p.35. Sanctioned recompute. **Author runs.**
3. **[NEEDS SIGN-OFF] B.1 Ch.5 CBIC misattribution** — `5_mobiwac.tex:44,140` say CBIC studied
   next-region and *observed* negative transfer (both false; inherited from the under-review
   paper). Repair text ready in `_history/_review_v1/CONSOLIDATED_REVIEW_REPORT.md (sec. 14_adversarial_advisor_report.md)` §B.1 → ERRATA route. **Author approves.**

### Tier 2 — [NEEDS SIGN-OFF] drafted content (approve or revise; the text compiles as-is)
4. **Resumo (PT) + Abstract (EN)** — `0_main.tex:174,236`, claim-parity pair from Ch.1/6 (certified parallel by 03/08).
5. **Appendix C AI-use disclosure** — `apx_c_ai_disclosure.tex:11`, one page, from the git trail; confirm scope + add the Opus-4.8 deviation line.
6. **Appendix A (BRACIS)** + **Appendix B (errata)** — `apx_a:17`, `apx_b:20`, new frame prose around quoted content.
7. **Ch.5 preface + dual recap + restored embquality figure** — `5_mobiwac.tex:18,82,417`, mandated new-to-chapter text.
8. **Gate-fix rewordings:** B-5 Song-93%-scope `2_fundamentals.tex:40`; B-2 64.51 convention `6_conclusion.tex:79`;
   L3 dedup A-1/A-2 `1_introduction.tex:79` + `2_fundamentals.tex:512`. All verdict-neutral; revert paths in the comments.

### Tier 3 — queued fixes not yet applied (review suite; need your call)
9.  **MJ-2 superiority-test naming** — Ch.2 says Wilcoxon, Ch.5 uses paired t at n=4. Scope to frame+Ch.5; defend the choice.
10. **MJ-3 user-disjoint CV scope** — Ch.2 sells it document-wide; only Ch.5 uses it. Scope + add one Ch.3 disclosure sentence.
11. **MJ-4 region pre-registration framing** — state region was pre-registered non-inferiority; superiority confirmed post-hoc.
12. **MJ-5 data vintage** — Ch.6 '2009 and 2010' vs measured 2009–2011. **MJ-6 93% ceiling** — Ch.2 §2.1 half fixed (B.5); confirm.
13. **MJ-8 'next-POI' task-name bridge** — one preface sentence in Ch.3/Ch.4 (Ch.5 already models it).
14. **MJ-17 class-weighting** — Ch.2 says class-weighted CE; Ch.5 unweighted + reports weighting hurt. **MJ-18 'MTLnet' naming seam** (persona 04).
15. **Visual:** Fig 2 Portuguese labels (regen EN); Fig 3 color-only Food/Shopping (regen grayscale-safe); chapter-title line-breaks; Table 1 overflow (~1cm).
16. **VETOED — do NOT run mechanically:** the 'at [dataset]' preposition sweep (persona 14 VETO — collides with the frozen verdict scopes; fix only non-verdict instances).
17. **Guard on persona-recommended NEW citations.** Some domain reports (e.g. persona 10) suggest ADDING an external work not currently cited (it names `arXiv:2311.04698`). No such citation was added to the dissertation or the bibliography — these are recommendations only. Per the fail-closed protocol (AGENT_GUARDRAILS §1), verify any such identifier against its source of record BEFORE adding it; do not add on the reviewer's word alone.

## 4. Gate statuses (after the fix loop)

| Gate | Status |
|---|---|
| Build both modes | **PASS** — **103/98 pp** (measured 2026-07-27, full three-pass build of the current source; the 87/83 at assembly and 89/84 at round 2 predate the round-4 and round-5 corrections), 0 errors, 0 undefined refs/cites, 0 overfull hboxes |
| Lint (check.sh) | **PASS** — exits 0 (em-dash 0, contractions 0, banned words 0, codenames 0) |
| N4 numeral (06) | **CONDITIONAL** — 0 fabrications, 0 mismatch; blocks only on CBIC placeholders |
| R3 citation (05) | **PASS** — 99/99 real, 0 fabrications, Gowalla mis-source fixed |
| Claim honesty (07) | **PASS** — verb-test binding airtight, AZ never upgraded |
| L5 translation (08) | **PASS** — Ch.4 faithful to the PT source |
| Style G3 (03) | **RE-RUN NEEDED** — 'unlocks'/percent fixed; CBIC ban cluster queued (Appendix B) |
| L3/L4 + WRITING_LAW §7 | **PASS** — em-dash 0, cross-refs resolve, parity certified |
| Concordance (04) | **SEAMS** — AL blur fixed; MTLnet-naming + motif residual queued |
| Change gate (14) | **PASS** — 6 landed fixes certified, 6 more applied, B.1/B.8 held for you |
| Two-build (UFV 13) | defense non-compliant ONLY on the title placeholder; final compliant with conditions; all measured rules pass |

## 5. Review-suite verdicts (18 personas, on claude-opus-4-8)

⚠ **Page references in these reports are stale.** The 18 reports in `src_utils/_history/_review_v1/` were
run against the older 87 pp defense build, so every physical-page pointer they carry (for example
"p.35") can be off by several pages against the current 103 pp build. The findings themselves
stand; only the pagination moved.

Full per-persona detail: `src/_review_v1/CONSOLIDATED_REVIEW_REPORT.md`. Headline: **no
fabricated citation, number, or unlicensed claim anywhere.** GATE PASS from 05 (citation), 07
(claim honesty), 08 (L5 translation); 17 (excellence) scores the science 6 OUTSTANDING / 4 GOOD
/ 0 BELOW; 12 (banca) returns *aprovado com correções menores* (45/50). Every FAIL/conditional
traces to the title, the CBIC placeholders, cross-chapter seams, or presentation — not the
experiments. Optional excellence moves (persona 17, for the SBC-CTD lens): a contributions→claims
table in §1.6, a consolidated cross-chapter results table in §6, and an artifacts/reproducibility
appendix. None is a defect; all are frame-only enhancements.

## 6. Author to-do list (in order) — round-2 updated

**Done this round (confirm only):**
- ~~Decide the title~~ → SET to the working option (confirm with advisor; alternates commented).
- ~~Run the CBIC recompute~~ → DONE from the sanctioned ETL output; Ch.3 filled with both bases
  (confirm which basis to keep; see `src_utils/evidence/cbic_recompute_result.md`).
- ~~Approve/revise B.1~~ → FIXED in Ch.5 **and** the MobiWac source (confirm wording; send with
  the next MobiWac review).

**Remaining (all in `src_utils/DECISOES_PENDENTES_ptBR.md` with fill-in fields):**
1. **Confirm the title** with the advisor (Tier 1.1).
2. **Confirm the CBIC basis** — both-bases wording is in place; keep it or reduce to one (Tier 1.2).
3. **Read + approve the Tier-2 `[NEEDS SIGN-OFF]` content** — Resumo/Abstract, Appendices A/C,
   Ch.5 new-to-chapter text. (Tier-2 item 2.5, the gate rewordings, you ruled **leave as-is**.)
4. **Rule on the Tier-3 queued fixes** — superiority-test naming, CV scope, region framing,
   **data vintage (confirmed 2009–2011 this round, Ch.6 says 2009–2010)**, task-name bridge,
   class-weighting, MTLnet naming seam, the figure regenerations. Each has a `DECISAO:` field.
5. **Message the advisor** about the machine-assembled v1 (this note + Appendix C) and the model
   deviation; confirm banca + Art. 22 timing.

## 7. Specialist verification (round 2)

The three configured specialist profiles were re-run on the corrected v1 (full reports in
`src_utils/_specialists_v1/`). Consolidated verdict:

| Profile | Verdict | Note |
|---|---|---|
| **BANCA_SIMULATOR** | **APROVADO COM CORREÇÕES MENORES — 46/50** (up from 45/50 round-1) | Verified all four round-2 fixes render correctly; removing the title placeholder + p.35 scaffolding stopped its hypercritical mode from triggering (text-quality dimension 4→5). |
| **DISSERTATION_REVIEWER** | **APPROVED WITH CORRECTIONS** | No regression to the science; B.1 fix faithful and correctly mirrored; src restructure clean (zero broken refs — confirmed the numeric-only `\ref` scheme means shortened headings cannot leak). 2 MAJORs are round-2 documentation/concordance fallout, 2 MINORs pre-existing. |
| **DISSERTATION_FACT_GATE** | **GATE FAIL → now RESOLVED** | B.1 correction PASS (matches the CBIC record everywhere). It flagged one BLOCKER: the CBIC dataset numbers were on the **wrong basis** (fresh-2026-ETL, not the CBIC-era `filtrado.csv`). Fixed after the run by switching Ch.3 to the CBIC-era basis (10,460/64,454/960,520), with the N_users `[VERIFY]` kept open. **⚠ SUPERSEDED by the author ruling of 2026-07-24** (`src_utils/evidence/cbic_recompute_result.md`:1-10; NORTH_STAR §4 Ch.3): the CBIC-era `filtrado.csv` basis was retired as a prior-ETL artifact, and Ch.3 now reports the CoUrb figures of record, 20,301 users / 65,009 POIs / 990,518 check-ins, matching Ch.4. The `[VERIFY]` flag is cleared. The other items (MTLnet "this task pair" antecedent, a 0.01 rounding note, the storyline ledger 64.54 sync) are MINOR, queued in Tier 3 / the pt_BR doc. |

**Headline:** two of three specialists pass on the corrected v1; the fact gate's single blocker
(CBIC basis) was a real catch and has been fixed. **⚠ The resolution recorded here is superseded**
(author ruling 2026-07-24, `src_utils/evidence/cbic_recompute_result.md`:1-10): the sentence below described
the interim state, in which Ch.3 reported the CBIC-era corpus and the N_users disagreement
(10,460 versus CoUrb's 20,301) was left as an open author `[VERIFY]`. That disagreement is now
settled the other way. Ch.3 reports the CoUrb figures of record (20,301 / 65,009 / 990,518), the
same corpus figures as Ch.4, and no `[VERIFY]` remains on them. No specialist found a fabricated
citation, number, or unlicensed claim, and none found a round-2 regression to the experiments.
6. **Message the advisor** about the machine-assembled v1 (this note + Appendix C) and the model deviation; confirm banca + Art. 22 timing.
7. **Re-sync note:** Ch.5 currently has NO drift vs `[mobiwac]/src/`; if you edit the paper after today, re-run the diff before the advisor build.

_All writes are under `articles/dissertacao/`. Source paper folders and law-file rules were not edited._

---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
