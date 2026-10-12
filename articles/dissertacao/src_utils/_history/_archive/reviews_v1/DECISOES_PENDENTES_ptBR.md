# Decisoes pendentes do autor -- dissertacao v1 (pt-BR)

> Documento de decisoes para o Vitor preencher. Cada item traz o contexto, o que ja foi feito
> nesta rodada, e o campo **DECISAO:** para voce escrever a sua escolha. Onde houver texto de
> reparo pronto, o caminho de aplicacao esta indicado. Nada aqui foi auto-aprovado; voce decide.
>
> Referencias uteis: `src_utils/HANDOFF_v1.md` (mapa completo + ordem), `src_utils/_history/_review_v1/`
> (relatorios das 18 personas), `src_utils/evidence/cbic_recompute_result.md` (numeros do CBIC).
> O PDF de defesa atual e `src/dissertacao.pdf` (87 pp).

---

## TIER 1 -- itens que bloqueiam a versao para a banca

### 1.1 Titulo da dissertacao

**Contexto.** O titulo estava em placeholder em todos os pontos (folha de rosto, cabecalho do Resumo e do Abstract,
metadados do PDF). **Feito nesta rodada.** Setei a **opcao 1** como titulo de trabalho, ativo em todos os pontos:
*"From Representations to a Single Joint Model: Multi-Task Learning for Point-of-Interest Category and Region
Prediction"*. As tres alternativas ficaram como comentario em `src/0_main.tex` (bloco do `\titulo`), para a conversa com
o orientador. **DECISAO (com o orientador):** confirmar a opcao 1, ou trocar por uma das alternativas comentadas (ou uma
nova). Se trocar, e so editar o `\titulo` e os dois cabecalhos-catalogo no `0_main.tex`.
> DECISAO: __________________________________________________


---

## TIER 2 -- conteudo redigido que precisa do seu OK (compila como esta)

### 2.1 Resumo (PT) + Abstract (EN)

Par redigido com paridade de alegacoes a partir dos Cap. 1 e 6 (certificado paralelo pelas personas 03/08). Em
`src/0_main.tex`. **DECISAO:** ler e aprovar/ajustar.
>
> **STATUS (rodada 3):** as ressalvas 1, 3, 4 e 5 abaixo foram **AUDITADAS e APLICADAS** nesta
> rodada, no Resumo E no Abstract como par (marcadas `[NEEDS SIGN-OFF]` no `0_main.tex` para voce
> revisar a redacao). Resumo do que mudou: (1) 1 frase dizendo que o par de tarefas mudou (so o
> MobiWac tem regiao); (3) a margem de nao-inferioridade agora e nomeada como Acc@10; (4) o
> intervalo 5,3-9,4 agora e explicitado como convencao joint-best; (5) "determina se" -> "depende
> de" (o verbo causal duro estava forte demais dado o confundimento da §6.2). Numeros e alegacoes
> inalterados. A ressalva 2 (fluencia/estilo) nao foi aplicada -- deixei para sua leitura.
> **Voce so precisa aprovar/ajustar a redacao.**
> DECISAO: __________________________________________________
> **Ressalvas de conteudo (1/3/4/5 APLICADAS; 2 = estilo, a seu criterio):**
>
> 1. Explicitar que o par de tarefas mudou: CBIC/CoUrb usaram classificacao estatica de categoria + previsao da
>    proxima categoria; somente MobiWac usou previsao da proxima categoria + previsao da proxima regiao. Como esta,
>    a abertura pode sugerir que os tres estudos avaliaram o mesmo par.
> 3. Identificar a margem de nao-inferioridade como dois pontos de Acc@10, tanto no Resumo quanto no Abstract.
> 4. Informar que o intervalo de 5,3--9,4 pontos de macro-F1 usa a convencao `joint-best`: um unico checkpoint por
>    particao, selecionado na validacao, com as duas tarefas avaliadas nesse checkpoint.
> 5. Reavaliar a forca causal de "determina se" / "determines whether", pois representacao, topologia e par de
>    tarefas mudaram juntos e a propria Secao 6.2 registra esse confundimento. Alternativas mais defensaveis seriam
>    "condiciona" ou "a evidencia indica que depende de".
>
> **Fluidez a revisar, sem mudanca de alegacao:** "leem o mesmo historico", "na ordem em que aconteceram",
> `read the same trace`, `in the order they happened` e `at every state tested`.

### 2.2 Apendice C -- declaracao de uso de IA

Uma pagina, a partir do historico git. Ja inclui a linha do desvio de modelo (suite de revisao rodou em Opus 4.8 porque
os tokens do Fable acabaram). **DECISAO:** confirmar o escopo e aprovar.
> DECISAO: Não altere mais nada no apendice C

### 2.3 Apendice A -- contribuicao de tooling/ETL vs contencao do BRACIS  ⚠ PRECISA DA SUA DECISAO

**O que voce pediu.** (i) Achou estranho citar um trabalho nao publicado e absorvido (BRACIS) --
nao ve necessidade; (ii) em vez disso, citar o refinamento do ETL do Gowalla + a codebase/suite de
ferramentas de MTL+POI como contribuicao, com um agente fazendo o scrape e formalizando o argumento
com evidencias solidas.

**FEITO nesta rodada.** Rodei um agente de levantamento (read-only) sobre a codebase. Evidencia
completa (cada numero rastreavel a um comando) em `src_utils/evidence/etl_tooling_contribution_evidence.md`
+ `handoff_tooling.json`. Numeros verificados: **192 modulos / 28.644 linhas** no `src/`; suite de
embeddings separada; camada de testes de tamanho comparavel; ~1.700 commits; **3 familias de
dataset** (Gowalla, Massive-STEPS, Foursquare), **8 engines de embedding** (DGI, HGI, Check2HGI...),
**21 otimizadores/balanceadores de MTL**, **13 backbones de MTL**; ETL do Gowalla que particiona em
**56 datasets estaduais dos EUA** (3 estagios, resumivel); protocolo de CV usuario-disjunta +
significancia padronizando todas as comparacoes. **Reescrevi o Apendice A** (`apx_a_contributions.tex`)
para LIDERAR com essa contribuicao de software (§A.1), sem nenhuma alegacao de desempenho/novidade
(essas ficam nos capitulos de resultado).

**O trade-off que preciso que voce decida (por isso NAO deletei o BRACIS sozinho).** Concordo em
foregroundar o tooling. Mas manter o paragrafo do BRACIS tem uma funcao que a sua pergunta talvez
nao esteja pesando: ele e o **dispositivo de contencao** (AGENT_GUARDRAILS C4, NORTH_STAR §3). A
dissertacao **precisa** revelar que existiu uma iteracao anterior cuja alegacao central (custo de
regiao no MTL) estava **errada** -- justamente para que, se um membro da banca achar a submissao
rejeitada, o documento ja tenha tratado disso honestamente, em vez de parecer que escondeu um
fracasso. Remover o BRACIS por completo pode **ler como ocultacao**. Por isso deixei o Apendice A
com DUAS secoes: §A.1 tooling (novo, o que voce quer em primeiro plano) e §A.2 "An earlier
unpublished iteration" (o BRACIS, curto, so a funcao de contencao -- sem citar numeros do paper
rejeitado).

**Sobre "algum exemplar faz isso?":** dos 3 exemplares do Locus que baixei, nenhum tem um apendice
"outras contribuicoes" diretamente comparavel -- a contencao do BRACIS e especifica desta
dissertacao (voce tem um trabalho rejeitado-e-absorvido no historico; eles nao). Ou seja, nao ha
precedente que obrigue nem que proiba; a decisao e de risco.

**DECISAO:** (a) **manter as duas secoes** (recomendado -- tooling em primeiro plano + contencao
preservada), OU (b) **remover a §A.2 (BRACIS)** e aceitar o risco de contencao (a banca pode achar
a submissao rejeitada sem que o documento a enderece). Se (b), eu removo a §A.2 e ajusto o
NORTH_STAR §3 para registrar a mudanca de politica.
> DECISAO: __________________________________________________

### 2.4 Cap. 5 -- prefacio + recap duplo + figura embquality restaurada

Texto novo-no-capitulo, obrigatorio pelo desenho do coletanea. **DECISAO:** aprovar as insercoes.
> DECISAO: Aprovado!

<!-- [VERIFICADO 2026-07-27] Este item NAO carregava marca de aplicacao (so 3.4 e 3.5 carregam
"✅ APLICADO nesta rodada"). Um relatorio anterior afirmou que 2.4 estava "marcado APLICADO no
proprio arquivo": FALSO, era so a sua aprovacao. Verificado agora contra o `5_mobiwac.tex`: os tres
elementos aprovados EXISTEM no capitulo -- prefacio de reproducao, recap, e a figura
`figures/mobiwac/fig3_embquality.pdf` incluida na linha 447. Portanto o item esta de fato cumprido,
mas por medicao feita nesta data, nao por um registro que existisse no arquivo. -->

### 2.5 Reformulacoes das correcoes de gate -- DEIXAR COMO ESTA (sua decisao)

**Contexto.** Reformulacoes neutras em relacao a alegacao, aplicadas nos gates: escopo dos 93% do Song
(`2_fundamentals.tex`), convencao do 64,51 (`6_conclusion.tex`), de-duplicacao L3 (`1_introduction.tex` +
`2_fundamentals.tex`). Todas com caminho de reversao nos comentarios. **Sua instrucao nesta rodada: deixar como esta.**
Nenhuma acao necessaria; registrado aqui so para constar. (Se um dia quiser reverter, os comentarios `[NEEDS SIGN-OFF]`
no fonte indicam o texto original.)
> DECISAO: mantido como esta (por decisao do autor)

---

## TIER 3 -- correcoes da suite de revisao que precisam da sua chamada

> Reescrito 2026-07-24 (rodada 3) com explicacoes completas, porque a versao anterior estava
> curta demais. Cada item agora diz: **(A) qual e a contradicao/lacuna exata** (com o que cada
> capitulo realmente escreve), **(B) por que importa** (um membro da banca notaria?), e **(C) as
> opcoes concretas**. Detalhe completo nos relatorios em `src_utils/_history/_review_v1/`.
> JA APLICADOS nesta rodada: **3.4** (vintage 2009-2011) e **3.5** (ponte next-POI). Os demais
> aguardam sua decisao.

### 3.1 (MJ-2) Qual teste estatistico foi usado para "supera" -- Wilcoxon ou t pareado?  ⚠ O MAIS IMPORTANTE DA TIER 3

**(A) A contradicao.** Tres textos discordam sobre QUAL teste sustenta as afirmacoes de
superioridade na tarefa de categoria:
- O **protocolo pre-registrado** (`docs/studies/closing_data/v17_completion/STATISTICAL_PROTOCOL.md`
  §2) diz: **Wilcoxon pareado (signed-rank)** sobre os deltas por fold, agrupados multi-seed (n=20).
- O **Cap. 5** (§5.4) reporta: **t pareado** sobre as medias por seed (**n=4** por dataset).
- O **Cap. 2** ainda diz **Wilcoxon**; e um comentario de plano no fonte do paper
  (`05_setup.tex:5`) tambem ainda diz "paired Wilcoxon for beats".

**(B) Por que importa (nao e cosmetico).** Um Wilcoxon com n=4 tem p minimo unilateral de
2^-4 = 0,0625 -- ou seja, **matematicamente nao consegue** dar significancia no pareamento
por-media-de-seed que o Cap. 5 adota. A troca para o t **parametrico** e o que torna a
significancia atingivel em n=4; mas o t em n=4 (df=3) apoia-se numa suposicao de normalidade que
4 pontos nao sustentam bem. Ou seja: a escolha do teste e "load-bearing" (carrega o resultado),
nao um detalhe. **Um examinador de estatistica quase certamente vai perguntar:** "qual teste voce
rodou, e por que o t e nao o Wilcoxon que voce pre-registrou?"

**(C) Opcoes.** (i) Se o numero de record e o t pareado n=4: unificar os tres textos para "t
pareado" (corrigir Cap. 2 e o comentario), e adicionar 1-2 frases justificando o desvio do
pre-registro (por que o t, e reconhecer a limitacao de n=4/normalidade) -- isto e o mais honesto e
defensavel. (ii) Se voce prefere manter o Wilcoxon pre-registrado: entao os numeros de
significancia do Cap. 5 precisam ser recalculados com Wilcoxon n=20 (agrupado por fold), o que e
mais trabalho e pode mudar quais celulas passam. **Recomendo (i)**, mas isto e uma decisao sua de
metodo -- eu nao troco teste nem recalculo significancia sem sua ordem.
> DECISAO: ______________________________

### 3.2 (MJ-3) A validacao cruzada usuario-disjunta vale para o documento todo, ou so o Cap. 5?

**(A) A lacuna.** O Cap. 2 (frame) apresenta a **validacao cruzada com usuarios disjuntos**
(nenhum usuario aparece em treino e teste ao mesmo tempo) como se fosse o protocolo do documento
inteiro. Mas so o **Cap. 5** de fato usa isso. O **Cap. 4 (CoUrb)** usa um split estratificado—
**por amostra** (o `userid` e descartado antes de dividir, entao janelas de um mesmo usuario podem
cair em treino e teste) -- um protocolo **mais fraco**, ja declarado honestamente no prefacio do
Cap. 4. O Cap. 3 (CBIC) usa o protocolo da epoca (5-fold simples).

**(B) Por que importa.** Se o Cap. 2 vende "usuario-disjunto" como padrao e o Cap. 3/4 nao seguem,
um leitor atento ve o frame prometer mais rigor do que dois dos tres estudos entregam. Vazamento
por usuario infla resultados; e importante que o texto seja preciso sobre onde o protocolo forte
foi (e nao foi) aplicado.

**(C) Opcoes.** Escopar a frase do Cap. 2 para dizer que o protocolo usuario-disjunto e o do
estudo final (Cap. 5), enquanto os estudos anteriores usaram protocolos mais fracos da epoca (ja
dito nos prefacios) -- e opcionalmente 1 frase de aviso no Cap. 3. Nao muda nenhum resultado; e
so precisao de escopo. **DECISAO:** aplicar o reescopo? > DECISAO: ______________________________

### 3.3 (MJ-4) Deixar explicito que a regiao foi "pre-registrada" como nao-inferioridade

**(A) O ponto.** O modelo conjunto foi testado para **superioridade** onde se esperava ganho
(categoria; e regiao em 4 datasets) e para **nao-inferioridade** (TOST) onde se esperava so
empatar (regiao em AL/AZ). Essa atribuicao "onde testar o que" foi **fixada antes de ver os
resultados** (num plano de analise, liberado com o codigo). O Cap. 5 ja diz isso, mas de forma
diluida.

**(B) Por que importa.** Fixar a hipotese antes de olhar os dados e o que impede a acusacao de
"voce escolheu o teste que dava certo depois de ver o resultado" (p-hacking). Tornar o
pre-registro explicito e uma **defesa**, nao uma concessao -- fortalece a honestidade do metodo
aos olhos da banca.

**(C) Opcao.** Adicionar/realcar uma frase curta no Cap. 5 (e talvez no Cap. 2) dizendo que a
atribuicao superioridade-vs-nao-inferioridade e a margem foram pre-registradas por eixo, antes dos
resultados. So ganho, sem custo de alegacao. **DECISAO:** aplicar? > DECISAO: ____________________

### 3.4 (MJ-5) Vintage dos dados -- CONFIRMADO 2009-2011  ✅ APLICADO nesta rodada

Os check-ins de Florida vao de **2009 a 2011**. O Cap. 6 dizia "2009 and 2010".
> DECISAO: Aprovado!  -> **FEITO:** Cap. 6 agora diz "between 2009 and 2011".

### 3.5 (MJ-8) Ponte do termo "next-POI"  ✅ APLICADO nesta rodada

> DECISAO: Aprovado  -> **FEITO:** adicionada 1 frase nos prefacios do Cap. 3 e Cap. 4 dizendo
> que "Next-POI Prediction" (termo dos artigos) = a tarefa "next category" do frame, e NAO a
> tarefa de lugar exato ("next place"), que nao e estudada.

### 3.6 (MJ-17) Contradicao sobre a funcao de perda (class-weighting)

**(A) A contradicao.** O **Cap. 2** (§2.4) diz: *"O pipeline de treino combate o desbalanceamento
com entropia cruzada ponderada por classe (class-weighted cross-entropy)."* O **Cap. 5** (§5.4,
Eq. 5.1) diz o oposto: as perdas sao *"entropia cruzada simples, nao-ponderada"*, e mais: que
**testar ponderacao de classe PIOROU** tanto a acuracia de regiao quanto o macro-F1 de categoria.

**(B) Por que importa.** O Cap. 2 (frame) descreve errado a funcao de perda do modelo que carrega
o resultado principal (Cap. 5). O remedio de desbalanceamento real no Cap. 5 e usar **macro-F1
como metrica** (que pesa as classes igualmente no relato), nao ponderar a perda. E uma contradicao
de metodo; nao muda resultado, mas um leitor cuidadoso percebe o frame descrevendo mal o modelo
final.

**(C) Opcao (recomendada).** Corrigir o **Cap. 2** para dizer que o desbalanceamento e tratado
pelo macro-F1 como metrica de relato (e que a ponderacao de classe foi testada e **nao** adotada
por piorar), OU escopar a frase de "class-weighted CE" para o estudo anterior que a usou.
**DECISAO:** corrigir o Cap. 2? > DECISAO: ______________________________

### 3.7 (MJ-18) O nome "MTLnet" e citado como "introduzido no Cap. 3", mas o Cap. 3 nunca usa o nome

**(A) A costura.** "MTLnet" e nomeado como o artefato central do documento -- "o modelo
introduzido no Cap. 3" -- no Abstract, no Resumo, e nos Cap. 1, 2, 4, 5 e 6. Mas o **Cap. 3
nao usa o nome "MTLnet" nenhuma vez** (nem no corpo, nem no prefacio), porque foi mantido fiel ao
paper CBIC publicado, que nao batizou o modelo. (O Cap. 4, em contraste, escreve "MTLNet" com N
maiusculo -- ha tambem uma inconsistencia de capitalizacao MTLnet/MTLNet.)

**(B) Por que importa.** Um membro da banca que for ao Cap. 3 procurar o "MTLnet" que o resto do
documento anuncia **nao o encontra**. E uma costura tipica de coletanea: partes escritas em
momentos diferentes que deixam de apontar uma para a outra.

**(C) Opcoes.** (i) Adicionar o nome "MTLnet" no **prefacio** do Cap. 3 (algo como "o modelo aqui
proposto, que os capitulos seguintes chamam de MTLnet") -- mantendo o corpo do capitulo fiel ao
publicado; e (ii) padronizar a grafia (MTLnet vs MTLNet) em todo o documento. **DECISAO:** aplicar
(i)+(ii)? Qual grafia e a canonica -- "MTLnet" (usada pelo frame/Cap.5) ou "MTLNet" (Cap.4)?
> DECISAO: ______________________________

### 3.8 Visual (persona 18) -- regeneracao de figuras

Tres itens visuais: **Fig. 2** (arquitetura, Cap. 4) tem rotulos **em portugues** num documento de
moldura em ingles (regenerar em EN); **Fig. 3** distingue Food/Shopping **so por cor** (ruim para
impressao P&B / daltonismo -- regenerar com padrao/marcador alem da cor); **Tabela 1** estoura a
margem em ~1cm. Sao regeneracoes de **asset**, nao de texto. **(B)** Importa para uma defesa
impressa e para acessibilidade. **DECISAO:** autoriza eu regenerar os assets? (posso fazer as
figuras que tem script-fonte; a Fig. 2 pode precisar do fonte original do desenho).
> DECISAO: ______________________________

### 3.9 Folha de aprovacao -- modelo real vs placeholder honesto

Os 3 exemplares do Locus mostram uma folha de aprovacao (assinaturas) de verdade; a v1 usa um
placeholder entre colchetes. A arvore do Germano ja traz o modelo em branco
(`pdfs/Modelo-pgs-de-assinaturas.pdf`). **Nota:** o proprio Germano deixou esse `\includepdf`
COMENTADO -- ou seja, ele tambem entregou com placeholder; a folha assinada e inserida na/apos a
defesa. **DECISAO:** (a) incluir o modelo em branco no build de defesa (PDF parece mais
"completo"), OU (b) manter o placeholder honesto atual (recomendado -- e o que o precedente de fato
faz). > DECISAO: ____________________

### 3.10 Movimentos opcionais de excelencia (persona 17, lente SBC-CTD)

Nao sao defeitos -- sao adicoes que elevariam o documento para a lente de premio (SBC-CTD):
(a) uma **tabela contribuicoes -> alegacoes** no §1.6 (liga cada contribuicao ao resultado que a
sustenta); (b) uma **tabela consolidada de resultados** cross-chapter no Cap. 6 (hoje os numeros
estao espalhados pelos capitulos); (c) um **apendice de artefatos/reprodutibilidade** (codigo,
seeds, configs). **DECISAO:** quer algum desses? (cada um e trabalho de frame, sem tocar
resultado). > DECISAO: ______________________________

---

## Itens que NAO precisam de decisao (so para constar)

- Vetado (persona 14): a varredura mecanica de preposicoes "at [dataset]" -- colide com escopos de veredito congelados;
  nao rodar em massa.
- Guarda: se algum relatorio recomenda ADICIONAR uma citacao nova (ex.: arXiv:2311.04698), NAO foi adicionada; verificar
  na fonte antes de incluir (protocolo fail-closed).


---

<!-- estado-rodada -->
> **Rodada encerrada · último toque 2026-07-27 · sem autoridade.**
> Este ficheiro é registo de proveniência do que foi discutido nesta passagem, não fonte
> de um facto corrente. O que ficou decidido está em [`VEREDITOS.md`](../../../../VEREDITOS.md);
> os valores entregues estão em `CLAUDE.md` §0.1. Não copie nada daqui sem confirmar lá.
