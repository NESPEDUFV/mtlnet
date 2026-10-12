# Plano da reescrita — etapas, estado e o que falta

> **Para que este documento existe.** Um agente que abrir este repositório daqui a três meses precisa
> saber, sem reconstruir nada: o que já foi feito e com que evidência, o que falta, o que foi
> deliberadamente deixado de fora e por quê, e onde estão as armadilhas que já custaram tempo.
>
> Atualizado 2026-08-13. Estado operacional do dia a dia: [`STATE.md`](STATE.md).

---

## 0 · O que é este projeto, em três frases

O `mtlcheck` reconstrói o **v18** — predição multitarefa de POI (próxima categoria + próxima região)
sobre um substrato Check2HGI em nível de check-in — a partir do repositório de referência
`/Users/vitor/Desktop/mestrado/ingred`, extraindo o sistema científico e descartando anos de
experimentos que não sobreviveram.

A barra acordada com o autor **não é igualdade dígito a dígito** (inatingível: o protocolo v18 roda
com `--compile`, e a própria referência registra que números compilados não são bit-reproduzíveis).
É reproduzir as **conclusões científicas**, com a camada determinística exata.

Defeito encontrado no código antigo é **documentado e corrigido** no novo, nunca reproduzido.

---

## 1 · As decisões que moldam tudo

Fechadas com o autor entre 2026-08-10 e 2026-08-13. Reabrir qualquer uma muda o projeto.

| # | Decisão | Escolha | Consequência |
|---|---|---|---|
| 1 | Objetivo | Base limpa pós-defesa | Sem pressa; o código antigo continua sendo o que roda até a defesa |
| 2 | Local | Worktree `../mtlcheck`, branch `rewrite/mtlcheck` | O código antigo fica visível ao lado — é o que torna os testes de equivalência possíveis |
| 3 | Escopo do substrato | v18 (check-in) **+** v14 (região) | Os dois, porque a torre de região consome o segundo |
| 4 | Validação | Gate barato local + A40 | Determinístico local, treinado no A40 |
| 5 | Ponto de partida | `data/checkins/<State>.parquet` | A ETL geográfica bruta é fase 2 |
| 6 | Datasets | AL, AZ, IST, FL, CA, TX | Georgia descartada (decisão do autor, 2026-08-12) |
| 7 | Resultados | Formato novo, sem compat | Não replico os sidecars antigos |
| 8 | CLIs | `check2hgi` + `train` + `wave` (+ Modal por último) | |
| 9 | Fidelidade | Conclusões científicas | Ver §4 |
| 10 | **Acoplamento** | Substrato e construção de input são fluxos **separados** | É a decisão mais estruturante; define as três camadas |
| 11 | Substrato | Rebuild dos 6 estados | Encoder portado e CLI pronto; falta rodar os 6 (execução longa, adiada) |

---

## 2 · A arquitetura em uma tela

```
data/checkins/<State>.parquet
        │
        ▼   CAMADA 1 · substrate/          CLI: mtlcheck check2hgi
   corpus → grafo → features → encoder → readout
        │
        │   artefato + manifest.json   ← o contrato entre as camadas
        ▼   CAMADA 2 · data/
   sequências → split → tensores → pareamento → montagem
        │
        ▼   CAMADA 3 · train/              CLI: mtlcheck train
   um runner, três famílias → métricas → seleção de época → resultado
        │
        ▼   wave + score                   CLI: mtlcheck wave
```

A camada 3 **nunca importa** da camada 1. O que hoje é um symlink de filesystem no repo antigo vira
uma referência nomeada no manifesto.

---

## 3 · Etapas — o que está feito, com que evidência

### ✅ Fase 1 · Inspeção e mapa (concluída)

`docs/SYSTEM_MAP.md` — os três caminhos de execução do v18 extraídos do código que rodou, **16
invariantes científicas numeradas (S1-S16)** e **13 divergências entre doc e implementação
(D1-D13)**. `docs/REFERENCE_DEFECTS.md` — **14 defeitos (R1-R14)** com status por item.

### ✅ Fase 2 · Revisão adversarial (concluída, e recorrente)

Quatro rodadas com o Fable 5. Cada uma achou defeito real:

| rodada | o que achou |
|---|---|
| mapa + plano | O pareamento cruzado aleatório (S13) — que eu ia converter em alinhado sem perceber |
| camadas 1-2 | Constante de decaimento 24× errada, invisível a uma suíte que só fixava contagens |
| camada 3 | Loss de validação sempre zero; a raia de scoring da região trocada pela do joint |
| resultados | "Três dentro de 0,01 pp" era exagero; e o braço de capacidade equiparada da dissertação rodou com 2,3× o alvo |

### ✅ Fase 3 · Esqueleto (concluída)

`pyproject`/uv, config congelada com validação na construção, seleção única de device, contrato de
semeadura, três CLIs, sistema de `studies/` com contrato verificado em teste.

### ✅ Fase 4 · Camada 1 — substrato (concluída 2026-08-16)

| peça | estado |
|---|---|
| corpus → grafo → features | ✅ verificado contra as contagens auditadas em **5 de 6 estados** |
| pesos de aresta | ✅ batem com o grafo congelado em <1e-6 (Alabama) |
| join espacial de regiões | ✅ **portado 2026-08-17** — reproduz a hierarquia bancada de AL exatamente; `--shapefile` substitui `--hierarchy` |
| encoders (`resln`, `Checkin2POI`, `POI2Region`) | ✅ portados; transplante de pesos, ≤1e-6 |
| modelo `Check2HGI` (caminho v18) | ✅ portado; mesma loss, mesmos gradientes, **mesma ordem de RNG** |
| carregadores POI2Vec + Delaunay | ✅ bit-idênticos em Alabama real |
| laço de treino (500 épocas, full-batch) | ✅ portado (ver §4 · substrato) |
| materialização dos parquets de saída | ✅ portado — reproduz as tabelas bancadas coluna a coluna |
| **CLI `check2hgi build` / `verify`** | ✅ **feito** — `substrate/pipeline.py`; é o único caminho de build |

### ✅ Fase 5 · Camada 2 — dados (concluída)

Sequências, split, tensores, pareamento, montagem com o guard S9 em runtime e cache em disco.

### ✅ Fase 6 · Camada 3 — treino (concluída)

Loss, métricas, seleção de época, estatística pareada, schema de resultado, diagnósticos, as três
cabeças, o modelo conjunto, os dois runners.

### ✅ Fase 7 · `wave` + `score` (concluída 2026-08-16)

`wave` expande a matriz de um TOML commitado, não de um laço de shell; retoma pulando **só** células
cujo `result.json` faz parse (uma célula que quebrou deixa diretório para trás, e o
"pula-se-o-diretório-existe" da referência re-bancava exatamente essas); uma célula que falha não
derruba a onda, mas o resumo se recusa a apresentar agregado sobre matriz furada sem nomear os
buracos; e as células rodam pelo **mesmo** `_train_cell` do CLI de célula única — a equivalência que
a referência perdeu quando a matriz virou 30+ drivers de shell.

`score` re-deriva os números na CPU a partir do que foi bancado, reporta a dispersão sobre **médias
por seed** (agrupar folds responde "quanto os folds diferem", que ninguém perguntou), tem `--compare`
com a banda pareada, e reporta **para onde foi o wall** ao lado das métricas — de propósito: "vale
otimizar o quê?" deve sair do mesmo artefato que responde "a mudança ajudou?".

### ⚠ Fase 8 · Validação (Alabama fechado, resto pendente)

### ⚠ Fase 9 · Documentação (viva)

### ❌ Fase 10 · Lane Modal (não iniciada)

---

## 4 · A evidência que já existe

### Camada determinística — exata

| teste | o que prova |
|---|---|
| **E1** folds | Idênticos aos do código antigo, **hash a hash**, nas 4 seeds |
| **E5** janelas | `sequences_next.parquet` reproduzido linha a linha do parquet cru |
| **E3/E4** | Contagens, a regra `n_regions = max+1`, alinhamento entre tabelas |
| **E6** capacidade | Cabeça de cat 1 433 863 (log de execução real); reg 417 117 e caminho de região do joint 2 466 542 (`POSTPONED.md`); total do joint 4 197 621 (auditoria) |
| **E7** transplante | Modelo conjunto: pesos da referência carregados no meu → **max\|Δ\| = 0,000e+00** nas duas cabeças |
| **E8** loss | Bit-exata (`atol=0`) contra as **duas** referências |
| **E9** métricas | 1e-9 contra o acumulador da referência; 1e-6 contra o caminho torchmetrics |
| **E10** grafo | Contagens de aresta em 5 de 6 estados; pesos <1e-6 |
| **E11** scheduler | Avanço por passo; `total_steps=500` confere com o estado gravado da referência |

### Caminho treinado — Alabama, seed 0

| família | referência | mtlcheck | Δ | procedência |
|---|---:|---:|---:|---|
| categoria dedicada | 30,7605 | 30,7669 | +0,006 | ✅ execução pareada, 2026-08-13 |
| região dedicada | 69,998 | 70,0517 | +0,054 | ✅ execução pareada, 2026-08-19 |
| joint · categoria | 30,6985 | 30,5409 | — | ⚠ não pareado — ver abaixo |
| joint · região | 69,5928 | 69,6852 | — | ⚠ não pareado — ver abaixo |

⚠ **As três linhas de `reg` e `joint` foram retiradas em 2026-08-19 por falta de procedência.**
Auditadas nesta data, não se sustentam:

* A coluna **referência** é sólida e foi reconferida: 69,9956 / 30,6985 / 69,5928 são células do
  `status.json` bancado do v18 (`/cells[13]`, `/cells[14]`). São números de placar, de outra máquina
  e de outro mês — não de uma execução pareada.
* A coluna **mtlcheck** de reg/joint — 70,0517, 30,5711, 69,7247 — não existia em lugar nenhum:
  nenhuma célula bancada em `runs/`, nenhum arquivo de evidência, nenhuma nota de origem no commit
  que a introduziu (`c571869d`).
  * **A de região foi desde então reproduzida e restaurada.** `ref_parity_al` deu 70,0517 — o mesmo
    valor, na quarta casa. A linha era legítima; faltava-lhe procedência, não correção.
* O `CLAUDE.md` escrito **no mesmo commit** afirma o contrário da tabela: *"nenhuma célula de região
  ou conjunta foi rodada contra a referência"*.

Só a linha de categoria tem execução pareada documentada (mesma máquina, mesmos folds conferidos por
hash, mesma convenção de métrica).

**O que a auditoria descobriu de fato**, ao rodar a referência hoje na A40 sobre o substrato bancado:
a referência reproduz o próprio placar — folds 72,14 / 68,98 / 73,53 / 71,14 / 64,22, média **69,998**
contra 69,9956 bancado. E a célula `al_full` do mtlcheck dá 73,72, **mas sob outro protocolo**: a
referência roda 5-fold plano (treina em 80 %, valida e seleciona nos 20 % de fora), enquanto `al_full`
rodou `inner_validation` (treina em 70 %, valida nos 10 % internos). Treino menor, conjunto de
validação diferente — a divergência cresce por fold (+0,22 no fold 0, +8,78 no fold 4), que é a
assinatura de partições diferentes, não de um defeito de porte.

A comparação pareada de verdade é `waves/ref_parity_al.toml`, executada em 2026-08-19 — **completa
para região, interrompida para o joint**.

⚠ **As duas linhas do joint continuam sem Δ, e a coluna da esquerda continua sendo placar de agosto,
não execução pareada.** A coluna do mtlcheck é agora real e reprodutível (`ref_parity_al`, protocolo
plano, convenção do `a40_score_matched.py`: categoria = média dos `cat_diag_best.f1`, região = média
dos `reg_diag_best.top10_full`). O braço da referência foi interrompido por decisão do autor em
19-08: com o protocolo de avaliação mudado e um conjunto de teste que o v18 não tinha, uma paridade
célula-a-célula contra a dissertação mede o porte e o protocolo ao mesmo tempo. A avaliação contra os
números da dissertação acontece **depois** que o mtlcheck for standalone, levando em conta a lista de
mudanças.

Registro do que a tentativa produziu, porque custou GPU: a primeira execução da referência foi
montada a partir do `run_mtl_alabama.sh` (um driver de sondagem) em vez da célula canônica
`run_wave.sh:186-212`, e perdeu `--logit-adjust-tau 0.5` e `--no-cat-class-weights`. O efeito é
diagnóstico e vale guardar — região reproduziu (69,5990 contra 69,5928 bancado) e categoria não
(27,61 contra 30,70), que é exatamente a assinatura de flags que só alcançam a cabeça de categoria
(`mtl_cv.py:500` mantém o critério de região em CE simples).

**Região, fold a fold, os dois braços medidos no mesmo dia na mesma máquina sobre o mesmo substrato:**

| fold | referência | mtlcheck | Δ |
|---:|---:|---:|---:|
| 0 | 72,14 | 72,06 | −0,08 |
| 1 | 68,98 | 68,96 | −0,02 |
| 2 | 73,53 | 73,67 | +0,14 |
| 3 | 71,14 | 70,91 | −0,23 |
| 4 | 64,22 | 64,66 | +0,44 |
| **média** | **69,998** | **70,052** | **+0,054** |

Δ pareado +0,054 pp, desvio dos deltas ≈ 0,25, erro-padrão ≈ 0,11 — indistinguível de zero.
**`reg` reproduz.** O braço da referência também reproduziu a si mesmo contra o valor bancado de
06-08 dentro de 0,02 pp por fold, que é o piso de ruído de sessão de compilação.

**E a partição é literalmente a mesma.** Os hashes dos cinco conjuntos de validação batem nos dois
lados — `7fe61623544ed762` / `60ddc94e2bc34019` / `50cfad119ed34196` / `a061494dcd33c2e5` /
`fd619b39cafa5649` — com a mesma distribuição das 7 categorias. Então o Δ de +0,054 pp **não tem
componente de partição**; é implementação pura. O cast de `userid` para int64 em `as_group_ids` é o
que faz isso funcionar: no parquet a coluna é `object`, e agrupar pela forma string produziria um
split válido que não é ESTE split.

⚠ **E isto corrige outra afirmação desta seção:** os valores **por fold** do braço da referência
existem sim nesta máquina — em `docs/results/P1/region_head_<estado>_*.json` para a família de
região, e nos rundirs que o `PROVENANCE.md` do v18 lista célula a célula. O denominador pareado é
computável; era só procurar.

**Calibração:** a minha própria implementação move 0,072 pp só ao trocar compilado por eager — esse
é o piso de ruído contra o qual qualquer Δ tem de ser lido. A comparação que essa nota fazia (0,127
contra 0,072) usava o Δ do joint·categoria, que foi retirado acima; a nota fica sem o segundo termo
até `ref_parity_al` fornecer um Δ com procedência.

⚠ **A coluna "Δ / desvio entre folds" saiu daqui em 2026-08-16, e a razão importa.** Ela dividia o Δ
pelo desvio **entre folds** (~1,2 pp em Alabama). Esse é o denominador errado: os folds diferem entre
si por motivos que atingem os dois braços igualmente — usuários diferentes, mistura de classes
diferente — e o pareamento cancela exatamente isso. O denominador certo é o desvio dos **deltas
pareados**, que é muito menor. Julgar contra o desvio entre folds infla a tolerância pelo efeito de
fold, que é quase tudo, e uma regressão real passa batida.

~~Não dá para recomputar a coluna certa a partir do que está bancado: os valores por fold do braço da
referência não existem nesta máquina.~~ **Falso, corrigido em 2026-08-19** — existem em
`docs/results/P1/*.json` (família de região) e nos rundirs que o `PROVENANCE.md` do v18 lista célula a
célula. A coluna foi removida na época por essa premissa errada; o critério certo vive no código: `PairedComparison.stderr` e `.band`, com uma
delta por **seed** (folds dentro de uma seed compartilham ~80 % do treino e não são réplicas).
Pinado em `test_stats_result.py`, que falha se a banda voltar a ser a dispersão não pareada.

### Geometria de gradiente — a conclusão científica reproduzida

Cosseno entre as tarefas sobre o tronco: **+0,00082** (mtlcheck) contra **+0,00148** (referência),
desvio ~0,011, metade das épocas negativa dos dois lados. Gradientes **ortogonais, não competindo** —
que é a razão de toda cirurgia de gradiente ter dado nulo.

### Substrato — o modelo do pretexto (2026-08-13)

Exato onde dá para ser exato. **A coluna "config" existe porque um review de 2026-08-16 pegou a
tabela anterior misturando duas** — as medições contra a referência em dado real só podem rodar no
grafo canônico bancado, que tem 11 canais de feature; o v18 de verdade tem 15 (as 4 colunas de tempo
decorrido). São 256 parâmetros de diferença (4 × 64 na primeira GCNConv), e a tabela antiga citava
"826 827 dos dois lados" sem dizer que o build real do v18 tem **827 083**.

| teste | config | resultado |
|---|---|---|
| 3 encoders, transplante de pesos | 15 canais | ≤1e-6 contra a referência |
| `Check2HGI` completo, loss em `eval` | 15 canais | \|Δ\| < 1e-6 |
| `Check2HGI` completo, loss em `train` **com seed compartilhada** | 15 canais | \|Δ\| < 1e-6 — prova a **ordem** das 3 extrações de RNG |
| gradientes (encoder, pool, tabela de lugares, 2 formas bilineares) | 15 canais | ≤1e-6 |
| loss + gradiente com negativo duro injetado igual dos dois lados | 15 canais | ≤1e-6 |
| contagem de parâmetros | 11 canais | 826 827 dos dois lados |
| contagem de parâmetros | 15 canais (o build real) | 827 083 — sem contraparte na referência medida |
| POI2Vec + Delaunay + alvo de reconstrução (Alabama real) | — | **bit-idênticos** |
| 25 épocas em Alabama real | 11 canais, bidirecional, negativo duro OFF, **determinismo pinado** | divergem só na época **24**; máx \|Δ\| **6,0e-08** ([harness](../../tests/equivalence/harnesses/trajectory_25.py) + [json](evidence/trajectory_25.json)) |

O que a divisão significa: as provas de **função** (loss, gradiente, transplante) rodam na config do
v18; as provas em **dado real contra a referência** rodam na única config em que a referência tem um
artefato comparável. O caminho das 4 colunas de tempo decorrido, portanto, é coberto pelos testes
unitários e não pela trajetória longa.

⚠ **Três números erraram nesta linha antes deste, e todos pelo mesmo motivo.** O original
(8,3e-05, divergindo por volta da época 10) veio de um script perdido em `/tmp`. A primeira
re-execução deu 5,0e-04 divergindo na época 2, e eu atribuí à CUDA; medi na CPU e deu 4,97e-04, o que
derrubou essa explicação. Duas execuções **idênticas** de CPU então deram 4,97e-04 e 3,13e-03 — 6× de
diferença — e aí ficou claro: as reduções `scatter`/`index_add` do torch **também não são
determinísticas na CPU** sob paralelismo de threads. O harness estava medindo o próprio ruído.

Com `use_deterministic_algorithms` e uma thread, o número é estável entre execuções e é **6,0e-08** —
um ULP. As duas implementações são, para efeitos práticos, bit-idênticas por 23 épocas.

Depois disso o caminho é caótico e nenhuma tolerância faz sentido — então a pergunta certa não é
"quão perto", e sim "**perto comparado a quê**". Três medições no A40, Alabama, 500 épocas:

| comparação | cos check-in | cos lugar | cos região | RMS |
|---|---:|---:|---:|---:|
| referência × referência, **mesma seed** | 0,9945 | 0,9965 | 0,9886 | 0,153 |
| **`mtlcheck` × referência, mesma seed** | **0,9932** | **0,9955** | **0,9787** | **0,163** |
| referência × referência, seeds diferentes | 0,089 | 0,292 | 0,433 | 1,855 |

**A referência não é reprodutível contra ela mesma** (R16): duas execuções idênticas divergem na
época 5 e terminam em 0,2236 × 0,2321. Melhor loss: referência 0,2349 / `mtlcheck` 0,2328, contra
0,0031 de dispersão entre três seeds da própria referência.

⚠ **Correção de 2026-08-16.** A redação anterior dizia que a distância entre as implementações "é
praticamente a distância da referência a si mesma". Isso arredondava a favor. Em `1 − cos`, o port
está **fora** daquele piso nos três níveis e sempre no mesmo sentido: 1,23× no check-in
(0,00675 × 0,00548), 1,30× no lugar, **1,86× na região** (0,02128 × 0,01143). Uma diferença
sistemática produz exatamente esse padrão, e com **n = 1** não havia como distinguir. A frase certa é
"a mesma ordem de grandeza do piso, e acima dele" — e o piso virou distribuição (§ piso, abaixo).

Corrigido no código novo: determinismo ligado por padrão — `max|Δ| = 0,0` entre execuções, +12,5 % de
wall. Não recupera os artefatos bancados (nada recupera), mas torna refazível o que se constrói agora.

#### O piso, agora como distribuição (2026-08-16)

Cinco execuções da referência, mesma seed, 10 pares. `1 − cos`, menor é melhor:

| nível | port | piso mín | piso mediana | piso máx | veredito |
|---|---:|---:|---:|---:|---|
| check-in | 0,00675 | 0,00129 | 0,00401 | 0,00717 | **dentro** (≈ percentil 90) |
| lugar | 0,00455 | 0,00146 | 0,00261 | 0,00453 | **na borda** (0,3 % acima do máximo) |
| região | 0,02128 | 0,00604 | 0,00881 | 0,01147 | **fora — 1,9× o máximo, 2,4× a mediana** |

O review estava certo e o `n = 1` estava escondendo isto: **o nível de região não está dentro do
desacordo da referência consigo mesma.** Check-in está; lugar está na borda.

**O que isso significa para o v18, com escopo honesto.** O downstream do v18 consome do substrato
**apenas o nível de check-in** (as 576 colunas de `next.parquet`, que alimentam a categoria e a torre
de categoria do joint). A torre de **região** lê `region_embeddings.parquet` de **outro engine**
(v14, `check2hgi_design_k_resln_mae_l0_1`), não deste substrato — verificado em
`dataset.py:133`. Os níveis de lugar e de região exportados aqui não entram em nenhuma célula v18.

Então: o nível que está fora do piso é o que o v18 não lê, e o nível que o v18 lê está dentro. Isso
**limita** a consequência; não a elimina. Se este código for usado para construir o engine v14 — que
é um uso declarado — a torre de região passa a consumir exatamente o nível divergente.

#### A causa, investigada (2026-08-16)

**Um forward só, pesos idênticos, Alabama real, os três níveis:**

| nível | port × referência | **referência × ela mesma, mesmo forward repetido** |
|---|---:|---:|
| check-in | 1,431e−06 | **1,431e−06** |
| lugar | 9,537e−07 | **9,537e−07** |
| região | 2,384e−07 | **2,384e−07** |

Iguais até o último dígito, e `1 − cos = 0,000e+00` nos três. **O port calcula a mesma função**: a
diferença de um forward é exatamente o ruído do forward da referência consigo mesma (átomos de CUDA
no scatter). Não há diferença aritmética sistemática a explicar.

O nível de região tem a menor magnitude (|x| médio 0,199 contra 0,994 no check-in), então a mesma
perturbação absoluta é ~5× maior em termos relativos, e é o mais fundo da hierarquia. Isso explica
por que ele é o nível onde 500 épocas de dinâmica caótica levam mais longe.

**Um confundidor que eu mesmo introduzi, registrado.** O experimento de trajetória
(`evidence/divergence_trajectory.json`) mostrava o port divergindo já na época 5 enquanto duas
execuções da referência ainda estavam idênticas — o que parecia diferença sistemática. Não é: aquele
run usou o sorteador **vetorizado** (S17), que consome o RNG de forma diferente do laço da
referência, então os negativos duros sorteados já não eram os mesmos no passo 1. A comparação de 500
épocas do `build_compare.json` **não** tem esse problema: rodou antes da vetorização, com o laço.

#### Fechado: distribuição contra distribuição (2026-08-16)

Cinco builds de cada lado, todos não-determinísticos, mesma init. `1 − cos`, mediana [mín–máx]:

| nível | ref × ref (10 pares) | port × port (10 pares) | **ref × port (25 pares)** |
|---|---|---|---|
| check-in | 0,00147 [0,00037–0,00459] | 0,00416 [0,00172–0,01235] | 0,00382 [0,00093–0,00853] |
| lugar | 0,00244 [0,00131–0,00622] | 0,00329 [0,00152–0,00597] | 0,00372 [0,00282–0,00929] |
| região | 0,00986 [0,00312–0,01698] | 0,01288 [0,00420–0,01882] | **0,01303 [0,00722–0,02872]** |

A distribuição cruzada **cai em cima dos dois pisos próprios** nos três níveis. Em região, a mediana
cruzada (0,01303) é praticamente o piso do próprio port (0,01288). E o valor que abriu esta
investigação — 0,02128, do `build_compare` — está **dentro** da faixa cruzada [0,00722–0,02872],
perto do topo. Era um sorteio de cauda, que é exatamente a alternativa que eu tinha deixado viva.

**A inflação de norma foi refutada por medição.** O review apontava inflação monotônica de
+2,7 / +4,8 / +10,5 % por nível, invisível ao cosseno, como o marcador de diferença sistemática.
Medido sobre 5 builds de cada lado:

| nível | \|x\| referência | \|x\| port | inflação |
|---|---:|---:|---:|
| check-in | 1,1087 ± 0,0063 | 1,1035 ± 0,0208 | **−0,5 %** |
| lugar | 0,7687 ± 0,0157 | 0,7613 ± 0,0308 | **−1,0 %** |
| região | 0,6119 ± 0,0138 | 0,6191 ± 0,0311 | **+1,2 %** |

Nem monotônica nem sistemática: três valores dentro do desvio entre execuções, com dois negativos.
Loss: referência 0,22786 ± 0,00268 contra port 0,22863 ± 0,00665. `place_gamma` aprendido:
1,05500 ± 0,00766 contra 1,04956 ± 0,01233. Todos sobrepostos.

**Veredito: as duas implementações produzem substratos da mesma distribuição.** O item de região do
R16 fecha. O que sobrevive como lição não é sobre o código e sim sobre o método: uma comparação n = 1
contra um piso n = 1 sustentou, por dois dias, uma suspeita de defeito sistemático que não existia.

### O círculo fechado — bruto → resultado (2026-08-13)

O materializador foi verificado primeiro contra as tabelas bancadas, a partir dos embeddings
bancados: **todas as colunas idênticas** — as 576 de embedding com `max|Δ| = 0,0`, mais `userid`,
`next_category`, `region_idx`, `last_region_idx` e a testemunha `sequences_next`. De quebra, a tabela
de região caiu de **223 MB para 12 MB**: a referência copia para dentro dela as 576 colunas que a
própria docstring dela chama de "VESTIGIAL", e ninguém lê.

Depois, a cadeia inteira em Alabama — corpus bruto → features (15 canais) → grafo forward-only
(109 988 arestas) → substrato (500 épocas) → tabelas de input → célula de categoria, 5 folds. Só a
hierarquia de regiões vem do artefato bancado (o join espacial é a peça adiada).

E como um substrato é **uma amostra** (R16), a pergunta certa de novo não é "bate?", e sim "quanto o
número anda se eu só reconstruir o substrato?". Três substratos meus, seeds diferentes:

| substrato | loss | macro-F1 | desvio entre folds |
|---|---:|---:|---:|
| meu, seed 42 | 0,20984 | 30,7181 | 1,2585 |
| meu, seed 43 | 0,21223 | 30,8754 | 1,1710 |
| meu, seed 7 | 0,22350 | 30,9001 | 1,2424 |
| **bancado v18** (referência) | — | **30,7013** | 1,0726 |

**Amplitude entre os três substratos meus: 0,18 pp. Distância da média deles ao bancado: +0,13 pp.**

⚠ **Como ler isto, corrigido em 2026-08-16 após review.** Três afirmações que a redação anterior fazia
e que os dados não sustentam:

1. **"Dispersão 0,18 pp" é a amplitude de n = 3**, não um desvio-padrão nem um intervalo. A amplitude
   de três amostras subestima a dispersão da população de forma sistemática e tem ela própria enorme
   variância. Não é um piso; é uma primeira indicação.
2. **A regra "qualquer afirmação com margem abaixo de 0,18 pp está dentro do ruído" foi generalizada
   demais** — de três seeds, num estado, numa métrica, para toda afirmação sobre substrato. Vale
   para: categoria, Alabama, esta receita. Nada além disso, até medir.
3. **Os dois braços não são o mesmo procedimento.** O v18 bancado veio do engine `check2hgi_dk_ovl`
   por um readout por janela (`evidence/banked_v18_materialize.json`); os meus vêm da cadeia nova com
   grafo forward-only de 15 canais. Os meus também convergem para uma loss mais baixa
   (0,210–0,224 contra 0,231–0,238 da referência) — o que se **explica** pelo grafo diferente, não
   por otimização melhor, mas é uma diferença, não ruído. O +0,13 pp mede *cadeia nova × artefato
   antigo*, e não *duas execuções do mesmo processo*.

O que continua de pé, e é o que importa: a cadeia escrita do zero produz um número na mesma faixa do
bancado, com a diferença menor que a amplitude entre reconstruções e muito menor que o desvio entre
folds (~1,2 pp). Não é "reproduz dentro do ruído" com rigor estatístico; é "não há sinal de defeito
nesta resolução".

---

## 5 · O que falta, em ordem de valor

### Alto — bloqueiam a reprodução completa

1. **Join espacial de regiões.** É o que resta entre a cadeia atual e o "do zero": produz
   `placeid_to_idx` / `poi_to_region` / adjacência / área / similaridade, que hoje leio do artefato
   bancado. Adiado por decisão, não por dificuldade. Junto com o HGI (POI2Vec + Delaunay, que **não**
   é portável — é outro engine), é a última dependência externa.
2. **As outras duas famílias sobre substrato próprio.** A categoria fechou (§4); região e joint ainda
   rodaram só sobre o substrato bancado. A célula de região depende sobretudo da torre de região, que
   vem de outro engine (v14) e não mudou — então é o teste menos informativo dos três, mas falta.
3. **`wave` + `score`.** Sem eles não há execução em massa nem re-scoring; a matriz de experimentos
   ainda depende de scripts ad-hoc.
4. **Validação nos outros estados e seeds.** Alabama fechou; AZ/IST têm n=20 no board e dariam poder
   estatístico real. FL/CA/TX agora cabem — o pico de memória caiu de ~79 GB para ~25 GB em TX (§6).

### Médio

5. **Testes de significância** na camada de estatística (t pareado e Wilcoxon, como a referência).
6. **Módulo de monitoramento e relatório** — plano estudado em [`docs/TELEMETRY_GUIDE.md`](../../docs/TELEMETRY_GUIDE.md).
7. **Higiene de comentários** — convenção em `CLAUDE.md`; varredura pendente.
8. **Lane Modal.**

### Registrado e fora de escopo

Estratificação por chave composta; CV aninhado; qualquer lever do catálogo de 27; ativar o prior
`α·log_T`; sweep de arquitetura de cabeça; adotar pareamento alinhado. Todos mudariam os números que
servem de comparação.

---

## 6 · As lacunas de performance — duas fechadas, uma aberta

Detalhe em [`docs/OPTIMIZATIONS.md`](../../docs/OPTIMIZATIONS.md).

**Fechadas em 2026-08-13.** O tensor de check-in passou a ser lido do parquet **uma posição de janela
por vez**, direto para um array já com a forma final: pico de 1,00 GB → 0,32 GB em Alabama, saída
bit-idêntica (verificada contra o caminho antigo *e* contra as colunas cruas). Extrapolado para as
duas torres: TX 79 GB → 25 GB, CA 60 GB → 19 GB — é o pico que forçava FL/CA/TX a rodarem 1-wide. E o
guard de RAM voltou, agora com margem **proporcional** (`necessidade × 1,6 + 1 GB`) em vez dos 16 GB
fixos que recusavam Alabama numa máquina de 12 GB livres.

**Aberta:** `torch.compile` refeito por fold (não corrigido — a correção arrisca a fidelidade). Só
custa wall.

Nenhuma das três afetava **correção** — as três afetavam escala.

---

## 7 · Armadilhas que já custaram tempo

Se você está retomando isto, leia esta seção antes de mexer.

| Armadilha | O que acontece |
|---|---|
| **`--model` troca só a classe** | Os hiperparâmetros vêm do `model_params` da fábrica da tarefa. A cabeça de cat do v18 tem 4 camadas e dropout 0.1, não os 2/0.3 do módulo. Construir pelos defaults dá **menos da metade** do modelo (D13) |
| **`--model-param` mescla** | Não substitui. É por isso que o braço de "capacidade equiparada" da dissertação rodou com 2,3× o alvo (R14) |
| **`userid` e `placeid` mudam de tipo** | String num artefato, int em outro. Agrupar o split por string **redesenha os folds** (D10/D12) |
| **A família de região usa outra convenção de scoring** | Seleciona por `top10_acc` puro; o joint por `indist × (1−ood)`. São estimadores diferentes em épocas diferentes (D4) |
| **Pareamento cruzado é aleatório no treino** | A implementação "limpa" natural é alinhada, e nenhuma conclusão detectaria a troca (S13) |
| **Contagem de parâmetros não vê head count** | `nn.MultiheadAttention` tem os mesmos pesos com 4 ou 8 heads. O tronco do v18 usa 4 |
| **Diagnóstico e `--compile` não convivem** | O probe de gradiente precisa de `retain_graph`; o backward compilado doa buffers e muta in-place |
| **O guard de RAM recusa em máquinas pequenas** | 16 GB de folga fixa para 0,4 GB de dado (R13) |

---

## 8 · Onde está cada coisa

| Preciso de… | Vá para |
|---|---|
| O que o v18 é | `docs/SYSTEM_MAP.md` |
| Como o `mtlcheck` o reconstrói | `docs/ARCHITECTURE.md` |
| Defeitos do código antigo e o que fiz | `docs/REFERENCE_DEFECTS.md` |
| Disposição das revisões | `docs/REVIEW_LEDGER.md` |
| Plano de performance | `docs/OPTIMIZATIONS.md` |
| Guia de telemetria | `docs/TELEMETRY_GUIDE.md` |
| Estado operacional | `studies/porting_validation/STATE.md` |
| Receitas congeladas | `recipes/v18/` |
| A evidência executável | `tests/equivalence/` |
