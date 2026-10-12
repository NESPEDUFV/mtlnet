# D1 experiment design — the capacity-matched dedicated baseline

> **Decision record.** The author chose option (a) in `AVAL_NECESSARIA_3_ptBR.md` D1: run the
> capacity-matched dedicated baseline on nespedgpu. This file is the experiment's design and its
> licensing contract, written BEFORE any run so the rules cannot bend to the result.

## 1. The question this answers (and the answer it replaces)

The banca question: *"se o ganho vem do tronco e não da interação entre as tarefas, um modelo
dedicado com a mesma capacidade não recuperaria o mesmo ganho?"*

**A caution on the answer the author sketched.** The reply "não, porque no tronco temos o gate que
permite a troca de conhecimento entre as tarefas" is NOT defensible as stated: MobiWac's own freeze
control (§6, `06_results.tex` L92–94) shows the category gain survives with the region pathway
frozen — the paper itself attributes the gain to "a stronger shared trunk, **not** the region task
teaching the category one," stated "as a finding, not a hypothesis." An examiner quotes that back in
one breath. What the cross-attention sharing legitimately explains is why sharing **does not hurt**
(negative transfer absent), not a knowledge exchange that the freeze control shows is unnecessary
for the gain. The honest, strong answer is empirical — this experiment.

## 2. Design

- **Models.** The dedicated single-task ceilings exactly as in the Ch.5 protocol (the
  `closing_data/baselines` STL configurations), with hidden width scaled so total trainable
  parameters ≈ the joint model's count on that dataset (~4.2M at AL; ~5.2M at CA; per-dataset
  targets read from the run configs, ±5%). Scale width, not depth (fewer confounds); one scaled
  variant per task (category; region optional but recommended at CA where the region stakes are
  highest).
- **Protocol, identical to Ch.5.** User-disjoint StratifiedGroupKFold 5-fold; stride-1 sliding
  windows; the same per-fold region-transition prior; same tuning budget as the STL ceilings
  (the same early-stopping and LR-search policy — a capacity-matched baseline with a worse budget
  proves nothing); metrics macro-F1 (category), Acc@10 (region); paired Wilcoxon vs the joint model,
  same n.
- **Scope (time-boxed).** Pilot: Alabama, seed 0 × 5 folds (cheapest; param audit + harness check).
  Main: AL + CA (smallest + largest region cardinality), seeds {0,1,7,100} if the pilot is clean;
  FL as stretch. This answers the question without re-running the whole board.
- **Infrastructure.** nespedgpu (A40 46GB, 128GB RAM, 32 cores; no scheduler). Inputs shipped from
  the repo's existing fold/window artifacts; code path `src/training/runners/*single_task*` +
  `../../../../../scripts/train.py` with an `--override` for hidden width. A param-count audit
  (`calflops`/`torchinfo`) runs BEFORE training and its output is committed with the results.

## 3. The licensing contract (fail-closed, agreed before results exist)

1. **Nothing enters Ch.5.** The MobiWac version of record is under review; these are
   post-submission frame analyses. Home: a Ch.5-adjacent frame discussion or Appendix, dated, with
   its own fact gate (personas 06/07 on the new numbers).
2. **Both outcomes are reportable; neither is suppressible.** The author's note "se a resposta não
   for muito a favor do MTL... vale não mencionar ou trabalhar muito disso no texto" is understood
   as a PROMINENCE decision, and it has a floor: once the experiment runs, its outcome BINDS the
   §3.4 concession. If the capacity-matched dedicated model recovers part of the joint gain, the
   concession/limitation must say so (briefly is fine; silently is not) — WRITING_LAW §3 and
   AGENT_GUARDRAILS §7 (silent correction) do not permit running an experiment and hiding an
   unfavorable answer while asserting the favorable claim. What stays discretionary: how much space
   it gets, and whether it appears as one limitation sentence vs a discussion subsection.
3. **Verbs bound to tests, as always.** "The joint model outperforms the capacity-matched dedicated
   model" only with the paired test; "matches" only with TOST ±2pp; the AZ rule unchanged.
4. **Pre-registered readings.** (i) capacity-matched STL ≈ original STL (joint still wins): the win
   is not a capacity artifact — the trunk story is confirmed and the §3.4 concession narrows.
   (ii) capacity-matched STL recovers part of the gap: reported as a quantified nuance of the
   two-factor story (capacity is a third contributing factor, measured); the mechanism paragraph in
   Ch.6 is drafted from that number. (iii) capacity-matched STL matches/exceeds the joint model:
   the operational benefit (one artifact, one pass) remains the honest claim and the mechanism
   claim is scoped down accordingly. All three are written BEFORE the run.

## 4. Execution steps (next actions)

1. Param-count audit of the joint model + STL ceilings per dataset (local, minutes).
2. Width-scaling implementation behind a config flag (no changes to existing STL code paths).
3. Pilot dispatch to nespedgpu (AL seed 0); harness + budget check.
4. Main runs; results JSON in `../../../../../docs/studies` following the closing_data schema, marked
   POST-SUBMISSION; fact gate before any sentence uses them.

## 5. Execution record (POST-SUBMISSION analyses — never enter Ch.5)

**5.1 Parameter audit (2026-07-23, local, repo .venv, `numel` over trainable params).**
The audit REPRODUCES the MobiWac §4 quote exactly:

| Dataset | joint (v17 dualtower) | STL cat (next_gru, h=256) | STL reg (stan_flow) | combined | ratio |
|---|---|---|---|---|---|
| Alabama (1109 reg.) | 4,197,621 (4.20M) | 644,359 | 417,117 | 1,061,476 (1.06M) | 3.95x |
| California (8501 reg.) | 5,151,189 (5.15M) | 644,359 | 1,370,685 | 2,015,044 (2.02M) | 2.56x |

Paper quote "~4.2M vs 1.1M (AL); 5.2 vs 2.0 (CA)" — CONFIRMED, and the method comment's
"~2.6–4.2x params" matches the two ratios. Capacity-matched widths found by search:
cat `next_gru hidden_dim=672` → 4,207,399 (100.2% of AL target); `hidden_dim=752` → 5,249,719
(101.9% of CA target); reg `next_stan_flow d_model=480` (AL) / `d_model=352` (CA).

**5.2 Pilot (A40 job `c0cc0edd`, 2026-07-23): AL seed 0 × 5 folds, cat, hidden=672, ceiling
recipe bs2048@0.005.** Result: **macro-F1 55.30 ±1.92** (per-fold 55.79/56.86/56.90/55.29/51.68;
scorer `score_stl_cat_ceiling.py`, f1-best epoch, fold-mean — same convention as the ceiling).
Reference points: dedicated ceiling at its own optimum (h=256, best-vs-best) = 56.82 ±0.03
(n=20); joint v17 = 64.54 (n=20). Runtime 4.7 min.

*Preliminary reading — reading (i) of the pre-registered three:* quadrupling the dedicated
model's parameters does not recover the joint gain; at seed 0 the wider model scores slightly
BELOW the tuned dedicated optimum. NOT yet citable: single seed, and the ceiling was
best-vs-best tuned while the wide arm has only the ceiling's recipe — the fairness sweep
(5.3) closes that gap.

**5.3 Main sweep (A40 job `d38a1382`, COMPLETE 2026-07-23): AL hidden=672, arms {bs2048@0.005,
bs2048@0.0025, bs8192@0.005} × seeds {0,1,7,100} × 5 folds** (pilot cell reused for
bs2048@0.005 s0). Full n=20 per arm, macro-F1 at f1-best epoch, `score_stl_cat_ceiling.py`
convention (same as the ceiling):

| Arm (h=672, ~4.2M params) | n | mean | std |
|---|---|---|---|
| bs2048 @ lr 0.0025 (**best**) | 20 | **56.16** | 1.88 |
| bs8192 @ lr 0.005 | 20 | 55.74 | 2.00 |
| bs2048 @ lr 0.005 | 20 | 55.61 | 2.05 |

**Alabama verdict — reading (i) of the pre-registered three.** The capacity-matched dedicated
category model (best arm, n=20) scores **56.16 ±1.88**, against the dedicated ceiling at its own
optimum **56.82 ±0.03** (h=256, best-vs-best, n=20) and the joint v17 model **64.54** (n=20).
Quadrupling the dedicated model's parameters does not move it (−0.66 vs the h=256 optimum;
within its own fold noise) and recovers none of the joint gain (+7.72 remains). At Alabama the
joint win is NOT a capacity artifact; the stronger-shared-trunk explanation stands, and the
§3.4 concession can be narrowed accordingly once California confirms. Licensing: these numbers
are POST-SUBMISSION frame analysis (never Ch.5); before any chapter sentence uses them, the
fact gate re-verifies against these JSONs (workdir `d38a1382`, copies in the session artifact
`al_capmatch_summary.json`).

*Fairness note:* the ceiling was tuned best-vs-best over a wider recipe grid; the wide arm got
a 3-recipe sweep around the ceiling's winners. The sweep's spread (0.55 pp across arms) is far
smaller than the gap it would need to close (+8.4 to reach the joint), so a wider grid cannot
change the verdict's direction. State this scope whenever the number is quoted.

**5.4 California (A40 job `4cff4b00`, running): hidden=752 (~5.2M), arms
{bs8192@0.005 = the CA ceiling winner, bs8192@0.0025} × seeds {0,1,7,100} × 5 folds.**
References for the verdict: CA dedicated ceiling 70.60 ±0.07 (bs8192@0.005, n=20), joint v17
77.05 (n=20).

*Partial read (2026-07-23, first arm, seeds {0,1,7} = n=15 of 20):* capacity-matched dedicated
= **68.35 ±0.53** (per-seed 68.41 / 68.12 / 68.53) on the ceiling's own winning recipe. Same
direction as Alabama, larger magnitude: the 2.6×-wider model runs 2.25 pp BELOW the tuned
narrow optimum and recovers none of the joint's +6.45. PRELIMINARY (one arm, 3 of 4 seeds);
the final value is the best arm's n=20 mean once seed 100 and the second arm land. Under the
pre-registered readings this is again reading (i).

**5.5 The mechanism read (what the two experiments together license).** The capacity experiment
closes the last cheap alternative explanation for the joint win. The chain now stands:
(1) the freeze control (MobiWac §6, in-paper) shows the category gain survives with the region
pathway frozen — so the gain is not the region task teaching the category task;
(2) the capacity-matched baseline (this experiment, post-submission) shows a dedicated model
with the joint model's parameter budget does not reproduce any part of the gain — at both
states it lands at or below the narrow dedicated optimum — so the gain is not parameter count;
(3) what remains, and what the paper already asserts as its finding, is the shared trunk: the
cross-attention stack trained on both tasks' signals builds a representation the dedicated
model cannot reach at any width tried. A width increase without a second task's signal has no
new information to spend its parameters on — the two experiments are the two halves of that
sentence. Licensing: (1) is citable from Ch.5; (2) and (3)'s second half are POST-SUBMISSION
frame analysis (Ch.6 discussion / appendix), never Ch.5.

---

## 6 · [2026-08-13] AS LARGURAS DO §5.1 MEDEM A ARQUITETURA v17, NAO A ATUAL

Esta nota existe porque as larguras publicadas acima (`d_model=480` em AL, `352` em CA;
`hidden_dim=672` em AL, `752` em CA) foram lidas numa sessao posterior como se pareassem capacidade
no modelo conjunto **atual**. Elas nao pareiam. O cabecalho da tabela do §5.1 ja diz qual arquitetura
mediu, "joint (v17 dualtower)", e essa coluna e a que mudou.

**Medicao.** Reconstruindo `mtlnet_crossattn_dualtower` com os defaults de treino que
`src/configs/experiment.py:423-431` fornece (`feature_size=64`, `shared_layer_size=256`,
`num_heads=8`, `num_layers=4`, `seq_length=9`, `num_shared_layers=4`), cabecas `next_gru` e
`next_stan_flow_dualtower` com `raw_embed_dim=64, fusion_mode=aux, freeze_alpha=True,
alpha_init=0.0`, blocos de cross-attention 2x4, e o vocabulario de regiao por dataset lido de
`output/check2hgi_design_k_resln_mae_l0_1/<state>/region_embeddings.parquet` (AL 1109, CA 8501,
TX 6553):

| dataset | conjunto v17 (§5.1) | conjunto ATUAL (medido) |
|---|--:|--:|
| Alabama | 4.197.621 | **6.909.789** |
| California | 5.151.189 | **8.809.533** |
| Texas | (nao medido no §5.1) | **8.308.897** |

Decomposicao do modelo atual em Alabama, por submodulo: `category_encoder` 149.760, `next_encoder`
149.760, `crossattn_blocks` 1.583.104, `category_poi` 3.161.608, `next_poi` 1.864.533, mais duas
LayerNorm. **Nenhum agrupamento reproduz o alvo de via de regiao de 2.466.542** que o
`POSTPONED.md` P1 cita para Alabama — a via `next_poi` da 1.864.533.

**Larguras pareadas contra o modelo atual**, alvo = modelo conjunto inteiro (decisao do autor,
2026-08-13), por busca sobre `next_stan_flow` com `embed_dim=64`:

| dataset | alvo | `d_model` | contagem | % do alvo |
|---|--:|--:|--:|--:|
| Alabama | 6.909.789 | **624** | 6.978.702 | 101,0% |
| California | 8.809.533 | **528** | 9.004.686 | 102,2% |
| Texas | 8.308.897 | **544** | 8.354.882 | 100,6% |

**Regra para quem ler este arquivo depois:** o §5.1 continua valido para o que ele mediu, e os
resultados que ele reporta permanecem os resultados daquela arquitetura. Ele **nao** e a fonte de
largura para um controle de capacidade sobre o modelo atual. Antes de usar qualquer largura daqui,
recompute contra a arquitetura que voce vai rodar.
