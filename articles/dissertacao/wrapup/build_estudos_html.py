#!/usr/bin/env python3
"""Gera ESTUDOS_DEFESA.html a partir de ESTUDOS_DEFESA.md.

O Markdown e' o documento canonico (renderiza nativo no app do GitHub, no celular).
Este script produz um HTML autocontido para leitura no navegador, com Mermaid,
KaTeX, destaque de sintaxe, indice lateral e tema claro/escuro.

    python3 build_estudos_html.py

Reexecutar depois de qualquer edicao no .md. Nao editar o .html a mao.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "ESTUDOS_DEFESA.md"
DST = HERE / "ESTUDOS_DEFESA.html"

TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Estudos para a Defesa — guia didático</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/styles/github-dark.min.css">
<style>
  :root {{
    --bg:#ffffff; --fg:#1f2328; --muted:#59636e; --line:#d1d9e0;
    --accent:#0969da; --code-bg:#f6f8fa; --quote:#f0f6ff; --warn:#fff8c5;
    --table-alt:#f6f8fa; --shadow:0 1px 3px rgba(0,0,0,.08);
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --bg:#0d1117; --fg:#e6edf3; --muted:#9198a1; --line:#30363d;
      --accent:#4493f8; --code-bg:#161b22; --quote:#121d2f; --warn:#272115;
      --table-alt:#161b22; --shadow:0 1px 3px rgba(0,0,0,.4);
    }}
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{
    margin:0; background:var(--bg); color:var(--fg);
    font:16px/1.68 -apple-system,BlinkMacSystemFont,"Segoe UI",
         "Noto Sans",Helvetica,Arial,sans-serif;
    -webkit-text-size-adjust:100%;
  }}
  #wrap {{ max-width:900px; margin:0 auto; padding:24px 20px 120px; }}
  h1,h2,h3,h4 {{ line-height:1.28; margin:1.9em 0 .6em; font-weight:650; }}
  h1 {{ font-size:1.95em; margin-top:.3em; }}
  h2 {{ font-size:1.5em; padding-bottom:.3em; border-bottom:1px solid var(--line); }}
  h3 {{ font-size:1.2em; }}
  h4 {{ font-size:1.03em; color:var(--muted); }}
  a {{ color:var(--accent); text-decoration:none; }}
  a:hover {{ text-decoration:underline; }}
  hr {{ border:0; border-top:1px solid var(--line); margin:2.6em 0; }}
  blockquote {{
    margin:1.1em 0; padding:.7em 1.1em; border-left:4px solid var(--accent);
    background:var(--quote); border-radius:0 6px 6px 0;
  }}
  blockquote p:first-child {{ margin-top:0; }}
  blockquote p:last-child {{ margin-bottom:0; }}
  code {{
    background:var(--code-bg); border-radius:5px; padding:.16em .38em;
    font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
    font-size:.875em;
  }}
  pre {{
    background:var(--code-bg); border:1px solid var(--line); border-radius:8px;
    padding:14px 16px; overflow-x:auto; -webkit-overflow-scrolling:touch;
    font-size:.83em; line-height:1.5;
  }}
  pre code {{ background:none; padding:0; font-size:1em; }}
  table {{
    border-collapse:collapse; width:100%; margin:1.2em 0;
    display:block; overflow-x:auto; font-size:.93em;
  }}
  th,td {{ border:1px solid var(--line); padding:7px 11px; text-align:left; vertical-align:top; }}
  th {{ background:var(--table-alt); font-weight:640; }}
  tbody tr:nth-child(even) {{ background:var(--table-alt); }}
  .mermaid {{
    text-align:center; margin:1.5em 0; padding:14px; background:var(--code-bg);
    border:1px solid var(--line); border-radius:8px; overflow-x:auto;
  }}
  sub {{ color:var(--muted); }}
  #top {{
    position:fixed; right:16px; bottom:16px; z-index:50;
    background:var(--accent); color:#fff; border:none; border-radius:50%;
    width:46px; height:46px; font-size:19px; cursor:pointer; box-shadow:var(--shadow);
    opacity:0; pointer-events:none; transition:opacity .2s;
  }}
  #top.on {{ opacity:.92; pointer-events:auto; }}
  .katex {{ font-size:1.03em; }}
  .katex-display {{ overflow-x:auto; overflow-y:hidden; padding:.35em 0; }}
</style>
</head>
<body>
<div id="wrap"><div id="doc">carregando…</div></div>
<button id="top" title="Voltar ao topo">↑</button>

<script id="md" type="text/markdown">{md}</script>
<script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/highlight.js@11.9.0/lib/common.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs';

  const src = document.getElementById('md').textContent;

  // 1. Proteger a matematica do parser de Markdown (o '_' viraria italico).
  const math = [];
  const guarded = src
    .replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, (_, t) => `@@M${{math.push(['block', t]) - 1}}@@`)
    .replace(/(?<![\\\\$])\\$([^$\\n]+?)\\$(?!\\$)/g, (_, t) => `@@M${{math.push(['inline', t]) - 1}}@@`);

  // 2. Markdown -> HTML, com ancoras no estilo do GitHub para os links internos.
  const slug = s => s.toLowerCase().trim()
    .replace(/[\\u0300-\\u036f]/g, '')
    .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
    .replace(/[^\\w\\s-]/g, '').replace(/\\s+/g, '-');
  const renderer = new marked.Renderer();
  renderer.heading = (text, lvl) => {{
    const id = slug(text.replace(/<[^>]+>/g, ''));
    return `<h${{lvl}} id="${{id}}">${{text}}</h${{lvl}}>`;
  }};
  marked.setOptions({{ renderer, gfm: true, breaks: false }});
  const doc = document.getElementById('doc');
  doc.innerHTML = marked.parse(guarded);

  // 3. Devolver a matematica, ja renderizada.
  doc.innerHTML = doc.innerHTML.replace(/@@M(\\d+)@@/g, (_, i) => {{
    const [kind, tex] = math[+i];
    try {{
      return katex.renderToString(tex, {{ displayMode: kind === 'block', throwOnError: false }});
    }} catch (e) {{ return tex; }}
  }});

  // 4. Mermaid.
  doc.querySelectorAll('pre > code.language-mermaid').forEach(c => {{
    const d = document.createElement('div');
    d.className = 'mermaid';
    d.textContent = c.textContent;
    c.parentElement.replaceWith(d);
  }});
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  mermaid.initialize({{ startOnLoad: false, theme: dark ? 'dark' : 'default', securityLevel: 'loose' }});
  await mermaid.run({{ querySelector: '.mermaid' }});

  // 5. Destaque de sintaxe.
  doc.querySelectorAll('pre code').forEach(b => {{
    if (!b.className.includes('language-mermaid')) hljs.highlightElement(b);
  }});

  // 6. Botao de voltar ao topo.
  const btn = document.getElementById('top');
  btn.onclick = () => scrollTo({{ top: 0, behavior: 'smooth' }});
  addEventListener('scroll', () => btn.classList.toggle('on', scrollY > 700));

  if (location.hash) document.getElementById(location.hash.slice(1))?.scrollIntoView();
</script>
</body>
</html>
"""


def main() -> None:
    md = SRC.read_text(encoding="utf-8")
    # o unico caractere que quebraria o <script type="text/markdown">
    md = md.replace("</script>", "<\\/script>")
    DST.write_text(TEMPLATE.format(md=md), encoding="utf-8")
    print(f"escrito: {DST}  ({DST.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
