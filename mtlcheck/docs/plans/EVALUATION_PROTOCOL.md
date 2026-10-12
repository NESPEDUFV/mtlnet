# Protocolo estatístico de avaliação — proposta da pesquisa de 2026-08-17

> **Status: ADOTADO em 2026-08-19.** O conteúdo não muda desde `e1abb759` (18-08 02:52), que
> **precede** a primeira leitura selada (`8fadf2fe`, 18-08 11:40) — a ordem de pré-registro está
> preservada e é verificável no histórico. A linha anterior dizia "PROPOSTA, não adotada" enquanto a
> leitura selada já o tratava como vinculante; um documento que se declara não-adotado e é usado
> como pré-registro é um presente para a banca, e a correção é declarar a adoção com data, não
> reescrever o conteúdo.
>
> Saída de uma pesquisa adversarial (33 agentes, 19 propostas
> sobreviveram a refutação independente, 8 descartadas) sobre a literatura e sobre a variância medida
> deste projeto. Lê-se junto de:
>
> - `docs/future_works/evaluation_protocol_cleanup.md` **no checkout de referência** (`…/mestrado/ingred/`, sha256 `e479c7e00320ee80`) — a auditoria de 454 linhas que originou o trabalho. ⚠ Não rastreada no git; o desenho que importa está transcrito em §12.8;
> - [`../NOMENCLATURE.md`](../NOMENCLATURE.md) — vocabulário obrigatório (repetição ≠ réplica ≠ fold);
> - [`../../studies/porting_validation/GATES_2026-08-17.md`](../../studies/porting_validation/GATES_2026-08-17.md) — os deltas medidos que o protocolo precisa resolver.
>
> **Uma correção que esta pesquisa já produziu e que foi aplicada:** a banda pareada usava
> multiplicador 2,0; com R = 4 repetições o correto é t = 3,182, e isso derrubou um veredito já
> reportado (Arizona/região a 30 épocas). Ver `train/stats.py`.
>
> Antes de adotar: decidir os pontos abertos no fim, e registrar o documento em git ANTES da primeira
> execução confirmatória — a pré-registro é a parte que sustenta a defensibilidade.
>
> **§10 e §11 foram escritas DEPOIS do resto**, contra dois fatos verificados em seguida, e ambas
> emendam o corpo do documento:
>
> - **§10** — cada "seed" gera uma **partição nova**, então o desenho histórico é k-fold CV
>   *repetido* e repetição está confundida com réplica. Muda o `split_seed` congelado de 42 para 0,
>   re-especifica o gate de calibração e acrescenta um fatorial 2×2 de 30 fits.
> - **§11** — o protocolo **tem** conjunto de teste dentro do estado (o fold externo selado, que é a
>   correção central), e **não tem** conjunto externo entre estados. Há **60 estados nunca usados** no
>   corpus; a recomendação é selar um deles como confirmação externa.
>
> Onde §10/§11 contradizem §2–§9, **§10/§11 prevalecem** — elas viram o texto de base na próxima
> revisão.

---

# Statistical Evaluation Protocol — MTL POI Prediction (six datasets)

**Status:** committed and dated BEFORE the first confirmatory fold of any cycle it governs. The pre-registration is the load-bearing part: every margin, selector, hypothesis type, and escalation rule below must be in git before the first confirmatory fold is trained, or the defensibility argument evaporates.

**Substrate:** the sealed 70/10/20 outer-test / inner-val design **transcribed in §12.8**, from `docs/future_works/evaluation_protocol_cleanup.md` in the reference checkout (untracked — see §12.8). This document does not repeat that audit; it completes it. Everything here is post-processing of artifacts that design already mandates, except where a cost is explicitly counted.

---

## 1. The estimand

Per **state × task**, the quantity compared is the **paired delta of the pooled out-of-fold (OOF)
metric**, **marginal over the partition draw** and conditional on the corpus.

**Marginal, not conditional on one partition** — amended 2026-08-25, before any number of the cycle
exists. The earlier wording ("conditional on the frozen user partition") described a design that ran
one partition and four replicates; it made the partition draw part of the object rather than part of
the noise, and a reviewer asking "would this hold under a different draw?" had no answer inside the
interval. Under the marginal definition, each execution is one draw of the whole procedure — both
the partition and the initialisation — and the reported delta is their mean. Adding executions is
therefore a better estimate of the **same** quantity, which is what makes the escalation ladder of §2
an adaptation on a nuisance parameter rather than a change of question (Kieser & Friede 2000; FDA
2019).

The evaluation population is invariant to the draw: every user is scored exactly once under any
partition, so averaging over partitions changes **who trained the model**, never who is measured.
That is the smallest possible change of estimand, and it is why the pairing discipline survives
untouched — all arms share `(split_seed, model_seed)` **within** each execution, so the ~1.2 pp
between-fold component still cancels where it always did.

**Pooled, not averaged.** Per (arm, seed): concatenate the five outer-fold row-level prediction files and compute the metric **once** over all OOF rows. Per-fold values are retained as heterogeneity diagnostics only. Reason: mean-of-fold macro-F1 is a biased estimator under class imbalance — measured at −0.24 pp on the Alabama structure, over half the non-inferiority margin — and no resampling removes a bias (Forman & Scholz 2010, SIGKDD Expl.: pool the counts; Tsamardinos, Greasidou & Borboudakis 2018, *Machine Learning*: inference on pooled OOF predictions). Acc@10 pooling is numerically near-identical to averaging but is pooled anyway for uniformity.

**Category:** macro-F1 = unweighted mean of per-class F1, each computed from pooled per-class TP/FP/FN counts, `zero_division=0`. Convention pinned in print because two non-equivalent "macro-F1" definitions exist (Opitz & Burst 2019, arXiv:1911.03347). Weighted-F1 is refused (it re-weights away the minority classes the training targets); dropping the rarest class is refused (changes the estimand mid-study). A 7-row per-class paired-delta table accompanies every headline delta, labelled descriptive — a macro win carried by one rare class must be visible.

**Region:** **top10_raw** — plain top-10 accuracy over **every** validation row, full per-state region vocabulary — is the single primary estimand for **all** arms. It is deployment-faithful (no train-label bookkeeping exists at inference) and is the definition the external next-POI literature uses (GETNext, STAN protocol), so the paper's numbers stay commensurable with its baselines. Precondition, asserted at scoring time: every compared arm's head covers the identical full vocabulary. The scorer refuses to build any table mixing estimand names or mask provenances. Diagnostics per state × arm: `ood_fraction`, `top10_acc_indist`, `top10_full`, and `ood_hit_rate = (raw − full)/ood_fraction`. The last is a **leak canary**, not a courtesy: a never-trained output unit essentially cannot rank top-10 of 1,109–8,501 classes, so `ood_hit_rate > 1%` fails the run (this guards the stale-log_T failure class already documented at +8–12 pp). MRR is a diagnostic column, never a claim carrier (its chance floor spans 12× across the six states — not catalogue-invariant).

**The joint arm's estimand is the (cat, reg) pair at ONE selector-chosen checkpoint per fitted run.** Selector: `geom_simple = sqrt(cat_macroF1 × reg_Acc@10)`, evaluated on the **inner validation split only**, frozen here with the disclosure that it was adopted on development-state outcomes (C21) and will not be re-tuned. Both reported task metrics are read from that single checkpoint's one-shot outer evaluation. Per-task diagnostic-best epochs appear only in a labelled diagnostic table (they describe two virtual models and would quietly contradict the "one model, one forward" headline). The reported quantity is the procedure "train joint + frozen selector"; each deployment of it produces one model — the paper states this per-run-checkpoint structure explicitly.

**Selection symmetry (mandatory):** STL comparator arms use the identical contract — checkpoint chosen on the same inner-validation users by frozen "best own-task metric", one outer evaluation. No arm in any headline table may use max-over-epochs on the reporting observations; the confirmatory scorer enforces this with a guard for **all** arms (Cawley & Talbot 2010, JMLR: unequal selection intensity confounds the comparison). Each arm is evaluated exactly as it deploys — STL genuinely ships two models with two checkpoints.

---

## 2. The design

Per state, per arm:

| Element | Choice | Justification from measured variance |
|---|---|---|
| Outer folds | 5, user-disjoint StratifiedGroupKFold, `split_seed` **drawn per execution** (§10.1; never 42), `partition_hash` pinned per execution, **fail-closed** if absent | Between-fold spread ~1.2 pp is user-composition variance, common to both arms; pairing on shared frozen folds cancels it. More folds buy nothing pairing doesn't already deliver. |
| Inner val | 10% of users (one fold of an 8-way SGKF on the 80% block), `inner_split_seed` recorded separately | Selection must not touch the outer fold; 10% is viable even at Alabama (audit's simulation: ~160 inner-val users on the smallest input). |
| Refit | **No-refit default** — evaluate the inner-selected checkpoint on the outer fold; declare the estimand as "procedure trained on ~70% of users" | Refit doubles fits for a shift the paired delta mostly cancels; budget goes to seeds/states instead. |
| Checkpoint | Inner-val only; `geom_simple` (joint), best-own-metric (STL); frozen | See §1. |
| Executions | **The escalation ladder of §2a.** One execution = one `(split_seed, model_seed)` pair, **both drawn fresh**, run for every arm of the family | See §2a. There is no fixed count and no seed budget: each dataset measures its own dispersion and buys what it needs. |
| Fits per state per arm | 3–6 executions × 5 folds, decided by the ladder | — |

**Tooling guard:** `stats.py` must refuse to print its 2·SE "separated" band below three
executions (at 1 df the calibrated multiplier is t₀.₉₇₅,₁ = 12.7, not 2.0).

### 2a. The escalation ladder — how many executions a dataset gets

**One execution = one `(split_seed, model_seed)` pair, both drawn fresh, never reused across
executions.** Repeating a model seed across partitions would nail that draw's offset into the mean —
where it never averages away as P grows — and hide it from the observed dispersion. With both knobs
fresh, the executions are i.i.d. draws of the procedure, which is exactly what the marginal estimand
of §1 requires.

**The ladder grows only in executions, and that is algebra, not preference.** With a fixed budget
`N = P·S`, the variance of the mean is `σ²_P/P + σ²_S/(P·S)`. The second term equals `σ²_S/N` —
it depends only on the total and is indifferent to how the budget is sliced. The first shrinks only
by adding partitions. So `P=N, S=1` weakly dominates for **any** ratio of the components, including
`σ_P = 0`. The exception would be a fixed per-partition cost; optimal two-stage allocation gives
`S* ≈ sqrt((cost_partition/cost_fit)·(σ²_S/σ²_P))`, and here a new partition costs one fit — the
substrate does not depend on it — so `S = 1`. The formula is registered rather than the conclusion,
so the rule recomputes itself if that ever changes.

**The gate is measured on the inner validation, which spends no reading.** Dispersion across
executions is computed on the inner split; it decides only **how many executions exist before the
single outer reading**. The published interval comes from the outer deltas per execution, with the
degrees of freedom of the final P. This is what keeps the internal proxy non-load-bearing: if it
under-estimates, the design is under-powered and the final interval comes out wider; if it
over-estimates, GPU is wasted. **Both failure modes cost budget, never the claim** — which is why
the adaptation needs no α-spending (Wittes & Brittain 1990; Kieser & Friede 2000; FDA 2019).

**The gate inflates the observed dispersion to its upper confidence limit** (Browne 1995): sizing a
design from a pilot's point estimate under-powers it with high probability. The one-sided 80 % UCL
factors are 3.95× (1 df), 2.12× (2), 1.73× (3), 1.56× (4). Halt when
`t₀.₉₇₅,P−₁ · UCL₈₀(σ̂) / √P < δ`.

| rung | executions | measures |
|---|---:|---|
| **R0** | 2 | total dispersion, 1 df — **triage only; halting here is forbidden** |
| **R1** | 3 | first printable band (2 df) |
| **R2** | 4 | 3 df |
| **R3** | 6 | 5 df — beyond it the outcome is the stamp, not more GPU |

**R0 never licenses a halt**, and that is an explicit rule rather than an emergent one. The Browne
factor makes it practically impossible, but with observed dispersion of exactly zero the factor
multiplies zero and the projection would fit inside δ. Two identical executions do not demonstrate
low dispersion; they are one sample at one degree of freedom. This is the "no band below three"
guard this protocol already carries, extended to the execution axis.

**Reaching the ceiling without resolving is a declared outcome**: the cell is stamped
**"partition-limited at this margin"** and never reported as resolved. It is not a fifth verdict —
the §3 taxonomy is unchanged.

⚠ **Read that stamp literally: it says "did not resolve at this margin, by the internal proxy".** It
does **not** say the effect is sensitive to the partition. At small datasets the dispersion between
executions on the inner validation is dominated by the sampling noise of the 10 % inner split, not by
the partition draw — a 2026-08-25 simulation puts Alabama at the ceiling in ~61 % of realistic
scenarios for that reason alone, and the published outer band (pooled OOF, every user, no resampling
between executions) will be far narrower than the internal projection. Subtracting the inner-sampling
component is next-cycle work, because it changes a pre-registered rule — and the naive subtraction is
not the way to do it (it collapses to zero, and Browne's factors do not apply to the corrected
statistic). The named corrector and what it needs are in
[`../future_works/escada_mede_o_ruido_do_medidor.md`](../future_works/escada_mede_o_ruido_do_medidor.md).

**How much α this actually costs, measured.** "No α-spending" is the conclusion, not the claim. A
2026-08-25 audit simulated this exact ladder (rungs 2/3/4/6, Browne inflation, floor never halting)
under H0 on the non-inferiority boundary: type I error **2.56 % against 2.5 % nominal** at realistic
parameters, rising to 3.9 % only under an artificial correlation of 1 between the internal proxy and
the outer test. The residual channel is selection — halting early favours samples with a small σ̂ —
and it anti-correlates across datasets: the large ones halt almost deterministically at three
executions (no selection), and the small ones halt variably but with a proxy that is nearly
independent of the outer test. **Report this as "inflation on the order of 0.1 pp of α", with the
simulation, rather than as an unquantified dispensation.**

⚠ **The blindness is load-bearing and must be preserved.** The dispensation holds because the rule
reads only `stdev`. No log line, no intermediate artifact and no status report may carry the *mean*
of the internal deltas before the confirmatory read — `ladder_<state>.json` deliberately stores `sd`,
its upper limit and the projected half-width, and not the deltas themselves.

**Attribution is not part of the ladder.** Splitting the dispersion into partition and replicate
components changes no allocation decision — the next rung is a new execution whichever component
dominates. Attribution exists as an on-demand diagnostic branch (add one replicate inside two
existing partitions of one dataset, analyse the unbalanced design by REML) when a dispersion looks
anomalous and the question is "is this a bug or real sensitivity?".

⚠ **This design is what `NOMENCLATURE.md` §1 calls the confounded one** — partition and
initialisation moving together. The confounding is fatal for **attributing** variance to an axis and
harmless for estimating the **marginal** effect, which is what the headline claims. What was wrong in
the legacy system was the bookkeeping (one field for two factors) and the analysis label ("seed
variance"), not the randomisation. State this before a reviewer finds it.

**What replaced what.** Until 2026-08-24 this section licensed S=2 at the large states against a
replicate band measured on the three smallest datasets and aggregated by the maximum — the "bridge".
It measured the wrong regime, handed the smallest dataset a veto over the largest, aggregated by a
maximum with the known properties of neither a UCL nor a meta-analytic prediction, and has no
published precedent in ML. The reasoning and the literature are in
[`../future_works/banda_da_ponte_transfere.md`](../future_works/banda_da_ponte_transfere.md); the
protocol as it governed the v19 campaign is preserved verbatim in
[`../v19_RECORD.md`](../v19_RECORD.md).

**Persistence contract (this is the engineering item):** every (arm, seed, fold) outer evaluation saves row-level predictions with user ID, fold ID, seed, selected epoch, per-row target rank (or top-k), and the per-fold train-label set. All inference below is post-processing of this table.

---

## 3. Within-state inference

Reduce once to **per-user sufficient statistics**: cat → per-class TP/FP/FN counts per user; reg → per-user (hit@10 count, window count). Each user occupies exactly one outer fold (user-disjoint split), so a resampled user carries one coherent bundle: all windows, both arms, all seeds. Every replicate is then a weighted sum — 10,000 replicates cost seconds.

**Two inference tiers; every published claim names its tier.**

**Tier A — user generalization (primary; backs all headline and margin claims).**
- *Effect + CI:* paired user-cluster bootstrap, ≥10,000 replicates; resample users with replacement, recompute each arm's global metric from summed sufficient statistics, take the paired Δ, average across seeds inside the replicate. Report percentile **and** BCa (delete-one-user jackknife — cheap over sums), flag disagreement. Note Acc@10 pooled over users is a **ratio** of user-sums (Σhits/Σwindows); the free closed-form cross-check is the cluster-robust delta-method SE for a ratio. (Field & Welsh 2007, JRSS-B: resample clusters, not rows, under within-cluster dependence; Efron 1987: BCa; Tsamardinos et al. 2018 for pooling — cited for pooling only, their bootstrap resamples rows.)
- *Superiority p:* user-level sign-permutation swapping each user's complete two-arm bundle, ≥10,000 permutations, statistic **studentized** (Chung & Romano 2013, Ann. Statist.) so the test is exact under the sharp null and valid under the weak null of metric equality. A superiority claim additionally requires the bootstrap CI to exclude 0 in the same direction.
- *Equivalence/non-inferiority:* TOST — 90% bootstrap CI ⊂ (−δ, +δ); one-sided NI — lower 95% bound > −δ (Schuirmann 1987, J Pharmacokinet Biopharm; Lakens 2017, Soc Psych Pers Sci; Wellek 2010). A TOST verdict is claimable **only if** the realized 90% half-width < δ.
- *Guards:* hard-fail if any class has <15 contributing users (a class contributed by k users empties a resample w.p. ≈ 0.368^k; silently redefining macro-F1 over surviving classes would bias the replicate metric); report min contributing-user count per class per state.

**Tier B — conditional configuration comparison (sweeps/ablations only).** The paired seed-level delta band (pooled-OOF delta per seed, band over seeds — `stats.py` as implemented). Resolves 0.05–0.15 pp; answers "does v2 beat v1 on this fixed data"; is **never** quoted as a generalization CI. A sub-0.3 pp Alabama effect may be reported as Tier-B-real but Tier-A-unresolved — say exactly that.

**The margin, pre-specified defensibly.** δ = **0.4 pp absolute**, per task-metric (macro-F1 and Acc@10), frozen in this document before any fold is trained. Anchor chain, in order: (1) *decidability floor* — δ must exceed 2× the largest paired-relevant noise component; top of the measured paired seed band is 0.15 pp, so δ ≥ 0.3 is necessary for the test to be decidable at all; (2) *re-instantiation floor* — same-method end-to-end rebuild moves the number ~0.18 pp (measured once); for claims that quantify over rebuilding, an effect below ~2×0.18 ≈ 0.4 pp is operationally indistinguishable from rebuilding yourself (Bouthillier et al. 2021, MLSys: measured nuisance variance as the yardstick for meaningful differences — the direct precedent); (3) *external ceiling* — stricter than the customary 1 pp example ROPE in the ML comparison literature (Benavoli, Corani, Demšar & Zaffalon 2017, JMLR — cited as customary example, not "convention"). This is non-circular because δ derives from same-arm measurements that exist independently of any A-vs-B delta; the dated commit makes that auditable. Each cycle's regenerations yield free additional rebuild-floor observations — logged as **validation of the anchor, never retuning**; if new floors exceed 0.2 pp, report the discrepancy, do not move δ. Mandatory sensitivity appendix: every equivalence verdict restated at δ ∈ {0.2, 0.4, 1.0}.

**Fixed-sequence gatekeeping (kills directional forking).** "Which of superiority/equivalence applies varies by state" must be an outcome of a rule, not a post-hoc choice. Per state × task, the pre-registered primary hypothesis is **non-inferiority of joint vs the STL ceiling at δ**; superiority is tested second, only where NI passes, at the same α (standard NI→superiority switching, CPMP/EWP/482/99, EMA 2000 — no correction needed). Four-way verdict per cell: superior / non-inferior / inferior (CI upper bound < −δ ... i.e. entirely below 0 and −δ respectively) / inconclusive. **Dual reporting:** a significant win with \|Δ̂\| < δ is reported verbatim as "significant, within the pre-registered practical margin" — never suppress either half. The co-primary headline per state ("no measured cost") is the intersection–union claim *reg NI ∧ cat superior-or-NI at the same checkpoint contract*, each component at full α (Berger 1982; no multiplicity correction across co-primaries).

**Corroborator (zero fits):** Bayesian correlated t-test with ROPE on the 5 paired fold deltas, seeds averaged within fold first, ρ = 1/k = 0.2 with sensitivity at ρ ∈ {0.1, 0.2, 0.3}; posterior P(Δ>δ), P(\|Δ\|≤δ), P(Δ<−δ) from the closed-form Student-t (df=4, scale = sd_folddelta·√(1/5+1/4)), unit-tested against `baycomp.two_on_single` (Corani & Benavoli 2015, *Machine Learning*; Benavoli et al. 2017). It speaks to the one dependence structure Tier A conditions away (75–80% train-set overlap). Division of labour, pre-registered: Tier A governs effects < 0.5 pp (the corroborator is underpowered there — its posterior scale is ≈0.07–0.2 pp, so it adjudicates only ≥0.2–0.6 pp); for effects ≥ 0.5 pp its wider posterior tempers claim strength. Nadeau–Bengio corrected t on the same deltas is a frequentist footnote, Holm-corrected within the headline family (Nadeau & Bengio 2003, *Machine Learning*; Dietterich 5×2cv rejected on its own terms — 50% training changes the learning regime, fatal for sparse 520–8,501-class region heads; Dietterich 1998, Neural Comp.).

**What a null licenses.** Superiority null: "no difference detectable at ~0.05–0.3 pp resolution for this state's users, conditional on the frozen split and fits" — explicitly NOT equivalence. Equivalence comes only from the TOST branch. TOST fail + superiority fail = "undetermined at margin δ", reported as such, never collapsed into either verdict; the sensitivity row shows at what margin the data would have decided. Pre-declared floor: \|Δ\| ≤ 0.05 pp is indistinguishable from re-running the same configuration (measured re-run noise 0.02–0.05 pp) and is never claimed in either direction, regardless of p.

**Mandatory first-run diagnostic:** on the first regenerated state (Alabama), report the realized paired CI half-width against the projected 0.05–0.3 pp and the unpaired ≈0.5 pp benchmark. The pairing gain is a hypothesis to verify, not an assumption; if it fails to materialize, sub-0.3 pp claims and δ=0.4 TOST are downgraded until seeds or the design are revisited.

---

## 4. Across-state: heterogeneity and scaling — not pooling

No pooled p-value exists in this protocol. The per-state table is always primary; the Florida-wins/Alabama-collapses pattern must stay visible.

**4a. Confirmatory cross-state statement: partial-conjunction replicability.** Combine the six per-state p-values on a **common null** — the NI direction, H0_s: δ_s ≤ −δ (superiority implies it) — via Benjamini & Heller (2008, JASA) / Dror, Baumler, Bogomolov & Reichart (2017, TACL — the established ML multi-dataset framework, no exchangeability assumed). Report u*: "non-inferior in at least u of 6 states", plus a second u* for the superiority sub-family. "Works in all six" is intersection–union: all six individual passes, no further correction. Precondition (one-hour pandas job): intersect user IDs across the six parquets — Gowalla users travel; if overlap is non-trivial, assign each traveller to one state or report the overlap and switch to the Bonferroni combining variant. Istanbul is clean by construction.

**4b. Descriptive synthesis: forest plot + prediction interval.** Two-stage IPD-style meta-analysis (Riley, Lambert & Abo-Zaid 2010, BMJ — datasets-as-studies, analogy confessed in-text), one per claim family: stage-1 inputs are the per-state Δ ± SE with **SE_i² = SE_boot,i² + s²_seed,i/S** (folding the seed component in stops seed noise masquerading as between-state heterogeneity). Stage 2: random effects, τ² by REML with Paule–Mandel sensitivity (never DerSimonian–Laird at k=6; Veroniki et al. 2016, Res Synth Methods), **modified** Knapp–Hartung (Röver, Knapp & Friede 2015, BMC MRM — plain HKSJ undercovers at τ̂²=0), Q-profile CI for τ². The cross-state sentence is the **95% prediction interval** with t₄ = 2.776 (Higgins, Thompson & Spiegelhalter 2009, JRSS-A; presentation per IntHout et al. 2016, BMJ Open), framed as "a new region sampled and evaluated the way these six were" — the pooled diamond is a figure annotation, never quoted. Caption warns that a zero-crossing PI at k=6 reflects low k plus real spread, not absence of effect. **Sensitivity row:** FL and AL are development states (B9 tuned on FL, H3-alt on AL/AZ); mark them and report the synthesis with and without them (k=4). Pre-commit the wording for the likely outcome "per-state NI: 6/6; predictive NI: not established at k=6" — arithmetic makes it likely at δ ≤ 0.5 whenever τ ≳ 0.15 pp.

**Sign test, one line, capped family:** exact binomial on the six per-state deltas, at most TWO primary uses (one per task on the headline), Holm within that pair — best achievable p = 2⁻⁶ = 0.0156, so any larger family kills it arithmetically. NI claims use the margin-shifted win rule (Δ_s > −δ); ties declared when \|Δ_s − shift\| ≤ max(0.05 pp, that state's band). It reliably certifies uniform effects ≥ ~0.2 pp; in the 0.05–0.2 pp regime it is a lottery (power 0.17–0.87) and 4a is the instrument (Demšar 2006, JMLR; Conover for exact/tie handling).

**Optional robustness layer (venue-dependent):** normal–normal Bayesian hierarchical model with ROPE (d_s ~ N(δ_s, se_s²), δ_s ~ N(μ, τ²), τ ~ half-N(0,1 pp), sensitivity at half-N(0,{0.5,2})), decision margin ±0.5 pp only — the ±0.1 pp "noise" tier is mathematically unreachable at AL/AZ/IST (needs se ≤ 0.05 pp) and is demoted to a descriptive overlay. **Shrinkage firewall:** per-state headline verdicts must hold in the unshrunken d_s ± se_s; a verdict that flips under pooling is "sensitive-to-pooling", not decided. (Benavoli et al. 2017; Friede, Röver, Wandel & Neuenschwander 2017, Res Synth Methods — k=2–5 is a workable regime; Kruschke 2018, AMPPS.)

**4c. Scaling.** The k=6 between-state meta-regression is **not defensible as confirmatory** (~4 residual df; windows/users/density/region-count are rank-correlated across the five US states — Cochrane's ~10-studies-per-covariate heuristic; one state flips the slope). It is demoted to: a bubble plot of Δ ± CI vs log₂(windows) (companion panel vs log₂(users); Istanbul highlighted as the confound-breaker — many users, few windows, lowest cardinality), with an exploratory REML slope protected by the Higgins & Thompson (2004, Stat Med) permutation test.

The **within-state dose–response supplements — it does not replace — the k=6 layer**, and it is the only defensible scaling *inference*. Design (invented, declared as such; framing precedent Hestness et al. 2017 / Kaplan et al. 2020): Florida; subsample development users at 25/50/75% (fixed subsample seed, nested); retrain the paired arms; evaluate every dose on the SAME sealed outer folds — only the training pool shrinks, so dose-to-dose and arm-to-arm deltas are paired on identical test users and the 1.2 pp fold component cancels. Under the drawn-partition design of §10.1 there is no single frozen partition, so a dose–response run must **name the execution that anchors it**; `(0, 0)` is the default, being the legacy diagonal and §8's like-for-like anchor. Fixing that anchor is what makes the dose axis paired, and it must be registered before the first dose is trained. Pins: (1) **frozen substrate** default — the claim is "scaling of the supervised stage given a fixed representation"; retrain-per-dose is an optional labelled upgrade (+3 substrate builds, +0.18 pp per-dose uncertainty); (2) rebuild all train-only artifacts (class weights; any active log_T) from each dose's pool per fold — the stale-log_T trap is +8–12 pp; (3) dose runs use the identical protocol and their 2 seeds ⊂ confirmatory seeds, so the 100% anchor is free; (4) verify low-dose seed variance transfers (AL at 96k windows bounds the FL-25% regime from below; else one 4-seed check at 25%); one replicate subsample seed at 25% bounds subsampling-realization variance; (5) per-dose test-region coverage diagnostic for reg (label-coverage collapse is structural, not architectural). Resolution ~±0.15–0.25 pp per dose — ~15–20× the between-state layer. A flat curve is a strong finding: "the joint-vs-STL effect is invariant to a 4× volume change within one geography", licensing transfer of per-state conclusions across the size axis; disagreement with the between-state plot means the between-state pattern is confounded by something other than volume — itself a finding.

---

## 5. Sweeps: screen/confirm and multiplicity

**Structural rule (from two rejected designs — do not soften it):** sweeps must never select on outer-test readings that later feed a confirmatory table. Selection-on-outer re-imports Cawley–Talbot bias into the exact protocol built to remove it, and fresh seeds do not cure it (the fold-idiosyncratic component of the delta survives seed refresh).

- **Screen:** candidate ranking uses **inner-validation metrics only**, or full Tier-B paired runs on development states whose outer readings are thereby burned for confirmatory use. Promotion threshold: paired Δ ≥ 0.15 pp on the screen instrument (calibrated to the top of the paired band — a decision rule, not a citable test; declared as invention). Screen ledger controlled at BH-FDR q = 0.10 (Benjamini & Hochberg 1995, JRSS-B; BY fallback if positive dependence is doubted) — false promotions are cheap because confirmation catches them.
- **Freeze:** the promoted shortlist is committed (arms, hyperparameters, tie-breaks) before any confirmatory outer fold is scored. This is the audit doc's own strategy made mechanical.
- **Confirm:** frozen arms enter the §2 matrix; outer folds are read once per arm per freeze cycle. Any post-viewing change reverts the run to exploratory (audit criterion 7). Winners are reported only from these sealed evaluations — multiplicity control does not remove winner's curse; only fresh confirmation does.
- **Multiplicity, layered by family** (family = state × task × claim-set; never pool states into one family):
  - *Within-family version sweep* (K versions vs champion, shared folds/seeds/users): **Romano–Wolf step-down max-T** (Romano & Wolf 2005, Econometrica) on the same user-cluster permutation replicates — one joint per-user relabeling of all K+1 arm bundles per replicate, all K statistics recomputed from it. It exploits exactly the cross-arm correlation that makes Bonferroni brutal here, and unlike raw Westfall–Young needs no subset pivotality.
  - *Per-state headline family* (2–3 tests): **Holm** (1979, Scand J Statist) within each state; no correction across states — each state is a separate confirmatory replication; cross-state evidence is §4a's job, not α-shrinking.
  - *Cross-state:* partial conjunction (§4a).
- **MDE discipline:** before any test, publish the per-state MDE table (§6) computed from saved predictions; where MDE exceeds the effect of interest, report the Tier-B band as "reproducible on this benchmark" and abstain from the population claim — a failed underpowered test is never reported as evidence of absence.

---

## 6. Power — what each design can actually detect

All numbers derived from the measured components (fold σ ≈ 1.2 pp; same-arm seed sd 0.02–0.07 pp; paired seed band 0.05–0.15 pp = 2·SE; re-run floor 0.02–0.05 pp; rebuild floor 0.18 pp). α = 0.05 two-sided, 80% power unless stated. This table is the answer to "no test has ever detected anything," and a version of it goes in the paper (precedent: Card et al. 2020, EMNLP, "With Little Power Comes Great Responsibility").

| Design | Alabama (3,858 users) | Texas (38,644 users) | Verdict |
|---|---|---|---|
| **Legacy unpaired** (2 arms × 5 fold means, t) | MDE ≈ **2.4 pp**; ≈ **3.6 pp** with the Nadeau–Bengio overlap correction | same order (fold σ is state-comparable) | Sees only the very top of the 0.1–3 pp range. **This is why the old tests never fired.** |
| Legacy invalid n=20 (seed×fold pooled) | MDE ≈ 1.1 pp | ≈ 1.1 pp | Still blind below 1 pp, *and* anti-conservative — worst of both. |
| **Tier B: paired over seeds** (4 seeds, paired t, df=3) | MDE ≈ **0.10–0.31 pp** | same (seed band is not user-count-driven) | 10–30× gain, zero extra compute. The measured +0.354 ± 0.095 pp schedule effect sits comfortably above it — the worked proof of concept. Conditional claim only (fixed users). |
| Tier B at 2 seeds | no valid band (1 df); raw deltas + verdict-shift gate | same | Point-estimate seed jitter ≤ ~0.1 pp; the gate makes it impossible for seed noise to silently decide a near-margin verdict. |
| Tier B under Holm (m≈12 family, df=3) | MDE ≈ 0.21–0.63 pp | same | Why the headline family is small and the sweep family uses Romano–Wolf. |
| **Tier A: paired user-cluster bootstrap** (pooled OOF) | 95% half-width ≈ **0.21–0.26 pp** (Acc@10), ≈ **0.30 pp** (macro-F1) → detects ≈ 0.3 pp, marginal at 0.2 | half-width ≈ **0.02–0.08 pp** → detects 0.1 pp easily | Scales ~1/√users. **Alabama's ~0.25–0.3 pp floor is a property of 3,858 users, not of the test — no method and no seed count beats it.** Effects below it are phrased as bounded ("\|Δ\| ≤ X pp"), never as detected. |
| TOST at δ = 0.4 (Tier A) | power ≈ 0.94 at true Δ = 0; true Δ = 0.3 fails (0.3 + 0.2 > 0.4) — failure onset ~0.3 pp | power ≈ 1 at true Δ = 0; onset just below δ | The margin is decidable at every state; verify realized half-width < δ before claiming (the §3 gate). |
| Reporting floor | \|Δ\| ≤ 0.05 pp = re-run noise; never claimed | same | — |

Back-of-envelope for the Tier-A rows: fold spread 1.2 pp over ~772-user folds ⇒ per-arm pooled SE ≈ 0.54 pp unpaired; between-arm per-user correlation ρ ≈ 0.95–0.99 for paired variants ⇒ SE_Δ ≈ 0.08–0.17 pp. These projections are **planning heuristics**; the binding numbers are the realized bootstrap half-widths from the first dataset read, and the table is republished with measured values (the §3 first-run diagnostic).

---

## 7. Cost

Confirmatory package (3 arms: joint, cat-STL, reg-STL):

| Item | Fits | Wall-clock (A40-scale) |
|---|---|---|
| Bridge: AL + AZ + IST × 3 arms × 4 seeds × 5 folds | 180 fits, all small states | well under a day |
| FL + CA + TX × 3 arms × executions × 5 folds | 135–180 fits | decided by the ladder of §2a; the large states are expected to halt at three executions |
| All inference (bootstrap, permutation, Romano–Wolf, TOST, meta layer) | 0 fits | CPU hours (per-user sufficient statistics make replicates weighted sums) |
| Golden fixtures + dual-scoring (§8) | 0 fits | ~1–2 analyst days |
| Optional: FL dose–response (3 doses × 3 arms × 2 seeds × 5 folds = 90 fits ≈ 9 full-FL arm-seed equivalents + checks) | 90 fits | ≈ **1.2 GPU-days** |
| User-overlap audit, manifests, pre-registration | 0 fits | hours |

Net: the mandatory package comes in at roughly **half the current 3-day design** while being strictly more rigorous; the only new-compute purchase is the optional scaling curve.

---

## 8. Migration: measuring the legacy bias

The reported numbers of the previous system were produced under a different selection rule
(per-seed max-over-epochs on the reporting observations) and are **not commensurable** with numbers
from this protocol. Any cell run under both rules measures that gap and is labelled as measuring it,
never as a result.

The v19 campaign carried a dedicated set of cells for this purpose; what it measured is recorded in
[`../v19_RECORD.md`](../v19_RECORD.md) §8. A new cycle that needs the comparison re-runs the
**method**, not the number.

---

## 9. What this protocol still cannot claim

1. **All within-state intervals are conditional** on the frozen split and the fitted models. They quantify user-sampling uncertainty for this state; they do not license "a fresh retraining lands inside this CI." No unbiased estimator of CV variance exists (Bengio & Grandvalet 2004, JMLR), and CV intervals estimate procedure error only with care (Bates, Hastie & Tibshirani 2023, JASA). Seed SD and the 0.18 pp rebuild component are reported beside every interval as separately measured procedure noise.
2. **Alabama's user floor is irreducible:** ~0.25–0.3 pp under user resampling at 3,858 users, at any seed count and any analysis. Sub-floor effects there are Tier-B conditional findings or bounded absences — never detected population effects.
3. **Six purposively chosen datasets are not a superpopulation.** The defensible targets are: new users within these six regions (§3); "at least u* of these six regions" (§4a); "a region sampled like these", with wide t₄ uncertainty (§4b's prediction interval). "US states in general" is not claimable.
4. **Development contamination is reduced, not removed.** Re-running AL/AZ/FL under the clean protocol removes checkpoint-selection bias but not tuning familiarity; Istanbul/CA/TX carry the confirmatory weight, and the k=4 sensitivity row exists for this reason.
5. **The scaling dose is a bundle.** User-subsampling shrinks windows, users, and density together; the FL curve attributes "training volume" as a bundle within one geography under a frozen representation. Separating components, or covering substrate scaling, is future work and is labelled as such.
6. **The margin is ultimately a judgement call dressed in measurements** ("why 2× the floor and not 3×"). The defence is the pre-registration date plus the δ ∈ {0.2, 0.4, 1.0} sensitivity appendix — which is why both are mandatory, and why nothing in this document may be edited after the first fold of the cycle it governs is trained. Amendments are dated entries in [`EVALUATION_PROTOCOL_CHANGES.md`](EVALUATION_PROTOCOL_CHANGES.md), which records what changed, when, and against when the cycle started.

---

### Pre-registration checklist (commit before the first fold)
δ = 0.4 pp per task ▪ fixed-sequence NI→superiority per state × task ▪ geom_simple frozen (with C21 disclosure) + symmetric STL selection ▪ executions: the ladder of §2a, both knobs drawn fresh per execution (§10.1; never 42) ▪ `partition_hash` pinned per execution, `model_seed` separate, inner_split_seed, fail-closed folds ▪ pooled-OOF estimands (macro-F1 convention, top10_raw, zero-support rule: skip-and-count) ▪ testing families + corrections (Holm headline / Romano–Wolf sweeps / BH q=0.10 screen / partial conjunction cross-state) ▪ 0.05 pp floor ▪ shadow-log quarantine spec ▪ dose–response pins (if bought) ▪ this document's git hash.

---

## 10. Repetitions vs replicates — the decision, and the test that reversed it

> Written after the protocol, against a fact verified afterwards: `splits.build(..., seed=s)` feeds
> `StratifiedGroupKFold(random_state=s)` while the same `s` seeds initialisation, so four seeds gave
> four **distinct partitions** (0 → `162efc6b2b4a`, 1 → `8757b9120c96`, 7 → `e721b25fe486`,
> 100 → `179e105519b2`). What the project called a seed is a **repetition**; repetition and
> **replicate** are confounded. This section re-derives §2's choices under the corrected reading.

**The headline consequences.** Every number measured before this section — the 0.05–0.15 pp paired
band, the 0.02–0.07 pp same-arm sd, §6's power table, every legacy result — came from **repeated
k-fold CV**, not restarts on a fixed split. So the measured band already covers partition
resampling: it is a *stronger* quantity than §2 believed, and since δ = 0.4 was anchored at ≥2× the
top of that band, **the margin already prices partition variability in**.

### 10.1 The partition is drawn per execution — and never at seed 42

**Decision: draw, do not freeze.** One `(split_seed, model_seed)` pair per execution, both drawn
fresh; the estimand of §1 is marginal over the partition draw. This reverses an earlier decision to
freeze one partition per state, and §10.4 records the measurement that reversed it — the reversal is
not a change of mind, it is a pre-registered test firing.

Pairing does not distinguish the two designs: repeated partitions stay paired as long as both arms
share each repetition's partition, exactly as a frozen design pairs on one. The 1.2 pp fold component
cancels either way.

**And never 42.** Every recipe choice was tuned at seed 42 — under the corrected reading that means
tuned on *partition-42 and init-42 jointly*, and the +3/+8 pp CA/TX development-seed overshoot is the
confounded symptom. A confirmatory design containing the development draw makes the confirmatory
partition the development partition, at whatever weight it carries. This is **enforced, not
advised**: the ladder's execution list (`src/mtlcheck/eval/pilot.py`) excludes 42 at every rung, with
a test that fails if it returns. It did return once — it sat at the P=6 rung until 2026-08-25, where
it would have been 1/6 of the confirmatory mean at exactly the datasets that escalate to the ceiling.

One amendment to §4b: per-state SE_i must use the **confounded** legacy band for the seed term, not
the narrower pure-replicate band a fixed-partition design would measure. Under the drawn design this
is no longer a correction — it is the matching quantity. The risk runs toward claiming less.

### 10.2 The bootstrap does not cover the partition axis

**Not the §3 bootstrap, and the protocol must never imply otherwise.** The bootstrap resamples
*evaluation users* within one partition from fixed fitted models. Re-partitioning changes which users
trained the model, and refits. Orthogonal axes.

Under the drawn design the objection a reviewer would raise — *"your CI is tight but your estimate
would move under another split"* — is answered by the design, and by **a second band reported
alongside the headline**. Be precise about which is which, because they are different objects:

* the **headline interval** is the §3 user bootstrap, with the executions averaged inside each
  replicate. It is the pre-registered one, and it does **not** shrink with P;
* the **execution band** is `t₀.₉₇₅,P−₁ · s / √P` over the per-execution pooled-OOF deltas. It is the
  only quantity P shrinks, and it is therefore exactly what the extra executions buy. Its form is
  deliberately the one §2a projects, so §3's realised-versus-projected confrontation is a
  subtraction and not a translation.

Which of the two is the headline was fixed **before any reading** — the only moment at which the
choice is not biased by the result. Below three executions the band does not exist, by the same rule
§2a applies to the ladder's floor.

What the bootstrap still cannot do is separate the two axes inside one execution, and §10.4 is where
that separation was measured, once. 

### 10.3 The floor of two executions is triage — never a stopping point

Two executions give 1 degree of freedom on the **confounded** variance, which is the larger one.
That is not a design; it is one sample. The §2a ladder therefore forbids halting at the floor
(`GL_MINIMO`, verified by a test that a dispersion of exactly zero still does not license a stop),
so every dataset buys at least three executions. It is the same guard this protocol already carried
as "no 2·SE band below R = 3" (t₀.₉₇₅,₁ = 12.706; 3.182 at 4 executions), moved to the execution axis.

### 10.4 The decomposition — it ran, and it reopened §2

2×2 factorial, `split_seed ∈ {0, 7}` × `model_seed ∈ {0, 7}`, three arms, 5 folds, on inner
validation. Pre-registered rule, written before it ran: *"if the partition axis exceeds 0.15 pp, the
freeze is unsafe and §2 reopens before any large-state fit"*.

Run 2026-08-23 at four datasets. Partition-axis main effect, in pp:

| dataset | users | cat | reg |
|---|---:|---:|---:|
| alabama | 1 101 | +0.077 | **+0.366** |
| arizona | 2 136 | +0.088 | **+0.306** |
| florida | 10 622 | +0.117 | −0.035 |
| istanbul | 14 530 | −0.022 | −0.075 |

**The rule fired.** On the region task the axis exceeds 0.15 pp at both datasets under 2 200 users,
and falls below it — with the sign inverted — at both above 10 000, while the standard error drops
from 0.28 to 0.07. The measurement becomes four times more precise exactly where the effect
disappears. Category stays below the threshold everywhere.

Two honest readings disagree: **literal** — the rule is mechanical, it fired, the freeze is unsafe;
**statistical** — 0.366 ± 0.283 is 1.29 standard errors, and applying a mechanical threshold to an
unresolved estimate is the error §3 forbids elsewhere. The protocol takes the literal reading,
because a pre-registered rule that is only obeyed when convenient is not a rule.

**And the finding shapes the replacement.** A partition axis that is a small-dataset phenomenon
cannot be handled by measuring it on small datasets and transferring the result to large ones — that
is precisely backwards, and it is what the retired calibration bridge did. It has to be measured
**per dataset**, which is what §2a does.

Declared limits: 1 df per axis, sign-and-magnitude only, inner validation.

### 10.5 What must be recorded

The confound survived because one field named `seed` meant two factors.

| Field | Content | Enforcement |
|---|---|---|
| `split_seed` | integer → `StratifiedGroupKFold(random_state=...)` | required; drawn per execution, never 42 (§10.1) — the pairs of rung P are `pilot.sementes(P)` |
| `partition_hash` | digest of the realised user→fold assignment | required; one hash per execution, asserted fail-closed — **the hash is ground truth, the seed is only the recipe** |
| `model_seed` | integer feeding `fold_seed`/`seed_everything` | required; moves with `split_seed`, never reused across executions |
| `fold_seed_rule` | derivation + `decorrelated_fold_seed` flag | required |
| `inner_split_seed`, `inner_partition_hash` | the §2 inner split | required wherever a checkpoint is selected |
| `repr_seed` | substrate build seed | unchanged |
| `band_over` | `model_seed` / `split_seed` / `confounded_legacy` | `stats.py` refuses to print a band without it |

`--seed` splits into `--split-seed` and `--model-seed`; `cell_id` embeds both; manifest validation
rejects a bare `training.seed`, so the single-knob shape cannot produce an accepted result.

⚠ **This design is what `NOMENCLATURE.md` §1 calls the confounded one** — partition and
initialisation moving together. The confounding is fatal for **attributing** variance to an axis and
harmless for estimating the **marginal** effect, which is what the headline claims. What was wrong in
the legacy system was the bookkeeping (one field for two factors) and the analysis label ("seed
variance"), not the randomisation. State this before a reviewer finds it.

---

## 11. Is there a test set? — verified 2026-08-17

Two different questions hide behind this, and they have different answers.

### 11.1 Within a state: yes, and it is the central fix

The **original protocol had no test set.** One held-out fold did two jobs — it selected the
checkpoint (max over epochs) *and* produced the reported score, which is selection on the reporting
observations. That is the defect this whole document exists to remove.

The proposed design **does** have one: of each state's users, 70 % train, 10 % inner validation
(checkpoint selection only), **20 % outer test, sealed and read exactly once** (§2). Every user
still receives an out-of-sample prediction across the five folds, so nothing is wasted; what changes
is that the observations deciding the checkpoint are disjoint from the observations reporting the
score. Audit criterion 6 — no runner may touch the outer loader inside an epoch loop — is what
enforces it mechanically.

So: within a state, the answer is yes, and it is already in the plan.

### 11.2 Across states: no — and 60 unused datasets say that is fixable

§9.4 concedes it: *"development contamination is reduced, not removed."* All six states were used
during a long development history. Re-running them under the clean protocol removes checkpoint bias
but not tuning familiarity, and no amount of internal splitting manufactures a dataset the project
has never looked at.

**Measured, not assumed:** `data/checkins/` holds **67 state corpora and the study uses 7.** Sixty
have never been touched by any tuning decision, any sweep, or any inspection. Candidates of usable
size:

| estado | check-ins | usuários | lugares |
|---|---:|---:|---:|
| New York | 714 666 | 20 874 | 47 930 |
| Washington | 607 882 | 8 658 | 35 272 |
| Illinois | 539 946 | 14 176 | 39 285 |
| Oklahoma | 472 210 | 6 549 | 24 539 |
| Pennsylvania | 460 460 | 9 841 | 37 268 |

New York sits between Istanbul (271 666 windows) and Florida (1 274 418) in scale, so it exercises
the size regime the scaling claim most needs and is not a degenerate small case.

**Recommendation: designate ONE unused state as the sealed external confirmation set, name it in the
pre-registration, and touch it exactly once — after every recipe, margin and selector is frozen.**
It answers the question the six states structurally cannot: *does the frozen procedure hold on a
geography nobody tuned against?* That converts §9.3's honest limitation ("six purposively chosen
datasets are not a superpopulation") from a caveat into a tested claim, and §9.4's "Istanbul/CA/TX
carry the confirmatory weight" from an argument into evidence.

Three conditions, or it is theatre. **(1)** The state is named in the pre-registration commit and
never opened before the confirmatory run — not for a smoke test, not to check the shapefile parses.
Preparation that must happen first (spatial join, HGI artifacts) runs as a mechanical build whose
*outputs are not inspected*. **(2)** It is read once. A second look after a disappointing first makes
it a development state, permanently, and there are 59 others but only one first look each. **(3)**
Its result is reported whatever it shows. A confirmation set that only appears in the paper when it
agrees is worse than none.

Cost: one state × three arms × R = 2 × 5 folds = 30 fits, plus its substrate build — the smallest
line item in the package, and the only one that buys external validity.

**Caveat, stated plainly:** this tests transfer to an untuned *US state from the same Gowalla
collection*. It is not evidence for a different data source, a different era, or a non-US geography.
Istanbul remains the only non-US corpus, and it is a development state.

---

## 12. Registered decisions

Decisions taken after the body was first written, folded in here rather than left as an appendix of
dated amendments. The previous form — a frozen body plus fourteen amendments, 57 % of the document —
made "what is the rule?" a reconciliation exercise. **Everything below is live.** The dated record of
what governed the v19 campaign, including the bridge and the amendments that patched it, is in
[`../v19_RECORD.md`](../v19_RECORD.md) and governs nothing new.

| decision | rule |
|---|---|
| **Multiplicity, within-family sweeps** | Romano–Wolf step-down is deferred; Holm stands in its place until a sweep family is actually run. |
| **Holm and the co-primary claim** | Different families. Holm corrects the per-state headline pair; the co-primary conjunction is intersection–union and each component is tested at full α (Berger 1982). |
| **Cross-state combination (§4a)** | **Bonferroni**, not Simes. §4a made a user-ID intersection a precondition; it ran on 2026-08-23 and failed — 24.5 % of users appear in more than one US state, and travellers carry 51 % of Texas check-ins. Simes needs independence or PRDS; Bonferroni holds under arbitrary dependence. Istanbul is the only genuinely independent dataset, and the text must say so. |
| **The printed verdict column** | The **marginal** verdict, with `†` marking what Holm would downgrade. Printing only the adjusted verdict hides the effect size; printing only the marginal hides the correction. |
| **Vocabulary** | **partition** is the word in prose, tables and published text. The configuration field, the parquet column and the `cell_id` segment stay spelled `split_seed`: the name enters `science_fingerprint`, and renaming it would invalidate banked cells for a word. |
| **Substrate design** | Sealed 70/10/20 outer-test / inner-val. The 10 % inner set is one fold of an 8-way `StratifiedGroupKFold` on the 80 % development block. **The outer-split seed, the inner-split seed and the model-initialisation seed are three separate fields** — the origin of `split_seed` / `inner_split_seed` / `model_seed`. |
| **Guards that must exist in code** | Window pairing (both arms score the identical `(fold, user, window)` sets), identical vocabulary across compared arms, the §1 leak canary refusing rather than warning under confirmatory reading, and no sealed cell printable without a recoverable scientific identity. |
| **How many executions** | The escalation ladder of §2a. The bridge that preceded it is retired — see §2a and [`../future_works/banda_da_ponte_transfere.md`](../future_works/banda_da_ponte_transfere.md). |
