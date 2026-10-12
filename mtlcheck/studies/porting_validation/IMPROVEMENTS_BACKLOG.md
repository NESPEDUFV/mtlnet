# Melhorias achadas durante a migração — medidas, decididas, **não** executadas

**Criado 2026-08-19.** Durante o porte apareceram coisas que são melhorias reais sobre a referência,
não correções de migração. Elas foram deliberadamente **não** executadas, por uma razão simples: cada
uma que entra sozinha exige uma receita nova (receitas são imutáveis uma vez citadas), e uma cadeia
de v20/v21/v22 destrói a consistência que a v19 acabou de criar.

**Elas entram juntas, numa única versão de receita, quando a fase de melhorias começar.**

> Como ler as colunas: veja o registro de três categorias em
> [`../../docs/DIVERGENCE_REGISTER.md`](../../docs/DIVERGENCE_REGISTER.md). Nada aqui é correção de
> migração — aquelas já foram feitas e estão em paridade.

---

## 1 · `mae_poi_target_dim` — corrigir de 8 para 7

**Veredito 2026-08-19: CORRIGIR.**

O alvo de reconstrução do lugar mascarado fatia `len(CATEGORIES_MAP)` = 8 colunas da matriz de
features. Há sete categorias reais mais um sentinela `None` que nenhum corpus usa, e a matriz é
`7 one-hot + hour_sin + hour_cos + …`. Então a **coluna 7 do alvo é a média de `hour_sin` do lugar**,
não uma categoria.

Não é arredondamento: o cosseno entre o alvo de 8 e o pretendido de 7 é 0,8785 em média (percentil 5
em 0,7193), e a loss é erro de cosseno escalado.

**Medido** (`waves/ablations/mae7.toml`, Alabama, mesma partição, mesma semente, protocolo aninhado;
piso de ruído entre sorteios 0,034 pp):

| | 8 (reproduzido) | 7 (pretendido) | Δ pareado | erro-padrão |
|---|---:|---:|---:|---:|
| categoria | 30,0751 | 30,1909 | **+0,116** | 0,087 |
| região | 74,5119 | 74,4586 | −0,053 | 0,151 |

⚠ **Uma semente.** O erro-padrão é entre folds dentro dela, não entre sementes — que é a grandeza
que a dissertação publica. Um veredito firme exigiria quatro.

**Por que corrigir mesmo com efeito pequeno:** o defeito não tem defesa, o objetivo pretendido é o de
7, e o efeito medido é não-negativo em categoria e nulo em região. O argumento de reproduzir —
"todo substrato bancado carrega" — vale para *comparar* com a dissertação, não para o que se
constrói daqui em diante.

**Custo:** rebuild de substrato em todos os estados.

---

## 2 · Delaunay: o descasamento de unidades que inverte a penalidade de região

**Veredito: PENDENTE — precisa de medição, e é a mais cara de todas.**

O peso da aresta é `log((1 + D**1.5) / (1 + dist**1.5))`, com `D` = diagonal do bounding box em
**graus** (Alabama: 5,887) e `dist` = haversine em **metros** (10³–10⁵). A razão fica muito abaixo de
1 e o log é **negativo em 98,56 % das arestas**. Multiplicar um número negativo pelo desconto de
cruzar região (`w_r = 0,7`) o torna **maior** — ou seja, a penalidade pretendida virou bônus.

`delaunay.build(fix_unit_mismatch=True)` já existe e está desligado.

**Por que ainda não foi medido:** corrigir redefine o grafo inteiro, então muda o POI2Vec, o
substrato e tudo a jusante. É a mudança de maior alcance da lista e merece medição multi-semente.

---

## 3 · POI2Vec: o grafo é caminhado DIRIGIDO

`edges.csv` guarda cada par não-dirigido uma vez e a referência não simetriza antes de caminhar,
então uma caminhada só anda de índice menor para maior. `symmetrise=True` existe e está desligado.

**Medido indiretamente:** a orientação canônica (low→high) elevaria os passos absorvidos de 61,4 %
para 78,9 % e derrubaria os nós distintos por caminhada de 4,47 para 2,87. A lista bancada é 49,7 %
high→low, então o grafo real **não** é um DAG — mas continua dirigido.

**Veredito: PENDENTE.** Simetrizar é o comportamento defensável de um node2vec; o efeito a jusante
não foi medido.

---

## 4 · Substrato por fold — o vazamento que o forward-only **não** cobre

O substrato é treinado **uma vez sobre o corpus inteiro, sem split de fold**. Toda linha do teste
externo esteve no treino do pretexto. Além disso o `Checkin2POI` agrupa visitas futuras, o alvo MAE é
a distribuição de categorias do corpus inteiro, e a normalização min-max do peso de aresta é ajustada
no corpus inteiro.

O forward-only fecha o canal **linha a linha** — que vale os 28,63 pp. Os níveis agregados e o
objetivo do pretexto seguem **transdutivos**, e eram transdutivos em toda célula da dissertação.

**Veredito: FORA DE ESCOPO por ora, e declarado.** Tornar isto causal exige substrato por fold —
outro protocolo, outra conta de compute, e incomparável com tudo que está bancado. O que **não** se
pode fazer é continuar dizendo "o substrato é causal", e isso já foi corrigido nos documentos.

---

## 5 · Retenção de checkpoint para o §8a

O `eval/optimism.py` existe e está testado, mas para rodar precisa de uma execução com
`retain_checkpoints != "none"` — e o default é `none` desde a decisão dos 125,5 GB.

**Veredito: quando a decomposição for necessária.** Ela separa "interferência entre tarefas" de
"custo de entregar um modelo só", que é o que o `SEALED_BRIDGE_READ.md` §2 diz ser necessário para
interpretar o Δ medido. Política sugerida: `selected` sempre, `every` só no estado onde a
decomposição for feita.
