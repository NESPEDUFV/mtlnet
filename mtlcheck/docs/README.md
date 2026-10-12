# mtlcheck — por onde começar

Reimplementação clean-room do sistema **v18** de predição de POI multi-tarefa, para uma dissertação
de mestrado. Três famílias treinadas sobre o mesmo substrato de check-ins:

| família | tarefa | classes | métrica |
|---|---|---|---|
| `cat` | próxima categoria | 7 | macro-F1 |
| `reg` | próxima região | 520–8 501 | Acc@10 |
| `joint` | as duas, num modelo | — | as duas |

A alegação-manchete é **"um modelo, um forward, N tarefas"**. Qualquer deploy que quebre essa
propriedade é evidência de apoio, nunca a manchete.

---

## Qual documento eu preciso?

```
                    ┌─────────────────────────────────────────┐
                    │  o que você está tentando fazer?        │
                    └─────────────────────────────────────────┘
                                     │
    ┌──────────────┬─────────────────┼─────────────────┬──────────────────┐
    ▼              ▼                 ▼                 ▼                  ▼
 rodar algo    comparar dois     entender o que    mexer no código    entender por
               modelos           foi gravado                          que é assim
    │              │                 │                 │                  │
    ▼              ▼                 ▼                 ▼                  ▼
 RUNNING_      EVALUATION_       TELEMETRY_        ARCHITECTURE      REFERENCE_
 STUDIES       METHOD_GUIDE      GUIDE             + SYSTEM_MAP      DEFECTS
```

| documento | responde | tamanho |
|---|---|---|
| **[`QUAL_CONJUNTO_USAR.md`](QUAL_CONJUNTO_USAR.md)** | **"uso a validação interna ou o teste?" — as duas perguntas e os dois instrumentos. Leia primeiro** | curto |
| **[`POR_QUE_O_TESTE_ESPERA.md`](POR_QUE_O_TESTE_ESPERA.md)** | **a estatística por trás do conjunto reservado — por que olhar antes estraga o número** | didático |
| **[`BEST_PRACTICES_NESPEDGPU.md`](BEST_PRACTICES_NESPEDGPU.md)** | rodar na A40 — cada item é um erro que já aconteceu aqui, com o custo que teve | prático |
| **[`RUNNING_STUDIES.md`](RUNNING_STUDIES.md)** | **como rodar qualquer coisa sem quebrar a proveniência — leia ANTES de executar** | didático |
| **[`EVALUATION_METHOD_GUIDE.md`](EVALUATION_METHOD_GUIDE.md)** | como um número vira conclusão; **§7 = como rodar um estudo grande sem gastar o teste**; §9 = partição × semente de modelo, e o eixo de partição | didático |
| **[`TELEMETRY_GUIDE.md`](TELEMETRY_GUIDE.md)** | o que cada execução grava e por quê; o contrato de checkpoint | didático |
| [`NOMENCLATURE.md`](NOMENCLATURE.md) | repetição × réplica, e por que `seed` virou dois botões | curto, **obrigatório** |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | as camadas, os módulos, as fronteiras de artefato | referência |
| [`SYSTEM_MAP.md`](SYSTEM_MAP.md) | o que o sistema antigo faz e o que foi deliberadamente deixado fora | referência |
| **[`DIVERGENCE_REGISTER.md`](DIVERGENCE_REGISTER.md)** | correção de migração ⧸ defeito reproduzido ⧸ melhoria real — **leia antes de escrever "melhoramos X pp"** | curto |
| [`REFERENCE_DEFECTS.md`](REFERENCE_DEFECTS.md) | os defeitos achados no sistema antigo (R1–R16) e como este os evita | referência |
| [`OPTIMIZATIONS.md`](OPTIMIZATIONS.md) | o que foi medido e vale otimizar, e o que não vale | referência |
| [`plans/EVALUATION_PROTOCOL.md`](plans/EVALUATION_PROTOCOL.md) | a especificação **congelada** — ciência, não código | formal |
| [`plans/EVALUATION_IMPLEMENTATION.md`](plans/EVALUATION_IMPLEMENTATION.md) | onde o código do protocolo mora | formal |

**Regra dos dois documentos formais:** o `EVALUATION_PROTOCOL.md` é congelado — editá-lo depois da
primeira execução confirmatória destrói o argumento de pré-registro. Emendas entram no **§12** dele,
datadas. Os guias didáticos podem mudar à vontade.

---

## Os seis fatos que evitam a maioria dos enganos

1. **`seed` são dois botões.** `--split-seed` decide a partição; `--seed` decide a inicialização.
   Uma **repetição** re-particiona; uma **réplica** re-treina numa partição fixa. Confundir os dois
   foi o que este projeto pagou caro. → [`NOMENCLATURE.md`](NOMENCLATURE.md)
2. **O teste externo é um instrumento por *ciclo de congelamento*, não por experimento.** Rode
   cinquenta variantes na validação interna de graça; congele uma lista curta; leia o teste **uma
   vez**. → `EVALUATION_METHOD_GUIDE.md` §7
3. **Divida os *estados*, não os experimentos.** AL/AZ/FL são estados de desenvolvimento; **CA e TX
   **já informaram decisões** — o batch size foi buscado neles, e as receitas carregam LR por estado.
   Não são reserva e nunca foram; são a faixa grande insubstituível. Reserva de verdade é o pool
   intocado. → `POR_QUE_O_TESTE_ESPERA.md`
4. **O número no `result.json` de uma célula selada é de validação *interna*.** O número de teste
   externo existe só nas predições, e só sai pelo `mtlcheck compare`.
5. **Execuções compiladas não são bit-reprodutíveis** entre sessões (0,02–0,05 pp). Nenhum delta
   abaixo disso é interpretável.
6. **Números deste protocolo não se comparam com números do v18**, e a leitura de validação
   **interna** não é resultado nenhum. Em Alabama/região convivem três leituras — 70,05 (plano, v18),
   73,72 (interna, otimista, nunca citar) e **69,01 (teste externo — o número científico)**. Só
   subtraia duas células que compartilham `eval_stream`. → `EVALUATION_METHOD_GUIDE.md` §8

---

## Comandos

```bash
# 1 · substrato (camada 1) — do corpus, sem insumo externo
mtlcheck check2hgi build --recipe recipes/v19/substrate.toml --state alabama \
    --shapefile <tract.shp>
#   o grafo Delaunay e o code book POI2Vec são COMPUTADOS aqui e escritos em temp/;
#   passe --poi2vec / --delaunay-places / --delaunay-edges para ler os artefatos do HGI antigo.
#   O manifesto carrega o digest de conteúdo dos três, dos dois jeitos.

#   v19: UM substrato por estado. A torre de região lê o MESMO — o substrato de região separado
#   (v14) foi arquivado em 576f7b85.

mtlcheck check2hgi verify --recipe recipes/v19/substrate.toml --state alabama

# 2 · treinar uma célula (camada 3)
mtlcheck train --recipe recipes/v19/joint.toml --state alabama \
    --seed 0 --split-seed 0 --set inner_validation=true
#   --save-predictions   grava as linhas do teste externo (exige --split-seed)
#   --no-grad-probe      desliga a sonda de geometria de gradiente
#   --only-folds 1,3     roda um subconjunto da partição canônica

# 3 · uma matriz declarativa
mtlcheck wave plan   studies/<estudo>/waves/<x>.toml    # o que rodaria
mtlcheck wave run    studies/<estudo>/waves/<x>.toml    # roda, com resume honesto
mtlcheck wave status studies/<estudo>/waves/<x>.toml

# 4 · ESTÁGIO 1 — re-pontuar o que já rodou (val interna, wall, memória)
mtlcheck score runs/<estudo> --compare cat joint:cat --state alabama

# 5 · ESTÁGIO 2 — o ÚNICO comando que lê o teste externo
mtlcheck compare runs/<estudo> --arm-a cat --arm-b joint --task cat --state alabama
```

---

## Onde ficam as coisas

```
src/mtlcheck/
├── substrate/     camada 1 — corpus → grafo → Check2HGI → embeddings → parquets
├── data/          camada 2 — janelas, tensores, splits, batches
├── models/        as cabeças (gru, stan) e o modelo joint
├── train/         camada 3 — runner, losses, métricas, scoring, telemetria, wave
└── eval/          ESTÁGIO 2 — o contrato de predições, estimandos, Tier A, multiplicidade

studies/<x>/       o registro científico commitado (board, waves, evidência)
runs/<x>/          bulk gitignorado, por célula     (RUNS_ROOT)
artifacts/         substratos                        (ARTIFACTS_ROOT)
```

Um estudo **não contém ciência executável** — sem laço de treino, sem torch, sem driver copiado.
Isso é testado (`tests/test_studies_contract.py`), porque no sistema antigo uma cópia de laço de
validação ficou dois meses atrás das correções do `src/`.

---

## Estado atual

**Feito:** camadas 1–3, `wave`/`score`/`compare`, protocolo de avaliação (Tier A/B, TOST,
multiplicidade), protocolo de telemetria (sonda de gradiente, retenção, FLOPs, escalares de saúde,
bloco top-K), e a primeira leitura selada em AL/AZ/IST
([`studies/porting_validation/SEALED_BRIDGE_READ.md`](../studies/porting_validation/SEALED_BRIDGE_READ.md)).

**Aberto, em ordem:** validar `reg` e `joint` contra a implementação de referência (só `cat` foi
comparada ponta a ponta); portar os pré-requisitos do HGI e o substrato de região v14 — hoje ambos
são insumos externos; o scorer do §8a, que é o consumidor dos checkpoints retidos.

O estado do dia vive em
[`studies/porting_validation/STATE.md`](../studies/porting_validation/STATE.md).
