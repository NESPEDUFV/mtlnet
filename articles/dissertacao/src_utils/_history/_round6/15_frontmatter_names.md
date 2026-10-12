# 15_frontmatter_names.md — the example-derived names in the front matter: measured, and absent

**The audit item:** remove names carried over from the exemplar dissertations that this document's
skeleton was derived from.

**Measured 2026-07-28.** Swept `src/0_main.tex` and `src/abntex2-UFV.sty` for every exemplar author
name (Germano, Canesche, Viegas, Passe, lapsusvgi), for generic placeholder names, and for any
hardcoded person or committee string in the class macros.

## What is actually in the front matter

| Field | Value | Verdict |
|---|---|---|
| `\titulo` | the selected title, author ruling 2026-07-24 | real |
| `\autor` | Vitor Hugo Oliveira Silva | real |
| `\orientador` | Fabrício Aguiar Silva | real |
| `\instituicao` | Universidade Federal de Viçosa | real |
| `\campus` | Campus Florestal | real, set 2026-07-27 on the author's word |
| `\curso` | Pós-graduação em Ciência da Computação | real |
| `\local` | Florestal - Minas Gerais | real |
| `\data` | 2026 | real |
| `\membrobancaA` | `[Banca member 1 --- pending advisor conversation]` | **honest placeholder** |
| `\membrobancaB` | `[Banca member 2 --- pending advisor conversation]` | **honest placeholder** |
| `\databanca` | `[defense date --- pending]` | **honest placeholder** |
| `\preambulo` | the Magister Scientiae formula | real |

**No exemplar-derived name exists anywhere in the front matter or the style file.** The two exemplar
mentions in `0_main.tex` are in a *comment* at lines 65-66, recording which citation style each
exemplar uses as precedent for a formatting decision. That is provenance, not content, and it does not
render.

The three bracketed fields are the right state for a document whose committee is not yet formed. They
are visibly placeholders in the rendered PDF, which is what makes them safe: nothing invented is
presented as fact. The audit item was presumably written against an earlier tree, or against the
possibility rather than the file.

**Verdict: nothing to remove.** The item is closed as already-clean, not as done.

One adjacent finding worth the author's attention, since it is the kind of thing that surfaces only
when someone reads these lines: `\campus{Campus Florestal}` is consumed by `\imprimircampus` in
`abntex2-UFV.sty:49`, which is called only inside `\imprimircapa` — and **neither build calls
`\imprimircapa` today**. So the campus renders nowhere. The existing comment at `0_main.tex:139-141`
already records this. It is correct as a data field and it will start rendering if a cover page is
added; it is simply not visible now. No action unless the author wants the cover page.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-28 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
