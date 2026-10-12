# GLOSSARY.md — the dissertation's term registry (v1, 2026-07-18)

> **What this is.** The single registry of every technical term, name, and symbol the
> dissertation uses — [`WRITING_LAW.md`](WRITING_LAW.md) states the *rules* (one name per
> concept, gloss at first use); THIS file holds the *names themselves*. It is the consistency
> artifact AGENT_GUARDRAILS L2 requires: agents lint their prose against this registry instead
> of trusting memory of earlier chapters.
>
> **Maintenance rule (fail-closed):** a term not in this registry may not be used in
> dissertation prose. Agents PROPOSE new entries in their handoff notes; the author approves;
> the entry lands here BEFORE the term lands in text. When a definition here conflicts with a
> source paper's local usage, the chapter keeps the paper's usage and the frame uses this
> registry (the per-paper mapping in §2 bridges them).

---

## 1 · The tasks (keep the three distinct; say "we do not predict the exact next place" once, early)

| Term | Definition (gloss at first use) | Notes |
|---|---|---|
| **next-category prediction** (next category) | Given a user's recent check-in sequence, predict the **category** of the next visited POI (7 top-level classes). | Present in all three papers. Hyphenate as compound adjective only. |
| **next-region prediction** (next region) | Given the recent sequence, predict the **region** of the next check-in among the dataset's regions (a census tract in the U.S. states; a mahalle in Istanbul). | Introduced in MobiWac (Ch.5). Never "area", never "cell". |
| **next-place prediction** (next place) | Predicting the exact next POI. **Out of scope for this dissertation** — named only to delimit. | Never conflate with the two above. |
| **category classification** | Static task: classify a POI's category from its representation (no sequence). | CBIC/CoUrb task A. |

**Per-paper task mapping (the bridge the frame must state once):**

| Paper | Paper's own term | Canonical term here |
|---|---|---|
| CBIC | "next-POI prediction" / "next-POI category prediction" (task B) | **next-category prediction** (the label is the next POI's category) |
| CBIC | "POI category classification" (task A) | **category classification** |
| CoUrb | "previsão do próximo POI" (categoria) | **next-category prediction** |
| MobiWac | "next category" + "next region" | identical — no mapping needed |

### 1.1 · Formal notation for the frame chapters

| Symbol | Definition | Notes |
|---|---|---|
| $\mathcal{U}$, $\mathcal{P}$, $\mathcal{C}$, $\mathcal{R}$ | Sets of users, POIs, category classes, and region classes. | Ch.2 notation block. |
| $x_i=(u,p_i,t_i,c_i,r_i)$ | The $i$th check-in of user $u$: visited POI, timestamp, category, and region. | A category or region may be used as a target rather than as an observed input. |
| $H_i=(x_{i-\ell},\ldots,x_{i-1})$ | The ordered history of length $\ell$ preceding check-in $x_i$. | Sequential-task input. |
<!-- [2026-08-12] The symbol row for the elapsed-time quantities was removed with the formal
definition it registered (Section 2.2.3.2): the chapter defines task and method concepts, not
feature encodings, and the category indicators and cyclic time values beside them carry no symbol
either. The TERM row below stays registered, because the prose still uses "elapsed time", and the
exact composition and width live in the Check2HGI and joint-model appendix. Removing the
definition also returns Section 2.3's four definitions to 2.10 through 2.13, so the rows citing
Definition 2.4 and Definition 2.9 are unaffected. -->
| $\mathbf{e}_p$ | The learned representation of POI $p$. | Static-task input; distinct from a per-visit Check2HGI vector. |
| $g_{\mathrm{cat}}(\mathbf{e}_p)$ | Static category classifier whose target is the category $c_p$ of POI $p$. | At evaluation, $p$ is held out from the classifier-training fold. |
| $f_{\mathrm{cat}}(H_i)$, $f_{\mathrm{reg}}(H_i)$ | Sequential predictors whose targets are the next category $c_i$ and next region $r_i$. | The two outputs of the final joint model. |
| $\mathbf{e}_{x_i}$ | The learned representation of check-in $x_i$. | The check-in-level counterpart of $\mathbf{e}_p$: same shape, and the subscript is the point, since it indexes a visit rather than a place. Two visits to one POI may carry different vectors. Definition 2.4. |
| $f_{\mathrm{place}}(H_i)$ | Next-place prediction: maps a check-in history to the next visited POI. | Registered so the excluded task is formally distinct rather than the only one described in prose. **This dissertation does not predict next place;** the row names what is out of scope. Definition 2.9. |
| $\rho$ | A representation map: assigns to each check-in $x_i$ a vector $\rho(x_i) \in \mathbb{R}^{d}$, extended elementwise to histories, $\rho(H_i) = (\rho(x_{i-\ell}), \ldots, \rho(x_{i-1}))$. | Every model of the SEQUENTIAL tasks reads $\rho(H_i)$ rather than $H_i$ itself; the static task reads $\mathbf{e}_p$ directly. The three studies hold the task definitions fixed and vary $\rho$, which is what makes the dissertation's central claim expressible. |
| $d$ | The representation dimension: the codomain dimension of $\rho$. | Kept generic in the definition and instantiated per chapter: $64$ in Chapter 3 (`3_cbic/method.tex` (*"64-dimensional DGI embedding"*)), $192$ in Chapter 4 (the concatenation of three encoders, `4_courb/methodology.tex` (a instanciacao de $d$ no canal sequencial)), and $64$ per check-in in Chapter 5 (`5_mobiwac/04_method.tex` (*"never sees the next category or the next region"*)). **This letter is NOT free, and the row is scoped for that reason.** $d$ unsubscripted means the dimension of $\rho$ and nothing else. Two subscripted uses are already live and keep their meanings: $d_{ij}$ is the **geodesic distance** between two POIs in the Delaunay edge weight (`3_cbic/method.tex` (a ponderacao por decaimento logaritmico da distancia geodesica), four uses across Chapters 3 and 4), and $d_{\mathrm{shared}}$ is the **width of the shared trunk** (`3_cbic/method.tex` (*"Input features for POI Category Classification"*), `4_courb/methodology.tex` (a instanciacao de $d$ no canal categorico e no sequencial), three uses, $256$ where stated). Neither is an instance of this row. |

## 2 · Model and artifact lineage (the table Ch.2 renders; one name per artifact, everywhere)

| Name | What it is | Introduced | Dissertation chapter |
|---|---|---|---|
| **DGI** | Deep Graph Infomax — self-supervised graph representation learning; here: 64-d POI embeddings from a Delaunay POI graph (one-hot category features, distance-decay edge weights). | Veličković et al.; used as input in CBIC | Ch.2 (defined), Ch.3 (used) |
| **HGI** | Hierarchical Graph Infomax — hierarchical place→region→city embeddings; the standard place-level baseline representation. | prior work; baseline in MobiWac Part 1 | Ch.2, Ch.5 |
| **MTLnet** | The joint architecture of the CBIC paper: task-specific MLP encoders → FiLM modulation → shared residual trunk → task heads (category ensemble; Transformer next-head). **Canonical spelling: `MTLnet`, lowercase `n`** (author decision 2026-07-26). The published CoUrb paper typesets it `MTLNet`; Ch.4 was normalized to `MTLnet` and the departure is listed in Appendix B. Never `MTLNet`, `MTL-Net`, or `MtlNet` in dissertation prose. | CBIC (Vitor) | Ch.3 (introduced), recapped Ch.4/Ch.5 related work |
| **FiLM** | Feature-wise Linear Modulation — per-task learned γ/β scaling that conditions shared layers on task identity. | Perez et al.; used in MTLnet | Ch.2 or Ch.3 (gloss once) |
| **Nash-MTL** | Gradient-balancing MTL optimizer (Nash bargaining over task gradients); used in CBIC/CoUrb. | Navon et al. | Ch.3/Ch.4; the frame does NOT amplify its benefit claims (NORTH_STAR §4 caveat) |
| **ST-MTLNet** | CoUrb's variant: MTLnet unchanged, input replaced by concatenated spatial + temporal + categorical encoders (64-d each → 192-d). **Canonical spelling: `ST-MTLNet`, capital `N`** — a separate registered name, not the MTLnet rule with a prefix; it is the published title of the CoUrb paper and keeps that form. The expansion is *Spatial-Temporal MTLNet*, also as published. | CoUrb (Tarik 1st author) | Ch.4 |
| **SIREN / Sphere2Vec-M** | The two spatial encoders compared in CoUrb (sinusoidal MLP on normalized coordinates; multi-scale spherical encoder). | CoUrb | Ch.4 only |
| **Time2Vec** | The temporal encoder (hour-of-day + day-of-week) in CoUrb. | Kazemi et al.; CoUrb | Ch.4 only |
| **Check2HGI** | **Our check-in-level representation**: extends the place→region→city hierarchy with a fourth check-in level, trained without task labels (hierarchical graph infomax); yields one vector per **visit** (semantic set) plus region vectors (spatial set). | MobiWac (Vitor) | Ch.5 (the centerpiece); gloss = "each visit gets its own vector" |
| **the joint model** (MobiWac) | One multitask model, one forward pass, two predictions: private per-task encoders → shared cross-attention trunk → category output (trunk) + region output (trunk + private spatial path). | MobiWac | Ch.5. In prose: "the joint model"; repo id `mtlnet_crossattn_dualtower` NEVER appears in text |
| **dedicated single-task model** | The comparison arm: one model trained for one task (the "ceiling" the joint model is measured against). | all papers | everywhere; never bare "baseline" |
| **the shared trunk** | The shared middle of the joint model, introduced once as "a shared cross-attention stack (the trunk)". | MobiWac GLOSSARY ruling | Ch.5 + frame |
| **label-history benchmark** (next category) | The best macro-F1 reached by four specified predictors that read only the genuine category history of the input window, with no representation read: persistence, and a balanced logistic model on the last category, on window category counts, and on positional one-hots. A property of the label sequence, NOT of any encoder. Measured: FL 0.3617, AL 0.2800, AZ 0.3232, CA 0.3242, IST 0.3016 (Appendix D). **It is NOT an upper bound:** the four predictors are a specified set, and a better predictor of the same restricted information could exceed them. Say so once, at first use. | this document, 2026-07-26; renamed 2026-07-27 | Ch.5 + Appendix D. Two quantities that must NOT be swapped: this one, and the **clean reference encoder** below, which is what the screen actually gates on |
| ~~**label-only ceiling**~~ | **RETIRED 2026-07-27** (author decision). Superseded by **label-history benchmark**, above. The quantity is unchanged; only its name is. It was never an upper bound, so "ceiling" overstated it. Do not reintroduce "ceiling", "autocorrelation ceiling", or "what the past itself allows" for this quantity. | — | The word *ceiling* stays correct for the **dedicated single-task model** row of this table, a different quantity: the score of a real trained model |
| **clean reference encoder** | The encoder a screened candidate is compared against in the leak-sniff screen (at Florida, our own graph encoder at 0.4090 standardized / 0.4074 raw). The screen's verdicts are relative to it, with a three-point margin. It scores ABOVE the label-history benchmark and is not the same quantity. | MobiWac screening record | Ch.5 + Appendix D; never call this "the ceiling" |
| **POI Encoder** | Chapter 4's name for the first phase of its categorical channel: a separately trained encoder that produces the 64-dimensional category embedding $\mathbf{E}_{\text{POI\_category}}$ over a Delaunay graph of the POIs, with edges weighted by logarithmic decay of the Haversine distance and penalized across county boundaries (GEOIDs). | **Ch. 4 vocabulary only** — it is the delivered chapter's own subsection name; never use it for the Ch. 3 or Ch. 5 encoders. `src/chapters/4_courb/methodology.tex` (`\subsubsection{POI Encoder}`). Registered 2026-08-24 |
| **`stream`** (e a nota sobre **`tower`**) | 🛑 **`stream`: NÃO USAR em prosa nova.** Autorizado pela `AUT-14` (26/08) e **revogado pelo autor em 27/08**: *"não é para entrar, isso causa confusão no leitor e na plateia; vamos usar um nome padronizado."* **O nome padronizado é o NOME DA TAREFA** — `next category` / `next region`, já registrado na §1. ✅ **`tower`: LIBERADO na Série B, quando o slide citar o Apêndice E.** Ver a correção ao lado. | ⚠ **O volume entregue MANTÉM `semantic stream` / `spatial stream`** (`5_mobiwac/04_method.tex`, `06_results.tex`, legenda da Fig. 2, e `6_conclusion.tex` (*"calls for an equal-dimension control"*)). **Isto é texto entregue e não muda.** A proibição governa **prosa nova**. Ao apontar para a Figura 2, nomeie o rótulo dela uma vez e siga com o nome da tarefa. 🔴 **CORREÇÃO 27/08 — a revogação de `tower` era MINHA, não do autor.** Ele nomeou `stream` (*"sobre o stram ter entrando no glossary"*); eu estendi ao par porque a `AUT-14` os autorizara juntos. **`tower` é termo do VOLUME**: usado 10+ vezes no Apêndice E (`apx_h_check2hgi_joint_model.tex` (a rota privada da cabeca de regiao e a nota de escopo)) e **em nenhum outro lugar do volume**. O volume tem um **corte de registro deliberado**: a prosa do Cap. 5 diz `private spatial path` (7 ocorrências), o apêndice de implementação diz `private tower` / `shared-context tower`. **O deck espelha isso corretamente** — trilha principal `private spatial path`, `B7-5` `tower` com *"Apêndice E, pp. 115-116"* impresso no rodapé. **Tirar `tower` de lá faria o slide divergir da página que ele cita**, e não há substituto no volume: `route` é palavra do slide, não do documento. Diferença de `stream`, que tinha substituto (o nome da tarefa) |
| **`route`** (Cap. 5 / Apêndice E) | As duas entradas da cabeça de região: a **private route**, que lê o histórico bruto $9\times64$, e a **shared-context route**, que lê a sequência $9\times256$ da atenção cruzada. Cada uma devolve um vetor de 128 dimensões, fundidas por $\mathbf{f}_R=\mathbf{f}_{priv}+\beta W\mathbf{f}_{shr}$. | MobiWac | ✅ **Vocabulário do volume**, não novo: `route`/`routes` aparecem **7×** no Apêndice E — o par em `apx_h:318` (*"The region head deliberately keeps two routes"*) e o membro em `apx_h:274` (*"a complete **private route** from the raw region history"*). ⚠ **O mesmo componente tem TRÊS nomes no volume**: `private spatial path` na prosa do Cap. 5 (7×), `private tower` na prosa do Apêndice E (10×), `private route` na legenda da figura. **Na trilha principal use `private spatial path`; na Série B que cita o Apêndice E, use `route`** — mantém o par que o slide contrasta e concorda com a própria legenda do slide |
| **cross-attention stack** | The shared trunk of the Chapter 5 joint model: **two blocks** in which attention lets each task read the other's representation, so each prediction still uses both inputs. It is what the private per-task encoders feed into, and it is distinct from the private spatial path that feeds the region output only. | The compound is the delivered surface; **the shared trunk** and **cross-attention** are already registered above. Never call it "hard parameter sharing" — that is the Ch. 3 topology. `src/chapters/5_mobiwac/01_introduction.tex` (*"in a single forward pass, with a shared trunk"*) e `04_method.tex` (*"one forward pass whose one set of inputs produces both answers at once"*). Registered 2026-08-24 |

## 3 · Data and protocol terms

| Term | Definition | Notes |
|---|---|---|
| **check-in** | One visit record (user, POI, timestamp) from an LBSN. | never "event" |
| **POI / place** | Point of Interest — a place a person can visit. | expand POI at first use; never "venue". **Hyphenation (settled, round 14):** open as a noun ("a point of interest", and the `siglas` expansion "Point of Interest"); hyphenated only attributively before the noun it modifies ("point-of-interest prediction"). This is WRITING_LAW §1's compound-adjective rule and APA's; both forms in the document are correct and neither is a drift to "standardize". Audited round 14: all 10 in-text uses conform, zero attributive uses left open. The `Multi-Task` in the CBIC and MobiWac chapter prefaces is a verbatim published title and stays. |
| **region** | The spatial prediction unit: a census tract (U.S.); a mahalle (Istanbul). | name the unit at first use |
| **Gowalla** | Public LBSN dataset (2009–2010 check-ins); we use five U.S. states: AL, AZ, FL, CA, TX. | vintage stated in limitations |
| **Istanbul (Massive-STEPS)** | The non-U.S. dataset (Ch.5): Istanbul check-ins from the Massive-STEPS benchmark, mapped to the 7-category taxonomy. | |
| **the 7-category taxonomy** | Community, Entertainment, Food, Nightlife, Outdoors, Shopping, Travel. | identical across chapters |
| **fold** | One of the five data splits of cross-validation. | gloss via "5-fold cross-validation" once |
| **seed** | One complete repetition of the five-fold experiment. A seed sets the random initialization **and** the fold partition, so each seed draws its own division of the users; within one seed the compared models read the same folds. | abstract/intro say "random initialization"; banned: "run", "multi-seed run", and "same folds" as a property **across** seeds (it holds only within a seed) |
| **user-disjoint split** | CV where a user's data never spans train and test (StratifiedGroupKFold by user) — Ch.5's protocol. | Ch.4 used sample-stratified splits — VERIFIED firsthand 2026-07-23 from the CoUrb codebase (plain StratifiedKFold, userid dropped; NORTH_STAR §4 Ch.4 has file/line); the frame states the difference plainly. Ch.3's split: same pipeline family, but verify from the CBIC codebase before asserting it in prose |
| **sliding windows** | Overlapping windows of the last 9 visits, one starting at each visit (stride 1) — Ch.5. | Ch.3/Ch.4 used non-overlapping windows; "sliding" is the ONE name (MobiWac ruling) |
| **transductive** | The representation was trained seeing all places (not new-place-generalizing). | gloss only where the leak discussion needs it |
| **leakage audit** | The controlled test (A4) verifying the transductive representation does not leak labels across the user-disjoint split (null: ≤0.33 pp region, ≤0.29 pp category). | Ch.5 §5.2 material |
| **bilinear discriminator** | The scoring function inside an infomax objective: it maps a pair of embeddings to a compatibility score through a learned weight matrix, $\mathcal{D}(\mathbf{e}_1,\mathbf{e}_2)=\sigma(\mathbf{e}_1^{\top}\mathbf{W}\mathbf{e}_2)$. Bilinear because it is linear in each argument separately. | Ch.2's Check2HGI equations. Registered 2026-07-28 to clear the fail-closed block the drafting agent recorded at `2_fundamentals.tex` (o bloco *fail-closed* que o agente de redacao registou sobre o discriminador bilinear). Ch.3 already uses the bare word "discriminator" in published prose, so only the modifier is new |
| **Delaunay triangulation** (PT: *triangulação de Delaunay*) | The spatial graph the three infomax representations are built on: places are the vertices, and the triangulation joins nearby ones. **The construction is shared; the edge weights are not** — Ch. 3 weights by logarithmic decay of the geodesic distance (`3_cbic/method.tex` (a ponderacao por decaimento logaritmico da distancia geodesica)), Ch. 4 by logarithmic decay of the Haversine distance with a county-boundary penalty (`4_courb/methodology.tex` (o decaimento logaritmico da Haversine com penalizacao de fronteira)), and the delivered Ch. 5 prose says only that "nearby places are linked at the place level", the name appearing in Appendix E of the **main volume** (`apx_h_check2hgi_joint_model.tex` (*"A Delaunay triangulation connects nearby"*)). Never assert that the three graphs are the same object. | Already live in the delivered prose of Chs. 3 and 4 and in Ch. 2 (`2_fundamentals.tex` (*"one graph convolution layer over a Delaunay"*)), and already printed on four deck slides without a registry line. Registered 2026-08-25 by the author, to regularize those and to license one shared line in the fundamentals slide |
| **mutual information** (PT: *informação mútua*) | The quantity an infomax objective maximizes: how much one representation tells about another. In HGI and Check2HGI the two are representations at **two adjacent levels** of the hierarchy. ⚠ **It is never evaluated in closed form** — the training loss is the score of a discriminator on a true pairing against a corrupted one, which is an estimator of the quantity, not the quantity itself. Say "infomax names what is maximized; the pairing test is how it is estimated"; never say the loss *is* the mutual information. | Already in the delivered prose (`2_fundamentals.tex` (a frase *"Training raises the mutual information"*), and the estimator literature at `:420`), but never registered. Registered 2026-08-25 by the author, after he caught the deck labelling the contrastive estimator as the infomax idea |
| **logistic function** | $\sigma(z)=1/(1+e^{-z})$, which maps a real score to the interval between 0 and 1. | Ch.2, naming $\sigma$ in the discriminator equation. Say "logistic function", never "sigmoid", in prose |
| **fine class** | The fine-grained class label attached to each place by the source data, one level below the 7-category taxonomy (Airport, Coffee Shop, Seafood): 284 to 365 distinct values per state, each mapping to exactly one top-level category. | Appendix B §B.5 only, where the static-task scope needs it. In code this column is `spot`, renamed `fclass` at `hgi/preprocess.py` (o campo `fclass`); NEVER write `fclass` in prose |
| **early stopping** | Halting training when a validation metric stops improving, instead of running the configured epoch budget to the end. | Used only to say a chapter did NOT use it. **Ch.3 and Ch.4** run the full budget and read *each task at its own best validation epoch* (per-task diagnostic-best). **Ch.5 also runs the full budget** but reads *both tasks at the one saved model per fold* — the **joint-best convention** below. Do not state the Ch.3/Ch.4 reading rule as if it covered Ch.5: that conflation is exactly what N5 forbids. Gloss at first use |
| **bottleneck** | The one factor limiting performance at a given stage: the input representation in Ch.4's diagnosis, not the sharing scheme. | Registered 2026-07-28 because the PT Resumo needs an anchor for *gargalo*. Never a metaphor for anything else |

## 4 · Metrics, statistics, conventions

| Term | Definition (defensive form: formula + plain reading + boundary) | Notes |
|---|---|---|
| **macro-F1** | Mean of per-category F1; counts every category equally, so rare ones matter. Out of 100. | category metric everywhere |
| **Acc@10** | Share of test check-ins whose true next region is among the model's top-10 predictions. | region metric (Ch.5) |
| **OOD-discounted Acc@10** | Acc@10 on in-distribution samples × (1 − out-of-distribution fraction) — regions unseen in training count as misses. | the "full" region metric of the MobiWac cells; define once in Ch.5 |
| **paired superiority test** | Paired *t* on the four per-seed means (inferential unit: n = 4, three degrees of freedom), with the 90 % confidence interval and Holm correction; this is the reported test. The plan had registered a per-fold Wilcoxon signed-rank over the 20 fitted models (n = 20); the text does not report it (author ruling 2026-09-02: the promise was removed rather than the test computed). Verdict verb: **"outperforms"**, licensed only where the test survives Holm correction within its task family: **next region at Texas and California, next category at Florida**. | verbs bound to tests (WRITING_LAW §3). At n = 4 the exact one-sided Wilcoxon floors at 0.0625 whatever the effect size, which is why the *t* carries the verdict; both footings and the departure are logged in `docs/studies/closing_data/log.md` D-1 to D-3 |
| **TOST non-inferiority** | Two one-sided tests within the **two-point margin**, registered for the **region axis** before any result was read. Readable surface, and the phrase the prose actually repeats: **"stays within the two-point margin"** (PT: **"permanece dentro da margem de dois pontos"**). The technical name, "statistically non-inferior (TOST)", is glossed once at first use in each language and thereafter used only where the test is being named. | "margin" is reserved for this; representation differences are "gaps". Verdict verb **"matches" is banned** — see the equivalence-bound row |
| **equivalence bound** (derived) | The smallest margin the data support, **read off the interval rather than chosen**: TOST at margin *d* passes at the five percent level exactly when the ninety percent CI for the difference lies inside ±*d*. **One bound per axis; never quote one axis's bound on the other.** Next category, per-dataset 0.334 pp and 0.489 pp simultaneous over the six datasets under Bonferroni, whose surface is **"equivalent to zero within half a point"**. Next region, 1.287 pp and 1.372 pp simultaneous, which is tighter than the registered two-point margin but roughly three times the category bound, so the region surface stays **"within the two-point margin"** and "half a point" is false there. | Because nothing is chosen there is no post-hoc margin to justify and no deviation to log. Quote the derived bound; never invent a margin for a sentence. Appendix F already uses this device ("equivalent to zero within a margin of five hundredths") |
| **equivalent to zero within half a point** | The verdict for the next-category differences. No equivalence margin was pre-registered on that axis, so the margin is not chosen: it is read off the confidence intervals, and two one-sided tests at that margin pass at all six datasets (worst $p = 0.008$), simultaneously under Bonferroni. Surface: **"equivalent to zero within half a point"** (PT: **"equivalente a zero dentro de meio ponto"**). | Never "matches", "empata", "semelhante", "a par", or any bare claim of equality: the phrase is a bounded-magnitude claim, and the bound travels with it. Region keeps its own surface, the two-point margin; never quote one axis's bound on the other |
| **Holm correction** | Multiplicity control across the six per-dataset tests. | cite, don't gloss textbook tests |
| **n = 20** (fitted models) and **n = 4** (inferential unit) | 4 seeds × 5 folds per cell = 20 fitted models. Each seed draws its own fold partition; the compared arms are built from one partition **within** a seed (same splitter call, same seed, same rows: `StratifiedGroupKFold` em `src/data/folds.py` (**codigo do repositorio, nao da dissertacao** — a arvore `src/` da RAIZ, nao a de `articles/dissertacao/src/`), `:1247`), which is what licenses pairing, and the reported tests pair the four per-seed means, so the inferential unit is n = 4. | state the arithmetic once (Ch.5 protocol); never write "n = 20 paired repetitions" for the reported test. Design: `docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md`:18-19 (seeds {0,1,7,100} × 5 folds), :187-190 (**same folds across ARMS**, the pairing condition, not across seeds, and it warns that regenerating folds for one arm silently unpairs the headline); `LANE2_OVERLAP_VALIDATION.md`:75 records partitions NOT bit-identical across arms and gives its reason in its own parenthetical, "(different windowed rows)", so it bears on comparisons consuming different windowings rather than on two models reading one. The within-seed property is code-level, not measured on saved indices. Code path and measurement: `science/fold_partition_and_seeds.md`; executed footings: `.../stats_n20/RESULTS.md`:65-67 |
| **joint-best convention** | Both tasks read at the one saved model per fold (the validation-selected epoch). Ch.5's reported convention. | never mix with per-task diagnostic-best without saying so |
| **the floors** | Reference points: majority-class floor (category), Markov-1 floor (region). | every number carries its reference point |
| **silhouette score** (by category) | Mean silhouette of the vectors, aggregated per place, under the seven category labels: how tight and well separated the seven labeled groups are, on a $-1$ to $1$ scale. Measured with **cosine** distance, averaged over the five U.S. states. Ch. 5 reports about **0.51** for the check-in-level representation against about **0.00** for the place embedding, measured on the delivered build (`docs/results/closing_data/v18/geometry/`; it was 0.57 on the v14 build until 2026-09-30). | **Geometry diagnostic, not a task metric.** The chapter states that both measures *"characterize the representation family rather than the exact configuration"* — never cite it as evidence of prediction performance. `src/chapters/5_mobiwac/06_results.tex` (*"per-visit vectors' silhouette score by category"*). Registered 2026-08-24 |
| **nearest-neighbor category purity** | The share of a vector's nearest neighbors that carry the vector's own category. Measured **leave-one-out, $k = 10$**, averaged over the five U.S. states: about **0.98** for the check-in-level vectors against about **0.78** for the place embedding. | Same boundary as the silhouette row: it characterizes the representation family, not a result of either task. `:39,:87`. Registered 2026-08-24 |
| **Markov-$K$ floor** | Reference point for the **category** axis: a transition table over the training visits that answers with the category that most often follows the recent ones, with the **order $K$ chosen per dataset**. The region analogue is the **Markov-1 floor** over region transitions. | ✅ Author-authorised 2026-08-26 (`AUT-14`). ⚠ **Not a trivial baseline and must never be called one**: $K$ is tuned per dataset, and Ch. 5 names the floor — not the published external systems — as the reference the region task has to clear. Hyphenated as here; **never** "Markov floor" unqualified, which collides with the Markov-1 region floor |
| **linear CKA** (Centered Kernel Alignment) | Similarity between two representations of the same points, invariant to rotation and isotropic scaling: $\operatorname{CKA}_{\mathrm{lin}}(X,Y)=\lVert Y_c^\top X_c\rVert_F^2 / (\lVert X_c^\top X_c\rVert_F\,\lVert Y_c^\top Y_c\rVert_F)$. Unlike the other geometry probes, it compares **two matrices** rather than measuring separability of a label. | ✅ Author-authorised 2026-08-27. 🛑 **SCOPE LIMIT, and it is the reason the term needed authorisation at all: this dissertation never ran it.** It lives only in `wrapup/ESTUDOS_DEFESA.md` §4.5, a study document. **A slide or sentence may explain what linear CKA IS; none may report a CKA value, comparison or conclusion for this work.** Writing one would be inventing evidence |
| **logit adjustment** | A class-prior correction added to the **category** cross-entropy **at training time**: the term $\tau\log P_{\mathrm{train}}(y)$, with $\tau = 0.5$, is added to the logits, shifting the decision boundary toward the balanced posterior that macro-F1 rewards. **Training only — inference uses the unadjusted logits, and the region term is never adjusted.** | **The dedicated category model receives the same adjustment**, so it is not a source of advantage in the joint-versus-dedicated comparison, and saying so is what keeps the comparison clean. `src/chapters/5_mobiwac/04_method.tex` (o paragrafo do `logit adjustment`, junto ao `\cite{menon2021logitadjustment}`); `apx_h_check2hgi_joint_model.tex` (a rota privada da cabeca de regiao e a nota de escopo). Registered 2026-08-24 |
| **controlled ablation** | A comparison that removes or holds one component fixed in order to attribute an effect to it. Ch. 6 uses the term **in the negative**: *"no single controlled ablation separates the representation-and-topology change from the task-pair change in the final result"*, and names Ch. 4 as the fixed-pair control. | Register the delivered surface **"controlled ablation"**, not bare "ablation". PT surface, where one is needed: **"ablação controlada"**. ⚠ Where prose already says "comparação controlada" for a different act (the corpus audit), that is a plain controlled comparison and not this term. `src/chapters/6_conclusion.tex` (a frase *"No single controlled ..."*). Registered 2026-08-24 |
| **technical tie** (Ch. 4 only) | Chapter 4's delivered surface for a per-combination difference too small to separate two arms on its sequential task: *"one additional technical tie in Outdoors in Florida, where the baseline mean exceeds the best variant by **0.02 percentage points**, a gap within one standard deviation."* | ⚠ **Ch. 4 vocabulary only, and never on the Ch. 5 verdict axis**, where `matches` / `empata` / `ties` are banned as verdict verbs (see the *TOST non-inferiority* and *equivalence bound* rows). Registered rather than paraphrased because paraphrasing the chapter on screen is worse than quoting it — the same ruling the author made for `match` in the Ch. 5 protocol slide. **The direction travels with it: MTLnet retains the higher mean, by 0.02 pp.** `src/chapters/4_courb/results.tex` (*"presents a more heterogeneous scenario"*), `conclusion.tex` (o empate tecnico do canal sequencial). Registered 2026-08-24 |

**The four rows below were added 2026-07-30** and close PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02), whose recorded decision is
option (a), register the term. They are multi-objective optimization vocabulary rather than names this
project coined, so each definition is copied from a source read at its PDF that session, named in the
row; nothing here is retyped from another paper's bibliography or from memory. The first three were
already in prose at five live sites (Ch.3 twice in `basis.tex` and once in `method.tex`, Ch.4's
`methodology.tex`, and the Appendix B errata row), which the fail-closed rule of §1 does not permit,
and the fourth was needed before §2.3 could define the quantity Appendix F measures.

| Term | Definition (gloss at first use) | Notes |
|---|---|---|
| **Pareto dominance** | One parameter setting dominates another when it is at least as good on every task loss and strictly better on at least one. | The comparison MTL lacks and single-task learning has: with two losses there is no natural ordering, so most pairs of models are simply incomparable. Definition from `liu2021cagrad` Def. 3.1 (arXiv:2110.14048v2 p4) and `sener2018mgda` Def. 1(a) (arXiv:1810.04650v2 p3); `nash` states it in words at arXiv:2202.01017v2 p2 |
| **Pareto optimality** (Pareto front) | A setting is Pareto optimal when no other setting dominates it. The set of all such settings is the Pareto set, and the set of their loss vectors is the **Pareto front**. | `nash` p2, `sener2018mgda` Def. 1(b) p3. **Not claimed by this dissertation, and claimed by only one of the methods §2.3 names**: `nash` reaches Pareto optimality only under an added convexity assumption (its Theorem 5.5, p6 and p14). Say "Pareto optimality is not claimed here" once, in §2.3, and never write that a balancer attains it |
| **Pareto-stationary point** | A point at which some convex combination of the task gradients is zero. It is a necessary condition for Pareto optimality, not a sufficient one. | `nash` p2 (*"a point is called Pareto stationary if there exists a convex combination of the gradients at this point that equals zero. Pareto stationarity is a necessary condition for Pareto optimality"*), formalized as $\min_{w} \lVert g_w(\theta)\rVert = 0$ over the probability simplex in `liu2021cagrad` Def. 3.1 p4. **Hyphenated, as here.** Ch.3's spelling is the published one (the sentence at `chapters/3_cbic/method.tex` is a verbatim substring of `articles/CBIC___MTL/sections/method.tex`, checked 2026-07-30); Ch.4's is **not published prose** but this dissertation's own errata-corrected sentence, listed in Appendix B, since the published PT source has zero occurrences of the term (`articles/CoUrb_2026/src`, nine `.tex` files). `tables/courb/errata.tex` carries the unhyphenated "Pareto stationary" inside its statement of the guarantee and is left as it stands |
| **gradient conflict** | Two tasks conflict at a point when the cosine of the angle between their per-task gradients is negative; near zero means the two updates are close to orthogonal, so neither reinforces nor opposes the other. | `yu2020pcgrad` Def. 1 (arXiv:2001.06782v4 p3). The quantity the gradient-surgery balancers act on, and the quantity Appendix~D measures on the joint model. Define it in §2.3; **report no value there** (`CONSIDERATIONS.md` work-list item 28). Never call a near-zero cosine "no conflict detected" where the appendix's equivalence test supports the positive statement |

## 5 · Acronym list (seeds the List of Abbreviations; expand each at first use)

LBSN · POI · MTL · STL · CV · DGI · HGI · Check2HGI · FiLM · GRU · OOD ·
TOST · CI (confidence interval) · SGKF (only if the protocol section needs it) ·
CBIC · CoUrb · SBRC · MobiWac · BRACIS (appendix only) · UFV · PPGCC

Keep the count low; method internals (STAN, CTLE, HMT-GRN, ReHDM, POI-RGNN — baseline names)
are named once each in Ch.5's baseline list and the List of Abbreviations only if used ≥3×.

## 6 · Portuguese equivalents (Resumo + AcademicoPG fields + folha de rosto)

| EN (body) | PT (Resumo/system) |
|---|---|
| multitask learning | aprendizado multitarefa |
| single-task / dedicated model | modelo dedicado (tarefa única) |
| point of interest (POI) | ponto de interesse (POI) |
| check-in / visit | check-in / visita |
| check-in-level representation | representação em nível de check-in |
| elapsed-time quantities / elapsed time | tempos decorridos (medidas de tempo decorrido) |
| place embedding | representação (embedding) em nível de POI |
| next-category prediction | previsão da próxima categoria |
| next-region prediction | previsão da próxima região |
| census tract | setor censitário |
| sliding windows | janelas deslizantes |
| cross-validation (5-fold) | validação cruzada (5 partições) |
| random initialization (seed) | inicialização aleatória (semente) |
| non-inferiority (TOST, 2-point margin) | não-inferioridade estatística (TOST, margem de 2 pontos) |
| stays within the two-point margin *(recurring surface)* | permanece dentro da margem de dois pontos |
| registered before any result was read | registrada antes de qualquer resultado ser lido |
| equivalent to zero within half a point *(next-category axis only)* | equivalente a zero dentro de meio ponto *(apenas no eixo da próxima categoria)* |
| equivalent to zero within half a point | equivalente a zero dentro de meio ponto |
<!-- [ERRATA 2026-08-21] A linha anterior era `| outperforms / matches | supera / equipara-se
     (estatisticamente) |`, e oferecia uma traducao para um verbo que ESTE MESMO arquivo bane em
     duas linhas (§4 "Verdict verb 'matches' is banned"; "Never 'matches', 'empata', 'semelhante',
     'a par'") e que o WRITING_LAW §3 bane em :226. "equipara-se" e semanticamente a familia
     banida. O defeito era acionavel: um redator de slides em portugues que consultasse esta
     tabela de equivalentes encontraria o termo proibido e o usaria de boa-fe. Achado na
     preparacao da apresentacao de defesa. As duas superficies corretas ja estavam registradas
     tres linhas acima; a linha agora aponta para elas em vez de competir com elas. -->
| outperforms *(licensed only where the test survives Holm)* | supera |
| ~~matches~~ — **BANNED VERB, no PT equivalent is offered** | *(use a superfície do eixo: região → "permanece dentro da margem de dois pontos"; categoria → "equivalente a zero dentro de meio ponto")* |
| external baseline | método externo usado como referência |
| leakage audit | auditoria de vazamento |
| shared trunk | tronco compartilhado |
| n = 20 (fitted models) | vinte modelos ajustados (por configuração) |
| user-disjoint split | usuários disjuntos entre treino e teste |
| fold (one of five) | partição (uma de cinco); *as cinco* partições fixas |
| per-seed mean(s) | média por inicialização; *plural* médias por inicialização |
| joint-best convention | seleção *joint-best* |
| cross-attention trunk | tronco de atenção cruzada |
| decomposed encoders (spatial, temporal, categorical) | codificadores decompostos (espacial, temporal, categórico) |
| hard parameter sharing | compartilhamento rígido de parâmetros |
| soft parameter sharing | compartilhamento flexível de parâmetros |
| negative transfer | transferência negativa |
| sharing topology | topologia de compartilhamento |
| bottleneck | gargalo |
| paired superiority test | teste pareado; *plural* testes pareados |
| Pareto optimality (Pareto front) | otimalidade de Pareto (fronteira de Pareto) |
| Pareto dominance | dominância de Pareto |
| Pareto-stationary point | ponto Pareto-estacionário |
| gradient conflict | conflito de gradientes |

The Resumo mirrors the Abstract claim-for-claim (WRITING_LAW §6); this table keeps the pair
translation-stable. "Embedding" may stay as a loanword in PT (standard in the BR community)
with "representação" as the running word.

**The last nine rows were added 2026-07-28**, after the Resumo was cut and rebuilt. Each was already
in use in the Resumo and none was registered, which the fail-closed rule (§1) does not permit. Before
adding each row I confirmed its English counterpart is itself registered above: `n = 20 (fitted
models)` §4, `user-disjoint split` §3, `fold` and `seed` §3, `joint-best convention` §4,
`cross-attention trunk` in **the joint model** §2, `the shared trunk` §2. Three had no English row of
their own and are ordinary MTL vocabulary rather than names this project coined, so they are
registered here as translation pairs only: decomposed encoders, hard parameter sharing, sharing
topology.

**Two rows added 2026-08-03 on the author's authorization: `soft parameter sharing` and `negative
transfer`.** They belong to the same class as `hard parameter sharing` above, ordinary MTL vocabulary
rather than names this project coined, and they are registered as translation pairs only. The reason to
record why they arrived late: **both were already in the live prose of Chapter 2 before they were
registered**, while §6 carried only `hard parameter sharing`. The fail-closed rule was therefore already
stretched, and converting that prose into numbered definition blocks (round 10, GER-08/GER-10) neither
widened nor caused the gap; it made it visible. A registry row is the author's alone to add, so the terms
were reported as owed rather than registered by an agent, and they entered when he authorized them.

Two notes on the choices, since a later translator will second-guess them:

- **`seleção joint-best` keeps the English term of art.** It names a selection rule this document
  defines (§4, "joint-best convention"), it appears in the results tables in English, and inventing a
  Portuguese calque would make the Resumo and the tables disagree. The Resumo italicizes it, which is
  the BR convention for a retained foreign term.
**The four Pareto rows were added 2026-07-30** with their English counterparts in §4, and one of the
four PT strings is attested in this repository while three are not. `otimalidade de Pareto` is the
author's own wording (`src_utils/PENDENCIAS.md`:98) and the advisor's
(`articles/[mobiwac]/REVIEW_GERMANO.md`:778), so it is settled. `dominância de Pareto`, `ponto
Pareto-estacionário` and `conflito de gradientes` are the standard renderings but appear nowhere in
this repository, in the published PT paper (`articles/CoUrb_2026/src`, nine `.tex` files, zero
occurrences of "pareto"), or in any Portuguese surface of the dissertation. They are therefore
**proposed, not settled**, and PENDENCIAS_RESOLVIDOS 2.12 (arquivado 2026-08-02) asks the author to confirm or replace them. No PT
surface uses any of the four today: the terms live in Chapter 2, which is English, and the Resumo does
not mention them. The rows exist because §6 is this registry's convention for every registered term,
so a later translator finds a decision rather than a gap.

- **`partição` for `fold`, and `as cinco partições fixas`.** The existing row translates "5-fold
  cross-validation" as "validação cruzada (5 partições)", so `partição` was already the registered
  word for the unit; these rows make the singular and the "fixed across seeds" sense explicit,
  because the Resumo needs to say that the five are the *same* five at every seed.

## 7 · Banned and repo-internal words (pointer)

The ban lists live in [`WRITING_LAW.md`](WRITING_LAW.md) §2 (repo codenames: B9, v11–v17,
champion-G, dk_ovl, log_T, "substrate", "engine", "board", "recipe"…) and §4 (AI-tells). This
registry deliberately contains NO entry for them: if a term is not here and not proposable
under the maintenance rule, it does not exist for this dissertation.
