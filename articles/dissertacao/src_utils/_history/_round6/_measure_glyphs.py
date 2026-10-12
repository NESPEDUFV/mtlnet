#!/usr/bin/env python3
"""_measure_glyphs.py -- measure ON-PAGE glyph size from geometry, not from the nominal
font size declared inside an embedded XObject.

WHY. FPDFText_GetFontSize reports the size DECLARED inside the embedded form XObject and is
blind to the \\includegraphics scale that places it. src_utils/_history/_round6/12_figures.md records
this trap: after the two Chapter 5 diagrams were rescaled, that API still returned 6.97 pt on
both pages, so an audit that trusted it would have reported no improvement at all.

THE INSTRUMENT USED INSTEAD. Take the char box of a chosen lowercase reference glyph (`o`, an
x-height letter with no ascender or descender, so its box height is a clean proxy for type
size), measured on the SAME PAGE, for the body font and for the in-figure text. Calibrate:

    nominal_pt_per_box_pt = body_nominal_size / body_o_box_height
    effective_size        = figure_o_box_height * nominal_pt_per_box_pt

Usage:
  python3 _measure_glyphs.py <pdf> --pages 62 65 [--glyph o]

The body nominal size is not an option: it is always inferred as the MODAL nominal size on the
page being measured, so the calibration comes from that page's own body text and never from a
value carried over from another page.

Prints, per page: body nominal size (modal), body reference-glyph box, per-nominal-size
clusters of in-figure glyphs, and the effective on-page size of each cluster.
"""
from __future__ import annotations

import argparse
import statistics
from collections import Counter, defaultdict

import pypdfium2.raw as pdfium_c
import pypdfium2 as pdfium


def page_chars(page):
    """Yield (index, char, nominal_size, (l, b, r, t)) for every char on the page."""
    tp = page.get_textpage()
    n = pdfium_c.FPDFText_CountChars(tp.raw)
    for i in range(n):
        code = pdfium_c.FPDFText_GetUnicode(tp.raw, i)
        ch = chr(code) if code else ""
        size = pdfium_c.FPDFText_GetFontSize(tp.raw, i)
        import ctypes

        l, b, r, t = (ctypes.c_double() for _ in range(4))
        ok = pdfium_c.FPDFText_GetCharBox(tp.raw, i, l, r, b, t)
        if not ok:
            continue
        yield i, ch, float(size), (l.value, b.value, r.value, t.value)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages", type=int, nargs="+", required=True, help="1-indexed")
    ap.add_argument("--glyph", default="o")
    args = ap.parse_args()

    doc = pdfium.PdfDocument(args.pdf)
    for pno in args.pages:
        page = doc[pno - 1]
        chars = list(page_chars(page))
        if not chars:
            print(f"p.{pno}: NO TEXT LAYER")
            continue
        sizes = Counter(round(s, 2) for _, _, s, _ in chars)
        body_nominal = sizes.most_common(1)[0][0]

        # reference-glyph boxes, grouped by nominal size
        by_size = defaultdict(list)
        for _, ch, s, (l, b, r, t) in chars:
            if ch == args.glyph:
                by_size[round(s, 2)].append(t - b)

        if body_nominal not in by_size or not by_size[body_nominal]:
            print(f"p.{pno}: body nominal {body_nominal} pt but no '{args.glyph}' at that size; "
                  f"available: {sorted(by_size)}")
            continue
        body_box = statistics.median(by_size[body_nominal])
        cal = body_nominal / body_box

        print(f"p.{pno}: body nominal={body_nominal:.2f} pt  "
              f"'{args.glyph}' box={body_box:.3f} pt  "
              f"calibration={cal:.4f} nominal-pt per box-pt  "
              f"(nominal-size histogram: {dict(sizes.most_common(6))})")
        for s in sorted(by_size):
            boxes = by_size[s]
            med = statistics.median(boxes)
            eff = med * cal
            tag = "BODY" if s == body_nominal else ""
            print(f"    nominal {s:6.2f} pt  n={len(boxes):4d}  "
                  f"'{args.glyph}' box={med:6.3f} pt  -> effective {eff:6.2f} pt  "
                  f"({100 * eff / body_nominal:5.1f}% of body) {tag}")
        below9 = sum(1 for _, ch, s, _ in chars if s < 9.0 and not ch.isspace())
        print(f"    glyphs with NOMINAL size < 9 pt (excluding whitespace): {below9}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
