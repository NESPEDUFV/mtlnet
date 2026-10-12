# Baseline de 1 fold — o que o módulo de monitoramento não pode piorar

> Banco de referência de 2026-08-17, medido no A40. **Existe por um motivo específico:** no código
> antigo o módulo de métricas foi a maior fonte de lentidão do treino. Então a ordem aqui é
> deliberada — medir, construir o monitoramento, medir de novo — e este arquivo é o meio-termo.
>
> Evidência bruta: [`evidence/baseline_1fold.json`](evidence/baseline_1fold.json) e
> [`evidence/baseline_1fold_diagnostics.json`](evidence/baseline_1fold_diagnostics.json).

## A configuração, sem ambiguidade

`{alabama, arizona, istanbul} × {cat, reg, joint} × seed 0`, **1 fold**, 50 épocas,
`--diagnostics`, **todas as nove células em eager** — e desta vez isso está gravado no artefato
(`diagnostics.execution.compiled = false`), não afirmado por mim.

## Os números

| célula | wall | pico GB | métrica | melhor época |
|---|---:|---:|---:|---:|
| cat/alabama | 23,0 s | 3,04 | 31,9452 | 13 |
| cat/arizona | 47,4 s | 3,26 | 34,4437 | 46 |
| cat/istanbul | 64,2 s | 3,42 | 36,4712 | 38 |
| reg/alabama | 16,1 s | **0,52** | 72,1879 | 45 |
| reg/arizona | 33,8 s | **0,76** | 62,6944 | 50 |
| reg/istanbul | 44,0 s | **0,90** | 76,5925 | 47 |
| joint/alabama | 121,9 s | 11,78 | cat 31,75 / reg 71,66 | — |
| joint/arizona | 247,8 s | 12,26 | cat 34,25 / reg 62,42 | — |
| joint/istanbul | 331,2 s | 12,50 | cat 36,45 / reg 76,45 | — |

Total: **27,2 min** (25,4 de treino, 1,7 de validação). Validação é ~6 % da wall.

## Por que este banco difere do primeiro, e por que o primeiro estava errado

Duas correções entraram entre as duas execuções, ambas em como o profiling media a si mesmo:

**Memória.** `peak_memory` lia `max_memory_allocated()` sem ninguém zerar o contador — que é um
máximo do **processo inteiro**, e uma wave roda as nove células num processo só. Cada célula herdava
o maior pico até então. O sinal estava na saída que eu imprimi e não li: as três células de região
reportando **exatamente 3,418 GB**, que era o pico da célula de categoria anterior. Agora zerado por
fold, antes de os tensores irem para o device: região cai para 0,52 / 0,76 / 0,90 GB e **escala com o
tamanho do estado**, como sempre deveria. O número antigo era **6,8× maior** — e é exatamente o
número que alguém usaria para dimensionar FL/CA/TX.

**Modo de execução.** `train_fold` compilava incondicionalmente; só o caminho joint checava
`diagnostics`. A wave anterior rodou seis células **compiladas** e três em eager, e eu descrevi tudo
como eager. Nada no artefato podia me contradizer. O gate agora é espelhado e o modo é gravado.

Consequência a declarar: as células de região ficaram **mais lentas** neste banco (13→16 s, 27→34 s,
35→44 s) porque antes rodavam compiladas. Não é regressão — é o preço de as nove serem comparáveis
entre si, que é a única coisa que torna este baseline utilizável.

Os valores de região também mudaram (72,06→72,19; 62,60→62,69; 76,45→76,59), pelo mesmo motivo:
compilado e eager diferem dentro do desvio entre folds. Comparar contra este banco exige eager.

## ⚠ Este banco ficou OBSOLETO para comparação de wall (2026-08-17)

Foi medido **em eager**, porque na época `--diagnostics` forçava eager. No mesmo dia a sonda de
geometria de gradiente foi separada das métricas baratas, então `--diagnostics` passa a rodar
**compilado** — e a mesma wave re-executada depois do monitoramento roda em outro modo:

| célula | baseline (eager) | depois (compilado) | Δ wall |
|---|---:|---:|---:|
| cat/alabama | 23,0 s | 23,6 s | +2,3 % |
| joint/alabama | 121,9 s | 95,8 s | **−21,5 %** |
| reg/istanbul | 44,0 s | 34,5 s | **−21,6 %** |

**Os −21 % não são o monitoramento; são eager → compilado.** E os desvios de qualidade (até 0,21 pp
em joint/istanbul) são a mesma troca de modo, não regressão — compilado e eager diferem além do ruído
compilado-contra-compilado de 0,02–0,05 pp.

Ou seja: esta comparação **não responde** à pergunta para a qual o banco foi criado. A pergunta certa
foi respondida direto: **a escrita do relatório leva 0,2 ms contra 23,6 s de célula — 0,001 %.** E por
construção ela roda uma vez, depois dos folds, fora do laço; nada do módulo de monitoramento executa
por época. O modo de falha do código antigo (métricas sincronizando por batch) é estruturalmente
impossível aqui.

Um novo baseline em modo compilado é `runs/profile_1fold_after`, e é contra ele que a próxima
comparação deve rodar.

## Como usar isto depois do monitoramento

Rodar exatamente a mesma wave e comparar **as duas coisas**:

1. **Qualidade** — as métricas por célula devem bater. Em eager e com determinismo, devem bater
   exatamente; qualquer diferença é o monitoramento mudando o cálculo, não ruído.
2. **Performance** — wall por célula e `val_share_of_wall` (~6 % hoje). O modo de falha a vigiar é
   o do código antigo: métricas que sincronizam por batch e transformam validação em metade da wall.
