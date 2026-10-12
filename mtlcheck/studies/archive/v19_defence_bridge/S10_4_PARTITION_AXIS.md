# §10.4 — o eixo de partição, medido em 2026-08-23

O protocolo congelou um sorteio de usuários em folds (`split_seed = 0`) e registrou que essa escolha
seria **medida**, não assumida. A medição nunca tinha rodado. Rodou agora: 30 fits no Alabama,
20 min de GPU, wave `s10_4_partition_axis.toml`, 6 células, 0 falhas.

Tudo sobre **validação interna** — é a grandeza de Tier B em que o limiar de 0,15 pp está escrito, e
nenhuma predição de fold externo foi tocada. As células novas não persistem predições.

## Os quatro deltas pareados (joint − dedicado), em pp

| | cat | sd entre folds | reg | sd entre folds |
|---|---:|---:|---:|---:|
| partição 0 · modelo 0 | −0,5329 | 0,583 | −1,2618 | 0,915 |
| partição 0 · modelo 7 | −0,4864 | 0,226 | −0,8580 | 0,367 |
| partição 7 · modelo 0 | −0,4657 | 0,386 | −0,4720 | 0,658 |
| partição 7 · modelo 7 | −0,3994 | 0,371 | −0,9158 | 0,411 |

## Os dois eixos

| tarefa | eixo de partição | erro-padrão | \|efeito\|/ep | eixo de modelo |
|---|---:|---:|---:|---:|
| cat | +0,0771 | 0,1741 | 0,44 | +0,0564 |
| **reg** | **+0,3659** | 0,2828 | **1,29** | −0,0200 |

⚠ **Uma primeira versão desta medição usou "média das diferenças absolutas" como movimento de eixo,
e deu 0,4238 pp para os DOIS eixos.** Não era coincidência: num 2×2 com aquele padrão de sinais, as
duas somas de valores absolutos são algebricamente idênticas. Um número que não distingue os eixos
não serve para decidir sobre um deles. O que está na tabela é o efeito principal — diferença das
médias marginais — com o erro-padrão ao lado, porque o §10.4 declara "1 df per axis,
sign-and-magnitude only" e a incerteza tem de aparecer junto do número.

## O que isto quer dizer

**Categoria: o congelamento se sustenta.** 0,077 pp, abaixo do limiar e dentro do próprio ruído.

**Região: a regra pré-registrada foi disparada, e o número não resolve.** O §10.4 escreve "if the
partition axis exceeds 0.15 pp, the freeze is unsafe and §2 reopens before any large-state fit".
0,366 pp excede. Mas 0,366 ± 0,283 é 1,29 desvio — indistinguível de zero.

As duas leituras honestas, e elas discordam:

* **literal** — a regra é mecânica e foi disparada; o congelamento é inseguro;
* **estatística** — aplicar um limiar mecânico a uma estimativa não resolvida é o mesmo erro que o
  §3 proíbe em toda parte ("never claimed in either direction").

Sendo uma regra de **segurança** e não de reivindicação, disparar no não-resolvido é o lado
conservador. O estado honesto é "pode ser inseguro", não "é seguro".

**O que o eixo NÃO faz:** virar o sinal. Os quatro deltas de região são negativos, de −0,47 a −1,26 —
o joint fica abaixo do teto dedicado em região nas duas partições, nas duas sementes de modelo. A partição
mexe na magnitude, não na direção.

## O que fecharia a questão

Mais colunas de partição. Cada uma custa ~20 min de GPU ociosa e usa o mesmo instrumento; duas ou
três levariam o eixo de 1 para 3 graus de liberdade e o erro-padrão de 0,28 para ~0,16. Isso não é
pré-registrado — o §10.4 especificou `{0, 7}` — e por isso vai como nota datada: é evidência a mais
sobre uma **conferência de segurança**, não sobre uma reivindicação, e move na direção conservadora.

Decisão do autor, pendente.

---

# O eixo nos quatro conjuntos com 2×2 completo — 2026-08-24

A wave `s10_4_axis_all_states.toml` rodou 32 das 36 células antes de ser interrompida por decisão do
autor. Ficou faltando o braço `joint` na Califórnia e no Texas, sem o qual o eixo não é computável
nesses dois — o eixo é joint menos dedicado.

## O resultado

| conjunto | usuários | tarefa | eixo de PARTIÇÃO | ep | \|ef\|/ep | eixo de MODELO |
|---|---:|---|---:|---:|---:|---:|
| alabama | 1 101 | cat | +0,0771 | 0,1741 | 0,44 | +0,0564 |
| alabama | 1 101 | **reg** | **+0,3659** | 0,2828 | 1,29 | −0,0200 |
| arizona | 2 136 | cat | −0,0361 | 0,1259 | 0,29 | +0,1197 |
| arizona | 2 136 | **reg** | **+0,3061** | 0,1736 | 1,76 | +0,0742 |
| florida | 10 622 | cat | +0,1167 | 0,0705 | 1,65 | +0,1031 |
| florida | 10 622 | reg | **−0,0349** | 0,0684 | 0,51 | −0,0798 |
| istanbul | 14 530 | cat | −0,0222 | 0,0709 | 0,31 | +0,0512 |
| istanbul | 14 530 | reg | **−0,0751** | 0,0749 | 1,00 | +0,0015 |

## A leitura

**O eixo de partição é fenômeno de conjunto pequeno.** Em região, ele passa o limiar de 0,15 pp nos
dois conjuntos com menos de 2 200 usuários e fica **abaixo** — com sinal invertido, aliás — nos dois
com mais de 10 mil. O erro-padrão cai junto, de 0,28 para 0,07: a medição fica quatro vezes mais
precisa exatamente onde o efeito some.

Categoria fica abaixo do limiar nos quatro.

Isso é o que a teoria previa: os resultados de estabilidade de validação cruzada condicionam tudo em
estabilidade do aprendiz, que melhora com o tamanho do conjunto de treino. Aqui deixou de ser
previsão.

## O que isto autoriza e o que não autoriza

**Autoriza** tratar o congelamento como seguro nos conjuntos grandes, e concentrar a ressalva onde
ela é devida: Alabama e Arizona.

**Não autoriza** estender por extrapolação até Califórnia (20 667) e Texas (22 592), que não foram
medidos. O maior conjunto medido tem 14 530 usuários, e os dois faltantes são ~1,5× maiores. A
extrapolação é razoável — o efeito já é indistinguível de zero a 10 mil, e o ruído só encolhe — mas
**é extrapolação, e o texto tem de dizer isso**. Completar os dois custa o braço `joint` a
`split_seed = 7`, ~8–14 h de GPU.

---

## A conta de "e se o eixo entrasse no intervalo" — construção pinada, 2026-08-24

Circulou nesta sessão a faixa "0,44–0,84 pp". O piso confere; **o teto não é reproduzível** por
nenhuma construção fechada, e um revisor de documentação o sinalizou antes que virasse texto. A
construção abaixo é a natural, e é a que fica registrada.

Componente de partição, das médias marginais do 2×2 do Alabama em região:

```
p0 = (−1,2618 + −0,8580)/2 = −1,0599        efeito = +0,3660 pp
p7 = (−0,4720 + −0,9158)/2 = −0,6939        σ_partição = 0,3660/√2 = 0,2588
```

Compondo `SE_total² = SE_boot² + σ²_partição + σ²_rep/S`, com σ_rep ≈ 0,10 e S = 4, sobre as
meias-larguras de região da leitura selada de 18-08:

| meia-largura atual (95 %) | SE_boot | SE_total | meia-largura a 90 % | a 95 % |
|---:|---:|---:|---:|---:|
| 0,095 | 0,0485 | 0,2680 | **0,4408** | 0,5253 |
| 0,171 | 0,0872 | 0,2777 | 0,4567 | 0,5442 |
| 0,199 | 0,1015 | 0,2825 | 0,4646 | 0,5536 |

**A faixa honesta é 0,44–0,55 pp a 90 %**, não 0,44–0,84.

A conclusão sobrevive: 0,441 > 0,400 = δ, então nenhuma célula de região seria não-inferior. Mas ela
passa **raspando** — 10 % acima da margem, não o dobro —, e o argumento "o intervalo ficaria maior
que a própria margem" tem de ser dito com esse número e não com o inflado.

O que continua valendo sem depender da faixa é o segundo argumento, que é estrutural: com agregação
por máximo, σ_partição é uma constante medida no Alabama, e num conjunto grande ela domina a soma —
o intervalo pararia de responder ao dado à medida que o dado melhora.
