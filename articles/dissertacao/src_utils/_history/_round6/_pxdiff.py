#!/usr/bin/env python3
"""Rasterize two PDFs page by page and report which pages differ by any pixel.

A text-layer comparison can miss a placement change (a figure moved, a rule redrawn);
this is the render-level test. Usage: _pxdiff.py A.pdf B.pdf [--scale 1.0]
"""
import argparse
import re

import numpy as np
import pypdfium2 as pdfium


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()
    da, db = pdfium.PdfDocument(args.a), pdfium.PdfDocument(args.b)
    print(f"pages: {len(da)} vs {len(db)}")
    diff = []
    for i in range(min(len(da), len(db))):
        ia = np.array(da[i].render(scale=args.scale).to_pil().convert("L"))
        ib = np.array(db[i].render(scale=args.scale).to_pil().convert("L"))
        if ia.shape != ib.shape:
            diff.append((i + 1, "shape"))
        elif not (ia == ib).all():
            diff.append((i + 1, int((ia != ib).sum())))
    print(f"pages differing: {diff if diff else 'NONE'}")
    for p in (args.a, args.b):
        raw = open(p, "rb").read()
        cd = re.findall(rb"/CreationDate\s*\(([^)]*)\)", raw)
        pid = re.findall(rb"/ID\s*\[\s*<([0-9A-Fa-f]+)>", raw)
        print(f"  {p.split('/')[-1]}: CreationDate={cd[:1]} ID_prefix={pid[:1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
