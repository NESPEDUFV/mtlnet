# Consolidated Review Report — Dissertation v1 (18-persona suite)

> 🛑 **GERACAO SUPERADA — nenhum numero deste ficheiro pode ser citado.**
>
> Isto e a suite de 18 personas sobre o build v1, corrido em 23 de julho de 2026, **antes** de a geracao v18 fechar o vazamento de rotulo
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


> Phase-7 deliverable. The full 18-persona review suite was run as fresh sub-agents on the
> `claude-opus-4-8` model (deviation from the plan's Fable mandate, made on the author's call
> after Fable-token exhaustion stalled the wave; logged in the handoff note). Each persona
> received only its persona file and the material its 'Read first' list names; the drafting
> agent reviewed none of its own text (L6). Full per-persona reports are in `src/_review_v1/`.

## 1. Per-persona verdicts

| # | Persona | Verdict | Summary |
|---|---------|---------|---------|
| 01 | Cold reader | **COMPREHENSIBLE — argument holds start to finish** | 3 top findings: next-POI collision, CBIC placeholders (BLOCKER), open title. Friction concentrated in known-open surface items, not the science. |
| 02 | Line editor | **MINOR PASS NEEDED** | All 5 zero-checks pass (em-dash 0, contractions 0). 3 majors: 'at [dataset]' inconsistency, Ch.4 title \:, percent-style. Ch.3/4 items route via Appendix B. |
| 03 | Style auditor | **GATE FAIL (document)** | 3 triggers: CBIC placeholder renders (BLOCKER), 'unlocks' in Ch.2 hinge, CBIC ban cluster. Punctuation triggers all clean. Ch.5 strongest; Ch.4 conditional pass. |
| 04 | Concordance checker | **SEAMS NEED WORK** | No blocker; no result misreported. 3 seams: 'MTLnet' named everywhere but absent in Ch.3; AL 64.51/64.54; weekday-motif residual. Arc threads cleanly. |
| 05 | Citation auditor | **GATE PASS** | 99/99 bib entries real, zero fabrications. 1 major (liu2014 Gowalla mis-source), 2 minor (date/title conventions). R4 errata 100% verified. No [VERIFY] outstanding. |
| 06 | Number auditor | **GATE FAIL (conditional)** | 1 blocker (CBIC placeholders, pre-existing), 0 fabrications, 0 mismatch. ~1225 numerals re-derived; 9/9 tables cell-identical. N-2 (AL 64.51/64.54), N-3 (CA n=15 partial). |
| 07 | Claim honesty auditor | **GATE PASS** | Zero unlicensed claims, verb-test binding airtight, AZ never upgraded. 2 majors straddle number scope (AL blur; data vintage 2009-2010 vs 2009-2011). Honesty devices intact. |
| 08 | Translation fidelity | **L5 PASS** | Ch.4 says exactly what the PT paper says. Tables cell-identical (63/63, 63/63, 9/9). Only departures = documented audited errata. Zero claim-strength drift. |
| 09 | Stats/leakage skeptic | **SURVIVES WITH CORRECTIONS** | Methods sound; holes are textual. B1 (BLOCKER): Wilcoxon vs t-test named two ways. B2/B3 majors: user-disjoint CV overclaimed; region pre-reg framing. Leak audit holds. |
| 10 | MTL expert | **SOUND WITH CORRECTIONS** | 1 BLOCKER: Ch.5 falsely says CBIC studied next-region + observed negative transfer. 2 majors: AL blur; cosine over-generalized to magnitude balancers. Well-armored vs field skepticism. |
| 11 | POI/mobility expert | **SOUND WITH CORRECTIONS** | 1 BLOCKER (CBIC placeholders render). 7 majors incl. 93% ceiling scope, Ch.3 split-axis silence, data vintage, Florida 990k vs 1.4M, no persistence baseline. Ch.5 exemplary. |
| 12 | Banca simulator | **APROVADO COM CORREÇÕES MENORES (45/50)** | 4 obligatory: title placeholder, CBIC scaffolding renders (p.35), AL 64.51/64.54, Wilcoxon-vs-t rigor overclaim. Honest correction-trail arc is the standout. None invalidating. |
| 13 | UFV compliance | **DEFENSE non-compliant as built / FINAL compliant with conditions** | 1 blocker (title renders on folha de rosto). Every MEASURED rule passes both builds (A4, Times 12pt, margins 3/2, 1.5 spacing, page nums). Table 1 overflow 29.8pt minor. |
| 14 | Adversarial advisor | **GATE — 6 landed fixes CERTIFIED** | All 6 phase-6 mechanical fixes certified (no rule broken, no disclosure lost). 6 pending APPROVE-WITH-EDIT (applied this loop). B.1 CBIC misattrib + B.8 preposition held for author. |
| 15 | Readability editor | **READ-WORTHY (overall 8/10; consistency 6/10)** | 1 critical (next-POI task collision), majors: Ch.4 italics, Ch.3 bold, CBIC unparseable sentences. Frame voice unified; surface seam not craft seam. |
| 16 | AI-credibility | **SCREENER MEDIUM / EXPERT-SUSPICION LOW** | Specificity audit PASS (largest credibility asset). 3 items: no front-matter disclosure line; do NOT sterilize Ch.3/4; freeze negative-parallelism count. Provenance shield strong. |
| 17 | Excellence assessor | **6 OUTSTANDING / 4 GOOD / 0 BELOW** | Science uniformly outstanding; every GOOD is packaging not substance. SBC CTD: yes-with-edits. Top moves: contributions->claims table, consolidated results view, artifacts appendix. |
| 18 | Visual presentation | **NEEDS A VISUAL PASS** | 4 majors: Fig 2 Portuguese labels, Fig 3 color-only, chapter-title line-breaks (Viegas defect), Table 1 overflow. Structural level reads as one document; booktabs throughout. |

**Headline:** No persona found a fabricated citation, a fabricated number, or an unlicensed
claim. Persona 05 (citation) and 07 (claim honesty) return outright GATE PASS; 08 (translation)
passes the mandatory L5 gate; 17 (excellence) scores the science uniformly outstanding. Every
gate FAIL / conditional is driven by one of four things: the known-open **title** placeholder,
the known-open **CBIC dataset placeholders**, cross-chapter **consistency seams**, or
**presentation** defects. None is a defect in the underlying experiments.

## 2. Findings inventory (24 items + 1 guard)

Routing: **MECH** = mechanical/defect, landed directly this loop; **SIGNOFF** = touches a
claim, a number's meaning, scope, or the author's voice — queued, never self-approved;
**AUTHOR** = author-only action (recompute or decision).

| ID | Sev | Route | Location | Finding | Status |
|----|-----|-------|----------|---------|--------|
| BL-1 | BLOCKER | AUTHOR | 3_cbic.tex:235 / PDF p.35 | CBIC dataset stats render as literal [VERIFY: recompute per ERRATA.md] placeholders (N_users/N_poi/N_checkins) | AUTHOR (CBIC recompute) |
| BL-2 | BLOCKER | AUTHOR | 0_main.tex folha de rosto + Resumo + Abstrac | Dissertation title is the placeholder [TITLE — open decision] | AUTHOR (title) |
| BL-3 | BLOCKER | SIGNOFF | 5_mobiwac.tex:44,140 | Ch.5 states CBIC prior work studied next-category AND next-region and observed negative transfer — both false (CBIC studied static | AUTHOR (B.1 — ERRATA.md + Appendix B; repair text supplied) |
| MJ-1 | MAJOR | SIGNOFF | 6_conclusion.tex:~79 vs 5_mobiwac.tex Table  | Alabama joint next-category macro-F1 = 64.51 in Ch.5 (joint-best/deploy convention) but 64.54 in Ch.6 (diagnostic-best board value | FIXED B.2 [signoff] |
| MJ-2 | MAJOR | SIGNOFF | 2_fundamentals.tex:442 vs 5_mobiwac.tex:349, | Ch.2 binds 'outperforms' to paired Wilcoxon; Ch.5 uses paired t on per-seed means (n=4); reproduced CBIC/CoUrb say 'significantly  | QUEUED signoff (MJ-2) |
| MJ-3 | MAJOR | SIGNOFF | 2_fundamentals.tex:~ (2.4 'used throughout') | Ch.2 sells user-disjoint CV as the whole-dissertation protocol; only Ch.5 uses it. CBIC/CoUrb code is StratifiedKFold on rows (use | QUEUED signoff |
| MJ-4 | MAJOR | SIGNOFF | 5_mobiwac.tex:5.3/5.6 | Region superiority presented as pre-assigned direction; protocol pre-registered region as non-inferiority. 4 region-superiority cl | QUEUED signoff |
| MJ-5 | MAJOR | SIGNOFF | 6_conclusion.tex limitation 1 | Ch.6 says the five state datasets collected '2009 and 2010'; Ch.5's own measured provenance (figshare dump) runs 2009–2011 and exp | QUEUED signoff |
| MJ-6 | MAJOR | SIGNOFF | 2_fundamentals.tex 2.1 vs 2.4 | 93% predictability is a universal 'ceiling any model should be read against' in 2.1 but disowned in 2.4 (Song's bound is next-loca | QUEUED signoff |
| MJ-7 | MAJOR | MECH | 2_fundamentals.tex:532 ('unlocks'); 3_cbic.t | Hard-banned WRITING_LAW §4 vocabulary in Ch.2 hinge + a CBIC ban cluster the AppB conformance pass missed. | PARTIAL — Ch.2 unlocks FIXED B.3; Ch.3 cluster queued (Appendix B) |
| MJ-8 | MAJOR | SIGNOFF | 3_cbic.tex / 4_courb.tex titles + 3.2.1 (PDF | 'Next-POI Prediction' (35× in Ch.3/4) reads as next-PLACE (which the frame explicitly does NOT predict); 3.2.1 defines it as 'whic | QUEUED signoff (preface bridge) |
| MJ-9 | MAJOR | MECH | 4_courb.tex (italicized common terms), 3_cbi | Ch.4 italicizes ordinary terms every page (leaks into LoF); Ch.3 uses inline bold for emphasis in prose — two register breaks vs t | QUEUED (Appendix B; guard: no sterilize) |
| MJ-10 | MAJOR | MECH | PDF p.46 (fig2_model, Ch.4) | Figure 2 carries Portuguese labels (Encoder Espacial/Temporal/Categórico, Coordenadas, Timestamps) in an English-frame chapter. | AUTHOR/asset (Fig 2 regen) |
| MJ-11 | MAJOR | MECH | PDF p.51 (fig3_embquality, Ch.5) | Figure 3 distinguishes Food from Shopping by color only (red vs orange) — collapses in grayscale. | AUTHOR/asset (Fig 3 regen) |
| MJ-12 | MAJOR | MECH | PDF p.25 etc (chapter title typesetting) | Chapter titles stretch to 3-4 justified lines with mid-word hyphen breaks (Multi-/Task, Ca-/tegory) → two-line running headers + 3 | QUEUED mech (title line-break) |
| MJ-13 | MAJOR | MECH | PDF p.20 (Table 1 model-lineage, 2_fundament | Table 1 overflows right margin by 29.8pt (~1cm). | QUEUED mech (Table 1 width) |
| MJ-14 | MAJOR | MECH | 4_courb.tex:226 | Cites liu2014geographical (a recommendation method) as the source of 'the Gowalla dataset'; canonical dataset keys cho2011gowalla/ | FIXED B.4 + Appendix B |
| MJ-15 | MAJOR | MECH | 4_courb.tex:8 | Chapter 4 title uses \: (math-mode space) in text-mode title; only \: in the build. Same name uses plain colon elsewhere. | FIXED B.6 |
| MJ-16 | MAJOR | MECH | 0_main.tex:265, 1_introduction.tex:114, 6_co | Reported performance uses both 'at' and 'on'/'across' for the same construction; internal inconsistency. | HELD — persona 14 VETO blanket; targeted only + author Q |
| MJ-17 | MAJOR | SIGNOFF | 2_fundamentals.tex:2.4 vs 5_mobiwac.tex:5.4 | Ch.2 says pipeline uses class-weighted cross-entropy; Ch.5 uses plain unweighted CE and reports class-weighting HURT. Direct contr | QUEUED signoff |
| MJ-18 | MAJOR | SIGNOFF | 0_main.tex:251,192 + ch1/2/4/5/6 vs 3_cbic.t | 'MTLnet' is named as the central artifact 'introduced in Chapter 3' by the Abstract, Resumo, and Ch.1/2/4/5/6, but Chapter 3 uses  | QUEUED signoff (MTLnet naming) |
| MN-1 | MINOR | MECH | 2_fundamentals.tex:162-163 (and gate-fix com | The de-dup gate-fix comment claims the 'weekday lunch / Saturday night' image now appears only in Ch.1, but §2.2 still carries a v | QUEUED mech |
| MN-2 | MINOR | AUTHOR | front matter (0_main.tex) + apx_c | AI-use disclosure lives only in Appendix C (last page); 2026 detail-on-demand norm wants a one-line front-matter statement pointin | AUTHOR (front-matter disclosure line) |
| GUARD-1 | GUARD | NONE | Ch.3/Ch.4 (re-typeset published papers) | GUARD (not a fix): do NOT sterilize Ch.3/Ch.4 -ly density or bold/italics beyond mechanical register alignment — they are peer-rev | CONSTRAINT (no action) |

## 3. Fixes applied this loop (6, all gate-approved by persona 14)

Persona 14 (adversarial advisor) certified all 6 phase-6 mechanical fixes and supplied exact
APPROVE-WITH-EDIT text for these 6, applied verbatim:

1. **B.3** `2_fundamentals.tex` — banned word `unlocks` → `enables in` (Ch.2 hinge). MECH.
2. **B.5** `2_fundamentals.tex` — Song 93% rescoped to next-location + forward-ref to §2.4. **[NEEDS SIGN-OFF]** (claim scope).
3. **B.7** `2_fundamentals.tex` — `93\%` → `93 percent` (document convention). MECH.
4. **B.4** `4_courb.tex` — Gowalla cite `liu2014geographical` → `cho2011gowalla,jure2014snap`; orphan key dropped; Appendix B row added. MECH (errata route).
5. **B.6** `4_courb.tex` — chapter-title `\:` → plain colon. MECH.
6. **B.2** `6_conclusion.tex` — AL joint value `64.54` → `64.51` (match Ch.5 table convention). **[NEEDS SIGN-OFF]** (number convention).

Two of the six (B.2, B.5) carry `[NEEDS SIGN-OFF]` LaTeX comments in place: they are the
author's to confirm or revert, though the change itself is verdict-neutral in both cases.
Post-fix rebuild: both modes compile, 0 errors, 0 undefined refs/cites, lint exits 0, page
counts stable (87/83).

## 4. Fixes queued [NEEDS SIGN-OFF] (touch claims/scope/voice — not self-applied)

- **B.1 (BLOCKER, persona 10/14):** Ch.5 falsely states CBIC studied next-region and *observed*
  negative transfer. Inherited verbatim from the under-review MobiWac paper; persona 14 supplied
  exact repair text for both lines (L44, L140) but routed it to the author because it edits an
  under-review paper's claims → ERRATA.md + Appendix B. **Top substantive item; do not ship to
  the advisor unresolved.**
- **MJ-2 (persona 09/12):** superiority test named as Wilcoxon (Ch.2) but t-test (Ch.5) at n=4;
  reproduced papers say 'significantly outperform' with no test. Scope Ch.2's rigor claim to
  frame+Ch.5; defend the parametric choice. Do NOT retrofit tests onto the reproduced papers.
- **MJ-3 (persona 09/11):** user-disjoint CV sold as document-wide in Ch.2; only Ch.5 uses it.
  Scope to Ch.5 + add one disclosure sentence to Ch.3.
- **MJ-4 (persona 09):** region superiority framed as pre-assigned; protocol pre-registered
  non-inferiority. State the post-hoc confirmation; enumerate the family.
- **MJ-5 (persona 07/11):** data vintage '2009 and 2010' (Ch.6) vs measured 2009–2011 (Ch.5).
- **MJ-6 (persona 11/01):** 93% ceiling scope — the Ch.2 §2.1 half is now fixed (B.5); confirm.
- **MJ-8 (persona 01/03/15/11/12):** 'next-POI' task-name collision — add a one-sentence preface
  bridge in Ch.3/Ch.4 (Ch.5 already models it). New connective prose.
- **MJ-17 (persona 09/10):** class-weighting contradiction — Ch.2 says class-weighted CE, Ch.5
  uses unweighted and reports weighting hurt. Correct Ch.2.
- **MJ-18 (persona 04):** 'MTLnet' named across the frame as 'introduced in Ch.3' but absent from
  Ch.3; Ch.4:82 claims the published paper typesets 'MTLNet'. Reconcile via preface bridge.
- **MN-1 (persona 04/03):** weekday-lunch motif residual in §2.2 (gate-fix comment says it lives
  only in Ch.1). **MN-2 (persona 16):** add a one-line front-matter AI-use disclosure.

## 5. Held for the author — VETO / decision (persona 14)

- **B.8 preposition campaign ('at [dataset]' → 'on'/'across'):** persona 14 **VETOED** a blanket
  find-replace — the region-verdict phrasings ('at four of six datasets', 'at AL/AZ') are
  law-mandated verbatim scopes echoed in the Abstract/Resumo/body with certified parity. Fix
  only non-verdict descriptive instances; a verdict-preposition change is a whitelist decision
  (all-at-once or nowhere).
- **Figure 2 Portuguese labels / Figure 3 color-only encoding (persona 18):** asset
  regenerations, not text edits — author/asset work before the advisor build.
- **GUARD (persona 16/03):** do NOT sterilize Ch.3/Ch.4 -ly density or bold/italics beyond
  mechanical register alignment — they are peer-reviewed published text; over-correction reads
  as defensive writing and risks altering published wording. Freeze the negative-parallelism count.

## 6. Re-run gate statuses (after the fix loop)

| Gate | Status |
|------|--------|
| Build (both modes) | PASS — defense 87pp / final 83pp, 0 errors, 0 undefined cites/refs |
| Lint (check.sh) | PASS — exits 0 (em-dash 0, contractions 0, banned words 0 in prose, codenames 0) |
| N4 numeral (06) | CONDITIONAL — 0 fabrications, 0 mismatch; blocks only on CBIC placeholders (author recompute). AL blur fixed (B.2). |
| R3 citation (05) | PASS — 99/99 real, 0 fabrications, Gowalla mis-source fixed (B.4) |
| Claim honesty (07) | PASS — verb-test binding airtight, AZ never upgraded |
| L5 translation (08) | PASS — Ch.4 faithful to PT source |
| Style G3 (03) | RE-RUN NEEDED after fixes — 'unlocks' (B.3) + percent (B.7) fixed; CBIC ban cluster still queued (Appendix B route); placeholder blocker remains author action |
| Concordance (04) | SEAMS — AL blur fixed; MTLnet-naming + motif-residual queued for sign-off |
| Change gate (14) | PASS — 6 landed fixes certified; 6 more applied this loop; B.1/B.8 held for author |

## 7. The two pre-existing blockers (author actions, unchanged by this loop)

1. **Title** — renders as `[TITLE — open decision]` on folha de rosto, Resumo, Abstract,
   pdftitle. Working title + 3 alternates sit in `0_main.tex` comments. Author decides + wire in.
2. **CBIC dataset placeholders** — `3_cbic.tex` renders `[N_users; VERIFY]` etc. on PDF p.35.
   Sanctioned CBIC-Florida recompute is an author action; no number may be invented (correct
   fail-closed handling, but blocks the banca build).

Both are the top two items in the handoff note's ranked action list.


---

# Anexo · Os relatorios de persona da ronda v1, na integra

> **Consolidado em 2026-08-28.** Eram 13 ficheiros irmaos, um por persona, da mesma ronda
> (build 87/83 pp, 23 Jul 2026). O conteudo esta VERBATIM e cada seccao mantem o nome do
> ficheiro original, para que um `grep` pelo nome antigo continue a encontrar o texto.
>
> **Fica de fora, de proposito:** `09_stats_leakage_skeptic_report.md`, porque o texto entregue
> o cita por caminho E por intervalo de linhas (`src/chapters/5_mobiwac/07_discussion.tex:245`
> aponta para `:294-307`). Fundi-lo destruiria a ancora.


---

## `01_cold_reader_report.md`

# Cold Reader Report — main_defense.pdf (v1)

> Persona 01 (cold reader). First-pass comprehension only. No project docs, planning files,
> NORTH_STAR, glossary, or paper folders read — inputs were the persona, the Common protocol,
> and the 87-page document alone. Read-only; no science judgments, no style-law enforcement,
> no grammar lists. Findings = quote + location + why it broke + one-line direction (not applied).
> Document read start to finish once (text layer for all 87 pp; pp.33,35,51,60,62,67,68 also
> rendered as images to check figures/tables), then one organizing pass.

---

## 1. Overall verdict (scope: first-pass comprehension)

**The document is comprehensible and the argument-thread holds from start to finish. I was not
lost in any chapter.** The three-study arc (negative result → representation diagnosis →
resolution) is set up in the abstract and Chapter 1, threaded through a genuinely useful
Fundamentals chapter, and consolidated honestly in Chapter 6; I could state at the end of each
chapter what it claimed and why. The coletânea machinery works: each article chapter opens with a
preface that told me its venue, its date/status, and which later chapters revise it, so I always
knew whether I was reading a "conclusion of the time" or the final position.

Friction is real but concentrated in two buckets, not spread through the argument:
(a) **unfinished surface items that are known-open** — the placeholder title, and three literal
`[VERIFY: recompute …]` dataset numbers printed in the Chapter 3 results; and
(b) **one recurring terminology collision inherited from the reproduced papers** — the term
"Next-POI Prediction" (Chapters 3–4) reads as the one task the dissertation repeatedly says it
does *not* do (next place), when it actually means next *category*.

Neither bucket broke my understanding of the science; both would trip a banca reader on first
contact, and the first bucket is not shippable as-is. Fix those and this reads as one document,
not three stapled papers.

## 2. Top 3 findings (marked)

**① [TOP] "Next-POI Prediction" collides with the frame's core distinction (comprehension).**
Chapters 1–2 work hard to separate *next place* (named, explicitly NOT predicted) from *next
category* (predicted). Then Chapters 3 and 4 title-case "Next-POI Prediction" throughout, which
reads as next-*place*; §3.2.1 (p.27) even defines it as predicting "which specific location a user
is likely to visit next," directly contradicting the same term's definition one page earlier
(p.26: "the category of the next POI"). A reader who believed the abstract stumbles: "didn't they
say they don't predict the exact place?" Recurs 4+ times (pp.26, 27, 41). The prefaces do not warn
that the reproduced term = the frame's "next category." *Direction:* one sentence in the Ch.3 and
Ch.4 prefaces mapping "Next-POI Prediction (as used in this article) = next-category in the frame's
terms"; and disambiguate the two definitions at p.27. (= findings [3-1]/[3-2]/[4-1].)

**② [TOP] Dataset size is three printed `VERIFY` placeholders in the Ch.3 results (p.35).**
"This subset comprises a total of [N_users; VERIFY: recompute per ERRATA.md] users,
[N_poi; VERIFY: recompute per ERRATA.md] unique Points-of-Interest, and [N_checkins; VERIFY:
recompute per ERRATA.md] check-ins." A first reader cannot learn how big the Florida dataset is —
the basic fact the whole chapter rests on — and sees the project's internal review tooling in the
built PDF. It IS disclosed as deliberate ("Pending. Not invented") in errata Table 11 (p.83), but
that disclosure sits 48 pages after the damage. *Direction:* fill the three numbers (or, if truly
pending, render a neutral "(counts pending recomputation)" rather than the raw VERIFY strings)
before any external eyes. BLOCKER if it reaches the banca. (= finding [3-3].)

**③ [TOP] The dissertation has no title (front matter).** Title page (p.1), Resumo (p.3), and
Abstract (p.4) all read `[TITLE — OPEN DECISION NORTH_STAR §5.8]`. As a cold reader I never learn
what the work is called; the abstract's first line carries a bracketed editorial note. Clearly a
known open decision, and it does not impede understanding the argument — but it is the first thing
a banca sees and is unmistakably unfinished. *Direction:* resolve the open title decision before
the defense build ships. (= finding [FM-1].)

## 3. Ranked findings (remaining, most valuable first)

Severity per Common-protocol §5. Each: quote/location + why it broke + one-line direction.

1. **[4-2] MTLnet vs MTLNet — two spellings, late disambiguation.** MINOR. Frame (Ch.1/2) and
   Ch.5 write "MTLnet"; Ch.4 writes "MTLNet" everywhere from its title (p.41) on. The note
   explaining the difference ("the published paper typesets the name as MTLNet") does not arrive
   until §4.2.5 (p.44). *Direction:* move that one-line note into the p.41 preface.
2. **[2-1] The 93% predictability figure lands three times before it is qualified.** MINOR.
   pp.12, 17, 23. Only at §2.4 (p.23) is it bounded ("not a ceiling on seven-class macro-F1 or
   region ranking"). I felt the repetition as "haven't I read this?" before the qualification
   resolved it. *Direction:* qualify at first substantive use (p.17), or trim one instance.
3. **[1-1] Four-task bookkeeping right after the abstract sells "two."** MINOR. §1.1/§1.4 ask the
   reader to track next place (not done), next category (done), next region (done), and a *fourth*
   "category classification" that "also appears" and was later dropped. Handled explicitly, but the
   task count is briefly muddy on first contact. *Direction:* at first mention, one clause —
   "a static, non-sequential fourth task used only in the first two studies."
4. **[4-3] A headline gain the eye cannot verify from its own table.** MINOR. "average gains per
   state are 20.2 to 22.0 percentage points" (pp.51–52, and again p.62/Ch.6), but Table 6 has no
   per-state average row, so I cannot check it on first read. *Direction:* add a per-state mean
   row, or state "averaged over the seven categories."
5. **[5-1] Gradient-cosine sentence with stacked caveats.** MINOR. p.59 §5.2.4: "Measured during
   development on the same joint architecture (on an earlier preparation of the data), the cosine
   similarity … averages +0.001 … (four seeds each on three of our six datasets, per-dataset means
   within ±0.003)." Two nested parentheticals plus "an earlier preparation of the data" made me
   stop to ask whether this is on the final data and whether that matters. *Direction:* split into
   two sentences; state why the earlier-data measurement still stands.
6. **[3-4] Ch.3 re-teaches MTL from scratch (§3.2.2) right after Ch.2 taught it.** MINOR /
   structural. Expected in a faithfully reproduced paper and partly covered by the preface, but as
   a continuous reader I felt the repetition (hard/soft sharing, MoE, GradNorm/PCGrad/DWA all
   re-defined). *Direction:* none required if fidelity is the priority; note only.
7. **[5-2] Table 10 "Dedicated" header names two different models.** NIT. p.67: one "Dedicated"
   under Next-category (the dedicated category model), one under Next-region (the dedicated region
   model). Caption resolves it; first scan read them as one. *Direction:* optional subscripts.
8. **[FIG-1] Figure 3 scatter tick labels near-unreadable at print size.** NIT. p.51. The
   co-location message survives via the caption, but the axis numbers are too small to use.
   *Direction:* larger tick fonts or drop the numeric ticks.

## 4. What holds / what reads well (do NOT "improve" these)

- **The abstract (pp.3–4).** A single clean arc — negative → diagnosis → resolution — every
  sentence resolving. The PT/EN pair is parallel. This sells the whole dissertation in one page.
- **§2.4's binding of verbs to tests.** "outperforms" ← paired superiority test; "matches" ← TOST
  non-inferiority within a stated margin. Stated once, plainly, and it made every later results
  claim legible. Best single paragraph in the frame for a skeptical reader.
- **All of Chapter 5.** Dense, but every term is defined before use; the leakage audit (three
  grounds, p.63–64), the superiority-vs-TOST pre-assignment, and the freeze/capacity controls are
  laid out so a first reader can follow the reasoning. The CTLE-vs-Check2HGI contrast (sequence
  model vs network model) is crisp and memorable.
- **Chapter 6 consolidation.** Reads as genuine synthesis, not a summary of unread things; §6.2's
  conditional yes/no lands the arc.
- **The article-chapter prefaces and Appendix B (errata).** The prefaces did their orienting job
  every time. Appendix B retroactively answered several frictions I had accumulated (the CBIC
  bolding convention, the MTLnet spelling, the p.35 placeholders) — reassuring, not padding.
- **Figures 4 and 5** (the two Ch.5 schematics) are interpretable from the caption alone.

## 5. Out-of-scope handoffs (one line each; not comprehension findings)

- **→ persona 06 (number auditor): cross-page value mismatch.** p.73 §6.2 says the Alabama joint
  model reaches "64.54"; Table 10 (p.67) gives AL Joint category 64.51 ±0.09. 64.54 vs 64.51.
  Caught only because §6.2 restates a table value. Author to rule.

## 6. Open questions (only the author can answer)

- Is the placeholder title (finding ③) blocked on a decision that will land before the defense
  build, or does it need escalation now?
- Are the p.35 dataset counts (finding ②) genuinely pending a recompute script, or can the
  published CBIC values be quoted directly in the interim?
- Is preserving "Next-POI Prediction" verbatim in Chapters 3–4 a hard fidelity requirement (finding
  ①)? If so, a preface bridge sentence is the whole fix; if not, the term itself could be aligned.

---

## Appendix — Running stumble log (raw, in reading order)

### Front matter (pp.1–11)
- **[FM-1] Title is a literal placeholder.** Title page (p.1), Resumo (p.3), Abstract (p.4)
  all read `[TITLE — OPEN DECISION NORTH_STAR §5.8]`. As a cold reader I never learn what the
  dissertation is *called*. Running head/footers throughout say "Chapter N. …" so the doc is
  navigable, but the missing title on the abstract line is jarring. (Known open decision; flag
  so it is not shipped to the banca this way.) — MINOR (BLOCKER only if it reaches the banca).
- Resumo/Abstract (pp.3–4): parallel PT/EN, dense but each sentence resolves. The abstract is a
  single long arc (negative → diagnosis → resolution). Reads well; no stumble.
- Lists of figures/tables (pp.5–7), acronyms (p.8), contents (pp.9–11): complete and navigable.

### Ch.1 Introduction (pp.12–16)
- Reads effortlessly. The three-study arc is set up cleanly; scope ("exact next place is NOT
  predicted") is stated early and repeatedly.
- **[1-1] The "fourth task" bookkeeping.** p.12–13 §1.1 and §1.4: the reader must track four
  tasks — next place (named, not done), next category (done), next region (done), and a
  *fourth*, "category classification," that "also appears" in the first two studies and was
  later dropped. It is handled explicitly (and §1.2/§2.1 revisit it), but on first contact the
  count of "how many tasks am I tracking?" is briefly muddy right after the abstract sold "two."
  — MINOR; direction: none needed, or one clause naming it "a static, non-sequential fourth task
  used only in the first two studies."

### Ch.2 Fundamentals (pp.17–24)
- Strong, linear, didactic. 2.2's one-hot → DGI → HGI → check-in lineage and Table 1 read
  effortlessly. 2.3 MTL taxonomy (hard/soft, negative transfer, balancers, routing) is clear.
- **[2-1] The 93% predictability figure lands three times.** p.12 (§1.1), p.17 (§2.1), p.23
  (§2.4). §2.4 is where it is finally qualified ("not a ceiling on seven-class macro-F1 or region
  ranking"). A cold reader feels the repetition before reaching the qualification. — MINOR.
- What reads well: §2.4 binding of verbs to tests ("outperforms" ← paired test; "matches" ← TOST)
  is unusually clear and I will remember it going into the results chapters.

### Ch.3 Article 1 (CBIC 2025) (pp.25–40)
- Preface (p.25) works: tells me venue, that it is a "conclusion of the time," and that Ch.4/5
  revise it, including the Nash-MTL caveat. This is the coletánea preface doing its job.
- **[3-1] "Next-POI Prediction" collides head-on with the frame's careful vocabulary.** Ch.1/2
  spent real effort separating *next place* (named, NOT predicted) from *next category*. Then
  Ch.3's title and headers say "Next-POI Prediction" everywhere, which reads as next-*place*. On
  p.26 (line 776) it is defined as "Predicting the category of the next POI" — i.e. next category.
  A cold reader who believed the abstract ("the exact next place is not predicted") stumbles hard:
  "wait, didn't they say they don't do this?" The preface does not warn that the reproduced
  article's term "Next-POI Prediction" = the frame's "next category." — MAJOR; direction: add one
  sentence to the p.25 preface mapping the old term to the frame term.
- **[3-2] Same term, two different definitions, adjacent pages (in-article contradiction).**
  p.26 (line 776): "Next-POI Prediction: Predicting the **category** of the next POI a user will
  visit." p.27 §3.2.1 (line 827): "Next-POI Prediction, in contrast, aims to predict which
  **specific location** a user is likely to visit next." Same bold term, category on one page and
  specific place on the next. On first pass I could not tell whether the paper predicts the
  category or the venue. (Inherited from the published paper; §3.2.1 is arguably describing the
  literature's task, but nothing signals that.) — MAJOR; direction: distinguish "the general
  next-POI task (place)" from "our next-POI *category* task" at first use in §3.2.1.
- **[3-3] Raw editorial placeholders in the results text.** p.35 §3.4.1 (line 1137): "comprises a
  total of [N_users; VERIFY: recompute per ERRATA.md] users, [N_poi; VERIFY: recompute per
  ERRATA.md] unique Points-of-Interest (POIs), and [N_checkins; VERIFY: recompute per
  ERRATA.md] check-ins." The dataset size — a basic fact the whole chapter rests on — is missing
  and shows the internal VERIFY tooling in the built PDF. A cold reader cannot learn how big
  Florida is. — BLOCKER if it reaches the banca; at minimum MAJOR. Direction: fill the three
  numbers before any external eyes.
- **[3-4] The chapter opens by re-teaching MTL from scratch.** p.25–29 §3.2.2 re-defines hard/soft
  sharing, MoE, negative transfer, GradNorm/PCGrad/DWA — all already taught in §2.3. Expected in a
  reproduced paper, and the preface sort of covers it, but as a continuous reader I felt "I just
  read this in Ch.2." — MINOR (structural to the coletánea format; note only).
- What reads well: §3.3.3 Nash-MTL bargaining-game explanation is self-contained and clear even
  without the equations rendering perfectly in the text layer.

### Ch.4 Article 2 (CoUrb 2026) (pp.41–55)
- Preface (p.41) works well: translated reproduction, Tarik first author, and — crucially — it
  warns me up front that the split is by-sample not user-disjoint ("a weaker protocol"), and that
  this chapter does NOT revisit MTL-vs-single. Good expectation-setting.
- **[4-1] "Next-POI Prediction" = next category, third and fourth times.** p.41 (line 1361):
  "Next-POI Prediction: predict the category of the next POI." Same collision as [3-1]/[3-2],
  now in Ch.4. Reinforces that this is a *document-wide* hazard: two of three article chapters
  use a term ("Next-POI Prediction") that reads as the one task the dissertation says it does not
  do (next place). — folds into top finding [3-1].
- **[4-2] MTLnet vs MTLNet capitalization.** Frame (Ch.1/2) and Ch.5 write "MTLnet"; Ch.4 writes
  "MTLNet" everywhere (title p.41, preface, intro). The disambiguation note ("the published paper
  typesets the name as MTLNet, and this chapter preserves that form") does not arrive until §4.2.5
  (p.44), several pages after the reader first trips on the two spellings. — MINOR; direction:
  move the one-line note into the p.41 preface.
- **[4-3] A worked "gain" figure the eye cannot verify from the table.** p.51–52: "average gains
  per state are 20.2 to 22.0 percentage points." Table 6 gives per-cell values but no per-state
  average row, so I cannot check the 20.2–22.0 claim against the table on first read. — MINOR;
  direction: add a per-state mean row, or say "computed over the 7 categories."
- What reads well: §4.4.2/4.4.3 walk through Tables 6–7 concretely (naming Nightlife, Travel,
  Food winners), and the Travel-category exception is honestly flagged in both results and
  conclusion. The by-sample caveat is repeated at the table (p.51), not just the preface.

### Ch.5 Article 3 (MobiWac 2026) (pp.56–71) — reading so far pp.56–62
- Preface (p.56) works: "submitted, under review (EDAS #...)", states the resolution cleanly, and
  promises errata for every departure. Status wording is consistent ("under review").
- **Relief: Ch.5 returns to the frame's vocabulary.** "next category" / "next region", and "we do
  not predict the exact next place" restated (p.56, p.60). After Ch.3/4's "Next-POI Prediction",
  this chapter reads as continuous with Ch.1/2. This makes the Ch.3/4 term collision [3-1] feel
  even more like the odd-one-out to fix.
- **[5-1] Dense gradient-cosine sentence with stacked caveats.** p.59 §5.2.4 (lines 2070–2074):
  "Measured during development on the same joint architecture (on an earlier preparation of the
  data), the cosine similarity ... averages +0.001 across training (four seeds each on three of
  our six datasets, per-dataset means within ±0.003)." Two nested parentheticals plus "an earlier
  preparation of the data" made me stop: is this measured on the final data or not, and does that
  matter? — MINOR; direction: split into two sentences and state why the earlier-data measurement
  still stands.
- What reads well: §5.1 intro and the three contribution bullets (p.57) are crisp; the CTLE-vs-
  Check2HGI distinction (sequence model vs network model) is a clean, memorable contrast.
- Ch.5 results (pp.63–71) read very well. §5.5.2/5.5.3 (windows, splitting, integrity, metrics,
  tests) is dense but every term is defined before use; the leakage audit (three grounds) and the
  superiority-vs-TOST assignment are laid out so a first reader can follow the logic. Tables 8–10
  and Figs 6–7 are interpretable from their captions (rendered-page check confirms this).
- **[5-2] Table 10 "Dedicated" header means two different models.** p.67: "Dedicated" appears once
  under Next-category and once under Next-region, denoting the dedicated *category* model and the
  dedicated *region* model respectively. The caption's "improvement over the dedicated model"
  resolves it, but on first scan I read one "Dedicated" model. — NIT.

### Ch.6 Conclusion (pp.72–75)
- Reads as genuine consolidation, not a summary of unread things. §6.2 "consolidated answer"
  (conditional yes/no) lands the arc cleanly. The two controls (freeze; capacity-matched baseline)
  are clearly flagged as frame-level additions run after Ch.5 submission.
- §6.3 six numbered limitations and §6.4 future-work-per-limitation are easy to follow.
- **[OOS-1 | out-of-scope, number-auditor handoff] Cross-page number mismatch.** p.73 §6.2 (line
  2580): the joint model at Alabama is "64.54 for the joint model"; Table 10 (p.67) gives AL Joint
  category = 64.51 ±0.09. 64.54 vs 64.51. I only caught it because §6.2 restates a Table-10 value;
  a true first-pass reader likely would not. Flagging for persona 06 (number consistency), not a
  comprehension finding. Author to rule.

### Appendices (pp.81–87)
- App.A (BRACIS) reads cleanly and explains the rejected iteration and why no result from it is
  cited, pre-empting a "what about BRACIS?" question. The phrase "Substrate Carries, Architecture
  Pays" appears only as the rejected paper's actual (quoted) title. No stumble.
- App.B errata (pp.83–86) is the most reassuring back matter: it retroactively answered several
  "why is this like this?" frictions — the CBIC bolding convention (why HMRM is never bold), the
  MTLnet/MTLNet spelling, and crucially the p.35 placeholders ("Pending. Not invented"). A reader
  who reaches B.1 learns the placeholders are deliberate. That does not remove the p.35 gap (most
  readers hit p.35 long before p.83) but downgrades it from "looks like a bug" to "disclosed item."
- App.C AI-use disclosure reads clearly and is thorough.

### Figure rendered-page check (pp.33,35,51,60,62,67,68)
- Figs 1,3,4,5,6,7 all interpretable from caption + panel. Fig 4/5 schematics read cleanly; Fig 6/7
  bar charts and the Table 10 ↑/≈ markers read well.
- **[FIG-1] Fig 3 (p.51) scatter tick labels near-unreadable at print size**; the co-location point
  survives via the caption, but the axis numbers are too small to use. — NIT.
- p.35 confirms the three `[N_… ; VERIFY: recompute per ERRATA.md]` placeholders print verbatim in
  the built PDF (see top finding [3-3]).

---

## `03_style_auditor_report.md`

# 03 · Style Auditor Report — G3 Style Gate (WRITING_LAW enforcement)

> Persona: `reviewers/03_style_auditor.md`. Scope: ALL SIX chapters
> (`src/chapters/1_introduction.tex` … `6_conclusion.tex`) + appendices
> (`apx_a`, `apx_b`, `apx_c`) + front matter (`src/0_main.tex`).
> Read-only. Enforces `WRITING_LAW.md` (+ inherited MobiWac GLOSSARY §7–§8 ban tables),
> `GLOSSARY.md` term registry. This gate's output is quantitative.
> Method: LaTeX comments stripped before prose sweeps; math/commands/`\cite`/`\ref`/tabular
> content stripped for word-count and -ly density; every hit carries `file:line`.
> All counts are a dated snapshot (2026-07-23); a re-audit replaces numbers, never rules.

---

## VERDICT (per-chapter + document)

**DOCUMENT: GATE FAIL.** Three independent triggers, none of which a mandated exemption
covers: (1) a hard-banned word in the Chapter 2 climax sentence (`unlocks`); (2) a
hard-ban cluster surviving in the re-typeset Chapter 3 prose (`crucial`/`Crucially` ×3,
`enhances` ×2, `surpassing`, `landscape` ×2, sentence-initial `Additionally`); (3) visible
unresolved editorial placeholders in rendered Chapter 3 body text
(`[$N_{\text{users}}$; VERIFY: recompute per ERRATA.md]`). The two re-typeset published
chapters also run over the -ly adverb band (Ch3 1.83%, Ch4 1.24%, band ≈0.8%).

| Chapter | Verdict | Why |
|---|---|---|
| Ch1 Introduction | **PASS** | Zero hard-ban, zero templates, -ly 0.64% (in band), healthy burstiness. |
| Ch2 Fundamentals | **FAIL** | `unlocks` (hard-ban, §2.5 hinge sentence); `co-equal` ×3 (idiom on the replacement list); metaphorical `carry` ×7 (budget ≤3). |
| Ch3 CBIC | **FAIL** | Hard-ban cluster (≥8 hits); participial significance tail; **visible `[VERIFY]` placeholders (BLOCKER)**; -ly 1.83%; `significant(ly)` ×12. |
| Ch4 CoUrb | **CONDITIONAL PASS** | No prose hard-ban words, no templates, no codenames; but -ly density 1.24% over band (MAJOR reservation). |
| Ch5 MobiWac | **PASS** | Hard triggers clean (`enhancements` L46 is the C2-mandated exemption; `frozen weights` glossed); "X, not Y" ×21 within its audited spec; -ly 0.46%. |
| Ch6 Conclusion | **PASS (1 MINOR)** | `frozen` L69 is a pathway, not weights → should be "fixed". -ly 0.48%. |
| Appendices + Front | **PASS (2 notes)** | AppA `substrate` is inside the rejected paper's verbatim title (keep); AppB banned words are all in the errata "published wording" column (documented corrections). Front-matter `[TITLE / banca / date]` placeholders are the documented open decisions — must be filled before the banca build. |

**Auto-fail triggers (document-wide): em-dash = 0, contractions = 0, booster-stacking
(≥2/sentence) = 0.** These are clean and confirmed on the raw files (comments/captions/tables
included). The failure is banned-vocabulary and one presentation blocker, not punctuation.

---

## TOP 3 FINDINGS

1. **[BLOCKER · Ch3 L235] Unresolved `[VERIFY: recompute per ERRATA.md]` placeholders render
   in the body.** The Gowalla-Florida dataset sentence ships three literal bracketed
   placeholders: `"This subset comprises a total of [$N_{\text{users}}$; VERIFY: recompute per
   ERRATA.md] users, [$N_{\text{poi}}$; VERIFY: ...] unique Points-of-Interest (POIs), and
   [$N_{\text{checkins}}$; VERIFY: ...] check-ins."` A reader of the built PDF sees the scaffolding.
   Presentation blocker (the number itself is persona 06's recompute; the *visible placeholder*
   is a style/presentation defect equivalent to an unresolved `\ref`). Must not reach the advisor.

2. **[MAJOR · Ch2 L532] Hard-banned `unlocks` in the frame's climax sentence.** `"It finally
   asks what a representation built for check-ins unlocks for a redesigned joint model"` — the
   §2.5 Relevance hinge, one of the most-read sentences of the fundamentals chapter, uses a
   verb on the leverage/harness/unlock ban list. Direction: "enables", "makes possible", or
   "what a redesigned joint model can do with".

3. **[MAJOR · Ch3, Ch4] The two re-typeset published chapters carry a distributional AI-tell the
   frame chapters do not: -ly adverb density 1.83% (Ch3) and 1.24% (Ch4) against a ≈0.8% band,
   plus a hard-ban cluster in Ch3 that the AppB conformance pass missed** (`crucial`/`Crucially`
   ×3, `enhances` ×2, `surpassing`, `landscape` ×2). AppB documents fixing `leverage`,
   `Moreover`, `underscore`, `Furthermore` in the same file, so the CBIC writing-rule pass was
   started but left incomplete. Ch3 also has the tightest sentence-length variance (CV 43%, 71%
   of sentences mid-length), consistent with the same signature.

---

## 1 · COUNTED WORD / TEMPLATE SWEEP (case-insensitive, whole text, comments stripped)

### 1a · Hard-ban words in the dissertation's OWN prose (exemptions already removed)

| Word (rule) | Loc | Quote (trimmed) | Note |
|---|---|---|---|
| `unlocks` (leverage/harness/unlock) | Ch2 L532 | "…built for check-ins **unlocks** for a redesigned joint model" | Frame §2.5 hinge. Not exempt. |
| `crucial` (pivotal/crucial/vital) | Ch3 L185 | "This is **crucial** for deployment on resource-constrained edge devices" | Reproduced CBIC prose. |
| `crucial` | Ch3 L244 | "Class-wise metrics are **crucial** because category frequencies are highly skewed" | |
| `Crucially` | Ch3 L327 | "**Crucially,** many of these observed differences in F1-scores are minor" | Sentence-initial. |
| `enhances` (enhance-family) | Ch3 L72 | "an inductive transfer mechanism that **enhances** generalization" | Describing MTL generally → "improves". |
| `enhances` | Ch3 L249 | "This model **enhances** a recurrent neural network with a Multi-Head Attention" | Describing MHA+PE → "augments/extends". |
| `surpassing` (surpasses-family) | Ch3 L290 | "significantly **surpassing** MHA+PE in these categories" | → "exceeding"/"outperforming". |
| `landscape` (realm/landscape) | Ch3 L290 | "indicate a competitive performance **landscape**" | → "…the results are competitive". |
| `landscape` | Ch3 L327 | "presents a more competitive **landscape** when compared against" | |
| `Additionally,` (sentence-initial) | Ch3 L139 | "…random shuffling method. **Additionally,** $\vec{s}$ is the global graph embedding" | AppB fixed the twin `Moreover`; this one survived. |

**Exempt hits verified and NOT counted above (evidence checked):**
- **AppB errata table (L108–123, 239–251):** `leverage` ×4, `Moreover` ×2, `Furthermore` ×2,
  `underscore` ×1, `surpass`-in-`standley` venue, `venue` ×4 — all sit in the LEFT "Published
  wording" column documenting corrections already applied, or in venue-erratum prose. Legitimate.
- **Ch5 L46 `enhancements`:** `"We propose two enhancements."` — the C2-mandated contributions
  lead-in, explicitly exempted by MobiWac GLOSSARY §7. Keep verbatim.
- **Front L59 `abnt-emphasize=bf`:** LaTeX package option, not prose.

### 1b · Auto-fail punctuation/format triggers

| Trigger | Count (prose) | Count (raw, incl. comments/tables/captions) |
|---|---|---|
| Em-dash `—` (U+2014) | **0** | **0** |
| LaTeX `---` ligature | 7 | all inside front-matter `[…]` placeholders (title/banca/date) |
| En-dash between words | — | **0** |
| Contractions | **0** | **0** |
| Booster stacking (≥2 intensifiers / sentence) | **0** | — |

### 1c · Template sweep

| Template | Hits | Verdict |
|---|---|---|
| Sentence-initial `Moreover`/`Furthermore`/`Additionally` | 1 (Ch3 L139 `Additionally`) | FAIL — see 1a |
| Participial significance tail | 1 (Ch3 L102: "…, **demonstrating the value of** attention-based models…") | MINOR — promote to a sentence with evidence or cut |
| `not only … but also` | 0 | pass |
| `plays a __ role` | 0 | pass |
| `in today's world` | 0 | pass |
| `Firstly/Secondly/Finally` scaffold | 0 | pass |
| `a wide array of` | 0 | pass |
| `let us / let's examine` (reader-facing meta) | 0 (2 false positives: verb "lets" in Ch5 L239, Front L243) | pass |
| Literal `Read this as:` tag | 0 (Ch5 L586 "We read this as a defense…" is ordinary prose) | pass |

---

## 2 · DENSITY METRICS (numbers)

### 2a · -ly adverb density (band ≈0.8% max; never two -ly in one sentence)

| Chapter | words | -ly | density | status |
|---|---:|---:|---:|---|
| Ch1 Introduction | 1,714 | 11 | **0.64%** | in band |
| Ch2 Fundamentals | 3,611 | 18 | **0.50%** | in band |
| Ch3 CBIC | 4,199 | 77 | **1.83%** | **OVER — 2.3× band** |
| Ch4 CoUrb | 4,268 | 53 | **1.24%** | **OVER — 1.5× band** |
| Ch5 MobiWac | 5,661 | 26 | **0.46%** | in band |
| Ch6 Conclusion | 1,238 | 6 | **0.48%** | in band |
| AppB errata | 1,183 | 9 | 0.76% | in band |

The split is clean: the four freshly-written frame/paper-native chapters (Ch1, Ch2, Ch5, Ch6)
are all comfortably in band; the two re-typeset published chapters (Ch3, Ch4) are the only ones
over. Ch3's top -ly contributors: `simultaneously` ×7, `jointly` ×5, `finally` ×4,
`significantly` ×4, `effectively`/`frequently`/`consistently`/`highly` ×3 each. Many are
functional (jointly, statistically, simultaneously) and legal; the decorative ones
(effectively, frequently, consistently, largely) are the trim targets. No sentence contains two
-ly adverbs (checked).

### 2b · Intensifier / booster counts (≤1 per claim; "significant" only with a test)

| Chapter | n | breakdown |
|---|---:|---|
| Ch3 CBIC | 11 | significantly ×4, highly ×3, very ×1, substantially ×1, strongly ×1, notably ×1 |
| Ch5 MobiWac | 7 | far ×3, entirely ×3, highly ×1 |
| Ch2 Fundamentals | 4 | far ×2, entirely ×1, widely ×1 |
| Ch1 / Ch4 / Front | 1 each | sharply / very / sharply |
| Ch6 + appendices | 0 | — |

No sentence stacks ≥2 boosters. Ch3's `significant(ly)` appears **12×** (L42, 44, 50, 67, 186,
214, 252, 290, 327, 330, 349, 358) — a density flag on its own; several attach to comparison
claims (L252 "significantly outperform HMRM", L290 "significantly surpassing MHA+PE") whose
test-binding is persona 07's call, but the sheer repetition is a style concern here. `far` in
Ch2/Ch5 is used non-decoratively ("far from random", "far below the check-in-level
representation's 75.15") and reads acceptably.

### 2c · "X, not Y" negative-parallelism (honesty device AND a known LLM fingerprint)

Total **27** (`, not <lowercase>`), plus **28** `rather than`. Distribution: **Ch5 21**, Ch1 1,
Ch2 1, Ch4 1, Ch6 1, AppB 1, Front 1. The Ch5 concentration matches the MobiWac paper's own
audited ~21 count and is within its documented spec. **Mandated verbatim keeps present (4 of 5):**
"a neighborhood, not a radio cell" (L213); "not a reproduction of the complete published system"
(L353); "not a claim that we outperform the cascade" (L587); "motivation, not a measured service
result" (L612); plus "a finding, not a hypothesis" (L568). **The keep "a match, not a gain" was
not found verbatim** — Ch5 phrases the Arizona/Alabama case as "matches … within two points" /
"remains non-inferior". The honesty content (non-inferiority, not a win) appears preserved, but
confirming that is persona 07's binding check — see out-of-scope handoffs. The frame's own uses
(Ch1 L115, Ch2 L287, Ch6 L42, Front L257) all scope the central thesis ("the input
representation, not the sharing architecture") — load-bearing, keep.

### 2d · Semicolon braids (a 2-semicolon prose sentence is two sentences; CI/stat notation exempt)

Sentence-level, non-numeric: **0 true prose braids.** The apparent hits are all exempt —
enumerated list colons `(i)…(ii)…(iii)` (Ch3 L74, L85), statistical-interval listings
(Ch5 L301, L554, L559), and one serial-semicolon list with internal commas (AppC L54: "checked
citations…; a separate style gate; and the author's own reading") which is a legitimate
three-item construction. No rewrite required.

### 2e · Metaphorical `carry/carries` budget (≤3 per chapter)

| Chapter | metaphorical carries | status |
|---|---:|---|
| Ch2 Fundamentals | **7** | **OVER** (L29, L69, L133, L190, L200, L227, L503) |
| Ch4 CoUrb | 3 metaphor (L89, L154, L291) + 2 "carried out" (L33, L169, phrasal verb = performed, exempt) | at budget |
| Ch5 MobiWac | 3 | at budget |
| Ch1 / AppA / AppB | 1 / 1 / 3 | in budget |

Ch2 is over: "each visit **carries** its own vector" recurs as the key-idea phrasing (L200,
L227) and mirrors the GLOSSARY gloss, so keep one or two; the others (L29 "carry geographic and
temporal detail", L190 "context these encoders carry", L503 "carries nothing") can become
holds / encodes / has.

---

## 3 · IDIOM SWEEP (phrasal-metaphor idioms at zero; register test on suspects)

| Idiom | Hits | Verdict |
|---|---|---|
| `co-equal` | **3** (Ch2 L91, L335, L498) | **FAIL** — on the MobiWac §8 replacement list ("rephrase around *equal standing*"; bare co-equal collides with the disclosed 0.75/0.25 loss weights). Repeated in the frame. |
| `sits` (on/above) | 1 (AppB L68 "the label … **sits on** the Dataset subsection") | MINOR — law mandates "lies", one verb everywhere; errata-appendix prose describing a fixed bug. |
| edges past / buys / ships / lands / folds in / clears by / comes out ahead / line up / settle on / staging / recent trail | **0** | pass — the MobiWac idiom cleanup held across the re-typeset chapters. |

No money/motion phrasal metaphors survive in the frame or Ch5. This sweep is otherwise clean —
the earlier campaign's idiom discipline transferred well.

---

## 4 · TERM-REGISTRY LINT (L2 — one name per concept; codenames zero; fail-closed on unlisted)

### 4a · Repo codenames in prose (must be ZERO)

| Codename | Hits | Verdict |
|---|---|---|
| `frozen` | 3 | Ch5 L355 "with **frozen weights** (no fine-tuning)" + L370 "With frozen weights" = the sanctioned *frozen-weights* exemption, glossed at first use — **legal**. Ch6 L69 "with the region pathway **frozen**" is a pathway, not weights → **MINOR**, should be "fixed". |
| `substrate` | 1 | AppA L27 — inside the **verbatim italic title** of the rejected BRACIS submission (*"Substrate Carries, Architecture Pays…"*). Title of record; keep as-is. Not a prose concept-use. |
| B9 / v11–v17 / champion-G / H3-alt / dk_ovl / log_T / engine / board / recipe / C2HGI / dualtower | **0** | clean |

Region-transition prior is written out (never `log_T`); "the joint model" is used throughout
(never `mtlnet_crossattn_dualtower`). The codename discipline is essentially intact — one
`frozen` misuse in Ch6.

### 4b · Banned task/place/visit synonyms

| Banned term | Hits | Verdict |
|---|---|---|
| `activity` (for the task) | 9 | **All exempt** — every instance describes another system's own term (MCARNN, iMTL, DRRGNN, CSLSL cascade). Law: "activity appears only when describing other papers." OK. |
| `area` (for region) | 1 | Ch1 L43 "planning resources **by area**" — generic geographic sense in a downstream-uses list, not the next-region task. NIT: "by region"/"geographically" would remove the collision. |
| `venue` | 5 | **All exempt** — publication-venue sense (Ch1 L220 "identifying its venue"; AppB "venue corrected to…"), never place/POI. OK. |
| `event` | 1 | Ch1 L209 "presented the paper at the **event**" = the conference, not a check-in. Exempt. |
| `cell` | 8 | **All legitimate senses** — "grid cell" (mandated full form), "radio cell" (the contrast), "recurrent cell" (LSTM), errata "cell values" (table cells). OK. |
| `zone` | 1 | Ch3 L120 "leisure **zones** are often near residential districts" — reproduced CBIC example of spatial co-location, not the region task. NIT. |
| `run` (for seed) | 12 | Mostly the verb "run" (execute a model) or the idiom "runs to" — legal. Two noun uses read loosely: Ch5 L413 "two independent **runs**" (two model executions, not seeds) and Ch6 L79 "a partial California **run**, fifteen of twenty repetitions" (the "repetitions" gloss saves it). NIT: prefer "training runs"/"the California experiment". |

### 4c · The "Next-POI" label — registry-bridge gap [MAJOR]

The task label **"Next-POI Prediction"** appears **35×** in reproduced Chapters 3 and 4 prose
(defined in Ch3 L35 as "Predicting the **category** of the next POI"). The frame chapters use
only the canonical "next category" in prose ("next-POI" appears in Ch2/Ch5 only inside LaTeX
comments, never rendered). GLOSSARY §1–§2 require the frame to state the per-paper bridge once
(CBIC "next-POI category prediction" = canonical **next-category prediction**). **That bridge is
absent** — no sentence in Ch2, Ch1, or the Ch3/Ch4 prefaces tells the reader that CBIC's
"Next-POI Prediction" is this dissertation's "next-category" task. The collision is real: a
reader who has just been told (Ch1, Ch2, Ch5) that "the exact **next place** is not predicted"
then meets a chapter whose central task is called "**Next-POI** Prediction". The label reads as
the very task the dissertation disclaims. Direction: add one bridging sentence to the Ch3 (and
Ch4) preface — "The task this article calls *Next-POI Prediction* is next-**category**
prediction in the dissertation's terminology (Chapter 2); it is not the exact-next-place task."
Registry violation, fail-closed.

---

## 5 · DISTRIBUTIONAL PASS (variance compression is the deepest tell)

**Sentence-length burstiness** (coefficient of variation of sentence word-counts; higher = more
human variance):

| Chapter | n sents | mean | std | CV% | short<12 / mid / long>28 |
|---|---:|---:|---:|---:|---|
| Ch1 | 65 | 26.4 | 12.9 | **49%** | 14 / 43 / 43 |
| Ch2 | 157 | 23.0 | 12.4 | **54%** | 22 / 52 / 27 |
| Ch3 | 207 | 20.3 | 8.7 | **43%** | 15 / 71 / 14 |
| Ch4 | 175 | 24.4 | 10.8 | 44% | 9 / 59 / 32 |
| Ch5 | 237 | 23.8 | 12.6 | 53% | 16 / 50 / 34 |
| Ch6 | 49 | 25.1 | 14.2 | **57%** | 18 / 47 / 35 |

Ch3 shows the most compressed distribution (CV 43%, 71% of sentences mid-length, only 14%
long) — the same chapter that fails 1a and 2a. This is the mildest of the three signals (43% is
low, not pathological), but it points the same direction: the CBIC chapter reads as the most
uniform. The frame chapters (Ch2, Ch6 especially) show good burstiness.

**Section openers (frame):** varied — Ch2's five sections open five different ways (a definition,
a consequence, a definition, a trust claim, a "these are one argument" synthesis); Ch1 and Ch6
likewise. No single opener template. The apparent duplicates in the Ch5 extraction are
section→subsection pairs sharing the first content sentence (a `\section` immediately followed by
its first `\subsection`), which is normal.

**Section closers (frame):** none ends by restating itself. Ch2 §2.1 closes on a forward hook
("the setting the following sections build the tools for"), §2.4 on the verb-binding rule, §2.5
on "these three questions in turn". Ch6 sections close on distinct concrete statements. Clean.

**Read-aloud spot check (one page/chapter):** the frame prose carries the author's voice
(concessive clauses, mid-paragraph result openers, varied length). No monotone smoothing
detected in Ch1/Ch2/Ch5/Ch6. Ch3 is the flattest to the ear, consistent with the metrics.

---

## 6 · STRUCTURE / PRESENTATION SPOT-CHECKS (Viegas-derived §5)

| Check | Result |
|---|---|
| Table captions **above** the tabular | **PASS** — every table (Ch2 lineage, Ch3 ×3, Ch4 ×2, Ch5 ×2) places `\caption` before `\begin{tabular}`. |
| Figure captions **below** the graphic | **PASS** — every figure places `\caption` after `\includegraphics` (Ch3, Ch4, Ch5 ×4). |
| Table lead-takeaway sentence, no literal "Read this as:" | **PASS** — the literal tag is at zero; Ch4/Ch5 tables are introduced by prose lead sentences (per the Ch4 ledger B4). |
| Metrics defined defensively at first use | **PASS** — macro-F1 (Ch2 L431, Ch5), Acc@10 (Ch2 L411), TOST/OOD-discounted defined; boundary behavior stated. |
| Model-lineage table present (DGI→…→joint model) | **PASS** — Table `tab:fund:lineage` (Ch2 L207), names taken from GLOSSARY. |
| "next category / region / place" kept distinct; disclaimer once, early | **PASS** — "the exact next place is not predicted" stated in Ch1 L172 and Ch2 L56, reinforced Ch5 L205, Ch6 L115. Consistent. |
| Acronyms expanded at first use | **PASS** — LBSN (Ch2 L27), POI (Ch1 L35), MTL (Ch1 L70), DGI/HGI/FiLM (Ch2 L150/154/187), TOST (Ch1 L132), Acc@10 (Ch2 L411) all expanded. STL and GRU (listed in the GLOSSARY §5 acronym set) are **used 0×** in the whole document — no unexpanded-acronym risk; drop them from the List of Abbreviations if they stay unused. |
| `this paper` / "is organized as" leftover in re-typeset chapters | **PASS on "this paper"** (zero); the roadmap sentences correctly say "this chapter" (Ch3 L53, Ch4 L44). Prefaces correctly say "This chapter reproduces the article…". |
| `Dataset N` prose anti-pattern | **PASS** — zero; datasets named (Florida, California, Istanbul…). |
| Unresolved `\ref`/`\cite` (`??`) | none literal in source. |
| **Visible editorial placeholders in body** | **FAIL** — Ch3 L235 `[VERIFY: recompute per ERRATA.md]` ×3 (see Top Finding 1); front-matter `[TITLE / Banca member / defense date]` placeholders (0_main L112–121, 161, 171, 233) are documented open decisions but MUST be resolved before the banca build. |

---

## 7 · RANKED FINDINGS (severity · location · rule · direction)

1. **BLOCKER — Ch3 L235.** Rendered `[VERIFY: recompute per ERRATA.md]` placeholders in the
   dataset sentence. Rule: WRITING_LAW §5 anti-patterns (no leftover scaffolding in body).
   Direction: fill the three counts (persona 06 recompute) or, if not yet available, remove the
   sentence rather than ship the brackets. Blocks the advisor handoff.
2. **MAJOR — Ch2 L532.** `unlocks` (hard-ban, leverage/harness/unlock family) in the §2.5
   climax. Direction: "enables" / "makes possible".
3. **MAJOR — Ch3 (8+ hits).** `crucial` L185/L244, `Crucially` L327, `enhances` L72/L249,
   `surpassing` L290, `landscape` L290/L327, `Additionally,` L139. Rule: AI-tell ban table.
   The AppB pass fixed the sibling words in this file; finish it. Direction: important/central
   (sparingly) or state the fact; improves/augments; exceeds/outperforms; "the results are
   competitive"; delete the sentence-initial connective.
4. **MAJOR — Ch3 1.83% / Ch4 1.24% -ly density.** Rule: §4 density (band ≈0.8%). Direction: cut
   decorative manner adverbs (effectively, frequently, consistently, largely, particularly) in
   the two re-typeset chapters; keep the functional ones (jointly, statistically, simultaneously).
5. **MAJOR — Ch2/Ch3/Ch4 registry bridge.** "Next-POI Prediction" (35×) is never bridged to
   canonical "next-category" and collides with the disclaimed "next place". Direction: one
   bridging sentence in the Ch3 and Ch4 prefaces (see §4c).
6. **MAJOR — Ch2 `co-equal` ×3 (L91, L335, L498).** Rule: MobiWac §8 replacement list.
   Direction: rephrase around "equal standing" / "neither target is subordinate to the other".
7. **MINOR — Ch2 metaphorical `carry` ×7 (budget ≤3).** Direction: keep "each visit carries its
   own vector" (key phrase); convert L29/L190/L503 to holds/encodes/has.
8. **MINOR — Ch3 `significant(ly)` ×12.** Density flag (binding to a test is persona 07's).
   Direction: let the ± spread carry the size; reserve "significant" for test-backed claims.
9. **MINOR — Ch3 L102 participial significance tail** ("…, demonstrating the value of…").
   Direction: promote to a sentence with the evidence, or cut.
10. **MINOR — Ch6 L69 `frozen`** ("region pathway frozen"). Rule: "frozen"→"fixed" except
    glossed weights. Direction: "with the region pathway fixed".
11. **MINOR — AppB L68 `sits on`.** Rule: "lies", one verb everywhere. Direction: "lies on".
12. **NIT — Ch1 L43 `by area`; Ch3 L120 `zones`; Ch5 L413 / Ch6 L79 noun `run(s)`.** Prefer
    "by region"/"geographically"; leave the reproduced `zones` or gloss; "training runs".
13. **NIT — Front matter placeholders.** `[TITLE]`, `[Banca member 1/2]`, `[defense date]` —
    documented open decisions; fill before the banca build (0_main L112–121, 161, 171, 233).

---

## 8 · PROPOSED LAW UPDATES (for author approval — never self-applied)

1. **Add a coletânea-specific rule: reproduced-chapter task labels must carry a one-line
   terminology bridge to the registry at first use in the chapter preface.** The current law
   (GLOSSARY §2) assumes the bridge is stated "once" but does not fix *where*; §4c shows the
   result is that no chapter states it at all. Proposed text: "Where a re-typeset article keeps
   its published task name (e.g. CBIC 'Next-POI Prediction'), its preface states the mapping to
   the canonical registry term once, before the term recurs."
2. **Add `unlock(s)` explicitly to the visible ban table.** It is a leverage/harness-family verb
   but is not spelled out; it slipped into the Ch2 climax. One line in the §7 table.
3. **Promote the -ly density check to a per-chapter reported metric with a hard ceiling for
   re-typeset chapters.** The band is stated but only the MobiWac chapter was ever audited; Ch3
   and Ch4 crossed it undetected. Proposed: "-ly density is reported per chapter at every G3
   pass; >1.0% blocks the gate for any chapter."
4. **Clarify the `frozen` exemption wording** to "frozen *weights only*, glossed; a frozen
   *pathway/branch/layer* is 'fixed'." Ch6 L69 shows the current phrasing is ambiguous.

---

## 9 · WHAT HOLDS / READS WELL (do not touch — avoid pushing the text toward sterility)

- **Punctuation and register discipline is genuinely clean:** em-dash 0, contractions 0, no
  booster stacking, no phrasal-metaphor idioms (edges past / buys / ships / lands / folds in all
  at zero across the re-typeset chapters). The earlier campaign's idiom cleanup transferred.
- **Ch5 (MobiWac) is the strongest chapter stylistically** — in-band -ly (0.46%), the "X, not Y"
  device used as a scoped honesty tool with its mandated keeps intact, the region wording bound
  to its tests, and healthy burstiness (CV 53%). Leave its prose alone.
- **Load-bearing CS vocabulary is used correctly and must NOT be banned:** `framework` (13×,
  all "MTL framework"/"unified framework"), `robust` (5× in Ch3, all technical — robust
  evaluation, robust feature representation), `baseline`, `novel` (1×), `comprehensive` (1×) are
  legitimate. The offense in this document is decoration/stacking and the specific banned tokens,
  not these working words. Do not sterilize.
- **The honesty scaffolding is present and precise:** the "we do not predict the exact next
  place" disclaimer is stated early and consistently; the CBIC/CoUrb conclusions are explicitly
  time-indexed ("the conclusions of the time, for the configuration studied here", Ch3 preface);
  the Nash-MTL benefit is not amplified. This is exactly the register the law asks for.
- **Structure/presentation is compliant:** caption placement correct throughout, lineage table
  present, metrics defined defensively, no "Dataset N", no "this paper" leftovers, roadmap uses
  "this chapter". The Viegas patterns landed.

---

## OUT-OF-SCOPE HANDOFFS (one line each; not this gate's call)

- **Persona 06 (numbers):** Ch3 L235 three dataset counts are unfilled — recompute and fill (I
  flag only the *visible placeholder*, not the value).
- **Persona 07 (claims/honesty):** the mandated keep "a match, not a gain" is absent verbatim;
  Ch5 rephrases the AL/AZ case as "matches … within two points" — confirm the
  non-inferiority-not-superiority content is intact. Also Ch3 L252/L290 "significantly
  outperform/surpassing" — confirm test-binding.
- **Persona 04 (concordance):** STL and GRU are in the GLOSSARY acronym set but used 0× —
  concordance should decide whether they stay in the List of Abbreviations.

---
_End of report. Verdict: **GATE FAIL** (document). Re-run this gate after the fixes land — the
banned-word tables rot, and words creep back through AI-assisted rewrites._

---

## `04_concordance_checker_report.md`

# Persona 04 · Concordance Checker — Cross-Chapter Consistency Report (v1)

> **Status: IN PROGRESS** (writing incrementally; a restart must not lose this).
> Scope: the FULL assembled document as a system — all six chapters + appendices + front
> matter. Checks: terminology/notation concordance, promises-vs-delivery, definitions,
> time-capsule integrity, duplication (L3), cross-references (L4), cross-chapter numbers,
> transitions/seams, Abstract↔Resumo parity.
> Read-only. I judge whether the document AGREES WITH ITSELF, not whether a claim is true
> (persona 07) or a number correct against external sources (persona 06).
> Builds under review: `src/main_defense.pdf` (87pp), `src/main_final.pdf` (83pp).
> Sources: `src/chapters/*.tex` + `src/0_main.tex`.

---

## VERDICT: **SEAMS NEED WORK**

The three chapters are individually sound and the arc (null -> diagnosis -> resolution) is
threaded cleanly: the research question is stated identically in Ch.1 and Ch.6, the region
result wording is locked across all six surfaces (four of six + non-inferior TOST at AL/AZ,
AZ never upgraded), the CoUrb audited numbers (20.2-22.0 pp; 15/21 + 1 tie) agree
chapter-to-appendix to the digit, and the L3 cross-chapter duplication sweep is clean (every
overlap is a sanctioned recap, errata quote, or the deliberately restated research question).
No blocker, and no result is misreported.

What holds the verdict back from "coherent" is a small cluster of **naming/number seams between
the frame and the chapter of record** — most seriously, the central artifact of the whole
document, **MTLnet, is named in the Abstract, Resumo, and Chapters 1, 2, 4, 5, and 6 as "the
model introduced in Chapter 3," yet its own Chapter 3 never uses the name once** — plus one
cross-chapter number that disagrees (Alabama joint category macro-F1: 64.51 in Ch.5's main
table vs 64.54 in Ch.6). These are exactly the seams a coletanea is most exposed to: parts
written apart that no longer point at each other correctly. All are fixable with small,
localized edits; none requires reopening a chapter's science.

## TOP 3 FINDINGS

1. **[MAJOR] "MTLnet" is introduced everywhere except its own chapter.** The name is used as
   the Ch.3 artifact by the Abstract (L251), Resumo (L192), Ch.1 (x4, incl. the Software
   contribution "The MTLnet framework (Chapter~\ref{ch:cbic})"), Ch.2 (lineage table + prose),
   Ch.4 (30+x), Ch.5 (L87), and Ch.6 (L25) — but Chapter 3 names it **zero** times (grep), in
   body and preface alike. A banca member directed to Ch.3 to meet "MTLnet" does not find it.
2. **[MAJOR] Cross-chapter number disagreement — Alabama joint category macro-F1.** Ch.5
   Table `tab:mobiwac:results` (L479) reports the AL joint value as **64.51**; Ch.6 §6.2 (L78)
   reports the same quantity as **64.54**. The dedicated value (56.82) agrees to the digit in
   both; only the joint value differs, and no erratum or "different run" note reconciles it.
3. **[MINOR] The de-duplicated "weekday/Saturday" image was not fully removed.** The L3-fix
   comment at Ch.2 L506 states the image "now appears only in Ch.1," but Ch.2 §2.2 (L162-163)
   still carries it ("visited on a weekday morning or a Saturday night, by a commuter or a
   tourist"), so the motif appears in both Ch.1 (L120) and Ch.2 after a fix that assumed it was
   gone from Ch.2.

---

## Working notes (raw, being refined into findings)

CONFIRMED (evidence captured):
- F-A [MAJOR]: "MTLnet" naming. Ch.3 (re-typeset CBIC) has ZERO "MTLnet"/"MTLNet" in prose
  (grep); published CBIC source only has it in a figure filename `mtlnet_poi.drawio.png` + repo
  `PoiMtlNet`, never as a prose model name. Ch.3 calls it "our MTL model"/"the proposed MTL
  framework". BUT Ch.4 L12+L82, Ch.5 L87, Ch.6 L25, Ch.2 lineage table + prose all name
  "MTLnet ... introduced in Chapter 3". Ch.4 L82 asserts "the published paper typesets the name
  as MTLNet, and this chapter preserves that form" — false vs the reproduced Ch.3.
- F-B [MAJOR]: 64.51 (Ch.5 tab:mobiwac:results, AL joint category) vs 64.54 (Ch.6 L77 capacity
  baseline para). Same dataset/model/task/metric. Hand exact value to persona 06.
- F-C [MINOR]: casing MTLnet (Ch.1/2/5/6) vs MTLNet (Ch.4, 30+x, explicitly sanctioned in-text).
  GLOSSARY canonical = MTLnet. Lineage table row = "MTLnet".
- F-D [MINOR]: "seed" (defined-term, GLOSSARY = one full 5-fold repetition) first USED Ch.1 L243
  "four seeds, five folds", DEFINED only in Ch.5 L349. Abstract correctly avoids it ("random
  initializations"). Ch.6 L88 also uses pre-definition.

PASSES (praise / what holds):
- L4 machine check: all \ref targets resolve to a real \label (built label/ref sets diffed).
  No dangling refs. Orphan (unreferenced) labels exist (eq:cbic:nbs, eq:courb:*, eq:mobiwac:loss,
  conclusion subsecs) — harmless.
- Region result wording locked across Ch.1/2/5/6/Abstract/Resumo: "four of six + non-inferior
  (TOST, 2pp) at AL/AZ"; AZ never upgraded; named set {Ist,FL,TX,CA} identical.
- CoUrb gain 20.2-22.0pp identical Ch.4/Ch.6/AppxB; "15/21 + 1 tie" identical Ch.4/AppxB.
- Category gain 5.3-9.4 (frame) consistent w/ Ch.5 +5.33..+9.35 under rounding.
- Abstract<->Resumo structural parity holds (same beats, same numbers, keywords mirror).
- Massive-STEPS spelling uniform; census tract / mahalle consistent; 520 Istanbul regions
  consistent within Ch.5.

---

## FINDINGS (ranked)

Locations are `file:line` in `src/` (chapters under `src/chapters/`, front matter in
`src/0_main.tex`). "Suggested direction" is never applied (read-only persona).

---

### 1 · [MAJOR] Terminology — "MTLnet" named as the Chapter 3 artifact everywhere but in Chapter 3

**Both sites quoted.** The frame and the two later paper chapters treat "MTLnet" as a proper
name introduced by Chapter 3:
- Abstract, `0_main.tex:251`: *"The first study built **MTLnet**, a joint model with a
  place-level embedding as input and hard parameter sharing"* (Resumo mirror, `0_main.tex:192`).
- Ch.1 `1_introduction.tex:102`: *"built the first joint model of this research, **MTLnet**"*;
  and the Software contribution, `1_introduction.tex:236`: *"The **MTLnet framework**
  (Chapter~\ref{ch:cbic})"*.
- Ch.2 lineage table, `2_fundamentals.tex:224`: row *"**MTLnet** ... First joint model ...
  \cite{silva2025mtlnet}"*, and §2.3 prose `2_fundamentals.tex:374`: *"Its own starting model,
  **MTLnet**, applies hard parameter sharing"*.
- Ch.4 preface, `4_courb.tex:12`: *"the baseline model **MTLNet**, introduced in
  Chapter~\ref{ch:cbic}"*, and `4_courb.tex:82`: *"the joint architecture introduced in
  Chapter~\ref{ch:cbic} \cite{silva2025mtlnet}; **the published paper typesets the name as
  MTLNet**, and this chapter preserves that form."*
- Ch.5 `5_mobiwac.tex:87`: *"Chapter~\ref{ch:cbic} introduced **MTLnet**, the first joint
  model"*; Ch.6 `6_conclusion.tex:25`: *"Chapter~\ref{ch:cbic} contributed **MTLnet**"*.

**The contradicting site:** Chapter 3, the chapter of record, calls the model *"our MTL model"*,
*"our proposed MTL model"*, *"the proposed MTL architecture"*, and *"the MTL framework"*
throughout (e.g. `3_cbic.tex:44,111,120,247,354`) and **never once writes "MTLnet"/"MTLNet"** in
prose, preface, caption, or heading (verified: `grep -c` = 0). This is faithful to the published
CBIC article, whose source contains the string only in a figure filename
(`imgs/mtlnet_poi.drawio.png`) and the repo URL (`PoiMtlNet`), never as a prose model name.

**Why it is a concordance defect, not a style nit.** (a) The reader is explicitly sent to Ch.3
to meet the name ("introduced in Chapter 3", "contributed MTLnet") and does not find it.
(b) Ch.4's assertion *"the published paper typesets the name as MTLNet"* is contradicted by the
reproduced Ch.3 in the same document — an internal self-contradiction about a verifiable fact.
(c) GLOSSARY §2 and WRITING_LAW §2 both make MTLnet the one canonical name and instruct that the
Ch.2 lineage table exists "so the names never blur"; the blur is precisely that the naming
chapter is silent.

**Suggested direction (author's call):** the cleanest fix is one sentence in the Ch.3 preface or
§3.3 naming the architecture ("we refer to this joint architecture as MTLnet"), which also
retro-justifies every "introduced in Chapter 3" downstream and makes Ch.4's "typesets the name
as MTLNet" true of the dissertation. Hand the underlying question — did the *published* CBIC
paper actually name it MTLNet — to persona 05 (Ch.4:82 makes a checkable claim about the source
of record). Note the casing split as part of the same fix (Finding 3).

---

### 2 · [MAJOR] Number disagreement across chapters — Alabama joint next-category macro-F1

- Ch.5 main results table `tab:mobiwac:results`, `5_mobiwac.tex:479`:
  `AL ... 56.82 (Dedicated) ... **64.51** (Joint)`.
- Ch.6 §6.2 capacity-baseline paragraph, `6_conclusion.tex:77-78`: *"its best configuration
  reaches 56.16 macro-F1, against 56.82 for the dedicated model at its own tuned width and
  **64.54** for the joint model."*

Same dataset (Alabama), same model (joint), same task (next category), same metric (macro-F1).
The dedicated value 56.82 matches to the digit across both; only the joint value differs (64.51
vs 64.54, a 0.03 gap). Ch.5 also states the largest category gain is +9.35 at Arizona and gives
AL dedicated 56.82 / joint 64.51 -> +7.69; Ch.6's 64.54 would make it +7.72. No erratum, seed
note, or convention difference reconciles the two.

**My finding is the DISAGREEMENT; the correct value is persona 06's call.** The Ch.5 table is
the source of record per README §Sources (RESULTS_BOARD -> the chapter table), so 64.51 is the
more likely correct value and Ch.6:78 the likely typo, but I do not adjudicate. Hand both exact
values + locations to persona 06.

**Suggested direction:** reconcile Ch.6:78 to the Ch.5 table value once 06 confirms.

---

### 3 · [MINOR] Notation — model-name casing: MTLnet vs MTLNet

Canonical form (GLOSSARY §2, lineage table row, WRITING_LAW §2) is **MTLnet** (lower-case n).
Used correctly in Ch.1 (x4), Ch.2 prose+table, Ch.5 (L80/87/93), Ch.6 (x2), and both Abstract
and Resumo. Chapter 4, however, uses **MTLNet** (capital N) 30+ times and explicitly sanctions
it at `4_courb.tex:82` (*"the published paper typesets the name as MTLNet, and this chapter
preserves that form"*), and Ch.2 quotes the CoUrb form once at `2_fundamentals.tex:224` inside
the ST-MTLNet row. So the document runs two casings for one artifact.

This is defensible IF the Ch.4:82 rationale is accepted (preserve the CoUrb paper's own
typesetting) — but then Ch.2 §2.2 (`2_fundamentals.tex:224`) writes "MTLnet" and "MTLNet" in
the *same paragraph* (the ST-MTLNet sentence: *"MTLnet, replaces the place-embedding input"* in
the What-it-added column while the model column reads MTLNet), which reads as an inconsistency
rather than a deliberate per-paper form. Decide once: either (a) MTLnet everywhere and Ch.4:82's
"preserves that form" sentence is dropped, or (b) keep MTLNet only inside the Ch.4 reproduction
and ensure no frame sentence mixes the two. Tied to Finding 1 — fix together.

---

### 4 · [MINOR] Duplication residue — the "weekday/Saturday" motif not fully de-duplicated

The gate L3-fix comment at `2_fundamentals.tex:506-509` states: *"The 'weekday lunch / Saturday
night out' image now appears **only in Ch.1**"* and reports that the §2.5 hinge was reworded to
avoid the duplication. But the image was removed from §2.5 only, not from §2.2: `2_fundamentals.tex:162-163`
still reads *"the same whether the place is visited on a weekday morning or a Saturday night, by
a commuter or a tourist"*, and Ch.1 `1_introduction.tex:120` carries *"cannot tell a weekday
lunch from a Saturday night out at the same place."* Two chapters, same motif — after a fix that
believed it had localized the motif to one.

Not a blocker (the §2.2 instance is a legitimate first technical statement of the static-vector
limitation, and Ch.1's is the signed-off mechanism beat), but the fix comment's own premise is
now false, which will mislead the next editor. **Suggested direction:** either accept the motif
in both places and correct the L506 comment to say so, or vary the §2.2 image (morning/night is
already a second variant — commuter/tourist — so the repetition is mild). Author's call on
whether it reads as a deliberate motif.

---

### 5 · [MINOR] Definition-before-use — "seed" used in the frame before it is defined in Ch.5

"seed" is a GLOSSARY defined term (one complete repetition of the five-fold experiment). It is
formally defined only in Ch.5, `5_mobiwac.tex:349` (*"A seed is one complete repetition of the
five-fold experiment ..."*), but it is USED earlier in reader order: Ch.1 §1.6/contributions
`1_introduction.tex:243` (*"twenty repetitions per configuration (four **seeds**, five folds)"*)
and Ch.6 `6_conclusion.tex:88` (*"twenty repetitions per configuration (four **seeds**, five
folds)"*). The Abstract/Resumo correctly avoid the bare term (they say "four random
initializations", per GLOSSARY's abstract rule), so the discipline is understood — it just is
not carried into the two frame body chapters that precede the definition.

Mild: "four seeds, five folds" is self-explaining in context. But Ch.2 §2.4 is where the
protocol vocabulary is set up, and it never glosses "seed" (it says "seeds" only in the
NORTH_STAR beat, not in the rendered §2.4 prose — the §2.4 text uses "repetitions"). **Suggested
direction:** add a one-clause gloss at the first frame use (Ch.1:243: "four seeds — four random
initializations of the five-fold experiment — ...") or in the Ch.2 §2.4 protocol paragraph, so
the term is defined at first use per WRITING_LAW §2. Persona 15/03 may also flag this; it is
listed here as a cross-chapter definition-ordering issue.

---

### 6 · [MINOR] Notation — lineage table mixes citation styles for same-status artifacts

`tab:fund:lineage` (`2_fundamentals.tex`) gives its Reference column as `\cite{...}` for DGI,
HGI, and **MTLnet** (`\cite{silva2025mtlnet}`), but as `Chapter~\ref{...}` for **ST-MTLNet**
(Ch.4), **Check2HGI** (Ch.5), and the **Joint model** (Ch.5). MTLnet and ST-MTLNet are both
"an artifact of a paper that is also a dissertation chapter," so a reader sees MTLnet pointed to
by a bibliography key while its sibling ST-MTLNet is pointed to by a chapter number, with no
stated reason for the split. (The MobiWac artifacts have no citeable published record — they are
"submitted, under review" — so Chapter-ref is correct for them; the inconsistency is specifically
MTLnet-via-cite vs ST-MTLNet-via-Chapter-ref, both published.)

**Suggested direction:** either give both published-chapter artifacts a Chapter-ref (and let the
bib key ride the chapter), or give both a `\cite`, so the column reads under one rule. Minor,
but the lineage table is the one place the law says the names/pointers "never blur." Tied to
Findings 1 and 3.

---

### 7 · [NIT] Gowalla vintage — a provenance nuance that does not surface in prose (handoff to 06)

Ch.6 §6.2 (`6_conclusion.tex:108`) and Ch.4 (`4_courb.tex:349`) both date Gowalla to
**2009-2010** ("collected in 2009 and 2010"; "between February 2009 and October 2010"), and
these two rendered statements AGREE. However, Ch.5 carries a hidden provenance comment
(`5_mobiwac.tex` datasets block) noting the actual figshare dump the ETL consumes spans
**2009-01-21 .. 2011-08-16** ("collected 2009 to 2011"), with cho2011 (Feb 2009-Oct 2010) cited
only as the LBSN reference. This never reaches rendered prose, so there is **no cross-chapter
prose disagreement** for me to flag as a concordance defect — but if Ch.5 ever states its own
2009-2011 range in prose, it will disagree with Ch.4/Ch.6's 2009-2010. Flagged to persona 06 as
a latent number issue, not an active concordance break. No action required from a concordance
standpoint today.

---

### 8 · [NIT] Task-name bridge ("next-POI prediction" = next category) present but late

WRITING_LAW/GLOSSARY require the per-paper task mapping (the older papers' "Next-POI Prediction"
= canonical **next category**) to be stated where the reader needs it. Ch.1 §1.1
(`1_introduction.tex:53`) defines next category as "the category of the next visited place" and
the arc paragraph explains the task-pair evolution, and Ch.2 §2.1 keeps the three targets
formally distinct — so the concept is bridged. BUT the *lexical* bridge is implicit: Ch.3 and
Ch.4 use "Next-POI Prediction" 17 and 16 times respectively (their published term), and no frame
sentence says in so many words "what these chapters call next-POI prediction is the next-category
task of this dissertation." Ch.4's preface and recap lean on "MTLNet ... POI Category
Classification and Next-POI Prediction" without the one-line mapping. A CS banca will follow it;
a careful reader may briefly wonder whether "Next-POI Prediction" in Ch.3/4 is the next-place
task Ch.1/Ch.2 explicitly exclude. **Suggested direction:** one bridging clause in the Ch.3
and/or Ch.4 preface ("the task this article calls next-POI prediction is the next-category task
of this dissertation; it predicts the next POI's category, not the exact next place"). Low
severity because §1.1/§2.1 carry the conceptual distinction; listed for completeness.

---

## Duplication report (L3)

Method: comment-stripped, LaTeX-stripped 12-gram sweep across all six chapters + three
appendices, coalesced into shared runs >= 14 words. **Result: clean — every cross-chapter
overlap is sanctioned.**

| Passage pair | Longest shared run | Verdict |
|---|---|---|
| Ch.4 <-> Appx B | "20.2 to 22.0 percentage points, considering the better of the two spatial encoders..." (19w); "Outdoors in Florida where the baseline mean exceeds the best variant by 0.02 pp" (16w) | **Sanctioned** — Appx B errata table quotes the corrected CoUrb values verbatim; identity is required (the erratum IS the quote). |
| Ch.1 <-> Ch.6 | "whether multi-task learning helps point-of-interest prediction for the next category and next region tasks and..." (18w) | **Sanctioned** — the research question, deliberately restated Intro->Conclusion (NORTH_STAR spine; the arc's bookend). |
| Ch.3 <-> Appx B | "about 2.3 times the cumulative 34.97 s of the individual single-task models" (15w) | **Sanctioned** — Appx B errata quotes the corrected Ch.3 wall-time sentence. |
| Ch.1 <-> Ch.3 | "Congresso Brasileiro de Inteligencia Computacional (CBIC 2025) DOI 10.21528/CBIC2025-1191324 with..." (14w) | **Sanctioned** — venue+DOI string, necessarily identical in the organization bullet and the Ch.3 preface. |

No unsanctioned near-duplicate prose across chapters. The mandated recaps are present exactly
where NORTH_STAR §3 places them and nowhere spurious: Ch.4 §4.2.5 "The MTLnet framework"
(`sec:courb:mtlnet-recap`) recaps the Ch.3 artifact; Ch.5 §5.2.1 "The MTLnet framework and the
representation diagnosis" (`sec:mobiwac:related-recap`) recaps BOTH the Ch.3 artifact and the
Ch.4 finding. Both are the sanctioned "The MTLnet framework" pattern; neither repeats the source
paper beyond the recap.

---

## Cross-reference lint (L4)

Machine check: every `\ref` target set diffed against the `\label` definition set across all
nine files. **All 90+ `\ref`/`\autoref` targets resolve to a defined label; no dangling
references.** Spot-checks of semantic targeting (the Viegas precedent shipped refs that compiled
but pointed at the wrong float):

| Cross-reference | From | Resolves to | Semantically correct? |
|---|---|---|---|
| "cascade architectures reviewed in Chapter~\ref{ch:mobiwac}" | Ch.6:151 | Ch.5 | **Yes** — Ch.5 §5.2.4 + §5.6 discuss the cascade (CSLSL/CatDM) at length (7 hits). |
| "Section~\ref{sec:intro:arc} explains why the final study replaced [category classification]" | Ch.1:63 | Ch.1 §1.2 | **Yes** — §1.2 L127 gives the "less natural fit under a per-visit representation" reason. |
| "Chapters~\ref{ch:cbic} and~\ref{ch:courb}" (FiLM conditions on task identity) | Ch.2:188 | Ch.3, Ch.4 | **Yes** — both use FiLM on task identity (Ch.3 §3.3.2, Ch.4 eq. film). |
| "Table~\ref{tab:mobiwac:results}" (the main result) | 8 sites | Ch.5 Table 3 | **Yes** — all point at the joint-vs-dedicated table. |
| Ch.2 lineage "ST-MTLNet ... Chapter~\ref{ch:courb}" / "Check2HGI ... Chapter~\ref{ch:mobiwac}" | Ch.2 table | Ch.4 / Ch.5 | **Yes.** |

Figure/table numbers in prose match the floats (all figures/tables are `\ref`'d, none by hard
number). One observation, not a defect: several equation labels are orphans (never `\ref`'d —
`eq:cbic:nbs`, `eq:courb:concat`, `eq:courb:film`, `eq:courb:time2vec`, `eq:mobiwac:loss`) and
several conclusion-subsection labels are unreferenced; harmless (numbered display equations need
no back-reference), listed only so persona 18/03 need not re-derive it.

---

## Numbers appearing in more than one chapter (concordance view; exact values -> persona 06)

| Quantity | Sites | Agree? |
|---|---|---|
| Research question wording | Ch.1:89-92, Ch.6:22-24, Abstract, Resumo | **Identical.** |
| Category gain 5.3-9.4 macro-F1 | Ch.1:132, Ch.2:530, Ch.5 (+5.33..+9.35), Ch.6:52, Abstract/Resumo | **Consistent** (frame rounds Ch.5's +5.33..+9.35). |
| Region result: 4 of 6 + non-inferior TOST(2pp) at AL/AZ; set {Ist,FL,TX,CA} | Ch.1:135, Ch.2:534, Ch.5, Ch.6:54, Abstract/Resumo | **Identical; AZ never upgraded** anywhere. |
| CoUrb category gain 20.2-22.0 pp | Ch.4:31,304,347, Ch.6:71, Appx B | **Identical.** |
| CoUrb win count 15/21 + 1 tie | Ch.4:295,347, Appx B | **Identical** (published 16/21 correctly relegated to the erratum). |
| Check2HGI vs place-level +28..+40 macro-F1 | Ch.5:33 (+27.63..+39.62), Ch.5 intro "+28 to +40" | Consistent within Ch.5 (rounding). |
| Capacity baseline AL: dedicated 56.82 | Ch.5:479, Ch.6:77 | **Agree.** |
| **Capacity baseline AL: JOINT category macro-F1** | **Ch.5:479 = 64.51; Ch.6:78 = 64.54** | **DISAGREE — Finding 2.** |
| Gowalla vintage 2009-2010 (rendered prose) | Ch.4:349, Ch.6:108 | **Agree** (Ch.5 2009-2011 is comment-only; Finding 7). |
| Parameter counts ~4.2M vs 1.1M (AL) | Ch.1:beat-guard region (scope), Ch.5:257, Ch.6:76 | **Consistent** (Ch.5 4.2M/1.1M; Ch.6 "about 4.2 million ... 0.6 million at its published width" — 0.6M is the dedicated *category* model, not the 1.1M *pair*; NOT a contradiction, but persona 06 should confirm the 0.6M vs 1.1M framing reads cleanly). |

---

## Transitions and seams (the arc)

- **Ch.1 -> Ch.2:** clean. Ch.1 §1.5 announces Ch.2 as "consolidates the background the three
  articles share"; Ch.2 delivers exactly that and closes §2.5 with the three-clause "pressing
  need" hinge pre-motivating Ch.3/4/5. The hinge's three clauses map 1:1 to the three chapters
  and to the four objectives.
- **Ch.2 -> Ch.3 -> Ch.4 -> Ch.5:** the null -> diagnosis -> resolution arc is stated
  consistently in every preface and in Ch.6. Time-capsule prefaces are present on all three
  paper chapters (Ch.3:10, Ch.4:10, Ch.5:20), each naming venue + status + what later chapters
  revise. Ch.4's mandated one-sentence floor ("isolates the representation effect ... does not
  revisit the MTL-versus-single-task question, which Chapter 5 reopens") is present verbatim
  (`4_courb.tex:12`).
- **Corrections cross-referenced both directions:** Ch.3 preface points forward ("Chapters 4
  and 5 revise that verdict"); Ch.4 and Ch.5 point back (recap subsections + "conclusion of the
  time"). Ch.5:141 explicitly reverses the Ch.3 negative-transfer observation on the new
  representation. The Nash-MTL of-the-time caution appears in Ch.3 preface, Ch.4:82, and Ch.6
  reading — consistent.
- **Status wording:** "published" for CBIC/CoUrb, "submitted, under review" for MobiWac —
  consistent across Abstract, Ch.1 bullets, all three prefaces, and Ch.6. No chapter reads
  MobiWac as published (the Ch.5 "published" hits are all about prior work, not its own status).
- **One seam to watch (Finding 1):** the MTLnet naming gap sits on the Ch.2->Ch.3 and
  Ch.3->Ch.4 seams — the reader crosses into Ch.3 expecting the named artifact and the name is
  absent, then crosses into Ch.4 which asserts the name was in the published paper.

---

## Abstract <-> Resumo structural parity (I own the structural half; values -> 06/07)

Structural parity **holds**. Same seven-beat structure, same paragraph order (LBSN/check-in ->
two tasks -> MTL + negative transfer -> three-study arc -> study 1 null -> study 2 diagnosis ->
study 3 resolution + protocol + headline number -> conditional-answer thesis). Numbers mirror:
"twenty repetitions (four random initializations, five folds)" = "vinte repetições (quatro
inicializações aleatórias, cinco partições)"; "5.3 to 9.4 macro-F1 points" = "5,3 a 9,4 pontos
de macro-F1"; "non-inferiority within a two-point margin (TOST)" = "não-inferioridade dentro de
uma margem de dois pontos (TOST)"; verbs bound to tests in both ("outperforms/matches" =
"supera/equipara-se"). Keywords mirror one-to-one (5 each, same order). Both correctly say
"random initializations"/"inicializações aleatórias" rather than the bare term "seed". Hand the
value-by-value and claim-strength halves to personas 06 and 07 as the contract directs; the
structural pair is sound.

---

## What holds / what reads well (do NOT touch)

1. **The arc is genuinely one investigation.** Research question identical at both bookends;
   every preface time-indexes its chapter; the correction trail is explicit and bidirectional.
   This is the hardest thing for a coletanea to achieve and it is achieved.
2. **The region result wording is locked to the digit and the test** across six surfaces
   (Abstract, Resumo, Ch.1, Ch.2, Ch.5, Ch.6): four of six, non-inferior TOST(2pp) at AL/AZ, AZ
   never upgraded, named set {Istanbul, FL, TX, CA} identical everywhere. Exemplary discipline.
3. **CoUrb's audited numbers are consistent chapter-to-appendix** (15/21 + 1 tie; 20.2-22.0 pp),
   with the superseded published values (16/21; 20-24 pp) correctly quarantined in Appendix B and
   never readable as current.
4. **L3 duplication is clean** — no padding, mandated recaps exactly where required.
5. **L4 cross-references all resolve and (on sample) target correctly** — no Viegas-style
   wrong-target refs.
6. **The lineage table exists and is consistent with chapter usage** for artifact identity and
   introduction chapter (the two residual issues — MTLnet-via-cite and the casing — are Findings
   1/3/6, narrow and fixable without touching the table's structure).

---

## Out-of-scope handoffs (one line each; not my verdict to make)

- **-> Persona 06 (numbers):** AL joint category 64.51 (Ch.5) vs 64.54 (Ch.6) — pick the correct
  value; Gowalla 2009-2010 (prose) vs 2009-2011 (Ch.5 provenance comment) latent issue; confirm
  the AL "0.6 million" (Ch.6) vs "1.1 million pair" (Ch.5) framing reads without contradiction.
- **-> Persona 05 (citations):** Ch.4:82 asserts "the published [CBIC] paper typesets the name
  as MTLNet" — verify against the source of record (my read of the CBIC source shows the string
  only in a figure filename + repo URL, not prose).
- **-> Persona 07 (claims/honesty):** Abstract/Resumo value-and-claim-strength parity (I
  confirmed structure only).
- **-> Persona 03/15 (style/readability):** "seed" defined-term first-use ordering (Finding 5);
  the weekday/Saturday motif density (Finding 4) if the author keeps it in both places.

---

## Open questions only the author can answer

1. **MTLnet naming (Finding 1):** do you want the name introduced in Ch.3 (one sentence), or do
   you intend Ch.3 to stay name-free (faithful to the published paper) and have the frame
   introduce the label? If the latter, Ch.4:82's "the published paper typesets the name as
   MTLNet" must be softened, because the reproduced Ch.3 does not show that name.
2. **Casing (Finding 3):** MTLnet everywhere, or MTLnet in the frame + MTLNet preserved only
   inside the Ch.4 reproduction? Either is defensible; the document currently does both without
   a stated rule at the one place they collide (Ch.2:224).
3. **Weekday/Saturday motif (Finding 4):** deliberate motif in both Ch.1 and Ch.2, or de-dupe to
   one? If kept, the L506 fix-comment should be corrected so the next editor is not misled.

---

## `05_citation_auditor_report.md`

# 05 · Citation Auditor — Report (dissertation v1)

**Status: COMPLETE**
**Reviewer:** Citation auditor (persona 05), G2 fact gate, rules R1–R5
**Scope:** ALL SIX chapters (src/chapters/1..6) + appendices + front matter (src/0_main.tex)
**Bib under audit:** src/references.bib (99 entries) + src/BIB_MERGE_REPORT.md
**Donor/template bib (verified):** articles/[mobiwac]/src/references.bib

---

## ★ VERDICT: GATE PASS

**No fabricated entry, no unresolvable entry, no unfixed R4 erratum, and no claim-support
failure on a load-bearing sentence.** One MAJOR finding (F-1, a wrong-source citation for the
Gowalla dataset in Ch.4, inherited from the CoUrb original) should be fixed before the advisor
handoff, but it is a mis-*attribution of a real, correctly-recorded work to the wrong sentence*,
not a fabrication or an unresolvable entry — it does not by itself fail the gate. Everything
else is MINOR/NIT.

**Per-chapter verdicts:**
| Chapter | Entry-level (R1/R2) | Claim-support (R3) | Verdict |
|---|---|---|---|
| Ch.1 Introduction | all cited entries real/attributed | 8/8 sites SUPPORTED | **PASS** |
| Ch.2 Fundamentals | all real/attributed (67 keys, most new-this-pass) | 72/72 sites SUPPORTED | **PASS** |
| Ch.3 CBIC | all real/attributed; R4 errata fixed | all key-sets SUPPORTED | **PASS** |
| Ch.4 CoUrb | all real/attributed; R4 errata fixed | 1 MAJOR mis-cite (F-1) | **PASS w/ F-1 fix** |
| Ch.5 MobiWac | all real/attributed | all key-sets SUPPORTED | **PASS** |
| Ch.6 + apx A/B/C + front matter | citation-free by design (0 `\cite`) | n/a | **PASS** |

**[VERIFY] list for the author:** NONE outstanding. Every one of the 99 entries resolved against
a source of record this session; the 3 inherited `[VERIFY]` caveat-comments in the bib
(kohavi1995crossval Zenodo re-deposit; wilcoxon1945 page range; yang2015tsmc online-first year)
are verification *detail*, not open questions — confirmed benign.

---

## Progress log
- [x] Read persona 05 + reviewers/README common protocol
- [x] Read CLAUDE.md
- [x] Read AGENT_GUARDRAILS §1 (citation protocol R1-R5)
- [x] Read NORTH_STAR §4 (inherited errata for R4)
- [x] Extract all \cite keys per chapter from .tex + .aux
- [x] Parse references.bib entries (99)
- [x] Cross-check: every cite key resolves; orphans; unresolved [?] — 0/0/0
- [x] Entry-level audit — 100% (99/99) against sources of record
- [x] Claim-support audit — 178/243 sites (73%), 100% of Ch.1+Ch.2
- [x] R4 errata check — all 5 fixed
- [x] R5 sweep (no AI output as source) — clean
- [x] Build-level render check (L4) — 0 unresolved markers in 87pp PDF
- [x] Per-chapter verdicts + document verdict — GATE PASS

---

## PART A — Mechanical cross-checks (100% coverage)

**A1. Cite-key ↔ bib-entry closure (rule: every `\cite` resolves; no orphans).**
Extracted every `\cite*` key from the 6 chapter `.tex` + 3 appendix `.tex` + `0_main.tex`,
split multi-key cites, compared against the 99 `@`-entries in `src/references.bib`:
- **99 distinct cited keys = 99 bib entries. 0 dangling (cited-not-in-bib). 0 orphan
  (in-bib-not-cited). 0 duplicate bib keys.** Matches BIB_MERGE_REPORT §1's claim exactly.
- Per-chapter distinct-key counts: Ch.1 = 9, Ch.2 = 67, Ch.3 = 31, Ch.4 = 28, Ch.5 = 33.
  Ch.6 / apx A/B/C carry no `\cite` (conclusion + appendices are citation-free by design).
- **Build-level confirmation (L4 cross-ref lint):** `main_defense.blg` reports
  `warning$ -- 0`, `cite$ -- 99`, 101 entries used (99 + 2 abntex2-options internal),
  **0 undefined citations**. The Viegas precedent's raw-`[?]`/unresolved-key defect class is
  ABSENT. Verified on the committed build, not asserted.

## PART B — Entry-level audit (R1/R2) — 100% coverage (99/99)

Every entry was resolved against a source of record this session (OpenAlex `get_work` by DOI;
arXiv `get_papers` by ID; OpenAlex/arXiv title+author search for identifier-light entries).
Identifier inventory: **63 DOI, 24 arXiv-only, 2 URL-only (FLAN OpenReview; SNAP dataset
`@misc`), 10 "record-only"** (full venue+year+pages, no DOI/arXiv string — all well-known works).

**Result: 99/99 entries are real, correctly attributed works. ZERO fabrications, ZERO
unresolvable entries, ZERO retractions.**

- **63/63 DOIs resolved** on OpenAlex; title/first-author/venue/pages match the bib. Automated
  flags all cleared on inspection (OpenAlex truncates titles at the subtitle colon and reorders
  some author lists — bib is correct in every case: e.g. `kendall2018uncertainty` bib order
  Kendall–Gal–Cipolla is the published order; OpenAlex reversed it).
- **24/24 arXiv IDs resolved** (`arxiv_get_papers`: n_found 24, not_found 0). Titles/authors
  match. One title-convention note below (`ruder2017sluice`).
- **10/10 record-only entries confirmed** by title+author+venue+year against OpenAlex
  (GradNorm/ICML'18, Holm 1979/Scand.J.Statist., Nash-MTL/Navon ICML'22, FAMO/Bo Liu NeurIPS'23,
  Aligned-MTL/CVPR'23, PCGrad/Yu NeurIPS'20, DGI/Veličković ICLR, sklearn/Pedregosa JMLR'11,
  Kurin/NeurIPS'22, `xin2022domtl`/Xin arXiv:2209.11379 NeurIPS'22 — all exact author matches).
- **Provenance-comment convention verified consistent:** every `% PROVENANCE`/`% verified`/
  self-labeled `[key]` block PRECEDES its entry (checked mechanically: 22/22 self-labeled
  annotations align to the following entry, 0 misfiled). No off-by-one in the provenance trail.

### B — findings (entry level)
See ranked findings §FINDINGS below (F-5, F-6, F-7 are the only entry-level items; all MINOR/NIT).

## PART C — R4 inherited-errata check (NORTH_STAR §4) — all FIXED
| Erratum (NORTH_STAR §4) | Required fix | State in bib | Verdict |
|---|---|---|---|
| CBIC: POI-RGNN wrong paper | use `capanema2023poirgnn` | Ad Hoc Netw. 138:103016 (2023), DOI 10.1016/j.adhoc.2022.103016, 5 authors — Crossref-confirmed | **FIXED** |
| CBIC: HMRM author names | `chen2020modeling` 5 authors incl. Yang Liu | Meng Chen, Yan Zhao, Yang Liu, Xiaohui Yu, Kai Zheng; TKDE 34(4):1902-1914; DOI 10.1109/TKDE.2020.3001025 — OpenAlex exact match | **FIXED** |
| CBIC: GAT cite the ICLR version | `velivckovic2017graph` → ICLR 2018 | booktitle Proc. ICLR, year 2018, arXiv:1710.10903 note | **FIXED** |
| CoUrb: `silva2025mtlnet` venue wrong | venue = CBIC 2025, drop "Submetido" | booktitle "Anais do XVII Congresso Brasileiro de Inteligência Computacional (CBIC 2025)", DOI 10.21528/CBIC2025-1191324, no Submetido | **FIXED** |
| (bonus) `paiva2026stmtlnet` 3rd author | restore Germano B. dos Santos | 4 authors incl. Germano B. dos Santos, pp 323-336, DOI 10.5753/courb.2026.22960 | **FIXED** |

## PART D — R5 sweep (no AI output as source): CLEAN
Grepped `references.bib` and all chapter/appendix `.tex` for AI-system / chatbot /
"personal communication" / "generated by" citations: **NONE**. The one lexical hit
(`wei2022finetuned`, "Finetuned Language Models Are Zero-Shot Learners", ICLR 2022) is a
legitimate peer-reviewed work cited as a real MTL-instruction-tuning example, not a laundered
model claim. The AI-use-disclosure appendix (apx_c) correctly carries **zero `\cite`**; apx_a
and apx_b likewise citation-free (the lone `\cite` grep hit in apx_b is inside a comment).
No claim is sourced to a model output.

## PART E — R3 claim-support audit — 73% of sites (178/243), 100% of Ch.1+Ch.2
**Coverage & method.** 243 citation sites total. Read in full context: Ch.1 (8/8) + Ch.2
(72/72) = **100% of the frame + fundamentals**, the highest-AI-share, most-new-entry chapters
(guardrails §5: audit intensity scales with AI share). Ch.3/4/5 (re-typeset published text):
**every distinct key-set site** read (35+28+35 = 98). Total **178/243 = 73%**, far above the
R3 ≥20% floor, and 100% for the entries new-this-pass (Ch.2's fundamentals set). Each cited
system was checked for (a) strength drift, (b) second-hand attribution, (c) description
fidelity ("as its authors describe it"), (d) hedge preservation. 60/99 entries carry the
drafter's own recorded claim/verification note; those were cross-read against the citing
sentence. Recent/sparse works (2022-2025) with specific technical claims were re-verified
against their sources this session (MCMG, DRRGNN, ReHDM, KGTB, HA-MTL, MCARNN, Halder 2021/2022,
Ye 2013, moura2025, sun2025) — all real, all faithfully described.

**Result: one real mis-citation (F-1), otherwise SUPPORTED across the board.** Descriptions are
faithful and appropriately hedged; the fundamentals chapter is notably careful (e.g. the Song
93%-predictability site explicitly states it is "not a ceiling on seven-class category macro-F1
or region ranking"). Verb-test discipline holds where checked (Wilcoxon licenses "outperforms";
TOST licenses "matches").

## PART F — build-level render check (L4)
`main_defense.pdf` (87 pp) extracted and scanned: **0 `[?]`, 0 `??`, 0 raw `\cite`, 0
"undefined"**. Citations render as parenthetical `(n)` marks (abntex2-num style); 97/99 numbers
observed spanning 1-99 (the 2 not matched are a line-break extraction artifact, not missing
entries — BibTeX emitted 99 `cite$` and the key-level check found 0 orphans). Bibliography is
fully wired to the text. The Viegas raw-key defect class is ABSENT.

---

## TOP 3 FINDINGS
1. **F-1 (MAJOR):** Ch.4 line 226 cites `liu2014geographical` (a CIKM-2014 location-recommendation
   *method* paper) as the source of "the Gowalla dataset" — a semantic mis-source. Inherited
   verbatim from the CoUrb original; the same chapter cites the dataset correctly elsewhere.
2. **F-2 (MINOR):** `luca2021mobilitysurvey` year 2021 (bib) vs 2023 issue-year (vol 55(1)) —
   an online-first vs issue-year convention mismatch; not wrong, but state one convention.
3. **F-3 (MINOR):** `ruder2017sluice` uses the arXiv-v1 title "Sluice Networks…"; the work was
   renamed "Latent Multi-task Architecture Learning" (AAAI 2019). Same authors/ID; a title-of-
   record choice worth a note, not an error.

---

## RANKED FINDINGS

### F-1 — MAJOR — Wrong source cited for the Gowalla dataset (Ch.4)
- **Location:** `chapters/4_courb.tex:226` (renders in the CoUrb chapter, results section).
- **Quote:** "The experiments were conducted with the Gowalla \emph{dataset}
  \cite{liu2014geographical} in the states of Florida, California, and Texas".
- **Defect:** `liu2014geographical` = Liu, Wei, Sun, Miao, "Exploiting Geographical Neighborhood
  Characteristics for Location Recommendation," CIKM 2014 (DOI 10.1145/2661829.2662002, verified
  this session) — a recommendation-*method* paper, NOT the source of the Gowalla dataset. The
  canonical dataset sources (`cho2011gowalla`, `jure2014snap`) are cited correctly in the SAME
  chapter at lines 18 and 33, so line 226 is both a semantic mis-source and internally
  inconsistent.
- **Origin:** inherited from the CoUrb original (`articles/CoUrb_2026/src_en/sections/results.tex:7`
  cites `\cite{10.1145/2661829.2662002}` for the same sentence). The merge faithfully renamed the
  slash-key to `liu2014geographical` and preserved the wrong attribution — an R2 defect that
  survived because the merge verified the *entry* (which is a real paper) not the *site*.
- **Suggested direction (NOT applied):** replace with `\cite{jure2014snap}` (matching line 33) or
  `\cite{cho2011gowalla,jure2014snap}` (matching line 18). Author rules; if the errata policy is
  "reproduce verbatim + errata note," this belongs in Appendix B as a corrected-in-dissertation
  item. Either way, remove `liu2014geographical` if it then becomes uncited (it would orphan).

### F-2 — MINOR — luca2021mobilitysurvey year vs issue-year
- **Location:** bib entry `luca2021mobilitysurvey`; cited in Ch.1, Ch.2, and Ch.5.
- **Quote (bib):** `year = {2021}` … `volume = {55}, number = {1}`.
- **Detail:** OpenAlex/ACM record the ACM Comput. Surv. 55(1) issue as 2023 (online-first 2021,
  DOI 10.1145/3485125 — resolves, correct). Title/authors/DOI all match; not a fabrication.
- **Suggested direction:** either keep 2021 with the online-first understanding, or align to the
  issue year 2023; whichever, be consistent with how other online-first entries are dated.

### F-3 — MINOR — ruder2017sluice title of record
- **Location:** bib entry `ruder2017sluice` (arXiv:1705.08142). Cited Ch.3:10,17.
- **Detail:** bib title "Sluice Networks: Learning What to Share Between Loosely Related Tasks"
  is the arXiv-v1 title; the work was retitled "Latent Multi-task Architecture Learning" and
  published at AAAI 2019. Same four authors (Ruder, Bingel, Augenstein, Søgaard), same arXiv ID
  (verified this session). The chapter prose calls it "Sluice networks," so the v1 title is the
  intended reference and is defensible.
- **Suggested direction:** optional — add the AAAI 2019 version of record, or keep the arXiv
  preprint (consistent with several other arXiv-only MTL entries). No action required.

### F-4 — MINOR — Two Halder works, verify the descriptions are not crossed (Ch.3 vs Ch.4)
- **Location:** `chapters/3_cbic.tex` cites `Halder2021`; `chapters/4_courb.tex` cites `Halder2022`.
- **Detail (VERIFIED this session — NOT a duplicate):** `Halder2021` = "Transformer-Based
  Multi-task Learning for Queuing Time Aware Next POI Recommendation," PAKDD 2021 (DOI
  10.1007/978-3-030-75765-6_41). `Halder2022` = "POI Recommendation with Queuing Time and User
  Interest Awareness," Data Mining and Knowledge Discovery 36:2379-2409, 2022 (DOI
  10.1007/s10618-022-00865-w). Both real, both correctly attributed, both by the same author team.
  Ch.4's description ("multi-task model based on Transformers to recommend the next POI and predict
  the waiting time") maps to the 2022 journal paper's abstract (queuing time + user interest,
  attention-based) — accurate. Ch.3's "TLR-M … Transformer … next POI + queue waiting time" maps
  to the 2021 paper — accurate.
- **Suggested direction:** none required; flagged only so the author is aware two near-identical
  entries coexist by design. If one was intended to be cited in both chapters, decide which.

### F-5 — NIT — chen2020modeling (HMRM) print-year convention
- **Detail:** bib `year = {2022}` (TKDE vol 34(4) print issue) vs OpenAlex 2020 (online-first,
  DOI 10.1109/TKDE.2020.3001025). The R4 HMRM erratum is correctly applied (5 authors incl. Yang
  Liu, vol 34(4):1902-1914 — OpenAlex exact match). The 2022 print year is the correct issue
  year; consistent with how the bib dates other early-access-then-issued IEEE works.
- **Note for author:** BIB_MERGE_REPORT §3.2 already flags that CBIC ERRATA #2's table row still
  shows the pre-correction vol/pages/year and omits Yang Liu — **the ERRATA registry lags the bib**;
  correct the registry, not the bib.

### F-6 — NIT — kendall2018uncertainty author order (OpenAlex quirk, bib is right)
- **Detail:** OpenAlex lists this work's authors Cipolla-Gal-Kendall; the bib and the universal
  "Kendall et al." attribution use Kendall-Gal-Cipolla, the published CVPR-2018 order. **Bib is
  correct**; recorded so a future automated re-check does not re-flag it.

### F-7 — NIT — 10 "record-only" entries lack a DOI/arXiv string in-entry
- **Entries:** chen2018gradnorm, holm1979, kurin2022scalarization, liu2023famo, nash,
  pedregosa2011sklearn, senushkin2023aligned, velickovic2019deep, xin2022domtl, yu2020pcgrad.
- **Detail:** all 10 carry a full venue+year(+pages) record and were confirmed real by
  title+author against OpenAlex/arXiv this session. Several have a resolvable identifier that is
  simply not written into the entry (e.g. senushkin2023aligned → DOI 10.1109/cvpr52729.2023.01923;
  nash → arXiv:2202.01017; chen2018gradnorm → arXiv:1711.02257; xin2022domtl → arXiv:2209.11379;
  velickovic2019deep → arXiv:1809.10341, noted in the comment). Adding the id would harden the
  entry against R1, but none is fabricated or unresolvable — no gate risk.
- **Suggested direction:** optional hardening; add the arXiv id/DOI where the provenance comment
  already names it.

---

## WHAT HOLDS / WHAT READS WELL (do not touch)
- **The bibliography is fundamentally sound.** 99/99 entries are real, correctly attributed,
  non-retracted works. Zero fabrications — the single highest risk in a literature-review
  dissertation is absent. This is the headline.
- **Mechanical closure is perfect:** 99 cited keys = 99 entries, 0 dangling, 0 orphan, 0 dup
  keys; BibTeX `warning$ -- 0`; the built PDF has 0 unresolved markers. The key-consolidation
  work (DGI triple-key, Nash-MTL double-key, Cho triple-key, etc.) landed cleanly.
- **All five R4 inherited errata are FIXED** in the bib (POI-RGNN, HMRM authors, GAT→ICLR,
  silva2025mtlnet venue+status, paiva2026 3rd author) — verified against sources of record.
- **The provenance trail is exemplary** and internally consistent: every entry carries a
  `% PROVENANCE` line; 60 carry a recorded supporting claim; the comment-precedes-entry
  convention holds without a single off-by-one (checked mechanically).
- **Description fidelity is high across 178 sites.** MTL optimizers, graph/representation methods,
  and mobility systems are each described the way their authors describe them. The fundamentals
  chapter's hedging is careful and honest.

## OPEN QUESTIONS (author only)
1. **F-1:** which dataset key should replace `liu2014geographical` at Ch.4:226 —
   `jure2014snap` (matches line 33) or `cho2011gowalla,jure2014snap` (matches line 18)? And does
   it go in the errata appendix as a corrected-in-dissertation item?
2. **F-4:** is citing two different Halder works (2021 in Ch.3, 2022 in Ch.4) intended, or should
   one be used consistently?
3. Errata-registry lag (BIB_MERGE_REPORT §3.2, §3.11): CBIC ERRATA #2 (HMRM row) and the
   `standley2020tasks` venue defect should be corrected in the ERRATA file — out of my
   read-only scope; handed to the author.

## OUT-OF-SCOPE HANDOFFS (one line each)
- **Numbers (persona 06):** the CoUrb chapter's "20.2 to 22.0 pp" (line 33) vs the original's
  "20 to 24 pp" — this is the sanctioned audited-number substitution (NORTH_STAR §4); a number
  auditor should confirm it traces to `slides/judge_feedback.md`. Not a citation issue.
- **Claim honesty (persona 07):** Ch.2:59 "MTLnet … does not outperform the dedicated single-task
  models, a result that holds for that configuration" — correctly time-indexed; flagging for the
  honesty auditor's verb-test pass, not a citation defect.

## COVERAGE STATEMENT
- **Entry level (R1/R2): 100%** (99/99) resolved against a source of record this session
  (OpenAlex get_work ×63 DOI, arXiv get_papers ×24, OpenAlex/arXiv title+author search ×12).
- **Claim-support (R3): 73%** of sites (178/243); 100% of Ch.1+Ch.2 (frame + fundamentals, the
  new-this-pass and highest-AI-share material); every distinct key-set site in Ch.3/4/5.
- **R4: 100%** (all 5 inherited errata verified fixed). **R5: 100%** sweep, clean.
- **Not audited:** ~65 duplicate-key-set repeat sites in Ch.3/4/5 (same key, same claim class,
  already covered by the first occurrence).

---

## `06_number_auditor_report.md`

# 06 · NUMBER AUDITOR REPORT — dissertation v1 (assembled, `src/`)

> Persona 06 (number auditor, G2 fact gate, rules N1–N5). Fresh-eyes, read-only.
> Auditor drafted none of the text under review. This file is the only file written.
> Scope: ALL SIX chapters (`src/chapters/1_introduction.tex` … `6_conclusion.tex`) +
> appendices (`apx_a`, `apx_b`, `apx_c`) + front matter (`src/0_main.tex`).
> Protocol: `reviewers/README.md` Common protocol; AGENT_GUARDRAILS §2 (N1–N5).
> The prior N4 report (`src/_gates/N4_R3_REPORT.md`) is RE-DERIVED here, not trusted.
>
> **STATUS: COMPLETE** — 2026-07-23. Exhaustive extraction + trace done for all ten files.

## VERDICT: **GATE FAIL (conditional)** — 1 BLOCKER (declared, pre-existing), 0 fabrications, 0 MISMATCH

The document's numbers are in excellent shape. Every result table is byte-faithful to its source
of record; every prose numeral, caption, footnote, abstract, and Resumo value traces to a
committed source; there is **no MISMATCH anywhere**, the **never-cite sweep is clean**, and the
**Abstract↔Resumo numeric parity is exact**. The gate fails on a single item — the three
**declared, unfilled dataset placeholders in Ch.3** (`3_cbic.tex:235`), which are orphan numerals
by definition and which the chapter's own ledger marks as blocking handoff. No value was
fabricated; the failure is that the gate cannot record PASS while three numerals have no source.
Two MAJOR items (a convention-naming gap between Ch.5's 64.51 and Ch.6's 64.54; a declared-partial
California value at n=15/20) are correct-but-incomplete, not mismatches. This independently
reproduces the prior N4 verdict (FAIL-conditional, same three-item shape) with fresh extraction.

### Per-chapter verdicts

| Chapter / part | Verdict | Basis |
|---|---|---|
| Ch.1 Introduction | **PASS** | 14 numerals all traced; DOIs/years/ordinal (23rd) correct |
| Ch.2 Fundamentals | **PASS** | 5 numerals (93% ×2, Acc@10 ×3), convention values, coherent |
| Ch.3 CBIC | **FAIL** | tables byte-identical + 84 prose numerals verbatim, BUT 3 orphan placeholders (N-1) |
| Ch.4 CoUrb | **PASS** | tables byte-identical; 99 prose numerals traced (0.02 pp sourced to judge_feedback) |
| Ch.5 MobiWac | **PASS** | tables byte-identical; 139 prose numerals traced; never-cite clean |
| Ch.6 Conclusion | **PASS (with MAJOR N-2/N-3)** | headline + capacity numbers all sourced; convention-naming gap + partial CA value to finalize |
| apx_a Contributions | **PASS** | dates owned by CLAUDE.md §1 |
| apx_b Errata | **PASS** | restatements self-consistent with sanctioned errata records |
| apx_c AI disclosure | **PASS** | CNPq Portaria 2.664/2026 |
| Front matter (0_main) | **PASS** | Resumo↔Abstract numeric parity exact; title still a placeholder (out-of-scope) |
| **Document** | **GATE FAIL (conditional on N-1)** | one declared BLOCKER; resolve N-1 (+ N-3 before banca) → re-run → PASS |

---

## Method

Scripted numeral extraction over the ten `.tex` files in scope: LaTeX comments stripped
(unescaped `%` to EOL), arguments of `\cite/\ref/\label/\url/\includegraphics/\input/\bibliography`
masked, every remaining numeral+unit captured with file:line context. Table cells verified
separately as ordered numeral sequences against the source-of-record files. Front matter
(Resumo/Abstract) extracted the same way. No sampling (gate day = exhaustive).

Sources of truth (per `reviewers/README.md §Sources`):
- Ch.5 (MobiWac): `docs/studies/closing_data/RESULTS_BOARD.md` §1 + §3 file map to JSONs.
- Ch.3 (CBIC): published tables in `articles/CBIC___MTL/`.
- Ch.4 (CoUrb): published tables in `articles/CoUrb_2026/` + `slides/judge_feedback.md`.
- Leak audit: `docs/studies/pre_freeze_gates/A4_RESULTS.md`.
- Venue/status/date: `articles/dissertacao/CLAUDE.md §1`.
- Never-cite: STAN v4-collapse, ReHDM v2 row, VOID fp16/bf16, `docs/PAPER_FINDINGS.md` flags.

---

## Part A — numeral extraction counts — COMPLETE

Exhaustive scripted extraction (digit numerals + a spelled-out-number sweep). Counts below are
digit-numeral totals; the spelled-number sweep (Part C) is additional and caught the CA
"fifteen of twenty" value a digit-only pass misses.

| File | Digit numerals | Classification |
|---|---|---|
| 1_introduction.tex | 14 | all traced (predictability 93; CBIC/CoUrb DOIs+years; 23rd MobiWac; 64-d) |
| 2_fundamentals.tex | 5 | all traced (93% ×2; Acc@10 "10" ×3) — convention/reference values |
| 3_cbic.tex | ~360 | table cells ordered-identical to source (Part B); 84 prose numerals all verbatim; **3 declared placeholders (BLOCKER, pre-existing)** |
| 4_courb.tex | ~366 | table cells ordered-identical; 99 prose numerals traced (0.02 pp + DOI frag explained) |
| 5_mobiwac.tex | 371 | table cells ordered-identical; 139 prose numerals traced (EDAS#/year owned by CLAUDE.md §1) |
| 6_conclusion.tex | 19 | all traced to capacity source + CoUrb ERRATA + board; 2 declared roundings; 1 declared-partial (CA n=15) |
| apx_a_contributions.tex | 4 | dates (BRACIS rejection, owned by CLAUDE.md §1) |
| apx_b_errata.tex | 60 | errata/bib restatements; sampled DOIs/pages match sanctioned records (Part C) |
| apx_c_ai_disclosure.tex | 3 | CNPq Portaria 2.664/2026 |
| 0_main.tex (front matter) | 23 | Resumo/Abstract data numerals = {5.3, 9.4} + n=20 convention; parity holds (Part D) |
| **Total** | **~1,225** | **0 MISMATCH; 3 ORPHAN-by-design placeholders (declared BLOCKER)** |

Digit-numeral counts track the prior N4 report within extraction-boundary noise (Ch.3/4 differ
by 1–5 tokens from how math-mode subscripts and DOI fragments are split; every such token was
individually resolved, none is a data cell). No numeral is left unaccounted for.

## Part B — table verification (cell-by-cell, ordered) — COMPLETE

Nine result tables traced to their sources of record. Method: extract ordered numeral
sequence from each chapter table environment and from its source file, strip layout/macro
tokens (`\multicolumn`, `\cmidrule`, `\multirow`, `\providecommand{\sd}`), diff the two
sequences, then independently re-verify the emphasis sets (`\textbf` = best; `\ul`/`\underline`
= second-best) as numeric-payload multisets.

| Chapter table | Source of record | Data cells | Emphasis | Verdict |
|---|---|---|---|---|
| tab:cbic:category | `CBIC___MTL/tables/category_result.tex` | ordered-identical | bold 21/21 | ✅ |
| tab:cbic:next | `.../next_result.tex` | ordered-identical | bold 21/21; **2nd-best 15/15** (`\ul`→`\underline` macro swap, same payloads) | ✅ |
| tab:cbic:convergence | `.../converge_result.tex` | ordered-identical | — | ✅ |
| tab:courb:dataset | `CoUrb_2026/src_en/resultados/tabela_dataset.tex` | ordered-identical | — | ✅ |
| tab:courb:category | `.../tabela_comparativa_f1_category.tex` | ordered-identical | bold 22/22 | ✅ |
| tab:courb:next | `.../tabela_comparativa_f1_next.tex` | ordered-identical | bold 22/22 | ✅ |
| tab:mobiwac:datasets | `[mobiwac]/src/tables/tbl1_datasets.tex` | ordered-identical | — | ✅ |
| tab:mobiwac:representation | `.../tbl2_substrate.tex` | ordered-identical | — | ✅ |
| tab:mobiwac:results | `.../tbl3_results.tex` | ordered-identical | bold 12/12 | ✅ |

The only sequence differences were traced and are NOT data:
- CBIC three tables: a stray `5` = the chapter rewrote the source's terse captions into fuller
  ones stating the fold convention ("over the 5 folds" / "5-fold cross-validation"). The
  numeric data cells are untouched. (Caption authorship, N5-relevant — see Part D.)
- mobiwac representation/results: source's `\providecommand{\sd}[1]{...#1}` macro-definition
  tokens (`1,1`), which the chapter defines in the preamble instead; and the chapter's
  `\cmidrule(lr){3-6}\cmidrule(lr){7-11}` vs the source's `\multicolumn{11}{...2\tabcolsep}`
  header-layout tokens. Layout only.

**No data cell differs from its source of record in any of the nine tables.** This
independently reproduces the prior N4 report's table verdict.

## Part C — prose numeral trace — COMPLETE

Method: extract prose numerals (outside table environments, true line numbers, identifier args
masked) per chapter; verify each appears verbatim in the chapter's source of record. Digit
regex supplemented by a spelled-out-number sweep (one…twenty, hundred/thousand/million) filtered
to experimental-unit nouns — this caught the "fifteen of twenty repetitions" CA value that a
digit-only sweep misses.

**Paper chapters (re-typeset published text) — all prose numerals trace:**
- **Ch.3 (CBIC): 84 prose numerals, 84 found verbatim** in `CBIC___MTL/sections/*.tex` +
  tables + `ERRATA.md`. 0 unexplained.
- **Ch.4 (CoUrb): 99 prose numerals, 97 found verbatim** in `CoUrb_2026/src_en/` sources. The
  two not found are both benign: (a) `2026.22960` = the DOI fragment `10.5753/courb.2026.22960`,
  matching CLAUDE.md §1 (owner of DOI facts); (b) `0.02` percentage points (FL-Outdoors technical
  tie) — quoted from `slides/judge_feedback.md §2` ("baseline 21,61 vs Sphere 21,59 — baseline
  ainda vence por 0,02 pp") and declared in the Ch.4 ledger A1 + ERRATA #1; the two cells 21.61
  and 21.59 are both present in the source table. Quoted, not computed (N2 OK).
- **Ch.5 (MobiWac): 139 prose numerals, 136 found verbatim** in `[mobiwac]/src/sections|tables|figs`.
  The three not found: `2026` and `1571313639` (EDAS #, owned by CLAUDE.md §1, confirmed);
  `003` = a regex-boundary artifact of `$\pm0.003$`, which appears verbatim in `02_related.tex:93`.

**Frame chapters + front matter (author-drafted, highest N-audit risk) — headline numbers traced
to the MobiWac board:**
- **Ch.6 capacity paragraph (L74–79)** traces cell-for-cell to
  `storyline/audit/capacity_baseline_experiment.md §5`:
  4.2M = 4,197,621 (§5.1); 0.6M = 644,359 (§5.1, declared rounding); 56.16 ±1.88 = best arm
  n=20 (§5.3); 56.82 = dedicated ceiling at its own width, n=20 (§5.3); 64.54 = joint v17 n=20
  (§5.2/§5.3); "fifteen of twenty repetitions" CA partial = "seeds {0,1,7} = n=15 of 20" (§5.4),
  "same direction" verbatim. **NOTE**: `56.16` exists in NO file under `docs/`; its only source of
  truth is this `storyline/audit/` file (job `d38a1382`, `al_capmatch_summary.json`). See finding
  N-2 on the convention distinction between Ch.6's 64.54 and Ch.5 Table 3's 64.51.
- **Ch.6 other numerals**: +0.001 cosine (L88, four seeds, three of six datasets) traces to
  `02_related.tex`; 2009/2010 Gowalla vintage traces to DATASETS/CoUrb conclusion; 20.2–22.0
  (L39) = CoUrb ERRATA #2 audited range; 5.3–9.4 (L51) = the headline (see Part D / N5).
  limitation~1…6 are `enumerate` counters, not data.
- **Ch.1**: 93 (song2010limits), CBIC/CoUrb DOIs + years, 23rd ACM MobiWac, 64-d embedding —
  all trace (93% is the DRAFT_LEDGER-verified predictability bound; 64-d is the CBIC/CoUrb input).
- **Ch.2**: 93%, Acc@10 ("10"), seven categories, six datasets / five states / two check-in
  datasets / one city — all convention constants, coherent with Ch.5 (see Part D).
- **apx_a**: BRACIS rejection "June 8, 2026" — owned by CLAUDE.md §1 (BRACIS containment C4).
- **apx_c**: CNPq Portaria 2.664/2026 — AGENT_GUARDRAILS §6.

## Part D — cross-checks (abstract ↔ body ↔ Resumo; captions ↔ tables; convention N5) — COMPLETE

**D.1 Abstract ↔ Resumo ↔ body numeric parity.** The Resumo (PT) and Abstract (EN) in
`0_main.tex` carry exactly one pair of data numerals: the headline range **5.3 to 9.4**
(PT "5,3 a 9,4" / EN "5.3 to 9.4" — correct decimal-separator localization), plus the
convention triple "twenty repetitions (four random initializations, five folds)" =
"vinte repetições (quatro inicializações aleatórias, cinco partições)". Both match Ch.6 L49–53
and NORTH_STAR §2. The claim structure maps 1:1: "outperforms at four of six … matches
(TOST ±2 pp / margem de dois pontos) at the other two" in both. **Parity holds.**
(The stray `5.8` in both blocks is the document pointer "NORTH_STAR §5.8" inside the
`[TITLE --- open decision]` placeholder — not a data numeral. See out-of-scope: title unresolved.)

**D.2 Headline range recomputed from source.** The deployable (joint-best) category deltas in
`joint_best/JOINT_BEST_RESULTS.md` are AL +7.69, AZ +9.35, FL +5.33, TX +7.45, CA +6.45,
Istanbul +8.58. min = 5.33 → 5.3; max = 9.35 → 9.4. The Ch.6/Abstract headline **"5.3 to 9.4"**
is the min/max of this set rounded, and Ch.5 body states the same range unrounded (+5.33 to
+9.35, L533). Internally consistent. The CoUrb headline **"20.2 to 22.0"** (Ch.6 L39) is the
min/max of the per-state best-of-two-encoder means FL +20.24 / CA +20.91 / TX +21.98
(`slides/judge_feedback.md §11`), with 21.98 → 22.0 the ERRATA #2 declared rounding. Correct.

**D.3 Captions ↔ table contents.** All nine result-table captions verified (Part B). The CBIC
captions were rewritten by the chapter to state the fold convention ("over the 5 folds"), which
introduces the caption `5` token; data cells untouched. Ch.5 Table 3 caption correctly names its
emphasis convention (bold = statistically supported improvement over dedicated; ↑ = supported
region improvement; ≈ = TOST ±2 pp non-inferior match). Ch.5 Table 2 caption correctly carries
the matched-recipe **seed-0 × 5-fold** convention and does not blur with Table 3's n=20.

**D.4 Convention constants — cross-chapter consistency (N5).** Verified coherent everywhere:
- "twenty repetitions = four seeds × five folds" (n=20): stated together in Ch.1, Ch.6, front
  matter; Ch.5 uses the operational "four seeds / five folds". Ch.3 (CBIC) correctly uses its
  own "5-fold" protocol (predates the n=20 convention; time-indexed).
- seven categories / six datasets / five US states + Istanbul / two check-in dataset sources:
  coherent in every chapter that names them (no count drift).
- "four of six" region result: identical wording in Ch.1, Ch.2, Ch.5 (×2), Ch.6, front matter.
- TOST two-point margin at **Alabama and Arizona**: consistent; AZ is never upgraded from a
  match to a beat (Ch.5 results comments enforce it; Ch.6 restates it as a match).

**D.5 The one genuine convention subtlety (see finding N-2).** The AL joint-category cell is
reported as **64.51** in Ch.5 Table 3 (deployable / joint-best checkpoint) and **64.54** in the
Ch.6 capacity paragraph (diagnostic-best, n=20). Both are individually correct and individually
sourced (`JOINT_BEST_RESULTS.md` L32: `AL 56.82 | 64.54 diag | 64.51 deploy | −0.04`). Ch.5 **does**
name its convention in rendered prose (`5_mobiwac.tex:515–518`); the gap is at the Ch.6 site, which
switches to the diagnostic-best value without signalling it, leaving a reader with an unexplained
0.03 discrepancy against Table 5.3. This is the "joint-best vs diagnostic-best distinction must
never blur" risk (N5) — not a MISMATCH, but a convention-naming gap at Ch.6. Reported as MAJOR N-2.

## Part E — never-cite sweep — COMPLETE (CLEAN)

Swept every chapter's prose (comments stripped) for each absolute never-cite value
(README §Sources + Ch.5 results comment L461–463):

| Never-cite value | Meaning | Hits in prose |
|---|---|---|
| 34.46 / 38.96 | STAN v4-collapse (AL/AZ) | **0** |
| 62.37 | HMT-GRN AL outlier | **0** |
| 66.06 / 65.68 | ReHDM v2 row (a, c) | **0** |
| 54.65 | ReHDM v2 row (b) | 1 — **FALSE POSITIVE, disambiguated below** |
| fp16 / bf16 VOID cells | — | **0** (none of those values present) |

**The single 54.65 hit is not a violation.** It occurs at `5_mobiwac.tex:402` as the **Istanbul
next-category macro-F1 at the check-in level** in Table 2 (`tab:mobiwac:representation`), traced
byte-identical to `tbl2_substrate.tex:24` and its provenance comment (Check2HGI-SC 54.65 ±0.56).
This is a different physical quantity that coincidentally shares the numeral with the ReHDM v2
region-Acc@10 value. Confirmed the chapter's actual ReHDM row (Table 3) uses the sanctioned **v4**
values (Ist 69.33 / AL 65.38 / AZ 53.00, per `rehdm.md` and Ch.5 comment L455), and the v2 triple
66.06 / 54.65 / 65.68 as a *set* appears nowhere. **Never-cite sweep passes.**

## Findings

### Top 3 (most valuable)
1. **N-1 [BLOCKER]** — three orphan dataset numerals in Ch.3 (declared placeholders, gate cannot pass).
2. **N-2 [MAJOR]** — AL joint-category cell differs between Ch.5 Table 3 (64.51) and Ch.6 (64.54) under two unnamed conventions (joint-best vs diagnostic-best).
3. **N-3 [MAJOR]** — Ch.6 California capacity value is a declared partial (n=15/20); must be finalized to n=20 before the final gate.

---

**[N-1] BLOCKER (declared, pre-existing) — Ch.3 dataset placeholders are orphan numerals.**
`3_cbic.tex:235`: "This subset comprises a total of `[$N_{\text{users}}$; VERIFY: recompute per
ERRATA.md]` users, `[$N_{\text{poi}}$; ...]` unique Points-of-Interest (POIs), and
`[$N_{\text{checkins}}$; ...]` check-ins." Three numerals have no source value — by the persona's
definition an orphan numeral is a BLOCKER, and the chapter's own ledger agrees: `3_cbic_ADAPTATION_LEDGER.md`
B1 marks it "**AUTHOR ACTION REQUIRED before handoff**" and D.1 marks it "**[VERIFY — blocks handoff]**".
The values were *not* invented (correct fail-closed behaviour); the sanctioned path (a repo-committed
recompute over the CBIC-era Florida pipeline — Gowalla FL, users with <5 visits dropped —
author-approved) has not been run. *Direction:* run the sanctioned script and author-approve, or
ship the advisor draft with visible placeholders only if the author explicitly accepts that. The
gate cannot record PASS while three orphan numerals stand. Reproduces prior N4-1.

**[N-2] MAJOR (BLOCKER-adjacent) — Ch.6 quotes the AL joint cell under a different, unnamed
selection convention than Ch.5.** The Alabama joint next-category value is **64.51** in Ch.5
Table 3 (`tab:mobiwac:results`, `5_mobiwac.tex:479`) and **64.54** in the Ch.6 capacity paragraph
(`6_conclusion.tex:78`, "64.54 for the joint model"). Both trace correctly to
`joint_best/JOINT_BEST_RESULTS.md` L32 (`AL | 56.82 | 64.54 diag | 64.51 deploy | −0.04`), so this
is **not a MISMATCH** — they are two legitimate summaries of the same model under two selection
rules the source keeps as distinct columns: *deployable* (one saved artifact per fold, epoch
chosen by the joint validation score) = 64.51, and *diagnostic-best* (each task read at its own
best epoch) = 64.54. **Ch.5 names its convention in rendered prose** (`5_mobiwac.tex:515–518`:
"every reported model is one saved artifact per fold, read at its validation-selected epoch … the
joint model at the epoch selected by its joint validation score"). The defect is at the **Ch.6**
site only: the capacity paragraph switches to the diagnostic-best 64.54 (the reference its own
source `capacity_baseline_experiment.md §5.2–5.3` uses, and internally consistent there with
56.16 / 56.82 on the same basis) **without signalling the switch**, so a reader who remembers
Table 5.3's AL joint = 64.51 meets "64.54 for the joint model" with an unexplained 0.03 gap. It is
BLOCKER-adjacent under the contract's "blurred convention" / "same fact quoted twice" cross-checks,
but ranked MAJOR because (i) both values are source-true, (ii) the capacity comparison is
internally convention-consistent, and (iii) the paragraph's conclusion (the +8 pp gap the wider
dedicated model fails to close) holds identically at 64.51 or 64.54. *Direction:* at
`6_conclusion.tex:78` name the convention (e.g. "64.54 for the joint model read at each task's best
epoch, the reference used by the capacity experiment; Table 5.3's deployable-checkpoint value is
64.51"), or switch the comparison to 64.51 for cross-table consistency. Which convention Ch.6
should present is also a claim decision (persona 07).

**[N-3] MAJOR (declared-partial) — Ch.6 California capacity value is n=15/20, not final.**
`6_conclusion.tex:78–80`: "A partial California run, fifteen of twenty repetitions at the time of
writing, shows the same direction." Matches the source (`capacity_baseline_experiment.md §5.4`:
job `4cff4b00`, seeds {0,1,7} = n=15/20, 68.35 ±0.53, "same direction"), and the prose honestly
discloses partiality and states no point value — so it is not an orphan or mismatch. But §5.4's
own contract says "the final value is the best arm's n=20 mean once seed 100 and the second arm
land." *Direction:* replace with the final n=20 California verdict when job `4cff4b00` completes,
then re-run this numeral check. Reproduces prior N4-2.

**[N-4] NOTE — declared-rounding inventory (all sanctioned, none agent-computed).**
- 5.33 → 5.3 and 9.35 → 9.4 (headline; Ch.6:51, Abstract `0_main.tex`, Resumo; source
  `JOINT_BEST_RESULTS.md`, min/max of the deployable deltas; NORTH_STAR §2 records "5.3…9.4").
- 21.98 → 22.0 (Ch.6:39; CoUrb ERRATA #2).
- 644,359 → 0.6M and 4,197,621 → 4.2M (Ch.6:74–75; `capacity_baseline_experiment.md §5.1` gives
  the full-precision values; the chapter quotes the ~M rounding). Each rounding exists in — or is
  the declared min/max over — its source; the chapters quote, they do not compute.

**[N-5] NOTE — CBIC captions rewritten (not reproduced verbatim).** The three CBIC tables' captions
were rewritten by the chapter to add the fold convention ("over the 5 folds" / "5-fold
cross-validation"), which is why a `5` token appears in the chapter tables that is absent from the
source captions. The numeric *data cells* are byte-identical. This is a legitimate N5 improvement
(the published captions did not state the convention), not a data change — recorded for completeness.

**[N-6] NOTE — 34.97 s and 2.3× in Ch.3 are sanctioned reconciliations.** `3_cbic.tex:349`:
"80.88 s … about 2.3 times the cumulative 34.97 s". The published paper said "almost four times";
CBIC `ERRATA.md` line 32 sanctions the correction ("80.88 s / 34.97 s = 2.3x — reconcile to the
table"). 34.97 = 16.26 + 18.71 (the two single-task times from the convergence table); the
reconciliation lives in the committed errata, not in agent arithmetic. N2-compliant.

## What holds (do not touch)

- **Every result table is byte-faithful to its source of record.** All nine tables (CBIC ×3,
  CoUrb ×3, MobiWac ×3) have data cells ordered-identical and emphasis sets (bold = best,
  `\ul`/`\underline` = second-best) identical to their published/board sources. This includes the
  CBIC next-table second-best set (15/15 cells, verified through the `\ul`→`\underline` macro swap)
  and the MobiWac Table 3 bold set (12/12).
- **Zero MISMATCH anywhere.** Not one numeral in prose, tables, captions, footnotes, abstract,
  or Resumo disagrees with its source. The only sequence differences found were layout/macro
  tokens (`\providecommand{\sd}`, `\cmidrule`, `\multicolumn`) and a rewritten-caption convention
  token — all individually traced.
- **The headline result is sound and consistently reported.** "5.3 to 9.4" (category, all six
  datasets) and "four of six, TOST ±2 pp at the other two" (region) are the correct min/max /
  count over the deployable joint-best deltas, stated identically across Ch.1, Ch.5 body, Ch.6,
  Abstract, Resumo, and NORTH_STAR §2. AZ is never upgraded from a match to a beat.
- **Abstract ↔ Resumo numeric parity is exact** (claim-parity includes numbers): same range, same
  n=20 convention, same hedges, correct decimal-separator localization (5,3 / 5.3).
- **Never-cite sweep is clean.** No STAN v4-collapse (34.46/38.96), no HMT-GRN AL 62.37, no
  ReHDM v2 row (66.06/54.65/65.68 as a set), no fp16/bf16 VOID cells. The lone 54.65 hit is a
  distinct, correctly-sourced quantity (Istanbul category F1).
- **Convention constants are internally coherent** across all six chapters + front matter
  (seven categories, six datasets = five US states + Istanbul, two check-in dataset sources,
  n=20 = four seeds × five folds). Ch.3's own 5-fold convention is correctly time-indexed and
  not conflated with the later n=20.
- **The capacity-experiment numbers trace cell-for-cell** to `capacity_baseline_experiment.md §5`
  (4.2M, 0.6M, 56.16, 56.82, 64.54, n=15 CA partial) — every value present and exact.
- **Declared roundings and reconciliations are all sanctioned** in committed sources
  (NORTH_STAR §2, CBIC/CoUrb ERRATA), never produced by agent arithmetic in prose (N2 holds).

## Could-not-verify (fail-closed)

- **The three Ch.3 dataset statistics (N-1)** cannot be verified because no value exists — they
  are unfilled placeholders awaiting the sanctioned recompute. This is *reported as a blocker*,
  not smoothed over. Missing input: the author-approved output of the CBIC-era Florida recompute
  script.
- **The final California capacity value (N-3)** cannot be verified as final because the run
  (`4cff4b00`) had reached only n=15/20 at the time of writing. The current text correctly
  discloses this and states no point value; the *final* n=20 number is what is missing.
- **apx_b DOI/venue/page restatements**: verified as *self-consistent with the sanctioned errata
  records* (CBIC/CoUrb `ERRATA.md`, `BIB_MERGE_REPORT.md`) — e.g. TKDE 34(4):1902–1914 2022,
  CVPR.2016.**433**, TKDE.2021.3070203, pp. 323–336, arXiv:1905.07553. Re-resolving those DOIs
  against Crossref/OpenAlex is persona 05's scope (the prior R3 pass did so and found no defect);
  as number auditor I confirm only that the appendix restates them without internal contradiction.

## Out-of-scope handoffs (one line each)
- **Dissertation title is still `[TITLE --- open decision NORTH_STAR §5.8]`** in the folha de
  rosto, Resumo, and Abstract (`0_main.tex`) — a front-matter completeness item for the author /
  concordance, not a numeral defect. (This is the source of the stray "5.8" pointer.)
- Approval-sheet placeholder in the front matter (`0_main.tex:161`) — expected pre-defense; format/persona 13.
- The 64.51/64.54 convention wording (N-2) also touches claim-honesty (persona 07): the choice of
  which convention Ch.6 presents is a claim decision, not only a number-naming one.

## Open questions for the author
1. **N-1**: run the sanctioned Florida recompute now and fill the three Ch.3 statistics, or ship
   the advisor draft with visible placeholders (the gate stays FAIL until they are filled)?
2. **N-2**: name the convention at `6_conclusion.tex:78` (64.54 = diagnostic-best) alongside a
   pointer to Table 5.3's deployable 64.51, or switch Ch.6 to 64.51 for cross-table consistency?
3. **N-3**: hold the final gate for the n=20 California capacity value, or keep the honestly-hedged
   partial for the advisor draft and finalize before the banca build?

---

## `07_claim_honesty_auditor_report.md`

# 07 · Claim & Honesty Auditor — Report on dissertation v1

> Persona 07 (claim-registry gate G2, rules C1–C4 + WRITING_LAW §3 honesty law).
> Scope: all six chapters (`src/chapters/1_introduction.tex` … `6_conclusion.tex`),
> appendices (`apx_a`/`apx_b`/`apx_c`), and front matter (`src/0_main.tex`).
> Read-only. Findings quote the licensed form; they never rewrite.
> Status: IN PROGRESS (written incrementally; a restart must not lose work).

---

## Working reference — the licenses (quoted from source, do not re-derive)

### MobiWac / Ch.5 CAN-say (PAPER_PLAN §3 + CLAUDE §2/§3)
- **Category beats ceiling everywhere:** Δ = AL +7.69 / AZ +9.35 / FL +5.33 / CA +6.45 / TX +7.45 / Ist +8.58 (vs n=20 best-vs-best ceilings; per-cell Holm m=6 all reject, worst adj p=1.0e-06). Joint cat cells: Ist 63.32 / AL 64.51 / AZ 65.79 / FL 79.84 / TX 77.24 / CA 77.05.
- **Region:** outperforms (paired Wilcoxon superiority, 90% CI>0) at **Ist +0.19, FL +0.71, TX +2.11, CA +2.20**; **matches** (TOST non-inferior, δ=2pp) at **AL −0.41, AZ 0.00**. Joint reg cells: Ist 75.35 / AL 69.70 / AZ 59.46 / FL 77.41 / TX 67.06 / CA 65.69. **NEVER upgrade AZ (0.00, CI straddles zero).**
- **Check2HGI vs HGI category margin:** +29.31 / +27.63 / +39.62 / +37.95 / +37.47 (AL/AZ/FL/CA/TX); two bands ~+28–29 (small) and ~+37–40 (large); Istanbul dk_ovl +28.09. HGI cat ≈ 0.46–0.52× Check2HGI cat. On next-region the two representations are within ~1.6–3.1 pts (HGI slightly ahead): representation benefit is **category-only**.
- **Markov region floor (text only, §6.2):** joint exceeds stride-1 Markov-1 floor (Acc@10 51–72 across six) by 4.9–10.3 pts.
- **n = 20** = 4 seeds × 5 folds; Holm across six; user-disjoint CV; A4 leak audit null (region ≤0.33 pp, category ≤0.29 pp at AL/AZ/FL).
- Scaling: region gain rises with region count **across the five U.S. states**; Istanbul (fewest regions) also positive.
- Cascade (CSLSL pattern) = **tie at equal cost** (Δ ≤ 0.02), framed as defense not win; it is a coupling-topology variant of *our own* model, NEVER a CSLSL re-implementation.
- Verdict verbs: **"outperforms"** (paired Wilcoxon) / **"matches"** (TOST); never "beats"/"wins"/"ties"/"Pareto".

### MobiWac must-NOT-say
"beats region everywhere"/"Pareto-dominates"; "ties" on region; "cost grows with region count"/cardinality-cost/TX −2.4; headline a two-model composite / per-task routing / two-substrate; old region numbers 7–17 or pre-2026-05; "trivial"/"padding" for dropped overlap windows; "we beat STAN-on-our-representation" (stl_hgi, sits above us at AL 70.35 vs 69.81); "we beat the cascade"; "we ran/benchmarked CSLSL".

### CBIC / Ch.3 (published, time-indexed)
"MTL does not help" = conclusion **of the time, for that configuration**. Nash-MTL "consistently better" predates the solver-bug discovery (NashMTL collapse to [1,1]) — do NOT amplify in the frame.

### CoUrb / Ch.4 (published, time-indexed)
Audited numbers: **15/21 strict wins + 1 technical tie** (NOT "16/21 (76%)"); per-state category means **+20.2…+22.0 pp** (NOT "+20–24 pp"). Split is **sample-stratified, not user-disjoint** (verified firsthand — plain StratifiedKFold, userid dropped) — say so plainly. Contribution note for Vitor mandatory. Required floor sentence (approved): "this chapter isolates the representation effect with MTLNet as its only baseline; it does not revisit the MTL-versus-single-task question, which Chapter 5 reopens."

### BRACIS (C4 containment)
Appears ONLY as "an earlier unpublished iteration"; its region-cost claim (MTL pays 7–17 pp on region) appears ONLY as corrected history (fp16 artifact + older protocol), never live.

### Story spine (C2 — frame arc claims must match NORTH_STAR §6)
Signed-off additions to the Intro arc paragraph (AVAL rounds 1–2, 2026-07-22): task-pair evolution named plainly; three-legged task-choice defense (leg 2 comparative form stays [VERIFY]); "unnatural" not "incoherent"; N2 caution form only (never "CBIC's future work called for better representations"); mechanism sentence as hypothesis. Ch.6: task-pair confound concession; N3 negative-transfer-reversal beats with cosine +0.001 full scope (four seeds, three of six datasets, directional conflict only, this pair not a general rule); "sharing stopped hurting" never "tasks teach each other"; never credit parameter count.

---

## FINDINGS (incremental)

### Front matter (0_main.tex) — Resumo/Abstract pair
- Abstract (EN) and Resumo (PT) are a claim-parity pair. Verbs bound: "outperforms … at all six … by 5.3 to 9.4 macro-F1 points" (category); region "outperforms at four of six … and statistically matches, with non-inferiority within a two-point margin (TOST), at the other two." PT mirror: "supera … por 5,3 a 9,4 pontos"; region "supera em quatro dos seis … e equipara-se estatisticamente … (TOST), nos outros dois." HOLDS. AZ not upgraded (folded into "the other two", not named as a win). Headline 5.3–9.4 matches CAN-say (+5.33…+9.35). Null result stated as "a null result reported as a finding" / "um resultado nulo relatado como um achado" — honest, not rushed. Both carry [NEEDS SIGN-OFF] comments (author-owned).

### Ch.1 Introduction — arc narrative (C2 spine conformance)
HOLDS against NORTH_STAR §6 signed-off spine. Verified present:
- Task-pair evolution named plainly (§1.1 "A fourth task also appears…"; §1.2 "The task pair therefore evolved…") — not narrated as one fixed experiment. ✓ (spine addition a)
- Three-legged task-choice defense (§1.1): "chosen for what a mobility-aware service can act on, and both are established end targets in the literature on the way to the harder next-place problem." Leg 2 in fallback form (established end targets + feeds next-place), NOT the [VERIFY] comparative "most-cited" form. ✓ (spine addition b)
- "less natural fit" (§1.2), NOT "incoherent"/"unnatural-as-incoherent". ✓ (spine addition c) — note spine said "unnatural"; chapter uses "less natural fit", same polarity, acceptable.
- N2 caution form (§1.2): "tested the representation explanation first, as the cheapest controlled test among the three" — NOT "CBIC's future work called for better representations", no foresight framing. ✓ (spine addition d)
- Mechanism sentence as hypothesis (§1.2): "That observation is the hypothesis the final study tests." ✓ (spine addition e)
- Region verbs (§1.2, §1.6 Practical): "four of six, with statistical non-inferiority within a two-point margin (TOST) at the other two" / "outperforming or remaining non-inferior". ✓ AZ not upgraded.
- Compute-cost honesty (F3 guard): "cost more to train" stated for CBIC (§1.2); operational wish framed as "single model to maintain … single forward pass", never lower compute. ✓

### Ch.2 Fundamentals — HOLDS on claims
- MTLnet null time-indexed: "does not outperform the dedicated single-task models, a result that holds for that configuration" (§2.3). ✓ Nash-MTL NOT amplified (named only in the balancer list, no benefit claim). ✓
- Verb law: §2.3 ledger notes all "beat" removed → "outperform". Region-as-end-target scoped to the multi-task co-equal setting (single-task region prediction acknowledged via zhu2022drrgnn). ✓
- §2.5 result wording bound to tests: "by paired superiority tests, outperforms … on the next category everywhere … and on the next region at four of six datasets, and matches … within a two-point margin, by non-inferiority testing, at the other two." ✓ AZ/AL not upgraded; forward-points to Ch.5.
- song2010limits 93% scope-corrected (§2.1, §2.4): explicitly "not … a ceiling on seven-class category macro-F1 or on region ranking"; dedicated single-task model is the operative ceiling. ✓ (honesty: number carries its reference-point scope)
- Lineage table: Check2HGI + joint model status "submitted, under review" in caption. ✓
- OPEN QUESTION Q1 (see below): "roughly a third" Food figure provenance.

### Ch.6 Conclusion — HOLDS on claims; two items to confirm
- §6.1 CoUrb: "+20.2 to 22.0 percentage points across the three states tested" = audited CoUrb numbers (NORTH_STAR §4), NOT the stale "+20–24 pp". ✓
- §6.1/§6.2 MobiWac verbs bound to tests, four-of-six named (Ist/FL/CA/TX), AL/AZ matched via TOST, never upgraded. ✓
- §6.2 capacity-matched baseline (POST-SUBMISSION frame analysis, licensed by D1 contract + NORTH_STAR §6): numbers trace to storyline/audit/capacity_baseline_experiment.md §5.3 — best arm 56.16 (±1.88 not quoted in prose), dedicated ceiling 56.82, joint 64.54, AL 4.2M vs 0.6M published width, partial CA n=15/20 "same direction". VERIFIED against source. Reading (i) reported honestly per contract §3.2 (unfavorable outcome would have been reportable; favorable one is not overstated). ✓
- §6.2 freeze control: "at the three datasets where the control was run (Alabama, Arizona, Florida)" = NORTH_STAR §6 N3 scope. ✓ Cited as a Ch.5 finding (licensed).
- §6.2 mechanism: cosine +0.001 full scope travels verbatim ("over four seeds on three of the six datasets … a finding for this pair of tasks rather than a general rule"). "sharing stopped hurting" present; "does not come from the region task teaching the category task" — never "tasks teach each other"; parameter count never credited (disclosed as cost). ✓ (NORTH_STAR §6 N3 beats)
- §6.3 limitation 6 (task-pair confound) + §6.4 future-work fixed-pair ablation present = signed-off 2026-07-22 additions. ✓

### Ch.3 CBIC — HOLDS (reproduced published text, correctly time-indexed)
- Preface time-indexes BOTH load-bearing conclusions: the null ("conclusions of the time, for the configuration studied here: with a place-level embedding and hard parameter sharing, multi-task learning did not consistently improve on the dedicated single-task models") AND the Nash-MTL preference ("likewise a conclusion of the time, weakened by a later finding about the optimizer implementation, and the following chapters do not rely on it"). ✓ (NORTH_STAR §4 Ch.3 claim-discipline)
- Null written with care, not rushed: three candidate explanations laid out in §conclusion. ✓ (checklist 9)
- The reproduced "Nash-MTL consistently yielded a better overall performance" (§sec:cbic:nash) is preserved verbatim by design (Appendix B preservation note) with the preface carrying the of-the-time caution — NOT amplified in frame prose. ✓
- CBIC-era task naming ("Next-POI Prediction" = the label is the next POI's category) is the chapter's own published usage; the frame (Ch.1 §1.1, Ch.2 §2.1 mapping) canonicalizes it. ✓
- Dataset placeholders render as visible "[VERIFY: recompute per ERRATA.md]" markers (not fabricated); Appendix B row 5 marks this "Pending, Not invented." Correct fail-closed handling — see MINOR-1.

### Ch.4 CoUrb — HOLDS (audited numbers, time-indexed, ownership disclosed)
- Audited numbers used throughout, NOT the stale published ones: "20.2 to 22.0 percentage points" (not "20–24"); "15 of the 21 ... with one additional technical tie" (not "16/21 (76%)"). Present in §intro, §results, §conclusion, and Appendix B. ✓ (NORTH_STAR §4 Ch.4)
- Ownership honesty (checklist 10): preface states "Tarik S. Paiva is the first author ... the author of this dissertation is the second author, presented the paper at the workshop, and is the first author of the baseline model MTLNet." Also in Ch.1 §1.5. ✓
- Protocol honesty: preface + §experimental-setup both state the split "is stratified by sample, not by user, so the check-ins of one user may appear in both training and validation; Chapter 5 adopts a stricter user-disjoint protocol." Weaker protocol disclosed plainly, strengthens the arc. ✓ (VERIFIED FIRSTHAND per NORTH_STAR §4, UW-3 closed)
- Required floor sentence present verbatim in preface: "This chapter isolates the representation effect with MTLNet as its only baseline; it does not revisit the MTL-versus-single-task question, which Chapter 5 reopens." ✓ (NORTH_STAR §6 Ch.4 approved Item 6)
- Verdict verb: "outperforms the baseline in most scenarios" (Appendix B records the "wins"→"outperforms" fix). ✓

### Ch.5 MobiWac — HOLDS (whitelist-exact; the highest-risk chapter, clean)
- **Category:** "outperforms ... on every dataset ... by +5.33 to +9.35 macro-F1 (smallest at Florida, largest at Arizona, and +8.58 at Istanbul)" = CAN-say exactly. Table III joint cat cells 63.32/64.51/65.79/79.84/77.24/77.05 match the whitelist memory-aid. ✓
- **Region verbs bound to tests:** Table III uses ↑ (superiority) at Ist/FL/TX/CA, ≈ (TOST non-inferior) at AL/AZ; the two matched cells are NOT bolded. Prose: "outperforms ... at Florida, Texas, California, and Istanbul, and stays a non-inferior match (TOST, ±2 pp) at Alabama and Arizona." ✓
- **AZ never upgraded** (the cardinal rule): "At Arizona, the interval is centered on zero, so we report a match, not a gain" (§results-part2). AL handled honestly: "the whole interval lies below zero, a small but statistically significant deficit, still well within the two-point margin." ✓
- **Scaling scoped to the five U.S. states:** "Across the five U.S. states, the region gain rises with region count"; "region count and corpus size co-vary here, so we read the trend across the points rather than as a precise law." ✓ (no over-claimed law)
- **Cascade = defense, not win:** "We read this as a defense of the parallel design, not a claim that we outperform the cascade"; "we test the cascade inside our own model rather than re-implementing those systems." Two qualifications present (parallel-tuned recipe; form fixed in advance). ✓ (decisions ledger cascade framing)
- **Never-cite (C3) absent:** STAN faithful (AL 60.72/AZ 49.86, not the 34.46/38.96 v4-collapse); ReHDM v4 row (69.33/65.38/53.00/64.49/48.81/50.26, not the v2 66.06/54.65/65.68); no HMT-GRN 62.37 outlier (Table III AL = 57.05); no fp16/bf16 VOID cells. ✓
- **stl_hgi / "beat STAN-on-our-representation" absent.** ✓
- **Compute-cost honesty (F3):** "the joint model has about 4.2 million parameters at Alabama against 1.1 million for the two dedicated models combined (5.2 against 2.0 at California) ... What the single model provides is operational rather than arithmetic." Never claims lower cost. ✓
- **Hygiene / evidence-guard (checklist 8) intact:** leak-audit prose restored (§setup-windows "Integrity of the representation", three grounds, region prior "built per fold from training data only" after "an earlier whole-dataset version inflated region accuracy by 13 to 27 points"); per-step hygiene sentences present; STAN partial-fold (†) and ReHDM single-seed (‡) disclosures kept; transductive limitation stated. ✓
- **Freeze control** reported as a finding, scoped: "the full category gain survives at Alabama, Arizona, and Florida"; "We report this attribution as a finding, not a hypothesis." ✓
- **Status wording:** "submitted to MobiWac 2026, under review" (preface + §intro). Never "published/accepted." ✓
- **N3 cosine +0.001 full scope** travels in §related-mtl: "averages +0.001 across training (four seeds each on three of our six datasets, per-dataset means within ±0.003) ... a finding for this pair of tasks, not a general rule." ✓

---

## TOP 3 FINDINGS

1. **[MAJOR] Cross-chapter numeric blur — the AL joint-model next-category cell reads 64.51 in Ch.5 but 64.54 in Ch.6** (joint-best vs diagnostic-best convention leak; N5 "the joint-best vs diagnostic-best distinction must never blur").
2. **[MAJOR] Data-vintage inconsistency — Ch.6 limitation 1 states "2009 and 2010", but Ch.5's own measured data provenance is 2009–2011** for the five-state datasets, and explicitly says the 2009–2010 range "is NOT the data source."
3. **[MINOR] Ch.3 CBIC dataset placeholders unresolved** ($N_{users}$/$N_{poi}$/$N_{checkins}$ render as visible `[VERIFY]` markers) — correctly not fabricated, but a number-completion blocker before the final build.

---

## RANKED FINDINGS (quote + location + rule + suggested direction)

### MAJOR-1 — AL joint-category value blurs joint-best (64.51) and diagnostic-best (64.54)
- **Ch.5** `chapters/5_mobiwac.tex:479` (Table III, joint-best convention): AL Joint category = `\textbf{64.51}\sd{0.09}`. The chapter states Table III is joint-best and that diag-best "would change every joint result by at most 0.06 (category)."
- **Ch.6** `chapters/6_conclusion.tex:77-78`: "its best configuration reaches 56.16 macro-F1, against 56.82 for the dedicated model at its own tuned width and **64.54** for the joint model."
- **Source:** `storyline/audit/capacity_baseline_experiment.md §5.3` quotes "joint v17 = **64.54** (n=20)" — this is the diagnostic-best board-of-record cell, 0.03 above the joint-best 64.51 the dissertation reports in Table III.
- **Rule:** WRITING_LAW §3 / AGENT_GUARDRAILS N5 — "the MobiWac joint-best vs diagnostic-best distinction must never blur." The same quantity (AL joint next-category macro-F1) reads two ways ~25 pages apart.
- **Impact:** the claim's direction (parameter count "yields nothing"; 56.16 ≪ joint) is TRUE under either value, so it does not mislead on the result. It is a convention blur a careful examiner cross-referencing Table III would catch.
- **Suggested direction (author rules):** reconcile Ch.6 to the dissertation's reported convention (64.51, the Table III joint-best value; the gap becomes +8.38 over the capacity arm, +7.69 over the ceiling = the whitelist's AL category Δ), OR add a half-clause naming the 64.54 as the diagnostic-best board value. Do not invent a third number. **Shared with persona 06 (value check).**

### MAJOR-2 — Gowalla vintage stated as 2009–2010 contradicts the project's own measured provenance (2009–2011)
- **Ch.6** `chapters/6_conclusion.tex:107-108` (limitation 1): "The five state datasets come from Gowalla check-ins collected in **2009 and 2010**."
- **Ch.5** `chapters/5_mobiwac.tex` data-provenance note (hidden comment, ~L295): "Date range MEASURED on the parquet 2026-07-09: 2009-01-21 .. 2011-08-16 -> 'collected 2009 to 2011'. **The SNAP/cho2011 dump (Feb 2009-Oct 2010) is NOT the data source.**" The five-state MobiWac data is the figshare CC0 dump (2009–2011), not the cho2011/SNAP Gowalla.
- **Ch.4** `chapters/4_courb.tex:349` says "collected between February 2009 and October 2010" — but that is the CoUrb/liu2014 Gowalla (published reproduced text), a different data source than Ch.5's five-state datasets.
- **Rule:** WRITING_LAW §3 (limitations are concrete AND honest — "2009-2010 Gowalla" is named as the model honesty item, so the concrete vintage must be the correct one) + AGENT_GUARDRAILS N1 (a frame chapter "may only repeat numbers already sourced in a chapter, with the same hedges"; the 2009–2010 vintage is not sourced in any chapter's prose and is contradicted by Ch.5's measurement).
- **Impact:** load-bearing honesty sentence; a banca reading limitation 1 against Ch.5's provenance would see a self-inconsistency. Does not touch a performance claim.
- **Suggested direction (author rules — this is genuinely ambiguous, so it is a QUESTION):** either (a) correct limitation 1 to "2009 to 2011" to match the figshare dump Ch.5 actually consumed, or (b) if the intent is to name the reference-dataset (cho2011) vintage generically across all three studies, say so explicitly and reconcile with Ch.5's measured range. Note Ch.3/Ch.4 use SNAP/liu2014 Gowalla (2009–2010) while Ch.5 uses the figshare dump (2009–2011) — the Conclusion consolidates all three, so the sentence needs to be precise about which data it bounds. **Shared with persona 06 (value check).**

### MINOR-1 — CBIC dataset statistics unresolved (visible placeholders)
- `chapters/3_cbic.tex:~330`: "[$N_{\text{users}}$; VERIFY: recompute per ERRATA.md] users, [$N_{\text{poi}}$; ...] unique Points-of-Interest, and [$N_{\text{checkins}}$; ...] check-ins."
- **Honesty verdict: CORRECT handling** — the values were never filled in the published paper; the chapter renders visible placeholders rather than fabricating them, and Appendix B (`tab:apx:cbic-errata` row 5) declares them "Pending. Not invented." This is exactly the fail-closed behavior AGENT_GUARDRAILS mandates.
- **Rule:** N2/N3 — the sanctioned path (repo-committed recompute over the CBIC-era FL pipeline, author-approved; CoUrb's FL row a cross-check only) must run before the final build; the placeholders cannot ship in the defense PDF.
- **Suggested direction:** number-completion task for persona 06 / the author; not a claim-honesty defect. **Handoff to persona 06.**

### MINOR-2 — Ch.2 "roughly a third" Food-share provenance pointer needs correcting
- `chapters/2_fundamentals.tex:~/§2.4`: "The Food class alone accounts for roughly a third of the check-ins in a representative state."
- The §2.4 ledger flags the provenance pointer should be the check-in distribution table (Alabama Food 34.2%), not the 32.5% POI-count table. The CLAIM ("roughly a third") is qualitative and TRUE under either figure (34.2% or 32.5%), so it holds; only the ledger's internal source pointer needs the fix.
- **Rule:** N3 (traceability of the number behind the claim). Claim intact; provenance line to tidy. **Handoff to persona 06.**

### NIT-1 — Ch.5 Table 1 Istanbul Majority (33.4%) from earlier windowing
- `chapters/5_mobiwac.tex:315` Istanbul Majority = 33.4; the table comment discloses it is "from the earlier windowing of the same visits (raw visit share 27.0; recompute on the dk_ovl inputs ... if exactness is wanted)." The §setup-windows prose range "from about 25 percent of visits in Florida to 34 percent in Alabama" uses the clean Gowalla cells (FL 24.7, AL 34.2), so the claim in prose is unaffected. Value-exactness item only. **Handoff to persona 06.**

---

## NEW-CLAIM LIST (C2 — for author sign-off)

All arc/frame claims trace to the NORTH_STAR §6 approved spine (verified above); no claim exceeds it. The following frame passages are marked `[NEEDS SIGN-OFF]` in the source and are author-owned by construction — listed so the author confirms them, not because they introduce unlicensed claims:
1. **Resumo + Abstract** (`0_main.tex`): claim-parity pair, drafted from Ch.1+Ch.6 only. Audit them as a pair (done — they match; headline 5.3–9.4 = rounded whitelist +5.33…+9.35). Author confirms the PT/EN wording is his.
2. **Ch.5 preface + recap subsection** (`5_mobiwac.tex`): new-to-chapter time-capsule prose; claims from the approved spine + whitelist, no numbers quoted. Confirm.
3. **Appendices A/B/C**: new frame prose (BRACIS containment, errata catalogue, AI disclosure). A satisfies C4 (BRACIS as "earlier unpublished iteration"; region-cost claim only as corrected history). Confirm scope + AI-tool naming (Appendix C leaves model-version naming to the author).
4. **Ch.6 §6.2 capacity-matched baseline paragraph**: POST-SUBMISSION frame analysis licensed by the D1 contract; reading (i) reported honestly. Confirm prominence/placement (D1 contract §3.2 leaves length discretionary; the outcome-binding floor is met). Fix MAJOR-1 (64.54→64.51) here.

---

## HONESTY DEVICES INTACT (the mandated keeps, verified present)

| Device | Location | Status |
|---|---|---|
| Time-capsule prefaces (venue/status/what-is-revised) | Ch.3, Ch.4, Ch.5 prefaces | ✓ all three present |
| CBIC null time-indexed + Nash-MTL of-the-time caution | Ch.3 preface; Ch.1 §1.2; Ch.6 §6.1 | ✓ |
| CoUrb sample-stratified-split disclosure | Ch.4 preface + §exp-setup; Ch.2 §2.4 GLOSSARY note | ✓ plain, not hidden |
| CoUrb ownership/contribution note | Ch.4 preface; Ch.1 §1.5 | ✓ |
| CoUrb "does not revisit MTL-vs-STL" floor sentence | Ch.4 preface | ✓ verbatim |
| AZ never upgraded (0.00 = match, not gain) | Ch.5 Table III (≈, unbolded), §results-part2, Ch.6, Abstract | ✓ everywhere |
| Region verbs bound to tests (↑ superiority / ≈ TOST) | Ch.5 Table III + prose; Ch.6; frame | ✓ |
| Scaling claim scoped to five U.S. states | Ch.5 §intro, §results-part2; "not a precise law" | ✓ |
| Cascade = defense at equal cost, not a win; not a re-implementation | Ch.5 §results-part2, §setup-baselines | ✓ |
| Compute-cost honesty (joint model larger; operational not arithmetic) | Ch.1 §1.2; Ch.5 §method-model; Ch.6 §6.2 | ✓ never promises lower cost |
| Leak-audit / hygiene sentences (per-fold prior, label-free, 13–27 pp inflation disclosed) | Ch.5 §setup-windows | ✓ restored + intact |
| Freeze control + capacity baseline as findings (gain in the shared trunk, not task-teaching, not parameter count) | Ch.5 §results-part2; Ch.6 §6.2 | ✓ "sharing stopped hurting", never "tasks teach each other" |
| N3 cosine +0.001 full scope (four seeds, three of six, this pair not a rule) | Ch.5 §related-mtl; Ch.6 §6.2 | ✓ travels verbatim |
| Negative result written with care (arc's foundation) | Ch.1 §1.2; Ch.6 §6.1, §6.4 | ✓ |
| BRACIS containment (corrected history only) | Appendix A | ✓ C4 satisfied |
| Task-pair confound concession + fixed-pair ablation future work | Ch.6 §6.3 lim 6, §6.4 | ✓ signed-off additions present |
| Placeholders left visible, not fabricated | Ch.3 dataset stats; Appendix B "Pending, Not invented" | ✓ fail-closed |

---

## OUT-OF-SCOPE HANDOFFS (one line each)
- **Persona 06 (numbers):** MAJOR-1 (64.51/64.54), MAJOR-2 (vintage), MINOR-1 (CBIC placeholders), MINOR-2 (Food-share pointer), NIT-1 (Istanbul majority) — all carry a value dimension; verify the values, I verified the claims around them.
- **Persona 08 (translation fidelity):** the Ch.4 English title rendering ("ST-MTLNet: Spatio-Temporal Point-of-Interest Representations for Multi-Task Learning") vs the published PT title is a translation-fidelity check, not a claim check.
- **Persona 04 (concordance):** MAJOR-1 and MAJOR-2 are also cross-chapter concordance items.

---

## WHAT HOLDS / WHAT READS WELL (do not touch)
- The arc is honest and the honesty devices are load-bearing and present. The verb-test binding is airtight across all six chapters — this is the single hardest thing to get right in this document and it is right.
- Ch.5 (the whitelist-governed chapter, highest fabrication risk) is whitelist-exact: no never-cite value, no AZ upgrade, cascade correctly framed, scaling correctly scoped, compute cost disclosed.
- The CBIC placeholders and the CoUrb audited-number corrections show the fail-closed discipline working as designed: nothing was smoothed over or invented.
- Ch.6's capacity-baseline paragraph is a model of honest post-hoc reporting: an unfavorable outcome would have been reportable (D1 contract), and the favorable one is not overstated.

## OPEN QUESTIONS (only the author can answer)
1. **MAJOR-2 vintage:** which data vintage bounds Ch.6 limitation 1 — the figshare dump Ch.5 measured (2009–2011), or a generic reference-dataset window? The five-state data Ch.5 uses is 2009–2011; the sentence currently says 2009–2010.
2. **MAJOR-1 convention:** reconcile Ch.6 to the joint-best 64.51 (dissertation's reported convention) or name 64.54 as the diagnostic-best board value?
3. **Appendix C:** name specific model versions (author-sourceable) or keep the family-level disclosure as drafted?

---

## VERDICT

**GATE PASS.**

No fail trigger is present: zero unlicensed claims (every arc/frame claim traces to the NORTH_STAR §6 approved spine and the MobiWac whitelist), zero verb-test mismatches (superiority↔"outperforms", TOST↔"matches" bound everywhere; AZ never upgraded; scaling scoped to the five U.S. states), zero C3 never-cite values, C4 BRACIS containment satisfied (Appendix A), and every mandated hygiene/fairness/honesty device is present and intact (inventory above).

Two **MAJOR** cross-chapter consistency findings remain (MAJOR-1: the 64.51/64.54 joint-best/diagnostic-best blur; MAJOR-2: the 2009–2010 vs 2009–2011 data vintage). Neither meets a gate-fail trigger — both preserve the direction and licensing of every result — but both are real defects a careful examiner would catch, both straddle persona 06's value-check scope, and both should be resolved before the advisor handoff. The three open questions are the author's to rule.

---

## `08_translation_fidelity_report.md`

# 08 · Translation Fidelity Checker — L5 gate report (CoUrb PT → EN)

**Scope:** Chapter 4 only — `src/chapters/4_courb.tex` vs the published Portuguese paper of
record `articles/CoUrb_2026/src/` (DOI 10.5753/courb.2026.22960, Anais do CoUrb 2026, pp. 323–336).
Intermediate EN translation `articles/CoUrb_2026/src_en/` used to classify each PT→chapter
difference as translation-artifact vs sanctioned-adaptation.
**Reviewer:** fresh eyes (did not draft this chapter). Read-only. **Date:** 2026-07-23.

---

## (1) VERDICT: **L5 PASS**

Every claim-bearing sentence in the English chapter maps 1:1 to the published Portuguese text in
quantifier, hedge, tense, negation, and scope. Every numeric value in the two result tables and
the dataset table is byte-identical to the published tables after locale normalization
(machine-checked: 63/63 category cells, 63/63 next-POI cells, 9/9 dataset counts — see §5). The
three departures from the published numbers/verbs are the **documented, audited errata**, applied
under the settled errata policy and listed in Appendix B — not silent fixes and not silent
reproductions. No claim was strengthened, weakened, or scope-shifted; nothing in the PT paper was
silently dropped, and nothing was added beyond the sanctioned frame devices (preface, MTLnet
recap subsection, protocol-honesty sentence, table lead-in sentences), each declared in the
chapter's `ADAPTATION_LEDGER.md` and/or Appendix B.

---

## TOP 3 FINDINGS

1. **[PASS — confirmation]** All three published CoUrb errata are correctly handled everywhere
   they occur: the category-gain range `20–24 pp` → audited `20.2 to 22.0 pp` with the
   best-of-two-encoders disclosure (chapter L33, L252, L343), and the sequential-task win count
   `16/21` → audited `15/21 + 1 technical tie` with the 0.02 pp / within-1σ explanation (L295,
   L343). No stray `16`, `76`, or `24` claim survives in the chapter. All three are itemized in
   Appendix B Table B.3. **This is the core of the L5 gate and it holds.**

2. **[MINOR — terminology landing, sanctioned]** The chapter keeps the paper's own task names
   *POI Category Classification* and *Next-POI Prediction* rather than the GLOSSARY canonical
   *category classification* / *next-category prediction*. This is **correct, not a drift**:
   GLOSSARY §1 rules "the chapter keeps the paper's usage and the frame uses this registry; the
   per-paper mapping in §2 bridges them." The chapter is internally clear that the predicted
   label is the category (intro list item: "predict the category of the next POI"). Flagged only
   so the author knows it was checked and is intentional — do **not** "fix" it to the canonical
   names inside Ch.4.

3. **[MINOR — coordination flag for persona 07, out of L5 scope]** The verb "outperforms" appears
   throughout the reproduced results prose resting on **mean-F1 comparison, not a paired
   significance test** (the CoUrb study reports mean ± std over 5 folds; no Wilcoxon/TOST). As a
   *translation* this is faithful — PT "supera"/"vence" → "outperforms" is equal-strength (ledger
   A3, "claim strength unchanged"). The note is cross-chapter: Ch.5 uses "outperforms" as a
   test-bound verb, so a reader may back-read significance onto Ch.4. The preface time-index +
   "only baseline / does not revisit MTL-vs-STL" sentence mitigates but does not explicitly say
   "no significance testing was performed." Author/persona-07 decision, not an L5 blocker.

---

## (2) DRIFT TABLE

Claim-bearing passages, PT-of-record vs EN chapter. Classification: **none** = faithful 1:1;
**number (sanctioned erratum)** = documented audited correction, not a fidelity failure.

| # | PT (published `src/`, verbatim) | EN chapter (`4_courb.tex`, verbatim) | Class |
|---|---|---|---|
| D1 | "ganhos médios de 20 a 24 pontos percentuais" (intro, results, conclusion) | "average gains per state of 20.2 to 22.0 percentage points, considering the better of the two spatial encoders in each combination" (L33, L252, L343) | **number — sanctioned erratum #2** (ledger A2, Appx B). Audit: FL +20.24 / CA +20.91 / TX +21.98; 22.0 = sanctioned rounding of 21.98. The "better of the two encoders" qualifier is the disclosure the audit requires. Not silent. |
| D2 | "os modelos espaço-temporais superam o MTLNet original em 16 das 21 combinações avaliadas" (results); "vence em 16 das 21" (conclusion) | "the spatio-temporal models outperform the original MTLNet in 15 of the 21 evaluated combinations, with one additional technical tie in *Outdoors* in Florida, where the *baseline* mean exceeds the best variant by 0.02 percentage points, a gap within one standard deviation" (L295); "in 15 of the 21 … with one additional technical tie" (L343) | **number — sanctioned erratum #1** (ledger A1, Appx B). Audit recount: 15 strict wins + 1 tie (FL Outdoors, baseline 21.61 vs Sphere2Vec-M 21.59). Not silent. |
| D3 | "o modelo proposto vence na maioria dos cenários" (intro) | "the proposed model outperforms the *baseline* in most scenarios" (L33) | **none** — banned verb "wins/vence" → "outperforms"; scope word "most scenarios / na maioria dos cenários" preserved exactly (ledger A3). Equal strength. |
| D4 | "ganhos particularmente **expressivos** em … *Nightlife* e *Travel*" (results) | "gains are particularly **substantial** in categories such as *Nightlife* and *Travel*" (L252) | **none** — "expressivo" is a false friend (means substantial-in-magnitude, not "expressive"); the correct EN sense was chosen (fixed at the `src_en` red-team stage). Faithful. |
| D5 | "a abordagem modular seja consistentemente superior ao *baseline*" (intro) | "the modular approach is consistently superior to the *baseline*" (L33) | **none** — 1:1. |
| D6 | "não há um único *encoder* espacial universalmente superior" (conclusion) | "there is no single universally superior spatial *encoder*" (L343) | **none** — 1:1. |
| D7 | "a diferença na dimensionalidade de entrada **pode influenciar parte** dos ganhos observados … permitiria validar de forma mais precisa" (methodology) | "the difference in input dimensionality **may influence part** of the observed gains … would allow validating more precisely" (§4.3 Embedding Integration) | **none** — hedge ("pode/may", "parte/part", conditional "permitiria/would allow") preserved 1:1. |
| D8 | "o *baseline* mantém vantagem em alguns casos, especialmente em *Travel* na Flórida e na Califórnia, além de … *Entertainment*, *Nightlife* e *Outdoors*" (results) | "the *baseline* maintains an advantage in some cases, especially in *Travel* in Florida and California, in addition to specific categories in California, such as *Entertainment*, *Nightlife*, and *Outdoors*" (L296) | **none** — 1:1 incl. all scope qualifiers. |
| D9 | Scope phrases throughout: "nos três estados", "três estados avaliados" | "in the three evaluated states" / "three states" (×5, no occurrence of "across the datasets" / "everywhere" / "six datasets") | **none** — scope never widened. Machine-checked. |

**Sanctioned frame additions** (present in chapter, absent from published PT — declared in ledger
§C and Appendix B, visibly frame material, no new results/contribution claims):
- **Preface** (L12): translated-reproduction statement + DOI + pages 323–336 + `\cite{paiva2026stmtlnet}`; Vitor's contribution note (2nd author, presenter, author of baseline MTLNet); sample-stratified-split caveat; time-index sentence; the "only baseline / does not revisit MTL-vs-STL, which Ch.5 reopens" floor sentence.
- **§4.2.5 "The MTLnet framework"** (L79–84): Ch.3 artifact recap + naming-variant note + time-indexed CBIC null recap.
- **Protocol-honesty sentence** in Experimental Setup (L224): "The split is stratified by sample, not by user, so the *check-ins* of one user may appear in both training and validation; Chapter 5 adopts a stricter user-disjoint protocol."
- **Three table lead-in sentences** (dataset/category/next-POI) + one Figure 4.2 caption reading-instruction (B4). Each reads its table/figure without introducing a new number or a new results claim; verified faithful to the cells. The dataset lead-in ("Texas concentrates the largest volume … Florida provides the smallest") is true from Table 4.1 (TX 3,355,419; FL 990,518).

---

## (3) TERMINOLOGY-LANDING REPORT

| PT term (published) | Chapter EN | GLOSSARY canonical | Landing verdict |
|---|---|---|---|
| Classificação de Categoria de POI | POI Category Classification | category classification | **OK — paper usage kept in-chapter** (GLOSSARY §1/§2 per-paper mapping; frame bridges). |
| Predição do Próximo POI (categoria) | Next-POI Prediction | next-category prediction | **OK — paper usage kept**; chapter defines it as "predict the category of the next POI". Frame owns the bridge sentence. |
| check-in / check-ins | check-in / check-ins (italic) | check-in (never "event") | **OK.** |
| POI / Ponto de Interesse | POI / Point of Interest | POI / place (never "venue") | **OK** — "place" also used; no "venue". |
| baseline | *baseline* (italic, paper voice) | dedicated single-task model / baseline | **OK in-chapter** (reproduced-paper voice; the frame reserves "dedicated single-task model"). |
| supera / vence | outperforms | verb bound to test in frame | **Faithful translation** (equal strength); cross-chapter verb-law note → finding #3 / persona 07. |
| representações desacopladas | decoupled representations | — | **OK — consistent.** |
| MTLNet (paper spelling) | MTLNet ×45 in body; MTLnet ×4 in the recap subsection with explicit note "the published paper typesets the name as MTLNet, and this chapter preserves that form" | MTLnet (glossary) / MTLNet (paper) | **OK — the naming-variant note (L82) is exactly the GLOSSARY-sanctioned bridge.** Body preserves the paper's MTLNet; the frame recap uses MTLnet and reconciles the two. |

No ad-hoc translation created a synonym pair with another chapter within Ch.4's own text.

---

## (4) ERRATA-POLICY CHECK — **PASS**

Policy (NORTH_STAR §5.7, decision #7): fix silently in the re-typeset chapter + one frame
sentence + list every departure in Appendix B; published records not edited.

- **Not silently reproduced:** the erroneous `16/21` and `20–24 pp` do not appear as chapter
  claims (grep: zero surviving `16`/`76`/`24` result claims).
- **Not silently fixed:** all three corrections are itemized in **Appendix B Table B.3**
  (`apx_b_errata.tex`), matching the audit source `slides/judge_feedback.md` §2 and
  `articles/CoUrb_2026/ERRATA.md`.
- **Preservation done right:** the published bold on the FL-Outdoors baseline cell in the
  next-POI table is kept exactly (`\textbf{21.61 ± 0.99}`); the technical-tie reading lives in
  prose only (ledger A4). This is the correct "reproduce the table, correct the prose" split.
- The published paper's **abstract** (which carried the uncorrected "76%" and "20–24 pp") is
  dropped per coletânea convention (ledger B7); the erroneous abstract numbers therefore do not
  leak into the chapter, and the corrected values appear in intro/results/conclusion. Clean.

---

## (5) SECTIONS VERIFIED CLEAN (coverage)

| Section | Grain | Result |
|---|---|---|
| Preface (frame) | sentence | All mandated elements present and correct (DOI, pages, authorship, split caveat, time-index, floor sentence). |
| §4.1 Introduction | sentence | 1:1 with `src/sections/intro.tex`; erratum #2 + verb sub applied. |
| §4.2 Related Work (4 axes) | paragraph | 1:1 with `src/sections/related.tex`; all cited systems described as in PT. |
| §4.2.5 MTLnet recap | sentence | Sanctioned frame addition; time-indexed, no new result claim. |
| §4.3 Methodology (baseline, data prep, spatial/SIREN/Sphere2Vec-M, temporal/Time2Vec, categorical/POI Encoder/HGI, integration) | paragraph | 1:1 with `src/sections/metodology.tex`; every parameter identical (64/192/256, L_h=9, 1728/576, τ=0.15, 10/70 km, α=0.5, S=16, 10 km–10,000 km, 7 classes, 8 heads/4 layers, 2/3/4-layer MLPs). |
| §4.4 Results (setup, category, next-POI) | sentence + cell | Prose 1:1; both errata applied; split-honesty sentence added; **tables cell-identical** (machine-checked). |
| §4.5 Conclusion | sentence | 1:1 with `src/sections/conclusion.tex`; both errata applied; limitations (Travel, no ablation, Gowalla 2009–2010) 1:1. |

**Machine checks run (fail-closed):**
- Category table: 63 mean±std cells PT vs chapter → **IDENTICAL**.
- Next-POI table: 63 cells → **IDENTICAL**.
- Dataset table: 9 counts {20301, 36106, 37522, 65009, 135570, 148314, 990518, 2535573, 3355419} → **IDENTICAL** (locale normalized).
- Scope-phrase sweep: "three states" only; no "datasets/everywhere/six" widening.
- Banned verb sweep: zero "wins/win/beats" in prose.

---

## WHAT HOLDS / WHAT READS WELL (do not touch)

- The **errata handling is exemplary**: corrected in prose, preserved in the table cell, disclosed
  in Appendix B, traced in the ledger. This is precisely the "not silent either way" standard.
- The **preface** carries the full reproduction statement, authorship note, protocol caveat,
  time-index, and the Ch.5-reopening floor sentence in four clean sentences — the most
  fidelity-sensitive paragraph in the chapter, and it is correct.
- **Number fidelity is total** — no fabricated, dropped, or corrupted cell; the hardest failure
  class for translated result tables is fully clean.
- The **false-friend trap** ("expressivo" → "substantial", not "expressive") was caught upstream
  and is right in the chapter.

---

## OUT-OF-SCOPE HANDOFFS (one line each)

- **→ persona 05 (citation auditor):** bib-key renames between PT and chapter for the *same works*
  — `huang2023learning`→`huang2023hgi` (HGI), `cho2011friendship`→`cho2011gowalla` and
  `10.1145/2661829.2662002`→`liu2014geographical` (Gowalla), and the sanctioned
  `church2017word2vec`→`mikolov2013word2vec` (Appx B bib row 6). Confirm the global bib resolves
  each renamed key to the identical work.
- **→ persona 07 (claim & honesty):** the mean-F1-based "outperforms" verb across the reproduced
  results (finding #3) — decide whether the preface needs one sentence stating no significance
  test was applied in this study, to prevent cross-chapter back-reading from Ch.5's test-bound
  "outperforms".
- **→ persona 04 (concordance) / frame:** ensure Ch.1/Ch.2 state once that CoUrb's "Next-POI
  Prediction" = the canonical "next-category prediction" (GLOSSARY §2 mapping); the bridge is a
  frame duty, not a Ch.4 edit.
- **→ persona 18 (visual):** the chapter title uses `\:` (renders as a thin space, not a colon)
  and the wording "Point-of-Interest Representations" vs the paper's EN "Representations of Points
  of Interest" — both are pre-existing author `[VERIFY]` flags in the ledger; heading/render, not
  claim fidelity.

## OPEN QUESTIONS (author only)

1. Chapter-heading title form + the `\:` thin-space (ledger §E [VERIFY] flags) — confirm the
   intended EN title wording and whether a literal colon is wanted (global to Ch.3/4/5 stubs).
2. Whether to add the Nash-MTL solver-bug caveat to Ch.4 (ledger §E marks it NOT added, to avoid
   a new claim; a preface sentence is the place if wanted).

---

## `10_mtl_expert_report.md`

# MTL Expert Review — Dissertation v1 (persona 10)

> Reviewer: MTL domain expert (persona `10_mtl_expert.md`). Read-only.
> Scope: Ch.2 (MTL fundamentals), Ch.3 (CBIC), Ch.4 (CoUrb), Ch.5 (MobiWac), MTL claims in Ch.1/Ch.6.
> Default prior: a tuned fixed-weight scalarization matches specialized MTL optimizers
> (Kurin 2201.04122; Xin 2209.11379; Royer 2310.08910; Hu 2308.13985).
> Sources of truth per reviewers/README §Sources. Numbers traced, never recomputed unless noted.
>
> STATUS: COMPLETE (2026-07-23).

## Files reviewed (read in full)
- src/chapters/2_fundamentals.tex — §2.3 MTL is the core of scope; §2.4 evaluation
- src/chapters/3_cbic.tex — the published null result (arc foundation)
- src/chapters/4_courb.tex — representation ablation (within-MTL)
- src/chapters/5_mobiwac.tex — the joint-model win (highest MTL content)
- src/chapters/1_introduction.tex — MTL/arc claims
- src/chapters/6_conclusion.tex — the consolidated MTL answer + capacity baseline
- Traced against: docs/studies/closing_data/{RESULTS_BOARD,perhead_lr_n20,joint_best/JOINT_BEST_RESULTS,v17_completion/CEILINGS_N20_FINAL}.md;
  storyline/audit/capacity_baseline_experiment.md; articles/[mobiwac]/src/sections/*.tex (to establish what is inherited vs introduced).

## Overall verdict: **SOUND-WITH-CORRECTIONS**

The MTL content is, at the level of the science, in strong shape and unusually well defended against
the field's 2022–2026 skeptical turn: the dissertation's own finding (a tuned fixed weighting won; the
balancers did not) *aligns* with the field null, and the text cites the skeptic literature (Kurin, Xin)
rather than only pro-balancer work. The freeze control, the parameter-count disclosure, the
capacity-matched baseline, the joint-best convention with its robustness bound, the test-bound region
verbs, and the task-pair confound concession are all present where the claims live. The verdict is not
"sound" because of **one BLOCKER**: Chapter 5 states that the CBIC prior work studied *next-category and
next-region* and *observed negative transfer*, which is false on both counts and contradicts Chapters 1,
3, 4, and 6 of this same document. It is inherited verbatim from the MobiWac version of record, so it is
a framing error the coletânea format newly exposes, and it is fixable through the sanctioned errata
mechanism, not an integrity problem with the experiments. Three MAJOR items (a cross-chapter joint-value
inconsistency, a mechanism sentence that over-generalizes the gradient-cosine measurement, and a
loss-shaping concordance gap) should be fixed before the advisor sees the document.

## Top 3 findings
1. **[BLOCKER] Ch.5 attributes a next-region task and an observed negative-transfer result to CBIC,
   which had neither** — contradicts Ch.1/Ch.3/Ch.4/Ch.6 (Finding 1).
2. **[MAJOR] The joint Alabama next-category score is 64.51 in Ch.5's headline table but 64.54 in Ch.6's
   capacity discussion** — the joint-best/diagnostic-best distinction (lens 6) blurs across chapters
   (Finding 2).
3. **[MAJOR] "A balancer therefore has no conflict to resolve" over-generalizes a directional (cosine)
   measurement to magnitude-based balancers** — the single most likely MTL-examiner objection; tighten and
   cite Elich (Finding 3).

## Ranked findings

### Finding 1 — BLOCKER (lens 12; attack Q12; NORTH_STAR §6 signed-off addition (a))
**Ch.5 states CBIC studied next-category + next-region and observed negative transfer. Both are false, and
both contradict the rest of the dissertation.**

Quotes (src/chapters/5_mobiwac.tex):
- L44: *"Prior work observed exactly this for next-category and next-region~\cite{silva2025mtlnet}"*
  (the "this" = "shared parameters can converge to a compromise ... helping one while hurting the other").
- L140: *"Our earlier work~\cite{silva2025mtlnet} established this two-task setup and observed negative
  transfer (sharing hurt one task)"* (in §5.2.3, titled "Predicting the next category and the next region").

Why it is false:
- CBIC (Ch.3, L34–35) studies **(1) POI Category Classification [static] and (2) Next-POI Prediction =
  "Predicting the category of the next POI"**. There is **no region task anywhere in Ch.3**. CoUrb (Ch.4,
  L24–25) studies the same two. **MobiWac (Ch.5) is the first chapter to add next region** — the chapter
  itself claims this novelty ("the first work to treat fine-grained region as an end target", L58).
- CBIC's *result* was a parity null, not an observed negative transfer. Ch.3 reports the MTL/Single
  difference is *"largely comparable ... without a clear, consistent, and significant advantage"* and only
  **hypothesizes** *"Subtle Negative Transfer"* ("We hypothesize", Ch.3 L358–360). Ch.4's recap states it
  correctly: MTLnet *"performed on par with the dedicated single-task models at a higher training cost"*
  (Ch.4 §4 mtlnet-recap). Ch.5 upgrades that hedged hypothesis into an observed fact ("sharing hurt one task").

Contradiction surface inside the dissertation (this is what makes it a BLOCKER, not a MINOR): the correct
framing is stated four times elsewhere — Ch.1 §1.2 (*"the first two studies paired next category prediction
with the static classification of a place's category"*), Ch.1 §1.2 arc (*"the task pair therefore evolved
... from static category classification plus next category in the first two to next category plus next
region in the last, and this dissertation names that evolution plainly"*), Ch.3's task definitions, Ch.4's
task definitions, and Ch.6 limitation 6 (*"Chapters 3 and 4 paired static category classification with next
category, while Chapter 5 pairs next category with next region"*). An examiner who reads Ch.3 then reaches
Ch.5 L140 has a one-line kill-shot: *"Chapter 3 has no region task — how did it observe negative transfer
on next region?"* This directly violates the signed-off addition NORTH_STAR §6(a) ("named plainly, never
narrated as one experiment on a constant pair").

Provenance / fix path: inherited verbatim from articles/[mobiwac]/src/sections/01_introduction.tex L17 and
02_related.tex L48–49. In the standalone paper, CBIC is only a citation and the slip is hard to check; in
the coletânea, CBIC is the adjacent Chapter 3. Suggested direction (author, not applied): correct the two
sentences so the negative-transfer observation is attributed to CBIC's *actual* pair (static category
classification + next category) — or to Caruana-style MTL in general — and state the region task enters in
this chapter; align the CBIC characterization with Ch.4's "on par" (or supply the measured basis if
"sharing hurt one task" is to stand). Because this departs from the version of record, log it in
articles/[mobiwac]/ERRATA.md and Appendix B per NORTH_STAR §4/§5(7).

### Finding 2 — MAJOR (lens 6; guardrails N5)
**The same joint result (Alabama, next-category, n=20) is 64.51 in Ch.5 and 64.54 in Ch.6 — the joint-best
vs diagnostic-best conventions are blurred across chapters.**

- Ch.5 Table 3 (`tab:mobiwac:results`) reports joint Alabama category = **64.51 ±0.09**. This is the
  **joint-best** value (author ruling 2026-07-18 to report joint-best; JOINT_BEST_RESULTS.md L32:
  `AL | ... | 64.54 ±0.10 | 64.51 ±0.09 | −0.04`, where 64.54 is diag-best, 64.51 is joint-best).
- Ch.6 §6.2 capacity paragraph quotes the joint as **64.54** ("56.16 macro-F1, against 56.82 for the
  dedicated model ... and 64.54 for the joint model") and again ("reaches 56.16 ... 64.54"). 64.54 is the
  **diagnostic-best** value, inherited from the capacity record (capacity_baseline_experiment.md §5.3:
  "joint v17 = 64.54 (n=20)").

Impact: the numeric verdict is unaffected (the capacity gap is +7.72 with 64.54 or +8.35 with 64.51), so
no *conclusion* moves. But lens 6 requires the joint-best/diagnostic-best distinction to *never blur*, and
here the flagship table reports one convention while the Conclusion silently uses the other for the same
cell. A number auditor comparing Ch.5 Table 3 to Ch.6 finds joint-AL = 64.51 ≠ 64.54. Suggested direction:
in Ch.6 use 64.51 to match Ch.5's reported convention (gap becomes +8.35), or state explicitly that the
capacity comparison is against the diagnostic-best joint value and why. Hand the exact numeric
reconciliation to persona 06 (number auditor).

### Finding 3 — MAJOR (lens 2; attack Q6; must-cite Elich 2311.04698)
**"A balancer therefore has no conflict to resolve" generalizes a directional (cosine) measurement to all
balancer families; magnitude-based balancers act on an axis the cosine does not measure.**

Quote (Ch.5 §5.2.4, L180–187): *"none of the balancers that we tried ... improved on a tuned fixed task
weighting in our model. The reason is visible in the gradients. ... the cosine similarity between the
next-category and next-region updates on the shared trunk averages +0.001 ... A balancer therefore has no
conflict to resolve"*.

The measurement itself is exemplary and honestly scoped (four seeds, three of six datasets, per-dataset
means within ±0.003, development-time, earlier data preparation, "a finding for this pair of tasks, not a
general rule"). The problem is the inference verb. Cosine ≈ 0 establishes there is no *directional*
conflict — which cleanly explains why the gradient-*surgery* family (PCGrad, CAGrad, Nash-MTL) found
nothing to project away. It does **not** establish "no conflict to resolve" for the *magnitude/loss-scale*
family (GradNorm, uncertainty weighting), which target gradient-norm imbalance, an axis a cosine cannot
see (Elich et al., arXiv:2311.04698: angular conflict is not the whole story; magnitude differences
dominate and Adam already partially normalizes scale). The honest reason those balancers did not help is
that **the tuned fixed 0.75/0.25 weighting already sets the task scale** — a static intervention on exactly
the axis GradNorm/UW would adjust. The empirical backstop ("none of the balancers we tried improved") makes
the *conclusion* sound regardless, so this is a tighten-and-cite fix, not a retraction. Suggested direction:
scope the sentence to directional conflict ("no *directional* conflict for a gradient-surgery method to
resolve; the fixed weighting already fixes the task scale"), and cite Elich (currently absent everywhere —
Kurin + Xin are present, which meets the skeptic-block minimum, but Elich is the specific anchor for a
gradient-conflict mechanism claim). Same sentence recurs in Ch.6 §6.2 ("essentially orthogonal gradients:
sharing stopped hurting") — that phrasing is safer and can stay.

### Finding 4 — MAJOR (attack Q9; lens 3 confound)
**Ch.2 says the pipeline uses class-weighted cross-entropy; Ch.5 says the joint model uses plain unweighted
cross-entropy and that class-weighting was tested and rejected. The dedicated arms' loss shaping is never
stated, leaving the MTL-vs-STL loss-shaping parity undocumented.**

- Ch.2 §2.4 (L409–410): *"The training pipeline counters the same imbalance with class-weighted
  cross-entropy."* §2.4 presents itself as the protocol "used throughout".
- Ch.5 §5.2 method-model (L248): *"$L_{cat}$ and $L_{reg}$ are plain unweighted cross-entropy losses ...
  Class-weighting, tested on both outputs, lowered both region accuracy and category macro-F1."*

Two problems: (i) a document-wide concordance contradiction on a method fact (class-weighted vs unweighted)
that lands in the fundamentals chapter, my primary scope; (ii) a Q9 confound-disclosure gap — Ch.5 states
the *joint* model's loss shaping (unweighted) but never states the *dedicated* single-task arms use the same
unweighted CE. If MTL and STL arms differed in loss shaping, the transfer comparison would be confounded.
It is very likely both arms are unweighted (the class-weighting rejection is disclosed, and the method
comment in the source reads "both outputs plain unweighted cross-entropy"), so this is probably a disclosure
gap rather than a real confound — but the text should say so at the dedicated arm, and Ch.2 must not assert
the opposite of what the headline model does. Suggested direction: reconcile Ch.2 §2.4 to the actual
practice (state that the joint model uses unweighted CE, class-weighting having been tested and rejected;
if class-weighting was used only in CBIC/CoUrb, scope the Ch.2 sentence to those chapters), and add one
clause to Ch.5 confirming the dedicated arms use identical unweighted CE. Hand the document-wide
reconciliation to personas 04 (concordance) and 06/09.

### Finding 5 — MINOR (attack Q1, Q8; lens 7)
**The balancer sweep budget is not stated, and the Nash-MTL solver used in the MobiWac sweep is not
identified relative to the CBIC-era solver bug.**

Ch.5 §5.2.4: *"none of the balancers that we tried, including [PCGrad, Nash-MTL], improved on a tuned fixed
task weighting"*. The fixed weight was "tuned once on validation"; the balancers' tuning budget is not
given (defaults or swept?). Asymmetry favors the null, so risk is low and the finding aligns with the field
prior — but a pro-balancer examiner (Kurin) will ask. Separately: Ch.3's preface contains the Nash-MTL
solver-bug containment (the CBIC-era NashMTL collapsing to [1,1]); Ch.5 does not say whether its Nash-MTL
run used the fixed solver. If it used the buggy one, "Nash did not beat fixed weighting" is partly
confounded — though the 0.75/0.25 fixed weight differs from a collapsed-to-[1,1] Nash, and the cosine
mechanism is solver-independent, so the conclusion survives either way. Suggested direction: one clause on
the balancer budget ("run at their published defaults" or "swept over X"), and a half-sentence confirming
the corrected Nash-MTL solver was used.

### Finding 6 — MINOR (must-cite canon; lens 3)
**Ch.2 §2.3 attributes the negative-transfer definition to a task-grouping paper and omits the canonical
anchor.**

Ch.2 §2.3: negative transfer is introduced via *"joint training can hurt as easily as it helps depending on
the pairing \cite{standley2020tasks}"*. Standley (1905.07553) supports the *pairing-dependence* claim but is
not the definitional source; the canonical negative-transfer anchor Zhang et al. (arXiv:2009.00909, "which
tasks should be learned together") is absent, as noted in the section's own ledger ("Zhang2020 REMOVED").
The informal definition given ("joint training can leave a task worse off than its single-task model") is
correct. Also absent from the skeptic block: Hu (2308.13985, theory), Royer (2310.08910), Elich
(2311.04698) — Kurin + Xin are present, meeting the essential minimum. This is a thin frame chapter, so the
guidance is: flag the gap, do not demand padding. Adding Zhang 2009.00909 (one cite) at the
negative-transfer definition and Elich where the cosine mechanism is discussed (Finding 3) would close the
two that matter.

### Finding 7 — MINOR (lens 7; NORTH_STAR §4)
**Ch.3's Nash-MTL preface caveat is vaguer than the repo record supports.**

Ch.3 preface: *"The chapter's preference for the Nash-MTL optimizer is likewise a conclusion of the time,
weakened by a later finding about the optimizer implementation"*. This satisfies the NORTH_STAR §4
containment ("the chapter preface may note the later finding"), and the body's Nash-MTL "consistently
yielded a better overall performance" claim is thereby contained. NORTH_STAR §4 only requires "may note", so
this passes — but "a later finding about the optimizer implementation" is soft; a reader cannot tell the
finding was a solver collapse to equal weights. Optional sharpening (author's call): name it as "a
solver-implementation bug that collapsed the balancer toward equal weighting", which strengthens the honesty
rather than weakening the chapter.

### Finding 8 — MINOR (lens 4/5; attack Q7)
**The freeze control (category-gain attribution) is run on 3 of 6 datasets; the category gain is claimed on
all six. The region win (4/6) has no symmetric per-direction control.**

Ch.5 §5.2.2: *"the full category gain survives at Alabama, Arizona, and Florida ... We therefore attribute
the category gain to a stronger shared trunk"* — reported "as a finding, not a hypothesis". The scope (3
named datasets) is stated in the sentence, so this is not hidden; but the attribution is generalized to the
category gain at all six, and Istanbul/TX/CA are untested by the freeze control. Separately, the freeze
control gives the *region-does-not-teach-category* direction only; the region win at 4/6 has no symmetric
control, and the text correctly does **not** claim "category teaches region" (it credits the private spatial
path + trunk semantic context), so there is no silent reverse-direction claim (lens 5 satisfied) — but the
region gain's source is less dissected than the category gain's. Suggested direction: soften "as a finding"
to name its scope ("at the three datasets where the control was run"), which Ch.6 already does correctly and
Ch.5 could mirror.

### Finding 9 — NIT
Ch.5 §5.2.2: *"A reader used to multi-task learning expects the harder task ... to teach the easier one"* is
a loose characterization of MTL expectations (the standard expectation is shared-representation
regularization, not specifically harder→easier transfer). It motivates the freeze control adequately; no
action needed beyond awareness.

## Credibility signals present (what an MTL expert will trust here)
- **Scalarization-first skepticism cited, not dodged.** Ch.2 §2.3 and Ch.5 §5.2.4 both cite Xin
  (2209.11379) and Ch.2 cites Kurin (2201.04122); the text states the fixed-weight baseline is "a serious
  competitor" and the finding *aligns* with the field null rather than claiming a balancer win.
- **Gradient-cosine measured and fully scoped** (four seeds, three datasets, ±0.003, development-time,
  "not a general rule") — not asserted "not shown".
- **Parameter-count disclosed as cost** ("4.2M at Alabama against 1.1M ... operational rather than
  arithmetic"); no compute-saving claim anywhere (F3 guard held, incl. Ch.1).
- **Freeze control** attributes the category gain to the trunk, explicitly refuting "the region task
  teaching the category one".
- **Capacity-matched dedicated baseline** (Ch.6 §6.2) closes the parameter-count alternative: a 4.2M-param
  dedicated category model reaches 56.16 vs 56.82 tuned-narrow, recovering none of the joint gain.
- **Joint-best convention named + diagnostic-best robustness bound** ("at most 0.06 / 0.11 points, so no
  claim depends on this choice").
- **Conservative asymmetry:** dedicated category models tuned per-dataset; the joint model uses one fixed
  config across all six and still wins.
- **Region verbs bound to tests; AZ never upgraded** ("interval centered on zero, so we report a match, not
  a gain").
- **Task-pair confound conceded** (Ch.6 limitation 6) with the fixed-pair ablation named as future work.
- **CBIC null time-indexed** and **Nash-MTL solver-bug contained** in the Ch.3 preface.
- **CoUrb capacity confound acknowledged** (192-d vs 64-d input; §4 embedding-integration calls for a
  dimensionality-equalized control).

## Unstated defenses (facts the repo holds but the text does not fully carry)
- **The cosine is directional-only, and the fixed weight handles the scale axis.** The capacity record and
  the field literature support this reasoning, but the chapter's mechanism sentence asserts "no conflict to
  resolve" without it (Finding 3). Stating it converts a weak spot into a defense.
- **The dedicated arms use the same unweighted CE as the joint model** (implied by the source method
  comment and the class-weighting rejection) — but Ch.5 never states the dedicated arms' loss shaping, so
  the loss-shaping parity that defeats the Q9 confound is undocumented (Finding 4).
- **The capacity sweep's fairness scope** (capacity_baseline_experiment.md §5.3: the wide arm got a
  3-recipe sweep vs the ceiling's wider grid; the 0.55 pp spread ≪ the 8.4 pp gap, so a wider grid cannot
  change the verdict) — Ch.6 carries the numbers and the "partial California, fifteen of twenty" honesty,
  but not the fairness-scope caveat. Worth one clause whenever the capacity number is quoted.

## Out-of-scope handoffs (noted, not judged by this persona)
- **Statistics/leakage** → persona 09: n=4 paired t / TOST power; development-seed contamination (Q10:
  recipe decisions made on the reported seeds?); the A4 leak-audit prose and the region-transition-prior
  per-fold rebuild.
- **Numbers** → persona 06: the exact 64.51/64.54 reconciliation (Finding 2); the Ch.6 capacity numbers
  (56.16/56.82/64.54) against al_capmatch_summary.json; CoUrb 15/21 + 1 tie and +20.2–22.0 pp.
- **Citations** → persona 05: `\cite{nash}` vs the ledger's `navon2022nashmtl` — verify the key resolves in
  the global bib; the DGI triple-key consolidation.
- **Concordance** → persona 04: the Ch.2↔Ch.5 class-weighted/unweighted contradiction (Finding 4) as a
  document-wide pass; the CBIC-task-pair reconciliation (Finding 1) across Ch.1/3/4/5/6.
- **POI/novelty** → persona 11: "first work to treat fine-grained region as an end target of equal
  standing".

## Open questions only the author can answer
1. Which joint Alabama next-category value is canonical for the frame — **64.51** (joint-best, Ch.5
   headline) or **64.54** (diagnostic-best, Ch.6 capacity comparison)? (Finding 2)
2. Do the **dedicated single-task arms use unweighted cross-entropy identical to the joint model**? Confirm
   for the Q9 parity disclosure. (Finding 4) And what is the source of Ch.2 §2.4's "class-weighted
   cross-entropy" statement — CBIC/CoUrb only, or a stale generalization?
3. Was **MobiWac's Nash-MTL run with the corrected solver** (post the CBIC-era [1,1] collapse)? (Finding 5)
4. Do you want the **CBIC negative-transfer misattribution corrected via ERRATA.md** (silent fix in the
   dissertation text + Appendix B listing), given it is inherited from the version of record? (Finding 1)

---
## Working notes (raw; superseded by the ranked findings above)

### Ch.2 §2.3 (MTL fundamentals) — working notes

**Scalarization skepticism (lens 1): PRESENT and correctly positioned.** §2.3 cites the
skeptic block: lin2022rlw (RLW competitive), xin2022domtl (optimizers often do not beat tuned
fixed weights), kurin2022scalarization (unitary scalarization matches/improves). Closes with:
"a fixed-weight baseline is a serious competitor, and a balancer earns its place only by
outperforming it." This is the field's null, stated correctly. Text engages Kurin AND Xin, not
only pro-balancer work. GOOD.

**Balancer canon coverage: essentially complete.** Present: caruana1997multitask, ruder2017,
kendall2018 (UW), chen2018 (GradNorm), sener2018 (MGDA), liu2019 (DWA), yu2020pcgrad, liu2021cagrad,
navon2022nashmtl (Nash), senushkin2023aligned, liu2023famo, lin2022rlw, kurin2022, xin2022,
vandenhende2022, standley2020, MMoE/PLE/DSelect-k/cross-stitch all present.
CAGrad "with convergence guarantees" — accurate. FAMO "constant time/space" — accurate.

**Canon GAPS (flag, do not demand padding — thin frame chapter):**
- Skeptic block INCOMPLETE: Hu (2308.13985, theory), Royer (2310.08910), Elich (2311.04698,
  gradient-conflict mechanism) NOT cited. Kurin+Xin present = essential minimum met. Elich is
  the one that matters IF Ch.5 makes a gradient-cosine mechanism claim (check Ch.5).
- Negative-transfer canonical anchor Zhang 2009.00909 NOT cited; §2.3 attributes negative
  transfer to standley2020tasks. Standley supports "joint training can hurt depending on
  pairing" (true) but is a task-grouping paper, not the definitional source. The informal
  definition given ("worse off than its single-task model") is CORRECT. MINOR.
- Task grouping TAG (2109.04617), surveys Zhang&Yang (1707.08114), Crawshaw (2009.09796) absent.
  Frame chapter; not blocking.

**Nash-MTL cite-key mismatch:** prose uses `\cite{nash}`; ledger references `navon2022nashmtl`
[ERRATA: consolidate nash double-key]. Verify `nash` resolves in the global bib (citation-auditor
scope; flag for cross-check). Description of Nash-MTL is accurate.

**MTLnet null (lens 12): time-indexed correctly.** "does not outperform the dedicated single-task
models, a result that holds for that configuration" — verb bound, "beat" removed, time-capsule
framing present. GOOD.

**Structured-sharing lineage (lens): NOT overclaimed.** Joint model "adopts the principle...
realized with cross-attention... though it realizes it with cross-attention rather than expert
gating" — no false PLE/MoE descent. GOOD.

**§2.4 evaluation:** TOST two-point margin, paired Wilcoxon bound to "outperforms", Holm,
user-disjoint StratifiedGroupKFold, majority floor + Markov floor + single-task ceiling all
present. song2010limits 93% correctly scoped as next-LOCATION bound, explicitly NOT a ceiling on
category macro-F1 / region Acc@10. Delta_m (maninis2019) as relative multi-task change. GOOD for
MTL-relevant evaluation framing.

**§2.5 relevance / hinge:** win verb explicitly bound to tests ("by paired superiority tests,
outperforms... on next category everywhere and next region at four of six datasets, and matches...
by non-inferiority testing... at the other two"). AZ/AL never upgraded. GOOD. (Number four-of-six
+ margin to be confirmed against Ch.5 board — cross-chapter, verify in Ch.5 read.)

### Ch.5 (MobiWac) — working notes (the win; highest-MTL-content chapter)

STRONG CREDIBILITY SIGNALS (lenses 1-8 largely satisfied):
- **Scalarization-first (L1):** §5.2.4 "joint training with a fixed loss weighting is standard
  practice, not itself our contribution... gradient-balancing methods... rarely improve on a
  well-tuned fixed weighting with two tasks [xin2022domtl]. We confirm this: none of the
  balancers that we tried, including [PCGrad, Nash-MTL], improved on a tuned fixed task
  weighting." Null-aligned, cites Xin. GOOD.
- **Gradient mechanism (L2):** §5.2.4 cosine +0.001 CITED WITH FULL SCOPE: "four seeds each on
  three of our six datasets, per-dataset means within ±0.003", "measured during development on
  an earlier preparation of the data", "directional conflict only", "a finding for this pair of
  tasks, not a general rule." Matches NORTH_STAR §6 N3 verbatim. Scope honestly stated. GOOD.
- **Capacity (L4):** §5.method-model parameter disclosure "4.2 million parameters at Alabama
  against 1.1 million for the two dedicated models combined (5.2 against 2.0 at California)...
  operational rather than arithmetic." No compute-saving claim (F3 guard held). GOOD.
- **Freeze control (L3/L4):** §5.results-part2 "We freeze the region pathway at the start of
  training so it can neither learn nor teach the category task, yet the full category gain
  survives at Alabama, Arizona, and Florida (within 0.3 of the joint model)... We therefore
  attribute the category gain to a stronger shared trunk, not to the region task teaching the
  category one." Gain-as-transfer explicitly refuted. GOOD.
- **Checkpoint honesty (L6):** §5.results-part2 joint-best convention named + diagnostic-best
  robustness bound "at most 0.06 (category) and 0.11 (region) points, so no claim depends on this
  choice." Selector a priori (geom_simple). Convention named at the table. GOOD.
- **STL tuned (Q2):** dedicated category "tuned per dataset over batch size and learning rate";
  joint uses ONE fixed config across all six -> joint wins DESPITE per-dataset-tuned dedicated
  category. Conservative. GOOD.
- **Per-task reporting (L8):** Table 3 per-task columns + Fig 4 signed deltas; geom-mean used
  ONLY for selection/cascade, never as headline. GOOD.
- **Region verbs bound to tests:** outperforms Ist/FL/TX/CA (90% CI > 0), matches AL/AZ (TOST
  ±2pp); AZ never upgraded ("interval centered on zero, we report a match, not a gain"). GOOD.

POTENTIAL FINDINGS (to rank):
- **[MAJOR? mechanism over-generalization]** §5.2.4 "A balancer therefore has no conflict to
  resolve" generalizes from a DIRECTIONAL (cosine) measurement to ALL balancers. Elich et al.
  (2311.04698 — in my canon, NOT cited anywhere) show angular conflict is not the whole story;
  magnitude/scale differences dominate and are what GradNorm/uncertainty-weighting address, and
  the fixed 0.75/0.25 weighting IS itself a static scale intervention. The cosine cleanly
  explains the PCGrad-family null (PCGrad acts on direction), but magnitude-based balancers
  target a different axis the cosine does not measure. The EMPIRICAL "none improved" backs the
  conclusion regardless, so this is "tighten the mechanism sentence + acknowledge the scale axis
  (and that the fixed weight handles it) + cite Elich", not "claim is wrong."
- **[CHECK / possible MAJOR confound — Q9 loss-shaping parity]** §5.method-model: joint model
  uses "plain unweighted cross-entropy" (class-weighting "lowered both region accuracy and
  category macro-F1"). But Ch.2 §2.4 states "The training pipeline counters the same imbalance
  with class-weighted cross-entropy." CONTRADICTION to resolve: do the DEDICATED single-task
  models use class-weighted CE while the joint uses unweighted? If loss-shaping differs across
  MTL vs STL arms, the transfer comparison is confounded (Q9). MUST verify against Ch.3/Ch.4 and
  the code. Flag concordance (Ch.2 vs Ch.5) either way.
- **[MINOR — balancer tuning budget, Q1]** "none of the balancers we tried improved" — budget
  for the balancers not stated (were they tuned or run at defaults?). Fixed weight was tuned
  once. Asymmetry favors the null but a pro-balancer examiner (Kurin) would ask. Since the
  finding is null-aligned, low risk; state the balancer sweep budget.
- **[MINOR — freeze control scope]** trunk attribution "reported as a finding, not a hypothesis"
  but freeze control run on 3/6 datasets (AL/AZ/FL); category gain claimed on all six. Scoped in
  the sentence (names the 3), not hidden; note generalization to Ist/TX/CA untested.
- **[MINOR — region-side mechanism asymmetry, Q7/L5]** category gain has the freeze control
  (region does not teach category); the REGION win (4/6) has no symmetric control. Text avoids
  claiming "category teaches region" (credits private spatial path + trunk semantic context),
  so no silent reverse-direction claim — but the region gain's source is less dissected than the
  category gain's. Per-direction affinity evidence is one-directional.
- **[CHECK — Nash-MTL solver bug carryover]** Ch.3 has the Nash-MTL solver-bug containment
  (collapsed to [1,1]). Ch.5's "Nash-MTL didn't improve" — did the MobiWac sweep use the fixed
  or buggy solver? If buggy, "balancers don't help" is partly confounded; but the cosine
  mechanism is solver-independent so the conclusion survives. Verify + note.
- **[MINOR framing]** "A reader used to MTL expects the harder task... to teach the easier one"
  is a loose characterization of MTL expectations (standard expectation is shared-representation
  regularization, not specifically harder->easier). Motivates the freeze control fine; light nit.

HANDOFFS (out of scope): n=4 seeds for paired t (persona 09); dev-seed contamination Q10
(persona 09); leak-audit prose (persona 09); novelty "first fine-grained region as end target"
(persona 11).

### Ch.3 (CBIC null) — working notes
- Preface: time-capsule done well. "conclusions of the time, for the configuration... with a place-level
  embedding and hard parameter sharing, MTL did not consistently improve on the dedicated single-task
  models. Ch.4/5 revise... The chapter's preference for the Nash-MTL optimizer is likewise a conclusion
  of the time, weakened by a later finding about the optimizer implementation." NASH-MTL CONTAINMENT
  PRESENT (NORTH_STAR §4). GOOD.
- CBIC TASKS (confirmed, line 34-35): (1) POI Category Classification [STATIC], (2) Next-POI Prediction =
  "Predicting the CATEGORY of the next POI". => CBIC pair = {static category classification, next-category}.
  NO next-region task anywhere in Ch.3.
- Nash-MTL body claim (§3.4, "consistently yielded a better overall performance... lower combined
  multi-task loss"): reproduced published claim; contained by preface. Preface caveat is vague (does not
  say the finding was solver collapse to [1,1]) but NORTH_STAR §4 only requires "may note" -> acceptable.
  MINOR: could be more specific.
- Errata (b) wall-time fixed ("about 2.3 times", was "almost four times"); errata (c) MFLOPs fixed
  ("table does not show a higher cost"). GOOD.
- INTERNAL TENSION (reproduced): "Rationale for Hard Parameter Sharing / Computational Efficiency /
  edge devices / Jetson" oversells efficiency that the chapter's own convergence result (MTL 2.3x wall
  time) refutes; chapter self-corrects in §Convergence. MINOR (in original). Ch.1 must NOT inherit
  "MTL is efficient" (F3 guard) — check Ch.1.
- Negative transfer: CBIC data = "largely comparable, within std, no consistent advantage" +
  HYPOTHESIZES "Subtle Negative Transfer" (hedged, "We hypothesize"). Honest. It does NOT cleanly
  "observe negative transfer (sharing hurt one task)".

### Ch.4 (CoUrb) — working notes
- CoUrb TASKS (confirmed, lines 24-25): (1) POI Category Classification [static], (2) Next-POI Prediction
  = next-category. NO region task. => neither CBIC nor CoUrb studied next-region.
- Preface: Item-6 floor PRESENT ("isolates the representation effect with MTLNet as its only baseline;
  does not revisit the MTL-vs-single-task question, which Ch.5 reopens"). Sample-stratified split
  disclosed as weaker. GOOD.
- CoUrb is a within-MTL representation ablation (MTLNet vs ST-MTLNet, all MTL). No MTL-vs-STL claim.
  Preface claim accurate.
- §4 mtlnet-recap: recaps CBIC as "performed ON PAR with the dedicated single-task models at a higher
  training cost." <-- CAREFUL, CORRECT recap of the null. Contrast with Ch.5's "negative transfer
  (sharing hurt one task)". DISSERTATION CONTAINS BOTH characterizations of the SAME CBIC result =>
  internal inconsistency (feeds the BLOCKER below).
- CAPACITY CONFOUND DISCLOSURE (§4 embedding-integration): "difference in input dimensionality may
  influence part of the observed gains... an additional experimental control equalizing the
  dimensionality... would allow validating... not only from the increase in input dimensionality."
  EXCELLENT capacity-confound acknowledgment (192-d vs 64-d). Credibility signal. Lens 4.
- Nash-MTL used (inherited), no superiority claim -> solver-bug caveat absent but LOW risk (Nash is a
  constant across baseline+variants; does not threaten the representation conclusion). MINOR/context.
- Win-count numbers are the AUDITED set (15/21 + 1 tie; +20.2..22.0 pp). Errata applied. GOOD.

### *** CROSS-CHAPTER BLOCKER (candidate top finding): Ch.5 misattributes next-region to CBIC ***
Ch.5 twice claims prior work (silva2025mtlnet = CBIC) studied next-category + next-region and observed
negative transfer. CBIC (Ch.3) and CoUrb (Ch.4) BOTH study {static category classification, next-category};
NEITHER has a region task. MobiWac (Ch.5) is the FIRST to add next-region.
- Ch.5 L44 (§5.1 intro): "Prior work observed exactly this [compromise, helping one while hurting the
  other] for next-category and next-region~\cite{silva2025mtlnet}". FALSE: CBIC had no next-region task.
- Ch.5 L140 (§5.2.3): "Our earlier work~\cite{silva2025mtlnet} established this two-task setup [next-cat +
  next-region] and observed negative transfer (sharing hurt one task)". FALSE: CBIC did not establish the
  next-region setup, and reported parity (not a clean "sharing hurt").
- Ch.5 §5.2.1 recap "the first joint model for this task pair" reinforces the conflation (softer).
VIOLATIONS: (1) NORTH_STAR §6 signed-off addition (a): "the pair evolved... named plainly, NEVER narrated
as one experiment on a constant pair." (2) Factual: CBIC has no region task -> contradicts Ch.3's own task
definitions (concordance failure the dissertation makes MORE visible by placing Ch.3 before Ch.5).
(3) Amplifies CBIC's hedged null ("on par", per Ch.4) into factual "negative transfer (sharing hurt one
task)" -> also contradicts Ch.4's careful recap. Examiner kill-shot: "Ch.3 has no region task; how did it
observe negative transfer on next-region?" SEVERITY: BLOCKER.
Suggested direction (author, not applied): in Ch.5 L44/L140, attribute negative transfer to CBIC's ACTUAL
pair (static category classification + next-category) OR to caruana-style MTL generally, and state the
task pair evolved to next-category+next-region in this chapter. Align the CBIC characterization with Ch.4's
"on par" (or add the measured basis if "sharing hurt one task" is to stay).

---

## `11_poi_mobility_expert_report.md`

# Review v1 — Persona 11 · POI / mobility expert

**Reviewer:** next-location / POI-recommendation domain expert (critique-canon prior: Dacrema 2019, Sánchez & Bellogín 2022, POI Pitfalls 2025).
**Scope:** Ch.2 (fundamentals), Ch.3–5, and POI/mobility claims in Ch.1/6.
**Build under review:** `articles/dissertacao/src/` — `main_defense.pdf` (87pp), chapter .tex sources.
**Status:** COMPLETE.

---

# ============ FINAL REPORT (output contract) ============

## Overall verdict: **SOUND-WITH-CORRECTIONS**

The POI/mobility science is sound and, in places, exemplary. Chapter 5 is a model of honest
protocol disclosure that most published next-location papers do not reach: the
overlap-cannot-leak argument is stated explicitly, the A4 transductivity audit travels with its
scope and its unseen-places residual, the per-fold region-transition prior carries the historical
13–27 pp inflation as a cautionary record, every external baseline has a provenance sentence with
its asymmetries disclosed at the point of comparison, the result verbs are bound to their tests,
and Istanbul is framed as external validity for the *gain over the ceiling*, not for absolute
Acc@10. Those are real credibility signals and the author should not touch them.

The verdict is not "sound" because one BLOCKER and a cluster of MAJOR items stand between the
current build and a defense. The BLOCKER is a build/interpretability defect (Ch.3 renders raw
`[VERIFY: recompute…]` placeholders in place of its only dataset statistics). The MAJORs are
text-level disclosure and consistency corrections, not failures of the underlying experiments:
a self-contradiction over the 93% predictability ceiling, an unstated split axis in Ch.3 that
breaks the arc's protocol-strengthening story, a data-vintage limitation that misdescribes the
Ch.5 data by the repo's own measurement, unreconciled cross-chapter dataset statistics, and two
missing-disclosure items the field's own critique canon demands (revisitation intuition;
per-user vs per-sample averaging). All are fixable in the text.

## Top 3 findings

1. **[BLOCKER] Ch.3 dataset statistics render as raw `[VERIFY: recompute per ERRATA.md]`
   placeholders in the compiled defense PDF (p.35).** A results chapter presents per-category F1
   tables with no users/POIs/check-ins count at all, and the scaffolding text is visible.
2. **[MAJOR] Ch.2 §2.1 presents Song et al.'s 93% predictability as "the ceiling … against which
   any predictive model should be read," which §2.4 explicitly contradicts** ("it is not … a
   ceiling on … category macro-F1 or … region ranking"). The §2.1 framing is also domain-wrong:
   the 93% bound is for next-location at coarse spatial resolution, not for 7-class category F1
   or census-tract ranking.
3. **[MAJOR] Ch.3 never states its cross-validation split axis (user- vs sample-disjoint).** The
   arc's honesty story is that the protocol strengthens across chapters; Ch.4 discloses its
   weaker sample-stratified split, but Ch.3 is silent, and no CBIC-era code exists in the repo to
   verify it. A reader cannot tell whether Ch.3's null result rests on a leakage-prone split.

---

## Ranked findings (quote + location + severity + suggested direction)

### BLOCKER

**B1 · Ch.3 dataset statistics are unfilled placeholders in the built PDF.** (Lens 9 —
reproducibility; also a build defect.)
- *Quote (main_defense.pdf p.35, from `chapters/3_cbic.tex` §5.1):* "This subset comprises a
  total of [$N_{\text{users}}$; VERIFY: recompute per ERRATA.md] users, [$N_{\text{poi}}$; VERIFY:
  recompute per ERRATA.md] unique Points-of-Interest (POIs), and [$N_{\text{checkins}}$; VERIFY:
  recompute per ERRATA.md] check-ins."
- *Why it matters:* Ch.3 is a results chapter whose Florida F1 tables cannot be interpreted
  without the corpus size, and the raw VERIFY scaffolding in a defense build is a kill-shot at
  the banca. Known and catalogued (CBIC `ERRATA.md` non-citation #1; NORTH_STAR §4).
- *Direction:* Execute the sanctioned recompute (repo-committed script over the CBIC-era Florida
  Gowalla pipeline, <5-visit users dropped), author-approve, insert. CoUrb's published FL row is
  a cross-check only, not a source. Until then the chapter is not defense-ready.

### MAJOR

**M1 · The 93% predictability figure is used as a universal ceiling in §2.1 and disowned in
§2.4.** (Lens 8 — metrics/ceilings; internal contradiction.)
- *Quote (§2.1, `2_fundamentals.tex`):* "a potential predictability of about 93\% on where an
  individual goes next. That ceiling is the reference point against which any predictive model
  should be read."
- *Contradicting quote (§2.4):* "it is not, however, a ceiling on seven-class category macro-F1
  or on region ranking, which are different label spaces."
- *Why it matters:* Song et al.'s Π_max is a next-location bound at cell/antenna resolution; it
  does not bound 7-class category macro-F1 or census-tract Acc@10 — the dissertation's actual
  targets. §2.1 anchors the reader on an inapplicable ceiling and then §2.4 removes it. Ch.1 §1.1
  uses the same number correctly ("next location"), so §2.1 is the lone offender.
- *Direction:* Harmonize §2.1 down to §2.4's already-correct scoping — present 93% as the
  next-location predictability bound that frames why mobility is learnable, and name the dedicated
  single-task model as the operative ceiling for the two tasks studied. The fix language already
  exists in §2.4.

**M2 · Ch.3's split axis is unstated; the arc's protocol-strengthening story requires it.** (Lens
1 — split legitimacy, the #1 lens.)
- *Quote (§5.1, `3_cbic.tex`):* "all experiments were conducted using a 5-fold cross-validation
  methodology." (No user-vs-sample axis anywhere in the chapter.)
- *Why it matters:* Ch.4's preface discloses its split is "by sample rather than by user, a
  weaker protocol"; Ch.5 states user-disjoint with the leakage argument. Ch.3 has no counterpart
  sentence. The GLOSSARY itself flags "Ch.3's split … verify from the CBIC codebase before
  asserting it in prose," and no CBIC-era code is committed (the `articles/CBIC___MTL/` folder is
  .tex/.bib only). The CoUrb codebase (same pipeline family, firsthand-verified in NORTH_STAR §4:
  plain `StratifiedKFold`, userid dropped) is sample-stratified, so the likely truth is that Ch.3
  is *also* not user-disjoint — precisely the leakage-sensitive fact the reader is left to assume.
- *Direction:* Add one preface/methods sentence stating Ch.3's split axis honestly (if
  sample-stratified like CoUrb, say so — it strengthens the arc; if it cannot be verified from a
  surviving artifact, state that it followed the same pipeline as Ch.4 and mark the residual). Do
  not let silence imply user-disjoint.

**M3 · The data-vintage limitation misdescribes the Ch.5 data by the repo's own measurement.**
(Lens 6 — staleness/representativeness.)
- *Quote (Ch.6 limitation 1):* "come from Gowalla check-ins collected in 2009 and 2010."
- *Repo provenance (author's hidden comment, `5_mobiwac.tex` §setup-data):* "Date range MEASURED
  on the parquet 2026-07-09: 2009-01-21 .. 2011-08-16 -> 'collected 2009 to 2011'. The
  SNAP/cho2011 dump (Feb 2009-Oct 2010) is NOT the data source."
- *Why it matters:* Vintage is a core credibility lever (the field's own critique says
  decade-old single-source results are anecdotes). By the author's own measurement the Ch.5
  five-state data extends into Aug 2011, so the global limitation understates the range of the
  data actually used in the resolution chapter. Ch.4 cites "February 2009 and October 2010" for a
  *different* source (liu2014/SNAP), compounding the inconsistency.
- *Direction:* State the measured range for the data each chapter uses (Ch.5: 2009–2011 figshare
  dump; Ch.4: its own source range) and make Ch.6's limitation cover both correctly. Reconcile
  with the number auditor (06).

**M4 · Same states carry different dataset statistics across Ch.4 and Ch.5, never reconciled.**
(Lens 6/9 — representativeness + reproducibility.)
- *Quote (Ch.4 Table `tab:courb:dataset`):* Florida "990,518 / 65,009 / 20,301"; California
  "2,535,573 / 148,314 / 36,106"; Texas "3,355,419 / 135,570 / 37,522."
- *Quote (Ch.5 Table `tab:mobiwac:datasets`):* FL "1,407,034 / 76,544 / 21,052"; CA "3,171,380 /
  169,145 / 37,090"; TX "4,089,892 / 160,938 / 38,644."
- *Why it matters:* Both are legitimate in their own chapter (different Gowalla source, min-visit
  filter 5 vs 10, vintage, and 3 vs 5 states — confirmed as-published in NORTH_STAR §4), but a
  banca member reading both chapters sees Florida as 990k *and* 1.4M with no explanation, which
  reads as an error. The frame never states that the two studies use different Gowalla
  extractions.
- *Direction:* One frame sentence (Ch.2 §2.4 or the Ch.4/Ch.5 prefaces) noting that Ch.4 and Ch.5
  draw on different Gowalla releases and filtering thresholds, so per-state counts are not
  comparable across the two chapters.

**M5 · No revisitation/repeat intuition anywhere; the trivial "predict last region/category"
anchor is absent.** (Lens 4 — floors & popularity bias; POI Pitfalls Pitfall 13; attack Q5.)
- *Evidence of absence:* grep across all six chapters for revisit/repeat/persistence/return
  yields only the Song/Cho *background* framing in §2.1 ("return to a small set of places");
  no measured repeat rate, and no persistence or per-user most-frequent baseline in any results
  table.
- *Why it matters:* In LBSN next-location, much of any Acc@K number is carried by revisitation.
  The first-order Markov region floor is high (51–72 Acc@10, Ch.5), which itself signals heavy
  revisitation, but the reader is never told what fraction of correct predictions are simply
  repeats, and there is no persistence baseline (predict the current region/category). Without it,
  a skeptic cannot separate "the model learned mobility" from "the data is repetitive."
- *Direction:* Add a persistence / most-frequent-per-user floor to the region results (or its
  prose) and one sentence giving the repeat-vs-explore split for the datasets. If revisitation is
  high, say so and frame the gain over the Markov floor as the non-trivial part.

**M6 · The metric averaging axis (per-visit vs per-user) is never stated, and per-user length skew
is extreme with no activity cap.** (Lens 8 — metric conventions; attack Q9/Q11.)
- *Quote (Ch.5 §setup-metrics):* "the fraction of test visits whose true region appears among the
  model's ten highest-scoring guesses" — i.e. per-visit (per-window) averaging.
- *Quote (Ch.5 Table 1):* max per-user length "42,300" (TX), "16,679" (FL), "14,855" (CA) against
  average length "105.8 / 66.8 / 85.5."
- *Why it matters:* With stride-1 overlapping windows and per-visit averaging, a single
  42,300-visit account contributes ~42k windows and dominates the reported mean; there is no
  per-user-averaged figure and no maximum-activity cap disclosed (only min ≥10 visits). Per-visit
  scoring is field-standard, so this is a disclosure gap rather than a methodological error, but a
  banca statistician will ask whether the headline Acc@10 reflects a typical user or a few
  hyperactive (possibly non-human) accounts. The tiny cross-seed sds show the estimate is *stable*,
  not that it is *user-representative*.
- *Direction:* State the averaging axis explicitly (per-check-in, standard in the field); note
  whether any upper activity bound was applied and, if a 42k-visit account is a real user; ideally
  add one per-user-macro-averaged robustness number so the reader knows power users do not carry
  the result.

**M7 · The transductivity audit covers only AL/AZ/FL; the three largest corpora (CA/TX/Istanbul)
are unaudited.** (Lens 3 — transductive-artifact leakage; attack Q3.)
- *Quote (Ch.5 §setup-windows):* "at Alabama, Arizona, and Florida … This measurement covers the
  visits whose places appear in training (67 to 87 percent)."
- *Why it matters:* The A4 numbers are faithful (verified against `A4_RESULTS.md`), and the
  in-coverage caveat and unseen-places residual are stated honestly. But the whole-corpus
  representation is trained once on all six datasets, and the audit's null is measured only on the
  three smallest US states. CA (8,501 regions, 3.2M check-ins), TX (6,553 / 4.1M) and Istanbul
  carry the most opportunity for transductive information flow and are exactly where the largest
  region gains are claimed (+2.10 TX, +2.19 CA). The text does not flag that the audit's
  reassurance does not extend to the cells doing the heaviest lifting.
- *Direction:* Add one sentence scoping the audit to AL/AZ/FL and naming CA/TX/Istanbul as
  unaudited (the repo already lists this as author TODO in a hidden comment); or run the audit
  there before the banca. Also note (from `A4_RESULTS.md`, not in the text) that the audit is
  non-deterministic — a re-run gave category +0.88 pp vs the committed +0.29 — so "at most a third
  of a point" is one draw, not a stable bound. → coordinate with stats/leakage skeptic (09).

### MINOR

**m1 · Cross-convention number slip: Ch.6 quotes 64.54 for the AL joint category cell that Ch.5
Table 3 reports as 64.51.** (Concordance; → number auditor 06.)
- *Quote (Ch.6 §6.2):* "56.82 for the dedicated model … and 64.54 for the joint model." *Ch.5
  Table `tab:mobiwac:results`:* AL Joint "64.51±0.09."
- *Why it matters:* `JOINT_BEST_RESULTS.md` shows 64.54 = diag-best, 64.51 = joint-best(deploy).
  Ch.5 reports the joint-best lane; Ch.6 imports the diag-best value for the same cell. Within one
  sd, but the same quantity should carry one number across chapters.
- *Direction:* Use the joint-best value (64.51) in Ch.6 to match Ch.5's reported convention.

**m2 · "Next-POI Prediction" persists 17× in Ch.3 and 16× in Ch.4 with no in-chapter bridge to
the canonical "next category."** (Lens 7 / attack Q12 — three-task blur.)
- *Quote (Ch.4 §related):* "HMT-GRN combines Next-POI Prediction and prediction of its geographic
  region." Both chapters *define* the term in-body ("predict the category of the next POI"), and
  Ch.1 §1.3 bridges it narratively, but neither preface says "this chapter's 'Next-POI Prediction'
  is the canonical next-category task."
- *Why it matters:* The label reads as next-*place* to a POI examiner scanning tables and
  headings, and banca members read reproduced chapters standalone. The design (reproduced chapters
  keep the paper's terms, the frame bridges) makes this defensible, so it is minor, not major.
- *Direction:* One sentence in each of the Ch.3/Ch.4 prefaces mapping "Next-POI Prediction" to the
  dissertation's "next category" would close the residual blur risk cheaply.

**m3 · Ch.2 §2.4 forward-promises MRR, which Ch.5 never reports.** (Metric convention.)
- *Quote (§2.4):* "mean reciprocal rank accompanies it where the joint comparison needs a
  rank-sensitive figure." Ch.5 reports Acc@10 only; MRR appears in no results table.
- *Direction:* Either drop the MRR promise from §2.4 or report MRR in Ch.5; an unfulfilled metric
  promise invites the question at the defense.

**m4 · Query-time information symmetry is never stated.** (Lens 7 — attack Q7, closing clause.)
- *Observation:* No chapter states whether the target visit's timestamp is available to the model
  at prediction time (it plausibly is, since category/region are predicted for a known next
  time-slot, but the reader is not told, and it affects whether the task is "predict the next
  visit" or "predict the visit at time t+1").
- *Direction:* One sentence in Ch.5's problem statement clarifying what is known about the target
  at query time.

**m5 · Istanbul vintage is unstated while Gowalla vintage is a named limitation.** (Lens 6.)
- *Observation:* Ch.6 limitation 5 caps non-US evidence at "a single city, Istanbul," but the
  Istanbul (Massive-STEPS) collection date is never given, while Gowalla's is a headline
  limitation. For symmetry and honesty the reader should know the Istanbul vintage too.
- *Direction:* State the Massive-STEPS/Istanbul collection period where the vintage limitation is
  discussed.

---

## What holds / what reads well (do NOT touch)

- **Ch.5 leakage hygiene is exemplary.** The overlap-cannot-leak sentence ("a test user's visits
  never appear in training"), the A4 audit with its 67–87% in-coverage caveat and unseen-places
  residual, the per-fold region-transition prior with the 13–27 pp historical-inflation record,
  and "our joint and dedicated models do not use this prior" are exactly the disclosures the
  field's critique canon asks for. Verified faithful to `A4_RESULTS.md`.
- **Baseline provenance is disclosed at the point of comparison** — POI-RGNN re-implemented,
  HMT-GRN region-native and explicitly "not a reproduction of the complete published system,"
  STAN partial folds (TX 4/5, CA 2/5) and ReHDM single-seed/own-protocol all footnoted. This is
  the fairness discipline most next-POI papers lack.
- **Verbs are bound to tests throughout**: "outperforms" only with the paired superiority test,
  "matches" only with TOST within a two-point margin, AZ never upgraded from a match to a win, and
  the region scaling read honestly as a trend ("we read the trend across the points rather than as
  a precise law").
- **Istanbul external validity is framed correctly**: "The comparable quantity is the gain over
  the ceiling, not the absolute Acc@10." This is the right way to use a non-US dataset and should
  be preserved verbatim.
- **The three tasks are kept formally distinct** and "we do not predict the exact next place" is
  stated early (Ch.1 §1.1, Ch.2 §2.1, Ch.5 problem). The label-cardinality table (520–8,501
  regions vs 7 categories) is present and no cross-cardinality Acc@K comparison is implied.
- **Ch.4's split-protocol disclosure** ("by sample rather than by user, a weaker protocol") is the
  honesty device the arc needs; keep it exactly as written (it is what M2 asks Ch.3 to match).
- **The floors are present and protocol-matched**: majority-class ~7% macro-F1 (internally
  consistent with Food ~33%), and the first-order Markov region floor (51–72 Acc@10) computed
  "under our windows and folds."

## Unstated defenses (facts the repo holds but the text does not carry)

- **A4 non-determinism.** `A4_RESULTS.md` records the audit is non-deterministic (a re-run gave
  cat +0.88 pp vs the committed +0.29) and that the category axis is a POI-level proxy on the
  in-coverage subset. Ch.5 states the proxy caveat but not the run-variance; the "at most a third
  of a point" phrasing implies a stable bound the repo does not claim.
- **CA/TX transductivity direction.** The repo TODO ("extend to CA/TX/Istanbul … non-blocking; the
  gate is on null at AL+AZ+FL") shows the unaudited-large-corpora gap is known; the text could name
  it as scoped future work rather than leave it silent (M7).
- **Cross-chapter dataset provenance.** NORTH_STAR §4 documents that Ch.4 (SNAP/liu2014, min-5) and
  Ch.5 (figshare CC0 dump, min-10) use different Gowalla releases — the fact that reconciles M4 —
  but no chapter tells the reader this.
- **AZ ceiling sensitivity.** A hidden Ch.5 comment records the AZ dedicated category ceiling
  (56.43) carries a pending 2-seed top-up that could raise it to ~57.0 (shrinking Δcat to ~+8.7);
  disclosed on-request per author policy, not in the text. Rule-clean per the pre-registered
  estimator, so not a finding — noted so the author knows the caveat exists if a reviewer probes.

## Out-of-scope handoffs (one line each; not my lens)

- **Number auditor (06):** the 64.54/64.51 convention slip (m1); the Gowalla date range
  reconciliation (M3); confirm the audited CoUrb win-counts/pp-gains (15/21 + 1 tie; +20.2…+22.0)
  match `slides/judge_feedback.md` — Ch.4 uses the audited numbers, which is correct.
- **Citation auditor (05):** CBIC `ERRATA.md` #1 marks `capanema2023poirgnn` (POI-RGNN) as
  "[VERIFY at adaptation] — the exact record could not be resolved via OpenAlex this session." That
  reference is load-bearing twice — the sole support for "next category as an end target" in Ch.2
  §2.1 and a Ch.5 category baseline — so its resolution matters for domain claims; confirm the
  record is opened before the bib freezes.
- **Stats/leakage skeptic (09):** A4 run-variance and the POI-proxy scope (M7 tail); the n=4
  per-dataset pairing for TOST/superiority power; the per-visit averaging power question (M6).
- **Style/concordance (03/04):** the em-dash-free / canonical-name checks are not my lens; I did
  not audit them.
- **Translation fidelity (08):** Ch.4 is a PT→EN reproduction; I reviewed its science, not its
  translation faithfulness.

## Open questions only the author can answer

1. Is the CBIC-era Florida split user-disjoint or sample-stratified, and does any surviving
   artifact establish it? (Decides the M2 wording — disclosure vs residual flag.)
2. Is the 42,300-visit Texas account a real user, and was any maximum-activity cap applied at any
   stage? (Decides whether M6 needs a data-hygiene sentence in addition to the averaging-axis
   disclosure.)
3. Will CA/TX/Istanbul get a transductivity audit before the banca, or should M7 be written as a
   scoped limitation + future-work item?
4. Should the vintage limitation state the measured 2009–2011 range for the Ch.5 figshare data
   (M3), given the published articles say 2009–2010?


**Read (session start):** persona file 11; reviewers/README common protocol; CLAUDE.md; NORTH_STAR §1-§6; GLOSSARY.md. (Persona "read first" order followed.)

---

## Working notes (raw findings as I go — reorganized into the output contract at the end)

<!-- appended below as review proceeds -->

### RAW NOTES BY LENS (pre-verification)

**Chapters read in full:** 2_fundamentals (551 l), 5_mobiwac (627 l), 4_courb (351 l), 3_cbic (365 l),
1_introduction (249 l), 6_conclusion (159 l). Build: main_defense.pdf 87pp.

**Lens 1 (split legitimacy):**
- Ch.5 GOOD: "We split by user with stratified five-fold cross-validation, so all of a user's windows fall in the same fold and overlap cannot leak: a test user's visits never appear in training." Overlap-cannot-leak argument explicit.
- Ch.4 GOOD (disclosed): preface + results both say sample-stratified, weaker than Ch.5, userid may span train/val.
- Ch.3 GAP: §5.1 "all experiments ... using a 5-fold cross-validation methodology" — split AXIS NOT STATED (user vs sample). GLOSSARY flags "verify from CBIC codebase before asserting". Arc honesty story is protocol-strengthening → CBIC's axis must be named. MAJOR.

**Lens 2 (window/seq leakage):** Ch.5 EXEMPLARY — min-len 10, stride-1, overlap, padding, end-of-history dedup all disclosed + overlap-cannot-leak. Ch.3/4 non-overlapping, min-len 5 (<5 dropped). Per-chapter disclosed. Note min-len differs 5 vs 10 across chapters (fine, each states own).

**Lens 3 (transductive):** Ch.5 §setup-windows "Integrity" para EXEMPLARY: label-free + A4 audit (region −0.33..+0.01, category 0.00..+0.29 at AL/AZ/FL) + in-coverage caveat (67–87% places seen) + unseen-places residual + per-fold transition prior w/ 13–27pp historical inflation record + prior only in HMT-GRN. BUT audit only AL/AZ/FL; CA/TX/Istanbul (largest corpora = most leak opportunity) UNAUDITED. Honest scope stated, residual on largest sets not flagged. MAJOR-soft.

**Lens 4 (floors + popularity):**
- Majority-class floor STATED (~7% macro-F1). Markov-K (cat) + first-order Markov region floor STATED, protocol-matched ("our windows and folds"), region floor 51–72 Acc@10. GOOD.
- MISSING: persistence (predict last region/category) + per-user most-frequent baseline. No repeat-vs-explore statistic anywhere. High Markov region floor (51–72) itself signals revisitation carries much of the number, but reader gets no repeat-rate intuition. Persona attack Q5 + Pitfall 13. MAJOR.

**Lens 5 (baseline fairness):** Ch.5 EXEMPLARY provenance — POI-RGNN (re-impl from published arch/hparams), HMT-GRN (region-native, our folds, keep MT skeleton + per-fold prior, drop beam/graph, "not a reproduction of the complete published system"), STAN (re-impl, own embeddings/seq, partial folds TX 4/5 CA 2/5 disclosed in footnote), ReHDM (own protocol, single-seed TX/CA disclosed). All asymmetries disclosed at point of comparison. GOOD.
- MINOR: conclusion "at least 4 Acc@10 over strongest region reference" — tightest point is Joint 69.70 vs ReHDM 65.38 at AL = +4.32, but ReHDM is CROSS-PROTOCOL. Disclosed as "own protocol" but aggregate claim leans on it.

**Lens 6 (staleness):**
- Gowalla vintage: Ch.6 lim1 "2009 and 2010"; Ch.4 "February 2009 and October 2010". BUT Ch.5 hidden comment: figshare dump ETL consumes spans "2009-01-21 .. 2011-08-16" measured on parquet; "SNAP/cho2011 (Feb 2009-Oct 2010) is NOT the data source". So Ch.5 data runs into Aug 2011 → stated 2009–2010 limitation MISDESCRIBES Ch.5 data. MAJOR (verify + reconcile). Cross-ref number auditor.
- Istanbul external validity FRAMED CORRECTLY: "The comparable quantity is the gain over the ceiling, not the absolute Acc@10". EXCELLENT credibility signal.
- Istanbul vintage unstated (staleness lim = Gowalla only). MINOR.

**Lens 6b / Lens 9 (cross-chapter dataset consistency):** SAME STATE, DIFFERENT STATS across chapters, unreconciled:
  FL: Ch.4 990,518 ck / 65,009 POI / 20,301 users  vs  Ch.5 1,407,034 / 76,544 / 21,052.
  CA: Ch.4 2,535,573 / 148,314 / 36,106  vs  Ch.5 3,171,380 / 169,145 / 37,090.
  TX: Ch.4 3,355,419 / 135,570 / 37,522  vs  Ch.5 4,089,892 / 160,938 / 38,644.
  Cause: different Gowalla source (SNAP/liu2014 vs figshare), min-visits 5 vs 10, vintage, 3 vs 5 states. NOT reconciled in text; a reader/examiner sees FL=990k (Ch.4) vs 1.4M (Ch.5). MAJOR.

**Lens 7 (formulation comparability):**
- Three tasks kept distinct throughout; "do not predict exact next place" stated early (Ch.1 §1.1, Ch.2 §2.1, Ch.5 problem). GOOD.
- Label cardinality TABLED (Ch.5 Table 1 Regions 520–8,501; category=7). GOOD.
- Region construction (census tract/mahalle) justified ("neighborhood, not radio cell"; official units vs grid). GOOD.
- No cross-cardinality Acc@K comparison: external-validity section forbids it explicitly ("gain over ceiling, not absolute Acc@10"). GOOD.
- Co-equal region novelty claim scoped ("to our knowledge", fine-grained region vs auxiliary grid; DRRGNN + sun2025kgtb named/distinguished). GOOD.
- Query-time info symmetry: text SILENT on whether target timestamp is a model input. MINOR.

**Lens 8 (metrics):**
- macro-F1 for imbalanced category + majority floor beside: GOOD (Ch.5 + fund §2.4 "plain accuracy inflated by Food ~third").
- Acc@10, K=10 motivated operationally (10-region shortlist / anticipatory set). OOD counted as miss, DEFINED. GOOD.
- HMT-GRN scored on FRIENDLIER denominator (visits w/ region in training, >99%) vs joint counts OOD as miss — DISCLOSED w/ subset size (>99%). Acceptable.
- PER-SAMPLE (per-window) averaging ("fraction of test visits") + EXTREME per-user skew (Table 1 Max len up to 42,300 at TX; 16,679 FL; 14,855 CA; avg 105.8 TX). Overlapping stride-1 windows weight users by visit count → power users dominate the reported mean. Undisclosed; no per-user-averaged number. Also 42,300-visit "user" likely non-human/venue acct — was any activity cap applied? MAJOR.
- MRR: fund §2.4 introduces MRR ("accompanies Acc@10 where the joint comparison needs a rank-sensitive figure") but Ch.5 reports no MRR. MINOR (drop forward-ref or report it).

**Lens 9 (reproducibility):**
- Code+data URLs (Ch.5 GitHub+figshare; Ch.3/4 GitHub), seeds (4; n=20=4×5), configs "in released code". GOOD.
- BLOCKER: Ch.3 §5.1 dataset stats UNFILLED — literal "[$N_{users}$; VERIFY: recompute per ERRATA.md]" ×3 in rendered text. Results chapter with no N + visible VERIFY brackets. Uninterpretable + build defect.

**Frame (Ch.1/6):**
- Ch.1 §1.1 "93 percent" correctly scoped to "next location". Ch.2 §2.1 OVERGENERALIZES same 93% as "the reference point against which any predictive model should be read" / "ceiling" — contradicts §2.4's correct scoping ("not a ceiling on ... category macro-F1 or region ranking"). §2.1 anchors reader on a ceiling that does not apply to the dissertation's actual tasks. MAJOR (harmonize §2.1↔§2.4).
- Ch.1 arc verbs bound to tests. GOOD. Task-pair evolution named plainly. GOOD.
- Ch.6 §6.2 capacity-matched baseline (frame-level, disclosed as post-submission). Quotes joint AL category "64.54"; Ch.5 Table 3 = 64.51±0.09. Within 1sd but should be same quantity. MINOR (concordance; number auditor).
- Ch.6 CoUrb "20.2 to 22.0 pp" = audited numbers (not stale 76%/+20-24). GOOD. MobiWac "5.3 to 9.4" ≈ +5.33..+9.35. GOOD.

### NUMBERS TO VERIFY AGAINST SOURCES OF TRUTH (reproduce-first, README §10)
1. Ch.5 Table 3 joint/dedicated cells vs RESULTS_BOARD.md (spot: AL cat 64.51, the 64.54 in Ch.6).
2. A4 audit numbers (−0.33..+0.01 reg; 0.00..+0.29 cat) vs A4_RESULTS.md.
3. Gowalla date range 2009–2011 claim (Ch.5 hidden comment) — the vintage finding.
4. CoUrb dataset table (990,518 etc.) is as-published (cross-chapter inconsistency, not my typo).
5. CBIC placeholder truly unfilled in built PDF.

### VERIFICATION RESULTS (reproduce-first, done)
- **CBIC placeholder — CONFIRMED BLOCKER.** main_defense.pdf p.35 renders verbatim: "This subset comprises a
  total of [N_users; VERIFY: recompute per ERRATA.md] users, [N_poi; VERIFY: recompute per ERRATA.md] unique
  Points-of-Interest (POIs), and [N_checkins; VERIFY: recompute per ERRATA.md] check-ins." Raw VERIFY scaffolding
  visible in the compiled defense build. Ch.3 presents Florida F1 tables with NO dataset size stated.
- **A4 audit — VERIFIED FAITHFUL.** A4_RESULTS.md: AL reg −0.33/cat +0.29@66.8%; AZ reg +0.01/cat +0.27@71.9%;
  FL reg −0.12/cat +0.00@86.9%. Ch.5 text ("region −0.33 to +0.01; category 0.00 to +0.29"; "67 to 87 percent")
  matches exactly. Scope AL/AZ/FL-only confirmed; CA/TX/Istanbul unaudited (Ch.5 states this honestly).
  NOTE (domain, not a text error): A4_RESULTS carries a RUN-VARIANCE caveat NOT in the dissertation — the
  per-fold train-only substrate is non-deterministic, "~±0.5–0.6 pp on cat", and an AL re-run gave cat +0.88 pp
  vs the committed +0.29. So "at most a third of a point" is the single committed draw, not a stable bound; a
  re-run exceeded it. Also cat is a POI-level proxy on the in-coverage subset, which Ch.5 does state. → stats
  skeptic (09) territory; I flag it as an unstated caveat, low severity for my lens (direction/scope honest).
- **Ch.6 "64.54" vs Ch.5 Table 3 "64.51" (AL joint category) — CONFIRMED CROSS-CONVENTION SLIP.**
  JOINT_BEST_RESULTS.md: AL joint category diag-best=64.54, joint-best(deploy)=64.51. Ch.5 Table 3 reports the
  JOINT-BEST lane (64.51) per its own provenance comment; Ch.6 §6.2 capacity-baseline para quotes 64.54 (the
  diag-best value) as "the joint model" (and 56.16 vs "64.54 for the joint model"). Two conventions mixed across
  chapters for the SAME cell. Within 1 sd but should be one number. → number auditor (06); I flag as concordance.
- **Gowalla vintage — CONFIRMED TEXT INCONSISTENCY (author's own note).** Ch.5 hidden provenance comment
  (author-written): the figshare dump the Ch.5 ETL consumes was MEASURED on the parquet as 2009-01-21 .. 2011-08-16
  → intended phrasing "collected 2009 to 2011"; and explicitly "The SNAP/cho2011 dump (Feb 2009-Oct 2010) is NOT
  the data source." YET Ch.6 limitation 1 renders "collected in 2009 and 2010" and Ch.4 "February 2009 and October
  2010". By the author's own measurement the Ch.5 five-state data runs into Aug 2011, so the stated vintage
  limitation under-states the range for the data actually used in Ch.5. (Ch.4 uses a different source, may be
  2009–2010 correctly — but Ch.6's limitation is global and covers the Ch.5 datasets.) The vintage limitation is a
  core credibility lever (Lens 6); it currently misdescribes the Ch.5 data per the repo's own provenance. MAJOR.
- **Majority floor ~7% — internally consistent** (Food ~33% → macro-F1 of always-Food ≈ 7.1%). Not a finding.
- **Cross-chapter dataset stats — confirmed both as-published.** NORTH_STAR §4 confirms CoUrb FL row
  990,518/65,009/20,301 is the genuine published number; Ch.5 FL 1,407,034 is from the board. Both legitimate in
  their own chapter; the FRAME never reconciles that Ch.4 and Ch.5 use different Gowalla extractions/filters/vintage.

---

## `14_adversarial_advisor_report.md`

# 14 · Adversarial advisor — change-gate report (fix-loop run)

> Persona: the adversarial second signature (`reviewers/14_adversarial_advisor.md`).
> Two lenses on every item: **Lens 1 (the law)** — WRITING_LAW / GLOSSARY / AGENT_GUARDRAILS
> / NORTH_STAR decisions / settled author rulings; **Lens 2 (information loss)** — what a
> reader or examiner loses, and whether it is recoverable elsewhere.
> Verdicts: **APPROVE** / **APPROVE-WITH-EDIT** (exact corrected text supplied) / **VETO**
> (rule or unrecoverable loss named + legal alternative) / **NEEDS-AUTHOR** (surface a
> conflict; the author owns the law).
> Read-only. I gate; the applier applies. Written incrementally so a restart cannot lose it.

**Run scope (from the invocation):** the change-gate run for the fix loop. The proposed-edit
batch is (A) the MECHANICAL fixes already landed this session — recorded in `src/_gates/`
reports and the git `phase 6` commit (`49a67996`) — audited for whether any broke a rule or
lost a disclosure; and (B) the top recommended fixes still pending across the 15 landed persona
reports in `src/_review_v1/`, each ruled.

Built PDFs: `src/main_defense.pdf` (87pp), `src/main_final.pdf` (83pp). Sources:
`src/chapters/*.tex` + `src/0_main.tex`.

---

## GATE VERDICT (summary)

**Part A — the 6 mechanical fixes already LANDED (phase-6 commit `49a67996`): ALL 6 CERTIFIED.**
None broke a rule; none lost a disclosure. Re-derived firsthand: the D-1 margin fix moved the
bottom text margin from 1.52 cm (pre-fix, every full page) to a measured **1.92 cm minimum**
across all 64 full body pages (median 2.30 cm), page counts unchanged (87 / 83), 0 undefined
refs/cites in both logs, `check.sh` exits 0. Two residues that are NOT regressions are noted
under A.7 (30 benign `Overfull \vbox 14.5pt` warnings; the page-67 "only floats" layout warning
that the L4 pointer did not clear because the figure legitimately fills its own page).

**Part B — the top PENDING recommendations across the 15 persona reports: ruled below.**
2 items are **NEEDS-AUTHOR** (both pre-existing BLOCKERs: Ch.3 dataset placeholders; the Ch.5
CBIC misattribution, which is a claim-level departure from a paper still under review). 6 are
**APPROVE-WITH-EDIT** with exact text supplied (64.54→64.51 convention; Ch.2 `unlocks`; Ch.4
Gowalla mis-cite F-1; Ch.2 Song 93% scope; Ch.4 title `\:`; frame `percent` style). 1 is
**APPROVE-IN-PRINCIPLE + VETO-BLANKET** (the "at [dataset]" preposition campaign must not be
run mechanically — it collides with the verdict-scope law). 1 figure item is NEEDS-AUTHOR
(Portuguese labels in Figure 2, a regen not a text edit).

**Net size effect:** ≈ neutral. Every pending text fix is an in-place reword; the two landed
dedup edits slightly shortened. No page-budget risk (Fundamentals stays within its 8–12 pp;
document stable at 87/83).

**Interaction flags:** (I1) the pending 64.54→64.51 edit lands in the SAME Ch.6 paragraph the
landed C-1 idiom fix touched — apply without disturbing the C-1 wording; (I2) the A-1/A-2 dedup
pair did NOT jointly delete the weekday-lunch image (it survives once in Ch.1 L119-121, the
signed-off mechanism beat) — safe; (I3) the "at [dataset]" campaign and the region-verdict law
overlap — see V-1.

---

# PART A — the 6 LANDED mechanical fixes (audit for rule-break / disclosure-loss)

Source: git `49a67996` diff (chapters + `0_main.tex` + `check.sh`), each site read in context and
re-verified against the built PDFs.

## A.1 — D-1 layout fix (`0_main.tex`): re-derive the block under 1.5 spacing. **CERTIFIED.**

- **Lens 1 (law):** UFV_COMPLIANCE §7 mandates 3 cm / 2 cm margins AND 1.5 line spacing; the fix
  serves both. It sets `\OnehalfSpacing` before `\setul/lrmarginsandblock{3cm}{2cm}{*}` +
  `\checkandfixthelayout[fixed]`, so the block is fixed under the spacing the manual mandates
  rather than under single spacing. No rule broken; this is the corrective the D-1 finding asked
  for. Note: `\OnehalfSpacing` is now issued twice (`0_main.tex:35` in the fix block and `:144`
  in the body) — harmless (idempotent), but the applier may drop the `:144` duplicate for
  tidiness (NIT, not required).
- **Lens 2 (loss):** nothing lost. Re-measured firsthand on the current `main_defense.pdf` at
  200 dpi across ALL 64 full body pages: bottom margin **min 1.92 cm, median 2.30 cm, max 3.44
  cm**; 0 pages below 1.70 cm (pre-fix: 1.52 cm on every full page). Left 2.96–3.00 cm, right
  1.96–2.02 cm, top unchanged. Page counts **unchanged (87 / 83)** — the fix did not push content
  onto new pages. **1.92 cm is within measurement tolerance of the 2 cm nominal** (ink bounding
  box + last-baseline-to-edge, ±0.05 cm; the glyph descender sits a few pt above nominal). Verdict
  APPROVE. (If the author wants dead-on 2 cm, add ~1.5 mm `\textheight` trim, but this is now a
  NIT, no longer the MAJOR D-1 was.)

## A.2 — Ch.1 L76 dedup (A-1): paper-chapter phrase reworded out of the frame. **CERTIFIED.**

- Landed text: *"a single model to maintain, and a single forward pass that returns both
  predictions together, instead of two dedicated single-task models running side by side."*
- **Lens 1:** claim unchanged (one artifact, one forward pass, two predictions); canonical names
  intact ("dedicated single-task models"); no banned idiom introduced; carries a `[NEEDS
  SIGN-OFF]` comment naming the revert path. The L3 defect (frame echoing Ch.5's version-of-record
  wording) is removed and the paper chapter keeps its wording — correct direction (the paper is
  the record and cannot move). **Crucially, it respects the F3 guard (NORTH_STAR §6 beat 2): it
  does NOT promise lower compute cost** — "a single model to maintain" is operational, not a cost
  claim. Clean.
- **Lens 2:** no disclosure lost; the operational-simplicity point is fully preserved. APPROVE.

## A.3 — Ch.2 L502 dedup (A-2): "weekday lunch / Saturday night out" image de-duplicated. **CERTIFIED.**

- Landed text: *"A vector that stays the same across visits carries nothing about the visit being
  predicted, and the check-in level is the response to that limit."*
- **Lens 1:** states the same static-vector limitation without the image; no rule broken.
- **Lens 2 (the interaction that matters):** I verified the image is NOT orphaned — it survives
  once, in Ch.1 L119-121 (*"a representation that cannot tell a weekday lunch from a Saturday
  night out at the same place is working against both tasks at once"*), which is the **signed-off
  mechanism beat** (NORTH_STAR §6 Ch.1 beat 4(e)). So the A-1 and A-2 edits together did NOT
  delete both copies of a load-bearing image (the classic dedup trap this persona exists to
  catch). The hinge role of §2.5 is preserved. APPROVE.

## A.4 — Ch.5 L420 (B-1/L4): pointer sentence added for the restored embquality figure. **CERTIFIED.**

- Landed text: *"Figure~\ref{fig:mobiwac:embquality} shows the same separability contrast
  graphically."* placed inside the restored-block, above the float.
- **Lens 1:** resolves the L4 defect (a float must be referenced in prose); the new `\ref`
  compiles with **0 undefined references** (verified in both logs). The comment correctly binds
  the pointer's lifetime to the restored block ("leaves with it") so a later revert-to-submitted
  removes both together — good hygiene.
- **Lens 2:** adds a reference, loses nothing. Note the "Text page 67 contains only floats"
  warning PERSISTS (verified: page 67 is the figure on its own page). That warning is about
  page-breaking, not about the missing `\ref`; the fix correctly targeted the `\ref` defect. The
  residual warning is benign (a full-page figure). APPROVE. (D-2 in the style report predicted the
  warning would "fix itself"; it did not, because the figure legitimately fills the page — this is
  cosmetic, not a defect.)

## A.5 — Ch.6 L80 (C-1): "buys nothing"→"yields nothing"; "the win lives in"→"the gain resides in". **CERTIFIED.**

- **Lens 1:** removes two WRITING_LAW §4 idiom-law violations (money-metaphor "buys"; phrasal
  metaphor "the win lives in"; and "win" as a result noun brushing the §3 banned verdict-verb
  family). "yields" and "the gain resides in" are within the safe-verb register. Claim strength
  unchanged (parameter count alone recovers nothing; the effect is in the shared trunk). Correct.
- **Lens 2:** no meaning lost. APPROVE. **Interaction (I1):** the pending 64.54→64.51 fix (B.2
  below) lands in THIS SAME paragraph — the applier must change only the numeral and leave this
  C-1 wording intact.

## A.6 — Ch.6 L126 (C-1): "the size of the win"→"the size of the improvement". **CERTIFIED.**

- **Lens 1:** same idiom-law cleanup ("win" result-noun) inside limitation 6 (the task-pair
  confound concession, a signed-off addition NORTH_STAR §6 Ch.6). "improvement" is neutral and
  preserves the concession's hedged force ("a possible contributor to the size of the
  improvement"). No weakening of the confound disclosure — the whole limitation sentence is
  intact. APPROVE.
- **Lens 2:** the concession (no single ablation separates representation+topology from task-pair
  homogeneity) is fully preserved. Nothing lost.

## A.7 — `check.sh` lint hardening. **CERTIFIED.**

- **Lens 1:** three changes, all correct: (1) em-dash grep now uses an explicit UTF-8 byte
  sequence `\xe2\x80\x94` with a proper comment-line exclusion `^[^:]*:[0-9]*: *%` (the old
  `$'\u2014'` was shell-fragile and the old `^\s*%` filter missed `file:line:  %` comment
  form); (2) the banned-word check now excludes `apx_b_errata` (which legitimately QUOTES the
  published banned words in its wording-substitution table — a real exemption, not a loophole);
  (3) all filters use the tightened comment pattern. I RAN it: **exits 0**, all checks OK. The
  "Pareto/wins" line it prints is a non-failing review sweep; its two hits are Ch.3 published
  method text (MGDA/Nash-MTL "Pareto") and apx_b quoting the published "wins" text — both legal.
- **Lens 2:** the apx_b exemption does not hide anything — apx_b's function IS to quote the
  published defects; the banned words there are the evidence, not a violation. No disclosure
  suppressed. APPROVE.

### A — verdict: all 6 landed fixes hold. No rule broken, no disclosure lost, no interaction damage.

---
# PART B — top PENDING recommendations, gated

Each item: the source finding, my two-lens read, and the verdict. APPROVE-WITH-EDIT items carry
**exact final text**, ready to apply verbatim. Ordered by severity.

## B.1 — Ch.5 CBIC misattribution (MTL-expert BLOCKER Finding 1). **VERDICT: NEEDS-AUTHOR.**

**Re-derived firsthand (not echoed):** Ch.3 L37-38 lists CBIC's two tasks as *POI Category
Classification* (static) + *Next-POI Prediction* (= next category); **there is no region task in
Ch.3.** Ch.3 L358-360 **hypothesizes** "Subtle Negative Transfer" ("We hypothesize"), and L356
reports the result as *"did not consistently demonstrate superior performance"* — a parity null,
not an observed negative transfer. Yet:
- Ch.5 L44: *"Prior work observed exactly this for next-category and next-region~\cite{silva2025mtlnet}"*
  (the "this" = one task helped while the other is hurt).
- Ch.5 L140: *"Our earlier work~\cite{silva2025mtlnet} established this two-task setup and observed
  negative transfer (sharing hurt one task)"*.

Both are false on two counts (region task; "observed" vs "hypothesized"), and both self-contradict
Ch.5 L58 (*"the first work to treat fine-grained region as an end target"*) and the correct
framing stated four other places (Ch.1 §1.2, Ch.3, Ch.4 recap, Ch.6 limitation 6). This is a real
banca kill-shot and it **violates signed-off addition NORTH_STAR §6(a)** ("the task pair evolved
... named plainly, never narrated as one experiment on a constant pair").

**Why NEEDS-AUTHOR, not APPROVE-WITH-EDIT:** the offending sentences are **inherited verbatim from
the version of record** (`articles/[mobiwac]/src/sections/01_introduction.tex` L17 and
`02_related.tex` L48-49) — a paper still **submitted / under review**. Rewriting them is a
claim-level departure from a published-of-record source, which routes through the errata policy
(NORTH_STAR §4/§5.7 → ERRATA.md + Appendix B) AND touches the MobiWac claim whitelist
(AGENT_GUARDRAILS C1). Per my hard limits, I cannot silently rewrite a claim the author has not
ruled on; I surface it. **This is the batch's single most important item — it should not ship to
the advisor unresolved.**

**Proposed legal text (for the author to approve, NOT to apply unilaterally),** repairing both the
task-pair and the observed/hypothesized errors while staying inside what Ch.3 actually supports:

- L44 (repair): *"Sharing can converge to a compromise optimal for neither task, helping one while
  hurting the other~\cite{caruana1997multitask}. Our earlier work reported no consistent
  multi-task advantage for the paired category tasks and attributed it, in part, to this
  effect~\cite{silva2025mtlnet}; the useful question is where sharing helps, what it costs, and how
  to share so the gains hold and the cost stays small."*
- L140 (repair): *"Our earlier work~\cite{silva2025mtlnet} paired static category classification
  with next-category prediction and found no consistent multi-task gain; this chapter introduces
  the next-region task and the check-in-level representation, on which sharing helps instead of
  hurting (Section~\ref{sec:mobiwac:results-part2})."*

Both keep the arc's honesty (the null is genuine, of its time) and remove the region-task error.
If approved: log in `articles/[mobiwac]/ERRATA.md` + Appendix B. **Escalation, not obedience: the
author must rule because it edits an under-review paper's claims.**

## B.2 — Ch.6 64.54 vs Ch.5 64.51 convention blur (MTL Finding 2 / Number N-2 / Banca A-1). **VERDICT: APPROVE-WITH-EDIT.**

**Re-derived firsthand:** Ch.5 Table 3 (5_mobiwac.tex:479) reports AL joint next-category =
**\textbf{64.51}\sd{0.09}** — the **joint-best** value, and the dissertation's reported convention
(author ruling 2026-07-18; `JOINT_BEST_RESULTS.md` L32: `AL | 56.82 | 64.54 diag | 64.51 jb`).
Ch.6 L78 uses **64.54** (the diagnostic-best value, from
`storyline/audit/capacity_baseline_experiment.md` L92/L113). Same cell, two conventions across
chapters — exactly the joint-best/diagnostic-best blur AGENT_GUARDRAILS N5 forbids.

- **Lens 1:** N5 (never blur joint-best vs diagnostic-best); the flagship table is the reference,
  so Ch.6 must match it. Verdict-neutral (capacity gap is +7.72 at 64.54 or +8.35 at 64.51; no
  conclusion moves), so this is a consistency fix, not a result change.
- **Lens 2:** I checked the OTHER two numerals in the sentence — 56.16 (capacity-baseline best
  arm) and 56.82 (dedicated ceiling) — these are capacity-experiment quantities that exist only at
  one convention; only the **joint** value has the dual-convention ambiguity. So editing just the
  64.54→64.51 does NOT create a new intra-paragraph mismatch (the 56.x numbers are not joint-model
  cells). Safe.
- **Exact edit** (6_conclusion.tex:78), preserving the landed C-1 wording around it:
  - FROM: `dedicated model at its own tuned width and 64.54 for the joint model.`
  - TO:   `dedicated model at its own tuned width and 64.51 for the joint model.`
- **Interaction (I1):** this is the same paragraph as landed fix A.5 — change only the numeral;
  do not touch "yields nothing" / "the gain resides in". **Number auditor (06) should re-run the
  N4 numeral sweep after this one-character change** to confirm the capacity gap prose (if any
  states a delta) still traces. (No delta is stated in prose here — the gap is left implicit — so
  no cascade.)

## B.3 — Ch.2 L532 hard-banned "unlocks" in the climax sentence (Style-auditor TOP-2). **VERDICT: APPROVE-WITH-EDIT.**

**Re-derived firsthand:** `2_fundamentals.tex:532` *"what a representation built for check-ins
unlocks for a redesigned joint model"*. **"unlock" IS on the inherited MobiWac GLOSSARY §8 ban
list** (line 222: `leverage, harness, unlock, foster ... → use, apply, enable, obtain`), which
WRITING_LAW §4 inherits wholesale. This is frame prose (full-force zone) and it is the chapter's
hinge sentence, so the tell is maximally visible.

- **Lens 1:** clear §4 idiom/AI-tell violation.
- **Lens 2:** the sentence must keep its forward-looking force (what the check-in representation
  makes possible for the joint model). "enables ... for" preserves it exactly.
- **Exact edit** (2_fundamentals.tex:531-532):
  - FROM: `It finally asks what a representation\nbuilt for check-ins unlocks for a redesigned joint model, one that, by paired`
  - TO:   `It finally asks what a representation\nbuilt for check-ins enables in a redesigned joint model, one that, by paired`
  - ("enables in" reads better than "enables for"; the glossary maps unlock→enable. Claim
    unchanged.)

## B.4 — Ch.4 L226 Gowalla dataset mis-cite (Citation F-1). **VERDICT: APPROVE-WITH-EDIT.**

**Re-derived firsthand:** `4_courb.tex:226` cites `\cite{liu2014geographical}` for "the Gowalla
dataset". That key is Liu et al., CIKM 2014, a location-recommendation *method* paper, not the
dataset source. The canonical dataset citations already appear correctly in the SAME chapter
(`cho2011gowalla` at L18, `jure2014snap` at L33), so L226 is both a mis-source and internally
inconsistent. Inherited from the CoUrb original (`src_en/sections/results.tex:7`).

- **Lens 1:** AGENT_GUARDRAILS R2 (attribute fidelity / cite the right source). It is inherited
  published text, so under the errata policy it is a fix-in-dissertation + Appendix B item (author
  ruling 2026-07-21 already makes such fixes silent in the text + listed once in Appendix B — this
  fits that standing ruling, so it does NOT need fresh author sign-off; it needs the Appendix B
  line).
- **Lens 2:** I verified `liu2014geographical` is cited ONLY at L226, so replacing it orphans the
  key — benign in a numeric single-list bib (an uncited entry simply is not numbered), but the
  applier should DROP the now-unused entry from `references.bib` to keep the list clean (or leave
  it; harmless). No information lost — the dataset is still cited, correctly.
- **Exact edit** (4_courb.tex:226), matching the chapter's own L18 usage:
  - FROM: `conducted with the Gowalla \textit{dataset} \cite{liu2014geographical} in the states`
  - TO:   `conducted with the Gowalla \textit{dataset} \cite{cho2011gowalla,jure2014snap} in the states`
  - Then remove `liu2014geographical` from `references.bib` if it is now uncited anywhere.
  - Appendix B: add one line ("CoUrb chapter: Gowalla dataset citation corrected from a
    recommendation-method paper to the dataset sources").

## B.5 — Ch.2 §2.1 Song 93% presented as a universal "ceiling" (POI-expert MAJOR M1/M2). **VERDICT: APPROVE-WITH-EDIT.**

**Re-derived firsthand:** §2.1 (L35-37) says *"a potential predictability of about 93\% on where
an individual goes next~\cite{song2010limits}. That ceiling is the reference point against which
any predictive model should be read."* §2.4 (L428-433) then correctly scopes it: *"it is not,
however, a ceiling on seven-class category macro-F1 or on region ranking ... The operative ceiling
... is the dedicated single-task model."* The §2.1 wording ("any predictive model") overstates a
next-location bound as a ceiling for tasks with different label spaces; §2.4 disowns it. The two
passages are ~400 lines apart, so a reader hits the universal claim first.

- **Lens 1:** WRITING_LAW §3 (scope every universal; every number carries its correct reference
  point). "any predictive model" is an unscoped universal contradicted later in the same chapter.
  This is a genuine honesty-law item, not a nit.
- **Lens 2 — the trap to avoid:** do NOT delete the 93% figure or its motivational role (it frames
  *why mobility is learnable at all*, a real and useful point that §2.4 also relies on). The fix
  is to SCOPE the §2.1 claim to next-location and point forward, not to cut it. Deleting it would
  lose the "learnable at all" motivation.
- **Exact edit** (2_fundamentals.tex:35-37):
  - FROM: `93\% on where an individual goes next \cite{song2010limits}. That ceiling is the\nreference point against which any predictive model should be read. A learned model\nthat trails it by a wide margin has room to improve; one that approaches it is near\nthe limit the data allows.`
  - TO:   `93\% on where an individual goes next \cite{song2010limits}. This bound is specific to
    next-location prediction at coarse spatial resolution; it shows that mobility is far from
    random and is learnable at all, and Section~\ref{sec:fund:eval} states the reference points
    that actually bound the category and region tasks studied here.`
  - This keeps the figure and its "learnable at all" role, removes the false universal ceiling,
    and forward-references §2.4 (`sec:fund:eval`, verified as the correct label) where the true
    reference points (majority-class floor, Markov floor, dedicated ceiling) live. No number lost;
    scope corrected; consistent with §2.4.

## B.6 — Ch.4 chapter title `\:` renders as thin space not colon (Line-editor TOP-2 / N4 out-of-scope). **VERDICT: APPROVE-WITH-EDIT.**

**Re-derived firsthand:** `4_courb.tex:8`:
`\chapter{Article 2: ST-MTLNet\: Spatio-Temporal Point-of-Interest Representations for Multi-Task
Learning}`. The `\:` is a math-mode medium-space command; in a title it prints a thin space where
a colon is intended ("ST-MTLNet Spatio-Temporal..." with an odd gap). The first `Article 2:` uses
a correct literal colon, so the intent is unambiguous.

- **Lens 1:** not a law item per se, but a visible typographic defect in a heading; the fix is
  mechanical and unambiguous.
- **Lens 2:** nothing lost; purely corrective.
- **Exact edit** (4_courb.tex:8):
  - FROM: `\chapter{Article 2: ST-MTLNet\: Spatio-Temporal`
  - TO:   `\chapter{Article 2: ST-MTLNet: Spatio-Temporal`
  - Applier confidence (verified firsthand): a literal `:` in a `\chapter{}` title is already
    proven safe in this exact template — **Ch.3 L8 (`Article 1: An Investigation...`) and Ch.5 L14
    (`Article 3: Predicting...: A Check-in-Level...`, two literal colons) compile cleanly**, and
    babel's main language is `english` (`\selectlanguage{english}`, `0_main.tex:72`; `brazil` is
    loaded as a secondary option only, and neither makes the colon active). Ch.4's `\:` is the
    lone outlier. Rebuild and eyeball the running header + TOC after applying.

## B.7 — Frame number style: "93 percent" vs "93\%" (Line-editor TOP-3). **VERDICT: APPROVE-WITH-EDIT (Ch.2 is the outlier).**

**Re-derived firsthand:** the SAME 93% figure prints as **"93 percent"** in Ch.1 L38 and as
**"93\%"** in Ch.2 L35 and L429. Ch.5 uses the spelled form consistently ("25 percent", "34
percent", "67 to 87 percent", "13 to 27 points"...). So the document convention is **spelled-out
"percent"**, and **Ch.2's two "93\%" are the outliers**, not Ch.1.

- **Lens 1:** WRITING_LAW §1 asks for consistency (digits for data quantities, but the running
  choice for percentages here is the spelled word, set by Ch.1 and Ch.5). Internal consistency is
  the law; the majority form wins.
- **Lens 2:** nothing lost; purely stylistic alignment.
- **Exact edits** (align Ch.2 to the document's spelled-out form):
  - `2_fundamentals.tex:35`: `93\%` → `93 percent`
  - `2_fundamentals.tex:429`: `93\%` → `93 percent`
  - (Do NOT touch Ch.5's `\%`-free prose or any table cell; tables and math stay numeric. Only
    these two body-prose instances are inconsistent with the rest of the frame.)
  - Interaction: B.5 rewrites L35's sentence entirely — if B.5 is applied, its replacement already
    reads "93\%"; apply the "percent" spelling INSIDE the B.5 replacement text too (i.e. the B.5
    final text should read "a potential predictability of about 93 percent"). L429 is independent.

## B.8 — "at [dataset/state]" as the reported-performance preposition (Line-editor TOP-1, systematic). **VERDICT: APPROVE-IN-PRINCIPLE, but VETO any blanket/mechanical find-replace.**

The line editor flags "at Alabama", "at four of six datasets", "at Istanbul" etc. as non-idiomatic
and inconsistent, proposing a systematic sweep to "on"/"for". **I APPROVE fixing genuine
readability instances but VETO running this as a mechanical campaign,** for one reason grounded in
the law:

- **Lens 1 — the collision:** the region-verdict law (WRITING_LAW §3; GLOSSARY §4) fixes exact
  verdict phrasings: *"outperforms ... at four of six datasets"*, *"matches ... at AL/AZ"*. These
  are **law-mandated verbatim scopes**, echoed identically in the Abstract, Resumo, Ch.2 §2.5,
  Ch.5, and Ch.6 (the L3/style report confirmed the parity). A blanket "at→on/for" replace would
  (a) desynchronize the Abstract↔Resumo↔body verdict wording that persona 03/08 certified as
  clause-for-clause parallel, and (b) risk changing a scope preposition inside a frozen verdict
  sentence. That is exactly the "compression that drops/alters a scope qualifier" trap in my
  known-trap list.
- **Lens 2:** the "at four of six datasets" / "at AL/AZ" phrasings carry the verdict SCOPE; they
  are not free stylistic choices. Their information (which datasets, how many) is load-bearing.
- **Legal alternative:** the line editor may fix ONLY the non-verdict, non-parallel instances
  (e.g. a stray "the model performs well at Texas" in descriptive prose), leaving every
  verdict-bearing "at N of six" / "at AL/AZ" / "at Istanbul/FL/TX/CA" UNTOUCHED, and must re-run
  the Abstract↔Resumo↔body parity check (persona 03/08) after any change. **This item goes back to
  the author/line-editor with that constraint; it is not a clean APPROVE.** If the author wants the
  verdict preposition itself changed, that is a whitelist-wording decision (AGENT_GUARDRAILS C1),
  changed everywhere at once or nowhere — NEEDS-AUTHOR for that sub-part.

---

# PENDING items I did NOT rule (correctly out of this gate's scope)

These are pre-existing BLOCKERs / regen tasks that are NOT "proposed edit texts" — they are author
decisions or asset regenerations, so they are NEEDS-AUTHOR by nature, not gateable edits:

- **Ch.3 dataset placeholders** (`3_cbic.tex:235`, the `[$N_{users}$; VERIFY]` triplet rendered in
  the built PDF — N4-1 / Style BLOCKER-1 / POI BLOCKER-B1 / Banca A-4 / Cold-reader ②).
  **NEEDS-AUTHOR:** the sanctioned fix is a repo-committed recompute over the CBIC-era Florida
  pipeline, author-approved before insertion (NORTH_STAR §4). This is not an edit I can supply
  text for — no number may be invented. It is the document's top pre-existing blocker; it must be
  resolved (run the script, or the author explicitly accepts visible placeholders for the advisor
  draft) before the advisor build. Flagged, not gated.
- **Dissertation title** still `[TITLE — ...]` on cover/Resumo/Abstract (Banca A-2, Cold-reader ③)
  — open decision NORTH_STAR §5.8; author-only.
- **Front-matter placeholders** (approval sheet, banca, date) — open decisions; author-only. NOTE
  the C-4 trap from the style report: these placeholders currently contain `---` that DO render as
  em-dashes in the PDF; when the real values land, confirm em-dash count returns to 0 (the
  chapter prose is already clean). A cheap hardening: switch the placeholder separators to colons
  now. (Recommend, not gate.)
- **Figure 2 Portuguese labels** (Visual-18 MAJOR-1) and **Figure 3 color-only Food/Shopping
  encoding** (Visual-18 MAJOR-2) — these are figure REGENERATIONS (matplotlib re-render with EN
  labels / hatch dual-encoding per WRITING_LAW §5), not text edits. NEEDS-AUTHOR/asset work; I
  cannot supply "exact replacement text" for a figure. Both are real and should be done before the
  advisor build; neither is in this gate's edit-text scope.
- **Ch.4 italicized loanwords** ("embedding"/"folds"/"dataset" in `\textit{}`, Readability-15
  MAJOR / Translation-08 handoff) — a fidelity-vs-style call on translated published prose (L5
  zone). NEEDS-AUTHOR: if the PT original italicized them, fidelity (L5) may require keeping them;
  a blanket de-italic is a style choice the author/persona-08 must rule. Not a clean gate item.

---

# INTERACTION FINDINGS (cross-item)

- **I1 (numeral vs idiom, same paragraph):** B.2 (64.54→64.51) edits the same Ch.6 paragraph that
  landed fix A.5 (C-1 idiom) already touched. Apply B.2 as a single-numeral change; do not
  re-touch the A.5 wording. No conflict, but same-site — sequence them in one edit pass.
- **I2 (dedup pair, image survival):** A.2 (Ch.1) + A.3 (Ch.2) are the two dedup edits. Verified
  they did NOT jointly orphan the "weekday lunch/Saturday night" image (survives in Ch.1 L119-121,
  the signed-off beat). No further action — recorded because this is the exact trap (delete both
  copies of a disclosure/motif) the persona guards.
- **I3 (preposition campaign vs verdict law):** B.8's "at→on/for" sweep overlaps the frozen
  verdict scopes. See B.8 VETO-blanket. The two must not be run together mechanically.
- **I4 (B.5 vs B.7, same line):** both touch 2_fundamentals.tex:35. If B.5 is applied, fold the
  B.7 "percent" spelling into the B.5 replacement text (do not apply B.7 to L35 separately). L429
  (B.7) is independent.
- **I5 (F-1 orphan):** B.4 removes the only use of `liu2014geographical`; the applier should drop
  the bib entry to avoid an uncited-but-present record (benign either way in numeric style).

---

# NET-SIZE ESTIMATE vs the page budget

- Active budget: Fundamentals is spec'd thin (8–12 pp, NORTH_STAR §5.6); document is 87 pp
  defense / 83 pp final, both stable post-phase-6.
- Every Part B text edit is an in-place reword or a single-token change; none adds or removes a
  paragraph. B.1 (if the author approves it) slightly SHORTENS two Ch.5 sentences. B.5 replaces
  four short sentences with two (slightly shorter). **Net effect: neutral-to-slightly-shorter.**
  No page-budget risk; re-confirm 87/83 after application (the margin fix already proved the
  layout has ~0.4 cm/page of reclaimed vertical space, so minor prose shortening will not reflow
  chapter boundaries).

---

# FINAL APPROVED LIST (ready to apply verbatim)

Apply in this order; rebuild + `check.sh` + persona-06 numeral re-sweep after.

1. **B.3** — `2_fundamentals.tex:531-532` — `unlocks for` → `enables in` (exact text in B.3).
2. **B.5** — `2_fundamentals.tex:35-37` — Song ceiling scoped to next-location + forward-ref to
   `sec:fund:eval` (exact text in B.5; write "93 percent" per I4).
3. **B.7** — `2_fundamentals.tex:429` — `93\%` → `93 percent` (L35 handled inside B.5 per I4).
4. **B.4** — `4_courb.tex:226` — `\cite{liu2014geographical}` → `\cite{cho2011gowalla,jure2014snap}`;
   drop the now-uncited bib entry; add the Appendix B line.
5. **B.6** — `4_courb.tex:8` — `ST-MTLNet\:` → `ST-MTLNet:` in the chapter title.
6. **B.2** — `6_conclusion.tex:78` — `64.54` → `64.51` (single numeral; leave A.5 wording intact).

**Held for the AUTHOR before the advisor build (NOT applied, NOT gateable as edit-text):**
- **B.1** (Ch.5 CBIC misattribution) — the batch's most important item; proposed repair text in
  B.1 for the author to approve, then ERRATA.md + Appendix B. Do not ship to advisor unresolved.
- **B.8** (preposition campaign) — approve targeted fixes only; VETO blanket; re-run parity check.
- Ch.3 dataset placeholders; title; front-matter placeholders; Figure 2/3 regen; Ch.4 loanword
  italics — pre-existing author decisions / asset work, listed above.

_End of gate report. Read-only pass; I gated, I applied nothing._

---

## `15_readability_editor_report.md`

# Persona 15 · Readability Editor — Review Report (v1 defense build)

> **Reviewer:** Readability editor (professional academic-editor quality pass).
> **Scope:** FULL defense build — all chapters, front matter, appendices.
> **Sources read:** `main_defense.pdf` (87 pp., built 2026-07-23 18:08) for reading experience;
> `.tex` sources under `src/` and `src/chapters/` for quoting (file:line).
> **Mandate:** judge the WRITING as writing — readability, flow, clarity, redundancy, conciseness,
> voice consistency, academic style, paragraph craft, sentence craft, reader experience. Assume
> science / numbers / citations are correct (other personas own them). Read-only; no rewrites.
> **Status:** IN PROGRESS — written incrementally.

---

## Document map (from TOC)

- Front matter pp. 1–11 (title, catalog, approval, abstract, resumo, lists, TOC)
- Ch.1 Introduction pp. 12–16 (frame prose)
- Ch.2 Fundamentals pp. 17–24 (frame prose — the thin de-duplicating chapter)
- Ch.3 Article 1 / CBIC pp. 25–40 (re-typeset paper, EN origin)
- Ch.4 Article 2 / CoUrb pp. 41–55 (re-typeset paper, translated PT→EN)
- Ch.5 Article 3 / MobiWac pp. 56–71 (re-typeset paper, EN origin)
- Ch.6 Conclusion pp. 72–75 (frame prose)
- References pp. 76–80
- Appendix A contributions p. 82; B errata pp. 83–86; C AI-use disclosure p. 87

---

## VERDICT (persona scope: is this text a pleasure to read?)

**Read-worthy, with one clear weak axis: cross-chapter consistency.** The frame prose
(Chapters 1, 2, 6, the appendices, the Abstract) is genuinely well written: one steady
authorial voice, varied section openers, real sentence-length variety, honest hedging, and
purpose statements that connect forward. The re-typeset paper chapters read clearly on their
own. What keeps the document from reading as *one* text is a surface seam, not a prose-craft
seam: three visibly different typographic/voice registers (frame; CBIC with inline bold; CoUrb
with pervasive italics), one cross-chapter task-name collision, and a few unparseable sentences
carried from the CBIC source. All of these are fixable without touching any protected claim,
number, or the published wording's meaning. Fix them and the "three papers read as one document"
goal is met.

---

## TOP 3 FINDINGS

1. **[CRITICAL] The task name collides across the frame/paper seam.** The frame builds its whole
   honesty spine on keeping *next place* / *next category* / *next region* distinct, yet
   Chapters 3 and 4 call their sequential task "Next-POI Prediction" while defining it as
   predicting the next *category*. A reader who trusted the frame's three-way distinction meets a
   name that sounds like *next place* but means *next category*. The prefaces do not pre-warn it.
2. **[MAJOR] CoUrb (Ch.4) italicizes ordinary English technical terms on every page** (*embedding*,
   *encoder*, *baseline*, *check-in*, *framework*, *heads*, *pipeline*, *timestamp*, *fclass* …),
   a translation carry-over that makes the page visibly speckled and breaks the one-voice
   illusion; it even propagates into the List of Figures. Includes the redundant "random walks
   (*random walks*)".
3. **[MAJOR] CBIC (Ch.3) uses inline bold for emphasis inside running prose** (*static
   classification task*, *dynamic, sequential task*, *negative transfer*, *POI Category
   Classification*), which the frame chapters never do; it is the second visible register break a
   reader hits when flipping between chapters.

---

## FINDINGS BY SEVERITY

### Critical

**C1 — Task-name collision across the seam (whole document; Ch.3 §3.1 / Ch.4 §4.1 vs frame Ch.1
§1.1, Ch.2 §2.1).**
Frame, Ch.1 §1.1: "The exact *next place* task ... is a third and different problem; this
dissertation does not address it, and Chapter 2 keeps the three tasks formally distinct." Ch.2
§2.1 spends a paragraph separating next-place / next-category / next-region. Then Ch.3 §3.1 item 2:
"**Next-POI Prediction**: Predicting the category of the next POI"; Ch.4 §4.1 repeats "Next-POI
Prediction: predict the category of the next POI." **Why it hurts the reader:** the label
"Next-POI" reads as the *next place* the frame just told us is NOT predicted; the reader must
override a distinction the document worked hard to install, at the exact chapter transition the
dissertation exists to smooth. This is comprehension of the through-line, not a terminology
nitpick. **Direction:** the term itself is protected (published text), so fix it at the seam, not
in the paper body: add one clause to each paper chapter's preface stating that the article's
"Next-POI Prediction" is the *next-category* task in the frame's vocabulary, and does not predict
the exact next place. The Ch.5 preface and body already model this careful naming; the Ch.3/Ch.4
prefaces should carry the same one-line bridge. (Terminology-consistency dimension -> persona 04.)

### Major

**M1 — CoUrb pervasive italicization of common English terms (Ch.4, throughout; confirmed on the
rendered page 49).**
Dozens of instances per page of *embedding(s)*, *encoder(s)*, *baseline*, *check-in(s)*,
*framework*, *heads*, *pipeline*, *timestamp*, *fclass*, *Shared Layers Module*, *random walks*,
*skip-gram*, *negative sampling*. In the Portuguese original these were loanword/foreign italics;
carried into an English chapter they italicize words that are plain English here. **Why it hurts
the reader:** a speckled page reads as visually noisy and, next to the un-italicized frame and
Ch.5, immediately marks Ch.4 as a different document, working directly against the "read as one"
goal. It also leaks into the List of Figures (Fig. 2 caption), so the seam appears in front
matter. **Direction:** de-italicize the terms that are ordinary English in this dissertation
(keep italics only for genuine first-use-of-term or non-English words); this is a typographic
pass over the re-typeset, not a change to the translated wording or terminology. Persona 14 should
confirm no meaning shifts.

**M2 — CoUrb translation-artifact redundancy (Ch.4 §4.3.5.1).**
"Over this graph, random walks (*random walks*) are executed" — the parenthetical repeats, in
italics, the same English term it follows. Reads as an untidied translation gloss. **Direction:**
drop the parenthetical (or the lead term). One-word fix; flagged for the reader-experience effect,
mechanical execution is persona 02/08.

**M3 — CBIC inline bold emphasis in running prose (Ch.3 §3.1, §3.2.2; confirmed rendered p.26).**
"POI Category Classification is primarily a **static classification task** ... Next-POI Prediction
is a **dynamic, sequential task**"; "could result in **negative transfer**"; bolded task names in
the intro list carry into body prose. **Why it hurts the reader:** the frame chapters emphasize
with sentence structure, never with mid-sentence bold; the bold makes Ch.3 read as a different
register and pulls the eye to phrases that are not the paragraph's actual point. **Direction:**
demote in-prose bold to normal weight (keep bold only for the genuine defined-term-at-first-use if
desired, consistently). Typographic, does not touch the published wording's meaning.

**M4 — Unparseable sentences carried from the CBIC source (Ch.3 §3.2.3, §3.4.2.2).**
(a) §3.2.3: "MTPR ... combines LSTMs and adversarial learning to address uncertainty in check-ins
and improve multi-task POI recommendation both location and temporal context with a generative
component." The clause after "recommendation" has no working grammar; a reader cannot recover the
intended meaning. (b) §3.4.2.2 final sentence: "Also, it is important to notice that since we have
an unbalanced result for the MTL and single, this could lead to the worse of other results." —
"the worse of other results" is not interpretable. (c) §3.2.3: "allowing for more accuracy" is
vague. **Why it hurts the reader:** these are hard stops — the reader re-reads and still cannot
parse them, in a published-paper chapter where the rest is followable. **Direction:** these need
sentence-level repair (mechanical repair is persona 02's gate, and any wording change to a
published-text chapter must clear persona 14 / the errata log). Flagged here because they are
genuine comprehension failures, not stylistic preferences. (b) may qualify as a content erratum,
not just a wording one -> handoff to persona 07/number-fact review.

**M5 — The two dedicated-vs-joint dense statistical paragraphs (Ch.5 §5.5.3, §5.6.2).**
§5.6.2 packs the per-dataset confidence intervals into one paragraph: "Alabama (-0.41; -0.63 to
-0.20) and Arizona (0.00; -0.08 to +0.07) ... Florida +0.71; +0.67 to +0.76; Istanbul +0.19;
+0.15 to +0.23 ... +2.10 to +2.13 at Texas, +2.19 to +2.21 at California." §5.5.3 similarly stacks
seed/fold definitions + TOST + power + margin rationale in one block. **Why it hurts the reader:**
correct and necessary precision, but read as an unbroken run it exhausts; the reader loses which
number is a point estimate and which is an interval bound. **Direction:** these are strong
candidates for a small results table or a two-column list of (dataset: estimate, 90% CI) so the
prose can state the pattern and the table carry the six rows. Content-neutral restructure; no
number changes. (A table already exists for the headline results; this is the CI detail.)

### Minor

**m1 — Abstract / Resumo one long enumerated sentence (front matter, both).** The validation-arc
sentence ("Under cross-validation ... at the other two") runs ~70 words across four clauses. In an
otherwise readable abstract it is the one place the reader must hold too much at once. The
Abstract is one dense ~250-word paragraph, which is genre-standard for an ABNT resumo, so the
paragraph shape is fine; only this sentence is worth a break. **Direction:** split at "and, on the
next-region task" into two sentences. Audit the Resumo in parallel to keep the pair identical.

**m2 — Ch.6 §6.2 capacity-baseline paragraph reads heavier than its neighbors.** It is long and
number-dense (56.16 / 56.82 / 64.54; 4.2M vs 0.6M; partial California run) relative to the
surrounding consolidation prose. The author already flags its prominence as an open decision in
the source. **Direction:** if kept at length, consider leading with the one-sentence conclusion
("parameter count alone does not recover the joint gain") and letting the numbers follow, so a
reader gets the takeaway before the evidence.

**m3 — MTLnet / MTLNet spelling coexists across chapters.** Ch.3 and the frame use "MTLnet"; Ch.4
uses "MTLNet" (its §4.2.5 preface-recap explicitly flags the published spelling, which helps).
**Why it matters to the reader:** the eye catches the case flip across the seam. The in-text note
softens it. **Direction:** author call — either keep with the existing note, or normalize display
form. (Consistency gate is persona 04.)

**m4 — Long chapter titles wrap to 3–4 lines (Ch.3 title 4 lines, Ch.5 title long; rendered
p.25).** These are the real article titles, so content is fixed, but the stretched title +
two-line running header is the WRITING_LAW §5 "3-line stretched title" anti-pattern as a
reader-experience matter. **Direction:** a shorter running-header form via the optional `\chapter[
]{}` argument would lighten every page header without changing the title. (Visual/format ->
persona 18.)

**m5 — "we/our" (paper chapters) vs authorless frame — mild, expected register shift.** Ch.3–5 use
first-person plural; Ch.1/2/6 are authorless ("this dissertation"). Standard for a coletânea and
not jarring given the prefaces, so no action is needed; noted only so the author knows it was
considered and judged acceptable.

### Strengths (protect these — do not "smooth" them away)

**S1 — The frame prose is the quality bar (Ch.1, Ch.2, Ch.6, appendices).** One steady voice,
varied openers, genuine sentence-length variety (short declaratives next to long ones), honest
hedging, and section-opening purpose statements. This is what the paper chapters should be made to
sit beside; do not let an editing pass homogenize it.

**S2 — The italic time-capsule prefaces are an excellent seam device.** Each paper chapter opens
in frame voice, states venue/status, and says what later chapters revise, before dropping into
paper voice. They do real orientation work and are the main reason the seams are tolerable.
Protect the device; it is also where the C1 fix belongs.

**S3 — Ch.2 §2.5 "Relevance" hinge paragraph.** "That question presses because its parts have not
been brought together ..." lands the motivation and pre-motivates Chapters 3–5 in three clean
clauses without restating §2.1–2.4. Model of a section ending that connects forward.

**S4 — Ch.5 §5.4.2 plain-language architecture explanation.** "The category task reads the window
of per-visit vectors (the semantic stream); the region task reads the same window ... (the spatial
stream)" makes a genuinely hard design (cross-attention trunk + private spatial path) readable
without dumbing it down. The strongest single stretch of technical exposition in the document.

**S5 — Ch.6 §6.5 Final remarks.** "The negative result was not an obstacle on the way to the
contribution; worked through, it was the contribution's first half." Closes with force, does not
restate the chapter, and states the arc's thesis in one line. Protect verbatim.

**S6 — Honest negative-result framing throughout.** The CBIC null is written with conviction, not
apology, and time-indexed cleanly ("the conclusions of the time, for the configuration"). Reads as
a confident scientific record rather than a hedge. This is a readability strength as much as an
honesty one: the reader always knows where each claim stands in the arc.

---

## SCORES (1–10)

| Axis | Score | One-line justification |
|---|---|---|
| Readability | 8 | Frame excellent; paper chapters mostly clear; pulled down by a few unparseable CBIC sentences and two dense stat blocks. |
| Flow | 8 | The negative-result -> diagnosis -> resolution arc is strong and the prefaces bridge the seams; within-chapter transitions are good. |
| Clarity | 7 | Mostly unambiguous, but the task-name collision (C1) and the garbled CBIC sentences (M4) create real confusion at specific points. |
| Conciseness | 8 | Generally disciplined; a few over-long sentences (abstract arc sentence, CBIC run-ons) and the §6.2 density are the exceptions. |
| Consistency | 6 | The weak axis: three typographic/voice registers (frame / CBIC bold / CoUrb italics), MTLnet~MTLNet, and the italic convention leaking into front matter. |
| **Overall writing quality** | **8** | High-quality dissertation prose; the frame is genuinely well written and Ch.5 nearly matches it. The remaining defects are surface and seam, not deep craft. |

---

## CHAPTER-SEAM VERDICT

**Do the re-typeset papers and the frame read as one voice? — Not yet, but the gap is surface, not
craft.** There are three distinguishable registers a reader sees immediately when flipping pages:
(A) the frame (Ch.1/2/6 + appendices + Abstract) — authorless, polished, varied; (B) Ch.3 (CBIC) —
first-person, inline **bold** emphasis, and several rough/garbled sentences from the source; (C)
Ch.4 (CoUrb) — first-person/impersonal mix with pervasive *italics* on ordinary terms. Ch.5
(MobiWac) sits closest to the frame and largely reads as one voice with it (its Appendix-C-noted
"Opus readability pass" shows). The prefaces do real work smoothing the *openings* of each paper
chapter, but the *within-chapter* typographic conventions (CBIC bold, CoUrb italics) and the
task-name collision are what break the single-voice impression. Crucially, the underlying prose
*craft* across chapters is close to unified; it is the typographic surface + naming that diverge.
Addressing C1, M1, and M3 (all content-neutral) would move this from "three papers" to "one
document" without editing a single protected claim or number.

---

## OPEN QUESTIONS (author-only)

1. **Ch.4 italics:** are the italics on English technical terms a deliberate house/venue
   convention you want preserved, or a translation carry-over safe to strip? (Determines whether
   M1 is a fix or a keep.)
2. **Ch.6 §6.2 capacity-baseline paragraph:** you flagged its prominence as open — keep at current
   length, or lead-with-conclusion and compress? (m2.)
3. **MTLnet vs MTLNet:** normalize display form across chapters, or keep the published spelling per
   chapter with the existing in-text note? (m3.)
4. **CBIC garbled sentences (M4):** these need wording repair on a published-text chapter — confirm
   they route through the errata log + persona 14, and that (b) is a wording fix rather than a
   content erratum.

## OUT-OF-SCOPE HANDOFFS (one line each; not my call to make)

- Terminology/notation consistency of the C1 task-name collision and m3 spelling -> **persona 04**.
- Mechanical sentence repair of M4 garbled sentences and M2 redundancy -> **persona 02** (and
  **08** for the translated chapter).
- Whether M4(b) "the worse of other results" is a content erratum, not just wording -> **persona
  07 / number-fact review**.
- Long chapter titles / running headers / italic leak into List of Figures as a *visual* matter ->
  **persona 18**.
- Any applied wording change to a published-text chapter -> **persona 14** gate + errata log.

---

## Reading log (scratch — evidence notes gathered while reading)

### Frame prose (Ch.1, Ch.2, Ch.6, appendices, Abstract/Resumo) — READ
- Uniformly high craft. Varied openers, high burstiness, honest hedging, purpose statements per section, forward-connecting endings. No AI-tell density. This IS the frame voice benchmark.
- Ch.2 §2.2 lineage table present and clear. §2.5 hinge paragraph ("That question presses because...") lands well.
- Abstract/Resumo are a claim-parity pair; both are single dense ~250-word paragraphs. Reading-experience note: each is ONE very long paragraph (Abstract ~250 words unbroken). Dense but standard for the genre. Both use one long enumerated arc sentence ("Under cross-validation ... at the other two") that runs ~70 words — borderline but parses.
- Ch.6 §6.2 capacity-baseline paragraph is long and number-dense (author already flagged prominence as open decision in source comment). Reads as heavier than surrounding prose.

### Ch.3 (CBIC, re-typeset EN paper) — READ. SEAM D::
- Preface = clean frame voice. Body = original paper voice: heavy "we/our", inline \textbf{bold} emphasis in running prose (POI Category Classification, negative transfer, static classification task, etc.) — NOT used anywhere in frame chapters. Biggest visual/voice seam.
- Garbled/awkward sentences carried from source:
  - §3.2.3 MTPR sentence: "improve multi-task POI recommendation both location and temporal context with a generative component" — broken grammar, unreadable.
  - §3.4.2.2 last sentence: "Also, it is important to notice that since we have an unbalanced result for the MTL and single, this could lead to the worse of other results." — garbled, meaning unclear.
  - §3.2.3 "allowing for more accuracy" — awkward/vague.
  - §3.3.1.1 "A place suffers from complementarity effect" — awkward article/phrasing.
- Clarity/seam: paper calls the task "Next-POI Prediction" but defines it as predicting the *category* of the next POI (§3.1 item 2). Frame Ch.1/2 carefully separate next-place vs next-category; a reader crossing the seam meets "Next-POI Prediction" = next category here. Preface does not pre-warn the naming. (Terminology in re-typeset paper is protected — flag as reader-experience, not a fix demand.)
- Long "Rationale for Hard Parameter Sharing" bullet list + "In this chapter we..." roadmap = paper conventions, fine but heavier than frame.

### Ch.4 (CoUrb, translated PT->EN paper) — READ. SEAM D2::
- Distinct texture from BOTH frame and Ch.3: pervasive \textit{} italicization of ordinary technical English words — embedding, encoder, baseline, check-in, framework, timestamp, pipeline, heads, random walks, fclass, Shared Layers Module, etc. Dozens per page. In the PT original these were foreign/loanword italics; carried into an EN chapter they read oddly (italicizing "baseline" and "embedding" in English prose is not standard). This is the single most visible seam in the document — a reader flipping Ch.3->Ch.4 sees a page speckled with italics that Ch.3 (same author on the model) does not have. Terminology is protected under L5/re-typeset rules, but the *typographic* italic convention is a readability/consistency call worth flagging.
- Translation redundancy: §4.3.5.1 "random walks (\textit{random walks})" — parenthetical repeats the same English term it translates. Reads as a translation artifact left in.
- §4.2.5 recap sentence "the published paper typesets the name as MTLNet, and this chapter preserves that form" — clarifies MTLnet/MTLNet spelling; good, but the two spellings coexisting across Ch.3 (MTLnet) and Ch.4 (MTLNet) is a cross-chapter consistency seam a reader will notice. (Concordance = persona 04; I note the reader-facing effect only.)
- Otherwise the translation reads fluently and clearly; sentences parse, arc is clear, tables well-introduced with lead sentences. Prose quality above Ch.3 in grammatical smoothness (no garbled sentences).
- Task naming same as Ch.3: "Next-POI Prediction" defined as predicting the *category* of the next POI. Same cross-seam naming friction with frame's next-place/next-category distinction.

### Ch.5 (MobiWac, EN paper, "Opus readability pass" per Apx C) — READ.
- Highest prose quality of the three paper chapters, closest to the frame voice. Good burstiness, clear plain sentences, honest hedging ("we read the trend across the points rather than as a precise law"), verbs bound to tests, "we do not predict the exact next place" stated. No \textbf/\textit emphasis-in-prose. Reads as one voice with the frame.
- Uses "we/our" (paper convention) vs frame's authorless/"this dissertation" — a mild seam vs Ch.1/2/6, but standard and not jarring.
- Dense spots (reader effort, not defects): §5.5.3 metrics-and-tests paragraph is long and packs seed/fold definitions + TOST + power in one block; §5.6.2 the CI-by-dataset paragraph ("Alabama (-0.41; -0.63 to -0.20) and Arizona...") is a dense list of parenthetical intervals — necessary precision, heavy to read. These are inherent to the content.
- §5.4.2 has a strong plain-language explanation of the architecture (semantic/spatial stream, cross-attention) — a STRENGTH; very readable for a hard design.

### Cross-document seam summary (the persona's core verdict input)
- THREE distinguishable voices: (A) frame = Ch.1/2/6 + appendices + abstract, authorless, polished, varied. (B) Ch.3 CBIC = original paper, "we", inline bold emphasis, some garbled sentences. (C) Ch.4 CoUrb = translated, "we"/impersonal mix, pervasive italics on common terms. Ch.5 sits between B/C and A, closest to A.
- The prefaces (italic, frame voice) do a lot of seam-smoothing work — each paper chapter opens in frame voice before dropping into paper voice. This is the design and it works. But the WITHIN-paper typographic conventions (Ch.3 bold, Ch.4 italics) are what a reader sees flipping pages and are the most visible inconsistency.

---

## `16_ai_credibility_report.md`

# 16 · AI-credibility reviewer report — the external-perception simulation

> Persona: `reviewers/16_ai_credibility.md`. Runs AFTER persona 03 (style gate). Two readers in
> one report: (1) the **screener** (a 2026-grade detector pass, Pangram-class, with the
> hybrid-text windowing caveat) and (2) the **suspicious expert** (a well-read CS examiner
> keying on gestalt). Evidence base: `reviewers/research/ai_detection_landscape_2026-07-20.md` +
> `reviewers/research/ai_writing_evidence_2026-07-18.md`, refreshed this session (§7). Read-only.
> Does NOT re-run 03's counted sweeps (banned words, -ly density) — references 03's report.
> Scope: full defense build (`src/main_defense.pdf`, 87 pp) + sources (`src/chapters/*.tex`,
> `src/0_main.tex`). Snapshot 2026-07-23.
>
> **Mission framing (from the persona header):** AI use here is disclosed and legitimate. The
> job is not camouflage; it is that the text earns full credibility anyway. "There is no problem
> in using AI, but the text needs to be great." Nothing below recommends evading detection of
> disclosed use.

---

## VERDICT (per channel)

**SCREENER RISK: MEDIUM** (windowing caveat stated). The frame chapters (1, 2, 6, appendices,
front matter) are disclosed *substantive* AI drafting from author-approved outlines, which is the
mode NeurIPS 2026 verified a Pangram-class detector *does* flag (as opposed to light copy-editing,
which it does not); so a hybrid-document scan would likely place frame stretches in the elevated
range. That number would not be a truth: on hybrid text, detector scores are window-size artifacts
(NeurIPS measured 42.7% of position papers "high-AI" at 250–350-word windows, 12.7% at ~100-word
windows), so any single score is unstable by measurement, not by opinion. Two facts hold the risk
at MEDIUM rather than HIGH: the prose is lexically rich and syntactically varied, so it does *not*
additionally trip the L2-simplicity false-positive channel that flags Brazilian-authored English
(Liang 61.3%→11.6% when vocabulary was enriched); and the provenance shield (§5) is strong enough
to convert any flag from an integrity question into a documented-process one. The three re-typeset
article chapters are human-published text — a flag there is a pure false positive on peer-reviewed
prose.

**EXPERT-SUSPICION RISK: LOW.** The strongest human tell is *absence* of concrete, first-person
research detail, and this document is saturated with the opposite: the capacity-matched baseline
triple (56.16 / 56.82 / 64.54 macro-F1), the 4.2M-vs-0.6M parameter budget, the +0.001 gradient
cosine over four seeds, the partial fifteen-of-twenty California run, the freeze control at three
named datasets, and a task-pair confound the author admits against his own result — material a
generator never produces because it does not run the experiments. Burstiness is high (03: frame CV
49–57%; Abstract CV 41%, sentences 19–83 words), section openers vary, copulas are plain ("is,"
not "serves as"), and every verdict verb is bound to a named test. The residual gestalt tells are
localized and context-exempt (two conventional bold-label lists; scoped negative parallelism), not
a pervasive machine evenness.

---

## TOP 3 FINDINGS

1. **[MEDIUM · credibility shield · front matter] No up-front disclosure line — the AI-use
   statement lives only in Appendix C (p. 87, the last page).** The 2026 evidence (arXiv 2601.09620,
   "Full Disclosure, Less Trust?") establishes the layered *detail-on-demand* pattern as the design
   that minimizes the disclosure trust penalty: a one-line statement up front (near-costless to
   trust) plus the full appendix behind it (~2/3 of readers want the detail, and it is there for
   them). The dissertation has the excellent appendix but not the one-liner, so a reader meets the
   disclosure only if they reach the final appendix. Direction (additive, not applied): add a single
   front-matter disclosure sentence (folha-de-rosto footnote, preface, or a pointer where the
   Resumo/Abstract sits) that names the tool and points to Appendix C. This also serves CAPES /
   CNPq Portaria 2.664/2026 visibility. Placement mechanics cross-ref persona 13 (compliance).

2. **[MEDIUM · over-correction guard · Ch3/Ch4] Do not sterilize the re-typeset published chapters
   when acting on 03's -ly-density finding.** Persona 03 correctly reports Ch3 at 1.83% and Ch4 at
   1.24% -ly density, over the ≈0.8% band. But those two chapters are *human-published, peer-reviewed*
   text (CBIC 2025, CoUrb 2026). Aggressively scrubbing manner adverbs out of genuinely-human prose
   to hit a band does two kinds of harm this persona is charged to prevent: it risks altering
   published wording (an errata-integrity issue), and blanket tell-scrubbing is the documented
   "defensive writing" failure mode that reads as its *own* red flag (Wikipedia WP:AISIGNS; the
   L2-harm literature). Direction: trim only the decorative manner adverbs 03 named
   (effectively/frequently/consistently/largely), keep the functional ones, and stop well short of
   flattening — a few decorative -ly adverbs in real human published text are not a credibility risk.

3. **[LOW–MEDIUM · human channel · document-wide watch] Negative parallelism ("X, not Y" /
   "rather than") is the single tell a 2026 CS examiner is most primed to see — currently in spec,
   keep it from creeping.** 03 counts 27 "X, not Y" + 28 "rather than", concentrated in Ch5 (21, its
   own audited spec) and used ~1× per frame chapter as a scoped honesty device ("the input
   representation, not the sharing architecture"). That density is defensible today. The finding is
   not a fix; it is a guard: this construction is #5 on the current human-tell catalog and the target
   of new public de-slop tooling (Peter Yang's `/no-ai-slop`, July 2026), so any future AI-assisted
   edit wave that adds more will cross from "load-bearing emphasis" into "tic." Freeze the count; do
   not let edit passes raise it.

---

## 1 · GESTALT PASS (human channel)

Read as a suspicious, LLM-fluent CS examiner (Russell et al. ACL 2025: this population detects at
~92%, keying on formality / originality / clarity — "too clean, too even" — plus lexical tells).
Chapter openings, section transitions, and one full results discussion per frame chapter (Ch6 §6.2,
the consolidated answer) were read on the built PDF for rhythm and on source for quoting.

**What an expert would NOT flag (the gestalt is human):**
- **No frictionless evenness.** The arc has real friction: a published *null* result carried as the
  foundation, a diagnosis that overturns it, an admitted confound (§6.3.6) that weakens the author's
  own attribution. Generators smooth toward success; this text argues against itself and wins anyway.
- **Openers vary** (03 confirmed Ch2's five sections open five different ways; I re-confirmed on the
  PDF). No outline-shaped "This section discusses…" skeleton repeating across sections.
- **Copulas are plain.** "The starting point is the one-hot identifier"; "A place embedding … shares
  one property." No systematic copula-avoidance ("serves as / functions as / boasts"), the #6 tell.
- **Closers do not restate.** §2.1 closes on a forward hook, §2.5 on "these three questions in turn,"
  Ch6 sections on distinct concrete statements. No appended wrap-up sentences (the #4 tell).

**The residual gestalt tells (localized, context-exempt — logged, not alarming):**
- **Two bold-header-colon description lists**: §1.6 Contributions (Theoretical / Software / Empirical
  / Practical, p. 16) and Appendix C's scope enumeration (Drafting / Editing and review / Formatting
  / Code, p. 87). The bold-label-colon vertical list is tell #3 ("bullet-itis where prose belongs").
  Here the tell fires on *form* but the *context exempts it*: a contributions taxonomy is a sanctioned
  dissertation convention (WRITING_LAW §5, the Viegas pattern), and a disclosure enumeration is
  clarity-first by design. An examiner reading a dissertation expects a contributions taxonomy. The
  content inside each label is concrete and specific, not filler. Net: these are the two spots the eye
  *pattern-matches* to an AI shape, but the residual suspicion is low. Noted so the author knows where
  the eye catches; no change required unless he wants to lower the visual signal (running prose would).
- **One business idiom**: "move the needle" — Ch6 §6.1 (L40), "A change of input, with no change of
  architecture, moved the needle farther than any architectural variation tried before it." A single
  instance, a motion/business-metaphor idiom that reads slightly off in a defense register. It is
  03/idiom-law scope (the counted idiom sweep), not this persona's counted call — handoff below.
  (Verified: "needle" occurs once in the frame chapters, Ch6 only; not in Ch1.)

## 2 · SPECIFICITY AUDIT (the highest-yield check)

The persona's core thesis: the strongest human signal is the presence of concrete research detail and
reflective, first-person methodological voice that a generator cannot fabricate because it did not run
the work. **This audit PASSES, and it is the dissertation's single largest credibility asset.** Every
frame section that *should* carry lived detail does.

| Frame location | Lived-research detail present (verified in source/PDF) | Verdict |
|---|---|---|
| Ch1 §1.2 arc | The three candidate explanations of the CBIC null, named and carried forward as the arc's engine; the honest "the promise, however, is not automatic." | Grounded |
| Ch2 §2.5 relevance | The three-gap → Ch3/4/5 mapping (a synthesis only the author of the arc can write), not a literature restatement. | Grounded |
| Ch6 §6.2 answer | Capacity-baseline triple 56.16 / 56.82 / 64.54; 4.2M vs 0.6M params at Alabama; freeze control at AL/AZ/FL; +0.001 gradient cosine over 4 seeds; partial 15-of-20 California run "at the time of writing." | **Exemplary** |
| Ch6 §6.3.6 limitation | The task-pair confound stated *against* the author's own result — "no single controlled ablation separates the representation-and-topology change from the task-pair change." | **Exemplary** |
| Ch6 §6.5 remarks | "The negative result was not an obstacle … worked through, it was the contribution's first half." | Reflective voice |

**No frame section reads as generic filler that should have carried detail but did not.** The
literature-background sections (§2.1–§2.3) are appropriately less first-person, but they take
positions rather than cataloging ("This lineage is background for the present work, not its target";
"a balancer earns its place only by outperforming it") — 17 corroborates. The specificity is placed
exactly where it defeats the human tell: in the arc (Ch1), the synthesis (Ch2.5), and the results
discussion (Ch6).

*One small additive opportunity (optional, not a gap):* §1.6's Practical/Empirical items describe the
validation abstractly; the concrete headline (5.3–9.4 macro-F1) lives in the Abstract and Ch6 but not
in the contributions list. Injecting it there would add one more anchor of specificity to the most-read
page. Low priority — the number is already carried nearby.

## 3 · RHYTHM / VARIANCE PASS (residual after 03)

Variance compression is the deepest measured tell (Claude-family revision reduced variance in ~78% of
stylometric features). 03 already reported per-chapter sentence-length CV; I do not re-run that sweep. I
add the one surface 03 did not measure — **the Abstract**, the single most externally-scrutinized
paragraph in the document:

- Abstract (EN, `0_main.tex` L240–271): **9 sentences, word counts [19, 53, 45, 27, 42, 44, 41, 83, 29],
  mean 42.6, CV 41%.** The 83-word results sentence (packed with the six-dataset numbers) sits between a
  19-word opener and a 29-word thesis close. This is healthy burstiness, not the flat ~20-word uniformity
  a detector reads as low-perplexity. The high mean (42.6) reflects the numeric-dense results sentence,
  within academic-abstract norms; the *variance* is what protects it, and the variance is good.
- Frame chapters (03's figures, cited not re-derived): Ch1 CV 49%, Ch2 54%, Ch6 57% — all high. The
  frame prose is the *opposite* of variance-compressed. An edit pass that only smooths would regress this;
  it has not happened yet (03's read-aloud found the author's voice intact — concessive clauses, mid-
  paragraph result openers, varied length).
- The one compressed chapter is Ch3 (CV 43%), the re-typeset CBIC paper — human-published text. See the
  over-correction guard (Top Finding 2): its compression is a property of the *original human* prose, and
  is not a credibility problem.

## 4 · DETECTOR SIMULATION (screener channel)

**No local detector was run, by design.** A Pangram-class screener is proprietary/API-gated and not
available in this environment; the only open-weights option (RoBERTa-family) is exactly the tool the
evidence shows misclassifies 30–69% of *human* text as AI (Booth audit) and would produce noise, not a
committee-relevant signal. Running it would violate the persona's own rule that a score is never a
verdict. The screener channel is therefore a **qualitative estimate**, stated as such.

Estimate, by the two-channel logic:
- **L2-simplicity false-positive channel: LOW.** The detector-bias literature (Liang; Pindrop/Authors
  Guild ACL 2026) flags *structurally simple, low-lexical-richness* L2 prose. This dissertation's prose is
  the opposite — rich technical vocabulary, varied and complex syntax, high burstiness. The single
  intervention proven to drop L2 false-positives (enrich the vocabulary: 61.3%→11.6%) is already the
  document's baseline state. A Brazilian-author FPR spike is unlikely here.
- **Substantive-generation channel: MEDIUM.** The frame chapters *are* disclosed generation, the mode a
  strong detector flags. A hybrid-document scan would probably light up frame stretches. But (a) the score
  is a window-size artifact, not a measurement, and must be reported to any committee with that caveat; and
  (b) the shield (§5) makes the flag a process question, not an integrity one. The re-typeset chapters are
  human text where a flag is a false positive.

**Reporting rule for the author:** if anyone ever produces a detector score on this document, it is — on
hybrid text, by NeurIPS's own calibration — unstable by measurement. The correct response is never to
argue the number; it is to present the provenance (§5). That is the officially-recognized corroboration
path (NeurIPS 2026 appeal protocol), and this author has the evidence to walk it.

## 5 · PROVENANCE-SHIELD STATUS TABLE (process, not prose — the real defense)

| Shield element | Status | Evidence |
|---|---|---|
| Git AI/author commit discipline (GUARDRAILS §5) | **PRESENT (strong)** | `git log` shows clean `draft(ai):` vs `edit(author):` labels across the assembly (phases 0b–6) and the CoUrb work; commit `b642d1ce` ("audit of the Opus readability pass") corroborates the appendix's Opus claim. Disclosure is reconstructible from history, not remembered. |
| Layered disclosure (short front + full appendix) | **PARTIAL** | Appendix C (p. 87) is present and well-drafted; the up-front one-liner is **absent** (Top Finding 1). The detail-on-demand pattern is only half-built. |
| Task-precise wording (generation vs editing) | **PRESENT (exemplary)** | Appendix C discloses frame chapters as "drafted by the assistant" (generation named as generation — the honest, higher-penalty framing, correct because true) and paper chapters as "re-typeset reproductions" + a fidelity-checked translation (editing named as editing). This is exactly the EMNLP-2024-informed distinction. **Protect it — do not soften "drafted" to "edited"** (false, and exposure-after-nondisclosure is the worst outcome, Schilke & Reimann). |
| PT-BR thinking trail | **PRESENT (rich)** | `storyline/01…07` (PT structure), three `AVAL_NECESSARIA_ptBR.md` audit docs, `ch1_beat_budget.md`, `capacity_baseline_experiment.md`. This is the near-unforgeable authorship evidence no generator produces incidentally. **Recommend preserving it past the defense** (do not delete the storyline/ tree). |
| Per-chapter pre-AI / post-AI / final checkpoints (NeurIPS format) | **ADEQUATE via git** | For AI-drafted frame chapters the "pre-AI" artifact is the author-approved outline (storyline/ + beat budgets), then the `draft(ai)` commit, then author edit/approval commits — a defensible three-point chain. Optional hardening: snapshot the explicit pre/post/final triple per chapter if belt-and-suspenders is wanted for a formal appeal. |
| Oral defensibility of any passage | **SUPPORTED (soft)** | The specificity audit (§2) is itself the evidence: the numbers and controls are the author's own experiments. Direct oral-readiness is persona 12's scope. |

## 6 · OVER-CORRECTION GUARD

Flag any place where tell-scrubbing has produced defensive, sterile, or vocabulary-flattened text (a
documented failure mode that harms L2 authors specifically and reads as its own red flag).

- **No over-correction detected in the frame.** The frame prose retains transitions, real hedges, and the
  author's register; 03's read-aloud confirms the voice is intact. The process is demonstrably aware of the
  risk — 03 §9 explicitly protects load-bearing CS vocabulary (framework, robust, baseline) and warns
  against sterilization.
- **The forward risk is on the re-typeset chapters** (Top Finding 2): if 03's -ly-band fix is applied
  bluntly to Ch3/Ch4, it would push *human-published* prose toward the defensive-sterile pattern and risk
  altering published wording. Trim decoration, keep function, stop early.
- **`co-equal` ×3 (03's finding)**: replacing it is fine (genuine awkwardness), but the guard is not to
  flatten "co-equal ends" into something bland — keep the meaning (neither target subordinate).

## 7 · REFRESH PASS (bounded web check, 2026-07-24 — proposed updates for author sign-off)

The two evidence files are 4–6 days old; a bounded pass confirms **nothing fundamental has moved** on the
stylometric-tells side. Genuinely-new, datable items worth folding into the evidence files (never
auto-applied):

1. **Vrije Universiteit Brussel study (peer-reviewed, June 2026)** — 4 detectors (Pangram, GPTZero,
   Turnitin, Copyleaks) × 160 academic papers >4,000 words, evenly split human-ESL / AI / hybrid /
   humanized. Only Pangram detected reliably (97.5% fully-AI, 95% humanized); the other three scored
   ~0% on fully-AI. This is *new peer-reviewed corroboration on LONG academic text* (the dissertation's
   exact genre) of both the legacy-detector collapse and Pangram dominance, and it tested ESL-human text
   directly. → add to `ai_detection_landscape` detector-landscape section.
2. **Peter Yang `/no-ai-slop` (open-source Claude skill, 22 Jul 2026, ~1k GitHub stars in a day)** —
   targets 20+ patterns including *binary contrasts* (= negative parallelism), fake-profound closers, and
   throat-clearing openers. Reinforces the Top-Finding-3 watch and is a new public human-tell catalog
   analog alongside Wikipedia WP:AISIGNS. → add to the human-perception catalog list.
3. **Substack platform-wide Pangram deployment (21–22 Jul 2026)**, scoring posts human / AI-assisted /
   AI-generated over 100 words. Context only: the Pangram-as-default-screener trend keeps spreading beyond
   venues/admissions; does not change a dissertation's threat model. → optional context note.
4. **Wikipedia WP:AISIGNS current state**: Grok-specific "underscore"/"causal/empirical/correlate"
   overuse persists into 2026; copula-avoidance and rule-of-three items stable; no new *structural* tell
   beyond the July-2026 baseline. Confirms the evidence file is current. No change needed.

## 8 · WHAT READS CREDIBLY HUMAN (protect it — do not push toward sterility)

- **The specificity (§2) is the crown jewel.** The capacity-baseline numbers, the freeze control, the
  +0.001 cosine, the admitted confound. This is what LLM filler cannot contain. Never trade it away in a
  trim.
- **The honest-arc reflective voice** — "the negative result … was the contribution's first half"; "a
  finding for this pair of tasks rather than a general rule." This is the subjective research voice the
  Witch-Hunt reviewers found *missing* in AI-suspected text. Keep it.
- **Burstiness and varied openers** (frame CV 49–57%; Abstract CV 41%). Protect against any smoothing pass.
- **Task-precise disclosure wording** (generation disclosed as generation). Correct and honest; protect it
  verbatim (§5).
- **The PT-BR trail + git discipline** — the actual shield. Preserve, do not prune.
- **The per-venue notation-dialect seam (Ch3 MTL/Single, Ch4 MTLNet/baseline, Ch5 Joint/Dedicated).**
  Persona 15 flags this as a *readability* defect and may be right to harmonize it. But from THIS channel it
  is a **credibility asset**: three visibly different provenances is what genuinely-different human papers
  look like, and a uniform machine-smoothed document would not have it. Conscious trade-off for the author:
  if harmonizing per 15, keep some human texture per chapter — do not flatten all three into one seamless
  machine voice, which would trade a readability gain for a small credibility loss.

## 9 · RANKED FINDINGS (channel · severity · location · direction — never applied)

1. **[credibility · MEDIUM · front matter]** No up-front layered disclosure line; disclosure only in
   Appendix C p. 87. → add a one-line front-matter disclosure pointing to Appendix C (detail-on-demand
   lowers the trust penalty; serves CAPES/CNPq visibility). Cross-ref 13 for placement mechanics.
2. **[over-correction guard · MEDIUM · Ch3/Ch4]** 03's -ly-band fix, if applied bluntly to the
   human-published chapters, risks sterilization + errata drift. → trim only named decorative adverbs; keep
   functional ones; stop short of flattening.
3. **[human channel · LOW–MEDIUM · document-wide]** Negative parallelism is the most examiner-primed 2026
   tell; currently in spec. → guard, do not add; freeze the count across future edit waves.
4. **[credibility asset trade-off · LOW · Ch3/4/5]** The notation-dialect seam (15's readability defect) is
   a human-provenance signal from this channel. → if harmonizing, retain per-chapter texture; do not
   machine-smooth to one voice.
5. **[human channel · LOW/NIT · Ch6 §6.1 L40]** "move the needle" business idiom (single instance) reads
   off-register. → 03/idiom-law counted scope (handoff); reword to "moved the results / mattered more than."
6. **[human channel · NIT/watch · §1.6, Appendix C]** Two bold-header-colon description lists are the eye-
   catch AI-shape spots, but sit in conventional dissertation contexts with specific content. → note only;
   optional conversion to running prose if the author wants to lower the visual signal.

## OUT-OF-SCOPE HANDOFFS (one line each)

- **Persona 03 (style/idiom counted gate):** "move the needle" (Ch6 §6.1 L40, single instance) is a
  motion/business idiom not on the current sweep — add to the idiom count.
- **Persona 13 (UFV compliance):** the *placement* of a front-matter disclosure line (Top Finding 1) and
  whether CAPES/CNPq require it in a specific front-matter location is compliance's call; I own only the
  credibility rationale.
- **Persona 15 (readability):** already owns the notation-dialect seam as a readability defect; §8 adds the
  credibility counter-weight for the author to balance.

## OPEN QUESTIONS (author only)

1. **Front-matter disclosure line** — do you want to add the one-liner (Top Finding 1), and where (folha-de-
   rosto footnote / preface / near the Abstract)? This is the single highest-value credibility edit.
2. **Detector-score posture** — if the banca or CAPES ever runs a detector, are you prepared to present the
   provenance (git trail + storyline/ PT-BR outlines + per-chapter checkpoints) rather than argue the score?
   The material exists; the question is whether to assemble it into a one-page "authorship evidence" packet
   pre-emptively.
3. **PT-BR trail retention** — confirm the `storyline/` tree and `AVAL_NECESSARIA_ptBR.md` docs are kept
   (not cleaned up) through and past the defense; they are your strongest authorship evidence.

---
_End of report. Screener risk MEDIUM (windowing caveat); expert-suspicion risk LOW. The text largely earns
its credibility; the one structural gap is the missing up-front disclosure line, and the one process risk is
over-scrubbing the human-published chapters. Re-run after the disclosure line lands and after any heavy edit
wave — tells creep back through AI-assisted rewriting._

---

## `18_visual_presentation_report.md`

# Reviewer 18 · Visual & Presentation — report (v1 defense build)

> Persona: the rendered-pages pass. Read-only. Input: `main_defense.pdf` (87 pp) rendered
> page by page as images, plus `main_final.pdf` front-matter check and the build log.
> Common protocol: reviewers/README.md. Sources: WRITING_LAW §5, VIEGAS_ANALYSIS §2–§3.
> Started: session in progress. This file is written incrementally.

## Status: COMPLETE

## Verdict: NEEDS A VISUAL PASS

The book reads as one document at the structural level: booktabs throughout, captions
placed correctly (above tables, below figures), self-contained captions, uniform mean +/- std,
clean cross-references, both build front matters correct. It is legible and coherent. It is
not yet print-ready: four MAJOR visual defects would be caught by a careful examiner and one
(Portuguese labels inside an English-frame figure) is a visible contradiction of the frame-
language decision. None rises to "not presentable" — all are localized and fixable without
touching the science. Fix the MAJORs, then this is a clean defense build.

## Method

`main_defense.pdf` (87 pp) rendered page by page at 120 dpi (survey contact sheets) and the
float-bearing pages re-rendered at 200 dpi; every figure additionally rendered to grayscale to
test print-safety. `main_final.pdf` (83 pp) front matter checked. Build log parsed for
overfull/underfull boxes and mapped to pages. Rule-edge overflow on Table 1 measured in pixels
against the text-block width. Evidence images live in `_history/_review_v1/hi/` and `_history/_review_v1/sheets/`.

## Top 3 findings

1. **[MAJOR] Figure 2 (p.46) carries Portuguese labels in an English-frame chapter** — the
   outer group boxes read "Encoder Espacial", "Encoder Temporal", "Encoder Categórico",
   "Coordenadas (lat, lon)", "Timestamps (hora, dia)", "Categorias (POI graph)". The frame is
   English (CLAUDE.md decision). This is the single most visible cross-chapter drift.
2. **[MAJOR] Figure 3 (p.51) distinguishes Food from Shopping by color only (red vs orange)** —
   fails grayscale print (the two collapse to near-identical gray) and is weak even in color;
   the co-location pattern the figure exists to show becomes unreadable. Violates WRITING_LAW §5
   (grayscale-safe dual encoding; no color-only distinctions).
3. **[MAJOR] Chapter-opening titles stretch to 3-4 justified lines with mid-word hyphen breaks**
   (Ch.3 p.25 is 4 lines: "Multi-/Task", "Ca-/tegory", "Pre-/diction"). This is the exact Viegas
   defect VIEGAS_ANALYSIS §3 says not to repeat, and worse (4 lines + hyphenation). Same long
   titles drive the two-line running headers and all 30 overfull-vbox warnings.

## Findings (ranked)

### MAJOR

**M1. Portuguese labels inside Figure 2, p.46 (CoUrb architecture).**
Quote (in-figure text): "Encoder Espacial", "Encoder Temporal", "Encoder Categórico",
"Coordenadas (lat, lon)", "Timestamps (hora, dia)", "Categorias (POI graph)". The inner boxes
are English ("Location Encoder", "Category Encoder", "Shared Layers Module", "Category Output").
The chapter frame and every other figure are English. A banca reading an English dissertation
hits Portuguese diagram labels in one figure only.
Direction: regenerate Figure 2 with English labels (Spatial Encoder / Temporal Encoder /
Categorical Encoder; Coordinates (lat, lon); Timestamps (hour, day); Categories (POI graph)).
If the source diagram is not regenerable, redraw to match the MobiWac diagram vocabulary (see M4).

**M2. Figure 3, p.51 (spatial distribution) uses a color-only, grayscale-unsafe encoding.**
Caption: "Spatial distribution of POIs of the Food (red) and Shopping (orange) categories".
Red vs orange is a weak contrast in color and near-indistinguishable in grayscale (verified on
`_history/_review_v1/hi/p051_gray.png`: both classes render as the same mid-gray dot). The figure's whole
point (Food/Shopping co-location) is lost in print. In-figure axis ticks, panel titles, and the
legend are also far below body size.
Direction: re-encode the two categories with distinct marker shapes AND a high-contrast,
grayscale-safe color pair (e.g. filled circle vs open triangle; dark blue vs light gray, matching
the MobiWac bar-chart palette on pp.67-68). Enlarge in-figure text to near body size.

**M3. Stretched, hyphen-broken chapter-opening titles.**
Evidence `_history/_review_v1/hi/openers_compare.png`. Ch.3 (p.25) title sets on 4 justified lines with
mid-word hyphenation ("into Multi-/Task", "Point-of-Interest Ca-/tegory", "Next-POI Pre-/diction");
Ch.4 (p.41) is 3 lines with large inter-word gaps on line 2 ("Point-of-Interest    Representations
   for"); Ch.5 (p.56) is 3 lines. Ch.6 "Conclusion" (1 line) shows how clean the rest look.
Direction: set chapter titles ragged-right (no justification) and suppress hyphenation in the
title font, and/or supply a short title via `\chapter[short]{full}`. A short title also fixes M5
and the running-header overflow (M6) in one move.

**M4. Cross-chapter figure-style drift (diagram vocabulary).**
Ch.3 Fig 1 (p.33) and Ch.4 Fig 2 (p.46) are saturated red/green/orange flowchart boxes (a
"different paper" look, and different from each other). Ch.5 Figs 4-5 (pp.60,62) are a muted
pastel, thin-rule, italic-annotation vocabulary that is visibly more refined and consistent.
The three chapters' architecture diagrams do not read as one hand.
Direction: adopt the Ch.5 diagram vocabulary as the house style and redraw Fig 1 and Fig 2 to
match (box fill, rule weight, font, arrow style). Keep an "adapted from [CBIC/CoUrb]" note if the
originals are preserved for provenance. This is the highest-leverage single consistency fix.

**M5. Table 1 (p.20, lineage) overflows the right text margin by ~29.8 pt (~1 cm).**
Build log: "Overfull \hbox (29.76408pt too wide) in paragraph at lines 214-232" (the `tabular`).
Measured on the render: text block right edge x=1494 px; Table 1 rules extend to x=1577 px = 83 px
= 29.9 pt past the margin (`_history/_review_v1/hi/t1_overflow_crop.png` shows "Reference"/"Chapter 4/5"
protruding). It looks flush only because the 2 cm right margin absorbs it; the table rule clearly
overshoots the body text and the header rule.
Direction: narrow the middle "What it added" column (it is the widest), e.g. wrap it in a fixed
`p{width}` column or shorten the phrasings, so the table fits `\textwidth`. Do not scale the whole
table down (would shrink the text below body size).

### MINOR

**m6. Two-line running headers on Ch.3 and Ch.5 overflow the header box (30 x 14.5 pt vbox).**
All 30 "Overfull \vbox (14.49998pt too high) while \output is active" warnings fall on exactly
pp.25-39 (Ch.3) and pp.56-70 (Ch.5) — the two chapters whose long titles wrap the running header
to two lines (`_history/_review_v1/hi/header_compare.png`). Ch.2/Ch.4/Ch.6 (one-line headers) produce zero.
The header does not visibly break on the page (the overflow is absorbed at shipout), so this is
log hygiene plus a small risk of a 14.5 pt vertical shift; still worth clearing.
Direction: same short-title fix as M3 collapses the header to one line and removes all 30 warnings;
alternatively increase `\headheight`.

**m7. Italic "one-hot" bleeds ~15 pt into the right margin, p.49.**
Build log: "Overfull \hbox (15.13911pt too wide) ... lines 173-174". On the render the italic
"one-hot" at a line end crosses the text-block edge (`_history/_review_v1/hi/p049_rightedge.png`). Does not
reach the page edge; visible only on close inspection.
Direction: rephrase the line or allow a discretionary hyphen so the italic token breaks cleanly.

**m8. p.67 is a float-only page (Table 9 + Figure 6 + Table 10 stacked).**
Build log: "Text page 67 contains only floats." p.66 is full body text ending "Figure 6 shows the
same separability contrast graphically"; the three floats then collide onto p.67. All three sit
within ~1 page of their first reference (Table 9 and Fig 6 referenced on p.66, Table 10 on p.68),
so placement is acceptable, but a page with zero body text between two full text pages reads as a
gap.
Direction: let one float (e.g. Table 9, the smallest) float earlier or nudge with `[tbp]` so p.67
carries at least a few body lines; low priority.

**m9. In-figure text below body size in the CBIC/CoUrb figures (Fig 1 p.33, Fig 2 p.46, Fig 3 p.51).**
Box labels, axis ticks, and legends are visibly smaller than ~80% of the 12 pt body (WRITING_LAW §5
floor). The MobiWac figures (pp.60,62,67,68) meet the bar. Bundled with the redraws in M1/M2/M4.

### NIT

**n10. Title placeholders still present, pp.1, 3, 4.** "[TITLE — OPEN DECISION NORTH_STAR §5.8]"
on the cover and above the Resumo/Abstract. This is a known open decision (CLAUDE.md §2 open #1),
not a defect, but it MUST be resolved before the banca build front matter ships (target ~Jul 23).
Flagged so it is not forgotten.

**n11. Approval-sheet placeholder, p.2.** "[Approval sheet placeholder — PPG signature-page model
is inserted here for the defense; signed version replaces it afterward]" — expected for the pre-
defense build; confirm the real signature page is inserted for the deposit.

## Per-chapter consistency matrix

| Chapter | Figure style | Table style | Caption style |
|---|---|---|---|
| Ch.2 Fundamentals | (only Table 1) | booktabs, caption above (OK); **T1 overflows margin, M5** | consistent |
| Ch.3 CBIC | **saturated flowchart, small in-fig text (drift, M4/m9)** | booktabs, caption above, bold = better-of-two (rule in caption) | consistent |
| Ch.4 CoUrb | **saturated flowchart + Portuguese labels (M1); Fig 3 color-only (M2)** | booktabs, caption above, bold = best-of-three (rule in caption) | consistent |
| Ch.5 MobiWac | muted/refined, English, grayscale-safe (the bar) | booktabs, caption above, bold = statistical significance + ↑/≈ legend | consistent |
| Ch.6 + apx | (errata tables only) | booktabs two-column defect/correction tables, caption above | consistent |

Reading: **caption style CONSISTENT** across the book; **table style CONSISTENT** (booktabs, no
vertical rules, caption-above everywhere) with legitimate per-chapter bold-rule differences, each
declared in its own caption (MobiWac's significance-bold is a required honesty device, not drift);
**figure style DRIFTS** — Ch.3/Ch.4 diagrams are a saturated, mutually-inconsistent flowchart look
(Ch.4 additionally Portuguese), while Ch.5 is a refined English house style. Fixing M1/M2/M4 closes
the only real consistency gap.

## Best pages (the bar for the rest)

- **p.67-68 (MobiWac results).** Table 9 and Table 10: booktabs, caption above, mean with subscript
  fold-sd, bold marking statistical significance, ↑/≈ region symbols with a footnote legend, a
  clarifying footnote on the 26.56 coincidence. Figure 6 and Figure 7 bar charts: dark-vs-light
  encoding PLUS a numeric value label on every bar, so they survive grayscale; the ±2 pp band is
  a shaded region, not a color. This is exactly the presentation law realized.
- **p.20 Table 1 (lineage), content.** The DGI -> HGI -> MTLnet -> ST-MTLNet -> Check2HGI -> joint
  model progression with a "What it added" column and per-row chapter/reference pointers is the
  clearest single object in the book (fix only its width, M5).
- **p.60, p.62 (MobiWac diagrams).** Self-contained, English, muted palette, italic side-notes; the
  "one model, one forward pass, two predictions" framing lands visually. Adopt as house style.
- **p.36 (Table 2) and p.52 (Table 6).** Clean multi-block results tables, fit the block, uniform
  formatting, lead sentence before each.

## What holds / reads well (do not touch)

- Booktabs discipline is total: no vertical rules anywhere; captions above every table and below
  every figure (fixes the Viegas inconsistency, as WRITING_LAW §5 intends).
- Captions are self-contained and interpretive (2-4 sentences, elements named, reading
  instructions and legends included).
- No undefined or multiply-defined references in the whole build.
- Both build front matters are correct: defense build (cover -> Resumo -> Abstract -> LoF -> LoT ->
  abbreviations -> Contents) and final build (lists -> sumário -> body starting p.11), page numbers
  top-right arabic throughout.
- Only 2 overfull hboxes in an 87-page book, both localized (M5, m7); the 30 vboxes share one root
  cause (m6). This is a tidy log for a three-venue re-typeset.

## Open questions for the author (only you can answer)

1. Are Figures 1, 2, 3 (CBIC/CoUrb) regenerable from source (matplotlib/draw.io/TikZ), or are they
   fixed bitmaps? The M1/M2/M4 fixes are cheap if regenerable, a redraw job if not. This decides
   the effort, not the finding.
2. Do you want to keep the "Article N:" prefix in chapter titles? It is a style choice (out of my
   scope), but dropping it or supplying a short title would shorten the titles and resolve M3 + m6
   at once.
3. Bolding rules differ per chapter (better-of-two / best-of-three / statistical significance). Each
   is declared in its own caption, so I read it as intentional and correct, not drift. Confirm you
   want them to stay per-chapter rather than harmonized. (Content truth is 06/07's call, not mine.)

## Out-of-scope handoffs (one line each)

- The "Article 1/2/3:" title phrasing and the bold-rule semantics are content/style decisions for
  03/06/07, not visual — flagged above only where they drive a layout symptom.
- Caption CONTENT truthfulness (e.g. whether "red"/"orange" in the Fig 3 caption still matches the
  figure after a re-encode) must be re-checked by 06/07 after any figure regeneration.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
