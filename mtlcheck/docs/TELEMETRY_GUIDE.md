# Guia — o que cada execução grava, e por quê

> **Leia isto primeiro se você vai mexer em telemetria, ou se está tentando responder uma pergunta
> sobre uma execução antiga.** Companheiro do [`EVALUATION_METHOD_GUIDE.md`](EVALUATION_METHOD_GUIDE.md),
> que explica como os números viram conclusões. Este explica que números existem.
>
> Estado: **implementado**. Substitui `plans/TELEMETRY.md` e `plans/MONITORING.md`.

## 1 · A pergunta que este protocolo responde

> **Quanto do trabalho desta pesquisa foi re-treinar modelos para obter um número que a execução
> original tinha em mãos e jogou fora?**

A resposta, auditada na dissertação, é: muito.

| o que faltou | o que custou |
|---|---|
| o cosseno de gradiente não era gravado por padrão | **≥ 4 campanhas de treino**; uma noite remota inteira perdida; uma varredura de 93 rundirs achou o campo preenchido em **4**; a pergunta "e em CA/TX?" segue **sem resposta para sempre** |
| o α aprendido nunca era persistido | 4 estados × 5 folds × 50 épocas re-executados para ler **quatro escalares** |
| as sondas rodaram `--no-checkpoints` | duas células re-treinadas só para recuperar pesos já calculados |
| FLOPs nunca existiu (fvcore ausente, falhava em **zero**) | não existe nenhum número de custo joint-vs-dedicado na dissertação |
| o objetivo efetivo de perda não era gravado | um tier inteiro re-executado; as ordenações inverteram |

E o contra-exemplo que define o desenho: **ninguém jamais havia pontuado o checkpoint joint** — o
autor acreditava que os números do paper o descreviam. Corrigir custou **minutos de CPU, zero GPU**,
porque as séries de validação por época estavam gravadas.

Mesma classe de pergunta. A diferença foi inteiramente o que havia em disco.

## 2 · A regra que organiza tudo

> **Grave o que, sem isso, exigiria re-executar. E nada que não tenha um consumidor nomeado.**

As duas metades importam. A primeira evita as campanhas da tabela acima. A segunda existe porque
todo campo é minerável: um campo sem pergunta registrada é superfície para achar história depois.

**Exceção deliberada: pesos.** Checkpoints são *infraestrutura*, não campo de telemetria — o valor
deles é justamente serem genéricos, servindo scripts que ainda não foram escritos. A regra do
consumidor nomeado aplica-se a *o que se grava sobre uma execução*, não a *guardar o modelo*.

## 3 · A taxonomia que decide o custo

O que separa "precisa re-treinar" de "precisa de uma tarde" **não é o log — é a retenção de peso**:

| classe | o que precisa | exemplos |
|---|---|---|
| **A** — irrecuperável | uma re-execução bit-idêntica | cosseno de gradiente, ‖Δθ‖, contagens de forgetting |
| **B** — recuperável | **um checkpoint naquela época** | CKA, calibração, FLOPs, re-pontuação, a curva de acumulação |
| **C** — recuperável | só os logits salvos | ECE@k, temperature scaling, Acc@k a qualquer k |

**Quase tudo é classe B.** Por isso a política de retenção é a decisão de maior alavancagem — e por
isso ela é *opt-in*, não default (§6).

## 4 · O que uma execução deixa em disco

```
runs/<estudo>/<cell-id>/
├── result.json              config resolvida · ambiente · agregado · séries por época por fold
├── report.md                o relatório legível: modelo, dados, receita, por fold, anomalias
├── arch.txt                 a árvore de módulos + parâmetros por caminho
├── folds/fold{k}.csv        a série por época, uma linha por época
├── predictions.parquet      ⟵ só com --save-predictions: uma linha por janela do teste externo
├── predictions_meta.json    o sidecar sem o qual as linhas não são interpretáveis
└── checkpoints/             ⟵ só com retain_checkpoints != none
    ├── fold{k}_selected.pt
    └── manifest.json
```

`<cell-id>` é `{família}-{estado}-p{split_seed}s{model_seed}` — **a partição e a semente de
modelo**, porque são dois fatores experimentais (ver [`NOMENCLATURE.md`](NOMENCLATURE.md); o
segmento continua grafado `split_seed` de propósito — protocolo §12.6e).

## 5 · Os campos, e o incidente que cada um previne

### 5.1 · Sempre (custo ~zero)

| campo | previne |
|---|---|
| **config resolvida** + `fingerprint` | um sidecar dizendo `fp32` enquanto a execução era fp16 |
| `environment` + **`code_fingerprint`** | dois braços rodados dos dois lados de uma mudança de código, sem nada no artefato dizendo isso (`git_commit` vem `null` no A40, que tem uma cópia rsync, não um checkout) |
| `parameter_counts` por caminho + `arch.txt` | uma auditoria de capacidade que contou um modelo montado fora do caminho de execução e publicou 644 359 onde a execução usou 1 433 863 |
| **as duas convenções de época** (`cat_diag_best`, `reg_diag_best`, `joint_best`) | a raia joint-best ficar vazia sem ninguém notar |
| séries por época por fold | é o que permitiu re-pontuar o checkpoint joint sem GPU |
| `eval_stream` (`inner_val` / `outer_fold`) | parear um número selado com um legado, cuja diferença é ~0,66 pp de otimismo de seleção |

### 5.2 · Com `diagnostics` (default **ligado**)

| campo | responde |
|---|---|
| tempo por fase (train/val), sincronizado na GPU | "vale otimizar o quê?" — sem sincronizar, uma fase mede o tempo de *enfileirar*, não de executar |
| forma da convergência (melhor época, épocas até 95 %/99 %, estabilidade da cauda) | "duas execuções chegaram no mesmo lugar do mesmo jeito?" |
| pico de memória, **resetado por fold** | um pico herdado da célula anterior fez três células reportarem 3,418 GB; o real era 0,505 |
| **norma de gradiente** (média/máx/fração clipada) e **contador de não-finitos**, por época | o colapso fp16 em CA época 30 foi diagnosticado exatamente disto — em execuções novas, instrumentadas depois do fato |
| LR realizado por grupo | três células queimadas descobrindo que LR por cabeça era inerte sob OneCycle |
| contadores do dynamo (delta por fold) | um braço "compilado" que rodou eager em silêncio |
| perdas por tarefa (joint) | a pergunta de balanço de perda, sem braços extras |

### 5.3 · A sonda de geometria de gradiente (joint, default **ligada**)

O cosseno entre os gradientes das duas tarefas **sobre o tronco compartilhado**, mais as normas, mais
a decomposição por bloco (`cross_ab`, `cross_ba`, `ffn_a`, `ffn_b`, `norms`, `final_ln`).

É a afirmação de mecanismo central da dissertação: se o cosseno é ~0, a cirurgia de gradiente não tem
o que projetar, e é por isso que PCGrad/NashMTL/CAGrad/GradNorm/Aligned-MTL deram nulo.

**Como funciona, e por que não do jeito óbvio.** A sonda roda **eager, num grafo próprio, sobre o
módulo não-compilado** (`model._orig_mod`), dentro de `fork_rng`:

```
      treino compilado ────────────────────────────────►
            │
            └─ 1 batch/época ─► forward eager próprio ─► ∂L_cat/∂tronco
                                        │                ∂L_reg/∂tronco   ─► cos, normas
                                        └─ fork_rng: o treino não vê nada disto
```

- **Um forward, não dois.** Os dois gradientes precisam compartilhar as mesmas máscaras de dropout.
  Medir cada tarefa no seu próprio forward daria máscaras independentes, o ruído não cancelaria, e o
  cosseno seria **atenuado em direção a zero** — uma sonda enviesada exatamente a favor da conclusão
  que ela sustenta.
- **`fork_rng`** para que o forward extra não consuma o stream de dropout do treino. Sem isso,
  ligar a sonda muda a trajetória que ela mede (medido: em MPS, selecionava outro checkpoint).
- **Grafo próprio** para que o treino continue compilado. Medido em `runs/probe_cost` (quatro
  braços: compilado/eager × com/sem sonda, manifesto em
  `studies/porting_validation/waves/probe_cost.toml`): `compile` vale 24,4 %, e a sonda
  no grafo do treino custava 35,2 % justamente por abrir mão dele. Como sidecar: **14 % em Alabama
  (pior caso, 9 batches/época), 6,9 % em Arizona, 5,0 % em Istambul.** Os dois últimos vêm de
  `runs/probe_cost_scaling` (`waves/probe_cost_scaling.toml`).

**Por que ligada por padrão:** a alternativa a medir durante a execução é medir numa **segunda**
execução — **+100 % contra +14 %**. `--no-grad-probe` desliga quando você sabe que não quer.

**Não existe para execuções dedicadas.** Uma célula `cat` ou `reg` não tem tronco compartilhado nem
segunda perda. Substitutos (cosseno entre minibatches sucessivos) medem ruído de otimização, que é
outra grandeza e não pode morar sob o mesmo nome.

### 5.4 · Com `--save-predictions` (o contrato de persistência)

Uma linha por janela do **teste externo**, avaliada **uma vez** pelo checkpoint selecionado:

`state · arm · task · split_seed · partition_hash · model_seed · fold · userid · window_id ·
selected_epoch · y_true · y_pred · rank_of_true` + o bloco opcional
`top_ids · top_log_probs · true_prob · logsumexp`.

**É o único artefato que não pode ser reconstruído depois.** Todo o resto do protocolo de avaliação
é pós-processamento; as linhas existem só enquanto o modelo roda. Uma wave confirmatória que as
esquece perde o Tier A inteiro, e o remédio é re-treinar.

Três detalhes que parecem menores e não são:

- **`train_labels` viaja no sidecar** — a fração OOD e o canário de vazamento dependem dele, e ele
  não é recuperável depois.
- **`partition_hash`** é o digest da atribuição usuário→fold realizada. O hash é a verdade; a semente
  é só a receita.
- **`logsumexp` em fp32** é o que torna o bloco top-K *sem perda*: `p_j = exp(logit_j − logsumexp)`.
  Sem ele, quem lê renormaliza sobre as K entradas guardadas e reporta probabilidades que o modelo
  nunca produziu. E as probabilidades são guardadas em **log**, não em probabilidade: fp16 zera
  qualquer valor abaixo de 2,98e-8, então a cauda seria destruída, não aproximada.

### 5.5 · FLOPs e custo

`torch.utils.flop_counter`, medido **numa cópia CPU** do modelo, no fold 0, **onde o modelo é
construído** — nunca sobre um modelo reconstruído (foi assim que a auditoria de capacidade publicou
o número errado).

Na CPU porque `nn.GRU` despacha para kernels fundidos do cuDNN que o contador não vê: medido na A40,
a cabeça de categoria reportou **3 584** FLOPs/amostra — exatamente o Linear final, para um GRU de
1,43 M parâmetros. Na CPU reporta 25,7 M. Como bônus, o número deixa de depender da máquina.

**O custo do joint em Alabama, o número que este projeto nunca teve:**

| braço | parâmetros | FLOPs/amostra |
|---|---:|---:|
| cat | 1 433 863 | 25 660 928 |
| reg | 417 117 | 5 232 896 |
| joint | 4 197 621 | 72 923 904 |
| **dois dedicados somados** | **1 850 980** | **30 893 824** |
| **joint ÷ dedicados** | **2,27×** | **2,36×** |

Os dois eixos concordam, o que é a verificação interna. **O joint custa ~2,3× dois modelos
dedicados.** Não favorece a tese; grava-se assim mesmo — é o número que uma banca pede, e "medimos"
é posição muito melhor que "não medimos".

## 6 · Retenção de peso — a decisão de custo

```
retain_checkpoints:  none  (DEFAULT)  │  selected  │  every
                     triagem          │  confirm.  │  §8a, transitório
                     0                │  4,9 GB    │  ~42 GB de pico
```

**`none` por default** porque uma célula de triagem **não pode** consumir um checkpoint: o protocolo
re-treina os vencedores sob confirmação selada, e sob selagem uma célula de triagem nunca avalia o
fold externo. Reter ali é saída write-only — a centenas de células por semana, dezenas de GB que
nada lê.

**`selected`** nas receitas confirmatórias: um arquivo por fold, o modelo sobre o qual qualquer
alegação de deploy fala. 13,7 MB cada, ~4,9 GB no pacote inteiro. É a base de evidência — é o que
permite a re-pontuação independente que um campeão anterior não pôde ter por falta de um `.pt`.

**`every`** é para o §8a e é **transitório**. O protocolo o precifica como "transient checkpoint
storage" e escopa o scorer **por estado**:

```
treina o estado → scorer em quarentena → grava a1/b1/b2 → APAGA → próximo estado
```

Pico ~42 GB por alguns dias; saída permanente, alguns KB de escalares. **Reter sem apagar não é o
§8a ser caro — é metade do §8a**, e a metade que custa 125 GB.

⚠ **Antes de apagar**, o scorer roda um teste que sai de graça: o `b1` na época selecionada tem de
bater **exatamente** com a avaliação externa única já bancada no `result.json`. Isso certifica o
scorer inteiro contra um número que já existe.

### O contrato do checkpoint, para scripts futuros

Um script que vai carregar um checkpoint precisa saber, sem ler o runner:

- **Chaves sem prefixo.** `checkpoints.snapshot()` remove o `_orig_mod.` que o `torch.compile`
  adiciona; um `state_dict()` cru de modelo compilado **não carrega** num modelo novo. (Foi um
  defeito real: todo checkpoint da A40 era inutilizável, e só se descobriria ao abrir o primeiro.)
- **CPU, desanexado, clonado.** O passo de treino muta os tensores in-place; uma referência seria um
  checkpoint do que o modelo tiver ao final.
- **"selected" é verificado.** A época gravada é conferida contra o seletor, e a execução **falha**
  se discordarem — um arquivo rotulado "selected" que não é o selecionado é pior que nenhum, porque
  carrega.
- **O índice é `checkpoints/manifest.json`**, com `fold`, `selected_epoch`, `selected_value` e o
  `config_fingerprint`. Ele **funde** entre processos, então um fan-out de folds não apaga o índice
  do vizinho. Nunca use `glob` — use o manifesto.
- **O que NÃO é retido:** estado do otimizador, do scheduler, do RNG. Um checkpoint serve para
  *avaliar*, não para *retomar* o treino.

## 7 · O que deliberadamente NÃO se grava

O laço de época **nunca vê o fold externo** — telemetria dentro do laço é estruturalmente incapaz de
ler o teste. O fold externo é tocado **exatamente duas vezes, jamais três**: a avaliação única do
checkpoint selecionado, e a passagem sombra em quarentena do §8a.

1. **Nenhuma série de teste externo por época**, nem "só para monitorar". Era o desenho legado, e é o
   defeito que o protocolo existe para remover. O `report.md` retém o número externo enquanto uma
   wave roda: *um número que o operador vê é um número sobre o qual ele pode agir.*
2. **Nenhum logit completo.** Disco é a razão menor (~34 GB/célula em Texas); a real é que logits
   externos gravados são convite permanente a re-pontuar o conjunto selado sob qualquer métrica que
   alguém pense depois — seleção-no-teste por outro nome. Top-K + logsumexp é o teto deliberado.
3. **Nenhum checkpoint por época fora da quarentena §8a.**
4. **Nenhum escalar-manchete duplicado entre artefatos.** Primitivos gravados, derivados recalculados
   na leitura — duas cópias em precisões diferentes é fonte de divergência, não de conveniência.
5. **Nenhum gráfico por padrão, nenhum adaptador W&B/MLflow, nenhum CSV formatado além do CSV.**

## 8 · Comparando wall-clock entre execuções

**Uma célula joint é ~14 % mais lenta desde 2026-08-18, de propósito** — é a sonda, ligada por
decisão. Não é regressão.

| | s/fold (joint, AL, 5 folds) |
|---|---:|
| compilado, sem sonda | 79,13 |
| **compilado, sidecar (o default)** | **90,19** |

Compare wall só entre execuções com o mesmo `execution.probe`, e confira o
`environment.code_fingerprint`. Para reproduzir a baseline antiga: `--no-grad-probe`.

E dois fatos medidos que qualquer comparação deve respeitar: **execuções compiladas não são
bit-reprodutíveis entre sessões** (0,02–0,05 pp), e **`--diagnostics` roda compilado** desde que a
sonda virou sidecar.

## 9 · O que ainda não existe

- **O scorer do §8a.** Nada em `src/mtlcheck/` carrega um checkpoint hoje. A retenção foi construída
  antes do consumidor — **não retenha em escala antes de o scorer rodar num estado**.
- **`progress.py`** — a linha por época na tela.
- **Camada 2 da telemetria** (curva de acumulação ruído-vs-ortogonalidade, manifesto de composição de
  fold, CKA, escala de ruído de gradiente): adiada até haver pergunta pré-registrada, que é a regra
  do §2.


---

## O contrato de checkpoint — o que um script futuro pode assumir

Escrito para quem for consumir os pesos retidos (o `eval/optimism.py` é o primeiro consumidor; não
será o último).

### O que fica em disco

```
runs/<estudo>/<cell_id>/checkpoints/
├── manifest.json                 # uma entrada por fold, com o id do fold DENTRO da entrada
├── fold{k}_selected.pt           # o checkpoint que o seletor escolheu — política != "none"
└── fold{k}_epoch{e}.pt           # a trajetória inteira — só na política "every"
```

### As oito garantias

1. **O `state_dict` carrega direto.** `ckpt.snapshot()` remove o prefixo `_orig_mod.` que o
   `torch.compile` injeta. Sem isso os arquivos existiam e **não carregavam** — foi um bug real.
2. **A escrita é atômica**, com nome de staging por pid + uuid. Um processo morto não deixa arquivo
   meio escrito que carrega e mente.
3. **Escreve conforme avança.** Uma célula que morre no fold 4 mantém os folds 0–3, e o pico de
   memória é um snapshot, não a trajetória.
4. **O id do fold viaja DENTRO da entrada do manifesto.** Num fan-out os processos escrevem no mesmo
   diretório, e um manifesto indexado por posição seria uma lista de linhas anônimas cujos arquivos
   se chamam por um fold que o índice não menciona.
5. **`selected_epoch` é 1-based**, como toda época no `result.json`. A época 0 é a inicialização e só
   aparece na política `every`.
6. **As épocas retidas em `every` são contíguas de 0 a `epochs`.** Se uma faltar, o
   `optimism.estimators_from_curve` **recusa** em vez de aproximar pela vizinha — a1 e b1 têm de sair
   da mesma trajetória, senão o cancelamento de variância que justifica o §8a não acontece.
7. **A política é config, não ambiente:** `retain_checkpoints ∈ {none, selected, every}`, com
   `keep_top_k` para a variante log-espaçada. Entra na receita, não numa variável exportada.
8. **O default é `none`.** Reter a trajetória inteira de uma wave-ponte dá 125,5 GB. Ligue
   deliberadamente, no estado onde a análise vai acontecer.

### O que um consumidor NÃO pode assumir

* **Que os checkpoints existam.** O default é `none`; cheque o manifesto e falhe alto.
* **Que a política foi a mesma em todas as células.** Ela é por execução; um estudo pode misturar.
* **Que o `state_dict` case com o modelo atual.** Os pesos não carregam a arquitetura. Reconstrua o
  modelo pela receita da célula (`result.json` → `config`), nunca por um default de código.
* **Que reter seja de graça em wall-clock.** A escrita é síncrona no fim da época.
