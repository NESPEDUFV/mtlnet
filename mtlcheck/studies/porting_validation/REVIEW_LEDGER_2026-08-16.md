# Review de 2026-08-16 — o ledger dos achados

> **Documento de trabalho, com prazo de validade.** Existe para que a rodada de review não vire
> memória de conversa. Quando cada item estiver fechado, o que sobreviver vira entrada em
> `docs/REFERENCE_DEFECTS.md` (defeito no código de referência) ou em `PLAN.md` (defeito meu,
> corrigido), e este arquivo morre.

Cinco revisores independentes (Fable 5) sobre o port do substrato, a correção do S17, a inferência
do R16 e o experimento de círculo fechado. **35 achados.** Cada um passou por um refutador
independente; **15 dos 41 agentes morreram no limite semanal de tokens**, incluindo o sintetizador,
então 14 achados ficaram sem veredito e estão marcados abaixo. Os números vieram do
`journal.jsonl` do workflow, não do resumo.

## Estado em 2026-08-16, fim do dia

A **rodada 2** (19/19 agentes, sem falhas) julgou os 14 achados órfãos, auditou as correções e
procurou performance e qualidade. O que mudou desde a tabela abaixo:

| item | desfecho |
|---|---|
| `src/mtlcheck/data/` nunca versionado | **corrigido** — `data/` no gitignore casava em qualquer profundidade; 3 commits alegaram mudanças que não continham |
| `DataConfig.min_sequence_length` / `.stride` decorativos | **corrigido** — mesma classe do `repr_seed`, um commit depois; agora há teste que falha para *qualquer* campo não lido |
| cronômetros de fase sem `synchronize` | **corrigido** — mas a magnitude alegada (20×) **não reproduz**: o bancado já contabilizava 95,5 % do wall; agora 99,8 % |
| "o laço é launch-bound, o lever é CUDA Graphs" | **falso aqui** — 98–100 % de utilização medidos; conclusão herdada da referência sem medir |
| tolerância do C4 | **corrigida** — banda pareada por seed; a coluna errada saiu do PLAN porque o dado da referência por fold não existe |
| guard de vazamento lia um dict do chamador | **corrigido** — verifica o `edge_index`; recusa flag e dados em desacordo nos dois sentidos |
| divergência do nível de região | **FECHADA** — 5 builds de cada lado: distribuição cruzada em cima dos pisos próprios; inflação de norma **refutada** (−0,5 / −1,0 / +1,2 %) |

Ainda abertos e ranqueados: CLI `check2hgi build` é stub (as correções não protegem chamador
nenhum), manifesto registra determinismo pedido e não obtido, mapas lugar→região não persistidos
(a torre de região cai de volta no repo de referência), e o arm de 25 épocas não tem config
arquivada.

**Regra de leitura:** um achado sem veredito não é um defeito confirmado. Vários que verifiquei à
mão eram reais; outros podem não ser. O que está marcado CORRIGIDO foi verificado por mim antes de
mexer no código — em dois casos por mutação, que é a única prova de que um teste morde.


---

## Corrigidos nesta rodada

| # | sev | claim | achado | status |
|---:|---|---|---|---|
| 1 | critical | C3 | Port accepted on an n=1 'floor' it actually sits outside of, on every level and every statis… | PARCIAL |
| 4 | major | C1 | One-shot export has no forward-only guard — a bidirectional build silently writes leaked inp… | CORRIGIDO ⚠sem veredito |
| 7 | major | C2 | The within-band uniformity assertion in the S17 distribution test is vacuous — even total co… | CORRIGIDO |
| 13 | major | C3 | R16's 'the port's distance is the reference's self-disagreement' overstates a single-pair fl… | CORRIGIDO |
| 15 | major | C3 | C3's headline — 'port-vs-reference distance equals the reference's self-distance' — overstat… | CORRIGIDO ⚠sem veredito |
| 16 | major | C4 | The rule 'substrate rebuild noise = 0.18 pp; any margin below is inside build noise' is a ra… | CORRIGIDO |
| 17 | major | C4 | The two arms are not the same procedure, and the own builds reach systematically lower prete… | CORRIGIDO (doc) ⚠sem veredito |
| 18 | major | C4 | The 0.18 pp 'build noise' bar generalizes a 3-sample, one-state, category-only range to all … | CORRIGIDO ⚠sem veredito |
| 20 | major | cross-cutting | Parameter-count evidence (826 827) contradicts the closed-loop substrate's manifest (827 083… | CORRIGIDO ⚠sem veredito |
| 23 | minor | C1 | spatial.py range guards admit negative placeids — np.clip maps them onto place index lookup[0] | CORRIGIDO ⚠sem veredito |
| 24 | minor | C1 | next_region_table's '-1 is asserted' is enforced only incidentally, through a dict-miss two … | CORRIGIDO ⚠sem veredito |
| 32 | minor | C4 | The '~0.18 pp build-noise margin' rule generalizes a range of three seed-means at one state,… | CORRIGIDO ⚠sem veredito |
| 33 | minor | C4 | PLAN.md contradicts itself on whether the materializer is ported | CORRIGIDO ⚠sem veredito |

---

## Abertos

| # | sev | claim | achado | status |
|---:|---|---|---|---|
| 2 | major | C1 | Conclusion uses the unpaired between-fold std (~1.2 pp) as its noise yardstick although the … | ABERTO |
| 3 | major | C1 | The 25-epoch trajectory arm cannot have run the production Alabama objective, and its config… | ABERTO ⚠sem veredito |
| 5 | major | C2 | Default gate removal changes the large-state objective while all validation evidence lives w… | ABERTO |
| 6 | major | C2 | 'Fixing was the right call' is argued without measuring what hard negatives do to anything | ABERTO |
| 8 | major | C3 | Row-mean cosine is scale-invariant and the port's own evidence shows an unexamined systemati… | ABERTO |
| 9 | major | C3 | The seed floor (cos 0.089) establishes no acceptance scale — and the loss numbers contradict… | ABERTO |
| 10 | major | C3 | R16 experiment is unauditable: the generating script is not versioned and the JSON omits eve… | ABERTO |
| 11 | major | C3 | Attribution to 'the three scatter/index_add of the two pools and the decoder' is asserted, n… | ABERTO |
| 12 | major | C3 | The determinism 'fix' is warn_only, leaks process-global state into downstream code, and can… | ABERTO |
| 14 | major | C3 | Manifest records requested determinism, not achieved determinism; the guarantee itself is wa… | ABERTO ⚠sem veredito |
| 19 | major | C4 | C4 uses the per-fold deviation (~1.2 pp) as the noise scale for comparing 5-fold MEANS — the… | ABERTO ⚠sem veredito |
| 21 | minor | C1 | The port's new hard-negative machinery is never executed inside a full forward by any test, … | ABERTO ⚠sem veredito |
| 22 | minor | C1 | _transplant discards the reference's `checkin2poi.scale` buffer without checking it equals t… | ABERTO |
| 25 | minor | C2 | Distribution-equivalence test compares the port to a transcription of the reference loop, no… | ABERTO |
| 26 | minor | C2 | Band cache is never invalidated and forward() silently tolerates a missing similarity matrix | ABERTO |
| 27 | minor | C3 | Determinism verification horizon, config and scaling are unrecorded; +12.5% wall is an Alaba… | ABERTO |
| 28 | minor | C3 | enable_determinism uses warn_only=True, so the 'deterministic by default' guarantee can sile… | ABERTO ⚠sem veredito |
| 29 | minor | C4 | 'The whole chain from raw corpus' is overstated: the region hierarchy AND the POI2Vec/Delaun… | ABERTO |
| 30 | minor | C4 | The headline experiment is not reproducible from its own artifact: no probe seed, fold seed,… | ABERTO |
| 31 | minor | C4 | Verified sound: the category probe is clean, and dropping the 576 vestigial columns from nex… | ABERTO |
| 34 | minor | cross-cutting | The rebuild-noise yardstick (0.18 pp) conflates seed sensitivity with build noise now that d… | ABERTO |
| 35 | minor | cross-cutting | The banked port-vs-reference build comparison appears to predate the vectorised sampler | ABERTO |

---

## Os que mais custam, em detalhe

### 1 · Port accepted on an n=1 'floor' it actually sits outside of, on every level and every statistic

**critical** · afeta C3 · `docs/REFERENCE_DEFECTS.md §R16 (table at lines 381-389); studies/porting_validation/evidence/{rerun_floor.json,build_compare.json}` · **PARCIAL**

> piso medido (n=5) confirma o achado; a CAUSA da divergência em região segue aberta

**Defeito.** The key inference — 'the distance between the two implementations is practically the reference's distance to itself' — rests on a single rerun pair (n=1, no variance estimate), and the port is consistently OUTSIDE that floor: in 1−cos terms the port is 1.23× the floor on check-in (0.00675 vs 0.00548), 1.30× on place (0.00455 vs 0.00349), and 1.86× on region (0.02128 vs 0.01143); cos_min on region is 0.9567 vs the floor's 0.9778 (2× the gap) and RMS 0.176 vs 0.137. Every number points the same direction, which is the signature of a systematic difference, not noise — yet the docs round this to 'praticamente a distância da referência a si mesma'. With one floor sample there is no way to say whether 1.9× the floor is inside the rerun distribution, and the only downstream check that could rescue the region level (a region or joint cell trained on a port-built substrate) was never run — PLAN.md §5 item 2 admits it, while STATE.md line 39 says the dissertation's central conclusion is about region.

**Como falha.** A systematic port defect that perturbs region embeddings at the observed magnitude (e.g., a subtly wrong PReLU/GCN interaction or adjacency handling in POI2Region) produces exactly this evidence pattern — cos ~0.98, 'comparable to the floor' — and is signed off. The region tower and joint model then consume systematically different region geometry, and the dissertation's central region-task conclusions are validated against a substrate that does not match the reference, with the acceptance argument structurally unable to detect it.

**Correção proposta.** Generate a proper floor distribution: N≥5 reference reruns (cheap: ~2 min each on the A40 per build_compare.json) and report the port's distance as a quantile of that distribution, per level. Independently, close the region gap with the decisive test: build the substrate with the port, run the region and joint cells, and compare against the same cells on a reference-built substrate — the category-only closure does not transfer to the axis the thesis is about.

### 2 · Conclusion uses the unpaired between-fold std (~1.2 pp) as its noise yardstick although the design is fold-paired, understating a consistent +0.13 pp offset

**major** · afeta C1 · `studies/porting_validation/PLAN.md:211-216 + evidence/substrate_sensitivity.json` · **ABERTO**

**Defeito.** All four arms share the identical StratifiedGroupKFold split (fold-profile correlations with the banked arm are 0.974/0.988/0.993), so the comparison is paired, but the PLAN judges the +0.13 pp mean-to-banked distance against the ~1.2 pp between-fold deviation. The correct paired scale is the SE of per-fold differences (0.09-0.15 pp per substrate) and the SE of the three rebuild means (0.099/sqrt(3)=0.057 pp). Against that scale the offset is t=2.28 (df=2), with 3/3 rebuild means above banked and 11/15 fold-level paired diffs positive. 'Both below the between-fold deviation, therefore the chain reproduces the banked number' is a ~10x-inflated acceptance criterion: it would equally have blessed a 1.0 pp systematic error, and it converts 'not refuted at n=3, with borderline evidence of a small positive systematic offset' into 'reproduces within noise'.

**Como falha.** A port defect that systematically shifted category macro-F1 by +0.5 pp on every fold would pass this test as stated ('below the 1.2 pp fold deviation'), while the paired analysis available in the same JSON would have flagged it at ~5 SE. Concretely today: the small positive offset (all 15 own-vs-banked comparisons trend up, mean +0.13 pp) is declared noise without the test that could distinguish it, so a real systematic difference between the port's substrates and the banked one may be being absorbed into the reproduction claim.

**Correção proposta.** Redo the inference with the paired structure: per-substrate paired t over the 5 fold diffs, plus the one-sample comparison of the 3 rebuild means to the banked value using SE=sigma/sqrt(3). State the result as an equivalence bound ('offset is +0.13 +/- 0.06 pp; effects above ~0.3 pp are excluded'), not as 'reproduces within noise'. Add 3-5 more substrate seeds if the offset needs to be resolved.

### 3 · The 25-epoch trajectory arm cannot have run the production Alabama objective, and its configuration is not archived

**major** · afeta C1 · `studies/porting_validation/PLAN.md:171 (mtlcheck); ingred Check2HGIModule.py:990-999 vs mtlcheck src/mtlcheck/substrate/model.py:266-281` · ⚠ **sem veredito independente** · **ABERTO**

**Defeito.** The strongest dynamic evidence for C1 — '25 epochs on real Alabama, identical to ~epoch 10, max|delta| 8.3e-05 at 25' — is only achievable with the p2r hard-negative branch disabled (or negatives injected) on both sides. With the branch live, the reference consumes RNG via a per-row Python loop drawing `torch.randint(len(candidates),(1,))` with no device argument (CPU generator) while the port draws two vectorized device tensors; the negative indices diverge at step 1 and a ~25% resample of ~11 848 places' p2r negatives moves the epoch-1 loss by O(1e-3), not 8.3e-05. But Alabama IS a hard-negative state under BOTH the reference gate (11 848 < 50 000) and the port default (gate=None). So the trajectory evidence covers an objective that neither side actually trains at Alabama. Unlike every other arm (rerun_floor.json, build_compare.json, ...), this arm has no evidence JSON and no archived script — the number exists only in PLAN.md, and the disabling of the branch is not disclosed there.

**Como falha.** A bug in the interaction between the vectorized hard-negative sampler and training — e.g. the `self._band` CSR cache being built once from a wrong/mutated similarity tensor, or a device mismatch that only appears when `_sample_region_negatives` runs on CUDA inside a real forward — produces a silently different substrate at AL/AZ/IST (the paper's hard-negative states) while every C1 test and the trajectory arm stay green, because none of them ever runs the hard branch inside a training forward.

**Correção proposta.** Re-run the trajectory arm with hard negatives ON and identical negatives injected per epoch (the same trick test_hard_negatives_reach_the_loss_identically uses), archive the script + JSON under evidence/, and annotate PLAN.md line 171 with the arm's exact configuration.

### 4 · One-shot export has no forward-only guard — a bidirectional build silently writes leaked input tables

**major** · afeta C1 · `/Users/vitor/Desktop/mestrado/mtlcheck/mtlcheck/src/mtlcheck/substrate/export.py:45-78 (write); config.py:66 (forward_only knob); docs/SYSTEM_MAP.md ~line 198-202` · ⚠ **sem veredito independente** · **CORRIGIDO**

> guard em `export.write`; recusa build não-forward-only

**Defeito.** export.write performs the one-shot full-graph readout unconditionally. Its own docstring states "Under a bidirectional graph the two would differ and this export would be wrong", and SYSTEM_MAP records that the reference's materialize_from_insample.py hard-fails on bidirectional arms and that "esse guard tem que sobreviver" — but write() never checks config.forward_only, graph_summary["forward_only"], or anything else. graph.build(forward_only=False) exists and SubstrateConfig(forward_only=False) constructs without complaint (__post_init__ validates only dim and encoder). The reference guard did not survive the port.

**Como falha.** Anyone builds a diagnostic/ablation substrate with forward_only=False (the config field exists precisely because the reference study had such arms). write() one-shot-encodes the full graph, so every history visit's vector is convolved over its successor — including the window's target. next.parquet then carries the target's identity into the features, the category cell scores ~56.9 instead of ~28.2 macro-F1 (the measured 28.63 pp leak the whole v18 protocol exists to remove), and the arm reads as a spectacular substrate improvement. Nothing raises; the manifest even records forward_only=False as if it were a benign switch.

**Correção proposta.** In export.write, hard-fail unless the graph the run was trained on was forward-only (pass the CheckinGraph or check graph_summary["forward_only"] is True), with an explicit override name like allow_leaky_export_for_diagnostics=True if bidirectional arms are ever needed. Mirror the reference's guard, which the docs already say must survive.

### 5 · Default gate removal changes the large-state objective while all validation evidence lives where the gate never bites

**major** · afeta C2 · `src/mtlcheck/config.py:98 (p2r_hard_neg_size_gate=None default); docs/OPTIMIZATIONS.md P10 (lines 80-81); studies/porting_validation/PLAN.md line 37` · **ABERTO**

**Defeito.** The port bundles two separable decisions and documents them as one: (a) vectorising the hard-negative draw (pure performance, correct) and (b) flipping the default so hard negatives run at every state (a change of training objective at FL/CA/TX relative to every banked artifact). OPTIMIZATIONS.md P10 states 'a correcao de performance e a correcao cientifica sao a mesma' — they are not: the CSR sampler serves either default at identical cost, so keeping the faithful gate as default was free. Meanwhile every piece of equivalence and loop-closing evidence (C1 weight transplant, C4 chain closure, the R16 floor argument, build_compare.json) was collected at Alabama, where the gate does not bite — the changed default is exercised by zero validation evidence. The project's own plan (PLAN.md roster includes FL/CA/TX; task list: 'fechando com FL ou CA') will build large states next, and PLAN.md never mentions S17 or the gate.

**Como falha.** Operator runs the planned closure at Florida with the default recipe, scores the substrate through the downstream cell, and compares to the banked FL number — the delta now conflates three things: port fidelity, build noise (0.18 pp, measured only at AL), and an objective change whose downstream magnitude nobody has measured. A mismatch gets read as 'the port is broken'; a coincidental match gets read as fidelity. The C3-style defense ('port-vs-reference distance equals the reference's self-disagreement') is structurally unavailable because the two sides no longer optimise the same loss. Either reading is a wrong scientific conclusion, and the manifest field only helps someone who already knows to look.

**Correção proposta.** Separate the two decisions: ship the vectorised sampler with the v18-reproduction recipe TOML pinning p2r_hard_neg_size_gate=50_000 (faithful by default for the engine identity that is validated against banked artifacts), and expose gate=None under a distinct recipe/engine name for forward work. Additionally add a guard in the scoring/compare path that refuses (or loudly warns) when a substrate whose manifest says region_hard_negatives=true at >=50k places is compared against banked v18 cells.

### 6 · 'Fixing was the right call' is argued without measuring what hard negatives do to anything

**major** · afeta C2 · `docs/SYSTEM_MAP.md S17 (lines 297-333); docs/REFERENCE_DEFECTS.md R15 (lines 317-355)` · **ABERTO**

**Defeito.** The justification for removing the gate measures band occupancy (20-27%), candidate coverage (no region without a candidate), and cost (72us x 42,286 = 3.1 s/epoch) — i.e., that the mechanism is well-defined and cheap everywhere. It never measures the EFFECT of the hard-negative objective on anything: not downstream F1, not loss geometry, not embedding structure, at any state. The C4 harness plus the measured 0.18 pp build-noise floor made the decisive experiment cheap: build one Alabama substrate with hard negatives OFF (one config change, a 16 s build) and score it through the same 5-fold cell. That single A/B would quantify the objective term against the noise floor and either validate S17's confound reading of the banked results ('large states' worse region axis may be the missing hard negatives') or show the whole fix is downstream-inert, in which case the faithful default costs nothing. Neither was run.

**Como falha.** If hard negatives are downstream-inert at the 0.18 pp scale, S17's headline framing ('small and large states are not trained by the same objective', 'a state-size effect and an objective change are confounded in the banked artifacts') overstates a distinction without a measurable difference, and readers discount banked cross-state comparisons for no reason. If they are NOT inert, the default flip silently shifts every future large-state number by an unquantified amount. Both branches are live because the one experiment that separates them is missing.

**Correção proposta.** Run the gate-on/gate-off A/B at Alabama (and ideally one large state once buildable) through the existing substrate_sensitivity harness; report the downstream delta next to the 0.18 pp floor in S17/R15. This either upgrades the confound claim to a measured effect or downgrades the fix to a documented no-op.

### 7 · The within-band uniformity assertion in the S17 distribution test is vacuous — even total concentration on one region passes

**major** · afeta C2 · `tests/equivalence/test_substrate_model.py:384-387 (and 297-311)` · **CORRIGIDO**

> chi² contra uniforme; as 2 mutações citadas agora falham

**Defeito.** The test's third claimed property ('the choice within a band is uniform') is asserted as `share.max() < 8.0/reachable`. With reachable ≈ 14 regions the threshold is 0.57, while the in-band mass at 25% hard-rate plus accidental uniform in-band hits (~29% of rows) caps any single region's share at ~0.47 even if EVERY hard draw landed on the same region. A sampler that always picked the first CSR candidate (`candidates[offsets[positives]]`, i.e. dropping `+ within`), or that truncated the last candidate (`draw*(counts-1)`), passes all three assertions: the rate matches (still in-band), band membership holds, and the positive is still excluded. Additionally, the comparison baseline `_reference_hard_negatives` is a transcription of the reference loop written inside the test file — the reference's actual `_sample_negative_indices_with_similarity` hard path is never executed anywhere in the substrate test suite (the exact arms gate it off via min_batch=0, the injection test monkeypatches it away).

**Como falha.** An off-by-one or indexing bug in the CSR draw (`offsets[positives] + within`) that systematically biases which similar region is chosen would ship undetected; every substrate built by mtlcheck would train against a skewed hard-negative distribution, changing the p2r objective at all six states while the S17 'fixed and verified' claim stands.

**Correção proposta.** Replace the max-share check with a per-positive-region chi-square (or exact multinomial) test of the drawn candidate against uniform-over-band, and drive the reference's real method (constructed with a large min_batch) as the loop baseline instead of a transcription.

### 8 · Row-mean cosine is scale-invariant and the port's own evidence shows an unexamined systematic +10.5% region-norm inflation

**major** · afeta C3 · `studies/porting_validation/evidence/build_compare.json (scale_ref/scale_mine fields); docs/REFERENCE_DEFECTS.md §R16` · **ABERTO**

**Defeito.** build_compare.json records scale_ref vs scale_mine: check-in 1.0637→1.0927 (+2.7%), place 0.7224→0.7569 (+4.8%), region 0.5465→0.6041 (+10.5%) — the port's embeddings are larger on all three levels, same sign everywhere, i.e. a systematic effect. The headline acceptance metric (per-row cosine averaged over rows) is invariant to exactly this kind of difference, and rerun_floor.json contains no scale fields, so there is no evidence the reference's self-rerun exhibits comparable norm drift. This is precisely the 'two systematically different embeddings at cos 0.99' failure mode: the metric chosen for the equivalence verdict cannot see the one systematic difference the evidence already recorded. Downstream heads consume raw (unnormalized) embedding columns via the materializer, so norm shifts are not automatically absorbed.

**Como falha.** The reference rerun shows no scale drift (plausible: same kernels, chaotic but unbiased), while the port's +10.5% region-norm inflation comes from a real implementation difference (e.g., different effective initialization interaction, PReLU channel handling). The cosine table declares equivalence; downstream region-tower training on port-built substrates behaves measurably differently (effective learning-rate/regularization shifts with input scale), and cross-implementation comparisons of region cells silently carry an uncontrolled variable.

**Correção proposta.** Add scale (and per-dimension distribution) statistics to the rerun-floor measurement so drift has a floor too; either explain the +10.5% mechanistically or treat it as an open discrepancy. Complement row-cosine with a scale- and rotation-sensitive metric (linear CKA, Procrustes residual) computed for both the rerun pair and the port pair.

### 9 · The seed floor (cos 0.089) establishes no acceptance scale — and the loss numbers contradict the floor/ceiling ordering

**major** · afeta C3 · `docs/REFERENCE_DEFECTS.md §R16 lines 385-389; studies/porting_validation/evidence/seed_floor.json vs rerun_floor.json` · **ABERTO**

**Defeito.** The 'separate universe' framing (port at 0.99 vs seed-to-seed at 0.089) is vacuous: independently seeded 64-dim contrastive embeddings are rotation/sign-arbitrary, so near-zero cross-seed cosine is generic — ANY port sharing init and early trajectory with the reference, however wrong afterwards (wrong loss weights, missing detach, wrong band), would clear that bar. It provides zero discriminative power between 'equivalent port' and 'systematically different port'. Worse, the auxiliary loss argument ('best loss ref 0.2349 / mine 0.2328 against 0.0031 dispersion across three seeds') uses the seed dispersion as the yardstick when the evidence's own same-seed rerun spread on best loss is 0.0085 (0.2236 vs 0.2321, and 0.2308 for seed 42 in seed_floor.json — a 0.0113 range across the four recorded seed-42 runs), i.e. same-seed reruns disperse MORE than different seeds on this metric. The floors and ceilings are not ordered, which means single-run best-loss comparisons carry no information, yet one is presented as supporting evidence.

**Como falha.** A reviewer (or the author in three months) reads the three-row table as 'port distance ≈ self distance ≪ seed distance, therefore equivalent'. The middle inequality is doing all the work and is false at region level (finding 1), while the outer inequality is true for any port whatsoever — the table structurally manufactures confidence. Any future port change that breaks equivalence but preserves init would pass the same table.

**Correção proposta.** Drop the seed row from the acceptance argument (keep it as context only). Replace the best-loss comparison with a distribution: best loss over N deterministic reruns of each side, or remove it. State explicitly which comparison bears the acceptance decision and what its rejection threshold is.

### 10 · R16 experiment is unauditable: the generating script is not versioned and the JSON omits every condition needed to check confounds

**major** · afeta C3 · `studies/porting_validation/evidence/rerun_floor.json; evidence/README.md` · **ABERTO**

**Defeito.** The repo versions the OUTPUT of the two-runs experiment but not the script, seed, epoch count, torch/CUDA versions, GPU state, CUBLAS_WORKSPACE_CONFIG value, process design (both runs in one process vs two), or per-epoch loss curves (only summary deltas). evidence/README.md justifies versioning the JSONs as eliminating 'roda de novo para conferir', yet without the script nothing can be re-run or checked. What CAN be verified from the JSON: loss_delta_epoch_1 = 0.0 with identical losses through epoch 4 proves init and RNG streams were identical (reseeding was done correctly) — so numeric non-reproducibility under the conditions used is genuine. What CANNOT be excluded: in a shared process, run B executes under different heap/workspace fragmentation than run A, and with CUBLAS_WORKSPACE_CONFIG unset cuBLAS algorithm/reduction selection is a legitimate alternative divergence source to scatter atomics; cudnn.benchmark state and whether the model/data objects were rebuilt (GCNConv(cached=True) buffers) are likewise unrecorded, only inferrable. first_epoch_where_the_loss_differs=5 is presumably float equality on item() values, but the absent curves make even that unverifiable.

**Como falha.** Someone re-runs the reference twice in separate processes with CUBLAS pinned and gets bit-identical curves — the headline 'the reference is not reproducible against itself' then needs the qualifier 'within one process, cuBLAS unpinned', and every claim calibrated against the 0.9945 floor (including the port's acceptance) inherits the ambiguity. Nobody can check, because the experiment exists only as its own output.

**Correção proposta.** Version the runner script alongside the evidence; extend the JSON with seed, epochs, versions, device, process design, CUBLAS state, and the two full loss curves. Re-run once as two fresh processes to close the shared-process confound.

### 11 · Attribution to 'the three scatter/index_add of the two pools and the decoder' is asserted, not demonstrated, and the op list is wrong

**major** · afeta C3 · `docs/REFERENCE_DEFECTS.md §R16 lines 368-370; src/mtlcheck/substrate/training.py:14-17` · **ABERTO**

**Defeito.** The determinism on/off flip (determinism.json: default diverges at epoch 4, deterministic max|Δ|=0.0) demonstrates only that the cause lies in the union of everything torch.use_deterministic_algorithms(True) + CUBLAS_WORKSPACE_CONFIG touches — dozens of op classes flipped at once. The specific causal story stated as fact in two documents ('the three scatter/index_add of each forward — the two attention pools and the reconstruction decoder') was never isolated and undercounts the candidate sites: each forward also runs scatter-add aggregation inside every GCNConv (2 encoder layers, the place GCN, the region conv — each twice, for the positive and corrupted passes), scatter-max/sum inside segment_softmax, and the nn.Embedding (place_table) backward, which uses CUDA atomics. cuBLAS matmul nondeterminism (workspace unpinned in the default arm) is also inside the flipped set. A one-line discriminating experiment — set CUBLAS_WORKSPACE_CONFIG alone, leave deterministic algorithms off — would separate cuBLAS from atomics; per-site isolation (deterministic mode with one op swapped back) would pin the site. Neither was run.

**Como falha.** Someone optimizes based on the stated mechanism — e.g., replaces only the two pools and the decoder with sort-based deterministic reductions to recover the 12.5% wall cost while keeping 'the' determinism — and ships a build that still diverges run-to-run through the GCN aggregations or the embedding backward, with the manifest claiming determinism.

**Correção proposta.** Either soften both documents to 'atomics-based reductions somewhere in the forward/backward, jointly with possible cuBLAS effects' or run the cheap discriminating experiments (CUBLAS-only arm; fresh-process arm) before naming the ops.

### 12 · The determinism 'fix' is warn_only, leaks process-global state into downstream code, and can record deterministic:true while cuBLAS is unpinned

**major** · afeta C3 · `src/mtlcheck/substrate/training.py:99-121; src/mtlcheck/cli.py:57; src/mtlcheck/substrate/export.py:122-126; src/mtlcheck/train/metrics.py:110` · **ABERTO**

**Defeito.** Three compounding gaps between the claim ('✅ corrigido, max|Δ|=0.0, ON by default') and the code. (1) enable_determinism uses torch.use_deterministic_algorithms(True, warn_only=True): any op without a deterministic implementation runs nondeterministically with only a warning — the guarantee is empirical (one A/B pair, horizon and config unrecorded in determinism.json), not enforced; the observed _bincount_cuda warning proves uncovered ops execute. (2) enable_determinism mutates process-global state (deterministic algorithms, cudnn.benchmark, the env var) and nothing ever restores it, so anything running after a substrate build in the same process — exactly the pattern of the substrate_sensitivity study, which builds a substrate then scores a 5-fold category cell — silently executes under different kernels than the banked baselines did; the float-weighted torch.bincount in the downstream macro-F1 (metrics.py:110) is where the warning fires (benign in value only because the 0/1 weights sum exactly in fp32 — an analysis nobody performed). (3) The cuBLAS side: the docstring says 'the CLI sets it before importing torch', but the check2hgi CLI raises SystemExit('layer 1 not implemented yet') at cli.py:57 — no versioned entry point pins CUBLAS_WORKSPACE_CONFIG; train() at line 120-121 discards enable_determinism's pinned return; and the manifest (export.py:125) records deterministic:true from the argument, unconditionally.

**Como falha.** A substrate is built on a machine where torch initialized before the env var was set (the only in-repo path today, since the CLI is a stub). Matmuls are nondeterministic, two 'deterministic' builds differ, but both manifests say deterministic:true — the provenance field designed to make builds refazíveis asserts a property the build does not have. Separately, a same-process build+score run produces downstream numbers under deterministic kernels that a fresh-process rerun of scoring alone will not reproduce.

**Correção proposta.** Record the pinned bool (and warn_only status) in the manifest instead of the request; scope the global mutation (context manager or process isolation for builds); decide warn_only per-op after auditing which ops actually warn, or run builds with warn_only=False once to enumerate them.

### 13 · R16's 'the port's distance is the reference's self-disagreement' overstates a single-pair floor; at the region level the port is 1.9x the floor

**major** · afeta C3 · `docs/REFERENCE_DEFECTS.md §R16 (comparison table); evidence/build_compare.json vs evidence/rerun_floor.json` · **CORRIGIDO**

> idem — a redação não arredonda mais a favor

**Defeito.** In 1-cosine terms the port-vs-reference disagreement is 1.23x (check-in), 1.30x (place) and 1.86x (region) the reference-vs-itself rerun; region RMS is 0.176 vs the floor's 0.137. The floor itself is estimated from ONE rerun pair, so there is no dispersion estimate against which 'the same as' can be judged. The region level — precisely the axis whose augmentation path (place table + Delaunay GCN + POI2Region) was most heavily rewritten — is the level furthest above the floor, and the equivalence phrasing absorbs any small systematic forward difference there. The qualitative conclusion (a separate universe from the 0.09/0.29/0.43 seed floor) survives; the quantitative identity claim does not.

**Como falha.** A subtle numerical difference in the port's region path (e.g. an op-order change inside POI2Region that only matters after hundreds of epochs of chaotic amplification) is classified as 'build noise' because the single-pair floor has no error bars; the region embeddings that feed the region-task inputs drift and the discrepancy is discovered only when region Acc@10 fails to reproduce.

**Correção proposta.** Run >=3 reference self-reruns to give the floor a distribution, report per-level ratios (1.2x/1.3x/1.9x) instead of 'the same', and note that region sits above the floor.

### 14 · Manifest records requested determinism, not achieved determinism; the guarantee itself is warn-only

**major** · afeta C3 · `/Users/vitor/Desktop/mestrado/mtlcheck/mtlcheck/src/mtlcheck/substrate/training.py:106,120-121,173 and export.py:125; cli.py:56-57` · ⚠ **sem veredito independente** · **ABERTO**

**Defeito.** Three gaps stack: (1) enable_determinism uses torch.use_deterministic_algorithms(True, warn_only=True), so an op with no deterministic implementation proceeds nondeterministically with only a log warning; (2) train() discards enable_determinism()'s return value — the bool that says whether CUBLAS_WORKSPACE_CONFIG was set in time — and SubstrateRun.deterministic is set to the requested argument, which export._manifest then writes as switches.deterministic; (3) the docstring's mitigation ("The CLI sets it before importing torch") is not true of any code: _run_check2hgi raises 'layer 1 not implemented yet', so no entry point sets the env var early. config.py's own charter says the reference's class of provenance lie (recorded fp32 while fp16 ran) is 'structurally impossible here' — this is the same class, still possible.

**Como falha.** A build runs in a process where a cuBLAS handle was already created (e.g., after any prior matmul in the same session, or a future op falls to the warn-only path). Two 'deterministic' builds differ; both manifests say deterministic: true. A later agent, following R16's logic, concludes the divergence must be a code or data change and burns time hunting it — or, worse, treats a byte-differing rebuild as evidence against the port's equivalence.

**Correção proposta.** Use warn_only=False (fail loudly, whitelist any op that genuinely needs an exception), propagate the pinned bool into SubstrateRun (e.g., deterministic="full"/"scatter-only"/False) and write that into the manifest, and make the layer-1 CLI set CUBLAS_WORKSPACE_CONFIG before importing torch as the docstring promises.

### 15 · C3's headline — 'port-vs-reference distance equals the reference's self-distance' — overstates a n=1 floor that the port actually exceeds ~2x at the region level

**major** · afeta C3 · `studies/porting_validation/PLAN.md §4 (lines ~173-189); docs/REFERENCE_DEFECTS.md §R16 (lines 379-389); evidence/{rerun_floor,build_compare,seed_floor}.json` · ⚠ **sem veredito independente** · **CORRIGIDO**

> piso virou distribuição n=5; região está FORA — registrado

**Defeito.** The self-disagreement floor is a single pair of runs (rerun_floor.json). In distance terms (1−cos) the port is above that floor at every level: check-in 0.0068 vs 0.0055 (1.23x), place 0.0045 vs 0.0035 (1.30x), region 0.0213 vs 0.0114 (1.86x); RMS 0.163 vs 0.153. Calling this 'praticamente a distância da referência a si mesma' asserts an equality the data does not show and that a one-sample floor cannot support. The accompanying loss calibration is internally inconsistent the same way: the same-seed rerun delta (0.0085) is 2.7x the quoted three-seed dispersion (0.0031), i.e. both floors are themselves noise-dominated at n≤3.

**Como falha.** A real residual divergence in the port's region path — the level with the largest excess over the floor, and the one feeding the region tower — of the same order as the nondeterminism floor would be classified as 'the reference's own noise' and never investigated. The claim as stated is unfalsifiable at n=1: any distance below the seed floor passes.

**Correção proposta.** Restate the claim as what the evidence shows: the port's distance is the same order of magnitude as the reference's nondeterminism floor and orders of magnitude below the seed floor. If equality matters, estimate the floor's dispersion (a handful of reference reruns) and test whether 0.9787 at the region level is inside it — or lean on the stronger evidence already in hand (the deterministic-layer exactness plus the C4 downstream loop).

### 16 · The rule 'substrate rebuild noise = 0.18 pp; any margin below is inside build noise' is a range of n=3 at one state/one probe/one fold-seed; its 95% CI spans an order of magnitude

**major** · afeta C4 · `studies/porting_validation/PLAN.md:218-220` · **CORRIGIDO**

> idem

**Defeito.** 0.18 pp is the range of three rebuild means (sample sigma=0.099 pp). The sampling distribution of a 3-sample range is extremely wide: the chi-square CI on sigma with 2 df is [0.051, 0.62] pp, i.e. the true rebuild noise could be 2x smaller or 6x larger than the quoted floor. It was measured only at Alabama (smallest state, 11,848 places), only through the category probe (the family least coupled to the substrate's region levels), at one fold-seed, one probe run per substrate, and entirely in the hard-negatives-ON regime (Alabama is below the reference's 50k gate, Check2HGIModule.py:57,987). The rule is also mis-scoped in both directions: claims comparing arms on the SAME substrate pair build noise out entirely (sub-0.18 margins can be real), claims comparing two independently rebuilt substrates carry sqrt(2) x sigma, and at FL/CA/TX new builds differ from banked artifacts by the S17 objective change — bias, not noise — so the floor cannot transfer there at all.

**Como falha.** A future substrate-level claim with a 0.25 pp margin is accepted as 'outside build noise' although the CI allows sigma up to 0.62 pp; conversely a valid within-substrate paired result with a 0.10 pp margin is dismissed as 'inside build noise' although build noise cancels in that design. Either way a wrong scientific conclusion is drawn from the rule, at states and task families where the 0.18 figure was never measured.

**Correção proposta.** Restate as 'at Alabama, category probe, sigma-hat = 0.10 pp (n=3; 95% CI 0.05-0.62)' and scope it to unpaired cross-substrate comparisons in the hard-neg-on regime. To make it a usable floor: ~10 rebuilds bounds sigma within [0.69, 1.83]x, ~20 within [0.76, 1.46]x; repeat at one large state (where the objective changed) and through the region/joint probes before generalizing.

### 17 · The two arms are not the same procedure, and the own builds reach systematically lower pretext loss than every reference-process build — untreated as a confound

**major** · afeta C4 · `evidence/substrate_sensitivity.json + evidence/seed_floor.json + evidence/banked_v18_materialize.json` · ⚠ **sem veredito independente** · **CORRIGIDO (doc)**

> diferença de procedimento e a loss 0,21×0,23 explicadas

**Defeito.** The banked arm is one non-deterministic draw of a different pipeline (engine check2hgi_dk_ovl, per-window prefix readout npz, one-shot export bounded at 2.4e-6 — that part is fine and documented). But the own builds' best losses are 0.2098/0.2122/0.2235 at seeds 42/43/7, while the reference process at the SAME seeds gives 0.2308/0.2339/0.2323 (seed_floor.json) and 0.2349 (build_compare.json) — the port's builds sit ~0.01-0.02 lower, i.e. 4-7x the reference's entire seed dispersion (0.0031). Worse, the repo's own seed-42 records disagree with each other: substrate_sensitivity own seed 42 = 0.20984 @494, own_substrate_manifest.json = 0.21627 @497 — two 'deterministic' seed-42 Alabama builds that differ by 2x the reference seed dispersion, with no config hash, device, or code revision recorded to reconcile them. The docs never mention or explain the loss gap. So the experiment does not compare 'rebuilds of the same process to the banked draw'; it compares three draws of a measurably different (better-optimizing, or differently-configured) process to one draw of the old one, and attributes the whole +0.13 pp gap to noise.

**Como falha.** If the loss gap reflects a recipe/config difference between the sensitivity builds and the validated build_compare configuration (the only one calibrated against the reference), then the closed loop was run on a substrate configuration whose equivalence was never established, and the 30.7-30.9 numbers validate a different chain than the one C1's evidence covers. The consistent +0.13 pp uplift would then be a fingerprint of that difference, not build noise.

**Correção proposta.** Record config hash + code rev + device in every evidence JSON; explain (or eliminate) the 0.21-vs-0.23 loss regime difference between the sensitivity builds and build_compare/seed_floor; rerun one sensitivity seed with the exact build_compare configuration to confirm the probe number is insensitive to whatever changed.

### 18 · The 0.18 pp 'build noise' bar generalizes a 3-sample, one-state, category-only range to all substrate-level claims

**major** · afeta C4 · `studies/porting_validation/PLAN.md §'O círculo fechado'; evidence/substrate_sensitivity.json; evidence/README.md (banked provenance note)` · ⚠ **sem veredito independente** · **CORRIGIDO**

> redação diz que é amplitude de n=3 e o que cobre

**Defeito.** The secondary claim — 'any substrate-level claim with a margin below ~0.18 pp is inside build noise' — rests on the range of n=3 rebuilt substrates, at one state (Alabama), through one downstream cell (7-way category macro-F1). The range of 3 samples is a downward-biased noise estimate (std of the three means is ~0.10, and a 3-sample range has huge sampling variance); the region task — the consumer the substrate's spatial augmentation exists for, with C≈1109 classes — was never re-scored on any rebuilt substrate and may be far more substrate-sensitive than a 7-class macro-F1. Also, all three rebuilds land ABOVE the banked number (+0.02/+0.17/+0.20), and the evidence README itself records that the banked v18 substrate came from a different engine/readout path (`check2hgi_dk_ovl`, per-window readout) — so the '+0.13 pp to banked' term compares across procedures, not across builds of the same procedure.

**Como falha.** A future substrate-level ablation shows a +0.3 pp region-Acc@10 effect and is accepted as above build noise using the 0.18 pp category-derived bar, when region-level build noise (never measured) is actually 0.5 pp — a wrong scientific conclusion drawn directly from this claim.

**Correção proposta.** State the bar as 'category macro-F1, Alabama, n=3'; measure region-task sensitivity on the same three rebuilt substrates before using the bar for any region claim; report std alongside range.

### 19 · C4 uses the per-fold deviation (~1.2 pp) as the noise scale for comparing 5-fold MEANS — the tolerance is inflated ~2.2x and the paired structure is ignored

**major** · afeta C4 · `studies/porting_validation/PLAN.md §4 (lines ~205-216); evidence/substrate_sensitivity.json` · ⚠ **sem veredito independente** · **ABERTO**

**Defeito.** The compared quantities (30.7181/30.8754/30.9001 vs 30.7013) are means over the same 5 folds, but the yardstick quoted is the within-run per-fold std (~1.2 pp). The std of a 5-fold mean is ~1.07/√5 ≈ 0.48 pp, and since the folds are identical across substrates the honest comparison is the paired per-fold delta (own-42 vs banked: diffs [-0.15, +0.08, +0.10, -0.41, +0.47], mean +0.017, se 0.145). The conclusion happens to survive under the correct test — the observed deltas are small even against 0.48 — but the stated rule ('uma fração do desvio entre folds ~1.2 pp') would also have accepted a genuine ~1 pp substrate-induced shift as 'inside the noise of building a substrate at all'.

**Como falha.** A future rebuild (different state, or after a substrate-layer change) lands 0.9 pp below the banked number. By the criterion as written it is 'below the between-fold deviation, therefore the chain reproduces the banked number' — and a real regression ships as a validated port.

**Correção proposta.** Recompute the closure claim against the standard error of the 5-fold mean, or better, report the paired per-fold deltas (they are already in substrate_sensitivity.json and make the case more strongly than the inflated yardstick does).

### 20 · Parameter-count evidence (826 827) contradicts the closed-loop substrate's manifest (827 083) — exactly the 4x64 first-layer widening of the 15-channel v18 feature layout

**major** · afeta cross-cutting · `studies/porting_validation/PLAN.md:169 vs evidence/own_substrate_manifest.json (training.n_params)` · ⚠ **sem veredito independente** · **CORRIGIDO**

> tabela de evidência agora diz a config de cada medição

**Defeito.** PLAN section 4 lists '826 827 params both sides' as C1 equivalence evidence, but the substrate actually built for C4 records n_params=827083. The difference is exactly 256 = 4x64, the GCNConv(in_channels->64) weight rows added by the continuous_time_4 feature block: 826827 corresponds to an 11-channel input, 827083 to the 15-channel layout ('canonical_11 + continuous_time_4') that both the own manifest and the banked v18 arm (build_study_repr.py --add-continuous-time) use. So the parameter-count comparison in the evidence table was apparently taken on a configuration that is not the v18 configuration the closed loop built and the banked substrate embodies. Neither number is asserted in any versioned test (test_substrate_model.py checks ref_count==my_count on a synthetic mini-state only).

**Como falha.** The equivalence dossier certifies a model shape the production chain does not run. If any other C1 measurements (e.g. the 25-epoch real-Alabama trajectory) were taken on the same 11-channel configuration, the trajectory equivalence also does not cover the 15-channel model that produced the C4 substrates — a port defect living in the continuous-time feature path (the 4 extra columns and their first-layer weights) would be invisible to the entire evidence table.

**Correção proposta.** Recount both sides at the real Alabama v18 configuration (15 channels) and correct PLAN section 4; state explicitly which configuration each C1 measurement (loss, gradients, trajectory) was taken on, and pin the expected Alabama count in a versioned test.

