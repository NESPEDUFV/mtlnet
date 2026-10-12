# Appendix D explained — the label-only ceiling, and why it exists

**What this doc is:** a plain-language walkthrough of `src/chapters/apx_d_ceiling.tex`, written
because the appendix reads as isolated/context-free on its own. It reconstructs the chain of
reasoning from the big-picture question down to the specific numbers in the table, then proposes
how to rewrite the appendix itself so a first-time reader (the banca) doesn't need this doc to
follow it.

---

## 1. The big-picture question this whole thing answers

The dissertation's central empirical claim rests on one representation: **Check2HGI**, a graph
built over check-ins where each visit is a node and consecutive visits by the same user are joined
by an edge. Every downstream result — the next-category task, the next-region task, the joint MTL
model that is the dissertation's actual contribution — is a number computed *on top of* embeddings
this graph produces.

That structure creates one specific, physically plausible failure mode: **a visit's node carries
its own category as a feature, and that node is directly linked by an edge to the *next* visit's
node.** If the graph-training process lets information cross that edge in the wrong direction, the
embedding for visit *t* could end up encoding something about visit *t+1* — the very thing the
next-category task is supposed to predict from visit *t* alone. If that happened, "predicting the
next category" would partly be reading a value that was smuggled in, not predicting anything, and
every downstream number in Chapters 3–5 would be inflated by an unknown amount.

So before trusting any of the downstream numbers, the dissertation needs an answer to: **does this
specific edge leak the future into the past?** Section `sec:mobiwac:method-rep` in Chapter 5 lists
four possible leakage channels and audits each one. Appendix D is entirely about auditing this one
channel — the fourth one, the edge itself.

## 2. The audit ("the screen"), in plain steps

1. Take an embedding of **only the last visit in the input window** — no sequence model, no GRU,
   no Transformer stacked on top. Just that one vector.
2. Try to predict the next category from that single vector alone, with a simple linear/logistic
   probe.
3. Ask: how well *should* that vector be able to do this, if it only carries legitimate
   information about the past? If it does dramatically better than that, something is leaking
   through the edge.

This is called "the screen" because it runs on every candidate encoder during development, as a
gate: an encoder that clears some threshold gets flagged as a suspected leaker and thrown out
before it's used for anything else. This isn't hypothetical — it already caught something: an
attention-based (GAT) encoder screened at Florida scored 8.9 points above the reference level and
was disqualified. **The screen already did its job once; that's why it matters enough to document
carefully.**

## 3. Where the confusion crept in — two different numbers with one name

To decide "how well *should* it do," the original screen compared each candidate encoder against a
**clean reference encoder** from the same lineage (the plain GCN version), rather than against a
number computed directly from the labels. That reference encoder scored **~0.41 macro-F1** at
Florida. In places, the internal research record and the Chapter 5 draft called this reference
score **"the autocorrelation ceiling."**

That name is the problem. There are two genuinely different quantities here:

| Quantity | What it is | How it's computed | Florida value |
|---|---|---|---|
| **(a) The clean reference encoder's score** | What one specific trained encoder achieves on the last-slot-only probe | Run the actual encoder, then the linear probe | ~0.4090 |
| **(b) The label-only ceiling** | The best *any* predictor could do using *only* the genuine category history — no embedding involved at all | Four label-only predictors (persistence, one-hot logistic, count logistic, positional logistic), take the best | 0.3617 |

(b) is a property of the **label sequence itself** — it doesn't touch the encoder at all. (a) is a
property of **one specific encoder**. They answer different questions, and (a) is *higher* than
(b) by 4–6 points. Calling (a) "the ceiling" implies it's the theoretical maximum from past
information alone — but it isn't; (b) is. Appendix D exists to compute (b) properly, for the first
time, directly from the label sequences (`scripts/embedding_eval/autocorrelation_ceiling.py`), and
to stop conflating it with (a).

## 4. Why the gap between (a) and (b) is not, by itself, a scandal

Once (b) is computed, a new fact appears: **every encoder screened, including the "clean"
reference ones, scores above the label-only ceiling** — 0.4090 and 0.4197 against 0.3617 at
Florida, a 4–6 point gap.

Read carelessly, this looks like the same kind of evidence that got the GAT encoder disqualified.
It isn't, for a specific reason: **the label-only ceiling only lets a predictor see the category
history.** A real per-visit embedding is allowed to see much more than that — the identity of the
place itself, its neighborhood in the graph, the hour of the visit — and every one of those is
legitimate, forward-flowing information that can predict the next category without any information
crossing the edge backward in time. So a clean encoder scoring above the label-only ceiling is
expected and fine; a clean encoder scoring dramatically above *another clean encoder* (the GAT
case) is the actual red flag.

## 5. What Appendix D concludes, and what it changes

1. **The screen's own verdicts don't need revisiting.** They were always relative comparisons
   (encoder vs. encoder), and the GAT disqualification clears the reference by 8.9 points — far
   past the reference/ceiling confusion either way.
2. **The claim Chapter 5 makes has to be stated as the weaker, more defensible one:** the screen
   bounds encoders *against each other*, not against an absolute "no information beyond the past"
   standard. That's a narrower claim than "we verified this encoder carries no more than the past
   allows" — and it's the one that's actually true.
3. Two coverage caveats are logged: Texas can't be computed (the artifacts needed no longer exist
   under the shipped pipeline), and Istanbul has 196 ambiguous places (modal category used; the
   effect of dropping them is negligible, <0.001 macro-F1).

Net effect: **no result changes, no number in the main chapters changes.** What changes is the
precision of one methodological claim, closing a gap a careful reader (or an examiner) could
otherwise use to challenge the leakage-freedom argument. This is a paper-trail / rigor fix, not a
scientific finding.

## 6. Status

The appendix currently carries a `[NEEDS SIGN-OFF]` marker (lines 78–81 of the `.tex`) — it's new
prose from the 2026-07-26 round, not yet approved. The comment also names the fallback: keep only
the corrected Chapter 5 paragraph and drop the appendix entirely, if a standalone appendix isn't
wanted. This doc's existence is itself an argument for keeping the appendix but rewriting it — see
below.

---

## 7. Proposed reframe of Appendix D itself

**Diagnosis of why the current appendix reads as confusing in isolation:** it opens directly on
"the ceiling is a property of the label sequence, not of any encoder" — a corrective/negating
sentence that only makes sense to a reader who already holds the *wrong* belief it's correcting.
A reader who hasn't just read Chapter 5's footnote-dense paragraph has no wrong belief to correct,
so the opening reads as answering a question that was never asked. The appendix also never
restates *why* a label-only ceiling matters (the leakage-channel motivation from §1–2 above) before
diving into the four predictors and the table.

**Concrete restructuring proposal**, same content, reordered to build context before correcting it:

1. **New opening paragraph — the motivation, self-contained.** State the leakage channel first,
   in one paragraph, without assuming the reader remembers Chapter 5's phrasing: *Check2HGI links
   consecutive visits by an edge, and each node carries its own category as a feature; this creates
   a channel through which a visit's embedding could in principle absorb its successor's category.
   Chapter 5 audits this with a screen: predict the next category from the last window slot alone,
   and check that no encoder does so implausibly better than the "last category repeats" baseline.*
   This is the "why should anyone care" paragraph the current version skips.
2. **Second paragraph — define the two quantities explicitly, named and contrasted, before either
   one is used.** Introduce "the screen's reference score" (one encoder's achieved number) and "the
   label-only ceiling" (the label-sequence property this appendix computes) as a named pair up
   front, so the rest of the appendix can refer to them without re-deriving the distinction. Consider
   literally bolding both terms on first use.
3. **Then the current material, largely as-is:** the four predictors, the protocol, the table.
4. **Reframe the "two readings" section as "what this does and doesn't affect":** keep the content
   (screen's verdicts stand; the absolute reading is the weaker one now claimed) but state it as
   answering the two questions a skeptical reader would actually ask — *"does this undo the GAT
   disqualification?"* (no) and *"does the encoder-above-ceiling gap mean the shipped encoder
   leaks?"* (no, and here's the legitimate-information argument from §4 above) — rather than as
   abstract "two readings."
5. **Keep the coverage-limits paragraph (Texas, Istanbul) and the code/data pointers as-is** — they
   are already self-contained and clear.
6. **Optional but recommended: one sentence bridging back to Chapter 5 at the very end**, e.g. *"Chapter
   5 §method-representation cites this appendix in place of the earlier, conflated 'autocorrelation
   ceiling' terminology"* — so a reader who arrived here from a citation, or cold, both land somewhere
   oriented.

This reorder doesn't add new claims or numbers — it just front-loads the motivation and the
terminology contrast that today only exist implicitly (or in Chapter 5, several pages away), which
is exactly what made the appendix feel like it was dropped into the document mid-argument.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
