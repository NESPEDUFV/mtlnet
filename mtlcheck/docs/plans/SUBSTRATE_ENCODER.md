# Portar o treino do encoder do substrato

> **Status: EXECUTADO em 2026-08-13**, no mesmo dia em que este plano foi escrito. O modelo, os três
> encoders, os carregadores espaciais e o laço estão portados e validados — evidência em
> [`studies/porting_validation/PLAN.md §4 · Substrato`](../../studies/porting_validation/PLAN.md).
> Falta a materialização dos parquets e a comparação downstream a partir de um substrato próprio.
>
> **Quatro coisas que este plano não previa** e que mudaram o resultado:
>
> 1. **`Check2HGI_DesignK` não existe no v18.** Com `hgi_poi_target=None` — que é o que o builder
>    passa — a subclasse não adiciona nada e `decoder_loss` nunca é chamado. Ela **é** a classe
>    canônica. Uma peça a menos.
> 2. **S17 — o objetivo muda com o tamanho do estado.** O negativo duro da fronteira POI↔região é
>    desligado acima de 50 000 lugares, o que separa AL/AZ/IST de FL/CA/TX sem registro nenhum. Ver
>    `SYSTEM_MAP.md §S17` e `REFERENCE_DEFECTS.md §R15`.
> 3. **R16 — a referência não é reprodutível contra ela mesma.** Duas execuções, mesma seed, mesma
>    máquina, divergem na época 5. Isso reescreveu o §6 abaixo: o passo 4 de validação não podia ser
>    "os embeddings batem", porque nem os da referência batem com os dela.
> 4. **O determinismo custa 12,5 %.** Ligado por padrão no código novo.

## 1 · A receita congelada

Pinada em `scripts/integrity_v2/build_study_repr.py:77-80`, deliberadamente ali "para que uma mudança
de default a montante não faça o estudo derivar":

```
dim=64  num_layers=2  attention_head=4  encoder="resln"  dropout=0.1
alpha_c2p=0.4  alpha_p2r=0.3  alpha_r2c=0.3
mae_poi_lambda=0.3  mae_poi_mask_rate=0.15  mae_poi_gamma=3.0
anchor_lambda=0.1  gamma_init=1.0
lr=1e-3  weight_decay=0.0  max_norm=0.9  lr_gamma=1.0  epochs=500
```

## 2 · O laço de treino é simples; o modelo é que não

```python
for epoch in range(1, 501):
    model.train(); optimizer.zero_grad()
    loss = model.loss(*model(data))        # FULL-BATCH: um forward sobre o grafo inteiro
    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=0.9)
    optimizer.step()
    if loss < lowest:                      # melhor estado = MENOR LOSS DE TREINO
        lowest, best_epoch, best_state = loss, epoch, deepcopy(state_dict)
```

Três coisas a não perder: é **full-batch** (não há minibatch, não há dataloader); o critério de
seleção é a **loss de treino**, não validação — não há conjunto de validação neste estágio; e
`Adam` com `weight_decay=0.0`, não AdamW.

## 3 · O que precisa ser portado

| peça | origem | linhas | observação |
|---|---|---:|---|
| `Check2HGI` (base) | `model/Check2HGIModule.py` | 1 243 | **466 são construtor de variantes opcionais**; o caminho v18 usa uma fração |
| `Check2HGI_DesignK` | `scripts/probe/build_design_k_delaunay.py` | 33 | Subclasse fina — adiciona as arestas de Delaunay no nível POI |
| `ResidualLNEncoder` | `model/variants.py` | 36 | O encoder `resln` |
| `Checkin2POI` | `model/Checkin2POI.py` | 168 | Agregação com atenção check-in → POI |
| `POI2Region` | `embeddings/hgi/model/RegionEncoder.py` | 196 | Vem do **HGI** — a dependência que o §6 do mapa quase mandou apagar |
| `load_delaunay_edges`, `_compute_poi_category_aggregate` | `scripts/probe/build_design_k_delaunay.py` | — | |
| `load_poi2vec_table` | `check2hgi/reg_poi_aug.py` | — | |

Estimativa honesta do caminho ativo: **400 a 550 linhas**, contra as ~1 900 do total das origens. A
diferença é toda variante desligada.

## 4 · A hierarquia e o objetivo

Quatro níveis — check-in → POI → região → cidade — maximizando informação mútua entre eles. Os
negativos vêm de **permutar as linhas** da matriz de features (`corruption`), que é exatamente o
mecanismo por trás do achado de que adicionar identidade de lugar ou região às features **piora**: um
bloco quase único por visita deixa o discriminador responder "real ou embaralhado?" sem usar o grafo.

Termos da loss, com os pesos da receita: infomax nos três níveis (0,4 / 0,3 / 0,3), reconstrução MAE
sobre a distribuição de categorias por POI (λ 0,3, máscara 15 %, γ 3,0, perda `sce`), e o termo
âncora (λ 0,1).

## 5 · Dependências que não são código

- **Arestas de Delaunay** por estado (`reg_poi_mode="delaunay_gcn"`).
- **Tabela POI2Vec** por estado.
- Ambas vêm de artefatos HGI: `output/hgi/<state>/temp/{pois,edges}.csv`.

Ou seja: portar o encoder **não basta** para reconstruir do zero — o HGI é pré-requisito. Isso já
está registrado em `ARCHITECTURE.md §1.1`, e é o que impede o "rebuild dos 6 estados" de ser só uma
questão de rodar o novo builder.

## 6 · Como validar — o plano, e o que ele não previa

O plano original tinha quatro degraus: contagem de parâmetros, uma época, curva curta, build
completo. Os três primeiros passaram e foram além do previsto — não só a loss inicial, mas a loss em
`train` **sob seed compartilhada** (o que prova a ordem das três extrações de RNG) e os gradientes.

O quarto degrau errou o alvo. "Comparar os embeddings do build completo" pressupõe que o build seja
uma função da seed, e **não é** (R16). A correção foi trocar a pergunta: em vez de "quão perto?",
medir **perto comparado a quê** — a referência contra si mesma, e a referência entre seeds. Só o
terceiro número dá sentido ao primeiro.

Lição transferível: quando o alvo é estocástico, um teste de equivalência precisa **medir o próprio
piso** antes de julgar a distância. Sem esse piso eu teria tanto material para declarar sucesso
(cosseno 0,99!) quanto para declarar fracasso (RMS 0,16!), e nenhum dos dois seria uma conclusão.

Continua valendo o degrau final de verdade: rodar as três famílias sobre um substrato construído por
mim e comparar as **métricas downstream**, que são as que alguém lê.

## 7 · Riscos

| risco | mitigação |
|---|---|
| O construtor de 466 linhas esconde uma variante ligada que eu leia como desligada | Construir a referência e a minha lado a lado e **diffar a árvore de módulos**, como no transplante do joint |
| A ordem de consumo do RNG difere e o full-batch não tem folds para diluir | Comparar a loss inicial (determinística dada a seed) antes da trajetória |
| O `POI2Region` do HGI arrasta mais dependências | Mapear antes de escrever; ele é o único componente que vem de outro engine |
| Alabama treina rápido, mas TX/CA em full-batch sobre 3,8 M de nós é outra escala | Medir memória em AL primeiro; o full-batch não tem como ser dividido sem mudar o objetivo |

## 8 · Ordem sugerida

1. `ResidualLNEncoder` + `Checkin2POI` + `POI2Region` — as três peças pequenas, com transplante de pesos.
2. A base `Check2HGI` restrita ao caminho v18, com o diff de árvore de módulos como gate.
3. `Check2HGI_DesignK` e os carregadores de Delaunay/POI2Vec.
4. O laço, que é trivial depois do resto.
5. Build de Alabama e comparação downstream.
