# SPEECH.md — o que dizer, slide a slide

> **Defesa · sexta, 28/08/2026, 10:00 · remota (Google Meet).** Gerado do `SLIDES.md`, que é a fonte da fala. **Nada aqui é novo**: é o mesmo texto, reorganizado para ser lido de relance em vez de lido inteiro.

> **Como usar.** Cada cartão tem quatro camadas, em ordem de urgência: **ABRE** (a primeira oração, para pegar o fio sem ler), **DIZER** (as superfícies de lei e os números que não podem sair errado), **NUNCA** (o que anula o slide se escapar), e a fala completa embaixo, para consulta.

> ⚠ **O relógio.** A fala escrita tem **6.963 palavras**, que a 140 palavras/minuto dão **49:44**, contra o teto de **50 min** do Art. 23. Os campos `Tempo:` dos cartões somam **52:54** e são orçamento, não medição — se os dois discordarem, o medido vale. **Cronometre o fim de cada seção.**


---

## Marcas de tempo — leve estas seis

| seção | slides | fim previsto | **seu tempo real** |
|---|---|---:|---|
| **ABERTURA — a pergunta e o escopo** | S1–S6 | 3:21 | ____________ |
| **FUNDAMENTOS — dito uma vez** | S5b–S19 | 10:54 | ____________ |
| **MTLnet — Cap. 3 (CBIC)** | S18–S25 | 16:11 | ____________ |
| **ST-MTLNet — Cap. 4 (CoUrb)** | S26–S32 | 23:33 | ____________ |
| **Check2HGI — Cap. 5 (MobiWac)** | S33–S48 | 46:21 | ____________ |
| **CONCLUSÃO — a resposta condicional** | S49–S55 | 52:54 | ____________ |


---



# ABERTURA — a pergunta e o escopo


## S1 · Multitask Learning for POI Classification and Prediction Tasks
`PDF p.1` · **20 s** · fim previsto **0:20**

> ### ▶ Bom dia. Meu nome é Vitor Hugo, e vou apresentar minha dissertação de mestrado, orientada pelo professor Fabrício Silva, no PPGCC da Universidade Federal de Viçosa.

**● COBRE** — INTRODUZ nada (capa)

**✕ NUNCA** — nenhum resultado na capa. · Nunca usar o título de um dos artigos como título da dissertação.

<sub>Bom dia. Meu nome é Vitor Hugo, e vou apresentar minha dissertação de mestrado, orientada pelo professor Fabrício Silva, no PPGCC da Universidade Federal de Viçosa. Um aviso de forma antes de começar: os slides estão em inglês e a fala é em português. Os números na tela são os do documento que a banca recebeu, sem conversão.</sub>

---

## S2 · Human Mobility
`slide **1** · PDF p.3` · **45 s** · fim previsto **1:05**

> ### ▶ O ponto de partida é uma regularidade. Os rastros de mobilidade são ruidosos, mas o movimento humano é bastante regular: as pessoas voltam a um conjunto pequeno de lugares, e fazem viagens longas com menos frequência.

**● COBRE** — INTRODUZ o gancho: a regularidade da mobilidade e as aplicações

**# NÚMEROS** — pessoa em cerca de 93 por cento. Faço

**✕ NUNCA** — "pioneiro", "o primeiro". · Nunca apresentar os 93 por cento como teto de nada. · Nenhum particular do corpus. · Nenhum número nosso.

<sub>O ponto de partida é uma regularidade. Os rastros de mobilidade são ruidosos, mas o movimento humano é bastante regular: as pessoas voltam a um conjunto pequeno de lugares, e fazem viagens longas com menos frequência. E isso é mensurável: uma análise de entropia sobre rastros em larga escala estimou a previsibilidade potencial da próxima localização de uma pessoa em cerca de 93 por cento. Faço a ressalva na mesma frase, porque ela importa. Essa estimativa é sobre a próxima localização em resolução grossa, e ela não é teto para nenhuma métrica que eu vou reportar aqui. O que ela mostra é que existe regularidade aprendível. E antecipar o que e o onde da próxima visita é o que sustenta recomendação, navegação, planejamento de transporte e alocação de recursos por área.</sub>

---

## S3 · The ground: check-ins and what joint training promises
`slide **2** · PDF p.4` · **55 s** · fim previsto **2:00**

> ### ▶ Duas palavras e um risco, antes da pergunta. Uma rede social baseada em localização é uma plataforma em que as pessoas registram os lugares por onde passam.

**● COBRE** — INTRODUZ LBSN e check-in (chão didático) · INTRODUZ a promessa operacional do aprendizado multitarefa · gloss de transferência negativa (a definição, Def. 2.12, é INTRODUZ em S9)

**✕ NUNCA** — nenhum particular do corpus. · Não definir formalmente transferência negativa aqui; · a Def. · 2.12 é de S9.

<sub>Duas palavras e um risco, antes da pergunta. Uma rede social baseada em localização é uma plataforma em que as pessoas registram os lugares por onde passam. O registro é o check-in, e ele liga um usuário, um ponto de interesse e um instante. É esse detalhe geográfico e temporal que sustenta o estudo de cidades a partir de dados, e a área que estuda como as pessoas se movem pela cidade é mobilidade humana. Agora o aprendizado multitarefa: treinar tarefas relacionadas juntas, para que compartilhem informação. Aqui o apelo é operacional. Um modelo para manter, uma passagem, as duas predições, em vez de dois modelos dedicados. Mas treino conjunto não garante predição melhor. Parâmetros compartilhados podem prejudicar uma tarefa, e essa falha tem nome: transferência negativa. A definição formal dela fica para a próxima seção. Por ora basta o nome, porque é ele que a pergunta seguinte carrega.</sub>

---

## S4 · The question
`slide **3** · PDF p.5` · **41 s *(medido)*** · fim previsto **2:41**

> ### ▶ A pergunta da dissertacao, literalmente: o aprendizado multitarefa ajuda a predicao da proxima categoria e da proxima regiao, e de que depende a resposta?

**● COBRE** — INTRODUZ a pergunta de pesquisa · INTRODUZ a restrição de modelo único · gloss do veredito nas superfícies registradas (o ladder de veredito é INTRODUZ em 5.5; macro-F1 e Acc@10 aparecem aqui como rótulo do número, e as definições

**✕ NUNCA** — "empata", "matches", "ties", "semelhante", "a par", "em todos". · Nunca aplicar a margem de dois pontos ao eixo de categoria, nem o meio ponto ao eixo de região. · Nunca chamar as quatro células dentro da margem de empates. · Nunca ler a frase do Resumo entregue.

<sub>A pergunta da dissertacao, literalmente: o aprendizado multitarefa ajuda a predicao da proxima categoria e da proxima regiao, e de que depende a resposta? Ela vem com uma restricao que vale para tudo o que vem depois: um artefato treinado tem de produzir as duas saidas numa passagem so. E uma delimitacao, para ninguem esperar o que nao vem: o proximo lugar exato eu nao predigo, e nenhum capitulo reporta resultado para ele. A resposta eu dou na Secao cinco, com intervalo e com teste, depois de voces terem visto como ela foi obtida.</sub>

---

## S6 · Three studies, in sequence
`slide **4** · PDF p.6` · **40 s** · fim previsto **3:21**

> ### ▶ A dissertação é uma coletânea de três artigos, e a ordem deles é o argumento.

**● COBRE** — INTRODUZ o arco e os três capítulos (título de capítulo, veículo, ano, autoria) · INTRODUZ a armadilha de nomenclatura *"Next-POI Prediction" = próxima categoria*

**✕ NUNCA** — ampliar o crédito de autoria no Cap. · 4 além do que o texto entregue declara. · Nenhum resultado dos três estudos aqui.

<sub>A dissertação é uma coletânea de três artigos, e a ordem deles é o argumento. O texto diz assim: o primeiro reporta um resultado negativo, o segundo identifica o gargalo principal, e o terceiro testa a solução que sai daí. Cada estudo estreita a explicação que a evidência sustenta, e é por isso que a progressão é ela própria parte da contribuição. Veículo, ano e autoria estão na tela. E um aviso de nome antes de seguir, porque ele evita confusão nas duas seções seguintes: o título do Capítulo 3 diz *Next-POI Prediction*, e nos Capítulos 3 e 4 essa expressão quer dizer próxima categoria, não próximo lugar.</sub>

---


# FUNDAMENTOS — dito uma vez


## S5b · The tasks
`slide **5** · PDF p.8` · **45 s *(os dois blocos que ele funde somavam 70 s)*** · fim previsto **4:06**

> ### ▶ As tarefas, todas de uma vez, para não voltar a elas depois.

**● COBRE** — INTRODUZ as quatro tarefas (Defs. 2.6, 2.7, 2.8, 2.9) · INTRODUZ a mudança de par de tarefas entre os capítulos *(herdada do bloco Two traps, que deixa de existir)*

**✕ NUNCA** — "prediz o próximo POI".

<sub>As tarefas, todas de uma vez, para não voltar a elas depois. Classificação de categoria é estática: lê a representação de um lugar e diz o tipo dele. Próxima categoria e próxima região são sequenciais: leem um histórico de visitas e dizem, respectivamente, o tipo do próximo lugar e a unidade em escala de bairro onde a próxima visita acontece. E o próximo lugar exato está aqui para ser excluído: ele é definido no Capítulo 2 justamente para delimitar o escopo, e nenhum capítulo reporta resultado para ele. Uma coisa muda ao longo da dissertação, e é melhor dizer agora do que surpreender depois: o par de tarefas. Os dois primeiros estudos juntam a estática com a próxima categoria. O terceiro junta duas sequenciais, próxima categoria e próxima região.</sub>

---

## S13 · Related work: POI prediction
`slide **6** · PDF p.9` · **60 s *(medido)*** · fim previsto **5:06**

> ### ▶ Duas telas de trabalho relacionado, e elas são o chão comum dos dois primeiros estudos.

**● COBRE** — INTRODUZ o contexto de POI e MTL, o chão comum dos Caps. 3 e 4

**✕ NUNCA** — nenhum resultado, nenhum número. · Nenhuma afirmação de ineditismo aqui: ela é de S14, e vem escopada.

<sub>Duas telas de trabalho relacionado, e elas são o chão comum dos dois primeiros estudos. A tarefa dominante da área é o próximo lugar exato. A linha vai dos recorrentes, ST-RNN, DeepMove, Flashback, para os de atenção, STAN, GeoSAN, GETNext. Todos eles predizem o lugar exato, e por isso nenhum é linha de base direta para os alvos que eu estudo. O par que os dois primeiros estudos atacam é outro: classificação de categoria e previsão da próxima categoria. E, em mobilidade, o multitarefa foi usado quase inteiramente a serviço do próximo lugar. O MCARNN prevê atividade e lugar juntos; o CSLSL prevê em cascata quando, o quê e onde; o iMTL e o HAMTL seguem a mesma direção. O TME é a exceção que puxa para o outro lado, com anotação semântica estática de ponto de interesse.</sub>

---

## S14 · Category and region: means or end
`slide **7** · PDF p.10` · **54 s *(medido)*** · fim previsto **6:00**

> ### ▶ O eixo que separa este trabalho da literatura não é a tarefa, é o papel dela.

**● COBRE** — INTRODUZ o eixo meio × fim · INTRODUZ o mapa de onde saem os métodos externos

**✕ NUNCA** — afirmação de ineditismo mais forte do que a do texto. · A redação entregue é escopada a "entre os trabalhos revisados nesta dissertação", e a fala mantém o escopo. · Nenhum resultado, nenhum número.

<sub>O eixo que separa este trabalho da literatura não é a tarefa, é o papel dela. De um lado, categoria e região como **meio** para chegar ao próximo lugar: o HMT-GRN usa a região prevista para estreitar a busca pelo lugar, o CatDM usa a categoria prevista para reduzir o conjunto de candidatos. Do outro lado, como **fim**: o DRRGNN prevê região de atividade, o POI-RGNN prevê a próxima categoria. E a frase do texto, escopada como ela está escrita: entre os trabalhos revisados nesta dissertação, nenhum trata próxima categoria e próxima região como alvos finais de igual estatuto num modelo conjunto que não prediz também o próximo lugar. O rodapé é o mapa de onde saem os métodos externos que vão aparecer nas tabelas.</sub>

---

## S9 · MTL Fundamentals
`slide **8** · PDF p.11` · **40 s** · fim previsto **6:40**

> ### ▶ Três definições e um critério.

**● COBRE** — INTRODUZ compartilhamento rígido (Def. 2.10) · INTRODUZ transferência negativa (Def. 2.12) · INTRODUZ o critério declarado para um balanceador · RETOMA a promessa operacional de 1.2

**✕ NUNCA** — nenhuma afirmação de otimalidade de Pareto sobre os nossos modelos: o Cap. · 2 recusa a afirmação explicitamente. · Nenhum resultado, nenhum número.

<sub>Três definições e um critério. Compartilhamento rígido é a topologia em que todas as tarefas atravessam um mesmo tronco e só se separam na saída de cada uma; o flexível é o extremo oposto --- cada tarefa tem a sua própria rede, e elas são acopladas por uma penalidade. Transferência negativa é o desfecho que se teme: o treino conjunto deixa uma tarefa pior do que o modelo dedicado dela deixaria. O critério está declarado no Capítulo 2, e eu vou cobrá-lo mais adiante: um método de balanceamento só é útil se superar uma ponderação fixa bem ajustada. Guardem essa frase. É ela que decide o que eu posso e o que eu não posso afirmar sobre o balanceador na Seção 3.</sub>

---

## S15 · How places are represented
`slide **9** · PDF p.12` · **45 s** · fim previsto **7:25**

> ### ▶ Esta é a base mais importante da dissertação, e ela é uma escada.

**● COBRE** — INTRODUZ a linhagem de representações, no nível de o que cada degrau resolve · INTRODUZ o grafo de Delaunay como substrato comum aos três · *(os nomes DGI, HGI e Check2HGI aparecem como o último degrau, sem mecanismo; os artefatos

**✕ NUNCA** — o mecanismo do DGI ou do HGI aqui — eles pertencem a 3.2A e 4.1A. · Nunca afirmar que os três grafos de Delaunay são o mesmo objeto: a construção é comum, os pesos não (decaimento geodésico no Cap. · Haversine com penalidade de GEOID no Cap. · Nunca bilinear: o discriminador do DGI no Cap.

<sub>Esta é a base mais importante da dissertação, e ela é uma escada. Começa no identificador one-hot, que marca um lugar por posição e não codifica relação nenhuma. Sobe para as representações distribuídas, skip-gram, DeepWalk, node2vec, em que a geometria do vetor reflete a relação que está nos dados. Sobe de novo para as redes de grafo, GCN, GAT, GraphSAGE, que aprendem essa relação por agregação de vizinhança. E o último degrau é o infomax contrastivo: o modelo aprende vetores úteis sendo obrigado a distinguir um pareamento verdadeiro de um pareamento corrompido, e não precisa de rótulo nenhum para isso. É a ideia que sustenta os três métodos desta dissertação, e cada um tem o capítulo dele.</sub>

---

## S10 · The evidence base: six datasets
`slide **10** · PDF p.13` · **55 s** · fim previsto **8:20**

> ### ▶ Esta é a base de evidência inteira, dita uma vez só.

**● COBRE** — INTRODUZ a base de evidência (Tab. 8): Gowalla e Istanbul · INTRODUZ as sete categorias · INTRODUZ a região como unidade nomeada (census tract, *mahalle*)

**✕ NUNCA** — "superconjunto" para a Flórida. · Não há evidência de contenção entre as duas extrações. · Nenhum resultado de nenhum capítulo.

<sub>Esta é a base de evidência inteira, dita uma vez só. Cinco estados do Gowalla e Istambul, do Massive-STEPS, e a ordem da tabela é a do documento, por número de regiões. As sete categorias são as mesmas nos três estudos: Community, Entertainment, Food, Nightlife, Outdoors, Shopping e Travel. Região é o setor censitário nos cinco conjuntos americanos e o *mahalle* em Istambul. Os dois particionam a cidade em escala de bairro, e não são o mesmo tipo de objeto: um é unidade de medida, o outro é unidade de governo. A última coluna diz qual capítulo usou qual conjunto.</sub>

---

## S11 · The metric all three studies share
`slide **11** · PDF p.14` · **59 s *(medido)*** · fim previsto **9:19**

> ### ▶ A métrica de categoria dos três estudos é a macro-F1: a média das F1 por categoria, com cada categoria pesando igual.

**● COBRE** — INTRODUZ macro-F1 · INTRODUZ o piso de classe majoritária

**✕ NUNCA** — chamar de "macro-F1" os valores impressos dos Caps. · 3 e 4 (são uma F1 por categoria). · Nunca ler a coluna Majority da Tab. · 8 como se fosse a macro-F1 do preditor de classe majoritária: uma é a fração de rótulos na classe mais comum, a outra é o resultado de um preditor.

<sub>A métrica de categoria dos três estudos é a macro-F1: a média das F1 por categoria, com cada categoria pesando igual. A razão é a distribuição. Food é cerca de um terço dos check-ins num estado representativo, e uma acurácia simples esconderia o desempenho nas classes menores. Ela também tem um custo, e eu digo qual: a macro-F1 não mostra que classe melhorou, e pode ficar baixa mesmo com acurácia alta. E toda métrica que eu disser vem com ponto de referência. São dois, e nenhum é concorrente: o piso de classe majoritária, que sempre responde a categoria mais comum; e o piso de Markov, uma tabela de transição sobre as visitas de treino, que responde com o que mais costuma vir depois do quê --- primeira ordem para região, melhor ordem de cada conjunto para categoria.</sub>

---

## S12 · The protocol of the first two studies
`slide **12** · PDF p.15` · **50 s** · fim previsto **10:09**

> ### ▶ O protocolo dos dois primeiros estudos, e ele é diferente do terceiro.

**● COBRE** — INTRODUZ o protocolo dos dois primeiros estudos · INTRODUZ a lei dos verbos · INTRODUZ a armadilha do par de tarefas e a armadilha da convenção métrica · RETOMA a armadilha de nomenclatura de 1.5

**✕ NUNCA** — "as mesmas janelas". · O Cap. · 5 usa janelas deslizantes sobrepostas, com passo 1, e os Caps. · 3 e 4 usaram janelas não sobrepostas.

<sub>O protocolo dos dois primeiros estudos, e ele é diferente do terceiro. Validação cruzada de cinco partições, estratificada por amostra: os check-ins de um mesmo usuário podem cair dos dois lados da divisão. Orçamento cheio de épocas, sem parada antecipada, e cada tarefa lida na época de melhor validação dela. Médias e desvios entre as cinco partições, sem teste de significância. Daí sai a lei dos verbos que eu obedeço a fala inteira: *supera* fica reservado para teste pareado de superioridade, e os Capítulos 3 e 4 não têm teste, então eles reportam diferenças, não veredito. E uma convenção que eu digo agora e não repito: os Capítulos 3 e 4 imprimem uma F1 por categoria, e o Capítulo 5 reporta macro-F1, um número só. Não são a mesma escala, e eu volto a lembrar disso quando as tabelas aparecerem.</sub>

---

## S19 · DGI
`slide **13** · PDF p.17` · **45 s** · fim previsto **10:54**

> ### ▶ O primeiro mecanismo, e o desenho conta a história: parte-se do grafo real, faz-se uma cópia corrompida embaralhando as features entre os nós, as duas passam pela MESMA r…

**● COBRE** — INTRODUZ o mecanismo do DGI · RETOMA a ideia infomax de 2.1 e o degrau do DGI em 2.7

**✕ NUNCA** — "one-hot da própria categoria" como atributo de nó. · Nunca "coocorrência": este canal não existe no Cap. · Nunca "o DGI não vaza" (a formulação correta está no slide B4-LEAK).

<sub>O primeiro mecanismo, e o desenho conta a história: parte-se do grafo real, faz-se uma cópia corrompida embaralhando as features entre os nós, as duas passam pela MESMA rede, e um discriminador julga se cada nó combina com o resumo global do grafo verdadeiro. É disso que sai o vetor, sem rótulo nenhum. Duas coisas que o desenho não diz e que importam. A primeira: a feature de entrada de um lugar é a média dos vizinhos dele com o próprio vetor excluído -- ou seja, a entrada descreve uma vizinhança, e não a lembrança do próprio rótulo. A segunda: o que sai é um vetor por lugar, e toda visita àquele lugar entra no modelo com o mesmo vetor. Guardem essa segunda, porque é ela que o Capítulo 5 desfaz.</sub>

---


# MTLnet — Cap. 3 (CBIC)


## S18 · MTLnet
`slide **14** · PDF p.18` · **45 s** · fim previsto **11:39**

> ### ▶ Esta é a arquitetura, o MTLnet. Vale guardar a figura, porque o Capítulo 4 não vai alterar uma linha dela.

**● COBRE** — INTRODUZ MTLnet · INTRODUZ FiLM

**# NÚMEROS** — compartilhamento rígido da Definição 2.10. E no fim

**✕ NUNCA** — nenhum número do Cap. · 3 ao lado de um do Cap. · Nunca "backbone": o nome é tronco compartilhado.

<sub>Esta é a arquitetura, o MTLnet. Vale guardar a figura, porque o Capítulo 4 não vai alterar uma linha dela. Cada tarefa entra por um encoder próprio, um MLP. Vem então a modulação FiLM, e ela cabe numa cláusula: um vetor de identidade de tarefa gera uma escala e um deslocamento, aplicados às features antes da parte compartilhada, de modo que as duas tarefas leiam os mesmos parâmetros sob escalas diferentes. Depois vem o tronco de blocos residuais, que é o compartilhamento rígido da Definição 2.10. E no fim duas saídas, uma por tarefa. O segundo item é o detalhe que vai importar no próximo slide: o capítulo declara os parâmetros em dois conjuntos disjuntos, os compartilhados e os específicos de tarefa. É sobre o primeiro conjunto que um balanceador de gradientes age.</sub>

---

## S21 · Two losses, one set of parameters
`sem página` · **70 s *(medido)*** · fim previsto **12:49**

> ### ▶ Antes de eu nomear o otimizador, o problema que ele existe para resolver.

**● COBRE** — INTRODUZ o problema multiobjetivo, a dominância e a fronteira de Pareto, e as duas classes de método de balanceamento

**✕ NUNCA** — nenhuma afirmação de Pareto sobre os nossos modelos. · Nenhum formalismo do zoo de balanceadores na tela (§8 regra 16): os nomes entram como lista, sem equação.

<sub>Antes de eu nomear o otimizador, o problema que ele existe para resolver. São duas perdas e um único conjunto de parâmetros compartilhados, e entre duas soluções não há ordem total: uma pode ser melhor numa tarefa e pior na outra, e as duas ficam incomparáveis. Escrever a soma ponderada das perdas não remove essa natureza multiobjetivo. Daí vem o vocabulário: uma configuração domina outra no sentido de Pareto quando não é pior em nenhuma perda e é melhor em pelo menos uma; ela é Pareto-ótima quando nenhuma outra a domina; e o conjunto dos vetores de perda dessas configurações é a fronteira de Pareto. A área respondeu a isso com uma família inteira de métodos, e a família se divide em duas classes: os que fixam os pesos das perdas e os que mudam a direção da atualização. Uma ressalva que é do Capítulo 2 e que eu repito de propósito: esta dissertação não reivindica nenhuma propriedade de Pareto para os modelos dela.</sub>

---

## S22 · Nash-MTL, and what the chapter may claim about it
`sem página` · **72 s *(medido)*** · fim previsto **14:01**

> ### ▶ O Nash-MTL cai na segunda classe.

**● COBRE** — INTRODUZ Nash-MTL · RETOMA o critério de 2.2 e as duas classes de S21

**✕ NUNCA** — nenhuma afirmação de Pareto sobre os nossos modelos. · Nunca apresentar a adoção do Nash como posição atual da dissertação.

<sub>O Nash-MTL cai na segunda classe. Ele muda a direção da atualização, tratando a combinação dos gradientes como uma barganha cooperativa entre as tarefas: cada tarefa tem uma utilidade, que é a redução da perda dela, e a direção escolhida é a que maximiza o produto dessas utilidades, o que evita que uma domine a outra. A garantia é convergência para um ponto Pareto-estacionário, que é condição necessária e não suficiente para otimalidade de Pareto; a otimalidade exigiria uma hipótese de convexidade que uma rede profunda não satisfaz. Agora a parte que eu preciso dizer com cuidado. O Capítulo 3 adotou o Nash porque, na comparação dele, contra o PCGrad e contra não usar balanceador nenhum, ele deu a menor perda multitarefa combinada. Isso é conclusão do tempo dele, enfraquecida depois por um achado sobre a implementação do otimizador. O critério da Seção 2 continua de pé: um balanceador só é útil se melhorar sobre uma ponderação fixa bem ajustada.</sub>

---

## S23 · The null result
`slide **16** · PDF p.20` · **70 s *(medido)*** · fim previsto **15:11**

> ### ▶ O resultado. Eu prefiro mostrá-lo a afirmá-lo, então são as duas tabelas do capítulo, reduzidas ao bloco de F1.

**● COBRE** — INTRODUZ o resultado nulo do Cap. 3 · RETOMA o mapa de métodos externos de 2.6

**✕ NUNCA** — "ambas as baselines externas batidas em absoluto" (vale só na tarefa estática; · na sequencial o MHA+PE lidera Community, Food e Shopping). · Nunca "supera": não há teste pareado neste capítulo. · Nenhum número do Cap.

<sub>O resultado. Eu prefiro mostrá-lo a afirmá-lo, então são as duas tabelas do capítulo, reduzidas ao bloco de F1. À esquerda, a tarefa estática: os nossos dois modelos ficam acima da HMRM em todas as categorias. À direita, a tarefa sequencial, e é aqui que está o ponto: as lideranças se dividem. O MHA+PE fica com a melhor F1 em Community, Food e Shopping; o nosso multitarefa, em Nightlife e Travel; o de tarefa única, em Entertainment e Outdoors. E a comparação que interessa é entre as nossas duas colunas, que é a comparação entre multitarefa e dedicado. A conclusão é a do próprio capítulo, e está na tela: largamente comparáveis, sem vantagem clara ou consistente para o arranjo multitarefa nestes experimentos. Boa parte dessas diferenças cai dentro do desvio padrão entre partições. E uma precisão que evita a comparação errada mais tarde: isto é F1 por categoria, a convenção dos Capítulos 3 e 4, e não é a macro-F1 do Capítulo 5.</sub>

---

## S24 · The null result: three possible causes
`slide **17** · PDF p.21` · **40 s *(medido)*** · fim previsto **15:51**

> ### ▶ É aqui que o capítulo deixa de ser um resultado negativo e vira um programa de trabalho, porque ele nomeia três suspeitos, e não um.

**● COBRE** — INTRODUZ a bifurcação de três hipóteses

**✕ NUNCA** — transferência negativa como algo observado. · Nunca dar a um dos três suspeitos precedência que o capítulo não dá.

<sub>É aqui que o capítulo deixa de ser um resultado negativo e vira um programa de trabalho, porque ele nomeia três suspeitos, e não um. Dissimilaridade das tarefas: o tronco compartilhado teria sido forçado a uma representação de compromisso, não especializada para nenhuma das duas. Insuficiência da representação: ela não seria rica o bastante para codificar propriedade semântica e dinâmica sequencial ao mesmo tempo. Rigidez da topologia: um único bloco compartilhado seria restritivo demais. Uma precisão sobre o rodapé, que eu faço questão de dizer: a transferência negativa foi hipotetizada aqui, não foi observada.</sub>

---

## S25 · Three possible causes do not close the investigation
`slide **18** · PDF p.22` · **20 s** · fim previsto **16:11**

> ### ▶ Três causas possíveis não encerram a investigação: elas desenham o próximo experimento.

**● COBRE** — RETOMA a bifurcação de 3.5 - ⚠ \specialframe sem \frametitle — o extrator do SPEECH não alcança este bloco e nunca vai alcançar. O cartão é emitido com sem página, e o texto só se confere lendo o corpo do frame. Foi assim que este

**✕ NUNCA** — que o próximo capítulo responde os três suspeitos. · Ele condena um.

<sub>Três causas possíveis não encerram a investigação: elas desenham o próximo experimento. Congelar a arquitetura e mover apenas a entrada.</sub>

---


# ST-MTLNet — Cap. 4 (CoUrb)


## S26 · Architecture or representation?
`slide **19** · PDF p.24` · **60 s *(medido)*** · fim previsto **17:11**

> ### ▶ O segundo estudo pega a pergunta herdada e a transforma em experimento controlado.

**● COBRE** — INTRODUZ o desenho controlado do Cap. 4 · RETOMA MTLnet e FiLM de 3.2, e Nash-MTL de 3.3B

**✕ NUNCA** — ampliar crédito de autoria. · A linha do divisor é a redação da própria Introdução entregue, e não se acrescenta nada a ela.

<sub>O segundo estudo pega a pergunta herdada e a transforma em experimento controlado. O gargalo é a representação, ou é a topologia de compartilhamento? Para separar as duas, ele mantém o MTLnet sem alterar uma linha: o mesmo tronco, a mesma modulação FiLM, o mesmo balanceador de gradientes, os mesmos hiperparâmetros. Só a entrada se move. A entrada antiga é o embedding monolítico de 64 dimensões do DGI; a nova é a concatenação de três codificadores, de 64 dimensões cada, o que dá 192. Vou por partes.</sub>

---

## S27 · HGI
`slide **20** · PDF p.25` · **55 s** · fim previsto **18:06**

> ### ▶ O segundo mecanismo, e ele é o mesmo objetivo subindo uma hierarquia.

**● COBRE** — INTRODUZ o mecanismo do HGI · RETOMA a ideia infomax de 2.1 e o degrau do HGI em 2.7

**✕ NUNCA** — introduzir o Check2HGI aqui, que é do Cap. · Nunca Space2Vec nem POI2Vec como componentes deste trabalho.

<sub>O segundo mecanismo, e ele é o mesmo objetivo subindo uma hierarquia. Um codificador de categoria dá as features iniciais, uma convolução sobre o grafo de Delaunay acrescenta vizinhança, a atenção junta os lugares de uma região, as regiões conversam entre si, e uma soma ponderada pela área fecha na cidade. As comparações contrastivas acontecem em duas fronteiras: lugar contra região, e região contra cidade. E duas consequências, sendo que a segunda está na tela. A primeira é a que explica o resultado do próximo capítulo: o vetor de um lugar já carrega a região a que ele pertence. A segunda é a ressalva: o HGI foi construído para representar regiões urbanas, e eu uso aqui a saída de nível de lugar dele para predição sequencial -- um uso que a avaliação original não cobre.</sub>

---

## S28 · Why these encoders
`slide **21** · PDF p.26` · **90 s *(medido)*** · fim previsto **19:36**

> ### ▶ Por que estes codificadores, e não outros quaisquer.

**● COBRE** — INTRODUZ SIREN, Sphere2Vec-M, Time2Vec e o canal categórico em duas fases

**✕ NUNCA** — Space2Vec ou POI2Vec como componentes deste trabalho. · Eles são arte prévia, e não estão no registro de termos.

<sub>Por que estes codificadores, e não outros quaisquer. O canal espacial existe porque o MTLnet codificava espaço só implicitamente, pela topologia do grafo, e nunca como coordenada contínua. O estudo compara dois com hipóteses diferentes: o SIREN, que modela uma função contínua das coordenadas normalizadas com ativações senoidais, e o Sphere2Vec-M, que é multiescala e opera direto em coordenadas esféricas, preservando propriedades de distância geodésica. Os dois são treinados com a mesma perda contrastiva sobre distância geográfica, com par abaixo de dez quilômetros como positivo e acima de setenta como negativo, e é isso que faz a comparação isolar a arquitetura. O canal temporal existe porque o MTLnet não tinha representação temporal nenhuma, e o Time2Vec combina um termo linear, de tendência global, com termos senoidais, para os padrões cíclicos de hora do dia e dia da semana. O canal categórico existe porque o DGI codificava categoria pela estrutura do grafo, sem capturar relação hierárquica ou regional entre elas, e ele vem em duas fases. Primeiro um codificador de lugar, que aprende coocorrência entre categorias a partir de caminhadas aleatórias sobre o grafo espacial, com amostragem negativa e um termo que amarra cada classe fina à categoria de topo dela. Depois o HGI, que acrescenta a hierarquia regional sobre esse resultado.</sub>

---

## S26b · Architecture or representation? (a arte)
`slide **22** · PDF p.27` · **18 s *(medido)* · ⚠ **deixou de ser 0 s**** · fim previsto **19:54**

> ### ▶ E aqui está tudo junto, dentro do modelo que não mudou.

**● COBRE** — RETOMA a Fig. 2 do Cap. 4 (arte reproduzida). INTRODUZ nada.

**✕ NUNCA** — nada de novo aqui. · O Task stamp é mandato da regra §8.5 (arte reproduzida dos Caps. · 3/4).

<sub>E aqui está tudo junto, dentro do modelo que não mudou. Os encoders de tarefa projetam qualquer entrada para a mesma largura latente de 256 nos dois braços, e é esse congelamento que faz o resultado ser diagnóstico, e não apenas melhor.</sub>

---

## S30 · The diagnostic result is the sequential task
`slide **23** · PDF p.28` · **100 s *(medido)*** · fim previsto **21:34**

> ### ▶ Antes dos números, a ressalva, porque ela decide como ler a tabela da esquerda: depois da publicação nós estabelecemos que a entrada da tarefa estática contém o rótulo qu…

**● COBRE** — INTRODUZ o resultado sequencial do Cap. 4

**✕ NUNCA** — "macro-F1". · Nunca "supera": este capítulo não tem teste pareado. · Nenhum número do Cap. · 5 nesta tela.

<sub>Antes dos números, a ressalva, porque ela decide como ler a tabela da esquerda: depois da publicação nós estabelecemos que a entrada da tarefa estática contém o rótulo que ela prediz. A feature de tipo de local mapeia um-para-um nas sete categorias. Então os números da esquerda medem uma consulta, não inferência semântica aprendida. O resultado diagnóstico é o da direita, a tarefa sequencial, cujo alvo nunca está na entrada. Na tela está a Flórida, com os três modelos lado a lado; Califórnia e Texas eu tenho prontos se a banca quiser. O cenário aqui é mais heterogêneo do que na tarefa estática, e continua favorável à entrada decomposta. Contando o melhor dos dois codificadores espaciais por combinação, os modelos espaço-temporais ficam com a média mais alta em quinze das vinte e uma combinações de categoria e estado, e o MTLnet, com a entrada original, retém seis. Uma dessas seis o capítulo chama, nas palavras dele, de um empate técnico adicional: é Outdoors na Flórida, onde a média do MTLnet fica dois centésimos de ponto percentual acima da melhor variante, dentro de um desvio padrão. Os maiores ganhos estão em Food, em que as duas variantes ficam acima nos três estados. E de novo a precisão: isto é F1 por categoria, não é macro-F1.</sub>

---

## S31 · Three limits of the decomposition
`slide **24** · PDF p.29` · **84 s *(medido)*** · fim previsto **22:58**

> ### ▶ Três limites, e eu ofereço os três antes que me peçam.

**● COBRE** — INTRODUZ os três limites declarados do Cap. 4

**✕ NUNCA** — "pareado em largura". · Deixar o ganho estático falar pela sequencial. · Ampliar crédito de autoria.

<sub>Três limites, e eu ofereço os três antes que me peçam. O primeiro é o Travel, e ele precisa de rótulo de tarefa, senão a sala se confunde: Travel na classificação de categoria melhora, Travel na próxima categoria não. Na tarefa sequencial o MTLnet mantém a liderança na Flórida, e a razão está escrita no capítulo: movimento de longa distância é esparso, e a topologia de grafo preserva relação entre lugares geograficamente distantes melhor do que um codificador baseado em coordenada. O segundo limite é que não existe codificador espacial universalmente melhor. O SIREN se destaca mais na Flórida e na Califórnia, o Sphere2Vec-M no Texas, e a adequação depende de como os lugares se distribuem em cada território. O terceiro é o que eu esperaria que a banca perguntasse, então eu digo primeiro: a comparação não é pareada em largura. São 192 dimensões contra 64. O capítulo declara isso como limite e pede um controle de dimensão equalizada, e esse controle nunca foi executado. Eu não vou defender o ponto: parte do ganho pode vir da largura. Junto com isso, os três componentes entram sempre juntos, então este capítulo não isola a contribuição de cada codificador.</sub>

---

## S32 · Freeze the architecture, move only the input
`slide **25** · PDF p.30` · **35 s** · fim previsto **23:33**

> ### ▶ Com a arquitetura fixa, a entrada moveu o resultado: a representação é o gargalo.

**● COBRE** — RETOMA o gargalo · INTRODUZ as três camadas que o Cap. 5 reconstrói (representação · topologia · protocolo)

**✕ NUNCA** — que a correção de um vazamento foi o pivô. · A direcionalidade das arestas entra em S37, como princípio de projeto, na redação do próprio Cap.

<sub>Com a arquitetura fixa, a entrada moveu o resultado: a representação é o gargalo. Mas o diagnóstico ainda é em nível de lugar, sob um protocolo que deixa o mesmo usuário dos dois lados da divisão. O terceiro estudo reconstrói as três camadas: representação, topologia e protocolo.</sub>

---


# Check2HGI — Cap. 5 (MobiWac)


## S33 · Three changes, each a consequence of the diagnosis
`slide **26** · PDF p.32` · **60 s** · fim previsto **24:33**

> ### ▶ As três mudanças do último estudo, e nenhuma delas é preferência minha: as três são consequência do diagnóstico do capítulo anterior.

**● DIZER EXATO**
- usuários disjuntos
- o par de tarefas muda

**✕ NUNCA** — creditar qualquer uma das três mudanças a uma correção de vazamento. · "Prevê o próximo lugar".

<sub>As três mudanças do último estudo, e nenhuma delas é preferência minha: as três são consequência do diagnóstico do capítulo anterior. A representação sai do nível de lugar para o nível de check-in, porque um vetor por lugar não distingue um almoço de quarta-feira de uma noite de sábado no mesmo lugar. A topologia sai do compartilhamento rígido para atenção cruzada entre as duas tarefas, com um caminho espacial privado na saída de região. E o protocolo sai do estratificado por amostra para validação cruzada com **usuários disjuntos**, quatro sementes, e testes fixados antes de qualquer resultado ser lido. Aqui eu cumpro o aviso que dei na Seção 2: **o par de tarefas muda**. Com uma entrada por visita, a classificação estática vira um par pouco natural, e o par passa a ser próxima categoria mais próxima região, dois alvos finais sequenciais. A restrição da abertura continua valendo: um artefato, uma passagem, duas respostas.</sub>

---

## S34 · Next region: the task, and why it is worth predicting
`slide **27** · PDF p.33` · **52 s *(medido)*** · fim previsto **25:25**

> ### ▶ Trabalho relacionado deste estudo, que os dois primeiros não têm, e a primeira metade é a tarefa nova.

**● COBRE** — INTRODUZ a tarefa de próxima região e as suas motivações · RETOMA o eixo meio × fim de 2.6 e as contagens de região da Tab. 8 (2.3)

**# NÚMEROS** — 520 em Istambul a 8.501 na Califórnia. Ela

**✕ NUNCA** — especulação sobre erro geográfico ou desempenho de serviço (§8 regra 16). · Afirmação de ineditismo mais forte que a entregue, que é escopada a "to our knowledge" e "underexplored".

<sub>Trabalho relacionado deste estudo, que os dois primeiros não têm, e a primeira metade é a tarefa nova. O alvo é a região --- de 520 em Istambul a 8.501 na Califórnia. Ela cobre uma área maior que um lugar, então é um alvo mais fácil do que o lugar exato. Mas a tarefa não é fácil. Prever sobre uma partição do mapa é a formulação padrão em mobilidade, com célula de grade como alvo; aqui entra no lugar dela a unidade administrativa de bairro. E onde a área já modela várias granularidades, categoria e região aparecem como sinais auxiliares de um alvo principal de próximo lugar. Eu estudo o par como objeto. O escopo vai junto com a motivação: preparação em nível de bairro, e nenhum serviço construído ou avaliado aqui.</sub>

---

## S35 · Why a per-visit representation is new in this line
`slide **28** · PDF p.34` · **49 s *(medido)*** · fim previsto **26:14**

> ### ▶ Segunda metade: por que uma representação por visita é nova nesta linha.

**● COBRE** — INTRODUZ CTLE como a arte prévia mais próxima · RETOMA a escada de representações de 2.7

**✕ NUNCA** — que o CTLE foi superado aqui. · O número do CTLE fica em S45, e o que ele estabelece é uma ordenação entre famílias de representação.

<sub>Segunda metade: por que uma representação por visita é nova nesta linha. A arte prévia mais próxima é o CTLE, que também dá um vetor por visita, aprendido mascarando e reconstruindo partes da sequência de check-ins do usuário. A diferença é de construção. O CTLE é um modelo de sequência, um Transformer que lê a própria sequência; o Check2HGI continua um modelo de grafo, com a mesma hierarquia de lugar, região e cidade e o mesmo objetivo infomax, agora um nível mais fundo. E o CTLE pré-treina só sobre identificador de lugar e marca de tempo, então o vocabulário de categoria nunca entra no treino dele. A novidade que eu reivindico é a combinação.</sub>

---

## S36 · Check2HGI: a fourth level below the place
`slide **29** · PDF p.35` · **80 s** · fim previsto **27:34**

> ### ▶ O Check2HGI, e ele se apoia direto no HGI do capítulo anterior.

**● DIZER EXATO**
- um quarto nível abaixo do lugar
- o grafo nunca vê a próxima categoria nem a próxima região

**# NÚMEROS** — auxiliares pequenos, de pesos 0,3 e 0,1, e

**✕ NUNCA** — nenhum p-valor nesta subseção. · "Substrate" (palavra de repositório).

<sub>O Check2HGI, e ele se apoia direto no HGI do capítulo anterior. O HGI tinha três níveis: lugar, região e cidade. O Check2HGI acrescenta **um quarto nível abaixo do lugar**, que é o próprio check-in. As arestas ligam cada nível ao de cima, ligam lugares próximos no nível de lugar, e ligam os check-ins consecutivos de um mesmo usuário, com um peso que decai conforme o intervalo entre as visitas cresce. Duas visitas ao mesmo lugar se encontram pelo nó de lugar, um nível acima. O treino é o objetivo infomax da Seção 2, agora um nível mais fundo: cada vetor aprende a reconhecer a vizinhança verdadeira e a rejeitar uma embaralhada. Junto com ele vão dois termos auxiliares pequenos, de pesos 0,3 e 0,1, e nenhum dos dois usa rótulo. Este é o ponto que eu quero deixar assentado antes de qualquer resultado: **o grafo nunca vê a próxima categoria nem a próxima região**. E do grafo treinado saem duas tabelas: um vetor de 64 dimensões por visita, do nível de check-in, e um vetor de 64 dimensões por região, do nível de região. São essas duas tabelas que o modelo da próxima tela vai ler.</sub>

---

## S37 · What each visit contributes
`slide **30** · PDF p.36` · **70 s** · fim previsto **28:44**

> ### ▶ O que cada visita contribui na entrada, e é aqui que está a informação que um vetor por lugar não consegue carregar.

**● COBRE** — INTRODUZ as features de nó por visita · INTRODUZ a aresta só para frente, como princípio de projeto

**✕ NUNCA** — a aresta só para frente como conserto, correção ou descoberta. · Ela é decisão de projeto que o documento explica. · Se perguntarem por que a direcionalidade importa, a resposta é o princípio; · se alguém perguntar por um episódio de correção no repositório, é o slide B2, com a proveniência primeiro.

<sub>O que cada visita contribui na entrada, e é aqui que está a informação que um vetor por lugar não consegue carregar. Três grupos. O semântico: a categoria do lugar visitado, como indicador sobre as classes. O tempo cíclico: hora do dia e dia da semana pelo seno e pelo cosseno, para que o fim e o começo de cada ciclo fiquem vizinhos, e não em pontas opostas de uma escala. E os tempos decorridos: o intervalo desde a visita anterior e o intervalo desde a primeira visita daquele usuário, os dois comprimidos por logaritmo, mais o intervalo dentro do mesmo dia e um indicador de primeira visita. É isso que dá ritmo à representação: distinguir a visita que vem minutos depois da anterior daquela que abre um passeio novo. E aqui um princípio de projeto, na redação do próprio capítulo: as arestas entre visitas consecutivas correm numa direção só, da visita anterior para a posterior. A razão está na mesma frase: o alvo é predito do passado do usuário, então a representação é construída só do passado. Todo valor é medido até a própria visita.</sub>

---

## S39 · The architecture: sharing by exchange
`slide **31** · PDF p.37` · **74 s *(medido)*** · fim previsto **29:58**

> ### ▶ A arquitetura, e o que mudou no multitarefa. Cada tarefa tem a sua entrada.

**● DIZER EXATO**
- por troca de informação entre as duas tarefas

**✕ NUNCA** — creditar transferência entre tarefas a partir desta tela. · "Backbone", "dual-tower", o identificador de repositório do modelo.

<sub>A arquitetura, e o que mudou no multitarefa. Cada tarefa tem a sua entrada. A de categoria lê a janela de vetores por visita, que é o fluxo semântico. A de região lê a mesma janela de visitas, só que cada visita agora representada pelo vetor treinado do nó de região dela, que é o fluxo espacial. As duas passam por encoders privados, sem peso nenhum compartilhado. E o tronco compartilhado é uma pilha de dois blocos de atenção cruzada: em cada bloco a atenção deixa um fluxo ler as features do outro, enquanto cada um mantém os próprios pesos feed-forward. É esta a frase que eu quero que fique da tela: as tarefas compartilham **por troca de informação entre as duas tarefas**, e não por possuírem camadas ocultas em comum. Comparem com o Capítulo 3, onde tudo atravessava um tronco único e as tarefas só se separavam nas saídas. É a mesma família de modelos, com a topologia de compartilhamento trocada, e a topologia era um dos três suspeitos do nulo.</sub>

---

## S40 · The private spatial path
`slide **32** · PDF p.38` · **90 s** · fim previsto **31:28**

> ### ▶ Duas coisas fecham a arquitetura, e depois uma posição que eu preciso enunciar com precisão.

**● DIZER EXATO**
- dentro do mesmo modelo
- modelo dedicado de categoria recebe o mesmo ajuste

**✕ NUNCA** — "não podemos provar que não contribuiu, portanto provavelmente contribuiu". · Creditar Texas e Califórnia a transferência entre tarefas. · Nenhuma afirmação de Pareto sobre estes modelos.

<sub>Duas coisas fecham a arquitetura, e depois uma posição que eu preciso enunciar com precisão. A primeira é o caminho espacial privado: a saída de região tem, além do tronco, um ramo pequeno **dentro do mesmo modelo**, e não um segundo modelo, que lê a janela espacial e contorna o tronco. A tarefa de categoria não toca nesse ramo. A segunda é a perda: uma soma de peso fixo, meio a meio entre as duas tarefas, e o peso é fixo **de propósito**, para que qualquer melhora sobre os dedicados venha da representação compartilhada e não de um esquema adaptativo de ponderação. A saída de categoria treina com ajuste de logit, que empurra a fronteira de decisão para o posterior balanceado que a macro-F1 premia, e o **modelo dedicado de categoria recebe o mesmo ajuste**, então a comparação entre os dois não é afetada por ele. Agora a posição. A evidência aqui **não separa** as contribuições do tronco compartilhado e do caminho espacial privado. Ela não estabelece que o compartilhamento ajuda, e não o descarta. A afirmação que eu faço é sobre o desenho: esta combinação produz uma saída de região acima de dois modelos dedicados, nos dois conjuntos com os maiores números de regiões. Não é uma afirmação sobre transferência entre tarefas.</sub>

---

## S41 · Protocol, step 1 of 4: the unit of data
`slide **33** · PDF p.39` · **75 s *(medido)*** · fim previsto **32:43**

> ### ▶ O protocolo, em quatro passos, e de cada um eu digo a razão.

**● COBRE** — INTRODUZ o split disjunto por usuário e as janelas sobrepostas de passo 1 · RETOMA o protocolo estratificado por amostra de 2.5

**✕ NUNCA** — "as mesmas janelas" para os três estudos. · "Fold" como palavra solta na fala: a superfície em português é partição.

<sub>O protocolo, em quatro passos, e de cada um eu digo a razão. Primeiro, a unidade de dado. Validação cruzada de cinco partições, disjunta por usuário: todas as janelas de uma pessoa ficam do mesmo lado da divisão. Isso é o reparo direto da limitação que o Capítulo 3 declarou, em que os check-ins de um mesmo usuário caíam dos dois lados. E uma ressalva que eu dou antes de alguém pedir: a partição retida é a que serve de validação, e eu não reservo uma terceira divisão. É dela que sai o segundo limite que eu apresento no fim desta seção.</sub>

---

## S42 · Protocol, step 2 of 4: what is measured
`slide **34** · PDF p.40` · **101 s *(medido)*** · fim previsto **34:24**

> ### ▶ Segundo, o que se mede.

**● COBRE** — INTRODUZ Acc@10, o desconto OOD e o piso de Markov-1 · RETOMA macro-F1 e o piso de classe majoritária de 2.4

**✕ NUNCA** — Acc@10 sem o desconto OOD. · Nenhum número sem o seu ponto de referência.

<sub>Segundo, o que se mede. Em categoria, macro-F1, e a razão é a distribuição: na Flórida, um preditor que sempre responde a categoria mais comum acerta vinte e quatro vírgula sete por cento das visitas e ainda assim marca cinco vírgula sete de macro-F1. É por isso que acurácia simples não é a métrica aqui: ela premiaria exatamente esse preditor. Em região, acurácia em dez, a fração de visitas cuja região verdadeira está entre as dez mais pontuadas. E eu digo o que ela não faz: não separa o primeiro lugar do décimo. Região ausente do treino conta como erro. Os pontos de referência são o modelo dedicado e o piso de Markov.</sub>

---

## S43 · Protocol, step 3 of 4: what is compared
`slide **35** · PDF p.41` · **99 s *(medido)*** · fim previsto **36:03**

> ### ▶ Terceiro, o que se compara. O modelo conjunto contra os dedicados, com a mesma representação, as mesmas janelas e as mesmas partições.

**● COBRE** — INTRODUZ a semente como unidade de repetição, os vinte modelos ajustados, a unidade inferencial n = 4 e a convenção joint-best

**✕ NUNCA** — "n = 20 repetições pareadas". · Misturar joint-best com a leitura por tarefa dos Caps. · 3 e 4 sem declarar. · "As mesmas partições" entre sementes: vale dentro de uma semente.

<sub>Terceiro, o que se compara. O modelo conjunto contra os dedicados, com a mesma representação, as mesmas janelas e as mesmas partições. E a convenção que decide qual número eu reporto: os dois resultados saem de um único modelo salvo por partição, escolhido pela média geométrica das duas métricas. Eu digo isso com todas as letras porque ela me custa caro: a convenção alternativa, ler cada tarefa na melhor época dela, é mais favorável ao modelo conjunto, e transformaria mais quatro células de categoria e mais duas de região em melhorias que sobrevivem à mesma correção. Eu escolhi a que produz menos vitórias, porque é a única que um sistema implantado consegue servir.</sub>

---

## S44 · Protocol, step 4 of 4: how it is decided
`slide **36** · PDF p.42` · **135 s *(medido)*** · fim previsto **38:18**

> ### ▶ Quarto, como se decide, e o ponto é que um ganho afirmado e uma paridade afirmada exigem testes diferentes.

**● COBRE** — INTRODUZ o teste pareado de superioridade, o TOST na margem registrada, a correção de Holm e o desvio declarado do Wilcoxon

**✕ NUNCA** — apresentar o desvio como confissão. · Aplicar a margem de dois pontos ao eixo de categoria. · "Significativo" sem nomear o teste.

<sub>Quarto, como se decide, e o ponto é que um ganho afirmado e uma paridade afirmada exigem testes diferentes. Para próxima categoria, superioridade: eu pergunto se o conjunto é melhor. Para próxima região, não-inferioridade, com margem de dois pontos registrada antes de qualquer resultado ser lido: eu pergunto se ele não é pior. Isso importa porque ausência de significância não é evidência de igualdade — dizer 'não deu diferença, logo empatou' é formalmente inválido, e é a prática corrente na literatura de multitarefa. O plano foi escrito antes. Teste t pareado, intervalo de noventa por cento, correção de Holm sobre os seis conjuntos. E um desvio declarado: o plano registrava Wilcoxon, e com quatro sementes o Wilcoxon exato não desce abaixo de zero vírgula zero seiscentos e vinte e cinco. Ele não podia decidir nada. Continua reportado ao lado, como sensibilidade, com os dois testes no código publicado. E o asterisco que está na tela: o protocolo estatístico foi refinado depois, com base na literatura. É posterior ao que a banca recebeu, e não muda nenhum veredito.</sub>

---

## S45 · Result 2: the representation, at every dataset
`sem página` · **48 s *(medido)*** · fim previsto **39:06**

> ### ▶ Segundo resultado, e é o mais controlado da dissertação: só a entrada muda.

**● COBRE** — INTRODUZ o resultado de representação (Tab. 9) e os dois controles · RETOMA CTLE de 5.2A

**✕ NUNCA** — "o nível de check-in bate o de lugar nos seis" no sentido de teste: o teste separa em cinco. · Nunca generalizar a cláusula do capítulo "under a tenth of the place-to-check-in gap": ela é dita por estado, e generalizá-la é aritmeticamente falso contra a própria Tabela 9, na mesma página. · Nunca chamar a diferença de representação de "margem".

<sub>Segundo resultado, e é o mais controlado da dissertação: só a entrada muda. Mesmo alvo, mesmo modelo, mesma configuração de treino, mesmas partições, mesmas janelas. A coluna da esquerda é a representação em nível de check-in, a do meio é o embedding por lugar, e a da direita é a diferença. Ela é positiva nos seis conjuntos, de mais zero vírgula vinte e três na Flórida a mais seis vírgula vinte e nove em Istambul. O desvio ao lado é entre as cinco partições, com semente zero. Um teste pareado separa as duas colunas em cinco dos seis conjuntos; a Flórida é a exceção, com p igual a zero vírgula zero sete.</sub>

---

## S46 · Result 3: one model, two tasks
`sem página` · **195 s *(medido)*** · fim previsto **42:21**

> ### ▶ Segundo resultado, e é o que decide a tese. Duas tabelas, uma por tarefa: à esquerda a categoria, à direita a região, com três sistemas externos.

**● COBRE** — INTRODUZ a Tab. 10 e os resultados dos métodos externos do Cap. 5 · RETOMA o mapa de métodos de referência de 2.6

**✕ NUNCA** — "empata", "matches", "ties", "em todos os conjuntos supera". · "Beats" ou "wins" para os métodos externos: o verbo é excede. · Nunca um número do Cap. · 3 nesta tela.

<sub>Segundo resultado, e é o que decide a tese. Duas tabelas, uma por tarefa: à esquerda a categoria, à direita a região, com três sistemas externos. Primeiro a comparação limpa. Em categoria, o conjunto fica pelo menos três vírgula zero seis pontos acima do POI-RGNN nos seis conjuntos, e o POI-RGNN é nativo da tarefa. Em região, fica acima do melhor externo de cada conjunto, também nos seis. Agora a ressalva de protocolo, porque os três não chegam em pé de igualdade. Só o HMT-GRN roda nos nossos dados, nas nossas partições e nas nossas inicializações. O STAN roda nas nossas partições mas constrói as próprias representações e as próprias sequências, e em dois conjuntos com partições incompletas. O ReHDM roda sob o protocolo publicado dele. E agora a coisa mais interessante do capítulo, e ela é contra eles, não a meu favor: o piso de Markov de primeira ordem, uma tabela de transição sem aprendizado nenhum, fica acima desses três sistemas na maioria dos conjuntos — acima do HMT-GRN nos seis. É por isso que eu trato o piso, e não os externos, como a referência que a próxima região tem de exceder. O conjunto excede o piso por quatro vírgula um a dez pontos. Os números vêm de quatro sementes por cinco partições; a dispersão e os intervalos estão no próximo slide, que é onde o veredito é decidido.</sub>

---

## S47 · The verdict, dataset by dataset
`slide **39** · PDF p.45` · **121 s *(medido)*** · fim previsto **44:22**

> ### ▶ E este é o veredito, com o intervalo de cada diferença.

**● DIZER EXATO**
- próxima região
- permanece dentro da margem de dois pontos
- déficits, não empates
- próxima categoria
- supera na Flórida
- não resolvidas

**# NÚMEROS** — dedicado no Texas, mais 1,21, e na Califórnia · e na Califórnia, mais 1,06; nos dois, as · os p corrigidos são 0,00013 e menos de · quero evitar: Alabama menos 0,87; Arizona menos 0,44

**✕ NUNCA** — "empata", "matches", "ties", "em todos". · Aplicar a margem de dois pontos ao eixo de categoria, ou meio ponto ao eixo de região. · Chamar as quatro diferenças dentro da margem de empates. · Dizer que uma diferença "exclui zero" sem dizer para que lado.

<sub>E este é o veredito, com o intervalo de cada diferença. Na **próxima região**, o modelo conjunto **supera** o dedicado no Texas, mais 1,21, e na Califórnia, mais 1,06; nos dois, as vinte partições favorecem o conjunto, e os p corrigidos são 0,00013 e menos de dez elevado a menos quatro. Nos outros quatro conjuntos ele **permanece dentro da margem de dois pontos**, registrada antes de qualquer resultado ser lido. E eu enuncio os quatro, porque citar três e omitir Istambul seria justamente o erro que eu quero evitar: Alabama menos 0,87; Arizona menos 0,44; Flórida menos 0,16; Istambul menos 0,08. Os quatro são **déficits, não empates**, e os quatro intervalos ficam inteiramente abaixo de zero. A direção é declarada, não arredondada. Na **próxima categoria**, ele **supera na Flórida**, mais 0,19, com p corrigido de 0,011 e dezenove das vinte partições a favor. As outras cinco são **não resolvidas**, e elas não apontam para o mesmo lado: Istambul, mais 0,08, exclui zero a favor do conjunto; Texas, menos 0,13, e Alabama, menos 0,19, excluem zero a favor do dedicado; Arizona e Califórnia ficam sobre o zero. Nenhuma das cinco sobrevive a Holm. O que se pode dizer sobre magnitude vem dos intervalos: o mais largo alcança 0,34 de ponto a partir de zero, no Alabama, e isso limita as seis diferenças de categoria a **meio ponto de zero de uma vez só**. Duas últimas coisas, ditas por mim antes de serem pedidas. Os dois ganhos de região são **resultados secundários, fora do plano registrado**. E Istambul, o único conjunto fora dos Estados Unidos, fica a menos de um décimo de ponto nos dois eixos, que é o teste de validade externa deste capítulo.</sub>

---

## S48 · Limitations and trade-offs
`slide **40** · PDF p.46` · **119 s *(medido)*** · fim previsto **46:21**

> ### ▶ A troca, medida, e depois quatro limites que eu ofereço antes de alguém pedir.

**● DIZER EXATO**
- operacional, não aritmético
- todo escore absoluto que eu reportei é otimista

**# NÚMEROS** — capítulo reporta cerca de 4,2 milhões no Alabama · milhões no Alabama contra 1,85 milhão dos dois · dois dedicados somados, e 5,2 contra 2,8 na · 2,8 na Califórnia. São 2,3 vezes e 1,8

**✕ NUNCA** — repetir a razão de parâmetros como se tivesse sido re-medida, e nunca citar uma recontagem. · Se a pergunta vier, a resposta é que a razão de parâmetros não foi re-medida. · Nunca citar as duas porcentagens de parâmetros impressas no Apêndice G do suplemento: elas estão erradas, e o assunto é do slide B3.

<sub>A troca, medida, e depois quatro limites que eu ofereço antes de alguém pedir. A troca primeiro: o modelo conjunto é **maior**. O capítulo reporta cerca de 4,2 milhões no Alabama contra 1,85 milhão dos dois dedicados somados, e 5,2 contra 2,8 na Califórnia. São 2,3 vezes e 1,8 vezes; uma passagem custa mais computação do que rodar os dois modelos pequenos. O que o modelo único entrega é **operacional, não aritmético**: um artefato para treinar, versionar e implantar, e uma passagem cujas entradas produzem as duas respostas de uma vez. E os quatro resultados de região dentro da margem são déficits pequenos, o maior deles 0,87 no Alabama: é uma troca medida, não uma substituição de graça. Os quatro limites. Primeiro: a representação é treinada uma vez sobre todos os lugares; uma reconstrução por partição, só com usuários de treino, mudou os resultados em no máximo 0,33 de acurácia em dez e 0,29 de macro-F1, em três conjuntos e numa semente, e a metade de categoria dessa verificação cobre de 67 a 87 por cento dos dados de validação. Segundo: a seleção de época consulta a mesma partição em que a nota é depois lida, então **todo escore absoluto que eu reportei é otimista**; a comparação entre conjunto e dedicado é bem menos afetada, porque a regra é a mesma para os dois nas mesmas partições e porque o dedicado de categoria recebe a busca mais ampla, mas daí não segue que o viés se cancele exatamente. Terceiro: eu não construo nem avalio serviço nenhum. Quarto: cada nó de visita se apoia só nas visitas que o precedem, e o grafo não passa informação de uma visita posterior para uma anterior, nem no treino nem na leitura.</sub>

---


# CONCLUSÃO — a resposta condicional


## S49 · Three studies, three layers
`slide **41** · PDF p.48` · **30 s** · fim previsto **46:51**

> ### ▶ Uma tela em que a coletânea inteira cabe. Três linhas, os três estudos.

**● COBRE** — INTRODUZ a leitura conjunta dos três estudos lado a lado | RETOMA a linhagem de 2.1 e as três camadas de 5.1

**✕ NUNCA** — nenhum número nesta tela, em nenhuma célula. · Nenhum "fomos de X para Y" atravessando protocolos (§8 regra 7). · Nunca "supera" nesta tela: a licença é por célula de resultado, e aqui não há resultado.

<sub>Uma tela em que a coletânea inteira cabe. Três linhas, os três estudos. Três colunas, as três camadas. Mais uma quarta coluna: o que moveu. O Capítulo 3 não separou nada, e é isso que ele entrega, um nulo com três suspeitos. O Capítulo 4 manteve a arquitetura fixa de propósito, e é esse congelamento que faz a troca de entrada valer como diagnóstico. O Capítulo 5 mexeu nas três camadas. Um veredito condicional, medido sob o protocolo mais estrito dos três. O que os três estudos, juntos, estabelecem, e o que não estabelecem?</sub>

---

## S50 · The conditional answer
`slide **42** · PDF p.49` · **55 s** · fim previsto **47:46**

> ### ▶ A resposta consolidada, e ela é condicional de propósito.

**● COBRE** — RETOMA o veredito de 5.5, a pergunta de 1.3 e o protocolo disjunto por usuário de 5.4 ("o protocolo mais estrito dos três")

**✕ NUNCA** — "MTL funciona" sem condição. · Re-caminhar a cadeia dos três estudos, que acabou de estar na tela em S49. · Creditar os ganhos de região a transferência entre tarefas. · Nenhum número novo.

<sub>A resposta consolidada, e ela é condicional de propósito. O aprendizado multitarefa ajuda a previsão da próxima categoria e da próxima região sob o desenho final e o protocolo de avaliação desenvolvidos nesta dissertação. O que isso não autoriza é dizer que o multitarefa sempre ajuda: ao longo dos três estudos, relação entre tarefas e treino conjunto não bastaram por si sós. Uma condição está estabelecida por comparação controlada, e é a representação de entrada. Duas outras a evidência sugere sem isolar: a arquitetura, e a escala do conjunto de dados. Sobre escala eu sou explícito. Ela continua sendo condição possível, não causa estabelecida, por duas razões que estão no próprio texto: a ordenação não se mantém dentro do par Texas e Califórnia, e estados com mais regiões também tendem a ter mais check-ins. Identificar essas condições é o achado principal desta dissertação.</sub>

---

## S51 · Contributions
`slide **43** · PDF p.50` · **45 s** · fim previsto **48:31**

> ### ▶ A contribuição, em duas metades. A prática: um modelo, uma passagem, duas predições --- um artefato para treinar, versionar e implantar, no lugar de dois.

**● COBRE** — RETOMA a contribuição de 1.5 (§8 regra 13: segunda das duas aparições, redação idêntica)

**✕ NUNCA** — redação diferente da de S7, mesmo que melhor. · Nenhum número novo. · Nunca a razão de parâmetros como verificada: o slide diz "maior", que é o que a página imprime, e nada além.

<sub>A contribuição, em duas metades. A prática: um modelo, uma passagem, duas predições --- um artefato para treinar, versionar e implantar, no lugar de dois. O ganho é operacional, não computacional: o conjunto é o artefato maior. Mais o Check2HGI publicado, que é a parte reutilizável, e o protocolo de avaliação, liberado com o código. A científica: acima de todo sistema externo que eu rodei, nas duas tarefas; resultados de referência para a próxima região, uma tarefa que não tinha protocolo fixado; e três condições sobre quando o multitarefa ajuda --- a representação de entrada, estabelecida por comparação controlada, e a arquitetura e a escala, sugeridas e não isoladas.</sub>

---

## S52 · Limitations
`slide **44** · PDF p.51` · **105 s *(estimado — as falas dos dois slides antigos fundiram-se aqui)*** · fim previsto **50:16**

> ### ▶ As limitações, cada uma amarrada ao passo que ela pede.

**● COBRE** — INTRODUZ as SEIS limitações

**✕ NUNCA** — que o confundimento de par de tarefas foi removido; · ele é limitado pelo controle de par fixo. · ablation — o termo não está no GLOSSARY; · a superfície é "teste controlado".

<sub>As limitações, cada uma amarrada ao passo que ela pede. Eu prefiro dizê-las antes de serem perguntadas. Não são desculpas: são experimentos que alguém pode rodar. Primeira, a idade dos dados. Os cinco estados vão de janeiro de 2009 a agosto de 2011, e Istambul tem check-ins em dois blocos, 2012 a 2013 e 2017 a 2018, com cerca de sete em cada dez no bloco mais antigo. E vale dizer de quem é a limitação: a antiguidade dos dados não é só deste trabalho. Nenhum conjunto público de check-ins com trajetória de usuário passa de 2018 --- nem o Massive-STEPS, de 2025, que foi publicado para resolver exatamente isso. Segunda, a taxonomia é grossa. Sete classes de topo, e uma divisão mais fina pode mudar o efeito do treino conjunto. Terceira, e esta é a que eu mais gostaria de ver feita: a representação é transdutiva. Treinada sobre o grafo de check-ins de cada conjunto, ela não representa lugar nem usuário novo sem retreinar. O passo é uma variante indutiva, que sustentaria uso numa cidade que cresce. E, na mesma representação, dois testes controlados: variar o acoplamento com a tabela de vetores de lugar pré-treinada, e uma formulação em hipergrafo, em que uma aresta junta as várias visitas de uma sessão. ele virou "Future work". Palavras inalteradas: so mudaram de frame, porque o slide passou a carregar os seis limites. A do limite 6 e a fala do Future work ficam DEVIDAS ao gate. Quarta: eu não predigo o próximo lugar exato, então as conclusões valem para próxima categoria e próxima região. Quinta: fora dos Estados Unidos, a evidência se apoia numa cidade só. Mais cidades ampliam a base.</sub>

---

## S53 · Future work
`slide **45** · PDF p.52` · **78 s *(estimado)*** · fim previsto **51:34**

> ### ▶ Três frentes, e são as mesmas três de que a resposta depende: a representação, a topologia e a escala.

**● COBRE** — INTRODUZ os trabalhos futuros, agrupados por eixo

**✕ NUNCA** — GSM++ — o deck nunca introduziu a sigla e o §8.11 é fail-closed; · a intenção entra como attention-based graph encoders.

<sub>Três frentes, e são as mesmas três de que a resposta depende: a representação, a topologia e a escala. Duas delas o próprio trabalho classifica como apenas sugeridas --- é aí que está o espaço. Na representação, a que eu mais gostaria de ver feita: torná-la indutiva. Hoje ela não representa lugar nem usuário novo sem retreinar, e uma cidade que cresce precisa disso. Na topologia, o próximo lugar exato: a tarefa mais visível da literatura está a uma cabeça de distância da representação que já existe. E treinar os dois estágios num só --- hoje a representação é aprendida sem rótulo e depois congelada; unificar é descobrir se ela continua agnóstica quando os gradientes das tarefas chegam nela. Na escala, a que eu devo: Texas e Califórnia são os dois que ganham, os dois com mais regiões, e os dois com mais dados. Separar as duas explicações exige um experimento controlado. E há mais três que não estão na tela: uma ablação da âncora da tabela de lugares, um alvo estático que a representação não carregue como entrada, e o Check2HGI dentro de outras arquiteturas de mobilidade.</sub>

---

## S54 · Closing
`slide **46** · PDF p.53` · **50 s *(medido)*** · fim previsto **52:24**

> ### ▶ Eu abri esta apresentação dizendo que antecipar o quê e o onde da próxima visita sustenta recomendação, navegação, planejamento de transporte e alocação de recursos por área.

**● COBRE** — RETOMA as aplicações de 1.1 e a restrição de modelo único de 1.3 | fecho

**✕ NUNCA** — nenhum número novo. · Nenhum "MTL funciona" sem condição. · Nunca ler a lista de agradecimentos da tela: ela não está na tela.

<sub>Eu abri esta apresentação dizendo que antecipar o quê e o onde da próxima visita sustenta recomendação, navegação, planejamento de transporte e alocação de recursos por área. Fecho no mesmo lugar, um nível acima. O produto prático desta dissertação é um modelo único que prediz duas propriedades da próxima visita numa passagem: que tipo de lugar a pessoa vai visitar, e em que parte da cidade. E a contribuição metodológica é a sequência de evidência que levou até ele: um resultado negativo publicado, o diagnóstico que identificou a representação de entrada como o gargalo, e uma solução desenhada a partir desse diagnóstico. O resultado negativo não foi obstáculo à contribuição. Ele foi a primeira metade dela.</sub>

---

## S55 · Obrigado
`slide **47** · PDF p.54` · **30 s** · fim previsto **52:54**

> ### ▶ E antes de encerrar, os agradecimentos. Ao meu orientador, o professor Fabrício Silva, pela liberdade de explorar as minhas ideias e pela confiança para levá-las adiante.

**● COBRE** — INTRODUZ nada (fecho social)

**✕ NUNCA** — nada de resultado aqui. · É fecho social, e é o slide que fica na tela durante a arguição.

<sub>E antes de encerrar, os agradecimentos. Ao meu orientador, o professor Fabrício Silva, pela liberdade de explorar as minhas ideias e pela confiança para levá-las adiante. Ao Germano Santos, que trabalhou ao meu lado em todos os artigos deste mestrado. Ao Tarik Paiva, à Ingred Almeida e ao Pedro Augusto, pela parceria de pesquisa ao longo do caminho. À Universidade Federal de Viçosa e aos professores que fizeram parte desta formação. À minha família, que sustentou tudo isto. E, por fim, aos senhores da banca: obrigado por lerem o trabalho e por estarem aqui. Fico à disposição para as perguntas.</sub>

---
