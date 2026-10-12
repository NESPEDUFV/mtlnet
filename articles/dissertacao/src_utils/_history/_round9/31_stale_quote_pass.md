# 31_stale_quote_pass.md — how every number in `CONSIDERATIONS.md` §1 was produced

Round 9, 2026-07-30. Build commit **`d4078c75`**. Every count below carries the command or the
procedure that yields it (GUARDRAILS §4b V1), and the two places where my own instrument was broken are
recorded, because a corrected number with no record of the correction is how a stale figure survives.

## 1 · The corpus

The live corpus is the same scope `check.sh` derives from the filesystem, plus `tables/*/*.tex` (the
lineage table FAB-27 is about lives there):

    cd articles/dissertacao/src
    ls chapters/*.tex chapters/*/*.tex preamble.tex content.tex tables/*/*.tex | wc -l
    # 50 files

Matching runs on **live text**: an unescaped `%` and everything after it is dropped per line, the
surviving lines are joined with single spaces, and whitespace is collapsed. This is the same convention
as `check_audit_claims.live_text()`, and it is not optional here: this tree's provenance comments quote
the very strings being searched for, so an unfiltered sweep over-reports (V4).

## 2 · The classifier

For each quoted passage, in order:

1. exact match in live text;
2. exact match ignoring all non-alphanumeric characters (the author's transcription of Germano lost the
   spaces in `Thecheck-in-levelrepresentation,Check2HGI`, which is a PDF copy-paste artifact, not a
   changed sentence);
3. exact match after **resolving `\ref` to its rendered number** and stripping `\emph`/`\textbf`;
4. otherwise the longest common run against the closest live passage, reported as a coverage ratio.

Step 3 matters and it is why one item moved buckets: Germano quoted *"In the models of Chapters 3 and 4
it conditions"*, which does not exist in the source. The source says
`In the models of Chapters~\ref{ch:cbic} and~\ref{ch:courb} it conditions`. He read the PDF. Scoring
that as a changed sentence would have been an instrument error, not a measurement.

## 3 · Two broken instruments, both caught by assertion

**(a) The label parse returned zero rows.** Resolving `\ref` needs the label table. My first attempt
read `build/main.aux` and got **0 labels**, which is indistinguishable in the output from "no labels
defined". The labels are in the per-file aux files:

    find build -name '*.aux' | wc -l          # 48
    grep -h 'newlabel' build/main-aux/chapters/*.aux build/main-aux/*.aux | wc -l

After repointing: **112 labels**, with `ch:cbic=3`, `ch:courb=4`, `ch:mobiwac=5`, `ch:fundamentals=2`,
`ch:conclusion=6`, and `sec:fund:tasks=2.1` through `sec:fund:relevance=2.5`. A parse returning zero
rows is a broken instrument, not a clean result (V13, fifth and sixth instances), so the fix was an
assertion that the parse found what it was meant to find.

**(b) I classified GER-01 as GONE, and it is a request.** Germano asked for two papers to be *added*.
I fed their TITLES to the quote classifier, which correctly found them absent, and I recorded the item
as having a dead anchor. The item's anchor is the paragraph he was reading, which is exact at
`chapters/2_fundamentals.tex:143`. Corrected in the item block, with the correction stated there rather
than silently fixed.

## 4 · The counts

| | items | anchors | exact | changed | gone | paraphrase |
|---|--:|--:|--:|--:|--:|--:|
| Fabricio (written) | 31 | 31 | 21 | 5 | 5 | 0 |
| Germano (verbal) | 11 | 14 | 10 | 0 | 0 | 4 |
| Total | 42 | 45 | 31 | 5 | 5 | 4 |

The four columns sum to 45 = the anchor count. The 42 reviewer items plus `AUT-01`
(the author's own question, which anchors on nothing) give the 43 blocks in the tracker.

**All ten stale anchors are Fabricio's, and all ten cite `0_main.tex`.** That file was split into
`preamble.tex` + `content.tex` on 2026-07-29, and the Resumo and Abstract were cut and rebuilt on
2026-07-28. Every one of the 21 anchors in Chapters 1, 2 and 6 is exact. So the staleness is not
scattered decay; it is one structural edit plus one rewrite, and it is concentrated entirely in the
front matter.

Three items are **already satisfied** as a result, verified by absence across the whole live corpus:

    # each returns no live hits
    grep -rn "coletânea" chapters/ content.tex preamble.tex | grep -v ':[[:space:]]*%'
    grep -rn "na ordem em que aconteceram" chapters/ content.tex | grep -v ':[[:space:]]*%'
    grep -rn "par de tarefas" chapters/ content.tex | grep -v ':[[:space:]]*%'

That is FAB-04, FAB-05 and FAB-08. Note the interaction the tracker flags: FAB-17 asks to delete the
same task-pair content from the *introduction*, where it is signed-off material.

## 5 · Re-measuring the 2026-07-28 audit

An audit is an anchor set like any other, so its own numbers were re-taken rather than carried:

| the audit's claim | now | verdict |
|---|---|---|
| 5 sections | 5 | holds |
| **zero** subsections | 0 | holds |
| ~4,456 words | 4367 | holds |
| 3 numbered equations | 3 | holds |
| ~1 citation per 64 words | 1 per 64 | holds |
| 27 paragraphs | 33 | **stale** |
| mean 161 words | 132 | **stale** |
| five paragraphs over 240 words | 4 | **stale** |

Paragraph counting is over live prose with `equation`, `align`, `table`, `tabular` and `figure`
environments removed and blocks under 12 words dropped as markup. The three stale rows are all from
Part V, whose whole argument is about paragraph structure, so anyone acting on Part V's items 24-27
should re-take the paragraph table first.

## 6 · POI hyphenation (FAB-20, FAB-25)

    # live counts, comments stripped, whole corpus
    hyphenated 'point-of-interest' : 11
    spaced     'point of interest' : 8

The prior audit reported 13 vs 8; the hyphenated count is now 11. Under the English
compound-modifier rule (attributive hyphenated, nominal open) most of the current distribution is
already correct, including the exact instance Fabricio flagged at `2_fundamentals.tex:27`
("a user, a point of interest (POI), and a timestamp"), which is nominal and correct as it stands.

## 7 · The `scenario` finding, which neither reviewer could have known

Fabricio asks three times for `states` to become `scenarios` (FAB-06, FAB-21, FAB-31). Measured:

- `scenario` is **absent from `GLOSSARY.md` and from `WRITING_LAW.md`**;
- it is **already in live prose 11 times**, all inside the reproduced paper chapters
  (`3_cbic/*`, `4_courb/*`) and `tables/courb/errata.tex`.

The registry is fail-closed: a term not in it may not be used. So the term is in use and unregistered,
and his edit cannot land until the entry does. That is a GLOSSARY change, which is the author's to
approve, and it is why the three items are grouped under one probe.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-30 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
