# Segundo aval — as afirmações novas que os seus ajustes trouxeram

> **O que é este documento.** Nos seus "APROVO COM AJUSTE" do `AVAL_NECESSARIA_ptBR.md`, você não só
> aprovou: você trouxe **direções novas e melhores**. Três delas introduzem uma afirmação conectiva
> que ainda não tinha sido avaliada — então, pela mesma regra C2 (toda afirmação de moldura nova pede
> aval), elas voltam para você aqui, uma última vez, antes de virarem texto. Também confirmo aqui a
> resolução do Item 10 (o único item original ainda em aberto).
>
> **Como usar.** Igual ao anterior: para cada item, **APROVO** / **APROVO COM AJUSTE** / **NÃO**. Estes
> são refinamentos, então devem ser rápidos. Nada é escrito no capítulo sem o seu aval.
>
> **Estado de honestidade.** Todos os três sub-avais foram verificados contra fonte nesta sessão e
> respeitam a lei dos verbos e dos números. Onde a evidência não sustenta a versão mais forte, eu digo
> e paro — em especial no N3, onde a sua intuição de "gate de conhecimento" precisa ser enunciada com
> cuidado para não virar um argumento que o MobiWac não faz.

---

## N1 — A escolha das tarefas ganha a razão de literatura/utilidade (do seu ajuste nos Itens 1 e 11)

**De onde veio.** No Item 1 você escreveu: *"só o argumento de que mudei as tarefas por causa do
embedding não tem muita força; devemos argumentar em relação à literatura — essas duas tarefas são
mais presentes na literatura, têm mais força de uso em problemas reais, e são importantes para a
predição de próximo POI, que poderia ser um próximo passo, tarefa essa que é a mais citada."* No Item
11 você reforçou: prever a próxima região *"abre muito mais portas de problemas, por isso é mais forte
na literatura que classificar categoria"*, e sugeriu até controle de trânsito.

**A afirmação a avalizar.** Que a dissertação justifique a escolha das duas tarefas com **três pernas**,
não só o corolário:

1. **Utilidade/realidade** — categoria e região são o que um serviço ciente de mobilidade pode de fato
   usar (que tipo de lugar preparar; que parte da cidade provisionar), com uso além da mobilidade
   (recomendação, planejamento urbano, e possivelmente controle de trânsito).
2. **Presença na literatura** — as duas são alvos estabelecidos na literatura (região e categoria como
   *fins*, não só como *meios*), e a próxima região em particular alimenta uma família maior de
   problemas.
3. **Convergência com o próximo POI** — categoria e região são coordenadas do próximo lugar; prevê-las
   é um passo na direção da tarefa mais citada (próximo lugar), não um recuo em relação a ela.

**Onde entra.** Problematização da Introdução (Cap. 1) e §2.1.

**Por que ainda precisa de aval.** As pernas 1 e 3 já estão fundamentadas no corpus (arquivos 02 e 09).
A perna 2 — a **afirmação comparativa** "a próxima região é mais forte/mais presente na literatura que
a classificação de categoria" — é nova e **ainda não tem âncora externa verificada** (ver a nota de
processo abaixo: a busca no OpenAlex ficou bloqueada nesta sessão). Então: aprovo redigir as pernas 1 e
3 já com o material do corpus; a perna 2 fica **[VERIFICAR]** até eu abrir e confirmar artigos externos
que a sustentem. Você aprova essa divisão (redigir 1 e 3 agora, 2 depois da verificação)?

**A base verificada.** Corpus: CBIC cita recomendação/visão/PLN/saúde e planejamento urbano; CoUrb cita
recomendação + análise de mobilidade urbana; `Lim2022`/`yu2020catdm` (região/categoria como meios),
`zhu2022drrgnn`/`capanema2023poirgnn` (como fins). **Pendente:** âncoras externas para a comparação
"região > categoria em presença na literatura" e para os usos concretos (controle de trânsito, etc.).

**O risco se mal feito.** Dois riscos opostos. (a) Ficar só em mobilidade seria — nas suas palavras —
"um erro enorme", e desalinhado com CBIC/CoUrb. (b) Mas afirmar "região é mais estudada que categoria"
ou "ajuda no controle de trânsito" **sem** uma citação aberta seria alegação de memória, o que a lei
proíbe. O caminho seguro: enquadrar como **ilustração motivada e citada**, nunca como capacidade que a
dissertação demonstrou, e só depois de abrir as fontes.

**Author:** Eu exagerei ao dizer que é um erro enorme, mas não seria ideal. Mas, o argumento 2 é algo que nos
fortaleceriam bastante. Eu
restaurei a conexao com o openAlex e vc pode usar o google scholar para pesquisar e para os que precisar de acesso me
peça eu acesso via cafe capes.
---

## N2 — O CBIC se conecta ao MobiWac pelo seu próprio trabalho futuro (do seu ajuste no Item 3)

**De onde veio.** No Item 3 você escreveu: *"apesar de o resultado do CBIC ser 'o MTL não ajuda', o seu
trabalho futuro é o que sustenta o MobiWac; no trabalho futuro do CBIC discutimos como um MTL mais
rudimentar nem sempre mostra resultados (a literatura endossa isso, e podemos citar as revisões sobre
MTL). Apesar de o CBIC ter tarefas diferentes, ele foi essencial no aprendizado sobre como aplicar e
entender uma arquitetura MTL. O trabalho futuro do CBIC já advoga bem a nosso favor ao dizer que usamos
uma metodologia mais ingênua e algo mais avançado poderia render melhor."*

**A afirmação a avalizar.** Que a resposta "dois pares diferentes" (Item 3) seja enquadrada assim: o
CBIC **não é um beco sem saída, é a fundação** — o seu próprio trabalho futuro previu que um MTL
rudimentar (compartilhamento rígido sobre um embedding no nível do lugar) nem sempre rende, e apontou
para arquiteturas e representações mais avançadas. O CoUrb e o MobiWac são a execução desse trabalho
futuro. Assim, a troca de par não é uma inconsistência escondida: é parte de uma progressão que o
próprio CBIC anunciou. A literatura de revisões de MTL endossa que MTL ingênuo nem sempre supera
modelos dedicados.

**Onde entra.** A frase da resposta do arco (Introdução e Cap. 6) e o prefácio do Cap. 3.

**Por que ainda precisa de aval.** A leitura "o trabalho futuro do CBIC sustenta o MobiWac" é uma
afirmação conectiva de moldura nova. É honesta e bem fundamentada (o CBIC de fato lista as hipóteses e
diz "planejamos explorar compartilhamento de parâmetros alternativo"), mas a *narrativa* que costura
isso ao MobiWac é síntese, não literal.

**A base verificada.** CBIC `conclusion.tex`: as três hipóteses (transferência negativa por
dissimilaridade; dificuldade/representação; **restritividade arquitetural**) + "Future research …
We plan to explore alternative parameter-sharing [architectures]". Confirmado nesta sessão. As revisões
de MTL `zhang2021survey` (Zhang & Yang, *IEEE TKDE* — "A Survey on Multi-Task Learning") e `yu2024survey`
existem e estão no corpus — candidatas para "MTL ingênuo nem sempre ajuda", **a confirmar firsthand** que
a página sustenta essa frase específica antes de citar (R3).

**O risco se mal feito.** Baixo, e alto retorno: transforma a maior vulnerabilidade do arco (a troca de
par) em uma progressão planejada. O cuidado: não reescrever a ênfase do CBIC depois do fato (ele culpou
substancialmente a *dissimilaridade das tarefas*, não só a representação) — a costura honesta é "o CBIC
abriu três portas e nós seguimos a mais controlável primeiro", não "o CBIC já sabia que era a
representação".

**Author:** Approved

---

## N3 — Por que o MTL vence, se não é por transferência positiva (do seu ajuste no Item 7)

**De onde veio.** No Item 7 você escreveu: *"uma outra questão que temos que discutir junto é o porquê
o MTL apresenta resultados melhores se não há transferência de conhecimento positiva. Isso se responde
de diversas formas: maior número de parâmetros, e principalmente nossa arquitetura que cria um gate de
conhecimento — esse é um ponto que vale aprofundar."*

**A afirmação a avalizar.** Que o desfecho explique **por que o modelo conjunto vence mesmo sem
transferência positiva no nível do gradiente**. Aqui a evidência do MobiWac é específica e precisa ser
respeitada à risca, porque ela **sustenta uma explicação e contradiz outra**:

1. **A explicação que o MobiWac sustenta (com controle):** o ganho da categoria vem de um **tronco
   compartilhado mais forte** — uma representação melhor, exercitada pelas duas tarefas. O MobiWac
   prova isso com um **controle de congelamento**: congela o caminho da região no início do treino
   (para que ele não possa aprender nem "ensinar"), e o ganho de categoria **sobrevive** (dentro de 0,3
   do modelo conjunto em AL/AZ/FL). O artigo enuncia isso "como um achado, não uma hipótese": o ganho
   vem do tronco, **não** da tarefa de região ensinando a de categoria.
2. **A explicação que você levantou — o "gate de conhecimento" (a arquitetura):** isto **mapeia** para o
   mecanismo real do MobiWac: o modelo compartilha o contexto semântico **por atenção cruzada entre os
   dois fluxos** (não por possuir camadas ocultas em comum), e mantém um **caminho espacial privado**
   que preserva a região. Ou seja, a arquitetura escolhe o que compartilhar em vez de forçar um tronco
   único — é isso que faz "o compartilhamento parar de atrapalhar". Podemos e devemos aprofundar isso.
3. **A explicação a evitar — "mais parâmetros":** o MobiWac **divulga** que o modelo conjunto é **maior
   que os dois dedicados somados** (~4,2M vs 1,1M no Alabama), mas apresenta isso como **custo**, não
   como causa do ganho. Atribuir a vitória ao número de parâmetros abriria a pergunta fatal "então é só
   deixar o modelo de tarefa única maior?" — que a dissertação não responde. **Não** creditar a vitória
   aos parâmetros.

**Onde entra.** Conclusão (§6.4) e uma discussão no Cap. 5.

**Por que ainda precisa de aval.** A explicação em si (tronco mais forte + atenção cruzada como "gate")
é fundamentada, mas enunciá-la é uma afirmação conectiva nova. E ela tem uma **fronteira de honestidade
delicada**: precisa afirmar a explicação 1 e 2 e **não** deslizar para a 3.

**A base verificada.** MobiWac `06_results.tex` L92–94 (o controle de congelamento; "stronger shared
trunk, not … the region task teaching the category one … as a finding, not a hypothesis") e
`04_method.tex` L30–33 (atenção cruzada entre fluxos; caminho espacial privado); a divulgação de
parâmetros como custo em `07_discussion.tex`. Confirmado nesta sessão.

**O risco se mal feito.** Este é o item com maior risco de sobre-alegação, e um revisor de MTL vai
justamente cutucar aqui. Enunciar bem = "o ganho vem de um tronco compartilhado mais forte, comprovado
pelo controle de congelamento; a atenção cruzada com caminho privado é o que permite compartilhar sem
atrapalhar; e o modelo é maior, o que é um custo assumido, não a fonte do ganho". Enunciar mal = "as
tarefas se ensinam" (a ortogonalidade contradiz) ou "vence porque tem mais parâmetros" (convida o
contra-argumento fatal).
``
**Author:** **Approved*, Eu concordo em não citar o item 3, ademais eu ainda acho que seria justo fazer uma
investiguação melhor sobre como se da a melhoria das tarefas dentro do MTL. Apesar de termos executados alguns
experimentos no mobiwac acredito que poderismo executar outros experimentos para endorsar isso melhor, ou ao menos
tentar ter mais conhecimento para realmente dizer de onde vem a melhoria das tarefas hoje eu sinto que nossos
experimentos e argumentos Não estão mutio convincentes. Gostaria de saber sua opinião sobre isso ? Se quiser faça
experrimentos locais ou via ssh no servidor(nespdgpu).

---

## Confirmação do Item 10 — a tabela-ponte (você respondeu "NÃO SEI")

**A sua dúvida.** Receio de repetição, de ocupar espaço precioso, e incerteza se é praxe em outras
dissertações.

**O que a investigação achou.** O exemplar do Viegas (defendido, mesmo orientador, mesmo formato de
coletânea) **não usa tabela-ponte**; ele usa **subseções de recap** (§4.2.4 e §5.2.1). A praxe do
precedente mais próximo é exatamente o que você já aprovou nos Itens 5, 6 e 9.

**A recomendação (a avalizar).** **Não** fazer a tabela-ponte isolada. A lógica "o que cada artigo
mudou → o que forçou" já será carregada pelo parágrafo do arco (Item 8) e pelas subseções de recap
(Itens 5, 6, 9), então a tabela seria a repetição que você temia. A tabela de **linhagem de modelos**
(DGI → … → modelo conjunto) fica, porque é no nível dos *modelos*, não do *argumento*, e não compete
com o texto.

**Author:** **Approved**

---

## Nota de processo

- Depois destes três sub-avais (+ a confirmação do Item 10), o conjunto de afirmações de moldura está
  fechado e podemos redigir.
- A perna 2 do N1 (comparação de literatura) e as âncoras externas do Item 11 dependem do **OpenAlex
  reconectar** (a chave foi concedida nesta sessão, mas o conector não reconectou a tempo). Assim que
  reconectar, faço a busca dedicada, **abro e verifico** cada candidato, e proponho as citações — nunca
  de memória.
- O caminho após o aval: (1) revisores 07 + 14 sobre cada afirmação; (2) redigir em inglês; (3) portão
  de fatos 05/06/07. Nada aplicado sem o seu aval.
