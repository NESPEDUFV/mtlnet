#!/bin/zsh
# Exporta a figura em tamanho final para o deck.  Confere o gabarito (140x60mm)
# e recusa entregar algo que a `ppt` teria de reduzir -- reduzir afina os tracos.
set -e
FIG="$1"; [ -z "$FIG" ] && { echo "uso: ./export.sh <fig>"; exit 1; }
cd "$(dirname "$0")"; mkdir -p build plates
xelatex -interaction=nonstopmode -halt-on-error -output-directory=build \
        "\def\FIGFILE{$FIG}\input{standalone.tex}" > "build/${FIG}_std.log" 2>&1 \
        || { echo "FALHOU:"; grep -n '^!' -A5 "build/${FIG}_std.log" | head -30; exit 1; }
mv build/standalone.pdf "plates/$FIG.pdf"
SZ=$(pdfinfo "plates/$FIG.pdf" | awk '/Page size/{print $3, $5}')
W=$(echo $SZ | awk '{printf "%.1f", $1*25.4/72.27}')
H=$(echo $SZ | awk '{printf "%.1f", $2*25.4/72.27}')
echo "plates/$FIG.pdf  ->  ${W} x ${H} mm"
# Dois limites, porque a altura util do slide NAO e' um numero so'.  A `ppt`
# mediu 67,4mm quando o \frametitle cabe em uma linha e 63,7mm quando quebra em
# duas -- e o titulo e' decisao do `gate`, nao minha.  Entao:
#   62mm = teto DURO, ja' descontado o pior caso de titulo (63,7) com margem;
#   56mm = alvo de FOLGA, para sobrar espaco de texto em volta da figura.
awk -v w=$W -v h=$H 'BEGIN{
  bad=0
  if (w > 140) { print "  *** ESTOURA a largura util (140 mm) ***"; bad=1 }
  if (h > 62)  { print "  *** ESTOURA a altura no pior caso de titulo (62 mm) ***"; bad=1 }
  else if (h > 56) { print "  aviso: acima do alvo de folga (56 mm) -- cabe, mas nao sobra linha de texto" }
  if (!bad) print "  ok: entra em tamanho final, sem escalar."
  exit bad
}'
