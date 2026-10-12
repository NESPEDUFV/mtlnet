# BANCA_v2 — simulated arguição on the corrected defense build

> 🛑 **GERACAO SUPERADA — nenhum numero deste ficheiro pode ser citado.**
>
> Isto e a simulacao de banca v2, corrido em 26 de julho de 2026, **antes** de a geracao v18 fechar o vazamento de rotulo
> no grafo de visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 de categoria
> medidas aqui vem da geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta: as questoes ja
> encerradas estao la com a prova, e este ficheiro nao e fonte de nenhuma delas.


**Persona:** 12 · Banca simulator (`reviewers/12_banca_simulator.md`), examiner (doutor, ML / urban
computing) on a UFV/PPGCC master's defense of a *coletânea de artigos*.
**Build under review:** `src/dissertacao.pdf`, 94 pages, rebuilt 2026-07-26 after the correction round.
**Companion build checked:** `src/build/main_final.pdf`, 89 pages (same defects, shifted pagination).
**Method:** full pre-read with annotation list, built first; then scoring; then the arguição from the
annotations. Read-only — no file in the dissertation was edited. Page numbers are printed pages, which
coincide with PDF pages from p. 13 onward.
**Prior reports were not consulted for findings.** Every number below was re-traced this session to the
source of truth named in `reviewers/README.md §Sources of truth`.

---

## 0 · Verdict

> ### APROVADO COM CORREÇÕES MENORES
> *(with the four **obrigatórias** of §3 filed, and verified in the corrected version before deposit)*

The science is defensible. I went looking for the kill-shot in the six places the evidence is thinnest,
and in five of them the text had already been there before me — the leakage channel is bounded rather
than declared closed, the checkpoint-selection bias is disclosed *with its direction*, the inferential
unit is stated honestly as four per-seed means over one fixed partition, and the freeze control that
undercuts the tidiest reading of the headline is reported by the candidate himself as a finding. That is
not a document trying to survive a defense. That is a document that already argued with itself and lost
in public, twice, and wrote down what it lost.

I have to be equally plain about why this verdict is not *sem ressalvas*.

**The fundamentals chapter contains a citation that renders as `(??)`.** Page 21, inside Chapter 2 —
the exact place where, as a matter of professional habit, my impression of a dissertation sets. Three
more follow in Chapter 4 (pp. 45, 49, 50). A sentence in Appendix A is destroyed mid-clause (p. 85). A
word is run together on p. 49. The build was handed to me described as *0 undefined refs/cites*; the
build log says otherwise, five times, and I reproduced the cause. I read the remaining 70 pages in the
adversarial register that discovery puts an examiner into, and I want the candidate to understand
that the length of the corrections list in §3 is partly a consequence of four characters on page 21.
The science survived that re-reading. The credibility of the *artifact* did not survive it intact, and
Appendix C makes the wound deeper by stating that this document "passed an eighteen-reviewer panel."

Nothing in the obrigatórias requires a new experiment, a re-run, or a restructuring. All four are text
and one bibliography file. That is what separates *menores* from *substanciais*, and I applied that line
rather than a feeling about volume.

**Counterfactual, stated so the candidate can calibrate:** had this build reached me *without* the
correction round's disclosures — with the region-pathway freeze unreported, the leak audit's three
limits unnamed, the inferential unit written as "twenty repetitions", and the selection bias
undisclosed — my verdict would have been **aprovado com correções substanciais**, and questions Q7,
Q9, Q10 and Q11 below would have been asked to establish whether the candidate knew. The correction
round is the reason this defense is a conversation instead of an interrogation.

---

## 1 · Dimension scores

| # | Dimension | Score | Evidence line |
|---|---|:---:|---|
| 1 | Problem clarity and delimitation | **5** | The question is set inline and bold (p. 14) and the three targets are held apart formally in §2.1, excluded in §1.4 ("The exact next place is not predicted anywhere in this work", p. 15), and re-stated as limitation 4 (p. 77). Three separate load-bearing places, no drift. |
| 2 | Command of the state of the art | **4** | §2.3 takes a position rather than cataloguing: "a fixed-weight baseline is a serious competitor, and a balancer earns its place only by outperforming it" (p. 23), grounded on Lin/Xin/Kurin. Held below 5 by four broken citations and by a novelty claim resting on "to our knowledge" (p. 61). |
| 3 | Methodological coherence | **4** | Alternatives are tested, not asserted: the cascade is rewired inside the model and reported as a tie (p. 72), balancers are tried and reported as no help (p. 61). Held below 5 because the cascade "runs under the configuration tuned for the parallel model" (p. 73, disclosed) and the task pair changed mid-arc (limitation 6, p. 77). |
| 4 | Rigor and honesty of results | **4** | Verbs are bound to tests, an analysis plan was "fixed during development and before any result was read" with its own departure disclosed (p. 67), floors are named, Holm applied. Held below 5 by the n=4 inferential unit over one fixed partition, by epoch selection reading the scored fold, and by an undisclosed pending revision to the AZ ceiling (§3, MODERATE-2). |
| 5 | Contribution | **4** | A nameable delta well above the master's bar: the check-in-level representation (+27.6 to +39.6 macro-F1 over the place embedding, Table 9, p. 69) plus a joint model that beats both dedicated models. Held below 5 because the candidate's own freeze control locates the category half in the trunk, not in cross-task transfer (p. 72). |
| 6 | Recognition of limitations | **4** | Six numbered limitations each tied 1:1 to a future-work item (pp. 77–78), plus three inside Ch. 5 and the volunteered width asymmetry (p. 75) and interval scope (p. 17). Held below 5 by one absent class: no privacy, consent, licensing or re-identification limitation exists anywhere in 94 pages. |
| 7 | Candidate ownership | **4** | The CoUrb contribution is stated in three independent places (§1.5 p. 16; Ch. 4 preface p. 43; Appendix C p. 94) and is specific — second author, presenter, author of the baseline. Held below 5 by Appendix A's platform-scope claim, which the author's own source comment flags as unsettled. |
| 8 | Text quality | **2** | Four citations render as `(??)` (pp. 21, 45, 49, 50); a sentence in Appendix A is destroyed — "released with the code. collection of one-off scripts" (p. 85); "two encodersthat" (p. 49). This is the flip trigger, and it fired inside the fundamentals chapter. |
| 9 | Coletânea unity | **4** | This is the strongest dimension of the document as a *coletânea*: the arc is written as a correction trail (p. 14), each chapter preface time-indexes its own conclusions, Ch. 5 recaps both predecessors by name (§5.2.1), and Appendix B is a genuine errata rather than a formality. Held below 5 by the incomplete dataset-count reconciliation (§3, MAJOR-2). |
| 10 | Defense-readiness of the text | **3** | The text pre-answers leakage, capacity, cascade choice, balancer choice and selection bias — most of my prepared attacks. It does not pre-answer the static-task circularity of Ch. 3/4, the ethics question, or the "is this multi-task learning at all" reading its own freeze control invites. |

**Mean 3.8.** Dimensions 1, 6 and 9 are what a good coletânea looks like. Dimension 8 is what loses a
committee's goodwill in the first ten minutes.

---

## 2 · Pre-read annotation list (built before the arguição, per the persona's procedure)

These are the marks in my copy. Each becomes a question, a correction, or both.

| # | p. | What I marked | Becomes |
|---|---|---|---|
| A1 | 21 | `(??)` in the fundamentals chapter | BLOCKER-1 |
| A2 | 45, 49, 50 | three more `(??)`, one mid-sentence | BLOCKER-1 |
| A3 | 85 | "released with the code. collection of one-off scripts" — sentence destroyed | BLOCKER-1 |
| A4 | 49 | "two encodersthat represent" | MINOR-1 |
| A5 | 94 | Appendix C: "passed an eighteen-reviewer panel" — falsified by A1–A3 | MAJOR-1 |
| A6 | 66 | leak audit: linear probe, Florida only, one seed, ancestor builds; "bounds this channel rather than closing it" | Q7 |
| A7 | 66 | "one encoder that passed it leaked under a downstream sequence model" — the candidate's own screen is documented as fallible | Q7 |
| A8 | 32–33 | Ch. 3 node features are "category one-hot encoding of each POI"; the task predicts that category | Q8 / MAJOR-3 |
| A9 | 17, 67 | n = 4 per-seed means, one fixed partition, Wilcoxon floors at 0.0625 | Q9 |
| A10 | 73 | "every absolute score reported here is optimistic"; "It does not follow that the bias cancels exactly" | Q10 |
| A11 | 72 | freeze control: full category gain survives with the region pathway at initialization | Q11 |
| A12 | 71 | AZ Δcat +9.35 is the range endpoint quoted in the abstract | MODERATE-2 |
| A13 | 53 vs 65 | FL/TX/CA counts differ between Ch. 4 and Ch. 5; Appendix B.4 reconciles Florida only | MAJOR-2 |
| A14 | 57 vs 77 | Gowalla vintage: "February 2009 and October 2010" (Ch. 4) vs "2009 and 2011" (Ch. 6) | MODERATE-1 |
| A15 | — | no privacy / consent / licensing / re-identification sentence in 94 pages | Q13 / MAJOR-4 |
| A16 | 20 | HGI repurposed *and* re-tuned (0.4 → 0.7); category F1 0.74 → 0.82 | Q12 |
| A17 | 68 | dedicated category model tuned per dataset; joint model one fixed configuration | Q12 |
| A18 | 64 | joint 4.2M params vs 1.1M for both dedicated models combined | Q15 |
| A19 | 86 | BRACIS rejection, and its central claim corrected by Ch. 5 | Q6 |
| A20 | 76 | capacity-matched control appears only in Ch. 6, post-submission | Q5 |

---

## 3 · Corrections list the banca would file

### Obrigatórias (must appear in the corrected version)

**BLOCKER-1 · Four citations render as `(??)`; the build is not clean.**
> p. 21: "again to honor the spherical domain that flat sine-and-cosine features distort **(??)**."
> p. 45: "applied to the geographic context **(??)**, models continuous functions"
> p. 49: "two encodersthat represent distinct spatial encoding paradigms: SIREN **(??)**"
> p. 50: "The SIREN model (Sinusoidal Representation Networks) **(??)** models a continuous function"

Root cause, reproduced this session and stated so no one wastes time on the wrong fix: the key
`russwurm2024geographiclocationencodingspherical` **exists correctly** in `src/references.bib:849`, and
the four citing sites are **correctly spelled** (`2_fundamentals.tex:211`, `4_courb.tex:65,129,148`).
The failure is upstream of both. `src/references.bib:831` is a `%` comment containing the literal
string `@misc`:

> `% (same class as the GAT erratum above, Appendix B): the donor entry was typed @misc as an`

BibTeX does **not** honour `%` comments — it scans for `@`. `build/main.blg` records the consequence:
*"I was expecting a `{` or a `(`---line 831 of file references.bib"*, then *"I'm skipping whatever
remains of this entry"*. The skip swallows the immediately following `@inproceedings` entry, and the
next line of the log reads *"I didn't find a database entry for
`ruß­wurm2024geographiclocationencodingspherical`"* — note that BibTeX reports the **pre-rename** key
with the U+00DF byte, i.e. it is reading a stale internal state produced by the same skip. The
bibliography ships **97 of 99** entries. `liu2014geographical` is the second absentee, but it is
deliberately uncited (Appendix B, p. 93) and therefore harmless.

*Direction (not applied):* remove or de-`@` the `@misc` token inside the comment at
`references.bib:831` — e.g. write it as `at-misc` or `\@misc` — then re-run the full
`latex → bibtex → latex → latex` cycle and confirm `main.blg` reports zero warnings and `main.bbl`
carries 98 items. **Do not ship a build whose `.blg` contains a `Warning--I didn't find` line.**
This one edit resolves all four `(??)` and the "0 undefined cites" claim becomes true.

**BLOCKER-2 · Appendix A opens with a destroyed sentence.**
> p. 85: "…supported the experiments of Chapters 3 and 5 and is released with the code. **collection
> of one-off scripts: name-keyed registries expose interchangeable implementations across each axis
> the dissertation studies.**"

At `apx_a_contributions.tex:57` a multi-line `%` comment block terminates mid-line and the surviving
prose fragment — "It is organized as a registry-driven experimental framework rather than a" — is
trapped inside the comment. The reader receives an orphaned subordinate clause as the second sentence
of the appendix. *Direction:* close the comment block on its own line before the prose resumes.

**MAJOR-3 · Chapters 3 and 4 evaluate a category prediction whose input encodes that category, and
the dissertation does not scope it.**
Chapter 3 builds its representation on a graph whose "node feature matrix is based on category one-hot
encoding of each POI" (p. 32), then defines the static task as pairs "(e, c), where c is the POI's
ground-truth category to be predicted" (p. 33). For the static *category classification* task, the
label of the target POI is present, one-hot, in the input from which that POI is embedded. The figures
in Tables 2 and 6 are therefore not measurements of inductive category inference; they measure how
much of an injected label survives graph convolution and DGI compression. Chapter 4 inherits the same
construction (HGI over category-derived POI Encoder embeddings, p. 51) and reports the largest numbers
in the document on it — "average gains per state are 20.2 to 22.0 percentage points" (p. 54).

Chapter 5 knows this. Page 66 states it exactly, for its own representation: "That bounds the training
signal and not the inputs, since each visit's own category enters as a node feature." The frame never
carries that sentence back to Chapters 3 and 4, which is where the static task lives and where the
exposure is largest. Chapter 5's own defence — that the task is *sequential*, so the target's features
are not in the window — does not transfer to a *static* task whose target is the embedded object.

This does not invalidate anything the dissertation concludes: the arc's claims are about MTL-vs-STL
*differences* under a shared representation, and both arms carry the same exposure. That is precisely
the sentence that is missing. Published status does not immunize the chapters — the Normas let this
banca demand changes in *forma, linguagem e conteúdo* even for published articles, and I am
demanding one here. *Direction:* one scoping paragraph, in §2.1 or the Ch. 3 preface, stating that the
static category-classification task of Chapters 3 and 4 is evaluated on a representation whose input
features include the target's own category label, that its absolute values are therefore not
comparable to inductive category prediction, and that the MTL-versus-single-task comparison the
chapters draw is unaffected because both arms share the exposure.

**MAJOR-4 · No statement on privacy, consent, licensing or re-identification exists in the document.**
A regex over all 94 pages for `privac|re-identif|anonym|consent|LGPD|GDPR|ethic|IRB|comitê de ética`
returns **zero matches**. The object of study is 9.5 million individual movement traces, split by
user, with per-user sequences reconstructed and users treated as the unit of generalization. The
repository already holds the verified evidence needed to write the paragraph
(`src_utils/evidence/DATASET_LICENSING_FINDINGS.md`: the consumed copy is Figshare
DOI 10.6084/m9.figshare.22126586.v2 under CC0, a licence applied by the depositor, with the upstream
source unreachable and rights provenance unestablished). The finding note itself says: "The
dissertation currently renders zero sentences on data licensing." *Direction:* a short subsection
(§1.4 or §6.3) stating the provenance and licence of each corpus with the depositor caveat named, the
observational and public nature of the data, the absence of human-subject intervention, and — this is
the part a committee will press — what the *outputs* enable, since a model that ranks the ten census
tracts a named user will visit next is a re-identification surface even when the training data is
public. State it; do not argue it away.

### Sugestões (strongly recommended, not blocking)

**MAJOR-1 · Appendix C's "passed" is falsified by the artifact.**
> p. 94: "The complete first version **passed** an eighteen-reviewer panel, each reviewer a separate
> agent … and a simulated defense committee, among others."

A committee member who reads this sentence and then turns back to the `(??)` on p. 21 draws a
conclusion about the whole verification apparatus that the apparatus does not deserve. *Direction:*
after BLOCKER-1 is fixed, either keep the sentence (it will then be defensible) or soften "passed" to
"was reviewed by". Do not ship both the claim and the defect.

**MAJOR-2 · The dataset-count reconciliation covers one of the three states that need it.**
Appendix B.4 (p. 92) explains that Ch. 3/4 report Florida as 20,301 / 65,009 / 990,518 and Ch. 5
reports 21,052 / 76,544 / 1,407,034. Correct and well argued. But Table 5 (p. 53) and Table 8 (p. 65)
also disagree on **Texas** (3,355,419 → 4,089,892 check-ins) and **California** (2,535,573 →
3,171,380), and B.4 names neither. A reader comparing the two tables sees three discrepancies and one
explanation. *Direction:* extend B.4's first sentence to all three states; the mechanism it already
gives (category-mapping widening) covers them.

**MODERATE-1 · The Gowalla vintage differs between chapters.**
Ch. 4, p. 57: "collected between **February 2009 and October 2010**." Ch. 6, p. 77: "collected between
**2009 and 2011**." Both are defensible in isolation — Ch. 4 reproduces the published SNAP-era
statement and Ch. 5's hidden provenance comment records a measured range of 2009-01-21 to 2011-08-16
for the Figshare dump the current pipeline consumes. Unreconciled, they read as carelessness in the
one place (limitation 1) where the reader is being told what not to trust. *Direction:* one clause in
B.4 or limitation 1 noting that the two extractions draw on different dumps with different date
coverage.

**MODERATE-2 · An abstract-level number carries an undisclosed pending revision.**
The abstract quotes "5.3 to 9.4 macro-F1 points" (p. 5). The upper endpoint is Arizona's +9.35, whose
value depends on the AZ dedicated ceiling of 56.43. The source of truth flags that ceiling as
provisional: `CEILINGS_N20_FINAL.md:11-12` — "Two n=10 screens sit higher still (bs2048@0.0025 =
57.04 …) — **pending a 2-seed top-up** … If 57.04 holds at n=20 the AZ ceiling becomes ~57.0 → Δcat
≈ +8.8." The caveat lives in a LaTeX comment (`5_mobiwac.tex:529-530`) and reaches no reader.
*Direction:* either complete the top-up, or footnote the AZ row of Table 10 with the pending screen.
The verdict does not change either way; the range endpoint does.

**MODERATE-3 · A `[VERIFY]` flag survives in the shipped chapter's source.**
`2_fundamentals.tex:174` carries "% [VERIFY: averaging convention of the swept "Cat F1"]" against the
sentence printed on p. 20 ("rose monotonically from 0.74 to 0.82"). The comment records that the
source files write "Cat F1" without naming macro versus weighted averaging. It does not render, so it
is not a reader-facing defect — but it is an open fact-gate item on a number that ships. *Direction:*
confirm the convention, or drop the two decimals and keep the clause qualitative, as the comment
itself proposes.

**MINOR-1 · p. 49: "two encodersthat represent".** Missing space, source `4_courb.tex:129`.

**MINOR-2 · p. 85: Appendix A's platform-scope claim is flagged unsettled by its own author.**
The hidden comment above the sentence asks the author to confirm whether the Chapter 4 experiments ran
on the platform. The printed sentence currently scopes to "Chapters 3 and 5". Settle it before the
defense — Q3 will land on it.

**NIT-1 · Table 9's footnote (p. 69) explains the 26.56/26.56 coincidence at Alabama and Istanbul.**
Keep it. It is the kind of pre-emption that stops a committee mid-question, and I nearly asked.

---

## 4 · Arguição transcript

Fifteen questions, posed as I would pose them in the sala. Six are from the coletânea block (minimum
four). Each carries: what it tests, what a strong answer contains, and what the **text as it stands**
can support — because that is the part the candidate cannot improvise around.

---

### Q1 — coletânea (bank Q19)
> *"Convença-me de que isto é uma dissertação e não três artigos grampeados. Qual é o fio condutor, em
> uma frase?"*

**Tests:** whether the collection has an argument or an order.
**A strong answer contains:** one sentence — the representation, not the architecture, decides whether
MTL helps — and then the demonstration that each chapter is a *move* in that argument rather than an
episode.
**What the text supports — fully.** p. 14 states the arc as "a negative result, its diagnosis, and its
resolution", and p. 76 closes it: "The representation, together with the sharing topology built on it,
is what the answer depends on." §1.2 and §6.2 answer with the same sentence in different words, which
is the test of a real fio condutor. **This is a pass; I would move on quickly.**

---

### Q2 — coletânea (bank Q20)
> *"O artigo 3 contradiz a conclusão do artigo 1. Em qual devo acreditar, e onde o texto me diz isso
> sem que eu tenha que descobrir sozinho?"*

**Tests:** whether inter-paper conflict is confronted or buried.
**A strong answer contains:** both conclusions are correct *within their configurations*; the later one
supersedes only under the stated change of representation and topology; and the reader is told this at
the point of reading, not retroactively.
**What the text supports — fully, and with a device.** Every article chapter opens with an italic
preface that time-indexes it: p. 27, "Its conclusions are the conclusions of the time, for the
configuration studied here … Chapters 4 and 5 revise that verdict." p. 77 refuses the easy synthesis:
"The negative result of Chapter 3 and the positive result of Chapter 5 do not contradict each other;
read together, they bound the claim." **Pass.** I would tell the candidate this device is the single
best structural decision in the document.

---

### Q3 — coletânea (bank Q21)
> *"No artigo do CoUrb o senhor é segundo autor. O que exatamente foi contribuição sua, e por que esse
> capítulo pertence à sua dissertação?"*

**Tests:** individual contribution — a live concern in this format, and the one a committee is
obliged to raise.
**A strong answer contains:** the specific contribution (not "I helped"), the norms basis for
inclusion, and a clean line between what the candidate did and what the first author did.
**What the text supports — well, in three places.** p. 16 and p. 43: first author is Tarik S. Paiva;
the candidate "is the second author, contributed the MTLnet baseline on which the study builds, and
presented the paper at the event." That is specific and it is the right basis — the chapter's entire
premise is a controlled substitution *into the candidate's own prior model*.
**Where the candidate is exposed:** Appendix A currently scopes the research platform to "the
experiments of Chapters 3 and 5" (p. 85), and the source comment records an unsettled question about
whether the Chapter 4 experiments ran on it. If I ask "and the Chapter 4 experiments — whose code?"
the document's answer is a footnote to a different repository (p. 44, `TarikSalles/Spatial_Embeddings`).
**Settle this before the defense.** The honest answer is likely "his code, my baseline, my
presentation", and that answer is fine — but it must be said, not discovered.

---

### Q4 — coletânea (bank Q22)
> *"A Tabela 5 e a Tabela 8 dão números diferentes para a Flórida, o Texas e a Califórnia. O Apêndice
> B.4 explica a Flórida. E os outros dois estados?"*

**Tests:** cross-chapter number discipline — the classic examiner trap, and the one that decides
whether I trust the other tables.
**A strong answer contains:** the mechanism (category-mapping widening between two extractions of the
same public dump), the fact that the earlier check-in set is a strict subset of the current one, and an
immediate concession that the appendix under-covers.
**What the text supports — partially, and this is a live hit.** B.4 (p. 92) gives an excellent
account for Florida, including the controlled comparison: "each of its POIs, users, and check-ins
reappears in the current extraction." The same mechanism plainly covers Texas (3,355,419 → 4,089,892)
and California (2,535,573 → 3,171,380), but the appendix does not say so, and a reader who checks the
two tables finds three gaps and one explanation. The candidate should concede the coverage gap
immediately and name the mechanism. See MAJOR-2.

---

### Q5 — coletânea (bank Q23)
> *"A Conclusão Geral afirma algo que nenhum dos três artigos afirma sozinho? Ou é um resumo?"*

**Tests:** whether the frame argues at thesis level.
**A strong answer contains:** a claim that exists only at the collection level, and evidence generated
*for the collection*.
**What the text supports — fully, and this is the strongest single move in the frame.** §6.2 (p. 76)
reports a capacity-matched dedicated baseline "run after the Chapter 5 manuscript was submitted and
reported here as a frame-level analysis": a dedicated category model widened to the joint model's
parameter budget reaches 56.16 macro-F1 at Alabama against 56.82 at its own tuned width and 64.51 for
the joint model, with California repeating the pattern (69.88 against 70.60 and 77.05). I traced every
one of those figures to `docs/results/closing_data/capacity_matched_stl_cat/capacity_matched_summary.json`
and they reproduce exactly, including the 101.9 percent parameter ratio at the h=752 width. The
Conclusão Geral therefore closes an explanation — "the joint model just has more parameters" — that no
individual paper closes. **That is what a Conclusão Geral is for, and few coletâneas manage it.**
I would say so aloud.

---

### Q6 — coletânea (bank Q24)
> *"Que tentativas fracassadas ficaram de fora, e por que devo confiar que a exclusão não foi
> conveniente?"*

**Tests:** whether the negative record is complete or curated.
**A strong answer contains:** the BRACIS submission, its rejection, and — the part that matters — that
its central claim was *corrected* by the candidate's own later work rather than quietly dropped.
**What the text supports — fully.** Appendix A.2 (p. 86) names the title, the venue, the rejection date
(June 8, 2026), and then does the hard thing: "its central claim, that multi-task learning imposes a
cost on region prediction, was later corrected by the MobiWac study: the observed cost traced back to
a numerical-precision artifact of that training configuration and to the older evaluation protocol.
For this reason, no result of the manuscript is cited as evidence anywhere in this dissertation."
Declaring a rejected paper whose headline your later work refutes, and then quarantining it from the
evidence base, is the opposite of convenient. **Pass.**

---

### Q7 — the leakage kill-shot (bank Q8)
> *"O senhor escreve que a auditoria 'limita o canal em vez de fechá-lo'. Então diga-me o que ficou
> fora do limite. E por que devo aceitar uma sonda linear, rodada em um único estado, em uma
> inicialização, sobre uma versão anterior da representação — quando o próprio parágrafo diz que uma
> sonda linear já deixou passar um vazamento?"*

**Tests:** the deepest exposure in the document, and whether the candidate can hold the line at the
boundary of his own evidence rather than retreating to "we audited it".
**A strong answer contains:** four parts. (i) Name the unbounded channels explicitly: visits to places
unseen in training (13 to 33 percent of visits, since the transductive measurement "covers the visits
whose places appear in training (67 to 87 percent)", p. 66); the nonlinear/multi-step forward-edge
channel, which the record shows the linear screen cannot see; and the five datasets other than Florida
where the forward-edge probe never ran. (ii) State why the linear screen was nonetheless the right
instrument at the time: it is a *disqualifier*, and it did disqualify — the attention-based encoder at
0.4976/0.4863 against a ~0.41 ceiling was thrown out on this evidence (p. 66). (iii) Argue the
differential: the leak channel, if open, is open identically for the joint and the dedicated arms,
which share the representation, so it inflates absolute scores and not the MTL-versus-STL difference
that carries every claim in the chapter. (iv) Concede the one thing that cannot be argued: the
place-level-versus-check-in-level comparison of Table 9 is *not* protected by that symmetry, because
the two arms use different representations with different exposure to the channel — the +27.6 to +39.6
gap is the number most at risk, not the +5.3 to +9.4 one.
**What the text supports — most of (i) and (ii), none of (iii) or (iv).** p. 66 is unusually candid;
I traced its numbers to `docs/results/embedding_eval/rescreen_cat/RESCREEN.md` and the four decimals
are quoted correctly, as is the admission that "the cheap per-step *linear* gate catches gat but
MISSES rgcn". But the chapter never argues the symmetry defence, and never distinguishes which of its
two headline gaps the audit protects. **This is the question I would spend the longest on. The
candidate must be able to say (iii) and (iv) aloud — they are not in the document.**
Note also: `A4_RESULTS.md` carries a run-variance caveat the chapter does not — a re-run moved the
Alabama category figure from +0.29 to +0.88 pp, so the transductive decimals are one traceable draw,
not a constant. The verdict ("within fold noise") holds; the decimals should not be defended as exact.

---

### Q8 — the static-task circularity
> *"Nos Capítulos 3 e 4, a matriz de atributos dos nós é o one-hot da categoria do POI, e a tarefa
> estática prediz essa mesma categoria. O que exatamente está sendo medido nas Tabelas 2 e 6?"*

**Tests:** whether the candidate understands what his first two chapters measured. This is the question
I would ask if I wanted to find out how well he knows work he did two years ago and did not do alone.
**A strong answer contains:** an immediate concession — the static task's input embeds the target's own
category, so those absolute values measure label survival through graph convolution, not inductive
category inference; followed by the correct scoping — the chapters' *conclusions* are about the MTL
arm versus the single-task arm under an identical representation, so the comparison stands while the
absolute numbers do not travel; and finally the observation that this is one more reason the arc moved
to a sequential pair, where the target's features are outside the window.
**What the text supports — nothing.** p. 32 states the node features, p. 33 states the task, and no
sentence in 94 pages connects them. Chapter 5 says the analogous sentence about its own representation
(p. 66) but the frame never carries it back. Ch. 4's gains of "20.2 to 22.0 percentage points" (p. 54)
are the largest numbers in the document and sit on exactly this construction, unqualified.
**The candidate is fully exposed here and must not improvise.** If the answer is "we never separated
that", say it — an honest "isso a pesquisa não explorou" costs far less than a constructed defence.
See MAJOR-3.

---

### Q9 — statistics (bank Q10)
> *"Vinte modelos ajustados, mas o teste pareia quatro médias. Então o n é quatro, sobre uma única
> partição fixa. Isso sustenta 'supera' em seis conjuntos de dados com correção de Holm?"*

**Tests:** whether the candidate knows what his own inferential unit is — and whether he can defend a
three-degrees-of-freedom test.
**A strong answer contains:** the arithmetic said plainly (4 seeds × 5 folds = 20 fitted models; the
test pairs the four per-seed means, n=4, 3 df); why the paired *t* carries the verdict (at n=4 the
exact one-sided Wilcoxon floors at 0.0625 and cannot reach significance whatever the effect); the fact
that the registered Wilcoxon is reported alongside and agrees, with all 20 folds favouring the joint
model at every dataset; the effect-size argument — gains of 5.33 to 9.35 macro-F1 against cross-seed
standard deviations of 0.01 to 0.10 are not marginal at any plausible n; and the honest limit, which
is that one fixed partition means the intervals do not cover uncertainty over resampled user splits.
**What the text supports — all of it, and unprompted.** p. 67 states the departure from the registered
test and why. p. 17 volunteers the scope limit: "All four seeds reuse the same fold partition, so the
reported intervals do not cover uncertainty over resampled user splits." p. 72 gives the fold-level
agreement. `GLOSSARY.md:79` fixes the convention and the document obeys it — I checked for the banned
phrasing "twenty repetitions" and it appears nowhere. **Pass, and better than most published papers in
this area.** The residual honest concession, which the candidate should offer rather than wait for: a
fixed partition means fold-composition luck is a systematic, not a sampled, component of every reported
interval.

---

### Q10 — checkpoint selection
> *"A época é escolhida na mesma partição em que a nota é lida. O senhor divulga isso e diz que os
> valores absolutos são otimistas. Otimistas em quanto?"*

**Tests:** whether disclosure is doing real work or is a shield.
**A strong answer contains:** the honest answer that the magnitude was not measured, because measuring
it needs a third split the protocol does not have; plus the argument the text already makes — the rule
is applied identically to both arms on the same folds, and the *dedicated* arm receives the wider
search (a per-dataset sweep over batch size and learning rate, against one fixed configuration for the
joint model), so the residual favours the comparator and the reported difference is conservative; plus
the refusal to overclaim, which the chapter already prints.
**What the text supports — the argument, not the magnitude.** p. 73–74 makes the case cleanly and then
declines the tempting step: "It does not follow that the bias cancels exactly." That last sentence is
what distinguishes a disclosure from an excuse, and I would say so. **The disclosure is adequate.**
What it cannot do is bound the absolute values, and the candidate should not let a friendly examiner
talk him into implying otherwise. The correct forward statement is the one in §6.4's spirit: a held-out
third split is the experiment that would close it.

---

### Q11 — the mechanism (bank Q5)
> *"Com o caminho da região congelado na inicialização, o ganho de categoria sobrevive inteiro. Então
> não há transferência entre tarefas. Em que sentido esta dissertação mostra que 'aprendizado
> multitarefa ajuda'?"*

**Tests:** whether the candidate's framing survives his own best control. This is the question that
separates a candidate who reports results from one who understands them.
**A strong answer contains:** no retreat. The distinction between *multi-task learning helps* and
*task B teaches task A* — the dissertation demonstrates the first and explicitly refutes the second for
the category half; the two are different claims and only the first was ever the research question. Then
the positive content: the region half is genuine joint benefit (+2.10 to +2.20 Acc@10 at Texas and
California, outside the two-point margin, from a model whose category loss is co-trained), the
capacity-matched control rules out parameters-alone, and the operational claim — one artifact, one
forward pass — is unaffected by mechanism. And then the concession: "helps" in the title's sense is
carried by the joint architecture, and for the category task the mechanism is a stronger shared trunk,
which is a *weaker and more interesting* claim than transfer.
**What the text supports — the refutation, stated as a finding rather than buried.** p. 72: "We
therefore attribute the category gain to a stronger shared trunk, not to the region task teaching the
category one … We report this attribution as a finding, not a hypothesis." p. 76 repeats it in the
frame. I traced the control to `W6_ENCODER_ISOLATION.md` and the three values (63.50, 63.67, 79.79)
and their deltas (+7.63, +6.54, +4.64) reproduce exactly, as does the single-seed n=5 footing the
chapter discloses.
**Where I would press:** the abstract and title still read as a multi-task-learning result, and a
reader who stops at p. 5 will not learn that the larger half of the headline is an architecture effect.
That is not dishonest — §6.2 says it plainly — but the candidate should be ready to defend the framing
rather than discover the tension at the table.

---

### Q12 — baselines and tuning effort (bank Q11 + Q7)
> *"Os modelos dedicados foram ajustados com o mesmo esforço que o seu? E a HGI — o senhor a usa fora
> do propósito para o qual foi publicada, e ainda a re-ajustou. Por que isso não é um baseline
> enfraquecido?"*

**Tests:** baseline fairness, the place where MTL papers most often cheat.
**A strong answer contains:** the direction of the asymmetry — the dedicated category model is tuned
*per dataset* over batch size and learning rate while the joint model runs one configuration fixed
across all six datasets (p. 68), so the tuning asymmetry favours the *comparator*; the HGI answer in
two parts, that the repurposing is declared and that the re-tuning *raised* the baseline (0.4 → 0.7
cross-region edge weight, category F1 rising monotonically 0.74 → 0.82 on Alabama, p. 20), which is
strengthening a baseline, not sabotaging one; and the width concession for Ch. 4, which the frame
already volunteers.
**What the text supports — all three, and the concessions are volunteered.** p. 68 states the tuning
asymmetry against the candidate's own interest. p. 20 declares the repurposing — "Huang et al. present
HGI as a method for urban region representation … so the work reported here repurposes its POI-level
output" — and the tuning in the same breath. p. 75 concedes Ch. 4's width asymmetry: "the decomposed
input is wider than the place embedding it replaces, 192 dimensions against 64, and Chapter 4 states
that an equal-dimension control would be needed." **Pass.** One caution: the swept "category F1"
values on p. 20 carry an unresolved averaging convention in the source (MODERATE-3); do not defend
0.74 → 0.82 as macro-F1 unless that is confirmed.

---

### Q13 — ethics and data governance (bank Q18)
> *"O objeto desta dissertação são trajetórias individuais de pessoas reais. Não encontrei uma única
> frase sobre privacidade, licenciamento ou re-identificação em 94 páginas. Por quê?"*

**Tests:** whether the candidate has thought about the object of study as data about people.
**A strong answer contains:** no defensiveness. The data is public and observational with no
intervention and no direct identifiers; the consumed copy is Figshare DOI
10.6084/m9.figshare.22126586.v2 under CC0, with the honest caveat that CC0 was applied by a
third-party depositor whose upstream source is unreachable and whose rights basis is unestablished;
and then the part that earns the answer: the *model* is the exposure, not the training data — ranking
ten census tracts for a user's next visit is a re-identification surface, and the user-disjoint
protocol makes that concrete, since the whole point is that predictions generalize to users the model
never saw.
**What the text supports — nothing at all.** Zero matches across the full text. The evidence to write
the answer exists in the repository (`src_utils/evidence/DATASET_LICENSING_FINDINGS.md`, verified against the
Figshare API this session) but reaches no page. **This is the one question where the document offers
the candidate no cover whatsoever, and it is a question a Brazilian banca in 2026 will ask.**
See MAJOR-4.

---

### Q14 — external validity and data vintage (bank Q13 + Q14)
> *"Check-ins de 2009 a 2011 representam mobilidade hoje? E o que acontece com usuários e POIs raros?"*

**Tests:** whether the external-validity argument is made or merely available.
**A strong answer contains:** the argument the design already makes — Istanbul is the non-U.S. check,
a different continent, a different administrative region unit (mahalle), a different source collection
(Massive-STEPS), and the category result repeats there (+8.58 macro-F1, p. 73); the concession that
one city is a thin base, which limitation 5 already states; the vintage concession; and, for the rare
tail, the concrete protocol facts — a region never seen in training counts as a miss (p. 67, so the
figure is not inflated by unpredictable new regions), and macro-F1 weights all seven categories
equally so the rare classes cannot be ignored.
**What the text supports — fully, including the discipline about what Istanbul does *not* show.** p. 73:
"The comparable quantity is the gain over the ceiling, not the absolute Acc@10, since region counts
differ across datasets." **Pass.** The vintage inconsistency of MODERATE-1 will surface here, so fix it
before it does.

---

### Q15 — cost and use (bank Q17)
> *"O modelo conjunto tem quatro vezes mais parâmetros que os dois dedicados somados. Onde está a
> economia?"*

**Tests:** whether the practical claim is calibrated, since "one model instead of two" invites the
assumption of cheapness.
**A strong answer contains:** the refusal of the easy claim — the joint model is *larger* and a forward
pass costs *more* than running the two small dedicated models; the benefit is operational, one artifact
to train, version and deploy, and one forward pass over one set of inputs; plus the honest note that
Chapter 3's convergence result runs the other way (the joint model needed 80.88 s against a cumulative
34.97 s, p. 40) and that the arc never claimed a compute win.
**What the text supports — exactly, and pre-emptively.** p. 64: "the joint model has about 4.2 million
parameters at Alabama against 1.1 million for the two dedicated models combined (5.2 against 2.0 at
California). What the single model provides is operational rather than arithmetic." **Pass.** Refusing
a claim the reader would have granted is the behaviour that most raises my confidence in the rest of
the numbers.

---

## 5 · Questions the candidate must be able to answer aloud

These have no adequate answer in the document. They are not defects in every case — some are simply
beyond a written text's scope — but each will be asked, and improvisation will cost more than
preparation.

1. **Which leakage channels remain unbounded, named one by one, and what fraction of the data does
   each touch?** (Q7. The text gives the 67–87 percent coverage figure but never enumerates the
   complement.)
2. **Does the leak channel, if open, threaten the MTL-versus-STL comparison or only the absolute
   scores — and does the same protection extend to Table 9's place-level comparison?** (Q7 (iii)–(iv).
   The symmetry argument is the candidate's strongest defence and it is nowhere in the document. The
   Table 9 exception is the one he must volunteer rather than concede under pressure.)
3. **What do Tables 2 and 6 measure, given that the target's category is a node input feature?**
   (Q8. No sentence in the document addresses this.)
4. **Whose code ran the Chapter 4 experiments, and does the Appendix A platform claim cover them?**
   (Q3/MINOR-2. The author's own comment records this as unsettled.)
5. **By how much does epoch-on-the-scored-fold selection inflate the absolute numbers?** (Q10. The
   honest answer is "unmeasured, and here is the experiment that would measure it." Say the second
   half.)
6. **In what sense does the dissertation show that multi-task learning helps, given the freeze
   control?** (Q11. §6.2 answers it; the abstract does not, and the candidate should be fluent in the
   distinction between *joint training helps* and *task B teaches task A*.)
7. **What are the privacy, licensing and re-identification considerations?** (Q13. Zero pages of
   cover. The Figshare/CC0 depositor caveat is the specific fact to have ready.)
8. **Why do Texas and California counts differ between chapters when Appendix B.4 discusses only
   Florida?** (Q4/MAJOR-2.)
9. **Is the Arizona category gain of +9.35 stable, given the pending ceiling top-up?** (MODERATE-2.
   The abstract's upper endpoint depends on the answer.)
10. **Was the swept "category F1" of p. 20 macro-averaged or weighted?** (MODERATE-3. A one-word
    answer, and the wrong one in front of a committee is expensive.)

---

## 6 · What impressed me (do not edit this away)

Recorded because a correction round is exactly when good things get flattened.

- **The time-capsule prefaces.** Each article chapter opens with an italic paragraph naming venue,
  status, and precisely which of its own conclusions later chapters revise (pp. 27, 43, 58). It solves
  the hardest problem in the coletânea format — a reader encountering a superseded claim as if it were
  current — and it solves it at the point of reading. Keep every word.
- **§6.2's capacity-matched control.** Frame-level evidence generated *for the dissertation*, closing
  an explanation no individual paper closes, reported with its own scope limits ("two of the six
  datasets, one width point per dataset, and width scaling rather than depth", p. 77). This is the
  single strongest argument that the collection is a dissertation.
- **The freeze control reported against the candidate's own interest** (p. 72), and labelled "a
  finding, not a hypothesis". Most authors would have left this in a drawer. Reporting it is what makes
  the rest of the chapter credible.
- **Verbs bound to tests, enforced document-wide.** p. 25 states the contract — "outperforms" follows
  only from a paired superiority test, "matches" only from non-inferiority within the stated margin —
  and I could not find a violation. Arizona is reported as a match with the interval centred on zero;
  Alabama's small significant deficit is reported *as* a deficit (p. 72) rather than rounded into a tie.
- **The refusal sentences.** "It does not follow that the bias cancels exactly" (p. 74). "The
  measurement bounds this channel rather than closing it" (p. 66). "We read this as a defense of the
  parallel design, not a claim that we outperform the cascade" (p. 73). "This remains motivation, not a
  measured service result" (p. 74). Each declines a claim the reader would have granted. That habit is
  worth more to this dissertation's credibility than any single result in it.
- **Appendix B as a genuine errata**, including corrections applied to the *version of record* and a
  table of claim-scope narrowings where the strength of a claim was reduced and never raised (Table 14,
  p. 91).
- **Every number I traced, reconciled.** I checked the joint-best table against
  `joint_best/JOINT_BEST_RESULTS.md`, the ceilings against `CEILINGS_N20_FINAL.md`, the capacity control
  against `capacity_matched_summary.json`, the freeze control against `W6_ENCODER_ISOLATION.md`, the
  forward-edge decimals against `RESCREEN.md`, the transductive figures against `A4_RESULTS.md`, and I
  recomputed the Markov region floor from the six committed JSONs: the chapter's "reaches 51 to 72
  Acc@10" and "exceeds it by 4.9 to 10.3 points" (p. 72) come out at 51.2–72.5 and 4.94–10.29. **Not one
  headline number failed its trace.** For a document of this size that is unusual, and it is the reason
  four stray characters on page 21 produce a corrections list instead of a different verdict.

---

## 7 · Scope note

Per the persona's hard limits, this review does not judge UFV formatting minutiae (persona 13) and does
not copyedit (persona 02); MINOR-1 is listed only because it renders inside a sentence already broken by
BLOCKER-1. Out-of-scope handoffs, one line each: **persona 13** — confirm that the approval-sheet
placeholder on p. 2 is replaced before deposit; **persona 05** — `references.bib` ships 97 of 99 entries
to the bibliography, which is a citation-integrity matter beyond the four `(??)`; **persona 06** — the
AZ ceiling's pending top-up (MODERATE-2) and the p. 20 averaging convention (MODERATE-3) are open
number-gate items.

*Read-only review. No file in the dissertation was modified. Findings are proposals; the author rules.*


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-26 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
