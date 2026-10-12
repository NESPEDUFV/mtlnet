# 63 · Audit of author items 31-36 — the conclusion chapter and its craft

> 🛑 **GERACAO SUPERADA — nenhum numero medido deste ficheiro pode ser citado.**
>
> Isto e a auditoria do capitulo de conclusao (itens 31-36 do autor), corrido **antes** de a geracao v18 fechar o vazamento de rotulo no grafo de
> visitas consecutivas (fechado em 2026-08-13). As celulas de macro-F1 medidas aqui vem da
> geracao com vazamento e **nao sao as do documento entregue**.
>
> **Como reconhecer uma celula morta sem a copiar daqui:** a categoria entregue vive na casa dos
> **30 a 38**. Qualquer valor de categoria muito acima disso neste ficheiro e da geracao anterior.
>
> **O que este ficheiro ainda vale:** o registo de que estas questoes foram levantadas, por quem,
> e o que se decidiu. O raciocinio e o processo continuam legiveis. So os **valores medidos**
> e que caducaram.
>
> Antes de agir sobre qualquer coisa aqui, ler `VEREDITOS.md` na raiz da pasta.


> **Measured against the WORKING TREE**, not the built PDF. Baseline `HEAD=82080ce4`, with
> `src/chapters/6_conclusion.tex` uncommitted (`git status --porcelain` shows ` M
> articles/dissertacao/src/chapters/6_conclusion.tex`). File mtimes read this session:
> `src/chapters/6_conclusion.tex` = **2026-08-03 20:37:29**, `src/build/main.pdf` =
> **2026-08-03 21:02:30**. The PDF is therefore **25 minutes NEWER** than the chapter source, not
> stale by 14 minutes as the task brief states — the brief's staleness premise does not hold for
> this file at this moment. Command:
> `cd articles/dissertacao/src && stat -f '%N mtime=%Sm' -t '%Y-%m-%d %H:%M:%S' build/main.pdf chapters/6_conclusion.tex`
> Every quote below is from the SOURCE file. Chapter 6 renders at build pages **83-87**
> (located by text search over `build/main.pdf`; page 83 opens `6 Conclusion This dissertation
> asked whether multitask learning helps point-of-intere...`).
>
> **Instrument used for every sweep** (`/tmp/pgrep.sh`, V4-compliant — blanks full-line comments
> *in the file* while preserving line numbers, so reported `file:line` are true source lines):
> ```bash
> #!/bin/bash
> pat="$1"; shift
> for f in "$@"; do sed 's/^[[:space:]]*%.*$//' "$f" | grep -HniE --label="$f" "$pat"; done
> ```
> **V3/V17 validation of that instrument, run before any absence was reported:**
> `/tmp/pgrep.sh 'This dissertation asked whether' chapters/6_conclusion.tex` returns
> `chapters/6_conclusion.tex:15:` (positive control: it finds a string at a known line);
> `/tmp/pgrep.sh 'ambos usaram o mesmo recorte' chapters/6_conclusion.tex` returns nothing although
> that string IS in the file inside a `%` comment (negative control: comments are correctly
> excluded); `/tmp/pgrep.sh 'cross-attention' $(find . -name '*.tex')` returns **18** lines
> (positive control that the whole-tree file list is actually read). Only after those three did I
> report any zero.
>
> Section line spans in `6_conclusion.tex` used throughout, from
> `grep -n 'section{\|chapter{' chapters/6_conclusion.tex`:
> chapter opener 12-33 · §6.1 34-115 · §6.2 116-292 · §6.3 293-414 · §6.4 415-435 · §6.5 436-445.

---

## ITEM 31 — the opening sentence omits the static task

**Author's premise.** The chapter-6 opening says the dissertation examined next-category and
next-region prediction, and "esquecemos de falar sobre o poi-classification".

**Verdict: PARTLY_CONFIRMED.** His quotation is stale, his observation about the opening sentence
is correct, and his implied conclusion (that it is a forgetting) is not supported: the omission is
the document's own consistent scoping rule, and Chapter 6 does state the three-task structure
twice, elsewhere.

### 31.1 His quote is not the live text

He quotes: *"This dissertation examined whether multitask learning helps next-category and
next-region prediction and what determines the answer."* That string returns zero hits.
`/tmp/pgrep.sh 'This dissertation examined' $(find . -name '*.tex')` → no output, against the
validated instrument above. The live opening is `6_conclusion.tex:15-17`:

> This dissertation asked whether multitask learning helps point-of-interest prediction
> for the next category and the next region of a visit, and which design choices
> determine the answer.

The difference is wording only ("asked" for "examined", "point-of-interest prediction for the next
category and the next region of a visit" for "next-category and next-region prediction", "which
design choices determine" for "what determines"). **The task list is identical, so his point
survives the staleness intact.**

### 31.2 The opening does omit static category classification — and so does the research question, by design

`NORTH_STAR.md:12-13` states the research question as two tasks:

> **Does multi-task learning help point-of-interest prediction (next category + next region),
> and what does the answer depend on?**

`1_introduction.tex:97` §Research question repeats it verbatim in bold:

> \textbf{Does multitask learning help point-of-interest prediction (next category and
> next region), and what does the answer depend on?}

`1_introduction.tex:162-163` §Objectives, general objective:

> The general objective is to determine whether multitask learning helps next-category
> and next-region prediction and to identify the conditions that shape the answer.

The chapter-6 opening is therefore a faithful echo of both. **The document's pattern is:
the research question names two tasks; the static task appears one level down, at the chapter
level.** That pattern is visible inside Ch.1 itself — specific objective 1
(`1_introduction.tex`, enumerate item 1) reads:

> Evaluate whether a joint model with hard parameter sharing benefits static
> category classification and next-category prediction when compared with
> dedicated single-task models (Chapter~\ref{ch:cbic}).

and `1_introduction.tex:135-139` states the pair change explicitly:

> The task pair thus changes across the studies: the first two combine static category
> classification with next-category prediction, whereas the final study combines
> next-category and next-region prediction.

### 31.3 The three-task structure IS stated in Chapter 6, twice

`/tmp/pgrep.sh 'static category classification|static task|category classification' chapters/6_conclusion.tex`
returns exactly three prose lines:

- `6_conclusion.tex:38-39` (§6.1, the Ch.3 recap):
  > The model combined static category classification and next-category prediction.
- `6_conclusion.tex:51` and `:88-90` (§6.1, the Ch.4 recap and its qualification):
  > The chapter reports results for both tasks. On the static task, category macro-F1 rose by
  > 20.2 to 22.0 percentage points across the three states tested.
  > […] The static task classifies a place from that place's own representation, so its input
  > already determines its target.
- `6_conclusion.tex:393-397` (§6.3, limitation 6):
  > Chapters~\ref{ch:cbic} and~\ref{ch:courb} paired static category classification with
  > next-category prediction, while Chapter~\ref{ch:mobiwac} pairs two sequential targets […]

So the reader of Chapter 6 meets the static task in the second paragraph of §6.1, twelve lines
after the opening sentence. **This is not an omission that misrepresents the work.** It is a
one-sentence scope statement whose scope is the research question, followed immediately by the
full three-task history.

### 31.4 What it would take

Adding the static task to the opening sentence would make the chapter-6 opening state a
research question that `NORTH_STAR.md:12-13`, `1_introduction.tex:97` and
`1_introduction.tex:162-163` do not state — three loci, two of them frame prose the author has
already approved. That is not a copy edit; it is a change to the dissertation's declared research
question and it propagates. The cheap alternative, if the author wants the static task visible
earlier, is one clause in the *second* sentence of the chapter (which currently reads "Three
studies addressed this question", `6_conclusion.tex:17-18`) naming that the first two studies
paired the sequential target with a static one — a single sentence inside Chapter 6, touching
nothing else.

**Disposition: I_DECIDE.** The premise is his own research question; only he can widen it.

---

## ITEM 32 — "the gain does not come from the region task teaching the category task"

**Author's premise.** That sentence is in §6.2 paragraph 2 and is badly wrong: the fixed-region
control only proves the *loss* was not contributing, while cross-attention and other artifacts
still do contribute to the gain. He asks for the same error to be swept for elsewhere.

**Verdict: REFUTED as to the quoted sentence and as to the defect; his scientific distinction is
correct and the live text already makes it, verbatim.** This is the ALREADY-SATISFIED outcome.

*(Vocabulary note: his "cross-switch" is his own term. The licensed name is **cross-attention**
(GLOSSARY §2, "the joint model" row: "shared cross-attention trunk"). I record the translation and
do not adopt his word.)*

### 32.1 FIRST — the location. Confirmed independently: the quoted string does not exist

Two sweeps, both against the validated instrument, both over all 61 `.tex` files under `src/`
(`find . -name '*.tex'`), comments stripped:

```bash
# exact substring, line-based
for f in $(find . -name '*.tex'); do grep -v '^[[:space:]]*%' "$f" | grep -q 'does not come from' && echo "HIT $f"; done
# same, but line-wrap-tolerant (join all prose lines, then match)
for f in $(find . -name '*.tex'); do out=$(grep -v '^[[:space:]]*%' "$f" | tr '\n' ' ' | grep -o 'gain does not come from[^.]*'); [ -n "$out" ] && echo "$f :: $out"; done
```
Both return **zero hits**. Per V13/V17 I proved the pipeline is not broken by running the identical
wrap-tolerant pipeline on two strings I knew were present:

```
POSITIVE-CONTROL-HIT ./chapters/6_conclusion.tex :: does not require training transfer from the region task
POSITIVE-CONTROL-HIT ./chapters/5_mobiwac/06_results.tex :: rules out the region task teaching the category one, since the gain survives with the region pathway untrained
```

**His quoted sentence is not in the document.** It is an earlier revision he read.

### 32.2 The two nearest live wordings, quoted in full

**(A) `6_conclusion.tex:151-157`** — the closing of §6.2's second paragraph (paragraph span
119-157, so this is indeed the paragraph he means):

> The control used one random initialization over five folds and was designed for one matched
> comparison: the fixed-region joint model against the dedicated category model under
> the same training configuration. At Alabama, Arizona, and Florida, the fixed-region
> model retains its category advantage. Within this control, the category improvement
> therefore does not require training transfer from the region task. The result rules out
> that explanation, but it does not determine whether the gain comes from the category
> encoder, the feed-forward blocks, the added depth, cross-attention, or a combination of
> these components.

**(B) `5_mobiwac/06_results.tex:203-209`** — the chapter-5 original:

> The control therefore rules out one reading and narrows the rest. It rules out the region task
> teaching the category one, since the gain survives with the region pathway untrained. What it leaves
> is the joint architecture itself, and the control does not say which part of it: freezing the region
> stream removes region training, not the category stream's own encoder, the per-stream feed-forward
> blocks, or the added depth. We therefore report the negative result, that the gain is not cross-task
> transfer, as a finding, and we attribute the gain to the joint architecture rather than to any named
> component of it.

### 32.3 SECOND — the merit. The live text already makes exactly his distinction

His complaint has two halves and the live text answers both, in the same sentence:

| His half | Where the live text says it |
|---|---|
| the control only rules out the **loss / training signal** | `6_conclusion.tex:147-150`: "This removes learning from the region side, so that task cannot provide a training signal to the category task, **but it leaves the rest of the joint architecture in place**"; and `:153` scopes the verdict to "**does not require training transfer**", not "does not benefit from the region task" |
| **cross-attention and other artifacts still contribute** | `6_conclusion.tex:154-157` names them one by one and refuses to exclude them: "it does not determine whether the gain comes from the category encoder, the feed-forward blocks, the added depth, **cross-attention**, or a combination of these components" |

The claim is additionally fenced twice more in the same section:

- `6_conclusion.tex:243-244`: "The available evidence supports attributing the category gain to
  the joint architecture as a whole, not to one component."
- `6_conclusion.tex:269-272`: "Together, the controls exclude two explanations within the
  settings in which they were evaluated: direct training transfer from the region task
  and parameter count alone. They do not isolate which remaining component of the joint
  architecture produces the gain."

And the cosine appendix carries the same guard for the *other* instrument, `apx_f_cosine.tex:475-477`:

> Orthogonal gradients also do not mean that the tasks share no knowledge: the two streams
> still exchange information through the cross-attention trunk, a sharing mechanism this measurement
> does not read.

**Nowhere does live prose say the gain does not come from sharing.** Every locus says the gain
does not come from *region-task training signal*, and immediately says the architecture — naming
cross-attention — remains a live candidate. **ITEM 32 IS ALREADY SATISFIED.**

### 32.4 THIRD — the sweep he asked for, per hit

Instrument: a sentence-level sweep (`/tmp/sweep32.py`) over all `chapters/*.tex`,
`chapters/*/*.tex`, `tables/*/*.tex`; full-line comments dropped, inline `%` tails stripped, lines
joined so sentences that wrap are matched whole, patterns
`teach|transfer|share knowledge|does not come from|rules? out|negative transfer|stopped hurting|knowledge from|inter-task|cross-task|one task .{0,30}the other`.
Validated by the two positive controls in §32.1. Thirty-one sentences matched. The ones that make
or deny a claim about inter-task transfer *in this dissertation's own results* are these; the rest
are definitional or describe other authors' systems.

| file:line | sentence (abridged where marked) | verdict |
|---|---|---|
| `6_conclusion.tex:153` | "Within this control, the category improvement therefore does not require training transfer from the region task." | **CLEAN.** Scoped by "Within this control" and by "training transfer"; followed at `:154` by the non-exclusion list. |
| `6_conclusion.tex:154-157` | "The result rules out that explanation, but it does not determine whether the gain comes from the category encoder, the feed-forward blocks, the added depth, cross-attention, or a combination of these components." | **CLEAN — this is the sentence that satisfies his request.** |
| `6_conclusion.tex:269-272` | "Together, the controls exclude two explanations within the settings in which they were evaluated: direct training transfer from the region task and parameter count alone. They do not isolate which remaining component…" | **CLEAN.** Both the scope clause and the non-isolation clause present. |
| `6_conclusion.tex:122` | "Negative transfer between the static and sequential tasks was one possible explanation." | **CLEAN.** Reports Ch.3's hypothesis as a hypothesis. Matches `apx_b_errata.tex:368-369`, which corrects the submitted MobiWac manuscript for saying Ch.3 *observed* negative transfer. |
| `6_conclusion.tex:43-45` | "The analysis identifies three possible causes: task dissimilarity and the resulting risk of negative transfer, …" | **CLEAN.** "possible causes", "risk of". |
| `5_mobiwac/06_results.tex:203-204` | "It rules out the region task teaching the category one, since the gain survives with the region pathway untrained." | **CLEAN, but this is the one closest to his complaint.** Standing alone the clause reads stronger than the Ch.6 version. It is immediately repaired by `:204-207` ("What it leaves is the joint architecture itself, and the control does not say which part of it: freezing the region stream removes region training, not the category stream's own encoder, the per-stream feed-forward blocks, or the added depth"). No edit is owed; but if the author wants a single locus tightened, this is it, and it is Ch.5 prose (published-status chapter — check the errata policy at `NORTH_STAR.md §5.7` before touching). |
| `5_mobiwac/06_results.tex:207-209` | "We therefore report the negative result, that the gain is not cross-task transfer, as a finding, and we attribute the gain to the joint architecture rather than to any named component of it." | **CLEAN.** The second half of the sentence is the guard. |
| `5_mobiwac/06_results.tex:193-194` | "A reader used to multitask learning~\cite{caruana1997multitask} expects the harder task … to teach the easier one; a control shows otherwise. We fix the region pathway at its initial values … so it can neither learn nor teach the category task…" | **CLEAN.** Framing device; "teach" is defined by the freeze operation in the next clause. |
| `apx_f_cosine.tex:475-477` | "Orthogonal gradients also do not mean that the tasks share no knowledge: the two streams still exchange information through the cross-attention trunk, a sharing mechanism this measurement does not read." | **CLEAN — and it is the strongest statement of his own point anywhere in the document.** |
| `apx_f_cosine.tex:95-96` | "when the two tasks ask for opposite updates, one task improves at the other's expense" | **CLEAN.** Definitional, introduces the measured quantity. |
| `apx_b_errata.tex:366-369` | records that the submitted manuscript wrongly said Ch.3 observed negative transfer between next-category and next-region | **CLEAN.** This is the erratum, not the error. |
| `2_fundamentals.tex:806-812`, `:832`, `:967` | Definition 2.x of negative transfer; "task relationships must be measured rather than assumed~\cite{standley2020tasks}"; "Gradient conflict describes one source of negative transfer" | **CLEAN.** Definitional. |
| `3_cbic/*`, `4_courb/*`, `tables/cbic/errata.tex` | eight hits, all inside the re-typeset published chapters, describing MTL in general or Ch.3's own hypotheses | **OUT OF SCOPE for this item.** None claims or denies transfer in the Ch.5 result. |

**Zero defects found.** No live sentence anywhere attributes the gain to inter-task transfer, and
no live sentence denies that sharing contributes.

### 32.5 FOURTH — compliance with the NORTH_STAR §6 Ch.6 wording constraint

`NORTH_STAR.md` §6, Ch.6 beats, N3 mechanism block:

> "Sharing stopped hurting", never "the tasks teach each other". NEVER credit the parameter count —
> disclosed as cost.

Checked with `/tmp/pgrep.sh 'stopped hurting|teach each other|teaches each|parameter count' $(find . -name '*.tex')`:

- **"the tasks teach each other"** — **0 hits anywhere.** COMPLIANT.
- **"sharing stopped hurting"** — **0 hits anywhere.** The prescribed *positive* phrase is not used
  either. This is a deviation from the beat's letter, not its spirit: Ch.6 delivers the same
  content through `:154-157` and `:269-272` rather than through that idiom. Reporting it rather
  than smoothing it: **the beat's licensed phrase is absent from the chapter.** Whether that
  matters is the author's call; the phrase itself is a repo idiom, not glossary vocabulary.
- **"parameter count"** — 3 hits, all in `6_conclusion.tex` (`:116`, `:127`, `:130`), and all three
  *deny* it as an explanation ("increasing the parameter count alone did not improve the dedicated
  model"; "the controls exclude two explanations … and parameter count alone"). The beat says never
  *credit* it. **COMPLIANT.**

### 32.6 Appendix F, as instructed

`apx_f_cosine.tex` measures the epoch-level cosine between task gradients on the shared trunk:
4,650 observations from seven datasets, five-fold user-disjoint CV over fifty epochs, fold as unit
of independence (`:168-171`, `:257-259`); equivalence to zero by TOST against ±0.05 (`:279-283`);
every dataset equivalent to zero (`:314-316`). Critically for item 32, the appendix draws the
distinction the author is asking for and states its own blind spot at `:475-477` (quoted above):
orthogonality is about *gradients*, and it explicitly does **not** license "the tasks share no
knowledge", because the cross-attention exchange is a sharing mechanism the measurement cannot
see. Ch.6 §6.2 paragraph 6 (`:274-284`) cites the appendix and inherits that scope, closing with
"This result measures directional conflict only and applies to this pair of tasks."

**Disposition: YOU_APPLY — where "apply" means record the item as ALREADY SATISFIED and close it.**
No prose change is required or recommended. The only optional, author-gated tightening is the
Ch.5 clause at `06_results.tex:203-204`, and it is already repaired in the following sentence.

---

## ITEM 33 — §6.1 should carry fewer numbers than §6.2

**Author's premise.** "Contributions by chapter" should foreground conceptual contributions and
findings and use numbers only where necessary; results belong in "The consolidated answer".

**Verdict: PARTLY_CONFIRMED.** The ratio he assumes already holds — §6.2 carries three times the
numerals of §6.1 in absolute terms and roughly twice the density. But §6.1 does carry three
result numbers that are not needed to state a conceptual contribution, so a small, bounded move is
defensible.

### 33.1 The measurement

Command, from `articles/dissertacao/src`:

```bash
python3 - <<'PY'
import re
L=open('chapters/6_conclusion.tex',encoding='utf-8').read().split('\n')
S={'6.1':(34,115),'6.2':(116,292),'6.3':(293,414),'6.4':(415,435),'6.5':(436,445)}
SP=r'\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|sixty|hundred|thousand|million)\b'
for k,(a,b) in S.items():
    d=s=0
    for i in range(a-1,b):
        l=L[i]
        if re.match(r'^\s*%',l): continue                       # V4: strip comment lines
        l=re.sub(r'(?<!\\)%.*$','',l)                           # V4: strip inline comments
        l=re.sub(r'\\(ref|label|cite|input|includegraphics)\{[^}]*\}',' ',l)   # EXCLUDED: cross-refs
        l=re.sub(r'macro-F1|Acc@10|Check2HGI|MTLnet|ST-MTLNet|limitation~?\d+','TERM',l)  # EXCLUDED: names, pointers
        d+=len(re.findall(r'\d+(?:[.,]\d+)*',l)); s+=len(re.findall(SP,l,re.I))
    print(k,'arabic=',d,'spelled=',s,'total=',d+s)
PY
```

**V2 — what this filter EXCLUDES and how many.** Before the exclusions the raw counts were
§6.1 arabic 10, §6.2 arabic 24, §6.3 arabic 3, §6.4 arabic 6. The filter removes: (a) the "1" in
`macro-F1` — 3 in §6.1, 3 in §6.2, 0 elsewhere; (b) `limitation~N` structural pointers — 6 in
§6.4, which is why §6.4 drops from 6 to 0; (c) `\ref`/`\cite`/`\label` internals — 0 numerals
reached the count from these in any section, they are stripped defensively. Nothing else is
excluded. `Acc@10` and the model names appear in the filter but contribute no removals in Ch.6.
V3 control on a line with a known count: the instrument returns `['56.16','1.89']` for
`6_conclusion.tex:253`, which is exactly the two data numerals present.

| section | arabic numerals | spelled quantities | total | prose words | numerals per 100 words |
|---|--:|--:|--:|--:|--:|
| §6.1 Contributions by chapter | **7** | 14 | **21** | 469 | 4.5 |
| §6.2 The consolidated answer | **21** | 32 | **53** | 851 | 6.2 |
| §6.3 Limitations | 2 | 8 | 10 | 214 | 4.7 |
| §6.4 Future work | 0 | 3 | 3 | 156 | 1.9 |
| §6.5 Final remarks | 0 | 2 | 2 | 87 | 2.3 |
| chapter opener (12-33) | — | — | — | 129 | — |

Word counts from the same script with the numeral counters replaced by a token count after macro
stripping; chapter prose total 1,906 words.

### 33.2 The seven arabic numerals in §6.1, each with what it costs to move

| line | numeral | sentence role | movable? |
|---|---|---|---|
| `:50` | 64 | "replaced the single 64-dimensional place embedding with decomposed spatial, temporal, and categorical encoders" | **No.** It IS the conceptual contribution — the whole of Ch.4 is "monolithic 64-d in, decomposed encoders out". |
| `:52` | 20.2, 22.0 | "On the static task, category macro-F1 rose by 20.2 to 22.0 percentage points across the three states tested." | **Yes, and this is his strongest case.** It is a *result*, on the *static* task, and the very next paragraph (`:88-95`) spends four sentences explaining why it is not evidence about the sequential task. |
| `:91`, `:92` | 192, 64 | "The decomposed input is wider than the place embedding that it replaces, 192 dimensions against 64" | **No.** This is the width-confound disclosure; the numbers are the disclosure. |
| `:108` | 5.3, 9.4 | "outperforms … on the category task at all six datasets, by 5.3 to 9.4 macro-F1 points" | **Yes.** The clause "at all six datasets" carries the contribution; the range is a result. |

### 33.3 What moving a number costs (WRITING_LAW §3)

A number in this document travels with its reference point and its convention, so it cannot be
deleted in place — it moves with its hedges or the whole construction goes. Concretely:

- **The 20.2-22.0 pair** is bound to a task label ("On the static task"), a scope ("across the
  three states tested"), and a comparison ("larger than the improvements obtained from the
  architectural variations evaluated in the first study", `:53-54`), plus the two-qualification
  paragraph at `:88-95`. Moving the figure to §6.2 means moving four sentences, and §6.2 currently
  says nothing about the static task at all — it would have to acquire that thread. **The cheaper
  edit is to drop the figure and keep the direction**: "category macro-F1 rose sharply on the
  static task in every state tested, by more than the architectural variations of the first study
  produced" — but that is a claim-strength change (a quantified claim becomes a qualitative one)
  and therefore needs the author, not a copy edit.
- **The 5.3-9.4 range** at `:108` is inside the protocol sentence block (`:103-114`) that also
  carries n=20, four seeds, five folds, the TOST margin, and the registered-primary-analysis
  disclaimer. Removing just the range leaves that block intact and loses nothing structural — this
  is the one genuinely cheap deletion, because §6.2 `:125-127` already restates the same
  partition without the range.
- **Duplication is the real finding here.** The headline region partition is stated **three
  times** in Ch.6: `:23-25` (opener), `:107-110` (§6.1), `:125-126` (§6.2). Command:
  a wrap-tolerant sentence sweep for `all six datasets|four of the six|four datasets|non-inferior`
  over `6_conclusion.tex` returns those seven sentences. If the author wants §6.1 lighter, cutting
  the *numbers* from the §6.1 instance while keeping the partition words is a smaller and safer
  edit than moving anything.

**Size of the work:** two sentences touched (`:52` and `:108`), zero new claims, one claim-strength
decision. Under an hour including the numbers-ledger update.

**Disposition: I_DECIDE.** The §6.1-vs-§6.2 ratio he assumes already exists (53 vs 21); the
remaining question — whether a quantified claim may become qualitative in a recap — is a
claim-strength decision reserved to the author under WRITING_LAW §3.

---

## ITEM 34 — the three limitation sub-points

### 34(a) Data vintage — "we use the Massive steps from 2025"

**Verdict: REFUTED.** The author's sentence conflates the benchmark's *publication year* with the
*collection vintage* of its check-ins, and the live limitation is careful to be about Gowalla only.

**What §6.3 actually says** (`6_conclusion.tex:328-331`, limitation 1):

> \item \textbf{Data vintage.} The five state datasets come from
> Gowalla~\cite{cho2011gowalla}, and the extraction used here spans January 2009
> to August 2011 across the five states. Mobility patterns, place inventories,
> and check-in behavior have changed since.

The limitation is **scoped to the five Gowalla states** ("The five state datasets") and says
nothing about Istanbul. So the premise "the vintage is a problem, but we use Massive-STEPS from
2025" does not rebut a claim the text makes — the text already excluded Istanbul from the vintage
complaint.

**The provenance, from an openable source of record.** `references.bib` carries
`wongso2025massivesteps` as `@misc{... howpublished = {arXiv:2505.11239}, year = {2025}}`.
Opened this session: OpenAlex work `W4416143324`, DOI `10.48550/arXiv.2505.11239`,
`type: "preprint"`, `publication_date: 2025-05-16`, primary location arXiv, `is_published: false`,
no journal ref. Its abstract (retrieved from the same OpenAlex record) states the point directly:

> the over-reliance on older datasets from 2012-2013 […] Massive-STEPS spans 15 geographically and
> culturally diverse cities and features more recent (2017-2018) and longer-duration (24 months)
> check-in data than prior datasets.

**So: benchmark published 2025 (as a preprint); Istanbul check-ins collected 2017-2018.** Both are
newer than Gowalla's 2009-2011, and neither is "2025 data". The author's own sentence walks into
the trap. Note also that no live prose anywhere states the Istanbul vintage:
`/tmp/pgrep.sh '2017|2018' chapters/*.tex chapters/*/*.tex` returns no hit outside CBIC-2025 venue
strings. **Chapter 2 does gesture at the point** (`2_fundamentals.tex:1343-1345`): "Istanbul
check-ins come from Massive-STEPS, which also draws attention to the field's continued dependence
on old datasets~\cite{wongso2025massivesteps}."

**THE GATE.** Probe `R8-vintage` in `src_utils/check_audit_claims.py:91-92` requires the literal
string `August\s+2011` to be PRESENT in `chapters/6_conclusion.tex`:

```python
("R8-vintage", "Ch.6 data-vintage item prints BOTH Gowalla windows, the paper's and the measured one",
 "chapters/6_conclusion.tex", r"August\s+2011", True),
```
Confirmed present: `/tmp/pgrep.sh 'August 2011' chapters/6_conclusion.tex` →
`chapters/6_conclusion.tex:330`. **Any edit that removes or rewords that clause breaks the gate and
must say so explicitly and update the probe.** (Side observation, not this item's business: the
probe's *description* no longer matches the text it guards — it says "prints BOTH Gowalla windows",
but the author's ruling of 2026-07-30, recorded in the comment block at `:333-341`, removed the
paper's window and left only the measured one. The regex still passes because "August 2011" is in
the surviving half. Flagged as a stale probe description, not a broken gate.)

**What it would take.** If the author wants the Istanbul vintage stated so the limitation reads as
bounded rather than global, the honest one-clause addition is: the Gowalla span stays exactly as
printed (gate), and one sentence is added naming Istanbul's 2017-2018 window, sourced to the
Massive-STEPS abstract. That is a **new number entering the document**, so it needs a bib-comment
claim location under §1 R1 and a numbers-ledger line under §2 N3. Also: `CONSIDERATIONS.md` §4
`wongso2025massivesteps` and §5 item 7 both record that the work is **still a preprint** and
recommend saying so where it is cited as the Istanbul source; the `.bib` entry is `@misc` with
`howpublished = {arXiv:2505.11239}` and carries no such note in prose. That recommendation is open
and touches the same sentence.

**Disposition: I_DECIDE.** His premise is wrong, the fix he implies (soften the vintage limitation)
is not warranted, and the defensible edit (name Istanbul's 2017-2018 window) is an addition that
introduces a number and interacts with a gate.

### 34(b) Transductive representation — "deserves a huge warning that this affects much of the literature"

**Verdict: PARTLY_CONFIRMED.** The live limitation is correct and narrow; his addition is a claim
about other work and needs a citation.

**The live text** (`6_conclusion.tex:386-388`):

> \item \textbf{Transductive representation.} Check2HGI is trained on the check-in
> graph of each dataset, so it cannot represent unseen places or users without
> retraining.

The chapter-5 measurement that bounds it (`5_mobiwac/05_setup.tex:66`):

> Rebuilding the representation per fold, from that fold's training users only, moves both tasks by
> at most a third of a point (region $-0.33$ to $+0.01$; category $0.00$ to $+0.29$, at Alabama,
> Arizona, and Florida), within fold noise. This measurement covers the visits whose places appear
> in training (67 to 87 percent); visits to places unseen in training are the one part it cannot
> reach.

**What his addition would need.** "This affects much of the literature" is a claim about other
authors' systems, so under §1 R1 it needs (a) a resolvable identifier, (b) the source opened, and
(c) the specific claim located in it — for *each* system named, or for a survey that makes the
general statement. It also cannot be asserted as a bare generality: the honest form is a bounded
comparative, e.g. "the graph-embedding methods this work builds on are transductive in the same
sense", naming them.

The nearest support **already in the tree and already cited** is the contrast the fundamentals
chapter draws at `2_fundamentals.tex:372-376`:

> Graph convolutional networks use a localized spectral rule~\cite{kipf2017gcn}, graph attention
> networks learn the weight of each neighbor~\cite{velivckovic2017graph}, and GraphSAGE learns
> aggregators that can embed nodes not seen during training~\cite{hamilton2017graphsage}.

`hamilton2017graphsage` is in `references.bib:228-235` with a claim comment ("GraphSAGE is an
inductive framework that generates node embeddings by learning aggregator functions over a node's
local feature neighborhood rather than training a per-node embedding") and is cited exactly once
in live prose, at that line. That gives the *inductive* pole a verified citation; it does not by
itself license "much of the literature is transductive". The transductive pole would need at
minimum `huang2023hgi` (the place embedding this work compares against, already cited at
`5_mobiwac/06_results.tex:15`) and ideally one survey sentence located firsthand.

**Size:** one clause in limitation 3, one or two citations already in the bib, one claim to locate
in a source this session did not open. Small, but it is a new claim (C2).

**Disposition: I_DECIDE.** A new claim about other work; C2 requires the author to approve it, and
the citation work must precede the sentence.

### 34(c) The task-pair confound — he is against it

**Verdict: PARTLY_CONFIRMED. His leakage reasoning holds. It does not delete the limitation; it
strengthens it, and it invalidates the tied future-work item as written.**

**The live limitation** (`6_conclusion.tex:393-404`, limitation 6):

> \item \textbf{The task-pair confound.} The task pair changed together with the
> representation and the sharing topology. Chapters~\ref{ch:cbic}
> and~\ref{ch:courb} paired static category classification with next-category
> prediction, while Chapter~\ref{ch:mobiwac} pairs two sequential targets,
> next-category and next-region prediction. No single controlled ablation
> separates the representation-and-topology change from the task-pair change in
> the final result. Chapter~\ref{ch:courb} is the fixed-pair control for the
> diagnosis. The capacity-matched baseline above addresses the parameter-count
> explanation only in the setting that it tested: the category task, two of the
> six datasets, one width point per dataset, and width scaling rather than
> depth. The greater similarity of the final pair may still contribute to the
> size of the improvement.

**The tied future-work item** (`6_conclusion.tex:430-433`):

> Training the Chapter~\ref{ch:mobiwac} joint model on the
> Chapter~\ref{ch:cbic} task pair, under the check-in-level representation, is the
> controlled comparison needed to isolate the effect of changing the task pair
> (limitation~6).

**Sign-off status.** `NORTH_STAR.md` §6 Ch.6 beats records the limitation as
"[signed-off addition, 2026-07-22] the task-pair confound concession from storyline/02 §3.4: no
single controlled ablation separates the representation+topology change from the task-pair
homogeneity change in the final win — CoUrb is the fixed-pair control for the diagnosis, not for
the joint win", and the same block ties a future-work item to it ("the fixed-pair ablation under
the check-in representation"). Removing it therefore needs new sign-off (C2).

**Does his leakage reasoning hold? Yes.** Three independent pieces of evidence, all opened this
session:

1. **The static task's input determines its target when the input is place-level**
   (`apx_b_static_scope.tex:34-46`): the Ch.4 place embedding is "a lookup table on that string:
   two places of the same venue type receive the same vector … The input therefore contains the
   answer. We confirmed this holds without exception across the five Gowalla state subsets …
   the venue type takes between 284 and 365 distinct values per state, and in every state each of
   those values maps to exactly one of the seven top-level categories."
2. **A check-in-level vector carries the visit's own category as an input feature.**
   `science/check2hgi_v17_complete_picture.md:71-76`: the check-in node feature vector is
   `[category one-hot, sin/cos hour, sin/cos day_of_week]`, "the active input width is `7 + 4 =
   11`". And `:50`: "A visit's own category is nevertheless an input feature, and aggregated
   current-visit category features are used by the masked reconstruction auxiliary. 'Label-free'
   here means no downstream future target, not absence of categorical information from the graph
   input." The POI-level pooling that a static POI classifier would consume is trained with a
   masked-reconstruction auxiliary whose target is, verbatim at `:323`, "the mean category one-hot
   vector of all its check-ins, equivalent to its empirical seven-category visit distribution."
3. **The dissertation already says Ch.5 escapes the problem *because* it left the static task
   behind** (`apx_b_static_scope.tex:83-86`): "Chapter~\ref{ch:mobiwac} does not inherit the
   problem … it replaces the place-level embedding with a check-in-level representation, whose
   input is a single visit, and the identity described above does not arise."

Putting (1)+(2)+(3) together: the proposed ablation reintroduces the static task, and it would
have to feed the static classifier a **place-level** object derived from Check2HGI (a POI pooling
or an average of that POI's visit vectors). Every such object is built from features that include
the category one-hot of the visits at that POI, and the POI-level pool is explicitly supervised
toward that POI's empirical category distribution. **The static task's target would be present in
its input, by construction, more directly than in Ch.4.** His term "data-leak" is the right
diagnosis. Note the precise scope: the leak concerns the **static** member of the Ch.3 pair. The
next-category member is unaffected — `apx_b_static_scope.tex:59-63` says so for Ch.4, and the same
argument holds here, since the sequential target is a category the model has not seen for that
step.

**Therefore:** the ablation named at `:430-433` is not cleanly runnable. Its outcome would be
uninterpretable, because any category-side improvement under the check-in-level representation
would be confounded with the leak — which is the same defect the collection already documents for
Ch.4 in Appendix B. **This does not weaken the confound; it converts it from "an ablation we have
not run" into "an ablation that cannot be run cleanly with this representation", which is a
stronger and more permanent limitation.**

**The coupling.** Limitation 6 and the §6.4 item at `:430-433` are a matched pair under
NORTH_STAR §6's "future work tied 1:1 to limitations" rule. Editing one without the other creates
an orphan: a limitation with no future-work answer, or a future-work item pointing at
`limitation~6` that no longer exists.

**THE OPTIONS, for the author to choose — I do not choose:**

1. **Keep both exactly as they are.** Zero work, zero gate risk. Cost: §6.4 proposes an experiment
   that the collection's own Appendix B implies would leak, and a reader who connects the two
   (Appendix B is in the same document) can ask about it at the defense.
2. **Keep the limitation, add why the ablation is not clean, rewrite the future-work item.**
   Limitation 6 gains one sentence of the form "the ablation that would separate the two changes
   is not cleanly available, because a static category task under the check-in-level
   representation would receive its own target as an input feature (Appendix~\ref{...})"; §6.4's
   item changes from "is the controlled comparison needed" to naming a *different*
   fixed-pair design (for example, holding the pair fixed at two sequential targets and varying
   only the representation — which is what the Ch.5 representation control at
   `5_mobiwac/06_results.tex:14-17` already partly does). **This is the option the evidence
   supports.** Size: two sentences, one cross-reference to Appendix B, both loci touched together.
   New claim → C2 sign-off, but it is a *strengthening* concession, which is the direction the
   guardrails favor.
3. **Weaken the limitation** to say the confound is partly addressed by the Ch.5 representation
   control. Not supported: that control varies the representation with the task pair held fixed at
   the *final* pair, so it speaks to the representation, not to the pair change. Listing it for
   completeness.
4. **Remove the limitation.** Needs new sign-off (C2) against a 2026-07-22 signed-off addition,
   and the evidence points the other way — his own argument makes the confound *harder* to
   resolve, not softer. Not recommended, recorded because he asked.

**Disposition: I_DECIDE.** A signed-off limitation and its coupled future-work item; the author
owns the choice among the four, and option 2 is the one the evidence supports.

---

## ITEM 35 — the seven future-work items

Live §6.4 is `6_conclusion.tex:415-433`, 156 prose words, two paragraphs, six items each tagged
`(limitation~N)`. Verbatim, in full:

> Future work follows directly from these limitations. Newer and denser traces would
> test the conclusions beyond the Gowalla vintage (limitation~1), and finer-grained
> taxonomies would test them beyond the seven-class division (limitation~2). Because the
> check-in-level representation is trained on a fixed graph, an inductive variant of it,
> one that embeds unseen places and users without retraining, would remove the
> transductive constraint and support deployment in growing cities (limitation~3).
>
> Adding the exact next place as a third target would extend the joint model beyond the
> two properties predicted in this work. The cascade architectures reviewed in
> Chapter~\ref{ch:mobiwac} suggest that category and region predictions can provide
> additional structure for this task (limitation~4).
> Further cities outside the United States would widen the geographic base
> (limitation~5). Training the Chapter~\ref{ch:mobiwac} joint model on the
> Chapter~\ref{ch:cbic} task pair, under the check-in-level representation, is the
> controlled comparison needed to isolate the effect of changing the task pair
> (limitation~6).

**Per item.** Absence sweeps below all use the validated `/tmp/pgrep.sh`; the positive control for
the whole-tree file list is `cross-attention` → 18 hits.

| # | his item | status | evidence |
|---|---|---|---|
| 1 | **Better Check2HGI integration** (parts are coupled, e.g. POI2Vec) | **ABSENT** | `/tmp/pgrep.sh 'poi2vec' $(find . -name '*.tex')` → **1 hit**, and it is `4_courb/related.tex:16` describing Feng et al.'s POI2Vec as prior work, not our coupling. Ch.6 has none. The coupling itself is real and documented outside the chapter: `check2hgi_v17_complete_picture.md:205-207` — "`E_poi` is a trainable `Embedding(num_pois, 64)`. It is initialized exactly from the remapped frozen POI2Vec table. The POI2Vec source table is retained as an immutable anchor buffer." |
| 2 | **Modern soft-sharing MTL** | **ABSENT from §6.4** | `/tmp/pgrep.sh 'soft.?shar|mixture-of-experts|MMoE|cross-stitch' chapters/6_conclusion.tex` → **0**. The material exists in Ch.2 (`2_fundamentals.tex:814-822`: cross-stitch, MMoE, PLE, DSelect-k) and Ch.3's own future work (`3_cbic/conclusion.tex:23`), so a §6.4 item would have a home to point at. |
| 3 | **More than 7 categories** | **ALREADY THERE** | `:419-420`: "finer-grained taxonomies would test them beyond the seven-class division (limitation~2)". |
| 4 | **Hypergraphs in Check2HGI** | **ABSENT** | `/tmp/pgrep.sh 'hyper-?graph' $(find . -name '*.tex')` → **0** across all 61 files. |
| 5 | **More non-U.S. datasets** | **ALREADY THERE** | `:429-430`: "Further cities outside the United States would widen the geographic base (limitation~5)." |
| 6 | **Cascade together with MTL** | **PARTLY THERE** | `:426-428` invokes cascade only as scaffolding for the next-place item: "The cascade architectures reviewed in Chapter~\ref{ch:mobiwac} suggest that category and region predictions can provide additional structure for this task." His item is different — tuning the cascade as a coupling in its own right. Ch.5 already licenses exactly that and names it as future work: `5_mobiwac/06_results.tex:379-380` — "the cascade runs under the configuration tuned for the parallel model, and its form was fixed in advance, so tuning the cascade itself remains future work." **So the claim is available and sourced; it is simply not carried into §6.4.** |
| 7 | **Next-place head on the joint model, reusing the embedding** (his "most promising") | **PARTLY THERE** | `:425-426` proposes the target — "Adding the exact next place as a third target would extend the joint model beyond the two properties predicted in this work" — but not his mechanism (reuse the existing representation, modify the input pipeline, attach a next-place output to the joint model). |

### The two constraints, checked

**(i) 1:1 tie to a §6.3 limitation** (NORTH_STAR §6: "future work tied 1:1 to limitations"). All
six live items carry a `(limitation~N)` tag, N = 1..6, one each; §6.3 has exactly six limitations
(`:296` "Six limitations bound the scope of these conclusions"). The mapping is complete and
bijective today. **Four of his seven items (1, 2, 4, 6) have no limitation to attach to.** Adding
them therefore requires *either* a new §6.3 limitation each — which changes the "Six limitations"
count sentence at `:296` and the numbering that `:419`-`:433` depends on — *or* attaching them to
an existing limitation as a second route (breaking 1:1). This is the real cost of item 35, and it
is structural, not cosmetic.

**(ii) Next place is formally out of scope.** `GLOSSARY.md:23` — "**next-place prediction** (next
place) | Predicting the exact next POI. **Out of scope for this dissertation** — named only to
delimit." `GLOSSARY.md:46` registers `f_{\mathrm{place}}(H_i)` for the same purpose.
`2_fundamentals.tex:295-302` pins it as Definition 2.9:

> \begin{definition}[Next-place prediction]\label{def:fund:nextplace}
> Next-place prediction maps a check-in history to the identity of the next visited POI:
> \begin{equation}
>     f_{\mathrm{place}}(H_i)\longrightarrow p_i.
> \end{equation}
> It is named to delimit the scope of the dissertation, and no chapter reports a result
> for $f_{\mathrm{place}}$.
> \end{definition}

Both gates confirmed present in the live file: probe `R12-fplace`
(`check_audit_claims.py:563-565`, regex `f_\{\\mathrm\{place\}\}\(H_i\)\\longrightarrow p_i`)
matches `2_fundamentals.tex:298`; probe `R12-fplace2` (`:566-569`, regex
`no chapter reports a result\s*for \$f_\{\\mathrm\{place\}\}\$`) matches `:300-301`.

**Collision check on the live §6.4 wording: none.** `:425-426` uses the conditional ("would
extend") and the contrastive ("beyond the two properties predicted in this work"), and `6.3`
limitation 4 (`:389-390`) states the exclusion as fact ("The experiments do not predict the exact
next POI, and their conclusions apply only to next category and next region"). Nothing reads as
something the dissertation did. **If his mechanism sentence is added, the tense discipline must
survive it**: "reusing the representation would require only a change to the input pipeline and an
additional output" is safe; anything in the present or perfect ("the representation already
supports next place", "we can already use it") reads as a claimed capability and would collide
with `2_fundamentals.tex:300-301` and with GLOSSARY §1.1. His own phrasing in PENDENCIAS ("do
jeito que está hoje já conseguimos usar") is exactly the form that must not be carried over
literally.

**Size.** Three absent items plus one partial (1, 2, 4, 6) = up to four new future-work sentences,
each needing a limitation to attach to; plus one clause on item 7's mechanism. If new limitations
are created, `:296` and the `limitation~N` numbering both change. Half a day with the ledger and
gate re-run, not an afternoon's copy edit.

**Disposition: I_DECIDE.** Adding future work means adding or re-tying limitations, which changes
the §6.3 count sentence and the 1:1 structure NORTH_STAR fixes; and item 7's wording sits against
a gated scope exclusion.

---

## ITEM 36 — a critical evaluation of the conclusion against the exemplars

**Author's premise.** The conclusion is on a good path but incomplete; §6.2 leans too hard on
numbers already shown in the papers; the target flow is question and thesis → chain of cause and
effect → what the initial thesis got wrong → the real lesson through the lens of the discoveries.

**Verdict: PARTLY_CONFIRMED.** The numbers observation is measurably correct in absolute terms
(§6.2 carries 21 arabic numerals in 851 words, against 1 for the whole of Viegas's conclusion and
0 for Germano's). The missing move in the flow is not the numbers, though — it is move 3, "what we
got wrong", which the chapter states nowhere.

### 36.1 The exemplars, measured

Each opened this session. Word counts from `pypdfium2` text extraction with running page numbers
stripped; numeral counts by regex over the same text.

| exemplar | conclusion location | length | sectioning | numbers quoted | move order |
|---|---|---|---|---|---|
| **viegas** (declared quality bar; same advisor; UFV/PPGCC coletânea, EN) | pp. 87-90 of 100 | **1,113 words**, 4 pages | 4 numbered sections: 6.1 Summary of Contributions, 6.2 Limitations, 6.3 Future Work, 6.4 Final Remarks, plus an unnumbered 1-paragraph opener | **one** arabic numeral in the entire chapter (`[1]` in a footnote-like position; section numbers excluded); three spelled quantities: "three interconnected contributions", "twelve Causal Discovery algorithms", "eight real-world datasets" | opener names the problem and lists the three contributions in one sentence → one topic-sentence-led paragraph per contribution (framework, metrics, benchmarking, application, interface) → limitations in continuous prose, no list → future work in continuous prose → final remarks that move to the field level |
| **germano** (same advisor, defended, EN, full LaTeX source at `exemples/germano/Dissertação_Mestrado___Germano/5_conclusion.tex`) | p. 86 of 96 | **284 words**, 5 paragraphs, **1 page** | **no sections at all** — `grep -c '\\section' 5_conclusion.tex` = 0 | **zero** numerals, zero spelled quantities | contribution 1 (HAVANA) → contribution 2 (HAMURE) → the field-level significance of the idea (spatial heterogeneity) → future work → one-sentence close |
| **canesche** (PT) | pp. 94-96 of 108 | **1,011 words** | unnumbered, continuous, but contains **Tabela 6.1** | numeral-dense: 502.1x, 4.6x, 10.1x, 7%, 2x, 4x, 21x, 20%, 784x, plus a four-row comparison table in the conclusion itself | recap of the two works → per-chapter result paragraph with speedups → a "still open" paragraph that concedes SA1000 beats YOTT100 on two of three metrics → future work (QCA/NML, GRNs) |
| **lapsusvgi** (PT) | pp. 60-61 of 77 | **592 words** | unnumbered, continuous | 2 numerals, both structural ("Seção 1.1", "ISO 22351") | framework recap → scope generalization beyond landslides → "all objectives in §1.1 were achieved" → future work in three paragraphs |
| **passe** (PT) | no general conclusion chapter | — | the document ends with §4.7 Conclusão (p. 59) and goes straight to references at p. 60 | — | not a usable exemplar for this item |
| **ctd2026** | 16 separate PDFs, not dissertations | — | — | — | not examined; out of scope for a conclusion-chapter comparison |

**Ours, for the same table:** `6_conclusion.tex`, **1,906 prose words**, PDF pages 83-87 (5 pages),
**five numbered sections**, **30 arabic numerals** (7+21+2+0+0 by the §33.1 command).

### 36.2 What the comparison actually shows

1. **We are the longest and by far the most numerate.** 1,906 words against Viegas's 1,113 and
   Germano's 284; 30 arabic numerals against Viegas's 1 and Germano's 0. Canesche is the one
   exemplar comparable in numeracy, and it is a non-coletânea PT dissertation whose conclusion
   quotes speedups because speedup *is* its thesis. **The author's instinct is right, and the
   gap is larger than he thinks.**
2. **§6.2 is the outlier, not §6.1.** Of our 30 numerals, 21 are in §6.2, and 18 of those 21 sit
   in two consecutive paragraphs — paragraph 4 (`:249-260`, the capacity-matched baseline: 0.6,
   4.2, 56.16, 1.89, 56.82, 0.03, 64.51, 0.09, 752, 101.9, 69.88, 0.26, 70.60, 0.07, 77.05, 0.01)
   and paragraph 5 (`:262-272`: 0.66, 0.72). **Those two paragraphs are 18 of the chapter's 30
   numerals in 282 of its 1,906 words** (word count over lines 249-272 by the §33.1 script with the
   numeral counters replaced by a token count). They are a controls report living inside the narrative
   answer. Note the constraint on them: the chapter header comment (`6_conclusion.tex:6-9`) records
   "[AUTHOR DECISION pending in section 6.2: prominence of the capacity-matched baseline
   paragraph — it is included per the D1 licensing contract (suppression is not an option once
   run), but its length and placement are the author's call.]" **Suppression is off the table;
   placement and length are exactly what is open.**
3. **The headline result is stated three times** (opener `:23-25`, §6.1 `:107-110`, §6.2
   `:125-126`), which is what makes §6.2 read as a re-report rather than a synthesis.
4. **Structurally we already match Viegas** (numbered sections, contributions → limitations →
   future work tied to limitations → final remarks), and we exceed him on one axis he is weak on:
   our §6.4 ties every item to a numbered limitation; his future work is continuous prose with no
   tie-back. **No structural change is needed to match the bar. The gap is entirely in §6.2.**

### 36.3 Ours against his target flow, move by move

| his move | present? | where |
|---|---|---|
| **1. Question and thesis** | **YES** | §6.2 opens `:119-121`: "Does multitask learning help point-of-interest prediction? The answer is conditional. Identifying those conditions is the dissertation's main finding." |
| **2. Chain of cause and effect** | **PARTLY** | The chain exists but is split across two sections and told twice. §6.1 tells it chapter by chapter (`:37`, `:49`, `:100`); §6.2 `:121-128` compresses it to two sentences (CBIC's null → the check-in-level representation) and then leaves the chain for the controls. **The causal links between the studies — why the null led to the representation test, why the diagnosis led to the check-in level — are stated in Ch.1 §Research question (`1_introduction.tex:99-102`, "The first reports a negative result, the second identifies its main bottleneck, and the third tests the resulting solution") but not narrated in §6.2.** |
| **3. Show what we got wrong in the initial thesis** | **ABSENT — this is the missing move** | Sweep for a live sentence in which the work states its own expectation was wrong: `6_conclusion.tex` has nothing. The nearest is `:286-290`: "The negative result of Chapter~\ref{ch:cbic} and the positive result of Chapter~\ref{ch:mobiwac} do not contradict each other" — a *reconciliation*, not a concession. Meanwhile the material for the move exists and is verified: (i) `5_mobiwac/06_results.tex:193-194` — "A reader used to multitask learning expects the harder task … to teach the easier one; a control shows otherwise", the field's expectation refuted; (ii) `apx_f_cosine.tex:99-101` — "The two tasks turn out not to disagree. Their gradients are statistically indistinguishable from orthogonal on every dataset measured … a gradient balancer had nothing to balance", which refutes the premise Ch.3's Nash-MTL choice rested on; (iii) `apx_b_static_scope.tex:41-46` — "The input therefore contains the answer", which retracts the reading of Ch.4's own headline task. **Three genuine "we were wrong" findings, all sourced, none of them in the conclusion's narrative.** |
| **4. Connect to the real lesson through the lens of the discoveries** | **PARTLY** | `:288-290` states the lesson ("Multitask learning does not provide an automatic benefit, but the first negative result does not rule it out … one path from the negative result to a positive one") and §6.5 restates it at the level of the artifact. But it arrives *after* three paragraphs of controls, so the lesson reads as an afterword rather than as the destination of the chain. |

### 36.4 The concrete structural recommendation

Not a rewrite. Four moves, in this order, inside §6.2:

1. **Keep move 1 where it is** (`:119-121`). It is already the right opening.
2. **Promote the chain (move 2) into a single narrated paragraph** immediately after it, replacing
   the current two-sentence compression at `:121-128`. It should carry the *causal* links, not the
   chapter list — §6.1 already has the chapter list, and the duplication at `:125-126` of the
   headline partition can go with it.
   *Illustrative topic sentence only, marked as illustrative, not proposed prose:* "Each study's
   result set the next study's question: the null result made the representation suspect, the
   representation test confirmed it, and the check-in level is what that diagnosis implied."
3. **Insert move 3, which does not currently exist**, as its own short paragraph after the chain.
   It has three candidate contents, all already verified in the tree (§36.3 row 3): the field's
   teaching expectation, the gradient-conflict premise, and the static task's input-target
   identity. **Choosing which of the three to concede here is an author decision and a C2 claim**,
   because a "we were wrong about X" sentence in the conclusion is a new frame-level claim even
   when every component is sourced.
   *Illustrative topic sentence only:* "Two premises this work started from did not survive its own
   measurements."
4. **Demote the two controls paragraphs** (`:249-260` and `:262-272`, the 18-numeral, 282-word block) to
   after move 3, and let move 4 close the section. Their content is licensed and cannot be
   suppressed (`:6-9`); what is open is whether they narrate the answer or evidence it. Placing
   them after the chain and the concession makes them evidence.

**Not recommended:** cutting numbers from §6.2 wholesale. Every value there carries its reference
point and convention per WRITING_LAW §3 (the 56.16 carries ±1.89 and its n=20 basis; the 64.51 is
joint-best rather than diagnostic-best per AGENT_GUARDRAILS N5, a distinction the comment block at
`:210-228` was written to protect). Reordering costs nothing; deleting costs a hedge each time.

**Disposition: I_DECIDE.** The reorder is mechanical, but move 3 is a new claim (C2) and the
capacity-baseline placement is an explicitly reserved author decision recorded in the file's own
header.

---

## Cross-item overlaps

- **31 ↔ 34(c) ↔ 35.** All three turn on the task-pair change. Item 31 wants the static task in the
  opening; 34(c) argues the static task cannot be revisited under Check2HGI; 35 item 6 wants the
  pair question reopened as future work. A consistent resolution treats the static task as
  *historical* — present in the Ch.3/Ch.4 recaps and in limitation 6, absent from the research
  question and from future work.
- **32 ↔ 36.** Item 32's answer (the live text already refuses to attribute the gain to any single
  component) is precisely the material item 36's move 3 would use, from the opposite direction:
  what the controls ruled out is also what the initial thesis got wrong.
- **33 ↔ 36.** Both are about numeral placement in §6.1 vs §6.2; 33 measures §6.1, 36 measures the
  chapter against external exemplars. They agree in direction and the same edit serves both.
- **34(a) ↔ probe R8-vintage**; **35 item 7 ↔ probes R12-fplace / R12-fplace2**. Both gated.

## [VERIFY] flags

1. **[VERIFY: probe description drift, not a failing gate]** `check_audit_claims.py:91` describes
   R8-vintage as "Ch.6 data-vintage item prints BOTH Gowalla windows, the paper's and the measured
   one". The live item prints only the measured window (`6_conclusion.tex:328-331`), per the
   author's ruling recorded at `:333-341`. The regex `August\s+2011` still matches, so the gate is
   green while its description is false. Not repaired here (audit phase, no edits).
2. **[VERIFY: Massive-STEPS is still a preprint]** Confirmed from OpenAlex `W4416143324` this
   session: `type: "preprint"`, `is_published: false`, no journal ref, DOI is the arXiv DataCite
   DOI `10.48550/arXiv.2505.11239`. `CONSIDERATIONS.md` §4 and §5 item 7 recommend that prose
   citing it as the Istanbul source say so; no live prose does. Open recommendation, not this
   item's scope.
3. **[VERIFY: Istanbul 2017-2018 window]** Sourced only from the Massive-STEPS **abstract** as
   returned by OpenAlex ("features more recent (2017-2018) and longer-duration (24 months)
   check-in data"). I did **not** open the arXiv PDF this session (arXiv's API returned HTTP 429 on
   two attempts, once bare and once after a five-second wait), and I did **not** measure the
   Istanbul date range on the repository's own files the way the Gowalla span was measured
   (`6_conclusion.tex:302-315` records that command). Before any Istanbul date enters the text, one
   of those two must happen.
4. **[VERIFY: the leakage argument in 34(c) is analytic, not measured.]** It follows from
   `check2hgi_v17_complete_picture.md:50`, `:71-76`, `:323` plus `apx_b_static_scope.tex:34-46`.
   **No experiment was run to demonstrate a static-task leak under Check2HGI**, and none exists in
   the repository as far as this audit's budget reached. The conclusion "the ablation is not
   cleanly runnable" is therefore a reasoned inference from the representation's specification, not
   an observation. If it is to enter the document it should be worded as such.
5. **[VERIFY: build-page mapping]** Chapter 6 at pages 83-87 was read off the **current**
   `build/main.pdf` (mtime 2026-08-03 21:02:30), which post-dates the source. If either file moves,
   re-derive.
6. **[VERIFY: the "Sharing stopped hurting" phrase]** NORTH_STAR §6 prescribes it and it appears
   nowhere in the tree (0 hits, validated instrument). I read this as content satisfied by
   different wording rather than a beat missed, but I cannot rule out that the author wants the
   phrase itself.

## Budget and coverage

Roughly 35 inspection commands across six items, under the 20-per-item ceiling (S1). Not examined,
and named rather than silently skipped (S3): the `ctd2026` folder (16 unrelated PDFs, no single
conclusion chapter to compare); `passe` beyond confirming it has no general conclusion; the
storyline/02 §3.4 source of the task-pair concession (referenced by NORTH_STAR but not opened —
the NORTH_STAR record was sufficient to establish sign-off status); the D1 capacity-baseline record
`storyline/audit/capacity_baseline_experiment.md` cited in the chapter header comment.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
