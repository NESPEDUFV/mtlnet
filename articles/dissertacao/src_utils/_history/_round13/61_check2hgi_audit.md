# 61 — AUDIT TRACK: the Check2HGI / representation claims

**Author items covered:** 19, 20, 22, 24, and the second half of item 7.
**Phase:** audit only. No `.tex` file was edited; the `science/` spec was not edited. This file is the
only thing written.

## 0 · What I measured against, and with what

**Working tree state, read at the start of this session** (`cd /Users/vitor/Desktop/mestrado/ingred`):

```bash
git log --oneline -1     # -> 82080ce4 fix(gate): I said eight probes were sabotage-validated ...
git status --porcelain   # -> M articles/dissertacao/GLOSSARY.md
                         #    M articles/dissertacao/src/chapters/2_fundamentals.tex
                         #    M articles/dissertacao/src_utils/PENDENCIAS.md   (+ 11 others)
```

**Every prose line number in this report is a line of the WORKING-TREE file, not of the committed
version and not of `src/build/main.pdf`.** The built PDF was not opened at any point in this audit,
so no claim below is measured against it. Where the author's item names a PDF page (item 22 names
p.23) I resolved it to the source subsection by heading, not by page.

**Grep discipline (V4).** Every search over `.tex` filtered the file first:
`grep -vn '^[[:space:]]*%' "$f" | grep PATTERN`. This matters here more than usual: `poi2vec`
appears in four dissertation `.tex` files but in **live prose of only one** (item 20 below), and the
difference is entirely comment blocks. Both the filtered and the unfiltered counts are reported for
that search so the instrument is visible.

**Sources of record used.** For our own system the repository is the source of record, in this
order: the spec `articles/dissertacao/science/check2hgi_v17_complete_picture.md` (659 lines), the
MTL-side spec `science/mtl_v17_complete_picture.md` (446 lines), and then the code the spec names.
All code paths below were opened this session.

---

## ITEM 19 — "The representations used in this work are trained without category or region labels."

**Live sentence.** `src/chapters/2_fundamentals.tex:382`, first line of the body of §2.2.2
(`\subsection{Hierarchical graph infomax}`, heading at `:377`).

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src/chapters
grep -vn '^[[:space:]]*%' 2_fundamentals.tex | grep 'trained without category or region labels'
# -> 218:382:The representations used in this work are trained without category or region labels.
```
(the leading `218:` is the position within the comment-stripped stream; `382` is the real file line.)

**Author's premise.** "no hgi vamos sim usar o category como target, não usamos nos dois primeiros
para não gerar vazamento de dados para tarefa estática."

**Verdict: PARTLY CONFIRMED — the author is right that a category target exists in the pipeline,
and wrong about where it sits.** It is not in HGI's own objective, and it is not absent from "the
first two". The correct statement is per study, and it is different from his, so I am setting it out
in full rather than agreeing.

### (a) Is the POI category used as a TARGET anywhere in representation training?

**Yes, in exactly two places, and neither is a next-step target.**

**A19.1 — Check2HGI (Ch.5): masked-POI category reconstruction. This is a real category target.**
Spec §6.5, `check2hgi_v17_complete_picture.md:315-331`:

- `:317` — "The active auxiliary samples 15% of POIs independently each epoch and zeroes their
  canonical pooled POI vectors. It then mean-aggregates neighboring POI embeddings over the Delaunay
  graph and decodes only the masked rows with: `Linear(64, 128) -> PReLU -> Linear(128, 7)`."
- `:323` — "The target for each POI is the mean category one-hot vector of all its check-ins,
  equivalent to its empirical seven-category visit distribution."
- `:331` — "Its coefficient is `0.3`. It operates on the pre-augmentation canonical POI pool, so its
  gradients train the check-in GCN and Checkin2POI semantic path, not the Design-K regional POI
  table."

In the loss (spec §6.7, `:347-356`): `L_total = 0.4*L_c2p + 0.3*L_p2r + 0.3*L_r2c + 0.3*L_masked_poi
+ 0.1*L_anchor`, followed at `:358` by "No downstream next-step target appears in this loss."

Confirmed in code, opened this session:

- Target construction: `research/embeddings/check2hgi/preprocess.py:457` `def
  _compute_poi_feature_aggregates`, docstring `:461-464` ("mean category one-hot of constituent
  check-ins (P, num_cat), i.e. the empirical category distribution over the visits to that POI"),
  computation `:485-491` (`np.add.at(counts, (poi_idx, cat_idx), 1.0)` then row-normalize).
- Decoder: `research/embeddings/check2hgi/model/variants.py:203` `class MaskedPOIDecoder`.
- Wiring, and this is the line that settles that the term is ON in the shipped build:
  `scripts/probe/build_design_k_delaunay.py:267-284` constructs `Check2HGI_DesignK(...
  mae_poi_lambda=_mae_lambda, mae_poi_mask_rate=0.15, mae_poi_target_kind="category_aggregate",
  mae_poi_loss_kind="sce", ...)`, and the spec's reproduction command at `:620-641` passes
  `--mae-poi-lambda 0.3`. The module default is `mae_poi_lambda: float = 0.0`
  (`Check2HGIModule.py:104`), i.e. off unless requested — and it is requested.

So a loss term whose target is a seven-dimensional category distribution carries weight 0.3 of five
weighted terms in the shipped Check2HGI objective. That is a category target.

**A19.2 — POI2Vec, upstream of both HGI and Check2HGI: a category-to-fine-class L2 pull. This is a
category *label* term, though not a classification target.** `research/embeddings/hgi/poi2vec.py`:

- `:116-121` class docstring: "Hierarchical fclass embedding model with category-fclass L2
  regularization. ... Loss: Skip-gram + L2(category_emb, fclass_emb)".
- `:356-361` — hierarchy pairs are extracted from the POI table's `['category', 'fclass']` columns.
- `:172-182` — `loss_hierarchy = 0.5 * self.le_lambda * (diff * diff).sum()` over those pairs,
  returned as part of `loss_graph + loss_hierarchy` (`:186`).
- Weight: `le_lambda=1e-8` at every call site I could find
  (`grep -rn "le_lambda" --include=*.py .` outside worktrees: definitions at `poi2vec.py:124,332,552`
  and the only non-ablation caller `experiments/scripts/profile_poi2vec_alabama.py:96`, plus the
  five ablation arms in `experiments/hgi_leakage_ablation.py:88-96`). `pipelines/embedding/hgi.pipe.py:143`
  and `scripts/substrate_protocol_cleanup/run_poi2vec.py:38` call `train_poi2vec(...)` **without**
  passing `le_lambda`, so they inherit the `1e-8` default.
- The code's own framing, `poi2vec.py:341-343`: "`le_lambda`: Weight on the category-fclass
  hierarchical L2 loss. Set to 0.0 to disable **the only explicit category-label path** into fclass
  embeddings (leakage ablation arm A)." Emphasis mine; that phrase is the repository's own
  characterization and it is the strongest single piece of evidence for the author's instinct.

At `1e-8` this term is numerically negligible against a skip-gram loss of order 1, so its practical
contribution is near zero — but *"trained without category labels"* is a statement about the
objective, not about the gradient magnitude, and this term is in the objective.

**Where POI2Vec lands.** POI2Vec is a build-time phase *inside* HGI
(`research/embeddings/hgi/hgi.py:207` "Phase 3b-3d: POI2Vec → fclass embeddings → POI embeddings";
executed at `:229-236` before HGI's own Phase 5 training). Its output CSV is also read by Check2HGI's
Design-K branch (spec `:111-112`; loader `research/embeddings/check2hgi/reg_poi_aug.py:27-35`). So
this term touches **Ch.4 (via HGI) and Ch.5 (via the anchor)** but not Ch.3.

**A19.3 — What is NOT a category target, checked so the two above are not overstated.**

- **HGI's own objective has no category term.** `research/embeddings/hgi/model/HGIModule.py:265-306`:
  `loss_poi2region` and `loss_region2city`, both contrastive; combined at `:306` as
  `loss_poi2region * alpha + loss_region2city * (1 - alpha)`. `grep -n "cross_entropy\|CrossEntropy\|category"
  research/embeddings/hgi/model/HGIModule.py` returns **nothing** — and that grep is validated by the
  same pattern returning 6 hits on `check2hgi/model/Check2HGIModule.py`, so it is not a broken
  instrument (V13/V17).
- **DGI's objective has no category term.** `research/embeddings/dgi/dgi.py:24` `loss =
  model.loss(pos_score, neg_score)` where `model` is `DGIModule` (`:43`); `DGIModule.loss`
  (`model/DGIModule.py:80-87`) is BCE of positive vs corrupted scores. A supervised
  `GCNClassification` with a weighted `CrossEntropyLoss` **does exist** at
  `research/embeddings/dgi/model/GCNEncoder.py:21-48` — but `grep -rn "GCNClassification"
  --include=*.py .` (excluding worktrees/.temp) returns **only its own definition and its `super()`
  call**, i.e. it is never instantiated. The same holds in the CoUrb codebase copy
  (`/Users/vitor/Desktop/mestrado/temp/tarik-new/PoiMtlNet_Novo/src/embeddings/dgi/model/GCNEncoder.py:21,23`
  and nowhere else). Dead code, reported here because a future reader greping "CrossEntropyLoss" in
  the DGI module will find it and reach the opposite conclusion.
- **The three `cross_entropy` calls in `Check2HGIModule.py` are InfoNCE, not category
  classification**: `:1051` (co-visit InfoNCE, in a docstring), `:1116`/`:1121` (p2p InfoNCE, off at
  `p2p_lambda=0`, spec `:588` inactive table), `:1178` (full-region p2r InfoNCE, off, spec `:588`).
  In each the "class index" is a position in the batch, not a category.

### (b) Is the category an INPUT FEATURE of a check-in node?

**Yes, unambiguously, and this is separate from (a).** Spec §3.2, `:66-76`: the check-in node feature
vector is `[category one-hot, sin/cos(hour), sin/cos(day_of_week)]`, "The final datasets use seven
categories, so the active input width is `7 + 4 = 11`". Code: `check2hgi/preprocess.py:615-641`,
`_build_node_features` — `category_onehot[np.arange(num_checkins), self.checkins['category_encoded'].values]
= 1.0` at `:623-624`, concatenated with the four temporal channels at `:639`.

The spec states the distinction itself at `:50`: "The representation builder never receives the
supervised **next-category** or **next-region** targets. A visit's own category is nevertheless an
input feature, and aggregated current-visit category features are used by the masked reconstruction
auxiliary. \"Label-free\" here means no downstream future target, not absence of categorical
information from the graph input."

That sentence is the honest form of the claim, and the live Ch.2 sentence is a strictly stronger
claim than it.

### (c) Per study, and what the protection actually is

| | Ch.3 (CBIC, DGI) | Ch.4 (CoUrb, decomposed) | Ch.5 (MobiWac, Check2HGI) |
|---|---|---|---|
| Category as an **input feature** | Yes — mean of *neighbors'* category one-hots, self excluded (`research/embeddings/dgi/preprocess.py:115,125-130`; published note at `3_cbic/method.tex:23` footnote) | Yes — the categorical channel is HGI over POI2Vec fclass embeddings (`4_courb/methodology.tex:157,235`) | Yes — the visit's **own** category one-hot, 7 of 11 input dims (spec `:66-76`) |
| Category as a **target in a loss** | **No.** DGI loss is BCE real-vs-corrupted only | **Yes, indirectly and negligibly** — the POI2Vec `le_lambda=1e-8` category↔fclass L2 inside the categorical encoder | **Yes, twice** — masked-POI category-distribution reconstruction at weight 0.3, and the POI2Vec anchor at weight 0.1 which inherits the same POI2Vec table |
| Region as a **target in a loss** | No | **Yes** — HGI's `L_poi2region` scores a POI against *its own region* vs another region (`HGIModule.py:275-292`); Ch.2 says so at `:411-413` | **Yes** — `L_p2r` and `L_r2c`, spec `:301-311` |
| Next-category / next-region target | No | No | **No** — spec `:528` |

Two consequences the author's framing inverts:

1. **"no hgi vamos sim usar o category como target" — not in HGI's own loss.** HGI's two loss terms
   are POI↔region and region↔city (`HGIModule.py:265-306`). What is true is that HGI's *input
   features* are POI2Vec vectors that were themselves trained with a category↔fclass L2 term, and
   that POI2Vec's reconstruction step is a pure fclass lookup (`poi2vec.py:449-505`,
   `poi_embedding[i] = fclass_embeddings[poi.fclass[i]]`) — which is precisely the identity
   Appendix B §B.5 documents for the static task (`apx_b_static_scope.tex:33-41`).
2. **"não usamos nos dois primeiros" — the pipeline with the *most* explicit category target is the
   third, Ch.5.** The masked-POI reconstruction is a Ch.5 mechanism only; neither Ch.3 nor Ch.4 has
   anything like it.

**What is actually protected.** Three separate guarantees, and only the first is airtight:

- **No next-step target ever enters representation training.** Spec `:528`: "The Check2HGI objective
  never sees the next-category or next-region target attached to a supervised window." Structurally
  guaranteed: representation training is full-batch over the whole graph with no window construction
  at all (spec §7.1, `:364`: "There is no node mini-batching, neighbor sampling, fold split, or
  downstream label split during representation training"), and windows are built afterward by a
  separate script (§9, `:462-478`).
- **The *static* category-classification task is the one a category target would compromise** — and
  that task does not exist in Ch.5. It is the Ch.3/Ch.4 task (`2_fundamentals.tex:265-268`;
  Definition 2.3 at `:241`). The author's instinct is exactly right about the *mechanism*; the fact
  pattern is that Ch.5 removed the vulnerable task rather than removing the category signal.
- **What is not protected, and is not claimed to be:** the *current* visit's category is in the
  input by design, and the graph links consecutive visits, so a per-visit vector could absorb a
  neighbor's category. Ch.5 already discloses this and measures it: `5_mobiwac/05_setup.tex:64`
  ("That bounds the training signal and not the inputs, since each visit's own category enters as a
  node feature") and `:70` (the fourth ground: the screening audit against the clean reference
  encoder). See item 7 below.

### (d) Is the live sentence TRUE, FALSE, or TRUE-ONLY-UNDER-A-NARROWER-READING?

**TRUE-ONLY-UNDER-A-NARROWER-READING, and the narrower reading is not available to the reader at
that point in the chapter.**

Under the reading "no *downstream task target* (next category, next region, or the static category
of the classified POI) is attached to the objective", the sentence is true for all three studies.
Under the plain reading a reader of §2.2.2 will take — "no category label appears anywhere in the
training signal" — it is false for Ch.5 (weight-0.3 category-distribution reconstruction) and
false-in-principle for Ch.4 (the `1e-8` term). Nothing in the surrounding paragraphs supplies the
narrower reading; the following sentences all reinforce the broad one, and `:402-404` closes with
"No label of any downstream task enters that comparison, so the representation is obtained without
supervision" — which is defensible only because it is scoped to *that comparison* (the bilinear
discriminator), a scope the reader has to notice.

**Two more places carry the same over-claim and must move together with `:382`:**

- `2_fundamentals.tex:601-603` — "learns one vector per visit **without using task labels**"
  (item 22, assertion A3 below).
- `2_fundamentals.tex:625-626` — "No prediction target appears in these equations, which is why the
  representation is described as trained without task labels." This one is **true as written**
  (three-boundary equation only) but the drafting agent's own comment at `:648-652` already flagged
  that Eq. (2.1) is not the complete shipped loss, with a `[VERIFY]`. That VERIFY is now answered:
  the shipped loss has five terms, spec `:347-356`.

**Narrowest correct wording I can defend (proposal only — I did not edit the file).** Replace `:382`
with the *scope* rather than the absence:

> The representations used in this work are trained without any prediction target: no objective
> reads the category or the region of a future visit, and none reads the category of a place as a
> label to be classified. A visit's own category does enter, as an input feature of its node.

If the author prefers a one-sentence form that keeps §2.2.2 thin, the minimum honest edit is to
delete "or region": HGI's `L_poi2region` scores each POI against its own region embedding
(`HGIModule.py:275-292`), which Ch.2 itself describes two paragraphs later at `:411-413`, so
"without ... region labels" is contradicted *inside the same subsection*. That internal
contradiction is independent of everything above and holds even under the narrow reading, because
region membership is a *current* property, not a future target.

**Disposition: I_DECIDE.** It is a WRITING_LAW §3 honesty edit on a sentence the author flagged
himself, it changes what the document claims, and the replacement wording introduces a scope
statement that is a C2 new claim. Three sentence sites, one paragraph of work.

---

## ITEM 20 — POI2Vec: does it have to be cited?

**Author's premise.** "no check2hgi, como descrito em check2hgi_v17_complete_picture.md também
usamos POI2vec, não teríamos que citar ele?"

**Verdict: PARTLY CONFIRMED. POI2Vec is genuinely in the pipeline, but citing `feng2017poi2vec` for
it would be a misattribution of exactly the CBIC POI-RGNN errata class.**

### (a) What role POI2Vec plays in Check2HGI — precisely

Three roles, all in the **spatial/regional** branch, none in the semantic check-in path:

1. **An external input table.** Spec §3.4, `:109-112`: "Design K adds two inputs produced by the HGI
   pipeline and remapped by `placeid` into Check2HGI's POI index space: 1. A 64-dimensional POI2Vec
   table from `output/hgi/<state>/poi2vec_poi_embeddings_<State>.csv`." Unmapped rows handled at
   `:116`: "Check2HGI POIs absent from POI2Vec retain a zero row."
2. **The initialization of a trainable table.** Spec §4.3, `:199-207`: `z_pre =
   stop_gradient(z_poi_canonical) + gamma * E_poi`, where "`E_poi` is a trainable
   `Embedding(num_pois, 64)`. It is initialized exactly from the remapped frozen POI2Vec table ...
   The POI2Vec source table is retained as an immutable anchor buffer." Code:
   `Check2HGIModule.py:471-474` — `self.reg_poi_table = nn.Embedding(int(num_pois),
   hidden_channels)`, `self.reg_poi_table.weight.copy_(poi2vec_table.float())`,
   `self.register_buffer("reg_poi2vec_anchor", poi2vec_table.float())`.
3. **An auxiliary loss term (the anchor).** Spec §6.6, `:335-343`: "The trainable regional POI table
   is regularized toward its frozen initialization: `L_anchor = mean((E_poi -
   E_poi2vec_frozen)^2)` ... Its coefficient is `0.1`." Code: `Check2HGIModule.py:1125-1135`,
   `return ((self.reg_poi_table.weight - self.reg_poi2vec_anchor) ** 2).mean()`.

So: **initialization AND frozen anchor buffer AND an auxiliary loss, all three** — the author's three
candidate roles are all correct simultaneously. It is not merely an initialization.

### (b) Does live prose mention it?

**Chapter 2: no. Chapter 5: not by that name.**

```bash
cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src
for f in $(find chapters -name '*.tex'); do
  out=$(grep -vn '^[[:space:]]*%' "$f" | grep -i 'poi2vec'); \
  if [ -n "$out" ]; then echo "--- $f"; echo "$out"; fi; done
# -> only: chapters/4_courb/related.tex:16 (the published related-work sentence)
grep -ril 'poi2vec' chapters/ | head
# -> 2_fundamentals.tex, 4_courb/related.tex, apx_b_static_scope.tex, apx_b_errata.tex
```
Four files match unfiltered, one matches in live prose. The three-file gap is entirely provenance
comments — the exact V4 failure mode, and the reason both counts are printed here.

Chapter 5 does refer to the mechanism without the name: `5_mobiwac/04_method.tex:19` — "an anchor to
a place embedding pre-trained, label-free, on the same data". True and complete as far as it goes;
it does not name POI2Vec and does not cite anything for it.

### (c) Does the MobiWac paper of record mention it?

**No.** Same filtered sweep over `articles/[mobiwac]/src/**/*.tex`: zero live-prose hits for
`poi2vec`; the only `anchor` hits outside `04_method.tex:21` are TikZ node anchors in
`src/figs/fig2_model.tex`. `feng2017poi2vec` **exists in that bib** (`src/references.bib:179`, header
comment `:7` says it was "ported from the CoUrb bib") but is **cited zero times in live prose** —
filtered `grep -o 'feng2017poi2vec'` over every `.tex` in `src/` returns nothing, while the same
harness returns 5 hits for `huang2023hgi`, so the instrument works.

### (d) The bib entry, and WHICH paper would be meant — the misattribution risk

`articles/dissertacao/src/references.bib:153` holds `@inproceedings{feng2017poi2vec}`, cited once in
live prose, at `4_courb/related.tex:16`, where it correctly describes the AAAI'17 method ("adapts the
Word2Vec architecture ... through a geographic binary tree structure").

**That paper is NOT what our pipeline runs.** The module says so itself, in a note the author's
collaborators wrote — `research/embeddings/hgi/poi2vec.py:3-9`:

> "⚠ NAMING (clarity note, 2026-06-19): despite the module/class name, this is an *fclass-level
> hierarchical Node2Vec teacher* used INSIDE HGI — it is NOT the AAAI'17 POI2Vec baseline (Feng et
> al. 2017). The faithful AAAI'17 POI2Vec baseline lives in ``scripts/baselines/poi2vec_lib/``."

Read against the code, that note is accurate. What our `poi2vec.py` implements
(`:11-22`, `:279`, `:356-378`, `:449-505`): PyG `Node2Vec` random walks over the Delaunay POI graph →
walks converted to **fine-class** sequences → skip-gram with hard negative sampling (negatives are
fclasses that never co-occurred with the center, `:74-83`) → a category↔fclass hierarchical L2 term
→ POI embeddings reconstructed by fclass lookup. The AAAI'17 method, as implemented faithfully
elsewhere in this same repository at `scripts/baselines/poi2vec_lib/model.py:1-40`, is a fixed
recursive rectangular midpoint geo-tree + overlap-area φ routing + CBOW + hierarchical softmax + a
negative-sampled user term. **Not one of those four mechanisms is present in the module our
representation actually uses.** The two implementations coexist in this repo under names that differ
only by directory.

**Therefore, three options, and I am not choosing among them:**

- **(i) Cite nothing new, name the mechanism.** Ch.2 (and optionally Ch.5) says the regional POI
  table is initialized from, and regularized toward, a place-level table pre-trained by
  category-aware random walks over the Delaunay graph. Accurate, no new bib entry, no attribution
  risk. Node2Vec (`grover2016node2vec`) and skip-gram/negative-sampling (`mikolov2013word2vec`,
  `mikolov2013negsampling`) are all already in the dissertation bib and already cited by
  `4_courb/methodology.tex:189,194` for this same component under the name "POI Encoder" — which is
  the honest name for it and the one Ch.4 already uses.
- **(ii) Cite `feng2017poi2vec` for it.** **I recommend against this.** It is the POI-RGNN errata
  class: a real paper attached to a sentence its method does not support. If the author wants the
  name POI2Vec in the text at all, it must come with the disclaimer that the implementation is a
  local fclass-level Node2Vec teacher, not that paper's method — at which point option (i) is
  cleaner.
- **(iii) Keep the text silent.** Defensible for Ch.5 (page limit, submitted, and `04_method.tex:19`
  already discloses the anchor's existence and its label-free provenance). Weaker for Ch.2, whose
  Eq. (2.1) already under-describes the shipped loss by two terms.

**Note the coupling to item 19.** Any option that names the anchor in Ch.2 must also fix `:382`,
because the POI2Vec teacher carries the `le_lambda` category term (A19.2) — naming the anchor while
claiming "trained without category labels" would put the two sentences in the same subsection.

**Disposition: I_DECIDE.** It is a citation-attribution decision with a live misattribution risk,
and AGENT_GUARDRAILS R2 puts "describe cited systems as their authors describe them" on the author's
side of the line. Size: one clause in Ch.2 under option (i); a bib entry plus a hedge under (ii).

---

## ITEM 22 — Is §2.2.3.2 "The check-in level" correct against the spec?

Subsection heading at `2_fundamentals.tex:599`; body `:601-626` plus the closing paragraph
`:662-666`. Renders at PDF p.23 per the author; I did not open the PDF, and the working-tree source
is 14 minutes newer than the build, so the two may differ.

Every factual assertion the subsection makes, in order, each with its own verdict and its own spec
line:

| # | Assertion (source line) | Verdict | Evidence |
|---|---|---|---|
| A1 | "Check2HGI completes the move from contextualized inputs to one learned representation per visit" (`:601-602`) | **SUPPORTED** | Spec `:34` "Its central change relative to a place-level embedding is that every **visit** receives its own vector"; export contract §8.1 `:481-489`, `embeddings.parquet` = "One row per check-in" (`:44` table) |
| A2 | "It adds a fourth level below the place" (`:602`) | **SUPPORTED** | Spec `:36-40`: "The hierarchy has four levels: `check-in event -> POI/place -> geographic region -> city`" |
| A3 | "and learns one vector per visit **without using task labels**" (`:602-603`) | **CONTRADICTED under the plain reading; SUPPORTED under "no downstream task target"** | Spec `:50`: "\"Label-free\" here means no downstream future target, **not absence of categorical information from the graph input**"; and the shipped loss carries `0.3 * L_masked_poi` whose target is a category distribution (`:323`, `:352`). Same defect as item 19, second site |
| A4 | "The hierarchy has three adjacent-level boundaries: check-in to place, place to region, and region to city" (`:603-605`) | **SUPPORTED** | Spec §6.2/§6.3/§6.4 `:293-311`; four levels give three boundaries, consistent with A2 |
| A5 | "Its objective is the fixed-weight sum `L = 0.4 L_c2p + 0.3 L_p2r + 0.3 L_r2c`" (`:605-608`) | **CONTRADICTED as stated ("its objective"); the three weights themselves are CORRECT** | Spec `:290` gives exactly this as `L_hier`, "The **base** hierarchical objective". Spec `:347-356` gives the actual v14 objective as five terms: `+ 0.3*L_masked_poi + 0.1*L_anchor`. The chapter presents a three-term sum as *the* objective. Ch.5 `04_method.tex:19` names the two extra terms with their weights, so the document states two different objectives for one artifact, twenty pages apart |
| A6 | "Each term uses a bilinear discriminator, `D(e1,e2) = σ(e1ᵀ W e2)`" (`:610-613`) | **SUPPORTED** | Spec `:281-284`: "Each hierarchy boundary has a learned `64 x 64` bilinear matrix ... `D(a,b;W) = sigmoid((a W) dot b)`". Code `Check2HGIModule.py:246`, `:1003-1018` |
| A7 | "`σ(z)=1/(1+e^{-z})` is the logistic function ... output lies between 0 and 1" (`:614-616`) | **SUPPORTED** | Definitional; matches spec `:283` `sigmoid`. GLOSSARY §3 registers "logistic function" and forbids "sigmoid" in prose — the chapter complies |
| A8 | "the loss favors a high score for a true pair and a low score for a false pair: `L_* = -log D(e⁺,e⁺) - log(1 - D(e⁺,e⁻))`" (`:617-622`) | **SUPPORTED** (transcription faithful) | Spec `:284`: `L_boundary = -mean(log D_positive) - mean(log(1 - D_negative))`. The chapter's per-example form drops the spec's `mean`, which the source it transcribes from (`docs/context/check2hgi_overview.tex:227`) also does — the two are the same equation at different granularity, not a discrepancy |
| A9 | "`e⁺` belongs to a true pair, such as a check-in and the place where it occurred" (`:623-624`) | **SUPPORTED** | Spec §6.2 `:295`: "For every check-in, the positive pair is its contextual check-in vector and its own canonical pooled POI vector" |
| A10 | "`e⁻` is substituted from another example in the batch" (`:624-625`) | **PARTLY SUPPORTED — imprecise for two of the three boundaries** | c2p: spec `:297` "a uniformly sampled **different POI** from the positive canonical POI matrix" — consistent. p2r: spec `:303-305` — negatives are other **region** vectors, and 25% may be replaced by a *hard* negative whose POI-category-distribution cosine lies in (0.6, 0.8); "substituted from another example in the batch" does not describe that. r2c: spec `:311` — negatives come from "a second hierarchy evaluated from the **shuffled** check-in features", i.e. a corruption pass, not a batch substitution. Also "batch" is misleading in a full-batch regime (spec `:364`: "One epoch consists of one forward and backward pass over the complete graph") |
| A11 | "No prediction target appears in these equations, which is why the representation is described as trained without task labels" (`:625-626`) | **SUPPORTED as written, MISLEADING in context** | Literally true of Eqs. (2.1)–(2.3). But it licenses the broad claim of A3 from a scope ("these equations") that A5 has already misidentified as the whole objective. The drafting agent's own comment at `:648-652` flagged this and left a `[VERIFY]`; that VERIFY is now answered — the two auxiliaries are ON in the shipped build (`build_design_k_delaunay.py:279-284`, `--mae-poi-lambda 0.3 --anchor-lambda 0.1`) |
| A12 | "Where a place embedding answers ``what is this place,'' a check-in-level representation answers ``what is this visit''" (`:662-664`) | **SUPPORTED** | Spec `:34`; Definitions 2.1/2.2 at `2_fundamentals.tex:175-179` and `:206-210` |
| A13 | "Table 2.x traces the full progression, from DGI through HGI to the check-in level and the joint model" (`:665-666`) | **SUPPORTED** (cross-reference resolves) | `\label{tab:fund:lineage}` exists at `src/tables/frame/lineage.tex:9` |

**Summary: 9 of 13 supported, 2 contradicted (A3, A5), 1 partly supported (A10), 1 supported-but-
misleading (A11).** The two contradictions are one defect with two heads: the subsection presents the
*base hierarchical* objective as the *complete* objective, and then draws a label-free conclusion
from it. Fixing A5 (name the five-term loss, or say explicitly that Eq. (2.1) is the hierarchical
core and the shipped configuration adds two auxiliary terms that Chapter 5 names) also fixes A3 and
A11, and is the same edit item 19 needs.

A10 is a smaller, independent inaccuracy and is worth a separate half-sentence.

**Disposition: I_DECIDE.** A5/A3/A11 change what the chapter claims about our own system (C2). A10
alone would be YOU_APPLY, but it sits in the same paragraph.

---

## ITEM 24 — "The models therefore differ in their sharing topology and in the private input available to the region output."

Live sentence: `2_fundamentals.tex:679-680`, in §2.2.4 `\subsection{Model lineage}` (`:667`).

**Author's premise.** "no MTLnet ele já recebia duas entradas, a diferença é que as duas entradas lá
eram de um mesmo embedding, aqui os embeddings são saídas diferentes do check2hgi, apesar de serem
diferentes elas ainda possuem correlação."

**Verdict: CONFIRMED on (a) and (b); PARTLY CONFIRMED on (c) — his correlation claim is directionally
right and the spec supports a *mechanism*, not a measured correlation.**

### (a) Did MTLnet take two inputs derived from ONE embedding? — YES

**Two inputs: yes.** `src/models/mtl/mtlnet/model.py:418` — `category_input, next_input = inputs`;
encoded separately at `:431-432` by `self.category_encoder` / `self.next_encoder`, built at `:112`
and `:119`. Ch.3 states it: `3_cbic/method.tex:78` — "Input features for POI Category Classification
($\mathbf{x}^{(c)}$) and Next-POI Prediction ($\mathbf{x}^{(n)}$) are first processed by separate,
task-specific encoders."

**From one embedding: yes, and this is stated in both paper chapters.**

- Ch.3: the static input is one POI's 64-d DGI vector, `3_cbic/method.tex:53` — "Each POI is
  represented by its 64-dimensional DGI embedding $\mathbf{e}\in\mathbb{R}^{64}$"; the sequential
  input is nine of the same vectors concatenated, `:64` — "the concatenation of the 64-dimensional
  embeddings of $p_1$--$p_9$, yielding a $9\times64=576$-dim vector". Same table, one shape per task.
- Ch.4: identical structure at 192-d. `4_courb/methodology.tex:93` — the static input is
  $\mathbf{E}_{cat} = [\mathbf{E}_{HGI} \| \mathbf{E}_{loc} \| \mathbf{E}_{time}] \in
  \mathbb{R}^{192}$; `:95` — the sequential input is "$9 \times 192 = 1728$ dimensions".
  `4_courb/methodology.tex:12` says it of the baseline in as many words: MTLnet "uses a single vector
  $\mathbf{E}_{DGI} \in \mathbb{R}^{64}$ **as input for both tasks**".
- Verified in the CoUrb codebase copy at `/Users/vitor/Desktop/mestrado/temp/tarik-new`
  (granted rw, read-only use): `PoiMtlNet_Novo/src/etl/create_inputs_hgi.py:407` —
  `def process_state(state, cat_embeddings=("poi","loc","time"), next_embeddings=("poi","loc","time"))`,
  and `:473`/`:484` build `X_cat` and `X_next` by `np.hstack` over the **same** `emb_map` dict
  (`:469`). Same three source tables for both tasks; the CLI can vary them (`:557`), the default does
  not. This is firsthand confirmation of the author's claim, from the CoUrb code rather than from
  its paper.

So: **two inputs, one representation, differing only in whether it is read once (a place) or nine
times (a window).** The author is right, and Ch.2's current sentence does not say this.

### (b) In the joint model, are the two streams fed by DIFFERENT Check2HGI outputs? — YES. Named.

The two tensors, from the export contract (spec §8) and the consumption contract (spec §10, `:498-510`):

| Stream | Exported table (spec §8) | What its rows are | Shape into the model |
|---|---|---|---|
| Category / semantic | **`embeddings.parquet`** (§8.1, `:481-489`) — columns `userid, placeid, category, datetime, 0..63`; "One row per check-in" (`:44`) | "the output of the residual check-in GCN, **before POI pooling and before Design-K regional augmentation**" (`:489`) | `[9, 64]` contextual check-in vectors (`:500-503`) |
| Region / spatial | **`region_embeddings.parquet`** (§8.3, `:493-496`) — columns `region_id, reg_0..reg_63` | "the outputs after POI-to-region attention and region adjacency GCN" (`:496`); looked up per historical visit through `placeid -> poi_idx -> region_idx` (`:496`) | `[9, 64]` region vectors (`:505-509`) |

`poi_embeddings.parquet` (§8.2) is the third export and is **not** read by the model: spec `:512`
"The POI export is not directly fed to `mtlnet_crossattn_dualtower`. Its influence is already
incorporated into the trained region vectors." Corroborated by the MTL-side spec,
`mtl_v17_complete_picture.md:21-23` (slot A input "64-dimensional Check2HGI check-in
representation", slot B "64-dimensional Check2HGI region representation").

**Note a real difference in kind, not just in table:** the region stream "intentionally repeats a
region vector whenever multiple visits map to the same region" (spec `:511`), so it is *not* a
per-visit representation. The two streams differ in granularity, not only in provenance. Ch.2
already states this correctly at `:232-234` in §2.1.

### (c) The correlation claim

**What the spec supports.** The two streams descend from a **shared forward computation up to the
canonical POI pool**, and the split is a gradient boundary rather than a value boundary. Spec §4.3,
`:199`: `z_pre = stop_gradient(z_poi_canonical) + gamma * E_poi`; `:215-222`:

> "The `detach()` is load-bearing. It creates an explicit one-way boundary: the regional losses may
> use the semantic POI content **numerically**; their gradients cannot update the check-in encoder or
> `Checkin2POI` through that content ... **The two branches share the same forward value up to the
> canonical POI pool, but do not share all backward paths.**"

Restated in the compact definition, `:657`: "The spatial path receives a stop-gradient copy of that
POI pool, adds a trainable POI2Vec-anchored table, diffuses it over weighted Delaunay POI edges,
pools into regions, and diffuses again over polygon adjacency."

Code: `Check2HGIModule.py:653-654` — `pos_pre_gcn = pos_poi_emb.detach() + self.reg_gamma *
poi_residual` (and the negative branch at `:654`).

So the region vector of a visit is a function — through POI-to-region attention and two graph
convolutions — of a pooled POI vector that the *same* check-in vectors produced. **The two streams
are statistically dependent by construction.** That is a structural statement the spec licenses, and
it is stronger than "they come from the same model": the dependence has a named path.

**What the spec does NOT support, and what I did not compute.** No number. The spec reports no
correlation, cosine, or mutual-information measurement between `embeddings.parquet` rows and the
`region_embeddings.parquet` rows they map to, and I did not run one (running it would need the frozen
parquet artifacts per state and would be a new measurement, not an audit finding). **The author's
word "correlação" must therefore stay qualitative in prose**, or be replaced by the mechanism. Any
sentence of the form "the two inputs are correlated" is a C2 new claim needing a measurement or a
hedge → `[VERIFY-24.1]` below.

**Two further facts that bear on how the sentence should read, both from the spec's own gradient
map** (§5, `:257-265`), because they cut *against* an unqualified "the streams are correlated":

- `L_masked_poi` and `L_c2p` train the check-in encoder and `Checkin2POI`; `L_p2r` and `L_r2c` are
  marked "**No, detached**" for both of those columns. So the spatial objectives never shape the
  semantic vectors.
- Spec `:265`: "the exported check-in representation is trained by the semantic objectives, while
  the exported region representation is trained by the spatial objectives plus the anchored POI
  substrate." The dependence is **one-way**: region ← check-in (forward values), not the reverse.

That one-way asymmetry is the precise, defensible version of the author's "apesar de serem
diferentes elas ainda possuem correlação", and it is more interesting than a correlation coefficient
would be.

**What the sentence at `:679-680` is missing.** It states the *difference* (sharing topology; private
region input) without the *contrast the author wants*: that both architectures have always taken two
inputs, and what changed is that the two inputs stopped being two views of one table and became two
different outputs of one representation — related by a stop-gradient boundary rather than identical.
A two- to three-sentence expansion, all of it sourceable from the rows above.

**Disposition: I_DECIDE.** Three new sentences about our own architecture in the frame chapter, one
of which characterizes the coupling between two inputs — C2 territory, and the "correlated" wording
needs the author's ruling on hedge-versus-measure.

---

## ITEM 7 (second half) — does the check-in vector encode the CURRENT visit's category, and should it?

**Author's premise.** "sobre regime de checking level e nosso motor de embedding, o embedding pode
vazar e deve vazar qual a categoria do checking atual, até para o modelo conseguir prever com mais
exatidão a próxima categoria."

**Verdict: CONFIRMED. It does, it is by design, it is documented, and it is the reason the static
task could not survive into Ch.5.**

### It does encode the current visit's category

- **By input.** The category one-hot is 7 of the 11 input dimensions of the check-in node (spec
  `:66-76`; code `check2hgi/preprocess.py:623-624,639`). The encoder is a two-layer residual GCN with
  a residual sum (`spec :169-173`: `z_checkin = x1 + h2`), so the node's own features are not merely
  neighborhood-averaged away.
- **By objective.** `L_c2p` (weight 0.4) pulls each check-in vector toward its own POI's pooled
  vector (spec `:295`), and the masked-POI auxiliary (weight 0.3) explicitly trains the pooled POI
  vectors to carry the POI's empirical category distribution (spec `:323`). Both push category
  information *into* the visit vectors.
- **Measured, in live prose.** `5_mobiwac/06_results.tex:20`: per-visit vectors reach silhouette by
  category of about $0.57$ (against about $0.00$ for the place embedding) and nearest-neighbor
  category purity of about $0.98$ (against about $0.78$), averaged over the five U.S. states. A
  0.98 own-category purity is as direct a statement as this document contains that the current
  category is recoverable from the vector.

### Is it by design? Yes — and the spec says so in the author's own framing

Spec `:50`: "A visit's own category is nevertheless an input feature ... \"Label-free\" here means no
downstream future target, not absence of categorical information from the graph input." The
distinction between *current* category (in, deliberately) and *next* category (out, structurally) is
the spec's organizing principle for this question.

The author's "**deve** vazar" — that it *should* — is a design rationale, not a fact about the code,
and the repository states the same rationale in its own terms:
`docs/studies/archive/embedding_eval/L0_METHODOLOGY.md:9-12` — "**next-cat (static-attribute task):
L0 is a legitimate, near-sufficient RANKER.** The target (a POI's own category) is a static property
carried in the embedding geometry, so own-label separability metrics ... map monotonically to
L2-cat." That is an internal study document, not a dissertation claim.

### The consequence for the STATIC task — this is the load-bearing part

If the per-visit vector encodes the current visit's own category with ~0.98 nearest-neighbor purity,
then a **static category-classification task defined on that vector is a lookup**, structurally the
same defect Appendix B §B.5 documents for Ch.4 — where the place embedding is a lookup table on the
fine class and "the input therefore contains the answer" (`apx_b_static_scope.tex:39-41`, with the
284–365 fine classes and the zero-ambiguity mapping at `:42-45`).

**So the task-pair change is not only a modeling-taste decision. Under a check-in-level
representation the static task would have been degenerate by construction.** That is the reason the
author is reaching for, and it is stronger than the reason Ch.1 currently gives.

### Already documented vs. new claim needing sign-off (C2)

| Statement | Status |
|---|---|
| Each visit's own category is an input feature of its node | **DOCUMENTED, live.** `5_mobiwac/04_method.tex:18`; `5_mobiwac/05_setup.tex:64` |
| The training objective never sees a next-category or next-region target | **DOCUMENTED, live.** `05_setup.tex:64`; spec `:528` |
| The graph could in principle let a visit vector absorb the NEXT visit's category; this was screened | **DOCUMENTED, live, with numbers.** `05_setup.tex:70` (fourth ground): reference encoder $0.4090$/$0.4074$ standardized/raw at Florida, residual variant $0.4197$/$0.4182$, the disqualified attention encoder $0.4976$/$0.4863$. Appendix D restates the two quantities and warns against conflating them (`apx_d_ceiling.tex:35-46`) |
| Per-visit vectors separate categories very strongly (silhouette ≈ 0.57, purity ≈ 0.98) | **DOCUMENTED, live.** `06_results.tex:20` |
| The transductive whole-graph channel was measured and is ≈ 0 | **DOCUMENTED.** `docs/studies/pre_freeze_gates/A4_RESULTS.md` — reg AL −0.33 pp, AZ +0.01, FL −0.12; cat AL +0.29 pp on the in-coverage POI proxy (66.8% of val rows at AL); spec §11.2 `:539-548` restates the bounds and the coverage caveat (67–87%) |
| **"Encoding the current category is desirable, because next-category prediction benefits from knowing the current one"** | **NEW CLAIM — needs sign-off (C2).** Nowhere in any `.tex`. It is a *rationale*, not a measurement; nothing in the repository isolates the contribution of the current-category channel to next-category accuracy. Defensible as a design statement, not as a result |
| **"Static category classification would be degenerate under a check-in-level representation, which is why the task pair changed"** | **NEW CLAIM — needs sign-off (C2).** The two halves it rests on are each documented (purity ≈ 0.98 at `06_results.tex:20`; the lookup-degeneracy argument at `apx_b_static_scope.tex:39-45`), but **the inference joining them appears nowhere**, and `apx_b_static_scope.tex:83-85` currently says the *opposite-facing* thing: "Chapter~\ref{ch:mobiwac} does not inherit the problem ... its input is a single visit, and the identity described above does not arise." That is true of the *fine-class lookup* identity specifically; it would read badly beside a new sentence saying the static task would be degenerate for a *different* reason. Both passages have to be written in one pass, or neither |
| **"These two tasks carry more weight in the literature than POI classification"** (the author's other stated reason in item 7) | **NEW CLAIM, and OUT OF THIS TRACK'S SCOPE.** It is a literature claim, not a repository claim, so this track's source of record does not reach it. It needs the citation protocol (§1 R1–R3), not a code audit |

**The live sentence the item is about** is `1_introduction.tex:132`: "Under a check-in level
representation, static category classification is a less natural companion task than a second
sequential target, so the final task pair becomes next category and next region." (Note: it is in
Chapter 1, not Chapter 2 — the author's item does not say which file, and it appears exactly once in
the whole `src/` tree; filtered `grep -i 'companion'` over every `.tex` returns that one line.)
"Less natural" is currently doing the work of an argument the repository can support much more
concretely.

**Disposition: I_DECIDE.** Two C2 claims, one of which requires a coordinated touch to
`apx_b_static_scope.tex:83-85`, plus a literature claim this track cannot adjudicate.

---

## [VERIFY] list

- **[VERIFY-19.1]** The `le_lambda=1e-8` category↔fclass term was in force for the **shipped**
  POI2Vec tables. I established the default (`poi2vec.py:552`) and that the two production callers
  (`pipelines/embedding/hgi.pipe.py:143`, `scripts/substrate_protocol_cleanup/run_poi2vec.py:38`) do
  not override it. I did **not** find a run log recording the value actually used for the frozen
  per-state CSVs. Closing it needs the build log for
  `output/hgi/<state>/poi2vec_poi_embeddings_<State>.csv`.
- **[VERIFY-19.2]** Ch.3's DGI: I confirmed the objective is unsupervised BCE and that the
  supervised `GCNClassification` is never instantiated in the main repo or in the CoUrb copy. I did
  **not** check the CBIC-era codebase as it stood at publication; the CBIC split protocol carries the
  same standing caveat in GLOSSARY §3 ("verify from the CBIC codebase before asserting it in prose").
- **[VERIFY-20.1]** Whether `feng2017poi2vec` in `articles/dissertacao/src/references.bib:153` was
  verified against the source of record for the CoUrb citation at `4_courb/related.tex:16`. Out of
  this track's scope (repository is my source of record); flagged because item 20 may add a second
  use of that key, and R1 requires the check before it does.
- **[VERIFY-22.1]** Whether Eq. (2.1) should name the two auxiliary terms. This is the drafting
  agent's own open flag at `2_fundamentals.tex:648-652`. **The factual half is now answered** —
  `--mae-poi-lambda 0.3 --anchor-lambda 0.1` are ON in the shipped v14 build
  (`scripts/probe/build_design_k_delaunay.py:279-284`; spec `:347-356`, `:620-641`). What remains is
  the author's editorial decision, not a fact.
- **[VERIFY-24.1]** The author's "correlação" between the semantic and spatial streams. **No
  measurement exists** in the repository and I did not compute one. The spec supports a *structural*
  dependence (shared forward values to the canonical POI pool, one-way via `detach()`, spec
  `:215-222`, `:657`), not a quantity. Prose must either use the mechanism or hedge.
- **[VERIFY-7.1]** No experiment isolates how much the current-category channel contributes to
  next-category accuracy. The A4 audit measures the *transductive* channel, not this one; the
  Ch.5 fourth ground screens the *next*-category channel, not the current one. The author's "deve
  vazar" is therefore a design rationale with no measurement behind it.
- **[VERIFY-7.2]** The literature-weight argument in item 7's first half ("essas outras duas tarefas
  possuem mais força na literatura que a classificação de POI") is a citation claim and was not
  audited here.

## Cross-item overlaps

- **19 ↔ 22 (A3, A5, A11) ↔ 20.** One defect with three surfaces: Eq. (2.1) is presented as the
  complete objective, which licenses two "without task labels" sentences, and the omitted fifth term
  is the POI2Vec anchor that item 20 asks about. **These four should be edited in one pass or the
  fixes will contradict each other.**
- **19 ↔ 7.** Both turn on the current-vs-future category distinction. Item 19 is about what the
  *chapter claims*; item 7 is about what the *design intends*. Same fact base, opposite direction.
- **7 ↔ Appendix B.** A new "static task would be degenerate at the check-in level" claim collides
  with `apx_b_static_scope.tex:83-85` as currently worded.
- **24 ↔ Ch.2 §2.1.** `2_fundamentals.tex:232-234` already states the two streams correctly (semantic
  = per-visit vector, spatial = the visit's region node vector). The §2.2.4 sentence at `:679-680`
  should not re-derive it; it should point back.

## Budget and coverage

Roughly 40 inspection commands across five items (item 19 was the largest share), inside the 20-per-
item cap, well inside the 60-minute box. Nothing was left undug for budget reasons; every open
question above is open because the evidence does not exist in the repository, not because I stopped.


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
