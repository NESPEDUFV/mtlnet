#!/usr/bin/env python3
"""Detect a body line that begins mid-sentence: a torn sentence whose opening clause is GONE.

WHY THIS EXISTS, AND WHY check_trapped_prose.py CANNOT DO IT
------------------------------------------------------------
check_trapped_prose.py finds prose trapped AFTER the last `%` on a comment line. That is a different
defect from this one. Here the text is not trapped anywhere: it is simply absent, the line above is
ordinary body text, and the build is clean.

It happened on 2026-07-27 in the Resumo and Abstract, rendered pages 3 and 4, four times. An
assistant compressing those blocks replaced a span that ENDED at a sentence terminator, and the
replacement dropped the following sentence's opening clause. The page rendered:

    "... through multi-task learning (MTL). sharing parameters between tasks can hurt one of them ..."
    "... at the other two. condition is the finding: whether multi-task learning helps ..."

Two things make this class dangerous. The abstract is the first prose a committee member reads, and
persona 03 found it only because it read the front matter as RENDERED prose rather than as source.

The rule below was proposed by persona 03 in its v3 report and is implemented as it specified: a body
line beginning with a lowercase word whose preceding non-blank body line ends in a sentence
terminator. On the repaired tree it returns zero; on the damaged tree it returned exactly the four
real defects and nothing else.

Usage:  python3 src_utils/check_torn_sentences.py [chapter.tex ...]
Exit 1 when any suspect is found.
"""
from __future__ import annotations

import glob
import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
TERMINATORS = (".", "!", "?")   # NOT ":" -- a colon legitimately introduces a lowercase clause,
                                # which produced two false positives in apx_b_errata.tex on the
                                # first run and no true positives.

# A lowercase opener is legitimate in these constructions, so they are not suspects.
LEGIT_OPENER = re.compile(
    r"""^(?:
        \\[a-zA-Z@]+          # a macro: \item, \cite, \emph, \ref, \input, \addlinespace ...
      | [\[\]{}&$%#_^~()]     # table/math punctuation
      | \d                    # a number continuing a list or a value
      | (?:and|or|but|so|nor|yet|then|with|without|for|from|to|by|as|at|in|on|of|the|a|an)\b
                              # a coordinating word: a genuine mid-sentence wrap
      | (?:e|ou|mas|com|sem|para|de|da|do|em|no|na|por|que|se|a|o|as|os|um|uma)\b
                              # the same in Portuguese
    )""",
    re.X,
)


def body_lines(path: str):
    """(line_number, text) for lines that are neither comments nor blank."""
    out = []
    for n, raw in enumerate(open(path, encoding="utf8", errors="replace").read().split("\n"), 1):
        s = raw.strip()
        if not s or s.startswith("%"):
            continue
        out.append((n, s))
    return out


def suspects(path: str):
    found = []
    lines = body_lines(path)
    for i in range(1, len(lines)):
        n, cur = lines[i]
        _, prev = lines[i - 1]
        if not prev.rstrip().endswith(TERMINATORS):
            continue
        # An ABBREVIATION ending a wrapped line is not a sentence end. Added 2026-08-02, when the
        # author's revised Abstract wrapped after "including one non-U.S." and the next line opened
        # with "dataset." -- correct prose, and the render confirms one continuous sentence on p. 3.
        # The wrap is HIS, present in src_clean before any merge, so the gate would have fired on his
        # tree alone. Matching the abbreviation rather than exempting the file: the next agent who
        # wraps after "et al." or "Fig." should not have to rediscover this.
        if re.search(r"\b(?:U\.S\.|U\.K\.|non-U\.S\.|et al\.|e\.g\.|i\.e\.|cf\.|vs\.|Fig\.|Eq\.|"
                     r"Sec\.|Ch\.|No\.|approx\.|resp\.)$", prev.rstrip()):
            continue
        # the previous line ends a sentence, so this line should open one
        if LEGIT_OPENER.match(cur):
            continue
        first = cur.split()[0] if cur.split() else ""
        if not first or not first[0].islower():
            continue
        # a lowercase word opening a line whose predecessor closed a sentence
        found.append((n, prev[-58:], cur[:70]))
    return found


def main(paths: list[str]) -> int:
    if not paths:
        # chapters/*/*.tex included since the 2026-07-28 per-section split: a glob that
        # stops at chapters/*.tex misses 55 percent of the prose and still reports OK.
        paths = sorted(glob.glob(os.path.join(SRC, "chapters", "*.tex"))) \
              + sorted(glob.glob(os.path.join(SRC, "chapters", "*", "*.tex"))) \
              + sorted(glob.glob(os.path.join(SRC, "tables", "*", "*.tex"))) \
              + [os.path.join(SRC, "preamble.tex"), os.path.join(SRC, "content.tex")]
    total = 0
    for p in paths:
        if not os.path.exists(p):
            continue
        for n, prev, cur in suspects(p):
            total += 1
            rel = os.path.relpath(p, SRC)
            print(f"  TORN SENTENCE  {rel}:{n}")
            print(f"     previous line ends: ...{prev}")
            print(f"     this line opens   : {cur}...")
    print(f"torn-sentence suspects: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
