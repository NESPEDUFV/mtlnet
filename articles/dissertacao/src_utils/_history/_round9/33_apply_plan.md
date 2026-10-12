# 33_apply_plan.md — the 20 "you apply" items: what parallelizes, what does not

Round 9, 2026-07-30. Baseline `d4078c75`; the split committed as `c39b7b77`.

## The partition, reconciled before anything else

Stated as an explicit reconciliation because the first two versions of this file each got it wrong:
a set expression missing a parenthesis counted Wave A as ten while its own table listed nine, and
FAB-25 appeared in two waves at once. Both were caught by joining the lists instead of trusting a
headline (GUARDRAILS §4b V13, eighth instance: a count of the instrument's output is not a count of
your set).

| wave | items | count | gated on |
|---|---|--:|---|
| **A** | FAB-01, FAB-11, FAB-12, FAB-13, FAB-16, FAB-19, FAB-23, FAB-24 | 8 | nothing — 7 edits applied and verified in the render, plus FAB-01 already satisfied and only confirmed |
| **B** | FAB-26, FAB-29, FAB-30, GER-01, GER-05, GER-06, GER-07 | 7 | another agent's open edit of `2_fundamentals.tex` |
| **C** | FAB-06, FAB-18, FAB-20, FAB-21, FAB-25, FAB-31 | 6 | an author decision (a fail-closed `GLOSSARY.md` row, or a claim-time call) |

    A = {'FAB-01', 'FAB-11', 'FAB-12', 'FAB-13', 'FAB-16', 'FAB-19', 'FAB-23', 'FAB-24'}
    B = {'FAB-26', 'FAB-29', 'FAB-30', 'GER-01', 'GER-05', 'GER-06', 'GER-07'}
    C = {'FAB-06', 'FAB-18', 'FAB-20', 'FAB-21', 'FAB-25', 'FAB-31'}
    assert len(A) + len(B) + len(C) == len(A | B | C) == 21
    # 21 = the 20 apply items + FAB-18, which MOVED to "author decides" while I was
    # applying it (see below) and is kept in Wave C so the plan still accounts for it.

## The constraint that decides the plan

**Another agent is editing this same checkout.** Measured mtimes: `GLOSSARY.md` 02:11:37 then
02:30:27, `src/chapters/2_fundamentals.tex` 02:23:31, `check_audit_claims.py` 02:38:44 (it added five
probes of its own on top of my two-root change), plus its commit `c94d1f19` and `_history/_round9/31_pareto.md`.
I lost one of its notes by replacing a block I had read half an hour earlier, repaired in `24eef3f1`.

That single fact decides Waves B and C: **7 items touch `2_fundamentals.tex`** and several depend on
`GLOSSARY.md`, and both files are in someone else's hands right now.

## Wave A — 7 edits applied and verified in the RENDERED PDF, plus 1 confirmation (8 items, two files)

Neither file had been touched by the other track. All are one-clause wording fixes with no registry
dependency.

| track | file | items |
|---|---|---|
| A1 | `chapters/1_introduction.tex` | FAB-12, FAB-13, FAB-16, FAB-19, FAB-23, FAB-24 |
| A2 | `content.tex` | FAB-01 (confirm only), FAB-11 |

Verified by extracting the text layer of `build/main.pdf` and asserting both directions per item: the
new wording present AND the old wording absent, sixteen assertions over the seven items (FAB-11 is
checked in both languages). Source-level greps were not accepted as evidence (V14).

**That claim was written before eight of those sixteen assertions existed.** The first run covered
both directions for only FAB-12, FAB-16 and FAB-19; FAB-13 and FAB-11 had presence checks only, and
FAB-23 and FAB-24 absence checks only. The missing eight were then run against the same build and all
sixteen pass. Recorded because the passing result does not retire the defect: the sentence asserted a
measurement it did not have, which is the same fault this file corrects for FAB-01 two paragraphs
down.

**FAB-01 is the eighth, and it is not one of them.** It asked for the advisor line in English; the
line was already there, so nothing was edited and the diff against `c39b7b77` contains no advisor
line added or removed. Only the presence half is measurable for it, because there is no superseded
wording that could be absent, and presence is what was checked (`Advisor: Fabrício Aguiar Silva` in
the English abstract, `Orientador: Fabrício Aguiar Silva` on the folha de rosto). I first gave it the
same applied-and-verified note as the other seven, which asserted a both-directions measurement that
cannot exist for a no-op. **A wave count is not a count of edits when one member changed nothing** —
the same V13 shape as the stale-anchor miscount earlier in this round, and the second time it landed
on a headline number in this file. One item, FAB-11, needed a check the reviewer could not have made: the "one keyword per line"
rule of `UFV_COMPLIANCE.md`:39 governs the **AcademicoPG web form**, and the keyword block renders on
pp. 2-3 of `main.pdf` and pp. 3-4 of `main_ppgc.pdf` but on **no page** of `main_academico.pdf`, the
deposit body. So the form rule was not in play and his request does not collide with it.

### FAB-18 left this wave while I was applying it

It asks for the present tense on "was unresolved when this research started". I had bucketed it
**apply** and FAB-03 — the *same sentence in Portuguese* — **author decides**. Both cannot be right:
the identical edit cannot be mine to make in English and his to rule on in Portuguese, and the
Resumo/Abstract pair must stay claim-for-claim identical (`WRITING_LAW` §6). The substantive question
is FAB-03's: the present tense asserts the question is open **today**, after this dissertation
answered it, which is what the time-indexing rule exists to prevent. It is now one decision over
three sites, in Wave C and in `PENDENCIAS.md` §6.2.

**Found by applying it, not by sorting it.** Worth recording: the sort was done from the quotes, and
the conflict only became visible when the edit had to be typed in both languages at once.

## Wave B — serialized behind the other track's §2.3 work (7 items)

FAB-26, FAB-29, FAB-30, GER-01, GER-05, GER-06, GER-07.

These do not conflict with each other; they conflict with **someone else's open edit**. Waiting costs
less than merging: that track added 106 lines to §2.3 and three of my coordinates in that file already
moved +106. Land them in one pass once §2.3 settles, in this order, because each later step reads text
the earlier one leaves behind:

1. **GER-01** — the two GNN citations. Self-contained; both works verified this session, two new bib
   entries.
2. **GER-05, GER-07, FAB-26** — one edit pass, not three: all three land in the same two paragraphs of
   §2.2 (the HGI-roles sentence and the Check2HGI sentence).
3. **GER-06** — the encoder paragraph, moving FiLM into §2.3. Must come **after** that track finishes,
   since it moves text *into* the section being rewritten.
4. **FAB-29, FAB-30** — §2.4 wording, last: least entangled, and their coordinates are the ones that
   already drifted.

## Wave C — blocked on an author decision, not on time (6 items)

FAB-06, FAB-18, FAB-20, FAB-21, FAB-25, FAB-31.

`GLOSSARY.md` is **fail-closed**: a term not in the registry may not appear in prose, and agents
propose while the author approves. Measured: `scenario` is absent from `GLOSSARY.md` and
`WRITING_LAW.md`, yet already live 11 times inside the reproduced paper chapters. So FAB-06, FAB-21 and
FAB-31 are mine to type and not mine to authorize. FAB-20 and FAB-25 need the hyphenation rule in the
registry before a tree-wide sweep can claim to enforce anything, and FAB-25's own flagged instance is
already correct under that rule. FAB-18 is here for the reason above.

**Not applied, and their blocks say so** rather than showing them as done.

## Sub-agent scope, if Wave B is delegated

Round 6 lost 2.6 hours to the slowest child in each of five waves, one running 5.4 hours on 84
inspection cells. Per `AGENT_GUARDRAILS` S1-S3:

- **Wall-clock checkpoint: 40 minutes.** Past it, a child writes what it has to its report file and
  says what remains, in the word *unfinished*. Partial results in hand beat complete ones later.
- **Archaeology budget: zero.** Every item block carries its coordinate and its build commit. A child
  needing history has hit something this plan got wrong and should report that rather than dig.
- **One file per child.** This round's clobber came from two writers and one file.
- **A child's self-report is not evidence.** The parent verifies every claimed edit in the **rendered
  PDF** (V14), and a probe lands in the same commit as its edit (V15).

## What "done" cannot mean this round

7 items wait on another agent's open file and 6 wait on the author. A report claiming all 20
are applied would be false in the exact way this repository has already been burned by. The honest end
state, and the one this round reached: **7 edits applied and verified in the render, 1 item
confirmed as already satisfied, and Waves B and C pending with the reason named.**


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
