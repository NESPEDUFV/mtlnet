# P1 — o controle de capacidade no eixo de regiao: resultado

**Medido 2026-08-13.** Alvo do pareamento: **o modelo conjunto inteiro** (decisao do autor).
Larguras derivadas contra a arquitetura atual. Semente 0, cinco folds, engine `check2hgi_v18`,
receita do dedicado de regiao identica a reportada. Metrica: `top10_acc` por fold, a mesma
convencao com que o valor reportado do dedicado e extraido (verificado: o arquivo do dedicado
reportado reproduz 63,4456 a partir dos seus proprios folds).

---

## 1 · O resultado, em uma linha

**A vantagem de regiao do modelo conjunto nao sobrevive ao pareamento de capacidade.** Dado o mesmo
orcamento de parametros, o modelo dedicado de regiao **supera** o conjunto nos dois datasets que
carregavam a vantagem.

| dataset | dedicado estreito | dedicado pareado | conjunto | conjunto − pareado | p | unanime |
|---|--:|--:|--:|--:|--:|:--:|
| California (`d_model=528`) | 63,446 | **64,931** | 64,503 | **−0,428** | 0,0082 | sim (5/5) |
| Texas (`d_model=544`) | 64,951 | **66,330** | 66,117 | **−0,214** | 0,1162 | nao (4/5) |

O ganho do pareamento sobre o estreito e grande e inequivoco: **+1,486** em California e **+1,379**
em Texas, ambos com p < 0,0001 e unanimes nos cinco folds. Ou seja, largura sozinha compra mais do
que a vantagem que o conjunto reivindicava (+1,058 em CA e +1,165 em TX sobre o estreito).

## 2 · A curva de largura, que e a evidencia mais forte

O arm de `d_model=352`, que comecou como sonda por um erro de proveniencia de largura, virou o ponto
que transforma um ponto isolado em curva:

| largura | parametros | top10 | vs estreito | vs conjunto |
|---|--:|--:|--:|--:|
| 256 (reportado) | 3.256.510 | 63,446 | — | −1,058 |
| 352 (sonda) | 5.014.942 | 64,910 | +1,464 | **+0,406** |
| 528 (pareado) | 9.004.686 | 64,931 | +1,486 | **+0,428** |
| conjunto | 8.809.533 | 64,503 | +1,058 | — |

**A curva satura em 352**, com 57% do orcamento do conjunto: de 352 para 528 o ganho e +0,021
(p = 0,40), estatisticamente indistinguivel de zero. E o conjunto fica **abaixo dos dois pontos
largos**. Isso descarta a leitura de que o dedicado precisaria de todo o orcamento para empatar: ele
passa o conjunto com pouco mais da metade dele.

## 3 · O veredicto pela regra registrada ANTES de rodar

A regra escrita em `EXECUTION_WAVE.md` §3 previa tres faixas: abaixo de 0,3 pp de folga do conjunto,
consolidacao; 1 pp ou mais, a construcao acrescenta; entre elas, inconclusivo.

**Nenhuma das tres descreve o que aconteceu**, porque as tres pressupunham folga positiva. A folga e
negativa nos dois datasets. Aplicada ao literal, a regra classificaria Texas como consolidacao
(|−0,214| < 0,3) e California como inconclusivo (0,3 < |−0,428| < 1,0) — mas essa leitura perde o
sinal, que e o ponto. A leitura honesta e mais simples e mais forte:

> No eixo de regiao, e com o mesmo orcamento de parametros, o modelo dedicado alcanca ou supera o
> modelo conjunto nos dois datasets onde o conjunto reportava vantagem. A vantagem reportada mede
> capacidade, nao partilha entre tarefas.

**Direcao registrada:** California favorece o dedicado com p = 0,0082 e unanimidade nos cinco folds;
Texas favorece o dedicado por −0,214 com p = 0,1162 (quatro de cinco folds), o que **nao** sustenta
uma afirmacao de superioridade do dedicado em Texas — sustenta apenas que a vantagem do conjunto
desapareceu.

## 4 · O que isso obriga a dizer, e o que nao obriga

**Obriga.** A afirmacao de que o modelo conjunto supera os dedicados no eixo de regiao em Texas e
California **passa a ser condicional ao orcamento de parametros**, e a condicao nao esta satisfeita
na comparacao reportada. O texto enviado nao faz essa ressalva no eixo de regiao — o limite de
capacidade foi retirado da lista de limitacoes junto com o apendice relocado.

**Nao obriga.** Nada disso toca o eixo de **categoria**, onde a tese sobre representacao vive: a
diferenca de categoria entre conjunto e dedicado e equivalente a zero dentro de meio ponto, e o
controle de capacidade em categoria (Alabama, quatro sementes) mostra que 6,5x os parametros **piora**
o dedicado em 0,53 ponto. Tambem nao toca a comparacao com as referencias externas, nem o resultado da
representacao em nivel de check-in, que e o achado central da dissertacao.

**Enquadramento defensavel.** Um modelo serve as duas tarefas com o orcamento de dois, sem custo
mensuravel em categoria e com paridade em regiao. Isso e consolidacao, e e um resultado limpo. O que
nao se sustenta e atribuir a vantagem de regiao a transferencia entre tarefas.

## 5 · Proveniencia

- Resultados: `docs/results/P1/region_head_{california,texas}_region_5f_50ep_v18_*_capmatched*_s0.json`
- Comparador do conjunto: `docs/results/closing_data/v18/joint_best_perfold.json`, celulas
  `{state}_s0_joint`, campo `top10_full` por fold — mesma semente, mesma engine, mesma receita.
- Comparador do dedicado estreito: `v18_results.json`, `stl_reg_folds`.
- Desvio registrado: `MTL_STRICT` omitido nos tres arms. O certificado de empate aborta a celula por
  uma linha ambigua em 585.091 (0,00017%); os logs registram o aviso em vez do abort.
- Larguras: derivadas nesta sessao contra a arquitetura atual, porque a auditoria publicada mede a
  anterior. Nota datada em `storyline/audit/capacity_baseline_experiment.md` §6.
