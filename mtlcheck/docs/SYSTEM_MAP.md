# Mapa do sistema v18 — o que reconstruir, o que descartar

> Entregável da fase 1 do rewrite `mtlcheck`. Escrito a partir da leitura direta do repositório
> `ingred` no commit `dafdc74d` (local) / `60f7a6e8` (A40), não de memória nem de resumo.
>
> **O que este documento é:** a especificação executável do v18, extraída do código que realmente
> rodou, cruzada com as regras científicas de `docs/studies/closing_data/`.
> **O que não é:** um plano de implementação. Esse é o `ARCHITECTURE.md`.

---

## 0 · Decisões já fechadas com o autor

| # | Decisão | Escolha |
|---|---|---|
| 1 | Objetivo | Base limpa pós-defesa — sem prazo de banca |
| 2 | Local | Worktree `../mtlcheck`, branch `rewrite/mtlcheck` |
| 3 | Escopo HGI | Substrato v18 (check-in) **+** substrato v14 (região) |
| 4 | Validação | Gate barato local (MPS) + A40 à vontade em AL/AZ/IST, fechando com um FL ou CA |
| 5 | Raw | Começa em `data/checkins/<State>.parquet`; ETL geográfica bruta = fase 2 |
| 6 | Datasets | Os 6 do v18: alabama, arizona, istanbul, florida, california, texas |
| 7 | Resultados | Formato novo, sem compatibilidade com os sidecars antigos |
| 8 | CLIs | `check2hgi` + `train` + `wave` (+ lane Modal por último) |
| 9 | Fidelidade | Reproduzir as **conclusões científicas**, não os números dígito a dígito |
| 10 | Acoplamento | Fluxo do substrato e fluxo de construção de input do modelo ficam **separados** |
| 11 | Substrato | Rebuild completo dos 6 estados |

---

## 1 · O que é o v18

**v18 = a receita congelada do v17, sobre um substrato sem vazamento, mais features de tempo decorrido.**

Três componentes, todos carregando peso:

1. **Receita v17 inalterada** — mesmo modelo, mesmas cabeças, mesmo otimizador, mesmas taxas de
   aprendizado, mesmo número de épocas, mesmo seletor, mesmos scorers. v18 **não** é mudança de
   arquitetura.
2. **Grafo de check-ins forward-only** — o preprocessador canônico emite as duas direções de cada
   aresta de visita consecutiva; o v18 mantém apenas `src < tgt`, no **treino e no readout**. Sem
   isso, o vetor de uma visita é convolvido sobre uma vizinhança que inclui a visita *seguinte*, e a
   cabeça de categoria enxerga uma feature do alvo que está sendo perguntada.
3. **Quatro colunas de tempo decorrido** anexadas às 11 canônicas → `in_channels = 15`.

O tamanho do vazamento, medido em Alabama: reter a visita-alvo custa **28,63 pontos de macro-F1**
(56,86 → 28,23). A auditoria reproduziu a coluna dedicada publicada (55,87 publicado seed-0 contra
56,86 na auditoria), então o buraco é propriedade do substrato, não de um harness divergente.

### 1.1 · O resultado do v18 — e por que ele redefine a barra de aceitação

`V18_RESULTS.md §1`, MTL contra o próprio teto dedicado, mesmo substrato e mesmo protocolo:

| estado | n | cat dedicado | cat MTL | Δcat | reg dedicado | reg MTL | Δreg |
|---|---:|---:|---:|---:|---:|---:|---:|
| istanbul | 20 | 35,34 | 35,45 | **+0,11** beats | 75,16 | 75,27 | **+0,11** beats |
| alabama | 20 | 30,77 | 30,70 | −0,08 matches | 70,12 | 69,67 | −0,45 matches |
| arizona | 20 | 34,57 | 34,62 | +0,04 matches | 59,48 | 59,26 | −0,22 matches |
| florida | 20 | 37,35 | 37,59 | **+0,24** beats | 76,69 | 77,09 | **+0,39** beats |
| texas | 10 | 36,32 | 36,36 | +0,04 beats | 64,95 | 66,88 | **+1,93** beats |
| california | 10 | 35,62 | 35,75 | +0,12 beats | 63,46 | 65,42 | **+1,96** beats |

No v17 o MTL batia o teto de categoria em **+4,7…+8,6 pp**. No substrato honesto isso virou **+0,1**.
A vantagem que sobrevive é **região nos estados grandes** (TX +1,93, CA +1,96) e um ganho pequeno mas
significativo em FL e Istambul.

> **Consequência para este rewrite:** a lista de conclusões que o código novo precisa reproduzir é
> escrita sobre o v18, e a conclusão central passou a ser sobre **região**, não sobre categoria.
> Qualquer teste de equivalência ancorado nas manchetes do v17 estaria validando um artefato de
> vazamento.

### 1.2 · Buracos conhecidos no board

- **CA e TX têm apenas seeds 0 e 1 nas famílias dedicadas** (`PROVENANCE.md`): as células `joint`
  existem nas 4 seeds, mas `cat`/`reg` só em duas. Daí o `n=10` dessas duas linhas contra `n=20`
  das outras quatro. Fechável com trabalho de A40.
- **A pergunta capacidade-vs-sinergia está aberta** (`POSTPONED.md §P1`): a torre de região do joint
  carrega **2,5–5,9× os parâmetros** do baseline dedicado (alabama 2 466 542 vs 417 117; california
  3 420 110 vs 1 370 685) *e* uma cabeça diferente. Ninguém sabe se o +2 pp em CA/TX é multi-tarefa
  ou só parâmetro. **O projeto novo não pode fechar essa pergunta por acidente** ao "limpar" as
  arquiteturas igualando capacidades.

---

## 2 · Os quatro caminhos de execução, exatamente como rodam hoje

Driver: `docs/studies/closing_data/v18/run_wave.sh`, uma wave por seed, seis estados, três famílias.

### 2.1 · Família (a) — categoria dedicada

```
train.py --task next --state <S> --engine check2hgi_v18
         --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed <SEED>
         --batch-size 8192 --max-lr <LR> --logit-adjust-tau 0.5 --compile --tf32 --no-checkpoints
env: MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1
LR por estado: alabama 0,0025 · arizona 0,0005 · istanbul 0,0005 · FL/CA/TX 0,005
scorer: scripts/closing_data/score_stl_cat_ceiling.py → cat_macro_f1_mean
```

Código: `scripts/train.py` → `src/training/runners/next_cv.py::run_cv` →
`src/training/runners/_single_task_train.py::train_single_task`.

Comportamento relevante:
- modelo criado **por fold**, `torch.compile` **por fold** em CUDA;
- `compute_class_weights` é chamado **sempre**, mesmo quando a loss calibrada o ignora — trabalho morto;
- quando `loss_calibration` está setado (o caso do v18, τ=0,5), o critério é `build_calibrated_loss`
  com estatísticas **só do train fold**; senão é `CrossEntropyLoss` com pesos de classe. Logit
  adjustment **substitui** class weighting, não empilha;
- early stopping por F1 de validação (patience), timeout e `target_cutoff` disponíveis;
- `_extract_diagnostics` faz **uma passada extra** sobre o val loader recarregando o melhor estado;
- o melhor `state_dict` fica **em memória** dentro do `MLHistory`.

### 2.2 · Família (b) — região dedicada

```
scripts/p1_region_head_ablation.py --state <S> --heads next_stan_flow
         --input-type region --region-emb-source check2hgi_design_k_resln_mae_l0_1
         --override-hparams freeze_alpha=True alpha_init=0.0
         --engine-override check2hgi_v18 --folds 5 --epochs 50 --seed <SEED>
         --target region --max-lr 0.003 --compile --tf32 --tag <TAG>
env: MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 MTL_STRICT=1
scorer: o próprio JSON P1 → heads.next_stan_flow.aggregate.top10_acc_mean × 100
```

**Esta família roda por um script de ablação, não pelo `train.py`.** Ela tem cópia própria de
carregamento de dados, split, laço de treino, validação, scoring e checkpoint. Diferenças reais
contra o caminho de `src/` (catalogadas em `docs/future_works/p1_val_loop_to_src.md`):

| eixo | `p1` | `src/training` |
|---|---|---|
| otimizador | `AdamW(lr=1e-4, weight_decay=0.01)` | cat também 0,01 (`default_next`, `experiment.py:538`); 0,05 é o default do **MTL** (`experiment.py:46,437`) |
| loss | `build_calibrated_loss` com stats do train fold | idem, mas via `config.loss_calibration` |
| RNG | **re-semeia por fold**: `seed_everything(seed + fold_idx)` | semeia uma vez |
| tracking | JSON próprio com `per_metric_best` | `MLHistory` |
| métrica de treino | **nenhuma** | opcional |
| early stopping | **nenhum** — roda as 50 épocas e guarda o melhor por métrica | **também nenhum no v18**: `default_next` traz `early_stopping_patience=-1` (`experiment.py:548`) e o driver não passa flag. O mecanismo existe, mas não foi usado |

O reseed por fold é o que torna o fan-out `--only-fold` byte-idêntico ao sequencial. **É contrato,
não acidente** — precisa sobreviver ou ser substituído por um contrato equivalente e documentado.

### 2.3 · Família (c) — joint (MTL v17)

```
train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_v18
         --state <S> --seed <SEED> --epochs 50 --folds 5 --batch-size 8192
         --mtl-loss static_weight --category-weight 0.50
         --no-reg-class-weights --no-cat-class-weights --logit-adjust-tau 0.5
         --cat-head next_gru --reg-head next_stan_flow_dualtower
         --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux
         --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
         --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
         --scheduler onecycle --max-lr 3e-3 --cat-lr <1e-3|2e-3> --reg-lr 3e-3 --shared-lr 1e-3
         --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32
         --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/<S> --no-checkpoints
env: MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
     MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 TORCHINDUCTOR_CACHE_DIR=<por estado+seed>
cat-lr: 1e-3 em AL/AZ/IST, 2e-3 em FL/CA/TX
scorers: a40_score_matched.py (diag-best) + score_joint_best.py (joint-best)
```

Código: `scripts/train.py` → `src/training/runners/mtl_cv.py` (2 338 linhas) + `mtl_eval.py`.

Pontos que importam:
- `MTL_ONECYCLE_PER_HEAD_LR=1` é o que faz `--cat-lr/--reg-lr` terem efeito. **Sem ele o `max_lr`
  escalar se propaga para todos os grupos e a execução vira v16 silenciosamente** — o mesmo comando,
  outro experimento;
- o critério de **região é `CrossEntropyLoss` puro**, sem pesos e sem calibração; só o de **categoria**
  passa por `build_calibrated_loss`. É por isso que `--logit-adjust-tau 0.5` no MTL atinge apenas a
  cabeça de categoria, que é exatamente o desejado (§3.3);
- `--per-fold-transition-dir` é passado **mas o prior está inerte** (`freeze_alpha=True`,
  `alpha_init=0.0`, KD 0.0). Correção do que eu tinha escrito antes: o campeão **não chega a carregar**
  o `log_T` — `MTL_SKIP_INERT_LOGT` é default-ON desde 2026-06-26 e `mtl_cv.py:611-618` retorna antes
  da carga e dos guards de vazamento. A flag no comando é inerte, não custosa;
- `steps_per_epoch` do OneCycle usa o **maior** dos dois train loaders sob `max_size_cycle`.

### 2.4 · O caminho HGI / substrato

Dois substratos distintos, hoje amarrados por symlink de filesystem:

**(i) Substrato de check-in (v18)** — `scripts/integrity_v2/build_study_repr.py`:
```
--forward-only --add-continuous-time, repr-seed 42, 500 épocas, encoder resln, dim 64, 2 camadas
```
- forward-only é literalmente um filtro de quatro linhas: `fwd = ei[0] < ei[1]`, aplicado a
  `edge_index` e `edge_weight`. Fato estrutural que o autoriza: o grafo de check-ins é união
  disjunta de caminhos por usuário com ids em ordem de visita (fato F1);
- as 4 colunas de tempo, todas medidas **até a própria visita**:
  `log1p(gap_horas)/10`, `log1p(horas_desde_a_primeira)/10`, `clip(gap, 0, 24)/24`, e uma quarta que o
  `build.json` chama de `is_first_visit` mas que o código calcula como **`gap == 0`**
  (`build_study_repr.py:418-432`) — empates de timestamp recebem 1.0, e a ordem entre empatados é
  instável (`preprocess.py:104`). Reproduzir o comportamento, não o nome;
- readout `infer_checkins.py --readout prefix_forward_only`, materialização por
  `materialize_engine.py` ou `materialize_from_insample.py`.

**(ii) Substrato de região (v14)** — engine `check2hgi_design_k_resln_mae_l0_1`, consumido como
`region_embeddings.parquet`. Nos seis estados o `check2hgi_v18/<estado>/region_embeddings.parquet`
é um **symlink** para o diretório do v14 (confirmado em `AUDIT.md`).

**Otimização já provada:** em grafo forward-only o readout por janela é **identidade** em relação ao
export one-shot — máx. 3,1e-06 sobre *todas* as janelas em quatro estados, contra tolerância 1e-4.
Florida materializou em 19 s o que o caminho por janela levava 20 min. **Vale só para arms
forward-only**; `materialize_from_insample.py` hard-falha em arms bidirecionais e esse guard tem que
sobreviver.

---

## 3 · Comportamentos cientificamente críticos (preservar)

Numerados para o teste de equivalência poder citá-los.

**S1 · Split.** `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)` sobre
`(y=next_category, groups=userid)`. As três famílias usam **o mesmo split**; no joint as duas tarefas
compartilham os mesmos índices. `p1` passa `np.zeros(len(y_cat))` como X e o joint passa o X real —
equivalente, porque `StratifiedGroupKFold` só usa o shape de X. Folds são **user-disjoint**: a
unidade retida é o usuário.

**S2 · Estatísticas só do treino.** Pesos de classe, prior de logit-adjustment e o conjunto de
rótulos in-distribution vêm exclusivamente do fold de treino. O offset do logit adjustment é uma
constante de comprimento 7 aplicada dentro do critério; `shared_evaluate` não recebe critério, então
os logits de avaliação não são ajustados. τ=0 reduz a CE pura.

**S3 · Logit adjustment é assimétrico entre cabeças.** τ=0,5 **só na categoria**; τ=0 na região, em
todos os estados. Medido em 5 folds e replicado em dois datasets: em região, τ=0,5 sobe macro-F1
(+0,377 AL / +0,671 IST) e **derruba** Acc@1/5/10 e MRR (Acc@10 −1,841 AL p=0,0002; −2,749 IST
p<0,0001). Isso é consistência de Bayes para erro balanceado — a fronteira ótima para macro-F1 é
subótima para métricas de ranking ponderadas por frequência. **Região é reportada por Acc@10 ⇒ τ=0.**

**S4 · Logit adjustment substitui class weighting, não empilha.** `next_cv.py:123-141` e
`mtl_cv.py:504-523` fazem da CE ponderada o ramo `else`. Empilhar os dois foi medido e afunda.

**S5 · Métrica de categoria** = macro-F1. Acima de 256 classes o cálculo sai do torchmetrics para a
acumulação por classe via `bincount` (o caminho do torchmetrics aloca `num_classes²`). As duas médias
macro dividem pelo número de classes **com suporte OU com predição** — incluir as classes só-FP é o
que faz o caminho hand-rolled bater com o torchmetrics.

**S6 · Métrica de região** = `top10_acc_indist × (1 − ood_fraction) × 100`, onde in-distribution
significa "o alvo aparece no conjunto de rótulos do fold de treino". Rank do alvo é
`1 + #{classes com logit estritamente maior}` — tie-handling canônico, independente de sort.
Desde 2026-08-10 os hits são derivados do rank (`hit@k == rank ≤ k`), o que os torna idênticos entre
CPU e CUDA, com um certificado de ambiguidade medido a cada época.

**S7 · Duas convenções de seleção de época, nunca misturadas.** *diag-best*: cada tarefa na sua
própria melhor época (a convenção da Tabela 3). *joint-best*: as duas no mesmo `e*` escolhido por
`geom_simple = sqrt(cat_macroF1 · reg_top10_indist)`, com `min_best_epoch=0` e empate resolvido pela
época mais cedo. `src/tracking/scoring.py` é a fonte única e é stdlib-puro.

**S8 · Sequências.** Janela deslizante de tamanho 9 + 1 alvo, `MIN_SEQUENCE_LENGTH=10`, stride 1
(overlap com gate). Posições curtas preenchidas com −1 → vetor zero, e as cabeças detectam padding
por `x.abs().sum(-1) == 0`.

**S9 · Alinhamento entre `next.parquet` e `next_region.parquet`.** Igualdade de contagem de linhas é
necessária mas **não suficiente**: a coluna `userid` tem que bater linha a linha. Um
`next_region.parquet` obsoleto de outra janela pode ter a mesma contagem e emparelhar errado cada
linha. O guard é hard-fail e tem que sobreviver.

**S10 · Prior `log_T` inerte no campeão.** `freeze_alpha=True, alpha_init=0.0` e KD desligado ⇒
`α·log_T = 0`. Com o prior inerte, nenhum arquivo de transição é necessário. Um prior **ativo**
(α aprendível, `α_init≠0`, ou qualquer peso de KD > 0) nunca pode pular os guards de vazamento.

**S11 · Precisão.** fp32 no treino (`MTL_DISABLE_AMP=1`). fp16 sem GradScaler estoura o teto de
65504 nos logits largos de região e produz um NaN determinístico por volta da época 30 que envenena
o backbone compartilhado. bf16 gera grad-NaN nesta A40 (Ampere) nas cardinalidades de CA/TX.

**S12 · Contagem de parâmetros por caminho.** Preservada como invariante explícita, para não fechar
por acidente a pergunta capacidade-vs-sinergia (§1.2).

**S13 · Pareamento cruzado das tarefas no joint — ALEATÓRIO no treino, alinhado na validação.**
Os dois train loaders do MTL sorteiam embaralhamentos **independentes**, então a cross-attention mistura
linhas cat↔reg **emparelhadas ao acaso** durante o treino, enquanto a validação é alinhada
(`mtl_eval.py:229-233` afirma isso explicitamente). O pareamento alinhado existe, mas apenas como
opt-in `--aligned-pairing` (`experiment.py:177-187`, `folds.py:1518-1530`, `train.py:936-941`), default
`False`, e o `run_wave.sh` **nunca o passa** — logo **toda célula joint bancada do v18 treinou com
pareamento aleatório**, e o gate G0.1 que decidiria isso continua ABERTO.

> ⚠ Esta é a armadilha número um deste rewrite. A implementação "limpa" natural da camada 2 — um
> dataset único devolvendo `(x_cat, x_reg, y_cat, y_reg)` por linha sobre o split compartilhado — **é**
> pareamento alinhado, ou seja, uma distribuição de treino diferente para o tronco cross-attn. Nenhuma
> das conclusões C1-C8 pega isso: a banda de ±2 pp de C5/C6 é 4-20× mais larga que os deltas bancados,
> e C8 falharia sem diagnóstico. O modo fiel ao v18 é o aleatório; o alinhado, se um dia for adotado,
> é mudança medida e deliberada. (Controle de derangement existente: `MTL_ALIGNED_DERANGE`,
> `folds.py:579`.)

**S14 · Clipping de gradiente por norma máxima 1,0** nas três famílias
(`_single_task_train.py:118`, `p1:685`, `mtl_cv.py:1122-1126` — a variante MTL clipa parâmetros do
modelo **e** do critério e carrega o guard de passo não-finito). Remover muda a trajetória nos estados
grandes sem mudar nada que C1-C8 meça.

**S15 · Contagem de passos do scheduler.** OneCycle avança **por batch**, com
`steps_per_epoch = ceil(max(len(loader_reg), len(loader_cat)) / grad_accum)` sob `max_size_cycle`
(`mtl_cv.py:443-458`). Um off-by-one ou um step por época desloca toda a curva de LR e passa por
qualquer banda de tolerância. Testável exatamente na CPU: despejar a série de LR por grupo e diferenciar.

**S16 · Camada de estatística.** As conclusões do v18 saem de médias pareadas **simétricas** sobre as
seeds comuns às duas colunas — diferenciar médias não-pareadas coloca um Δ ao lado de um `n` e de um
`p` calculados sobre outro conjunto. Uma reimplementação ingênua move os vereditos sem mudar uma linha
de treino.

**S17 · O objetivo do substrato muda com o tamanho do estado.** Encontrado 2026-08-13 ao portar o
`Check2HGIModule`. No amostrador de negativos da fronteira POI↔região
(`_sample_negative_indices_with_similarity`), 25 % dos negativos são **duros** — sorteados de uma
banda de similaridade (0,6 – 0,8) em vez de uniformemente — **mas só quando o número de lugares é
menor que 50 000**:

| estado | lugares | negativo duro |
|---|---:|---|
| Alabama | 11 848 | **ON** |
| Arizona | 20 666 | **ON** |
| Istanbul | 29 816 | **ON** |
| Florida | 76 544 | OFF |
| California | 169 145 | OFF |
| Texas | > FL | OFF |

Ou seja: os substratos dos estados pequenos e dos grandes **não são treinados pelo mesmo objetivo**, e
o corte cai exatamente sobre o agrupamento pequeno/grande usado para comparar resultados. Nada no log,
no manifesto ou no nome do artefato registra qual dos dois rodou.

**O gate não é uma decisão de modelagem — é o custo da implementação.** O ramo duro da referência é um
laço Python com um sync de device por sorteio: 72 µs × 42 286 sorteios = **3,1 s por época na
Califórnia**, meia hora a mais num build de 500 épocas. Caro, não impossível — mas caro o bastante
para alguém ter escolhido um limiar. O mecanismo em si está bem definido em todos os estados: a banda
(0,6 – 0,8) contém 20–27 % dos pares de região nos seis, e **nenhuma região em nenhum estado fica sem
candidato** (medido nos grafos congelados).

**Corrigido no `mtlcheck` removendo a razão, não o comportamento.** O sorteio foi vetorizado sobre um
índice CSR da banda, construído uma vez: **0,11 ms por época na Califórnia** contra os 3,1 s do laço,
com 63 MB de índice. Sem laço, sem sync, sem dependência de tamanho — negativo duro ligado em todos os
estados por padrão. `p2r_hard_neg_size_gate=50_000` reproduz o corte da referência para quem for
re-derivar os artefatos bancados.

Consequência a declarar: um substrato de estado grande construído aqui é treinado sobre um objetivo
**diferente** do bancado — o que a receita descreve. Três testes cobrem isso: a ausência de dependência
de tamanho, a equivalência de **distribuição** contra o laço (taxa de reamostragem, pertinência à
banda, uniformidade dentro dela) e a igualdade exata de loss e gradiente quando os dois lados recebem
os mesmos índices.

---

## 4 · Problemas de performance e arquitetura encontrados

Herdando o plano existente (`docs/studies/train_perf_multifold/`, `INVESTIGATION_gpu_cpu_alternation.md`
de 2026-08-10) e anexando o que encontrei.

### 4.1 · Já medido — carrego a conclusão, não re-derivo

- **Fan-out de 5 folds não acelera em 1 GPU** (AL: 654 s → 695 s). O valor é multi-GPU,
  resumabilidade e granularidade por fold.
- **O laço é launch-bound**: modelo de 0,47 M parâmetros, utilização de GPU 10–57 %, célula de
  categoria a 2,04× entre H100 e A40 — teto de lançamento de kernel. O lever é CUDA Graphs / fundir
  folds no mesmo processo, não micro-otimizar kernel.
- **Scoring de validação na CPU** era ~39 % da wall da célula de região; corrigido em `2c844974`.

### 4.2 · Encontrado nesta inspeção

| # | Problema | Onde | Custo |
|---|---|---|---|
| P1 | A família de região roda por um **script de ablação paralelo ao `train.py`**, com laço próprio | `p1_region_head_ablation.py` | Causa-raiz estrutural do bug de scoring que sobreviveu 2 meses |
| P2 | **Prior `log_T` inerte, mas executado**: aloca `[C,C]` de zeros (CA: 289 MB) e faz gather `[B,C]` + `masked_fill` + multiplicação por zero a cada forward, treino e validação | `next_stan_flow/head.py` | ~3-4 passes `[B,C]` extras por batch |
| P3 | **`torch.compile` refeito a cada fold** | `p1:622-646`, `next_cv.py:112` | Dezenas de s × 5 folds × 6 estados × 4 seeds |
| P4 | **Sequências construídas em loop Python** (9 posições × `pd.Series.map`) e **reconstruídas por célula** | `p1:289-299` | 3 famílias × 6 estados × 4 seeds refazem o mesmo trabalho |
| P5 | **Build de input do MTL pica ~66 GB de RAM**, forçando FL/CA/TX a rodarem 1-wide atrás de um `wait_ram` de 80 GB | `folds.py`, `run_wave.sh` | Serializa metade da wave |
| P6 | **Comportamento científico governado por variáveis de ambiente** | 15+ variáveis `MTL_*`/`P1_*` | Ver §5 — já corrompeu 8 de 10 células |
| P7 | `compute_class_weights` sempre computado, mesmo quando descartado | `next_cv.py:115`, `mtl_cv.py:492-496` | Pequeno, mas é sintoma |
| P8 | Passada extra sobre o val loader para diagnósticos | `next_cv.py:197` | Uma época a mais por fold |
| P9 | `results/` mora em `/home` no A40 (90 % cheio, 38 GB livres) enquanto `/dados` tem 2,2 TB | infra | Risco operacional |

---

## 5 · Variáveis de ambiente: o argumento mais forte do rewrite

O `PRECISION_CAVEAT.md` documenta que **8 das 10 células de categoria do v18 rodaram em fp16 enquanto
o sidecar afirma fp32**. Mecanismo: `cell_joint` faz `export MTL_DISABLE_AMP=1` dentro de uma função
de shell; o export **persiste nas células seguintes do mesmo shell**; `cell_cat` nunca seta nem
limpa a variável; e `_single_task_train.py:72-82` liga autocast fp16 exatamente nela. O resultado
dependia de a wave ter sido **retomada** ou não, porque numa retomada as células anteriores são
puladas e nunca exportam nada.

Consequências registradas na época: a comparação cross-seed de categoria em Florida ficou VOID e o
Δcat de +0,96 em Texas — a única veredito "beats" da coluna de categoria — também.
`TORCHINDUCTOR_CACHE_DIR` vazou pelo mesmo mecanismo, então Florida seed-0 compilou contra o cache do
Arizona.

> **Correção importante (a revisão pegou minha imprecisão):** o vazamento **já foi corrigido no driver
> que produziu os números do §1.1**. O `run_wave.sh:202-206` fixa o ambiente por comando com um
> comentário explícito de "NO bare export here"; as 10 células afetadas saíram do board em 2026-08-09
> (`v18/log.md:16`); e o Δcat de Texas foi re-medido limpo em **+0,020** (`v18/log.md:25`), que é o
> +0,04 que aparece na tabela do §1.1. Ou seja: o campo `precision` dos sidecars atuais é verdadeiro.
> O incidente permanece como **a melhor evidência disponível de por que ambiente não pode decidir
> ciência** — não como um defeito vivo do board.

Inventário parcial das variáveis que decidem ciência hoje: `MTL_DISABLE_AMP`, `MTL_DISABLE_AMP_EVAL`,
`MTL_AUTOCAST_BF16`, `MTL_ONECYCLE_PER_HEAD_LR`, `MTL_CHUNK_VAL_METRIC`, `P1_CHUNK_VAL_METRIC`,
`P1_STREAM_VAL`, `P1_STREAM_GPU`, `P1_SCORE_AB`, `MTL_STRICT`, `MTL_SKIP_INERT_LOGT`,
`MTL_COMPILE_DYNAMIC`, `MTL_COMPILE_CACHE_LIMIT`, `MTL_COMPILE_MODE`, `MTL_S2_AUTO_BUDGET_GB`,
`P1_S2_AUTO_BUDGET_GB`, `MTL_RAM_HEADROOM_GB`, `MTL_NO_TRAIN_DIAGNOSTICS`, `MTL_TRAIN_DIAGNOSTICS`,
`MTL_DUMP_VAL_PREDS`, `MTL_ROLL_TASKB_EVAL`, `MTL_STAN_LEGACY_MASK`, `MTL_STAN_FP32_ATTN`,
`MTL_PROFILE`, `DISABLE_AMP`.

E as que eu tinha perdido, que decidem mais ciência que várias da lista acima:
`MTL_SKIP_INERT_PRIOR` (default ON, **não documentada**), `REGION_EMB_ENGINE`
(`folds.py:971-973` — uma chave de substrato duplo, não documentada, **no caminho do joint**: a gêmea
MTL do `--region-emb-source` do p1), `MTL_STREAM_TRAIN_METRIC` (`mtl_cv.py:1505`),
`MTL_ALIGNED_DERANGE` (`folds.py:579`), `MTL_BETA_NO_WD` (`helpers.py:170-174`),
`MTL_DATASET_CPU`/`MTL_DATASET_GPU`, `MTL_GPU_HEADROOM_GB`, `INGRED_DEVICE`,
`DATA_ROOT`/`OUTPUT_DIR`/`RESULTS_ROOT` — e note que os ramos `Path("output")` do p1
(`p1:176-235`) **ignoram** `OUTPUT_DIR`, o que é um risco de misturar substratos.

**E um interruptor que nem é variável de ambiente:** `_auto_fp32_for_large_c`
(`mtl_cv.py:1151-1167`) torna a precisão de uma execução sem flags **dependente do estado** — AL em
fp16, FL/CA/TX em fp32. O S11 tem que registrar que o fp32 do v18 veio do pin explícito, e a config
do projeto novo tem que ser dona dessa decisão de forma declarada.

**Regra do projeto novo: nenhuma variável de ambiente decide comportamento científico.** Tudo em
configuração explícita, serializada junto do resultado. Variáveis de ambiente ficam permitidas
apenas para o que é genuinamente de ambiente (caminho de cache, device visível).

---

## 6 · Funcionalidade obsoleta — não carregar

| O quê | Evidência de que morreu |
|---|---|
| ~20 ramos de `--region-emb-source` (design_b/d/e/h/i/j/k/m, resln_*, substrate_s1/s3b/s4, poi2vec, postpool, c2hgi_hgi_concat) | O v18 usa **um**: `check2hgi_design_k_resln_mae_l0_1` |
| 11 cabeças em `ALL_HEADS` do p1 | O v18 usa **uma**: `next_stan_flow` |
| Balanceadores MTL adaptativos: NashMTL, PCGrad, GradNorm, CAGrad, Aligned-MTL, DWA, FAMO | O v18 usa `static_weight`; o catálogo de 27 levers marca a família como refutada/nula em G |
| Arquiteturas MTL alternativas: PLE, CGC, MMoE | Não usadas pelo v18 |
| Engine FUSION + `full_fusion_ablation` + `pipelines/fusion.pipe.py` | Estudo arquivado; nenhuma célula v18 |
| Engines DGI, HMRM, Time2Vec, Space2Vec, Sphere2Vec, POI2HGI | Nenhuma célula v18; HGI só aparece como baseline de substrato |
| `--task category` (categoria a partir de embedding de POI) e todo o protocolo de POIs ambíguos em `create_folds_mtl` | O par de tarefas do v18 é {next_category, next_region}, ambas sobre as mesmas linhas |
| Seletores `joint_f1_mean` e `geom_lift` | v18 usa `geom_simple`; os outros existem para reproduzir v11 |
| `--canon` v11/v12/v15/v16/v17 e todo o mecanismo de bundle | O v18 passa `--canon none` + receita explícita |
| Modos de fusão do prior: `log_t_kd`, `log_c_kd`, `cat_kd` | Todos com peso 0 no v18 |
| `nyc`, `georgia` e demais estados | 6 datasets |
| Amostragem ponderada (`WeightedRandomSampler`) | Substituída por CE ponderada, e essa por logit adjustment |

**Regra de descarte:** se não aparece em `run_wave.sh` nem em `FINAL_SETTINGS.md`, não entra — a menos
que seja um guard de segurança científica (§3) ou um experimento explicitamente enfileirado em
`POSTPONED.md` / `future_works/`.

### 6.1 · Exceções: itens da lista acima que são carga estrutural

A revisão adversarial mostrou que a lista, aplicada literalmente, quebra os três caminhos. No repo
antigo esses itens são **acoplamentos de import**, não funcionalidade viva — no projeto novo eles
simplesmente não existem, mas o descarte precisa ser feito com o olho aberto:

| Item "obsoleto" | Por que não pode sumir sozinho |
|---|---|
| Balanceadores MTL | `mtl_cv.py:53` → `create_loss` → `_ensure_registered()` importa **as 21 losses** avidamente (`losses/registry.py:20-69`). `static_weight` morre junto se o registry não for podado na mesma mudança |
| `next_stan` | É a **classe base** das duas cabeças de região do v18 (`next_stan_flow/head.py:47`, `next_stan_flow_dualtower/head.py:49-50`) |
| Arquiteturas PLE/CGC/MMoE | Moram no mesmo `_components.py` que os blocos FiLM/Residual do MTLnet |
| Engine FUSION | `EmbeddingEngine` é avaliado no corpo de classes de `paths.py` e FUSION é ramificado em 6 métodos que o v18 atravessa |
| `--task category` | O **mapeamento de categorias** (`CATEGORIES_MAP` / `_map_categories`, `folds.py:383-385`) produz o `y_cat` que é o **rótulo de estratificação de todo split das três famílias**. Apagar a tarefa não pode encostar nele |
| `--canon none` | Não desliga o guard 3 do `_preflight_canon_guards`: a checagem de versão do torch roda incondicionalmente e sai com `SystemExit` sob `MTL_STRICT=1` (`train.py:1936-1940,1977-1979`) |
| Dependências HGI/POI2Vec | Os **dois** builders de substrato dependem delas: `build_study_repr.py:70-73,298-300` importa `POI2Region` de `research/embeddings/hgi` e as arestas de Delaunay; o builder do v14 é `scripts/probe/build_design_k_delaunay.py` e lê `output/hgi/<state>/temp/{pois,edges}.csv` mais a tabela POI2Vec. **Rebuild do substrato exige esse material** — ver §6.2 |

### 6.2 · Georgia — pendência para o autor

A decisão "os 6 datasets do v18" (AL/AZ/IST/FL/CA/TX) exclui **georgia**, que aparece na matriz mais
antiga (`RUN_MATRIX §0` fala em `{AL, AZ, FL, CA, TX, GE}` — Georgia no lugar de Istambul) e que
`future_works/mtl_improvement_catx_scale_conditional.md` nomeia como estado paper-grade do campeão-G.
O v18 não tem nenhuma célula de Georgia, então a decisão está correta para reproduzir o v18 — mas é
uma perda deliberada de cobertura em relação a uma linha de trabalho anterior. **Confirmar com o autor
antes de apagar.**

---

## 7 · Premissas de device

| Premissa | Onde | O que o projeto novo faz |
|---|---|---|
| `torch.compile` só em CUDA | `next_cv.py:112`, `p1:622` | Mantém: compile é opt-in e só em CUDA |
| autocast fp16 só em CUDA; MPS/CPU sempre `nullcontext` | `_single_task_train.py:76-82` | Mantém, mas a precisão vira config explícita |
| `_rank_of_target` cai para CPU em MPS quando N×C > 2³¹ | `metrics.py:169` | Mantém — é limite real do MPSGraph |
| `clear_mps_cache()` entre folds | `next_cv.py:208` | Mantém |
| tf32 é flag global de CUDA | `train.py` | Vira config, aplicada num único ponto |
| Dataset residente na GPU com auto-fit por RAM | `folds._dataset_device` | Mantém a ideia, simplifica a heurística |
| `num_workers=0` em todo lugar | `folds.py:315-328` | Mantém (dataset já está no device) |
| A40: torch 2.11.0+cu128, 46 GB VRAM, 125 GB RAM compartilhada, `/dados` 2,2 TB | `docs/infra/a40/` | Alvo primário de execução |
| Local: torch 2.11.0, MPS disponível, Python 3.12.11 | verificado | Alvo do gate barato |
| H100 via Lightning/Modal | `v18_2/MODAL_MANUAL.md` | Última fase |

**Regra:** um único ponto de seleção de device (CUDA → MPS → CPU) e **nenhuma implementação de modelo
duplicada por device**.

---

## 8 · Divergências entre metodologia documentada e implementação

Ledger aberto; cada item vira uma linha na documentação final do projeto novo.

**D1 · Receita de categoria.** `v18/METHODOLOGY.md §4` documenta dois tiers herdados de
`CEILINGS_N20_FINAL` (AL/IST em bs 2048 lr 0,005; resto bs 8192 lr 0,005). O que roda em
`run_wave.sh` é o `FINAL_SETTINGS` de 2026-08-09: **bs 8192 em todos**, lr 0,0025 (AL) / 0,0005
(AZ, IST) / 0,005 (FL, CA, TX). A metodologia descreve uma receita que não foi a executada.

**D2 · Precisão declarada vs executada — RESOLVIDA, mantida como lição.** Os sidecars de categoria
gravam `"precision": "fp32 (MTL_DISABLE_AMP=1)"`, o que foi falso em 8 de 10 células **da wave
superseded**. O driver foi corrigido (`run_wave.sh:202-206`) e essas células saíram do board; o campo é
verdadeiro nos números atuais. Fica no ledger porque é a evidência empírica que justifica a regra do §5.

**D3 · Logit adjustment: refutado num lugar, adotado em outro.** O catálogo de levers de 2026-06-27
lista "Calibrated cat loss (logit-adjust/focal/CB)" como **refutado** (cat −0,87 em τ=0,5), enquanto
o `FINAL_SETTINGS.md` do v18 o adota como *a* mudança principal (+2,86 dedicado / +3,18 MTL). Não é
contradição real — o catálogo mediu sobre o substrato **com vazamento** — mas nada no catálogo diz
isso, e um leitor futuro cruzaria os dois.

**D4 · Assimetria na definição de Acc@10 entre as famílias.** O MTL reporta
`top10_acc_indist × (1 − ood_fraction)`, que **assume que toda linha OOD é um miss**. A família
dedicada (`p1`) reporta `top10_acc` puro sobre todas as linhas de validação, onde uma linha OOD
*pode* acertar por acaso — a cabeça tem `n_regions = max(y_region)+1` saídas, cobrindo toda região
presente na tabela completa, inclusive as que só aparecem na validação (`p1:318`,
`folds.py:1565-1568`). Os dois são chamados de "FULL top10" e comparados diretamente.

**A assimetria é maior do que eu tinha registrado.** As duas famílias diferem não só no estimador,
mas também na **métrica de seleção de época**:

| | seleciona por | reporta |
|---|---|---|
| dedicada (o teto bancado) | `top10_acc` puro, todas as linhas | `top10_acc` puro |
| joint (diag-best) | `top10_acc_indist` | `top10_acc_indist × (1 − ood_fraction)` |

São duas quantidades diferentes lidas em épocas diferentes, e as tabelas publicadas as colocam lado
a lado. O `p1` retorna `per_metric_best["top10_acc"]["snapshot"]` e o driver banca
`aggregate['top10_acc_mean']`. Eu inicialmente reimplementei a família dedicada com a convenção do
joint, o que teria produzido números não comparáveis com todas as células bancadas — pego pela
revisão. O `scoring.single_task_best` agora devolve **as duas raias**, com a bancada como primária.

**MEDIDO em Alabama (2026-08-13, A40, seed 0, 5 folds): a assimetria é 9,5e-07 pp.**

A álgebra explica por quê. `top10_full = indist × (1−ood) = acertos_indist / N`, enquanto
`top10_raw = (acertos_indist + acertos_ood) / N`. As duas diferem **exclusivamente pelos acertos
OOD** — e em Alabama, com fração OOD de 0,4–0,7 % por fold, **nenhuma região não vista no treino
entrou no top-10 em nenhum dos cinco folds**. As duas convenções coincidem numericamente.

Isso é bem menor que o limite superior que eu tinha derivado (0,01–0,06 pp): a cota assumia que uma
classe nunca treinada pode cair no top-10 por acaso com probabilidade ~10/C, e na prática ela não
cai — os pesos de saída de uma classe nunca vista ficam abaixo dos de mil classes treinadas.

**Consequência prática:** nesta escala de região, a comparação dedicada-vs-joint **não** é
confundida pela diferença de estimador. Continua valendo reportar as duas colunas — o argumento é que
a igualdade é medida, não presumida, e não há garantia de que se mantenha num estado com fração OOD
maior.

Confirmado pela revisão, com o sinal e a ordem de grandeza: o viés é **unilateral** — só pode inflar a
coluna **dedicada**, e portanto **deflacionar o Δreg**. Cota superior:
`ood_fraction × P(acerto@10 | classe nunca treinada)`; com OOD ≤ ~3 % e logits quase uniformes dando
≤ 10/C ≈ 2 %, o pior caso fica em ~0,06 pp, realisticamente O(0,01 pp) na melhor época. Irrelevante
para C8 (+1,9 pp), mas **da mesma ordem dos vereditos de ±0,1–0,5 pp dos estados pequenos** (C2/C5/C6).
Por isso a medição das duas formas deixa de ser curiosidade e vira **coluna dupla obrigatória**.
Nota relacionada: o **seletor** do joint consome `top10_acc_indist`, não a versão escalada por OOD
(`mtl_cv.py:974,207`) — a distinção tem que sobreviver.

**D5 · `--per-fold-transition-dir` no joint é uma flag morta.** O comando aponta para o diretório de
transições do v14 enquanto `freeze_alpha=True, alpha_init=0.0, log-t-kd 0.0` tornam o prior
identicamente nulo — e `MTL_SKIP_INERT_LOGT` (default ON) faz o carregamento ser pulado por completo.
A flag não custa nada; ela apenas **descreve uma dependência que não existe**, e um leitor futuro
concluiria que o campeão precisa dos arquivos `region_transition_log_*.pt`. Não precisa.

**D6 · Significância declarada vs qualificada.** `V18_RESULTS.md` marca "beats" em deltas de ~0,1 pp,
e o próprio documento (§ disclosures) avisa que os testes agregam pares (seed, fold) como se fossem
independentes, quando as 5 folds de uma seed compartilham ~80 % dos dados de treino — os p-valores são
anti-conservadores e a unidade honesta é a seed. **A lista de aceitação deste rewrite não pode
consagrar uma significância que a própria fonte repudia.**

**D7 · O `n` das tabelas.** Em `V18_RESULTS.md §1`, `n` é lido do campo de categoria
(`make_results.py:156`), então TX/CA aparecem com um `n` que vale para a coluna de categoria mas não
para a de região — só a família **dedicada de região** parou nas seeds {0,1} (`PROVENANCE.md`).
Defeito do documento-fonte; registrar em vez de herdar.

**D13 · Os hiperparâmetros da cabeça não vêm da cabeça — e as duas famílias usam convenções
opostas.** Descoberto ao comparar a contagem de parâmetros do log de uma execução real da main com a
do meu porte. A flag `--model next_gru` troca apenas a **classe**; os hiperparâmetros continuam vindo
do `model_params` da fábrica da tarefa (`default_next`), que carrega **`num_layers=4, dropout=0.1`**.
O módulo `next_gru` tem defaults de **2 camadas e dropout 0.3**. Construir a partir do módulo dá
**644 359** parâmetros onde a execução reporta **1 433 863** — menos da metade do modelo, sem
nenhum sinal. Ler o arquivo da cabeça não diz o que rodou.

E a família de **região** faz o **oposto**: o `p1` declara explicitamente que "respeita os
hiperparâmetros default de cada cabeça; só passamos embed_dim, num_classes e seq_length", depois de
uma revisão anterior ter forçado um `hidden_dim` único em todas e desafinado várias. Então a cabeça
de região roda nos defaults do módulo (d_model 128, 4 heads, dropout 0.3) → **417 117** parâmetros,
que é exatamente o número que o `POSTPONED.md` cita como baseline dedicado de Alabama.

Duas confirmações independentes do porte correto: o log de uma execução viva e um documento de
estudo. No `mtlcheck` a identidade e a forma da cabeça vivem na receita e entram no fingerprint.

**D12 · Identificadores têm dtypes inconsistentes entre artefatos do mesmo engine — três instâncias,
todas silenciosas.** Medido ao construir a camada 2. Num único estado:

| identificador | `next.parquet` | `sequences_next.parquet` | `checkin_graph.pt` |
|---|---|---|---|
| `userid` | **string** | int64 | — |
| `placeid` | — | **string** | chaves int |

Mesmos valores, tipos diferentes. Cada uma falha de um jeito que não grita: agrupar o split por
`userid` string redesenha os folds (D10); procurar `placeid` string num mapa de chaves int erra
**todas** as linhas — e um `.get(pid, 0)` complacente em qualquer ponto desse caminho teria colocado
toda visita na região 0. O repo antigo se defende do primeiro com um `.astype(int)` sem comentário;
do segundo não se defende — funciona porque hoje recebe o tipo certo. No projeto novo virou
`mtlcheck.ids`, um ponto único de coerção que nomeia o identificador ao falhar.

**D10 · `userid` tem dtypes diferentes em dois artefatos do mesmo engine, e isso redesenha o split.**
Medido ao reproduzir os folds (teste E1): em `next.parquet` a coluna é **string**; em
`sequences_next.parquet` é **int64** — mesmos valores, mesma ordem. O `StratifiedGroupKFold` ordena
as chaves de grupo, e string ordena lexicograficamente (`'10' < '2'`), então agrupar pela forma
string **produz um split válido que não é o split**, sem nenhum sinal de erro. Verificado: com
string, as quatro seeds de reporte divergem da referência já no fold 1. O código antigo se protege
com um `.astype(int)` dentro do `load_next_data` — uma linha sem comentário, da qual depende a
comparabilidade de todas as células. No projeto novo virou `splits.as_group_ids`, documentada.

**D11 · A regra de janelamento é stride 1 **sem** janelas de cauda, e o `MIN_SEQ=10` é implicado.**
Determinado empiricamente contra as 96 326 janelas de referência: `MIN_SEQ` 5 e 10 dão o **mesmo**
resultado, porque com a cauda desligada um usuário precisa de 10 visitas para gerar sequer uma
janela. Consequência prática que não está escrita em lugar nenhum: **no stride 1 nenhum padding é
produzido** — toda janela tem nove visitas reais. É por isso que os dois idiomas de máscara que
coexistem nas cabeças (o `seq_lengths-1` do GRU e o robusto do STAN) concordam nestes dados.

**D9 · O join espacial de regiões é um filtro, e só é load-bearing em Istambul.** Medido ao
reimplementar a camada 1 (teste E10): nos **cinco estados americanos** o join com os census tracts
não descarta nenhum check-in — o corpus já foi segregado pelos mesmos polígonos, então todo POI cai
dentro de um. Em **Istambul** ele descarta **81 856 de 544 471 check-ins** (15 %), porque o corpus
Massive-STEPS não foi pré-filtrado pelas mahalle; sobram 462 615 check-ins e **520 das 972**
mahalle contêm POIs (`data/massive_steps_istanbul/graph_report.json`). Nenhum documento do estudo
menciona esse descarte, e ele é a razão pela qual a construção de grafo a partir do parquet bruto
reproduz cinco estados exatamente e erra Istambul por +80 103 arestas.

**D8 · Escopo real do "forward-only".** O fix cobre o **eixo de check-ins**. O sinal de treino do
pretexto continua vendo o futuro por outras vias: o `Checkin2POI` agrupa visitas futuras, o alvo de
reconstrução MAE é a distribuição de categorias do corpus inteiro, a normalização min-max do peso de
aresta é ajustada no corpus inteiro, e os grafos de Delaunay / adjacência de região não são tocados.
Além disso, **a torre de região consome embeddings v14 totalmente bidirecionais**. Isso não invalida o
v18 — invalida a leitura de que "v18 é causal em tudo".

---

## 9 · Componentes genuinamente compartilhados

O que as quatro linhas (categoria, região, joint, substrato) realmente dividem:

- **Leitura do corpus** `data/checkins/<State>.parquet` → filtragem → mapeamento de usuários, POIs,
  categorias e regiões;
- **Construção de sequências** (janela 9+1, `MIN_SEQ=10`, stride 1) — uma implementação, consumida
  pelas três famílias de treino;
- **Split** `StratifiedGroupKFold` por usuário — literalmente o mesmo split (§ S1);
- **Métricas** — `StreamingClsMetrics` já é a implementação única, consumida por
  `mtl_eval`/`mtl_cv`/`p1`/`_single_task_train`;
- **Seleção de época** — `src/tracking/scoring.py`, stdlib-puro, já é fonte única;
- **Laço de treino/validação** — hoje **três cópias**; é a duplicação que este rewrite elimina;
- **Serialização de resultado** — hoje três formatos (sidecar do driver, JSON do P1, `MLHistory`);
  vira um.

O que **não** deve ser compartilhado, por decisão do autor: o fluxo do `check2hgi` (grafo → substrato)
e o fluxo de construção de input do modelo. Contrato entre eles é **arquivo em disco**, não import.

---

## 10 · O que ainda não li (honestidade sobre a cobertura)

A fase 1 cobriu: as regras científicas do `closing_data`, os três caminhos de treino, folds,
métricas, seleção de época, a construção do substrato v18 e o `future_works`. **Ainda não li em
profundidade**, e vou ler ao implementar a camada correspondente:

- os modelos: `next_gru`, `next_stan_flow`, `next_stan_flow_dualtower`, `mtlnet_crossattn_dualtower`;
- o interior do `Check2HGIModule` (1 272 linhas) e `variants.py` (1 278);
- `research/embeddings/check2hgi/preprocess.py` (991 linhas) — construção do grafo;
- `scripts/train.py` (2 371 linhas, 93 flags) na íntegra;
- `scripts/integrity_v2/infer_checkins.py` — o readout de referência.
