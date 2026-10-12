# WORDCOUNT_CONVENTION.md — the Resumo/Abstract word counts of record

> **Why this file exists.** Three instruments gave three answers for the same two blocks
> (310/271, 312/277, 345/307), and item 2.19 of `PENDENCIAS.md` asked which convention governs.
> The author ruled: **310 for the Resumo and 271 for the Abstract**, in his words
> *"310/271 no relatorio, eu não entendi porque há 3, mas o quantidade de plavras no resumo hoje
> são essas."* His ruling settles **which numbers are of record**, not which instrument is right.
> This file records the convention that produces them, so the figures can be re-checked rather
> than only re-taken. That was the durable defect item 2.19 named: a measurement with no stated
> tree state can only be re-measured, never re-verified.
>
> **Created** 2026-07-30 (round 9c), on the author's ruling. Measured against the defense build of
> that day, **101 pages**.

## The convention

Counted from the **rendered PDF**, not the source, because the deposit's limits apply to what the
librarian reads. One block per page: the Resumo on p. 2 and the Abstract on p. 3 of the defense
build.

1. Extract the page text.
2. Remove the catalog header, everything through the advisor line.
3. Remove the keyword block, from `Palavras-chave:` / `Keywords:` onward.
4. Remove the soft-break marker the extractor inserts at a hyphenated line break.
5. Split on whitespace. **Every token counts, including numerals.**

Step 5 is the whole of the disagreement between the three answers. Excluding numeric tokens gives
308/272; counting a hyphenated word as two gives more; measuring the source rather than the render
gives more again. The convention above is the one that reproduces the author's figure for the
Resumo exactly.

## The command

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao
python3 - <<'PY'
import importlib.util, re, pypdfium2 as pdfium
spec = importlib.util.spec_from_file_location("ma", "src_utils/_history/_round6/_measure_abs.py")
ma = importlib.util.module_from_spec(spec); spec.loader.exec_module(ma)
doc = pdfium.PdfDocument("src/build/main.pdf")
for label, pg in (("Resumo", 2), ("Abstract", 3)):
    raw = doc[pg - 1].get_textpage().get_text_range()
    body, _ = ma.strip_header(raw)
    body, _ = ma.strip_keywords(body)
    print(label, len(body.replace('\ufffe', '').split()))
PY
# EXPECT: Resumo 310
# EXPECT: Abstract 274   <- see "the Abstract's three words" below
```

## The Abstract's three words, and why 271 is still the number of record

Run today, the convention returns **Resumo 310** — the author's figure, exactly — and
**Abstract 274**, three more than his 271. The gap is not an instrument disagreement. The Abstract's
prose changed after the round-6 report was written:

| revision | Abstract words (source, same cleaning) |
|---|---|
| `35fe46cc`, the report-era commit | 270 |
| `HEAD`, 2026-07-30 | 275 |

The word-level diff is one wording change: *"every state"* became *"the three states"*, and *"so"*
became *"indicating that in that configuration"*. That is +5 source words, which lands as +3 in the
render under this convention.

So the author's 271 is the count **of the Abstract as it stood when he read it**, and it is correct
for that text. Two readings are available and the choice is his:

- **Keep 310/271 as the figures of record** and treat 274 as the current measurement of a block that
  has since been edited. Nothing in the document prints either number, so nothing is wrong today.
- **Re-take the Abstract figure at deposit time** and record 274 (or whatever the block then
  measures), keeping this convention.

Neither is urgent: **no sentence in the dissertation prints a word count.** Measured 2026-07-30
across all live `.tex` files, the strings 310, 271, 312 and 277 appear in no word-count claim in
prose. The figures live in reports and in this file.

## What was corrected in a durable record

`src_utils/_history/_round6/VERIFY_LIST.md` item 4's annotation expected `Pareto-stationary 0` in the
glossary and was corrected to `2` when the author's decision (a) registered the term. The
word-count figures in `_history/_round6/15_resumo_abstract.md` and `_history/_round6/06_07_number_claim_audit.md` are
**left as written**: they were correct against the tree they measured, and this file is the pointer
that says which tree that was. Overwriting them would destroy the record rather than date it.

## Limits of the deposit, for context

The PPGCC template's own guidance is 233–282 words for a Resumo and 195–250 for an Abstract, quoted
in the provenance comment of `src/content.tex`. Both blocks are above the upper bound under this
convention, which is a separate question from which number is of record, and it is the author's to
raise with the program if he chooses.