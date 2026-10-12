# NEW_VERSION — o mtlcheck, e o que a reescrita muda para a defesa

> **O que este registro e.** O sistema experimental foi reescrito do zero depois do envio da
> dissertacao, num repositorio novo chamado `mtlcheck`. O trabalho encontrou defeitos no codigo
> antigo, corrigiu parte deles, reproduziu outra parte de proposito, e trocou o protocolo de
> avaliacao inteiro. Este documento registra **o que isso significa para a banca**: o que muda, o que
> nao muda, e a resposta preparada para cada pergunta que a reescrita torna possivel.
>
> **O que este registro nao e.** Nao e descricao de arquitetura de software. Onde a decisao tecnica
> importa, ela entra so pelo lado que um arguidor pode puxar.
>
> **Regra de qualidade aplicada.** Nenhuma afirmacao entra sem o artefato que a sustenta. Todo
> caminho citado e relativo a raiz do repo novo, declarada na secao 11.
>
> **Aviso de escopo.** Nada aqui edita o documento enviado. O que exige mudanca esta na secao 4 e na
> secao 10, marcado como decisao do autor.

---

## Indice: o que fecha como

| Fecha por | Item |
|---|---|
| **Resposta oral, ja sustentada por medicao** | N1, N2, N5, N6, N7, N8 |
| **Resposta oral que declara um limite** | N3, N4, N9 |
| **Decisao sua, antes da defesa** | a margem de dois pontos (secao 4). *A contagem de usuarios (secao 10.1) e a contagem de parametros do apendice de capacidade (secao 10.6) foram resolvidas a 2026-09-01 e 2026-09-02; ver o topo de cada secao (anotado 2026-10-02).* |
| **So fecha com execucao** | a paridade do modelo conjunto, a decomposicao do checkpoint unico (secao 10) |

---

## 1 · O que e, em uma linha

Uma reimplementacao limpa do sistema que produziu o Capitulo 5, escrita sem reaproveitar codigo do
repositorio antigo, e validada contra ele numero a numero.

Em 2026-08-21 ela e **independente do corpus bruto ate modelos treinados**: le os check-ins e o
shapefile, constroi o grafo de Delaunay e o code book do POI2Vec em processo, treina o substrato,
treina as tres familias (categoria dedicada, regiao dedicada, conjunto) e pontua. Nenhum arquivo
produzido pelo repositorio antigo entra no caminho.

O ponto que interessa a defesa nao e a reescrita em si. E o que ela permitiu: **rodar o sistema
antigo e o novo lado a lado, com a mesma particao, e atribuir cada diferenca a uma causa nomeada.**

---

## 2 · A regra que organiza tudo, e sem a qual o resto se le errado

Quando um numero muda entre o mtlcheck e a dissertacao, ele mudou por **um** de tres motivos, e eles
tem implicacoes opostas:

| | quem estava errado | o que o numero significa |
|---|---|---|
| **correcao de migracao** | **nos** | fechamos um buraco do porte. **Nao e ganho sobre a dissertacao** |
| **defeito reproduzido** | a referencia, e mantemos | o numero e comparavel com a dissertacao porque carrega o mesmo defeito |
| **melhoria real** | a referencia, e corrigimos | o numero **deixa de ser comparavel** sem declarar a mudanca |

Fonte: `docs/DIVERGENCE_REGISTER.md`.

**Por que isto e a primeira secao.** As tres correcoes do POI2Vec valeram **+0,86 pp** em regiao. Lida
sem categoria, essa frase parece "superamos a dissertacao em quase um ponto". E o oposto: era um bug
nosso, aberto pelo porte, e o resultado e **paridade** — 74,70 contra 74,64 do incumbente. Se alguem
citar um ganho da reescrita na defesa sem dizer de qual coluna ele saiu, a frase esta errada.

---

## 3 · [N1] Os numeros da dissertacao se sustentam

Esta e a pergunta que a banca fara primeiro se souber da reescrita: *voces reescreveram o sistema; os
numeros mudaram?*

**Nao.** Comparacao do estado atual do mtlcheck contra a tabela do Capitulo 5, sob o **protocolo dela**
(cinco folds planos) e com o substrato ja corrigido, em Alabama e Arizona, oito celulas:

| estado | tarefa | braco | mtlcheck | dissertacao | sd entre sementes (dela) | delta |
|---|---|---|--:|--:|--:|--:|
| Alabama | categoria | dedicado | 30,737 | 30,77 | 0,07 | −0,033 |
| Alabama | categoria | conjunto | 30,568 | 30,59 | 0,07 | −0,022 |
| Alabama | regiao | dedicado | 69,858 | 70,12 | 0,10 | −0,262 |
| Alabama | regiao | conjunto | 69,661 | 69,24 | 0,16 | **+0,421** |
| Arizona | categoria | dedicado | 34,556 | 34,57 | 0,04 | −0,014 |
| Arizona | categoria | conjunto | 34,481 | 34,57 | 0,06 | −0,089 |
| Arizona | regiao | dedicado | 59,350 | 59,48 | 0,07 | −0,130 |
| Arizona | regiao | conjunto | 59,162 | 59,04 | 0,22 | +0,122 |

**Delta medio: −0,001 pp. Maior desvio absoluto: 0,421 pp.** Categoria reproduz quase exatamente
(−0,014 a −0,089).

⚠ Esta tabela tem prazo de validade, e ele esta na secao 10.5.

**Duas ressalvas que a frase oral precisa carregar.** Primeira: **uma** semente do nosso lado contra
quatro do lado dela, e o desvio entre sementes dela (0,04 a 0,22) e da ordem de varios desses deltas
— eles nao sao distinguiveis de variacao de semente. Segunda: as duas colunas nao sao a mesma
configuracao. O substrato foi reconstruido em casa, a torre de regiao foi unificada (secao 6) e o
POI2Vec foi corrigido; sao mudancas declaradas, nao uma re-execucao identica.

**A frase defensavel:** *"o sistema foi reescrito do zero e reproduz a tabela do Capitulo 5 com desvio
medio de um milesimo de ponto em oito celulas; o maior desvio individual e quatro decimos, e fica na
ordem do desvio entre sementes que a propria tabela publica."*

Evidencia: `studies/porting_validation/evidence/estado_vs_dissertacao.json`.

---

## 4 · [N2] O que muda nao e o numero. E o veredito, e por causa da margem

Este e o ponto de errata mais importante que a reescrita produz, e ele nao vem de um numero
diferente.

O Capitulo 5 declara uma margem de nao-inferioridade de **dois pontos**, fixada no plano de analise
antes de qualquer resultado ser lido, e marca Alabama/regiao como dentro dela. O protocolo novo fixa
a margem em **0,4 pp**, derivada de tres pisos medidos (secao 5). Sob a margem nova, com teste
externo lacrado e quatro replicas, a mesma celula da **inferior**:

| estado | tarefa | dedicado | conjunto | delta | BCa 95 % | p | veredito |
|---|---|--:|--:|--:|---|--:|---|
| Alabama | categoria | 30,339 | 30,079 | −0,273 | [−0,500, −0,056] | 0,024 | inconclusivo |
| Alabama | regiao | 69,006 | 68,053 | **−0,953** | [−1,149, −0,751] | 0,0001 | **inferior** |
| Arizona | categoria | 34,317 | 34,201 | −0,120 | [−0,249, +0,009] | 0,066 | nao-inferior |
| Arizona | regiao | 58,696 | 58,224 | −0,472 | [−0,636, −0,295] | 0,0001 | inconclusivo |
| Istambul | categoria | 35,132 | 35,302 | **+0,164** | [+0,049, +0,272] | 0,0032 | **superior** |
| Istambul | regiao | 74,973 | 74,820 | −0,152 | [−0,282, −0,080] | 0,0005 | nao-inferior |

Correcao de multiplicidade ainda nao aplicada; os vereditos acima sao por celula, no nivel nominal.
Fonte: `studies/porting_validation/SEALED_BRIDGE_READ.md` §1 e
`evidence/sealed_bridge_tier_a.json`, leitura selada de 2026-08-18.

**O que isto obriga a dizer.** A nao-inferioridade de Alabama/regiao **depende da margem de dois
pontos**. Com uma margem cinco vezes menor e com o protocolo aninhado, a mesma comparacao conclui
inferioridade. A margem precisa estar justificada em voz alta, e ela **esta** — o §5.5.3 do Capitulo 5
argumenta a partir do servico ("uma mudanca de dois pontos em Acc@10 esta abaixo do nivel em que
este servico se comportaria diferente") e, o que e mais forte, **ja nomeia Alabama como a excecao**:
*"The intervals at Istanbul, Arizona, and Florida are narrow enough to support a margin as small as
one point; Alabama's is not, and it is the dataset with the largest region difference."*

**O que isto nao obriga.** Nao vira uma correcao de numero: os numeros da secao 3 ficam. E o delta
medido tem uma segunda leitura, registrada na secao 10.2, que nao e sobre o modelo.

**A frase defensavel:** *"a margem e uma escolha declarada, e o texto ja diz que Alabama e o dataset
que ela menos sustenta. Refizemos a analise com uma margem cinco vezes mais estrita e protocolo
selado, e nessa margem Alabama/regiao fica abaixo. As outras cinco celulas mantem o veredito, e a
alegacao co-primaria se sustenta inteira em Istambul, cujo teste externo so foi lido uma vez, em
2026-08-18."*

⚠ **Uma coisa que essa frase nao pode carregar, e que e facil supor.** Istambul **nao** e um dataset
livre de ajuste — pela cobertura declarada no proprio texto entregue, ele e o **mais** ajustado dos
tres pequenos, nao o menos (secao 10.7). O que sustenta a leitura de Istambul e o teste externo ter
sido lido uma vez, e o tamanho do dataset; nao a ausencia de ajuste.

**O padrao, e o limite dele.** O deficit de regiao encolhe com o tamanho do dataset — Alabama
(1 101 usuarios) −0,95, Arizona (2 136) −0,47, Istambul (14 530) −0,15. Com tres datasets e o
confundimento tamanho×dataset, o proprio protocolo proibe promover isso a achado. E observacao.

---

## 5 · [N3] As correcoes de abordagem estatistica

Seis erros de protocolo, cada um medido, cada um com o conserto em codigo. O guia completo esta em
`docs/EVALUATION_METHOD_GUIDE.md`; a especificacao congelada em `docs/plans/EVALUATION_PROTOCOL.md`.

### 5.1 · A epoca era escolhida no mesmo conjunto que reportava o numero

O protocolo antigo treinava em 80 % e usava os 20 % de fora para **as duas coisas**: escolher a epoca
e reportar o resultado. O novo particiona os usuarios em tres blocos disjuntos por fold — 70 % treino,
10 % validacao interna, 20 % teste externo — e o teste externo e lido **uma vez por braco, por ciclo
de congelamento**, depois de todas as decisoes.

A leitura direta em Alabama/regiao mostra os tres numeros lado a lado, e so um e resultado:

| leitura | protocolo | Acc@10 | e resultado? |
|---|---|--:|---|
| plano, seleciona e reporta no mesmo conjunto | antigo | 70,05 | e o que o sistema antigo reportava |
| aninhado, validacao interna | novo | 73,72 | **nao** — serve para escolher a epoca |
| aninhado, teste externo lido uma vez | novo | **69,01** | **sim** |

**O numero mais limpo e 3,67 pp**, entre a primeira e a segunda linha. Nove vezes a margem: ler uma
tabela contra a outra nao produz erro de arredondamento, produz conclusao invertida.

⚠ **"Mais limpo" nao e "limpo".** Entre essas duas linhas o protocolo e o que mais muda, mas nao e a
unica coisa: mudam tambem a populacao avaliada, a fracao de treino e a contagem de replicas. Nenhuma
das tres cifras desta secao isola um so fator.

⚠ **O tamanho exato do otimismo de selecao ainda nao foi medido, e a frase oral precisa dizer isso.**
Ha tres cifras circulando e elas nao tem o mesmo peso:

| cifra | o que e | como citar |
|---|---|---|
| **3,67 pp** | o protocolo e o que mais muda (com populacao, fracao de treino e replicas junto) | medido, o mais limpo dos tres |
| **~1 pp** | 69,01 selado contra 70,05 plano; protocolo **e** convencao de agregacao mudam juntos | ordem de grandeza |
| **~0,66 pp** | **um fold de Alabama** | **sugestivo, nunca "medido"** |

O ~0,66 pp nasceu como *"a single Alabama fold already suggests ~0.66 pp"* no manifesto da leitura
selada, e virou "the measured optimism" em cinco pontos do codigo do repo novo. E exagero de
citacao, corrigido em 2026-08-20.

**A resposta honesta hoje**, se a banca perguntar quanto valia exatamente a regra antiga: *"temos uma
sugestao de um fold, e o instrumento pronto para medir direito."* O instrumento existe
(`src/mtlcheck/eval/optimism.py`, dez testes passando): ele decompoe a diferenca em otimismo da regra
legada e custo de comprometer-se com um checkpoint unico, co-registrados na mesma trajetoria. Nunca
rodou porque exige reter checkpoints por epoca, e o padrao e nao reter. E o primeiro item do plano de
melhorias — e a mesma medicao que fecharia a secao 10.2.

**Simetria de selecao.** O protocolo novo exige que **todo** braco use o mesmo contrato. Se o braco
dedicado pudesse colher a melhor epoca de cada tarefa e o conjunto fosse obrigado a um checkpoint
so, a comparacao principal do trabalho ficaria estruturalmente enviesada contra o conjunto.

### 5.2 · A metrica era a media dos folds, e nao devia ser

O antigo calculava macro-F1 fold a fold e tirava a media dos cinco. O novo junta as predicoes
out-of-fold dos cinco folds e calcula a metrica **uma vez** sobre o conjunto agregado. Sob
desbalanceamento de classe os dois estimadores nao coincidem: o vies da media-de-folds foi medido em
**−0,24 pp** na estrutura de Alabama, mais da metade da margem de 0,4.

### 5.3 · O `n` do teste era o numero errado

A inferencia foi separada em dois niveis, e todo numero publicado tem de dizer a qual pertence:

- **Tier A — generalizacao de usuario.** Bootstrap pareado em cluster de **usuario** sobre as
  predicoes agregadas, 10 000 replicas, intervalo BCa, e permutacao sign-flip **estudentizada** para
  superioridade. E este nivel que sustenta toda alegacao-manchete.
- **Tier B — comparacao condicional.** Delta pareado por repeticao, com banda sobre o desvio entre
  repeticoes. Resolve efeitos de 0,05 a 0,15 pp, mas nunca e citado como intervalo de generalizacao.

A regra que fecha o buraco antigo: os cinco folds de uma repeticao compartilham 75 a 80 % dos dados
de treino, entao **nao sao cinco replicas independentes**. O `n` do Tier B e o numero de repeticoes,
nunca repeticoes × folds. O `n` do Tier A e o numero de usuarios, nunca o de janelas.

### 5.4 · A margem passou a ser derivada, nao escolhida

δ = 0,4 pp sai de tres pisos, em ordem, e nenhum depende de um delta A-contra-B:

1. **decidibilidade** — o topo da banda de ruido entre repeticoes pareadas e 0,15 pp, entao δ ≥ 0,3;
2. **reinstanciacao** — reconstruir a mesma configuracao do zero move o numero em ~0,18 pp, e o dobro
   disso e ~0,4;
3. **teto externo** — 0,4 ainda e mais estrito que a regiao de equivalencia da ordem de 1 pp usada
   como exemplo comum na literatura de comparacao de classificadores.

Todo veredito de equivalencia e reapresentado em δ ∈ {0,2; 0,4; 1,0} pp, para o leitor ver onde a
decisao mudaria.

### 5.5 · A ordem dos testes foi fixada

Para cada par (dataset, tarefa): primeiro nao-inferioridade por TOST, e superioridade **so se** a
primeira passar; Holm na familia manchete. As quatro saidas possiveis — inferior, inconclusivo,
nao-inferior, superior — sao distintas, e "inconclusivo" nunca colapsa em "nao-inferior". Onde a
superioridade e significativa mas o efeito e menor que δ, a regra obriga a frase completa:
*"significativo, e dentro da margem pratica pre-registrada"*.

### 5.6 · Tres regras pre-registradas nao existiam em codigo

Achado por auditoria adversarial em 2026-08-19, implementado no mesmo dia, e aplicado
**retroativamente** a leitura selada. **Nenhum dos seis vereditos muda** — e por isso o registro e um
adendo datado, e nao uma edicao silenciosa:

| regra | onde estava | efeito nos seis vereditos |
|---|---|---|
| piso de re-execucao (\|Δ\| ≤ 0,05 pp nunca e reivindicado) | em lugar nenhum | nenhum: o menor \|Δ\| e 0,120, 2,4× o piso |
| gate de permutacao (superioridade exige NI **e** permutacao) | o veredito so olhava o intervalo | nenhum: o unico "superior" passa com p = 0,0032 |
| canario de vazamento (`ood_hit_rate > 1 %` reprova a execucao) | codigo morto, um unico chamador | nenhum: **60 folds, zero disparos** |

O canario merece uma frase propria porque e evidencia positiva, nao ausencia de alarme: com 1,1 % das
linhas de Alabama fora de distribuicao, havia oportunidade de sobra para disparar, e o valor medido
foi **exatamente 0,00000** nos sessenta folds.

### 5.7 · "Semente" era um botao so, e sao dois

`--split-seed` reparticiona, `--seed` reinicializa o modelo. No sistema antigo um unico inteiro
governava os dois, e "repeticao" e "replica" eram inseparaveis — um numero movia dois fatores
experimentais ao mesmo tempo. Fonte: `docs/NOMENCLATURE.md`.

---

## 6 · [N4] As correcoes no Check2HGI

### 6.1 · Corrigidas porque eram bugs do porte

Nenhuma delas e ganho sobre a dissertacao. O deficit de −0,9 pp em regiao que a validacao encontrou
foi rastreado ate ser **do construtor, nao do sorteio** (quatro sorteios de substrato, desvio 0,034
contra distancia 0,78) e dai ate tres divergencias do POI2Vec, atribuidas uma a uma:

| divergencia | ganho |
|---|--:|
| negativos amostrados uniformemente em vez de por co-ocorrencia | **+0,563 pp** |
| regularizador de hierarquia ausente (era puxao global para zero) | **+0,282 pp** |
| objetivo por par em vez de por janela | +0,012 pp (ruido) |

Regiao saiu de 73,84 para 74,70 contra o incumbente de 74,64. **Isso e paridade.**

O grafo de Delaunay tambem fechou, e e a primeira parte do substrato a reproduzir o artefato bancado
**bit a bit**: 35 519 arestas, orientacao identica, zero invertidas.

### 6.2 · Corrigidas porque eram defeitos da referencia

| o que a referencia fazia | o que o mtlcheck faz |
|---|---|
| POI2Vec **sem semente nenhuma** — nao reproduz nem a si mesmo | semeado, com kernel de caminhada proprio (o do `torch_cluster` ignora `torch.manual_seed`) |
| lugares fora de todo poligono descartados em silencio por um inner join | contados e logados. O contrapeso honesto: nos dois datasets medidos o descarte foi **zero** — Alabama tem 11 848 lugares sobre 1 109 tracts e nenhum fora. Risco real, dano nao observado |
| um lugar que cruza dois tracts virava duas linhas, com dois vertices de Delaunay | vira uma linha |
| dois substratos por dataset: a torre de regiao lia um substrato bidirecional separado, que entrava por symlink | **um substrato so** (v19), a torre de regiao le o mesmo forward-only. Autorizado por medicao **antes** de deletar: efeito do grafo +0,122 pp, erro-padrao 0,108, indistinguivel de zero |
| o substrato nao e reproduzivel nem contra ele mesmo | determinismo ligado por padrao, custo +12,5 % de tempo |

Duas delas rendem pergunta de banca e a resposta e melhor do que parece:

**O objetivo do substrato mudava com o tamanho do dataset, sem registro.** No amostrador de negativos
POI↔regiao, 25 % dos negativos vem de uma banda de similaridade — mas **o ramo inteiro era ignorado
em datasets com 50 000 lugares ou mais**. Medido nos grafos congelados: AL, AZ e Istambul **com**
negativo duro; FL, CA e TX **sem**. O corte separa exatamente o mesmo agrupamento pequeno/grande sobre
o qual os resultados sao comparados. Isso nao invalida numero nenhum — todos os substratos foram
construidos sob a mesma regra — mas invalida a frase "o mesmo substrato foi construido em todos os
datasets". O mtlcheck removeu a causa em vez do sintoma: o sorteio foi vetorizado (3,1 s por epoca na
California viraram 0,11 ms), e sem laco nao ha motivo para o corte.

**A leitura assustadora foi medida, e caiu.** A duvida natural aqui e "entao 'datasets grandes tem
regiao pior' pode ser efeito do negativo duro desligado, e nao do tamanho". Florida foi construida
**nas duas configuracoes** — 76 544 lugares, acima do corte como California e Texas, mas dataset de
desenvolvimento, entao medir nao custa reserva:

| celula | com negativo duro | sem | delta | erro-padrao |
|---|--:|--:|--:|--:|
| categoria dedicada | 38,6722 | 38,6856 | −0,013 | 0,019 |
| regiao dedicada | 76,1414 | 76,1089 | +0,033 | 0,045 |
| conjunto, categoria | 38,7767 | 38,7639 | +0,013 | 0,019 |
| conjunto, regiao | 76,4152 | 76,3937 | +0,022 | 0,049 |

Os quatro deltas ficam dentro do erro-padrao e abaixo do piso de 0,034 pp. **Ligar ou desligar o
negativo duro num dataset grande nao move nada mensuravel.** O defeito continua real como variavel
confundida que nao foi registrada em lugar nenhum; o efeito dele, onde deu para medir, e nulo.

⚠ Uma semente, validacao interna, um dataset. E o suficiente para tirar a leitura assustadora da mesa,
nao para afirmar que o efeito e zero em California e Texas.

⚠ **E isso corta nos dois sentidos, o que e a metade que quase ficou de fora.** Alabama, Arizona e
Istambul tem 11 848, 20 666 e 29 816 lugares, todos **abaixo** do corte, entao ali os dois objetivos
coincidem — e por isso a divergencia nunca apareceu em nada que foi rodado ate hoje. Ela so morde em
Florida, California e Texas, onde a dissertacao construiu o substrato com o negativo duro
**desligado** e o mtlcheck o constroi **ligado**. Pela regra da secao 2, isso e uma **melhoria real**:
os substratos grandes do repo novo **nao sao comparaveis celula a celula** com a tabela da
dissertacao sem declarar a mudanca, e quem comparar os tres grandes carrega o objetivo do pretexto
como uma variavel a mais. A receita do repo novo passou a declarar o valor explicitamente
(`p2r_hard_neg_size_gate = 50000` restaura a divisao da dissertacao). California e Texas sao
os dois datasets que menos receberam ajuste (secao 10.7), o que torna a declaracao mais do que uma
formalidade.

**A referencia nao reproduz o proprio substrato.** Duas execucoes, mesma semente, mesma maquina,
mesmo codigo: melhor loss 0,2236 contra 0,2321, com as curvas divergindo na quinta epoca. A causa sao
os `scatter`/`index_add_` de cada forward, cujos atomicos de CUDA somam floats em ordem nao
deterministica. **Consequencia que importa:** um substrato bancado e *uma amostra*, nao uma funcao da
semente, e "reconstruir o substrato com a mesma semente" nao e uma instrucao executavel — nem pela
referencia. Isso nao invalida os resultados: os artefatos existem, foram usados, e todas as
comparacoes a jusante foram feitas sobre os **mesmos arquivos**. O que cai e a possibilidade de
regenera-los. O mtlcheck liga `torch.use_deterministic_algorithms`, e por isso um build feito hoje
pode ser refeito amanha.

Esse mesmo fato deu a calibracao que faltava para validar a reescrita: a distancia entre as duas
implementacoes e comparada contra **o desacordo da referencia consigo mesma**, nao contra zero. Com
cinco builds de cada lado, a distribuicao cruzada cai sobre os pisos proprios nos tres niveis.

### 6.3 · Reproduzidas de proposito, porque corrigir tornaria a dissertacao irreproduzivel

Estas a banca pode perguntar, e a resposta honesta e "sim, esta errado, e mantivemos de proposito,
porque foi isso que produziu todo artefato bancado":

- **descasamento de unidades no peso da aresta de Delaunay** — `D` em graus contra distancia em
  metros, o que torna o logaritmo negativo em **98,56 %** das arestas e faz a penalidade de cruzar
  regiao virar **bonus**. O conserto existe no codigo, desligado.
- **`mae_poi_target_dim = 8`** — a coluna 7 do alvo de reconstrucao e a media de `hour_sin` do lugar,
  nao uma categoria. Cosseno 0,8785 contra o alvo pretendido. Veredito registrado: **corrigir**, na
  proxima versao de receita.
- **o regularizador de hierarquia indexa a tabela de `fclass` com codigo de categoria** — so e
  inofensivo porque ha 7 categorias contra 284 fclasses.
- **o POI2Vec caminha o grafo dirigido**, que nao e o node2vec padrao. O conserto existe, desligado.

---

## 7 · [N5] As correcoes no modelo e no treino

O ledger completo e `docs/REFERENCE_DEFECTS.md`, R1 a R16. Os que rendem pergunta:

| # | o defeito | afeta numero bancado? |
|---|---|---|
| R1 | o trio de taxas de aprendizado por cabeca so era ativado por variavel de ambiente; sem ela, a execucao virava silenciosamente a receita anterior | nao — todos os drivers exportavam a variavel |
| R2 | a precisao de uma execucao sem flags dependia do dataset (fp16 ou fp32 conforme a cardinalidade de regioes) | nao — as celulas fixavam a precisao |
| R3 | um `export` em funcao de shell vazava entre celulas | **sim, numa leva descartada** — 8 de 10 celulas de categoria rodaram fp16 enquanto o arquivo de proveniencia afirmava fp32. Corrigido a montante em 2026-08-09; as celulas afetadas sairam do board |
| R5 | o loader conjunto duplicava linhas quando os dois fluxos tinham tamanhos diferentes, super-ponderando um subconjunto da validacao | nao — no par de tarefas do check2hgi as duas tarefas indexam as mesmas linhas |
| R6 | o prior desligado ainda alocava um tensor `[C,C]` de zeros (289 MB na California) e executava a multiplicacao por zero a cada forward | nao — aritmeticamente identico |
| R9 | o `n` da tabela de resultados era lido do campo de categoria, entao em TX e CA o `n` publicado nao valia para a coluna de regiao | **sim, na apresentacao** — um `n` errado ao lado de um `p` muda como o leitor pesa o resultado. Corrigido a montante em 2026-08-11 |
| R10 | um scorer era chamado com falha suprimida, e por isso uma lane inteira de resultados ficou vazia sem ninguem notar | nao os que existem — impediu que uma coluna existisse |
| R11 | o pooling do ultimo passo valido assumia empacotamento a esquerda | nao — no stride 1 nao ha padding |
| R12 | a torre privada era preenchida com zeros quando sua entrada faltava, em vez de falhar | nao — a entrada sempre chegava |
| R13 | o guard de memoria exigia 16 GB livres fixos, sem relacao com o tamanho do dado: calculava corretamente que precisava de 0,4 GB e recusava assim mesmo | nao — mas impedia qualquer reproducao fora do servidor |

O padrao que atravessa a lista, e que e a resposta de fundo: **quase nenhum deles atingiu um numero
publicado, e varios so nao atingiram por sorte.** Uma mudanca de artefato ativaria metade em silencio.
O mtlcheck troca cada um por um erro explicito — configuracao invalida nao constroi, entrada ausente
levanta excecao, precisao indisponivel e recusada em vez de rebaixada.

Alem do ledger, tres mudancas estruturais:

- **nenhuma variavel de ambiente decide ciencia.** As tres lidas sao de caminho e nenhuma pode mudar
  um numero. O sistema antigo roteava cerca de 25 variaveis para decisoes cientificas.
- **tres copias do laco de validacao viraram uma.** No repo antigo uma delas ficou dois meses atras
  das correcoes, servindo pontuacao em CPU.
- **toda celula citavel sai de um manifesto declarativo**, executado pelo pacote, com o substrato que
  ela leu carimbado no resultado e recusado no consumo quando nao bate.

---

## 8 · [N6] O limite que o repo novo declara com mais franqueza que a dissertacao

Se houver **uma** pergunta que a banca faca e que merece a resposta ja pronta, e esta.

**O forward-only nao torna o substrato causal.** Ele fecha o canal linha a linha, e isso vale — o
canal fechado valia **28,63 pp de macro-F1**. Mas o substrato continua sendo treinado **uma vez sobre
o corpus inteiro, sem split de fold**. Logo, toda linha do teste esteve no treino do pretexto. Alem
disso: o `Checkin2POI` agrupa visitas futuras, o alvo de reconstrucao e a distribuicao de categorias
do corpus todo, a normalizacao min-max do peso de aresta e ajustada no corpus inteiro, e os grafos de
Delaunay e de adjacencia de regiao nao sao tocados.

Fonte: `docs/SYSTEM_MAP.md` D8.

**O que isso invalida:** a leitura de que o sistema e causal em tudo. **O que nao invalida:** nada dos
resultados — o desenho e transdutivo, foi transdutivo em toda celula, e o e por construcao do
substrato, nao por descuido de split. Os splits de treino/validacao/teste continuam disjuntos por
usuario, e o canario de vazamento da zero.

**A frase defensavel:** *"o substrato e transdutivo por construcao, e o texto nao deve dizer que ele e
causal. O que o forward-only garante e que a representacao de uma visita nao ve as visitas seguintes
daquele usuario, e isso vale 28,63 pontos de macro-F1. A representacao ver a estatistica global do
corpus e uma propriedade do aprendizado auto-supervisionado sobre grafo, nao um vazamento de rotulo:
os rotulos de teste nunca entram, e o canario de fora-de-distribuicao deu exatamente zero em sessenta
folds."*

Isto vale para a dissertacao tambem. **Nao e regressao; e honestidade nova.**

---

## 9 · [N7, N8, N9] O que a banca vai perguntar, e onde a reescrita responde melhor

| pergunta | resposta curta | onde |
|---|---|---|
| **N7** · "Voces escolheram a epoca no mesmo conjunto que reportam?" | No sistema antigo, sim. O protocolo novo separa os dois conjuntos e o teste externo e lido uma vez, por ato datado. Quanto isso valia: entre os dois protocolos a distancia medida e 3,67 pp em AL/regiao; o otimismo de selecao isolado ainda **nao** foi medido, so sugerido por um fold, e o instrumento esta pronto | secao 5.1 |
| **N7** · "Quantas vezes voces olharam o conjunto de teste?" | Ha registro. Pontuar e um comando separado e datado; as predicoes ficam em disco, so o escore e racionado. AL/AZ/Istambul tiveram o teste externo lido em 2026-08-18; CA e TX ainda nao, embora tenham sido usados para busca de hiperparametro antes deste protocolo (secao 10.7) | `SEALED_BRIDGE_READ.md` |
| **N7** · "Como voces sabem que os folds sao os mesmos?" | Hash. Na paridade de regiao os cinco hashes de fold batem exatamente com os da referencia | `waves/ref_parity_al.toml` |
| **N8** · "O que e `n` no seu teste?" | Usuario, no Tier A. Janelas superestimariam, porque as janelas de um usuario nao sao independentes; folds tambem, porque compartilham 75 a 80 % do treino | secao 5.3 |
| **N8** · "Por que uma margem de dois pontos?" | E declarada, derivada do servico, e o proprio texto diz que Alabama e o dataset que ela menos sustenta. A analise nova usa 0,4 pp e muda o veredito daquela celula | secao 4 |
| **N9** · "E se o experimento nao for reproduzivel?" | A **referencia** nao reproduz a si mesma: dois builds, mesma semente, mesma maquina, loss 0,2236 contra 0,2321. Isso e medido e declarado, e a reescrita e validada contra esse piso, nao contra zero | secao 6.2 |
| **N9** · "Por que o modelo conjunto nao perde em regiao no Istambul?" | O deficit encolhe com o tamanho do dataset. Com tres datasets e o confundimento tamanho×dataset, isso e observacao, e o protocolo proibe promover a achado | secao 4 |
| **N9** · "Que garantia voces tem de que o codigo faz o que o texto diz?" | Uma auditoria adversarial de 49 agentes, que achou 31 problemas confirmados e esta documentada com os erros dentro | secao 10.3 |

---

## 10 · O que ainda esta aberto, dito abertamente

### 10.1 · A contagem de usuarios da tabela de datasets [decisao do autor]

> **RESOLVIDO 2026-09-01** (anotado aqui a 2026-10-02). A saida escolhida foi a clausula na legenda: a
> tabela de datasets do Cap. 5 diz agora que check-ins, usuarios e POIs sao contagens do corpus
> inteiro, **antes** do filtro de dez visitas, e que a coluna de janelas e calculada **depois** dele.
> Commit `e1f9b8c0`; registo na tabela do §1.2 do `CLAUDE.md` (linha "Table 8") e uma linha da
> Tabela B.5 do suplemento. Nenhum numero mudou.

A Tabela de estatisticas dos datasets publica **3 858 usuarios** para Alabama, **7 869** para Arizona e
**23 694** para Istambul. O mtlcheck, contando sobre o substrato v18, encontra **1 101**, **2 136** e
**14 530** usuarios efetivamente presentes nas predicoes agregadas.

A coluna de janelas bate exatamente nos tres (96 326, 200 895, 271 666), o que diz que e o mesmo
substrato. **A reconciliacao esta verificada no corpus bruto**, e nao inferida: uma contagem direta
sobre `data/checkins/{Alabama,Arizona}.parquet` da, em Alabama, 113 846 check-ins, **3 858 usuarios**
e **11 848 lugares**; em Arizona, 236 450, **7 869** e **20 666**. Sao exatamente os tres numeros que
a tabela publica, ao caractere, nas tres colunas e nos dois datasets. Entao:

| coluna da tabela | populacao |
|---|---|
| check-ins | corpus bruto |
| usuarios | corpus bruto |
| lugares | corpus bruto |
| janelas | **pos-filtro** de comprimento minimo de dez check-ins, stride 1 |

Tres colunas de corpus e uma de experimento, na mesma linha, com uma legenda que nao distingue.
A fronteira e limpa: **so a coluna de janelas atravessa o filtro.** A aritmetica fecha nos dois
sentidos: em Alabama, os 1 101 usuarios que qualificam somam 106 235 check-ins dos 113 846 do corpus, sobrando
7 611 para os 2 757 que nao qualificam — cerca de 2,8 check-ins cada, coerente com usuarios curtos.

**Onde a verificacao para.** Isto estabelece a que populacao a coluna **corresponde**, nao o que ela
**pretendia** reportar. Se a intencao era o pos-filtro, e erro de extracao; se era o bruto, e a
legenda que falta. Os dados nao distinguem os dois casos. Como esta, um arguidor que pergunte
"quantos usuarios entram no seu teste?" recebe 3 858 quando o numero certo e 1 101.

**Um efeito colateral que ja foi verificado, e que sobrevive.** O mesmo 3 858 foi herdado pela
projecao de piso de reamostragem do protocolo novo, que previa ~0,25 a 0,3 pp de meia-largura em
Alabama. O piso realmente medido ficou em **0,199 a 0,222 pp** — melhor que a projecao, apesar de ela
ter partido de um `n` 3,5 vezes maior que o real. A conclusao dessa projecao (existe um piso, e
Alabama e o dataset mais apertado) sobrevive; o numero que a sustentava, nao.

**Custo de cada saida.** Uma clausula na legenda ("usuarios do corpus; as janelas sao posteriores ao
filtro de comprimento minimo") resolve sem tocar em nenhum numero. Uma linha de errata resolve
tambem. Nao mexer significa aceitar a ambiguidade em voz alta.

### 10.2 · O delta de Alabama/regiao mede duas coisas somadas

O −0,953 da secao 4 nao e "o custo da multi-tarefa". O braco dedicado e lido na epoca que a validacao
interna **daquela tarefa** escolheu; o braco conjunto e lido na unica epoca escolhida pelo escore
conjunto. Entao:

> delta medido = (interferencia entre tarefas) + (custo de comprometer-se com um checkpoint unico)

e a assimetria **corre contra o braco conjunto**. Os dois termos nao sao separaveis com o que esta
bancado — separar exige pontuar checkpoints por epoca retidos, que e trabalho em fila. Ate la, a
frase defensavel e *"o checkpoint conjunto unico entrega X pp a menos que dois modelos dedicados,
cada um no seu melhor"*, e **nao** *"a multi-tarefa custa X pp"*.

O instrumento que separa os dois nao produz um numero, produz **dois**, e o protocolo proibe soma-los:

| cifra | o que mede |
|---|---|
| otimismo de selecao | o que a regra antiga ganhava so por poder escolher a epoca olhando o resultado |
| custo de checkpoint unico | o que se paga por entregar **um** modelo em vez de um por tarefa |

**So o segundo e uma propriedade do modelo conjunto.** O primeiro e uma propriedade do protocolo, e
seria pago por qualquer braco lido sob a regra antiga. Se a banca perguntar quanto a multi-tarefa
custa, a resposta honesta hoje e que a medicao que separa as duas coisas esta pronta e nao rodou.

Vale notar que isto e a mesma convencao restritiva que o Capitulo 5 ja adota e ja declara — a
reescrita nao introduziu a assimetria, ela mediu o tamanho dela.

### 10.3 · A auditoria, e por que ela e um ativo e nao um passivo

O porte passou por uma auditoria adversarial de 49 agentes em seis dimensoes independentes, cada
achado atacado por um cetico antes de contar. Trinta e um problemas confirmados. Os tres que mais
importam, e que estao documentados **com o erro dentro**:

1. a suite estava rodando com uma mascara que escondia oito falhas;
2. um commit capturou seis mutacoes de auditoria em `src/` **sem o pytest mover um numero** — o que
   provou, de uma vez, que a suite era cega ao que importava;
3. um arquivo de evidencia contradizia em varias ordens de grandeza a paridade que deveria provar.

Todos enderecados, com testes de fiacao que agora quebram sob aquelas seis mutacoes, ambiente pinado
e CI. Pelo menos um achado da auditoria foi **refutado** por um advisor independente, e isso tambem
esta registrado.

**Por que isto se conta na defesa em vez de se esconder:** um registro que admite os proprios
quase-acidentes e mais convincente que uma alegacao de que nao houve nenhum. A pergunta "como voces
sabem que o codigo faz o que o texto diz?" tem, aqui, uma resposta com nome de arquivo.

E ha um caso que fecha o argumento melhor que a auditoria, porque aconteceu **enquanto este
documento era escrito**. A cifra de otimismo de selecao da secao 5.1 estava citada em cinco pontos do
codigo do repo novo como "the measured optimism"; a origem era uma frase de manifesto que dizia
*sugere*, sobre **um** fold. Perguntar de onde vinha o numero bastou para derrubar a alegacao, e os
cinco sitios foram corrigidos no mesmo dia. O caso ficou registrado como uma secao propria do
registro de divergencias, porque e exatamente a classe que aquele documento existe para impedir —
alegacao acima da evidencia — virada para dentro do proprio repositorio.

Isso e o enquadramento mais forte que o trabalho de reescrita oferece: **o projeto tem um mecanismo
escrito para separar alegacao de evidencia, e o mecanismo pegou o proprio projeto.** Nao muda numero
nenhum. Muda o que se pode afirmar, que e o ponto.

### 10.4 · O que ainda nao foi medido

- **paridade do modelo conjunto.** As capacidades conferem, incluindo o total de 4 197 621 pelo
  caminho da receita, e o transplante de pesos da `max|Δ| = 0` nas duas cabecas. Mas a paridade
  celula a celula foi interrompida por decisao do autor: com o protocolo de avaliacao mudado, ela
  mediria o porte e o protocolo ao mesmo tempo.
- **o vies assimetrico em regiao.** Na secao 3, o dedicado fica **abaixo** da dissertacao e o conjunto
  **acima**, nos dois datasets. Isso **encolhe** o gap conjunto-contra-dedicado, ou seja, aqui a
  multi-tarefa custaria menos em regiao do que a dissertacao reporta. Com uma semente nao e afirmavel.
- **a dispersao entre folds da categoria no Arizona** e 2,26 contra 0,66 em Alabama e 0,50 em
  Istambul. Nao e a taxa de aprendizado, nao e a particao, e reproduz entre execucoes independentes.
  Continua aberta — **nao afirme nada sobre ela**.
- **a leitura selada de 2026-08-18 descreve uma configuracao superada**: o substrato foi unificado e o
  POI2Vec corrigido no dia seguinte. O primeiro ciclo de congelamento foi gasto numa receita que
  durou um dia. CA e TX sao os dois datasets cujo teste externo ainda nao foi lido, o que os torna o
  ativo mais proximo de uma reserva que ainda existe — com a ressalva da secao 10.7.

---

### 10.5 · O prazo de validade deste registro

A secao 3 e a mais util deste documento e a que envelhece primeiro. Ela mede o estado do repo novo
em 2026-08-21, e **toda melhoria da fila reconstroi o substrato**. Quatro execucoes a invalidam, e
nenhuma foi aplicada:

| o que executar | estado em 21-08 | o que muda aqui |
|---|---|---|
| corrigir a coluna 7 do alvo de reconstrucao (`mae_poi_target_dim` 8→7) | veredito **corrigir**, nao aplicado | a paridade da secao 3. Medido em +0,116 pp categoria / −0,053 regiao, uma semente |
| o fatorial unidades do Delaunay × simetrizacao do POI2Vec | **medido** (ver abaixo) | nada por enquanto: nao foi aplicado, e em regiao nao resolveu |
| congelar a proxima versao de receita | **decisao futura do autor** | a linha de base inteira. Todo numero dela e "melhoria real" pela regra da secao 2, com a comparabilidade quebrada por declaracao |
| rodar a decomposicao do §8a | pendente | a secao 5.1 e a secao 10.2 — troca "sugerido por um fold" por duas medicoes, que o protocolo proibe somar |

**O fatorial rodou, e o resultado desarma o item que era o mais perigoso da lista.** Contra o
erro-padrao pareado — e nao contra o piso de sorteio de substrato, que e o denominador errado para
um delta pareado:

| lever | regiao | categoria |
|---|---|---|
| correcao de unidades do Delaunay | −0,178 (1,09 ep) — **nao resolvido** | +0,141 (2,39 ep) — resolvido |
| simetrizacao do POI2Vec | +0,162 (1,21 ep) — **nao resolvido** | +0,170 (2,98 ep) — resolvido |
| os dois juntos | +0,073 (0,40 ep) | +0,116 (1,07 ep) — **nao resolvido** |

**Em regiao nada e resolvido**, apesar de a correcao de unidades redefinir o peso de 98,56 % das
arestas. Em categoria os tres efeitos sao reais, e a combinacao e **menor que cada um sozinho**: os
dois levers interferem, e empilha-los nao soma. O candidato limpo e a simetrizacao. Nada disso foi
aplicado, entao a secao 3 continua valendo.

O aviso reciproco esta registrado no lado que causa a mudanca, e nao so nesta pasta: o
`studies/improvements/STUDY.md` do repo novo carrega a mesma tabela, com o caminho deste arquivo.
Uma dependencia entre repositorios que vive so numa conversa morre com a conversa.

**Havia uma decisao com prazo mais curto que as quatro, e ela foi fechada por medicao.** O conserto
do negativo duro transferia uma escolha para o primeiro build de California e Texas — o corte da
referencia, que preservaria a comparabilidade celula a celula, ou o objetivo unico. Era a unica da
lista cujo custo de errar nao era re-medir. **A medicao em Florida (secao 6.2) mostrou que a escolha
nao move nada mensuravel**, entao ela deixou de ser um trade-off: fica o objetivo unico, e o custo
declarado da secao 6.2 e menor do que parecia.

**Se alguma das quatro tiver rodado quando este documento for lido, a secao 3 precisa ser
re-executada antes de ser citada em voz alta.** As demais secoes nao dependem disso: as correcoes,
os defeitos reproduzidos, o limite do substrato e as perguntas de banca continuam valendo, porque
descrevem o que foi encontrado, nao o numero que estava na tela.

### 10.6 · A contagem de parametros do controle de capacidade [decisao do autor]

> **RESOLVIDO 2026-09-02** (anotado aqui a 2026-10-02). As contagens foram corrigidas nos dois
> volumes: o Apendice G do suplemento imprime 1.433.863 / 9.634.471 (229,5 %) / 12.044.791
> (233,8 %), e as duas somas do volume principal passaram de 1,1 / 2,0 para 1,9 / 2,8 milhoes.
> Reproduzivel sem GPU por `research/reproducibility/mobiwac_v18/param_counts.py`. Registo: `CLAUDE.md`
> §5, armadilha 6. O texto abaixo e o diagnostico de antes da correcao.

Este e o unico item do ledger de defeitos que toca um numero **ja escrito no material de defesa**, e
por isso ele nao pertence a lista de execucoes futuras: ele ja esta na pagina.

O apendice do controle de contagem de parametros, no volume suplementar desta pasta
(`material_extra/chapters/apx_i_parameter_count_control.tex`), afirma que os modelos dedicados
alargados alcancam **100,2 % e 101,9 %** do orcamento do modelo conjunto, *"so they do not receive a
smaller parameter budget"*, e publica a tabela:

| dataset | conjunto | dedicado original | dedicado alargado |
|---|--:|--:|--:|
| Alabama | 4 197 621 | 644 359 | 4 207 399 (h=672) |
| California | 5 151 189 | 644 359 | 5 249 719 (h=752) |

**O apendice nao errou as larguras. Contou as tres pela profundidade errada.** Os seis numeros saem
de **um mecanismo so**, e a recontagem contra uma implementacao independente da cabeca de categoria
da **diferenca zero** nos seis:

| largura | publicado (2 camadas) | o que rodou (4 camadas) |
|---|--:|--:|
| 256, dedicado original | 644 359 | **1 433 863** |
| 672, alargado em Alabama | 4 207 399 (**100,2 %** do conjunto) | **9 634 471** (**230 %**) |
| 752, alargado em California | 5 249 719 (**101,9 %** do conjunto) | **12 044 791** (**234 %**) |

A causa: a auditoria construiu as cabecas pelos defaults do modulo (2 camadas); a celula que executou
herda `num_layers=4` da fabrica de configuracao, e a flag de largura **mescla** sobre esse dicionario
em vez de substitui-lo. Cada valor da coluna do meio e a mesma largura contada com duas camadas;
cada valor da coluna da direita e a mesma largura com quatro.

**A conclusao do controle nao cai. Ela fica mais forte.** O braco alargado nao foi equiparado em
capacidade: recebeu **mais que o dobro** do orcamento do conjunto e ainda assim ficou abaixo do
modelo estreito. O argumento sai de *"damos ao dedicado o orcamento do conjunto e ele nao
recupera"* para *"damos a ele mais que o dobro e ele nao recupera"*. Sobrevive tambem a razao contra
o modelo original (6,5 e 8,1 vezes viram 6,7 e 8,4), porque as duas pontas foram contadas pela mesma
profundidade errada e a largura domina.

**O que nao sobrevive** sao os dois rotulos: "100,2 % / 101,9 % equiparado" e a leitura de que o
controle quadruplica os parametros do dedicado.

**Onde a verificacao para.** Isto identifica **qual configuracao gerou cada numero**, o que e mais
forte que constatar que eles diferem — e mais forte que ler o artefato da execucao, porque explica os
seis de uma vez. O que ainda nao foi lido e o artefato de arquitetura daqueles rundirs, que vive na
maquina remota. Tambem nao verifiquei se a auditoria quis dizer outra coisa por "dedicado original";
mas o proprio documento de auditoria afirma reproduzir a citacao do artigo, e essa citacao e sobre os
modelos dedicados da tabela principal, que sao os de quatro camadas.

**A verificacao vizinha foi feita, e o controle de regiao passa.** O estudo `P1_capacity_region.md`
desta mesma pasta faz um controle de capacidade **no eixo de regiao**, com a mesma forma de alegacao
("pareado"), e por isso a duvida era legitima. As tres contagens da curva de largura foram
recontadas contra uma **reimplementacao independente** da cabeca de regiao, em California:

| largura | recontado | publicado em P1 |
|---|--:|--:|
| 256 | 3 256 509 | 3 256 510 |
| 352 | 5 014 941 | 5 014 942 |
| 528 | 9 004 685 | 9 004 686 |

**Um** parametro de diferenca nas tres, e ele e explicado: o escalar do prior de trajetoria, que a
referencia instancia e o repo novo omite por desenho (o item R6 da secao 7 — prior inativo e ramo
ausente, nao multiplicacao por zero). Nao e folga; e uma diferenca conhecida, do tamanho certo, e
constante.

⚠ **O limite dessa verificacao, com a forca certa.** Ela confirma que os numeros publicados sao os da
arquitetura que o documento **nomeia**. Nao confirma que as execucoes usaram essa configuracao — para
isso e preciso ler os `arch.txt` daqueles rundirs, que vivem na maquina remota. Mas o defeito da
secao 10.6 falhou **justamente nessa primeira etapa**: o 644 359 era o build pelos defaults do
modulo, e nao o que rodou. Aqui a primeira etapa passa nas tres larguras.

**E uma armadilha que vale registrar, porque quase passou por verificacao.** Os tres pontos
publicados caem exatamente sobre uma curva quadratica na largura, e ajustar essa curva usando so 256
e 352 preve 528 com 99,9 % de acerto. Consistencia interna perfeita — que o proprio defeito da secao
10.6 **tambem** exibia, porque as duas pontas vieram do mesmo caminho errado. Consistencia interna
descarta "um numero foi inventado"; nunca descarta "todos vieram de uma configuracao que nao e a que
rodou". So a contagem independente separa os dois casos.

E o passo que evitou o engano nao foi medir — foi **perguntar se aquele teste era capaz de falhar**.
O ajuste quadratico passou primeiro, e teria sido entregue como verificacao; o que o descartou foi
aplica-lo ao defeito da secao 10.6 e ver que ele o aprovaria tambem. Um teste que nao reprova o caso
conhecido nao verifica nada. A regra ficou registrada como um erro proprio na lista de abertura do
guia de avaliacao do repo novo: **aceitar consistencia interna como verificacao.**

**Custo de cada saida.** Uma errata no apendice suplementar troca tres numeros e um rotulo, e a
frase que sobra e mais forte que a atual. Nao mexer significa levar a defesa uma tabela cujas duas
ultimas colunas nao descrevem as execucoes que produziram a linha ao lado.

### 10.7 · Nenhum dos seis datasets e uma reserva intocada [emenda de 2026-08-21]

Este e o item que a banca puxa primeiro se alguem usar, em voz alta, o vocabulario do protocolo novo
— "reserva", "selado", "gasto". Ele **nao** e uma errata contra a dissertacao. E o contrario: foi a
dissertacao que derrubou a premissa, por escrito, na propria nota da tabela de resultados.

**A premissa que caiu.** O protocolo do repo novo atribuia peso confirmatorio a alguns datasets "por
nunca terem sido dataset de ajuste". A nota da tabela principal e o capitulo de configuracao dizem
outra coisa, e sao especificos:

| busca | cobertura declarada no texto entregue |
|---|---|
| batch size, categoria dedicada | **todos os seis** — cinco folds em Istambul, Alabama e Arizona; menos folds em Florida e Texas |
| taxa de aprendizado, categoria dedicada | cinco folds em Istambul, Alabama e Arizona; **folds unicos no Texas**; em Florida e California **nao foi variada** |
| modelo conjunto | buscado em Istambul, Alabama e Arizona; triado em Florida; **Texas e California recebem a configuracao transferida** |
| regiao dedicada | uma configuracao so, herdada, com apenas a forca do ajuste de logit testada |

**Pela definicao do proprio protocolo** — um conjunto deixa de ser reserva no instante em que alguem
o ve — **nenhum dos seis e uma reserva intocada.** Istambul e o mais ajustado dos tres pequenos, nao
o menos. Texas recebeu busca de largura de lote e de taxa de aprendizado. California e o menos
tocado dos seis, e ainda assim recebeu busca de largura de lote.

**O que nao sobrevive.** Qualquer frase da forma "validado em dados que nunca foram usados para
nenhuma decisao", para os seis. E o peso confirmatorio **pela razao dada** — a razao e falsa, entao
a conclusao nao decorre dela.

**O que sobrevive, e e a maior parte do desenho.**

- **O fold externo lacrado dentro de cada dataset.** A correcao central do protocolo novo — quem
  escolhe a epoca nao e quem reporta o numero — nao e tocada por este erro. Ela e sobre **folds**,
  nao sobre datasets.
- **O desenho pareado.** O vies de reuso ataca numeros absolutos muito mais que deltas pareados, e a
  alegacao-manchete e um delta pareado. Os dois bracos de cada comparacao pagam a mesma contaminacao.
- **O gatekeeping, a multiplicidade, a definicao dos estimandos, o gate de calibracao.** Nenhum
  depende da premissa da reserva.
- **Uma alegacao mais fraca e honesta para Texas e California**: receberam busca de hiperparametro,
  nao busca de receita ou de arquitetura, e a configuracao do modelo conjunto foi **transferida** e
  nao buscada neles. Menos contaminados que os outros quatro. Nao limpos.

**Por que isto e emenda e nao conserto silencioso, e por que essa distincao e a resposta.** A
premissa era falsa **quando foi escrita**, e nao foi falsificada depois. Editar o protocolo no lugar
apagaria o rastro de que o argumento de peso confirmatorio um dia se apoiou nela. O registro esta
carimbado como **anterior a primeira leitura confirmatoria** sob aquele protocolo, e o gatilho foi
**ler a nota de rodape da dissertacao**, nao ver um resultado. E isso que separa uma emenda de uma
racionalizacao pos-hoc, e e a primeira coisa que um arguidor competente vai querer estabelecer.

**A frase defensavel:** *"o protocolo novo atribuia peso confirmatorio a alguns conjuntos por nunca
terem sido usados para ajuste. Fomos verificar contra a nota da minha propria tabela e a premissa e
falsa: a largura de lote foi buscada em todos os seis. Registramos a emenda antes de ler qualquer
numero confirmatorio. O que ela derruba e a palavra 'reserva'; o que ela nao toca e a separacao
entre quem escolhe a epoca e quem reporta o numero, que e a correcao que importa, e que e sobre
folds e nao sobre conjuntos."*

⚠ **Cite o capitulo de configuracao para isto, e nao a nota da tabela.** As duas dizem a mesma coisa
em graus diferentes de precisao, e so uma sobrevive a uma pergunta. A nota da tabela funde os dois
botoes numa frase; o capitulo os separa, e e a unica forma que os artefatos sustentam. O proprio
`.tex` registra por que, e a historia importa mais que a conclusao: a cobertura foi apurada **duas
vezes**, e a segunda apuracao **contradisse a primeira e prevaleceu**. Um censo restrito a geracao
mais recente concluiu que a largura de lote nunca variou na California; incluir a geracao anterior
revela **oito bracos da California** variando-a entre 2 048 e 8 192, e um terceiro artefato de
configuracao corrobora por outro caminho. As duas formulacoes superadas, *"at every dataset"* e
*"except California"*, ficam registradas ali como **falsas** — preservadas, nao apagadas — porque
confundiam largura de lote com taxa de aprendizado. A apuracao tambem nomeia a lacuna verdadeira com
precisao, e ela e a **taxa de aprendizado**: California e Florida num ponto unico nas duas geracoes,
Texas variando tres pontos mas em folds unicos.

**A frase curta, se a pergunta vier:** *"a cobertura de busca foi apurada duas vezes; a segunda
apuracao contradisse a primeira e prevaleceu porque incluia os artefatos da geracao anterior, e as
duas leituras superadas continuam no registro."* Isso e mais defensavel que uma cobertura que sempre
esteve certa, porque exibe o processo em vez de afirma-lo.

O unico detalhe que a frase do capitulo nao da e **quantos folds** a busca de largura de lote cobriu
na California — ela enumera a contagem de folds para cinco dos seis. Nao e contradicao; e um numero
nao dito.

---

## 11 · Proveniencia

**Repositorio.** `/Users/vitor/Desktop/mestrado/mtlcheck/mtlcheck`, branch `rewrite/mtlcheck`,
HEAD `824ebb76` em 2026-08-21. Todo caminho citado neste documento e relativo a essa raiz.

**Verificado contra o repo novo em 2026-08-21.** Desde a primeira redacao (20-08) mudaram quatro
coisas, todas ja refletidas acima: a emenda da reserva (secao 10.7), o fatorial medido e a decisao
do gate fechada (secoes 10.5 e 6.2), a cifra de 3,66 corrigida para 3,67 e rebaixada de "limpa" para
"a mais limpa" (secao 5.1), e os caminhos do lado da dissertacao, que a reorganizacao de 20-08
moveu de `src_fix/` para `src/`. **Nao** mudaram: os oito deltas da secao 3, os seis vereditos
selados da secao 4, o 28,63 pp do forward-only, o piso de 0,034 pp, as 35 519 arestas, o
determinismo e as tres divergencias do POI2Vec.

**Documentos-fonte, na ordem em que respondem as perguntas deste registro:**

| caminho | o que sustenta |
|---|---|
| `docs/DIVERGENCE_REGISTER.md` | a secao 2, e a leitura correta de todo numero das secoes 6 e 7; o §3.1 e o caso da secao 10.3 |
| `studies/porting_validation/evidence/estado_vs_dissertacao.json` | a secao 3, celula a celula |
| `studies/porting_validation/SEALED_BRIDGE_READ.md` + `evidence/sealed_bridge_tier_a.json` | a secao 4 e o adendo da secao 5.6 |
| `docs/EVALUATION_METHOD_GUIDE.md`, `docs/plans/EVALUATION_PROTOCOL.md` | a secao 5 inteira; o §0.2 e a armadilha registrada na secao 10.6; a emenda §12.3 e a secao 10.7 |
| `articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex:42-63` (neste repo) | a cobertura de busca da secao 10.7, lida na fonte — **e a citacao certa**; a nota da tabela de resultados funde os dois botoes e nao deve ser usada para isto |
| `docs/QUAL_CONJUNTO_USAR.md` | a secao 5.1, na forma curta — e o documento mais util se a banca puxar protocolo |
| `docs/REFERENCE_DEFECTS.md` (R1-R16) | a secao 6.2 e a secao 7 |
| `studies/porting_validation/SUBSTRATE_FROM_SCRATCH.md` | a secao 6.1, com a atribuicao das tres divergencias |
| `docs/SYSTEM_MAP.md` (S1-S17, D1-D8) | a secao 8 |
| `studies/porting_validation/AUDIT_2026-08-19.md`, `INCIDENT_2026-08-19_commit.md` | a secao 10.3 |
| `studies/improvements/PLAN.md`, `studies/porting_validation/STATE.md` | a secao 10.4 |
| `studies/improvements/STUDY.md` (secao final) | a secao 10.5, e o aviso reciproco do lado que causa a mudanca |
| `articles/dissertacao/src/tables/mobiwac/datasets.tex` (neste repo) | a secao 10.1 |
| `data/checkins/{Alabama,Arizona}.parquet` (contagem direta de check-ins, usuarios e lugares, 2026-08-20) | a verificacao da secao 10.1 |
| `src/mtlcheck/eval/optimism.py`, `waves/sealed_bridge.toml:9` | a secao 5.1, e o limite do ~0,66 pp |
| `articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex:119` (neste repo) | a justificativa da margem de dois pontos, secao 4 |
| `wrapup/material_extra/chapters/apx_i_parameter_count_control.tex:89,101,102` (nesta pasta) | a secao 10.6 |
| `docs/REFERENCE_DEFECTS.md` §R14, `studies/improvements/PLAN.md:46` | a secao 10.6 e o roteamento dela como errata |
| recontagem de parametros da cabeca de regiao, reimplementacao independente, 2026-08-20 | a verificacao do P1 na secao 10.6 |

**Como os numeros deste registro foram obtidos.** As secoes 3, 4, 5 e 6 saem de artefatos JSON e de
prosa curada do repo novo, lidos diretamente. A reconciliacao da secao 10.1 foi confirmada por
contagem direta no corpus bruto, e o ponto onde a verificacao para esta escrito ali. A cifra de
otimismo de selecao da secao 5.1 foi rastreada ate a origem e **rebaixada** de "medida" para
"sugerida por um fold" em 2026-08-20; o repo novo carregava o exagero em cinco pontos do
codigo. As duas sessoes que executaram o porte foram consultadas e confirmaram o conteudo das
secoes 1 a 8.

**O que este documento nao mede.** Nenhuma celula foi executada para escrever este registro. E
auditoria e preparacao oral, como o resto desta pasta.
