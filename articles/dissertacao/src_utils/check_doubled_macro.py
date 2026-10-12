#!/usr/bin/env python3
"""check_doubled_macro.py -- catch `\\\\ref{...}` where `\\ref{...}` was meant.

WHY THIS EXISTS. On 2026-07-28 the claim-scoping pass found two cross-references in
chapters/5_mobiwac.tex written with a DOUBLED backslash. In LaTeX that is a line break
followed by the literal characters "ref{...}", so page 75 of the defense PDF printed the
raw label text to the reader. And NO EXISTING GATE COULD SEE IT:

  * pdflatex raises no warning. `\\\\` is legal and `ref{tab:x}` is legal text.
  * `undef_ref` stays at 0. There is no reference to resolve, so nothing goes undefined.
    Every build report since the defect landed said undef_ref=0, truthfully.
  * check.sh does not look for it, and the torn-sentence and trapped-prose checkers are
    looking for other shapes.

The whole class is invisible to a build that succeeds. That is what makes it worth a
dedicated checker: this repository's standing failure mode is a defect that every
instrument reports as clean (AGENT_HANDOFF section 2.3).

WHAT IT CHECKS. Comment-stripped source only -- a comment quoting the defect (this
round's own provenance comments do) is not a defect. Any of the reference-like macros
below preceded by an even number of backslashes greater than one is a hit.

Exit 1 on any hit, 0 on none. Validated in BOTH directions before being trusted
(AGENT_GUARDRAILS section 7): the self-test below reconstructs the original defect and
asserts the checker fails on it, then asserts it passes on the corrected form.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

# Macros whose doubled form is silent: they take an argument and produce no warning when
# the backslash is doubled, because the argument text is legal prose.
MACROS = ("ref", "cite", "citeonline", "eqref", "autoref", "pageref", "nameref",
          "citet", "citep", "textcite", "input", "include", "label")

# An even run of 2+ backslashes before the macro name. One backslash is correct;
# two is `\\` (line break) plus literal text; three is `\\\` which is also wrong.
PATTERN = re.compile(r"(?<!\\)(\\{2,})(" + "|".join(MACROS) + r")\s*\{")


def strip_comments(text: str) -> str:
    """Blank out LaTeX comments, preserving line numbering and escaped percent signs."""
    out = []
    for line in text.split("\n"):
        buf = []
        i = 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            buf.append(line[i])
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def scan(text: str):
    """Return [(lineno, macro, snippet)] for every doubled-macro hit in `text`."""
    hits = []
    for lineno, line in enumerate(strip_comments(text).split("\n"), 1):
        for m in PATTERN.finditer(line):
            hits.append((lineno, m.group(2), line.strip()[:110]))
    return hits


def self_test() -> None:
    """Validate the checker in both directions before its verdict is used."""
    broken = r"as reported in Table~\\ref{tab:mobiwac:results} and \\cite{silva2025mtlnet}."
    fixed = r"as reported in Table~\ref{tab:mobiwac:results} and \cite{silva2025mtlnet}."
    commented = r"% the defect was written \\ref{tab:x}, which prints literal text"
    assert len(scan(broken)) == 2, f"must catch the defect, got {scan(broken)}"
    assert scan(fixed) == [], f"must pass correct source, got {scan(fixed)}"
    assert scan(commented) == [], f"must ignore comments, got {scan(commented)}"
    # a real line break followed by ordinary prose is not a hit
    assert scan(r"first line \\ second line") == []


def main() -> int:
    self_test()
    # chapters/*.tex AND chapters/*/*.tex: the three paper chapters were split into
    # per-section files on 2026-07-28, and a glob that stops at chapters/*.tex misses 55
    # percent of the document's prose while still reporting OK.
    files = sorted(SRC.glob("*.tex")) + sorted(SRC.glob("chapters/*.tex")) + \
        sorted(SRC.glob("chapters/*/*.tex")) + sorted(SRC.glob("tables/*/*.tex"))
    total = 0
    for path in files:
        for lineno, macro, snippet in scan(path.read_text(encoding="utf-8")):
            rel = path.relative_to(SRC)
            print(f"{rel}:{lineno}: doubled backslash before \\{macro} -> {snippet}")
            total += 1
    if total:
        print(f"\nFAIL: {total} doubled-macro site(s). These render as literal text and "
              f"raise no LaTeX warning.")
        return 1
    print(f"OK: no doubled reference macros in {len(files)} files "
          f"(checker self-test passed in both directions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
