#!/usr/bin/env python3
"""_lint_subset.py -- the load-bearing ChkTeX/lacheck checks, implemented directly.

WHY THIS EXISTS. Persona 19 specifies running chktex and lacheck. Neither is present in this
machine's TeX Live 2026 *basic* tree (`which chktex lacheck` -> not found; nothing under
/usr/local/texlive matches either name; `kpsewhich chktexrc` returns nothing). Rather than
report silence, the subset of their warnings that is load-bearing for THIS document is
implemented here and run against the real source.

CHECKS IMPLEMENTED HERE (nine; each maps to a named ChkTeX/lacheck warning class):
  1. missing tie before a reference macro   (ChkTeX 13: "You should use ~ ...")
  2. hardcoded float/section numbers in prose ("Figure 3.2", "Table 8", "Section 5.6")
  3. straight double quote " used instead of TeX `` '' (ChkTeX 38)
  4. inline math with $...$ rather than \\(...\\) (ChkTeX 1 / l2tabu, informational)
  5. italic-correction and small-caps obsolete forms: \\bf \\it \\rm \\sc \\tt (l2tabu)
  6. ellipsis typed as ... rather than \\dots / \\ldots
  7. footnote placed before the punctuation it belongs after
  8. unbalanced $ count per line
  9. \\label placed BEFORE its \\caption inside a float (lacheck; the label then silently
     points at the enclosing section number rather than the float)

NOT implemented, and therefore NOT covered by a green run of this script: ChkTeX 11
(swallowed space after a text macro) and nested-quote direction. If either matters, run the
real chktex on a machine with a full TeX Live.

Checks 1-8 are per-line regex; check 9 is a small float-environment state machine.
Comment-stripped source only. Run from src/.
"""
import glob
import re
import sys

MACROS = r"(?:ref|cref|Cref|autoref|pageref|eqref|cite|citeonline|citep|citet)"


def strip_comments(text: str):
    """Blank comments but preserve line numbering."""
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
    return out


def files():
    return (sorted(glob.glob("chapters/*.tex")) + sorted(glob.glob("chapters/*/*.tex"))
            + sorted(glob.glob("tables/*/*.tex")) + ["0_main.tex", "main.tex", "main_ppgc.tex"])


CHECKS = {
    # 1. a word character immediately before the macro with a plain space, no tie
    "no_tie_before_ref": re.compile(r"[A-Za-z\)\]] \\" + MACROS + r"\s*\{"),
    # 2. hardcoded cross-reference numbers
    "hardcoded_number": re.compile(
        r"\b(?:Figure|Table|Section|Chapter|Equation|Appendix)~?\s?\d+(?:\.\d+)*\b"),
    # 3. straight double quotes
    "straight_quote": re.compile(r'(?<!\\)"'),
    # 4. dollar-delimited inline math
    "dollar_math": re.compile(r"(?<!\\)\$(?!\$)"),
    # 7. obsolete font commands (l2tabu)
    "obsolete_font": re.compile(r"\\(?:bf|it|rm|sc|tt|sf|sl|cal)(?![a-zA-Z])"),
    # 8. bare ellipsis
    "bare_ellipsis": re.compile(r"(?<![.\\])\.\.\.(?!\.)"),
    # 9. footnote before punctuation
    "footnote_before_punct": re.compile(r"\\footnote\{[^{}]*\}\s*[.,;:]"),
}


FLOAT_BEGIN = re.compile(r"\\begin\{(figure|table|longtable)\*?\}")
CAPTION = re.compile(r"\\caption")
LABEL = re.compile(r"\\label\{")


def label_before_caption(lines):
    """Check 9 (lacheck): a \\label placed before its \\caption inside a float.

    LaTeX resolves \\label against the most recently incremented counter, so a label that
    precedes its caption points at the enclosing SECTION number, not at the float. The build
    is clean and \\ref resolves, to the wrong number -- no warning is ever raised.
    """
    out = []
    env = cap = lab = start = None
    for i, line in enumerate(lines, 1):
        m = FLOAT_BEGIN.search(line)
        if m:
            env, cap, lab, start = m.group(1), None, None, i
        if env:
            if cap is None and CAPTION.search(line):
                cap = i
            if lab is None and LABEL.search(line):
                lab = i
            if re.search(r"\\end\{" + env + r"\*?\}", line):
                if lab and cap and lab < cap:
                    out.append((start, f"{env}: \\label at :{lab} precedes \\caption at :{cap}"))
                env = None
    return out


def main() -> int:
    hits = {k: [] for k in CHECKS}
    hits["unbalanced_dollar"] = []
    hits["label_before_caption"] = []
    for f in files():
        try:
            lines = strip_comments(open(f, encoding="utf8").read())
        except FileNotFoundError:
            continue
        for n, line in enumerate(lines, 1):
            for name, pat in CHECKS.items():
                for m in pat.finditer(line):
                    hits[name].append((f, n, line.strip()[:110], m.group(0)))
            if line.count("$") % 2 and "$$" not in line:
                hits["unbalanced_dollar"].append((f, n, line.strip()[:110], "$"))
        for start, why in label_before_caption(lines):
            hits["label_before_caption"].append((f, start, why, "label/caption"))
    for name in list(CHECKS) + ["unbalanced_dollar", "label_before_caption"]:
        rows = hits[name]
        print(f"\n== {name}: {len(rows)} hit(s) ==")
        for f, n, line, tok in rows[:14]:
            print(f"   {f}:{n}: [{tok}] {line}")
        if len(rows) > 14:
            print(f"   ... {len(rows) - 14} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
