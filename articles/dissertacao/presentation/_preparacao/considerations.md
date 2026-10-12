# considerations.md — as revisões do autor sobre o deck, organizadas

> **O que este documento é.** A lista de mudanças que o autor pediu no deck de defesa, reorganizada
> por assunto, re-ancorada por conteúdo e com cada item marcado como *pronto para implementar*,
> *bloqueado por investigação* ou *decisão do autor*.
>
> **O que ele não é.** Não é a especificação dos slides. A especificação é o
> [`SLIDES.md`](../SLIDES.md), e este documento é a fila de entrada dele.
>
> **Original preservado** em [`archive/considerations_RAW_2026-08-26.md`](considerations_RAW_2026-08-26.md)
> (548 linhas, redação do autor, intacta). Os extras estão em
> [`archive/extra_RAW_2026-08-26.md`](extra.md) e foram absorvidos na §7.
>
> **Reorganizado em 2026-08-26** pela sessão `gate`. Nada foi removido: todo item do original tem um
> ID aqui. Onde eu discordo ou onde há conflito com a lei do projeto, está dito no item, não escondido.
>
> **Coordenação — fechada pelo autor em 2026-08-26.** `gate` = conteúdo e estrutura (este documento
> e o `SLIDES.md`). **`ppt` = a única mão no `slides/main.tex`.** A sessão `presentation` **será
> desligada** pelo autor; o histórico dela está absorvido aqui.

---

## ✔ Decisões do autor — 2026-08-26

Fecham quatro itens que estavam bloqueando o resto. **Não reabrir.**

| #         | Decisão                                                                                                                                                                                                                                                                                                    | Efeito                                                                                                                                                                                                              |
|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **AUT-1** | **O relógio não é problema desta rodada.**                                                                                                                                                                                                                                                                 | A §⏱ fica como registro, não como restrição. Os itens marcados ⏱ podem ser especificados normalmente                                                                                                                |
| **AUT-2** | **O S6 sai, e a regra §8.13 do PLANO fica revogada.** A contribuição aparece **uma vez só**, na conclusão (S50)                                                                                                                                                                                            | Fecha `X1`, `I11`, `K9`. ⚠ **O `[BLOCO-CONTRIBUIÇÃO]` do cabeçalho do `SLIDES.md` tem três cópias sincronizadas — a remoção precisa desfazer a sincronia, não só apagar um slide**                                 |
| **AUT-3** | **O S3 perde a tabela de resultados.** *"Revendo como foi a apresentação do a defesa de referência, remover os resultados do slide 3 corta tempo de prosa e deixa a linha de raciocínio mais limpa."* O S3 fica com a **pergunta** e a **restrição de modelo único**                                                     | Fecha `I6`, `I7`, `I8`, `D5`, `Q7`, `Q8` **de uma vez** — os nomes de dataset saem junto com a tabela, então a exceção da Seção 1 deixa de ser necessária. Ver **N1**                                               |
| **AUT-4** | **Travessão: a regra é por função e continua valendo.** *"Não existem duas situações. Usar o travessão para glosa e usar o travessão no meio de um texto — o que eu peço para remover, e temos que remover, é o travessão no texto corrido."*                                                              | Fecha `X4`, `G3`, `Q4`. **Confirma a decisão de 24/08.** O separador de rótulo, o título de bloco e o subtítulo **ficam**; sai só o que faz trabalho de prosa dentro de frase completa                              |
| **AUT-5** | **Os DOIS carimbos saem — `Task stamp` e `Metric stamp`. A regra §8.5 fica revogada.** *"Durante a prosa isso não vai ser discutido, polui o slide, e é algo fácil de ser explicado caso alguém pergunte."*                                                                                                | Fecha `X2`, `G7`, `Q16`, `M2`, `M31`, `A5`, `A6`, `A20`. **Sete slides perdem o rodapé: S15, S16, S21, S24, S25, S28, S29.** ⚠ **libera altura em sete slides de uma vez** — é a maior devolução de caixa da lista |
| **AUT-6** | **O S45 é reorganizado por tarefa, com as externas nomeadas.** *Next-category:* **POI-RGNN · Dedicated · Joint**. *Next-region:* **ReHDM · STAN · Dedicated · Joint**. E a mensagem: **em ambas as tarefas o nosso modelo supera os modelos da literatura** — tratada como achado, não como nota de rodapé | Reescreve `C45`–`C54` e a §6.5. ⚠ **traz duas afirmações novas para validar** — ver **N2**                                                                                                                         |
| **AUT-7** | **O S18 e o S28 SAEM.** S18: *"já explicamos esse protocolo nos fundamentos compartilhados"*. S28: *"pode remover, eu vou conversar com meu professor; qualquer coisa re-adicionamos"*                                                                                                                     | Fecha `D3`, `Q2`, `Q5`, `M11`, `M15`, `A14`–`A16`. ⚠ **três verificações obrigatórias antes de executar — ver N3**                                                                                                 |
| **AUT-18** | ✅ **EXECUTADA 26/08.** O slide 30 (*Check2HGI: a fourth level below the place*) ficou **SÓ COM A IMAGEM**. *"Vamos tirar os textos e deixar só a imagem, mas é bom revisitar ela."* | Substituiu o `C15` (que era *figura + dois pontos*). **Zero marcadores, `Overfull` zero.** ⚠ **E ela não dependia do gênero da figura — isso foi um erro meu.** A `fig1_dataflow` estava a `width=0.50\textwidth`, **exibida pela METADE** do tamanho para que foi desenhada; tirados os marcadores ela entra no natural (136,6 × 62,4 mm contra 66,2 úteis) e o texto interno passa de ilegível a legível. **O gênero segue aberto e não bloqueia: trocar pela `c2h_flow` é uma linha** |
| **AUT-17** | **A tabela de Category Classification ENTRA, com a ressalva de vazamento em nota de rodapé.** *"Podemos mostrar a tabela com uma nota de rodapé sobre o leak."* **E o overlay da chapa do HGI está DESCARTADO** — *"vai ser melhor ter tudo em uma imagem."* | Fecha `A17`, `§6.3` e a dependência da §14.6. **Destrava o slide 24** |
| **AUT-11** | **`Q6`: o item 6 do slide 48 (*task-pair confound*) SAI.** *"Já esclarecemos isso durante o texto o porquê teve essa mudança, e se por ventura alguém perguntar podemos responder em prosa."* | Fecha `K30`, `Q6`. **Meu parecer contrário fica registrado e superado** — a decisão é dele, e a justificativa é boa: o texto entregue explica a mudança de par |
| **AUT-12** | **`Q13`: o slide 10 (*The idea these three share*) SAI**, e o **item 4 do slide 9** (*graph infomax*) é substituído por: *"**Contrastive infomax** — an approach to create representations using two pairs, one positive and one corrupted, so we don't need labels to train."* | Fecha `F10`, `F11`, `F13`, `D3`, `Q13`. ⚠ **muda a numeração de novo: 50 → 49.** E **`contrastive` entra no `GLOSSARY`** (AUT-14) |
| **AUT-13** | **`Q14`: a linha de `Controls` do slide 40 SAI.** *"Tinha alguns problemas com esse teste, principalmente por ele ter sido feito pre-leak."* ✅ **Verificado, e é pior do que isso — ver R-β corrigido** | Fecha `C42`, `Q14`, `R-β` |
| **AUT-14** | **`Q18`: SIM, autoriza os termos novos no `GLOSSARY`** — `stream`/`tower`, `Markov-K floor`, `contrastive` | Fecha `V3`, `V4`, `Q18`, e destrava a `AUT-12` |
| **AUT-15** | **`Q15`: a gradação das três condições fica.** E ele acrescenta a **própria lista de contribuições**, em `wrapup/Questions_author.md:98` | Fecha `Q15`. Ver **§13** |
| **AUT-16** | **`Q10` e `Q17`: os slides EXTRAS não são meu escopo.** *"Não é trabalho de você tocar em nada extras, isso será trabalho de outro agent."* | **A §7 deste documento sai do meu escopo.** Fica como registro para o agente dos extras |
| **AUT-10** | **`Q3` respondida: o `Metric stamp` sai de TODOS os lugares** — *"eu já vou falar isso em prosa ao apresentar os resultados dos cap. 3 e 4"* — **inclusive do slide 13**, que era o único candidato a guardá-lo. **E a informação do `Task stamp` passa a viver no slide 6** (as tarefas) | Fecha `X3`, `T2`, `F23`, `Q3`. **O bloco `Two traps` deixa de existir por inteiro.** Ver **N4** |
| **AUT-9** | **A Seção 2 vira: POI related work → as tarefas (S4 ⊕ S15 fundidos) → o eixo + baselines → MTL Fundamentals.** O item 4 do S7 atual (*related work de MTL em POI*) vai para o slide de **MTL Fundamentals**. O slide de MTL fica **único**, cortando o que não couber                                      | Fecha `D1`, `D2`, `R1`–`R7`. Ver **D1** para a tabela da nova ordem                                                                                                                                                 |
| **AUT-8** | ✅ **CUMPRIDA.** O diagrama do HGI esperava a descrição do autor — ela chegou, está em [`hgi_draw.txt`](hgi_draw.txt), e **a chapa já está integrada** (`slides/main.tex:759`, impresso **22**). ~~O diagrama do HGI espera a descrição do autor~~                                                                                                                                                                                                                                      | **`§6.2`, `A9` e `Q11` estão DESBLOQUEADOS.** Sobra um item, e é cosmético: `figures/src/hgi_flow.tex:2` ainda diz "impresso 23" |
| **AUT-19** | **A pergunta de pesquisa perde o parêntese, na forma do objetivo geral.** *"Eu queria tirar o parênteses, como eu havia pedido"* → *"prefiro a segunda forma"*. A redação fechada: **_Does multitask learning help next-category and next-region prediction, and what does the answer depend on?_** | Fecha o parêntese pedido. **Não é paráfrase**: é `1_introduction.tex:249-250` (objetivo geral) virado para interrogativa, com o `depend on` de `:133-134`. ⚠ **Tira `point-of-interest prediction` da âncora da defesa** — o termo ambíguo que a armadilha de nome do impresso 6 existe para desambiguar. Enviada à `ppt` em 26/08 |
| **AUT-20** | **A chapa do HGI mantém a seta do negativo saindo do ramo corrompido**, mesmo não sendo o que o método faz. Decidido com **os dois renders lado a lado**: a `tikz` construiu a variante fiel ao código, ele comparou e ficou com a dele. | ⚠ **Não reabrir — a evidência já foi apresentada duas vezes.** No HGI o negativo daquela fronteira é outro lugar da tabela **original** pareado com a mesma região (`HGIModule.py:281-283`, `neg_pois = pos_poi_emb[neg_poi_idx]`); o ramo corrompido serve à fronteira região–cidade. **Consequência:** a resposta oral do bloco `S27` deixa de ser rede de segurança e vira **ativa** — se alguém da banca conhecer o HGI, ela é necessária. **Não gastar fala da trilha principal com ela** |
| **AUT-30** | **Os cinco cortes de fala ENTRAM.** 684 palavras, 4:53 | Fala de **52:28 → 47:35**, margem de **2:25**. ⚠ **Aplicar por TÍTULO:** os cinco alvos mudaram de número (protocolo 36–39 → **34–37**; `Result 3` → **`Result 2`**). Textos em [`SPEC_EXTRAS.md (anexo, sec. `CORTES_FALA.md`)`](SPEC_EXTRAS.md) |
| **AUT-31** | **A coda do slide 48 SAI.** O fecho passa a ser a pergunta dividida e respondida | Sai *"The negative result was not an obstacle… It was its first half"*. **A frase continua sendo o fim da FALA** — sai só da tela |
| **AUT-32** | **O slide 15 (`Two losses…`) migra para o `MTL Fundamentals`** (impresso 8). *"Aquilo é agnóstico aos três estudos."* | ⚠ **Dois custos levantados e decididos assim mesmo:** (a) o slide 8 **já carrega as duas classes** comprimidas — é **fusão com corte**, o marcador de balanceamento é **substituído**, não somado; (b) o slide 16 passa a usar `Pareto-stationary` com a definição **oito slides atrás** em vez de um. 🛑 **O disclaimer de Pareto é ocorrência única no deck e tem de viajar** |
| **AUT-33** | **`linear CKA` e `Markov-K floor` entram no `GLOSSARY`** | ✅ **Escritos em 27/08** (`GLOSSARY.md §4`). 🛑 **O `linear CKA` entrou com LIMITE DE ESCOPO no próprio registro:** a dissertação **nunca o rodou** — ele vive só em `wrapup/ESTUDOS_DEFESA.md §4.5`. **Um slide pode explicar o que CKA é; nenhum pode reportar valor, comparação ou conclusão de CKA.** ⚠ O `Markov-K floor` estava autorizado desde a `AUT-14` e **nunca tinha sido executado** |
| **AUT-34** | **A `fig2_model` troca a nomenclatura** (`semantic/spatial stream` → **Next Category / Next Region**) **e o slide 32 recebe mais conteúdo** | ⚠ **A figura é do repositório da TESE**, não chapa da `tikz` — `src/figures/mobiwac/`. Instrução dada: **só os dois rótulos**, resto byte a byte. ⚠ **O defeito passou despercebido porque a figura estava a 0,495 e os rótulos eram ilegíveis; a ampliação para 0,62 não o criou, tornou-o visível** |
| **AUT-35** | **As erratas ficam para DEPOIS da defesa.** O *submitted / under review* em cinco lugares não se toca agora | Registrado para o depósito final |
| **AUT-29** | **O impresso 38 (*Result 1: the geometry of the vectors*) SAI da trilha principal e vira extra.** *"O slide 39 já mostra evidências sobre a melhora do Check2HGI em relação ao HGI."* **Sem ressalva compensatória no 39** — *"essa cláusula só aparece como necessidade quando se mostra essa imagem; como não teremos a imagem, não teremos a pergunta."* | ✅ **Concordo, e o argumento dele é mais forte do que ele formulou:** o 39 prova que a representação **move a tarefa** (carga da tese); o 38 prova **por quê** — e mecanismo responde a pergunta, não sustenta afirmação. **Os quatro protocolos do slide estão na lista de estudo dele** (`wrapup/Questions_author.md:32-36`) como perguntas esperadas: **é promoção para o lugar certo, não corte.** ⚠ **A ressalva única do deck** (*"the same geometry does not separate regions: the benefit is category-only"*) **viaja com o slide** e passa a ficar colada ao gatilho. **Relógio: 54:00 → 52:28; com os cinco cortes, 47:25 — 2:35 de margem, a primeira vez abaixo do teto.** Renumerar `Result 2/3` → `1/2`: dois títulos + as duas primeiras palavras das falas, **zero referências cruzadas** |
| **AUT-24** | **O último terço muda de GÊNERO, não de densidade.** *"São os últimos slides e neles a plateia já não lê mais, só escuta — então é importante ser o mais didático e simples possível."* Atinge **42 · 43 · 45 · 46 · 47** | ⚠ **Três réguas numéricas falharam antes disto** (palavras na tela · palavras por unidade · objetos de leitura): nenhuma separava os slides que ele citou dos que não citou. **O que separa é POSIÇÃO** — sete dos últimos oito. **A intervenção passa a ser "converter frase em etiqueta", e o conteúdo não é cortado: volta para a fala, onde já está.** Relógio inalterado |
| **AUT-25** | **Slide 26: Opção A SEM a terceira frase** — *"o próximo slide 27 fala exatamente isso"* | ✅ **A edição dele é melhor que a minha proposta.** Eu tinha recomendado a Opção B para resolver o salto "dois limites → três camadas"; **tirando a linha, o salto deixa de existir** |
| **AUT-26** | **Slide 48: a pergunta de pesquisa volta, dividida em duas metades, respondida pelas frases que já estavam na tela** | 🛑 **`Under this design` NÃO PODE SAIR.** Dividir a pergunta cria expectativa de sim-ou-não, e um "sim" nu seria a afirmação mais forte do deck — **em categoria, cinco das seis diferenças são NÃO RESOLVIDAS**. O escopo é verbatim de `6_conclusion.tex:35` e está com o argumento inteiro no `.tex`. **A coda (*"It was its first half"*) está VIVA e aguarda o sim/não do autor** |
| **AUT-27** | **Slide 47: o bloco de trabalho futuro estava propondo o que o Cap. 5 entrega.** Corrigido | 🔴 **Falha minha, apontada pelo autor:** *"você é o agente que deveria averiguar e validar o conteúdo, não averiguou e nem validou o que estava entrando."* O slide propunha *"a shared trunk with cross-attention"* e o `5_mobiwac/04_method.tex:28` diz do modelo entregue *"the shared trunk, a **cross-attention stack** of two blocks"*. **Duas das três propostas já estavam entregues.** Causa: o item veio da lista crua dele, escrita sobre o **MTLnet do Cap. 3**, e **perdeu o escopo de capítulo** ao entrar na Conclusão. **Eu auditei a lista de contribuições e não a de trabalhos futuros — o mesmo arquivo, na mesma leitura** |
| **AUT-28** | **Os títulos que ele cobrou nominalmente**, aprovados: `Nash-MTL` e `Three limits of the decomposition`. E **46/47 perdem o numeral** | Fecha a colisão **cinco × seis limitações** com o volume (`6_conclusion.tex:205`), sem reabrir a `AUT-11`. A fala do 46 perde o *"cinco experimentos"* junto |
| **AUT-21** | **Fundamentos: as tarefas vêm ANTES do trabalho relacionado.** Inverte os impressos **5** e **6**. *"O público passa a conhecer os conceitos necessários antes de entrar na discussão da literatura."* Levantado num ensaio | ⚠ **Revoga o primeiro passo da `AUT-9`**, que punha *POI related work* primeiro. **Ensaio é a evidência certa para reverter.** ✅ **A evidência está dentro dos slides:** o 5 diz *"none is a direct baseline for **the targets studied here**"* — alvos que só o 6 define; e o 5 ensina *"next-POI = next place, same task"* enquanto a **armadilha de nome vive no 6** (`main.tex:238`, ocorrência **única**). **Hoje a correção chega depois do mal-entendido** |
| **AUT-22** | **Seção 3: o embedding vem ANTES da arquitetura.** Inverte os impressos **13** (MTLnet) e **14** (DGI) | ⚠ **O argumento do autor não se aplica aqui, e o real é outro.** A figura `cbic_mtlnet_arch` rotula as entradas genericamente (*Next POI Input* · *Category Input*) — **DGI não aparece nela**, ao contrário da chapa da Seção 4. **O que sustenta a inversão:** hoje o DGI **interrompe a linha de MTL** (MTLnet 13 → DGI 14 → Two losses 15 → Nash 16), e a fala do MTLnet atravessa a interrupção (*"o detalhe que vai importar **daqui a dois slides**"*). Invertido, a linha fica contígua e a referência vira *"no próximo slide"*. **É o mesmo defeito que o autor corrigiu na Seção 2 em 26/08** |
| **AUT-36** | **O controle de dimensão igual do Cap. 4 (192 vs 64) NÃO entra no slide de trabalhos futuros.** *"É trabalho futuro do Cap. 4 de um artigo que já mudamos muita coisa; não acho que vale voltar nisso."* | Fecha o último ponto aberto do ITEM 4 da rodada de 27/08. O item é real e está no volume (`6_conclusion.tex:79`, *"Chapter 4 therefore calls for an equal-dimension control"*) — **fica no texto, sai da tela.** ⚠ **Consequência a segurar:** se a banca perguntar pelo resultado do Cap. 4, a ressalva de largura (a comparação **não é width-matched**, 192 contra 64) continua sendo a resposta honesta e **está só no volume agora** — não há apoio na tela nem na fala |
| **AUT-23** | **Seção 4: HGI e codificadores ANTES da arquitetura.** Move os impressos **22** e **23** para antes do **21**, preservando a ordem entre eles | ✅ **Confirma a recomendação que eu já tinha levantado e validado.** É a inversão com a evidência mais forte das três: a figura do 21 **contém uma caixa escrita `PoiEncoder + HGI`** e outra `Time2Vec` — a banca lê os nomes antes de eles serem explicados. ⚠ **Custo: os impressos 20 e 21 dividem UMA fala de 40 s** (`main.tex:703`); ela tem de rachar, e a cauda viaja com a figura |

### N1 · O que a saída da tabela do S3 obriga a verificar

O S3 é hoje o único lugar da abertura onde o veredito é dado. Se ele sai, três coisas mudam:

1. **A promessa da fala muda.** A fala atual diz *"a resposta eu dou agora, no minuto três, e não no fim, porque daqui
   em diante cada slide é resposta a uma pergunta que eu já fiz."* Essa frase **deixa de ser verdadeira** e tem de ser
   reescrita.
2. **`INTRODUZ` do ledger.** O veredito era introduzido em 1.3. Passa a ser introduzido no **S46**. O `SLIDES.md`
   precisa mover a etiqueta, senão o ledger fica com um elemento sem dono.
3. **Um risco fica MENOR, não desaparece.** ⚠ *(correção — eu tinha escrito que ele saía junto.)*
   A frase *"equivalent to zero within half a point"* estava na fronteira da lei que proíbe
   `match`/`empata`/`ties` como veredito (risco **F-33**). **Medido: ela sobrevive em dois lugares** —
   `main.tex:1724` (S46, *"bounding all six within half a point"*) e `main.tex:2171` (reserva `B1-2`, verbatim). O que a
   AUT-3 remove é **a instância da ABERTURA, que é a única sem o co-texto *"unresolved"* ao lado.** Isso é ganho real,
   mas **F-33 continua aberto no S46.**

---

### N2 · O que a AUT-6 obriga a validar antes de ir para a tela

O autor quer duas afirmações, e elas têm forças diferentes:

**(a) "superamos a literatura no next-region"** — ✅ **verdadeira célula a célula.** Conferi a Tabela 10 entregue contra
o **melhor externo de cada dataset**:

| dataset  | melhor externo | Dedicated | Joint | margem sobre o melhor externo |
|----------|----------------|----------:|------:|------------------------------:|
| AL       | ReHDM 65,38    |     70,12 | 69,24 |               **+3,9 / +4,7** |
| AZ       | ReHDM 53,00    |     59,48 | 59,04 |               **+6,0 / +6,5** |
| Istanbul | ReHDM 69,33    |     75,16 | 75,08 |               **+5,8 / +5,8** |
| FL       | STAN 72,99     |     76,69 | 76,54 |               **+3,6 / +3,7** |
| CA       | STAN 58,52 †   |     63,48 | 64,54 |               **+5,0 / +6,0** |
| TX       | STAN 61,67 †   |     64,94 | 66,15 |               **+3,3 / +4,5** |

> **Os dois modelos superam o melhor externo nos seis datasets, por 3,3 a 6,5 pontos.** A afirmação
> se sustenta.
>
> 🛑 **Três ressalvas obrigatórias, e nenhuma é opcional:**
> 1. **as marcas † e ‡ são do próprio documento**: STAN roda **folds parciais** (TX 4/5, CA 2/5,
>    semente 0) e ReHDM roda **uma única semente** em TX e CA. Não são células cheias;
> 2. **o piso Markov-1 de região (51 a 72 Acc@10) está acima do HMT-GRN nos seis e do STAN em
     > quatro.** Derivando por dataset: AL 62,26 · AZ 51,23 · IST 65,06 · FL 72,47 · **CA 59,09** ·
>    TX 60,10. **Em California o melhor externo (STAN 58,52) fica ABAIXO do piso não-aprendido.**
>    Isso tem de estar num rodapé, senão a banca o encontra sozinha;
> 3. ⚠ **o autor pede para omitir o HMT-GRN, e a nota da Tabela 10 o chama de *"the primary external
     > comparison"* por ser o único region-native.** Omitir o primário e mostrar as referências
>    **inverte a hierarquia do próprio capítulo** — ainda que, por acaso, mostre os externos mais
>    FORTES, o que torna a comparação mais dura e não mais fácil. **Precisa de nota, e o slide extra
     > de adaptação que o autor propôs é o lugar certo.**

**(b) "definimos métricas para o next-region"** — ❌ **não se sustenta, e a busca fechou.**
Acc@10 é canônica, o piso de Markov é baseline padrão desde Cuttone et al. (2016), e o desconto de OOD é adaptação do N²
do HMT-GRN. **E a tarefa também não é nova** — o DRRGNN (TKDD 2022) já prevê região como alvo final em multitarefa com
categoria de POI.

> ✅ **Mas o que sobra no lugar é MAIS FORTE, e já está nos dados entregues: os três sistemas
> publicados ficam abaixo de um piso de Markov de primeira ordem — HMT-GRN nos SEIS datasets, STAN em
> quatro, ReHDM em três.** Esse é o pontapé, e é honesto.
> **A especificação completa do slide, com a redação, os números e as ressalvas, está na §6.5.**

⚠ **E uma instrução da AUT-6 tem de ser revista: o HMT-GRN precisa FICAR na tabela.** É a única baseline pareada e
region-native, e é ela que carrega o caso 6/6 abaixo do piso. Ver §6.5.

### N3 · A AUT-7 verificada — você está certo, com três buracos

Grep sobre o deck inteiro (principal **e** Série B). **O S14 cobre o protocolo, literalmente:**

| elemento do S18                                     | onde mais está                                                                         | veredito                                 |
|-----------------------------------------------------|----------------------------------------------------------------------------------------|------------------------------------------|
| 5-fold estratificado por amostra                    | S14 (`:552`)                                                                           | ✅ coberto                               |
| orçamento cheio de épocas, sem parada antecipada    | S14 (`:554`)                                                                           | ✅ coberto                               |
| cada tarefa na melhor época dela                    | S14 (`:554`) e S48                                                                     | ✅ coberto                               |
| médias e desvios sobre os cinco folds               | S14 (`:555`)                                                                           | ✅ coberto                               |
| sem teste de significância                          | S14 (`:555`)                                                                           | ✅ coberto                               |
| *"reports differences, never a verdict"*            | S14 (`:557`), **mesma frase**                                                          | ✅ **redundância literal**               |
| corpus de Florida, 990.518 check-ins                | S12 (`:509`)                                                                           | ✅ coberto                               |
| as sete categorias                                  | S12 e S15                                                                              | ✅ coberto                               |
| **20.301 usuários · 65.009 lugares**                | **só na reserva `B4-4`** (`:2727`)                                                     | ⚠ **sai do deck principal**             |
| **usuários com menos de CINCO visitas descartados** | **nenhuma outra ocorrência no arquivo**                                                | 🛑 **desaparece do deck**                |
| **uma semente**                                     | **não está no S14.** Só no S48 (`:1806`, a escada, no fim do deck) e na reserva `B2-2` | ⚠ **some do ponto da fala do Cap. 3**   |
| janelas **não sobrepostas** de nove visitas         | S15 diz "nine visits" sem a janela; S40 (`:1460`) só por **negação**, 22 slides depois | ⚠ **coberto só por contraste, e tarde** |

> ✅ **A remoção é segura para o protocolo.** O que ela custa são **três fatos de setup**, e o mais
> caro é o **filtro de cinco visitas**, que não existe em nenhum outro lugar.
>
> **Proposta: o S14 ganha UMA LINHA de setup dos Caps. 3/4** — *"non-overlapping windows of N visits;
> users with fewer than five visits discarded; one seed"* — e o S18 sai inteiro. Custo: uma linha num
> slide que acabou de ganhar a altura do `Metric stamp`. Alternativa: mandar os três para a reserva
> `B4-4`, que já carrega os números de corpus.
>
> 🛑 **E as duas colisões entre pedidos seus continuam de pé:** se o `T1` remover *"The verb law"* do
> S14 **e** o S18 sair, a lei dos verbos some do deck. Se o `C31` remover a frase de janelas do S40
> **e** o S18 sair, a janela dos Caps. 3/4 some. **A linha proposta acima resolve as duas.**

### N4 · O que a AUT-10 obriga, e ela se paga

**O `Metric stamp` sai de todo lugar, e a convenção métrica não fica em nenhum slide.** O autor a diz
**em prosa**, ao apresentar os resultados dos Caps. 3 e 4. Isso fecha a colisão que a `X3` registrava
— não havia saída boa enquanto ele quisesse a informação e não quisesse falá-la; ele resolveu
escolhendo falá-la.

> **Consequência: o bloco `Two traps` do slide 13 deixa de existir por inteiro.** *"The task pair
> changes"* já tinha migrado para o slide 6 (as tarefas); a convenção métrica vai para a fala. **O
> slide 13 fica só com o protocolo e com a linha de setup herdada** — e é justamente essa altura que
> a linha de setup precisava.

**E a armadilha de nome muda de casa, o que resolve um aperto.** O autor pediu que a informação do
`Task stamp` viva no **slide 6**. Ela existe hoje como um `alertblock` no **slide 4**
(*"In Chapters 3 and 4, 'Next-POI Prediction' means the next category, not the exact next place"*).

⚠ **Mas o slide 6 está em 0,930 de tinta, sem folga** — um `alertblock` novo custa ~28 pt e não cabe.

> ✅ **Saída: fundir com o bloco que já existe lá.** O slide 6 já tem um `alertblock` (*"Named to be
> excluded"*), e os dois blocos tratam **do mesmo assunto** — o que as palavras significam e o que não
> significam. Um bloco só faz os dois trabalhos, e custa **~10 pt em vez de ~28**:
>
> > **Two names, one warning.** *Next place* (Def. 2.9) is **named to be excluded** — no chapter
> > reports a result for it. And in Chapters 3 and 4, **"Next-POI Prediction" means the next
> > category**, not the exact next place.
>
> **E o slide 4 perde o `alertblock` inteiro**, devolvendo ~28 pt num slide que não estava pedindo —
> o que é folga líquida para o deck.

⚠ **Um cuidado que isto cria:** com os carimbos fora de todos os slides das Seções 3 e 4, **o slide 6
passa a ser o ÚNICO lugar do deck onde a armadilha de nome é dita.** Ela é lida uma vez, no minuto
quatro, e cobre trinta slides depois. **A fala dos Caps. 3 e 4 tem de dizer "próxima categoria", nunca
"próximo POI"** — não há mais rede embaixo.


## 🗺 As TRÊS numerações — e por que a conta não é um `−1` uniforme

> 🔴 **A TABELA DE FAIXAS ABAIXO É HISTÓRICA E NÃO SERVE MAIS PARA CALCULAR NADA. 26/08, 23h.**
> Ela mapeia um `alvo` de **50** contra um `hoje` de **51**. **O deck de hoje tem 49 impressos** — a
> `AUT-12` removeu mais um slide depois que ela foi escrita. **Quem usar as faixas erra por um em
> tudo acima do impresso 9.** Fica só como registro de como a migração foi planejada.
>
> ✅ **A fonte corrente do número impresso é o campo `Slide impresso:` de cada bloco do
> [`SLIDES.md`](../SLIDES.md)**, re-derivado do PDF construído em 26/08 e **verificado título a título,
> 49 de 49.**
>
> 🛑 **E o mesmo defeito estava vivo lá até agora, por 37 blocos.** O bloco `S8` (*The idea these
> three share*) continuou na lista ATIVA depois que a `AUT-12` removeu o slide, e **todo `Slide
> impresso:` a partir do 10 ficou deslocado em +1**. Arquivado e corrigido na mesma passada.
> **A lição não é o erro, é o mecanismo:** um número derivado que se escreve à mão **não sabe que
> ficou velho**. Nada no build reclama, e os dois números apontam para slides reais.

> 🛑 **Erro meu, corrigido em 2026-08-26.** A primeira versão desta tabela dava só `alvo → original`,
> e **o deck de hoje não é nenhum dos dois**: a Fase A já rodou (54 → 51), mas a fusão `4⊕15` é Fase B,
> então o alvo (50) ainda não existe. **Quem lesse "41" pensando em *Result 2* editaria *Result 1*, e
> nada no build reclamaria** — os dois números existem e apontam para slides reais.
>
> ⚠ **E o deslocamento NÃO é um `−1` constante.** Ele tem quatro faixas, porque a fusão consome um
> slide da Seção 1 (o impresso 4) e outro da Seção 3 (o impresso 14), e faz nascer um na Seção 2:
>
> | faixa | relação |
> |---|---|
> | alvo **1–3** | **= hoje 1–3** |
> | alvo **4–5** | = hoje **5–6** *(+1)* |
> | alvo **6** | **NASCE** da fusão de hoje **4** com hoje **14** |
> | alvo **7–13** | **= hoje 7–13** |
> | alvo **14–50** | = hoje **15–51** *(+1)* |

### 🔒 A convenção que elimina o problema de vez

**Todo slide é identificado por TÍTULO. O número vai junto, como conferência.**

> `slide 41 · "Result 2: one model, two tasks"`

**Se os dois discordarem, quem implementa PARA e pergunta** — não escolhe. O título é a identidade estável do frame; o
número é derivado e muda a cada remoção.

⚠ **Duas exceções, e elas precisam de tratamento próprio:**

- os **`\specialframe` de transição** — hoje impressos **19** e **26** — **não têm `\frametitle`**. Para esses, **o
  número é a única âncora**, e tem de ser lido do PDF. *(⚠ os números desta linha estavam errados: diziam 21 e 28,
  do mapa velho. Corrigidos e conferidos no PDF de 26/08.)*
- **dois grupos compartilham título:** os dois *Architecture or representation?* (hoje **20 e 21**) e os quatro *The
  protocol, in four steps* (hoje **34–37**). Nesses, **título + `\framesubtitle`**. *(⚠ idem: diziam 22–23 e 36–39.)*

### A tabela

|   alvo |       hoje |  orig. | slide                                                | o que muda                                                                          |
|-------:|-----------:|-------:|------------------------------------------------------|-------------------------------------------------------------------------------------|
|  **1** |          1 |      1 | Movement is regular, and services depend on that     | título → **Human Mobility** (`I2`); inverter itens 2 e 3 (`I1`)                     |
|  **2** |          2 |      2 | The ground: check-ins, mobility…                     | remover a menção a human mobility (`I3`)                                            |
|  **3** |          3 |      3 | The question, and the answer in one line             | **`\specialframe` + cartão; perde a tabela** (`AUT-3`); **+ a linha do next place** |
|  **4** |          5 |      5 | Three studies, in sequence                           | —                                                                                   |
|  **5** |          6 |      7 | Related work: POI prediction…                        | **perde os itens 3 e 4**; **+ a sinonímia** (`T4`)                                  |
|  **6** | **4 ⊕ 14** | 4 ⊕ 15 | **The tasks** *(NASCE)*                              | a fusão. **É o passo B1**                                                           |
|  **7** |          7 |      8 | The axis that separates this work                    | **+ o mapa de baselines com destaque** (`F2`)                                       |
|  **8** |          8 |      9 | **MTL Fundamentals**                                 | **+ o item 4** · **+ balancing method** · **+ `For this dissertation`**             |
|  **9** |          9 |     10 | The line this work stands on                         | —                                                                                   |
| **10** |         10 |     11 | The idea these three share                           | fusão no 9 é decisão do autor (`F10`)                                               |
| **11** |         11 |     12 | The evidence base: six datasets                      | **sem a linha das duas extrações de Florida** (`F15`)                               |
| **12** |         12 |     13 | The metric all three studies share                   | **+ Markov**; **sai** o item da cross-entropy                                       |
| **13** |         13 |     14 | The protocol of the first two studies                | **+ a linha de setup herdada** · o bloco `Two traps` sai                            |
| **14** |         15 |     16 | MTLnet                                               | figura maior · **sem carimbos**                                                     |
| **15** |         16 |     17 | DGI                                                  | **🆕 diagrama** (§6.1)                                                              |
| **16** |         17 |     19 | Two losses, one set of parameters                    | `M17` · ⚠ `M18` **não** construir a ligação Pareto ↔ negative transfer             |
| **17** |         18 |     20 | Nash-MTL                                             | `M22` · `M23` · `M26`                                                               |
| **18** |         19 |     21 | The null result, shown rather than asserted          | **sem carimbos** · `G4` nas duas tabelas                                            |
| **19** |         20 |     22 | A null with three suspects                           | ⚠ `V5`: *"expert-based routing"* → **Mixture-of-Experts**                          |
| **20** |     **21** |     23 | *(transição — sem `\frametitle`)*                    | —                                                                                   |
| **21** |         22 |     24 | Architecture or representation? *(texto)*            | **sem carimbo** · `A1` · `A3` · `A4`                                                |
| **22** |         23 |     25 | Architecture or representation? *(a arte)*           | **sem carimbos**                                                                    |
| **23** |         24 |     26 | HGI                                                  | **🆕 diagrama** (§6.2, bloqueado em `AUT-8`)                                        |
| **24** |         25 |     27 | Why these encoders                                   | ⚠ `V2`: *"fine class"* fora de escopo                                              |
| **25** |         26 |     29 | The diagnostic result is the sequential task         | **+ 🆕 a tabela de Category Classification** · **sem carimbos**                     |
| **26** |         27 |     30 | What the decomposition moved…                        | `A21`–`A26`                                                                         |
| **27** |     **28** |     31 | *(transição — sem `\frametitle`)*                    | `A27`–`A30`                                                                         |
| **28** |         29 |     32 | Three changes, each a consequence…                   | `C1`–`C6`                                                                           |
| **29** |         30 |     33 | Next region: the task…                               | `C7`–`C9`                                                                           |
| **30** |         31 |     34 | Why a per-visit representation is new…               | `C10`–`C12`                                                                         |
| **31** |         32 |     35 | Check2HGI: a fourth level below the place            | **🆕 figura refeita** (§6.4)                                                        |
| **32** |         33 |     36 | What each visit contributes                          | `C17` · `C18`                                                                       |
| **33** |         34 |     38 | The architecture: sharing by exchange                | **+ cross-attention** · `C24`–`C27`                                                 |
| **34** |         35 |     39 | The private spatial path…                            | `C28` · `C29`                                                                       |
| **35** |         36 |     40 | The protocol · 1 the unit of data                    | `C30`–`C32`                                                                         |
| **36** |         37 |     41 | · 2 what is measured                                 | `C33`–`C35`                                                                         |
| **37** |         38 |     42 | · 3 what is compared                                 | **+ a fórmula do joint-best**                                                       |
| **38** |         39 |     43 | · 4 how it is decided                                | `C38`–`C41`                                                                         |
| **39** |     **40** |     37 | The geometry of the vectors → **Result 1**           | *(já movido na Fase A)* · `C19`–`C21`                                               |
| **40** |         41 |     44 | Result 1 → **Result 2**                              | `C42`–`C44`                                                                         |
| **41** |         42 |     45 | Result 2 → **Result 3**                              | **🆕 tabela refeita** (§6.5)                                                        |
| **42** |         43 |     46 | The verdict, dataset by dataset                      | 🛑 ver §4C · **herda o `INTRODUZ` do veredito**                                     |
| **43** |         44 |     47 | The measured trade… → **Limitations and trade-offs** | `C58`–`C62`                                                                         |
| **44** |         45 |     48 | The ladder: three studies, three layers              | `K1` · `K2`                                                                         |
| **45** |         46 |     49 | The conditional answer                               | `K3`–`K8` · ⚠ `V1`                                                                 |
| **46** |         47 |     50 | The contribution → **Contributions**                 | a única cópia (`AUT-2`)                                                             |
| **47** |         48 |     51 | Six limitations, six next steps (1 of 2)             | `K21`–`K27`                                                                         |
| **48** |         49 |     52 | (2 of 2)                                             | `K28`–`K30`                                                                         |
| **49** |         50 |     53 | Closing                                              | `K31`–`K36`                                                                         |
| **50** |         51 |     54 | Acknowledgements → **Obrigado**                      | `K37`–`K40`                                                                         |

**Contagem por seção no alvo:** 4 · 9 · 7 · 7 · 16 · 7 = **50**.

---

## 🔧 Ordem de execução — e por que NÃO é "Seção 1 primeiro"

> Eu tinha proposto começar pela Seção 1, porque A2 e A3 já a determinam. **Está errado, por duas
> dependências que uma revisão adversarial encontrou.**

1. **A Seção 1 não fecha antes da D1.b.** O item `I10` (tirar a restrição de modelo único do S4) e o destino da exclusão
   de *next place* dependem de o S4 **migrar ou não** para Fundamentos — que é decisão da Seção 2. Executar a Seção 1
   primeiro é retrabalho garantido no S3 e no S4.
2. **Os artefatos 🆕 da §6 têm o maior tempo de produção e são independentes de tudo.** O próprio documento os chama de
   prioridade máxima, e o diagrama do HGI (§6.2) está **bloqueado no autor**
   (`Q11`). Se não começarem hoje, não existem na sexta.

### 🛑 A armadilha que a A2 cria, e que precisa ser resolvida ANTES de qualquer cirurgia

**Remover o S6 desloca o número impresso de TODOS os slides 7 a 54.** E **este documento inteiro ancora pelo número
impresso** (declarado na §0.1). Depois da primeira mudança estrutural, **todas as tabelas da §5 ficam stale.**

> **Instrução operacional, e ela não é opcional:** antes de executar AUT-2, AUT-3, D1, D2 ou D4, **converter
> as âncoras da §5 de número impresso para TÍTULO do slide.** Só então mexer na estrutura. O título é
> estável sob renumeração; o número não é.

### A ordem que as dependências realmente impõem

| #     | passo                                                                                                                                                                                                                                 | por quê                                                                     |
|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| **0** | **Hoje:** despachar as perguntas que gateiam mais itens — `Q2`, `Q3`, `Q5`, `Q11`, `Q14`, `Q15`, `Q16`, `Q19` — **e disparar em paralelo os artefatos §6.1 (DGI) e §6.4 (figura do Check2HGI)**, que não dependem de resposta nenhuma | maior tempo de produção, zero dependência                                   |
| **1** | **Converter as âncoras da §5 para título**                                                                                                                                                                                            | senão o passo 2 invalida o documento                                        |
| **2** | **Toda a cirurgia estrutural numa passada só:** AUT-2 (S6 sai) · AUT-3 (S3 perde a tabela) · D1 (Seção 2) · D2 (S19) · D4 (S37) · o que a D3 devolver · **e a renumeração**                                                           | mexer na estrutura duas vezes é o dobro do risco de estouro de caixa        |
| **3** | **Conteúdo slide a slide (§5) e as varreduras transversais** (G3 travessão, G4 tabelas, X2 carimbos)                                                                                                                                  | **nunca antes do passo 2** — senão edita-se slide que vai morrer ou fundir  |
| **4** | **Render página a página, com canária por frame**                                                                                                                                                                                     | o log não vê estouro; o `pdftotext` não vê o que não foi desenhado. Ver §4F |

---

## ⏱ O relógio — medido, e adiado por decisão do autor (AUT-1)

**Adiado. Não bloqueia nenhum item desta lista.** Fica o registro, medido por duas sessões independentes: a fala escrita
do deck principal soma **8.810–8.837 palavras ≈ 63 min a 140 ppm**, contra um teto de **~50 min** (Art. 23) e um
orçamento declarado de 47,7 min. **Folga real: ≈ −13 min.**

Duas coisas que valem para quando for:

- **cortar tela não compra relógio.** Duas varreduras tiraram 29% do texto de tela e **zero segundos**
  — a prosa não sumiu, mudou de lugar;
- **a única alavanca que corta os dois é trocar prosa por figura.** O deck tem **6 `\includegraphics`
  em 103 frames**, contra 706 `\textbf`. Um diagrama substitui fala; um marcador reescrito, não. **É por isso que os
  quatro artefatos da §6 são prioridade máxima** — eles atacam relógio e caixa ao mesmo tempo, e são os únicos que fazem
  isso.

---

## 0 · Como ler este documento

### 0.1 · A chave de numeração — leia antes de qualquer coisa

Existem **três numerações diferentes** em circulação neste projeto, e confundi-las já produziu retrabalho:

| Numeração                | Onde vive                            | S1 é…                                                  |
|--------------------------|--------------------------------------|--------------------------------------------------------|
| **Nº impresso no slide** | canto inferior direito do `main.pdf` | *Movement is regular…* (a capa **não** é numerada)     |
| **`Sn` do `SLIDES.md`**  | [`SLIDES.md`](../SLIDES.md)             | a **capa**                                             |
| **Página do PDF**        | `main.pdf`, 112 páginas              | capa. Slide impresso `n` = página `n+2` até o slide 47 |

> ⚠ **Não existe fórmula de conversão entre o `Sn` do `SLIDES.md` e o nº impresso.** Eu supus
> `S(n+1) = impresso n` e a sessão `ppt` mediu que **o deslocamento não é constante**: `S8`→7,
> `S12`→11, `S13`→12, mas `S28`→28. A reordenação da Seção 2 moveu blocos **sem renumerar**, porque
> doze referências cruzadas internas apontam para eles pelo número.
> **Ancore sempre pelo TÍTULO do slide, nunca pelo número.**

**Este documento usa o Nº IMPRESSO**, que é o que o autor lê na tela e o que a banca ouve (*"volte ao slide 14"*, regra
§8.10 do plano).

### 0.2 · A re-ancoragem — por que os números do original não batem

O `considerations.md` original foi escrito em duas passadas contra **duas versões diferentes do deck**. A Seção 2 foi
reorganizada quatro vezes entre as passadas (`a8ccc7cd` *9 slides viram 7* → `170b96e4` → `1627c5b9` → `372d4026` *o
slide de representação vira dois*), e a numeração deslizou.

Verifiquei item a item contra o `main.tex` vigente (mtime 2026-08-25 22:52, PDF de 22:55). O resultado:

| Bloco do original                                       | Contra qual versão foi escrito                                 | Correção aplicada                                                                                                                                                                                                                                                                                                       |
|---------------------------------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Os **6 primeiros bullets** (antes de `---- Introdução`) | deck **anterior** à reorganização (commit `a76405be` ou antes) | `slide 11` → **S14** · `slide 12` → **S7** · `slide 16` → **S15**                                                                                                                                                                                                                                                       |
| De `---- Introdução` até o fim                          | deck **atual**                                                 | bate 1:1, com **duas exceções**                                                                                                                                                                                                                                                                                         |
| `Slide 25 — representação visual do HGI`                | —                                                              | é o **S26** (o HGI)                                                                                                                                                                                                                                                                                                     |
| `Slide 25 — nota de rodapé`                             | —                                                              | é o **S25**, o segundo frame de *Architecture or representation?*. **Desambiguado por medição:** o S26 (HGI) **não tem rodapé nenhum** — nem `\footnote`, nem tira em corpo reduzido. O que o autor chama de "nota de rodapé" é a **tira do `Task stamp`**, e os dois frames de *Architecture or representation?* a têm |
| `Slide 32 — Scope`                                      | —                                                              | é o **S33** (o bloco `Scope` está em *Next region: the task…*)                                                                                                                                                                                                                                                          |
| `Slide 46L`                                             | —                                                              | é o **S46** (*The verdict, dataset by dataset*)                                                                                                                                                                                                                                                                         |

*(Verificado por reconstrução do `main.tex` em cada commit: no deck anterior o 11 era o único frame com *"The verb law"*
e *"Two traps"*, o 12 o único com *"the pair the first two studies attack"*, e o 16 o único com *"nine visits"*.)*

### 0.3 · O deck de hoje, para referência

**54 slides numerados + 49 páginas de reserva** (Série B, `\miniframesoff`, `[noframenumbering]`).

| #      | Título                                                            | | #      | Título                                                            |
|--------|-------------------------------------------------------------------|-|--------|-------------------------------------------------------------------|
| **1**  | Movement is regular, and services depend on that                  | | **28** | The caveat, then the number                                       |
| **2**  | The ground: check-ins, mobility, and what joint training promises | | **29** | The diagnostic result is the sequential task                      |
| **3**  | The question, and the answer in one line                          | | **30** | What the decomposition moved, and where it did not                |
| **4**  | What is predicted, and what is not                                | | **31** | *(transição)* With the architecture fixed…                        |
| **5**  | Three studies, in sequence                                        | | **32** | Three changes, each a consequence of the diagnosis                |
| **6**  | The contribution, in one block                                    | | **33** | Next region: the task, and why it is worth predicting             |
| **7**  | Related work: POI prediction and multitask learning               | | **34** | Why a per-visit representation is new in this line                |
| **8**  | The axis that separates this work                                 | | **35** | Check2HGI: a fourth level below the place                         |
| **9**  | How two tasks share a model, and how that fails                   | | **36** | What each visit contributes                                       |
| **10** | The line this work stands on                                      | | **37** | The geometry of the vectors                                       |
| **11** | The idea these three share                                        | | **38** | The architecture: sharing by exchange                             |
| **12** | The evidence base: six datasets, said once                        | | **39** | The private spatial path, and what the evidence does not separate |
| **13** | The metric all three studies share                                | | **40** | The protocol, in four steps · 1 the unit of data                  |
| **14** | The protocol of the first two studies, and two names that change  | | **41** | …· 2 what is measured                                             |
| **15** | One static task, one sequential task                              | | **42** | …· 3 what is compared                                             |
| **16** | MTLnet                                                            | | **43** | …· 4 how it is decided                                            |
| **17** | DGI: how it works ∣ why it was used                               | | **44** | Result 1: the representation, at every dataset                    |
| **18** | Setup, and the protocol declared                                  | | **45** | Result 2: one model, two tasks                                    |
| **19** | Two losses, one set of parameters                                 | | **46** | The verdict, dataset by dataset                                   |
| **20** | Nash-MTL, and what the chapter may claim about it                 | | **47** | The measured trade, and four declared limits                      |
| **21** | The null result, shown rather than asserted                       | | **48** | The ladder: three studies, three layers                           |
| **22** | A null with three suspects                                        | | **49** | The conditional answer                                            |
| **23** | *(transição)* A null with three suspects does not close…          | | **50** | The contribution, in one block                                    |
| **24** | Architecture or representation? *(texto)*                         | | **51** | Six limitations, six next steps (1 of 2)                          |
| **25** | Architecture or representation? *(figura)*                        | | **52** | Six limitations, six next steps (2 of 2)                          |
| **26** | HGI: how it works ∣ why it was used                               | | **53** | Closing                                                           |
| **27** | Why these encoders                                                | | **54** | Acknowledgements                                                  |

### 0.4 · Legenda de status

| Marca             | Significado                                                  |
|-------------------|--------------------------------------------------------------|
| ✅ **PRONTO**     | decisão clara, sem dependência; o `ppt` pode implementar     |
| 🔎 **INVESTIGAR** | depende de uma pesquisa da §3; o ID da pesquisa está no item |
| ⚖️ **DECIDIR**    | precisa de escolha estrutural; a decisão está na §2          |
| 🛑 **CONFLITO**   | colide com uma regra registrada do projeto; ver §4           |
| 👤 **AUTOR**      | só o Vitor fecha                                             |

---

## 1 · Regras transversais

Estas valem para o deck inteiro e resolvem dezenas de itens de uma vez. Aplicar uma regra aqui é mais barato do que
repetir a correção slide a slide.

### G1 · Títulos: diretos, descritivos, sérios ✅

Fim das analogias, trocadilhos e frases-conceito. O título diz o assunto do slide na primeira leitura. Atinge, no
mínimo: **S9, S17, S26, S30, S36, S38, S39, S47, S50**, e qualquer outro em que o `ppt` identificar metáfora. *(
Origem: "Slides em geral — títulos" + os pedidos individuais de S9/S30/S36/S39/S47/S50.)*

### G2 · Inglês simples, dito em voz alta ✅

A plateia é majoritariamente lusófona e a fala é em português. Nenhuma frase de tela pode exigir releitura. Alvos
nomeados pelo autor: **S33** (*"coarser than a place, not easier"*), **S36**
(*"the consecutive-visit edges run in one direction only"*), **S47** (itens 2 e 4), **S24** (item 4).

### G3 · Travessão: sai só o de texto corrido ✅ (AUT-4)

**Fica:** separador de rótulo (`\textbf{Semantic} --- the category…`), título de bloco, subtítulo. **Sai:** travessão
**dentro de frase completa** — vira vírgula, ponto e vírgula, dois-pontos ou duas frases. Alvos nomeados pelo autor:
**S16, S20, S24, S47, S49, S50** — verificar cada um contra este critério; provavelmente nem todos precisam de mudança.
Regra completa em §4/X4.

### G4 · Convenção única para toda tabela de PLACAR ✅

**Negrito = melhor · sublinhado = segundo melhor.** Hoje só a tabela *Next category* do **S21** obedece. Atinge: **S21**
(as duas tabelas), **S29** (as duas tabelas), **S44**, **S45**.

> 🛑 **Exceção obrigatória: o S46 fica FORA.** *(correção — eu o tinha incluído.)* O S46 não é tabela
> de placar: é a **tabela de veredito**, com Δ e intervalo de confiança. **As quatro células de região
> dentro da margem são déficits declarados**, e marcá-las com "melhor / segundo melhor" **reintroduz
> visualmente o veredito de vencedor que a lei proíbe** (*"all four are deficits, not ties"*).
> No S46 o destaque já existe e é o certo: o **▲** nas três células que o teste sustenta.

### G5 · Escopo por capítulo ✅

Dentro da seção de um estudo, só o que é daquele estudo. Nada de *"o Capítulo 5 faz X"* enquanto se apresenta o Capítulo
3. Comparações entre estudos ficam para a Conclusão (S48, a escada). Atinge: **S20** (remover a menção ao Cap. 5),
**S40** (remover a comparação de janelas com Cap. 3/4), **S16/S21/S24/S25/S29** (o *Metric stamp*, que compara com o
Cap. 5). *Nota:* isto **coincide** com a regra §8.7 do plano ("nenhum número do Cap. 3 e do Cap. 5 no mesmo eixo, tabela
ou frase"), então é reforço, não exceção.

### G6 · Terminologia — Capítulo ≠ Seção ✅

"**Capítulo N**" = da dissertação. "**Seção N**" = do deck. Este documento já obedece.

### G7 · Notas de rodapé ✅ (AUT-5)

**Os carimbos `Task stamp` e `Metric stamp` saem de todos os slides** (X2). Para as demais notas (S20, S37, S45), o
critério é: **fica só o que carrega informação que a fala não carrega**, e vale o protocolo §4c do `HANDOFF.md` — **toda
cláusula que sai da tela tem de ser localizada no destino** (a fala do mesmo slide ou um slide de reserva) **antes** de
sair. Sem isso vira perda de honestidade com aparência de design.

### G8 · Densidade ✅ — e este é o item com maior alavanca do documento

Medição registrada no `HANDOFF.md` §4b: **mediana de 119 palavras por slide** contra **~25–30** da defesa de referência
(mesmo template, mesma duração, 64 slides). **54 de 54 slides violam a regra §8.10 do plano** (*"marcadores por
palavra-chave, nunca parágrafos"*). **Quem enxuga não está sobrepondo o plano; está aplicando uma regra que ele já
continha.**
Corte pela **função** da frase, não pela contagem.

---

### G9 · Vocabulário travado — não reabrir numa reescrita 🛑

Decisões registradas do autor que qualquer reescrita de texto pode desfazer por acidente:

| termo                                           | decisão                                                                                                                                         |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| **`supera` / `outperforms`**                    | só nas **três células** de §5.1 (TX e CA em região, FL em categoria), e **contra o modelo dedicado**. Ver X5                                    |
| **`match` / `empata` / `ties`**                 | **banidos como veredito sobre o Cap. 5.** As quatro células dentro da margem são **déficits declarados**, não empates                           |
| **`technical tie`**                             | **fica verbatim** no S30. É redação literal do Cap. 4 entregue, sobre outro eixo e outro protocolo. **Não confundir com o `ties` banido acima** |
| **`category classification`**                   | é o termo da Def. 2.6. **Não** *"categorical classification"*. §8.11 é fail-closed                                                              |
| **macro-F1 de PRÓXIMA CATEGORIA entre 54 e 80** | é **número vazado pré-v18**. Se aparecer, pare. ⚠ a faixa é escopada: `Acc@10` de região em 59–77 é legítimo                                   |
| **`contrastive`**                               | fora do `GLOSSARY` hoje, e já em tela com outro sentido no S27. Ver F11                                                                         |

### G10 · Tamanho de corpo — a régua real é mais dura que a registrada ✅

Medição da sessão `ppt`: a geometria do `nesped.sty` é `16 cm × 9 cm`, então **1 pt aqui aparenta 2,117 pt** num slide
16:9 normal. Pela norma de dimensionamento (AVIXA/DISCAS), a régua não é `pt`, é **altura-de-x sobre altura-da-imagem**,
e a banca no Meet, num notebook, está a ~3,3–3,7 alturas.

> **`\scriptsize` (2,77) e `\small` (3,47) já falham para a banca no remoto.**
> `\normalsize` (3,80) e `\large` (4,16) passam.

O deck tem hoje **214 comandos de redução de corpo** (97 `\scriptsize`, 95 `\small`, 22
`\footnotesize`) contra **um** `\normalsize`. **Corpo pequeno é a causa da densidade atual, não o sintoma** — e é por
isso que "reduzir a fonte para caber" não é solução para nenhum item desta lista.

### G11 · Orçamento de caixa: o que entra exige o que sai 🛑 — a regra mais restritiva desta lista

**O deck inteiro está dimensionado para o corpo atual, e isso foi MEDIDO, não estimado.**
A sessão `presentation` subiu **um único degrau** de corpo em todo o deck (`\scriptsize→\footnotesize`,
`\small→\normalsize`, 217 substituições) e recompilou:

|                                    |   antes |      depois |
|------------------------------------|--------:|------------:|
| páginas com `Overfull \vbox`       |  **25** |      **50** |
| S46 (*The verdict*), fora da caixa | 17,9 pt | **48,5 pt** |
| S12 (*The evidence base*)          |       — | **38,5 pt** |
| S21 (*The null result*)            |       — | **28,5 pt** |
| S45 (*Result 2*)                   |       — | **19,3 pt** |

> **Consequência: a régua de tipo da G10 continua verdadeira como diagnóstico, mas NÃO é executável
> como política nesta rodada.** A ordem obrigatória é
> **cortar conteúdo → encolher o slide → subir o corpo → renderizar página a página.**
> Nunca as duas últimas sem as duas primeiras.

**Estado atual: 25 páginas estouram, nove no deck principal.** O pior é o **S46**, cuja última linha — *"…read off the
intervals, not established by a further test"*, que a lei do veredito **obriga** a estar ali — **desce a y = 1,004: os
descendentes passam da borda inferior da página.** O **S3** também estoura (4,0 pt), e a saída da tabela (AUT-3)
conserta isso de graça.

> 🔴 **A regra operacional, e ela vale para todo item marcado ➕ na §5:**
> **todo item que ACRESCENTA conteúdo a um slide existente tem de declarar o que SAI do mesmo slide.**
> Não é orçamento de tempo — o autor adiou isso (AUT-1). É orçamento de **caixa**, e ele não foi adiado.
> Uma especificação que só diz o que entra volta como pergunta.

**E há uma segunda pressão, na mesma direção.** O autor recusou `\documentclass[t]` e `12pt` (prefere o conteúdo
centrado) e **pediu mais respiro entre os elementos**, com a caixa mais para o rodapé. Cinco tratamentos estão em teste.
Isso significa que **os intervalos entre blocos vão crescer** — ou seja, **três blocos num slide podem ter de virar
dois**.

**O modelo de custo, medido no deck vigente** — use-o antes de propor qualquer acréscimo:

| o que                         | custo em altura                              |
|-------------------------------|----------------------------------------------|
| **um item a mais numa lista** | ~10 pt (a linha) + ~10 pt (o `itemsep` novo) |
| **um bloco novo**             | ~28 pt + o conteúdo                          |

E a capacidade de absorção medida página a página (o conteúdo é centrado, então cresce para os dois lados:
`2 × min(folga acima, folga abaixo)`):

| capacidade             |                    páginas |
|------------------------|---------------------------:|
| ≥ 35 pt                | 21 *(11 delas na Série B)* |
| ≥ 10 pt                |                         43 |
| **< 0 — já no limite** |                     **30** |

**Mediana: 7,1 pt.** ⚠ **Trinta slides não têm um ponto de folga**, e neles "o que sai" tem de ser **altura**, não
palavra: trocar uma frase longa por uma curta **não devolve linha** se ela continuar ocupando duas.

⚠ **E o log não vê nada disso.** Sete slides já perderam conteúdo com **`0 erros` e `0 overfull`**: o que é empurrado
para fora da caixa **não é desenhado e também não é extraído pelo `pdftotext`**, então checagem de texto aprova. **Só
renderizar revela.** Toda especificação que sair daqui tem de dizer também **o que conferir no render**, não só o que
escrever.

## 2 · Decisões estruturais

Cada uma muda a arquitetura do deck, não só um slide. Estão aqui porque precisam ser decididas **antes** dos itens da §5
que dependem delas.

### D1 · ✔ RESOLVIDA (AUT-9) — a nova Seção 2

**Decisão do autor, 2026-08-26.** E ela veio com uma correção dele que melhorou a proposta:

> *"De trabalho relacionado ao MTL a única coisa que temos é o item 4 do slide 7. O slide 8 é um misto
> entre quais modelos treinam category e region e as baselines para cada tarefa. Para ser sincero, o
> slide 7 é uma continuação do slide de fundamento de POI."*

**Ele está certo, e há uma redundância que a correção expõe:** o item 4 do S7 (*"in mobility, MTL has served next place
almost entirely: MCARNN, **CSLSL**, iMTL, HAMTL"*) e o bloco esquerdo do S8 (*"Category and region as a MEANS — toward
the next place: HMT-GRN, CatDM, **CSLSL**"*) **dizem a mesma coisa**, com o CSLSL nas duas listas.

#### A nova ordem

| impresso | slide                                                | conteúdo                                                                                                                                                                                                                                                                                                      |
|----------|------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **7**    | **Related work: POI prediction**                     | next place é a tarefa dominante · os modelos (ST-RNN, DeepMove, HST-LSTM, Flashback, STAN, GeoSAN, GETNext) · *"none is a direct baseline"* · **+ a sinonímia `next-POI / next-location / next-venue`** (`T4`, ver P1.1). **Perde o item 3** (*"the pair the first two studies attack"*, `T3`) **e o item 4** |
| **8**    | **As tarefas** — **S4 ⊕ S15 fundidos**               | next category (Def. 2.7) · next region (Def. 2.8) · category classification (Def. 2.6) · **next place, nomeado para ser excluído** (Def. 2.9) · a natureza diferente das duas do Cap. 3 e a hipótese do capítulo                                                                                              |
| **9**    | **O eixo que separa este trabalho** *(o S8 de hoje)* | categoria/região como **meio** × como **fim** · a frase de escopo · **o mapa de baselines por tarefa**, com o destaque do `F2`                                                                                                                                                                                |
| **10**   | **MTL Fundamentals** *(o S9 de hoje)*                | hard sharing (Def. 2.10) · negative transfer (Def. 2.12) · o critério **com o prefixo `For this dissertation` restaurado** · **+ o item 4 do S7** (*related work of MTL applied to POI*) · **+ balancing method**                                                                                             |

**Por que as tarefas entram no meio:** o eixo do slide 9 fala de categoria e região **como alvos finais**. Colocá-lo
antes das tarefas seria falar do alvo antes de nomeá-lo. E o mapa de baselines cai imediatamente depois das tarefas
serem definidas, que é onde ele é legível.

#### O que a decisão obriga

- ⚠ **O item 4 vai para o slide 10, por instrução expressa do autor** — não para o 9. **Então a redundância com o bloco
  *"as a MEANS"* do slide 9 continua viva e precisa ser resolvida na redação:**
  ou o bloco do 9 larga o CSLSL, ou o item 4 do 10 larga. **Não repetir o modelo nos dois.**
- **O slide 10 fica com cinco elementos** e o autor decidiu **manter um slide só, cortando o que não couber**.
  Prioridade sugerida, se faltar caixa: (1) hard sharing · (2) negative transfer · (3) o item 4 · (4) balancing method
  em meia linha · (5) o critério, que pode ir para a fala. ✅ **A `ppt` mediu que este slide tem folga** — foi um dos
  seis que receberam respiro extra.
- **Markov NÃO entra aqui.** Vai para o **S13**, junto do piso de classe majoritária, porque os dois são pontos de
  referência (`T5`).
- **Pareto NÃO entra aqui.** Fica no S19, onde está (fecha a **D2** pela via curta).
- A Introdução perde o S4 e fica com **1, 2, 3, 5** — quatro slides. **A exclusão do *next place*
  precisa de uma linha no S3**, para a sala saber o escopo antes do veredito.

### D2 · ✔ RESOLVIDA pela via curta — o S19 fica onde está

A D1 fechou sem levar Pareto para os Fundamentos, e o autor optou por manter o slide de MTL como um só. **Então o S19 (
*Two losses, one set of parameters*) permanece na seção do Cap. 3**, que é onde ele prepara o Nash-MTL — o único lugar
do deck que o usa.

O que muda no S19 é só redação: `M17` (nomear *negative transfer*) e `M18`. ⚠ **E o `M18` tem resposta: NÃO construir a
ligação Pareto ↔ negative transfer.** A dissertação não a afirma (ver P2.3), e o próprio slide já diz a frase certa — *"
This dissertation claims no Pareto property for its models"*.

### D3 · Os cinco candidatos a remoção ⚖️👤

| Slide   | O que é                                                | Pedido                          | Meu parecer                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|---------|--------------------------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **S6**  | *The contribution, in one block* (Introdução)          | remover; reconstruir só no S50  | ✔ **DECIDIDO (AUT-2): sai.** A §8.13 fica revogada. Ver X1 para o que a remoção arrasta                                                                                                                                                                                                                                                                                                                                                                                             |
| **S11** | *The idea these three share* (o estimador contrastivo) | avaliar remoção                 | 👤 **decisão do AUTOR, não minha.** ⚠ este slide foi separado do S10 em **25/08, por decisão dele** (`372d4026`) — fundi-lo de volta desfaz uma decisão de um dia atrás, que é a classe de erro que a §4E condena. **Meu parecer, para ele decidir: manter, fundido de volta no S10.** Foi separado do S10 há 1 dia por decisão do autor (`372d4026`); remover apaga o único lugar onde "infomax ≠ estimador contrastivo" é dito, e essa distinção foi corrigida ontem (`1627c5b9`) |
| **S14** | *Two traps* (bloco)                                    | remover o bloco, talvez o slide | **manter o slide; encolher o bloco a UMA linha** (só a mudança de par de tarefas) — ver X2/X3                                                                                                                                                                                                                                                                                                                                                                                        |
| **S18** | *Setup, and the protocol declared*                     | remover da principal            | **não remover inteiro.** Ver o parecer abaixo                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **S28** | *The caveat, then the number* (o vazamento)            | remover da principal            | 👤 **decisão que o autor levará ao orientador.** Ver o parecer abaixo                                                                                                                                                                                                                                                                                                                                                                                                                |

**S18 — o que se perde se sair.** O slide carrega quatro coisas, e só uma é "ETL":

1. o corpus do Cap. 3 (Florida, 990.518 check-ins) — **isto sim pode sair**;
2. a janela de **nove visitas não sobrepostas** e o corte de usuários com menos de cinco;
3. **o protocolo declarado**: 5-fold estratificado por amostra, uma semente, orçamento cheio de épocas, cada tarefa na
   melhor época dela, **sem teste de significância**;
4. a frase que autoriza tudo depois: *"So this chapter reports differences, never a verdict."*

Os itens 3 e 4 são a base da **lei dos verbos** e a razão pela qual o Cap. 3 não pode dizer "supera". Se o S18 sair,
eles têm de existir em outro lugar da tela — e o único candidato é o **S14**, que o autor quer *encolher*.
**Recomendação: manter o S18, cortar só o item 1 e comprimir o resto a duas linhas.** Alternativa: fundir S18 dentro do
S14 e matar o slide.

**S28 — o que se perde se sair.** É a ressalva de que a entrada da tarefa estática do Cap. 4 **contém o rótulo que ela
prediz** (`venue type` mapeia 1:1 nas sete categorias). Duas consequências:

- a regra §8.6 do plano (*"ressalva antes da manchete, sempre"*) nomeia **este slide** como o **caso paradigmático**;
  ele é o molde da regra, não uma aplicação dela;
- o número `+20.2 a +22.0 pp` da tarefa estática **só pode ser dito depois dela**. Sem a ressalva, o número não pode ser
  dito — e o S29 é sobre a tarefa **sequencial**, então o ganho estático some do deck inteiro.

> **Parecer:** se o S28 sair, o `+20.2 a +22.0` sai junto e o Cap. 4 passa a reportar **só** o
> resultado sequencial. Isso é defensável e até mais limpo — mas é uma perda de conteúdo, não só de
> tempo. E há um slide de reserva pronto (`B4-LEAK`) que responde se a banca perguntar.
> **Recomendo levar ao orientador exatamente nestes termos.**

### D4 · A nova ordem dos resultados do Cap. 5 ⚖️

Pedido do autor: **S37** (*The geometry of the vectors* — Silhouette + KNN purity) é resultado, não método, e deve ir
para junto do S44.

Nova ordem proposta: `Resultado 1 = S37 · Resultado 2 = S44 · Resultado 3 = S45`.

**Problema:** o S44 já se chama *"Result 1: the representation, at every dataset"* e o S45, *"Result 2: one model, two
tasks"*. Com o S37 na frente, há **três** resultados e a numeração dos títulos muda. E o S46 (*The verdict*) é, na
prática, o Resultado 4.

**Duas leituras possíveis do que o S37 e o S44 medem** (e elas não são a mesma coisa):

- **S37** mede a **geometria** da representação, sem tarefa, sem fold, sem semente — o próprio slide diz: *"These
  measures characterize the representation family, not the exact configuration evaluated later. They need no fold, no
  seed, and no pairing."*
- **S44** mede o **efeito na tarefa**: mesma configuração, só a entrada muda.

> **Minha recomendação:** aceitar a mudança, e renomear para tornar a diferença visível:
> `Result 1 — the representation, measured on its own geometry (S37)` ·
> `Result 2 — the representation, measured on the task (S44)` ·
> `Result 3 — one model, two tasks (S45)` · `The verdict, dataset by dataset (S46)`.
> Isso resolve também o pedido do autor de que o S37 não repita os números em texto: a tabela do S44
> passa a ser a vizinha imediata.

### D5 · ✔ RESOLVIDO (AUT-3) — o S3 não antecipa resultados

A tabela do veredito sai do S3. Não é mais preciso consultar advisor. **`P4.1` fica cancelada.**
O que a decisão obriga a verificar está em **N1**.

### D6 · O S45 pode dizer que supera a literatura? 🛑 → ver §4, X5

### D7 · A Série B: quanto reduzir? ⚖️👤 → ver §7

---

## 3 · O que precisa ser investigado

Agrupado por **fonte**, não por slide, para que uma consulta responda vários itens. O status de cada uma é atualizado
nesta seção; os itens da §5 apontam para cá.

### P1 · Literatura externa (busca na web)

| ID       | Pergunta                                                                                                                                                                                                                 | Resolve os itens |
|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|
| **P1.1** | *next-POI*, *next-place* e *next-location* nomeiam a mesma tarefa na literatura? Qual é a formulação dominante e como os surveys tratam a sinonímia?                                                                     | `T4`, `I9`, `F1` |
| **P1.2** | Qual é a disponibilidade temporal real dos datasets públicos de check-in? É correto dizer que raramente passam de ~2022? Quais são os mais recentes (Massive-STEPS, Foursquare NYC/TKY, Semantic Trails, YFCC, Gowalla)? | `K21`–`K24`      |
| **P1.3** | Comparar *dedicated* × *joint* com um plano de análise registrado, margem de equivalência e teste de não-inferioridade é prática comum em MTL? Ou é raro o bastante para ser reivindicado?                               | `K19`, `K20`     |
| **P1.4** | Grafia canônica: **POI-RGNN**, **HMT-GRN**, **CTLE**, **STAN**, **DRRGNN**, **MCMG**. *(Parcialmente resolvido: o `main.tex` já usa POI-RGNN e HMT-GRN; o autor escreveu "POI-RGN" no original.)*                        | `C49`            |

### P2 · A dissertação e a documentação (leitura do `src/` e `docs/`)

> **Status: em execução.** Doze leitores paralelos sobre `src/chapters/`, `src/tables/`, `science/`,
> `wrapup/`, `GLOSSARY.md`, `WRITING_LAW.md`, `AGENT_GUARDRAILS.md`. Resultados consolidados em
> `kb/00_MAPA.md`.

| ID        | Pergunta                                                                                                                                                                                                    | Resolve            |
|-----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| **P2.1**  | Onde a dissertação explica **cadeias de Markov**, com qual definição, e para que serve o *Markov-1 floor*                                                                                                   | `T5`, `C35`        |
| **P2.2**  | A frase *"A balancing method is useful only if it improves on a tuned fixed weighting"* existe no Cap. 2? Com qual redação? Ela é defensável como escrita? Em quais estudos um balanceador é de fato usado? | `F8`, `F9`, `M26`  |
| **P2.3**  | Relação formal entre **Pareto dominance**, **conflito de gradientes** e **negative transfer** — o que a dissertação afirma e o que ela não afirma                                                           | `M17`, `M18`, `D2` |
| **P2.4**  | O **tronco compartilhado** do Cap. 5: existem camadas pelas quais os dois fluxos passam? A frase *"not by owning hidden layers in common"* é correta?                                                       | `C26`              |
| **P2.5**  | **Cross-attention**: quem atende quem, o que é query/key/value, o que exatamente é trocado                                                                                                                  | `C25`              |
| **P2.6**  | **OOD-discounted Acc@10** — a métrica existe no texto entregue, com esse nome?                                                                                                                              | `C34`              |
| **P2.7**  | A **fórmula** do *joint-best*                                                                                                                                                                               | `C37`              |
| **P2.8**  | **Inferential unit** (`n = 4`) e **declared departure** (Wilcoxon → t pareado): o que são, em português simples                                                                                             | `C36`, `C38`       |
| **P2.9**  | *"Each visit draws only on the visits that precede it"* — que restrição causal é essa, e de onde vem                                                                                                        | `C62`              |
| **P2.10** | *"Epoch selection reads the fold it scores"* — qual é a limitação metodológica exata                                                                                                                        | `C61`              |
| **P2.11** | A **cross-entropy** é usada **com pesos de classe** em cada capítulo?                                                                                                                                       | `F19`              |
| **P2.12** | **Regiões por dataset**: qual tem mais? (o S33 cita Istanbul 520 e California 8.501; o TX tem 6.553 — confirmar se California é mesmo o máximo)                                                             | `C8`               |
| **P2.13** | **Anos** de cada dataset. O S51 diz "os cinco estados cobrem 2009 a 2011; Istanbul cai em dois períodos separados" — quais?                                                                                 | `K22`              |
| **P2.14** | Os corpora do **Cap. 3 e do Cap. 4** — check-ins, usuários, POIs, para a tabela extra                                                                                                                       | `M13`              |
| **P2.15** | *"same latent width on both sides… project N, input to 256"* — o que isso quer dizer no Cap. 4                                                                                                              | `A3`               |
| **P2.16** | O **fluxo do HGI**, passo a passo, para virar diagrama                                                                                                                                                      | `A7`, `A9`         |
| **P2.17** | Outros fundamentos de **MTL** que valham um slide (task interference, capacidade, tarefa auxiliar, MTL como regularização)                                                                                  | `F5`, `F6`         |
| **P2.18** | O **aprimoramento pós-entrega do protocolo estatístico**: existe? Onde está documentado? Qual é a redação honesta para a nota de rodapé?                                                                    | `C39`, `C40`       |
| **P2.19** | O **protocolo estatístico** é reivindicado como contribuição em algum lugar da dissertação?                                                                                                                 | `K19`, `K20`       |
| **P2.20** | *"Travel, labeled by task"* — o que essa conclusão do Cap. 4 significa                                                                                                                                      | `A23`              |
| **P2.21** | A **taxonomia** — sete categorias, e a limitação de granularidade como o texto a declara                                                                                                                    | `K25`, `K26`       |
| **P2.22** | A definição de **next place** e a de **next region** na dissertação, literais                                                                                                                               | `I9`               |
| **P2.23** | O tamanho da janela: a definição usa **N** ou **nove**?                                                                                                                                                     | `T6`               |

### P2 · RESPOSTAS — o que a leitura da dissertação devolveu

> Doze leitores paralelos sobre `src/`, `science/`, `wrapup/` e as três leis. Cada resposta abaixo
> traz `arquivo:linha`. **Onze das vinte e três perguntas estão fechadas.**

**P2.1 · Markov — a dissertação NÃO explica cadeia de Markov.** ✅ resposta
`grep -i markov 2_fundamentals.tex` dá **duas** ocorrências, **uma** em prosa. O Cap. 2 **não** define cadeia de Markov,
**não** define matriz de transição, **não** define ordem K, **não** dá fórmula. Ele só nomeia o piso
(`2_fundamentals.tex:1689`). A definição operacional está no **Cap. 5**
(`5_mobiwac/05_setup.tex`): *"a Markov model that predicts the category that most often follows the recent categories.
We select the best Markov order for each dataset. For region prediction, we compute a Markov-1 floor over region
transitions, under the same sliding windows and fold splits."*
> **Consequência para `T5`:** explicar Markov num slide de Fundamentos **acrescenta ao deck algo que a
> dissertação não tem em Fundamentos**. É legítimo numa apresentação, mas tem de ser dito como
> **definição operacional do Cap. 5**, não como fundamento do Cap. 2. E custa fala (⏱).
> ⚠ **Duas armadilhas no mesmo lugar:**
> 1. **a única citação de Markov do documento** (`gambs2012mmc`) é *"Next Place Prediction Using
     > Mobility Markov Chains"* — alvo **next place**, não categoria nem região. O próprio Cap. 2
>    reconhece isso num comentário oculto;
> 2. **o stride-1 do Cap. 5 é o que infla o piso de Markov na região**: *"the region of the last visit
     > is a strong predictor of the next one… At Alabama the target region is the last visited region in
     > 32.9 percent of windows"* (`06_results.tex:273-276`). Se o slide explicar Markov, essa é a
>    ressalva que o acompanha.

**P2.2 · O critério do balanceador — a frase existe, e é a única normativa de cinco.** ✅ resposta A frase normativa está
em `2_fundamentals.tex:1392`. As outras quatro superfícies do mesmo objeto são **descritivas e trazem "often" / "
rarely"**:

- `:1387` *"specialized optimizers **often** fail to improve on a tuned fixed-weight baseline"*;
- `:1852` *"The balancing methods proposed to prevent that outcome **often** do not improve…"*;
- `5_mobiwac/02_related.tex:122` *"… **rarely** improve on a well-tuned fixed weighting with two tasks"*.

E há um **achado empírico próprio, escopado** (`1_introduction.tex:449`): *"Nineteen loss and gradient balancers were
screened at their default configurations, at a single random initialization, on **Alabama and Florida**, and **none
improved** on a tuned fixed task weighting across both tasks and both datasets."*
> **Portanto o autor está certo em `F9`/`M26`:** a frase da tela é **normativa e absoluta**, enquanto
> tudo que a sustenta é **descritivo com hedge** ou **empírico escopado a dois datasets, uma semente e
> configurações default**. A formulação defensável é a do próprio digest:
> *"a balancing method earns its place only when, **at a matched tuning and seed budget**, it improves
> on a tuned fixed weighting **on at least one task without degrading the other beyond the registered
> margin**."*
> ⚠ **CORREÇÃO — a minha primeira recomendação errava o alvo.** Eu propus trocar a frase da tela por
> uma descritiva de literatura. **Isso substituiria texto entregue por paráfrase**, que é exatamente o
> princípio que este documento aplica em sentido contrário no `K8`.
>
> **Fui ler o original (`2_fundamentals.tex:1392`), e o defeito é outro e é trivial de consertar:**
>
> > *"**For this dissertation**, a balancing method is useful only if it improves on a tuned fixed
> > weighting."*
>
> **O slide cortou o prefixo de escopo.** Foi o corte que transformou um **critério escopado** numa
> **norma universal** — e é exatamente a queixa do autor (*"parece excessivamente restritiva"*).
>
> ✅ **A correção é RESTAURAR as três palavras: `For this dissertation, …`.** Resolve `F8`, `F9`,
> `M25` e `M26` de uma vez, sem tocar em nada mais, e devolve a frase ao que o documento diz.
> ⚠ E confirma a observação do autor: **balanceador é usado nos Caps. 3 e 4, não no 5** — o Cap. 5 usa
> peso fixo 0,5/0,5, *"No dynamic task balancing"*.

**P2.4 · O tronco compartilhado — a frase do slide está CORRETA, mas o slide se lê como contradição.** ✅ resposta O
texto do Cap. 5 é literalmente o do slide (`04_method.tex`): *"…into **the shared trunk, a cross-attention stack of two
blocks**… The tasks share by **exchanging information between per-task streams, not by owning hidden layers in
common**."*
No código: o bloco de cross-attention **é** o grupo `shared` do AdamW (`apx_h:396-400`), então "tronco compartilhado" é
verdadeiro **como módulo**. Mas **nenhum stream passa pelos pesos do outro** — cada um mantém seus próprios projetores.
**As duas frases são compatíveis.**
> **O problema é de tela, não de fato:** as duas afirmações ficam a três linhas uma da outra sem a
> reconciliação. **Solução: uma linha só** — *"one shared module, no shared hidden layers: the streams
> exchange, they do not merge."*
> ⚠ Registrar: o Apêndice H chama o mesmo módulo de *"interaction module, not classical hard parameter
> sharing"*, enquanto o Cap. 5 chama de *"the shared trunk, the only place where the two tasks
> interact"*. **Tensão terminológica declarada, não erro.**

**P2.5 · Cross-attention — é BIDIRECIONAL.** ✅ resposta
`04_method.tex`: *"Two **bidirectional** cross-attention blocks connect the encoded streams. In each block, **the
category stream queries the region stream and the region stream queries the category stream**."* Configuração
(`apx_h:444`): **dois blocos · quatro cabeças · largura 256 · dropout 0,15**. A torre privada de região usa **4
cabeças / dropout 0,3**; a torre de contexto compartilhado, **8 cabeças / dropout 0,1**.
> Isto é tudo que `C25` precisa. Cabe em duas linhas.

**P2.6 · OOD-discounted Acc@10 — a métrica EXISTE, mas o NOME só está no Cap. 2.** ✅ resposta Nome exato em
`2_fundamentals.tex:1666-1670`: *"Regions absent from the training partition count as errors. The reported
**out-of-distribution discounted, or OOD-discounted, Acc@10**…"*. Grep exaustivo por `OOD|out-of-distribution|discount`
em `chapters/5_mobiwac/*` → **zero ocorrências em prosa renderizada**: o Cap. 5 usa **a regra**, não o nome.
> **Veredito para `C34`: o slide pode manter o nome** — ele é do documento entregue, só que do Cap. 2.
> ⚠ **Mas a leitura descobriu um risco maior, e ele é de arguição:** o comentário oculto
> `06_results.tex:147-149` especifica o seletor implementado como
> `geom_simple = sqrt(cat F1 × reg Acc@10-**in-distribution**)`. Ou seja, **a seleção de checkpoint usa
> Acc@10 sem o desconto de OOD, enquanto a métrica reportada tem o desconto.** Nada no texto renderizado
> diz isso. Se a banca perguntar *"o seletor usa a mesma métrica que o senhor reporta?"*, a resposta
> honesta é: **quase — difere no desconto de OOD.** → **candidato a slide de reserva.**

**P2.7 · A fórmula do joint-best existe, e só no Cap. 2.** ✅ resposta
`2_fundamentals.tex:1679-1681`, Eq. `eq:fund:joint-selection`:
> $$S_{\mathrm{joint}} = \sqrt{\mathrm{MacroF1} \times \mathrm{Acc@10}}$$

O Cap. 5 descreve em palavras (*"the geometric mean of the two task metrics"*), o Apêndice H também.
> **`C37` é executável:** pôr a fórmula na tela, citando a Eq. do Cap. 2.
> ⚠ E há um número que o slide **não** diz e que sustenta o valor da escolha: a convenção alternativa
> (cada tarefa na melhor época dela) é mais favorável ao modelo conjunto **por até 0,23 macro-F1 e 0,93
> Acc@10**, e **transformaria mais quatro células de categoria e mais duas de região em melhorias**.
> *"A convenção mais estrita é a reportada, e todo veredito do capítulo é o que ela produz."* Essa é a
> frase forte do slide, e já está lá em parte.

**P2.8 · "Inferential unit" NÃO é termo do documento. "Declared departure" também não.** 🛑 resposta

- **`inferential unit`** — o termo literal **não aparece no Cap. 5**. É invenção do slide. O texto diz:
  *"The primary analysis aggregates the five folds within each seed and reports a paired $t$-test on the **four per-seed
  means** ($n=4$)"* (`05_setup.tex:115`). **§8.11 é fail-closed** → o termo tem de sair ou ser registrado no `GLOSSARY`.
  **Redação segura:** *"The test compares four numbers: one mean per seed."* Razão (dita na fala):
  folds dentro de uma semente não são independentes. Consequência dura, e ela está no texto: *"the exact one-sided
  Wilcoxon p-value **cannot be less than 0.0625**"* nesse apoio.
- **`declared departure`** — o desvio é **trocar o teste primário**: o plano registrou **Wilcoxon pareado sobre as 20
  diferenças por fold**; a análise primária virou **t pareado sobre as 4 médias por semente**. O Wilcoxon registrado
  continua reportado **como análise de sensibilidade**. ⚠ **A fala do slide diz que os dois "concordam" — e essa
  concordância NÃO está afirmada nessa frase do Cap. 5.** É afirmação do slide. Verificar antes de manter.

**P2.11 · Cross-entropy: SEM pesos, nos três capítulos — e há uma razão medida.** ✅ resposta
`2_fundamentals.tex`: *"The models use **unweighted cross-entropy** rather than a reweighted loss. **In Chapter 5, class
weighting lowered both category macro-F1 and region accuracy**"*. O Cap. 5 confirma: peso fixo 0,5/0,5, *"No dynamic
task balancing, class weighting, label smoothing…"*.
> **`F18`/`F19` liberados:** o item pode sair do S13. A resposta para a banca existe e é **melhor** que
> o item — não é só "não usamos", é "testamos e piorou".
> ⚠ Única exceção no código: há class weighting **dentro do pré-treino do embedding DGI**.

**P2.12 · California TEM mais regiões. O erro é outro, e o autor farejou certo.** ✅ resposta Regiões: Istanbul 520 · AL
1.109 · AZ 1.547 · FL 4.703 · TX 6.553 · **CA 8.501 (máximo)**. **A faixa "520 (Istanbul) a 8.501 (California)" está
correta para regiões.**
> ⚠ **Mas a frase de origem no Cap. 5 é ambígua:** *"about 3.2 million check-ins and 8,501 regions in
> California"*. Lida como faixa, sugere que **California é o máximo nos dois eixos** — e **é falso em
> check-ins: Texas tem 4.089.892 contra 3.171.380 da California.**
> **Para `C8`: manter California como extremo de regiões, e não deixar a frase sugerir tamanho.**

**P2.13 · Anos — e há uma contradição declarada entre capítulos.** ✅ resposta Os cinco estados do Gowalla: **jan/2009 a
ago/2011** (`6_conclusion.tex`), por dataset:
AL 2009-03-18→2011-07-27 · AZ 2009-03-26→2011-07-04 · FL 2009-03-13→2011-08-11 · TX 2009-01-21→2011-08-16 · CA
2009-01-24→2011-08-14.
> ⚠ **Contradição declarada:** `4_courb/conclusion.tex:12` (prosa **publicada**, Cap. 4) diz Gowalla
> *"collected between February 2009 and October 2010"*. A discrepância está explicada em comentário no
> `6_conclusion.tex:210-222`: fev/2009–out/2010 é o que o **paper** `cho2011` afirma; jan/2009–ago/2011
> é o que **a extração usada aqui** cobre. **Para `K22`: usar os anos do Cap. 6 e não citar o Cap. 4.**
> **Istanbul/Massive-STEPS: os anos não saíram desta leitura — segue aberto.**

**P2.19 · O protocolo estatístico NÃO é reivindicado como contribuição. Em lugar nenhum.** ✅ resposta
> **`K19`/`K20` estão fechados: NÃO pôr como contribuição científica no S50.** O próprio autor já
> suspeitava. Uma reivindicação de novidade que não está no volume entregue é exatamente o tipo de
> afirmação que a banca externa pode cobrar.

**P2.23 · A janela: o Cap. 2 NÃO fixa nove.** ✅ resposta O Cap. 2 usa um comprimento genérico. Quem fixa nove é o setup
de cada capítulo, **e eles diferem**:
Cap. 3/4 = janelas de nove **não sobrepostas**, com padding zero; Cap. 5 = nove **com stride 1**, usuários com ≥10
visitas, **sem janela curta**.
> **`T6` está correto e apoiado pelo documento: o slide de definição deve dizer *N visits*.** O nove é
> configuração de experimento, não definição.

**P1.1 · next-POI × next-place — parcialmente respondido internamente.** ◐ O termo canônico da dissertação é
**next-place prediction** (Def. 2.9), e a exclusão é explícita:
*"no chapter reports a result for $f_{\mathrm{place}}$"*. O fecho da §2.1.2: *"Every model named here predicts the exact
next place, so none of them is a direct baseline for the targets studied here."*
E os Caps. 3 e 4 **já carregam a nota de terminologia** de que *"Next-POI Prediction"* ali significa **next category**.
> ⚠ **Nenhum título da bibliografia diz "next place"** — dizem *"Predicting the Next Location"*,
> *"Predicting Human Mobility"*, etc. A sinonímia que o autor quer afirmar (`T4`) é real na prática,
> mas **a dissertação não a declara**. Falta a confirmação externa: **P1.1 segue aberta para busca.**

**P2.3 · A relação Pareto ↔ negative transfer NÃO é afirmada pela dissertação.** ✅ resposta Medido: a definição de
*negative transfer* (`2_fundamentals.tex:960-963`) e o bloco de Pareto (`:1082-1086`, `:1199-1213`) estão em **subseções
diferentes** e **nenhuma frase liga as duas**. Não existe nada como *"negative transfer = ser dominado por Pareto pelo
par de modelos dedicados"*. A única ponte é implícita, no `apx_f_cosine.tex:101-102`: *"A joint model can end up worse
at both than two dedicated models are at one each"* — que **é** dominância de Pareto na prática, mas a palavra não
aparece. E o capítulo fecha o assunto: *"**This dissertation therefore claims no Pareto property for its models.** It
judges each task against its dedicated single-task model under the tests defined in Section 2.4."*
> **Veredito para `M18`: não construir a ligação no slide.** O S19 já diz exatamente a frase certa
> (*"This dissertation claims no Pareto property for its models"*). **Afirmar a relação seria ir além
> do documento.** O que o slide pode fazer é o que o `M17` pede: dizer que o fenômeno tem nome —
> *negative transfer* — e parar aí.

**P2.9 · "Each visit draws only on the visits that precede it" = o grafo é forward-only.** ✅ resposta Limitação 4 do
Cap. 5 (`07_discussion.tex:194-198`), literal: *"each visit node in the representation graph draws on the visits that
precede it… **the graph does not pass information from a later visit back to an earlier one, in training or at readout,
which is what keeps a node from carrying a feature of the target it is used to predict**."*
Fonte mecânica (Apêndice E do volume principal, `apx_h:70-79`): *"Consecutive visits by the same user are connected **in
one direction only**… The direction is **part of the design**: a target is predicted from a user's past, so a
representation built for that target is constructed from the past alone."*
> **Em uma frase: o grafo de check-ins é acíclico no tempo, e essa é a defesa estrutural contra
> vazamento do rótulo.** Não é uma limitação fraca — é a correção que define a geração **v18** dos
> números (em Alabama o vazamento valia **28,63 macro-F1**, e é por isso que o eixo de categoria
> inteiro vive na faixa 30–38).
> **Portanto `C62` não deve remover o item: deve reescrevê-lo como o que ele é** — uma escolha de
> projeto que impede o vazamento, e não uma restrição incômoda. É a mesma ideia do `C18` (S36).

**P2.10 · A limitação de seleção de época — e a munição que vem junto.** ✅ resposta Literal
(`07_discussion.tex:131-158`): *"**epoch selection consults the fold that the score is then read on**, so **every
absolute score reported here is optimistic**."* Causa raiz (`05_setup.tex:30`): *"The held-out fold provides the
validation data, and **we do not reserve a third split**."*
**Mas a comparação é afetada muito menos**, e o capítulo diz por quê **sem supor**: a regra de seleção é a mesma para os
dois modelos nos mesmos folds, e na categoria **o modelo dedicado recebe a busca mais ampla** — o que torna a diferença
reportada **conservadora**. Fecha com honestidade:
*"It does not follow that the bias cancels exactly."*
> **Redação para `C61`:** *"The epoch is chosen on the same fold the score is read on: there is no
> third split. Absolute scores are optimistic; the joint-against-dedicated comparison much less so,
> because both sides use the same rule."*
> 💪 **E aqui está munição de primeira ordem para a arguição** (`06_results.tex:138-145`): a convenção
> alternativa (cada tarefa na melhor época dela) **é mais favorável ao modelo conjunto** e
> transformaria **mais quatro células de categoria e mais duas de região** em melhorias
> Holm-significantes. **O autor escolheu a convenção que produz MENOS vitórias.** Sob a outra, seriam
> 5 de 6 em categoria e 4 de 6 em região. Isso vale um slide de reserva, se ainda não houver.

**P2.15 · "Same latent width… project to 256" — o que a frase quer dizer.** ✅ resposta São **dois fatos**, que o
capítulo declara em lugares diferentes:

1. `methodology.tex:25` — *"task-specific encoders… **project the input embeddings into a shared latent space of
   dimension d_shared = 256**"*. Depois desse ponto, **tudo é idêntico** nos dois modelos: FiLM, os quatro blocos
   residuais compartilhados, as duas cabeças;
2. `methodology.tex:257` — *"The input dimensionality of ST-MTLNet (R^192) is higher than that of the baseline (R^64)…
   **Even so, the difference in input dimensionality may influence part of the observed gains.**"* O capítulo **pede um
   controle de dimensão equalizada que nunca foi executado**.

> **Redação simples para `A3`:** *"Both models share the same 256-dimensional latent width: each
> task encoder projects whatever it receives to 256, so the trunk and the heads are identical. What
> differs is the input: **192 dimensions against 64**."*
> Números para a fala: entrada estática **64 → 192** (3×), sequencial **576 → 1728**, latente **256**
> nos dois. ⚠ **A resposta honesta se pressionado:** capacidade pareada **depois** da projeção, não
> pareada **na** projeção — os encoders de tarefa têm 192×256 contra 64×256 na primeira camada.

**P2.16 · O fluxo do HGI, em quatro passos — pronto para virar diagrama.** ✅ resposta
`2_fundamentals.tex:441-453`, literal: **(1)** um **codificador de categoria pré-treinado** fornece as features iniciais
dos POIs → **(2)** uma **camada de convolução de grafo sobre um grafo de Delaunay**
dos POIs da área acrescenta contexto espacial a cada um → **(3)** **atenção multi-cabeça agrega os embeddings de POI de
uma região** → **(4)** uma **soma ponderada pela área** sobre as regiões produz **um embedding de cidade**. O sinal de
treino atualiza os três juntos, de modo que *"a POI embedding is optimized to score high against the embedding of **its
own region** and low against the embeddings of **other regions**"*.
> **Isto já é o desenho do §6.2** — a espinha existe sem precisar esperar a descrição do autor. O que
> falta dele é o grau de detalhe que ele quer, não o conteúdo.

**P2.20 · "Travel, labeled by task" — o que significa.** ✅ resposta É o **mesmo rótulo de categoria com resultados
opostos nas duas tarefas** do Cap. 4:

- **classificação de categoria** (Tab. 6): Travel **move muito** — FL 45,49 → **64,89** (SIREN), CA 38,88 → **63,59**,
  TX 39,37 → **64,73**;
- **próxima categoria** (Tab. 7): Travel **não move** — a MTLnet mantém a liderança, **64,47** contra 45,00 em Florida,
  e o mesmo em California.

> **A mensagem é: a decomposição ajuda a dizer o que um lugar É, e não ajuda a dizer para onde a
> pessoa VAI, nesta categoria.** Escrito assim, o bloco vale a pena e o `A23` vira reescrita, não
> remoção. Escrito como *"Travel, labeled by task"*, não comunica nada.

**P2.13b · Os anos de Istanbul — e eles são um bom argumento, não uma fraqueza.** ✅ resposta
`6_conclusion.tex`, literal: *"**The Istanbul dataset is not appreciably more recent for most of its volume: its
check-ins fall in two separate periods, 2012 to 2013 and 2017 to 2018, with none in between, and roughly seven in ten
belong to the earlier period.**"*
> **Para `K22`:** o dado sustenta exatamente o que o autor quer dizer — **houve tentativa de usar um
> conjunto mais recente, e mesmo ele é majoritariamente de 2012-13**. Isso transforma a limitação de
> "os dados são velhos" em "os dados públicos são velhos", que é a versão que o `K23` pede.

---

### ⚠ Um achado que não estava em nenhuma pergunta, e que muda a leitura do S47

**A quinta limitação do Cap. 5 — a de CAPACIDADE — foi RETIRADA por decisão do autor em 2026-08-12.**
O texto retirado dizia: *"the joint model is the larger artifact… so **capacity is one variable the region comparison
does not hold fixed**."* Motivo registrado: o apêndice de contagem de parâmetros migrou para o volume suplementar, e o
autor preferiu retirar o limite a deixá-lo apontando para nada.

> 🛑 **Isto interage diretamente com o risco R-α.** O estudo pós-entrega **P1** mediu que, com
> capacidade pareada, a vantagem de região **desaparece** — e o limite que cobriria exatamente isso
> **não está mais declarado no texto**. Existe uma errata escrita e **não aplicada**
> (`erratas/errata_Q14_capacity_region.tex`), que devolveria os limites do Cap. 5 de quatro para cinco.
> **Consequência de defesa: capacidade não é limite declarado; se a banca perguntar, é pergunta
> oral.** O S47 diz *"four declared limits"* e está **correto** em relação ao texto entregue.
> ⚠ E o controle vive no **Apêndice G do suplemento, cujos números de parâmetro estão errados**
> (100,2% / 101,9% impressos; os reais são 230% / 234%). **Nunca dizer "100,2%" em voz alta.**

**Perguntas ainda abertas:** `P2.14` (corpora dos Caps. 3/4), `P2.17` (outros fundamentos de MTL),
`P2.18` (o refinamento do protocolo estatístico), `P2.21` (taxonomia), `P2.22` (parcial), e as três buscas externas
`P1.1`, `P1.2`, `P1.3`.

### P1 · RESPOSTAS — as buscas externas

**P1.2 · Datasets — a afirmação do autor é VERDADEIRA e ele estava sendo conservador demais.** ✅ O corte real não é
2022; **é 2018**, e a evidência é forte:

| dataset                      | período                                                               | fonte                                                         |
|------------------------------|-----------------------------------------------------------------------|---------------------------------------------------------------|
| Gowalla (SNAP)               | **fev/2009 – out/2010**                                               | snap.stanford.edu/data/loc-gowalla.html                       |
| Brightkite                   | abr/2008 – out/2010                                                   | SNAP                                                          |
| Foursquare NYC/TKY           | abr/2012 – fev/2013                                                   | Dingqi Yang                                                   |
| Foursquare Global (TIST2015) | abr/2012 – set/2013                                                   | idem                                                          |
| Semantic Trails 2013         | abr/2012 – set/2013                                                   | arXiv:1812.04367                                              |
| **Semantic Trails 2018**     | **out/2017 – out/2018**                                               | idem — **a fronteira de recência**                            |
| **Massive-STEPS** (2025)     | **2012–2013 + 2017–2018**                                             | arXiv:2505.11239 — é **re-curadoria** do STD, não coleta nova |
| Yelp Open Dataset            | última versão **2022**; check-in só como contagem agregada            | business.yelp.com                                             |
| Foursquare OS Places (2024)  | POIs atualizados mensalmente — **sem check-ins**                      | opensource.foursquare.com                                     |
| YJMob100K (2023)             | 75 dias, **datas e cidade ocultadas por privacidade**, grade de 500 m | Nature Sci. Data 2024                                         |

> **Não existe dataset público de check-ins com trajetória de usuário posterior a 2018 em uso
> corrente.** O que existe depois é de outra natureza: POIs sem visitas, mobilidade sem semântica, ou
> reviews.
>
> **E o argumento mais forte para o slide é este:** o próprio Massive-STEPS, publicado em **2025** com
> o objetivo declarado de resolver a defasagem temporal, **ainda para em 2018**. O abstract dele diz
> *"the over-reliance on older datasets from 2012-2013"* e *"behavioral patterns captured over a
> decade ago may no longer align with modern user preferences"*.
>
> **Causas documentadas:** Gowalla encerrada em 2012 (comprada pelo Facebook) e Brightkite extinta ·
> mudança de política de API do Foursquare · **fim do acesso acadêmico ao Twitter/X em fev/2023**, que
> era o canal do STD 2018 · GDPR · SafeGraph fechou o catálogo aberto em jan/2022.

**Redação para `K21`–`K24`** (do relatório, e cabe em duas linhas):
> *"**Data vintage** — the five Gowalla states span 2009–2010 and Istanbul comes in two separate
> blocks (2012–2013 and 2017–2018). This is a constraint of the field, not of this work: after Gowalla
> and Brightkite shut down and Foursquare and Twitter closed their research APIs, **no public
> check-in dataset with user trajectories extends past 2018** — even Massive-STEPS (2025), released
> precisely to fix data recency, still stops there."*

⚠ **Uma discrepância que o relatório levantou e que já tem resposta interna:** o SNAP Gowalla vai de **fev/2009 a
out/2010**, e a dissertação diz **jan/2009 a ago/2011**. **Não é erro** — o
`6_conclusion.tex:210-222` registra em comentário que fev/2009–out/2010 é o que o *paper* `cho2011`
afirma e jan/2009–ago/2011 é o que **a extração usada aqui** cobre. O Cap. 4 (prosa publicada) usa a primeira; o Cap. 6,
a segunda. **Usar a do Cap. 6 e não citar a do Cap. 4** (item `K22`).

**P1.3 · O protocolo estatístico NÃO é contribuição — e a redação honesta é melhor do que reivindicá-lo.** ✅
> **Veredito da busca: não se sustenta como contribuição metodológica. É higiene metodológica bem
> executada, com rigor acima da mediana da literatura de MTL.**

- **O padrão dominante em MTL é um escalar sem teste**: o `Δm` de Maninis et al. (2019), consolidado pelo survey de
  Vandenhende et al. (arXiv:2004.13379) — média das variações relativas por tarefa contra o single-task, **sem intervalo
  e sem teste**, tipicamente de uma execução ou poucas seeds;
- **quando há teste, é de superioridade**, nunca de equivalência. A busca **não encontrou nenhum**
  trabalho de MTL usando não-inferioridade, TOST ou margem registrada;
- **mas os precedentes cercam a ideia e são fortes** — em especial **ROPE** (Benavoli, Corani, Demšar, Zaffalon, *JMLR*
  18, 2017), que é ML-nativo e faria uma reivindicação de novidade ruir.

> **O que É defensável dizer, e é um diferencial real:** *"we adopted a pre-specified analysis plan
> with a registered margin and a non-inferiority test — standard practice in clinical trials and
> recommended in ML (ROPE, Benavoli et al., JMLR 2017), but rarely applied in the multitask
> literature."*
> E o argumento que **justifica** o TOST, também de Benavoli et al.: *"two methods that are not
> statistically significantly different are not necessarily equivalent"* e *"When NHST does not
> reject the null hypothesis, no conclusion can be made."* **A prática padrão de MTL — "p > 0,05,
> logo empatou" — é formalmente inválida.** É por isso que o protocolo desta dissertação existe.
>
> **Fecha `K19` e `K20`: não entra como contribuição no S50. Entra na fala, como rigor.**

**P1.1 · Terminologia — sim, é a mesma tarefa. E o slide escolheu o nome MENOS usado dos quatro.** ✅ Busca em fontes
primárias (arXiv 2023–2026, títulos da bibliografia):

- **os quatro nomes designam a mesma tarefa** — mesmo alvo, mesmos benchmarks, mesmas métricas:
  `next-POI` · `next-location` · `next-place` · `next-venue`;
- **o dominante é `next-POI`**, e com folga: *"next POI recommendation"* aparece **36 vezes** em 2023–2026 no arXiv
  contra **zero** de *"next place"*;
- os próprios títulos da bibliografia confirmam a sinonímia: `liu2016strnn` = *"Predicting the Next **Location**"* ·
  `feng2018deepmove` = *"Predicting Human **Mobility**"* — **nenhum diz "next place"**.

> ⚠ **A frase atual do S7 — *"Next place is the dominant task in the field"* — é o ponto mais
> atacável do slide**, e por um motivo empírico: o nome não é o dominante.
>
> 🛑 **Mas trocar o nome principal para `next-POI` colide com a disciplina de nomes do próprio deck.**
> A dissertação **reserva** `next place` para a tarefa de POI exato (Def. 2.9, no `GLOSSARY`, §8.11
> fail-closed) **justamente para que "Next-POI Prediction" nos Caps. 3 e 4 possa significar next
> category** — que é o `Task stamp` da regra §8.5. Se o S7 disser *"next-POI prediction is the
> dominant task"*, o deck passa a usar `next-POI` com **dois sentidos opostos**.
>
> ✅ **A saída que atende o `T4` sem quebrar nada: manter `next place` como o termo do trabalho e
> DIZER a sinonímia.** Redação sugerida:
>
> > *"**Next place** — the literature also calls it **next-POI**, **next-location** or **next-venue**,
> > and they are the same task. It is the dominant target in the field, and every model named below
> > predicts the exact establishment, so **none is a direct baseline** for the targets studied here."*
>
> Isso responde exatamente ao que o autor pediu (*"next-poi e next-place na literatura é usado para a
> mesma tarefa"*), **remove a afirmação atacável**, e **preserva a armadilha de nome** que o S5 e os
> carimbos dos Caps. 3/4 dependem.

### P3 · RESPOSTAS — o template

**P3.1 · Por que o destaque da research question não funciona: a caixa é branca no branco.** ✅ O S3 usa
`\begin{block}{}` com **título vazio**. Nessa configuração o `block` fica com `bg=white`
sobre um slide branco, com apenas um traço `offwhite` de contorno — **a caixa não existe visualmente**. Não é tamanho de
fonte: aumentar para `\Large` dentro dela continua sem moldura.

**A recomendação, e ela vem de duas fontes que convergem** — a auditoria do `.sty` e o sandbox compilado pela sessão
`ppt` (quatro molduras, todas com 0 erros e 0 overfull):

> **`\specialframe` (degradê de tela cheia) + a pergunta dentro de um CARTÃO BRANCO.**
>
> O `.sty` tem um `\AtBeginEnvironment{block}` que força `normal text fg=black`, então um `block`
> dentro de um `\specialframe` vira **um cartão branco flutuando sobre o gradiente, com texto preto**
> — o elemento de maior contraste do deck inteiro. A linha da restrição fica em branco abaixo.
>
> ⚠ **Por que o cartão e não a pergunta direto sobre o gradiente:** medido pela `ppt`, branco sobre
> `primary` (a ponta CLARA do degradê) dá **2,67:1 — reprovado**. Sobre `secondary` (a ponta escura)
> dá 9,83:1. A pergunta é o elemento que menos pode ficar fraco. **O cartão resolve.**
> Se algum texto ficar em branco sobre o degradê, mantenha em `\normalsize` ou maior e **empurre para
> a metade direita/baixa**, que é onde escurece.
>
> ⚠ **Dentro de `\specialframe`, NÃO abrir o corpo do frame com uma chave** — `{\Large …}` vira
> subtítulo e o conteúdo vai parar dentro da faixa do título, **com log limpo**. Abrir com `\vfill`,
> `\par` ou o próprio `\begin{block}`.
>
> O deck já usa `\specialframe` quatro vezes (S23, S31, S53, S54) e são os slides que melhor
> funcionam. O S3 é o terceiro numerado, precedido de dois slides brancos — **não há risco de dois
> degradês seguidos**.

**P3.3 · A tabela do S45: o problema é o número de LINHAS, não a fonte.** ✅ São 12 linhas de dados + 2 cabeçalhos de
grupo + 1 cabeçalho = **15 linhas empilhadas num canvas de 9 cm**. Foi isso que forçou o `\arraystretch{0.58}`. Medido:
a versão empilhada a `\footnotesize` com
`\arraystretch{1.05}` dá **overfull de 21,8 pt**. **Não cabe empilhada, ponto.**

> **Recomendação: duas tabelas lado a lado dentro de `columns`, uma por tarefa, 6 linhas cada.**
> Converte pressão vertical (que não há) em horizontal (que sobra, num 16:9). Medido:
> `\footnotesize` + `\arraystretch{1.3}` + `\tabcolsep 5pt` → **0 overfull**, com ~35% da altura
> livre. Isso é **um passo inteiro de fonte acima do atual** e **2,2× o espaçamento entre linhas**.
>
> Outras alavancas verificadas: `\multicolumn` com `\color{primaryshade}` como cabeçalho de grupo
> funciona e amarra a tabela ao tema · `\rowcolor{primarytint}` **NÃO funciona out-of-the-box** (o
> `.sty` carrega `xcolor` **sem** a opção `table`; precisa de `\usepackage{colortbl}` depois do
> `nesped`) · negrito + sublinhado leem bem na fonte do template · ⚠ **empates existem** (AZ 34,57 e
> CA 35,63 aparecem nos dois lados) — hoje os dois vão em negrito; manter, **e dizer na nota**.

**P3.2 · Divisor "Extras"** — o `\specialframe` é exatamente isso e já é usado no S54 (Acknowledgements). Um
`\specialframe` com a palavra **Extras** centralizada resolve o item `E2`.

**P3.4 · Armadilhas do `.sty`** — consolidadas na §4F.

### P4 · Consultas a advisor (Fable)

| ID       | Pergunta                                                                               | Resolve    |
|----------|----------------------------------------------------------------------------------------|------------|
| **P4.1** | O S3 deve antecipar o veredito, ou a Introdução deve ficar só com problema + pergunta? | `I7`, `D5` |
| **P4.2** | Revisão adversarial deste documento e do plano de mudanças, antes de virar `SLIDES.md` | —          |

---

## 4 · Conflitos com as leis registradas do projeto

Cinco pedidos do autor colidem com regra escrita. Nenhum é impossível — **quem aprova é o autor**
(decisão de 2026-08-22, registrada) — mas nenhum deve ser executado sem que o custo esteja na mesa.

### X1 · ✔ RESOLVIDO (AUT-2) — o S6 sai e a §8.13 fica revogada

> **§8.13 (revogada):** *"A contribuição aparece **duas vezes**, com redação idêntica: um slide cedo e
> o slide de fechamento — sempre com a ressalva de que o ganho é operacional, não computacional."*

**Decisão do autor:** a contribuição aparece **uma vez só**, no **S50**.

⚠ **Duas coisas que a remoção arrasta e não podem ser esquecidas:**

1. o `[BLOCO-CONTRIBUIÇÃO]` do cabeçalho do `SLIDES.md` existe **em três cópias sincronizadas**
   (definição + S7 + S51 na numeração do `SLIDES.md`), **com teste de sincronia**. Apagar o slide sem desfazer a
   definição deixa o teste falhando e o documento mentindo sobre si mesmo;
2. a ressalva **"operational, not computational"** era obrigatória pela §8.13 nas duas cópias. Com uma cópia só, **ela
   tem de continuar no S50** — é a única coisa da regra que vale a pena preservar, e o autor já pede o mesmo em `K13`.

### X2 · ✔ RESOLVIDO (AUT-5) — os dois carimbos saem, e a §8.5 fica revogada

> **§8.5 (revogada):** *"Toda figura/tabela dos Caps. 3/4 mantém a citação de origem e recebe a
> anotação `Next-POI Prediction = next category (Def. 2.7)`."* O `HANDOFF.md` §4c a classificava como
> **mandato de tela**.

**Decisão do autor, nas palavras dele:** *"Remova o Task stamp e o Metric stamp. Durante a prosa isso não vai ser
discutido, polui o slide, e é algo fácil de ser explicado caso alguém pergunte."*

**Sete slides perdem o rodapé** — e o levantamento importa, porque as duas etiquetas **não aparecem sempre juntas**:

| slide                                     | `Task stamp` | `Metric stamp` | linha   |
|-------------------------------------------|:------------:|:--------------:|---------|
| **S15** *One static task…*                |      ✔      |       —        | `:609`  |
| **S16** *MTLnet*                          |      ✔      |       ✔       | `:637`  |
| **S21** *The null result*                 |      ✔      |       ✔       | `:841`  |
| **S24** *Architecture or representation?* |      ✔      |       —        | `:924`  |
| **S25** *…(a arte)*                       |      ✔      |       ✔       | `:939`  |
| **S28** *The caveat, then the number*     |      —       |       ✔       | `:1069` |
| **S29** *The diagnostic result…*          |      ✔      |       ✔       | `:1122` |

> ✅ **É a maior devolução de caixa da lista inteira:** sete slides ganham altura de uma vez, e três
> deles (**S21**, **S29**, **S16**) estão entre os mais densos do deck.
> ⚠ **Duas notas:** o **S28 sai inteiro** por `AUT-7`, então na prática são **seis**. E a **armadilha
> de nome continua viva no S5** (*"Naming trap: in Chapters 3 and 4, 'Next-POI Prediction' means the
> next category"*) — **é ela que passa a carregar sozinha o que os carimbos diziam.** Não removê-la.

### X3 · Com a AUT-5, a convenção métrica só pode viver no S14 — e o autor quer tirá-la de lá 🛑

`T2` e `F23` pedem que o S14 **não** fale da mudança de convenção métrica: *"não precisamos falar sobre o fato da gente
mudar as métricas no capítulo cinco, só comente a questão das mudanças das tarefas em si."*

**Antes da AUT-5 isso era um problema pequeno**, porque o `Metric stamp` repetia a informação em seis slides. **Agora a
AUT-5 removeu os seis.** Se o S14 também perder a linha, **a mudança de convenção métrica desaparece do deck inteiro** —
e ela é real e material:

> os Caps. 3 e 4 imprimem **uma F1 por categoria**; o Cap. 5 reporta **macro-F1**, um número só.
> **Não são a mesma escala**, e as tabelas do S21 (7 linhas por categoria) e do S45 (um número)
> estão lado a lado na mesma apresentação.

**Leitura do pedido, e ela reconcilia os dois:** o autor está falando de **tempo de fala**, não de tela — a frase dele é
*"não precisamos **falar** sobre"*.

> ✅ **Proposta: o S14 mantém UMA LINHA de convenção métrica, não falada.** Existe para quem lê a tela
> e para a banca; a fala cobre só a mudança de par de tarefas. **Custo: uma linha, num slide que
> acabou de ganhar espaço.** É a pergunta **Q3**, e continua aberta.

### X4 · ✔ RESOLVIDO (AUT-4) — travessão de glosa fica, travessão de prosa sai

A `WRITING_LAW.md:131` diz *"No em-dash anywhere"* e o checklist em `:410` exige contagem zero. **O autor revogou isso
para os slides em 24/08.** Está no `HANDOFF.md` §4f, que abre com o aviso:

> *"⚠ NÃO 'conserte' isto numa varredura de estilo. Um agente que rode essa regra sobre o deck vai
> querer eliminar todos. O autor decidiu que não."*

A regra vigente é **por função, não por presença**:

| onde                                                                                          | decisão                                                        |
|-----------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| separador de rótulo num fragmento — `\textbf{Semantic} --- the category of the visited place` | **fica**                                                       |
| título de bloco — `\begin{block}{Practical --- what it delivers}`                             | **fica**                                                       |
| subtítulo de frame                                                                            | **fica**                                                       |
| **dentro de frase completa** — `…in place of two --- operational, not computational`          | **sai**: vírgula, ponto e vírgula, dois-pontos, ou duas frases |

Aplicada em 24/08: dos 105 travessões do deck, **11 faziam trabalho de prosa e mudaram; 93 ficaram**. Hoje há **168
`---` em tela** no arquivo inteiro (a Série B não foi varrida, por decisão de escopo).

**O autor confirmou a regra em 2026-08-26, nas palavras dele:**

> *"Não existem duas situações. Usar o travessão para glosa e usar o travessão no meio de um texto —
> o que eu peço para remover, e temos que remover, é o travessão no texto corrido."*

> **Portanto, para todo item deste documento que diz "corrigir o travessão" (`G3`, `M1`, `M21`, `A2`,
> `C59`, `K7`, `K14`): não é varredura.** É verificar, naquele slide, se há travessão **dentro de
> frase completa** — e só esse muda. Se o slide só tem separador de rótulo, **não há nada a fazer**.
> Isso vale inclusive para o `K7`/`K14` (S49 e S50), onde o autor tinha escrito "respeitar a regra
> geral de não utilizar travessões": **a regra geral é a de função.**

### X5 · "Supera as baselines externas" — sim na categoria, não na região 🛑

O autor pede (`C51`) que o S45 deixe **visualmente evidente** que o método supera as externas. A regra §8.2 é dura: *"'
Supera' só nas três células de §5.1"* — e essas três células são contra o modelo **dedicado**, não contra a literatura.

**O que a dissertação de fato autoriza** (do slide de reserva `B6-5`, que já está escrito e citado ao Cap. 5
§5.2/§5.5.4):

- **Próxima categoria — comparação limpa.** POI-RGNN é **nativo da tarefa** e está acima do piso Markov-K nos seis.
  Frase do próprio capítulo: *"the joint model stands **at least 3.06 points**
  above the strongest external baseline at every dataset."* ✅ **isto pode ir para a tela.**
- **Próxima região — o documento afirma, o capítulo hedge.** ⚠ **Correção ao que eu tinha escrito:**
  o Abstract entregue **diz** *"On both tasks, the joint model's results were also above those reported by the external
  baselines"* (`content.tex:265`). **Então NÃO é sobre-afirmação em relação ao documento** — é uma afirmação que o
  documento faz. **Mas o capítulo a enquadra com cuidado**, e o slide de reserva `B6-5` diz por quê: *"No published
  model targets this exact task"* (o mais próximo, DRRGNN, prevê região sobre regiões descobertas por pessoa, não uma
  partição fixa), e o **piso Markov-1 está acima do HMT-GRN nos seis datasets** e do STAN em quatro. O capítulo trata
  **o piso**, e não os sistemas externos, como referência de região. → **Pode ser dito. Não deve ser manchete.** Superar
  uma baseline que o próprio piso não-aprendido supera não é o argumento forte, e uma banca externa vê isso na hora.
- **A ressalva que vale para os dois eixos:** as externas rodam sobre os embeddings delas, então a margem **inclui a
  vantagem de representação**. *"The comparison that decides the thesis is the Dedicated column."*

> **Proposta para o S45:** a tabela dá destaque à coluna **Dedicated × Joint** (é ela que decide a
> tese) e mostra a coluna **External** com os nomes reais; a mensagem "acima da literatura" aparece
> **só na linha de categoria**, com a ressalva de representação numa nota de uma linha. O eixo de
> região ganha o **piso Markov** como referência, não a comparação externa.

---

## 4B · Os riscos da dissertação que tocam os slides desta lista

> O estudo da dissertação (13 agentes, `kb/00_MAPA.md`, seção F) catalogou **43 contradições e
> riscos**. A maioria não toca o deck. **Estes seis tocam — e cinco deles tocam exatamente um slide
> que esta lista manda mudar.** Não são motivo para não mudar; são a ressalva que acompanha a mudança.

### R-α · O ganho de região em TX e CA mede CAPACIDADE, não partilha *(risco F-12)*

Estudo pós-entrega **P1**, medido em 2026-08-13. Pareando o orçamento de parâmetros com o do modelo conjunto inteiro
(seed 0, 5 folds):

| dataset    | dedicado estreito | **dedicado pareado** | conjunto | conjunto − pareado |                  p |
|------------|------------------:|---------------------:|---------:|-------------------:|-------------------:|
| California |            63,446 |           **64,931** |   64,503 |         **−0,428** | 0,0082 (5/5 folds) |
| Texas      |            64,951 |           **66,330** |   66,117 |         **−0,214** |       0,1162 (4/5) |

Veredito literal do estudo: *"A vantagem reportada mede **capacidade, não partilha entre tarefas**."*
A curva satura a **57%** do orçamento do conjunto. Errata escrita, **não aplicada** ao volume.

> **Toca:** `C51` / `X5` (dar destaque a "superamos"), o S45, o S46, e o S3 — que **sai** por A3, o
> que já ajuda.
> **Regra que decorre: não fortalecer a afirmação de região em lugar nenhum do deck principal.**
> Os `+1,21` e `+1,06` continuam corretos como estão escritos (contra o dedicado **como publicado**),
> e o capítulo já os chama de **resultados secundários, fora do plano registrado**. Isso basta.
> Há reserva pronta: **`B-P1`** e **`U2`** (duplicados — ver `E9`).
> **Enquadramento que sobrevive, e é bom:** *"um modelo serve as duas tarefas com o orçamento de dois,
> sem custo mensurável em categoria e com paridade em região. Isso é consolidação."*

### R-β · ✔ RESOLVIDO (AUT-13) — e a verificação inverteu a minha leitura

Eu tinha marcado a remoção da linha de `Controls` como **risco de esconder** um resultado
inconveniente. **O autor disse que o teste é pré-leak, fui verificar, e ele está certo — com uma
consequência mais dura do que ele disse.**

**A frase entregue** (`06_results.tex:41-47`): o controle de concatenação *"raises the place embedding
by only **+2.0, +1.7, and +0.8** macro-F1, **under a tenth of the place-to-check-in gap** at each
state."*

🛑 **Essa aritmética é impossível contra a Tabela 9 entregue.** Os gaps place→check-in de lá são
**AL +1,62 · AZ +2,58 · FL +0,23**. Um ganho de **+2,0** sobre um gap de **1,62** é **123% do gap**,
não *"under a tenth"*. **"Under a tenth" só fecha contra um gap de ~20 pontos** — que é o que existia
**antes da correção de vazamento**, quando a categoria estava inflada em ~28 pontos em Alabama.

> ✅ **Portanto os números `+2.0 / +1.7 / +0.8` são de uma geração superada (pré-v18), e a afirmação
> presa a eles é falsa contra a tabela do próprio capítulo.**
> **Remover a linha não é esconder: é corrigir.** E o estudo pós-entrega Q13 (2026-08-16, pós-v18)
> mede o controle de verdade — fecha **111% / 68% / 490%** do gap — e é ele que a reserva `B-Q13`
> carrega.
>
> ⚠ **O que NÃO muda:** a conclusão central — **a representação de entrada domina a arquitetura** —
> continua **apoiada** por esse resultado, não contrariada.
>
> ⚠ **E o que fica aberto, para a arguição:** a frase *"under a tenth of the gap"* **está no volume
> entregue** e é aritmeticamente falsa contra a Tabela 9 do mesmo volume. Sai do slide, mas **não sai
> do documento**. Se a banca fizer a conta, a resposta honesta é que o controle foi medido numa
> geração anterior e re-medido depois, com o resultado na errata `errata_Q13_concatenation_scope.tex`.

### R-γ · Duas condições com verbo forte, três com verbo fraco *(risco F-01, verificado e corrigido por mim)*

> ⚠ **A síntese apontou o Abstract, e o Abstract está OK.** Fui ler: `content.tex:265` diz
> *"its effectiveness **depends on** the input representation and the sharing topology"* — "depends
> on", não "determine". Isso é compatível com o Cap. 6. **A discrepância é outra e é mais estreita.**

**O locus real é `1_introduction.tex:425-426`, a seção de Contribuições:**

- **Cap. 1 §Contributions (Theoretical):** *"The studies **show** that the input representation and its sharing topology
  **determine** whether MTL helps these POI prediction tasks."*
  → **duas** condições · verbo assertivo · **{representação, topologia}**;
- **Cap. 6 §The consolidated answer:** *"The controlled comparisons identify **the input representation as one
  condition**, while the results **suggest** that **the architecture and dataset scale may matter**, although their
  individual effects were **not fully isolated**."*
  → **três** condições · duas com verbo fraco · **{representação, arquitetura, escala}**.

**São duas diferenças, não uma:** o *verbo* (`determine` × `identify one / may matter`) **e a lista**
(topologia × arquitetura + escala).

⚠ **E o deck é FIEL ao Cap. 1:** o bloco de contribuição do S50 reproduz a frase do Cap. 1 palavra por palavra. **A
tensão está dentro do documento entregue, e o deck a herdou.** Não é defeito do slide.

> **Toca `K5`, `K18` e o S50 inteiro.** O autor quer as **três condições** (input representation,
> architecture, scale) tanto no S49 quanto como contribuição científica no S50.
> **A versão segura é a do Cap. 6**, e o S49 hoje já a respeita (*"established by controlled ablation"*
> × *"suggested, not isolated"* × *"a possible condition, not an established cause"*).
> **Se o S50 listar as três em pé de igualdade, ele afirma mais do que o Cap. 6 estabelece.**
> A banca lê o Abstract e cobra o Cap. 6. **Manter a gradação nos dois slides.**

### R-δ · Dois protocolos, vereditos opostos nas mesmas células *(risco F-14)*

Cap. 5 (δ = 2 pp): Istanbul/categoria = **não resolvido**; Alabama/região = **não-inferior**. Estudo `mtlcheck` (δ = 0,4
pp, protocolo aninhado, leitura selada 2026-08-18): Istanbul/categoria = **SUPERIOR**; Alabama/região = **INFERIOR**.
**Nenhum dos dois documentos declara qual prevalece.**
> **Toca `C39`/`C40`** — a nota de rodapé que o autor quer no S43 sobre *"aprimoramento posterior do
> protocolo de avaliação estatística"*. **É exatamente este estudo.**
> ⚠ **Regra dura: nunca misturar um número do `mtlcheck` com um da dissertação na mesma frase.**
> A nota do S43 pode dizer que houve refinamento; **não pode dar número, e não pode sugerir que os
> vereditos mudaram.** A redação que o autor já propôs (*"The statistical evaluation protocol was
> later refined based on the literature"*) é segura **porque não dá número**. Manter assim.

### R-ε · A tabela de errata do Cap. 4 não está no PDF *(risco F-21)*

O Cap. 4 corrige o artigo publicado **silenciosamente**: 16→15 de 21 combinações; 20-24 → **20,2-22,0 pp**. A tabela de
errata existe no fonte e **não sai no PDF entregue**.
> **Toca o S28 e o S29.** O `+20,2 a +22,0 pp` do S28 é **o número corrigido**, não o publicado. Se o
> S28 sair (`A14`/`D3`), o número sai com ele — e a correção deixa de ser dita em qualquer lugar.
> **Mais um argumento para a decisão do S28 ir ao orientador com o custo na mesa.**

### R-ζ · Nash-MTL foi adotado no Cap. 3 sem um único número *(riscos F-06, F-37)*

O Cap. 3 diz que o Nash-MTL *"consistently yielded a better overall performance"* — **sem número**. E o *"later
finding"* que o enfraquece, citado no S20, **nunca é descrito** em lugar nenhum. Além disso, a coluna `MTL` de
*next-category* do Cap. 3 **não reproduz de nenhum artefato** conhecido.
> **Toca `M20`** (*"melhorar a descrição de Nash-MTL"*) e `M22`.
> ⚠ **Melhorar a descrição é seguro; acrescentar evidência não é, porque não há.** O slide atual está
> na redação certa: *"A conclusion of the time, weakened by a later finding."* **Não converter isso
> numa afirmação mais forte.**

---

### R-η · Mais sete riscos que tocam itens desta lista *(achados numa revisão adversarial)*

Eu tinha cruzado seis riscos da dissertação com o deck. **Faltavam sete, e cada um toca um item que esta lista manda
mexer.**

| risco                                                                                                                                                                                                                                                           | toca                                                                                                                                                         | o que fazer                                                                                                                                                                                                                                                                                             |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **F-15** · o modelo conjunto tem **três** contagens de parâmetros sem reconciliação (**4,2 M** no texto entregue · **6,9 M** numa reconstrução do modelo atual · **4.197.621** pelo caminho da receita)                                                         | **S47** — exatamente o slide que `C58`–`C62` mandam reescrever, e cuja tela diz *"4.2 M parameters at Alabama against 1.1 M for the two dedicated combined"* | ⚠ a **§8.9 do PLANO já proíbe repetir o `1,1 milhão` como se estivesse verificado**, e proíbe citar a recontagem (1.850.980), que **não tem fonte no repositório**. A reescrita do S47 tem de carregar essa ressalva. **Se a pergunta vier, a resposta é que a razão de parâmetros não foi re-medida** |
| **F-04** · *"none of them is a direct baseline"* (`2_fundamentals.tex:335`) × **STAN é baseline de região no Cap. 5**, aparecendo 27×                                                                                                                           | **§6.5** (a tabela nova do S45) e **S8**                                                                                                                     | a conciliação é **baseline adaptada, não direta** — e o `1_introduction.tex:454` já a declara: *"Neither adaptation reproduces its complete published system."* **Uma linha na tabela resolve**                                                                                                         |
| **F-28** · o Cap. 2 chama o piso de maioria de *"for **category classification**"* (a tarefa estática, Def. 2.6), mas no Cap. 5 ele é referência da **next-category**                                                                                           | **F20** (S13), que manda rotular *"Majority class — reference point"*                                                                                        | ⚠ **não copiar o rótulo do Cap. 2**, senão o slide aponta para a tarefa errada                                                                                                                                                                                                                         |
| **F-29** · o rótulo da linha de Markov tem **três** versões: *"strongest order per dataset"* (impresso) · *"Markov-9-cat"* (comentário de proveniência) · K=5/3 (nos estudos)                                                                                   | **T5** / **P2.1** — o slide novo de Markov                                                                                                                   | **não fixar uma ordem específica na tela.** Dizer *"best Markov order per dataset"*, que é o impresso                                                                                                                                                                                                   |
| **F-10** · peso da perda: **0,50/0,50** no texto entregue × **0,75/0,25** no `CLAUDE.md` da raiz do repo e nos docs v17                                                                                                                                         | **F6**/**F9** (o slide de balanceador) e **S39**                                                                                                             | ⚠ **quem pesquisar "o peso usado" fora de `src/` pega o número errado.** O entregue é **0,50/0,50, por design**                                                                                                                                                                                        |
| **F-05** · o "suspeito 2" do Cap. 3 fala da representação **APRENDIDA pelas camadas compartilhadas** (*"the representation learned by the shared layers might have become biased"*); os Caps. 1 e 6 o reescrevem como **representação de ENTRADA insuficiente** | **S22**, que o `M33` manda **manter** com revisão de clareza                                                                                                 | ⚠ **uma revisão de clareza sem este aviso pode "corrigir" para a versão errada.** A reinterpretação é a costura que justifica o Cap. 4 inteiro — ela é deliberada, não um deslize                                                                                                                      |
| **F-43** · as **oito perguntas cuja resposta honesta é "não foi medido"** têm resposta preparada, e é **a família B5 inteira (10 slides)**                                                                                                                      | **E10**/**E12** (cortar a Série B)                                                                                                                           | 🛑 **a B5 entra na lista de NÃO-CORTÁVEIS**, junto do critério da §7.3. Cortar ali é ficar sem resposta para as perguntas que já se sabe que vêm                                                                                                                                                        |

### R-θ · O objetivo contrastivo do DGI é degenerado — e agora existe a prova, não só o sintoma

**Achado da sessão `tikz`, ao desenhar o diagrama; verificado por mim no código entregue.**

**O que o texto entregue diz** (e o §6.1 repete, porque é a especificação do autor): a corrupção
**embaralha a matriz de features** dos nós, e **os dois grafos passam pela mesma GNN** — duas passadas.

**O que o código faz** (`research/embeddings/dgi/model/DGIModule.py:66-73`):

```python
x = self.poi_encoder(data.x, data.edge_index)   # UMA passada, só
summary = self.readout(x)                        # média sobre os nós, depois sigmoid
permuted_idx = torch.randperm(x.size(0))
x_corrupted = x[permuted_idx]                    # permuta as REPRESENTAÇÕES já codificadas
pos_score = self.discriminator(summary, x)
neg_score = self.discriminator(summary, x_corrupted)
```

> 🛑 **E a consequência é matemática, não empírica.** O `summary` é **um vetor único, igual para todo
> nó** (`:30`), e o discriminador é `linear(summary ⊙ x_i)` (`:43`) — **o score de um nó depende só
> dele e do resumo global**. Como `x_corrupted` é uma **permutação do mesmo conjunto**, o **multiconjunto
> de scores positivos e o de negativos são idênticos, exatamente**. A BCE pedindo 1 para um e 0 para o
> outro tem ótimo em todos os scores iguais a zero, o que dá perda **2·ln 2 ≈ 1,3863**.

**Isto explica um sintoma que o deck já registra.** O slide de reserva **`B4-DGI`** diz hoje:

> *"An audit recorded, incidentally and outside the leak question, that the contrastive objective **as
> implemented appears degenerate**: positive and negative score sets **identical as multisets**, and a
> measured loss floor matching **2·ln 2 to six decimals**. **If confirmed**, *"trained DGI embedding"*
> may not describe what Chapter 3 actually used."*

> ✅ **O "if confirmed" pode cair.** Os multiconjuntos idênticos e o piso em 2·ln 2 **não são
> coincidência medida: são o que aquelas três linhas produzem necessariamente.** A auditoria mediu o
> sintoma; o código dá a causa.

**O que isto NÃO muda, e é importante dizer:** o Cap. 3 reporta um **resultado nulo**. Um embedding
sub-treinado torna o nulo **menos** surpreendente, não invalida uma afirmação positiva — o capítulo não
tem nenhuma. E o Cap. 4 **substituiu** essa entrada, que é exatamente o experimento que ele fez.

**O que fazer:**
- **o diagrama (§6.1) segue o TEXTO ENTREGUE**, com dois grafos e a mesma GNN. Uma figura que
  contradiga o capítulo na frente da banca é pior que a divergência. *(Recomendação da `tikz`, e
  concordo.)*
- **atualizar o `B4-DGI`**: trocar *"appears degenerate… if confirmed"* por a causa, com a linha do
  código. É mais forte responder *"sim, e eu sei exatamente por quê"* do que *"uma auditoria sugeriu"*.
- ⚠ **e registrar como resposta oral**, porque a pergunta natural depois do diagrama é *"o texto diz
  duas passadas; o código faz uma?"*.

### R-ι · Duas correções ao meu próprio `P2.16` (o fluxo do HGI)

Também da `tikz`, também verificadas por mim:

1. 🛑 **O HGI tem DOIS objetivos contrastivos, não três.** As três fronteiras
   (`check-in→lugar`, `lugar→região`, `região→cidade`) e a equação de pesos `0.4/0.3/0.3`
   (`2_fundamentals.tex:711-713`, `eq:fund:check2hgi`) são **do Check2HGI**. O HGI tem
   `lugar→região` e `região→cidade`. **Confirmado no fonte.**
2. 🛑 **A prosa do Cap. 2 OMITE um passo do HGI.** Entre a atenção POI→região e a soma ponderada pela
   área existe uma **GCN de nível de região, sobre um grafo de adjacência de regiões** —
   `research/embeddings/hgi/model/RegionEncoder.py:35,191-192` (`GCNConv`, comentário literal
   *"Apply region-level GCN on adjacency graph"*). **Os quatro passos do `P2.16` são uma compressão da
   prosa, não o mecanismo completo.**

> **Consequência para a `AUT-8`:** quando o autor escrever o fluxo do HGI, **vale ele saber dos dois
> antes** — senão o diagrama sai mais pobre que o mecanismo, e com o número de objetivos errado.

---

---

## 4C · Ficha do S46 — o slide mais próximo do limite

> **Correção de um erro que circulou e que eu tinha copiado: NÃO há colisão com o número da página.**
> Medido por caixa de glifo (`pdftotext -bbox`): a tinta do corpo termina em **x = 0,893**; o "46"
> começa em **x = 0,963**. Nunca se tocam. O que parecia colisão é proximidade vertical.

**O defeito real é pior:** a última linha desce a **y = 1,004** — os descendentes passam da borda inferior da página.
Estouro de **17,9 pt**. Ninguém tentou consertar ainda.

**Três restrições, e elas eliminam os caminhos óbvios:**

1. **A folga NÃO pode vir do texto.** As duas linhas de leitura sob a tabela são redação de lei:
   *"all four are deficits, not ties"* · *"the widest interval reaches 0.34 from zero"* · *"read off the intervals, not
   established by a further test"*. A §8.6 (ressalva antes da manchete)
   e a lei do veredito obrigam cada uma. **Cortar aqui é regressão, não enxugamento** — e é por isso que o `C56`, como o
   autor o escreveu, não pode ser executado ao pé da letra.
2. **Reduzir o corpo não está disponível: já está em `\scriptsize`.** E o caminho contrário custa caro — subir **um**
   degrau leva este slide de 17,9 para **48,5 pt**.
3. **Nada de `\vspace` negativo.** O deck já acumulou 31 e as sobreposições que a varredura de 24/08 corrigiu.

> **O caminho a tentar primeiro é a tabela: `\arraystretch` e as colunas de intervalo de confiança,
> que são as mais largas.** Foi o que resolveu o S28 sem tocar em conteúdo.
> O pedido do autor de **aumentar a tabela** (`C57`) vai na direção oposta e precisa ser
> reinterpretado como *"tornar a tabela mais legível"*, não *"maior"*.

---

## 4D · Vocabulário: cinco correções pendentes, e o registro NÃO está aberto

Auditoria de terminologia fechada em 25/08, com comentários LaTeX filtrados. **Nada aplicado.**
O que deu limpo também é resultado: **zero inconsistência de grafia** em todo o deck (`Check2HGI`,
`MTLnet`/`ST-MTLNet`, `macro-F1`, `Sphere2Vec-M`, `next-POI`, o hífen de `next-category`), **zero palavra banida** no
deck principal, e `macro-F1` nunca rotulando os números por categoria dos Caps. 3/4.

| #      | achado                                        | slide                     | ação                                                                                                                                                                                                                                                                                                                                                                                                              |
|--------|-----------------------------------------------|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **V1** | `controlled ablation` usado na **afirmativa** | **S49**                   | Não é contradição — o Cap. 6 continua com *"Chapter 4 is the fixed-pair control for the diagnosis"* (`6_conclusion.tex:349`). É risco de arguição: o slide usa afirmativamente um termo que a conclusão usa na negativa, sem dizer de qual ablação fala, e o slide `U6` da reserva repete a versão negativa. **Correção: nomear o Cap. 4. Cinco palavras.** *(Um auditor chamou isto de contradição e exagerou.)* |
| **V2** | `fine class` fora de escopo                   | **S27**                   | A entrada do `GLOSSARY` restringe o termo a *"Appendix B §B.5 only"*. Ou parafrasear, ou o autor amplia o escopo                                                                                                                                                                                                                                                                                                  |
| **V3** | família `stream` / `tower` sem registro       | **S37, S38** + 4 slides B | `semantic stream`, `spatial stream`, `category stream`, `region stream`, `private tower`, `shared-context tower`, `region tower`. **É buraco do registro, não defeito do deck** — todos vivem na prosa entregue (`2_fundamentals.tex:235-236`, `04_method.tex:27`, `apx_h:236,295-296,318-322`)                                                                                                                   |
| **V4** | `Markov-K floor` sem registro                 | 2 slides B                | Vocabulário entregue (`06_results.tex:260`); o registro só cobre o piso de classe majoritária e o `Markov-1 floor`                                                                                                                                                                                                                                                                                                |
| **V5** | `expert-based routing`                        | **S22**                   | **Vocabulário que o deck inventou.** O Cap. 3 já nomeia: *"Mixture-of-Experts (MoE) models"* (`3_cbic/conclusion.tex:23`). ⚠ o autor pediu para **manter o S22** (`M33`) — esta é a única mudança que ele precisa                                                                                                                                                                                                |
| **V6** | `frozen` no slide B6-1                        | reserva                   | `WRITING_LAW` §2 manda `fixed` fora do sentido de pesos congelados. **Único termo banido no arquivo inteiro**                                                                                                                                                                                                                                                                                                     |

> 🛑 **Três dos cinco mexem no `GLOSSARY`, e o registro NÃO está aberto.**
> O autor autorizou **dois termos** em 25/08 (`Delaunay triangulation`, `mutual information`) e disse
> explicitamente que era isso, **não uma varredura**. **Não existe precedente.** Se `V3`, `V4` — ou a
> proposta de registrar `contrastive` do `F11` — forem em frente, cada um precisa de autorização
> própria dele.

---

## 4E · Três decisões que não estão em arquivo nenhum

A sessão `presentation` foi desligada. Estas três passaram por ela, **não estão escritas em lugar nenhum**, e morreriam
com a sessão. Ficam aqui.

1. **O registro de termos não foi aberto.** Dois termos autorizados em 25/08, e só. Ver 4D.
2. **O autor rejeitou enquadrar o RESULTADO NEGATIVO DO CAP. 3 como contribuição direta.** Foi proposto e recusado: *"o
   resultado negativo não é uma contribuição direta."* O nulo é produtivo porque **fabrica os três suspeitos**, e é
   assim que a Seção 3 o narra — mas ele **não vai para a lista de contribuições**. **Não reintroduzir.**
   *(Coerente com o `K33`, que manda remover do S53 a frase "The negative result was not an obstacle to the
   contribution. It was its first half.")*

   > 🛑 **A fronteira, porque eu mesmo a errei numa primeira leitura:**
   >
   > | item | veredito |
      > |---|---|
   > | o **nulo do Cap. 3** como contribuição direta | **recusado por ele. Não reintroduzir** |
   > | a **identificação das condições** como contribuição científica | **É a contribuição dele.** Está em tela, e a redação atual saiu de um pedido textual dele para *fortalecer* esse ponto. **Manter** |
   >
   > O `K18` **não** é a tentação descrita acima. O que ele pede — as três condições no S50 — é o que
   > o autor mandou reforçar. **O cuidado é outro, e é o da R-γ: não achatar o estatuto probatório.**
3. **A Série B NÃO foi varrida de travessão, de propósito.** São ~59 ocorrências. Decisão de escopo, sancionada pelo
   autor quando mandou commitar. **Se alguém "terminar o trabalho", desfaz a decisão que ele acabou de reconfirmar (
   AUT-4).**

---

## 4F · O que quebra sem aviso — para quem implementa

**Pipeline e build — o essencial; o resto está no `HANDOFF.md` §3 e §4, não duplicado aqui**

- **Ordem obrigatória: `SLIDES.md` → reconstruir o deck → regenerar o `SPEECH`.** O extrator confere títulos contra o
  **PDF construído**; regenerar antes de reconstruir casa com títulos velhos e **não avisa**.
- ⚠ **O `% FALA` do `.tex` NÃO é espelho da fala** — o bloco de comentário carrega notas de projeto junto. Uma medição
  de "deriva em seis blocos" foi feita contra ele e **a deriva não existe**. **Para medir sincronia, meça texto de
  TELA.**
- ⚠ **`SB<n>` não casa `S\d+`** — os 48 blocos da Série B **nunca chegam ao `SPEECH.pdf`** (`Q17`).
- ⚠ **Circulou que os quatro frames do protocolo (impressos 40–43) são UM bloco no `SLIDES.md`. Medi: são QUATRO**
  (`S41`–`S44`). O que é verdade é que os títulos divergem, e o extrator tem `ALIAS`.
- **`xelatex`, duas passagens.** Sob `pdflatex` a capa e os divisores saem **em branco, sem erro**.
- **Nunca `make` em `articles/dissertacao/src/`** — cinco alvos sobrescrevem o `dissertacao.pdf`.
- **Estouro é silencioso**, e `\begin{frame}{t}{s}` é sintaxe válida (o corpo aberto com chave vai para dentro da faixa
  do título). **Renderizar sempre:** `pdftoppm -f N -l N -png -scale-to-x 1230`.
- **A linha de base é 25 páginas com `Overfull`, não 24.**

> 🔴 **CORREÇÃO à segunda linha acima, e ela custou o dia — medida em 26/08.**
> O aviso *"o `% FALA` do `.tex` NÃO é espelho da fala"* está certo sobre a **contagem de palavras** (os blocos de
> comentário carregam notas de projeto). **Está errado sobre o CONTEÚDO**, e a inferência que ele autorizava —
> *"não meça sincronia por ali"* — deixou passar a terceira superfície do projeto.
>
> **O `.tex` e o `SLIDES.md` divergiram em 17 das 50 falas.** Não por erro de um dos dois: por **edição de um só
> lado**. E como o `SLIDES.md` é a **fonte do `SPEECH`**, em todas as 17 é a versão dele que vai para a boca do autor.
>
> **O que a divergência estava carregando, e cada item é uma decisão registrada voltando pela porta dos fundos:**
>
> | onde | o que ressuscitava | morto por |
> |---|---|---|
> | `S53`, `S52` | a *"sexta limitação"* — o confound de par de tarefas | **`AUT-11`** |
> | `S12` | *"toda tabela que eu reproduzir vai levar esse carimbo"* | **`AUT-5`** |
> | `S41` | *"estas não são as mesmas janelas dos Capítulos 3 e 4"* | **`C30`/`G5`** |
> | `S44` | *"o Wilcoxon é reportado ao lado **e concorda**"* | **sem proveniência no volume** |
>
> **E na direção contrária, que é a pior:** a **ressalva de vazamento** do `S30` (*"a entrada da tarefa estática
> contém o rótulo que ela prediz"*) e a **divulgação de que o controle de dimensão nunca foi executado** (`S31`)
> existiam **só no deck**. Uma regeração do `SPEECH` **apagava as duas da fala** — e são as duas divulgações de
> honestidade mais caras da Seção 4.
>
> ✅ **Fechado em 26/08:** 16 das 17 sincronizadas (10 copiadas do deck, 6 corrigidas à mão). **O `S46` ficou de fora
> de propósito** — é uma das cinco falas reescritas e não aplicadas, e sincronizar antes da decisão do autor seria
> escrever por cima da reescrita.
>
> 🔧 **A ferramenta existe e é de segundos: `presentation/diff_fala.py`** (escrita pela `ppt`). **Rode-a antes de
> cada regeração do `SPEECH`.** ⚠ **Ela pareia por posição, não por título** — dois frames com o mesmo
> `\frametitle` são dois frames, e deduplicar por título quebra os overlays.

**Risco de perda de dado, fora do escopo desta lista**

- O vídeo de referência (a defesa do a defesa de referência) está em `presentation/exemples/`, que é **gitignored**
  — **6,6 GB que existem só em disco**. O backup registrado no `CLAUDE.md` §2 é de 20/08 e **não contém o vídeo**.

---

## 5 · Mudanças, slide a slide

### 5.0 · ➕ Os itens que ACRESCENTAM, e o que cada um obriga a tirar

Pela regra **G11**, nenhum destes pode ser especificado sozinho. A coluna da direita é o que eu vou propor que saia;
onde estiver `?`, é decisão que ainda não tem resposta.

| ➕ item                   | slide   | o que entra                                                                                                 | o que sai do mesmo slide                                                                                                      |
|---------------------------|---------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `R5` + `F6` + `T5` + `D2` | **S9**  | o item de MTL vindo do S7, uma explicação de *balancing method*, possivelmente Markov, possivelmente Pareto | ⚠ **o S9 não absorve tudo isso.** Ver a nota abaixo                                                                          |
| `F11`, `F13`              | S10/S11 | Contrastive InfoMax na tela, Graph InfoMax                                                                  | ⚠ **provável duplicata** — os dois já existem em alguma forma. Verificar antes de tratar como acréscimo                      |
| `M20`                     | S20     | descrição melhor de Nash-MTL                                                                                | o bloco *"What Chapter 3 claims"* perde a moldura (`M22`) e a nota de rodapé sai (`M25`)                                      |
| `A17`                     | **S29** | a tabela de Category Classification                                                                         | as três notas de interpretação encolhem (`A18`) e o `Metric stamp` sai (`X2`). ⚠ **e depende do S28 sobreviver** — ver `6.3` |
| `C25`                     | S38     | explicação de Cross-Attention (2 linhas)                                                                    | a faixa inferior vira item curto (`C27`) e os nomes de stream saem (`C24`)                                                    |
| `C37`                     | S42     | a fórmula do joint-best                                                                                     | a explicação textual da convenção, que a fórmula substitui                                                                    |
| `C39`                     | S43     | nota de rodapé de uma linha                                                                                 | nada — é uma linha; cabe                                                                                                      |
| `K3` + `K5` + `K6`        | S49     | a nota de não-extrapolação e as três condições descritas                                                    | *"Identifying these conditions is the main finding…"* sai (`K8`) e o bloco *"What it does not authorize"* encolhe             |
| `K15`–`K18`               | S50     | Check2HGI nos dois blocos + as três condições                                                               | o texto extenso do *Joint model* vira uma linha (`K12`)                                                                       |
| `K22` + `K23`             | S51     | os anos e a ressalva de que a limitação é da literatura                                                     | a coluna direita (*next steps*) encolhe para caber                                                                            |

> ### ⚠ O S9 não cabe, e isso é um achado da própria lista
> Com a reorganização **D1**, o S9 recebe: as duas definições que já tem (*hard sharing*, *negative
> transfer*), **mais** o item de MTL do S7 (MCARNN, CSLSL, iMTL, HAMTL, TME), **mais** uma explicação
> de *balancing method*, **mais** possivelmente Pareto (D2) e Markov (T5). São cinco blocos onde hoje
> há três — e a G11 diz que **três blocos podem ter de virar dois** por causa do respiro novo.
>
> **Proposta: o bloco de MTL da Seção 2 vira DOIS slides**, não um:
> - **S9a — MTL: como duas tarefas dividem um modelo.** Hard sharing · negative transfer · o critério
>   do balanceador (em redação descritiva, ver P2.2);
> - **S9b — MTL em POI.** O que a literatura de mobilidade fez (o item vindo do S7) + o eixo
>   meio × fim (que é o **S8** de hoje, e que já é sobre isso).
>
> Isso **não cria um slide novo**: o S8 já existe e é exatamente o conteúdo do S9b. É reordenar e
> mover um item, não inflar. E o Markov vai para o **S13**, junto do *majority-class floor*, porque
> os dois são pontos de referência e o S13 é o slide de métricas.

### 5.1 · Seção 1 — Introdução

| ID      | Slide  | Status          | O que fazer                                                                                                                                                                                                                                                                                                                                                             |
|---------|--------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **I1**  | S1     | ✅              | Inverter a ordem do 2º e do 3º itens: *"people return to a small set of places…"* passa a vir antes de *"potential predictability… 93 percent"*                                                                                                                                                                                                                         |
| **I2**  | S1     | ✅              | Título → **Human Mobility** (o slide introduz o conceito e a área)                                                                                                                                                                                                                                                                                                      |
| **I3**  | S2     | ✅              | Remover o item *"human mobility research studies how people move through a city"* — o conceito já entrou no S1                                                                                                                                                                                                                                                          |
| **I4**  | S3     | 🔎 P3.1         | Procurar no template um componente que apresente a research question melhor que o `block` vazio de hoje                                                                                                                                                                                                                                                                 |
| **I5**  | S3     | ✅              | Reformular a pergunta para soar natural falada. Referência do autor: *"Does multitask learning help predict the category and region of the next point of interest? And what does the answer depend on?"* — a redação exata é livre                                                                                                                                      |
| **I6**  | S3     | ✅ **AUT-3**    | **A tabela de resultados sai inteira.** O slide fica com a pergunta e a restrição de modelo único. A composição visual deixa de ser problema porque o elemento que a quebrava era a tabela de três colunas                                                                                                                                                              |
| **I7**  | S3     | ✅ **AUT-3**    | **Resolvido: a Introdução não antecipa o veredito.** Consultar advisor deixa de ser necessário                                                                                                                                                                                                                                                                          |
| **I8**  | S3     | ✅ **AUT-3**    | **Resolvido de graça:** os nomes de dataset (Texas, California, Florida) estavam **só** na tabela do veredito. Saindo ela, a Seção 1 volta a ser 100% genérica e a exceção registrada no `PLANO §3` deixa de ser usada                                                                                                                                                  |
| **N1a** | S3     | ⚠️ **AUT-3**    | **Reescrever a fala.** A fala atual promete *"a resposta eu dou agora, no minuto três"* — deixa de ser verdade                                                                                                                                                                                                                                                          |
| **N1b** | S3→S46 | ⚠️ **AUT-3**    | **Mover a etiqueta `INTRODUZ` do veredito** de 1.3 para o S46 no `SLIDES.md`, senão o ledger fica com elemento sem dono                                                                                                                                                                                                                                                 |
| **I9**  | S4     | 🔎 P1.1 + P2.22 | Revisar a definição de *next place* contra a terminologia dominante da literatura. ⚠ **risco F-02:** a Introdução diz que *next place* está fora de escopo, e o **título do Cap. 3** diz *"Next-POI Prediction"*. A ponte existe nos prefácios dos Caps. 3 e 4 e no `GLOSSARY`, **não na Introdução**. O S5 já carrega o aviso (*"Naming trap"*) — confirmar que basta |
| **I10** | S4     | ✅              | Remover o último item (*"The constraint again: one trained artifact, one forward pass, both outputs"*). ⚠ **com A3, o S3 passa a ser o único lugar da abertura onde a restrição de modelo único aparece** — então ela tem de **ficar no S3** e sair aqui, não o contrário                                                                                              |
| **I11** | S6     | ✅ **AUT-2**    | **O slide sai.** Ver X1 para as duas coisas que a remoção arrasta (a definição sincronizada no `SLIDES.md` e a ressalva *operational, not computational*)                                                                                                                                                                                                               |
| **D1**  | S4     | ⚖️ D1           | O S4 pode migrar inteiro para Fundamentos, fundido ao S15                                                                                                                                                                                                                                                                                                               |

### 5.2 · Seção 2 — Fundamentos compartilhados

| ID         | Slide     | Status       | O que fazer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|------------|-----------|--------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **F1**     | S7        | ✅           | Manter o conteúdo, reorganizar a hierarquia visual. O problema é prioridade entre informações, não conteúdo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **R4**     | S7        | ⚖️ D1        | Retirar o 4º item (*"in mobility, MTL has served next place almost entirely: MCARNN, CSLSL, iMTL, HAMTL. TME…"*) e levá-lo para o S9                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **T3**     | S7        | ✅           | Remover *"the pair the first two studies attack: category classification and next-category prediction"*. No lugar, uma frase **abaixo** de *"in mobility, MTL has served…"*: **em geral esses modelos não produzem duas saídas; usam MTL só para apoiar a tarefa principal de next-POI**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **F2**     | S8        | ✅           | Dar destaque visual às baselines por tarefa. A fonte pode continuar pequena; há espaço para quebra de linha. Hoje é uma linha corrida: `next category POI-RGNN, Markov… \| next region HMT-GRN, STAN, ReHDM, Markov-1 floor \| Ch. 3 HMRM, MHA+PE \| Ch. 4 MTLnet`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **D1.c**   | S8        | ⚖️ D1        | Considerar mover o S8 para depois do S9 (o S8 é sobre MTL)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **F4**     | S9        | ✅ G1        | Título → **MTL Fundamentals** (ou, se D1/R5 for aceito, **MTL Fundamentals and POI**)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **F5**     | S9        | 🔎 P2.17     | Verificar se há outro fundamento de MTL que valha meia linha aqui                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **F6**     | S9        | 🔎 P2.17     | Incluir explicação **curta** de *balancing method* — o que é e para que serve. ⚠ §8.16 proíbe formalismo do zoo de balanceadores                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **F7**     | S9        | ✅           | *Negative transfer* — **já está** (Def. 2.12). Nada a fazer, item satisfeito                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **F8**     | S9        | 🔎 P2.2      | O bloco *"The criterion this dissertation states"* parece deslocado; avaliar remoção                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **F9**     | S9        | 🔎 P2.2      | A frase *"A balancing method is useful only if it improves on a tuned fixed weighting"* é excessivamente restritiva e **balanceadores são usados nos dois primeiros estudos, não no terceiro**. Achar a formulação teoricamente correta **e discutir antes de substituir**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **R5**     | S9        | ⚖️ D1        | Absorver o item de MTL vindo do S7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **D2**     | S9        | ⚖️ D2        | Possivelmente absorver a definição de Pareto vinda do S19                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **F11**    | S10/S11   | 👤           | **Contrastive InfoMax — parcialmente feito, e o resto é decisão dele.** O commit `1627c5b9` corrigiu o bloco que se chamava "infomax" e de fato descrevia o **estimador contrastivo**; o S11 hoje separa os dois (*"Infomax names what is maximized… The pairing test is the estimator"*). ⚠ Mas a palavra **`contrastive` ficou na FALA, não na tela**, por duas razões registradas: o Cap. 2 cortou a palavra de propósito (`2_fundamentals.tex:523`) e ela **já está em tela com outro sentido** (a perda contrastiva de 10 km/70 km do Cap. 4, no S27). **Se o autor quiser a palavra na tela, o termo precisa ser registrado no `GLOSSARY` (§8.11 é fail-closed) — e o registro NÃO está aberto: ele autorizou dois termos em 25/08 e disse que era isso. Ver §4D.** |
| **F12**    | S10       | ✅ **FEITO** | **Triangulação de Delaunay já entrou.** O commit `372d4026` registrou o termo no `GLOSSARY` §3 e o pôs em tela, no bloco *"The substrate the three have in common"*. Nada a fazer — **confirmar com o autor que é isso que ele queria**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **F13**    | S10       | ⏱            | Se couber, um quarto elemento sobre **Graph InfoMax**. ⚠ o degrau *"graph infomax"* **já é o quarto item da escada** no S10. Provável duplicata do F11; **verificar antes de acrescentar fala**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **F14**    | S10       | ✅           | DGI/HGI/Check2HGI: **só citados**. Quanto menos fala aqui, melhor — cada um tem o capítulo dono                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| **F10**    | S11       | 👤 D3        | Avaliar remoção. ⚠ **o slide foi criado por decisão do autor em 25/08** (`372d4026`); fundi-lo de volta desfaz essa decisão. **Meu parecer: fundir de volta no S10, não apagar — mas é ele quem fecha.** Ver D3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **F15**    | S12       | ✅           | Remover *"Florida appears twice, as two extractions: 990,518 check-ins in Chapters 3 and 4; 1,407,034 in Chapter 5."* A diferença entre ETLs sai da apresentação principal (há reserva pronta: `B4-4`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **F16**    | S13       | ✅           | O 2º item (*why — the class distribution is imbalanced…*) vira **subitem** do item de macro-F1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **F17**    | S13       | ✅           | O 3º item (*what it does not do…*) vira **subitem** também                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **F18**    | S13       | 🔎 P2.11     | Remover o 4º item (*"the loss is not reweighted — unweighted cross-entropy"*). Se a banca perguntar, responde-se falando                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **F19**    | S13       | 🔎 P2.11     | **Antes de remover**, conferir no Cap. 5 se a cross-entropy é usada com pesos — para o slide não contradizer o procedimento                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **F20**    | S13       | ✅           | O item de **majority class** (hoje o 5º e último) vira **"Majority class — reference point"** + descrição curta, deixando explícito que é ponto de referência e **não** baseline competitiva                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **F21**    | S14       | ✅ G8        | Melhorar a apresentação visual; as relações entre as informações têm de ficar claras. Itens podem continuar sendo a solução                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **F22**    | S14       | 🔎 P2        | Avaliar a remoção do 4º item (*The verb law*). **Cuidado:** é ele que explica por que os Caps. 3 e 4 não dizem "supera". Se sair da tela, tem de existir na fala (protocolo §4c)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **T1**     | S14       | ✅           | Remover a **frase** *"The verb law: outperforms is reserved for a paired superiority test…"* — mesmo item que F22, dito no primeiro bloco do original                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **T2/F23** | S14       | 🛑 X3        | *"The metric convention changes"* — o autor quer fora. Conflita com X2. Ver X3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **F24**    | S14       | ⚖️           | Remover *"The task pair changes"* — **mas** o autor também disse (T2) que é justamente **a mudança de tarefas** que ele quer comentar. **Contradição interna do original; precisa de decisão**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **F25**    | S14       | ⚖️ X3        | Considerar remover o bloco *Two traps* inteiro, já que ambas as informações reaparecem nas seções dos artigos                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **T2b**    | S14       | ✅           | Se o bloco ficar, renomear *"Two traps"* → **"Two points of attention"** / **"Two notes"**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **T5**     | S9 ou S13 | 🔎 P2.1      | **Explicar Markov** em algum slide de Fundamentos. Meu palpite: no **S13**, junto do *majority-class floor*, porque os dois são pontos de referência — mas depende de P2.1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

### 5.3 · Seção 3 — MTLnet (Cap. 3)

| ID          | Slide    | Status       | O que fazer                                                                                                                                                                                                                             |
|-------------|----------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **R1/R2**   | S15      | ⚖️ D1        | Mover para Fundamentos, possivelmente fundido ao S4                                                                                                                                                                                     |
| **T6**      | S15      | 🔎 P2.23     | *"A history of **nine** visits"* → **"a history of N visits"**. É uma definição; a janela é um hiperparâmetro                                                                                                                           |
| **M1**      | S16      | 🛑 X4        | Revisar travessão                                                                                                                                                                                                                       |
| **M2**      | S16      | ✅ **AUT-5** | Remover as duas notas de rodapé (`Task stamp` + `Metric stamp`)                                                                                                                                                                         |
| **M3**      | S16      | ✅           | Usar o espaço liberado para **aumentar a figura** `cbic_mtlnet_arch`                                                                                                                                                                    |
| **M4**      | S17      | ✅           | Remover a redundância: *"graph attention → one 64-dimensional vector per place"* (coluna esquerda) e *"What it gives — one vector per place; every visit enters with the same vector"* (coluna direita) dizem a mesma coisa. Consolidar |
| **M5**      | S17      | ✅           | Delaunay e InfoMax já terão sido apresentados no S10; aqui **só mencionar** que o método os usa                                                                                                                                         |
| **M6**      | S17      | ✅           | Reduzir o tempo de fala: os fundamentos funcionam como referência ao pipeline                                                                                                                                                           |
| **M7**      | S17      | ✅           | Manter os dois blocos visualmente distintos, mas testar composição **vertical** (um abaixo do outro) em vez de lado a lado                                                                                                              |
| **M8**      | S17      | 🆕 §6.1      | **Novo diagrama do DGI.** Especificação completa em §6.1                                                                                                                                                                                |
| **M11/M15** | S18      | ⚖️ D3        | Remover da principal. **Parecer contrário registrado em D3** — o que se perde é o protocolo declarado e a lei dos verbos                                                                                                                |
| **M12**     | S18      | ✅           | O corpus de Florida do Cap. 3 (990.518) pode sair da principal                                                                                                                                                                          |
| **M14**     | S12/S18  | ✅           | Em Fundamentos, manter só o que é necessário para entender o **Cap. 5**                                                                                                                                                                 |
| **M16**     | S19      | ⚖️ D2        | Mover para Fundamentos, inteiro, em parte, ou não mover. Ver D2                                                                                                                                                                         |
| **M17**     | S19      | 🔎 P2.3      | Tornar explícito que o fenômeno descrito é **negative transfer**, o conceito já introduzido no S9                                                                                                                                       |
| **M18**     | S19      | 🔎 P2.3      | Revisar a relação entre **Pareto dominance**, conflito entre tarefas e negative transfer. O slide menciona Pareto mas não fecha a explicação                                                                                            |
| **M19**     | S19      | ⚖️ D2        | Não mover mecanicamente: escolher entre incorporar tudo, incorporar em parte, ou dividir                                                                                                                                                |
| **M20**     | S20      | 🔎 P2        | Melhorar a descrição de **Nash-MTL** — conceitualmente mais clara                                                                                                                                                                       |
| **M21**     | S20      | 🛑 X4        | Revisar travessão                                                                                                                                                                                                                       |
| **M22**     | S20      | ✅           | Reavaliar se *"What Chapter 3 claims"* precisa de `alertblock`. Provavelmente não                                                                                                                                                       |
| **M23**     | S20      | ✅ G5        | Remover *"and Chapter 5 does not rely on it"*                                                                                                                                                                                           |
| **M25**     | S20      | ✅           | Avaliar remover a nota *"Criterion from Section 2, still standing: useful only if it improves on a tuned fixed weighting"* — já discutida em Fundamentos                                                                                |
| **M26**     | S20      | 🔎 P2.2      | Remover ou revisar *"useful only if it improves on a tuned fixed weighting"*. Mesma dúvida de F9, e aqui é ainda menos necessária                                                                                                       |
| **M28**     | S21      | ✅           | *"Static task"* → **"Category classification"**. ⚠ a Def. 2.6 da dissertação é **"category classification"**, não *"categorical classification"* — a §8.11 é **fail-closed**: usar o termo do glossário                                |
| **M29**     | S21      | ✅           | Remover *"both of our models score above HMRM in every category"*                                                                                                                                                                       |
| **M30**     | S21      | ✅ G4        | Aplicar negrito/sublinhado também na tabela da esquerda (hoje só a da direita tem sublinhado)                                                                                                                                           |
| **M31**     | S21      | ✅ **AUT-5** | Remover as duas notas de rodapé. **Este é um dos slides mais densos do deck** — a altura liberada vai para as tabelas                                                                                                                   |
| **M32**     | S21      | ✅           | *"F1 block only; mean ± standard deviation over the five folds"* está mal escrita e no corpo. Reescrever e mandar para **rodapé curto**, deixando claro que **± é o desvio sobre os cinco folds**                                       |
| **M33**     | S22, S23 | ✅           | Manter. Só revisão final de clareza e concisão                                                                                                                                                                                          |

### 5.4 · Seção 4 — ST-MTLNet (Cap. 4)

| ID          | Slide | Status       | O que fazer                                                                                                                                                                                                                                                     |
|-------------|-------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **A1**      | S24   | ✅           | Título do bloco → só **"The inherited question"**, removendo *"suspect 2 against suspect 3"*                                                                                                                                                                    |
| **A2**      | S24   | 🛑 X4        | Revisar travessão                                                                                                                                                                                                                                               |
| **A3**      | S24   | 🔎 P2.15     | Reescrever o 4º item — *"same latent width on both sides: the per-task encoders project any input to 256"* não é compreensível. Descobrir o que quer dizer e dizer simples                                                                                      |
| **A4**      | S24   | ✅           | Remover o 5º item (*"three states: Florida, California, Texas. Protocol as in Chapter 3."*) — os datasets aparecem sozinhos nos resultados. ⚠ *"Protocol as in Chapter 3"* está no mesmo item; se sair, confirmar que o protocolo continua dito em algum lugar |
| **A5**      | S24   | ✅ **AUT-5** | Remover o `Task stamp`                                                                                                                                                                                                                                          |
| **A6**      | S25   | ✅ **AUT-5** | Remover as duas notas. A figura `arquitetura_modelo` ganha a altura                                                                                                                                                                                             |
| **A7**      | S26   | 🆕 §6.2      | **Novo diagrama do HGI**, substituindo boa parte do texto                                                                                                                                                                                                       |
| **A8**      | S26   | ✅           | Reduzir o texto: nada de descrever passo a passo o que a fala vai dizer sobre o diagrama                                                                                                                                                                        |
| **A9**      | S26   | 👤           | **Aguardar a descrição do fluxo do HGI que o autor vai fornecer**, como fez com o DGI                                                                                                                                                                           |
| **A10–A13** | S27   | ✅           | Manter estrutura, blocos e títulos. Só revisão de redação (mais curta, mais natural) e de composição visual                                                                                                                                                     |
| **A14–A16** | S28   | ⚖️👤 D3      | Candidato a remoção; **decisão vai ao orientador**. Parecer completo em D3                                                                                                                                                                                      |
| **A17**     | S29   | 🆕 §6.3      | **Adicionar a tabela de Category Classification.** Hoje o slide só mostra Next Category                                                                                                                                                                         |
| **A18**     | S29   | ✅           | Reestruturar os itens de interpretação: hoje exigem leitura cuidadosa. A audiência tem de bater o olho e entender o achado                                                                                                                                      |
| **A19**     | S29   | ✅           | Hierarquia explícita: separar **observação**, **interpretação** e **conclusão**                                                                                                                                                                                 |
| **A20**     | S29   | ✅ **AUT-5** | Remover as duas notas. **A altura liberada é o que torna viável a segunda tabela do `A17`**                                                                                                                                                                     |
| **A32**     | S29   | ✅ G4        | Convenção negrito/sublinhado nas **duas** tabelas                                                                                                                                                                                                               |
| **A21**     | S30   | ✅ G1        | Título mais direto que *"What the decomposition moved, and where it did not"*                                                                                                                                                                                   |
| **A22**     | S30   | ⚖️           | Decidir a função do slide: **Conclusions**, **Limitations**, ou os dois. Hoje mistura                                                                                                                                                                           |
| **A23**     | S30   | 🔎 P2.20     | *"Travel, labeled by task"* não comunica. Descobrir o que significa; se não der para dizer simples, **remover o bloco**                                                                                                                                         |
| **A24**     | S30   | ✅           | **Manter** *"No universally better spatial encoder"* — é conclusão importante do artigo                                                                                                                                                                         |
| **A25**     | S30   | ✅           | **Manter** *"Not width-matched"* como limitação, revisando a redação (*"192 dimensions against 64"*)                                                                                                                                                            |
| **A26**     | S30   | ✅           | Separar visualmente o que é conclusão do que é limitação                                                                                                                                                                                                        |
| **A27–A30** | S31   | ✅           | Reduzir muito. Condensar o achado em **uma linha**, e usar o resto como **transição para o Cap. 5**. Função: fechamento + gancho, não nova explicação. ⚠ §8.12: slide de transição é estrutural e **não pode ser removido** — encolher, sim                    |

### 5.5 · Seção 5 — Check2HGI (Cap. 5)

| ID          | Slide | Status                           | O que fazer                                                                                                                                                                                                                                                                                                                                                                                                        |
|-------------|-------|----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **C1**      | S32   | ✅                               | Manter a tabela — funciona como abertura da seção                                                                                                                                                                                                                                                                                                                                                                  |
| **C2**      | S32   | ✅                               | **Não** incluir a mudança de ETL na tabela                                                                                                                                                                                                                                                                                                                                                                         |
| **C3**      | S32   | ✅                               | Aumentar o respiro entre linhas e colunas                                                                                                                                                                                                                                                                                                                                                                          |
| **C4**      | S32   | ✅                               | Manter o bloco *"The task pair changes here"*                                                                                                                                                                                                                                                                                                                                                                      |
| **C5**      | S32   | ✅                               | Reescrever a primeira frase do bloco (*"Under a check-in-level representation, static category classification is a less natural companion than a second sequential target"*) — mais clara e natural                                                                                                                                                                                                                |
| **C6**      | S32   | ✅                               | Remover *"The restriction holds: one artifact, one forward pass, two answers."*                                                                                                                                                                                                                                                                                                                                    |
| **C7**      | S33   | ✅                               | Manter o conteúdo do bloco `Scope`; renomear para **"Practical applications"**                                                                                                                                                                                                                                                                                                                                     |
| **C8**      | S33   | 🔎 P2.12                         | *"520 (Istanbul) to 8,501 (California)"* — por que esses dois? Confirmar se California é mesmo o máximo (TX tem 6.553) e se a faixa está correta                                                                                                                                                                                                                                                                   |
| **C9**      | S33   | ✅ G2                            | Reescrever *"coarser than a place, not easier"*                                                                                                                                                                                                                                                                                                                                                                    |
| **C10**     | S34   | ✅                               | Manter a estrutura — o slide está bom                                                                                                                                                                                                                                                                                                                                                                              |
| **C11**     | S34   | ✅                               | Dar mais ênfase visual ao bloco *"The novelty is the combination"* — é um dos pontos centrais                                                                                                                                                                                                                                                                                                                      |
| **C12**     | S34   | ✅                               | Compactar a explicação de **CTLE** (hoje em três itens)                                                                                                                                                                                                                                                                                                                                                            |
| **C13**     | S35   | 🆕 §6.4                          | **Refazer a figura** `fig1_dataflow` para slide: hoje está a 0,50 da largura e comprimida                                                                                                                                                                                                                                                                                                                          |
| **C14**     | S35   | ✅                               | Figura maior, menos elementos, foco **só na extensão do HGI** introduzida aqui                                                                                                                                                                                                                                                                                                                                     |
| **C15**     | S35   | ✅                               | Reduzir a **dois** pontos: (1) foi acrescentada uma camada de **check-in**, de onde sai a representação por visita; (2) o modelo produz vetores de **64 dimensões**, um vindo da camada de check-in e outro da camada de **região**, este último entrando no *next region*                                                                                                                                         |
| **C16**     | S35   | ✅                               | Não reexplicar o HGI — o Check2HGI é apresentado como **extensão**                                                                                                                                                                                                                                                                                                                                                 |
| **C17**     | S36   | ✅ G1                            | Encurtar o título / subtítulo (*"The node features, and one design principle"* + *"A design principle, in the chapter's own wording"*)                                                                                                                                                                                                                                                                             |
| **C18**     | S36   | ✅ G2                            | Reescrever *"The consecutive-visit edges run in one direction only, from an earlier visit to a later one…"* — curta, direta, compreensível numa leitura                                                                                                                                                                                                                                                            |
| **C19**     | S37   | ✅                               | Concentrar o texto em explicar **Silhouette Score** e **KNN purity**                                                                                                                                                                                                                                                                                                                                               |
| **C20**     | S37   | ✅                               | **Não** repetir os valores em texto — estão na figura e podem ser ditos                                                                                                                                                                                                                                                                                                                                            |
| **C21**     | S37   | ✅                               | Reduzir ou remover a nota de rodapé, que comprime a figura                                                                                                                                                                                                                                                                                                                                                         |
| **C22/C23** | S37   | ⚖️ D4                            | **Mover para junto do S44**, virando o Resultado 1 da nova sequência. Ver D4                                                                                                                                                                                                                                                                                                                                       |
| **C24**     | S38   | ✅                               | Remover *"semantic stream"* / *"spatial stream"* onde não forem necessários; dizer **Next Category** e **Next Region**                                                                                                                                                                                                                                                                                             |
| **C25**     | S38   | 🔎 P2.5                          | **Adicionar explicação clara de Cross-Attention** — é o diferencial arquitetural em relação aos Caps. 3 e 4                                                                                                                                                                                                                                                                                                        |
| **C26**     | S38   | 🔎 P2.4                          | Validar *"The tasks share by exchanging information between per-task streams, not by owning hidden layers in common."* ⚠ **o próprio slide diz, três linhas acima, "the shared trunk — a cross-attention stack of two blocks"**. Como escrito, o slide se contradiz                                                                                                                                               |
| **C27**     | S38   | ✅                               | A frase inferior não pode ocupar faixa própria abaixo da figura; se ficar, vira item curto                                                                                                                                                                                                                                                                                                                         |
| **C28**     | S39   | ✅ G1                            | Título mais direto que *"The private spatial path, and what the evidence does not separate"*                                                                                                                                                                                                                                                                                                                       |
| **C29**     | S39   | ✅                               | Considerar continuidade com o S38: *"Architecture: sharing by exchange"* + *"Part II"*                                                                                                                                                                                                                                                                                                                             |
| **C30/C31** | S40   | ✅ G5                            | Remover o 4º item (*"not the same windows as Chapters 3 and 4, which used non-overlapping ones"*)                                                                                                                                                                                                                                                                                                                  |
| **C32**     | S40   | 🔎 P2.10                         | Revisar o 5º item (*"the held-out fold provides the validation data — no third split is reserved. Limit 2…"*): explicar melhor antes de decidir se fica                                                                                                                                                                                                                                                            |
| **C33**     | S41   | ✅                               | Macro-F1 já explicado no S13; manter só como indicação da métrica, sem redefinir                                                                                                                                                                                                                                                                                                                                   |
| **C34**     | S41   | 🔎 P2.6                          | **OOD-discounted Acc@10** — confirmar que a métrica existe no texto entregue com esse nome. **Não manter sem evidência**                                                                                                                                                                                                                                                                                           |
| **C35**     | S41   | 🔎 P2.1                          | Reavaliar o item *"Reference points for region"* (Markov-1 floor), já que Markov será discutido depois. Se T5 mover Markov para Fundamentos, aqui vira uma linha                                                                                                                                                                                                                                                   |
| **C36**     | S42   | 🔎 P2.8                          | Revisar *"Inferential unit: n = 4, the four per-seed means"* — reescrever simples ou remover                                                                                                                                                                                                                                                                                                                       |
| **C37**     | S42   | 🔎 P2.7                          | Substituir a explicação textual de *"The joint-best convention"* pela **fórmula**; a interpretação vai na fala                                                                                                                                                                                                                                                                                                     |
| **C38**     | S43   | 🔎 P2.8                          | Revisar *"Declared departure: registered Wilcoxon reported alongside, and agrees"*                                                                                                                                                                                                                                                                                                                                 |
| **C39**     | S43   | 🔎 P2.18                         | Nota de rodapé **muito curta**, marcada com asterisco: houve **aprimoramento posterior do protocolo de avaliação estatística com base na literatura**                                                                                                                                                                                                                                                              |
| **C40**     | S43   | ✅                               | Tom da nota: **não** *"we created a protocol"*. Preferir *"The statistical evaluation protocol was later refined based on the literature."* ⚠ §8.8: material pós-submissão em geral só vai na Série B — a nota de uma linha é a exceção que o autor está pedindo; **confirmar**                                                                                                                                   |
| **C41**     | S43   | ✅                               | A nota é gatilho visual; o detalhe vai na fala                                                                                                                                                                                                                                                                                                                                                                     |
| **C42**     | S44   | ⚠️ **R-β / Q14**                 | Remover *"Controls — CTLE (Florida) 33.45 macro-F1; feature concatenation +2.0 / +1.7 / +0.8"*. ⚠ **essa é a linha do controle de concatenação, que o estudo pós-entrega Q13 mostra ser mais forte do que o capítulo afirma** (fecha 111% / 68% / 490% do gap). Remover é permitido; **esconder, não**. Se sair, a resposta tem de estar na fala e a reserva `B-Q13` tem de continuar viva                        |
| **C43**     | S44   | ✅                               | Remover a última frase do slide                                                                                                                                                                                                                                                                                                                                                                                    |
| **C44**     | S44   | ✅                               | Remover *"All five folds favor the check-in-level representation at every dataset. A paired test separates the two columns at every dataset except Florida (p = 0.07)."* ⚠ a segunda metade é uma ressalva estatística; ver protocolo §4c antes de tirá-la da tela                                                                                                                                                |
| **C45–C54** | S45   | 🛑 X5 + 🆕 §6.5                  | **Refazer a tabela**, não só aumentá-la. Especificação completa em §6.5                                                                                                                                                                                                                                                                                                                                            |
| **C55**     | S46   | ✅                               | Ordenar os datasets na ordem canônica do deck. Hoje o S46 usa `TX, CA, FL, Istanbul, AZ, AL` (ordem do resultado) e o S12 usa `Istanbul, AL, AZ, FL, TX, CA` (ordem por nº de regiões, que é a do documento). **Escolher uma e aplicar em todo o deck** (S12, S44, S45, S46)                                                                                                                                       |
| **C56**     | S46   | 🛑 **NÃO EXECUTAR COMO ESCRITO** | Remover os dois parágrafos *"Region."* e *"Category."*. ⚠⚠ **essas duas linhas são redação de lei**, não prosa: carregam *"all four are deficits, not ties"*, *"the widest interval reaches 0.34 from zero"* e *"read off the intervals, not established by a further test"* — a ressalva que a §8.6 e a lei do veredito obrigam. **Cortar aqui não é enxugar, é regressão.** Ver a ficha completa do S46 em §4C |
| **C57**     | S46   | ✅                               | Usar o espaço liberado para aumentar a tabela. ⚠ a última linha (*"…read off the intervals, not established by a further test"*) é **obrigatória pela lei do veredito** e não pode ser a vítima do corte                                                                                                                                                                                                          |
| **C58**     | S47   | ✅ G1                            | Título → **"Limitations and trade-offs"**                                                                                                                                                                                                                                                                                                                                                                          |
| **C59**     | S47   | 🛑 X4                            | Revisar travessão                                                                                                                                                                                                                                                                                                                                                                                                  |
| **C60**     | S47   | ✅ G2                            | Reescrever os itens para leitura rápida                                                                                                                                                                                                                                                                                                                                                                            |
| **C61**     | S47   | 🔎 P2.10                         | Reescrever *"Epoch selection reads the fold it scores — absolute scores are optimistic"*. A limitação é: **a época é escolhida no mesmo conjunto em que o número é reportado**; não há terceiro split                                                                                                                                                                                                              |
| **C62**     | S47   | 🔎 P2.9                          | *"Each visit draws only on the visits that precede it"* — descobrir a restrição causal que isso descreve e reescrever explicitamente, ou remover                                                                                                                                                                                                                                                                   |

### 5.6 · Seção 6 — Conclusão

| ID              | Slide | Status                              | O que fazer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-----------------|-------|-------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **K1**          | S48   | ✅                                  | **Manter a tabela** — funciona muito bem como síntese                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **K2**          | S48   | ✅ G8                               | Reduzir a densidade das células. Hoje exige leitura demais para um slide de conclusão                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **K3**          | S49   | ✅                                  | Depois da primeira frase do bloco *"The answer"*, acrescentar que as conclusões **não se extrapolam entre os estudos**. Redação de partida: *"The conclusions are study-specific; what carries across studies is the methodology and the conditions identified."*                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **K4**          | S49   | ✅                                  | Deixar explícito que a resposta é **condicional**, nem sim nem não                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **K5**          | S49   | ✅ ⏱                                | Reorganizar os três últimos itens nas **três condições**: **1. Input representation · 2. Architecture · 3. Scale**. ⚠ o texto atual gradua a força de cada uma (*"established by controlled ablation"* × *"suggested, not isolated"* × *"a possible condition, not an established cause"*) — **essa gradação não pode sumir** na reorganização. ⚠⚠ **risco de arguição levantado pela sessão `presentation`:** o slide usa `controlled ablation` na **afirmativa**, e o Cap. 6 registra a mesma expressão na **negativa**. Não é contradição (o capítulo diz *"Chapter 4 is the fixed-pair control"*), mas resolve-se **nomeando o capítulo** na tela                                                                                                                                                          |
| **K6**          | S49   | ✅                                  | Cada condição com descrição curta e direta                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **K7**          | S49   | 🛑 X4                               | Sem travessão entre nome e explicação; usar dois-pontos ou quebra de linha                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **K8**          | S49   | ⚠️ **a frase é VERBATIM do Cap. 6** | Remover *"Identifying these conditions is the main finding of this dissertation."* ⚠ **verificado: é citação literal de `6_conclusion.tex:169`**, não editorialização do deck. **Três consequências:** (1) a remoção é **preferência retórica** do autor, não conformidade com a lei — nada na `WRITING_LAW` a proíbe (a §147 bane auto-referência *à escrita*, que é outra coisa); (2) **a frase tem de ir para o campo `Fala (PT)` do S49, não sumir** — é a resposta escrita do Cap. 6 à pergunta *"qual é a principal contribuição do seu trabalho?"*, e ela aparece **uma única vez** no `main.tex` hoje; (3) ela é a **âncora de proveniência da gradação** — a frase e o *established × suggested × possible* saem do mesmo parágrafo do capítulo, e quem tirar uma sem saber tende a tirar a outra junto |
| **K9**          | S50   | 🛑 X1                               | Reconstruir aqui o conteúdo de contribuições. Depende de X1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **K10**         | S50   | ✅ G1                               | Título → **"Contributions"**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **K11**         | S50   | ✅                                  | Manter os dois blocos: **Practical** e **Scientific**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **K12/K13**     | S50   | ✅                                  | Practical → item simples centrado em **"Joint model"**, dizendo que a contribuição é **operacional**, não redução de custo computacional. Evitar *"one model, one forward pass, two predictions"* se estiver deixando o slide verboso. ⚠ §8.13 exige a ressalva *"operational, not computational"* explícita                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **K14**         | S50   | 🛑 X4                               | Sem travessão. Proposta do autor: *"Joint model — operational integration rather than computational reduction"* → sem travessão                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **K15/K16**     | S50   | ✅                                  | Practical → incluir **Check2HGI**, com a ideia de que é um **artefato reutilizável** por trabalhos futuros, não restrito a este experimento                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **K17**         | S50   | ✅                                  | Scientific → **Check2HGI** também, aqui pela **novidade metodológica/arquitetural**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **K18**         | S50   | ✅ ⚠️ **R-γ**                       | Scientific → as **três condições** (input representation, architecture, scale). ✅ **é a contribuição científica declarada da dissertação, e a redação atual saiu de um pedido do próprio autor para fortalecê-la** — não confundir com o resultado negativo do Cap. 3, que ele recusou como contribuição (§4E). ⚠ **o cuidado é o estatuto:** *established by controlled ablation* (representação) × *suggested, not isolated* (arquitetura) × *a possible condition, not an established cause* (escala). **Listá-las achatadas como "as três condições que identificamos" é a regressão a evitar**                                                                                                                                                                                                             |
| **K19/K20**     | S50   | 🔎 P1.3 + P2.19                     | O **protocolo estatístico** pode ser reivindicado como contribuição científica? **Não colocar sem sustentação** — a dissertação, até onde se sabe, **não o reivindica**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **K21**         | S51   | ✅                                  | Manter **Data vintage**, com discussão mais precisa                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **K22**         | S51   | 🔎 P2.13                            | Incluir os **anos**, sobretudo de Istanbul/Massive-STEPS, para mostrar que houve tentativa de usar dado mais recente                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **K23**         | S51   | ✅                                  | Deixar claro que a antiguidade **não é limitação só desta dissertação**: é restrição recorrente da literatura de POI/check-ins                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **K24**         | S51   | 🔎 P1.2                             | **Confirmar na literatura** se é correto dizer que datasets públicos amplamente utilizáveis raramente passam de ~2022, **antes** de pôr no slide                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **K25/K26**     | S51   | 🔎 P2.21                            | Reescrever *"Taxonomy coarseness — seven top-level classes"* para explicitar que a limitação é de **granularidade e número de categorias**, e que outras taxonomias poderiam mudar os resultados                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **K27**         | S51   | ✅                                  | Item 3 (*Transductive representation*): manter, e dizer, quando couber, que também é limitação recorrente da literatura                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **K28**         | S52   | ✅                                  | Manter o item 4 (**No next-place task**)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **K29**         | S52   | ✅                                  | Manter o item 5 (**Geographic coverage**)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **K30**         | S52   | ⚖️                                  | Reavaliar o item 6 (**The task-pair confound**). Preferência do autor: **remover**. ⚠ **parecer contrário:** é a limitação mais forte da dissertação e a única que a banca externa provavelmente vai levantar (par, representação e topologia mudaram juntos). Remover parece frágil. **Decisão do autor**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **K31**         | S53   | ✅ G8                               | Simplificar radicalmente. O fecho não recapitula resultados                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| **K32**         | S53   | ✅                                  | Tirar os links de GitHub do corpo; se ficarem, em nota discreta                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **K33**         | S53   | ✅                                  | Remover *"The negative result was not an obstacle to the contribution. It was its first half."* e qualquer outra recontagem da evolução                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **K34/K35/K36** | S53   | ✅                                  | Construir o fecho em **uma frase forte** que responda à pergunta central e deixe claro que o benefício do MTL é **condicional** — dependendo sobretudo de **input representation, architecture e scale**. O último slide conceitual **encerra**, não abre discussão                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **K37**         | S54   | ✅                                  | Título → **"Obrigado"**, em português                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **K38**         | S54   | ✅                                  | Subtítulo **"Acknowledgements"** abaixo, menor                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **K39**         | S54   | ✅                                  | Manter agradecimento breve a: **orientador · instituição · banca · colegas de pesquisa**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **K40**         | S54   | ✅                                  | Simples, limpo, pouco texto                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |

---

## 6 · Artefatos novos a produzir

### 6.0 · Quem produz os diagramas, e o gabarito

**Uma sessão dedicada — `tikz` — foi criada pelo autor para produzir os diagramas TikZ.** Escopo dela:
os artefatos das §6.1, §6.2 e §6.4. **Ela não toca no `slides/main.tex`** — entrega cada figura como
`.tex` standalone e itera visualmente com o autor antes de declarar pronta; a integração é da `ppt`.

**O gabarito, medido** (`nesped.sty:27-37`, `:54`, `:59`):

|             | valor                                                                                                                                                                                                   |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| página      | **16 × 9 cm = 453,54 × 255,12 pt**                                                                                                                                                                      |
| margens     | `text margin left/right = 10 mm` → **largura útil 14 cm ≈ 396,85 pt**                                                                                                                                   |
| altura útil | a faixa do título come **0,171 a 0,348** da página, **e varia por slide** — pedir a altura exata à `ppt`                                                                                                |
| paleta      | `primary` .22/.69/.61 · `primaryshade` .18/.61/.58 · `primarytint` .90/.95/.94 · `secondary` .04/.27/.47 · `secondarytint` .88/.92/.96 · `alert` .74/.07/.43 · `alertshade` .48/.19/.40 · `offwhite` .9 |

🛑 **Três armadilhas passadas à `tikz`:** o `nesped.sty` carrega tikz **só com `calc` e `shadows`** — **`positioning` não
vem junto** e precisa entrar também no preâmbulo do deck · **`primaryshade` sobre branco dá 3,33:1, reprovado para
corpo** · **branco sobre `primary` dá 2,67:1, reprovado** (só a ponta
`secondary` do degradê passa, com 9,83:1). ⚠ **E o rótulo do diagrama não pode usar corpo reduzido:** `\scriptsize` e
`\small` **reprovam** para a banca no remoto pela régua de altura-de-x. **`\normalsize` ou maior.**
**Desenhar para `\textwidth`**, não para meia largura — a `fig1_dataflow` está hoje a `0.50\textwidth`
e é justamente a que o autor achou pequena demais.

### 6.1 · Diagrama do DGI (S17) 🆕

Substituir parte da explicação textual por um diagrama simples, sobre o qual a explicação é feita **oralmente**.
Sequência a representar:

1. duas versões do grafo: **positivo/original** e **negativo/corrompido**;
2. **mesmo conjunto de nós** e mesma estrutura nos dois;
3. no positivo, cada nó mantém suas **features originais** (aqui, associadas aos POIs);
4. no negativo, as features são **embaralhadas entre os nós** — nós e arestas preservados, a correspondência nó↔feature
   quebrada;
5. os dois grafos passam pela **mesma GNN** (mesmos parâmetros);
6. a GNN produz representações para os nós dos dois grafos; do positivo sai também um **resumo do contexto global**;
7. as representações vão a um **discriminador**, que avalia a compatibilidade de cada representação de nó com o contexto
   global do grafo positivo;
8. objetivo contrastivo: **~1** para o positivo, **~0** para o corrompido;
9. a saída alimenta a **loss contrastiva**; o gradiente volta pelo discriminador e pela GNN;
10. resultado: embeddings que preservam a relação entre cada nó e o contexto global.

**Duas restrições do autor:**

- o diagrama **não** explica a matemática. Ele sustenta uma fala curta:
  *grafo original → corrupção → mesma GNN → discriminador → loss*;
- ⚠ **não** representar o discriminador como classificador de *"grafo positivo × grafo negativo"*. O ponto do DGI é
  distinguir pares **nó–contexto global** compatíveis de incompatíveis.

**Nota de precisão que o `main.tex` já registra:** o discriminador do DGI **como entregue no Cap. 3 é LINEAR**, não
bilinear (`3_cbic/method.tex:50`). O diagrama não pode sugerir o contrário.

### 6.2 · Diagrama do HGI (slide 23) 🆕 — **DESBLOQUEADO em 2026-08-26**

> **A descrição do fluxo vive em [`hgi_draw.txt`](hgi_draw.txt)**, em forma textual — o mesmo formato
> da descrição do DGI que o autor escreveu (§6.1). **Não duplicar aqui.** O arquivo traz os sete
> passos com a fonte de cada um declarada, o que o desenho não deve fazer, a restrição de
> continuidade com o Check2HGI, e o orçamento do slide.

**Os dois pontos que mais importam, para quem só lê esta seção:**

- 🛑 **duas fronteiras contrastivas, não três.** As três (`check-in→lugar`, `lugar→região`,
  `região→cidade`) e a equação `0,4 / 0,3 / 0,3` são **do Check2HGI**;
- 🛑 **a prosa do Cap. 2 omite a GCN de nível de região** (passo 4), que existe no código.

### 6.3 · A tabela de Category Classification no slide 24 🆕 — **LIBERADA (AUT-17)**

**A dependência que a remoção da ressalva criou está resolvida pelo autor:** a tabela entra, **e a
ressalva de vazamento vai numa nota de rodapé**. Isso satisfaz a §8.6 (a ressalva **acompanha** o
resultado que ela limita) sem gastar um slide.

**Os dados** — Tabela 6 do Cap. 4, bloco de **Florida**, para ficar paralela à tabela de *next
category* que o slide já tem (Tabela 7, também Florida):

| | MTLnet | ST-MTLNet SIREN | ST-MTLNet Sphere2Vec-M |
|---|--:|--:|--:|
| Community | 51.86 ±0.73 | **70.00** ±0.81 | <u>69.84</u> ±0.98 |
| Entertainment | 41.24 ±1.83 | **64.45** ±1.82 | <u>63.92</u> ±1.61 |
| Food | 55.47 ±1.55 | <u>72.92</u> ±0.59 | **73.22** ±0.66 |
| Nightlife | 32.59 ±1.96 | **62.60** ±1.96 | <u>62.44</u> ±2.00 |
| Outdoors | 47.71 ±1.60 | <u>65.64</u> ±1.73 | **66.35** ±1.51 |
| Shopping | 62.96 ±0.62 | **77.48** ±0.36 | <u>77.47</u> ±0.72 |
| Travel | 45.49 ±1.20 | **64.89** ±1.20 | <u>64.77</u> ±1.54 |

**A nota de rodapé, e ela é obrigatória** — sem ela o número não pode ser dito:

> ⚠ *The static task's input **contains the label it predicts** — the venue-type feature maps
> one-to-one onto the seven categories — so these numbers measure a **lookup**, not learned semantic
> inference. **The sequential task, on the right, is the diagnostic result.***

**Por que a segunda frase importa tanto quanto a primeira:** ela diz **para onde olhar**. Sem ela, a
tabela da esquerda (ganhos de ~20 pp) domina visualmente a da direita, e a plateia leva embora o
número que **não** significa o que parece.

⚠ **Dois cuidados de número** *(risco R-ε)*: a **errata do Cap. 4 não saiu no PDF entregue**. Os
valores corrigidos são **15 de 21** combinações (não 16) e **+20,2 a +22,0 pp** (não 20–24).
**Usar os corrigidos.** E o `+20,2 a +22,0` é a **média por estado, tomando o melhor dos dois
encoders espaciais em cada célula** — não o ganho de uma configuração única.

### 6.4 · A figura do Check2HGI (slide 30) 🆕 — **SÓ A IMAGEM (AUT-18)**

**O slide perde os quatro marcadores.** Não é *figura + duas linhas*, como eu tinha especificado: é
**figura e nada mais**. Isso transfere para o desenho o que o texto carregava.

**Sai da tela e vai para a fala** — o autor já tinha decidido, e agora sem substituto na tela:
- as arestas (nível acima · lugares próximos · check-ins consecutivos com peso decaindo no tempo);
- o objetivo (infomax + os dois termos auxiliares, 0,3 e 0,1).

**Passa a ser obrigação da figura** — era texto, virou desenho:
1. **os quatro níveis nomeados, com o `check-in` marcado como o novo**: `check-in · place · region ·
   city`. ⚠ **É aqui que os rótulos de andar importam.** Na chapa do HGI eles não existem (lá são
   nomes de módulo); **aqui eles são o argumento**, e o `check-in` embaixo **é** a mensagem;
2. **as duas saídas, ambas de 64 dimensões** — um vetor **por visita**, da camada de check-in, e um
   vetor **por região**, da camada de região. ⚠ **e a segunda tem destino:** o vetor de região é o que
   alimenta a tarefa de *next region*.

**Duas coisas a favor do desenho:**
- **a caixa inteira do slide fica livre.** A `fig1_dataflow` está hoje a `0.50\textwidth` — foi ela
  que o autor chamou de *"pequena e comprimida demais para apresentação"*. Sem os marcadores, a
  figura tem a altura toda;
- **"revisitar" é convite, não conserto.** A figura atual é a da dissertação reaproveitada; ele quer
  **uma feita para slide** — menos elementos, foco na extensão que este trabalho introduz.

⚠ **E o parentesco com o HGI continua sendo a restrição mais importante:** esta chapa é a do HGI
**com um andar a mais embaixo**. Com os rótulos de nível aparecendo só aqui, o contraste fica claro —
lá módulos, aqui andares.

### A escolha que resta é de GÊNERO, não de completude *(corrigido 2026-08-26)*

⚠ **Correção de uma coisa que eu escrevi errado.** Eu tinha registrado que, se a figura escolhida
fosse o fluxo de dados, ela **não mostraria** as duas saídas nem marcaria o check-in — e que portanto
*"ou a figura mostra, ou os marcadores voltam"*. **Fui ao fonte da chapa nova (`figures/src/c2h_flow.tex`)
e é falso:**

```
:74  \node[newchip] (Lcheck) ... {check-in};        ← chip destacado, borda primaryshade 1,3 pt
:78  {\textbf{the level this work adds}}
:91  {\textbf{64-d per region}\\{from the region level}}
:93  {\textbf{64-d per visit}\\{from the check-in level}}
```

**Os dois pontos estão lá.** Eu tinha descrito a `fig1_dataflow` **original** como se fosse a chapa
nova. **O dilema não existe: nos dois casos o slide 30 fica sem marcador.**

**A escolha real, para o autor:**

| | o que mostra | o argumento que carrega |
|---|---|---|
| **Fluxo de dados** *(a chapa que existe)* | os quatro andares · o check-in marcado como o novo · as duas saídas de 64-d, com a origem de cada uma | ***"olha o que ele produz"*** |
| **Fluxo de treino** *(derivado da chapa do HGI)* | tornaria visual o *"é o mesmo método, um nível mais fundo"* | ***"olha que é o mesmo método"*** — ao custo de discriminadores e ramo corrompido competirem com os andares e as saídas |

**São duas coisas boas, não uma completa e uma incompleta.**

⚠ **E isso reformula a restrição que eu tinha marcado como a mais importante do desenho.** Eu escrevi
que *"a chapa do Check2HGI é a do HGI com um andar a mais embaixo"*. **Isso só vale se ele escolher o
fluxo de treino.** A `fig1_dataflow` é **fluxo de dados** e a do HGI é **fluxo de treino** — **não são
irmãs, e forçá-las a ser seria mentir sobre o que cada uma mostra.** Se ele ficar com o fluxo de
dados, o *"é o mesmo método, um nível mais fundo"* **é dito na fala, não mostrado.**

### A seta da trilha — verificado: NÃO é errata

Circulou que a `fig1_dataflow` teria um erro de fato, com a seta da trilha entrando no nível `region`.
**Fui ao fonte:** `src/figures/mobiwac/fig1_dataflow.tex:95` é `\draw[flow] (trail) -- (graph);` — o
alvo é **o nó da caixa**, e a caixa **é** o grafo. A trilha alimenta o grafo inteiro; a seta só
aterrissa no centro vertical, que calha de ficar na altura de `region`.

> **É imprecisão de desenho, não afirmação falsa. NÃO há errata da dissertação.** A chapa de slide
> aponta para o `check-in`, o que é melhor — mas a original não afirma nada falso.
> ⚠ **Registrado com esta precisão de propósito:** uma errata que não se sustenta, levada à banca com
> o nome do autor, custa mais do que a imprecisão que ela consertaria.

### 6.5 · O S45 refeito — e a mensagem é MELHOR do que "superamos a literatura" 🆕 (AUT-6)

> **Duas buscas fecharam sobre as duas afirmações da AUT-6. A primeira se sustenta com a redação
> certa. A segunda não — mas o que sobra no lugar é mais forte do que ela.**

#### O achado que vale a pena, e ele já está nos dados entregues

**Os três sistemas externos publicados ficam ABAIXO de um piso de Markov de primeira ordem.**

| dataset  | piso Markov-1 |  HMT-GRN |     ReHDM |      STAN | **Dedicated** | **Joint** |
|----------|--------------:|---------:|----------:|----------:|--------------:|----------:|
| AZ       |         51,23 | 43,70 ✗ |     53,00 |  49,86 ✗ |         59,48 |     59,04 |
| CA       |         59,09 | 49,61 ✗ | 50,26 ✗‡ | 58,52 ✗† |         63,48 | **64,54** |
| TX       |         60,10 | 53,85 ✗ | 48,81 ✗‡ |   61,67 † |         64,94 | **66,15** |
| AL       |         62,26 | 57,05 ✗ |     65,38 |  60,72 ✗ |         70,12 |     69,24 |
| Istanbul |         65,06 |  60,4 ✗ |     69,33 |  61,86 ✗ |         75,16 |     75,08 |
| FL       |         72,47 | 63,74 ✗ |  64,49 ✗ |     72,99 |         76,69 |     76,54 |

*(✗ = abaixo do piso. Pisos citados de `markov_1step_region_acc10_mean`, `06_results.tex:303`; as margens
`+4,07 a +10,02` são **derivadas**, e o próprio arquivo declara isso.)*

> 🎯 **HMT-GRN fica abaixo do piso nos SEIS. STAN em quatro. ReHDM em três.**
> **É esse o pontapé, e é honesto:** modelos profundos publicados não superam uma tabela de transição
> de primeira ordem nesta tarefa. **Isso diz algo sobre o estado da literatura de região que ninguém
> tinha dito** — e é muito mais forte do que "nosso modelo é melhor que os deles".

#### (a) "superamos a literatura" — verdadeiro, com a redação certa

✅ O modelo conjunto supera o **melhor externo de cada dataset** nos seis, por **+3,55 a +6,04**
(mínimo em FL contra STAN; máximo em AZ contra ReHDM). O dedicado também, nos seis.

> 🛑 **Mas nunca escrever "we beat the literature".** A redação obrigatória é
> **"above every external system we ran"**, e a razão é dupla:
> 1. **só o HMT-GRN é comparação pareada** — mesmos dados, mesmas dobras, mesmas inicializações. O
>    STAN tem **saída adaptada** para região, representações e sequências próprias, e **dobras
     > parciais** (TX 4/5, CA 2/5, semente 0). O ReHDM roda **no protocolo publicado dele**, nem nas
>    nossas janelas nem nas nossas dobras — e com **semente única** em CA e TX;
> 2. **a "literatura de next-region" nesta formulação não existe** (ver (b)). Dizer que se supera algo
>    que não existe superafirma duas vezes.

#### (b) "definimos métricas para o next-region" — NÃO se sustenta

Os três componentes são empréstimos padrão: **Acc@10** é a métrica canônica de next-POI (HMT-GRN, ReHDM, MCMG, e o
survey de Luca et al.); o **piso de Markov de 1ª ordem** é baseline canônico desde Cuttone et al. (2016) e
*normativamente recomendado*; o **desconto de OOD** não existe com esse nome, mas o **N²/Next-New do HMT-GRN** cobre a
mesma intenção.

**E a tarefa também não é nova:** predizer a próxima região existe como alvo auxiliar (HMT-GRN, MCMG)
e, no **DRRGNN** (TKDD 2022), **como alvo final já em multitarefa com categoria de POI** — o análogo mais próximo desta
dissertação. ⚠ **Se a defesa disser "tarefa nova" ou "métricas nossas" sem citar DRRGNN, HMT-GRN e o piso de Markov
canônico, a crítica é imediata e barata de fazer.**

> ✅ **A versão fraca e verdadeira, que preserva o que o autor quer dizer:**
>
> *"**No evaluation protocol existed for next-region over a fixed administrative partition. We fix
> one:** standard Acc@10, **out-of-vocabulary regions counted as errors** (the common practice filters
> them out), and a **first-order Markov floor as a mandatory reference** — a floor that the deep
> baselines themselves fail to clear."*
>
> O que **é** defensável como novidade de formulação: *(partição administrativa fixa, dada
> exogenamente)* × *(escala de bairro)* × *(alta cardinalidade, 520–8.501 classes)* × *(alvo final,
> não instrumento para o POI)*. A literatura usa grade/geohash (arbitrária, geométrica) ou clusters
> descobertos (data-dependent — no MCMG, **nove** classes).

#### 🛑 O HMT-GRN tem de FICAR na tabela — contra a instrução da AUT-6

O autor pediu *next-region: ReHDM · STAN · Dedicated · Joint*, omitindo o HMT-GRN. **Três razões para mantê-lo:**

1. é **a única baseline region-native e pareada** (`05_setup.tex:180`: *"The primary next-region comparison is HMT-GRN…
   same data, folds, and random initializations… predicts region as one of its original targets"*), e a nota da Tabela
   10 o chama de **primary external comparison**;
2. **omiti-lo esconde o caso 6/6 abaixo do piso** — que é justamente o achado forte;
3. sem ele, a tabela mostra só sistemas cuja comparação **não é pareada**, e a banca pergunta por quê.

> **Proposta: as quatro colunas de região viram HMT-GRN · ReHDM · STAN · Dedicated · Joint, com o
> HMT-GRN marcado como o pareado**, e a adaptação dos outros dois no slide extra que o autor propôs.

#### Layout, medido

**O problema não é a fonte, são as 15 linhas empilhadas num canvas de 9 cm** (a versão empilhada a
`\footnotesize` dá **overfull de 21,8 pt**). **Duas tabelas lado a lado dentro de `columns`, uma por tarefa, 6 linhas
cada:** `\footnotesize` + `\arraystretch{1.3}` + `\tabcolsep 5pt` → **0 overfull**, com ~35% da altura livre. Um passo
de fonte acima do atual e 2,2× o espaçamento.

**Convenção (G4):** negrito no melhor, sublinhado no segundo. ⚠ **há empates** (AZ 34,57 e CA 35,63 em categoria) — hoje
os dois vão em negrito; manter **e dizer na nota**.

#### Redação sugerida

**Título:** *Next-region: above every external reference, on a task with no fixed protocol*

**Corpo (três linhas):**

- Joint beats the strongest external system on **all six datasets** (+3.55 to +6.04 Acc@10);
- exceeds the **first-order Markov floor by +4.1 to +10.0** everywhere — while **HMT-GRN, the only matched-protocol
  region-native baseline, stays below that floor on 6 of 6**;
- **no established protocol exists** for next-region over an administrative partition. **We fix one:**
  Acc@10, unseen regions counted as errors (not filtered), Markov floor as mandatory reference.

**Rodapé (uma linha, corpo pequeno):** *HMT-GRN: same data, folds and initializations (primary comparison). †STAN: our
re-implementation, own representations, output adapted to regions; TX 4/5, CA 2/5 folds, seed 0. ‡ReHDM: reference under
its own published protocol; single seed on CA/TX. Protocol components are standard instruments; the contribution is
fixing the protocol, not new metrics.*

⚠ **Na fala, nunca: "we defined the metrics" nem "we beat the literature".**

### 6.6 · Tabela comparativa dos dados dos Caps. 3 e 4 — **slide de reserva** 🆕

Check-ins, usuários, POIs e demais estatísticas dos corpora dos Caps. 3 e 4, para responder se a banca perguntar sobre a
diferença de ETL. **Não** entra na apresentação principal. ⚠ **Verificar antes de criar:** o `B4-4` (*"Os números do
corpus de Florida mudam entre capítulos. 990.518 no Cap. 3 e 1.407.034 no Cap. 5"*) já existe na Série B e pode cobrir
isto — talvez seja caso de **estender o B4-4**, não de criar slide novo.

---

## 7 · Série B — os extras

> Fonte: [`archive/extra_RAW_2026-08-26.md`](extra.md).

### 7.1 · O estado real: dois pedidos do `extra.md` já estão atendidos

A Série B **já é** o índice **B0** (com `\hyperlink` em cada entrada e `\beamerreturnbutton` de volta em cada slide) +
**48 slides em sete famílias temáticas**: B1 veredito e estatística (6) · B2 protocolo e vazamento (5) · B3
pós-submissão (8) · B4 Caps. 3 e 4 (7) · B5 não foi medido (10) · B6 documento e escopo (6) · B7 como o Check2HGI e o
modelo conjunto funcionam (6).

> **Logo, *"criar um índice"* e *"organizar por tema"* estão FEITOS.** As categorias que o `extra.md`
> sugere (Data, Architecture, Evaluation, Results, Limitations, Methodological Details) mapeiam quase
> 1:1 nas existentes.

### 7.2 · O que continua valendo

| ID      | Pedido                                                                                                                                             | Status                                                                                                                                                                                                                                                                                                                                                                                              |
|---------|----------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **E1**  | Remover o primeiro slide dos extras se ele existir só para introduzir a seção                                                                      | ⚖️ **O B0 é o índice, não um introdutor.** Se removido, perdem-se os links de navegação. **Recomendo manter**                                                                                                                                                                                                                                                                                       |
| **E2**  | Criar um **divisor visual "Extras"**, com fundo colorido, no estilo do de Acknowledgements                                                         | ✅ 🔎 P3.2                                                                                                                                                                                                                                                                                                                                                                                          |
| **E3**  | **Trocar títulos-pergunta por títulos-conclusão**                                                                                                  | ✅ **É a mudança de maior valor da §7.** Hoje o título é a pergunta e o `framesubtitle` é a resposta. **Inverter:** título = a conclusão; subtítulo = a pergunta que ela responde. Já existe precedente no deck (`B6-5 — sim, e a resposta é diferente nos dois eixos`). ⚠ **custo:** são 48 slides e **mexe no B0**, que lista as perguntas como texto dos botões. Fazer os dois na mesma passada |
| **E4**  | Reduzir muito o texto; extras são apoio rápido, não apêndice escrito                                                                               | ✅ G8                                                                                                                                                                                                                                                                                                                                                                                               |
| **E5**  | Priorizar tabelas, gráficos, diagramas, números-chave e frases curtas                                                                              | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E6**  | Dados podem ser mais detalhados que na principal, desde que visualmente organizados                                                                | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E7**  | Converter os extras muito textuais em estrutura de slide                                                                                           | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E8**  | Revisar **todos** os extras individualmente contra a versão atual da defesa                                                                        | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E9**  | **Fundir** extras que respondem a perguntas próximas                                                                                               | ✅ **Duas duplicatas literais, confirmadas pelas duas sessões:** (1) *"A vantagem de região sobrevive a um controle de capacidade pareada?"* aparece **duas vezes** — `B-P1` (família B3) e `U2` (família B5); (2) *"a dependência entre as duas entradas do modelo conjunto"* aparece **duas vezes** — `Q5` e `U3` ⚠ *(o `U5` NÃO entra: ele pergunta quão longe cai a região predita quando o modelo erra — outra pergunta, outra evidência. Fundi-lo apagaria uma resposta.)*. Fundir cada par                                                           |
| **E14** | Dois slides B novos, criados em 25/08                                                                                                              | ℹ️ `B6-5` (*"Vocês chegam a superar os modelos da literatura?"*) e `B6-6` (*"Como cada baseline externo rodou"*), já ligados a partir do B0. **São a fonte do X5** e não devem ser cortados                                                                                                                                                                                                          |
| **E10** | **Reduzir o total** — hoje são muitos e há risco de não achar o slide certo na hora                                                                | ⚖️👤                                                                                                                                                                                                                                                                                                                                                                                                |
| **E11** | Remover redundâncias entre extras e com a principal                                                                                                | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E12** | Remover extras obsoletos                                                                                                                           | ✅                                                                                                                                                                                                                                                                                                                                                                                                  |
| **E13** | Critério para manter: só o que é **difícil de reproduzir verbalmente** (tabela, comparação quantitativa, fórmula, detalhe arquitetural, evidência) | ✅ **Adotar como regra de corte**                                                                                                                                                                                                                                                                                                                                                                   |

### 7.3 · Duas restrições que o corte tem de respeitar

- **§8.8** — todo slide pós-submissão carrega o rodapé *"pós-submissão — não consta em nenhum dos dois volumes"*. Isso
  atinge a família **B3** inteira;
- alguns extras são **destino** de cláusulas que saíram da tela principal (o `HANDOFF.md` §4c cita o **S47**, cujos
  itens foram para `B1-1`, `S3` e `S50`). **Antes de apagar um extra, verificar se ele é destino de algo.** Apagá-lo
  reabre o buraco na principal.

---

## 8 · Perguntas ao autor

As que eu **não** consigo fechar sozinho, em ordem de impacto.

### 8.1 · Fechadas em 2026-08-26

`Q1` (S6 → **sai**, AUT-2) · `Q4` (travessão → **por função**, AUT-4) · `Q7` e `Q8` (S3 → **perde os resultados**,
AUT-3) · `Q12` (**`ppt` implementa**, `presentation` desligada) · `Q16` (**os dois carimbos saem, §8.5 revogada**,
AUT-5) · `Q2` e `Q5` (**S18 e S28 saem**, AUT-7, com as verificações da N3) · `Q11` (**o autor escreve o fluxo do HGI**,
AUT-8) · `Q19` (**a mensagem entra, com o formato da AUT-6** — as ressalvas obrigatórias estão na N2).

### 8.2 · ~~Em aberto~~ → **TODAS FECHADAS** (verificado 26/08, 23h)

> 🔴 **Esta tabela estava STALE e induzia a erro.** Ela lista `Q6`, `Q10`, `Q13`, `Q14`, `Q15`, `Q17` e
> `Q18` como abertas — **o autor respondeu as sete logo abaixo, em texto corrido**, e as respostas
> viraram `AUT-10` a `AUT-16`. **Nenhuma pergunta do §8 continua aberta.** A tabela fica como registro
> do que foi perguntado; o estado é este:
>
> | Q | fechada por | o que ficou |
> |---|---|---|
> | `Q3` | `AUT-10` | os dois carimbos saem de todo lugar; a convenção métrica vira prosa |
> | `Q6` | `AUT-11` | o item do par de tarefas sai. ⚠ **e é daqui que nasce a colisão “cinco × seis limitações”** com o volume entregue — ver §14.1e |
> | `Q9` | sem contestação | ordem `AL → AZ → Istanbul → FL → CA → TX` nas tabelas de resultado; o *evidence base* mantém a ordem por regiões. **Aplicada no deck** |
> | `Q10` · `Q17` | `AUT-16` | os extras não são escopo da `gate`. ⚠ **consequência não resolvida:** os 48 slides B continuam **fora do `SPEECH.pdf`** |
> | `Q13` | `AUT-12` | slide 10 sai; item 4 vira *Contrastive infomax*. Deck de 50 → 49 |
> | `Q14` | `AUT-13` | a linha de `Controls` sai. **A verificação inverteu o meu parecer**: os números eram pré-vazamento |
> | `Q15` | `AUT-15` | a gradação fica, e a lista dele entra — auditada na §13 |
> | `Q18` | `AUT-14` | `stream`/`tower`, `Markov-K floor` e `contrastive` autorizados no `GLOSSARY` |
>
> **A lição, e ela é a mesma do §14.1:** o autor respondeu **em prosa, abaixo da tabela**, e a tabela
> nunca foi atualizada. **Um registro de estado que não é atualizado junto com a resposta vira uma
> fila de trabalho falsa** — nos dois sentidos, porque o §14.3 dizia o contrário e listava como
> pendente o que já estava feito.


| #       | Pergunta                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Onde     |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| **Q6**  | O item 6 do **S52** (*task-pair confound*) sai? É a limitação que a banca externa tem mais chance de levantar                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | K30      |
| **Q9**  | ✅ **respondida, e não é preferência — é o que o documento faz.** As **duas tabelas de resultado do Cap. 5** usam **AL → AZ → Istanbul → FL → CA → TX** (contagem de check-ins crescente: 113.846 · 236.450 · 462.615 · 1.407.034 · 3.171.380 · 4.089.892), e a **tabela de datasets** usa outra ordem, por nº de regiões, **que é a que o S12 do deck reproduz**. ⚠ Note que **CA vem antes de TX** na ordem de resultados (CA tem mais regiões, TX tem mais check-ins). **Recomendação: toda tabela de RESULTADO do deck (S44, S45, S46) usa a ordem de resultados; o S12 mantém a ordem por regiões, que é a da tabela que ele reproduz.** Confirmar só se você discordar | C55      |
| **Q10** | Quantos extras você quer no fim? (hoje 48)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | E10      |
| **Q13** | O `Delaunay` e a distinção `infomax × estimador contrastivo` **já foram implementados em 25/08**. Era isso que você queria, ou quer mais?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | F11, F12 |
| **Q14** | O **S44** perde a linha de `Controls` (`C42`). Ela contém o controle de concatenação, que o estudo Q13 mostra ser **mais forte do que o capítulo afirma** (risco R-β). Remover mesmo assim?                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | C42, R-β |
| **Q15** | No **S50**, as três condições entram **em pé de igualdade** ou com a gradação do Cap. 6 (representação = estabelecida; arquitetura e escala = sugeridas)? A segunda é a segura                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | K18, R-γ |
| **Q17** | Os 48 slides da Série B **nunca chegam ao `SPEECH.pdf`** (o prefixo `SB<n>` não casa o regex do extrator). Deliberado, ou você espera ter a fala impressa ao pular para um slide B na arguição? É uma linha de regex                                                                                                                                                                                                                                                                                                                                                                                                                                                          | 4F       |
| **Q18** | Três correções de vocabulário precisam de termo novo no `GLOSSARY` (`stream`/`tower`, `Markov-K floor`, e `contrastive` se você quiser a palavra na tela). Você autorizou **dois** termos em 25/08 e disse que era isso. **Autoriza mais?**                                                                                                                                                                                                                                                                                                                                                                                                                                   | 4D, F11  |

Eu coloquei a descriçõa do hgi no documento consideration, vc pode mover ele, só alinha isso com o agent tikz que já
deve etar trabalahando sobre ele.

Q3 - Sobre o metric stamp podemos remover de todos os locais, eu já vou falar isso em prosa ao apresentar os resultados
dos cap. 3 e 4. Quanto ao Task stamp, podemos remover do s14 é deixar essa informação para o S6. 
Q6 - Só para esclarecer
a questão do item 6, é referente ao fato de termos mudado de tarefa entre o chap 4 e 5, certo ? Se for eu endorso mais
uma vez que podemos remover, já esclarecemos isso durante o texto o porque teve esse mudança e se por ventura alguém
perguntar podemos reposnder em prosa
Q10 - Não é trabalho de voce tocar em nada extras isso será trabalho de outro agent. 
Q13 - Não, podemos revmover o atual slide 10: "The idea these three share". E no slide 9, onde há o iten 4: "graph infomax", trocar ele pode "Contrastive
infomax -- An approach to create representation using two pars one positve and other corrupted, so we don't need lables
to train."
Q14 - Pode remover a linha, se não me engano tinha alguns problemas com esse teste principalmete por ele ter sido feito pre-leak
Q15 - Concordo podemos faazer essa mudança, é ainda sugiro mais. No arquivo
articles/dissertacao/wrapup/Questions_author.md:98, voce vai minha lista de sugestões que eu iria te passar apra essa
tela para vc muda nela, acho que vc já peode pegar essa lisata junto com essa alteração sugerida e fazer as mudanças
nesses slides, pf averigue minhas sugestões contra os textos e documentações
Q17 - Não mexer nos lsides extra, outro agent ira fazer isso.
Q18 - Sim Outros: Eu vi que diversas mudanças que eu pedi ainda não foram feitas: Mudanças dos titulos, o slide 41 e
varias outras, esses foram só alguns exemplos.





### Descrição HGI — escrita pelo autor

> 🛑 **O desenho do autor foi REFLOWADO neste arquivo** — um formatador de markdown colapsou as
> quebras de linha do diagrama ASCII numa linha só, e ele ficou ilegível.
> **A versão íntegra vive em [`hgi_draw.txt`](hgi_draw.txt)**, que é `.txt` exatamente para isso não
> voltar a acontecer. **É esse o arquivo canônico; a cópia abaixo é referência.**

```text
POI Categories
      |
[Pretrained Category Encoder]
      |
POI Category Embeddings
      |  Delaunay
POI Graph
    /        \
  Xp          X~p
original    shuffled
    \        /
[same POI GCN]
      |
POI Embeddings  {orig., corr.}
      |  MHA
Region Raw Embeddings  {orig., corr.}
      |  Geographic Adjacency
Region Graph
      |
[same Region GCN]
      |
Region Embeddings  {orig., corr.}
      |  original only
      v
Area-weighted aggregation
      |
City Embedding
```

Junto com o grafo acima, temos que puxar dos nós:

```text
POI Embedd Pos & Negativo <-> REGION      REGION Embedd Pos & Negativo <-> CITY

     (p_i, r_k)   +                            (r_k, city)    +
     (p_j, r_k)   -                            (r~_k, city)   -
          |                                         |
        D_pr                                      D_rc
          |                                         |
        L_pr                                      L_rc
           \                                      /
            +------------  Total Loss  ----------+
                              |
                       Backpropagation
                              |
                POI GCN  +  MHA  +  Region GCN
```

**As notas de precisão** (duas fronteiras e não três · discriminadores bilineares, ao contrário do
DGI · o negativo da fronteira POI–região é **um POI diferente na mesma região** · a GCN de região que
a prosa do Cap. 2 omite · só o ramo original sobe para a cidade) **estão no
[`hgi_draw.txt`](hgi_draw.txt)**, junto com a restrição de continuidade com o Check2HGI e o orçamento
do slide.

---

## 9 · Especificação de conteúdo — Seções 1 e 2

> **Formato:** blocos prontos para transplante no `SLIDES.md`. **Numeração = o deck ALVO** (§🗺).
> Só os slides que **mudam** estão aqui; os demais seguem como estão.
> **Fase A da `ppt`** (remoções e o movimento do 37) é livre de conteúdo e roda antes. **Isto é a
> Fase B.**

### Uma de-duplicação que a fusão resolve, e que vale registrar

Ao montar o slide de tarefas, três conteúdos que hoje vivem em lugares diferentes convergem:

1. **a hipótese do Cap. 3** (*"that difference limits what one shared trunk can do for both"*, hoje no S15) **já existe
   no slide 19←22**, como o **suspeito 1**: *"Task dissimilarity — a static task and a sequential task may force the
   shared trunk into a compromise representation."* **É a mesma frase com outras palavras.** → **sai da fusão**, e o
   slide de tarefas fica mais leve;
2. **"The task pair changes"** hoje vive no bloco *Two traps* do slide 13←14. **Com um slide dedicado às tarefas, o
   lugar natural dele é lá.** → **move para o slide 6**, e isso **fecha o `F24`** sem perder a informação;
3. **a restrição de modelo único** aparece hoje no slide 3 **e** no 4 (`I10`). → **fica só no 3**.

---

### Slide 3 · The question *(era 3 — perde a tabela, `AUT-3`)*

- **Seção/subseção:** 1.3 **Tempo:** 40 s *(era 60 s)*
- **LEDGER:** INTRODUZ a pergunta de pesquisa · INTRODUZ a restrição de modelo único · INTRODUZ a exclusão do próximo
  lugar *(herdada do slide 4, que migra)*
  **⚠ o `INTRODUZ` do veredito migra daqui para o slide 42←46** (N1)
- **Moldura:** `\specialframe` + a pergunta num `block` de título vazio, que sobre o degradê vira **cartão branco com
  texto preto**. *(Diagnóstico: hoje o mesmo `block` fica branco sobre branco e a caixa não existe visualmente.)*
- **Na tela:**
    - *(cartão, `\Large\bfseries`, quebrado por unidade de sentido)*
      **Does multitask learning help point-of-interest prediction — the next category and the next region — and what
      does the answer depend on?**
    - *(abaixo do cartão, branco sobre a metade escura do degradê, `\normalsize` ou maior)*
      The answer is held to one constraint: **one trained artifact, one forward pass, both outputs.**
    - *(uma linha, menor)* The exact **next place** (Def. 2.9) is **not predicted**, in any chapter.
- **Fala (PT):** "A pergunta da dissertação, literalmente: o aprendizado multitarefa ajuda a predição de pontos de
  interesse, próxima categoria e próxima região, e de que depende a resposta? Ela vem com uma restrição que vale para
  tudo o que vem depois: um artefato treinado tem de produzir as duas saídas numa passagem só. E uma delimitação, para
  ninguém esperar o que não vem: o próximo lugar exato eu não predigo, e nenhum capítulo reporta resultado para ele. A
  resposta eu dou na Seção cinco, com intervalo e com teste, depois de vocês terem visto como ela foi obtida."
- **Proveniência:** pergunta → `chapters/1_introduction.tex:133-134`; restrição → `:325-330`; exclusão → Def. 2.9,
  `chapters/2_fundamentals.tex:313-320` (*"no chapter reports a result for f_place"*).
- **Nunca dizer:** ⚠ **a fala antiga prometia *"a resposta eu dou agora, no minuto três"*. Isso deixou de ser
  verdade** — reescrever, não adaptar. Nenhum número. Nenhum nome de dataset (a exceção do `PLANO §3` deixa de ser
  usada, porque a tabela que a exigia saiu).

---

### Slide 5 · Related work: POI prediction *(era 7 — perde dois itens, ganha a sinonímia)*

- **Seção/subseção:** 2.1 **Tempo:** 40 s
- **LEDGER:** INTRODUZ o trabalho relacionado de predição de POI · INTRODUZ a sinonímia dos nomes da tarefa
- **Na tela:**
    - **Next place** — the literature also calls it **next-POI**, **next-location** or **next-venue**, and they are the
      same task;
    - **it is the dominant target in the field** — recurrent: ST-RNN, DeepMove, HST-LSTM, Flashback; attention: STAN,
      GeoSAN, GETNext;
    - every model named there predicts the **exact establishment**, so **none is a direct baseline** for the targets
      studied here.
- **Fala (PT):** "O chão comum dos dois primeiros estudos. A tarefa dominante da área é o próximo lugar exato, e vale
  dizer que a literatura a chama por quatro nomes: next-POI, next-location, next-place e next-venue. São a mesma tarefa,
  com os mesmos conjuntos e as mesmas métricas. A linha vai dos recorrentes, ST-RNN, DeepMove, HST-LSTM, Flashback, para
  os de atenção, STAN, GeoSAN, GETNext. Todos eles predizem o estabelecimento exato, e por isso nenhum é linha de base
  direta para os alvos que eu estudo."
- **Proveniência:** modelos e a frase de não-baseline → `chapters/2_fundamentals.tex:294-336` (*"Every model named here
  predicts the exact next place, so none of them is a direct baseline"*). **Sinonímia → P1.1**: os próprios títulos da
  bibliografia usam três nomes diferentes (`liu2016strnn` = *"Predicting the Next **Location**"*), e nenhum diz *"next
  place"*.
- **O que SAI:** o item 3 (*"the pair the first two studies attack…"*, `T3`) e o item 4 (*"in mobility, MTL has served
  next place almost entirely…"*, que vai para o **slide 8**, `AUT-9`).
- **Nunca dizer:** ⚠ **não trocar `next place` por `next-POI` como nome principal.** A dissertação **reserva**
  `next place` para o POI exato (Def. 2.9) justamente para que *"Next-POI Prediction"* nos Caps. 3 e 4 possa significar
  **next category**. Usar `next-POI` aqui daria dois sentidos opostos à mesma palavra no mesmo deck. ⚠ E **não** dizer
  *"next place is the dominant task"* sem a sinonímia ao lado: o nome não é o dominante (zero ocorrências no arXiv
  2023–2026, contra 36 de *"next POI recommendation"*), e é o ponto mais atacável do slide.

---

### Slide 6 · The tasks *(NOVO — fusão do 4 com o 15, `AUT-9`)*

- **Seção/subseção:** 2.2 **Tempo:** 45 s *(era 40 + 30 = 70 s; a fusão devolve 25 s)*
- **LEDGER:** INTRODUZ as quatro tarefas (Defs. 2.6, 2.7, 2.8, 2.9) · INTRODUZ a mudança de par entre os capítulos *(
  herdada do bloco `Two traps` do slide 13)*
- **Na tela:** *(uma tabela de quatro linhas, compacta — lê-se de um golpe, e custa menos altura que quatro marcadores)*

  | | **reads** | **predicts** |
    |---|---|---|
  | **Category classification** (2.6) | one place | that place's category |
  | **Next category** (2.7) | a history of **N** visits | the category of the next visit |
  | **Next region** (2.8) | a history of **N** visits | the neighborhood-scale unit of the next visit |
  | **Next place** (2.9) | — | *not predicted in this work* |

    - `alertblock` — **Named to be excluded.** No chapter reports a result for the exact next place.
    - **The pair changes between the studies.** Chapters 3 and 4: **category classification + next category** — one
      static task and one sequential task. Chapter 5: **next category + next region** — two sequential tasks.
- **Fala (PT):** "As tarefas, todas de uma vez, para não voltar a elas depois. Classificação de categoria é estática: lê
  a representação de um lugar e diz o tipo dele. Próxima categoria e próxima região são sequenciais: leem um histórico
  de visitas e dizem, respectivamente, o tipo do próximo lugar e a unidade em escala de bairro onde a próxima visita
  acontece. E o próximo lugar exato está aqui para ser excluído: ele é definido no Capítulo 2 justamente para delimitar
  o escopo, e nenhum capítulo reporta resultado para ele. Uma coisa muda ao longo da dissertação, e é melhor dizer agora
  do que surpreender depois: o par de tarefas. Os dois primeiros estudos juntam a estática com a próxima categoria. O
  terceiro junta duas sequenciais, próxima categoria e próxima região."
- **Proveniência:** Defs. 2.6 a 2.9 → `chapters/2_fundamentals.tex:245-267` e `:313-320`; *"an administrative unit at
  neighborhood scale"* → `:275-276`; a mudança de par → `chapters/5_mobiwac/01_introduction.tex` e o bloco *"The task
  pair changes here"* do slide 28←32.
- **O que NÃO entra, e por quê:** a hipótese do Cap. 3 (*"that difference limits what one shared trunk can do for
  both"*) **sai** — ela já é o **suspeito 1** do slide 19←22, com outras palavras. E a **restrição de modelo único** sai
  daqui (`I10`): fica só no slide 3.
- **`N` em vez de `nove`** (`T6`): a Def. 2.7 do Cap. 2 usa comprimento genérico; **nove é configuração de experimento,
  e ela difere entre capítulos** (Caps. 3/4: nove não sobrepostas; Cap. 5: nove com stride 1).
- **Nunca dizer:** *"prediz o próximo POI"*. ⚠ **Sem particulares do corpus** — nem o número de classes, nem setor
  censitário, nem *mahalle*, nem nome de estado: isso é do slide 11←12.

---

### Slide 7 · The axis that separates this work *(era 8 — o mapa de baselines ganha destaque)*

- **Seção/subseção:** 2.3 **Tempo:** 45 s
- **LEDGER:** INTRODUZ o eixo meio × fim · INTRODUZ o mapa de baselines por tarefa
- **Na tela:** estrutura atual mantida (dois blocos + a frase de escopo), **com o rodapé de baselines reorganizado** —
  hoje é uma linha corrida com quatro grupos separados por barra, e o `F2` pede que se veja **qual baseline é de qual
  tarefa**. Fonte pode continuar pequena; há espaço para quebra de linha.
    - `block` — **Category and region as a MEANS.** Toward the next place: HMT-GRN, CatDM, CSLSL.
    - `exampleblock` — **Category or region as an END.** Activity region (DRRGNN), next category (POI-RGNN).
    - *(itálico)* Among the works reviewed in this dissertation, none treats the next category and the next region as
      **co-equal end targets** of one joint model that does not also predict the next place.
    - *(rodapé, em duas linhas em vez de uma)*
      **next category** — POI-RGNN · Markov over category transitions **next region** — HMT-GRN · STAN · ReHDM ·
      Markov-1 floor **Ch. 3** — HMRM · MHA+PE · **Ch. 4** — MTLnet
- **Fala (PT):** *(a atual, mantida)*
- ⚠ **DE-DUPLICAÇÃO OBRIGATÓRIA:** o **CSLSL** aparece no bloco *"as a MEANS"* deste slide **e** no item de MTL que vai
  para o slide 8. **São a mesma afirmação.** Um dos dois larga o modelo — recomendo que **este slide fique com a lista
  completa** (HMT-GRN, CatDM, CSLSL, porque aqui ela é o eixo) e o slide 8 nomeie só os que não repetem (**MCARNN, iMTL,
  HAMTL, TME**).
- **Nunca dizer:** *"supera"* em relação a nenhum desses nomes aqui. Este slide mapeia, não compara.

---

### Slide 8 · MTL Fundamentals *(era 9 — ganha o item 4 e o balancing method)*

- **Seção/subseção:** 2.4 **Tempo:** 55 s
- **LEDGER:** INTRODUZ hard parameter sharing (Def. 2.10) · INTRODUZ negative transfer (Def. 2.12) · INTRODUZ o trabalho
  relacionado de MTL em mobilidade · INTRODUZ o que é um método de balanceamento
- **Na tela:** *(a `ppt` mediu que este slide tem folga — foi um dos seis que receberam respiro extra)*
    - **Hard parameter sharing** (Def. 2.10) — every task passes through one shared trunk before branching, and
      separates only at its own output;
    - **Negative transfer** (Def. 2.12) — joint training leaves a task **worse than its dedicated single-task model**;
    - **Balancing methods** — they set the weight of each task's loss, or change the update direction, so that one task
      does not dominate;
    - **In mobility, MTL has served the next place almost entirely** — MCARNN, iMTL, HAMTL. TME instead applies
      tree-guided multitask embedding to static semantic POI annotation.
    - `exampleblock` — *"**For this dissertation**, a balancing method is useful only if it improves on a tuned fixed
      weighting."*
- **Fala (PT):** "Três definições e um critério. Compartilhamento rígido é a topologia em que todas as tarefas
  atravessam um mesmo tronco e só se separam na saída de cada uma. Transferência negativa é o desfecho que se teme: o
  treino conjunto deixa uma tarefa pior do que o modelo dedicado dela deixaria. E método de balanceamento é o nome da
  família que tenta evitar isso, ou escolhendo o peso da perda de cada tarefa, ou mudando a direção da atualização, para
  que uma tarefa não domine a outra. Nos dois primeiros estudos eu uso um desses métodos; no terceiro, não. Vale dizer
  também o que a literatura de mobilidade fez com multitarefa: quase tudo a serviço do próximo lugar. O TME é a exceção
  que puxa para o outro lado, com anotação semântica estática. E o critério está declarado no Capítulo 2, escopado como
  está escrito: para esta dissertação, um método de balanceamento só é útil se superar uma ponderação fixa bem ajustada.
  Guardem essa frase; é ela que decide o que eu posso afirmar sobre o balanceador na Seção 3."
- **Proveniência:** Defs. 2.10 e 2.12 → `chapters/2_fundamentals.tex:960-963` e a seção de vocabulário de MTL; MTL em
  mobilidade → `:1399` e seguintes; **o critério → `2_fundamentals.tex:1392`, com o prefixo `For this dissertation` que
  o slide atual havia cortado.**
- ⚠ **A correção mais importante deste slide:** o texto entregue é *"**For this dissertation**, a balancing method is
  useful only if…"*. **Restaurar as três palavras.** Foi o corte delas que transformou um critério escopado numa norma
  universal — a queixa do autor (`F9`). **Não** substituir por uma frase descritiva de literatura: isso trocaria texto
  entregue por paráfrase.
- **De-duplicação:** o item de mobilidade **não repete o CSLSL**, que fica no slide 7 (ver acima).
- **Se faltar caixa, cortar nesta ordem:** (5) o `exampleblock` do critério, que pode ir para a fala → (4) a frase do
  TME → (3) a explicação de balancing method, reduzida a meia linha.
- **Nunca dizer:** ⚠ **nada de formalismo do zoo de balanceadores** — a `§8.16` do PLANO o proíbe explicitamente num
  slide. **E não afirmar que balanceadores não funcionam:** a evidência própria é escopada a **dois datasets, uma
  semente e configurações default** (`1_introduction.tex:449`).

---

### Slide 12 · The metric all three studies share *(era 13 — ganha Markov, perde um item)*

- **Seção/subseção:** 2.7 **Tempo:** 45 s
- **LEDGER:** INTRODUZ macro-F1 · INTRODUZ os dois pontos de referência (piso de classe majoritária e piso de Markov)
- **Na tela:**
    - **macro-F1** — the mean of the per-category F1 scores; every category counts equally, so rare ones matter. Out of
      100;
        - *(subitem, `F16`)* **why** — the class distribution is imbalanced, so plain accuracy hides poor performance on
          rare classes;
        - *(subitem, `F17`)* **what it does not do** — it does not show *which* classes improve, and it can be low while
          overall accuracy is high;
    - **Two reference points, not competitors:**
        - **Majority class** — a predictor that always answers the most common category;
        - **Markov** — a transition table over the training visits: it answers with what most often follows what.
          **First order for region; best order per dataset for category.**
- **Fala (PT):** "A métrica de categoria dos três estudos é a macro-F1: a média das F1 por categoria, com cada categoria
  pesando igual. A razão é a distribuição, que é desbalanceada, e uma acurácia simples esconderia o desempenho nas
  classes menores. Ela também tem um custo, e eu digo qual: a macro-F1 não mostra que classe melhorou, e pode ficar
  baixa mesmo com acurácia alta. E toda métrica que eu disser vem com ponto de referência. São dois, e nenhum deles é
  concorrente: o piso de classe majoritária, que é um preditor que sempre responde a categoria mais comum; e o piso de
  Markov, que é uma tabela de transição montada sobre as visitas de treino, e responde com o que mais costuma vir depois
  do quê. Para região eu uso a primeira ordem; para categoria, a melhor ordem de cada conjunto."
- **Proveniência:** macro-F1 → `chapters/2_fundamentals.tex` §2.4; pisos → `:1689` (*"a majority-class predictor for
  category classification and a first-order Markov model over training visits for sequential transitions"*,
  `gambs2012mmc`); definição operacional do Markov → `chapters/5_mobiwac/05_setup.tex`.
- **O que SAI:** o item *"the loss is not reweighted — unweighted cross-entropy"* (`F18`). ✅ **Liberado por
  verificação:** a cross-entropy é sem pesos nos três capítulos, **e o Cap. 5 testou pesos de classe e eles pioraram as
  duas métricas.** A resposta oral é melhor que o item.
- ⚠ **Markov, três cuidados:** (1) o Cap. 2 **não define** cadeia de Markov, não dá matriz de transição nem ordem K — a
  definição operacional é do **Cap. 5**, e é assim que tem de ser dita; (2) **não fixar uma ordem específica na tela**
  para categoria: o rótulo tem três versões no repositório, e o **impresso** é *"strongest order per dataset"*; (3) a
  única citação de Markov do documento (`gambs2012mmc`) tem como alvo o **next place**, não categoria nem região.
- **Nunca dizer:** que os 93 por cento do slide 1 são teto de qualquer coisa. Que o piso de Markov é fraco — **ele
  supera três sistemas publicados na região**, e isso é assunto do slide 41.

---

### Slide 13 · The protocol of the first two studies *(era 14 — herda o setup do 18)*

- **Seção/subseção:** 2.8 **Tempo:** 50 s
- **LEDGER:** INTRODUZ o protocolo dos Caps. 3 e 4 · INTRODUZ a lei dos verbos · **INTRODUZ o setup dos Caps. 3 e 4** *(
  herdado do slide 18, que sai)*
- **Na tela:**
    - **Ch. 3 and 4** — five-fold cross-validation stratified **over samples**: one user's check-ins may fall on both
      sides;
    - **non-overlapping windows of N visits**; users with fewer than five visits are discarded; **one seed**;
    - full epoch budget, no early stopping; each task read at **its own best validation epoch**;
    - fold means and standard deviations, **no significance tests**;
    - **so these two chapters report differences, never a verdict.**
- **Fala (PT):** "O protocolo dos dois primeiros estudos, e ele é diferente do terceiro. Validação cruzada de cinco
  partições, estratificada por amostra: os check-ins de um mesmo usuário podem cair dos dois lados da divisão. As
  janelas são de N visitas, sem sobreposição, e usuários com menos de cinco visitas ficam de fora. Uma semente só.
  Orçamento cheio de épocas, sem parada antecipada, e cada tarefa lida na época de melhor validação dela. Médias e
  desvios entre as cinco partições, sem teste de significância. Daí sai a lei que eu obedeço a apresentação inteira:
  *supera* fica reservado para teste pareado de superioridade, e os Capítulos 3 e 4 não têm teste. Então eles reportam
  diferenças, nunca veredito."
- **Proveniência:** protocolo → `chapters/3_cbic/method.tex` §3.3 e `chapters/4_courb/methodology.tex`; janelas e filtro
  de cinco visitas → `chapters/3_cbic/method.tex`; a lei dos verbos → `WRITING_LAW.md` §3.
- **O que MUDA, e por quê:**
    - **entra a linha de setup** (janelas, filtro de cinco visitas, uma semente). **Verificado por grep sobre o deck
      inteiro:** o filtro de cinco visitas **não existe em nenhum outro lugar**; *"uma semente"* só aparece no slide
      44←48; a janela não sobreposta só aparece **por negação**, no slide 35←40, 22 slides depois. **Sem esta linha, os
      três somem** (N3);
    - **o bloco `Two traps` deixa de existir.** *"The task pair changes"* migrou para o **slide 6** (as tarefas), que é
      o lugar dele. Sobra a convenção métrica → **é a pergunta `Q3`, e continua aberta**;
    - ⚠ **`T1` pede remover *"The verb law"*.** Está **reescrito**, não removido: virou a última linha, em inglês direto
      (*"so these two chapters report differences, never a verdict"*), que é a frase que o slide 18 carregava. **Remover
      a ideia inteira deixaria o deck sem o que impede os Caps. 3 e 4 de dizerem "supera".**
- **Nunca dizer:** *"supera"* sobre qualquer resultado dos Caps. 3 e 4. Nenhum número do Cap. 5 nesta tela.

---

## 10 · Especificação de conteúdo — Seções 3 e 4

> **Numeração = a do deck de hoje**, que desde a Fase B1 é a numeração alvo. **Identificação por
> título; o número é conferência.**

### 🛑 O orçamento dos slides de diagrama, medido

A `tikz` mediu a figura do DGI em **138,6 × 58,6 mm**. A altura útil do slide é **67,4 mm**.
**Sobram 8,8 mm — duas linhas de `\small`, ou um `block` e nada mais.**

> **Nos slides 15 (DGI), 23 (HGI) e 31 (Check2HGI): a figura + no máximo DUAS linhas.**
> Não cabe figura + legenda + conclusão.

⚠ **E o comprimento do `\frametitle` muda a altura disponível:** título de **uma** linha → 67,4 mm;
título de **duas** linhas, ou com `\framesubtitle` → **63,7 mm**. São 3,7 mm, quase uma linha inteira.
**Num slide de diagrama, um título de duas linhas custa a linha de conclusão** — então ali a escolha
entre título curto e título com subtítulo (`G1`) **não é de hierarquia, é de caixa.**

---

### Slide 14 · MTLnet

- **Muda:** a figura `cbic_mtlnet_arch` **cresce** (`M3`) com a altura que os dois carimbos devolveram (`AUT-5`); revisar travessão **só dentro de frase completa** (`M1`, `AUT-4`).
- **Na tela:** a figura, e os dois itens atuais (FiLM · blocos residuais compartilhados = hard parameter sharing, Def. 2.10).
- **Nunca dizer:** ⚠ com os carimbos fora, **a armadilha de nome vive só no slide 4** (*"Naming trap"*). A fala deste slide tem de dizer *"próxima categoria"*, nunca *"próximo POI"*.

### Slide 15 · DGI: how it works ∣ why it was used → **título curto**

- **🆕 recebe o diagrama do §6.1.** **Orçamento: a figura + duas linhas.**
- **Título:** encurtar para **uma linha** — `DGI` ou `DGI: the contrastive objective`. O `∣ why it was used` custa a linha de conclusão.
- **Na tela, as duas linhas que sobrevivem** *(de oito itens hoje)*:
  1. **Node features, as released** — the mean of the one-hot vectors of a place's graph **neighbors**, with the place's own vector **excluded**: the input describes a neighborhood, **not the place's own label**;
  2. **What it gives** — one 64-dimensional vector **per place**: every visit enters with the same vector.
- **O que SAI, e para onde:** *Delaunay graph* e *infomax objective* **já foram ditos no slide 9** (`M5`) — aqui só se aponta para o diagrama. Os pesos logarítmicos por distância geodésica vão para a **fala**. A redundância `64-dimensional vector per place` × `one vector per place` (`M4`) **desaparece na fusão das duas linhas acima**.
- **Por que essas duas e não outras:** a linha 1 é a **defesa contra vazamento** do Cap. 3 (*"spatial homophily, not recall of the place's own label"*) e a banca pergunta; a linha 2 é **o contraste que o Cap. 5 desfaz** — é dela que sai a frase *"one vector per place"* × *"one vector per visit"*.
- ⚠ **R-θ:** o diagrama segue o **texto entregue** (dois grafos, mesma GNN). O código faz uma passada e permuta as representações. **Resposta oral preparada; o slide não menciona.**

### Slide 16 · Two losses, one set of parameters

- **Muda:** `M17` — tornar explícito que o fenômeno tem nome, **negative transfer**, já definido no slide 8.
- 🛑 **`M18` — NÃO construir a ligação Pareto ↔ negative transfer.** A dissertação **não a afirma**: os dois conceitos vivem em subseções diferentes e **nenhuma frase os liga** (P2.3). O slide já diz a frase certa e ela fica: *"This dissertation claims no Pareto property for its models."*
- **Nunca dizer:** que o modelo é Pareto-ótimo, Pareto-estacionário, ou que evita transferência negativa **por construção**.

### Slide 17 · Nash-MTL, and what the chapter may claim about it → **título mais direto**

- **Muda:** `M20` descrição mais clara · `M22` o bloco *"What Chapter 3 claims"* **perde a moldura** e vira texto · `M23` **remover** *"and Chapter 5 does not rely on it"* (`G5`) · `M25`/`M26` a nota de rodapé do critério **sai** — ele já está no slide 8, **agora com o prefixo `For this dissertation`**.
- ⚠ **`M20`, e é um limite:** *"melhorar a descrição"* é seguro; **acrescentar evidência não é, porque não há.** O Cap. 3 afirma que o Nash-MTL *"consistently yielded a better overall performance"* **sem um único número**, e o *"later finding"* que o enfraquece **nunca é descrito** (R-ζ). A redação atual — *"A conclusion of the time, weakened by a later finding"* — **é a certa. Não fortalecer.**

### Slide 18 · The null result, shown rather than asserted

- **Muda:** `M28` **"Static task" → "Category classification"** ⚠ o termo do glossário é **`category classification`** (Def. 2.6), **não** *"categorical classification"* — a §8.11 é fail-closed · `M29` **remover** *"both of our models score above HMRM in every category"* · `M30`/`G4` **negrito no melhor, sublinhado no segundo, nas DUAS tabelas** (hoje só a da direita tem sublinhado) · `M31` os carimbos **saem** (`AUT-5`) · `M32` a frase *"F1 block only; mean ± standard deviation over the five folds"* **vira nota curta**, deixando claro que **± é o desvio sobre os cinco folds**.
- **A altura devolvida pelos carimbos vai para as tabelas**, que são o conteúdo do slide.
- **Nunca dizer:** *"supera"* sobre qualquer célula. Este capítulo **não tem teste** (slide 13).

### Slide 19 · A null with three suspects

- **Manter** (`M33`). **Uma única correção, e é de vocabulário:** ⚠ **`V5` — *"expert-based routing"* é vocabulário que o deck inventou.** O Cap. 3 nomeia: **"Mixture-of-Experts (MoE) models"** (`3_cbic/conclusion.tex:23`). §8.11 fail-closed.
- ⚠ **`F-05`, e é uma armadilha para quem "melhorar a clareza":** o **suspeito 2** deste slide é a **reinterpretação** que os Caps. 1 e 6 fazem. O Cap. 3 escreveu *"the representation **learned by the shared layers** might have become biased"*; o frame relê como **representação de ENTRADA insuficiente**. **A reinterpretação é deliberada — é a costura que justifica o Cap. 4 inteiro.** Não "corrigir" para a versão do Cap. 3.
- **Este slide carrega agora a hipótese do Cap. 3** que saiu da fusão (suspeito 1, *Task dissimilarity*).

### Slide 20 · *(transição, sem `\frametitle`)*

- **Manter.** §8.12: slide de transição é estrutural e **não pode ser removido**.

---

### Slide 21 · Architecture or representation? *(texto)*

- **Muda:** `A1` o bloco vira só **"The inherited question"**, sem *"suspect 2 against suspect 3"* · `A4` **remover o 5º item** (*"three states: Florida, California, Texas"*) ⚠ **mas `"Protocol as in Chapter 3"` está no mesmo item** — se sair, **confirmar que o protocolo continua dito**; ele está no slide 13 · `A5` o carimbo **sai** (`AUT-5`) · `A2` travessão só em frase completa.
- **`A3` — o 4º item, reescrito.** A frase *"same latent width on both sides: the per-task encoders project any input to 256"* não é compreensível. **O que ela quer dizer** (`methodology.tex:25,257`):

  > **Both models share the same 256-dimensional latent width: each task encoder projects whatever it receives to 256, so the trunk and the heads are identical. What differs is the input: 192 dimensions against 64.**

  Números para a fala: entrada estática **64 → 192** (3×), sequencial **576 → 1728**, latente **256** nos dois.
  ⚠ **A resposta honesta se pressionado:** capacidade pareada **depois** da projeção, **não pareada na** projeção — os encoders de tarefa têm 192×256 contra 64×256 na primeira camada. E o Cap. 4 **pede um controle de dimensão equalizada que nunca foi executado**.

### Slide 22 · Architecture or representation? *(a arte)*

- **Muda:** os dois carimbos **saem** (`A6`, `AUT-5`); a figura `arquitetura_modelo` **ganha a altura**.
- **Sem fala própria** — é a arte da Fig. 2, falada dentro do slide 21.

### Slide 23 · HGI: how it works ∣ why it was used → **título curto**

- **🆕 recebe o diagrama do §6.2** — **bloqueado na `AUT-8`**, esperando a descrição do autor.
- **Orçamento: a figura + duas linhas.** Título de **uma** linha.
- **As duas linhas que sobrevivem** *(de quatro blocos hoje)*:
  1. **A consequence of the design** — the place-level output **already reflects the region the place belongs to**;
  2. **Why it is used here, and the limit** — built for **urban region representation**; its place-level output is **repurposed** here for sequential prediction, **a use the original evaluation does not cover**.
- **Por que essas duas:** a 1 é o que **explica** o resultado do Cap. 4 e a 2 é a **ressalva obrigatória** pela §8.6. O *"how it works"* passa a ser o diagrama, que é o ponto de trocar prosa por figura.
- 🛑 **Duas correções ao mecanismo, antes de o autor escrever o fluxo (R-ι):** o HGI tem **DOIS** objetivos contrastivos, não três — as três fronteiras e a equação `0.4/0.3/0.3` são **do Check2HGI**; e a prosa do Cap. 2 **omite uma GCN de nível de região** entre a atenção POI→região e a soma ponderada pela área (`RegionEncoder.py:35,191-192`).

### Slide 24 · Why these encoders

- **Manter** estrutura, blocos e títulos (`A10`–`A13`). Só revisão de redação e de composição.
- ⚠ **`V2` — *"fine class"* está fora de escopo.** A entrada do `GLOSSARY` restringe o termo a *"Appendix B §B.5 only"*. **Ou parafrasear, ou o autor amplia o escopo** (`Q18`).

### Slide 25 · The diagnostic result is the sequential task

- **🆕 recebe a tabela de Category Classification** (`A17`, §6.3). **A altura vem dos dois carimbos que saem** (`A20`) — foi essa devolução que tornou o item viável.
- 🛑 **DEPENDÊNCIA DURA:** o slide 28 do deck antigo (*The caveat, then the number*) **foi removido** (`AUT-7`). Ele era a ressalva que a §8.6 exige **antes** do número da tarefa estática. **Sem ela, o ganho `+20,2 a +22,0 pp` NÃO pode ser dito** — e a tabela de Category Classification **é** esse resultado.
  > **Portanto: a tabela de Category Classification só entra se vier com a ressalva de vazamento junto**, numa linha: *"the input to this chapter's static task contains the label it predicts — the venue-type feature maps one-to-one onto the seven categories, so this measures a lookup, not learned inference."*
  > **Se o autor não quiser a ressalva na tela, a tabela não entra.** É uma coisa ou outra. **Isto precisa voltar para ele** — ele removeu o slide 28 dizendo *"vou conversar com meu professor"*, e este é o custo concreto.
- **Muda também:** `A18`/`A19` reestruturar os itens de interpretação em **observação → interpretação → conclusão**, com hierarquia visual explícita · `A32`/`G4` a convenção nas **duas** tabelas.

### Slide 26 · What the decomposition moved, and where it did not → **título mais direto**

- **Muda:** `A21` título · `A26` separar visualmente **conclusão** de **limitação** · `A22` decidir a função do slide.
- **`A23` — *"Travel, labeled by task"* tem significado, e ele é bom.** É o **mesmo rótulo com resultado oposto nas duas tarefas**: na **classificação de categoria** Travel move muito (FL 45,49 → **64,89**; CA 38,88 → **63,59**; TX 39,37 → **64,73**); na **próxima categoria** não move (MTLnet mantém **64,47** contra 45,00 em Florida). **Redação:** *"The decomposition helps say what a place **is**. On Travel, it does not help say where the user **goes** next."* **Escrito assim o bloco vale; escrito como está, não comunica.**
- **`A24` manter** *"No universally better spatial encoder"* — SIREN em FL e CA, Sphere2Vec-M em TX. É conclusão do artigo.
- **`A25` manter** *"Not width-matched"* como **limitação**, com a redação do `A3`: **192 dimensões contra 64**, e o capítulo **pede um controle que não foi feito**.

### Slide 27 · *(transição, sem `\frametitle`)*

- **Muda:** `A27`–`A30` — reduzir muito, condensar o achado em **uma linha** e usar o resto como **gancho** para o Cap. 5. ⚠ §8.12: **encolher, não remover**.
- **A linha que fica:** *"With the architecture fixed, the input moved the result: the input representation is the bottleneck."*
- **O gancho:** *"The diagnosis is still at the place level, under a protocol that leaves the same user on both sides of the split. The third study rebuilds three layers: representation · topology · protocol."*

---

## 11 · Especificação de conteúdo — Seções 5 e 6

### Slide 28 · Three changes, each a consequence of the diagnosis

- **Manter a tabela** (`C1`) — funciona como abertura. **Não incluir a mudança de ETL** (`C2`).
- **Muda:** `C3` mais respiro entre linhas e colunas · `C5` reescrever a primeira frase do bloco *"The task pair changes here"*, que hoje é longa · `C6` **remover** *"The restriction holds: one artifact, one forward pass, two answers"* — a restrição já está no slide 3, e agora é o único lugar dela.
- ⚠ **`C4` manter o bloco**, mas note que **a mudança de par já foi anunciada no slide 6** (as tarefas). Aqui ela é **retomada com a razão**, não introduzida. O `LEDGER` tem de refletir isso: **`RETOMA`, não `INTRODUZ`.**

### Slide 29 · Next region: the task, and why it is worth predicting

- **Muda:** `C7` **`Scope` → `Practical applications`**, mantendo o conteúdo (demand and load anticipation, caching ahead of time, capacity planning) e a ressalva *"No such service is built or evaluated here"* · `C9` reescrever *"coarser than a place, not easier"*, que exige interpretação.
- **`C8` — a faixa de regiões está CORRETA, e o problema é outro.** California **tem** o máximo (8.501) e Istanbul o mínimo (520). ⚠ **Mas a frase de origem no Cap. 5 é ambígua** — *"about 3.2 million check-ins and 8,501 regions in California"* — e, lida como faixa, sugere que California é o máximo **nos dois eixos**. **É falso em check-ins: Texas tem 4.089.892 contra 3.171.380.**
  > **Redação segura:** *"classification over the dataset's candidate regions — **520 at Istanbul to 8,501 at California**"*, **sem mencionar volume de check-ins na mesma frase**.

### Slide 30 · Why a per-visit representation is new in this line

- **Manter a estrutura** (`C10`). **Dar mais ênfase visual** ao bloco *"The novelty is the combination"* (`C11`) — é um dos pontos centrais.
- **`C12` — CTLE em três itens vira dois:**
  1. **CTLE** — the closest prior contextual check-in representation: one vector per visit, learned by masking and reconstructing a user's check-in sequence, from **place identifiers and timestamps alone**;
  2. **the difference is the construction** — CTLE is a **sequence model**; Check2HGI stays a **graph model**: same hierarchy, same infomax objective, **one level deeper**.
- ⚠ O terceiro item de hoje (*"the category vocabulary never enters its training"*) **funde-se no item 1** acima, e é ele que sustenta a comparação limpa.

### Slide 31 · Check2HGI: a fourth level below the place

- **🆕 SÓ A FIGURA** (`AUT-18`, §6.4). **Zero marcadores** — os quatro saem. A figura carrega os dois pontos sozinha: **os quatro níveis com o `check-in` marcado como o novo**, e **as duas saídas de 64 dimensões**, com a de região indo para o *next region*.
- **O que sai da tela e vai para a fala:** as arestas, o objetivo infomax e os dois termos auxiliares — mais a reserva `B7-2`/`B7-3`, que já os carrega.
- **Não reexplicar o HGI** (`C16`) — o Check2HGI é **extensão**, e é a figura que tem de mostrar isso.

### Slide 32 · What each visit contributes

- **Muda:** `C17` encurtar título e subtítulo · `C18` reescrever a frase principal em inglês direto.
- **A frase, reescrita:** *"**Edges between consecutive visits run forward in time only.** A target is predicted from a user's past, so the representation is built from the past alone — in training and at readout."*
- ⚠ **`C62`/P2.9 — esta é a MESMA ideia do item 4 do slide 43.** Ela é a **defesa estrutural contra vazamento do rótulo**, e é a correção que define a geração **v18** dos números (em Alabama o vazamento valia **28,63 macro-F1**). **Dito uma vez, aqui, com força — e no slide 43 vira referência, não repetição.**

### Slide 33 · The architecture: sharing by exchange

- **`C25` — a explicação de cross-attention, e ela cabe em duas linhas:**
  > **Two bidirectional cross-attention blocks:** the **category stream queries the region stream**, and the **region stream queries the category stream**. Two blocks · four heads · width 256.
- **`C26` — a frase de compartilhamento está CORRETA, e o problema é de tela.** *"not by owning hidden layers in common"* é literal do Cap. 5, e no código **nenhum stream passa pelos pesos do outro**. Mas o slide diz *"the shared trunk"* três linhas acima, sem reconciliar. **Uma linha resolve:**
  > **One shared module, no shared hidden layers: the streams exchange, they do not merge.**
- **Muda também:** `C24` **remover** *semantic stream* / *spatial stream* onde não forem necessários — dizer **Next Category** e **Next Region** · `C27` a frase inferior **não** ocupa faixa própria abaixo da figura.
- ⚠ **`V3`:** a família `stream`/`tower` **não está no `GLOSSARY`**, embora viva na prosa entregue. **É buraco do registro, não defeito do deck** — mas §8.11 é fail-closed e o registro **não está aberto** (`Q18`).

### Slide 34 · The private spatial path, and what the evidence does not separate → **título mais direto**

- **Muda:** `C28` título · `C29` considerar continuidade com o 33 (*"Architecture: sharing by exchange · Part II"*).
- **Manter intacto** o bloco *"The evidence does not separate the contributions of the shared trunk and the private spatial path. It does not establish that sharing helps, and it does not rule it out."* **É a posição do autor, redigida para se sustentar** — e é o que responde `U1`.

### Slides 35 a 38 · The protocol, in four steps

- ⚠ **São QUATRO blocos no `SLIDES.md`** (`S41`–`S44`), não um. Mas **os quatro frames compartilham `\frametitle`** — identificar por **título + `\framesubtitle`**.
- **35 · 1 the unit of data:** `C31` **remover** o 4º item (*"not the same windows as Chapters 3 and 4"*, `G5`) ⚠ **mas isso deixa a janela dos Caps. 3/4 sem menção** — **resolvido**, porque a linha de setup entrou no slide 13 (N3). `C32` revisar o 5º item.
- **36 · 2 what is measured:** `C33` macro-F1 **não** se redefine (já está no slide 12) · `C35` o item *"Reference points for region"* **encolhe para uma linha**, porque Markov passou a ser explicado no slide 12.
  **`C34` — o `OOD-discounted Acc@10` FICA.** ✅ o nome existe no documento entregue, em `2_fundamentals.tex:1666-1670`. ⚠ **Mas apareceu um risco maior:** o seletor implementado usa `Acc@10` **in-distribution** enquanto a métrica reportada tem o desconto (`06_results.tex:147-149`, comentário oculto). **Nada no texto renderizado diz isso.** → **candidato a slide de reserva.**
- **37 · 3 what is compared:** `C36` reescrever *"Inferential unit"* ⚠ **o termo NÃO existe no Cap. 5** — é invenção do slide, e §8.11 é fail-closed. **Redação segura:** *"The test compares four numbers: one mean per seed."* · `C37` **substituir a explicação da convenção pela fórmula**, que existe e só no Cap. 2:
  > $$S_{\mathrm{joint}} = \sqrt{\mathrm{MacroF1} \times \mathrm{Acc@10}}$$
  💪 **E aqui cabe a frase mais forte do protocolo, que já está meio dita:** a convenção alternativa é **mais favorável ao modelo conjunto** e transformaria **mais quatro células de categoria e mais duas de região** em melhorias Holm-significantes. **O autor escolheu a convenção que produz MENOS vitórias.**
- **38 · 4 how it is decided:** `C38` reescrever *"Declared departure"* — o desvio é **trocar o teste primário**: o plano registrou **Wilcoxon pareado sobre as 20 diferenças por fold**, e a análise primária virou **t pareado sobre as 4 médias por semente**; o Wilcoxon continua reportado **como sensibilidade**. ⚠ **a fala do slide diz que os dois "concordam" — e essa concordância NÃO está afirmada nessa frase do Cap. 5.** Verificar antes de manter.
  `C39`/`C40` a nota de rodapé do refinamento posterior: *"The statistical evaluation protocol was later refined based on the literature."* ⚠ **sem número, e sem sugerir que os vereditos mudaram** — é o estudo `mtlcheck`, que sob outro protocolo **inverte duas células** (R-δ). ⚠ **§8.8:** material pós-submissão em geral só vai na Série B; **esta linha é a exceção que o autor pediu** (`Q-aberta`).

### Slide 39 · The geometry of the vectors → **Result 1**

- **Já movido na Fase A.** Renomear para **`Result 1 — the representation, measured on its own geometry`**, e o 40 vira **`Result 2 — the representation, measured on the task`**. **A distinção é real:** este slide mede a **geometria**, sem tarefa, sem fold, sem semente; o 40 mede o **efeito na tarefa**.
- **Muda:** `C19` o texto explica **só** Silhouette e KNN purity · `C20` **não repetir os valores** — estão na figura · `C21` a nota de rodapé **encolhe drasticamente**, porque hoje comprime a figura.
- ⚠ **A ressalva que NÃO pode sair:** *"These measures characterize the representation family, not the exact configuration evaluated later."* E: *"the same geometry does not separate regions — the benefit is category-only."* **A segunda é a que impede uma leitura errada do slide seguinte.**
- ⚠ **`both averaged over the five U.S. states`** — **Istanbul NÃO entra nessa média.** Pergunta provável de banca.

### Slide 40 · Result 1 → **Result 2**

- **Muda:** `C43` remover a última frase · `C44` remover *"All five folds favor the check-in-level representation at every dataset"* ⚠ **a segunda metade dessa frase é uma ressalva estatística** (*"a paired test separates the two columns at every dataset **except Florida (p = 0.07)**"*) — **se sair da tela, tem de estar na fala** (protocolo §4c).
- 🛑 **`C42` — a linha de `Controls` é a pergunta `Q14`, e ela não é neutra.** Ela contém *"feature concatenation +2.0 / +1.7 / +0.8"*, que é **o controle que o estudo pós-entrega Q13 mostra ser mais forte do que o capítulo afirma** (fecha 111% / 68% / 490% do gap; em Florida **supera** a representação por check-in). **Remover é permitido; esconder, não.** Se sair, a resposta tem de estar na fala e a reserva `B-Q13` tem de continuar viva.

### Slide 41 · Result 2 → **Result 3: one model, two tasks**

- **🆕 tabela refeita — a especificação completa está na §6.5.** É o slide de maior risco do deck.
- ⚠ **Ele está hoje em 0,945 de tinta e a coluna nova exige que algo saia.** O que eu proponho tirar: **o bloco `"Before the reading:"`** (`C47`, quatro linhas) — ele explica a assimetria de busca de hiperparâmetros, que **já está dita no slide 43 como limitação 2** e na fala do slide 38.

### Slide 42 · The verdict, dataset by dataset

- 🛑 **Ficha completa em §4C.** **Não executar o `C56` como escrito** — as duas linhas sob a tabela são **redação de lei** (*"all four are deficits, not ties"* · *"the widest interval reaches 0.34 from zero"* · *"read off the intervals, not established by a further test"*), obrigadas pela §8.6 e pela lei do veredito. **A folga vem da tabela, não do texto.**
- **Muda:** `C55` ordenar os datasets na ordem canônica de resultado — **AL → AZ → Istanbul → FL → CA → TX** (`Q9`) · `C57` aumentar a tabela ⚠ **reinterpretado como "tornar mais legível", não "maior"** — o slide já estoura em 17,9 pt.
- 🛑 **`G4` NÃO se aplica aqui.** É tabela de **veredito**, não de placar: marcar "melhor/segundo" nas quatro células dentro da margem **reintroduz o veredito de vencedor que a lei proíbe**. O destaque certo já existe: o **▲** nas três células que o teste sustenta.
- **Herda o `INTRODUZ` do veredito**, que saiu do slide 3 (N1).

### Slide 43 · The measured trade → **Limitations and trade-offs**

- **Muda:** `C58` título · `C59` travessão só em frase completa · `C60` reescrever os itens para leitura rápida.
- **`C61` — o item 2, reescrito:** *"The epoch is chosen on the same fold the score is read on: **there is no third split**. Absolute scores are optimistic; the joint-against-dedicated comparison much less so, because both sides use the same rule."*
- **`C62` — o item 4 NÃO deve ser removido, deve ser reescrito.** Ele é o grafo **forward-only**, a defesa estrutural contra vazamento (P2.9) — **não uma restrição incômoda**. Como o slide 32 já o diz com força, **aqui vira referência**: *"Each visit reads only its own past (slide 32)."*
- ⚠ **`F-15`:** a tela diz *"4.2 M parameters at Alabama against **1.1 M** for the two dedicated combined"*. **A §8.9 do PLANO proíbe repetir o 1,1 M como verificado**, e proíbe citar a recontagem (1.850.980), que **não tem fonte no repositório**. **Se a pergunta vier, a resposta é que a razão de parâmetros não foi re-medida.**
- ⚠ **A quinta limitação (capacidade) foi RETIRADA por decisão do autor em 2026-08-12.** *"Four declared limits"* está **correto** em relação ao texto entregue. Mas o estudo pós-entrega **P1** mediu que, com capacidade pareada, a vantagem de região **desaparece** (R-α) — e o limite que cobriria isso não está mais declarado. **Existe errata escrita e não aplicada.**

---

## 12 · Especificação de conteúdo — Seção 6

### Slide 44 · The ladder: three studies, three layers

- **Manter a tabela** (`K1`) — funciona muito bem como síntese. **Reduzir a densidade das células** (`K2`): hoje exige leitura demais para um slide de conclusão.
- ⚠ **É o único lugar do deck onde os três capítulos aparecem lado a lado.** A `G5` (escopo por capítulo) **não se aplica aqui** — é justamente a síntese que a `G5` reserva para o fim.

### Slide 45 · The conditional answer

- **Muda:** `K3` acrescentar, depois da primeira frase do bloco *"The answer"*, que **as conclusões não se extrapolam entre os estudos**: *"The conclusions are study-specific; what carries across studies is the methodology and the conditions identified."* · `K4` deixar explícito que a resposta é **condicional** · `K5`/`K6` reorganizar em **três condições** com descrição curta · `K7` sem travessão entre nome e explicação (dois-pontos ou quebra de linha).
- 🛑 **`K5` — a GRADAÇÃO NÃO PODE SUMIR na reorganização** (R-γ). As três condições **não têm o mesmo estatuto probatório**:
  | condição | estatuto, nas palavras do Cap. 6 |
  |---|---|
  | **Input representation** | *established by controlled ablation* |
  | **Architecture** | *suggested, not isolated* |
  | **Scale** | *a possible condition, not an established cause* |
  **Listá-las achatadas como "as três condições que identificamos" é a regressão a evitar.**
- **`K8` — remover *"Identifying these conditions is the main finding of this dissertation"*.** ⚠ **é citação VERBATIM de `6_conclusion.tex:169`**, não editorialização do deck. Três consequências: a remoção é **preferência retórica**, não conformidade com a lei; **a frase TEM de ir para o campo `Fala (PT)`**, porque é a resposta escrita do Cap. 6 à pergunta *"qual é a principal contribuição?"* e **aparece uma única vez no deck**; e ela é a **âncora de proveniência da gradação** — sai do mesmo parágrafo.
- ⚠ **`V1`:** o slide usa `controlled ablation` na **afirmativa** e o Cap. 6 usa a mesma expressão na negativa. **Não é contradição** (o capítulo continua com *"Chapter 4 is the fixed-pair control for the diagnosis"*), mas é risco de arguição. **Correção: nomear o Cap. 4. Cinco palavras.**

### Slide 46 · The contribution → **Contributions**

- **É a ÚNICA cópia agora** (`AUT-2`; a §8.13 foi revogada). ⚠ **A ressalva *"operational, not computational"* TEM de sobreviver aqui** — é a única coisa da regra revogada que vale preservar, e o `K13` pede o mesmo.
- **Estrutura:** manter os dois blocos, **Practical** e **Scientific** (`K11`).
- **Practical:**
  - **Joint model** — operational integration rather than computational reduction *(sem travessão, `K14`; o ganho é o número de modelos a treinar e manter, não o custo de uma passagem)*;
  - **Check2HGI** — a reusable artifact: one vector per visit, **independent of the prediction heads on top** (`K15`, `K16`).
- **Scientific:**
  - **Check2HGI**, aqui pela **novidade metodológica** (`K17`);
  - **as três condições** (`K18`) — ✅ **é a contribuição científica declarada**, e a redação atual saiu de um pedido do próprio autor para fortalecê-la. ⚠ **com a gradação da R-γ**, não achatada.
- 🛑 **`K19`/`K20` — o protocolo estatístico NÃO entra.** Duas verificações fecharam: a dissertação **não o reivindica em lugar nenhum**, e a busca externa achou que **os componentes são padrão** (Acc@10 canônica; TOST e pré-registro anteriores; **ROPE**, Benavoli et al., *JMLR* 2017, é o precedente ML-nativo que derrubaria a reivindicação). **O que É defensável, e vai para a FALA:** *"adotamos um plano de análise pré-especificado com margem registrada e teste de não-inferioridade — prática padrão em ensaios clínicos e recomendada em ML, mas que a literatura de MTL raramente aplica."*
- 🛑 **E o que NÃO pode voltar:** o **resultado negativo do Cap. 3 como contribuição direta**. O autor **recusou explicitamente** esse enquadramento (§4E). O nulo é produtivo porque **fabrica os três suspeitos** — não porque seja contribuição.

### Slides 47 e 48 · Six limitations, six next steps

- **`K21`–`K24` · Data vintage.** ✅ **A busca externa fechou, e o autor estava sendo conservador demais: o corte não é ~2022, é 2018.**
  > **Redação:** *"**Data vintage** — the five Gowalla states span 2009–2010 and Istanbul comes in two separate blocks (**2012–2013** and **2017–2018**). This is a constraint of the field, not of this work: after Gowalla and Brightkite shut down and Foursquare and Twitter closed their research APIs, **no public check-in dataset with user trajectories extends past 2018** — even Massive-STEPS (2025), released precisely to fix data recency, still stops there."*
  ⚠ **Usar os anos do Cap. 6, não os do Cap. 4** — o Cap. 4 (prosa publicada) diz fev/2009–out/2010, que é o que o *paper* `cho2011` afirma; o Cap. 6 diz jan/2009–ago/2011, que é **a extração usada aqui**. A discrepância está declarada em comentário.
- **`K25`/`K26` · Taxonomy coarseness:** reescrever para explicitar que a limitação é de **granularidade e número** — sete classes de topo — e que **outras taxonomias poderiam mudar os resultados**.
- **`K27` · Transductive representation:** manter, dizendo que também é limitação recorrente da literatura.
- **`K28` · No next-place task** e **`K29` · Geographic coverage:** manter.
- ⚠ **`K30` · The task-pair confound — o autor prefere remover, e eu registro parecer contrário.** É a limitação **mais forte** da dissertação e a que a banca externa tem mais chance de levantar: par, representação e topologia **mudaram juntos**, e o Cap. 4 é o controle de par fixo. **Removê-la parece frágil.** É a `Q6`.

### Slide 49 · Closing

- **Simplificar radicalmente** (`K31`). O fecho **não recapitula resultados**.
- **Sai:** os links de GitHub do corpo (`K32`; se ficarem, em nota discreta) · *"The negative result was not an obstacle to the contribution. It was its first half."* (`K33`) e qualquer recontagem da evolução.
- **Fica: UMA frase**, que responde à pergunta central e deixa claro que o benefício é **condicional** (`K34`–`K36`).
  > **Proposta:** *"One model predicts two properties of the next visit in one forward pass — **and whether that helps depends on the input representation, the sharing topology, and the scale of the problem.**"*
- ⚠ **O último slide conceitual encerra, não abre discussão.** A audiência sai dele entendendo **em uma frase** qual é a resposta da dissertação.

### Slide 50 · Acknowledgements → **Obrigado**

- **Título → `Obrigado`**, em português (`K37`); **subtítulo `Acknowledgements`** abaixo, menor (`K38`).
- **Conteúdo:** orientador · instituição · banca · colegas de pesquisa (`K39`). **Simples, limpo, pouco texto** (`K40`).
- ⚠ **A grafia `Pedro Augusto Maia Silva` foi resolvida pelo autor em 24/08** e é a única fonte possível — o nome não aparece em nenhum artigo nem no texto entregue. **Não reescrever de memória.**

---

## 13 · A lista de contribuições do autor, auditada

> Fonte: `wrapup/Questions_author.md:98`. **Cada item confrontado com o texto entregue e com as
> verificações já feitas.** ✅ = pode ir para a tela como está · ⚠ = vai, com a redação ajustada ·
> 🛑 = não vai, e o motivo está no item.

### Científicas

| # | o que ele escreveu | veredito |
|---|---|---|
| 1 | *Superamos a literatura no next-category* | ✅ **sustentado.** O capítulo diz: *"the joint model stands **at least 3.06 points** above the strongest external baseline at every dataset"*, e o **POI-RGNN é nativo da tarefa** e está acima do piso Markov-K nos seis. **É a comparação limpa dos dois eixos.** ⚠ redação: *"above every external system we ran"*, não *"we beat the literature"* |
| 2 | *Publicamos resultados base para a literatura do next-region* | ✅ **e é a formulação certa** — é exatamente a versão honesta que a busca externa recomendou, depois de derrubar *"definimos métricas"*. **Nenhum protocolo existia para next-region sobre partição administrativa fixa; este trabalho fixa um** e publica os números de referência. ⚠ **não** dizer *"definimos métricas"* nem *"a tarefa é nova"* — o **DRRGNN** (TKDD 2022) já prevê região como alvo final em multitarefa com categoria |
| 3 | *Novelty: criamos um modelo de embedding (Check2HGI) agnóstico à tarefa* | ⚠ **vai, com cuidado de redação.** 🛑 **NÃO usar *"trained without task labels"***: essa formulação está **declarada FALSA pelo próprio Cap. 2** (a categoria da visita entra como **feature de entrada do nó**), e ainda está viva no `GLOSSARY` como defeito conhecido. **A forma correta é a que o deck já usa:** *"no next-category and no next-region target enters training"* |
| 4 | *Determinamos 3 condições para que um MTL funcione* | ⚠ **o verbo é forte demais.** O Cap. 6 **estabelece uma** (*established by controlled ablation*) e **sugere duas** (*suggested, not isolated* · *a possible condition, not an established cause*). **Manter a gradação** (R-γ, e é a `AUT-15`). Redação: *"identified"*, não *"determined"* |

### Práticas

| # | o que ele escreveu | veredito |
|---|---|---|
| 1 | *Publicamos o Check2HGI* | ✅ **e é o par prático do científico 3.** O enquadramento que o `K16` pede: **artefato reutilizável, independente das cabeças de predição em cima** |
| 2 | *Modelo unificado para next-category e next-region — ganho operacional e não computacional* | ✅ **e a ressalva `operational, not computational` é obrigatória** — é a única coisa da §8.13 revogada que vale preservar |
| 3 | *Protocolo de avaliação estat[ístic]a dos modelos* | ⚠ **vai como PRÁTICO, nunca como novidade.** A busca externa fechou: os componentes são padrão (Acc@10 canônica; TOST, margem e pré-registro anteriores; **ROPE**, Benavoli et al., *JMLR* 2017, é o precedente ML-nativo). **E a dissertação não o reivindica em lugar nenhum.** ✅ **Pô-lo em `Práticas` é a escolha certa** — como artefato publicado com o código, e não como contribuição metodológica. **Na fala** é onde ele brilha: *"a prática padrão de MTL — p > 0,05, logo empatou — é formalmente inválida; foi por isso que o protocolo existe"* |
| 4 | *Gama de trabalhos futuros* | 🛑 **não é contribuição, é trabalho futuro.** A lista dele (Check2HGI: features nos nós · POI encoder no HGI · hypergraph · GSM++; MTL: remover a camada de embedding, tronco compartilhado com MMoE ou cross-attention; **nova tarefa Next-POI**, cabeça independente ou cascata; unificar Check2HGI com MTL) **é excelente e pertence aos slides 46 e 47**, a coluna *next steps*. ⚠ **`Next-POI` como trabalho futuro já é a limitação 4** (*No next-place task*) |

### 🛑 O que NÃO pode voltar por esta porta

**O resultado negativo do Cap. 3 como contribuição direta.** O autor **recusou explicitamente** esse
enquadramento quando foi proposto (§4E). Nenhum item acima o reintroduz — mas a seção de contribuições
é onde a tentação aparece.

### A tela proposta para o slide de contribuições

**Practical — what it delivers**
- **Joint model** — one artifact for two tasks: **operational integration, not computational reduction**;
- **Check2HGI, published** — one vector per visit, **independent of the prediction heads on top**;
- **An evaluation protocol**, released with the code.

**Scientific — what it establishes**
- **Above every external system we ran, on both tasks** — at least **3.06** macro-F1 over the strongest external on next category;
- **Baseline results for next region**, a task with no fixed evaluation protocol before this work;
- **Check2HGI** — a check-in-level representation trained with **no next-category and no next-region target**;
- **Three conditions** on when multitask learning helps: **input representation** (established by controlled ablation), **architecture** and **scale** (suggested, not isolated).

---

## 14 · Reconciliação com o `considerations.md` ORIGINAL

> **Pedido do autor:** *"se você tiver o histórico original das minhas mudanças, valide o fechamento
> do original e o que ainda está em aberto."*
>
> **Fonte:** [`archive/considerations_RAW_2026-08-26.md`](considerations_RAW_2026-08-26.md),
> 548 linhas · **240 itens** · **49 slides citados** (216 menções) · **19 regras gerais sem número**.
> **Estado do deck:** 105 páginas · **49 slides** · `Overfull` 24 · hyperlinks 49/49 sem órfãos.
> **Auditoria de execução da `ppt` lida do artefato**, não de relatório.

### 14.1 · Placar — FECHADO

| estado | itens |
|---|---:|
| ✅ **NO DECK, verificado no artefato** | **~200** |
| 🖼 **esperando as chapas da `tikz`** | ~~3 slides~~ → **0.** DGI (`:505`) e HGI (`:750`) **integrados**; a `c2h_flow` está **pronta desde 18:05** e só espera a troca de uma linha |
| ⛔ **decidido contra**, com motivo registrado | ~14 |
| 🔄 **resolvido por outra via** | ~18 |
| 🚪 **fora do meu escopo** (extras, `AUT-16`) | ~20 |
| ❓ **aberto** | ~~0 do meu lado~~ → **9, verificados 26/08 23h** — ver §14.1e |

> 🔴 **CORRIGIDO 26/08, e a correção é sobre este placar, não sobre o deck.** As duas linhas riscadas
> acima estavam **falsas**, e uma varredura independente as derrubou lendo o artefato. **Um placar que
> diz "0 aberto" desliga a próxima verificação** — foi assim que dois títulos que o autor cobrou
> nominalmente passaram três rodadas.

### 14.1e · As nove pendências reais, verificadas no artefato (26/08, 23h)

Cada uma conferida por mim no `.tex`, no PDF extraído ou no `main.log` corrente — não em relatório.

| # | o que | onde | classe |
|---|---|---|---|
| 1 | **`fig1_dataflow` no lugar da `c2h_flow`.** A `AUT-18` transferiu quatro conteúdos para a figura; a figura em tela não carrega dois deles (**zero ocorrências de "64"**; nenhuma marca de "nível novo"). A `c2h_flow` traz *"the level this work adds"*, *"64-d per visit…"* e *"64-d per region…"* | `:1070` | **PENDENTE** — uma linha |
| 2 | **Título `Nash-MTL, and what the chapter may claim about it`** — construção esperta, `G1` | `:564` | **PENDENTE** — cobrado nominalmente pelo autor |
| 3 | **Título `What the decomposition moved, and where it did not`** — idem | `:894` | **PENDENTE** — idem |
| 4 | **Travessão de prosa dentro de frase completa** (`FiLM: … a shift --- both tasks read…`). Os outros cinco alvos que o autor nomeou **estão conformes**, conferidos um a um | `:485` | **PENDENTE** (`AUT-4`) |
| 5 | **A pergunta de pesquisa sem moldura de template.** A metade negativa da `I4` foi feita (saiu o bloco branco-no-branco); a positiva não | `:132` | **PENDENTE** |
| 6 | 🔴 **O frame do HGI estoura 4,44 pt** — `Overfull \vbox … detected at line 758`, no build corrente das 20:30. **Regressão de 26/08**, apareceu com a última revisão da chapa | `:758` | **REGRESSÃO** |
| 7 | **`Check2HGI, published`** onde o pedido era **artefato reutilizável**. `reusable` tem **0 ocorrências no deck inteiro** | `:1648` | **PARCIAL** |
| 8 | **A frase de substituição do `T3` nunca entrou.** A remoção foi feita; a frase que a substituiria (esses modelos **não produzem duas saídas**; usam MTL para apoiar a tarefa principal) não existe | `:303` | **PARCIAL — metade executada** |
| 9 | **A ressalva obrigatória da §6.5** (*"the contribution is fixing the protocol, **not new metrics**"*) não está no rodapé, e a tela afirma *"This work fixes one"* sem o freio | `:1432` | **PARCIAL** |

**Mais duas de segunda ordem**, registradas por completude: o **`V1`** entrou em *The conditional answer*
(`:1621`) e **não no slide irmão** *Contributions* (`:1665`); e a **`fig2_model`** continua imprimindo
`semantic stream` / `spatial stream`, os dois termos que a `V3` trocou **no corpo e não na figura**
(`:1118`) — o que interage com o pedido do autor de **ampliar** essa figura.

**A especificação inteira foi despachada em seis lotes e executada**, com as nove exceções acima.

### 14.1b · O deck, medido — antes e depois

| | início (2026-08-26, manhã) | fim |
|---|---:|---:|
| páginas do PDF | 111 | **105** |
| slides impressos | 54 | **49** |
| `Overfull \vbox` | 25 | **22** |
| páginas acima de 0,93 | 18 | **2** |
| sítios de carimbo | 7 | **0** |
| maior `Overfull` da trilha principal | 17,9 pt *(o veredito, conteúdo cortado)* | **6,6 pt** *(sombra de bloco)* |
| páginas com conteúdo perdido | 1 *(o veredito, última linha cortada)* | **0** |
| hyperlinks órfãos | 0 | **0** |

**As 44 páginas de conteúdo da trilha principal foram verificadas uma a uma, pelo número impresso.**
As duas que passam de 0,940 — impressos **18** (0,957) e **23** (0,944) — foram **renderizadas e estão
completas**; o `Overfull` delas é sombra de bloco, não conteúdo.

> ✅ **A lista de "se sobrar tempo" ficou vazia.** O último item — o slide **43**, a tabela da escada,
> que é o único do deck onde os três capítulos aparecem lado a lado — **subiu para `\footnotesize`**,
> alargando as cinco colunas e baixando o `tabcolsep` para 2,5 pt. **0,883, com folga.**
> ⚠ **E a aritmética dizia que não caberia:** o cálculo de largura de célula previa ~16,1 cm contra os
> 14 disponíveis. **Coube.** O LaTeX reparte as quebras entre as colunas de um jeito que a conta não
> prevê. **Medir custou um build; a estimativa teria custado uma conclusão errada** — no slide de
> síntese da dissertação inteira.

### 14.1c · Os quatro defeitos que a verificação pegou e que teriam ido para a banca

1. **a condição `Scale` cortada da página** no slide 44 — a tela diria **duas** condições onde o Cap. 6
   tem três, e a única visível com verbo fraco seria a *architecture*. **É o risco R-γ materializado.**
   Achado porque o `Overfull` subiu de 21 para 23 e a pergunta *"quais duas?"* foi feita;
2. **`and it agrees`** sobre o Wilcoxon, em tela e em fala, **sem fonte no volume entregue** — o Cap. 5
   registra o teste como sensibilidade e **nunca reporta o resultado**;
3. **a linha de `Controls`** com números **pré-correção-de-vazamento**, presa a uma frase (*"under a
   tenth of the gap"*) que é **aritmeticamente falsa** contra a Tabela 9 do próprio volume;
4. **`fine class`** vivo em tela, invisível ao `grep` porque **a fonte quebra a linha entre as duas
   palavras** — achado renderizando.

> **Os quatro têm a mesma forma:** um instrumento passou porque mediu outra coisa. É o caso 6 do
> `HANDOFF` §3, quatro vezes num dia. **Nenhum deles apareceu no log de compilação.**

### 14.1d · Os dois padrões de verificação que ficaram

- **auditoria de termo sobre o PDF extraído, não sobre a fonte.** A fonte mente por quebra de linha e
  por macro; o PDF é o que a banca vê;
- ⚠ **e ela não substitui renderizar.** O PDF extraído só mostra **o que foi desenhado** — conteúdo
  empurrado para fora da caixa **não aparece na extração**. **Extrair pega termo errado; renderizar
  pega conteúdo ausente.** Os dois são necessários.

### 14.2 · O que JÁ ESTÁ NO DECK

**Estrutura — 54 → 49 slides, em três passadas verificadas:**

| pedido do original | estado |
|---|---|
| *"Slide 6 — remover o bloco de contribuição"* | ✅ **o slide inteiro saiu** (`AUT-2`; a §8.13 do PLANO foi revogada) |
| *"Slide 18 — remover da apresentação principal"* | ✅ **saiu** (`AUT-7`), com o protocolo já coberto no slide 12 |
| *"Slide 28 — remover da apresentação principal"* | ✅ **saiu** (`AUT-7`) — valia 2 páginas, tinha overlay |
| *"Slide 37 — mover para perto do Slide 44"* | ✅ **movido**, abre a subseção de resultados |
| *"Slide 15 — mover para Fundamentos"* + *"Slide 4 + 15 — avaliar fusão"* | ✅ **fundidos** no novo **6 · The tasks** (`AUT-9`) |
| *"Slide 11 — avaliar a remoção completa"* | ✅ **removido** (`AUT-12`) |
| *"Slide 7 — separar POI e MTL"* + *"Slide 9 — incorporar o conteúdo de MTL"* | ✅ **a Seção 2 foi reordenada** (`AUT-9`) |
| *"Slide 10 — Contrastive InfoMax"* | ✅ **o item 4 do slide 9 virou a definição dele**, com a redação do próprio autor |
| *"Slide 10 — Delaunay triangulation"* | ✅ **já estava**, entrou em 25/08 com o termo registrado no `GLOSSARY` |
| *"Slide 16/21/24/25/29 — remover as notas de rodapé"* | ✅ **cinco sítios, zero carimbos restantes** (`AUT-5`+`AUT-10`; a §8.5 foi revogada) |
| *"Slide 1 — título Human Mobility"* | ✅ |
| *"Slide 9 — título MTL Fundamentals"* | ✅ |
| *"Slide 47 — título Limitations and Trade-offs"* | ✅ |
| *"Slide 50 — título Contributions"* | ✅ |
| *"Acknowledgements — título Obrigado"* | ✅ |
| *"Nova ordem de resultados: 37 → 44 → 45"* | ✅ **rotulados Result 1 / 2 / 3** |
| *"Slides em geral — títulos diretos"* | 🟡 **12 de 15.** As três que faltam exigem redação nova, **já entregue à `ppt`** |

### 14.3 · ~~O que está ESPECIFICADO e ainda não entrou~~ → **O mapa spec → itens**

> 🔴 **A frase que abria esta seção era FALSA e foi removida em 26/08.** Ela dizia *"a `ppt`
> confirmou, lendo o artefato: **nada abaixo está no deck**"*. Uma varredura independente foi ao
> artefato e a derrubou: **a maior parte está no deck** — a fusão dos slides das tarefas, a ordem da
> Seção 2, os três slides de resultado, a tabela de Category Classification, a fórmula do joint-best,
> *Contributions*, *Five limitations*. **Quem lesse esta tabela como fila de trabalho refaria trabalho
> pronto.**
>
> A tabela abaixo **continua útil e fica**, com outra função: é o **mapa de qual especificação cobre
> quais itens do original**. Para saber o que falta, a fonte é a **§14.1e**, que foi verificada item a
> item no artefato.

| bloco | spec | itens do original cobertos |
|---|---|---|
| Seções 1 e 2 — 7 slides | §9 | `I1`–`I11` · `T1`–`T6` · `F1`–`F25` · `R1`–`R7` |
| Seções 3 e 4 | §10 | `M1`–`M33` · `A1`–`A32` |
| Seções 5 e 6 | §11 · §12 | `C1`–`C64` · `K1`–`K40` |
| **slide 40 · Result 3** | §6.5 | `C45`–`C54` — ⚠ **o autor nomeou este como não-feito** |
| **slide 45 · Contributions** | §13 | `K9`–`K20`, com a lista dele auditada |
| Lote 1 — 4 remoções + 3 títulos | mandado à `ppt` | `AUT-3`, `AUT-11`, `AUT-13`, armadilha de nome, `V5` |

### 14.4 · DECIDIDO CONTRA — e por quem

| pedido do original | veredito | quem decidiu |
|---|---|---|
| *"Slide 13 — remover o quarto item"* (cross-entropy sem pesos) | ✅ **sai**, e com evidência melhor: o Cap. 5 **testou pesos de classe e eles pioraram as duas métricas** | verificação (P2.11) |
| *"Slide 41 — verificar de onde veio OOD discounted accuracy"* | ⛔ **FICA.** O nome existe no documento entregue, `2_fundamentals.tex:1666-1670` | verificação (P2.6) |
| *"Slide 50 — protocolo estatístico como contribuição científica"* | ⛔ **não como científica.** Componentes padrão; **ROPE** (JMLR 2017) derruba a novidade. ✅ **vai como prática**, que foi onde o autor a pôs | verificação (P1.3) + autor |
| *"Slide 19 — revisar a relação entre Pareto dominance e negative transfer"* | ⛔ **não construir a ligação.** A dissertação **não a afirma**; o slide já diz *"claims no Pareto property"* | verificação (P2.3) |
| *"Slide 46 — remover as duas frases de Region e Category"* | ⛔ **não executar como escrito.** São **redação de lei** (*"all four are deficits, not ties"*), obrigadas pela §8.6 | §4C |
| *"Regra geral de tabelas: negrito + sublinhado"* aplicada ao slide do veredito | ⛔ **exceção obrigatória.** É tabela de **veredito**, não de placar: marcar "melhor" nas células dentro da margem **reintroduz o veredito de vencedor que a lei proíbe** | §4C |
| *"Slide 52 — item 6, preferência por remover"* | ✅ **removido** (`AUT-11`). **Meu parecer era contrário e foi superado** | autor |
| *"Slide 44 — remover Controls"* | ✅ **removido** (`AUT-13`). ⚠ **eu tinha marcado como risco de esconder; a verificação inverteu**: os números são pré-vazamento e a frase presa a eles é aritmeticamente falsa contra a Tabela 9 | autor + verificação |
| *"Slide 21 — static task → categorical classification"* | 🟡 **sim, mas `category classification`** — é o termo da Def. 2.6, e a §8.11 é fail-closed | `GLOSSARY` |
| *"Slide 3 — travessão"* e os outros cinco | 🟡 **só o de texto corrido.** O de glosa fica — decisão do próprio autor, reconfirmada | autor (`AUT-4`) |

### 14.5 · RESOLVIDO POR OUTRA VIA

| ele pediu | o que aconteceu |
|---|---|
| *"Slide 3 — datasets: reavaliar a presença dos nomes"* | 🔄 **resolveu-se de graça:** os nomes estavam **só** na tabela do veredito. Saindo ela, a Seção 1 volta a ser genérica |
| *"Slide 3 — consultar um Fable Agent sobre antecipar resultados"* | 🔄 **desnecessário:** o autor decidiu remover a tabela (`AUT-3`) |
| *"Slide 14 — remover 'The metric convention changes'"* × *"o Metric stamp"* | 🔄 **os dois pedidos colidiam.** Resolvido pelo autor: **o carimbo sai de todo lugar e ele diz a convenção em prosa** (`AUT-10`) |
| *"Slide 14 — remover 'The task pair changes'"* | 🔄 **migrou** para o slide 6, onde as tarefas são introduzidas. O bloco `Two traps` **deixou de existir** |
| *"Slide 11 — remover 'The verb law'"* | 🔄 **reescrito, não removido.** Vira a última linha do slide 12: *"so these two chapters report differences, never a verdict"*. **Sem ela e sem o slide 18, nada impediria os Caps. 3 e 4 de dizerem "supera"** |
| *"Slide 45 — deixar evidente que superamos as baselines externas"* | 🔄 **a mensagem melhorou.** A busca derrubou *"definimos métricas"* e devolveu um achado mais forte: **os três sistemas publicados ficam abaixo de um piso de Markov de primeira ordem** — HMT-GRN nos seis, STAN em quatro, ReHDM em três |
| *"Slide 45 — omitir o HMT-GRN"* | ⚠ **parecer contrário registrado:** é a única baseline pareada e region-native, e **é ela que carrega o caso 6/6 abaixo do piso** |
| *"Slide 30 — Travel labeled by task: se não der para formular, remover"* | 🔄 **deu.** Significa que o **mesmo rótulo tem resultado oposto nas duas tarefas** — redação na §10 |
| *"Slide 47 — item 4: se não for relevante, remover"* | 🔄 **é relevante e fica.** É o grafo **forward-only**, a defesa estrutural contra vazamento — a correção que define a geração v18 |
| *"Slide 33 — quantidade de regiões, Texas seria mais representativo"* | 🔄 **a faixa está certa** (CA tem o máximo). **O problema era outro:** a frase de origem sugere que CA é o máximo nos dois eixos, e **é falso em check-ins** |
| *"Slide 51 — datasets recentes raramente passam de 2022"* | 🔄 **você era conservador demais: o corte é 2018**, e o argumento mais forte é que o **Massive-STEPS (2025), feito para resolver a defasagem, também para em 2018** |
| *"Slide 25 — aguardar a descrição do HGI"* | 🔄 **ela existia** no `considerations.md`, destruída por um formatador. Restaurada em [`hgi_draw.txt`](hgi_draw.txt) |

### 14.6 · ✔ RESOLVIDA (AUT-17) — a dependência que a remoção do slide 28 criou

**O original pede a tabela de Category Classification no slide 29** (`A17`). Mas o slide 28 — a ressalva de que **a entrada da tarefa estática contém o rótulo que ela prediz** — **foi removido** (`AUT-7`). A §8.6 exige a ressalva **antes** da manchete, e o ganho `+20,2 a +22,0 pp` **é** essa manchete.

> ✅ **Decidido pelo autor: a tabela ENTRA, com a ressalva em nota de rodapé.** Especificação
> completa em §6.3, com os dados da Tabela 6 e a redação da nota.

### 14.7 · ❓ O último item aberto — e ele encolheu

**O desenho do Check2HGI** (§6.4). A `tikz` está parada esperando o autor dizer como será, e já desenhou o HGI com o andar de baixo previsto, para que a chapa nasça desta sem redesenho.
⚠ **Vale checar se ela já não está escrita em algum lugar** — foi o que aconteceu com o HGI.


### Descrição Check2HGI — escrita pelo autor

        ┌──────────────────────────┐
        │ Preprocessing/Pretraining│
Check-in│                          │
───────►│ Encoder                  │
        └────────────┬─────────────┘
                     ↓
         Check-in Feature Embedding
                     │
          Build directed user
             visit sequence
                     │
             ┌───────┴───────┐
             ↓               ↓
        Original Graph   Corrupted Graph
             │               │
             └───────┬───────┘
                     ↓
                same GCN
                     ↓
          Check-in Embeddings
          {original, corrupted}
                     │
          Attention Pooling
              per POI
                     ↓
              POI Embeddings
                     │
                     ▼
                    HGI


### Preprocessing HGI
                    POI Representation Pre-training                         
POIs ───── Delaunay + Node2Vec + Skip-Gram + Hierarchical Category Loss ────► fclass Embeddings ─── POI Lookup ──► Initial POIEmbeddings ──► HGI

### Preprocessing Check2HGI

                    Check-in Feature Preprocessing

Check-ins ─── Category + Temporal Features + Time Since Previous Check-in ───► Check-in Features/embedding ──► Check2HGI


                                                              
                                                                  