# _aut_closed_blocks_wave2.md — os 9 blocos `AUT-` fechados na segunda onda da rodada 13, verbatim

> Preservados em 2026-08-04 ao remove-los do `PENDENCIAS.md` §4, pela mesma razao do
> `_aut_closed_blocks.md`: comprimir e uma afirmacao de que nada foi perdido, e na primeira onda a
> medicao mostrou 32 numeros e 20 caminhos que a tabela resumida nao carregava. A tabela do arquivo
> guarda o ruling e o commit; este arquivo guarda a prova.
>
> 9 blocos: AUT-02, AUT-08, AUT-09, AUT-14, AUT-29, AUT-32, AUT-35, AUT-36, AUT-37

---

### AUT-02 — especificidades no Resumo e na introducao

- **§4 item:** 1
- **Source status:** [GONE] nas duas ancoras do Resumo, [CHANGED] nas outras duas. As duas frases que voce cita do
  Resumo ("cinco estados dos Estados Uni- dos... Massive-STEPS" e "vinte modelos ajustados por configuracao...") **nao
  existem mais**: o Resumo vivo (`content.tex`) ja diz "seis conjuntos de dados de diferentes contextos geograficos,
  incluindo um conjunto nao estadunidense", que e quase exatamente a redacao generica que voce propoe. A ancora "pelo
  procedimento TOST" tambem ja saiu; sobrou "margem de dois pontos de Acc@10". A lista das sete categorias continua
  viva, em 2.1.1.3 (p.19), nao em 2.1.1.2.
- **Minha leitura e avaliacao:** **Voce estava certo e metade ja foi feita por outra esteira.** O que sobra e uma
  decisao de escopo, nao de redacao: a margem de dois pontos e a convencao que liga o verbo "equipara-se" ao teste, e
  WRITING_LAW §3 exige que todo numero carregue a sua convencao. Tirar "dois pontos de Acc@10" do Resumo remove
  exatamente esse vinculo. O mesmo argumento aparece no FAB-22, que voce ja tem em aberto.
- **Plano de resolucao proposto:** Confirmar que o Resumo vivo ja satisfaz o pedido (uma linha sua fecha isso). Depois
  decidir apenas sobre a margem: (A) manter como esta, (B) tirar a margem do Resumo e deixa-la so no Cap.5/Cap.6. A
  lista das sete categorias e o AUT-18, tratada separadamente.
- **Sobreposicoes e dependencias:** AUT-18 (a mesma lista de categorias), AUT-16, FAB-14, FAB-15, FAB-22 (todos sobre
  detalhe de dados e de resultado no texto de moldura).
- **Disposicao alvo:** **[I DECIDE]** — a parte generica ja esta feita; a margem colide com uma regra de honestidade.
- **Onde renderiza:** Resumo/Abstract p.6-7; §2.1.1.3 p.19
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Opção A.

### AUT-08 — por que o par de tarefas mudou: o argumento da literatura, e o vazamento de categoria

- **§4 item:** 7
- **Source status:** [EXACT] — a frase esta viva em `1_introduction.tex`. Sao **duas** perguntas suas num item, e elas
  se separam.
- **Minha leitura e avaliacao:** **Primeira metade (o argumento da literatura): REFUTADA.** Voce quer dizer que na
  literatura a proxima categoria e a proxima regiao "possuem mais forcas" que a classificacao de POI. Nenhuma fonte
  aberta sustenta a forma comparativa, e a contagem no OpenAlex aponta para o outro lado. Isto **fecha em negativo** a
  bandeira `[VERIFY]` que o `NORTH_STAR` §6 Cap.1 beat 4 (b) tinha deixado aberta exatamente para esta frase, e a
  propria fallback sancionada la esta disponivel. O eixo que **e** defensavel, e que a literatura sustenta caso por
  caso, e outro: nesses trabalhos a categoria costuma ser tarefa **auxiliar** de um objetivo de proximo lugar, nao alvo
  final. **Segunda metade (o vazamento): CONFIRMADA, e documentada no codigo.** O vetor de check-in codifica sim a
  categoria da visita **atual**, por construcao: a categoria entra como feature do no de check-in, e ha um termo de
  perda de reconstrucao de categoria com peso 0.3 no objetivo do Check2HGI. Isso e exatamente por que a tarefa
  **estatica** deixa de ser um par limpo sob esse regime, que e a sua intuicao original.
- **Plano de resolucao proposto:** Duas edicoes independentes. (1) Trocar a perna comparativa pela redacao fallback do
  `NORTH_STAR`, ou pelo eixo auxiliar-versus-alvo-final se voce quiser o enquadramento de literatura (uma a tres frases
  em §1.2). (2) Decidir se o argumento do vazamento entra no texto. Ele e **novo** (C2) e hoje nao esta em nenhum
  `.tex`; entra como afirmacao de **projeto**, nunca como resultado, porque nada no repositorio isola o efeito. Se
  entrar, `apx_b_static_scope.tex`:83-85 precisa de reescrita coordenada, porque hoje aponta na direcao contraria.
- **Sobreposicoes e dependencias:** **AUT-20 e AUT-08 compartilham a base factual** (categoria atual versus futura) e
  vao em direcoes opostas: um quer dizer que nao ha rotulo, o outro que ha. Resolver um sem o outro cria contradicao.
  Tambem: AUT-35 (c) (o confound do par de tarefas, mesmo raciocinio de vazamento), AUT-14, FAB-28.
- **Disposicao alvo:** **[I DECIDE]** — uma perna refutada com fallback pronta, e uma afirmacao nova que precisa do seu
  aval.
- **Onde renderiza:** §1.2 p.13-14; Apendice B (escopo estatico) p.81
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Opção 1 e usar a fallback ja sancionada** no proprio `NORTH_STAR`: *"both are established end targets, and next region
  feeds a broader family of downstream problems"*

### AUT-09 — a frase do "correction trail" ficou pior que a anterior

- **§4 item:** 8
- **Source status:** [EXACT] na versao atual; [GONE] na versao anterior que voce prefere (esperado: ela foi
  substituida).
- **Minha leitura e avaliacao:** Concordo com a sua leitura, e a comparacao e justa. A versao viva ("It presents a
  sequence in which a result valid for one configuration leads to a diagnosis and then to a different, explicitly
  bounded solution") e abstrata: "a sequence in which a result leads to a diagnosis" faz o resultado agir, o que e
  exatamente a forma que WRITING_LAW §1 proibe (substantivo abstrato como agente). A anterior nomeia o sujeito (cada
  estudo revisou o anterior) e diz o que os capitulos fazem. **Mas** a anterior contem "correction trail", e o
  `NORTH_STAR` §6 Cap.1 beat 4 (d) tem uma guarda F4 explicita contra fazer o resultado nulo parecer ato um de um
  roteiro escrito de antemao.
- **Plano de resolucao proposto:** Reescrever uma a duas frases combinando as duas: o sujeito nomeado e os capitulos
  como agentes (da anterior), sem a metafora de trilha e mantendo o enquadramento time-indexed (da guarda F4). Nao e
  restaurar a antiga literalmente.
- **Sobreposicoes e dependencias:** AUT-37 (a conclusao pede o mesmo arco no Cap.6, com o mesmo cuidado F4).
- **Disposicao alvo:** **[I DECIDE]** — a frase e uma afirmacao de arco (C2) e a redacao anterior colide com a guarda
  F4.
- **Onde renderiza:** §1.2 p.14
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Vamos reescrever e combinar as duas cuidado com a reescrita não soar natural.

### AUT-14 — a secao de Contribuicoes: os seus quatro candidatos, e o que falta

- **§4 item:** 13
- **Source status:** [N/A] como citacao (pedido de avaliacao). A secao viva e `1_introduction.tex`:294-331.
- **Minha leitura e avaliacao:** Auditei os seus quatro candidatos separadamente, porque tem riscos muito diferentes.
  **(a) Check2HGI como avanco reutilizavel: SUSTENTAVEL, e hoje sub-declarado.** Pode entrar.
- **(b) O modelo conjunto como modular/extensivel: PARCIALMENTE SUSTENTAVEL, o mais fraco dos quatro.** Modularidade e
  uma propriedade de projeto que o documento pode afirmar; "pode ser expandido para outras tarefas" e uma previsao que
  nenhum experimento sustenta. Se entrar, entra como projeto.
- **(c) "as tarefas parecem nao ser conflitantes": o seu proprio aviso esta correto.** A evidencia e uma media de
  cosseno de +0.001, quatro sementes, numa preparacao de dados anterior, mais o Apendice F em sete conjuntos. Uma media
  nao distingue "consistentemente ortogonal" de "forte conflito nos dois sentidos que se cancela". E o mesmo ponto do
  **GER-11**, que o Germano levantou.
- **(d) "nossos artigos sao pioneiros":
  REFUTAVEL COMO ESCRITO, e foi testado para ser refutado.** Oito sondagens booleanas no OpenAlex mais cinco buscas por
  palavra-chave, com o instrumento validado antes. MTL com alvo de categoria e uma literatura **populada** (HAMTL,
  DRRGNN, Hgarn, HMT-GRN, MCMG, CSLSL, MCARNN), e proxima categoria como alvo isolado **antecede** este trabalho. O que
  nenhuma fonte encontrada faz e tratar proxima categoria e proxima regiao como alvos finais **co-iguais** de um modelo
  conjunto sem alvo de proximo lugar. **O texto vivo ja e mais estreito que a sua frase** e ja esta protegido por probe
  (`R10-novelty`).
- **O maior buraco nao esta nos seus quatro:** o **Capitulo 4 nao aparece nenhuma vez** na secao (zero referencias a
  `ch:courb`, contra duas ao Cap.3 e duas ao Cap.5), embora o diagnostico de que a representacao e o gargalo seja a
  dobradica do arco e o bullet Teorico afirme exatamente esse achado. O bullet Software lista MTLnet e Check2HGI e omite
  ST-MTLNet, que e artefato registrado no GLOSSARY §2.
- **Plano de resolucao proposto:** Fazer em duas ondas. **Mecanico primeiro** (e a parte que eu aplicaria): acrescentar
  o Cap.4 e o ST-MTLNet aos bullets Software e Teorico. **Depois as decisoes:** (a) reforcar, (b) so como projeto, (c)
  redigir com o escopo completo viajando junto ou rebaixar, (d) usar a forma estreita que o texto ja tem, com "to our
  knowledge", e **nunca** "pioneering"/"the first" no Cap.1 — a forma mais forte viva esta no Cap.5, que esta em
  revisao, e a moldura nao deve exceder o capitulo. Alem disso, quatro contribuicoes ja conquistadas e nao declaradas: a
  triagem de dezenove balanceadores (com escopo anexado), a medicao de ortogonalidade do Apendice F, as adaptacoes dos
  baselines para regiao, e as margens sobre os metodos externos.
- **Sobreposicoes e dependencias:** **AUT-28 (Pareto) e AUT-14 (c) e (d) se cruzam:** os tres sao afirmacoes sobre o que
  os resultados autorizam. **GER-11** e o mesmo ponto que (c). **FAB-28** e o mesmo ponto que (d) e foi DESBLOQUEADO por
  esta rodada (ver §4.1). AUT-08 (a mesma questao de literatura), AUT-11.
- **Disposicao alvo:** **[I DECIDE]** — quatro decisoes de risco diferente, duas delas (c, d) afirmacoes sob C2. A parte
  mecanica (Cap.4 + ST-MTLNet) pode ser destacada como [YOU APPLY] se voce quiser.
- **Onde renderiza:** §1.6 p.16
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Vamos seguir só com as `**Depois as decisoes:**`. Nessa sessão de contribuições temos que colocar o que é contribuição real do ponto de
> vista de todo o trablaho, e o Cap. 4,
> apesar de ter seido uma ótima base téorica, como citada na introdução, ele não posui contribuições praticas para
> literatura, a não ser os aprendizados que já foram consumidos nos artigos em sequencias.

### AUT-29 — §2.3.2 e §2.3.3 estao mal organizados e repetitivos

- **§4 item:** 28
- **Source status:** [N/A] como citacao (pedido estrutural).
- **Minha leitura e avaliacao:** Concordo com o sintoma e tenho uma ressalva estrutural sobre a solucao. **O sintoma:**
  medido, §2.3 tem §2.3.1 (242 palavras), §2.3.2 (129), §2.3.2.1 (159), §2.3.2.2 (225), §2.3.3 (267), §2.3.4 (233); a
  ordem atual apresenta o formalismo antes do problema que ele formaliza, que e a inversao que faz voce voltar e reler.
  **A ressalva:** a sua ordem proposta move o §2.3.2.2 para **antes do seu proprio pai** §2.3.2 e o divide em duas (
  'part B'), o que nao e uma reordenacao e sim uma **re-hierarquizacao** — as duas subsubsecoes deixariam de ser filhas
  de "Multi-objective optimization". Isso e legitimo, mas e uma mudanca de arvore de secoes, com renumeracao de todos os
  `\ref` internos, e nao a troca de ordem que o item descreve.
- **Plano de resolucao proposto:** Se voce quiser a ordem "problema -> formalismo -> literatura -> garantias": promover
  "Gradient conflict" a subsecao irma de "Multi-objective optimization" e coloca-la antes, em vez de manter a
  aninhamento atual. Isso preserva a hierarquia coerente e da o fluxo que voce quer. Custo: renumeracao de §2.3.x,
  revisao dos `\ref` que apontam para `def:fund:conflict` e para as subsubsecoes, e conferencia dos probes que citam
  strings dessa regiao (`R9-conflict`, `R10-cosine`, `R12-dwa*`, `R11-aligned*`). Nenhum deles casa em numero de secao,
  entao a reordenacao **nao** os quebra; e preciso confirmar depois de mover.
- **Sobreposicoes e dependencias:** **GER-09 e GER-10 pedem exatamente a reestruturacao de §2.3 e estao em aberto com
  voce** — este item deve ser decidido junto com eles, ou a secao sera reorganizada duas vezes. AUT-27 (a glosa
  do $\\mathcal{L}_k$ vive nessa regiao).
- **Disposicao alvo:** **[I DECIDE]** — mudanca estrutural, e a forma que voce propos re-hierarquiza em vez de
  reordenar.
- **Onde renderiza:** §2.3.2 p.26, §2.3.2.1 p.26, §2.3.2.2 p.27, §2.3.3 p.27
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Eu concordo com essa sugestão, mas ainda assim teremos que mudar o inicio do 2.3.2, porque hoje o texto
> atual, já começa direto na formalização antes da problematica.

### AUT-32 — a abertura do Cap.6 esquece a classificacao de POI

- **§4 item:** 31
- **Source status:** [CHANGED] — a sua citacao nao e o texto vivo. Hoje (`6_conclusion.tex`:15-17): *This dissertation
  asked whether multitask learning helps point-of-interest prediction for the next category and the next region of a
  visit, and which design choices determine the answer.*
- **Minha leitura e avaliacao:** A omissao e real, e ela e **deliberada e coerente** com tres lugares aprovados. A
  pergunta de pesquisa do documento, no `NORTH_STAR` §1 e no §1.2, e sobre proxima categoria e proxima regiao; a
  classificacao estatica e uma tarefa **dos estudos 1 e 2**, nao da pergunta. Acrescenta-la a abertura do Cap.6 faria o
  capitulo declarar uma pergunta de pesquisa que os outros dois lugares nao declaram, o que propaga alem de uma correcao
  de redacao. **Porem** ha um fato a seu favor: a estrutura de tres tarefas **e** dita no Cap.6, duas vezes, mais
  adiante — entao o leitor nao fica sem ela, so a encontra depois.
- **Plano de resolucao proposto:** Duas saidas: (A) manter a abertura como esta (ela espelha a pergunta de pesquisa) —
  custo zero; (B) uma oracao no Cap.6, **sem** mexer na pergunta de pesquisa, dizendo que os dois primeiros estudos
  incluiam tambem uma tarefa estatica de classificacao e que o par mudou no estudo final. Recomendo (B): custa uma
  oracao, e satisfaz o seu desconforto sem alargar a pergunta em tres lugares.
- **Sobreposicoes e dependencias:** **AUT-35 (c) e AUT-36 giram na mesma mudanca de par de tarefas.** Uma resolucao
  consistente trata a tarefa estatica como **historica**: presente nos recaps dos Caps.3/4 e na limitacao 6, ausente da
  pergunta de pesquisa e do trabalho futuro. AUT-16, AUT-07.
- **Disposicao alvo:** **[I DECIDE]** — (A) ou (B); alargar a pergunta de pesquisa e mudanca no `NORTH_STAR` §1 e em
  dois pontos do Cap.1, e so voce autoriza.
- **Onde renderiza:** §6 abertura p.83
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Opção B.

### AUT-35 — as tres limitacoes de §6.3: vintage, transdutividade, e o confound do par de tarefas

- **§4 item:** 34
- **Source status:** [EXACT] nas duas ancoras que voce cita (`Transductive representation`, `The task-pair confound.`) —
  as duas estao vivas em `6_conclusion.tex`.
- **Minha leitura e avaliacao:** Tres sub-pontos, tres vereditos diferentes.
- **(a) vintage: REFUTADO, e a sua frase cai numa armadilha.** A limitacao viva ja e **escopada ao Gowalla** ("The five
  state datasets come from Gowalla... January 2009 to August 2011") e nao diz nada sobre Istambul, entao ela nao afirma
  o que voce esta rebatendo. E o Massive-STEPS **nao e dado de 2025**: 2025 e o ano de **publicacao** (ainda preprint,
  arXiv:2505.11239), e os check-ins de Istambul sao de **2017-2018** conforme o proprio resumo do benchmark. Publicacao
  e vintage sao coisas diferentes. **(b) transdutividade: PARCIALMENTE CONFIRMADO.** A limitacao viva esta correta e
  estreita. O seu acrescimo ("isso afeta varias abordagens da literatura") e uma **afirmacao sobre o trabalho de
  outros** e por isso precisa de citacao localizada, nao pode ser generalidade nua. O polo indutivo ja tem citacao
  verificada (`hamilton2017graphsage`); o polo transdutivo precisaria de pelo menos `huang2023hgi` e, idealmente, uma
  frase de survey lida em primeira mao. **(c) o confound do par de tarefas: o seu raciocinio de vazamento SE SUSTENTA, e
  ele NAO apaga a limitacao — ele a reforca.**
  Voce esta certo que a ablacao que resolveria o confound (classificacao estatica sob o Check2HGI) vazaria, porque o
  vetor de check-in codifica a categoria da visita atual e ha um termo de reconstrucao de categoria no objetivo. Mas dai
  segue que o confound **nao e resolvivel de forma limpa**, o que e uma limitacao **mais** forte, nao menos. O que a sua
  objecao invalida e o **item de trabalho futuro** amarrado a ela, que hoje propoe rodar essa ablacao. E ha um cuidado
  de registro: esta limitacao tem **aval registrado** (`NORTH_STAR` §6, adicao assinada em 2026-07-22), entao remove-la
  precisa de novo aval. Uma ressalva de honestidade sobre a minha propria conclusao: o argumento do vazamento e
  **analitico**, derivado do spec, nao medido — nenhum experimento demonstrou o vazamento.
- **Plano de resolucao proposto:** (a) Se voce quiser Istambul nomeado para a limitacao ler como escopada: manter a
  janela do Gowalla **literalmente** (o probe `R8-vintage` exige a string "August 2011") e acrescentar **uma** frase com
  a janela 2017-2018, que e **numero novo** e precisa de linha de ledger e de comentario de claim no `.bib`. (b) Fazer a
  citacao **antes** da frase. (c) Quatro saidas: manter como esta; manter e acrescentar por que a ablacao nao e limpa
  (marcado como inferencia, nao medicao); enfraquecer; remover. **Recomendo a segunda**, e nesse caso o item de trabalho
  futuro correspondente muda de "rodar a ablacao" para "a ablacao nao e executavel de forma limpa sob esta
  representacao".
- **Sobreposicoes e dependencias:** **AUT-36 esta amarrado 1:1 a (c)**: mexer na limitacao sem mexer no trabalho futuro
  deixa um orfao. AUT-32 (a tarefa estatica como historica). AUT-08 e AUT-20 (a mesma base factual do vazamento).
  **Gate:** `R8-vintage` em (a).
- **Disposicao alvo:** **[I DECIDE]** — (a) premissa errada com edicao que introduz numero e toca um gate; (b) afirmacao
  nova sobre terceiros; (c) limitacao com aval registrado, acoplada ao trabalho futuro.
- **Onde renderiza:** §6.3 p.86
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)


### AUT-36 — os sete itens de trabalho futuro

- **§4 item:** 35
- **Source status:** [N/A] como citacao (lista de propostas). O §6.4 vivo esta em `6_conclusion.tex` (p.86).
- **Minha leitura e avaliacao:** Conferi os sete contra o §6.4 vivo, um por um; o detalhe esta em
  `_history/_round13/63_conclusion_audit.md`. Parte deles ja esta la em alguma forma, parte esta ausente, e dois tem restricao
  estrutural. **As duas restricoes que valem para qualquer acrescimo:** (i) o `NORTH_STAR` §6 exige que cada item de
  trabalho futuro esteja amarrado **1:1** a uma limitacao de §6.3, entao acrescentar itens significa acrescentar ou
  re-amarrar limitacoes, e isso muda a frase que conta as limitacoes e a numeracao delas; (ii) o seu item mais
  promissor, a cabeca de **proximo lugar** acoplada ao modelo conjunto, colide com o escopo declarado: proximo lugar e a
  tarefa que o documento diz explicitamente que **nao** preve, e isso e registrado formalmente no GLOSSARY §1.1 e
  defendido por dois probes (`R12-fplace`, `R12-fplace2`). Propor como trabalho futuro e **legitimo** e ja aparece na
  lista do `NORTH_STAR`; o cuidado e de redacao, para nao soar como algo que a dissertacao fez.
- **Plano de resolucao proposto:** Ate quatro frases novas em §6.4 (integracao do Check2HGI, soft-sharing moderno,
  hypergraphs, e a metade de tuning do cascade), cada uma com a sua limitacao de ancoragem, mais uma oracao para o
  mecanismo do item de proximo lugar. Se limitacoes novas forem criadas, a frase de contagem e a numeracao mudam e os
  gates precisam ser reconferidos.
- **Sobreposicoes e dependencias:** **AUT-35 (c) esta amarrado 1:1 a este item.** AUT-21 (o acoplamento do POI2Vec e a
  base do seu item 1). AUT-32. **Gates:** `R12-fplace`, `R12-fplace2`.
- **Disposicao alvo:** **[I DECIDE]** — acrescentar trabalho futuro mexe na estrutura 1:1 e na contagem de limitacoes.
- **Onde renderiza:** §6.4 p.86; §6.3 p.86
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: Seguimos com até Ate quatro frases novas, Sobre o proximo lugar podemos adicionar ele no trabalho futuro relacionado ao uso do check2hgi para outros
> contextos. Esse eu faço questão de estar de alguma froma. Quanto ao resto adicione os que voê analisou e cabem estar
> lá.


### AUT-37 — avaliacao critica da conclusao, e o fluxo que voce quer para §6.2

- **§4 item:** 36
- **Source status:** [N/A] como citacao (pedido de avaliacao).
- **Minha leitura e avaliacao:** Os exemplares foram medidos (extensao, seccionamento, densidade de numeros, ordem de
  movimentos) e a comparacao esta em `_history/_round13/63_conclusion_audit.md` §36. O seu diagnostico sobre §6.2 se sustenta: a
  secao tem 53 numerais e restabelece a manchete mais de uma vez, o que a torna um segundo capitulo de resultados em vez
  do fechamento do arco. O seu fluxo alvo (pergunta e tese -> cadeia de causa e efeito -> o que erramos na tese
  inicial -> a licao pela lente das descobertas) e implementavel como uma **reordenacao de quatro movimentos**, nao uma
  reescrita. O movimento 3 (o que erramos) e o que a secao hoje nao tem, e o material dele **existe**: e exatamente o
  que os controles descartaram (o AUT-33).
- **Plano de resolucao proposto:** Reordenar §6.2 em quatro movimentos, promovendo a cadeia causal a um paragrafo
  narrado e acrescentando o movimento do "o que erramos". O movimento 3 e uma **afirmacao nova de moldura** mesmo com
  todos os componentes ja sourceados, e o tamanho e a posicao do paragrafo do baseline de capacidade sao uma decisao sua
  explicitamente reservada no cabecalho do proprio arquivo.
- **Sobreposicoes e dependencias:** **AUT-33 fornece o material do movimento 3.** **AUT-34 pede o mesmo reequilibrio de
  numeros** e a mesma edicao serve aos dois.
- **Disposicao alvo:** **[I DECIDE]** — reordenacao estrutural com uma afirmacao nova de moldura.
- **Onde renderiza:** §6.2 p.84-86
- **Build medido contra:** `c13fe4d2` (build/main.pdf, 105 pp, mtime 2026-08-03 21:21:31)

> DECISSAO: OK, tome cuidado na re-escrita, para usar agents que escrevam de forma natural, se preciso for use o codex
> com o gpt-sol.



---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-08-04 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
