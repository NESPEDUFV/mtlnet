#!/usr/bin/env python3
"""Audit the Resumo/Abstract keyword blocks against UFV_COMPLIANCE section 2 system rules:
one keyword per line, lowercase except proper nouns, no punctuation.

Measured on the RENDERED page text layer, not the source, so what is checked is what prints.
Usage: _kwaudit.py <pdf> <resumo_page> <abstract_page>
"""
import re
import sys

import pypdfium2 as pdfium

PARA = re.compile(r"^\s{2,}\S", re.M)


def main() -> int:
    pdf, p_res, p_abs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    d = pdfium.PdfDocument(pdf)
    for pno, lbl in ((p_res, "Resumo"), (p_abs, "Abstract")):
        t = d[pno - 1].get_textpage().get_text_range()
        m = re.search(r"(Palavras-chave|Keywords)\s*:(.*)$", t, re.S)
        if not m:
            print(f"p.{pno} {lbl}: NO keyword block found on this page")
            continue
        lines = [l.strip() for l in m.group(2).split("\n") if l.strip()]
        print(f"p.{pno} {lbl}: keyword block has {len(lines)} line(s)")
        for line in lines:
            issues = []
            if re.search(r"[.,;:]$", line):
                issues.append("trailing punctuation")
            for w in line.split():
                if w[:1].isupper():
                    issues.append(f"capitalized token '{w}'")
            flag = ("   <-- " + ", ".join(issues)) if issues else ""
            print(f"    {line!r}{flag}")
        body = t[:m.start()]
        n_para = len(PARA.findall(body))
        print(f"    indented paragraph starts in the block above the keywords: {n_para}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
