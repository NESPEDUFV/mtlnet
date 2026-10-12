#!/usr/bin/env python3
"""verify_format.py -- prove that an accelerated or parallel build produced THE SAME DOCUMENT.

WHY THIS EXISTS. `make fast` loads a precompiled preamble and `make all3` builds three targets
concurrently. Both are pure speed changes, so both are only worth having if the PDF is
identical to the one the plain serial path produces. "The build succeeded and the page count
matches" is not that proof: page counts collide easily, and a format dump's whole failure mode
is producing a plausible PDF from a stale preamble (science/AGENT_HANDOFF.md §2.3b -- a PDF
existing is not evidence the source is correct).

WHAT IT COMPARES, AND WHY NOT BYTES. Two pdflatex runs of the same source never produce
identical bytes: /CreationDate, /ModDate and /ID change every run. So the comparison is on the
extracted TEXT LAYER of the whole document, with DIGITS MASKED.

  - Whole document, not page by page. A page-by-page diff drowns in false positives the moment
    one line reflows; that was learned the expensive way in a previous round.
  - Digits masked to '#'. A page number that shifts is not a difference in the document, and
    neither is a date in the front matter.
  - Whitespace collapsed. pypdfium2's extractor is sensitive to where a line happens to break.

WHAT THAT LEAVES THE INSTRUMENT BLIND TO -- stated because a claim built on an
uninterrogated instrument is this repository's second-largest defect class
(AGENT_GUARDRAILS §4b V3):

  1. Anything NUMERIC. Masking digits means a build that got every number wrong would pass.
     Mitigated by --numbers, which compares the digit sequences separately and is reported as
     its own line. Run both; the text check is the primary one and the number check is the one
     that catches a wrong table.
  2. Anything NOT IN THE TEXT LAYER: figure raster content, rule positions, font choices,
     colours, kerning, margins. A format dump that lost a package would almost always also
     change the text layer (missing captions, changed hyphenation), but it need not.
     `--pages` additionally compares the page count and each page's media box.
  3. PDF metadata and bookmarks. --outline compares the bookmark tree, which is where a
     hyperref difference would show up first.

USAGE
    make verify-equiv                    the whole proof: plain build -> reference -> fast
                                         build -> compare (about 8 minutes, all three targets)
    make check-equiv                     compare whatever is on disk against the reference
    python3 src_utils/verify_format.py --reference     store build/*.pdf as the reference
    python3 src_utils/verify_format.py --compare       compare build/*.pdf to the reference
    python3 src_utils/verify_format.py A.pdf B.pdf --all      any two PDFs, every surface
Exit 0 when every requested comparison matches, 1 otherwise. On a mismatch it prints the first
differing region with context, so the failure is diagnosable rather than merely reported.

The reference lives in build/verify-serial/ and carries a REFERENCE.txt naming the commit and
the command that produced it, because a reference PDF of unknown provenance proves nothing.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys

# main_final/final -> main_academico/academico on 2026-07-29 (LATEX_UPGRADE.md §4 A-1). A stale
# stem here does not error: the target is reported as SKIPped for want of a PDF, and the
# skip line makes it visible rather than passing silently.
STEMS = [("main", "defense"), ("main_academico", "academico"), ("main_ppgc", "ppgc")]
REFDIR = "build/verify-serial"


def load(path: str):
    import pypdfium2 as pdfium
    return pdfium.PdfDocument(path)


def text_of(doc) -> str:
    return "\n".join(doc[i].get_textpage().get_text_range() for i in range(len(doc)))


def fingerprint(raw: str) -> str:
    """Digits -> '#', whitespace collapsed. The primary comparison surface."""
    t = re.sub(r"\d", "#", raw)
    return re.sub(r"\s+", " ", t).strip()


def digits_of(raw: str) -> list[str]:
    """Every digit run, in order. The check that masking would otherwise hide."""
    return re.findall(r"\d+", raw)


def first_diff(a: str, b: str, width: int = 110) -> str:
    """Locate and print the first divergence.

    NOT difflib on the whole string. These fingerprints are ~275,000 characters, and
    SequenceMatcher(autojunk=False) over two of them ran for about ELEVEN MINUTES on the first
    real mismatch -- long enough that the run looked hung rather than informative, which is its
    own kind of failure in a gate. A common-prefix scan finds the same first divergence in
    milliseconds, and printing a window around it is all the diagnosis this needs.
    """
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    if i == n and len(a) == len(b):
        return "      (no differing region found, which contradicts the equality test)"
    ctx = 55
    lo = max(0, i - ctx)
    return (f"      first divergence at character {i} of {len(a)}/{len(b)}\n"
            f"      A: ...{a[lo:i + ctx][:width]}...\n"
            f"      B: ...{b[lo:i + ctx][:width]}...")


def same_file(a_path: str, b_path: str) -> str | None:
    """Detect a comparison of a file with itself. Returns a reason, or None if independent.

    THIS CHECK IS THE DIFFERENCE BETWEEN A PROOF AND A TAUTOLOGY, and it is here because the
    first run of this comparator reported "text IDENTICAL, digit sequence IDENTICAL, all media
    boxes equal, bookmark tree IDENTICAL" for all three targets while the accelerated build had
    REFUSED TO RUN. The candidate PDFs were still the serial ones, so the comparator matched
    each reference against an unchanged copy of itself, and a green result carried no
    information at all. That is the "gate that has never fired" bias in AGENT_GUARDRAILS §7,
    reached from the §2.2 direction: identical outputs looked exactly like a converged result.

    Two pdflatex runs of the same source NEVER produce identical bytes -- /CreationDate,
    /ModDate and the file /ID trailer all change per run. So byte-identity here does not mean
    "equivalent", it means "this is the same file", and it is reported as a FAILURE of the
    comparison rather than as its strongest possible pass.
    """
    if os.path.samefile(a_path, b_path):
        return "the two paths are the same file"
    with open(a_path, "rb") as fa, open(b_path, "rb") as fb:
        if fa.read() == fb.read():
            return ("byte-identical, which two pdflatex runs never are (/CreationDate and the "
                    "/ID trailer differ every run), so this is a copy, not an independent build")
    return None


def compare(a_path: str, b_path: str, label: str, want: set) -> tuple[bool, list[str]]:
    lines = []
    ok = True
    if not os.path.exists(a_path) or not os.path.exists(b_path):
        return False, [f"{label}: MISSING ({a_path if not os.path.exists(a_path) else b_path})"]
    why = same_file(a_path, b_path)
    if why:
        return False, [f"{label}: NOT AN INDEPENDENT BUILD -- {why}.",
                       f"      A comparison of a file with itself proves nothing. Build the "
                       f"candidate, then compare.",
                       f"      reference {a_path} (mtime {int(os.path.getmtime(a_path))})",
                       f"      candidate {b_path} (mtime {int(os.path.getmtime(b_path))})"]
    da, db = load(a_path), load(b_path)
    ra, rb = text_of(da), text_of(db)

    if "text" in want:
        fa, fb = fingerprint(ra), fingerprint(rb)
        if fa == fb:
            lines.append(f"{label}: text IDENTICAL (digits masked, {len(fa)} chars compared)")
        else:
            ok = False
            lines.append(f"{label}: text DIFFERS ({len(fa)} vs {len(fb)} chars)")
            lines.append(first_diff(fa, fb))

    if "numbers" in want:
        na, nb = digits_of(ra), digits_of(rb)
        if na == nb:
            lines.append(f"{label}: digit sequence IDENTICAL ({len(na)} runs)")
        else:
            # Page numbers legitimately differ ONLY if the page count differs; when the page
            # counts match, every digit should too, so a mismatch here is a real finding.
            ok = False
            extra = [x for x in nb if x not in na][:6]
            lines.append(f"{label}: digit sequence DIFFERS ({len(na)} vs {len(nb)} runs; "
                         f"first unmatched in B: {extra})")

    if "pages" in want:
        if len(da) != len(db):
            ok = False
            lines.append(f"{label}: page COUNT differs ({len(da)} vs {len(db)})")
        else:
            boxes = [(round(da[i].get_width(), 2), round(da[i].get_height(), 2)) !=
                     (round(db[i].get_width(), 2), round(db[i].get_height(), 2))
                     for i in range(len(da))]
            n = sum(boxes)
            if n:
                ok = False
                lines.append(f"{label}: {n} page(s) differ in media box; "
                             f"first at page {boxes.index(True) + 1}")
            else:
                lines.append(f"{label}: {len(da)} pages, all media boxes equal")

    if "outline" in want:
        # An UNREADABLE outline must NOT compare equal to another unreadable outline. Two
        # sentinels match trivially, and the old code then printed "bookmark tree IDENTICAL
        # (1 entries)" -- a pass carrying no information, which is the same tautology class as
        # same_file() above. An empty outline gets the same treatment: nothing was compared, so
        # nothing is proven, and it is reported as UNVERIFIED rather than as a match.
        def outline(doc):
            try:
                return [(b.get_title(), b.get_count()) for b in doc.get_toc()], None
            except Exception as exc:                  # noqa: BLE001 - reported, never hidden
                return None, exc.__class__.__name__
        oa, ea = outline(da)
        ob, eb = outline(db)
        if ea or eb:
            ok = False
            lines.append(f"{label}: bookmark tree UNVERIFIED -- unreadable "
                         f"(reference: {ea or 'ok'}, candidate: {eb or 'ok'}). "
                         f"Two unreadable outlines are not a match.")
        elif not oa and not ob:
            ok = False
            lines.append(f"{label}: bookmark tree UNVERIFIED -- both PDFs report an EMPTY "
                         f"outline, so this surface compared nothing.")
        elif oa == ob:
            lines.append(f"{label}: bookmark tree IDENTICAL ({len(oa)} entries)")
        else:
            ok = False
            lines.append(f"{label}: bookmark tree DIFFERS ({len(oa)} vs {len(ob)} entries)")
    return ok, lines


def make_reference(src: str, note: str) -> int:
    """Copy the PDFs now in build/ into build/verify-serial/, with their provenance."""
    ref = os.path.join(src, REFDIR)
    os.makedirs(ref, exist_ok=True)
    stored = []
    for stem, _label in STEMS:
        pdf = os.path.join(src, "build", f"{stem}.pdf")
        if not os.path.exists(pdf):
            print(f"reference: SKIP {stem}.pdf (not built)")
            continue
        shutil.copy2(pdf, os.path.join(ref, f"{stem}.pdf"))
        log = os.path.join(src, "build", f"{stem}.log")
        pages = "?"
        if os.path.exists(log):
            hits = re.findall(r"Output written on \S+ \((\d+) pages",
                              open(log, encoding="utf8", errors="replace").read())
            pages = hits[-1] if hits else "?"
        stored.append(f"{stem}.pdf  {pages} pp")
    try:
        commit = subprocess.run(["git", "-C", src, "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception:                                  # noqa: BLE001
        commit = "unknown"
    with open(os.path.join(ref, "REFERENCE.txt"), "w", encoding="utf8") as fh:
        fh.write(f"produced by: {note}\ncommit: {commit or 'unknown'}\n")
        fh.write("\n".join(stored) + "\n")
    print(f"reference: stored {len(stored)} of {len(STEMS)} PDFs in {REFDIR} "
          f"at commit {commit or 'unknown'} ({note})")
    return 0 if stored else 1


def selftest() -> int:
    """Both directions: the fingerprint must ignore page shifts and CATCH a prose change."""
    fails = []
    base = "Chapter 2 Fundamentals\npage 17 of 108\nthe joint model outperforms"
    shifted = "Chapter 3 Fundamentals\npage 21 of 105\nthe joint model outperforms"
    reflowed = "Chapter 2 Fundamentals page 17 of 108\nthe joint  model outperforms"
    changed = "Chapter 2 Fundamentals\npage 17 of 108\nthe joint model matches"
    if fingerprint(base) != fingerprint(shifted):
        fails.append("fingerprint flagged a pure page-number shift (false positive)")
    if fingerprint(base) != fingerprint(reflowed):
        fails.append("fingerprint flagged a whitespace reflow (false positive)")
    if fingerprint(base) == fingerprint(changed):
        fails.append("fingerprint MISSED a changed word (false negative -- the check is useless)")
    if digits_of(base) == digits_of(shifted):
        fails.append("digit check missed a changed number")
    if not first_diff(fingerprint(base), fingerprint(changed)).strip():
        fails.append("first_diff produced no diagnostic for a real difference")

    # The self-comparison detector, both directions. Without this the comparator reports a
    # perfect match for a build that never ran -- which it did, once, before this test existed.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p1 = os.path.join(td, "a.pdf")
        p2 = os.path.join(td, "b.pdf")
        p3 = os.path.join(td, "c.pdf")
        open(p1, "wb").write(b"%PDF-1.5 same bytes")
        shutil.copy2(p1, p2)                      # a copy: must be REJECTED
        open(p3, "wb").write(b"%PDF-1.5 other bytes")
        if same_file(p1, p1) is None:
            fails.append("same_file accepted a path compared with itself")
        if same_file(p1, p2) is None:
            fails.append("same_file accepted a byte-identical COPY as an independent build")
        if same_file(p1, p3) is not None:
            fails.append("same_file rejected two genuinely different files (false positive)")
        ok, lines = compare(p1, p2, "fixture", {"text"})
        if ok or not any("NOT AN INDEPENDENT BUILD" in l for l in lines):
            fails.append("compare() passed a file compared against its own copy")

    # The outline check must not call two UNREADABLE or two EMPTY outlines a match. Exercised on
    # stand-ins for the two document objects, since building a real PDF here would be absurd.
    class _Doc:
        def __init__(self, toc): self._toc = toc
        def get_toc(self):
            if self._toc is None:
                raise RuntimeError("unreadable")
            return self._toc
    def _outline_verdict(a, b):
        def outline(doc):
            try:
                return [(x, 0) for x in doc.get_toc()], None
            except Exception as exc:                  # noqa: BLE001
                return None, exc.__class__.__name__
        oa, ea = outline(a); ob, eb = outline(b)
        if ea or eb: return "UNVERIFIED"
        if not oa and not ob: return "UNVERIFIED"
        return "IDENTICAL" if oa == ob else "DIFFERS"
    if _outline_verdict(_Doc(None), _Doc(None)) != "UNVERIFIED":
        fails.append("two UNREADABLE outlines compared as a match")
    if _outline_verdict(_Doc([]), _Doc([])) != "UNVERIFIED":
        fails.append("two EMPTY outlines compared as a match")
    if _outline_verdict(_Doc(["a", "b"]), _Doc(["a", "b"])) != "IDENTICAL":
        fails.append("two equal readable outlines did not compare as identical")
    if _outline_verdict(_Doc(["a"]), _Doc(["b"])) != "DIFFERS":
        fails.append("two different readable outlines did not compare as differing")

    total = 13
    for f in fails:
        print("FAIL: " + f)
    print(f"verify_format selftest: {total - len(fails)}/{total} checks pass")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", nargs="*")
    ap.add_argument("--compare", action="store_true",
                    help="compare build/*.pdf against the stored reference")
    ap.add_argument("--reference", action="store_true",
                    help="store the current build/*.pdf as the reference")
    ap.add_argument("--note", default="unrecorded command",
                    help="what produced the reference (recorded in REFERENCE.txt)")
    ap.add_argument("--src", default=None)
    ap.add_argument("--numbers", action="store_true")
    ap.add_argument("--pages", action="store_true")
    ap.add_argument("--outline", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    want = {"text"}
    if a.numbers or a.all:
        want.add("numbers")
    if a.pages or a.all:
        want.add("pages")
    if a.outline or a.all:
        want.add("outline")

    # The self-test runs BEFORE any report, per the both-directions rule: a green comparison
    # from a broken comparator is worth nothing.
    if selftest() != 0:
        print("verify_format: the comparator's own self-test failed; its result is not evidence")
        return 1

    src = os.path.abspath(a.src or os.getcwd())
    if a.reference:
        return make_reference(src, a.note)

    rc = 0
    if len(a.pdfs) == 2:
        ok, lines = compare(a.pdfs[0], a.pdfs[1], "pair", want)
        print("\n".join(lines))
        rc = 0 if ok else 1
    elif a.compare:
        ref = os.path.join(src, REFDIR)
        prov = os.path.join(ref, "REFERENCE.txt")
        if os.path.exists(prov):
            print("reference provenance: " +
                  " | ".join(open(prov, encoding="utf8").read().split("\n")[:2]))
        seen = 0
        for stem, label in STEMS:
            pa = os.path.join(ref, f"{stem}.pdf")
            pb = os.path.join(src, "build", f"{stem}.pdf")
            if not (os.path.exists(pa) and os.path.exists(pb)):
                missing = REFDIR + f"/{stem}.pdf" if not os.path.exists(pa) else f"build/{stem}.pdf"
                print(f"{label}: SKIP (missing {missing})")
                continue
            seen += 1
            ok, lines = compare(pa, pb, label, want)
            print("\n".join(lines))
            if not ok:
                rc = 1
        # A skip is never silent, and "nothing to compare" must not read as success.
        print(f"verify_format: {seen} of {len(STEMS)} targets compared, "
              f"{len(STEMS) - seen} skipped for want of a PDF")
        if seen == 0:
            print("verify_format: nothing was compared, so nothing is proven")
            rc = 1
    else:
        ap.print_help()
        return 2
    return rc


if __name__ == "__main__":
    sys.exit(main())
