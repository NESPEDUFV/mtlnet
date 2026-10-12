#!/usr/bin/env python3
"""Diff fala-a-fala entre slides/main.tex (% FALA) e SLIDES.md (Fala (PT)).

A terceira superficie onde um texto pode morrer em silencio: nao por estar errado
em algum dos dois, mas por existir SO' EM UM. Descoberta 26/08, quando a ressalva
de vazamento do slide 24 existia so' no .tex -- uma regeracao do SPEECH a teria
apagado da boca do autor.

Uso:  python3 diff_fala.py [--full]
"""
import re, sys, difflib, unicodedata

TEX, MD, CORTE_SERIE_B = 'slides/main.tex', 'SLIDES.md', 1837
PARA = re.compile(r'^%\s*(NOTA\b|\d{4}-\d{2}-\d{2}\s*·|\[BLOCO|⚠|====|-----|Ordem fixa|Moldura|FALA \(divisor\))')
PONTE = re.compile(r'^\s*(\{|\}|\\specialframe|\\subsection\b.*|\\section\b.*)?\s*$')
ALIAS = {  # titulo do frame -> titulo do bloco, quando divergem por desenho
    'The protocol, in four steps': None,   # 4 overlays: resolvidos por ordem
}

def sem_acento(t):
    """Compara IGNORANDO acento e apostrofo-por-acento. Alguns blocos % FALA do .tex
    foram escritos em ASCII ("nao", "e'", "estatica") e o SLIDES.md tem a forma acentuada.
    E' o MESMO texto; contar isso como divergencia afoga as divergencias reais em ruido."""
    t = t.replace("e' ", "e ").replace("a' ", "a ")
    return ''.join(c for c in unicodedata.normalize('NFD', t.lower())
                   if unicodedata.category(c) != 'Mn')


def norm(t):
    t = re.sub(r'\*\*|`|\\textbf\{|\\alert\{|\\emph\{|\\textit\{|[{}]', ' ', t)
    t = re.sub(r'^["“]|["”]$', '', t.strip())
    return re.sub(r'\s+', ' ', t).strip()

def falas_do_tex():
    src = open(TEX, encoding='utf-8').read().split('\n')[:CORTE_SERIE_B]
    out, i = [], 0
    while i < len(src):
        if re.match(r'^%\s*FALA', src[i]):
            buf, j = [re.sub(r'^%\s*FALA[^:]*:\s*', '', src[i])], i + 1
            while j < len(src) and src[j].lstrip().startswith('%') and not PARA.match(src[j].strip()):
                buf.append(src[j].lstrip()[1:].strip()); j += 1
            k, tit = j, None
            while k < len(src):
                l = src[k]
                if l.lstrip().startswith('%') or PONTE.match(l): k += 1; continue
                m = re.match(r'\s*\\begin\{frame\}(?:\[[^\]]*\])?\{(.*?)\}', l)
                tit = m.group(1) if m else ('(specialframe)' if re.match(r'\s*\\begin\{frame\}\s*$', l) else None)
                break
            out.append((i + 1, tit, norm(' '.join(buf)), k + 1))   # k+1 = linha do frame dono
            i = j
        else:
            i += 1
    return out

def blocos_do_md():
    t = open(MD, encoding='utf-8').read()
    t = t[:t.rfind('\n# Blocos REMOVIDOS')]
    out = []
    for m in re.finditer(r'\n### (S\d+[a-z]?) · (.+?)\n(.*?)(?=\n### |\n# |\Z)', t, re.S):
        if m.group(1).startswith('SB'): continue
        f = re.search(r'\*\*Fala \(PT\):?\*\*(.*?)(?=\n- \*\*|\Z)', m.group(3), re.S)
        out.append((m.group(1), m.group(2).strip(), norm(f.group(1)) if f else ''))
    return out

divisores = []


def main():
    tex, md = falas_do_tex(), blocos_do_md()
    # ⚠ uma fala de DIVISOR DE SECAO nao tem frame proprio: ela precede o frame seguinte
    # mas nao pertence a ele. Se duas falas caem no mesmo frame, so' a ULTIMA e' dele.
    vistos, filtrado = set(), []
    for ln, tit, fala, fr in reversed(tex):
        if fr in vistos:                     # ⚠ mesmo FRAME, nao mesmo titulo: overlays
            divisores.append((ln, tit, fala)); continue
        vistos.add(fr); filtrado.append((ln, tit, fala))
    tex = list(reversed(filtrado))
    por_tit = {}
    for cod, tit, fala in md: por_tit.setdefault(tit, []).append((cod, fala))
    usados, div, sem_par, so_acento = {}, [], [], []
    for ln, tit, fala in tex:
        cands = por_tit.get(tit, [])
        k = usados.get(tit, 0)
        if k >= len(cands): sem_par.append((ln, tit, fala)); continue
        cod, fmd = cands[k]; usados[tit] = k + 1
        if fala == fmd: continue
        if sem_acento(fala) == sem_acento(fmd):
            so_acento.append((cod, tit, ln)); continue
        r = difflib.SequenceMatcher(None, fala.split(), fmd.split()).ratio()
        div.append((r, cod, tit, ln, fala, fmd))
    div.sort()
    print(f"{len(tex)} falas de frame no .tex · {len(md)} blocos no SLIDES.md · "
          f"{len(div)} divergem · {len(so_acento)} so' no acento · "
          f"{len(sem_par)} sem par · {len(divisores)} divisores\n")
    for r, cod, tit, ln, a, b in div:
        print(f"── {cod} · {tit[:52]}   (L{ln}, similaridade {r:.2f})")
        sm = difflib.SequenceMatcher(None, b.split(), a.split())
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal': continue
            so = ' '.join(b.split()[i1:i2]); st = ' '.join(a.split()[j1:j2])
            if so: print(f"     só no SLIDES.md: {so[:96]}")
            if st: print(f"     só no .tex     : {st[:96]}")
        print()
    if so_acento:
        print("identicas a menos de acento (o .tex esta em ASCII; higiene, nao defeito):")
        for cod, tit, ln in so_acento: print(f"   {cod:<5} L{ln:<5} {tit[:52]}")
        print()
    if sem_par:
        print("falas do .tex sem bloco correspondente:")
        for ln, tit, _ in sem_par: print(f"   L{ln:<5} {str(tit)[:56]}")

main()
