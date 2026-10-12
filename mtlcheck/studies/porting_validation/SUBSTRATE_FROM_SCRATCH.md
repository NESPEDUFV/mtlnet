# O substrato construído do zero — o que ele custa

**2026-08-19.** Primeira medição do substrato que o mtlcheck constrói contra o bancado.

## 1 · O cosseno é o instrumento errado, e por quê

A primeira comparação foi por similaridade de cosseno contra o substrato bancado:

| | cosseno médio | piso do R16 (mesma seed) | R16 entre seeds |
|---|---:|---:|---:|
| janelas de check-in (v18) | 0,043 | 0,9945 | 0,089 |
| embeddings de região (v14) | 0,301 | 0,9886 | — |

Parece catastrófico e não é. O R16 mede que a referência, rodada **duas vezes com a mesma seed**,
chega a cos 0,9945; e que **entre duas seeds** cai para 0,089. Os nossos números estão no segundo
regime, não no primeiro.

Isso é o esperado. `repr_seed = 42` só coloca duas execuções na mesma bacia se elas consumirem o RNG
**na mesma ordem**, e uma reescrita independente não consome — o mesmo motivo pelo qual as épocas
escolhidas já divergiam no lado do treino. O cosseno responde "é o mesmo sorteio?", e a pergunta que
interessa é "o substrato serve igual?".

⚠ Erro cometido no caminho, registrado para não se repetir: a primeira rodada comparou o
`region_embeddings.parquet` que o build **v18** escreve contra o do **v14**. São o mesmo modelo em
grafos diferentes (`forward_only` e `continuous_time` são os únicos campos que separam as duas
receitas), então o resultado era interpretável como divergência quando era só o par errado.

## 2 · A medição que responde: desempenho a jusante

Mesmo protocolo aninhado, mesma partição (`split_seed 0`), mesma semente de modelo (`seed 0`), mesma
receita. **Só o substrato muda.** `al_full` construiu o seu; `sealed_bridge` leu o bancado.

| | do zero | bancado | Δ pareado | erro-padrão | por fold |
|---|---:|---:|---:|---:|---|
| **cat** | 30,0870 | 30,0693 | **+0,018** | 0,219 | +0,54 +0,24 +0,02 +0,07 −0,78 |
| **reg** | 73,7165 | 74,6435 | **−0,927** | 0,151 | −1,02 −0,76 −1,31 −1,11 −0,44 |

**Categoria passa.** +0,018 contra erro-padrão 0,219, e dentro dos ~0,18 pp que o R16 atribui a uma
reconstrução.

**Região não passa.** −0,927 é seis erros-padrão e os **cinco folds são negativos**. Não é ruído de
fold.

## 3 · O que ainda NÃO está separado

**n = 1 substrato.** Os cinco folds compartilham o mesmo substrato, então a consistência de sinal
entre folds não distingue:

* **(A) o sorteio saiu pior** — a nossa construção com `repr_seed 42` caiu numa bacia ruim, e outra
  semente cairia acima do bancado;
* **(B) o construtor é pior** — algo no caminho do v14 sistematicamente entrega menos.

Só (B) é um defeito. **Resolvido em 19-08: é (B).** Ver §6.

## 4 · O suspeito, se for (B)

O substrato de região consome POI2Vec e o grafo Delaunay, e o POI2Vec carrega três divergências
conhecidas, documentadas no seu módulo e **nunca corrigidas**:

* negativos amostrados uniformemente, onde a referência amostra pela hierarquia;
* o regularizador de hierarquia ausente;
* o objetivo ponderado por janela em vez de por par.

Mais a DIVERGÊNCIA 0 do Delaunay: 2,3 % das arestas saem com orientação trocada, o que importa
porque o POI2Vec caminha o grafo **dirigido**.

Adiar essas correções foi decidido com o argumento de que "a validação lê o substrato bancado, então
as divergências não a afetam". **Esse argumento caiu**: a validação agora constrói o substrato, e é
exatamente onde o déficit aparece.


## 5 · A unificação (v19) e o SHA de arquivamento

**2026-08-19.** O substrato de região separado deixou de existir. Check2HGI é hierárquico sobre
quatro níveis, então uma execução já emite os embeddings de região; ter um segundo substrato, vindo
de outro grafo e bidirecional, era herança da referência e não desenho.

### O triângulo que autorizou a troca

Medido ANTES de deletar qualquer coisa — mesma partição (`split_seed 0`), mesma semente de modelo,
protocolo aninhado, Alabama:

| | Acc@10 | por fold |
|---|---:|---|
| v14 bancado (referência) | 74,6435 | 73,38 71,96 77,19 77,24 73,44 |
| v14 do zero | 73,7165 | 72,36 71,20 75,88 76,13 73,00 |
| v18-região do zero | 73,8385 | 72,78 71,27 75,87 76,45 72,83 |

| efeito | Δ | erro-padrão |
|---|---:|---:|
| **grafo** (v18-região contra v14, mesmo construtor) | **+0,122** | 0,108 |
| **construtor** (nosso v14 contra o da referência) | **−0,927** | 0,151 |

Trocar o grafo é de graça. O déficit inteiro é do construtor, e sobrevive à unificação — o
`_scaffolding` (POI2Vec + Delaunay) alimenta o build v18 do mesmo jeito.

### O que foi arquivado, e onde encontrá-lo

`recipes/v14/region.toml`, `export.write_region` e `tests/test_region_substrate.py` existiram pela
última vez em **`576f7b85`**. Recuperáveis com `git show 576f7b85:<caminho>`.

Não foram deletados por desprezo: todo número de `reg` e `joint` da dissertação está apoiado em
embeddings v14, e a avaliação contra ela precisa poder **atribuir** diferenças. O que sai é a
possibilidade de uma receita pedir a versão vazada; o parâmetro `forward_only` de `graph.build`
continua existindo e testado.

### A frase que NÃO passa a ser verdadeira

"O substrato é causal." O forward-only fecha o canal de vazamento **linha a linha** — o que vale os
28,63 pp. O substrato continua treinado uma vez sobre o corpus inteiro, **sem split de fold**, então
toda linha do teste externo esteve no treino do pretexto; o `Checkin2POI` agrupa visitas futuras, o
alvo MAE é a distribuição de categorias do corpus inteiro e a normalização min-max do peso de aresta
é ajustada no corpus inteiro. Tudo isso é transdutivo, era transdutivo em toda célula da
dissertação, e só deixaria de ser com substrato por fold — outro protocolo e outra conta de compute.


## 6 · O veredito: é o construtor, não o sorteio

Quatro sorteios do substrato (`repr_seed ∈ {42, 0, 1, 7}`), `reg` treinado em cada, mesma partição e
mesma semente de modelo, contra o incumbente (v14 bancado da referência, 74,6435):

| repr_seed | Acc@10 | Δ contra o incumbente |
|---:|---:|---:|
| 42 | 73,8385 | −0,805 |
| 0 | 73,9150 | −0,729 |
| 1 | 73,8549 | −0,789 |
| 7 | 73,8506 | −0,793 |

**Desvio entre sorteios: 0,034 pp.** A distância ao incumbente é 0,78 — vinte vezes toda a dispersão
dos sorteios — e os quatro estão abaixo. A hipótese (A) está morta.

Duas rotas independentes concordam: v14-contra-v14 mediu **−0,927**, e v18-região-contra-v14 mede
**−0,78** com o efeito de grafo em +0,12 (−0,78 − 0,12 ≈ −0,90).

### Descartada a armadilha do nulo

Um desvio de 0,034 seria trivial se o `--seed` não tivesse surtido efeito. Não é o caso: os quatro
substratos têm hashes distintos, cosseno **0,36–0,49** entre si, e norma média variando de 9,08 a
11,92.

### O achado colateral

A representação varia enormemente entre sementes — cosseno ~0,4, normas ±30 % — e o desempenho a
jusante move **0,03 pp**. A cabeça é praticamente invariante à base e à escala da representação, o
que é por si a razão de o cosseno nunca poder responder "o substrato serve igual?".

## 7 · O que fazer com isso

O déficit é sistemático e vale ~0,9 pp em Acc@10 de região. Os suspeitos estão nomeados e são todos
do `_scaffolding`, que alimenta o substrato unificado exatamente como alimentava o v14:

| suspeito | onde | estado |
|---|---|---|
| negativos amostrados uniformemente (a referência amostra pela hierarquia) | `substrate/poi2vec.py` | divergência conhecida, não corrigida |
| regularizador de hierarquia ausente | `substrate/poi2vec.py` | divergência conhecida, não corrigida |
| objetivo ponderado por janela em vez de por par | `substrate/poi2vec.py` | divergência conhecida, não corrigida |
| 2,3 % das arestas com orientação trocada | `substrate/delaunay.py` | DIVERGÊNCIA 0, e importa porque o POI2Vec caminha o grafo **dirigido** |

Adiar essas correções foi decidido com o argumento de que "a validação lê o substrato bancado". Esse
argumento morreu duas vezes: a validação passou a construir o substrato, e agora existe um déficit
medido, sistemático e localizado exatamente onde essas divergências vivem.

## 8 · As divergências do POI2Vec ERAM o déficit — e ele fechou

**2026-08-19.** As três divergências corrigidas uma de cada vez, cada uma medida em Alabama contra o
incumbente (v14 bancado da referência, 74,6435), com o piso de ruído entre sorteios em 0,034 pp.

| estado do POI2Vec | Acc@10 | contra o incumbente |
|---|---:|---:|
| antes das correções | 73,8385 | −0,805 |
| + divergência 3 (ponderação do objetivo) | 73,8504 | −0,793 |
| + divergências 1 e 2 (negativos duros ⊕ regularizador) | **74,6952** | **+0,052** |

**O déficit de −0,9 pp era o POI2Vec.** Corrigido, a região sai de 0,8 pp abaixo da referência e chega
à paridade: os +0,052 estão praticamente no piso de ruído.

### O que cada uma valeu

| divergência | Acc@10 | ganho |
|---|---:|---:|
| — (antes) | 73,8385 | — |
| 3 · ponderação do objetivo | 73,8504 | **+0,012** |
| 1 · negativos duros | 74,4132 | **+0,563** |
| 2 · regularizador de hierarquia | 74,6952 | **+0,282** |

* **Divergência 3: +0,012 pp** — abaixo do piso de ruído de 0,034, sem efeito mensurável. Trocar
  "pares com média 1:1" por "janelas somando 4 positivos contra 20 negativos" é uma mudança
  substancial no objetivo e move a região em nada.
* **Divergência 1: +0,563 pp** — o maior peso isolado. Restringir os negativos aos fclasses que
  nunca co-ocorrem é o que mais importa.
* **Divergência 2: +0,282 pp** — e vale notar que é um termo com λ = 1e-8, nove ordens de grandeza
  abaixo da loss principal. Ele não é inerte porque o Adam é livre de escala no gradiente, o que a
  docstring do módulo já afirmava sem prova; agora há uma.

### O que foi corrigido

1. **Negativos duros.** Por fclass central, a lista dos fclasses que NUNCA co-ocorrem com ele nas
   janelas — sem reposição dentro da janela, com fallback para "todos menos o centro" quando esvazia.
   Antes: uniforme sobre o vocabulário inteiro, incluindo o próprio centro e os contextos
   verdadeiros. Em Alabama a restrição deixa **mediana 195 de 284** fclasses como candidatos.
   `random.sample` sobre listas e não `Generator.choice`: é a ferramenta da referência, e
   `choice(replace=False)` permuta o pool inteiro a cada uma das ~35 milhões de chamadas por build.
2. **Regularizador de hierarquia.** `½·λ·Σ‖in[cat] − in[fclass]‖²` sobre os 284 pares únicos
   (categoria, fclass). Antes: `λ·Σ emb²`, um puxão global para zero — outro termo com o mesmo λ e
   gradiente completamente diferente. ⚠ Indexar a tabela de **fclass** com código de **categoria** é
   defeito da referência e foi **reproduzido**; só é inofensivo porque há 7 categorias contra 284
   fclasses. Onde a referência estouraria com `IndexError` opaco, agora há erro explícito.
3. **Ponderação do objetivo.** Janelas em vez de pares, `sum` na linha e `mean` no lote.

Testes novos verificados por mutação: trocar o amostrador de volta para uniforme quebra dois deles, e
o teste do regularizador passa um par idêntico junto de uma linha de norma enorme — o termo antigo
daria valor positivo, o novo dá exatamente zero.

### O que isso muda no quadro anterior

O §6 concluiu "é o construtor, não o sorteio", e estava certo. O §7 nomeou os suspeitos, e estava
certo. O que **não** se sustentou foi a expectativa implícita de que a divergência mais estrutural (a
ponderação do objetivo) fosse a que mais pesava: ela não vale nada, e o peso está inteiro na
distribuição dos negativos e no termo de regularização.

### DIVERGÊNCIA 0 do Delaunay — fechada, e verificável

A ordem de varredura decide a orientação de cada aresta. A referência percorre
`for simplex in triangles: for x, y in combinations(simplex, 2)` — as três arestas do simplex 0,
depois as do simplex 1. Esta implementação concatenava blocos de COLUNA (todas as (0,1), depois todas
as (0,2)), o que dá o mesmo conjunto não dirigido e a mesma proporção de orientações, mas troca a
orientação de arestas individuais. Importa porque o `poi2vec` caminha o grafo **dirigido**.

Corrigido para varredura por linha. Verificado contra o `edges.csv` bancado do HGI em Alabama:

| | |
|---|---|
| places | 11 848, `pois.csv` idêntico |
| arestas | 35 519, conjunto e **ordem** idênticos |
| orientação por aresta | **idêntica — 0 invertidas de 35 519** |
| `\|Δ peso\|` máximo | 1,1e-16 |

Isto é a primeira parte do substrato que reproduz o artefato bancado **bit a bit**, em vez de
reproduzir dentro do ruído.

## 9 · A dispersão do Arizona é do protocolo, não do porte

**2026-08-19.** Levantado pelo autor: a categoria de Arizona saiu com desvio entre folds de **2,26**
contra **0,66** em Alabama, num estado com o dobro de usuários. Investigado por eliminação.

### O que NÃO era

* **Taxa de aprendizado.** AZ usa `max_lr = 0,0005` contra 0,0025 em AL, o que explica as épocas
  tardias (28–45 contra 16–26). Mas **Istambul usa o mesmo 0,0005**, escolhe épocas ainda mais
  tardias (38–47) e tem o **menor** desvio dos três (0,50).
* **A partição.** Folds disjuntos por usuário, 421–430 usuários cada, e a estratificação na categoria
  deixa a mistura de classes praticamente idêntica entre folds (a classe mais rara fica em 4,69 % em
  todos os cinco).
* **Ruído de execução.** Duas execuções independentes reproduzem os mesmos folds:
  `sealed_bridge` deu 32,01/31,68/33,98/32,81/37,36 e `final_az` deu 31,97/31,66/34,03/32,69/37,22.

### O que era

O **protocolo aninhado**. Rodando a mesma categoria no protocolo PLANO da referência, sobre o nosso
substrato:

| | referência | mtlcheck (plano) | mtlcheck (aninhado) |
|---|---|---|---|
| AL | 30,71 ± **1,233** | 30,74 ± **1,277** | 30,08 ± **0,656** |
| AZ | 34,50 ± **1,124** | 34,56 ± **1,177** | 33,51 ± **2,262** |

Fold a fold quase coincide — AZ: 34,40/34,35 · 35,47/35,55 · 33,27/33,19 · 33,55/33,73 · 35,80/35,96.

A validação interna **infla** a dispersão de AZ (1,18 → 2,26) e **desinfla** a de AL (1,28 → 0,66).
Direções opostas, então não é tamanho de amostra — é composição: qual usuário cai no conjunto
interno, que é recortado do bloco de treino de cada fold por um SGKF de 8 vias com semente própria.

### O resultado colateral, que vale mais que o diagnóstico

**A categoria reproduz a referência em dois estados**, média e dispersão dentro do ruído: Δ +0,03 pp
em AL e +0,06 pp em AZ. Somado ao Δ +0,054 de região, o porte tem agora duas famílias reproduzindo
sob protocolo pareado — antes havia só a `cat` de Alabama, medida em 13-08.

### A consequência prática

Dispersão entre folds de leitura interna **não é comparável entre estados**, e muito menos com o ±
da dissertação, que é entre sementes. Já era proibido citar número de inner-val; este é mais um
motivo.
