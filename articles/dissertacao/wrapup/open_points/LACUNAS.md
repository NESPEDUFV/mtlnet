# DEFENSE_OPEN_POINTS, Parte I: as lacunas

**Auditoria de 2026-08-12.** Todos os registros de pendencia do projeto foram varridos, e cada item
foi remedido contra o **fonte vivo** em `articles/dissertacao/src_fix/` e contra o **PDF construido**,
nunca contra o cabecalho do proprio item.

**A versao medida.** `src_fix/build/main.pdf`, **119 pp** (defesa), sha256 comeca em `c71e0b1d02fdcd2a`;
`main_academico.pdf` **114 pp** (deposito); `main_extra.pdf` **27 pp** (suplemento);
`main_ppgc.pdf` **120 pp**. O `dissertacao.pdf` na raiz de `src_fix/` e byte-identico ao build de defesa.
A arvore `src_clean/` carrega **o mesmo texto vivo, arquivo por arquivo** (61 de 61 identicos apos
remover comentarios), diferindo so no volume de comentario (5.108 linhas de comentario em `src_fix`
contra 61 em `src_clean`); o build dela tambem tem 119 pp mas **nao** e byte-identico
(sha256 `fa6be5f954b44525`).

**Instrumentos validados antes de qualquer zero.** Quatro vezes nesta sessao um instrumento devolveu
zero por estar quebrado, e nao por ausencia:

1. Contagem de paginas por regex sobre os bytes do PDF devolveu **0 pp para os cinco arquivos**.
   Substituida por biblioteca de PDF.
2. Busca de frase linha a linha nao acha sentenca que quebra em varias linhas. Todo teste de presenca
   aqui corre sobre corpus **sem linhas de comentario e com espaco achatado**, e o corpus foi validado
   achando uma frase que so existe quando as linhas se juntam.
3. Antes de aceitar que o `apx_b_static_scope.tex` **nao** chega ao leitor, dois controles positivos
   foram medidos com o mesmo instrumento (8 de 12 e 10 de 12 frases achadas em arquivos que sabemos
   renderizar). So depois o zero foi aceito.
4. O gate `check_audit_claims.py` le `../src` por construcao (`src_utils/check_audit_claims.py:45`).
   Foi re-apontado para `src_fix` por harness e **validado nos dois sentidos**: o controle apontado
   para `src` reproduz os 28 do registro, o mesmo harness apontado para `src_fix` da 16.

**Como ler a classificacao.** Cinco categorias, uma por item: **MORTO** (a versao enviada resolveu),
**ERRATA** (muda no deposito final), **ORAL** (resposta na arguicao, sem tocar o texto),
**EXECUCAO** (so fecha rodando experimento) e **DECISAO DO AUTOR** (nenhum agente fecha).

---

## Indice por categoria

| categoria | itens | onde estao |
|---|--:|---|
| **EXECUCAO** | 4 | §1, quatro blocos |
| **DECISAO DO AUTOR** | 7 | §2, sete blocos |
| **ERRATA** | 7 | §3, sete blocos |
| **ORAL** | 6 | §4, seis blocos |
| **MORTO** | 18 | §5, dezoito linhas de tabela |
| **total** | **42** | 24 blocos mais 18 linhas |

A soma fecha: §1 tem 4 blocos, §2 tem 7, §3 tem 7 e §4 tem 6, o que da 24 blocos, e a tabela do §5 tem
18 linhas, uma por item morto. 24 mais 18 sao 42. Os marcadores por bloco sao **18 ABERTO** e
**6 FECHADO**; todo bloco do §4 e FECHADO, porque uma resposta oral nao deixa nada pendente no texto.

**Dois dos sete itens de errata (ERR-6 e ERR-7) nao vinham de nenhum registro**: sao defeitos de
proveniencia na mesma frase de cobertura de busca do `05_setup.tex`, achados nesta auditoria e
verificados contra o registro de configuracao. Os dois **reduzem** o que a frase reivindica.

**Os itens que este relatorio julga INVALIDOS** (registrados como abertos, medidos como nao mais
validos): PENDENCIAS 2.32, PENDENCIAS 2.1 (a contagem de 56), PENDENCIAS 2.27 item 1 (a contagem de
28), NEEDS_SIGN_OFF 46 (a premissa de que renderiza), LEFT_OUT LO-9 (a metade `[VERIFY]`),
LEFT_OUT LO-10 (as 41 linhas decorativas), CONSIDERATIONS GER-09 (as tres partes ditas abertas),
fundamentals/OPEN_QUESTIONS item 1. Cada um traz a medicao no bloco correspondente.

**Registros que os arquivos conhecidos nao citavam** (achado desta varredura):
`../../science/fundamentals/GAP_STATUS.md`, `../../science/fundamentals/OPEN_QUESTIONS.md`,
`docs/studies/closing_data/v18/region_1fold_triage/FINDING.md`,
`docs/studies/archive/mtl-protocol-fix/DEFERRED_WORK.md`,
`docs/findings/F49_LAMBDA0_DECOMPOSITION_GAP.md`,
`docs/studies/merge_design/AUDIT_HGI_GAP.md`.
E o `OPEN_REGISTER.md` que a tarefa nomeia **nao existe em disco**: e uma tupla dentro de
`src_utils/check_register.py:423`.

---


## §1 · EXECUCAO: so fecha rodando um experimento

Estes quatro sao os que podem morder na defesa, porque cada um deixa uma pergunta de mecanismo em
aberto e o texto enviado ja diz que esta em aberto.

### [FECHADO 2026-08-13] · P1 · Controle de regiao com capacidade pareada: a vantagem em Texas e California e compartilhamento ou parametro?

**RESPOSTA FINAL (executado; numeros corrigidos a 2026-09-02, propagados aqui a 2026-10-02):** na
California, e capacidade. Contra a contagem do modelo conjunto lida nos logs de treino (5.151.189),
o braco pareado e o de `d_model=352` (5.014.942, **97,4 %**), e ele **supera** o conjunto por
$+0{,}41$ Acc@10 ($p = 0{,}010$, unanime nos cinco folds); o de 528 (**174,8 %**) faz $+0{,}43$
($p = 0{,}008$), e o passo de um para o outro nao se separa de zero ($+0{,}021$, $p = 0{,}40$). O
**Texas nao tem controle pareado**: o unico braco (544, **170,5 %**) faz $+0{,}21$, $p = 0{,}12$.
*Esta resposta dizia, ate 2026-10-02, que o "orcamento inteiro" era o braco de 528, que o Texas era
igualado, e que um braco "a 57 por cento" ja chegava ao mesmo nivel; o 57 % dividia por uma contagem
reconstruida (8.809.533), nao medida.* Registro completo em
`../post_submission_studies/P1_capacity_region.md` (que ainda traz os percentuais antigos), a
correcao em `../erratas/VERIFICACAO.md`, e a errata que leva isso ao texto em
`../erratas/errata_Q14_capacity_region.tex`.

**Nota de largura:** as larguras publicadas em `capacity_baseline_experiment.md` medem a arquitetura
anterior e nao pareiam capacidade no modelo atual. As derivadas contra o modelo atual, alvo igual ao
modelo conjunto inteiro, sao $624$ (AL), $528$ (CA) e $544$ (TX). *(2026-10-02: essas tres foram
derivadas contra contagens reconstruidas do conjunto, e contra as medidas ficam a 166 a 175 %. O unico
braco proximo da paridade e o de 352 em California. Ver `VERIFICACAO.md`.)*

<details><summary>o registro de quando o item estava aberto</summary>


**ACAO NECESSARIA:** rodar o protocolo dedicado de regiao com a cabeca alargada ate a contagem de
parametros da via de regiao do modelo conjunto, e comparar com o escore de regiao do modelo conjunto.
Comando exato registrado em `POSTPONED.md:14-27`. **Custo medido, citado da fonte:** as paredes do
dedicado-regiao na preparacao final da representacao, semente 0, sao **189 s em Alabama e 5.177 s em
California**; com a cabeca mais
larga, **cerca de 5 min (AL) e cerca de 2,2 h (CA) por semente**. A largura ja esta precomputada:
`d_model=480` em Alabama, `352` em California.
**DADOS:** existe hoje uma triagem de UMA dobra em `region_1fold_triage/FINDING.md`, medida na
preparacao anterior da representacao (o proprio registro adverte que aquela preparacao tinha o
vazamento de rotulo que a atual corrige, e que a receita e a de antes do re-tuning), semente 0,
dobra 0: severar o tronco move regiao em **-0,099 (California)** e
**-0,120 (Texas)**; apagar tambem a tarefa de categoria move **-0,077 (California)**. O proprio driver
declara o limite: *"If the arms land within a few tenths of each other, that is NOT a null result — it
is an inconclusive screen."* Existe, alem disso, o contraste de parametros: a via de regiao carrega
**2,5 a 5,9 vezes** os parametros do dedicado (Alabama 2.466.542 contra 417.117; California 3.420.110
contra 1.370.685). Falta a medicao com capacidade pareada, com dispersao e teste pareado.
**Atencao a uma deriva de numero:** o registro P1 fundamenta a aposta em *"joint reg 65,57 vs dedicated
ceiling 63,45, delta +2,12"* e cita *"+2,12 / +2,05"*. Nenhum desses quatro numeros aparece nos builds
enviados: sao do substrato anterior. Os numeros do texto enviado sao **Texas +1,21 e California +1,06**
(`REVISION_PLAN.md` §1.1). Se o senhor citar P1 na defesa, cite a margem enviada, nao a do registro.
**RESPOSTA FINAL:** "O texto nao atribui a vantagem de regiao a transferencia entre tarefas. Ele diz,
na secao de discussao, que a evidencia nao separa as contribuicoes, e que onde o tronco foi isolado
diretamente os bracos moveram as duas tarefas por quantidades que uma triagem daquele tamanho nao
distingue de ruido, e que esses bracos nao foram rodados nos dois conjuntos que carregam a vantagem de
regiao. A afirmacao que faco e sobre o desenho, nao sobre transferencia: este desenho, representacao
compartilhada e caminho espacial privado juntos, produz uma saida de regiao acima de dois modelos
dedicados nos dois conjuntos com o maior vocabulario de regioes. O controle com capacidade pareada
custa cerca de duas horas e vinte minutos em California por semente e fecha essa pergunta; ele nao
estava pronto a tempo e esta registrado com o comando exato."
*Fonte: docs/studies/closing_data/v18/POSTPONED.md:9-49; GAPS.md §7 item 2; region_1fold_triage/FINDING.md*

</details>

### [ABERTO] · P4 · Ablacao do tronco em cinco dobras em California e Texas

**ACAO NECESSARIA:** bracos A/A' em California e Texas, 5 dobras, semente 0. **Custo citado:** **cerca
de 22 h**. Fecha a pergunta "o tronco contribui alguma coisa nesses dois conjuntos?", que hoje esta
sem medicao: a triagem de uma dobra tinha poder para detectar um colapso de varios pontos, e nao para
resolver um efeito abaixo de 0,15 pp.
**DADOS:** em Alabama existem bracos de cinco dobras (2026-08-07): T1 `disable_cross_attn` da
Δcat **-0,015** e Δreg **-0,138**; T2 `identity_cross_attn` da Δcat **-0,154** e Δreg **-0,004**, ambos
dentro do sigma de dobra (cerca de 1,7 em categoria e 3,0 em regiao). O registro carrega o aviso
explicito, em `POSTPONED.md:86-89`: **nao citar "o tronco e inerte" como afirmacao geral**: vale em
Alabama, em cinco dobras, e em nenhum outro lugar. O argumento de compute que tenta a remocao
(1.094 s com tronco contra 359 s sem, em Alabama) esta marcado como escopado a Alabama, nao como
veredito de arquitetura.
**RESPOSTA FINAL:** "Em Alabama o tronco e inerte em cinco dobras, nem ajuda nem prejudica, e isso e um
resultado de um conjunto so. Nos dois conjuntos onde o modelo conjunto tem vantagem em regiao existe
apenas uma triagem de uma dobra, que refuta a hipotese de que o tronco carrega a vantagem, porque tinha
poder para detectar um colapso de varios pontos e nenhum ocorreu, mas nao resolve uma contribuicao
abaixo de 0,15 pp. O texto enviado nao afirma nada alem disso."
*Fonte: docs/studies/closing_data/v18/POSTPONED.md:75-89*

### [ABERTO] · P6 · A metade grande do sweep de re-tuning: linha 8 (California e Texas, modelo conjunto)

**ACAO NECESSARIA:** linha 8, os botoes do modelo conjunto levados a Texas ou California, 2 bracos.
**Custo citado:** **cerca de 12,5 h** (Texas conjunto cerca de 22.500 s por braco). As linhas 5 e 6
foram parcialmente liberadas em 2026-08-08 e rodaram em Texas com uma dobra (cerca de 1,9 h em vez de
9,6 h), o que reduz mas nao elimina o risco de transferencia: uma dobra escolhe direcao, nao certifica
receita.
**DADOS:** este e **o unico adiamento com risco direcional conhecido**, e o registro o descreve: o modo
de falha inverte com o tamanho dos dados. Alabama e Arizona sobreajustam (lacuna treino-validacao de
cerca de +42 pp) enquanto **California e Texas nao mostram lacuna nenhuma** (+0,25 e +0,52), pois sao
limitados por capacidade, nao por sobreajuste. A correcao dos conjuntos pequenos e **taxa de
aprendizado menor**, que e o oposto do que um modelo limitado por capacidade quer. O texto enviado
absorve isso corretamente: a cobertura de busca esta declarada por botao e por conjunto
(`5_mobiwac/05_setup.tex`), e a discussao diz que em Texas e California o modelo conjunto roda uma
configuracao transferida, nao validada.
**RESPOSTA FINAL:** "A cobertura de busca esta declarada no texto, por botao e por conjunto: tamanho de
lote buscado no dedicado de categoria nos seis conjuntos, taxa de aprendizado em quatro dos seis, e o
modelo conjunto buscado nos conjuntos menores. Texas e California carregam configuracao transferida, e
o texto diz isso onde reporta o resultado. Onde a busca do dedicado e a mais ampla, o residuo favorece
o dedicado, o que torna a diferenca de categoria que reporto conservadora ali. Nao afirmo que o vies
se cancela exatamente, e o texto tambem diz isso."
*Fonte: docs/studies/closing_data/v18/POSTPONED.md:91-118*

### [ABERTO] · GAPS-D · Certificado de empate ausente em 20 das 24 celulas de regiao

**ACAO NECESSARIA:** nada a re-treinar. O que falta e um campo de uma linha, `scored_on` /
`scoring_path`, nas 21 celulas pontuadas pelo caminho antigo, para que um leitor separe as duas
populacoes sem arqueologia. Onde o certificado existe, o efeito medido e **1 a 2 linhas em 585.092
(California) e 1 em 766.083 (Texas)**, isto e **menos de 0,0003 pp** de Acc@10, cerca de 1% da
dispersao entre sementes.
**DADOS:** `ambiguous_rows` esta registrado em **3 de 24** celulas de regiao, as produzidas depois de
2026-08-10. Uma celula (texas s100) foi preenchida a posteriori a partir do proprio JSON de resultado,
copiada verbatim e marcada com bloco `post_hoc_fields`. O defeito de origem foi corrigido:
`run_lane.sh` nao copiava o certificado enquanto o driver do A40 copiava, entao a divulgacao dependia
da maquina usada.
**RESPOSTA FINAL:** "O empate em hit@k afeta menos de tres decimos de milesimo de ponto percentual de
Acc@10 onde foi medido, cerca de um por cento da dispersao entre sementes, e portanto nao move nenhum
veredito. As celulas antigas foram pontuadas por um caminho onde a pergunta nao surge; isso esta
declarado em vez de preenchido por suposicao."
*Fonte: docs/studies/closing_data/v18/GAPS.md §4 (linhas 178-193), A1, A2*

---

## §2 · DECISAO DO AUTOR: nenhum agente fecha

### [ABERTO] · NEEDS_SIGN_OFF 46 · O unico marcador de aval que continua anotado como aberto no fonte

**ACAO NECESSARIA:** ler um paragrafo e confirmar ou ajustar. O paragrafo caracteriza o canal do
Capitulo 3 para o problema static-task como **indireto**, e nao **ausente**, o que e mais fraco do que
a decisao anterior do autor (que o problema era exclusivo do CoUrb). Duas saidas: (a) confirmar a
formulacao "canal indireto", custo zero, ou (b) pedir ajuste, e ai vira ERRATA de deposito.
**DADOS:** este e o **unico** dos 34 marcadores `[NEEDS SIGN-OFF]` vivos em `src_fix` que carrega
anotacao `| OPEN`; os outros 32 numerados carregam `| CLOSED`, e um (em `apx_d_ceiling.tex:10`) nao
segue a forma numerada. Vive em `chapters/apx_b_static_scope.tex:70`.
**A premissa do item, porem, esta invalidada.** O cabecalho do item diz *"renderiza no volume extra,
p. 13"*. Medido: `chapters/apx_b_static_scope` **nao e chamado por nenhum `\input` ou `\include` vivo**
em toda a arvore; a unica chamada esta comentada em `chapters/apx_b_errata.tex:475`. Doze frases do
arquivo foram normalizadas e buscadas nos tres builds: **zero aparicoes**. Os dois controles positivos
com o mesmo instrumento acharam 8 de 12 e 10 de 12. Ou seja: **o paragrafo nao chega ao leitor da
versao enviada**, e a decisao deixou de ser urgente. O que a p. 13 do suplemento carrega e outro texto,
do proprio `apx_b_errata`.
**RESPOSTA FINAL:** "Esse paragrafo nao esta na versao entregue: a secao esta suprimida por convencao do
proprio arquivo de errata. O que o suplemento afirma sobre o Capitulo 3 e que ele emparelha
classificacao estatica de categoria com predicao da proxima categoria, nao contem tarefa de regiao, e
hipotetiza transferencia negativa em vez de observa-la."
*Fonte: src_utils/_history/NEEDS_SIGN_OFF.md:1980 (item 46); chapters/apx_b_static_scope.tex:70*

### [ABERTO] · LO-6 · Tamanho de tipo das duas figuras de arquitetura publicadas

**ACAO NECESSARIA:** decisao mais uma exportacao manual, que nenhum agente pode fazer (nao ha `drawio`
nem `inkscape` no ambiente). Receita: subir `fontSize` de 13 para cerca de 20 e reexportar na mesma
largura em pixels. Custo: minutos no Draw.io, mais um build. **A saida (a)** e deixar como esta, e o
proprio autor observou que o contraste hoje deixa legivel. **A saida (b)** e reexportar, e ai o
deposito final carrega figuras que diferem das publicadas em apresentacao.
**DADOS:** medido em `LEFT_OUT.md:141-146`: a figura do Cap. 3 (`figures/cbic_mtlnet_arch.png`,
1200 x 336) imprime rotulos a **45,3%** do corpo de 11,96 pt; a do Cap. 4
(`figures/courb/arquitetura_modelo.png`, 1102 x 348) a **44,4%**. As duas do Cap. 5, reescaladas, ficam
a 93,2% e 66,3%. Confirmado nesta sessao por sha256: o raster do Cap. 3 e **byte-identico** a
`articles/CBIC___MTL/imgs/mtlnet_poi.drawio.png` (ambos `0dc7e9dc3afa3fce48cf...`), portanto e o
artefato publicado exatamente como publicado. Os dois `.drawio` existem no repositorio.
**RESPOSTA FINAL:** "As duas figuras de arquitetura sao os artefatos publicados, reproduzidos sem
alteracao de apresentacao. A do Capitulo 3 e byte-identica ao arquivo do artigo do CBIC. Subir o
tamanho de tipo e uma mudanca de apresentacao num artefato publicado, e num deles co-autorado, e nao
foi autorizada como parte da errata; a errata autorizada naquela figura foi a traducao de seis rotulos
na figura do Capitulo 4."
*Fonte: src_utils/LEFT_OUT.md:136-174; PENDENCIAS.md:97-113 (item 2.5)*

### [ABERTO] · LO-11 · Credito por funcao do autor no artigo CoUrb

**ACAO NECESSARIA:** decidir se entra uma frase no Apendice A. **Saida (a):** nao entra, que e a decisao
registrada duas vezes pelo proprio autor (*"Nao precisa mexer nisso, pode remover essa
preocupacao."*). **Saida (b):** entra, e ai custa uma frase no Apendice A com
`[NEEDS SIGN-OFF: COD-018]` e envolve nomear um aluno de graduacao no documento, que e decisao sobre
terceiro.
**DADOS:** o que o texto tem hoje sao as funcoes de registro publico: no prefacio do Cap. 4
(`chapters/4_courb.tex:19`), Tarik S. Paiva e primeiro autor, o autor da dissertacao e segundo autor,
apresentou o trabalho no workshop, e e primeiro autor do modelo de base MTLnet. Medido nos builds: a
expressao "first author" aparece **3 vezes** na defesa e no deposito. O Apendice A descreve a plataforma
e o ETL e nao atribui funcao por item no CoUrb. O gate registra a retirada em vez de deixa-la silenciosa:
`COD-018` esta na tabela `RETIRED` de `check_audit_claims.py`, que imprime a cada rodada com a citacao
do autor como motivo, confirmado nesta sessao na saida do gate.
**RESPOSTA FINAL:** "O prefacio do Capitulo 4 declara as funcoes que sao de registro publico: primeira
autoria do Tarik, minha segunda autoria, a apresentacao no workshop, e minha primeira autoria do modelo
de base. Credito por funcao num artigo co-autorado e uma afirmacao que cabe a mim fazer, e eu decidi
nao expandir alem do registro publico."
*Fonte: src_utils/LEFT_OUT.md:277-311; src_utils/check_audit_claims.py (tabela RETIRED, COD-018)*

### [ABERTO] · LO-12 · A tensao nao resolvida na descricao do insumo temporal do Capitulo 4

**ACAO NECESSARIA:** nada que agente feche, e nada que exija edicao. Fechar exige **um artefato que
ninguem tem**: o `data/output/{state}/time_embedding.parquet` da epoca do CoUrb, onde `len(df)` contra
as contagens de POI e de check-in daquele estado decidiria em um comando. O autor declarou nao te-lo.
Regenerar foi considerado e **deliberadamente nao feito**: mediria o codigo de hoje, nao a rodada
publicada.
**DADOS:** as duas frases da metodologia publicada nao podem ser as duas verdadeiras: `:93` liga a
concatenacao de 192 dimensoes a um POI e o pareia com a categoria daquele POI (um vetor temporal por
POI), enquanto `:153` diz que o embedding temporal *"representa o timestamp de cada check-in"* (um vetor
por visita). O codigo da epoca estabelece que o codificador temporal emite **uma linha por check-in**
(`Time_Encoder.ipynb`, saidas armazenadas: 2.535.573 check-ins em California, forma
`time_embeds_sin (2535573, 64)`) e que o insumo da tarefa de categoria **deduplica por lugar**
(`create_inputs_hgi.py:437`), **mas os dois nao podem ser conectados**: o ETL le um `.parquet` que nada
naquele repositorio escreve. Medido: o Cap. 2 descreve a posicao da janela do Cap. 4 como carregando
"a vector that is a function of the visited POI", **sem qualificacao temporal nenhuma**, confirmado
nesta sessao, 1 ocorrencia. As duas redacoes proibidas continuam ausentes: "of the visit's timestamp"
tem **zero** ocorrencias na arvore.
**RESPOSTA FINAL:** "O Capitulo 4 e uma versao de registro e nao foi editado. O Capitulo 2 descreve o
insumo daquele estudo como um vetor que e funcao do POI visitado, sem qualificacao temporal, porque o
nivel do insumo temporal nao esta estabelecido: duas frases da metodologia publicada implicam niveis
diferentes, o codigo da epoca emite uma linha por check-in e o ETL deduplica por lugar, e a tabela que
os conectaria nao existe em disco. Preferi nao afirmar o nivel a afirmar o errado."
*Fonte: src_utils/LEFT_OUT.md:315-375*

### [ABERTO] · LO-13 · A correlacao entre os dois fluxos de entrada do modelo conjunto

**ACAO NECESSARIA:** decidir se vale medir. Nomear uma correlacao afirma uma quantidade; medi-la e
experimento de verdade (cosseno ou informacao mutua entre as duas tabelas exportadas, por conjunto,
com um nulo) e responderia a uma pergunta sobre a propria representacao que nenhum capitulo faz.
**DADOS:** o que esta estabelecido e um fato de construcao, nao uma estatistica: o caminho espacial
recebe uma **copia com gradiente interrompido** do conjunto de POIs, entao as duas tabelas compartilham
origem pelo modo como o grafo e construido. Medido nesta sessao: §2.2.4 afirma exatamente isso, "share
an origin by construction, so they are not independent views" (**2 ocorrencias** em
`chapters/2_fundamentals.tex`), e a palavra "correlated" **nao aparece** em prosa viva de capitulo:
as tres ocorrencias na arvore estao em `tables/cbic/errata_wording.tex` (2) e `3_cbic/basis.tex` (1),
que sao prosa publicada e tabela de errata.
**RESPOSTA FINAL:** "O texto afirma o fato de construcao: as duas entradas vem de uma unica
representacao no nivel de check-in e compartilham origem por construcao, logo nao sao visoes
independentes. Nao afirmo correlacao, porque isso seria uma quantidade, e eu nao a medi."
*Fonte: src_utils/LEFT_OUT.md:386-425*

### [ABERTO] · GAPS §7.1 · O piso de significancia pratica

**ACAO NECESSARIA:** decidir se o registro do estudo passa a declarar um piso. O gerador de tabelas
premia "beats" a deltas de **+0,04 pp**, porque o pareamento em dobras identicas colapsa a variancia.
Tres argumentos independentes dizem que isso nao deve ser reportado como vitoria: dependencia entre
dobras (dobras de uma mesma semente compartilham cerca de 80% dos dados de treino), vies do comparador
ajustado, e tamanho de efeito.
**DADOS:** e uma decisao sobre o **gerador**, nao sobre o texto: medido nesta sessao, a menor vitoria
que o texto enviado reivindica e **+0,19** em categoria em Florida, com intervalo de 90% de +0,14 a
+0,25 e p corrigido de 0,011, e as duas de regiao sao **+1,21** e **+1,06**. Nenhuma celula de
0,04 pp e chamada de vitoria em lugar nenhum do documento. O gerador continua sem o piso.
**RESPOSTA FINAL:** "Nenhum resultado abaixo de dois decimos de ponto e reportado como vitoria no
documento. Cada vitoria carrega o teste pareado, a correcao de Holm dentro da familia da tarefa, e o
intervalo. As demais diferencas de categoria sao reportadas pelo limite que o intervalo sustenta, meio
ponto, e nao promovidas a empate."
*Fonte: docs/studies/closing_data/v18/GAPS.md §7 item 1 (linhas 245-249)*

### [ABERTO] · PENDENCIAS 4.1 · Os vinte e um itens marcados como decisao do autor

**ACAO NECESSARIA:** ler e decidir, item por item. Nenhum deles espera trabalho de agente, e por isso
nenhum deles bloqueia o deposito por si. O bloco de cada um traz opcoes, troca e esforco.
**DADOS:** medido: `PENDENCIAS.md:741` declara os 21 `[I DECIDE]` do §4.1 como fora do plano de
execucao, esperando a palavra do autor. Dos itens `AUT-`, dois seguem abertos por natureza distinta:
**AUT-26** (renomear o modelo conjunto; FECHADO 2026-10-06: nome MTVisitNet, texto inalterado) tinha raio de impacto medido: `MTLChkNet`
aparece **0 vezes** na arvore, e "the joint model" tem 57 ocorrencias em prosa viva, 17 delas no
Cap. 5, que e o manuscrito submetido, e 5 dentro de tabelas de errata onde a string citada **e** a
evidencia; **AUT-38** esta vazio no fonte, com decisao registrada "NADA A FAZER" e o ID reservado.
Confirmado nesta sessao que `MTLChkNet` tem **zero** ocorrencias nos tres builds.
**RESPOSTA FINAL:** *(vazio, porque depende de quais itens o autor decidir levar a defesa; nenhum e uma
pergunta que a banca faz espontaneamente)*
*Fonte: src_utils/PENDENCIAS.md:441-451, 688-746; blocos AUT-26 e AUT-38*

---

## §3 · ERRATA: muda no deposito final

> ## ESTADO A 2026-09-04 — seis dos sete fecharam; este bloco manda sobre os cabecalhos abaixo
>
> Auditado contra a arvore viva, nao contra este registo. Os cabecalhos de cada item foram
> actualizados, mas o corpo deles descreve o defeito **como era** e fica intacto, que e o seu valor.
>
> **A 2026-09-06 os sete estao fechados.** Nenhum ERR continua a precisar do autor.
>
> | | estado | o que aconteceu |
> |---|---|---|
> | **ERR-1** | **NAO E DEFEITO** | Verificado a 04/09 e o diagnostico estava errado. A tabela de erratas **nao esta no PDF de deposito** — e `\input` so pelo suplemento, e `pdftotext build/main_academico.pdf \| grep "Published wording"` devolve **0**. A frase sem hifen que se via no PDF e a **prosa do proprio Cap. 3, ja corrigida**: comeca por "In addition", que e exactamente o que a coluna direita da errata manda. E `multi-task` aparece **24 vezes intacto** nesse mesmo PDF, logo nao ha normalizacao a atropelar hifens. |
> | **ERR-2** | **RATIFICADO** 06/09 | Era o ultimo que precisava do autor, e fechou sem alteracao. O check que ele pediu antes de seguir o glossario confirma-o: **73 "multitask" contra 3 "multi-task"**, e as tres estao todas a citar um titulo (CBIC, MobiWac, e a coluna de redaccao superseded da errata). A razao decisiva nao e o estilo da casa mas a **fidelidade da citacao** — um titulo reproduz-se como foi publicado, em APA e em IEEE por igual. |
> | **ERR-3** | **APLICADO** 01/09 | O campo `note` de `liu2019dwa` saiu da entrada para comentario acima dela. ⚠ A primeira tentativa pos o comentario DENTRO das chavetas e partiu o BibTeX: percentagem nao e caractere de comentario para o BibTeX, que varre a procura do arroba. |
> | **ERR-4** | **DECIDIDO** 04/09 | Ruling do autor: **manter as orfas**, com nota a dizer que sao entradas de arquivo. Aplicado a `gambs2012mmc`, que ficou orfa hoje ao sair o paragrafo dos floors do Cap. 2. `belkin2003laplacian` e `santos2024urban` mantem-se. |
> | **ERR-5** | **FECHADO** 02/09 | `senushkin2023aligned` e `liu2023famo` receberam DOI (o segundo tambem `pages`). **`holm1979` fechou a falha, e nao esta em falta**: o DOI proposto **nao resolve** — doi.org 404, Crossref "Resource not found", e o Holm 1979 nao esta na Crossref de todo. A OpenAlex afirma-o na mesma, um id JSTOR herdado do MAG e nunca registado. A entrada leva `url` do JSTOR, que responde 200. **Nao restaurar da OpenAlex.** |
> | **ERR-6 / ERR-7** | **APLICADOS** 01/09 | O texto vivo le "on a single fold at Texas" e nomeia o valor de dataset grande. |
>
> **Fora dos sete, e da mesma familia:** a 04/09 acrescentou-se ao `.bib` a entrada
> `menon2021logitadjustment` — o ajuste de logit era usado nos resultados entregues e **nao era
> citado em lado nenhum**. Verificada na fonte (arXiv 2007.07314, campo do proprio registo:
> "Published as a conference paper in ICLR 2021"). **Sem DOI, e isso nao e omissao**: a Crossref nao
> tem nenhum registado para este trabalho. A citacao no Cap. 5 e texto reproduzido, logo entra como
> linha na Tabela B.5.

Nenhuma destas cinco muda um resultado, um veredito ou um numero. Sao defeitos de registro e de
apresentacao, e cada uma diz qual arquivo e qual frase.

### [NAO E DEFEITO] · ERR-1 · A normalizacao ortografica de "multi-task" entra na coluna de prosa PUBLICADA da tabela de errata

**ACAO NECESSARIA:** em `tables/cbic/errata_wording.tex`, a linha cuja coluna esquerda cita a prosa
publicada como *"Furthermore, investigating advanced multi-task optimizers..."* imprime, no volume
principal e no de deposito, com o hifen removido: **"investigating advanced multitask optimizers"**.
A coluna esquerda dessa tabela e a **evidencia** da redacao publicada, e a normalizacao a altera. No
volume suplementar a mesma linha imprime **com** o hifen. Correcao: blindar a coluna de prosa publicada
contra a normalizacao (a fonte ja carrega o hifen; a divergencia esta na normalizacao aplicada ao
build principal).
**DADOS:** a fonte de registro foi aberta nesta sessao: `articles/CBIC___MTL/sections/conclusion.tex:17`
carrega *"investigating \textbf{advanced multi-task optimizers and loss-balancing schemes}"*, com
hifen. Medido nos builds: hifenizado 0 na defesa, 0 no deposito, **1 no suplemento**; sem hifen **1 na
defesa** e **1 no deposito**, 0 no suplemento. A fonte `tables/cbic/errata_wording.tex:44` tem o hifen,
e o comentario em `:34` registra que a frase publicada le "advanced multi-task optimizers".
**RESPOSTA FINAL:** "A coluna de prosa publicada cita a redacao do artigo. No volume principal a
normalizacao ortografica da dissertacao alcancou essa citacao e removeu um hifen; o volume suplementar
imprime a forma correta. E um defeito de blindagem de citacao, corrigido no deposito final, e nao
altera nenhuma correcao listada."
*Fonte: tables/cbic/errata_wording.tex:34,:44; fonte de registro articles/CBIC___MTL/sections/conclusion.tex:17*

### [RATIFICADO] · ERR-2 · Os titulos dos capitulos 3 e 5 desidratam o hifen de titulos citados

**ACAO NECESSARIA:** decidir se o titulo de capitulo pode divergir do titulo do artigo. Hoje o
cabecalho do Cap. 5 le **"A Check-in-Level Multitask Study of Next Category and Region"** enquanto o
prefacio, tres linhas abaixo, cita o titulo do manuscrito como **"A Check-in-Level Multi-Task Study on
Mobility Data"**, com hifen. O mesmo padrao no Cap. 3. Correcao possivel: nenhuma, se a divergencia for
deliberada (o cabecalho e titulo de capitulo, nao citacao); ou alinhar o cabecalho.
**DADOS:** medido nos builds: o cabecalho desidratado aparece em **21 paginas** da defesa (p. 13 no
sumario e p. 67-86 como cabecalho corrente), e a forma hifenizada do titulo do manuscrito aparece na
p. 67 e na p. 92, na lista de referencias. O `GLOSSARY.md:130` manda a grafia "multitask"; a fonte de
registro do manuscrito (`articles/[mobiwac]/src/main.tex:51-52`) carrega o hifen. Contado na arvore
viva: 76 ocorrencias de "multitask" contra 3 de "multi-task", e as 3 estao onde citam titulo.
**RESPOSTA FINAL:** "O cabecalho do capitulo segue a grafia do glossario da dissertacao; o titulo do
artigo aparece citado com a grafia do registro, no prefacio e na lista de referencias. As duas formas
convivem por essa razao, e nao por descuido."
*Fonte: chapters/5_mobiwac.tex:16 e :29; chapters/3_cbic.tex:25; GLOSSARY.md:130*

> **RATIFICADO PELO AUTOR, 2026-09-06.** Instrucao: *"como estamos escrevendo o texto em ingles e a
> conferencia do mobiwac tbm e ieee, estamos usando o apa style... tem que ver qual e o formato
> correto, mas acho que ja esta no glossary e podemos seguir com o que esta la, mas so da um check
> antes."* O check foi feito e confirma o glossario. **Nenhuma alteracao.**
>
> **O que o check mediu**, na arvore viva com os comentarios filtrados do ficheiro: **73 ocorrencias
> de "multitask" contra 3 de "multi-task"**, e as tres hifenizadas estao todas em `3_cbic.tex`
> (prefacio, a citar o titulo publicado do CBIC), `5_mobiwac.tex` (prefacio, a citar o titulo aceite
> do MobiWac) e `tables/cbic/errata_wording.tex` (a coluna que cita a redaccao superseded, a letra).
> **Nenhuma das tres e prosa do documento**: as tres sao citacao de um registo.
>
> **A razao mais forte nao e o estilo da casa, e a fidelidade da citacao.** Um titulo citado
> reproduz-se como foi publicado, e isso vale igual em APA e em IEEE — nao se re-estiliza o titulo de
> outra pessoa para o conformar ao proprio manual. Portanto a pergunta "qual e o formato correto"
> tem duas respostas que nao competem: para prosa nossa, **multitask** (APA fecha prefixos como
> *multi-* sem hifen salvo colisao de vogais ou ambiguidade, e o glossario ja o manda); para um
> titulo citado, **a grafia do registo**, hifen incluido. As duas formas coexistem por essa razao.
>
> O `GLOSSARY.md:86` ja tinha antecipado exactamente isto para o POI, e na mesma ronda 14: aberto
> como substantivo (*"a point of interest"*), hifenizado so atributivamente (*"point-of-interest
> prediction"*), com a nota de que **ambas as formas estao correctas e nenhuma e um desvio a
> "uniformizar"**. O caso do *multitask* e o mesmo padrao.

### [APLICADO] · ERR-3 · Uma nota de anotacao interna imprime dentro de uma referencia

**ACAO NECESSARIA:** remover o campo `note` da entrada `liu2019dwa` no `references.bib`, ou move-lo
para comentario. A referencia **[52]** imprime, na lista de referencias da defesa e do deposito,
terminando em *"Introduces Dynamic Weight Average (DWA)."*, uma anotacao de trabalho, nao parte do
registro bibliografico.
**DADOS:** medido: das 98 referencias impressas, **exatamente uma** carrega uma sentenca de anotacao
desse tipo. Doze entradas do `.bib` tem campo `note`; onze delas sao legitimas (`arXiv:NNNN.NNNNN`,
"Accessed: 2024-05-21", a nota institucional da dissertacao de mestrado) e uma e anotacao interna.
**RESPOSTA FINAL:** "Uma entrada carregava uma nota de trabalho num campo que o estilo bibliografico
imprime. Nada da referencia esta errado; a nota nao pertence a lista publicada e sai no deposito."
*Fonte: src_fix/references.bib, entrada liu2019dwa; impresso na p. 95 do build de defesa*

### [DECIDIDO] · ERR-4 · Duas entradas do `.bib` nao sao citadas por nenhum ponto do texto

**ACAO NECESSARIA:** decidir por entrada. `belkin2003laplacian` (Laplacian Eigenmaps) e
`santos2024urban` (a dissertacao de 2024 do PPGCC) estao no `references.bib` e **nao** aparecem em
nenhum `\cite` da arvore viva. Nao imprimem (a lista tem 98 entradas para 100 no arquivo), entao nao
ha nada errado no PDF; o que existe e ruido no arquivo de deposito.
**DADOS:** medido nesta sessao: 100 entradas, 98 citadas, 0 chaves duplicadas, 98 referencias impressas.
O `santos2024urban` foi adicionado especificamente porque o Apendice E apoiava uma afirmacao
institucional num precedente de 2024 (comentario de proveniencia no `.bib`); medido, o apendice de etica
vivo cita `cho2011gowalla`, `jure2014snap`, `wongso2025massivesteps` e `luca2021mobilitysurvey`, e **nao**
cita o precedente. Ou seja: a afirmacao que motivou a entrada saiu do texto, e a entrada ficou.
**RESPOSTA FINAL:** "Duas entradas ficaram no arquivo depois que as frases que as citavam foram
reescritas. Elas nao imprimem na lista de referencias, entao nenhum leitor ve uma referencia sem
chamada; e limpeza de arquivo para o deposito."
*Fonte: src_fix/references.bib; chapters/apx_e_ethics.tex (citacoes vivas)*

### [FECHADO] · ERR-5 · Seis entradas do `.bib` sem identificador em campo, tres delas resolviveis agora

**ACAO NECESSARIA:** adicionar tres DOIs que foram resolvidos nesta sessao contra a fonte de registro,
e deixar as outras tres declaradas como sao:
- `holm1979` -> **10.2307/4615733** (OpenAlex, aberto nesta sessao; Scandinavian Journal of Statistics,
  vol. 6, pp. 65-70, 1979, bate com o que a entrada ja declara).
- `senushkin2023aligned` -> **10.1109/cvpr52729.2023.01923** (registro DOI do Crossref aberto nesta
  sessao; CVPR 2023, pp. 20083-20093, pagina identica a entrada).
- `liu2023famo` -> **10.52202/075280-2500** (registro DOI aberto; NeurIPS 36, pp. 57226-57243; a
  entrada hoje **nao** tem campo de paginas).
- `jure2014snap`: **nao existe DOI**. O registro do OpenAlex para a colecao SNAP nao carrega DOI nem
  venue; a URL em `howpublished` e o identificador de registro. Deixar como esta.
- `wei2022finetuned`: a versao ICLR 2022 nao tem DOI registrado em nenhuma das duas fontes; o que existe
  e o preprint (arXiv:2109.01652). A URL do OpenReview na entrada **e** o identificador resolvivel.
- `santos2024urban`: **[VERIFY]**, o registro do repositorio institucional nao foi aberto nesta sessao.
  Os metadados vieram da folha de rosto do PDF. Se a entrada permanecer (ver ERR-4), abrir o registro.
**DADOS:** medido sobre as 100 entradas: **87** carregam DOI ou identificador arXiv em campo; das 13
restantes, **7** trazem o identificador no proprio comentario de proveniencia e **6** nao trazem em
lugar nenhum. Nenhuma chave duplicada. Nota de contexto: o estilo bibliografico imprime DOI em apenas
5 pontos da lista, entao adicionar DOI ao `.bib` e questao de registro, nao de aparencia.
**RESPOSTA FINAL:** "A bibliografia tem cem entradas, sem chaves duplicadas, e oitenta e sete carregam
identificador em campo. Das treze restantes, sete registram o identificador no comentario de
proveniencia da propria entrada, e seis nao tinham: tres foram resolvidas contra a fonte de registro,
duas nao possuem identificador registrado em nenhuma fonte, e uma segue marcada para verificacao."
*Fonte: src_fix/references.bib; REVISION_PLAN.md §17.2 (a bibliografia como superficie nao coberta pelo painel)*
### [APLICADO] · ERR-6 · A frase de cobertura de busca atribui errado a origem da taxa de aprendizado de Florida e California

**ACAO NECESSARIA:** em `chapters/5_mobiwac/05_setup.tex:53-55`, a clausula *"at Florida and California
it was not varied, so those two carry the value the smaller searches selected"* atribui aos conjuntos
pequenos um valor que eles nao selecionaram. Correcao minima: trocar por "carry the value of the
large-dataset tier" ou nomear a origem real (a triagem de uma dobra em Texas). Nao muda nenhum numero
nem nenhum veredito, e **reduz** o que a frase reivindica.
**DADOS:** o registro de configuracao que a frase cita foi aberto nesta sessao.
`docs/studies/closing_data/v18/FINAL_SETTINGS.md:77`, familia (a), modelo dedicado de categoria, le
verbatim: `| max_lr | AL **0.0025**, AZ **0.0005**, IST **0.0005** | **0.005** | [5f] small; [1f] TX
flat 0.005-0.01 |`. Ou seja: as buscas dos conjuntos pequenos selecionaram **0,0025 e 0,0005**, e o
valor **0,005** que Florida e California carregam e o do nivel dos conjuntos grandes, creditado a
triagem de uma dobra em Texas. A legenda de grau esta na linha 12 do mesmo arquivo: `[5f]` significa
cinco dobras com teste pareado, `[1f]` significa triagem de uma dobra. O texto vivo esta correto em
tudo o mais dessa frase: a busca de taxa de aprendizado **foi** em cinco dobras em Istanbul, Alabama e
Arizona e em uma dobra em Texas, e Florida e California **nao** a variaram.
**RESPOSTA FINAL:** "A cobertura por botao e por conjunto esta correta: taxa de aprendizado buscada em
cinco dobras nos tres conjuntos menores, em uma dobra em Texas, e nao variada em Florida e California.
O que a frase atribui mal e a origem do valor que esses dois carregam: ele vem do nivel dos conjuntos
grandes, nao da selecao dos menores, que escolheram valores dez vezes menores. E uma frase de
proveniencia a corrigir no deposito, e a correcao enfraquece a frase em vez de fortalece-la."
*Fonte: chapters/5_mobiwac/05_setup.tex:53-55; docs/studies/closing_data/v18/FINAL_SETTINGS.md:12,:77*

### [APLICADO] · ERR-7 · A mesma frase grada Florida como "fewer folds" na busca de tamanho de lote

**ACAO NECESSARIA:** na mesma frase (`:52-53`), a clausula *"over five folds at Istanbul, Alabama and
Arizona and on fewer folds at Florida and Texas"* grada Florida junto com Texas. Pelo registro, so
**Texas** e triagem de uma dobra na familia do dedicado de categoria. Correcao: nomear apenas Texas, ou
declarar qual geracao de medicao esta sendo gradada.
**DADOS:** `FINAL_SETTINGS.md:76`, familia (a): `| batch size | **8192** | **8192** | [5f] AL; [1f] TX
(...) |`. A anotacao de dobra unica esta em Texas, e nenhuma em Florida. A linha 97, familia (c),
modelo conjunto, e onde Florida aparece como `[1f] FL **null**`, isto e, a triagem de uma dobra em
Florida pertence a busca do **modelo conjunto**, e a frase a atribuiu a busca do **dedicado**. As duas
buscas estao na mesma frase do texto, uma sentenca adiante da outra, o que explica a troca.
**RESPOSTA FINAL:** "A triagem de uma dobra em Florida pertence a busca do modelo conjunto, nao a do
dedicado de categoria; no dedicado, a anotacao de dobra unica e de Texas. As duas buscas sao descritas
em sentencas vizinhas e a graduacao de dobra migrou de uma para a outra. E correcao de deposito, e nao
altera a cobertura declarada: tamanho de lote buscado nos seis conjuntos na familia do dedicado de
categoria, e em quatro na do modelo conjunto, com Texas e California carregando configuracao
transferida."
*Fonte: chapters/5_mobiwac/05_setup.tex:52-53; docs/studies/closing_data/v18/FINAL_SETTINGS.md:76,:97*


---

## §4 · ORAL: nao muda o texto; e resposta que o autor da na arguicao

### [FECHADO] · ORA-1 · Por que o Capitulo 5 diz reproduzir o manuscrito revisado, e nao o submetido

**ACAO NECESSARIA:** nenhuma edicao. O contrato foi decidido e aplicado; o que resta e saber explica-lo,
porque um membro de banca que compare os dois PDFs vera numeros diferentes.
**DADOS:** medido nesta sessao, tabela por tabela. Os numeros do Cap. 5 sao **identicos aos do
manuscrito revisado** (`articles/[mobiwac]/src_fix/tables/tbl3_results.tex`) nos seis conjuntos, e
**diferem do submetido** (`.../src/tables/`) nos seis. Exemplos: regiao em California 65,69 no submetido
contra **64,54** no revisado e no capitulo; regiao em Texas 67,06 contra **66,15**. O prefacio do Cap. 5
declara *"in the revised form that followed the final evaluation"*, mantendo o status
*"submitted to MobiWac 2026, under review at the time of writing (EDAS #1571313639)"*. A §1.5 declara,
de forma mais geral, que o conteudo segue as versoes publicadas ou, para o artigo em revisao, o
manuscrito submetido, a formulacao generica da §1.5 e a especifica do prefacio do Cap. 5 nao dizem
exatamente a mesma coisa, e a do prefacio e a que governa aquele capitulo.
**RESPOSTA FINAL:** "O Capitulo 5 reproduz o manuscrito na forma revisada apos a avaliacao final, e o
prefacio diz isso. O status de submissao continua o mesmo, submetido e em revisao, porque a decisao dos
revisores nao chegou. A revisao superseda os numeros da versao submetida e pode ser enviada ao evento; o
Apendice B registra que as correcoes de escopo foram aplicadas tambem na fonte submetida. Se comparar
com o PDF submetido, os numeros de regiao em California e Texas sao os que mais se movem, e para baixo:
de 65,69 para 64,54 e de 67,06 para 66,15."
*Fonte: chapters/5_mobiwac.tex:29; chapters/apx_b_errata.tex (contrato de identidade); REVISION_PLAN.md §11.1, §14.3*

### [FECHADO] · ORA-2 · Por que o Apendice G (controle de contagem de parametros) esta no suplemento e nao no volume principal

**ACAO NECESSARIA:** nenhuma. Decisao tomada e aplicada; a pergunta e por que.
**DADOS:** o apendice imprime como **Apendice G**, pp. 24-26 do suplemento de 27 pp, e o proprio texto
declara a razao: *"reported in the supplementary volume because the main volume's category results are
bounded within half a point, the same band this control's own effects fall near, so it does not carry an
argument there"*. Ele declara tambem o proprio escopo: Alabama com o protocolo completo de quatro
sementes, California com uma semente, esta limitada por custo por dobra trinta e seis vezes maior.
**RESPOSTA FINAL:** "O controle testa a explicacao concorrente, capacidade em vez de representacao, e
responde em Alabama: multiplicar por 6,7 (era 6,5 antes da recontagem de 2026-09-02) os parametros
treinaveis do modelo dedicado **baixa** o
macro-F1 em 0,53 ponto, com teste pareado sobre quatro sementes separando a diferenca de zero,
p = 0,0011, e direcao unanime nas vinte dobras. Em California os tres bracos ficam dentro de 0,06 ponto
numa semente so, e isso e reportado como leitura de semente unica, sem teste e sem media entre
conjuntos. Esta no suplemento porque os resultados de categoria do volume principal estao limitados a
meio ponto, a mesma faixa dos efeitos deste controle, entao ele nao sustenta argumento la."
*Fonte: chapters/apx_i_parameter_count_control.tex; suplemento pp. 24-26; REVISION_PLAN.md §11.2, §14.4*

### [FECHADO] · ORA-3 · A convencao de selecao de epoca e o que ela custa ao modelo conjunto

**ACAO NECESSARIA:** nenhuma. Esta divulgado na prosa enviada, e e a pergunta metodologica mais provavel
da banca.
**DADOS:** medido na p. 80-81 da defesa. O texto declara a convencao (um artefato salvo por dobra, lido
na epoca selecionada pela validacao; cada dedicado na melhor epoca da sua tarefa, o conjunto na epoca
escolhida pelo escore conjunto, media geometrica das duas metricas) e declara o que a alternativa
mudaria: ela e **mais favoravel ao modelo conjunto**, por no maximo **0,23 macro-F1 e 0,93 Acc@10** como
maior lacuna em uma semente, e e favoravel o suficiente para **mudar vereditos**, transformando mais
quatro celulas de categoria e mais duas de regiao em melhorias que sobrevivem a mesma correcao de Holm.
E declara por que a mais estrita foi escolhida: a alternativa nao descreve nenhum modelo salvo.
**RESPOSTA FINAL:** "Reporto a convencao que um sistema em producao pode servir: um checkpoint por dobra.
A alternativa, ler cada tarefa na sua propria melhor epoca, descreve dois checkpoints como se um sistema
produzisse os dois. Ela e mais favoravel ao meu modelo, por no maximo 0,23 macro-F1 e 0,93 Acc@10 na
maior lacuna de uma semente, e mudaria vereditos: quatro celulas de categoria e duas de regiao passariam
a melhorias sob a mesma correcao. Escolhi a mais estrita por isso, e o texto declara os dois lados."
*Fonte: chapters/5_mobiwac/06_results.tex; defesa pp. 80-81; REVISION_PLAN.md §1.3*

### [FECHADO] · ORA-4 · Provenancia: trinta celulas sem SHA de commit, e por que nao serao preenchidas

**ACAO NECESSARIA:** nenhuma. Fechado como **irrecuperavel**, com a causa registrada.
**DADOS:** as 30 celulas sem `commit_sha` sao **todas** de sementes 7 e 100, nenhuma produzida
localmente. Duas sessoes independentes confirmaram que nao ha rota de recuperacao:
`summary/full_summary.json` e os JSON de resultado do p1 **nao carregam** chave de git, commit ou host,
verificado diretamente. O achado nao e apenas que o tar remoto nao tinha `.git`. Onde ha evidencia, ela
foi usada e marcada: tres celulas receberam `lane_host` declarado a partir de heartbeat observado, com
bloco `post_hoc_fields` nomeando quem preencheu e com que base; as outras 40 ficaram **declaradamente
indeclaradas em vez de supostas**.
**RESPOSTA FINAL:** "A rastreabilidade de codigo esta completa para as celulas produzidas localmente e
irrecuperavel para as rodadas alugadas: os artefatos daquelas rodadas nao gravaram chave de git nem de
host, verificado nos dois arquivos que poderiam carrega-la. Preencher aquele campo seria inventar
provenancia, entao ele ficou vazio e declarado. Nenhum numero do quadro depende disso: os resultados
sao sonoros; o que falta e a prova de qual commit os gerou."
*Fonte: docs/studies/closing_data/v18/GAPS.md §2, A6, A7, A8, "On GAP A, from this side" (linhas 548-554)*

### [FECHADO] · ORA-5 · Efeito de hardware entre A40 e H100: no ou abaixo do quantum de reporte

**ACAO NECESSARIA:** nenhuma. Divulgacao, nao correcao.
**DADOS:** a mistura de hardware e **universal**, nao um defeito de uma celula: sementes 0 e 1 sao
locais e 7 e 100 alugadas, nos seis conjuntos e nas tres familias. Isso retira "rodar de novo a celula
estranha" como opcao. A medicao apertada, mesma dobra, mesma semente, mesmos dados, mesmo codigo
(California semente 100, dobra 0): Acc@1 **0,3344** nas duas maquinas, Acc@10 **0,6283** nas duas, MRR
**0,4346** nas duas; o desvio entre hardwares que motivou a preocupacao e de cerca de **0,086 pp**.
**RESPOSTA FINAL:** "As sementes correram em duas classes de GPU, e isso vale para todos os conjuntos e
todas as familias, nao para uma celula isolada. Onde a mesma dobra foi medida nas duas maquinas, Acc@1,
Acc@10 e MRR coincidem nas quatro casas decimais. O desvio entre hardwares esta no ou abaixo do quantum
com que reporto, e por isso e declarado em vez de corrigido."
*Fonte: docs/studies/closing_data/v18/GAPS.md A3 (linhas 292-312)*

### [FECHADO] · ORA-6 · Os dezesseis probes de gate que continuam vermelhos na arvore enviada

**ACAO NECESSARIA:** nenhuma edicao. Cada um dos 16 vigia uma frase que a revisao do autor reescreveu,
e o probe ficou apontando para a string antiga; e divida tecnica do instrumento, nao defeito de texto.
**DADOS:** re-medido nesta sessao com o gate re-apontado para `src_fix`, com controle validado nos dois
sentidos. Em `src`: **200 de 236 probes valem, 28 nao aplicados**. Em `src_fix`: **212 de 236 valem, 16
nao aplicados**, mais 6 nao probeaveis por processo e 1 retirado pelo autor. O conjunto dos 16 medidos
e **exatamente** o conjunto que o `REVISION_PLAN.md` §16 tabula, item por item: nenhum a mais, nenhum a
menos. Os 12 que `src_fix` fecha em relacao a `src` sao A9-diss, COD-016b, R10-blq2, R10-blq3b,
R13-leak4th, R13-leak4th2, R13-limitcount, R13-noratio, R13-sweepscope2, R9-apxf7, R9-apxfn, R9-apxfold.
**RESPOSTA FINAL:** "A suite de verificacao tem duzentos e trinta e seis checagens. Duzentas e doze valem
na arvore entregue. As dezesseis restantes vigiam frases que eu proprio reescrevi na revisao: a
checagem procura a redacao anterior e nao a acha, o que reporta corretamente que a mudanca que ela
guardava nao esta mais no formato que ela conhecia. Nao e um defeito no texto; e um instrumento que
precisa ser reapontado."
*Fonte: src_fix/REVISION_PLAN.md §16; medicao desta sessao com src_utils/check_audit_claims.py*

---

## §5 · MORTO: a versao enviada resolveu, com a medicao ao lado

Uma linha por item. A coluna **medicao** e a prova; nenhum destes pede acao.

| item | o que afirmava | medicao no fonte vivo / no PDF enviado | veredito |
|---|---|---|---|
| **PENDENCIAS 2.1** | "56 marcadores `[NEEDS SIGN-OFF]` no fonte" | **34** em `src_fix`, e 34 tambem em `src`; 33 seguem a forma numerada e 1 nao; **32 anotados `CLOSED`**, **1 anotado `OPEN`** (item 46). Em `src_clean`: **0** | MORTO, a contagem de 56 esta invalidada; so 1 marcador segue aberto |
| **PENDENCIAS 2.27 item 1** | "28 blocos `[ORPHANED 2026-08-02]`" | **16** em `src_fix` e em `src` (10 no Cap. 2, 3 no `preamble`, 1 em cada de `main_extra`, Cap. 1, Cap. 3); **0** em `src_clean` | MORTO, a contagem de 28 esta invalidada |
| **PENDENCIAS 2.27 item 2** | "54 marcadores continuam abertos, 7 no Cap. 2, 8 no Cap. 6, 6 no Apendice A" | 34 marcadores, dos quais 6 no Cap. 2, 5 no Cap. 6, 1 no Apendice A, e **32 anotados CLOSED** | MORTO |
| **PENDENCIAS 2.27 (C)** | "builds 106/103/107/22 pp" | **119 / 114 / 27 / 120 pp** (defesa / deposito / suplemento / programa) | MORTO, a versao cresceu treze paginas desde a medicao |
| **PENDENCIAS 2.32** | "o Apendice E nao e citado por nenhum capitulo; zero `\ref` em prosa viva" | **1 `\ref` vivo**, em `chapters/2_fundamentals.tex`, e imprime na **p. 26** da defesa como "Appendix E gives the exact composition and its width". O apendice imprime como **Apendice E, p. 109** | MORTO, a saida (b) que o item oferecia foi aplicada |
| **PENDENCIAS 2.31** | dois grupos de referencia cruzada entre capitulos ficaram fora | fechado na rodada 14 por decisao registrada do autor; probes `STL-01` a `STL-05` valem na medicao desta sessao | MORTO |
| **PENDENCIAS 4.2** | 15 itens `[YOU APPLY]` em duas ondas | os probes que guardam essas aplicacoes valem em `src_fix`; nenhum dos 16 vermelhos remanescentes e um `[YOU APPLY]` | MORTO |
| **NEEDS_SIGN_OFF 1-45, 47-56** | 55 itens de aval | **32** marcadores numerados anotados `CLOSED` no fonte; os outros tiveram o marcador **removido** do `.tex` (itens 6, 8, 47-53 entre eles). So o 46 segue anotado `OPEN` | MORTO |
| **REVISION_PLAN §15.5** | a checagem de rotulos congelados foi sobre-afirmada | re-executada nesta sessao contra os `.aux` do build de 119 pp: **9 de 9 rotulos congelados batem, 0 divergencias** (`ch:cbic` 3, `ch:courb` 4, `ch:mobiwac` 5, `sec:intro:organization` 1.5, `fig:courb:distribuicao` 3, `tab:courb:dataset` 5, `tab:courb:category` 6, `tab:courb:next` 7, `tab:mobiwac:results` 10). O parser foi validado: 131 entradas `\newlabel` lidas, nao zero | MORTO |
| **REVISION_PLAN §17.3** | a contagem de celulas abaixo do dedicado estava errada (seis em vez de oito) | a tabela corrigida do proprio §17.3 traz **4 celulas negativas em categoria e 4 em regiao, 8 de 12, sobre 6 conjuntos**; o texto enviado nao carrega nenhuma contagem de celulas negativas (medido: "of the twelve" tem **0** ocorrencias nos builds), entao o defeito viveu so em comentario de fonte | MORTO |
| **GAPS B, E, F** | tres lacunas de rastreabilidade e de relatorio | fechadas com evidencia por execucao, nao por inspecao (o item 2 do GAP E foi verificado escondendo uma celula e vendo o total cair de 20 para 15, e restaurando); `TASKS.md` criado | MORTO |
| **_history/_round6/VERIFY_LIST item 14** | "o intervalo de paginas do `nash`, o unico identificador que ninguem conseguiu resolver" | resolvido nesta sessao: `proceedings.mlr.press/v162/navon22a.html` (HTTP 200) declara **PMLR 162:16428-16446, 2022**; o `.bib` carrega `pages = {16428--16446}`. **Batem** | MORTO, o `[VERIFY]` fecha |
| **LEFT_OUT LO-9 (metade `[VERIFY]`)** | "o intervalo de paginas nao esta confirmado por nenhuma fonte de registro alcancavel" | idem acima: a fonte de registro foi aberta e confere. A `tables/frame/bib_errata.tex` ja declarava "The page range was already correct here and is unchanged" | MORTO |
| **LEFT_OUT LO-10** | "41 linhas de regra puramente decorativas" a remover | **0** linhas decorativas (`%======` ou `%------`) na arvore viva; a passagem da rodada 7 as removeu. A metade de relocacao continua recomendada contra, e o autor pode reabrir se quiser o volume reduzido | MORTO na metade das 41 linhas |
| **CONSIDERATIONS GER-09** | "faltam a taxonomia dos balanceadores, a linhagem, e a definicao de conflito na prosa do §2.3" | os tres estao no texto enviado: §2.3.4 abre com "Balancing methods differ in whether they modify loss weights or task-gradient directions" e separa as duas classes; a linhagem e creditada por nome (Kendall, Chen, S. Liu, B. Liu, Sener e Koltun, Yu, Navon, Senushkin); e o conflito e **definido** na Definicao 2.13 com a equacao do cosseno. O Cap. 2 carrega **13 ambientes de definicao** | MORTO |
| **CONSIDERATIONS AUT-01** | "a fundamentacao de MTL precisa de otimalidade de Pareto?" | o texto trata dominancia, otimalidade e estacionariedade de Pareto, e fecha com a frase de contencao: "This dissertation therefore claims no Pareto property for its models" | MORTO |
| **fundamentals/OPEN_QUESTIONS item 1** | "nao me deixe citar um numero de `song2010limits` ate que alguem leia o PDF" | o PDF esta no repositorio (`science/articles/201002-19_Science-Predictability.pdf`) e foi **lido nesta sessao**: DOI 10.1126/science.1177170, Science 327, 1018 (2010), e a frase *"we find a 93% potential predictability in user mobility across the whole user base"*. O `.bib` declara Science 327(5968):1018-1021, 2010, mesmo DOI. As tres sentencas vivas que citam o numero dizem "about 93 percent", com o qualificador "potential predictability" | MORTO, verificado em primeira mao |
| **LEFT_OUT LO-2, LO-3, LO-4, LO-5, LO-7, LO-8** | seis omissoes deliberadas com decisor e data | cada uma tem decisor nomeado e nada pendente; a LO-7 e a LO-8 sao decisoes de falha-fechada (nao regenerar figura por regra inventada) | MORTO |

---

## Ledger de fontes desta auditoria

**Registros lidos integralmente** (nenhum amostrado): `src_utils/LEFT_OUT.md` (430 linhas, 13 entradas),
`src_utils/PENDENCIAS.md` (746), `src_utils/_history/NEEDS_SIGN_OFF.md` (2.206, 56 itens numerados),
`src_utils/CONSIDERATIONS.md` (913, 46 blocos), `src_utils/_history/_round6/VERIFY_LIST.md` (1.316, 21 itens),
`src_fix/REVISION_PLAN.md` (903), `docs/studies/closing_data/v18/POSTPONED.md` (138, P1-P6),
`docs/studies/closing_data/v18/GAPS.md` (554, A-F + §7 + nove adendos), tres
`src_utils/adaptation_ledgers/*.md`.

**Fontes de registro abertas nesta sessao** (para os itens de citacao):
`proceedings.mlr.press/v162/navon22a.html` (HTTP 200), `api.crossref.org` (registros DOI de
`senushkin2023aligned` e `liu2023famo`), `api.openalex.org` (com chave de API; `holm1979`,
`jure2014snap`, `wei2022finetuned`), `articles/CBIC___MTL/sections/conclusion.tex` (redacao publicada),
`articles/[mobiwac]/src/` e `src_fix/` (as duas versoes do manuscrito),
`science/articles/201002-19_Science-Predictability.pdf` (5 pp, lido).

**Bandeiras `[VERIFY]` que esta auditoria deixa abertas:**

1. **`santos2024urban`**, o registro do repositorio institucional nao foi aberto; metadados vindos da
   folha de rosto do PDF. Se a entrada sair do `.bib` (ERR-4), a bandeira morre com ela.
2. **`wang2025hamtl`**, o resumo continua nao aberto (Crossref e OpenAlex nao entregam, `oa_status`
   fechado, a chave Springer devolve 401, o `link.springer.com` redireciona para autenticacao). Os
   ATRIBUTOS estao verificados contra o Crossref, sete autores; a ALEGACAO nao. Registrada em
   `CONSIDERATIONS.md` §5 item 1 e nao reaberta aqui.
3. **`kohavi1995crossval`**, segue com a nota PLAUSIBLE da auditoria anterior; nenhuma decisao desta
   auditoria dependia dela.
4. **Massive-STEPS**, continua preprint (arXiv:2505.11239v3); a busca por titulo no Crossref nao achou
   versao revisada, o que e evidencia fraca, e o Semantic Scholar devolveu 429 e nao foi repetido.
5. **A convencao de media do F1 do sweep do HGI** (macro contra ponderada), o `[VERIFY]` original
   segue no fonte e nao foi resolvido nesta sessao.
6. **Os 13 `[VERIFY]` vivos em `src_fix`**, 4 no Cap. 2, 2 no Apendice A, 2 no Apendice de cosseno, e
   um em cada de Cap. 1, Apendice B, `3_cbic/results`, `5_mobiwac/05_setup`, `5_mobiwac/07_discussion`.
   Todos vivem em comentario `%` e **nenhum imprime**. Esta auditoria leu os 13 e nenhum e uma afirmacao
   nao sustentada em prosa; sao pedidos de decisao ou anotacoes de escopo.

**O que esta auditoria NAO cobriu**, declarado por item e nao por atacado:

- **Os numeros dos Capitulos 3 e 4 contra os artigos publicados.** O `REVISION_PLAN.md` §17.2 registra
  isso como superficie nao coberta pelo painel de revisao, e esta auditoria tambem nao a cobriu: verificar
  cada valor das tabelas dos Caps. 3 e 4 contra os PDF publicados e um trabalho distinto.
- **Os 21 itens `[I DECIDE]` do §4.1 um por um.** Foram contados e localizados, e dois (AUT-26, AUT-38)
  foram medidos; os outros dezenove nao foram remedidos individualmente contra o fonte vivo.
- **A prosa dos 46 blocos de `CONSIDERATIONS.md`.** Foram tabulados por ID e tres foram remedidos
  (GER-09, AUT-01, FAB-32); os demais nao.
