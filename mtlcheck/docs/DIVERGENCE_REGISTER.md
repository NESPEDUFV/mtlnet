# Registro de divergências — três categorias que se confundem, e o preço de confundi-las

> Existe porque a pergunta "essa leva de correções foi melhoria ou correção?" foi feita e a resposta
> não era óbvia nem para quem tinha feito o trabalho.

Quando um número muda entre o mtlcheck e a dissertação, ele mudou por **um** destes três motivos. Eles
têm implicações opostas e são fáceis de trocar.

| | quem estava errado | o que o número significa |
|---|---|---|
| **correção de migração** | **nós** | fechamos um buraco nosso. **Não é ganho sobre a dissertação** |
| **defeito reproduzido** | a referência, e mantemos | o número é comparável com a dissertação porque carrega o mesmo defeito |
| **melhoria real** | a referência, e corrigimos | o número **não** é mais comparável sem declarar a mudança |

**O erro concreto que isto impede:** as três divergências do POI2Vec valeram **+0,86 pp** em região.
Lido sem categoria, isso parece "superamos a dissertação em quase um ponto". É o oposto: era um bug
nosso, e o resultado é **paridade** — 74,70 contra 74,64 do incumbente.

---

## 1 · Correções de migração — nós estávamos errados

Nenhuma delas melhora nada em relação à referência. Todas fecham buracos abertos no porte.

| o quê | onde | efeito |
|---|---|---|
| POI2Vec: negativos uniformes em vez de amostrados por co-ocorrência | `substrate/poi2vec.py` | **+0,563 pp** região |
| POI2Vec: regularizador global para zero em vez do de hierarquia sobre pares | `substrate/poi2vec.py` | **+0,282 pp** região |
| POI2Vec: objetivo por par (1:1) em vez de por janela (4 positivos, 20 negativos) | `substrate/poi2vec.py` | +0,012 pp — ruído |
| Delaunay: varredura por bloco de coluna em vez de por linha de simplex | `substrate/delaunay.py` | orientação de 2,3 % das arestas; agora **bit-exato** |
| `fclass` caindo para `category` (7 símbolos onde a referência tem 284) | `substrate/delaunay.py` | code book inteiramente diferente |
| `torch_cluster.random_walk` ignora `torch.manual_seed` | `substrate/poi2vec.py` | reprodutibilidade que não existia |
| checkpoints inutilizáveis pelo prefixo `_orig_mod` do `torch.compile` | `train/checkpoints.py` | os arquivos não carregavam |
| `verify` reprovando substratos de região com 6 problemas espúrios | `cli.py` | falso negativo |
| chave de região fixa em `GEOID` (TIGER); as mahalles do OSM trazem `@id` | `substrate/regions.py` | **Istambul não construía** — ver abaixo |

### Istambul: por que este caminho nunca rodou, nem lá nem aqui

Vale detalhar porque a forma do erro se repete. O `regions.py` exigia `GEOID`, que é do census tract
americano. Os cinco estados dos EUA passavam; **Istambul falhava na primeira feição**.

O que escondeu por tanto tempo: a **referência não faz este join para Istambul**. Ela pré-posiciona um
CSV (`output/check2hgi/istanbul/temp/boroughs_area.csv`) que **renomeia `@id` para `GEOID`**
— `pipelines/embedding/hgi.pipe.py:88-91`. Ou seja, o caminho de join do OSM nunca foi exercitado em
nenhum dos dois lados: lá porque era contornado por preprocessamento, aqui porque só rodávamos
estados dos EUA.

Escolher `@id` **reproduz a referência exatamente** — o CSV dela traz `relation/1275322`.

A guarda que ficou importa mais que o fallback: `name` também está no arquivo e é a escolha
"natural", mas tem **774 valores únicos para 964 feições**. Usá-la colapsaria 190 mahalles distintas
em silêncio, e o sintoma apareceria muito depois, como uma contagem de regiões diferente. `build`
agora **recusa** qualquer chave que não identifique as feições unicamente, com as contagens no erro.

---

## 2 · Defeitos reproduzidos — a referência está errada e mantemos

Mantidos porque **foi isso que produziu todo artefato bancado**. Corrigir tornaria todo número da
dissertação irreproduzível — o que é uma decisão legítima, mas é uma decisão, e tem que ser declarada.

| o quê | por que dói | estado |
|---|---|---|
| Delaunay: `D` em graus contra `dist` em metros → log negativo em 98,56 % das arestas, e a penalidade de cruzar região vira **bônus** | inverte o sinal do mecanismo espacial | `fix_unit_mismatch=True` existe, desligado |
| `mae_poi_target_dim = 8`: a coluna 7 do alvo é a média de `hour_sin`, não uma categoria | cosseno 0,8785 contra o alvo pretendido | **veredito: corrigir**, na leva de melhorias |
| regularizador de hierarquia indexa a tabela de **fclass** com código de **categoria** | só é inofensivo porque há 7 categorias contra 284 fclasses | reproduzido, com erro explícito onde a referência estoura opaco |
| POI2Vec caminha o grafo **dirigido** | não é o node2vec padrão | `symmetrise=True` existe, desligado |
| `le_lambda = 1e-8` não é inerte | o Adam é livre de escala no gradiente — e isso **foi medido**: vale +0,282 pp | reproduzido |

---

## 3 · Melhorias reais — corrigimos um defeito da referência

Poucas, e nenhuma muda o objetivo do modelo.

| o quê | o que a referência fazia |
|---|---|
| POI2Vec **semeado** | não tinha semente nenhuma — não reproduz nem a si mesma |
| lugares fora de todo polígono **contados e logados** | descartados por um inner join, em silêncio |
| um lugar que cruza dois tracts vira **uma** linha | virava duas, com dois vértices de Delaunay independentes |
| erro explícito onde a referência estoura `IndexError` opaco | — |
| **v19: um substrato só** — a torre de região lê o forward-only | lia um substrato bidirecional separado (medido: +0,122 pp, erro-padrão 0,108) |
| o protocolo de avaliação inteiro | teste externo lacrado, seleção no inner-val, TOST, multiplicidade |

---

## 3.1 · A regra vale para o próprio repositório — um caso real

Em 2026-08-20 uma sessão parceira, escrevendo o material de defesa, perguntou de onde vinha a cifra
de otimismo de seleção que este repositório cita. Fui verificar antes de confirmar:

* **cinco** sítios de código diziam *"the measured optimism is ~0.66 pp"*;
* a origem é `studies/porting_validation/waves/sealed_bridge.toml:9` — *"a single Alabama fold
  already **suggests** ~0.66 pp"*.

**Um fold, de um estado, sugestivo.** Os cinco foram corrigidos para "sugerido por UM fold", com a
origem citada. Um sítio (`data/dataset.py`) já dizia "on one Alabama fold" e estava certo desde o
início.

Isto é a mesma classe do que este documento existe para impedir, virada para dentro: **alegação
acima da evidência**. A diferença é que aqui não muda número nenhum — muda o que se pode dizer na
defesa. A hierarquia honesta das três cifras:

| cifra | o que é |
|---:|---|
| **3,66 pp** | **limpo e medido** — mesmo código, mesmo substrato, mesma partição; só o protocolo muda |
| ~1 pp | ordem de grandeza — mistura protocolo E convenção de agregação (§8) |
| ~0,66 pp | **sugestivo** — um fold de Alabama |

E o que fecha: o instrumento da medição própria **existe e nunca rodou**. É o §8a
(`src/mtlcheck/eval/optimism.py`, dez testes), que decompõe em a1 − b1 e b1 − b2 co-registrados na
mesma trajetória, e exige `retain_checkpoints != "none"` — o default é `"none"`. Primeiro item de
`studies/improvements/PLAN.md`.

---

## 4 · A regra prática

Antes de escrever "melhoramos X pp", pergunte de qual coluna o X saiu.

Se saiu da **primeira**, a frase certa é "o porte agora reproduz a referência". Se saiu da
**terceira**, a frase certa nomeia a mudança e diz que o número deixou de ser comparável sem ela.
