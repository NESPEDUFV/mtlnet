# A ponte: o que fazer no lugar dela — recomendação para o v20

**Aberto em** 2026-08-24, durante a leitura confirmatória da v19.
**Estado:** recomendação formada, com literatura. **Não aplicável ao v19** — a receita está congelada,
a ponte já foi gasta, e o gate reprovou; trocar a regra depois disso é o pós-hoc que o §12.7 cataloga.

## A recomendação, em uma linha

**Substituir a ponte por um *internal pilot* pré-registrado**: rodar S=2 no conjunto, medir a
dispersão entre réplicas **na validação interna** — que não gasta leitura —, e escalar para S=4 se
ela exceder um limiar declarado antes de qualquer dado do ciclo existir.

Isso é melhor que a ponte (mede o regime certo, no conjunto certo) e melhor que "S=4 sempre" (não
paga o dobro quando o conjunto é estável — e a evidência deste ciclo sugere que os grandes são).

## Por que a ponte precisa sair

**O que ela é, com o nome que a literatura usa.** Não há precedente em ML — calibrar a contagem de
réplicas em conjuntos pequenos para licenciar menos réplicas em conjuntos grandes do mesmo estudo
parece ser construção local, sem nome publicado. Mas em ensaios clínicos há o análogo direto:
**external pilot**, o uso de variância histórica para dimensionar um estudo novo. E há crítica
publicada.

**Browne (1995, *Statistics in Medicine* 14:1933–1940)**: usar o desvio de um piloto **diretamente**
produz poder abaixo do nominal com probabilidade alta; a correção é usar o **limite superior de
confiança** do desvio, não o valor pontual. **Kieser & Wassmer (1996, *Biometrical Journal* 38)** e
**Julious & Owen (2006, *Pharmaceutical Statistics*)** dão a inflação em função dos graus de
liberdade da estimativa externa.

**Schmidli, Neuenschwander & Friede (2017, *CSDA*)** dão o framework formal — *meta-analytic-predictive*:
meta-análise de efeitos aleatórios sobre o log-variância dos estudos históricos, produzindo uma
distribuição preditiva para o estudo novo. A diferença que importa: o MAP **modela a heterogeneidade
entre estudos** em vez de assumi-la nula ou resolvê-la por máximo.

**A disciplina consolidada dessa literatura é: variância externa serve para DESENHO; a ANÁLISE usa
variância interna.** O headline do v19 conforma — o Tier A é bootstrap de usuário, interno, e a
banda da ponte não entra em estimador nenhum. **Quem viola são os gates de escalada**, que aplicam o
envelope da ponte às células dos grandes mesmo a S=4. O §12.9 mediu a consequência: gates (i) e (ii)
cegos (exigem 0,76 e 1,61 pp para disparar), gate (iii) disparando quase independentemente do dado.

**A agregação por máximo não tem crítica publicada porque ninguém a usa.** O que a literatura usa é
UCL (Browne) ou predição MAP. O máximo é conservadorismo *ad hoc*, sem as propriedades conhecidas de
nenhum dos dois — e deixa o **menor** conjunto com veto sobre o **maior**.

**E a não-transferência foi medida dentro deste próprio ciclo:**

| conjunto | usuários | banda cat | banda reg |
|---|---:|---:|---:|
| alabama | 1 101 | 0,1241 | 0,1363 |
| arizona | 2 136 | 0,0521 | **0,3167** |
| istanbul | 14 530 | 0,0415 | **0,0286** |

Istambul, o maior, tem a **menor** banda — 11× menor que a do Arizona, que detém o veto. E a
agregação por máximo fez o Arizona, com 2 136 usuários, ditar o desenho do Texas, com 22 592.

## Por que o internal pilot é válido, e a proposta ingênua não

A literatura de desenhos adaptativos separa duas coisas, e a separação é exatamente a que este
problema pede:

* adaptar sobre o **efeito observado** exige maquinário *group-sequential*: fronteiras
  pré-especificadas (Pocock 1977; O'Brien & Fleming 1979), gasto de α (Lan & DeMets 1983), ou SPRT
  (Wald 1945). Sem isso, a regra de parada vira parte do estimador e o α nominal deixa de valer;
* adaptar sobre um **parâmetro de perturbação** — a variância — é o **internal pilot**
  (Wittes & Brittain 1990; **Kieser & Friede 2000, *Statistics in Medicine* 19:901–911**, com
  controle exato do tipo I; revisão em Friede & Kieser 2006, *Biometrical Journal* 48:537–555). A
  posição regulatória é explícita: o **FDA (2019, *Adaptive Designs for Clinical Trials*)** registra
  que adaptação de tamanho amostral informada por parâmetro de perturbação tem inflação de tipo I
  negligenciável e **não exige gasto de α**.

**A restrição peculiar deste projeto resolve a favor do internal pilot.** Olhar o teste externo o
GASTA, de forma irreversível e registrada no livro. Olhar a dispersão entre réplicas na **validação
interna** não gasta nada. Então "rodar 2, olhar, escalar" é inválido se o gatilho for o delta do
teste externo, e **válido** se for a dispersão interna — desde que a regra esteja pré-registrada
antes de qualquer dado do ciclo existir.

⚠ **Ressalva de engenharia.** A banda que o v19 computa sai de leituras OOF externas
(`seed_deltas` no payload de `compare`). O v20 precisa defini-la sobre `inner_val`, ou sobre
predições externas geradas-mas-não-lidas — distinção que o `READ_LEDGER.json` já sabe fazer, mas que
o código de banda ainda não faz.

## O desenho proposto para o v20

1. **Pré-registrar**, antes de o ciclo produzir qualquer número: o limiar da dispersão interna, o
   incremento da escalada (2 → 4), e o teto.
2. **Rodar S=2** em todo conjunto.
3. **Medir a dispersão entre as duas réplicas na validação interna.** Não gasta leitura.
4. **Escalar mecanicamente** se exceder o limiar. Nenhuma decisão humana no laço.
5. **Ler o teste externo uma única vez**, no S final.
6. **Reportar o desfecho da escalada** ao lado de cada célula — quem escalou, quem não, e por quê.

Os três gates de auditoria do §2 passam a usar a banda **do próprio conjunto** quando S ≥ 3, e não
a de outro. O §12.9 registra por que isso importa: com o envelope da ponte, o passo do gate (iii) a
S=4 é 0,3802 contra uma margem de 0,4 — quase todo veredito decisivo vira `seed-limited`.

## Alternativa, se o internal pilot for caro demais de implementar

**Calibrar no regime certo**: usar o mais barato dos conjuntos grandes (Flórida, 4,4 h por par de
réplicas) a S=4 para licenciar Califórnia e Texas. Custa menos que a ponte de conjuntos pequenos e
mede o aprendiz no regime que pretende calibrar. É pior que o internal pilot — ainda transfere entre
conjuntos — mas transfere dentro de uma ordem de grandeza em vez de através de uma.

## O que NÃO é o argumento

**Não é custo.** Ex post, abolir a ponte não teria economizado nada: o gate reprovou, e S=4 em tudo
custa as mesmas horas. O argumento é que (a) a evidência deste ciclo mostra que a banda pequeno→grande
não transfere, e (b) sob agregação por máximo, a probabilidade de o gate de região passar era
praticamente nula — logo o valor esperado da economia que a ponte prometia era ~zero.

**Não é que a ponte enviesou os resultados.** A banda não entra em estimador nenhum; cada Δ dos
conjuntos grandes sai do bootstrap de usuário do próprio conjunto. O que ela contamina é o **rótulo
de estabilidade** que acompanha o veredito (§12.9), não o número.

## E uma contradição maior, que este memorando não resolve

**Bouthillier et al. (2021, *MLSys* 3, "Accounting for Variance in Machine Learning Benchmarks")**
medem que a **amostragem de dados é a fonte dominante de variância** — a inicialização contribui
menos da metade — e recomendam *"as many sources of variation as possible should be randomized"*.

Este protocolo congela a partição e varia só a inicialização. Ele compensa: o eixo dominante é
carregado pelo bootstrap de usuário do §3, e o eixo de partição é medido à parte (§10.4/§12.6a).
Mas sobra o seguinte, e é maior que a discussão da ponte:

> Toda a controvérsia S=2 contra S=4 é travada sobre o eixo que a literatura ranqueia como o **menos
> importante** (réplica/inicialização, 0,05–0,15 pp), enquanto o eixo de partição medido neste
> próprio projeto — **+0,37 pp em região no Alabama** — é quase do tamanho da margem δ=0,4, e vai
> **ao lado** do intervalo em vez de dentro dele.

Um parecerista informado por essa literatura ataca ali, não no S. O v20 deve decidir o que fazer com
o eixo de partição antes de refinar o eixo de réplica.
