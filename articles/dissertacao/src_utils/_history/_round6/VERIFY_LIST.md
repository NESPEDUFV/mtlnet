# VERIFY_LIST.md — the twenty checks worth your own eyes, in order of consequence

**Built 2026-07-28 by the ledger track**, against `4e84cf7a` (108 / 105 / 109 pp; the per-section
chapter split, whose render is byte-identical to `01915ba7`). Companion to
[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md), which carries the full trail; this file is the short list.

**How to read the ordering.** Consequence, not effort. Items 1-6 are things that would mislead the
banca or the advisor if wrong. Items 7-13 are claims a pass verified about **its own work**, where no
fresh eyes have looked. Items 14-20 are traceability and hygiene. Every row gives the phrase to
anchor on, the command or the page, and **what the answer should be if all is well** — so a check
that comes back different is the finding.

**If you only do three, do these:** item 0 (a numeric bound in your submitted paper is false for the
first state it names), item 6 (a frame sentence on p. 23 now contradicts a chapter sentence on
p. 36, and the repair was drafted but never applied) and item 1 (a gate reported green across the
whole round is red, and has been red since before the round started).

> ## FECHADO EM 2026-07-30 — 15 dos 21 itens estao resolvidos; os 6 restantes vivem no PENDENCIAS
>
> **Este arquivo nao e mais uma fila; e o registro de verificacao da rodada 6, fechado.** O autor
> pediu em 2026-07-30 que os pontos ja resolvidos saissem das filas. Aqui eles **nao foram apagados**,
> por dois motivos medidos: (1) `check_verify_list.py` e `check_meta_claims.py` leem este arquivo por
> caminho e executam os blocos de comando dele, entao apagar itens quebraria dois gates; (2) cada
> bloco carrega o *comando* que produziu a verificacao, que e a evidencia — apagar o item apagaria a
> prova junto com a conclusao.
>
> **CORRECAO DESTE PROPRIO CABECALHO, 2026-07-30.** A primeira versao dizia "15 dos **20**" e listava
> "cinco" abertos acima de uma tabela de **seis** linhas. Sao **21** itens numerados (0 a 20): o item
> **10** — as contagens de palavras do Resumo e do Abstract — nao estava em nenhum dos dois grupos,
> apesar de este arquivo dizer, no proprio bloco dele, que os numeros **nao reproduzem**. Exatamente o
> item que o cabecalho deveria destacar foi o que caiu do somatorio.
>
> **Estado, por item, e a soma fecha em 21:** **15 resolvidos** — 0, 1, 2, 3, 6, 7, 8, 9, 11, 12, 13,
> 17, 18, 19, 20 (mais os anexos A1, A2, A4, A5, A6). **6 abertos**, e **nenhum espera trabalho meu**:
> sao decisoes suas, e a fila viva delas e o `PENDENCIAS.md`, nao este arquivo.
>
> | item daqui | onde a decisao vive agora |
> |---|---|
> | 4 (termo fora do registro) | `PENDENCIAS.md` §2.12 |
> | 5 (assimetria do resultado de regiao) | §2.11 |
> | **10 (contagens do Resumo/Abstract, tres instrumentos e tres respostas)** | **§2.19** |
> | 14 (intervalo de paginas do `nash`) | §2.14 |
> | 15 e 16 (citacoes e termo banido em prosa publicada) | §2.15 |
> | A3 (artefatos publicados divergentes) | §2.16 |
>
> (15 + 6 = 21. Os anexos A1-A7 sao contados a parte dos numerados, e A3 aparece na tabela porque a
> decisao dele esta viva; os outros anexos estao entre os resolvidos.)
>
> A7 apontava para §2.13, que foi **arquivado** em 2026-07-30 (o defeito do comando foi corrigido e a
> contagem passou a bater); o ponteiro no bloco dele registra isso em vez de apontar para o vazio.
>
> **Nao adicione item novo aqui.** Achado novo vai para o `PENDENCIAS.md`; este arquivo e historico.

> ## ROUND 8 DISPOSITION, 2026-07-30 — every item worked, none dropped
>
> Read this before the three above: **all three have since been resolved.** Item 0 is fixed in both
> texts, item 6's repair is in the prose (its *command* was the thing that was wrong), and item 1's
> gate exits 0. Each item below now carries a dated block saying what was measured, with the command.
>
> | disposition | items |
> |---|---|
> | **verified as described** | 2, 3, 7, 9, 11, 12, 13, 17, 18, 19 (numbers), 20, A1, A2, A4, A5, A6 |
> | **fixed this round** | 0 (both texts), 1 (gate green), 6 and 6b (and their commands), 8 (closed without the author) |
> | **the item's own command was defective** | 5 (named a deleted file, expectation passed anyway), 6 (comment-blind, failed a landed fix), 17 (superseded by a gate), A3 (asked by-path, claim is by-content), A7 (over-counts by four, always) |
> | **handed to the author** | 4 → §2.12, 5 → §2.11, 14 → §2.14, 15 and 16 → §2.15, A3 → §2.16, A7 → §2.13 **(§2.13 foi arquivado em 2026-07-30: o defeito do comando foi corrigido e a contagem passou a bater; ver `_history/_archive/PENDENCIAS_RESOLVIDOS.md`)** |
> | **still `[NEEDS SIGN-OFF]`, unchanged** | 2, 3, 12, 19, A1 |
>
> **Three things about this file itself are now wrong and are corrected in place**, because a reader
> who trusts a coordinate here is the reader this file exists to protect. The build is **100 / 97 /
> 101 pages, not 108 / 105 / 109** — round 7 moved two appendices into the supplementary volume, so a
> page number past 100 or naming the errata appendix is a pre-round-7 coordinate. Item 10's word
> counts do not reproduce. And several line numbers moved with the files.
>
> **One caution for whoever measures next.** Round 8 ran eight tracks in parallel against this
> checkout. A count taken here is a reading at a timestamp, not a property of the repository: the
> sign-off total moved twice while this file was open (item A7). Where a number could not be pinned,
> the block asserts the *structural* defect and dates the count, rather than pinning a total a
> legitimate edit would break.

---

**0. The `±0.003` gradient-cosine bound is false, in the dissertation AND in the submitted paper.**
`chapters/5_mobiwac/02_related.tex:161` and `articles/[mobiwac]/src/sections/02_related.tex:99`,
both reading "per-dataset means within $\pm0.003$".
```bash
sed -n '29,31p' ../../docs/studies/archive/mtl_improvement/WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md
```
(from the repository root). *If all is well:* the per-state means read FL +0.0007, **AL +0.0032**,
AZ −0.0005, GE −0.0004 — and `0.0032 > 0.003`, so the bound is false for **Alabama, the first state
the sentence names**. The round rescoped this sentence's pool from three datasets to four and carried
the bound over unchanged; the bound is right only against the superseded two-run figures (AL
+0.0026). The pooled `+0.001` is correct and the orthogonality conclusion is untouched — this is a
false bound, not a false finding. It is first on the list because it is in a manuscript under review
and it needs the two-file change plus the `ERRATA.md` line. Raised as N-1 by the number/claim pass;
**I re-derived it at the source and confirm it**, and I note that my own ledger row is where it slipped
past, because I recorded the cosine as inherited rather than re-deriving it. Ledger finding L-8.

> **ROUND 8, 2026-07-30 — FIXED IN BOTH TEXTS. The false bound is gone; the sentence now reports the
> largest per-dataset mean instead of bounding it.** Both files read "the largest per-dataset mean in
> absolute value is $+0.0032$" — `chapters/5_mobiwac/02_related.tex:156-165` and
> `articles/[mobiwac]/src/sections/02_related.tex:94-104`. `\pm0.003` appears in neither, in prose or
> in comment:
> ```bash
> cd ../..
> python3 -c "
> import sys
> from pathlib import Path
> sys.path.insert(0, 'articles/dissertacao/src_utils')
> from check_audit_claims import live_text
> for p in ('articles/dissertacao/src/chapters/5_mobiwac/02_related.tex',
>           'articles/[mobiwac]/src/sections/02_related.tex'):
>     t = live_text(Path(p))
>     print(Path(p).parent.name, 'pm0.003:', 'pm0.003' in t, '| reports_0.0032:', '+0.0032' in t)
> "
> # EXPECT: lines=2
> # EXPECT: contains=pm0.003: False | reports_0.0032: True
> ```
> That is the right repair rather than loosening the bound to `±0.004`: `0.0032` is the value the
> source of record carries (`WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:29-31`, per-state FL +0.0007,
> **AL +0.0032**, AZ −0.0005, GE −0.0004), so printing it is quoting rather than bounding. The pooled
> figure prints as `+0.001` in both texts and the orthogonality conclusion is untouched, as this item
> predicted. `articles/[mobiwac]/ERRATA.md` carries the parity entries.

Before anything else, one command reproduces the build state every other row assumes:

```bash
cd ~/Desktop/mestrado/ingred/articles/dissertacao && source src_utils/texenv.sh \
  && (cd src && make defense && make academico && make ppgc)
grep -h 'Output written' src/build/main.log src/build/main_academico.log src/build/main_ppgc.log
```
Expect **100, 97, 101 pages**.

> **ROUND 8, 2026-07-30 — the expected counts in this block were 108 / 105 / 109 and are now
> 100 / 97 / 101.** Measured, one target at a time:
> `make defense` prints `Output written on build/main-aux/main.pdf (100 pages, 1538478 bytes)` and the
> builder line `latexbuild main -> build/main.pdf pages=100 tex_errors=0`; `main_academico.pdf` is 97
> pages and `main_ppgc.pdf` is 101, both read with `pypdfium2` (`len(PdfDocument(...))`), which is the
> instrument that cannot disagree with the file. The eight-page drop is round 7 moving Appendices B and
> D into the supplementary volume `main_extra.pdf` (20 pages) — the same move that makes this list's
> "page 93/95/99" coordinates unresolvable in `main.pdf`. **Consequence for every other row here: a
> page number in this file that lands past 100, or names the errata appendix, is a coordinate into the
> pre-round-7 build.** The per-page claims re-measured in round 8 are annotated with the build they
> were read from. The gate `recorded page counts vs the measured build` covers this going forward.
> (This rewrites the tracked `src/dissertacao.pdf`; `git checkout --
> articles/dissertacao/src/dissertacao.pdf` afterwards if you do not intend to commit it.)

---

## Where to run these commands

Unless a block says otherwise with its own `cd`, **run from `articles/dissertacao/`**:

```bash
cd articles/dissertacao
```

Paths that reach outside the dissertation folder are written `../../` from there. Blocks that begin
`cd articles/dissertacao` are meant to run from the **repository root** and say so in their own first
line.

**What has and has not been verified about these commands.** Run
`python3 src_utils/check_verify_list.py` from `articles/dissertacao/`; as of 2026-07-28 it reports:

```
15 documented command(s) executed; 7 carried a machine-checkable expectation; 0 failed.
2 skipped to avoid recursion (they invoke this gate's own caller)
1 build block: cwd checked, build NOT run here
8 were executed but NOT asserted against their prose expectation.
```

Read that as four categories, because they are not the same thing:

- **7 verified.** Output compared against a stated expectation (`# EXPECT: lines=N` / `contains=` /
  `equals=` inside the block).
- **8 run, not verified.** They execute and produce output, but their "if all is well" text is a human
  judgment or too discursive to encode. **Do not describe these as verified.**
- **2 skipped, deliberately.** They invoke `make check`, which invokes this harness. Running them here
  does not terminate; they are exercised every time `make check` itself runs.
- **1 build block.** Its working directory is checked but the three-target build is not re-run here —
  that takes four minutes and `build.sh` is the tool for it. Verified separately: 108/105/109 pages,
  `tex_errors 0`, `make check` RC=0.

**Greps over `.tex` files strip comment lines first** (`grep -vn '^[[:space:]]*%'`). This source carries
dense provenance comments that quote the very strings being searched for, so an unfiltered sweep
reports more hits than the reader sees. Three commands in this file were wrong for exactly that reason
on 2026-07-28 and were corrected: a `\path{}` count annotated 13 that returned 15, a "four of six"
sweep promising 3 prose hits that returned 4, and a "three of our six" sweep promising **zero** that
returned 5, every one an audit comment. Six paths across four commands also resolved from neither
working directory. The harness above exists so the next such defect is caught by running the file
rather than by reading it.

## Tier 1 — would mislead a reader or the banca (items 1-6)

**1. `make check` is red, and the round's build claim says it is green.**
The round state and the split commit both assert "`make check` all gates pass". It exits 1, and it
does so at `870f882c`, `01915ba7` and `4e84cf7a` alike, on the `'this paper' / 'this article'`
gate.
```bash
cd src && bash ../src_utils/check.sh; echo "EXIT=$?"
```
*If all is well:* you see exactly one hit,
`chapters/apx_b_errata.tex:307: This article differs from the other two…`, `EXIT=1`, and you decide
whether that sentence (which refers to the MobiWac manuscript, not to the dissertation) earns the
same documented exemption `apx_b_errata` already has in the banned-words gate. **What must not
stand is a durable record claiming the gate passes while it does not** — that is the failure mode
`AGENT_GUARDRAILS` §7 names, and it is the reason this item is first. Ledger finding L-1.

> **ROUND 8, 2026-07-30 — RESOLVED, and by the exemption route this item offered rather than by a
> prose edit. `check.sh` now exits 0.** Read directly, never after a pipe (a round-7 commit reported a
> gate as passing when the rc belonged to `head`):
> ```
> cd src && bash ../src_utils/check.sh >/tmp/chk.txt 2>&1; echo "CHECK_RC=$?"   ->  CHECK_RC=0
> ```
> 22 gates, suite total 2.047 s, every gate under the 5 s threshold. The `'this paper' / 'this
> article'` gate now carries `apx_b_errata` as a documented exemption in its own header line
> ("apx_b_errata exempt: see below", `check.sh:129-131`), which is the disposition this item put to the
> author: the sentence refers to the MobiWac manuscript and survives at
> `chapters/apx_b_errata.tex:348` (not `:307` — the file grew). So the durable record and the gate now
> agree, which is what the item asked for.
>
> Two things worth carrying forward, because they are the reason this row was first and they are both
> now covered. The suite was **265 s** in round 7, 99.5 percent of it this file's own harness
> rebuilding the PDFs on every run; the build refusal in `check_verify_list.py` closed that and the
> per-gate timing table above is what makes a regression visible (§4b V12). And the gate count in the
> header is 22, matching the 22 rows of the timing table — count them if you change the suite, because
> a headline that does not reconcile with its own rows discredits the measurements beside it (V13).

**2. The Standley correction changes a published claim against the chapter's own interest.**
Page 34 of the defense PDF, the `Empirical Performance` bullet plus its footnote.
*Check:* read p. 34 and the footnote, then read the Appendix B row (p. 93). *If all is well:* the
bullet claims **only** reduced inference cost; the footnote reproduces the published sentence, says
the cited work names accuracy and reduced training time among benefits joint training may have "in
theory", and quotes it arguing the other way. I re-read `arXiv:1905.07553` (v3 and v4) this session
and confirm all nine quotations verbatim. **This is `[NEEDS SIGN-OFF]` and it removes a stated
advantage of the architecture Chapter 3 adopts — it is your call, not the reviewer's.**

> **ROUND 8, 2026-07-30 — the text is as this item describes it; the SIGN-OFF is still open.** Both
> halves measured in the source with the comment stripper, and located in the render:
> the bullet at `chapters/3_cbic/method.tex` claims **only** reduced inference cost ("sharing one
> network across tasks reduces inference cost, since one network is evaluated instead of one per task")
> and its footnote reproduces the published sentence, then states that the cited work names improved
> accuracy and reduced training time among the benefits joint training may have "in theory" and argues
> the other way empirically, quoting "often leads to inferior overall performance as task objectives
> can compete". It prints on **p. 35** of the 100-page defense build, not p. 34 (round-7 pagination).
> The Appendix B row is in the supplementary volume, `main_extra.pdf` p. 14, not defense p. 93.
> **No agent action is possible here and none was taken**: the item is `[NEEDS SIGN-OFF]` because it
> narrows a published claim against the chapter's own interest, which is an author ruling. It is one of
> the 53 markers inventoried under `PENDENCIAS.md` §2.1 (see §2.13 for the corrected count).

**3. The Nash-MTL guarantee, narrowed in published co-authored prose.**
`chapters/4_courb/methodology.tex:36`, rendered p. 47.
*If all is well:* the sentence reads "Away from a Pareto-stationary point … and under the method's
assumption that the gradients are linearly independent there, that direction is a descent direction
for every task". Both conditions are in the paper: p.1 "Under certain as-sumptions", p.3 "if θ is
not Pareto stationary then the gradients are linearly independent", p.6 "our update rule is a
descent direction for all tasks". I verified all three in the 19-page PDF. Also `[NEEDS SIGN-OFF]`.

> **ROUND 8, 2026-07-30 — the narrowed sentence is in the source, word for word as this item quotes
> it.** At `chapters/4_courb/methodology.tex`, comment-stripped: "Away from a Pareto-stationary point,
> meaning a point at which some convex combination of the task gradients is zero, and under the
> method's assumption that the gradients are linearly independent there, that direction is a descent
> direction for every task, avoiding the dominance of one task over the other." Both conditions the
> item requires are present ("Away from a Pareto-stationary point", "under the method's assumption that
> the gradients are linearly independent"). It prints on **p. 48** of the defense build, not p. 47. I
> did **not** re-open `arXiv:2202.01017` to re-verify the three page-level quotations; that half rests
> on the round-6 pass's authority and is recorded here as inherited rather than re-derived, which is
> the distinction item 0's own ledger row shows is worth making. Still `[NEEDS SIGN-OFF]` — and note
> that the same sentence is the second prose site of the unregistered "Pareto-stationary point" of item
> 4, so the two decisions touch one line and should be taken together.

**4. Two glossary terms are in the rendered document and not in the registry.**
The registry is fail-closed, so this **blocks** the new Ch.2 paragraph rather than merely awaiting
wording.
```bash
grep -c 'bilinear discriminator\|logistic function' GLOSSARY.md   # expect 0 today
```
*If all is well:* you approve (or reject) the two proposed entries in `16_frame_numbers.md` §4 and
the entry lands **before** p. 19 ships. Same question for **Pareto-stationary point** at p. 47
(`15_claim_scoping_applied.md` §9). Three entries, one decision.

> **ROUND 8, 2026-07-30 — TWO OF THREE LANDED; THE THIRD IS STILL AN OPEN FAIL-CLOSED BREACH.**
> Credit the part, not the finding (§4b V14 consequence 2), so this row is split:
> ```bash
> cd articles/dissertacao
> printf 'bilinear discriminator %s\nlogistic function %s\nPareto-stationary %s\n' \
>   "$(grep -c 'bilinear discriminator' GLOSSARY.md)" \
>   "$(grep -c 'logistic function' GLOSSARY.md)" \
>   "$(grep -c 'Pareto-stationary' GLOSSARY.md)"
> # EXPECT: contains=bilinear discriminator 1
> # EXPECT: contains=logistic function 1
> # EXPECT: contains=Pareto-stationary 2
> ```
> (`grep -c` counts matching LINES, so each registered term reads 1: one row each. An earlier draft of
> this probe annotated `logistic function 2`, carried over from a string-occurrence count — the term
> appears twice on line 72, as the row name and again inside its own note. The harness failed the
> block, which is the point of annotating it rather than describing it. §4b V1, and it is the same
> class of defect as the `# 13` that returned 15.)
> **bilinear discriminator** is registered at `GLOSSARY.md:71` and **logistic function** at `:72`,
> both with the note that they clear this block; the terms print in Chapter 2 (defense build p. 20).
> That half is closed.
>
> **ROUND 9, 2026-07-30 — THE THIRD LEG IS NOW CLOSED, AND THE EXPECT ANNOTATION ABOVE CHANGED FROM
> `Pareto-stationary 0` TO `2` FOR THAT REASON.** The author decided the open question recorded as
> `PENDENCIAS.md` §2.12 with `DESICAO: A.` (register the term), and the entry landed: `GLOSSARY.md:103`
> in §4 and `:148` in the §6 Portuguese table, which is why `grep -c` reads 2 rather than 1. Three
> further terms were registered in the same pass (Pareto dominance, Pareto optimality, gradient
> conflict) because §2.3 needed them. Source ledger, with the page of each definition in the paper it
> came from: `_history/_round9/31_pareto.md`. **This annotation was stale for exactly one commit**, and the
> harness caught it, which is the behavior wanted: the gate failed on a claim that had become false
> because the underlying decision was taken. That is `§4b V6` in action, a fixed number surviving at a
> second site, so the count was re-measured here rather than carried across.
>
> The original finding, kept because it is the reason the entry exists: the term was **in prose at
> five live sites and absent from the registry**, breaking the fail-closed rule.
> `chapters/3_cbic/method.tex` ("convergence to a Pareto-stationary point"), two in
> `chapters/3_cbic/basis.tex` ("Pareto-optimal descent directions", "Pareto efficiency"),
> `chapters/4_courb/methodology.tex` (the narrowed Nash-MTL guarantee of item 3 above), and the
> `tables/courb/errata.tex` row that records that narrowing, which carries the unhyphenated "Pareto
> stationary". The earlier note said two sites and pp. 36 and 48; the count and the volume are
> corrected here, and so are the page numbers, for two separate reasons.
>
> **Rendered pages, measured with pypdfium2 against the 101-page defense build of this commit** (the
> new §2.3 passage adds one page, so every site after Chapter 2 moved by one, and the pre-edit
> 100-page figures are what the first draft of this note wrongly carried). The builds are the ordinary
> `make defense` / `make extra` in `src/`, quoted in prose rather than as a shell block on purpose:
> `check_verify_list.py` executes every fenced block it finds, and a three-target build took that gate
> from 4 seconds to 297, which is why build blocks there are cwd-probed rather than run.
>
> | site | defense page | volume |
> |---|--:|---|
> | the new §2.3 passage (this round's addition) | 23 | defense |
> | `3_cbic/basis.tex` "MGDA finds Pareto-optimal descent directions" | 31 | defense |
> | `3_cbic/basis.tex` "guarantees of Pareto efficiency" | 32 | defense |
> | `3_cbic/method.tex` "convergence to a Pareto-stationary point" | 37 | defense |
> | `4_courb/methodology.tex` the narrowed Nash-MTL guarantee | 49 | defense |
> | `tables/courb/errata.tex` the row recording that narrowing | 16 | **supplementary** (`make extra`, 20 pp; not in the defense build at all) |
>
> A page number in a durable record is only true of the build it was taken against, which is why the
> build and its page count are named in the row above rather than left implicit.
>
> **One correction to this item's own reasoning, since it governed what an agent was allowed to do.**
> It stated that both prose sites are reproduced published prose. Measured in round 9: the Chapter 3
> sentences are (each is a verbatim substring of `articles/CBIC___MTL/sections/*.tex`), but the
> Chapter 4 sentence is **not** — it is this dissertation's own errata-corrected sentence, and the
> published Portuguese source contains no occurrence of the term (`articles/CoUrb_2026/src`, nine
> `.tex` files, zero live matches). The conclusion the item drew still holds for a different reason:
> the Chapter 4 sentence is already listed in Appendix B, so rewording it again would mean revising an
> errata entry, not a published one.
>
> Each of the five sentences was also checked against the guarantee its source paper actually states,
> and all five state it correctly; the one imprecision, MGDA described as finding "Pareto-optimal
> descent directions" where `sener2018mgda` states a dichotomy between Pareto stationarity and a
> common descent direction (its pp. 4 and 6), sits inside published prose and was left as published.
> Note that the gate suite's informational Pareto gate ("the technical term is legal") passes and
> always did: it counts occurrences, not registration, so `make check` never caught the breach. What
> catches it now is `check_audit_claims.py`, probes `R9-pareto` and `R9-conflict`.

**5. Chapter 5 hedges the region result and the frame does not.**
`chapters/5_mobiwac/05_setup.tex:76` (p. 66) states that the analysis plan "did not cover
next-region superiority, so the four next-region gains … are secondary results outside it". The
Resumo (p. 2), the Abstract (p. 3), Chapter 1 (p. 13) and Chapter 6 all say the joint model
outperforms on region "at four of six" with no such qualifier.
```bash
cd articles/dissertacao
# REPOINTED 2026-08-02, after the author's revised tree was merged. The finding this block
# records -- that the frame prose asserted a region win at four of six WITHOUT the qualifier --
# is now CLOSED, by his own decision 2.11 (option B, taken this round). Every surviving site
# carries the non-inferiority caveat: content.tex once in the Resumo and once in the Abstract,
# 6_conclusion.tex twice, each reading "at four of the six. At the other two, it remains
# statistically non-inferior within a two-point margin (TOST)". He removed the claim from the
# introduction entirely in his revision, so the count is 3, not 4. Verified by reading all
# three hits, not by adjusting the number to match.
# REWRITTEN 2026-08-02 to check the CLAIM instead of a phrase. The original grepped for the
# literal "four of six"; the author has since reworded the same claim twice ("four of the six",
# then "em quatro conjuntos"), and each rewording made the probe report a defect that was not
# there. What the finding is actually about is whether a region-win claim ever appears WITHOUT
# its non-inferiority qualifier, so that is what this now measures: every sentence naming a
# four-of-six region result must also carry the TOST caveat.
python3 - <<'PY'
import sys, re, glob; sys.path.insert(0, 'src_utils')
from pathlib import Path
from check_audit_claims import live_text
bad = 0
for f in ['src/content.tex', 'src/chapters/1_introduction.tex', 'src/chapters/6_conclusion.tex']:
    t = re.sub(r'\s+', ' ', live_text(Path(f)))
    for m in re.finditer(r'[^.]{0,220}(?:four of (?:the )?six|em quatro conjuntos|at four of)[^.]{0,260}\.', t):
        s = m.group(0)
        # The caveat may live in the NEXT sentence ("... at four of the six. At the other two,
        # it remains statistically non-inferior ..."), which is correct prose and how Chapter 6
        # writes it. So the window extends past the claim's own full stop. A per-sentence window
        # reported both conclusion sentences as unqualified when both are qualified.
        tail = t[m.end():m.end() + 240]
        if not re.search(r'non-inferior|n[aa\u00e3]o-inferior|TOST', s + tail, re.I):
            print('UNQUALIFIED:', f, s[:150]); bad += 1
print('unqualified region claims:', bad)
PY
# EXPECT: contains=unqualified region claims: 0
```

> **ROUND 9c, 2026-07-30 — THE EXPECTATION MOVED FROM 3 TO 4, and the author's ruling is why.**
> `PENDENCIAS` 2.11, his option B: promote the non-inferiority caveat wherever the region result is
> stated. Chapter 6's consolidated-answer sentence stated it without the partition at all ("outperforms
> the dedicated models on the category task everywhere and outperforms or matches them on the region
> task"), so it matched neither `four of six` nor `four of the six` and this command could not see it.
> Rewritten to carry the partition, it now does, which takes the count to **4 prose hits**: one in
> `content.tex` (the Abstract), one in `1_introduction.tex`, and **two** in `6_conclusion.tex`.
> The premise of the finding above is also corrected by the same measurement. It says the frame states
> the result "with no such qualifier". Swept across all 54 live `.tex` files of both trees on
> 2026-07-30, comments stripped and matching across line wraps: 15 sites state the partition and **14
> already carried the TOST caveat**. The two that did not were this Chapter 6 sentence and the Chapter 5
> results subsection lead, and both now do. What the frame still does not carry is the *analysis-plan*
> qualifier this item is actually about (that region superiority sat outside the registered plan), which
> is a different claim from the TOST caveat and is untouched by 2.11.
Comment lines are dropped **before** the search (`grep -vn` keeps the original line numbers). Without
that this returns 4 hits, one being an indented provenance comment rather than prose the reader sees:
**3 prose hits is the answer**, not 4.

> **ROUND 8 CORRECTION, 2026-07-30 — the command named a file that does not exist, and its
> expectation passed anyway.** The first element was `src/0_main.tex`; the front matter moved into
> `src/content.tex` before this list was written, so that `grep` wrote
> `grep: src/0_main.tex: No such file or directory` to **stderr** and contributed nothing to stdout.
> `# EXPECT: lines=3` counts stdout lines only, so the block reported *verified* while searching two
> files instead of three. The three hits it printed are all in the two files that do exist
> (`1_introduction.tex:132`, `6_conclusion.tex:21`, `6_conclusion.tex:93`) — the arithmetic was a
> coincidence, not a check. §4b V1/V2: the number matched, the command did not do what its prose
> says. With `content.tex` substituted the expectation is unchanged at 3, because the Resumo and the
> Abstract phrase the count as "quatro deles" / "four of them" rather than "four of six":
> ```
> src/content.tex:166:            a joint-best selection. On next region it outperforms at four of them and
> ```
> That is the same claim in different words, so the asymmetry this item raises is **wider than the
> item states**, not narrower. Measured with the comment-stripping sweep over all 54 `.tex` files:
> the unhedged count appears in prose at `1_introduction.tex`, `2_fundamentals.tex:786`,
> `5_mobiwac/01_introduction.tex:39`, `5_mobiwac/08_conclusion.tex:14`, `5_mobiwac.tex`, and twice in
> `6_conclusion.tex` — seven sites, plus the two front-matter paraphrases. In the rendered defense
> PDF the phrase prints on pages 14, 58, 59, 76, 77 and 78; the hedge prints on page 67 alone.
> The decision this item asks for is unchanged and is now `PENDENCIAS.md` §2.11.

*If all is well:* you rule either that the frame adds "as a secondary result" once, or that the
asymmetry is deliberate and goes in `LEFT_OUT.md`. The statistics record's own 2026-07-27 correction
is unambiguous that the registered primary test for **every** region cell is TOST non-inferiority.
No round-6 track owned this. Ledger finding L-5. **Handed to the author as `PENDENCIAS.md` §2.11 on
2026-07-30** (round 8): the measurement is complete, the ruling is his.

**6. The Ch.2 sentence that the Ch.3 protocol addition just falsified.**
Chapter 2 (`chapters/2_fundamentals.tex:601-602`, **rendered p. 23**) says Chapter 3 "reports
five-fold cross-validation without identifying the split axis". The Ch.3 addition landed and does
identify it (`chapters/3_cbic/results.tex:30`, rendered p. 36). I confirmed both in the PDF, so this
is a live contradiction the reader can see, thirteen pages apart.
```bash
# The clause wraps across two source lines, so the file is read as one string -- AND the
# comments are stripped first, with this tree's own stripper, because the repair's provenance
# comment quotes the retired clause verbatim. A comment-blind read of this file reports the
# landed fix as missing (round-8 correction below).
python3 -c "
import sys; sys.path.insert(0, 'src_utils')
from pathlib import Path
from check_audit_claims import live_text
# REPOINTED 2026-08-02: the author's revised tree MOVED this clause out of the fundamentals
# chapter and into Appendix A. Verified before repointing, over every live .tex: the repair
# sentence occurs exactly once, in chapters/apx_a_contributions.tex, and the retired clause
# occurs ZERO times anywhere. So the claim this block checks still holds; only its address moved.
# ADDRESS WIDENED 2026-08-03 (round 12), after the same repointing came due a SECOND time. The
# author's instruction moved Section A.1 out of the defense volume and into the supplementary
# volume, so the repair sentence now lives in chapters/apx_extra_platform.tex and the hard-coded
# path below read False for a sentence that had not changed one character. A probe that names one
# file measures the ADDRESS, not the claim. Neither EXPECT line changes and neither assertion is
# relaxed: both strings are now sought across every live .tex under src/, which is strictly wider
# than one file in each direction, so the retired clause is caught wherever it reappears and the
# repair is found wherever the author puts it. Measured with this stripper before the change:
#   repair sentence -> exactly one live site, src/chapters/apx_extra_platform.tex
#   retired clause  -> zero live sites anywhere
t = ''.join(live_text(p) for p in sorted(Path('src').rglob('*.tex')) if 'build' not in p.parts)
print('retired_clause_in_prose:', 'without identifying the split axis' in t)
print('repair_in_prose:', 'stratified its folds by sample rather than by user' in t)
"
# EXPECT: contains=retired_clause_in_prose: False
# EXPECT: contains=repair_in_prose: True
```
*If all is well:* `retired_clause_in_prose: False` and `repair_in_prose: True`, because the clause has
been replaced by the repair drafted in the comment at the Ch.3 site ("Chapters 3 and 4 both stratify
by sample rather than by user … and only Chapter 5 splits by user"). `[VERIFY]` V-8.

> **ROUND 8, 2026-07-30 — VERIFIED APPLIED, and the command as written said the opposite.** The
> repair is in the prose, at `chapters/2_fundamentals.tex:646-649`: "Chapters 3 and 4 both stratify by
> sample rather than by user, so that the check-ins of one user may appear in both training and
> validation, and only Chapter 5 splits by user." It prints on **p. 24** of the 100-page defense build
> (`pypdfium2`, hyphenation normalized). The retired clause survives only inside the `%` provenance
> comment at `:651` that explains why it was retired, so the old command — which read the raw file —
> printed `True` and scored a real fix as unapplied. This is trap 1 of
> `_history/_round8/28_postmortem_false_applied.md` inverted: a comment-blind read can fail a fix as easily as
> it can pass a missing one. The block above now strips comments with `check_audit_claims.strip_text`,
> per §4b V4, and carries two assertions so the harness checks both halves rather than the absence
> alone.

---

**6b. A printed count in the errata appendix does not sum.**
Page 95 says the MTLnet spelling was normalized "at all 25 places where the name appears in the
printed chapter: 21 in prose, one in a subsection heading, one in a figure caption, and two in table
headings".
```bash
grep -rn 'subsection{.*MTLnet' src/chapters/4_courb/    # expect TWO hits
# EXPECT: lines=2
```
*If all is well:* the appendix says 26 with "two in subsection headings" — because there are two
(`methodology.tex:87` "Baseline: MTLnet with DGI" and `related.tex:42` "The MTLnet framework"), and
21 + 2 + 1 + 2 = 26. The chapter's own source comment (`4_courb.tex:7`) already says **26 sites**,
and `12_figures.md` calls it the 26-site normalization, so three records give three counts and the
wrong one is the one that prints. No result depends on it; it is in the appendix whose only job is to
be exactly right about what changed. Ledger finding L-9.

> **ROUND 8, 2026-07-30 — CLOSED, and the printed count is now 28, neither 25 nor the 26 this item
> predicted.** The appendix reads: "normalized to the second form at all **28** places where the name
> appears in the printed chapter **and its tables**: 23 in prose, two in subsection headings, one in a
> figure caption, and two in table headings" — supplementary volume `main_extra.pdf` p. 9 (the errata
> appendix moved out of the defense build in round 7, which is why this item's "page 95" no longer
> resolves there). Every component reconciles against the source, counted with this tree's own
> stripper over the seven `4_courb/*.tex` files, `4_courb.tex`, and the four `tables/courb/*.tex`:
>
> **ROUND-EXTRAVOL, this session — RECOUNTED to 27 (22 in prose).** Removing the Tarik
> first-authorship sentence from `4_courb.tex`'s preface (author instruction, unrelated to this
> normalization) dropped one of the 23 prose `MTLnet` occurrences as a side effect. The appendix
> prose and the EXPECT annotation below are both updated to 27 / 22; the command and its scope are
> unchanged.
> ```bash
> cd articles/dissertacao
> python3 -c "
> import sys; sys.path.insert(0, 'src_utils')
> from pathlib import Path
> from check_audit_claims import strip_text
> SRC = Path('src')
> files = sorted((SRC/'chapters/4_courb').glob('*.tex')) + [SRC/'chapters/4_courb.tex'] \
>         + sorted((SRC/'tables/courb').glob('*.tex'))
> b = {'prose': 0, 'subsection': 0, 'caption': 0, 'table_heading': 0}
> for f in files:
>     in_tables = 'tables/' in str(f)
>     for line in f.read_text().splitlines():
>         live = strip_text(line)
>         n = live.count('MTLnet')
>         if not n: continue
>         k = ('subsection' if '\\\\subsection' in live else
>              'caption' if '\\\\caption' in live else
>              'table_heading' if in_tables else 'prose')
>         b[k] += n
> print('prose', b['prose'], 'subsection', b['subsection'],
>       'caption', b['caption'], 'table', b['table_heading'], 'total', sum(b.values()))
> "
> # EXPECT: contains=prose 22 subsection 2 caption 1 table 2 total 27
> ```
> The two table-heading sites are `tables/courb/category.tex:10` and `tables/courb/next.tex:10`, both
> `\textbf{MTLnet}` column heads. Note what the earlier count missed and why: the phrase "in the
> printed chapter" excluded the two `tables/courb/` files, which the chapter `\input`s and the reader
> sees — so 21 prose was really 23 prose plus 2 table headings across a wider file set. The appendix
> now names the file set in the sentence ("and its tables"), which is what makes the total checkable
> rather than merely arithmetic. Verified against the render, not the intent.

---

## Tier 2 — a pass verified its own work and no fresh eyes have looked (items 7-13)

**7. The Appendix A protocol numbers, which describe your own conduct.**
`chapters/apx_a_contributions.tex:107,113` (rendered p. 91): `StratifiedGroupKFold`, five splits,
partition seed **42**, grouping by user, seeds **0, 1, 7, 100**.
```bash
grep -n 'random_state=42\|Seeds {0, 1, 7, 100}' ../../docs/context/DATA_SPLITS.md
```
*If all is well:* `DATA_SPLITS.md:16` and `:65` say exactly that. I reproduced both. The reason to
look yourself is that this appendix is new this round and is a claim about how the experiments were
run, which is the class of claim you personally answer for at the defense.

> **ROUND 8, 2026-07-30 — VERIFIED, with the appendix's coordinates re-anchored.** The two source
> lines are unchanged: `DATA_SPLITS.md:16` reads
> `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)` and `:65` reads
> `**Seeds {0, 1, 7, 100}** for the standard 4-seed pool. Combined with 5 folds -> n=20 paired
> (seed, fold) tuples.` The appendix states the same five facts, now at
> `chapters/apx_a_contributions.tex:153-154` (splitter, five splits, shuffling, seed 42, grouping by
> user) and `:160` (the four initializations), not at the `:107,113` this item cites — the file grew
> after the list was written, so cite the phrase and date the line number (`ANCHORS.md` §5). One
> wording note, not a defect: the appendix writes the seeds as prose ("0, 1, 7, and 100"), so a probe
> searching for the literal `0, 1, 7, 100` returns false. Match on `0, 1, 7, and 100`.

**8. The Check2HGI loss equation (three numbered equations, new to Ch.2, p. 19).**
The weights `0.4 / 0.3 / 0.3` appear in two independent places and agree:
`docs/context/check2hgi_overview.tex:215` and
`research/embeddings/check2hgi/model/Check2HGIModule.py:51-53`, summed at `:1192-1195`. I checked
both. *If all is well:* they still agree, **and** you settle the open question the pass could not:
the code carries two further auxiliary terms whose defaults are `0.0` and which the equation omits.
`[VERIFY]` V-14's sibling; the pass says settling it needs the run configuration of the shipped
representation.

> **ROUND 8, 2026-07-30 — VERIFIED, and the open question is CLOSED without needing the author. The
> auxiliary terms are FOUR, not two.** The weights still agree in both places:
> `check2hgi_overview.tex:215` prints `0.4 L_c2p + 0.3 L_p2r + 0.3 L_r2c` and
> `Check2HGIModule.py:51-53` declares `alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3`, summed at
> `:1192-1195`. Chapter 2's Equation (`eq:fund:check2hgi`) prints the same three coefficients.
> ```bash
> cd ../..
> python3 -c "
> import re
> from pathlib import Path
> seg = Path('research/embeddings/check2hgi/model/Check2HGIModule.py').read_text()
> seg = seg[seg.find('def __init__'):][:6000]
> for name in ('mae_lambda', 'p2p_lambda', 'n2v_lambda', 'n2v_align_lambda'):
>     m = re.search(name + r'\s*:?\s*[\w\[\].]*\s*=\s*([^\n,]+)', seg)
>     print(name, m.group(1).strip() if m else 'NOT_IN_SIGNATURE')
> "
> # EXPECT: lines=4
> # EXPECT: contains=mae_lambda 0.0
> # EXPECT: contains=n2v_align_lambda 0.0
> ```
> All four default to `0.0`: `mae_lambda` (T4.1 masked reconstruction), `p2p_lambda` (T6.1 co-visit
> InfoNCE), `n2v_lambda` (T5.2a Node2Vec skip-gram) and `n2v_align_lambda` (its alignment term). What
> settles the question is that each is guarded by a **conjunction**, not by the coefficient alone:
> every one requires both `lambda > 0` **and** an optional data structure or head that the canonical
> path never builds (`self._mae_loss is not None`, `data.covisit_pairs`, `self.n2v_head is not None`).
> The four coefficients are also unreachable from the canonical entry point: `check2hgi.py` reads each
> through `getattr(args, ..., 0.0)`, and the only `add_argument` declarations for them live in
> `scripts/canonical_improvement/regen_emb_t3.py`, a T3 experiment helper, where `--n2v-lambda`'s
> non-zero default of 0.3 is itself gated behind `--use-node2vec-poi`
> (`_n2v_lambda_eff = float(args.n2v_lambda) if args.use_node2vec_poi else 0.0`, `:356`).
> So the equation as printed is exact for the shipped representation, and the omission is correct
> rather than a simplification. This does **not** need the author's run configuration, which is why it
> is closed here and not handed over.

**9. The joint model's descent from MTLnet (new frame prose, p. 20).**
The claim is that the joint model is a *specialization* of the MTLnet class overriding exactly one
component.
```bash
sed -n '42p'  ../../src/models/mtl/mtlnet_crossattn_dualtower/model.py  # class …DualTower(MTLnetCrossAttn)
sed -n '207p' ../../src/models/mtl/mtlnet_crossattn/model.py            # class MTLnetCrossAttn(MTLnet)
sed -n '368p' ../../src/models/mtl/mtlnet_crossattn/model.py            # "Override MTLnet's FiLM + shared_layers…"
```
(from the repository root). *If all is well:* all three lines read as above — I confirmed each of the
six coordinates the comment cites. This one is worth your eyes because it is the sentence that
licenses reading Chapter 3's null against Chapter 5's positive result, which is the arc of the
dissertation.

> **ROUND 8, 2026-07-30 — VERIFIED. All three lines read as documented, at the lines documented.**
> ```bash
> cd ../..
> sed -n '42p'  src/models/mtl/mtlnet_crossattn_dualtower/model.py
> sed -n '207p' src/models/mtl/mtlnet_crossattn/model.py
> sed -n '368p' src/models/mtl/mtlnet_crossattn/model.py
> # EXPECT: lines=3
> # EXPECT: contains=class MTLnetCrossAttnDualTower(MTLnetCrossAttn):
> # EXPECT: contains=class MTLnetCrossAttn(MTLnet):
> ```
> `:42` is `class MTLnetCrossAttnDualTower(MTLnetCrossAttn):`, `:207` is
> `class MTLnetCrossAttn(MTLnet):`, and `:368` is the docstring
> `"""Override MTLnet's FiLM + shared_layers with cross-attention blocks."""`. The inheritance chain
> the frame prose asserts is therefore in the code as two class statements, and the single overridden
> component is named by the class that overrides it. Unusually for this list, the coordinates did not
> drift; these three are the load-bearing ones and they are now annotated so the harness re-reads them
> on every `make check` instead of only when a human runs the block.

**10. The Resumo and Abstract word counts, on the rendered page.**
Reported as 310 / 271. I measure **310 and 272** with the report's own instrument.
```bash
python3 src_utils/_history/_round6/_measure_abs.py <(printf '[{"pdf":"src/build/main.pdf","pages":[2],"label":"Resumo"},{"pdf":"src/build/main.pdf","pages":[3],"label":"Abstract"}]')
```
*If all is well:* Resumo 310 words / 11 sentences / mean 28.2 exactly, Abstract 272 / 11 / 24.7. The
one-word gap is two soft-hyphen breaks on p. 3; the instrument does not apply the hyphenation
normalization its own documentation declares. Trivial in size, but it is a number in a durable
record that does not reproduce. Ledger finding L-4.

> **ROUND 8, 2026-07-30 — RE-MEASURED, AND NEITHER PAIR REPRODUCES: the counts are now 312 and 277.**
> Same instrument, same pages, on the current 100-page build (write the spec to a file; process
> substitution is not available in this sandbox):
> ```
> printf '[{"pdf":"src/build/main.pdf","pages":[2],"label":"Resumo"},
>          {"pdf":"src/build/main.pdf","pages":[3],"label":"Abstract"}]' > /tmp/abs_spec.json
> python3 src_utils/_history/_round6/_measure_abs.py /tmp/abs_spec.json
>   Resumo   312 words / 11 sentences / mean 28.4
>   Abstract 277 words / 11 sentences / mean 25.2
> ```
> This is a **stale record, not a defect in the document**: the sentence counts still hold at 11 and 11,
> and both blocks were edited after that measurement — `src/content.tex` moved through three commits
> since (`2b9b853d` split `0_main.tex` into `preamble.tex` + `content.tex`, `e771d331`, `19396c9f`).
> Nothing in the dissertation claims 310 or 271, checked across all 54 `.tex` files for a
> word-count sentence carrying any of 310/271/312/277: zero hits. The figures live only in round-6
> reports (`06_07_number_claim_audit.md:302-303`, `15_resumo_abstract.md:75`), and the standing rule for
> those is item 20: do not repair the reports, use this file as the address book. So L-4's substance is
> closed — the instrument's soft-hyphen blindness is real and documented, and it is now the smaller half
> of the discrepancy.

**11. The near-blank page the Resumo cut was meant to remove.**
*Check:* open p. 2 of the defense PDF. *If all is well:* the `Palavras-chave` block is on **p. 2
with the Resumo** (I confirmed: keywords appear on p. 2 only, and the old orphan page is gone; front
matter word counts are p.1 = 54, p.2 = 363, p.3 = 317). Worth a glance because the pagination has
moved three times since that fix.

> **ROUND 8, 2026-07-30 — VERIFIED, still true after the round-7 repagination.** `Palavras-chave`
> appears on **p. 2 only** (swept across all 100 pages with `pypdfium2`, one hit), so the orphan page
> has not come back. The front-matter word counts read p.1 = 54, p.2 = 361, p.3 = 317 — p.1 and p.3
> unchanged, p.2 two words below the recorded 363, which is the same two words the Resumo gained in
> item 10 landing on a page whose total was measured with a different tokenizer. The first numbered
> page is physical 12 printing 12, so the front matter is intact ahead of it.

**12. The paper/dissertation parity divergence at the trunk attribution.**
The round softened the attribution in **both** texts and declared one deliberate divergence:
Chapter 5 states the disconfirming ablation with its numbers, the paper does not.
```bash
cd ../..
for f in articles/dissertacao/src/chapters/5_mobiwac/07_discussion.tex \
         'articles/[mobiwac]/src/sections/07_discussion.tex'; do
  grep -vn '^[[:space:]]*%' "$f" | grep 'One model serves both tasks' | sed "s|^|$f:|"
done
# EXPECT: lines=2
```
Two fixes to this command: the paper path was written relative to `articles/dissertacao/` and did not
resolve from where the rest of this list is run, and without the comment filter the paper file returns
an extra hit that is a section banner. Filtered, **one prose hit per file** is the answer.
*If all is well:* the same sentence opens both (dissertation p. 73), neither names a component as
the source of the category gain, and `articles/[mobiwac]/ERRATA.md` carries the four dated entries.
The declared divergence is a judgment you should endorse or reject, since it is your submitted
paper.

> **ROUND 8, 2026-07-30 — the parity holds; the JUDGMENT is still open.** The block returns exactly
> one prose hit per file, `5_mobiwac/07_discussion.tex:12` and `[mobiwac]/src/sections/07_discussion.tex:13`,
> both opening "One model serves both tasks." Neither names a component as the source of the category
> gain: the dissertation closes the paragraph with "Which part of the joint architecture produces the
> category gain is not settled by the controls reported here", and the paper carries the same sentence.
> The declared divergence is visible in the same two lines — the paper stops there, the dissertation
> continues into the disconfirming ablation with its numbers. `articles/[mobiwac]/ERRATA.md` exists and
> carries dated entries. The sentence prints on **p. 75** of the defense build, not p. 73.
> **Endorsing or rejecting the divergence is an author judgment about a submitted manuscript, so no
> agent action was taken.**

**13. The `+0.001` gradient-cosine sentence, fixed for parity in both texts.**
```bash
for f in $(grep -rl 'three of our six\|three of six' src/ '../[mobiwac]/src/' 2>/dev/null); do
  grep -vn '^[[:space:]]*%' "$f" | grep 'three of our six\|three of six' | sed "s|^|$f:|"
done
# EXPECT: lines=0
```
Comment lines are dropped before the search. Unfiltered this returns **5 hits, every one an audit
comment** recording the old wording, which is the opposite of the "zero" the expectation states — the
filtered form returns nothing, which is what "zero prose hits" means.
*If all is well:* **zero prose hits** (only audit comments mention the old wording — I verified
this), and both texts read "four Gowalla states … Alabama, Arizona and Florida, which are three of
the five United States datasets reported here, and Georgia, which this study does not otherwise
use". I did **not** re-derive the cosine value itself; that number remains on the protocol pass's
authority.

> **ROUND 8, 2026-07-30 — VERIFIED. Zero prose hits, and confirmed by a second, wider instrument.**
> The documented block returns nothing. Independently, a comment-stripped sweep for
> `three of our six|three of six` over every `.tex` in `articles/dissertacao/src/` **and**
> `articles/[mobiwac]/src/` returns 0 sites, which is the stronger form of the same claim (the block
> only searches files that `grep -rl` matched raw, so a file whose only hit was in a comment is still
> opened and then correctly yields nothing). Both texts read as the item quotes them, with the
> dissertation saying "this dissertation does not otherwise use" and the paper "this study does not
> otherwise use" — a deliberate register difference, not a parity break. The cosine value itself: item 0
> above **did** re-derive it this round against
> `WHY_ORTHOGONAL_AND_NO_MODERN_OPTIMIZERS.md:29-31`, so the caveat this item ends on ("remains on the
> protocol pass's authority") is now discharged for the `+0.001` pooled figure and for the `+0.0032`
> maximum that replaced the false bound.

---

## Tier 3 — traceability and hygiene (items 14-20)

**14. The `nash` page range, the one identifier nobody could resolve.**
`references.bib` gives `pages = {16428--16446}`. Crossref has no DOI for the ICML version, OpenAlex
returns only the preprint with null pages, Semantic Scholar confirms ICML 2022 but no pages, and
`proceedings.mlr.press` and `dblp.org` are both outside the sandbox allowlist. *One click closes
it:* `proceedings.mlr.press/v162/navon22a.html`. *If all is well:* the range matches, or you drop
the field — which is the precedent this same bibliography set for `standley2020tasks`. `[VERIFY]` V-5.

> **ROUND 8, 2026-07-30 — RE-ATTEMPTED AND STILL UNRESOLVABLE FROM HERE. The `[VERIFY]` stands.** The
> entry is unchanged (`@inproceedings{nash, ... booktitle = {Proc. ICML}, pages = {16428--16446},
> year = {2022}`). Two sources of record queried this session:
> **OpenAlex** returns exactly one work for the title, `W4225981399`, typed `preprint`, venue "arXiv
> (Cornell University)", `doi 10.48550/arxiv.2202.01017`, with `first_page` and `last_page` both
> **null** — the ICML version is not a separate record there. **Crossref** `query.bibliographic` returns
> five works, none of them this paper (top hits are bargaining-theory economics papers), so there is no
> registered DOI for the proceedings version to carry a page range. `proceedings.mlr.press` is not on
> the sandbox allowlist and was not fetched. **So the page range remains unverifiable by any
> automatable route**, and per §1 it may not be presented as checked. The one click still closes it, and
> the decision is the author's: confirm the range or drop the field, following the
> `standley2020tasks` precedent. Handed over as `PENDENCIAS.md` §2.14.

**15. `ruder2017sluice` is the third preprint entry, and it was not upgraded.**
The entry's title is the superseded preprint title ("Sluice Networks…"); the arXiv title of record
is "Latent Multi-task Architecture Learning" and the version of record is AAAI 2019
(`10.1609/aaai.v33i01.33014822`, v.33 pp. 4822-4829). I resolved both. *If all is well:* you take
the metadata decision **together with** the claim decision at the same key (it carries the round's
highest-load NOT-SUPPORTED verdict, `chapters/3_cbic/method.tex:91`) so the entry is touched once.
Ledger finding L-3.

> **ROUND 8, 2026-07-30 — verified and handed over INSIDE item 16 below, deliberately.** This item asks
> for the two decisions at this key to be taken together, so splitting the verdict across two rows
> would be the opposite of what it requests. The metadata half is unchanged and still resolves as
> stated (`.bib` title is the superseded preprint one; title of record "Latent Multi-task Architecture
> Learning", version of record AAAI 2019, `10.1609/aaai.v33i01.33014822`, pp. 4822-4829). The claim
> half is measured in item 16. Both are in `PENDENCIAS.md` §2.15 as one decision.

**16. Three claim-support verdicts on published prose you have not yet ruled on.**
`chapters/4_courb/methodology.tex:126` (`sun2020go` cited for temporal cycles revealing place
*function*), `:184` (`belkin2003laplacian` cited for a hierarchical embedding regularizer), and
`chapters/3_cbic/method.tex:91` (`ruder2017sluice` cited for hard-sharing regularization). All three
are NOT-SUPPORTED at high load, all three are in reproduced published prose, so all three are
errata decisions rather than free edits. *If all is well:* each gets a ruling and, if changed, an
Appendix B row. The suggested swaps (`baxter2000model`, `Xu2023`) are already in the bibliography
and already cited for those claims elsewhere.

> **ROUND 8, 2026-07-30 — ALL THREE SITES ARE STILL AS DESCRIBED, ALL THREE STILL UNRULED, and the
> coordinates have drifted.** Located by phrase, comments stripped: `ruder2017sluice` is cited for
> "By constraining the hypothesis space, hard sharing acts as a regularizer, often leading to more
> generalizable models, especially when tasks are related" (`3_cbic/method.tex`); `sun2020go` for
> cyclical regularities carrying "discriminative information about the functional nature of the visited
> POIs" (`4_courb/methodology.tex:173` region); `belkin2003laplacian` for "a hierarchical regularization
> term ... between category and fclass" (`4_courb/methodology.tex:184`). Each key appears exactly once
> in its file. **No agent edit is admissible on any of the three** — they are reproduced published
> sentences, so a swap is an errata decision with an Appendix B row, which is precisely what this item
> reserves to the author. Handed over as `PENDENCIAS.md` §2.15, jointly with item 15, since
> `ruder2017sluice` is one key carrying both a metadata decision and a claim decision.
>
> **AND ONE FINDING THIS ITEM DID NOT RAISE, found while reading those two lines.** The banned term
> **`fclass` is in rendered prose three times**, all in `4_courb/methodology.tex` (`:173` twice in the
> Node2Vec paragraph, `:184` twice more in the regularizer sentence — four occurrences, three source
> lines), against `GLOSSARY.md:73`, whose note reads "In code this column is `spot`, renamed `fclass`
> at `hgi/preprocess.py:62`; **NEVER write `fclass` in prose**". Verified with the comment-stripping
> sweep over all 54 `.tex` files: `4_courb/methodology.tex` is the only file, and the registered term
> "fine class" is what the appendix uses instead.
> ```bash
> cd articles/dissertacao
> python3 -c "
> import sys; sys.path.insert(0, 'src_utils')
> from pathlib import Path
> from check_audit_claims import live_text
> hits = {str(f): live_text(f).count('fclass')
>         for f in sorted(Path('src').rglob('*.tex')) if 'build/' not in str(f)}
> print({k: v for k, v in hits.items() if v})
> "
> # EXPECT: output={}
>
> **ROUND 9c, 2026-07-30 — THE EXPECTATION IS NOW AN EMPTY DICT, and that is the finding closed.**
> The author ruled on `PENDENCIAS` 2.15 by path A: fix the banned term in the original article trees
> and in the dissertation, and record it in the errata appendix. All three occurrences in
> `4_courb/methodology.tex` are replaced by the registered reader-facing name, **fine class**
> (`GLOSSARY.md:73`), set roman because it is ordinary English rather than a code token. The same
> replacement was applied to the published CoUrb sources, PT and EN, and an errata row is in Table B.3.
> Re-measured after the edit across all 54 live `.tex` files: `fclass` in rendered prose = **0**, and
> zero in the CBIC, CoUrb-PT, CoUrb-EN and MobiWac trees as well. The pattern was proved able to find
> the term when present (positive control: it is in `GLOSSARY.md`, which is where the ban is registered),
> so the zero is an absence and not a broken instrument.
> ```
> It is the **same class as items 15 and 16 and it goes to the same place**: the identical sentences are
> in the published CoUrb paper (`articles/CoUrb_2026/src_en/sections/metodology.tex:109` and `:120`),
> so removing the term edits a published sentence and is an errata decision, not cleanup. No gate covers
> it — the repo-codenames gate at `check.sh` matches `B9|v1[1-7]|champion-G|H3-alt|dk_ovl|log_T|substrate`
> and not `fclass`. Handed over inside `PENDENCIAS.md` §2.15.

**17. The Appendix B reconciliation count.**
The header now claims `8 + 13 + 4 + 18 = 43` itemized rows, replacing a stale `= 36`.
```bash
python3 - <<'PY'
import re
for f in ["src/tables/cbic/errata.tex","src/tables/cbic/errata_wording.tex",
          "src/tables/courb/errata.tex","src/tables/frame/bib_errata.tex"]:
    t="\n".join(l for l in open(f).read().splitlines() if not l.lstrip().startswith('%'))
    m=re.search(r'\\endlastfoot(.*?)\\end\{longtable\}',t,re.S) or re.search(r'\\midrule(.*?)(?:\\bottomrule|\\end\{longtable\}|\\end\{tabular\})',t,re.S)
    rows=[r for r in re.split(r'\\\\\s*',m.group(1)) if r.count('&')>=1 and r.strip() and 'multicolumn' not in r]
    print(f, len(rows))
PY
```
*If all is well:* 8, 13, 4, 18. I reproduced exactly this.

> **ROUND 8, 2026-07-30 — the second table is now 14, not 13, and the appendix and the tables agree at
> 44.** The block above returns **8, 14, 4, 18**. That is not a drift the appendix missed: the header
> claims 44, and `check_audit_claims.py`'s own record notes the round-8 change ("B.2 goes 13 -> 14 and
> the total 43 -> 44, with the COD-016a row"), so the source moved and the claim moved with it. This
> is now covered by a gate rather than by this block — `count_errata_rows.py`, run inside `check.sh`,
> prints per table and reconciles the total:
> ```
> ok  B.1  cbic/errata.tex          measured   8  claimed   8  (longtable)
> ok  B.2  cbic/errata_wording.tex  measured  14  claimed  14  (table)
> ok  B.3  courb/errata.tex         measured   4  claimed   4  (table)
> ok  B.4  frame/bib_errata.tex     measured  18  claimed  18  (longtable)
> ok  TOTAL                         measured  44  claimed  44
> ```
> Two independent instruments, one of them the item's own, agreeing on each row and on the sum. The
> `= 43` this item introduced is superseded; leave the block as written, since a stale expectation that
> a gate contradicts is exactly the signal a reader should get.

**18. The two errata rows and the claim they carry, as the reader sees them.**
Pages 93 (B.1, the Standley narrowing) and 96 (B.3, the Nash guarantee). *If all is well:* both rows
name the cited work's own position; the B.4 Sphere2Vec row **names the work rather than printing the
52-character key** (printing it produced the round's only overfull box, `113.58371pt`); and there
are **0 overfull boxes and 0 oversized floats** in all three builds — which I confirmed.

> **ROUND 8, 2026-07-30 — VERIFIED, at the new addresses.** The rows moved with Appendix B into the
> supplementary volume: B.1/Standley and B.4/Sphere2Vec are on `main_extra.pdf` **p. 14**, the Nash row
> on **p. 12** (defense pp. 93 and 96 no longer hold either row — see the build note at the top of this
> file). The B.4 cell names the work in prose, "The Sphere2Vec location encoder of Mai et al.", with no
> bare key printed, so the fix that removed the overfull box is intact. Boxes re-counted from the logs
> of all three defense-family builds:
> ```bash
> cd articles/dissertacao
> # `grep -c` exits 1 when the count is ZERO, which is the passing case here, so the count is
> # taken in python: a shell block that exits nonzero is a FAIL to the harness regardless of
> # what it printed. (My first version of this probe exited 1 with an empty stderr and was
> # correctly failed.)
> python3 -c "
> for stem in ('main', 'main_academico', 'main_ppgc'):
>     t = open(f'src/build/{stem}.log', errors='replace').read()
>     print(stem, 'overfull', t.count('Overfull'), 'hfootnote', t.count('Hfootnote'))
> "
> # EXPECT: lines=3
> # EXPECT: contains=main overfull 0 hfootnote 0
> # EXPECT: contains=main_ppgc overfull 0 hfootnote 0
> ```
> **0 in all three.** (`Hfootnote` is also 0 in all three, which is item A5 below, so one probe
> settles both.)

**19. The Appendix B static-scope section, which makes a public statement about a published
co-authored result.**
Rendered p. 99, and **suppressible by commenting one `\input` line** at
`chapters/apx_b_errata.tex:407`, per your own condition. Its numbers reproduce: I recomputed the
fine-class counts from `data/checkins_by_state/*.parquet` and get 284 / 305 / 324 / 333 / 365 across
AL/AZ/FL/CA/TX with **zero** values spanning more than one category — exactly the range the section
states. *If all is well:* the numbers are right and the only open question is the one you reserved,
the advisor conversation. `[NEEDS SIGN-OFF]`.

> **ROUND 8, 2026-07-30 — RECOMPUTED INDEPENDENTLY FROM THE PARQUETS; all five counts and the
> ambiguity claim reproduce exactly.** Not re-read from the section: re-derived from
> `data/checkins_by_state/{Alabama,Arizona,Florida,California,Texas}.parquet` under the pipeline's own
> convention, which the section's provenance comment states and which is the whole reason the number is
> stable — the `spot` column (renamed `fclass` at `hgi/preprocess.py:62`), rows with a null category
> dropped (`:64`), then reduced to one row per `placeid` (`:75-80`):
> ```
> Alabama    claim 284  measured 284    fclass spanning >1 category: 0
> Arizona    claim 305  measured 305    0
> Florida    claim 324  measured 324    0
> California claim 333  measured 333    0
> Texas      claim 365  measured 365    0
> ```
> The section's "Not one is ambiguous" therefore holds at zero across all five states. **The instrument
> matters here and the section's comment is right to warn about it**: counting the per-check-in
> `spot_categories` JSON column instead, over raw rows without the `placeid` dedup, gives
> 284/306/325/334/**377** — the trap that produced a wrong "fix" to 377 on 2026-07-30. Counting distinct
> category URLs gives a third set again (284/304/322/331/372). Same file, three defensible-looking
> quantities, one of which the pipeline actually uses; §4b V3.
> The section is still `\input` at `chapters/apx_b_errata.tex:448` (not `:407`) and remains suppressible
> by commenting that one line. **The numbers are closed. The `[NEEDS SIGN-OFF]` is not** — the advisor
> conversation about a public statement on a published co-authored result is yours, and it is item 2.4
> of `PENDENCIAS.md`.

**20. Sixty-three percent of this round's report coordinates now point past the end of their file.**
279 of 443 `file:line` references across the fifteen `_history/_round6/*.md` reports land past EOF, because
the split reduced `3_cbic.tex`, `4_courb.tex` and `5_mobiwac.tex` to 55, 42 and 50 lines.
*If all is well:* you do not fix those reports. Use `SOURCE_LEDGER.md` tables A and B and this file
as the current address book — every load-bearing coordinate there was re-resolved by phrase against
the split tree on 2026-07-28 — and hold future reports to `ANCHORS.md` §5: cite the phrase, date the
line number. Ledger finding L-6.

> **ROUND 8, 2026-07-30 — RE-MEASURED: 270 of 656, which is 41 percent, not 63.** Swept across the 26
> `_history/_round6/*.md` **reports** (the item says fifteen; the directory has grown, and this file is excluded
> from its own denominator — it is the address book, not a report), resolving each `file.tex:line`
> against `src/`, `src/chapters/` or the path as written, and counting only those that resolve to a real
> file.
>
> **This measurement is deliberately NOT in a runnable block, and the reason is a hazard worth knowing.**
> The natural way to write it compares a line number against a file length with `>`, and
> `check_verify_list.py`'s mutation guard reads every `>` whose target is not `/dev/null` as a write —
> correctly, since it cannot tell a comparison from a redirect without parsing shell. My first draft of
> this probe was refused on exactly that ground. **The right response is to keep the block out of the
> fence, not to loosen the guard**: a guard that has to distinguish `a > b` from `a > file` is a guard
> that will eventually let a real write through. The script, for a human to run from
> `articles/dissertacao/`, phrased with the comparison reversed so it reads as a filter rather than a
> redirect:
>
>     python3 -c "
>     import re
>     from pathlib import Path
>     tot = past = 0
>     for md in sorted(Path('src_utils/_round6').glob('*.md')):
>         if md.name == 'VERIFY_LIST.md': continue
>         for m in re.finditer(r'([\w/\[\].-]+\.tex):(\d+)', md.read_text(errors='replace')):
>             cands = [Path('src')/m.group(1), Path('src/chapters')/m.group(1), Path(m.group(1))]
>             f = next((c for c in cands if c.exists()), None)
>             if f is None: continue
>             tot += 1
>             nl = len(f.read_text(errors='replace').splitlines())
>             past += nl < int(m.group(2))
>     print('resolvable', tot, 'past_eof', past)
>     "
>     resolvable 656 past_eof 270
>
> The **disposition is unchanged and correct: do not fix the reports.** Two notes for whoever reads a
> round-6 coordinate next. The denominators differ because the two sweeps counted different things —
> 443 was every `file:line` string, 656 is every one that resolves to a file that exists — so the two
> percentages are not comparable and neither is wrong; this is the R4 shape (a filter that does not
> match the question asked), recorded rather than reconciled. And the rot has since spread past the
> chapter split that caused it: this file's own page numbers went stale in round 7 when eight pages of
> appendix left the defense build, so **a stale coordinate here is now as likely to be a page number as
> a line number.** `ANCHORS.md` §5 covers both: cite the phrase, date the number.

---

### Two things deliberately NOT on this list

- **The 43 `[NEEDS SIGN-OFF]` markers as a set.** Six are this round's and are covered above (items
  2, 3, 7, 12, 19, plus the "identically" narrowing at p. 74). Reading all 43 is a separate pass,
  not a spot check.
- **The 25-row citation failure table as a whole.** Ten of its rows are low-load PARTIALs in
  reproduced prose, dispositioned "leave and record". Items 16 and 15 above pull out the four that
  carry real weight. The full table, with every identifier resolved and every site re-anchored, is
  `SOURCE_LEDGER.md` §A.3.

### One flag you should not re-raise

"The CA and TX category cells are provisional and the frame does not say so" was raised, checked,
and **withdrawn** — correctly. `stats_n20/RESULTS.md` is at rev 4 (2026-07-13) and reports all six
datasets rejecting at α = 0.05 (CA +6.45, TX +7.45, Holm-adjusted p = 8.9e-07); the provisional
material sits under a heading that literally begins `## 1b · … (✅ A1 n=20 now COMPLETE`. I
re-verified this independently. **"At all six" is correct.** The lesson worth keeping: that record
retains its superseded revisions inline, so anchor on the revision header, not on the first matching
line.

---

# Addendum: the seven items added after this list was written

**Appended 2026-07-28.** This list was written at `c5c6789d`, before the eight review tracks landed.
These seven come from what they found and what was changed in response. Same ordering rule as above:
by consequence, not by chapter order.

### A1. The corrected Appendix B paragraph on Chapter 3 — highest consequence in the document

**What to check.** That the paragraph says what you want said about Chapter 3, because it no longer
says what your 2026-07-27 ruling assumed.

**Where.** Defense PDF **p. 99**, section B.5, the paragraph beginning "The second is that the two
chapters differ in how direct the channel is". Source `src/chapters/apx_b_static_scope.tex`.

**How.** Read the paragraph. Then, if you want the mechanism checked rather than taken:

```bash
sed -n '114,131p' ../../research/embeddings/dgi/preprocess.py    # the feature: neighbours' mean, self excluded
sed -n '28,30p'  ../../research/embeddings/hgi/model/POIEncoder.py  # a single GCNConv, self-loops on by default
```

**What the answer should be if all is well.** The paragraph should say the two chapters differ in
**degree**: CoUrb's channel is an exact deterministic lookup, CBIC's is a neighbourhood average that
returns diluted through one convolution. It should **not** say Chapter 3 is unaffected. Your ruling
said "esse nao se aplica ao DGI que usamos no cbic"; the measurement says the channel there is
indirect, not absent. If you want the stronger exculpation, it cannot be supported as written.

> **ROUND 8, 2026-07-30 — the paragraph says exactly this, though not in the words this item quotes.**
> It has been rewritten since; the opening is now "The second is that Chapter 3 has a version of the
> same problem, milder but present, and saying so is more honest than drawing a line between the two",
> so a search for "how direct the channel is" returns nothing and the paragraph is still there. It
> carries the mechanism the item requires: the DGI feature "deliberately leaves the place itself out,
> which looks like it closes the channel. It does not. The place graph is undirected, so a place appears
> in its own neighbors' features, and a single graph convolution averages a place together with its
> neighborhood. The place's own label comes back at the first hop, diluted among its neighbors." And it
> lands on the required verdict verbatim: "The difference between the two chapters is therefore one of
> degree: an exact lookup in Chapter 4, a diluted average in Chapter 3." The one occurrence of
> "unaffected" is in a different clause ("The first is that the sequential task is unaffected"), not an
> exculpation of Chapter 3. It prints in the supplementary volume, `main_extra.pdf`, section B.5 — not
> defense p. 99. **The reading is the author's to endorse; the text is not what his 2026-07-27 ruling
> assumed, which is what this item exists to surface, and that remains true.**

### A2. The bounded Ch.4 number in the conclusion

**What to check.** That the two added sentences say what you would say.

**Where.** Defense PDF **p. 76**, from "Two qualifications bound what that number licenses".

**What the answer should be.** The 20.2 to 22.0 point figure stays (it is the published chapter's own
audited number), now labelled as the **static task's** and pointing at Appendix B; and the arc's
diagnosis should rest on the sequential task, naming Chapter 5 as what tests it.

> **ROUND 8, 2026-07-30 — VERIFIED.** Both sentences are in `chapters/6_conclusion.tex` and print on
> **p. 74** of the 100-page defense build (this item says p. 76). The figure stays and is bounded
> exactly as prescribed: "raised category macro-F1 by 20.2 to 22.0 percentage points across the three
> states tested", then "Two qualifications bound what that number licenses. It is measured on the
> **static task**, which classifies a place from that place's own representation, and **Appendix B of
> the supplementary volume** records that this task's input determines its target by construction, so
> the figure is not evidence about the sequential task." The second qualification is the width
> mismatch, 192 against 64. The arc's diagnosis then rests on the sequential task in the following
> sentence. Nothing here needs the author beyond reading it.

### A3. The weakened reproducibility sentence

**What to check.** Whether you would rather publish the **nine** missing files than weaken the
sentence. Appendix A cites **thirteen** paths; four are already public.

**Where.** Defense PDF **p. 88**; source `src/chapters/apx_a_contributions.tex`.

**How.** Check all thirteen at once, so the four that are already there are visible too:

```bash
cd ../..
S=docs/studies/closing_data/v17_completion/stats_n20
for p in src/data/folds.py \
         scripts/closing_data/score_joint_best.py \
         scripts/closing_data/superiority_wilcoxon.py \
         scripts/closing_data/region_match_tost.py \
         docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md \
         scripts/build_phase3_per_fold_transitions.sh \
         docs/studies/closing_data/joint_best/JOINT_BEST_RESULTS.md \
         "$S" "$S/m1_stats_n20.py" "$S/m2_prereg_perfold.py" \
         "$S/m1_full_output.txt" "$S/m2_prereg_output.txt" \
         scripts/embedding_eval/autocorrelation_ceiling.py; do
  printf "%-70s " "$(basename "$p")"
  git cat-file -e "mobiwac:$p" 2>/dev/null && echo PRESENT || echo ABSENT
done
# EXPECT: lines=13
```

**What the answer should be.** The **first four PRESENT**, the **remaining nine ABSENT**. Push the
nine and the strong sentence comes back; the instruction is in the `[round6, F-01]` comment at the
site.

> **Two corrections to this item, 2026-07-28 (`c6e62c62`).** It first said "the eight files" and its
> command listed only eight, omitting `m1_full_output.txt` — a line-based grep of the appendix missed
> it, because it shares a source line with another `\path{}`. The command was also wrong in a way
> that would have looked right: it queried the four bare filenames at the repository root, where they
> do not exist in any branch, so they would have reported ABSENT for the wrong reason. They live
> inside `stats_n20/`, and the command above gives their full paths.

> **THIRD CORRECTION, ROUND 8, 2026-07-30 — the command still answers the wrong question, and the
> answer by content is EIGHT of thirteen present, not four.** Run as written it prints 6 PRESENT and 7
> ABSENT, which matches neither the "four/nine" the item states nor the "five still absent" the
> appendix comment records. The reason is the one already written into `apx_a_contributions.tex`:
> `git cat-file -e mobiwac:<path>` asks *is this PATH in the branch*, and the claim is *is this FILE in
> the branch*. The `mobiwac` branch has **no `docs/` tree** and keeps these artifacts under
> `analysis_protocol/`, so byte-identical files read as absent. Re-measured by hashing each local file
> and looking the object up among the branch's blobs (the four bare filenames resolved into
> `stats_n20/` first, as the second correction requires):
>
>     ON BRANCH, BYTE-IDENTICAL (8): src/data/folds.py; STATISTICAL_PROTOCOL.md and
>       JOINT_BEST_RESULTS.md and m1_full_output.txt and m2_prereg_output.txt (all under
>       analysis_protocol/); scripts/build_phase3_per_fold_transitions.sh;
>       scripts/closing_data/score_joint_best.py; autocorrelation_ceiling.py (at scripts/, not
>       scripts/embedding_eval/)
>     NOT ON BRANCH BY CONTENT (4): superiority_wilcoxon.py, region_match_tost.py,
>       m1_stats_n20.py, m2_prereg_perfold.py
>     DIRECTORY, unclassifiable by a file-hashing instrument (1): stats_n20/
>
> **All four of the "not on branch by content" files are on the branch at their own paths with
> DIFFERENT content**, which is a materially different situation from missing and is the one the author
> already reserved to himself in `PENDENCIAS.md` §2.2: `superiority_wilcoxon.py` 147 local lines against
> 126 published (37 differing lines), `region_match_tost.py` 74 against 74 (2 lines),
> `m1_stats_n20.py` 411 against 335 (84), `m2_prereg_perfold.py` 214 against 222 (36). So **nothing is
> missing from the public branch; four published artifacts have diverged from the working copies.**
> Replacing a published artifact with a divergent local version is an author decision, not cleanup, and
> §2.2 already says so for two of the four — it now covers four (`PENDENCIAS.md` §2.16).
>
> This is the **fourth** count this one item has produced (9 of 13, then 5 of 13, then 4-of-13
> by-path, now 8 of 13 by content), and every revision came from an instrument answering a narrower
> question than the claim built on it. §4b V3, V6. The count that matters for the prose is **zero
> genuinely absent**, and the prose is already scoped to what is true either way: the appendix says the
> statistical scripts "are part of the working repository and are supplied on request", which no
> reading of these numbers falsifies.
> **The block above is left exactly as written.** It is the by-path question, it is correctly labelled
> in this note, and rewriting it to the by-content form would put a `git hash-object` loop into a
> harness-executed block for no gain — the finding is recorded here in full.

> **ROUND 9, 2026-07-30 — CLOSED BY EXECUTION, not by a decision.** The question this item asks (publish
> the missing files, or weaken the sentence) was overtaken: the files were published. Verified against the
> REMOTE, not a local branch: `git fetch origin mobiwac && git ls-tree -r origin/mobiwac --name-only`
> lists 555 files and all six of the analysis artifacts this item turns on are among them --
> `m1_stats_n20.py`, `m2_prereg_perfold.py`, `autocorrelation_ceiling.py`, `score_joint_best.py`,
> `superiority_wilcoxon.py`, `region_match_tost.py`. The sentence in `apx_a_contributions.tex` therefore
> does not need weakening and the author has no decision left to take here.
> The earlier count in this item ("nine missing, four already public") was superseded twice, first to five
> and then to three, each time by auditing CONTENT rather than filename: files existed on the branch under
> a different directory, and two differed in content and were deliberately left alone as the author's call
> (`PENDENCIAS` 2.16). The history is in that item; the arithmetic here is stale by design and is left
> rather than rewritten, since re-deriving it would only re-answer a closed question.

### A4. The deposit build's page numbering

**What to check.** That each build prints its own physical page number.

**How.** This compares the printed number against the physical position for you, rather than asking
you to eyeball three PDFs:

```bash
python3 - <<'PY'
import pypdfium2 as pdfium, re
for stem in ("main", "main_academico", "main_ppgc"):
    d = pdfium.PdfDocument(f"src/build/{stem}.pdf")
    for i in range(min(20, len(d))):
        t = d[i].get_textpage().get_text_range()
        m = re.match(r'\s*(\d{1,3})\s', t) or re.search(r'\n\s*(\d{1,3})\s*$', t)
        if m:
            got = int(m.group(1))
            print(f"{stem:11s} first numbered page: physical {i+1:3d} prints {got:3d}  "
                  f"{'OK' if got == i+1 else 'MISMATCH'}")
            break
PY
# EXPECT: lines=3
# EXPECT: contains=main        first numbered page: physical  13 prints  13  OK
```

**What the answer should be.** Three `OK` lines: `main` physical 12 prints 12, `main_academico`
physical 9 prints **9**, `main_ppgc` physical 13 prints 13. Before this round the deposit build
(then `main_final`) printed 11 on physical page 8, and every page after it inherited that three-page
error. Run `make defense && make academico && make ppgc` first if `src/build/` is stale.
(The deposit target was renamed `final` -> `academico` on 2026-07-29, LATEX_UPGRADE.md §4 A-1; the
command above is executed by `src_utils/check_verify_list.py`, so the stem here is live tooling and
not a frozen record.)

> **ROUND 8, 2026-07-30 — VERIFIED: three `OK` lines, and the prose numbers here were one page stale
> in all three builds.** Measured output:
> ```
> main        first numbered page: physical  12 prints  12  OK
> main_academico first numbered page: physical   9 prints   9  OK
> main_ppgc   first numbered page: physical  13 prints  13  OK
> ```
> The `# EXPECT: contains=` annotation on the block already carried `physical  12 prints  12`, so the
> executable half was right and only the **prose** said 11 / 8 / 12; the prose is corrected above. That
> asymmetry is the useful part: the annotated line is re-read on every `make check` and the sentence
> beside it is not, which is why an expectation belongs in the block rather than in the paragraph. The
> property the item cares about — printed number equals physical position, no inherited offset —
> holds in all three, on builds of 100, 97 and 101 pages.

### A5. The footnote links

**What to check.** That clicking a footnote mark no longer jumps to page 1.

**How.** `grep -c Hfootnote src/build/main.log src/build/main_academico.log src/build/main_ppgc.log`,
then click a footnote mark in the PDF.

**What the answer should be.** **0** in all three logs, and the mark should be plain text with no link.

> **ROUND 8, 2026-07-30 — VERIFIED.** `Hfootnote` count is **0** in all three logs (`main`,
> `main_academico`, `main_ppgc`), counted in python rather than with the `grep -c` this item
> prescribes: that command exits 1 on a zero count, which is the passing case here, so as an
> automated check it fails while reporting the right number. The python form is annotated under item
> 18 above, so both properties are checked on every `make check` rather than only when someone runs
> this block by hand. Clicking a mark to confirm it is plain text is the human half and is not
> automatable here.

### A6. The gate suite, including the four new gates

**How.**

```bash
cd articles/dissertacao && source src_utils/texenv.sh && (cd src && make check); echo "RC=$?"
# EXPECT: contains=RC=0
```

**What the answer should be.** **RC=0** — for the first time this round; it exited 2 throughout while
six commit messages said otherwise. You should see `OK: 54 .tex files, every root directive present and
resolving`, `negative parallelism: ... 3.35 per 1k (ceiling 3.60)`, `OK: no doubled reference macros in
54 files`, and `trapped-prose suspects: 0`. Each of the four new gates self-tests in both directions
before it reports; if one prints only OK and no self-test line, distrust it.

> **ROUND 8, 2026-07-30 — VERIFIED RC=0, and three of the four expected strings had drifted.** The
> suite is now **22 gates, 2.047 s total**, every gate under the 5 s threshold. Measured strings, with
> the stale value this item carried:
> ```
> OK: 54 .tex files, every root directive present and resolving          (item said 49)
> negative parallelism: 120 instances / 35844 prose words = 3.35 per 1k  (item said 3.19)
> OK: no doubled reference macros in 54 files                            (item said 49)
> trapped-prose suspects: 0                                              (unchanged)
> ```
> The prose above is corrected. None of these is a defect: the file count grew with the chapter split
> and the appendix move, and the parallelism density stayed under its 3.60 ceiling. **The instruction
> in the last sentence is worth keeping and is now stronger than it reads.** `selftest_all.py` classifies
> the fourteen checkers by *sabotage* rather than by whether a `def self_test` exists, and reports
> **PROVEN 3, FAILED 0, UNPROVEN or HALF 11 of 14** — so "distrust a gate that prints only OK" is not a
> hypothetical: eleven of the fourteen currently have no fixture proving they fire on their own defect.
> That inventory is `PENDENCIAS.md` §2.10 and is the author's to prioritize.

### A7. The 46 sign-off markers, three of them first

**How.** `grep -rn "NEEDS SIGN-OFF" src/ | wc -l` should give 46. The by-file inventory is in
`PENDENCIAS.md` §2.1.

**What the answer should be.** Read A1, A3 and A2 above before the other 43. Those three are the ones
where the round changed what the document claims rather than how it says it.

> **ROUND 8, 2026-07-30 — the count is not 46, the command as written over-counts, and the number is
> NOT STABLE ENOUGH TO ASSERT. What is assertable is the over-count.**
> ```bash
> cd articles/dissertacao
> python3 -c "
> import subprocess
> def n(args):
>     return len(subprocess.run(['grep', '-rn', 'NEEDS SIGN-OFF'] + args,
>                               capture_output=True, text=True).stdout.splitlines())
> with_build, source_only = n(['src/']), n(['src/', '--exclude-dir=build'])
> print('inflated_by_generated_build_copy', with_build - source_only)
> print('build_copy_is_generated', __import__('pathlib').Path('src/build/fmt/_body.tex').exists())
> "
> # EXPECT: contains=inflated_by_generated_build_copy 4
> # EXPECT: contains=build_copy_is_generated True
> ```
> The gap is **four markers in `src/build/fmt/_body.tex`, a generated file** that `src/.gitignore`
> excludes — the same four counted twice, once in the source and once in the formatter's copy. **Any
> count of these must pass `--exclude-dir=build`**; the bare command in this item does not, so every
> number it has ever produced was inflated by four.
>
> **Why the absolute number is deliberately not asserted here, which is the finding worth carrying.**
> I measured 53 in source, then 55 twenty minutes later in the same session. Nothing was wrong with
> either measurement: **a concurrent round-8 track added a `[NEEDS SIGN-OFF]` to
> `apx_b_errata.tex` while this file was open**, and two more arrived in commits that landed between my
> own (`3ef8dc8b`, `d9ab436f`). Pinning an exact total in an `EXPECT` would hand the author a gate that
> the next legitimate sign-off breaks. So the block asserts the structural defect, which is durable, and
> the count is recorded with its moment: **55 in source / 59 with `build/`, measured at `d9ab436f`,
> with one further marker uncommitted in the working tree.**
> This is `§4b V14` at the level of measurement rather than bookkeeping: in a parallel round a count is
> a reading at a timestamp, not a property of the repository, and it must be written down with both.
> The §2.1 inventory table is stale on the same account, and separately by structure — it lists
> `0_main.tex` with 4, a file that no longer exists; those four are now in `content.tex`. Since the
> markers are the author's queue rather than a claim in the document, the corrected count, the by-file
> breakdown and the `--exclude-dir=build` rule go to `PENDENCIAS.md` §2.13 rather than being edited into
> §2.1 by an agent.
> **The reading order this item recommends is unchanged and still right**: A1, then A3, then A2.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
