# DEFENSE_OPEN_POINTS, Parte II: as perguntas provaveis da banca

> **O que este registro e.** As perguntas que um arguidor competente fara sobre os dois documentos
> enviados, cada uma com a resposta preparada e o numero que a sustenta. Derivado da leitura do
> volume de defesa (119 pp), do volume suplementar (27 pp) e do artigo reproduzido que tambem esta
> submetido (`articles/[mobiwac]/src_fix/`, 10 pp).
>
> **Regra de qualidade aplicada.** Nenhuma resposta entra sem um numero, uma tabela ou uma pagina
> que o autor possa apontar em pe. Onde o numero nao existe, a entrada esta marcada `[VERIFY]` ou
> aparece na secao final, cuja resposta honesta declara um limite.
>
> **Medida usada.** Toda pagina citada como `p. N` e a **pagina impressa** do PDF correspondente
> (`src_fix/build/main.pdf` para o volume de defesa; `src_fix/build/main_extra.pdf` para o
> suplemento). Toda linha citada como `arquivo:N` e a linha do fonte vivo em
> `articles/dissertacao/src_fix/`. A arvore `src/` nao foi consultada para nenhuma entrada.
>
> **Aviso de escopo.** Este registro nao edita nenhum `.tex`. E auditoria e preparacao oral.

---

## Indice: o que fecha como, e onde

| Fecha por | Perguntas |
|---|---|
| **Resposta oral, ja sustentada pelo texto** (FECHADO) | Q1, Q2, Q3, Q4, Q6, Q7, Q9, Q11, Q12, Q13, Q14, Q15, Q16, Q17, Q18 |
| **Resposta oral que declara um limite** (FECHADO, mas a frase precisa ser dita como limite) | Q5, Q8, Q10, Q19, Q20, Q21, Q22, Q23 |
| **So fecha com execucao** (ABERTO) | Q5 (numero da dependencia entre as duas entradas), Q8 (a ablacao do trunk em cinco folds em CA/TX; o controle de capacidade correu a 2026-08-13, ver o bloco), Q10 (segunda cidade fora dos EUA) |
| **Fecha por decisao sua, antes da defesa** | Q13 (divergencia do controle de concatenacao entre os dois documentos), Q14 (limite de capacidade que o artigo carrega e a dissertacao nao), Q15 (o quarto fundamento de integridade descrito na errata e ausente do volume principal) |
| **Errata para o deposito final** | Q13, Q14, Q15, e o item de silhueta registrado em `REVISION_PLAN.md` §15.4 (defeito do lado do artigo, nao da dissertacao) |

Ordem dentro de cada capitulo: as mais duras primeiro.

---

## Grupo A · Capitulo 5 e o artigo submetido (o resultado principal)

### [FECHADO] · Q1 · O senhor escolheu a convencao de checkpoint mais restrita, que remove seis melhorias que o senhor poderia estar reclamando. Por que essa e nao a outra, e quem decide isso depois de ver os resultados?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 80-81 (Cap. 5, paragrafo imediatamente acima da Tabela 10). O texto declara a
convencao e a alternativa no mesmo paragrafo: cada modelo dedicado e lido na melhor epoca da sua
tarefa; o modelo conjunto e lido na epoca escolhida pelo seu escore conjunto de validacao (a media
geometrica das duas metricas), com as duas tarefas lidas do mesmo modelo salvo. A alternativa, ler
cada tarefa na sua propria melhor epoca, e mais favoravel ao modelo conjunto "by at most 0.23
macro-F1 and 0.93 Acc@10 points as the largest gap at any one seed" e "favorable enough to change
the verdicts, turning four further category cells and two further region cells into improvements
that survive the same Holm correction applied here" (p. 80-81). A media sobre as quatro sementes,
registrada em `src_fix/REVISION_PLAN.md:93-94`, e menor: categoria +0.03 a +0.17, regiao +0.19 a
+0.90. Fonte definidora da convencao: `chapters/5_mobiwac/06_results.tex:141-142`.
**RESPOSTA FINAL:** A convencao reportada e a unica que um sistema em producao pode servir, porque
compromete-se com um checkpoint por fold, e a alternativa favoreceria o modelo conjunto em ate 0.23
macro-F1 e 0.93 Acc@10 na pior semente, virando mais seis celulas a meu favor, o que e exatamente
por que eu nao a uso; Cap. 5, p. 80-81.

### [FECHADO] · Q2 · A margem de equivalencia de dois pontos foi registrada apenas para o eixo de regiao. Por que nao para categoria, e o que o senhor usa em categoria no lugar dela?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 76 (Cap. 5, §5.5.3): o plano escrito, fixado durante o desenvolvimento e antes de
qualquer resultado ser lido, atribuiu **teste de superioridade** a next category e **teste de
nao-inferioridade** a next region; "On next category the plan registered no equivalence margin, so
a difference that fails the superiority test is reported as unresolved rather than as a match".
No lugar da margem, o eixo de categoria usa o limite lido dos proprios intervalos: p. 82, "the
widest of them reaches 0.34 points from zero, at Alabama, which bounds all six differences within
half a point of zero at once. The bound is read off the intervals rather than established by a
further test". A legenda da Tabela 10 (p. 81) carrega a assimetria explicitamente: as celulas de
categoria nao levam marca de equivalencia. Fonte: `tables/mobiwac/results.tex:26-30`.
**RESPOSTA FINAL:** O plano registrou superioridade em categoria e nao-inferioridade em regiao, e
por isso as cinco diferencas de categoria que falham a superioridade sao relatadas pelo limite que
os proprios intervalos sustentam, meio ponto, com o extremo em Alabama a 0.34 de zero, nunca como
empate; §5.5.3, p. 76, e p. 82.

### [FECHADO] · Q3 · O braco dedicado recebeu mais busca de hiperparametros que o conjunto. Isso enviesa a comparacao a favor de quem?
**ACAO NECESSARIA:** vazio.
**DADOS:** cobertura por knob em p. 75-76 (Cap. 5, §5.5.2, `chapters/5_mobiwac/05_setup.tex`):
para o modelo dedicado de categoria, batch size buscado nos seis datasets; taxa de aprendizado
buscada em cinco folds em Istanbul, Alabama e Arizona e em folds unicos no Texas, **nao variada em
Florida e California** (quatro dos seis). Para o modelo conjunto, batch size e taxa de aprendizado
do cabeçalho de categoria buscados em Istanbul, Alabama e Arizona em cinco folds e triados em
Florida; Texas e California carregam configuracao transferida. O modelo dedicado de regiao usa uma
configuracao fixa do inicio ao fim, dos dois lados. A leitura de direcao esta em p. 85, segundo
limite: "Where the dedicated search is the wider of the two, the residual favors the dedicated
model, which makes the reported category difference conservative there. At Florida and California,
where the dedicated learning rate was not varied, the two searches are closer in extent and the
reading does not apply". E fechado com "It does not follow that the bias cancels exactly".
**RESPOSTA FINAL:** O vies corre contra o modelo conjunto no eixo de categoria, porque e o braco
dedicado que recebe a busca mais ampla, o que torna a diferenca de categoria que eu reporto
conservadora; em Florida e California, onde a taxa de aprendizado dedicada nao foi variada, as duas
buscas ficam proximas e essa leitura nao se aplica, e no eixo de regiao os dois lados rodam
configuracao fixa, de modo que a mitigacao nao vale ali; p. 85, segundo limite, com a cobertura por
knob em §5.5.2, p. 75-76.

### [FECHADO] · Q4 · Um teste de nao-inferioridade nao e um empate. Nas quatro celulas de regiao dentro da margem, qual e a direcao?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 82: as quatro sao deficits, Alabama (-0.87; -1.00 a -0.75), Arizona (-0.44; -0.62 a
-0.25), Florida (-0.16; -0.19 a -0.13) e Istanbul (-0.08; -0.16 a -0.002), e "every one of the four
intervals lies entirely below zero". Um teste na direcao reversa, aplicado post hoc as mesmas seis
comparacoes de regiao e corrigido entre elas, resolve tres das quatro; o de Istanbul nao e
resolvido, seu intervalo chegando a dois milesimos de zero. O texto fecha: "Each of the four clears
the margin comfortably, which is what the pre-registered analysis asked of them, but none of them is
a tie". Repetido em p. 84, primeiro paragrafo do §5.7: o maior deficit e 0.87 Acc@10 em Alabama, "so
the trade is a measured one and not a free substitution".
**RESPOSTA FINAL:** Todas as quatro sao deficits pequenos, com os quatro intervalos inteiramente
abaixo de zero e o maior deles 0.87 Acc@10 em Alabama, e o texto os reporta como diferencas dentro
da margem, nunca como empates; p. 82 e p. 84.

### [ABERTO] · Q5 · As duas entradas do modelo conjunto vem do mesmo grafo. Elas nao sao independentes. Qual o tamanho dessa dependencia?
**ACAO NECESSARIA:** medir a dependencia entre a tabela de vetores por check-in e a tabela de
vetores de regiao exportadas pelo mesmo grafo, em uma quantidade unica (por exemplo, similaridade
representacional entre as duas janelas na mesma sequencia, ou a informacao que uma janela carrega
sobre a outra em uma sonda linear). Nao existe numero para isso em nenhum dos dois documentos.
**DADOS:** a nao independencia esta declarada, sem numero, no Cap. 2, p. 27: "Both architectures
receive two inputs, and what changes between them is the source: MTLnet derives both from one place
embedding, whereas the joint model reads two tables exported from the same check-in-level
representation. The two tables share an origin by construction, so they are not independent views"
(`chapters/2_fundamentals.tex:813`). O mecanismo de fronteira que existe e a copia com gradiente
interrompido na rota espacial, descrita no Apendice E, p. 112: "The pooled place representation is
detached on this route. As a consequence, the place-region and region-city objectives cannot update
the check-in encoder through the spatial branch" (`chapters/apx_h_check2hgi_joint_model.tex:172`).
Isso limita o fluxo de gradiente **dentro do treinamento da representacao**; nao quantifica a
sobreposicao de informacao entre as duas tabelas exportadas.
**RESPOSTA FINAL:** As duas tabelas partilham origem por construcao e eu digo isso no Cap. 2, p. 27;
a unica fronteira quantificada e arquitetural, a rota espacial recebe a representacao de lugar com
gradiente interrompido, Apendice E, p. 112, e a magnitude da sobreposicao de informacao entre as
duas entradas nao foi medida.

### [FECHADO] · Q6 · Uma dissertacao sobre POI que nao prediz o POI. Por que?
**ACAO NECESSARIA:** vazio.
**DADOS:** o escopo e declarado tres vezes e sempre no mesmo sentido. p. 15 (§1.1): "These tasks
differ from next-place prediction, which identifies the exact establishment and is outside the scope
of this work". p. 22 (Definicao 2.9): "It is named to delimit the scope of the dissertation, and no
chapter reports a result for f_place", seguido do motivo pelo qual os metodos de next place aparecem
no texto: eles fornecem a base metodologica, e "Every model named here predicts the exact next
place, so none of them is a direct baseline for the targets studied in this dissertation". p. 90,
limitacao 4: "No next-place task. The experiments do not predict the exact next POI, and their
conclusions apply only to next category and next region". A justificativa positiva esta em p. 34
(§2.5.1) e em p. 70, que separa tres formas do trabalho relacionado: em MCMG e HMT-GRN "category
and region are auxiliary signals that help a primary next-place task"; na cascata CSLSL a predicao
corre em cadeia com o lugar como saida primaria e a categoria como passo intermediario; e CatDM
"likewise uses the predicted category only to filter candidate places". Contra as tres, "We instead
predict category and region in parallel, as end targets of equal standing in one model with a single
forward pass, and we drop the next-place target entirely, so neither task is an intermediate step
toward a third".
**RESPOSTA FINAL:** Porque a contribuicao e tratar categoria e regiao como saidas finais de igual
estatuto em um unico modelo, e nao como sinal auxiliar nem como passo intermediario para o lugar,
que e o que os tres desenhos que eu reviso na p. 70 fazem, e o limite esta declarado como limitacao
4, p. 90, com a delimitacao formal na Definicao 2.9, p. 22.

### [FECHADO] · Q7 · O senhor compara o modelo conjunto com baselines externos. Esses baselines rodaram no seu protocolo ou no deles?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 77 (§5.5.4) e a nota da Tabela 10 (p. 81). HMT-GRN e avaliado nos mesmos dados, folds
e inicializacoes, com a estrutura multitarefa preservada, um prior de transicao de regiao construido
com os dados de treino de cada fold, e os componentes de grafo e a busca em feixe hierarquica
removidos porque servem a predicao exata de lugar; o texto declara que "it is not a reproduction of
the complete published system". STAN e re-implementado e roda nos mesmos folds mas com as proprias
representacoes e construcao de sequencia, sob configuracao fixa, com folds parciais (TX 4/5, CA 2/5,
semente 0). ReHDM e reportado sob o protocolo publicado dele. POI-RGNN e re-implementado a partir da
arquitetura e dos hiperparametros publicados. E p. 82 declara o que a comparacao externa inclui:
"These externals run on their own embeddings, so this comparison also includes the representation
advantage of Section 5.6.1; the controlled comparison for the joint model remains the Dedicated
column of Table 10".
**RESPOSTA FINAL:** A comparacao controlada e a coluna Dedicated da Tabela 10, que partilha
representacao, janelas e folds; os externos rodam nos proprios embeddings e por isso a diferenca
contra eles inclui tambem a vantagem de representacao, o que esta dito em p. 82, com a proveniencia
de cada um em §5.5.4, p. 77.

### [ABERTO] · Q8 · O resultado de regiao e transferencia entre tarefas, ou e a arquitetura e os parametros que o senhor acrescentou?
> **Atualizado 2026-10-02.** O controle de capacidade **existe desde 2026-08-13** (P1), com os
> numeros corrigidos a 2026-09-02: na California, o dedicado de regiao com **97,4 %** dos parametros
> do conjunto (5.014.942 contra 5.151.189, contados nos logs) faz **+0,41 Acc@10 acima** dele,
> p = 0,010, cinco folds na mesma direcao; o **Texas nao tem braco pareado** (o unico, a 170,5 %, faz
> +0,21, p = 0,12). Fonte: `../erratas/VERIFICACAO.md` e `../erratas/errata_Q14_capacity_region.tex`.
> A resposta passa a ser: na California a vantagem de regiao mede capacidade. O que continua sem
> existir e a ablacao do trunk em cinco folds em CA/TX (LACUNAS P4). O texto abaixo e o de antes.

**ACAO NECESSARIA:** um controle de capacidade pareada em Texas e California, cinco folds, e uma
ablacao do trunk de cinco folds nesses dois datasets. Nenhum dos dois existe. O registro interno
que documenta a ausencia e `docs/studies/closing_data/v18/SWEEP_PLAN.md:285-290` ("A 5-fold trunk
ablation at CA/TX does not exist"), com o adiamento em `POSTPONED.md` P4, decisao de 2026-08-07.
**DADOS:** o texto **nao** credita transferencia. p. 84 (§5.7): "The evidence here does not separate
their contributions. Where the trunk was isolated directly, the arms moved both tasks by small
amounts that a screen of that size cannot distinguish from noise, and those arms were not run at the
two datasets that carry the region advantage", e a afirmacao que sobrevive e sobre o modelo, nao
sobre transferencia: "this design, shared representation and private path together, produces a joint
region output above two dedicated models at the two datasets with the largest region vocabularies".
A triagem de um fold que existe: `docs/studies/closing_data/v18/region_1fold_triage/FINDING.md`,
semente 0, `--only-fold 0`, tres bracos. Em California a vantagem de regiao sobrevive a severar o
trunk (65.4044 para 65.3051, -0.099) e a deletar tambem a tarefa de categoria (65.3276, -0.077); em
Texas sobrevive a severar o trunk (66.9797 para 66.8600, -0.120). O proprio driver declara que
"one fold gives ONE number per arm ... so it can only detect a LARGE effect" e que bracos a poucos
decimos de distancia constituem "an inconclusive screen". O candidato arquitetural nomeado no mesmo
registro: um caminho de regiao carregando 2.5 a 5.9 vezes os parametros do dedicado (Alabama
2,466,542 contra 417,117; California 3,420,110 contra 1,370,685). Em cinco folds, apenas Alabama e
Florida foram ablacionados (`SWEEP_PLAN.md:275-277`: Alabama dcat -0.015 / dreg -0.138 e dcat -0.154
/ dreg -0.004; Florida dcat +0.002 / dreg +0.026).
**RESPOSTA FINAL:** Eu nao reivindico transferencia: uma triagem de um fold mostra que a vantagem de
regiao em California e Texas sobrevive a severar o trunk e a deletar a tarefa de categoria, movendo
menos de 0.15 ponto, o que desfavorece a leitura de transferencia com um teste que tinha poder para
ela, e por isso o Cap. 5 atribui o resultado ao desenho completo, representacao partilhada mais
caminho espacial privado, e nao a troca entre as tarefas; p. 84.

### [FECHADO] · Q9 · Por que Nash-MTL, e nao um dos outros balanceadores? E a garantia dele vale aqui?
**ACAO NECESSARIA:** vazio.
**DADOS:** duas respostas distintas, uma por capitulo, e a banca pode confundi-las.
No **Cap. 5** nenhum balanceador e usado: a perda e uma soma de peso fixo, L = 0.5 L_cat + 0.5 L_reg
(Eq. 5.1, p. 73), e o motivo esta em p. 70: dezenove balanceadores de perda e de gradiente foram
triados nas configuracoes default, uma semente, dois datasets (Alabama e Florida), e "none improved
on a tuned fixed task weighting across both tasks and both datasets"; dois excedem o peso igual em
next category em Alabama, Nash-MTL por 0.68 pontos e a normalizacao de escala por 0.19, e em Florida
Nash-MTL cai abaixo do peso igual nas duas tarefas. A razao mecanistica esta no Apendice D, p. 106:
equivalencia a zero do cosseno entre os gradientes das duas tarefas nos quatro datasets medidos,
TOST contra margem de +-0.05, com as medias dentro de dois milesimos de zero.
Sobre a **garantia**, p. 29-30 (§2.3.3.1): Nash-MTL prova convergencia de uma subsequencia a um
ponto Pareto-estacionario e alcanca otimalidade de Pareto "only under an additional convexity
assumption that does not hold for a deep network"; e "This dissertation therefore claims no Pareto
property for its models".
No **Cap. 3**, onde Nash-MTL foi de fato usado, a preferencia esta datada no prefacio, p. 36: "The
chapter's preference for the Nash-MTL optimizer is likewise a conclusion of the time, weakened by a
later finding about the optimizer implementation, and Chapter 5 does not rely on it". Duas erratas
publicadas no suplemento corrigem afirmacoes sobre o metodo (invariancia de escala, nao sinais de
gradiente; e a retirada da alegacao de dois produtos matriz-vetor por iteracao, substituida pelo
custo real de um procedimento concavo-convexo iterativo, vinte passadas por default): volume
suplementar, p. 7-8.
**RESPOSTA FINAL:** O modelo final nao usa nenhum balanceador, usa peso fixo de 0.5 e 0.5, porque
dezenove deles foram triados e nenhum superou o peso fixo ajustado nas duas tarefas e nos dois
datasets, e porque o cosseno entre os dois gradientes e equivalente a zero dentro de +-0.05 nos
quatro datasets medidos; a preferencia por Nash-MTL pertence ao Cap. 3 e esta datada no prefacio
como conclusao da epoca, p. 36, p. 70 e Apendice D, p. 106.

### [FECHADO com limite] · Q10 · Cinco estados de um pais mais uma cidade. Isso generaliza?
**ACAO NECESSARIA:** vazio para a resposta; a extensao exige nova cidade.
**DADOS:** p. 90, limitacao 5: "Geographic coverage. Outside the United States, the evidence rests
on a single city, Istanbul". O que existe de evidencia externa esta em p. 83 (§5.6.3): em Istanbul
as duas tarefas ficam a um decimo de ponto dos modelos dedicados, categoria +0.08 macro-F1
(dedicado 35.34, conjunto 35.42) e regiao -0.08 Acc@10 (dedicado 75.16, conjunto 75.08), com a
diferenca de regiao bem dentro da margem de dois pontos, e o texto ressalva que "The comparable
quantity is the gain over the ceiling, not the absolute Acc@10, since region counts differ across
datasets (520 mahalle here)". A unidade de regiao muda de tract censitario para mahalle, e o Cap. 2,
p. 32, declara a diferenca de natureza: "one is a unit of measurement and the other a unit of
government". A extensao esta amarrada 1:1 a limitacao em p. 91: "Further cities outside the United
States would widen the geographic base (limitation 5)".
**RESPOSTA FINAL:** Fora dos Estados Unidos a evidencia e uma cidade, Istanbul, onde as duas tarefas
ficam a um decimo de ponto do dedicado com a regiao dentro da margem, e eu declaro isso como
limitacao 5 na p. 90, com mais cidades como trabalho futuro amarrado a ela na p. 91.

### [FECHADO] · Q11 · O senhor diz que um modelo substitui dois. O modelo conjunto e maior que os dois somados. Onde esta o ganho?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 73: o modelo conjunto tem cerca de 4.2 milhoes de parametros em Alabama contra 1.1
milhao dos dois dedicados somados (5.2 contra 2.0 em California), e uma passada adiante custa mais
computo que rodar os dois modelos pequenos. O que o texto reivindica esta na mesma pagina: "What the
single model provides is operational rather than arithmetic: one artifact to train, version, and
deploy, and one forward pass whose one set of inputs produces both answers at once". O Cap. 2, p.
35, repete a delimitacao com as mesmas palavras: "The gain is operational, not computational".
**RESPOSTA FINAL:** O ganho e operacional e esta declarado como tal: um artefato para treinar,
versionar e implantar, com as duas respostas em uma passada, e o custo aparece reportado, 4.2 milhoes
de parametros contra 1.1 milhao em Alabama, p. 73, com a mesma delimitacao na p. 35.

### [FECHADO] · Q12 · A representacao foi treinada uma vez sobre o dataset inteiro, incluindo os usuarios de validacao. Isso nao vaza?
**ACAO NECESSARIA:** vazio para o que foi medido; a cobertura que falta esta declarada.
**DADOS:** p. 75-76 (§5.5.2). O objetivo de treino da representacao nao usa os alvos de next
category nem de next region. A verificacao: uma representacao nova construida por fold, so com os
usuarios de treino daquele fold, cobrindo tres datasets em uma semente, com diferencas de -0.33 a
+0.01 Acc@10 em regiao e 0.00 a +0.29 macro-F1 em categoria. A qualificacao esta no proprio texto:
para categoria, um grafo construido so com usuarios de treino nao tem vetores de visita para
usuarios de validacao, entao a comparacao usou um vetor por lugar e manteve so as janelas cujos
lugares de entrada ocorriam no treino, cobrindo 67 a 87 por cento dos dados de validacao; "The
comparison does not cover information specific to each visit or places unseen in training". O canal
de aresta para frente esta fechado por construcao (p. 26 e p. 85, quarto limite): cada valor e
medido ate a propria visita e as arestas entre visitas consecutivas apontam so para frente, "so a
vector encodes the visit together with its own history; the graph does not pass information from a
later visit back to an earlier one, in training or at readout".
**RESPOSTA FINAL:** A representacao nunca ve os rotulos das duas tarefas, e reconstrui-la por fold
so com usuarios de treino move os resultados em no maximo 0.33 Acc@10 e 0.29 macro-F1 em tres
datasets numa semente, cobrindo 67 a 87 por cento das janelas de validacao, e o que fica fora dessa
cobertura eu declaro na mesma secao; §5.5.2, p. 75-76.

---

## Grupo B · Divergencias entre a dissertacao e o artigo submetido (as tres mais perigosas)

> Estas tres nao estao na lista de ataques prevista e sao, na minha leitura, as perguntas mais
> perigosas do conjunto, porque um arguidor que leia os dois documentos lado a lado as encontra sem
> esforco. Todas as tres tem a mesma forma: uma frase que promete mais do que mede, ou um limite que
> um documento carrega e o outro nao.

### [FECHADO por decisao sua] · Q13 · No Cap. 5 o senhor conclui que o ganho vem da representacao hierarquica e nao da injecao de features. No artigo submetido, sobre o mesmo controle, o senhor diz explicitamente que nao faz essa separacao. Qual das duas frases o senhor defende?
**ACAO NECESSARIA:** decidir, antes da defesa, se a frase da dissertacao e reescrita como errata ou
defendida oralmente com o escopo do estudo separado. A frase, como esta, nao carrega o escopo que o
artigo carrega.
**DADOS:** dissertacao, p. 79 (`chapters/5_mobiwac/06_results.tex:44-48`): o controle de
concatenacao eleva o place embedding em +2.0, +1.7 e +0.8 macro-F1 em Alabama, Arizona e Florida,
"under a tenth of the place-to-check-in gap at each state. The gain therefore comes from the
hierarchical per-visit representation, not from contextualization alone or feature injection".
Artigo submetido, p. 6 (`[mobiwac]/src_fix/sections/06_results.tex:25-37`), sobre os **mesmos tres
numeros**: "It is a separate study: a different variant of our graph, its own harness, and
embeddings built on different hardware, so its values are not on the scale of Table III and we do
not place them beside it. Within that study, concatenation raises the place embedding by +2.0, +1.7,
and +0.8 macro-F1 at Alabama, Arizona, and Florida, margins the size of the category gaps we report
or larger. On the category axis, therefore, this control does not separate the hierarchical
representation from the per-visit features it reads, and we make no such separation claim."
Verificado no registro de origem, `docs/studies/pre_freeze_gates/A2_RESULTS.md`: as fracoes de
"gap closed" (AL 18.3% / 12.4% / 2.5% contra uma variante anterior da representacao; 8.3% / 7.1% /
2.4% contra a variante seguinte) sao calculadas contra o gap **interno daquele estudo**, cujo braco
de place embedding marca 26.29 / 29.58 / 36.21 e cujo braco por check-in marca 50.73 / 52.76 / 70.45,
nao contra o gap da Tabela 9 da dissertacao (+1.62 AL, +2.58 AZ, +0.23 FL). Contra os valores da
Tabela 9, +2.0 nao e "um decimo do gap": e maior que o gap. O termo "place-to-check-in gap" aparece
uma unica vez no volume principal, nessa mesma frase (grep no fonte vivo: uma ocorrencia,
`06_results.tex:46`), e nao esta definido em nenhum outro lugar. As palavras "separate study" nao
aparecem em nenhuma pagina do volume de defesa nem do suplemento; aparecem nas pp. 6 e 7 do artigo,
a primeira vez neste paragrafo.
**RESPOSTA FINAL:** A fracao de um decimo e calculada contra o gap interno do estudo de
concatenacao, que roda em outra variante do grafo e em outro harness, e nao contra a Tabela 9 desta
dissertacao; na escala da Tabela 9 o controle nao separa a representacao hierarquica das features
por visita, que e exatamente o que o artigo submetido declara, e essa e a frase que eu defendo.
**[VERIFY: a frase do Cap. 5, p. 79, afirma a separacao que o artigo submetido recusa; nenhuma
frase do volume principal informa que o controle pertence a um estudo separado em escala diferente.
Isto e errata, nao interpretacao.]**

### [FECHADO por decisao sua] · Q14 · O artigo submetido lista o confundimento de capacidade como um dos seus cinco limites do resultado de regiao. A lista de limites da dissertacao nao o carrega. Por que ele saiu?
**ACAO NECESSARIA:** decidir se o limite volta para o deposito final ou se a resposta oral supre.
**DADOS:** artigo submetido, p. 9 (`[mobiwac]/src_fix/sections/07_discussion.tex:105-109`), quarto
de cinco limites: "the joint model carries more parameters than the two dedicated models combined,
and its region pathway in particular is several times the size of the dedicated region model. The
region advantage at Texas and California is therefore confounded with capacity: a capacity-matched
dedicated region model is the control that would separate the two, and it has not been run".
Dissertacao, p. 85: a lista comeca com "Four limits qualify these results" e nenhum dos quatro e o
confundimento de capacidade. Busca no fonte vivo do volume principal, com comentarios removidos:
"capacity-matched", "confounded with capacity" e "several times the size" nao ocorrem em nenhum
`.tex` de `chapters/` nem em `content.tex`. Nas tres extracoes de PDF: "confounded with capacity"
aparece so na p. 9 do artigo. O comentario de proveniencia em `07_discussion.tex:191` registra a
mudanca de contagem ("five members become four"). O que o volume principal **tem** e o custo de
parametros declarado em p. 73 (4.2 contra 1.1 milhao em Alabama) e a atribuicao suavizada em p. 84,
que nao credita o trunk. O que existe de controle de capacidade e o Apendice G do suplemento, p.
24-26, que cobre **apenas next category** (Alabama nas quatro sementes, California em uma semente) e
cujo proprio texto declara: "What the control does not do is decompose the joint model: it holds the
representation fixed and varies width".
**RESPOSTA FINAL:** O custo de parametros esta reportado na p. 73 e a atribuicao do resultado de
regiao na p. 84 nao credita o trunk nem a transferencia, mas o confundimento de capacidade no eixo
de regiao, que o artigo submetido lista como o quarto dos seus cinco limites, nao aparece na lista de
quatro limites da dissertacao, e o unico controle de capacidade que existe, no Apendice G, cobre
categoria e nao regiao. **[VERIFY: limite presente no artigo submetido e ausente do volume de defesa; o Apendice G
nao o cobre porque nao mede o eixo de regiao.]**

### [FECHADO por decisao sua] · Q15 · A errata do suplemento descreve um quarto fundamento de integridade da representacao, com uma sonda linear em Florida. Onde ele esta no volume de defesa?
**ACAO NECESSARIA:** verificar se a linha de errata descreve uma correcao que nao foi aplicada ao
texto depositado, ou se o texto foi reescrito e a errata ficou desatualizada.
**DADOS:** volume suplementar, p. 18, Tabela 4 (`tables/mobiwac/errata_scope.tex:31-38`), descreve a
correcao aplicada ao Cap. 5: a negativa universal do artigo ("passes no usable information about the
test visits, on three grounds") e substituida por uma afirmacao limitada sobre canais nomeados, e
"a fourth ground is added, reporting the development audit that probes the forward-edge channel
between consecutive visits, with its three limits stated: a linear probe, Florida at one random
initialization, and earlier builds of the representation. Every number already in the paragraph is
unchanged". Medido no volume de defesa: as palavras "on three grounds" e "fourth ground" nao ocorrem
em nenhuma linha viva de `chapters/` nem de `content.tex`; nas extracoes de PDF, "three grounds" e
"fourth ground" aparecem apenas na p. 18 do suplemento. Tambem ausentes do volume principal:
"linear probe", "forward-edge", "absorb", e o numero "13 to 27" do prior de transicao de regiao
construido sobre o dataset inteiro (presente na p. 5 do artigo submetido, ausente das tres
extracoes do volume principal). O paragrafo que efetivamente esta no volume de defesa, p. 75-76, e
mais curto e nao enumera fundamentos; o canal de aresta para frente aparece, sim, como quarto limite
na p. 85, em prosa e sem numero.
**RESPOSTA FINAL:** O canal de aresta para frente esta declarado no volume de defesa como quarto
limite na p. 85, mas em prosa e sem a sonda linear; a linha de errata do suplemento, p. 18, descreve
um quarto fundamento numerado que o texto depositado nao carrega, e essa divergencia entre a errata
e o texto que ela descreve e minha para corrigir. **[VERIFY: a Tabela 4 do suplemento descreve uma
correcao cuja forma enumerada nao esta presente no volume principal; decidir se a errata sobredeclara
ou se o texto perdeu o fundamento em uma reescrita.]**

---

## Grupo C · Capitulo 4 (ST-MTLNet, CoUrb)

### [FECHADO] · Q16 · O prefacio do Cap. 4 admite que a entrada da tarefa estatica contem o rotulo que ela prediz. Como isso nao invalida os ganhos de 20 a 22 pontos daquele capitulo?
**ACAO NECESSARIA:** vazio. Verificado no texto antes de escrever a resposta: a comparacao e
interna e a exposicao e comum aos dois bracos.
**DADOS:** p. 52 (prefacio do Cap. 4): "After publication, we established that the input to this
chapter's static task contains the label it predicts: the venue-type feature maps one-to-one onto
the seven top-level categories across the Gowalla state subsets used, so the reported static-task
accuracy measures that lookup rather than learned semantic inference. This does not affect the
sequential task, whose input is a check-in history and whose target category is never present in
that history". A comparacao daquele capitulo e interna: MTLnet e a **unica** baseline, declarada no
mesmo prefacio ("This chapter isolates the representation effect with MTLnet as its only baseline").
Os dois bracos leem a mesma familia de entrada: MTLnet le o embedding monolitico de 64 dimensoes
(p. 61) e as variantes leem a concatenacao de 192 dimensoes cuja componente categorica e construida
por POI Encoder sobre fine classes e depois enriquecida por HGI (p. 60-61). Como consequencia, a
exposicao ao venue type esta nos dois lados. E o Cap. 6, p. 87, ja tira a conclusao correta em duas
qualificacoes: "the static task classifies a place from that place's own representation, so the
input already determines the target. The gain therefore provides no evidence about the sequential
task", e "the comparison is not width-matched: the decomposed input has 192 dimensions, whereas the
place embedding has 64". O diagnostico que o capitulo carrega para frente e o da tarefa **sequencial**
(p. 88): "The sequential task provides the relevant diagnosis because its input does not determine
its target", com 15 de 21 combinacoes categoria-estado favoraveis as variantes e um empate tecnico
(p. 64-65).
**RESPOSTA FINAL:** Porque a comparacao daquele capitulo e interna, MTLnet contra as variantes, e a
exposicao ao venue type esta nos dois bracos, de modo que os 20 a 22 pontos medem uma mudanca de
representacao sob a mesma consulta, e o Cap. 6, p. 87, ja declara que aquele ganho nao fornece
evidencia sobre a tarefa sequencial, que e onde o diagnostico e feito com 15 de 21 combinacoes; p.
52 e p. 87-88.

### [FECHADO] · Q17 · A entrada decomposta tem 192 dimensoes e a baseline tem 64. Quanto do ganho e so largura?
**ACAO NECESSARIA:** vazio para a resposta; o controle de dimensao igual permanece nao executado e
esta declarado como tal.
**DADOS:** p. 61: a arquitetura MTLnet projeta qualquer entrada ao mesmo espaco latente partilhado de
dimensao 256 pelos encoders especificos de tarefa, "so that the capacity of the shared layers and
task heads remains unchanged across the evaluated models", e o proprio capitulo publicado declara na
mesma pagina que "the difference in input dimensionality may influence part of the observed gains.
For this reason, an additional experimental control equalizing the dimensionality of the
representations would allow validating more precisely whether the gains occur mainly from the
semantic specialization of the encoders". O Cap. 6, p. 87, repete a exigencia: "Chapter 4 therefore
calls for an equal-dimension control to separate the semantic contribution of the encoders from the
effect of the additional width".
**RESPOSTA FINAL:** As camadas partilhadas e as cabecas tem capacidade identica nos dois bracos,
porque MTLnet projeta qualquer entrada ao mesmo espaco de 256 dimensoes, mas a largura de entrada
difere e o controle de dimensao igual nao foi executado, o que esta declarado no proprio capitulo,
p. 61, e repetido como qualificacao no Cap. 6, p. 87.

### [FECHADO] · Q18 · Em Travel a baseline continua ganhando. O senhor tem uma explicacao ou uma desculpa?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 65 (Tabela 7): em Florida, Travel e MTLnet 64.47 +- 1.02 contra 45.00 +- 1.10 (SIREN) e
44.93 +- 1.11 (Sphere2Vec-M); em California, 46.05 +- 0.84 contra 36.94 e 37.82. A explicacao esta em
p. 64: "This behavior may be related to the nature of the Travel category itself, which tends to
involve sparser movements between distant regions. In these cases, the graph topology used by DGI
may be more efficient for preserving relationships between geographically distant POIs", com o
fechamento de que os dois tipos de representacao capturam aspectos complementares. A limitacao esta
declarada em p. 66, junto com a de que os tres componentes sao usados em conjunto e o capitulo nao
isola a contribuicao individual de cada encoder.
**RESPOSTA FINAL:** Em Travel a topologia de grafo do DGI preserva melhor relacoes entre POIs
geograficamente distantes, que e o padrao dessa categoria, e o capitulo declara isso como limitacao
em vez de arredondar; Tabela 7, p. 65, com a leitura em p. 64 e a limitacao em p. 66.

---

## Grupo D · Capitulo 3 (CBIC) e o protocolo dos dois primeiros estudos

### [FECHADO] · Q19 · Os dois primeiros estudos usam divisao estratificada por amostra, nao disjunta por usuario. Os resultados deles ainda valem?
**ACAO NECESSARIA:** vazio.
**DADOS:** o protocolo esta declarado no proprio Cap. 3, p. 46: "The folds are formed by a
stratified splitter over the samples rather than over the users, so the check-ins of one user may
appear in both training and validation. For the category task the sample unit is the place, so no
place spans two folds. The code of record pins a single random seed, so the five folds constitute
one repetition of the experiment rather than several". Cada tarefa e lida na epoca da sua propria
maior macro-F1 de validacao, medida no mesmo fold onde o escore e reportado (p. 47). Os dois
prefacios datam as conclusoes, cada um com sua formulacao: p. 36, "Its conclusions are the
conclusions of the time, for the configuration studied here"; p. 52, "The conclusions reported here
are those of the time, for that configuration". O Cap. 2, p. 35, faz a delimitacao no nivel do enquadramento: "Chapters 3
and 4 instead use sample-stratified splits and report fold means without significance tests. In the
final study, user-disjoint cross-validation limits leakage between a user's training and test
visits". A validade que os dois capitulos carregam para frente e a **direcional e interna**: Cap. 3
entrega um resultado nulo (p. 49: as diferencas entre MTL e Single sao pequenas e frequentemente
caem dentro dos desvios reportados), e Cap. 4 entrega uma comparacao contra uma unica baseline sob o
mesmo protocolo nos dois bracos.
**RESPOSTA FINAL:** Eles valem como o que sao, comparacoes internas sob um protocolo mais fraco,
declarado na p. 46 e datado nos dois prefacios, e nenhuma conclusao do documento depende de um
numero absoluto deles: o Cap. 3 entrega um nulo e o Cap. 4 uma comparacao contra uma unica baseline
com o mesmo protocolo nos dois lados; a delimitacao de enquadramento esta na p. 35.

### [FECHADO] · Q20 · Os numeros do corpus de Florida mudam entre capitulos. 990.518 check-ins no Cap. 3 e 1.407.034 no Cap. 5. Qual esta certo?
**ACAO NECESSARIA:** vazio.
**DADOS:** volume suplementar, §B.4, p. 13-14: "Chapters 3 and 4 report the Florida subset of
Gowalla as 20,301 users, 65,009 POIs, and 990,518 check-ins, while Chapter 5 reports 21,052 users,
76,544 POIs, and 1,407,034 check-ins for the same state of the same public dataset. The two are
different extractions of that state, not different datasets and not a discrepancy between them". O
mecanismo declarado e a tabela de mapeamento de categorias, estendida cerca de onze meses depois da
extracao anterior, com os lugares acrescentados caindo majoritariamente em Entertainment, Outdoors e
Travel; uma comparacao controlada confirma que cada POI, usuario e check-in da extracao anterior
reaparece na atual, que adiciona outros. O registro esta em `src_utils/evidence/cbic_recompute_result.md`.
Os tres numeros do Cap. 3 sao, eles proprios, uma errata declarada: o artigo publicado deixou
placeholders e os valores vieram da tabela publicada do CoUrb (suplemento, p. 7).
**RESPOSTA FINAL:** Sao duas extracoes do mesmo estado do mesmo dataset publico, nao um conflito: a
tabela de mapeamento de categorias foi estendida cerca de onze meses depois, cada registro da
extracao anterior reaparece na atual, e cada capitulo reporta o corpus como o pipeline da sua epoca
o produziu; suplemento, §B.4, p. 13-14.

---

## Grupo E · Capitulos 1, 2 e 6 (o enquadramento)

### [FECHADO] · Q21 · O senhor cita 93 por cento de previsibilidade potencial da mobilidade humana. Seus melhores numeros sao 37 de macro-F1 e 66 de Acc@10. Por que a distancia?
**ACAO NECESSARIA:** vazio.
**DADOS:** o Cap. 2, p. 20, ja desarma a comparacao no ponto onde a cita: "An entropy analysis
estimated the potential predictability of an individual's next location at about 93 percent. Because
this estimate concerns next-location prediction at a coarse spatial resolution, it shows that
mobility contains learnable regularity but does not provide a reference point for the category and
region metrics defined" nesta dissertacao. Os pontos de referencia que valem sao declarados: piso de
classe majoritaria entre 5.7 e 7.3 macro-F1 conforme o dataset, mais baixo em Florida (p. 80); palpite
aleatorio de dez regioes certo em no maximo cerca de dois por cento (p. 80); piso de Markov de
primeira ordem para regiao entre 51 e 72 Acc@10 sob nossas janelas e folds, excedido pelo modelo
conjunto por 4.1 a 10.0 pontos nos seis datasets (p. 82).
**RESPOSTA FINAL:** Aquela estimativa e de next location em resolucao espacial grosseira e o proprio
Cap. 2 diz, na pagina em que a cita, que ela nao serve de ponto de referencia para as minhas
metricas; os pontos que servem sao o piso de classe majoritaria de 5.7 a 7.3 macro-F1 e o piso de
Markov de regiao de 51 a 72 Acc@10, que eu supero por 4.1 a 10.0 pontos; p. 20, p. 80 e p. 82.

### [FECHADO] · Q22 · O piso de Markov de regiao fica acima de tres sistemas externos publicados. Isso nao diz que a sua tarefa e facil, ou que os externos foram mal executados?
**ACAO NECESSARIA:** vazio.
**DADOS:** p. 82-83 trata a questao de frente. HMT-GRN fica abaixo do piso nos seis datasets, a
referencia ReHDM em tres, e STAN em quatro. Dois fatos sobre a producao dos numeros sao declarados:
o piso e computado sob nosso proprio protocolo de janela deslizante e nossos folds, e as janelas
avancam uma visita por vez, "so the region of the last visit is a strong predictor of the next one,
and a first-order transition table reads exactly that signal", com o alvo sendo a ultima regiao
visitada em 32.9 por cento das janelas em Alabama; e os tres sistemas nao encontram o piso em termos
iguais (HMT-GRN nos mesmos dados, folds e inicializacao; STAN nos mesmos folds mas com embeddings e
sequencias proprios; ReHDM sob o protocolo publicado dele). O texto declina explicitamente de uma
explicacao unica: "Neither fact establishes why the floor lies above the three systems, and we do
not claim a single explanation. We treat the floor, not the external systems, as the reference the
region task has to clear".
**RESPOSTA FINAL:** O piso e computado sob as minhas janelas, que avancam uma visita por vez, e em
Alabama o alvo e a ultima regiao visitada em 32.9 por cento das janelas, de modo que uma tabela de
transicao de primeira ordem le exatamente esse sinal; eu trato o piso, e nao os sistemas externos,
como a referencia que a tarefa de regiao tem de vencer, e nao reivindico uma explicacao unica para a
ordenacao; p. 82-83.

### [FECHADO] · Q23 · Sete classes de categoria e uma tarefa de dez regioes em milhares. As duas metricas nao sao comparaveis entre datasets. O que sustenta a leitura de escala?
**ACAO NECESSARIA:** vazio.
**DADOS:** as duas limitacoes de metrica estao declaradas no Cap. 2, p. 32: macro-F1 "does not show
which individual classes improve, and it can be low even when overall accuracy is high"; Acc@10
"does not distinguish first place from tenth and does not measure the probability assigned to the
true region", e regioes ausentes da particao de treino contam como erro, com o desconto de fora de
distribuicao definido em p. 32-33. A comparabilidade entre datasets esta restringida em p. 83: "The
comparable quantity is the gain over the ceiling, not the absolute Acc@10, since region counts
differ across datasets". A leitura de escala e declarada como observacao, nao lei, em tres lugares
(p. 82, p. 86, p. 88-89): a ordenacao nao e monotona dentro do par, porque California tem mais
regioes que Texas e ganho ligeiramente menor, e a contagem de regioes co-varia com o tamanho do
corpus, de modo que "A controlled experiment is therefore required to separate the effect of region
count from the amount of data and other differences between the states. Problem scale remains a
possible condition, not an established cause".
**RESPOSTA FINAL:** A quantidade comparavel entre datasets e o ganho sobre o dedicado, nao o Acc@10
absoluto, e eu digo isso na p. 83; a leitura de escala e declarada como observacao e nao como lei
nas p. 82, 86 e 88, porque a ordenacao nao e monotona dentro do par Texas-California e a contagem de
regioes co-varia com o tamanho do corpus.

---

## As perguntas cuja resposta honesta e "nao foi medido"

> Cada uma destas tem uma resposta correta que declara um limite. A frase preparada declara o limite
> e diz por que ele nao derruba a tese. Uma pergunta sem resposta preparada custa mais na sala que
> uma resposta que declara um limite.

### U1 · O trunk partilhado contribui algo em Texas e California?
**Nao foi medido.** O que existe: uma triagem de um fold, semente 0, tres bracos, onde a vantagem de
regiao sobrevive a severar o trunk e a deletar a tarefa de categoria, com movimento abaixo de 0.15
ponto em todos os bracos (`region_1fold_triage/FINDING.md`). O proprio driver declara que bracos a
poucos decimos de distancia constituem uma triagem inconclusiva para efeitos pequenos. A ablacao de
cinco folds nesses dois datasets nao existe (`SWEEP_PLAN.md:285-290`).
**Por que nao derruba a tese.** Porque a tese nao afirma que o trunk carrega o resultado. A
afirmacao que o Cap. 5 faz, na p. 84, e sobre o desenho completo, representacao partilhada mais
caminho espacial privado, e o texto declara na mesma pagina que a evidencia nao separa as
contribuicoes das duas partes. A triagem tinha poder para a hipotese de que o trunk carrega os dois
pontos e nao a confirmou, o que reforca a formulacao cautelosa em vez de contradiz-la.

### U2 · A vantagem de regiao sobrevive a um controle de capacidade pareada?
> **Atualizado 2026-10-02: foi medido** (P1, 2026-08-13; numeros corrigidos a 2026-09-02). Na
> California **nao sobrevive**: o dedicado de regiao com 97,4 % dos parametros do conjunto faz +0,41
> Acc@10 acima dele (p = 0,010, 5/5). O Texas nao tem braco pareado. Ver Q8 acima e
> `../erratas/RESPOSTAS_ORAIS.md` §Q14. O paragrafo abaixo e o de antes da medicao, e o fator de
> categoria e **6,7** desde a recontagem de 2026-09-02.

**Nao foi medido no eixo de regiao.** O controle de capacidade que existe, Apendice G do suplemento,
p. 24-26, cobre **next category**: em Alabama, multiplicar por 6.5 os parametros treinaveis do
modelo dedicado **reduz** sua macro-F1 em 0.53 ponto, com teste pareado sobre as quatro sementes
separando a diferenca de zero (p = 0.0011) e direcao unanime nos vinte folds; em California, com uma
semente, os tres bracos ficam a 0.06 ponto entre si. O proprio apendice declara: "What the control
does not do is decompose the joint model: it holds the representation fixed and varies width".
**Por que nao derruba a tese.** No eixo de categoria, que e onde a tese central sobre representacao
vive, a explicacao alternativa por contagem de parametros esta testada e nao sustentada em Alabama.
No eixo de regiao, os dois ganhos sao resultados secundarios fora do plano de analise registrado,
declarado na p. 76 e repetido na p. 88, e o custo de parametros esta reportado na p. 73 em vez de
escondido. A tese, "a representacao e o fator dominante", nao depende dos dois ganhos de regiao.

### U3 · Qual o tamanho da dependencia entre as duas entradas do modelo conjunto?
**Nao foi medido.** A nao independencia esta declarada sem numero no Cap. 2, p. 27. A unica fronteira
quantificada e arquitetural: a copia com gradiente interrompido na rota espacial, Apendice E, p. 112.
**Por que nao derruba a tese.** Porque a comparacao que sustenta as conclusoes e pareada e interna:
o modelo conjunto contra os dedicados, sob a mesma representacao, as mesmas janelas e os mesmos
folds (p. 82). As duas entradas partilharem origem afeta a interpretacao mecanistica do que o trunk
faz, questao que o texto ja deixa aberta na p. 84, e nao a validade da diferenca medida.

### U4 · O cosseno entre os gradientes das duas tarefas continua ortogonal em Texas e California?
**Nao foi medido.** O Apendice D cobre quatro dos seis datasets, e a tabela declara: "Texas and
California are not measured here, so the table covers four of the six datasets of Chapter 5" (p.
106). Sao precisamente os dois onde o modelo conjunto supera em regiao, e o apendice diz isso: o
diagnostico "leaves the largest label spaces untested" (p. 108). O apendice tambem limita a si mesmo
por arquitetura: "Nothing here says the gradients stay orthogonal in a model that shares more of its
depth, couples the tasks in a cascade, or shares an output layer" (p. 108).
**Por que nao derruba a tese.** Porque a funcao do apendice e explicar por que um balanceador de
gradiente nao tinha o que balancear, e essa explicacao e sustentada de forma independente pela
triagem de dezenove balanceadores em dois datasets (p. 70). Nos quatro datasets medidos, a
equivalencia a zero vale com margem de +-0.05 e medias dentro de dois milesimos de zero, e nenhuma
conclusao do Cap. 5 depende do cosseno em Texas ou California.

### U5 · Quao longe fica a regiao predita quando o modelo erra?
**Nao foi medido.** Declarado na p. 85: "Where the shortlist misses, the geographic size of the error
is the quantity that would matter to such a service, and measuring it requires the per-visit
predictions that the evaluation path does not retain, so it is left to future work". O
enquadramento de servico e explicitamente motivacao, nao resultado: terceiro limite da p. 85, "we do
not build or evaluate a mobility-aware service; it is background motivation".
**Por que nao derruba a tese.** Porque nenhuma afirmacao do documento e sobre desempenho de servico.
As afirmacoes sao os resultados de predicao, e a leitura de lista curta em p. 84 e apresentada com o
numero que a sustenta, o proprio Acc@10 da Tabela 10 (California 64.54 por cento em dez tracts de
8.501; Texas 66.15 por cento em dez de 6.553).

### U6 · O senhor consegue separar a mudanca de par de tarefas da mudanca de representacao e de topologia?
**Nao foi medido, e o motivo e estrutural.** Limitacao 6, p. 90: nenhuma ablacao controlada separa a
mudanca de representacao e topologia da mudanca de par de tarefas; o Cap. 4 e o controle de par fixo
para o diagnostico; e a ablacao que separaria as duas, rodar classificacao estatica de categoria sob
a representacao por check-in, "is not clean under that representation: the category of the visited
place is an input feature of a check-in node, so that target would be partly readable from its own
input. This follows from the design of the representation and was not measured, so the confound is
bounded by the fixed-pair control rather than removed". Trabalho futuro amarrado a ela, p. 91:
precisa de um alvo estatico que a representacao nao carregue como feature de entrada.
**Por que nao derruba a tese.** Porque a tese e condicional por construcao, declarada na p. 89: "It
is that multitask learning helps next-category and next-region prediction under the final design and
evaluation protocol developed in this dissertation". O Cap. 4 mantem o par fixo enquanto muda a
representacao, e e esse capitulo, nao o Cap. 5, que sustenta a afirmacao de que a representacao e o
fator dominante.

### U7 · A representacao serve modelos que nao sao o seu?
**Nao foi medido.** Cap. 6, p. 88: o resultado "also supports testing Check2HGI in other mobility
prediction architectures, although its benefit in those architectures has not yet been evaluated". E
limitacao 3, p. 90: a representacao e transdutiva, treinada no grafo de check-ins de cada dataset,
"so it cannot represent unseen places or users without retraining".
**Por que nao derruba a tese.** Porque toda comparacao que sustenta a tese mantem o modelo
consumidor fixo e varia so a representacao (Tabela 9, p. 79: mesmo modelo de tarefa unica, mesma
configuracao, mesmas janelas, mesmo orcamento de epocas, mesmos folds; so a entrada muda), o que e
exatamente o desenho que isola o efeito de representacao dentro deste documento.

### U8 · A margem de dois pontos e o limiar em que um servico se comportaria diferente. Isso foi medido em um servico?
**Nao foi medido.** A justificativa da margem esta em p. 77 e e um julgamento declarado como tal: um
servico atenta a qual regiao ficara movimentada, nao a uma posicao unica no ranking, e "A two-point
change in Acc@10 is below the level at which this service would behave differently". O que existe de
apoio empirico e a dispersao: o desvio padrao da diferenca pareada entre as quatro particoes de
usuarios vai de 0.02 a 0.16 ponto, e os intervalos em Istanbul, Arizona e Florida sao estreitos o
bastante para sustentar uma margem de um ponto, ao contrario de Alabama.
**Por que nao derruba a tese.** Porque a margem foi registrada antes de qualquer resultado ser lido
(p. 76) e as quatro celulas dentro dela vencem a margem com folga, com o maior deficit em 0.87
(p. 82). Se a margem fosse de um ponto, tres dos quatro datasets ainda a sustentariam pelos proprios
intervalos, e o documento declara qual e a excecao.

---

## Passagem do agente critico (porta exigida por AGENT_GUARDRAILS)

As 31 entradas deste registro passaram por uma verificacao independente, entrada por entrada, contra
o texto integral das paginas que cada uma cita. O verificador nao escreveu nenhuma entrada e recebeu
apenas a entrada mais as paginas, com a instrucao de classificar cada afirmacao como sustentada, nao
sustentada ou nao verificavel com o material fornecido.

Resultado: 27 entradas passaram sem achado. Quatro voltaram com achados, todos verificados por mim
contra a fonte antes de qualquer mudanca, e tres deles corretos:

1. **Q6.** A entrada atribuia a HMT-GRN o papel de filtro de candidatos. A p. 70 atribui esse papel
   a CatDM; HMT-GRN e descrito ali como sistema em que categoria e regiao sao sinais auxiliares de
   uma tarefa primaria de proximo lugar, e a cascata em cadeia e CSLSL. **Corrigido:** a entrada
   agora separa os tres desenhos como a p. 70 os separa.
2. **Q14.** A entrada chamava o confundimento de capacidade de "quinto limite" do artigo, enquanto
   os proprios DADOS da entrada o citavam como quarto de cinco. Contado na p. 9 do artigo: primeiro,
   representacao treinada uma vez; segundo, selecao de epoca; terceiro, ausencia de servico; quarto,
   capacidade; quinto, canal de aresta para frente. **Corrigido** no titulo e na resposta final.
3. **Q19.** A entrada citava uma unica frase de datacao como se fosse identica nos dois prefacios. As
   formulacoes diferem: p. 36, "Its conclusions are the conclusions of the time, for the
   configuration studied here"; p. 52, "The conclusions reported here are those of the time, for that
   configuration". **Corrigido:** as duas citacoes aparecem agora separadamente.
4. **Q13.** O verificador marcou como nao verificaveis, com o material que recebeu, duas afirmacoes
   de ausencia: que "place-to-check-in gap" ocorre uma unica vez no volume principal e que "separate
   study" nao ocorre em nenhum dos dois volumes da dissertacao. Ambas sao afirmacoes de ausencia
   sobre corpus inteiro, que uma amostra de paginas nao pode confirmar. Eu as medi diretamente sobre
   as tres extracoes completas de PDF e sobre o fonte vivo com comentarios removidos, e ambas se
   mantem. As tres afirmacoes substantivas de Q13, as duas citacoes e a aritmetica contra a Tabela 9,
   foram classificadas como sustentadas.

Alem da passagem critica, todas as 79 citacoes literais deste registro foram conferidas
programaticamente contra a pagina citada, e todas as 14 referencias arquivo:linha contra o arquivo
correspondente. Sete referencias de linha estavam deslocadas em uma a seis linhas na primeira versao
e foram corrigidas; nenhuma citacao literal falhou depois da correcao de pagina em Q13.

**O que esta verificacao nao cobre.** Ela confirma que cada afirmacao corresponde ao texto dos
documentos e que cada numero esta na pagina indicada. Ela nao reexecuta nenhum experimento, nao
valida os numeros contra os arquivos de resultado, e nao substitui a auditoria independente do autor.

---

## Ledger de fontes deste registro

| Documento | Caminho | O que foi lido |
|---|---|---|
| Volume de defesa (119 pp) | `articles/dissertacao/src_fix/build/main.pdf` | Cap. 1 (pp. 15-19), Cap. 2 (pp. 20-35), Cap. 3 (pp. 36-51), Cap. 4 (pp. 52-66), Cap. 5 (pp. 67-86), Cap. 6 (pp. 87-91), Apendices A-E (pp. 100-118) |
| Volume suplementar (27 pp) | `articles/dissertacao/src_fix/build/main_extra.pdf` | Apendice B errata (pp. 6-18), Apendice D benchmark de historico de rotulos (pp. 19-21), Apendice G controle de contagem de parametros (pp. 24-26) |
| Artigo submetido (10 pp) | `articles/[mobiwac]/src_fix/main.pdf` e `sections/*.tex` | integral, comparado sentenca a sentenca com o Cap. 5 |
| Fonte vivo | `articles/dissertacao/src_fix/chapters/`, `content.tex`, `tables/` | linhas citadas por arquivo:linha; comentarios de proveniencia lidos e nao tratados como texto |
| Triagem do trunk | `docs/studies/closing_data/v18/region_1fold_triage/FINDING.md` | tabela de resultados e secao de limites |
| Plano de varredura | `docs/studies/closing_data/v18/SWEEP_PLAN.md` | linhas 275-290 (bracos de ablacao do trunk e o escopo declarado) |
| Controle de concatenacao | `docs/studies/pre_freeze_gates/A2_RESULTS.md` | tabelas de categoria e de regiao, e a base de calculo das fracoes de gap |
| Plano de revisao | `articles/dissertacao/src_fix/REVISION_PLAN.md` | §1.3 (convencao), §15.4 (divergencia de silhueta) |
| Registro de exclusoes | `articles/dissertacao/src_utils/LEFT_OUT.md` | LO-9 (condicoes da garantia de Nash-MTL) |

## Flags [VERIFY] deste registro

1. **Q13.** A frase do Cap. 5, p. 79, afirma que o ganho vem da representacao hierarquica e nao de
   injecao de features; o artigo submetido, p. 7, recusa explicitamente essa separacao sobre os
   mesmos tres numeros. A fracao "under a tenth of the place-to-check-in gap" e calculada contra o
   gap interno de um estudo separado (`A2_RESULTS.md`), nao contra a Tabela 9 da dissertacao, e
   nenhuma frase do volume principal informa isso. Falta: decisao do autor entre errata e resposta
   oral com escopo.
2. **Q14.** O confundimento de capacidade do resultado de regiao e o quinto limite do artigo
   submetido e nao consta da lista de quatro limites da dissertacao (p. 85); as expressoes
   "capacity-matched", "confounded with capacity" e "several times the size" nao ocorrem em nenhuma
   linha viva do volume principal. Falta: decisao sobre reintroduzir o limite no deposito final.
3. **Q15.** A Tabela 4 do suplemento (p. 18) descreve um quarto fundamento de integridade com sonda
   linear em Florida; a forma enumerada nao existe no volume principal, cujo paragrafo de integridade
   (pp. 75-76) nao enumera fundamentos. Falta: verificar se a errata sobredeclara ou se o texto
   perdeu o fundamento em reescrita.
4. **Q5 / U3.** Nenhum numero quantifica a dependencia entre as duas tabelas de entrada. Falta: uma
   medida unica de sobreposicao de informacao entre as janelas semantica e espacial.
5. **Apendice de escopo estatico.** `chapters/apx_b_static_scope.tex` existe na arvore e nao esta
   incluido em nenhum dos dois builds (nao aparece em `content.tex` nem em `main_extra.tex`). Seus
   comentarios carregam um sign-off aberto do autor sobre um canal de auto-vazamento medido no
   embedding do Cap. 3 (peso medio de 0.10 contra peso total de 0.39 da propria categoria; sonda
   caindo de 0.46 para 0.30 macro-F1 contra piso de 0.07) e uma constatacao incidental sobre o
   objetivo contrastivo do Cap. 3. Nada disso esta em nenhum dos dois volumes. Falta: decisao do
   autor sobre se algo dali deve ser dito oralmente. **Nao e uma pergunta que a banca fara sem o
   repositorio**, mas e a unica coisa que eu encontrei que um arguidor com acesso ao codigo poderia
   levantar e que nenhum dos dois documentos antecipa.
