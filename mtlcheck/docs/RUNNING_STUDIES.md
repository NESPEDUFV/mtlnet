# Como rodar um estudo — e por que a regra é chata

> Se você só quer o comando, vá para o §2. O §1 existe porque **três equipes diferentes já quebraram
> esta regra neste projeto**, incluindo a que escreveu a regra.

---

## 1 · A regra, e as três vezes que ela foi quebrada

**Toda célula cujo número alguém vai citar sai de um manifesto de wave, executado por
`mtlcheck wave run`.** Chamar `mtlcheck train` direto é para depuração descartável, e o resultado vai
para um estudo chamado `scratch*`.

Não é burocracia. É o registro de três falhas com a mesma forma:

| quando | o quê | custo |
|---|---|---|
| repo de referência | a matriz vivia em 30+ drivers de shell; um deles fazia `export MTL_DISABLE_AMP=1` dentro de uma função e o export vazava para a célula seguinte | 8 células de categoria rodaram em fp16 com os sidecars dizendo fp32; uma comparação entre sementes ficou inválida por meses |
| repo de referência | um estudo guardava a própria cópia do laço de validação (~280 linhas) | a cópia ficou 2 meses atrás das correções do `src/` e servia um caminho de pontuação em CPU — ~39 % do wall-clock de uma célula |
| **este repo, 2026-08-19** | a campanha de medição inteira rodou de scripts ad-hoc **fora do repo**, em `/dados/.../*.sh` | 46 estudos bancados contra 9 manifestos. Os números existem, o código está no git, e a **matriz** não existe em lugar nenhum reproduzível |

A terceira é a mais instrutiva, porque o `tests/test_studies_contract.py` **não pegou**: ele proíbe
ciência executável *dentro* de `studies/`, e os drivers estavam fora do repo — o que é pior, não
melhor. E o próprio docstring da `wave` já dizia o que ia acontecer: *"com nenhum executor, todo
substrato veio de um script ad-hoc, que é como o `repr_seed` ficou decorativo por três rodadas de
validação"*.

---

## Antes de soltar uma campanha: `--preflight`

Três coisas eram checáveis separadamente e ninguém as rodava juntas. Agora são uma invocação, e ela
custa o piso da escada — minutos no conjunto mais barato:

```bash
mtlcheck wave run studies/<estudo>/waves/<manifesto>.toml --preflight
```

Ele roda **só o piso** e para, reportando:

* a identidade do substrato conferida contra o que o manifesto declara (fail-closed);
* o **piso de ruído do estimador** contra o limiar de cada degrau — ou seja, se algum degrau é
  alcançável com a dispersão que esta configuração consegue medir;
* o comando do ensaio de leitura, para você rodar em seguida.

⚠ **Por que isto existe.** Em 2026-08-25 dois conjuntos subiram ao teto da escada e o motivo só
apareceu depois de duas horas de GPU: a dispersão é medida na validação interna, que são 10 % dos
usuários, e o ruído de amostragem desse estimador (~0,184 pp) sozinho já excedia o limiar dos degraus
P=2, P=3 e P=4 (0,011 / 0,076 / 0,146). **O desfecho estava decidido por aritmética antes da primeira
execução terminar.** Era computável em quatro minutos.

Se o preflight imprimir `⚠ O RUÍDO DO MEDIDOR JÁ DECIDE O DESFECHO`, pare e trate — as horas
seguintes comprariam execuções contra o ruído do próprio medidor, não contra a dispersão que
interessa.

**E rode o ensaio da leitura depois**, sempre, contra as células que o piso acabou de produzir:

```bash
mtlcheck compare <runs>/<estudo> --analysis <receita> --state <conjunto> --dry-run
```

`--dry-run` não gasta leitura — conferido no código: ele retorna antes de qualquer escrita no livro.
Foi assim que se descobriu, em 25-08, que o caminho de leitura estava **bloqueado** sob a escada por
uma guarda que recebia o estimando num sítio de chamada e não no outro. Sem o ensaio contra células
reais, isso apareceria depois das ~30 h da campanha inteira.


## 2 · O caminho, do zero a um número citável

```bash
# ── 0 · variáveis de ambiente. As três decidem ONDE, nunca O QUÊ.
export DATA_ROOT=.../data            # dados primários (fonte única, por symlink)
export ARTIFACTS_ROOT=.../artifacts  # substratos
export RUNS_ROOT=.../runs            # células

# ── 1 · o substrato. AINDA É UM PASSO MANUAL — ver §4.
mtlcheck check2hgi build  --recipe recipes/v19/substrate.toml --state alabama --shapefile <tract.shp>
mtlcheck check2hgi verify --recipe recipes/v19/substrate.toml --state alabama

# ── 2 · o manifesto. Isto é o experimento; o resto é execução.
$EDITOR studies/<estudo>/waves/<x>.toml
mtlcheck wave plan studies/<estudo>/waves/<x>.toml      # o que rodaria, sem rodar

# ── 3 · executar, com resume honesto
mtlcheck wave run    studies/<estudo>/waves/<x>.toml
mtlcheck wave status studies/<estudo>/waves/<x>.toml

# ── 4 · pontuar (validação interna) e, só no fim, comparar (teste externo)
mtlcheck score   runs/<estudo> --compare cat joint:cat --state alabama
mtlcheck compare runs/<estudo> --arm-a cat --arm-b joint --task cat --state alabama
```

### O que o `wave run` garante, e o que não garante

**Garante:** um processo por célula, sem estado de shell viajando entre elas; a matriz expandida em
código de biblioteca e não num laço de shell; e um resume que **só pula** uma célula quando o
`result.json` dela parseia, o `science_fingerprint` bate, o **substrato é o mesmo** e — se a célula
grava predições — as linhas existem.

**Não garante:** que o substrato exista, esteja correto, ou seja o que você pensa. Ver §4.

---

## 2.1 · As predições do teste são guardadas SEMPRE — o escore é que é racionado

Confusão comum, e ela custou uma campanha inteira de retreino em 19-08.

Logo que um fold termina de treinar, com a época **já fixada no inner-val**, o runner pontua o fold
externo e grava as **predições linha a linha** em `predictions.parquet`. Isso é automático e não é
"ler o teste": o que fica em disco são linhas, não um número.

O ato racionado é o `mtlcheck compare`, que transforma linhas em métrica. É ele que gasta a leitura,
porque é ele que produz algo que influencia decisão.

```
treino do fold  →  época escolhida no inner-val  →  predições do fold externo em disco
                                                      (automático, custo: 1 passada)
                                                                    ↓
                                          mtlcheck compare  ←  O ATO RACIONADO
```

**Guardar custa uma passada de validação por fold e ~700 KB por célula. NÃO guardar custa retreinar
a execução inteira.** Por isso, desde 19-08, `train` liga `--save-predictions` por padrão sempre que
há `--split-seed`; sem ele, desliga com aviso.

⚠ **Numa wave o campo continua sendo explícito**, e o default do manifesto **não** foi invertido:
o resume re-executa uma célula que declara predições e não as tem, então mexer no default
invalidaria toda célula bancada cujo manifesto omite o campo — as seladas inclusive. Manifesto novo
escreve `save_predictions = true`.

---

## 3 · O que um número citável precisa ter

Antes de colocar um número num documento, confira os cinco:

1. **Manifesto commitado** que descreve a célula. Teste: `mtlcheck wave status <manifesto>` reconhece
   a célula bancada como válida. Um manifesto escrito depois que não reproduz os fingerprints
   bancados descreve *outro experimento*.
2. **`substrate` no `result.json`**, com a identidade por nível. Ausente significa "bancada antes de
   2026-08-19" — o número vale, mas ninguém consegue dizer sobre qual substrato.
3. **`eval_stream` compatível** com aquilo contra o que você o está comparando. `outer_fold` e
   `inner_val` não se subtraem — ver [`EVALUATION_METHOD_GUIDE.md`](EVALUATION_METHOD_GUIDE.md) §8.
4. **A leitura certa.** Um número de `inner_val` é leitura de desenvolvimento e **não é resultado**.
   O resultado sai do teste externo, uma vez, pelo `mtlcheck compare`.
5. **O Δ acima do piso de ruído.** Execuções compiladas variam 0,02–0,05 pp entre sessões; sorteios
   de substrato variam ~0,03 pp a jusante. Nada abaixo disso é interpretável.

---

## 4 · A lacuna que ainda existe: a wave não constrói substrato

`grep -c "check2hgi\|substrate_dir" src/mtlcheck/train/wave.py` → **0**. Uma wave é uma matriz de
células de TREINO. A construção do substrato é um passo de CLI separado, executado à mão.

Consequência prática: **a metade "construir" de toda campanha é ad-hoc por construção.** Quando um
experimento varia o substrato — sementes de representação, uma correção no POI2Vec, um grafo
diferente — a wave não consegue expressá-lo, porque a identidade do substrato não é campo de célula.

O que existe hoje para conter o dano, em três camadas:

1. a célula **registra** qual substrato leu (`substrate/identity.py` → `result.json["substrate"]`);
2. o **resume invalida** uma célula cujo substrato mudou desde que ela foi bancada;
3. o manifesto pode **declarar** o substrato que suas células exigem, e a wave **recusa rodar**
   sobre outro:

```toml
[substrate]
recipe = "recipes/v19/substrate.toml"     # informativo: como reconstruí-lo
[substrate.identity]
checkin = "696ac00419d287d3"
```

A recusa aborta a wave inteira, não célula a célula: se o disco tem o substrato errado, TODA célula
da matriz está errada, e parar na primeira é a única leitura útil. Omitir o bloco mantém o
comportamento antigo.

As três camadas cobrem os três momentos: (3) antes de rodar, (1) no que fica gravado, (2) ao
retomar. O que **continua em aberto** é a wave CONSTRUIR o substrato — hoje ela só confere o que já
existe.

---

## 5 · Estado atual, 2026-08-19

**Substrato:** um por estado, `recipes/v19/` (forward-only, tempo contínuo). A torre de região lê o
mesmo substrato que a de check-in; o substrato bidirecional separado (v14) foi arquivado em
`576f7b85`. As receitas `v18/` continuam no repo porque células bancadas as citam e receitas são
imutáveis uma vez citadas — **não** são uma alternativa viva.

**Estados:** AL / AZ / IST são de desenvolvimento e já tiveram o teste externo lido (2026-08-18). CA
e TX **também são desenvolvimento** — a nota da tabela da dissertação diz que o batch size foi
buscado *at every dataset*, e no protocolo antigo a busca tocou o fold reportado. Contaminação
menor que a de AL/AZ/IST, não ausente. **Reserva de verdade só existe fora dos seis datasets.**

**Estudos bancados:** 46. A campanha de 19-08 (10) foi retrofitada e verificada contra o banco; os
anteriores estão triados em
[`studies/porting_validation/STUDY_LEDGER.md`](../studies/porting_validation/STUDY_LEDGER.md) em três
baldes — rastreáveis, documentados-mas-não-reverificáveis, e descartáveis. **Todo número citado em
documento hoje sai de um estudo com manifesto**; o que não é rastreável também não é citado.

**A frase que NÃO é verdadeira:** "o substrato é causal". O filtro forward-only fecha o canal de
vazamento **linha a linha**, que vale 28,63 pp de macro-F1. O substrato continua treinado uma vez
sobre o corpus inteiro, **sem a partição em folds**, então toda linha do teste externo esteve no treino do
pretexto; o `Checkin2POI` agrupa visitas futuras e o alvo MAE é a distribuição de categorias do
corpus inteiro. Tudo isso era transdutivo em toda célula da dissertação também.

---

## 6 · Três categorias que se confundem com facilidade

Quando um número muda, ele mudou por qual destes?

| categoria | o que significa | exemplo |
|---|---|---|
| **correção de migração** | o porte estava errado, a referência certa | as três divergências do POI2Vec (+0,86 pp). **Não é ganho sobre a dissertação** — é um buraco nosso fechando |
| **defeito reproduzido** | a referência está errada e mantemos, porque foi o que produziu os artefatos bancados | o descasamento de unidades do Delaunay, que inverte a penalidade de cruzar região em bônus para 98,56 % das arestas |
| **melhoria real** | corrigimos um defeito da referência | o POI2Vec passou a ser semeado (a referência não tem semente e não reproduz nem a si mesma) |

Confundir a primeira com a terceira faz alguém ler "+0,86 pp" e concluir que superamos a
dissertação. Não superamos: chegamos à paridade.

---

## 7 · Rodar a suíte — os DOIS ambientes, e por quê

⚠ **Escrito em 2026-08-19 depois de uma auditoria constrangedora.** A sessão inteira validou com
`--ignore=tests/equivalence` e com o venv do repo ANTIGO, e nesse arranjo a suíte parecia verde
enquanto o ambiente do próprio projeto tinha **8 falhas**.

```bash
# o ambiente DO PROJETO — o que `uv sync` produz. É este que decide.
PYTHONPATH=src .venv/bin/python -m pytest tests/ -q
#   → 392 passed, 25 skipped

# o ambiente COM A REFERÊNCIA — necessário para os testes de equivalência
PYTHONPATH=src <venv-com-o-repo-antigo>/bin/python -m pytest tests/ -q
#   → 415 passed, 2 skipped
```

**Os 23 skips do primeiro são corretos, não dívida.** São os testes que importam a implementação de
referência e precisam das dependências dela (`cvxpy`, `pytorch_warmup`). O venv do projeto não as tem
e não deve ter — a suíte de equivalência é bi-ambiente por natureza.

**Nunca rode com `--ignore=tests/equivalence`** para declarar verde. Foi assim que três defeitos
ficaram escondidos por um dia:

| o que estava quebrado | por que passou despercebido |
|---|---|
| `np.issubdtype` sobre `StringDtype` travava o build de substrato no pandas 3 | o venv antigo tem pandas 2, onde a coluna vem como `object` |
| a fixture tinha 4 usuários para uma partição de 5 folds | o sklearn 1.8 aceitava em silêncio; o 1.9 recusa, e está certo |
| a guarda de dtype do `userid` checava o backend em vez da propriedade | idem |

**E a divergência de ambiente continua declarada, não resolvida:** o `pyproject.toml` pede
`pandas>=2.2` e o `uv.lock` entrega `3.0.5`. Os dois funcionam hoje; a intenção não está escrita.
