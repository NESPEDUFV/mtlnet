#!/usr/bin/env python3
"""_fnlinks.py -- does clicking a footnote mark take the reader to the footnote?

WHY. pdfTeX emits "warning (dest): name{Hfootnote.N} has been referenced but does not exist"
once per footnote in this document. Checking that the name EXISTS in the PDF name tree is the
wrong test: a dest can exist and still point at the wrong page. The right test is where each
footnote dest lands versus where that footnote's text actually sits.

WHAT IT MEASURES, per build:
  1. every named destination matching Hfootnote.N and the physical page it resolves to;
  2. the physical pages that actually carry footnote text (small type in the bottom band,
     following the footnote rule);
  3. every link annotation on a body page whose target is a footnote dest, and whether that
     target page equals the page the reader is on.

Usage: _fnlinks.py <pdf> [<pdf> ...]
"""
import ctypes
import sys

import pypdfium2 as pdfium
import pypdfium2.raw as C


def named_dests(doc):
    out = {}
    for k in range(C.FPDF_CountNamedDests(doc.raw)):
        ln = C.c_long(0)
        C.FPDF_GetNamedDest(doc.raw, k, None, ctypes.byref(ln))
        buf = ctypes.create_string_buffer(ln.value)
        dest = C.FPDF_GetNamedDest(doc.raw, k, buf, ctypes.byref(ln))
        name = buf.raw.decode("utf-16-le", "replace").rstrip("\x00")
        out[name] = C.FPDFDest_GetDestPageIndex(doc.raw, dest) if dest else None
    return out


def footnote_text_pages(doc, size_max=10.5, band_top=260.0, min_glyphs=60):
    """Physical pages carrying a block of small type low on the page."""
    pages = []
    for i in range(len(doc)):
        pg = doc[i]
        tp = pg.get_textpage()
        n = C.FPDFText_CountChars(tp.raw)
        count = 0
        for j in range(n):
            code = C.FPDFText_GetUnicode(tp.raw, j)
            ch = chr(code) if code else ""
            if ch.isspace() or not ch:
                continue
            size = C.FPDFText_GetFontSize(tp.raw, j)
            if size >= size_max:
                continue
            l, b, r, t = (ctypes.c_double() for _ in range(4))
            if not C.FPDFText_GetCharBox(tp.raw, j, l, r, b, t):
                continue
            if b.value < band_top:
                count += 1
        if count >= min_glyphs:
            pages.append((i + 1, count))
    return pages


def footnote_link_annots(doc, dests):
    """Link annotations whose destination is a footnote dest, with source and target pages."""
    rows = []
    fn = {k: v for k, v in dests.items() if k.lower().startswith("hfootnote")}
    targets = set(fn.values())
    for i in range(len(doc)):
        pg = doc[i]
        for j in range(C.FPDFPage_GetAnnotCount(pg.raw)):
            an = C.FPDFPage_GetAnnot(pg.raw, j)
            try:
                if C.FPDFAnnot_GetSubtype(an) != C.FPDF_ANNOT_LINK:
                    continue
                lk = C.FPDFAnnot_GetLink(an)
                if not lk:
                    continue
                ds = C.FPDFLink_GetDest(doc.raw, lk)
                if not ds:
                    continue
                tgt = C.FPDFDest_GetDestPageIndex(doc.raw, ds)
                if tgt in targets and tgt == 0 and i > 0:
                    rows.append((i + 1, tgt + 1))
            finally:
                C.FPDFPage_CloseAnnot(an)
    return rows


def main() -> int:
    for path in sys.argv[1:]:
        doc = pdfium.PdfDocument(path)
        dests = named_dests(doc)
        fn = {k: v for k, v in sorted(dests.items()) if k.lower().startswith("hfootnote")}
        print(f"=== {path.split('/')[-1]} ({len(doc)} pp) ===")
        print(f"  footnote dests -> resolved physical page: "
              f"{ {k: (v + 1 if v is not None and v >= 0 else v) for k, v in fn.items()} }")
        txt = footnote_text_pages(doc)
        print(f"  pages actually carrying footnote text: {txt}")
        bad = [k for k, v in fn.items() if v == 0]
        print(f"  footnote dests landing on physical page 1: {len(bad)} of {len(fn)} -> {sorted(bad)}")
        if txt and bad:
            print(f"  => every one of those anchors is wrong: the earliest footnote text is on "
                  f"p.{txt[0][0]}, not p.1")
        rows = footnote_link_annots(doc, dests)
        print(f"  link annotations on a body page whose footnote target is p.1: {len(rows)} "
              f"{rows[:8]}")
        controls = {k: dests.get(k) for k in ("chapter.5", "section.5.6", "cite.silva2025mtlnet")}
        print(f"  control dests (should NOT be 0): "
              f"{ {k: (v + 1 if v is not None else v) for k, v in controls.items()} }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
