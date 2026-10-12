#!/usr/bin/env python3
"""Measure a Resumo/Abstract block on ONE stated convention, from the RENDERED page.

CONVENTION (the same one applied to every row below, ours and the exemplars):
  1. Take the text layer of the named page(s).
  2. Strip the UFV catalog/identification header: the author-venue-year line, the bold title,
     and the advisor line -- everything up to and including the "Orientador:/Advisor:" or
     "Orientadora:" field. If no such field exists on the page, strip nothing and say so.
  3. Strip the keyword block: everything from "Palavras-chave"/"Keywords"/"Palavras chave"
     to the end of the extracted region.
  4. WORDS  = tokens matching [A-Za-z\u00c0-\u00ff][A-Za-z\u00c0-\u00ff'-]* or a number, i.e. no
     punctuation-only tokens; hyphenated compounds count as ONE word.
  5. SENTENCES = terminal '.', '!' or '?' NOT preceded by a single capital letter (initials),
     not inside a decimal number, and not part of a known abbreviation (Sec., Fig., cf.,
     e.g., i.e., et al., Dr., Prof., M.Sc., Ph.D., U.S.).
  6. MEAN = words / sentences, printed to one decimal.
"""
from __future__ import annotations
import re, sys, json

ABBR = ("sec", "fig", "cf", "eg", "ie", "al", "dr", "prof", "msc", "phd", "us", "no", "vs",
        "etc", "ph", "d", "sc", "univ", "ed", "pp")

NAMEISH = re.compile(r"^(?:[A-Z\u00c0-\u00dd][\w\u00c0-\u00ff.'-]*|d[aeo]s?|e|von|van|del|Filho|J\u00fanior|Neto)"
                     r"(?:\s+(?:[A-Z\u00c0-\u00dd][\w\u00c0-\u00ff.'-]*|d[aeo]s?|e|von|van|del))*$")

def strip_header(t: str):
    """Drop the UFV identification header: author/venue/year line, bold title, advisor and
    co-adviser fields, plus the RESUMO/ABSTRACT heading, plus any name-only lines left over
    when the advisor's name wraps past the field label."""
    hit = False
    for m in re.finditer(r"(Orientador[ae]?s?|Coorientador[ae]?s?|Co-?advis[eo]rs?|Advisors?|Advisers?)"
                         r"\s*\(?[ae]?\)?\s*:?[^\n]*", t):
        t2, hit = t[m.end():], True
    if hit:
        t = t2
    lines = t.split("\n")
    i = 0
    while i < len(lines):
        L = lines[i].strip()
        if L == "" or L.lower() in ("resumo", "abstract") or NAMEISH.match(L):
            i += 1
            continue
        break
    return "\n".join(lines[i:]), hit

def strip_keywords(t: str):
    m = re.search(r"(Palavras[-\s]?chave|Keywords?|Palavras[-\s]?Chave)", t, re.I)
    if m:
        return t[: m.start()], True
    return t, False

def words(t: str):
    return re.findall(r"[A-Za-z\u00c0-\u00ff][A-Za-z\u00c0-\u00ff'\u2019-]*|\d+[\d.,]*", t)

def sentences(t: str):
    t = re.sub(r"\s+", " ", t)
    # protect decimals
    t = re.sub(r"(\d)\.(\d)", "\\1\u2024\\2", t)
    out, buf = [], ""
    i = 0
    while i < len(t):
        ch = t[i]
        buf += ch
        if ch in ".!?":
            tail = re.findall(r"[A-Za-z\u00c0-\u00ff]+$", buf[:-1])
            last = (tail[0] if tail else "").lower().replace(".", "")
            single_cap = bool(re.search(r"(?:^|[\s(])[A-Z]$", buf[:-1]))
            if last in ABBR or single_cap:
                pass
            else:
                nxt = t[i + 1: i + 3]
                if nxt == "" or re.match(r"\s+[A-Z\u00c0-\u00dd\u201c(]", nxt) or re.match(r"\s*$", nxt):
                    s = buf.strip()
                    if words(s):
                        out.append(s)
                    buf = ""
        i += 1
    if words(buf):
        out.append(buf.strip())
    return out

def measure(text: str, label: str, note: str = ""):
    body, hdr = strip_header(text)
    body, kw = strip_keywords(body)
    body = body.replace("\u2024", ".")
    w = words(body)
    s = sentences(body)
    return {"label": label, "words": len(w), "sentences": len(s),
            "mean": round(len(w) / len(s), 1) if s else None,
            "header_stripped": hdr, "keywords_stripped": kw, "note": note,
            "first20": " ".join(w[:12]), "last12": " ".join(w[-12:]),
            "sentence_words": [len(words(x)) for x in s]}

def pdf_pages(path, pages):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(path)
    return "\n".join(doc[p - 1].get_textpage().get_text_range() for p in pages)

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    rows = []
    for item in spec:
        txt = pdf_pages(item["pdf"], item["pages"])
        rows.append(measure(txt, item["label"], item.get("note", "")))
    print(json.dumps(rows, ensure_ascii=False, indent=1))
