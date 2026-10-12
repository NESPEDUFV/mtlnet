# REPOINTED 2026-08-02, when the author's revised tree (src_clean) was merged into src.
# All six of these went ABSENT after the merge. Each was checked in the RENDER before being
# repointed, and in every case the advisor's request is still satisfied -- the author expressed
# it in his own words rather than the exact string this file pinned. Examples: FAB-12 asked for
# the generic plural, and his revision reads "check-in records associating a user, a point of
# interest (POI), and a time"; FAB-16 asked that the next-place task be marked as out of scope,
# and his reads "predicts the exact next place, so none of them is a direct baseline for the
# targets studied in this dissertation". The OLD-string assertions are kept: they still prove the
# superseded wording has not come back.
#!/usr/bin/env python3
"""Wave A, verified in the RENDERED PDF -- both directions, every item, as a runnable check.

WHY THIS FILE EXISTS. Three times in round 9 a summary sentence claimed a measurement that had not
been taken (ten stale anchors that were nine; eight applied items that were seven; seven
both-directions render checks that were three). The first two were caught by a reviewer, the third
was caught in the paragraph written to close out the second. Prose that says "verified in both
directions" is a claim; this file is the evidence, and it re-runs in two seconds.

WHAT IT ASSERTS. For each Wave A edit: the NEW wording is present in build/main.pdf's text layer AND
the SUPERSEDED wording is absent. Sixteen assertions over seven items -- FAB-11 is checked in both
languages, because the Resumo and the Abstract must move together or they contradict.

FAB-01 IS DELIBERATELY NOT HERE. It was already satisfied before this round: nothing was edited, so
there is no superseded wording that could be absent and the both-directions form does not apply to
it. Its presence-only check is the last row, labelled as such. Counting it among the applied edits is
the exact defect this file guards.

Usage:  python3 35_wave_a_render_check.py [path/to/main.pdf]      rc 0 = every assertion holds
"""
import re
import sys
import unicodedata
from pathlib import Path

import pypdfium2 as pdfium

DEFAULT_PDF = Path(__file__).resolve().parent.parent.parent.parent / "src" / "build" / "main.pdf"

# (item, direction, needle, want_present, ascii_fold)
CHECKS = [
    ("FAB-11", "new", "multitask learning, point of interest, next-category prediction", True, False),
    ("FAB-11", "old EN", "multi-task learning point of interest next-category prediction", False, False),
    ("FAB-11", "new PT", "aprendizado multitarefa, ponto de interesse, previsao", True, True),
    ("FAB-11", "old PT", "aprendizado multitarefa ponto de interesse previsao", False, True),
    ("FAB-12", "new", "check-in records associating a user, a point of interest", True, False),
    ("FAB-12", "old", "records that a given user visited a given place", False, False),
    ("FAB-13", "new", "next category and next region are predicted", True, False),
    ("FAB-13", "old", "The two properties above are the two prediction tasks of this dissertation", False, False),
    ("FAB-16", "new", "predicts the exact next place, so none of them is a direct baseline", True, False),
    ("FAB-16", "old", "different problem; this dissertation does not address it", False, False),
    ("FAB-19", "new", "Research question", True, False),
    ("FAB-19", "old", "Research question and the arc of this dissertation", False, False),
    ("FAB-23", "new", "Chapter 2 formally defines the three tasks", True, False),
    ("FAB-23", "old", "Chapter 2, Fundamentals,", False, False),
    ("FAB-24", "new", "Chapter 6 answers the research question across the three studies", True, False),
    ("FAB-24", "old", "Chapter 6, Conclusion,", False, False),
]

# Presence-only, and separated on purpose: no edit was made, so there is no absent half to assert.
CONFIRM_ONLY = [
    ("FAB-01", "EN abstract advisor line", "Advisor: Fabr"),
    ("FAB-01", "folha de rosto advisor line", "Orientador: Fabr"),
]


def text_of(pdf: Path) -> tuple[str, str]:
    doc = pdfium.PdfDocument(str(pdf))
    raw = " ".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))
    flat = re.sub(r"\s+", " ", raw)
    folded = unicodedata.normalize("NFKD", flat).encode("ascii", "ignore").decode()
    return flat, folded


def main() -> int:
    pdf = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PDF
    if not pdf.exists():
        print(f"FAIL: {pdf} does not exist -- build it with `make defense` first.")
        return 2
    flat, folded = text_of(pdf)

    # Self-test: a needle that must NOT be found, and one that must, so a broken extractor
    # (empty text layer) cannot make every absence assertion pass vacuously.
    assert "Fabr" in flat, "self-test: the text layer is empty or unreadable; absences would be vacuous"
    assert "zzzz-not-in-any-dissertation" not in flat, "self-test: the matcher returns true for anything"

    failures = []
    for item, direction, needle, want, fold in CHECKS:
        hay = folded if fold else flat
        got = needle in hay
        if got != want:
            failures.append((item, direction, needle, want, got))
        print(f"  {'OK  ' if got == want else 'FAIL':4s} {item} {direction:7s} "
              f"{'found ' if got else 'absent'} (wanted {'present' if want else 'absent'})")

    for item, what, needle in CONFIRM_ONLY:
        got = needle in flat
        if not got:
            failures.append((item, what, needle, True, got))
        print(f"  {'OK  ' if got else 'FAIL':4s} {item} {what:26s} "
              f"{'found' if got else 'absent'} (presence only: nothing was edited)")

    n_items = len({c[0] for c in CHECKS})
    print(f"\n  {len(CHECKS)} two-directional assertions over {n_items} edited items, "
          f"plus {len(CONFIRM_ONLY)} presence checks on 1 confirm-only item.")
    if failures:
        print(f"  {len(failures)} FAILED.")
        return 1
    print("  all hold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
