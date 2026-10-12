# BASELINES_EXTERNOS.md — o que a comparação com a literatura estabelece, e como dizê-la

> **Escrito 2026-08-24**, quatro dias antes da defesa, a pedido do autor. **Nada aqui é resultado
> novo**: cada número e cada cláusula vem do texto entregue, com `arquivo:linha`. O que é novo é a
> *leitura* — o texto entregue reporta a comparação externa e depois a rebaixa de propósito, e este
> registro explica por quê, o que ainda assim se pode afirmar, e onde.
>
> **A pergunta que o originou.** O autor observou que a apresentação não destaca que o modelo
> conjunto supera os baselines da literatura, e perguntou se isso não deveria aparecer entre as
> contribuições e no Resumo/Abstract. A resposta curta é: **sim para a apresentação, com uma frase
> escopada e um slide de reserva; não para as contribuições e não para o Resumo** — e as razões
> estão abaixo, incluindo as que contrariam a intuição inicial.

---

## 1 · O fato, primeiro

O modelo conjunto está **à frente de todo baseline externo reportado, nas duas tarefas, nos seis
conjuntos** (`chapters/5_mobiwac/06_results.tex:256`). As margens, calculadas da Tabela 10
(`tables/mobiwac/results.tex`):

| eixo | melhor externo | margem do conjunto | células |
|---|---|---|---|
| **próxima categoria** (macro-F1) | POI-RGNN | **+4,11 a +6,93** (era +3,06 a +6,93 até 2026-10-01; ver a nota abaixo) | 6 de 6 |
| **próxima região** (Acc@10) | HMT-GRN / STAN / ReHDM, o melhor por conjunto | **+3,55 a +6,04** | 6 de 6 |

> **Corrigido 2026-10-02.** As células do POI-RGNN em FL/CA/TX eram **34,49 / 31,78 / 33,03**, de uma
> implementação anterior (TF, outubro de 2025) com folds que dividiam as janelas de cada utilizador.
> Desde 2026-10-01 o Cap. 5 imprime as da reimplementação, com folds disjuntos por utilizador:
> **33,35 / 30,71 / 32,08**. A menor margem do conjunto sobre o POI-RGNN passa de **3,06 para 4,11**,
> no Texas (36,19 − 32,08); a maior continua 6,93, no Arizona. Fonte: `src/tables/mobiwac/results.tex`
> e a linha correspondente da Tabela B.5 (`src/tables/mobiwac/errata_scope.tex`); a história da
> mistura está no `CLAUDE.md` §5, armadilha 3.

E o contraste que motiva a pergunta do autor é real:

| comparação | faixa |
|---|---|
| conjunto × **dedicado** — a comparação controlada, onde toda a maquinaria estatística é gasta | **−0,88 a +1,21** |
| conjunto × **literatura** | **+4,11 a +6,93** |

**A margem sobre a literatura é de outra ordem de grandeza que a margem que a tese discute.** A
observação do autor procede.

---

## 2 · Por que o texto entregue a rebaixa, e por que isso é correto

O capítulo declara a sua posição em `06_results.tex:292`:

> *"We treat **the floor, not the external systems, as the reference** the region task has to
> clear, and we read the external columns as **a comparison against published designs rather than
> as the standard for this task**."*

Três razões a sustentam, e elas **não têm o mesmo peso nos dois eixos** — o que é a chave deste
registro.

### 2.1 · A margem externa inclui a vantagem de representação

`06_results.tex:261`: *"These externals run on their own embeddings, so this comparison **also
includes the representation advantage** of §5.6.1; the controlled comparison for the joint model
remains the Dedicated column."*

⚠ **Consequência dura:** a margem sobre a literatura **não é evidência sobre multitarefa**. Usá-la
para sustentar a tese de MTL é erro de categoria. Ela é evidência **da representação**.

### 2.2 · No eixo de REGIÃO, um piso de Markov supera os externos

`06_results.tex:264-271`: o piso de Markov-1, computado sob as nossas janelas e partições, alcança
**51 a 72** Acc@10; o conjunto o supera por **4,1 a 10,0** nos seis. E:

> *"That floor is also above the three external region systems at most datasets. **HMT-GRN falls
> below it at all six**, the ReHDM reference at three, and **STAN at four**."*

A razão está declarada: as janelas avançam **uma visita por vez**, então a região da última visita
prediz muito bem a próxima — no Alabama o alvo é a última região visitada em **32,9%** das janelas.

⚠ **Isto é o que torna perigoso reivindicar "superamos a literatura" no eixo de região.** Um
arguidor que pergunte *"e como vai um baseline trivial?"* encontra a resposta na própria Tabela 10,
e ela desmonta a manchete. **A pergunta já está no banco: `ARGUICAO.md` Q22.**

### 2.3 · Os três sistemas de região não competem em pé de igualdade

`06_results.tex:285-289` e `ARGUICAO.md` Q7:

| sistema | como rodou | ressalva |
|---|---|---|
| **HMT-GRN** | mesmos dados, partições e inicializações; **estrutura multitarefa preservada**; prior de transição de região construído com o treino de cada partição; componentes de grafo e busca em feixe hierárquica **removidos porque servem à predição exata de lugar** | *"not a reproduction of the complete published system"* |
| **STAN** | mesmas partições, mas **embeddings e construção de sequência próprios**, configuração fixa; **saída adaptada** para ranquear regiões | partições **parciais**: TX 4/5, CA 2/5, semente 0 |
| **ReHDM** | **protocolo publicado dele** | não medido nas nossas janelas nem partições; TX e CA com uma semente |

---

## 3 · ⚠ A assimetria entre os dois eixos, que é o achado deste registro

**As três ressalvas acima valem para REGIÃO. Nenhuma delas vale para CATEGORIA.** Medido:

| | próxima categoria | próxima região |
|---|---|---|
| o baseline externo é **nativo da tarefa**? | **sim** — POI-RGNN prediz a próxima categoria (`2_fundamentals.tex:351`) | **não diretamente** — ver §4 |
| foi **adaptado**? | **não** — *"which we re-implement from its published architecture and hyperparameters"* (`05_setup.tex:178`) | STAN sim (saída trocada); HMT-GRN parcialmente (ver §4) |
| roda nas **nossas partições**? | sim | HMT-GRN sim; STAN parcial; ReHDM não |
| o **piso trivial** o supera? | **não.** O POI-RGNN está acima do Markov-K **nos seis** (20,50→23,80; 23,92→27,64; 24,55→30,12; 29,74→33,35; 27,58→30,71; 28,67→32,08) | **sim**, na maioria |

> **Conclusão operacional.** O momento *"estamos à frente da literatura"* existe e é honesto —
> **mas vive no eixo de CATEGORIA**, onde o baseline é nativo, fielmente reimplementado, e acima do
> piso sintonizado nos seis conjuntos. **+4,11 a +6,93, seis de seis.**
> No eixo de região a coluna externa valida pouco, e reivindicá-la custa mais do que rende.

---

## 4 · Duas correções ao enquadramento fácil, que o autor levantou e o texto confirma

**(a) O HMT-GRN NÃO foi amputado da sua capacidade de predizer região — ele a tem nativamente.**
`2_fundamentals.tex:348`: *"HMT-GRN uses a **predicted region** to constrain the search for a
place."* E `05_setup.tex:180`: *"We **keep its shared multitask structure**."* O que foi removido
foram os componentes que servem à **busca do lugar**, que é a etapa seguinte e irrelevante para uma
avaliação só de região.
⚠ **Portanto não se deve dizer que "amputamos" o HMT-GRN.** A formulação correta: *ele prediz
região como etapa intermediária da sua hierarquia; nós avaliamos exatamente essa etapa, mantendo a
estrutura multitarefa dele.* A ressalva de "not a complete reproduction" continua verdadeira e deve
acompanhar — mas ela é sobre a pilha de próximo-lugar, não sobre a predição de região.

**(b) O Markov não é um "piso trivial" a ser descartado — é baseline sintonizado.**
`05_setup.tex:178`: *"a Markov model that predicts the category that most often follows the recent
categories. We **select the best Markov order for each dataset**."* E o piso de região é computado
sob as nossas janelas e partições, o que o torna a referência mais justa que existe para esta
tarefa — que é exatamente por que o capítulo o adota como referência declarada.
⚠ **Tratá-lo com desdém na fala é um erro.** Ele é o degrau 1 do argumento, não uma ameaça a ele.

---

## 5 · Por que não existe baseline nativo de próxima-região — a justificativa, que já está escrita

Esta é a pergunta que o autor previu e que **ainda não estava no banco de arguição**. A resposta
está no texto entregue, em `chapters/5_mobiwac/02_related.tex:93-102`:

> *"The field increasingly models several granularities at once; in those systems, **category and
> region are auxiliary signals that help a primary next-place task** (MCMG, HMT-GRN). We study the
> pair as the object itself. To our knowledge, **fine-grained region as an end target of equal
> standing, rather than an auxiliary coarse grid cell, is underexplored.**
> **The nearest exceptions do not study our exact pairing:** DRRGNN forecasts a person's next
> activity region jointly with a mobility-intention label, **but over regions discovered per person
> rather than a fixed citywide partition**; a generative recommender predicts category and region
> together, **but only as auxiliary steps toward its next-place ranking.*"*

**Ou seja: não é que não se procurou. É que os candidatos existem e não são comparáveis** —
o DRRGNN prediz região diretamente, mas **num espaço de rótulos diferente** (regiões descobertas por
pessoa, não uma partição fixa da cidade), e o outro a usa como etapa auxiliar. Foi por isso que a
comparação de região teve de ser **construída**, e é por isso que ela carrega as ressalvas da §2.3.

⚠ **Esta é uma força, não uma fraqueza, e deve ser dita como tal:** a ausência de baseline nativo é
a evidência mais direta de que o alvo é pouco explorado — que é a alegação de originalidade que o
Cap. 5 faz em `01_introduction.tex:36` (*"to our knowledge, the first work to treat fine-grained
region as an end target of equal standing"*).

---

## 6 · A escada — a forma recomendada de apresentar

Apresentar a hierarquia inteira, **em ordem**, num único momento. O ganho é que a pergunta do piso
de Markov deixa de ser ameaça e vira **o primeiro degrau do próprio argumento**:

| degrau | | |
|---|---|---|
| **1** | **piso de Markov** (região 51–72; categoria Markov-K por conjunto) | é a referência declarada do capítulo, computada sob as nossas janelas e partições. No eixo de região ele supera HMT-GRN nos seis, STAN em quatro, ReHDM em três — o que mostra que, **sob este protocolo**, a literatura adaptada não é a régua |
| **2** | **modelo dedicado** | acima do piso e de todo sistema externo, nos seis, nas duas tarefas. **É o sistema mais forte da tabela — é a régua real** |
| **3** | **modelo conjunto** | **não-inferior ao dedicado nos seis** (TOST, margem de 2 pontos registrada antes de qualquer resultado), **à frente em três células**, com **metade dos modelos e uma passagem** |

> **Correção (2026-10-01):** o piso Markov-K de categoria **não** é computado "sob as nossas janelas e partições". Ele usa `SEED=42` sobre as linhas da ETL do POI-RGNN (janelas de 9 visitas sem sobreposição, duplicatas consecutivas removidas — ~11% das nossas linhas no Alabama, 10.749 contra 96.326), StratifiedGroupKFold agrupado por usuário próprio, e o K é escolhido nos próprios folds de avaliação. Evidência: `scripts/compute_markov_kstep_cat.py`, `research/baselines/poi_rgnn/etl.py`, `docs/results/P0/simple_baselines/<estado>/next_category_markov_kstep.json`.

**O que a escada faz que uma manchete isolada não faz:**
- responde à pergunta do piso antes de ela ser feita;
- traz a comparação externa à tela, mas **subordinada e explicada**;
- termina na tese, não na literatura;
- e converte o resultado de ±1 ponto de aparente fraqueza em argumento: **igualar uma régua forte,
  com metade dos modelos, é o ponto do multitarefa.**

⚠ **As três superioridades, ditas com precisão:** Flórida em categoria (+0,19, Holm *p* 0,011);
Texas (+1,21, *p* corrigido 0,00013) e Califórnia (+1,06) em região. **As duas de região são
resultados secundários fora do plano registrado** — o plano não definiu teste de superioridade para
região. Os dois fatos viajam juntos, sempre.

---

## 7 · O que NÃO fazer, e por quê

| proposta | veredito | razão |
|---|---|---|
| pôr *"supera baselines da literatura"* entre as **contribuições enumeradas** | **não** | a margem inclui a vantagem de representação, então não é contribuição do multitarefa; e no eixo de região o piso trivial também os supera |
| acrescentar ao **Resumo / Abstract** | **não** | o abstract passaria a destacar o que o próprio Cap. 5 rebaixa explicitamente (*"not the standard for this task"*). Abstract que contradiz o seu capítulo convida arguição sobre **integridade do texto**, não sobre ciência. A base estatística (STAN em 4/5 e 2/5 partições, semente única; ReHDM uma semente) não sustenta a posição de maior escrutínio do documento |
| dizer *"superamos o STAN"* espontaneamente | **não** | o STAN é o caso mais adaptado dos três (saída trocada) e o de partições mais parciais. É a alegação de pior apoio da tabela |
| dizer *"amputamos os externos"* | **não** | falso para o HMT-GRN (§4a) e desnecessário para o STAN, cuja ressalva já está escrita |

**Condição para reabrir o Resumo:** só na versão pós-defesa, e **só se a banca pedir** comparação
com a literatura em destaque. Nesse caso, uma frase escopada, atribuída à **pilha** (representação +
cabeça), jamais ao multitarefa, jamais como contribuição enumerada.

---

## 8 · Duas respostas de arguição, prontas

### ⓐ *"Vocês chegam a superar os modelos da literatura?"*

> "Sim, nas duas tarefas e nos seis conjuntos. **Na próxima categoria a comparação é limpa**: o
> POI-RGNN é nativo da tarefa, foi reimplementado da arquitetura e dos hiperparâmetros publicados,
> está acima do piso de Markov sintonizado nos seis, e nós ficamos de **três a sete pontos de
> macro-F1 acima dele**, nos seis.
> **Na região eu sou mais cauteloso, e digo por quê**: não existe baseline nativo desse alvo, então
> a comparação teve de ser construída, e um piso de Markov de primeira ordem também supera dois dos
> três sistemas na maioria dos conjuntos — o que me diz que a coluna externa valida pouco ali. Por
> isso o capítulo declara o **piso**, não os sistemas externos, como a referência que a tarefa tem
> de vencer.
> E a ressalva que vale para as duas: **essa margem inclui a vantagem da representação**. Por isso
> a comparação que decide a tese não é essa — é a coluna *Dedicated*, que partilha representação,
> janelas e partições comigo."

### ⓑ *"Por que não há um baseline que faça exatamente próxima-região?"*

> "Porque não encontramos um comparável, e isso está no capítulo. Os sistemas que modelam região a
> usam como **sinal auxiliar** para a predição do lugar exato — é o caso do HMT-GRN e do MCMG. As
> exceções mais próximas não estudam o nosso par: o **DRRGNN** prediz região diretamente, mas sobre
> **regiões descobertas por pessoa**, não uma partição fixa da cidade, então o espaço de rótulos é
> outro; e o recomendador generativo prediz categoria e região juntas, mas **só como etapas
> auxiliares** do ranqueamento de lugar.
> Foi por isso que a comparação de região teve de ser construída a partir do que existe — e é
> também por isso que o capítulo afirma, **até onde sabemos**, ser o primeiro trabalho a tratar
> região de granularidade fina como alvo final de igual estatuto."

---

## 9 · Onde isto entra na apresentação

| onde | o quê |
|---|---|
| slide de **contribuições** | **intocado** |
| **S46**, o slide da Tabela 10 | uma frase na **fala** sobre a coluna *Dedicated* ser o sistema mais forte da tabela — a escada, dita uma vez |
| **série B**, slide novo | a tabela externa completa, com as notas de adaptação, as partições parciais, a linha do piso de Markov, e a resposta ⓐ. É ali que *"superamos o STAN"* mora — **como resposta, nunca como afirmação espontânea** |
| **série B**, `SB40` (`B6-4`) | já existe e já responde a pergunta do piso de Markov. **Nada a fazer** |
| **ARGUICAO** `Q7`, `Q22` | já cobrem o lado defensivo (protocolo dos externos; o piso). Este registro cobre o lado **afirmativo**, que faltava |

---

## 10 · Proveniência

| afirmação | fonte |
|---|---|
| todas as células da Tabela 10 | `src/tables/mobiwac/results.tex` |
| *"above every external baseline reported, on both tasks, across all six datasets"* | `src/chapters/5_mobiwac/06_results.tex:256` |
| a margem inclui a vantagem de representação | `:261` |
| piso de Markov 51–72; conjunto o supera por 4,1 a 10,0 | `:264-266`. ⚠ a faixa 4,1–10,0 é **derivada**, não citada — o comentário de proveniência ao lado a redeuz célula a célula: FL 4,07 (a mais estreita) a Istambul 10,02 (a mais larga) |
| o piso acima dos três externos; HMT-GRN nos seis, ReHDM em três, STAN em quatro | `:269-271` |
| janelas stride-1; 32,9% no Alabama | `:275` |
| os três sistemas não competem em pé de igualdade | `:285-289` |
| *"the floor, not the external systems, as the reference"* | `:292` |
| POI-RGNN reimplementado da arquitetura e hiperparâmetros publicados; Markov de melhor ordem por conjunto | `src/chapters/5_mobiwac/05_setup.tex:178` |
| HMT-GRN: estrutura multitarefa preservada; prior de transição por partição | `:180` |
| STAN: saída adaptada para ranquear regiões | `:182` |
| HMT-GRN prediz região para restringir a busca do lugar | `src/chapters/2_fundamentals.tex:348` |
| POI-RGNN prediz a próxima categoria | `src/chapters/2_fundamentals.tex:351` |
| DRRGNN sobre regiões por pessoa; recomendador generativo como etapa auxiliar | `src/chapters/5_mobiwac/02_related.tex:99` |
| *"to our knowledge, the first work to treat fine-grained region as an end target of equal standing"* | `src/chapters/5_mobiwac/01_introduction.tex:36` |
| FL +0,19 Holm *p* 0,011 | `src/chapters/5_mobiwac/06_results.tex:209` |
| TX +1,21 *p* corrigido 0,00013; CA +1,06 | `:223` |
| as duas superioridades de região são resultados secundários fora do plano | `src/chapters/5_mobiwac/05_setup.tex:113` |
| protocolo dos externos, já respondido | `wrapup/open_points/ARGUICAO.md` Q7 |
| o piso acima dos publicados, já respondido | `wrapup/open_points/ARGUICAO.md` Q22 |
