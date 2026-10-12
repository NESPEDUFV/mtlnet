"""Claim-parity + envelope check for the Resumo/Abstract pair, measured on the RENDERED page.

USAGE
    PAIR_PDF=<path to a FRESH main.pdf> PT_PAGE=3 EN_PAGE=4 python3 _check_pair_parity.py

It defaults to ../../../src/build/main.pdf, which may be STALE: if the pair has not been rebuilt, the
Abstract is still on p.5 and this script will report EN=0 words on p.4 and divide by zero. That is
the intended failure -- it means you are pointing it at a PDF that does not match the source, not
that the check is broken. Rebuild (make defense) or pass PAIR_PDF/PT_PAGE/EN_PAGE explicitly.

Measured 2026-07-28 against 870f882c + the cut 0_main.tex: PT p.3 310 w / 11 s, EN p.4 271 w / 11 s,
19/19 floor claims present in both languages, zero law-sweep hits.
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _measure_abs import words, sentences, strip_header, strip_keywords
import pypdfium2 as pdfium

def norm(t):
    """Undo PDF line-break hyphenation so phrase matching sees the prose, not the typesetting.
    pdfium emits U+FFFE/U+00AD style soft hyphens at justified line breaks: 'user-\\ndisjoint'
    renders as 'user\\ufffedisjoint'. Both the break hyphen and the newline must go."""
    t = t.replace("\ufffe", "-").replace("\u00ad", "-").replace("\r", "\n")
    t = re.sub(r"-\n(?=\w)", "-", t)      # keep a real compound hyphen, drop the newline
    t = re.sub(r"\s+", " ", t)
    return t

def block(pdf, page):
    t = pdfium.PdfDocument(pdf)[page-1].get_textpage().get_text_range()
    t, _ = strip_header(t); t, _ = strip_keywords(t)
    return norm(t)

PDF = os.environ.get("PAIR_PDF",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "src", "build", "main.pdf"))
PAGES = (int(os.environ.get("PT_PAGE", 3)), int(os.environ.get("EN_PAGE", 4)))
PT, EN = block(PDF, PAGES[0]), block(PDF, PAGES[1])

FLOOR = {
 "research question open":   (r"permanecia em aberto",                      r"was unresolved"),
 "answer CONDITIONAL":       (r"condicional",                               r"conditional"),
 "representation dominates": (r"o gargalo era a representa",                r"bottleneck was the representation"),
 "input > architecture":     (r"substituiu apenas a entrada",               r"replaced only the input"),
 "joint model outperforms":  (r"supera os modelos dedicados",               r"outperforms the dedicated models"),
 "next category":            (r"próxima categoria",                         r"next category"),
 "next region":              (r"próxima região",                            r"next region"),
 "next PLACE excluded":      (r"mas não o ponto de interesse exato",        r"though not the exact next place"),
 "5.3 to 9.4":               (r"5,3 a 9,4",                                 r"5\.3 to 9\.4"),
 "joint-best convention":    (r"joint-best",                                r"joint-best"),
 "four of six":              (r"quatro deles",                              r"four of them"),
 "TOST two-point margin":    (r"margem de dois pontos de Acc@10",           r"two-point Acc@10 margin"),
 "Gowalla five US states":   (r"cinco estados dos Estados Unidos",          r"five states of the United States from Gowalla"),
 "Istanbul Massive-STEPS":   (r"Istambul, do Massive-STEPS",                r"Istanbul from Massive-STEPS"),
 "user-disjoint CV":         (r"usuários disjuntos entre treino e teste",   r"user-disjoint cross-validation"),
 "MTL expanded":             (r"aprendizado multitarefa \(MTL\)",           r"multi-task learning \(MTL\)"),
 "check-in level":           (r"nível do check-in",                         r"check-in level"),
 "n=20 fitted models":       (r"vinte modelos ajustados",                   r"twenty fitted models"),
 "equipara-se / matches":    (r"equipara-se estatisticamente",              r"statistically matches"),
}
print("FLOOR CHECK on the RENDERED pages, hyphenation normalized:")
bad = []
for k, (p, e) in FLOOR.items():
    hp, he = bool(re.search(p, PT, re.I)), bool(re.search(e, EN, re.I))
    if not (hp and he): bad.append(k)
    print(f"  {'OK ' if hp and he else '!! '}{k:26s} PT={'Y' if hp else 'N'}  EN={'Y' if he else 'N'}")
print(f"floor failures: {len(bad)} {bad}")

sp, se = sentences(PT), sentences(EN)
print(f"\nrendered sentence counts: PT {len(sp)} / EN {len(se)}")
print(f"rendered word counts:     PT {len(words(PT))} / EN {len(words(EN))}")
print(f"rendered means:           PT {len(words(PT))/len(sp):.1f} / EN {len(words(EN))/len(se):.1f}")

