# 49 · Merging the author's revised tree into `src`

**What this is.** On 2026-08-02 the author delivered `src_clean`, a tree he had read and edited
himself. He asked for three things: bring it into `src`, audit whether any of the agent's recent
changes were lost in it, and decide which comments should stay. This records what was measured.

## The tree he delivered had no comment layer

| | `src` before | `src_clean` | `src` after the merge |
|---|---:|---:|---:|
| comment lines | 4,114 | 55 | 4,234 |
| comment blocks | 275 | ~2 | 275 |
| `[NEEDS SIGN-OFF]` markers | 54 | 0 | 54 |

His prose is byte-for-byte his in all 54 shared files. The comment layer was re-anchored onto it by
aligning the two trees' prose with a sequence matcher and reattaching each block to the prose line it
preceded. **228 of 275 blocks re-anchored exactly.** The other 47 annotate sentences he rewrote or
cut; they are kept, marked `[ORPHANED 2026-08-02]`, listed below.

This mattered beyond history: `check_comment_hygiene`, `check_trapped_prose` and `check_audit_claims`
read the comment layer, and the provenance pointers into `PENDENCIAS_RESOLVIDOS` live in it.

## What he was missing, and what he had already fixed better

Fifteen changes had landed in `src` after he forked. **Fourteen were absent from his tree.** None
collided with his edits, verified by checking each passage against the fork baseline.

| | outcome |
|---|---|
| reapplied to his prose | R15-01, R15-01b, R15-02, R15-02b, R15-04, R15-04b, R15-06, R15-06b, R15-08, B5-2 |
| **obsolete: his rewrite dissolved the defect** | R15-03b, B5-1, R15-07, R15-07b |
| already present in his tree | R15-03 |

The four obsolete ones were confirmed by checking the *defect*, not the fix: the omitted pronouns and
the 24-word preposed protocol clause are absent from his text because he rewrote those sentences.

## The Abstract and Resumo, on his instruction

His revision dropped the equivalence-test wording, the numbers, and the expansion of MTL. He ruled:
restore the TOST language and the expansion, restore the numbers **without** "joint-best selection"
(an unexplained term), and add the external-baseline comparison. That last claim was verified at
source before being written: Chapter 5 states the joint model "is also above every external baseline
reported, on both tasks, across all six datasets", naming HMT-GRN, STAN, a ReHDM reference, POI-RGNN
and the Markov floor.

## Gate failures after the merge: seven stale patterns, one real move, one real defect

Eleven checks failed. **Each was traced to its cause rather than repointed to make it pass.**

| check | cause | action |
|---|---|---|
| `A11-frame`, `A11-frame2` | he writes the adjective, probe demanded the noun | repointed |
| `A23-EX9`, `R9-pareto` ×3, `R9-conflict` | concepts survive in his wording | repointed |
| `NUM-4` | **the HGI sweep MOVED to his new `apx_g_hgi_tuning.tex`** (renders p. 106) | repointed to that file |
| six `FAB-*` render assertions | advisor's requests satisfied in his words, not his strings | repointed, verified in the PDF first |
| `VERIFY_LIST` repair clause | moved to `apx_a_contributions.tex` | repointed |
| `VERIFY_LIST` page number | his revision added a page; invariant still holds | expectation updated |
| `check_trapped_prose`, `check_torn_sentences` | **defects the merge itself introduced** | fixed, below |

`NUM-4` is the one that was not a wording change. Repointing it by pattern-fiddling would have
recorded a lost measurement as a rewrite.

## Two defects the merge introduced, and one instrument gap

Five orphan-marker blocks landed *between* the two halves of a sentence, one of them swallowing a
line of prose from the render. All five relocated below their sentence; swept for the shape and none
remain.

`check_torn_sentences` fired on the author's own line wrap after "non-U.S.", which is not a sentence
end. Guarded by matching the abbreviation rather than exempting the file, and validated in both
directions with a fixture whose opening word is not in `LEGIT_OPENER` (the first fixture used "of",
which the checker legitimately allows, so its silence proved nothing).

## One real inconsistency, resolved on his ruling

The merged document carried both spellings of the central term: **"multitask learning" 20× and
"multi-task learning" 18×**. `GLOSSARY.md:130` registers "multitask learning", so his spelling is
canonical. Only **three** of the hyphenated instances are prose; the other 36 are cited titles in
`references.bib` and must not be altered. The three were changed; the titles were not.

## The `VERIFY_LIST` region check, rewritten to check the claim

Its original grep pinned the literal "four of six". The author reworded that claim twice during this
session, and each rewording made the probe report a defect that was not there. It now measures what
the finding is about: whether a region-win claim ever appears without its non-inferiority qualifier.
The caveat window extends past the claim's own full stop, because Chapter 6 correctly puts it in the
next sentence. Validated by removing a caveat: rc=1, then rc=0 restored.

## The 47 orphaned comment blocks, for the author

Each annotates a sentence that is no longer in the text. None was deleted.

| file | block opens | anchor that is gone |
|---|---|---|
| `chapters/1_introduction.tex` | [FAB-12, round 9] "users" plural at the advisor's request. The sentence is generic (it | \emph{check-in} records that users visited a given place, a point of i |
| `chapters/1_introduction.tex` | [FAB-13, round 9] "the two prediction tasks that are the object of study of this | The two properties above are the two prediction tasks that are the obj |
| `chapters/1_introduction.tex` | [NEEDS SIGN-OFF: raised v1 assembly, 2026-07-23 / gate L3 fix A-1. Original sentence was near-ve | Sharing parameters between tasks can hurt one of them, a failure mode  |
| `chapters/1_introduction.tex` |   % [FAB-23, round 9] ", Fundamentals" dropped at his request: the \ref renders the number and t | \item \textbf{Chapter~\ref{ch:fundamentals}} consolidates the backgrou |
| `chapters/1_introduction.tex` |         % Venue verified 2026-07-23 against the official CBIC 2025 site | \item \textbf{Chapter~\ref{ch:courb}} presents the second article, pub |
| `chapters/1_introduction.tex` |         % Venue verified 2026-07-23 against SBC OpenLibrary (sol.sbc.org.br/index.php/ | The article is first-authored by Tarik S.\ Paiva; this author is the s |
| `chapters/1_introduction.tex` |         % Venue verified 2026-07-23 against the official symposium site | \item \textbf{Chapter~\ref{ch:conclusion}} consolidates the answer to  |
| `chapters/1_introduction.tex` |         % [NEEDS SIGN-OFF: raised round 4, 2026-07-26 / REV-014, 2026-07-26] "twenty repetitions | \item[Practical.] Evidence that one deployable model can serve both pr |
| `chapters/2_fundamentals.tex` | --------------------------------------------------------------------------- |  |
| `chapters/2_fundamentals.tex` | Section 2.3 -- Multi-task learning |  |
| `chapters/2_fundamentals.tex` | [round9, 2026-07-30] TWO SENTENCES REWRITTEN, found independently by the style and the | A multi-objective problem needs a definition of optimum. Deep multi-ta |
| `chapters/2_fundamentals.tex` | [round9c, PENDENCIAS_RESOLVIDOS 2.23 (arquivado 2026-08-02), readability report R-5, author decision "Aplique o R-3,5,6 e o EX-6"] | Not every |
| `chapters/2_fundamentals.tex` | [round9, 2026-07-30] ATTRIBUTION CORRECTED (M2, MTL persona). It read "Two of these papers state | claim at all \cite{yu2020pcgrad}. Two of these papers raise the residu |
| `chapters/2_fundamentals.tex` | [round9, 2026-07-30] TERM NAMED (style persona, REQUIRED). The sentence defined the concept with | Gradient conflict has a standard measure, and it is the quantity the g |
| `chapters/2_fundamentals.tex` | [round9, 2026-07-30] SENTENCE CORRECTED, and it was a technical error, not a wording one. It rea | \cite{yu2020pcgrad}. Orthogonality is not a conflict resolved but a co |
| `chapters/2_fundamentals.tex` | [round9, 2026-07-30] THREE CORRECTIONS IN ONE SENTENCE, all from the MTL persona, all verified h | measures the cosine on the joint model of Chapter~\ref{ch:mobiwac} and |
| `chapters/2_fundamentals.tex` | relative clause ending on a stranded preposition is the sub-case where a non-native reader's par | the metrics and reference points that each result is read against, the |
| `chapters/2_fundamentals.tex` | [round6, N-2, fact gate persona 06/07] REPAIRED. This clause used to read "Chapter 3 reports | The statistical treatment is scoped the |
| `chapters/2_fundamentals.tex` | [round9c, PENDENCIAS_RESOLVIDOS 2.21 (arquivado 2026-08-02), the advisor's flag, 2026-07-30] "license verbs in Chapter 5 alone" -> | Comparisons there are made across the folds and |
| `chapters/2_fundamentals.tex` | MOVED HERE 2026-07-30: this block sat between "cannot be assumed;" and "it has to be measured", | Whether joint training |
| `chapters/2_fundamentals.tex` | [GATE FIX B-3, 2026-07-24] "unlocks for" -> "enables in": "unlock" is on the inherited | superiority tests, outperforms the dedicated single-task models on the |
| `chapters/3_cbic.tex` | !TeX root = ../main.tex | \chapter[Multi-Task Learning for POI Category and Next-POI Prediction] |
| `chapters/4_courb.tex` | !TeX root = ../main.tex | \chapter[ST-MTLNet: Spatio-Temporal POI Representations]{ST-MTLNet: Sp |
| `chapters/5_mobiwac.tex` | !TeX root = ../main.tex | \chapter[A Check-in-Level Multi-Task Study of Next Category and Region |
| `chapters/6_conclusion.tex` | [round9c, 2026-08-02, R15-03] TWO fixes in one clause. (1) "region head" -> "region output": | taken on an earlier configuration whose region output was driven by a  |
| `chapters/6_conclusion.tex` | [round5, F50 audit] The author asked whether this experiment is sound enough to cite. It is not, | Second, |
| `chapters/6_conclusion.tex` | [round5, COD-010] The previous sentence said "across three training configurations and all twent | The California run, completed since, repeats the pattern. At the match |
| `chapters/6_conclusion.tex` | [NEEDS SIGN-OFF: raised round 4, 2026-07-26 / REV-013, 2026-07-26] The interim sentence ("A part | Parameter count alone, without the second task's training signal, yiel |
| `chapters/6_conclusion.tex` | [round9, 2026-07-30] POINTER ADDED (excellence persona EX-3). This paragraph cites the cosine fr | tasks rather than a general rule. Appendix~\ref{apx:cosine} reports th |
| `chapters/6_conclusion.tex` | [round8, 2026-07-30, PENDENCIAS_RESOLVIDOS 5.6 (arquivado 2026-07-30)] BOTH DATES, because they  | \item \textbf{Data vintage.} The five state datasets come from Gowalla |
| `chapters/6_conclusion.tex` | [round9c, PENDENCIAS_RESOLVIDOS 5.6b (arquivado 2026-08-02), author decision, 2026-07-30] ONE WINDOW, THE MEASURED ONE. His words: | \item \textbf{Taxonomy coarseness.} The category task uses seven top-l |
| `chapters/apx_b_errata.tex` | [round5, author decision 1b.3] The Nash-MTL cost claim moved OUT of this section and INTO the |  |
| `chapters/apx_b_errata.tex` | [round6, L-9, source-ledger pass] COUNT CORRECTED. This read "all 25 places ... 21 in prose, one | \emph{ST-MTLNet} is a different name and keeps its published form thro |
| `chapters/apx_b_errata.tex` | [round9c, 2026-08-02, R15-01] WAS \ref{apx:cosine}, which labels an appendix of the MAIN volume. | dissertation. |
| `chapters/apx_d_ceiling.tex` | [2026-07-27] Exception traced to leak_sniff_fl.csv rgcn: perstep=0.3328 (below 0.3617), |  |
| `chapters/apx_f_cosine.tex` | [round9c, 2026-07-30] CITATION ADDED at the author's instruction (PENDENCIAS_RESOLVIDOS 2.22 (ar | The usual reason is a disagreement, and it shows up in the gradients:  |
| `chapters/apx_f_cosine.tex` | [round9c, 2026-08-02, R15-06] WAS "It now covers". Two defects in seven words. "now" is true onl | The second axis is the data. The seven datasets cover every dataset Ch |
| `chapters/apx_f_cosine.tex` | [round9, 2026-07-30] PARAGRAPH DELETED, at the author's instruction, and it deserved to go for f |  |
| `content.tex` |         % [NEEDS SIGN-OFF: Resumo CUT, round 6, 2026-07-28] The pair was cut on the author's | \noindent Redes sociais baseadas em localização registram \emph{check- |
| `content.tex` |         % afirmacoes (WRITING_LAW §6) continuar passando no par. Resultado primeiro, protocolo d | Sob validação cruzada com usuários disjuntos entre treino e teste, |
| `content.tex` |             % [NEEDS SIGN-OFF: Abstract CUT, round 6, 2026-07-28] Cut as the claim-parity pair o | \noindent Location-based social networks record \emph{check-ins}: visi |
| `content.tex` |             % conditions ahead of its subject "that joint model" (measured: the subject sits at  | Under user-disjoint cross-validation, that joint model outperforms |
| `main_extra.tex` | [round9c, 2026-08-02, R15-02] WAS a quoted title, ``From Representations to a Single Joint Model | cover of this volume and that are published beside it rather than insi |
| `main_extra.tex` | stacked before a reduced relative clause ending on a stranded preposition -- the hardest of the  | reference level that one screening |
| `preamble.tex` | !TeX root = main.tex |  |
| `preamble.tex` | -- Machinery (from the source tree, kept) -- | \usepackage{abntex2-UFV}        % UFV front matter + 3/2 cm margins (c |
| `preamble.tex` | --------------------------------------------------------------- | \titulo{\normalsize{\textbf{Multi-Task Learning for Point-of-Interest  |


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
