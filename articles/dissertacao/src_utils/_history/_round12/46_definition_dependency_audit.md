# 46_definition_dependency_audit.md — the author's four findings, measured before any redesign

Round 12, 2026-08-03. Measured against the live `chapters/2_fundamentals.tex` at the tree that follows
commit `0f231856`. Written BEFORE the consolidation work so the agents doing it argue from measurement.

## The twelve definitions, in source order (= rendered numbering)

| # | line | title | label |
|---|--:|---|---|
| 2.1 | 71 | Check-in | `def:fund:checkin` |
| 2.2 | 80 | Check-in history | `def:fund:history` |
| 2.3 | 116 | Category classification | `def:fund:catclf` |
| 2.4 | 126 | Next-category prediction | `def:fund:nextcat` |
| 2.5 | 133 | Next-region prediction | `def:fund:nextreg` |
| 2.6 | 167 | Next-place prediction | `def:fund:nextplace` |
| 2.7 | 434 | Place embedding | `def:fund:placelevel` |
| 2.8 | 461 | Check-in-level representation | `def:fund:checkinlevel` |
| 2.9 | 678 | Hard parameter sharing | `def:fund:hard` |
| 2.10 | 684 | Soft parameter sharing | `def:fund:soft` |
| 2.11 | 693 | Negative transfer | `def:fund:negtransfer` |
| 2.12 | 887 | Gradient conflict | `def:fund:conflict` |

## Finding 1 (MECHANICALLY CONFIRMED): a forward dependency, 2.3 -> 2.7

A dependency graph over the symbols each definition consumes against the definition that introduces
them gives exactly one violation of source order:

**Definition 2.3 (Category classification) uses $\mathbf{e}_p$, which Definition 2.7 (Place embedding)
introduces 318 lines later.** 2.3 states $g_{\mathrm{cat}}(\mathbf{e}_p) \longrightarrow c_p$ and its
own closing sentence refers again to "the graph used to learn $\mathbf{e}_p$", so the reader meets the
symbol, the task that consumes it, and a remark about how it is trained, three sections before the object
is defined.

Every other consumption is backward and legal: 2.2 uses $x_i$ from 2.1; 2.4, 2.5 and 2.6 use $H_i$ from
2.2 and their targets from 2.1; 2.8 uses $x_i$ from 2.1.

## Finding 2 (CONFIRMED FROM THE PAPER CHAPTERS): 2.2 defines the wrong element type

Definition 2.2 makes the history a sequence of **check-in tuples**: $H_i=(x_{i-\ell},\ldots,x_{i-1})$
where each $x$ is the 5-tuple of Definition 2.1. The models do not consume tuples. From
`chapters/5_mobiwac/04_method.tex` (a version of record, quoted):

- ":22 -- from the trained graph, we extract one 64-dimensional vector per check-in ... **so a model sees
  a sequence of per-visit vectors rather than repeated per-place ones**"
- ":27 -- we then train one model that **reads a window of recent per-visit vectors**"

So the sequential tasks consume a history of REPRESENTATIONS, and which representation depends on the
study: a per-visit vector in the final study, a per-place vector repeated across visits in the earlier
two. Definition 2.2 as written describes neither, and 2.4, 2.5 and 2.6 inherit the mismatch through
$H_i$.

## Finding 3 (CONFIRMED, and subtler than a rename): $\mathbf{e}_p$ versus $\mathbf{e}_{p_i}$

The author asks whether the place embedding should be $\mathbf{e}_{p_i}$ for a given place $p_i$. Both
forms are needed and they are not interchangeable, which is why this needs deciding rather than
substituting:

- **$\mathbf{e}_p$ is correct in Definition 2.3.** The static task is quantified over POIs, not over
  visits: it classifies a POI from that POI's own representation, and no check-in index exists in it.
  Writing $\mathbf{e}_{p_i}$ there would silently make a static task look sequential.
- **$\mathbf{e}_{p_j}$ is what a HISTORY position carries.** When the place-level input is fed to a
  sequential model, position $j$ of the window holds the embedding of the POI visited at check-in $j$,
  which is $\mathbf{e}_{p_j}$, the composition of $j \mapsto p_j$ (from Definition 2.1) with
  $p \mapsto \mathbf{e}_p$ (from 2.7). That composition is exactly the "every check-in at that POI enters
  the model with the same representation" clause of 2.7, stated in words rather than in symbols.

Measured: **no `\mathbf{e}_{p_i}`-style notation exists anywhere in the live tree today**, so nothing
depends on the choice yet.

## Finding 4 (CONFIRMED): 2.6 consumes the wrong history for the same reason as Finding 2

$f_{\mathrm{place}}(H_i) \longrightarrow p_i$ inherits whatever $H_i$ is. If $H_i$ becomes a sequence
of representations, 2.6 follows automatically; the finding is not separate from Finding 2, it is its
consequence at the fourth site.

## What this means for the chapter, stated as a constraint and not a solution

The definitions currently mix two levels: 2.1 and 2.2 are about OBSERVED DATA (tuples), 2.3 through 2.6
are about TASKS, and 2.7 and 2.8 are about REPRESENTATIONS, yet the task definitions consume
representations. Any repair has to decide where the map from data to representation lives, and it has to
keep three things that are already correct and gated:

1. **The three tasks stay formally distinct** (`GLOSSARY` §1, the chapter's stated job).
2. **The static task stays static.** Probe `R12-eqxi`, `R12-fplace`, `R12-fplace2` and the registry rows
   in `GLOSSARY` §1.1 pin the current symbols; any renaming updates the probes IN THE SAME COMMIT.
3. **The scope exclusion on next place survives** beside its function, per `R12-fplace2`.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
