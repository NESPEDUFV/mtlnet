# FRAME_INTEGRATION_REPORT — Ch.1 / Ch.2 / Ch.6 into src/ (2026-07-23)

Integration of the frame chapters into the assembled tree + verification of the frame's
promises against the assembled paper chapters (3/4/5). Prose was NOT rewritten: a
normalized diff (comments stripped, `Chapter~N` <-> `\ref{ch:...}` treated as equal)
shows the imported prose is byte-identical to the gate-passed drafts. Zero new
connective sentences were needed (see §4). Compiled: `make defense` -> 79 pp PDF.

## 1 · What was imported from where

| Target (src/chapters/) | Source | Notes |
|---|---|---|
| `1_introduction.tex` | `storyline/drafts/1_introduction.tex` (draft 1, ledger `1_citations.md`) | Title-candidate header comment block KEPT as a comment. All ledger comments kept. |
| `2_fundamentals.tex` | `fundamentals/fundamentals.tex` (wrapper) + the five section files under `fundamentals/2.*/` (draft 2, panel-reviewed) + `fundamentals/model_lineage_table.tex` | INLINED into one self-contained file, source order 2.1–2.5; each section's trailing citation/number ledger comment kept in place. |
| `6_conclusion.tex` | `storyline/drafts/6_conclusion.tex` (draft 1, ledger `6_citations.md`) | The pending-author-decision header comment (capacity-paragraph prominence) kept. |

## 2 · Mechanical fixes applied (file:line of the RESULT files)

Labels:
- `1_introduction.tex:28` — chapter label `ch:introduction` -> `ch:intro` (the skeleton's
  label; the assembled tree and stubs use `ch:intro`; no file referenced `ch:introduction`).
- `2_fundamentals.tex:9` (`ch:fundamentals`) and `6_conclusion.tex:12` (`ch:conclusion`)
  arrive correct from the drafts; kept.
- All draft section labels kept: `sec:intro:*` (6), `sec:fund:*` (5) + `tab:fund:lineage`,
  `sec:conc:*` (5). Collision check against chapters 3/4/5 + appendices: **zero duplicate
  labels** in the whole `chapters/` set.

Cross-chapter reference wiring (literal `Chapter~N` -> `\ref` against the real labels):
- `1_introduction.tex` — 19 wired pointers (lines 58, 97, 106, 114, 149, 151, 153, 156–157,
  167, 172, 186, 190, 196, 206, 212, 232–235): `Chapter~2`->`ch:fundamentals` (3),
  `~3`->`ch:cbic` (4), `~4`->`ch:courb` (3), `~5`->`ch:mobiwac` (5), `~6`->`ch:conclusion` (3),
  plus the plural `Chapters~3 and~5` pair.
- `2_fundamentals.tex` — 7 wired pointers (in §2.2: `Chapters~3 and~4` pair, `Chapter~4`,
  `Chapter~5`; one `Chapter~5` each in §2.3, §2.4, §2.5). The lineage table's
  `Chapter~\ref{ch:courb}` / `\ref{ch:mobiwac}` cells arrived already wired.
- `6_conclusion.tex` — 18 wired pointers (lines 17–20, 25, 36, 45, 60, 69, 73, 81, 93,
  119–123, 140, 143): `~3`->`ch:cbic` (5), `~4`->`ch:courb` (3), `~5`->`ch:mobiwac` (9),
  plus the plural `Chapters~3 and~4` pair.
- Residual-literal sweep after wiring: 0 `Chapter~N` literals remain in the three files.

Ch.2 inlining mechanics (no prose touched):
- Per-file `% !TeX root` lines removed on inlining (6); the drafts' `../dissertation.tex`
  root comments in Ch.1/Ch.6 updated to `../main_defense.tex` (comment only).
- `model_lineage_table.tex` inlined at the END of §2.2 (`2_fundamentals.tex:206–236`),
  immediately after the paragraph that introduces `Table~\ref{tab:fund:lineage}`
  (line 203) and before §2.2's ledger comment. The wrapper had no `\input` for the table;
  §2.2 is the only section that references it, so this is the mechanically forced placement.
- Wrapper header comment updated to record the inlining (comment only).

Hygiene sweeps on the three result files (prose lines): em-dashes 0, contractions 0,
banned repo codenames 0, unresolved `\ref` 0 (compile-checked).

## 3 · Build

`make defense` with `TEXMFHOME` pointed at the usermode tree compiles clean to
`main_defense.pdf` (79 pages). One environment repair was needed: `updmap-user` had to be
re-run (writable `TEXMFVAR`) to enable `newtx.map`; this is a build-machine state issue,
not a source issue. Remaining warnings are EXPECTED at this phase:
- **235 undefined citations** — `references.bib` still holds only the 2 Phase-1 seed
  entries; the Phase-4 global merge has not run. No action taken here.
- A few `figure.caption.N` pdfTeX dest warnings from the pre-existing paper chapters
  (present before this integration).

## 4 · New connective prose

**None.** The Ch.2 wrapper's roadmap paragraph already existed in the draft; inlining the
sections and the table required no new sentence. Zero sentences were added to any chapter.

## 5 · Verification results (items 1–5)

### 5.1 Ch.1 §Organization bullets vs. prefaces and CLAUDE.md §1 — PASS
- **Ch.3 bullet**: "published in English at the XVII Congresso Brasileiro de Inteligência
  Computacional (CBIC 2025, DOI 10.21528/CBIC2025-1191324), with this author as first
  author" — matches CLAUDE.md §1 (published, that DOI, Vitor 1st) and the Ch.3 preface.
- **Ch.4 bullet**: published PT, X Workshop de Computação Urbana (CoUrb 2026,
  DOI 10.5753/courb.2026.22960), with SBRC 2026, English translation, Tarik S. Paiva 1st
  author, this author 2nd + MTLnet baseline + presenter — matches CLAUDE.md §1 and the
  Ch.4 preface (which adds pp. 323–336) clause for clause. The contribution note required
  by NORTH_STAR §6 beat 7 is present.
- **Ch.5 bullet**: "submitted to the 23rd ACM International Symposium on Mobility
  Management and Wireless Access (MobiWac 2026) and currently under review, with this
  author as first author" — matches CLAUDE.md §1 and the Ch.5 preface (EDAS #1571313639).
  **Status sweep**: no "published/accepted" appears near MobiWac anywhere in the three
  frame files; §1.2's arc paragraph says "submitted to MobiWac 2026 and under review";
  §2.5 forward-points without a status word; the lineage table caption says "submitted,
  under review". PASS everywhere.
- The decision-#7 errata sentence ("re-typeset ... any correction applied afterward is
  listed in the errata appendix rather than silently edited") is present in §1.5.

### 5.2 Ch.1 objectives 1:1 with chapters — PASS
Four objectives, numbered 1–4: (1) naive hard-sharing joint model for the two category
tasks -> Ch.3; (2) representation diagnosis, architecture held fixed -> Ch.4; (3)
check-in-level representation + joint model for next category / next region -> Ch.5;
(4) consolidation under the leakage-guarded protocol -> Ch.6. Each bullet's parenthetical
now resolves via `\ref`. The task-pair evolution (category classification + next category
in objectives 1–2 vs next category + next region in 3) matches the signed-off AVAL
additions and the assembled chapters' actual task pairs.

### 5.3 Ch.2 §2.5 hinge paragraph — PASS
The closing paragraph carries exactly three clauses in chapter order:
1. "whether naive multi-task learning helps at all, given a place-level embedding and hard
   parameter sharing ... an honest answer for that configuration" -> Ch.3's actual content
   (place-level DGI + hard sharing; null result, time-indexed in its preface).
2. "whether the representation, rather than the architecture, is the lever, by decomposing
   and enriching the input the same model receives" -> Ch.4's actual content (MTLnet
   unchanged, decomposed 192-d input; its preface states it isolates the representation
   effect).
3. "what a representation built for check-ins unlocks for a redesigned joint model" with
   verbs bound: "by paired superiority tests, outperforms ... next category everywhere it
   is tested and ... next region at four of six datasets, and matches ... within a
   two-point margin, by non-inferiority testing, at the other two" -> matches Ch.5's
   preface and results section word-for-word in substance (outperforms Istanbul/FL/TX/CA;
   TOST ±2 pp at AL/AZ; AZ never upgraded). §2.5 contains zero `\cite` (synthesis-only
   rule holds).

### 5.4 Ch.6 vs Ch.1 and the assembled chapters — PASS (2 number notes)
- **Loop closes**: Ch.6's opening sentence restates Ch.1's bold research question nearly
  verbatim and answers it conditionally; §6.5 returns to the one-model/one-forward-pass
  operational payoff promised in §1.1 (no compute-cost promise anywhere; the F3 guard
  holds: Ch.1 and Ch.6 both disclose the higher training cost / larger parameter count).
- **Verbs bound to tests**: category "outperforms ... at all six datasets, by 5.3 to 9.4
  macro-F1 points"; region "outperforms ... at four of six, Istanbul, Florida, California,
  and Texas, while remaining statistically non-inferior within a two-point margin (TOST)
  at Alabama and Arizona". Matches Ch.5's assembled results (Ch.5 states +5.33 to +9.35;
  Ch.6's 5.3/9.4 is the NORTH_STAR §2 rounded form — see note N1 below). AZ never
  upgraded. Freeze control scoped to its three named datasets (Alabama, Arizona, Florida)
  — identical to Ch.5's own sentence. Gradient cosine carries its FULL scope (+0.001,
  four seeds, three of six datasets, earlier data preparation, directional only, this
  pair not a general rule) — matches Ch.5's related-work passage. Capacity-baseline
  numbers (4.2M vs 0.6M; 56.16 / 56.82 / 64.54; CA partial fifteen of twenty) match
  `storyline/audit/capacity_baseline_experiment.md` §5.1–5.4 and are explicitly framed
  as post-submission frame analysis.
- **Limitations -> future work 1:1**: six limitations (data vintage, taxonomy coarseness,
  transductive representation, no next-place task, geographic coverage, task-pair
  confound); §6.4 references `limitation~1` through `limitation~6` exactly once each, in
  order. PASS.
- **N1 (note, no action)**: Ch.6 "5.3 to 9.4" vs Ch.5 "+5.33 to +9.35" — consistent under
  standard rounding; the Ch.6 ledger names NORTH_STAR §2 / MobiWac §8 as its source. The
  fact gate should record this as declared rounding (AGENT_GUARDRAILS N4).
- **N2 (note, no action)**: the Ch.6 draft's own header records the pending author
  decision on the capacity-paragraph prominence, and its ledger requires replacing the
  California partial sentence when job 4cff4b00 completes. Both remain open by design.

### 5.5 Cross-chapter \ref audit within the frame — PASS
- Frame -> papers: every wired `\ref{ch:cbic}` / `\ref{ch:courb}` / `\ref{ch:mobiwac}`
  points at the real chapter labels (verified against `3_cbic.tex:9`, `4_courb.tex:9`,
  `5_mobiwac.tex:15`).
- Papers -> frame: chapters 3/4/5 reference only each other (`ch:cbic`, `ch:courb`,
  `ch:mobiwac`), never the frame labels, so replacing the stubs breaks nothing.
- Intra-frame: `sec:intro:arc` (Ch.1), `sec:fund:tasks`/`sec:fund:repr` (Ch.2 internal),
  `tab:fund:lineage` (referenced from §2.2, defined in the inlined table) all resolve.
  Compile log: 0 undefined references (the 235 undefined CITATIONS are the pending
  Phase-4 bib merge, §3 above).

## 6 · [NEEDS SIGN-OFF] queue (wording that would alter or scope a claim; NOT applied)

1. **§2.4 protocol scoping vs Ch.4's split** — `2_fundamentals.tex:436–441` presents the
   user-disjoint grouped splitter as THE validation protocol ("Estimates use stratified
   k-fold cross-validation, and the folds are formed so that no user spans a split"),
   and the chapter roadmap (`2_fundamentals.tex:16–17`) says "the datasets, metrics, and
   validation protocol used throughout". Ch.4's assembled chapter states (preface +
   `4_courb.tex:224`) that ITS split is stratified by sample, not user (firsthand-verified,
   NORTH_STAR §4). A cold reader of Ch.2 could take user-disjoint CV as covering all three
   studies. PROPOSED (one clause, at `2_fundamentals.tex:438`, after "cross-validation
   \cite{kohavi1995crossval},"): "and, in the protocol of the final study, the folds are
   formed so that no user spans a split: ..." — or the author may prefer to leave §2.4
   as the dissertation-level protocol statement and rely on Ch.4's preface, as the
   panel-approved draft implicitly does. Author's call; not applied.
2. **Ch.6 banned idiom "buys"** — `6_conclusion.tex:80`: "Parameter count alone, without
   the second task's training signal, buys nothing here." WRITING_LAW §4 idiom rule bans
   "buys" as a phrasal-metaphor idiom. PROPOSED: "Parameter count alone, without the
   second task's training signal, yields nothing here." Claim-neutral, but it edits
   gate-passed prose, so it is queued rather than applied.
3. **Ch.6 "win" as verdict noun (check.sh hits)** — `6_conclusion.tex:82` ("the win lives
   in the shared trunk") and `:126` ("the size of the win"). The check.sh verdict-verb
   sweep flags them; WRITING_LAW bans "wins" as a result VERB, and NORTH_STAR §6 itself
   licenses "the joint win" as spine vocabulary, so these are likely acceptable — but
   line 82 combines it with "lives in", and "the win lives" is arguably a phrasal
   metaphor. PROPOSED (if the author wants it): "that the gain lives in the shared
   trunk" / "the size of the gain". Queued for the G3 style gate; not applied.
4. **Ch.6 bare "everywhere"** — `6_conclusion.tex:64`: "outperforms the dedicated models
   on the category task everywhere". WRITING_LAW §3 scopes every universal ("at all six
   datasets" only right after the six are enumerated; bare "everywhere" never). §6.1 does
   enumerate the six datasets one section earlier, and the spine's own wording is
   "category outperforms everywhere", so this may be author-sanctioned; §2.5 uses the
   safer "everywhere it is tested". PROPOSED (if wanted): "on the category task at all
   six datasets". Queued; not applied.

## 7 · Notes for the Phase-4 bibliography merge (logged, no action here)

The frame keeps its `\cite` keys AS-IS per instruction. The merge must reconcile these
same-paper key variants now present across chapters:
- DGI: `velickovic2019deep` (Ch.2, Ch.4) / `velivckovic2018deep` (Ch.3) /
  `velickovic2019dgi` (Ch.5) — the known triple-key, consolidation already in the errata
  registry.
- HGI: `huang2023hgi` (Ch.2, Ch.5) / `huang2023learning` (Ch.4).
- HMT-GRN: `Lim2022` (Ch.2, Ch.3, Ch.4) / `lim2022hmtgrn` (Ch.5).
- Cho et al. 2011: `cho2011gowalla` (Ch.2, Ch.5) / `cho2011friendship` (Ch.4).
- Sphere2Vec: Ch.1 cites the normalized short key `mai2023sphere2vec` (per
  `1_citations.md`), Ch.2/Ch.4 the long
  `mai2023sphere2vecgeneralpurposelocationrepresentation`; only the long key exists in a
  donor bib today — the merge must add or alias the short key.
- Ch.2's 26 new keys live in `fundamentals/_bib/new_references_ch2.bib`; the inherited
  errata fixes (misra2016cross DOI, GAT->ICLR, capanema2023poirgnn, nash double-key,
  church2017word2vec->mikolov2013word2vec) are catalogued in the per-article ERRATA.md
  files and `_bib/BIB_NOTES.md`.

## 8 · Source ledger of this integration

Files read for the verification: CLAUDE.md §1 (venue/status owner), NORTH_STAR §3/§4/§6,
WRITING_LAW, GLOSSARY, AGENT_GUARDRAILS §1–§3/L1/L4, the three assembled chapters + Ch.5
results section, `storyline/audit/capacity_baseline_experiment.md` §5, the two draft
ledgers (`1_citations.md`, `6_citations.md`), the Ch.2 review-panel reports and
DRAFT_LEDGER. No number was computed; every number named in §5 was matched by string
against its named source file. Self-reported success is not trusted: the author should
spot-check §5.4's number matches and adjudicate §6 items 1–4.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
