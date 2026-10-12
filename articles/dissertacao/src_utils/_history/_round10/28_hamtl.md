# FAB-28 — there is more MTL-for-POI work than the two papers cited

**Baseline commit:** `dda8978e`
**Files touched:** `src/chapters/2_fundamentals.tex` (§2.3), `src/references.bib`. Nothing else.
**Date of work:** 2026-08-03.

## The author's ruling, verbatim

> **DECISAO SUA:** Vamos então avaliar o wang2025hamtl, adicione no caminho:
> articles/dissertacao/science/articles/wang2025hamtl.pdf. Apos ler ele avalie quais adicionar na
> dissertação se todos forme interessante, adicionamos todos.

The item's prior status was **BLOCKED**: three sessions could not obtain the paper's content
(closed access, Springer key 401, landing page redirecting to an authentication gate). The author
placed the PDF on disk so it could be read. It was read this session, in full, and that is what
unblocks the item.

## 1. What the PDF establishes, page by page

Source: `science/articles/wang2025hamtl.pdf`, 28 pages, text extracted with `pypdfium2`. Page
numbers below are the PDF's own printed page numbers ("Page N of 28"), which coincide with the
extraction index.

**The record.** Wang, Chen, Liu, Zhang, Wu, Cui, Hu, "Hierarchy aware-based multi-task learning for
user location prediction", The Journal of Supercomputing 81(11), article 1196, 2025,
DOI `10.1007/s11227-025-07643-7`. Crossref (`api.crossref.org/works/10.1007/s11227-025-07643-7`,
opened this session) returns exactly this: volume 81, issue 11, article-number 1196, issued
2025-07-29, seven authors in the order the committed bib entry already carries. **The bib entry's
attributes needed no correction.**

### Question 1: is a region-like unit a co-equal end target? **NO.**

- p. 2: "Our framework consists of two tasks: location prediction as the main task and category
  prediction as the auxiliary task."
- p. 6, Sect. 4.1: the hierarchical decoder "first predicts the location category, and then predicts
  the specific location based on the category and prior hierarchy information".
- p. 6, Definition 3: "User location prediction is to infer p^{r+1}_u in S̃_u based on T_u", where a
  spatial-temporal point is a location plus a timestamp. The end target is the location.
- p. 17, Table 1: the counted units are User, Location, Category, Check-in, Trajectory. There is no
  spatial-partition unit.
- p. 18: the two metrics, top-k accuracy and mean reciprocal rank, are both defined over "the true
  next location".
- **Negative evidence, and it is the decisive part.** A whole-document scan for `region`, `Region`,
  `grid`, `district`, `administrative`, `zone`, `geohash`, `area of interest` and `spatial hierarchy`
  returns exactly ONE hit in the entire paper: the word "region" inside the title of reference [40]
  (Tobler, "A computer movie simulating urban growth in the Detroit region") on p. 27. The paper's
  hierarchy is category-over-location, not space-over-space.

  Command, run from the repository root, that yields that count:

  ```
  python - <<'PY'
  import pypdfium2 as pdfium
  d = pdfium.PdfDocument("science/articles/wang2025hamtl.pdf")
  pages = [d[i].get_textpage().get_text_range() for i in range(len(d))]
  for w in ["region","Region","grid","district","administrative","zone","geohash",
            "area of interest","spatial hierarchy"]:
      print(w, [(i+1, p.count(w)) for i, p in enumerate(pages) if w in p])
  PY
  ```
  Output: `region [(27, 1)]`; every other term returns an empty list.

### Question 2: what is the hierarchy, and how does the multi-task structure work?

The hierarchy is a **hierarchy tree over location categories**, from abstract to specific. The
paper's own example, p. 2: a location that is a hotpot restaurant "also belongs to more abstract
categories, such as Chinese restaurant and restaurant". Top-to-bottom paths through that tree are
extracted and the embeddings of all nodes on a path are concatenated into the hierarchy feature
(p. 3, p. 7). Location embeddings come from a heterogeneous GNN over a location graph built from
transition and geospatial relationships (p. 7); the trajectory embedding concatenates hierarchy,
user and time information; a Transformer-based encoder produces the latent representation (p. 6).

The multi-task structure is **cascaded, not parallel**, and the paper says so as a design choice:
"MTL is broadly classified into parallel and cascaded types. In this work, we focus on cascaded MTL,
where the computations for subsequent tasks depend on the outputs of preceding ones" (p. 5). The
decoder mechanism, p. 14: "It first predicts the category for the next destination (e.g.,
restaurant). This category prediction inherently restricts the potential search space for the
subsequent fine-grained location prediction (e.g., limiting candidate venues to hotpot
restaurants)." Its RQ4 (p. 16) compares the hierarchical decoder against a parallel architecture.
The joint loss is the plain sum of the location and category cross-entropies (Eq. 18, p. 16), with
no gradient balancer.

Datasets are Foursquare TKY and NYC (p. 16-17). No category-side metric is reported anywhere: the
paper measures top-k accuracy and reciprocal rank for the location only (p. 18). The category head
is instrumental throughout, exactly as the "auxiliary task" label on p. 2 says.

### Question 3: what does HAMTL cite for MTL-on-POI?

Its §2.2 (pp. 4-5) is the harvest target, and the harvest is thinner than the item hoped. HAMTL's
MTL section cites a general MTL survey [28] and a medical-imaging MTL review [29], then cascaded MTL
in **natural language processing** [30, 31], **medical imaging** [32, 33] and **multi-behavior
recommendation** [34-38]. **None of [29]-[38] is mobility work.** Its mobility citations sit in §2.1
(location prediction) and are single-task next-POI models, not MTL: ST-RNN, LSTPM, GETNext, TGSTAN,
KGNext and so on.

The one genuinely new MTL-for-mobility candidate in HAMTL's reference list is **[13] IeMTLF**, which
HAMTL calls "our previous work" on p. 7. Two of the candidates are already in the dissertation's
bibliography:

| HAMTL ref | Work | Already in `references.bib`? |
|---|---|---|
| [28] | Zhang and Yang, A Survey on Multi-Task Learning, TKDE | **yes**, key `zhang2021survey` |
| [13] | IeMTLF, Information Sciences 661:120153, 2024 | **no** — added this session |
| [29]-[38] | MTL outside mobility (medical imaging, NLP, multi-behavior recommendation) | not proposed: out of §2.3's scope |
| [9] | CTLE (Lin et al., AAAI 2021) | **yes**, key `lin2021ctle`, cited in §2.1 |

## 2. What the LIVE text said before the edit, and what it says now

Located in the live file immediately before editing. The item's line numbers were stale by roughly
176 lines: the passage sat at 730-732, not at 454 or 560.

**BEFORE** (`src/chapters/2_fundamentals.tex`:730-732):

> HAMTL uses a cascaded decoder that predicts the next category before the exact next POI, using the
> category to refine the place prediction~\cite{wang2025hamtl}.

**AFTER** (`src/chapters/2_fundamentals.tex`:730-736):

> HAMTL sets location prediction as its main task and category prediction as an auxiliary task, and
> its hierarchical decoder predicts the category of the next destination first and then refines the
> prediction of the specific location using that predicted category~\cite{wang2025hamtl}. The same
> group had already published IeMTLF, an interaction-enhanced multitask framework for next location
> prediction~\cite{wang2024iemtlf}.

**Why the old sentence was changed.** It was not false, but it was not the authors' own framing
either, and R2 requires describing a cited system as its authors describe it. Two defects. First,
"cascaded decoder" is the paper's category for its *multi-task structure* (p. 5); the component is
named **hierarchical decoder** (p. 6, Fig. 4 on p. 13, and the paper's own keyword list on p. 1).
Second, and this is the substantive one, the old sentence gave no hint of the **main and auxiliary
asymmetry** that is HAMTL's own first description of itself on p. 2. That asymmetry is precisely
what distinguishes HAMTL from this dissertation's joint model, so suppressing it weakened the
contrast the paragraph exists to draw.

**The novelty sentence was NOT touched, and it should not be.** It now sits at :738-741 and reads:

> Among the works reviewed here, none treats next category and next region as co-equal end targets
> of one joint model.

HAMTL does not threaten it, on three independent grounds taken from the source: it names category
prediction *auxiliary* (p. 2), so the two heads are not co-equal; it predicts no region-like unit at
all (the negative scan above); and it reports no category-side metric (p. 18), so the category head
is not an end target even within its own evaluation. The prior session's read, recorded in the bib
provenance from the MobiWac donor and dated 2026-07-06, is confirmed by the full text.

The bib provenance comment for `wang2025hamtl` now carries the located quotations with their pages,
so the next session does not have to re-open the PDF to know what was established.

## 3. Source ledger

Six external records were the cap; **three** were opened. Each row: identifier, where it was opened
this session, and the specific claim located.

| Work | Identifier | Opened | Claim located | Verdict |
|---|---|---|---|---|
| Wang et al., HAMTL | DOI `10.1007/s11227-025-07643-7` | the **full PDF** at `science/articles/wang2025hamtl.pdf`, plus Crossref `api.crossref.org/works/10.1007/s11227-025-07643-7` for attributes | main task and auxiliary task split (p. 2); hierarchical decoder order (pp. 6, 14); no region-like unit anywhere (whole-text scan); location-only metrics (p. 18) | **ADMISSIBLE.** Supersedes the earlier INADMISSIBLE verdict in `CONSIDERATIONS.md`, which was recorded because the abstract could not be opened. It can now be opened. |
| Wang et al., IeMTLF | DOI `10.1016/j.ins.2024.120153` | Crossref (full record: Information Sciences 661, article 120153, 2024-03, six authors) + OpenAlex `works/doi:...` + Semantic Scholar `graph/v1` | The title is the authors' own description of the system. HAMTL p. 7 names it "our previous work [13]"; HAMTL p. 26 resolves [13] to this DOI. | **ADMISSIBLE for the title-level claim only.** See the [VERIFY] flag below. |
| Zhang and Yang, A Survey on Multi-Task Learning | DOI `10.1109/TKDE.2021.3070203` | OpenAlex `works/doi:...`, abstract read via the inverted index | "Multi-Task Learning (MTL) is a learning paradigm in machine learning and its aim is to leverage useful information contained in multiple related tasks to help improve the generalization performance of all the tasks." Attributes confirm TKDE 34(12):5586-5609. | Already cited as `zhang2021survey`; **no change made.** Opened only to confirm HAMTL's [28] is the same work. |

**Unreached, and named rather than skipped.** HAMTL's [29] through [38] (the medical-imaging, NLP and
multi-behavior-recommendation cascaded-MTL citations) were **not opened and are not proposed**. They
are real MTL work with resolvable DOIs printed on pp. 26-27, but none is mobility work, and §2.3's
subsection is "Multitask learning for mobility prediction". Adding ten out-of-domain citations would
inflate the count Fabricio complained about without answering his complaint, which is about
MTL-for-POI coverage specifically. If the author wants general-MTL breadth instead, those ten are the
pool and they are listed on pp. 26-27 of the PDF.

## 4. [VERIFY] flags

1. **`wang2024iemtlf` — cited at the title level only.** The abstract and full text were NOT opened:
   Unpaywall reports the article closed, Semantic Scholar returns a null abstract field, OpenAlex
   carries no inverted index for it, and `api.elsevier.com` is outside this sandbox's network
   allowlist (403 at the proxy). The sentence written into §2.3 asserts nothing beyond what the
   title states plus the "our previous work" pointer on HAMTL p. 7. **Do not attribute a task
   structure, a dataset, or a number to it without opening the paper.** If the author prefers not to
   carry a title-level citation at all, deleting the one added sentence and the one added bib entry
   reverses it cleanly; the HAMTL fidelity correction stands independently.
2. **`CONSIDERATIONS.md` carries a now-stale verdict.** Its `wang2025hamtl` ledger row says
   "Localizada: NOT LOCATED" and "Veredito: INADMISSIBLE for any claim", and its FAB-28 row says
   BLOCKED. Both are superseded by this session. `CONSIDERATIONS.md` and `PENDENCIAS.md` are outside
   the files this item authorizes me to edit, so they were **not** updated. Per V6, correcting a
   finding at its source is not correcting the record: those two files still carry the old status.

## 5. Terms proposed for the registry, NOT used in prose beyond what already existed

`GLOSSARY.md` is fail-closed, and grep shows it registers no system names at all (`MCARNN`, `CSLSL`,
`iMTL`, `TME`, `HAMTL` all return zero hits), so §2.3's existing naming of cited systems is the
established practice and `IeMTLF` follows it. Two words in my new sentence, `auxiliary` and
`cascade`, were already in this same paragraph before I touched it (lines 720, 726, 734), so I
introduced no unregistered vocabulary. **Proposed for the author's decision, used by me only in this
report:** `main task` and `auxiliary task` as a registered pair, since the asymmetry they name is the
exact axis on which this dissertation's joint model differs from HAMTL, and Chapter 5 will need to
draw that contrast. I did not add them to the registry; registry rows are the author's alone.

## 6. Build

Run from `/Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src`, exit codes read directly
from `$?`, not through a pipe:

| Command | Exit code |
|---|---|
| `make defense` | **0** |
| `make check` | **0** |
| `make selftest` | **0** |

`make defense` produced `build/main-aux/main.pdf`, **106 pages**, identical to the baseline page
count, so `sync_page_counts` had nothing to reconcile. `make check` reports "68 of 68 probes hold"
and "All 25 gates under the 5s threshold". `make selftest` reports "PROVEN 5 | FAILED 0 | UNPROVEN or
HALF 12 of 17", the same distribution as the baseline.

**One failure happened and was fixed, and it is worth recording because it will recur.** The first
`make defense` returned **2**. The cause was not LaTeX but BibTeX: my provenance comment quoted the
paper's metric name with an at-sign in it, and BibTeX treats an at-sign inside a comment as the start
of an entry ("I was expecting a `{' or a `('---line 1185 of file references.bib"), which aborted the
bibliography run and left the new citation undefined. The metric names are now spelled out in words
in that comment and a note to future editors sits beside them. The rendered passage was then read
back out of the built PDF (page 26) to confirm both citations resolve to numbered references.

## UNFINISHED

- **`CONSIDERATIONS.md` and `PENDENCIAS.md` still record FAB-28 as BLOCKED** and `wang2025hamtl` as
  INADMISSIBLE. Both statements are now false. They are outside this item's authorized file list, so
  the author or a tracker item must retire them.
- **No probe was added to `check_audit_claims.py`.** GUARDRAILS §4b V15 wants the probe in the same
  commit as the fix. The natural probe is a `contains=` assertion on the phrase "main task and
  category prediction as an auxiliary task" in `2_fundamentals.tex`, which would fire if a later
  sweep reverted the fidelity correction. `check_audit_claims.py` is outside this item's file list,
  so it was not written.
- **HAMTL references [29]-[38] were not opened** (deliberate, see §3): ten cascaded-MTL works outside
  mobility. If the author wants general-MTL breadth in §2.3 rather than MTL-for-POI breadth, that is
  the pool.
- **IeMTLF's own content is unread** (see [VERIFY] 1). A UFV library copy of Information Sciences 661
  would settle whether it deserves a substantive sentence rather than a title-level one, and whether
  it has a region-like head. Given that the group's later paper does not, it very likely does not
  either, but that is an inference and it is not written into the document.
- **Fabricio's complaint is answered only partly.** He asked for more MTL-for-POI coverage; §2.3 now
  names seven systems where it named six. The honest finding of this session is that HAMTL, the
  paper he pointed at, does not open onto a large uncited MTL-for-POI literature: its own MTL section
  cites almost nothing from mobility. A systematic count, which is what the item title actually asks
  for, was not attempted inside the time budget and would need its own item.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-03 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
