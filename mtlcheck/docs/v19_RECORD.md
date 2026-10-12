# Registro da campanha v19 — o protocolo que a governou, preservado

> **Este arquivo é histórico e não é a regra vigente.** Ele preserva, sem edição, o protocolo
> estatístico como estava congelado quando a campanha `v19_defence` foi desenhada, treinada e
> parcialmente lida. A regra vigente é [`plans/EVALUATION_PROTOCOL.md`](plans/EVALUATION_PROTOCOL.md),
> que abandonou a ponte de calibração e adotou a escada de escalada.
>
> **Por que ele existe.** Em 2026-08-24 a leitura confirmatória dos três estados-ponte aconteceu —
> Alabama, Arizona, Istambul, 36 pares (identidade, conjunto) gastos e registrados em
> `studies/READ_LEDGER.json`, irreversíveis. Os números daquela leitura vão para a dissertação, e o
> que os governou é load-bearing na defesa. Apagar este texto para deixar a documentação limpa
> tornaria aqueles números indefensáveis.
>
> **O que mudou depois, e por quê.** A ponte — medir a dispersão em três conjuntos pequenos e
> transferi-la para licenciar menos execuções nos grandes — foi examinada contra a literatura depois
> de o gate dela reprovar. Ela mede o regime errado, dá ao menor conjunto veto sobre o maior, agrega
> por um máximo que não tem propriedades conhecidas, e não tem precedente publicado em ML. Foi
> substituída por uma escada em que **cada conjunto mede a si mesmo**, na validação interna, que não
> gasta leitura. O raciocínio completo está em `future_works/banda_da_ponte_transfere.md` e nas
> emendas §12.9 e §12.10 abaixo.
>
> **O que este registro NÃO autoriza.** Ele não governa nenhuma campanha nova. Um ciclo futuro que
> cite estas regras estará citando história, não protocolo.

---

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

**Status:** to be committed, dated, BEFORE the AL/AZ/Istanbul bridge regeneration. The pre-registration is the load-bearing part: every margin, selector, hypothesis type, and escalation rule below must be in git before the first confirmatory fold is trained, or the defensibility argument evaporates.

**Substrate:** the sealed 70/10/20 outer-test / inner-val design **transcribed in §12.8**, from `docs/future_works/evaluation_protocol_cleanup.md` in the reference checkout (untracked — see §12.8). This document does not repeat that audit; it completes it. Everything here is post-processing of artifacts that design already mandates, except where a cost is explicitly counted.

---

## 1. The estimand

Per **state × task**, the quantity compared is the **paired delta of the pooled out-of-fold (OOF) metric**, conditional on the frozen user partition and the fitted models.

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
| Outer folds | 5, user-disjoint StratifiedGroupKFold, `split_seed=0` (amended per §10.1; was 42), frozen artifact + pinned `partition_hash`, **fail-closed** if absent | Between-fold spread ~1.2 pp is user-composition variance, common to both arms; pairing on shared frozen folds cancels it. More folds buy nothing pairing doesn't already deliver. |
| Inner val | 10% of users (one fold of an 8-way SGKF on the 80% block), `inner_split_seed` recorded separately | Selection must not touch the outer fold; 10% is viable even at Alabama (audit's simulation: ~160 inner-val users on the smallest input). |
| Refit | **No-refit default** — evaluate the inner-selected checkpoint on the outer fold; declare the estimand as "procedure trained on ~70% of users" | Refit doubles fits for a shift the paired delta mostly cancels; budget goes to seeds/states instead. |
| Checkpoint | Inner-val only; `geom_simple` (joint), best-own-metric (STL); frozen | See §1. |
| Model seeds — bridge states (AL/AZ/IST) | **4** ({0,1,7,100}) | Needed for like-for-like legacy comparison AND as the calibration set: the 0.05–0.15 pp paired seed band was measured under the legacy selection rule (per-seed max-over-epochs, which flatters and couples seeds) and does not automatically transfer to the new regime. The bridge re-measures it under the regime it will govern. |
| Model seeds — FL/CA/TX | **2** ({0,7}), locked from the bridge calibration | Measured seed SD (0.02–0.07 pp same-arm; 0.05–0.15 pp paired) is 20–50× below the fold/user component. Going 2→4 seeds shrinks the effective half-width by at most ~0.06 pp — invisible next to the user-sampling half-width the bootstrap measures — while doubling the dominant wall-clock. **4 seeds are not worth it at the large states**, provided the calibration gate passes: S=2 iff calibrated paired seed sd/√2 ≤ ⅓ × min(smallest effect of interest, TOST margin slack); otherwise S=4 from the start. |
| Escalation (pre-registered, mechanical) | (i) sign disagreement between the two seed deltas with \|Δ\| above the calibrated 2·sd envelope; (ii) \|Δ_s0 − Δ_s7\| > 3·sd·√2 (~99.7% envelope, known ~0.3% false-trip rate); (iii) **verdict-shift gate**: recompute the §3 verdict with Δ̂ shifted ±2·sd/√S — if it flips, escalate to S=4; if still unstable, report "seed-limited at this margin", never resolved. Every escalation event is reported. | A fixed 0.15 pp tripwire would fire 3–48% across the measured band; calibrated thresholds have known operating characteristics. |
| Fits per state per arm | 20 (bridge) / 10 (FL/CA/TX) | — |

**Tooling guard:** `stats.py` must refuse to print its 2·SE "separated" band when `n_seeds < 3` (at 1 df the calibrated multiplier is t₀.₉₇₅,₁ = 12.7, not 2.0); at S=2 it prints the two raw seed deltas and the verdict-shift-gate result instead.

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

**The margin, pre-specified defensibly.** δ = **0.4 pp absolute**, per task-metric (macro-F1 and Acc@10), frozen in this document before the bridge. Anchor chain, in order: (1) *decidability floor* — δ must exceed 2× the largest paired-relevant noise component; top of the measured paired seed band is 0.15 pp, so δ ≥ 0.3 is necessary for the test to be decidable at all; (2) *re-instantiation floor* — same-method end-to-end rebuild moves the number ~0.18 pp (measured once); for claims that quantify over rebuilding, an effect below ~2×0.18 ≈ 0.4 pp is operationally indistinguishable from rebuilding yourself (Bouthillier et al. 2021, MLSys: measured nuisance variance as the yardstick for meaningful differences — the direct precedent); (3) *external ceiling* — stricter than the customary 1 pp example ROPE in the ML comparison literature (Benavoli, Corani, Demšar & Zaffalon 2017, JMLR — cited as customary example, not "convention"). This is non-circular because δ derives from same-arm measurements that exist independently of any A-vs-B delta; the dated commit makes that auditable. The bridge regenerations yield free additional rebuild-floor observations — logged as **validation of the anchor, never retuning**; if new floors exceed 0.2 pp, report the discrepancy, do not move δ. Mandatory sensitivity appendix: every equivalence verdict restated at δ ∈ {0.2, 0.4, 1.0}.

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

The **within-state dose–response supplements — it does not replace — the k=6 layer**, and it is the only defensible scaling *inference*. Design (invented, declared as such; framing precedent Hestness et al. 2017 / Kaplan et al. 2020): Florida; subsample development users at 25/50/75% (fixed subsample seed, nested); retrain the paired arms; evaluate every dose on the SAME sealed outer folds — only the training pool shrinks, so dose-to-dose and arm-to-arm deltas are paired on identical test users and the 1.2 pp fold component cancels. Pins: (1) **frozen substrate** default — the claim is "scaling of the supervised stage given a fixed representation"; retrain-per-dose is an optional labelled upgrade (+3 substrate builds, +0.18 pp per-dose uncertainty); (2) rebuild all train-only artifacts (class weights; any active log_T) from each dose's pool per fold — the stale-log_T trap is +8–12 pp; (3) dose runs use the identical protocol and their 2 seeds ⊂ confirmatory seeds, so the 100% anchor is free; (4) verify low-dose seed variance transfers (AL at 96k windows bounds the FL-25% regime from below; else one 4-seed check at 25%); one replicate subsample seed at 25% bounds subsampling-realization variance; (5) per-dose test-region coverage diagnostic for reg (label-coverage collapse is structural, not architectural). Resolution ~±0.15–0.25 pp per dose — ~15–20× the between-state layer. A flat curve is a strong finding: "the joint-vs-STL effect is invariant to a 4× volume change within one geography", licensing transfer of per-state conclusions across the size axis; disagreement with the between-state plot means the between-state pattern is confounded by something other than volume — itself a finding.

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

Back-of-envelope for the Tier-A rows: fold spread 1.2 pp over ~772-user folds ⇒ per-arm pooled SE ≈ 0.54 pp unpaired; between-arm per-user correlation ρ ≈ 0.95–0.99 for paired variants ⇒ SE_Δ ≈ 0.08–0.17 pp. These projections are **planning heuristics**; the binding numbers are the realized bootstrap half-widths from the first bridge state, and the table is republished with measured values (the §3 first-run diagnostic).

---

## 7. Cost

Confirmatory package (3 arms: joint, cat-STL, reg-STL):

| Item | Fits | Wall-clock (A40-scale) |
|---|---|---|
| Bridge: AL + AZ + IST × 3 arms × 4 seeds × 5 folds | 180 fits, all small states | well under a day |
| Shadow per-epoch outer scoring on bridge states (§8) | 0 fits | +10–20% eval on bridge only |
| FL + CA + TX × 3 arms × **2** seeds × 5 folds | 90 fits | ≈ **1.5 days** (vs ~3 at 4 seeds — the single largest saving, licensed by the measured seed component and the bridge calibration; expected escalation adds 10 fits × the calibrated rare trip rate) |
| All inference (bootstrap, permutation, Romano–Wolf, TOST, meta layer) | 0 fits | CPU hours (per-user sufficient statistics make replicates weighted sums) |
| Golden fixtures + dual-scoring (§8) | 0 fits | ~1–2 analyst days |
| Optional: FL dose–response (3 doses × 3 arms × 2 seeds × 5 folds = 90 fits ≈ 9 full-FL arm-seed equivalents + checks) | 90 fits | ≈ **1.2 GPU-days** |
| User-overlap audit, manifests, pre-registration | 0 fits | hours |

Net: the mandatory package comes in at roughly **half the current 3-day design** while being strictly more rigorous; the only new-compute purchase is the optional scaling curve.

---

## 8. Migration: make the bridge MEASURE the legacy bias

The AL/AZ/IST regeneration does triple duty: legacy comparison, seed-band calibration (§2), and a direct measurement of what the old selection rule was worth. Three components, all pre-registered:

**8a. Selection-optimism estimators, co-registered on one trajectory.** On the bridge states, retain per-epoch checkpoints and run a **post-hoc scoring pass** over the sealed outer fold — mechanically quarantined: a separate process, append-only sink outside the rundir, no filesystem access from the selection code path, refuses to run until all seeds × folds of a state are complete (this satisfies audit criterion 6 rather than waiving it; cost ≈ 6% of bridge compute plus transient checkpoint storage). Per fold × seed × task, from the SAME trajectory on the SAME fold — so the 1.2 pp fold variance and seed variance cancel exactly:
- **a1** legacy-per-task = max over epochs ≥ 5 of the outer score (this IS the §0.1 rule — per task, not a joint selector);
- **b1** clean-per-task = outer score at the inner-val-selected epoch for that task;
- **b2** clean-joint = outer per-task scores at the single inner-val geom_simple epoch.

Report **biaŝ = a1 − b1** ("selection-on-test optimism") and **b1 − b2** ("single-checkpoint deployability cost") separately — never summed. SE over folds (n=5, seeds averaged within fold first): expected ≈ 0.13–0.22 pp against a prior of 0.3–0.5 pp mean (p90 ~1.2 pp from the 66 stored curves) — decisive either way. Also compute the per-arm deflation for the STL arms vs the joint arm: the legacy deployable comparison let each STL arm harvest its own per-task epoch-max while the joint arm committed to one checkpoint, an asymmetry expected to have run **against** the joint model — but registered as a hypothesis the bridge tests, because the post-hoc adoption of geom_simple (C21, +5.62 pp) is selector-level optimism in the joint arm's favor; the net direction is empirical (Cawley & Talbot 2010 §5; Varma & Simon 2006, BMC Bioinformatics).

**8b. Measurement pinning, so implementation drift cannot masquerade as protocol effect.** Before any bridge number: (i) golden-prediction fixtures — real bundles PLUS synthetic adversarial cases (supported-but-never-predicted class, FP-only class, top-k tie straddles, OOD targets) dual-scored through the legacy stack (torchmetrics, divides by all C) and mtlcheck (support∪predicted divisor), gate < 0.01 pp on every reported metric for every case occurring in real data; (ii) the fixture dual-scores BOTH aggregations (fold-mean vs pooled) so that offset is measured, not assumed; (iii) legacy torch/torchmetrics versions pinned from manifests (or the version spread reported as an ambiguity band); (iv) eligibility reconciliation as a **gate** — per-state manifests (row counts, eligible users, MIN_SEQUENCE_LENGTH, stride, per-fold row-set digests) must match or the fixture guarantee is void for that state; (v) every legacy joint-vs-STL cell recomputed under the unified top10_raw estimand from saved predictions — the historical mixing (joint scored with top10_full, dedicated-region with raw) is one-sided against the joint arm, so unification can only close or preserve the gap, which pre-empts the post-hoc-estimand suspicion. Historical contamination bound reported as measured ood_fraction × ood_hit_rate (realistically ≲ 0.15 pp), not the worst case.

**8c. What to say about legacy numbers.** The errata line: "the legacy selection rule's optimism, measured under the corrected protocol at AL/AZ/IST, is X ± SE pp (per task); legacy absolute numbers are expected to carry optimism of this order." An order-of-magnitude errata, not an exact correction — the bridge trains on ~70% under a rebuilt substrate, so it measures the legacy *rule* under the new regime, not the published numbers themselves. Legacy **paired** version-vs-version deltas are labelled "approximately unbiased, noisier" (both arms harvested similar optimism) — never "clean". Do not extrapolate the bias magnitude to CA/TX; their numbers are produced natively by the corrected protocol. If biaŝ < 0.1 pp, the errata is a footnote and the legacy NI margins survive — cheap good news, though the 66-curve prior makes it unlikely at AL.

---

## 9. What this protocol still cannot claim

1. **All within-state intervals are conditional** on the frozen split and the fitted models. They quantify user-sampling uncertainty for this state; they do not license "a fresh retraining lands inside this CI." No unbiased estimator of CV variance exists (Bengio & Grandvalet 2004, JMLR), and CV intervals estimate procedure error only with care (Bates, Hastie & Tibshirani 2023, JASA). Seed SD and the 0.18 pp rebuild component are reported beside every interval as separately measured procedure noise.
2. **Alabama's user floor is irreducible:** ~0.25–0.3 pp under user resampling at 3,858 users, at any seed count and any analysis. Sub-floor effects there are Tier-B conditional findings or bounded absences — never detected population effects.
3. **Six purposively chosen datasets are not a superpopulation.** The defensible targets are: new users within these six regions (§3); "at least u* of these six regions" (§4a); "a region sampled like these", with wide t₄ uncertainty (§4b's prediction interval). "US states in general" is not claimable.
4. **Development contamination is reduced, not removed.** Re-running AL/AZ/FL under the clean protocol removes checkpoint-selection bias but not tuning familiarity; Istanbul/CA/TX carry the confirmatory weight, and the k=4 sensitivity row exists for this reason.
5. **The scaling dose is a bundle.** User-subsampling shrinks windows, users, and density together; the FL curve attributes "training volume" as a bundle within one geography under a frozen representation. Separating components, or covering substrate scaling, is future work and is labelled as such.
6. **The margin is ultimately a judgement call dressed in measurements** ("why 2× the floor and not 3×"). The defence is the pre-registration date plus the δ ∈ {0.2, 0.4, 1.0} sensitivity appendix — which is why both are mandatory, and why nothing in this document may be edited after the first bridge fold is trained.

---

### Pre-registration checklist (commit before the bridge)
δ = 0.4 pp per task ▪ fixed-sequence NI→superiority per state × task ▪ geom_simple frozen (with C21 disclosure) + symmetric STL selection ▪ seeds: bridge {0,1,7,100}, large states {0,7} with the calibration gate and tripwires ▪ split_seed=0 (§10.1; was 42), `partition_hash` pinned, `model_seed` separate, inner_split_seed, fail-closed folds ▪ pooled-OOF estimands (macro-F1 convention, top10_raw, zero-support rule: skip-and-count) ▪ testing families + corrections (Holm headline / Romano–Wolf sweeps / BH q=0.10 screen / partial conjunction cross-state) ▪ 0.05 pp floor ▪ shadow-log quarantine spec ▪ dose–response pins (if bought) ▪ this document's git hash.

---

## 10. Repetitions vs replicates — the design decision this protocol has to make

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

### 10.1 Freeze the partition — but not at seed 42

Pairing does not distinguish the two designs: repeated partitions stay paired as long as both arms
share each repetition's partition, exactly as a frozen design pairs on one. The 1.2 pp fold component
cancels either way. The decision is about what the interval covers, what the sealed-artifact
machinery can enforce, and whether the budget can quantify what it buys.

The case for repeated partitions is real. An interval over repetitions covers "this procedure,
however the data happens to split", and a reviewer will ask whether an effect is specific to one
split — Bouckaert & Frank (2004, PAKDD) measured exactly that failure, and Dietterich's 5×2cv (1998)
exists because partition variance is first-order for single-partition tests.

Three things defeat it here. **The estimand:** under §1's pooled-OOF construction every user is held
out exactly once under *any* partition, so re-partitioning does not resample the evaluation data at
all — it changes which users co-trained the model scoring each held-out user. Partition variance is a
training-side noise component, not a test-side sampling axis; the test-side axis is carried by the
user bootstrap regardless. **The bound is already measured:** the legacy runs are a free
four-partition robustness study, and the paired delta moved ≤0.15 pp across four distinct partitions
— below δ/2. A component biasing every arm identically cancels in the paired delta; the residual is
the arm × partition interaction, which §10.4 measures. **Repetitions do not buy the clean quantity
the objection imagines:** Bengio & Grandvalet (2004, JMLR) prove no unbiased estimator of k-fold CV
variance exists, and Nadeau–Bengio (2003) is a heuristic correction, not identification. The choice
is between two *conditional* quantities.

**Decision — freeze, for both the within-state and the cross-state claims.** One `split_seed` per
state, one frozen artifact, fail-closed; R indexes `model_seed`. The FL dose–response *requires* it
(§4c evaluates every dose on the same sealed folds).

**But freeze at `split_seed = 0`, not 42.** Every recipe choice was tuned at seed 42 — under the
corrected reading that means tuned on *partition-42 and init-42 jointly*, and the +3/+8 pp CA/TX
development-seed overshoot is the confounded symptom. Freezing partition 42 would make the
confirmatory partition the development partition. Partition `162efc6b2b4a` was never used for tuning,
and its `(split_seed=0, model_seed=0)` cell reproduces one legacy diagonal cell exactly, anchoring
§8's like-for-like comparison.

One amendment to §4b: if per-state SE_i omits the partition component, τ² absorbs it as spurious
between-state heterogeneity. Use the **confounded** legacy band for the seed term in SE_i², not the
narrower pure-replicate band the bridge will measure. The risk runs toward claiming less.

### 10.2 What replaces the lost partition variability

**Not the §3 bootstrap, and the protocol must never imply otherwise.** The bootstrap resamples
*evaluation users* within a fixed partition from fixed fitted models. Re-partitioning changes which
users trained the model, and refits. Orthogonal axes. A reviewer who says "your CI is tight but your
estimate would move under another split" is making a legitimate objection the CI cannot answer.

Three obligations wherever a within-state interval is published: the conditionality sentence names
the partition; the four-partition legacy bound (≤0.15 pp, below δ/2) is cited as measured
sensitivity; and §10.4 replaces "measured under confounding" with "measured in isolation, once".

### 10.3 R = 2 at the large states survives — *because of* the freeze

Under a frozen partition R indexes pure replicates, and the variance it averages is the optimisation
component alone — necessarily ≤ the confounded band §2 reasoned from. §2's argument holds a fortiori.
The tooling guard stands: no 2·SE band below R = 3 (t₀.₉₇₅,₁ = 12.706; 3.182 at R = 4).

One re-specification is mandatory: the bridge calibration gate must **re-measure** the band as a
*replicate* band (frozen `split_seed = 0`, `model_seed ∈ {0,1,7,100}`), not inherit 0.05–0.15 pp,
which is repetition-inclusive and now only an upper bound. The narrowed band may **not** shrink δ.

Had the protocol chosen repeated partitions, R = 2 would be incoherent: 1 df on the *larger*
variance, covering partitions in expectation while unable to quantify the coverage.

### 10.4 The decomposition — run it once

2×2 factorial at Alabama: `split_seed ∈ {0, 7}` × `model_seed ∈ {0, 7}`, three arms, 5 folds. The
bridge already produces the `split_seed = 0` column, so the increment is **30 small-state fits, a few
hours**. Prerequisite: the code separation in §10.5 — the decomposition is unrunnable in the current
CLI, which is the confound's signature.

Report the four paired deltas plus both axis movements. **Pre-registered rule:** if the partition
axis exceeds 0.15 pp, the freeze is unsafe and §2 reopens before any large-state fit; otherwise the
freeze stands and the measured component is quoted in §10.2 and folded into §4b. Declared limits: one
state, 1 df per axis, sign-and-magnitude only. "Declare-only" was rejected — 30 fits against a
270-fit package, and the enabling code change is required anyway.

### 10.5 What must be recorded

The confound survived because one field named `seed` meant two factors.

| Field | Content | Enforcement |
|---|---|---|
| `split_seed` | integer → `StratifiedGroupKFold(random_state=...)` | required; 0 per §10.1 |
| `partition_hash` | digest of the realised user→fold assignment | required; asserted against the frozen artifact, fail-closed — **the hash is ground truth, the seed is only the recipe** |
| `model_seed` | integer feeding `fold_seed`/`seed_everything` | required; the only factor R indexes |
| `fold_seed_rule` | derivation + `decorrelated_fold_seed` flag | required |
| `inner_split_seed`, `inner_partition_hash` | the §2 inner split | required wherever a checkpoint is selected |
| `repr_seed` | substrate build seed | unchanged |
| `band_over` | `model_seed` / `split_seed` / `confounded_legacy` | `stats.py` refuses to print a band without it |

`--seed` splits into `--split-seed` and `--model-seed`; `cell_id` embeds both; manifest validation
rejects a bare `training.seed`, so the single-knob shape cannot produce an accepted result.

**Amendments to the rest of the document:** §2 fold row (`split_seed` 42 → 0, hash pinned); §2
calibration gate (replicate band); §4b SE_i (confounded-band term); §8c (anchor-cell wording); §9.1
(partition named in the conditionality statement); pre-registration checklist.

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

## 12. Registered amendments

Applied here rather than silently, because a pre-registered document that changes without a record
is not pre-registered. Each entry says what moved, when, and why. §10.5 mandated the first two.

| Date | Amendment | Basis |
|---|---|---|
| 2026-08-18 | §2 fold row and the pre-registration checklist: `split_seed` **42 → 0**, `partition_hash` pinned, `model_seed` named as the separate factor. | §10.1/§10.5, which decided this and listed the edit as pending. |
| 2026-08-18 | **Romano–Wolf step-down deferred** for the within-family sweep (§5); Holm stands in its place until the sweep family is actually run. | Below. |
| 2026-08-21 | **§9.4 and §4b: the premise that California and Texas are untouched is FALSE.** Both were used for hyperparameter selection before this protocol existed. See §12.3. | `src/chapters/5_mobiwac/05_setup.tex:52-63`, the delivered text. |
| 2026-08-23 | **§12.5: four findings from the substrate/training review**, one of them a code correction (the joint selector's region operand), the rest declared. See §12.5. | Adversarial review of `substrate/`, `data/`, `train/` before closing v19. |
| 2026-08-23 | **Three reading notes, registered BEFORE the first confirmatory read.** They resolve what the frozen text left underdetermined; none of them changes a registered value. See §12.4. | Conformance audit of `eval/` against §1–§5, before `studies/v19_defence` stage 3. |
| 2026-08-24 | **§12.6: the §10.4 partition axis measured (discharging the §12.4c debt), the §4a overlap precondition failed, and three reporting decisions** — freeze certification moves from fit to read; the Bonferroni combining variant is adopted; the printed verdict column is the marginal one with `†`; "partition" becomes the word while `split_seed` stays the field. See §12.6. | `studies/v19_defence/S10_4_PARTITION_AXIS.md` + `S4A_USER_OVERLAP.md`, both run before the first confirmatory read (`studies/READ_LEDGER.json` absent at this commit). |

> **Onde mora a regra vigente.** O corpo §1–§11 é imutável; sete emendas o modificam, e a mais nova
> vence. Se você precisa de UMA resposta, procure aqui primeiro:
>
> | a pergunta | a resposta vigente |
> |---|---|
> | quantas réplicas em cada conjunto? | §12.7 — ponte 4, grandes **4** (o gate de licença reprovou em 24-08) |
> | qual receita de análise usar? | §12.7 — ponte: `v19_headline.toml`; grandes: `v19_headline_s4.toml` |
> | como o §4a combina os p? | §12.6c — **Bonferroni**, porque a precondição de sobreposição falhou |
> | que veredito vai na tabela? | §12.6d — o **marginal**, com `†` no que o Holm rebaixaria |
> | o eixo de partição entra no intervalo? | §12.6b — **não**; vai ao lado, e a certificação move do fit para a leitura |
> | como a banda da ponte é agregada? | §12.4b — pelo **máximo**, e §12.5b desconta réplicas de fluxo colidido |
> | qual o desenho do substrato? | §12.8 — 70/10/20, três sementes separadas |
| por que meu veredito saiu `seed-limited`? | §12.9 — o envelope é da ponte e pode ser 13× a banda do próprio conjunto; o diagnóstico `own_band` sai ao lado |
| a ponte é o jeito certo de decidir quantas réplicas? | §12.10 — **não**, e há substituto com literatura (*internal pilot*). Mas ele é v20: trocar a regra agora é pós-hoc |
> | Romano–Wolf? | §12.1 — adiado; Holm no lugar |
>
> ⚠ **12.2 e 12.4d NÃO são emendas** — registram o que foi considerado e mantido. Se você está
> procurando o que mudou, pule as duas.

### 12.1 Why Romano–Wolf is deferred, and what it costs

RW is more powerful than Holm precisely because it uses the cross-arm correlation, and it gets that
correlation from a **joint** resampling distribution: one per-user relabeling per replicate, applied
to all K+1 arm bundles, with all K statistics recomputed from it. The implemented layer resamples
**per comparison**, so the joint distribution RW needs does not exist yet — it is a change to the
resampling scheme, not a p-value adjustment bolted on afterwards.

What the substitution costs: Holm controls FWER under arbitrary dependence and is uniformly more
conservative, so every rejection Holm makes RW would also make. The loss is power, not validity, and
it falls on the *sweep* family — which no confirmatory run has yet produced. The headline family is
small and already Holm-corrected by design (§5).

Condition for lifting: before the first within-family sweep is analysed, either implement the joint
relabeling or restate the sweep's conclusions as Holm-conservative in the text. It may **not** be
lifted after seeing the sweep's p-values.

### 12.2 Not an amendment: the studentized permutation

Recorded because it was briefly proposed as one and should not be mistaken for a deferral. §3's
studentized sign-flip statistic (Chung & Romano 2013) **is implemented**, scaled by jackknife
pseudo-values. The unstudentized p-value is computed alongside as a diagnostic: for a paired
sign-flip the two agree to first order — the flip leaves the sum of squared per-user contributions
unchanged, so only the second-order centering term moves — and a visible gap between them therefore
means the linearization is straining and the interval should carry the claim.

### 12.3 California and Texas were never a reserve — what survives

**The factual error.** §9.4 assigns confirmatory weight to Istanbul/CA/TX "por nunca terem sido
estado de tuning", and §4b marks only FL/AL as development states. Both rest on a premise that the
delivered dissertation contradicts in writing:

Source: `articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex:52-63`, the delivered text. It
states the two knobs **separately**, and a comment in the same file records that the earlier
formulations — the table footnote's *"at every dataset"* and an "except California" — were **both
false** because they conflated the knobs. What the artifacts support:

| knob, dedicated category | coverage |
|---|---|
| **batch size** | searched at **all six**: five folds at IST/AL/AZ, fewer folds at FL and TX (CA's fold count is not stated) |
| **learning rate** | five folds at IST/AL/AZ, **single folds at Texas**; **not varied at Florida and California**, which carry the value the smaller searches selected |
| **joint model** | searched at IST/AL/AZ, screened at FL; **TX and CA carry a transferred configuration** |
| **dedicated region** | one configuration throughout, inherited |

So: **California had its batch size searched; Texas had both knobs searched.** Istanbul is the *most*
tuned of the three small datasets, not the least.

⚠ Do not cite the table footnote's "at every dataset" for this — it is a superseded formulation, and
citing it reintroduces the conflation the delivered text corrected.
- Istanbul's outer test was read on **2026-08-18** (`studies/porting_validation/SEALED_BRIDGE_READ.md`),
  a fact this protocol predates.

Under this document's own definition — a set stops being reserve the moment anyone sees it — **none
of the seven datasets is an untouched reserve except Jakarta**, which is not yet on disk.

**Why this is an amendment and not a correction.** The premise was false when written, not falsified
later. Editing §9.4 in place would leave no trace that the confirmatory-weight argument ever rested
on it, which is exactly what §12's opening rule forbids. The body stays as it was; this entry is the
record.

**What does NOT survive.**

- "CA/TX carry confirmatory weight because they were never tuning states" — the reason is false, so
  the weight does not follow from it.
- Any claim of the form "validated on datasets never used for any decision", for the six.

**What DOES survive, and it is most of the design.**

- **The sealed outer fold within each state.** The central correction of this protocol — selection
  and reporting on different data — is untouched by this error. It is about folds, not states.
- **The paired design.** Reuse bias attacks absolute numbers far more than paired deltas, and the
  headline is a paired Δ with TOST. Both arms of every comparison pay the same contamination.
- **The gatekeeping, the multiplicity control, the estimand definitions, the calibration gate.**
  None depends on the reserve premise.
- **A weaker but honest claim for CA/TX**: they were used for *hyperparameter selection*, not for
  recipe or architecture search, and the joint configuration was **transferred** rather than
  searched there. Less contaminated than AL/AZ/IST — not clean.

**The consequence for the next cycle.** A confirmatory claim about generalisation to untouched data
requires a dataset that is actually untouched. The pool exists (untouched Gowalla states, 14
unfetched Massive-STEPS cities); the choice must be committed **before** the substrate is built, and
the honest fallback when no suitable set exists — the large band cannot be replenished — is to weaken
the claim, not to relabel a used set.

**Timing.** Recorded before the first confirmatory read under this protocol
(`studies/v19_defence`, stage 3). No result influenced this entry; the trigger was reading the
dissertation's own footnote.

### 12.4 Three reading notes, registered 2026-08-23 — before the first confirmatory read

These are **notes, not amendments**: each resolves something the frozen text leaves
underdetermined, and none changes a registered value. They are dated here because the alternative —
deciding them silently while the reading runs — is what §12's opening rule exists to forbid. All
three were written before `mtlcheck compare` had ever been invoked; `studies/READ_LEDGER.json` was
empty at the time of this commit, which is checkable.

**Context.** A conformance audit of the implementation against §1–§5 found that three registered
rules were absent from code (Holm on the headline family, the S=2 escalation gates, the 90/95 split)
and that the verdict path read every interval at 95%. Restoring the registered behaviour is
conformance and needs no amendment. What follows is only the residue that the text does not decide.

#### 12.4a Holm and the co-primary claim are different families

§5 requires Holm within a state's headline family (2–3 tests); §3 requires the co-primary
intersection–union claim with **each component at full α** (Berger 1982). Both are registered, and
applied to the same two tests they disagree about the threshold for the weaker task.

**The reading adopted:** they are two different reporting objects, not one.

- The **marginal table** — each task claimed on its own — is the family of m = 2 under Holm.
- The **conjunctive headline** ("no measured cost" = reg NI ∧ cat superior-or-NI at the same
  checkpoint contract) is one claim, tested by intersection–union with each component at full α.

Within a chain, NI → superiority stays a fixed sequence at the chain's own level; a chain that
clears NI tests superiority at the level its NI was rejected at, spending no further α. The three
places Holm does **not** enter — inside a chain, across states, across co-primary components — each
carry a test in `tests/test_eval/test_headline.py`.

**Why this reading and not the other.** Correcting the co-primary components would charge
multiplicity for a conjunction, and a conjunction is already harder than either component alone —
the correction would be paid twice. Leaving the marginal table uncorrected would report two
independently-claimable wins at nominal α, which is exactly the family §5 names.

#### 12.4b The bridge band is aggregated by the maximum

§2 conditions S = 2 on a "calibrated paired seed sd" and says the calibration comes from the bridge,
but does not say how to combine the three bridge states into one number.

**The reading adopted:** per task, the **maximum** of the per-state replicate standard deviations.
Declared in the analysis recipe (`recipes/analysis/v19_headline.toml`, `[escalation]`), not in code,
so it is diffable. The maximum is the conservative choice: it makes all three gates fire more
readily, and a gate that fires costs fits, while a gate that fails to fire costs a verdict.

#### 12.4c The S = 2 calibration gate is verified retrospectively, and §10.4 is owed

Two ordering commitments were not met, and both are repairable only because the large states'
predictions are still sealed.

**The calibration gate.** §2 licenses S = 2 at FL/CA/TX *conditional on* the bridge calibration.
Its operational form: `sd/√2 ≤ δ/ratio`, with `ratio` declared in the analysis recipe (3.0). §2 writes
`⅓ × min(smallest effect of interest, TOST margin slack)` and never defines "smallest effect of
interest"; the reading adopted uses **the margin** as the effect scale, which is the quantity a
non-inferiority design actually has. `licences_two_replicates` in `eval/escalation.py` is that rule,
and `mtlcheck compare` REFUSES a non-bridge state at S = 2 without `--bridge-reading` — the ordering
is a refusal, not a procedure note.
The campaign trained those cells at S = 2 before any bridge reading existed — the manifest cites the
gate, but the gate had not run. The fits are sunk; the reading is not. **The gate is therefore
computed at the bridge reading and applied before the large states are read.** If it fails, seeds
{1, 100} are trained at the large states before their reading, which §7 already budgets as the
expected escalation. This ordering is the reason the reading is per state and bridge-first.

**§10.4.** The 2 × 2 factorial (`split_seed` × `model_seed` at Alabama, 30 small-state fits) has not
run: no cell with `split_seed = 7` exists on disk. Its pre-registered consequence is load-bearing —
"if the partition axis exceeds 0.15 pp, the freeze is unsafe and §2 reopens before any large-state
fit" — and §10.4 explicitly records that "declare-only was rejected". The debt is recorded here
rather than discharged by amendment, because amending it away would contradict a sentence written to
prevent exactly that. Author decision pending: run the 30 fits before the large-state verdicts, or
register a separate dated amendment accepting the legacy four-partition bound as substitute
evidence.

#### 12.4d Not an amendment: the sealed bridge read of 2026-08-18 is not recomputed

That reading was taken with every interval at 95%. Recomputing its six verdicts under the restored
90/95 split would be reinterpretation of a spent reading, not a correction, so it is not done.
`tests/test_eval/test_compare.py::test_no_banked_sealed_verdict_changes` pins those six verdicts
against the primitive they were produced with.


### 12.5 Four findings from the pre-closure review, 2026-08-23

An adversarial review of the substrate, data and training layers ran before closing v19. **Nothing
it found invalidates the 54 banked cells** — the seal, the one-checkpoint property, the user-disjoint
split and the substrate's causal edge were each verified, and two of them re-measured on the real
corpora rather than read off the code. What follows is what did not verify cleanly.

#### 12.5a The joint selector's region operand was the wrong lane — corrected, with zero effect measured

§1 registers the joint selector as `geom_simple = sqrt(cat_macroF1 × reg_Acc@10)`. The code used
`top10_acc_indist` — the in-distribution diagnostic — while the **dedicated** region arm already
selected on plain `top10_acc`. Two arms of the same headline comparison were choosing their
checkpoint by different quantities, which §1 forbids under "selection symmetry (mandatory)".

**Measured before deciding what to do:** recomputing both selectors over the banked per-epoch
inner-validation series of all 18 joint cells, the chosen epoch is **identical in all 90 folds**. The
deviation moved no banked number.

The code is now conformed to the registered operand (`train/scoring.py`, `train/runner.py`), with the
in-distribution lane kept and labelled as the diagnostic it is. `tests/test_selector_symmetry.py`
pins it — no test did before, which is how the asymmetry crossed a whole campaign unseen.

#### 12.5b The bridge replicates are partially correlated, and the band is now the conservative one

`seeding.fold_seed` is `seed + fold`, the reference contract. With 5 folds, replicates whose seeds
differ by less than 5 share random streams: at the bridge states, seeds **0 and 1 train 4 of their 5
folds from identical initial weights**. They are not independent replicates, and the standard
deviation between them understates the dispersion it is supposed to measure.

This matters precisely where §2 uses it: the bridge band licenses S = 2 at the large states, and an
understated band makes the gates fire less and the licence pass more easily.

**Scope, measured:** only the bridge is affected, and only the pair (0, 1). The large states run
{0, 7}, which do not collide. Fixing it in the banked cells would mean retraining; instead
`escalation.calibrate` now takes the **maximum** of the band over all replicates and the band over a
maximal stream-disjoint subset, and reports which replicates were dropped. Conservative in the
direction that matters, and no retraining.

The honest statement for the text: at the bridge, two of four replicates are correlated by the seed
rule; the licensing band is therefore reported as the conservative maximum, and the "2 seeds suffice"
argument rests on that maximum rather than on the naive spread.

#### 12.5c `train/stats.py` at R = 2 prints a band where §2 says refuse

§2's tooling guard: at `n_seeds < 3`, refuse the 2·SE band and print the two raw seed deltas plus the
verdict-shift result. The code prints a Student-t band instead, with the correct multiplier
(12.706 at R = 2) — wide enough that it almost never separates, so the direction is conservative. It
is also Tier B, on inner-validation values, and never carries a sealed verdict, which lives in
`eval/` with `escalation.py`. Declared rather than changed, because changing a diagnostic printer
days before the reading buys nothing.

#### 12.5d Istanbul's coverage number was wrong, and its "129 unexplained places" are explained

`REFERENCE_DEFECTS.md` stated that Istanbul's number covers 88.5% of check-ins. That figure subtracts
only the venues with no coordinate and omits the geometric discard; the correct figure is **~85%**.
Corrected there, with the arithmetic shown.

The same review closed the open question of the 129-place gap against the reference: it is a
**geometry-reader dependency**, not a defect of this code. The Istanbul GeoJSON holds 972 features, 8
of them MultiPolygon; the GDAL on the build machine read only the 964 Polygons. Re-running the join
elsewhere reproduces the reference exactly (29,816 places / 520 regions). The campaign is internally
consistent — all 12 Istanbul cells read one substrate identity — but the geometry file is **not
hashed in the manifest**, so a rebuild on another machine would silently differ. Hashing it is
recorded as owed work, not done before this reading.


### 12.6 The partition axis measured, the §4a audit failed — registered 2026-08-24, before the first confirmatory read

Two measurements this protocol prescribes had never run; both ran on 2026-08-23/24, against inputs
only. The §10.4 factorial ran on **internal validation** — the Tier-B quantity the 0.15 pp
threshold is written in; the new cells persist no predictions — and the §4a audit ran on the
**input corpora**. No outer-fold prediction was touched, `studies/READ_LEDGER.json` did not exist
at the time of this commit, and the git date is what proves the order. Sources:
`studies/v19_defence/S10_4_PARTITION_AXIS.md` (waves `s10_4_partition_axis.toml`, 6 cells / 30
Alabama fits / ~20 min, and `s10_4_axis_all_states.toml`, 32 of 36 cells before the author stopped
it) and `studies/v19_defence/S4A_USER_OVERLAP.md`. This entry discharges the §10.4 debt §12.4c
recorded as "author decision pending", by its first branch: the fits ran before any large-state
verdict.

#### 12.6a The axis, measured — and the rule/measurement separation

§10.4 pre-registered a 2×2 (`split_seed ∈ {0,7}` × `model_seed ∈ {0,7}`) to decide whether freezing
one partition is safe, and it had never run. It ran on 2026-08-23/24, on **internal validation**, the
quantity in which the 0.15 pp threshold is written; no outer-fold prediction was touched.

**The rule this amendment registers** — and the rule is the part that outlives the numbers:

1. the axis is train-side procedural noise. It is reported **beside** every interval, never folded
   into one (§9.1, §10.2), and the conditionality sentence names the frozen partition;
2. the 0.15 pp threshold is a **safety check**, not a claim. Firing on an unresolved estimate is the
   conservative side; "may be unsafe" is the honest state, not "is safe";
3. **every cycle re-measures on its own architecture.** The v19 numbers do not transfer — CV
   stability is a property of the learner, and inheriting a measurement from a different one is the
   defect §0.2 catalogues.

**The measurement itself lives in
[`../../studies/v19_defence/S10_4_PARTITION_AXIS.md`](../../studies/v19_defence/S10_4_PARTITION_AXIS.md)**
— four datasets, both axes, standard errors, and the "what if the axis entered the interval"
construction. It is dated and belongs to the study. It is **not** repeated here: a range that
circulated between copies already failed to reproduce once, and only a reviewer caught it before it
became text.

The one-line result, for a reader who needs it without leaving this page: the partition axis is a
**small-dataset phenomenon** — it crosses the threshold in region at both datasets under 2 200 users
and falls below it, with the sign inverted, at both over 10 000. It never flips the sign of the
effect.

#### 12.6b The consequence, transferred from fit to read

§10.4's pre-registered consequence reads "if the partition axis exceeds 0.15 pp, the freeze is
unsafe and §2 reopens **before any large-state fit**". The fits came first: all 54 cells were
trained and sealed before the factorial ever ran. The jurisprudence is §12.4c's, verbatim: **the
fits are sunk; the reading is not.** The consequence therefore attaches to the reading, and the
freeze certification is granted per dataset:

- **Not certified — Alabama and Arizona, region.** The trigger fired (0.366 and 0.306 against
  0.15). Neither estimate separates from zero at its own SE (1.29 and 1.76 sd) — but this is a
  safety rule, not a claim, and tripping on an unresolved estimate is the conservative side: the
  honest state is "may be unsafe", never "safe". Their region verdicts are still read; they are
  printed with the axis (value ± SE) beside the interval, and their conditionality sentence names
  the frozen `split_seed = 0` partition (per-state `partition_hash` as pinned) explicitly.
- **Certified — Florida and Istanbul, both tasks; category at all four measured datasets.** Below
  threshold — at FL/IST with SEs (~0.07) small enough for the certificate to mean something; at
  AL/AZ category with the caveat that SEs of 0.13–0.17 make it a noise-limited pass.
- **Extrapolated — California and Texas.** Unmeasured; their verdicts carry 12.6a's extrapolation
  sentence.

One option stays open and undecided, recorded in the study rather than adopted here: additional
partition columns (~20 min each at a small dataset) would take the axis from 1 to 3 df and the SE
from ~0.28 to ~0.16. §10.4 pre-registered `{0, 7}` and nothing more, so extra columns are extra
evidence on a safety check, dated when they run — not a change to the registered design.

#### 12.6c The §4a precondition failed — and what "six datasets" may claim

§4a made a user-ID intersection across the corpora a **precondition** of any cross-state statement
and pre-registered the remediation. It had never run. It ran on 2026-08-23, on the input corpora —
corpus user counts, a different universe from 12.6a's substrate counts (Alabama is 3 858 users in
the corpus, 1 101 eligible under v19 windowing; both are correct, for different denominators).

**The precondition fails, by a lot.** Between 37 % and 80 % of each US state's users appear in at
least one other state (AL 71.1 %, AZ 80.4 %, FL 45.1 %, CA 39.0 %, TX 37.2 %); of 80 875 distinct
people across the five states, 24.5 % appear in more than one; and counting users understates the
dependence, because travellers are more active than average — at Texas they are 37 % of the users
but **51 % of the check-ins**.

**Tested against the ETL-artifact hypothesis, and the hypothesis is discarded.** The state slices
share zero places (the cut is by place geography); exactly 5 duplicated `(user, instant)`
check-ins exist in ~9 million rows; and the case examined closely — 182 check-ins in Florida over
one week, then a single Alabama check-in on that week's last day — is unambiguously one person
travelling home. Gowalla users travel, as §4a's own sentence predicted; the ETL does not
duplicate.

**Istanbul is clean by construction, and the audit confirmed the construction, not the naive
count.** A naive intersection accuses 1 952 users "shared" between Istanbul and California. It is
**integer collision** between two independent identifier spaces (Massive-STEPS vs SNAP Gowalla),
not people; an audit that "finds" Istanbul overlap is measuring id collision.

**The pre-registered consequence is hereby adopted** — §4a's own cheap branch: the
partial-conjunction layer switches to the **Bonferroni combining variant**, with the overlap table
reported next to it. Zero GPU, paid in statistical power. (The other branch — assigning each
traveller to one state — would change the corpora and retrain everything, which the sunk seal
turns into a second reading.)

**And the larger consequence, which goes in the dissertation's text:** "replicated in six
datasets" is not six independent observations. The five US states are geographic slices of **one**
Gowalla population — and at the two small states, which are the bridge states, more than 70 % of
the users also appear in the larger ones. **Istanbul is the only genuinely independent dataset.**
This invalidates no within-state reading — each is conditional on that state's users, and the user
bootstrap resamples within it — but it bounds what the cross-state sentence may say, and the text
must say it before a committee member asks.

#### 12.6d The printed verdict column is the marginal one, with `†` for what Holm would downgrade

§12.4a separated the two reporting objects — the marginal table (per-task claims, Holm at m = 2)
and the conjunctive headline (intersection–union, each component at full α; §3, Berger 1982). It
did not fix which of the two a single printed verdict column shows, and the gap has a trap in it:
with both per-task p inside (0.025, 0.05), Holm rejects neither (min p > α/2) while both
components pass at full α — a naive table would print "cat indeterminate · reg indeterminate ·
joint headline YES", contradicting its own headline inside one row.

Registered: the verdict column of the published table is the **marginal** verdict — full α, from
the same 90 % two-sided interval whose lower bound is §3's one-sided 95 % NI bound, i.e. exactly
what the co-primary components use — with a **`†`** on every cell whose stand-alone claim Holm at
m = 2 would downgrade, and the Holm-adjusted reading stated in the caption. Why this way and not
the other: the headline is the co-primary conjunction, and by §3 its components are tested at full
α; a column printing post-Holm verdicts would flip cells the headline still counts, manufacturing
exactly the row-level contradiction above. The `†` keeps both halves visible — §3's dual-reporting
rule ("never suppress either half") applied to multiplicity. A `†` cell is claimable inside the
conjunction and not claimable as a stand-alone per-task win; the mark is what carries that
difference.

#### 12.6e "partition" is the word; `split_seed` stays the field — deliberately

`docs/NOMENCLATURE.md` §2 froze **partition** as the term for one complete division of users into
K folds. From this entry on, prose, the method guide and published tables use it — partition axis,
frozen partition, partition hash — where earlier text said "split" or overloaded "seed".

The configuration field, the parquet column and the `cell_id` segment **remain `split_seed`, on
purpose.** Renaming them would rotate every recipe's `science_fingerprint`; under the read-ledger's
identity rule the 54 sealed cells would stop matching the v19 recipe identity, and reproducing the
campaign would mean retraining the suite — a second reading of a sealed test, bought for a word.
The hash, not the name, is ground truth (§10.5); the vocabulary changes where vocabulary lives —
prose and tables — and nowhere a sealed artifact depends on.

#### 12.6f Four things the code wrote and never read — closed 2026-08-24

The §1 preconditions were stated in this document and enforced nowhere. Each of the four below had
the same shape: a field the writer persisted faithfully, that no reader ever consulted, so the
precondition held by luck and would have failed silently.

**Window pairing.** `window_id` has been in `predictions.COLUMNS` since the first cell was written,
and `eval/` never read it: the paired comparison intersected `userid` alone. A user's metric is a
sum over whatever windows that arm happens to carry, so two arms scoring different window sets
produce a delta over different denominators — with the partition hash, the fold guard, the replicate
guard and the seal all green. `compare._assert_paired_windows` now asserts the (fold, user, window)
sets agree, before any statistic is computed.

The campaign was audited rather than assumed: all six datasets, both dedicated arms, every replicate
— **54 of 54 cells agree**, including the eight California and Texas pairs checked on 24-08
(2 925 466 rows per California pair, 3 830 414 per Texas pair, identical on both sides). The guard
therefore rescues nothing in v19. It exists for the accidents that are actually plausible: a
partially-synced run directory, or a cell left behind by a superseded wave.

**Vocabulary.** §1 says "every compared arm's head covers the identical full vocabulary", and
`n_regions` / `n_categories` sat in the sidecar unread. Different catalogues give macro-F1 different
denominators and Acc@10 a different candidate set; `assert_comparable` now refuses the pair.

**The canary that could not fire.** A fold with no banked `train_labels` was *skipped* with a log
warning. §1 says the canary "fails the run" — and a canary that never ran is indistinguishable, in
the reported zero, from a canary that ran and found nothing. Under confirmatory reading it now
refuses; exploratory reading keeps the warning.

**The lock without the door.** `--exploratory` refuses sealed-but-unread cells by looking each one up
in the read ledger by scientific identity. A cell whose identity was unrecoverable — a v1 sidecar
whose `result.json` is gone — produced no identity, fell out of the filter, and printed. It is now
refused explicitly: without an identity there is no way to ask whether that dataset was already
spent.

**And the design that was the silent default.** A `[[cell]]` omitting `split_seed` gave each model
seed its own partition — the confounded design, where between-run spread mixes partition draw and
initialisation in one degree of freedom that no downstream analysis can separate. Four manifests in
`studies/porting_validation/` ran that way without saying so. The field is now **mandatory**:
`split_seed = 0` declares replicates on a fixed partition, `split_seed = "per-seed"` declares
repetitions. The four historical manifests are annotated with what they did; the annotation resolves
to the same value the old default produced, so no banked identity moves.

A third form, added the same day, makes the partition a first-class axis of a wave:
`partitions = [0, 7]` crosses with `seeds`. §10.4 asks for exactly that decomposition and, until
now, running it required a separate study with hand-written manifests — which is how it was in fact
measured (`studies/v19_defence/waves/s10_4_*.toml`). Manifest keys do not enter any recipe
fingerprint, so this costs nothing in banked identity; it is the one piece of the "partition"
vocabulary work that could be done after the campaign rather than never. The **field, the parquet
column and the `cell_id` segment stay `split_seed`** for the reason 12.6e gives, now measured: a
pure rename — changing no number at all — rotates every fingerprint, because `science_digest` hashes
`json.dumps(payload, sort_keys=True)` and the field names are the JSON keys. `joint-alabama-p0s0`
would move from `c696d8786ad2d938` to `ee017d90139bd26c`, and the 54 sealed cells recorded the
former.

### 12.7 The escalation the protocol ordered was unreachable in code — 2026-08-24

§2's calibration gate was computed at the bridge reading, as §12.4c requires, and it **failed for
region**: `sd/√2 = 0.2688 > δ/3 = 0.1333`, the band coming from Arizona (sd 0.3802 under the
disjoint-stream subset). §2's answer to a failed gate is "S=4 from the start", and §12.4c had
already budgeted seeds {1, 100} at the large states as the expected escalation. Both were followed.

The code could not express the outcome. An adversarial sweep found **two** refusals, not one, and
the second is the one nobody had looked at.

**There was no disk state in which the large states could be read.** With S=2, `gates.bridge_band`
refuses on the failed licence. With S=4 on disk, `gates.assert_replicates` — which runs *earlier* —
refuses first, because the frozen recipe pre-registers `florida = [0, 7]`: "florida tem réplicas
[0, 1, 7, 100] e o §2 registra [0, 7]". The 27 GPU-hours the gate ordered would have produced
exactly the cells the reader rejects. Neither guard had a single test; the campaign's most
consequential refusal was uncovered code.

**And the natural fix was a trap.** Escalating means changing `[replicates]`, which the recipe
header declares immutable — so it must be a new file, and a new file has a new fingerprint. But
`gates.bridge_band` compared that fingerprint by equality against the one stamped in the bridge payloads,
and the bridge is spent: rotating the hash makes three irreversible readings worthless, with no
second reading available. **Editing `recipes/analysis/v19_headline.toml` in place is therefore
vetoed permanently**, and the veto is now enforced: the frozen-artifact fixture recorded the string
`REFUSED:KeyError` for that file — the *name of an exception*, a value independent of the file's
contents — so nothing would have caught the edit. It now records the real fingerprint,
`a3e2854771f0868d`, cross-checked against all three payloads.

#### The escalation ladder

`recipes/analysis/v19_headline_s4.toml` is a new file that declares
`accepts_bridge_from = ["a3e2854771f0868d"]`. The predecessor stays frozen forever, as the recipe
that produced the bridge readings; the successor changes three things and nothing else — its name,
that key, and the three purchase-table lines. A `git diff` between them is eight lines, and the test
suite asserts every other section is byte-equal.

A declaration alone would be faith, so it is verified: `gates.assert_calibrates` also checks the three
inference parameters the payload carries — margin, levels, correction — against the current recipe.
A "successor" that moved δ and declared itself compatible dies there, on an axis the byte hash never
looked at. That axis is not hypothetical: **four one-token edits to this recipe turn today's refusal
into a licence** — `sd_aggregation = mean` together with dropping `folds` (0.1135 ≤ 0.1333),
`calibration_ratio = 1.45`, or δ = 1.0, which is a value already listed in `sensitivity`. Which is
why the exclusion list is minimal: only `[replicates]` and the labels sit outside the inference
identity. `[escalation]` in particular stays **inside** — it reads as design, but it is a decision
rule applied *after* seeing the bridge, and it holds the two cheapest levers in the file.

#### Two further conformance repairs, same day

**The licence is scoped to the question it asks.** It answers "does S=2 suffice?"; once the state
is at S=4 the question has no object, so the refusal now applies only below four replicates. The
guards keep their order — `gates.assert_replicates` still runs first and still proves the disk matches the
pre-registered set, which is what makes the scoping check cheap. Moving `gates.bridge_band` earlier was
considered and rejected: §12.4c says "before the large states are **read**", and both guards already
precede any reading; the move would only duplicate the per-arm replicate scan.

**A rehearsal reports instead of dying.** `--dry-run` passes `tolerante=True`, but the licence
refusal ignored it, so nobody could rehearse a large state to see whether the *rest* of it was in
order — precisely the check worth running before buying dozens of GPU-hours.

#### What this does not do

It does not re-read the bridge. Recomputing a spent reading under a new recipe was proposed and
rejected: §12.4d calls that reinterpretation, it would cost 3 states × 2 tasks × 10 000 bootstrap
resamples, and it buys no information — `replicates_by_state` is consumed in exactly one place, and
always for the state being read, so Florida's purchase table cannot move Alabama's numbers.

It does not derive the purchase table from code. That alternative was also rejected: it would leave
`git diff recipes/` reporting no change while the large states run at four replicates, trading a
fingerprint problem for a provenance lie. The tables stay in the file, where a reader can diff them.

### 12.8 The substrate definition this document rests on was one `git clean` from oblivion — 2026-08-24

§0 declares: *"**Substrate:** the sealed 70/10/20 outer-test / inner-val design of
`docs/future_works/evaluation_protocol_cleanup.md`. This document does not repeat that audit; it
completes it."* The path resolves to nothing in this repository, and the preamble's link to the same
file points at `https://example.invalid`.

The audit is not lost, but it is not safe either. It lives at
`docs/future_works/evaluation_protocol_cleanup.md` **in the reference checkout**
(`…/mestrado/ingred/`), 454 lines, sha256 `e479c7e00320ee80`, and it is **untracked** — absent from
git history, recoverable from no commit, one `git clean` from gone. A frozen protocol whose
foundational design is defined by an untracked file in another repository is not frozen.

Copying 454 lines here would trade one problem for another; the fix is to make this document
self-sufficient on the load-bearing part and cite the rest. **The design, quoted verbatim:**

| Role | Share of all users | Purpose |
|---|---:|---|
| outer test | 20 % | one-shot reporting only |
| inner validation | 10 % | checkpoint/epoch selection only |
| inner training | 70 % | fit the checkpoint-selection model |

> "One deterministic way to obtain the 10 % inner set is to run an 8-way `StratifiedGroupKFold` on
> the 80 % outer-development block and use one of its folds as validation: `12.5 % × 80 % = 10 %` of
> the full data. **The outer-split seed, inner-split seed, and model-initialisation seed must be
> separate fields.**"

That last sentence is the origin of `split_seed` / `inner_split_seed` / `model_seed` as three fields,
which `NOMENCLATURE.md` §1 later re-derived from measurement after the code had conflated two of
them. `splits.build_inner` implements the 8-way construction, and its docstring says the same thing.

The everything-else of that audit — the simulated row counts, the argument for keeping five folds,
the refit discussion — is context, not definition. It stays where it is, now identified by hash so a
future reader can tell whether the file they found is the file this cites.

### 12.9 The escalation envelope is 13× the band it audits — dual reporting, registered 2026-08-24 before the first large-state read

The §2 escalation gates audit each large-state cell against the **bridge** band (`sd_source = "bridge"`,
aggregated by the maximum). That band is measured on the three smallest datasets, and the three gates
inherit it even at S = 4. Recomputed with the project's own `escalation.calibrate` over the sealed
bridge payloads:

| | region | category |
|---|---:|---:|
| bridge band (max, disjoint-stream corrected) | 0.3802 | 0.1512 |
| gate (i) fires only if \|Δ\| > 2·sd | **0.7603** | 0.3024 |
| gate (ii) fires only if range > 3·sd·√2 | **1.6129** | 0.6415 |
| gate (iii) verdict-shift step, 2·sd/√S at S = 4 | **0.3802** | 0.1512 |
| — against the registered margin δ | 0.4 | 0.4 |
| Istanbul's own replicate band, for scale | **0.0286** | 0.0415 |

Two consequences, in opposite directions, and neither was anticipated when §12.4b registered the
maximum as the conservative aggregation.

**Gates (i) and (ii) go blind.** A genuinely defective replicate at Texas would need a 0.76 pp
deviation to trip the sign gate, or a 1.61 pp spread to trip the dispersion gate. The anomaly
detector that S = 4 was supposed to buy does not function under this envelope.

**Gate (iii) fires almost regardless of the data.** In region the shift step at S = 4 is 0.3802
against a margin of 0.4: a result *identical to Istanbul's* (Δ = −0.139, 90 % BCa [−0.201, −0.082],
non-inferior) slides to `inferior` on the down-shift and to `superior` on the up-shift. The gate
therefore fires, and §2's escalation rule stamps **"seed-limited at this margin, never resolved"** —
on a cell whose own dispersion is an order of magnitude smaller than the envelope being applied to
it. Category has a narrow escape window; region, at any decisive effect in the plausible range,
does not.

**What this amendment does, and what it deliberately does not do.** It changes no registered value:
not δ, not the levels, not the aggregation, not the gates, not their thresholds. The bridge band
remains the envelope, and the gate outcome remains what §2 says it is. Editing any of those after
seeing that the gate refused is precisely the post-hoc §12.7 catalogues — four one-token edits to
this recipe turn today's refusal into a licence, and that door stays shut.

**What it adds is a diagnostic.** From this entry on, every large-state reading reports, beside the
gate outcome, **the replicate band measured in that state itself** (S = 4, 3 df) and the ratio
between the envelope and it. The number decides nothing. It exists so that a reader who meets a
`seed-limited` stamp can see whether it came from the cell's own instability or from an envelope
imported from a dataset ten times smaller. This is §3's "never suppress either half" applied to the
envelope rather than to the verdict, and it is registered here — before any large-state test has
been read (`studies/READ_LEDGER.json` holds 36 entries, all AL/AZ/IST).

**What is owed to v20, and now has the data to be answered.** The bridge is a poor instrument for
calibrating datasets an order of magnitude larger, and this cycle's own numbers say so: Istanbul, the
largest bridge dataset, has the smallest band of the three — 11× smaller than Arizona's, which holds
the veto under maximum aggregation. The four-replicate bands that the escalation is measuring at
Florida, California and Texas right now are exactly the evidence needed to retire it. The options,
with the reasoning behind each, are in
[`../future_works/banda_da_ponte_transfere.md`](../future_works/banda_da_ponte_transfere.md);
§12.9 adds two to that list: **gate (iii) should take its step from the state's own band once
S ≥ 3**, and a bridge, if one survives, should contain the regime it claims to calibrate — the
cheapest large state (Florida, 4.4 h per replicate pair) calibrating the two expensive ones costs
less than the small-state bridge and measures the right regime.

**A note on what the bridge did not do**, because the opposite is easy to believe: it did not bias
any estimate — the band enters no estimator, and every large-state Δ comes from that state's own
paired user bootstrap. And it did not cause the 27 GPU-hours. Running S = 4 everywhere without a
bridge costs the same hours; running S = 2 everywhere has no defensible answer to "why is two
enough?". The bridge was the only mechanism that could have *avoided* those hours, and it declined
to.

### 12.10 The bridge has no precedent in ML, and a valid replacement exists — registered 2026-08-24

§2 licenses S = 2 at the large states against a replicate band measured on the three smallest
datasets and aggregated by the maximum. That construction was examined against the literature after
the gate refused, and three things came back.

**It has no name or precedent in machine learning.** Calibrating replicate counts on small datasets
to license fewer replicates on large ones, within the same study, appears to be a local
construction. The closest established analogue is in clinical trials — the **external pilot**, using
historical variance to size a new study — and there the criticism is published: **Browne (1995,
*Stat Med* 14:1933–1940)** shows that using a pilot's SD directly yields below-nominal power with
high probability, and prescribes the **upper confidence limit** instead of the point estimate;
**Schmidli, Neuenschwander & Friede (2017, *CSDA*)** give the formal meta-analytic-predictive
framework, which **models between-study heterogeneity** rather than assuming it away or resolving it
by taking a maximum.

**The maximum has no published critique because nobody uses it.** The literature uses a UCL or an
MAP prediction. Maximum aggregation is an ad-hoc conservatism with the known properties of neither,
and it hands the smallest dataset a veto over the largest — Arizona (2 136 users) dictating the
design of Texas (22 592).

**That literature's settled discipline is: external variance sizes the DESIGN; the ANALYSIS uses
internal variance.** The headline conforms — Tier A is the state's own user bootstrap, and the
bridge band enters no estimator. §12.9 records where it does not: the escalation gates apply the
imported envelope to large-state cells even at S = 4.

#### The replacement, for the next cycle

Adaptive-design theory separates adaptation on the observed **effect** — which needs group-sequential
machinery, pre-specified boundaries and α-spending — from adaptation on a **nuisance parameter**,
which is the ***internal pilot*** (Wittes & Brittain 1990; **Kieser & Friede 2000, *Stat Med*
19:901–911**, with exact type-I control). The **FDA (2019) adaptive-designs guidance** records that
nuisance-parameter-driven sample-size adaptation carries negligible type-I inflation and **requires
no α-spending**.

This project's peculiar constraint resolves in that direction: reading the outer test **spends** it,
irreversibly and on the record; reading between-replicate dispersion on the **inner validation**
spends nothing. So "run two, look, escalate" is invalid keyed on the outer delta and **valid** keyed
on inner dispersion, provided the rule is pre-registered before the cycle produces any number. The
design is written out in
[`../future_works/banda_da_ponte_transfere.md`](../future_works/banda_da_ponte_transfere.md).

#### Why none of this touches v19

The gate refused on 2026-08-24. Changing the rule after seeing it refuse — and standing down the
escalation because the new rule licenses what the old one denied — is the post-hoc §12.7 already
catalogues, one level up: not a one-token edit to the recipe, but a substitution of the whole
decision procedure, chosen after its answer was known. §12.9 already considered amending gate (iii)
before the large-state read and **declined**, preferring dual reporting; reopening that in the
direction the refusal made attractive would compound it.

The escalation therefore runs to completion as §2 ordered, and the four-replicate bands it produces
at Florida, California and Texas are the evidence the next cycle needs to retire the bridge on its
own numbers rather than on an argument.

#### And the larger question this defers

**Bouthillier et al. (2021, *MLSys* 3)** measure that data sampling is the **dominant** variance
source in ML benchmarks, with weight initialisation contributing less than half, and recommend
randomising as many sources as possible. This protocol freezes the partition and varies only
initialisation. It compensates — §3's user bootstrap carries the dominant axis, and §10.4 measures
the partition axis separately — but the residual point stands and is bigger than the bridge: the
entire S = 2 vs S = 4 dispute is fought over the axis that literature ranks least important
(0.05–0.15 pp), while the partition axis measured here, **+0.37 pp in region at Alabama**, is nearly
the size of δ = 0.4 and is reported *beside* the interval rather than inside it. A reviewer working
from that literature attacks there, not at S.
