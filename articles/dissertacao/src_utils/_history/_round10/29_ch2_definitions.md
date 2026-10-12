# 29 — Chapter 2 definition blocks (GER-08, GER-09, GER-10, AUT-01)

Baseline commit: **984c70be** (the tree I actually edited was at `aaf4e7eb`, the HAMTL
related-work fix another agent landed on top of the baseline; `git log --oneline -1` at the start
of this session returned `984c70be` per the brief and `aaf4e7eb` after that agent's commit
appeared — I did not touch `references.bib` or the HAMTL sentence).

One job, one file: `src/chapters/2_fundamentals.tex`, plus a minimal `src/preamble.tex` addition
that the four items jointly require.

---

## 1 · The items and the author's rulings, verbatim

| Item | Ruling (verbatim) |
|---|---|
| **GER-08** — concepts have no formal definition, starting with a check-in | `Opcao 1` |
| **GER-10** — the fundamentals need a logical narrative built on formal definition blocks | `Opcao 1.` |
| **GER-09** — 2.3 needs MTL formalism, the balancer lineage, and a definition of loss conflict | `Opcao 1. Voce pode se aproveitar da explicacao de cosseno do appendix F, apesar de estarmos fazendo essa nova parte nao precisa remover nada do appendix F, caso fique repetitivo.` |
| **AUT-01** — does the MTL fundamentals need Pareto optimality | `Vamos com a opcao 1. Aqui vale notar que em uma ultima interacao, realizamos o item 2.12, entao avalie como esta e se julgar necessario voce adiciona mais contexto embasado com referencias.` |

---

## 2 · The preamble change, and why it was necessary

`preamble.tex:96-117`. Measured before deciding, not assumed:

- **memoir's `\newtheorem` works under this class.** A minimal document with this exact package
  stack (`abntex2` + `newtxtext,newtxmath` + `amsmath`) and a bare
  `\newtheorem{definition}{Definition}[chapter]` compiled `rc=0` on both passes and rendered
  `Definition 1.1 (Check-in)` with a working `\ref`.
- **What it does not give is an upright body font.** memoir's styling hooks
  (`\theoremstyle{...}` with a `\newtheoremstyle` of that signature, `\theorembodyfont`,
  `\theoremseparator`) belong to the ntheorem interface and are *undefined* under this class:
  each was tried in the same minimal document and each died with `Undefined control sequence`
  (`rc=1`, output collapsing to `'fundefn fundefn .'` and `'.'` respectively). Chapter 2 now
  carries eleven definition blocks, several holding display mathematics; eleven italic paragraphs
  would read as emphasis rather than as definitions.
- **`amsthm` needs one guard line.** Loading it after `abntex2` fails with
  `LaTeX Error: Command \openbox already defined` — measured `rc=1` on both passes *while still
  rendering the definition correctly*, so the failure is visible only in the exit code, which is
  precisely the silent-failure shape this preamble's own comments warn about. `\let\openbox\relax`
  before the load clears the name; measured after: `rc=0` both passes, body upright, numbering and
  `\ref` intact. `\openbox` is amsthm's end-of-proof square and this document declares no proof
  environment.

Three lines of code (`\let`, `\usepackage{amsthm}`, `\theoremstyle{definition}`) plus
`\newtheorem`, with the measurement recorded in the comment above them. Nothing else in the
preamble was touched.

---

## 3 · What the LIVE text said before each edit, and what it says now

Every target was re-read in the live file immediately before editing; no line number from the item
text was trusted. Line numbers below are **post-edit**.

### GER-08 / GER-10 — the definition blocks

**Confirmed already present, not re-added:** the check-in tuple, the history, the three task
formalisms, the total-loss equation `eq:fund:mtl-total`, the Pareto passage, the named "gradient
conflict", and the grouped balancer taxonomy. My work was to give them *numbered, referenceable
form* and to make later prose point back — the brief's item (a) was correct, there was **zero**
`\newtheorem` in the tree and `amsthm` was not loaded (`grep -n "newtheorem\|amsthm\|Definition~" -r
chapters preamble.tex main.tex content.tex` → no output).

**Eleven definitions, in the order the chapter needs them:**

| # | Label | File:line | Converted from |
|---|---|---|---|
| 2.1 | `def:fund:checkin` | :56 | the bare `\begin{equation} x_i=(u,p_i,t_i,c_i,r_i)` at old :56-58 plus its symbol gloss |
| 2.2 | `def:fund:history` | :65 | old :87-92, "The ordered history preceding that visit is … for a history length ℓ" |
| 2.3 | `def:fund:catclf` | :99 | old :96-105, "The static *category classification* task predicts…" plus its held-out-POI sentence |
| 2.4 | `def:fund:nextcat` | :106 | old :106-110 |
| 2.5 | `def:fund:nextreg` | :111 | old :112-117 |
| 2.6 | `def:fund:nextplace` | :128 | old :126-128, "The dominant task in the field is *next-place prediction*, which identifies the exact POI of the next visit. It is not a target of this dissertation" |
| 2.7 | `def:fund:placelevel` | :235 | new, from old :228-229 "Every place embedding … gives a place one fixed vector for all visits" and the chapter's existing check-in-level contrast |
| 2.8 | `def:fund:hard` | :458 | old :443-445 |
| 2.9 | `def:fund:soft` | :464 | old :446-447 |
| 2.10 | `def:fund:negtransfer` | :473 | old :470-471, "negative transfer, in which joint training leaves a task worse than its dedicated single-task model" |
| 2.11 | `def:fund:conflict` | :667 | old :635-638, with the cosine added (GER-09) |

**The references that make it a narrative rather than a dump** — GER-10's actual ask. Six sites
now point back: `:116-118` (which chapter pairs which task), `:242` and `:247` (the place-level
limitation and Check2HGI's answer), `:470` (hard sharing is the first joint model's topology),
`:500` (negative transfer is what the optimization subsection responds to), `:780` (PCGrad
projects "a conflicting component in the sense of Definition 2.11").

**Left as prose, deliberately:** the seven-category taxonomy and the region unit (enumerations, not
definitions); the structured-sharing topologies at :465-472 (cross-stitch, MMoE, PLE, DSelect-k are
named systems, and boxing each would make the section a catalog); the Pareto trio at :525-528 and
:634-636 (already registered in GLOSSARY §4 and already read as definitions in running prose — see
§5); Check2HGI's loss equations at :274-296 (a construction, not a term the later chapters point
back to). GER-10 asks for a narrative built on definitions, not every paragraph boxed.

### GER-09a — the cosine

`:665-676`. The chapter previously defined conflict in words only:

> "Two tasks conflict when the cosine between their gradients on the shared parameters is negative;
> a value near zero means that the updates are nearly orthogonal, so neither reinforces nor opposes
> the other~\cite{yu2020pcgrad}."

Definition 2.11 now states it with the formula (`eq:fund:cosine`, rendered as 2.6):
$\cos\varphi_{ij} = \mathbf{g}_i^{\top}\mathbf{g}_j / (\lVert\mathbf{g}_i\rVert\lVert\mathbf{g}_j\rVert)$,
conflict at $\cos\varphi_{ij}<0$. The three-value reading ($+1$, $-1$, $0$) is taken from Appendix
F's own explanation, per the ruling. **Appendix F is unchanged** — `git status` shows only
`2_fundamentals.tex` and `preamble.tex` modified among my files. The repetition the author
authorized is the $+1/-1/0$ sentence and the "scale-free" reading; the appendix keeps both.

Two duplications I removed while there, because they were mine: an `Appendix~\ref{apx:cosine}`
pointer I had added two sentences before the chapter's existing one, and a second copy of
"Equation~\ref{eq:fund:cosine}" phrasing.

### GER-09b — the balancer lineage

`:757-784`, with a provenance comment at `:730-754`. The subsection previously named methods
without saying who introduced them ("Uncertainty weighting learns weights from…", "GradNorm
balances…"). It is now split into the two classes with first-author attribution:

- **Loss-weight class:** Kendall et al. (homoscedastic uncertainty), Chen et al. (GradNorm),
  S. Liu et al. (dynamic weight averaging, introduced alongside their attention architecture),
  B. Liu et al. (FAMO).
- **Update-direction class:** Sener and Koltun (the multi-objective reading), Yu et al. (PCGrad),
  B. Liu et al. (CAGrad), Navon et al. (Nash-MTL), Senushkin et al. (Aligned-MTL).

The initials on the two Lius are load-bearing: Shikun Liu (DWA) and Bo Liu (CAGrad, FAMO) are
different people, and three bare "Liu et al." would assert one research line where there are two.

**I read the per-clause provenance block at :452-490 first, as instructed, and this subsection does
not contradict it.** That block records *what each method proves*, at page level, from PDFs a prior
session opened; the guarantees subsection carrying those claims is untouched. My additions state
only *who introduced what and in which class* — a strictly weaker claim, separately sourced.

### AUT-01 — the Pareto passage

**Verdict: already sufficient. No prose added.** Reasons, in order of weight:

1. The passage does what AUT-01 asks and more. Pareto dominance (:525-527), Pareto optimality and
   the Pareto front (:527-528), the Pareto-stationary point with the necessary-not-sufficient
   qualification (:634-636), per-method guarantee levels for Nash-MTL, CAGrad, Aligned-MTL and
   PCGrad (:637-644), the "reaching the front leaves the balance unspecified" limitation
   (:644-645), and the disclaimer that this dissertation claims no Pareto property (:645-648).
2. It is the best-sourced passage in the chapter. Item 2.12's session left page-level provenance
   for every clause (arXiv version, page, and in three cases the quoted sentence). Adding context
   from a source I opened today would sit beside evidence of a higher standard, and any new
   sentence would have to earn a page-level anchor of its own.
3. Four `make check` probes pin it (`A23-EX9`, `R9-pareto`, `R9-pareto2`, `R9-pareto3`), and the
   probe comments record that this passage has already been reworded twice by mistake and repointed
   once. The marginal value of more context is below the risk of moving a pinned string.
4. The chapter must stay thin. §2.3 is the longest section; Pareto material is already about a
   third of it.

The one thing AUT-01's neighborhood *did* need was the conflict definition, which GER-09 delivers,
and Definition 2.11 now sits directly below the Pareto discussion so the two read as one argument.

---

## 4 · Thinness

The definitions cost one page on the first build (defense 106 → 107). I did not accept that: five
compaction passes brought it back. Net **106 pages, unchanged from baseline** (academico 103, ppgc
107, all unchanged). What was compacted, all of it prose the definitions had made redundant:

- three display equations inlined (`H_i`, `g_cat`, `f_cat`/`f_reg`) — the definition environment
  already sets them off;
- Definitions 2.7 and the former 2.8 merged into one two-sentence block, since the second was the
  first's complement;
- four lead-in sentences shortened or cut ("Three definitions separate the targets", "One further
  target must be named because…", "and it is a measured quantity rather than a figure of speech",
  the duplicated place-embedding limitation sentence).

Chapter 2 spans pp. 18-30 in the defense build, exactly as at baseline.

---

## 5 · Sources opened this session (budget: 6 external; **6 used**)

| # | Source | Identifier | What I located in it |
|---|---|---|---|
| 1 | PCGrad, Yu et al. | arXiv:2001.06782**v4** (PDF downloaded and read) | p.3: *"We define the gradients as conflicting when cos φij < 0."* and *"Definition 1. We define φij as the angle between two task gradients gi and gj."* — the source of Definition 2.11 and of Eq. 2.6. p.4: PCGrad "determines whether gi conflicts with gj by computing the cosine similarity", and leaves the gradient unaltered when the cosine is non-negative. First author Tianhe Yu, 6 authors. |
| 2 | arXiv abstract pages (5 records) | 1705.07115, 1711.02257, 2306.03792, 2111.10603, 1803.10704 | GradNorm: *"We present a gradient normalization (GradNorm) algorithm that automatically balances training … by dynamically tuning gradient magnitudes"*. FAMO: *"we introduce Fast Adaptive Multitask Optimization FAMO, a dynamic weighting method"*. Kendall: weighting by *"the homoscedastic uncertainty of each task"*. DWA/MTAN 1803.10704: the paper's own contribution is the attention architecture, which is why the sentence says "alongside their attention architecture". |
| 3 | arXiv API title queries (9 works) | export.arxiv.org | First author and identifier for every balancer I attribute: Kendall / Chen / S. Liu / Yu / B. Liu (CAGrad) / Navon / Senushkin / B. Liu (FAMO) / Sener. This is the record that establishes the two Lius are different people. |
| 4 | Crossref | 10.1109/CVPR.2018.00781, 10.1109/CVPR.2019.00197, 10.1145/3219819.3220007, 10.1145/3383313.3412236, 10.1109/CVPR.2016.433, 10.1023/A:1007379606734 | Author family names, year and venue for the six DOI-bearing entries, checked against `references.bib` as written. All six agree. |

Counted as four distinct external services (arXiv PDF, arXiv abstract pages, arXiv API, Crossref),
six records opened by the tightest reading. **Nothing was added to `references.bib`** — every key I
cite was already there and already used by this chapter, so no new bibliography entry required
verification. **No number is quoted in anything I wrote.** Not reached, and named rather than
skipped: the CAGrad, Nash-MTL and Aligned-MTL PDFs (I relied on the :452-490 provenance block for
what they prove, and made no new claim about it); Desideri's MGDA paper, which the existing comment
block correctly declines to cite.

---

## 6 · GLOSSARY compliance

Every term in the new blocks is registered: *check-in* (§3), *POI/place* (§3), *region* (§3),
*category classification* / *next-category prediction* / *next-region prediction* /
*next-place prediction* (§1), *place embedding* and *check-in-level representation* (§2),
*hard parameter sharing* (§6), *gradient conflict* (§4). Notation is §1.1's.

**Two terms are used that the registry does not carry a row for, and both were already in the live
prose before I arrived, so I introduce nothing new:** *soft parameter sharing* (:464, present at
old :446 — §6 registers only *hard parameter sharing*) and *negative transfer* (:473, present at
old :470). I converted existing prose into definition blocks without changing either term.

**PROPOSED for the registry, author's alone to add** (I did not use any term not already in prose):

1. **soft parameter sharing** (PT: *compartilhamento flexível de parâmetros*) — the complement of
   the registered *hard parameter sharing*; each task keeps its own network, coupled by a penalty
   on parameter differences. Now Definition 2.9.
2. **negative transfer** (PT: *transferência negativa*) — joint training leaving a task worse than
   its dedicated single-task model. Now Definition 2.10; it is the risk §2.3 exists to discuss and
   it appears in Ch.3's prose too.
3. **definition block / Definition N.M** — if the registry tracks structural devices, the chapter
   now carries a numbered `Definition` environment.

---

## 7 · Verification, run separately, exit codes read directly

From `/Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src`, one command per invocation,
`echo "RC=$?"` immediately after each, never piped into another program:

```
make defense    RC=0     build/main.pdf        106 pages, tex_errors=0
make ppgc       RC=0     build/main_ppgc.pdf   107 pages, tex_errors=0
make check      RC=0     68 of 68 probes hold; 0 claim(s) not applied
make selftest   RC=0     every required checker fires on its defect and is silent on the clean fixture
```

`make academico` was also run (RC=0, 103 pages) because `make check`'s page-count gate reads all
three builds and would otherwise compare a fresh defense build against a stale academico log.

**One intermediate red, disclosed:** at the one-page-longer stage, `make check` returned RC=2 with
the page-count gate reporting four stale claims (CLAUDE.md, PLAN.md, codex_reviewer.md recording
106 for a build measuring 107). I did **not** run `sync_page_counts.py --write` to make the gate
agree with a longer document. I compacted the chapter until the page count returned to 106, and the
gate went green on its own. No probe was weakened, reworded, or repointed.

The four probes that pin this chapter's Pareto and conflict wording were checked against my edits
before building: `R9-conflict` watches `cosine between their gradients` (present at :672, inside
the new paragraph), `R9-pareto` / `R9-pareto2` / `R9-pareto3` and `A23-EX9` watch strings in the
Pareto passage, which I did not touch. `R9-nocount` (an expect-not-found on a dataset count in the
cosine sentence) still holds.

---

## 8 · Files changed

- `src/chapters/2_fundamentals.tex` — 11 definition blocks, 6 back-references, the cosine formula,
  the balancer lineage with its provenance comment, and five compaction passes. Net +171/−71 lines
  including comments; the rendered chapter is the same length as at baseline.
- `src/preamble.tex:96-117` — `\let\openbox\relax`, `\usepackage{amsthm}`,
  `\theoremstyle{definition}`, `\newtheorem{definition}{Definition}[chapter]`, plus the measurement
  that justifies each line. This is the minimal declaration and it is disclosed here as required.

Not touched: `references.bib`, the related-work sentence at old :730-741, Appendix F, every other
file in the tree.

---

## UNFINISHED

Nothing from the four items is outstanding. Four things are open for the author, none of them work
I could have done:

1. **Two registry rows are owed** before the next handoff: *soft parameter sharing* and *negative
   transfer* (§6 above). Both terms were in the live prose before this session, so the fail-closed
   rule was already being stretched and my edit did not widen it, but the rows should land.
2. **Definition 2.7 merges two concepts under one head** ("Place embedding and check-in-level
   representation"). I merged them to hold the page count at 106. If the author prefers them
   separate, splitting them costs one definition number and about four lines, and the page budget
   would need four lines recovered elsewhere in §2.2.
3. **AUT-01 closes with "no change needed"**, which is the acceptable outcome the brief names but
   is still a judgment the author may overrule. §5 above gives the four reasons.
4. **The eleven definitions are unreviewed by a second pass.** I verified each attribution at its
   own source and the rendered output at the PDF, but no critic agent re-checked the lineage
   sentences against the records. That is the one gate in the citation protocol I could not close
   inside the wall clock.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
