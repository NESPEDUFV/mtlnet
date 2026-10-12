#!/usr/bin/env python3
"""check_extra_xrefs.py -- guard the frozen cross-volume references of the supplementary volume.

WHAT THIS EXISTS FOR
--------------------
src/main_extra.tex is a SEPARATE document carrying Appendix B (errata) and Appendix D (the
label-history benchmark). Those two appendices discuss chapters of the DISSERTATION, so they
contain \\ref{ch:cbic}, \\ref{ch:mobiwac}, \\ref{tab:mobiwac:results} and so on -- 46 call
sites whose targets live in a document this one does not read. src/main_extra.tex resolves them
by declaring frozen (label -> printed number) pairs with \\dissertationlabel.

A frozen number is exactly the kind of record that drifts (science/AGENT_HANDOFF.md §2.6:
page counts drifted four times, each caught by review rather than by the edit that caused
it). Reorder the chapters and the supplementary volume keeps printing "Chapter 3" for a
chapter that is now Chapter 4, with no warning from any build: both documents compile clean,
because each is internally consistent. Only a comparison ACROSS the two can see it.

THE THREE DIRECTIONS IT CHECKS
------------------------------
1. STALE   a label declared in main_extra.tex whose frozen number differs from the number the
           main defense build actually printed for it.
2. MISSING a \\ref target used by the supplementary volume's own sources that is neither
           defined inside that volume nor declared in main_extra.tex -- i.e. it would render
           as `??`.
3. DEAD    a label declared in main_extra.tex that nothing in the volume references any more.
           This direction matters because a dead declaration is what makes the other two
           look green: it is a value nobody is checking, kept alive by a gate that only
           compared declarations against the main build.

WHERE THE TRUTH COMES FROM
--------------------------
The number the MAIN build printed, read out of its own aux tree
(src/build/main-aux/**/*.aux, the \\newlabel lines), never from this file and never from
prose. If that tree is absent the gate SKIPS with a stated reason and a nonzero-free exit,
because a missing build is not a defect in the source -- but it says so out loud rather than
passing silently (AGENT_GUARDRAILS §4b V2: a skip is never silent).

SELF-TEST (AGENT_GUARDRAILS §4b V7, and it runs BEFORE the gate reports)
-----------------------------------------------------------------------
--selftest builds three synthetic trees in a temp directory, one per direction, and asserts
this checker FAILS on each, then asserts it PASSES on a correct tree. A gate that has never
fired carries no information; four of this repository's checkers were wrong at least once by
being tuned only on the case in front of them.

Usage:
    python3 src_utils/check_extra_xrefs.py            # gate (runs the self-test first)
    python3 src_utils/check_extra_xrefs.py --selftest  # only the self-test
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

UTILS = Path(__file__).resolve().parent
SRCROOT = UTILS.parent / "src"
# REPOINTED 2026-08-20. The supplementary volume moved out of the shipping tree to
# wrapup/material_extra at 264c7996 (it is defense support, not deposited text). Before this
# repoint the gate found no main_extra.tex and returned SKIP -- reporting green while checking
# nothing. The MAIN build aux stays under SRCROOT; only the volume source moved.
EXTRAROOT = UTILS.parent / "wrapup" / "material_extra"

# \dissertationlabel{ch:cbic}{3}
DECL = re.compile(r"^\s*\\dissertationlabel\{([^}]*)\}\{([^}]*)\}", re.M)
# \newlabel{ch:cbic}{{3}{26}{...}}  -- first braced group inside the value is the number
NEWLABEL = re.compile(r"\\newlabel\{([^}]*)\}\{\{([^}]*)\}\{")
LABEL = re.compile(r"\\label\{([^}]*)\}")
REF = re.compile(r"\\(?:ref|autoref|pageref|nameref)\{([^}]*)\}")


def strip_comments(text: str) -> str:
    """Drop whole-line LaTeX comments.

    AGENT_GUARDRAILS §4b V4: this source carries provenance comments that quote the very
    strings being searched for, so an unfiltered sweep always over-reports. Filter the FILE,
    not the grep output.
    """
    return "\n".join(l for l in text.splitlines() if not re.match(r"^\s*%", l))


def volume_sources(srcroot: Path, entry: str = "main_extra.tex") -> list[Path]:
    """Every .tex the supplementary volume pulls in, followed transitively from its entry."""
    seen: list[Path] = []
    todo = [srcroot / entry]
    pat = re.compile(r"\\(?:input|include)\{([^}]*)\}")
    while todo:
        f = todo.pop()
        if f in seen or not f.exists():
            continue
        seen.append(f)
        for m in pat.finditer(strip_comments(f.read_text(errors="replace"))):
            t = m.group(1)
            rel = t if t.endswith(".tex") else t + ".tex"
            # Same search order as the volume's Makefile (TEXINPUTS=".//:<src>//:"): the volume's
            # own tree first, then src/. FIXED 2026-10-05: after the 08-20 repoint only the first
            # was tried, so every \input{tables/...} (the errata tables live in src/tables) was
            # skipped silently, their labels went unseen, and six refs were reported MISSING while
            # any real broken ref inside those tables could no longer be seen.
            for base in (srcroot, SRCROOT):
                cand = base / rel
                if cand.exists():
                    todo.append(cand)
                    break
    return seen


def measured_numbers(auxroot: Path) -> dict[str, str]:
    """label -> printed number, read from the main build's own aux tree."""
    out: dict[str, str] = {}
    for aux in sorted(auxroot.rglob("*.aux")):
        for m in NEWLABEL.finditer(aux.read_text(errors="replace")):
            out.setdefault(m.group(1), m.group(2))
    return out


def audit(srcroot: Path, auxroot: Path) -> tuple[list[str], list[str], int, int, int]:
    """Returns (findings, notes, n_declared, n_sites, n_checked)."""
    findings: list[str] = []
    notes: list[str] = []

    entry = srcroot / "main_extra.tex"
    if not entry.exists():
        return ([], [f"SKIP: {entry} does not exist (no supplementary volume in this tree)"], 0, 0, 0)

    declared = {m.group(1): m.group(2) for m in DECL.finditer(strip_comments(entry.read_text(errors="replace")))}

    files = volume_sources(srcroot)
    own_labels: set[str] = set()
    used: dict[str, int] = {}
    for f in files:
        body = strip_comments(f.read_text(errors="replace"))
        own_labels |= set(LABEL.findall(body))
        for r in REF.findall(body):
            used[r] = used.get(r, 0) + 1

    n_sites = sum(v for k, v in used.items() if k not in own_labels)

    # ---- direction 2: MISSING (would render as ??) ----
    for r in sorted(used):
        if r not in own_labels and r not in declared:
            findings.append(
                f"MISSING: \\ref{{{r}}} is used {used[r]}x in the supplementary volume, is not "
                f"defined inside it, and is not declared in main_extra.tex -- it renders as ??"
            )

    # ---- direction 3: DEAD declaration ----
    for d in sorted(declared):
        if d not in used:
            findings.append(
                f"DEAD: main_extra.tex declares {d} but nothing in the volume references it. "
                f"Remove the declaration, or restore the reference that used it."
            )

    # ---- direction 1: STALE against the main build ----
    n_checked = 0
    if not auxroot.exists():
        notes.append(
            f"SKIP (staleness only): {auxroot} absent, so the {len(declared)} frozen numbers "
            f"were NOT compared against the main build. Run `make defense` first. "
            f"The MISSING and DEAD directions above did run."
        )
    else:
        measured = measured_numbers(auxroot)
        if not measured:
            notes.append(
                f"SKIP (staleness only): no \\newlabel found under {auxroot}; "
                f"{len(declared)} frozen numbers unverified."
            )
        else:
            unfound = []
            for lbl, frozen in sorted(declared.items()):
                if lbl not in measured:
                    unfound.append(lbl)
                    continue
                n_checked += 1
                if measured[lbl] != frozen:
                    findings.append(
                        f"STALE: {lbl} is frozen as {frozen!r} in main_extra.tex but the main "
                        f"build printed {measured[lbl]!r}"
                    )
            if unfound:
                findings.append(
                    f"NOT IN MAIN BUILD: {len(unfound)} declared label(s) absent from the main "
                    f"document's aux tree ({', '.join(unfound)}) -- the target may have been "
                    f"renamed or removed there"
                )
            notes.append(
                f"checked {n_checked} of {len(declared)} frozen numbers against "
                f"{auxroot.name} ({len(measured)} labels available there)"
            )

    return findings, notes, len(declared), n_sites, n_checked


# --------------------------------------------------------------------------------------
# SELF-TEST
# --------------------------------------------------------------------------------------
_GOOD_EXTRA = r"""
\dissertationlabel{ch:cbic}{3}
\dissertationlabel{ch:mobiwac}{5}
\include{chapters/apx_x}
"""
_GOOD_CHAP = r"""
\chapter{X}\label{apx:x}
Chapter~\ref{ch:cbic} and Chapter~\ref{ch:mobiwac}, and Table~\ref{tab:apx:x}.
\label{tab:apx:x}
"""


def _tree(root: Path, extra: str, chap: str, aux_num_cbic: str | None = "3") -> tuple[Path, Path]:
    src = root / "src"
    (src / "chapters").mkdir(parents=True, exist_ok=True)
    (src / "main_extra.tex").write_text(extra)
    (src / "chapters" / "apx_x.tex").write_text(chap)
    auxroot = src / "build" / "main-aux"
    auxroot.mkdir(parents=True, exist_ok=True)
    lines = [r"\newlabel{ch:mobiwac}{{5}{57}{A}{chapter.5}{}}"]
    if aux_num_cbic is not None:
        lines.append(r"\newlabel{ch:cbic}{{%s}{26}{B}{chapter.3}{}}" % aux_num_cbic)
    (auxroot / "main.aux").write_text("\n".join(lines))
    return src, auxroot


def selftest() -> int:
    cases = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # (a) correct tree -> must PASS
        s, a = _tree(root / "ok", _GOOD_EXTRA, _GOOD_CHAP)
        f, _, nd, ns, nc = audit(s, a)
        cases.append(("correct tree passes", len(f) == 0 and nd == 2 and nc == 2, f))

        # (b) STALE: aux says 4, declaration says 3 -> must FAIL
        s, a = _tree(root / "stale", _GOOD_EXTRA, _GOOD_CHAP, aux_num_cbic="4")
        f, _, _, _, _ = audit(s, a)
        cases.append(("stale number detected", any(x.startswith("STALE") for x in f), f))

        # (c) MISSING: the chapter references a label nobody declares -> must FAIL
        s, a = _tree(root / "missing", _GOOD_EXTRA,
                     _GOOD_CHAP + "\nAlso Chapter~\\ref{ch:courb}.\n")
        f, _, _, _, _ = audit(s, a)
        cases.append(("missing declaration detected", any(x.startswith("MISSING") for x in f), f))

        # (d) DEAD: a declaration nothing references -> must FAIL
        s, a = _tree(root / "dead", _GOOD_EXTRA + "\n\\dissertationlabel{ch:courb}{4}\n", _GOOD_CHAP)
        f, _, _, _, _ = audit(s, a)
        cases.append(("dead declaration detected", any(x.startswith("DEAD") for x in f), f))

        # (e) absent aux -> must SKIP LOUDLY, not silently pass
        s, _ = _tree(root / "noaux", _GOOD_EXTRA, _GOOD_CHAP)
        f, notes, _, _, nc = audit(s, s / "build" / "nonexistent-aux")
        cases.append(("absent aux skips loudly", nc == 0 and any("SKIP" in n for n in notes), notes))

    bad = [(n, d) for n, ok, d in cases if not ok]
    for name, ok, _ in cases:
        print(f"  selftest {'PASS' if ok else 'FAIL'}: {name}")
    if bad:
        for name, detail in bad:
            print(f"    -> {name}: {detail}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    only = "--selftest" in sys.argv
    rc = selftest()
    if rc:
        print("check_extra_xrefs: SELF-TEST FAILED -- the gate is not trustworthy, not reporting",
              file=sys.stderr)
        return rc
    if only:
        return 0

    findings, notes, n_decl, n_sites, n_checked = audit(EXTRAROOT, SRCROOT / "build" / "main-aux")
    for n in notes:
        print(f"  {n}")
    if findings:
        print(f"check_extra_xrefs: {len(findings)} finding(s)", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"check_extra_xrefs: OK -- {n_decl} frozen cross-volume label(s) covering "
          f"{n_sites} reference site(s); {n_checked} verified against the main build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
