# `src/tables/` — table sources, one file per table

Organized by article, mirroring `src/figures/`:

| Directory | Contents |
|---|---|
| `cbic/` | Chapter 3 result tables + its Appendix B errata tables |
| `courb/` | Chapter 4 result tables + its Appendix B errata table |
| `mobiwac/` | Chapter 5 result tables + its Appendix B claim-scope table |
| `frame/` | Tables belonging to the frame: the Chapter 2 lineage table, Appendix D's benchmark table, and the bibliography errata table |

Each file holds exactly one table and is pulled in with `\input{tables/<dir>/<name>}` from the
chapter that presents it. Float placement, caption and label live with the table, so moving a table
between chapters is a one-line change.

## Provenance of the extraction (2026-07-27)

The 16 tables were extracted from the chapter files in commit `e8974e81`, at the author's request and
following the convention of the source papers (`CBIC___MTL/tables/`, `[mobiwac]/src/tables/`).

**The extraction was verified text-neutral.** The pre-extraction tree was built with the same prose
edits applied, and the rendered text layer of both PDFs was compared: 260,848 characters each,
identical. Float placement, captions and every value are unchanged; only the container moved.

Two corrections to that record, both found by review rather than by the agent that wrote it:

1. The per-file headers originally claimed the extraction was verified "by comparing the rendered PDF
   checksum before and after". No checksum comparison was ever run, and it could not have matched:
   that commit also changed prose, so the PDF bytes moved 1,322,758 to 1,323,852. The check that was
   actually performed is the rendered-text comparison described above, which is the right check for
   the claim of text-neutrality.
2. `frame/bib_errata.tex` was converted from `table` to `longtable` in commit `82f2949f`. It is
   taller than the text block, so as a float it hung 163.43 pt below the bottom margin on page 96.
   The build reported zero overfull boxes throughout, because LaTeX logs this as `Float too large for
   page`, a warning class the build checker did not read. `src_utils/build.sh` now reports and fails
   on it.

## Adding a table

Put it in the directory of the article that presents it, one table per file, and `\input` it. Keep
the provenance of every printed number in a comment inside the table file, next to the value: that
comment is what the fact gate follows when it traces a figure back to a committed artifact.
