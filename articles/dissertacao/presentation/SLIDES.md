# SLIDES.md — o deck da defesa, slide a slide

> **O que este documento é.** O conteúdo de cada slide do deck de defesa: o que vai na tela, o que
> se fala, de onde vem cada número. Escrito 2026-08-23 a partir de
> [`PLANO_FLUXO_DEFESA.md`](_preparacao/PLANO_FLUXO_DEFESA.md), que é a lei da estrutura — este documento não
> redesenha nada, escreve o que aquele especifica.
>
> **As três leis governam cada palavra**: [`../WRITING_LAW.md`](../WRITING_LAW.md) (registro, lei
> dos verbos, banidos), [`../GLOSSARY.md`](../GLOSSARY.md) (**fail-closed**) e
> [`../AGENT_GUARDRAILS.md`](../AGENT_GUARDRAILS.md) (protocolo de número e de afirmação).
>
> **Idioma:** tela em **inglês**, fala em **português**.
>
> **Fonte de todo número:** a árvore entregue, `../src/`. Nenhum número foi re-derivado, e
> **nenhum foi obtido subtraindo células** — a Tabela 10 imprime Florida 37,35 e 37,55, cuja
> subtração dá 0,20, mas o delta entregue é **+0,19**.

>
> 🛑 **CONVENÇÃO OBRIGATÓRIA DO CAMPO `Fala (PT)` — quebrá-la mete texto de bastidor no roteiro que
> o autor lê em voz alta.**
>
> **A fala vai ENTRE ASPAS. Toda anotação editorial fica FORA delas** — o parentético de versão
> antes da aspa de abertura, a nota de revisão depois da de fechamento:
>
> ```
> - **Fala (PT):** *(v3, 26/08 — o que mudou)* "a fala, inteira, entre aspas."
>   ⚠ a nota de revisão, aqui, fora das aspas.
> ```
>
> **Por que isto é lei e não estilo:** o extrator do `SPEECH` lê o campo inteiro. Em 26/08, **doze
> blocos** carregavam anotação minha dentro dele, e o roteiro impresso traria *"(v3, 26/08 — a
> primeira frase foi refeita…)"* no meio do que o autor diria em voz alta. **Ninguém viu, de nenhum
> lado:** no `SLIDES.md` a anotação está formatada e parece óbvia; no `.tex` ela não existe; só
> aparece no que o extrator produz, e o `SPEECH` estava desatualizado.
>
> O extrator (`build_speech_1_extract.py:53-68`) hoje tira o editorial e **depois** procura as
> aspas — nessa ordem, porque uma nota de revisão pode ter aspas internas. **Mas ele cai para o
> campo inteiro quando não há aspas.** É o `fallback` que a convenção protege: **um bloco sem
> aspas mais uma anotação = vazamento silencioso.**

## ⚠ Estado, 2026-08-26 — leia antes de usar este arquivo

Cópia pré-migração em [`archive/SLIDES_PRE_MIGRACAO_2026-08-26.md`](archive/SLIDES_PRE_MIGRACAO_2026-08-26.md).

### O que foi corrigido

1. **Os `S<n>` NÃO são o número que aparece no slide, e não há fórmula de conversão.** O `S1` é a capa,
   que não é numerada, e a reordenação da Seção 2 moveu blocos **sem renumerar**, porque ~130
   referências cruzadas internas apontam para eles pelo número. Cada bloco carrega agora o campo
   **`Slide impresso:`** logo abaixo do título — **é ele que a banca vê e é ele que o
   `considerations.md` usa.** *(Exemplos do descompasso: `S8` → impresso **10** · `S13` → **6** ·
   `S51` → **47**.)*
2. **Faltava um bloco:** o segundo frame de *Architecture or representation?* (a arte da Fig. 2 do
   Cap. 4) existia no `main.tex` desde a construção e nunca teve entrada aqui. Criado como **`S26b`**.
3. **A Fase A da cirurgia foi executada e este arquivo foi reancorado a partir do PDF construído**,
   não de uma conta. Ver abaixo.

### A cirurgia, executada em 2026-08-26 (Fases A e B1)

**Saíram três slides** (`AUT-2`, `AUT-7`): os antigos impressos **6** *(The contribution, in one
block — a §8.13 do PLANO foi revogada)*, **18** *(Setup, and the protocol declared)* e **28**
*(The caveat, then the number)*.
**Um foi movido:** *The geometry of the vectors* passou a abrir a subseção de resultados.
**Dois viraram um** (`AUT-9`, Fase B1): *What is predicted, and what is not* ⊕ *One static task, one
sequential task* → o novo **`S5b` · The tasks**, impresso **6**, na Seção 2.

| | original | pós-A | **pós-B1** |
|---|---:|---:|---:|
| páginas do PDF | 111 | 107 | **106** |
| frames | 103 | 100 | **99** |
| slides impressos | 54 | 51 | **50** |
| `Overfull \vbox` | 25 | 25 | **25** |
| hyperlinks órfãos | 0 | 0 | **0** |
| páginas acima de 0,93 | 18 | 18 | **18** |

**Os cinco blocos consumidos estão preservados no fim deste arquivo**, sob `# Blocos REMOVIDOS`.

> 🛑 **Duas regressões conhecidas, medidas e ainda abertas:**
> 1. **o slide 3** (*The question*) foi de **0,947 para 0,998** de tinta ao receber a linha do
>    *next place* — **a última linha fica cortada na borda inferior, agora, no deck.** A reforma do
>    slide (tirar a tabela do veredito) mais que paga; **mas se ela não acontecer, essa linha tem de
>    sair.** Não é surpresa: foi prevista antes de aplicar e medida depois;
> 2. **o slide 6** (*The tasks*) ficou em **0,930** — dentro do limite, **sem folga**. Ele não
>    absorve mais nada; se um item futuro quiser entrar, algo sai.

### Verificado nesta reancoragem

**51 blocos** na trilha principal (capa + 50), **ordem do arquivo == ordem do deck**, impressos
**1 a 50 sem lacuna** — conferido por script sobre o arquivo montado. A única divergência de título são os quatro blocos do protocolo (`S41`–`S44`,
impressos 35–38), que aqui se chamam *"Protocol, step N of 4"* e no deck usam um `\frametitle` único
+ `\framesubtitle` — o extrator do `SPEECH` já tem `ALIAS` para esse caso.
*(Uma nota que circulou dizendo que os quatro protocolos são **um** bloco só aqui está errada: são
quatro.)*

## Estado

| | |
|---|---|
| Deck principal | **50 slides impressos** + a capa · **106 páginas** |
| Série B (reserva) | **49 páginas**: o índice **B0** + **48 slides** em sete famílias (B1–B7), fora da contagem e da barra |
| Orçamento declarado | 48 min. ⚠ **a fala escrita soma ~63 min a 140 ppm** — ver `considerations.md` §⏱ |
| Estouro de caixa | **25 páginas com `Overfull \vbox`**. ⚠ **30 slides com folga vertical zero** |
| Ledger | **73 elementos `INTRODUZ`, zero duplicatas** — conferido sobre o arquivo montado |
| Barra de navegação | Introdução · Fundamentos · **MTLnet** · **ST-MTLNet** · **Check2HGI** · Conclusão |
| Fila de mudanças | [`considerations.md`](_preparacao/considerations.md) — §9 traz o conteúdo da Fase B, Seções 1 e 2 |

## `[BLOCO-CONTRIBUIÇÃO]` — a definição única

A regra §8.13 do plano exige que a contribuição apareça **duas vezes com redação idêntica** — cedo
e no fechamento. Antes desta correção as duas cópias divergiam, e **ambas diziam ser idênticas a
uma definição no cabeçalho que não existia**. Agora existe: é este bloco, e **S7 e S51 o
reproduzem palavra por palavra**. Qualquer edição muda os dois.

**Revisto 2026-08-24, por decisão do autor.** A versão anterior tinha duas metades, `Practical` e
`Scientific`, e **nenhuma das duas nomeava o Check2HGI** — a contribuição que dá título à
dissertação. A nova redação segue o grupo **Software** das contribuições entregues
(`src/chapters/1_introduction.tex:432-441`), que é onde a reutilização está enunciada, **com a
ressalva de projeto colada nela**: *"a property of its design rather than a result measured on
further tasks"*. A manchete sobe para uma moldura própria; as duas metades viram blocos de
fragmentos; a ressalva que a §8 regra 13 obriga (*"operational, not computational"*) fica no rodapé,
na tela, nos dois slides.

  > **Practical — what it delivers.** One model, one forward pass, two predictions — one artifact
  > to train, version and deploy, **in place of two**; **operational, not computational**: the joint
  > model is the larger artifact; **Check2HGI is the reusable part** — one vector per visit,
  > independent of the prediction heads on top.
  >
  > **Scientific — what it establishes.** The **input representation** and its **sharing topology**
  > determine **whether** multitask learning helps these POI prediction tasks.

---

---

# sec1-2

# SEÇÃO 1 · Abertura: a pergunta e o escopo (5 min)

> `\section[Introdução]{Abertura --- a pergunta e o escopo}`
> **Aviso de seção (PLANO §3):** nenhum particular do corpus entra aqui. Nada de sete categorias,
> nada de *mahalle*, nenhum nome de estado, **com uma exceção declarada**: a frase do veredito em
> **S4** nomeia Flórida, Texas e Califórnia (PLANO §3, exceção do autor).
> **Orçamento:** 20 + 45 + 55 + 60 + 40 + 40 + 40 = **300 s**.

### S1 · Multitask Learning for POI Classification and Prediction Tasks
- **Slide impresso:** — (capa, `\titleframe`, sem numeração)
- **Seção/subseção:** 1.0 (capa)   **Tempo:** 20 s
- **LEDGER:** INTRODUZ nada (capa)
- **Na tela:** `\titleframe`, os campos copiados caractere a caractere da folha de rosto depositada.
  - **Multitask Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the Check-in-Level Representation**
  - Vitor Hugo De Oliveira Silva
  - Supervisor: Fabrício Aguiar Silva
  - Universidade Federal de Viçosa · Campus Florestal · Pós-graduação em Ciência da Computação
  - August 28, 2026
  - `\titlelogo` NESPeD + `\titlelogo` UFV
- **Fala (PT):** "Bom dia. Meu nome é Vitor Hugo, e vou apresentar minha dissertação de mestrado, orientada pelo professor Fabrício Silva, no PPGCC da Universidade Federal de Viçosa. Um aviso de forma antes de começar: os slides estão em inglês e a fala é em português. Os números na tela são os do documento que a banca recebeu, sem conversão."
- **Proveniência:** título, autor, orientador, local e ano copiados de `src/preamble.tex:226-236`; conferidos contra a folha de rosto de `src/banca.pdf` p. i (`VITOR HUGO DE OLIVEIRA SILVA`; `MULTITASK LEARNING FOR POINT-OF-INTEREST CLASSIFICATION AND PREDICTION TASKS: THE ROLE OF THE CHECK-IN-LEVEL REPRESENTATION`; `Supervisor: Fabrício Aguiar Silva`; `FLORESTAL - MINAS GERAIS`, `2026`).
- **Nunca dizer:** nenhum resultado na capa. Nunca usar o título de um dos artigos como título da dissertação.

### S2 · Human Mobility
- **Slide impresso:** **1**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 1.1   **Tempo:** 45 s
- **LEDGER:** INTRODUZ o gancho: a regularidade da mobilidade e as aplicações
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **Human movement is highly regular**; potential predictability of an individual's next location at about **93 percent** (Song et al., 2010); people return to a small set of places, and travel far less often;
  - Bloco **The caveat, in the same breath**:
    - That estimate is for the next **location** at a coarse spatial resolution. It shows that mobility contains learnable regularity, and it is **not a ceiling** for the metrics reported in this work;
  - What a service acts on, once the next visit is anticipated: recommendation, navigation, transit planning, allocation by area;
- **Fala (PT):** "O ponto de partida é uma regularidade. Os rastros de mobilidade são ruidosos, mas o movimento humano é bastante regular: as pessoas voltam a um conjunto pequeno de lugares, e fazem viagens longas com menos frequência. E isso é mensurável: uma análise de entropia sobre rastros em larga escala estimou a previsibilidade potencial da próxima localização de uma pessoa em cerca de 93 por cento. Faço a ressalva na mesma frase, porque ela importa. Essa estimativa é sobre a próxima localização em resolução grossa, e ela não é teto para nenhuma métrica que eu vou reportar aqui. O que ela mostra é que existe regularidade aprendível. E antecipar o que e o onde da próxima visita é o que sustenta recomendação, navegação, planejamento de transporte e alocação de recursos por área."
- **Proveniência:** 93 percent → `chapters/1_introduction.tex:41-43` e `chapters/2_fundamentals.tex:31-33` (`song2010limits`). Ressalva de não-teto → `chapters/2_fundamentals.tex:33-36` ("does not provide a reference point for the category and region metrics") e `:1691-1694` ("do not serve as ceilings"). Comportamento recorrente → `chapters/2_fundamentals.tex:30-31` (`cho2011gowalla`). Aplicações → `chapters/1_introduction.tex:42-45` e `chapters/2_fundamentals.tex:1899-1901`.
- **Nunca dizer:** "pioneiro", "o primeiro". Nunca apresentar os 93 por cento como teto de nada. Nenhum particular do corpus. Nenhum número nosso.

### S3 · The ground: check-ins and what joint training promises
- **Slide impresso:** **2**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 1.2   **Tempo:** 55 s
- **LEDGER:** INTRODUZ LBSN e check-in (chão didático) · INTRODUZ a promessa operacional do aprendizado multitarefa · **gloss** de transferência negativa (a definição, Def. 2.12, é INTRODUZ em S9)
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **LBSN** — a location-based social network; its record is the **check-in**: a user, a place (point of interest, POI), and a time; **human mobility** research studies how people move through a city; **multitask learning (MTL)** — train related tasks together so they can share information; the operational appeal here: **one model to maintain, one forward pass, both predictions**;
  - Bloco **No guarantee**:
    - Joint training does not guarantee better predictions. Shared parameters can harm one task — a failure known as **negative transfer**;
- **Fala (PT):** "Duas palavras e um risco, antes da pergunta. Uma rede social baseada em localização é uma plataforma em que as pessoas registram os lugares por onde passam. O registro é o check-in, e ele liga um usuário, um ponto de interesse e um instante. É esse detalhe geográfico e temporal que sustenta o estudo de cidades a partir de dados, e a área que estuda como as pessoas se movem pela cidade é mobilidade humana. Agora o aprendizado multitarefa: treinar tarefas relacionadas juntas, para que compartilhem informação. Aqui o apelo é operacional. Um modelo para manter, uma passagem, as duas predições, em vez de dois modelos dedicados. Mas treino conjunto não garante predição melhor. Parâmetros compartilhados podem prejudicar uma tarefa, e essa falha tem nome: transferência negativa. A definição formal dela fica para a próxima seção. Por ora basta o nome, porque é ele que a pergunta seguinte carrega."
- **Proveniência:** LBSN e check-in → `chapters/2_fundamentals.tex:27-29` e `chapters/1_introduction.tex:38-40`; detalhe geográfico e temporal → `chapters/2_fundamentals.tex:28-29` (`silva2019urbancomputing`). MTL, apelo operacional e transferência negativa → `chapters/1_introduction.tex:108-118` ("its operational appeal is a single model to maintain and one forward pass that produces both predictions"; "Shared parameters can harm one task, a failure known as negative transfer").
- **Nunca dizer:** nenhum particular do corpus. Não definir formalmente transferência negativa aqui; a Def. 2.12 é de S9. Nada de "MTL funciona".

### S4 · The question
- **Slide impresso:** **3**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 1.3   **Tempo:** 41 s  *(medido)*
- **LEDGER:** INTRODUZ a pergunta de pesquisa · INTRODUZ a restrição de modelo único · **gloss** do veredito nas superfícies registradas (o ladder de veredito é INTRODUZ em 5.5; `macro-F1` e `Acc@10` aparecem aqui como rótulo do número, e as definições ficam em 2.4 e 5.4)
- **Na tela:** *(v2 · reescrito 2026-08-24 por decisão do autor: os dois blocos de prosa viraram uma **grade de veredito**. Toda superfície de lei foi preservada **verbatim** — verificado string por string, 13 de 13.)*
  - **Does multitask learning help next-category and next-region prediction, and what does the answer depend on?**  ⟵ **v3 · `AUT-19`, 26/08:** perde o parêntese. É `1_introduction.tex:249-250` (objetivo geral) virado para interrogativa, com o `depend on` de `:133-134`.
  - 🛑 **E é SÓ isso na tela.** Por decisão do autor (26/08) saíram: a **restrição de modelo único** (já dita no impresso 2) e a **grade de veredito inteira** (`AUT-3`). O frame é um parágrafo, `\Large`, sem bloco e sem coluna — e **deixou de ser `\specialframe`**, que é a família das transições, porque este é conteúdo. A grade abaixo fica como **registro do que existiu**, não do que está na tela:

  |  | **Outperforms** the dedicated model | **The rest** |
  |---|---|---|
  | **Next region** | **Texas** +1.21 Acc@10 · **California** +1.06<br>*corrected p = 0.00013 and p < 10⁻⁴* | four datasets **stay within the two-point margin, registered before any result was read** — small **deficits, not ties** |
  | **Next category** | **Florida** +0.19 macro-F1<br>*Holm-corrected p = 0.011* | five differences are **equivalent to zero within half a point** |
- **v2 · por que a grade, e o que ela NÃO muda:** o autor apontou que os dois `exampleblock` de prosa estavam densos e a apresentação não estava interessante. **A forma mudou; nenhuma palavra de lei mudou.** Conferido no frame construído: `Outperforms`, `stay within the two-point margin, registered`, `before any result was read`, `deficits, not ties`, `equivalent to zero within half a point`, e os seis números com os seus *p* — 13 de 13 presentes. ⚠ **Os dois *p* de região continuam separados** (`0.00013` e `< 10⁻⁴`), porque combiná-los num só seria re-derivação, que a regra 3 proíbe. ⚠ **As duas colunas têm o mesmo peso visual de propósito:** a coluna *The rest* carrega as ressalvas, e encolhê-la inverteria a **R6** (*ressalva antes da manchete, sempre*) no slide que a banca mais vai escrutinar. Foi por isso que a variante de "três números grandes" foi recusada.
- **Fala (PT):** *(v3, 26/08 — a primeira frase foi refeita junto com a tela; recitava o parêntese que a `AUT-19` removeu)* "A pergunta da dissertacao, literalmente: o aprendizado multitarefa ajuda a predicao da proxima categoria e da proxima regiao, e de que depende a resposta? Ela vem com uma restricao que vale para tudo o que vem depois: um artefato treinado tem de produzir as duas saidas numa passagem so. E uma delimitacao, para ninguem esperar o que nao vem: o proximo lugar exato eu nao predigo, e nenhum capitulo reporta resultado para ele. A resposta eu dou na Secao cinco, com intervalo e com teste, depois de voces terem visto como ela foi obtida."
- **Proveniência:** pergunta → `chapters/1_introduction.tex:249-250` (o objetivo geral, virado para interrogativa) ⊕ o `depend on` de `:133-134` (a seção *Research question*). **As duas metades são texto entregue; nenhuma é paráfrase.** Restrição de modelo único → `chapters/1_introduction.tex:329-330` ("one trained artifact must produce both outputs in one forward pass"). Texas +1.21 e Califórnia +1.06 → `chapters/5_mobiwac/06_results.tex:198-199`; os *p* corrigidos de região → `:223-224`. Florida +0.19 e `corrected p=0.011` → `:209`. "equivalent to zero within half a point" → `:214-217` e `GLOSSARY.md` §4. Frase falada montada só das superfícies registradas, conforme PLANO §5.1b (redação fixa, aprovada pelo autor em 2026-08-22).
- **Nunca dizer:** "empata", "matches", "ties", "semelhante", "a par", "em todos". Nunca aplicar a margem de dois pontos ao eixo de categoria, nem o meio ponto ao eixo de região. Nunca chamar as quatro células dentro da margem de empates. Nunca ler a frase do Resumo entregue. Nunca enumerar aqui os quatro conjuntos dentro da margem: a exceção de nomeação da Seção 1 cobre só Flórida, Texas e Califórnia. Nunca falar a moldura *"sob o desenho final e o protocolo mais estrito dos três"*: ela fica na tela (decisão do autor, PLANO §5.1b).

### S6 · Three studies, in sequence
- **Slide impresso:** **4**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 1.5   **Tempo:** 40 s
- **LEDGER:** INTRODUZ o arco e os três capítulos (título de capítulo, veículo, ano, autoria) · INTRODUZ a armadilha de nomenclatura *"Next-POI Prediction" = próxima categoria*
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **Ch. 3 — Multitask Learning for POI Category and Next-POI Prediction.** CBIC 2025, DOI 10.21528/CBIC2025-1191324. First author; **Ch. 4 — ST-MTLNet: Spatio-Temporal POI Representations.** CoUrb 2026 (SBRC workshop), DOI 10.5753/courb.2026.22960. Contributed the MTLnet baseline; presented at the event; **Ch. 5 — A Check-in-Level Multitask Study of Next Category and Region.** MobiWac 2026, submitted. First author. ``The first reports a negative result, the second identifies its main bottleneck, and the third tests the resulting solution.'';
  - Bloco **Naming trap**:
    - In Chapters 3 and 4, ``Next-POI Prediction'' means the **next category**, not the exact next place;
- **Fala (PT):** "A dissertação é uma coletânea de três artigos, e a ordem deles é o argumento. O texto diz assim: o primeiro reporta um resultado negativo, o segundo identifica o gargalo principal, e o terceiro testa a solução que sai daí. Cada estudo estreita a explicação que a evidência sustenta, e é por isso que a progressão é ela própria parte da contribuição. Veículo, ano e autoria estão na tela. E um aviso de nome antes de seguir, porque ele evita confusão nas duas seções seguintes: o título do Capítulo 3 diz *Next-POI Prediction*, e nos Capítulos 3 e 4 essa expressão quer dizer próxima categoria, não próximo lugar."
- **Proveniência:** títulos de capítulo → `chapters/3_cbic.tex:1`, `chapters/4_courb.tex:1`, `chapters/5_mobiwac.tex:1`. Veículo, DOI, status e declaração de autoria por capítulo → `chapters/1_introduction.tex:349-377`. Frase citada → `chapters/1_introduction.tex:136-139`. Nota de terminologia → prefácio do Cap. 3, `chapters/3_cbic.tex` (bloco `chapterpreface`, "the term ``Next-POI Prediction'' ... denotes the frame's *next category* task"), repetida no prefácio do Cap. 4, `chapters/4_courb.tex`.
- **Nunca dizer:** ampliar o crédito de autoria no Cap. 4 além do que o texto entregue declara. Nenhum resultado dos três estudos aqui.

### S5b · The tasks
- **Slide impresso:** **5**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.2   **Tempo:** 45 s  *(os dois blocos que ele funde somavam 70 s)*
- **LEDGER:** INTRODUZ as quatro tarefas (Defs. 2.6, 2.7, 2.8, 2.9) · INTRODUZ a mudança de par de tarefas entre os capítulos *(herdada do bloco `Two traps`, que deixa de existir)*
- **Na tela:** *(bloco criado 2026-08-26 na Fase B1 — funde os antigos `S5` (impresso 4, "What is predicted, and what is not") e `S17` (impresso 15, "One static task, one sequential task"), ambos preservados no fim deste arquivo.)*
  - Tabela `l | l | l`, corpo `\small`, `\arraystretch{1.35}`:

    | | **reads** | **predicts** |
    |---|---|---|
    | **Category classification** (2.6) | one place | that place's category |
    | **Next category** (2.7) | a history of **N** visits | the category of the next visit |
    | **Next region** (2.8) | a history of **N** visits | the neighborhood-scale unit |
    | **Next place** (2.9) | — | *not predicted in this work* |

  - `alertblock` — **Named to be excluded.** No chapter reports a result for the exact next place.
  - **The pair changes between the studies.** Chapters 3 and 4: **category classification + next category**, one static task and one sequential. Chapter 5: **next category + next region**, two sequential tasks.
- **Fala (PT):** "As tarefas, todas de uma vez, para não voltar a elas depois. Classificação de categoria é estática: lê a representação de um lugar e diz o tipo dele. Próxima categoria e próxima região são sequenciais: leem um histórico de visitas e dizem, respectivamente, o tipo do próximo lugar e a unidade em escala de bairro onde a próxima visita acontece. E o próximo lugar exato está aqui para ser excluído: ele é definido no Capítulo 2 justamente para delimitar o escopo, e nenhum capítulo reporta resultado para ele. Uma coisa muda ao longo da dissertação, e é melhor dizer agora do que surpreender depois: o par de tarefas. Os dois primeiros estudos juntam a estática com a próxima categoria. O terceiro junta duas sequenciais, próxima categoria e próxima região."
- **Proveniência:** Defs. 2.6 a 2.9 → `chapters/2_fundamentals.tex:245-267` e `:313-320`; "an administrative unit at neighborhood scale" → `:275-276`; a mudança de par → `chapters/5_mobiwac/01_introduction.tex` e o bloco "The task pair changes here" do slide 28.
- **O que NÃO entrou, e por quê:** a hipótese do Cap. 3 (*"that difference limits what one shared trunk can do for both"*, do antigo `S17`) **saiu** — ela já é o **suspeito 1** do slide 19, *"Task dissimilarity"*, com outras palavras. **Duplicata, não sacrifício.** E a **restrição de modelo único** saiu (`I10`): fica só no slide 3.
- **`N` em vez de `nove`** (`T6`): a Def. 2.7 usa comprimento genérico, e nove é configuração de experimento — que **difere entre capítulos** (Caps. 3/4: nove não sobrepostas; Cap. 5: nove com stride 1).
- **Nunca dizer:** *"prediz o próximo POI"*. ⚠ Sem particulares do corpus — nem número de classes, nem setor censitário, nem *mahalle*, nem nome de estado: isso é do slide 11.
- ⚠ **Armadilha do template, viva neste frame:** o corpo **não pode abrir com uma chave** (`{\small…`). `\begin{frame}{título}{grupo}` é sintaxe válida, e o beamer lê o grupo como **subtítulo** — as primeiras linhas da tabela vão parar **dentro da faixa colorida do título**, em branco sobre verde, com **log limpo e `pdftotext` extraindo tudo**. Aconteceu neste slide na Fase B1 e **só o render pegou**. Abrir com `\vspace`, `\par` ou `\begin{block}`.


### S13 · Related work: POI prediction
- **Slide impresso:** **6**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.6 (a)   **Tempo:** 60 s  *(medido)*
- **LEDGER:** INTRODUZ o contexto de POI e MTL, o chão comum dos Caps. 3 e 4
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **Next place is the dominant task in the field** — recurrent: ST-RNN, DeepMove, Flashback; attention: STAN, GeoSAN, GETNext; every model named there predicts the **exact next place**, so **none is a direct baseline for the targets studied here**; the pair the first two studies attack: **category classification** and **next-category prediction**; in mobility, MTL has served **next place** almost entirely — MCARNN, CSLSL, iMTL, HAMTL. TME instead applies tree-guided multitask embedding to static semantic POI annotation;
- **Fala (PT):** "Duas telas de trabalho relacionado, e elas são o chão comum dos dois primeiros estudos. A tarefa dominante da área é o próximo lugar exato. A linha vai dos recorrentes, ST-RNN, DeepMove, Flashback, para os de atenção, STAN, GeoSAN, GETNext. Todos eles predizem o lugar exato, e por isso nenhum é linha de base direta para os alvos que eu estudo. O par que os dois primeiros estudos atacam é outro: classificação de categoria e previsão da próxima categoria. E, em mobilidade, o multitarefa foi usado quase inteiramente a serviço do próximo lugar. O MCARNN prevê atividade e lugar juntos; o CSLSL prevê em cascata quando, o quê e onde; o iMTL e o HAMTL seguem a mesma direção. O TME é a exceção que puxa para o outro lado, com anotação semântica estática de ponto de interesse."
- **Proveniência:** `chapters/2_fundamentals.tex:322-336` (a linha do próximo lugar e a frase "none of them is a direct baseline") e `:1396-1418` (MCARNN, CSLSL, iMTL, Halder, TME, HAMTL, IeMTLF; "In mobility, MTL has been used almost entirely in the service of next place").
- **Nunca dizer:** nenhum resultado, nenhum número. Nenhuma afirmação de ineditismo aqui: ela é de S14, e vem escopada.

### S14 · Category and region: means or end
- **Slide impresso:** **7**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.6 (b)   **Tempo:** 54 s  *(medido)*
- **LEDGER:** INTRODUZ o eixo meio × fim · INTRODUZ o mapa de onde saem os métodos externos
- **Na tela:** *(v2 · 141 → ~78 palavras. A frase em itálico é a única frase completa e É a contribuição de posicionamento do slide.)*
  - Bloco **Category and region as a MEANS**: Toward the next place: HMT-GRN, CatDM, CSLSL.
  - Bloco **Category or region as an END**: Activity region (DRRGNN), next category (POI-RGNN).
  - *Among the works reviewed in this dissertation, none treats the next category and the next region as co-equal end targets of one joint model that does not also predict the next place.*
  - Faixa de índice, em fragmento: **next category** POI-RGNN, Markov over category transitions | **next region** HMT-GRN, STAN, ReHDM, Markov-1 floor | **Ch. 3** HMRM, MHA+PE | **Ch. 4** MTLnet.
- **v2 · o que saiu da tela, e onde ficou:** as glosas de cada método (*"a predicted region constrains the search for a place"*, *"a predicted category reduces the candidate set"*, *"a cascade ending at the location"*) → fala do próprio S14. *"(order chosen per dataset)"* do Markov, *"(primary)"* do HMT-GRN, *"over a Markov-1 floor"* e *"MTLnet as its only baseline"* → fala do S14; a faixa manteve os **nomes**, que são o índice que a banca precisa ver, e largou as qualificações. ⚠ **A frase do eixo FICA na tela, inteira**: é a afirmação de originalidade do trabalho e a única coisa deste slide que a banca precisa poder reler.
- **Fala (PT):** "O eixo que separa este trabalho da literatura não é a tarefa, é o papel dela. De um lado, categoria e região como **meio** para chegar ao próximo lugar: o HMT-GRN usa a região prevista para estreitar a busca pelo lugar, o CatDM usa a categoria prevista para reduzir o conjunto de candidatos. Do outro lado, como **fim**: o DRRGNN prevê região de atividade, o POI-RGNN prevê a próxima categoria. E a frase do texto, escopada como ela está escrita: entre os trabalhos revisados nesta dissertação, nenhum trata próxima categoria e próxima região como alvos finais de igual estatuto num modelo conjunto que não prediz também o próximo lugar. O rodapé é o mapa de onde saem os métodos externos que vão aparecer nas tabelas."
- **Proveniência:** eixo meio × fim → `chapters/2_fundamentals.tex:346-353`. Frase de lacuna, escopada, copiada de `chapters/2_fundamentals.tex:1418-1420` e `chapters/1_introduction.tex:429-431`. Mapa dos métodos externos do Cap. 5 → `chapters/5_mobiwac/05_setup.tex:178-182`. HMRM e MHA+PE → `chapters/3_cbic/results.tex:120,122`. Cap. 4 com o MTLnet como única linha de base → prefácio, `chapters/4_courb.tex`.
- **Nunca dizer:** afirmação de ineditismo mais forte do que a do texto. A redação entregue é escopada a "entre os trabalhos revisados nesta dissertação", e a fala mantém o escopo. Nenhum resultado, nenhum número.

### S9 · MTL Fundamentals
- **Slide impresso:** **8**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.2   **Tempo:** 40 s
- **LEDGER:** INTRODUZ compartilhamento rígido (Def. 2.10) · INTRODUZ transferência negativa (Def. 2.12) · INTRODUZ o critério declarado para um balanceador · RETOMA a promessa operacional de 1.2
- **Na tela:**
  - **Hard parameter sharing** (Def. 2.10): every task passes through one shared trunk before branching, and separates only at its own output.
  - **Negative transfer** (Def. 2.12): joint training leaves a task worse than its dedicated single-task model.
  - The criterion this dissertation states: *a balancing method is useful only if it improves on a tuned fixed weighting.*
- **Fala (PT):** "Três definições e um critério. Compartilhamento rígido é a topologia em que todas as tarefas atravessam um mesmo tronco e só se separam na saída de cada uma; o flexível é o extremo oposto --- cada tarefa tem a sua própria rede, e elas são acopladas por uma penalidade. Transferência negativa é o desfecho que se teme: o treino conjunto deixa uma tarefa pior do que o modelo dedicado dela deixaria. O critério está declarado no Capítulo 2, e eu vou cobrá-lo mais adiante: um método de balanceamento só é útil se superar uma ponderação fixa bem ajustada. Guardem essa frase. É ela que decide o que eu posso e o que eu não posso afirmar sobre o balanceador na Seção 3."
- **Proveniência:** Def. 2.10 → `chapters/2_fundamentals.tex:936-941`; Def. 2.12 → `:960-963`; o critério, citado literalmente → `:1391-1393` ("For this dissertation, a balancing method is useful only if it improves on a tuned fixed weighting").
- **Nunca dizer:** nenhuma afirmação de otimalidade de Pareto sobre os nossos modelos: o Cap. 2 recusa a afirmação explicitamente. Nenhum resultado, nenhum número.

### S15 · How places are represented
- **Slide impresso:** **9**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.4a   **Tempo:** 45 s
- **LEDGER:** INTRODUZ a linhagem de representações, no nível de **o que cada degrau resolve** · INTRODUZ o **grafo de Delaunay** como substrato comum aos três · *(os nomes `DGI`, `HGI` e `Check2HGI` aparecem como o último degrau, sem mecanismo; os artefatos continuam INTRODUZ em 3.2A, 4.1A e 5.2)*
- **Na tela:** *(v6 · 2026-08-25 — o slide fundido foi DIVIDIDO EM DOIS por decisão do autor. Este é a linhagem; o `S8` é a ideia.)*
  - `itemize`, um degrau por marcador, com a glosa de cada um:
    - **one-hot identifier** — marks a place or a category by position, and encodes no relationship between identifiers;
    - **skip-gram, DeepWalk, node2vec** — dense vectors whose geometry reflects relationships in the data;
    - **GCN, GAT, GraphSAGE** — those relationships learned through neighborhood aggregation;
    - **graph infomax** *(em alert)* — **DGI**, **HGI** and **Check2HGI**, the three this dissertation uses. *Each chapter explains its own.*
  - `exampleblock` **The substrate the three have in common**: *In all three, a **Delaunay triangulation** joins the places. The **edge weights differ**, and each chapter states its own.*
- **v6 · por que dividir, e o que voltou:** o slide fundido carregava escada, ideia e substrato numa tela só, sem separação visual — na palavra do autor, *"lotado de informação, difícil de ser lido, difícil de acompanhar, as informações não estão separadas"*. **As glosas de cada degrau VOLTARAM**: elas eram o conteúdo do antigo 2.7 e tinham sido espremidas numa tira de uma linha na fusão de 25/08. O deck ganha um slide e a fala não muda de tamanho. ⚠ **O `exampleblock` do Delaunay ficou AQUI, e não no `S8`**, por duas razões: ele fala dos três métodos que este slide acabou de nomear, e o `S8` estourava a caixa com ele (13,2 pt medidos).
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "Esta é a base mais importante da dissertação, e ela é uma escada. Começa no identificador one-hot, que marca um lugar por posição e não codifica relação nenhuma. Sobe para as representações distribuídas, skip-gram, DeepWalk, node2vec, em que a geometria do vetor reflete a relação que está nos dados. Sobe de novo para as redes de grafo, GCN, GAT, GraphSAGE, que aprendem essa relação por agregação de vizinhança. E o último degrau é o infomax contrastivo: o modelo aprende vetores úteis sendo obrigado a distinguir um pareamento verdadeiro de um pareamento corrompido, e não precisa de rótulo nenhum para isso. É a ideia que sustenta os três métodos desta dissertação, e cada um tem o capítulo dele."
- **Proveniência:** a escada, na ordem do capítulo, com as glosas → `chapters/2_fundamentals.tex:369-379` (one-hot, skip-gram, DeepWalk, node2vec, GCN, GAT, GraphSAGE) e `:420-426`. Delaunay → `2_fundamentals.tex:442`, `3_cbic/method.tex:23`, `4_courb/methodology.tex:163`, `apx_h_check2hgi_joint_model.tex:80` (Apêndice E do **volume principal**). Termo registrado no `GLOSSARY` §3 em 2026-08-25.
- **Nunca dizer:** o mecanismo do DGI ou do HGI aqui — eles pertencem a 3.2A e 4.1A. **Nunca afirmar que os três grafos de Delaunay são o mesmo objeto**: a construção é comum, os pesos não (decaimento geodésico no Cap. 3; Haversine com penalidade de GEOID no Cap. 4). Nunca **`bilinear`**: o discriminador do DGI no Cap. 3 entregue é **linear** (`3_cbic/method.tex:50`), e esta escada começa no DGI. Nenhum resultado, nenhum número. Nunca Space2Vec nem POI2Vec como componentes deste trabalho.

### S10 · The evidence base: six datasets
- **Slide impresso:** **10**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.3   **Tempo:** 55 s
- **LEDGER:** INTRODUZ a base de evidência (**Tab. 8**): Gowalla e Istanbul · INTRODUZ as sete categorias · INTRODUZ a região como unidade nomeada (census tract, *mahalle*)
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - llrrrl@ Dataset & Source & Check-ins & Regions & Majority (\%) & Used by Istanbul & Massive-STEPS & 462,615 & 520 & 33.4 & Ch. 5 AL & Gowalla & 113,846 & 1,109 & 34.2 & Ch. 5 AZ & Gowalla & 236,450 & 1,547 & 34.0 & Ch. 5 FL & Gowalla & 1,407,034 & 4,703 & 24.7 & Ch. 5 TX & Gowalla & 4,089,892 & 6,553 & 31.0 & Ch. 4, Ch. 5 CA & Gowalla & 3,171,380 & 8,501 & 32.7 & Ch. 4, Ch. 5 **The seven categories**, identical in all three studies: Community, Entertainment, Food, Nightlife, Outdoors, Shopping, Travel. **Region** — a census tract in the five U.S. datasets, a *mahalle* in Istanbul; both partition a city at neighborhood scale. *Majority* — share of next-visit labels in the most common category, which is **Food** in every dataset. *(⚠ a linha "Florida appears twice, as two extractions" foi REMOVIDA da tela em 2026-08-26, item `F15` — a diferença entre ETLs sai da apresentação principal e vive na reserva `B4-4`)*;
- **Fala (PT):** "Esta é a base de evidência inteira, dita uma vez só. Cinco estados do Gowalla e Istambul, do Massive-STEPS, e a ordem da tabela é a do documento, por número de regiões. As sete categorias são as mesmas nos três estudos: Community, Entertainment, Food, Nightlife, Outdoors, Shopping e Travel. Região é o setor censitário nos cinco conjuntos americanos e o *mahalle* em Istambul. Os dois particionam a cidade em escala de bairro, e não são o mesmo tipo de objeto: um é unidade de medida, o outro é unidade de governo. A última coluna diz qual capítulo usou qual conjunto."
- **Proveniência:** todas as células copiadas de `tables/mobiwac/datasets.tex` (Tab. 8), linha a linha, sem aritmética. Florida dos Caps. 3/4 → `chapters/3_cbic/results.tex:15` ("20,301 users, 65,009 unique Points-of-Interest, and 990,518 check-ins") e `tables/courb/dataset.tex` (Tab. 5, mesma célula 990,518). Quem usou o quê → `chapters/3_cbic/results.tex:15` (Florida), `tables/courb/dataset.tex` (Florida, Califórnia, Texas), `chapters/1_introduction.tex:290-292` (os seis do Cap. 5). Census tract × *mahalle* → `chapters/2_fundamentals.tex:1442-1451`. As sete categorias → `chapters/2_fundamentals.tex:273-276`. Definição da coluna *Majority* → legenda de `tables/mobiwac/datasets.tex`.
- **Nunca dizer:** "superconjunto" para a Flórida. Não há evidência de contenção entre as duas extrações. Nenhum resultado de nenhum capítulo.

### S11 · The metric all three studies share
- **Slide impresso:** **11**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.4   **Tempo:** 59 s  *(medido)*
- **LEDGER:** INTRODUZ macro-F1 · INTRODUZ o piso de classe majoritária
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **macro-F1** — the mean of the per-category F1 scores; every category counts equally, so rare ones matter. Out of 100; **why** — the class distribution is imbalanced (**Food is roughly one third** of the check-ins in a representative state), so plain accuracy hides poor performance on rare classes; **what it does not do** — it does not show *which* classes improve, and it can be low while overall accuracy is high; **the loss is not reweighted** — unweighted cross-entropy; reference point — the **majority-class floor**, a predictor that always answers the most common category;
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "A métrica de categoria dos três estudos é a macro-F1: a média das F1 por categoria, com cada categoria pesando igual. A razão é a distribuição. Food é cerca de um terço dos check-ins num estado representativo, e uma acurácia simples esconderia o desempenho nas classes menores. Ela também tem um custo, e eu digo qual: a macro-F1 não mostra que classe melhorou, e pode ficar baixa mesmo com acurácia alta. E toda métrica que eu disser vem com ponto de referência. São dois, e nenhum é concorrente: o piso de classe majoritária, que sempre responde a categoria mais comum; e o piso de Markov, uma tabela de transição sobre as visitas de treino, que responde com o que mais costuma vir depois do quê --- primeira ordem para região, melhor ordem de cada conjunto para categoria."
- **Proveniência:** definição, equação e a leitura de fronteira → `chapters/2_fundamentals.tex:1626-1641` (Eq. 2.x de macro-F1; "Food accounts for roughly one third"; "The models use unweighted cross-entropy rather than a reweighted loss"). Piso de classe majoritária → `:1686-1690` ("a majority-class predictor for category classification").
- **Nunca dizer:** chamar de "macro-F1" os valores impressos dos Caps. 3 e 4 (são uma F1 por categoria). Nunca ler a coluna *Majority* da Tab. 8 como se fosse a macro-F1 do preditor de classe majoritária: uma é a fração de rótulos na classe mais comum, a outra é o resultado de um preditor. Nenhum valor de piso aqui; os pisos entram com os resultados que eles ancoram.

### S12 · The protocol of the first two studies
- **Slide impresso:** **12**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.5   **Tempo:** 50 s
- **LEDGER:** INTRODUZ o protocolo dos dois primeiros estudos · INTRODUZ a lei dos verbos · INTRODUZ a armadilha do par de tarefas e a armadilha da convenção métrica · RETOMA a armadilha de nomenclatura de 1.5
- **Na tela:** *(v2 · 134 → ~80 palavras. O bloco das duas armadilhas é carimbo de convenção — a R7 depende dele.)*
  - **Ch. 3 and 4:** five-fold CV stratified **over samples** — **one user's check-ins may fall on both sides**;
  - Full epoch budget, no early stopping; each task at **its own best epoch**;
  - Fold means and standard deviations, **no significance tests**;
  - **The verb law:** *outperforms* is reserved for a paired superiority test — Ch. 3 and 4 report none, so they report differences, never a verdict.
  - Bloco **Two traps**: **The task pair changes.** Ch. 3/4: category classification + next category. Ch. 5: next category + next region. **The metric convention changes.** Ch. 3/4 print one F1 per category; Ch. 5 reports macro-F1. **Not one scale.**
- **v2 · o que saiu da tela, e onde ficou:** a linha final centrada *"Each study names its own convention when its turn comes"* → fala do próprio S12 (verificado); era meta-comentário sobre a estrutura do deck, não conteúdo. ⚠ **O bloco `Two traps` NÃO foi encurtado além do estritamente óbvio**: ele é o carimbo de convenção de que a **R7** (proibição entre gerações) depende, e a admissão *"not one scale"* é o que impede a banca de comparar um número do Cap. 3 com um do Cap. 5. Cortá-lo seria regressão, não enxugamento.
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "O protocolo dos dois primeiros estudos, e ele é diferente do terceiro. Validação cruzada de cinco partições, estratificada por amostra: os check-ins de um mesmo usuário podem cair dos dois lados da divisão. Orçamento cheio de épocas, sem parada antecipada, e cada tarefa lida na época de melhor validação dela. Médias e desvios entre as cinco partições, sem teste de significância. Daí sai a lei dos verbos que eu obedeço a fala inteira: *supera* fica reservado para teste pareado de superioridade, e os Capítulos 3 e 4 não têm teste, então eles reportam diferenças, não veredito. E uma convenção que eu digo agora e não repito: os Capítulos 3 e 4 imprimem uma F1 por categoria, e o Capítulo 5 reporta macro-F1, um número só. Não são a mesma escala, e eu volto a lembrar disso quando as tabelas aparecerem."
- **Proveniência:** protocolo dos Caps. 3/4 → `chapters/3_cbic/results.tex:36` ("The folds are formed by a stratified splitter over the samples rather than over the users"; "training runs for the full number of epochs configured, without early stopping, and each task is read at the epoch of its own highest validation macro-F1") e prefácio do Cap. 4, `chapters/4_courb.tex` ("This study and Chapter 3 share one evaluation protocol, which stratifies the cross-validation split by sample rather than by user"); consolidado em `chapters/2_fundamentals.tex:1731-1734`. Lei dos verbos → `chapters/2_fundamentals.tex:1773-1786` ("Chapters 3 and 4 report fold means and standard deviations without significance tests"; "*outperforms* is reserved for paired superiority"). Par de tarefas → `chapters/2_fundamentals.tex:269-273` e `chapters/1_introduction.tex:224-226`. Convenção métrica → as legendas entregues `tables/cbic/next.tex` ("per-category F1-score, precision, and recall") e `tables/courb/next.tex` ("Average F1-Score (%) per model and state"), contra `chapters/2_fundamentals.tex:1626-1636` (macro-F1 do Cap. 5).
- **Nunca dizer:** "as mesmas janelas". O Cap. 5 usa janelas deslizantes sobrepostas, com passo 1, e os Caps. 3 e 4 usaram janelas não sobrepostas. Nenhum resultado, nenhum número de capítulo. Nada do protocolo estatístico do Cap. 5 aqui: sementes, *t* pareado, TOST e Holm entram em 5.4.

# sec3-4

# SEÇÃO 3 · Multitask Learning for POI Category and Next-POI Prediction (5,5 min)

> `\section[MTLnet]{Multitask Learning for POI Category and Next-POI Prediction}`
> Proveniência no divisor: **CBIC 2025, DOI 10.21528/CBIC2025-1191324. This dissertation's author is its first author.**
> Orçamento: 330 s (30 + 45 + 45 + 30 + 40 + 40 + 55 + 25 + 20).

> ### O divisor desta seção carrega a transição da Seção 2 — **falado, não em tela**
> *(2026-08-25: o `\specialframe` "With the vocabulary fixed…" foi cortado. A regra 12 do PLANO §8
> protege a **frase**, não o frame, e prevê literalmente a forma "falada sobre ele". O `\autotocframe`
> já põe um divisor no início de toda `\section`, então a frase cai aqui, antes da proveniência.)*
>
> **Onde ela vive no roteiro impresso:** no **fim da fala do S12** (o slide de protocolo, que agora fecha a Seção 2) — o gerador do `SPEECH` só lê blocos `### S<n>`, e uma frase solta em cabeçalho de seção **não chega ao roteiro**. Verificado 2026-08-25.
>
> **Fala (PT), sobre o divisor, nesta ordem:** "Com o vocabulário, os dados e a métrica fixados uma
> única vez, cada estudo agora só precisa dizer o que mudou. O primeiro usou o que a literatura
> oferecia: um vetor por lugar e um tronco compartilhado." — e só então a proveniência do capítulo.
> **Tempo:** ~10 s de transição + a proveniência.
>
> ⚠ **Duas cláusulas do frame cortado NÃO voltam, e é de propósito.** (a) *"Each study now says only
> what it changed, and names its own convention when its turn comes"* — esta é **a mesma frase que a
> revisão v2 já expulsou da tela do S12**, com o veredito registrado *"era meta-comentário sobre a
> estrutura do deck, não conteúdo"*; readmiti-la aqui repetiria o defeito. (b) *"The task pair of the
> first two studies is not the pair of the third"* — **duplica a armadilha 1 do bloco `Two traps`**,
> que agora fecha a Seção 2 e é dita segundos antes.

### S19 · DGI
- **Slide impresso:** **13**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.2A   **Tempo:** 45 s
- **LEDGER:** INTRODUZ o mecanismo do DGI · RETOMA a ideia infomax de 2.1 e o degrau do DGI em 2.7
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - Bloco **How it works**:
    - **Delaunay graph** over the area's places; edge weights decrease with **geodesic distance**, logarithmically; graph attention one **64-dimensional** vector per place; infomax objective — real graph against shuffled node features;
  - Bloco **Node features, as released**:
    - The mean of the one-hot vectors of a place's graph neighbors, **with the place's own vector excluded**;
  - **Why that matters** — the input describes a **neighborhood**: spatial homophily, not recall of the place's own label; **What it gives** — one vector per place; every visit enters with the same vector;
- **Fala (PT):** "O primeiro mecanismo, e o desenho conta a história: parte-se do grafo real, faz-se uma cópia corrompida embaralhando as features entre os nós, as duas passam pela MESMA rede, e um discriminador julga se cada nó combina com o resumo global do grafo verdadeiro. É disso que sai o vetor, sem rótulo nenhum. Duas coisas que o desenho não diz e que importam. A primeira: a feature de entrada de um lugar é a média dos vizinhos dele com o próprio vetor excluído -- ou seja, a entrada descreve uma vizinhança, e não a lembrança do próprio rótulo. A segunda: o que sai é um vetor por lugar, e toda visita àquele lugar entra no modelo com o mesmo vetor. Guardem essa segunda, porque é ela que o Capítulo 5 desfaz."
- **Proveniência:** `chapters/3_cbic/method.tex` §3.3.1 (grafo de Delaunay, peso de aresta $w_{ij}$ com $d_{ij}$ geodésica, camada de atenção de grafo, objetivo do DGI com embaralhamento das features e resumo global, embedding de 64 dimensões) e a **nota de rodapé** da mesma seção, literal: *"the released implementation feeds the network the mean of the one-hot vectors of a POI's graph neighbors, with the POI's own vector excluded"*.
- **Nunca dizer:** "one-hot da própria categoria" como atributo de nó. Nunca "coocorrência": este canal não existe no Cap. 3. **Nunca "o DGI não vaza"** (a formulação correta está no slide B4-LEAK).

### S18 · MTLnet
- **Slide impresso:** **14**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.2   **Tempo:** 45 s
- **LEDGER:** INTRODUZ MTLnet · INTRODUZ FiLM
- **Na tela:** **Fig. 1, redesenhada em TikZ** (o raster entregue imprime tipo de ~7 pt contra corpo de 12; ver o inventário de assets). Cadeia da esquerda para a direita:
  - `Category input` and `Next-POI input` → **per-task encoders** (MLPs) →
  - **FiLM** (Feature-wise Linear Modulation): a learnable task embedding produces a scale and a shift for the encoded features, so both tasks read the same parameters under different scalings →
  - **shared residual blocks** (LayerNorm, LeakyReLU, dropout): this is **hard parameter sharing**, Def. 2.10 →
  - **two outputs, one per task** (`CategoryHead`, `NextHead` in the figure).
  - Rodapé, from the chapter: the parameters are declared in two disjoint sets, **shared** (task embeddings, FiLM, shared layers) and **task-specific** (the two encoders and the two outputs).
  - `[CARIMBO-TAREFA]`
- **Fala (PT):** "Esta é a arquitetura, o MTLnet. Vale guardar a figura, porque o Capítulo 4 não vai alterar uma linha dela. Cada tarefa entra por um encoder próprio, um MLP. Vem então a modulação FiLM, e ela cabe numa cláusula: um vetor de identidade de tarefa gera uma escala e um deslocamento, aplicados às features antes da parte compartilhada, de modo que as duas tarefas leiam os mesmos parâmetros sob escalas diferentes. Depois vem o tronco de blocos residuais, que é o compartilhamento rígido da Definição 2.10. E no fim duas saídas, uma por tarefa. O segundo item é o detalhe que vai importar no próximo slide: o capítulo declara os parâmetros em dois conjuntos disjuntos, os compartilhados e os específicos de tarefa. É sobre o primeiro conjunto que um balanceador de gradientes age."
- **Proveniência:** `chapters/3_cbic/method.tex` §3.3.2 (encoders por tarefa, equação do FiLM, blocos residuais compartilhados, saídas específicas de tarefa) e §3.3.3, parágrafo *Parameter Partition* (os dois conjuntos disjuntos $\Theta_{shared}$ / $\Theta_{specific}$); legenda da Fig. 1, `figures/cbic_mtlnet_arch.png`, redesenhada sem as elipses `Task ID` e o losango `Task Embedding`.
- **Nunca dizer:** nenhum número do Cap. 3 ao lado de um do Cap. 5. Nunca "backbone": o nome é **tronco compartilhado**.

### S21 · Two losses, one set of parameters
- **Slide impresso:** **15**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.3A   **Tempo:** 70 s  *(medido)*
- **LEDGER:** INTRODUZ o problema multiobjetivo, a dominância e a fronteira de Pareto, e as duas classes de método de balanceamento
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - The problem, before any method is named: **two losses, one set of shared parameters, no total order between solutions**; the usual objective is a **weighted sum** — the scalar sum does not remove the multi-objective nature of the problem; **Pareto dominance** — no worse on every task loss, better on at least one; **Pareto optimal** — nothing dominates it; hence two classes of method: **set the weights** — uncertainty weighting, GradNorm, DWA, FAMO; **change the update direction** — MGDA, PCGrad, CAGrad, Nash-MTL, Aligned-MTL;
  - Bloco **(sem título)**:
    - **This dissertation claims no Pareto property for its models.**;
- **Fala (PT):** "Antes de eu nomear o otimizador, o problema que ele existe para resolver. São duas perdas e um único conjunto de parâmetros compartilhados, e entre duas soluções não há ordem total: uma pode ser melhor numa tarefa e pior na outra, e as duas ficam incomparáveis. Escrever a soma ponderada das perdas não remove essa natureza multiobjetivo. Daí vem o vocabulário: uma configuração domina outra no sentido de Pareto quando não é pior em nenhuma perda e é melhor em pelo menos uma; ela é Pareto-ótima quando nenhuma outra a domina; e o conjunto dos vetores de perda dessas configurações é a fronteira de Pareto. A área respondeu a isso com uma família inteira de métodos, e a família se divide em duas classes: os que fixam os pesos das perdas e os que mudam a direção da atualização. Uma ressalva que é do Capítulo 2 e que eu repito de propósito: esta dissertação não reivindica nenhuma propriedade de Pareto para os modelos dela."
- **Proveniência:** `chapters/2_fundamentals.tex` §2.3.3 (Eq. da soma ponderada; *"the scalar sum does not remove the multi-objective nature of the problem"*; dominância, otimalidade e fronteira de Pareto), §2.3.3.1 (*"This dissertation therefore claims no Pareto property for its models"*) e §2.3.4 (as duas classes e os métodos nomeados). Nenhum número nesta tela.
- **Nunca dizer:** nenhuma afirmação de Pareto sobre os nossos modelos. Nenhum formalismo do zoo de balanceadores na tela (§8 regra 16): os nomes entram como lista, sem equação.

### S22 · Nash-MTL, and what the chapter may claim about it
- **Slide impresso:** **16**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.3B   **Tempo:** 72 s  *(medido)*
- **LEDGER:** INTRODUZ Nash-MTL · RETOMA o critério de 2.2 e as duas classes de S21
- **Na tela:** *(v2 · 137 → ~78 palavras. Zero frases completas nos marcadores.)*
  - Changes the **update direction** — gradient combination as a **cooperative bargaining problem**;
  - Each task's utility is its own loss reduction; the direction **maximizes the product**;
  - Guarantee: a **Pareto-stationary point** — necessary, not sufficient.
  - Bloco **What Chapter 3 claims**: Lower combined multitask loss than PCGrad and than no such optimizer; the chapter adopted it. **A conclusion of the time**, weakened by a later finding — **and Chapter 5 does not rely on it**.
  - Rodapé: *Criterion from Section 2, still standing: useful only if it improves on a tuned fixed weighting.*
- **v2 · o que saiu da tela, e onde ficou:** *"which keeps one task from dominating the other"* e *"which needs a convexity assumption a deep network does not satisfy"* → fala do próprio S22 (verificado). *"Against PCGrad and against training without such an optimizer"* virou *"than PCGrad and than no such optimizer"* — mesma informação, metade das palavras. ⚠ **A ressalva completa (*"a conclusion of the time, weakened by a later finding — and Chapter 5 does not rely on it"*) FICA na tela**: é a distância que o deck põe entre o Cap. 3 e o veredito, e a R6 exige que ela acompanhe a afirmação que limita.
- **Fala (PT):** "O Nash-MTL cai na segunda classe. Ele muda a direção da atualização, tratando a combinação dos gradientes como uma barganha cooperativa entre as tarefas: cada tarefa tem uma utilidade, que é a redução da perda dela, e a direção escolhida é a que maximiza o produto dessas utilidades, o que evita que uma domine a outra. A garantia é convergência para um ponto Pareto-estacionário, que é condição necessária e não suficiente para otimalidade de Pareto; a otimalidade exigiria uma hipótese de convexidade que uma rede profunda não satisfaz. Agora a parte que eu preciso dizer com cuidado. O Capítulo 3 adotou o Nash porque, na comparação dele, contra o PCGrad e contra não usar balanceador nenhum, ele deu a menor perda multitarefa combinada. Isso é conclusão do tempo dele, enfraquecida depois por um achado sobre a implementação do otimizador. O critério da Seção 2 continua de pé: um balanceador só é útil se melhorar sobre uma ponderação fixa bem ajustada."
- **Proveniência:** `chapters/3_cbic/method.tex` §3.3.3 (barganha cooperativa, utilidade por tarefa, produto das utilidades, ponto Pareto-estacionário; e o parágrafo final, *"Nash-MTL was compared with different strategies, including PCGrad and an approach with no optimizer... consistently yielded a better overall performance... with a lower combined multitask loss"*); prefácio do Cap. 3, `chapters/3_cbic.tex` (*"a conclusion of the time, weakened by a later finding about the optimizer implementation"*); `chapters/2_fundamentals.tex` §2.3.3.1 (a hipótese de convexidade) e §2.3.4 (o critério). Nenhum número nesta tela.
- **Nunca dizer:** nenhuma afirmação de Pareto sobre os nossos modelos. Nunca apresentar a adoção do Nash como posição atual da dissertação.

### S23 · The null result
- **Slide impresso:** **17**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.4   **Tempo:** 70 s  *(medido)*
- **LEDGER:** INTRODUZ o resultado nulo do Cap. 3 · RETOMA o mapa de métodos externos de 2.6
- **Na tela:** duas tabelas reduzidas lado a lado, **só o bloco F1** de cada uma (as faixas de Precision e Recall saem; a tabela de 21 linhas nunca vai para um slide, §8 regra 16).
  - **Left, from Tab. 2, static task.** Seven category rows, columns *MTL · Single · HMRM*. One-line lead: **both of our models score above HMRM in every category** (F1 shown; the chapter states the same for precision and recall).
  - **Right, from Tab. 3, next category.** Seven category rows, columns *MTL · Single · MHA+PE*. One-line lead: **the leads split.** MHA+PE holds the best F1 at Community, Food and Shopping; MTL at Nightlife and Travel; Single at Entertainment and Outdoors.
  - Center band, in `alertblock`, the chapter's own sentence: *"largely comparable, without a clear or consistent advantage for the multitask learning setup in these experiments"*.
  - `[CARIMBO-TAREFA]` · `[CARIMBO-MÉTRICA]`
- **Fala (PT):** "O resultado. Eu prefiro mostrá-lo a afirmá-lo, então são as duas tabelas do capítulo, reduzidas ao bloco de F1. À esquerda, a tarefa estática: os nossos dois modelos ficam acima da HMRM em todas as categorias. À direita, a tarefa sequencial, e é aqui que está o ponto: as lideranças se dividem. O MHA+PE fica com a melhor F1 em Community, Food e Shopping; o nosso multitarefa, em Nightlife e Travel; o de tarefa única, em Entertainment e Outdoors. E a comparação que interessa é entre as nossas duas colunas, que é a comparação entre multitarefa e dedicado. A conclusão é a do próprio capítulo, e está na tela: largamente comparáveis, sem vantagem clara ou consistente para o arranjo multitarefa nestes experimentos. Boa parte dessas diferenças cai dentro do desvio padrão entre partições. E uma precisão que evita a comparação errada mais tarde: isto é F1 por categoria, a convenção dos Capítulos 3 e 4, e não é a macro-F1 do Capítulo 5."
- **Proveniência:** `tables/cbic/category.tex` (Tab. 2, bloco F1, sete linhas, colunas MTL / Single / HMRM) e `tables/cbic/next.tex` (Tab. 3, bloco F1, mesmas sete linhas, colunas MTL / Single / MHA+PE), **células copiadas sem alteração**; as lideranças são as marcas de negrito impressas nas mesmas tabelas (legenda da Tab. 3: *"best value per row in bold, second-best underlined"*). Frase entre aspas: `chapters/3_cbic/results.tex` §3.4.2.2. A afirmação sobre a HMRM é a do mesmo arquivo, §3.4.2.1 (*"both our MTL and Single models outperform HMRM in every POI category in terms of F1-score, precision, and recall"*).
- **Nunca dizer:** **"ambas as baselines externas batidas em absoluto"** (vale só na tarefa estática; na sequencial o MHA+PE lidera Community, Food e Shopping). Nunca "supera": não há teste pareado neste capítulo. Nenhum número do Cap. 3 ao lado de um do Cap. 5.

### S24 · The null result: three possible causes
- **Slide impresso:** **18**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.5   **Tempo:** 40 s  *(medido)*
- **LEDGER:** INTRODUZ a bifurcação de três hipóteses
- **Na tela:** três caixas numeradas, sem hierarquia entre elas.
  1. **Task dissimilarity.** A static task and a sequential task may force the shared trunk into a compromise representation, specialized for neither.
  2. **Representation insufficiency.** The shared representation may not be rich enough to encode semantic properties and sequential dynamics at once.
  3. **Topology rigidity.** One shared block may be too restrictive; soft sharing or expert-based routing might fit better.
  - Rodapé: **Negative transfer was hypothesized here. It was never observed.**
- **Fala (PT):** "É aqui que o capítulo deixa de ser um resultado negativo e vira um programa de trabalho, porque ele nomeia três suspeitos, e não um. Dissimilaridade das tarefas: o tronco compartilhado teria sido forçado a uma representação de compromisso, não especializada para nenhuma das duas. Insuficiência da representação: ela não seria rica o bastante para codificar propriedade semântica e dinâmica sequencial ao mesmo tempo. Rigidez da topologia: um único bloco compartilhado seria restritivo demais. Uma precisão sobre o rodapé, que eu faço questão de dizer: a transferência negativa foi hipotetizada aqui, não foi observada."
- **Proveniência:** `chapters/3_cbic/conclusion.tex` (as três hipóteses, na ordem e com o conteúdo dos títulos do próprio capítulo: *Subtle Negative Transfer due to Task Dissimilarity*, *Task Difficulty and Representation Mismatch*, *Architectural Restrictiveness*). Nenhum número nesta tela.
- **Nunca dizer:** transferência negativa como algo observado. Nunca dar a um dos três suspeitos precedência que o capítulo não dá.

### S25 · Three possible causes do not close the investigation
- **Slide impresso:** **19**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 3.x (transição interna, Cap. 3 → Cap. 4)   **Tempo:** 20 s
- **LEDGER:** RETOMA a bifurcação de 3.5
- ⚠ **`\specialframe` sem `\frametitle`** — o extrator do `SPEECH` **não alcança este bloco** e nunca vai alcançar. O cartão é emitido com `sem página`, e o texto **só se confere lendo o corpo do frame**. Foi assim que este bloco ficou desatualizado sem ninguém ver.
- **Na tela:** `\specialframe`, duas linhas *(atualizado 2026-08-26 — o corpo acompanhou o retítulo do impresso 18, de "A null with three suspects" para "The null result: three possible causes")*:
  - *Three possible causes do not close the investigation. They design the next experiment:*
  - **keep the architecture fixed, and move only the input.**
- **Fala (PT):** "Três causas possíveis não encerram a investigação: elas desenham o próximo experimento. Congelar a arquitetura e mover apenas a entrada."
- **Proveniência:** PLANO §2, transição interna do Ato II, redação literal. Nenhum número.
- **Nunca dizer:** que o próximo capítulo responde os três suspeitos. Ele condena **um**.

---

# SEÇÃO 4 · ST-MTLNet: Spatio-Temporal POI Representations (6 min)

> `\section[ST-MTLNet]{ST-MTLNet: Spatio-Temporal POI Representations}`
> Proveniência no divisor: **CoUrb 2026 (SBRC), DOI 10.5753/courb.2026.22960. This dissertation's author contributed the MTLnet baseline used in the study and presented the work at the event.** (redação literal de `chapters/1_introduction.tex` §1.4.)
> Orçamento: 360 s (40 + 55 + 60 + 45 + 60 + 65 + 35).

### S26 · Architecture or representation?
- **Slide impresso:** **20**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.1   **Tempo:** 60 s  *(medido)*
- **LEDGER:** INTRODUZ o desenho controlado do Cap. 4 · RETOMA MTLnet e FiLM de 3.2, e Nash-MTL de 3.3B
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - Bloco **The inherited question — suspect 2 against suspect 3**:
    - Is the bottleneck the **representation**, or the **sharing topology**?;
  - **The design that separates them** — MTLnet unchanged, **only the input moves**: same trunk, same FiLM, same balancer, same hyperparameters; **old input** — one monolithic **64-dimensional** place embedding (DGI); **new input** — three **64-dimensional** encoders, spatial, temporal and categorical, concatenated into **192**; same latent width on both sides: the per-task encoders project any input to **256**; three states: Florida, California, Texas. Protocol as in Chapter 3. **Task stamp.** ``Next-POI Prediction'' is the next **category** (Def. 2.7), not the exact next place;
- **Fala (PT):** "O segundo estudo pega a pergunta herdada e a transforma em experimento controlado. O gargalo é a representação, ou é a topologia de compartilhamento? Para separar as duas, ele mantém o MTLnet sem alterar uma linha: o mesmo tronco, a mesma modulação FiLM, o mesmo balanceador de gradientes, os mesmos hiperparâmetros. Só a entrada se move. A entrada antiga é o embedding monolítico de 64 dimensões do DGI; a nova é a concatenação de três codificadores, de 64 dimensões cada, o que dá 192. Vou por partes."
- **Proveniência:** `chapters/4_courb/methodology.tex` §4.3 (decomposição em três componentes de 64, treinados separadamente e integrados por concatenação), §4.3.1 (*"whose internal architecture is kept unchanged in this chapter"*; $\mathbf{E}_{DGI} \in \mathbb{R}^{64}$; 192 dimensões), §4.3 (Nash-MTL no treino multitarefa; $d_{shared} = 256$) e §4.3.6 (*"All models share the same hyperparameters of the MTLnet architecture, differing only in the input embeddings"*); `chapters/4_courb/results.tex` §4.4.1 (Flórida, Califórnia e Texas; cinco partições, divisão estratificada 80/20); prefácio do Cap. 4 (protocolo compartilhado com o Cap. 3).
- **Nunca dizer:** ampliar crédito de autoria. A linha do divisor é a redação da própria Introdução entregue, e não se acrescenta nada a ela.


### S27 · HGI
- **Slide impresso:** **21**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.1A   **Tempo:** 55 s
- **LEDGER:** INTRODUZ o mecanismo do HGI · RETOMA a ideia infomax de 2.1 e o degrau do HGI em 2.7
- **Na tela:** quatro blocos, todos em fragmento e agora em `\small`. *(v2 · 138 → ~66 palavras.)*
  - **How it works, in order**: Pretrained category encoder → **graph convolution** (Delaunay) → **multi-head attention** over a region's places → **area-weighted sum** → city embedding.
  - **What is maximized**: Mutual information between **two adjacent levels**. **No downstream label enters that comparison.**
  - **A consequence of the design**: **The place-level output already reflects the region the place belongs to.**
  - **Why it is used here — and the limit**: Built for **urban region representation**; its **place-level** output repurposed here for sequential prediction — **a use the original evaluation does not cover**.
- **v2 · o que saiu da tela, e onde ficou:** *"through a bilinear discriminator"* → fala do próprio S27. O mecanismo da consequência — *"place encoder, aggregation and region encoder are updated together, and region membership also enters through the edge weights"* → fala do S27 (verificado); **a consequência em si ficou**, porque é ela que carrega o argumento e é o que a banca precisa ver escrito. ⚠ **A ressalva *"a use the original evaluation does not cover"* FICA na tela** — é admissão contra o próprio argumento, não qualificação técnica.
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "O segundo mecanismo, e ele é o mesmo objetivo subindo uma hierarquia. Um codificador de categoria dá as features iniciais, uma convolução sobre o grafo de Delaunay acrescenta vizinhança, a atenção junta os lugares de uma região, as regiões conversam entre si, e uma soma ponderada pela área fecha na cidade. As comparações contrastivas acontecem em duas fronteiras: lugar contra região, e região contra cidade. E duas consequências, sendo que a segunda está na tela. A primeira é a que explica o resultado do próximo capítulo: o vetor de um lugar já carrega a região a que ele pertence. A segunda é a ressalva: o HGI foi construído para representar regiões urbanas, e eu uso aqui a saída de nível de lugar dele para predição sequencial -- um uso que a avaliação original não cobre."
- **Proveniência:** `chapters/2_fundamentals.tex` §2.2.2 (a cadeia completa: codificador de categoria pré-treinado, convolução sobre o grafo de Delaunay, atenção multi-cabeça por região, soma ponderada por área; o discriminador bilinear e a função logística; *"No label of any downstream task enters that comparison"*; *"It already reflects the region the place belongs to"*; e o parágrafo do reaproveitamento, *"a use the original evaluation does not cover"*); `chapters/4_courb/methodology.tex` §4.3.5.2 (os dois níveis da perda e $\mathbf{E}_{HGI} \in \mathbb{R}^{64}$).
- 🔴 **RESPOSTA ORAL ATIVA — o negativo da fronteira lugar–região.** *(Decisão do autor, 26/08, tomada com os dois renders lado a lado: a `tikz` construiu a variante fiel ao código e ele manteve a dele. Não reabrir.)*
  **A chapa mostra a seta do negativo saindo do ramo corrompido. O método não faz isso.** No HGI, o negativo daquela fronteira é **outro lugar da tabela ORIGINAL pareado com a mesma região** — `(pⱼ, rₖ)`, sem til. O ramo corrompido serve à fronteira de cima, **região–cidade**, via `r̃ₖ`.
  **Se perguntarem, a resposta é uma frase e ela é forte:** *"o diagrama unifica os dois negativos numa origem só, por clareza; na fronteira lugar–região o negativo é um lugar de outra região vindo da mesma tabela original, e a corrupção de features entra na fronteira região–cidade."*
  **Fonte, se pedirem:** `HGIModule.py:276` (`neg_loss = -log(1 - σ(POI_j @ W @ region[R]))`) e `:281-283` (`neg_pois = pos_poi_emb[neg_poi_idx]` — mesmo tensor das positivas, índice diferente); `2_fundamentals.tex:449-453`. O desenho escrito do autor rotula a coluna `POI Embedd Pos & Negativo ↔ REGION` (`hgi_draw.txt:48`), que é a leitura fiel.
  ⚠ **NÃO dizer isto espontaneamente.** O slide está em 0,941 de tinta e a fala em 56 s, num deck a 43 s do teto. É resposta, não conteúdo.
- **Nunca dizer:** introduzir o Check2HGI aqui, que é do Cap. 5. Nunca Space2Vec nem POI2Vec como componentes deste trabalho.

### S28 · Why these encoders
- **Slide impresso:** **22**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.1B   **Tempo:** 90 s  *(medido)*
- **LEDGER:** INTRODUZ SIREN, Sphere2Vec-M, Time2Vec e o canal categórico em duas fases
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - Bloco **Spatial, 64 d**:
    - **Why:** space entered only through graph topology, never as a coordinate. **SIREN** — sinusoidal activations over normalized coordinates; **Sphere2Vec-M** — multi-scale, spherical, geodesic distance preserved; one contrastive loss for both: positive under **10 km**, negative over **70 km**;
  - Bloco **Temporal, 64 d**:
    - **Why:** no explicit temporal representation. **Time2Vec** — a linear term for trend, sinusoidal terms for hour of day and day of week;
  - Bloco **Categorical, 64 d, two phases**:
    - **Why:** graph structure alone — no hierarchy, no region. **1. POI Encoder** — skip-gram with negative sampling, each **fine-grained source label** tied to its top-level category *(⚠ era `fine class`, termo restrito pelo `GLOSSARY` ao Apêndice B §B.5 — trocado em 2026-08-26 pela DESCRIÇÃO do registro, que não é o termo)*. **2. HGI** — the regional hierarchy above;
- **v2 · o que saiu da tela, e onde ficou:** nada de conteúdo. O slide **estourava a caixa do frame** (borda inferior cortada, com `0 erros` no log): na v1 o bloco **Spatial** vazava por baixo; ao reequilibrar as colunas o vazamento migrou para o **Categorical**. Correção 2026-08-25: colunas `0.426/0.504` → **`0.478/0.452`**, os três blocos em **`\footnotesize`** (≈19 pt projetados, acima do piso de 16 pt da regra 10), e dois cortes lexicais sem perda de conteúdo — *"never as a continuous coordinate"* → *"never as a coordinate"*, e o ponto-e-vírgula do `POI Encoder` virou vírgula. **Toda a fala continua valendo, inclusive a palavra "contínua"**, que é onde `continuous` foi parar. Verificado por render da página 33, não só por canária: canária responde *foi desenhado?*, não *o bloco fecha?*
- **Fala (PT):** "Por que estes codificadores, e não outros quaisquer. O canal espacial existe porque o MTLnet codificava espaço só implicitamente, pela topologia do grafo, e nunca como coordenada contínua. O estudo compara dois com hipóteses diferentes: o SIREN, que modela uma função contínua das coordenadas normalizadas com ativações senoidais, e o Sphere2Vec-M, que é multiescala e opera direto em coordenadas esféricas, preservando propriedades de distância geodésica. Os dois são treinados com a mesma perda contrastiva sobre distância geográfica, com par abaixo de dez quilômetros como positivo e acima de setenta como negativo, e é isso que faz a comparação isolar a arquitetura. O canal temporal existe porque o MTLnet não tinha representação temporal nenhuma, e o Time2Vec combina um termo linear, de tendência global, com termos senoidais, para os padrões cíclicos de hora do dia e dia da semana. O canal categórico existe porque o DGI codificava categoria pela estrutura do grafo, sem capturar relação hierárquica ou regional entre elas, e ele vem em duas fases. Primeiro um codificador de lugar, que aprende coocorrência entre categorias a partir de caminhadas aleatórias sobre o grafo espacial, com amostragem negativa e um termo que amarra cada classe fina à categoria de topo dela. Depois o HGI, que acrescenta a hierarquia regional sobre esse resultado."
- **Proveniência:** `chapters/4_courb/methodology.tex` §4.3.3 (perda contrastiva comum aos dois codificadores espaciais, com os limiares de 10 km e 70 km; SIREN; Sphere2Vec-M multiescala em coordenadas esféricas), §4.3.4 (Time2Vec: termo linear e termos senoidais, hora do dia e dia da semana), §4.3.5 e §4.3.5.1 (as duas fases; caminhadas aleatórias; skip-gram com amostragem negativa; o termo hierárquico entre categoria e classe fina) e §4.3.5.2 (HGI sobre a saída do POI Encoder, com $\mathbf{E}_{HGI} \in \mathbb{R}^{64}$). `POI Encoder` é o nome do próprio capítulo entregue: na tela ele aparece nessa grafia, com a glosa *"a category encoder trained on random walks"*.
- **Nunca dizer:** Space2Vec ou POI2Vec como componentes deste trabalho. Eles são arte prévia, e não estão no registro de termos.

### S26b · Architecture or representation? (a arte)
- **Slide impresso:** **23**  ·  *(v3 · `AUT-23`: a arte passa a FECHAR a Seção 4, depois do HGI e dos codificadores)*
- **Seção/subseção:** 4.1   **Tempo:** 18 s *(medido)*  ·  ⚠ **deixou de ser 0 s**
- **Fala (PT):** *(v3, 26/08 — fala PRÓPRIA, criada pela `AUT-23`. Antes este frame não tinha nenhuma: era falado dentro dos 40 s do S26, que agora fica dois slides atrás.)* "E aqui está tudo junto, dentro do modelo que não mudou. Os encoders de tarefa projetam qualquer entrada para a mesma largura latente de 256 nos dois braços, e é esse congelamento que faz o resultado ser diagnóstico, e não apenas melhor."
- **Proveniência:** a cauda da fala de 40 s do `S26`, que descrevia esta figura e viaja com ela. Largura latente de 256 e o argumento do congelamento → `chapters/4_courb/methodology.tex` §4.3.6.
- ⚠ **Custo medido do racha:** a fala única tinha **124 palavras (53 s)**; as duas somam **129 (55 s)**. **+2,1 s**, e a compressão do `S26` paga quase todo o custo da ponte. *(A nota antiga dizia "fala de 40 s" — ela já estava 13 s acima do declarado antes de qualquer mudança.)*
- **LEDGER:** RETOMA a Fig. 2 do Cap. 4 (arte reproduzida). INTRODUZ nada.
- **Na tela:** *(bloco criado 2026-08-26 na migração — este frame existe no `slides/main.tex` desde a
  construção do deck e nunca teve bloco aqui. Campo derivado do frame vigente.)*
  - `\framesubtitle`: The same MTLnet, with the decomposed input in place of the monolithic one
  - `\includegraphics[width=\textwidth]{arquitetura_modelo}`
  - Rodapé: **Task stamp.** ``Next-POI Prediction'' is the next **category** (Def. 2.7), not the exact next place. **Metric stamp.** Chapters 3 and 4 print one F1 **per category**; Chapter 5 reports **macro-F1**. Not one scale.
- **Fala (PT):** *(sem fala própria — é a arte da Fig. 2, falada dentro dos 40 s do S26.)*
- **Proveniência:** figura `arquitetura_modelo`, Fig. 2 do Cap. 4 (`src/figures/courb/`). O comentário do frame no `main.tex` registra a ausência de fala.
- **Nunca dizer:** nada de novo aqui. O `Task stamp` é mandato da regra §8.5 (arte reproduzida dos Caps. 3/4).

### S30 · The diagnostic result is the sequential task
- **Slide impresso:** **24**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.3   **Tempo:** 100 s  *(medido)*
- **LEDGER:** INTRODUZ o resultado sequencial do Cap. 4
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - lccc@ & **MTLnet** & **ST-MTLNet** & **ST-MTLNet** & & **SIREN** & **Sphere2Vec-M** Community & 34.33 1.33 & **38.31 0.90** & 37.98 1.22 Entertainment & 25.34 1.07 & **31.38 1.72** & 31.24 2.41 Food & 27.12 2.79 & **41.91 1.93** & 41.65 3.15 Nightlife & 21.33 1.61 & 23.32 2.74 & **23.98 1.94** Outdoors & **21.61 0.99** & 21.29 1.59 & 21.59 1.91 Shopping & 39.62 3.40 & 44.00 2.04 & **44.66 2.38** Travel & **64.47 1.02** & 45.00 1.10 & 44.93 1.11 decomposed input holds the higher mean in **15 of 21** combinations; **MTLnet retains six** — one a *``technical tie''* at Outdoors in Florida, MTLnet higher by **0.02 pp**, inside one standard deviation; gains concentrate at **Food**, in all three states. **Task stamp.** the next **category** (Def. 2.7), not the exact next place. **Metric stamp.** one F1 **per category** here; **macro-F1** in Chapter 5. Not one scale;
- **Fala (PT):** *(v3, 26/08 — a ressalva de vazamento estava no deck e NÃO estava aqui: numa regeração do `SPEECH` ela sumiria da minha boca. Reposta.)* "Antes dos números, a ressalva, porque ela decide como ler a tabela da esquerda: depois da publicação nós estabelecemos que a entrada da tarefa estática contém o rótulo que ela prediz. A feature de tipo de local mapeia um-para-um nas sete categorias. Então os números da esquerda medem uma consulta, não inferência semântica aprendida. O resultado diagnóstico é o da direita, a tarefa sequencial, cujo alvo nunca está na entrada. Na tela está a Flórida, com os três modelos lado a lado; Califórnia e Texas eu tenho prontos se a banca quiser. O cenário aqui é mais heterogêneo do que na tarefa estática, e continua favorável à entrada decomposta. Contando o melhor dos dois codificadores espaciais por combinação, os modelos espaço-temporais ficam com a média mais alta em quinze das vinte e uma combinações de categoria e estado, e o MTLnet, com a entrada original, retém seis. Uma dessas seis o capítulo chama, nas palavras dele, de um empate técnico adicional: é Outdoors na Flórida, onde a média do MTLnet fica dois centésimos de ponto percentual acima da melhor variante, dentro de um desvio padrão. Os maiores ganhos estão em Food, em que as duas variantes ficam acima nos três estados. E de novo a precisão: isto é F1 por categoria, não é macro-F1."
- **Proveniência:** `tables/courb/next.tex` (Tab. 7, bloco da Flórida, sete linhas, três colunas, células copiadas sem alteração); contagens, o *"technical tie"* e os 0.02 pontos percentuais de `chapters/4_courb/results.tex` §4.4.3 (*"outperform the original MTLnet in 15 of the 21 evaluated combinations, with one additional technical tie in Outdoors in Florida, where the baseline mean exceeds the best variant by 0.02 percentage points, a gap within one standard deviation"*; *"the baseline retains six of them"*) e `chapters/4_courb/conclusion.tex`.
- **Nunca dizer:** "macro-F1". Nunca "supera": este capítulo não tem teste pareado. Nenhum número do Cap. 5 nesta tela. Nunca citar o empate sem a direção (a média da baseline é a mais alta, por 0,02). ⚠ **E não confundir o `technical tie` desta tela com o `ties` proibido do eixo do veredito** (`GLOSSARY` §4, linha *TOST non-inferiority*: *verdict verb "matches" is banned*). Aqui é a **redação literal do Cap. 4 entregue** (`src/chapters/4_courb/results.tex:62` e `conclusion.tex:14`), sobre a tarefa sequencial do Cap. 4 — **outro eixo, outro protocolo, outro capítulo**. O que continua banido é `tie`/`empata`/`matches` como veredito sobre o resultado do **Cap. 5**. Decisão do autor, 2026-08-24: **fica verbatim**, pelo mesmo motivo do `match` no S44 — parafrasear o capítulo na tela é pior do que citá-lo.
- **Se perguntarem** — *"o senhor bane 'empate' e o slide diz 'technical tie'"*:
  > "É a redação do Capítulo 4, citada literalmente, e é sobre a tarefa sequencial daquele capítulo, que roda sob outro protocolo. O que o registro bane é `empata` como veredito sobre o resultado do Capítulo 5 — e ali eu digo `supera` em três células, `não-inferior` em seis, e `não resolvido` no resto. Nunca `empata`."

### S31 · Three limits of the decomposition
- **Slide impresso:** **25**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.4   **Tempo:** 84 s  *(medido)*
- **LEDGER:** INTRODUZ os três limites declarados do Cap. 4
- **Na tela:** *(v2 · 132 → ~70 palavras.)*
  - Bloco **Travel, labeled by task**: *Travel (category classification)* **moved** · *Travel (next category)* **did not**. On the sequential task MTLnet keeps the lead at **Florida** and **California**.
  - Bloco **No universally better spatial encoder**: **SIREN** at Florida and California, **Sphere2Vec-M** at Texas.
  - Bloco **Not width-matched**: **192 dimensions against 64** — the chapter states this as a limit.
  - Rodapé: *The three components are used together — this chapter does not isolate each encoder.*
- **v2 · o que saiu da tela, e onde ficou:** a explicação do porquê — *"long-distance movement is sparse, and graph topology preserves relationships between geographically distant places better than a coordinate-based encoder does"* → fala do próprio S31. *"Suitability depends on how the places are distributed over each territory"* → fala do S31. *"and asks for an equal-dimension control"* → fala do S31 **e tela do SB22** (`B4-1`, que é a pergunta de banca sobre os 192 contra 64; verificado). ⚠ **A ressalva de largura e a de não-isolamento FICAM na tela** — as duas são admissões contra o próprio argumento.
- **Fala (PT):** "Três limites, e eu ofereço os três antes que me peçam. O primeiro é o Travel, e ele precisa de rótulo de tarefa, senão a sala se confunde: Travel na classificação de categoria melhora, Travel na próxima categoria não. Na tarefa sequencial o MTLnet mantém a liderança na Flórida, e a razão está escrita no capítulo: movimento de longa distância é esparso, e a topologia de grafo preserva relação entre lugares geograficamente distantes melhor do que um codificador baseado em coordenada. O segundo limite é que não existe codificador espacial universalmente melhor. O SIREN se destaca mais na Flórida e na Califórnia, o Sphere2Vec-M no Texas, e a adequação depende de como os lugares se distribuem em cada território. O terceiro é o que eu esperaria que a banca perguntasse, então eu digo primeiro: a comparação não é pareada em largura. São 192 dimensões contra 64. O capítulo declara isso como limite e pede um controle de dimensão equalizada, e esse controle nunca foi executado. Eu não vou defender o ponto: parte do ganho pode vir da largura. Junto com isso, os três componentes entram sempre juntos, então este capítulo não isola a contribuição de cada codificador."
- **Proveniência:** `chapters/4_courb/results.tex` §4.4.3 (Travel na tarefa sequencial em Flórida e Califórnia; a razão da esparsidade e da topologia de grafo; SIREN × Sphere2Vec-M por estado) e `chapters/4_courb/conclusion.tex` (*"there is no single universally superior spatial encoder"*; *"this chapter does not isolate the individual contribution of each encoder"*); `chapters/4_courb/methodology.tex` §4.3.6 (192 contra 64, e *"an additional experimental control equalizing the dimensionality of the representations"*).
- **Nunca dizer:** "pareado em largura". Deixar o ganho estático falar pela sequencial. Ampliar crédito de autoria.

### S32 · Freeze the architecture, move only the input
- **Slide impresso:** **26**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 4.5 (transição de saída do Ato II)   **Tempo:** 35 s
- **LEDGER:** RETOMA o gargalo · INTRODUZ as três camadas que o Cap. 5 reconstrói (representação · topologia · protocolo)
- **Na tela:** *(v3 · decisão do autor 27/08 — Opção A **sem a terceira frase**: o slide 27 diz exatamente aquilo. ⚠ Tirando-a, o salto "dois limites → três camadas" deixa de existir, que era a razão de eu ter recomendado a Opção B. A edição dele é melhor que a minha proposta.)*
  - Freeze the architecture, move only the input, and the result moves.
  - **The representation is the bottleneck.**
  - Two limits stay: one vector per **place**, and a split that shares users.
- **Fala (PT):** "Com a arquitetura fixa, a entrada moveu o resultado: a representação é o gargalo. Mas o diagnóstico ainda é em nível de lugar, sob um protocolo que deixa o mesmo usuário dos dois lados da divisão. O terceiro estudo reconstrói as três camadas: representação, topologia e protocolo."
- **Proveniência:** PLANO §2, transição de saída do Ato II, redação literal; `chapters/6_conclusion.tex` §6.1 (*"this comparison identifies the input representation as the main bottleneck in that configuration"*); prefácio do Cap. 4 (o protocolo estratificado por amostra, e a chegada da validação cruzada disjunta por usuário só no último estudo). Nenhum número.
- **Nunca dizer:** que a correção de um vazamento foi o pivô. A direcionalidade das arestas entra em S37, como princípio de projeto, na redação do próprio Cap. 5.

---

# sec5

# SEÇÃO 5 · A Check-in-Level Multitask Study of Next Category and Region (20 min)

> `\section[Check2HGI]{A Check-in-Level Multitask Study of Next Category and Region}`
> Proveniência no divisor: **MobiWac 2026, submitted, under review. Vitor H. O. Silva, first author.**
> **Ordem fixa (PLANO §3):** 5.1 · **5.2A** · 5.2 · 5.3 · 5.4 · 5.5 · 5.6. O trabalho relacionado
> deste estudo vem **antes** do método, porque a lacuna precede a solução.

### S33 · Three changes, each a consequence of the diagnosis
- **Slide impresso:** **27**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.1   **Tempo:** 60 s
- **LEDGER:** INTRODUZ as três mudanças do Cap. 5 (representação, topologia, protocolo) · RETOMA o gargalo de 4.5, a armadilha 2 (o par de tarefas muda) e a restrição de modelo único de 1.3
- **Na tela:** três linhas *from → to*, com a razão à direita, e uma faixa de fecho.
  - **Representation.** place level → **check-in level.** A place embedding cannot tell a weekday lunch from a Saturday night out at the same place.
  - **Topology.** hard parameter sharing → **cross-attention between per-task streams**, with a private spatial path for the region output.
  - **Protocol.** sample-stratified folds → **user-disjoint** five-fold cross-validation, four seeds, tests fixed before any result was read.
  - Faixa: **The task pair changes here.** Under a check-in-level representation, static category classification is a less natural companion than a second sequential target, so the pair becomes **next category + next region**. The restriction holds: one artifact, one forward pass, two answers.
- **Fala (PT):** "As três mudanças do último estudo, e nenhuma delas é preferência minha: as três são consequência do diagnóstico do capítulo anterior. A representação sai do nível de lugar para o nível de check-in, porque um vetor por lugar não distingue um almoço de quarta-feira de uma noite de sábado no mesmo lugar. A topologia sai do compartilhamento rígido para atenção cruzada entre as duas tarefas, com um caminho espacial privado na saída de região. E o protocolo sai do estratificado por amostra para validação cruzada com **usuários disjuntos**, quatro sementes, e testes fixados antes de qualquer resultado ser lido. Aqui eu cumpro o aviso que dei na Seção 2: **o par de tarefas muda**. Com uma entrada por visita, a classificação estática vira um par pouco natural, e o par passa a ser próxima categoria mais próxima região, dois alvos finais sequenciais. A restrição da abertura continua valendo: um artefato, uma passagem, duas respostas."
- **Proveniência:** as três mudanças e a razão da troca do par → `chapters/1_introduction.tex:168-190`; a formulação das duas melhorias → `chapters/5_mobiwac/01_introduction.tex:24-27`; "one model, one forward pass, two predictions" → `chapters/5_mobiwac/04_method.tex:70` (legenda da Fig. 5).
- **Nunca dizer:** creditar qualquer uma das três mudanças a uma correção de vazamento. "Prevê o próximo lugar".

### S34 · Next region: the task, and why it is worth predicting
- **Slide impresso:** **28**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.2A (a)   **Tempo:** 52 s  *(medido)*
- **LEDGER:** INTRODUZ a tarefa de próxima região e as suas motivações · RETOMA o eixo meio × fim de 2.6 e as contagens de região da Tab. 8 (2.3)
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **The task** — classification over the dataset's candidate regions, **520 (Istanbul) to 8,501 (California)**; coarser than a place, not easier; **Why this target** — the category says *what type* comes next; the region says *where*, hence where to prepare; **Where it sits** — the standard formulation targets a **grid cell**; here, official neighborhood-scale units. In MCMG and HMT-GRN, category and region are **auxiliary** to a primary next-place task; **Scope** — demand and load anticipation, caching ahead of time, capacity planning. **No such service is built or evaluated here.**;
- **Fala (PT):** "Trabalho relacionado deste estudo, que os dois primeiros não têm, e a primeira metade é a tarefa nova. O alvo é a região --- de 520 em Istambul a 8.501 na Califórnia. Ela cobre uma área maior que um lugar, então é um alvo mais fácil do que o lugar exato. Mas a tarefa não é fácil. Prever sobre uma partição do mapa é a formulação padrão em mobilidade, com célula de grade como alvo; aqui entra no lugar dela a unidade administrativa de bairro. E onde a área já modela várias granularidades, categoria e região aparecem como sinais auxiliares de um alvo principal de próximo lugar. Eu estudo o par como objeto. O escopo vai junto com a motivação: preparação em nível de bairro, e nenhum serviço construído ou avaliado aqui."
- **Proveniência:** 520 a 8.501, as sete categorias, a motivação e o escopo → `chapters/5_mobiwac/03_problem.tex:13-24`; célula de grade e a substituição por unidade administrativa, categoria e região como auxiliares em MCMG e HMT-GRN → `chapters/5_mobiwac/02_related.tex:80-95`; contagens de região por conjunto → `tables/mobiwac/datasets.tex` (Tab. 8, coluna Regions).
- **Nunca dizer:** especulação sobre erro geográfico ou desempenho de serviço (§8 regra 16). Afirmação de ineditismo mais forte que a entregue, que é escopada a "to our knowledge" e "underexplored".

### S35 · Why a per-visit representation is new in this line
- **Slide impresso:** **29**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.2A (b)   **Tempo:** 49 s  *(medido)*
- **LEDGER:** INTRODUZ CTLE como a arte prévia mais próxima · RETOMA a escada de representações de 2.7
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **CTLE** — the closest prior contextual check-in representation: one vector per visit, learned by masking and reconstructing a user's check-in sequence; **the difference is the construction** — CTLE is a **sequence model**, a Transformer; Check2HGI stays a **graph model**: same hierarchy, same infomax objective, **one level deeper**; **what CTLE pretrains on** — place identifiers and timestamps alone; the category vocabulary never enters its training;
  - Bloco **(sem título)**:
    - **The novelty is the combination:** per-visit context **inside** a hierarchical graph-infomax representation;
- **Fala (PT):** "Segunda metade: por que uma representação por visita é nova nesta linha. A arte prévia mais próxima é o CTLE, que também dá um vetor por visita, aprendido mascarando e reconstruindo partes da sequência de check-ins do usuário. A diferença é de construção. O CTLE é um modelo de sequência, um Transformer que lê a própria sequência; o Check2HGI continua um modelo de grafo, com a mesma hierarquia de lugar, região e cidade e o mesmo objetivo infomax, agora um nível mais fundo. E o CTLE pré-treina só sobre identificador de lugar e marca de tempo, então o vocabulário de categoria nunca entra no treino dele. A novidade que eu reivindico é a combinação."
- **Proveniência:** CTLE, a distinção modelo de sequência × modelo de grafo e "The novelty is this specific combination" → `chapters/5_mobiwac/02_related.tex:59-72`; o que o CTLE pré-treina → `chapters/5_mobiwac/06_results.tex:40`.
- **Nunca dizer:** que o CTLE foi superado aqui. O número do CTLE fica em S45, e o que ele estabelece é uma ordenação entre famílias de representação.

### S36 · Check2HGI: a fourth level below the place
- **Slide impresso:** **30**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.2 (a)   **Tempo:** 80 s
- **LEDGER:** INTRODUZ Check2HGI · RETOMA a ideia infomax de 2.1, o diagrama de níveis de 2.1 e o HGI de 4.1A
- **Na tela:** *(v3 · `AUT-18` executada 26/08)* **SÓ A IMAGEM** — `fig1_dataflow` no **tamanho natural** (136,6 × 62,4 mm, `\includegraphics` sem `width=`), `\makebox` sem cola. **Zero marcadores.**
  > ⚠ **Por que o tamanho natural importa, e foi medido:** a figura estava a `width=0.50\textwidth`, ou seja, **exibida pela metade** do tamanho para que foi desenhada, e o texto interno (`four-level graph`, `per-visit vectors`, `edges: consecutive visits by a user`) ficava abaixo do piso de legibilidade no Meet. A 136,6 mm a altura é 62,4 contra **66,2 mm úteis** — cabe com folga. **Eram os quatro marcadores que a espremiam.**
  >
  > ✅ **"Nada se perde" foi verificado antes do corte, marcador por marcador, contra a fala:** *four levels* → *"acrescenta um quarto nível abaixo do lugar"* · *edges* → *"ligam cada nível ao de cima… e os check-ins consecutivos"* · *no task label* → *"nenhum dos dois usa rótulo"* + *"o grafo nunca vê a próxima categoria"* · *two outputs* → *"um vetor de 64 dimensões por visita, e um vetor por região"*. **A tela perdeu redundância, não informação.**
  >
  > 🔧 **O gênero da figura continua aberto e NÃO bloqueia nada.** Trocar pela `c2h_flow` é **uma linha** — o `\graphicspath` já cobre `plates/`.

  **O que a figura carrega, e que a fala diz junto** *(registro; não está mais na tela)*:
  - The four levels: **check-in · place · region · city.** The place, region, city hierarchy is the HGI of Chapter 4; **the check-in is the new level**.
  - Edges: each level to the one above it; nearby places at the place level; **a user's consecutive check-ins**, with a weight that decays as the time gap grows. Two visits to one place meet through their shared place node.
  - **Trained with no task label:** mainly an infomax objective, each vector learning to match its real neighborhood and reject a shuffled one, plus two small label-free auxiliary terms (weights 0.3 and 0.1).
    > 🛑 **NÃO "corrija" 0,3 e 0,1 para 0,4/0,3/0,3.** São **dois pares diferentes** e os dois estão certos: `0.3` e `0.1` são os **termos auxiliares** (`5_mobiwac/04_method.tex:18`, *"Two small label-free auxiliary terms are added (weights 0.3 and 0.1)"*); `0.4/0.3/0.3` é a soma das **três fronteiras hierárquicas** (`2_fundamentals.tex:711-713`, `eq:fund:check2hgi`). Confundi-los troca um mecanismo pelo outro.
  - Two outputs: **one 64-dimensional vector per visit**, and **one vector per region**.
- **Fala (PT):** "O Check2HGI, e ele se apoia direto no HGI do capítulo anterior. O HGI tinha três níveis: lugar, região e cidade. O Check2HGI acrescenta **um quarto nível abaixo do lugar**, que é o próprio check-in. As arestas ligam cada nível ao de cima, ligam lugares próximos no nível de lugar, e ligam os check-ins consecutivos de um mesmo usuário, com um peso que decai conforme o intervalo entre as visitas cresce. Duas visitas ao mesmo lugar se encontram pelo nó de lugar, um nível acima. O treino é o objetivo infomax da Seção 2, agora um nível mais fundo: cada vetor aprende a reconhecer a vizinhança verdadeira e a rejeitar uma embaralhada. Junto com ele vão dois termos auxiliares pequenos, de pesos 0,3 e 0,1, e nenhum dos dois usa rótulo. Este é o ponto que eu quero deixar assentado antes de qualquer resultado: **o grafo nunca vê a próxima categoria nem a próxima região**. E do grafo treinado saem duas tabelas: um vetor de 64 dimensões por visita, do nível de check-in, e um vetor de 64 dimensões por região, do nível de região. São essas duas tabelas que o modelo da próxima tela vai ler."
- **Proveniência:** quatro níveis, arestas, decaimento temporal, objetivo infomax, os dois termos auxiliares de pesos 0.3 e 0.1, "The training uses no task label" e a extração dos dois conjuntos de vetores → `chapters/5_mobiwac/04_method.tex:18-22`; Fig. 4 = `figures/mobiwac/fig1_dataflow.pdf`, declarada em `chapters/5_mobiwac/02_related.tex:280`.
- **Nunca dizer:** nenhum p-valor nesta subseção. "Substrate" (palavra de repositório).

### S37 · What each visit contributes
- **Slide impresso:** **31**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.2 (b)   **Tempo:** 70 s
- **LEDGER:** INTRODUZ as features de nó por visita · INTRODUZ a aresta só para frente, como princípio de projeto
- **Na tela:** **The node features, and one design principle.** *(v2 · 161 → ~91 palavras. Acima do teto, e de propósito: o `alertblock` é citação verbatim do capítulo.)*
  - **Semantic** — the category of the visited place, as an indicator;
  - **Cyclical time** — time of day and day of week, through sine and cosine;
  - **Elapsed time** — since the previous visit, since the first visit, the within-day gap, a first-visit indicator.
  - Bloco **A design principle, in the chapter's own wording**, verbatim e intocado: *"The consecutive-visit edges run in one direction only, from an earlier visit to a later one, for the same reason: a target is predicted from a user's past, so the representation is built from the past alone."*
- **v2 · o que saiu da tela, e onde ficou:** *"the endpoints of the daily and weekly cycles fall next to each other"*, *"both log-compressed"* e *"these give the representation a sense of tempo"* → fala do próprio S37. A linha de rodapé *"Every value is measured up to the visit itself: a node describes the visit and the history preceding it, never anything that follows"* saiu por ser **redundante com o `alertblock` logo acima**, que diz a mesma coisa em redação mandatada — não por corte de densidade. ⚠ **O `alertblock` NÃO foi tocado**: é a direcionalidade dita como princípio de projeto, nas palavras do próprio Cap. 5 (decisão travada, `HANDOFF.md` §5).
- **Fala (PT):** "O que cada visita contribui na entrada, e é aqui que está a informação que um vetor por lugar não consegue carregar. Três grupos. O semântico: a categoria do lugar visitado, como indicador sobre as classes. O tempo cíclico: hora do dia e dia da semana pelo seno e pelo cosseno, para que o fim e o começo de cada ciclo fiquem vizinhos, e não em pontas opostas de uma escala. E os tempos decorridos: o intervalo desde a visita anterior e o intervalo desde a primeira visita daquele usuário, os dois comprimidos por logaritmo, mais o intervalo dentro do mesmo dia e um indicador de primeira visita. É isso que dá ritmo à representação: distinguir a visita que vem minutos depois da anterior daquela que abre um passeio novo. E aqui um princípio de projeto, na redação do próprio capítulo: as arestas entre visitas consecutivas correm numa direção só, da visita anterior para a posterior. A razão está na mesma frase: o alvo é predito do passado do usuário, então a representação é construída só do passado. Todo valor é medido até a própria visita."
- **Proveniência:** os três grupos e a direcionalidade → `chapters/5_mobiwac/04_method.tex:18` (frase citada literalmente) e `chapters/2_fundamentals.tex:703-712` (a mesma composição, com seno e cosseno).
- **Nunca dizer:** a aresta só para frente como conserto, correção ou descoberta. Ela é decisão de projeto que o documento explica. Se perguntarem por que a direcionalidade importa, a resposta é o princípio; se alguém perguntar por um episódio de correção no repositório, é o slide **B2**, com a proveniência primeiro.

### S39 · The architecture: sharing by exchange
- **Slide impresso:** **32**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.3 (a)   **Tempo:** 74 s  *(medido)*
- **LEDGER:** INTRODUZ o modelo conjunto e o tronco de atenção cruzada · RETOMA o compartilhamento rígido de 3.2 e a bifurcação de três suspeitos de 3.5
- **Na tela:** figura + três fragmentos + uma faixa de fecho. *(v2 · reescrito 2026-08-24 por decisão do autor — "slide 39 precisa de atenção".)*
  - **[Fig. 5]** `fig2_model`, agora em **0,56 da largura** (era 0,38).
  - **Two inputs, one model** — o **semantic stream** lê os vetores por visita; o **spatial stream** lê a mesma janela, cada visita como o vetor do seu nó de região;
  - **private per-task encoders** — sem pesos compartilhados;
  - **the shared trunk** — uma pilha de atenção cruzada de dois blocos.
  - Faixa de fecho: The tasks share by **exchanging information between per-task streams**, not by owning hidden layers in common.
- **v2 · os dois defeitos, e a troca que os resolveu:** (1) **a figura estava a 52% do tamanho nativo** — 148 pt renderizados contra os 283,6 pt do `fig2_model.pdf` —, o que tornava ilegíveis os rótulos internos (*"shared trunk (bidirectional cross-attention ×2)"*, *"raw region (private spatial path)"*) no tamanho real de uma janela do Meet. Passou a **81%**: 1,55× linear, ~2,4× em área. (2) **O `alertblock` de fecho estourava a caixa do frame** — corria até a borda sem fechar. ⚠ **A troca que liberou o espaço:** o bloco virou **faixa de uma linha** (~14 pt de altura em vez de ~40). A frase permanece na tela **inteira**, porque ela é o RETOMA do compartilhamento rígido do Cap. 3 e não podia sair. O que saiu foi a repetição em palavras do que a figura mostra em desenho: *"attention lets each stream read the other's features, each keeping its own feed-forward weights"* → fala do próprio S39 (verificado: a fala já a carregava).
- **Fala (PT):** "A arquitetura, e o que mudou no multitarefa. Cada tarefa tem a sua entrada. A de categoria lê a janela de vetores por visita, que é o fluxo semântico. A de região lê a mesma janela de visitas, só que cada visita agora representada pelo vetor treinado do nó de região dela, que é o fluxo espacial. As duas passam por encoders privados, sem peso nenhum compartilhado. E o tronco compartilhado é uma pilha de dois blocos de atenção cruzada: em cada bloco a atenção deixa um fluxo ler as features do outro, enquanto cada um mantém os próprios pesos feed-forward. É esta a frase que eu quero que fique da tela: as tarefas compartilham **por troca de informação entre as duas tarefas**, e não por possuírem camadas ocultas em comum. Comparem com o Capítulo 3, onde tudo atravessava um tronco único e as tarefas só se separavam nas saídas. É a mesma família de modelos, com a topologia de compartilhamento trocada, e a topologia era um dos três suspeitos do nulo."
- **Proveniência:** dois fluxos, encoders privados, pilha de dois blocos de atenção cruzada e "not by owning hidden layers in common" → `chapters/5_mobiwac/04_method.tex:26-31`; Fig. 5 = `figures/mobiwac/fig2_model.pdf`, legenda em `chapters/5_mobiwac/04_method.tex:66-70`.
- **Nunca dizer:** creditar transferência entre tarefas a partir desta tela. "Backbone", "dual-tower", o identificador de repositório do modelo.

### S40 · The private spatial path
- **Slide impresso:** **33**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.3 (b)   **Tempo:** 90 s
- **LEDGER:** INTRODUZ o caminho espacial privado, a perda de peso fixo com ajuste de logit, e a posição do autor sobre o tronco compartilhado
- **Na tela:** *(v2 · 183 → ~99 palavras. Acima do teto de 70, e de propósito: o bloco da posição é redação mandatada pelo `PLANO_FLUXO_DEFESA.md` §5.3 e é o conteúdo do slide.)*
  - **A branch inside the one model**, not a second model — bypasses the shared trunk, feeds the region output only; **the category task never touches it**;
  - **Fixed loss:** **0.5 category + 0.5 region**, by design;
  - **Logit adjustment** on category (τ = 0.5, training only) — **the dedicated model receives the same**.
  - Bloco **The position on the shared trunk**, verbatim e intocado: *"The evidence does not separate the contributions of the shared trunk and the private spatial path. It does not establish that sharing helps, and it does not rule it out. The claim I make is about the design."*
- **v2 · o que saiu da tela, e onde ficou:** *"it reads the spatial input window"* e *"so that any improvement over the dedicated models comes from the shared representation and not from an adaptive weighting scheme"* → fala do próprio S40. *"which shifts the decision boundary toward the balanced posterior that macro-F1 rewards"* e *"class weighting was tested on both outputs and lowered both scores"* → fala do S40. ⚠ **O `alertblock` da posição NÃO foi tocado** — é redação mandatada (§5.3) **e** é admissão contra o próprio argumento; sai da tela por cima do meu cadáver.
- **Fala (PT):** "Duas coisas fecham a arquitetura, e depois uma posição que eu preciso enunciar com precisão. A primeira é o caminho espacial privado: a saída de região tem, além do tronco, um ramo pequeno **dentro do mesmo modelo**, e não um segundo modelo, que lê a janela espacial e contorna o tronco. A tarefa de categoria não toca nesse ramo. A segunda é a perda: uma soma de peso fixo, meio a meio entre as duas tarefas, e o peso é fixo **de propósito**, para que qualquer melhora sobre os dedicados venha da representação compartilhada e não de um esquema adaptativo de ponderação. A saída de categoria treina com ajuste de logit, que empurra a fronteira de decisão para o posterior balanceado que a macro-F1 premia, e o **modelo dedicado de categoria recebe o mesmo ajuste**, então a comparação entre os dois não é afetada por ele. Agora a posição. A evidência aqui **não separa** as contribuições do tronco compartilhado e do caminho espacial privado. Ela não estabelece que o compartilhamento ajuda, e não o descarta. A afirmação que eu faço é sobre o desenho: esta combinação produz uma saída de região acima de dois modelos dedicados, nos dois conjuntos com os maiores números de regiões. Não é uma afirmação sobre transferência entre tarefas."
- **Proveniência:** caminho privado e a equação da perda 0.5/0.5, "kept simple by design", o ajuste de logit com τ = 0.5 e "The dedicated category model receives the same adjustment" → `chapters/5_mobiwac/04_method.tex:31-46`; a formulação simétrica sobre o tronco → `chapters/5_mobiwac/07_discussion.tex:51-59` ("The evidence here does not separate their contributions"); a redação em três frases curtas → PLANO §5.3.
- **Nunca dizer:** "não podemos provar que não contribuiu, portanto provavelmente contribuiu". Creditar Texas e Califórnia a transferência entre tarefas. Nenhuma afirmação de Pareto sobre estes modelos.

### S41 · Protocol, step 1 of 4: the unit of data
- **Slide impresso:** **34**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.4 (degrau 1)   **Tempo:** 75 s  *(medido)*
- **LEDGER:** INTRODUZ o split disjunto por usuário e as janelas sobrepostas de passo 1 · RETOMA o protocolo estratificado por amostra de 2.5
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **User-disjoint five-fold cross-validation** — every window from one user stays in one fold; **the repair of the limitation declared in Chapter 3**; stratified by the **next-category label**, the seven classes being imbalanced; **sliding windows, stride 1** — nine visits in, the next visit is the target; **not the same windows as Chapters 3 and 4**, which used non-overlapping ones; the **held-out fold provides the validation data** — no third split is reserved. *Limit 2, later in this section, comes from this line.*;
- **Fala (PT):** O protocolo, em quatro passos, e de cada um eu digo a razão. Primeiro, a unidade de dado. Validação cruzada de cinco partições, disjunta por usuário: todas as janelas de uma pessoa ficam do mesmo lado da divisão. Isso é o reparo direto da limitação que o Capítulo 3 declarou, em que os check-ins de um mesmo usuário caíam dos dois lados. E uma ressalva que eu dou antes de alguém pedir: a partição retida é a que serve de validação, e eu não reservo uma terceira divisão. É dela que sai o segundo limite que eu apresento no fim desta seção.
- **Proveniência:** janelas de nove visitas, passo 1, mínimo de dez visitas e remoção de duplicatas → `chapters/5_mobiwac/05_setup.tex:28`; split por usuário, estratificação por próxima categoria e "The held-out fold provides the validation data, and we do not reserve a third split" → `chapters/5_mobiwac/05_setup.tex:30`.
- **Nunca dizer:** "as mesmas janelas" para os três estudos. "Fold" como palavra solta na fala: a superfície em português é partição.

### S42 · Protocol, step 2 of 4: what is measured
- **Slide impresso:** **35**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.4 (degrau 2)   **Tempo:** 101 s  *(medido)*
- **LEDGER:** INTRODUZ Acc@10, o desconto OOD e o piso de Markov-1 · RETOMA macro-F1 e o piso de classe majoritária de 2.4
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - **Category: macro-F1** — reference point the **majority-class floor**, **5.7 to 7.3** depending on the dataset. *At Florida that floor is right on **24.7%** of the visits and still scores **5.7** macro-F1 — which is why plain accuracy is not the metric here*; **Region: Acc@10** — the share of test visits whose true region is among the ten highest-scoring predictions; *it does not separate first place from tenth*; **OOD-discounted Acc@10** — a region absent from the training fold counts as an error; **Reference points for region** — the **dedicated single-task model**, and the **Markov-1 floor** over region transitions, **51 to 72** Acc@10 under the same windows and folds;
- **Fala (PT):** Segundo, o que se mede. Em categoria, macro-F1, e a razão é a distribuição: na Flórida, um preditor que sempre responde a categoria mais comum acerta vinte e quatro vírgula sete por cento das visitas e ainda assim marca cinco vírgula sete de macro-F1. É por isso que acurácia simples não é a métrica aqui: ela premiaria exatamente esse preditor. Em região, acurácia em dez, a fração de visitas cuja região verdadeira está entre as dez mais pontuadas. E eu digo o que ela não faz: não separa o primeiro lugar do décimo. Região ausente do treino conta como erro. Os pontos de referência são o modelo dedicado e o piso de Markov.
- **Proveniência:** macro-F1, Acc@10 e o desconto OOD → `chapters/2_fundamentals.tex:1645-1667` e `chapters/5_mobiwac/05_setup.tex:111`; piso de classe majoritária 5.7 a 7.3 → `chapters/5_mobiwac/06_results.tex:122-123`; piso de Markov-1 de 51 a 72 e a razão do piso alto (persistência de região sob janelas de passo 1) → `chapters/5_mobiwac/06_results.tex:264-266` e `:274-284`; construção do piso → `chapters/5_mobiwac/05_setup.tex:178`. ⚠ **O exemplo da Flórida, acrescentado 2026-08-24 por decisão do autor:** os **24,7%** são a coluna *Majority* da Tab. 8, linha FL → `tables/mobiwac/datasets.tex`; o piso de **5,7** → `06_results.tex:54-56`. A derivação de qual conjunto tem o máximo (**Alabama, 7,3** — nunca nomeado em documento entregue) está em `docs/studies/closing_data/v18/MAJORITY_CLASS_FLOOR_PER_STATE.md`, com script. ⚠ **A redação contrasta as duas medidas do MESMO preditor, e não as equipara** — equipará-las é o que o `Nunca dizer` do S11 proíbe.
- **Nunca dizer:** Acc@10 sem o desconto OOD. Nenhum número sem o seu ponto de referência.

### S43 · Protocol, step 3 of 4: what is compared
- **Slide impresso:** **36**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.4 (degrau 3)   **Tempo:** 99 s  *(medido)*
- **LEDGER:** INTRODUZ a semente como unidade de repetição, os vinte modelos ajustados, a unidade inferencial n = 4 e a convenção joint-best
- **Na tela:** **3 · what is compared.** *(v2 · 185 → ~62 palavras. Zero frases completas nos marcadores; a única frase é a admissão do bloco.)*
  - Joint model against the **dedicated single-task models**;
  - Same representation, same windows, **same folds**;
  - **A seed** = one full five-fold repetition: initialization *and* user partition;
  - Four seeds **{0, 1, 7, 100}** × five folds = **20 fitted models**;
  - Inferential unit: **n = 4**, the four per-seed means.
  - Bloco **The joint-best convention**: Both scores from **one saved model per fold**, at the epoch the joint validation score picks. **Every verdict here is the one the stricter convention yields.**
- **v2 · o que saiu da tela, e onde ficou:** *"which is what licenses pairing"* → fala do próprio S43. Os números da convenção mais frouxa — **0,23 macro-F1** e **0,93 Acc@10**, e as *"four further category results and two further region results"* que ela transformaria em melhorias → fala do S43 **e tela do SB4** (`B1-3`, que é a pergunta de banca sobre exatamente esta escolha; verificado por grep). ⚠ **A admissão *"every verdict here is the one the stricter convention yields"* FICA na tela** — é admissão contra o próprio argumento, não qualificação técnica.
- **Fala (PT):** Terceiro, o que se compara. O modelo conjunto contra os dedicados, com a mesma representação, as mesmas janelas e as mesmas partições. E a convenção que decide qual número eu reporto: os dois resultados saem de um único modelo salvo por partição, escolhido pela média geométrica das duas métricas. Eu digo isso com todas as letras porque ela me custa caro: a convenção alternativa, ler cada tarefa na melhor época dela, é mais favorável ao modelo conjunto, e transformaria mais quatro células de categoria e mais duas de região em melhorias que sobrevivem à mesma correção. Eu escolhi a que produz menos vitórias, porque é a única que um sistema implantado consegue servir.
- **Proveniência:** definição de semente, 4 × 5 = 20 modelos ajustados, unidade inferencial n = 4 → `chapters/5_mobiwac/05_setup.tex:115-117`; as sementes 0, 1, 7 e 100 → `chapters/apx_a_contributions.tex:56`; joint-best, a média geométrica das duas métricas e os limites 0.23 macro-F1 e 0.93 Acc@10, com "four further category cells and two further region cells" → `chapters/5_mobiwac/06_results.tex:134-146`; equação da nota conjunta → `chapters/2_fundamentals.tex:1677-1680`.
- **Nunca dizer:** "n = 20 repetições pareadas". Misturar joint-best com a leitura por tarefa dos Caps. 3 e 4 sem declarar. "As mesmas partições" entre sementes: vale dentro de uma semente.

### S44 · Protocol, step 4 of 4: how it is decided
- **Slide impresso:** **37**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.4 (degrau 4)   **Tempo:** 135 s  *(medido)*
- **LEDGER:** INTRODUZ o teste pareado de superioridade, o TOST na margem registrada, a correção de Holm e o desvio declarado do Wilcoxon
- **Na tela:** **4 · how it is decided.** *(v2 · 206 → 59 palavras. Uma frase completa, a que É o conteúdo; o resto em fragmentos.)*

  > **A claimed gain and a claimed match require different tests**  *(verbatim, `05_setup.tex:113` — a passagem anti-match do capítulo; decisão do autor 2026-08-24)*

  - Analysis plan written **before any result was read**;
  - **Superiority** → next category;
  - **Non-inferiority** → next region, **two-point margin**;
  - Paired *t* · 90% CI · **Holm** across the six datasets;
  - **Declared departure:** registered Wilcoxon **reported alongside, and agrees**.
- **v2 · o que saiu da tela, e onde ficou:** *"a non-significant difference is not evidence of equivalence"* → fala do próprio S44 (dita logo após a manchete). A razão dos dois pontos (*"below the level at which neighborhood-scale preparation would behave differently"*) → fala do S44. O piso de **0.0625** do Wilcoxon exato e a não-independência das partições dentro de uma semente → fala do S44 **e tela do SB5** (`B1-4`, verificado). As **duas consequências** (região sem teste de superioridade → resultados secundários; categoria sem margem → não resolvida) → fala do S44 **e telas do SB2** (`B1-1`, direção das quatro células) **e do SB3** (`B1-2`, o que se usa em categoria). Nenhuma cláusula saiu sem destino conferido.
- **Fala (PT):** Quarto, como se decide, e o ponto é que um ganho afirmado e uma paridade afirmada exigem testes diferentes. Para próxima categoria, superioridade: eu pergunto se o conjunto é melhor. Para próxima região, não-inferioridade, com margem de dois pontos registrada antes de qualquer resultado ser lido: eu pergunto se ele não é pior. Isso importa porque ausência de significância não é evidência de igualdade — dizer 'não deu diferença, logo empatou' é formalmente inválido, e é a prática corrente na literatura de multitarefa. O plano foi escrito antes. Teste t pareado, intervalo de noventa por cento, correção de Holm sobre os seis conjuntos. E um desvio declarado: o plano registrava Wilcoxon, e com quatro sementes o Wilcoxon exato não desce abaixo de zero vírgula zero seiscentos e vinte e cinco. Ele não podia decidir nada. Continua reportado ao lado, como sensibilidade, com os dois testes no código publicado. E o asterisco que está na tela: o protocolo estatístico foi refinado depois, com base na literatura. É posterior ao que a banca recebeu, e não muda nenhum veredito.
- **Proveniência:** "A claimed gain and a claimed match require different tests", a atribuição por tarefa, os ganhos de região como resultados secundários fora do plano e a categoria como não resolvida → `chapters/5_mobiwac/05_setup.tex:113`; t pareado sobre as quatro médias, IC de 90%, Wilcoxon registrado como sensibilidade e o piso de 0.0625 → `:115`; Holm sobre as seis comparações de cada eixo → `:117`; TOST, a margem de dois pontos fixada em avanço e a razão de serviço → `:119`.
- **Nunca dizer:** apresentar o desvio como confissão. Aplicar a margem de dois pontos ao eixo de categoria. "Significativo" sem nomear o teste. ⚠ **E não confundir o `match` desta manchete com o `match` proibido do `HANDOFF.md` §6.** Aqui a palavra é usada no sentido ABSTRATO e NEGATIVO do próprio Cap. 5 — *que tipo de alegação exige que tipo de teste* —, colada à frase seguinte do capítulo (*"a non-significant difference does not provide evidence of a match"*). O que continua proibido é `match`/`empata`/`ties` como **verbo de veredito** sobre o nosso resultado. Se algum agente futuro for "higienizar" esta palavra, ele estará apagando a passagem anti-match do capítulo.
- **Se perguntarem** *(criado 2026-08-24 pela decisão do verbatim; a pergunta é natural para um arguidor que esteja acompanhando a disciplina de linguagem):* — *"o seu glossário proíbe 'match' e o seu slide diz 'match'. Como é?"*
  > "É a frase do próprio Capítulo 5, citada literalmente, e ela é a passagem que **proíbe** o termo, não que o usa: afirmar ganho e afirmar match exigem testes diferentes, e uma diferença não significativa não é evidência de match. O que o registro bane é `match` como **verbo de veredito** sobre o meu resultado — e esse eu não uso em lugar nenhum do deck nem do documento."
  ⚠ **Descompasso deliberado tela/voz neste slide:** a tela diz `match` (inglês, verbatim do capítulo) e a fala diz *equivalência* (português, termo técnico). As duas **não são tradução uma da outra** — `match` é a alegação leiga, *equivalência* é a técnica. Saída limpa, se quiser fechar: citar e depois glosar — *"a frase do capítulo é esta: afirmar ganho e afirmar equivalência exigem testes diferentes"*. Assim a defasagem vira gesto deliberado em vez de descompasso.

### S45 · Result 2: the representation, at every dataset
- **Slide impresso:** **39**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.5 (a)   **Tempo:** 48 s  *(medido)*
- **LEDGER:** INTRODUZ o resultado de representação (Tab. 9) e os dois controles · RETOMA CTLE de 5.2A
- **Na tela:** **Tab. 9 inteira**, agora em largura cheia e corpo maior. **Ela aparece uma vez só no deck.** *(v2 · 221 → 66 palavras de prosa. O bloco lateral de prosa some — regra 4: resultado é tabela + legenda.)*

  | **Dataset** | **Check-in level** | **Place level** | **Δ** |
  |---|---:|---:|---:|
  | AL | **30.77** ±1.16 | 29.15 ±0.84 | +1.62 |
  | AZ | **34.51** ±1.15 | 31.93 ±1.08 | +2.58 |
  | Istanbul | **35.35** ±0.89 | 29.07 ±0.63 | +6.29 |
  | FL | **37.36** ±0.42 | 37.13 ±0.41 | +0.23 |
  | CA | **35.62** ±0.47 | 34.74 ±0.41 | +0.88 |
  | TX | **36.32** ±0.51 | 35.33 ±0.48 | +0.99 |

  - Convenção desta tabela, distinta da próxima: **seed 0, five matched folds; ± is the fold sd.**
  - **Only the input changes** — same target, model, training configuration, folds, windows, epoch budget, logit adjustment.
  - Nota de rodapé da própria tabela: **All five folds favor the check-in-level representation at every dataset. A paired test separates the two columns at every dataset except Florida (p = 0.07).**
  - Faixa dos controles, em uma linha: **Controls — CTLE (Florida) 33.45 macro-F1; feature concatenation +2.0 / +1.7 / +0.8.**
- **v2 · o que saiu da tela, e onde ficou:** a prosa do **CTLE** (*"fine-tuned at Florida... about two points below the place embedding under the same rule, and repeats the ordering with fixed weights at Alabama, Arizona and Istanbul"*) → fala do próprio S45; **o número 33.45 permanece na tela**, porque o `Nunca dizer` do S35 registra que *"o número do CTLE fica em S45"* e ele não tem outra casa em nenhum slide. A prosa da **concatenação de features** → fala do S45 **e tela do SB13** (`B3-2 · B-Q13`, que carrega a tabela do controle refeito, com o *share of the gap*). A faixa de leitura longa (*"same target, same single-task model, same..."*) virou fragmento; a íntegra continua na fala. Nenhum número saiu da tela sem destino conferido.
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "Segundo resultado, e é o mais controlado da dissertação: só a entrada muda. Mesmo alvo, mesmo modelo, mesma configuração de treino, mesmas partições, mesmas janelas. A coluna da esquerda é a representação em nível de check-in, a do meio é o embedding por lugar, e a da direita é a diferença. Ela é positiva nos seis conjuntos, de mais zero vírgula vinte e três na Flórida a mais seis vírgula vinte e nove em Istambul. O desvio ao lado é entre as cinco partições, com semente zero. Um teste pareado separa as duas colunas em cinco dos seis conjuntos; a Flórida é a exceção, com p igual a zero vírgula zero sete."
- **Proveniência:** todas as células e a nota de rodapé → `tables/mobiwac/representation.tex` (Tab. 9, copiadas célula a célula, incluindo a convenção "seed 0" da legenda); faixa de +0.23 a +6.29, unanimidade das cinco partições, Florida a p = 0.07 e "a consistent direction rather than a large effect" → `chapters/5_mobiwac/06_results.tex:28-36`; CTLE 33.45 → `:40`; concatenação +2.0, +1.7, +0.8 → `:45`.
- **Nunca dizer:** "o nível de check-in bate o de lugar nos seis" no sentido de teste: o teste separa em cinco. Nunca generalizar a cláusula do capítulo *"under a tenth of the place-to-check-in gap"*: ela é dita **por estado**, e generalizá-la é aritmeticamente falso contra a própria Tabela 9, na mesma página. Nunca chamar a diferença de representação de "margem". ⚠ **E nunca a frase retratada** — *"o ganho vem da representação hierárquica e não da injeção de features"*. O controle refeito (`wrapup/post_submission_studies/Q13_concatenation_control.md`, 16/08) conclui que **a frase depositada está errada na direção**, e há errata escrita. Os números desta própria tela a refutam: no Alabama a concatenação levanta **+2,0** contra um salto total de **+1,62**.

### S46 · Result 3: one model, two tasks
- **Slide impresso:** **40**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.5 (b)   **Tempo:** 195 s  *(medido)*
- **LEDGER:** INTRODUZ a Tab. 10 e os resultados dos métodos externos do Cap. 5 · RETOMA o mapa de métodos de referência de 2.6
- **Na tela:** **Tab. 10, os dois blocos, com as colunas externas reduzidas a uma por eixo.**

  **Next-category (macro-F1)**

  | **Dataset** | **Regions** | **POI-RGNN** | **Dedicated** | **Joint (ours)** |
  |---|---:|---:|---:|---:|
  | AL | 1,109 | 23.80 | 30.77 ±0.07 | 30.59 ±0.07 |
  | AZ | 1,547 | 27.64 | 34.57 ±0.04 | 34.57 ±0.06 |
  | Istanbul | 520 | 30.12 | 35.34 ±0.01 | 35.42 ±0.06 |
  | FL | 4,703 | 34.49 | 37.35 ±0.02 | **37.55** ±0.07 ↑ |
  | CA | 8,501 | 31.78 | 35.63 ±0.01 | 35.63 ±0.02 |
  | TX | 6,553 | 33.03 | 36.33 ±0.01 | 36.19 ±0.04 |

  **Next-region (Acc@10)**

  | **Dataset** | **Regions** | **HMT-GRN** | **Dedicated** | **Joint (ours)** |
  |---|---:|---:|---:|---:|
  | AL | 1,109 | 57.05 | 70.12 ±0.10 | 69.24 ±0.16 ≈ |
  | AZ | 1,547 | 43.70 | 59.48 ±0.07 | 59.04 ±0.22 ≈ |
  | Istanbul | 520 | 60.4 | 75.16 ±0.01 | 75.08 ±0.05 ≈ |
  | FL | 4,703 | 63.74 | 76.69 ±0.01 | 76.54 ±0.01 ≈ |
  | CA | 8,501 | 49.61 | 63.48 ±0.03 | **64.54** ±0.04 ↑ |
  | TX | 6,553 | 53.85 | 64.94 ±0.01 | **66.15** ±0.07 ↑ |

  - Legenda dos marcadores, mantida da tabela entregue: **↑** = improvement over the dedicated model that survives Holm correction within its task family. **≈** = stays within the two-point margin registered before any result was read (TOST). *Category results carry no equivalence mark: the margin was registered for the region axis only.*
  - Convenção desta tabela: **four seeds × five folds; ± is the sd across seeds.** Different from Table 9.
  - `alertblock`, antes da leitura: **the dedicated category model was searched at every dataset and the joint model was not searched at Texas and California**, which carry a transferred configuration. Where the dedicated search is the wider of the two, the residual favors the dedicated model.
- **Fala (PT):** Segundo resultado, e é o que decide a tese. Duas tabelas, uma por tarefa: à esquerda a categoria, à direita a região, com três sistemas externos. Primeiro a comparação limpa. Em categoria, o conjunto fica pelo menos três vírgula zero seis pontos acima do POI-RGNN nos seis conjuntos, e o POI-RGNN é nativo da tarefa. Em região, fica acima do melhor externo de cada conjunto, também nos seis. Agora a ressalva de protocolo, porque os três não chegam em pé de igualdade. Só o HMT-GRN roda nos nossos dados, nas nossas partições e nas nossas inicializações. O STAN roda nas nossas partições mas constrói as próprias representações e as próprias sequências, e em dois conjuntos com partições incompletas. O ReHDM roda sob o protocolo publicado dele. E agora a coisa mais interessante do capítulo, e ela é contra eles, não a meu favor: o piso de Markov de primeira ordem, uma tabela de transição sem aprendizado nenhum, fica acima desses três sistemas na maioria dos conjuntos — acima do HMT-GRN nos seis. É por isso que eu trato o piso, e não os externos, como a referência que a próxima região tem de exceder. O conjunto excede o piso por quatro vírgula um a dez pontos. Os números vêm de quatro sementes por cinco partições; a dispersão e os intervalos estão no próximo slide, que é onde o veredito é decidido.
- **Proveniência:** todas as células e a legenda de marcadores → `tables/mobiwac/results.tex` (Tab. 10, copiadas célula a célula); convenção de quatro sementes × cinco partições e desvio entre sementes → nota de rodapé da mesma tabela; ≥ 3.06 macro-F1 sobre o método externo mais forte → `chapters/5_mobiwac/06_results.tex:110-111`; ≥ 3.55 Acc@10 sobre a referência de região mais forte → `chapters/5_mobiwac/08_conclusion.tex:30-33`; piso de classe majoritária 5.7 a 7.3 → `:122-123`; o piso de Markov acima dos três sistemas externos e "We treat the floor, not the external systems, as the reference the region task has to clear" → `:269-284`; ressalvas de protocolo de STAN e ReHDM → `chapters/5_mobiwac/05_setup.tex:182`; cobertura de busca → `:39-63` e `chapters/5_mobiwac/07_discussion.tex:61-69`. ⚠ **A frase da escada, acrescentada 2026-08-24 por decisão do autor:** *"the joint model stands at least 3.06 points above the strongest external baseline at every dataset"* e *"the smallest of the three effects at work here, which is the sense in which one model can replace two on this task"* → `chapters/5_mobiwac/06_results.tex:110-113`. Ela é **RETOMA**, não INTRODUZ: os métodos externos já entram nesta mesma tela. Análise completa: [`wrapup/open_points/BASELINES_EXTERNOS.md`](../../wrapup/open_points/BASELINES_EXTERNOS.md). ⚠ **Custo: ~36 s** numa seção que já está 4,5 min acima do orçamento — reavaliar depois do ensaio.
- **Nunca dizer:** "empata", "matches", "ties", "em todos os conjuntos supera". "Beats" ou "wins" para os métodos externos: o verbo é **excede**. Nunca um número do Cap. 3 nesta tela. Nunca "Pareto".

### S47 · The verdict, dataset by dataset
- **Slide impresso:** **41**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.5 (c)   **Tempo:** 121 s  *(medido)*
- **LEDGER:** INTRODUZ o veredito com intervalos (Fig. 7 e as dez diferenças)
- **Na tela:** uma **tabela de seis linhas** (um conjunto por linha) com dois grupos de colunas — *Next region* (Acc@10) e *Next category* (macro-F1) — cada um com Δ e o intervalo de 95 %. Um marcador ▲ na cor primária assinala as três células em que o conjunto **supera**. Ordem das linhas: Texas, California, Florida, Istanbul, Arizona, Alabama (Δ de região, decrescente). Abaixo da tabela, três parágrafos curtos, e **nada mais**:
  - ▲ **Outperforms the dedicated model** — Texas (p = 0.00013, 20 of 20 folds), California (p < 10⁻⁴, 20 of 20), Florida (p = 0.011, 19 of 20); Holm-corrected. **The two region gains are secondary results, outside the registered plan.**
  - **Region.** The other four stay within the **two-point margin, registered before any result was read** — and **all four are deficits, not ties**: every one of the four intervals lies entirely below zero.
  - **Category.** The other five are **unresolved**. The widest interval reaches **0.34** from zero, at Alabama — bounding all six within half a point; read off the intervals, not established by a further test.

  > **Reformulado 2026-08-24 (varredura visual).** A forma anterior — Fig. 7 em cima e duas listas em prosa corrida — punha ~200 palavras de frase justificada na tela e espremia a figura a um quinto da largura, ilegível. Os doze pares número-e-intervalo passaram para a tabela, que é o recipiente natural deles. **Nenhum número saiu e nenhuma cláusula de lei saiu.** Três itens deixaram a tela e continuam no deck:
  > - o detalhe *post-hoc* / Istambul a dois milésimos → já vivia inteiro no **B1-1**, que é a pergunta que ele responde, e continua na fala deste slide;
  > - *under the final design and the strictest protocol of the three studies* → já está em **S3**, no início;
  > - o agrupamento Texas-Califórnia por número de regiões como observação e não lei → já está em **S50**.
  >
  > **Fig. 7 não foi descartada:** virou o slide de reserva **B1-6**, em tamanho legível, ligada a partir da família B1.
- **Fala (PT):** "E este é o veredito, com o intervalo de cada diferença. Na **próxima região**, o modelo conjunto **supera** o dedicado no Texas, mais 1,21, e na Califórnia, mais 1,06; nos dois, as vinte partições favorecem o conjunto, e os p corrigidos são 0,00013 e menos de dez elevado a menos quatro. Nos outros quatro conjuntos ele **permanece dentro da margem de dois pontos**, registrada antes de qualquer resultado ser lido. E eu enuncio os quatro, porque citar três e omitir Istambul seria justamente o erro que eu quero evitar: Alabama menos 0,87; Arizona menos 0,44; Flórida menos 0,16; Istambul menos 0,08. Os quatro são **déficits, não empates**, e os quatro intervalos ficam inteiramente abaixo de zero. A direção é declarada, não arredondada. Na **próxima categoria**, ele **supera na Flórida**, mais 0,19, com p corrigido de 0,011 e dezenove das vinte partições a favor. As outras cinco são **não resolvidas**, e elas não apontam para o mesmo lado: Istambul, mais 0,08, exclui zero a favor do conjunto; Texas, menos 0,13, e Alabama, menos 0,19, excluem zero a favor do dedicado; Arizona e Califórnia ficam sobre o zero. Nenhuma das cinco sobrevive a Holm. O que se pode dizer sobre magnitude vem dos intervalos: o mais largo alcança 0,34 de ponto a partir de zero, no Alabama, e isso limita as seis diferenças de categoria a **meio ponto de zero de uma vez só**. Duas últimas coisas, ditas por mim antes de serem pedidas. Os dois ganhos de região são **resultados secundários, fora do plano registrado**. E Istambul, o único conjunto fora dos Estados Unidos, fica a menos de um décimo de ponto nos dois eixos, que é o teste de validade externa deste capítulo."
- **Proveniência:** as cinco diferenças de categoria com intervalos, o p corrigido de 0.011, 19 de 20 partições e o limite de 0.34 no Alabama → `chapters/5_mobiwac/06_results.tex:207-220`; as seis de região com intervalos, os p corrigidos, "every one of the four intervals lies entirely below zero" e "none of them is a tie" → `:222-233`; o agrupamento por número de regiões como observação e não lei → `:189-205`; ganhos de região como resultados secundários fora do plano → `chapters/5_mobiwac/05_setup.tex:113`; Istambul nos dois eixos → `chapters/5_mobiwac/06_results.tex:345-353`; Fig. 7 = `figures/mobiwac/fig4_deltas.pdf`.
- **Nunca dizer:** "empata", "matches", "ties", "em todos". Aplicar a margem de dois pontos ao eixo de categoria, ou meio ponto ao eixo de região. Chamar as quatro diferenças dentro da margem de empates. Dizer que uma diferença "exclui zero" sem dizer para que lado. Creditar Texas e Califórnia a transferência entre tarefas. **E não ler os rótulos da Fig. 7 como se fossem os valores:** a figura imprime uma casa decimal na região (−0,1 e −0,9) e a lista embaixo imprime duas; Istambul é −0,08, não "menos zero vírgula um".

### S48 · Limitations and trade-offs
- **Slide impresso:** **42**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.6   **Tempo:** 119 s  *(medido)*
- **LEDGER:** INTRODUZ o custo medido do modelo conjunto e os quatro limites do Cap. 5 · RETOMA a ressalva operacional × computacional de 1.3
- **Na tela:** duas metades, em fragmentos. *(v2 · 272 → 72 palavras. Zero frases completas; a íntegra de cada limite está na fala e cada um tem slide de reserva próprio.)*
  - **THE TRADE**
    - Larger: **4.2 M** parameters at Alabama against **1.1 M** for the two dedicated combined;
    - **Operational, not arithmetic** — one artifact, one forward pass, both answers;
    - Largest region deficit inside the margin: **0.87 Acc@10** at Alabama.
  - **FOUR LIMITS, OFFERED BEFORE THEY ARE ASKED**
    1. Representation trained once over all places;
    2. Epoch selection reads the fold it scores — **absolute scores are optimistic**;
    3. **No mobility-aware service** is built or evaluated;
    4. Each visit draws only on the visits that precede it.
- **v2 · o que saiu da tela, e onde ficou:** *"5.2 against 2.0 at California"* e *"a forward pass costs more compute"* → fala do próprio S48. Limite 1 — **0.33 Acc@10**, **0.29 macro-F1**, cobertura de **67 a 87 por cento** → fala do S48 **e tela do SB7** (`B2-1`, que os carrega com mais detalhe que esta tela jamais teve). Limite 2 — *"the comparison is affected far less: same rule, same folds, and the dedicated category model receives the wider search. It does not follow that the bias cancels exactly"* → fala do S48 **e SB9** (`B2-3`); ⚠ **a consequência auto-incriminatória (*"absolute scores are optimistic"*) FICA na tela** de propósito: mandá-la para a fala pareceria escondê-la, e a R6 pede que a ressalva acompanhe o resultado. Limite 3 — *"background motivation; the claims are the prediction results themselves"* → fala do S48. Limite 4 — *"no information passes backward from a later visit, in training or at readout"* → fala do S48 **e SB10** (`B2-4`). Nenhuma cláusula saiu sem destino conferido.
- **Fala (PT):** "A troca, medida, e depois quatro limites que eu ofereço antes de alguém pedir. A troca primeiro: o modelo conjunto é **maior**. O capítulo reporta cerca de 4,2 milhões no Alabama contra 1,85 milhão dos dois dedicados somados, e 5,2 contra 2,8 na Califórnia. São 2,3 vezes e 1,8 vezes; uma passagem custa mais computação do que rodar os dois modelos pequenos. O que o modelo único entrega é **operacional, não aritmético**: um artefato para treinar, versionar e implantar, e uma passagem cujas entradas produzem as duas respostas de uma vez. E os quatro resultados de região dentro da margem são déficits pequenos, o maior deles 0,87 no Alabama: é uma troca medida, não uma substituição de graça. Os quatro limites. Primeiro: a representação é treinada uma vez sobre todos os lugares; uma reconstrução por partição, só com usuários de treino, mudou os resultados em no máximo 0,33 de acurácia em dez e 0,29 de macro-F1, em três conjuntos e numa semente, e a metade de categoria dessa verificação cobre de 67 a 87 por cento dos dados de validação. Segundo: a seleção de época consulta a mesma partição em que a nota é depois lida, então **todo escore absoluto que eu reportei é otimista**; a comparação entre conjunto e dedicado é bem menos afetada, porque a regra é a mesma para os dois nas mesmas partições e porque o dedicado de categoria recebe a busca mais ampla, mas daí não segue que o viés se cancele exatamente. Terceiro: eu não construo nem avalio serviço nenhum. Quarto: cada nó de visita se apoia só nas visitas que o precedem, e o grafo não passa informação de uma visita posterior para uma anterior, nem no treino nem na leitura."
- **Proveniência:** 4.2 e 1.1 milhões, 5.2 e 2.0, "operational rather than arithmetic" → `chapters/5_mobiwac/04_method.tex:51-57`; o déficit de 0.87 no Alabama e "the trade is a measured one and not a free substitution" → `chapters/5_mobiwac/07_discussion.tex:27-36`; os quatro limites, na ordem do capítulo, com 0.33 Acc@10, 0.29 macro-F1 e "It does not follow that the bias cancels exactly" → `:128-198`; cobertura de 67 a 87 por cento → `chapters/5_mobiwac/05_setup.tex:75`.
- **Nunca dizer:** repetir a razão de parâmetros como se tivesse sido re-medida, e nunca citar uma recontagem. Se a pergunta vier, a resposta é que a razão de parâmetros não foi re-medida. Nunca citar as duas porcentagens de parâmetros impressas no Apêndice G do suplemento: elas estão erradas, e o assunto é do slide B3.

### S49 · Three studies, three layers
- **Slide impresso:** **43**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 6.0 (fronteira Ato III → Ato IV)   **Tempo:** 30 s
- **LEDGER:** INTRODUZ a leitura conjunta dos três estudos lado a lado | RETOMA a linhagem de 2.1 e as três camadas de 5.1
- **v2 · a colisão de ledger, fechada 2026-08-24 (decisão do autor):** o deck construído tinha **duas** cópias deste slide — uma fechando a §5 (`main.tex:1770`) e outra abrindo a §6. A da **§5 foi removida**. Não foi escolha de gosto: (a) o `PLANO_FLUXO_DEFESA.md` orça a escada na **Seção 6** e este próprio bloco diz *Seção/subseção: 6.0*, então a cópia da §5 não tinha mandato; (b) a cópia da §5 **parafraseava uma cláusula de lei** — dizia *"margin registered **in advance**"* onde a forma canônica, que aparece **6×** no deck e na cópia sobrevivente, é *"the margin registered **before any result was read**"*; (c) as duas renderizavam bem, sem desempate por qualidade. **Remover foi conserto, não edição.** Devolve ~30 s ao orçamento, que estavam sendo contados duas vezes. Achado por varredura independente de dois agentes; verificado na fonte antes de agir.
- **Na tela:** grade 3 × 4, **zero números**. Asset a criar (não existe no repositório; conteúdo exato abaixo). As duas células `unchanged, by design` da linha ST-MTLNet recebem marca visual, porque é o congelamento que produz o diagnóstico.

  | | **Representation** | **Sharing topology** | **Protocol** | **What moved** |
  |---|---|---|---|---|
  | **MTLnet** (Ch. 3) | one vector per place (DGI over a Delaunay graph) | hard parameter sharing, FiLM conditioning the shared layers | sample-stratified folds, one seed, each task read at its own best epoch | nothing was separated: a null result, and three named suspects |
  | **ST-MTLNet** (Ch. 4) | decomposed spatial, temporal, and categorical encoders | **unchanged, by design** | **unchanged, by design** | with the architecture fixed, the input moved the result: the input representation is the bottleneck |
  | **Check2HGI** (Ch. 5) | one vector per visit, a graph with four levels (check-in, place, region, city) | cross-attention between per-task streams, private spatial path for the region task | user-disjoint folds, four seeds, joint-best, the margin registered before any result was read | one joint model replaces two dedicated single-task models on both tasks |

- **Fala (PT):** "Uma tela em que a coletânea inteira cabe. Três linhas, os três estudos. Três colunas, as três camadas. Mais uma quarta coluna: o que moveu. O Capítulo 3 não separou nada, e é isso que ele entrega, um nulo com três suspeitos. O Capítulo 4 manteve a arquitetura fixa de propósito, e é esse congelamento que faz a troca de entrada valer como diagnóstico. O Capítulo 5 mexeu nas três camadas. Um veredito condicional, medido sob o protocolo mais estrito dos três. O que os três estudos, juntos, estabelecem, e o que não estabelecem?"
- **Proveniência:** linha MTLnet, `src/chapters/3_cbic/method.tex:23` (grafo de Delaunay), `:75` e `:88` (compartilhamento rígido e FiLM) e `src/chapters/3_cbic/results.tex:36` (partições por amostra, semente única, melhor época por tarefa); linha ST-MTLNet, `src/chapters/4_courb/methodology.tex:90` (*"whose internal architecture is kept unchanged in this chapter"*, e a substituição da representação monolítica pela concatenação dos três codificadores); linha Check2HGI, `src/chapters/5_mobiwac/04_method.tex:18` (o grafo de quatro níveis) e `:27-33` (atenção cruzada entre os fluxos por tarefa, e o caminho espacial privado da região), com o protocolo de `src/chapters/6_conclusion.tex:91` (validação cruzada disjunta por usuário, quatro sementes); coluna *What moved*, `src/chapters/6_conclusion.tex:35` (*"one joint model replaces two dedicated single-task models on both tasks"*) e `:174` (os três suspeitos), `:178` (o gargalo). A transição falada é a de PLANO §2, saída do Ato III.
- **Nunca dizer:** nenhum número nesta tela, em nenhuma célula. Nenhum "fomos de X para Y" atravessando protocolos (§8 regra 7). Nunca "supera" nesta tela: a licença é por célula de resultado, e aqui não há resultado.

### S50 · The conditional answer
- **Slide impresso:** **44**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 6.1   **Tempo:** 55 s
- **LEDGER:** RETOMA o veredito de 5.5, a pergunta de 1.3 e o protocolo disjunto por usuário de 5.4 ("o protocolo mais estrito dos três")
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - Bloco **The answer**:
    - Multitask learning helps next-category and next-region prediction **under the final design and evaluation protocol developed in this dissertation.**;
  - Bloco **What it does not authorize**:
    - Not that multitask learning always helps — task relatedness and joint training were **not sufficient by themselves**;
  - **Established by controlled ablation** — the input representation is one condition; **suggested, not isolated** — the architecture, and the scale of the dataset; **problem scale is a possible condition, not an established cause**. *Identifying these conditions is the main finding of this dissertation.*;
- **Fala (PT):** "A resposta consolidada, e ela é condicional de propósito. O aprendizado multitarefa ajuda a previsão da próxima categoria e da próxima região sob o desenho final e o protocolo de avaliação desenvolvidos nesta dissertação. O que isso não autoriza é dizer que o multitarefa sempre ajuda: ao longo dos três estudos, relação entre tarefas e treino conjunto não bastaram por si sós. Uma condição está estabelecida por comparação controlada, e é a representação de entrada. Duas outras a evidência sugere sem isolar: a arquitetura, e a escala do conjunto de dados. Sobre escala eu sou explícito. Ela continua sendo condição possível, não causa estabelecida, por duas razões que estão no próprio texto: a ordenação não se mantém dentro do par Texas e Califórnia, e estados com mais regiões também tendem a ter mais check-ins. Identificar essas condições é o achado principal desta dissertação."
- **Proveniência:** `src/chapters/6_conclusion.tex:165-169` (a pergunta, a resposta sob a configuração final, e *"Identifying these conditions is the main finding"*), `:190-195` (a insuficiência da relação entre tarefas; a representação como condição estabelecida; arquitetura e escala não isoladas), `:197-200` (a conclusão condicional, palavra por palavra), `:144-149` (as duas ressalvas de escala e *"Problem scale remains a possible condition, not an established cause"*).
- **Nunca dizer:** "MTL funciona" sem condição. Re-caminhar a cadeia dos três estudos, que acabou de estar na tela em S49. Creditar os ganhos de região a transferência entre tarefas. Nenhum número novo.

### S51 · Contributions
- **Slide impresso:** **45**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 6.2   **Tempo:** 45 s
- **LEDGER:** RETOMA a contribuição de 1.5 (§8 regra 13: segunda das duas aparições, redação idêntica)
- **Na tela:** dois blocos. **Reproduz o `[BLOCO-CONTRIBUIÇÃO]` do cabeçalho palavra por palavra.** *(v2 · **quarta** reescrita, 2026-08-24 — ver a nota abaixo, que é a mais importante das quatro.)*
  - Bloco **Practical — what it delivers**:
    - **one model, one forward pass, two predictions** — one artifact to train, version and deploy, **in place of two**;
    - **operational, not computational**: the joint model is the larger artifact;
    - **Check2HGI is the reusable part** — one vector per visit, independent of the prediction heads on top.
  - Bloco **Scientific — what it establishes**, uma frase só:
    - The **input representation** and its **sharing topology** determine **whether** multitask learning helps these POI prediction tasks.
- **v2 · a quarta reescrita, e o defeito que ela conserta:** ⚠ **a metade científica anterior era, inteira, tela de OUTROS slides.** Medido linha a linha: *"the novelty is the combination: per-visit context inside a hierarchical graph-infomax representation"* é **verbatim a tela do S35**; *"helps under the final design and evaluation protocol"* é o bloco *The answer* do **S50**; *"the input representation is one condition; architecture and scale suggested, not isolated"* é o **terceiro item do S50**. E o **S50 é o slide imediatamente anterior a este no fechamento** — a banca via um slide e, um clique depois, dois terços dele repetidos. **Violação tripla da R4** (um elemento carrega INTRODUZ em exatamente um slide), num slide cujo ledger eu não conferi enquanto conferia o dos outros 34.
  **Dois defeitos caíram junto.** (a) **Referência para a frente:** `graph-infomax` estava na tela do S7, mas a ideia infomax é **INTRODUZ no S8** — um slide *depois*. (b) **Tela e fala afirmavam coisas diferentes:** a fala já dizia *"a representação de entrada e a topologia de compartilhamento decidem se o multitarefa ajuda"*, que é o grupo **Theoretical** entregue, enquanto a tela dizia a taxonomia do §6.2. Um arguidor atento ouvia uma tese e lia outra. **A nova tela alinha as duas** — e a fala não muda, então o relógio não se move.
  **A metade científica agora é a primeira frase do grupo Theoretical** (`src/chapters/1_introduction.tex:422-426`), que é o recorte da própria seção de Contribuições e **não está em tela nenhuma do deck**. Ela faz o que o autor pediu — o achado amplo primeiro (**`whether`** é a condicionalidade, numa palavra) e a representação nomeada dentro dele. ⚠ **A taxonomia graduada das três condições fica no S50**, que a possui: *representação* estabelecida por comparação controlada, *arquitetura* e *escala* sugeridas e não isoladas. ⚠ **E note a granularidade:** o Theoretical afirma que representação **e topologia** *determinam*; o §6.2 diz que só a representação foi *isolada*. Não se contradizem — são recortes diferentes da mesma evidência —, e a resposta de arguição é essa.
  **A objeção do autor sobre a redundância prática:** *"one model, one forward pass, two predictions"* e *"one artifact"* diziam a mesma ideia. Fundidos num marcador só, com o travessão marcando que são a mesma coisa vista da inferência e do ciclo de vida. ⚠ **A ressalva que a R13 obriga ficou em linha própria** — enterrá-la dentro da fusão a enfraquecia. Densidade: **92 → ~66 palavras**.
  **Revisão crítica por agente Fable**, a pedido do autor, sobre o texto entregue e o deck: foi ela que achou a duplicação tripla, que eu não tinha visto.
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "A contribuição, em duas metades. A prática: um modelo, uma passagem, duas predições --- um artefato para treinar, versionar e implantar, no lugar de dois. O ganho é operacional, não computacional: o conjunto é o artefato maior. Mais o Check2HGI publicado, que é a parte reutilizável, e o protocolo de avaliação, liberado com o código. A científica: acima de todo sistema externo que eu rodei, nas duas tarefas; resultados de referência para a próxima região, uma tarefa que não tinha protocolo fixado; e três condições sobre quando o multitarefa ajuda --- a representação de entrada, estabelecida por comparação controlada, e a arquitetura e a escala, sugeridas e não isoladas.""
- ⚠ **O `[BLOCO-CONTRIBUIÇÃO]` deixou de ter duas cópias.** A nota antiga dizia *"redação IDÊNTICA à de S7, §8 regra 13, não editar aqui"*. A **`AUT-2` revogou a §8.13 e removeu o S6/S7**: a contribuição aparece **uma vez só**, e é esta. **Este bloco agora é a única cópia — edite aqui.**
- **Proveniência:** idêntica à de S7. Metade prática, `src/chapters/6_conclusion.tex:468-470` (*"a single model that predicts two properties of the next visit in one forward pass"*) e `src/chapters/5_mobiwac/04_method.tex:51-57` (*"larger than either dedicated model"*, *"operational rather than arithmetic: one artifact to train, version, and deploy"*). Metade científica, `src/chapters/1_introduction.tex:425-431` (Theoretical: a representação de entrada e a topologia de compartilhamento decidem; o nulo não conflita com o positivo).
- **Nunca dizer:** redação diferente da de S7, mesmo que melhor. Nenhum número novo. Nunca a razão de parâmetros como verificada: o slide diz "maior", que é o que a página imprime, e nada além.

### S52 · Limitations
- **Slide impresso:** **44**  ·  *(reestruturado 28/08; era "Five limitations, five next steps (1 of 2)", impresso 46)*
- **Seção/subseção:** 6.3 (a)   **Tempo:** 105 s  *(estimado — as falas dos dois slides antigos fundiram-se aqui)*
- **LEDGER:** INTRODUZ as SEIS limitações
- **Na tela:** tabela de duas colunas, seis linhas, uma por limitação, com respiro entre os itens. *(O volume abre a seção com "Six limitations bound the scope"; o deck principal mostrava cinco — a sexta, o confundimento do par de tarefas, só existia na Série B.)*

  | | |
  |---|---|
  | **1 · Data vintage** | Gowalla 2009–2011 · Istanbul 2012–2018 — *a field-wide constraint* |
  | **2 · Taxonomy coarseness** | seven top-level classes |
  | **3 · Transductive representation** | no unseen places or users without retraining |
  | **4 · No next-place task** | conclusions cover next category and next region only |
  | **5 · Geographic coverage** | outside the United States, one city |
  | **6 · The task-pair confound** | the pair changed together with the representation and the topology; **Chapter 4 is the fixed-pair control** |

- **28/08 · o que mudou:** o slide passou a carregar SÓ limitações, e as seis. Os trabalhos futuros migraram para o S53. O botão `\hyperlink{u6}` da linha 6 **saiu a pedido do autor** — a meia-frase *"Chapter 4 is the fixed-pair control"* fica, porque é ela que impede a linha de ler como rendição.
- **Fala (PT):** "As limitações, cada uma amarrada ao passo que ela pede. Eu prefiro dizê-las antes de serem perguntadas. Não são desculpas: são experimentos que alguém pode rodar. Primeira, a idade dos dados. Os cinco estados vão de janeiro de 2009 a agosto de 2011, e Istambul tem check-ins em dois blocos, 2012 a 2013 e 2017 a 2018, com cerca de sete em cada dez no bloco mais antigo. E vale dizer de quem é a limitação: a antiguidade dos dados não é só deste trabalho. Nenhum conjunto público de check-ins com trajetória de usuário passa de 2018 --- nem o Massive-STEPS, de 2025, que foi publicado para resolver exatamente isso. Segunda, a taxonomia é grossa. Sete classes de topo, e uma divisão mais fina pode mudar o efeito do treino conjunto. Terceira, e esta é a que eu mais gostaria de ver feita: a representação é transdutiva. Treinada sobre o grafo de check-ins de cada conjunto, ela não representa lugar nem usuário novo sem retreinar. O passo é uma variante indutiva, que sustentaria uso numa cidade que cresce. E, na mesma representação, dois testes controlados: variar o acoplamento com a tabela de vetores de lugar pré-treinada, e uma formulação em hipergrafo, em que uma aresta junta as várias visitas de uma sessão. ele virou "Future work". Palavras inalteradas: so mudaram de frame, porque o slide passou a carregar os seis limites. A do limite 6 e a fala do Future work ficam DEVIDAS ao gate. Quarta: eu não predigo o próximo lugar exato, então as conclusões valem para próxima categoria e próxima região. Quinta: fora dos Estados Unidos, a evidência se apoia numa cidade só. Mais cidades ampliam a base."
- **Proveniência:** `src/chapters/6_conclusion.tex:204` (as seis), `:239-246` (safra), `:314-315` (taxonomia), `:316-321` (transdutividade), `:339-340` (próximo lugar), `:341-342` (cobertura), `:343-361` (par de tarefas).
- **Nunca dizer:** que o confundimento de par de tarefas foi removido; ele é **limitado** pelo controle de par fixo. `ablation` — o termo não está no `GLOSSARY`; a superfície é *"teste controlado"*.

### S53 · Future work
- **Slide impresso:** **45**  ·  *(reestruturado 28/08; era "Five limitations, five next steps (2 of 2)", impresso 47)*
- **Seção/subseção:** 6.3 (b)   **Tempo:** 78 s  *(estimado)*
- **LEDGER:** INTRODUZ os trabalhos futuros, agrupados por eixo
- **Na tela:** três `exampleblock` em `columns`, um por eixo, com três etiquetas cada. *(Os três títulos são a espinha do próprio deck: o slide de contribuições gradua os três e o `Closing` responde "what does the answer depend on?" com exatamente estes.)*

  | **Input representation** | **Sharing topology** | **Problem scale** |
  |---|---|---|
  | **An inductive Check2HGI** — new places and users, no retraining | **The exact next place** — a third head, same representation | **Region count vs. data volume** — the controlled experiment |
  | a hypergraph over sessions | deeper sharing — one trunk, per-task heads | newer traces · finer taxonomies · new cities |
  | attention-based graph encoders | one training stage — representation and model together | the geographic size of a miss |

  Fecho: *Eleven items in the volume, each tied to a named limitation.*

- **28/08 · o que mudou:** de 3 itens em corpo grande para 9 etiquetas em três eixos, a pedido do autor. **Não revoga a `AUT-24`:** a tela ganha etiquetas, não frases, e a fala vai de ~150 para ~188 palavras.
- 🛑 **O ÚLTIMO PARÁGRAFO DA FALA É O ÚLTIMO A SER CORTADO POR TEMPO.** Ele carrega os três que **só existem na fala** — a ablação da âncora da tabela de lugares, o alvo estático e o Check2HGI noutras arquiteturas. Se cair, eles desaparecem da defesa inteira.
- **Fala (PT):** "Três frentes, e são as mesmas três de que a resposta depende: a representação, a topologia e a escala. Duas delas o próprio trabalho classifica como apenas sugeridas --- é aí que está o espaço. Na representação, a que eu mais gostaria de ver feita: torná-la indutiva. Hoje ela não representa lugar nem usuário novo sem retreinar, e uma cidade que cresce precisa disso. Na topologia, o próximo lugar exato: a tarefa mais visível da literatura está a uma cabeça de distância da representação que já existe. E treinar os dois estágios num só --- hoje a representação é aprendida sem rótulo e depois congelada; unificar é descobrir se ela continua agnóstica quando os gradientes das tarefas chegam nela. Na escala, a que eu devo: Texas e Califórnia são os dois que ganham, os dois com mais regiões, e os dois com mais dados. Separar as duas explicações exige um experimento controlado. E há mais três que não estão na tela: uma ablação da âncora da tabela de lugares, um alvo estático que a representação não carregue como entrada, e o Check2HGI dentro de outras arquiteturas de mobilidade."
- **Proveniência:** `src/chapters/6_conclusion.tex:126` (Check2HGI noutras arquiteturas), `:145-147` (contagem de regiões × volume), `:397-409` (indutiva, hipergrafo, place-table), `:439-443` (próximo lugar), `:448` (alvo estático); `5_mobiwac/07_discussion.tex:77` (o tamanho geográfico de um erro); `apx_f_cosine.tex:610` (*deeper sharing*).
- **Nunca dizer:** `GSM++` — o deck nunca introduziu a sigla e o §8.11 é fail-closed; a intenção entra como *attention-based graph encoders*.

### S54 · Closing
- **Slide impresso:** **48**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 6.4   **Tempo:** 50 s  *(medido)*
- **LEDGER:** RETOMA as aplicações de 1.1 e a restrição de modelo único de 1.3 | fecho
- **Na tela:** o takeaway na tela, o "obrigado" pela voz. **Sem lista de agradecimentos na tela.**
  - **One model predicts two properties of the next visit in one forward pass: what kind of place the user will visit, and in which part of the city.**
  - **The methodological contribution is the sequence of evidence:** a published negative result, the diagnosis that identified the input representation as the main bottleneck, and a solution designed from that diagnosis.
  - *The negative result was not an obstacle to the contribution. It was its first half.*
  - Rodapé, código: `github.com/VitorHugoOli/PoiMtlNet` (Ch. 3) · `github.com/VitorHugoOli/PoiMtlNet/tree/mobiwac` (Ch. 5) · `github.com/TarikSalles/Spatial_Embeddings` (Ch. 4).
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "Eu abri esta apresentação dizendo que antecipar o quê e o onde da próxima visita sustenta recomendação, navegação, planejamento de transporte e alocação de recursos por área. Fecho no mesmo lugar, um nível acima. O produto prático desta dissertação é um modelo único que prediz duas propriedades da próxima visita numa passagem: que tipo de lugar a pessoa vai visitar, e em que parte da cidade. E a contribuição metodológica é a sequência de evidência que levou até ele: um resultado negativo publicado, o diagnóstico que identificou a representação de entrada como o gargalo, e uma solução desenhada a partir desse diagnóstico. O resultado negativo não foi obstáculo à contribuição. Ele foi a primeira metade dela."
- **Proveniência:** as aplicações, `src/chapters/1_introduction.tex:42-44` (*"recommendation, navigation, transit planning, and the allocation of resources by area"*); as três frases do takeaway, `src/chapters/6_conclusion.tex:468-474`, copiadas; os URLs, `src/chapters/3_cbic/intro.tex:30`, `src/chapters/5_mobiwac/01_introduction.tex:27` e `src/chapters/4_courb/intro.tex:35`. Grafias: **Fabrício Silva**, **Germano Santos**, **Tarik Paiva** dos agradecimentos entregues (`src/content.tex:47-67`); **Ingred F. Almeida** de `src/references.bib:971` (autoria do CBIC 2025).
- **Nunca dizer:** nenhum número novo. Nenhum "MTL funciona" sem condição. Nunca ler a lista de agradecimentos da tela: ela não está na tela.
  > ⚠ **PENDÊNCIA ABERTA, só o autor fecha (PLANO §9, item 7).** A grafia completa de **Pedro Maia** não foi localizada em nenhum artigo, no texto entregue, nem em lugar nenhum do repositório (varredura desta sessão: `grep -rn "Pedro" articles/ docs/` devolve apenas os próprios documentos de planejamento da defesa, nenhuma fonte). O nome fica como o autor o ditou, e a grafia é dele para fechar.
  > ⚠ **DIVERGÊNCIA COM O DEPOSITADO, registrada e não decidida.** Os agradecimentos entregues (`src/content.tex:47-67`) nomeiam **Fabrício Silva**, **Germano Santos**, **a defesa de referência Santana**, **Gustavo Viegas** e **Tarik Paiva**; **Ingred F. Almeida** e **Pedro Maia** não constam. A lista falada acima é a que o autor ditou para o slide. Se ele quiser alinhar com o depositado, a inserção é de uma oração, entre o Germano e o Tarik: *"Ao a defesa de referência Santana, ao Gustavo Viegas e ao Tarik Paiva, pela amizade que ficou mais forte ao longo do mestrado."* O CBIC 2025 tem ainda um coautor que a lista não menciona, **Felipe T. Sousa**.

---

# Série B (trilha de reserva) — os 46 slides que vivem depois do "Obrigado", entre `\miniframesoff` e `\miniframeson`. Cobertura 1:1 com os códigos do ARGUICAO: os dois `[ABERTO]` (Q5, Q8) e os oito `U1`–`U8` têm slide próprio identificado pelo código; mais B0, as sete famílias B1–B7 e os cinco slides que o plano nomeia (B4-LEAK, B4-DGI, B-NOM, B-KARPATHY, B-MTLCHECK).

> **Onde esta parte entra no `SLIDES.md`.** Depois do slide "Obrigado" da trilha principal, entre
> `\miniframesoff` e `\miniframeson` (plano §6 e §11.1). Os slides desta série **não entram no
> orçamento de 48 min** e **não registram ponto na barra de navegação**. O `\insertframenumber`
> congela sob `\miniframesoff`, então **o rótulo `B-n` vai no conteúdo de cada slide**, nunca no
> rodapé. Numeração interna aqui: `SB1 … SB46`, só para referência de redação. No cabeçalho de cada bloco
> o formato é `SB<n> · <código B> · <a pergunta>`; **na tela o título é só a pergunta**, e o código
> `B-n` fica no canto do conteúdo, como a primeira linha de **Na tela**.
>
> **Contrato herdado do plano §6, aplicado a todos os 46:** uma pergunta = um slide · o título é a
> pergunta, em português, como a banca a faria · rodapé de proveniência · números copiados de célula
> impressa ou do `ladder_recompute.json`, nunca re-derivados · onde a resposta honesta é "não foi
> medido", o limite é a manchete · carimbo de convenção métrica em toda arte reproduzida dos Caps. 3/4.

---

### S55 · Obrigado
- **Slide impresso:** **49**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 6.5   **Tempo:** 30 s
- **LEDGER:** INTRODUZ nada (fecho social)
- **Na tela:** duas colunas. **Orientador:** Prof. Fabrício Aguiar Silva. **Colegas de pesquisa:** Germano Santos · Tarik Paiva · Ingred Almeida · Pedro Augusto Maia Silva. **Instituição:** Universidade Federal de Viçosa, NESPeD-LAB — PPGCC. **Banca examinadora:** Prof. Fabrício Aguiar Silva · Prof. Clayson Celes · Prof. Alex Borges. Fecha em **Obrigado.**
- **Fala (PT):** *(v3, 26/08 — sincronizada com o deck, que é a versão vigente)* "E antes de encerrar, os agradecimentos. Ao meu orientador, o professor Fabrício Silva, pela liberdade de explorar as minhas ideias e pela confiança para levá-las adiante. Ao Germano Santos, que trabalhou ao meu lado em todos os artigos deste mestrado. Ao Tarik Paiva, à Ingred Almeida e ao Pedro Augusto, pela parceria de pesquisa ao longo do caminho. À Universidade Federal de Viçosa e aos professores que fizeram parte desta formação. À minha família, que sustentou tudo isto. E, por fim, aos senhores da banca: obrigado por lerem o trabalho e por estarem aqui. Fico à disposição para as perguntas."
- **Proveniência:** os nomes dos colegas confirmados pelo autor em 2026-08-24 (Pedro Augusto Maia Silva); a banca, do convite de defesa (`APRESENTACAO_DEFESA_GUIDE.md` §0); o orientador, da folha de rosto de `../src/banca.pdf`.
- **Nunca dizer:** nada de resultado aqui. É fecho social, e é o slide que fica na tela durante a arguição.


### SB1 · B0 · Se a pergunta for uma destas, o slide já existe
- **Seção/subseção:** Série B · índice (B0)   **Tempo:** sob demanda · ~15 s
- **LEDGER:** INTRODUZ o índice clicável da série de reserva | RETOMA nada
- **Na tela:**
  `B0 · Index`
  Seven families, one question per slide. Every entry is a `\hyperlink`.
  - **B1 · Verdict and statistics**: the four region cells and their direction · the five category cells and their sign · checkpoint convention · what `n` is · why a two-point margin
  - **B2 · Protocol and leakage**: training the representation on all places · the two studies' split · choosing the epoch on the fold that is reported · the forward-only edge · search coverage
  - **B3 · Post-submission**: capacity control on region · the concatenation control · the limit the paper carries · the supplement errata line · naming · capacity in the literature · the reimplementation · Appendix G counts
  - **B4 · Chapters 3 and 4**: label in the input, by mechanism · the contrastive objective · width · Travel by task · best-of-two · the Florida corpus · convergence cost
  - **B5 · Not measured**: U1 to U8, the limit as the headline
  - **B6 · Document and scope**: the Portuguese Resumo · appendix letters · the user column · the region Markov floor · **do we beat the literature?**
  - **B7 · How Check2HGI and the joint model work**: Appendix E of the main volume
- **Fala (PT):** "Posso ir direto ao slide da pergunta." E clico. Nada mais.
- **Proveniência:** rodapé: `série de reserva · fora da contagem principal`.
- **Nunca dizer:** nada aqui é falado como conteúdo; o B0 é navegação.

---

### SB2 · B1-1 · Um teste de não-inferioridade não é um empate. Nas quatro células de região dentro da margem, qual é a direção?
- **Seção/subseção:** Série B · família B1 (Q4)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA o ladder de veredito (5.5) | RETOMA a margem de dois pontos (5.4)
- **Na tela:**
  `B1-1`
  **All four are deficits. All four intervals lie entirely below zero.**
  | Dataset | Δ Acc@10 | 90% CI |
  |---|---:|---|
  | Alabama | −0.87 | −1.00 to −0.75 |
  | Arizona | −0.44 | −0.62 to −0.25 |
  | Florida | −0.16 | −0.19 to −0.13 |
  | Istanbul | −0.08 | −0.16 to −0.002 |
  - A reverse-direction test, post hoc over the same six comparisons and corrected across them, resolves three of the four. Istanbul is not resolved.
  - Each of the four clears the registered two-point margin. **None of them is a tie.**
- **Fala (PT):** "O senhor tem razão, e o texto diz isso na mesma página. As quatro são déficits, e os quatro intervalos ficam inteiramente abaixo de zero: Alabama menos zero vírgula oitenta e sete, Arizona menos zero vírgula quarenta e quatro, Flórida menos zero vírgula dezesseis, Istambul menos zero vírgula zero oito. Um teste na direção contrária, aplicado depois às mesmas seis comparações e corrigido entre elas, resolve três das quatro; o de Istambul não, o intervalo dele chega a dois milésimos de zero. As quatro vencem a margem com folga, que é o que a análise registrada pediu delas. Nenhuma é um empate, e eu não as chamo assim em lugar nenhum."
- **Proveniência:** Cap. 5, p. 82 (volume principal, `src/banca.pdf`); precisão cheia em `wrapup/evidence/ladder_recompute.json`, bloco `reg`.
- **Nunca dizer:** "empata", "matches", "ties", "semelhante", "a par". Nunca aplicar a margem de dois pontos ao eixo de categoria.

---

### SB3 · B1-2 · A margem de equivalência foi registrada só para região. O que o senhor usa em categoria?
- **Seção/subseção:** Série B · família B1 (Q2)   **Tempo:** sob demanda · ~50 s
- **LEDGER:** RETOMA o ladder de veredito (5.5) | RETOMA o plano de análise registrado (5.4)
- **Na tela:**
  `B1-2`
  **The plan assigned a superiority test to next category and a non-inferiority test to next region.** No equivalence margin was registered on the category axis.
  | Dataset | Δ macro-F1 | 90% CI | favors |
  |---|---:|---|---|
  | Istanbul | +0.08 | +0.01 to +0.15 | joint model |
  | Arizona | −0.00 | −0.04 to +0.03 | no direction |
  | California | −0.00 | −0.03 to +0.02 | no direction |
  | Texas | −0.13 | −0.19 to −0.08 | dedicated |
  | Alabama | −0.19 | −0.33 to −0.04 | dedicated |
  - Florida (+0.19) is the one cell that survives Holm.
  - The other five are **unresolved**, and the bound is read off the intervals: the widest reaches 0.34 from zero, at Alabama. **Equivalent to zero within half a point.**
- **Fala (PT):** "O plano registrou superioridade em categoria e não-inferioridade em região, e não registrou margem no eixo de categoria. Então uma diferença que falha o teste de superioridade é relatada como não resolvida, nunca como empate. O que eu posso dizer sobre a magnitude vem dos próprios intervalos: o mais largo chega a zero vírgula trinta e quatro de zero, em Alabama, o que limita as seis diferenças a meio ponto de zero de uma vez. E a direção viaja junto, porque as cinco não apontam para o mesmo lado: Istambul favorece o modelo conjunto, Texas e Alabama favorecem o dedicado, e Arizona e Califórnia ficam sobre o zero."
- **Proveniência:** Cap. 5, §5.5.3 (p. 76) e p. 82; legenda da Tabela 10 (p. 81), `src/tables/mobiwac/results.tex:26-30`; intervalos em `wrapup/evidence/ladder_recompute.json`, bloco `cat`.
- **Nunca dizer:** "equipara-se", "empata". Nunca citar meio ponto no eixo de região (lá o limite derivado é 1,372 pp).

---

### SB4 · B1-3 · O senhor escolheu a convenção de checkpoint mais restrita, que remove seis melhorias que poderia estar reclamando. Quem decide isso depois de ver os resultados?
- **Seção/subseção:** Série B · família B1 (Q1)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a convenção joint-best (5.4)
- **Na tela:**
  `B1-3`
  **Reported convention:** each dedicated model is read at its own task's best epoch; the joint model is read at the epoch its joint validation score selects, both tasks from the one saved model.
  **The alternative** (each task at its own best epoch) is more favorable to the joint model:
  - at most **0.23 macro-F1** and **0.93 Acc@10** at any one seed;
  - averaged over the four seeds, **+0.03 to +0.17** category and **+0.19 to +0.90** region;
  - enough to turn **four further category cells and two further region cells** into improvements that survive the same Holm correction.
  **That is exactly why it is not the one reported.** One checkpoint per fold is what a deployed system can serve.
- **Fala (PT):** "A convenção que eu reporto é a única que um sistema em produção consegue servir, porque se compromete com um checkpoint por dobra. A outra leitura favoreceria o modelo conjunto em até zero vírgula vinte e três de macro-F1 e zero vírgula noventa e três de Acc@10 na pior semente, e viraria mais seis células a meu favor sob a mesma correção. É por isso que eu não a uso. E ela está declarada no parágrafo imediatamente acima da tabela, não num apêndice."
- **Proveniência:** Cap. 5, p. 80-81; definição da convenção em `src/chapters/5_mobiwac/06_results.tex:141-142`; médias por semente em `articles/dissertacao/src_fix/REVISION_PLAN.md:93-94` (registro de revisão).
- **Nunca dizer:** apresentar os números da convenção alternativa como resultado.

---

### SB5 · B1-4 · O que é o n do seu teste? E por que o senhor trocou o Wilcoxon registrado pelo t pareado?
- **Seção/subseção:** Série B · família B1 (plano §7, item 4)   **Tempo:** sob demanda · ~50 s
- **LEDGER:** RETOMA n = 4, sementes, TOST, Holm (5.4)
- **Na tela:**
  `B1-4`
  - 4 seeds × 5 folds = **20 fitted models** per configuration. **Inferential unit: n = 4**, the per-seed means.
  - **Primary:** paired *t* on the four per-seed means, with the 90% CI, because folds inside a seed are not independent.
  - **Registered:** paired Wilcoxon signed-rank over the 20 matched fold differences. **Reported alongside, and it agrees.**
  - At the seed-level footing the exact one-sided Wilcoxon cannot fall below **0.0625**, whatever the effect size. That is why the *t* carries the verdict.
  - The departure is stated in the chapter and both tests ship in the code release.
- **Fala (PT):** "Vinte modelos ajustados, quatro médias por semente, e a unidade inferencial é quatro. O plano tinha registrado o Wilcoxon pareado sobre as diferenças por dobra, e ele continua reportado ao lado, e concorda. O primário é o t pareado sobre as quatro médias porque as cinco dobras dentro de uma semente compartilham a maior parte do treino e não são cinco observações independentes. E há uma razão aritmética: no nível de semente o Wilcoxon exato de uma cauda não desce abaixo de zero vírgula zero seiscentos e vinte e cinco, por maior que seja o efeito. Não é confissão de desvio, é desvio declarado, com os dois apoios e o mesmo veredito."
- **Proveniência:** Cap. 5, §5.5.3, p. 76 (`src/chapters/5_mobiwac/05_setup.tex:115,:117`); `GLOSSARY.md` §4, linhas `n = 20` / `n = 4`.
- **Nunca dizer:** "n = 20 repetições pareadas" (proibido pelo `GLOSSARY`).

---

### SB6 · B1-5 · Por que dois pontos? A margem não foi escolhida para caber no resultado?
- **Seção/subseção:** Série B · família B1 (Q2 / justificativa da margem)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a margem de dois pontos registrada (5.4)
- **Na tela:**
  `B1-5`
  - Fixed in the written analysis plan, **before any result was read**.
  - The reason is the use: a mobility-aware service acts on **which region will be busy**, not on a single rank position. A two-point change in Acc@10 is below the level at which that service would behave differently.
  - What the data say about the margin, stated in the chapter: the sd of the paired difference across the four user partitions runs **0.02 to 0.16**; the intervals at **Istanbul, Arizona and Florida** are narrow enough to support a margin as small as **one point**; **Alabama's is not**, and Alabama has the largest region difference.
  - **The chapter names its own weakest case.**
- **Fala (PT):** "Ela é uma escolha, e está declarada como escolha, fixada antes de qualquer resultado ser lido. A justificativa é de uso: o serviço age sobre qual região vai ficar movimentada, não sobre uma posição de ranking, e dois pontos de Acc@10 ficam abaixo do nível em que ele se comportaria diferente. E o texto vai além: diz que Istambul, Arizona e Flórida têm intervalos estreitos o bastante para sustentar uma margem de um ponto, e que o de Alabama não, que é justamente o conjunto com a maior diferença de região. Eu nomeio o meu pior caso na mesma página."
- **Proveniência:** Cap. 5, §5.5.3, p. 76-77 (`src/chapters/5_mobiwac/05_setup.tex:119`).
- **Nunca dizer:** que a margem foi derivada dos dados (ela é registrada; o limite **derivado** é outro objeto, e vale 1,372 pp simultâneo em região).

---

### SB6b · B1-6 · A Figura 7 do capítulo: as diferenças com os seus intervalos
- **Seção/subseção:** Série B · família B1 (a figura, sob demanda)   **Tempo:** sob demanda · ~20 s
- **LEDGER:** RETOMA o veredito de S47 na forma gráfica do capítulo
- **Na tela:**
  `B1-6`
  - `figures/mobiwac/fig4_deltas.pdf` em tamanho legível (largura 0.86, altura máx. 0.62 da área útil), e mais nada.
  - Rodapé: **a figura imprime uma casa decimal na região; a tabela do veredito imprime duas.**
- **Fala (PT):** "Esta é a Figura 7 do capítulo, as dez diferenças com os seus intervalos. Um aviso de leitura: ela imprime uma casa decimal na região e a tabela do veredito imprime duas. Istambul é menos zero vírgula zero oito, não menos zero vírgula um."
- **Proveniência:** `figures/mobiwac/fig4_deltas.pdf` — Fig. 7, Cap. 5 (volume principal).
- **Nunca dizer:** ler os rótulos da figura como se fossem os valores. **Istambul é −0,08, não "menos zero vírgula um".**
- **Criado 2026-08-24 (varredura visual):** a figura estava em S47 espremida a um quinto da largura e ilegível; saiu de lá e ganhou tela própria. Nada foi descartado.

---

### SB7 · B2-1 · A representação foi treinada uma vez sobre o conjunto inteiro, incluindo os usuários de validação. Isso não vaza?
- **Seção/subseção:** Série B · família B2 (Q12)   **Tempo:** sob demanda · ~50 s
- **LEDGER:** INTRODUZ a cobertura de 67 a 87 por cento do controle de reconstrução por dobra | RETOMA o split disjunto por usuário (5.4) e os quatro limites declarados (5.6)
- **Na tela:**
  `B2-1`
  - The representation objective **never reads the next-category or next-region targets**.
  - Control: a fresh representation built **per fold, from that fold's training users only**. Three datasets, one seed.
  - Differences: **−0.33 to +0.01 Acc@10** (region), **0.00 to +0.29 macro-F1** (category).
  - The declared limit of that control: for category, a graph built from training users only has no visit vectors for validation users, so the comparison used one vector per place and kept only windows whose input places occurred in training. **Those windows cover 67 to 87 percent of the validation data**, and the comparison does not cover per-visit information or places unseen in training.
  - Forecast evaluation is **user-disjoint**; representation learning is **transductive** with respect to the graph, and the chapter says so.
- **Fala (PT):** "O objetivo que treina a representação nunca vê os rótulos das duas tarefas. E eu rodei o controle: reconstruir a representação por dobra, só com os usuários de treino daquela dobra, move o resultado no máximo zero vírgula trinta e três de Acc@10 e zero vírgula vinte e nove de macro-F1, em três conjuntos numa semente. O que esse controle não cobre está escrito na mesma seção: no lado da categoria ele roda sobre sessenta e sete a oitenta e sete por cento das janelas de validação, porque um grafo só de treino não tem vetor de visita para usuário de validação. A avaliação é disjunta por usuário; o aprendizado da representação é transdutivo, e o texto declara os dois."
- **Proveniência:** Cap. 5, §5.5.2, p. 75-76 (`src/chapters/5_mobiwac/05_setup.tex:65-77`); primeiro dos quatro limites, p. 85.
- **Nunca dizer:** que a representação é causal, ou que o controle cobre visitas e lugares não vistos.

---

### SB8 · B2-2 · Os dois primeiros estudos usam divisão estratificada por amostra, não disjunta por usuário. Os resultados deles ainda valem?
- **Seção/subseção:** Série B · família B2 (Q19)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA o protocolo dos dois primeiros estudos (2.5)
- **Na tela:**
  `B2-2`
  - Declared in Chapter 3 itself (p. 46): a stratified splitter **over the samples**, so one user's check-ins may appear in both training and validation. For the category task the sample unit is the place, so **no place spans two folds**. One pinned seed, so the five folds are **one repetition**.
  - Both prefaces date their conclusions: p. 36, *"Its conclusions are the conclusions of the time, for the configuration studied here"*; p. 52, *"The conclusions reported here are those of the time, for that configuration"*.
  - What each chapter carries forward is **internal and directional**: Chapter 3 delivers a **null result**; Chapter 4 compares against **one baseline under the same protocol on both arms**.
  - No conclusion of this dissertation rests on an absolute number from either.
  `Next-POI Prediction = next category (Def. 2.7)` · Caps. 3/4 report **per-category F1**, not macro-F1
- **Fala (PT):** "Eles valem como o que são: comparações internas sob um protocolo mais fraco, declarado na página quarenta e seis e datado nos dois prefácios. O Capítulo 3 entrega um nulo, e um nulo não fica melhor com um protocolo pior. O Capítulo 4 compara contra uma única baseline, com o mesmo protocolo nos dois braços, então o que muda entre eles é a entrada. Nenhuma conclusão do documento depende de um número absoluto desses dois capítulos."
- **Proveniência:** Cap. 3, p. 46-47; prefácios p. 36 e p. 52; delimitação de moldura no Cap. 2, p. 35.
- **Nunca dizer:** chamar as médias por categoria dos Caps. 3/4 de macro-F1; comparar um número do Cap. 3 com um do Cap. 5.

---

### SB9 · B2-3 · O senhor escolheu a época no mesmo conjunto em que reporta o número?
- **Seção/subseção:** Série B · família B2   **Tempo:** sob demanda · ~50 s
- **LEDGER:** RETOMA os quatro limites declarados (5.6)
- **Na tela:**
  `B2-3`
  **Yes, and it is the second of the four declared limits, in the chapter's own words:** *"epoch selection consults the fold that the score is then read on, so every absolute score reported here is optimistic"*.
  Why the **comparison** is affected far less, stated rather than assumed:
  - the selection rule is **the same for both models on the same folds**, each model selected on its own validation objective;
  - for the category comparison the **dedicated** model receives the **wider search**: batch size at all six datasets and learning rate at four, against a joint-model search covering four of six, with Texas and California carrying a transferred configuration;
  - both sides of the **region** comparison run one fixed configuration, so that mitigation does not apply there.
  - The chapter closes it: *"It does not follow that the bias cancels exactly"*.
- **Fala (PT):** "Sim, e está declarado como segundo dos quatro limites: todo escore absoluto que eu reporto é otimista. O que eu posso defender é a comparação, e por duas razões que o texto declara em vez de supor. A regra de seleção é a mesma nos dois modelos, nas mesmas dobras, cada um selecionado no próprio objetivo de validação. E no eixo de categoria é o braço dedicado que recebe a busca mais ampla, o que torna a diferença que eu reporto conservadora, exceto em Flórida e Califórnia, onde as duas buscas ficam próximas. No eixo de região os dois lados rodam configuração fixa, então essa mitigação não vale ali. E eu fecho dizendo que não se segue que o viés se cancele exatamente."
- **Proveniência:** Cap. 5, p. 85, limite 2; cobertura por botão em §5.5.2, p. 75-76.
- **Nunca dizer:** que o viés se cancela.

---

### SB10 · B2-4 · As arestas entre visitas consecutivas só correm para frente. Isso foi sempre assim, ou foi corrigido?
- **Seção/subseção:** Série B · família B2   **Tempo:** sob demanda · ~55 s
- **LEDGER:** INTRODUZ a correção do canal entre visitas consecutivas no repositório e o que ela valeu | RETOMA a aresta só para frente como princípio de projeto (5.2)
- **Na tela:**
  `B2-4` · **provenance first**
  - **In the delivered text** the direction is a **design decision**, stated as the fourth of the four limits (p. 85) and in the method (p. 26): each visit node draws on the visits that precede it, in training and at readout, *"which is what keeps a node from carrying a feature of the target it is used to predict"*.
  - **In the repository**, the generation that produced every delivered cell is the one in which that channel is closed. Closing it was worth **28.63 macro-F1 at Alabama** on the category axis; the region axis moved by under two points.
  - **What the closure does not buy:** the representation is still trained **once over the whole graph**, so it is transductive by construction. The forecast splits stay user-disjoint.
  - Nothing in either volume reports a before-and-after of this channel, and this slide does not present one as a result.
- **Fala (PT):** "No documento a direcionalidade é decisão de projeto, e está nas duas páginas que a explicam: o alvo é predito do passado do usuário, então a representação é construída só do passado, no treino e na leitura. No repositório, a geração que produziu todas as células entregues é aquela em que esse canal está fechado, e fechá-lo valeu vinte e oito vírgula sessenta e três de macro-F1 em Alabama. Isso não torna a representação causal: ela continua treinada uma vez sobre o grafo inteiro, e eu digo isso. Se o senhor quiser o rastro completo, ele está no repositório, e nenhum dos dois volumes o narra."
- **Proveniência:** Cap. 5, p. 26 e p. 85 (limite 4). O valor de 28,63 macro-F1: `articles/dissertacao/CLAUDE.md` §0.2 e `wrapup/NEW_VERSION.md` §8. **pós-submissão / repositório: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** levantar isto se ninguém perguntar; apresentá-lo como descoberta ou como conserto da história do arco. O plano §2 tira o vazamento da narrativa principal.

---

### SB11 · B2-5 · A frase de cobertura de busca do Cap. 5 está correta?
- **Seção/subseção:** Série B · família B2 (ERR-6, ERR-7)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ as duas erratas de cobertura de busca (ERR-6, ERR-7)
- **Na tela:**
  `B2-5` · **two errata, offered rather than defended**
  - **ERR-6.** The clause *"at Florida and California it was not varied, so those two carry the value the smaller searches selected"* credits the small-dataset searches with a value they did not select. The small searches selected **0.0025 and 0.0005**; Florida and California carry **0.005**, the large-dataset tier. The coverage itself is right; the **provenance clause** is not.
  - **ERR-7.** The same sentence grades **Florida** with Texas as *"fewer folds"* in the batch-size search. In the dedicated category family the single-fold annotation is **Texas only**; Florida's single-fold screen belongs to the **joint-model** search, described one sentence later.
  - Neither changes a number or a verdict. Both **reduce** what the sentence claims.
- **Fala (PT):** "Duas frases de proveniência, não de resultado, e eu as trago em vez de esperar. A cobertura por botão está certa: taxa de aprendizado buscada em cinco dobras nos três conjuntos menores, em uma dobra no Texas, e não variada em Flórida e Califórnia. O que a frase atribui mal é a origem do valor que esses dois carregam. E a graduação de dobra única em Flórida pertence à busca do modelo conjunto, não à do dedicado; as duas buscas estão em sentenças vizinhas e a anotação migrou de uma para a outra. As duas correções enfraquecem a frase, e é por isso que eu as declaro."
- **Proveniência:** `wrapup/open_points/LACUNAS.md` §ERR-6, §ERR-7; texto vivo `src/chapters/5_mobiwac/05_setup.tex:52-55`. Correções destinadas ao depósito final.
- **Nunca dizer:** que a cobertura declarada está errada; o que está errado é a atribuição de origem.

---

### SB12 · B3-1 · B-P1 · A vantagem de região sobrevive a um controle de capacidade pareada?
- **Seção/subseção:** Série B · família B3 (Q14, U2)   **Tempo:** sob demanda · ~70 s   **OFERECER PROATIVAMENTE**
- **LEDGER:** INTRODUZ o controle de capacidade pareada no eixo de região
- **Na tela:**
  `B-P1` · **OFFER THIS BEFORE IT IS ASKED**
  **The control: give the dedicated region model the joint model's entire parameter budget, change nothing else. Seed 0, five folds.**
  | Dataset | dedicated (narrow) | dedicated (matched) | joint | joint − matched | *p* | unanimous |
  |---|---:|---:|---:|---:|---:|:--:|
  | California | 63.446 | **64.931** | 64.503 | **−0.428** | 0.0082 | 5/5 |
  | Texas | 64.951 | **66.330** | 66.117 | −0.214 | 0.1162 | 4/5 |
  - The width curve **saturates early**: an arm at **57 percent** of that budget already reaches the same level (352 → 528 is +0.021, *p* = 0.40).
  - **The reported region advantage measures capacity, not exchange between the tasks.**
  - What survives: one model produces both predictions in one forward pass, at no measured cost on either task.
  - **Category is untouched:** there a dedicated model with 6.5 times the parameters scores **lower** by 0.53 macro-F1 (*p* = 0.0011).
- **Fala (PT):** "Esta é a pergunta que eu quero fazer no lugar do senhor. O artigo submetido lista o confundimento de capacidade como um dos seus cinco limites e diz que o controle pareado não havia sido rodado. Eu o rodei. Dando ao dedicado de região o orçamento inteiro do modelo conjunto, ele fica acima do modelo conjunto na Califórnia por quatro décimos de Acc@10, com direção unânime nas cinco dobras; no Texas os dois ficam a zero vírgula vinte e um de distância, e o mesmo teste não separa essa diferença de zero. E um braço com cinquenta e sete por cento daquele orçamento já chega no mesmo nível. Ou seja: a vantagem de região que eu reporto mede capacidade, não troca entre as tarefas. O que sobrevive é o resultado operacional, um modelo produz as duas predições numa passada sem custo mensurável em nenhuma das duas. E o eixo de categoria, onde a tese vive, não é tocado: lá multiplicar por seis e meio os parâmetros do dedicado baixa o macro-F1 dele."
- **Proveniência:** `wrapup/post_submission_studies/P1_capacity_region.md` (medido 2026-08-13); verificação célula a célula em `wrapup/erratas/VERIFICACAO.md`; errata redigida em `wrapup/erratas/errata_Q14_capacity_region.tex`. **pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** `+2,12 / +2,05` (números de uma representação superada). As margens entregues são **TX +1,21** e **CA +1,06**. Nunca dizer que o Texas favorece o dedicado: lá a diferença não se separa de zero.

---

### SB13 · B3-2 · B-Q13 · O senhor afirma que o ganho vem da estrutura hierárquica e não das features. Como sabe?
- **Seção/subseção:** Série B · família B3 (Q13)   **Tempo:** sob demanda · ~70 s   **OFERECER PROATIVAMENTE**
- **LEDGER:** INTRODUZ o controle de concatenação refeito na escala da Tabela 9
- **Na tela:**
  `B-Q13` · **OFFER THIS BEFORE IT IS ASKED**
  **The deposited sentence is wrong in its direction, and there is a written errata.**
  Control redone on the scale of Table 9. Three arms per dataset, one seed, five folds, one training configuration, only the input changes.
  | Dataset | gap (place → check-in) | concatenation gain | share of the gap |
  |---|---:|---:|---:|
  | Alabama | +1.56 | **+1.73** (*p* = 0.003) | the whole gap |
  | Arizona | +2.50 | **+1.70** (*p* < 0.001) | 68 percent |
  | Florida | +0.21 | **+1.02** (*p* < 0.001) | past it |
  - Arizona is the one dataset where the check-in-level representation still leads the concatenation arm, by **0.80** (*p* = 0.03). At Alabama the two are within **0.18** (*p* = 0.53). At Florida the concatenation arm leads by **0.81** (*p* = 0.001).
  - **What Table 9 establishes stands:** the input representation dominates the architecture. **What falls** is the finer claim about which part of the representation carries the gain.
  - Fidelity: Alabama reproduces fold by fold and epoch by epoch. Arizona and Florida reproduce the mean within 0.07 and 0.03 but **not** fold by fold, so their scale is **open**.
- **Fala (PT):** "Não sabemos, e a afirmação no texto está errada. A fração de um décimo que ela cita vem de outro estudo, em outra variante do grafo e outro código, e não está na escala da Tabela 9. Refiz o controle na escala da própria tabela, em três conjuntos. Concatenar as features por visita ao place embedding fecha o intervalo inteiro em Alabama, sessenta e oito por cento em Arizona, e em Flórida vai muito além dele. São as features que carregam a maior parte do ganho de categoria. Há errata escrita. O que a tabela estabelece continua de pé: a representação de entrada domina a arquitetura. O que cai é a afirmação mais fina sobre qual parte da representação carrega o ganho. E digo o limite: Alabama reproduz exatamente, fold a fold; Arizona e Flórida reproduzem a média mas não os folds, e essa fidelidade fica em aberto."
- **Proveniência:** `wrapup/post_submission_studies/Q13_concatenation_control.md` (medido 2026-08-16); errata em `wrapup/erratas/errata_Q13_concatenation_scope.tex`; frase substituída no Cap. 5, p. 79. **pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** *"sob um décimo do salto place→check-in"* (aritmeticamente falso contra a Tabela 9 na mesma página). Nunca a frase retratada sobre representação hierárquica × injeção de features.

---

### SB14 · B3-3 · B-Q14 · O artigo submetido lista o confundimento de capacidade entre seus limites. A lista da dissertação não o carrega. Por que ele saiu?
- **Seção/subseção:** Série B · família B3 (Q14)   **Tempo:** sob demanda · ~50 s   **OFERECER PROATIVAMENTE**
- **LEDGER:** INTRODUZ a divergência de limites entre o artigo submetido e o volume principal
- **Na tela:**
  `B-Q14` · **OFFER THIS BEFORE IT IS ASKED**
  - **Submitted paper, p. 9, fourth of five limits:** the joint model carries more parameters than the two dedicated models combined, its region pathway several times the dedicated one, so *"the region advantage at Texas and California is therefore confounded with capacity"*, and the capacity-matched control *"has not been run"*.
  - **Main volume, p. 85:** *"Four limits qualify these results"*, and capacity on the region axis is not one of them.
  - What the main volume **does** carry: the parameter cost on p. 73 (about **4.2 million** at Alabama against **1.1 million** for the two dedicated models combined) and an attribution on p. 84 that credits neither the shared trunk nor transfer.
  - The only capacity control in either volume is **Appendix G of the supplement**, which covers **next category only**.
  - **It should not have gone out. It returns as an errata, and it now carries the measurement the paper said was missing** (→ `B-P1`).
- **Fala (PT):** "Ele não deveria ter saído. O artigo lista cinco limites e o quarto é exatamente esse; a dissertação lista quatro e ele não está entre eles. O custo de parâmetros está reportado na página setenta e três, e a atribuição da página oitenta e quatro já não credita o tronco compartilhado nem transferência, mas o limite nomeado saiu. Entra como errata, e agora vem com a medição que o artigo declarava faltar. É a página seguinte do meu material de reserva."
- **Proveniência:** artigo submetido `articles/[mobiwac]/src_fix/sections/07_discussion.tex:105-109`, p. 9; volume principal p. 85 e p. 73; Apêndice G do **suplemento**, p. 24-26. Errata: `wrapup/erratas/errata_Q14_capacity_region.tex`.
- **Nunca dizer:** "Apêndice B" ou "Apêndice G" sem nomear o volume (§8 regra 14).

---

### SB15 · B3-4 · B-Q15 · A errata do suplemento descreve um quarto fundamento de integridade com sonda linear em Florida. Onde ele está no volume de defesa?
- **Seção/subseção:** Série B · família B3 (Q15)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ a divergência entre a linha de errata do suplemento e o texto que ela descreve
- **Na tela:**
  `B-Q15`
  - **Supplement, p. 18, Table 4** describes a correction that adds *"a fourth ground"*, reporting a development audit of the forward-edge channel, with its three limits stated: **a linear probe**, **Florida at one random initialization**, and **earlier builds of the representation**.
  - **Main volume:** the integrity paragraph at pp. 75-76 does not enumerate grounds. Measured across the three full PDF extractions and the comment-stripped source: *"on three grounds"*, *"fourth ground"*, *"forward-edge"* have **zero** occurrences in the main volume; *"linear probe"* has one, inside the errata table itself.
  - **This is not an errata to write. It is an errata to correct, and the correction is to remove the line.** The audit it describes measured an earlier build of the representation, not the one the results use.
  - What the main volume does carry: the forward-edge channel as the **fourth declared limit**, p. 85, in prose and without a probe.
- **Fala (PT):** "Aquela linha da tabela de errata descreve uma auditoria de desenvolvimento feita sobre uma construção anterior da representação, e a própria linha declara os três limites dela. O texto que eu depositei não carrega esse fundamento, e não deveria: ele mediria uma preparação que não é a que os resultados usam. A linha de errata é que está sobredeclarando, e ela sai. O que está no volume de defesa é o canal de aresta como quarto limite, na página oitenta e cinco, em prosa e sem sonda."
- **Proveniência:** suplemento, p. 18, Tabela 4 (`wrapup/material_extra/`, `tables/mobiwac/errata_scope.tex:31-38`); volume principal, pp. 75-76 e p. 85. Ausências medidas em `wrapup/erratas/VERIFICACAO.md`.
- **Nunca dizer:** "Apêndice B" sem o volume. Aqui é **Apêndice B do suplemento** (Errata), não o do volume principal (Declaração de Uso de IA).

---

### SB16 · B3-5 · B-NOM · Vocês chamaram de semente o que a literatura chama de repetição. Isso muda os resultados?
- **Seção/subseção:** Série B · família B3   **Tempo:** sob demanda · ~55 s
- **LEDGER:** INTRODUZ a distinção repetição × réplica e o confundimento de um botão só
- **Na tela:**
  `B-NOM`
  - **It does not change the inference.** The reported test was always the paired *t* on the **four per-seed means**: n = 4, three degrees of freedom. The registry already separates `n = 20` (fitted models) from `n = 4` (inferential unit) and forbids writing "n = 20 paired repetitions".
  - **It changes the name, and it names a limit.** Each seed is one **repetition** of the cross-validation: one integer drives **two** things, the user partition and the initialization. So variance "between seeds" is partition plus initialization, and **no result produced so far separates them**.
  - Measured magnitudes: between folds **≈1.2 pp** · between repetitions **0.02 to 0.07 pp** · paired band over repetitions **0.05 to 0.15 pp**.
  - The fold term is **20 to 50 times** the repetition term **and is common to both arms**, which is why pairing detects what an unpaired analysis does not.
  - The later work did not correct an error. **It named a confound nobody had named.**
- **Fala (PT):** "Não muda a inferência: o teste reportado sempre foi o t pareado sobre as quatro médias por semente, e o registro de termos já distingue vinte modelos ajustados de unidade inferencial quatro. Muda o nome, e o nome nomeia um limite. Cada semente é uma repetição da validação cruzada, e um único inteiro governa duas coisas, a partição e a inicialização. Então variância entre sementes é partição mais inicialização, e nenhum resultado que eu já produzi separa as duas. As magnitudes ajudam a ver por que o pareamento importa: entre dobras é cerca de um vírgula dois ponto, entre repetições é dois a sete centésimos, e o termo de dobra é comum aos dois braços, então o pareamento o remove."
- **Proveniência:** `mtlcheck/docs/NOMENCLATURE.md` §§1-5 (repositório da reescrita); `GLOSSARY.md` §4, linhas `seed`, `n = 20` / `n = 4`; Cap. 5, §5.5.3, p. 76. **pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** "n = 20 repetições pareadas"; "réplicas independentes" para as quatro sementes.

---

### SB17 · B3-6 · B-KARPATHY · Como se decide quanta capacidade cada tarefa recebe num modelo multitarefa?
- **Seção/subseção:** Série B · família B3   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ o problema aberto de alocação de capacidade em aprendizado multitarefa (contexto de literatura)
- **Na tela:**
  `B-KARPATHY` · **context for `B-P1`**
  - Karpathy (2019), on designing a multitask network: *"how much feature sharing is there"*, *"tasks fight for the same shared capacity"*, *"there's finite capacity to go around... I don't really have language to describe how to correctly allocate capacity to tasks"*.
  - Standley et al. (ICML 2020): the task-affinity matrix, which asks the same question empirically.
  - PCGrad and GradNorm, which that discussion names, are **already in this dissertation** (Chapter 2).
  - **The point:** the capacity control in `B-P1` is exactly the measurement this literature says the field does not know how to design in advance. Running it is the answer to an open problem, not a wound.
- **Fala (PT):** "Isso é um problema aberto reconhecido da área, e não uma fragilidade só deste trabalho. Quando o Karpathy descreve como se desenha uma rede multitarefa, ele diz que não tem linguagem para descrever como alocar capacidade corretamente entre tarefas, e a matriz de afinidade entre tarefas do Standley e colegas ataca a mesma pergunta empiricamente. Os dois métodos que ele discute, PCGrad e GradNorm, já estão no meu Capítulo 2. O controle de capacidade que eu rodei é exatamente a medição que essa literatura diz que ninguém sabe desenhar de antemão."
- **Proveniência:** Karpathy (2019), palestra sobre desenho de redes multitarefa; Standley et al., ICML 2020; Cap. 2, §2.3 (PCGrad, GradNorm). **contexto de literatura, fora dos dois volumes.**
- **Nunca dizer:** nunca na trilha principal. Nunca usar *"tasks fight for capacity"* para **explicar** os resultados entregues: é exagero na direção oposta à posição simétrica de §5.3, e concederia a posição sobre o tronco.

---

### SB18 · B3-7 · B-MTLCHECK · Vocês reescreveram o sistema. Os números mudaram?
- **Seção/subseção:** Série B · família B3   **Tempo:** sob demanda · ~60 s
- **LEDGER:** INTRODUZ a reimplementação independente e a paridade de oito células
- **Na tela:**
  `B-MTLCHECK`
  - A clean reimplementation, written without reusing code from the old repository, running from raw check-ins to trained models. **No file produced by the old repository enters the path.**
  - Eight cells at Alabama and Arizona, under **the chapter's own protocol** (five flat folds): **mean delta −0.001 pp**, largest single deviation **0.421 pp**, which is **of the order of** the seed spread the chapter itself prints (0.04 to 0.22) — about twice its top, and the only cell above it.
  - Two caveats the sentence must carry: **one seed** on the new side against four on the chapter's; and the two columns are **not the same configuration** (the representation was rebuilt, the region tower unified, one component corrected).
  - **This is extra material. It does not correct Chapter 5.**
- **Fala (PT):** "O sistema foi reescrito do zero, sem reaproveitar código, e reproduz a tabela do Capítulo 5 com desvio médio de um milésimo de ponto em oito células; o maior desvio individual é de quatro décimos, e fica na ordem do desvio entre sementes que a própria tabela publica. Duas ressalvas viajam junto: uma semente do meu lado contra quatro do lado dela, e as duas colunas não são a mesma configuração, porque a representação foi reconstruída e a torre de região unificada. É material extra, e não corrige o Capítulo 5."
- **Proveniência:** `wrapup/NEW_VERSION.md` §3 (tabela de oito células) e §11 (procedência); evidência em `studies/porting_validation/evidence/estado_vs_dissertacao.json`. **pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** misturar um número da reescrita com um da dissertação na mesma frase. Os protocolos são outros (divisões aninhadas 70/10/20, métricas agrupadas fora de dobra, margem derivada de 0,4 pp contra os 2 pp registrados). Sob aquele protocolo, Alabama/região **vira inferior**, e isso vem de outro livro de regras.

---

### SB19 · B3-8 · As contagens de parâmetros do Apêndice G do suplemento estão certas?
- **Seção/subseção:** Série B · família B3   **Tempo:** sob demanda · ~50 s
- **LEDGER:** INTRODUZ as contagens corrigidas do Apêndice G do suplemento
- **Na tela:**
  `B-APXG`
  - **Printed (supplement, Appendix G, Table 8):** joint 4,197,621 (AL) and 5,151,189 (CA); original dedicated 644,359; wider dedicated 4,207,399 and 5,249,719, labeled 100.2% and 101.9% of the joint budget.
  - **Recounted against an independent implementation of the head:** 1,433,863 · 9,634,471 (**230%**) · 12,044,791 (**234%**). The published figures counted the same widths at the wrong depth (two layers instead of the four the cell inherits).
  - **The conclusion does not fall. It gets stronger.** The wider arm was not capacity-matched: it received **more than double** the joint budget and still scored **lower** than the narrow model.
  - What does not survive: the labels *"100.2% / 101.9% matched"*.
  - The result columns of Table 7 (Alabama −0.53, *p* = 0.0011; California, one seed, three arms within 0.06) are unaffected.
- **Fala (PT):** "As larguras estão certas; as contagens foram feitas pela profundidade errada, duas camadas em vez das quatro que a célula executada herda. Recontadas contra uma implementação independente da cabeça, os três números sobem, e o braço alargado passa a ter mais que o dobro do orçamento do modelo conjunto, não cem por cento dele. A conclusão do controle fica mais forte: eu dou ao dedicado mais que o dobro e ele não recupera. O que não sobrevive é o rótulo de pareado. Há errata."
- **Proveniência:** suplemento, Apêndice G, Tabelas 7 e 8, pp. 24-26; recontagem em `wrapup/NEW_VERSION.md` §10.6. **pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** `100,2%` e `101,9%` como se fossem pareamento de capacidade (§8 regra 9, proibição literal).

---

### SB20 · B4-LEAK · O embedding do Capítulo 3 também devolve a própria categoria do lugar?
- **Seção/subseção:** Série B · família B4   **Tempo:** sob demanda · ~75 s
- **LEDGER:** INTRODUZ o canal indireto de rótulo medido no embedding do Cap. 3 (auditoria de código)
- **Na tela:**
  `B4-LEAK` · **the two chapters differ by mechanism, not by innocence**
  - **Chapter 4:** the venue-type feature maps **one to one** onto the seven top-level categories, 284 to 365 distinct values per state, **not one ambiguous**. That is an **exact lookup**.
  - **Chapter 3:** each place's input feature is built from the **average of its neighbors' categories**, with the place's own one-hot excluded by construction. **The exclusion holds exactly, and it does not close the channel.** Each neighbor's feature is itself an average over that neighbor's neighborhood, and the place belongs to those neighborhoods.
  - Measured: the place's own category returns at a **mean weight of 0.10** against a **total own-category weight of 0.39**. Removing that contribution and changing nothing else lowers a probe of the place's own category from **0.46 to 0.30 macro-F1** (0 to 1 scale), against a **majority-class floor of 0.07**.
  - Confirmed by causal intervention: relabeling one place, without touching that place's own input row, changes the embedding of every place that receives a message.
  - **The formulation is the code audit's: an exact lookup in Chapter 4, a diluted average recovered through one hop in Chapter 3.**
  - **Does it invalidate the chapters? No.** The **sequential** task of both never has the target in its input, and that is where the arc's conclusions come from. Chapter 4's preface: *"every claim this chapter makes about the sequential task [...] stands as published"*.
  `Next-POI Prediction = next category (Def. 2.7)` · Caps. 3/4 report **per-category F1**
- **Fala (PT):** "Os dois capítulos têm o problema, e a diferença é de mecanismo, não de inocência. No Capítulo 4 a feature de tipo de local mapeia um para um nas categorias: é consulta direta, e o prefácio já declara isso. No Capítulo 3 o vetor de entrada de cada POI exclui o one-hot dele próprio, por construção, e eu verifiquei que essa exclusão vale exatamente. Ela não fecha o canal. Cada vizinho tem, no próprio vetor, a média do bairro dele, e o lugar está nesse bairro, então um salto de agregação devolve o rótulo. Medido: peso médio de zero vírgula dez contra zero vírgula trinta e nove de peso total da própria categoria, e uma sonda do próprio rótulo cai de zero vírgula quarenta e seis para zero vírgula trinta de macro-F1, contra um piso de classe majoritária de zero vírgula zero sete. E confirmei por intervenção causal. A pergunta que importa vem depois: isso invalida os capítulos? Não, porque a tarefa sequencial dos dois nunca teve o alvo na entrada, e é dela que vêm as conclusões que o arco carrega."
- **Proveniência:** auditoria de código do repositório (`DGI-leak-audit`), texto registrado em `wrapup/erratas/material_apx_static_scope.tex`; prefácio do Cap. 4, p. 52; range 284 a 365 reproduzido sobre os cinco parquets de estado. ⚠ **o texto que registra isto não chegou a nenhum dos dois volumes**: o apêndice que o carrega não é chamado por nenhum `\input` vivo. **Resposta oral apoiada no repositório, não citação do documento.**
- **Nunca dizer:** **"o DGI não vaza"**. A auditoria foi encomendada precisamente para não depender dessa crença, e mediu que o canal não fecha. O que se afirma é a diferença de mecanismo e de grau.

---

### SB21 · B4-DGI · O objetivo contrastivo do DGI está fazendo o que vocês pensam?
- **Seção/subseção:** Série B · família B4   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ a constatação incidental sobre o objetivo contrastivo do Cap. 3
- **Na tela:**
  `B4-DGI` · **the limit is the headline**
  - An audit recorded, incidentally and outside the leak question, that the contrastive objective **as implemented appears degenerate**: positive and negative score sets identical as multisets, and a measured loss floor matching `2·ln2` to six decimals.
  - If confirmed, *"trained DGI embedding"* may not describe what Chapter 3 actually used.
  - **What I cannot say is that it was re-measured. It was not.** The artifacts of that audit are not in the repository and the observation was never acted on.
  - **What it would limit:** Chapter 3 is the **null result** of the arc. A weaker representation than assumed makes the null **less** surprising, not more. And neither later chapter inherits DGI: Chapter 4 replaces it, Chapter 5 builds on the check-in-level representation.
- **Fala (PT):** "Uma auditoria registrou, de passagem, que o objetivo contrastivo daquele capítulo, como implementado, parece degenerado: os conjuntos de escore positivo e negativo são idênticos como multiconjuntos, e o piso de perda medido bate dois ln dois em seis casas. Se isso se confirmar, chamar aquilo de embedding treinado pode não descrever o que o capítulo usou. O que eu não posso dizer é que foi re-medido, porque não foi. E o que isso limitaria: o Capítulo 3 é o nulo do arco, e uma representação mais fraca que a suposta torna o nulo menos surpreendente, não mais. Os dois capítulos seguintes não herdam aquele embedding."
- **Proveniência:** ledger §F da auditoria de código, registrado no comentário de aval aberto em `wrapup/erratas/material_apx_static_scope.tex`. **não consta em nenhum dos dois volumes.**
- **Nunca dizer:** que foi re-medido. **Se ninguém perguntar, não levantar.**

---

### SB22 · B4-1 · A entrada decomposta tem 192 dimensões e a baseline tem 64. Quanto do ganho é só largura?
- **Seção/subseção:** Série B · família B4 (Q17)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a comparação não pareada em largura (4.4)
- **Na tela:**
  `B4-1`
  - MTLnet projects **any** input to the same 256-dimensional shared space through the task-specific encoders, *"so that the capacity of the shared layers and task heads remains unchanged across the evaluated models"* (p. 61).
  - The **input** width differs: 192 against 64. The published chapter says so on the same page: *"the difference in input dimensionality may influence part of the observed gains"*, and asks for a control that equalizes dimensionality.
  - Chapter 6, p. 87, repeats the requirement: *"Chapter 4 therefore calls for an equal-dimension control to separate the semantic contribution of the encoders from the effect of the additional width"*.
  - **The equal-dimension control has not been run. It is declared, not defended.**
  `Next-POI Prediction = next category (Def. 2.7)` · Cap. 4 reports **per-category F1**
- **Fala (PT):** "As camadas compartilhadas e as cabeças têm capacidade idêntica nos dois braços, porque a arquitetura projeta qualquer entrada ao mesmo espaço de duzentos e cinquenta e seis dimensões. O que difere é a largura de entrada, cento e noventa e dois contra sessenta e quatro, e o próprio capítulo publicado diz que isso pode influenciar parte dos ganhos e pede o controle de dimensão igual. O Capítulo 6 repete a exigência. O controle não foi executado, e eu declaro isso como limite em vez de defender."
- **Proveniência:** Cap. 4, p. 61; Cap. 6, p. 87.
- **Nunca dizer:** "pareado em largura".

---

### SB23 · B4-2 · Em Travel a baseline continua ganhando. O senhor tem uma explicação ou uma desculpa?
- **Seção/subseção:** Série B · família B4 (Q18)   **Tempo:** sob demanda · ~50 s
- **LEDGER:** RETOMA Travel rotulado por tarefa (4.4)
- **Na tela:**
  `B4-2` · **label Travel by task, because it moves in opposite directions**
  | Travel, Florida | MTLnet | ST-MTLNet (SIREN) |
  |---|---:|---:|
  | **category** (Table 6) | 45.49 ± 1.20 | **64.89 ± 1.20** |
  | **next category** (Table 7) | **64.47 ± 1.02** | 45.00 ± 1.10 |
  - California repeats the pattern on the sequential task: 46.05 ± 0.84 against 36.94 ± 1.70 and 37.82 ± 1.04. **Texas does not**: there the variants lead (34.26 ± 0.90 against 29.71 ± 1.32).
  - The chapter's own reading, p. 64: Travel *"tends to involve sparser movements between distant regions"*, and *"the graph topology used by DGI may be more efficient for preserving relationships between geographically distant POIs"*, with the two representation types capturing complementary aspects.
  - The chapter declares this as a limitation (p. 66), together with the fact that the three encoders are used jointly and no individual contribution is isolated.
  `Next-POI Prediction = next category (Def. 2.7)` · Cap. 4 reports **per-category F1**
- **Fala (PT):** "Primeiro rotulo a tarefa, porque Travel se move em direções opostas nas duas e a sala se confunde. Em categoria, Travel é onde a decomposição mais ganha: em Flórida vai de quarenta e cinco vírgula quarenta e nove para sessenta e quatro vírgula oitenta e nove. Na tarefa sequencial, é onde ela mais perde: sessenta e quatro vírgula quarenta e sete da baseline contra quarenta e cinco. A explicação do capítulo é que Travel envolve movimentos esparsos entre regiões distantes, e ali a topologia de grafo preserva melhor as relações entre POIs geograficamente distantes, enquanto codificadores de coordenada capturam padrão local. E o capítulo declara isso como limitação, junto com o fato de que os três codificadores são usados em conjunto e ele não isola a contribuição de cada um."
- **Proveniência:** Cap. 4, Tabela 6 e Tabela 7, p. 65; leitura em p. 64; limitação em p. 66.
- **Nunca dizer:** deixar o ganho da tarefa estática falar pela sequencial.

---

### SB24 · B4-3 · O melhor codificador espacial depende do estado. Isso não é escolha de hiperparâmetro disfarçada?
- **Seção/subseção:** Série B · família B4   **Tempo:** sob demanda · ~50 s
- **LEDGER:** INTRODUZ a acusação de overfitting de seleção e o ganho por variante isolada (SIREN no Texas) | RETOMA a declaração de melhor-de-dois por linha (4.2)
- **Na tela:**
  `B4-3`
  - **The range is best-of-two per row, and saying so is the answer.** Category gains of **20.2 to 22.0** points per state count, for each category-state cell, the better of SIREN and Sphere2Vec-M.
  - Read **by isolated variant**, SIREN alone at Texas averages **+17.89**, outside the announced range.
  - On the sequential task the same rule gives **15 of 21** category-state combinations to the variants, with one technical tie at Outdoors in Florida (the baseline mean above the best variant by 0.02, inside one standard deviation).
  - The chapter states the pattern as an observation: SIREN stands out in Florida and California, Sphere2Vec-M more often in Texas. **There is no universally better spatial encoder here, and no rule for choosing one without seeing the evaluation.**
  `Next-POI Prediction = next category (Def. 2.7)` · Cap. 4 reports **per-category F1**
- **Fala (PT):** "É melhor de dois por linha, e a resposta é dizer isso. O intervalo de vinte vírgula dois a vinte e dois pontos conta, em cada célula, o melhor dos dois codificadores. Lido por variante isolada, o SIREN sozinho no Texas rende dezessete vírgula oitenta e nove em média, fora do intervalo anunciado. Na tarefa sequencial, o mesmo critério dá quinze de vinte e uma combinações às variantes, com o que o capítulo chama de um empate técnico em Outdoors na Flórida, a dois centésimos e dentro de um desvio padrão. E o capítulo declara o padrão como observação: não há codificador espacial universalmente melhor, e eu não tenho regra para escolher um sem olhar a avaliação."
- **Proveniência:** Cap. 4, `chapters/4_courb/results.tex:44,:62`, Tabelas 6 e 7, p. 65; a leitura por variante isolada em `articles/CoUrb_2026/slides/judge_feedback.md:11`.
- **Nunca dizer:** apresentar a faixa sem declarar que é melhor de dois por linha.

---

### SB25 · B4-4 · Os números do corpus de Florida mudam entre capítulos. 990.518 no Cap. 3 e 1.407.034 no Cap. 5. Qual está certo?
- **Seção/subseção:** Série B · família B4 (Q20)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a base de evidência e as duas extrações de Florida (2.3)
- **Na tela:**
  `B4-4` · **two extractions of one state of one public dataset, not a discrepancy**
  | | users | POIs | check-ins |
  |---|---:|---:|---:|
  | Chapters 3 and 4 | 20,301 | 65,009 | 990,518 |
  | Chapter 5 | 21,052 | 76,544 | 1,407,034 |
  - The mechanism is declared: the category-mapping table was extended about eleven months after the earlier extraction, and the added places fall mostly in Entertainment, Outdoors and Travel.
  - A controlled comparison confirms that **every POI, user and check-in of the earlier extraction reappears in the current one**, which adds others.
  - The three Chapter 3 figures are themselves a declared errata: the published article left placeholders, and the values come from the published CoUrb table.
- **Fala (PT):** "São duas extrações do mesmo estado do mesmo conjunto público, não um conflito. A tabela de mapeamento de categorias foi estendida cerca de onze meses depois da extração anterior, e os lugares acrescentados caem majoritariamente em Entertainment, Outdoors e Travel. Uma comparação controlada confirma que cada POI, usuário e check-in da extração anterior reaparece na atual, que adiciona outros. Cada capítulo reporta o corpus como o pipeline da sua época o produziu, e os três números do Capítulo 3 são, eles próprios, uma errata declarada."
- **Proveniência:** suplemento, §B.4, pp. 13-14; registro em `src_utils/evidence/cbic_recompute_result.md`.
- **Nunca dizer:** "superconjunto". Não há evidência de contenção declarada nesses termos no texto; o que há é a reaparição verificada de cada registro.

---

### SB26 · B4-5 · Quanto custou o modelo conjunto do Capítulo 3?
- **Seção/subseção:** Série B · família B4   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ o custo de convergência do Cap. 3 (Tabela 4)
- **Na tela:**
  `B4-5` · **the table, never the published prose**
  | Model | Time (s) | Epochs | MFLOPs |
  |---|---:|---:|---:|
  | Category | 16.26 | 3.8 | 2.315 |
  | Next | 18.71 | 3.2 | 0.012 |
  | **MTL** | **80.88** | 3.2 | 0.234 |
  - Wall time to reach the target F1 scores: **80.88 s against the cumulative 34.97 s** of the two single-task models, about **2.3 times**.
  - MFLOPs do not follow the same pattern, and the chapter says so.
  - **The published prose of that article carries two defective statements about this measurement**, both registered in its own errata. **I quote the table, not the prose.**
  `5-fold cross-validation` · targets: Category F1 47, Next F1 32.2 · `Next-POI Prediction = next category (Def. 2.7)`
- **Fala (PT):** "A tabela é esta, e eu leio dela, não da prosa publicada. Para alcançar os alvos de F1, o modelo conjunto levou oitenta vírgula oitenta e oito segundos de tempo de parede, contra trinta e quatro vírgula noventa e sete somados dos dois modelos de tarefa única, cerca de duas vírgula três vezes. Em MFLOPs o padrão não se repete, e o capítulo diz isso. A prosa publicada daquele artigo carrega duas frases defeituosas sobre esta medição, e as duas estão registradas na errata dele."
- **Proveniência:** Cap. 3, Tabela 4, e o parágrafo de leitura na mesma seção; erratas em `articles/CBIC___MTL/ERRATA.md` e Apêndice B do **suplemento**.
- **Nunca dizer:** "quase quatro vezes" e "cerca do dobro" em MFLOPs (as duas frases defeituosas da prosa publicada). Nunca MFLOPs sem o enquadramento de tempo de parede (§8 regra 16).

---

### SB27 · Q5 · As duas entradas do modelo conjunto vêm do mesmo grafo. Elas não são independentes. Qual o tamanho dessa dependência?
- **Seção/subseção:** Série B · família B5 (Q5, `[ABERTO]`)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ o limite sobre a dependência entre as duas entradas do modelo conjunto
- **Na tela:**
  `Q5` · **not measured, and the limit is the headline**
  - **Declared, without a number**, in Chapter 2, p. 27: MTLnet derives both inputs from one place embedding, whereas the joint model reads two tables exported from the same check-in-level representation, and *"The two tables share an origin by construction, so they are not independent views"*.
  - The only **quantified** boundary is architectural: on the spatial route the pooled place representation is **detached**, so the place-region and region-city objectives cannot update the check-in encoder through that branch (Appendix E of the main volume, p. 112).
  - That bounds gradient flow **inside representation training**. It does not quantify the **information overlap** between the two exported tables.
  - **Why it does not overturn the thesis:** the comparison that carries the conclusions is paired and internal, the joint model against the dedicated models under the same representation, windows and folds. Shared origin bears on the mechanistic reading of what the trunk does, which p. 84 already leaves open, not on the validity of the measured difference.
- **Fala (PT):** "As duas tabelas partilham origem por construção, e eu digo isso no Capítulo 2, página vinte e sete. A única fronteira quantificada é arquitetural: na rota espacial a representação de lugar entra com gradiente interrompido, e está no Apêndice E, página cento e doze. A magnitude da sobreposição de informação entre as duas entradas não foi medida. Isso afeta a leitura mecanística do que o tronco faz, que o texto já deixa aberta na página oitenta e quatro, e não a validade da diferença medida, porque a comparação é pareada e interna."
- **Proveniência:** Cap. 2, p. 27 (`chapters/2_fundamentals.tex:813`); Apêndice E do volume principal, p. 112 (`chapters/apx_h_check2hgi_joint_model.tex:172`); Cap. 5, p. 82 e p. 84.
- **Nunca dizer:** inventar um número para a dependência.

---

### SB28 · Q8 · O resultado de região é transferência entre tarefas, ou é a arquitetura e os parâmetros que o senhor acrescentou?
- **Seção/subseção:** Série B · família B5 (Q8, `[ABERTO]`)   **Tempo:** sob demanda · ~60 s
- **LEDGER:** INTRODUZ a triagem de uma dobra sobre o tronco em California e Texas
- **Na tela:**
  `Q8` · **I do not claim transfer, and the text does not either**
  - Chapter 5, p. 84: *"The evidence here does not separate their contributions"*, and the surviving claim is about the **design**: this combination, shared representation and private spatial path together, produces a joint region output above two dedicated models at the two datasets with the largest region vocabularies.
  - **A one-fold screen** (seed 0, `--only-fold 0`, three arms; **one number per arm, so it detects only a large effect**): at California the region advantage survives severing the trunk (**−0.099**) and survives deleting the category task as well (**−0.077**); at Texas it survives severing the trunk (**−0.120**). All under 0.15 point.
  - **The five-fold trunk ablation at those two datasets does not exist.** Five-fold ablations were run only at Alabama and Florida.
  - **Post-submission**, a capacity-matched control answers the other half: the reported region advantage **measures capacity** (→ `B-P1`).
- **Fala (PT):** "Eu não reivindico transferência, e o texto não reivindica. A afirmação da página oitenta e quatro é sobre o desenho completo, representação compartilhada mais caminho espacial privado. Uma triagem de uma dobra mostra que a vantagem de região na Califórnia sobrevive a severar o tronco e a deletar a tarefa de categoria, movendo menos de zero vírgula quinze ponto, e no Texas sobrevive a severar o tronco. É uma triagem: uma dobra dá um número por braço, então ela só detecta efeito grande, e tinha poder para a hipótese de que o tronco carrega os dois pontos. Não a confirmou. A ablação de cinco dobras nesses dois conjuntos não existe, e eu declaro isso. E a outra metade da pergunta, os parâmetros, eu respondo no slide seguinte, com o controle de capacidade."
- **Proveniência:** Cap. 5, p. 84; triagem em `docs/studies/closing_data/v18/region_1fold_triage/FINDING.md`; ausência da ablação de cinco dobras em `docs/studies/closing_data/v18/SWEEP_PLAN.md:285-290`. **os números da triagem são de repositório: não constam em nenhum dos dois volumes.**
- **Nunca dizer:** creditar TX/CA a transferência entre tarefas. Nunca apresentar os valores absolutos da triagem ao lado das células da Tabela 10: são convenções diferentes (uma dobra, uma semente).

---

### SB29 · U1 · O tronco compartilhado contribui algo em Texas e California?
- **Seção/subseção:** Série B · família B5 (U1)   **Tempo:** sob demanda · ~40 s
- **LEDGER:** RETOMA a triagem de uma dobra (Q8) | RETOMA a posição sobre o tronco (5.5)
- **Na tela:**
  `U1` · **not measured**
  - What exists: the one-fold screen of `Q8`, where every arm moves under **0.15** point.
  - The five-fold ablation at those two datasets **does not exist**. Five-fold arms were run at **Alabama** (dcat −0.015 / dreg −0.138, and dcat −0.154 / dreg −0.004) and **Florida** (dcat +0.002 / dreg +0.026).
  - **Why it does not overturn the thesis:** the thesis does not claim the trunk carries the result. The claim on p. 84 is about the full design, and the same page states that the evidence does not separate the two parts. The screen had power for the hypothesis that the trunk carries the two points and did not confirm it, which **supports** the cautious wording rather than contradicting it.
- **Fala (PT):** "Não foi medido em cinco dobras nesses dois conjuntos, e eu digo isso. O que existe é a triagem de uma dobra, onde todos os braços se movem menos de zero vírgula quinze ponto, e ablações de cinco dobras em Alabama e Flórida. Isso não derruba a tese porque a tese não afirma que o tronco carrega o resultado: a afirmação é sobre o desenho completo, e a mesma página declara que a evidência não separa as duas partes."
- **Proveniência:** `region_1fold_triage/FINDING.md`; `SWEEP_PLAN.md:275-277,:285-290`; Cap. 5, p. 84. **repositório: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** "não podemos provar que não contribuiu, portanto provavelmente contribuiu".

---

### SB30 · U2 · A vantagem de região sobrevive a um controle de capacidade pareada?
- **Seção/subseção:** Série B · família B5 (U2)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA o controle de capacidade pareada (B-P1) | RETOMA o Apêndice G do suplemento
- **Na tela:**
  `U2` · **not measured on the region axis, in either volume**
  - The only capacity control in the two volumes is **Appendix G of the supplement**, and it covers **next category**: at Alabama, multiplying the dedicated model's trainable parameters by 6.5 **lowers** its macro-F1 by **0.53** (*p* = 0.0011, direction unanimous over the twenty folds); at California, one seed, the three arms lie within **0.06**. The appendix states its own limit: *"What the control does not do is decompose the joint model: it holds the representation fixed and varies width"*.
  - **Post-submission it was measured on the region axis**, and the answer is unfavorable to the region reading (→ `B-P1`).
  - **Why it does not overturn the thesis:** on the **category** axis, where the representation thesis lives, the parameter-count explanation is tested and not supported. The two region gains are **secondary results outside the registered analysis plan**, declared on p. 76 and repeated on p. 88, and the parameter cost is reported on p. 73 rather than hidden.
- **Fala (PT):** "Nos dois volumes, não. O único controle de capacidade que eles carregam é o Apêndice G do suplemento, e ele cobre next category: em Alabama, multiplicar por seis e meio os parâmetros do dedicado baixa o macro-F1 dele em meio ponto, com direção unânime nas vinte dobras. Depois do envio eu rodei o controle no eixo de região, e a resposta não me favorece: está no slide do P1. Isso não derruba a tese porque a tese vive no eixo de categoria, e os dois ganhos de região são resultados secundários, fora do plano registrado, o que o texto declara em duas páginas."
- **Proveniência:** suplemento, Apêndice G, Tabela 7, pp. 24-26; Cap. 5, p. 73, p. 76, p. 88; `wrapup/post_submission_studies/P1_capacity_region.md`.
- **Nunca dizer:** "100,2% / 101,9% pareado" (contagens corrigidas em `B-APXG`).

---

### SB31 · U3 · Qual o tamanho da dependência entre as duas entradas do modelo conjunto?
- **Seção/subseção:** Série B · família B5 (U3)   **Tempo:** sob demanda · ~30 s
- **LEDGER:** RETOMA o limite sobre a dependência entre as duas entradas (Q5)
- **Na tela:**
  `U3` · **not measured** · same answer as `Q5`
  - Non-independence is **declared without a number** (Chapter 2, p. 27). The only quantified boundary is the detached copy on the spatial route (Appendix E of the main volume, p. 112).
  - **What would close it:** a single overlap quantity between the semantic and spatial windows on the same sequence, for example representational similarity or the information one window carries about the other under a linear probe.
  - **Why it does not overturn the thesis:** the comparison that carries the conclusions is paired and internal, under the same representation, windows and folds (p. 82).
- **Fala (PT):** "É a mesma pergunta do Q5, e a resposta é a mesma: não foi medido. O que fecharia isso é uma quantidade única de sobreposição entre as duas janelas na mesma sequência. E não derruba a tese porque a comparação que a sustenta é pareada e interna."
- **Proveniência:** Cap. 2, p. 27; Apêndice E do volume principal, p. 112; Cap. 5, p. 82.
- **Nunca dizer:** oferecer um número aproximado.

---

### SB32 · U4 · O cosseno entre os gradientes das duas tarefas continua ortogonal em Texas e California?
- **Seção/subseção:** Série B · família B5 (U4)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA o Apêndice D do volume principal (cosseno)
- **Na tela:**
  `U4` · **not measured at those two**
  - Appendix D of the main volume covers **four of the six** datasets, and says so: *"Texas and California are not measured here"*. Those are precisely the two where the joint model outperforms on region, and the appendix names that too: the diagnosis *"leaves the largest label spaces untested"*.
  - It also limits itself by architecture: *"Nothing here says the gradients stay orthogonal in a model that shares more of its depth, couples the tasks in a cascade, or shares an output layer"*.
  - At the four measured datasets, equivalence to zero holds within a **±0.05** margin, with every mean inside it and **99.6 percent** of individual epochs (Figure 8, Table 11).
  - **Why it does not overturn the thesis:** the appendix explains why a gradient balancer had nothing to balance, and that explanation is supported independently by the screen of nineteen balancers at two datasets (p. 70). No conclusion of Chapter 5 depends on the cosine at Texas or California.
- **Fala (PT):** "Não foi medido nesses dois, e o apêndice diz isso na própria tabela: ele cobre quatro dos seis conjuntos, e deixa os maiores espaços de rótulo sem teste. Nos quatro medidos, a equivalência a zero vale com margem de cinco centésimos, com todas as médias dentro dela. E o apêndice também se limita por arquitetura: ele não diz nada sobre um modelo que compartilhe mais profundidade ou acople as tarefas em cascata. Isso não derruba nada porque a função dele é explicar por que um balanceador de gradiente não tinha o que balancear, e essa explicação é sustentada de forma independente pela triagem de dezenove balanceadores."
- **Proveniência:** Apêndice D do volume principal, p. 106-108; Figura 8, p. 107; Tabela 11; triagem de balanceadores, Cap. 5, p. 70.
- **Nunca dizer:** chamar um cosseno próximo de zero de "nenhum conflito detectado" (o `GLOSSARY` exige a formulação de equivalência).

---

### SB33 · U5 · Quão longe fica a região predita quando o modelo erra?
- **Seção/subseção:** Série B · família B5 (U5)   **Tempo:** sob demanda · ~40 s
- **LEDGER:** RETOMA o terceiro dos quatro limites declarados (5.6)
- **Na tela:**
  `U5` · **not measured, and declared as such**
  - Chapter 5, p. 85: *"Where the shortlist misses, the geographic size of the error is the quantity that would matter to such a service, and measuring it requires the per-visit predictions that the evaluation path does not retain, so it is left to future work"*.
  - The service framing is explicitly motivation, not result, and is the **third** of the four declared limits: *"we do not build or evaluate a mobility-aware service"*.
  - **Why it does not overturn the thesis:** no claim in the document is about service performance. The shortlist reading on p. 84 is presented with the number that supports it, the Acc@10 of Table 10 itself: **California 64.54 percent** in ten tracts out of 8,501; **Texas 66.15 percent** in ten out of 6,553.
- **Fala (PT):** "Não foi medido, e o texto declara por quê: medir o tamanho geográfico do erro exige as predições por visita, que o caminho de avaliação não retém. Isso é trabalho futuro. E o enquadramento de serviço é motivação, não resultado: é o terceiro dos quatro limites. Nenhuma afirmação do documento é sobre desempenho de serviço; a leitura de lista curta vem com o número que a sustenta, que é o próprio Acc@10 da tabela."
- **Proveniência:** Cap. 5, p. 84 e p. 85; Tabela 10.
- **Nunca dizer:** especular sobre erro geográfico ou desempenho de serviço (§8 regra 16).

---

### SB34 · U6 · O senhor consegue separar a mudança de par de tarefas da mudança de representação e de topologia?
- **Seção/subseção:** Série B · família B5 (U6)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a sexta limitação e o trabalho futuro amarrado a ela (6.3)
- **Na tela:**
  `U6` · **not measured, and the reason is structural**
  - Limitation 6, p. 90: no controlled ablation separates the change of representation and topology from the change of task pair.
  - The ablation that would separate them, running **static category classification under the check-in-level representation**, *"is not clean under that representation: the category of the visited place is an input feature of a check-in node, so that target would be partly readable from its own input"*. That follows from the design and was not measured, **so the confound is bounded by the fixed-pair control rather than removed**.
  - **Chapter 4 is the fixed-pair control**: same architecture, same task pair, only the input moves.
  - **Why it does not overturn the thesis:** the thesis is conditional by construction (p. 89), and it is Chapter 4, not Chapter 5, that carries the claim that the representation is the dominant factor.
  - Future work tied 1:1 to the limitation, p. 91: a static target the representation does not carry as an input feature.
- **Fala (PT):** "Não, e a razão é estrutural, não uma omissão. A ablação que separaria as duas seria rodar classificação estática de categoria sob a representação por check-in, e essa ablação não é limpa: a categoria do lugar visitado é feature de entrada de um nó de check-in, então o alvo seria parcialmente legível da própria entrada. Como não é limpa, o confundimento fica limitado pelo controle de par fixo em vez de removido, e esse controle é o Capítulo 4, que mantém o par e move só a entrada. A tese é condicional por construção, e é o Capítulo 4 que sustenta a afirmação sobre representação."
- **Proveniência:** Cap. 6, limitação 6, p. 90; trabalho futuro, p. 91; tese condicional, p. 89.
- **Nunca dizer:** "MTL funciona" sem condição.

---

### SB35 · U7 · A representação serve modelos que não são o seu?
- **Seção/subseção:** Série B · família B5 (U7)   **Tempo:** sob demanda · ~40 s
- **LEDGER:** RETOMA a terceira limitação (transdutividade) e o trabalho futuro (6.3)
- **Na tela:**
  `U7` · **not measured**
  - Chapter 6, p. 88: the result *"also supports testing Check2HGI in other mobility prediction architectures, although its benefit in those architectures has not yet been evaluated"*.
  - Limitation 3, p. 90: the representation is **transductive**, trained on each dataset's check-in graph, *"so it cannot represent unseen places or users without retraining"*.
  - **Why it does not overturn the thesis:** every comparison that carries the thesis holds the consuming model fixed and varies only the representation. Table 9 is exactly that design: same single-task model, same training configuration, same folds, same sliding windows, same epoch budget; only the input changes.
- **Fala (PT):** "Não foi avaliado, e o Capítulo 6 diz isso com essas palavras. E há um limite anterior: a representação é transdutiva, treinada no grafo de check-ins de cada conjunto, então ela não representa lugares ou usuários novos sem retreino. Isso não derruba a tese porque toda comparação que a sustenta mantém o modelo consumidor fixo e varia só a representação, que é exatamente o desenho da Tabela 9."
- **Proveniência:** Cap. 6, p. 88 e limitação 3, p. 90; Tabela 9, p. 79, e sua legenda.
- **Nunca dizer:** afirmar transferência da representação para outras arquiteturas.

---

### SB36 · U8 · A margem de dois pontos é o limiar em que um serviço se comportaria diferente. Isso foi medido em um serviço?
- **Seção/subseção:** Série B · família B5 (U8)   **Tempo:** sob demanda · ~45 s
- **LEDGER:** RETOMA a justificativa da margem de dois pontos (B1-5)
- **Na tela:**
  `U8` · **not measured in a service, and it is stated as a judgment**
  - The justification is a declared judgment: a service acts on which region will be busy, not on a single rank position, and *"A two-point change in Acc@10 is below the level at which this service would behave differently"* (p. 77).
  - The empirical support that does exist is the dispersion: the sd of the paired difference across the four user partitions runs **0.02 to 0.16**, and the intervals at **Istanbul, Arizona and Florida** would support a **one-point** margin. **Alabama's would not.**
  - **Why it does not overturn the thesis:** the margin was registered **before any result was read** (p. 76), and the four cells inside it clear it comfortably, the largest deficit being **0.87** (p. 82). Under a one-point margin three of the four datasets still hold by their own intervals, and the document names the exception.
- **Fala (PT):** "Não, e o texto apresenta a margem como julgamento, não como medição de serviço. O apoio empírico que existe é a dispersão: o desvio padrão da diferença pareada entre as quatro partições de usuários vai de dois a dezesseis centésimos, e os intervalos de Istambul, Arizona e Flórida sustentariam uma margem de um ponto. O de Alabama não, e o texto nomeia isso. E ela foi registrada antes de qualquer resultado ser lido, com as quatro células vencendo-a com folga, o maior déficit em zero vírgula oitenta e sete."
- **Proveniência:** Cap. 5, §5.5.3, pp. 76-77; p. 82.
- **Nunca dizer:** apresentar a margem como derivada dos dados.

---

### SB37 · B6-1 · O Resumo em português diz que o modelo conjunto superou os dedicados na próxima categoria em todos os conjuntos. O senhor sustenta isso?
- **Seção/subseção:** Série B · família B6   **Tempo:** sob demanda · ~40 s
- **LEDGER:** INTRODUZ o defeito do Resumo entregue e a errata aplicada
- **Na tela:**
  `B6-1` · **no. It is a defect, it was isolated, and it is corrected**
  | | what it says |
  |---|---|
  | **Resumo (delivered)** | superiority on next category *"em todos os conjuntos"* |
  | **English Abstract, §2.5, Ch. 5, Ch. 6** | superiority **at one dataset** |
  | **The delivered result** | **Florida only**, +0.19, Holm *p* 0.011 |
  - The defect was **isolated to the Portuguese Resumo**. Every other surface of the document already said one dataset.
  - Corrected in the source for the final deposit, with a registered errata. The delivered PDF is kept frozen as the record of what the banca received, and it differs from the source in this one sentence.
- **Fala (PT):** "Não sustento. É um defeito, e é isolado: o Abstract em inglês, a seção dois ponto cinco, o Capítulo 5 e o Capítulo 6 já diziam em um conjunto. O resultado entregue é superioridade na Flórida, mais zero vírgula dezenove, com p de Holm de zero vírgula zero onze. Está corrigido no fonte para a versão final, com errata registrada, e o PDF entregue fica congelado como o registro do que a banca recebeu."
- **Proveniência:** `wrapup/erratas/errata_resumo_escopo_categoria.tex`, aplicada ao fonte em 2026-08-21; `articles/dissertacao/CLAUDE.md` §1.2.
- **Nunca dizer:** a frase do Resumo entregue, em voz alta, exceto se perguntado (§8 regra 9 e decisão do autor).

---

### SB38 · B6-2 · Quando o senhor diz "Apêndice B", de qual dos dois documentos está falando?
- **Seção/subseção:** Série B · família B6   **Tempo:** sob demanda · ~35 s
- **LEDGER:** INTRODUZ a colisão de letras de apêndice entre os dois volumes
- **Na tela:**
  `B6-2` · **two volumes, colliding letters. Always name the volume.**
  | | **main volume** (119 pp) | **supplement** (27 pp) |
  |---|---|---|
  | A | Other Scientific Contributions | not present |
  | **B** | **AI-Use Disclosure** | **Errata to the Reproduced Articles** |
  | C | Data Ethics and Governance | not present |
  | **D** | **Why the Two Tasks Do Not Compete on the Shared Trunk** | **A Label-History Benchmark for the Next-Category Task** |
  | **E** | **How Check2HGI and the Joint Model Work** | **The Human-Subjects Question** |
  | F | not present | Adaptation of the HGI Baseline |
  | G | not present | A Parameter-Count Control for Next-Category Prediction |
  - The deposited text **deliberately does not point at the supplement**: it cites only itself and the repository. That is the document's policy.
- **Fala (PT):** "Preciso nomear o volume toda vez, porque as letras colidem. No volume principal, o Apêndice B é a Declaração de Uso de IA; no suplemento, é a Errata dos artigos reproduzidos. O D e o E também colidem. E o texto depositado não aponta para o suplemento de propósito: ele cita apenas a si próprio e o repositório."
- **Proveniência:** `articles/dissertacao/CLAUDE.md` §1; política declarada em `wrapup/erratas/README.md` (Q24).
- **Nunca dizer:** "Apêndice B" sem o volume (§8 regra 14).

---

### SB39 · B6-3 · Quantos usuários entram de fato no seu teste?
- **Seção/subseção:** Série B · família B6   **Tempo:** sob demanda · ~45 s
- **LEDGER:** INTRODUZ a distinção entre a coluna de usuários do corpus e a população pós-filtro
- **Na tela:**
  `B6-3` · **the table's user column is the raw corpus, and only the window column crosses the filter**
  | Table 8 column | population |
  |---|---|
  | check-ins · users · POIs | **raw corpus** |
  | windows | **after** the minimum-length filter (ten check-ins), stride 1 |
  - Verified by direct count on the raw files: Alabama 113,846 check-ins, **3,858 users**, 11,848 places; Arizona 236,450, **7,869**, 20,666. Those are exactly the printed values.
  - Counted on the representation actually used, the users **present in the pooled predictions** are **1,101** (AL), **2,136** (AZ) and **14,530** (Istanbul). The window column agrees exactly in all three (96,326 · 200,895 · 271,666), which is what shows it is the same representation.
  - Arithmetic closes both ways at Alabama: the 1,101 qualifying users hold 106,235 of the 113,846 check-ins, leaving 7,611 for the 2,757 who do not qualify, about 2.8 each.
  - **A caption clause fixes this without touching a number.**
- **Fala (PT):** "A coluna de usuários é do corpus bruto, e só a coluna de janelas atravessa o filtro de comprimento mínimo. Conferi por contagem direta nos arquivos brutos: os três números impressos de Alabama e Arizona batem ao caractere. Contando sobre a representação que roda, os usuários que efetivamente entram nas predições são mil cento e um em Alabama, dois mil cento e trinta e seis em Arizona. Três colunas de corpus e uma de experimento na mesma linha, com uma legenda que não distingue. Resolve-se com uma cláusula na legenda, sem tocar em nenhum número, e é uma errata que eu declaro."
- **Proveniência:** Tabela 8, p. 75 do volume principal (`src/tables/mobiwac/datasets.tex`); reconciliação e contagem direta em `wrapup/NEW_VERSION.md` §10.1. **a contagem pós-filtro é pós-submissão: não consta em nenhum dos dois volumes.**
- **Nunca dizer:** que os números impressos estão errados. Eles descrevem o corpus; o que falta é a legenda que distingue as duas populações.

---

### SB40 · B6-4 · O piso de Markov de região fica acima de três sistemas publicados. Isso não diz que a sua tarefa é fácil, ou que os externos foram mal executados?
- **Seção/subseção:** Série B · família B6 (Q22)   **Tempo:** sob demanda · ~50 s
- **LEDGER:** RETOMA o piso Markov-1 (5.4) e a comparação externa (5.5)
- **Na tela:**
  `B6-4` · **the chapter takes this head on, and declines a single explanation**
  - HMT-GRN falls below the floor at **all six** datasets, the ReHDM reference at **three**, STAN at **four**.
  - Two facts are declared about how the numbers were produced:
    - the floor is computed under **our own sliding windows and folds**, and the windows advance one visit at a time, *"so the region of the last visit is a strong predictor of the next one, and a first-order transition table reads exactly that signal"*. At Alabama the target is the last visited region in **32.9 percent** of windows.
    - the three systems do not meet the floor on equal terms: HMT-GRN on the same data, folds and initializations; STAN on the same folds but with its own representations and sequence construction; ReHDM under its own published protocol.
  - The chapter's closing: *"Neither fact establishes why the floor lies above the three systems, and we do not claim a single explanation. We treat the floor, not the external systems, as the reference the region task has to clear."*
  - The joint model exceeds the floor by **4.1 to 10.0** points at all six datasets.
- **Fala (PT):** "O piso é computado sob as minhas janelas, que avançam uma visita por vez, e em Alabama o alvo é a última região visitada em trinta e dois vírgula nove por cento das janelas, de modo que uma tabela de transição de primeira ordem lê exatamente esse sinal. E os três sistemas não encontram o piso em termos iguais: um roda nos mesmos dados, dobras e inicializações; outro nas mesmas dobras mas com representações próprias; o terceiro sob o protocolo publicado dele. Nenhum desses dois fatos estabelece por que o piso fica acima, e eu não reivindico uma explicação única. Eu trato o piso, e não os sistemas externos, como a referência que a tarefa de região tem de ultrapassar, e o modelo conjunto fica de quatro vírgula um a dez pontos acima dele nos seis conjuntos."
- **Proveniência:** Cap. 5, pp. 82-83; Tabela 10 e sua nota de rodapé.
- **Nunca dizer:** atribuir a ordenação a má execução dos sistemas externos.

---

### SB40b · B6-5 · Vocês chegam a superar os modelos da literatura?
- **Seção/subseção:** Série B · família B6   **Tempo:** sob demanda · ~55 s
- **LEDGER:** RETOMA a Tab. 10 (5.5), a arte prévia de 5.2 e o piso de Markov de 5.4 · **não INTRODUZ nada** — cada cláusula é reprodução do texto entregue
- **Na tela:**
  - **Next category — the comparison is clean.** POI-RGNN is **native to the task** and re-implemented from its published architecture and hyperparameters; it is **above the tuned Markov-K floor at all six**. A frase do próprio capítulo: *"the joint model stands **at least 3.06 points** above the strongest external baseline at every dataset."*
  - **E o capítulo usa isso como argumento, não como vitória:** a representação move a mesma métrica em **+0,23 a +6,29**, o salto sobre a literatura é de pelo menos **3,06**, e um modelo contra dois é **meio ponto** — *"the smallest of the three effects at work here, which is the sense in which one model can replace two on this task."*
  - **Next region — more careful, and here is why.** Não existe modelo publicado que ataque este alvo exato: o mais próximo, **DRRGNN**, prediz região sobre **regiões descobertas por pessoa**, não sobre uma partição fixa da cidade. A comparação teve de ser construída — e o **piso de Markov-1 está acima do HMT-GRN nos seis e do STAN em quatro**. Por isso o capítulo trata **o piso, não os sistemas externos**, como a referência.
  - **A ressalva que vale para os dois eixos.** Os externos rodam nos próprios embeddings, então esta margem **inclui a vantagem de representação**. A comparação que decide a tese é a coluna **Dedicated** — mesma representação, mesmas janelas, mesmas partições.
- **Fala (PT):** "Sim, e a resposta é diferente nos dois eixos, então eu separo. Na próxima categoria a comparação é limpa: o POI-RGNN é nativo da tarefa, foi reimplementado da arquitetura e dos hiperparâmetros publicados, e está acima do piso de Markov sintonizado nos seis. O capítulo diz a frase inteira: o modelo conjunto fica pelo menos três vírgula zero seis pontos acima do baseline externo mais forte em todos os conjuntos. E ele usa isso como argumento, não como vitória: a representação move a mesma métrica de zero vírgula vinte e três a seis vírgula vinte e nove, o salto sobre a literatura é de pelo menos três, e a diferença entre um modelo e dois é meio ponto. É o menor dos três efeitos, e é nesse sentido que um modelo pode substituir dois. Na região eu sou mais cauteloso, e digo por quê. Não existe baseline nativo desse alvo: o mais próximo, o DRRGNN, prediz região sobre regiões descobertas por pessoa, não sobre uma partição fixa da cidade, então o espaço de rótulos é outro. A comparação teve de ser construída, e um piso de Markov de primeira ordem supera o HMT-GRN nos seis e o STAN em quatro. Por isso o capítulo trata o piso, e não os sistemas externos, como a referência que a tarefa tem de vencer. E a ressalva que vale para os dois eixos: esses externos rodam nos próprios embeddings, então essa margem inclui a vantagem de representação. A comparação que decide a tese não é essa. É a coluna Dedicated, que partilha representação, janelas e partições comigo."
- **Proveniência:** *"at least 3.06 points above the strongest external baseline at every dataset"*, os três efeitos e *"the smallest of the three effects"* → `chapters/5_mobiwac/06_results.tex:108-113`; POI-RGNN reimplementado e o Markov de melhor ordem por conjunto → `05_setup.tex:178`; HMT-GRN com a estrutura multitarefa preservada → `:180`; STAN com a saída adaptada → `:182`; DRRGNN sobre regiões descobertas por pessoa → `02_related.tex:99`; o piso acima dos três externos → `06_results.tex:271`; *"the floor, not the external systems, as the reference"* → `:292`; a margem inclui a vantagem de representação → `:261`. Análise completa e o restante da proveniência: [`wrapup/open_points/BASELINES_EXTERNOS.md`](../../wrapup/open_points/BASELINES_EXTERNOS.md).
- **Nunca dizer:** ⚠ **"superamos o STAN"** como afirmação espontânea — é a alegação de pior apoio da tabela (saída adaptada, partições parciais TX 4/5 e CA 2/5, semente 0). ⚠ **"amputamos" o HMT-GRN** — ele prediz região **nativamente**, como etapa para restringir a busca do lugar (`2_fundamentals.tex:348`); o que se removeu serve à busca do lugar, não à predição de região. ⚠ Tratar o **piso de Markov com desdém** — ele é baseline sintonizado (melhor ordem por conjunto) e é a referência que o próprio capítulo adota. ⚠ Usar a margem sobre a literatura como evidência **sobre multitarefa** — ela inclui a vantagem de representação, e o capítulo diz isso na mesma página. ⚠ Reivindicar a margem de **região** sobre os externos sem dizer, na mesma respiração, que o piso trivial também os supera.

### SB40c · B6-6 · Como cada baseline externo rodou
- **Seção/subseção:** Série B · família B6   **Tempo:** sob demanda · ~60 s
- **LEDGER:** RETOMA os baselines de 5.4 e a arte prévia de 5.2 · **não INTRODUZ nada** — cada célula é reprodução do texto entregue
- **Na tela:** uma tabela **Sistema × Tarefa × Como rodou × A ressalva**, mais a linha de por que nenhum é nativo de região.

  | Sistema | Tarefa | Como rodou | A ressalva |
  |---|---|---|---|
  | **POI-RGNN** | categoria | *re-implemented from its published architecture and hyperparameters*, nas nossas partições | **nenhuma** — é nativo da tarefa e está acima do piso Markov-K nos seis |
  | **Markov** | ambas | *best order per dataset* (categoria); Markov-1 sobre transições de região, sob as nossas janelas e partições | não é figurante: é **a referência que o capítulo declara** |
  | **HMT-GRN** | região | mesmos dados, partições e inicializações; **estrutura multitarefa preservada**; prior de transição por partição | *"not a reproduction of the complete published system"* — o que saiu serve à **busca do lugar** |
  | **STAN** | região | mesmas partições, mas **embeddings e sequências próprios**; **saída adaptada** para ranquear regiões | **partições parciais: TX 4/5, CA 2/5**, semente 0 |
  | **ReHDM** | região | sob o **protocolo publicado dele** | não medido nas nossas janelas nem partições; TX e CA com uma semente |

  - **Por que nenhum é nativo de região:** nenhum modelo publicado ataca este alvo; o mais próximo, **DRRGNN**, prediz região sobre **regiões descobertas por pessoa**.
- **Fala (PT):** "Este é o mapa de como cada externo rodou, e eu prefiro mostrá-lo do que ser perguntado. Na categoria: o POI-RGNN é nativo da tarefa e foi reimplementado da arquitetura e dos hiperparâmetros publicados, nas minhas partições. Nada a ressalvar ali. Na região é diferente, e a razão é a última linha: não existe modelo publicado que ataque este alvo. O mais próximo, o DRRGNN, prediz região diretamente, mas sobre regiões descobertas por pessoa, não sobre uma partição fixa da cidade — o espaço de rótulos é outro. Então a comparação teve de ser construída, e cada um dos três carrega uma ressalva diferente. O HMT-GRN é o mais próximo de justo: mesmos dados, mesmas partições, mesmas inicializações, e eu mantive a estrutura multitarefa dele. O que removi serve à busca do lugar exato, que é a etapa seguinte à predição de região — ele prediz região nativamente, e é essa etapa que eu avalio. O STAN é o mais adaptado: eu troquei a camada de saída dele para ranquear regiões, ele constrói os próprios embeddings e as próprias sequências, e as partições são parciais em dois conjuntos. O ReHDM roda sob o protocolo publicado dele, então não está nas minhas janelas nem nas minhas partições. E o Markov não é figurante: a ordem é escolhida por conjunto, e é ele que o capítulo declara como a referência que a tarefa tem de vencer."
- **Proveniência:** POI-RGNN reimplementado e Markov de melhor ordem por conjunto → `chapters/5_mobiwac/05_setup.tex:178`; HMT-GRN com estrutura multitarefa preservada e prior por partição → `:180`; STAN com saída adaptada → `:182`; DRRGNN sobre regiões descobertas por pessoa → `02_related.tex:99`; *"not a reproduction of the complete published system"*, partições parciais de STAN e a semente única de ReHDM → nota da Tabela 10, `tables/mobiwac/results.tex`; o piso como referência declarada → `06_results.tex:292`. Análise completa: [`wrapup/open_points/BASELINES_EXTERNOS.md`](../../wrapup/open_points/BASELINES_EXTERNOS.md).
- **Nunca dizer:** ⚠ **"amputamos" o HMT-GRN** — ele prediz região nativamente (`2_fundamentals.tex:348`) e a estrutura multitarefa foi **preservada**; o que saiu serve à busca do lugar. ⚠ Tratar o **Markov** como figurante. ⚠ Apresentar esta tela **espontaneamente**: ela é resposta, não afirmação — a manchete continua sendo a coluna *Dedicated*.

### SB41 · B7-1 · Como o Check2HGI aprende sem ver os rótulos das duas tarefas?
- **Seção/subseção:** Série B · família B7 (Apêndice E do volume principal)   **Tempo:** sob demanda · ~60 s
- **LEDGER:** INTRODUZ o pipeline de cinco estágios e os três discriminadores bilineares do Apêndice E | RETOMA a ideia infomax (2.1)
- **Na tela:**
  `B7-1` · **Figure 9 (main volume, p. 111)**
  Five stages, and the boundary between the third and the fourth is the point:
  1. validate the records, order each user's visits by time, map each place to a polygon;
  2. build temporal, place and region graphs linked by the check-in / place / region / city hierarchy;
  3. train Check2HGI, export separate **64-dimensional** check-in and region tables;
  4. build stride-one windows, nine observed visits, the tenth as target;
  5. train one joint model on the two representation sequences.
  - **Check2HGI is fitted first and its exported tables stay fixed during supervised training.** The joint model does not rebuild the graph or update the representation encoder. **Check2HGI never receives the two forecast labels.**
  - Learning signal: **bilinear discriminators at three hierarchy boundaries** (check-in to place, place to region, region to city), each separating a true pairing from a corrupted one.
  - Two auxiliary terms: masked-place reconstruction (15 percent hidden, neighbors aggregated, category distribution reconstructed) and a place-table anchor.
  - Optimization: full-batch Adam, 500 epochs, learning rate 1e-3, clip norm 0.9; the saved state is the epoch with the smallest complete training loss.
- **Fala (PT):** "O objetivo que treina a representação distingue um pareamento verdadeiro de um corrompido, em três fronteiras da hierarquia: visita para lugar, lugar para região, região para cidade. Nenhum rótulo de próxima categoria ou próxima região entra ali. E a fronteira que importa é entre o terceiro e o quarto estágio: a representação é ajustada primeiro, e as duas tabelas exportadas ficam fixas durante o treino supervisionado. O modelo conjunto não reconstrói o grafo nem atualiza o codificador."
- **Proveniência:** Apêndice E do volume principal, §§ "The complete method at a glance" e "How Check2HGI learns and what it exports", pp. 109-113; Figura 9, p. 111; Tabela 12, p. 117.
- **Nunca dizer:** que a representação é causal ou indutiva. Ela é **transdutiva**, e o próprio capítulo diz.

---

### SB42 · B7-2 · O que exatamente entra num nó de check-in, e por que as arestas só correm para frente?
- **Seção/subseção:** Série B · família B7   **Tempo:** sob demanda · ~50 s
- **LEDGER:** INTRODUZ o decaimento exponencial de uma hora na aresta de sucessão e a ausência de coocorrência no conjunto de arestas | RETOMA as features de nó por visita e a aresta só para frente como princípio de projeto (5.2)
- **Na tela:**
  `B7-2`
  - Each check-in starts with **15 values**: seven category indicators, sine and cosine of hour of day, sine and cosine of day of week, and four elapsed-time values. Cyclic encoding makes the endpoints of the daily and weekly clocks adjacent.
  - **Coordinates are not appended.** They determine polygon membership, Delaunay edges and region adjacency instead.
  - **Check-in succession:** consecutive visits by the same user are connected **in one direction only**, earlier to later, with an edge weight decaying exponentially with the time interval, one-hour decay constant. The appendix states the reason as design: *"a target is predicted from a user's past, so a representation built for that target is constructed from the past alone, in training and at readout alike"*.
  - **Category co-occurrence is absent from the reported edge set.** Repeated visits to one place receive no extra check-in edge; they meet through their common place node.
- **Fala (PT):** "Cada nó de check-in começa com quinze valores: sete indicadores de categoria, seno e cosseno da hora do dia, seno e cosseno do dia da semana, e quatro tempos decorridos. As coordenadas não entram nesse vetor; elas decidem a que polígono o lugar pertence e quais arestas de Delaunay existem. E as arestas entre visitas consecutivas do mesmo usuário correm numa direção só, da anterior para a posterior, com peso caindo exponencialmente no intervalo de tempo. A razão está escrita como projeto: o alvo é predito do passado do usuário, então a representação é construída só do passado, no treino e na leitura."
- **Proveniência:** Apêndice E do volume principal, § "From check-in records to a heterogeneous mobility graph", p. 109-110; Tabela 12, p. 117, linha "Check-in input".
- **Nunca dizer:** "coocorrência" como canal deste grafo. E não narrar a direcionalidade como conserto: no documento ela é decisão de projeto (§2 do plano).

---

### SB43 · B7-3 · Como a hierarquia sobe de uma visita até a cidade?
- **Seção/subseção:** Série B · família B7   **Tempo:** sob demanda · ~55 s
- **LEDGER:** INTRODUZ a cópia com gradiente interrompido na rota espacial e o resumo de cidade ponderado por área (Apêndice E) | RETOMA o Check2HGI e o diagrama de níveis (5.2)
- **Na tela:**
  `B7-3` · **bottom-up, four steps (Figure 9)**
  1. **Two check-in graph-convolution layers** over the succession edges, residual update. Output: one 64-dimensional vector per visit. A row that described only the visit's own category and time now also reflects the visits that precede it.
  2. **Pool visits at their place** with four attention heads, one learned query shared across places, keys and values from that place's visits. Result: how a place is used, not only where it is.
  3. **Add the spatial place neighborhood:** combine the pooled place representation with a trainable place table initialized from a pretrained one, then one weighted graph convolution over the Delaunay place graph. **The pooled place representation is detached on this route**, so the place-region and region-city objectives cannot rewrite the check-in encoder through the spatial branch.
  4. **Region and city:** a second four-head pooling over the places of a region, a 64 to 64 convolution between adjacent region polygons, then an **area-weighted city summary**. The city vector serves the highest objective and is **not** an input to the joint model.
- **Fala (PT):** "O passe é de baixo para cima. Duas camadas de convolução sobre as arestas de sucessão dão o vetor por visita, e a partir dali uma linha que descrevia só a própria categoria e o próprio tempo passa a refletir as visitas que a precedem. Depois as visitas de um mesmo lugar são resumidas por atenção, com quatro cabeças, o que produz como um lugar é usado e não apenas onde ele fica. A rota espacial recebe esse resumo com o gradiente interrompido, e essa fronteira é deliberada: impede que as perdas geográficas mais altas reescrevam a representação temporal da visita. Em cima, região e cidade. O vetor de cidade serve ao objetivo mais alto e não entra no modelo conjunto."
- **Proveniência:** Apêndice E do volume principal, §§ "Step 1" a "Step 4", pp. 110-112; a cópia com gradiente interrompido em p. 112.
- **Nunca dizer:** nada aqui é resultado; é descrição de método.

---
- ⚠ **v3 · 27/08 — duas cláusulas saíram da TELA e ficaram na `% FALA:` do próprio frame** *(protocolo de relocação, passo 3: registro)*:
  - **passo 1**, *"A row that described only the visit's own category and time now also reflects the visits that precede it"* → fala, em português: *"uma linha que descrevia só a própria categoria e o próprio tempo passa a refletir as visitas que a precedem"*;
  - **passo 2**, *"Result: how a place is used, not only where it is"* → fala: *"o que produz como um lugar é usado e não apenas onde ele fica"*.
  - **Motivo:** o frame absorveu a carga do `B7-2` e sobravam 12 pt, com o rodapé colidindo com o último fragmento. **As duas são interpretação, não mecanismo.**
  - 🛑 **O que NÃO pode sair, e foi proposto uma vez:** a cláusula do **destacamento** no passo 3 (*"The pooled place representation is detached on this route"*). Ela é a manchete do slide (`Four steps, and one deliberate gradient cut`) **e** a evidência que o `Q5` aponta (*"a única fronteira quantificada é arquitetural"*). Cortá-la quebra a referência cruzada e deixa o subtítulo sem referente.
  - ⚠ **Sobre a assimetria que fica:** os passos 1 e 2 viram mecanismo puro; os passos 3 e 4 mantêm as orações de consequência. **Isso é correto e não é descuido** — o que sobra em 3 e 4 (*"não podem reescrever o codificador de check-in"*, *"o vetor de cidade não é entrada do modelo conjunto"*) são **fatos sobre o que não pode acontecer e sobre a interface**, que é mecanismo. O que saiu de 1 e 2 era glosa.

### SB44 · B7-4 · O modelo conjunto é compartilhamento rígido com outro nome?
- **Seção/subseção:** Série B · família B7   **Tempo:** sob demanda · ~55 s
- **LEDGER:** INTRODUZ as projeções direcionais não amarradas do módulo de interação (Apêndice E) | RETOMA compartilhamento rígido (2.2) e o tronco de atenção cruzada (5.3)
- **Na tela:**
  `B7-4` · **Figure 10 (main volume, p. 114)**
  - **Private encoders, same shape, different parameters:** each history goes through 64 → 256 → 256 → 256, ReLU and layer normalization after every transformation, dropout 0.1 after the first two. Equal tensor widths do not imply equal meaning: a check-in vector describes one visit in a trajectory, a region vector a geographic area after spatial aggregation.
  - **Two bidirectional cross-attention blocks.** In each block the category stream queries the region stream first; the region stream then queries the already updated category stream. Four heads, padding positions excluded, each direction with its own projections, residual connections, normalizations and a 256 → 256 → 256 GELU feed-forward network.
  - **The interaction subsystem is jointly optimized, but the directional projections are not tied.** The appendix states the difference plainly: *"The model therefore differs from classical hard parameter sharing: the tasks keep private encoders and heads, while their activations meet in a fixed trainable interaction module that receives gradients from both losses."*
- **Fala (PT):** "Não. Os dois históricos entram em codificadores próprios, de mesma forma e parâmetros diferentes, porque largura igual não é significado igual: um vetor de check-in descreve uma visita numa trajetória, e um vetor de região descreve uma área depois de agregação espacial. O que compartilha é um módulo de interação: dois blocos de atenção cruzada bidirecional, em que a corrente de categoria consulta a de região e depois a de região consulta a de categoria já atualizada. As projeções das duas direções não são amarradas. As tarefas mantêm codificadores e cabeças privados, e o que se encontra são as ativações, num módulo que recebe gradiente das duas perdas."
- **Proveniência:** Apêndice E do volume principal, §§ "Step 1" e "Step 2" do modelo conjunto, pp. 113-115; Figura 10, p. 114; Tabela 12, p. 117, linhas "Private encoders" e "Interaction".
- **Nunca dizer:** chamar o desenho de compartilhamento rígido, e também não afirmar que o compartilhamento é o que produz o resultado (§5.3 do plano: a evidência não separa as contribuições).

---

### SB45 · B7-5 · Por que a região tem uma torre privada, e o que o β faz?
- **Seção/subseção:** Série B · família B7   **Tempo:** sob demanda · ~55 s
- **LEDGER:** INTRODUZ a fusão de duas torres na cabeça de região e o prior de transição inativo
- **Na tela:**
  `B7-5`
  - **Category head:** a four-layer unidirectional GRU, width 256, reading the category-context sequence; the top-layer state at the last valid position, then layer normalization, dropout, seven logits.
  - **Region head keeps two routes on purpose:**
    - the **private tower** reads the **raw 9×64 region history** with a spatio-temporal attention model, four heads, dropout 0.3;
    - the **shared-context tower** reads the 9×256 sequence produced by cross-attention, eight heads, dropout 0.1.
    - Each returns one 128-dimensional feature, fused as **f_R = f_priv + β · W_shr f_shr**, with **β trainable, initialized at 0.1**.
  - **This lets category context help region prediction without removing the direct spatial sequence model.**
  - **One term is inactive in the reported configuration:** an additive region-transition prior, whose scalar weight is **fixed at zero and not trained**, so it reaches neither the logits nor the gradients. The same table is never used as a training signal, and the category output is never an input to the region output. **Region prediction depends only on the two towers.**
- **Fala (PT):** "A cabeça de categoria é uma GRU de quatro camadas sobre a sequência de contexto. A de região mantém duas rotas de propósito: uma torre privada, que lê o histórico de região cru, com um modelo de atenção espaço-temporal, e uma torre de contexto, que lê a saída da atenção cruzada. As duas devolvem um vetor de cento e vinte e oito dimensões, e a fusão é aditiva, com um escalar treinável inicializado em zero vírgula um. Isso deixa o contexto de categoria ajudar a região sem remover o modelo sequencial espacial direto. E há um termo que fica inativo na configuração reportada: um prior aditivo de transição entre regiões, com peso fixado em zero e não treinado, então ele não chega nem aos logits nem aos gradientes."
- **Proveniência:** Apêndice E do volume principal, § "Step 3", pp. 115-116, e o parágrafo sobre os caminhos inativos; Tabela 12, p. 117, linhas "Category head", "Region head" e "Inactive region paths".
- **Nunca dizer:** escrever `log_T` ou qualquer nome de repositório para o prior; o nome do documento é **region-transition prior**.

---

### SB46 · B7-6 · O cross-attention atende histórico de região de um usuário com histórico de categoria de outro?
- **Seção/subseção:** Série B · família B7   **Tempo:** sob demanda · ~50 s
- **LEDGER:** INTRODUZ o pareamento aleatório de linhas entre os dois carregadores durante o treino
- **Na tela:**
  `B7-6` · **the sharpest question in the appendix, and the appendix answers it**
  - **During training: yes.** The category and region loaders use the **same user-disjoint fold** and **shuffle independently**, so their batch rows have compatible shapes but *"need not describe the same user or window in one optimizer step; cross-attention operates on that random pairing"*. The shorter loader cycles until the longer one is exhausted.
  - **At validation: no.** *"Validation rows are record-aligned."*
  - The appendix calls it what it is: *"This operational detail is unusual, but it is part of the reported training protocol."*
  - Objective: **fixed 0.50 / 0.50** cross-entropy, logit adjustment τ = 0.5 on the category term at train time only, region term unadjusted. AdamW with three parameter groups (category, region, shared), one backward pass through the connected model. Fifty epochs, five user-disjoint folds, seeds {0, 1, 7, 100}. **The checkpoint maximizes the geometric mean of category macro-F1 and region Acc@10, so selection depends on both tasks.**
- **Fala (PT):** "No treino, sim, e o apêndice declara isso em vez de esconder. Os dois carregadores usam a mesma dobra disjunta por usuário e embaralham de forma independente, então as linhas de um passo de otimização não descrevem necessariamente o mesmo usuário ou a mesma janela, e a atenção cruzada opera sobre esse pareamento. Na validação as linhas são alinhadas por registro. O próprio apêndice chama isso de detalhe operacional incomum, e diz que é parte do protocolo reportado. Se o senhor quiser a leitura mais dura: durante o treino a atenção cruzada aprende a usar contexto de região em geral, não o contexto daquele usuário, e o resultado é medido na validação alinhada."
- **Proveniência:** Apêndice E do volume principal, § "How the joint model is optimized and evaluated", pp. 116-117; Tabela 12, p. 117, linhas "Objective", "Optimization" e "Evaluation".
- **Nunca dizer:** apresentar isto como defeito corrigido. É o protocolo reportado, declarado no documento.

---

## Perguntas abertas dos redatores

- *(sec1-2)* TENSÃO INTERNA DO PLANO, resolvida por leitura declarada (o portão G2 deve confirmar): o §3 da Seção 1 exige em 1.1 o número de Song et al. (~93%) e, no mesmo bloco, o campo 'Nunca dizer' proíbe 'nenhum número além do veredito'. Li a proibição como valendo para números NOSSOS: o 93 é licenciado pela própria subseção 1.1, e os deltas de S4 são o veredito. Registrado no campo 'Nunca dizer' de S2 e S4.
- *(sec1-2)* LEDGER: `macro-F1` e `Acc@10` aparecem em S4 apenas como rótulo do número (a WRITING_LAW §3 proíbe porcentagem nua), e não como definição. As definições continuam sendo INTRODUZ em 2.4 (macro-F1, S11) e em 5.4 (Acc@10). Se o G2 preferir a leitura estrita do ledger, a correção é retirar os deltas da tela de S4 e deixar só as superfícies registradas; a fala não muda em nenhum dos dois casos, porque a frase de §5.1b não carrega número.
- *(sec1-2)* LEDGER: os nomes `MTLnet` e `Check2HGI` aparecem em S8 como linhas da Tab. 1 (o asset plan manda reduzir a tabela a DGI, HGI, MTLnet, Check2HGI). Os artefatos continuam sendo INTRODUZ em 3.2 e 5.2. Declarei duas reduções na linha MTLnet: sai 'Null result for that configuration' (a Seção 2 não reporta resultado) e sai 'FiLM conditioning' (FiLM é INTRODUZ em 3.2). Nenhum valor foi alterado, mas é edição de arte entregue e o autor precisa sancioná-la.
- *(sec1-2)* S12 referencia `[CARIMBO-TAREFA]` e `[CARIMBO-MÉTRICA]` pelo nome. Os dois blocos são definidos no preâmbulo do SLIDES.md, fora desta parte; quem montar o documento precisa garantir que a definição do preâmbulo sobreviva à remontagem.
- *(sec1-2)* S7 carrega `[BLOCO-CONTRIBUIÇÃO]` por extenso porque a §8 regra 13 exige redação IDÊNTICA entre este slide e o de fechamento da Seção 6. Quem escrever a Seção 6 deve copiar o bloco de S7 palavra por palavra, e não reescrevê-lo. A metade prática foi reancorada em `chapters/2_fundamentals.tex:1901-1906`, que é mais forte que a redação anterior ('o modelo conjunto é o artefato maior, e uma passagem por ele custa mais do que rodar os dois dedicados'), e deliberadamente não cita contagem de parâmetros.
- *(sec1-2)* Correção de fato em relação à versão anterior do S1: o slide de capa levava o título do artigo do MobiWac ('Predicting the Next Category and Region of a Visit'). O título depositado é 'Multitask Learning for Point-of-Interest Classification and Prediction Tasks: The Role of the Check-in-Level Representation' (`src/preamble.tex:226`, folha de rosto de `banca.pdf` p. i). A grafia depositada do nome é 'Vitor Hugo De Oliveira Silva', com 'De' maiúsculo; se o autor preferir 'de', é decisão dele e vale para a folha de rosto também.
- *(sec1-2)* Defeito evitado que vale registrar para o resto do deck: a coluna *Majority* da Tab. 8 (AL 34.2, FL 24.7, IST 33.4) é a fração de rótulos na categoria mais comum, e NÃO é a macro-F1 do preditor de classe majoritária. Equiparar as duas produziria um piso falso. Está no campo 'Nunca dizer' de S11.
- *(sec1-2)* Correção de posicionamento em relação à versão anterior: as três armadilhas de nomenclatura estavam todas no slide de 2.5. O PLANO §3 manda 2.5 carregar apenas as DUAS que sobram (o par de tarefas, a convenção métrica), porque a primeira ('Next-POI Prediction' = próxima categoria) é desarmada na Seção 1. Ela agora vive em S6, que é onde o título do Cap. 3 imprime a expressão pela primeira vez.
- *(sec1-2)* Correção em relação à versão anterior do S4: a moldura 'sob o desenho final e o protocolo mais estrito dos três' estava sendo FALADA. A decisão do autor (PLANO §5.1b) é que ela sai da fala e fica na tela. A fala agora termina numa ponte para a Seção 5, onde as quatro células dentro da margem são enumeradas com intervalo e teste.
- ✅ **FECHADO 2026-08-24 (decisão do autor: registrar).** `POI Encoder` entrou no `GLOSSARY.md` §2, com a fronteira *"Ch. 4 vocabulary only"* e proveniência `4_courb/methodology.tex:160`. Fica na tela do S28 como está. — *pendência original:* `POI Encoder` não está no registro do GLOSSARY (regra fail-closed), mas é o nome do próprio Cap. 4 entregue para a primeira fase do canal categórico. Usei-o em S28 com glosa. O autor precisa registrar a entrada, ou aprovar a substituição por uma descrição sem nome próprio.
- ✅ **FECHADO 2026-08-24 (decisão do autor: manter verbatim).** `technical tie` entrou no `GLOSSARY.md` §4 como vocabulário **do Cap. 4 apenas**, com a direção colada (*MTLnet retém a média mais alta, por 0,02 pp*) e a proibição explícita no eixo do Cap. 5. Guarda e resposta de arguição registradas no bloco do S30. — *pendência original:* S30 mantém `empate técnico` / `technical tie`, que é a redação literal do Cap. 4 entregue (`one additional technical tie`), com a direção declarada junto (a média do MTLnet é a mais alta, por 0,02 pp). `ties` é verbo banido no eixo do veredito do Cap. 5; este uso está fora daquele eixo. Precisa do carimbo do portão G3, ou de troca por `o MTLnet retém a média mais alta por 0,02 pp`.
- *(sec3-4)* Divergência de redação entre partes: S9 (Seção 2) traduz o critério do Cap. 2 como `um balanceador só é útil se superar uma ponderação fixa`, e S22 usa `melhorar sobre`, para manter o verbo licenciado `supera` fora de uma afirmação que não é veredito. O EN entregue é `improves on a tuned fixed weighting`. Uma das duas redações tem de vencer, e a decisão é de uma mão só.
- *(sec3-4)* A Fig. 1 precisa ser redesenhada em TikZ antes do build (o raster entregue imprime tipo de ~7 pt). Até lá S18 não tem arte utilizável, e é o único slide desta parte bloqueado por asset.
- *(sec3-4)* O número do juiz do CoUrb (SIREN sozinho no Texas, fora da faixa anunciada) NÃO aparece em lugar nenhum destes slides: a fonte dele é `articles/CoUrb_2026/slides/judge_feedback.md`, e não uma célula de tabela entregue. S29 carrega a declaração `melhor-de-dois` que o juiz exigiu, sem o número. Se o autor quiser dizer o número em voz alta, ele precisa entrar com a linha de proveniência confirmada.
- *(sec3-4)* Os números de subseção citados no campo Proveniência dos Caps. 3 e 4 (§3.3.1, §3.3.3, §4.3.5.2, §4.3.6, §4.4.3, entre outros) foram derivados da ordem dos cabeçalhos nos arquivos `.tex` entregues, não lidos da numeração do PDF construído. Se algum deles for para a tela, confirmar contra `src/banca.pdf`.
- *(sec5)* COLISÃO DE LEDGER A RESOLVER PELO ORQUESTRADOR: o S49 (escada da fronteira) está aqui porque a instrução da minha parte manda encerrar nele, mas o PLANO §3 orça os seus 30 s dentro da Seção 6 e a versão anterior do SLIDES.md o numerava como primeiro slide da Seção 6. Se o redator da Seção 6 também o escrever, o elemento 'a leitura conjunta dos três estudos' recebe dois INTRODUZ e 30 s são contados duas vezes. Decidir: ou o S49 fica nesta parte (Seção 6 começa em S50), ou sai daqui.
- ✅ **FECHADO 2026-08-24 (decisão do autor: registrar).** Quatro dos cinco termos entraram no `GLOSSARY.md` — `silhouette score`, `nearest-neighbor category purity` e `logit adjustment` em §4, `cross-attention stack` em §2, cada um com proveniência arquivo:linha e a fronteira que impede o mau uso (os dois primeiros são **diagnóstico de geometria, não métrica de tarefa**). O quinto, `feature-concatenation control`, **não está na tela** (medido) e não precisou de entrada. — *pendência original:* VOCABULÁRIO FORA DO REGISTRO (GLOSSARY é fail-closed). Cinco termos usados na tela vêm literalmente do Cap. 5 entregue mas não têm linha no GLOSSARY: 'silhouette score', 'nearest-neighbor category purity', 'logit adjustment', 'cross-attention stack' e 'feature-concatenation control'. Eu os usei porque são as palavras do próprio capítulo que a banca leu, e não invenção minha, mas eles precisam de entrada aprovada pelo autor antes do build. [PROPOR: silhouette score · nearest-neighbor category purity · logit adjustment · feature-concatenation control]
- *(sec5)* SEMENTES {0, 1, 7, 100} (S43): o corpo do Cap. 5 diz apenas 'four seeds'; os quatro inteiros aparecem nos apêndices do volume principal (`chapters/apx_a_contributions.tex:56` e `chapters/apx_h_check2hgi_joint_model.tex:410`). Confirmar com o autor se ele quer dizer os quatro inteiros em voz alta ou ficar em 'quatro sementes'.
- *(sec5)* NUMERAÇÃO DE SEÇÃO DO CAPÍTULO: eu citei arquivo e linha em toda a Proveniência, em vez dos números §5.x que a versão anterior do SLIDES.md usava, porque não pude verificar o mapeamento de seções no PDF construído (o Cap. 5 tem preâmbulo e a numeração impressa pode estar deslocada em um). Se o deck for citar §5.x na tela, alguém precisa conferir contra `src/banca.pdf`.
- *(sec5)* ASSETS QUE NÃO EXISTEM E PRECISAM SER PRODUZIDOS: (a) a grade 3 × 3 do S49; (b) o recorte da Fig. 4 para o S36, que remove as três anotações em itálico do original (elas viraram fala) e escala o miolo. Fig. 5, Fig. 6, Fig. 7 e Tab. 9 vão como entregues; a Tab. 10 vai com colunas externas reduzidas a uma por eixo.
- *(sec5)* DECISÃO DE DENSIDADE NO S47: incluí, em fonte menor, a frase entregue sobre o teste post-hoc na direção reversa (resolve três dos quatro déficits; Istambul não). Ela fortalece o 'déficits, não empates' e é texto entregue, mas o S47 já é o slide mais denso da seção. O autor decide se fica na tela ou migra para a série B1.
- *(sec5)* ORÇAMENTO REAL: os 5,5 min de 5.5 estão distribuídos como 110 + 120 + 100 s. No ensaio de 24/08, se a Seção 5 estourar, a ordem de sacrifício que eu recomendo é S35 (25 s, o CTLE pode ser dito dentro do S45) e depois 10 s de cada um de S42 e S43. S38, S44 e S47 não são cortáveis: são o payoff da representação, a maquinaria que licencia o veredito, e o veredito.
- *(sec6)* A grafia completa de Pedro Maia. Varredura desta sessão sobre o repositório inteiro (grep -rn "Pedro" articles/ docs/) devolve apenas os documentos de planejamento da defesa; nenhuma fonte primária. Não inventei sobrenome; o nome fica como o autor o ditou e a grafia é dele para fechar.
- *(sec6)* Divergência entre a lista ditada e os agradecimentos depositados (src/content.tex:47-67). O depositado nomeia Fabrício Silva, Germano Santos, a defesa de referência Santana, Gustavo Viegas e Tarik Paiva; Ingred F. Almeida e Pedro Maia não constam. Deixei a oração de inserção pronta em S54 caso o autor queira alinhar. O CBIC 2025 tem ainda um coautor que a lista não menciona, Felipe T. Sousa.
- *(sec6)* O [BLOCO-CONTRIBUIÇÃO] de S51 tem de ser byte-idêntico ao de S7 (§8 regra 13). Reproduzi o bloco como ele está hoje no cabeçalho do SLIDES.md. Se o redator da Seção 1 mudar uma palavra em S7, S51 muda junto, e o portão G2 precisa comparar os dois campos caractere a caractere.
- *(sec6)* O asset da escada 3 × 4 de S49 não existe no repositório (confirmado contra o inventário GROUND B). Precisa ser desenhado em Beamer/TikZ, com marca visual nas duas células 'unchanged, by design' da linha ST-MTLNet.
- ✅ **FECHADO 2026-08-24 (decisão do autor: registrar `controlled ablation` e usar em toda parte).** A superfície entregue **`controlled ablation`** entrou no `GLOSSARY.md` §4, com equivalente PT (*ablação controlada*) e a ressalva de que `comparação controlada` usada para a auditoria de corpus é outro ato, não este termo. `input pipeline` **não está na tela** (medido), então a substituição por *"como as entradas são construídas"* fica de pé sem entrada nova. — *pendência original:* Dois termos do próprio Cap. 6 e foram substituídos por superfície registrada em vez de propostos: 'ablation' (usado em §6.3 limitação 6 e em §6.4) virou 'teste controlado' / 'comparação controlada', e 'input pipeline' (§6.4, item do próximo lugar) virou 'como as entradas são construídas'. Se o autor preferir propor as entradas ao registro, as duas telas voltam à letra do capítulo.
- *(sec6)* Confirmação do portão G2 sobre o alcance de 'nenhum número novo' (PLANO §3, Seção 6): mantive as datas da limitação 1 (janeiro de 2009 a agosto de 2011; 2012 a 2013 e 2017 a 2018; cerca de sete em dez) e as sete classes da limitação 2, porque a WRITING_LAW §3 exige que uma limitação seja concreta e nenhuma delas é resultado. Nenhum outro numeral entra na seção.
- *(Série B (trilh)* A grafia completa de "Pedro Maia" continua não localizada (plano §9, pendência 7). Nenhum slide da série B a usa, mas o slide de agradecimentos da trilha principal precisa dela e eu não invento sobrenome.
- *(Série B (trilh)* Q13 tem duas camadas de proveniência que o autor precisa decidir antes de segunda: a fidelidade dos braços de Arizona e Florida está EM ABERTO no próprio registro (a média cai dentro de 0,07 e 0,03 da Tabela 9, mas a igualdade por fold, que Alabama demonstra ser alcançável, não se verifica, e a causa não foi identificada). O slide B-Q13 declara isso como limite. Se o autor preferir não levar o número de Florida à sala, o slide precisa ser recortado para Alabama e Arizona.
- *(Série B (trilh)* O plano §6 pede a matriz de cobertura de busca em B2 "com ERR-6/ERR-7 oferecidas". Escrevi um slide (B2-5) com as duas erratas em prosa, não a matriz por botão × conjunto. A matriz existe em `FINAL_SETTINGS.md:76,:97,:12`, mas ela não está impressa em nenhum dos dois volumes, e transcrevê-la para a tela criaria uma tabela nova sem célula impressa de origem. Decisão do autor: prosa (como está) ou tabela derivada com carimbo de proveniência de repositório.
- *(Série B (trilh)* O plano §6 lista, na família B6, "as sete perguntas [FECHADO] hoje sem família" com prioridade em Q22. Cobri Q22 (SB40). As outras seis do grupo E/C/D já entraram por outras famílias (Q17, Q18, Q19, Q20, Q21 parcialmente via Q22, Q6). **Q6** ("uma dissertação sobre POI que não prediz o POI") e **Q21** (os 93 por cento de previsibilidade contra 37 de macro-F1) NÃO têm slide próprio nesta parte: os dois são respondidos pela trilha principal (Def. 2.9 excluída em 1.4; os pontos de referência em 2.4 e 5.4). Se o autor quiser 1:1 também com os `[FECHADO]`, faltam esses dois slides e eu os escrevo.
- *(Série B (trilh)* A citação de Karpathy (2019) é uma palestra, e eu não abri a fonte primária nesta sessão: as três frases entre aspas vêm do plano §6, que as registra. Antes do deck construído, a proveniência exata (título da palestra, minutagem ou transcrição) precisa ser fixada, ou o slide B-KARPATHY cita apenas Standley et al. (ICML 2020), que é referência formal e verificável.
- *(Série B (trilh)* Os números da triagem de uma dobra em Q8 (−0,099 / −0,077 / −0,120) vêm de `region_1fold_triage/FINDING.md`, que eu não abri nesta sessão: li a transcrição deles em `wrapup/open_points/ARGUICAO.md` §Q8, que os cita com o caminho. Se o autor quiser esses três na tela, vale reabrir o arquivo de origem antes do ensaio de segunda; a alternativa segura é o slide dizer só "todos os braços se movem menos de 0,15 ponto", que é a formulação da RESPOSTA FINAL do próprio registro.


---

# Blocos REMOVIDOS do deck — preservados para reversão

> Removidos na **Fase A** de 2026-08-26, por decisão do autor (`considerations.md` AUT-2 e AUT-7).
> O deck foi de 111 para **107 páginas**; `Overfull` 25 → 25; grafo de hyperlinks intacto.
> **Se algum voltar, o número impresso de tudo depois dele volta a mudar.**

### S7 · The contribution, in one block
- **Slide impresso:** **6**
- **Seção/subseção:** 1.5 (§8 regra 13, primeira das duas aparições)   **Tempo:** 40 s
- **LEDGER:** INTRODUZ a contribuição una (a segunda aparição, com redação idêntica, é o slide de fechamento da Seção 6)
- **Na tela:** dois blocos. **Reproduz o `[BLOCO-CONTRIBUIÇÃO]` do cabeçalho palavra por palavra.** *(v2 · **quarta** reescrita, 2026-08-24 — ver a nota abaixo, que é a mais importante das quatro.)*
  - Bloco **Practical — what it delivers**:
    - **one model, one forward pass, two predictions** — one artifact to train, version and deploy, **in place of two**;
    - **operational, not computational**: the joint model is the larger artifact;
    - **Check2HGI is the reusable part** — one vector per visit, independent of the prediction heads on top.
  - Bloco **Scientific — what it establishes**, uma frase só:
    - The **input representation** and its **sharing topology** determine **whether** multitask learning helps these POI prediction tasks.
- **v2 · a quarta reescrita, e o defeito que ela conserta:** ⚠ **a metade científica anterior era, inteira, tela de OUTROS slides.** Medido linha a linha: *"the novelty is the combination: per-visit context inside a hierarchical graph-infomax representation"* é **verbatim a tela do S35**; *"helps under the final design and evaluation protocol"* é o bloco *The answer* do **S50**; *"the input representation is one condition; architecture and scale suggested, not isolated"* é o **terceiro item do S50**. E o **S50 é o slide imediatamente anterior a este no fechamento** — a banca via um slide e, um clique depois, dois terços dele repetidos. **Violação tripla da R4** (um elemento carrega INTRODUZ em exatamente um slide), num slide cujo ledger eu não conferi enquanto conferia o dos outros 34.
  **Dois defeitos caíram junto.** (a) **Referência para a frente:** `graph-infomax` estava na tela do S7, mas a ideia infomax é **INTRODUZ no S8** — um slide *depois*. (b) **Tela e fala afirmavam coisas diferentes:** a fala já dizia *"a representação de entrada e a topologia de compartilhamento decidem se o multitarefa ajuda"*, que é o grupo **Theoretical** entregue, enquanto a tela dizia a taxonomia do §6.2. Um arguidor atento ouvia uma tese e lia outra. **A nova tela alinha as duas** — e a fala não muda, então o relógio não se move.
  **A metade científica agora é a primeira frase do grupo Theoretical** (`src/chapters/1_introduction.tex:422-426`), que é o recorte da própria seção de Contribuições e **não está em tela nenhuma do deck**. Ela faz o que o autor pediu — o achado amplo primeiro (**`whether`** é a condicionalidade, numa palavra) e a representação nomeada dentro dele. ⚠ **A taxonomia graduada das três condições fica no S50**, que a possui: *representação* estabelecida por comparação controlada, *arquitetura* e *escala* sugeridas e não isoladas. ⚠ **E note a granularidade:** o Theoretical afirma que representação **e topologia** *determinam*; o §6.2 diz que só a representação foi *isolada*. Não se contradizem — são recortes diferentes da mesma evidência —, e a resposta de arguição é essa.
  **A objeção do autor sobre a redundância prática:** *"one model, one forward pass, two predictions"* e *"one artifact"* diziam a mesma ideia. Fundidos num marcador só, com o travessão marcando que são a mesma coisa vista da inferência e do ciclo de vida. ⚠ **A ressalva que a R13 obriga ficou em linha própria** — enterrá-la dentro da fusão a enfraquecia. Densidade: **92 → ~66 palavras**.
  **Revisão crítica por agente Fable**, a pedido do autor, sobre o texto entregue e o deck: foi ela que achou a duplicação tripla, que eu não tinha visto.
- **Fala (PT):** "A contribuição, em duas metades, e eu volto a esta tela no fim com as mesmas palavras. A metade prática: um modelo, uma passagem, duas predições. O ganho é operacional, não computacional. O modelo conjunto é o artefato maior, e uma passagem por ele custa mais do que rodar os dois dedicados; o que diminui é o número de modelos para treinar e manter. A metade científica: o que eu entrego são condições, não um sim universal. A representação de entrada e a topologia de compartilhamento decidem se o multitarefa ajuda nestas tarefas. É por isso que um resultado nulo com embedding por lugar e compartilhamento rígido não contradiz um resultado positivo com representação em nível de check-in e outra forma de compartilhar."
- **Proveniência:** metade científica copiada de `chapters/1_introduction.tex:425-431` (grupo Theoretical). Metade prática copiada de `chapters/2_fundamentals.tex:1901-1906` ("a single model to maintain and one forward pass"; "The gain is operational, not computational"; "the reduction is in the number of models to train and maintain"); o custo por passagem também em `chapters/5_mobiwac/04_method.tex:51-56`.
- **Nunca dizer:** "MTL funciona" sem condição. Nenhum número aqui, e em particular nenhuma contagem de parâmetros: a razão entre o modelo conjunto e os dois dedicados **não foi re-medida** (PLANO §8 regra 9).

---

# SEÇÃO 2 · Fundamentos compartilhados: dito uma vez (6 min)

> `\section[Fundamentos]{Fundamentos compartilhados}`
> **Propósito:** o motor de de-duplicação. Depois desta seção, cada estudo só diz o que mudou.
> **Orçamento:** 35 + 30 + 40 + 45 + 50 + 55 + 35 + 50 = **340 s** em **oito** slides (eram 360 s em nove; a fusão levou a sete e a divisão do slide de representação, em 25/08, devolveu um).
> ⚠ **Ordem revista em 2026-08-25 (decisão do autor). Nove slides viraram sete.** Antes o deck abria
> pela linhagem — que no texto é a *conclusão* do bloco de representações — e fechava pelo trabalho
> relacionado, que é a *premissa*. As duas pontas estavam invertidas, e a plateia encontrava DGI, HGI
> e Check2HGI antes do panorama que os contextualiza.
>
> **A ordem agora agrupa por assunto, e não há ida-e-volta:**
> **(1) MTL inteiro** — panorama (§2.1.2) → o eixo que separa este trabalho (§2.1.3) → vocabulário,
> compartilhamento rígido e transferência negativa (§2.3);
> **(2) representação inteira** — escada (§2.2.1) → infomax (§2.2.2) → Tab. 1 e o diagrama de níveis
> (§2.2.4, que o capítulo põe por último);
> **(3) o aparato** — dados, métrica e protocolo fechando (§2.4).
>
> ⚠ **A segunda passada (troca do 3º com o 4º) corrigiu um defeito da primeira.** Espelhar o Cap. 2
> literalmente punha §2.2 antes de §2.3 — mas os dois slides de trabalho relacionado que agora abrem
> **já são de MTL**, então a seção saía de MTL, entrava em representação e voltava a MTL. O capítulo
> pode se dar ao luxo dessa ordem porque o leitor volta atrás; a plateia não.
>
> **Os números dos blocos (`S8`…`S14`) são identidades históricas, não posições.** Eles NÃO foram
> renumerados de propósito: doze referências cruzadas neste arquivo apontam para eles pelo número, e
> renumerar quebraria todas em silêncio. **Identifique slide por título, nunca por número** — a
> numeração do `SLIDES.md` já diverge da impressa no deck (ver `HANDOFF.md (anexo, sec. `HANDOFF_SLIDES.md`)` §1.5).
>
> **Dois blocos saíram:** o antigo **S15** (*Related work in representation*) foi **absorvido pelo
> S8**; o antigo **S16** (*With the vocabulary fixed…*) teve o **frame cortado** — a frase continua,
> falada sobre o divisor automático da Seção 3, que é a forma que a regra 12 do PLANO §8 prevê
> literalmente (*"falada sobre ele, ou vai num `\specialframe` próprio quando merecer a tela inteira"*).

### S20 · Setup, and the protocol declared
- **Slide impresso:** **18**
- **Seção/subseção:** 3.3   **Tempo:** 30 s
- **LEDGER:** RETOMA os dados de 2.3, as sete categorias de 2.3 e o protocolo de 2.5
- **Na tela:**
  - **Data.** Florida, from Gowalla: 20,301 users, 65,009 places, 990,518 check-ins. The seven categories.
  - **Sequences.** Non-overlapping windows of nine visits; users with fewer than five visits are discarded.
  - **Protocol, declared here.** Five-fold cross-validation **stratified over samples**, one seed. Full epoch budget, no early stopping. Each task read at **its own best validation epoch**. Mean and standard deviation across the five folds, **no significance test**.
  - So this chapter reports **differences**, never a verdict.
- **Fala (PT):** "O setup em três linhas, e a terceira é a autodeclaração de protocolo que eu prometi na Seção 2. Os dados são a Flórida do Gowalla, vinte mil trezentos e um usuários, sessenta e cinco mil e nove lugares, novecentos e noventa mil quinhentos e dezoito check-ins, nas mesmas sete categorias. As sequências são janelas não sobrepostas de nove visitas, e quem tem menos de cinco visitas sai. O protocolo é o estratificado por amostra: cinco partições, uma semente, orçamento cheio de épocas, cada tarefa lida na melhor época de validação dela, e média com desvio entre as cinco partições. Sem teste de significância. É por isso que este capítulo reporta diferenças, e não veredito, e é por isso que eu não vou usar o verbo supera em nenhum slide desta seção."
- **Proveniência:** `chapters/3_cbic/results.tex` §3.4.1 (Flórida: 20,301 / 65,009 / 990,518; as sete categorias; cinco partições estratificadas por amostra; semente única; sem parada antecipada; leitura na melhor época de validação de cada tarefa; média e desvio entre as cinco partições); `chapters/3_cbic/method.tex` §3.3.1.3 (janelas não sobrepostas de nove, corte em cinco visitas). As três contagens da Flórida também estão impressas na Tab. 5, `tables/courb/dataset.tex`, e já apareceram em S10.
  **Cobertura da frase *no significance test* (AGENT_GUARDRAILS §4b V1):** rodado em `src/`, `for f in chapters/3_cbic/*.tex chapters/3_cbic.tex; do grep -vn '^[[:space:]]*%' "$f" | grep -icE "p-value|p value|significan|t-test|wilcoxon|confidence interval|hypothesis test"; done` soma **8** linhas, e as oito são uso comum de *significant* ou *hypothesis*. Nenhum teste estatístico é nomeado no capítulo. Nada foi excluído da varredura além das linhas de comentário.
- **Nunca dizer:** "as mesmas janelas" do Cap. 5 (lá são sobrepostas, passo 1). Nunca chamar a média por categoria deste capítulo de macro-F1.

### S29 · The caveat, then the number
- **Slide impresso:** **28**
- **Seção/subseção:** 4.2   **Tempo:** 45 s
- **LEDGER:** INTRODUZ o resultado da tarefa estática do Cap. 4 e a ressalva de rótulo na entrada
- **Na tela:** *(v2 · 2ª varredura, 2026-08-24 — este campo foi **derivado mecanicamente do frame vigente em `slides/main.tex`**, não transcrito à mão, porque nesta passada o `.tex` foi editado primeiro. A fonte da fala continua sendo este arquivo.)*
  - Bloco **From the chapter preface**:
    - After publication we established that the input to this chapter's static task **contains the label it predicts**: the venue-type feature maps one-to-one onto the seven top-level categories. The reported static-task accuracy measures **that lookup**, not learned semantic inference;
  - **The static gain therefore says nothing about the sequential task**; then, and only then: the decomposed input leads in **all 21 category-state combinations**, **+20.2 to +22.0 pp** per state; declared with the range — the **better of the two spatial encoders** in each combination, not either one alone. **Metric stamp.** Chapters 3 and 4 print one F1 **per category**; Chapter 5 reports **macro-F1**. Not one scale;
- **Fala (PT):** "Aqui a ordem importa mais que o número, então eu digo a ressalva primeiro, em uma cláusula, e sigo em frente. Depois da publicação, nós estabelecemos que a entrada da tarefa estática deste capítulo contém o rótulo que ela prevê: a feature de tipo de local mapeia um-para-um nas sete categorias de topo. A acurácia reportada nessa tarefa mede essa consulta, e não inferência semântica aprendida. A consequência é direta e eu prefiro dizê-la eu mesmo: o ganho estático não diz nada sobre a tarefa sequencial. Dito isso, o número. Na tarefa estática a entrada decomposta lidera nas vinte e uma combinações de categoria e estado, com ganhos médios por estado de vinte vírgula dois a vinte e dois pontos percentuais. E eu declaro o que essa faixa é: é o melhor dos dois codificadores espaciais em cada combinação, não é nenhum dos dois sozinho."
- **Proveniência:** ressalva copiada do prefácio do Cap. 4, `chapters/4_courb.tex`, redação literal; contagem e faixa de `chapters/4_courb/results.tex` §4.4.2 e `chapters/4_courb/conclusion.tex` (*"in all 21 category-state combinations, with average gains per state of 20.2 to 22.0 percentage points, considering the better of the two spatial encoders in each combination"*); tabela de origem `tables/courb/category.tex` (Tab. 6), que **não** vai para a tela (21 × 3 × 3 não cabe, e a ressalva desqualifica leitura célula a célula).
- **Nunca dizer:** número antes da ressalva. "macro-F1 subiu 20 a 22" (são médias de F1 por categoria). A faixa sem dizer que é melhor-de-dois. Deixar o ganho estático falar pela tarefa sequencial. E não gastar dois minutos justificando a ressalva: uma cláusula, e adiante.

### S5 · What is predicted, and what is not
- **Slide impresso:** **4**  ·  *(pós-Fase A, medido no PDF de 107 páginas)*
- **Seção/subseção:** 1.4   **Tempo:** 40 s
- **LEDGER:** INTRODUZ as três tarefas (Defs. 2.6, 2.7, 2.8) e a exclusão do próximo lugar (Def. 2.9) · RETOMA a restrição de modelo único
- **Na tela:**
  - **Next category** (Def. 2.7): the category of the next visited place.
  - **Next region** (Def. 2.8): the administrative unit, at neighborhood scale, where the next visit occurs.
  - **Next place** (Def. 2.9): the exact establishment. **Named to be excluded. No chapter reports a result for it.**
  - Also used in this work: **category classification** (Def. 2.6), a static task that reads one place rather than a history.
  - The constraint again: one trained artifact, one forward pass, both outputs.
- **Fala (PT):** "O escopo, no positivo. Eu predigo duas propriedades da próxima visita: a categoria, que é o tipo do lugar, e a região, que é a unidade administrativa em escala de bairro onde a visita acontece. O próximo lugar exato eu não predigo. Ele está definido no Capítulo 2 justamente para ser excluído, e nenhum capítulo reporta resultado para ele. Existe ainda uma terceira tarefa no trabalho, a classificação de categoria, que é estática: lê a representação de um lugar, e não um histórico. Ela é metade do par nos dois primeiros estudos."
- **Proveniência:** Defs. 2.6 a 2.9 → `chapters/2_fundamentals.tex:245-267` e `:313-320` (numeração confirmada em `build/main-aux/chapters/2_fundamentals.aux`); "an administrative unit at neighborhood scale" → `:275-276`; escopo e restrição → `chapters/1_introduction.tex:325-330`; "outside the scope of this work" → `chapters/1_introduction.tex:89-92`.
- **Nunca dizer:** "prediz o próximo POI". Nenhum particular do corpus: nem o número de classes, nem setor censitário, nem *mahalle*, nem nome de estado (isso é de S10).

### S17 · One static task, one sequential task
- **Slide impresso:** **14**  ·  *(pós-Fase A, medido no PDF de 107 páginas)*
- **Seção/subseção:** 3.1   **Tempo:** 30 s
- **LEDGER:** INTRODUZ a dicotomia estática × sequencial que o Cap. 3 põe à prova · RETOMA as Defs. 2.6 e 2.7 e a armadilha de nome de S12
- **Na tela:**
  - **Task A, static** (Def. 2.6). Read one place's representation, predict that place's category.
  - **Task B, sequential** (Def. 2.7). Read a history of nine visits, predict the category of the next visit.
  - **Related on the surface.** Same mobility data, same seven categories.
  - **Different in nature.** One reads the intrinsic features of a place; the other reads temporal order and transitions.
  - **The chapter's hypothesis:** that difference limits what one shared trunk can do for both.
  - `[CARIMBO-TAREFA]`
- **Fala (PT):** "O par do primeiro estudo. Uma tarefa estática: ler a representação de um lugar e prever a categoria dele. E uma tarefa sequencial: ler um histórico de nove visitas e prever a categoria da próxima. Na superfície elas são relacionadas, porque saem dos mesmos dados e do mesmo espaço de sete categorias. Na natureza, não: uma depende das características intrínsecas de um lugar, a outra depende de ordem temporal e de transição. O capítulo entra no experimento com uma hipótese declarada, e ela é negativa: essa diferença é grande o bastante para limitar o que um tronco compartilhado consegue fazer pelas duas."
- **Proveniência:** `chapters/3_cbic/intro.tex` §3.1 (as duas tarefas, a dicotomia estática × sequencial, e a hipótese central do estudo); `chapters/2_fundamentals.tex`, Defs. 2.6 e 2.7. Nenhum número nesta tela.
- **Nunca dizer:** "prediz o próximo POI" ou "próximo lugar". Neste capítulo *Next-POI Prediction* é a próxima **categoria**, e o carimbo está na tela.



> ⚠ **Arquivado 26/08.** Este bloco continuou na lista ATIVA depois que a `AUT-12` removeu o slide,
> e por isso **todos os `Slide impresso` a partir do 10 ficaram deslocados em +1** — 37 blocos.
> A defasagem foi medida e corrigida na mesma passada, re-derivando cada número do PDF construído.

### S8 · The idea these three share
- **Slide impresso:** **10**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 2.4b   **Tempo:** 50 s
- **LEDGER:** INTRODUZ a ideia compartilhada pelos três métodos infomax · INTRODUZ a distinção entre **o que se maximiza** e **como se estima** · INTRODUZ o escopo estreito de *"sem rótulos"*
- **Na tela:** *(v6 · três caixas, uma por ideia, usando as três cores do template.)*
  - `block` (verde) **Said once, so that no chapter has to repeat it**: *The model learns useful vectors by being asked to tell a true pairing of two parts of the data from a corrupted one, and it needs no labels to do so.*
  - `exampleblock` (azul) **What is maximized $\mid$ how it is estimated**: ***Infomax** names what is maximized: the **mutual information** between representations at two adjacent levels. The pairing test is the **estimator**, because the quantity is never evaluated in closed form.*
  - `alertblock` (magenta) **The scope of "no labels", stated before anyone asks**: *In this work: **no next-category and no next-region target**.*
- **v6 · as duas correções que este slide carrega:**
  1. **O título do primeiro bloco é do capítulo, não nosso.** O deck chamava esta frase de *"The infomax idea, in one sentence"*, e ela **não é o infomax**: é o **estimador contrastivo**. O Cap. 2 é cuidadoso e chama-a de ***"The idea these methods share"*** (`2_fundamentals.tex:383`), dizendo o objetivo em separado: *"**The name states what is maximized.** Training raises the mutual information between representations at two adjacent levels, **and it does so without evaluating that quantity in closed form**"* (`:433-436`). Correção do autor, 25/08. **Não reverter.**
  2. **`contrastive` NÃO vai para a tela**, só para a fala: o Cap. 2 **cortou a palavra de propósito** (`:523`, *"The prose sentence naming the contrastive paradigm was CUT in the trim"*), e ela **já está em tela com outro sentido** — `main.tex`, a perda contrastiva de 10 km/70 km dos codificadores do Cap. 4. Na fala é ancorada no Cap. 3 (`3_cbic/method.tex:35`, *"DGI as a contrastive learning method"*). ⚠ `mutual information` **foi registrado** no `GLOSSARY` §3 em 25/08 e por isso pôde ir para a tela.
- **Fala (PT):** "Aqui eu digo só a ideia que os três compartilham, uma vez, para não ter de repeti-la três vezes. Nas palavras do próprio capítulo: o modelo aprende vetores úteis sendo obrigado a distinguir um pareamento verdadeiro de um pareamento corrompido, e não precisa de rótulo nenhum para isso, porque os próprios dados dizem qual é o verdadeiro. E aqui vale separar duas coisas que costumam ser confundidas. Infomax é o nome do que se maximiza, que é a informação mútua entre representações de dois níveis adjacentes. O teste de pareamento é como isso se estima, e na literatura ele é da família do aprendizado contrastivo, que é o nome que o Capítulo 3 usa. A informação mútua nunca é calculada em forma fechada. E um cuidado de escopo que eu prefiro dar eu mesmo, antes que me perguntem: a frase sem rótulos é da ideia geral. Nesta dissertação a forma correta é a que está na tela, sem alvo de próxima categoria e sem alvo de próxima região, porque a categoria da visita entra como característica de entrada do nó."
- **Proveniência:** a frase compartilhada, verbatim → `chapters/2_fundamentals.tex:383-387`. A distinção entre o que se maximiza e como se estima → `:420-426` e `:433-436`. O nome `contrastivo`, para a fala → `chapters/3_cbic/method.tex:35` e o registro de proveniência do Cap. 2 em `:521`. A forma estreita de "sem rótulos" → `:416`, correção AUT-20.
- **Nunca dizer:** ⚠ **nunca estender "sem rótulos" ao Check2HGI.** A forma do capítulo é *sem alvo de próxima categoria e sem alvo de próxima região* — a categoria da visita **entra como característica de entrada** e, na configuração do estudo final, como alvo de uma reconstrução mascarada com peso 0,3 (correção AUT-20). Nunca dizer que a perda **é** a informação mútua: ela é um estimador. Nunca **`bilinear`** aqui. Nenhum resultado, nenhum número de capítulo.


> ⚠ **Arquivado 27/08.** O frame migrou para a Série B pela `AUT-29` (`main.tex:2415`), mas o bloco
> **continuou na parte VIVA** — e o extrator do `SPEECH` estava a imprimir como trilha principal um slide
> que já saíra dela: **189 palavras contadas a mais no relógio.** É a mesma classe do `S8`, que ficou vivo
> depois da `AUT-12` e deslocou 37 números impressos. **Mover o bloco é escrituração de decisão já tomada.**

### S38 · Result 1: the geometry of the vectors
- **Slide impresso:** **38**  ·  *(pós-B1, medido no PDF de 106 páginas)*
- **Seção/subseção:** 5.2 (c)   **Tempo:** 90 s
- **LEDGER:** INTRODUZ a separabilidade por categoria (Fig. 6)
- **Na tela:** **Fig. 6** inteira, que já é legível no tamanho entregue.
  - **Silhouette by category** (how tight and well separated the seven labeled groups are, on a −1 to 1 scale): about **0.57** for the check-in-level representation against about **0.00** for the place embedding.
  - **Nearest-neighbor category purity** (the share of nearest neighbors with the vector's own category, k = 10): about **0.98** against about **0.78**.
  - Both averaged over the five U.S. states.
  - Duas ressalvas na tela, em fonte menor:
    - *These measures characterize the representation family, not the exact configuration evaluated later. They need no fold, no seed, and no pairing.*
    - *The same geometry does not separate regions. The benefit is category-only; the model's spatial stream reads the region-level vectors of the same graph instead.*
- **Fala (PT):** "E este é o resultado da representação sozinha, antes de qualquer modelo. A pergunta é simples: esses vetores por visita separam as sete categorias? A silhueta por categoria mede quão compactos e quão separados estão os grupos rotulados, numa escala de menos um a um. Ela dá cerca de **0,57** para a representação em nível de check-in contra cerca de **0,00** para o embedding por lugar. A pureza de categoria dos dez vizinhos mais próximos dá cerca de **0,98** contra **0,78**. As duas médias são sobre os cinco estados americanos. Duas ressalvas, e eu faço as duas antes de alguém pedir. A primeira: a figura caracteriza a **família** da representação, e não a configuração exata que eu avalio depois. É por isso que ela não precisa de partição, de semente nem de pareamento, e é por isso que ela pode vir antes do protocolo. A segunda: a mesma geometria **não** separa regiões. O benefício é de categoria, e o fluxo espacial do modelo lê os vetores de região do mesmo grafo, não estes. Nenhum p-valor nesta tela: aqui é geometria, e o teste vem depois, no bloco de resultados."
- **Proveniência:** 0.57, 0.00, 0.98, 0.78, "averaged over the five U.S. states", "characterize the representation family rather than the exact configuration" e "The same geometry does not separate regions" → `chapters/5_mobiwac/06_results.tex:39-40`; k = 10 e a definição de silhueta cosseno → legenda da Fig. 6, `chapters/5_mobiwac/06_results.tex:85-88`; Fig. 6 = `figures/mobiwac/fig3_embquality.pdf`.
- **Nunca dizer:** nenhum p-valor aqui, e nenhuma afirmação de significância sobre esta figura. Nunca chamar a diferença de representação de "margem": margem é do TOST, e isto é uma diferença.
