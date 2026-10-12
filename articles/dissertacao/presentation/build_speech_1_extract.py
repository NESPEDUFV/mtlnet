#!/usr/bin/env python3
"""Gera SPEECH.md e SPEECH.tex a partir do SLIDES.md (a fonte da fala) e do PDF construido.

Desenho: NAO e' uma transcricao. A fala media tem ~158 palavras, o que e' ilegivel de
relance. Cada slide vira um CARTAO com quatro camadas, em ordem de urgencia:

    1. ABRE   -- a primeira oracao, para pegar o fio sem ler
    2. DIZER  -- os trechos que o SLIDES.md marca em negrito: sao as superficies de lei
                 e os numeros que nao podem sair errado
    3. NUNCA  -- o campo 'Nunca dizer' do bloco, condensado
    4. a fala completa, em corpo menor, para consulta

Nada e' inventado: tudo sai do bloco correspondente do SLIDES.md.
"""
import re, subprocess, sys, unicodedata

MD = 'SLIDES.md'
TEX = 'slides/main.tex'
PDF = 'slides/main.pdf'


def limpa(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def parse_blocos():
    t = open(MD, encoding='utf-8').read()
    # ⚠ CORTA na secao de blocos removidos. Sem isto o SPEECH imprime cartao de slide que
    # NAO EXISTE -- em 26/08 eram 6 blocos e 774 palavras, e o roteiro dava 59:34 contra os
    # 54:03 reais. A ancora tem de ser em INICIO DE LINHA: a frase tambem aparece no
    # cabecalho do arquivo, e um `find` solto corta o arquivo inteiro no lugar errado.
    corte = re.search(r'(?m)^#\s*Blocos REMOVIDOS', t)
    if corte:
        t = t[:corte.start()]
    out = []
    for m in re.finditer(r'\n### (S\d+[a-z]?) · (.+?)\n(.*?)(?=\n### |\n# |\Z)', t, re.S):
        code, title, body = m.group(1), m.group(2).strip(), m.group(3)
        if code.startswith('SB'):
            continue
        def campo(nome, ate=r'\n- \*\*'):
            mm = re.search(r'\*\*' + nome + r':?\*\*(.*?)(?=' + ate + r'|\Z)', body, re.S)
            return limpa(mm.group(1)) if mm else ''
        tempo = ''
        mt = re.search(r'\*\*Tempo:\*\*\s*([^\n]+)', body)
        if mt:
            tempo = limpa(mt.group(1))
        out.append(dict(code=code, title=title,
                        tempo=tempo,
                        fala=so_a_fala(campo(r'Fala \(PT\)')),
                        nunca=campo(r'Nunca dizer'),
                        ledger=campo(r'LEDGER'),
                        secao=None))
    _guarda_editorial(out)
    return out


# ⚠ GUARDA -- NAO REMOVER. O fallback de `so_a_fala` (campo sem aspas -> campo inteiro)
# e' SILENCIOSO por desenho: um bloco novo, sem aspas, com anotacao, e o bastidor volta
# ao roteiro sem que nada avise. Foi exatamente esse o modo de falha de 26/08, quando 12
# dos 56 blocos levavam "*(v3, 26/08 -- ...)*" para dentro do que o autor le' em voz alta.
# Este guarda troca o vazamento silencioso por um erro de build com o codigo do bloco.
# ⚠ NAO troque isto por uma lista de marcas. O gate usa 19 formas de anotacao e inventou
# 4 delas num unico dia -- enumerar persegue um alvo que ele move sozinho. A invariante e'
# melhor: NENHUMA fala legitima tem crase, porque o autor nao diz caminho de arquivo, nome
# de variavel nem numero de secao em voz alta; mas TODA marca editorial que sobreviva ao
# `so_a_fala` carrega uma (`AUT-19`, `main.tex:759`, `§8.11`). Medido em 0/56 hoje, entao
# nao ha' falso positivo a pagar -- e cobre a marca que ainda nao foi inventada.
# O glifo de status entra ao lado: e' o que ele usa quando esta com pressa e NAO poe crase.
_EDITORIAL = re.compile(r'[`✅🔴🛑⟵⚠]')


def _guarda_editorial(blocos):
    sujos = [(b['code'], _EDITORIAL.search(b['fala']).group(0))
             for b in blocos if b['fala'] and _EDITORIAL.search(b['fala'])]
    if sujos:
        print('ERRO: anotacao editorial dentro da fala -- ela iria impressa no SPEECH.',
              file=sys.stderr)
        for cod, marca in sujos:
            print(f'  {cod}: achei {marca!r} no texto extraido', file=sys.stderr)
        print('\nA fala DEVE vir entre aspas; a anotacao fica fora delas.'
              '\nVer a convencao no cabecalho do SLIDES.md e `so_a_fala` neste arquivo.',
              file=sys.stderr)
        sys.exit(2)



def so_a_fala(campo):
    """A fala e' o que esta ENTRE ASPAS. O resto do campo e' anotacao editorial.

    Descoberto 26/08: 12 dos 56 blocos carregavam marca editorial dentro do campo
    -- um parentetico de versao ANTES da aspa de abertura ("*(v3, 26/08 -- ...)*")
    e uma nota de revisao DEPOIS da de fechamento. O extrator lia o campo inteiro,
    entao o roteiro impresso traria "*(v3, 26/08...)*" no meio do que o autor le'
    em voz alta. 55 dos 56 blocos seguem a convencao das aspas; o unico que nao
    segue e' uma nota de 17 palavras, e para ele o campo inteiro esta certo.
    """
    if not campo:
        return campo
    # 1 · tira o editorial ANTES de procurar as aspas -- uma nota de revisao pode
    #     conter aspas internas, e af o rfind cai dentro dela (caso S51).
    campo = re.sub(r'\*\((?:v\d|20\d\d)[^)]*\)\*', ' ', campo)   # *(v3, 26/08 -- ...)*
    campo = re.split(r'(?:^|\s)[-•]?\s*⚠', campo, maxsplit=1)[0]     # tudo a partir do primeiro ⚠
    i, j = campo.find('"'), campo.rfind('"')
    if i < 0 or j <= i or (j - i) < 40:
        return campo                      # sem aspas: campo inteiro (fallback)
    return campo[i + 1:j].strip().strip('"\u201c\u201d').strip()


def secao_por_frame():
    """titulo do frame -> nome da \\section a que ele pertence, lido do main.tex.

    ⚠ NAO derive secao de faixa de codigo (S1..S8..S17...). Os codigos do SLIDES.md
    nao acompanham as fronteiras de secao do deck: em 26/08 o `S5b` (Fundamentos)
    caia em ABERTURA e o `S49` (Conclusao) caia em Check2HGI, porque as faixas foram
    escritas quando a numeracao era outra. A secao e' propriedade do DECK; leia dela.
    """
    import os
    tex = os.path.join(os.path.dirname(PDF) or '.', 'main.tex')
    if not os.path.exists(tex):
        return {}
    sec, out = None, {}
    for l in open(tex, encoding='utf-8'):
        if l.lstrip().startswith('%'):
            continue
        m = re.match(r'\s*\\section(?:\[(.*?)\])?\{(.*?)\}', l)
        if m:
            sec = m.group(1) or m.group(2)
        f = re.match(r'\s*\\begin\{frame\}(?:\[[^\]]*\])?\{(.*?)\}', l)
        if f and sec:
            out.setdefault(f.group(1), sec)
    return out

def paginas():
    """titulo do frame -> lista de (pagina_pdf, numero_impresso), na ordem do PDF."""
    pgs = subprocess.run(['pdftotext', PDF, '-'], capture_output=True, text=True).stdout.split('\f')
    info = []
    for i, p in enumerate(pgs, 1):
        nums = [int(x) for x in re.findall(r'(?m)^\s*(\d{1,2})\s*$', p)]
        info.append((i, nums[-1] if nums else None, p))
    return info


# titulos que diferem entre o SLIDES.md e o frame construido
ALIAS = {
    'Protocol, step 1 of 4: the unit of data':   '1 · the unit of data',
    'Protocol, step 2 of 4: what is measured':   '2 · what is measured',
    'Protocol, step 3 of 4: what is compared':   '3 · what is compared',
    'Protocol, step 4 of 4: how it is decided':  '4 · how it is decided',
    'Multitask Learning for POI Classification and Prediction Tasks': 'Defesa de Dissertação de Mestrado',
    # A arte da Fig. 2 divide o \frametitle com o frame da pergunta herdada; so' o
    # \framesubtitle a distingue. Depois da AUT-23 ela ficou a tres slides de distancia
    # e GANHOU fala propria -- um cartao sem referencia de pagina, para um slide que o
    # autor agora tem de falar, e' pior do que era quando ele era mudo.
    'Architecture or representation? (a arte)': 'The same MTLnet, with the decomposed input',
}


ALIAS_SEC = {
    'Architecture or representation? (a arte)': 'Architecture or representation?',
    'Protocol, step 1 of 4: the unit of data':  'The protocol, in four steps',
    'Protocol, step 2 of 4: what is measured':  'The protocol, in four steps',
    'Protocol, step 3 of 4: what is compared':  'The protocol, in four steps',
    'Protocol, step 4 of 4: how it is decided': 'The protocol, in four steps',
}


def acha_pagina(title, info, desde):
    title = ALIAS.get(title, title)
    """primeira pagina >= desde cujo texto contem o titulo (normalizado)."""
    alvo = limpa(re.sub(r'[^\w\s]', ' ', title)).lower()[:34]
    for i, num, p in info:
        if i < desde:
            continue
        if alvo and alvo in limpa(re.sub(r'[^\w\s]', ' ', p)).lower():
            return i, num
    return None, None


def segundos(tempo):
    m = re.search(r'([\d,\.]+)\s*(s|min)', tempo)
    if not m:
        return 0
    v = float(m.group(1).replace(',', '.'))
    return int(v * 60 if m.group(2) == 'min' else v)


def mmss(s):
    return '%d:%02d' % (s // 60, s % 60)


def negritos(fala):
    """os trechos que o SLIDES.md marca em negrito na fala = as superficies que nao podem sair errado."""
    b = re.findall(r'\*\*(.+?)\*\*', fala)
    vistos, out = set(), []
    for x in b:
        x = limpa(x).strip(' .,;:')
        k = x.lower()
        if len(x) > 3 and k not in vistos:
            vistos.add(k)
            out.append(x)
    return out


def abre(fala):
    f = re.sub(r'^["“]', '', fala.strip())
    f = re.sub(r'\*\*', '', f)
    m = re.match(r'(.{0,180}?[\.\?!])(\s|$)', f)
    out = limpa(m.group(1)) if m else limpa(f[:170]) + '…'
    if len(out) < 45:                      # parou cedo demais: pega a oracao seguinte tambem
        m2 = re.match(r'(.{0,220}?[\.\?!])(\s|$)', f[len(out):].strip())
        if m2:
            out = out + ' ' + limpa(m2.group(1))
    return out


def nunca_curto(n):
    n = re.sub(r'⚠.*$', '', n)
    n = re.sub(r'\*\*|\*|`', '', n)
    partes = [limpa(x) for x in re.split(r'(?<=[\.;])\s+', n) if len(limpa(x)) > 3]
    return partes[:4]


def main():
    blocos = parse_blocos()
    info = paginas()
    secs = secao_por_frame()
    cursor, acum = 1, 0
    for b in blocos:
        pg, num = acha_pagina(b['title'], info, cursor)
        if pg:
            cursor = pg + 1
        b['pdf'], b['num'] = pg, num
        b['seg'] = segundos(b['tempo'])
        acum += b['seg']
        b['acum'] = acum
        b['abre'] = abre(b['fala'])
        b['dizer'] = negritos(b['fala'])
        b['nunca_l'] = nunca_curto(b['nunca'])
        b['secao'] = secs.get(ALIAS_SEC.get(b['title'], b['title']))
    # \specialframe nao tem \frametitle, entao nao casa por titulo. A secao dele e' a do
    # bloco anterior -- os blocos estao em ordem de apresentacao, e um divisor nunca abre
    # uma secao (a \section vem antes dele no .tex).
    ultima = None
    for b in blocos:
        if b['secao']:
            ultima = b['secao']
        elif b['code'] != 'S1':
            b['secao'] = ultima
    print("blocos: %d | mapeados a pagina: %d | tempo total declarado: %s"
          % (len(blocos), sum(1 for b in blocos if b['pdf']), mmss(acum)))
    for b in blocos[:6]:
        print("  %-5s pdf p%-4s impresso %-5s %-46s %ss" % (b['code'], b['pdf'], b['num'], b['title'][:46], b['seg']))
    import json
    json.dump(blocos, open('/tmp/_speech_blocos.json', 'w'), ensure_ascii=False)
    return blocos


if __name__ == '__main__':
    main()
