#!/usr/bin/env python3
"""Emite SPEECH.md e SPEECH.tex a partir dos blocos extraidos por gen_speech.py."""
import json, re, sys

B = json.load(open('/tmp/_speech_blocos.json'))

# ⚠ A chave e' o nome da \section DO DECK, nao uma faixa de codigo do SLIDES.md.
# Faixa de codigo nao acompanha fronteira de secao: em 26/08 o `S5b` (Fundamentos) caia
# em ABERTURA e o `S49` (Conclusao) caia em Check2HGI, porque as faixas foram escritas
# quando a numeracao era outra. A secao e' propriedade do deck; o extrator a le' de la'.
SECOES = [
    ('Introdução', 'ABERTURA — a pergunta e o escopo', 5),
    ('Fundamentos', 'FUNDAMENTOS — dito uma vez', 6),
    ('MTLnet', 'MTLnet — Cap. 3 (CBIC)', 5.5),
    ('ST-MTLNet', 'ST-MTLNet — Cap. 4 (CoUrb)', 6),
    ('Check2HGI', 'Check2HGI — Cap. 5 (MobiWac)', 20),
    ('Conclusão', 'CONCLUSÃO — a resposta condicional', 5.5),
]


def _n(code):
    """S5 -> 5.0 ; S5b -> 5.1 (o sufixo ordena logo apos o numero, sem colidir)."""
    m = re.match(r"S(\d+)([a-z]?)", code)
    return int(m.group(1)) + (ord(m.group(2)) - 96) / 100 if m.group(2) else float(m.group(1))


def mmss(s):
    return '%d:%02d' % (s // 60, s % 60)


def numeros_da_fala(f):
    """So' numeros que sao RESULTADO: com separador decimal, ou seguidos de 'por cento'/'pp'.
    Inteiro nu (Secao 5, Capitulo 3) e' referencia, nao resultado, e polui.
    Recorta por TOKEN, nunca por caractere, para nao partir palavra ao meio."""
    f = re.sub(r'\*\*', '', f)
    toks = f.split()
    alvo = re.compile(r'^\(?\d+[,\.]\d+\)?[,;:\.]?$')
    pct = re.compile(r'^\d+$')
    out, vistos, usados = [], set(), set()
    for i, t in enumerate(toks):
        eh = bool(alvo.match(t)) or (pct.match(t) and i + 1 < len(toks)
                                     and toks[i + 1].lower().startswith(('por', 'pp')))
        if not eh or i in usados:
            continue
        ini, fim = max(0, i - 4), min(len(toks), i + 4)
        for k in range(ini, fim):
            usados.add(k)
        frag = ' '.join(toks[ini:fim]).strip(' ,;:.')
        k = frag.lower()
        if k not in vistos and len(frag) > 6:
            vistos.add(k); out.append(frag)
    return out[:4]


def limpa(s):
    return re.sub(r'\s+', ' ', s).strip()


def dizer_util(lst):
    """so' o que nao pode sair errado: superficie longa, ou trecho com numero."""
    out = []
    for x in lst:
        if len(x) >= 14 or re.search(r'\d', x):
            out.append(x)
    if not out:
        out = [x for x in lst if len(x) >= 6]
    return out[:6]


def fala_limpa(f):
    f = re.sub(r'^["“]|["”]$', '', f.strip())
    return f



def _relogio(B):
    """(palavras, mm:ss medido a 140 ppm) -- COMPUTADO, nunca digitado.

    ⚠ Este numero ja' esteve escrito a mao no cabecalho, e em 26/08 dizia 8.840 palavras
    e ~63 min quando o real era 7.566 e 54:03. Um roteiro que anuncia 13 min de estouro
    quando ha' 4 faz o autor cortar o que nao precisa -- e o que sai primeiro sao as
    ressalvas. E' a mesma doenca do numero de slide na tela e do `Slide impresso:`
    defasado: um derivado escrito a mao nao sabe que ficou velho.
    """
    w = sum(len(b['fala'].split()) for b in B)
    seg = round(w / 140 * 60)
    return w, '%d:%02d' % (seg // 60, seg % 60)

def sec_de(b):
    """Nome de exibicao da secao de um bloco. Recebe o BLOCO, nao o codigo."""
    real = b.get('secao') if isinstance(b, dict) else None
    for chave, nome, _ in SECOES:
        if real == chave:
            return nome
    return SECOES[0][1]


# ─────────────────────────── MARKDOWN ───────────────────────────
def emit_md():
    L = []
    tot = B[-1]['acum']
    L.append('# SPEECH.md — o que dizer, slide a slide\n')
    L.append('> **Defesa · sexta, 28/08/2026, 10:00 · remota (Google Meet).** Gerado do '
             '`SLIDES.md`, que é a fonte da fala. **Nada aqui é novo**: é o mesmo texto, '
             'reorganizado para ser lido de relance em vez de lido inteiro.\n')
    L.append('> **Como usar.** Cada cartão tem quatro camadas, em ordem de urgência: '
             '**ABRE** (a primeira oração, para pegar o fio sem ler), **DIZER** (as superfícies '
             'de lei e os números que não podem sair errado), **NUNCA** (o que anula o slide se '
             'escapar), e a fala completa embaixo, para consulta.\n')
    _w, _t = _relogio(B)
    L.append('> ⚠ **O relógio.** A fala escrita tem **%s palavras**, que a 140 palavras/minuto '
             'dão **%s**, contra o teto de **50 min** do Art. 23. Os campos `Tempo:` dos cartões '
             'somam **%s** e são orçamento, não medição — se os dois discordarem, o medido vale. '
             '**Cronometre o fim de cada seção.**\n'
             % ('{:,}'.format(_w).replace(',', '.'), _t, mmss(tot)))
    L.append('\n---\n')

    # sumario por secao
    L.append('## Marcas de tempo — leve estas seis\n')
    L.append('| seção | slides | fim previsto | **seu tempo real** |')
    L.append('|---|---|---:|---|')
    for c, nome, mins in SECOES:
        grp = [b for b in B if sec_de(b) == nome]
        if not grp:            # secao sem bloco: nao inventa linha
            continue
        # ⚠ primeiro/ultimo por POSICAO na apresentacao, nao por numero de codigo.
        # Depois da AUT-22 o DGI (S19) vem ANTES do MTLnet (S18): ordenar por codigo
        # rotularia a secao como "S18-S25" quando ela comeca no S19.
        prim, último = grp[0], grp[-1]
        L.append('| **%s** | %s–%s | %s | ____________ |' % (nome, prim['code'], último['code'], mmss(último['acum'])))
    L.append('')
    L.append('\n---\n')

    sec_atual = None
    for b in B:
        s = sec_de(b)
        if s != sec_atual:
            sec_atual = s
            L.append('\n\n# %s\n' % s)
        loc = []
        if b['num']:
            loc.append('slide **%s**' % b['num'])
        if b['pdf']:
            loc.append('PDF p.%s' % b['pdf'])
        if not loc:
            # sem referencia de pagina: \specialframe (texto no corpo, sem \frametitle) ou bloco
            # cujo titulo nao casa com frame nenhum. O cartao vale; a crase vazia le como defeito.
            loc.append('sem página')
        L.append('\n## %s · %s' % (b['code'], b['title']))
        L.append('`%s` · **%s** · fim previsto **%s**\n' % (' · '.join(loc), b['tempo'], mmss(b['acum'])))
        if b['abre']:
            L.append('> ### ▶ %s' % b['abre'])
        d = dizer_util(b['dizer'])
        if d:
            L.append('\n**● DIZER EXATO**')
            for x in d:
                L.append('- %s' % x)
        elif b['ledger']:
            L.append('\n**● COBRE** — %s' % re.sub(r'\*\*|`', '', b['ledger'])[:230])
        nums = numeros_da_fala(b['fala'])
        if nums:
            L.append('\n**# NÚMEROS** — %s' % ' · '.join(nums))
        if b['nunca_l']:
            L.append('\n**✕ NUNCA** — %s' % ' · '.join(b['nunca_l']))
        L.append('\n<sub>%s</sub>\n' % fala_limpa(b['fala']))
        L.append('---')
    open('SPEECH.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('SPEECH.md escrito (%d cartões)' % len(B))


# ─────────────────────────── LATEX ───────────────────────────
def tex_esc(s):
    for a, c in (('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'), ('$', r'\$'),
                 ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}')):
        s = s.replace(a, c)
    s = s.replace('“', '``').replace('”', "''").replace('—', '---').replace('·', r'$\cdot$')
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    return s


def emit_tex():
    tot = B[-1]['acum']
    P = [r'''\documentclass[11pt,a4paper]{article}
\usepackage{fontspec}
\usepackage[margin=15mm,top=13mm,bottom=13mm]{geometry}
\usepackage{xcolor}
\usepackage{tcolorbox}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage[brazilian]{babel}
\tcbuselibrary{breakable}
\definecolor{teal}{HTML}{1C7A72}
\definecolor{crim}{HTML}{A83455}
\definecolor{ink}{HTML}{131C1A}
\definecolor{soft}{HTML}{5B6B68}
\definecolor{band}{HTML}{EAF2F0}
\renewcommand{\familydefault}{\sfdefault}
\setlength{\parindent}{0pt}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\fancyhead[L]{\small\color{soft}SPEECH — defesa 28/08/2026}
\fancyhead[R]{\small\color{soft}\thepage}
\begin{document}
\begin{center}
{\Huge\bfseries\color{teal} O que dizer, slide a slide}\\[3mm]
{\large Defesa de Mestrado \textbf{28/08/2026, 10:00} --- remota (Google Meet)}
\end{center}
\vspace{3mm}
\begin{tcolorbox}[colback=band,colframe=teal,boxrule=0.8pt,arc=2pt]
\textbf{Como usar.} Cada cartão tem quatro camadas, em ordem de urgência:
\textbf{\textcolor{teal}{ABRE}} (a primeira oração, para pegar o fio sem ler),
\textbf{\textcolor{teal}{DIZER}} (as superfícies de lei e os números que não podem sair errado),
\textbf{\textcolor{crim}{NUNCA}} (o que anula o slide se escapar), e a fala completa embaixo.
\textbf{Nada aqui é novo} --- é o texto do \texttt{SLIDES.md}, reorganizado para ser lido de relance.
\smallskip

\textbf{\textcolor{crim}{O relógio.}} A fala escrita tem \textbf{''' + '{:,}'.format(_relogio(B)[0]).replace(',', '.') + r''' palavras},
que a 140 palavras/minuto dão \textbf{''' + _relogio(B)[1] + r'''}, contra o teto de \textbf{50 min} do Art.~23.
Os campos \texttt{Tempo:} somam ''' + mmss(tot) + r''' e são orçamento, não medição: se discordarem, o medido vale.
\textbf{Cronometre o fim de cada seção} e anote na tabela abaixo.
\end{tcolorbox}
\vspace{4mm}

{\large\bfseries\color{teal} Marcas de tempo --- leve estas seis}
\vspace{2mm}

\begin{tabular}{@{}p{62mm} p{22mm} r p{34mm}@{}}
\hline
\textbf{seção} & \textbf{slides} & \textbf{previsto} & \textbf{seu tempo real} \\
\hline
''']
    for c, nome, mins in SECOES:
        grp = [b for b in B if sec_de(b) == nome]
        if not grp:
            continue
        prim, ult = grp[0], grp[-1]      # ⚠ por POSICAO, nao por codigo -- ver a nota acima
        P.append(r'\textbf{%s} & %s--%s & %s & \rule{32mm}{0.4pt} \\' %
                 (tex_esc(nome), prim['code'], ult['code'], mmss(ult['acum'])))
    P.append(r'''\hline
\end{tabular}
\clearpage
''')

    sec_atual = None
    for b in B:
        s = sec_de(b)
        if s != sec_atual:
            sec_atual = s
            P.append(r'\vspace{2mm}{\LARGE\bfseries\color{teal} %s}\par\vspace{2mm}' % tex_esc(s))
        loc = []
        if b['num']:
            loc.append(r'slide \textbf{%s}' % b['num'])
        if b['pdf']:
            loc.append('PDF p.%s' % b['pdf'])
        if not loc:
            # sem referencia de pagina: \specialframe (texto no corpo, sem \frametitle) ou bloco
            # cujo titulo nao casa com frame nenhum. O cartao vale; a crase vazia le como defeito.
            loc.append('sem página')
        P.append(r'\begin{tcolorbox}[breakable,colback=white,colframe=teal!55,boxrule=0.6pt,arc=2pt,'
                 r'left=3mm,right=3mm,top=2mm,bottom=2mm]')
        P.append(r'{\small\color{soft}\textbf{%s} $\cdot$ %s $\cdot$ %s $\cdot$ fim previsto \textbf{%s}}\par\vspace{1mm}'
                 % (b['code'], ' $\\cdot$ '.join(loc), tex_esc(b['tempo']), mmss(b['acum'])))
        P.append(r'{\large\bfseries\color{ink} %s}\par\vspace{2mm}' % tex_esc(b['title']))
        if b['abre']:
            P.append(r'{\color{teal}\textbf{\textrightarrow}}\ \textbf{\itshape %s}\par\vspace{1.5mm}' % tex_esc(b['abre']))
        d = dizer_util(b['dizer'])
        if d:
            P.append(r'{\small\color{teal}\textbf{DIZER EXATO}}')
            P.append(r'\begin{itemize}[leftmargin=6mm,itemsep=0.4mm,topsep=0.8mm]')
            for x in d:
                P.append(r'\item %s' % tex_esc(x))
            P.append(r'\end{itemize}')
        elif b['ledger']:
            P.append(r'{\small\color{teal}\textbf{COBRE} --- %s}\par\vspace{1mm}'
                     % tex_esc(re.sub(r'\*\*|`', '', b['ledger'])[:230]))
        nums = numeros_da_fala(b['fala'])
        if nums:
            P.append(r'\vspace{0.5mm}{\small\textbf{N\'UMEROS} --- %s}\par' % ' $\\cdot$ '.join(tex_esc(x) for x in nums))
        if b['nunca_l']:
            P.append(r'\vspace{0.5mm}{\small\color{crim}\textbf{NUNCA} --- %s}\par' %
                     ' $\\cdot$ '.join(tex_esc(x) for x in b['nunca_l']))
        P.append(r'\vspace{1.5mm}{\footnotesize\color{soft} %s\par}' % tex_esc(fala_limpa(b['fala'])))
        P.append(r'\end{tcolorbox}\vspace{2mm}')
    P.append(r'\end{document}')
    open('SPEECH.tex', 'w', encoding='utf-8').write('\n'.join(P) + '\n')
    print('SPEECH.tex escrito')


emit_md()
emit_tex()
