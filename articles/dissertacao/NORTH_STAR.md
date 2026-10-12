# NORTH_STAR.md — the thesis, the arc, and the chapter map

> 🔴 **HÁ DOIS `NORTH_STAR.md` NESTE REPOSITÓRIO, E SÃO DOCUMENTOS DIFERENTES.**
>
> | | é | fala de |
> |---|---|---|
> | **este** — `articles/dissertacao/NORTH_STAR.md` | a **tese**, o arco e o mapa dos capítulos | o que a dissertação argumenta |
> | o irmão — `docs/NORTH_STAR.md` | a **receita campeã** de MTL (`DEFAULT_CANON`) | como se treina o modelo |
>
> Nenhum dos dois substitui o outro e um `grep` por `NORTH_STAR.md` encontra os dois. **Confirme o
> caminho antes de medir**: a 2026-09-08 uma sessão mediu o do `docs/` para responder a uma pergunta
> sobre este, concluiu "zero ocorrências", e escreveu essa medição num guarda — que passou a mandar
> apagar frases correctamente tarjadas. Não é uma busca que não podia encontrar: é **a busca certa no
> sítio errado**.
>
> Contado no dia: **241** referências a `NORTH_STAR.md` sem caminho, contra 67 qualificadas.


> The single place that says **what this dissertation argues and how the chapters deliver it**.
> Companion to [`CLAUDE.md`](CLAUDE.md) (state + ledger) and [`archive/PLAN.md`](archive/PLAN.md) (schedule).
> Sources for every factual statement here: the three paper folders (`articles/CBIC___MTL/`,
> `articles/CoUrb_2026/`, `articles/[mobiwac]/`), audited 2026-07-18.

---

> ## ⚠ BANNER 2026-08-20 — O VEREDITO ABAIXO ESTA SUPERADO EM QUATRO PONTOS
>
> Este documento foi escrito antes da geracao **v18**, que fechou um vazamento de rotulo no grafo
> de visitas consecutivas (valia **28,63 macro-F1** em Alabama). O veredito que ele descreve e o de
> antes. **O ladder entregue e este:**
>
> | eixo | veredito ENTREGUE |
> |---|---|
> | next-category | **supera em Florida apenas** (+0,19, Holm *p* 0,011). As outras cinco diferencas sao **nao resolvidas** — nunca "em todos", nunca "empata" |
> | next-region | **nao-inferior nos seis** (TOST, margem registrada de 2 pontos), com **Texas +1,21** e **California +1,06** superando |
>
> **Onde aparecer** `+28…+40 macro-F1`, `category everywhere` ou `region at four of six`, e a tese
> de quando o arco foi desenhado — **nao o resultado entregue** (a faixa real e **+0,23…+2,81**, e a
> categoria supera **so em Florida**; corrigido 2026-10-02, dizia +6,29, de uma celula de Istambul
> nao pareada — `docs/results/closing_data/v18/istanbul_pair/`). Fica marcado `[SUPERADO 2026-08-20]` onde aparece, porque
> reescrever o corpo apagaria o registro de qual era a tese na altura — mas **nenhuma dessas frases
> pode ser copiada para prosa nova**.
>
> ⚠ E numero pre-v18, **com vazamento**: nao e' uma tese anterior que foi revista, e' uma geracao
> que foi invalidada.
>
> *(Este aviso apontava por numero de linha — 26, 175, 330, 394 — e o texto ja nao estava la; a
> linha que o carregava sem marcador nenhum era outra. Ponteiro por numero de linha apodrece;
> por conteudo, nao. Corrigido 2026-08-28.)*
>
> Fonte do ladder entregue: `src/tables/mobiwac/results.tex` e
> `wrapup/evidence/ladder_recompute.json`. Regra de redacao: `WRITING_LAW.md` §3.
> Mapa completo de versoes: `CLAUDE.md` §0.

---

## 1 · The research question (one sentence, the whole document answers it)

> **Does multi-task learning help point-of-interest prediction (next category + next region),
> and what does the answer depend on?**

*Task-name mapping (needed to read the older papers):* CBIC and CoUrb call their sequential task
"next-POI prediction", but the label they predict is the **category of the next POI** — i.e., the
canonical **next category** task (WRITING_LAW §2). No chapter predicts the exact **next place**;
the scope statement in §1.4 holds for all three. MobiWac adds **next region** as the second task.

The dissertation's answer, delivered across three papers:

> **The representation is the dominant factor.** With a place-level embedding and naive hard
> sharing, MTL does not beat single-task models (CBIC). Decomposing and enriching the input
> representation moves the needle more than any architecture change (CoUrb). With a
> **check-in-level representation** and the right sharing topology, **one joint model finally
> outperforms both dedicated single-task models** — category everywhere, region at four of six
> `[SUPERADO 2026-08-20 — ver o banner no topo: categoria so em Florida; regiao nao-inferior nos seis]`
> datasets with statistical non-inferiority at the other two (MobiWac).

This is a rare, honest arc: a published negative result, its diagnosis, and its resolution —
the Introdução Geral must present it exactly that way (a correction trail, not three stapled
papers).

## 2 · The arc (evidence-checked 2026-07-18)

> Numbers in this section are **orientation only** — before any of them enters dissertation
> text, re-verify against the chapter's source of truth (AGENT_GUARDRAILS §2 N1): the board for
> MobiWac, the published tables + audited errata for CBIC/CoUrb.

| # | Paper | Year/venue | Language | 1st author | Status | Role in the arc |
|---|---|---|---|---|---|---|
| 1 | **CBIC** — *An Investigation into Multi-Task Learning for Point-of-Interest Category Classification and Next-POI Prediction* | CBIC 2025 | EN | **Vitor** | **Published** — DOI `10.21528/CBIC2025-1191324` (verified 2026-07-18; **satisfies Art. 21**) | **The starting point.** First unified MTL model (MTLnet: DGI embeddings + FiLM + hard sharing + Nash-MTL). Honest null result: MTL ≈ STL at higher cost. Closes hypothesizing that the shared **representation may not be rich enough** — the thread the rest pulls. |
| 2 | **CoUrb** — *ST-MTLNet: Representações Espaço-Temporais de Pontos de Interesse para Aprendizado Multitarefa* | CoUrb/SBRC 2026 (presented 2026-05-25) | PT | Tarik S. Paiva (**Vitor 2nd**, presenter) | **Published** — DOI `10.5753/courb.2026.22960`, Anais do CoUrb 2026, pp. 323–336 (verified 2026-07-18) | **The diagnosis.** Keeps MTLnet unchanged; replaces the monolithic 64-d DGI input with decomposed spatial+temporal+categorical encoders (192-d). Category F1 up +20.2…+22.0 pp per state (FL/CA/TX; audited means, `slides/judge_feedback.md`) — **the representation, not the architecture, is the bottleneck.** |
| 3 | **MobiWac** — *Predicting the Next Category and Region of a Visit: A Check-in-Level Multi-Task Study on Mobility Data* | MobiWac 2026 | EN | **Vitor** | **Accepted for publication** (2026-08-26; EDAS #1571313639, uploaded 2026-07-09) `[corrigido 2026-10-02: dizia "Submitted, under review"]` | **The resolution.** Check2HGI check-in-level representation (+28…+40 macro-F1 over place-level on next-category) `[SUPERADO 2026-08-20 — faixa real +0,23…+2,81; numero pre-v18, com vazamento]` + cross-attention joint model: category outperforms the dedicated model at all six datasets (+5.3…+9.4) `[SUPERADO 2026-08-20 — categoria supera so em Florida (+0,19, Holm p 0,011); as outras cinco sao nao resolvidas]`, region outperforms at Istanbul/FL/TX/CA and matches (TOST ±2 pp) at AL/AZ. n=20, Holm, user-disjoint CV, leak audit null. |

**BRACIS 2026** (*Substrate Carries, Architecture Pays*, rejected 2026-06-08) is **not a
chapter**: unpublished, absorbed into MobiWac, and its headline claim (MTL pays 7–17 pp on
region) was **corrected** by MobiWac (fp16-harness artifact + older protocol). In the frame it
appears only as an intermediate iteration whose reviewer objections (the leak allegation)
MobiWac answers with the A4 audit. Including it as a chapter would be redundant AND
self-contradictory.

### ✅ Order SETTLED (author, 2026-07-18): CBIC → CoUrb → MobiWac

The author confirmed the chronological = intellectual order after the evidence check (CBIC is
2025 and CoUrb explicitly cites CBIC's MTLNet as the baseline it improves). The initial
"CoUrb → CBIC" listing was a slip; the narrative "first MTL model → representation diagnosis →
final form" maps 1:1 onto CBIC → CoUrb → MobiWac.

## 3 · Chapter map (Viegas-pattern, adapted — see `exemples/viegas/VIEGAS_ANALYSIS.md`)
*(A pasta `exemples/` foi apagada em 28/08/2026 na limpeza; o conteudo esta em `~/Backups/dissertacao_exemples_2026-08-20.tgz`, backup verificado.)*

```
PRE-TEXTUAL (defense build only; the final AcademicoPG upload starts at the lists — TEMPLATE.md)

1  INTRODUCTION                        [EN — the "Introdução Geral" of UFV §2.6]
   1.1 Context and motivation          (LBSNs, mobility prediction, the two tasks)
   1.2 Research problem                (bold inline research question, §1 above)
   1.3 Objectives and contributions    (objectives 1:1 with chapters, Viegas device)
   1.4 Scope and assumptions           (Gowalla+Istanbul; category/region, NOT next-place;
                                        observational check-ins; single-model constraint —
                                        split from evaluation-time limitations, Viegas §1.3)
   1.5 Dissertation organization       (the "magic sentence" declaring the coletânea format +
                                        per-chapter venue/status bullets)
2  FUNDAMENTALS                        [thin; de-duplicates background across the papers]
   2.1 POI prediction tasks            (category, region, next-place — kept distinct)
   2.2 Representations for mobility    (DGI → HGI → the check-in level; embeddings glossed)
   2.3 Multi-task learning             (hard/soft sharing, negative transfer, balancers)
   2.4 Datasets and evaluation         (Gowalla states, Istanbul; macro-F1, Acc@10, CV protocol)
   2.5 Relevance                       (why these fundamentals matter here — Viegas device;
                                        ends with the "pressing need" hinge paragraph that
                                        pre-motivates the three paper chapters)
3  ARTICLE 1 — CBIC                    [EN, re-typeset; the first MTL model, honest null]
4  ARTICLE 2 — CoUrb / ST-MTLNet       [language: open decision #3; representation diagnosis]
5  ARTICLE 3 — MobiWac                 [EN, re-typeset; the check-in-level resolution]
6  CONCLUSION                          [EN — the "Conclusão Geral"]
   6.1 Summary of contributions        (one paragraph per chapter, topic-sentence-led)
   6.2 Limitations                     (cross-cutting, concrete: dataset vintage, 7-category
                                        taxonomy, transductive-representation caveat, no
                                        next-place prediction)
   6.3 Future work                     (each item tied to a §6.2 limitation)
   6.4 Final remarks
BIBLIOGRAPHY                           [single global, renumbered — open decision #5]
APPENDIX A — Other scientific contributions
                                       [the research platform / ETL contribution ONLY.
                                        The BRACIS-iteration section was REMOVED
                                        2026-07-27 by author ruling — see §5.11;
                                        the instruction below is superseded, kept for
                                        the trail. Do not reinstate without a new ruling.
                                        SUPERSEDED: "BRACIS submission as intermediate
                                        iteration; report_orientador is internal — out"]
APPENDIX B — Errata to the reproduced articles
                                       [only if errata policy #7 = "fix + note"; lists every
                                        departure from the published texts]
```

**Bridging devices (from Viegas, mandatory):** each later paper-chapter gets a short Related-Work
subsection recapping the previous chapter's artifact by name (Ch.4 gets "The MTLnet framework",
Ch.5 gets both); the general Introduction owns the explicit arc narrative; chapters cite each
other's papers by bibliography entry.

**The time-capsule rule (this arc's special need):** CBIC's conclusion ("MTL does not help") and
CoUrb's protocol are **time-indexed** — presented as "the conclusion of the time, for that
configuration". The Introduction and each chapter's short preface (one italic paragraph before
§N.1, stating venue, status, and what later chapters revise) carry this framing. Never let a
superseded number or claim read as the project's current state.

## 4 · Per-chapter adaptation notes + known errata (do NOT lose these)

### Ch.3 — CBIC
- Re-typeset from `articles/CBIC___MTL/` (IEEE 2-col → dissertation 1-col), "this paper" → "this
  chapter", renumber sections/figures.
- **Errata to handle (open decision #7):** (a) unfilled dataset placeholders in results.tex
  (`N_users`, `N_poi`, `N_checkins` never inserted). **RESOLVED (author ruling 2026-07-24):** the
  CoUrb published Florida row is now the **source of record** for Ch.3 as well as Ch.4:
  **20,301 users / 65,009 POIs / 990,518 check-ins** (`tabela_dataset.tex`). Rationale recorded in
  `src_utils/evidence/cbic_recompute_result.md`:1-10. The `filtrado.csv` artifact behind the earlier
  recompute (10,460 / 64,454 / 960,520) comes from a prior ETL no longer in use; the CBIC paper
  never published these three statistics, so no published value is overridden, and one corpus
  figure now serves both chapters. The `[VERIFY]` flag is cleared, and the shipped text carries the
  ruling (`src/chapters/3_cbic.tex`:246, `src/chapters/4_courb.tex`:238).
  *Superseded history (kept for the trail, do not act on it):* until 2026-07-24 the sanctioned
  fail-closed path was a repo-committed recompute over the CBIC-era Florida pipeline, with the
  CoUrb row admitted as a **cross-check only, not a source**, on the grounds that its filtering
  might differ;
  (b) prose says "almost four times more wall time", table says 80.88 s vs 34.97 s = 2.3×;
  (c) prose says MFLOPs "roughly double", table contradicts; (d) three documented citation errors
  (POI-RGNN wrong paper: use capanema2023poirgnn; HMRM author names; GAT cite the ICLR version);
  (e) broken cross-ref label semantics (`sec:method:single_task_heads` on the Dataset subsection);
  (f) typo "spatio-tegm mporal" in basis.tex.
- **Claim discipline:** Nash-MTL "consistently better" predates the solver-bug discovery
  (NashMTL collapsing to [1,1]; repo memory 2026-04-10) — do not amplify in the frame; the
  chapter preface may note the later finding. "MTL does not help" is time-indexed (§3 rule).

### Ch.4 — CoUrb
- Source `articles/CoUrb_2026/` (SBC format, PT). Language per open decision #3.
- **Errata to handle:** the paper text says "16/21 (76%)" wins on its sequential task (its
  "next-POI prediction" = canonical **next category**, §1 mapping) and "+20–24 pp" category
  gains; the internal audit (slides/judge_feedback.md) recounted **15/21 strict wins + 1
  technical tie** and per-state means **+20.2…+22.0 pp** (the deck was corrected; the .tex was
  not). The chapter must use the audited numbers (or reproduce verbatim + errata note —
  decision #7).
- **Honesty items:** split is stratified by sample, not user-disjoint (weaker than Ch.5's
  protocol — say so, it strengthens the arc). [VERIFIED FIRSTHAND 2026-07-23 from the CoUrb
  codebase (author-provided copy, /Users/vitor/Desktop/mestrado/temp/tarik-new):
  `PoiMtlNet_Novo/src/etl/mtl/create_fold.py` L190–199 reads `userid`, then DROPS the column and
  splits with plain `StratifiedKFold(n_splits, shuffle=True)` on sample rows stratified by class
  (L225–228); `src/etl/next/fold.py` L19+L34 likewise; no group-aware splitter exists anywhere in
  the project code. A user's windows can therefore span train and test. UW-3 closed.];
  ~~Nash-MTL caveat as in Ch.3~~ **REVOKED by author ruling 2026-07-27** (the PENDENCIAS of that date, item 2.3 — the tracker was rewritten in round 6 and renumbered again 2026-07-29, so that number no longer resolves; the ruling is quoted verbatim here because the quote outlives the coordinate. Option A:
  "vamos manter como estar, de fato e um erro, mas nao e algo que afeta o escopo do projeto de forma
  critica"). No caveat and no errata for the optimizer-preference claim in Ch.3 or Ch.4. Scope of what
  this gives up, so the decision stays auditable: only the optimizer-PREFERENCE claim. Ch.3's main
  result (MTL at parity with single-task) does not depend on which balancer was active, and Ch.5 does
  not use Nash at all. Verified 2026-07-27 that no frame chapter amplifies the preference: Ch.2's
  mention is a neutral method description, and Ch.4's preface carries no Nash sentence.
  No external baselines;
  update the `silva2025mtlnet` bib entry (venue name wrong: says "Brazilian Conference on
  Intelligent Systems (CBIC)"; note "Submetido" stale).
- **Authorship note:** state Vitor's contribution (baseline model MTLnet is his 1st-author work;
  he presented the paper) — wherever the Comissão wants it (organization section or preface).

### Ch.5 — MobiWac
- Source: `articles/[mobiwac]/src/` (current 9-page working build; open decision #4). IEEE 2-col
  → dissertation 1-col; keep the paper's GLOSSARY-governed prose (it is already the writing law).
- **Claim discipline is inherited verbatim** from `articles/[mobiwac]/` (CLAUDE §3 ledger +
  PAPER_PLAN §3 whitelist): region verbs bound to tests ("outperforms" Istanbul/FL/TX/CA,   % [SUPERADO 2026-08-20: regiao supera so em TX e CA]
  "matches" AL/AZ, never upgrade AZ); scaling claim scoped to the five U.S. states; cascade is
  "a tie at equal cost"; never-cite lists (STAN v4-collapse numbers, ReHDM v2 row, VOID cells).
- Status wording: "submitted to MobiWac 2026, under review" — never "published/accepted".
  `[SUPERADO 2026-10-02 — aceito a 2026-08-26; a redacao entregue e "accepted for publication" (AUT-35, commit e1f9b8c0)]`
- The dissertation gains space the paper lacked: restore the compressed leak-audit prose (§5.2
  floor; the A4 record lives at `docs/studies/pre_freeze_gates/A4_RESULTS.md` +
  `docs/results/pre_freeze_gates/a4/`), the statistical protocol detail, and the fp16→fp32
  harness lesson if the advisor wants the fuller record (those two live under
  `docs/studies/closing_data/`).

## 4b · Absorbed from `noth_star_consideration.md` (author notes, 2026-07-25)

That file held three author notes. It is archived at
`src_utils/_history/_archive/reviews_v1/noth_star_consideration.md`; this section carries what had not yet
landed, so nothing is lost by the archive. Checked point by point against the source on 2026-07-27.

**Point 1a, the arc — ABSORBED.** The three-paper arc it describes (CBIC's first attempt, the
representation diagnosed as the bottleneck, MobiWac's resolution) is the arc §2 already states, and
Chapters 1 and 6 carry it.

**Point 1b, dropping the MTL optimizers as a maturity signal — ABSORBED.** Chapter 5 states the
conservative-by-design position (`5_mobiwac.tex`, the limitations section — the pointer said `:179` until 2026-09-08 and the file has 65 lines) and Chapter 6 names the orthogonal-gradient
finding (`6_conclusion.tex:180`). Round 5 strengthened it: the chapter now reports the full
nineteen-balancer screen rather than implying a two-optimizer test.

**Point 1c, why embeddings and not raw inputs — NOT ABSORBED. This is a live open item.** Grep for
"raw input", "raw feature", "one-hot input" and "learned end-to-end" across Chapters 1 and 2 returns
nothing. The author's observation is correct and it is a question a committee can reasonably ask: in
consolidated deep-learning practice the first layers of a raw-input model construct the latent space
anyway, so a reader may ask why the representation is built separately here rather than learned
inside the model. The answer this document can defend is on the record and does not need new
experiments: the place-level and check-in-level representations are trained by an unsupervised
objective over a graph the prediction model never sees, which is what makes the leak audits and the
label-history benchmark of Appendix D meaningful at all. That is a paragraph in Section 2.2, next to
the place-level-to-check-in-level move. **Not drafted, because the author asked for the literature to
be searched and the point strengthened, which is a grounded-citation task rather than a rewrite.**

**Point 2, mining the repository for the fundamentals — ABSORBED.** Done, including the prior
Claude Science survey under `science/`. The known defects of that survey are recorded in this file.

**Point 3, broadening the application examples beyond mobility — PARTLY ABSORBED.** The introduction
carries one example outside pure mobility. The author's point stands that CBIC and CoUrb contain
further examples the frame could use, and that MobiWac's mobility-only framing was a venue
constraint rather than a scope limit. Cheap to extend, and it is frame prose, so no errata cost.

## 5 · Decision record (status per item; settled rulings mirrored in CLAUDE.md §2 ledger)

> **v1-assembly status (2026-07-24, updated after corrections round 2):** every settled decision
> below was realized in the assembled `src/` tree (order, CoUrb full EN chapter, numeric bib, thin
> fundamentals, errata policy, AI disclosure). Live status after round 2:
> **#4 (MobiWac re-sync)** — ✅ done (no drift at the Phase-8 re-sync); additionally, the B.1 CBIC
> misattribution was corrected in BOTH Ch.5 and the version-of-record `[mobiwac]/src/` this round
> (author-authorized, logged in the MobiWac ERRATA + Appendix B). **#8 (title)** — now SET to the
> working option (*Multi-Task Learning for Point-of-Interest Classification and Prediction Tasks: …*) live at all echo points, with
> the three alternates commented in `src/0_main.tex`; the final call rests with the advisor, so it
> is "decided for now," not closed. **CBIC dataset counts** — recomputed this round via the
> sanctioned Gowalla ETL (`src/src_utils/evidence/cbic_recompute_result.md`), pending author confirmation.
> Nothing here was reopened.

1. **Order** — ✅ SETTLED (author, 2026-07-18): CBIC → CoUrb → MobiWac (§2 above).
2. **CoUrb inclusion** — ✅ SETTLED (author, 2026-07-18): full chapter. Norms check: nothing in
   Normas §2.3/§2.6 or the regimento requires first authorship (articles need only be pertinent
   to the research and published/accepted/submitted; CoUrb is published with DOI). Advisor/
   Comissão sign-off still recommended (unregulated; the Viegas precedent used 1st-author works
   only). The chapter carries a contribution note (Vitor: 2nd author, presenter, author of the
   baseline MTLnet). Fallback (only if the Comissão objects): CoUrb summarized in the frame and
   the coletânea proceeds with CBIC + MobiWac.
3. **CoUrb language** — ✅ SETTLED (author, 2026-07-18): translate to EN (author launches the
   translation agent; AGENT_GUARDRAILS L5 fidelity gate mandatory). The chapter states it is a
   translated reproduction, citing the original DOI. Courtesy: inform Tarik.
4. **MobiWac version** — ✅ SETTLED (author, 2026-07-18): the current working build in
   `articles/[mobiwac]/src/` ("the last one in the src"); the author is refining it in parallel,
   so **re-sync the chapter before the final gate pass** (single-source rule).
5. **Bibliography** — ✅ SETTLED (author, 2026-07-18): single global, Viegas-style numeric.
6. **Fundamentals chapter** — ✅ thin (≈8–12 pages), reusing `docs/context/` and the papers' own
   background sections; it is what makes three differently-shaped papers read as one document.
7. **Errata policy** — DEFAULT ADOPTED (confirm with advisor): fix in the re-typeset chapters +
   one frame sentence ("chapters were reformatted from the originals; typographical and
   tabulation errata corrected, listed in Appendix B"), never silently.
   - **Errata registry (2026-07-21):** the per-article defects are now catalogued in an
     `ERRATA.md` inside each original article folder — `articles/CBIC___MTL/ERRATA.md`,
     `articles/CoUrb_2026/ERRATA.md`, `articles/[mobiwac]/ERRATA.md`. The published article
     records are NOT edited. During adaptation the fixes are applied **silently in the
     dissertation text and its global bib** (author ruling 2026-07-21), and the whole set is
     listed once in Appendix B. Add future points to the relevant folder's `ERRATA.md`.
     The CBIC set includes the four inherited errata (POI-RGNN wrong paper -> `capanema2023poirgnn`;
     HMRM `chen2020modeling` author/type/DOI; GAT -> ICLR 2018; plus `misra2016cross` and
     `zhang2021survey` DOI corrections, `church2017word2vec` -> `mikolov2013word2vec`,
     `yu2019mmoe` confirm-or-drop, and the DGI/Nash key consolidations); CoUrb includes the
     audited win-count / pp-gain numbers and the `silva2025mtlnet` venue fix.
8. **Title of the dissertation** — 🔵 SET FOR NOW (round 2, 2026-07-24), pending the advisor's
   final call. Live at all echo points (folha de rosto, Resumo + Abstract headers, pdftitle):
   - **SELECTED:** *Multi-Task Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the Check-in-Level Representation*
   - Alternates kept commented in `src/0_main.tex` for the advisor conversation (the newer
     2026-07-23 author decision block in `src/chapters/1_introduction.tex` supersedes the earlier
     §5.8 shortlist; the commented set is the current candidate list).
9. **AI-use disclosure** — ✅ SETTLED (author, 2026-07-18): proceed. Recommended placement: a
   short appendix ("AI-use disclosure"), which survives both build modes; drafted from git
   provenance (AGENT_GUARDRAILS §6).
10. **Art. 21 path** — ✅ RESOLVED IN SUBSTANCE: CBIC DOI `10.21528/CBIC2025-1191324` verified
    2026-07-18 (event publication satisfies the new Art. 21 §1 under either reading). Remaining
    ACTION (PLAN Day 0): file the comprovante with the PPGCC secretariat + confirm the operative
    checklist. Details: [`UFV_COMPLIANCE.md`](UFV_COMPLIANCE.md) §3.
11. **The BRACIS iteration is not disclosed in the dissertation** — ✅ SETTLED (author,
    2026-07-27). Appendix A §A.2 ("An earlier unpublished iteration") is **removed**. The
    author's grounds, in his words: less detail makes the reading less complex; the reader is
    motivated by the final result, the methodology, and the conclusion, and the trail of errors
    is not constructive for him; and this is not concealment from the banca, because the text
    changed substantially after the rejection and reworking a manuscript after a reject is
    common practice, with the conclusion unchanged.
    - **What this supersedes.** §3's Appendix A scope line (annotated in place above) and
      **AGENT_GUARDRAILS C4**, which mandates the containment device ("BRACIS material may
      inform prose but is cited only as 'an earlier unpublished iteration'"). C4's *prohibition*
      half survives and is now the whole rule: no BRACIS result, number, or claim appears
      anywhere in the dissertation, and its region-cost claim is never reissued. C4's
      *disclosure* half is void. **AGENT_GUARDRAILS.md still carries the old wording and needs
      the matching edit** (not applied here; that file was outside the editing scope of the
      session that made this change).
    - **Consequence the author flagged himself**, and the sweep result: no prose anywhere in the
      document asserts a correction relative to that manuscript. Every "earlier"/"corrected"
      passage checked (`5_mobiwac.tex`:105, :145, :202-203; `6_conclusion.tex`:156;
      `1_introduction.tex`:139; all of `apx_b_errata.tex` §B.3) refers to CBIC, to CoUrb, to the
      submitted MobiWac manuscript, or to a development-time data preparation, and each names
      its own antecedent. Nothing was left pointing at the deleted section.
    - **One orphan remains, outside the editing scope:** the `BRACIS` entry in the List of
      Abbreviations (`src/0_main.tex`:346) and its comment (:343, "BRACIS appears in Appendix A
      only"). The acronym now appears nowhere in prose, so both lines should go; GLOSSARY §5
      lists BRACIS as "(appendix only)" and needs the same treatment.

## 6 · Story spine (the settled narrative — G0 outline for the frame chapters)

> This section is the **approved storytelling**. Tomorrow's drafting agents expand it; they do
> not reinvent it. Chapter-level claims here are covered by AGENT_GUARDRAILS C2 (frame-claim
> sign-off): the author approved this spine on 2026-07-18; anything beyond it needs new
> sign-off.

### Ch.1 Introduction — the beats, in order

1. **Context funnel** (≤3 paragraphs): LBSNs produce check-in traces → anticipating *what kind
   of place* (next category) and *where* (next region) enables mobility-aware services → the
   natural engineering wish: **one model for both tasks** (multi-task learning), instead of one
   dedicated model per task.
2. **The tension**: MTL promises shared structure and operational simplicity (one artifact to
   train, deploy, and maintain; one forward pass for both predictions), but naive sharing can
   hurt (negative transfer); whether it helps for POI prediction, and what the answer depends
   on, was unresolved when this research started. [F3 guard: do NOT promise lower compute cost —
   CBIC's joint model cost more to train, and MobiWac's is larger than the two dedicated models
   combined (~4.2M vs 1.1M params at Alabama, disclosed as cost). The wish the arc actually
   delivers is operational; if cost is raised here, the Conclusion must narrate the
   redefinition explicitly.]
3. **Research question**, bold inline (§1 wording).
4. **The journey as the contribution** (the honest-arc paragraph): a first joint model that did
   NOT beat dedicated models (CBIC, published); the diagnosis that the input representation,
   not the sharing architecture, was the bottleneck (CoUrb, published); and the resolution — a
   check-in-level representation plus a redesigned sharing topology under which ONE joint model
   outperforms both dedicated models (MobiWac, submitted). [SUPERADO 2026-08-20 — ver banner] State plainly that the dissertation
   presents the negative result as a finding, its diagnosis as the turning point, and the final
   model as the payoff.
   [SIGNED-OFF ADDITIONS to this beat (AVAL rounds 1-2, 2026-07-22) — the arc paragraph must
   also carry:
   (a) the task-pair acknowledgment (Items 1/3): the pair evolved (CBIC/CoUrb: static category
       classification + next category; MobiWac: next category + next region) — named plainly,
       never narrated as one experiment on a constant pair;
   (b) the three-legged task-choice defense (N1): utility (what a service can act on) +
       established end targets in the literature + convergence toward next place (the field's
       most-cited task; legs 1 and 3 draftable now; leg 2's comparative form stays [VERIFY]
       until an opened anchor supports it — fallback: "both are established end targets, and
       next region feeds a broader family of downstream problems");
   (c) the corollary (Item 1, corrected form): under a per-visit representation the static task
       becomes the less natural fit — "unnatural", never "incoherent" (pooling remains possible);
   (d) the N2 framing (its caution form ONLY): CBIC opened three doors and its future work
       proposed the architecture door; the dissertation took the representation door first as
       the cheapest controlled test — NEVER "CBIC's future work called for better
       representations", never foresight (F4 guard: the null stays a genuine of-its-time
       finding, not act one of a script);
   (e) the mechanism sentence (same place, different visit, same vector) framed as the
       hypothesis the journey tests.]
5. **Objectives 1:1 with chapters** (4 bullets: investigate naive MTL for the task pair;
   diagnose the representation bottleneck; design and validate a check-in-level joint model;
   consolidate the evidence under a leakage-guarded statistical protocol).
6. **Scope and assumptions** (§1.4): observational Gowalla check-ins (5 U.S. states) +
   Istanbul; tasks are next category and next region — the exact next place is NOT predicted;
   7-category taxonomy; single-model, one-forward-pass constraint for the joint model;
   design-time assumptions split from evaluation-time limitations (Ch.6).
7. **Organization** with the coletânea magic sentence + per-chapter venue/status/DOI bullets +
   the reformatting/translation/errata sentence (decision #7) + Vitor's contribution note on
   the CoUrb chapter.
8. **Contributions summary** taxonomy: Theoretical (the representation-dominance finding; the
   corrected view of MTL for POI tasks), Software (MTLnet + Check2HGI + reproducible pipeline,
   repo footnote), Empirical (the six-dataset, n=20, leakage-audited benchmark), Practical
   (one deployable model for two prediction services).

### Ch.2 Fundamentals — beats

Tasks (category / region / place, kept distinct) → representations for mobility (one-hot →
DGI/HGI place embeddings → why place-level vectors are static across visits) → MTL (hard/soft
sharing, negative transfer, balancing) → datasets + metrics + validation protocol (macro-F1,
Acc@10, user-disjoint CV, seeds) → **Relevance + the "pressing need" hinge paragraph** whose
three clauses pre-motivate Ch.3 (does naive MTL help?), Ch.4 (is the representation the
lever?), Ch.5 (what does a representation built for check-ins unlock?). Includes the
model-lineage table (GLOSSARY.md is the source).

### Ch.3/4/5 prefaces — one italic paragraph each (time-capsule device)

- Ch.3: published CBIC 2025 (DOI); conclusions are of-the-time; Ch.4–5 revise them.
- Ch.4: published CoUrb 2026 (DOI); translated reproduction; Vitor's role; protocol weaker
  than Ch.5's (sample-stratified split) — flagged, not hidden. [VERIFIED FIRSTHAND 2026-07-23
  from the CoUrb codebase: plain StratifiedKFold on samples, userid dropped before splitting —
  see §4 Ch.4 honesty items for file/line. UW-3 closed.]
  ALSO REQUIRED here (approved Item 6, one-sentence floor): "this chapter isolates the
  representation effect with MTLNet as its only baseline; it does not revisit the
  MTL-versus-single-task question, which Chapter 5 reopens."
- Ch.5: submitted to MobiWac 2026, under review `[SUPERADO 2026-10-02 — aceito a 2026-08-26]`; the arc's resolution; numbers governed by the
  paper's claim whitelist.

### Ch.6 Conclusion — beats

One sentence naming the three contributions in chapter order → per-chapter contribution
paragraphs → the consolidated answer to the research question (representation-dominant;
verbs bound to tests: category outperforms everywhere, region outperforms at 4 of 6 and   [SUPERADO 2026-08-20 — ver banner]
matches at AL/AZ) → limitations (concrete: Gowalla vintage 2009–2010, 7-category taxonomy,
transductive-representation caveat, no next-place task, single-city non-U.S. coverage,
AND [signed-off addition, 2026-07-22] the task-pair confound concession from storyline/02
§3.4: no single controlled ablation separates the representation+topology change from the
task-pair homogeneity change in the final win — CoUrb is the fixed-pair control for the
diagnosis, not for the joint win) →
future work tied 1:1 to limitations (exact next-place; newer/denser traces; inductive
representations; matured cascade coupling; AND the fixed-pair ablation under the check-in
representation — the future-work item the new limitation is tied to; pending the author's
N3 experiment decision it may instead be run pre-defense) → final remarks (one deployable
model, one forward pass, two predictions — and an honest record of how a negative result
became a method).
[N3 mechanism beats (signed off, AVAL-2): §6.4 names the negative-transfer reversal with the
cosine number's FULL scope traveling verbatim (+0.001, four seeds, three of six datasets,
measured during development on an earlier data preparation, directional conflict only, a
finding for this pair not a general rule) and explains the win as: a stronger shared trunk
(proven by the freeze control — gain survives at AL/AZ/FL, three named datasets), enabled by
cross-attention sharing between per-task streams with a private spatial path. "Sharing
stopped hurting", never "the tasks teach each other". NEVER credit the parameter count —
disclosed as cost. The author's vocabulary "knowledge gate" translates to the paper's own
sharing-by-exchange wording; "gate" is not licensed vocabulary.]
