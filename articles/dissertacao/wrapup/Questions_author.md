# Pontos de estudo e dúvidas para a defesa

1. Como sustentar uma conclusão sobre o efeito do MTL na predição de POI a partir de três estudos que utilizaram dois
   pares de tarefas diferentes? Nos dois primeiros artigos, o modelo combinou classificação estática de categoria com
   previsão da próxima categoria; no último, combinou previsão da próxima categoria com previsão da próxima região.

   1.1. Como justificar a inclusão desse último par de tarefas na mesma linha de investigação?

   1.2. É necessário demonstrar que esse par também apresentava um efeito nulo antes das mudanças na representação e na
   arquitetura?

   1.3. Caso não seja possível fazer essa afirmação, como delimitar corretamente a conclusão geral da dissertação?
2. O que é o DRRGNN, e pq não usamos ele como baseline ?
3. Será que essas tarefas não melhoram em qualquer modelo mtl ?



---

# Estudos específicos

1. Métodos estatísticos utilizados e situações em que cada um deles é aplicado:
    1. TOST
    2. Wilcoxon
    3. Holm
    4. macro-f1
2. Como funcionam, bases e conceitos principais:
    1. Infomax
    2. DGI
    3. HGI
    4. Check2HGI.
3. Novo modelo conjunto (*joint model*):
    1. Como funciona, camadas, otimizadores, e outros hyperparmetros
    2. Justificativa para cada componente da arquitetura.
3. Markov-k, como funciona o que é ?
4. Protocolos de comparação de embeddings:
    1. kNN-LOO (*k*-nearest neighbors with leave-one-out).
    2. Silhouette com distância baseada em cosseno.
    3. *Centroid separability ratio*.
    4. Linear CKA em comparação com o *engine* de referência.
1. MTL
    1. Film
    2. Cross-Attention
    3. Nash-MTL
    4. Coss-gradient

----

# Pontos para validar

1. No Capítulo 2, o tamanho dos conjuntos de dados é diferente do apresentado nos Capítulos 3 e 4. É necessário validar
   se os resultados reportados no Capítulo 3 para o modelo descrito no Capítulo 2 foram obtidos com os dados novos.
2. Nos Capítulos 2 e 3, é necessário validar como era a entrada do modelo MTL, especialmente em comparação com o
   Capítulo 4, no qual o modelo recebe duas entradas.

3. **δ-crítico — decisão pendente do autor (levantado 2026-08-24).**

   Hoje a tabela de resultados publica um veredito binário indexado por uma margem fixa: "não-inferior a δ = 0,4 pp". A
   proposta é publicar, ao lado, o **δ-crítico** de cada célula — a margem a partir da qual o veredito mudaria. Ele é
   lido do próprio intervalo por subtração (`δ_NI = −limite inferior`), não é escolhido, e não é análise nova:
   recomputado sobre a leitura selada, reproduz 6/6 dos vereditos já bancados.

   *Por que interessa:* é a única parte da leitura cuja validade não depende da arquitetura que gerou os números — um
   leitor futuro, com outro modelo e outra margem, relê a tabela sem refazer nada. E dá mais informação que o carimbo:
   Alabama/região passa de "inconclusivo a 0,4" para "seria não-inferior a partir de 1,149 pp", que está acima do teto
   de ~1 pp usual na literatura — ou seja, nenhuma margem razoável salva aquela célula.

   *A decidir:* entra na tabela principal, em apêndice, ou não entra. **Não substitui** o veredito pré-registrado de δ =
   0,4, que continua sendo o da manchete. Explicação completa em
   `mtlcheck/docs/EVALUATION_METHOD_GUIDE.md` §5.1.

4. **Uma partição só vs. várias — justificar no texto (levantado 2026-08-24).**

   O protocolo congela um sorteio de usuários em folds e usa as sementes como réplicas de inicialização; boa parte da
   literatura de comparação de algoritmos usa k-fold *repetido*, com um sorteio novo por repetição. A pergunta vai
   aparecer na banca.

   *A justificativa a escrever:* como a métrica é agrupada sobre todas as predições fora-de-fold, **todo usuário é
   avaliado exatamente uma vez sob qualquer sorteio** — re-particionar não muda quem é avaliado, muda quem co-treinou. O
   efeito foi **medido** (Alabama: +0,37 pp em região, ±0,28) e é reportado **ao lado** do intervalo, não dentro dele:
   embutido, a meia-largura iria a 0,44–0,84 pp contra δ = 0,4 e apagaria toda não-inferioridade de região, inclusive a
   de Istambul.

   *A ressalva honesta a carregar junto:* a corrente majoritária da literatura (Dietterich 1998; Nadeau & Bengio 2003;
   Bouckaert & Frank 2004; Bouthillier et al. 2021) põe a partição dentro da incerteza para afirmações sobre
   procedimento. A inferência condicional à partição é modo reconhecido (Bayle et al. 2020; Bates, Hastie & Tibshirani
   2024), mas é minoritária — e a dissertação deve nomear o alvo em vez de deixar implícito.

----

# Ideias futuras

1. Uma única entrada, uma única camada compartilhada (*shared layer*) e uma cabeça para cada tarefa.
2. Avaliar a utilização de cabeças separadas ou de uma arquitetura em cascata.
3. Unificar o Check2HGI com o MTL.
4. Como adicionar mais features no check2hgi
    1. Problema no infomax
5. Usar o GSM++ da google no || An end-to-end attention-based approach for learning on graphs. No DGI ao inves do GNN.

---

# Contribuições

Cientificas

1. Superamos a literatura no next-category
2. Publicamos resultados base para a literatura do next-region
3. Novelty: Criamos um modelo de embedding (check2Hgi) agnostico a tarefa
4. Determinamos 3 condições para que um MTL funcione para o trinamento das tarefas de forma conjunta

Praticas

1. Publicamos o Check2Hgi.
2. Criamos um modelo unificado para tarefas noext-category e next-region – ganho operacional e não computacional.
3. Protocolo de avaliação estatica dos modelos
4. Gama de trabalhos futuros.
   1. Check2Hgi
      1. Incorporar novas feat aos nós do checking (Problema no infomax)
      2. Agregar o poi encoder ao HGI(propagar o erros das features) 
      3. Usar hypergraph no Check2Hgi
      4. Mudar o GCN para GSM++ ou outro.
   2. MTL
      1. Remover a camada embedding, ter uma camada compartilhada(mmoe ou cross-attention)
      2. 
   3. Adicionar nova tarefa Next-POI
      1. Cabeça idepentende || Criar uma versão cascate
   4. Unificar check2hgi com o MTL ?

----

# Pergbuntas basicas da banca.

1. **Aprendizado multitarefa (MTL) e aprendizado monotarefa (STL):** diferenças, vantagens, custos e situações em que o
   compartilhamento de parâmetros pode produzir transferência positiva ou negativa.
2. **Topologias de compartilhamento:** *hard parameter sharing*, camadas específicas por tarefa, *soft sharing* e
   atenção cruzada (*cross-attention*).
3. **Transferência negativa e conflito entre gradientes:** como identificar esses fenômenos e por que uma melhoria em
   uma tarefa pode prejudicar outra.
4. **Representações em nível de POI e em nível de check-in:** o que cada representação consegue capturar e por que um
   vetor fixo por POI não representa adequadamente o contexto de cada visita.
5. **Aprendizado supervisionado, auto-supervisionado e representação por *Infomax*:** qual é o objetivo de cada etapa do
   Check2HGI e quais rótulos são ou não utilizados durante o treinamento da representação.
6. **Conceitos básicos de grafos:** nós, arestas, grafos heterogêneos, convolução em grafos, agregação de vizinhança e o
   caráter transdutivo da representação aprendida.
7. **Atenção e atenção cruzada:** consultas, chaves e valores; diferença entre compartilhar informação e permitir que
   cada tarefa mantenha uma representação específica.
8. **Função de perda e treinamento conjunto:** soma ponderada das perdas, pesos das tarefas, seleção de *checkpoint*,
   ajuste de logits e diferença entre treinamento e inferência.
9. **Métricas utilizadas:** macro-F1, precisão, revocação, Acc@10, diferença entre acurácia Top-1 e Top-10 e efeito do
   desbalanceamento entre classes.
10. **Validação e comparação experimental:** divisão por usuário, validação cruzada, *seed*, pareamento entre modelos,
    vazamento de dados, representação transdutiva e generalização para usuários ou POIs não observados.
11. **Inferência estatística:** hipótese nula e alternativa, valor de *p*, intervalo de confiança, tamanho de efeito,
    testes unilaterais e diferença entre ausência de significância e evidência de não inferioridade.
12. **Validade das conclusões:** diferença entre associação e causalidade, variáveis confundidoras, limitações da
    mudança simultânea de tarefas, representação e arquitetura, e alcance da generalização para outras cidades e
    conjuntos de dados.
