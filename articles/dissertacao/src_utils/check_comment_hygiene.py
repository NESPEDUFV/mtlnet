#!/usr/bin/env python3
"""Two MECHANICAL comment-hygiene defects, gated so they cannot come back.

WHY THIS EXISTS
---------------
Round 7 (2026-07-29) measured the comments in the build files rather than the chapters, and
found the defect there is not fact-free commentary -- it is DUPLICATION plus one wrong
self-description:

  * the "three builds, one source" story was told in 5 files,
  * the nested-\\if scanning hazard in 4,
  * the usermode TeX tree in 4,
  * -halt-on-error vs nonstopmode in 5,
  * and "main_ppgc.tex is N lines of content" in 7 places, THREE of which said "four lines"
    for a file with 2 content lines.

Both classes are mechanically checkable, and neither is caught by any existing gate. This one
checks them:

  CLASS A -- a canonical story duplicated across files. Each story is fingerprinted by a set of
    regexes; a file counts as TELLING the story only when it matches the story's TELL pattern
    (the substantive explanation), not merely mentioning the subject. One canonical home is
    declared per story; every other file may hold at most a POINTER. A second full telling
    fails.

  CLASS B -- a self-describing count that disagrees with the file it describes. The tree
    carried exactly this on 2026-07-29: three files claimed main_ppgc.tex was a "four-line
    file" while it has two content lines. The check reads the described file and compares.

VALIDATION IN BOTH DIRECTIONS IS NOT OPTIONAL HERE
--------------------------------------------------
Four of this repository's checkers were wrong at least once by being tuned only on the case in
front of them (AGENT_GUARDRAILS §7). --selftest builds synthetic trees carrying each defect and
asserts this checker FAILS on them, then asserts it passes on the fixed form. It runs before any
verdict is printed, and a failing self-test makes the gate report itself broken rather than
report a clean tree.

Both classes were then validated against the REAL historical tree, not only synthetic fixtures.
The pre-fix tree was reconstructed from commit 0bfc9e5e with `git show` (a `git worktree` attempt
failed with "Operation not permitted" and left an EMPTY directory, against which this checker
reported 0 findings -- a reading that measured nothing and was discarded; never accept a clean
result without confirming the tree under test exists). Measured on the reconstructed tree, with
the run's own output copied here:

  CLASS B, pre-fix: 3 findings -- src/main_ppgc.tex:8, src/main.tex:12, src/Makefile:35, each
    claiming 4 lines where main_ppgc.tex has 2 content lines. CLASS B, fixed tree: 0.
  CLASS A, pre-fix: 1 finding -- src_utils/README_SRC.md told "three builds, one source" in full
    alongside its canonical home src/main.tex. CLASS A, fixed tree: 0.

THE FIRST VERSION OF THIS NOTE WAS WRONG, and the way it was wrong is the point. It was written
BEFORE the validation ran, from what the check was expected to do: it claimed 2 violations and
named src/main.tex as one of the two caught. The first real run found src/main_ppgc.tex:8 and
src/Makefile:35 -- and MISSED src/main.tex:12. So the file the note credited as detected was the
one copy the checker could not see. That is root cause R1/R2 of AGENT_GUARDRAILS §4b in a single
sentence, committed inside the gate written to prevent it.

Why main.tex:12 escaped, stated exactly (a later draft of this paragraph got the direction wrong
too, which is its own small lesson about describing a window from memory). At 0bfc9e5e the header
reads, on consecutive lines 10-12: "main_ppgc.tex -> the SAME defense PDF ..." / "build/
main_ppgc.pdf. That is its ONLY difference ..." / "... it is a four-line file". The subject is
therefore TWO LINES ABOVE the count. The original window was `line + next line` -- one line
FORWARD and none backward -- so from line 12 it could not see line 10. The window is now the
surrounding comment paragraph, up to 6 lines back and 2 forward (see check_counts), after which
all three copies are found. Do not write a measurement into this file before reading the output.

    python3 src_utils/check_comment_hygiene.py             # gate: exit 0 clean, 1 on a finding
    python3 src_utils/check_comment_hygiene.py --selftest   # both-directions validation only
    python3 src_utils/check_comment_hygiene.py --verbose    # also list every pointer accepted
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

DISS = Path(__file__).resolve().parent.parent

# --------------------------------------------------------------------------------------------
# CLASS A -- canonical stories.
#
# Each story declares:
#   canonical : the ONE file allowed to carry the full explanation. Chosen as the file where a
#               reader needs it at the moment they need it -- for the build shape that is
#               src/main.tex, because src_utils/README_SRC.md lives outside src/ and does not
#               travel with an Overleaf paste of the source.
#   tell      : a regex matching the SUBSTANTIVE telling. Deliberately narrow: a pointer such as
#               "see the main.tex header" must NOT match, or every pointer would read as a
#               duplicate and the gate would fight its own fix.
#   scope     : files to examine. Frozen audit trails (_round*/, _review_v*/, _history/_archive/,
#               _specialists_v*/, CODEX_*.md, codex_reviewer.md, PENDENCIAS.md) are NOT in scope:
#               they are historical records of what was true when written, and rewriting them to
#               remove a duplicate would falsify the record. Same exclusion rule every rename in
#               LATEX_UPGRADE.md uses.
# --------------------------------------------------------------------------------------------
SCOPE = [
    "src/main.tex", "src/main_ppgc.tex", "src/main_academico.tex",
    "src/preamble.tex", "src/content.tex",
    "src/Makefile", "src_utils/README_SRC.md", "CLAUDE.md", "archive/PLAN.md",
    # Added 2026-07-29 after the round-7 correction: this file was the one place a wrong count
    # could still be introduced unguarded, and it is where a coordinate had ALREADY drifted
    # (:154 and :215 cite main_ppgc.tex:9; the assertion was at :8). It is safe to include only
    # because REPORTED exempts reported speech -- without that, its two historical references to
    # the defect produced 4 false positives, from 2 lines (:154 and :215) that each name two
    # filenames and so are reported once per match. Verified by neutralizing REPORTED and
    # re-running: 0 findings with the guard, those same 4 without it.
    # Frozen audit trails stay OUT (_round*/ , _review*/):
    # they record what was true when written and must not be edited to satisfy a gate.
    "src_utils/LATEX_UPGRADE.md",
    # Added 2026-07-29 (round 8 audit) -- T2, a checker whose scope silently missed files. SCOPE was
    # a hand-written list of the files that existed when the gate was written, so the two build
    # scripts and the fourth entry file were never examined. Measured before the extension by
    # running the story patterns over every non-frozen file NOT in SCOPE: the
    # halt-on-error-vs-nonstopmode story matched in src_utils/build.sh and src_utils/fastbuild.sh,
    # neither carrying a pointer -- i.e. two full re-tellings the gate reported clean, which is the
    # very duplication it exists to prevent. main_extra.tex is here because it is the fourth entry
    # file and it self-describes a "four-line layout unit" (a claim about preamble.tex, not about
    # itself, so CLASS B does not fire on it -- but the file must be in scope for a future count
    # claim about a counted file to be caught).
    "src_utils/build.sh", "src_utils/fastbuild.sh", "src_utils/latexbuild.sh",
    "wrapup/material_extra/main_extra.tex",   # moved out of the shipping tree at 264c7996
]

# A SCOPE that a refactor can shrink without error is the T2 defect this gate was itself carrying.
# The floor is asserted at run time: if the list ever drops below the number of files present when
# it was last audited, the gate says so instead of reporting a clean tree over a smaller sample.
SCOPE_FLOOR = 12

STORIES = [
    {
        "id": "three-builds-one-source",
        "canonical": "src/main.tex",
        # The full telling enumerates the builds AND their entry files or switches. A line that
        # merely says "three builds, one source" in passing is a pointer, not a telling.
        "tell": re.compile(
            r"(THREE|three)\s+(builds|targets).{0,80}(ONE|one)\s+source"
            r"(?:.|\n){0,400}?(?:\\ifdefensebuild|\\FINALBUILD|\\APPROVALSHEET|entry file)",
            re.I),
    },
    {
        "id": "nested-if-scanning-hazard",
        "canonical": "src/main.tex",
        # A telling explains the MECHANISM (scanning / \fi counting / why \ifdefined avoids it).
        "tell": re.compile(
            r"nested[- ]\\+if(?:.|\n){0,400}?"
            r"(?:scan|\\fi|counts every|miscount|primitive)", re.I),
    },
    {
        "id": "halt-on-error-vs-nonstopmode",
        "canonical": "src_utils/README_SRC.md",
        # The telling is the two-tools-disagree LESSON, not the mere presence of a flag in a
        # recipe: src/Makefile legitimately CONTAINS -halt-on-error without explaining it, and
        # build.sh legitimately contains nonstopmode. So the pattern requires nonstopmode near
        # the word "recover" -- that pairing is the explanation and nothing else uses it.
        # ANCHORED ON THE REAL TEXT, not on what the pattern's author imagined it said: the
        # canonical telling is README_SRC.md's "`build.sh` runs `-interaction=nonstopmode`, under
        # which pdflatex **recovers** from an error and still writes a PDF". An earlier version of
        # this regex demanded "halt-on-error" or "no PDF" within 300 characters AFTER "recover"
        # and matched NOTHING -- the canonical home showed 0 tellers and the story therefore
        # passed vacuously, which is the "gate that has never fired" defect in AGENT_GUARDRAILS
        # §7. Verified after the fix: this story reports src_utils/README_SRC.md as its teller.
        "tell": re.compile(r"nonstopmode(?:.|\n){0,120}?recover", re.I),
    },
]

# A story must be TOLD SOMEWHERE. A story whose canonical home stopped matching would otherwise
# pass with zero tellers -- exactly the vacuous-gate failure this file's §7 note describes. Any
# story listed here is asserted to have at least its canonical teller.
REQUIRE_CANONICAL_TELLER = True

POINTER = re.compile(
    r"(?:see|read it|documented|canonical|explained|reasoning|full (?:reasoning|story)|"
    r"points? (?:here|at|to)|described)\b", re.I)

# --------------------------------------------------------------------------------------------
# CLASS B -- self-describing counts.
#
# A claim of the form "<file> is a <N>-line file" / "<N> lines of content" is checked against
# the file it names. "Content lines" = non-blank lines that are not comments, which is the
# convention every one of the seven copies of this claim was using.
# --------------------------------------------------------------------------------------------
NUMWORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
           "seven": 7, "eight": 8, "nine": 9, "ten": 10}

# Reported speech: the text is QUOTING a count rather than asserting one. A finding that reads
# `main.tex:12 says "four-line file"` documents the defect; the gate must not demand its deletion.
# Deliberately narrow -- each verb must sit next to the count, and a quotation mark alone is not
# enough (a correct claim may legitimately be quoted).
# "read"/"reads" is deliberately ABSENT: a shim comment saying it "reads main.tex" is an
# assertion, and including that verb silenced the self-test's own defective fixture
# ("% main_ppgc.tex is a four-line file that sets one switch and reads this one"). The self-test
# caught it on the run that introduced it, which is the entire reason the self-test runs first.
REPORTED = re.compile(
    r"\b(?:says?|said|claim(?:s|ed)?|assert(?:s|ed)?|state[sd]?|"
    r"describ(?:e[sd]?|ing)\s+\w+\s+as|contradiction|errata|"
    r"used\s+to\s+say|was\s+wrong|no\s+longer)\b", re.I)

# Matches "four-line file", "two lines of content", "TWO lines of content", "2-line file".
#
# TWO NARROWINGS, each from a false positive this check produced on the real tree before it was
# wired in (V3: prove the instrument can see the defect, and interrogate what else it sees):
#
#  1. `(?<![\d.])` and `(?![\d.])` exclude a DECIMAL. Without them, 0_main.tex's "1.5 line
#     spacing" -- the UFV manual's line-spacing specification -- parsed as a claim of "5 lines"
#     and was reported as a wrong count. A line-spacing figure is not a line count.
#  2. The claim must be about CONTENT: "N lines of content", "N-line file", or "N-line shim".
#     A bare "N lines" is ordinary prose ("eleven lines of provenance comment", "two lines
#     plus a pointer") and says nothing about any file's length.
# Three accepted shapes, and only three:
#   1. "N lines of content" / "N-line file" / "N-line shim"  -- says so in words
#   2. "N-line"  HYPHENATED and SINGULAR                     -- adjectival, modifies the file
#   3. (nothing else)
# Shape 2 is what CLAUDE.md actually carries, and it needed its own alternate: its text reads
# "from a two-line" / "`main_ppgc.tex`" across a line break, with the FILENAME as the noun the
# adjective modifies -- the word "file" never appears. A first version of this pattern demanded
# file|shim|of-content and silently did not see it, which is the same wrong-question defect the
# decimal false positive was. The hyphenated singular is what makes shape 2 safe: ordinary prose
# writes "eleven lines of provenance comment" (plural, unhyphenated) and the manual writes
# "1.5 line spacing" (decimal, unhyphenated); neither can match.
NUMS = r"\d+|one|two|three|four|five|six|seven|eight|nine|ten"
COUNT_CLAIM = re.compile(
    rf"(?<![\d.])(?P<num>{NUMS})(?![\d.])\s*(?:-|\s)\s*lines?\s+(?:of\s+content|file|shim)"
    rf"|(?<![\d.])(?P<num2>{NUMS})(?![\d.])-line\b", re.I)

# Which file a claim describes: the nearest filename on the same line, else the file the claim
# lives in (a file describing itself, e.g. main_ppgc.tex's own header).
FILENAME = re.compile(r"\b([\w./-]+\.(?:tex|md|sh|py))\b")

# Both two-line shims self-describe, so both are checked. Extend this when another file starts
# describing its own length. main_academico.tex was added on 2026-07-29, the day it was created
# by the rename track -- it carries the same "TWO lines of content" sentence main_ppgc.tex does,
# which is exactly the claim that was wrong in three places before this gate existed.
COUNTED_FILES = ["src/main_ppgc.tex", "src/main_academico.tex"]


def content_lines(path: Path, marker: str) -> int:
    """Non-blank, non-comment lines. The convention the claims themselves use."""
    n = 0
    for line in path.read_text(encoding="utf8").splitlines():
        s = line.strip()
        if not s or s.startswith(marker):
            continue
        n += 1
    return n


def marker_for(path: Path) -> str:
    return "#" if path.name == "Makefile" or path.suffix in (".sh", ".py") else "%"


def comment_text(path: Path) -> str:
    """Only the COMMENT lines of a source file; markdown is returned whole.

    A story told in LaTeX/Make comments is what this gate is about. For .md there is no
    comment marker -- the whole file is prose -- so it is examined entirely.
    """
    if path.suffix == ".md":
        return path.read_text(encoding="utf8")
    marker = marker_for(path)
    keep = [l for l in path.read_text(encoding="utf8").splitlines()
            if l.strip().startswith(marker)]
    return "\n".join(keep)


def check_stories(root: Path, scope: list[str], verbose: bool = False) -> list[str]:
    problems = []
    for story in STORIES:
        tellers = []
        for rel in scope:
            p = root / rel
            if not p.exists():
                continue
            if story["tell"].search(comment_text(p)):
                tellers.append(rel)
        extra = [t for t in tellers if t != story["canonical"]]
        if story["canonical"] not in tellers:
            if tellers:
                problems.append(
                    f"story '{story['id']}': the canonical home {story['canonical']} no longer "
                    f"tells it, but {', '.join(extra)} do(es). Either restore it there or move "
                    f"the canonical declaration.")
            elif REQUIRE_CANONICAL_TELLER:
                # Zero tellers is NOT a pass. Either the story was deleted from the tree, or this
                # story's `tell` pattern has drifted from the text and the check is now vacuous.
                problems.append(
                    f"story '{story['id']}': NOBODY tells it, including its canonical home "
                    f"{story['canonical']}. Either the explanation was lost, or this story's "
                    f"`tell` pattern no longer matches the text it was written for -- a story "
                    f"with zero tellers passes vacuously and must never be reported as clean.")
            continue
        for rel in extra:
            body = comment_text(root / rel)
            m = story["tell"].search(body)
            window = body[max(0, m.start() - 200):m.end() + 200] if m else ""
            hint = "" if POINTER.search(window) else " (and it carries no pointer either)"
            problems.append(
                f"story '{story['id']}': told in FULL in {rel} as well as its canonical home "
                f"{story['canonical']}{hint}. Reduce {rel} to a pointer.")
        if verbose:
            print(f"    story '{story['id']}': canonical={story['canonical']} "
                  f"tellers={tellers or ['none']}")
    return problems


def check_counts(root: Path, scope: list[str], counted: list[str],
                 verbose: bool = False) -> list[str]:
    problems = []
    truth = {}
    for rel in counted:
        p = root / rel
        if p.exists():
            truth[Path(rel).name] = (content_lines(p, marker_for(p)), rel)
    if not truth:
        return problems
    checked = 0
    for rel in scope:
        p = root / rel
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf8").splitlines()
        for lineno, line in enumerate(raw, 1):
            # A WRAPPED claim must still be one claim, and the subject can be SEVERAL lines from
            # the count. Two real shapes prove both directions are needed:
            #   CLAUDE.md      "... from a two-line" / "`main_ppgc.tex` that sets one switch"
            #                  -> subject one line AFTER the count
            #   main.tex (pre-fix, 0bfc9e5e:10-12)
            #                  "main_ppgc.tex -> the SAME defense PDF ..." / "build/main_ppgc.pdf.
            #                  That is its ONLY difference ..." / "... it is a four-line file"
            #                  -> subject TWO lines BEFORE the count (0bfc9e5e:10 vs :12)
            # A line-at-a-time scan sees a count with no filename and a filename with no count and
            # reports neither. That is root cause R2 in AGENT_GUARDRAILS §4b -- a line-based grep
            # missing a match that shares a boundary -- which cost this repository an 8-of-12 that
            # was really 9-of-13. The window is therefore the surrounding COMMENT PARAGRAPH: back
            # to the last blank/non-comment line, capped at 6 lines back and 2 forward so it can
            # never reach across into an unrelated block.
            lo = lineno - 1
            back = 0
            while lo - 1 >= 0 and back < 6:
                prev = raw[lo - 1].strip()
                if not prev or prev in ("%", "#", "%%"):
                    break
                lo -= 1
                back += 1
            hi = min(len(raw), lineno + 2)
            window = " ".join(raw[lo:hi])
            named = [n for n in FILENAME.findall(window) if n.split("/")[-1] in truth]
            # A file may describe ITSELF without naming itself at all ("This file is deliberately
            # two lines of content"). That fallback only applies when THIS file is one of the
            # counted files -- otherwise a stray "N lines of content" in a file that merely
            # MENTIONS a counted file would be attributed to it.
            #
            # THE FALSE POSITIVE THAT MOTIVATED BOTH GUARDS, described accurately because an
            # earlier version of this comment blamed the wrong one. 0_main.tex's header carries
            #   "%%       \OnehalfSpacing enforced (manual §7: 1.5 line spacing)."
            #   "%% Compile with pdflatex via main.tex (defense), main_ppgc.tex (defense + ...)"
            # on CONSECUTIVE lines. The subject came from the FORWARD half of the window (the next
            # line genuinely names main_ppgc.tex), not from the self-description fallback -- so the
            # fix that mattered was the decimal exclusion in COUNT_CLAIM, which stops "1.5 line
            # spacing" being read as "5 lines". The `rel in counted` restriction above is a second,
            # independent narrowing and was not what cleared this case.
            if not named:
                if p.name in truth and rel in counted:
                    named = [p.name]
                else:
                    continue
            cm = COUNT_CLAIM.search(window)
            if not cm:
                continue
            # Only report on the line that carries the COUNT, so a wrapped claim is reported once
            # rather than twice (once for its own line and once for the previous line's window).
            if not COUNT_CLAIM.search(line):
                continue
            # REPORTED SPEECH IS NOT AN ASSERTION. A finding, errata row or post-mortem that says
            # `main.tex:12 SAYS "four-line file"` is the RECORD that the claim was wrong; flagging
            # it would make the gate demand the deletion of its own evidence, and the exclusion of
            # frozen audit trails from SCOPE is the same principle applied at file granularity.
            #
            # This mattered the moment it was written. src_utils/LATEX_UPGRADE.md was outside SCOPE,
            # so a wrong count could be introduced there unguarded -- and that file is precisely
            # where a coordinate HAD already drifted (:154 and :215 both cite main_ppgc.tex:9; the
            # assertion was at :8). Adding it to SCOPE without this guard produced 4 false
            # positives on its two historical references. With the guard it is in scope and clean,
            # so a NEW wrong assertion there is caught while the record of the old one survives.
            #
            # HOW THAT WAS ESTABLISHED, so the claim is a measurement and not an intention: the
            # file was added to SCOPE (see the list above, 9 entries), then check_counts was run
            # twice over the real tree -- once as shipped and once with REPORTED replaced by a
            # pattern matching nothing. As shipped: 0 findings. Guard neutralized: 4, all in
            # LATEX_UPGRADE.md. Two self-tests below pin both directions so this cannot silently
            # regress: a finding QUOTING a wrong count must pass, and an assertion containing a
            # verb like "reads" must still fire.
            # Scoped to the CLAIM'S OWN LINE, not the window. Tested: with the window, an
            # unrelated neighbouring sentence containing "defect" silenced a genuine wrong
            # assertion on the next line -- a gate that can be muted by an adjacent word is worse
            # than one false positive. The cost of the narrower form is that a finding which wraps
            # its verb onto the previous line is still flagged; that is a visible false positive a
            # reader can dismiss, not a silent miss.
            if REPORTED.search(line):
                continue
            # The pattern has two alternates ("N lines of content|file|shim" and "N-line
            # file|shim"), so the number lands in whichever group matched.
            numtok = (cm.group("num") or cm.group("num2")).lower()
            claimed = int(numtok) if numtok.isdigit() else NUMWORD[numtok]
            for n in named:
                real, realrel = truth[n.split("/")[-1]]
                checked += 1
                if claimed != real:
                    problems.append(
                        f"{rel}:{lineno} claims {n} has {claimed} lines; {realrel} has {real} "
                        f"content lines. Measure it: "
                        f"grep -v '^[[:space:]]*%' {realrel} | grep -cv '^[[:space:]]*$'"
                        f"  --  {line.strip()[:90]}")
                elif verbose:
                    print(f"    OK {rel}:{lineno} claims {claimed} for {n} (real {real})")
    if verbose:
        print(f"    count claims examined: {checked}")
    return problems


# --------------------------------------------------------------------------------------------
# Self-test: BOTH directions, on synthetic trees, before any verdict is printed.
# --------------------------------------------------------------------------------------------
def _write(root: Path, rel: str, body: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf8")


def selftest() -> bool:
    ok = True
    results = []

    CANON_TELL = (
        "% THREE builds, ONE source. Two entry files, and this is the main one:\n"
        "%   main.tex -> the DEFENSE PDF.\n"
        "%   \\ifdefensebuild selects the front matter.\n"
        "% nested-\\if scanning problem: TeX skips the untaken branch by scanning for \\fi and\n"
        "% counts every \\if it passes, so \\ifdefined is used because it is a single primitive.\n")
    PPGC_2 = "% header only\n\\def\\APPROVALSHEET{}\n\\input{main.tex}\n"

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # ---- direction 1: DEFECTIVE tree, class A (story told twice in full) ----
        _write(root, "src/main.tex", CANON_TELL)
        _write(root, "src/main_ppgc.tex", PPGC_2)
        _write(root, "src_utils/README_SRC.md",
               "THREE targets, ONE source. Two switches select among them, both using the same\n"
               "`\\ifdefined` pattern, and here is the whole entry file table again.\n")
        probs = check_stories(root, ["src/main.tex", "src_utils/README_SRC.md"])
        hit = any("three-builds-one-source" in p for p in probs)
        results.append(("A: duplicate full telling is DETECTED", hit))
        ok &= hit

        # ---- direction 2: FIXED tree, class A (second file reduced to a pointer) ----
        _write(root, "src_utils/README_SRC.md",
               "THREE targets, ONE source, selected by two switches.\n"
               "The canonical explanation lives in the src/main.tex header; read it there.\n")
        probs = check_stories(root, ["src/main.tex", "src_utils/README_SRC.md"])
        clean = not any("three-builds-one-source" in p for p in probs)
        results.append(("A: pointer-only second file PASSES", clean))
        ok &= clean

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # ---- direction 1: DEFECTIVE tree, class B (the real "four lines" defect) ----
        _write(root, "src/main_ppgc.tex", PPGC_2)
        _write(root, "src/main.tex",
               "% main_ppgc.tex is a four-line file that sets one switch and reads this one.\n")
        probs = check_counts(root, ["src/main.tex", "src/main_ppgc.tex"], ["src/main_ppgc.tex"])
        hit = any("claims" in p and "4 lines" in p for p in probs)
        results.append(("B: wrong self-describing count is DETECTED", hit))
        ok &= hit

        # ---- direction 2: FIXED tree, class B ----
        _write(root, "src/main.tex",
               "% main_ppgc.tex holds two lines of content: one switch and an \\input.\n")
        probs = check_counts(root, ["src/main.tex", "src/main_ppgc.tex"], ["src/main_ppgc.tex"])
        clean = not probs
        results.append(("B: correct count PASSES", clean))
        ok &= clean

        # ---- REPORTED SPEECH, both directions ----
        # A finding that QUOTES a wrong count is the record of the defect and must pass; an
        # ASSERTION must still fire even when the sentence contains a verb like "reads". Both
        # cases are here because the second one broke on the run that introduced REPORTED: the
        # verb list included "read", which silenced the defective fixture below.
        _write(root, "src_utils/LATEX_UPGRADE.md",
               '`main.tex:12` says `main_ppgc.tex` is a "four-line file"; it has two content lines.\n')
        probs = check_counts(root, ["src_utils/LATEX_UPGRADE.md", "src/main_ppgc.tex"],
                             ["src/main_ppgc.tex"])
        clean = not probs
        results.append(("B: a finding QUOTING a wrong count PASSES", clean))
        ok &= clean

        _write(root, "src_utils/LATEX_UPGRADE.md",
               "% main_ppgc.tex is a four-line file that sets one switch and reads this one.\n")
        probs = check_counts(root, ["src_utils/LATEX_UPGRADE.md", "src/main_ppgc.tex"],
                             ["src/main_ppgc.tex"])
        hit = any("claims" in p and "4 lines" in p for p in probs)
        results.append(("B: an ASSERTION containing 'reads' still FIRES", hit))
        ok &= hit

        # ---- direction 1b: a file describing ITSELF wrongly, without naming itself ----
        _write(root, "src/main_ppgc.tex",
               "% This file is deliberately four lines of content.\n"
               "\\def\\APPROVALSHEET{}\n\\input{main.tex}\n")
        _write(root, "src/main.tex", "% nothing to see\n")
        probs = check_counts(root, ["src/main.tex", "src/main_ppgc.tex"], ["src/main_ppgc.tex"])
        hit = any("main_ppgc.tex:1" in p for p in probs)
        results.append(("B: a file miscounting ITSELF is DETECTED", hit))
        ok &= hit

    for label, passed in results:
        print(f"  self-test {'PASS' if passed else 'FAIL'}: {label}")
    return ok


def main(argv: list[str]) -> int:
    verbose = "--verbose" in argv
    print("comment hygiene: self-test first (a green tree means nothing from a broken checker)")
    if not selftest():
        print("  FAIL: self-tests do not pass -- this checker is broken and its verdict on the "
              "tree is NOT evidence")
        return 1
    if "--selftest" in argv:
        return 0

    in_scope = [r for r in SCOPE if (DISS / r).exists()]
    absent = [r for r in SCOPE if r not in in_scope]
    # A SHRUNK SCOPE IS A FINDING, NOT A CLEAN RUN. A chapter split once moved most of this
    # repository's prose out of every checker's glob and all of them immediately reported OK.
    if len(in_scope) < SCOPE_FLOOR:
        print(f"  FAIL: scope floor breached -- {len(in_scope)} file(s) examined, floor is "
              f"{SCOPE_FLOOR}. Missing: {', '.join(absent) or 'none declared absent'}. A gate over "
              f"a shrunken sample reports clean for the wrong reason; restore the files or lower "
              f"SCOPE_FLOOR deliberately with a reason.")
        return 1
    problems = check_stories(DISS, in_scope, verbose)
    problems += check_counts(DISS, in_scope, COUNTED_FILES, verbose)

    print(f"  scope: {len(in_scope)} files examined"
          + (f"; {len(absent)} declared but absent and therefore NOT examined: "
             f"{', '.join(absent)}" if absent else "; 0 skipped"))
    if problems:
        print(f"  {len(problems)} finding(s):")
        for p in problems:
            print(f"    {p}")
        return 1
    print(f"  OK: {len(STORIES)} canonical stories each told once; "
          f"self-describing counts agree with the files they describe")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
