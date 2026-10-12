#!/usr/bin/env python3
"""ink_sweep.py — ate onde a tinta do corpo desce, pagina a pagina.

Responde a pergunta que o log de compilacao NAO responde e que a canaria de
`pdftotext` NAO responde: "o conteudo desce ate onde nao devia?". O log nao ve
colisao de blocos; a canaria ve se o texto existe no PDF, nao onde ele esta.

Calibrado ao nesped.sty:
  * a faixa de navegacao + a faixa colorida do titulo ocupam o topo -> descartadas;
  * o numero do frame mora no canto inferior direito -> descartado;
  * capa, \\tocframe e \\specialframe pintam a pagina inteira de degrade ->
    detectadas pela luminancia do miolo e tiradas da conta. Sem isso a taxa de
    falso positivo e 100%.

Alvo medido (2026-08-26): o demo do proprio nesped_slides_template tem mediana
0,750 em 13 paginas de conteudo. O deck da defesa tinha 0,912 em 100 paginas,
com 60 acima de 0,90. **A tinta do corpo deve parar em ~0,85; acima de 0,93 e
defeito.** Ver BOAS_PRATICAS_SLIDES.md §8.1.

uso:  python3 ink_sweep.py slides/main.pdf [dpi] [--limiar 0.93]
      python3 ink_sweep.py nesped_slides_template/main.pdf   # a referencia
"""
import glob
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

ALVO = 0.85
LIMIAR = 0.93


def sweep(pdf, dpi=72, limiar=LIMIAR):
    tmp = tempfile.mkdtemp(prefix="ink_")
    subprocess.run(
        ["pdftoppm", "-r", str(dpi), "-png", "-gray", pdf, f"{tmp}/p"], check=True
    )
    rows = []
    palidas = []          # paginas quase sem tinta -- candidato a fundo que nao desenhou
    for i, p in enumerate(sorted(glob.glob(f"{tmp}/p-*.png")), 1):
        a = np.asarray(Image.open(p).convert("L"))
        h, w = a.shape

        # pagina de fundo cheio: o miolo da area de conteudo e' escuro (degrade)
        core = a[int(h * 0.35): int(h * 0.90), int(w * 0.10): int(w * 0.90)]
        if core.mean() < 180:
            rows.append((i, None, False))
            continue

        # ⚠ DIVISOR QUEBRADO (26/08). A regra acima -- ignorar pagina de fundo cheio -- e' a
        # que escondeu o divisor da Secao 5 renderizado SEM o degrade: texto branco sobre
        # branco. Os tres instrumentos passaram (pdftotext extraia os seis titulos, nenhum
        # Overfull, e esta varredura classificava a pagina como fundo cheio e a EXCLUIA).
        # Quem achou foi o autor, olhando. A correcao inverte o sinal: numa pagina que
        # DEVERIA ter fundo, exigir tinta em vez de ignora-la. Um \tocframe sem fundo tem
        # tinta perto de zero, e e' isso que o denuncia.
        pal = a[int(h * 0.22):, :] < 200
        if pal.mean() < 0.004 and i not in (1,):
            palidas.append((i, float(pal.mean())))

        ink = a < 200                                   # tinta = nao-fundo
        ink[int(h * 0.92):, int(w * 0.93):] = False      # numero do frame
        ink[: int(h * 0.22), :] = False                  # navbar + faixa do titulo

        r = np.where(ink.any(axis=1))[0]
        low = (r[-1] / h) if len(r) else 0.0

        # A faixa y 0.92-0.98 e' onde o nesped desenha o numero do frame, em
        # x 0.978-0.987 (medido). Numa pagina saudavel do template ela nao tem
        # mais nada. Dois sinais distintos, e nao sao a mesma coisa:
        #   invade  -> ha conteudo nessa faixa (o slide ficou sem margem inferior)
        #   colide  -> o conteudo chega ate a COLUNA do numero e passa por cima
        band = ink[int(h * 0.92): int(h * 0.98), :]
        invade = bool(band[:, : int(w * 0.95)].any())
        colide = bool(band[:, int(w * 0.95): int(w * 0.975)].any())
        rows.append((i, low, invade, colide))
    return rows, palidas


def main():
    pdf = sys.argv[1]
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 72
    limiar = LIMIAR
    if "--limiar" in sys.argv:
        limiar = float(sys.argv[sys.argv.index("--limiar") + 1])

    rows, palidas = sweep(pdf, dpi, limiar)
    corpo = [r for r in rows if r[1] is not None]
    fundo = len(rows) - len(corpo)
    b = np.array([r[1] for r in corpo])

    print(f"{pdf}   {len(rows)} paginas @ {dpi} dpi "
          f"({len(corpo)} de conteudo, {fundo} de fundo cheio)")
    print(f"  tinta mais baixa: mediana {np.median(b):.3f} · p25 {np.percentile(b,25):.3f}"
          f" · p90 {np.percentile(b,90):.3f} · max {b.max():.3f}")
    print(f"  alvo {ALVO:.2f}   ·   acima de {limiar:.2f}: {(b>limiar).sum()}/{len(b)}"
          f"   ·   acima de 0.90: {(b>0.90).sum()}/{len(b)}")
    print()

    invade = [r for r in corpo if r[2]]
    colide = [r for r in corpo if r[3]]
    fundo_ = [r for r in corpo if r[1] > limiar]

    print(f"COLIDE com o numero do frame ({len(colide)}):  "
          + (", ".join(f"p{r[0]}" for r in colide) or "nenhuma"))
    print(f"desce alem de {limiar:.2f} ({len(fundo_)}):  "
          + (", ".join(f"p{r[0]}" for r in fundo_) or "nenhuma"))
    print(f"invade a faixa do rodape, sem colidir ({len(invade)-len(colide)}):  "
          + (", ".join(f"p{r[0]}" for r in invade if not r[3]) or "nenhuma"))
    print()
    if palidas:
        print(f"🛑 PAGINA QUASE SEM TINTA ({len(palidas)}) -- provavel fundo que nao desenhou.")
        print("   Reconstrua com `make all` (TRES passes) e OLHE a pagina; nenhum outro")
        print("   instrumento pega este defeito.")
        for i, m in palidas:
            print(f"     p{i:<4} tinta {m*100:.2f}% da area util")
    else:
        print("nenhuma pagina quase sem tinta (divisores e capa desenharam o fundo)")
    print()
    print("--- as 12 paginas de conteudo que mais descem ---")
    for i, low, inv, col in sorted(corpo, key=lambda r: -r[1])[:12]:
        tags = ("   COLIDE" if col else ("   invade" if inv else ""))
        print(f"  p{i:>3}   {low:.3f}{tags}")

    return 1 if (colide or fundo_) else 0


if __name__ == "__main__":
    sys.exit(main())
