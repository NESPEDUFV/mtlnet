#!/usr/bin/env python3
"""canaria_coluna.py — a última palavra de cada coluna chegou ao PDF?

POR QUE ISTO EXISTE (27/08). Uma coluna de `columns` que transborda **não gera
`Overfull`**. A varredura de caixa do deck é contagem de `Overfull`, então todo
slide de duas colunas esteve fora do alcance do instrumento principal.

O caso que o revelou: o slide 32 em `\\small` perdia a palavra `MERGE` — a última
da frase que a fala designa como a que deve ficar na tela. Log limpo, `Overfull`
zero, e metade da frase-chave fora da página. Quem viu foi o autor, olhando.

O QUE ELA MEDE, E O QUE NÃO MEDE.
  mede    : a última palavra visível de cada `column` aparece no texto DAQUELA página.
  não mede: se a palavra está no lugar certo, se colide com o número do frame, ou se
            uma palavra do MEIO caiu (só a cauda é testada).

⚠ A armadilha que ela evita: pegar a "última palavra" de um `.tex` sem filtrar dá
nome de ambiente (`tabular`, `itemize`), argumento de `\\ref`, nome de cor. A canária
passa a medir a si mesma e reporta ausentes falsos. Os filtros abaixo são isso.

⚠ E a busca é PALAVRA ÚNICA, nunca frase: o `pdftotext` quebra linha na largura da
coluna, então qualquer padrão que atravesse a quebra dá ausente — e ausente é sempre
o resultado que parece confirmar que está tudo bem.
"""
import re
import subprocess
import sys

TEX = 'slides/main.tex'
PDF = 'slides/main.pdf'

# nomes que NAO sao conteudo -- se a cauda cair num destes, a canaria mede a si mesma
RUIDO = {
    'columns', 'column', 'itemize', 'enumerate', 'frame', 'block', 'alertblock',
    'exampleblock', 'tabular', 'center', 'minipage', 'figure', 'table',
    'primaryshade', 'secondaryshade', 'alertshade', 'primarytint', 'alerttint',
    'secondarytint', 'black', 'white', 'gray', 'alert', 'textwidth', 'linewidth',
}


def ultima_palavra(corpo: str):
    """A última palavra que um humano vê nesta coluna, ou None."""
    t = re.sub(r'(?<!\\)%.*', '', corpo)                    # comentarios
    t = re.sub(r'\\(ref|label|hyperlink|hypertarget|includegraphics|input)\s*'
               r'(\[[^\]]*\])?\{[^}]*\}', ' ', t)           # comandos cujo ARG nao e' texto
    # ⚠ \textcolor{cor}{texto}: o PRIMEIRO arg e' nome de cor, o segundo e' conteudo.
    # Sem esta linha a canaria colhe 'secondary' e reporta um ausente falso -- aconteceu.
    t = re.sub(r'\\(textcolor|color|colorbox|pagecolor)\s*\{[^}]*\}', ' ', t)
    t = re.sub(r'\\(begin|end)\s*\{[^}]*\}', ' ', t)        # ambientes
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', t)      # o resto dos comandos
    t = re.sub(r'[{}$&#_^~\\]', ' ', t)
    pal = re.findall(r"[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9'’@-]*", t)
    for p in reversed(pal):
        if p.lower() not in RUIDO and len(p) > 2:
            return p
    return None


def paginas_por_titulo():
    """titulo do frame -> primeira pagina do PDF onde ele aparece."""
    n = int(subprocess.run(['pdfinfo', PDF], capture_output=True, text=True)
            .stdout.split('Pages:')[1].split()[0])
    txt = {}
    for i in range(1, n + 1):
        txt[i] = subprocess.run(['pdftotext', '-f', str(i), '-l', str(i), PDF, '-'],
                                capture_output=True, text=True).stdout
    return txt


def main():
    s = open(TEX, encoding='utf-8').read()
    txt = paginas_por_titulo()

    frames = re.findall(r'\\begin\{frame\}.*?\\end\{frame\}', s, re.S)
    linhas, ausentes = [], []
    for fr in frames:
        if '\\begin{columns}' not in fr:
            continue
        # ⚠ \begin{frame}{titulo}{subtitulo} e' sintaxe valida (§5.4 armadilha 3). Colar os
        # dois da uma string que nao existe no PDF ("ObrigadoAcknowledgements") e a pagina
        # deixa de ser localizavel. So' o PRIMEIRO grupo e' o titulo.
        cab = fr.split('\n')[0]
        tit = re.search(r'\\begin\{frame\}(?:\[[^\]]*\])?\{(.+?)\}(?:\{|\s*$)', cab)
        tit = tit.group(1) if tit else '(sem titulo)'
        tit_busca = re.sub(r'\\[a-zA-Z]+|[{}\\]', '', tit).strip()

        pgs = [i for i, t in txt.items() if tit_busca[:34] in t]
        if not pgs:
            # ⚠ NAO cair para "procura em todas as paginas": isso transforma qualquer
            # palavra comum num `ok` sem valor. Declarar o alcance vale mais que um verde.
            linhas.append((tit_busca[:40], '(pagina nao localizada)', 0, None))
            continue
        for col in re.findall(r'\\begin\{column\}\{[^}]*\}(.*?)\\end\{column\}', fr, re.S):
            p = ultima_palavra(col)
            if not p:
                continue
            ok = any(p in txt[i] for i in pgs)
            linhas.append((tit_busca[:40], p, pgs[0] if pgs else 0, ok))
            if ok is False:
                ausentes.append((tit_busca, p, pgs))

    print(f"{len(linhas)} colunas testadas em "
          f"{len({l[0] for l in linhas})} frames com `columns`\n")
    for t, p, pg, ok in linhas:
        marca = '?  ' if ok is None else ('ok ' if ok else '🛑 ')
        print(f"  {marca} p{pg:<4d} {t:42s} ultima palavra: {p!r}")

    # ---- segundo teste: os botoes do indice B0 chegam a' pagina? ----
    # Um botao que nao renderiza e' um link morto DURANTE a arguicao, e o `Overfull`
    # nao o ve (o indice e' um `columns`). Descoberto ao acrescentar o V19 ao indice.
    i = s.find('Se a pergunta for uma destas')
    if i >= 0:
        fr_idx = s[i:s.find('\\end{frame}', i)]
        rot = re.findall(r'\\beamerbutton\{([^}]+)\}', fr_idx)
        pg_idx = [k for k, t in txt.items() if 'Se a pergunta for uma destas' in t]
        if pg_idx and rot:
            falta = [r for r in rot if r not in txt[pg_idx[0]]]
            print(f"\n{len(rot)} botoes no indice B0 (p{pg_idx[0]}) · "
                  f"{len(rot) - len(falta)} na pagina")
            if falta:
                print(f"   🛑 nao renderizam: {falta}")
                ausentes.append(('indice B0', ', '.join(falta), pg_idx))

    if ausentes:
        print(f"\n🛑 {len(ausentes)} coluna(s) cuja ultima palavra NAO esta na pagina:")
        for t, p, pgs in ausentes:
            print(f"   {t} -> {p!r} (procurado nas paginas {pgs})")
        return 1
    print("\n✅ nenhuma coluna perdeu a cauda.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
