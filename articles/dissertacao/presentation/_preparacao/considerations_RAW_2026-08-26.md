- No slide 11, podemos remover a frase "The verb law ..."
- No slide 11, onde está "two traps", mude para algo como dois adendos ou dois pontos de atenção. Eu acho que a gente
  não precisa falar sobre o fato da gente mudar as métricas no capítulo cinco, só comente a questão das mudanças das
  tarefas em si.
- No slide 12, podemos remover a frase "the pair the first ....". Ao invés de ter ela, eu acho que vale mais ter uma
  outra frase embaixo da: "In mobility...", dizendo que em geral esses esses modelos da literatura não fazem a saída de
  duas tarefas mas que usam mtl somente pra dar suporte à tarefa principal next-poi.
- você pode pesquisar pra ter mais contexto, mas uma coisa que a gente precisa dizer também a questão de que next-poi e
  next-place na literatura e usado apra a mesma tarefa
- Temos que explicar o markov em algum slide, acho que no de fundamentos compartilhados
- No slide 16, eu acredito que não devemos citar nove visitas, já que podemos modificar o tamanho da janela de visitas,
  ainda mais sendo uma definição.dessa forma eu acredito que o ideal seja colocar N visits.

---- Introdução

* Slide 1: inverter a ordem do segundo e do terceiro itens. A ideia é colocar primeiro o item que atualmente aparece em
  terceiro e depois o que atualmente aparece em segundo, porque essa sequência parece mais natural e coerente durante a
  apresentação oral.
* Slide 1 — título: considerar renomear o slide para “Human Mobility”, já que ele funciona como introdução ao conceito e
  à própria área de pesquisa de Human Mobility.
* Slide 2: remover a menção a Human Mobility, porque esse conceito já terá sido introduzido no slide anterior e a
  repetição parece desnecessária.
* Slide 3 — template/layout: consultar o template original e verificar se existe algum artefato, componente visual ou
  recurso do próprio template que possa ser utilizado para apresentar a pergunta de pesquisa de uma forma mais
  interessante. A forma atual de destacar a research question não está funcionando visualmente.
* Slide 3 — research question: revisar também a formulação da pergunta. A versão atual não soa tão natural quando
  falada. Explorar uma formulação próxima de:
  “Does multitask learning help predict the category and region of the next point of interest? And what does the answer
  depend on?” O objetivo não é necessariamente usar exatamente essa redação, mas encontrar uma pergunta que seja simples
  de ler e, principalmente, natural de dizer durante a apresentação.
* Slide 3 — organização visual: repensar a composição geral do slide, porque a organização atual não parece visualmente
  satisfatória, especialmente na parte em que os resultados aparecem.
* Slide 3 — resultados: consultar um Fable Agent para avaliar se faz sentido antecipar resultados já neste slide ou se
  seria melhor deixar a introdução apenas com o problema e a pergunta de pesquisa.
* Slide 3 — datasets: reavaliar a presença dos nomes dos datasets. Havia uma decisão anterior de evitar mencionar
  datasets nesta primeira seção da apresentação, portanto é preciso verificar se a versão atual está quebrando essa
  regra e se realmente existe ganho em apresentá-los tão cedo.
* Slide 4 — terminologia: revisar a definição de “next place”. Fazer uma checagem na literatura para confirmar a
  terminologia predominante, considerando que muitos trabalhos utilizam “next POI” além de “next place”. Ajustar o slide
  para refletir melhor o vocabulário utilizado na literatura.
* Slide 4: remover o último item, identificado atualmente como “constraint again”. Perfeito. Correção registrada: o
  bloco de contribuições corresponde ao Slide 6.
* Slide 6 — bloco de contribuições: remover o bloco atual de contribuição. Ele será reescrito posteriormente do zero,
  porque as tentativas anteriores ainda não chegaram a uma versão satisfatória. Não tentar fazer mais uma reformulação
  automática desse bloco neste momento.

--- Fundamentos compartilhados

* Slide 7 — hierarquia da informação: manter o conteúdo atual, porque as informações necessárias já parecem estar
  presentes, mas reorganizar melhor a hierarquia visual e lógica do slide. O principal problema aqui não é conteúdo, e
  sim estrutura e prioridade entre as informações.
* Slide 8 — baselines por tarefa: dar mais destaque visual às baselines apresentadas para cada tarefa. Não é necessário
  aumentar o tamanho da fonte; o texto pode permanecer menor. Como existe espaço disponível, considerar uma quebra de
  linha e uma organização visual que deixe mais evidente qual baseline pertence a cada tarefa.
* Slides em geral — títulos: revisar os títulos de toda a apresentação, especialmente aqueles construídos como
  analogias, jogos de palavras ou frases mais criativas. Preferir títulos mais diretos, descritivos e sérios, que deixem
  imediatamente claro o assunto do slide.
* Slide 9 — título: substituir “How two tasks share a model and how that fails” por algo mais direto e explicativo,
  possivelmente na linha de “MTL Fundamentals” ou outra formulação equivalente.
* Slide 9 — fundamentação de MTL: fazer uma revisão da dissertação e da documentação disponível, podendo usar um Opus
  Agent, para verificar se existe algum outro conceito fundamental de Multi-Task Learning que valha a pena apresentar
  brevemente neste slide.
* Slide 9 — balancing methods: incluir uma explicação curta sobre o que é um balancing method / método de balanceamento
  em Multi-Task Learning. A intenção é apenas introduzir a existência e a função desse tipo de método, sem
  aprofundamento excessivo.
* Slide 9 — negative transfer: já introduzir brevemente o conceito de negative transfer neste slide, junto dos demais
  fundamentos de MTL.
* Slide 9 — “criterion dissertation states”: remover ou reavaliar esse trecho. A informação parece deslocada e pode ser
  explicada verbalmente, caso seja necessária.
* Slide 9 — afirmação sobre balancing methods: revisar criticamente a frase “A balancing method is useful only if it
  improves on a tuned fixed weighting.” Ela parece excessivamente restritiva e não representa adequadamente todos os
  casos considerados na dissertação. Além disso, métodos de balanceamento são utilizados nos dois primeiros estudos, mas
  não no último. Verificar na dissertação/documentação qual formulação seria teoricamente mais correta e discutir essa
  revisão antes de substituir a frase.
* Slide 11: avaliar a remoção completa do slide. As informações presentes nele podem ser explicadas verbalmente e
  parecem não justificar um slide separado.
* Slide 10 — Contrastive InfoMax: introduzir brevemente Contrastive InfoMax como um dos fundamentos necessários para
  compreender os métodos utilizados posteriormente.
* Slide 10 — Delaunay triangulation: introduzir também a triangulação de Delaunay como fundamento relacionado à
  construção do grafo espacial.
* Slide 10 — Graph InfoMax: caso haja espaço e faça sentido visualmente, incluir um quarto elemento referente a Graph
  InfoMax, conectando conceitualmente a construção do grafo com os métodos de aprendizado contrastivo.
* Slide 10 — DGI/HGI/Check-HGI: DGI, HGI e Check-HGI devem, no máximo, ser citados brevemente neste momento. Evitar
  explicá-los aqui, porque serão detalhados nas seções posteriores. Quanto menos tempo de fala for gasto com esses
  métodos nesta seção, melhor.
* Slide 12: remover a frase “Florida appears twice in two extractions.” A diferença entre os ETLs já será explicada
  posteriormente durante a apresentação dos artigos: os dois primeiros estudos utilizam uma extração e o terceiro
  utiliza outra extração com mais dados.
* Slide 13 — Macro-F1: transformar o segundo item, que ainda complementa a explicação de Macro-F1, em subitem do item
  principal de Macro-F1.
* Slide 13 — Macro-F1: fazer o mesmo com o terceiro item, colocando-o como subitem, caso ele também esteja
  complementando diretamente a explicação da métrica.
* Slide 13 — quarto item: remover o quarto item. Caso essa questão seja levantada pela banca, ela pode ser respondida
  verbalmente.
* Slide 13 — Cross-Entropy: antes de remover definitivamente o quarto item, conferir no Capítulo 5 se a Cross-Entropy é
  utilizada com weights, para garantir que o slide não esteja simplificando ou contradizendo o procedimento adotado.
* Slide 13 — Majority Class: melhorar a formulação do primeiro item para algo na linha de “Majority Class — reference
  point”, seguido de uma descrição curta de sua função. A intenção é deixar explícito que Majority Class funciona como
  um ponto de referência, e não como uma baseline competitiva no mesmo sentido dos demais métodos.
* Slide 14 — apresentação visual: o conteúdo do slide está bom, mas a forma como ele é apresentado pode ser melhorada.
  Revisar a composição visual para deixar as relações entre as informações mais claras. Itens ainda podem ser a melhor
  solução, mas vale procurar uma organização mais elegante e legível.
* Slide 14 — item 4: avaliar a remoção do quarto item. Nos Capítulos 3 e 4 não há análise estatística que permita
  afirmar superioridade entre modelos, portanto é preciso evitar qualquer redação que sugira uma conclusão estatística
  que só poderia ser sustentada no Capítulo 5.
* Slide 14 — bloco “Two Traps”: remover “The metric convention changes” desse bloco.
* Slide 14 — bloco “Two Traps”: remover também “The task pair changes”.
* Slide 14 — bloco “Two Traps”: considerar remover o bloco inteiro, já que ambas as informações serão discutidas
  novamente dentro das seções específicas dos artigos. Mantê-lo criaria redundância e aumentaria desnecessariamente o
  tempo de fala.

--- MTLnet

* Slide 15 — mover para Fundamentos Compartilhados: o conteúdo do Slide 15 parece ser, na verdade, um fundamento
  compartilhado e deve ser movido para essa seção.
* Slide 4 + Slide 15 — avaliar fusão: reavaliar também o posicionamento do Slide 4, que atualmente está na introdução.
  Ele parece conversar diretamente com o Slide 15. Considerar remover o Slide 4 da introdução e levar ambos para
  Fundamentos Compartilhados. Avaliar se é melhor:
    * juntar os dois em um único slide, reorganizando visualmente o conteúdo para caber de forma clara; ou
    * mantê-los separados, mas consecutivos e com uma relação explícita entre eles. A preferência inicial é pela fusão,
      caso seja possível fazer isso sem comprometer legibilidade.
* Reorganização de Fundamentos Compartilhados — fluxo sugerido: repensar a sequência da seção para evitar idas e voltas
  conceituais. Uma possibilidade é:
    1. Slide 7 focado apenas em Related Work de POI Prediction;
    2. em seguida, apresentar as tarefas tratadas na dissertação, utilizando o conteúdo atualmente distribuído entre os
       Slides 4 e 15;
    3. depois, entrar nos fundamentos de Multi-Task Learning.
* Slide 7 — separar POI e MTL: atualmente o slide mistura Related Work de POI Prediction com Multi-Task Learning.
  Retirar dele a parte de MTL, provavelmente o quarto item, para deixar o slide dedicado ao contexto de POI Prediction.
* Slide 9 — incorporar conteúdo de MTL vindo do Slide 7: mover para o Slide 9 o conteúdo de Multi-Task Learning retirado
  do Slide 7.
* Slide 9 — título: considerando essa reorganização, avaliar um título mais representativo, como “MTL Fundamentals and
  POI”, “POI in MTL” ou outra formulação direta que mostre a relação entre os fundamentos de MTL e o problema de POI.
* Estrutura geral — reduzir tempo de fala: avaliar toda essa reorganização também com o objetivo de eliminar repetições
  e reduzir o tempo gasto alternando entre POI, tarefas e fundamentos de MTL.
* Slide 16 — regra de escrita: corrigir o uso de travessão, pois ele viola a regra de escrita estabelecida para a
  apresentação.
* Slide 16 — notas de rodapé: remover as notas de rodapé. Elas repetem informações que já foram apresentadas
  anteriormente e não parecem necessárias neste ponto.
* Slide 16 — imagem: utilizar o espaço liberado pelas notas de rodapé para aumentar a imagem e dar mais destaque ao
  elemento visual.
* Slide 17 — remover redundâncias: revisar os textos porque existem informações aparentemente repetidas. Por exemplo:
    * “Graph Attention, 64-dimensional vector per place”
    * e posteriormente “What it gives? One vector per place. Every visitor enters with the same vector.” Consolidar
      essas ideias para evitar repetir que existe um vetor por lugar.
* Slide 17 — Delaunay Graph / InfoMax: como Delaunay e InfoMax já terão sido apresentados em Fundamentos Compartilhados,
  aqui apenas mencionar brevemente que o método utiliza esses componentes, sem voltar a explicá-los.
* Slide 17 — reduzir tempo de explicação: a intenção é que esses fundamentos funcionem aqui apenas como referência ao
  pipeline, evitando gastar novamente tempo de fala com conceitos já apresentados.
* Slide 17 — reestruturação visual: após a remoção das redundâncias, reorganizar visualmente o slide. Manter os dois
  blocos atualmente diferenciados visualmente, mas testar uma composição vertical, um bloco abaixo do outro, em vez de
  lado a lado.
* Slide 18 — remover da apresentação principal: a tendência é remover completamente esse slide da sequência principal.
* Slide 18 — dados dos Capítulos 3 e 4: a informação de que os dados dos Capítulos 3 e 4 passaram por um ETL diferente
  não precisa ocupar tempo da apresentação principal.
* Slide extra — comparação dos dados: criar, como material extra/backup, uma tabela comparativa dos dados utilizados nos
  Capítulos 3 e 4, incluindo quantidade de check-ins, usuários e outras estatísticas relevantes. Assim, caso a banca
  pergunte, a informação permanece disponível sem consumir tempo da apresentação principal.
* Fundamentos Compartilhados — dados: manter na seção principal apenas as informações de dados realmente necessárias
  para compreender o Capítulo 5, evitando antecipar toda a diferença entre os ETLs.
* Slide 18 — pedir avaliação do agente: apesar da preferência pela remoção, o agente deve avaliar criticamente essa
  decisão e apontar se existe alguma informação realmente indispensável que seria perdida.
* Slide 19 — possível mudança para Fundamentos Compartilhados: reavaliar fortemente o posicionamento deste slide. O
  problema de “two losses, one set of parameters” é um problema geral de Multi-Task Learning e afeta os três
  estudos/Capítulos 3, 4 e 5. Portanto, conceitualmente, parece pertencer aos Fundamentos Compartilhados.
* Slide 19 — negative transfer: o slide descreve um problema de MTL, mas não deixa explícito que esse fenômeno está
  relacionado ao conceito de negative transfer, que já será introduzido nos Fundamentos Compartilhados. Integrar melhor
  essa terminologia.
* Slide 19 — Pareto dominance: revisar a relação entre Pareto dominance, conflito entre tarefas e negative transfer. O
  slide atualmente menciona Pareto dominance, mas parece incompleto como explicação do problema.
* Slide 19 — discutir antes de reposicionar: avaliar se o slide deve:
    * ser incorporado integralmente aos Fundamentos Compartilhados;
    * ser parcialmente incorporado e simplificado dentro da seção do artigo;
    * ou ser dividido entre fundamento geral e aplicação específica. Não fazer a mudança mecanicamente sem verificar
      qual opção preserva melhor a narrativa.
* Slide 20 — Nash-MTL: melhorar a descrição do que é Nash-MTL. O slide já possui algumas frases, mas a explicação ainda
  pode ficar mais clara e conceitualmente precisa.
* Slide 20 — regra de escrita: corrigir novamente o uso de travessão.
* Slide 20 — box “What Chapter Three Claims”: reavaliar se essa informação realmente precisa estar dentro de um box. A
  forma de destaque atual pode não ser necessária.
* Slide 20 — não citar Capítulo 5: remover referências ao Capítulo 5 deste slide.
* Regra para as seções dos artigos: dentro de cada seção referente aos Capítulos 3, 4 e 5, manter apenas informações
  relativas ao respectivo estudo. Evitar comparações ou antecipações como “Chapter 5 does X” enquanto se apresenta o
  Capítulo 3. Isso pode confundir a audiência sobre qual trabalho está sendo discutido.
* Slide 20 — nota de rodapé: avaliar a remoção da nota de rodapé, já que a informação provavelmente já terá sido
  discutida nos Fundamentos Compartilhados.
* Slide 20 — tuned fixed weighting: remover ou revisar a frase “useful only if it improves on a tuned fixed weighting”.
  Já existe dúvida sobre a validade geral dessa afirmação, e ela parece ainda menos necessária neste ponto,
  especialmente dentro da discussão específica do Capítulo 3.
* Terminologia para o agente: quando estas observações mencionam Capítulo 3, trata-se do Capítulo 3 da dissertação.
  “Seção 3” refere-se à seção atual da apresentação/slides. Não confundir os dois níveis.
* Slide 21 — nomenclatura da tarefa: substituir “static task” por “categorical classification”.
* Slide 21 — remover frase de resultado agregado: remover a frase “Both of our models score above 8 mAP in every
  category”. Ela não parece necessária.
* Slide 21 — destaque de primeiro e segundo lugar: padronizar a convenção visual entre as tarefas. Em Next Category, o
  primeiro lugar aparece em negrito e o segundo sublinhado. Aplicar a mesma convenção em Categorical Classification,
  incluindo o sublinhado para o segundo colocado.
* Slide 21 — notas de rodapé: remover as notas de rodapé atuais, pois não parecem acrescentar informação necessária.
* Slide 21 — nota sobre ± desvio padrão: a frase que atualmente aparece no corpo do slide, algo como “F1 block only
  means ± standard deviation of the five folds”, deve ser reformulada porque está mal escrita e pode funcionar melhor
  como uma nota de rodapé curta. Deixar claro que o “±” representa o desvio padrão calculado sobre os cinco folds.
* Slides 22 e 23: em princípio, manter como estão. Fazer apenas uma revisão final de clareza, concisão e qualidade da
  redação, especialmente do texto interno dos slides. Não há, neste momento, necessidade percebida de alteração
  estrutural.

* Slide 17 [Pesquise se quiser ter mais contexto] — adicionar representação visual do DGI: considerar substituir parte
  da explicação textual por um diagrama simples do funcionamento do DGI, para que o fluxo possa ser explicado
  verbalmente durante a apresentação. O desenho deve mostrar, de forma aproximadamente sequencial:
    1. Construção de duas versões do grafo: partir de um grafo positivo/original e de um grafo negativo/corrompido.
    2. Mesmo conjunto de nós: os dois grafos mantêm a mesma estrutura/conjunto de nós.
    3. Features nos nós: no grafo positivo, cada nó mantém suas features originais. No contexto deste trabalho, essas
       features estão associadas aos POIs.
    4. Corrupção das features: no grafo negativo, as features são embaralhadas entre os nós, preservando os nós e a
       estrutura do grafo, mas quebrando a correspondência entre nó e feature.
    5. GNN compartilhada: tanto o grafo positivo quanto o grafo corrompido passam pelo mesmo encoder GNN, ou seja, pelos
       mesmos parâmetros.
    6. Representações: a GNN produz representações para os nós dos dois grafos. A partir do grafo positivo também é
       obtida uma representação/resumo do contexto global do grafo.
    7. Discriminador: as representações são encaminhadas a um discriminador, cuja função é avaliar o quanto cada
       representação de nó é compatível com o contexto global obtido do grafo positivo.
    8. Objetivo contrastivo: idealmente, o discriminador deve atribuir valores próximos de 1 às representações
       provenientes do grafo positivo e próximos de 0 às representações provenientes do grafo corrompido.
    9. Loss e treinamento: a saída do discriminador é utilizada para calcular a loss contrastiva. O gradiente dessa loss
       retorna pelo discriminador e pela GNN, atualizando o encoder ao longo das iterações.
    10. Resultado esperado: com o treinamento, a GNN aprende embeddings que preservam informação relevante sobre a
        relação entre cada nó e o contexto global do grafo.
* Slide 17 — objetivo do desenho: o diagrama não deve tentar explicar toda a matemática do DGI. Ele deve funcionar como
  um suporte visual para uma explicação oral curta do tipo grafo original → corrupção → mesma GNN → discriminador →
  loss, reduzindo a quantidade de texto necessária no slide.
* Slide 17 — precisão conceitual: tomar cuidado para não representar o discriminador simplesmente como um classificador
  de “grafo positivo versus grafo negativo”. O ponto central do DGI é distinguir pares nó–contexto global compatíveis e
  incompatíveis, aproximando as representações locais do contexto global do grafo positivo.

-- ST-MTLNet

* Slide 24 — box “The Inherited Question”: remover o complemento “Suspect 2 against Suspect 3” e manter apenas “The
  Inherited Question”.
* Slide 24 — regra de escrita: revisar o texto do slide para remover o uso de travessão, mantendo a regra de escrita
  adotada para toda a apresentação.
* Slide 24 — quarto item: revisar completamente a frase “same latent width on both sides, the per-task encoder, project
  N, input to 256”. Ela não está clara e, na forma atual, não é compreensível. Verificar na dissertação/documentação o
  que exatamente esse item pretende comunicar e reescrevê-lo de forma simples.
* Slide 24 — quinto item: remover o quinto item. Não é necessário antecipar aqui quais são os três datasets, porque eles
  inevitavelmente aparecerão quando os resultados forem apresentados.
* Slide 24 — nota de rodapé: remover a nota de rodapé.
* Slide 25 — nota de rodapé: remover a nota de rodapé.
* Slide 25 — representação visual do HGI: assim como foi sugerido para o DGI no Slide 17, considerar substituir boa
  parte da explicação textual do HGI por um diagrama visual sobre o qual a explicação será feita oralmente.
* Slide 25 — reduzir texto: evitar manter textos que simplesmente descrevem passo a passo o funcionamento do HGI, porque
  muitas dessas informações serão naturalmente explicadas durante a fala ao acompanhar o diagrama.
* Slide 25 — desenho do HGI: aguardar a descrição específica do fluxo do HGI que será fornecida separadamente e, a
  partir dela, transformar o processo em um desenho visual simples e didático.
* Slide 27 — conteúdo: manter a estrutura conceitual atual. O conteúdo do slide está bom.
* Slide 27 — revisão textual: fazer uma revisão de redação para deixar os textos mais claros, curtos e naturais para
  apresentação oral.
* Slide 27 — revisão visual: revisar também a composição visual, mas preservar a lógica atual de divisão em blocos,
  porque ela funciona bem.
* Slide 27 — títulos: manter a linha dos títulos atuais, que estão funcionando bem.
* Slide 28 — remover da apresentação principal: a preferência é remover completamente este slide.
* Slide 28 — questão de vazamento dos resultados: embora a dissertação discuta explicitamente a questão de resultados
  terem sido vazados, essa informação provavelmente não precisa fazer parte da apresentação oral de 40–50 minutos. O
  texto da dissertação já explica o problema com mais profundidade.
* Slide 28 — decisão final: essa remoção ainda será discutida com o orientador. Portanto, por enquanto, tratar o slide
  como candidato à remoção, e não como exclusão irrevogável.
* Slide 29 — resultados de Category Classification: adicionar também a tabela de resultados de Category Classification.
  Atualmente o slide mostra apenas os resultados de Next Category, deixando incompleta a apresentação das duas tarefas.
* Slide 29 — organização dos itens: reestruturar os itens de interpretação dos resultados. Na forma atual, eles exigem
  leitura cuidadosa demais para serem compreendidos. O objetivo é que a audiência consiga bater o olho e entender
  imediatamente o principal achado.
* Slide 29 — hierarquia da informação: deixar explícito visualmente quais são os principais resultados, evitando
  parágrafos ou bullets que misturem observação, interpretação e conclusão.
* Slide 29 — notas de rodapé: remover as notas de rodapé.
* Slide 30 — título: substituir o título atual “What did the decomposition move, and where did not” por algo mais direto
  e sério.
* Slide 30 — função do slide: revisar se este slide deve ser apresentado como Conclusions, Limitations ou uma combinação
  curta dos dois. Pelo conteúdo atual, ele parece estar reunindo conclusões gerais do estudo junto de pelo menos uma
  limitação.
* Slide 30 — primeiro bloco “Travel labeled by task”: revisar o significado desse bloco. A mensagem não está clara. Caso
  não represente uma conclusão importante ou não seja possível formulá-la de maneira simples, remover o bloco.
* Slide 30 — “No universally better spatial encoder”: manter. Essa é uma conclusão importante do artigo e deve
  permanecer destacada.
* Slide 30 — “No this matched”: manter como limitação do estudo, mas revisar a redação para que a ideia fique clara e
  correta.
* Slide 30 — estrutura visual: reorganizar o slide para distinguir claramente o que é conclusão e o que é limitação,
  caso ambos permaneçam no mesmo slide.
* Slide 31 — reduzir bastante o conteúdo: o slide funciona bem como encerramento da seção, mas está longo demais para um
  slide final.
* Slide 31 — mensagem principal: condensar o achado do estudo em uma única linha ou um único parágrafo curto, deixando
  apenas a principal conclusão que deve permanecer na cabeça da audiência.
* Slide 31 — transição: usar o restante do slide para criar uma transição natural para o próximo trabalho,
  correspondente ao Capítulo 5 da dissertação.
* Slide 31 — objetivo narrativo: o slide deve funcionar menos como uma nova explicação e mais como um fechamento +
  gancho, encerrando este estudo e preparando a pergunta que será respondida no próximo.
* Regra geral para tabelas de resultados: padronizar todas as tabelas da apresentação seguindo a mesma convenção visual
  utilizada no Slide 21:
    * negrito para o melhor resultado;
    * sublinhado para o segundo melhor resultado. Aplicar essa regra de forma consistente em todas as tarefas, datasets
      e métricas apresentadas.
* Slide 29 — tabelas de resultados: aplicar explicitamente essa convenção tanto na tabela de Next Category quanto na
  nova tabela de Category Classification, garantindo que primeiro e segundo lugares sejam destacados de forma
  consistente.

--- Check2Hgi

* Slide 32 — tabela inicial: manter a tabela, porque ela funciona bem como abertura da seção.
* Slide 32 — ETL: avaliar com cautela se vale a pena incluir na tabela que o ETL mudou neste estudo. Como já houve uma
  decisão anterior de não enfatizar essa diferença na apresentação principal, adicionar essa informação pode aumentar a
  carga cognitiva sem trazer ganho proporcional. A princípio, não incluir, a menos que seja necessário para entender o
  capítulo.
* Slide 32 — espaçamento da tabela: aumentar o espaço de respiro entre linhas, colunas e elementos da tabela. Atualmente
  ela está visualmente muito comprimida.
* Slide 32 — bloco “The task pair changes here”: manter o bloco, porque ele comunica uma mudança importante desta etapa
  da dissertação.
* Slide 32 — texto do bloco: revisar a primeira frase de “The task pair changes here” para torná-la mais clara e
  natural.
* Slide 32 — remover frase: remover “Duration holds, one artifact, one forward pass, two answers.”
* Slide 32 — “Scope”: manter o conteúdo do quarto item, porque ele comunica casos de uso práticos da tarefa. Avaliar
  renomear “Scope” para algo mais explícito, como “Applications” ou “Practical Applications”. A segunda opção parece
  especialmente clara para apresentação oral.
* Slide 33 — quantidade de regiões: revisar por que são citadas especificamente as quantidades de regiões de Istanbul e
  California. California não é o dataset com maior número de regiões; aparentemente Texas seria um exemplo mais
  representativo. Verificar os dados e corrigir a escolha ou explicar por que esses dois casos foram destacados.
* Slide 33 — inglês simples: reescrever a frase “Coarser, then a place, not easier” ou equivalente. A formulação atual é
  pouco natural e exige interpretação excessiva, especialmente em uma apresentação para uma audiência majoritariamente
  lusófona. Usar inglês direto e fácil de processar oralmente.
* Slide 34 — manter estrutura geral: o slide está muito bom e pode permanecer conceitualmente como está.
* Slide 34 — destaque da contribuição: dar mais ênfase visual ao box referente à nova combinação de tarefas,
  possivelmente usando negrito, porque esse é um dos pontos centrais da dissertação e desta seção.
* Slide 34 — CTLE: tornar a explicação sobre CTLE mais curta e concisa. Atualmente ela está dividida em três itens e
  pode ser reorganizada em uma estrutura mais compacta, sem perder o essencial.
* Slide 35 — refazer figura: a figura atual está pequena e comprimida demais para apresentação. Mesmo sendo a mesma
  utilizada na dissertação, ela precisa ser redesenhada ou adaptada especificamente para slides.
* Slide 35 — aumentar legibilidade: priorizar uma figura maior, com menos elementos e com foco apenas na extensão do HGI
  introduzida neste trabalho.
* Slide 35 — reduzir texto para dois pontos principais: remover a maior parte dos itens atuais e manter apenas duas
  ideias:
    1. foi adicionada ao HGI uma nova camada de Check-in, da qual é extraída a representação em nível de check-in usada
       posteriormente;
    2. o modelo produz representações de 64 dimensões, sendo utilizada uma representação proveniente da camada de
       Check-in e outra da camada de Region, esta última como entrada para Next Region.
* Slide 35 — evitar reexplicar HGI: não repetir o funcionamento completo do HGI, porque ele já terá sido explicado
  anteriormente. O Check-HGI deve ser apresentado principalmente como uma extensão do HGI.
* Slide 36 — título: encurtar o título atual, especialmente se ele estiver na linha de “Design Principle in the Chapter
  on Wording”. O título precisa ser mais direto e menos longo.
* Slide 36 — frase principal: reescrever “The concept of visitor is running in the one direction only” ou frase
  equivalente. A ideia é importante, mas o inglês atual está pouco natural. Torná-la curta, direta e imediatamente
  compreensível em uma única leitura.
* Slide 37 — foco conceitual: manter o slide, mas concentrar o texto apenas em explicar Silhouette Score e KNN Purity.
* Slide 37 — resultados: não repetir os valores numéricos em texto. Os resultados já estarão na tabela/figura e podem
  ser explicados verbalmente.
* Slide 37 — nota de rodapé: reduzir drasticamente ou remover a nota de rodapé, porque ela está comprimindo demais o
  espaço disponível para a figura.
* Slide 37 — mover para resultados: mover este slide para perto do Slide 44. Ele é, em essência, um slide de resultados
  e faz mais sentido dentro da sequência de resultados.
* Nova ordem de resultados: considerar:
    1. Resultado 1: antigo Slide 37, com Silhouette/KNN Purity;
    2. Resultado 2: Slide 44;
    3. Resultado 3: Slide 45.
* Slide 38 — nomenclatura das streams: remover termos como “semantic key stream” e “spatial stream” quando eles não
  forem necessários. Preferir diretamente Next Category e Next Region, evitando introduzir novas nomenclaturas que
  aumentem a carga cognitiva.
* Slide 38 — Cross-Attention: adicionar uma explicação clara de Cross-Attention, pois esse é um diferencial arquitetural
  importante em relação aos modelos de MTL apresentados nos Capítulos 3 e 4.
* Slide 38 — verificar compartilhamento: validar a frase “The tasks share by exchanging information between per-task
  streams, not by owning hidden layers in common.” A afirmação pode estar imprecisa, porque existem camadas pelas quais
  ambos os fluxos passam e nas quais ocorre compartilhamento de informação. Conferir a arquitetura na dissertação/código
  antes de manter ou reescrever.
* Slide 38 — frase inferior: não deixar essa afirmação ocupando uma faixa separada abaixo da figura. Transformá-la em um
  item curto, caso seja mantida, liberando espaço para o elemento visual.
* Slide 39 — título: substituir “The private spatial path and what the evidence does not separate” por um título mais
  direto e relacionado à arquitetura.
* Slide 39 — continuidade com Slide 38: considerar utilizar o mesmo conceito de título do slide anterior, como
  “Architecture: Sharing by Exchange”, com alguma indicação de continuação, por exemplo “Part II”, se isso funcionar
  visualmente.
* Slide 40 — manter foco no Capítulo 5: remover qualquer referência aos Capítulos 3 e 4. Dentro desta seção, apresentar
  somente informações do estudo correspondente ao Capítulo 5 da dissertação.
* Slide 40 — quarto item: remover o quarto item caso ele faça comparação com capítulos anteriores.
* Slide 40 — quinto item: revisar o significado do quinto item e explicar melhor antes de decidir se ele deve
  permanecer. Na forma atual, a mensagem não está clara.
* Slide 41 — Macro-F1: como Macro-F1 já foi explicado em Fundamentos Compartilhados, não é necessário explicá-lo
  novamente. Pode permanecer como indicação da métrica utilizada, mas sem ocupar tempo de fala com uma nova definição.
* Slide 41 — OOD discounted accuracy: verificar de onde veio “OOD discounted accuracy” e se essa métrica realmente
  aparece no texto da dissertação/artigo. Não manter sem evidência explícita no material original.
* Slide 41 — “reference point for region”: reavaliar a necessidade desse quarto item. Como Markov será discutido
  posteriormente, verificar se antecipá-lo aqui realmente ajuda ou apenas cria redundância.
* Slide 42 — “Inferential Unit”: revisar o quinto item que começa com “Inferential Unit”. A formulação atual não está
  clara. Conferir o significado original e reescrever de forma mais simples ou remover.
* Slide 42 — Joint Best: substituir a explicação textual de “The Joint Best Convention” pela fórmula do Joint Best. A
  interpretação pode ser feita verbalmente durante a apresentação.
* Slide 43 — “Declared Departure”: revisar o quinto item. A expressão não está clara e o significado precisa ser
  recuperado a partir da dissertação/documentação antes de decidir se permanece.
* Slide 43 — protocolo estatístico: adicionar uma nota de rodapé muito curta, marcada com asterisco, indicando que houve
  posteriormente um aprimoramento do protocolo de avaliação estatística com base na literatura.
* Slide 43 — tom da nota: evitar uma formulação como “we created a protocol”. Preferir algo mais preciso, na linha de
  “The statistical evaluation protocol was later refined based on the literature.”
* Slide 43 — explicação oral: usar a nota apenas como gatilho visual. A explicação verbal pode mencionar que esse
  refinamento foi realizado posteriormente à publicação da dissertação.
* Slide 44 — remover “controls, STL”: remover essa referência caso ela não seja necessária para interpretar a tabela.
* Slide 44 — remover última frase: remover a frase final do slide.
* Slide 44 — remover afirmação dos folds: remover “All five folds favor the check-in-level representation at every
  dataset” ou formulação equivalente. A tabela já mostra a evidência necessária.
* Slide 45 — aumentar tabela: aumentar significativamente o tamanho da tabela para melhorar a leitura à distância.
* Slide 45 — convenção visual: aplicar a regra geral:
    * negrito para o melhor resultado;
    * sublinhado para o segundo melhor resultado.
* Slide 45 — “Before the reading”: revisar o significado desse bloco. A princípio, ele parece removível. Se não houver
  uma função narrativa clara, remover.
* Slide 45 — refazer a tabela de resultados: a tabela atual não está funcionando visualmente e deve ser reestruturada,
  não apenas aumentada. O objetivo é permitir que a audiência identifique rapidamente quais métodos estão sendo
  comparados e qual é o principal resultado.
* Slide 45 — identificar as baselines externas pelo nome: não utilizar apenas a indicação genérica “External”. Mostrar
  explicitamente os nomes das baselines externas utilizadas na comparação, incluindo POI-RGN e HMT-GRN (confirmar a
  grafia exata dos métodos no artigo/dissertação antes de alterar).
* Slide 45 — organização das baselines: manter somente as baselines externas realmente relevantes para a comparação,
  evitando poluir a tabela. Avaliar uma organização visual que diferencie claramente nosso método/modelos das external
  baselines, mas sem repetir “External” em várias células ou criar uma estrutura visual desnecessariamente complexa.
* Slide 45 — principal mensagem: deixar visualmente evidente que o método proposto supera as baselines externas nos
  resultados em que essa afirmação é sustentada pelos dados. Essa é uma das mensagens importantes do slide e não deve
  depender de a audiência interpretar sozinha uma tabela difícil de ler.
* Slide 45 — convenção de ranking: manter rigorosamente a convenção definida para todas as tabelas:
    * negrito para o melhor resultado;
    * sublinhado para o segundo melhor resultado.
* Slide 45 — hierarquia visual: a nova tabela deve permitir uma leitura aproximadamente nesta ordem: dataset/métrica →
  métodos comparados → melhor resultado → segundo melhor resultado → relação com as baselines externas.
* Slide 45 — prioridade: tratar esta tabela como um elemento importante da seção de resultados. Usar mais área do slide
  para ela e reduzir elementos textuais secundários, se necessário. A tabela deve ser compreensível rapidamente durante
  a apresentação, e não exigir leitura detalhada para descobrir quem venceu.
* Slide 46L — ordenar datasets: reorganizar a tabela/visualização seguindo a mesma ordem de datasets adotada ao longo da
  apresentação. Conferir a sequência exata antes de aplicar, pois a enumeração verbal contém repetição de estados.
* Slide 46L — remover frases explicativas: remover as duas frases textuais relativas a Region e Category. Essas
  conclusões podem ser ditas oralmente.
* Slide 46L — dar ênfase à tabela: usar o espaço liberado para aumentar e destacar a tabela.
* Slide 47 — título: substituir o título atual por algo mais direto. Avaliar opções como “Trade-offs and Limitations” ou
  “Limitations and Trade-offs”.
* Slide 47 — regra de escrita: remover travessões e revisar o texto de acordo com as regras de escrita da apresentação.
* Slide 47 — clareza geral: reescrever os itens para que possam ser compreendidos em uma leitura rápida, sem necessidade
  de interpretar frases muito condensadas.
* Slide 47 — item 2 / checkpoint selection: reescrever a ideia de que os números reportados correspondem ao checkpoint
  selecionado pelo melhor desempenho em validação. Deixar claro qual é a limitação metodológica: o processo de seleção
  usa o conjunto de validação, e os números finais devem ser reportados no conjunto de teste correspondente ao
  checkpoint selecionado. Evitar uma formulação ambígua como “Epoch selection reads default its score, absolute score,
  optimistic.”
* Slide 47 — item 4: revisar “Each visit draws only on the visits that preceded it.” A frase não está clara no contexto
  atual. Conferir o que ela pretende representar, provavelmente alguma restrição causal/temporal, e reescrever de
  maneira explícita ou remover se não for relevante.
* Regra geral — títulos e inglês: continuar aplicando nesta seção a regra já definida anteriormente: evitar títulos
  metafóricos, jogos de palavras e inglês excessivamente comprimido. Priorizar títulos descritivos e frases curtas,
  simples e fáceis de dizer em voz alta.
* Regra geral — capítulos: nesta seção, referente ao Capítulo 5 da dissertação, não introduzir comparações com Capítulos
  3 e 4 dentro dos slides do estudo. Se alguma comparação for necessária, reservar para uma síntese posterior da
  dissertação.

--- Conclusão

* Slide 48 — tabela final: manter a tabela, porque ela funciona muito bem como síntese geral da dissertação.
* Slide 48 — reduzir densidade: simplificar a tabela para que ela possa ser compreendida mais rapidamente. Atualmente
  ela exige leitura e processamento excessivos. Reduzir texto, deixar as células mais diretas e destacar apenas o que
  realmente precisa permanecer na conclusão.
* Slide 49 — resposta geral: após a primeira frase do bloco “Answer”, adicionar uma observação curta deixando claro que
  as conclusões específicas dos estudos não devem ser automaticamente extrapoladas entre eles. Uma formulação possível,
  a ser refinada, seria algo próximo de:
  “The conclusions are study-specific; what carries across studies is the methodology and the conditions identified.”
  Manter a ideia, mas usar inglês simples e natural para apresentação oral.
* Slide 49 — resposta condicional: deixar explícito que a resposta final da dissertação sobre Multi-Task Learning é
  condicional, e não simplesmente positiva ou negativa.
* Slide 49 — três condições principais: reorganizar os três últimos itens para representar claramente as três variáveis
  das quais o sucesso do MTL depende:
    1. Input representation
    2. Architecture
    3. Scale
* Slide 49 — explicação das condições: apresentar cada uma das três condições com uma descrição curta e direta. Evitar a
  forma atual, em que essas ideias existem, mas não aparecem como uma estrutura conceitual clara.
* Slide 49 — regra de escrita: apesar da sugestão verbal de utilizar travessão entre o nome e a explicação, respeitar a
  regra geral da apresentação de não utilizar travessões. Usar dois-pontos, quebra de linha ou outra solução visual.
* Slide 49 — remover frase: remover “Identifying these conditions is the main finding of this dissertation” ou
  formulação equivalente. O próprio slide deve permitir que a importância dessas condições fique evidente sem precisar
  declarar isso explicitamente.
* Slide 50 — relação com Slide 6: este é o mesmo conteúdo de contribuições anteriormente apresentado no Slide 6. Como já
  foi decidido que o Slide 6 será removido da introdução, reconstruir este conteúdo apenas aqui, na conclusão.
* Slide 50 — título: substituir “The Contribution in One Block” simplesmente por “Contributions”.
* Slide 50 — estrutura: manter a divisão em dois blocos:
    * Practical Contributions
    * Scientific Contributions
* Slide 50 — Practical / Joint Model: substituir o texto extenso atual por um item mais simples centrado em “Joint
  Model”.
* Slide 50 — Joint Model: expressar de forma curta a ideia de que a contribuição é principalmente operacional, e não
  necessariamente uma redução de custo computacional. Não usar a formulação atual “one model, one forward pass, two
  predictions” se ela estiver tornando o slide mais verboso.
* Slide 50 — regra de escrita: novamente, não utilizar travessão na composição final. Uma possibilidade seria:
  Joint Model Operational integration rather than computational reduction.
* Slide 50 — Practical / Check-HGI: incluir Check-HGI como contribuição prática.
* Slide 50 — reutilização do Check-HGI: explicar de forma curta que o Check-HGI constitui um artefato/método que pode
  ser reutilizado por trabalhos futuros da literatura, em vez de ficar restrito ao experimento desta dissertação.
* Slide 50 — Scientific / Check-HGI: incluir também o Check-HGI no bloco científico, mas aqui sob a perspectiva de
  novelty metodológica/arquitetural.
* Slide 50 — Scientific / condições do MTL: incluir as três condições identificadas ao longo da dissertação:
    * Input representation
    * Architecture
    * Scale Essas condições devem aparecer como um dos principais resultados científicos da investigação.
* Slide 50 — Scientific / protocolo estatístico: investigar se o protocolo estatístico utilizado para comparar dedicated
  vs. joint models pode legitimamente ser apresentado como contribuição científica.
* Slide 50 — validar novidade do protocolo: antes de colocá-lo como contribuição, fazer uma revisão mais cuidadosa da
  literatura e da própria dissertação. A impressão atual é que poucos trabalhos estruturam explicitamente essa
  comparação dessa maneira, mas isso não foi reivindicado como novidade na dissertação. Portanto, não apresentar como
  contribuição científica sem sustentação.
* Slide 51 — Data Vintage: manter essa limitação, mas tornar a discussão mais precisa.
* Slide 51 — anos dos datasets: incluir os anos correspondentes aos dados, especialmente para Istanbul/Massive-STEPS,
  para mostrar que houve uma tentativa de utilizar um dataset mais recente.
* Slide 51 — restrição da literatura: deixar claro que a antiguidade dos dados não é apenas uma limitação específica
  desta dissertação. Ela é também uma restrição recorrente da literatura de POI/check-ins, na qual datasets públicos
  recentes são escassos.
* Slide 51 — pesquisa sobre datasets recentes: verificar na literatura/documentação qual é de fato a disponibilidade
  temporal dos datasets públicos mais recentes. Confirmar se é correto afirmar que datasets amplamente utilizáveis
  raramente ultrapassam aproximadamente 2022, antes de inserir essa afirmação no slide.
* Slide 51 — Taxonomy / Coarseness: manter a limitação conceitual, mas reescrever o item. A ideia é que os experimentos
  trabalharam com uma taxonomia limitada, por exemplo, sete categorias, e outras granularidades ou taxonomias poderiam
  produzir resultados diferentes.
* Slide 51 — melhorar redação: substituir “Taxonomy, Coarseness” por uma formulação mais direta que explicite que a
  limitação está na granularidade e no número de categorias consideradas.
* Slide 51 — item 3: manter a limitação, mas deixar claro, quando apropriado, que ela também é uma limitação recorrente
  na literatura e não exclusivamente deste trabalho.
* Slide 52 — Next Place Task: manter o item referente à tarefa de Next Place, pois representa uma extensão/limitação
  relevante.
* Slide 52 — item 5: manter.
* Slide 52 — item 6: reavaliar criticamente. A preferência atual é remover, a menos que exista uma justificativa forte
  para mantê-lo.
* Closing slide — simplificar radicalmente: reduzir bastante o conteúdo. O slide final não precisa recapitular novamente
  todos os resultados da dissertação.
* Closing slide — GitHub: remover os links/referências de GitHub do corpo principal do slide. Se for importante
  mantê-los disponíveis, colocá-los de maneira discreta em nota de rodapé ou material auxiliar.
* Closing slide — não reviver a narrativa completa: remover frases como “The negative result was not an obstacle to the
  contribution; it was the first half” ou outras tentativas de recontar a evolução inteira da dissertação.
* Closing slide — uma única mensagem: construir o encerramento em torno de uma frase forte que responda diretamente à
  pergunta central da dissertação.
* Closing slide — natureza da resposta: essa frase deve deixar claro que MTL apresentou resultados relevantes, mas que o
  seu benefício é condicional, dependendo sobretudo de input representation, architecture e scale.
* Closing slide — função narrativa: o último slide conceitual deve encerrar a defesa, não abrir novas discussões. A
  audiência deve sair dele entendendo em uma frase qual é a resposta da dissertação.
* Acknowledgements — título: substituir o título atual por “Obrigado”, em português.
* Acknowledgements — subtítulo: utilizar “Acknowledgements” logo abaixo, em tamanho menor, caso seja desejável manter a
  identificação formal da seção em inglês.
* Acknowledgements — conteúdo: manter um agradecimento breve ao:
    * orientador;
    * instituição;
    * banca;
    * colegas de pesquisa.
* Acknowledgements — visual: manter o último slide simples, limpo e com pouco texto, evitando transformar os
  agradecimentos em outro slide denso.