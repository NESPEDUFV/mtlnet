#!/usr/bin/env python3
r"""Gate `\finalbuildfirstpage` -- the number the first body page of the DEPOSIT build prints.

WHY THIS EXISTS, and it is not a hypothetical risk
--------------------------------------------------
`src/main.tex` sets the printed page number of the first body page of `main_academico.pdf`. That
number has now been "corrected" FOUR times -- 11, then 8, then 9, then 10 -- and every one of the
first three was wrong. The fourth (10) was also wrong: the RASCUNHO measured on 2026-09-06 shows
the correct value is 20.

Three things made that possible, and this file answers all three.

1. THE RECIPE IN THE SOURCE TAUGHT THE WRONG METHOD. The comment above the macro said: count the
   pre-textual pages of `build/main_academico.pdf` and add one. Our PDF contributes NINE unnumbered
   pages, so that recipe yields 10 -- and 10 is what it yielded, consistently, while being wrong by
   exactly the pages the recipe cannot see. AcademicoPG PREPENDS its own front matter to whatever we
   upload, and the UFV manual counts those pages. They are not in our file, so no amount of measuring
   our file will ever reveal them.

2. THE MACRO'S OWN COMMENT CLAIMED A GATE THAT DID NOT EXIST. It read "src_utils/_history/_round6/
   VERIFY_LIST.md item A4 carries the command, and check.sh runs it, which is how this was caught."
   Verified 2026-09-06 by listing every script `check.sh` invokes: nothing checked this number.
   `sync_page_counts.py` checks page TOTALS, never the first-page NUMBER. A false claim that a guard
   exists is worse than no guard, because it makes each successive wrong value feel verified.

3. THE ONE GATE THAT DOES RUN IS INDISTINGUISHABLE FROM ITS OWN MISSING-BUILD ERROR. To be precise,
   and correcting a wrong statement made earlier the same day: `sync_page_counts.py` does NOT exit 0
   when a build is missing -- it exits 1 and `check.sh` records FAIL. The problem is subtler. It
   `sys.exit`s on the FIRST missing build, and `main_ppgc.pdf` is routinely absent, so the run ends
   before any count is compared. Its failure for "you did not build ppgc" looks exactly like its
   failure for "a recorded number is wrong", so the noise trains a reader to skip it. This file
   therefore separates the two outcomes explicitly: a missing build exits 2 ("cannot check"), a
   real disagreement exits 1 ("wrong"). They must never be confused again.

WHAT THE UFV RULE ACTUALLY IS
-----------------------------
Manual de entrega, §7, and `UFV_COMPLIANCE.md:37`:
  - pre-textual pages are COUNTED but NOT NUMBERED;
  - the cover and the ficha catalográfica are NEITHER counted NOR numbered;
  - the first body page therefore prints (counted pre-textual pages) + 1.

So the number depends on the ASSEMBLED document, not on ours.

THE ARITHMETIC, from the RASCUNHO of 2026-09-06 (127 sheets, watermarked, system-emitted)
-----------------------------------------------------------------------------------------
    127 sheets  =  11 prepended by the system  +  116 ours
     11 prepended  =  1 cover (not counted)  +  10 counted
    counted pre-textual  =  10 (system)  +  9 (ours, unnumbered)  =  19
    first body page prints  =  19 + 1  =  20

Cross-check, independently: the last sheet is 127; only the cover is uncounted; so it is counted
page 126. From the other end, 20 + 107 - 1 = 126, where 107 is our body pages (116 - 9). The two
paths agree, which is what makes 20 trustworthy rather than merely measured.

THE FICHA DOES NOT MOVE THIS NUMBER. When the Library attaches it there will be 128 sheets, but the
ficha is inserted before the body and is not counted: 128 - cover - ficha = 126 still, and the first
body page still prints 20. It shifts the physical index only. Do not "correct" this value when the
ficha arrives.

WHAT THIS GATE CANNOT DO, stated so nobody trusts it further than it goes
------------------------------------------------------------------------
`SYSTEM_COUNTED_SHEETS` below is NOT derivable from anything in this repository. It is a property of
what AcademicoPG generates, and the only authority is a system-emitted RASCUNHO. It is pinned here
with its provenance, and the manual says so twice: "a referência correta para a numeração das páginas
deve ser sempre o arquivo emitido pelo sistema." If the portal's front matter changes -- a new field,
a second signature sheet -- this constant is stale and this gate will confidently certify a wrong
number. RE-MEASURE IT AGAINST A FRESH RASCUNHO whenever the portal's front matter might have changed,
and record the new measurement here rather than adjusting the macro to match.

Run:  python3 src_utils/check_first_body_page.py     (from articles/dissertacao/, or via check.sh)
Exit: 0 agree · 1 the macro disagrees with the rule · 2 cannot check (missing build / unreadable)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN_TEX = ROOT / "src" / "main.tex"
PDF = ROOT / "src" / "build" / "main_academico.pdf"

# Counted sheets AcademicoPG prepends to the uploaded body: 11 generated, minus the cover, which the
# manual excludes from the count. MEASURED on the RASCUNHO emitted 2026-09-06 (127 sheets, DRAFT
# watermark, 1,744,823 bytes), by the `academico` session, and reconciled independently by two others.
# See the module docstring before changing this: it is not derivable from our build.
SYSTEM_COUNTED_SHEETS = 11 - 1

MACRO = re.compile(r"\\newcommand\{\\finalbuildfirstpage\}\{(\d+)\}")


def unnumbered_prefix(pdf_path: Path) -> tuple[int, int]:
    """(pages before the first printed number, the value that first printed number is).

    Reads the top-right corner box rather than the header text: the running head and the page
    number are different objects, and matching header prose has produced false readings here
    before. The band is generous (right 28%, top 10%) because the number sits inside a box whose
    exact origin moves with the geometry package.
    """
    import pypdfium2  # imported late so a missing dep is a "cannot check", not an import crash

    doc = pypdfium2.PdfDocument(str(pdf_path))
    for i, page in enumerate(doc):
        w, h = page.get_size()
        corner = page.get_textpage().get_text_bounded(
            left=w * 0.72, bottom=h * 0.90, right=w, top=h
        ).strip()
        # ⚠ NOT `re.fullmatch(r"\d+", corner)`, which is what this was until 2026-09-06 and which
        # gives FALSE NEGATIVES ON ARBITRARY PAGES of any watermarked PDF. The `academico` session
        # hit exactly this while verifying the RASCUNHO: the DRAFT watermark lays glyphs on the same
        # line as the page number, so sheets 22, 23 and 126 read as "no number at all" under a
        # line-anchored match while their neighbours read fine. A gate that skips a page it cannot
        # parse would here silently report the FIRST NUMBERED PAGE AS LATER THAN IT IS, and that is
        # the very quantity this file exists to certify.
        # So: pull every integer out of the corner box and take the first. On our own unwatermarked
        # build this is identical to the strict match (verified: same 9 / 20 result); on a
        # system-emitted RASCUNHO it keeps working.
        nums = re.findall(r"\d+", corner)
        if nums:
            return i, int(nums[0])
    raise ValueError("no page in the deposit build prints a number in the top-right corner")


def main() -> int:
    if not MAIN_TEX.exists():
        print(f"CANNOT CHECK: {MAIN_TEX} is missing.")
        return 2
    m = MACRO.search(MAIN_TEX.read_text(encoding="utf-8", errors="replace"))
    if not m:
        print(r"CANNOT CHECK: \finalbuildfirstpage is not defined in src/main.tex. If the macro was "
              "renamed, repoint this gate in the same commit -- a probe whose target is gone is "
              "not a pass.")
        return 2
    declared = int(m.group(1))

    # A MISSING BUILD IS "CANNOT CHECK" (2), NEVER "WRONG" (1) AND NEVER A PASS. Keeping these
    # distinct is the whole point of this file; see docstring §3.
    if not PDF.exists():
        print(f"CANNOT CHECK: {PDF.relative_to(ROOT)} is not on disk. Run `make academico` (it does "
              "NOT overwrite dissertacao.pdf), then re-run. Not a pass and not a failure.")
        return 2
    try:
        n_unnumbered, first_printed = unnumbered_prefix(PDF)
    except Exception as exc:  # noqa: BLE001 -- any read failure is "cannot check", not "correct"
        print(f"CANNOT CHECK: could not read page numbers from {PDF.relative_to(ROOT)}: "
              f"{type(exc).__name__}: {exc}")
        return 2

    expected = SYSTEM_COUNTED_SHEETS + n_unnumbered + 1

    print("== first printed body-page number of the DEPOSIT build ==")
    print(f"  our unnumbered pre-textual pages (measured)   {n_unnumbered:4d}")
    print(f"  counted sheets AcademicoPG prepends (pinned)  {SYSTEM_COUNTED_SHEETS:4d}")
    print(f"  UFV rule: counted pre-textual + 1             {expected:4d}")
    print(f"  \\finalbuildfirstpage declares                 {declared:4d}")
    print(f"  the build actually prints                     {first_printed:4d}")

    # Internal consistency: the counter must start ON the first body page. If these disagree the
    # macro is being applied somewhere other than where this gate assumes, and the comparison below
    # would be meaningless rather than wrong.
    if first_printed != declared:
        print(f"\nCANNOT CHECK: the build prints {first_printed} where the macro declares {declared}. "
              "The PDF on disk is older than main.tex, or the macro no longer sets this counter. "
              "Rebuild and re-run before reading anything into the number.")
        return 2

    if declared != expected:
        print(f"\nFAIL: the deposit build's first body page prints {declared}; the UFV rule gives "
              f"{expected}.")
        print(f"  Fix: set \\finalbuildfirstpage to {expected} in src/main.tex, rebuild, re-attach in "
              "AcademicoPG, and re-emit the RASCUNHO to confirm.")
        print("  Do NOT derive this by counting only our own pre-textual pages -- that recipe is what "
              "produced the previous three wrong values. See this file's docstring.")
        return 1

    print("\nOK: the first body page prints the number the UFV rule requires.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
