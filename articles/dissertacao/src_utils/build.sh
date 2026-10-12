#!/bin/bash
# Build the dissertation and verify the result honestly.
#
#   usage: src_utils/build.sh <srcdir> [defense|academico|both]     ('final' still accepted)
#   e.g.   src_utils/build.sh src both
#
# This lived in /tmp for one whole working session and was swept mid-session, which silently turned
# a "rebuild and check" step into "check a stale PDF". It belongs in the repository.
#
# VERIFICATION RULES, each learned by shipping the corresponding defect:
#   - LaTeX WRAPS warnings at 79 columns, so the log MUST be flattened before matching. A
#     line-anchored grep reported "0 undefined citations" while four rendered as (??) in both PDFs.
#   - The .blg must be read separately: a BibTeX error (e.g. a bare at-sign inside a % comment in
#     references.bib) never reaches the .log.
#   - "Text page N contains only floats" is NOT emitted for every floats-only page, so those are
#     measured from the PDF text layer instead.
#   - Report ONLY the variants this invocation actually built; a stale build/<stem>.log was
#     otherwise presented as a fresh measurement.
#   - FAIL LOUDLY if a build produced no PDF. A silent build failure is how a stale PDF gets
#     audited in place of the real one.
#
# The TeX font map must come from the user tree; without TEXMFVAR/TEXMFCONFIG set, pdflatex dies
# with "Font ntx-Regular-tlf-ot1r ... not found" (or t1xtt, depending on which face it reaches
# first). That is NOT a missing font: the .tfm and .pfb are both in $TEXMFHOME. It is the font
# MAP, which newtx writes into the usermode updmap output. The defaults below point at the
# PERSISTENT tree under $TEXMFHOME rather than /tmp: a swept /tmp used to lose the map and
# trigger a full updmap-user rebuild, and on this machine
# `kpsewhich -var-value TEXMFVAR` reports an unreadable path, so it cannot be probed either.
# Same values as src_utils/texenv.sh, which is what a human should source before `make`.
set -u
export PATH=/Library/TeX/texbin:$PATH
export TEXMFHOME="${TEXMFHOME:-$HOME/Library/texmf}"
export TEXMFVAR="${TEXMFVAR:-$HOME/Library/texmf/.texmf-var}"
export TEXMFCONFIG="${TEXMFCONFIG:-$HOME/Library/texmf/.texmf-config}"
mkdir -p "$TEXMFVAR" "$TEXMFCONFIG"
# Regenerate the user font map if it is missing.
if ! kpsewhich pdftex.map >/dev/null 2>&1 || ! grep -q "^ntx-Regular" "$TEXMFVAR/fonts/map/pdftex/updmap/pdftex.map" 2>/dev/null; then
  updmap-user --quiet >/dev/null 2>&1 || true
fi

SRC="${1:?usage: build.sh <srcdir> [defense|academico|both]}"
MODE="${2:-defense}"
cd "$SRC" || exit 1
mkdir -p build build/chapters

run_defense() {
  pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null 2>&1
  BIBINPUTS=.: TEXMFOUTPUT=build bibtex build/main >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null 2>&1
  BIBINPUTS=.: TEXMFOUTPUT=build bibtex build/main >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null 2>&1
  pdflatex -interaction=nonstopmode -output-directory=build main.tex >/dev/null 2>&1
}
# The deposit build. Was `run_final`, writing main_final.pdf from a command-line
# "\def\FINALBUILD{}\input{main.tex}" injection, until 2026-07-29: the author renamed the build
# `academico` and it now has its own thin entry file (LATEX_UPGRADE.md §4 A-1/A-2/A-3), so this
# compiles main_academico.tex like the other two and injects nothing.
run_academico() {
  J="-jobname=main_academico"
  pdflatex -interaction=nonstopmode -output-directory=build $J main_academico.tex >/dev/null 2>&1
  BIBINPUTS=.: TEXMFOUTPUT=build bibtex build/main_academico >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -output-directory=build $J main_academico.tex >/dev/null 2>&1
  BIBINPUTS=.: TEXMFOUTPUT=build bibtex build/main_academico >/dev/null 2>&1 || true
  pdflatex -interaction=nonstopmode -output-directory=build $J main_academico.tex >/dev/null 2>&1
  pdflatex -interaction=nonstopmode -output-directory=build $J main_academico.tex >/dev/null 2>&1
}

BUILT=""
case "$MODE" in
  defense)   run_defense; BUILT="main";;
  academico) run_academico; BUILT="main_academico";;
  # `final` was this mode's name until 2026-07-29. Kept as an accepted spelling rather than
  # removed: `build.sh src both` is what the documented protocol calls, but `src final` appears
  # in older notes, and a mode name that silently exits 2 would read as a broken script.
  final)     run_academico; BUILT="main_academico";;
  both)      run_defense; run_academico; BUILT="main main_academico";;
  *) echo "unknown mode: $MODE (defense|academico|both; 'final' = academico, renamed 2026-07-29)"; exit 2;;
esac

# NOTE: we already cd'd into "$SRC", so the verifier must resolve paths from the CURRENT
# directory, not from "$SRC" again. Passing "$SRC" here looked for src/build/ INSIDE src/ and
# printed "BUILD FAILED" for a build that had in fact succeeded. Only invocations that happened
# to pass "." were unaffected, which is why this survived a whole session.
BUILT="$BUILT" python3 - "$PWD" <<'PY'
import os, re, sys
src = sys.argv[1]
built = os.environ.get("BUILT", "").split()
label = {"main": "DEFENSE", "main_academico": "ACADEMICO"}
rc = 0
for stem in built:
    lg = os.path.join(src, "build", stem + ".log")
    pdf = os.path.join(src, "build", stem + ".pdf")
    if not os.path.exists(pdf):
        print(f"{label[stem]}: BUILD FAILED — no PDF produced")
        for pat in (r"^! .*", r"Fatal error occurred.*", r"Font \S+ .*not found"):
            if os.path.exists(lg):
                for m in re.findall(pat, open(lg, encoding="utf8", errors="replace").read(), re.M)[:3]:
                    print(f"    {m.strip()[:110]}")
        rc = 1
        continue
    raw = open(lg, encoding="utf8", errors="replace").read()
    flat = raw.replace("\n", "")                      # LaTeX wraps warnings at 79 cols
    pages = re.findall(r"Output written on \S+ \((\d+) pages", raw)
    ofh = re.findall(r"Overfull \\hbox \(([\d.]+)pt too wide\)", raw)
    ofv = re.findall(r"Overfull \\vbox \(([\d.]+)pt too high\)", raw)
    undc = sorted(set(re.findall(r"Citation `([^']+)' on page \d+ undefined", flat)))
    undr = sorted(set(re.findall(r"Reference `([^']+)' on page \d+ undefined", flat)))
    # Floats taller than the text block. LaTeX reports this as a WARNING, never as an overfull
    # box, so the ofh/ofv counters miss it: a table can hang 160pt below the bottom margin while
    # the build reports 0 overfull. Found 2026-07-27 by the AUTHOR'S EYE on p.96, after this
    # checker had certified the build clean four times. The log carried "Float too large for page
    # by 163.4335pt on input line 98" the whole time.
    bigfloat = re.findall(r"Float too large for page by ([\d.]+)pt on input line (\d+)", flat)
    # TeX ERRORS, which this checker did not look for until 2026-07-28 and which is the worst
    # miss in its history: this script's interaction mode means the "no PDF produced" branch
    # above never fires on a source that does not compile, so THIS is the only place a TeX error
    # is caught. The mechanism, the six commits it cost (6d780b58..a880632b) and the numbers
    # this script printed while blind are documented once, canonically, in
    # src_utils/README_SRC.md -- read it there before weakening anything below.
    # Errors are collected from BOTH the raw log (each "! ..." line) and the flattened log
    # (the fatal notice wraps).
    texerr = re.findall(r"^! .*", raw, re.M)
    fatal = bool(re.search(r"Fatal error occurred", flat))
    blg = os.path.join(src, "build", stem + ".blg")
    bibe = []
    if os.path.exists(blg):
        b = open(blg, encoding="utf8", errors="replace").read()
        bibe = [l for l in b.split("\n") if re.search(r"error|didn't find|I was expecting", l, re.I)]
    low = "unmeasured"
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(pdf)
        low = [i + 1 for i in range(len(doc))
               if len(re.findall(r"[A-Za-z]{2,}", doc[i].get_textpage().get_text_range())) < 120] or "none"
    except Exception as exc:
        low = f"unmeasured({exc.__class__.__name__})"
    print(f"{label[stem]}: pages={pages} tex_errors={len(texerr)} overfull_hbox={len(ofh)} "
          f"overfull_vbox={len(ofv)} "
          f"undef_cite={len(undc)} undef_ref={len(undr)} bibtex_problems={len(bibe)} "
          f"oversized_floats={len(bigfloat)} "
          f"low_text_pages(<120 words, inspect)={low}")
    for e in texerr[:5]:
        print(f"    TEX ERROR: {e.strip()[:110]}")
    if texerr:
        print("    ^ a PDF was still written because nonstopmode recovers; `make` (-halt-on-error) "
              "produces NOTHING from this source. The PDF above is not the document.")
    if fatal:
        print("    FATAL: the log records a fatal error")
    for pt, ln in bigfloat:
        print(f"    FLOAT TOO LARGE: {pt}pt past the text block, declared at input line {ln}")
    for u in undc: print(f"    UNDEFINED CITE: {u}")
    for u in undr: print(f"    UNDEFINED REF: {u}")
    for e in bibe[:5]: print(f"    BIBTEX: {e[:110]}")
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\)([^\n]*)", raw):
        print(f"    hbox {m.group(1)}pt:{m.group(2)[:80]}")
    if undc or undr or bibe or ofh or ofv or bigfloat or texerr or fatal:
        rc = 1
sys.exit(rc)
PY
