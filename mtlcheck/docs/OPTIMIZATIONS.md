# Plano de otimizações — herdado e estendido, com status verificado

> Herda `docs/studies/train_perf_multifold/` e a investigação `INVESTIGATION_gpu_cpu_alternation.md`
> (2026-08-10) do repositório de referência, mais os pontos que encontrei durante a portabilidade.
>
> **O status de cada item foi verificado no código, não consultado de memória.** Duas revisões
> adversariais já me pegaram afirmando "implementado" para coisa que era plano; esta tabela existe
> para que a pergunta "você está aplicando as melhorias?" tenha uma resposta auditável.

## Status

| # | Ponto | Status |
|---|---|---|
| P1 | A família de região rodava por um script de ablação com laço próprio | ✅ **feito** — um runner, três famílias |
| P2 | Prior inerte alocava `[C,C]` e executava gather + multiplicação por zero | ✅ **feito** — ramo ausente (R6) |
| P3 | `torch.compile` refeito a cada fold | ❌ **não feito** — `runner.py:101` e `:352` recompilam por fold, igual à referência |
| P4 | Sequências em loop Python, reconstruídas por célula | ⚠ **parcial** — construção vetorizada ✅; cache em disco **só para a torre de região**, o tensor de check-in é relido do parquet a cada célula |
| P5 | Build de input pica ~66 GB de RAM e força FL/CA/TX a rodarem 1-wide | ✅ **feito** — leitura em blocos por posição direto para um array pré-alocado; pico 1,00 → 0,32 GB em AL, saída bit-idêntica |
| P6 | `MTL_CHUNK_VAL_METRIC` forçado em todos os estados | ✅ **feito** — sem env vars; streaming sempre, decidido por cardinalidade |
| P7 | `compute_class_weights` sempre computado, mesmo descartado | ✅ **feito** — só quando a loss usa |
| P8 | Passada extra sobre o val loader para diagnósticos | ✅ **feito** — sem passada extra |
| P9 | `results/` em `/home` no A40 (90 % cheio) | ✅ **mecanismo pronto** — `RUNS_ROOT`/`ARTIFACTS_ROOT`; falta apontar para `/dados` na execução |
| R13 | Guard de RAM exige 16 GB de folga fixa para um dataset de 0,4 GB | ✅ **feito** — `memory.check`, margem `necessidade × 1,6 + 1 GB`; avisa por padrão, recusa sob `strict` |

## P5 e R13 — fechados em 2026-08-13

**P5 — memória.** O caminho antigo materializava o parquet inteiro como `DataFrame` (576 colunas
float64 do pandas), selecionava as colunas de embedding, convertia para float32 e só então dava
`reshape` — três representações do mesmo dado vivas ao mesmo tempo. O novo lê **uma posição da janela
por vez** (64 colunas) direto para dentro de um array já alocado com a forma final, e devolve o bloco
antes de ler o próximo. O `DataFrame` some do caminho: `dataset.load` manda o *path* para
`checkin_tensor` e só leva para o pandas as colunas de rótulo.

Medido em Alabama (96 326 janelas, tensor de 0,21 GB):

| caminho | pico acima da base |
|---|---|
| antigo (frame inteiro + cópia) | **+1,00 GB** — 4,8× o tensor |
| novo (streaming por posição) | **+0,32 GB** — 1,5× o tensor |

Extrapolando o fator medido para as duas torres dos estados grandes:

| estado | tensor | antes (2 torres) | agora (2 torres) |
|---|---:|---:|---:|
| Alabama | 0,2 GB | 2,0 GB | 0,6 GB |
| California | 6,3 GB | 60,3 GB | 18,8 GB |
| Texas | 8,2 GB | 78,9 GB | 24,7 GB |

É o que dava o pico de ~66 GB e forçava FL/CA/TX a rodarem 1-wide. Com ~25 GB de pico, TX cabe em uma
máquina de 64 GB com folga para mais de um processo.

Uma otimização de memória que muda um valor é pior do que a memória que ela poupou, então a saída foi
verificada nas duas direções — contra o caminho antigo e contra a leitura crua das colunas:
`np.array_equal` verdadeiro, `max|delta| = 0,0`. Pinado em
`tests/equivalence/test_assembly.py::test_streamed_and_frame_paths_agree`.

**R13 — guard de RAM.** Eu tinha criticado o guard da referência (16 GB fixos para 0,4 GB de dado) e
respondido removendo o guard inteiro, o que troca "recusa quando não devia" por "não avisa quando
devia". Agora existe `memory.check`: a margem é `necessidade × 1,6 + 1 GB`, calculada a partir da
forma real do tensor. Numa máquina com 4 GB livres, Alabama passa e Texas avisa — a referência recusa
os dois. Avisa por padrão e só recusa sob `strict`, porque um aviso errado custa uma linha de log e
uma recusa errada custa a execução. Disponibilidade não mensurável prossegue: recusar por não
conseguir medir é o mesmo defeito com outra roupa.

## P11 — os cronômetros de fase mediam lançamento, não trabalho (2026-08-16)

`diagnostics.Phase` usava `perf_counter` sem `torch.cuda.synchronize`. Lançamentos de CUDA são
assíncronos, então o cronômetro media o tempo de **enfileirar** o trabalho; o trabalho aterrissava na
próxima sincronização, geralmente dentro da fase seguinte. Fases não só com valores errados: com os
valores umas das outras.

**Magnitude real, medida — e menor do que o review afirmou.** O achado dizia "~20× errado". Não
reproduz: o `joint` bancado (pré-correção) já contabilizava **95,5 %** do wall do fold, com
`val_share` 6,5 %. A razão é que o laço tem `.item()` dentro da região cronometrada (loss, métricas),
que sincroniza por acidente. Depois da correção, a célula de categoria contabiliza **99,8 %**
(42,95 s de treino + 4,55 s de validação contra 47,6 s de wall).

Então: o defeito é real e a correção fica — depender de um `.item()` acidental para que um cronômetro
esteja certo é frágil, e some no dia em que alguém remover o log. Mas a atribuição bancada estava
aproximadamente certa, não 20× errada, e o ledger registra isso.

Custo: uma barreira por fase por época. Diagnósticos são opt-in, então uma execução com
`--diagnostics` agora é um pouco mais lenta — e o wall dela não deve ser comparado ao de uma execução
sem.

## P10 — o negativo duro era o gargalo do build inteiro (2026-08-13)

Descoberto ao corrigir o S17, e maior do que eu tinha estimado. O sorteio de negativo duro da
fronteira POI↔região é um laço Python com um sync de device por sorteio; em Alabama são 2 962
sorteios por época a ~70 µs, ou seja **~0,2 s dos 0,23 s de cada época**. Não era um custo marginal
dos estados grandes: era ~87 % do build, em todos os estados que o executavam.

Vetorizado sobre um índice CSR da banda de similaridade:

| | laço | vetorizado |
|---|---:|---:|
| sorteio, Alabama | ~0,2 s/época | 0,10 ms/época |
| sorteio, Califórnia | 3,1 s/época | 0,11 ms/época |
| **build completo de Alabama, 500 épocas** | **~115 s** | **16 s** |

**7× no build inteiro**, medido ponta a ponta. E como o custo saiu, o gate de tamanho que existia
para evitá-lo saiu junto (S17) — a correção de performance e a correção científica são a mesma.

## A lacuna que resta

**P3 — compile por fold.** A referência recompila o modelo a cada fold, e eu reproduzi isso. São
dezenas de segundos × 5 folds × 6 estados × 4 seeds. A correção (reutilizar o modelo compilado entre
folds, reinicializando pesos em vez de reconstruir) é **arriscada para a fidelidade**: mudar quando o
inductor compila muda a sessão de compilação, e a própria referência registra que números compilados
não são bit-reproduzíveis entre sessões. Por isso não entrou junto com o resto — mas a razão precisa
estar escrita, e até agora não estava.

Ela não afeta **correção**, só wall-clock, e é a única das três que segue aberta.

## Já medido na referência — carrego a conclusão, não re-derivo

- **Fan-out de 5 folds não acelera numa GPU** (AL: 654 s → 695 s). O ganho é multi-GPU,
  resumabilidade e granularidade por fold.
- ~~**O laço é launch-bound**: utilização de GPU 10–57 %, o lever é CUDA Graphs.~~ **Medido aqui em
  2026-08-16 e é FALSO para o `mtlcheck`.** Amostrando `nvidia-smi` durante uma célula de categoria em
  Alabama no A40: **98–100 % de utilização**, oito amostras seguidas. Herdei essa conclusão da
  referência sem medir no código novo, que é exatamente o erro que este documento existe para evitar.
  (Ressalva de método: a métrica do `nvidia-smi` é "fração do tempo com pelo menos um kernel ativo",
  não ocupação real — ela descarta o cenário *launch-bound com GPU ociosa*, que era a afirmação, mas
  não prova que os kernels são eficientes.) **Consequência:** perseguir CUDA Graphs aqui persegue ~0 %.
  O que sobra é reduzir trabalho, não overhead de lançamento.
- **Scoring de validação na CPU** era ~39 % da wall da célula de região; corrigido a montante.

## Medição própria, e o que ela realmente diz

Alabama, categoria dedicada, 5 folds, MPS: **827 s** contra **~1 121 s** da referência.

A maior parte dos ~295 s **não é velocidade de treino** — é instrumentação que a referência faz e o
`mtlcheck` não: métrica de treino acumulada por época, cópia do melhor estado a cada melhora, duas
passadas extras de validação por fold, e 62 artefatos de diagnóstico. Em regime, 3,3 s/época contra
4,4 s/época. E o cronômetro do `mtlcheck` começa **depois** do carregamento de dados, então nem a
comparação de wall é simétrica. A frase defensável é "o runner enxuto contra o harness
instrumentado", não "26 % mais rápido".
