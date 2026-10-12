# Plano priorizado — triagem das três fontes

**Criado 2026-08-19.** Reconcilia as três fontes que o [`STUDY.md`](STUDY.md) nomeia. Cada veredito
foi **verificado contra o código do mtlcheck**, não contra a memória dos documentos — duas entradas
de ledger da própria fonte B estavam desatualizadas em relação ao código (ver R3 e §8a abaixo), o
que confirma que verificar era necessário.

## Os cinco vereditos

| veredito | significado |
|---|---|
| **DONE-BY-PORT** | o porte já entrega; o arquivo que prova está citado |
| **OBSOLETE** | a premissa caiu — pela v19, pelo protocolo aninhado, ou por medição que já fechou a pergunta |
| **IMPLEMENTATION** | melhoria real da máquina; **este estudo é o dono** |
| **RESEARCH** | pergunta científica aberta sobre o *modelo*; este estudo só registra e roteia |
| **SUPERSEDED** | dobrado em outro item, nomeado |

**Contagem: 7 IMPLEMENTATION · 8 RESEARCH · 10 OBSOLETE · 4 SUPERSEDED · ~30 DONE-BY-PORT**
(6 memos/sub-itens da fonte C + 24 itens de otimização/defeito da fonte B).

---

## 1 · Tabela de triagem completa

Nada é descartado em silêncio: toda ideia das três fontes tem uma linha.

### Fonte A — `porting_validation/IMPROVEMENTS_BACKLOG.md` (5 itens, re-ranqueados)

| # | ideia | veredito | por quê |
|---|---|---|---|
| A1 | `mae_poi_target_dim` 8→7 | **IMPLEMENTATION** | veredito CORRIGIR já dado no backlog; medido AL 1 réplica (+0,116 cat, −0,053 reg); falta multi-réplica. Rebuild de substrato em todos os estados |
| A2 | Delaunay: descasamento de unidades (`fix_unit_mismatch=True`, existe desligado em `src/mtlcheck/substrate/delaunay.py:149`) | **IMPLEMENTATION** | pendente de medição; redefine o grafo inteiro → a mais cara da lista |
| A3 | POI2Vec: grafo caminhado dirigido (`symmetrise=True`, existe desligado em `src/mtlcheck/substrate/poi2vec.py:287`) | **IMPLEMENTATION** | pendente de medição; efeito a jusante nunca medido |
| A4 | substrato por fold (fechar os canais transdutivos que o forward-only não cobre) | **RESEARCH** | outro protocolo, outra conta de compute, incomparável com tudo bancado — o próprio backlog o declara fora de escopo. Estudo próprio, se um dia |
| A5 | retenção de checkpoint para o §8a | **IMPLEMENTATION** | `eval/optimism.py` existe e está testado; falta a política de retenção. É **telemetria**, fora do `science_fingerprint` (`config.py:433`) → **não força versão de receita** |

### Fonte B — `docs/OPTIMIZATIONS.md` + `docs/REFERENCE_DEFECTS.md`

| # | ideia | veredito | por quê / prova |
|---|---|---|---|
| P1, P2, P5–P8, P10, P11 | runner único, prior-ramo-ausente, memória de build, streaming, class-weights, passada extra, negativo-duro vetorizado, cronômetros | **DONE-BY-PORT** | marcados ✅ feito no próprio `OPTIMIZATIONS.md`, com medição |
| P3 | `torch.compile` refeito a cada fold | **IMPLEMENTATION** | única lacuna declarada; só wall-clock, com risco de fidelidade documentado |
| P4 (resíduo) | cache em disco do tensor de check-in (hoje só a torre de região tem) | **IMPLEMENTATION** | perf pura; o tensor é relido do parquet a cada célula |
| P9 (resíduo) | apontar `RUNS_ROOT`/`ARTIFACTS_ROOT` para `/dados` no A40 | **IMPLEMENTATION** | mecanismo pronto; falta o apontamento na execução. Uma linha de ops |
| — | CUDA Graphs / "o laço é launch-bound" | **OBSOLETE** | medido FALSO para o mtlcheck em 2026-08-16: 98–100 % de utilização (`OPTIMIZATIONS.md §Já medido`). Perseguir isso persegue ~0 % |
| R1–R2, R4–R13, R15–R16 | trio de LR, precisão explícita, ids, loader, prior, vocabulário, coluna de tempo, `n` por coluna, scorer, pooling, torre privada, guard de RAM, negativo-duro sem gate, determinismo de build | **DONE-BY-PORT** | todos ✅ implementado no ledger, verificados por amostragem no código (ex.: trio de LR em `config.py:199–207`; `memory.py`; determinismo em `substrate/training.py`) |
| R3 | env var vazando entre células | **DONE-BY-PORT** | o ledger diz "parcial — o executor de wave ainda não existe", mas está **desatualizado**: `src/mtlcheck/train/wave.py` existe, é o executor declarativo, e `cli.py` o expõe (`mtlcheck wave run`). Atualizar a linha do ledger ao fechar este plano |
| R14 | auditoria de capacidade conta a cabeça errada (toca citação da dissertação e do MobiWac) | **DONE-BY-PORT** (lado máquina) | o mtlcheck ancora contra 1 433 863 (teste E6). O **resíduo é uma errata de dissertação, decisão do autor** — roteado para fora deste estudo, registrado aqui para não sumir |

### Fonte C — `ingred/docs/future_works/` (16 memos)

| memo | veredito | por quê / prova |
|---|---|---|
| `evaluation_protocol_cleanup.md` | **DONE-BY-PORT** | é exatamente o protocolo do mtlcheck: 70/10/20 com teste externo lacrado (`docs/EVALUATION_METHOD_GUIDE.md §0–§2`, `docs/plans/EVALUATION_PROTOCOL.md`), pooling OOF (§1 do guia), `split_seed` ≠ `model_seed` (`NOMENCLATURE.md`, erro #5), predições linha a linha sempre gravadas (STATE do porte §3), fail-closed de partição. Até o alerta "não cite n=20" virou o erro #3 do guia |
| `p1_val_loop_to_src.md` | **DONE-BY-PORT** | um runner serve as três famílias (`src/mtlcheck/train/runner.py`, cabeçalho: "The reference has three… the region one fell two months behind"); o contrato de estudos **proíbe** cópia de laço (`tests/test_studies_contract.py`) |
| `per_head_lr_onecycle_fix.md` | **DONE-BY-PORT** | a presença dos três valores É a ativação e a família joint recusa construir sem eles (`config.py:199–207, 360–371`; R1). Os dois itens abertos do checklist morreram: o teste de paridade flag-OFF não tem objeto (não há flag), e a promoção bs=8192 + cat-lr já está na v19 (`recipes/v19/joint.toml`: `batch_size = 8192`, `[train.optim.cat_lr_by_state]`) |
| `overlapping_windows.md` | **DONE-BY-PORT** | o próprio memo se marca superseded (adotado 2026-06-19/21); a v19 é stride-1 com MIN_SEQ=10 (`recipes/v19/joint.toml [data]`) |
| `pipeline_audit_quality_followups.md` #1 (cond_coupling × aligned) | **OBSOLETE** | testado e fechado na referência (PAIRING_BATTERY 2026-07-02): nunca bate a base; "não reabrir sem mecanismo novo" |
| — #2 (G0.1 binding, aligned pairing multi-semente) | **RESEARCH** | a única pergunta de pairing ainda viva. O mtlcheck a carrega explicitamente: `Pairing.ALIGNED` existe e o comentário da v19 diz "whose gate was never closed" (`config.py:41`, `recipes/v19/joint.toml`). Pergunta sobre o modelo → estudo próprio |
| — #3 (batch-level pairing) | **OBSOLETE** | desmotivado pela battery (random-other ≡ base; não há gap a fechar) |
| — #4 (β no-WD + trajetória) | **RESEARCH** | sonda de mecanismo que só faz sentido acoplada a um braço aligned (#2); roteia junto |
| — #5 (higiene de input: OOV≠pad, piso de contexto por janela, top10 cru, categoria do alvo) | **OBSOLETE / DONE-BY-PORT** | sob stride-1 **não existe padding** — o mtlcheck **asserta** isso (`data/materialize.py:62–74`), então os levers de pad não têm objeto. O top10 cru já é emitido junto do descontado (`train/metrics.py:244–272`: `top10_acc_indist` + `top10_full` + `ood_fraction`) |
| — #6 (estratificação por suporte de região) | **OBSOLETE** | diagnóstico fechado 2026-07-06: eixo não-estratificado é inócuo (OOD ≤3 %, piso estrutural); manter split congelado |
| — #7 (aligned × cross-stitch, screen promissor) | **RESEARCH** | eixo arquitetura×pairing; screening-grade, sem claim. Roteia para o estudo de arquitetura MTL |
| `task_pivot_memo.md` | **OBSOLETE** (para este estudo) | prosa histórica de dissertação, não máquina; o par de tarefas já está incorporado no mtlcheck. Se quiser preservar o racional, o destino é `articles/dissertacao/`, não aqui |
| `paper_canon_reevaluation.md` | **SUPERSEDED** | premissa era re-analisar os run dirs v11 do repo antigo sob o selector novo. O protocolo aninhado substituiu a convenção inteira de seleção, e a re-avaliação contra a dissertação é o item aberto #17 do `porting_validation` — é lá que isso vive agora |
| `substrate_adaptive_mtl_balancing.md` | **RESEARCH** | balanceadores de loss = pergunta aberta sobre o modelo. Nota de custo: o mtlcheck implementa deliberadamente só 3 critérios (`train/losses.py`, cabeçalho) — qualquer balanceador entra em `src/` atrás de campo de config, nunca num estudo (contrato de `studies/README.md`) |
| `mtl_architecture_revisit.md` | **RESEARCH** | MMoE/CGC/DSelect-K/cross-stitch fiéis = agenda de arquitetura; o mtlcheck só carrega gru/stan/joint (`src/mtlcheck/models/`). Estudo próprio, absorve o #7 acima |
| `head_window_batch_audit.md` §A (heads) | **RESEARCH** | sweep de cabeças por tarefa; roteia com o estudo de arquitetura |
| — §B (auditoria janela/máscara) | **DONE-BY-PORT** | a camada determinística do porte validou janelas/folds/loss/métricas contra a referência (`studies/log.md` 2026-08-13), e stride-1 eliminou o padding cuja máscara era a preocupação (assert em `materialize.py`) |
| — §C (balanceamento de batch) | **OBSOLETE** | sampler falsificado na referência (−18 a −30 pp); a variante focal também: focal foi medido e refutado no catálogo de levers e o mtlcheck deliberadamente não o carrega (`train/losses.py`) |
| `reg_head_architecture_sweep.md` | **SUPERSEDED** | o próprio memo diz que rola para dentro do `head_window_batch_audit §A` / arquitetura — mesma rota RESEARCH |
| `joint_selection_and_loss_combination.md` Parte 1 (upgrades de selector: Pareto-restrito, suavização, lift-over-baseline) | **RESEARCH** | o selector `geom_simple` já é o da v19; os upgrades são reviewer-proofing opcionais sobre o modelo de seleção. Nota: a "higiene" da Parte 1 (selecionar ≠ reportar) é DONE-BY-PORT — é o §2 do protocolo + o §8a (`eval/optimism.py`) |
| — Parte 2 (combinação de losses) | **SUPERSEDED** | o próprio memo manda fundir em `substrate_adaptive_mtl_balancing.md` — mesma linha RESEARCH |
| `composite_two_substrate_engine.md` | **OBSOLETE** | três mortes independentes: (a) a v19 unificou o substrato e o mtlcheck **não carrega HGI** (`src/mtlcheck/substrate/` é só a família check2hgi; o v14 bidirecional está arquivado em `576f7b85`); (b) a propriedade single-model é primária — composite concede a tese e nunca é headline (feedback registrado em memória); (c) os artefatos STL-HGI que ele roteava são do repo antigo |
| `part2_mtl_dual_substrate_routing.md` | **OBSOLETE** | falsificado por piloto na própria fonte (UPDATE 2026-06-02: routing 47,17 ≈ v14-only 47,18 ≈ canônico 47,15 — "o regime MTL é a parede") **e** a v19 eliminou a arquitetura de dois substratos que ele roteava |
| `poi_decoder_hgi_distill.md` | **OBSOLETE** | exigia o embedding POI do HGI como alvo de destilação — artefato que o mtlcheck não tem nem constrói; o memo se condicionava à rejeição do composite, que também caiu. Especulativo então, sem premissa agora |
| `mtl_improvement_catx_scale_conditional.md` | **SUPERSEDED** | as instruções de build (v14 design_k em CA/TX + log_T por fold) morreram com a v19; a completude CA/TX acontece na campanha confirmatória do mtlcheck (6 estados × 3 famílias × 4 réplicas, `QUAL_CONJUNTO_USAR.md §1`), não como card avulso. A predição registrada (margem cresce com C) fica preservada aqui: **testável de graça quando a campanha rodar** |

---

## 2 · Plano de execução — só os 7 itens IMPLEMENTATION

### A restrição que ordena tudo

Receitas são imutáveis uma vez citadas por célula bancada. Cada melhoria de ciência aplicada avulsa
força uma versão nova, e uma cadeia v20/v21/v22 destrói a consistência da v19. Então o plano separa
os itens em **dois grupos**:

- **Grupo receita (A1, A2, A3)** — mudam o que o substrato computa → entram **juntos, numa única
  v20**, depois de medidos individualmente por *waves de ablação* (receitas de ablação não são a
  linha canônica; `waves/ablations/mae7.toml` é o precedente).
- **Grupo sem-receita (A5, P4, P9, P3)** — telemetria, perf e ops. `retain_checkpoints` está fora do
  `science_fingerprint` por decisão registrada (`config.py:433`: "Telemetry is not science"); P4/P9
  não mudam número nenhum (P4 com prova bit-idêntica obrigatória, como o P5 teve). Podem ir **agora,
  sem tocar versão**.

### Ordem de execução

**Fase 0 — sem-receita, imediato (dias)**

1. **A5 · política de retenção de checkpoint.** O que muda: waves da campanha passam a declarar
   `retain_checkpoints="selected"`; `"every"` só no estado onde a decomposição do §8a rodar (a
   política que o próprio backlog sugere). Custo: disco (a decisão dos 125,5 GB foi sobre `every`
   em tudo; `selected` é ~1 checkpoint/célula). Risco: zero — telemetria, fingerprint de ciência
   intacto, resume não invalida. Dependência: nenhuma; **desbloqueia** a decomposição
   a1/b1/b2 que o `SEALED_BRIDGE_READ.md §2` diz ser necessária para interpretar o Δ. Junto: fechar
   o contrato de checkpoint (item aberto #12 do porting_validation — o que um script futuro pode
   assumir dos arquivos retidos).
2. **P9 · apontar `RUNS_ROOT`/`ARTIFACTS_ROOT` para `/dados` no A40.** Uma linha de ambiente de
   execução (não de ciência). Antes de qualquer campanha grande, senão ela enche `/home`.
3. **P4 · cache em disco do tensor de check-in.** O que muda: a torre de check-in ganha o mesmo
   cache que a de região; hoje o tensor é relido do parquet a cada célula. Custo: código + um teste
   de equivalência. Risco: zero **se e só se** a saída for provada bit-idêntica
   (`np.array_equal`, o padrão que `test_assembly.py` já estabelece para o P5). Medição: trivial —
   wall de duas células AL, mesma semente.

**Fase 1 — medição das três mudanças de substrato (waves de ablação em Alabama)**

4. **A1 · `mae_poi_target_dim` 7 — estender a 4 réplicas.** O veredito CORRIGIR está dado; o que
   falta é a grandeza que a dissertação publica (o backlog avisa: "uma réplica… um veredito firme
   exigiria quatro"). O `waves/ablations/mae7.toml` existe; é rodar as sementes que faltam.
5. **A2 + A3 · Delaunay unit-fix × POI2Vec symmetrise — medir JUNTOS, fatorial 2×2 em AL.**
   Por que juntos: A2 redefine os pesos de aresta que alimentam o POI2Vec, e A3 redefine a direção
   das caminhadas sobre o mesmo grafo — os efeitos não são separáveis medindo um de cada vez sobre
   bases diferentes. Braços: incumbente / +unit-fix / +symmetrise / +ambos, mesma partição, mesma
   semente. Custo: o build AL pós-P10 é ~16 s; o custo real são as células downstream (2 torres ×
   4 braços × sementes). **Piso de ruído entre sorteios: 0,034 pp** — como o substrato é uma
   amostra e não função da semente (R16), cada braço precisa de ≥2 sorteios para que um Δ < ~0,15 pp
   seja interpretável; uma célula AL lê a maioria dos efeitos. Risco da medição: zero (ablação não
   toca a v19).

**Fase 2 — a única versão nova de receita**

6. **Congelar a v20 = v19 + mae7 + (A2/A3 conforme a Fase 1).** O que muda: uma versão, um rebuild
   de substrato nos 6 estados, um re-treino das famílias base. Custo: o maior do plano — é a conta
   que já existia para qualquer melhoria de substrato; pagá-la uma vez é o objetivo do agrupamento.
   Riscos, ditos abertamente:
   - **Quebra a comparabilidade com a dissertação de propósito** — todo número v20 é coluna 3 do
     `DIVERGENCE_REGISTER.md` (melhoria real) e tem de nomear as mudanças ao ser citado.
   - **Nenhum artefato v19 é sobrescrito.** Células bancadas citam a v19; a identidade de substrato
     gravada na célula (STATE do porte §3) invalida resume se alguém trocar por baixo — é para isso
     que a guarda existe, não a contorne.
   - **Ponto de decisão do autor**: se a Fase 1 mostrar que A2 ou A3 *pioram*, a escolha é entre
     coluna 2 (defeito reproduzido, declarado — fica fora da v20) e coluna 3 por princípio. O plano
     não presume; o mae7 entra de qualquer forma (veredito já dado, efeito não-negativo).

**Fase 3 — perf opcional, depois de tudo**

7. **P3 · reutilizar o modelo compilado entre folds.** Só wall-clock. Risco conhecido: mudar a
   sessão de compilação move números compilados 0,02–0,05 pp entre sessões — a mesma ordem do piso
   de ruído, então **não é adotável em silêncio**. Fazer: atrás de campo de config, default =
   comportamento atual; A/B em AL; adotar só se o autor aceitar a ressalva. Última prioridade
   porque o ganho é dezenas de segundos × folds e o custo de atenção é alto.

### O que ships junto, resumido

| pacote | itens | versão de receita |
|---|---|---|
| telemetria/ops/perf | A5, P9, P4 | **nenhuma** (fora do science_fingerprint / prova bit-idêntica) |
| ciência de substrato | A1 + A2 + A3 (os que sobreviverem à Fase 1) | **v20, única** |
| perf arriscada | P3 | nenhuma; campo de config default-off, adoção é decisão explícita |

---

## 3 · Registro de rota dos itens RESEARCH

Este estudo não os executa; registra para que não se percam e diz onde viveriam:

| item | rota |
|---|---|
| A4 substrato por fold (causalidade do pretexto) | estudo próprio, se um dia; até lá a frase "o substrato é causal" continua proibida (já corrigida nos docs) |
| balanceadores de loss (fonte C, 2 memos fundidos) | estudo futuro "mtl_balancing" — cada método entra em `src/` atrás de config; começar pelo Tier 0 do memo (normalizar CE por log C + litmus RLW), que é o de maior EV |
| arquiteturas MTL fiéis + sweep de cabeças (3 memos fundidos) | estudo futuro "mtl_architecture" — herda o screen cross-stitch×aligned (#7) como hipótese de entrada |
| pairing G0.1 binding + β no-WD (#2, #4) | mesmo estudo de arquitetura; `Pairing.ALIGNED` já existe no mtlcheck, gate nunca fechado |
| upgrades de selector (Parte 1 do joint_selection) | só se um revisor desafiar o `geom_simple`; ~10 linhas quando for |
| errata R14 (capacidade, dissertação/MobiWac) | decisão do autor, fora deste estudo — registrado para não sumir |

## 3.1 · ⚠ DECISÃO COM PRAZO — sob qual objetivo construir CA e TX

**Levantado por uma sessão parceira em 2026-08-20, verificado aqui número por número.** Não é item
de melhoria: é uma decisão que **bloqueia o primeiro build de CA/TX** e não tem volta depois de
gasta a reserva.

### O fato

`p2r_hard_neg_size_gate` tem default `None`, que significa **negativo duro sempre ligado**. A
referência fixa **50 000 lugares** e o **desliga** acima. Contagens verificadas do corpus:

| estado | lugares | sob a referência |
|---|---:|---|
| Alabama | 11 848 | ligado |
| Arizona | 20 666 | ligado |
| Istambul | 29 816 | ligado |
| **Florida** | **76 544** | **DESLIGADO** |
| **Texas** | **160 938** | **DESLIGADO** |
| **California** | **169 145** | **DESLIGADO** |

### Por que nunca apareceu

Em AL/AZ/IST os dois objetivos **coincidem** — todos abaixo do corte. Tudo que rodamos até hoje foi
nesses três estados. O primeiro build de FL/CA/TX é a primeira vez que a diferença existe.

### Por que tem prazo

⚠ **CORRIGIDO 2026-08-21: CA e TX NÃO são reserva intocada** — o batch size foi buscado neles sob o
protocolo antigo. Isso **enfraquece** o argumento de urgência abaixo, que foi escrito supondo
reserva. O que continua valendo é que o objetivo do pretexto não deve ser variável escondida.
Construí-los com o default e
depois comparar com a tabela da dissertação deixa o **objetivo do pretexto** como variável a mais na
comparação. O custo de reconstruir 500 épocas não é o problema — o problema é **gastar a reserva sob
a configuração errada**, e isso não se desfaz.

### As duas saídas — decisão do autor, não nossa

**(a)** construir CA/TX com `p2r_hard_neg_size_gate = 50000`, restaurando a divisão da dissertação e
preservando comparabilidade célula a célula;
**(b)** manter objetivo único em todos os estados e **declarar** a incomparabilidade nos grandes,
como coluna 3 do [`DIVERGENCE_REGISTER`](../../docs/DIVERGENCE_REGISTER.md).

Nenhuma das duas é errada. O que **é** errado é construir sem escolher — que é o estado de hoje,
porque o default decide sozinho.

### Estado

`recipes/v19/substrate.toml` já **declara** a escolha e os seis números, em vez de deixar a omissão
decidir (commit `14d79850` e o anterior da sessão parceira). O `R15` do `REFERENCE_DEFECTS.md` foi
corrigido — dizia "TX maior" sem número, e TX tem **menos** lugares que CA.

---

## 4 · Incertezas declaradas

- O Δ do mae7 em categoria (+0,116, ep 0,087) é **uma réplica**; a Fase 1 existe porque isso não é
  um veredito de grandeza publicável.
- O efeito de A2/A3 é **completamente não medido a jusante**; o plano não tem opinião sobre o sinal.
- O custo de disco de `retain_checkpoints="selected"` na campanha completa não foi estimado aqui;
  estimar antes de ligar board-wide (a decisão dos 125,5 GB foi sobre outra política, então o número
  não transfere).
- A linha R3 do `REFERENCE_DEFECTS.md` está desatualizada em relação a `train/wave.py`; corrigi-la
  é edição de doc, não deste plano — mas está anotada aqui para não se perder.
