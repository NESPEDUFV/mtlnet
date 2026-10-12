#!/bin/bash
# texenv.sh -- the TeX environment this document needs. `source` it before make/build.sh/check.sh.
#
# WHY THIS FILE EXISTS. The abntex2 + newtx stack lives in a USERMODE TeX tree under
# $HOME/Library/texmf, not in the system TeX Live tree. Two variables must point there or the
# build fails in two DIFFERENT ways, and the second one is easy to misread:
#
#   TEXMFHOME unset  -> "LaTeX Error: File `abntex2.cls' not found" (obvious).
#   TEXMFVAR wrong   -> the class and every .tfm resolve fine, three passes run, and then
#                       pdftex dies with "!pdfTeX error: Font ntx-Regular-tlf-ot1r at 657 not
#                       found ==> Fatal error occurred, no output PDF file produced!" That is
#                       NOT a missing font: the .tfm and the .pfb are both present in the home
#                       tree. It is the font MAP. newtx registers itself in the usermode
#                       updmap output at $TEXMFHOME/.texmf-var/fonts/map/pdftex/updmap/pdftex.map
#                       (36 ntx entries); the system map at /usr/local/texlive/.../texmf-var has
#                       zero. kpsewhich -var-value TEXMFVAR reports the WRONG path here
#                       ($HOME/Library/texlive/2026basic/texmf-var, which is not readable), so
#                       the value is set explicitly below rather than probed.
#
# pdflatex itself is the system TeX Live 2026 binary at /Library/TeX/texbin, which is not on a
# non-interactive PATH; that is the third line.
export PATH="/Library/TeX/texbin:$PATH"
export TEXMFHOME="$HOME/Library/texmf"
export TEXMFVAR="$HOME/Library/texmf/.texmf-var"
export TEXMFCONFIG="$HOME/Library/texmf/.texmf-config"
