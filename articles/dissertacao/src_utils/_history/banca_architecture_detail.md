# 12 · Banca simulator — single-charge review: is the architectural detail on Check2HGI and MTLnet sufficient?

> **Persona:** 12, banca simulator (`reviewers/12_banca_simulator.md`) — a UFV/PPGCC examiner
> pre-reading the defense build.
> **Charge:** ONE question, the author's own. Not a re-review of the document.
> **Build under review:** `src/dissertacao.pdf`, 104 pp, rebuilt 2026-07-27.
> **Protocol:** read-only; fail-closed; every finding carries `file:line` or a rendered page plus a
> severity; quote never compute.
> **Written:** 2026-07-27. Measurements supplied in the task were spot-verified, not redone; where I
> re-derived a figure I say so and give the command's basis.
>
> **Prior-review overlap check:** `_history/_review_v1/12_banca_simulator_report.md` was grepped for
> `equation|formalism|algorithm|pseudocode|Check2HGI|architecture`. One hit, at :167, and it is about
> CoUrb co-authorship, not about formalism. **This question has never been asked of this document
> before.** Nothing here repeats a fixed finding.

---

## 0 · The answer in four sentences

Yes, it is a real defense risk, but not the one the author is worried about. The committee will not
object that the *papers* are thin — a coletânea buys exactly that concession, and the norms
guarantee it. It will object that the **frame**, which is freely editable and where the examiner
looks for the candidate's own account of his own artifact, spends 104 pages and never once states
what Check2HGI computes. The remedy is one appendix and one equation, roughly four pages, and
almost everything needed for it is already written in this repository, in Portuguese, unrendered.

**Verdict on this charge:** *aprovado com correções menores*, with the correction being additive
frame material rather than any change to a reproduced chapter. The current state is defensible on
format grounds and indefensible on ownership grounds, and ownership is the axis this persona scores
hardest (dimension 7).

---

## 1 · Is this a real defense risk, or is it fine for a coletânea?

**Both, and the distinction is the whole answer.** Separate two claims the author is running
together.

### 1a · "The papers are too thin" — NOT a real risk. Defend this, do not fix it.

The coletânea format exists precisely to accept a published article at the density its venue
imposed. `UFV_COMPLIANCE.md`:51-53 records the norms verbatim: articles have "**free formatting**
given internal consistency (§2.6)", and "previously published articles may be reproduced from the
originals (§2.6.4)". A CBIC 8-pager and a MobiWac 9-pager are what they are. No examiner who
understands the format will ask why an ACM 9-page submission has one equation.

The precedent supports you on this axis too. Of the five exemplars, **the closest one — Viegas 2026,
same program, same advisor, approved 2026-03-04 — carries three numbered display equations in its
entire Fundamentals chapter** (extracted from `exemples/viegas/dissertacao_viegas_2026-02-09.pdf`:
labels `(2.1)`, `(2.2)`, `(2.3)` on rendered pp. 22 and 24, plus `(3.1)`). That is not a
high-formalism document, and it passed.

So if a reviewer tells you "add formalism because the exemplars have more", the honest answer is
that one exemplar has more (Germano, 35 chapter-numbered equations) and one has none at all
(Dorigueto: zero equations, zero algorithms, zero tables). Formal density is not the bar.

### 1b · "The frame never defines the contribution" — THIS is the real risk.

Here the format gives you no cover, and in fact it works against you.

The errata regime is a shield for the *reproduced* text and it is airtight. It is also, by the
document's own construction, **not a constraint on Chapters 1, 2, 6 or the appendices**.
`science/AGENT_HANDOFF.md`:188 states it flatly: "**Frame text (ch.1, ch.2, ch.6, appendices):
freely editable, no errata cost.**" The examiner does not know that sentence exists, but he does not
need to: he knows a coletânea has an Introdução Geral and a Conclusão Geral that the candidate wrote
himself, and that appendices are unrestricted (`UFV_COMPLIANCE.md`:56-57, Normas §2.8). Everything
he wants is placeable, and he knows it.

Worse, this document has already **demonstrated to him, four times, that it knows how to use that
freedom** — and never once for the method:

| Frame device already used | Location | What it adds |
|---|---|---|
| Appendix D, a whole methodological appendix built for the defense | pp. 99–101 | The label-history benchmark, four predictors, a table |
| Appendix B, an errata apparatus | pp. 89–97 | Nine rendered pages of scholarly bookkeeping |
| Appendix E, data ethics | pp. 102+ | Governance material no paper carried |
| A figure restored *because the dissertation had room* | `src_utils/adaptation_ledgers/5_mobiwac_ADAPTATION_LEDGER.md`:21, rendered p. 70 | Figure 6, cut from the 8-page build for space |

That last row is the one that closes the "no room" defense permanently. The author already reasoned
"the dissertation has no page limit, so restore what the venue cut" — and applied it to a
*results* figure. The examiner's question writes itself: **you restored what the page limit cut from
your results; why did you not restore what it cut from your method?**

And there is a specific, technical reason the omission bites, which I develop in §3: the missing
detail is load-bearing for an argument the chapter *does* make.

### 1c · One more thing the examiner is empowered to do

`reviewers/research/banca_evaluation_research_2026-07-20.md`:28 records that under the UFV Normas "the
banca is explicitly empowered to demand changes in **'forma, linguagem e conteúdo'**". Published
status does not immunize a chapter from a *requested* correction — and it certainly does not
immunize the frame. A committee that wants a method appendix can simply require one as a correção
obrigatória. Better to ship it than to receive it.

---

## 2 · The arguição — what an examiner asks that the current text cannot answer

Seven questions. Each is posed in the register a Brazilian committee uses, then: **what it tests**,
**the passage that fails to answer it**, and **what a sufficient answer needs**. Where the text
already answers, I say so and mark it a pass.

---

### Q1 — the one I would actually open with

> *"Professor, o senhor pode ir ao quadro e escrever a função de perda do Check2HGI? Só a função de
> perda. É a contribuição central da dissertação."*

**Tests:** candidate ownership (dim. 7) and contribution (dim. 5), in the cheapest possible form. An
examiner does not ask this to be cruel; he asks it because the answer takes forty seconds from
someone who built the thing, and because he could not find it in 104 pages.

**Where the text fails:** `src/chapters/5_mobiwac.tex`:274-284, rendered **p. 63**, §5.4.1 "The
check-in-level representation". This subsection is the *entire* formal account of the contribution.
I re-derived its length rather than trusting the brief: **240 words** after stripping LaTeX comments
and commands. It contains zero display equations, zero symbols, and one bare number pair. What it
does say about the objective is:

> "We train the graph mainly with an infomax objective, under which each vector learns to match its
> real neighborhood and reject a shuffled one" (`5_mobiwac.tex`:280)

and

> "Two small label-free auxiliary terms are added (weights 0.3 and 0.1): a masked reconstruction of
> each place's aggregated category features, and an anchor to a place embedding pre-trained,
> label-free, on the same data." (`5_mobiwac.tex`:280-282)

That is a paraphrase, not a definition. "Mainly" is doing heavy lifting: the reader cannot tell what
the main term is, over which pairs it is taken, how the three hierarchy boundaries combine, or what
"weights 0.3 and 0.1" are weights *relative to*.

**What a sufficient answer needs:** the total loss written once, with its terms named and its
weights attached; the discriminator; and a sentence saying which boundaries the sum runs over.
`docs/context/check2hgi_overview.tex`:211-230 already contains all of it, in Portuguese, unrendered
(the three-term sum at :215, the bilinear discriminator at :220, the per-boundary form at :226-228).

**Aggravating detail — the weights do not obviously reconcile, and only the author can settle it.**
The chapter reports auxiliary weights **0.3 and 0.1** (`5_mobiwac.tex`:280). The repository
explainer reports a three-term hierarchical loss with weights **0.4 / 0.3 / 0.3**
(`docs/context/check2hgi_overview.tex`:215). These are plausibly two different decompositions of the
same training objective — main hierarchical terms versus auxiliary terms — and I am **not** asserting
a contradiction. But that is exactly the point: with no equation in the document, *nothing on the
page lets a reader determine whether they agree*, and the explainer is the only written account that
exists. **[VERIFY: reconcile the 0.3/0.1 auxiliary weights of `5_mobiwac.tex`:280 against the
0.4/0.3/0.3 boundary weights of `docs/context/check2hgi_overview.tex`:215 before either set is
printed in an appendix. Author-only; I did not open the training code and make no claim about which
is current.]** Writing the equation is what forces this to be checked — which is an argument for
writing it, not against.

---

### Q2 — the four levels

> *"O senhor descreve quatro níveis: check-in, POI, região, cidade. Como exatamente a informação
> sobe de um nível para o outro? É uma média? Uma atenção? Uma convolução?"*

**Tests:** whether the candidate can distinguish his contribution from its parent (HGI) at the level
of the operator, not the diagram.

**Where the text fails:** `5_mobiwac.tex`:280, p. 63. The chapter names the four levels and says
"Edges connect each level to the one above it". It never names a single aggregation operator. The
reader has Figure 4 (p. 62, the dataflow) and Figure 5 (p. 65, the model), and both are good
figures, but a box-and-arrow diagram does not answer "média ou atenção?".

**What a sufficient answer needs:** four lines, one per level. They exist verbatim, unrendered, at
`docs/context/check2hgi_overview.tex`:141-155 — GCN propagation at the check-in level (with the
symmetric-normalized rule written out), multi-head attention for check-in→POI, attention plus GCN
over the spatial adjacency for POI→region, area-weighted pooling for region→city. This is a
four-row table plus two equations. It is the single highest-value half-page in the whole remedy.

---

### Q3 — the one that connects to a claim the chapter already makes

> *"Na seção sobre integridade da representação o senhor argumenta que o objetivo de treinamento é
> label-free e que a categoria entra apenas como feature do nó. Muito bem. Mas eu não vi o objetivo
> escrito em lugar nenhum. Como eu verifico essa afirmação?"*

**Tests:** experimental rigor (dim. 4) and the leakage question — question 8 of the standing bank,
the classic kill-shot.

**Why this is the sharpest form of the whole problem.** §5.5.2 (`5_mobiwac.tex`:340-380, rendered
**pp. 65–67**) is, on its own terms, the best-argued passage in the document. It bounds four
channels, states what each measurement covers *and does not*, discloses that the probe is linear,
Florida-only, one initialization, and run on ancestor builds. It is exemplary and I will defend it
against anyone who wants it shortened.

But its **first ground** is a claim about the loss function:

> "First, its training objective is label-free: it contrasts real graph neighborhoods against
> shuffled ones and never sees a next-category or next-region target." (`5_mobiwac.tex`:346, the
> *Integrity of the representation* paragraph)

An examiner who wants to test that claim has exactly one move: look at the objective. **It is not in
the document.** The strongest argument in the chapter therefore rests on an object the chapter never
exhibits. That is not a cosmetic gap; it is an evidentiary one, and it is why I rank the Check2HGI
formalism as MAJOR rather than as polish.

**What a sufficient answer needs:** the loss displayed, with one sentence noting that no term reads
a task label — which makes ground one checkable by inspection instead of by trust.

---

### Q4 — the ownership asymmetry

> *"O senhor reproduz, do Nash-MTL, os axiomas, a solução de barganha, o sistema não-linear e a
> regra de atualização. É um método de terceiros. Do Check2HGI, que é seu, o senhor escreve duzentas
> e quarenta palavras. Por que a assimetria?"*

**Tests:** dimension 7, candidate ownership, and it is the question I would return to if the answer
to Q1 wobbled.

**Where the text fails — by contrast, so both locations matter:**

| | Location | Rendered | Formal content |
|---|---|---|---|
| **Nash-MTL** (Navon et al., borrowed) | `3_cbic.tex`:225-278 | pp. 35–36 | 3 axioms, Eq. (3.2), the system $(\mathbf{G}^{\top}\mathbf{G})\boldsymbol{\alpha}=\boldsymbol{\alpha}^{-1}$, the update rule, a displayed parameter partition |
| **DGI** (Veličković et al., borrowed) | `3_cbic.tex`:151-166 | p. 32 | Eq. (3.1), the full infomax objective with corruption and discriminator |
| **Check2HGI** (yours) | `5_mobiwac.tex`:274-284 | p. 63 | 240 words, no symbols |

The document is **formally more generous to two borrowed methods than to its own contribution.**
That is the sentence an examiner will form, and it is not a formatting observation — it is a
judgment about the candidate's relationship to his own work. It is unfair as a judgment, because I
can see from `apx_a_contributions.tex`:34-35 that the platform behind Check2HGI is a "192-module,
28,644-line source tree … developed across roughly 1,700 commits". But the text invites the
judgment, and this persona's standing rule is that the written text, not the talk, determines the
verdict.

---

### Q5 — MTLnet, and it is a *different* question from Q1–Q4

> *"O MTLnet é a linha de base de toda a dissertação. No Capítulo 3 o senhor escreve $d_{\mathrm{shared}}$
> e $L_{\mathrm{shared}}$ sem dizer quanto valem. No Capítulo 4 aparece $d_{\mathrm{shared}}=256$ e
> quatro blocos residuais. É o mesmo modelo? Se for, por que os números só aparecem no artigo do
> qual o senhor não é primeiro autor?"*

**Tests:** text quality (dim. 8) and coletânea unity (dim. 9). This is a **sloppiness probe, and it
is a flip-trigger** — my own red-flag list names "inconsistent notation" and "numbers that differ
between chapters" as the things that turn a cooperative examiner hypercritical about everything
else.

**Where the text fails, precisely:**

- `3_cbic.tex`:194 — "map the raw input features into a shared latent space of dimension
  $d_{\mathrm{shared}}$." No value, anywhere in Chapter 3. Verified: grep for `shared}}` in
  `3_cbic.tex` returns :194, :204, :273 and no numeral.
- `3_cbic.tex`:204 — "continues through $L_{\mathrm{shared}}$ residual blocks." No value.
- `4_courb.tex`:109 — "a shared latent space of dimension $d_{\mathrm{shared}} = 256$."
- `4_courb.tex`:116 — "four shared residual blocks".
- `4_courb.tex`:118 — the heads, fully specified: three parallel MLPs of depths 2/3/4 for category,
  and a Transformer encoder with 8 attention heads and 4 layers for the sequential task.

So the reader learns what MTLnet *is* from Chapter 4, which is the chapter where the candidate is
second author. This is a genuine unity defect (two chapters bind the same symbol differently), and
it is the **cheapest fix in this entire report**: two numerals.

**Important scoping.** This is a *bound-symbol* defect, not a missing-formalism defect. MTLnet's
architecture is otherwise well covered: `3_cbic.tex`:188-216 walks encoders, FiLM (with the modulation
written out at :198-200), the shared stack, the heads, and — unusually and creditably — a
*Rationale for Hard Parameter Sharing* subsection at :209-216 that argues the choice against
alternatives. Figure 1 (p. 35) shows the architecture. **MTLnet is not the risk.** See §3.

---

### Q6 — the parameter count

> *"O senhor diz que o modelo conjunto tem cerca de 4,2 milhões de parâmetros em Alabama contra 1,1
> milhão dos dois modelos dedicados. Eu não consigo verificar isso a partir do texto."*

**Tests:** whether every number is traceable — and this one is a number the candidate volunteered
*against himself*.

**Where the text fails:** `5_mobiwac.tex`:302-308, rendered **p. 64**, discloses "about 4.2 million
parameters at Alabama against 1.1 million for the two dedicated models combined (5.2 against 2.0 at
California)". The disclosure is honest and unprompted, and `1_introduction.tex` guards against
selling MTL as cheaper. But no width, depth, or head count appears anywhere for the joint model: the
trunk is "a cross-attention stack of two blocks" (`5_mobiwac.tex`:290) and that is the only
structural quantity in the chapter. Grep for `hidden|width|attention head` across `5_mobiwac.tex`
returns nothing dimensional outside comments.

**What a sufficient answer needs:** one small configuration table — embedding dimension (64, already
stated), trunk width, number of blocks (2, already stated), heads, head widths, private-path width.
Six rows. It makes an honest number checkable and costs a third of a page.

**Note in your favour:** the *comparison* protocol around this is already strong.
`5_mobiwac.tex`:471 states that the dedicated category model is tuned per dataset over batch size
and learning rate, and :786 discloses that "the dedicated model receives the wider search … The
residual therefore favors the comparator." That pre-answers the "unfair baselines" probe (bank
question 11). Do not touch it.

---

### Q7 — the one where the text already wins (a pass, recorded so it is not edited away)

> *"E o código?"*

**The text answers this three times, at first artifact mention, exactly as it should:**

- `3_cbic.tex`:66 — footnote, `https://github.com/VitorHugoOli/PoiMtlNet`, "for full reproducibility".
- `4_courb.tex`:48 — footnote, `https://github.com/TarikSalles/Spatial_Embeddings`.
- `5_mobiwac.tex`:55 — footnote `fn:mobiwac:code`, "Code (model, representation, baselines,
  statistical tests): `https://github.com/VitorHugoOli/PoiMtlNet/tree/mobiwac`", **plus both data
  sources**, the figshare Gowalla dump and Massive-STEPS.
- And it is re-invoked where it matters: `5_mobiwac.tex`:396 — "the full training configuration for
  every model is in the released code (footnote~\ref{fn:mobiwac:code})".

Four repository or data URLs render in the PDF. That is at or above every exemplar (§4). **This is a
pass. Say so if asked, and do not add a reproducibility appendix on top of it.**

---

## 3 · Which is the bigger risk: Check2HGI or MTLnet?

**Check2HGI, and not narrowly. It is not close.** Justified by what each carries in the argument:

| | **Check2HGI** | **MTLnet** |
|---|---|---|
| Role in the arc | The **resolution**. `NORTH_STAR.md`:§2 — the joint win exists *because* of it | The **starting point**, whose result is a null |
| Whose it is | Yours; `GLOSSARY.md`:47 calls it "Ch.5 (the centerpiece)" | Yours (CBIC), but its published account is the artifact of record |
| Formal account in the document | 240 words, `5_mobiwac.tex`:274-284, p. 63 | Full walkthrough + FiLM equation + architecture figure, `3_cbic.tex`:188-223, pp. 34–35 |
| Prose account elsewhere in frame | 5 lines, `2_fundamentals.tex`:222-228, p. 22 | Recapped twice (`4_courb.tex`:89, `5_mobiwac.tex`:96-102) |
| Load-bearing for another claim? | **Yes** — ground one of the §5.5.2 integrity argument (Q3) | No |
| Named in Resumo/Abstract? | **No** — flagged independently by persona 17 (`17_resumo_abstract_assessment.md`:317, :445) | Yes, it is the only artifact named |
| If the examiner probes and the answer is thin | Attacks the contribution itself | Attacks a null result the dissertation already frames as of-its-time |
| Verdict | **MAJOR** | **MINOR** (bound symbols only, Q5) |

Three things settle it.

**First, a null result survives a thin description; a contribution does not.** If MTLnet turns out
under-specified, the damage is bounded: the chapter's finding is "this configuration did not beat
single-task", the preface time-indexes it (`NORTH_STAR.md`:§3, time-capsule rule), and Chapters 4
and 5 revise it. Nothing in the dissertation's headline claim rests on MTLnet's exact width. The
joint win rests entirely on Check2HGI.

**Second, MTLnet is *already* the better-documented of the two**, which inverts the author's
instinct. It has a dedicated architecture figure, a written-out FiLM modulation, per-component
paragraphs, and a *justification* subsection arguing hard sharing against soft sharing on three
grounds (`3_cbic.tex`:209-216) — the "considered-and-rejected alternatives" device this persona
explicitly rewards. Check2HGI has none of that. The residual MTLnet risk is Q5's two unbound
symbols, and that is a typo-class defect.

**Third, and decisively: only the Check2HGI gap disarms an argument the document is making.** Q3 is
the difference between "an omission" and "a defect". The chapter asks the reader to accept that the
training objective is label-free, and then does not show the objective. MTLnet has no analogous
dependency.

**Corollary for the author, since his failure mode is over-correction:** do not spend pages on
MTLnet. Q5 is two numerals. Spend the pages on Check2HGI.

---

## 4 · Is code expected? What the norms and the exemplars actually do

**Short answer: no code appendix, no pseudocode, no artifact-availability section. You already
exceed the local norm. Adding these would be over-correction.**

### 4a · What the norm requires

I read `UFV_COMPLIANCE.md` end to end for this. **Nothing in it requires, mentions, or implies a
code appendix, an artifact link, a reproducibility statement, or an algorithm environment.** The
mandatory-formatting table (§2, lines 28-40) covers font, paper, margins, spacing, page numbers,
pre-textual pages, resumo/abstract field rules and the funding sentence. The coletânea rules (§3)
cover structure, language, and reproduction of published articles. The defense prerequisites (§3)
are Art. 21 publication proof, Art. 22's twenty days, Art. 23's public defense, the anti-plagiarism
certificate, and wet signatures. Appendices are *permitted* (§2.8) and never required.

Two adjacent obligations exist and are already discharged: the anti-plagiarism certificate
(`UFV_COMPLIANCE.md`:71-73) and AI-use disclosure (§6, and Appendix C exists, p. 98). Neither is a
code obligation.

**Finding: the norm imposes nothing here. Any addition is a scientific choice, not a compliance
one.** [Scope note: I read the distilled `UFV_COMPLIANCE.md`, not the underlying PDFs. Persona 13
owns primary-source compliance.]

### 4b · What the five exemplars actually do

Extracted from the PDFs under `exemples/` with `pypdfium2` this session (text-layer extraction;
counts are of rendered caption labels and of end-of-line equation numbers, so treat them as close
rather than exact):

| Exemplar | pp. | Numbered display eqs | Algorithm envs | Figures | Code/repro **appendix** | Repo URL in text |
|---|---|---|---|---|---|---|
| Germano 2024 (same advisor, EN, coletânea) | 96 | **35** (2.1–2.6, 3.1–3.20, 4.1–4.9) | **0** | 11 | **none** (appendix block commented out in `0_main.tex`:292-305) | 2 (`gegen07/havana`; + a 4open.science anonymized link) |
| Viegas 2026 (same advisor, EN, coletânea, approved) | 100 | **3** in Ch.2 (2.1–2.3) + 3.1 | **2** (Algorithms 1–2, `Input:`/`Output:` floats) | 15 | **none** — Appendix A is *Other Scientific Contributions* | 2 own (`gfviegas/causal-nest`, gRPC repo) |
| Canesche 2021 (PT) | 108 | **0** | **1** (Algoritmo 1) | 57 | **none** | 1 (`github.com/canesche/`) |
| Passe 2020 (PT, modelo de artigos) | 68 | ~3 | **0** | 33 | **none** | 3, all third-party tools |
| Dorigueto (PT, coletânea) | 77 | **0** | **0** | 11 | **none** — Apêndice A is an extended abstract, Apêndice B an installation tutorial | project page `dpi.ufv.br/projetos/lapsusVGI` |
| **This dissertation** | **104** | **7** | **0** | **7** | none | **4** (2 own repos, 1 co-author repo, 1 data source) |

**Five of five have no code or reproducibility appendix. Zero of five.** Not one of them carries an
artifact-availability section, a hardware/versions block as an appendix, or a code listing in the
body. Every one of them handles code the way you already do: a footnote or an inline URL at first
artifact mention.

On algorithms: **two of five carry any algorithm environment at all** (Viegas 2, Canesche 1).
Canesche's thirteen "pseudo-code" occurrences are *figure captions* — pseudocode rendered as
images inside a 57-figure document, which is a compilers-thesis idiom, not a general expectation.

On repository links you are **at the top of the distribution**: four URLs, two of them your own
repositories, one with a branch pinned to the specific study. Only Germano and Viegas are
comparable, and neither pins a branch.

### 4c · Where you actually sit

You are low on **figures** (7, against 11 / 15 / 57 / 33 / 11 — you are last, and it is not
marginal), and mid on **equations** (7: more than Canesche's 0, Dorigueto's 0 and Viegas's ~4; far
below Germano's 35). Two qualifications keep this from being alarming: your figure count is
document-wide sequential numbering across only three method chapters plus a thin frame, and Viegas
— the closest structural precedent, same advisor, approved — sits at roughly your equation level and
passed.

**Conclusion for question 4: code is NOT expected, pseudocode is NOT expected, a reproducibility
appendix is NOT expected, and you already do better than the local norm on code availability. Add
none of these.** What the exemplars *do* show is that the two with the strongest method chapters
(Germano, Viegas) both write their own method formally — Germano with 35 equations, Viegas with
algorithm floats that specify his own procedures. Neither of them writes 240 words about his
centerpiece.

---

## 5 · The remedy — scoped, costed, ranked by defense risk removed per page added

Total: **≈ 4 pages**, all in freely editable frame or additive material, none of it touching a
reproduced result. Ranked. **R1–R3 are what I would file as obrigatórias. R4 is a suggestion. R5 is
optional and I would probably skip it.**

---

### R1 · One equation: the Check2HGI training objective — ★ highest value per page

**What:** the total loss, displayed and numbered, in §5.4.1, with terms named, weights attached, the
bilinear discriminator given, and one sentence stating that no term reads a task label.

**Where it can legally go — two routes, and route (b) is the safer one:**

- **(a) Both texts.** `apx_b_errata.tex`:238-244 and `AGENT_HANDOFF.md`:183-187 establish that for
  the under-review MobiWac chapter a minor correction needs no erratum: apply it to
  `articles/[mobiwac]/src/` as well and keep the two identical. Clean, but it spends space in a
  9-page paper under review.
- **(b) Dissertation-only, as a fourth marked addition.** Direct precedent: `apx_b_errata.tex`:231-234
  already declares "three marked additions declared in the chapter source" for Chapter 5 — the italic
  preface, the recap subsection, and the restored figure. A fourth is a one-clause edit to that
  sentence. **Recommend (b).** (Note for whoever applies it: an audit comment at
  `apx_b_errata.tex`:47-49 records that this count was re-checked by 8-gram diff against
  `articles/[mobiwac]/src/` and found correct, so the number is load-bearing and must be updated,
  not left at three.)

**Length:** one display equation plus 3–4 sentences. **≈ ⅓ page.**

**Source, already written:** `docs/context/check2hgi_overview.tex`:211-230 — the three-term
hierarchical loss, the bilinear discriminator $\mathcal{D}(\mathbf{e}_1,\mathbf{e}_2)=\sigma(\mathbf{e}_1^{\top}\mathbf{W}\mathbf{e}_2)$, and the
per-boundary positive/negative form. **In Portuguese; translate, do not re-derive.** Resolve the
`[VERIFY]` of §2/Q1 (0.3–0.1 versus 0.4/0.3/0.3) *before* it is typeset.

**Risk removed:** Q1 and Q3 together — the two sharpest questions in this report, and the only place
where a missing object undercuts an argument the document makes.

---

### R2 · A method appendix: "The check-in-level representation in detail" — ★ the load-bearing move

**What:** a new appendix (F, after E) carrying what a paper had no room for:

1. The four-level construction, one paragraph per level, each naming its **operator** — GCN
   propagation, multi-head attention, attention + spatial GCN, area-weighted pooling.
2. Two or three equations: the GCN propagation rule, the attention aggregation, and the temporal /
   time-decay edge weight.
3. The input feature vector: category one-hot, cyclic hour and day encoding, and the
   $w_{ij}=\exp(-\Delta t/\tau)$ edge weight with its $\tau$.
4. One small table: **level → input → operator → output**.
5. Two or three sentences on the embedding-corruption training variant, framed as an engineering
   choice.
6. Explicit **delta against HGI**: HGI is three levels (POI→region→city), this is four; that
   sentence is the contribution in one line.

**Where:** post-textual appendix. `UFV_COMPLIANCE.md`:56-57 (Normas §2.8) permits it; frame text,
zero errata cost, no interaction with the paper under review.

**Length: 2–3 pages.** Calibrate against Appendix D, which is pp. 99–101 = 3 pages for prose plus one
table. Two pages is enough if you are disciplined; do not let it reach four.

**Source, already written:** `docs/context/check2hgi_overview.tex`:100-230 (240-line file, Portuguese —
overview, input encoding, all four encoders, the corruption optimization, the loss).
`docs/context/EMBEDDINGS.md` for cross-checking. **This is translation and compression work, not new
science, and no experiment is required.**

**Risk removed:** Q2, Q4, and the residue of Q1 — and it converts the ownership asymmetry from a
liability into a strength, because the appendix is unambiguously the candidate's own writing about
the candidate's own artifact.

**Guardrails, since this is where over-correction would happen:**
- Every claim traces to the repository explainer or the code, per `AGENT_GUARDRAILS.md` §2 N1–N3;
  the "Speedup de 2x" of `check2hgi_overview.tex`:209 (also asserted at :114) is a **measured claim
  needing a source ledger line or a `[VERIFY]`** — do not print it bare.
- No new results, no new numbers beyond configuration constants.
- Canonical names only: "check-in-level representation (Check2HGI)", "place embedding (HGI)". No
  repo codenames — `dk_ovl`, `resln`, `gcn_ctrl`, "substrate", "engine" all appear in the source
  comments and none may reach prose (`WRITING_LAW.md`; `GLOSSARY.md` is fail-closed).
- It is an **appendix**, not a second method chapter. Chapter 5 stays as published.

---

### R3 · Bind $d_{\mathrm{shared}}$ and $L_{\mathrm{shared}}$ in Chapter 3 — ★ best cost-to-risk ratio in the report

**What:** give the two symbols their values at `3_cbic.tex`:194 and :204, matching
`4_courb.tex`:109 and :116 (256; four residual blocks) — subject to the author confirming the two
chapters describe the same configuration.

**Where:** Chapter 3 is *published* text, so this is an errata-regime item, not a free edit.
`NORTH_STAR.md` §5.7 sets the policy: fixes applied in the re-typeset chapter, listed once in
Appendix B. A specification value that the published paper left unbound is squarely within the
existing pattern (`tables/cbic/errata.tex` already carries content corrections of this class).
Alternatively, and even cheaper: leave Chapter 3 untouched and bind both symbols **once in Chapter
2's lineage discussion**, which is frame text with no errata cost at all.

**Length: two numerals**, plus one errata row if routed through Appendix B.

**Risk removed:** Q5, and with it the sloppiness flip-trigger — which protects every other finding
in this report from being read uncharitably.

---

### R4 · A joint-model configuration table — suggestion, not obrigatória

**What:** a six-row table making the 4.2M/1.1M parameter disclosure checkable: embedding dimension,
trunk width, blocks, heads, head widths, private-path width. Values from the released code.

**Where:** end of the R2 appendix. Frame text, no errata cost.

**Length: ⅓ page.**

**Risk removed:** Q6. Lower priority because the number is already disclosed honestly and
*against* the author's interest, which is itself a credibility asset; this only makes it verifiable.

---

### R5 · Name Check2HGI in the Resumo and Abstract — optional here, already filed elsewhere

Persona 17 raised this independently (`17_resumo_abstract_assessment.md`:317, :332, :445: "No
artifact is named: `Check2HGI` … absent; only `MTLnet`, the null-result model, is named"). It
reinforces the ownership theme of this report, but it is that persona's finding and its own cost
argument. **Roughly six words. Route it through persona 17's report, not this one, to avoid two
uncoordinated edits to the same paragraph.**

---

### Ranked summary

| # | Add | Pages | Where | Errata cost | Risk removed |
|---|---|---|---|---|---|
| R1 | Check2HGI loss equation | ⅓ | §5.4.1, as a fourth marked addition | none (route b) | Q1, Q3 — the two sharpest |
| R2 | Method appendix (Appendix F) | 2–3 | post-textual | none | Q2, Q4 + ownership |
| R3 | Bind two symbols | ~0 | Ch.3 (+ Appendix B row) *or* Ch.2 | one row, or none | Q5 + flip-trigger |
| R4 | Config table | ⅓ | inside R2 | none | Q6 |
| R5 | Name it in Resumo/Abstract | ~0 | front matter | none | (persona 17's finding) |

**Total ≈ 4 pages, taking the build from 104 to ≈ 108.** Every exemplar except Passe and Dorigueto is
longer than 104; Canesche is 108. You are not near any limit, and `AGENT_GUARDRAILS.md` §7's padding
caution is about *unearned* length — four pages of the candidate's own method is the opposite of
padding.

---

### What to add: NOTHING. The explicit do-not list.

Because the author's failure mode is over-correcting on a reviewer's suggestion, these are the
things a less careful reading of this report would produce, and each is wrong:

1. **No code appendix.** Zero of five exemplars have one; the norm does not ask; four URLs already
   render.
2. **No code listings or `lstlisting` in the body.** The repository explainer has two Python blocks
   (`check2hgi_overview.tex`:178-188 and :196-205); they are teaching aids for a repo document and do not belong
   in a dissertation. Prose plus one equation replaces them.
3. **No algorithm environments.** Only two of five exemplars use them, both for procedures with
   genuine control flow (Viegas's cycle-breaking loop, Canesche's placement traversal). Check2HGI is
   a forward pass over a hierarchy — an equation and a level table describe it better than
   pseudocode would.
4. **No re-derivation of Chapter 3's or Chapter 4's methods.** They are published and adequately
   described. R3 is two numerals.
5. **No new experiments.** Nothing in this report is answerable only by a run. R1–R4 are writing.
6. **Do not lengthen Chapter 5's body beyond R1.** The published/submitted shape is the format's
   protection. Detail goes in the appendix, where the format also protects you.
7. **Do not touch §5.5.2.** See below.

---

## 6 · What holds, and must not be edited away

The author's question presumes a weakness across the board. On most of this axis the document is
strong, and a correction pass could easily damage it:

- **§5.5.2, the integrity-of-the-representation passage** (`5_mobiwac.tex`:346 for the four grounds,
  :361 for the three limits; rendered pp. 65–67) is the
  best-argued page in the dissertation. Four named channels, each with what its measurement covers
  *and does not*; three stated limits on the probe (linear, Florida-only at one initialization,
  ancestor builds); and a passing candidate that later leaked, disclosed rather than buried. This
  pre-answers bank question 8, the standard kill-shot. R1 *serves* this passage by making its first
  ground checkable. Nothing here should be shortened, softened, or "tightened".
- **The two method figures are good and the dissertation already has more of them than the paper it
  reproduces.** The paper carries 3 figures and 1 equation (verified: `[mobiwac]/src/main.pdf`,
  9 pp, Figs. 1–3, one `(1)`); the chapter carries 4 figures and 1 equation, Figure 6 having been
  restored precisely because the dissertation had room
  (`5_mobiwac_ADAPTATION_LEDGER.md`:21). The chapter is *already* an improvement on its source.
- **Figure 5's caption** (p. 65) does real architectural work: private encoders, shared trunk as "the
  only place where the two tasks interact", category output from the trunk alone, region output
  combining trunk and private path. A self-contained caption with reading instructions — the Viegas
  device done right.
- **The joint model's topology is completely specified in prose** (`5_mobiwac.tex`:289-293), even
  though its dimensions are not. Which stream reads which input, where sharing happens, what the
  private path bypasses, and what the category task does *not* touch — all stated. This is better
  than most 9-page papers manage, and the Check2HGI subsection immediately above it is the outlier,
  not the norm.
- **Cost disclosed against interest**, twice: the parameter counts at `5_mobiwac.tex`:302-308, and
  the wider hyperparameter search granted to the comparator at :471 and :786. Examiners reward this.
- **Repository and data links at first artifact mention**, three chapters, one with a pinned branch.
- **Appendix D** already proves the author knows how to build a methodological appendix under this
  format. R2 is the same move, applied to the method instead of the benchmark.

---

## 7 · Verdict on this charge

**Aprovado com correções menores.** The gap is real, it is confined to the frame, it is entirely
additive, and the material to close it is already written in the repository — in Portuguese,
unrendered, at `docs/context/check2hgi_overview.tex`.

To the author's question, in his own terms: *sim, falta — mas não onde o senhor pensa.* It is not
missing from the papers; the papers are allowed to be what they are, and defending that is the
correct answer if a reviewer pushes on it. It is missing from **your** part of the document — the
part no venue constrained, the part where the committee looks to find out whether you own the thing
you built. Four pages closes it, and roughly three of those four are translation.

**Confidence and limits of this review.** I read the LaTeX sources, the rendered PDF text layer, the
five exemplar PDFs, the governing docs, and the repository explainer. I did **not** open the
training code, so I make no claim about which loss weights are current (§2/Q1 `[VERIFY]`), and I did
**not** re-verify the UFV primary-source PDFs behind `UFV_COMPLIANCE.md` (persona 13's scope).
Exemplar counts come from PDF text-layer extraction and should be read as close, not exact; the
qualitative pattern — **zero of five have a code appendix, two of five have any algorithm
environment, and you lead on repository links** — is robust to any counting error I could plausibly
have made.

### Out-of-scope handoffs

- **Persona 17** owns R5 (naming Check2HGI in the Resumo/Abstract); already filed at
  `17_resumo_abstract_assessment.md`:317. Coordinate so the paragraph is edited once.
- **Persona 18** (visual/presentation): the figure count, 7 against the exemplar range 11–57, is a
  standing question outside this charge.
- **Persona 13** (UFV compliance): §4a's reading of the norm is from the distilled
  `UFV_COMPLIANCE.md`, not the primary PDFs.
- **Persona 14** (adversarial advisor) must gate R1–R4 before anything is applied, per the standing
  pipeline. R1 in particular changes a chapter that reproduces a manuscript under review.

### Open question only the author can answer

Do the auxiliary weights **0.3 / 0.1** (`5_mobiwac.tex`:280) and the boundary weights **0.4 / 0.3 /
0.3** (`docs/context/check2hgi_overview.tex`:215) describe the same training objective under two
decompositions, or has the objective changed since that explainer was written? R1 cannot be typeset
until this is settled, and settling it is a code question, not a text question.
