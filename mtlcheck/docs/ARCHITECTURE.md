# mtlcheck — arquitetura

> Companheiro do [`SYSTEM_MAP.md`](SYSTEM_MAP.md). O mapa diz o que o v18 **é**; este documento diz
> como o `mtlcheck` o reconstrói.
>
> **Revisão 2** — incorpora a revisão adversarial do Fable 5 (3 blockers, 7 highs) e a avaliação
> dedicada da arquitetura de pastas. Ver [`REVIEW_LEDGER.md`](REVIEW_LEDGER.md) para a disposição
> item a item.

---

## 1 · Princípio organizador: três camadas, contrato de arquivo entre elas

A decisão estruturante do autor foi: **o fluxo do Check2HGI e o fluxo de construção de input do
modelo são coisas diferentes e não devem se acoplar.**

```
   data/checkins/<State>.parquet
              │
              ▼
   ┌──────────────────────────┐
   │  CAMADA 1 — substrate    │   CLI: mtlcheck check2hgi
   │  grafo → representação   │
   └──────────────────────────┘
              │  artefato + manifest.json  (o contrato)
              ▼
   ┌──────────────────────────┐
   │  CAMADA 2 — data         │
   │  substrato + check-ins   │
   │  → tensores + folds      │
   └──────────────────────────┘
              │  tensores + índices de fold
              ▼
   ┌──────────────────────────┐
   │  CAMADA 3 — train        │   CLI: mtlcheck train {cat,reg,joint}
   │  um runner, três tarefas │
   └──────────────────────────┘
              │  resultado em schema único
              ▼
        wave  +  score            CLI: mtlcheck wave / mtlcheck score
```

A camada 3 **nunca importa** da camada 1. O acoplamento que hoje é um symlink de filesystem
(`check2hgi_v18/<estado>/region_embeddings.parquet → check2hgi_design_k_resln_mae_l0_1/…`) vira uma
referência explícita no manifesto.

### 1.1 · O que o contrato de arquivo tem que carregar

A revisão mostrou que "um parquet numa pasta" não é contrato suficiente. O `manifest.json` de cada
artefato de substrato carrega, no mínimo:

| Campo | Por quê |
|---|---|
| identidade do engine + hash do conteúdo | Sem isso, "qual substrato produziu este número" volta a ser inferência por caminho de arquivo |
| `placeid_to_idx`, `poi_to_region` | O `p1` hoje lê esses mapas do engine **canônico** (`p1:249`, `IoPaths.CHECK2HGI` fixo) mesmo sob `--engine-override check2hgi_v18`. Eles não pertencem a nenhum dos dois substratos que o plano reconstrói — pertencem ao contrato |
| proveniência do espaço de linhas: engine de origem, janela, stride, `MIN_SEQ` | O `next.parquet`/`next_region.parquet` do v18 são **copiados verbatim** do engine `check2hgi_dk_ovl` (`materialize_engine.py:93-95`). Reproduzir o v18 exige reproduzir esse espaço de linhas, não inventar um novo |
| `n_regions` e a regra que o derivou | É `max(y_region)+1` sobre a tabela **completa** — não `#unique`, não só-treino (S6/M4) |
| referência ao substrato de região usado | Substitui o symlink |
| build config completo + contagem de arestas antes/depois | É contra isso que o teste E10 roda, sem GPU |

**Dependência que o descarte não pode levar junto:** os dois builders de substrato dependem de
artefatos HGI/POI2Vec (`build_study_repr.py:70-73,298-300` importa `POI2Region` e as arestas de
Delaunay; o builder do v14 é `scripts/probe/build_design_k_delaunay.py` e lê
`output/hgi/<state>/temp/{pois,edges}.csv` mais a tabela POI2Vec). O "rebuild dos 6 estados" tem
essas dependências como **pré-requisito nomeado**, não como surpresa.

---

## 2 · Layout do repositório

```
mtlcheck/
├── pyproject.toml            # uv; [project.scripts] mtlcheck = "mtlcheck.cli:main"
├── uv.lock                   # um lockfile para Mac / A40 / Modal
├── CLAUDE.md                 # porta de entrada do agente → docs/ARCHITECTURE.md + studies/README.md
├── src/
│   └── mtlcheck/             # src-layout: importa o pacote instalado, não o checkout
│       ├── config.py         # dataclasses congeladas + loader de receita + hash da config resolvida
│       ├── paths.py          # DATA_ROOT / ARTIFACTS_ROOT / RUNS_ROOT — as ÚNICAS env vars permitidas
│       ├── device.py         # ponto único CUDA → MPS → CPU + precisão
│       ├── seeding.py        # contrato de semeadura (incl. reseed por fold)
│       ├── substrate/        # camada 1: corpus, graph, features, encoder, train, readout, region
│       ├── data/             # camada 2: sequences, splits, tensors, loaders, pairing
│       ├── models/           # camada 3: gru, stan_flow, joint
│       ├── train/            # camada 3: runner único + losses, metrics, scoring, stats, result
│       ├── wave/             # parser de manifesto + executor + lane Modal
│       └── cli/              # subcomandos: check2hgi, train, wave, score
├── recipes/                  # receitas congeladas e versionadas — o ÚNICO jeito de parametrizar ciência
│   └── v18/                  # substrate.toml, cat.toml, reg.toml, joint.toml
├── tests/
│   ├── equivalence/          # E1-E11 e S1-S16 como testes executáveis
│   └── test_studies_contract.py   # CI: nada de torch, laço de treino ou arquivo >1 MB em studies/
├── docs/                     # só prosa, curada, pequena
│   ├── SYSTEM_MAP.md · ARCHITECTURE.md · REVIEW_LEDGER.md
│   ├── CLAIMS.md             # conclusões promovidas
│   ├── DIVERGENCES.md        # o ledger D1-D8
│   └── infra/                # a40.md, modal.md, local.md
├── studies/                  # workspaces de pesquisa isolados (ver §5)
│   ├── README.md · log.md · _template/ · <estudo>/ · archive/
├── data/                     # gitignored — bruto
├── artifacts/                # gitignored — substrato (44 GB); manifest.json é a exceção COMMITADA
├── runs/                     # gitignored — saídas por execução: runs/<estudo>/<cell-id>/
└── scratch/                  # gitignored, efêmero; nada aqui pode ser citado por um board
```

Alvo de tamanho: **~3 500 linhas** no pacote. É estimativa, não gate — o builder do v14 (Delaunay +
POI2Vec + MAE) e a camada de estatística podem estourar.

---

## 3 · Decisões de design

### 3.1 · Um runner, três tarefas

`train/runner.py` recebe uma `TaskSpec` e roda o mesmo laço. A diferença entre famílias é **dados**:

| | categoria | região | joint |
|---|---|---|---|
| entrada | check-in `[N,9,64]` | região `[N,9,64]` | ambas |
| alvo | `next_category` (7) | `next_region` (C) | ambos |
| cabeça | `next_gru` | `next_stan_flow` | `next_gru` + `next_stan_flow_dualtower` sobre tronco |
| loss | CE + logit-adjust τ=0,5 | CE pura (τ=0) | τ=0,5 só na cat; região CE pura |
| weight decay | **0,01** | **0,01** | **0,05** |
| early stopping | **nenhum** (50 épocas) | **nenhum** (50 épocas) | **nenhum** |
| clipping | norma 1,0 | norma 1,0 | norma 1,0, modelo **e** critério |
| otimizador | AdamW | AdamW | AdamW, 3 grupos (cat/reg/shared) |
| pareamento | n/a | n/a | **aleatório no treino, alinhado na validação** |
| seleção | melhor macro-F1 | melhor Acc@10 | `geom_simple` + diag-best |

Os valores de weight decay e a ausência de early stopping vêm da leitura do código, não de
harmonização: `default_next` traz `weight_decay=0.01` e `early_stopping_patience=-1`
(`experiment.py:538,548`); `0.05` é o default do MTL. **Nenhum valor é unificado por conveniência.**

**Pareamento (S13) é o ponto mais perigoso.** A implementação "limpa" natural — um dataset devolvendo
`(x_cat, x_reg, y_cat, y_reg)` por linha — seria pareamento **alinhado**, e todo o v18 treinou com
pareamento **aleatório**. O runner implementa o aleatório como modo fiel; o alinhado existe como
opção, desligada, e só entra por medição deliberada (o gate G0.1 continua aberto no repo antigo).

**Reconciliação do RNG.** O contrato de reseed por fold do `p1` (`seed_everything(seed + fold_idx)`,
que afeta init/shuffle e **não** a partição — a partição é calculada antes do laço a partir de
`random_state=seed`) vira o padrão de todas as famílias, porque é o que torna um fold independente da
ordem. Duas ressalvas da revisão, aceitas: (i) é mudança deliberada em cat/joint, **e a medição que a
justificaria ainda NÃO foi feita** — o A40 está ocupado, nenhuma comparação multi-seed existe; até lá
é mudança aceita, não medida; (ii) `seed + fold` **colide entre seeds** (seed 0/fold 1
compartilha stream com seed 1/fold 0), correlacionando levemente células que a estatística trata como
independentes. Derivação decorrelacionada (`hash(seed, fold)`) é melhor, mas quebra a identidade byte
a byte com o `p1` — se adotada, é quebra registrada, não silenciosa.

### 3.2 · Configuração explícita, serializada com o resultado

Uma dataclass congelada por camada, construída de um arquivo de receita + overrides de CLI.
**Nenhuma variável de ambiente decide ciência.** As três permitidas são de caminho:
`DATA_ROOT`, `ARTIFACTS_ROOT`, `RUNS_ROOT`.

A config **resolvida** (não a declarada), com hash, é serializada dentro do resultado. Ninguém mais
precisa acreditar num campo `precision` escrito à mão pelo driver — ele passa a ser lido do objeto que
o treino usou. Isso mata D2 na raiz.

O preflight é função pura sobre a config: uma receita com τ>0 na região é **rejeitada na construção**,
não avisada no log. Idem para empilhar logit-adjust com class weighting — a `CalibratedLoss` do repo
antigo compõe os dois alegremente (`calibrated.py:120-141`); a exclusividade é convenção lá e vira
invariante aqui.

E a decisão de precisão é **declarada**, nunca inferida: o `_auto_fp32_for_large_c`
(`mtl_cv.py:1151-1167`) do repo antigo torna a precisão de uma execução sem flags dependente do
estado (AL fp16, FL/CA/TX fp32). Aqui não existe "sem flags".

### 3.3 · Prior inerte é ramo ausente

Com `alpha_init=0.0` e `freeze_alpha=True`, o prior `α·log_T` **não é construído** — nem o tensor
`[C,C]` (289 MB em CA), nem o gather. O repo antigo já pula o gather desde `aab23985` (via
`MTL_SKIP_INERT_PRIOR`, default ON e não documentada) e já pula a carga do arquivo desde 2026-06-26
(`MTL_SKIP_INERT_LOGT`); o que sobra é o buffer. Contrato de reprodução herdado daquele commit: eager
exato, compilado ≤1,5e-4.

### 3.4 · Substrato: caminho rápido por padrão, guard preservado

Export one-shot como padrão (identidade provada, ≤3,1e-06 sobre todas as janelas). O readout por
janela continua como caminho de referência, e a montagem **hard-falha** se o manifesto não declarar
`forward_only == true`. Duas ressalvas: a equivalência foi medida em AL/AZ/IST/FL — **CA e TX estão
como `n/a` no `AUDIT.md`** — e a representação de Alabama nunca foi reconstruída (veio da célula E2 do
estudo). O teste E10 tem que dizer isso por estado, e o invariante forte que vale nos seis é
"depois == antes / 2, zero self-loops".

### 3.5 · Construção de dados vetorizada e cacheada

Sequências saem do loop Python (9 × `pd.Series.map`) para indexação vetorizada, com cache em disco por
(estado, engine, janela). Hoje três famílias × 6 estados × 4 seeds reconstroem o mesmo tensor; o cache
também remove o pico de ~66 GB de RAM que força FL/CA/TX a rodarem 1-wide.

### 3.6 · Device num lugar só

`device.py` resolve CUDA → MPS → CPU e devolve junto o contexto de precisão e as capacidades. Modelos
idênticos nos três devices. As duas concessões reais ao MPS sobrevivem porque são limites de
plataforma: fallback de `_rank_of_target` acima de 2³¹ elementos, e limpeza de cache entre folds.

### 3.7 · Camada de estatística é entregável, não detalhe

Os vereditos do v18 saem de **médias pareadas simétricas sobre as seeds comuns às duas colunas**.
Uma reimplementação ingênua (diferenciar médias não-pareadas) move vereditos sem mudar uma linha de
treino. `train/stats.py` é a implementação única, e todo número reportado carrega `n`, a unidade de
pareamento e a ressalva de que folds dentro de uma seed **não** são réplicas independentes (D6).

---

## 4 · Estratégia de equivalência

Barra: reproduzir as **conclusões científicas**. Isso exige uma lista fechada.

### 4.1 · Nível 1 — determinístico, sem GPU

Exatos, não aproximados.

| # | Teste | Critério |
|---|---|---|
| E1 | Índices de fold | Idênticos aos do `FoldCreator`/`p1`, 5 folds, cada (estado, seed) |
| E2 | Disjunção de usuários | Nenhum usuário em treino e validação da mesma fold |
| E3 | Contagens e regras | Linhas, classes, `n_regions` — e a **regra** que derivou `n_regions`, não só o número |
| E4 | Alinhamento | `userid` linha a linha entre a tabela de categoria e a de região |
| E5 | Sequências | Janelas byte-idênticas às de `sequences_next.parquet`, mesma ordem e padding |
| E6 | Parâmetros | Contagem por cabeça e por caminho idêntica (invariante S12) |
| E7 | **Transplante de checkpoint** | Carregar um `state_dict` antigo no modelo novo por um mapa de chaves documentado e comparar forwards em entradas fixas. *(Substitui o teste original "mesma seed → mesmos logits", que é impossível: um rewrite clean-room não consome o RNG na mesma ordem, e nenhuma tolerância fp32 concilia pesos diferentes.)* |
| E8 | Loss | CE e CE com logit-adjust τ=0,5 contra a implementação antiga, entradas fixas |
| E9 | Métricas e seleção | `StreamingClsMetrics` + diag-best/joint-best contra a implementação antiga |
| E10 | Substrato | Arestas antes/depois por estado; colunas de tempo idênticas ao `build.json`; invariante "depois == antes/2" nos seis |
| E11 | **Série de LR** | Despejar o LR por grupo de parâmetro a cada passo e diferenciar contra a implementação antiga (S15) |

Pré-requisito operacional: E1/E3/E4/E5 leem `next.parquet` / `next_region.parquet` /
`sequences_next.parquet` do `check2hgi_v18`, que **só existem no A40**. Primeira tarefa da fase 8 é
trazer os três parquets de AL (319 + 285 + 2 MiB) para a máquina local.

### 4.2 · Nível 2 — A40, estados pequenos

AL/AZ/IST, seeds {0,1,7,100}, 5 folds, as três famílias — as células que o v18 tem bancadas em n=20.

| # | Conclusão | Como verifico |
|---|---|---|
| C1 | O substrato forward-only derruba a categoria de forma massiva | AL dedicado na faixa do v18. **Ancorar por receita**: 28,23 é o harness da auditoria (sem logit-adjust); o board sob `FINAL_SETTINGS` é **30,77** (τ=0,5, lr 0,0025). Confundir os dois faz o gate "falhar" por ~2,5 pp estando certo |
| C2 | Região é praticamente invariante ao fix do vazamento | Região dedicada em AL/AZ/IST batendo o v18 |
| C3 | Logit adjustment τ=0,5 ajuda a categoria | A/B na categoria dedicada. **O braço τ=0 do v18 NÃO é CE pura**: com `--logit-adjust-tau 0.0` a calibração fica vazia (`train.py:1396` testa truthiness) e o critério cai na CE **balanceada por pesos de classe** (`experiment.py:545`, `next_cv.py:138-141`). O lever medido é "τ=0,5 substitui pesos balanceados". O comparador tem que ser esse |
| C4 | τ machuca Acc@10 de região e ajuda o macro-F1 dela | A/B na região, os dois sinais na direção prevista |
| C5 | Nos estados pequenos MTL empata com os tetos (±2 pp) | Δcat e Δreg dentro da banda, mesmo sinal. **Banda larga demais para servir de gate sozinha** — ver §4.5 |
| C6 | Em Istambul o MTL bate os dois tetos com margem pequena | Δ positivos, com a ressalva D6 sobre significância |
| C7 | diag-best e joint-best concordam | ⚠ **Sem âncora no v18**: a lane joint-best está vazia (`V18_RESULTS.md §2` todo "—"; o driver chama o scorer com `|| true`). Ou eu populo essa lane nas execuções do gate, ou C7 vira "as duas convenções são calculadas e reportadas", sem limiar |

### 4.3 · Nível 3 — um estado grande

Florida primeiro (custo), California só se Florida deixar dúvida.

| # | Conclusão | Critério |
|---|---|---|
| C8 | Nos estados grandes o MTL bate o teto de região com margem real (FL +0,39; CA +1,96) | Δreg positivo e de magnitude comparável |

### 4.4 · O que não vou tentar provar

Igualdade dígito a dígito no treino — inatingível no próprio v18, que roda com `--compile` e cujo
`METHODOLOGY.md §5.2` registra que números compilados são "within-fold-std mas **não**
bit-reproducíveis".

### 4.5 · O que C1-C8 não pegaria (e os testes que fecham o buraco)

A revisão perguntou isso diretamente. O que passaria por todas as oito conclusões:

- **pareamento cruzado trocado de aleatório para alinhado** → coberto por S13 + um teste que checa que
  os dois train loaders têm embaralhamentos independentes;
- **clipping de gradiente removido** → S14, teste de configuração;
- **scheduler avançando por época em vez de por batch** → E11;
- **estatística não-pareada** → teste unitário de `stats.py` contra os pares do `v18_results.json`;
- **coluna de região mudando de estimador** → coluna dupla obrigatória (D4).

---

## 5 · O sistema de `studies/`

O `docs/studies/` do repo antigo funcionou muito bem para estudos isolados conduzidos por agentes, e
é preservado — em `studies/` no topo, **fora de `docs/`**, com um contrato anti-deriva.

**Por que fora de `docs/`:** os estudos do repo antigo são workspaces operacionais, não documentação.
`closing_data/v18` guarda 30+ drivers de shell e `train_perf_multifold` guarda `.out` e diretórios de
execução inteiros — dentro de `docs/`. É assim que `docs/` chegou a 256 MB e que "documentação" virou
executável e derivou. Repo separado foi rejeitado (fixar SHA entre repos adiciona atrito, e a eficácia
com agentes vinha justamente de ter estudo + código + registro num checkout só). Branch como casa foi
rejeitado (o `closing_data` atravessa meses e vários PRs; o registro tem que viver na main) — mas a
convenção `CLAUDE.local.md` de ponteiro por branch é mantida, porque funcionou e não custa nada.

**O que um estudo pode conter:** prosa (`STUDY.md`, `STATE.md`, `log.md`), manifestos de wave (dados,
não código), `status.json`, scripts de análise **read-only**, e o board commitado.

**O que um estudo nunca pode conter:** laço de treino, código de modelo/métrica/scoring, cópia de
driver, ou qualquer import de torch. Isso mira exatamente o `p1_region_head_ablation.py` — a cópia
do laço que ficou dois meses atrás dos fixes de `src/` — e o `run_wave.sh`, cujo `export` em função de
shell rodou 8 de 10 células de categoria em fp16. **Enforcement por CI** (`.github/workflows/tests.yml`, criado em 19-08 — até então a frase era uma alegação sem job)
(`tests/test_studies_contract.py`), não por convenção.

**Como um estudo parametriza sem forkar o runner:**
`mtlcheck train --recipe recipes/v18/cat.toml --set max_lr=0.005 --state alabama --seed 0`, ou um
manifesto de wave listando células como referência-de-receita + overrides. Se o estudo precisa de
**comportamento** novo, ele entra em `src/mtlcheck/` atrás de um campo de config, passando pelos
testes de equivalência; o estudo então o referencia por receita.

**Ciclo de vida:** copiar `_template/` → preencher `STUDY.md` com a pergunta e as referências
congeladas (SHA do código, versões de receita, hashes dos manifestos de substrato) → linha no
registro. As waves anexam células ao `status.json`. Um agente que retoma lê `STATE.md` + `status.json`.
No fechamento: `CLOSURE.md`, promoção das conclusões sobreviventes para `docs/CLAIMS.md`, `git mv` para
`studies/archive/`, e apagar o bulk de `runs/<estudo>/` exceto as células citadas pelo board.

**Fronteira de artefatos:** registro científico commitado = `studies/<x>/board/` (board em markdown +
JSON agregado pequeno, cada número carregando cell-id, hash de config e SHA do código). Bulk
gitignorado = `runs/<estudo>/<cell-id>/` e `artifacts/substrate/<engine>/<estado>/`, este último
representado no git só pelo `manifest.json`. No A40, `RUNS_ROOT` e `ARTIFACTS_ROOT` apontam para
`/dados` — o que resolve o P9 (`/home` a 90 %).

---

## 6 · Ordem de execução

| Fase | Entrega | Depende de |
|---|---|---|
| 3 | Esqueleto: pyproject/uv, config, paths, device, seeding, CLI, contrato de studies + CI | — |
| 4 | Camada 1: substrato v18 + substrato de região; pré-requisitos HGI/POI2Vec; rebuild dos 6 no A40 | 3 |
| 5 | Camada 2: sequências, tensores, splits, pareamento, cache | 3 |
| 6 | Camada 3: runner único, losses, métricas, scoring, stats, schema de resultado | 5 |
| 7 | `wave` + `score` | 6 |
| 8 | Validação nível 1 → 2 → 3 | 6 |
| 9 | Documentação + ledger de divergências | 8 |
| 10 | Lane Modal | 7 |

As fases 4 e 5 são independentes: a camada 2 pode ser construída e validada contra o substrato
`check2hgi_v18` que já existe no A40 enquanto a camada 1 é reescrita. Se a camada 2 funciona contra o
substrato antigo **e** contra o novo, o contrato de arquivo está certo.

---

## 7 · Future work incorporado agora (e o que fica de fora)

Cabível agora, porque é refatoração e não muda resultado:

- **`p1_val_loop_to_src.md`** — é literalmente esta reescrita; seus critérios de aceite viram E1-E11;
- **`head_window_batch_audit.md` §B** (auditoria de janela / máscara causal) — sai de graça ao
  reimplementar `sequences.py`. Invariante a declarar explicitamente: **o padding é estritamente
  posterior** (`core.py:263`), que é o que torna o idioma `seq_lengths-1` do `next_gru` equivalente ao
  idioma robusto do STAN;
- **STAN U1/U2** — hardening bit-idêntico nos dados atuais; implemento a forma robusta desde o início;
- **coluna raw `top10_acc` ao lado de `_indist`** (`pipeline_audit_quality_followups.md`) — é a
  medição de D4.

**Fora de escopo por decisão explícita** — mudariam os números de comparação: estratificação por chave
composta; CV aninhado (`evaluation_protocol_cleanup.md`); qualquer lever do catálogo de 27; ativar o
prior `α·log_T`; sweep de arquitetura de cabeça de região; adotar pareamento alinhado.

Memos ainda não incorporados e que precisam de leitura antes da fase 6:
`per_head_lr_onecycle_fix.md` (o mecanismo por trás do aviso do §2.3 do mapa),
`part2_mtl_dual_substrate_routing.md` (documenta `REGION_EMB_ENGINE`),
`overlapping_windows.md` (o registro de adoção da janela `dk_ovl` que o rewrite tem que reproduzir),
`composite_two_substrate_engine.md` (precisa de HGI em FL/CA/TX).

---

## 8 · Riscos

| Risco | Mitigação |
|---|---|
| **Converter o joint de pareamento aleatório para alinhado sem perceber** | S13 + teste de embaralhamentos independentes; é o risco nº 1 e nenhuma conclusão C1-C8 o pegaria |
| Ao unificar o laço, mudo silenciosamente a semântica de uma família | Cada diferença real está na tabela do §3.1 com o valor que rodou; nenhuma é harmonizada |
| O reseed por fold vira padrão e desloca cat/joint | Mudança deliberada, medida em AL nas 4 seeds nas duas famílias; colisão `seed+fold` registrada |
| Rebuild do substrato não reproduz o v18 | E10 checa grafo e features sem treinar; o espaço de linhas `dk_ovl` é entregável nomeado |
| Perder um guard científico ao simplificar | S1-S16 numeradas, cada uma vira teste |
| Fechar por acidente a pergunta capacidade-vs-sinergia | S12 testada |
| Um estudo futuro copiar o driver de novo | Contrato de `studies/` + linhagem recusada no consumo. ⚠ O contrato sozinho **não** pegou o caso real de 19-08: os drivers estavam FORA do repo, e o que fechou foi `assert_comparable` |
