# 07 · Claim & honesty auditor — Gate G2 (C1–C4 + the honesty law)

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e a persona de honestidade de alegacoes, portao G2 da ronda 9, corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
> visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 medidas aqui vem da
> geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta.


**Persona:** `reviewers/07_claim_honesty_auditor.md` (fresh eyes; wrote none of the text under audit,
AGENT_GUARDRAILS L6).
**Build commit:** `03b53d16`
**Volumes read (page counts as built at this commit):** `src/build/main.pdf` 102 pp (full text read
for the claim-bearing chapters: front matter pp. 2–8, Ch.2 pp. 22–27, Ch.3 pp. 28, 36, 40–43,
Ch.4 p. 44, 55, 57, Ch.5 pp. 59–60, 71–73, 77, Ch.6 pp. 78–81, Appendix C p. 93, Appendix E p. 94,
Appendix F pp. 98–101); `src/build/main_extra.pdf` 20 pp (all pages); `src/build/main_ppgc.pdf`
103 pp and `src/build/main_academico.pdf` 99 pp (front matter + full-text sweeps only, for
Resumo/Abstract parity and must-not-say containment).
**Date:** 2026-07-30 (report written 05:15 −03).
**Verdict:** **GATE FAIL** — two unlicensed-universal claims (findings B-1, B-2). Everything else in
scope is clean, and the honesty-device inventory in §4 is intact.

## Commands run

Working directory `/Users/vitor/Desktop/mestrado/ingred/articles/dissertacao` unless noted.
No build, no `make check`, no `make selftest` (per brief). Read-only apart from this file.

```
date && git log --oneline -1                      # -> 03b53d16 fix(gate): "verified in both directions" ...
ls -la src/build/*.pdf
# text extraction of all four targets, one file per volume, page-delimited:
python3 -c "import pypdfium2 as p; ... open('/tmp/<vol>.txt','w')"   # main 102, main_academico 99,
                                                                     # main_ppgc 103, main_extra 20
# vocabulary sweeps over the extracted text (regex, per page, counts + page lists):
#   beat|win|tie|Pareto|everywhere|publish|accept|BRACIS|outperform|match|TOST|non-inferior|
#   submitted|under review|cost grows|cardinality|-2.4|Pareto-dominat|free gain
# source-side sweeps, comments stripped per AGENT_GUARDRAILS §4b V4:
for f in $(find src -name '*.tex' -not -path 'src/build/*'); do \
    grep -vn '^[[:space:]]*%' "$f" | grep -n '<pattern>' | sed "s|^|$f:|"; done
grep -n 'everywhere' src/chapters/6_conclusion.tex src/chapters/2_fundamentals.tex
grep -rn 'costs nothing' --include=*.tex src | grep -v build
grep -rn 'consistently' src/chapters/{1_introduction,2_fundamentals,3_cbic,6_conclusion}.tex
grep -rn 'From Representations to a Single Joint Model' --include=*.tex src | grep -v build
# Resumo/Abstract parity: whitespace-normalized page comparison, main p2/p3 vs main_ppgc p3/p4
```

**Instrument caveats, stated because the claims below rest on them (V2/V3).** The page sweeps run on
`pypdfium2` text extraction, which flattens soft hyphens (the PDF renders `single-\ntask` as
`single￾task`); every quote below was re-read in the extracted page text AND, where a source location
is given, against the `.tex` line. Source-side `grep`s strip comment lines from the **file** before
matching, so provenance comments that quote the searched strings are not counted; that is why the
`% they were unreported everywhere` line at `2_fundamentals.tex:688` is excluded from the
`everywhere` count. The sweeps cannot see claims phrased without any of the swept tokens — an
un-swept paraphrase of a banned claim would pass, and I did not read Chapters 3, 4 and 5 line by
line (see UNFINISHED).

---

## 1 · Blockers

### BLOCKER B-1 — Appendix F asserts an unlicensed universal ("costs nothing") that the dissertation's own Alabama region cell refutes, and labels Chapter 5's topology "hard sharing"

**WHERE:** `src/build/main.pdf` p. 101 (§F.3, first consequence) · source
`src/chapters/apx_f_cosine.tex`:290–291.

**WHAT** (verbatim, PDF p. 101):

> "Orthogonality leaves them nothing to resolve. That is why hard sharing costs nothing in this
> architecture, and why Chapter 5 finds no balancer improving on a fixed loss weighting: the
> measurement explains the finding."

Same paragraph, preceding sentence (p. 101):

> "Orthogonal gradients mean neither task's update reinforces or cancels the other's on the shared
> parameters, so the trunk can serve both without either improvement being paid for by the other."

**WHY:** Two separate defects, both in scope for G2.

1. *Unlicensed universal, contradicted in-document.* "costs nothing" is an unbounded claim about the
   joint model's cost, and the dissertation measures a cost. `main.pdf` p. 73: "At Alabama, the whole
   interval lies below zero, a small but statistically significant deficit, still well within the
   two-point margin", for the region point estimate "Alabama (−0.41; −0.63 to −0.20)"; Table 10
   (p. 72) gives AL region dedicated `70.11 ±0.10` against joint `69.70 ±0.09≈`. A statistically
   significant deficit at one of six datasets is not "nothing". WRITING_LAW §3 requires every
   universal to be scoped ("Scope every universal … bare 'everywhere' never") and binds verbs to
   tests; PAPER_PLAN §3 must-NOT-say lists "beats region everywhere" / "Pareto-dominates everywhere"
   as the same offense in the other direction. The licensed mechanism sentence, from NORTH_STAR §6
   (Ch.6 N3 beats), is **"sharing stopped hurting"** — which the document already uses at p. 80 and
   which is exactly the weaker claim orthogonality supports.
2. *Architecture mislabel.* Chapter 5's model is not hard sharing. Ch.2 §2.3 (p. 22) defines the
   term: "hard parameter sharing, where the tasks use a common trunk and split only at the output
   heads". Ch.5's model, per `main.pdf` p. 79 and `src/chapters/5_mobiwac/04_method.tex`:28, has
   "per-task encoders (a small input network per task, with no shared weights)", a cross-attention
   trunk, and "a private spatial path for the region task"; Ch.1 (p. 13) states the change as
   "replacing the shared hidden layers with cross-attention between two task-specific streams". The
   appendix's own chapter title and §F.1 call the measured object "the shared cross-attention trunk"
   (`apx_f_cosine.tex`:90). Calling it hard sharing here reads as a claim that the arc's
   architectural change was unnecessary, which is not the arc.

**FIX:** Author's call on wording; the claim must come down to what is licensed and measured. A form
that keeps the mechanism and drops both defects, built only from strings already in the document:
"Orthogonality leaves them nothing to resolve. That is why sharing stopped hurting in this
architecture, and why Chapter 5 finds no balancer improving on a fixed loss weighting: the
measurement explains the finding." If the author wants to keep a cost statement, it has to carry its
scope and its exception (the AL region deficit), and it cannot be attached to "hard sharing".
Flagging rather than ruling on the preceding sentence ("without either improvement being paid for by
the other"), which has the same problem in milder form: it is defensible as a statement about the
shared parameters, not as a statement about the reported scores.

### BLOCKER B-2 — the consolidated answer (§6.2) uses bare "everywhere" and collapses the region verdict into "outperforms or matches"

**WHERE:** `src/build/main.pdf` p. 79 (§6.2, first paragraph) · source
`src/chapters/6_conclusion.tex`:106–107.

**WHAT** (verbatim, PDF p. 79):

> "With a check-in-level representation and a sharing topology built for it, yes: one model, one
> forward pass, both predictions, at quality that outperforms the dedicated models on the category
> task everywhere and outperforms or matches them on the region task."

**WHY:** WRITING_LAW §3, verbatim: *"Scope every universal: 'at all six datasets' only right after
the six are enumerated; the region-count scaling claim is scoped to the five U.S. states; bare
'everywhere' never."* This is the one live bare "everywhere" in the document (sweep: three
occurrences in `main.pdf`, at pp. 21, 27, 79; the p. 21 one is not a universal about results — "they
agree everywhere else", about two architectures — and the p. 27 one is immediately scoped, "everywhere
it is tested and on the next region at four of six datasets"). It matters most here because §6.2 is
the paragraph a reader or a committee member quotes as the dissertation's answer.

Second half, same sentence: "outperforms **or** matches them on the region task" states a disjunction
where the document has a partition — four datasets by paired superiority, two by TOST non-inferiority
within two points. It does not upgrade AZ, so it is not a C1 must-NOT-say violation, but it discards
the split that the honesty law exists to protect, and it is the only site in the frame that does:
p. 78 (§6.1 opening) has "at all six datasets and on the region task at four of the six, and is
statistically non-inferior to them, within a two-point margin (TOST), at the other two", p. 79 (§6.1,
Ch.5 paragraph) has the same with the four datasets named, and Ch.2 p. 27 has the scoped form. So the
protected headline shape is present three times and blurred once.

**FIX:** Reuse the wording the same chapter already carries two paragraphs earlier. Concretely:
"… at quality that outperforms the dedicated models on the category task at all six datasets and on
the region task at four of the six, and is statistically non-inferior to them within a two-point
margin (TOST) at the other two." That keeps the sentence's rhetorical position, removes the bare
universal, and restores the tested partition.

---

## 2 · Should-fix

### SF-1 — Ch.2 §2.3 states CBIC's null without "consistently", strengthening a negative claim beyond the published text

**WHERE:** `src/build/main.pdf` p. 24 (§2.3, last paragraph) · source
`src/chapters/2_fundamentals.tex`:569–571.

**WHAT** (verbatim, PDF p. 24):

> "Its own starting model, MTLnet, applies hard parameter sharing on a place-level embedding and does
> not outperform the dedicated single-task models, a result that holds for that configuration and
> motivates the representation argument the next chapters develop [1]."

**WHY:** C1 — claims about CBIC come from its published text. The reproduced CBIC conclusion, `main.pdf`
p. 42, reads: "Essentially, the MTL approach did not consistently demonstrate superior performance over
its single-task counterparts and exhibited higher computational demands". The published Florida table
(Ch.3 Table 2, p. 40) has MTL ahead of Single on two of seven category F1 rows — Food 57.43 ± 1.46
against 56.70 ± 0.84, Shopping 62.51 ± 0.94 against 61.88 ± 1.01 — which is why the published verb
carries "consistently". Every other frame site keeps the qualifier: `1_introduction.tex`:115 ("did not
consistently outperform the"), `6_conclusion.tex`:35 and :102, `3_cbic.tex`:25 ("did not consistently
improve on"). §2.3 is the outlier. Under WRITING_LAW §3 the CBIC null is load-bearing and is to be
written "with the same care as the wins"; overstating it is the same class of error as overstating a
win. The trailing "a result that holds for that configuration" satisfies the time-index rule and is
not at issue.

**FIX:** "… and does not consistently outperform the dedicated single-task models, a result that holds
for that configuration …". One word. I rank this should-fix rather than blocker because the sentence is
a survey-level pointer with the time-index intact; the author may reasonably escalate it, since the
strengthened form is not derivable from the cited source.

### SF-2 — the supplementary volume names the dissertation by a title the dissertation does not carry

**WHERE:** `src/build/main_extra.pdf` p. 3 ("About this volume", first sentence) · source
`src/main_extra.tex`:206–208.

**WHAT** (verbatim, `main_extra.pdf` p. 3):

> "This volume holds two appendices that were written for the dissertation "From Representations to a
> Single Joint Model: Multi-Task Learning for Point-of-Interest Category and Region Prediction" and
> that are published beside it rather than inside it."

The title of record, on `main.pdf` p. 1 (folha de rosto), p. 2 (Resumo header), p. 3 (Abstract header)
and on `main_extra.pdf` p. 1 itself: "MULTI-TASK LEARNING FOR POINT-OF-INTEREST CLASSIFICATION AND
PREDICTION TASKS: THE ROLE OF THE CHECK-IN-LEVEL REPRESENTATION".

**WHY:** A meta-claim about the work that is false as written (AGENT_GUARDRAILS §4b V1/V2 class: the
record describes something other than what exists). The supplementary volume is a separately deposited
artifact, so this is the sentence a reader uses to tie it to the dissertation, and it names a document
that does not exist. The string appears elsewhere in the tree only inside comments listing candidate
titles (`src/preamble.tex`:198, `src/chapters/1_introduction.tex`:9), which is consistent with a
superseded title decision that this one live occurrence missed. Not a science claim, hence should-fix
rather than blocker — but for the deposit it behaves like one.

**FIX:** Replace the quoted title with the title of record, or drop the quotation and write "the
dissertation" (the volume's own cover, p. 1, already carries the full title directly above).

### SF-3 — [VERIFY] the "that a deep network does not satisfy" clause is attributed to Nash-MTL by citation placement, and I could not confirm the source states it

**WHERE:** `src/build/main.pdf` p. 23 (§2.3, Pareto paragraph).

**WHAT** (verbatim, PDF p. 23):

> "Nash-MTL proves that its updates have a subsequence converging to a Pareto-stationary point, and
> reaches Pareto optimality only under an added convexity assumption on the losses that a deep network
> does not satisfy [47]; the fixed points of CAGrad are Pareto-stationary [48]; and Aligned-MTL
> converges to such a point for task weights fixed in advance [49]."

**WHY:** AGENT_GUARDRAILS R1(c)/R3 — the specific claim attributed to a reference must be located in
the source. The first two halves are supported by the round-9 Pareto ledger, which quotes
arXiv:2202.01017v2 Theorem 5.4 p6 and Theorem 5.5 p6/p14 (`src_utils/_history/_round9/31_pareto.md`:31). The
third clause, "that a deep network does not satisfy", is a claim about deep networks, and in that same
ledger it appears as the reviewer's own gloss, outside the quoted material: "Nash-MTL reaches Pareto
*optimality* only with convexity added, which a deep network does not give" (`31_pareto.md`:41). As
typeset, `[47]` sits after the clause and reads as attributing it to the paper. **I did not open
arXiv:2202.01017 this session**, so I can neither confirm nor deny that the paper says it; under the
fail-closed rule this is a flag, not a verdict.

**FIX:** Either (a) open the source and, if the paper states it, note page/section in the bib comment
and leave the sentence as is; or (b) move the clause out of the citation's scope so it reads as the
dissertation's own observation, e.g. "… only under an added convexity assumption on the losses [47],
which a deep network does not give". Author's call which.

---

## 3 · Nits

### N-1 — the verb-binding law is stated conditionally in Ch.2, where the law itself is unconditional

**WHERE:** `src/build/main.pdf` pp. 25–26 (end of §2.4) · source
`src/chapters/2_fundamentals.tex`:782–784.

**WHAT:** "Wherever this dissertation reports a test, the verb and the test are bound together:
"outperforms" follows only from a paired superiority test, and "matches" only from a non-inferiority
test within the stated margin."

**WHY:** WRITING_LAW §3 binds the verb to the test unconditionally; "wherever this dissertation reports
a test" makes the binding conditional on a test being reported, which as written leaves an untested
"outperforms" outside the rule. Ch.4 then does use "consistently outperforms" (p. 57) with no
significance test in that study. The document handles this correctly elsewhere — p. 25 discloses that
"Chapters 3 and 4 report fold means and standard deviations and run no significance test, so the tests
set out below license verbs in Chapter 5 alone" — so the disclosure exists; only the law sentence is
loosely scoped. Nit for that reason.

**FIX:** "Throughout this dissertation the verb and the test are bound together: …", leaving the
Chapters 3/4 exemption to the sentence that already states it.

### N-2 — the Ch.4 preface flags the split but not the absence of significance testing

**WHERE:** `src/build/main.pdf` p. 44 (Ch.4 preface) · `src/build/main.pdf` p. 57 (Ch.4 conclusion,
reproduced).

**WHAT:** The preface carries the protocol caveat — "stratifies the cross-validation split by sample
rather than by user, a weaker protocol than the user-disjoint cross-validation adopted in Chapter 5;
the conclusions reported here are those of the time, for that configuration" — and the required Item 6
sentence. The chapter then reads "ST-MTLNet consistently outperforms the baseline based only on DGI"
(p. 57) and "outperforms MTLnet in all 21 category-state combinations, with average gains per state of
20.2 to 22.0 percentage points".

**WHY:** Reproduced published prose, and the audited counts are in place (15 of 21 plus one technical
tie, p. 57, matching the errata table at `main_extra.pdf` p. 16), so this is not a C1 violation. But a
reader who reads the preface and then the chapter meets an "outperforms" whose licensing exemption is
stated only back in Ch.2 §2.4 (p. 25). One clause in the preface would close it locally.

**FIX:** Optional, author's call: append to the preface's protocol sentence "and it reports fold means
and standard deviations without significance testing". Purely additive; changes no claim.

---

## 4 · Honesty devices intact (verified present at this commit)

Recorded so future editors know what is load-bearing. Each was measured, not remembered.

| Device | Status | Where verified |
|---|---|---|
| **C4 BRACIS prohibition** | **zero occurrences** of `BRACIS`/`Bracis` in all four PDFs | sweep over `main`, `main_academico`, `main_ppgc`, `main_extra` |
| **C1 must-NOT-say: cardinality-cost framing** | zero occurrences of `cost grows`, `cardinality`, and of the TX `−2.4` figure, in all four PDFs | same sweep |
| **C1 must-NOT-say: "beats"/"wins"/"Pareto-dominates"** | zero `beat*`; zero `Pareto-dominat*`/"dominates everywhere"; `win` appears once, p. 25, non-verdict ("the comparison a joint model has to win is made per task") | `main.pdf` sweep |
| **"ties" never used as a region verdict** | three `tie*` hits: pp. 55/57 "technical tie" (published CoUrb wording, errata-audited) and p. 64 "ties this structure to" (verb) | `main.pdf` pp. 55, 57, 64 |
| **AZ never upgraded** | p. 73: "At Arizona, the interval is centered on zero, so we report a match, not a gain." | `main.pdf` p. 73 |
| **AL deficit stated, not smoothed** | p. 73: "At Alabama, the whole interval lies below zero, a small but statistically significant deficit, still well within the two-point margin." | `main.pdf` p. 73 |
| **MobiWac status wording** | "submitted, under review" / "submitted to MobiWac 2026 and under review" at pp. 6 (List of Tables), 13, 15, 21 (lineage table), 59 (preface); `accept*` never applied to it (its three hits, pp. 93/94/100, are unrelated: review findings, a dataset agreement prompt, a statistical basis) | `main.pdf`, sweep + read |
| **Time-index prefaces** | Ch.3 p. 28 "Its conclusions are the conclusions of the time, for the configuration studied here"; Ch.4 p. 44 "the conclusions reported here are those of the time, for that configuration"; Ch.5 p. 59 "under review at the time of writing" | `main.pdf` pp. 28, 44, 59 |
| **Nash-MTL preference time-indexed** | Ch.3 preface p. 28: "The chapter's preference for the Nash-MTL optimizer is likewise a conclusion of the time, weakened by a later finding about the optimizer implementation, and Chapter 5 does not rely on it." | `main.pdf` p. 28 |
| **Pareto non-claim (the §2.3 mandated sentence)** | p. 23: "This dissertation therefore claims no Pareto property of any kind for its models. Its verdicts are per-task scores measured against dedicated single-task models under the tests of Section 2.4." | `main.pdf` p. 23 |
| **Cost disclosed, never sold as a saving** | p. 78 "and it cost more to train"; p. 79 "about 4.2 million parameters at Alabama against 0.6 million at its published width" | `main.pdf` pp. 78–79 |
| **Cosine number travels with its full scope** | p. 80: "+0.001 over four seeds on four Gowalla states, three of which are among the five we report, directional conflict only, a finding for this pair of tasks rather than a general rule" | `main.pdf` p. 80 |
| **Freeze control not over-read** | p. 79: "at the three datasets where the control was run (Alabama, Arizona, Florida) … The control does not say which part." plus the refusal to use the −0.04 ± 0.13 ablation as evidence of no contribution | `main.pdf` p. 79 |
| **Task-pair confound concession** | p. 81, limitation 6, with the fixed-pair ablation tied to it in §6.4 | `main.pdf` pp. 81 |
| **Ch.4 ownership note** | p. 44: "Tarik S. Paiva is the first author of the paper; the author of this dissertation is the second author, presented the paper at the workshop" | `main.pdf` p. 44 |
| **next place delimited, once, early** | p. 14 (§1.4): "The exact next place is not predicted anywhere in this work." Restated as limitation 4, p. 81 | `main.pdf` pp. 14, 81 |
| **Resumo/Abstract claim parity** | Claim-by-claim match, `main.pdf` p. 2 vs p. 3: three studies; "não superou consistentemente" / "did not consistently outperform"; "naquela configuração" / "in that configuration"; six datasets named identically; "vinte modelos ajustados por configuração, quatro inicializações aleatórias sobre cinco partições fixas" / "twenty fitted models per configuration, four random initializations over five fixed folds"; "nos seis, por 5,3 a 9,4 pontos de macro-F1 sob uma seleção joint-best" / "at all six, by 5.3 to 9.4 macro-F1 points under a joint-best selection"; "supera em quatro deles e equipara-se estatisticamente, com não-inferioridade dentro de uma margem de dois pontos de Acc@10 (TOST), nos outros dois" / "outperforms at four of them and statistically matches, with non-inferiority within a two-point Acc@10 margin (TOST), at the other two". No claim appears in one language only; no quantifier or hedge differs. | `main.pdf` pp. 2–3 |
| **Cross-volume containment** | `main_ppgc.pdf` pp. 3–4 are whitespace-identical to `main.pdf` pp. 2–3 (Resumo, Abstract). `main_academico.pdf` carries no Resumo/Abstract by design (`src/main_academico.tex`:3-4: the deposit system generates them), so there is no second copy to drift. The must-not-say sweeps above return zero on all four volumes. | normalized page comparison |

## 5 · NEW CLAIM — needs author sign-off

Not judged, flagged per C2.

1. **`apx_f_cosine.tex`:290, "That is why hard sharing costs nothing in this architecture."** Not on
   the PAPER_PLAN §3 CAN-say list and not derivable from it; the licensed mechanism claim is "sharing
   stopped hurting" (NORTH_STAR §6, Ch.6 N3 beats), which the document uses at p. 80. See B-1. Either
   the weaker licensed form goes in, or the stronger claim needs sign-off with its scope and its AL
   exception attached.
2. **`main.pdf` p. 23, "an added convexity assumption on the losses that a deep network does not
   satisfy [47]."** Whether this clause is the source's statement or the dissertation's own is a
   sign-off question as well as a verification one. See SF-3.

## COUNTS

**blockers 2 / should-fix 3 / nits 2**

## UNFINISHED

Reached the 25-minute checkpoint. Not done:

1. **Line-by-line read of Chapters 3, 4 and 5.** I read their prefaces, their conclusions, the
   results pages carrying the protected headline (pp. 40–43, 55, 57, 60, 71–73, 77), and swept all
   three for the must-not-say vocabulary. I did **not** read their method and related-work sections
   sentence by sentence, so an un-swept paraphrase of a banned claim inside those sections would have
   passed. Highest-value next pass: `chapters/5_mobiwac/07_discussion.tex` and
   `chapters/3_cbic/*.tex` against PAPER_PLAN §3's must-NOT-say list, reading rather than grepping.
2. **The never-cite lists (C3) as claims.** I verified the TX `−2.4` figure and the cardinality-cost
   framing are absent from all four PDFs, but I did not check the STAN v4-collapse numbers, the ReHDM
   v2 row, or the VOID fp16/bf16 cells against `docs/PAPER_FINDINGS.md` — I never opened that file, so
   I do not know the forbidden values and cannot certify their absence. Persona 06 sweeps the numerals;
   the claims built on them are unaudited here. Table 10 (p. 72) does carry `‡ReHDM at TX and CA: a
   single seed` and `†STAN partial folds: TX 4/5, CA 2/5 (seed 0)`, which is disclosure, not a
   never-cite check.
3. **CAN-say scope conformance item by item.** I checked the region and category verdicts, the
   scaling-claim scope, the cascade framing (not reached), and the AL/AZ handling. I did not walk the
   full CAN-say list (the +28 to +40 representation margins, the 64–72 / 89–90 percent context
   attribution, the Markov-1 floor 51 to 72 / +4.9 to +10.3) against the chapters that state them.
4. **`main_academico.pdf` and `main_ppgc.pdf` body text.** Read only as sweeps plus front matter.
   The three volumes share `content.tex`, so body divergence is unlikely by construction, but I did
   not verify that.
5. **The `[VERIFY]` in SF-3 was not resolved.** Resolving it needs arXiv:2202.01017 opened and the
   convexity clause located; that is a citation-auditor action (persona 05) or one fetch I did not
   have time for.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
