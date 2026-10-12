#!/bin/zsh
# Compila src/<fig>.tex dentro de um slide real e exporta PNG para revisao visual.
set -e
FIG="$1"; TITLE="${2:-${1//_/ }}"
[ -z "$FIG" ] && { echo "uso: ./build.sh <fig> [titulo]"; exit 1; }
cd "$(dirname "$0")"
mkdir -p build png
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build \
        "\def\FIGFILE{$FIG}\def\FIGTITLE{$TITLE}\input{preview.tex}" \
        > "build/$FIG.log" 2>&1 || { echo "FALHOU:"; grep -n '^!' -A6 "build/$FIG.log" | head -40; exit 1; }
mv "build/preview.pdf" "build/$FIG.pdf"
pdftoppm -png -r 220 "build/$FIG.pdf" "png/$FIG"
echo "OK -> png/$FIG-1.png"
echo "  avisos de caixa: $(grep -c 'Overfull\|Underfull' build/$FIG.log)"
