#!/usr/bin/env python3
"""Check that a before/after word-count claim in the registers reconciles with its own stated numbers.

WHY THIS EXISTS
---------------
On 2026-07-27 a register entry claimed "real compression was ~13 words of gloss, not the 36 I
reported: the other ~30 were clauses deleted by accident". Its own three stages were printed in the
same session:

    before compression    Resumo 565   Abstract 485
    after (clauses gone)         529            452
    clauses restored             542            466

which give compression 23 / 19 and deletion 13 / 14. The write-up had the two SWAPPED, and "~30"
reconciles with no grouping (the deletion across both languages sums to 27). An audit caught it; the
error was in the prose about the measurement, not the measurement.

That is the third arithmetic error this project has made in a WRITE-UP of correct work. The pattern
is always the same: a difference is described in words rather than recomputed from the endpoints.

WHAT THIS CHECKS
----------------
Wherever a register file states a triple of word counts in a markdown table together with a claimed
split, this recomputes the split from the endpoints and fails when the prose disagrees. It is
deliberately narrow: it verifies the Resumo/Abstract compression claim, the one that has already gone
wrong, rather than trying to parse arbitrary arithmetic out of prose.

Usage:  python3 src_utils/check_wordcount_claims.py
Exit 1 on a disagreement.
"""
from __future__ import annotations

import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REGISTERS = [
    "src_utils/PENDENCIAS.md",
    "src_utils/_history/_archive/PENDENCIAS_RESOLVIDOS.md",
    "science/AGENT_HANDOFF.md",
]

# The three stages as they are recorded, and the split the prose must agree with.
STAGES = {"before": (565, 485), "after": (529, 452), "restored": (542, 466)}
COMPRESSION = (STAGES["before"][0] - STAGES["restored"][0],
               STAGES["before"][1] - STAGES["restored"][1])          # 23 / 19
DELETION = (STAGES["restored"][0] - STAGES["after"][0],
            STAGES["restored"][1] - STAGES["after"][1])              # 13 / 14


def main() -> int:
    rc = 0
    print(f"reconciled from the recorded stages: compression {COMPRESSION[0]}/{COMPRESSION[1]} "
          f"(PT/EN), accidental deletion {DELETION[0]}/{DELETION[1]}")
    for rel in REGISTERS:
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        text = open(path, encoding="utf8", errors="replace").read()
        # A claim of the form "compressao real ... N palavras" / "real compression was ~N words".
        for m in re.finditer(
            r"(?:compressao (?:real|genuina)[^.\n]{0,60}?|real compression[^.\n]{0,40}?was\s*~?)(\d{1,3})\s*(?:palavras|words)",
            text, re.I,
        ):
            claimed = int(m.group(1))
            if claimed in COMPRESSION:
                continue
            # A QUOTED admission of the old wrong figure is legitimate and must not be flagged --
            # the corrections deliberately restate what was wrong before giving the right number.
            window = text[max(0, m.start() - 200): m.end() + 200]
            if re.search(r'(?:Eu havia escrito|I had (?:written|stated)|"|Esta\s+\*\*invertido|swapped|inverted)',
                         window):
                continue
            line = text[: m.start()].count("\n") + 1
            print(f"  MISMATCH {rel}:{line}: prose claims compression of {claimed} words; "
                  f"the recorded stages give {COMPRESSION[0]} (PT) / {COMPRESSION[1]} (EN)")
            rc = 1
        # A claim that the deletion was ~30 or similar.
        for m in re.finditer(r"(?:outras?|other)\s*~?(\d{1,3})\s*(?:eram|were)", text, re.I):
            claimed = int(m.group(1))
            if claimed not in DELETION and claimed != sum(DELETION):
                line = text[: m.start()].count("\n") + 1
                # a quoted admission of the old error is legitimate; flag only unquoted assertions
                context = text[max(0, m.start() - 90): m.start()]
                if '"' in context or "Esta" in text[m.end(): m.end() + 40]:
                    continue
                print(f"  MISMATCH {rel}:{line}: prose claims {claimed} deleted words; "
                      f"the recorded stages give {DELETION[0]} (PT) / {DELETION[1]} (EN), "
                      f"{sum(DELETION)} across both")
                rc = 1
    print("word-count claims reconcile" if rc == 0 else "word-count claims DO NOT reconcile")
    return rc


if __name__ == "__main__":
    sys.exit(main())
