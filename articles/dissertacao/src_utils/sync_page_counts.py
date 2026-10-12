#!/usr/bin/env python3
"""Sync the recorded page counts in the governance files to the measured build.

WHY THIS EXISTS
---------------
The page counts in CLAUDE.md, PLAN.md, PENDENCIAS.md and codex_reviewer.md are PRESENT-TENSE claims
about what is on disk, and they have now drifted three times (87/83 -> 89/84 -> 103/98 -> 104/99).
Each drift was found by review, never by the author of the edit, because the cell that changes the
document is never the cell that updates the record.

The page-drift note in codex_reviewer.md is load-bearing: it tells a reader that every file:line in
that review has moved, and by roughly how much. A wrong count there silently misleads.

Run after any build that changes the page count:
    python3 src_utils/sync_page_counts.py            # report only
    python3 src_utils/sync_page_counts.py --write    # apply

Exits 1 when a recorded count disagrees with the build, so it can gate a commit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (file, regex with ONE capture group for the number, which build the number refers to)
#
# THE THIRD FIELD IS THE INTERNAL KEY, NOT DOC TEXT. It was "final" until 2026-07-29 and is now
# "academico", matching measured() below and the renamed build (LATEX_UPGRADE.md §4 A-1). The
# REGEXES are deliberately NOT renamed with it: they match what the author-facing documents
# actually say, and those documents still say `make final` / `main_final.pdf`. Renaming a
# pattern to match a document that has not changed is how this tool went silent on 2026-07-28 --
# it printed nothing and exited 0 while four page-count claims went unchecked. If a document is
# later reworded to `academico`, change its pattern HERE in the same commit and confirm this
# script still reports it (an UNMATCHED line is the loud failure; there is no silent skip).
CLAIMS = [
    # REPOINTED 2026-08-20. CLAUDE.md was rewritten in the reorganisation that collapsed the three
    # source trees into one, and its build facts moved from a prose paragraph into a table (one row
    # per target, page count in its own cell). The three old patterns went UNMATCHED -- three guards
    # announcing that the claim they protected was no longer checked -- so they follow the table now.
    # Verified in both directions: each matches the current CLAUDE.md and none matches the pre-reorg
    # one. NOTE the middle target was `main_final.pdf` until it was renamed `main_academico.pdf`
    # (2026-07-29); the pattern below tracks the current name.
    ("CLAUDE.md",                r"`build/main\.pdf`[^|]*\|\s*\*\*(\d+)\*\*", "defense"),
    ("CLAUDE.md",                r"`build/main_academico\.pdf`[^|]*\|\s*\*\*(\d+)\*\*", "academico"),
    ("CLAUDE.md",                r"`build/main_ppgc\.pdf`[^|]*\|\s*\*\*(\d+)\*\*", "ppgc"),

    # RETIRED 2026-08-20, and retired rather than repointed, for the reason this file already states
    # for the PENDENCIAS rows below: PLAN.md moved to archive/ in the same reorganisation, and an
    # archived record is a historical snapshot that must NOT be rewritten when the build moves --
    # guarding it would make this tool edit history. PLAN.md's counts (118/113) describe the v1 tree
    # that was deleted; they are correct as history and wrong as a current claim, which is precisely
    # why the file now lives under archive/ with a "ainda vale? nao" row against it.
    #   ("PLAN.md", r"defense \*\*(\d+) pp\*\*", "defense"),
    #   ("PLAN.md", r"final AcademicoPG \*\*(\d+) pp\*\*", "academico"),

    # PENDENCIAS was rewritten as a three-part tracker on 2026-07-28 and its build state became a
    # table row per target, not a "X/Y" pair in prose. The old patterns SKIPped silently after that,
    # which is the same failure this whole tool exists to prevent: a page-count claim nobody checks.
    #
    # RETIRED 2026-07-29 (trackers track), and retired rather than repointed on purpose. That §1
    # table lived inside the "Fechado nesta rodada" section, which moved to
    # _history/_archive/PENDENCIAS_RESOLVIDOS.md when the tracker was split -- so these three patterns went
    # UNMATCHED, i.e. three guards reporting that the claim they protected was no longer checked.
    # (Confirmed in both directions: all three match ba5dd5b3^:PENDENCIAS.md and none matches the
    # split file.) They are NOT repointed at the archive, because an archived record is a historical
    # snapshot and must NOT be rewritten when the build moves -- guarding it would make this tool
    # edit history. And they are NOT repointed at the live tracker's new build-state section,
    # because that section deliberately carries NO per-target page number today: the tree was being
    # rebuilt by a concurrent track and the honest claim was "not confirmed, remeasure when it
    # settles". A guard over a number that is not asserted has nothing to check.
    #
    # WHEN THE TRACKER CARRIES PAGE COUNTS AGAIN, restore three rows here in the same commit that
    # adds them, or this comment becomes the next silent gap.
    #
    # RESTORED 2026-07-30, in the commit that reintroduced the numbers. PENDENCIAS §4 item 5 is the
    # author's own "run these before you trust anything" list, and it had drifted twice over: it told
    # him to run `make final` (renamed to `academico` on 2026-07-29) and promised 108/105/109 against
    # a tree building 101/98/102. I corrected it by hand -- and MY CORRECTION WAS STALE WITHIN THE
    # HOUR, because a concurrent track added a page to §2.3 between my measurement and the next
    # build. That is the argument for the guard rather than for more careful typing: this is the one
    # page-count claim the author is most likely to act on, and it was the only one no tool watched.
    # The pattern matches the three-target form "**102/99/103** paginas" as a unit, so all three
    # targets are checked, and a fourth number in that slot cannot pass silently.
    # REMOVED 2026-07-30. These three watched the "**102/99/103** paginas" claim in PENDENCIAS §4, and
    # §4 was retired the same day (VERIFY_LIST closed, so the audit-priority list it pointed at had no
    # reason to exist). The claim they guarded is GONE, not stale: there is no page-count assertion left
    # in PENDENCIAS.md to keep in sync. Verified before removing, and stated precisely because a loose
    # count would be wrong: `grep -c "\*\*[0-9]+/[0-9]+/[0-9]+\*\* paginas"` returns 0, i.e. no claim in
    # the three-target form these rows parsed. The bare word "paginas" still appears 11 times, all of
    # them prose about a past measurement ("medido contra o build de 101 paginas") or a page RANGE in a
    # citation, none of them a present-tense assertion of this tree's page count. That distinction is
    # the whole point of the rows: they guard claims a build can falsify, not mentions of the word.
    # Left as a comment rather than deleted so the next agent does not re-add a row for a claim the file
    # no longer makes. The gate's UNMATCHED branch caught this immediately, which is what it is for: a
    # pattern that stops matching is a claim that has become unchecked, and that is a defect either way.
    ("src_utils/codex_reviewer.md", r"The builds on disk are \*\*(\d+)/\d+ pages\*\*", "defense"),
    ("src_utils/codex_reviewer.md", r"The builds on disk are \*\*\d+/(\d+) pages\*\*", "academico"),
]


def measured() -> dict[str, int]:
    out = {}
    skews: list[str] = []
    # ppgc added 2026-07-28: three targets now, and a claim about a target this tool does not
    # measure would raise a KeyError rather than being silently skipped, which is the right failure.
    # main_final -> main_academico on 2026-07-29 (LATEX_UPGRADE.md §4 A-1). The stem is
    # hardcoded here and in five other tools; a missed one does not error, it silently reports
    # the page count of a log that is no longer written.
    for stem, key in (("main", "defense"), ("main_academico", "academico"), ("main_ppgc", "ppgc")):
        log = ROOT / "src" / "build" / f"{stem}.log"
        pdf = ROOT / "src" / "build" / f"{stem}.pdf"
        if not log.exists():
            sys.exit(f"no {log.relative_to(ROOT)} -- build first, this script reads the real log")
        # THE LOG IS NOT THE DOCUMENT. Until 2026-07-29 this function read the page count out of
        # the .log and never looked at the .pdf, so it certified page counts for documents that
        # were NOT ON DISK. Reproduced: with all three PDFs deleted and the three logs left in
        # place it printed "measured from the build logs: defense 104 pp, ..." followed by "all
        # recorded page counts agree with the build" and exited 0 -- as `make check`'s page gate.
        # That is a good result about an artifact that does not exist, which is the exact defect
        # class of science/AGENT_HANDOFF.md §2.3b read from the other side.
        if not pdf.exists():
            sys.exit(f"no {pdf.relative_to(ROOT)} -- the log records a page count for a PDF that "
                     f"is not on disk; rebuild rather than trusting the log")
        # And the two must come from the SAME run. latexbuild.sh and fastbuild.sh publish the
        # .pdf and the .log in one loop, so the skew is milliseconds in practice (measured
        # +/-0.0 s on all four stems on 2026-07-29). A large skew means the log describes a
        # different build than the PDF beside it, which is the WRONG-ARTIFACT case. The measured
        # skew is printed on every run rather than only on failure (§4b V12: a number a human has
        # to interpret every run will not be interpreted).
        skew = log.stat().st_mtime - pdf.stat().st_mtime
        if abs(skew) > 300:
            sys.exit(f"{stem}: the .log and the .pdf are {skew:+.0f} s apart -- they are not from "
                     f"the same build, so the page count does not describe this PDF")
        skews.append(f"{stem} {skew:+.0f}s")
        hits = re.findall(r"Output written on \S+ \((\d+) pages", log.read_text(errors="replace"))
        if not hits:
            sys.exit(f"{log.relative_to(ROOT)} has no page count -- the build did not finish")
        out[key] = int(hits[-1])
    print("pdf/log skew, same-run check: " + ", ".join(skews))
    return out


def main(write: bool) -> int:
    truth = measured()
    print("measured from the build logs: " +
          ", ".join(f"{k} {v} pp" for k, v in truth.items()))
    stale = 0
    for rel, pattern, which in CLAIMS:
        path = ROOT / rel
        if not path.exists():
            print(f"  SKIP  {rel} (missing)")
            continue
        text = path.read_text()
        m = re.search(pattern, text)
        if not m:
            # NOT a silent skip. A pattern that stops matching is a page-count claim that
            # nobody is checking any more -- the exact thing this tool exists to prevent.
            # PENDENCIAS.md drifted this way on 2026-07-28 when it was restructured.
            print(f"  UNMATCHED {rel}: pattern no longer matches -- {pattern}")
            print(f"            the claim it guarded is now unchecked. Fix the pattern or "
                  f"drop the row from CLAIMS.")
            stale += 1
            continue
        recorded = int(m.group(1))
        if recorded == truth[which]:
            continue
        stale += 1
        print(f"  STALE {rel}: records {recorded} for the {which} build, measured {truth[which]}")
        if write:
            lo, hi = m.span(1)
            path.write_text(text[:lo] + str(truth[which]) + text[hi:])
            print(f"        -> updated")
    if not stale:
        print("all recorded page counts agree with the build")
        return 0
    if write:
        print(f"{stale} claim(s) updated")
        return 0
    print(f"{stale} claim(s) stale; re-run with --write to fix")
    return 1


if __name__ == "__main__":
    sys.exit(main("--write" in sys.argv))
