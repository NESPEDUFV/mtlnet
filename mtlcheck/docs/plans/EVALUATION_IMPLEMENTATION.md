# Como implementar o protocolo — decisões de arquitetura

> **Documento de desenho, deliberadamente separado de
> [`EVALUATION_PROTOCOL.md`](EVALUATION_PROTOCOL.md).** O protocolo é um documento *científico* que
> precisa ser congelado e datado antes da primeira execução confirmatória — ele mesmo diz que nada
> nele pode ser editado depois disso. A arquitetura do código **vai** mudar enquanto o código existir.
> Misturar os dois obrigaria a editar um documento pré-registrado, que é exatamente o que destrói o
> argumento de defensibilidade.
>
> Regra: o protocolo diz **o que** medir e **por quê**; este diz **onde o código mora**. Uma mudança
> aqui nunca é uma mudança de protocolo.
>
> Estado: **decisões tomadas, nada implementado.** Escrito 2026-08-18 a partir das perguntas do autor.

## 1 · Dois estágios — sim, e o corte é mais forte do que "conveniência"

```
ESTÁGIO 1 · execução                      ESTÁGIO 2 · comparação
(por braço, estado, repetição)            (roda depois, sobre arquivos)
                                          
treina 5 folds                            lê predições de ≥2 braços
seleciona época na inner-val       ──▶    pooling OOF por (braço, repetição)
avalia outer-test UMA vez                 Tier B  (delta pareado por repetição)
grava PREDIÇÕES linha-a-linha             Tier A  (bootstrap por usuário)
                                          TOST / superioridade / NI
   escreve. não julga.                    multiplicidade entre estados e métricas
```

A separação é a que o protocolo já assume: ele abre dizendo que tudo nele é *pós-processamento de
artefatos que o desenho já exige*. Então sim, a leitura do autor está correta.

### A emenda: o Estágio 1 não calcula métrica de outer-test — nem para monitorar

O autor propôs que o pooling OOF de um único braço pudesse acontecer no Estágio 1, "já que não
depende de comparar com outro braço". Tecnicamente cabe: uma célula já roda os 5 folds, então o
pooling está disponível ao fim dela. **Mesmo assim, não deve acontecer lá**, por dois motivos — e o
segundo é científico, não de engenharia.

**Um: duas implementações do mesmo estimando.** O §1 do protocolo fixa detalhes que decidem o número
— a convenção de macro-F1 (há duas não-equivalentes), `zero_division=0`, a regra de suporte zero,
`top10_raw` sobre o vocabulário completo. Calcular isso em dois lugares é dar duas chances de
divergir. Este projeto já registrou esse modo de falha: `metrics.py` documenta que a referência
mantinha duas implementações de métrica e trocava entre elas em C=256, e a resposta aqui foi manter
**uma**.

**Dois, e decisivo: um número de outer-test impresso durante a wave é um número que o operador vê.**
O critério 7 da auditoria diz que qualquer mudança feita após olhar o outer-test converte a execução
em exploratória. Se a wave imprime macro-F1 de outer-test por célula enquanto roda, o selo passa a
depender de disciplina humana em vez de estrutura. **Fazendo o Estágio 1 gravar linhas e nenhum
número de outer-test, o selo vira propriedade do fluxo de dados** — não há o que olhar, então não há
como olhar cedo.

O que o Estágio 1 **pode** reportar sem quebrar nada: métricas de **inner-val** (necessárias para a
seleção de época, e explicitamente não são o estimando), wall-clock, memória, época escolhida,
convergência. Ou seja, o `report.md` atual continua útil — perde só a linha do resultado.

Quando alguém quiser o número de um braço só, chama o Estágio 2 com um braço. É deliberado, datado, e
fica no log.

## 2 · Módulo novo, e `train/stats.py` fica como está

O `stats.py` de hoje opera sobre `Cell(seed, fold, value)` — métrica já agregada. O Tier A exige
predições cruas. **Módulo novo ao lado, não extensão in-place.** Três razões:

1. **São estimandos diferentes com `n` diferentes.** Tier B: n = repetições. Tier A: n = usuários.
   O [`NOMENCLATURE.md`](../NOMENCLATURE.md) acabou de existir porque confundir unidades inferenciais
   custou caro aqui; uma função que aceita linha-a-linha *ou* célula convida a mesma confusão de volta.
2. **O `stats.py` está validado e seus vereditos estão bancados** (os gates de schedule). Mudar o
   contrato de entrada de um módulo cujos resultados já foram reportados é risco sem ganho.
3. Uma função que aceita as duas formas é uma função fazendo duas coisas.

### O acoplamento que PRECISA existir

Uma única definição de métrica, usada por todos. É o que impede o Estágio 1 (se algum dia reportar) e
o Estágio 2 de discordarem, e o que impede Tier A e Tier B de medirem coisas sutilmente diferentes.

```
src/mtlcheck/
├── train/stats.py          INTACTO — Tier B sobre células (gates, uso legado)
└── eval/                   NOVO
    ├── predictions.py      o "persistence contract": schema, escrita, leitura, validação
    ├── estimands.py        métrica a partir de LINHAS — a única implementação
    ├── compare.py          Tier A (bootstrap/permutação), TOST, gatekeeping sequencial
    └── multiplicity.py     Holm / Romano-Wolf / BH / conjunção parcial
```

`compare.py` importa `train/stats.py` para o Tier B em vez de reimplementá-lo. `estimands.py` é
importado pelo Estágio 2 e, se um dia o Estágio 1 quiser um número de inner-val comparável, por ele
também.

## 3 · O persistence contract **não existe** — e é o primeiro item, por um motivo que não é gosto

Verificado: `result.json` grava seleção por fold, série por época, diagnósticos e contagem de
parâmetros. **Não grava uma única predição.** Nenhum arquivo do pacote persiste `userid` ao lado de
uma predição.

Isso deve ser o primeiro item do checklist de pré-registro, e a razão é assimétrica:

> **Todo o resto do protocolo é pós-processamento e pode ser refeito. As predições só podem ser
> capturadas no momento em que o modelo roda.**

Se uma wave confirmatória rodar sem isso, o Tier A inteiro — bootstrap de usuário, permutação, TOST,
os intervalos que sustentam toda alegação-manchete — fica indisponível, e a única saída é re-treinar.
Errar a ordem aqui custa a wave inteira; errar qualquer outra ordem custa um script.

### O que grava (§2 do protocolo), por linha de outer-test

`state · arm · split_seed · partition_hash · model_seed · fold · userid · window_id ·
selected_epoch · y_true · rank_of_true` (+ `top_k` para a região) · e por fold o
`train_label_set` — este último porque `ood_fraction` e o canário `ood_hit_rate` dependem dele, e
ele não é recuperável depois.

Formato: parquet por célula, particionado por `(state, arm, model_seed)`. Ordem de linhas estável e
`partition_hash` conferido na leitura — o hash é a verdade, a seed é só a receita
(§10.5 do protocolo).

## 4 · Onde cada decisão fica registrada

| Documento | Papel | Muda quando |
|---|---|---|
| [`EVALUATION_PROTOCOL.md`](EVALUATION_PROTOCOL.md) | ciência: estimando, desenho, inferência, margens | **congela** antes da primeira execução confirmatória |
| **este documento** | onde o código mora, contratos entre estágios | sempre que o código mudar |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | o mapa de camadas do projeto | ganha um ponteiro para cá |
| [`../NOMENCLATURE.md`](../NOMENCLATURE.md) | vocabulário obrigatório | ao acrescentar um fator experimental |
| [`EVALUATION_METHOD_GUIDE.md`](../EVALUATION_METHOD_GUIDE.md) | didático: por que o método é assim | acompanha o protocolo |

## 5 · Ordem de implementação

1. **`eval/predictions.py`** — o contrato. Schema, escrita, leitura, validação, teste de ida-e-volta.
   Nada mais pode começar antes.
2. **Ligar no runner** — a avaliação de outer-test emite linhas em vez de (além de) um número.
   Um teste que falha se um número de outer-test escapar para o `report.md`.
3. **`eval/estimands.py`** — pooled macro-F1 e `top10_raw` a partir de linhas, com as convenções do
   §1 pinadas em teste (incluindo o viés medido de −0,24 pp entre pooling e média-de-fold, que é o
   teste que prova que a distinção importa).
4. **`eval/compare.py` Tier B primeiro** — delegando ao `stats.py`, para fechar o circuito
   linhas → pooling → delta pareado contra um resultado já conhecido.
5. **Tier A** — bootstrap em cluster de usuário, percentil + BCa, permutação estudentizada.
6. **TOST e gatekeeping**, depois **multiplicidade**.

Os passos 1–2 são pré-requisito de qualquer wave confirmatória. Os passos 3–6 podem ser escritos
enquanto a wave roda, porque operam sobre arquivos.

## 6 · O que ainda não está decidido

- **Onde `eval/` fica na CLI.** `mtlcheck score` hoje faz o papel de Estágio 2 para o Tier B legado.
  Estender `score` ou criar `mtlcheck compare` — a decidir quando o passo 4 chegar, e a diferença é
  só ergonomia.
- **Tamanho em disco.** Uma linha por janela de outer-test por braço por repetição: em Texas são
  ~3,8 M janelas, 20 % de outer-test, × 3 braços × 2 repetições ≈ 4,6 M linhas. Cabe folgado em
  parquet, mas o número deve ser medido antes de rodar os estados grandes, não estimado.

## 7 · Estado da implementação (2026-08-18) e o que ficou de fora de propósito

Os passos 1–6 do §5 estão implementados. O que segue registra as decisões que a revisão adversarial
apontou e como cada uma foi fechada — e, no fim, duas que foram **deliberadamente adiadas**, com o
motivo, para que ninguém as reabra achando que foram esquecidas.

### 7.1 · Duas sementes, dois botões

`--seed` passou a ser **só a semente do modelo** (inicialização, shuffling, dropout). A partição
tem a sua própria: `--split-seed` → `DataConfig.split_seed`. Um inteiro governando as duas torna
variância-de-partição e variância-de-inicialização inseparáveis, que é exatamente a confusão que o
[`NOMENCLATURE.md`](../NOMENCLATURE.md) existe para eliminar.

Consequência operacional: **`--save-predictions` exige `--split-seed` explícito.** Sem ele o sidecar
gravaria duas colunas de semente com o mesmo número, alegando dois fatores experimentais onde só
houve um.

No manifesto de wave, `seeds = [...]` continua significando **repetições** (`split_seed == seed`:
re-particiona *e* re-inicializa). Um `split_seed = N` escalar na célula fixa a partição e converte
aquelas sementes em **réplicas** — afirmação bem mais estreita, e agora impossível de fazer por
acidente.

### 7.2 · O selo é uma propriedade gravada, não uma promessa

`FoldResult.eval_stream` registra de qual fluxo veio a série por época: `inner_val` (selado) ou
`outer_fold` (legado). Ele sobe para o agregado, para o `result.json`, para o `index.jsonl` e para o
sidecar de predições. **`score.compare` recusa parear os dois fluxos**, e `evaluate_folds` recusa
promediar folds de fluxos diferentes.

O motivo é quantitativo: o otimismo medido da regra legada é ~0,66 pp, **acima** da margem de
equivalência de 0,4 pp. Um delta entre fluxos reporta mudança de *protocolo* como efeito de
*modelo*, na direção favorável e com intervalo estreito. É o erro mais perigoso que esta camada
podia cometer, porque produz exatamente o resultado que se esperava ver.

`predictions.assert_comparable` passou de *aviso* a **recusa** (`confirmatory=True` por padrão) pela
mesma razão: um log rola a tela, uma exceção não. Leitura exploratória continua disponível — mas
exige dizer `confirmatory=False`, o que é assumir a responsabilidade em vez de herdá-la.

### 7.3 · Uma pista de seleção para a região, congelada

O runner rastreava `top10_acc_indist` (com gate) enquanto o seletor devolvia o argmax **cru** e
**sem gate** de `top10_acc`. Com predições ligadas, a célula de região abortava sempre que as duas
pistas picassem em épocas diferentes — quase sempre, quando há OOD.

Congelado no **cru**: `top10_acc` é o estimando reportado (§1 do protocolo — não existe contabilidade
de rótulos de treino no momento da inferência), então é a pista em que o checkpoint persistido tem
de ser escolhido. `min_best_epoch` agora governa a pista selecionada nos dois lados. A pista
in-distribution continua sendo reportada, como diagnóstico.

### 7.4 · A célula joint persiste, e persiste UMA época

`train_joint_fold` ganhou o caminho de captura: rastreia o melhor `geom_simple` **na série interna**,
recarrega aquele checkpoint, faz **uma** passada no outer e emite linhas das duas tarefas com o
**mesmo** `selected_epoch`. Persistir cada tarefa no seu próprio melhor descreveria um par de modelos
virtuais sob uma manchete que afirma um só — o que contradiz a propriedade "um modelo, um forward, N
tarefas" que é justamente o argumento do trabalho.

O `if joint` que descartava a captura em silêncio saiu.

### 7.5 · O espaço de rótulos da categoria é fechado

`category_counts` inferia o número de classes dos dados. Uma classe que não aparece **e** não é
predita saía do denominador e a macro-F1 subia 1/C de graça — e dois braços podiam ser comparados
sob dois C diferentes, com o braço que **falhou** em prever a classe rara pontuando mais alto por
isso. Agora o padrão é `NUM_CATEGORIES = 7` e um rótulo fora do espaço é erro.

### 7.6 · O que a segunda revisão mudou

A primeira rodada de correções foi re-revisada adversarialmente e **reprovada** — não pelo código de
treino, que passou, mas por defeitos na camada de leitura e pelo manifesto. Registro do que mudou:

**O manifesto contradizia o protocolo congelado.** `sealed_bridge.toml` rodava *repetições*
(`split_seed == model_seed`), enquanto §10.1 decide congelar a partição em `split_seed = 0` e §10.3
torna **obrigatório** que o gate de calibração re-meça a banda como banda de *réplica*. Pior: quatro
partições produzem quatro `partition_hash`, e o Tier A pooled do §3 fica **irrodável** — o
`assert_comparable` recusa células de mais de uma partição, sem escape. Corrigido: `split_seed = 0`
nas três células.

**O resume da wave não conferia nada.** A docstring prometia comparar o fingerprint desde que o
módulo existe; o código lia `payload["fingerprint"]` (o schema grava `config_fingerprint`) e não
comparava com coisa alguma. Editar uma receita mantinha todas as células que ela tocava. Além disso
`result.json` era escrito **antes** de `predictions.parquet`, então uma queda entre os dois deixava
uma célula que resume para sempre sem linhas — Tier A perde aquele braço em silêncio. Agora: as
predições vão primeiro, o fingerprint é comparado de verdade, e uma célula confirmatória sem linhas
volta para a fila.

**`score --compare` colapsava estados.** `stats.Cell` era chaveada em `(seed, fold)`; dois estados
compartilham essas coordenadas, os dicionários dos braços colapsam e vence o `result.json` que
ordenar por último. Em um estudo de dois estados o delta reportado era o de um deles, sem aviso, com
`n` plausível. `state` virou parte da chave e uma colisão agora é erro.

**A isenção do guard de suporte por classe tinha um buraco.** Usava o **mínimo** entre os dois
braços, então uma classe que um braço nunca toca e o outro apoia em três usuários passava como
"ausente em todo lugar" — distorção medida de 0,37 pp contra margem de 0,4 pp. Agora é o máximo:
isento só quando os dois braços estão vazios.

**`cell_id` não expressava o desenho.** Era `{family}-{state}-s{seed}`, então duas das quatro células
do fatorial 2×2 do §10.4 colidiam no mesmo diretório. §10.5 exige que o `cell_id` carregue os dois —
agora carrega.

Também: pareamento por **id real de fold** (não posição — `--only-folds` comprime a lista), recusa de
parear células cujo `eval_stream` é desconhecido (o default `outer_fold` rotularia uma célula selada
como legada), `band_over` obrigatório para imprimir banda (§10.5), tabela t exata até n=30 (a
fórmula anterior era anti-conservadora em torno de n=11), mid-p para empates no BCa, e jackknife
O(n) em vez de O(n²) — exato, não aproximado, porque as contagens são inteiras.

**A permutação estudentizada foi implementada, não adiada.** O argumento de que estudentizar um
sign-flip é um no-op está correto em primeira ordem, mas §3 a pré-registra, e "está registrado como
decisão" não substitui cumprir o documento. Implementada com pseudo-valores jackknife; o p-valor não
estudentizado viaja ao lado como diagnóstico. Ver §12.2 do protocolo.

**Romano-Wolf continua adiado — agora como emenda registrada** (§12.1 do protocolo), não como nota de
rodapé de implementação. A diferença importa: RW aparece na checklist de pré-registro, então omiti-lo
é emendar o documento, e emenda tem data e justificativa.

**Estágio 2 ganhou CLI.** `mtlcheck compare` é o **único** lugar que calcula um número de
outer-test: lê os sidecars, recusa células não seladas fora de `--exploratory`, roda Tier A + TOST e
imprime a linha de sensibilidade em δ ∈ {0,2, 0,4, 1,0} que o §3 torna obrigatória. Sem ele o
propósito (2) da bridge — medir o otimismo do protocolo legado — aconteceria em um notebook sem
auditoria.

**Tamanho em disco nos estados grandes** (§6) continua a medir, não a estimar.
