# 50 · Auditing every PENDENCIAS item against the document

**What was asked.** Audit each item in §2 and §5: confirm the ones marked done are still done, find any
marked open that are now finished, archive the genuinely closed, and say which of the author's earlier
rulings no longer hold. §4 (his own forward-looking notes) was explicitly out of scope and was not touched.

**Method.** Each item was measured against the tree at `45c75611` plus the working tree, reading the
document rather than the item's own status line. That distinction is the point: two items disagreed with
their own headers, in opposite directions.

## Result: 14 closed, 5 open

| item | verdict | evidence |
|---|---|---|
| `2.1` | OPEN (yours) | 54 [NEEDS SIGN-OFF] markers measured in src, 21 files. Unchanged. |
| `2.5` | OPEN (yours) | both .drawio still at fontSize=14 and 13; no drawio/inkscape in this environment |
| `2.8` | **CLOSED** | sua propria decisao fecha o item: "nada aqui. Este item esta fechado; o que espera voce esta no §6". |
| `2.9` | **CLOSED** (after a correction) | The first closure was wrong twice over and is recorded in full below. Now measured: the same standalone sentence, word for word, in the dissertation's Ch.5 and in the `[mobiwac]` article; the Appendix D pointer in the dissertation's section preamble, rendering on p. 64 with zero undefined refs. Probes `A9-diss`, `A9-ptr`, `A9-oldnum`, each validated by its own sabotage. |
| `2.11` | **CLOSED** | Opcao B aplicada: 21 mencoes de nao-inferioridade na prosa viva, incluindo Resumo e Abstract, cada uma com a margem e o teste nomeados. |
| `2.12` | **CLOSED** | `Pareto-stationary point` registrado no `GLOSSARY.md`, e a linha de errata que voce pediu esta no Apendice B. |
| `2.14` | **CLOSED** | Entrada `nash` reconstruida do seu paste do PMLR: `pages = {16428--16446}`, `volume = {162}`, `publisher = {PMLR}`, com url. |
| `2.15` | **CLOSED** | Caminho A aplicado nas duas arvores de artigo: `standley2020tasks` no lugar da citacao nao atestada, mais as linhas de errata. |
| `2.16` | **CLOSED** | `origin/mobiwac` esta em `488e4d10`, cujo pai `0288cb70` publica os tres artefatos de reprodutibilidade que faltavam. Lido do remoto. |
| `2.18` | **CLOSED** | `git ls-remote origin / grep -c refs/notes` = **0**. A ref saiu do publico. |
| `2.19` | **CLOSED** | `src_utils/WORDCOUNT_CONVENTION.md` fixa a convencao que voce escolheu (310/271) e diz por que as outras duas contagens diferem. |
| `2.20` | **CLOSED** | Opcao 2 aplicada: `\textit` na prosa viva do Cap. 4 = **48** (eram 157 no fonte em `5c074a2a`). Os sobreviventes sao os 7 nomes de categoria, nomes de modelo e substantivos proprios. |
| `2.21` | OPEN (yours) | 'license the verbs' not in prose; you said it was the only term he flagged |
| `2.23` | **CLOSED** | R-3, R-5 (a frase longa caiu para 17 palavras), R-6 (13 referencias ao apendice) e EX-6 aplicados. **EX-9 SUPERSEDIDO** pela sua propria revisao, por sua decisao de 2026-08-02: voce mandou nao aplicar e depois reescreveu as quatro |
| `2.24` | OPEN (yours) | one British 'towards' still in live prose |
| `2.25` | **CLOSED** | sua propria decisao: "Done!". |
| `2.26` | **CLOSED** | R15-09 e R15-10 aplicados em 2026-08-02: "The figure shows two patterns." e "Answering that question needs the same diagnostic". `check_register` e `check_process_narration` em rc=0. |
| `2.27` | PARTLY (yours) | you resolved 19 of 47 orphan flags (47 -> 28); 54 sign-offs intact; gates green |
| `5.6b` | **CLOSED** | A prosa carrega so as datas do banco, ['2009', '2010', '2011'], como voce mandou; os marcadores de sign-off que voce liberou sairam do LaTeX. |

## The two that disagreed with their own status

**`2.26` was recorded as resolved and was not.** The author ruled "Aplique o R15-10 e o R15-09". Neither had
been applied: `"Two patterns stand out in the data."` and `"Settling that needs"` were both still in live
prose in the cosine appendix. Applied on 2026-08-02.

**`EX-9`, inside `2.23`, was undone by the author's own revision.** He ruled *not* to apply it. Its four
phrasings — `deserves one statement`, `worth reporting`, `needs saying`, `worth stating` — are all gone from
live prose; `git log -S` on each shows two leaving in his own `src_clean` merge (`807183c1`) and two in
earlier rounds. Put to him, he ruled that his read-through supersedes the earlier decision. Recorded as
SUPERSEDED, not as applied.

**And the probe guarding that decision could not have caught it.** `A23-EX9` watched `r"Pareto front"`,
which is still in the chapter and is unrelated to the four phrasings. It passed for its whole existence
while the decision it was written to protect was being undone. Repointed to the Pareto-front *definition*
he declined to cut, and validated by sabotage: rc=1 with the definition altered, rc=0 restored.

## One the tracker called open that was applied

`2.20`, the ordinary-English italics in Chapter 4. His option 2 is applied: `\textit` in Chapter 4's live
prose is **48**, against 157 in the source at `5c074a2a`. The survivors are the seven category names,
model names and proper nouns. Two arguable forms remain, `one-hot` and `skip-gram`, left alone.

An instrument note: the first measurement of this item returned **2**, because it counted `\emph` when the
chapter marks italics with `\textit`. A drop from 153 to 2 was too large to be believed, which is the only
reason the wrong macro was caught.

## Archiving cost 54 citation repoints

Moving 14 items broke **51** live citations to their coordinates, plus 3 more in `GLOSSARY.md` and the
tracker itself that the first sweep did not scan. All repointed to
`PENDENCIAS_RESOLVIDOS <id> (arquivado 2026-08-02)`, the convention already in the tree. Two gate probes read
the tracker at archived coordinates and were repointed to the archive file; one needed a wrap-tolerant
pattern, because the phrase it pins now wraps across two lines and a one-line pattern reported a present
sentence as missing.

`check_tracker_refs` also caught the audit entry itself being filed under the wrong section: `§3` follows
`§6` in this file, so appending before `§3` put the item inside `§6`. Refiled at the end of `§2`.

## What remains the author's

| item | what is missing |
|---|---|
| `2.1` | 54 `[NEEDS SIGN-OFF]` markers in 21 files. He asked to be given three priority ones; none named yet. |
| `2.5` | Both `.drawio` still at `fontSize=14` and `13`. No `drawio` or `inkscape` in this environment. |
| `2.21` | His advisor marked terms in a PDF not available here. |
| `2.24` | One British `towards` in published CBIC prose; his option (a) was offered, not chosen. |
| `2.27` | 28 `[ORPHANED]` flags (down from 47 — he cleared 19 in `45c75611`) and the 54 sign-offs. |

**His earlier rulings on all five still hold.** None was superseded by a change in the text; what each
needs is a choice or a tool this environment lacks.

## The correction this audit needed itself

`2.9` was closed on evidence that could not distinguish done from not-done. The probe searched Chapter 5
for `+0.001`, `0.0032`, `"seven datasets"` and `cosine`, and reported all four present. But `+0.001` and
`+0.0032` **are the old four-seed development numbers the item is about** — the item's own DECISAO states
that Chapter 5 still reported them. A pattern that matches the pre-state cannot certify the post-state.

The closure line then said "both trees edited (artigo e dissertacao) as you authorized", while the
measurement globbed `src/**/*.tex` only. **The article tree was never opened.** Measuring it found the
dissertation carried the appendix pointer and the article carried nothing — and the article has no appendix,
so an internal `\ref` was never possible there. The paragraph's own provenance comment requires the two
texts to stay identical, so the dissertation-only sentence had already broken that parity.

Resolved on the author's instruction: the sentence was rewritten to **stand alone** — no dependence on a
document the reader may not hold — and applied identically in both trees, with the Appendix D link moved to
the dissertation's section preamble, which is dissertation-only prose that already cites Chapters 3 and 4
by `\ref`.

This is the same failure as the `A23-EX9` probe described above, arriving from the other direction: there a
probe watched a string unrelated to its claim, here a probe watched strings that were present before the
work began. Both certified a claim they could not test. The three replacement probes were each validated by
sabotaging only their own target, because a suite where every sabotage trips the same probe first proves
only that one probe works.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-02 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
