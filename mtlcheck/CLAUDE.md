# mtlcheck

Reescrita limpa do sistema experimental **v18**: predição multi-tarefa de POI — próxima categoria e
próxima região — sobre um substrato Check2HGI em nível de check-in.

## Leia nesta ordem

1. [`docs/SYSTEM_MAP.md`](docs/SYSTEM_MAP.md) — o que o v18 é, extraído do código que rodou. As
   invariantes científicas estão numeradas **S1-S16**; o ledger de divergências entre metodologia
   documentada e implementação real é **D1-D8**.
2. [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — como este projeto o reconstrói, a estratégia de
   equivalência (**E1-E11**, **C1-C8**) e o sistema de `studies/`.
3. [`docs/REVIEW_LEDGER.md`](docs/REVIEW_LEDGER.md) — a revisão adversarial da fase 1 e a disposição
   de cada achado.

O repositório de referência (o código antigo, que ainda é a fonte de verdade sobre o que rodou) está
dois níveis acima, na raiz deste worktree.

## O trabalho vivo, em 2026-08-20

A migração **fechou**: o porte reproduz a dissertação (Δ médio −0,001 pp em oito células), é
standalone do corpus bruto a modelos treinados, e passou por uma auditoria adversarial de 49 agentes
([`studies/porting_validation/AUDIT_2026-08-19.md`](studies/porting_validation/AUDIT_2026-08-19.md)).

Três estudos abertos, e o trabalho novo vai para o primeiro:

| estudo | pergunta | estado |
|---|---|---|
| [`studies/v19_defence/`](studies/v19_defence/STATE.md) | a **vitrine** do protocolo de avaliação novo — o conjunto contra os dedicados, sob a escada do §2a | **VIVO — rodando**. Alabama e Istambul fechados em 25-08 (P=6, resolveram), auditados; faltam AZ/FL/CA/TX. A leitura NÃO aconteceu |
| [`studies/improvements/`](studies/improvements/STUDY.md) | o que melhorar agora que o porte está em paridade? | pausado desde 21-08 |
| [`studies/root_migration/`](studies/root_migration/STUDY.md) | promover o `mtlcheck/` a raiz | bloqueado |

> ⚠ **Se você vai executar qualquer coisa, leia [`studies/v19_defence/STATE.md`](studies/v19_defence/STATE.md) primeiro.**
> Aquele estudo gasta um recurso que não se recompõe: cada `mtlcheck compare` consome, de uma vez e
> para sempre, o teste externo de um conjunto. Trinta e seis pares já foram gastos e estão em
> `studies/READ_LEDGER.json` — o arquivamento da campanha da ponte **não os devolve**. A defesa é em
> **2026-08-28**.

> ⚠ **A ponte de calibração foi aposentada em 25-08.** Quem transferia dispersão de conjunto pequeno
> para licenciar menos execuções no grande agora é a **escada do §2a**: cada conjunto mede a própria
> dispersão na validação interna e escala sozinho, de 2 a 6 execuções, com os dois botões
> (`split_seed`, `model_seed`) sorteados juntos. O protocolo antigo está preservado sem edição em
> [`docs/v19_RECORD.md`](docs/v19_RECORD.md); a campanha que o rodou, em
> [`studies/archive/v19_defence_bridge/`](studies/archive/v19_defence_bridge/ARQUIVADO.md).

⚠ **A barra do `improvements` é o INVERSO da do `porting_validation`.** Lá um Δ dentro do ruído é
sucesso; aqui é um Δ **fora** do ruído, na direção certa — e um número que sai de lá **não é
comparável** com a dissertação sem nomear a mudança. Confundir os dois é o erro que o
[`docs/DIVERGENCE_REGISTER.md`](docs/DIVERGENCE_REGISTER.md) existe para desfazer.

## ⚠ Antes de executar QUALQUER COISA

**Leia [`docs/RUNNING_STUDIES.md`](docs/RUNNING_STUDIES.md).** Ele é curto e existe porque a regra
que ele descreve já foi quebrada três vezes neste projeto — duas no repo de referência e uma aqui,
em 2026-08-19, pela sessão que escreveu a própria regra.

A regra, em uma linha: **toda célula cujo número alguém vai citar sai de um manifesto de wave,
executado por `mtlcheck wave run`.** `mtlcheck train` direto é depuração descartável e vai para um
estudo `scratch*`.

O que isso protege, concretamente: o `test_studies_contract.py` proíbe ciência executável dentro de
`studies/`, mas não impede drivers de shell FORA do repo — e foi exatamente assim que 46 estudos
foram bancados contra 9 manifestos, com os números existindo e a matriz não existindo em lugar
nenhum reproduzível.

Duas armadilhas que o documento detalha e que custam caro:

* um número de `inner_val` **não é resultado** — é a leitura que escolhe a época;
* números deste protocolo **não se comparam** com números do v18 (`eval_stream` diferente).


## As três regras que este projeto existe para manter

1. **Nenhuma variável de ambiente decide ciência.** As únicas três lidas são de caminho
   (`DATA_ROOT`, `ARTIFACTS_ROOT`, `RUNS_ROOT`) e nenhuma pode mudar um número. O repo antigo
   roteava ~25 variáveis para decisões científicas, e uma delas vazou de uma função de shell e
   rodou 8 de 10 células em fp16 enquanto os arquivos de proveniência afirmavam fp32.
2. **Ciência inválida não constrói.** Uma receita que põe logit adjustment na cabeça de região, ou
   que empilha logit adjustment com pesos de classe, levanta exceção em `config.py` — não emite um
   WARN num log que ninguém lê.
3. **Um estudo nunca contém código executável de ciência.** Contrato em
   [`studies/README.md`](studies/README.md), verificado por `tests/test_studies_contract.py`.

## Convenção de comentários

Uma linha, no máximo. Prefira não comentar. Remova o que não serve mais.

O que **merece** comentário aqui: o motivo de um valor ser aquele e não o óbvio, uma armadilha que já
mordeu alguém, e uma decisão que um leitor desfaria por engano. O que **não** merece: descrever o que
o código já diz, história de como se chegou ali, ou justificativa defensiva.

Se precisar de mais de uma linha, provavelmente é docstring de módulo — onde o contexto longo tem
lugar — ou pertence a `docs/`.

> ⚠ **O código atual viola isto.** Escrevi muitos blocos de três a seis linhas ao portar, quando cada
> armadilha era descoberta. A varredura está pendente (ver `studies/porting_validation/PLAN.md §5`);
> o critério é: sobrevive o que um agente futuro erraria sem ele.

## Comandos

```bash
# A versão congelada da campanha é a v19. As receitas v18 continuam existindo para reprodução
# histórica — usá-las por engano constrói outro substrato, em silêncio.
mtlcheck check2hgi build --recipe recipes/v19/substrate.toml --state alabama
mtlcheck train --recipe recipes/v19/cat.toml --state alabama --seed 0 --split-seed 0
mtlcheck train --recipe recipes/v19/joint.toml --state alabama --seed 0 --split-seed 0 --dry-run
mtlcheck wave run studies/<estudo>/waves/<manifesto>.toml
```

Receitas em `recipes/` são **congeladas**: uma receita citada por um resultado bancado é imutável;
uma configuração nova é um arquivo novo.

## Onde as coisas ficam

| Caminho | O quê | Git |
|---|---|---|
| `src/mtlcheck/` | o pacote | sim |
| `recipes/` | receitas congeladas | sim |
| `studies/` | workspaces de pesquisa | sim (só prosa, manifesto, board) |
| `docs/` | prosa curada | sim |
| `tests/` | equivalência + contrato | sim |
| `data/` | corpora brutos | não |
| `artifacts/` | substratos (44 GB) | só os `manifest.json` |
| `runs/` | saídas por execução | não |
| `scratch/` | efêmero | não |

No A40, aponte `ARTIFACTS_ROOT` e `RUNS_ROOT` para `/dados` — `/home` está a 90 %.

## Estado (2026-08-19)

> A versão anterior desta seção era de 13-08 e **negava o resultado central** — dizia "wave/CLI não
> implementada" depois de uma wave de 36 células ter rodado, "sem testes de significância" com o
> `eval/compare.py` pronto, e "nenhuma célula de região ou conjunta foi rodada contra a referência"
> quando a paridade de região é a conclusão principal. Ela é injetada em toda sessão de agente, então
> todo agente começava com o estado de seis dias atrás.

| Camada | Estado |
|---|---|
| 1 · substrato | ✅ **do corpus bruto ao substrato, sem nada do repo antigo.** Delaunay, POI2Vec e o join espacial de regiões computados em processo; encoder portado e validado por transplante de pesos |
| 2 · dados | ✅ sequências, split, tensores, pareamento — E1-E5 contra a referência |
| 3 · treino | ✅ um runner para cat/reg/joint; loss e métricas bit-exatas |
| avaliação | ✅ Tier A (bootstrap por usuário, BCa, permutação estudentizada), TOST, multiplicidade, piso de re-execução, gate de permutação, canário de vazamento |
| telemetria | ✅ sonda de gradiente, FLOPs, retenção de checkpoint, §8a |
| wave / CLI | ✅ `wave plan/run/status`, resume honesto, substrato declarado, linhagem carimbada |

**Paridade contra a referência, sob protocolo pareado:**

| família | Δ | proveniência |
|---|---:|---|
| **região** | **+0,054 pp** | ✅ `waves/ref_parity_al.toml`, partição idêntica por hash nos 5 folds |
| categoria | *(re-executando)* | ⚠ rebaixada em 19-08 — a alegação anterior não tinha manifesto |

**O que NÃO é verdade e é fácil supor que seja:**

* "o substrato é causal" — **não é**. O forward-only fecha o canal linha a linha (os 28,63 pp); o
  substrato segue treinado uma vez sobre o corpus inteiro, sem split de fold.
* "melhoramos X pp sobre a dissertação" — as correções do POI2Vec valeram +0,86 pp e foram
  **correções de migração**, bugs nossos. O resultado é **paridade**. Ver
  [`docs/DIVERGENCE_REGISTER.md`](docs/DIVERGENCE_REGISTER.md).
* números de `inner_val` **não são resultado** — escolhem a época. Ver
  [`docs/QUAL_CONJUNTO_USAR.md`](docs/QUAL_CONJUNTO_USAR.md).

Suíte: **750 testes** (24-08) no venv do projeto (25 skips são os que importam a referência e precisam das
dependências dela). ⚠ **Nunca declare verde com `--ignore=tests/equivalence`** — foi assim que oito
falhas ficaram escondidas por um dia. Ver [`docs/RUNNING_STUDIES.md`](docs/RUNNING_STUDIES.md) §7.

**Validação de ponta a ponta (2026-08-13):** Alabama, categoria dedicada, seed 0, 5 folds, mesma
máquina e mesmo device, mesmos folds (verificados por hash) e mesma convenção de métrica.

| | média | desvio entre folds |
|---|---:|---:|
| referência (main, local) | 30,7605 | 1,0135 |
| `mtlcheck` (local) | 30,7669 | 1,0531 |
| board v18 (A40, n=20) | 30,775 | 0,068 entre seeds |

A diferença entre as médias é **0,006 pp contra um erro-padrão da diferença de ~0,08 pp**, e os
folds individuais diferem em até **0,28 pp**. A leitura honesta é "reproduz dentro do ruído de
execução", não "idêntico" — a concordância na terceira casa é sorte (probabilidade ~7 %). As duas
execuções locais ficam a ≤0,015 pp do board. As épocas escolhidas diferem ([18,16,18,22,16] contra
[13,19,15,25,20]), como esperado de uma reescrita que não consome o RNG na mesma ordem.

**Tempo:** 827 s contra ~1 121 s. A maior parte dos ~295 s de diferença é **instrumentação**, não
velocidade de treino: a referência acumula métrica de treino por época, copia o melhor estado a cada
melhora, faz duas passadas extras de validação por fold e escreve 62 artefatos de diagnóstico. Em
regime, ~3,3 s/época contra ~4,4 s/época. É "o runner enxuto contra o harness instrumentado".

⚠ **A frase que estava aqui — "nenhuma célula de região ou conjunta foi rodada contra a
referência" — é de 13-08 e foi superada em 19-08.** A região FOI rodada e reproduz: Δ pareado
**+0,054 pp** sobre partição verificada idêntica por hash nos cinco folds
([`studies/porting_validation/PLAN.md`](studies/porting_validation/PLAN.md) §4).

O que ainda **não** tem paridade medida: o modelo conjunto. As capacidades conferem, incluindo o
total de 4 197 621 pelo caminho da receita, e o transplante de pesos dá `max|Δ| = 0` nas duas
cabeças — mas o braço pareado da referência foi interrompido por decisão do autor, porque com o
protocolo de avaliação mudado uma paridade célula-a-célula mede o porte e o protocolo ao mesmo
tempo.
