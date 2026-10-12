# 30_r10_audit.md — the author's 28 rulings, re-measured against the live tree before acting

Round 10, 2026-08-03. Baseline commit `dda8978e` (builds 106/103/107/22 pp, `make check` rc=0 with 68
probes, `make selftest` rc=0). The author answered every open item in `PENDENCIAS.md` §6 and asked for
an audit first, with a warning that carried the round: **"we have made several changes to the text since
your last update, so please check if the items are still valid and re-read the text."** That warning was
correct and it is the single most useful fact in this file.

## The headline: sixty commits landed, and nine of the twenty-eight items had already been fixed

Between the items being filed and the rulings arriving, 60 commits touched this tree. Nine rulings ask
for text that **no longer exists**, so the correct action was to close them as already-done rather than
apply anything. Measured by locating each item's target string in the live, comment-stripped source:

| item | the text the item asks about | live status |
|---|---|---|
| FAB-14 | `, one of seven top-level classes` | **gone** |
| FAB-17 | `A fourth task also appears` | **gone**; `1_introduction.tex`:70 now says "the three tasks" |
| FAB-10 | the old results opener | **gone** |
| GER-03 | the HGI tuning sweep, thrown into §2.2 | **relocated** to `apx_g_hgi_tuning.tex` |
| GER-11 | Appendix F's evidence for task non-conflict | rebuilt; author ruled no action |
| BLQ-1 | `hard sharing costs nothing` | **gone** |
| BLQ-2 | bare `everywhere` in the conclusion | **fixed** at `6_conclusion.tex`:126-127 |
| BLQ-4 | `replacing the sharing scheme changed so little` | **gone** |
| BLQ-5 | `makes no Pareto claim at all` | **gone** |

GER-03 deserves its own line. The author's ruling named three separate defects: the sentence reads with
no nexus, it is overwhelming, and it belongs in the methodology rather than the fundamentals. All three
are addressed in the live tree by his own hand: the sweep is now a dedicated appendix with a table, and
it closes on a scope disclaimer stating that it supports adapting one baseline hyperparameter and is
**not** evidence about HGI versus Check2HGI. Nothing was left for me to do.

## What I actually applied (four edits, each verified in the rendered PDF)

**BLQ-2, the surviving site.** Chapter 6 was already correct, but ONE instance survived, and a
line-level grep did not see it because the sentence wraps across three source lines:
`1_introduction.tex`:289-292 still said the model "either outperforms or matches it on next region",
which collapses the partition the ruling says to keep. It now mirrors Chapter 6: category at all six
datasets, region at four of the six, TOST non-inferiority within two points at the other two. The
category half keeps a universal because it is true six times out of six; `WRITING_LAW` §3 bans bare
"everywhere", so it names the datasets instead. **Lesson worth keeping: a wrapped sentence is invisible
to a line-oriented search. The comment-stripped, whitespace-collapsed concatenation found it.**

**BLQ-3.** The two derived ratios are gone from `apx_f_cosine.tex`. They were arithmetically correct
(35.92 and 16.35) and that was never the objection: they were computed in prose, so nothing regenerated
them when a dataset was added, and a dataset was added to that appendix twice in one week. The four
endpoint counts stay, each traceable to §D.1's table. The author's own reason is the better one: the
ratios did not tell him what they meant.

**FAB-08.** A comment now records what the Resumo omits: that the task pair CHANGES between studies
(Chapters 3 and 4 pair static POI category classification with next-POI prediction; Chapter 5 pairs
next category with next region). It names the omission as a deliberate round-6 length cut rather than an
oversight, points at the two places the reader does get it, and states that restoring it means editing
both abstract blocks in one commit.

**FAB-22.** Most of this ruling was already satisfied: the per-dataset detail he objected to had left
the paragraph. One clause was missing, and it was the half carrying the argument, that **Istanbul is
there because it is not a United States dataset**. Without that, Istanbul reads as a sixth dataset
rather than as evidence about generalization. Now stated.

## FAB-27's margin concern: real, and already fixed. I nearly reported it wrong

The author: "algo que temos que tomar cuidado e que a tabela esta passando da margem." Measured:

- **zero** `Overfull \hbox` warnings in all four builds;
- per-page ink extraction over all 106 defense pages against the true text block
  (`\setlrmarginsandblock{3cm}{2cm}`, `\textwidth` 455.24pt measured by asking TeX directly): every
  page ends **0.5 mm inside** the block, and the tightest page measures 1.99 cm against the 2 cm rule;
- the lineage table is `tabularx` sized to `\textwidth`, which cannot overrun by construction, and its
  own comment records that the previous `lll` version **did** overrun by 29.76pt;
- commit `6d780b58` is titled "fix the p.96 overflow".

His observation was true of an earlier build and is fixed. **The near-miss is worth recording.** I first
concluded "no overflow" from the zero-warning count plus a page-level scan that showed +0.3pt on table
pages, and wrote that the 0.3pt was body text. Then prose pages measured **−0.3pt**, a 0.6pt difference
between table pages and prose pages, which meant tables genuinely reach further and my explanation was
wrong. That gap is what sent me to ask TeX for the real geometry instead of assuming 2 cm from the
requirement. Had the two numbers happened to match, I would have shipped a correct verdict resting on a
wrong reason, which is the sixth unearned measurement of this work and the fifth of the pattern in
`_history/_round9/34`.

## FAB-28: the blocker of round 9, settled by the PDF the author supplied

Three prior sessions could not obtain `wang2025hamtl` (publisher API 401, landing page redirecting to an
authentication gate, no abstract in OpenAlex or Unpaywall), so the item was recorded BLOCKED and the
paper inadmissible. The author placed the PDF on disk and it has now been read in full. Details in
`28_hamtl.md`; the load-bearing outcome is that the chapter's claim of absence **survives unchanged** on
three independent grounds from the source, and what actually needed fixing was our own description of
HAMTL, which named the wrong component and omitted the main/auxiliary asymmetry the paper leads with.

## GER-04: the author asked me to validate his idea, and the answer is that it is right and already done

His proposal was to keep the encoder paragraph where it sits, because it works as a bridge to the
embedding types the check-in representation then consumes, and to strengthen its link to the preceding
paragraph by saying that a per-visit representation needs temporal and spatial embeddings. The sentence
he quoted is gone. What stands reads: limitation (one fixed vector per place, so a weekday morning and a
Saturday night are identical inputs) → **"A per-visit representation needs temporal and spatial context
in addition to the identity of the visited POI"** → the encoder inventory → the check-in level that
consumes it. That is his proposal, implemented. The introduction half needs nothing either:
`1_introduction.tex`:125-131 already carries the argument.

## Still running when this was written

GER-08, GER-09, GER-10 and AUT-01 are one job in one file (numbered definition environments, the cosine
definition for gradient conflict, and the balancer lineage), dispatched separately. Its report will be
`29_ch2_definitions.md`. Nothing in this file depends on its outcome.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
