#!/usr/bin/env python3
"""check_tex_root.py -- every .tex must name a root file that exists.

WHY THIS EXISTS. Two separate defects in one week, both silent:

  * 2026-07-28 (a): six files carried "% !TeX root = ../main_defense.tex" and
    main_defense.tex has never existed in this tree. Every editor opening
    1_introduction.tex, 6_conclusion.tex, apx_a_contributions.tex, apx_b_errata.tex,
    apx_b_static_scope.tex or apx_c_ai_disclosure.tex was pointed at a missing file, so
    build-from-editor was broken for all six.
  * 2026-07-28 (b), found by the LaTeX source persona (E-2): six OTHER files had no
    directive at all, and after the per-section split those six included the three
    paper-chapter masters -- exactly the files an editor opens to navigate the chapters.

Neither is visible from a command-line build: `make` reads main.tex and never looks at a
magic comment. The cost lands on whoever opens a file in an editor and gets a compile of
the wrong document, or no compile at all. That is why it went two rounds unnoticed.

WHAT IT CHECKS. Every .tex under src/ (excluding build/) has a "% !TeX root =" directive on
its FIRST line, and the path it names resolves to a file that exists, relative to the file's
own directory. Both halves matter: defect (a) had a directive that pointed nowhere, defect
(b) had no directive at all.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
DIRECTIVE = re.compile(r"^%\s*!TeX root\s*=\s*(\S+)")


def targets() -> list[Path]:
    return sorted(p for p in SRC.rglob("*.tex") if "build" not in p.parts)


def self_test() -> None:
    assert DIRECTIVE.match("% !TeX root = ../main.tex").group(1) == "../main.tex"
    assert DIRECTIVE.match("%!TeX root=main.tex").group(1) == "main.tex"
    assert DIRECTIVE.match("% a normal comment") is None
    assert DIRECTIVE.match("\\section{x}") is None


def main() -> int:
    self_test()
    problems = []
    for path in targets():
        rel = path.relative_to(SRC)
        first = path.read_text(encoding="utf-8").split("\n")[0]
        m = DIRECTIVE.match(first)
        if not m:
            problems.append((rel, "no '% !TeX root' directive on the first line"))
            continue
        target = (path.parent / m.group(1)).resolve()
        if not target.exists():
            problems.append((rel, f"root '{m.group(1)}' does not exist "
                                  f"(resolves to {target})"))
    for rel, why in problems:
        print(f"{rel}: {why}")
    if problems:
        print(f"\nFAIL: {len(problems)} file(s) with a missing or dangling TeX root. "
              f"An editor cannot build these; a command-line make never notices.")
        return 1
    print(f"OK: {len(targets())} .tex files, every root directive present and resolving")
    return 0


if __name__ == "__main__":
    sys.exit(main())
