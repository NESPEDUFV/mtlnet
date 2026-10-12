#!/usr/bin/env python3
"""Mechanical bibliography audit: duplicate keys, key fragmentation, dangling and dead keys.

This is the citation MACHINERY only (does a key resolve, and does it resolve to ONE entry).
Whether a reference is real and supports its sentence is persona 05's gate, not this one.

Run from src/.
"""
import glob
import re
from collections import Counter, defaultdict

BIB = "references.bib"


def strip_comments(text: str) -> str:
    out = []
    for line in text.split("\n"):
        buf = []
        i = 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                break
            buf.append(line[i])
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def main() -> int:
    raw = open(BIB, encoding="utf8").read()
    keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", raw)
    counts = Counter(keys)
    dup = {k: v for k, v in counts.items() if v > 1}
    print(f"entries={len(keys)} unique={len(counts)} duplicate_keys={dup or 'NONE'}")

    clusters = defaultdict(list)
    for k in keys:
        m = re.match(r"([a-zA-Z]+)(\d{4})", k)
        if m:
            clusters[(m.group(1).lower(), m.group(2))].append(k)
    multi = {k: v for k, v in clusters.items() if len(v) > 1}
    print("\nsame-author-same-year key clusters (candidate fragmentation of one work):")
    for k, v in sorted(multi.items()):
        titles = []
        for key in v:
            m = re.search(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,(.*?)\n\}", raw, re.S)
            t = re.search(r"title\s*=\s*[{\"](.+?)[}\"],?\s*\n", m.group(1), re.S) if m else None
            title = re.sub(r"\s+", " ", t.group(1))[:64] if t else "(no title)"
            titles.append(f"{key} = {title}")
        print(f"  {k[0]} {k[1]}:")
        for t in titles:
            print(f"      {t}")

    cited = set()
    files = (sorted(glob.glob("chapters/*.tex")) + sorted(glob.glob("chapters/*/*.tex"))
             + sorted(glob.glob("tables/*/*.tex")) + ["0_main.tex"])
    for f in files:
        txt = strip_comments(open(f, encoding="utf8").read())
        for m in re.finditer(r"\\cite[a-z]*\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}", txt):
            for k in m.group(1).split(","):
                cited.add(k.strip())
    defined = set(keys)
    print(f"\nfiles scanned={len(files)}  cited_keys={len(cited)}  defined_entries={len(defined)}")
    print(f"cited but NOT defined (dangling): {sorted(cited - defined) or 'NONE'}")
    print(f"defined but NEVER cited (dead weight): {sorted(defined - cited) or 'NONE'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
