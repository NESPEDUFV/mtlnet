# _aut_original.md — o §4 do PENDENCIAS.md como voce o escreveu, byte por byte

> Preservado em 2026-08-04, antes da reescrita da rodada 13. Nada aqui foi editado.
>
> - bytes: 16263 (caracteres apos decodificar UTF-8: 16024; a diferenca sao os acentos)
> - linhas: 162
> - itens: 37 (36 com texto + o 37 vazio)
> - sha256 dos bytes: e2a44feac34971e68ea98b623f52ea409551103afae3c5a73560771ced1f37f6
> - identico nos commits `82080ce4` e `c13fe4d2`, conferido nos dois
>
> Reproduzir a medicao:
> ```
> cd /Users/vitor/Desktop/mestrado/ingred/articles/dissertacao/src_utils
> ln=$(grep -n 'Pensamentos e considera' PENDENCIAS.md | head -1 | cut -d: -f1)
> tail -n +"$ln" PENDENCIAS.md | shasum -a256   # e2a44feac34971e6...
> ```

---

## §4 · Pensamentos e considerações do Autor

1. No resumo e na introdução, valha fazermos uma analise sobre o uso de especificidades, e por especificidades me refiro
   a menção como: "O modelo final foi avaliado em cinco estados dos Estados Uni- dos, extraídos do Gowalla, e em
   Istambul, extraída do Massive-STEPS"(resumo), "vinte modelos ajustados por configuração, quatro inicializações
   aleatórias sobre cinco partições fixas e testes pareados sobre as médias de cada inicialização"(resumo) ou "The
   category space contains Community, Entertainment, Food, Nightlife, Outdoors, Shopping, and Travel."(2.1.1.2). Vide
   que o nosso trabalho ele é generico, podemos usar qualquer dataset e quaquer N numeros de categorias. Assim, nos
   texto que não explicativos de métodologia ou sobre os dados em si, podemos ser mais genericos; no resumo que dei
   exemplo podemos usar algo como: "O modelo final foi avaliado em 6 datasets, sendo 4 localizados nos U.S e afins de
   generalização um não U.S"(Temos que refinar bem essa frase é só um exemplo). Ainda sobre esse tópico, no resumo tabém
   falamos
   "considerando uma margem de dois pontos de Acc@10 pelo procedimento TOST", outra especificação que não vejo
   necessidade.
2. Padronização das palavras tecnicas. Palavras que já estão no "List of abbreviations and acronyms" estão sendo
   escritas de forma distintas pelo texto. Um exemplo é Point of Interest que em muitos locais aparece como
   Point-of-Interest. Outro detalhe é o uso correto dessas palavras como no caso de Multi-Task Learning, essa palavra no
   artigo original é escrita como: Multitask Learning, sem o hifén sem contar que o APA Style, também define a
   preferencia por uso de plavras sem hifén; enfim faça uma pesquisa para validar essa é outras palavras técnicas e
   vamos substituir onde necessario.
3. Na introdução a frase: ",while place categories provide the semantic information used by location-based
   services [4].", em uma leitura rápida parece não ter nexo com o que está sendo dito anteriormente ou parece ser uma
   frase só jogada sem muito contexto.
4. Na frase: "Some methods used in this dissertation also come from neighboring geospatial tasks. In particular, the
   spatial encoders examined in the second study were first validated for applications such as
   speciesrecognitionandremote-sensingclassification [5, 6].", será que já fala de métodologia no primiero paragrafo é
   interessante, estamso contrunido a problmeatica e as bases do problema para o leitor, é o que seria "neighboring
   geospatial tasks", me parece bem solto.
5. Na frease: "Because next category and next region are predicted from the same visit history, one model may serve both
   tasks.", temos que na frase anterior defimos 3 tarefas que treinamos nos modelos conjuntos. Será que essa frase não
   serai melhor escrita como algo: "Because the previous tasks cited consumes the same visit history, one unify model
   ,such as Multitask learning (MTL),may server for them. MTL ..."(Temos que melhorar)
6. We are using the term: "static place categories" to refear to the poi classification of a unkown POI category. But in
   the §1.1 we are define this task as "category classification, a static task that predicts..."; my point is for a
   reader that are not familirazed with the tasks and are nobie about this point, this will create confusion. FOr the
   other tasks we define them and use the same jarguan throught the text.
7. Na frase: "Under a check-in level representation, static category classification is a less natural companion task
   than a second sequential target, so the final task pair becomes next category and next region.", acho que a
   explicação do porque da mudança ainda falta conteudo, principalmente, pq outro motivo é diria até que mais forte apra
   mudança foiq eu na literatura essas outras duas tarefas possuem mais forças que a classifiçação de poi; sem contar
   que temos outro problema que não sei se temos que explicitar, mas sobre regime de checking level e nosso motor de
   embedding a o embedding pode vazar e deve vazar qual a categoria do checking atual, até para o modelos conseguir
   prever com mais exatidão a proxima categoria.
8. A frase: "The dissertation does not treat these as one unchanged experiment. It presents a sequence in which a result
   valid for one configuration leads to a diagnosis and then to a different, explicitly bounded solution."; Eu acredito
   que podemos melhorar bem, na clareza ainda mais quando se comparado com a que estava antes: ", and this dissertation
   names that evolution plainly rather than narrating one fixed experiment. The arc it reports is a correction trail:
   each study revised what the previous one concluded, and the later chapters state precisely which earlier conclusions
   they supersede."
9. We use hard share paramter through all the introduction and never explain what is: An common MTL apporach on the
   paramter and the data flow are shared. Eval this.
10. No paragrafo: "Evaluate whether a joint model with hard parameter sharing benefits static category classification
    and next-category prediction when compared with dedicated single-task models (Chapter3).", Acho que podmes incluir:
    "Evaluate on how an MTL model can be build and work on the POI field and whether a joint model using hard sharing
    benefits poi classification and next-category...."
11. No paragrtafo: "Consolidatetheevidenceundertheuser-disjointcross-validation,significance-testing,and
    non-inferiorityprotocolusedinthefinalstudy (Chapter 6)." isso tá errado é no Chapter 5.
12. No paragrafo: "The joint setting imposes a single-model constraint: one trained artifact must produce both outputs
    in one forward pass.". Que joint settings ?
13. Na parte de contribuições não estamos a destacar achados importantes, e ela não está bem escrita faça uma avaliação
    mais profunda. Vou dar alguns exemplos: - O check2hgi é um avanço quanto ao uso de um embedding de mobilidade que se
    utiliza checkin ao inves de poi, e este pode ser usado em varios trabalhos futuros com difererntes propositos; -
    Nosso MTLnet final ou o joint model final ele é um modelo que pode ser usado para treinamento conjunto das tarefas
    ou ainda pode ser expandido para outras tarefas dado sua modularidade; - O achado que as tarefas parecem não serem
    conflitantes em um modelo MTL. (Esse tem que tomar bastante cuidado);; - Nossos artigos são pioneiros na utilização
    e MTL para essas duas tarefas, tarefas essas que podemos ter um escopo mais abrangente que o de next-poi Por favor,
    avalie eses pontos, avalie os que já estão e faca uma analise pelo texto e trabalho para ver se não estamos
    esquecendo nada.
14. A frase: "It indicates that mobility is learnable, but it is not a reference point for the category and region
    metrics defined in Section~\ref{sec:fund:eval}." Para mim não faz sentido dizer "It indicates that mobility is
    learnable, but it is not a reference point for the category and region metrics defined in Section~\ref{sec:fund:
    eval}.", justamente o contrario podemos sim ter os estudo de mobility e next-location como referencia para o
    category e regio. A frase original era: "This bound is specific to next-location prediction at coarse spatial
    resolution; it shows that mobility is far from random and is learnable at all, and Section~\ref{sec:fund:eval}
    states the reference points that actually bound the category and region tasks studied here."
15. Eu tô com um medo, eu posso estar deixando passar batido por já ter lido varias vez, mas se referir as tarefas como,
    sequenciais e estaticas, como no exemplo: "three experimental tasks, two sequential and one static.", para mim faz
    muinto sentido, só que será que estamos explicando isso bem no texto ? E estamos explicando antes de usarmos no
    texto, as vezes deixa a explicação na lista de abreviassões e accronimos ?. Faca uma analise.
16. O §2.1.1.1 foi uma introdução bem legal, porém está precisa ser revisada, é precismos ser mais precisos na
    explicação, algumas lacunas ainda estão presentes como o fato de não falarmos o que é 𝑥𝑖 ou H𝑖. Da onde saiu 𝑐𝑝, 𝑐i
    e ri, precisamos explicar o que é isso, estamos tacando simbolos sem explicar.
17. No §2.1.1.1 na frase: "The category space contains Community, Entertainment, Food, Nightlife, Outdoors, Shopping,
    and Travel. The region target is a census tract in the United States datasets and a mahalle in Istanbul. ", listar
    as categorias em um definição técnica é um erro, até pq nosso modelo poderia usar N categoria e não só essas 7, além
    disso citar os datasets não é algo para agora mas para a sessão §2.4
18. No §2.2.2 se graph-infomax é tão importante para o trabalho, temos que explicar em linhas gerais o que ele é e como
    funciona.
19. No §2.2.2 a frase: "The representations used in this work are trained without category or region labels.", tem que
    ser dita com bastante cudidado, por que no hgi vamso sim usar o categoryu como target, não usamos nos dois primeiros
    para não gerar vazamento de dados para tarefa estatica.
20. Não sei se no §2.2.2, mas no check2hgi, como descrito
    em:  [check2hgi_v17_complete_picture.md](../science/check2hgi_v17_complete_picture.md) tabém usamos POI2vec, não
    teriamos que citar ele ?
21. A frase: "MTLnet uses FiLM to condition its shared layers on task identity. Chapter 4 keeps this architecture but
    replaces its single place embedding withspatial, temporal,and categoricalencoders.The controlled changeisolates the
    effectoftheinput representation.". não deveria estar no §2.2.3.1, deveria estar na sessão sobre MTL
22. On the §2.2.3.2 get more context in the
    file: [check2hgi_v17_complete_picture.md](../science/check2hgi_v17_complete_picture.md) if necessary, and evla if
    what is in there is correct.
23. A frase: "The representation changes are paired with a controlled progression in model architecture." não ficou
    clara para mim, é não pareceu uma boa frase de transição.
24. A frase: "The models therefore differ in their sharing topology and in the private input available to the region
    output." Temos que explicar isso melhor, no MTLnet ele já recebia duas entradas, a diferença e que as duas entradas
    lá era de um mesmo embedding, aqui os embeedings são saidas diferetned do check2hgi, apesar de serem diferentes elas
    ainda possuem correlação.[VALIDE E PESQUISE MAIS NA CODEBASE]
25. Será que nomear o joint model, como MTLChkNet agora seria muito tarde ? Alguma outra sugestão de nome melhor ?
    Podemos, até atualizar no mobiwac, vide que ainda está em revisão ?
26. No §2.3.3 não explicamos o que é o `L𝑘`, also the explanation make in the §2.3.3 and §2.3.2.1 is working but i
    belive that we can improve make it more easy to read the concepts better and the constructioin of the logic flow
    easy to follow and undertand.
27. Reading more about pareto make me think, shouldn't we have some claim about the pareto property that we enconunter
    in the chapter 5 ? Even if this claim came in the appendix F ?
28. The §2.3.2 and §2.3.3 are very poor organized and repetitive, the concepts are out of order and the paragraphs
    requeries read more the once and go and back on other paragraphs to have a complet explanation. My take would be
    start wiht the §2.3.2.2 that define the problem, from the problem we formal define it with the §2.3.2, then we
    discuss the current options of the literature witht the §2.3.3, then we closes with §2.3.2.1 and with the part B of
    the §2.3.2.2 where discuss about the chapter 5 finds and the appendix D. what do you think ?
29. Na frase: "Equivalently, the reported OOD-discounted Acc@10 is the in-distribution Acc@10 multiplied by one minus
    the out-of-distributionfraction." eu não a entendi, sem contar que não estamos explicando o que é OOD.
30. No §2.4 precisamos reorganizar a ordem das sub seções e melhora a escrita de algumas, entre a §2.4.1 e a §2.4.2,
    temo que criar um nova chamada `preparation and data split` onde vamos pegar o que já temos no segundo paragrafo do
    §2.4.3 e descorrer mais sobre como os dados estão sendo preparados é a metodologia de split e separação antes dos
    dados entrarem no modelo. Enfim, seguimos para o `Metrics andreferencepoints` e o §2.4.3 vira
    `Comparision and statistical decisions` onde descorremos sobre o problem de comprar diferetnes resultados e como
    criamos uma métodologia estruturada para isso.
31. No primeiro paragrafo do chap 6, é falado: "This dissertation examined whether multitask learning helps
    next-category and next-region prediction and what determines the answer." Mas, esquecemos de falar sobre o
    poi-classification.
32. No paragrafo 2 do §6.2, onde temos: "so the gain does not come from the region task teaching the category task;"
    Isso está bastante errado já analisamos isso e validamos que na verdade esse não e o big picture e que essas
    analises, só comprovam que o loss não estava contribuindo para o ganho, mas a métodologia do cross-switch e outros
    artefatos ainda continuam auxiliando no ganho. (Pesquise e se aprodunde sobre isso); Além disso avali se esse mesmo
    erros está acontecendo em outras partes do texto.
33. On the "Contributions by chapter", we should focus less on the results and numbers and show more the conecptual
    contributions and finds, use numbers and results only if very necessary. We should reserve the results for the
    `The consolidated answer`, where we should show the results not exensivally, but we an show it more here.
34. Sobre as limitações, em §6.3 tenho alguns pensamentos sobre eles: - The data vintage is a problem, but we use the
    Massive steps from 2025; - The `Transductiverepresentation` desirves a huge warn that this is a problem of several
    apporachs in the literature; - The `The task-pair confound.` I am against it, the problem of isolates the previus
    MTLnet wiht the check2hgi, is that the check2hgi is a checking embeeding so the poi-classification would recive a
    data-leack.
35. Sobre o future works tenho outros pontos que considero essenciais de serem detacados e discutidos: - Melhor
    integração do check2hgi, hoje ele possui um arch que varias partes são acopladas como o Poi2vec, poderiamos tentar
    fazer algo mais integrado; - O testar o uso de outras abordagens modernas de MTL, usando soft-sharing; - Testar com
    mais categorias além de 7; - no check2hgi testar hypergraphs, assunto envolga no contexto the mobility; - Executar
    para mais datasets não U.S; - Testar cascate no junto ao MTL; - O embedding já serve para tentar trainar para o
    next-poi, as vezes podemos analisar alguma ou outra feature que podemos adicionar, mas do jeito que está hoje já
    conseguimos usar, basta modificarmos a pipeline de inputs e criar uma cabeça para o next-poi e acopla-la no nosso
    joint-model; (Eu vejo esse sendo o mais promissor de todos.)
36. Eu gostaria de uma avalaição critaca da conclusão eu tenho a impressão que ela está em um bom caminho, mas ainda
    falta algo para ela ficar melhor. Compare com o que os articles/dissertacao/exemples fazem nas dissertações deles.
    Ainda sobre a conclusão meu maior problema está sendo com o `The consolidated answer` esse tem um conteudo bastante
    interessante, mas parece se focar muito em numeros que já foram mostrados nos artigos, assim acho que aqui seria um
    lugar para mostra os numero mais de forma geral ficando na narrativa da resposta final achada. Essa parte ela bem
    importante, pq ela fecha o arco do artigo ela tem que ser prazerosa e facil de sere lida. O fluxo em alto nivel: ```
    Question and thesis-> Chain of cause and effect (explain the chain of discovers that leaves to the resutls) ->
    Show what we got wrong in your initial thesis ->
    Connect to the real lesson and results through the lens of the discovers.
    ```
37. 
    


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
