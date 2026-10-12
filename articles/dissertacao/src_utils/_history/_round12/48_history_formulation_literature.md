# 48_history_formulation_literature.md — how the field actually formulates a check-in history

Round 12, 2026-08-03. The author asked whether the check-in history should be defined "in the traditional
sense, as I believe is typically done in the literature (this needs check and proof)", or directly as a
history of check-in embeddings, which is what the model consumes. He also asked whether following the
field's pattern buys credibility.

Four sources, every one OPENED THIS SESSION and quoted from its own text. This is the proof he asked for.

## The evidence

| source | how the sequence is defined | where the embedding enters |
|---|---|---|
| CSLSL, `huang2024cslsl`, EPJ Data Science 13:22 (2024), doi 10.1140/epjds/s13688-024-00460-7, PDF sheet 5 | Def 1 (Record) is the 3-tuple $(u_i,l_j,t_k)$; Def 2 (Individual Trajectory) is "a record sequence $R=\{r_1,r_2,\ldots,r_{|R|}\}$". The task is stated over it: "given a record sequence of a user $R_{t-1}=\{r_1,\ldots,r_{t-1}\}$, the goal is to predict where the user $u$ is most likely to go" | Section 4, Methodology: "an embedding part for learning the representations of arrival time, category, and location" |
| CTLE, `lin2021ctle`, AAAI 35(5) (2021), doi 10.1609/aaai.v35i5.16548, PDF sheet 3 | "a trajectory $s$ consisting of sequential visiting records", a visiting record being $(u,l,t)$ | The Problem Statement itself: "we aim to pre-train a parameterized mapping function $f$ to generate a contextual embedding vector $z(l)$ for a target location $l$ given its context $C(l)$" |
| HAMTL, `wang2025hamtl`, J. Supercomputing (2025), doi 10.1007/s11227-025-07643-7, PDF sheet 5 | Def 1 (Spatial-Temporal Point) is the pair $\langle l,t\rangle$; Def 2 (Trajectory) is a chronologically arranged set of those points | Not in either definition |
| **This dissertation's own MobiWac chapter**, `chapters/5_mobiwac/03_problem.tex`, a version of record | "Given a user's time-ordered check-in history, we predict two properties of the next visit." | `04_method.tex:22`, "we extract one 64-dimensional vector per check-in ... so a model sees a sequence of per-visit vectors rather than repeated per-place ones"; `:27`, "reads a window of recent per-visit vectors" |

## What the evidence says

**Four of four define the sequence over RAW OBSERVATIONS and introduce the representation afterwards, as a
mapping.** None defines the history as a sequence of embeddings. So the author's belief is correct, and it
is now checked rather than believed.

**The decisive case is CTLE**, because its entire contribution IS the location embedding and it still
keeps the two layers apart: the trajectory is over visiting records in Preliminaries, and the embedding is
a function $z(l)$ in the Problem Statement. A paper with every incentive to fold the representation into
the data model declines to.

**And the dissertation is already consistent with the field where it counts.** MobiWac's problem statement
is over the check-in history and its per-visit vectors live in the method. That chapter is a version of
record, so Chapter 2 defining the history over embeddings would put the fundamentals chapter at odds with
the paper it is supposed to be the background for.

## On the credibility question, stated as narrowly as the evidence allows

Following the field's layering does buy something real, and it is worth being precise about what:

1. **A reader who knows the field recognizes the objects immediately.** Record, trajectory, session,
   prediction target: a committee member reading Definitions 2.1 and 2.2 sees the same shape they have
   read in every next-location paper, and the dissertation's own contribution stands out against a
   familiar background rather than competing with it for attention.
2. **It keeps the DATA claim separable from the MODEL claim, which is this dissertation's whole thesis.**
   The argument is that the representation is the dominant factor. That argument is only expressible if
   the data is defined independently of the representation: three studies feed three different
   representations to the same task, and the task must be the SAME OBJECT across all three for the
   comparison to mean anything. Defining the history as a sequence of embeddings would make the task
   definition change between chapters, and the central claim would lose the fixed reference point it is
   measured against.
3. **It is the honest form for what the tasks actually are.** Next-category prediction is a problem about
   visits, not about vectors. The vectors are an implementation choice this dissertation varies on purpose.

What following the convention does NOT buy, and should not be claimed: it is not evidence of correctness,
it does not make the results stronger, and no reviewer credits a formulation for being conventional. The
gain is legibility and a defensible separation of claims, not merit.

## The design consequence

The fix for the author's finding 2 is therefore NOT to redefine $H_i$ over embeddings. It is to keep
$H_i$ as the sequence of check-ins (the field's form, and MobiWac's) and to introduce the map from a
check-in to its representation as a NAMED FUNCTION before the tasks consume it, so that a place-level
input and a check-in-level input are two instantiations of one encoder rather than two different task
definitions. That is what CTLE does with $z(l)$ and what CSLSL does with its embedding part, and it
resolves the forward dependency of finding 1 at the same time.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
