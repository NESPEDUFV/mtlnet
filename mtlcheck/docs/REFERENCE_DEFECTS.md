# Defeitos encontrados no código de referência

> Política do autor (2026-08-13): **defeito encontrado no código antigo durante a portabilidade é
> documentado aqui e corrigido no código novo** — não reproduzido.
>
> Isto é diferente do ledger D1-D12 do [`SYSTEM_MAP.md`](SYSTEM_MAP.md), que registra divergências
> entre o que a documentação afirma e o que o código faz. Ali o código pode estar certo e a doc
> errada. Aqui o **código está errado**.
>
> Cada item responde três perguntas, nesta ordem, porque a terceira só importa se a segunda for
> "sim": **o que é**, **afeta algum número bancado**, **o que o `mtlcheck` faz**.

## Status de cada item — o que já é código e o que ainda é plano

Uma revisão adversarial (2026-08-13) apontou que a coluna "o que o mtlcheck faz" estava escrita no
presente para itens que ainda não existiam. Isso é exatamente o modo de falha que este projeto foi
criado para eliminar, então cada item agora carrega status.

| # | Defeito | Status da correção |
|---|---|---|
| R1 | Trio de LR só ativado por env var | ✅ **implementado** — `config.TrainConfig` recusa joint sem os três |
| R2 | Precisão dependente do estado | ✅ **implementado** — `device.resolve` + campo obrigatório |
| R3 | `export` vazando entre células | ✅ **implementado** — nenhuma env var decide ciência, e o executor de wave existe (`train/wave.py`, `mtlcheck wave run`). ⚠ *Existir não bastou*: a campanha de 19-08 rodou por scripts fora do repo mesmo assim, e o que fechou foi a linhagem carimbada na célula e recusada no consumo (`eval/predictions.py::assert_comparable`) |
| R4 | Sem defesa contra tipo de identificador | ✅ **implementado** — `mtlcheck.ids` |
| R5 | Loader duplica linhas com tamanhos diferentes | ✅ **implementado** — `loaders.joint_batches` levanta exceção |
| R6 | Prior inerte alocado e executado | ✅ **implementado** — `models/stan.py` não constrói o buffer nem o ramo |
| R7 | Metadata afirma vocabulário que o código não usa | ✅ **implementado** — `substrate.corpus` codifica por ordenação explícita |
| R8 | Quarta coluna de tempo com nome errado | ✅ **implementado** — `gap_is_zero` no layout |
| R9 | `n` lido do campo errado | ✅ **implementado** — `train/stats.py` pareia sobre células comuns e reporta `n` por coluna. *O defeito foi corrigido a montante em 2026-08-11* — mantido como registro histórico |
| R10 | Scorer chamado com falha suprimida | ✅ **implementado** — as duas convenções saem de uma execução e vão para `result.json` junto da config resolvida |
| R11 | Pooling assume empacotamento à esquerda | ✅ **implementado** — forma robusta nas duas cabeças (`gru.last_valid_index`, `stan.last_valid_index_from_mask`) |
| R12 | Torre privada preenchida com zeros | ✅ **implementado** — `DualTowerRegionHead` levanta exceção com entrada ausente |

## Como ler a coluna "afeta números bancados"

- **Não** — o defeito existe mas nunca foi atingido na configuração que rodou. Corrigir é gratuito.
- **Não, por sorte** — não foi atingido porque a entrada, hoje, tem a forma certa. Uma mudança de
  artefato o ativaria em silêncio. Corrigir é barato e evita uma bomba-relógio.
- **Sim** — números publicados dependem dele. Corrigir muda resultado, e a correção precisa de
  medição, não só de código.

---

## R1 · O trio de LR por cabeça só era ativado por variável de ambiente

**O que é.** `--cat-lr/--reg-lr/--shared-lr` só têm efeito quando `MTL_ONECYCLE_PER_HEAD_LR=1` está
exportado. Sem a variável, o `max_lr` escalar se propaga para todos os grupos de parâmetros e a
execução vira a receita anterior — mesmo comando, outro experimento, sem nenhuma mensagem.
Documentado no próprio driver (`run_wave.sh:15-16`): *"sem ele o max_lr escalar se propaga para todos
os grupos e a run é silenciosamente v16, não v17"*.

**Afeta números bancados?** Não — todo driver do v18 exporta a variável.

**O que o `mtlcheck` faz.** A presença dos três valores **é** a ativação, e a família joint
**recusa construir** sem eles (`config.TrainConfig.__post_init__`). Não há estado externo que possa
desligar um mecanismo que o comando pediu.

---

## R2 · A precisão de uma execução sem flags depende do estado

**O que é.** `_auto_fp32_for_large_c` (`mtl_cv.py:1151-1167`) escolhe fp16 ou fp32 conforme a
cardinalidade de regiões do estado. Uma execução idêntica em Alabama e em California roda em
precisões diferentes sem que nada no comando diga isso.

**Afeta números bancados?** Não — as células v18 fixam `MTL_DISABLE_AMP=1` explicitamente.

**O que o `mtlcheck` faz.** Precisão é campo obrigatório da config, serializado com o resultado. Não
existe "sem flags". E `device.resolve` **recusa** uma precisão indisponível no device em vez de
rebaixá-la em silêncio — uma execução que pediu bf16 e recebeu fp32 é outra execução.

---

## R3 · Um `export` em função de shell vazava entre células

**O que é.** `cell_joint` fazia `export MTL_DISABLE_AMP=1`; o export persiste nas células seguintes
do mesmo shell; `cell_cat` nunca setava nem limpava. O resultado dependia de a wave ter sido
**retomada** ou não, porque na retomada as células anteriores são puladas e não exportam nada.

**Afeta números bancados?** **Sim, na wave superseded** — 8 de 10 células de categoria rodaram fp16
enquanto o sidecar afirmava fp32; invalidou a comparação cross-seed de Florida e o único "beats" da
coluna de categoria (Texas). Corrigido a montante em 2026-08-09; as células afetadas saíram do board.

**O que o `mtlcheck` faz.** Nenhuma variável de ambiente decide ciência, e nenhum script de shell
executa uma célula. A matriz de experimentos é um manifesto declarativo e o executor está no pacote.

---

## R4 · Nenhuma defesa contra a incompatibilidade de tipo de identificador

**O que é.** `userid` e `placeid` são gravados ora como string, ora como int, em artefatos do mesmo
engine. O caminho do split se protege com um `.astype(int)` sem comentário
(`folds.py`, `load_next_data`); o caminho de lookup de região **não se protege** — funciona porque
hoje recebe o tipo certo. Detalhe agravante: um `.get(pid, 0)` complacente em qualquer ponto desse
caminho colocaria toda visita na região 0, silenciosamente.

**Afeta números bancados?** Não, por sorte.

**O que o `mtlcheck` faz.** Identificadores atravessam toda fronteira por `mtlcheck.ids`, que nomeia
o identificador ao falhar. Ver D10 e D12 no `SYSTEM_MAP`.

---

## R5 · O loader conjunto duplica linhas quando os dois fluxos têm tamanhos diferentes

**O que é.** `zip_longest_cycle` recicla o loader mais curto, e as saídas reprocessadas são contadas
**de novo** nas métricas pontuadas, super-ponderando um subconjunto determinístico da validação
daquela tarefa. O próprio código emite um WARN e segue (`mtl_eval.py:241-249`).

**Afeta números bancados?** Não — no par de tarefas do check2hgi as duas tarefas indexam as mesmas
linhas, então os tamanhos sempre batem.

**O que o `mtlcheck` faz.** `loaders.joint_batches` **levanta exceção** com tamanhos diferentes. Num
par de tarefas que compartilha linhas, tamanhos diferentes significam que algo a montante quebrou, e
super-ponderar um subconjunto é a resposta errada para isso.

---

## R6 · O prior inerte alocava e executava trabalho identicamente nulo

**O que é.** Com `freeze_alpha=True, alpha_init=0.0`, a cabeça de região registrava um tensor
`[C,C]` de zeros (289 MB de VRAM em California) e executava, a cada forward, um gather `[B,C]`, um
`masked_fill`, uma multiplicação por zero e uma soma — em treino e em validação.

**Afeta números bancados?** Não — o resultado é aritmeticamente idêntico.

**O que o `mtlcheck` faz.** Prior desligado é **ramo ausente**: sem tensor, sem gather. Um prior
ativo é outro objeto, com os guards de vazamento intactos. (O repo antigo já pula o gather desde
`aab23985` e a carga do arquivo desde 2026-06-26; o que sobrava era o buffer.)

---

## R7 · Metadata de build afirma uma fonte de vocabulário que o código não usa

**O que é.** O `build.json` registra que os códigos de categoria vêm de um `CATEGORIES_MAP` fixo. O
código usa um `LabelEncoder` ajustado no corpus (`preprocess.py:107-110`). Os dois coincidem hoje
porque o mapa fixo é alfabético e o encoder ordena — mas a metadata descreve uma garantia que não
existe.

**Afeta números bancados?** Não.

**O que o `mtlcheck` faz.** Codifica por ordenação explícita dos nomes e **registra a regra**, não a
fonte imaginada. O manifesto não copia esse campo.

---

## R8 · A quarta coluna de tempo tem nome errado

**O que é.** O `build.json` chama a coluna de `is_first_visit`; o código computa `gap == 0`
(`build_study_repr.py:418-432`), então empates de timestamp também recebem 1.0 — e a ordem entre
empatados não é estável.

**Afeta números bancados?** Não (nenhum dos seis corpora tem timestamps sub-segundo; verifiquei).

**O que o `mtlcheck` faz.** Reproduz o comportamento, registra o nome honesto (`gap_is_zero`) e
mantém a ressalva de estabilidade de ordenação no `SYSTEM_MAP`.

---

## R9 · O `n` da tabela de resultados é lido do campo errado

**O que é.** `make_results.py:156` lê o `n` do campo de categoria, então em TX e CA a tabela publica
um `n` que vale para a coluna de categoria mas não para a de região — só a família **dedicada de
região** parou nas seeds {0,1}.

**Afeta números bancados?** **Sim, na apresentação** — os valores estão certos, o `n` ao lado deles
não. Um `n` errado ao lado de um `p` muda como o leitor pesa o resultado.

**O que o `mtlcheck` faz.** A camada de estatística carrega `n` **por coluna**, junto da unidade de
pareamento, e o serializador recusa emitir um Δ cujas duas colunas não compartilhem o mesmo conjunto
de seeds. Ver S16 e D7.

---

## R10 · Um scorer é chamado com falha suprimida

**O que é.** `run_wave.sh:226` invoca o scorer de joint-best com `|| true`, então qualquer falha dele
passa silenciosamente. Resultado observável: a lane joint-best do v18 está **inteiramente vazia**
(`V18_RESULTS.md §2`, todas as células "—") e ninguém notou.

**Afeta números bancados?** Não os que existem — impediu que uma coluna inteira existisse.

**O que o `mtlcheck` faz.** As duas convenções de seleção de época são calculadas **dentro** da
execução e gravadas no resultado, não por um passo posterior que pode falhar sem consequência. Por
decisão do autor (2026-08-12) o gate popula essa lane.

---

## R11 · Pooling do último passo válido assume empacotamento à esquerda

**O que é.** A cabeça STAN localiza o último passo válido por contagem (`last_idx = num_valid - 1`),
que está correto para sequências empacotadas à esquerda e **silenciosamente errado** sob padding
interior ou à direita. Registrado no catálogo de levers como "U1", bit-idêntico nos dados de hoje.

**Afeta números bancados?** Não — no stride 1 não existe padding nenhum (D11).

**O que o `mtlcheck` faz.** Implementa a forma robusta (posição do último `True`) desde o início. É
gratuito e correto, e remove a dependência de um invariante de empacotamento que nada verifica.

---

## R12 · A torre privada é preenchida com zeros quando sua entrada falta

**O que é.** O `_fuse` da cabeça dual-tower preenche a torre privada com zeros se `raw_region_seq`
não chegar, em vez de falhar. Uma entrada ausente vira uma torre silenciosamente inerte.

**Afeta números bancados?** Não — a entrada sempre chega na configuração que rodou.

**O que o `mtlcheck` faz.** Entrada ausente é erro. Uma torre que não recebe o que precisa não deve
produzir um número.

---

## R13 · O guard de RAM exige uma folga fixa, independente do que o dado precisa

**O que é.** `_guard_cpu_resident_ram` recusa a carga quando a memória disponível é menor que uma
folga **fixa de 16 GB**, sem relação com o tamanho real do dataset. Medido ao tentar rodar a célula
de categoria de Alabama nesta máquina:

```
MemoryError: load_next_data: CPU-resident next dataset needs ~0.4 GB (n_rows=96326,
num_features=576) but only 11.5 GB is available (head-room 16.0 GB).
```

Ele **calcula corretamente** que precisa de 0,4 GB e mesmo assim recusa, porque a folga não é uma
função da necessidade. Consequência prática: nenhuma máquina com menos de 16 GB livres roda
**qualquer** estado, nem o menor deles. A mensagem ainda sugere "um build stride-1 de estado grande"
como causa provável, o que é enganoso quando o dataset em questão pede 0,4 GB.

**Afeta números bancados?** Não — o A40 tem 125 GB. Afeta quem tenta reproduzir em outro lugar, que
é justamente para quem um guard desses deveria servir.

**O que o `mtlcheck` faz.** ✅ **corrigido** (`src/mtlcheck/memory.py`, 2026-08-13). `memory.check`
compara a necessidade estimada — derivada da forma real do tensor — com o disponível, e exige uma
margem **proporcional**: `necessidade × 1,6 + 1 GB`. Com 4 GB livres, Alabama passa e Texas avisa; a
referência recusa os dois. Duas escolhas deliberadas: avisa por padrão e só recusa sob `strict`
(aviso errado custa uma linha de log, recusa errada custa a execução), e prossegue quando não
consegue ler a memória disponível — recusar por não conseguir medir seria o mesmo defeito com outra
roupa. Pinado em `test_assembly.py::test_memory_guard_scales_with_the_requirement`.

## R14 · A auditoria de capacidade conta a cabeça de categoria pelos defaults do módulo, não pela que rodou

> ⚠ **Este é o único item do ledger que toca um número citado na dissertação e no MobiWac.** Não
> corrija nada com base nele sem verificar — o que segue é o que eu medi, e onde a medição para.

**O que é.** `articles/dissertacao/storyline/audit/capacity_baseline_experiment.md §5.1` audita a
capacidade dos arms e registra:

| Dataset | joint (v17 dualtower) | STL cat (next_gru, h=256) | STL reg | combinado | razão |
|---|---:|---:|---:|---:|---:|
| Alabama | 4 197 621 | **644 359** | 417 117 | 1 061 476 | **3,95×** |
| California | 5 151 189 | **644 359** | 1 370 685 | 2 015 044 | **2,56×** |

O valor **644 359** é o que se obtém construindo `next_gru(embed_dim=64, num_classes=7)` com os
**defaults do módulo** — 2 camadas, dropout 0,3. Mas a célula que roda não é essa. O sweep do teto
(`v17_completion/cat_ceiling_sweep/sweep.sh:31`) e o driver do v18 (`v18/run_wave.sh`) usam o mesmo
entrypoint, `scripts/train.py --task next --model next_gru`, e `--model` troca só a **classe**: os
hiperparâmetros continuam vindo do `model_params` de `default_next`, que traz `num_layers=4,
dropout=0.1`. Isso dá **1 433 863** parâmetros (D13).

### Verificação independente, 2026-08-20 — os seis números, um mecanismo só

O mecanismo acima foi confirmado recontando com a cabeça de categoria **deste** pacote, que é
implementação independente. Não sobra ambiguidade: cada valor publicado é a mesma largura contada
com **2 camadas**, e cada valor real é a mesma largura com **4**.

| braço | `hidden_dim` | publicado (L=2, defaults do módulo) | real (L=4, config que roda) |
|---|---:|---:|---:|
| dedicado | 256 | 644 359 | 1 433 863 |
| alargado A | 672 | 4 207 399 | 9 634 471 |
| alargado B | 752 | 5 249 719 | 12 044 791 |

Diferença **zero** nos seis. O apêndice não errou as larguras — contou as três pela profundidade
errada. As larguras 672 e 752 foram recuperadas resolvendo a contagem analítica da GRU
(`3h·64 + 3h² + 6h + (L−1)(6h² + 6h) + 2h + 7h + 7`, validada contra 644 359 e 1 433 863).

**Onde isso morde.** O apêndice de defesa
`articles/dissertacao/wrapup/material_extra/chapters/apx_i_parameter_count_control.tex:89` conclui
que os alargados alcançam **100,2 %** e **101,9 %** do orçamento do conjunto, "so they do not receive
a smaller parameter budget". Com as contagens reais são **229,5 %** (9 634 471 / 4 197 621) e
**233,8 %** (12 044 791 / 5 151 189).

**O que sobrevive, e o que não.** A conclusão fica **mais forte**: o braço alargado recebeu mais que
o dobro do orçamento do conjunto e mesmo assim ficou abaixo do estreito. As razões contra o modelo
original quase não se movem (6,53 e 8,15 documentados contra 6,72 e 8,40 reais), porque as duas
pontas foram construídas pelo mesmo caminho errado e a largura domina. O que **não** sobrevive são os
rótulos: "pareado" e "não recebe orçamento menor".

⚠ **O limite desta verificação.** Ela confirma qual configuração produz cada número publicado. Não
lê o artefato que a execução gravou — para isso faltam os `arch.txt` daqueles rundirs, que só existem
na A40. A primeira etapa é onde o defeito está, e ela está fechada nos seis.

Achado originalmente pela sessão que mantém o `NEW_VERSION.md`; recontagem e as larguras, aqui.

**Evidência direta.** Rodei a célula dedicada de Alabama da main nesta máquina, com a receita v18, e
o próprio log imprime `Params: 1433863` e, ao fim, `Params: 1.43M`.

**Se a cabeça que rodou for a de 1 433 863**, as razões mudam:

| Dataset | documentado | com a cabeça que rodou |
|---|---:|---:|
| Alabama | 4 197 621 / 1 061 476 = **3,95×** | 4 197 621 / 1 850 980 = **2,27×** |
| California | 5 151 189 / 2 015 044 = **2,56×** | 5 151 189 / 2 804 548 = **1,84×** |

E a citação do artigo — "~4.2M vs 1.1M (AL); 5.2 vs 2.0 (CA)" e "~2.6–4.2× params" — passaria a
"~4.2M vs 1.85M (AL); 5.2 vs 2.8M (CA)" e "~1.8–2.3×". O piloto de capacidade equiparada
(`hidden_dim=672`) foi resolvido para alcançar 4,20M **partindo de 644 359**, então a leitura
"quadruplicar os parâmetros do modelo dedicado" descreve um fator 6,5× a partir do número
documentado, e 2,9× a partir do que rodou. A conclusão qualitativa do piloto — um dedicado mais
largo não recupera o ganho do joint — **não depende disso**; a magnitude citada depende.

**Afeta números bancados?** Não os de desempenho. **Sim uma razão publicada**, se a leitura acima
estiver certa.

**E a segunda célula da tabela também está errada — verificado nos pesos salvos.** O braço de
"capacidade equiparada" foi lançado com `--model-param hidden_dim=672`, e o README do estudo diz
"nothing else changed". Mas `--model-param` **mescla** sobre o dict da fábrica
(`train.py:1456-1459`; substituir exige a flag `--replace-model-params`), então `num_layers=4` foi
preservado. O `arch.txt` que a própria execução salvou confirma:

```
GRU(64, 672, num_layers=4, batch_first=True, dropout=0.1)     # alabama
GRU(64, 752, num_layers=4, batch_first=True, dropout=0.1)     # california
```

| | documentado | o que rodou |
|---|---:|---:|
| Alabama, h=672 | 4 207 399 (**100,2 %** do alvo) | **9 634 471** (**230 %** do alvo) |
| California, h=752 | 5 249 719 (**101,9 %** do alvo) | **12 044 791** (**234 %** do alvo) |

Os números documentados são a construção de 2 camadas — o mesmo caminho fora-de-execução que
produziu o 644 359.

**A conclusão qualitativa do controle não cai; ela FICA MAIS FORTE.** O braço não foi equiparado em
capacidade: recebeu **2,3× o orçamento do joint** e ainda assim não recuperou nada da margem
(AL −8,38, CA −7,17 contra o joint). "Damos ao modelo dedicado o orçamento do joint e ele não
recupera" vira "damos a ele mais que o dobro e ele não recupera". O que não sobrevive são os rótulos
"100,2 % equiparado" e "quadruplicar os parâmetros".

**Onde a minha medição para.** Verifiquei, pelos pesos salvos das execuções, a arquitetura dos dois
braços de capacidade equiparada; e verifiquei, por entrypoint e por log de execução viva, a cabeça da
célula dedicada. **Não** verifiquei se a auditoria quis dizer outra coisa por "STL cat" — se foi uma
escolha deliberada de arquitetura nominal, por exemplo. Mas o próprio documento afirma "REPRODUCES
the MobiWac §4 quote exactly", e essa citação é sobre os modelos dedicados da Tabela 3, que são os de
4 camadas. **A decisão sobre a errata é do autor.**

**O que o `mtlcheck` faz.** ✅ A identidade e a forma da cabeça vivem na receita e entram no
fingerprint, e o teste E6 ancora contra **1 433 863** — um número observado fora das duas
implementações, no log de uma execução real.

## R15 · O objetivo do substrato muda com o tamanho do estado, sem registro nenhum

**O que é.** No amostrador de negativos POI↔região do `Check2HGIModule`, 25 % dos negativos são
sorteados de uma banda de similaridade em vez de uniformemente — **mas o ramo inteiro é ignorado
quando o estado tem 50 000 lugares ou mais** (`batch_size < self.p2r_hard_neg_min_batch`, default
50 000, onde `batch_size` é o número de lugares).

Medido nos grafos congelados: AL 11 848, AZ 20 666, IST 29 816 (**com** negativo duro) contra
FL 76 544, TX 160 938, CA 169 145 (**sem**). O corte separa exatamente o mesmo agrupamento
pequeno/grande sobre o qual os resultados são comparados.

> Correção 2026-08-20, em duas partes. **(a)** Este parágrafo dizia "TX maior" sem número, e a
> imprecisão foi propagada daqui para `recipes/v19/substrate.toml` antes de alguém conferir. TX tem
> **menos** lugares que CA. Os seis números batem com
> `articles/dissertacao/src_fix/tables/mobiwac/datasets.tex`.
>
> **(b)** A primeira versão desta nota inferiu que a coluna de lugares da `datasets.tex` seria
> pós-join espacial, porque a contagem de AL (11 848) coincide com a do nosso build. **A inferência
> estava errada**, e medi-la custava uma leitura de parquet: o corpus bruto de Alabama tem
> 113 846 check-ins, 3 858 usuários e 11 848 lugares, e o de Arizona 236 450 / 7 869 / 20 666 — os
> **três** batem com a tabela nos **dois** estados. A coluna é corpus bruto, como as outras duas.
>
> O que a coincidência significa é outra coisa, e é um dado útil sobre o defeito ao lado: **o join
> espacial não descarta lugar nenhum em Alabama nem em Arizona.** O nosso próprio build já registrava
> isso (`0 places outside every tract`) e ninguém conectou. Ou seja, o inner join que descarta em
> silêncio — corrigido aqui para contar e logar — teve zero linhas para descartar nesses dois
> estados; ele continua sendo um risco real, sem ser um dano observado.
>
> A conclusão do R15 não depende de nada disso: 160 938 está 3,2× acima do corte de 50 000.

**Afeta números bancados?** Não os invalida — todos os substratos foram construídos sob esta regra e
são internamente consistentes. Mas invalida a frase "o mesmo substrato foi construído em todos os
estados": foram dois objetivos, e qual deles rodou não aparece em log, manifesto ou nome de arquivo.
Qualquer leitura de "estados grandes têm região pior" precisa considerar que o negativo duro é uma
variável confundida com o tamanho.

**O que o `mtlcheck` faz.** ✅ **corrigido**, removendo a causa em vez do sintoma.

### MEDIDO 2026-08-21 — o gate não muda nada, e isso fecha a decisão de CA/TX

A decisão "sob qual objetivo construir CA e TX" estava registrada como bloqueio com prazo. Foi
respondida medindo na **Flórida** — 76 544 lugares, acima do corte de 50 000 como CA/TX, mas estado de
desenvolvimento e não a reserva. Dois substratos completos, mesma partição, mesma semente:

| | gate LIGADO (v19) | gate 50 000 (a divisão da referência) | Δ | erro-padrão |
|---|---:|---:|---:|---:|
| categoria dedicada | 38,6722 | 38,6856 | −0,013 | 0,019 |
| região dedicada | 76,1414 | 76,1089 | +0,033 | 0,045 |
| joint · categoria | 38,7767 | 38,7639 | +0,013 | 0,019 |
| joint · região | 76,4152 | 76,3937 | +0,022 | 0,049 |

**Os quatro Δ estão dentro do erro-padrão** e abaixo do piso de ruído entre sorteios (0,034 pp).
Ligar ou desligar o negativo duro num estado grande não move nada mensurável.

**O que isto decide.** Os dois caminhos dão o mesmo resultado, então não há trade-off: fica o
objetivo único (o default da v19, mais limpo de descrever) e a escolha é declarada na receita. O
bloqueio de `PLAN.md §3.1` está resolvido — não por escolha, por medição.

**O que isto diz do próprio R15.** A leitura de que "estados grandes têm região pior porque o
negativo duro estava desligado" **não se sustenta**: onde dá para medir, o negativo duro não explica
diferença nenhuma. O defeito continua real como *variável confundida não registrada* — nada em log,
manifesto ou nome de arquivo dizia qual objetivo rodou — mas o efeito dela é nulo na única escala
onde foi medido.

⚠ Uma semente, validação interna, um estado. Suficiente para descartar um efeito da ordem da margem
(0,4 pp); não é um veredito sobre efeitos muito menores.

### A varredura, 2026-08-20 — o R15 é caso isolado, verificado

O R15 pertence a uma classe: **configuração cujo default decide ciência em silêncio e só se manifesta
em escala ainda não rodada.** Ele foi encontrado por acaso, ao conferir outra coisa, o que levanta a
pergunta óbvia — há outros? Varridos os **59 campos** de `SubstrateConfig` (25), `DataConfig` (9) e
`TrainConfig` (25), mais toda condicional que compara contra quantidade contável e toda leitura de
ambiente.

**Resultado: nenhum outro.** Escrito porque ausência verificada é diferente de ausência não
procurada — sem isto, o R15 fica como sintoma de um problema não investigado em vez de caso isolado.

Os quatro ramos condicionados a escala que existem, e por que nenhum é da classe:

| onde | condição | veredito |
|---|---|---|
| `train/metrics.py:81` | `rank <= min(k, n_classes)` | tratamento **correto** de poucas classes (top-10 com 7 categorias), e o ramo de ambiguidade é pulado porque não existe fronteira k/k+1. Direção pequena, não grande |
| `train/metrics.py:195` | `mps and logits.numel() > 2³¹` | limite de plataforma do MPSGraph, documentado, cai para CPU — mais lento, **mesmos números**. A A40 é CUDA |
| `substrate/poi2vec.py:229` | `count <= len(pool)` | o fallback de negativos quando a lista de candidatos é menor que 20. Escala com o vocabulário de fclass, na direção **pequena**, e reproduz o ramo da própria referência |
| `substrate/model.py:170` | `gate is None or num_places < gate` | **é o R15.** O único que muda o objetivo |

E o canal de ambiente, que na referência era o pior: as únicas leituras em `src/` são as três raízes
de caminho (`DATA_ROOT`, `ARTIFACTS_ROOT`, `RUNS_ROOT` — localização, não ciência) e o
`CUBLAS_WORKSPACE_CONFIG`, fixado defensivamente para determinismo. **Nenhum interruptor de ciência
vem do ambiente** — o contraste é com a família `MTL_*` da referência, onde um `export` vazado entre
funções de shell trocou a precisão de oito células de categoria sem que os sidecars soubessem.

O gate existe porque o ramo duro da referência é um laço Python com um sync por sorteio. Medido:
72 µs por sorteio × 42 286 sorteios = **3,1 s por época na Califórnia** — meia hora a mais num build
de 500 épocas. Caro, não impossível; caro o bastante para alguém ter escolhido um limiar em vez de
reescrever o sorteio.

O sorteio agora é vetorizado sobre um índice CSR da banda de similaridade, construído uma vez:
**0,11 ms por época na Califórnia** (63 MB de índice, 8 ms para construir) contra os 3,1 s do laço.
Sem laço, sem sync — e portanto **sem razão para o gate**. Negativo duro fica ligado em todos os
estados (`p2r_hard_neg_size_gate=None`, o padrão), que é a receita como descrita.
`p2r_hard_neg_size_gate=50_000` restaura o corte da referência.

**O que isso custa, dito abertamente:** um substrato de estado grande construído aqui treina sobre um
objetivo diferente do bancado, então não é comparável célula a célula com FL/CA/TX antigos sem
reconstruir. Para estados pequenos nada muda conceitualmente (já tinham negativo duro), embora o
stream de RNG mude — o que é irrelevante dado o R16.

Vetorizar não é bit-idêntico, então a evidência foi reorganizada em vez de perdida: a distribuição é
comparada contra o laço (taxa de reamostragem, pertinência à banda, uniformidade dentro dela), e a
loss e o gradiente são comparados **exatamente** alimentando os dois lados com os mesmos índices —
o que isola "o sorteio mudou" de "o que consome o sorteio mudou". Invariante **S17** no `SYSTEM_MAP.md`.

## R16 · O build do substrato não é reprodutível nem contra ele mesmo

**O que é.** A referência, rodada **duas vezes com a mesma seed, na mesma máquina, com o mesmo
código**, produz substratos diferentes. Medido no A40, Alabama, 500 épocas:

| | run A | run B |
|---|---:|---:|
| melhor loss | 0,22362 @499 | 0,23213 @499 |
| primeira época em que as curvas divergem | \_ | **época 5** |
| embeddings (cosseno médio) | check-in 0,9945 · lugar 0,9965 · região 0,9886 | |

A causa são os três `scatter`/`index_add_` de cada forward — os dois pools de atenção e o decoder de
reconstrução — cujos átomicos de CUDA somam floats em ordem não determinística. A diferença nasce na
5ª casa e 500 épocas de um objetivo não-convexo a amplificam.

**Consequência que importa.** Um substrato bancado é **uma amostra**, não uma função da seed. A frase
"reconstruir o substrato com a mesma seed" não é executável — nem pela referência. Isso muda o que se
pode afirmar sobre reprodutibilidade dos artefatos, e não estava registrado em lugar nenhum.

**Isso invalida os resultados?** Não. Os artefatos bancados existem, foram usados, e as comparações
downstream foram feitas todas sobre os MESMOS arquivos. O que cai é a possibilidade de regenerá-los.

**Afeta a validação da reescrita?** Ao contrário — dá a ela a calibração que faltava:

| comparação (Alabama, 500 épocas) | cos check-in | cos lugar | cos região | RMS |
|---|---:|---:|---:|---:|
| referência × referência, **mesma seed** | 0,9945 | 0,9965 | 0,9886 | 0,153 |
| **`mtlcheck` × referência, mesma seed** | **0,9932** | **0,9955** | **0,9787** | **0,163** |
| referência × referência, seeds diferentes | 0,089 | 0,292 | 0,433 | 1,855 |

⚠ **Corrigido 2026-08-16 após review.** A frase original aqui dizia que a distância entre as
implementações era "praticamente a distância da referência a si mesma". Com **n = 1** isso não era
verificável, e arredondava a favor. Com o piso medido como distribuição (5 execuções, 10 pares,
`evidence/floor_distribution.json`), em `1 − cos`:

| nível | port | piso mín – máx | veredito |
|---|---:|---:|---|
| check-in | 0,00675 | 0,00129 – 0,00717 | dentro |
| lugar | 0,00455 | 0,00146 – 0,00453 | na borda |
| região | 0,02128 | 0,00604 – 0,01147 | **fora, 1,9× o máximo** |

O nível de região **não** está dentro do desacordo da referência consigo mesma — **medido com n = 1
dos dois lados, e isso acabou sendo o erro.**

**Fechado em 2026-08-16 com 5 builds de cada lado** (`evidence/port_distribution.json`): a
distribuição cruzada cai sobre os pisos próprios nos três níveis (região: piso da referência 0,00986,
piso do port 0,01288, cruzado **0,01303** de mediana), e o 0,02128 que abriu a suspeita está dentro
da faixa cruzada. A inflação de norma que seria o marcador sistemático também não existe: −0,5 %,
−1,0 %, +1,2 % por nível, dentro do desvio entre execuções. **As duas implementações amostram a mesma
distribuição.** Melhor loss: referência 0,2349 / `mtlcheck` 0,2328,
contra uma dispersão de 0,0031 entre três seeds da própria referência.

**O que o `mtlcheck` faz.** ✅ **corrigido** — `torch.use_deterministic_algorithms(True)` +
`CUBLAS_WORKSPACE_CONFIG`. Medido: duas execuções com `max|Δ| = 0,0`, sem divergir em nenhuma época,
por **+12,5 % de wall**. **Ligado por padrão** (`train(..., deterministic=True)`), porque não custa
fidelidade nenhuma: o determinismo não recupera os artefatos bancados, mas **nada** os recupera. O que
se ganha é que um build feito hoje pode ser refeito amanhã. `deterministic=False` restaura o
comportamento da referência, inclusive a irreprodutibilidade.

## Itens observados que **não** são defeitos

Registrados para não serem "corrigidos" por engano:

- **`p1` recorrer a seed por fold (`seed + fold_idx`)** — é contrato deliberado, o que torna o
  fan-out por fold idêntico ao sequencial. O `mtlcheck` o adota para todas as famílias.
- **Batch 2048 na região contra 8192 nas outras** — é o default do `p1` que o driver não sobrescreve,
  mas é o que rodou. Harmonizar seria mudar o experimento.
- **Normalização min-max do peso de aresta ajustada no corpus inteiro** — é uma via pela qual o
  pretexto vê informação de fora do passado de uma visita, mas é a definição do substrato, não um
  bug. Registrado em D8.
- **`n_regions = max+1` sobre a tabela completa** — parece desperdício (57 saídas nunca são alvo em
  Alabama), mas é o contrato que define a largura da cabeça. Mudar altera contagem de parâmetros e
  todo denominador de ranking.

## Istambul: 29 % dos lugares não têm coordenada — na FONTE

**Achado 2026-08-21**, ao construir o substrato de Istambul pela primeira vez neste pacote.

⚠ **A primeira versão desta entrada dizia que "os polígonos de mahalle não ladrilham a região
metropolitana" e que o descarte de 30 % era inevitável para essa geometria. Estava errado**, e o
autor mandou verificar em vez de aceitar. A decomposição medida:

| causa | lugares | do corpus |
|---|---:|---:|
| **sem latitude/longitude na fonte** | **12 516** | **29,2 %** |
| lacuna geométrica real (dentro do bbox, fora de polígono) | 328 | 0,77 % |
| coordenada em outro lugar do mundo (uma em Nova York) | 6 | 0,01 % |

O arquivo de mahalles está **correto e íntegro**: 964 polígonos, zero inválidos, zero vazios, e a
área somada dá ~5 425 km² contra os 5 461 km² reais da província. A lógica do join também: ordem
`longitude, latitude` certa, `predicate="intersects"`, ambos em WGS84.

**A causa é dado faltante na origem.** O `tabular` bruto do Massive-STEPS Istanbul
(`massive_steps_istanbul/raw/tabular/*.parquet`) traz **62 621 linhas com `latitude`/`longitude`
nulos** — 11,5 % das 544 471 — e os 12 516 venues afetados **nunca** têm coordenada em nenhuma linha.
**A nossa ETL não perde nada**; o dado não existe.

Esses venues são legítimos: trazem `venue_city` (distritos reais, "Bağcılar", "Üsküdar"),
`state_name` Istanbul, `country_name` Turkey e categoria FSQ. Só não trazem posição.

**Substituir pela coordenada da cidade não é opção.** `venue_city` tem **14 valores distintos** com
14 pares de coordenadas: usá-los colapsaria 12 516 venues em 13 pontos, com os 36 902 check-ins de
Üsküdar num único par. Seria fabricar precisão, não recuperar dado.

**O que a dissertação carrega sem declarar:** Istambul é o único conjunto não-americano da tabela, e
o número dele é sobre **70 % dos venues** e **~85 % dos check-ins**. Os venues sem coordenada são
bem menos visitados (5,0 visitas em média contra 15,9 dos demais), o que amortece a perda — mas não
a elimina. A referência fazia a mesma exclusão, em silêncio, dentro de um CSV de bairros
pré-posicionado.

> ⚠ **Corrigido em 2026-08-23: aqui dizia 88,5 %, e a conta estava errada.** 88,5 % é
> (544 471 − 62 621)/544 471 — subtrai só os check-ins de venue sem coordenada e **esquece o
> descarte geométrico**, os venues que têm coordenada e caem fora de todo polígono. Contando os
> dois, sobram ~462,6 k de 544,5 k, ou seja **~85 %**. Achado numa revisão adversarial da camada de
> substrato. Um número errado dentro de uma ressalva de honestidade é o pior lugar possível para
> ter um número errado, e este iria à defesa.

**No mtlcheck é declarado e separado das outras causas.** `regions.build` retira os lugares sem
coordenada **antes** do join e registra quantos; a guarda de shapefile-trocado passa a medir só
desencontro geométrico, com **limiar único de 20 % para toda fonte**. (Houve por algumas horas um
`MAX_SHARE_OUTSIDE_BY_KEY` que afrouxava para 35 % em `@id` — abstração errada, construída sobre a
explicação errada, e removida quando a medição apareceu.)

⚠ Sobram **129 lugares** de diferença contra a referência (29 945 nossos contra 29 816 dela) que
**não estão explicados**. A contagem de regiões bate exatamente (**520**).

Família: mesma do **R15** — variável que decide o resultado e não é registrada em lugar nenhum.
