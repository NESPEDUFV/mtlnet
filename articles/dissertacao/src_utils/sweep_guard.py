#!/usr/bin/env python3
"""Assert that a text substitution ACTUALLY APPLIED before its result is believed.

WHY THIS EXISTS
---------------
Twice in this project a parameter sweep produced byte-identical results across arms and the identical
results were read as evidence rather than as the tell they were:

  * 2026-07-27, the \needspace sweep in 0_main.tex. A regex had written the macro as
    \needspace{N\\onelineskip} with a doubled backslash. The 8/9/10 arms then substituted with a
    single-backslash pattern that could not match the corrupted form, so those arms never applied.
    Three arms returned pages=104, whole=False and the same p.4 head, and the conclusion drawn from
    them ("needspace never works at any value") was false: correctly escaped, it works.
  * Earlier the same day, a needspace value sweep run through a shell heredoc whose regex raised
    `bad escape \o` on every iteration, printing three identical lines from one unchanged build.

The failure mode is the same both times: a no-op substitution is indistinguishable from a real
measurement unless you check that the file changed.

USAGE
    from sweep_guard import substitute
    new = substitute(text, pattern, replacement, expect=2)   # raises if it did not apply

    for value in values:
        body = substitute(original, PATTERN, f"...{value}...", expect=2)
        write(body); build(); record(value, measure())

Also usable as a check on results:
    assert_distinct(results)   # raises when every arm returned the same thing
"""
from __future__ import annotations

import re


class SubstitutionDidNotApply(AssertionError):
    """The pattern matched nothing, or matched a different number of times than expected."""


def substitute(text: str, pattern: str, replacement: str, expect: int | None = None) -> str:
    """re.sub, but refuses to return silently when nothing changed.

    expect: required number of substitutions. None means "at least one".
    """
    # A replacement string is a TEMPLATE: backslashes in it are escapes. `\o` raises
    # `bad escape \o`, which is precisely how an earlier sweep in this project died silently inside a
    # shell heredoc, printing identical lines from one unchanged build. Escape the replacement unless
    # the caller asked for template semantics with backreferences.
    if not re.search(r'\\[1-9g]', replacement):
        replacement = replacement.replace("\\", "\\\\")
    try:
        new, n = re.subn(pattern, replacement, text)
    except re.error as exc:
        raise SubstitutionDidNotApply(
            f"the pattern or replacement is not valid regex: {exc}\n"
            f"  pattern={pattern!r}\n  replacement={replacement!r}\n"
            f"  This raises rather than returning the input unchanged, because an unchanged input\n"
            f"  makes the next measurement a measurement of the previous state."
        ) from exc
    if n == 0:
        raise SubstitutionDidNotApply(
            f"pattern matched NOTHING: {pattern!r}\n"
            f"  the file is unchanged, so any measurement taken after this is a measurement of the\n"
            f"  PREVIOUS state. Check the escaping: a doubled backslash in the target is the usual cause."
        )
    if expect is not None and n != expect:
        raise SubstitutionDidNotApply(
            f"pattern applied {n} time(s), expected {expect}: {pattern!r}"
        )
    if new == text:
        raise SubstitutionDidNotApply(
            f"pattern matched {n} time(s) but the text is IDENTICAL: {pattern!r}\n"
            f"  the replacement equals what was already there; the arm is a no-op."
        )
    return new


def assert_distinct(results: dict | list, label: str = "sweep") -> None:
    """Raise when every arm of a sweep returned the same value.

    Identical results across arms are occasionally real, but they are far more often a sign that the
    arms never differed. Raising forces the question to be answered explicitly.
    """
    values = list(results.values()) if isinstance(results, dict) else list(results)
    if len(values) < 2:
        return
    if len({repr(v) for v in values}) == 1:
        raise AssertionError(
            f"{label}: all {len(values)} arms returned {values[0]!r}.\n"
            f"  Before believing this, verify each arm CHANGED the input. A substitution that matched\n"
            f"  nothing yields identical results and looks exactly like a real null."
        )


if __name__ == "__main__":
    # The historical case, as a regression test: the corrupted form must be caught, not silently missed.
    corrupted = r"\needspace{7\\onelineskip}"
    single = r"needspace\{\d+\\onelineskip\}"
    try:
        substitute(corrupted, single, "needspace{8\\onelineskip}", expect=1)
        raise SystemExit("FAIL: the single-backslash pattern was allowed to no-op on the doubled form")
    except SubstitutionDidNotApply:
        print("ok: a pattern that cannot match the corrupted macro now raises instead of no-opping")

    # The same case WITHOUT expect=, so the n == 0 branch itself is exercised. Without this the
    # expect= check masks it, and disabling `if n == 0` leaves every test passing (found 2026-07-27
    # by breaking the guard on purpose and watching the suite stay green).
    try:
        substitute(corrupted, single, "needspace{8\\onelineskip}")
        raise SystemExit("FAIL: a zero-match substitution returned silently with no expect= given")
    except SubstitutionDidNotApply as exc:
        assert "matched NOTHING" in str(exc), f"wrong branch caught it: {exc}"
        print("ok: a zero-match substitution raises even when no expect= is given")
    try:
        assert_distinct({8: "104pp/False", 9: "104pp/False", 10: "104pp/False"}, "needspace sweep")
        raise SystemExit("FAIL: three identical arms were accepted as a result")
    except AssertionError:
        print("ok: identical arms across a sweep now raise instead of reading as evidence")
    good = substitute(r"\needspace{7\onelineskip}", single, "needspace{8\\onelineskip}", expect=1)
    print("ok: a correctly escaped target still substitutes ->", good)
