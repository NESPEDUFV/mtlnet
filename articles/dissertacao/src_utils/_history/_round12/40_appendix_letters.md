# 40_appendix_letters.md — the file-to-letter mapping, read from the build before anything moved

Round 12, 2026-08-03. Baseline commit `8f17f294`. Written BEFORE any file was touched, because the
author's instruction named appendices by RENDERED LETTER ("remover A.1, C.3 e E") while the repository
names them by FILE PREFIX, and the two had drifted apart. He asked for the mapping and a confirmation
before deletion, on the grounds that removing the wrong appendix is not recoverable from his side of the
review.

## Why the prefixes stopped matching the letters

There are two `apx_b_*` files, which looks like a collision and is not. **The appendices are split across
two volumes, and each volume letters its own appendix sequence from A.** `content.tex` includes the
defense appendices; `main_extra.tex` includes a different set. So `apx_b_errata.tex` and
`apx_d_ceiling.tex` never appear in the defense volume at all, and the defense letters skip over their
prefixes. Nothing is mislabelled. The file prefixes are simply stale relative to a sequence that changed
under them.

## The mapping, from the per-volume `.aux` label tables

**Defense volume** (`main.pdf`, 108 pp) -- the letters the committee sees:

| letter | file | title | pp. |
|---|---|---|---|
| A | `apx_a_contributions.tex` | Other Scientific Contributions | 96-99 |
| A.1 | | The experimental platform | 96 |
| A.2 | | Reproducing the reported numbers | 96 |
| B | `apx_c_ai_disclosure.tex` | AI disclosure | 99 |
| C | `apx_e_ethics.tex` | Data Ethics and Governance | 100-102 |
| C.1 | | Where the data came from | 100 |
| C.2 | | Real people, and how the traces are handled | 101 |
| C.3 | | The human-subjects question | 101 |
| D | `apx_f_cosine.tex` | Why the Two Tasks Do Not Conflict | 103-107 |
| D.1-D.4 | | (the "§D.1" that appendix's own prose cites) | 103-106 |
| E | `apx_g_hgi_tuning.tex` | Adaptation of the HGI Baseline | 108 |

**Extra volume** (`main_extra.pdf`, 22 pp), lettering independently:

| letter | file | pp. |
|---|---|---|
| B | `apx_b_errata.tex` (B.1-B.6) | 5-13 |
| D | `apx_d_ceiling.tex` | 19 |

## The ambiguity, resolved: E is the HGI sweep

**E = `apx_g_hgi_tuning.tex`, not `apx_e_ethics.tex`.** The author predicted this before the measurement
and his reasoning was the deciding evidence: item 2 of his instruction says "como vamos remover o
appendix E nao preciso referenciar ele" in the same breath as the 0.7 cross-region weight, and the sweep
that fixed 0.7 is that appendix's entire content. The measurement agrees with the intent.

`A.1` and `C.3` are unambiguous once the letters are fixed: `apx_a_contributions.tex`:26-95 and
`apx_e_ethics.tex`:83-98 respectively.

## One flag raised before removal, and his ruling on it

C.3 is titled "The human-subjects question" and is not a procedural note. It records the author's
POSITION that review by a research ethics committee was not required for a secondary analysis of two
already-public collections, states plainly that it records "no approval and no exemption, because none
was sought and none is claimed", and cites the 2024 dissertation from the same program and advisor that
handled the question the same way. `UFV_COMPLIANCE.md` imposes no ethics-statement requirement, so this
was never a compliance blocker; the concern raised was narrower, that a committee question about ethics
review would be answered by a document the committee may not have open.

**His ruling: move all three as instructed.** Recorded here rather than argued again. The position remains
on record and citable in the supplementary volume, and C.1 and C.2 stay in the defense volume.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
