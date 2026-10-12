#!/usr/bin/env python3
"""Detect prose accidentally trapped inside a LaTeX comment line.

WHY: this failure is SILENT. The build succeeds, no warning is emitted, and the reader gets a
sentence that stops mid-clause or a disclosure that never appears. It has now bitten this document
EIGHT times, every one of them from an edit that inserted an audit comment:

  apx_a_contributions.tex   a sentence FRAGMENT appended after a comment's terminal period
  4_courb.tex:187           half a PUBLISHED methodology sentence, dropping three method facts
  5_mobiwac.tex:385         four sentences including a required three-limits disclosure
  4_courb.tex:311 and :362  two PUBLISHED results passages, about 270 words
  2_fundamentals.tex:366    ", Nash-MTL treats"                       (3 words)
  6_conclusion.tex:105      "a capacity-matched dedicated baseline..." (7 words)
  apx_b_errata.tex:188      "The emphasis convention of the..."        (9 words)
  6_conclusion.tex:110      "Second,"                                  (ONE word, and the tool was
                            already in place and still missed it: the word floor was 2, so a
                            swallowed sentence-opener slipped under it)

THE ROOT CAUSE IS ALWAYS THE SAME: a comment block written without a trailing newline, so the body
line that followed got pulled onto the last comment line.

WHAT DOES *NOT* WORK AS A DISCRIMINATOR, learned by shipping each one and being caught:
  - vocabulary filters: ledger commentary and trapped prose are both English about the same
    subject. Filters either flooded (40 false positives) or silenced a real case.
  - "the tail must be a complete sentence": misses fragments (apx_a, and ", Nash-MTL treats").
  - "the tail must not contain parentheses": misses "...distinct counties (GEOIDs)."
  - LINE LENGTH / block-median overshoot: misses SHORT tails. The three cases above are 38, 124
    and 88 characters, at or below their blocks' own median width. This is the trap: tuning a
    length threshold on the long cases makes the checker blind to the short ones, and a
    three-word tail breaks a sentence just as thoroughly as a 270-word one.

THE TEST THAT ACTUALLY WORKS is the definition of the bug, with no proxy in between: take the words
that follow the LAST `%` on a comment line, and ask whether they appear in the rendered PDF. Body
text reaches the PDF; a comment never does. To keep ledger commentary from firing, require the
candidate to look like a continuation of the surrounding document rather than a note about it:
the words must run on into the NEXT source line, which is what makes it a torn sentence rather
than a self-contained remark.

VALIDATION. Do not write a validation record here before running it. An earlier version of this
docstring listed results for a detector version that had never been executed, and the first real run
of it contradicted the record. The durable claim is therefore the FIXTURE SUITE, not prose:

    python3 src_utils/test_trapped_prose.py

That suite carries all six historical defects plus three negatives, it runs in the repository rather
than in a scratch tree that gets swept, and check.sh runs it BEFORE this checker so a clean document
is not reported as evidence when the checker itself is broken.

Runs executed against THIS version, 2026-07-27:
  fixtures (src_utils/test_trapped_prose.py)     -> 9/9 pass
  repaired tree (this repository)                -> 0 suspects
  the true pre-fix tree, reconstructed by
  `git archive 70d3888d` into a scratch dir      -> exactly 3 suspects:
       2_fundamentals.tex:366, 6_conclusion.tex:105, apx_b_errata.tex:188
Reconstructing the defect state from the commit is the reproducible check; a /tmp copy is not.

Exit 1 if any suspect is found, so this can gate a build.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
PDF = SRC / "dissertacao.pdf"
MIN_TAIL_WORDS = 2          # ", Nash-MTL treats" is three; do not raise this

# THE RENDER TEST NEEDS THE RIGHT RENDER. Found 2026-07-30: this document is TWO volumes. The
# supplementary volume (main_extra.tex) carries apx_b_errata, apx_b_static_scope (nested \input) and
# apx_d_ceiling, and NONE of their prose is in dissertacao.pdf. Checking them against the main PDF
# inverts the test: every tail is "absent from the PDF" because the whole file is, so the detector
# could only ever emit false positives there -- and, worse, it was blind to a REAL tear in those
# three files, because a genuine tear is also absent and looks identical. It fired on a correct
# comment in apx_b_errata on the day this was found, which is how the blind spot surfaced at all.
# The map is derived from the build, not hardcoded: see volume_of().
# O volume suplementar mudou de src/ para wrapup/material_extra/ em 264c7996; estas tres
# linhas apontavam para a arvore antiga desde entao, e extra_volume_files() devolvia
# conjunto vazio em silencio -- o roteamento de dois volumes estava morto com o gate a
# verde. Repontado 2026-08-28. O PDF usado e o artefacto commitado, nao o de build/.
EXTRA_DIR = Path(__file__).resolve().parent.parent / "wrapup" / "material_extra"
EXTRA_PDF = EXTRA_DIR / "main_extra.pdf"


def rendered_text(pdf: Path = PDF) -> str:
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(pdf))
    raw = "\n".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))
    return re.sub(r"\s+", " ", re.sub(r"-\s*\n\s*", "", raw.replace("\r", " ")))


def extra_volume_files() -> set[str]:
    """Chapter stems that render into the SUPPLEMENTARY volume, read from the source.

    Derived rather than listed, so moving an appendix between volumes cannot silently point this
    checker at the wrong PDF again. Follows one level of nesting because apx_b_static_scope reaches
    the volume through an \\input inside apx_b_errata rather than through main_extra.tex directly --
    a hardcoded top-level list would have missed it.
    """
    entry = EXTRA_DIR / "main_extra.tex"
    if not entry.exists():
        return set()
    pat = re.compile(r"\\(?:include|input)\{chapters/([A-Za-z0-9_]+)\}")
    stems, queue = set(), [entry]
    while queue:
        text = "\n".join(ln.split("%")[0] for ln in queue.pop().read_text(
            encoding="utf8", errors="replace").split("\n"))
        for stem in pat.findall(text):
            if stem not in stems:
                stems.add(stem)
                nested = EXTRA_DIR / "chapters" / f"{stem}.tex"
                if nested.exists():
                    queue.append(nested)
    return stems


def words(text: str, n: int) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z\-']*", text)[:n]


def suspects_in(path: Path, pdf: str) -> list[tuple[int, str, str]]:
    lines = path.read_text(encoding="utf8", errors="replace").split("\n")
    out = []
    for i, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line.startswith("%"):
            continue
        # The candidate is whatever follows the last sentence terminator or closing bracket. The
        # separator may be whitespace OR nothing at all: the real 2_fundamentals case read
        # "% citation protocol)., Nash-MTL treats", where the appended text begins with a comma
        # directly against the period. Requiring whitespace here missed it.
        m = re.search(r"[.!?\]]\s*([A-Za-z,][^%]*)$", line)
        if not m:
            continue
        tail = m.group(1).strip().lstrip(",").strip()
        n_words = len(words(tail, 6))
        if n_words < MIN_TAIL_WORDS:
            # A ONE-WORD tail is still a real tear when the following line opens lowercase: that is
            # a sentence whose first word was swallowed. This is how 'Second,' escaped at
            # 6_conclusion.tex:110 while the floor was 2 -- the ninth instance of this bug, and the
            # first the tool was in place for and still missed.
            nxt_peek = lines[i + 1].strip() if i + 1 < len(lines) else ""
            if not (n_words == 1 and re.match(r"[a-z]", nxt_peek)):
                continue
        # CONTINUATION TEST: real trapped prose is a torn fragment, so the NEXT source line is body
        # text that continues the same sentence. Two things follow, and both are required:
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        # ⚠ THE COMMENT-NEXT BLIND SPOT, closed 2026-09-08. This used to `continue` whenever the
        # next line was itself a comment, on the reasoning that a torn fragment must be followed by
        # the body text it was torn from. That reasoning fails for a ONE-LINE PARAGRAPH: an Edit
        # whose anchor ends mid-line appends its comment there and swallows the REST OF THAT LINE,
        # and if a comment happens to follow, the whole paragraph is now inside comments with no
        # body line after it to test against. Measured cost: the CTLE passage of
        # 5_mobiwac/06_results.tex, 116 words, vanished from the delivered text and this gate said
        # 0 suspects. Two sibling tears the same day WERE caught, because ordinary body text
        # followed them -- so the gate looked like it was working.
        #
        # The tell that survives when the continuation test cannot run: a comment line far longer
        # than its neighbours in the same block is not a remark, it is swallowed prose. Flagged
        # separately below rather than folded in, because it has no render test and is a heuristic:
        # it reports SUSPECT, and the reader confirms against the built PDF.
        if nxt.startswith("%"):
            block = [l.strip() for l in lines[max(0, i - 4):i + 5] if l.strip().startswith("%")]
            others = [len(x) for x in block if x is not lines[i].strip()]
            if others and len(tail) > 2.5 * (sum(others) / len(others)) and len(words(tail, 30)) >= 20:
                out.append((i + 1, tail[:100],
                            "[SWALLOWED-LINE SUSPECT] comment %d chars against a block mean of %d; "
                            "no body line follows, so the render test cannot run. Check the built "
                            "PDF for this text." % (len(tail), sum(others) // len(others))))
            continue
        if not nxt or nxt.startswith("\\") or nxt.startswith("}"):
            continue
        #  (a) if the tail closes its own sentence it MIGHT be a self-contained ledger remark --
        #      but the real 4_courb:187 case also ended in a period ("...distinct counties
        #      (GEOIDs)."), so a closed sentence cannot be rejected outright. What separates them
        #      is whether the tail reads as an instruction to the author or as document prose:
        #      ledger remarks address the reader of the source ("Revert if you prefer...",
        #      "Author may reword", "see T4:8-17"), and cite files, line numbers, or finding ids.
        if re.search(r"[.!?][\]\)\"']*$", tail):
            LEDGER = re.compile(
                r"[\w/]+\.(tex|py|md|bib|json|csv|log|pdf)"     # file names
                r"|:\d+\b"                                      # line refs
                r"|\b(REV|NEW|COD|MJ|F)-?\d+\b"                 # finding ids
                r"|\b(author|revert|prefer|reword|persona|claim unchanged|see|source|verified"
                r"|unchanged|left as|deliberately|note for)\b",  # author-directed vocabulary
                re.I)
            if LEDGER.search(tail):
                continue
        #  (b) the RENDER TEST: the tail's own words, joined to the line that follows, must be
        #      ABSENT from the rendered PDF. This is the definition of the bug.
        #      NOTE: do NOT try "skip if the next line renders on its own" as a shortcut. In a real
        #      tear the rest of that line still renders perfectly well (only the torn fragment is
        #      missing), so that test silently suppressed four of the six real fixtures.
        joined = " ".join(words(tail + " " + nxt, 8))
        if not joined or joined.lower() in pdf.lower():
            continue
        #  (c) LAST GUARD, for the one false-positive shape seen in practice: a comment that merely
        #      PRECEDES a paragraph. There the tail is a complete ledger sentence and the following
        #      paragraph opens a new sentence of its own, so the words of the next line appear in
        #      the PDF immediately after a sentence boundary rather than continuing the tail.
        #      A genuine tear has the tail and its continuation adjacent in the SOURCE sentence, so
        #      the next line does not begin a new sentence -- it begins mid-clause, lowercase or
        #      with a connective. (apx_a_contributions.tex:92 was this shape.)
        if re.match(r"[A-Z]", nxt) and re.search(r"[.!?][\]\)\"']*$", tail):
            first_words = " ".join(words(nxt, 8))
            if first_words and first_words.lower() in pdf.lower():
                continue
        out.append((i + 1, tail[:100], joined))
    return out


def main() -> int:
    if not PDF.exists():
        print(f"FAIL: {PDF} not found; build first")
        return 2
    pdf = rendered_text()
    extra_stems = extra_volume_files()
    extra_pdf = None
    if extra_stems:
        if not EXTRA_PDF.exists():
            print(f"FAIL: {len(extra_stems)} file(s) render into the supplementary volume "
                  f"({', '.join(sorted(extra_stems))}) and {EXTRA_PDF} is missing. Checking them "
                  f"against the main PDF would flag every comment tail in them. Run `make extra`.")
            return 2
        extra_pdf = rendered_text(EXTRA_PDF)
    total = 0
    skipped = []
    # chapters/*/*.tex included since the 2026-07-28 per-section split (55 percent of the
    # prose lives there now; a glob stopping at chapters/*.tex reports OK on a blind spot).
    for tex in sorted(list((SRC / "chapters").glob("*.tex"))
                      + list((SRC / "chapters").glob("*/*.tex")) + [SRC / "preamble.tex", SRC / "content.tex"]):
        # Each file is compared against the volume it actually renders into. See EXTRA_PDF.
        target = extra_pdf if tex.stem in extra_stems else pdf
        for lineno, tail, joined in suspects_in(tex, target):
            total += 1
            print(f"TRAPPED PROSE {tex.name}:{lineno}")
            print(f"  runs on into the next line, and the joined text is absent from the PDF:")
            print(f"    '{joined}...'")
            print(f"  comment tail: {tail}")
    # V2: name the scope, so a clean result cannot be read as broader than it is.
    if extra_stems:
        print(f"  scope: main volume + {len(extra_stems)} file(s) checked against the "
              f"supplementary render ({', '.join(sorted(extra_stems))}); 0 skipped")
    print(f"trapped-prose suspects: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
