"""Confere REVISAO_BANCA_PDF.md contra o PDF por um caminho independente:
   texto via pdftotext (poppler) e anotacoes via pypdf — nao PyMuPDF, que gerou o doc."""
import os, re, subprocess, unicodedata, sys
from pypdf import PdfReader

PDF="/Users/vitor/Downloads/dissertacao - vitor hugo (1).pdf"
MD=os.path.join(os.path.dirname(os.path.abspath(__file__)), "REVISAO_BANCA_PDF.md")

pages={pg: subprocess.run(["pdftotext","-f",str(pg),"-l",str(pg),"-enc","UTF-8",PDF,"-"],
                          capture_output=True,text=True).stdout for pg in range(1,120)}
def norm(s):
    s=unicodedata.normalize("NFKD",s)
    s="".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]","",s.lower())

FULL=norm("".join(pages.values()))
r=PdfReader(PDF)
annots=[]
for i,p in enumerate(r.pages,1):
    for a in (p.get("/Annots") or []):
        o=a.get_object()
        if o.get("/Subtype")=="/Highlight":
            annots.append((i,(o.get("/Contents") or "").strip().replace("\r\n","\n").replace("\r","\n")))

md=open(MD).read()
parts=re.split(r"\n### (B-\d\d)\n", md)
items={}
for k in range(1,len(parts),2):
    bid, body = parts[k], parts[k+1].split("\n---\n")[0]
    m=re.match(r"\*\*Página (\d+) · (.+?) · 26/08 (\d\d:\d\d)\*\*", body.strip())
    unq=lambda t: None if t is None else "\n".join(re.sub(r"^> ?","",l) for l in t.split("\n")).strip()
    def grab(label,nxt):
        mm=re.search(re.escape(label)+r".*?\n\n(.*?)\n\n(?="+nxt+")", body, re.S)
        return unq(mm.group(1)) if mm else None
    # O comentário do revisor termina onde começa o bloco **Parecer** (acrescentado 2026-09-02).
    # Sem este limite, o parecer entra na captura e a comparação com o /Contents do PDF -- que é a
    # razão de ser deste verificador -- passa a falhar em todos os itens comentados.
    cm=re.search(r"\*\*Comentário do revisor\*\*\n\n(.*?)(?=\n\n\*\*Parecer\*\*|$)", body, re.S)
    comment="" if "nenhum: o revisor grifou" in body else unq(cm.group(1)) if cm else None
    items[bid]=dict(page=int(m.group(1)), sec=m.group(2), time=m.group(3),
                    quote=grab("**Trecho destacado**", r"\*\*Contexto"),
                    ctx=grab("**Contexto**", r"\*\*Comentário"), comment=comment)
idx=re.findall(r"^\| \[(B-\d\d)\]\(#b-\d\d\) \| (\S) \| (\d+) \| ([^|]+?) \|", md, re.M)

# A legenda, lida do próprio documento: cada linha `| `X` | descrição |` da tabela de estados.
LEGENDA = set(re.findall(r"^\| `(\S)` \|", md, re.M))

fails=[]
chk=lambda c,m: None if c else fails.append(m)

# 1 · nada pulado
chk(len(annots)==27, "pypdf achou %d highlights (esperado 27)"%len(annots))
chk(len(items)==27, "MD tem %d itens"%len(items))
chk(len(idx)==27, "índice tem %d linhas"%len(idx))
ids=sorted(items)
chk(ids==["B-%02d"%i for i in range(1,28)], "IDs não são B-01..B-27 contíguos")

OQ={"B-19","B-27"}                       # trecho com nota "[legenda completa...]"
OC={"B-06","B-07","B-08","B-10"}         # contexto = texto literal entre «» + nota de enquadramento
for n,bid in enumerate(ids):
    it=items[bid]; apage,acom=annots[n]
    # 2 · página e comentário batem com a anotação do PDF
    chk(it["page"]==apage, "%s: página %s no MD, %s no PDF"%(bid,it["page"],apage))
    chk(norm(it["comment"] or "")==norm(acom), "%s: comentário difere\n     MD =%r\n     PDF=%r"%(bid,it["comment"],acom))
    # 3 · índice coerente com o item
    iid,st,ipg,isec=idx[n]
    chk(iid==bid, "%s: índice fora de ordem (%s)"%(bid,iid))
    chk(int(ipg)==apage, "%s: página no índice (%s) != %s"%(bid,ipg,apage))
    # Qualquer marca da legenda do ficheiro serve. Exigir '☐' contradizia a instrução do próprio
    # documento ("Marque o status na tabela abaixo"): o verificador falharia no instante em que o
    # autor decidisse o primeiro item. Corrigido 2026-09-02, ao marcar os 27 pela primeira vez.
    #
    # ⚠ E A LEGENDA É LIDA DO FICHEIRO, não fixada aqui. Corrigido 2026-09-08: estava fixada como
    # "☐✔✎✖?", e no instante em que o documento ganhou um símbolo novo (`✅`, para as erratas já
    # aplicadas) o verificador rejeitou seis itens legítimos. Uma cópia de uma lista que vive noutro
    # ficheiro envelhece sozinha, e este script existe precisamente para apanhar esse género de
    # divergência -- não para o produzir. A legenda sai agora das linhas `| \`X\` | ... |` do MD.
    chk(st in LEGENDA, "%s: status %r não está na legenda do próprio documento (%s)"
        %(bid, st, " ".join(sorted(LEGENDA))))
    chk(isec.strip()==it["sec"], "%s: seção no índice != no item"%bid)
    # 4 · trecho destacado existe literalmente na página
    q=re.sub(r"\*\*","",it["quote"]).replace("[legenda completa no contexto abaixo]","").strip()
    chk(norm(q) in norm(pages[apage]), "%s: TRECHO ausente na pág %s: %r"%(bid,apage,q[:80]))
    # 5 · contexto existe literalmente na página (por segmento, entre os cortes […])
    if bid in OC:
        spans=re.findall(r"«([^»]+)»", it["ctx"])
        chk(len(spans)>=2, "%s: contexto de enquadramento sem trechos entre «»"%bid)
        for span in spans:   # titulos de subsecao vivem em outra pagina; conferem contra o documento todo
            chk(norm(span) in FULL, "%s: trecho «» não existe no PDF: %r"%(bid,span[:70]))
        chk(any(norm(sp) in norm(pages[apage]) for sp in spans),
            "%s: nenhum trecho «» está na própria página %s"%(bid,apage))
    else:
        for seg in re.sub(r"\*\*","",it["ctx"]).split("[…]"):
            if len(norm(seg))<20: continue
            chk(norm(seg) in norm(pages[apage]), "%s: CONTEXTO não confere na pág %s: %r"%(bid,apage,seg.strip()[:80]))
        # 6 · o trecho está dentro do contexto e vai em negrito
        if bid not in OQ:
            chk(norm(q) in norm(re.sub(r"\*\*","",it["ctx"])), "%s: trecho fora do seu contexto"%bid)
        chk("**" in it["ctx"], "%s: contexto sem o destaque em negrito"%bid)

# 7 · rótulo de seção existe no sumário do PDF (título completo)
flat=[]
def walk(o):
    for e in o:
        walk(e) if isinstance(e,list) else flat.append(e.title)
walk(r.outline)
for bid,it in items.items():
    key=re.sub(r"^[\d.]+\s*","",re.sub(r"\s*\(.*?\)\s*$","",it["sec"]).split(" · ")[0])
    chk(any(norm(t)==norm(key) for t in flat) or key=="Resumo", "%s: seção %r não bate com o sumário"%(bid,it["sec"]))

print("itens: %d | destaques no PDF: %d | linhas de índice: %d"%(len(items),len(annots),len(idx)))
print("FALHAS: %d"%len(fails))
for f in fails: print(" -",f)
sys.exit(1 if fails else 0)
